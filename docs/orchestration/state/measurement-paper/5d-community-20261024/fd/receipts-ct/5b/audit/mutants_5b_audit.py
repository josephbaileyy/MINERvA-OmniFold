#!/usr/bin/env python3
"""Mutation run for the 5B block's audit (FD-CT-5B-AUDIT-DECLARATION.md section 9): one textual change at a time to
nd-unfolding/fd_ct_5b_audit.py, applied in place; test_fd_ct_5b_audit runs against it, and the file is restored (its
sha256 checked after every mutant and at the end). A mutant is killed if the run fails; one whose text is not found
exactly once counts as a failure of this receipt. The mutants cover every stop clause's threshold, comparison and
operand, the statistics behind them, each refusing control, and the leak guard's table.

    python3 -I -B mutants_5b_audit.py <repo>        (--dry checks only that every mutant applies once)
"""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
ND = REPO / "nd-unfolding"
A = ND / "fd_ct_5b_audit.py"
MUTANTS = [
    # the stop condition: thresholds, comparisons, operands
    ("O: E threshold 0.45", "O_E, O_A = 0.5, 2.0", "O_E, O_A = 0.45, 2.0"),
    ("O: amplitude bound 2.5", "O_E, O_A = 0.5, 2.0", "O_E, O_A = 0.5, 2.5"),
    ("O: E strict", 'return bool(all(idf[X]["E"] >= O_E and', 'return bool(all(idf[X]["E"] > O_E and'),
    ("O: amplitude signed", "all(abs(a) <= O_A for a", "all(a <= O_A for a"),
    ("O: PB alone", 'for a in idf[X]["a"]) for X in ("PB", "PC")))', 'for a in idf[X]["a"]) for X in ("PB",)))'),
    ("O: any period", 'return bool(all(idf[X]["E"] >= O_E and all(abs(a) <= O_A for a in idf[X]["a"]) for X in',
     'return bool(any(idf[X]["E"] >= O_E and all(abs(a) <= O_A for a in idf[X]["a"]) for X in'),
    ("O: E inverted", 'out[X] = {"E": 1.0 - c1 / c0,', 'out[X] = {"E": c1 / c0,'),
    ("O: no intercept", "coef, c1 = wls(g[X], w, [one, *ds])", "coef, c1 = wls(g[X], w, [*ds])"),
    ("O: weights 1/sigma", "        w = 1.0 / sig[X] ** 2\n", "        w = 1.0 / sig[X]\n"),
    ("O: uniform kept", "UNIFORM_REL = 1e-12 ", "UNIFORM_REL = 0.0 "),
    ("O: stat and seed candidates", '        if G in ("stat", "seed"):\n            continue\n', ""),
    ("O: one mode per block", "CAND_FRAC, CAND_TOP = 0.01, 3", "CAND_FRAC, CAND_TOP = 0.01, 1"),
    ("O: 50% cut", "CAND_FRAC, CAND_TOP = 0.01, 3", "CAND_FRAC, CAND_TOP = 0.5, 3"),
    ("N: threshold 0.6", "N_SMED = 0.5\n", "N_SMED = 0.6\n"),
    ("N: >= ", "    N = bool(s_med > N_SMED)", "    N = bool(s_med >= N_SMED + 1e-3)"),
    ("N: population SD", "s_med = float(np.std(med, ddof=1) / np.median(sig))", "s_med = float(np.std(med) / np.median(sig))"),
    ("N: mean sigma", "s_med = float(np.std(med, ddof=1) / np.median(sig))", "s_med = float(np.std(med, ddof=1) / np.mean(sig))"),
    ("R: threshold 0.4", "R_RET = 0.5\n", "R_RET = 0.4\n"),
    ("R: inverted", "    R = bool(retention_median < R_RET)", "    R = bool(retention_median > R_RET)"),
    ("R: retention over P", "R = [float(np.trace(Pi @ C) / np.trace(C)) for C in Pk]", "R = [float(np.trace(Pi @ C) / np.trace(P)) for C in Pk]"),
    ("stop ignores R", '"stop": bool(O or N or R),', '"stop": bool(O or N),'),
    # the construction and its statistics
    ("k = V2", "    return V2 / (1.0 - V2)\n", "    return V2\n"),
    ("block unweighted", "    return k * sum(e[X] * np.outer(g[X], g[X]) for X in PER), g",
     "    return k * sum(np.outer(g[X], g[X]) for X in PER) / 3.0, g"),
    ("OV: max", "float(sum(min(li, bi) for li, bi", "float(sum(max(li, bi) for li, bi"),
    ("OV: along P", "(float(m[1] @ B @ m[1]) for m in mp)", "(float(m[1] @ P @ m[1]) for m in mp)"),
    ("DR misses C_resp", 'if G in ("detector", "lateral", "C_resp"):\n            groups["DR"] += B',
     'if G in ("detector", "lateral"):\n            groups["DR"] += B'),
    ("noise vs stat: sqrt k", "math.sqrt(2.0 * k),", "math.sqrt(k),"),
    ("look-elsewhere squared", '"if_PB_PC_patterns_identical": n * BETA_TAIL,', '"if_PB_PC_patterns_identical": n * BETA_TAIL ** 2,'),
    ("uniform share 1/16", "    u = np.full(N_CELLS, 0.25)", "    u = np.full(N_CELLS, 1.0 / 16)"),
    ("E_avail contrast sign", "val = float(dlt[lo].mean() - dlt[hi].mean())", "val = float(dlt[hi].mean() - dlt[lo].mean())"),
    ("5A noise: seed not halved", "seed = {X: (om @ hs[X]) ** 2 / 2.0 for X in PER}", "seed = {X: (om @ hs[X]) ** 2 for X in PER}"),
    ("5A noise: not centred", "        return {X: dd[X] - mm for X in PER}", "        return {X: dd[X] for X in PER}"),
    ("debiased unclipped", "    Pd = (V[:, pos] * lam[pos]) @ V[:, pos].T", "    Pd = (V * lam) @ V.T"),
    # the refusing controls
    ("A0: pin unchecked", '    f0.require("A0", a.readout_5b, READOUT_5B_SHA256, "5B readout")\n', ""),
    ("A1: directory unchecked", '            raise f0.Stop("A1", f"{X}: the unfold directory holds {have}, not the declared {len(want)}")\n',
     "            pass\n"),
    ("A1: unfold digests unchecked", '                raise f0.Stop("A1", f"{X} b{b}: the unfold is not the one the 5B readout read")\n',
     "                pass\n"),
    ("A1: block tolerance 1", "float(np.max(np.abs(C - P)) / np.max(np.abs(P))) <= TOL,", "float(np.max(np.abs(C - P)) / np.max(np.abs(P))) <= 1.0,"),
    ("A1: noise sigma unchecked", 'np.allclose(g[X], gv[X]["g_5b"], rtol=0, atol=TOL) and np.allclose(g_sig[X], gv[X]["g_5b_noise_sigma"],',
     'np.allclose(g[X], gv[X]["g_5b"], rtol=0, atol=TOL) and np.allclose(g_sig[X], g_sig[X],'),
    ("A2: C_e sum unchecked", '"C_e is the sum of S1\'s blocks": np.allclose(sum(blocks.values()), S["C_e"],',
     '"C_e is the sum of S1\'s blocks": np.allclose(S["C_e"], S["C_e"],'),
    ("A2: band count 37", "N_BANDS, N_LATERALS = 38, 5", "N_BANDS, N_LATERALS = 37, 5"),
    ("A3: 2D digests unchecked", '            raise f0.Stop("A3", f"{path}: not at its analysis.json digest")\n', "            pass\n"),
    ("A3: seed-42 r unchecked", "all(np.allclose(r0[X], z[f\"r_{X}\"], rtol=TOL, atol=0) for X in PER), \"differs\")",
     "True, \"differs\")"),
    ("A3: noise share unchecked", "abs(share / share_ref - 1.0) <= CONTROL_2D_REL,", "True,"),
    ("A3: reprojection unchecked", "all(np.allclose(om @ z[f\"g_{X}\"], g5a_committed[X], rtol=0, atol=TOL) for X in PER), \"differs\")",
     "True, \"differs\")"),
    ("S: E_avail sets unchecked", "bad = cp.cell_sets_problems(a.definition) + ea_sets_problems(a.definition)",
     "bad = cp.cell_sets_problems(a.definition)"),
    ("guard: no integrals", 'guard = cp.guarded(f, b5["integrals"])', "guard = cp.guarded(f, [])"),
    ("A0: schema unchecked", 'bool(ro.get("schema") == "fd-ct-5b-periods/1" and pins.get("s1_npz")', 'bool(pins.get("s1_npz")'),
    ("A1: receipts unchecked", '            raise f0.Stop("A1", f"{X}: the check receipt is not the one the 5B readout read")\n',
     "            pass\n"),
    ("A1: floor unchecked", 'np.sqrt(np.diag(Cn)), ro["C_PL5D"]["noise_floor_sigma_rel"], rtol=TOL, atol=0),',
     'np.sqrt(np.diag(Cn)), np.sqrt(np.diag(Cn)), rtol=TOL, atol=0),'),
    ("A1: sigma_M unchecked", 'np.allclose(np.sqrt(np.diag(M)), ro["sigma_rel_M"], rtol=TOL, atol=0),',
     'np.allclose(np.sqrt(np.diag(M)), np.sqrt(np.diag(M)), rtol=TOL, atol=0),'),
    ("A1: exposure unchecked", 'abs(e[X] - ro["constants"]["exposure_share"][X]) <= TOL for X in PER),',
     'abs(e[X] - e[X]) <= TOL for X in PER),'),
    ("A4: span unchecked", "    if Q.shape[1] > 2 or worst > 1e-8:", "    if Q.shape[1] > 2:"),
    ("OV: no zero floor", "    b = [v if abs(v) >= EIG_FLOOR else 0.0 for v in", "    b = [v for v in"),
    ("mean shift sign", '"mean_shift_diag": (np.diag(Pm) - np.diag(P)).tolist(),', '"mean_shift_diag": (np.diag(P) - np.diag(Pm)).tolist(),'),
]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


orig = A.read_text()
digest = sha(A)
env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
if "--dry" in sys.argv:
    bad = [(n, orig.count(o)) for n, o, _ in MUTANTS if orig.count(o) != 1]
    print(f"{len(MUTANTS)} mutants; not applicable exactly once: {bad}")
    raise SystemExit(1 if bad else 0)
killed = survived = unapplied = 0
print(f"file {A.name} {digest[:16]}  mutants {len(MUTANTS)}", flush=True)
try:
    for name, old, new in MUTANTS:
        if orig.count(old) != 1:
            unapplied += 1
            print(f"NOT APPLIED  {name}: found {orig.count(old)} times", flush=True)
            continue
        A.write_text(orig.replace(old, new))
        r = subprocess.run([sys.executable, "-B", "-m", "unittest", "test_fd_ct_5b_audit"],
                           cwd=ND / "tests", env=env, capture_output=True, text=True, timeout=1800)
        A.write_text(orig)
        if sha(A) != digest:
            raise SystemExit("the file was not restored")
        ok = r.returncode != 0
        killed += ok
        survived += not ok
        tail = [ln for ln in r.stderr.splitlines() if ln.startswith(("FAILED", "OK", "Ran"))]
        print(f"{'KILLED  ' if ok else 'SURVIVED'}  {name}  ({'; '.join(tail)})", flush=True)
finally:
    A.write_text(orig)
restored = sha(A) == digest
print(f"killed {killed} of {len(MUTANTS)}; survived {survived}; not applied {unapplied}; file restored {restored}")
raise SystemExit(0 if survived == 0 and unapplied == 0 and restored else 1)
