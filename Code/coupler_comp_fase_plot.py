import matplotlib
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from pathlib import Path
from scipy.interpolate import interp1d

matplotlib.style.use('tesis.mplstyle')
#plt.rcParams.update({'figure.dpi': '100'})

SCRIPT_DIR  = Path(__file__).resolve().parent
MEAS_DIR    = SCRIPT_DIR.parent / "Measurements"
OUTPUT_DIR  = SCRIPT_DIR.parent / "Figures"
OUTPUT_DIR.mkdir(exist_ok=True)

X_LIMIT_GHZ = (1.2, 3.2)
F_MARK      = 2.2  # GHz, frecuencia de interés

palette = sns.color_palette("muted", 3)
c_lab   = palette[0]
c_ads   = palette[1]
c_cst   = palette[2]

lab = np.loadtxt(MEAS_DIR / "LAB_CNEA" / "parsed_data" / "phase_difference_S21_S31_v2.dat", skiprows=1)
ads = np.loadtxt(MEAS_DIR / "ADS"      / "parsed_data" / "phase_difference_S21_S31.dat"   , skiprows=1)
cst = np.loadtxt(MEAS_DIR / "CST"      / "parsed_data" / "phase_difference_S21_S31.dat"   , skiprows=1)

fig, ax = plt.subplots()

datasets = [
    ("CNEA", lab, c_lab, -0.23,  20),
    ("ADS",  ads, c_ads, -0.15, -20),
    ("CST",  cst, c_cst,  0.25,  -7),
]

for label, data, color, x_offset, y_offset in datasets:

    mask  = (data[:, 0] >= X_LIMIT_GHZ[0]) & (data[:, 0] <= X_LIMIT_GHZ[1])
    freq  = data[mask, 0]
    phase = data[mask, 1]

    ax.plot(freq, phase, c=color, label=label)

    # interpola para encontrar valor de fase a 2.2 GHz
    y_mark = float(interp1d(freq, phase, kind='cubic')(F_MARK))

    ax.scatter(F_MARK, y_mark, marker='o', s=16, color='black',zorder=6)

    ax.annotate(
        r"{}: {:.2f}$^\circ$".format(label.split()[0], y_mark),
        xy         = (F_MARK, y_mark),
        xytext     = (F_MARK + x_offset, y_mark + y_offset),
        fontsize   = 12,
        arrowprops = dict(arrowstyle='->', lw=0.7),
    )

ax.set_xlim(*X_LIMIT_GHZ)
ax.set_xlabel(r"Frecuencia (GHz)"      , labelpad=3)
ax.set_ylabel(r"Diferencia de fase (°)", labelpad=3)
ax.grid(True, linestyle='--', alpha=0.3)
ax.legend()

plt.tight_layout()
#plt.show()

fig.savefig(OUTPUT_DIR / "coupler_fase_lab_ads_cst.png", format='png')
print("\nGuardado\n")