import os
import numpy as np
import tkinter as tk
import matplotlib
import matplotlib.pyplot as plt

from tkinter import ttk
from matplotlib.ticker import AutoMinorLocator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
matplotlib.use("TkAgg")

# Constants
FREQ       = 2.2e9
WLEN       = 3e8 / FREQ
R_EARTH    = 6378
K_DB       = -228.6
EBN0_QPSK  = 9.6
EBN0_8PSK  = 13.3
EBN0_16PSK = 18.3
ANG        = np.arange(0.0, 90.1, 0.1)
RAD        = np.deg2rad(ANG)

MOD_COLORS = {"QPSK": "#2d7dd2", "8-PSK": "#1d9e75", "16-PSK": "#d85a30"}
MOD_REQS   = {"QPSK": EBN0_QPSK, "8-PSK": EBN0_8PSK, "16-PSK": EBN0_16PSK}

BG      = "#ffffff"
BG2     = "#f5f5f5"
FG      = "#2c2c2a"
FG_MUT  = "#73726c"
ACCENT  = "#185fa5"
FONT    = ("Helvetica", 9)
MONO    = ("Courier", 9)

PAPER_RC = {
    "text.usetex": True,
    "text.latex.preamble": r"\usepackage{bm} \renewcommand{\seriesdefault}{\bfdefault} \boldmath",
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "font.weight": "bold",
    "axes.labelsize": 8,
    "axes.labelweight": "bold",
    "font.size": 8,
    "legend.fontsize": 7,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
}


# ── Computation ───────────────────────────────────────────────────────────────
def compute(r_orb, bit_rate, power_tx, loss_tx, gain_tx, loss_point, loss_atm, gain_rx, loss_rx, t_ant, t_lna, margin_min):
    eirp      = power_tx - loss_tx + gain_tx
    
    d         = (np.sqrt((R_EARTH*1e3 + r_orb*1e3)**2 - (R_EARTH*1e3 * np.cos(RAD))**2) - R_EARTH*1e3 * np.sin(RAD))
    fsl       = 20 * np.log10(4 * np.pi * d / WLEN)
    loss_path = fsl + loss_point + loss_atm
    
    rsl       = eirp - loss_path + gain_rx - loss_rx
    
    t_sys     = t_ant + t_lna
    n0        = K_DB + 10 * np.log10(t_sys)
    
    ebn0_disp = rsl - n0 - 10 * np.log10(bit_rate)
    
    margins   = {k: ebn0_disp - v for k, v in MOD_REQS.items()}

    def min_elev(m):
        idx = np.where(m >= margin_min)[0]
        return ANG[idx[0]] if len(idx) else None

    return ebn0_disp, margins, {k: min_elev(v) for k, v in margins.items()}

# ── GUI ───────────────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Satellite Link Budget  —  LEO @ 2.2 GHz")
        self.configure(bg=BG)
        self.resizable(True, True)
        self._last_ebn0      = None
        self._last_min_elevs = None
        self._last_r_orb     = 600
        self._last_bit_rate  = 500000
        self._build()
        self._update()

    def _build(self):
        self.columnconfigure(0, weight=0, minsize=340)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # ── Left column ──
        left = tk.Frame(self, bg=BG)
        left.grid(row=0, column=0, sticky="nsew")
        left.rowconfigure(0, weight=1)
        left.rowconfigure(1, weight=0)
        left.columnconfigure(0, weight=1)

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

        cvs.bind("<Configure>", lambda e: cvs.itemconfigure(wid, width=e.width))
        cvs.bind_all("<MouseWheel>", lambda e: cvs.yview_scroll(int(-e.delta/120), "units"))

        r = 0
        r = self._sep(inner, "Órbita y señal", r)
        self.e_rorb  = self._entry(inner, "Radio de órbita", "km",  "600",    r); r += 1
        self.e_brate = self._entry(inner, "Tasa de bits",    "bps", "500000", r); r += 1

        r = self._sep(inner, "Transmisor", r)
        self.sl_ptx    = self._slider(inner, "Potencia Tx",        "dBW", r, -10, 30, 0.0,  0.5);   r += 1
        self.sl_ltx    = self._slider(inner, "Pérdidas Tx",        "dB",  r,   0,  5, 1.0,  0.5);   r += 1
        self.sl_gtx    = self._slider(inner, "Ganancia Tx",        "dBi", r,   0, 45, 5.0,  0.5);   r += 1

        r = self._sep(inner, "Trayecto", r)
        self.sl_lpoint = self._slider(inner, "Pérd. apuntamiento", "dB",  r,   0,  5, 1.0,  0.1);   r += 1
        self.sl_latm   = self._slider(inner, "Pérd. atmosférica",  "dB",  r,   0,  5, 1.0,  0.1);   r += 1

        r = self._sep(inner, "Receptor", r)
        self.sl_grx    = self._slider(inner, "Ganancia Rx",        "dBi", r,   0, 45, 25.0, 0.5);   r += 1
        self.sl_lrx    = self._slider(inner, "Pérdidas Rx",        "dB",  r,   0,  5,  1.0, 0.5);   r += 1

        r = self._sep(inner, "Ruido del sistema", r)
        self.sl_tant   = self._slider(inner, "T antena",           "K",   r,  10, 300,  55.0, 1.0); r += 1
        self.sl_tlna   = self._slider(inner, "T LNA",              "K",   r,  10, 500, 120.0, 1.0); r += 1

        r = self._sep(inner, "Criterio de cierre", r)
        self.sl_mmin   = self._slider(inner, "Margen mínimo",      "dB",  r,   0,  10,  1.0, 1.0);   r += 1

        # ── Status box ──
        status_wrap = tk.Frame(left, bg=BG2, highlightthickness=1, highlightbackground="#c4c2ba")
        status_wrap.grid(row=1, column=0, sticky="ew")

        tk.Label(status_wrap, text="ESTADO DEL ENLACE", bg=BG2, fg=FG_MUT, font=("Helvetica", 8, "bold"), anchor="w", padx=12, pady=5).pack(fill="x")
        ttk.Separator(status_wrap).pack(fill="x")

        self.status = tk.Text(
            status_wrap, height=7, bg=BG2, fg=FG, font=MONO, relief="flat", 
            bd=0, highlightthickness=0, state="disabled", padx=12, pady=6, wrap="none"
        )

        self.status.pack(fill="x")

        # ── Save button ──
        btn_frame = tk.Frame(left, bg=BG2, highlightthickness=1, highlightbackground="#c4c2ba")
        btn_frame.grid(row=2, column=0, sticky="ew")

        save_btn = tk.Button(
            btn_frame,
            text             = "Guardar gráfico",
            command          = self._save_plot,
            bg               = ACCENT, 
            fg               = "#ffffff",
            font             = ("Helvetica", 9, "bold"),
            relief           = "flat", 
            bd               = 0,
            padx             = 12, 
            pady             = 7,
            activebackground = "#134f8a",
            activeforeground = "#ffffff",
            cursor           = "hand2",
        )

        save_btn.pack(fill="x", padx=10, pady=8)

        self.save_label = tk.Label(btn_frame, text="", bg=BG2, fg=FG_MUT, font=("Helvetica", 8), anchor="center")
        self.save_label.pack(fill="x", padx=10, pady=(0, 6))

        # ── Right column (plot) ──
        right = tk.Frame(self, bg=BG, padx=10, pady=12)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        self.fig, self.ax = plt.subplots(figsize=(7, 5.4))
        self.fig.patch.set_facecolor(BG)
        self.ax.set_facecolor("#ffffff")

        self.cv = FigureCanvasTkAgg(self.fig, master=right)
        self.cv.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    # ── Widget constructors ───────────────────────────────────────────────────
    def _sep(self, p, title, row):
        tk.Label(p, text=title.upper(), bg=BG, fg=FG_MUT, font=("Helvetica", 8, "bold"), anchor="w").grid(row=row, column=0, columnspan=3, sticky="ew", pady=(12, 1))
        
        row += 1
        ttk.Separator(p).grid(row=row, column=0, columnspan=3, sticky="ew", pady=(0, 4))
        
        return row + 1

    def _entry(self, p, label, unit, default, row):
        p.columnconfigure(1, weight=1)
        tk.Label(p, text=label, bg=BG, fg=FG, font=FONT, anchor="w").grid(row=row, column=0, sticky="w", pady=3)
        var    = tk.StringVar(value=default)
        
        holder = tk.Frame(p, bg=ACCENT)
        holder.grid(row=row, column=1, columnspan=2, sticky="ew", padx=(6, 0), pady=3)
        
        ent = tk.Entry(holder, textvariable=var, font=("Courier", 10), bg="#ffffff", fg=ACCENT, insertbackground=ACCENT, relief="flat", bd=3, highlightthickness=0)
        ent.pack(side="left", fill="x", expand=True)
        
        tk.Label(holder, text=f" {unit} ", bg=ACCENT, fg="#ffffff", font=("Helvetica", 8, "bold")).pack(side="right")
        
        var.trace_add("write", lambda *_: self._update())
        return var

    def _slider(self, p, label, unit, row, lo, hi, init, res):
        p.columnconfigure(1, weight=1)
        tk.Label(p, text=label, bg=BG, fg=FG, font=FONT, anchor="w").grid(row=row, column=0, sticky="w", pady=2)
        
        var        = tk.DoubleVar(value=init)
        badge_text = tk.StringVar(value=f"{init:.1f} {unit}")
        badge      = tk.Label(
                              p, textvariable=badge_text, 
                              bg=ACCENT, fg="#ffffff", 
                              font=("Courier", 8, "bold"), 
                              padx=6, pady=2, 
                              relief="flat", anchor="e", width=9
                            )
        
        badge.grid(row=row, column=2, sticky="e", padx=(4, 0), pady=2)

        def _cmd(v, _var=var, _bt=badge_text, _res=res, _u=unit):
            rounded = round(float(v) / _res) * _res
            _var.set(rounded)
            _bt.set(f"{rounded:.1f} {_u}")
            self._update()

        sl = ttk.Scale(p, from_=lo, to=hi, variable=var, orient="horizontal", command=_cmd)
        sl.grid(row=row, column=1, sticky="ew", padx=(6, 4), pady=2)
        return var

    # ── Actions ───────────────────────────────────────────────────────────────
    def _update(self):
        try:
            r_orb    = float(self.e_rorb.get())
            bit_rate = float(self.e_brate.get())
            if r_orb <= 0 or bit_rate <= 0:
                return
        except ValueError:
            return

        ebn0_disp, margins, min_elevs = compute(
            r_orb      = r_orb,
            bit_rate   = bit_rate,
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
        self._last_ebn0      = ebn0_disp
        self._last_min_elevs = min_elevs
        self._last_r_orb     = r_orb
        self._last_bit_rate  = bit_rate

        self._draw(ebn0_disp, min_elevs)
        self._refresh_status(ebn0_disp, margins, min_elevs)

    def _save_plot(self):
        if self._last_ebn0 is None:
            return

        with matplotlib.rc_context(PAPER_RC):
            fig_p, ax_p = plt.subplots(figsize=(3.5, 2.8))
            fig_p.patch.set_facecolor("#ffffff")
            ax_p.set_facecolor("#ffffff")

            ebn0_disp = self._last_ebn0
            min_elevs = self._last_min_elevs
            mmin      = self.sl_mmin.get()

            ax_p.plot(ANG, ebn0_disp, color="#2c2c2a", lw=1.5, label=r"$E_b/N_0$ Available", zorder=5)

            for mod, req in MOD_REQS.items():
                col = MOD_COLORS[mod]
                eff = req + mmin
                ax_p.axhline(eff, color=col, ls="--", lw=1.0, label=r"{} req+margin={:.1f} dB".format(mod, eff), zorder=3)
                ax_p.fill_between(ANG, eff, ebn0_disp, where=ebn0_disp >= eff, color=col, alpha=0.09, zorder=1)
                
                elev = min_elevs[mod]
                if elev is not None:
                    ax_p.axvline(elev, color=col, ls=":", lw=0.8, alpha=0.7, zorder=2)
                    ax_p.plot(elev, eff, 'o', color=col, markersize=4, zorder=6)
                    ax_p.text(elev - 4, eff + 0.3, r"${:.0f}^\circ$".format(elev), color=col, fontsize=7, va="bottom")

            ax_p.set_xlabel(r"Elevation Angle ($^\circ$)", labelpad=3)
            ax_p.set_ylabel(r"$E_b/N_0$ (dB)", labelpad=3)
            ax_p.set_xlim(0, 90)
            ax_p.grid(True, linestyle='--', linewidth=0.4, alpha=0.7, which="major")
            ax_p.grid(True, linestyle='--', linewidth=0.2, alpha=0.3, which="minor")
            ax_p.xaxis.set_minor_locator(AutoMinorLocator())
            ax_p.yaxis.set_minor_locator(AutoMinorLocator())

            legend = ax_p.legend(loc="lower right", framealpha=1.0, edgecolor='black', fancybox=False)
            legend.get_frame().set_linewidth(1.0)

            fig_p.tight_layout(pad=0.3)

            output_path = os.path.expanduser("~/Downloads/link_budget_plot.png")
            fig_p.savefig(output_path, dpi=300, bbox_inches='tight', format='png')
            plt.close(fig_p)

        self.save_label.config(text="Guardado en ~/Downloads/LinkBudget_plot.png")

    def _draw(self, ebn0_disp, min_elevs):
        ax = self.ax
        ax.cla()
        ax.set_facecolor("#ffffff")

        ax.plot(ANG, ebn0_disp, color="#2c2c2a", lw=2.2, label=r"Eb/N0 Available", zorder=5)

        mmin = self.sl_mmin.get()

        for mod, req in MOD_REQS.items():
            col = MOD_COLORS[mod]
            eff = req + mmin
            ax.axhline(eff, color=col, ls="--", lw=1.5, label=f"{mod} req+margin={eff:.1f} dB", zorder=3)
            ax.fill_between(ANG, eff, ebn0_disp, where=ebn0_disp >= eff, color=col, alpha=0.09, zorder=1)
            
            elev = min_elevs[mod]
            if elev is not None:
                ax.axvline(elev, color=col, ls=":", lw=1.0, alpha=0.7, zorder=2)
                ax.plot(elev, eff, 'o', color=col, markersize=7, zorder=6)
                ax.text(elev - 4, eff + 0.3, f"{elev:.0f}°", color=col, fontsize=9, va="bottom")

        ax.set_xlabel("Elevation Angle (°)", fontsize=10)
        ax.set_ylabel("Eb/N0 (dB)", fontsize=10)
        ax.set_xlim(0, 90)

        ax.grid(True, linestyle='--', linewidth=0.4, alpha=0.7, which="major")
        ax.grid(True, linestyle='--', linewidth=0.2, alpha=0.3, which="minor")
        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.yaxis.set_minor_locator(AutoMinorLocator())

        legend = ax.legend(loc="lower right", framealpha=1.0, edgecolor='black', fancybox=False)
        legend.get_frame().set_linewidth(1.0)

        self.fig.tight_layout(pad=1.4)
        self.cv.draw_idle()

    def _refresh_status(self, ebn0_disp, margins, min_elevs):
        lines = [
            f"  Eb/N0 @ zenith (90°) : {ebn0_disp[-1]:+6.2f} dB",
            f"  Eb/N0 @ 5° elevacion : {ebn0_disp[50]:+6.2f} dB",
            "",
        ]

        for mod in ["QPSK", "8-PSK", "16-PSK"]:
            mz   = margins[mod][-1]
            elev = min_elevs[mod]
            req  = MOD_REQS[mod]
            stat = f"VIABLE  >= {elev:.0f} deg" if elev is not None else "NO VIABLE"
            lines.append(f"  {mod:<7}  req={req:.2f} dB  M@90={mz:+.1f} dB  {stat}")

        self.status.configure(state="normal")
        self.status.delete("1.0", "end")
        self.status.insert("end", "\n".join(lines))
        self.status.configure(state="disabled")


if __name__ == "__main__":
    App().mainloop()