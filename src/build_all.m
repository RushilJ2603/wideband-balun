% Writes every balun model used in the report. Each folder is then run
% with openEMS, and post_all reads the results.

function build_all()
geo = @(n) fullfile('..', 'geometry', [n '.csv']);
build_balun('b2b_paper_B', geo('paper_B'));
build_balun('b2b_paper_A', geo('paper_A'));
build_balun('b2b_paper_B_smooth', geo('paper_B_smooth'));
build_balun('b2b_paper_B_short', geo('paper_B_short'));
build_balun('b2b_improved', geo('improved'), struct('dump_f', [2.5e9 10e9]));
build_balun('single_paper_B', geo('paper_B'), struct('mode', 'single'));
build_balun('single_improved', geo('improved'), struct('mode', 'single'));
end
