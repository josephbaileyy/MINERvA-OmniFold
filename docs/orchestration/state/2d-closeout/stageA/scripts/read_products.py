"""Read-only dump of 2D central products for the Stage A checklist (2d-closeout A-2).

Opens every file READ, writes one JSON to the path given as argv[1]. No product is modified.
"""
import hashlib, json, os, sys
import ROOT

P = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding"
PRODUCTS = {
    "E_U": f"{P}/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root",
    "E_U_cfs": "/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/fig_products/2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root",
    "L0": "/global/cfs/cdirs/m3246/josephrb/xr-linux-20261011/outputs/L0/a1/XR-L0.root",
    "L1": "/global/cfs/cdirs/m3246/josephrb/xr-linux-20261011/outputs/L1/a1/XR-L1.root",
    "PN_CV": f"{P}/uq/purity_newomni/2d_xsec_MEFHC_5iter_lgbm_pn_uni_CV.root",
    "SEED1": f"{P}/seedscan_lgbm/2d_xsec_MEFHC_5iter_lgbm_seed1.root",
    "E_C": f"{P}/2d_crossSection_omnifold_MEFHC_5iter.root",
}
FLUX = f"{P}/baseline_flux/runEventLoopMC_MEFHC.root"
OMNI = {
    "E_U_omnifile": f"{P}/runEventLoopOmniFold_MEFHC_universes_full.root",
    "XR_omnifile": "/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root",
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def h1(h):
    return {"name": h.GetName(), "class": h.ClassName(), "nx": h.GetNbinsX(),
            "edges": [h.GetXaxis().GetBinLowEdge(i) for i in range(1, h.GetNbinsX() + 2)],
            "vals": [repr(h.GetBinContent(i)) for i in range(1, h.GetNbinsX() + 1)]}


def h2(h):
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    return {"name": h.GetName(), "class": h.ClassName(), "title": h.GetTitle(), "nx": nx, "ny": ny,
            "xedges": [h.GetXaxis().GetBinLowEdge(i) for i in range(1, nx + 2)],
            "yedges": [h.GetYaxis().GetBinLowEdge(i) for i in range(1, ny + 2)],
            "vals": [[repr(h.GetBinContent(ix, iy)) for iy in range(1, ny + 1)] for ix in range(1, nx + 1)],
            "errs": [[repr(h.GetBinError(ix, iy)) for iy in range(1, ny + 1)] for ix in range(1, nx + 1)],
            "uflow_oflow_sum": repr(sum(h.GetBinContent(ix, iy) for ix in range(0, nx + 2) for iy in range(0, ny + 2)
                                        if ix in (0, nx + 1) or iy in (0, ny + 1)))}


def dump(path, hashit=True, objects=True):
    st = os.stat(path)
    out = {"path": path, "size": st.st_size, "mtime": st.st_mtime,
           "realpath": os.path.realpath(path)}
    if hashit:
        out["sha256"] = sha256(path)
    f = ROOT.TFile.Open(path, "READ")
    keys = []
    for k in f.GetListOfKeys():
        keys.append([k.GetName(), k.GetClassName(), k.GetCycle()])
    out["keys"] = keys
    params, named, hists = {}, {}, {}
    for name, cls, _ in keys:
        if cls.startswith("TParameter"):
            o = f.Get(name)
            params[name] = repr(o.GetVal())
        elif cls == "TNamed":
            o = f.Get(name)
            t = o.GetTitle()
            named[name] = t if len(t) < 20000 else t[:20000] + "...(truncated)"
        elif objects and cls.startswith("TH2"):
            hists[name] = h2(f.Get(name))
        elif objects and cls.startswith("TH1"):
            hists[name] = h1(f.Get(name))
        elif objects and cls.startswith("TVector"):
            o = f.Get(name)
            hists[name] = {"class": cls, "vals": [repr(o[i]) for i in range(o.GetNoElements())]}
    out["params"], out["named"], out["hists"] = params, named, hists
    f.Close()
    return out


res = {"host": os.uname().nodename, "root": ROOT.gROOT.GetVersion(), "products": {}, "omnifiles": {}}
for k, p in PRODUCTS.items():
    try:
        res["products"][k] = dump(p)
    except Exception as e:  # record, never hide
        res["products"][k] = {"path": p, "error": repr(e)}
try:
    res["flux"] = dump(FLUX)
except Exception as e:
    res["flux"] = {"path": FLUX, "error": repr(e)}
for k, p in OMNI.items():
    try:
        res["omnifiles"][k] = dump(p, hashit=False, objects=False)
    except Exception as e:
        res["omnifiles"][k] = {"path": p, "error": repr(e)}
with open(sys.argv[1], "w") as f:
    json.dump(res, f, indent=1)
print("wrote", sys.argv[1])
