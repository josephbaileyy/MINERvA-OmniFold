#!/usr/bin/env python3
"""Generator-agnostic truth-event reader.

Each reader yields per-event dicts in a common schema so the downstream
analyzer (genie_to_xsec3d.py) is generator-independent:

    {
      "cc":  bool,                       # charged-current?
      "nu":  (E, px, py, pz),            # incoming neutrino 4-momentum (GeV)
      "lep": (E, px, py, pz),            # final-state primary lepton (GeV)
      "fs":  [(pdg, E, px, py, pz), ...] # final-state particles (GeV)
    }

`read_gst` implements this for the GENIE flat 'gst' tree (from
`gntpc -f gst`). To add NuWro / NEUT / GiBUU, write a `read_<gen>` that emits
the same schema -- nothing else changes.

Run in the analysis env (root_6_28).
"""
import ROOT


def read_gst(path, tree_name="gst"):
    """Yield events from a GENIE gst file. Neutrino travels along +z (gevgen
    flux convention), so the analyzer's (pT, p_||) are already in the
    neutrino-beam frame -- no tilt rotation needed."""
    ROOT.gErrorIgnoreLevel = ROOT.kError
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise RuntimeError(f"cannot open gst file {path}")
    t = f.Get(tree_name)
    if not t:
        raise RuntimeError(f"tree '{tree_name}' not in {path}")
    n = t.GetEntries()
    for i in range(n):
        t.GetEntry(i)
        nf = int(t.nf)
        fs = [(int(t.pdgf[j]), float(t.Ef[j]),
               float(t.pxf[j]), float(t.pyf[j]), float(t.pzf[j]))
              for j in range(nf)]
        yield {
            "cc": bool(t.cc),
            "nu": (float(t.Ev), float(t.pxv), float(t.pyv), float(t.pzv)),
            "lep": (float(t.El), float(t.pxl), float(t.pyl), float(t.pzl)),
            "fs": fs,
        }
    f.Close()


# Map of available readers (generator name -> function), for the analyzer CLI.
READERS = {"genie": read_gst}
