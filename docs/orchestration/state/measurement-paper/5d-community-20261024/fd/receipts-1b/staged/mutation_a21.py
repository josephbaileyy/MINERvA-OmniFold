"""Mutation receipt for addendum A2.1 (FD-1B-STAGED-ADDENDUM-A2-1.md), over fd_1b_mc, fd_1b_c2, fd_1b_cvdenom and
fd_1b_binning. Amendment 2's mutants (mutation_mc_a2.py's M, read from that file, not retyped) are carried against
fd_1b_mc with its suite; those whose target A2.1 replaced are printed NOT APPLICABLE, by name; two whose target
A2.1 rewrote (the U checks, now through same_functional) are re-anchored. A2.1's own mutants follow, each with the
suites that must kill it. Run from nd-unfolding/ with TMPDIR set:

    python3 ../docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/mutation_a21.py

KILLED means the suites exit 1 (a test failed); any other non-zero exit is ERROR, not a kill. Bytecode-free, with a
fixed hash seed, as mutation_mc_a2.py.
"""
import ast
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0", OMP_NUM_THREADS="1",
           OPENBLAS_NUM_THREADS="1")
PYTEST = [sys.executable, "-B", "-m", "pytest", "-p", "no:cacheprovider", "-q", "-x"]
HERE = Path(__file__).resolve().parent
MC, C2, CVD, BIN, E2E = ("tests/test_fd_1b_mc.py",), ("tests/test_fd_1b_c2.py",), ("tests/test_fd_1b_cvdenom.py",), \
    ("tests/test_fd_1b_binning.py",), ("tests/test_fd_1b_a21_e2e.py",)


def literal(path: Path, name: str):
    t = ast.parse(path.read_text())
    return next(ast.literal_eval(n.value) for n in t.body if isinstance(n, ast.Assign)
                and getattr(n.targets[0], "id", "") == name)


CARRIED = literal(HERE / "mutation_mc_a2.py", "M")
REPLACED_A2 = literal(HERE / "mutation_mc_a2.py", "REPLACED")
REPLACED_A21 = {"A2c: the nature rule keeps the truth", "A2c: the nature rule ignores negative truths",   # S3
                "G: the clip gate always open", "G: the clip gate reads anything"}                      # S2
U_OLD = '    if not np.allclose(U, s1["U"], rtol=0, atol=1e-6):\n        raise Refusal("the definition\'s functional is not S1\'s")\n'
U_NEW = '    if not same_functional(U, s1["U"]):\n        raise Refusal("the definition\'s functional is not S1\'s")\n'
REANCHOR = {"B1 (audit): null U check dropped", "B3: readout U check dropped"}
GATE_OLD = "    inv.OPENED.clear()\n    check_clip_gate(a)"           # A2.1 moved the call after the role checks
GATE_NEW = "    check_clip_gate(a)                        # after the role checks"
# Equivalent on every input, with the proof a test (test_fd_1b_c2 Gate.test_i_at_exactly_0_20_is_unreachable): no
# double r has |r - 1| == 0.20, so (i)'s > and >= agree everywhere.
EQUIVALENT = {"724(i): exactly 0.20 counts as beyond"}

NEW = [
    # ---- fd_1b_mc: the U check, truth_weight's install, S3, (e2), S2
    ("fd_1b_mc.py", "U1: the U check back to an absolute tolerance",
     "    return bool(np.array_equal(np.asarray(U).astype(np.float32), np.asarray(stored).astype(np.float32)))",
     "    return bool(np.allclose(U, stored, rtol=0, atol=1e-6))", MC),
    ("fd_1b_mc.py", "U2: the U check compares in float64",
     "    return bool(np.array_equal(np.asarray(U).astype(np.float32), np.asarray(stored).astype(np.float32)))",
     "    return bool(np.array_equal(np.asarray(U, float), np.asarray(stored, float)))", MC),
    ("fd_1b_mc.py", "TW: truth_weight without s5e_deform's install",
     "    s5e_deform.install_ratio_truth(s5n_pseudo)      # idempotent", "    pass  # ", MC),
    ("fd_1b_mc.py", "S3: the nature truth not clipped",
     '        du = dict(du, w_truth=np.where(tz, 0.0, wt), denom_nd=dn)', '        du = dict(du, w_truth=wt, denom_nd=dn)', MC + E2E),
    ("fd_1b_mc.py", "S3: the nature truth clipped on lambda too (the old rule)",
     '        du = dict(du, w_truth=np.where(tz, 0.0, wt), denom_nd=dn)',
     '        du = dict(du, w_truth=np.where(tz | neg, 0.0, wt), denom_nd=dn)', MC + E2E),
    ("fd_1b_mc.py", "S3: the truth clip on w_truth's sign, not w_truth r's",
     '        tz = np.asarray(ui["pass_truth"], bool) & (wt * r < 0)', '        tz = np.asarray(ui["pass_truth"], bool) & (wt < 0)', MC),
    ("fd_1b_mc.py", "S3: the denominator not clipped",
     '        dn = np.where(m_den > 0, np.asarray(ui["denom_nd"], float) + m_den, np.asarray(ui["denom_nd"], float))',
     '        dn = np.asarray(ui["denom_nd"], float)', MC + E2E),
    ("fd_1b_mc.py", "S3: the denominator's negative mass subtracted",
     '        dn = np.where(m_den > 0, np.asarray(ui["denom_nd"], float) + m_den, np.asarray(ui["denom_nd"], float))',
     '        dn = np.where(m_den > 0, np.asarray(ui["denom_nd"], float) - m_den, np.asarray(ui["denom_nd"], float))', MC),
    ("fd_1b_mc.py", "S3: nature without the row denominator",
     '        if "tdw_rows" not in ui:\n            raise Refusal', '        if False:\n            raise Refusal', MC),
    ("fd_1b_mc.py", "e2: a composite subtracts the float64 d_CV",
     '    if d32 is not None:\n        cv = dict(cv, denom=d32)', '    if False:\n        cv = dict(cv, denom=d32)', MC + E2E),
    ("fd_1b_mc.py", "e2: a detector universe keeps its float64 denominator",
     '                if d32 is not None:\n                    single["denom"] = d32', '                if False:\n                    single["denom"] = d32', MC),
    ("fd_1b_mc.py", "e2: a composite without the CV's tdw",
     '        if tdw_cv is None:\n            raise Refusal("a composite needs', '        if False:\n            raise Refusal("a composite needs', MC),
    ("fd_1b_mc.py", "e2: a detector denominator off the CV's accepted",
     '            else:\n                raise Refusal(f"{tag}: its denominator is not the CV\'s',
     '            elif False:\n                raise Refusal(f"{tag}: its denominator is not the CV\'s', MC),
    ("fd_1b_mc.py", "e2: the receipt keeps the float64 d_CV",
     '    cv = dict(cv, denom=d32)\n    labels', '    labels', MC + E2E),
    ("fd_1b_mc.py", "e2: the receipt without the CV's tdw",
     '    if world.get("tdw_cv") is None:\n        raise InvalidReceipt', '    if False:\n        raise InvalidReceipt', MC + E2E),
    ("fd_1b_mc.py", "e2: a negative CV tdw accepted",
     '        if not (np.all(np.isfinite(tdw_cv)) and np.all(tdw_cv >= 0)):', '        if False:', MC),
    ("fd_1b_mc.py", "S2: 'data' runs any item",
     "        if bad:\n            raise Refusal(f\"'data' runs only", "        if False:\n            raise Refusal(f\"'data' runs only", MC),
    ("fd_1b_mc.py", "S2: 'nature' runs any role",
     '    if a.role not in BULK_ROLES:', '    if False:', MC),
    ("fd_1b_mc.py", "S2: the gate without its schema",
     '    want = {"schema": fd_1b_c2.SCHEMA_GATE, **CLIP_GATE}', '    want = dict(CLIP_GATE)', MC),
    ("fd_1b_mc.py", "S2: another truth's reading accepted",
     '    if g.get("reads", {}).get(a.truth) != "option (1)":', '    if False:', MC),
    ("fd_1b_mc.py", "S2: the declared seeds not checked",
     '    if g.get("declared_seeds", {}).get(a.truth) != [int(TOY_SEEDS[a.truth][0]), int(TOY_SEEDS[a.truth][-1])]:',
     '    if False:', MC),
    ("fd_1b_mc.py", "S2: the code digests not checked",
     '    if g.get("code_sha256") != fd_1b_c2.gate_code_digests():', '    if False:', MC),
    ("fd_1b_mc.py", "S2: the inputs not checked", '    if diff:\n        raise Refusal(f"the clip gate was read on other inputs',
     '    if False:\n        raise Refusal(f"the clip gate was read on other inputs', MC),
    ("fd_1b_mc.py", "S2: no calibration needed", '    if not g.get("calibration_sha256"):', '    if False:', MC),
    ("fd_1b_mc.py", "S2: the pre-gate set takes every toy",
     '    out |= {(t, "central", "T") for t in TRUTHS}',
     '    out |= {(t, "central", "T") for t in TRUTHS} | {(t, "toy", str(s)) for t in TRUTHS for s in TOY_SEEDS[t]}', MC),
    # ---- fd_1b_c2: #724, the reading, the law, the truth, the calibration, c2check
    ("fd_1b_c2.py", "724(i): two cells already stop", '    out["i"] = out["cells_beyond"] <= GATE_K', '    out["i"] = out["cells_beyond"] < GATE_K', C2),
    ("fd_1b_c2.py", "724(i): exactly 0.20 counts as beyond", '"cells_beyond": int(np.sum(dev > GATE_DEV))', '"cells_beyond": int(np.sum(dev >= GATE_DEV))', C2),
    ("fd_1b_c2.py", "724(ii): at the bound stops", '    out["ii"] = abs(out["mean_log"]) <= GATE_LOGMEAN', '    out["ii"] = abs(out["mean_log"]) < GATE_LOGMEAN', C2),
    ("fd_1b_c2.py", "724(ii): one-sided", '    out["ii"] = abs(out["mean_log"]) <= GATE_LOGMEAN', '    out["ii"] = out["mean_log"] <= GATE_LOGMEAN', C2),
    ("fd_1b_c2.py", "724(iii): at the bound stops", '    out["iii"] = out["max_dev"] <= GATE_MAX', '    out["iii"] = out["max_dev"] < GATE_MAX', C2),
    ("fd_1b_c2.py", "724: passes without (iii)", '    out["passes"] = bool(out["i"] and out["ii"] and out["iii"])', '    out["passes"] = bool(out["i"] and out["ii"])', C2),
    ("fd_1b_c2.py", "724: passes without (ii)", '    out["passes"] = bool(out["i"] and out["ii"] and out["iii"])', '    out["passes"] = bool(out["i"] and out["iii"])', C2),
    ("fd_1b_c2.py", "724: k = 3", "GATE_K, GATE_DEV, GATE_LOGMEAN, GATE_MAX = 2, 0.20, 0.07, 0.35", "GATE_K, GATE_DEV, GATE_LOGMEAN, GATE_MAX = 3, 0.20, 0.07, 0.35", C2),
    ("fd_1b_c2.py", "724: a non-finite ratio accepted", "    if r.shape != (N_CELLS,) or not np.all(np.isfinite(r)) or np.any(r <= 0):",
     "    if r.shape != (N_CELLS,):", C2),
    ("fd_1b_c2.py", "reading: q1 without the clipped gate", '                 and gate[CLIPPED])\n        pos', '                 and True)\n        pos', C2),
    ("fd_1b_c2.py", "reading: 1B's gate on the clipped ratio is C2's", 'GATES_1B = {CLIPPED: lambda v: gate_724(v)["passes"],',
     'GATES_1B = {CLIPPED: c2_gate,', C2),
    ("fd_1b_c2.py", "law: the flux band uniform", "        p = (w_flux / w_flux.sum()) if b == flux else np.full(n, 1.0 / n)",
     "        p = np.full(n, 1.0 / n)", C2),
    ("fd_1b_c2.py", "truth: the completeness inverted (packed)", "    comp[nz] = B[nz] / D[nz]\n    denom = comp * np.asarray(flux, float)[:, pack[\"pt\"]]",
     "    comp[nz] = D[nz] / B[nz]\n    denom = comp * np.asarray(flux, float)[:, pack[\"pt\"]]", C2 + E2E),
    ("fd_1b_c2.py", "law: first order subtracts k CVs", "    k = S.sum(axis=1, keepdims=True) - 1.0\n    return",
     "    k = S.sum(axis=1, keepdims=True)\n    return", C2),
    ("fd_1b_c2.py", "law: two flux universes accepted", "    if not np.all(F.sum(axis=1) == 1):", "    if False:", C2),
    ("fd_1b_c2.py", "streams: CAL_SALT 0 accepted", "    if CAL_SALT == 0:\n        raise Refusal", "    if False:\n        raise Refusal", C2),
    ("fd_1b_c2.py", "rates: (b) not from gate_724", '        b = {k: np.array([not x[k] for x in g]) for k in ("i", "ii", "iii")}',
     '        b = {"i": np.sum(dev > GATE_DEV, axis=1) > GATE_K, "ii": np.abs(ml) >= GATE_LOGMEAN, "iii": mx > GATE_MAX}', C2),
    ("fd_1b_c2.py", "rates: to Joseph on (c)", '    out["to_joseph"] = out["over_truths_b"]["union_per_replicate"] > UNION_LIMIT',
     '    out["to_joseph"] = out["over_truths_c"]["union_per_replicate"] > UNION_LIMIT', C2),
    ("fd_1b_c2.py", "rates: (c)(ii) at the fixed threshold", "        thr_ii = SD_MULT_LOGMEAN * sd_ml", "        thr_ii = GATE_LOGMEAN", C2),
    ("fd_1b_c2.py", "control: z bound 40", "CONTROL_Z = 4.0 ", "CONTROL_Z = 40.0 ", C2),
    ("fd_1b_c2.py", "linearisation: no tolerance", '"holds": bool(np.all(np.abs(m) <= LINEARISATION_TOL))}', '"holds": True}', C2),
    ("fd_1b_c2.py", "calibration: the linearisation verdict dropped",
     '"LINEARISATION_TO_DIRECTOR" if not lin["holds"] else', '"LINEARISATION_TO_DIRECTOR" if False else', C2),
    ("fd_1b_c2.py", "prepare: a detector denominator off the CV's accepted",
     "    if det_differs:\n        raise Refusal(f\"detector denominators differ", "    if False:\n        raise Refusal(f\"detector denominators differ", C2),
    ("fd_1b_c2.py", "prepare: without the CV's tdw",
     '    if world.get("tdw_cv") is None:\n        raise Refusal("the calibration and c2check need', '    if False:\n        raise Refusal("the calibration and c2check need', C2 + E2E),
    ("fd_1b_c2.py", "prepare: (e2)'s d_CV not applied", '    cv["D"] = d_cv\n', '    pass\n', C2 + E2E),
    ("fd_1b_c2.py", "c2check: an uncalibrated calibration accepted",
     '    if cal.get("schema") != SCHEMA_CAL or cal.get("verdict") != "CALIBRATED":', '    if False:', E2E),
    ("fd_1b_c2.py", "c2check: another calibration's single_x accepted",
     '            if not np.array_equal(z[f"single_x_{t}"], P["single_x"][t]):', '            if False:', E2E),
    ("fd_1b_c2.py", "c2check: PASS on any reading", '    verdict = "PASS" if all(v == "option (1)" for v in reads.values()) else "STOP"',
     '    verdict = "PASS"', E2E),
    ("fd_1b_c2.py", "c2_truth: the truth clip on lambda", '            wtp = np.where(wt * r < 0, 0.0, wt)', '            wtp = np.where(lam < 0, 0.0, wt)', C2),
    ("fd_1b_c2.py", "c2_truth: no denominator clip", '            Dp = np.where(m_den > 0, Dc + m_den, Dc)', '            Dp = Dc', C2),
    ("fd_1b_c2.py", "c2_block: R adds m_all", '        o_1 = o_a - q["m_all"] / q["N"]', '        o_1 = o_a + q["m_all"] / q["N"]', E2E),
    ("fd_1b_c2.py", "c2_block: the clipped ratio is first order's", '              CLIPPED: np.var(q["Nc"], axis=1, ddof=1) / ref_x,',
     '              CLIPPED: np.var(q["N"], axis=1, ddof=1) / ref_x,', C2 + E2E),
    # ---- fd_1b_cvdenom: the gates and B's attribution rule
    ("fd_1b_cvdenom.py", "cvd: the npz's rows without the extras gate", "    return base & ps, base & extras & ps", "    return base & ps, base & ps", CVD),
    ("fd_1b_cvdenom.py", "cvd: w = 1e4 kept", "(w >= 0) & (w < W_MAX)", "(w >= 0) & (w <= W_MAX)", CVD),
    ("fd_1b_cvdenom.py", "cvd: A without NaN equality", "np.asarray(t, np.float32), equal_nan=True)", "np.asarray(t, np.float32))", CVD),
    ("fd_1b_cvdenom.py", "cvd: (a) any move accepted", "        one_stride = on_grid & (np.abs(u32 - u64).sum(axis=0) == 1)", "        one_stride = on_grid", CVD),
    ("fd_1b_cvdenom.py", "cvd: (b) not checked", "    b_ok = bool(np.all(resid[bad] <= bound[bad]) and np.all(resid[touched] <= bound[touched]))", "    b_ok = True", CVD),
    ("fd_1b_cvdenom.py", "cvd: (c) not checked", "    c_ok = untouched.size == 0", "    c_ok = True", CVD),
    ("fd_1b_cvdenom.py", "cvd: usable without C", '                  and rec["C_npz_writer_reproduced"] and rec["D_all_equal"])', '                  and rec["D_all_equal"])', CVD),
    ("fd_1b_cvdenom.py", "cvd: usable without D", '                  and rec["C_npz_writer_reproduced"] and rec["D_all_equal"])', '                  and rec["C_npz_writer_reproduced"])', CVD),
    # ---- fd_1b_binning: the two identities
    ("fd_1b_binning.py", "bin: bound - e2 without the detectors", "    return ((len(tags) - 1) - n_det) * dcv", "    return (len(tags) - 1) * dcv", BIN),
    ("fd_1b_binning.py", "bin: e2 - f64 lets a detector bring a universe row", "        vals = [rows_u[t][j] if t in rows_u else w_cv for t in tags]",
     "        vals = [rows_u[t][j] if t in rows_u else 0.0 for t in tags]", BIN),
    ("fd_1b_binning.py", "bin: Delta_CV sign", "        d[c32] += w\n        d[c64] -= w\n    return d", "        d[c32] -= w\n        d[c64] += w\n    return d", BIN),
]


def purge():
    for d in (Path("__pycache__"), Path("tests/__pycache__")):
        shutil.rmtree(d, ignore_errors=True)


def run(tests) -> int:
    purge()
    return subprocess.run(PYTEST + list(tests), capture_output=True, text=True, env=ENV).returncode


files = {f: Path(f).read_text() for f in ("fd_1b_mc.py", "fd_1b_c2.py", "fd_1b_cvdenom.py", "fd_1b_binning.py")}
for p in list(files) + [t for ts in (MC, C2, CVD, BIN, E2E) for t in ts]:
    print(f"sha256 {hashlib.sha256(Path(p).read_bytes()).hexdigest()}  {p}")
print("KILLED means the suites exit 1 (a test failed); any other non-zero exit is ERROR, not a kill")
plan = []
for name, old, new in CARRIED:
    if name in REANCHOR:
        assert old.count(U_OLD) == 1, name
        old, new = old.replace(U_OLD, U_NEW), new.replace(U_OLD, U_NEW)
    if name == "G: the clip gate never checked":
        assert old == GATE_OLD, name
        old, new = GATE_NEW, "    pass                                      # after the role checks"
    plan.append(("fd_1b_mc.py", name, old, new, MC, name in REPLACED_A2 | REPLACED_A21))
plan += [(f, n, o, w, t, False) for f, n, o, w, t in NEW]
for f, name, old, new, tests, replaced in plan:                      # every anchor, before anything runs
    c = files[f].count(old)
    assert (c == 0) if replaced else (c == 1), f"{name}: its target occurs {c} times in {f}"
print(f"plan: {len(plan)} mutants, {sum(r for *_, r in plan)} not applicable; every anchor occurs as required")
if "--check" in sys.argv:
    sys.exit(0)
rows = []
try:
    for f, name, old, new, tests, replaced in plan:
        if name in EQUIVALENT:
            rows.append((name, "EQUIVALENT"))
            print(f"EQUIV    {name}  (equivalent on every input; its proof is a test)", flush=True)
            continue
        if replaced:
            rows.append((name, "N/A"))
            print(f"N/A      {name}  (its target code was replaced: amendment 2 or A2.1)", flush=True)
            continue
        Path(f).write_text(files[f].replace(old, new))
        rc = run(tests)
        Path(f).write_text(files[f])
        state = "KILLED" if rc == 1 else "SURVIVED" if rc == 0 else f"ERROR rc={rc}"
        rows.append((name, state))
        print(f"{state:8s} {name}{'  [re-anchored]' if name in REANCHOR else ''}", flush=True)
finally:
    for f, text in files.items():
        Path(f).write_text(text)
purge()
r = subprocess.run([sys.executable, "-B", "-m", "pytest", "-p", "no:cacheprovider", "-q"] +
                   list(MC + C2 + CVD + BIN + E2E), capture_output=True, text=True, env=ENV)
print("unmutated:", r.stdout.strip().splitlines()[-1])
applicable = [k for _, k in rows if k not in ("N/A", "EQUIVALENT")]
print(f"{sum(1 for k in applicable if k == 'KILLED')} of {len(applicable)} applicable killed; "
      f"{sum(1 for _, k in rows if k == 'N/A')} not applicable; {sum(1 for _, k in rows if k == 'EQUIVALENT')} "
      f"equivalent (proved by a test); {len(rows)} in all")
