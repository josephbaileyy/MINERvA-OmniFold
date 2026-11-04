"""Scratch experiments behind the writer fix: kOverwrite's reach over several cycles, the endings under many
autosaves at fixture size, and whether a test can reach the TTree the bound write_data_file builds."""
import sys
from array import array
from pathlib import Path

import numpy as np
import ROOT

R = Path(sys.argv[1])


def keys(p):
    f = ROOT.TFile.Open(str(p))
    k = [(x.GetName(), x.GetCycle()) for x in f.GetListOfKeys()]
    f.Close()
    return k


# E1: kOverwrite after three plain Writes of the same name
f = ROOT.TFile.Open(str(R / "e1.root"), "RECREATE")
t = ROOT.TTree("data", "data")
b = array("d", [0])
t.Branch("x", b, "x/D")
for i in range(10):
    b[0] = i
    t.Fill()
t.Write()
t.Write()
t.Write()
t.Write("", ROOT.TObject.kOverwrite)
f.Close()
print("E1 three plain Writes then one kOverwrite:", keys(R / "e1.root"))


# E2: at fixture size, an autosave every 200 entries, under each ending
def write(p, autosave_after=None, overwrite=False, n=2345):
    f = ROOT.TFile.Open(str(p), "RECREATE")
    t = ROOT.TTree("data", "data")
    t.SetAutoSave(200)
    if autosave_after is not None:
        t.SetAutoSave(autosave_after)
    b = array("d", [0])
    t.Branch("x", b, "x/D")
    for i in range(n):
        b[0] = i
        t.Fill()
    if overwrite:
        t.Write("", ROOT.TObject.kOverwrite)
    else:
        t.Write()
    f.Close()


for name, kw in (("plain", {}), ("overwrite", dict(overwrite=True)), ("autosave0", dict(autosave_after=0)),
                 ("both", dict(autosave_after=0, overwrite=True))):
    write(R / f"e2_{name}.root", **kw)
    print(f"E2 autosave every 200 entries, {name}:", keys(R / f"e2_{name}.root"))

# E3: can a test reach the TTree the bound function builds? Replace ROOT.TTree with a factory.
sys.path.insert(0, sys.argv[2])
import cov2d_writer as w  # noqa: E402

real = ROOT.TTree


def small(*a):
    t = real(*a)
    t.SetAutoSave(200)
    return t


try:
    ROOT.TTree = small
    print("E3 ROOT.TTree replaced:", ROOT.TTree is small)
    r = np.random.default_rng(1)
    n = 2345
    w.write_data_file(R / "e3.root", {"measured": r.uniform(size=n), "measured_pz": r.uniform(size=n),
                                      "measured_pass": np.ones(n, np.uint8)}, 1.0)
    print("E3 bound write_data_file under the factory:", keys(R / "e3.root"))
finally:
    ROOT.TTree = real
print("E3 restored:", ROOT.TTree is real)
