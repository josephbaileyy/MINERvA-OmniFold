"""Read-only reproduction of CONTROL-2A's extra cycles: the bound write_data_file (blob 2402ed4b, at M) on
4,119,797 synthetic rows with $CV's dtypes, then keys and cycles. Variants are scratch copies, not the blob."""
import subprocess, sys, time
from pathlib import Path
import numpy as np
S, M, N = sys.argv[1], sys.argv[2], 4119797
blob = subprocess.run(["git", "-C", f"{S}/wt", "rev-parse", f"{M}:2d-unfolding/cov2d/cov2d_writer.py"], capture_output=True, text=True).stdout.strip()
print("cov2d_writer blob at M:", blob)
sys.path.insert(0, f"{S}/wt/2d-unfolding/cov2d")
import cov2d_writer as w
assert subprocess.run(["git", "-C", f"{S}/wt", "hash-object", w.__file__], capture_output=True, text=True).stdout.strip() == blob
import ROOT
r = np.random.default_rng(5)
cols = {"measured": r.uniform(0, 3, N), "measured_pz": r.uniform(1, 30, N), "measured_pass": (r.uniform(size=N) < .8).astype(np.uint8)}
out = Path(sys.argv[3])

def keys(path):
    f = ROOT.TFile.Open(str(path))
    ks = [(k.GetName(), k.GetCycle(), k.GetClassName(), k.GetNbytes()) for k in f.GetListOfKeys()]
    t = f.Get("data")
    info = (t.GetEntries(), t.GetAutoSave(), t.GetAutoFlush(), t.GetZipBytes())
    f.Close()
    return ks, info

t0 = time.time()
w.write_data_file(out / "bound.root", cols, 1.057394261158926e21)
print(f"bound write: {time.time()-t0:.0f}s")
ks, info = keys(out / "bound.root")
print("bound keys:", ks)
print("bound tree: entries, fAutoSave, fAutoFlush, zipbytes =", info)

# scratch variants of the same loop, to separate the causes
def variant(path, autosave=None, overwrite=False):
    from array import array
    f = ROOT.TFile.Open(str(path), "RECREATE"); t = ROOT.TTree("data", "data")
    if autosave is not None:
        t.SetAutoSave(autosave)
    b = {k: array(c, [0]) for k, (c, _) in w.LEAVES.items()}
    for k, (c, leaf) in w.LEAVES.items():
        t.Branch(k, b[k], f"{k}/{leaf}")
    m, mz, mp = cols["measured"], cols["measured_pz"], cols["measured_pass"]
    for i in range(N):
        b["measured"][0], b["measured_pz"][0], b["measured_pass"][0] = float(m[i]), float(mz[i]), int(mp[i])
        t.Fill()
    t.Write("", ROOT.TObject.kOverwrite) if overwrite else t.Write()
    ROOT.TParameter("double")("dataPOTUsed", 1.0).Write(); f.Close()
for name, kw in (("autosave0", dict(autosave=0)), ("overwrite", dict(overwrite=True)), ("both", dict(autosave=0, overwrite=True))):
    variant(out / f"{name}.root", **kw)
    print(f"{name} keys:", keys(out / f"{name}.root")[0])
