% Writes the openEMS model of the two-arm Archimedean spiral of Section III
% of the paper, fed through one balun standing under the spiral board
% (Fig. 9).
%
%   build_spiral(name, geomfile)
%   build_spiral(name, geomfile, opts)
%
% The spiral board lies in the xy-plane with its copper at z = h. The
% balun board stands along z under the centre, its substrate between
% x = -h/2 and x = h/2, top strip on the +x face and bottom conductor on the
% -x face. The balanced end meets the spiral at z = 0 and the 50 ohm end is
% at z = -L.
%
% opts fields (all optional):
%   turns   number of turns (default 8)
%   r1      inner radius and arm width in mm (default 0.86)
%   board   spiral board side in mm (default 60)
%   nf2ff_f frequencies in Hz for far-field patterns

function build_spiral(name, geomfile, opts)
if nargin < 3, opts = struct(); end
opts = set_default(opts, 'turns', 8);
opts = set_default(opts, 'r1', 0.86);
opts = set_default(opts, 'board', 60);
opts = set_default(opts, 'nf2ff_f', [2 2.5 3 4 5 6 10 15]*1e9);

setup_paths();
p = balun_params();
g = readmatrix(geomfile);
zb = g(:, 1); w = g(:, 2); wb = g(:, 3);
L = zb(end);
h = p.h;
ext = 10;
air = 25;
unit = 1e-3;

FDTD = InitFDTD('NrTS', 400000, 'EndCriteria', 1e-4);
FDTD = SetGaussExcite(FDTD, 8.5e9, 7.5e9);
FDTD = SetBoundaryCond(FDTD, {'PML_8' 'PML_8' 'PML_8' 'PML_8' 'PML_8' 'PML_8'});
CSX = InitCSX();

% Spiral arms. Each arm spans r1 + a*phi to r1 + a*phi + r1, and the
% second arm is the first turned by 180 degrees. a gives a growth of four
% arm widths per turn, so arms and gaps have equal width.
r1 = opts.r1;
a = 4 * r1 / (2*pi);
phi = linspace(0, 2*pi*opts.turns, 120*opts.turns + 1);
rin = r1 + a*phi;
rout = rin + r1;
arm = [rin.*cos(phi) fliplr(rout.*cos(phi)); rin.*sin(phi) fliplr(rout.*sin(phi))];
CSX = AddConductingSheet(CSX, 'spiral', p.sigma_cu, p.t_cu*1e-3);
CSX = AddPolygon(CSX, 'spiral', 10, 2, h, arm);
CSX = AddPolygon(CSX, 'spiral', 10, 2, h, -arm);

CSX = add_substrate(CSX, p, [-opts.board/2 -opts.board/2 0], [opts.board/2 opts.board/2 h]);

% Balun board under the spiral. Its outline is given from the 50 ohm end,
% so the balun coordinate zb maps to z = zb - L.
zz = [-ext; zb] - L;
ww = [p.w50; w];
wwb = [wb(1); wb];
topst = [zz' fliplr(zz'); ww'/2 fliplr(-ww'/2)];
botst = [zz' fliplr(zz'); wwb'/2 fliplr(-wwb'/2)];
CSX = AddConductingSheet(CSX, 'balun', p.sigma_cu, p.t_cu*1e-3);
% Polygons normal to x take their points as (y, z) pairs.
CSX = AddPolygon(CSX, 'balun', 10, 0, h/2, topst([2 1], :));
CSX = AddPolygon(CSX, 'balun', 10, 0, -h/2, botst([2 1], :));
bw = max(wb) + 6;
CSX = AddMaterial(CSX, 'balun_sub');
eps0 = 8.854187817e-12;
CSX = SetMaterialProperty(CSX, 'balun_sub', 'Epsilon', p.er, 'Kappa', 2*pi*10e9*eps0*p.er*p.tand);
CSX = AddBox(CSX, 'balun_sub', 0, [-h/2 -bw/2 -L-ext], [h/2 bw/2 0]);

% The strips continue up through the spiral board and onto its top face,
% where short tabs join them to the inner ends of the arms.
we = w(end);
CSX = AddBox(CSX, 'balun', 11, [h/2 -we/2 0], [h/2 we/2 h]);
CSX = AddBox(CSX, 'balun', 11, [-h/2 -we/2 0], [-h/2 we/2 h]);
CSX = AddBox(CSX, 'balun', 11, [h/2 -we/2 h], [r1 + r1/2 we/2 h]);
CSX = AddBox(CSX, 'balun', 11, [-h/2 -we/2 h], [-r1 - r1/2 we/2 h]);

% Mesh
half = opts.board/2;
fx = [-h/2 h/2 0 r1 -r1 2*r1 -2*r1 [1 -1]*half [1 -1]*(half + air)];
mesh.x = mesh_axis(fx, [-half half 0.25; -h/2 h/2 h/6], 2.5, 1.3);
fy = [0 [1 -1]*we/2 [1 -1]*p.w50/2 [1 -1]*wb(1)/2 [1 -1]*half [1 -1]*(half + air)];
mesh.y = mesh_axis(fy, [-half half 0.25], 2.5, 1.3);
fz = [h 0 h/2 zz' -L-ext-air/2 h+air];
mesh.z = mesh_axis(fz, [0 h h/6; -L-ext 0 0.45], 2.5, 1.3);
CSX = DefineRectGrid(CSX, unit, mesh);

% Microstrip port at the bottom of the balun, wave travelling in +z, field
% from the +x strip to the -x conductor. Reference plane at the board edge.
% The feed has a 50 ohm source resistance. Without it the two halves of the
% antenna are floating conductors, and the small DC content of the
% excitation leaves a static charge on them that decays only through the
% substrate loss.
CSX = AddMetal(CSX, 'PEC');
[CSX, port] = AddMSLPort(CSX, 999, 1, 'PEC', [h/2 -p.w50/2 -L-ext], [-h/2 p.w50/2 -L], 'z', [-1 0 0], ...
    'ExcitePort', true, 'FeedShift', 2, 'MeasPlaneShift', ext, 'Feed_R', 50);

% Near-field box for the far-field transform, a few cells inside the PML.
% The box fields are kept in the frequency domain at the pattern
% frequencies only, which avoids writing the full time signal to disk.
nb_lo = [mesh.x(12) mesh.y(12) mesh.z(12)];
nb_hi = [mesh.x(end-11) mesh.y(end-11) mesh.z(end-11)];
[CSX, nf2ff] = CreateNF2FFBox(CSX, 'nf2ff', nb_lo, nb_hi, 'Frequency', opts.nf2ff_f);

sim = sim_dir(name);
WriteOpenEMS(fullfile(sim, 'model.xml'), FDTD, CSX);
meta.name = name; meta.geomfile = geomfile; meta.opts = opts;
meta.ncells = numel(mesh.x) * numel(mesh.y) * numel(mesh.z);
save(fullfile(sim, 'ports.mat'), 'port', 'nf2ff', 'meta');
fprintf('%s: %d x %d x %d = %.2f M cells, smallest cell %.3f mm, written to %s\n', name, ...
    numel(mesh.x), numel(mesh.y), numel(mesh.z), meta.ncells/1e6, ...
    min([diff(mesh.x) diff(mesh.y) diff(mesh.z)]), sim);
end

function s = set_default(s, f, v)
if ~isfield(s, f), s.(f) = v; end
end
