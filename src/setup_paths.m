% Adds the openEMS MATLAB interface to the path. openEMS is expected in
% C:\openEMS, or at the location given by the OPENEMS_DIR environment
% variable.

function setup_paths()
root = getenv('OPENEMS_DIR');
if isempty(root)
    root = 'C:\openEMS';
end
addpath(fullfile(root, 'matlab'));
addpath(fullfile(root, 'CTB'));
end
