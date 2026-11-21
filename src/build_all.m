% Writes every balun model used in the report. Each folder is then run
% with openEMS, and post_all reads the results.

function build_all()
geo = @(n) fullfile('..', 'geometry', [n '.csv']);
build_balun('b2b_paper_B', geo('paper_B'));
build_balun('b2b_paper_B_stated', geo('paper_B_stated'));
build_balun('b2b_paper_A_stated', geo('paper_A_stated'));
build_balun('b2b_paper_B_stated_short', geo('paper_B_stated_short'));
build_balun('single_paper_B_stated', geo('paper_B_stated'), struct('mode', 'single'));
build_balun('single_paper_B_stated_p2', geo('paper_B_stated'), struct('mode', 'single', 'excite', 2));
build_balun('b2b_improved', geo('improved'), struct('dump_f', [2.5e9 10e9]));
build_balun('single_improved', geo('improved'), struct('mode', 'single'));
build_balun('single_improved_p2', geo('improved'), struct('mode', 'single', 'excite', 2));
% Mesh check: the paper design back to back with every cell 1.5 times smaller.
build_balun('b2b_paper_B_stated_fine', geo('paper_B_stated'), struct('refine', 1.5));
end
