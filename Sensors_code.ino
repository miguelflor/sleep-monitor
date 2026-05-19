#include <Wire.h>
#include <math.h>
#include "MAX30105.h"
#include "heartRate.h"
#include <MPU9250_WE.h>
#include "driver/i2s.h"

// ---------- Pins ----------
#define I2C_SDA   21
#define I2C_SCL   19

#define I2S_BCLK  26
#define I2S_LRC   25
#define I2S_DOUT  22

#define MPU_ADDR  0x68

// ---------- Audio ----------
#define SAMPLE_RATE     16000

// ---------- BPM history (last 60 s) ----------
#define BPM_HISTORY_SIZE 256
struct BeatRecord { unsigned long t; float bpm; };
BeatRecord bpmHistory[BPM_HISTORY_SIZE];
int   bpmHead   = 0;
int   bpmCount  = 0;

// ---------- Motion detection ----------
float motionLevel   = 0.0f;
const float MOTION_ALPHA     = 0.15f;
const float MOTION_THRESHOLD = 0.035f;
bool  isMoving      = false;

// ---------- Deep sleep detection ----------
const float    BASELINE_LEARN_SECONDS = 120.0f;   // first 2 min: learn awake HR
const float    HR_DROP_FRACTION       = 0.90f;    // current HR < 90% of baseline = "low"
const float    STILLNESS_THRESHOLD    = 0.03f;    // motionLevel below this = "still"
const uint32_t SUSTAINED_MS           = 15000UL;  // hold conditions 60 s before noise
const uint32_t RELEASE_GRACE_MS       = 5000UL;  // keep playing 30 s after break

float    awakeBaseline   = 0.0f;
bool     baselineLocked  = false;
uint32_t startupMs       = 0;
uint32_t deepStartedMs   = 0;
uint32_t lastDeepMs      = 0;

float baselineSumBpm     = 0.0f;
int   baselineSamples    = 0;

// ---------- Pink noise (Voss-McCartney) ----------
#define PINK_OCTAVES 8
int32_t  pinkRows[PINK_OCTAVES] = {0};
int32_t  pinkRunningSum         = 0;
uint32_t pinkCounter            = 0;

const int16_t PINK_AMPLITUDE_TARGET = 4000;   // adjust to taste (max 32767)
const float   FADE_STEP             = 50.0f; // amplitude change per chunk
float         currentAmplitude      = 0.0f;
bool          noiseActive           = false;

// ---------- Sensors ----------
MAX30105 hr;
MPU9250_WE mpu = MPU9250_WE(&Wire, MPU_ADDR);
bool mpuOk = false;

unsigned long lastBeatMs    = 0;
unsigned long lastPrintMs   = 0;
unsigned long lastMotionMs  = 0;
float bpm = 0;

// ---------- I2S setup ----------
void setupI2S() {
  i2s_config_t cfg = {
    .mode                 = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
    .sample_rate          = SAMPLE_RATE,
    .bits_per_sample      = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format       = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags     = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count        = 8,
    .dma_buf_len          = 256,
    .use_apll             = false,
    .tx_desc_auto_clear   = true,
    .fixed_mclk           = 0
  };
  i2s_pin_config_t pins = {
    .bck_io_num   = I2S_BCLK,
    .ws_io_num    = I2S_LRC,
    .data_out_num = I2S_DOUT,
    .data_in_num  = I2S_PIN_NO_CHANGE
  };
  i2s_driver_install(I2S_NUM_0, &cfg, 0, NULL);
  i2s_set_pin(I2S_NUM_0, &pins);
  i2s_zero_dma_buffer(I2S_NUM_0);
}

// ---------- Pink noise sample generator ----------
int16_t nextPinkSample(int16_t amplitude) {
  pinkCounter++;
  int bit = 0;
  uint32_t n = pinkCounter;
  while ((n & 1) == 0 && bit < PINK_OCTAVES - 1) { n >>= 1; bit++; }

  int32_t newVal = (int32_t)(esp_random() & 0xFFFF) - 0x8000;
  pinkRunningSum -= pinkRows[bit];
  pinkRows[bit]   = newVal;
  pinkRunningSum += newVal;

  int32_t white  = (int32_t)(esp_random() & 0xFFFF) - 0x8000;
  int32_t sample = (pinkRunningSum + white) / (PINK_OCTAVES + 1);

  return (int16_t)((sample * amplitude) / 0x8000);
}

// ---------- Stream one chunk of audio to I2S ----------
void streamPinkChunk() {
  const int CHUNK = 256;
  int16_t buf[CHUNK];
  size_t written;

  // Smooth amplitude toward target (fade in/out)
  float target = noiseActive ? (float)PINK_AMPLITUDE_TARGET : 0.0f;
  if (currentAmplitude < target) {
    currentAmplitude = fminf(currentAmplitude + FADE_STEP, target);
  } else if (currentAmplitude > target) {
    currentAmplitude = fmaxf(currentAmplitude - FADE_STEP, target);
  }

  if (currentAmplitude < 1.0f) {
    // Inaudible dither — keeps the amp out of idle and prevents buzz
    for (int i = 0; i < CHUNK; i++) {
      buf[i] = (int16_t)((esp_random() & 0x03) - 2);   // ±2 LSB, ~−84 dB
    }
  } else {
    for (int i = 0; i < CHUNK; i++) {
      buf[i] = nextPinkSample((int16_t)currentAmplitude);
    }
  }
  i2s_write(I2S_NUM_0, buf, sizeof(buf), &written, 0);  // non-blocking
}

// ---------- BPM history helpers ----------
void pushBpm(float value, unsigned long t) {
  bpmHistory[bpmHead].t   = t;
  bpmHistory[bpmHead].bpm = value;
  bpmHead = (bpmHead + 1) % BPM_HISTORY_SIZE;
  if (bpmCount < BPM_HISTORY_SIZE) bpmCount++;
}

float averageBpm60s(unsigned long now) {
  float sum = 0.0f;
  int   n   = 0;
  for (int i = 0; i < bpmCount; i++) {
    int idx = (bpmHead - 1 - i + BPM_HISTORY_SIZE) % BPM_HISTORY_SIZE;
    if (now - bpmHistory[idx].t > 60000UL) break;
    sum += bpmHistory[idx].bpm;
    n++;
  }
  return (n > 0) ? (sum / n) : 0.0f;
}

// ---------- Motion ----------
void updateMotion() {
  if (!mpuOk) return;

  xyzFloat acc = mpu.getGValues();
  float mag = sqrtf(acc.x * acc.x + acc.y * acc.y + acc.z * acc.z);
  float deviation = fabsf(mag - 1.0f);
  motionLevel = MOTION_ALPHA * deviation + (1.0f - MOTION_ALPHA) * motionLevel;
  isMoving = (motionLevel > MOTION_THRESHOLD);
}

// ---------- Setup ----------
void setup() {
  Serial.begin(115200);
  delay(200);

  Wire.begin(I2C_SDA, I2C_SCL, 400000);

  // ---- MAX30102 ----
  if (!hr.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("MAX30102 not found");
    while (1) delay(1000);
  }
  hr.setup(0x1F, 1, 2, 400, 411, 4096);
  hr.setPulseAmplitudeRed(0x50);
  hr.setPulseAmplitudeIR(0x50);

  // ---- MPU6500/9250 ----
  mpu.init();
  delay(200);
  mpu.setAccRange(MPU9250_ACC_RANGE_4G);
  mpu.setGyrRange(MPU9250_GYRO_RANGE_500);
  mpu.setSampleRateDivider(5);
  mpu.setAccDLPF(MPU9250_DLPF_6);
  mpu.setGyrDLPF(MPU9250_DLPF_6);
  delay(50);

  xyzFloat test = mpu.getGValues();
  float testMag = sqrtf(test.x * test.x + test.y * test.y + test.z * test.z);
  mpuOk = (testMag > 0.5f && testMag < 1.5f);

  if (mpuOk) {
    Serial.println("MPU ready");
  } else {
    Serial.printf("MPU init failed (mag=%.2f g) — motion detection disabled\n", testMag);
  }

  // ---- I2S ----
  setupI2S();

  startupMs = millis();
  Serial.println("Pink noise sleep aid ready.");
  Serial.println("Learning awake heart-rate baseline for 2 minutes...");
}

// ---------- Loop ----------
void loop() {
  unsigned long now = millis();
  long ir = hr.getIR();

  // ---- Beat detection ----
  if (checkForBeat(ir)) {
    unsigned long delta = now - lastBeatMs;
    lastBeatMs = now;

    if (delta > 250 && delta < 2000) {
      float instantBpm = 60000.0f / (float)delta;
      if (instantBpm >= 45.0f && instantBpm <= 65.0f) {
        bpm = instantBpm;
        pushBpm(instantBpm, now);

        // Accumulate baseline during the learning window
        if (!baselineLocked && (now - startupMs) < (BASELINE_LEARN_SECONDS * 1000.0f)) {
          baselineSumBpm += instantBpm;
          baselineSamples++;
        }
      }
    }
  }

  // ---- Lock baseline when learning window ends ----
  if (!baselineLocked && (now - startupMs) >= (BASELINE_LEARN_SECONDS * 1000.0f)) {
    if (baselineSamples > 10) {
      awakeBaseline = baselineSumBpm / baselineSamples;
      Serial.printf("Baseline locked: %.1f BPM (%d samples)\n",
                    awakeBaseline, baselineSamples);
    } else {
      awakeBaseline = 65.0f;
      Serial.println("Baseline learning failed (too few beats); default 65 BPM");
    }
    baselineLocked = true;
  }

  // ---- Motion polling (~50 Hz) ----
  if (now - lastMotionMs >= 20) {
    lastMotionMs = now;
    updateMotion();
  }

  // ---- Deep sleep state machine ----
  if (baselineLocked) {
    float avg60 = averageBpm60s(now);
    bool hrLow       = (avg60 > 0.0f) && (avg60 < awakeBaseline * HR_DROP_FRACTION);
    bool stillEnough = (motionLevel < STILLNESS_THRESHOLD);
    bool conditionsMet = hrLow && stillEnough;

    if (conditionsMet) {
      if (deepStartedMs == 0) deepStartedMs = now;
      lastDeepMs = now;

      if (now - deepStartedMs >= SUSTAINED_MS) {
        noiseActive = true;
      }
    } else {
      if (noiseActive && (now - lastDeepMs > RELEASE_GRACE_MS)) {
        noiseActive = false;
      }
      if (now - lastDeepMs > RELEASE_GRACE_MS) {
        deepStartedMs = 0;
      }
    }
  }

  // ---- Feed I2S continuously ----
  streamPinkChunk();

  // ---- Serial output (1 Hz) ----
  if (now - lastPrintMs >= 1000) {
    lastPrintMs = now;
    float avg60 = averageBpm60s(now);
    Serial.printf("BPM=%.1f  Avg60=%.1f  Base=%.1f  Motion=%.3f  Moving=%d  Noise=%s  Amp=%.0f\n",
                  bpm, avg60, awakeBaseline, motionLevel,
                  isMoving ? 1 : 0,
                  noiseActive ? "ON" : "off",
                  currentAmplitude);
  }
}