"""TEST ONLY (not a study output): code-v8 glue on real inputs, login node: gibuu_file on 2 C12 files, gibuu_codes, one playlist's Tune
species, r12_charm (decay + checks), and the decayed lists' E_avail against the undecayed."""
import sys, json, os
from pathlib import Path
import numpy as np
CODE, WORK = Path(sys.argv[1]), Path(sys.argv[2])
WORK.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(CODE))
import mp2_s2_harmonize as H
files = [os.path.join(H.G, f"work_gibuu_arr/task{i}/FinalEvents.dat") for i in (1, 2)]
per = [H.gibuu_file(f)[1] for f in files]
offs, base = [], 0
for p in per:
    offs.append(p["fs_offsets"][:-1] + base); base += int(p["fs_offsets"][-1])
ent = {k: np.concatenate([p[k] for p in per]) for k in ("fs_pdg", "fs_E", "fs_px", "fs_py", "fs_pz")}
ent["fs_offsets"] = np.concatenate(offs + [np.array([base], np.int64)])
gid, gq = H.gibuu_codes(ent["fs_pdg"])
print("SMOKE events", ent["fs_offsets"].size - 1, "charm parents", int(np.isin(gid, list(H.chm.GIBUU_CHARM_IDS)).sum()),
      "codes", sorted({(int(a), int(b)) for a, b in zip(gid, gq) if a in H.chm.GIBUU_CHARM_IDS}))
# r12_charm with the species of ONE playlist (the job uses all twelve)
p0 = H.s1d.PLAYLISTS[0]
s = np.load(f"{sys.argv[3]}/s1_{p0}.npz")
sp = H.tune_species_playlist((sys.argv[3], p0, 0, int(s["n_rows"])))
print("SMOKE tune species (one playlist)", sp.size, "has 130:", 130 in sp, "has 3122:", 3122 in sp)
H.tune_species = lambda s1dir, nproc: {int(v) for v in sp}
new, rec = H.r12_charm(ent, sys.argv[3], 4, WORK)
print("SMOKE branch", rec["branch"], "| checks", {k: v.get("pass", v) if isinstance(v, dict) else v for k, v in rec["checks"].items()})
print("SMOKE mix", rec["parent_mix"], "| products", rec["product_species"])
ea1 = H.s1d.eavail_mat(new["fs_pdg"], new["fs_E"], new["fs_offsets"])
ea0 = H.s1d.eavail_mat(new["fs0_pdg"], new["fs0_E"], new["fs0_offsets"])
d = ea1 - ea0
print("SMOKE eavail shift MeV: n changed", int((d != 0).sum()), "min", float(d.min()), "median(changed)", float(np.median(d[d != 0])) if (d != 0).any() else None, "max", float(d.max()))
