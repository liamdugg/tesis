import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from pathlib import Path

matplotlib.style.use('tesis.mplstyle')
#plt.rcParams.update({"figure.dpi": 100}) 

SCRIPT_DIR	= Path(__file__).resolve().parent
MEAS_DIR	= SCRIPT_DIR.parent / "Measurements"
OUTPUT_DIR	= SCRIPT_DIR.parent / "Figures"
OUTPUT_DIR.mkdir(exist_ok=True)

palette	      = sns.color_palette("muted", 2)
c_drain	      = palette[0]
c_pae	      = palette[1]
c_grid	      = "#b0b0b0"

VDS			  = 28.0  # V
PAE_OBJETIVO  = 35.0  # %

df = pd.read_excel(MEAS_DIR / "PowerMeter.xlsx", sheet_name="Sheet1", header=3, usecols="A,D,I")

df.columns = ["Pin", "Pout", "Id_mA"]
df         = df.dropna(subset=["Pin", "Pout", "Id_mA"])

for col in ["Pin", "Pout", "Id_mA"]:
	df[col] = df[col].astype(float)

Pin	       = df["Pin"].values
Pout       = df["Pout"].values
Id_mA      = df["Id_mA"].values

# Ganancia del driver (Pin del PA = Pin del sistema + ganancia del driver), tomada de la celda B1
driver_gain = pd.read_excel(MEAS_DIR / "PowerMeter.xlsx", sheet_name="Sheet1", header=None).iloc[0, 1]

Pin_pa_dBm = Pin + driver_gain

Pout_mW	   = 10 ** (Pout / 10)
Pin_mW	   = 10 ** (Pin_pa_dBm / 10)
P_DC	   = VDS * Id_mA  # mW, dado que Id está en mA

drain_eff  = Pout_mW / P_DC * 100
pae		   = (Pout_mW - Pin_mW) / P_DC * 100

# Punto más cercano al P1dB (30.3 dBm de Pout, según extracción de p1db_plot.py)
P1DB_POUT  = 30.3
idx_p1db   = np.argmin(np.abs(Pout - P1DB_POUT))

# Plot
fig, ax = plt.subplots()

# drain eff. y pae vs. pout
ax.plot(Pout, drain_eff, c=c_drain, marker='o', ms=4, mfc='none', label=r"Eficiencia de drain")
ax.plot(Pout, pae      , ls='-',c=c_pae  , marker='s', ms=4, mfc='none', label=r"PAE")

# punto de p1db
ax.plot(Pout[idx_p1db], pae[idx_p1db], marker='o', ms=3, c='black', zorder=6)
ax.annotate(
	r"PAE $= {:.1f}\%$".format(pae[idx_p1db]),
	xy=(Pout[idx_p1db], pae[idx_p1db]),
	xytext=(Pout[idx_p1db]-2, pae[idx_p1db] - 16),
	fontsize=12,
	arrowprops=dict(arrowstyle='->', color='black', lw=0.8),
)

ax.set_xlabel(r"$P_{out}$ (dBm)", labelpad=3)
ax.set_ylabel(r"Eficiencia (\%)", labelpad=3)

ax.grid(True, ls='--', alpha=0.3)
ax.legend(loc='upper left')
plt.tight_layout()

#plt.show()

output_path = OUTPUT_DIR / "pa_pae_drain_eff.png"
fig.savefig(output_path, format='png')
print(f"Guardado: {output_path.resolve()}")