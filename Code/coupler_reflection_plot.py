import matplotlib
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from pathlib import Path

matplotlib.style.use('tesis.mplstyle')
plt.rcParams.update({'figure.dpi': '100'})

SCRIPT_DIR  = Path(__file__).resolve().parent
MEAS_DIR    = SCRIPT_DIR.parent / "Measurements"
RESULTS_DIR = MEAS_DIR / "LAB_CNEA" / "results_data"
OUTPUT_DIR  = SCRIPT_DIR.parent / "Figures"
OUTPUT_DIR.mkdir(exist_ok=True)

X_LIMIT_GHZ = (1.2, 3.2)

palette = sns.color_palette("muted", 3)
c_s11   = palette[0]
c_s22   = palette[1]
c_s33   = palette[2]

def load_s2p(filename):
	"""Carga un archivo Touchstone .s2p (Freq, S11 dB/ang, S21 dB/ang, S12 dB/ang, S22 dB/ang)."""
	data     = np.loadtxt(RESULTS_DIR / filename, comments=('!', '#'))
	freq_ghz = data[:, 0] / 1e9
	
	return freq_ghz, data

def plot_reflection(version):
	"""Grafica S11, S22 y S33 para la versión indicada ('V1' o 'V2') del acoplador."""

	# P1-P2: puerto 1 y puerto 2 del acoplador -> S11 y S22 (columnas 1 y 7)
	# P1-P3: puerto 1 y puerto 3 del acoplador -> S33 (columna 7, ya que en este
	#        archivo de 2 puertos, el "puerto 2" del VNA está conectado al puerto 3
	#        del acoplador)
	freq, d12 = load_s2p(f"P1-P2_s2p_coupler{version}_cal.s2p")
	_,    d13 = load_s2p(f"P1-P3_s2p_coupler{version}_cal.s2p")

	s11 = d12[:, 1]
	s22 = d12[:, 7]
	s33 = d13[:, 7]

	fig, ax = plt.subplots()

	ax.plot(freq, s11, c=c_s11, label=r"$\mathrm{S_{11}}$")
	ax.plot(freq, s22, c=c_s22, label=r"$\mathrm{S_{22}}$")
	ax.plot(freq, s33, c=c_s33, label=r"$\mathrm{S_{33}}$")

	ax.set_xlim(*X_LIMIT_GHZ)
	ax.set_ylim(bottom=-40)
	
	ax.set_xlabel(r"Frecuencia (GHz)", labelpad=3)
	ax.set_ylabel(r"Magnitud (dB)"   , labelpad=3)

	
	ax.grid(True, linestyle='--', alpha=0.3)
	ax.legend()

	plt.tight_layout()
	plt.show()

	fig.savefig(OUTPUT_DIR / f"coupler_reflexion_{version.lower()}.png", format='png')
	print(f"\nGuardado\n")

plot_reflection("V1")
plot_reflection("V2")