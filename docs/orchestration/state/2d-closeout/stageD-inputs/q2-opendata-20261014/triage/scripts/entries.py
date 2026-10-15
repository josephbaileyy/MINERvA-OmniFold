"""Print MasterAnaDev entries and Meta POT_Used for each given file. Usage: python -I entries.py <src>..."""
import sys

import ROOT

for s in sys.argv[1:]:
    f = ROOT.TFile.Open(s)
    t, m = f.Get("MasterAnaDev"), f.Get("Meta")
    p = 0.0
    for i in range(m.GetEntries()):
        m.GetEntry(i)
        p += m.POT_Used
    print(s.split("/")[-1], "remote" if s.startswith("root:") else "local", int(t.GetEntries()), p, flush=True)
    f.Close()
