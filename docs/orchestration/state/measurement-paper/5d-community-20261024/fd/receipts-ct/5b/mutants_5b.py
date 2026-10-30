#!/usr/bin/env python3
"""Mutation run for 5B (FD-CT-5B-DECLARATION.md section 11): one textual change at a time to fd_ct_period_inputs.py,
fd_ct_periods.py or submit_fd_ct.sh's 5b stages, applied in place; test_fd_ct_periods runs against it, and the file
is restored (every file's sha256 checked after every mutant and at the end). A mutant is killed if the run fails; one
whose text is not found exactly once counts as a failure of this receipt.

    python3 -I -B mutants_5b.py <repo>
"""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
ND = REPO / "nd-unfolding"
I, P, S = ND / "fd_ct_period_inputs.py", ND / "fd_ct_periods.py", ND / "submit_fd_ct.sh"
MUTANTS = [
    # the inputs driver
    (I, "merge: loop digests unchecked", '"sha256": require(p, ZERO_LOOPS[pl], f"zero loop {pl}")', '"sha256": sha256(p)'),
    (I, "merge: playlists reversed", "    for pl in PERIODS[a.period]:\n        p = a.loops_dir", "    for pl in reversed(PERIODS[a.period]):\n        p = a.loops_dir"),
    (I, "merge: overwrite allowed", "    fresh(a.out, receipt, partial)\n", "    pass\n"),
    (I, "PB grouping", '"PB": PLAYLISTS[6:9]', '"PB": PLAYLISTS[6:8]'),
    (I, "stage-flux: copies unchecked", '        require(d, FLUX[P], f"{P} flux copy")\n', "        pass\n"),
    (I, "stage-flux: sources unchecked", '        require(a.src_dir / dests[P].name, FLUX[P], f"{P} flux source")\n', "        pass\n"),
    (I, "check: merge receipt unchecked", '        problems.append("the merge is not the one its receipt names")\n', "        pass\n"),
    (I, "check: flux pin unchecked", 'flux_sha = require(a.flux, FLUX[a.period], f"{a.period} flux file")', "flux_sha = sha256(a.flux)"),
    (I, "check: dtype ignored", "    if a.shape != b.shape or a.dtype != b.dtype:\n", "    if a.shape != b.shape:\n"),
    (I, "check: nn vs lat unchecked", "    if not all(nn_vs_lat.values()):\n", "    if False:\n"),
    (I, "check: background meta unchecked", '        problems.append("the background dump does not name this lateral npz and merge")\n', "        pass\n"),
    (I, "check: flux POT unchecked", ' or abs(pot["flux_weighting_over_merge_minus_1"]) > POT_REL:', ":"),
    (I, "check: flux flatness exact", "FLUX_FLAT = 1e-14\n", "FLUX_FLAT = 0.0\n"),
    (I, "check: ALL vs MP-1 on the nn npz", 'rec["all_vs_mp1_zero"] = {"lat_npz": compare(a.lat_npz, a.mp1_lat_npz, NPZ_KEYS),',
     'rec["all_vs_mp1_zero"] = {"lat_npz": compare(a.lat_npz, a.lat_npz, NPZ_KEYS),'),
    (I, "check: MP-1 pins unchecked", '        require(a.mp1_lat_npz, MP1_ZERO["lat_npz"], "MP-1 lat_zero.npz")\n', "        pass\n"),
    (I, "unfold: existing product allowed", "    fresh(*targets)\n", "    pass\n"),
    (I, "merge: POT unchecked before the dumps", "    if abs(pot_rel) > POT_REL:\n        partial.unlink()", "    if False:\n        partial.unlink()"),
    (I, "check: folders not made", "        d.mkdir(parents=True, exist_ok=True)\n", "        pass\n"),
    (I, "unfold: receipt period unchecked", '("fd-ct-5b-inputs/1", a.period):', '("fd-ct-5b-inputs/1", rec.get("period")):'),
    (I, "unfold: dump digests unchecked", '    require(Path(bkg), bkg_sha, f"{a.period} background dump")\n', "    pass\n"),
    (I, "unfold: missing product accepted", "    if rc == 0 and missing:\n", "    if False:\n"),
    # the readers
    (P, "K0: receipt code unchecked", '        raise f0.Stop(control, f"{p.name}: not made by this deploy\'s fd_ct_period_inputs.py")\n', "        pass\n"),
    (P, "K0: key coverage unchecked", '        raise f0.Stop("K0", "the ALL receipt\'s comparison does not cover every declared key")\n', "        pass\n"),
    (P, "K1 ignores the background", 'for d in ("lat_npz", "lat_bkg") for k, v in cmp_[d].items() if not v)', 'for d in ("lat_npz",) for k, v in cmp_[d].items() if not v)'),
    (P, "K2 to a tolerance", "k2 = bool(x_all.shape == x_mp1.shape and np.array_equal(x_all, x_mp1))", "k2 = bool(np.allclose(x_all, x_mp1, rtol=1e-12))"),
    (P, "K3 without sqrt 2", "TAU_K = 5.0 * math.sqrt(2.0)", "TAU_K = 5.0"),
    (P, "K3 one-sided", "within = np.abs(X / f - 1.0) <= tau", "within = (X / f - 1.0) <= tau"),
    (P, "K3 writes q", '"tau_rel": tau.tolist(), "tau_k": TAU_K,', '"q": (np.abs(X / f - 1.0) / tau).tolist(), "tau_rel": tau.tolist(), "tau_k": TAU_K,'),
    (P, "K0: period unfolds allowed", '        raise f0.Stop("K0", f"period unfolds exist before the control: {present}")\n', "        pass\n"),
    (P, "precheck exits 0 on FAIL", "    return rc if ok else 1", "    return rc"),
    (P, "gate: verdict unchecked", '    if (r.get("schema"), r.get("verdict")) != (schema, "PASS"):', '    if r.get("schema") != schema:'),
    (P, "gate: code unchecked", '        raise f0.Stop("G", f"{p.name} was not made by this deploy\'s fd_ct_periods.py")\n', "        pass\n"),
    (P, "gate: ALL unfold unchecked", '            raise f0.Stop("G", "the ALL unfold is not the one the control read")\n', "            pass\n"),
    (P, "gate: period receipts unchecked", '        for P in PER:\n            receipt(a.b, P, "G")\n', ""),
    (P, "seed blocks shared", '"PB": tuple(range(2001, 2011))', '"PB": tuple(range(1001, 1011))'),
    (P, "K3 sigma unchecked", '        raise f0.Stop("K3", "the jitter sigma recomputed from the pinned receipts is not the declared one")\n', "        pass\n"),
    (P, "verdict ignores K2", 'verdict = "PASS" if (k1 and k2 and k3_ok) else "FAIL"', 'verdict = "PASS" if (k1 and k3_ok) else "FAIL"'),
    (P, "control exits 0 on FAIL", '    return rc if verdict == "PASS" else 1', "    return rc"),
    (P, "control guard unfiltered", "    return f0.LeakGuard(f, [np.where(ct.near_f(x, f), np.nan, x) for x in integrals])",
     "    return f0.LeakGuard(f, list(integrals))"),
    (P, "Q0: verdict unchecked", '("fd-ct-5b-control/1", "PASS"):', '("fd-ct-5b-control/1", cj.get("verdict")):'),
    (P, "Q0: ALL unfold unchecked", '        raise f0.Stop("Q0", "the ALL unfold is not the one the control read")\n', "        pass\n"),
    (P, "Q1: file set unchecked", "        if have != want:\n", "        if False:\n"),
    (P, "Q1: replica seed unchecked", '{"construction": "data", "truth": "nominal", "bootstrap_seed": b, "jitter_seed": None,',
     '{"construction": "data", "truth": "nominal", "jitter_seed": None,'),
    (P, "Q2: truth npz unchecked", '("s5p-mc-truth-pred/1", rec[P]["files"]["lat_npz"][1]):', '("s5p-mc-truth-pred/1", m.get("npz_sha256")):'),
    (P, "Q2: flatness unchecked", '        if not rec[P].get("flux_constant_over_pt"):\n', "        if False:\n"),
    (P, "exposure without the flux", 'e_raw[P] = float(z["data_pot"]) * float(np.asarray(z["flux"], float).mean())', 'e_raw[P] = float(z["data_pot"])'),
    (P, "dr numerator unflipped", '(lambda n, d: r[n] / r[d] - 1.0) if q == "dr"', '(lambda n, d: r[d] / r[n] - 1.0) if q == "dr"'),
    (P, "dr is raw", '(lambda n, d: r[n] / r[d] - 1.0) if q == "dr" else (lambda n, d: x[n] / x[d] - 1.0)',
     '(lambda n, d: x[n] / x[d] - 1.0) if q == "dr" else (lambda n, d: x[n] / x[d] - 1.0)'),
    (P, "noise pairing broken", "    draws = [sum(a * D[X][k] for X, a in coef.items()) for k in range(N_BOOT)]",
     "    draws = [sum(a * D[X][(k + i) % N_BOOT] for i, (X, a) in enumerate(coef.items())) for k in range(N_BOOT)]"),
    (P, "noise without the coefficients' square", "    N = sum(np.outer(a, a) * np.mean(", "    N = sum(np.outer(a, 1) * np.mean("),
    (P, "metric without C_resp", '    M = S["M"] / S["ff"]\n    Mi', '    M = S["C_total"] / S["ff"]\n    Mi'),
    (P, "contrast cells swapped", "    return float(q(PZ_HI) / q(PZ_LO) - 1.0)", "    return float(q(PZ_LO) / q(PZ_HI) - 1.0)"),
    (P, "C_PL without k", "    C = k * sum(e[P] * np.outer(g[P], g[P]) for P in PER)", "    C = sum(e[P] * np.outer(g[P], g[P]) for P in PER)"),
    (P, "C_PL mean unweighted", "    mbar = sum(e[P] * r[P] for P in PER)", "    mbar = sum(r[P] for P in PER) / 3.0"),
    (P, "5A difference signed the other way", '        dlt = g[P] - np.asarray(g5a[P], float)', '        dlt = np.asarray(g5a[P], float) - g[P]'),
    (P, "5A readout unpinned", '    f0.require("Q4", a.readout_5a, READOUT_5A_SHA256, "5A readout")\n', ""),
    (P, "periods guard without the truths", "    guard = guarded(f, [*allX, *T.values()])", "    guard = guarded(f, [*allX])"),
    # the submit stages
    (S, "submit 5b: pin unchecked", '    [ "$(git -C "$D" rev-parse HEAD)" = "$PIN" ] || { echo "refusing: $D is not at $PIN" >&2; exit 2; }\n    # the login',
     "    # the login"),
    (S, "submit 5b: existing run allowed", '        [ ! -e "$B/$d" ] || { echo "refusing: $B/$d exists" >&2; exit 2; }\n      done\n    else', "      done\n    else"),
    (S, "submit 5b: B unchecked", '    [ "$n" -eq "$N" ] && [ "$m" -eq "$N" ] || { echo "refusing: $n steps, $m of them writing under $B/" >&2; exit 2; }\n', ""),
    (S, "submit 5b: premium", "      TIME=01:00:00; JOB=fd_ct_5b_inputs", "      TIME=01:00:00; JOB=fd_ct_5b_inputs; COMMON+=(--qos=premium)"),
    (S, "submit 5b: periods limit", "TIME=01:30:00", "TIME=03:00:00"),
    (S, "submit 5b: gate skipped", '      || { echo "refusing: the gate did not pass', '      || true || { echo "refusing: the gate did not pass'),
    (S, "submit 5b: step folders not made", '    for d in "${MAKE[@]}"; do mkdir "$B/$d"; done', '    true'),
    (S, "submit 5b: inputs at 64 CPUs", "N=17; LAST=3; CPT=32; MEM=56G", "N=17; LAST=3; CPT=64; MEM=120G"),
    (S, "submit 5b: flux not staged", '      "${PY[@]}" "$D/nd-unfolding/fd_ct_period_inputs.py" stage-flux', '      true "$D/nd-unfolding/fd_ct_period_inputs.py" stage-flux'),
]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


orig = {p: p.read_text() for p in (I, P, S)}
digest = {p: sha(p) for p in orig}
env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
if "--dry" in sys.argv:
    bad = [(n, orig[p].count(o)) for p, n, o, _ in MUTANTS if orig[p].count(o) != 1]
    print(f"{len(MUTANTS)} mutants; not applicable exactly once: {bad}")
    raise SystemExit(1 if bad else 0)
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
        r = subprocess.run([sys.executable, "-B", "-m", "unittest", "test_fd_ct_periods"],
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
