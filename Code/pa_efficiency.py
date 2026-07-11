import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path

plt.style.use("tesis.mplstyle")

OUTPUT_FILE = Path(__file__).parent.parent / "Figures" / "pa_efficiency.png"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

def eficiencia(alpha):
    """Eficiencia de drain en funcion del angulo de conduccion (rad)."""
    num = alpha - np.sin(alpha)
    den = np.sin(alpha / 2) - (alpha / 2) * np.cos(alpha / 2)
    return 0.25 * num / den

# evitar division por cero exacta en alpha = 0 y alpha = 2*pi
eps   = 1e-6
alpha = np.linspace(2 * np.pi - eps, eps, 1000)  # de 2pi a 0 (izquierda a derecha)
eta   = eficiencia(alpha) * 100  # en porcentaje

fig, ax = plt.subplots()
ax.plot(alpha, eta)

ax.set_xlim(2 * np.pi, 0)  
ax.set_xticks([2*np.pi, 3*np.pi/2, np.pi, np.pi/2, 0])
ax.set_xticklabels([r"$2\pi$", "", r"$\pi$", "", r"$0$"])

ax.set_ylabel(r"Máxima Eficiencia Teórica $\eta$ (\%)")
ax.set_ylim(45, 105)
ax.grid(True, axis='both', linestyle="--", alpha=0.3)

# segundo eje x, debajo del primero, con las clases de operacion
ax2 = ax.secondary_xaxis(-0.07)
ax2.set_xticks([2*np.pi, 1.5*np.pi, np.pi, 0.5*np.pi])
ax2.set_xticklabels(["A", "AB", "B", "C"])
ax2.tick_params(which='both',length=0)

ax2.spines["bottom"].set_visible(False)  # sin la linea del eje secundario

# xlabel del eje principal, empujado por debajo del segundo eje
ax.set_xlabel(r"Ángulo de conducción $\alpha$ (rad)", labelpad=18)

plt.tight_layout()
fig.savefig(OUTPUT_FILE, bbox_inches="tight")