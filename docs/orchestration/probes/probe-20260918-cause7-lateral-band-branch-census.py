import uproot, re
F="/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/runEventLoopOmniFold_5D_1A_universes_full_bkgaware.root"
NINE=["BeamAngleX","BeamAngleY","MuonResolution","Muon_Energy_MINERvA","Muon_Energy_MINOS",
      "MinosEfficiency","GEANT_Neutron","GEANT_Pion","GEANT_Proton"]
FIVE=set(NINE[:5])
f=uproot.open(F)
t=f["mc_signal_reco"]
br=set(t.keys())
print("file  :", F.split("/")[-1])
print("tree  : mc_signal_reco   n_branches =", len(br))
print()
print("For each band: do WEIGHT branches exist, and do KINEMATIC (lateral) branches exist?")
print("%-22s %-8s %-10s %-34s %s" % ("band","idx","weights","kinematic pt/pz/q3/W","VERDICT"))
rows=[]
for b in NINE:
    for i in (0,1):
        s=f"{b}_{i}"
        w=[f"w_truth_{s}", f"w_reco_{s}"]
        kin=[f"MC_{s}", f"MC_pz_{s}", f"sim_{s}", f"sim_pz_{s}"]
        axk=[f"MC_q3_{s}", f"sim_q3_{s}", f"MC_W_{s}", f"sim_W_{s}"]
        nw=sum(x in br for x in w); nk=sum(x in br for x in kin); na=sum(x in br for x in axk)
        v = "LATERAL (shifts kinematics)" if nk>0 else ("WEIGHT-ONLY" if nw>0 else "ABSENT")
        rows.append((b,i,nw,nk,na,v))
        print("%-22s %-8d %-10s %-34s %s" % (b, i, f"{nw}/2", f"kin {nk}/4  q3+W {na}/4", v))
print()
lat={b for b,i,nw,nk,na,v in rows if nk>0}
wo ={b for b,i,nw,nk,na,v in rows if nk==0 and nw>0}
print("MEASURED lateral set     :", sorted(lat))
print("MEASURED weight-only set :", sorted(wo))
print("p4_lib.BANDS (the five)  :", sorted(FIVE))
print()
print("lateral set == the five  :", lat==FIVE)
print("the four excluded are all weight-only:", set(NINE[5:]) <= wo)
import uproot, os, re
D="/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding"
NINE=["BeamAngleX","BeamAngleY","MuonResolution","Muon_Energy_MINERvA","Muon_Energy_MINOS",
      "MinosEfficiency","GEANT_Neutron","GEANT_Pion","GEANT_Proton"]
FIVE=set(NINE[:5])
A=D+"/active_universe_5d/standard/candidate/std_final5_candidate.root"
S=D+"/uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root"
for lab,p in (("ACTIVE candidate",A),("SUPPORT combined",S)):
    if not os.path.exists(p): print("%-18s MISSING"%lab); continue
    f=uproot.open(p); ks=[k.split(";")[0] for k in f.keys()]
    cov=[k for k in ks if k.startswith("hCov_")]
    bands=sorted({re.sub(r'^hCov_[a-z0-9]+5d_','',k) for k in cov})
    print("=== %s  (%.1f GB, %d keys, %d hCov_*) ===" % (lab, os.path.getsize(p)/1e9, len(ks), len(cov)))
    print("   prefixes:", sorted({k.split('5d_')[0]+'5d_' for k in cov}))
    print("   n band names:", len(bands))
    lat=[b for b in bands if b in FIVE]; other=[b for b in bands if b not in FIVE]
    print("   LATERAL bands present (of the five): %d -> %s" % (len(lat), sorted(lat)))
    print("   the four weight-only present       : %s" % sorted(b for b in bands if b in set(NINE[5:])))
    print("   first 12 other band names          : %s" % other[:12])
    print()
print("=== the ten endpoint products: are all ten complete? ===")
base=D+"/active_universe_5d/standard"
for b in NINE[:5]:
    for i in (0,1):
        d=f"{base}/{b}_{i}"
        if not os.path.isdir(d): print("   %-24s MISSING DIR"%f"{b}_{i}"); continue
        roots=[x for x in os.listdir(d) if x.endswith(".root")]
        tot=sum(os.path.getsize(os.path.join(d,x)) for x in roots)
        print("   %-24s %2d root files  %7.1f GB" % (f"{b}_{i}", len(roots), tot/1e9))
