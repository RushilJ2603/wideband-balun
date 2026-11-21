% Writes the spiral antenna models used in the report: the spiral alone with
% a 188 ohm feed, and the spiral with each balun standing under it, fed at
% the balun edge. Each folder is then run with openEMS; post_spiral reads
% the port and nf2ff.exe the far field.

function build_antennas()
geo = @(n) fullfile('..', 'geometry', [n '.csv']);
full = struct('fine', true, 'port', 'lumped', 'air', 40, 'balun_board', 18);
build_spiral('spiral_lumped', geo('paper_B_stated'), struct('feed', 'lumped'));
build_spiral('spiral_full', geo('paper_B_stated'), full);
build_spiral('spiral_full_improved', geo('improved'), full);
end
