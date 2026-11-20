% Uniform 50 ohm microstrip on RT/duroid 5880 over an 18 mm wide ground,
% with the same ports, mesh rules and materials as the balun models. Used
% to check the setup before the balun runs.
%
%   check_msl('build')   writes the model to sim_dir('check_msl')
%   check_msl('post')    reads the finished run, writes results/check_msl.csv

function check_msl(step)
setup_paths();
p = balun_params();
name = 'check_msl';
L = 40;
w = p.w50;
h = p.h;
wg = 18;
air = 20;

if strcmp(step, 'build')
    FDTD = InitFDTD('NrTS', 300000, 'EndCriteria', 1e-5);
    FDTD = SetGaussExcite(FDTD, 8.25e9, 7.75e9);
    FDTD = SetBoundaryCond(FDTD, {'PML_8' 'PML_8' 'PML_8' 'PML_8' 'PML_8' 'PML_8'});
    CSX = InitCSX();
    CSX = add_substrate(CSX, p, [-L/2 -15 0], [L/2 15 h]);
    CSX = AddConductingSheet(CSX, 'bot', p.sigma_cu, p.t_cu*1e-3);
    CSX = AddBox(CSX, 'bot', 10, [-L/2 -wg/2 0], [L/2 wg/2 0]);

    mesh.x = mesh_axis([-L/2 L/2 0], zeros(0, 3), 0.4, 1.3);
    mesh.y = mesh_axis([0 [1 -1]*w/2 [1 -1]*wg/2 [1 -1]*15 [1 -1]*(15 + air)], ...
        [-1.4 1.4 0.08; -2.6 2.6 0.15; -9.5 9.5 0.3], 2.0, 1.3);
    mesh.z = mesh_axis([0 h/2 h -air h+air], [0 h h/6], 1.5, 1.3);
    CSX = DefineRectGrid(CSX, 1e-3, mesh);

    CSX = AddMetal(CSX, 'PEC');
    [CSX, port{1}] = AddMSLPort(CSX, 999, 1, 'PEC', [-L/2 -w/2 h], [-L/2+10 w/2 0], 'x', [0 0 -1], ...
        'ExcitePort', true, 'FeedShift', 4, 'MeasPlaneShift', 10);
    [CSX, port{2}] = AddMSLPort(CSX, 999, 2, 'PEC', [L/2 -w/2 h], [L/2-10 w/2 0], 'x', [0 0 -1], ...
        'MeasPlaneShift', 10);
    CSX = AddConductingSheet(CSX, 'top', p.sigma_cu, p.t_cu*1e-3);
    CSX = AddBox(CSX, 'top', 10, [-L/2+10 -w/2 h], [L/2-10 w/2 h]);

    sim = sim_dir(name);
    WriteOpenEMS(fullfile(sim, 'model.xml'), FDTD, CSX);
    save(fullfile(sim, 'ports.mat'), 'port');
    fprintf('%s written to %s\n', name, sim);
else
    sim = fullfile(tempdir, 'balun_sims', name);
    S = load(fullfile(sim, 'ports.mat'));
    f = linspace(0.5e9, 16e9, 621);
    port = calcPort(S.port, sim, f, 'RefImpedance', 50);
    s11 = port{1}.uf.ref ./ port{1}.uf.inc;
    s21 = port{2}.uf.ref ./ port{1}.uf.inc;
    z0 = real(port{1}.ZL);
    out = fullfile(fileparts(mfilename('fullpath')), '..', 'results');
    writetable(table(f'/1e9, z0', 20*log10(abs(s11))', 20*log10(abs(s21))', ...
        'VariableNames', {'f_GHz', 'Z0_ohm', 's11_dB', 's21_dB'}), fullfile(out, [name '.csv']));
    fprintf('Z0 at 2, 6, 10, 14 GHz: %s ohm\n', mat2str(interp1(f, z0, [2 6 10 14]*1e9), 4));
    fprintf('max |S11| %.1f dB, |S21| at 10 GHz %.3f dB\n', max(20*log10(abs(s11))), ...
        20*log10(abs(interp1(f, s21, 10e9))));
end
end
