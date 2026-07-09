clear;
clc;

% Change these values before running Simulink.
machine = 1;
target_armature_voltage = 220;
target_speed_rpm = 3000;

params = dc_machine_params(machine);
target_speed_rad_s = target_speed_rpm * 2 * pi / 60;
viscous_load_coeff = ((params.kphi * target_armature_voltage / target_speed_rad_s) - params.kphi^2) / params.Ra - params.fr;

G_motor = dc_tf_function(machine, viscous_load_coeff);

[num_motor, den_motor] = tfdata(G_motor, 'v');

steady_speed_rad_s = dcgain(G_motor) * target_armature_voltage;
steady_speed_rpm = steady_speed_rad_s * 60 / (2 * pi);

%% ============================
% PI TUNING
% ============================

Ra = params.Ra;
La = params.La;
J  = params.J;
Lf = params.Lf;
kphi = params.kphi;
k=params.k;
Tc = 1/(2*6*50);
tau_e = (La+Lf)  / Ra;
tau_m = (J*Ra)/(kphi*kphi);

% % ---- CURRENT LOOP ----
tr_i=0.1;
b=22/Ra;
temp1 = tau_e * Tc;
temp2 = tau_e + Tc;
Ki_i = 4.6/(tr_i*b);
Kp_i = temp2*Ki_i;
Kd_i = temp1*Ki_i;

% temp1 = tau_e;
% Ki_i = 10;
% Kp_i = temp1*Ki_i;

% ---- SPEED LOOP ----
tr_w=1;
a=kphi/k;
Temp = J/k;
Ki_w = 4.6/(tr_w*a);
Kp_w = Temp*Ki_w;

% % ---- CURRENT LOOP Cr = cte ----
% tr_i=0.01;
% temp1 = tau_e * Tc;
% temp2 = tau_m;
% Ki_i = 4.6*Tc*Ra/(tr_i*tau_m*22);
% Kp_i = temp2*Ki_i;
% Kd_i = temp1*Ki_i;
% 
% % ---- SPEED LOOP Cr = cte ----
% zeta = 5;
% wn = 5;
% Kp_w = (2 * zeta * wn * J) / kphi;
% Ki_w = (wn^2 * J) / kphi;

%% Display
fprintf('\nCURRENT PI: Kp=%.2f | Ki=%.2f | Kd=%.2f\n', Kp_i, Ki_i, Kd_i);
% fprintf('\nCURRENT PI: Kp=%.2f | Ki=%.2f \n', Kp_i, Ki_i);
fprintf('SPEED PI:   Kp=%.2f | Ki=%.2f\n', Kp_w, Ki_w);
