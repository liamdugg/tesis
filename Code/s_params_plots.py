import matplotlib
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from pathlib import Path
from scipy.interpolate import interp1d
from matplotlib.transforms import blended_transform_factory

matplotlib.style.use('tesis.mplstyle')

SCRIPT_DIR	= Path(__file__).resolve().parent   # scripts/Python/
SCRIPTS_DIR	= SCRIPT_DIR.parent                 # scripts/
MEAS_DIR	= SCRIPTS_DIR / "Measurements"
OUTPUT_DIR	= SCRIPTS_DIR / "Figures"

palette = sns.color_palette("muted", 2)
c_grid  = "#b0b0b0"

FREQ_MARK		= 2.2   # GHz
S21_MEAS_OFFSET	= 30.3  # dB — corrección vertical para S21 medido (positivo = sube)

# Parser
def parse_s2p(file_path: Path):
	data = {k: [] for k in ['frequency', 'S11_db', 'S21_db']}
	with file_path.open('r') as f:
		for line in f:
			if line.startswith('!') or line.startswith('#') or not line.strip():
				continue
			try:
				v = line.split()
				if len(v) >= 9:
					data['frequency'].append(float(v[0]))
					data['S11_db'].append(float(v[1]))
					data['S21_db'].append(float(v[3]))

			except (ValueError, IndexError):
				continue
	return {k: np.array(v) for k, v in data.items()} if data['frequency'] else None


# Clip to common range
def common_range(d1, d2):
	f_min = max(d1['frequency'].min(), d2['frequency'].min())
	f_max = min(d1['frequency'].max(), d2['frequency'].max())
	return f_min, f_max

def clip(data, f_min, f_max):
	mask = (data['frequency'] >= f_min) & (data['frequency'] <= f_max)
	return {k: v[mask] for k, v in data.items()}


# Marker at FREQ_MARK
def add_marker(ax, freq_ghz, y_data, color, x_mark=FREQ_MARK, text_offset=(0.3, -1.5), alpha=1.0):
	
	interp = interp1d(freq_ghz, y_data, kind='linear', fill_value='extrapolate')
	y_mark = float(interp(x_mark))
	
	ax.plot(x_mark, y_mark, 'o', color=color, markersize=4, zorder=6, alpha=alpha)
	
	ax.annotate(
	    r"{:.1f} dB".format(y_mark),
	    xy=(x_mark, y_mark),
	    xytext=(x_mark + text_offset[0], y_mark + text_offset[1]),
	    fontsize=12,
	    color=color,
	    arrowprops=dict(arrowstyle='->', color=color, lw=0.7),
	)


# Plot factory (separate single-axis plots)
def make_s11_plot(freq_meas, s11_meas, freq_sim, s11_sim, filename):

	fig, ax = plt.subplots()

	# S11 plot
	ax.plot(freq_meas, s11_meas, linestyle='-' , color=palette[0], label=r"S11 Medido")
	ax.plot(freq_sim,  s11_sim,  linestyle='--', color=palette[0], alpha=0.85, label=r"S11 Simulado")

	# Add vertical dashed line at FREQ_MARK
	ax.axvline(x=FREQ_MARK, color=c_grid, linestyle='--', linewidth=1.0, alpha=0.5, zorder=1)
	t_s11 = blended_transform_factory(ax.transData, ax.transAxes)
	
	ax.text(FREQ_MARK + 0.17, 0.275, "2.2 GHz", transform=t_s11, rotation=270, va='top', ha='right', color=c_grid, fontsize=12)

	# Add markers for S11
	add_marker(ax, freq_meas, s11_meas, 'black', text_offset=(0.35, -1.5))
	add_marker(ax, freq_sim,  s11_sim,  'black', text_offset=(0.35, -1.0), alpha=0.85)

	ax.set_xlabel(r"Frecuencia (GHz)", labelpad=3)
	ax.set_ylabel(r"S11 (dB)", labelpad=3)
	ax.set_xlim(freq_meas.min(), freq_meas.max())
	ax.grid(True, linestyle='--', alpha=0.3)
	ax.legend(loc='lower left')

	plt.tight_layout()

	return fig, OUTPUT_DIR / filename


def make_s21_plot(freq_meas, s21_meas, freq_sim, s21_sim, filename):

	fig, ax = plt.subplots()

	# S21 plot
	ax.plot(freq_meas, s21_meas, linestyle='-' , color=palette[0], label=r"S21 Medido")
	ax.plot(freq_sim,  s21_sim,  linestyle='--', color=palette[0], alpha=0.85, label=r"S21 Simulado")

	# Add vertical dashed line at FREQ_MARK
	ax.axvline(x=FREQ_MARK, color=c_grid, linestyle='--', linewidth=1.0, alpha=0.5, zorder=1)
	t_s21 = blended_transform_factory(ax.transData, ax.transAxes)
	
	ax.text(FREQ_MARK + 0.17, 0.275, "2.2 GHz", transform=t_s21, rotation=270, va='top', ha='right', color=c_grid, fontsize=12)

	# Add markers for S21
	add_marker(ax, freq_meas, s21_meas, 'black', text_offset=(0.35, -1.0))
	add_marker(ax, freq_sim,  s21_sim,  'black', text_offset=(0.35, 1.0), alpha=0.85)

	ax.set_xlabel(r"Frecuencia (GHz)", labelpad=3)
	ax.set_ylabel(r"S21 (dB)", labelpad=3)
	ax.set_xlim(freq_meas.min(), freq_meas.max())
	ax.grid(True, linestyle='--', alpha=0.3)

	ax.legend(loc='lower left')

	plt.tight_layout()

	return fig, OUTPUT_DIR / filename


# Main
if __name__ == "__main__":
	path_meas = MEAS_DIR / "sparam full scale Pin 0dBm.s2p"
	path_sim  = MEAS_DIR / "sparam_sim.s2p"

	data_meas = parse_s2p(path_meas)
	data_sim  = parse_s2p(path_sim)

	if data_meas is None or data_sim is None:
		raise FileNotFoundError(f"No se pudieron cargar los archivos .s2p desde {MEAS_DIR}")

	f_min, f_max = common_range(data_meas, data_sim)
	d_meas = clip(data_meas, f_min, f_max)
	d_sim  = clip(data_sim,  f_min, f_max)

	freq_meas = d_meas['frequency'] / 1e9
	freq_sim  = d_sim['frequency']  / 1e9

	# Create separate plots for S11 and S21
	fig_s11, path_s11 = make_s11_plot(
		freq_meas, d_meas['S11_db'],
		freq_sim,  d_sim['S11_db'],
		filename="s11_plot.png",
	)

	fig_s21, path_s21 = make_s21_plot(
		freq_meas, d_meas['S21_db'] + S21_MEAS_OFFSET,
		freq_sim,  d_sim['S21_db'],
		filename="s21_plot.png",
	)

	OUTPUT_DIR.mkdir(exist_ok=True)
	fig_s11.savefig(path_s11, format='png')
	fig_s21.savefig(path_s21, format='png')