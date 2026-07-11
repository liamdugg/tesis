import matplotlib
import matplotlib.pyplot as plt

from pathlib import Path

matplotlib.style.use('tesis.mplstyle')

OUTPUT_FILE = Path(__file__).parent.parent / "Figures" / "im_spectrum.png"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# Posición de cada componente espectral
x = [0, 1, 2, 3, 4, 5]

# Potencia relativa
y = [0.15, 0.45, 1.35, 1.35, 0.45, 0.15]

labels = [
    r"$3f_1-2f_2$",
    r"$2f_1-f_2$",
    r"$f_1$",
    r"$f_2$",
    r"$2f_2-f_1$",
    r"$3f_2-2f_1$",
]

fig, ax = plt.subplots()

# Líneas espectrales
ax.vlines(x, 0, y)

# Límites
ax.set_xlim(-0.5, 5.5)
ax.set_ylim(0, 1.45)

# Etiquetas
ax.set_ylabel("Potencia")
ax.set_xlabel("Frecuencia")

# Ticks
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_yticks([])


plt.tight_layout()
fig.savefig(OUTPUT_FILE, bbox_inches="tight")