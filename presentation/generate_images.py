#!/usr/bin/env python3
"""
Generate device illustration images for Sleep Monitor beamer presentation.
Run from the presentation/ directory:  python3 generate_images.py
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Arc
import numpy as np
import os

# ── Colour palette (matches beamer theme) ─────────────────────
NAVY  = '#0B2545'
TEAL  = '#0D9488'
BLUE  = '#1E88E5'
MID   = '#1565C0'
BG    = '#F8FAFC'
GRAY  = '#94A3B8'
LGRAY = '#E2E8F0'
AMBER = '#F59E0B'
GREEN = '#16A34A'
WHITE = '#FFFFFF'
RED   = '#EF4444'

plt.rcParams.update({'font.family': 'sans-serif', 'font.size': 9})
os.makedirs('images', exist_ok=True)


# ── Helpers ───────────────────────────────────────────────────

def new_fig(w=5.0, h=5.3, xlim=(0, 10), ylim=(0, 10)):
    fig, ax = plt.subplots(figsize=(w, h), dpi=150)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis('off')
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    return fig, ax


def chip(ax, x, y, w, h, fc, ec, label, sub=None, lc=WHITE):
    """Rounded chip/module box with optional subtitle."""
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.1',
                                facecolor=fc, edgecolor=ec, linewidth=1.5,
                                zorder=3))
    ty = y + h / 2 + (0.18 if sub else 0)
    ax.text(x + w / 2, ty, label, color=lc, fontsize=7.5,
            ha='center', va='center', fontweight='bold', zorder=4)
    if sub:
        ax.text(x + w / 2, y + h / 2 - 0.28, sub, color=lc,
                fontsize=5.5, ha='center', va='center', alpha=0.8, zorder=4)


def dash(ax, x0, y0, x1, y1, color=BLUE, lw=1.2):
    ax.plot([x0, x1], [y0, y1], color=color, lw=lw,
            linestyle='dashed', alpha=0.65, zorder=2)


def arrow(ax, x0, y0, x1, y1, color=BLUE, lw=1.5, rad=0.0, label=None):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw,
                                connectionstyle=f'arc3,rad={rad}'), zorder=3)
    if label:
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        ax.text(mx, my + 0.3, label, color=color, fontsize=5.5,
                ha='center', va='center', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.18', facecolor=BG,
                          edgecolor=color + '88', lw=0.8), zorder=4)


# ═════════════════════════════════════════════════════════════
# 1. HEADBAND DEVICE
# ═════════════════════════════════════════════════════════════
fig, ax = new_fig()

# Band arc
theta = np.linspace(np.radians(18), np.radians(162), 120)
r, bx, by = 3.8, 5.0, 4.2
xb = bx + r * np.cos(theta)
yb = by + r * np.sin(theta)
ax.fill_between(xb, yb - 0.25, yb + 0.25, color=NAVY, alpha=0.15, zorder=1)
ax.plot(xb, yb, color=NAVY, lw=4, solid_capstyle='round', zorder=2)

# Elastic tails hanging down
for side in [18, 162]:
    ex = bx + r * np.cos(np.radians(side))
    ey = by + r * np.sin(np.radians(side))
    ax.plot([ex, ex], [ey - 0.05, ey - 1.1],
            color=NAVY, lw=3, alpha=0.45, solid_capstyle='round')

# ESP32 top of band
chip(ax, 3.25, 8.2, 3.5, 1.2, BLUE, WHITE, 'ESP32', 'MCU + ESP-NOW Radio')

# MPU-6050 left
chip(ax, 0.4, 5.6, 2.6, 1.0, NAVY, TEAL, 'MPU-6050', 'Gyro · Accel')

# MAX30102 right
chip(ax, 7.0, 5.6, 2.6, 1.0, NAVY, TEAL, 'MAX30102', 'SpO₂ · HR')

# Bone conduction actuator (bottom)
ax.add_patch(FancyBboxPatch((3.1, 1.85), 3.8, 1.35,
                             boxstyle='round,pad=0.1',
                             facecolor=AMBER + '33', edgecolor=AMBER,
                             linewidth=1.8, zorder=3))
ax.text(5.0, 2.72, 'Bone Conduction', color=AMBER, fontsize=7.5,
        ha='center', va='center', fontweight='bold', zorder=4)
ax.text(5.0, 2.18, 'Speaker  ·  Actuator', color=AMBER, fontsize=5.5,
        ha='center', va='center', alpha=0.8, zorder=4)

# Dashed connections
dash(ax, 3.5, 8.2, 2.7, 6.6)
dash(ax, 6.5, 8.2, 7.3, 6.6)
dash(ax, 5.0, 8.2, 5.0, 3.2)

fig.savefig('images/headband.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print('✓ headband.png')


# ═════════════════════════════════════════════════════════════
# 2. GATEWAY DEVICE
# ═════════════════════════════════════════════════════════════
fig, ax = new_fig()

# Device enclosure
ax.add_patch(FancyBboxPatch((0.9, 1.0), 8.2, 8.3,
                             boxstyle='round,pad=0.25',
                             facecolor=TEAL + '14', edgecolor=TEAL, lw=2))
ax.text(5.0, 9.8, 'Gateway Device', color=NAVY, fontsize=8,
        ha='center', va='center', fontweight='bold')

# ESP32 main chip
chip(ax, 2.9, 5.5, 4.2, 1.7, TEAL, WHITE, 'ESP32', 'Main Controller')

# OLED screen
ax.add_patch(FancyBboxPatch((2.3, 2.4), 5.4, 2.6,
                             boxstyle='round,pad=0.1',
                             facecolor=NAVY, edgecolor='#475569', lw=1.5,
                             zorder=3))
ax.text(5.0, 4.65, 'OLED Display', color='#94A3B8',
        fontsize=5.5, ha='center', va='center')
ax.text(5.0, 3.9, '♥  72 bpm', color='#4ADE80', fontsize=11,
        ha='center', va='center', fontweight='bold')
ax.text(5.0, 3.1, 'SpO₂  98 %', color=TEAL, fontsize=11,
        ha='center', va='center', fontweight='bold')

# Wi-Fi badge
ax.add_patch(FancyBboxPatch((7.3, 6.8), 1.4, 0.95,
                             boxstyle='round,pad=0.08',
                             facecolor=BLUE + '22', edgecolor=BLUE + '77', lw=1))
ax.text(8.0, 7.28, 'Wi-Fi', color=BLUE, fontsize=6.5,
        ha='center', va='center', fontweight='bold')

# Bluetooth badge
ax.add_patch(FancyBboxPatch((1.3, 6.8), 1.5, 0.95,
                             boxstyle='round,pad=0.08',
                             facecolor=MID + '22', edgecolor=MID + '77', lw=1))
ax.text(2.05, 7.28, 'BT', color=MID, fontsize=8,
        ha='center', va='center', fontweight='bold')

# Connections ESP32 → badges
dash(ax, 7.1, 6.4, 7.5, 6.8, BLUE)
dash(ax, 2.9, 6.4, 2.5, 6.8, MID)

# GPIO pins
for xi in np.linspace(2.2, 7.8, 9):
    ax.plot([xi, xi], [1.0, 0.55], color=NAVY, lw=2.5, solid_capstyle='round')
    ax.add_patch(Circle((xi, 0.42), 0.14, facecolor=NAVY + '66',
                        edgecolor='none'))

fig.savefig('images/gateway.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print('✓ gateway.png')


# ═════════════════════════════════════════════════════════════
# 3. CLINICAL CONTEXT  (slide 2 — "The Problem")
# ═════════════════════════════════════════════════════════════
fig, ax = new_fig()

# Room background
ax.add_patch(FancyBboxPatch((0.2, 0.2), 9.6, 9.6,
                             boxstyle='round,pad=0.1',
                             facecolor='#EFF6FF', edgecolor=LGRAY, lw=1))

# Bed
ax.add_patch(FancyBboxPatch((0.6, 0.8), 6.4, 3.6,
                             boxstyle='round,pad=0.15',
                             facecolor='#DBEAFE', edgecolor=MID + '55', lw=1.5,
                             zorder=1))
ax.add_patch(FancyBboxPatch((0.9, 3.3), 2.1, 1.0,
                             boxstyle='round,pad=0.1',
                             facecolor=WHITE, edgecolor=LGRAY, lw=1, zorder=2))
ax.add_patch(FancyBboxPatch((0.7, 0.9), 6.1, 2.5,
                             boxstyle='round,pad=0.1',
                             facecolor='#BFDBFE', edgecolor=MID + '33', lw=1,
                             zorder=2))

# Patient head
ax.add_patch(Circle((2.1, 3.75), 0.6, facecolor='#FDE68A',
                    edgecolor='#D97706', lw=1.5, zorder=4))

# Headband on patient
ax.add_patch(Arc((2.1, 3.75), 1.45, 1.1, angle=0,
                 theta1=15, theta2=165, color=NAVY, lw=3.5, zorder=5))

# Tiny sensor on headband
ax.add_patch(FancyBboxPatch((1.62, 4.35), 0.96, 0.42,
                             boxstyle='round,pad=0.04',
                             facecolor=BLUE, edgecolor=WHITE, lw=0.8, zorder=6))
ax.text(2.1, 4.56, 'sensor', color=WHITE, fontsize=4.5,
        ha='center', va='center', zorder=7)

# Traditional wires (the "problem")
for angle, ln in [(220, 1.5), (270, 1.3), (320, 1.6)]:
    rad = np.radians(angle)
    ax.plot([2.1, 2.1 + ln * np.cos(rad)],
            [3.15, 3.15 + ln * np.sin(rad)],
            color=RED, lw=1.5, ls='--', alpha=0.5, zorder=3)
ax.text(2.1, 1.2, 'intrusive wires', color=RED, fontsize=5,
        ha='center', alpha=0.65)

# Bedside table + gateway
ax.add_patch(FancyBboxPatch((7.5, 0.8), 2.1, 3.6,
                             boxstyle='round,pad=0.1',
                             facecolor='#F1F5F9', edgecolor=GRAY, lw=1,
                             zorder=1))
ax.add_patch(FancyBboxPatch((7.65, 2.4), 1.8, 1.6,
                             boxstyle='round,pad=0.08',
                             facecolor=TEAL + '30', edgecolor=TEAL, lw=1.2,
                             zorder=2))
ax.add_patch(FancyBboxPatch((7.82, 2.6), 1.46, 0.8,
                             boxstyle='round,pad=0.04',
                             facecolor=NAVY, edgecolor='#475569', lw=0.8,
                             zorder=3))
ax.text(8.55, 3.0, '98%  ♥72', color=TEAL, fontsize=5.5,
        ha='center', va='center', fontweight='bold', zorder=4)
ax.text(8.55, 2.15, 'Gateway', color=TEAL, fontsize=5.5,
        ha='center', va='center', fontweight='bold')

# Cloud
for (cx, cy, cr) in [(7.1, 8.2, 0.55), (7.75, 8.55, 0.7), (8.45, 8.2, 0.55)]:
    ax.add_patch(Circle((cx, cy), cr, facecolor=TEAL + '44',
                        edgecolor='none', zorder=2))
ax.add_patch(FancyBboxPatch((6.6, 7.8), 2.3, 0.5,
                             boxstyle='square,pad=0',
                             facecolor=TEAL + '44', edgecolor='none', zorder=1))
ax.text(7.7, 8.2, 'Cloud', color=TEAL, fontsize=6.5,
        ha='center', va='center', fontweight='bold', zorder=3)

# Doctor dashboard (top left)
ax.add_patch(FancyBboxPatch((0.5, 6.0), 4.5, 3.5,
                             boxstyle='round,pad=0.1',
                             facecolor=WHITE, edgecolor=LGRAY, lw=1, zorder=1))
ax.add_patch(FancyBboxPatch((0.6, 6.1), 4.3, 2.5,
                             boxstyle='round,pad=0.05',
                             facecolor=NAVY, edgecolor='none', zorder=2))
xch = np.linspace(0.75, 4.75, 30)
yc1 = 7.1 + 0.3 * np.sin(np.linspace(0, 5, 30))
yc2 = 7.7 + 0.2 * np.sin(np.linspace(1, 6, 30))
ax.plot(xch, yc1, color=TEAL, lw=1.5, zorder=3)
ax.plot(xch, yc2, color=BLUE, lw=1.5, zorder=3)
ax.text(2.75, 9.0, "Doctor's Dashboard", color=NAVY, fontsize=5.5,
        ha='center', va='center', fontweight='bold')

# Arrows
arrow(ax, 3.5, 4.5, 7.55, 3.3, BLUE, 1.5, rad=-0.2, label='ESP-NOW')
arrow(ax, 8.55, 4.2, 7.9, 7.6, TEAL, 1.5, rad=0.25, label='MQTT')
arrow(ax, 7.1, 8.4, 5.1, 8.6, MID, 1.2, rad=0.1, label='API')

fig.savefig('images/clinical_ward.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print('✓ clinical_ward.png')


# ═════════════════════════════════════════════════════════════
# 4. DOCTOR DASHBOARD MOCKUP  (slide 9)
# ═════════════════════════════════════════════════════════════
fig, ax = new_fig(w=5.8, h=5.0, xlim=(0, 11.6), ylim=(0, 10))

# Window chrome
ax.add_patch(FancyBboxPatch((0.1, 0.1), 11.4, 9.8,
                             boxstyle='round,pad=0.1',
                             facecolor='#F1F5F9', edgecolor=LGRAY, lw=1.5))
# Nav bar
ax.add_patch(FancyBboxPatch((0.1, 8.85), 11.4, 1.05,
                             boxstyle='round,pad=0.05',
                             facecolor=NAVY, edgecolor='none'))
ax.text(5.9, 9.38, 'Sleep Monitor  —  Doctor Dashboard',
        color=WHITE, fontsize=7, ha='center', va='center', fontweight='bold')

# ── Sidebar ──────────────────────────────────────────────────
ax.add_patch(FancyBboxPatch((0.2, 0.2), 2.5, 8.5,
                             boxstyle='round,pad=0.05',
                             facecolor=WHITE, edgecolor=LGRAY, lw=1))
ax.text(1.45, 8.4, 'Patients', color=NAVY, fontsize=6.5,
        ha='center', va='center', fontweight='bold')

names = ['P. Silva', 'J. Costa', 'M. Ramos', 'A. Nunes']
pcols = [TEAL, BLUE, NAVY, GRAY]
for i, (nm, cl) in enumerate(zip(names, pcols)):
    y0 = 7.4 - i * 1.45
    ax.add_patch(FancyBboxPatch((0.3, y0 - 0.42), 2.3, 1.12,
                                 boxstyle='round,pad=0.05',
                                 facecolor=cl + '44' if i == 0 else cl + '18',
                                 edgecolor=cl + '66', lw=0.9))
    ax.text(1.35, y0 + 0.13, nm, color=NAVY, fontsize=5.5,
            ha='center', va='center',
            fontweight='bold' if i == 0 else 'normal')
    ax.add_patch(Circle((2.35, y0 + 0.13), 0.15, facecolor=cl))

# ── SpO2 chart ────────────────────────────────────────────────
ax.add_patch(FancyBboxPatch((2.9, 5.1), 4.0, 3.6,
                             boxstyle='round,pad=0.1',
                             facecolor=WHITE, edgecolor=LGRAY, lw=1))
ax.text(4.9, 8.4, 'SpO₂ (%)', color=NAVY, fontsize=6,
        ha='center', va='center', fontweight='bold')
rng = np.random.RandomState(42)
xc = np.linspace(3.05, 6.7, 35)
yc = 6.6 + 0.35 * np.sin(np.linspace(0, 5, 35)) + 0.07 * rng.randn(35)
ax.plot(xc, yc, color=TEAL, lw=2, zorder=2)
ax.plot([3.05, 6.7], [6.25, 6.25], color=TEAL + '55', lw=1, ls='--')
ax.text(6.75, 6.6, '98%', color=TEAL, fontsize=6,
        ha='left', va='center', fontweight='bold')

# ── HR chart ──────────────────────────────────────────────────
ax.add_patch(FancyBboxPatch((7.2, 5.1), 4.2, 3.6,
                             boxstyle='round,pad=0.1',
                             facecolor=WHITE, edgecolor=LGRAY, lw=1))
ax.text(9.3, 8.4, 'Heart Rate (bpm)', color=NAVY, fontsize=6,
        ha='center', va='center', fontweight='bold')
rng2 = np.random.RandomState(7)
xc2 = np.linspace(7.35, 11.2, 35)
yc2 = 6.6 + 0.5 * np.sin(np.linspace(0, 6, 35)) + 0.1 * rng2.randn(35)
ax.plot(xc2, yc2, color=BLUE, lw=2, zorder=2)
ax.text(11.25, 6.6, '72', color=BLUE, fontsize=6,
        ha='left', va='center', fontweight='bold')

# ── Control panel ─────────────────────────────────────────────
ax.add_patch(FancyBboxPatch((2.9, 0.3), 8.5, 4.5,
                             boxstyle='round,pad=0.1',
                             facecolor=WHITE, edgecolor=LGRAY, lw=1))
ax.text(7.15, 4.5, 'Therapy Control', color=NAVY, fontsize=6.5,
        ha='center', va='center', fontweight='bold')

# Frequency slider
ax.text(3.4, 3.85, 'Sound Freq.', color=GRAY, fontsize=5.5, va='center')
ax.add_patch(FancyBboxPatch((5.2, 3.62), 4.5, 0.38,
                             boxstyle='round,pad=0.05',
                             facecolor=LGRAY, edgecolor='none'))
ax.add_patch(FancyBboxPatch((5.2, 3.62), 2.8, 0.38,
                             boxstyle='round,pad=0.05',
                             facecolor=TEAL, edgecolor='none'))
ax.add_patch(Circle((8.0, 3.81), 0.3, facecolor=WHITE,
                    edgecolor=TEAL, lw=2, zorder=3))
ax.text(10.2, 3.81, '40 Hz', color=TEAL, fontsize=6,
        ha='center', va='center', fontweight='bold')

# Vital cards
vitals = [('SpO₂', '98 %', TEAL), ('Heart Rate', '72 bpm', BLUE),
          ('Movement', 'Low', GREEN)]
for i, (lbl, val, cl) in enumerate(vitals):
    xv = 3.7 + i * 2.7
    ax.add_patch(FancyBboxPatch((xv - 0.9, 1.1), 2.3, 2.1,
                                 boxstyle='round,pad=0.08',
                                 facecolor=cl + '1A', edgecolor=cl + '66',
                                 lw=1))
    ax.text(xv + 0.25, 2.38, val, color=cl, fontsize=8.5,
            ha='center', va='center', fontweight='bold')
    ax.text(xv + 0.25, 1.58, lbl, color=NAVY, fontsize=5,
            ha='center', va='center')

fig.savefig('images/dashboard.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print('✓ dashboard.png')

# ═════════════════════════════════════════════════════════════
# 5. COMPONENT LAYOUT  (slide 10 — wide strip)
# ═════════════════════════════════════════════════════════════
fig, ax = new_fig(w=11.0, h=2.6, xlim=(0, 22), ylim=(0, 5))

# ── Section backgrounds ───────────────────────────────────────
ax.add_patch(FancyBboxPatch((0.1, 0.2), 12.8, 4.5,
                             boxstyle='round,pad=0.1',
                             facecolor=BLUE + '0C', edgecolor=BLUE + '44',
                             lw=1.2, linestyle='--'))
ax.add_patch(FancyBboxPatch((13.3, 0.2), 8.5, 4.5,
                             boxstyle='round,pad=0.1',
                             facecolor=TEAL + '0C', edgecolor=TEAL + '44',
                             lw=1.2, linestyle='--'))

ax.text(6.55, 4.4, 'Headband', color=BLUE, fontsize=7,
        ha='center', va='center', fontweight='bold')
ax.text(17.55, 4.4, 'Gateway', color=TEAL, fontsize=7,
        ha='center', va='center', fontweight='bold')

# ── I2C bus lines ─────────────────────────────────────────────
# Headband bus (horizontal backbone)
ax.plot([1.1, 11.8], [1.5, 1.5], color=BLUE + '55', lw=2, zorder=1)
ax.text(6.5, 1.15, 'I²C / GPIO', color=BLUE + '88', fontsize=5.5,
        ha='center', va='center')
# Gateway bus
ax.plot([14.2, 20.8], [1.5, 1.5], color=TEAL + '55', lw=2, zorder=1)

# ── Helper: draw a component ──────────────────────────────────
def comp(ax, x, y, w, h, fc, ec, label, sub=None, lc=WHITE):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle='round,pad=0.08',
                                facecolor=fc, edgecolor=ec,
                                lw=1.4, zorder=3))
    ty = y + h / 2 + (0.18 if sub else 0)
    ax.text(x + w / 2, ty, label, color=lc, fontsize=6.5,
            ha='center', va='center', fontweight='bold', zorder=4)
    if sub:
        ax.text(x + w / 2, y + h / 2 - 0.25, sub, color=lc,
                fontsize=5, ha='center', va='center', alpha=0.8, zorder=4)
    # Tap down to bus
    cx = x + w / 2
    ax.plot([cx, cx], [y, 1.5], color=ec + '77', lw=1.2,
            ls='dashed', zorder=2)

# ── Headband components ───────────────────────────────────────
comp(ax, 0.2,  1.8, 2.4, 2.0, BLUE,  WHITE, 'ESP32',         'MCU')
comp(ax, 3.1,  1.8, 2.3, 1.6, NAVY,  TEAL,  'MPU-6050',      'Gyro · Accel')
comp(ax, 5.9,  1.8, 2.3, 1.6, NAVY,  TEAL,  'MAX30102',       'SpO₂ · HR')
comp(ax, 9.2,  1.8, 2.6, 1.6, AMBER + '33', AMBER,
     'Bone Cond.', 'Speaker', AMBER)

# ── ESP-NOW link between the two boards ──────────────────────
ax.annotate('', xy=(13.2, 2.55), xytext=(12.0, 2.55),
            arrowprops=dict(arrowstyle='<->', color=MID, lw=1.5,
                            connectionstyle='arc3,rad=0'))
ax.text(12.6, 3.5, 'ESP-NOW', color=MID, fontsize=5.5,
        ha='center', va='center', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.18', facecolor=BG,
                  edgecolor=MID + '77', lw=0.9), zorder=5)

# ── Gateway components ────────────────────────────────────────
comp(ax, 13.4, 1.8, 2.4, 2.0, TEAL,  WHITE, 'ESP32',    'MCU')
comp(ax, 17.0, 1.8, 3.6, 1.6, NAVY,  '#475569',
     'OLED Display', '98%  ♥ 72', TEAL)

fig.savefig('images/component_layout.png', dpi=150,
            bbox_inches='tight', facecolor=BG)
plt.close()
print('✓ component_layout.png')

print('\nAll images saved to presentation/images/')
