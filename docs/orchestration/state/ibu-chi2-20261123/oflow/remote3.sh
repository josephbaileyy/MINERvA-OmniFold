eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook 2>/dev/null)"; set +u; conda activate $HOME/.conda/envs/root_6_28
W=/pscratch/sd/j/josephrb/oflow-split-20261123
L=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/runEventLoopOmniFold_5D_MEFHC_universes_full_bkgaware.root
export OMP_NUM_THREADS=1
python3 - "$W/cv.root" "$L" > $W/split.json 2> $W/split.err <<'PY'
import sys, json, numpy as np, ROOT
base = ["sim_background", "sim_background_pz", "sim_background_pass", "w_bkg"]
lab = ["bkg_nuPDG", "bkg_current", "bkg_vtx_x", "bkg_vtx_y", "bkg_vtx_z"]
cv = ROOT.RDataFrame("mc_background", sys.argv[1]).AsNumpy(base)
a = ROOT.RDataFrame("mc_background", sys.argv[2]).AsNumpy(base + lab)
same = all(np.array_equal(cv[k], a[k], equal_nan=True) if cv[k].dtype.kind == "f" else np.array_equal(cv[k], a[k]) for k in base)
f = ROOT.TFile.Open(sys.argv[1]); s = f.Get("dataPOTUsed").GetVal() / f.Get("mcPOTUsed").GetVal()
pt, pz, w = cv["sim_background"].astype(float), cv["sim_background_pz"].astype(float), cv["w_bkg"].astype(float)
ok = (cv["sim_background_pass"] != 0) & np.isfinite(pt) & np.isfinite(pz) & np.isfinite(w) & (w >= 0) & (w < 1e6)
x, y, z = a["bkg_vtx_x"].astype(float), a["bkg_vtx_y"].astype(float), a["bkg_vtx_z"].astype(float)
ap = 850.0; side = ap * 2 / np.sqrt(3)
fid = (np.abs(x) <= ap) & ((np.abs(y) < side / 2) | (np.abs(y) < side - np.abs(x) * (side / 2) / ap)) & (z >= 5980) & (z <= 8422)
cc = (a["bkg_nuPDG"] == 14) & (a["bkg_current"] == 1)
PT = np.array([0,0.07,0.15,0.25,0.33,0.40,0.47,0.55,0.70,0.85,1.00,1.25,1.50,2.50,4.50]); PZ = np.array([1.5,2,2.5,3,3.5,4,4.5,5,6,7,8,9,10,15,20,40,60])
ip = np.searchsorted(PT, pt, side="right") - 1; iz = np.searchsorted(PZ, pz, side="right") - 1
g = np.where((ip >= 0) & (ip < 14) & (iz >= 0) & (iz < 16), ip * 16 + iz, -1)
out = {"C_SAME": bool(same), "n_cv": int(len(pt)), "n_lab": int(len(a["w_bkg"])), "pot_scale": s}
for name, sel in [("FAKE_PS", cc & fid), ("FAKE_VTX", cc & ~fid), ("OTHER", ~cc)]:
    m = ok & sel & (g >= 0)
    out[name] = np.bincount(g[m], weights=w[m] * s, minlength=224).tolist(); out[name + "_n"] = int(m.sum())
print(json.dumps(out))
PY
echo "python rc=$?"; tail -3 $W/split.err; sha256sum $W/split.json; cat $W/split.json
