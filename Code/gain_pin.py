import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Datos de ejemplo
# -----------------------------
pin = np.linspace(-20, 15, 300)  # dBm

gain_ss = 15.0                   # Ganancia de pequeña señal (dB)
p1db = 10.0                      # Punto de compresión de 1 dB (Pin)

# Modelo simple de compresión
compression = np.zeros_like(pin)
compression[pin > p1db] = 0.08 * (pin[pin > p1db] - p1db) ** 2

gain = gain_ss - compression
pout = pin + gain

# Saturación suave
psat = 27
pout = psat - (psat - pout) * np.exp(-(psat - pout) / 2)
pout = np.minimum(pout, psat)

# Recalcular la ganancia luego de saturar
gain = pout - pin

# -----------------------------
# Figura
# -----------------------------
fig, ax1 = plt.subplots(figsize=(6.5, 4.2))

ax2 = ax1.twinx()

# Potencia de salida
line1 = ax1.plot(
    pin,
    pout,
    lw=2.5,
    color="tab:blue",
    label=r"$P_{out}$"
)

# Ganancia
line2 = ax2.plot(
    pin,
    gain,
    lw=2.5,
    color="tab:red",
    label="Gain"
)

# Etiquetas
ax1.set_xlabel(r"$P_{in}$ (dBm)")
ax1.set_ylabel(r"$P_{out}$ (dBm)", color="tab:blue")
ax2.set_ylabel("Gain (dB)", color="tab:red")

ax1.tick_params(axis='y', colors='tab:blue')
ax2.tick_params(axis='y', colors='tab:red')

ax1.grid(True, alpha=0.3)

# Leyenda combinada
lines = line1 + line2
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc="lower right")

plt.tight_layout()
plt.show()