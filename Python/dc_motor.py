"""
DC-motor cascade control — Python port of the MATLAB scripts.

Mirrors:
  * dc_machine_params.m  -> machine_params()
  * dc_tf_function.m     -> motor_tf()
  * main.m               -> operating_point() + tune_current_loop() / tune_speed_loop()

The closed-loop transfer functions used for the report figures follow the exact
design of the MATLAB tuning:

  Inner current loop  (PID, pole-zero cancellation) -> first-order  1 / (1 + tau*s)
  Speed loop, Cr=cte  (PI on kΦ/(J s))              -> second-order (2ζωn s + ωn²)
                                                                    ------------------
                                                                    s² + 2ζωn s + ωn²
"""

from dataclasses import dataclass
import numpy as np


# --------------------------------------------------------------------------- #
# 1. Machine parameters  (port of dc_machine_params.m)
# --------------------------------------------------------------------------- #
@dataclass
class MachineParams:
    Ra: float      # armature resistance [ohm]
    La: float      # armature inductance [H]
    kphi: float    # torque / back-emf constant [V.s/rad]
    J: float       # rotor inertia [kg.m^2]
    fr: float      # viscous friction [N.m.s]
    Lf: float      # series / smoothing inductance [H]
    k: float = 1.25e-2  # equivalent mechanical damping used in the speed tuning


def machine_params(machine: int = 1) -> MachineParams:
    if machine == 1:
        return MachineParams(Ra=2.33, La=10.6e-3, kphi=0.57,
                             J=7.5e-3, fr=1.75e-4, Lf=276e-3, k=1.25e-2)
    if machine == 2:
        return MachineParams(Ra=2.85, La=0.75e-3, kphi=1.5,
                             J=0.395, fr=0.0, Lf=5e-3, k=1.25e-2)
    raise ValueError("machine must be 1 or 2")


# --------------------------------------------------------------------------- #
# 2. Motor transfer function  (port of dc_tf_function.m)
# --------------------------------------------------------------------------- #
def motor_tf(p: MachineParams, Kr: float = 0.0):
    """Return (num, den) of G(s) = Omega(s)/U(s) as polynomial coefficient lists.

    G(s) = kphi / [ (Ra + La s)(J s + fr + Kr) + kphi^2 ]
    """
    # (Ra + La s)(J s + (fr+Kr)) = La*J s^2 + (Ra*J + La*(fr+Kr)) s + Ra*(fr+Kr)
    a2 = p.La * p.J
    a1 = p.Ra * p.J + p.La * (p.fr + Kr)
    a0 = p.Ra * (p.fr + Kr) + p.kphi ** 2
    num = [p.kphi]
    den = [a2, a1, a0]
    return num, den


# --------------------------------------------------------------------------- #
# 3. Operating point + tuning  (port of main.m)
# --------------------------------------------------------------------------- #
@dataclass
class OperatingPoint:
    Kr: float                 # back-computed viscous load coefficient
    dc_gain: float            # G(0)  [rad/s per volt]
    steady_speed_rpm: float   # resulting steady speed
    tau_e: float              # electrical time constant
    tau_m: float              # mechanical time constant
    Tc: float                 # converter dead-time (6-pulse, 50 Hz)


def operating_point(p: MachineParams, target_voltage=220.0, target_rpm=3000.0):
    w_target = target_rpm * 2 * np.pi / 60.0
    Kr = ((p.kphi * target_voltage / w_target) - p.kphi ** 2) / p.Ra - p.fr
    num, den = motor_tf(p, Kr)
    dc_gain = num[-1] / den[-1]
    steady_rpm = dc_gain * target_voltage * 60.0 / (2 * np.pi)
    Tc = 1.0 / (2 * 6 * 50)
    tau_e = (p.La + p.Lf) / p.Ra
    tau_m = (p.J * p.Ra) / (p.kphi ** 2)
    return OperatingPoint(Kr, dc_gain, steady_rpm, tau_e, tau_m, Tc)


def tune_current_loop(p: MachineParams, op: OperatingPoint, tr_i=0.1):
    """PID gains from pole-zero cancellation + 1% settling-time criterion."""
    b = 22.0 / p.Ra
    Ki = 4.6 / (tr_i * b)
    Kp = (op.tau_e + op.Tc) * Ki
    Kd = (op.tau_e * op.Tc) * Ki
    return dict(Kp=Kp, Ki=Ki, Kd=Kd, b=b, tau_cl=tr_i / 4.6)


def tune_speed_loop(p: MachineParams, tr_w=1.0):
    """PI gains for the (nominal) speed loop -> first-order closed loop."""
    a = p.kphi / p.k
    Ki = 4.6 / (tr_w * a)
    Kp = (p.J / p.k) * Ki
    return dict(Kp=Kp, Ki=Ki, a=a, tau_cl=tr_w / 4.6)


# --------------------------------------------------------------------------- #
# 4. Closed-loop transfer functions used by the figures
# --------------------------------------------------------------------------- #
def current_loop_first_order(tr_i: float):
    """First-order closed loop 1/(1+tau s), tau = tr_i/4.6  (rise time set by tr_i)."""
    tau = tr_i / 4.6
    return [1.0], [tau, 1.0], tau


def speed_loop_second_order(zeta: float, wn: float):
    """Actual PI-controlled speed loop for constant load torque.

    T(s) = (2 zeta wn s + wn^2) / (s^2 + 2 zeta wn s + wn^2)
    (the numerator zero at -wn/(2 zeta) is the PI zero — it adds overshoot).
    """
    num = [2 * zeta * wn, wn ** 2]
    den = [1.0, 2 * zeta * wn, wn ** 2]
    return num, den


if __name__ == "__main__":
    p = machine_params(1)
    op = operating_point(p)
    ci = tune_current_loop(p, op)
    sp = tune_speed_loop(p)
    print(f"Kr={op.Kr:.6f}  DC gain={op.dc_gain:.5f}  steady={op.steady_speed_rpm:.1f} rpm")
    print(f"tau_e={op.tau_e:.6f}  tau_m={op.tau_m:.6f}  Tc={op.Tc:.6f}")
    print(f"CURRENT  Kp={ci['Kp']:.4f}  Ki={ci['Ki']:.4f}  Kd={ci['Kd']:.6f}")
    print(f"SPEED    Kp={sp['Kp']:.4f}  Ki={sp['Ki']:.4f}")
