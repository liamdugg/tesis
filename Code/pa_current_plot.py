import numpy as np
import matplotlib.pyplot as plt

plt.style.use('tesis.mplstyle')

# Corriente normalizada (Imax = 1)
def current(theta, alpha):
    c       = np.cos(alpha / 2)
    y       = np.zeros_like(theta)
    mask    = np.abs(theta) <= alpha / 2
    y[mask] = (np.cos(theta[mask]) - c) / (1 - c)
    
    return y

# Coeficientes de Fourier
def fourier_coeff(alpha, max_harm=5, N=5000):
    theta = np.linspace(-np.pi, np.pi, N)
    i     = current(theta, alpha)
    
    a0 = (1/(2*np.pi)) * np.trapezoid(i, theta)
    
    harmonics = []
    
    for n in range(1, max_harm + 1):
        an = (1/np.pi) * np.trapezoid(i*np.cos(n*theta), theta)
        bn = (1/np.pi) * np.trapezoid(i*np.sin(n*theta), theta)
        amplitude = np.sqrt(an**2 + bn**2)
        harmonics.append(amplitude)
    
    return a0, harmonics

# Barrido de ángulo de conducción
alphas = np.linspace(0.05, 2*np.pi, 250)
dc     = []
harm   = [[] for _ in range(5)]

for alpha in alphas:
    a0, amps = fourier_coeff(alpha)
    dc.append(a0)

    for k in range(5):
        harm[k].append(amps[k])

# Plot
plt.figure(figsize=(4.79,3.6))

plt.plot(alphas, dc     , label='DC')
plt.plot(alphas, harm[0], label='Fundamental')

for k in range(1,5):
    plt.plot(alphas, harm[k], label=f'{k+1}° Armónico')

plt.gca().invert_xaxis()
plt.xlabel(r'Ángulo de Conducción $\alpha$ (rad)')
plt.ylabel('Amplitud (Imax = 1)')
plt.xticks([2*np.pi, 1.5*np.pi, np.pi, 0.5*np.pi,0], [r'$2\pi$ \n A', r'$\frac{3}{2}\pi$', r'$\pi \n B$', r'$\frac{1}{2}\pi$', '0'])
plt.xlim(2*np.pi, 0)
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig('pa_harmonics.png')
#plt.show()