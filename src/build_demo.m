% Writes the models for the live demonstration and for the study of the two
% design changes: a coarse copy of each design that runs in about three
% minutes, the taper length and profile changed one at a time, and the
% improved balun with time-domain field recording.

function build_demo()
geo = @(n) fullfile('..', 'geometry', [n '.csv']);
coarse = struct('refine', 0.6, 'ext', 14);
build_balun('live_improved', geo('improved'), coarse);
build_balun('live_paper', geo('paper_B_stated'), coarse);
build_balun('b2b_step_exp60', geo('step_exp60'));
build_balun('single_step_exp60', geo('step_exp60'), struct('mode', 'single'));
build_balun('b2b_step_klop45', geo('step_klop45'));
build_balun('single_step_klop45', geo('step_klop45'), struct('mode', 'single'));
build_balun('movie_improved', geo('improved'), struct('movie', true));
end
