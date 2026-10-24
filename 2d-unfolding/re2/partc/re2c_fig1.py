#!/usr/bin/env python3
"""RE-2 part C copy of stageF/rebuild/scripts/make_fig1_q.py (7710d601...), RE2-DECLARATION-C.md §3.8.

  (no --arm)      the original: with the purity inputs it must reproduce fig1_validation.pdf 82665808... (K1-roll),
                  in the recorded environment (python 3.12.2, matplotlib 3.11.2, numpy 2.5.4; RUN-fig1.txt)
  --arm refined --pins-json FILE
                  Fig. 1 from E_R and Q_R. What changes, and nothing else:
    - --reduce is re2c_reduce.py's output (its digest in FILE), and the drawn central value is its field "E_R",
      named explicitly (P13), not "CV42_universe_file";
    - the s5_npz, playlist_npz and combination digests are the ones the previous steps recorded (FILE);
    - check 1 requires cov2d_Q_205.npz's x to equal that E_R, and each npz to carry arm = refined;
    - the inset's \\uqMedian is Q_R's (budget_Q.json), as before.

The original docstring follows.

Regenerate the article's Fig. 1 with the adopted covariance Q = S5 total + C_PL (decision 2026-10-17).

Derived from receipts/2d-c04-adopt-20261012/make_fig1_vl175.py (rebuild SPEC §6). The central-value swap and its
E_C control are unchanged. The covariance is `Q` from cov2d_Q_205.npz (step A), and its checks no longer use the
VL175 --sigma file. They are, each a refusal:
  1. cov2d_Q_205.npz `cells` equal remote_reduce.json's cell gids;
  2. diag(Q) equals diag(s5_total) + diag(C_PL), with those read from the CFS products
     production_cov.npz and playlist_term.npz (--s5-npz, --playlist-npz), not from step A's outputs;
  3. sqrt(diag Q) / E_U on the 205 cells reproduces combination.json's S5_total_plus_C_PL median, p84 and max
     to 1e-12 relative.
The printed inset value comes from --values, a temporary file holding only \\uqMedian (SPEC §6). The script refuses
unless make_figs.py's regex finds exactly one \\uqMedian there and it equals budget_Q.json's Q median at 2 decimals,
and unless --cov and --budget appear in step A's SHA256SUMS (--step-a-sums) with their measured digests.

  python3 make_fig1_q.py --npz fig_arrays.npz --reduce remote_reduce.json --make-figs make_figs.py \\
      --values <uqmedian.tex> --tmp <dir> --outdir <dir> --cov cov2d_Q_205.npz \\
      --s5-npz production_cov.npz --playlist-npz playlist_term.npz --combination combination.json \\
      --budget budget_Q.json --step-a-sums <step A outdir>/SHA256SUMS
"""
import argparse
import re
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

PINS = {
    "npz": "72394a2b4eff9f14b01903ff97525bcb690c2adee58ccaf573a8d95139b415b8",
    "reduce": "2ecfc243ab4a6c508a69df0e231676019106f3ad86f34e3ac3423f7bd2bca9ce",
    "make_figs": "9c4dbf24d5e19161034fbdf6f84834f578fbde3a1b879961ef7c25a739301c7c",
    "s5_npz": "6689d2fc2a795a72e66ee953a32d94c7906dd81a866771979f379c5f163a9ddc",
    "playlist_npz": "c1723cb5e185ae7a6176fbbe523432ab87877c8cddcfe721eaed71f0a43b9476",
    "combination": "050e256023277ec9da492ffa7b9d129275c3afa2bfc6c47091999d88de5bf18d",
}

ap = argparse.ArgumentParser()
for k in ("npz", "reduce", "make_figs", "values", "tmp", "outdir", "cov", "s5_npz", "playlist_npz", "combination",
          "budget", "step_a_sums"):
    ap.add_argument("--" + k.replace("_", "-"), required=True, type=Path)
ap.add_argument("--arm", choices=("purity", "refined"), default="purity")
ap.add_argument("--pins-json", type=Path)
a = ap.parse_args()
REFINED = a.arm == "refined"
CENTRAL = "E_R" if REFINED else "CV42_universe_file"
if REFINED:   # chain of custody: re2c_reduce.json and the refined s5, playlist and combination products
    if not a.pins_json:
        sys.exit("[FAIL] --arm refined needs --pins-json")
    chain = json.loads(a.pins_json.read_text())
    if set(chain) != {"reduce", "s5_npz", "playlist_npz", "combination"}:
        sys.exit(f"[FAIL] --pins-json keys {sorted(chain)}")
    PINS.update(chain)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


for k, want in PINS.items():
    got = sha(getattr(a, k))
    if got != want:
        sys.exit(f"[FAIL] {k}: sha256 {got} != pinned {want}")
sums = {}
for line in a.step_a_sums.read_text().splitlines():
    d, name = line.split(None, 1)
    sums[name.strip()] = d
for k, name in (("cov", "cov2d_Q_205.npz"), ("budget", "budget_Q.json")):
    got = sha(getattr(a, k))
    if sums.get(name) != got:
        sys.exit(f"[FAIL] {name}: sha256 {got} is not step A's SHA256SUMS entry {sums.get(name)}")
print("cov2d_Q_205.npz and budget_Q.json match step A SHA256SUMS")
budget = json.loads(a.budget.read_text())
vals = a.values.read_text()
hits = re.findall(r"\\newcommand\{\\uqMedian\}\{([^}]*)\}", vals)
if len(hits) != 1 or vals.count("\\newcommand") != 1:
    sys.exit(f"[FAIL] --values must hold exactly one \\uqMedian newcommand; found {len(hits)}")
want = f"{budget['Q']['median_pct']:.2f}"
if hits[0] != want:
    sys.exit(f"[FAIL] \\uqMedian {hits[0]!r} != budget_Q.json Q median {want!r}")
print("values file sha256", sha(a.values), "uqMedian", hits[0])

z = dict(np.load(a.npz, allow_pickle=False))
rr = json.loads(a.reduce.read_text())
gids = np.array([pt * 16 + pz for pt, pz in rr["cells"]])
mask = np.diag(z["cov_stat"]) > 0
if not (mask.sum() == 205 and np.array_equal(np.sort(gids), np.flatnonzero(mask))):
    sys.exit("[FAIL] remote_reduce cells are not the released reported mask")
ctl = np.zeros(224); ctl[gids] = rr["central"]["E_C"]
if not np.array_equal(ctl[mask], z["ours_v"][mask]):
    sys.exit("[FAIL] E_C in remote_reduce must equal the released ours_v")
new = np.zeros_like(z["ours_v"]); new[gids] = rr["central"][CENTRAL]
z["ours_v"] = new

cz = np.load(a.cov, allow_pickle=False)
Q = cz["Q"]
if REFINED:
    for nm, path in (("s5_npz", a.s5_npz), ("playlist_npz", a.playlist_npz)):
        zz = np.load(path, allow_pickle=False)
        if "arm" not in zz.files or str(zz["arm"]) != "refined":
            sys.exit(f"[FAIL] {nm} carries no arm = refined")
if Q.shape != (205, 205):
    sys.exit(f"[FAIL] Q shape {Q.shape}")
# check 1: cell identity
if not np.array_equal(np.asarray(cz["cells"], dtype=np.int64), gids):
    sys.exit("[FAIL] cov2d_Q_205.npz cells differ from remote_reduce cells")
if not np.array_equal(cz["x"], new[gids]):
    sys.exit(f"[FAIL] cov2d_Q_205.npz x differs from the drawn central value ({CENTRAL})")
# check 2: diagonal from the independent CFS products
s5 = np.load(a.s5_npz, allow_pickle=False)["total"]
cpl = np.load(a.playlist_npz, allow_pickle=False)["C_PL"]
if not np.allclose(np.diag(Q), np.diag(s5) + np.diag(cpl), rtol=1e-12, atol=0):
    sys.exit("[FAIL] diag(Q) != diag(S5 total) + diag(C_PL)")
# check 3: per-cell relative sigma against the committed combination report
x = new[gids]
rel = 100.0 * np.sqrt(np.diag(Q)) / x
ref = json.loads(a.combination.read_text())["report"]["budget"]["S5_total_plus_C_PL"]["cell_rel_sigma_pct"]
got = {"median": float(np.median(rel)), "p84": float(np.percentile(rel, 84)), "max": float(rel.max())}
for k in ("median", "p84", "max"):
    if abs(got[k] - ref[k]) > 1e-12 * abs(ref[k]):
        sys.exit(f"[FAIL] per-cell sigma {k}: {got[k]!r} != combination.json {ref[k]!r}")
print("checks passed: cells, diag(Q) = diag(S5) + diag(C_PL), per-cell sigma vs combination.json;", got)

c224 = np.zeros((224, 224)); c224[np.ix_(gids, gids)] = Q
z["cov_ours"] = c224
a.tmp.mkdir(parents=True, exist_ok=True)
out_npz = a.tmp / "fig_arrays_q.npz"
np.savez(out_npz, **z)
sys.exit(subprocess.call([sys.executable, str(a.make_figs), "--npz", str(out_npz), "--outdir", str(a.outdir),
                          "--values", str(a.values)]))
