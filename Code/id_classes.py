import matplotlib
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path

matplotlib.style.use('tesis.mplstyle')
#plt.rcParams.update({'figure.dpi': '300'})

OUTPUT_FILE = Path(__file__).parent.parent / "Figures" / "id_classes.png"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# Tiempo
wt = np.linspace(0, 4*np.pi, 4000)

# Corrientes

# Clase A (360°)
I_A = 0.5*(1 + np.cos(wt))

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

# ======= Figure =======
fig, ax = plt.subplots(2, 2, figsize=(4.79*2,3.6*2))

titles   = ["Clase A", "Clase AB", "Clase B", "Clase C"]
currents = [I_A, I_AB, I_B, I_C]

for a, title, current in zip(ax.flat, titles, currents):
    a.plot(wt, current)

    a.set_xlim(0, 4*np.pi)
    a.set_ylim(0, 1.1)

    a.set_title(title)

    a.set_xticks([0,np.pi/2, np.pi, 3*np.pi/2, 2*np.pi, 5*np.pi/2, 3*np.pi, 7*np.pi/2, 4*np.pi])
    a.set_xticklabels(["0", r"$\frac{\pi}{2}$", r"$\pi$", r"$\frac{3\pi}{2}$", r"$2\pi$", r"$\frac{5\pi}{2}$", r"$3\pi$", r"$\frac{7\pi}{2}$", r"$4\pi$"])

# Etiquetas eje x
ax[1,0].set_xlabel(r"$\omega t$")
ax[1,1].set_xlabel(r"$\omega t$")

# Etiquetas eje y
ax[0,0].set_ylabel("Corriente de Drain ($I_D$)")
ax[1,0].set_ylabel("Corriente de Drain ($I_D$)")

# Flechas α
def alpha_arrow(axis, x1, x2, y=0.55):
    axis.annotate("", (x2, y), (x1, y), arrowprops=dict(arrowstyle="<->"))
    
    axis.text((x1+x2)/2, y+0.06, r"$\alpha$", ha="center")

# Clase AB (>180°)
alpha_arrow(ax[0,1], 1.30*np.pi, 2.70*np.pi)

# Clase B (=180°)
alpha_arrow(ax[1,0], 1.50*np.pi, 2.50*np.pi)

# Clase C (<180°)
alpha_arrow(ax[1,1], 1.65*np.pi, 2.35*np.pi)

plt.tight_layout()

fig.savefig(OUTPUT_FILE, format='png', bbox_inches='tight')

#plt.show()