#!/usr/bin/env python3
"""Write the corrected ME-FHC data flux as a ROOT TH1D that NuWro samples correctly.

NuWro's EnergyProfile::readHistRoot treats bin CONTENTS as bin probabilities and
samples uniformly within a bin, so contents are density x width (GeV). The ROOT
file is written by a generated C++ macro because this machine has no PyROOT.
"""
import subprocess
import sys
from pathlib import Path

import numpy as np

npz, out_root = Path(sys.argv[1]), Path(sys.argv[2])
d = np.load(npz)
edges = d["edges"]
contents = d["phi_t_density"] * np.diff(edges)
macro = out_root.with_suffix(".C")
macro.write_text(
    "void %s(){\n" % macro.stem
    + "  double e[%d] = {%s};\n" % (edges.size, ",".join(repr(float(x)) for x in edges))
    + "  double c[%d] = {%s};\n" % (contents.size, ",".join(repr(float(x)) for x in contents))
    + '  TFile f("%s","RECREATE");\n' % out_root
    + '  TH1D h("flux_mefhc_phi_t","phi_t density x width;E_{#nu} (GeV);m^{-2}/POT per bin",%d,e);\n' % contents.size
    + "  for(int i=0;i<%d;i++) h.SetBinContent(i+1,c[i]);\n" % contents.size
    + "  h.Write(); f.Close();\n"
    + '  printf("integral %.9e nbins %d\\n", h.Integral(), h.GetNbinsX());\n}\n')
subprocess.run(["root", "-l", "-b", "-q", str(macro)], check=True)
print("expected integral (Phi_t) %.9e" % float(d["Phi_t"]))
