import matplotlib
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from pathlib import Path

matplotlib.style.use('tesis.mplstyle')
#plt.rcParams.update({'figure.dpi': '100'})

SCRIPT_DIR	= Path(__file__).resolve().parent
MEAS_DIR	= SCRIPT_DIR.parent / "Measurements"
OUTPUT_DIR	= SCRIPT_DIR.parent / "Figures"
OUTPUT_DIR.mkdir(exist_ok=True)

X_LIMIT_GHZ = (1.2, 3.2)

palette	= sns.color_palette("muted", 3)
c_lab	= palette[0]
c_ads	= palette[1]
c_cst	= palette[2]

lab = np.loadtxt(MEAS_DIR / "LAB_CNEA" / "parsed_data" / "s21_v2.dat", skiprows=1)
ads = np.loadtxt(MEAS_DIR / "ADS"      / "parsed_data" / "s21.dat"   , skiprows=1)
cst = np.loadtxt(MEAS_DIR / "CST"      / "parsed_data" / "s21.dat"   , skiprows=1)

fig, ax = plt.subplots()

ax.plot(lab[:, 0], lab[:, 1], color=c_lab, label=r"CNEA")
ax.plot(ads[:, 0], ads[:, 1], color=c_ads, label=r"ADS")
ax.plot(cst[:, 0], cst[:, 1], color=c_cst, label=r"CST")

ax.set_xlim(*X_LIMIT_GHZ)

ax.set_xlabel(r"Frecuencia (GHz)", labelpad=3)
ax.set_ylabel(r"$|S_{21}|$ (dB)" , labelpad=3)

ax.grid(True, linestyle='--', alpha=0.3)
ax.legend()

plt.tight_layout()
#plt.show()

fig.savefig(OUTPUT_DIR / "coupler_s21_lab_ads_cst.png", format='png')
print(f"\nGuardado\n")
