import sys,ROOT,random
from array import array
N=int(sys.argv[1]); asv=None if sys.argv[2]=="d" else int(sys.argv[2])
f=ROOT.TFile.Open("/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/a521c516-1aad-4f64-89cb-e3ed26161eec/scratchpad/a1/review/k2.root","RECREATE")
t=ROOT.TTree("data","data")
if asv is not None: t.SetAutoSave(asv)
bs=[array('d',[0]),array('d',[0]),array('b',[0])]
for n,l,b in zip("abc",["D","D","B"],bs): t.Branch(n,b,f"{n}/{l}")
r=random.random
for i in range(N):
    bs[0][0]=r(); bs[1][0]=r(); bs[2][0]=1; t.Fill()
print("pre-write autosave",t.GetAutoSave(),"autoflush",t.GetAutoFlush(),"totbytes",t.GetTotBytes())
t.Write(); f.Close()
f=ROOT.TFile.Open(f.GetName()); print(N,asv,[(k.GetName(),k.GetCycle()) for k in f.GetListOfKeys()])
