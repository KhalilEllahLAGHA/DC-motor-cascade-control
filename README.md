# DC motor cascade control (MATLAB / Simulink)

Cascade speed-and-current control of a separately-excited **DC machine** fed by a
**three-phase (6-pulse) thyristor rectifier**, modelled in MATLAB/Simulink with
Simscape Electrical (SimPowerSystems). An **outer speed loop** sets the current
reference for an **inner current loop**; the PI/PID gains are tuned analytically
from the machine's electrical and mechanical time constants.

## Contents

| File | What it is |
|---|---|
| `main.m` | Entry script — sets the operating point (e.g. 220 V armature, 3000 rpm), computes the load coefficient, derives the motor transfer function and tunes the current/speed loop gains. |
| `dc_machine_params.m` | DC machine parameters (Ra, La, J, kΦ, …) per machine preset. |
| `dc_tf_function.m` | Builds the motor transfer function from the parameters. |
| `DC_Motor_Control_SPS_PI.slx` | SimPowerSystems model — cascade loops, PI. |
| `DC_Motor_Control_SPS_PID.slx` | SimPowerSystems model — cascade loops, PID. |
| `DC_Motor_Control_SPS_PID_cr_cte.slx` | Constant-load-torque tuning variant. |
| `DC_Motor_Control_SPS_rectifier.slx` | Model with the detailed thyristor rectifier. |
| `DC_Motor_Control_block_diagram_PID.slx` | Transfer-function block-diagram model. |

## Run

1. Open `main.m`, set `machine`, `target_armature_voltage`, `target_speed_rpm`.
2. Run it — it prints the tuned current/speed PI(D) gains and populates the workspace.
3. Open and run the matching `.slx` model.

Requires MATLAB/Simulink with Simscape Electrical (SimPowerSystems).
