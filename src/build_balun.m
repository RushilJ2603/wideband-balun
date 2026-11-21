% Writes the openEMS model of a balun on its own or of two identical baluns
% joined back to back at their balanced ends, as in Fig. 4 of the paper.
%
%   build_balun(name, geomfile)
%   build_balun(name, geomfile, opts)
%
% geomfile is a CSV with columns z, w, wb for one balun: position from the
% unbalanced end (mm), top strip width and bottom conductor width. Widths
% are joined by straight lines between rows, as in Fig. 3 of the paper.
%
% opts fields (all optional):
%   mode      'b2b' for two baluns back to back (default), or 'single' for
%             one balun whose balanced end is closed by a lumped port
%   zload     resistance of that lumped port in ohm (default 188)
%   excite    port that is driven, 1 (default) or 2; 2 is used with mode
%             'single' to get the reflection seen from the balanced end
%   board     substrate width in mm (default 18, the 70 mm x 18 mm board
%             of the paper)
%   ext       50 ohm line added outside each end for the ports (default 10)
%   lossless  true to use PEC and a loss-free substrate (default false)
%   dump_f    frequencies in Hz for field dumps (default 2.5e9)
%   refine    factor by which every cell is made smaller, for a mesh
%             convergence check (default 1)
%
% The model and port data go to a folder from sim_dir(name). The solver is
% then run on model.xml in that folder, and post_balun(name) reads the
% results.

function build_balun(name, geomfile, opts)
if nargin < 3, opts = struct(); end
opts = set_default(opts, 'mode', 'b2b');
opts = set_default(opts, 'zload', 188);
opts = set_default(opts, 'board', 18);
opts = set_default(opts, 'refine', 1);
opts = set_default(opts, 'ext', 10);
opts = set_default(opts, 'lossless', false);
opts = set_default(opts, 'dump_f', 2.5e9);
opts = set_default(opts, 'excite', 1);
single = strcmp(opts.mode, 'single');

setup_paths();
p = balun_params();
if opts.lossless
    p.tand = 0;
end
g = readmatrix(geomfile);
z = g(:, 1); w = g(:, 2); wb = g(:, 3);
L = z(end);
h = p.h;
ext = opts.ext;
air = 20;
unit = 1e-3;

FDTD = InitFDTD('NrTS', 300000, 'EndCriteria', 1e-5);
FDTD = SetGaussExcite(FDTD, 8.25e9, 7.75e9);
FDTD = SetBoundaryCond(FDTD, {'PML_8' 'PML_8' 'PML_8' 'PML_8' 'PML_8' 'PML_8'});
CSX = InitCSX();

% The balun runs from x = -L (50 ohm end) to x = 0 (balanced end). In
% back-to-back mode the second balun is its mirror image about x = 0.
zz = [-ext; z];
ww = [p.w50; w];
wwb = [wb(1); wb];
x = zz - L;
if single
    xt = x; wt = ww; wbt = wwb;
    xend = 0;
else
    xt = [x; flipud(-x)];
    wt = [ww; flipud(ww)];
    wbt = [wwb; flipud(wwb)];
    [xt, k] = unique(xt, 'stable');
    wt = wt(k); wbt = wbt(k);
    xend = L + ext;
end

top = [xt' fliplr(xt'); wt'/2 fliplr(-wt'/2)];
bot = [xt' fliplr(xt'); wbt'/2 fliplr(-wbt'/2)];

if opts.lossless
    CSX = AddMetal(CSX, 'top');
    CSX = AddMetal(CSX, 'bot');
else
    CSX = AddConductingSheet(CSX, 'top', p.sigma_cu, p.t_cu*1e-3);
    CSX = AddConductingSheet(CSX, 'bot', p.sigma_cu, p.t_cu*1e-3);
end
CSX = AddPolygon(CSX, 'top', 10, 2, h, top);
CSX = AddPolygon(CSX, 'bot', 10, 2, 0, bot);
CSX = add_substrate(CSX, p, [-L-ext -opts.board/2 0], [xend opts.board/2 h]);

% Mesh. Fixed lines sit on the edges of the uniform sections: the 50 ohm
% line, the ground under it and the parallel strip. The tapered edges are
% resolved by the fine grid around the centre line.
edges_y = unique(abs([p.w50/2 wb(1)/2 w(end)/2 wb(end)/2]));
fy = [0 edges_y -edges_y [1 -1]*opts.board/2 [1 -1]*(opts.board/2 + air)];
wmax = max(wb)/2 + 0.5;
k = opts.refine;
mesh.y = mesh_axis(fy, [-1.4 1.4 0.08/k; -2.6 2.6 0.15/k; -wmax wmax 0.3/k], 2.0/k, 1.3);
if single
    mesh.x = mesh_axis([xt' -5 air], [-1 1 0.1/k], 0.4/k, 1.3);
else
    mesh.x = mesh_axis([xt' 0], zeros(0, 3), 0.4/k, 1.3);
end
mesh.z = mesh_axis([0 h/2 h -air h+air], [0 h h/(6*k)], 1.5/k, 1.3);
CSX = DefineRectGrid(CSX, unit, mesh);

% Microstrip port on the 50 ohm extension, reference plane at x = -L.
CSX = AddMetal(CSX, 'PEC');
[CSX, port{1}] = AddMSLPort(CSX, 999, 1, 'PEC', [-L-ext -p.w50/2 h], [-L p.w50/2 0], 'x', [0 0 -1], ...
    'ExcitePort', opts.excite == 1, 'FeedShift', 4, 'MeasPlaneShift', ext);
if single
    % Lumped port across the substrate at the balanced end, between the
    % ends of the two strips.
    we = w(end);
    [CSX, port{2}] = AddLumpedPort(CSX, 999, 2, opts.zload, [0 -we/2 0], [0 we/2 h], [0 0 1], opts.excite == 2);
    xm = -5;
else
    [CSX, port{2}] = AddMSLPort(CSX, 999, 2, 'PEC', [L+ext -p.w50/2 h], [L p.w50/2 0], 'x', [0 0 -1], ...
        'MeasPlaneShift', ext);
    xm = 0;
end

% Current through the top and bottom strip on the parallel-strip section.
[~, i] = min(abs(mesh.x - xm));
xm = mesh.x(i);
ym = mesh.y(find(mesh.y > 2, 1));
zmid = mesh.z(find(mesh.z > h/2, 1));
ztop = mesh.z(find(mesh.z > h, 1));
zbot = mesh.z(find(mesh.z < 0, 1, 'last'));
CSX = AddProbe(CSX, 'It_top', 1, 'weight', 1);
CSX = AddBox(CSX, 'It_top', 0, [xm -ym zmid], [xm ym ztop]);
CSX = AddProbe(CSX, 'It_bot', 1, 'weight', 1);
CSX = AddBox(CSX, 'It_bot', 0, [xm -ym zbot], [xm ym zmid]);

% Magnetic field one cell above the top conductor and below the bottom one.
CSX = AddDump(CSX, 'Hf_top', 'DumpType', 11, 'Frequency', opts.dump_f, 'FileType', 1);
CSX = AddBox(CSX, 'Hf_top', 0, [-L-ext -opts.board/2 ztop], [xend opts.board/2 ztop]);
CSX = AddDump(CSX, 'Hf_bot', 'DumpType', 11, 'Frequency', opts.dump_f, 'FileType', 1);
CSX = AddBox(CSX, 'Hf_bot', 0, [-L-ext -opts.board/2 zbot], [xend opts.board/2 zbot]);

sim = sim_dir(name);
WriteOpenEMS(fullfile(sim, 'model.xml'), FDTD, CSX);
meta.name = name; meta.geomfile = geomfile; meta.opts = opts; meta.L = L;
meta.zref = [50 50];
if single, meta.zref(2) = opts.zload; end
meta.ncells = numel(mesh.x) * numel(mesh.y) * numel(mesh.z);
save(fullfile(sim, 'ports.mat'), 'port', 'meta');
fprintf('%s: %d x %d x %d = %.2f M cells, smallest cell %.3f mm, written to %s\n', name, ...
    numel(mesh.x), numel(mesh.y), numel(mesh.z), meta.ncells/1e6, ...
    min([diff(mesh.x) diff(mesh.y) diff(mesh.z)]), sim);
end

function s = set_default(s, f, v)
if ~isfield(s, f), s.(f) = v; end
end
