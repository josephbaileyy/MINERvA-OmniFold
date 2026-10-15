"""Print the Meta tree (1 entry) and the Truth/MasterAnaDev tree titles of a file. Usage: python -I read_meta_tree.py <url>"""
import sys
import ROOT
f = ROOT.TFile.Open(sys.argv[1])
t = f.Get("Meta")
t.GetEntry(0)
for b in t.GetListOfBranches():
    lf = b.GetLeaf(b.GetName()) or b.GetListOfLeaves().At(0)
    vals = [lf.GetValue(i) for i in range(min(lf.GetLen(), 10))] if lf.GetTypeName() not in ("Char_t",) else lf.GetValuePointer()
    print("Meta", b.GetName(), b.GetTitle(), lf.GetTypeName(), vals)
for n in ("MasterAnaDev", "Truth"):
    print(n, "title:", repr(f.Get(n).GetTitle()))
