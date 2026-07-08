import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
from scipy.interpolate import interp1d
from matplotlib.widgets import TextBox

script_dir       = Path(__file__).parent
measurements_dir = script_dir.parent / "Measurements"

file_path = measurements_dir / "CADENA_IMD_Sweep_-5dBm.csv"
#file_path = measurements_dir / "IMD_Sweep_-10dBm.csv"

# Leer el CSV (saltando encabezados de Keysight)
df = pd.read_csv(file_path, skiprows=6)

# convertir todo lo posible a número
df = df.apply(pd.to_numeric, errors='coerce')

# Apply 30dB correction to all columns except frequency and IIP3(dB)
cols_to_correct = [col for col in df.columns[1:] if 'IIP3' not in col]
df[cols_to_correct] += 31.2

# El valor del atenuador es de 31.2 dB porque al medir como analizador de espectro, 
# hay que considerar la pérdida del cable sumada al atenuador de 30 dB.

# Mostrar columnas para verificar
print("Columnas detectadas:")
print(df.columns)

# Tomar primera columna como eje X
x = df.iloc[:, 0]

# Limit to 5 GHz
x_limit     = 5e9  # 5 GHz in Hz

mask        = x <= x_limit
x_filtered  = x[mask]
df_filtered = df[mask]

# Interpolate with 3rd order polynomial for smoother curves
x_interp = np.linspace(x_filtered.min(), x_filtered.max(), len(x_filtered) * 3)

fig = plt.figure(figsize=(12, 7))
ax  = fig.add_subplot(111)

# Filter out phase columns (keep only magnitude/dB columns)
plot_cols = [col for col in df_filtered.columns[1:] if '(DEG)' not in col]

# Store interpolation functions and original data
interp_funcs = {}
colors = plt.cm.tab10(np.linspace(0, 1, len(plot_cols)))

for idx, col in enumerate(plot_cols):
    y_data = df_filtered[col].values
    
    # Create interpolation function with cubic (3rd order) spline
    interp_func = interp1d(x_filtered.values, y_data, kind='cubic', fill_value='extrapolate')
    interp_funcs[col] = interp_func
    
    # Interpolate for smoother plotting
    y_interp = interp_func(x_interp)
    
    ax.plot(x_interp, y_interp, label=col, color=colors[idx], linewidth=2)

ax.set_xlabel(df_filtered.columns[0], fontsize=12)
ax.set_ylabel("Amplitude / Power (dB)", fontsize=12)
ax.set_title("IMD Sweep (up to 5 GHz)", fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(loc='upper left', fontsize=9)
ax.set_xlim(x_filtered.min(), x_filtered.max())

# Store plot data for marker interaction
plot_data = {
    'ax': ax,
    'fig': fig,
    'x': x_interp,
    'x_original': x_filtered.values,
    'interp_funcs': interp_funcs,
    'columns': plot_cols,
    'colors': colors,
    'current_x': x_interp[len(x_interp) // 2],
    'markers': {},
    'vline': None,
    'text_boxes': {},
    'dragging': False,
    'plot_cols': plot_cols
}

# Initialize marker at the middle of the data
initial_x = plot_data['current_x']

# Create vertical line
vline = ax.axvline(x=initial_x, color='black', linestyle='--', linewidth=2, alpha=0.7)
plot_data['vline'] = vline

# Create marker points and text boxes for all curves (positioned on the right)
for idx, col in enumerate(plot_cols):
    y_at_x = interp_funcs[col](initial_x)
    
    # Plot marker
    marker, = ax.plot([initial_x], [y_at_x], 'o', color=colors[idx], markersize=10, zorder=5)
    plot_data['markers'][col] = marker
    
    # Create text annotation on the right side of the plot to avoid overlap
    text_str = f'{col}\nx: {initial_x:.1f}\ny: {y_at_x:.2f}'
    text_box = ax.text(0.98, 0.98 - idx * 0.12, text_str, transform=ax.transAxes,
                       verticalalignment='top', horizontalalignment='right',
                       bbox=dict(boxstyle='round', facecolor=colors[idx], alpha=0.6), 
                       fontsize=9)
    plot_data['text_boxes'][col] = text_box

# Add text box for marker x value input
ax_textbox = fig.add_axes([0.2, 0.05, 0.2, 0.04])
textbox = TextBox(ax_textbox, 'Marker X:', initial=f'{initial_x:.1f}')

def update_marker_from_input(text):
    """Update marker position from text input"""
    try:
        new_x = float(text)
        # Clamp to data range
        new_x = max(min(new_x, x_filtered.max()), x_filtered.min())
        plot_data['current_x'] = new_x
        textbox.set_val(f'{new_x:.1f}')
        update_markers()
    except ValueError:
        textbox.set_val(f'{plot_data["current_x"]:.1f}')

def update_markers():
    """Update all markers and text boxes"""
    current_x = plot_data['current_x']
    
    # Update vertical line
    plot_data['vline'].set_xdata([current_x, current_x])
    
    # Update all markers and text boxes
    for col in plot_data['plot_cols']:
        y_at_x = interp_funcs[col](current_x)
        plot_data['markers'][col].set_data([current_x], [y_at_x])
        
        # Update text
        text_str = f'{col}\nx: {current_x:.1f}\ny: {y_at_x:.2f}'
        plot_data['text_boxes'][col].set_text(text_str)
    
    plot_data['fig'].canvas.draw_idle()

textbox.on_submit(update_marker_from_input)

# Event handlers for interactive marker
def on_press(event):
    """Handle mouse press for dragging"""
    if event.inaxes != ax or event.xdata is None:
        return
    
    # Check if click is near the vertical line
    dist = abs(event.xdata - plot_data['current_x'])
    if dist < 0.05 * (x_filtered.max() - x_filtered.min()):
        plot_data['dragging'] = True

def on_release(event):
    """Handle mouse release"""
    plot_data['dragging'] = False

def on_motion(event):
    """Handle mouse motion for dragging or displaying values"""
    if event.inaxes != ax or event.xdata is None:
        return
    
    if plot_data['dragging']:
        # Update marker position while dragging
        new_x = max(min(event.xdata, x_filtered.max()), x_filtered.min())
        plot_data['current_x'] = new_x
        textbox.set_val(f'{new_x:.1f}')
        update_markers()

# Connect mouse events
fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('button_release_event', on_release)
fig.canvas.mpl_connect('motion_notify_event', on_motion)

plt.tight_layout(rect=[0, 0.1, 1, 1])
plt.show()
