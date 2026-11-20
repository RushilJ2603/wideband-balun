% Returns an empty working folder for one simulation. Field dumps can be
% large, so the folders live in the system temp directory.

function d = sim_dir(name)
d = fullfile(tempdir, 'balun_sims', name);
if exist(d, 'dir')
    rmdir(d, 's');
end
mkdir(d);
end
