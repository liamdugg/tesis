import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from pathlib import Path

matplotlib.style.use('tesis.mplstyle')

SCRIPT_DIR	= Path(__file__).resolve().parent
MEAS_DIR	= SCRIPT_DIR.parent / "Measurements"
OUTPUT_DIR	= SCRIPT_DIR.parent / "Figures"
OUTPUT_DIR.mkdir(exist_ok=True)

palette = sns.color_palette("muted", 2)
c_pout	= palette[0]
c_gain	= palette[1]

def find_p1db(Pin_i, Pout_i, Gain_i):
	G_lin		= np.max(Gain_i)
	Pout_ideal	= Pin_i + G_lin
	compression	= Pout_ideal - Pout_i
	idx_1db		= np.argmin(np.abs(compression - 1.0))
	
	return Pin_i[idx_1db], Pout_i[idx_1db]

def ideal_pout_line(Pin, Pout, Pin_i):
	mask	= (Pin == -20) | (Pin == -12.5)
	G_ideal	= np.mean(Pout[mask] - Pin[mask])
	
	return Pin_i + G_ideal, G_ideal

df = pd.read_csv(MEAS_DIR / "P1dB_csv.csv")

for col in ["Pin", "Pout", "Gain_tot"]:
	df[col] = df[col].astype(str).str.replace(",", ".", regex=False).astype(float)

Pin	   = df["Pin"].values
Pout   = df["Pout"].values
Gain   = df["Gain_tot"].values

Pin_i  = np.linspace(Pin.min(), Pin.max(), 300)
Pout_i = np.interp(Pin_i, Pin, Pout)
Gain_i = np.interp(Pin_i, Pin, Gain)

Pin_1dB, Pout_1dB = find_p1db(Pin_i, Pout_i, Gain_i)
Pout_ideal, _     = ideal_pout_line(Pin, Pout, Pin_i)

# Plot 
fig, ax1 = plt.subplots()

# Pout medido
ax1.plot(Pin, Pout, color=c_pout, marker='o', markersize=4, markerfacecolor='none', label=r"$P_{out}$")
ax1.plot(Pin_i, Pout_ideal, linestyle=':', color='gray')

# Punto P1dB
ax1.plot(Pin_1dB, Pout_1dB, marker='o', markersize=3, color='black', zorder=6)
ax1.annotate(
	r"$P_{{1dB}}= {:.1f}$ dBm".format(Pout_1dB),
	xy=(Pin_1dB, Pout_1dB),
	xytext=(Pin_1dB - 11, Pout_1dB + 1.8),
	fontsize=12,
	arrowprops=dict(arrowstyle='->', color='black', lw=0.8),
)

ax1.set_xlabel(r"$P_{in}$ (dBm)" , labelpad=3)
ax1.set_ylabel(r"$P_{out}$ (dBm)", labelpad=3)
ax1.grid(True, linestyle='--', alpha=0.3)

# Gain
ax2 = ax1.twinx()

ax2.plot(Pin, Gain, color=c_gain, marker='s', markersize=4, markerfacecolor='none', label=r"Ganancia")

ax2.set_ylabel(r"Ganancia (dB)", labelpad=3)
ax2.grid(False)

# Leyenda combinada
handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()

if handles1 or handles2:
	legend = ax1.legend(handles1 + handles2, labels1 + labels2, loc='center left', bbox_to_anchor=(0, 0.8))

plt.tight_layout()

output_path = OUTPUT_DIR / "p1db_plot.png"

fig.savefig(output_path, format='png')
print(f"Guardado: {output_path.resolve()}")