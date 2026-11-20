% Reads a finished spiral run. Writes the input reflection to
% results/<name>.csv, the pattern cuts to results/<name>_patterns.csv and
% the half-power beamwidths to results/<name>_hpbw.csv.
%
% The E-plane is taken as the xz-plane (phi = 0), which contains the
% balanced feed, and the H-plane as the yz-plane (phi = 90).

function post_spiral(name)
setup_paths();
sim = fullfile(tempdir, 'balun_sims', name);
S = load(fullfile(sim, 'ports.mat'));
port = S.port;
nf2ff = S.nf2ff;

f = linspace(1e9, 16e9, 301);
port = calcPort(port, sim, f, 'RefImpedance', 50);
s11 = port.uf.ref ./ port.uf.inc;

out = fullfile(fileparts(mfilename('fullpath')), '..', 'results');
writetable(table(f'/1e9, real(s11)', imag(s11)', 'VariableNames', {'f_GHz', 's11_re', 's11_im'}), ...
    fullfile(out, [name '.csv']));

fp = S.meta.opts.nf2ff_f;
theta = (-180:1:180) * pi/180;
rows = [];
hp = zeros(numel(fp), 3);
for k = 1:numel(fp)
    cut = cell(1, 2);
    for m = 1:2
        ph = (m - 1) * pi/2;
        r = CalcNF2FF(nf2ff, sim, fp(k), theta, ph, 'Mode', 0, 'Outfile', sprintf('ff_%d_%d.h5', k, m));
        e = r.E_norm{1}(:) / max(r.E_norm{1}(:));
        cut{m} = 20*log10(e);
        rows = [rows; repmat(fp(k)/1e9, numel(theta), 1) repmat(ph*180/pi, numel(theta), 1) ...
            theta(:)*180/pi cut{m} r.Dmax(1)*ones(numel(theta), 1)]; %#ok<AGROW>
    end
    hp(k, :) = [fp(k)/1e9 beamwidth(theta*180/pi, cut{1}) beamwidth(theta*180/pi, cut{2})];
end
writetable(array2table(rows, 'VariableNames', {'f_GHz', 'phi_deg', 'theta_deg', 'E_dB', 'Dmax'}), ...
    fullfile(out, [name '_patterns.csv']));
writetable(array2table(hp, 'VariableNames', {'f_GHz', 'hpbw_E_deg', 'hpbw_H_deg'}), ...
    fullfile(out, [name '_hpbw.csv']));
disp(array2table(hp, 'VariableNames', {'f_GHz', 'hpbw_E_deg', 'hpbw_H_deg'}));
end

% Width of the -3 dB beam around the stronger of the two broadside
% directions, theta = 0 (above the spiral) or theta = 180 (below it).
function bw = beamwidth(th, g)
[~, i0] = min(abs(th));
[~, i1] = min(abs(abs(th) - 180));
if g(i1) > g(i0)
    th = mod(th, 360) - 180;
    [th, k] = sort(th);
    g = g(k);
    [~, i0] = min(abs(th));
end
ref = g(i0) - 3;
iL = find(g(1:i0) < ref, 1, 'last');
iR = i0 - 1 + find(g(i0:end) < ref, 1);
if isempty(iL) || isempty(iR)
    bw = NaN;
    return;
end
tL = interp1(g(iL:iL+1), th(iL:iL+1), ref);
tR = interp1(g(iR-1:iR), th(iR-1:iR), ref);
bw = tR - tL;
end
