% Reads a finished balun run and writes the results to results/<name>.csv.
%
% CSV columns: frequency (GHz), S11 and S21 (real, imaginary), and the
% currents through the top and bottom strip at the junction (real,
% imaginary). The field dumps are read by export_fields.py instead, since
% MATLAB's HDF5 reader cannot open files written by HDF5 2.x.

function post_balun(name)
setup_paths();
sim = fullfile(tempdir, 'balun_sims', name);
S = load(fullfile(sim, 'ports.mat'));
port = S.port;

f = linspace(0.5e9, 16e9, 621);
zref = S.meta.zref;
for k = 1:2
    port{k} = calcPort(port{k}, sim, f, 'RefImpedance', zref(k));
end
s11 = port{1}.uf.ref ./ port{1}.uf.inc;
s21 = (port{2}.uf.ref / sqrt(zref(2))) ./ (port{1}.uf.inc / sqrt(zref(1)));

I = ReadUI({'It_top', 'It_bot'}, sim, f);
it = I.FD{1}.val;
ib = I.FD{2}.val;

out = fullfile(fileparts(mfilename('fullpath')), '..', 'results');
if ~exist(out, 'dir'), mkdir(out); end
T = table(f'/1e9, real(s11)', imag(s11)', real(s21)', imag(s21)', ...
    real(it)', imag(it)', real(ib)', imag(ib)', 'VariableNames', ...
    {'f_GHz', 's11_re', 's11_im', 's21_re', 's21_im', 'itop_re', 'itop_im', 'ibot_re', 'ibot_im'});
writetable(T, fullfile(out, [name '.csv']));

bw = band_edges(f, s11);
fprintf('%s: |S11| < -10 dB from %.2f to %.2f GHz, max |S11| 2-12 GHz %.1f dB\n', ...
    name, bw(1)/1e9, bw(2)/1e9, max(20*log10(abs(s11(f >= 2e9 & f <= 12e9)))));
end

function bw = band_edges(f, s11)
ok = 20*log10(abs(s11)) < -10;
i0 = find(ok, 1);
i1 = i0 - 1 + find(~ok(i0:end), 1) - 1;
if isempty(i1), i1 = numel(f); end
bw = [f(i0) f(i1)];
end
