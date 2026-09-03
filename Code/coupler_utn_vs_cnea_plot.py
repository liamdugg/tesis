import matplotlib
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from pathlib import Path

matplotlib.style.use('tesis.mplstyle')
#plt.rcParams.update({'figure.dpi': '100'})

SCRIPT_DIR  = Path(__file__).resolve().parent
MEAS_DIR    = SCRIPT_DIR.parent / "Measurements"
OUTPUT_DIR  = SCRIPT_DIR.parent / "Figures"
OUTPUT_DIR.mkdir(exist_ok=True)

X_LIMIT_GHZ = (1.2, 3.2)

palette  = sns.color_palette("muted", 2)
c_s21    = palette[0]  # azul
c_s31    = palette[1]  # naranja

# Datos CNEA (medición definitiva, acoplador v2)
s21_cnea = np.loadtxt(MEAS_DIR / "LAB_CNEA" / "parsed_data" / "s21_v2.dat", skiprows=1)
s31_cnea = np.loadtxt(MEAS_DIR / "LAB_CNEA" / "parsed_data" / "s31_v2.dat", skiprows=1)

# Datos UTN (medición preliminar)
s21_utn  = np.loadtxt(MEAS_DIR / "LAB" / "parsed_data" / "s21.dat", skiprows=1)
s31_utn  = np.loadtxt(MEAS_DIR / "LAB" / "parsed_data" / "s31.dat", skiprows=1)

fig, ax = plt.subplots()

ax.plot(s21_cnea[:, 0], s21_cnea[:, 1], c=c_s21, ls='-' , label=r"$\mathrm{S_{21}}$ CNEA")
ax.plot(s21_utn[:, 0] , s21_utn[:, 1] , c=c_s21, ls='--', alpha=0.6, label=r"$\mathrm{S_{21}}$ UTN")

ax.plot(s31_cnea[:, 0], s31_cnea[:, 1], c=c_s31, ls='-' , label=r"$\mathrm{S_{31}}$ CNEA")
ax.plot(s31_utn[:, 0] , s31_utn[:, 1] , c=c_s31, ls='--', alpha=0.6, label=r"$\mathrm{S_{31}}$ UTN")

ax.set_xlim(*X_LIMIT_GHZ)

ax.set_xlabel(r"Frecuencia (GHz)", labelpad=3)
ax.set_ylabel(r"Magnitud (dB)"   , labelpad=3)

ax.grid(True, linestyle='--', alpha=0.3)
ax.legend()

plt.tight_layout()
#plt.show()

fig.savefig(OUTPUT_DIR / "coupler_utn_vs_cnea.png", format='png')
print("\nGuardado\n")