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
#define SAMPLE_RATE       16000
#define BEEP_FREQ_HZ        880
#define BEEP_DURATION_MS     80
#define BEEP_AMPLITUDE     8000

// ---------- BPM history (last 60 s) ----------
#define BPM_HISTORY_SIZE 256        // generous: 256 beats covers >60 s even at 240 BPM
struct BeatRecord { unsigned long t; float bpm; };
BeatRecord bpmHistory[BPM_HISTORY_SIZE];
int   bpmHead   = 0;                // next write slot
int   bpmCount  = 0;                // valid entries currently stored

// ---------- Motion detection ----------
float motionLevel   = 0.0f;         // smoothed |a - 1g|, in g
const float MOTION_ALPHA     = 0.15f;   // low-pass smoothing factor (0..1)
const float MOTION_THRESHOLD = 0.18f;   // g; above this = "moving"
bool  isMoving      = false;

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

void playBeep(int freqHz, int durationMs) {
  const int totalSamples = (SAMPLE_RATE * durationMs) / 1000;
  const int CHUNK = 128;
  int16_t buf[CHUNK];
  size_t written;
  int sampleIdx = 0;

  while (sampleIdx < totalSamples) {
    int n = min(CHUNK, totalSamples - sampleIdx);
    for (int i = 0; i < n; i++) {
      float t = (float)(sampleIdx + i) / SAMPLE_RATE;
      buf[i] = (int16_t)(sinf(2.0f * (float)M_PI * freqHz * t) * BEEP_AMPLITUDE);
    }
    i2s_write(I2S_NUM_0, buf, n * sizeof(int16_t), &written, portMAX_DELAY);
    sampleIdx += n;
  }
  memset(buf, 0, sizeof(buf));
  i2s_write(I2S_NUM_0, buf, sizeof(buf), &written, portMAX_DELAY);
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
    // walk backwards from the most recent entry
    int idx = (bpmHead - 1 - i + BPM_HISTORY_SIZE) % BPM_HISTORY_SIZE;
    if (now - bpmHistory[idx].t > 60000UL) break;   // older than 60 s
    sum += bpmHistory[idx].bpm;
    n++;
  }
  return (n > 0) ? (sum / n) : 0.0f;
}

// ---------- Motion ----------
void updateMotion() {
  if (!mpuOk) return;

  xyzFloat acc = mpu.getGValues();   // returns acceleration in g
  float mag = sqrtf(acc.x * acc.x + acc.y * acc.y + acc.z * acc.z);
  float deviation = fabsf(mag - 1.0f);                          // remove gravity
  motionLevel = MOTION_ALPHA * deviation + (1.0f - MOTION_ALPHA) * motionLevel;
  isMoving = (motionLevel > MOTION_THRESHOLD);
}

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
  mpuOk = mpu.init();
  if (mpuOk) {
    delay(1000);
    mpu.autoOffsets();
    mpu.setAccRange(MPU9250_ACC_RANGE_4G);
    mpu.setGyrRange(MPU9250_GYRO_RANGE_500);
    mpu.setSampleRateDivider(5);
    mpu.setAccDLPF(MPU9250_DLPF_6);
    mpu.setGyrDLPF(MPU9250_DLPF_6);
  } else {
    Serial.println("MPU init failed (motion detection disabled)");
  }

  setupI2S();

  Serial.println("IR,BPM,Avg60,Motion_g,Moving");
}

void loop() {
  unsigned long now = millis();
  long ir = hr.getIR();

  // ---- Beat detection ----
  if (checkForBeat(ir)) {
    unsigned long delta = now - lastBeatMs;
    lastBeatMs = now;

    if (delta > 250 && delta < 2000) {          // physiologically plausible interval
      float instantBpm = 60000.0f / (float)delta;
      if (instantBpm >= 40.0f && instantBpm <= 70.0f) {   // accept 40–70 only
        bpm = instantBpm;
        pushBpm(instantBpm, now);
      }
    }
    playBeep(BEEP_FREQ_HZ, BEEP_DURATION_MS);
  }

  // ---- Motion (poll at ~50 Hz) ----
  if (now - lastMotionMs >= 20) {
    lastMotionMs = now;
    updateMotion();
  }

  // ---- Serial output (10 Hz) ----
  if (now - lastPrintMs >= 100) {
    lastPrintMs = now;
    float avg60 = averageBpm60s(now);
    Serial.printf("%ld,%.1f,%.1f,%.3f,%d\n",
                  ir, bpm, avg60, motionLevel, isMoving ? 1 : 0);
  }
}