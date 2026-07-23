"""
Generate the report figures for the DC-motor cascade-control study.

Produces, into results/:
  fig_order1_rise_time.png   - first-order current loop, rise time vs response-time spec
  fig_order2_damping.png     - second-order speed loop, oscillation vs damping ratio zeta
  fig_order2_settling.png    - second-order speed loop, settling time vs natural freq wn
  fig_nominal_response.png   - the actual designed operating point (verification vs MATLAB)
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import signal

import dc_motor as dc

# --------------------------------------------------------------------------- #
# Plot style
# --------------------------------------------------------------------------- #
INK        = "#0b0b0b"
INK_2      = "#52514e"
MUTED      = "#898781"
GRID       = "#e1e0d9"
SURFACE    = "#fcfcfb"
ACCENT     = "#eb6834"   # orange: reference lines / bands

# blue shades — light = small swept value, dark = large swept value
BLUE = {250: "#86b6ef", 350: "#5598e7", 400: "#3987e5", 450: "#2a78d6",
        550: "#1c5cab", 600: "#184f95", 700: "#0d366b"}

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "font.size": 11,
    "font.family": "DejaVu Sans",
    "axes.edgecolor": MUTED,
    "axes.linewidth": 0.8,
    "axes.labelcolor": INK_2,
    "axes.titlecolor": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "text.color": INK,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "legend.frameon": False,
})

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results")
os.makedirs(OUT, exist_ok=True)


def _finish(ax, title, sub):
    ax.set_title(title, fontsize=12.5, fontweight="bold", pad=14, loc="left")
    ax.text(0.0, 1.015, sub, transform=ax.transAxes, fontsize=10,
            color=INK_2, ha="left", va="bottom")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.margins(x=0)


def rise_time_10_90(t, y, yfinal=1.0):
    y10, y90 = 0.1 * yfinal, 0.9 * yfinal
    t10 = np.interp(y10, y, t)
    t90 = np.interp(y90, y, t)
    return t90 - t10


def settling_time(t, y, yfinal=1.0, tol=0.02):
    outside = np.abs(y - yfinal) > tol * yfinal
    idx = np.where(outside)[0]
    return t[idx[-1]] if len(idx) else 0.0


# --------------------------------------------------------------------------- #
# Figure 1 — ORDER 1: current loop, rise time set by the response-time spec
# --------------------------------------------------------------------------- #
def fig_order1():
    tr_values = [0.05, 0.10, 0.20, 0.40]
    colors = [BLUE[250], BLUE[400], BLUE[550], BLUE[700]]
    t = np.linspace(0, 0.6, 2000)

    fig, ax = plt.subplots(figsize=(7.4, 4.3))
    ax.axhline(1.0, color=MUTED, lw=0.8, ls=(0, (4, 3)))
    for tr, c in zip(tr_values, colors):
        num, den, tau = dc.current_loop_first_order(tr)
        _, y = signal.step((num, den), T=t)
        tr1090 = rise_time_10_90(t, y)
        ax.plot(t, y, color=c, lw=2.0,
                label=f"$t_r$ = {tr:.2f} s   (rise {tr1090*1000:.0f} ms)")
    ax.set_xlabel("time  [s]")
    ax.set_ylabel("current  $i_a / i_{ref}$")
    ax.set_ylim(0, 1.12)
    ax.legend(loc="lower right", fontsize=9.5)
    _finish(ax,
            "Inner current loop — first-order response",
            "PID pole–zero cancellation ⇒ $T(s)=1/(1+\\tau s)$, $\\tau=t_r/4.6$ — no overshoot")
    fig.tight_layout()
    p = os.path.join(OUT, "fig_order1_rise_time.png")
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


# --------------------------------------------------------------------------- #
# Figure 2 — ORDER 2: speed loop, oscillation set by damping ratio zeta
# --------------------------------------------------------------------------- #
def fig_order2_damping():
    wn = 5.0
    zetas = [0.2, 0.4, 0.707, 1.0, 2.0]
    colors = [BLUE[250], BLUE[400], BLUE[450], BLUE[600], BLUE[700]]
    t = np.linspace(0, 4.0, 3000)

    fig, ax = plt.subplots(figsize=(7.4, 4.3))
    ax.axhline(1.0, color=MUTED, lw=0.8, ls=(0, (4, 3)))
    for z, c in zip(zetas, colors):
        num, den = dc.speed_loop_second_order(z, wn)
        _, y = signal.step((num, den), T=t)
        os_pct = max(0.0, (y.max() - 1.0) * 100.0)
        lbl = f"ζ = {z:.3g}"
        lbl += f"   (OS {os_pct:.0f}%)" if os_pct > 0.5 else "   (no overshoot)"
        ax.plot(t, y, color=c, lw=2.0, label=lbl)
    ax.set_xlabel("time  [s]")
    ax.set_ylabel("speed  $\\omega / \\omega_{ref}$")
    ax.set_ylim(0, 1.7)
    ax.legend(loc="upper right", fontsize=9.5)
    _finish(ax,
            "Constant-torque speed loop — second-order response",
            "$\\omega_n=5$ rad/s fixed · lower ζ ⇒ more overshoot & oscillation")
    fig.tight_layout()
    p = os.path.join(OUT, "fig_order2_damping.png")
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


# --------------------------------------------------------------------------- #
# Figure 3 — ORDER 2: speed loop, settling time set by natural frequency wn
# --------------------------------------------------------------------------- #
def fig_order2_settling():
    zeta = 0.7
    wns = [2.0, 5.0, 10.0, 20.0]
    colors = [BLUE[250], BLUE[400], BLUE[550], BLUE[700]]
    t = np.linspace(0, 3.5, 4000)

    fig, ax = plt.subplots(figsize=(7.4, 4.3))
    # +/-2% settling band
    ax.axhspan(0.98, 1.02, color=ACCENT, alpha=0.10, lw=0)
    ax.axhline(1.0, color=MUTED, lw=0.8, ls=(0, (4, 3)))
    for wn, c in zip(wns, colors):
        num, den = dc.speed_loop_second_order(zeta, wn)
        _, y = signal.step((num, den), T=t)
        ts = settling_time(t, y, tol=0.02)
        ax.plot(t, y, color=c, lw=2.0,
                label=f"$\\omega_n$ = {wn:.0f} rad/s   ($t_s$ ≈ {ts:.2f} s)")
    ax.text(3.48, 1.02, "±2% band", color=ACCENT, fontsize=8.5, ha="right", va="bottom")
    ax.set_xlabel("time  [s]")
    ax.set_ylabel("speed  $\\omega / \\omega_{ref}$")
    ax.set_ylim(0, 1.3)
    ax.legend(loc="lower right", fontsize=9.5)
    _finish(ax,
            "Constant-torque speed loop — second-order response",
            "ζ = 0.7 fixed · higher $\\omega_n$ ⇒ faster settling, same overshoot shape")
    fig.tight_layout()
    p = os.path.join(OUT, "fig_order2_settling.png")
    fig.savefig(p, dpi=200)
    plt.close(fig)
    return p


# --------------------------------------------------------------------------- #
# Figure 4 — the actual designed operating point (verification vs MATLAB)
# --------------------------------------------------------------------------- #
def fig_nominal():
    p = dc.machine_params(1)
    op = dc.operating_point(p)
    ci = dc.tune_current_loop(p, op, tr_i=0.1)
    sp = dc.tune_speed_loop(p, tr_w=1.0)

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.1))

    # inner current loop, tr_i = 0.1 s
    t1 = np.linspace(0, 0.4, 2000)
    num, den, tau = dc.current_loop_first_order(0.1)
    _, y1 = signal.step((num, den), T=t1)
    ts1 = settling_time(t1, y1, tol=0.02)
    ax = axes[0]
    ax.axhline(1.0, color=MUTED, lw=0.8, ls=(0, (4, 3)))
    ax.plot(t1, y1, color=BLUE[450], lw=2.2)
    ax.axvline(0.1, color=ACCENT, lw=1.0, ls=":")
    ax.text(0.104, 0.15, "$t_r$ = 0.1 s", color=ACCENT, fontsize=9, rotation=90, va="bottom")
    ax.set_title(f"Current loop (PID)\nKp={ci['Kp']:.3f}  Ki={ci['Ki']:.3f}  Kd={ci['Kd']:.4f}",
                 fontsize=10.5, color=INK, loc="left")
    ax.set_xlabel("time  [s]"); ax.set_ylabel("$i_a / i_{ref}$")
    ax.set_ylim(0, 1.1); ax.margins(x=0)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

    # nominal speed loop, tr_w = 1 s (first order)
    t2 = np.linspace(0, 3.0, 2000)
    _, y2 = signal.step(([1.0], [1.0/4.6, 1.0]), T=t2)
    ax = axes[1]
    ax.axhline(1.0, color=MUTED, lw=0.8, ls=(0, (4, 3)))
    ax.plot(t2, y2, color=BLUE[550], lw=2.2)
    ax.axvline(1.0, color=ACCENT, lw=1.0, ls=":")
    ax.text(1.04, 0.15, "$t_r$ = 1 s", color=ACCENT, fontsize=9, rotation=90, va="bottom")
    ax.set_title(f"Speed loop (PI)\nKp={sp['Kp']:.4f}  Ki={sp['Ki']:.4f}",
                 fontsize=10.5, color=INK, loc="left")
    ax.set_xlabel("time  [s]"); ax.set_ylabel("$\\omega / \\omega_{ref}$")
    ax.set_ylim(0, 1.1); ax.margins(x=0)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)

    fig.suptitle("Designed operating point — 220 V / 3000 rpm  (10× time-scale separation)",
                 fontsize=12.5, fontweight="bold", x=0.02, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out = os.path.join(OUT, "fig_nominal_response.png")
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out, op, ci, sp


if __name__ == "__main__":
    f1 = fig_order1()
    f2 = fig_order2_damping()
    f3 = fig_order2_settling()
    f4, op, ci, sp = fig_nominal()
    print("Saved:")
    for f in (f1, f2, f3, f4):
        print("  ", os.path.relpath(f, HERE))
    print("\n--- verification against MATLAB ---")
    print(f"Kr={op.Kr:.6f}  DC gain={op.dc_gain:.5f}  steady={op.steady_speed_rpm:.1f} rpm")
    print(f"CURRENT  Kp={ci['Kp']:.4f}  Ki={ci['Ki']:.4f}  Kd={ci['Kd']:.6f}")
    print(f"SPEED    Kp={sp['Kp']:.4f}  Ki={sp['Ki']:.4f}")
