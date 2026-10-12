"""Read-only dump of the 2D universe sweeps (July purity_newomni and negweight_uni, May
universe_sweep_fluxfix) for 2d-closeout Stage B (KI-92, KI-93).

Opens every product READ. Writes argv[1].npz (histogram contents incl. flow, and errors) and
argv[1].json (sha256, size, mtime, realpath, parameters, TNamed strings, key list).
"""
import glob, hashlib, json, os, sys
import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)
P = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/uq"
SETS = {
    "pn": (f"{P}/purity_newomni", "2d_xsec_MEFHC_5iter_lgbm_pn_uni_"),
    "nw": (f"{P}/negweight_uni", "2d_xsec_MEFHC_5iter_lgbm_nw_uni_"),
    "may": (f"{P}/universe_sweep_fluxfix", "2d_xsec_MEFHC_5iter_lgbm_uni_full_"),
}
EXTRA = {"ref/E_U": f"{P}/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def contents(h):
    if h.InheritsFrom("TH2"):
        nx, ny = h.GetNbinsX(), h.GetNbinsY()
        v = np.array([[h.GetBinContent(i, j) for j in range(ny + 2)] for i in range(nx + 2)])
        e = np.array([[h.GetBinError(i, j) for j in range(ny + 2)] for i in range(nx + 2)])
    else:
        nx = h.GetNbinsX()
        v = np.array([h.GetBinContent(i) for i in range(nx + 2)])
        e = np.array([h.GetBinError(i) for i in range(nx + 2)])
    return v, e


arrays, meta = {}, {}
files = dict(EXTRA)
for s, (d, pre) in SETS.items():
    for p in sorted(glob.glob(f"{d}/{pre}*.root")):
        files[f"{s}/{os.path.basename(p)[len(pre):-5]}"] = p
for tag, p in files.items():
    st = os.stat(p)
    rp = os.path.realpath(p)
    m = {"path": p, "realpath": rp, "size": st.st_size, "mtime": os.stat(rp).st_mtime,
         "sha256": sha256(rp), "params": {}, "named": {}, "keys": []}
    f = ROOT.TFile.Open(p, "READ")
    for k in f.GetListOfKeys():
        c = k.GetClassName()
        m["keys"].append([k.GetName(), c])
        o = k.ReadObj()
        if c.startswith("TParameter"):
            m["params"][k.GetName()] = repr(o.GetVal())
        elif c == "TNamed":
            m["named"][k.GetName()] = o.GetTitle()
        elif c.startswith("TH"):
            v, e = contents(o)
            arrays[f"{tag}|{k.GetName()}"] = v
            arrays[f"{tag}|{k.GetName()}|err"] = e
    f.Close()
    meta[tag] = m
np.savez_compressed(sys.argv[1] + ".npz", **arrays)
json.dump(meta, open(sys.argv[1] + ".json", "w"), indent=1, sort_keys=True)
print(len(files), "files;", len(arrays), "arrays")
