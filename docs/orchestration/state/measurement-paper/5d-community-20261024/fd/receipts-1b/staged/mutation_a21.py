"""Mutation receipt for addendum A2.1 (FD-1B-STAGED-ADDENDUM-A2-1.md), over fd_1b_mc, fd_1b_c2, fd_1b_cvdenom and
fd_1b_binning. Amendment 2's mutants (mutation_mc_a2.py's M, read from that file, not retyped) are carried against
fd_1b_mc with its suite; those whose target A2.1 replaced are printed NOT APPLICABLE, by name; two whose target
A2.1 rewrote (the U checks, now through same_functional) are re-anchored. A2.1's own mutants follow, each with the
suites that must kill it. Run from nd-unfolding/ with TMPDIR set:

    python3 ../docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/mutation_a21.py

KILLED means the suites exit 1 (a test failed); any other non-zero exit is ERROR, not a kill. Bytecode-free, with a
fixed hash seed, as mutation_mc_a2.py. The unmutated suites run first and again last; a red first run stops before
any mutant (exit 3). The harness exits 1 unless every applicable mutant is killed and the last control passes.
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
TAB = ("tests/test_fd_1b_tables.py",)
GEN = "../docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/stage1/tables/make_stage1_tables.py"


def literal(path: Path, name: str):
    t = ast.parse(path.read_text())
    return next(ast.literal_eval(n.value) for n in t.body if isinstance(n, ast.Assign)
                and getattr(n.targets[0], "id", "") == name)


CARRIED = literal(HERE / "mutation_mc_a2.py", "M")
REPLACED_A2 = literal(HERE / "mutation_mc_a2.py", "REPLACED")
REPLACED_A21 = {"A2c: the nature rule keeps the truth", "A2c: the nature rule ignores negative truths",   # S3
                "G: the clip gate always open", "G: the clip gate reads anything",                     # S2
                "C4: the clipping readout under nature"}   # the director's ruling (iii): its converse is below
U_OLD = '    if not np.allclose(U, s1["U"], rtol=0, atol=1e-6):\n        raise Refusal("the definition\'s functional is not S1\'s")\n'
U_NEW = '    if not same_functional(U, s1["U"]):\n        raise Refusal("the definition\'s functional is not S1\'s")\n'
REANCHOR = {"B1 (audit): null U check dropped", "B3: readout U check dropped"}
GATE_OLD = "    inv.OPENED.clear()\n    check_clip_gate(a)"           # A2.1 moved the call after the role checks
# clipping_readout_nature and resume_matches repeat three lines amendment 2's mutants target, so those mutants are
# anchored on the 'data' path's or the meta's own preceding text (the nature path's have their own mutants below)
CM_REANCHOR = {"A2: two clipmean products accepted": '    cm = sorted(unfolds.glob(f"{tag}_{truth}_clipmean_*.npz"))\n',
               "A2: clipped fraction over the wrong total": '            tot = rec[comp]["sum_lambda"]\n',
               "A2e: the meta records the fixed config": '"item": item, '}
GATE_NEW = "    check_clip_gate(a)                        # after the role checks"
# Each equivalent mutant with its scope and the test that proves it (the audit's W1 at c00e9b4a: one label for both
# overstated the second). (i)'s > and >= agree on every input, since no double r has |r - 1| == 0.20. The lane cap is
# equivalent on the declared inputs only: 1,054 and 1,581 items need 6 and 9 nodes at 22 or 23 per lane, and the
# round-robin then puts at most 22 in a lane either way; the cap matters only for a larger table.
EQUIVALENT = {
    "724(i): exactly 0.20 counts as beyond":
        "on every input; test_fd_1b_c2 Gate.test_i_at_exactly_0_20_is_unreachable",
    "tables: 23 per lane":
        "on the declared inputs only; test_fd_1b_tables Tables.test_the_lane_cap_has_no_effect_on_the_declared_tables",
}

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
    ("fd_1b_mc.py", "S3: the denominator clipped under 'data' too",
     '    du = dict(ui, w_reco=np.where(neg, 0.0, w))\n    if rule == "nature":',
     '    du = dict(ui, w_reco=np.where(neg, 0.0, w))\n'
     '    if rule == "data" and "tdw_rows" in ui:\n'
     '        _c, _r = ui["td_cells"], np.asarray(ui["tdw_rows"], float)\n'
     '        _k = (_c >= 0) & (_r < 0)\n'
     '        _m = np.bincount(_c[_k], weights=-_r[_k], minlength=int(np.prod(np.shape(ui["denom_nd"]))))\n'
     '        du = dict(du, denom_nd=np.asarray(ui["denom_nd"], float) + _m.reshape(np.shape(ui["denom_nd"])))\n'
     '    if rule == "nature":', MC + E2E),
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
     '        if not (np.all(np.isfinite(tdw_cv)) and np.all(tdw_cv >= 0)):', '        if False:', MC + E2E),   # its test is e2e's
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
    # ---- fd_1b_mc: H1, the declared digest from the pins file (the director's ruling on the audit's H1)
    ("fd_1b_mc.py", "H1: the digest read from a hashed file", 'GATE_PIN = _ND.parent / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/a2-1/BOUND_GATE.sha256"',
     'GATE_PIN = _ND / "fd_1b_c2.py"', MC),
    ("fd_1b_mc.py", "H1: the pins file never compared", "    if a.expect_clip_gate_sha256 != bound:\n        raise Refusal(\"the clip gate is not",
     "    if False:\n        raise Refusal(\"the clip gate is not", MC),
    ("fd_1b_mc.py", "H1: a missing pins file not refused", "    if not GATE_PIN.exists():\n        raise Refusal(",
     "    if False:\n        raise Refusal(", MC),
    ("fd_1b_mc.py", "H1: a pins file of any length", '    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text) or raw.decode().count("\\n") > 1:',
     '    if any(ch not in "0123456789abcdef" for ch in text) or raw.decode().count("\\n") > 1:', MC),
    ("fd_1b_mc.py", "H1: a pins file of any characters", '    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text) or raw.decode().count("\\n") > 1:',
     '    if len(text) != 64 or raw.decode().count("\\n") > 1:', MC),
    ("fd_1b_mc.py", "H1: a pins file of several lines", '    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text) or raw.decode().count("\\n") > 1:',
     '    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text):', MC),
    ("fd_1b_mc.py", "H1: the pins blob not recorded", "    a.gate_pin_blob = blob ", "    a.gate_pin_blob = None ", MC),
    ("fd_1b_mc.py", "H1: the pins blob over the stripped text", '    blob = hashlib.sha1(b"blob %d\\0" % len(raw) + raw).hexdigest()',
     '    blob = hashlib.sha1(b"blob %d\\0" % len(text) + text.encode()).hexdigest()', MC),
    # ---- fd_1b_c2: #724, the reading, the law, the truth, the calibration, c2check
    ("fd_1b_c2.py", "724(i): two cells already stop", '    out["i"] = out["cells_beyond"] <= GATE_K', '    out["i"] = out["cells_beyond"] < GATE_K', C2),
    ("fd_1b_c2.py", "724(i): exactly 0.20 counts as beyond", '"cells_beyond": int(np.sum(dev > GATE_DEV))', '"cells_beyond": int(np.sum(dev >= GATE_DEV))', C2),
    ("fd_1b_c2.py", "724(ii): at the bound stops", '    out["ii"] = abs(out["mean_log"]) <= GATE_LOGMEAN', '    out["ii"] = abs(out["mean_log"]) < GATE_LOGMEAN', C2),
    ("fd_1b_c2.py", "724(ii): one-sided", '    out["ii"] = abs(out["mean_log"]) <= GATE_LOGMEAN', '    out["ii"] = out["mean_log"] <= GATE_LOGMEAN', C2),
    ("fd_1b_c2.py", "724(iii): at the bound stops", '    out["iii"] = out["max_dev"] <= GATE_MAX', '    out["iii"] = out["max_dev"] < GATE_MAX', C2),
    ("fd_1b_c2.py", "724: passes without (iii)", '    out["iii"] = out["max_dev"] <= GATE_MAX\n' + '    out["passes"] = bool(out["i"] and out["ii"] and out["iii"])', '    out["iii"] = out["max_dev"] <= GATE_MAX\n    out["passes"] = bool(out["i"] and out["ii"])', C2),
    ("fd_1b_c2.py", "724: passes without (ii)", '    out["iii"] = out["max_dev"] <= GATE_MAX\n' + '    out["passes"] = bool(out["i"] and out["ii"] and out["iii"])', '    out["iii"] = out["max_dev"] <= GATE_MAX\n    out["passes"] = bool(out["i"] and out["iii"])', C2),
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
    ("fd_1b_c2.py", "c2check: PASS on any reading", '    verdict = "PASS" if all(v == "option (1)" for v in reads.values()) and all(b["passes"] for b in back.values()) \\',
     '    verdict = "PASS" if all(b["passes"] for b in back.values()) \\', C2 + E2E),
    ("fd_1b_c2.py", "c2check: PASS without the backstop", '    verdict = "PASS" if all(v == "option (1)" for v in reads.values()) and all(b["passes"] for b in back.values()) \\',
     '    verdict = "PASS" if all(v == "option (1)" for v in reads.values()) \\', C2 + E2E),
    ("fd_1b_c2.py", "c2check: the first 300 not compared", '            if not np.array_equal(qn[k][:, :v.shape[1]], v):',
     '            if False:', C2 + E2E),
    ("fd_1b_c2.py", "c2check: the clipped ratio read at #724's fixed gate", '{CLIPPED: lambda v, thr=thr: gate_n(v, thr)["passes"], "first_order": c2_gate,',
     '{CLIPPED: c2_gate, "first_order": c2_gate,', C2 + E2E),
    ("fd_1b_c2.py", "c2check: another truth's thresholds", '        thr = cal["rule"]["thresholds"][t]', '        thr = cal["rule"]["thresholds"][truths[0]]', C2 + E2E),
    ("fd_1b_c2.py", "c2_truth: the truth clip on lambda", '            wtp = np.where(wt * r < 0, 0.0, wt)', '            wtp = np.where(lam < 0, 0.0, wt)', C2),
    ("fd_1b_c2.py", "c2_truth: no denominator clip", '            Dp = np.where(m_den > 0, Dc + m_den, Dc)', '            Dp = Dc', C2),
    ("fd_1b_c2.py", "c2_block: R adds m_all", '        o_1 = o_a - q["m_all"] / q["N"]', '        o_1 = o_a + q["m_all"] / q["N"]', C2 + E2E),   # its test is c2's
    ("fd_1b_c2.py", "c2_block: the clipped ratio is first order's", '              CLIPPED: np.var(q["Nc"], axis=1, ddof=1) / ref_x,',
     '              CLIPPED: np.var(q["N"], axis=1, ddof=1) / ref_x,', C2 + E2E),
    # ---- fd_1b_mc: H2, the bound gate's re-verified calibration, backstop and config hash
    ("fd_1b_mc.py", "H2: any calibration verdict", '    if cal.get("verdict") != "CALIBRATED" or cal.get("sha256")',
     '    if False or cal.get("sha256")', MC),
    ("fd_1b_mc.py", "H2: the calibration not the one named", ' or cal.get("sha256") != g["calibration_sha256"]:', ':', MC),
    ("fd_1b_mc.py", "H2: a projected union accepted", '    if not cal.get("three_truths_measured") or cal.get("union")',
     '    if cal.get("union")', MC),
    ("fd_1b_mc.py", "H2: the union not bounded", ' or cal["union"] > fd_1b_c2.UNION_LIMIT:', ':', MC),
    ("fd_1b_mc.py", "H2: the power not required", '    if not cal.get("power_meets"):', '    if False:', MC),
    ("fd_1b_mc.py", "H2: the backstop not required", '    if a.truth not in back or not all(', '    if False and not all(', MC),
    ("fd_1b_mc.py", "H2: the config hash not checked", '    if g.get("config_hash") != fd_1b_c2.config_hash(', '    if False and fd_1b_c2.config_hash(', MC),
    # ---- fd_1b_mc: the resume check and the readout's clipping section under 'nature' (the director's rulings on the
    # audit's finding on ruling (A))
    ("fd_1b_mc.py", "resume: an existing product skipped unchecked", "            resume_matches(target, a)\n            continue",
     "            continue", MC),
    ("fd_1b_mc.py", "resume: the clip rule not compared", '    want = {"config": a.estimator, "clip_rule": a.clip_rule, ',
     '    want = {"config": a.estimator, ', MC),
    ("fd_1b_mc.py", "resume: the estimator not compared", '    want = {"config": a.estimator, "clip_rule": a.clip_rule, ',
     '    want = {"clip_rule": a.clip_rule, ', MC),
    ("fd_1b_mc.py", "resume: the gate config hash not compared",
     '            "gate_config_hash": getattr(a, "gate_config_hash", None)}\n    diff = sorted(',
     '            }\n    diff = sorted(', MC),
    ("fd_1b_mc.py", "resume: the gate config hash not recorded",
     '                "gate_config_hash": getattr(a, "gate_config_hash", None),\n                "slurm_job"',
     '                "slurm_job"', MC),
    ("fd_1b_mc.py", "clipping: 'nature' refused (C4's refusal restored)",
     '    if clip_rule == "nature":\n        return clipping_readout_nature(',
     '    if clip_rule == "nature":\n        raise Refusal(NATURE_UNRULED)\n        return clipping_readout_nature(', MC),
    ("fd_1b_mc.py", "clipping (c): --data-unfolds not required 'data'",
     '    refuse_mixed_estimator(data_unfolds, tag, truth, estimator, "data")\n', '', MC),
    ("fd_1b_mc.py", "clipping (c): --data-unfolds may be the graded directory",
     '    if a.data_unfolds is not None and a.data_unfolds.resolve() == a.unfolds.resolve():',
     '    if False:', MC),
    ("fd_1b_mc.py", "clipping (b): the readout without the bound gate", '        return None\n    raw = read_bound_gate(a)',
     '        return None\n    raw = Path(a.clip_gate).read_bytes()', MC),
    ("fd_1b_mc.py", "clipping (c): two clipmean products accepted",
     '    cm = sorted(data_unfolds.glob(f"{tag}_{truth}_clipmean_*.npz"))\n    if len(cm) != 1:',
     '    cm = sorted(data_unfolds.glob(f"{tag}_{truth}_clipmean_*.npz"))\n    if len(cm) < 1:', MC),
    ("fd_1b_mc.py", "clipping (a): the clipped fraction over the wrong total",
     '            tot = rec[comp][key]\n            frac[comp].append(abs(rec[comp]["sum_negative"]) / tot if tot else 0.0)',
     '            tot = rec[comp][key]\n            frac[comp].append(abs(rec[comp]["sum_negative"]) if tot else 0.0)', MC),
    ("fd_1b_mc.py", "clipping (a): the toys' rule not checked", '        if rec.get("rule") != "nature":\n            raise Refusal(f"{p.name}: clip rule',
     '        if False:\n            raise Refusal(f"{p.name}: clip rule', MC),
    ("fd_1b_mc.py", "clipping (a): the denominator's fraction over the truth's total",
     '"denominator": "sum_rows", "truth": "sum_truth"}', '"denominator": "sum_rows", "truth": "sum_rows"}', MC),
    ("fd_1b_mc.py", "clipping (c): the graded central, not S1-0b's", '    xc = U @ np.asarray(np.load(data_unfolds / product_name(tag, truth, "central", "T"), allow_pickle=False)["xsec_flat"],',
     '    xc = U @ np.asarray(np.load(unfolds / product_name(tag, truth, "central", "T"), allow_pickle=False)["xsec_flat"],', MC),
    ("fd_1b_mc.py", "S3 arrays: the truth clip's array not stored", '                  **{k: clip[k] for k in NATURE_CLIP_ARRAYS if k in clip}}',
     '                  **{k: clip[k] for k in NATURE_CLIP_ARRAYS[1:] if k in clip}}', MC + E2E),
    ("fd_1b_mc.py", "S3 arrays: the truth clip on lambda's rows", '        clip["clip_truth_nature_flat"] = _flat_hist(ui["MCgen"][tz], -(wt * r)[tz], edges)',
     '        clip["clip_truth_nature_flat"] = _flat_hist(ui["MCgen"][tneg], -lam[tneg], edges)', MC + E2E),
    ("fd_1b_mc.py", "S3 arrays: the denominator's mass signed", '        clip["clip_denom_flat"] = m_den.ravel(order="C")',
     '        clip["clip_denom_flat"] = -m_den.ravel(order="C")', MC + E2E),
    # ---- fd_1b_c2: the large-sample gate (P1, P2, P4, P6)
    ("fd_1b_c2.py", "P1: the gate seeds shifted by one", '    return [int(x) for x in mc.TOY_SEEDS[truth]] + list(range(GATE_SEED_BASE[truth],',
     '    return [int(x) for x in mc.TOY_SEEDS[truth]] + list(range(GATE_SEED_BASE[truth] + 1,', C2),
    ("fd_1b_c2.py", "P1: the declared 300 not first", '    return [int(x) for x in mc.TOY_SEEDS[truth]] + list(range(GATE_SEED_BASE[truth],',
     '    return [int(x) for x in mc.TOY_SEEDS[truth]][::-1] + list(range(GATE_SEED_BASE[truth],', C2),
    ("fd_1b_c2.py", "P2: stops_at without (i)", '    return st["i"] | (np.abs(st["ml"])', '    return (np.abs(st["ml"])', C2),
    ("fd_1b_c2.py", "P2: stops_at without (iii)", ' | (np.max(z, axis=1) > s * SD_MULT_CELL)', '', C2),
    ("fd_1b_c2.py", "P2: (ii) at the cell multiple", '(np.abs(st["ml"]) > s * SD_MULT_LOGMEAN * sd_ml)', '(np.abs(st["ml"]) > s * SD_MULT_CELL * sd_ml)', C2),
    ("fd_1b_c2.py", "P2: (iii) at the mean-log multiple", '(np.max(z, axis=1) > s * SD_MULT_CELL)', '(np.max(z, axis=1) > s * SD_MULT_LOGMEAN)', C2),
    ("fd_1b_c2.py", "P2: the last s, not the first", '        if chosen is None and u <= UNION_LIMIT:', '        if u <= UNION_LIMIT:', C2),
    ("fd_1b_c2.py", "P2: the projection without the plug-in", '        return 1.0 - float(np.prod([1 - x for x in p])) * (1.0 - float(np.mean(p)))',
     '        return 1.0 - float(np.prod([1 - x for x in p]))', C2),
    ("fd_1b_c2.py", "P2: three truths as a product", '        if three:\n            n = min', '        if False:\n            n = min', C2),
    ("fd_1b_c2.py", "P2: the null SD over too few sets", '            "dev": np.abs(R - 1.0), "sd_ml": float(np.std([x["mean_log"] for x in g], ddof=1)),',
     '            "dev": np.abs(R - 1.0), "sd_ml": float(np.std([x["mean_log"] for x in g[:100]], ddof=1)),', C2),
    ("fd_1b_c2.py", "P4: a uniform inflation", '        uni = rate(r * (1.0 - UNIFORM_DEFLATION))', '        uni = rate(r * (1.0 + UNIFORM_DEFLATION))', C2),
    ("fd_1b_c2.py", "P4: power at the boundary fails", '"uniform_meets": bool(uni >= POWER_MIN)', '"uniform_meets": bool(uni > POWER_MIN)', C2),
    ("fd_1b_c2.py", "P4: one truth's power suffices", '    out["meets"] = all(v["uniform_meets"]', '    out["meets"] = any(v["uniform_meets"]', C2),
    ("fd_1b_c2.py", "P4: the verdict without power", '    if not power["meets"]:\n        return "POWER_SHORT', '    if False:\n        return "POWER_SHORT', C2),
    ("fd_1b_c2.py", "P2: the verdict without a threshold", '    if rule["s"] is None:\n        return', '    if False:\n        return', C2),
    ("fd_1b_c2.py", "P2: the verdict without (i) alone", '    if rule["i_alone_exceeds"]:\n        return', '    if False:\n        return', C2),
    ("fd_1b_c2.py", "gate_n: passes without (iii)", '           "ii": abs(g["mean_log"]) <= thr["ii_mean_log"], "iii": z <= thr["iii_alpha_multiple"]}\n    out["passes"] = bool(out["i"] and out["ii"] and out["iii"])',
     '           "ii": abs(g["mean_log"]) <= thr["ii_mean_log"], "iii": z <= thr["iii_alpha_multiple"]}\n    out["passes"] = bool(out["i"] and out["ii"])', C2 + E2E),
    ("fd_1b_c2.py", "gate_n: (ii) at the null SD, not the threshold", '"ii": abs(g["mean_log"]) <= thr["ii_mean_log"]', '"ii": abs(g["mean_log"]) <= thr["sd_mean_log"]', C2 + E2E),
    ("fd_1b_c2.py", "gate_n: (iii) one-sided", '    z = float(np.max(np.abs(r - 1.0) / sd_c))', '    z = float(np.max((r - 1.0) / sd_c))', C2 + E2E),
    ("fd_1b_c2.py", "P6: the backstop without (i)", '            "passes": bool(g["i"] and z <= BACKSTOP_SD_MULT)}', '            "passes": bool(z <= BACKSTOP_SD_MULT)}', C2 + E2E),
    ("fd_1b_c2.py", "P6: the backstop without (iii)", '            "passes": bool(g["i"] and z <= BACKSTOP_SD_MULT)}', '            "passes": bool(g["i"])}', C2 + E2E),
    ("fd_1b_c2.py", "P6: the config hash without the clip rule", '    doc = {"code": code, "inputs": inputs, "clip_rule": clip_rule,', '    doc = {"code": code, "inputs": inputs,', C2 + E2E),
    ("fd_1b_c2.py", "P6: the config hash without the toy seeds", '    return hashlib.sha256(json.dumps(doc, sort_keys=True).encode()).hexdigest()',
     '    doc.pop("toy_seeds")\n    return hashlib.sha256(json.dumps(doc, sort_keys=True).encode()).hexdigest()', C2 + E2E),
    # ---- the stage 1 tables generator: S2's bulk under 'nature' and the director's ruling (A)
    (GEN, "tables: the bulk without the pilot's graded items", "    bulk = [x for x in items if x[1] in mc.BULK_ROLES]\n",
     "    bulk = [x for x in items if x[1] in mc.BULK_ROLES and x not in set(pilot) | set(pilot_b)]\n", TAB),
    (GEN, "tables: the bulk keeps clipmean", "    bulk = [x for x in items if x[1] in mc.BULK_ROLES]\n",
     "    bulk = [x for x in items if x[1] in mc.BULK_ROLES + ('clipmean',)]\n", TAB),
    (GEN, "tables: nature steps without the gate", ' + (gate if rule == "nature" else []))', ')', TAB),
    (GEN, "tables: no CV tdw", '              "--cv-tdw", CV_TDW, "--expect-cv-tdw-sha256", CV_TDW_SHA256,\n', '', TAB),
    (GEN, "tables: the pins file not required committed", "    if head.returncode != 0 or head.stdout.strip() != blob:\n",
     "    if False:\n", TAB),
    (GEN, "tables: the gate sha not compared", "        if a.expect_clip_gate_sha256 != committed_gate_sha(mc, co):\n",
     "        if False:\n", TAB),
    (GEN, "tables: the bulk under data", '        tables("s1-bulk", lanes, "nature")', '        tables("s1-bulk", lanes, "data")', TAB),
    (GEN, "tables: S1-0 under nature", '    tables("s1-0", [[x] for x in pilot], "data")', '    tables("s1-0", [[x] for x in pilot], "nature")', TAB),
    (GEN, "tables: one unfolds directory for both rules", '    return f"{W}/stage1/unf/{rule}-{estimator}"',
     '    return f"{W}/stage1/unf"', TAB),
    (GEN, "tables: the directory without the estimator", '    return f"{W}/stage1/unf/{rule}-{estimator}"',
     '    return f"{W}/stage1/unf/{rule}"', TAB),
    (GEN, "tables: 23 per lane", "LANES, PER_LANE = 8, 22", "LANES, PER_LANE = 8, 23", TAB),
    # ---- fd_1b_c2: ruling (a), the hoisted multiplicative, one truth per job and the merge (each with its killer)
    ("fd_1b_c2.py", "mult: every Z pair floors", '        d, k = np.nonzero(S[:, T["zu"]] > 0)', '        d, k = np.nonzero(S[:, T["zu"]] >= 0)', C2),
    ("fd_1b_c2.py", "mult: no sparse floor", '    if T["zu"].size:\n        d, k', '    if False:\n        d, k', C2),
    ("fd_1b_c2.py", "mult: the floor on the universe, not the row", '        floored[d, T["zrow"][k]] = True',
     '        floored[d, T["zu"][k]] = True', C2),
    ("fd_1b_c2.py", "mult: L without the CV's log", ' - lcv[None], 0.0)', ', 0.0)', C2),
    ("fd_1b_c2.py", "mult: Z without the CV's sign", '    zu, zrow = np.nonzero(pos[None] & (V <= 0))',
     '    zu, zrow = np.nonzero(V < 0)', C2),
    ("fd_1b_c2.py", "c2_truth: a negative selection accepted", '    if np.any(S < 0):\n        raise Refusal("a selection',
     '    if False:\n        raise Refusal("a selection', C2),
    ("fd_1b_c2.py", "c2check: truths outside the calibration's", '    if not truths or not set(truths) <= set(cal["truths"]):',
     '    if not truths:', E2E),
    ("fd_1b_c2.py", "c2check: threads not recorded",
     '"r_negative": P["r_neg"],\n            "threads": {k: os.environ.get(k) for k in THREAD_VARS},\n', '"r_negative": P["r_neg"],\n', E2E),
    ("fd_1b_c2.py", "merge: one part accepted", '    if len(parts) < 2:', '    if len(parts) < 1:', E2E),
    ("fd_1b_c2.py", "merge: the shared fields not compared", '    for k in MERGE_SAME:\n        if any(p.get(k) != first.get(k) for p in parts):',
     '    for k in ():\n        if any(p.get(k) != first.get(k) for p in parts):', E2E),
    ("fd_1b_c2.py", "merge: (vi) not compared", '    if any(p["record"]["vi"] != first["record"]["vi"] for p in parts):', '    if False:', E2E),
    ("fd_1b_c2.py", "merge: a truth in two parts", '    if len(named) != len(set(named)):', '    if False:', E2E),
    ("fd_1b_c2.py", "merge: the verdict without the backstop",
     '    g["verdict"] = "PASS" if all(v == "option (1)" for v in reads.values()) and all(b["passes"] for b in back.values()) \\\n',
     '    g["verdict"] = "PASS" if all(v == "option (1)" for v in reads.values()) \\\n', E2E),
    ("fd_1b_c2.py", "merge: the verdict without the readings",
     '    g["verdict"] = "PASS" if all(v == "option (1)" for v in reads.values()) and all(b["passes"] for b in back.values()) \\\n',
     '    g["verdict"] = "PASS" if all(b["passes"] for b in back.values()) \\\n', E2E),
    ("fd_1b_c2.py", "merge: truths in part order", '    truths = [t for t in mc.TRUTHS if t in named]', '    truths = list(named)', E2E),
    ("fd_1b_c2.py", "merge: a part's digest not checked", '            if hashlib.sha256(raw).hexdigest() != sha:\n                raise Refusal(f"{path}: its digest',
     '            if False:\n                raise Refusal(f"{path}: its digest', E2E),
    ("fd_1b_c2.py", "probe: the projection without prepare", '"projected_seconds_per_truth": t_prep + blocks_per_truth * mean,',
     '"projected_seconds_per_truth": blocks_per_truth * mean,', E2E),
    ("fd_1b_c2.py", "probe: the first block's one-off costs kept", '    mean = float(np.mean(per_block[1:] if len(per_block) > 1 else per_block))',
     '    mean = float(np.mean(per_block))', E2E),
    ("fd_1b_c2.py", "probe: two truths timed as one", '    if len(a.truths) != 1:\n        raise Refusal("the probe times one truth")',
     '    if False:\n        raise Refusal("the probe times one truth")', E2E),
    ("fd_1b_mc.py", "H2: any gate sample", '    if gs.get("n") != fd_1b_c2.GATE_N or gs.get("first_300_bitwise") is not True:', '    if False:', MC),
    ("fd_1b_mc.py", "H2: the gate sample's first 300 not required", ' or gs.get("first_300_bitwise") is not True:', ':', MC),
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


files = {f: Path(f).read_text() for f in ("fd_1b_mc.py", "fd_1b_c2.py", "fd_1b_cvdenom.py", "fd_1b_binning.py", GEN)}
for p in list(files) + [t for ts in (MC, C2, CVD, BIN, E2E, TAB) for t in ts]:
    print(f"sha256 {hashlib.sha256(Path(p).read_bytes()).hexdigest()}  {p}")
print("KILLED means the suites exit 1 (a test failed); any other non-zero exit is ERROR, not a kill")
plan = []
for name, old, new in CARRIED:
    if name in REANCHOR:
        assert old.count(U_OLD) == 1, name
        old, new = old.replace(U_OLD, U_NEW), new.replace(U_OLD, U_NEW)
    if name in CM_REANCHOR:
        old, new = CM_REANCHOR[name] + old, CM_REANCHOR[name] + new
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
SUITES = list(MC + C2 + CVD + BIN + E2E + TAB)
purge()                                    # the unmutated control first: a red baseline would read every mutant KILLED
r = subprocess.run([sys.executable, "-B", "-m", "pytest", "-p", "no:cacheprovider", "-q"] + SUITES,
                   capture_output=True, text=True, env=ENV)
print("unmutated:", r.stdout.strip().splitlines()[-1], flush=True)
if r.returncode != 0:
    print(f"STOP: the unmutated suites exit {r.returncode}; no mutant is run")
    sys.exit(3)
rows = []
try:
    for f, name, old, new, tests, replaced in plan:
        if name in EQUIVALENT:
            rows.append((name, "EQUIVALENT"))
            print(f"EQUIV    {name}  (equivalent {EQUIVALENT[name]})", flush=True)
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
        print(f"{state:8s} {name}{'  [re-anchored]' if name in REANCHOR | set(CM_REANCHOR) else ''}", flush=True)
finally:
    for f, text in files.items():
        Path(f).write_text(text)
purge()
r = subprocess.run([sys.executable, "-B", "-m", "pytest", "-p", "no:cacheprovider", "-q"] + SUITES,
                   capture_output=True, text=True, env=ENV)
print("unmutated, after:", r.stdout.strip().splitlines()[-1])
applicable = [k for _, k in rows if k not in ("N/A", "EQUIVALENT")]
killed = sum(1 for k in applicable if k == "KILLED")
print(f"{killed} of {len(applicable)} applicable killed; "
      f"{sum(1 for _, k in rows if k == 'N/A')} not applicable; {sum(1 for _, k in rows if k == 'EQUIVALENT')} "
      f"equivalent (each with its scope and proving test); {len(rows)} in all")
sys.exit(0 if killed == len(applicable) and r.returncode == 0 else 1)   # a survivor, an ERROR or a red control fails
