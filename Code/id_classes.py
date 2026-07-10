import matplotlib
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path

matplotlib.style.use("tesis.mplstyle")

OUTPUT_FILE = Path(__file__).parent.parent / "Figures" / "id_classes.png"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# Tiempo
wt = np.linspace(0, 4 * np.pi, 4000)

# Corrientes

# Clase A (360°)
I_A = 0.5 * (1 + np.cos(wt))

# Clase AB (>180°)
I_AB = np.cos(wt) + 0.30
I_AB[I_AB < 0] = 0
I_AB /= I_AB.max()

# Clase B (180°)
I_B = np.cos(wt)
I_B[I_B < 0] = 0

# Clase C (<180°)
I_C = np.cos(wt) - 0.45
I_C[I_C < 0] = 0
I_C /= I_C.max()

# 
alphas = {
    "Clase A" : 2 * np.pi,
    "Clase AB": 1.40 * np.pi,
    "Clase B" : np.pi,
    "Clase C" : 0.70 * np.pi,
}


fig, ax  = plt.subplots(2, 2, figsize=(4.79 * 2, 3.6 * 2))

titles   = ["Clase A", "Clase AB", "Clase B", "Clase C"]
currents = [I_A, I_AB, I_B, I_C]

for a, title, current in zip(ax.flat, titles, currents):

    a.plot(wt, current)

    a.set_xlim(0, 4 * np.pi)
    a.set_ylim(0, 1.1)

    a.set_title(title)

    alpha = alphas[title]

    ticks  = [0, np.pi, 2*np.pi, 3*np.pi, 4*np.pi]
    labels = ["0", r"$\pi$", r"$2\pi$", r"$3\pi$", r"$4\pi$"]

    if title != "Clase A":
        ticks.extend([2*np.pi - alpha/2, 2*np.pi + alpha/2])

    labels.extend([r"$-\frac{\alpha}{2}$", r"$+\frac{\alpha}{2}$"])

    ticks, labels = zip(*sorted(zip(ticks, labels), key=lambda x: x[0]))

    a.set_xticks(ticks)
    a.set_xticklabels(labels)

ax[1, 0].set_xlabel(r"$\omega t$")
ax[1, 1].set_xlabel(r"$\omega t$")

ax[0, 0].set_ylabel("Corriente de Drain ($I_D$)")
ax[1, 0].set_ylabel("Corriente de Drain ($I_D$)")

plt.tight_layout()

fig.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")