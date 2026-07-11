import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from pathlib import Path

matplotlib.style.use('tesis.mplstyle')

OUTPUT_FILE = Path(__file__).parent.parent / "Figures" / "rf_power.png"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

def rf_power_rel_db(alpha):
    """Potencia de RF relativa a Clase A, en dB, en función del angulo de conduccion (rad)."""
    num = alpha - np.sin(alpha)
    den = np.pi * (1 - np.cos(alpha / 2))
    
    return 10 * np.log10(num / den)

eps   = 1e-4
alpha = np.linspace(2 * np.pi - eps, eps, 2000) 
p_rel = rf_power_rel_db(alpha)

fig, ax = plt.subplots()
ax.plot(alpha, p_rel)

# eje x
ax.set_xlim(2 * np.pi, 0)
ax.set_xticks([2*np.pi, 3*np.pi/2, np.pi, np.pi/2, 0])
ax.set_xticklabels([r"$2\pi$", "", r"$\pi$", "", r"$0$"])

# segundo eje x con clases de operacion
ax2 = ax.secondary_xaxis(-0.07)
ax2.set_xticks([2*np.pi, 1.5*np.pi, np.pi, 0.5*np.pi])
ax2.set_xticklabels(["A", "AB", "B", "C"])
ax2.tick_params(which="both", length=0)
ax2.spines["bottom"].set_visible(False)

ax.set_xlabel(r"Ángulo de conducción $\alpha$ (rad)", labelpad=18)

# eje y
ax.set_ylim(-5, 2)
ax.set_ylabel(r"Potencia de RF relativa a Clase A (dB)")

ax.grid(True, axis='both', linestyle="--", alpha=0.3)

plt.tight_layout()
fig.savefig(OUTPUT_FILE, bbox_inches="tight")