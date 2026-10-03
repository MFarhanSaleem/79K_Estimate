# Schematic solar layout (Register J3) drawn on the measured terrace outline (roof_rev1.json).
# Coordinates in feet from the rear-left corner of the building, x to the right, y towards the road.
import json, os, sys, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'solar_layout.png')
ROOF = json.load(open(os.path.join(HERE, 'roof_rev1.json')))

PW, PH = 2.384 / 0.3048, 1.303 / 0.3048           # panel 7.82 ft x 4.27 ft
COS = math.cos(math.radians(15))
GAP = 0.08                                        # ~1" between panels

def table(x0, y_front, n_across, n_high, landscape=True):
    """Return panel rectangles (plan) of a table whose low (front) edge is at y_front."""
    w, d = (PW, PH) if landscape else (PH, PW)
    depth = n_high * d * COS
    rects = [(x0 + i * (w + GAP), y_front - depth + j * d * COS, w, d * COS) for i in range(n_across) for j in range(n_high)]
    return rects, depth, n_across * (w + GAP) - GAP

def plinths(x0, y_front, width, depth, n_frames):
    xs = [x0 + k * width / (n_frames - 1) for k in range(n_frames)]
    return [(x - 0.625, y - 0.625) for x in xs for y in (y_front - depth + 0.9, y_front - 0.9)]

fig, ax = plt.subplots(figsize=(7.6, 9.6), dpi=200)
T = ROOF['T_coords']
ax.add_patch(Polygon(T, closed=True, fc='#EEF2F7', ec='#1F3864', lw=1.4))
# mumty blocks (outer outline) and open shaft
ax.add_patch(Rectangle((2.78, 0), 16.85, 7.75, fc='#D9D9D9', ec='#404040', lw=1.2))
ax.add_patch(Rectangle((19.63, 0), 17.63, 12.63, fc='#D9D9D9', ec='#404040', lw=1.2))
ax.add_patch(Rectangle((32.89, 19.5), 4.0, 14.39, fc='white', ec='#7F7F7F', lw=0.8, hatch='////'))
ax.text(34.9, 26.7, 'OPEN\nSHAFT', ha='center', va='center', fontsize=6.5, color='#595959')
ax.text(11.2, 1.0, 'MUMTY ROOF (stair block)', ha='center', fontsize=6.5, color='#404040')
ax.text(25.2, 11.5, 'MUMTY ROOF (room block)', ha='center', fontsize=6.5, color='#404040')
# tank platform on mumty roof, rear-right corner
ax.add_patch(Rectangle((31.76, 0.5), 5.0, 5.0, fc='#BDD7EE', ec='#2E5597', lw=1.0))
ax.text(34.26, 3.0, 'Tank\nplatform\n5\'x5\'', ha='center', va='center', fontsize=6, color='#1F3864')

rows = [  # (label, x0, y_front, across, high, landscape, frames)
    ('Row 1: 8 panels (4 x 2)', 1.5, 46.01, 4, 2, True, 5),
    ('Row 2: 6 panels (3 x 2)', 7.89, 34.51, 3, 2, True, 4),
    ('Row 3: 6 panels (3 x 2)', 7.89, 23.01, 3, 2, True, 4),
    ('2 panels', 21.0, 10.6, 2, 1, False, 2),
    ('1 panel', 7.4, 6.4, 1, 1, True, 2),
]
n_pan = n_pl = 0
for lab, x0, yf, na, nh, land, nf in rows:
    rects, depth, width = table(x0, yf, na, nh, land)
    for (x, y, w, h) in rects:
        ax.add_patch(Rectangle((x, y), w, h, fc='#2E5597', ec='white', lw=0.6, alpha=0.9))
        n_pan += 1
    for (px, py) in plinths(x0, yf, width, depth, nf):
        ax.add_patch(Rectangle((px, py), 1.25, 1.25, fc='#C00000', ec='black', lw=0.4, zorder=5))
        n_pl += 1
    ax.text(x0 + width / 2, yf - depth / 2, lab, ha='center', va='center', fontsize=6.5, color='white', fontweight='bold', zorder=6)
assert n_pan == 23 and n_pl == 34, (n_pan, n_pl)

ax.annotate('', xy=(39.2, 46.01), xytext=(39.2, 34.51), arrowprops=dict(arrowstyle='<->', lw=0.7))
ax.text(39.5, 40.3, "pitch\n11'-6\"", fontsize=6, va='center')
ax.annotate('', xy=(39.2, 34.51), xytext=(39.2, 23.01), arrowprops=dict(arrowstyle='<->', lw=0.7))
ax.text(39.5, 28.8, "pitch\n11'-6\"", fontsize=6, va='center')
ax.annotate('', xy=(39.2, 48.26), xytext=(39.2, 46.01), arrowprops=dict(arrowstyle='<->', lw=0.7))
ax.text(39.5, 47.4, "2'-3\"", fontsize=6, va='center')
ax.text(18.6, 52.3, 'FRONT / ROAD SIDE (assumed SOUTH - panels face this way, tilt 15°)', ha='center', fontsize=7, color='#1F3864', fontweight='bold')
ax.annotate('N\n(assumed)', xy=(-8.0, 3.0), xytext=(-8.0, 9.0), ha='center', fontsize=6.5,
            arrowprops=dict(arrowstyle='-|>', lw=1.0, color='black'))
ax.add_patch(Rectangle((-13.0, 16.0), 1.25, 1.25, fc='#C00000', ec='black', lw=0.4))
ax.text(-11.4, 16.6, '= RCC plinth\n15"x15"x12" with\n2 cast-in M12\nJ-bolts (34 nos)', fontsize=5.8, va='center')
ax.add_patch(Rectangle((-13.0, 22.0), 1.25, 1.25, fc='#2E5597', ec='white', lw=0.4))
ax.text(-11.4, 22.6, '= 650 W panel\n(23 nos)', fontsize=5.8, va='center')
ax.set_xlim(-14.0, 42.5); ax.set_ylim(54.0, -1.5)        # road at the bottom, as on the architect's plans
ax.set_aspect('equal'); ax.axis('off')
ax.set_title('Schematic solar layout - terrace (first-floor roof) and mumty roof\n23 x 650 W = 14.95 kWp, 34 plinths (not for setting out; confirm north on site)',
             fontsize=8, color='#1F3864')
fig.tight_layout()
fig.savefig(OUT, dpi=200, bbox_inches='tight', pad_inches=0.08)
print('saved', OUT, n_pan, 'panels', n_pl, 'plinths')
