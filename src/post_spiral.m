% Reads the port of a finished spiral run and prepares the far-field step.
%
%   post_spiral(name)
%
% Writes the input reflection, referred to the port impedance (50 ohm at
% the balun, 188 ohm for a lumped feed), to results/<name>.csv and the input file
% nf2ff.xml for the openEMS far-field tool in the run folder. The tool is
% then run on that file (nf2ff.exe nf2ff.xml) and far_field.py reads its
% output. This replaces CalcNF2FF, whose reader relies on MATLAB's HDF5
% functions, which cannot open files written by HDF5 2.x.
%
% Pattern cuts: theta from 0 to 180 degrees at phi = 0, 90, 180 and 270
% degrees, which together give the full xz and yz planes.

function post_spiral(name)
setup_paths();
sim = fullfile(tempdir, 'balun_sims', name);
S = load(fullfile(sim, 'ports.mat'));

f = linspace(1e9, 16e9, 301);
zref = 50;
if isfield(S.meta, 'zref'), zref = S.meta.zref; end
port = calcPort(S.port, sim, f, 'RefImpedance', zref);
s11 = port.uf.ref ./ port.uf.inc;
out = fullfile(fileparts(mfilename('fullpath')), '..', 'results');
writetable(table(f'/1e9, real(s11)', imag(s11)', 'VariableNames', {'f_GHz', 's11_re', 's11_im'}), ...
    fullfile(out, [name '.csv']));

nf2ff = S.nf2ff;
x.Planes = {};
x.ATTRIBUTE.Outfile = 'nf2ff.h5';
x.ATTRIBUTE.LegacyHDF5 = 1;
for n = 1:numel(nf2ff.filenames_E)
    if nf2ff.directions(n) ~= 0
        fe = dir(fullfile(sim, ['*' nf2ff.filenames_E{n} '.h5']));
        fh = dir(fullfile(sim, ['*' nf2ff.filenames_H{n} '.h5']));
        for k = 1:numel(fe)
            x.Planes{end+1}.ATTRIBUTE.E_Field = fe(k).name;
            x.Planes{end}.ATTRIBUTE.H_Field = fh(k).name;
        end
    end
end
x.ATTRIBUTE.freq = S.meta.opts.nf2ff_f;
x.theta = (0:1:180) * pi/180;
x.phi = [0 90 180 270] * pi/180;
struct_2_xml(fullfile(sim, 'nf2ff.xml'), x, 'nf2ff');

sel = f >= 2e9 & f <= 15e9;
fprintf('%s: |S11| max %.1f dB over 2-15 GHz, %.1f dB over 2.5-15 GHz\n', name, ...
    max(20*log10(abs(s11(sel)))), max(20*log10(abs(s11(f >= 2.5e9 & f <= 15e9)))));
end
