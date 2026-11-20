% Reads every finished balun run listed in build_all.

function post_all()
names = {'b2b_paper_B', 'b2b_paper_A', 'b2b_paper_B_smooth', 'b2b_paper_B_short', ...
    'b2b_improved', 'single_paper_B', 'single_improved'};
for k = 1:numel(names)
    if exist(fullfile(tempdir, 'balun_sims', names{k}, 'port_ut_1'), 'file') || ...
            ~isempty(dir(fullfile(tempdir, 'balun_sims', names{k}, 'port_ut*')))
        post_balun(names{k});
    else
        fprintf('%s: no results yet\n', names{k});
    end
end
end
