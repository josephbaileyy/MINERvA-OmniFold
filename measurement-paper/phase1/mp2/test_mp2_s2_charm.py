"""TEST ONLY (not a study output): mp2_s2_charm.decay_entries with the real PYTHIA6 library on synthetic GiBUU lists.
argv: CODE WORKDIR. Run on Perlmutter (CVMFS), root_6_28's python, no ROOT import."""
import sys
from pathlib import Path

import numpy as np

CODE, WORK = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(CODE))
import mp2_s2_charm as chm  # noqa: E402

OB = 900_000_000
WORK.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(3)


def code(gid, q):
    return OB + 10 * gid + (q + 2)


# 6 events: 0 none; 1 a Lambda_c+ beside a proton; 2 a D0 and a D+; 3 a Sigma_c++ (-> Lambda_c+ pi+ -> ...); 4 a Xi (53,
# not charm) only; 5 a D_s+ and a Xi_c0 among pions
lists = [[(2212, None), (211, None)], [(2212, None), (code(56, 1), 2.2865)], [(code(114, 0), 1.8648), (code(114, 1), 1.8696)],
         [(code(57, 2), 2.4540)], [(code(53, -1), 1.3217)], [(211, None), (code(118, 1), 1.9683), (code(59, 0), 2.4709), (-211, None)]]
mass = {2212: 0.93827, 211: 0.13957, -211: 0.13957}
pdg, E, px, py, pz, off = [], [], [], [], [], [0]
for ev in lists:
    for c, m in ev:
        p3 = rng.normal(0, 0.6, 3)
        m_ = m if m is not None else mass[c]
        pdg.append(c)
        E.append(1000 * np.sqrt(m_ ** 2 + p3 @ p3))
        px.append(1000 * p3[0]); py.append(1000 * p3[1]); pz.append(1000 * p3[2])
    off.append(len(pdg))
ent = {"fs_pdg": np.array(pdg, np.int64), "fs_E": np.array(E), "fs_px": np.array(px), "fs_py": np.array(py), "fs_pz": np.array(pz),
       "fs_offsets": np.array(off, np.int64), "c": np.ones(len(lists))}
x = ent["fs_pdg"] - OB
um = x >= 0
gid, gq = np.where(um, x // 10, -1), np.where(um, x % 10 - 2, 0)
TUNE = {2212, 2112, -2212, -2112, 211, -211, 111, 22, 321, -321, 130, 11, -11, 12, -12, 13, -13, 14, -14, 16, -16, 311, -311,
        3122, -3122, 3112, 3212, 3222}
new, rec = chm.decay_entries(ent, (gid, gq), TUNE, WORK)
print("TEST pass", rec["pass"], "parents", rec["n_parents"], "events with charm", rec["n_events_with_charm"], "mix", rec["parent_mix"])
print("TEST checks", {k: v.get("pass", v) if isinstance(v, dict) else v for k, v in rec["checks"].items()})
print("TEST p4 worst", rec["checks"]["four_momentum"]["max_rel_residual"], "BR max dev", rec["checks"]["br_sum_per_decayed_species"]["max_abs_dev"],
      "n decayed species", rec["checks"]["br_sum_per_decayed_species"]["n_species"])
print("TEST decayer", rec["decayer"]["table_dump_sha256"][:16], rec["decayer"]["flags"])
assert rec["pass"] and rec["n_parents"] == 6 and rec["n_events_with_charm"] == 4
n0, n1 = np.diff(ent["fs_offsets"]), np.diff(new["fs_offsets"])
assert n1[0] == n0[0] and n1[4] == n0[4], "events without charm must be untouched"
for e in (0, 4):
    a0, b0 = ent["fs_offsets"][e], new["fs_offsets"][e]
    assert np.array_equal(ent["fs_pdg"][a0:a0 + n0[e]], new["fs_pdg"][b0:b0 + n1[e]])
    assert np.array_equal(ent["fs_E"][a0:a0 + n0[e]], new["fs_E"][b0:b0 + n1[e]])
# event 1: the proton stays first, unchanged, and the Lambda_c is replaced in place
b = new["fs_offsets"][1]
assert new["fs_pdg"][b] == 2212 and new["fs_E"][b] == ent["fs_E"][2]
assert not np.any(chm.has_charm(new["fs_pdg"])) and not np.any(np.isin(new["fs_pdg"] - OB, [10 * 56 + 3]))
assert code(53, -1) in new["fs_pdg"], "the Xi (not charm) is kept as it was"
# event 5: the first and last pions keep their places
b5, e5 = new["fs_offsets"][5], new["fs_offsets"][6]
assert new["fs_pdg"][b5] == 211 and new["fs_pdg"][e5 - 1] == -211
for c in ("fs_E", "fs_px", "fs_py", "fs_pz"):
    s0 = np.add.reduceat(ent[c], ent["fs_offsets"][:-1])
    s1 = np.add.reduceat(new[c], new["fs_offsets"][:-1])
    assert np.max(np.abs(s1 - s0) / np.add.reduceat(ent["fs_E"], ent["fs_offsets"][:-1])) < 1e-9, c
assert np.array_equal(new["fs0_pdg"], ent["fs_pdg"]) and np.array_equal(new["fs0_offsets"], ent["fs_offsets"])
print("TEST rebuild: untouched events identical, in-place replacement, event four-momentum kept, fs0 kept")
# determinism: the same seed gives the same products
new2, rec2 = chm.decay_entries(ent, (gid, gq), TUNE, WORK)
assert np.array_equal(new2["fs_pdg"], new["fs_pdg"]) and np.array_equal(new2["fs_E"], new["fs_E"])
print("TEST deterministic (same products on a second call)")
# fallback triggers: an unknown charm code; a Tune species set without K0L
bad = dict(ent, fs_pdg=ent["fs_pdg"].copy())
bad["fs_pdg"][-2] = code(61, 1)              # Omega_c with charge +1: not a hadron in the map
xb = bad["fs_pdg"] - OB
umb = xb >= 0
n3, r3 = chm.decay_entries(bad, (np.where(umb, xb // 10, -1), np.where(umb, xb % 10 - 2, 0)), TUNE, WORK)
print("TEST unknown code -> no decays:", n3 is None, r3["unknown_charm_codes"], r3["checks"])
species = set(int(k) for k in rec["product_species"])
if 130 in species:
    n4, r4 = chm.decay_entries(ent, (gid, gq), TUNE - {130}, WORK)
    print("TEST Tune without K0L -> pass", r4["pass"], "not_in_tune", r4["checks"]["tune_species"]["not_in_tune"])
    assert not r4["pass"]
else:
    print("TEST (no K0L among these products; the species check is exercised with", sorted(species)[:3], ")")
    n4, r4 = chm.decay_entries(ent, (gid, gq), TUNE - {sorted(species)[-1]}, WORK)
    assert not r4["pass"]
print("TEST product species", rec["product_species"])
print("TEST OK")
