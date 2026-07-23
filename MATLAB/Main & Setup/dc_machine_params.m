function params = dc_machine_params(machine)

% Returns the DC machine parameters for the selected machine.

if nargin < 1
    machine = 1;
end

if machine == 1
    params.Ra = 2.33;
    params.La = 10.6e-3;
    params.kphi = 0.57;
    params.k=1.25e-2;
    params.J = 7.5e-3;
    params.fr = 1.75e-4;
    params.Lf= 276e-3;

elseif machine == 2
    params.Ra = 2.85;
    params.La = 0.75e-3;
    params.kphi = 1.5;
    params.J = 0.395;
    params.fr = 0;
    params.Lf= 5e-3;

else
    error('Machine must be 1 or 2');
end

end