set -u
SRC=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC.root
PIN=43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df
W=/pscratch/sd/j/josephrb/oflow-split-20261123
mkdir -p $W && [ ! -e $W/cv.root ] || { echo "REFUSED: $W/cv.root exists"; exit 2; }
a0=$(stat -c '%X' $SRC)
python3 - "$SRC" "$W/cv.root" <<'PY'
import hashlib, os, sys
fd = os.open(sys.argv[1], os.O_RDONLY | os.O_NOATIME); h = hashlib.sha256()
with open(sys.argv[2], "wb") as out:
    while True:
        b = os.read(fd, 1 << 24)
        if not b: break
        h.update(b); out.write(b)
os.close(fd); print("src_sha", h.hexdigest())
PY
a1=$(stat -c '%X' $SRC); echo "src atime pre $a0 post $a1"
csha=$(sha256sum $W/cv.root | cut -c1-64); echo "copy_sha $csha"
[ "$csha" = "$PIN" ] || { echo "STOP: copy digest differs from pin"; exit 3; }
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook 2>/dev/null)"
conda activate $HOME/.conda/envs/root_6_28
export OMP_NUM_THREADS=1
/usr/bin/time -v python3 - "$W/cv.root" > $W/split.json 2> $W/split.err <<'PY'
import sys, json, numpy as np, ROOT
f = ROOT.TFile.Open(sys.argv[1]); s = f.Get("dataPOTUsed").GetVal() / f.Get("mcPOTUsed").GetVal()
cols = ["sim_background", "sim_background_pz", "sim_background_pass", "w_bkg", "bkg_nuPDG", "bkg_current", "bkg_vtx_x", "bkg_vtx_y", "bkg_vtx_z"]
a = ROOT.RDataFrame("mc_background", sys.argv[1]).AsNumpy(cols)
pt, pz, ok, w = a["sim_background"].astype(float), a["sim_background_pz"].astype(float), a["sim_background_pass"] != 0, a["w_bkg"].astype(float)
ok &= np.isfinite(pt) & np.isfinite(pz) & np.isfinite(w) & (w >= 0) & (w < 1e6)
x, y, z = a["bkg_vtx_x"].astype(float), a["bkg_vtx_y"].astype(float), a["bkg_vtx_z"].astype(float)
ap = 850.0; side = ap * 2 / np.sqrt(3)
hexok = (np.abs(x) <= ap) & ((np.abs(y) < side / 2) | (np.abs(y) < side - np.abs(x) * (side / 2) / ap))
fid = hexok & (z >= 5980) & (z <= 8422)
cc = (a["bkg_nuPDG"] == 14) & (a["bkg_current"] == 1)
PT = np.array([0,0.07,0.15,0.25,0.33,0.40,0.47,0.55,0.70,0.85,1.00,1.25,1.50,2.50,4.50]); PZ = np.array([1.5,2,2.5,3,3.5,4,4.5,5,6,7,8,9,10,15,20,40,60])
ip = np.searchsorted(PT, pt, side="right") - 1; iz = np.searchsorted(PZ, pz, side="right") - 1
g = np.where((ip >= 0) & (ip < 14) & (iz >= 0) & (iz < 16), ip * 16 + iz, -1)
out = {"pot_scale": s, "n_events": int(ok.sum())}
for name, sel in [("FAKE_PS", cc & fid), ("FAKE_VTX", cc & ~fid), ("OTHER", ~cc)]:
    m = ok & sel & (g >= 0)
    out[name] = np.bincount(g[m], weights=w[m] * s, minlength=224).tolist(); out[name + "_n"] = int(m.sum())
print(json.dumps(out))
PY
echo "python rc=$?"; grep -E 'Maximum resident|Elapsed' $W/split.err; sha256sum $W/split.json
