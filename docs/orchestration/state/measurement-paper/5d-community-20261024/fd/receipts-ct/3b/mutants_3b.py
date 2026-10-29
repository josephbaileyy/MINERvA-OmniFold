#!/usr/bin/env python3
"""Mutation run for 3b (FD-CT-3B-DECLARATION.md section 11): one textual change at a time to fd_ct_closure.py,
fd_ct_readers.py's mismatch reader or submit_fd_ct.sh, applied in place; test_fd_ct_closure and test_fd_ct_readers run
against it, and the file is restored (every file's sha256 checked after every mutant and at the end). A mutant is
killed if the run fails; one whose text is not found exactly once counts as a failure of this receipt.

    python3 -I -B mutants_3b.py <repo>
"""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
ND = REPO / "nd-unfolding"
C, R, S = ND / "fd_ct_closure.py", ND / "fd_ct_readers.py", ND / "submit_fd_ct.sh"
MUTANTS = [
    # the driver
    (C, "truth side: w_truth unchecked", '"MCgen", "w_truth", "pass_truth"', '"MCgen", "pass_truth"'),
    (C, "truth side: edges unchecked", '        bad.append("edges")\n', "        pass\n"),
    (C, "truth side: MCreco dtype unchecked", ' or \\\n            np.asarray(resp["MCreco"]).dtype != np.asarray(pseudo["MCreco"]).dtype:', ":"),
    (C, "observed rows from the response dump", 'reco = np.asarray(pseudo["MCreco"])', 'reco = np.asarray(resp["MCreco"])'),
    (C, "observed rows without the window", "        keep &= (reco[:, k] >= e[0]) & (reco[:, k] < e[-1])\n", "        pass\n"),
    (C, "observed rows with fakes", 'keep = np.asarray(pseudo["pass_reco"], bool) & np.asarray(pseudo["pass_truth"], bool)',
     'keep = np.asarray(pseudo["pass_reco"], bool)'),
    (C, "observed counts unweighted", 'exp["obs"], exp["obs_counts"] = reco[keep], w[keep]', 'exp["obs"], exp["obs_counts"] = reco[keep], np.ones(int(keep.sum()))'),
    (C, "digest check removed", "(a.expect_response_sha256, a.expect_pseudo_sha256):", "(shas[\"response\"], shas[\"pseudo\"]):"),
    (C, "axes check removed", "        if names != AXES:\n", "        if False:\n"),
    (C, "overwrite allowed", "    if a.out.exists():\n", "    if False:\n"),
    (C, "reco-identical flag inverted", 'reco_identical = bool(np.array_equal(resp["MCreco"], pseudo["MCreco"]))',
     'reco_identical = not bool(np.array_equal(resp["MCreco"], pseudo["MCreco"]))'),
    (C, "truth reference from the pseudo dump", "exp, x_true = L.closure_inputs(resp, ones)", "exp, x_true = L.closure_inputs(pseudo, ones)"),
    # the reader
    (R, "M0 file set unchecked", "    if have != want:\n", "    if False:\n"),
    (R, "M0 pseudo pin unchecked", '"pseudo_npz_sha256": pins[variant], ', ""),
    (R, "M0 refinement unchecked", '        bad.append("the refinement must not run in a signal-only closure")\n', "        pass\n"),
    (R, "M0 reco-identical unchecked", '        bad.append("pseudo_reco_identical must be true for zero and false for every shifted variant")\n', "        pass\n"),
    (R, "M0 estimator unchecked", '        bad.append("estimator parameters")\n    code', "        pass\n    code"),
    (R, "M0 code digests unchecked", '            bad.append(f"code_sha256[{name}] is not this deploy\'s")\n', "            pass\n"),
    (R, "M1 truth unchecked", "all(np.array_equal(xt[v], T0) for v in pins)", "True"),
    (R, "M2 recoil pin unchecked", 'f0.require("M2", a.recoil_readout, RECOIL_READOUT_SHA256, "3a readout")', "pass"),
    (R, "delta without the floor", "delta = {v: b[v] - b[\"zero\"] for v in pins}", "delta = dict(b)"),
    (R, "bias against f", "b = {v: X[v] / T - 1.0 for v in pins}", "b = {v: X[v] / f - 1.0 for v in pins}"),
    (R, "cosine against +d", 'float(-h @ d / (nh * nd))', 'float(h @ d / (nh * nd))'),
    (R, "residual h - d", "        res = h + d\n", "        res = h - d\n"),
    (R, "half-span not halved", 'h = (delta[f"{s}_p1"] - delta[f"{s}_m1"]) / 2.0', 'h = (delta[f"{s}_p1"] - delta[f"{s}_m1"])'),
    (R, "data half-span against T", 'd = (dat[f"{s}_p1"] - dat[f"{s}_m1"]) / (2.0 * f)', 'd = (dat[f"{s}_p1"] - dat[f"{s}_m1"]) / (2.0 * T)'),
    (R, "W2b half-span from rr0 only", 'w2b = pair((delta["w2b_rr1"] - delta["w2b_rr0"]) / 2.0, d_w2b)', 'w2b = pair(delta["w2b_rr0"], d_w2b)'),
    (R, "closure analogue with cross-talk", '            for s in PRIMARY)\n    out = {"schema": "fd-ct-mismatch/1"', '            for s in SPECIES)\n    out = {"schema": "fd-ct-mismatch/1"'),
    (R, "guard without the closures", "guard = f0.LeakGuard(f, [T, *X.values(), *(np.where", "guard = f0.LeakGuard(f, [T, *(np.where"),
    (R, "guard without the data", "*(np.where(near_f(x, f), np.nan, x) for x in dat.values())])", "])"),
    (R, "shared not-citable list", '"not_citable_for": LABELS["mismatch_not_citable_for"],', '"not_citable_for": LABELS["not_citable_for"],'),
    # the submit line
    (S, "submit: pin unchecked", '    [ "$(git -C "$D" rev-parse HEAD)" = "$PIN" ] || { echo "refusing: $D is not at $PIN" >&2; exit 2; }\n', ""),
    (S, "submit: existing closures allowed", '    [ ! -e "$B/closures" ] && [ ! -e "$B/lanes" ] || { echo "refusing: $B/closures or $B/lanes exists" >&2; exit 2; }\n', ""),
    (S, "submit: B unchecked", '    [ "$n" -eq 13 ] && [ "$m" -eq 13 ] || { echo "refusing: $n steps, $m of them writing under $B/closures/" >&2; exit 2; }\n', ""),
    (S, "submit: premium QOS", "--qos=regular", "--qos=premium"),
    (S, "submit: longer limit", "--time=00:45:00", "--time=02:00:00"),
]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


orig = {p: p.read_text() for p in (C, R, S)}
digest = {p: sha(p) for p in orig}
env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
killed = survived = unapplied = 0
print(f"files {[f'{p.name} {digest[p][:16]}' for p in orig]}  mutants {len(MUTANTS)}", flush=True)
try:
    for path, name, old, new in MUTANTS:
        text = orig[path]
        if text.count(old) != 1:
            unapplied += 1
            print(f"NOT APPLIED  {name}: found {text.count(old)} times", flush=True)
            continue
        path.write_text(text.replace(old, new))
        r = subprocess.run([sys.executable, "-B", "-m", "unittest", "test_fd_ct_closure", "test_fd_ct_readers"],
                           cwd=ND / "tests", env=env, capture_output=True, text=True, timeout=1800)
        path.write_text(text)
        if any(sha(p) != digest[p] for p in orig):
            raise SystemExit("a file was not restored")
        ok = r.returncode != 0
        killed += ok
        survived += not ok
        tail = [ln for ln in r.stderr.splitlines() if ln.startswith(("FAILED", "OK", "Ran"))]
        print(f"{'KILLED  ' if ok else 'SURVIVED'}  {name}  ({'; '.join(tail)})", flush=True)
finally:
    for p, t in orig.items():
        p.write_text(t)
restored = all(sha(p) == digest[p] for p in orig)
print(f"killed {killed} of {len(MUTANTS)}; survived {survived}; not applied {unapplied}; files restored {restored}")
raise SystemExit(0 if survived == 0 and unapplied == 0 and restored else 1)
