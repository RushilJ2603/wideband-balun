% Adds a box of RT/duroid 5880. The loss tangent is converted to a
% conductivity at 10 GHz, which is how openEMS models dielectric loss.

function CSX = add_substrate(CSX, p, start, stop)
eps0 = 8.854187817e-12;
kappa = 2*pi*10e9 * eps0 * p.er * p.tand;
CSX = AddMaterial(CSX, 'substrate');
CSX = SetMaterialProperty(CSX, 'substrate', 'Epsilon', p.er, 'Kappa', kappa);
CSX = AddBox(CSX, 'substrate', 0, start, stop);
end
