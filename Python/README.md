# Python

Python port of the DC-motor cascade-control study — reproduces the MATLAB design
and generates the closed-loop step-response figures used in the report.

```
Python/
├── dc_motor.py           # port of the .m files: params, motor TF, operating point, tuning
├── generate_figures.py   # builds the four report figures into results/
├── requirements.txt      # numpy, scipy, matplotlib
└── results/              # generated PNGs (used in ../MATLAB/Report.pdf)
    ├── fig_nominal_response.png     # designed 220 V / 3000 rpm operating point
    ├── fig_order1_rise_time.png     # 1st-order current loop: rise time vs t_r
    ├── fig_order2_damping.png       # 2nd-order speed loop: overshoot vs zeta
    └── fig_order2_settling.png      # 2nd-order speed loop: settling time vs wn
```

## Run

```bash
pip install -r requirements.txt
python dc_motor.py            # prints the design cross-check against MATLAB
python generate_figures.py    # (re)generates the four PNGs in results/
```

On this machine use the Windows launcher: `py dc_motor.py` / `py generate_figures.py`
(tested with Python 3.14, NumPy 2.5, SciPy 1.18, Matplotlib 3.11).

## What it reproduces

`dc_motor.py` mirrors the MATLAB scripts one-to-one and matches every design
quantity exactly (`Kr = 0.031697`, `G(0) = 1.428`, steady speed 3000 rpm, current
PID `0.607 / 4.872 / 0.001`, speed PI `0.0605 / 0.1009`). `generate_figures.py`
then sweeps the controller targets to show how the response changes:

* **Order 1** (current loop, `1/(1+τs)`) — rise time set by the response-time
  target `t_r`, no overshoot.
* **Order 2** (constant-torque speed loop) — overshoot/oscillation set by the
  damping ratio `ζ`, and settling time set by the natural frequency `ωn`.

The figures and their commentary are in the report,
[`../MATLAB/Report.pdf`](../MATLAB/Report.pdf).
