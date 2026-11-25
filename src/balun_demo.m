% Demonstration of the project in MATLAB. Run balun_demo with no argument
% for a control window, or give the name of one view:
%
%   balun_demo('model')     3D model of both baluns
%   balun_demo('viewer')    openEMS model of the improved balun with its
%                           mesh, in AppCSXCAD
%   balun_demo('profile')   impedance and widths along the taper
%   balun_demo('run')       build and run a coarse model of the improved
%                           balun, then plot it over the full run
%   balun_demo('run', 'paper')   the same for the paper design
%   balun_demo('last')      plot the last coarse run again ('last', 'paper').
%                           If no finished run is left in the temp folder,
%                           the saved copy in results/ is plotted.
%   balun_demo('paper')     structure B against Fig. 7(d) of the paper
%   balun_demo('mesh')      paper design on three meshes
%   balun_demo('steps')     taper length and profile changed one at a time
%   balun_demo('improved')  paper design against improved design
%   balun_demo('balance')   phase and amplitude of the strip currents
%   balun_demo('fields')    E field in three cross-sections at 5 GHz
%   balun_demo('movie')     Ez of the pulse moving through the balun
%   balun_demo('spiral')    input match of the spiral antenna
%   balun_demo('pattern')   radiation pattern, with a frequency menu

function fig = balun_demo(view, varargin)
cd(fileparts(mfilename('fullpath')));
if nargin == 0
    view = 'control';
end
switch view
    case 'control',  h = control_window();
    case 'model',    h = show_model();
    case 'viewer',   h = show_viewer();
    case 'mesh',     h = show_mesh();
    case 'profile',  h = show_profile();
    case 'run',      h = run_live(varargin{:});
    case 'last',     h = last_run(varargin{:});
    case 'paper',    h = show_paper();
    case 'steps',    h = show_steps();
    case 'improved', h = show_improved();
    case 'balance',  h = show_balance();
    case 'fields',   h = show_fields();
    case 'movie',    h = show_movie(varargin{:});
    case 'spiral',   h = show_spiral();
    case 'pattern',  h = show_pattern(varargin{:});
    otherwise, error('unknown view: %s', view);
end
if nargout > 0, fig = h; end
end

function fig = control_window()
items = {
    'Simulation', '';
    '3D model', 'model';
    'Model and mesh in openEMS', 'viewer';
    'Run simulation: improved (3 min)', 'run';
    'Run simulation: paper design (3 min)', 'run_paper';
    'Show the last run again', 'last';
    'Pulse moving through the balun', 'movie';
    'E field in the cross-section', 'fields';
    'Validation', '';
    'Structure B against the paper', 'paper';
    'Mesh check', 'mesh';
    'Current balance', 'balance';
    'Spiral antenna, S11', 'spiral';
    'Spiral antenna, pattern', 'pattern';
    'Improvement', '';
    'Impedance along the taper', 'profile';
    'What each change did', 'steps';
    'Paper design against improved', 'improved'};
n = size(items, 1);
h = 34;
fig = figure('Name', 'Wideband balun', 'NumberTitle', 'off', 'MenuBar', 'none', 'ToolBar', 'none', ...
    'Color', 'w', 'Position', [40 80 340 h*n + 20]);
for k = 1:n
    y = h*(n - k) + 10;
    if isempty(items{k, 2})
        uicontrol(fig, 'Style', 'text', 'String', items{k, 1}, 'Position', [15 y 310 24], ...
            'BackgroundColor', 'w', 'FontSize', 11, 'FontWeight', 'bold', 'HorizontalAlignment', 'left');
    else
        uicontrol(fig, 'Style', 'pushbutton', 'String', items{k, 1}, 'Position', [15 y 310 30], ...
            'FontSize', 10, 'Callback', @(~, ~) press(items{k, 2}));
    end
end
end

function press(v)
if strcmp(v, 'run_paper')
    balun_demo('run', 'paper');
else
    balun_demo(v);
end
end

% ---------------------------------------------------------------- model

function fig = show_model()
fig = new_figure('3D model', [60 60 1250 640]);
t = tiledlayout(fig, 2, 1, 'Padding', 'compact', 'TileSpacing', 'compact');
draw_balun(nexttile(t), 'paper_B_stated', 'Paper design: exponential taper over 45 mm');
draw_balun(nexttile(t), 'improved', 'Improved design: Klopfenstein taper over 60 mm');
end

function draw_balun(ax, name, ttl)
g = readmatrix(geo(name));
z = g(:, 1); w = g(:, 2); wb = g(:, 3);
h = 1.5748;
hold(ax, 'on');
xs = [0 70 70 0];
ys = [-9 -9 9 9];
for zz = [0.03 h - 0.03]
    patch(ax, xs, ys, zz*[1 1 1 1], [0.91 0.89 0.80], 'FaceAlpha', 0.25, 'EdgeColor', [0.6 0.6 0.55]);
end
for s = [-9 9]
    patch(ax, xs, s*[1 1 1 1], [0 0 h h], [0.91 0.89 0.80], 'FaceAlpha', 0.35, 'EdgeColor', [0.6 0.6 0.55]);
end
px = [z; flipud(z)];
patch(ax, px, [w; -flipud(w)]/2, h*ones(size(px)), [0.85 0.50 0.20], 'EdgeColor', 'none');
patch(ax, px, [wb; -flipud(wb)]/2, -0.03*ones(size(px)), [0.55 0.30 0.12], 'EdgeColor', 'none');
text(ax, -1, 0, h + 2, '50 \Omega, unbalanced', 'FontSize', 10, 'HorizontalAlignment', 'left');
text(ax, 71, 0, h + 2, '188 \Omega, balanced', 'FontSize', 10, 'HorizontalAlignment', 'right');
daspect(ax, [1 1 0.35]);
view(ax, -18, 38);
grid(ax, 'on');
xlabel(ax, 'z (mm)'); ylabel(ax, 'y (mm)'); zlabel(ax, 'mm');
title(ax, ttl, 'FontWeight', 'normal');
xlim(ax, [-2 72]); ylim(ax, [-10 10]); zlim(ax, [-1 6]);
rotate3d(ax, 'on');
end

function fig = show_profile()
fig = new_figure('Impedance along the taper', [80 80 1150 520]);
a = readtable(res('profile_paper_B_stated'));
b = readtable(res('profile_improved'));
c = palette();
t = tiledlayout(fig, 1, 2, 'Padding', 'compact');
ax = nexttile(t); hold(ax, 'on');
plot(ax, a.z_mm, a.Z_ohm, 'Color', c.paper, 'LineWidth', 2.2, 'DisplayName', 'paper design, exponential');
plot(ax, b.z_mm, b.Z_ohm, 'Color', c.improved, 'LineWidth', 2.2, 'DisplayName', 'improved, Klopfenstein');
xlabel(ax, 'distance from the 50 \Omega end (mm)'); ylabel(ax, 'line impedance (\Omega)');
legend(ax, 'Location', 'southeast'); grid(ax, 'on'); xlim(ax, [0 70]);
title(ax, 'Impedance', 'FontWeight', 'normal');
ax = nexttile(t); hold(ax, 'on');
plot(ax, a.z_mm, a.w_mm, 'Color', c.paper, 'LineWidth', 2, 'DisplayName', 'paper, top strip');
plot(ax, a.z_mm, a.wb_mm, '--', 'Color', c.paper, 'LineWidth', 2, 'DisplayName', 'paper, ground');
plot(ax, b.z_mm, b.w_mm, 'Color', c.improved, 'LineWidth', 2, 'DisplayName', 'improved, top strip');
plot(ax, b.z_mm, b.wb_mm, '--', 'Color', c.improved, 'LineWidth', 2, 'DisplayName', 'improved, ground');
set(ax, 'YScale', 'log'); xlabel(ax, 'distance from the 50 \Omega end (mm)'); ylabel(ax, 'width (mm)');
legend(ax, 'Location', 'northeast'); grid(ax, 'on'); xlim(ax, [0 70]);
title(ax, 'Conductor widths', 'FontWeight', 'normal');
end

% ------------------------------------------------------------- live run

% A failed run falls back to the saved copy of the same coarse run in
% results/, so there is always a graph to show.
function fig = run_live(design)
if nargin < 1, design = 'improved'; end
d = live_design(design);
exe = fullfile(openems_root(), 'openEMS.exe');
try
    if ~exist(exe, 'file'), error('%s not found', exe); end
    build_balun(d.name, geo(d.geom), struct('refine', 0.6, 'ext', 14));
    fprintf('Running openEMS on the %s. The solver window closes when it finishes.\n', d.lab);
    ps = fullfile(pwd, 'no_throttle.ps1');
    launch('powershell.exe', sprintf('-NoProfile -ExecutionPolicy Bypass -Command "Start-Sleep 5; & ''%s''"', ps));
    t0 = tic;
    status = system(sprintf('start "openEMS: %s" /wait /d "%s" "%s" model.xml --numThreads=16', d.lab, d.sim, exe));
    if status ~= 0, error('openEMS stopped with status %d', status); end
    secs = toc(t0);
    writematrix(secs, fullfile(d.sim, 'done.txt'));
    fprintf('Solver finished in %.0f s.\n', secs);
catch e
    warning('balun_demo:run', 'The live run did not finish (%s). Showing the saved coarse run.', e.message);
end
fig = last_run(design);
end

function fig = last_run(design)
if nargin < 1, design = 'improved'; end
d = live_design(design);
done = fullfile(d.sim, 'done.txt');
fresh = exist(done, 'file') == 2;
if fresh
    try
        [f, s11, s21] = live_sp(d.sim);
        S = load(fullfile(d.sim, 'ports.mat'));
        cells = S.meta.ncells/1e6;
        secs = readmatrix(done);
        who = 'this run';
    catch
        fresh = false;
    end
end
if ~fresh
    [f, s11, s21] = sp(d.name);
    I = run_info(d.name);
    cells = I.cells_M;
    secs = I.solve_s;
    who = 'saved coarse run';
end
[ff, a, b] = sp(d.full);
F = run_info(d.full);
c = palette();
fig = new_figure(['Live run: ' d.lab], [90 90 1150 580]);
ax = axes(fig); hold(ax, 'on');
plot(ax, ff, a, 'Color', c.grey, 'LineWidth', 1.6, 'DisplayName', '|S11| full mesh, saved run');
plot(ax, f, s11, 'Color', c.improved, 'LineWidth', 2.4, 'DisplayName', ['|S11| ' who ', coarse mesh']);
plot(ax, ff, b, 'Color', c.grey, 'LineWidth', 1.2, 'LineStyle', '--', 'DisplayName', '|S21| full mesh, saved run');
plot(ax, f, s21, 'Color', c.paper, 'LineWidth', 2.2, 'DisplayName', ['|S21| ' who ', coarse mesh']);
finish_s(ax, {sprintf('Back to back, %s: %s has %.2f M cells and took %.0f s', d.lab, who, cells, secs), ...
    sprintf('|S11| below -10 dB from %.2f GHz (full mesh, %.1f M cells: %.2f GHz)', ...
    lower_edge(f, s11), F.cells_M, lower_edge(ff, a))});
end

function d = live_design(design)
if strcmp(design, 'paper')
    d = struct('name', 'live_paper', 'full', 'b2b_paper_B_stated', 'geom', 'paper_B_stated', 'lab', 'paper design');
else
    d = struct('name', 'live_improved', 'full', 'b2b_improved', 'geom', 'improved', 'lab', 'improved design');
end
d.sim = fullfile(tempdir, 'balun_sims', d.name);
end

function [f, s11, s21] = live_sp(sim)
setup_paths();
S = load(fullfile(sim, 'ports.mat'));
fq = linspace(0.5e9, 16e9, 621);
port = S.port;
for k = 1:2
    port{k} = calcPort(port{k}, sim, fq, 'RefImpedance', 50);
end
f = fq/1e9;
s11 = 20*log10(abs(port{1}.uf.ref ./ port{1}.uf.inc));
s21 = 20*log10(abs(port{2}.uf.ref ./ port{1}.uf.inc));
end

function I = run_info(name)
T = readtable(res('run_info'));
I = T(strcmp(T.run, name), :);
end

function r = openems_root()
r = getenv('OPENEMS_DIR');
if isempty(r), r = 'C:\openEMS'; end
end

% ------------------------------------------------------------------- mesh

function fig = show_viewer()
fprintf('Writing the openEMS model of the improved balun...\n');
build_balun('view_improved', geo('improved'));
xml = fullfile(tempdir, 'balun_sims', 'view_improved', 'model.xml');
launch(fullfile(openems_root(), 'AppCSXCAD.exe'), sprintf('--disableEdit "%s"', xml));
fig = [];
end

% Starts a program without waiting for it. MATLAB's system() waits for
% programs started with "start" as well, so .NET is used instead.
function launch(exe, args)
psi = System.Diagnostics.ProcessStartInfo(exe, args);
psi.UseShellExecute = false;
psi.CreateNoWindow = true;
System.Diagnostics.Process.Start(psi);
end

function fig = show_mesh()
runs = {'live_paper', 'coarse (live run)'; 'b2b_paper_B_stated', 'normal (all results)'; ...
    'b2b_paper_B_stated_fine', 'fine, cells 1.5 times smaller'};
cols = [0.97 0.72 0.55; 0.91 0.38 0.16; 0.45 0.15 0.04];
widths = [3.4 2.2 1.3];
fig = new_figure('Mesh check', [110 110 1250 560]);
t = tiledlayout(fig, 1, 2, 'Padding', 'compact');
a1 = nexttile(t); hold(a1, 'on');
a2 = nexttile(t); hold(a2, 'on');
for k = 1:3
    [f, s11, s21] = sp(runs{k, 1});
    I = run_info(runs{k, 1});
    plot(a1, f, s11, 'Color', cols(k, :), 'LineWidth', widths(k), ...
        'DisplayName', sprintf('%s, %.1f M cells: from %.2f GHz', runs{k, 2}, I.cells_M, lower_edge(f, s11)));
    plot(a2, f, s21, 'Color', cols(k, :), 'LineWidth', widths(k), 'DisplayName', runs{k, 2});
end
yline(a1, -10, ':', 'Color', [0.3 0.3 0.3], 'HandleVisibility', 'off');
xlim(a1, [0.5 15]); ylim(a1, [-50 2]); grid(a1, 'on');
xlim(a2, [0.5 15]); ylim(a2, [-3 0]); grid(a2, 'on');
xlabel(a1, 'frequency (GHz)'); ylabel(a1, '|S11| (dB)');
xlabel(a2, 'frequency (GHz)'); ylabel(a2, '|S21| (dB)');
legend(a1, 'Location', 'southoutside', 'FontSize', 9);
legend(a2, 'Location', 'southoutside', 'FontSize', 9);
title(a1, 'Paper design back to back, |S11| on three meshes', 'FontWeight', 'normal');
title(a2, '|S21|', 'FontWeight', 'normal');
end

% ------------------------------------------------------------ S-parameters

function fig = show_paper()
[f, s11, s21] = sp('b2b_paper_B_stated');
P = readtable(fullfile('..', 'data', 'paper', 'fig7d_structure_B.csv'));
c = palette();
fig = new_figure('Structure B against the paper', [100 100 1150 560]);
ax = axes(fig); hold(ax, 'on');
plot(ax, P.f_GHz, P.paper_sim_s11_dB, '--', 'Color', [0.45 0.45 0.45], 'LineWidth', 1.5, 'DisplayName', '|S11| paper, CST');
plot(ax, P.f_GHz, P.paper_meas_s11_dB, 'Color', [0.65 0.65 0.65], 'LineWidth', 1.2, 'DisplayName', '|S11| paper, measured');
plot(ax, f, s11, 'Color', c.improved, 'LineWidth', 2.4, 'DisplayName', '|S11| this work, openEMS');
plot(ax, f, s21, 'Color', c.paper, 'LineWidth', 2.2, 'DisplayName', '|S21| this work, openEMS');
finish_s(ax, sprintf('Structure B back to back: below -10 dB from %.2f to 15 GHz (paper 1.75 to 15 GHz)', lower_edge(f, s11)));
end

function fig = show_steps()
runs = {'paper_B_stated', 'paper: exponential, 45 mm'; ...
    'step_exp60', 'longer: exponential, 60 mm'; ...
    'step_klop45', 'new shape: Klopfenstein, 45 mm'; ...
    'improved', 'both: Klopfenstein, 60 mm'};
cols = [0.91 0.38 0.16; 0.30 0.65 0.40; 0.55 0.35 0.75; 0.16 0.47 0.85];
fig = new_figure('What each change did', [120 120 1280 590]);
t = tiledlayout(fig, 1, 2, 'Padding', 'compact');
for m = 1:2
    ax = nexttile(t); hold(ax, 'on');
    pre = {'b2b_', 'single_'};
    for k = 1:size(runs, 1)
        [f, s] = sp([pre{m} runs{k, 1}]);
        plot(ax, f, s, 'Color', cols(k, :), 'LineWidth', 2.1, ...
            'DisplayName', sprintf('%s: from %.2f GHz', runs{k, 2}, lower_edge(f, s)));
    end
    yline(ax, -10, ':', 'Color', [0.3 0.3 0.3], 'HandleVisibility', 'off');
    xlim(ax, [0.6 4]); ylim(ax, [-35 0]); grid(ax, 'on');
    xlabel(ax, 'frequency (GHz)'); ylabel(ax, '|S11| (dB)');
    legend(ax, 'Location', 'southoutside', 'FontSize', 9);
    if m == 1
        title(ax, 'Back to back', 'FontWeight', 'normal');
    else
        title(ax, 'One balun into 188 \Omega', 'FontWeight', 'normal');
    end
end
end

function fig = show_improved()
c = palette();
fig = new_figure('Paper design against improved', [130 130 1150 680]);
t = tiledlayout(fig, 2, 1, 'Padding', 'compact');
titles = {'Back to back', 'One balun into 188 \Omega'};
runs = {'b2b_paper_B_stated', 'b2b_improved'; 'single_paper_B_stated', 'single_improved'};
for m = 1:2
    ax = nexttile(t); hold(ax, 'on');
    xregion(ax, 1, 2, 'FaceColor', [0.93 0.91 0.83], 'HandleVisibility', 'off');
    [f, a] = sp(runs{m, 1});
    [~, b] = sp(runs{m, 2});
    plot(ax, f, a, 'Color', c.paper, 'LineWidth', 2, 'DisplayName', sprintf('paper design, from %.2f GHz', lower_edge(f, a)));
    plot(ax, f, b, 'Color', c.improved, 'LineWidth', 2.2, 'DisplayName', sprintf('improved, from %.2f GHz', lower_edge(f, b)));
    finish_s(ax, [titles{m} ', |S11| (shaded: L band)']);
end
end

function fig = show_balance()
c = palette();
fig = new_figure('Current balance', [140 140 1150 500]);
t = tiledlayout(fig, 1, 2, 'Padding', 'compact');
a1 = nexttile(t); hold(a1, 'on');
a2 = nexttile(t); hold(a2, 'on');
names = {'b2b_paper_B_stated', 'paper design', c.paper; 'b2b_improved', 'improved', c.improved};
for k = 1:2
    T = readtable(res(names{k, 1}));
    r = (T.itop_re + 1i*T.itop_im) ./ (T.ibot_re + 1i*T.ibot_im);
    p = mod(angle(r)*180/pi, 360);
    sel = T.f_GHz >= 1 & T.f_GHz <= 15;
    plot(a1, T.f_GHz(sel), p(sel), 'Color', names{k, 3}, 'LineWidth', 2.1, 'DisplayName', names{k, 2});
    plot(a2, T.f_GHz(sel), 20*log10(abs(r(sel))), 'Color', names{k, 3}, 'LineWidth', 2.1, 'DisplayName', names{k, 2});
end
yline(a1, 180, '--', 'Color', [0.4 0.4 0.4], 'HandleVisibility', 'off');
yline(a2, 0, '--', 'Color', [0.4 0.4 0.4], 'HandleVisibility', 'off');
ylim(a1, [160 200]); ylim(a2, [-3 3]); xlim(a1, [1 15]); xlim(a2, [1 15]);
grid(a1, 'on'); grid(a2, 'on');
xlabel(a1, 'frequency (GHz)'); xlabel(a2, 'frequency (GHz)');
ylabel(a1, 'phase of I_{top} / I_{bottom} (deg)'); ylabel(a2, '|I_{top} / I_{bottom}| (dB)');
legend(a1, 'Location', 'northeast');
end

% ------------------------------------------------------------------ fields

function fig = show_fields()
D = load(res_mat('movie_improved'));
fig = new_figure('E field in the cross-section, 5 GHz', [150 150 1300 470]);
t = tiledlayout(fig, 1, 3, 'Padding', 'compact');
names = {'z = 2.5 mm: microstrip, field to the wide ground', 'z = 35 mm: inside the taper', ...
    'z = 67.5 mm: parallel strip, balanced'};
geom = readmatrix(geo('improved'));
for k = 1:3
    ax = nexttile(t); hold(ax, 'on');
    y = D.(sprintf('y%d', k)); z = D.(sprintf('z%d', k));
    Ey = D.(sprintf('Ey%d', k)); Ez = D.(sprintf('Ez%d', k));
    m = sqrt(Ey.^2 + Ez.^2);
    L = 20*log10(m'/max(m(:)) + 1e-6);
    imagesc(ax, y, z, L);
    set(ax, 'YDir', 'normal');
    clim(ax, [-30 0]); colormap(ax, 'turbo');
    span = max(max(geom_at(geom, k), 1.5) + 2, 3.5);
    ky = max(1, round(span/20/(y(2) - y(1))));
    iy = 1:ky:numel(y); iz = 1:ky:numel(z);
    [Y, Z] = meshgrid(y(iy), z(iz));
    u = Ey(iy, iz)'./(m(iy, iz)' + 1e-12);
    v = Ez(iy, iz)'./(m(iy, iz)' + 1e-12);
    off = L(iz, iy) < -24;
    u(off) = NaN; v(off) = NaN;
    quiver(ax, Y, Z, u, v, 0.5, 'k', 'LineWidth', 0.6);
    zp = [2.5 35 67.5];
    w = interp1(geom(:, 1), geom(:, 2), zp(k));
    wb = interp1(geom(:, 1), geom(:, 3), zp(k));
    plot(ax, [-w w]/2, 1.5748*[1 1], 'w', 'LineWidth', 3);
    plot(ax, [-wb wb]/2, [0 0], 'w', 'LineWidth', 3);
    xlim(ax, [-span span]); ylim(ax, [-2.5 4]);
    xlabel(ax, 'y (mm)'); ylabel(ax, 'z (mm)');
    title(ax, names{k}, 'FontWeight', 'normal', 'FontSize', 10);
end
cb = colorbar(ax); cb.Layout.Tile = 'east'; cb.Label.String = '|E| (dB)';
end

function s = geom_at(geom, k)
zp = [2.5 35 67.5];
s = interp1(geom(:, 1), geom(:, 3), zp(k))/2;
end

function fig = show_movie(nloop, t_show)
if nargin < 1, nloop = 1; end
D = load(res_mat('movie_improved'));
g = readmatrix(geo('improved'));
nf = size(D.Ez, 3);
fig = new_figure('Pulse moving through the balun', [100 180 1320 520]);
ax = axes(fig, 'Position', [0.07 0.24 0.82 0.66]);
I = imagesc(ax, D.x, D.y, double(D.Ez(:, :, 1))'/127);
set(ax, 'YDir', 'normal'); hold(ax, 'on');
xe = [g(:, 1) - 70; flipud(70 - g(:, 1))];
plot(ax, xe, [g(:, 2); flipud(g(:, 2))]/2, 'k', xe, -[g(:, 2); flipud(g(:, 2))]/2, 'k', 'LineWidth', 0.9);
plot(ax, xe, [g(:, 3); flipud(g(:, 3))]/2, 'k--', xe, -[g(:, 3); flipud(g(:, 3))]/2, 'k--', 'LineWidth', 0.8);
pbaspect(ax, [4.6 1 1]);
clim(ax, [-1 1]); colormap(ax, diverging());
cb = colorbar(ax); cb.Label.String = 'E_z in the substrate (normalised)';
xlabel(ax, 'x (mm)    solid: top strip, dashed: ground'); ylabel(ax, 'y (mm)');
ttl = title(ax, '', 'FontWeight', 'normal');
s = uicontrol(fig, 'Style', 'slider', 'Min', 1, 'Max', nf, 'Value', 1, 'SliderStep', [1 10]/(nf - 1), ...
    'Units', 'normalized', 'Position', [0.07 0.03 0.72 0.05], 'Callback', @(h, ~) draw(round(h.Value)));
uicontrol(fig, 'Style', 'pushbutton', 'String', 'Play', 'Units', 'normalized', ...
    'Position', [0.81 0.03 0.08 0.05], 'FontSize', 10, 'Callback', @(~, ~) play());
draw(1);
if nargin > 1
    [~, k] = min(abs(D.t_ns - t_show));
    draw(k);
else
    for n = 1:nloop, play(); end
end

    function draw(k)
        I.CData = double(D.Ez(:, :, k))'/127;
        ttl.String = sprintf('Improved balun back to back, t = %.2f ns', D.t_ns(k));
        s.Value = k;
    end

    function play()
        for k = 1:nf
            if ~isvalid(fig), return; end
            draw(k);
            drawnow;
            pause(0.06);
        end
    end
end

function m = diverging()
n = 128;
a = [linspace(0.10, 1, n)' linspace(0.35, 1, n)' linspace(0.75, 1, n)'];
b = [linspace(1, 0.80, n)' linspace(1, 0.15, n)' linspace(1, 0.10, n)'];
m = [a; b];
end

% ----------------------------------------------------------------- antenna

function fig = show_spiral()
P = readtable(fullfile('..', 'data', 'paper', 'fig10_spiral.csv'));
c = palette();
fig = new_figure('Spiral antenna, S11', [170 170 1150 560]);
ax = axes(fig); hold(ax, 'on');
plot(ax, P.f_GHz, P.paper_sim_s11_dB, '--', 'Color', [0.45 0.45 0.45], 'LineWidth', 1.4, 'DisplayName', 'paper, CST (Fig. 10)');
plot(ax, P.f_GHz, P.paper_meas_s11_dB, 'Color', [0.65 0.65 0.65], 'LineWidth', 1.2, 'DisplayName', 'paper, measured');
[f, a] = sp('spiral_full');
[g, b] = sp('spiral_full_improved');
plot(ax, f, a, 'Color', c.paper, 'LineWidth', 2.1, 'DisplayName', 'antenna with the paper design');
plot(ax, g, b, 'Color', c.improved, 'LineWidth', 2.1, 'DisplayName', 'antenna with the improved balun');
finish_s(ax, 'Spiral antenna with its balun, one openEMS model');
ylim(ax, [-40 0]);
end

function fig = show_pattern(fq)
if nargin < 1, fq = 10; end
T = readtable(res('spiral_full_patterns'));
T.f_GHz = round(T.f_GHz, 3);
list = unique(T.f_GHz);
fig = new_figure('Spiral antenna, pattern', [180 60 720 760]);
ax = polaraxes(fig, 'Units', 'normalized', 'Position', [0.12 0.12 0.76 0.74]);
uicontrol(fig, 'Style', 'text', 'String', 'Frequency (GHz)', 'Units', 'normalized', ...
    'Position', [0.03 0.94 0.2 0.04], 'BackgroundColor', 'w', 'FontSize', 10);
uicontrol(fig, 'Style', 'popupmenu', 'String', compose('%g', list), 'Units', 'normalized', ...
    'Position', [0.24 0.945 0.14 0.04], 'Value', find(list == fq), 'FontSize', 10, ...
    'Callback', @(s, ~) draw_pattern(ax, T, list(s.Value)));
draw_pattern(ax, T, fq);
end

function draw_pattern(ax, T, fq)
c = palette();
cla(ax); hold(ax, 'on');
if fq == 10
    P = readtable(fullfile('..', 'data', 'paper', 'fig11_pattern_10GHz.csv'));
    polarplot(ax, deg2rad(P.angle_deg), max(P.paper_sim_dB, -30), 'Color', [0.45 0.45 0.45], ...
        'LineWidth', 2.4, 'DisplayName', 'paper, Fig. 11 (CST)');
end
for pl = {'E', c.improved, 'xz plane (E)'; 'H', c.paper, 'yz plane (H)'}'
    d = T(T.f_GHz == fq & strcmp(T.plane, pl{1}), :);
    polarplot(ax, deg2rad(d.theta_deg), max(d.E_dB, -30), 'Color', pl{2}, 'LineWidth', 1.7, 'DisplayName', pl{3});
end
ax.ThetaZeroLocation = 'top'; ax.ThetaDir = 'counterclockwise';
ax.RLim = [-30 0]; ax.RTick = [-30 -20 -10 0];
title(ax, sprintf('%g GHz, normalised |E| (dB)', fq), 'FontWeight', 'normal');
legend(ax, 'Location', 'southoutside', 'Orientation', 'horizontal');
end

% ----------------------------------------------------------------- helpers

function [f, s11, s21] = sp(name)
T = readtable(res(name));
f = T.f_GHz;
s11 = 20*log10(abs(T.s11_re + 1i*T.s11_im));
if ismember('s21_re', T.Properties.VariableNames)
    s21 = 20*log10(abs(T.s21_re + 1i*T.s21_im));
else
    s21 = [];
end
end

% Lowest frequency from which |S11| stays below -10 dB up to 15 GHz.
function lo = lower_edge(f, s)
k = find(f <= 15 & s >= -10, 1, 'last');
if isempty(k)
    lo = f(1);
else
    lo = f(k) + (f(k + 1) - f(k)) * (-10 - s(k)) / (s(k + 1) - s(k));
end
end

function finish_s(ax, ttl)
yline(ax, -10, ':', 'Color', [0.3 0.3 0.3], 'HandleVisibility', 'off');
xlim(ax, [0.5 15]); ylim(ax, [-50 2]); grid(ax, 'on');
xlabel(ax, 'frequency (GHz)'); ylabel(ax, 'magnitude (dB)');
legend(ax, 'Location', 'southoutside', 'Orientation', 'horizontal', 'NumColumns', 2);
title(ax, ttl, 'FontWeight', 'normal');
end

function fig = new_figure(name, pos)
fig = figure('Name', name, 'NumberTitle', 'off', 'Color', 'w', 'Position', pos);
set(fig, 'DefaultAxesFontSize', 12);
end

function c = palette()
c.paper = [0.91 0.38 0.16];
c.improved = [0.16 0.47 0.85];
c.grey = [0.55 0.55 0.55];
end

function p = geo(name)
p = fullfile('..', 'geometry', [name '.csv']);
end

function p = res(name)
p = fullfile('..', 'results', [name '.csv']);
end

function p = res_mat(name)
p = fullfile('..', 'results', [name '.mat']);
end
