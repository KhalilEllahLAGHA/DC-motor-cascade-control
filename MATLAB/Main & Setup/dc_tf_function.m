function G = dc_tf_function(machine, Kr)

% Returns transfer function Omega(s)/U(s)
% with optional viscous load torque Cr = Kr * omega included.

if nargin < 1
    machine = 1;
end

if nargin < 2
    Kr = 0;
end

params = dc_machine_params(machine);

%% -------- TRANSFER FUNCTION --------
s = tf('s');

G = params.kphi / ( (params.Ra + params.La*s) * (params.J*s + params.fr + Kr) + params.kphi^2 );

end