import matplotlib
import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt

from pathlib import Path

matplotlib.style.use('tesis.mplstyle')

SCRIPT_DIR  = Path(__file__).resolve().parent
SCRIPTS_DIR = SCRIPT_DIR.parent
MEAS_DIR    = SCRIPTS_DIR / "Measurements"
OUTPUT_DIR  = SCRIPTS_DIR / "Figures"

df = pd.read_csv(MEAS_DIR / "Stability.csv")

palette  = sns.color_palette("muted", 2)
c_load   = palette[0]
c_source = palette[1]

fig, ax = plt.subplots()

ax.plot(df['freq'] / 1e9, df['mu_load']  , label=r'$\mu$ Load'  , color=c_load  , marker='o', markersize=3, markerfacecolor='none')
ax.plot(df['freq'] / 1e9, df['mu_source'], label=r'$\mu$ Source', color=c_source, marker='o', markersize=3, markerfacecolor='none')

ax.axhline(y=1, color='r', linestyle='--', linewidth=0.8, label=r'Stability limit ($\mu=1$)', alpha=0.5)

ax.legend()
ax.grid(True, linestyle='--', alpha=0.3)
ax.set_xlabel(r'Frecuencia (GHz)', labelpad=3)
ax.set_ylabel(r'Valor $\mu$'     , labelpad=3)

plt.tight_layout()

OUTPUT_DIR.mkdir(exist_ok=True)
output_path = OUTPUT_DIR / "stability_plot.png"

plt.savefig(output_path, format='png')
print(f"Guardado: {output_path}")