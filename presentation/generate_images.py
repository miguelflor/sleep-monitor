#!/usr/bin/env python3
"""
Generate device illustration images for Sleep Monitor beamer presentation.
Run from the presentation/ directory:  python3 generate_images.py
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Arc, PathPatch, Ellipse
from matplotlib.path import Path
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


def draw_cloud(ax, cx, cy, w, h, fc, zorder=2):
    """Smooth 3-bump cloud drawn as a single bezier path."""
    # Normalised vertices in [-0.5, 0.5] × [-0.35, 0.50]
    # MOVETO + 4×CURVE4 (12 pts) + CLOSEPOLY = 14 entries
    verts = [
        (-0.50, -0.30),                              # MOVETO  bottom-left
        (-0.50,  0.02), (-0.40,  0.30), (-0.24, 0.30),  # left bump
        (-0.10,  0.30), (-0.13,  0.50), ( 0.00, 0.50),  # up to centre bump
        ( 0.13,  0.50), ( 0.10,  0.30), ( 0.24, 0.30),  # down to right bump
        ( 0.40,  0.30), ( 0.50,  0.02), ( 0.50, -0.30), # right side down
        (-0.50, -0.30),                              # CLOSEPOLY
    ]
    codes = [
        Path.MOVETO,
        Path.CURVE4, Path.CURVE4, Path.CURVE4,
        Path.CURVE4, Path.CURVE4, Path.CURVE4,
        Path.CURVE4, Path.CURVE4, Path.CURVE4,
        Path.CURVE4, Path.CURVE4, Path.CURVE4,
        Path.CLOSEPOLY,
    ]
    scaled = [(cx + x * w, cy + y * h) for x, y in verts]
    ax.add_patch(PathPatch(Path(scaled, codes),
                           facecolor=fc, edgecolor='none', zorder=zorder))


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
# 1. HEADBAND DEVICE  —  drawsvg illustrated style
# ═════════════════════════════════════════════════════════════
import drawsvg as dw

W, H = 520, 560
d = dw.Drawing(W, H, id_prefix='hb')

# palette
_NAVY  = '#0B2545'; _TEAL  = '#0D9488'; _BLUE  = '#1E88E5'
_MID   = '#1565C0'; _AMBER = '#F59E0B'; _WHITE = '#FFFFFF'
_SKIN  = '#FDDBB4'; _SKND  = '#C9884E'; _HAIR  = '#2C1B0E'
_BG    = '#F8FAFC'; _LBGE  = '#ECF5FF'

d.append(dw.Rectangle(0, 0, W, H, fill=_BG))
d.append(dw.Circle(260, 295, 240, fill=_LBGE))

# ── Head geometry ─────────────────────────────────────
HCX, HCY = 260, 300   # head centre
HW,  HH  = 88,  112   # half-width, half-height

# ── Shoulders ─────────────────────────────────────────
sp = dw.Path(fill=_SKIN, stroke=_SKND, stroke_width=1)
sp.M(HCX-120, H).L(HCX-110, HCY+HH+55).C(HCX-60, HCY+HH+35, HCX-28, HCY+HH+18, HCX-22, HCY+HH+5)
sp.L(HCX+22, HCY+HH+5).C(HCX+28, HCY+HH+18, HCX+60, HCY+HH+35, HCX+110, HCY+HH+55)
sp.L(HCX+120, H).Z()
d.append(sp)

# ── Neck ──────────────────────────────────────────────
d.append(dw.Rectangle(HCX-22, HCY+HH-8, 44, 70, rx=7, ry=7,
                       fill=_SKIN, stroke=_SKND, stroke_width=1))

# ── Ears ──────────────────────────────────────────────
for sx in [-1, 1]:
    d.append(dw.Ellipse(HCX + sx*(HW+2), HCY+8, 11, 20,
                         fill=_SKIN, stroke=_SKND, stroke_width=1))

# ── Head shape: bezier for natural silhouette ─────────
def head_path_d():
    p = dw.Path(fill=_SKIN, stroke=_SKND, stroke_width=1.5)
    p.M(HCX, HCY - HH)
    # right side: crown → temple → jaw → chin
    p.C(HCX+HW*0.62, HCY-HH,       HCX+HW,     HCY-HH*0.32, HCX+HW,     HCY+HH*0.08)
    p.C(HCX+HW,      HCY+HH*0.52,  HCX+HW*0.6, HCY+HH*0.82, HCX+HW*0.3, HCY+HH)
    # chin
    p.C(HCX+HW*0.10, HCY+HH*1.07,  HCX-HW*0.10, HCY+HH*1.07, HCX-HW*0.3, HCY+HH)
    # left side: jaw → temple → crown
    p.C(HCX-HW*0.6,  HCY+HH*0.82,  HCX-HW,     HCY+HH*0.52, HCX-HW,     HCY+HH*0.08)
    p.C(HCX-HW,      HCY-HH*0.32,  HCX-HW*0.62, HCY-HH,      HCX,        HCY-HH)
    p.Z()
    return p

# clip path for masking hair to head outline
clip = dw.ClipPath(id='hd-clip')
clip.append(head_path_d())
d.append(clip)

# head fill
d.append(head_path_d())

# ── Hair: ellipse clipped to head shape ───────────────
hair_grp = dw.Group(clip_path='url(#hd-clip)')
hair_grp.append(dw.Ellipse(HCX, HCY - HH*0.38, HW*1.06, HH*0.76, fill=_HAIR))
d.append(hair_grp)

# re-draw lower face over hair bottom edge
lower = dw.Path(fill=_SKIN, stroke=_SKND, stroke_width=1.5)
HAIR_CUT = HCY - HH*0.18   # y where hair ends / face re-appears
lower.M(HCX - HW*0.98, HAIR_CUT)
# follow head bezier on left side from HAIR_CUT down to chin, then back up right side
lower.C(HCX-HW*0.98, HCY-HH*0.05, HCX-HW, HCY+HH*0.2, HCX-HW, HCY+HH*0.08)
lower.C(HCX-HW, HCY+HH*0.52, HCX-HW*0.6, HCY+HH*0.82, HCX-HW*0.3, HCY+HH)
lower.C(HCX-HW*0.10, HCY+HH*1.07, HCX+HW*0.10, HCY+HH*1.07, HCX+HW*0.3, HCY+HH)
lower.C(HCX+HW*0.6, HCY+HH*0.82, HCX+HW, HCY+HH*0.52, HCX+HW, HCY+HH*0.08)
lower.C(HCX+HW, HCY-HH*0.05, HCX+HW*0.98, HAIR_CUT, HCX+HW*0.98, HAIR_CUT)
lower.Z()
d.append(lower)

# ── Eyes ──────────────────────────────────────────────
EYE_Y = HCY + 14
for ex in [HCX-30, HCX+30]:
    d.append(dw.Ellipse(ex, EYE_Y, 12, 8, fill='#2C1B0E'))
    # small white highlight
    d.append(dw.Ellipse(ex+5, EYE_Y-3, 3, 2, fill='rgba(255,255,255,0.5)'))

# ── Headband: horizontal elastic around head ──────────
# band centre y sits just at the hairline/forehead boundary
BAND_CY = HCY - int(HH * 0.60)   # ~233  (forehead level)
BHW_PX  = 17                      # half-height of band in pixels

# half-width of head at band top/bottom/centre (ellipse approximation)
def hw_at(y):
    dy = (y - HCY) / HH
    return HW * (1 - dy*dy)**0.5 if abs(dy) < 1 else 0

xc = hw_at(BAND_CY);       xwt = hw_at(BAND_CY - BHW_PX);  xwb = hw_at(BAND_CY + BHW_PX)

# drop-shadow
shp = dw.Path(fill='rgba(0,0,0,0.10)')
shp.M(HCX-xwt+3, BAND_CY-BHW_PX+4).L(HCX+xwt+3, BAND_CY-BHW_PX+4)
shp.L(HCX+xwb+3, BAND_CY+BHW_PX+4).L(HCX-xwb+3, BAND_CY+BHW_PX+4).Z()
d.append(shp)

# band front face (trapezoid)
bp = dw.Path(fill=_NAVY)
bp.M(HCX-xwt, BAND_CY-BHW_PX).L(HCX+xwt, BAND_CY-BHW_PX)
bp.L(HCX+xwb, BAND_CY+BHW_PX).L(HCX-xwb, BAND_CY+BHW_PX).Z()
d.append(bp)

# top-edge highlight strip
d.append(dw.Line(HCX-xwt+2, BAND_CY-BHW_PX+5, HCX+xwt-2, BAND_CY-BHW_PX+5,
                  stroke='rgba(255,255,255,0.22)', stroke_width=2))

# side caps (half-ellipses suggesting wrap-around)
for sx in [-1, 1]:
    cap_cx = HCX + sx * xc
    # semi-circle cap, slightly squashed
    cap = dw.Path(fill=_NAVY, fill_opacity=0.65)
    if sx > 0:
        cap.M(cap_cx, BAND_CY-BHW_PX).A(13, BHW_PX, 0, 0, 1, cap_cx, BAND_CY+BHW_PX).Z()
    else:
        cap.M(cap_cx, BAND_CY-BHW_PX).A(13, BHW_PX, 0, 0, 0, cap_cx, BAND_CY+BHW_PX).Z()
    d.append(cap)

# ── Callout helper ────────────────────────────────────
def sv_callout(d, dot_x, dot_y, lx, ly, label, sub, fc, ec, dot_r=8):
    # dashed line
    d.append(dw.Line(dot_x, dot_y, lx, ly,
                      stroke=ec, stroke_width=1.2,
                      stroke_dasharray='5,4', stroke_opacity=0.65))
    # dot on band
    d.append(dw.Circle(dot_x, dot_y, dot_r, fill=ec, stroke=_WHITE, stroke_width=1.5))
    # label box
    BW, BH = 86, 34
    d.append(dw.Rectangle(lx-BW//2, ly-BH//2, BW, BH, rx=6, ry=6,
                            fill=fc, stroke=ec, stroke_width=1.5))
    d.append(dw.Text(label, font_size=11, x=lx, y=ly - (4 if sub else 0),
                      fill=_WHITE, text_anchor='middle', font_weight='bold',
                      font_family='sans-serif'))
    if sub:
        d.append(dw.Text(sub, font_size=8, x=lx, y=ly+10,
                          fill=_WHITE, text_anchor='middle',
                          font_family='sans-serif', fill_opacity=0.85))

# MAX30102 — forehead centre
sv_callout(d, HCX+12, BAND_CY, 385, 95, 'MAX30102', 'SpO2 & HR',    _NAVY, _TEAL)
# MPU-6050 — top of band (hairline)
sv_callout(d, HCX-12, BAND_CY-BHW_PX, 130, 55, 'MPU-6050', 'Gyro & Accel', _NAVY, _TEAL)
# Bone Conduction — left temple
sv_callout(d, int(HCX-xc), BAND_CY, 68, BAND_CY, 'Bone Cond.', 'Speaker', '#7A4500', _AMBER)
# ESP32 — right side
sv_callout(d, int(HCX+xc), BAND_CY, 452, BAND_CY, 'ESP32', 'MCU & Radio', _BLUE, _MID)

# title
d.append(dw.Text('Wearable Headband', font_size=15, x=W//2, y=H-18,
                  fill=_NAVY, text_anchor='middle', font_weight='bold',
                  font_family='sans-serif'))

d.save_png('images/headband.png')
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

# ── Patient: head on pillow, body under covers ────────────────
hx, hy, hr = 2.1, 3.7, 0.42   # head centre + radius

# Head (skin-toned circle)
ax.add_patch(Circle((hx, hy), hr, facecolor='#FDDBB4',
                    edgecolor='#C9884E', lw=1.5, zorder=4))

# Headband — horizontal line across the head at forehead level
band_y = hy + hr * 0.28
band_hw = np.sqrt(max(0.0, hr**2 - (band_y - hy)**2))
ax.plot([hx - band_hw, hx + band_hw], [band_y, band_y],
        color=NAVY, lw=4.0, solid_capstyle='round', zorder=6)

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
draw_cloud(ax, cx=7.75, cy=8.3, w=2.6, h=1.4, fc=TEAL + '44', zorder=2)
ax.text(7.75, 8.2, 'Cloud', color=TEAL, fontsize=6.5,
        ha='center', va='center', fontweight='bold', zorder=4)

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
arrow(ax, 2.6, 3.7, 7.55, 3.3, BLUE, 1.5, rad=-0.20, label='ESP-NOW')
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
