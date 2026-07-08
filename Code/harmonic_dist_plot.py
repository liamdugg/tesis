import matplotlib
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from pathlib import Path
from matplotlib.patches import FancyArrowPatch

matplotlib.style.use('tesis.mplstyle')

palette = sns.color_palette("muted", 2)
c_v		= palette[0]   # azul
c_i		= palette[1]   # naranja
c_spec	= palette[0]   # azul

SCRIPT_DIR	= Path(__file__).resolve().parent
MEAS_DIR	= SCRIPT_DIR.parent / "Measurements"
OUTPUT_DIR	= SCRIPT_DIR.parent / "Figures"

def read_spectrum(path: Path):
	rows = []
	with path.open('r') as f:
		for line in f:
			line = line.strip()
			
			if not line or line.startswith('freq'):
				continue
			try:
				parts = line.split()
				if len(parts) >= 2:
					rows.append({'freq_ghz': float(parts[0]) / 1e9,
								 'power_dbm': float(parts[1])})
			except ValueError:
				continue

	return pd.DataFrame(rows)


def read_time_signal(path: Path):
	voltage_rows = []
	current_rows = []
	reading_voltage = True

	with path.open('r') as f:
		for line in f:
			line = line.strip()
			
			if 'I_load' in line and 'time' in line:
				reading_voltage = False
				continue
			
			if not line or ('time' in line.lower() and 'Vload' in line):
				continue
			try:
				parts = line.split()
				if len(parts) >= 2:
					t_ns = float(parts[0]) * 1e9
					val  = float(parts[1])
					
					if reading_voltage:
						voltage_rows.append({'time_ns': t_ns, 'voltage_v': val})
					else:
						current_rows.append({'time_ns': t_ns, 'current_ma': val * 1000})

			except ValueError:
				continue

	return pd.DataFrame(voltage_rows), pd.DataFrame(current_rows)


# ── Plot espectro ─────────────────────────────────────────────────────────────
def plot_spectrum(ax, spectrum_df):
	ax.set_ylim(-35, 35)
	ax.set_xlim(0, 11.5)
	ax.set_xlabel(r"Frecuencia (GHz)", labelpad=3)
	ax.set_ylabel(r"Potencia (dBm)", labelpad=3)
	ax.grid(True, linestyle='--', alpha=0.3)

	for _, row in spectrum_df.iterrows():
		freq  = row['freq_ghz']
		power = row['power_dbm']
		arrow = FancyArrowPatch(
			(freq, -40), (freq, power),
			arrowstyle='->',
			mutation_scale=8,
			color=c_spec,
			linewidth=1.2,
			alpha=0.9,
		)
		ax.add_patch(arrow)

	freq_ticks = sorted(f for f in spectrum_df['freq_ghz'].unique() if f <= 11.5)
	ax.set_xticks(freq_ticks)
	ax.set_xticklabels([r"{:.1f}".format(f) for f in freq_ticks])


# Plot señal en tiempo
def plot_time(ax, voltage_df, current_df):
	ax2 = ax.twinx()

	ax.plot(voltage_df['time_ns'] , voltage_df['voltage_v'] , color=c_v , label=r"Tensión")
	ax2.plot(current_df['time_ns'], current_df['current_ma'], color=c_i , label=r"Corriente")
	
	ax.set_xlabel(r"Tiempo (ns)", labelpad=3)
	ax.set_ylabel(r"Tensión (V)", labelpad=3)
	ax2.set_ylabel(r"Corriente (mA)", labelpad=3)
	
	ax.set_ylim(-15, 15)
	ax2.set_ylim(-500, 500)
	ax.grid(True, linestyle='--', alpha=0.3)
	ax2.grid(False)

	# Leyenda combinada
	handles1, labels1 = ax.get_legend_handles_labels()
	handles2, labels2 = ax2.get_legend_handles_labels()
	ax.legend(handles1 + handles2, labels1 + labels2, loc='upper left')

	return ax2


if __name__ == "__main__":
	spectrum_df             = read_spectrum(MEAS_DIR / "spectrum_sim.txt")
	voltage_df, current_df  = read_time_signal(MEAS_DIR / "time_signal_load_sim.txt")

	fig, ax = plt.subplots()

	#plot_time(ax, voltage_df, current_df)
	plot_spectrum(ax, spectrum_df)
	plt.tight_layout()

	OUTPUT_DIR.mkdir(exist_ok=True)
	output_path = OUTPUT_DIR / "spectrum_plot.png"
	
	fig.savefig(output_path, format='png')
	print(f"Guardado: {output_path}")