import skrf as rf
import matplotlib
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
from collections import defaultdict

matplotlib.style.use('tesis.mplstyle')

file_path = Path(__file__).parent.parent / "Measurements" / "PAE_Power_Contours.txt"

pae_data = defaultdict(lambda: defaultdict(list))
pwr_data = defaultdict(lambda: defaultdict(list))
current_mode = None

with open(file_path, "r") as f:
    for line in f:
        line = line.strip()

        if not line:
            continue

        if line.startswith("level"):
            if "PAE_contours" in line:
                current_mode = 'PAE'
            elif "Power_contours" in line:
                current_mode = 'PWR'
            else:
                current_mode = None
            continue

        if current_mode:
            parts = line.split()

            if len(parts) >= 6:
                try:
                    level      = float(parts[0])
                    contour_id = int(parts[1])
                    mag        = float(parts[3])
                    phase      = float(parts[5])

                    gamma = mag * np.exp(1j * np.deg2rad(phase))

                    if current_mode == 'PAE':
                        pae_data[level][contour_id].append(gamma)
                    else:
                        pwr_data[level][contour_id].append(gamma)

                except ValueError:
                    continue

pwr_levels = sorted(pwr_data.keys(), reverse=True)
pae_levels = sorted(pae_data.keys(), reverse=True)

c_pwr = 'red'
c_pae = 'blue'

fig = plt.figure()

# Smith Chart
ax = fig.add_axes([0.02, 0.02, 0.65, 0.96])
rf.plotting.smith(
    ax=ax,
    draw_labels=True,
    ref_imm=1.0,
    chart_type='z'
)

# Power contours
for lvl in pwr_levels:
    for cid in pwr_data[lvl]:
        pts = np.array(pwr_data[lvl][cid])

        if len(pts) < 2:
            continue

        ax.plot(
            pts.real,
            pts.imag,
            color=c_pwr,
            linestyle='-',
            linewidth=1
        )

# PAE contours
for lvl in pae_levels:
    for cid in pae_data[lvl]:
        pts = np.array(pae_data[lvl][cid])

        if len(pts) < 2:
            continue

        ax.plot(
            pts.real,
            pts.imag,
            color=c_pae,
            linestyle='-',
            linewidth=1
        )

# ------------------------------------------------------------------
# LEYENDA CENTRADA VERTICALMENTE
# ------------------------------------------------------------------

n_pwr = len(pwr_levels)
n_pae = len(pae_levels)

step  = 0.055
gap   = 0.03
title = 0.06

# Eje de leyenda ocupando toda la altura
ax_leg = fig.add_axes([0.68, 0.02, 0.31, 0.96])
ax_leg.axis('off')

# Altura total consumida por el contenido
content_height = (
    title + n_pwr * step +
    gap +
    title + n_pae * step
)

# Posición inicial para centrar verticalmente
y = (1.0 + content_height) / 2.0

# Título Power
ax_leg.text(
    0.0, y,
    "Power contour levels",
    color=c_pwr,
    transform=ax_leg.transAxes,
    fontsize=12,
    fontweight='bold',
    va='top',
    ha='left'
)

y -= title

# Valores Power
for lvl in pwr_levels:
    ax_leg.text(
        0.0, y,
        f"{lvl:.2f} dBm",
        color=c_pwr,
        transform=ax_leg.transAxes,
        fontsize=12,
        fontweight='bold',
        va='top',
        ha='left'
    )
    y -= step

# Separación
y -= gap

# Título PAE
ax_leg.text(
    0.0, y,
    "PAE contour levels",
    color=c_pae,
    transform=ax_leg.transAxes,
    fontsize=12,
    fontweight='bold',
    va='top',
    ha='left'
)

y -= title

# Valores PAE
for lvl in pae_levels:
    ax_leg.text(
        0.0, y,
        f"{lvl:.3f} %",
        color=c_pae,
        transform=ax_leg.transAxes,
        fontsize=12,
        fontweight='bold',
        va='top',
        ha='left'
    )
    y -= step

# Guardar
output_path = Path(__file__).parent.parent / "Figures" / "loadpull_plot.png"
output_path.parent.mkdir(parents=True, exist_ok=True)

fig.savefig(output_path, format='png', bbox_inches='tight')
print(f"Guardado: {output_path.resolve()}")