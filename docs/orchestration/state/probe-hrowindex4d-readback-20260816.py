#!/usr/bin/env python3
"""hRowIndex4D READBACK -- closes gaps_remaining[0] of 20260810T0630Z-cross-object-verdict.json.

Predeclared: docs/orchestration/PREDECLARATION-20260816-hrowindex4d-readback.md (319f1e4), BEFORE this ran.

READ-ONLY, and made falsifiable rather than asserted: the 4D product is sha256'd before and after and
equality is required. TFiles opened READ only. The 39.4 GiB C5 is NOT OPENED -- its digest is carried
forward from the receipt, and this script says so rather than implying it was checked.

No p4_lib, no build_projection_M, no AXIS_EDGES values: the index set needs the grid SHAPE and the two
central supports only, so this leg is not exposed to the edge-array question.
"""
import hashlib
import json
import sys

import numpy as np
import ROOT

ROOT.gErrorIgnoreLevel = ROOT.kFatal

BASE = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding"
PROJ = f"{BASE}/active_universe_5d/standard/candidate/std_proj4d_candidate.root"
PROJMAN = f"{BASE}/active_universe_5d/standard/candidate/std_proj4d_candidate_projmanifest.json"
CEN5 = (f"{BASE}/products/5d/xsec_5d_MEFHC_5iter_lgbm.root", "hXSecND_flat")
CEN4 = (f"{BASE}/products/4d/xsec_4d_MEFHC_5iter_lgbm.root", "hXSecND_flat")

NB5 = (14, 16, 7, 7, 6)          # grid_nbins 65856; cardinality independently confirmed by the Aug-10 audit
NB4 = (14, 16, 7, 7)             # 10976
W_AXIS_LAST_SIZE = NB5[-1]       # W is the last axis in C order, so i4 = i5 // 6
EXPECTED_N = 4825
EXPECTED_UNREACHABLE = [9679, 9686, 9714, 9721, 10169]

out = {"check": "hRowIndex4D readback vs an independently derived effective-4D index set",
       "predeclaration": "PREDECLARATION-20260816-hrowindex4d-readback.md (319f1e4)",
       "closes": "gaps_remaining[0] of 20260810T0630Z-cross-object-verdict.json",
       "results": {}, "failures": [], "notes": {}}
R = out["results"]


def fail(tag, detail):
    out["failures"].append({tag: detail})
    print(f"  [FAIL] {tag}: {detail}")


def ok(tag, detail=""):
    print(f"  [PASS] {tag}{(' -- ' + detail) if detail else ''}")


def file_sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


def open_read(p):
    f = ROOT.TFile.Open(p, "READ")
    if not f or f.IsZombie():
        raise SystemExit(f"cannot open {p}")
    if f.TestBit(ROOT.TFile.kRecovered):
        raise SystemExit(f"{p} is marked kRecovered")
    return f


def th1_flat(path, key):
    f = open_read(path)
    h = f.Get(key)
    if not h:
        raise SystemExit(f"missing {path}:{key}")
    n = int(h.GetNbinsX())
    a = np.array([h.GetBinContent(i + 1) for i in range(n)], dtype=np.float64)
    f.Close()
    return a


print("=" * 78)
print("STEP 1  digest the 4D product BEFORE (read-only made falsifiable, not asserted)")
sha_before = file_sha(PROJ)
print(f"  before = {sha_before}")
R["proj4d_sha256_before"] = sha_before

print("STEP 2  read hRowIndex4D OUT OF THE CLOSED FILE")
f = open_read(PROJ)
hidx = f.Get("hRowIndex4D")
if not hidx:
    raise SystemExit("hRowIndex4D absent from the product")
nbins = int(hidx.GetNbinsX())
raw = np.array([hidx.GetBinContent(i + 1) for i in range(nbins)], dtype=np.float64)
hcov = f.Get("hCov_std_proj4d_candidate")
cov_nx = int(hcov.GetNbinsX()) if hcov else -1
cov_ny = int(hcov.GetNbinsY()) if hcov else -1
f.Close()
print(f"  TH1D bins = {nbins}   TH2D = {cov_nx} x {cov_ny}")
R["hRowIndex4D_nbins"] = nbins
R["cov_shape"] = [cov_nx, cov_ny]

print("STEP 3  G5: the read-back vector is a well-formed index vector")
integral = np.all(raw == np.floor(raw))
idx = raw.astype(np.int64)
if not integral:
    fail("G5-integral", "non-integral bin contents")
else:
    ok("G5-integral")
if idx.min() < 0 or idx.max() >= int(np.prod(NB4)):
    fail("G5-range", f"min={idx.min()} max={idx.max()} vs 4D grid {int(np.prod(NB4))}")
else:
    ok("G5-range", f"min={idx.min()} max={idx.max()} < {int(np.prod(NB4))}")
if not np.all(np.diff(idx) > 0):
    fail("G5-monotonic", "not strictly increasing")
else:
    ok("G5-monotonic")

print("STEP 4  G2: assert length 4825 rather than assuming it")
if nbins != EXPECTED_N:
    fail("G2-length", f"TH1D bins {nbins} != {EXPECTED_N}")
elif cov_nx != EXPECTED_N or cov_ny != EXPECTED_N:
    fail("G2-length", f"covariance {cov_nx}x{cov_ny} != {EXPECTED_N}")
else:
    ok("G2-length", f"{nbins} == {EXPECTED_N} == covariance dimension")

print("STEP 5  INDEPENDENT derivation (grid shape + central supports; no widths, no p4_lib)")
x5 = th1_flat(*CEN5)
x4 = th1_flat(*CEN4)
if x5.size != int(np.prod(NB5)) or x4.size != int(np.prod(NB4)):
    fail("grid-shape", f"central sizes {x5.size}/{x4.size} vs {int(np.prod(NB5))}/{int(np.prod(NB4))}")
m5 = x5 > 0
m4 = x4 > 0
i5 = np.nonzero(m5)[0]
reach = np.zeros(int(np.prod(NB4)), bool)
reach[np.unique(i5 // W_AXIS_LAST_SIZE)] = True
eff4 = np.nonzero(m4 & reach)[0].astype(np.int64)
unreach = np.nonzero(m4 & ~reach)[0].astype(np.int64)
print(f"  m5 reported = {int(m5.sum())}   m4 reported = {int(m4.sum())}   "
      f"effective4 = {eff4.size}   unreachable = {unreach.size}")
R["m5_reported"] = int(m5.sum())
R["m4_reported"] = int(m4.sum())
R["effective4_size"] = int(eff4.size)
R["unreachable_derived"] = [int(v) for v in unreach]

print("STEP 6  G1: read-back vector == independently derived effective4")
if idx.size != eff4.size:
    fail("G1", f"length {idx.size} vs derived {eff4.size}")
elif not np.array_equal(idx, eff4):
    d = int(np.count_nonzero(idx != eff4))
    first = int(np.nonzero(idx != eff4)[0][0])
    fail("G1", f"{d} of {idx.size} entries differ; first at row {first}: "
               f"stored {int(idx[first])} vs derived {int(eff4[first])}")
else:
    ok("G1", f"all {idx.size} row labels agree exactly")

print("STEP 7  G4: derived unreachable set == the recorded one")
if [int(v) for v in unreach] != EXPECTED_UNREACHABLE:
    fail("G4", f"derived {[int(v) for v in unreach]} != recorded {EXPECTED_UNREACHABLE}")
else:
    ok("G4", f"{EXPECTED_UNREACHABLE}")

print("STEP 8  G3: sha256 of the READ-BACK array vs the receipt's row_index_sha256")
pm = json.load(open(PROJMAN))
recorded = pm.get("row_index_sha256")
readback = hashlib.sha256(np.ascontiguousarray(idx.astype(np.int64)).tobytes()).hexdigest()
R["row_index_sha256_recorded"] = recorded
R["row_index_sha256_readback"] = readback
print(f"  recorded (hashed from the in-memory array) = {recorded}")
print(f"  read back OUT OF THE OBJECT                = {readback}")
if recorded != readback:
    fail("G3", "the artifact disagrees with the intent it was hashed from")
else:
    ok("G3", "artifact and intent agree -- two digests of DIFFERENT objects now, not one array twice")

print("STEP 9  G7: MUTATION CONTROL -- perturb one entry in memory; the comparison MUST fire")
mut = idx.copy()
mut[100] = int(mut[100]) + 1
fired_eq = not np.array_equal(mut, eff4)
mut_sha = hashlib.sha256(np.ascontiguousarray(mut.astype(np.int64)).tobytes()).hexdigest()
fired_sha = mut_sha != recorded
print(f"  perturbed row 100: {int(idx[100])} -> {int(mut[100])}")
print(f"  equality comparison fired : {fired_eq}")
print(f"  digest comparison fired   : {fired_sha}")
R["mutation_control"] = {"row": 100, "from": int(idx[100]), "to": int(mut[100]),
                         "equality_fired": bool(fired_eq), "digest_fired": bool(fired_sha)}
if not (fired_eq and fired_sha):
    fail("G7", "the instrument did not detect a one-entry perturbation; NO PASS MAY BE REPORTED")
else:
    ok("G7", "both comparisons detect a single perturbed entry")

print("STEP 10 G6: digest the 4D product AFTER -- read-only proven, not claimed")
sha_after = file_sha(PROJ)
R["proj4d_sha256_after"] = sha_after
print(f"  after  = {sha_after}")
if sha_after != sha_before:
    fail("G6", "the 4D product changed during this check")
else:
    ok("G6", "byte-identical before and after")

out["notes"]["c5_not_opened"] = ("the 39.4 GiB std_final5_candidate.root was NOT opened by this check; "
                                "its digest 950f8cb1... is carried forward from the stages-4-6 receipt "
                                "and was NOT re-verified here")
out["verdict"] = "PASS" if not out["failures"] else "FAIL"
print("=" * 78)
print(f"VERDICT: {out['verdict']}   failures: {len(out['failures'])}")
print(json.dumps(out, indent=2))
sys.exit(0 if out["verdict"] == "PASS" else 1)
