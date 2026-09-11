import numpy as np
import tkinter as tk
import matplotlib
import matplotlib.pyplot as plt

from tkinter import ttk
from pathlib import Path
from matplotlib.ticker import AutoMinorLocator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

matplotlib.use("TkAgg")
matplotlib.style.use("tesis.mplstyle")

# dpi bajo para la vista en pantalla. se sube al guardar
plt.rcParams.update({"figure.dpi": 100})  

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR.parent / "Figures"
OUTPUT_DIR.mkdir(exist_ok=True)

# constants
FREQ         = 2.2e9
WLEN         = 3e8 / FREQ
R_EARTH      = 6378
K_DB         = -228.6
EBN0_QPSK    = 9.6
EBN0_8PSK    = 13.3
EBN0_16PSK   = 18.3
ANG          = np.arange(0.0, 90.1, 0.1)
RAD          = np.deg2rad(ANG)

BITS_PER_SYM = {"QPSK": 2, "8-PSK": 3, "16-PSK": 4}
MOD_COLORS   = {"QPSK": "#2d7dd2", "8-PSK": "#1d9e75", "16-PSK": "#d85a30"}
MOD_REQS     = {"QPSK": EBN0_QPSK, "8-PSK": EBN0_8PSK, "16-PSK": EBN0_16PSK}

BG           = "#ffffff"
BG2          = "#f5f5f5"
FG           = "#2c2c2a"
FG_MUT       = "#73726c"
ACCENT       = "#185fa5"
FONT         = ("Helvetica", 9)
MONO         = ("Courier", 9)


# computation
def compute(r_orb, bw_mhz, rolloff, power_tx, loss_tx, gain_tx, loss_point, loss_atm, gain_rx, loss_rx,t_ant, t_lna, margin_min):

    # geometry + path
    eirp       = power_tx - loss_tx + gain_tx
    d          = (np.sqrt((R_EARTH*1e3 + r_orb*1e3)**2 - (R_EARTH*1e3 * np.cos(RAD))**2) - R_EARTH*1e3 * np.sin(RAD))
    fsl        = 20 * np.log10(4 * np.pi * d / WLEN)
    loss_path  = fsl + loss_point + loss_atm
    rsl        = eirp - loss_path + gain_rx - loss_rx   # dBW, vs angle

    # noise
    t_sys      = t_ant + t_lna
    n0         = K_DB + 10 * np.log10(t_sys)            # dBW/Hz

    # symbol rate from bandwidth and roll-off
    bw_hz      = bw_mhz * 1e6
    sym_rate   = bw_hz / (1.0 + rolloff)                # baud

    # per-modulation bitrate and Eb/N0 available
    bitrates   = {mod: sym_rate * b for mod, b in BITS_PER_SYM.items()}
    ebn0_disps = {mod: rsl - n0 - 10*np.log10(rb) for mod, rb in bitrates.items()}
    margins    = {mod: ebn0_disps[mod] - MOD_REQS[mod] for mod in MOD_REQS}

    def min_elev(m):
        idx = np.where(m >= margin_min)[0]
        return ANG[idx[0]] if len(idx) else None

    min_elevs = {mod: min_elev(margins[mod]) for mod in MOD_REQS}
    return ebn0_disps, margins, min_elevs, bitrates


# application
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Satellite Link Budget - LEO @ 2.2 GHz")
        self.configure(bg=BG)

        self.resizable(True, True)
        self._last_ebn0disps = None
        self._last_min_elevs = None
        self._last_bitrates  = None
        self._last_r_orb     = 600

        self._build()
        self._update()

    # layout
    def _build(self):
        self.columnconfigure(0, weight=0, minsize=340)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # LEFT column
        left = tk.Frame(self, bg=BG)
        left.grid(row=0, column=0, sticky="nsew")
        left.rowconfigure(0, weight=1)
        left.rowconfigure(1, weight=0)
        left.rowconfigure(2, weight=0)
        left.columnconfigure(0, weight=1)

        # Scrollable inner panel
        cvs_host = tk.Frame(left, bg=BG)
        cvs_host.grid(row=0, column=0, sticky="nsew")
        cvs_host.rowconfigure(0, weight=1)
        cvs_host.columnconfigure(0, weight=1)

        cvs = tk.Canvas(cvs_host, bg=BG, highlightthickness=0, width=330)
        vsb = ttk.Scrollbar(cvs_host, orient="vertical", command=cvs.yview)
        cvs.configure(yscrollcommand=vsb.set)

        vsb.grid(row=0, column=1, sticky="ns")
        cvs.grid(row=0, column=0, sticky="nsew")

        inner = tk.Frame(cvs, bg=BG, padx=14, pady=8)
        wid   = cvs.create_window((0, 0), window=inner, anchor="nw")

        inner.bind("<Configure>", lambda e: (
            cvs.configure(scrollregion=cvs.bbox("all")),
            cvs.itemconfigure(wid, width=cvs.winfo_width())
        ))

        cvs.bind("<Configure>"     , lambda e: cvs.itemconfigure(wid, width=e.width))
        cvs.bind_all("<MouseWheel>", lambda e: cvs.yview_scroll(int(-e.delta/120), "units"))

        # Controls
        r = 0
        r = self._sep(inner, "Órbita y señal", r)
        self.e_rorb   = self._entry (inner, "Radio de órbita", "km" , "600", r); r += 1
        self.sl_bw    = self._slider(inner, "Ancho de banda" , "MHz",     r, 0.5, 30.0,   5.0, 0.5); r += 1
        self.sl_ro    = self._slider(inner, "Roll-off"       ,    "",     r, 0.1,  0.5,  0.35, 0.05); r += 1

        r = self._sep(inner, "Transmisor", r)
        self.sl_ptx    = self._slider(inner, "Potencia Tx",        "dBW", r, -10, 30,  0.0, 0.5); r += 1
        self.sl_ltx    = self._slider(inner, "Pérdidas Tx",        "dB",  r,   0,  5,  1.0, 0.5); r += 1
        self.sl_gtx    = self._slider(inner, "Ganancia Tx",        "dBi", r,   0, 45,  8.0, 0.5); r += 1

        r = self._sep(inner, "Trayecto", r)
        self.sl_lpoint = self._slider(inner, "Pérd. apuntamiento", "dB",  r,   0,  5,  1.0, 0.1); r += 1
        self.sl_latm   = self._slider(inner, "Pérd. atmosférica",  "dB",  r,   0,  5,  1.0, 0.1); r += 1

        r = self._sep(inner, "Receptor", r)
        self.sl_grx    = self._slider(inner, "Ganancia Rx",        "dBi", r,   0, 45, 30.0, 0.5); r += 1
        self.sl_lrx    = self._slider(inner, "Pérdidas Rx",        "dB",  r,   0,  5,  1.0, 0.5); r += 1

        r = self._sep(inner, "Ruido del sistema", r)
        self.sl_tant   = self._slider(inner, "T antena",           "K",   r,  10, 300,  70.0, 1.0); r += 1
        self.sl_tlna   = self._slider(inner, "T LNA",              "K",   r,  10, 500,  75.0, 1.0); r += 1

        r = self._sep(inner, "Criterio de cierre", r)
        self.sl_mmin   = self._slider(inner, "Margen mínimo",      "dB",  r,   0,  10,  1.0, 1.0); r += 1

        # Pinned status box
        status_wrap = tk.Frame(left, bg=BG2, highlightthickness=1, highlightbackground="#c4c2ba")

        status_wrap.grid(row=1, column=0, sticky="ew")
        tk.Label(status_wrap, text="ESTADO DEL ENLACE",

                 bg=BG2, fg=FG_MUT,
                 font=("Helvetica", 8, "bold"),
                 anchor="w", padx=12, pady=5).pack(fill="x")
        ttk.Separator(status_wrap).pack(fill="x")

        self.status = tk.Text(
            status_wrap, height=9,
            bg=BG2, fg=FG, font=MONO,
            relief="flat", bd=0,
            highlightthickness=0,
            state="disabled", padx=12, pady=6, wrap="none"
        )

        self.status.pack(fill="x")

        # Save button
        btn_frame = tk.Frame(left, bg=BG2, highlightthickness=1, highlightbackground="#c4c2ba")
        btn_frame.grid(row=2, column=0, sticky="ew")

        tk.Button(
            btn_frame, text="Guardar gráfico",
            command=self._save_plot,
            bg=ACCENT, fg="#ffffff",
            font=("Helvetica", 9, "bold"),
            relief="flat", bd=0,
            padx=12, pady=7,
            activebackground="#134f8a",
            activeforeground="#ffffff",
            cursor="hand2",
        ).pack(fill="x", padx=10, pady=8)

        self.save_label = tk.Label(btn_frame, text="", bg=BG2, fg=FG_MUT, font=("Helvetica", 8), anchor="center")
        self.save_label.pack(fill="x", padx=10, pady=(0, 6))

        # RIGHT: plot
        right = tk.Frame(self, bg=BG, padx=10, pady=12)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        self.fig, self.ax = plt.subplots(figsize=(7, 5.4))
        self.fig.patch.set_facecolor(BG)
        self.ax.set_facecolor("#ffffff")

        self.cv = FigureCanvasTkAgg(self.fig, master=right)
        self.cv.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    # widget helpers
    def _sep(self, p, title, row):
        tk.Label(p, text=title.upper(),
                 bg=BG, fg=FG_MUT,
                 font=("Helvetica", 8, "bold"),
                 anchor="w"
                 ).grid(row=row, column=0, columnspan=3,
                        sticky="ew", pady=(12, 1))
        row += 1
        ttk.Separator(p).grid(row=row, column=0, columnspan=3, sticky="ew", pady=(0, 4))
        return row + 1

    def _entry(self, p, label, unit, default, row):
        p.columnconfigure(1, weight=1)
        tk.Label(p, text=label, bg=BG, fg=FG, font=FONT, anchor="w").grid(row=row, column=0, sticky="w", pady=3)

        var    = tk.StringVar(value=default)
        holder = tk.Frame(p, bg=ACCENT)

        holder.grid(row=row, column=1, columnspan=2, sticky="ew", padx=(6, 0), pady=3)
        tk.Entry(holder, textvariable=var,
                 font=("Courier", 10),
                 bg="#ffffff", fg=ACCENT,
                 insertbackground=ACCENT,
                 relief="flat", bd=3,
                 highlightthickness=0
                 ).pack(side="left", fill="x", expand=True)
        
        tk.Label(holder, text=f" {unit} ", bg=ACCENT, fg="#ffffff", font=("Helvetica", 8, "bold")).pack(side="right")
        var.trace_add("write", lambda *_: self._update())
        return var

    def _slider(self, p, label, unit, row, lo, hi, init, res):
        p.columnconfigure(1, weight=1)
        tk.Label(p, text=label, bg=BG, fg=FG,font=FONT, anchor="w").grid(row=row, column=0, sticky="w", pady=2)

        var        = tk.DoubleVar(value=init)
        badge_text = tk.StringVar(value=f"{init:.2f} {unit}".strip())

        tk.Label(p, textvariable=badge_text,
                 bg=ACCENT, fg="#ffffff", font=("Courier", 8, "bold"),
                 padx=6, pady=2, relief="flat", anchor="e", width=10
                ).grid(row=row, column=2, sticky="e", padx=(4, 0), pady=2)

        def _cmd(v, _var=var, _bt=badge_text, _res=res, _u=unit):
            rounded = round(float(v) / _res) * _res
            _var.set(rounded)
            _bt.set(f"{rounded:.2f} {_u}".strip())
            self._update()

        ttk.Scale(p, from_=lo, to=hi, variable=var, orient="horizontal", command=_cmd).grid(row=row, column=1, sticky="ew", padx=(6, 4), pady=2)
        return var

    # Update
    def _update(self):
        try:
            r_orb = float(self.e_rorb.get())
            if r_orb <= 0:
                return
        except ValueError:
            return

        bw_mhz  = self.sl_bw.get()
        rolloff = self.sl_ro.get()
        if bw_mhz <= 0:
            return

        ebn0_disps, margins, min_elevs, bitrates = compute(
            r_orb      = r_orb,
            bw_mhz     = bw_mhz,
            rolloff    = rolloff,
            power_tx   = self.sl_ptx.get(),
            loss_tx    = self.sl_ltx.get(),
            gain_tx    = self.sl_gtx.get(),
            loss_point = self.sl_lpoint.get(),
            loss_atm   = self.sl_latm.get(),
            gain_rx    = self.sl_grx.get(),
            loss_rx    = self.sl_lrx.get(),
            t_ant      = self.sl_tant.get(),
            t_lna      = self.sl_tlna.get(),
            margin_min = self.sl_mmin.get(),
        )
        self._last_ebn0disps = ebn0_disps
        self._last_min_elevs = min_elevs
        self._last_bitrates  = bitrates
        self._last_r_orb     = r_orb

        self._draw(ebn0_disps, min_elevs)
        self._refresh_status(ebn0_disps, margins, min_elevs, bitrates, rolloff)

    # Plot
    def _draw(self, ebn0_disps, min_elevs):
        ax = self.ax
        ax.cla()
        ax.set_facecolor("#ffffff")

        mmin = self.sl_mmin.get()

        # One Eb/N0 curve per modulation
        for mod, ebn0 in ebn0_disps.items():
            col = MOD_COLORS[mod]
            ax.plot(ANG, ebn0, c=col, lw=1.5, label=f"Eb/N0 Disponible {mod}", zorder=5)

        # Horizontal threshold lines with inline text labels
        for mod, req in MOD_REQS.items():
            col = MOD_COLORS[mod]
            eff = req + mmin

            ax.axhline(eff, c=col, ls="--", lw=1.4, zorder=3)

            # text label just above the line, at the right edge
            label_txt = f"{mod} = {eff:.1f} dB"

            ax.text(1, eff + 0.2, label_txt, c=col, ha="left", va="bottom", fontsize=8, fontweight="bold", zorder=7)

            # Fill and min-elevation markers
            for ebn0 in [ebn0_disps[mod]]:
                ax.fill_between(ANG, eff, ebn0, where=ebn0 >= eff, color=col, alpha=0.08, zorder=1)

            elev = min_elevs[mod]

            if elev is not None:
                ax.axvline(elev, c=col, ls=":", lw=0.9, alpha=0.7, zorder=2)
                ax.plot(elev, eff, "o", c=col, ms=7, zorder=6)
                ax.text(elev - 2, eff + 1, f"{elev:.0f}°", c=col, fontsize=12, fontweight='bold', va="top")

        ax.set_xlabel("Ángulo de Elevación (°)", labelpad=3)
        ax.set_ylabel("Eb/N0 (dB)"             , labelpad=3)

        ax.set_xlim(0, 90)
        ax.grid(True, ls="--", lw=0.4, alpha=0.7)
        ax.grid(True, ls="--", lw=0.2, alpha=0.3, which="minor")

        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.yaxis.set_minor_locator(AutoMinorLocator())

        legend = ax.legend(loc="lower right", framealpha=1.0, edgecolor="black", fancybox=False)
        legend.get_frame().set_linewidth(1.0)

        self.fig.tight_layout(pad=1.4)
        self.cv.draw_idle()

    # Status box
    def _refresh_status(self, ebn0_disps, margins, min_elevs, bitrates, rolloff):
        bw_mhz = self.sl_bw.get()
        sym_rate = bw_mhz * 1e6 / (1 + rolloff)

        lines = [
            rf"  Roll-off ($\alpha$) : {rolloff:.2f}",
            f"  Sym. rate    : {sym_rate/1e3:.1f} kbaud",
            "",
        ]

        for mod in ["QPSK", "8-PSK", "16-PSK"]:
            rb     = bitrates[mod]
            mz     = margins[mod][-1]
            elev   = min_elevs[mod]
            stat   = f"VIABLE  >= {elev:.0f} deg" if elev is not None else "NO VIABLE"
            rb_str = f"{rb/1e3:.1f} kbps" if rb < 1e6 else f"{rb/1e6:.3f} Mbps"

            lines.append(f"  {mod:<7}  Rb={rb_str:<12}  M@90°={mz:+.1f} dB  {stat}")
        
        lines += [
            "",
            f"  Eb/N0 @ zenith  QPSK={ebn0_disps['QPSK'][-1]:+.1f}  "
            f"8PSK={ebn0_disps['8-PSK'][-1]:+.1f}  "
            f"16PSK={ebn0_disps['16-PSK'][-1]:+.1f} dB",
        ]

        self.status.configure(state="normal")
        self.status.delete("1.0", "end")
        self.status.insert("end", "\n".join(lines))
        self.status.configure(state="disabled")

    # save
    def _save_plot(self):
        if self._last_ebn0disps is None:
            return

        fig_p, ax_p = plt.subplots()

        fig_p.patch.set_facecolor("#ffffff")
        ax_p.set_facecolor("#ffffff")

        ebn0_disps = self._last_ebn0disps
        min_elevs  = self._last_min_elevs
        mmin       = self.sl_mmin.get()

        for mod, ebn0 in ebn0_disps.items():
            col = MOD_COLORS[mod]
            ax_p.plot(ANG, ebn0, c=col, lw=1.0, label=f"Eb/N0 Disponible {mod}", zorder=5)

        for mod, req in MOD_REQS.items():
            col = MOD_COLORS[mod]
            eff = req + mmin

            ax_p.axhline(eff, c=col, ls="--", lw=1.0, zorder=3)

            label_txt = f"{mod}"
            ax_p.text(1, eff + 0.2, label_txt, c=col, ha="left", va="bottom", fontsize=7, fontweight="bold", zorder=7)

            for ebn0 in [ebn0_disps[mod]]:
                ax_p.fill_between(ANG, eff, ebn0, where=ebn0 >= eff, color=col, alpha=0.08, zorder=1)

            elev = min_elevs[mod]
            if elev is not None:
                ax_p.axvline(elev, c=col, ls=":", lw=0.7, alpha=0.7, zorder=2)
                ax_p.plot(elev, eff, "o", c=col, ms=4, zorder=6)
                ax_p.text(elev - 2.5, eff + 1.25, r"${:.0f}^\circ$".format(elev), c=col, fontsize=12, fontweight='bold', va="top")

        ax_p.set_xlabel(r"Angulo de Elevación ($^\circ$)", labelpad=3)
        ax_p.set_ylabel(r"$E_b/N_0$ (dB)"                 , labelpad=3)

        ax_p.set_xlim(0, 90)
        ax_p.grid(True, ls="--", lw=0.4, alpha=0.7)
        ax_p.grid(True, ls="--", lw=0.2, alpha=0.3, which="minor")

        ax_p.xaxis.set_minor_locator(AutoMinorLocator())
        ax_p.yaxis.set_minor_locator(AutoMinorLocator())

        legend = ax_p.legend(loc="lower right", framealpha=1.0, edgecolor="black", fancybox=False)
        legend.get_frame().set_linewidth(1.0)

        fig_p.tight_layout(pad=0.3)

        out = OUTPUT_DIR / "lb_bw_plot.png"
        fig_p.savefig(out, dpi=600, bbox_inches="tight", format="png")  # dpi alto (tesis.mplstyle), para guardar
        plt.close(fig_p)

        self.save_label.config(text=f"Guardado en {out}")


if __name__ == "__main__":
    App().mainloop()