% Mesh lines along one axis.
%
%   lines = mesh_axis(fixed, regions, rmax, ratio)
%
% fixed    lines that must appear in the mesh; the first and last set the
%          extent of the axis
% regions  rows [a b r]: cells no larger than r between a and b
% rmax     largest cell anywhere
% ratio    largest growth from one cell to the next
%
% The allowed cell size at a point is the smallest of rmax and, for each
% region, r plus (ratio - 1) times the distance to the region. Each gap
% between fixed lines is filled with cells that follow that size.

function lines = mesh_axis(fixed, regions, rmax, ratio)
fixed = unique(fixed(:)');
res = @(x) local_res(x, regions, rmax, ratio);

% Fixed lines closer than half the local cell size are merged.
keep = fixed(1);
for v = fixed(2:end)
    if v - keep(end) > 0.5 * min(res(v), res(keep(end)))
        keep(end+1) = v; %#ok<AGROW>
    end
end
keep(end) = fixed(end);

lines = keep(1);
for k = 1:numel(keep) - 1
    p = keep(k); q = keep(k+1);
    xs = linspace(p, q, 4001);
    cum = cumtrapz(xs, 1 ./ res(xs));
    n = max(1, ceil(cum(end) - 0.1));
    seg = interp1(cum, xs, linspace(0, cum(end), n + 1));
    lines = [lines seg(2:end)]; %#ok<AGROW>
end
end

function r = local_res(x, regions, rmax, ratio)
r = rmax * ones(size(x));
for i = 1:size(regions, 1)
    d = max(0, max(regions(i, 1) - x, x - regions(i, 2)));
    r = min(r, regions(i, 3) + (ratio - 1) * d);
end
end
