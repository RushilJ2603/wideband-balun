% Substrate and taper data from Vinayagamoorthy, Coetzee and Jayalath,
% "Microstrip to parallel strip balun as spiral antenna feed", IEEE VTC
% 2012 Spring. Lengths in mm.

function p = balun_params()
p.er = 2.2;              % RT/duroid 5880
p.tand = 0.0009;         % Rogers datasheet value at 10 GHz
p.h = 1.5748;
p.t_cu = 0.035;          % 1 oz copper
p.sigma_cu = 5.8e7;
p.w50 = 4.8;

% Table I of the paper: position along the balun, top strip width,
% bottom conductor width, target impedance.
p.table = [
     5.0  4.80  18.00   50
    12.7  2.60  16.00   70
    22.2  1.76   7.00   90
    29.8  1.20   2.00  110
    41.5  1.10   1.80  150
    46.2  0.92   0.98  170
    50.0  0.88   0.88  188
    70.0  0.88   0.88  188 ];

p.L = 70;                % one balun, feed end to balanced end
p.feed = 5;              % 50 ohm section before the taper
p.Z0 = 50;
p.ZL = 188;
end
