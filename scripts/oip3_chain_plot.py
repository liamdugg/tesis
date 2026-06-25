import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from pathlib import Path
from scipy.interpolate import interp1d
from matplotlib.transforms import blended_transform_factory

matplotlib.style.use('tesis.mplstyle')

SCRIPT_DIR	= Path(__file__).resolve().parent
MEAS_DIR	= SCRIPT_DIR.parent / "measurements"
OUTPUT_DIR	= SCRIPT_DIR.parent / "imgs"
OUTPUT_DIR.mkdir(exist_ok=True)

palette	= sns.color_palette("muted", 2)
c_oip3	= palette[0]   # azul
c_grid	= "#b0b0b0"   # gris para grilla y línea vertical

ATT_CORRECTION = 31.2 # dB
X_LIMIT_GHZ	   = 5.0  # GHz

df = pd.read_csv(MEAS_DIR / "CADENA_IMD_Sweep_-5dBm.csv", skiprows=6)
df = df.apply(pd.to_numeric, errors='coerce')
df = df.dropna()

freq_ghz = df["Freq(Hz)"] / 1e9
oip3     = df["OIP3(DB)"] + ATT_CORRECTION

mask	 = freq_ghz <= X_LIMIT_GHZ
freq_ghz = freq_ghz[mask]
oip3	 = oip3[mask]

# Interpolación
freq_interp	= np.linspace(freq_ghz.min(), freq_ghz.max(), len(freq_ghz) * 3)
oip3_interp	= interp1d(freq_ghz.values, oip3.values, kind='cubic', fill_value='extrapolate')(freq_interp)

# Plot
fig, ax = plt.subplots()

ax.plot(freq_ghz, oip3, color=c_oip3, label="OIP3")
ax.axvline(x=2.2, color=c_grid, linestyle='--', zorder=1)
t = blended_transform_factory(ax.transData, ax.transAxes)

ax.text(2.2 + 0.13, 0.275, "2.2 GHz", transform=t, rotation=270, va='top', ha='right', color=c_grid, fontsize=12)

x_mark = 2.2
y_mark = float(interp1d(freq_ghz.values, oip3.values, kind='cubic', fill_value='extrapolate')(x_mark))

ax.plot(x_mark, y_mark, marker='o', markersize=3, color='black', zorder=6)
ax.annotate(
	r"{:.1f} dBm".format(y_mark),
	xy=(x_mark, y_mark),
	xytext=(x_mark + 0.3, y_mark - 1.5),
	fontsize=12,
	color='black',
	arrowprops=dict(arrowstyle='->', color='black', lw=0.7),
)

ax.set_xlabel(r"Frecuencia (GHz)", labelpad=3)
ax.set_ylabel(r"OIP3 (dBm)", labelpad=3)
ax.set_xlim(freq_ghz.min(), freq_ghz.max())
ax.grid(True, linestyle='--', alpha=0.3)

plt.tight_layout()

output_path = OUTPUT_DIR / "oip3_plot.png"
fig.savefig(output_path, format='png')
print(f"Guardado: {output_path.resolve()}")