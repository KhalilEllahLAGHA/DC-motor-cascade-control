function results = export_dc_motor_results(outputFolder)
% Run the two saved models and export their response and rectifier figures.
% From the repository root: addpath('MATLAB'); export_dc_motor_results
root = fileparts(mfilename('fullpath'));
if nargin < 1
    outputFolder = fullfile(root, 'assets');
end
if ~isfolder(outputFolder)
    mkdir(outputFolder);
end

names = {'DC_Motor_Control_block_diagram_PID', 'DC_Motor_Control_SPS_rectifier'};
folders = {'PID Block Diagram', 'Library'};
assert(~any(cellfun(@bdIsLoaded, names)), ...
    'Close the two DC motor models before exporting their results.');
parameters = controllerParameters(fullfile(root, 'Main & Setup', 'main.m'));

basicSignals = {
    'Omega_ref',       1, 'speedRef';
    'Gain2',           1, 'speed';
    'PID Controller',  1, 'currentRef';
    'Moteur DC',       2, 'current';
    'Transfer Fcn',    1, 'voltage'};
rectifierSignals = {
    'Subsystem',           1, 'speedRef';
    'Gain2',               1, 'speed';
    'Saturation',          1, 'currentRef';
    'Current Measurement', 1, 'current';
    'Bus Selector',        2, 'torque';
    'Voltage Measurement', 1, 'voltage';
    'Alpha generator',     1, 'firingAngle'};

for index = 1:numel(names)
    model = names{index};
    load_system(fullfile(root, folders{index}, [model '.slx']));
    closeModel = onCleanup(@() close_system(model, 0));
    if index == 1
        fprintf('Simulating the basic-block model.\n');
        results.basic = runModel(model, parameters, basicSignals);
        exportBasicResponse(results.basic, outputFolder);
    else
        fprintf('Simulating the Simscape Electrical rectifier model.\n');
        selector = [model '/Bus Selector'];
        set_param(selector, 'OutputSignals', ...
            [get_param(selector, 'OutputSignals') ',Electrical torque Te (n m)']);
        add_block('simulink/Sinks/Terminator', [model '/Torque logging terminator']);
        add_line(model, 'Bus Selector/2', 'Torque logging terminator/1');
        results.simscape = runModel(model, parameters, rectifierSignals);
        exportSimscapeResponse(results.simscape, outputFolder);
        exportRectifierCycle(results.simscape, outputFolder);
    end
    clear closeModel
end
end

function parameters = controllerParameters(setupScript)
% main.m clears its workspace, so run it inside this local function.
run(setupScript);
parameters = struct('Kp_w', Kp_w, 'Ki_w', Ki_w, ...
    'Kp_i', Kp_i, 'Ki_i', Ki_i, 'Kd_i', Kd_i, ...
    'La', La, 'Lf', Lf, 'Ra', Ra, 'J', J, 'kphi', kphi, 'Tc', Tc);
end

function signals = runModel(model, parameters, sources)
input = Simulink.SimulationInput(model);
for name = string(fieldnames(parameters))'
    input = input.setVariable(char(name), parameters.(name));
end
for row = 1:size(sources, 1)
    ports = get_param([model '/' sources{row, 1}], 'PortHandles');
    set_param(ports.Outport(sources{row, 2}), 'DataLogging', 'on', ...
        'DataLoggingNameMode', 'Custom', 'DataLoggingName', sources{row, 3});
end
input = input.setModelParameter('SignalLogging', 'on');
output = sim(input);
for row = 1:size(sources, 1)
    name = sources{row, 3};
    signals.(name) = output.logsout.getElement(name).Values;
end
end

function exportBasicResponse(data, folder)
[fig, layout] = startFigure(3, 'DC motor response with basic Simulink blocks');
cleanup = onCleanup(@() close(fig));
responseAxes(layout, data.speed, data.speedRef, 'Speed (rpm)', [0 4]);
responseAxes(layout, data.current, data.currentRef, 'Armature current (A)', [0 4]);
ax = nexttile(layout);
plotOverview(ax, data.voltage, '-', [0.02 0.45 0.38]);
styleAxes(ax, 'Averaged converter output (V)', [0 4]);
xlabel(ax, 'Time (s)');
exportgraphics(fig, fullfile(folder, 'dc-motor-block-diagram-response.png'), 'Resolution', 160);
end

function exportSimscapeResponse(data, folder)
[fig, layout] = startFigure(3, 'DC motor response with a six-thyristor rectifier');
cleanup = onCleanup(@() close(fig));
responseAxes(layout, data.speed, data.speedRef, 'Speed (rpm)', [0 20]);
responseAxes(layout, data.current, data.currentRef, 'Armature current (A)', [0 20]);
ax = nexttile(layout);
plotOverview(ax, data.torque, '-', [0.02 0.45 0.38]);
styleAxes(ax, 'Electromagnetic torque (N·m)', [0 20]);
xlabel(ax, 'Time (s)');
exportgraphics(fig, fullfile(folder, 'dc-motor-simscape-response.png'), 'Resolution', 160);
end

function exportRectifierCycle(data, folder)
start = 8.8;
stop = start + 1/50;
[fig, layout] = startFigure(2, 'Six-pulse rectifier during one 50 Hz source cycle');
cleanup = onCleanup(@() close(fig));
title(layout, {'Six-pulse rectifier during one 50 Hz source cycle', ...
    'Simscape Electrical   |   3,000 rpm command   |   8.800–8.820 s'}, ...
    'Color', [0.09 0.16 0.25], 'FontSize', 14, 'FontWeight', 'bold');

traces = {data.voltage, data.current};
labels = {'Bridge DC output (V)', 'Armature current (A)'};
colors = {[0.10 0.34 0.62], [0.02 0.45 0.38]};
for index = 1:2
    ax = nexttile(layout);
    signal = traces{index};
    inCycle = signal.Time >= start & signal.Time <= stop;
    plot(ax, 1000*(signal.Time(inCycle)-start), signal.Data(inCycle), ...
        'Color', colors{index}, 'LineWidth', 1.4);
    styleAxes(ax, labels{index}, [0 20]);
    xticks(ax, 0:2:20);
end
xlabel(ax, 'Time within source cycle (ms)');
exportgraphics(fig, fullfile(folder, 'dc-motor-simscape-rectification.png'), 'Resolution', 160);
end

function [fig, layout] = startFigure(rows, heading)
fig = figure('Visible', 'off', 'Color', 'white', ...
    'Position', [100 100 960 200*rows+75]);
layout = tiledlayout(fig, rows, 1, 'TileSpacing', 'compact', 'Padding', 'compact');
title(layout, heading, 'Color', [0.09 0.16 0.25], ...
    'FontSize', 16, 'FontWeight', 'bold');
end

function responseAxes(layout, measured, reference, label, limits)
ax = nexttile(layout);
hold(ax, 'on');
plotOverview(ax, reference, '--', [0.65 0.26 0.09]);
plotOverview(ax, measured, '-', [0.10 0.34 0.62]);
styleAxes(ax, label, limits);
legend(ax, {'Reference', 'Measured'}, 'Location', 'northeast', 'Box', 'off');
end

function plotOverview(ax, series, lineStyle, color)
step = max(1, floor(numel(series.Time)/20000));
indices = [1:step:numel(series.Time)-1, numel(series.Time)];
plot(ax, series.Time(indices), series.Data(indices), lineStyle, ...
    'Color', color, 'LineWidth', 1.4);
end

function styleAxes(ax, label, limits)
ylabel(ax, label);
xlim(ax, limits);
grid(ax, 'on');
set(ax, 'Box', 'off', 'FontName', 'Arial', 'FontSize', 11, ...
    'XColor', [0.17 0.23 0.31], 'YColor', [0.17 0.23 0.31], ...
    'GridColor', [0.70 0.75 0.82], 'GridAlpha', 0.36, 'Layer', 'top');
end
