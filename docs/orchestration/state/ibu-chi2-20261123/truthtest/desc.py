import numpy as np
d = np.load("vectors.npz"); m, s, mod, mask = d["m"], d["sig"], d["mod"], d["mask"]
PT = [0,0.07,0.15,0.25,0.33,0.40,0.47,0.55,0.70,0.85,1.00,1.25,1.50,2.50,4.50]
PZ = [1.5,2,2.5,3,3.5,4,4.5,5,6,7,8,9,10,15,20,40,60]
rel = np.where(mask, 100*(mod/m - 1), np.nan).reshape(14,16)
print("100*(shipped/ours-1), rows pT bins, cols p|| bins")
print("pT\\p||  " + " ".join(f"{PZ[j]:>5}" for j in range(16)))
for i in range(14):
    print(f"{PT[i]:4.2f}-{PT[i+1]:<4.2f}" + " ".join("    ." if np.isnan(v) else f"{v:5.1f}" for v in rel[i]))
# theta edge: cells whose corner pt_hi/pz_lo > tan20 but reported
t20 = np.tan(np.radians(20))
edge = np.array([[ (PT[i+1]/PZ[j] > t20) for j in range(16)] for i in range(14)]).ravel() & mask
inner = mask & ~edge
r = (mod/m-1)
print("edge cells (theta=20 deg crosses the cell):", edge.sum(), " median rel %.2f%%  mean %.2f%%" % (100*np.median(r[edge]), 100*np.mean(r[edge])))
print("interior cells:", inner.sum(), " median rel %.2f%%  mean %.2f%%  rms %.2f%%" % (100*np.median(r[inner]), 100*np.mean(r[inner]), 100*np.sqrt(np.mean(r[inner]**2))))
print("interior pull (MC stat) rms %.2f; edge pull rms %.2f" % (np.sqrt(np.mean(((mod-m)/s)[inner]**2)), np.sqrt(np.mean(((mod-m)/s)[edge]**2))))
