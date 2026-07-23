# DC motor cascade control

Cascade speed-and-current control of a separately-excited **DC machine** fed by a
**three-phase (6-pulse) thyristor rectifier**. An **outer speed loop** sets the
current reference for an **inner current loop**; the PI/PID gains are tuned
analytically from the machine's electrical and mechanical time constants.

The full write-up (system overview, controlled rectifier and firing-angle model,
plant transfer function, analytical PID design, and the Simulink models) is in
**[`MATLAB/Report.pdf`](MATLAB/Report.pdf)**.

## Layout

| Folder | Contents |
|---|---|
| [`MATLAB/`](MATLAB/) | The MATLAB/Simulink work — setup scripts, the Simulink models, and the report. |
| [`Python/`](Python/) | An independent Python port that reproduces the tuning and generates the response figures. |

### MATLAB/

```
MATLAB/
├── Report.pdf           full report
├── Main & Setup/        main.m, dc_machine_params.m, dc_tf_function.m
├── PID Block Diagram/   transfer-function block-diagram model (.slx)
├── Library/             SimPowerSystems model with the detailed thyristor rectifier (.slx)
├── Variants/            alternative SPS models kept for comparison
└── assets/              diagram images exported from the models
```

Run:

1. Open `MATLAB/Main & Setup/main.m`, set `machine`, `target_armature_voltage`,
   `target_speed_rpm`.
2. Run it — it prints the tuned current/speed PI(D) gains and populates the
   workspace.
3. Open and run the matching `.slx` model.

Requires MATLAB/Simulink R2024a with Simscape Electrical (SimPowerSystems).

### Python/

A NumPy/SciPy re-implementation that matches the MATLAB design exactly and produces
the closed-loop step-response figures. See [`Python/README.md`](Python/README.md).

```bash
cd Python
pip install -r requirements.txt
python dc_motor.py          # prints the design cross-check against MATLAB
python generate_figures.py  # regenerates the figures in results/
```
