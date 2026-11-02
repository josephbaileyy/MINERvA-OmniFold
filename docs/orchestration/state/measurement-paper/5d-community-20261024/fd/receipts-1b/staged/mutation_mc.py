"""Mutation receipt for nd-unfolding/fd_1b_mc.py (stage 1's code, for binding 2). Run from nd-unfolding/ with TMPDIR set:

    python3 ../docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/mutation_mc.py

KILLED means the suite exits 1 (a test failed); any other non-zero exit is ERROR, not a kill.
"""
import hashlib, subprocess, sys
from pathlib import Path
src, tests = Path("fd_1b_mc.py"), Path("tests/test_fd_1b_mc.py")
orig = src.read_text()
for p in (src, tests, Path("fd_1b_null.py")):
    print(f"sha256 {hashlib.sha256(p.read_bytes()).hexdigest()}  {p}")
print("KILLED means the suite exits 1 (a test failed); any other non-zero exit is ERROR, not a kill")
M = [
 ("ratio composition inverted", "acc[k][m] = acc[k][m] * (a_u[m] / cv[k][m])", "acc[k][m] = acc[k][m] * (cv[k][m] / a_u[m])"),
 ("zero-CV rows not added", "acc[k][~m] = acc[k][~m] + a_u[~m]", "acc[k][~m] = acc[k][~m]"),
 ("negatives clipped", 'ui["w_truth"], ui["w_reco"], ui["denom_nd"] = acc["wt"], acc["wr"], acc["denom"]', 'ui["w_truth"], ui["w_reco"], ui["denom_nd"] = np.clip(acc["wt"], 0, None), acc["wr"], acc["denom"]'),
 ("denominator not composed", 'ui["w_truth"], ui["w_reco"], ui["denom_nd"] = acc["wt"], acc["wr"], acc["denom"]', 'ui["w_truth"], ui["w_reco"] = acc["wt"], acc["wr"]'),
 ("first universe not copied", "acc[k], peak[k] = a_u.copy(), np.abs(a_u)", "acc[k], peak[k] = cv[k].copy(), np.abs(a_u)"),
 ("two flux universes allowed", "    if len(fluxes) > 1:\n        raise Refusal", "    if False:\n        raise Refusal"),
 ("flux universe keeps CV flux", 'ui["flux"] = np.asarray(flux[int(idx)], float)', 'ui["flux"] = np.asarray(inputs["flux"], float)'),
 ("with_mc leaves the nature's flux", '    out["flux"] = ui["flux"]\n    return out', '    return out'),
 ("toy unfolds with the nature MC", "    exp = with_mc(exp, inputs, bkg)\n    return toys.mc_template_streams", "    return toys.mc_template_streams"),
 ("toy without streams", "    return toys.mc_template_streams(exp, seed), x_true", "    return exp, x_true"),
 ("stat jitter offset 0", "s5p_numerics.jittered(inputs, bkg, JITTER_OFFSET + b)", "s5p_numerics.jittered(inputs, bkg, b)"),
 ("stat replica not bootstrapped", "    return s5n_pseudo.bootstrap_replica(exp, b)", "    return exp"),
 ("plugin r off truth rows", "        r[m] = push", "        r[:push.size] = push"),
 ("capture keeps a view", "self.push = np.array(push, copy=True)", "self.push = push"),
 ("capture wrap not removed", "            s5c_unfold.onc.omnifold_loop = orig\n", "            pass\n"),
 ("ratio digest unchecked", "    if got != toys.committed_ratio_sha256(name):", "    if False:"),
 ("role pairing unchecked", '    if (a.role in ("control", "capture")) != (a.truth == "data"):', "    if False:"),
 ("toy range unchecked", "        if seed not in TOY_SEEDS[truth]:", "        if False:"),
 ("stat range unchecked", "        if b not in STAT_REPLICAS:", "        if False:"),
 ("control list unchecked", "        if item not in CONTROLS:", "        if False:"),
 ("seed check skipped", "    if not np.array_equal(X_T, seedX):", "    if False:"),
 ("flux block unweighted", "blocks[f\"band:{band}\"] = sa.mat_cov(X, w if band == sa.FLUX else None)", "blocks[f\"band:{band}\"] = sa.mat_cov(X, None)"),
 ("lateral not transferred", "blocks[f\"lat:{b}\"] = np.outer(v * g, v * g)", "blocks[f\"lat:{b}\"] = np.outer(v, v)"),
 ("C_model left out of C_T", '"C_T": C_e + C_mabs,', '"C_T": C_e,'),
 ("joint flag dropped", 'if (any(cell_flag) or joint_flag) else "COVERS"', 'if any(cell_flag) else "COVERS"'),
 ("over-coverage flags", '"verdict": "UNDER-COVERS" if (any(cell_flag) or joint_flag)', '"verdict": "UNDER-COVERS" if (any(cell_flag) or joint_flag or any(over))'),
 ("cell flag strict", "cell_flag = [bool(int(n) <= k)", "cell_flag = [bool(int(n) < k)"),
 ("atime move exits 0", "        return status | 8", "        return status"),
 ("walls limit doubled", "ok = s_max <= UNIT_SECONDS and r_max <= RSS_LIMIT_KIB", "ok = s_max <= 2 * UNIT_SECONDS and r_max <= RSS_LIMIT_KIB"),
 ("seed role at 42", "seed = SEED_CHECK if role == \"seed\" else toys.ESTIMATOR_SEED\n", "seed = toys.ESTIMATOR_SEED\n"),
 ("D1: the reader gets the source", "        return reader(copy)", "        return reader(Path(path))"),
 ("D1: a toy reads the constraint plainly", "d = toys.draw_for_seed(seed, via_noatime(toys.flux_probabilities, a.flux_constraint)", "d = toys.draw_for_seed(seed, toys.flux_probabilities(a.flux_constraint)"),
 ("D1: receipt reads the constraint plainly", "    flux_p = via_noatime(toys.flux_probabilities, a.flux_constraint)", "    flux_p = toys.flux_probabilities(a.flux_constraint)"),
 ("D1: remade reads the constraint plainly", "    w = via_noatime(sa.flux_weights, constraint)", "    w = sa.flux_weights(constraint)"),
 ("D1: null reads the assembly plainly", "def null_step(a) -> dict:\n    \"\"\"Section 5.2: the draw-matched nulls at T (C_T and the leave-out-MEC C_T^-) from the remade products only.\"\"\"\n    s1 = via_noatime(fs.load_s1, ", "def null_step(a) -> dict:\n    \"\"\"Section 5.2: the draw-matched nulls at T (C_T and the leave-out-MEC C_T^-) from the remade products only.\"\"\"\n    s1 = fs.load_s1("),
 ("B1 (audit): N1 composite stat constant", 'stats[k] = {"max_composite_over_max_single": float(np.max(r)), "rows_above_bound": int(np.sum(r > N1_BOUND))}', 'stats[k] = {"max_composite_over_max_single": 1.0, "rows_above_bound": 0}'),
 ("B1 (audit): receipt count off", '"rows_ratio_above_bound": int(np.sum(ratio > N1_BOUND))}', '"rows_ratio_above_bound": 0}'),
 ("B1 (audit): receipt max ratio off", '"max_abs_ratio": float(ratio.max()),', '"max_abs_ratio": 0.0,'),
 ("B1 (audit): receipt cv_zero count off", '"cv_zero_u_nonzero": int(np.sum((c == 0) & fin & (u != 0)))', '"cv_zero_u_nonzero": 0'),
 ("B1 (audit): readout null digest unchecked", '    if inv.sha256_noatime(a.null) != a.expect_null_sha256:', '    if False:'),
 ("B1 (audit): readout products unchecked", '    if nl["products_sha256"] != products_digest(a.unfolds, a.tag, a.truth, BLOCK_ROLES):', '    if False:'),
 ("B1 (audit): products digest drops stat", 'BLOCK_ROLES = ("central", "seed", "block", "stat")', 'BLOCK_ROLES = ("central", "seed", "block")'),
 ("B1 (audit): toy seed set unchecked", '    if have != seeds:', '    if False:'),
 ("B1 (audit): flux law uniform", 'p = w / w.sum() if band == sa.FLUX else np.full(n, 1.0 / n)', 'p = np.full(n, 1.0 / n)'),
 ("B1 (audit): lateral law half width", 'laws.append((f"lat:{b}", fn.Discrete.two_point(2 * v * g), None))', 'laws.append((f"lat:{b}", fn.Discrete.two_point(v * g), None))'),
 ("B1 (audit): surrogate skipped", '    X_hat = fs.surrogate(np.array(X_raw), draws, rm["deltas"], f, rm["X_T"])', '    X_hat = np.array(X_raw)'),
 ("B1 (audit): offset sign flipped", '    offset = -sum(law.probs @ X - rm["X_T"]', '    offset = sum(law.probs @ X - rm["X_T"]'),
 ("B1 (audit): variant graded on C_T", '    variant = grade(E, rm["C_e"] + C_mabs_minus, _null_dict(nl["C_T_minus_mec"]))', '    variant = grade(E, rm["C_T"], _null_dict(nl["C_T_minus_mec"]))'),
 ("B1 (audit): leave-out keeps MEC", 'minus = sum(np.outer(s, s) for v, s in S.items() if v != "genie_mec")', 'minus = sum(np.outer(s, s) for v, s in S.items())'),
 ("B1 (audit): plugin control (b) skipped", '        if np.max(np.abs(xt / s1["f"] - 1)) > 1e-12:', '        if False:'),
 ("B1 (audit): zero mask from acc", '            m = nz[k]\n', '            m = acc[k] != 0\n'),
 ("B1 (audit): stat block ddof 0", 'blocks["stat"] = np.cov(R, rowvar=False, ddof=1)', 'blocks["stat"] = np.cov(R, rowvar=False, ddof=0)'),
 ("B1 (audit): normalization block dropped", '    blocks["normalization"] = np.outer(sa.NORM_FRACTION * X_T, sa.NORM_FRACTION * X_T)', '    blocks["normalization"] = 0 * np.outer(X_T, X_T)'),
 ("B1 (audit): null gauss drops C_model", '        null = fn.null_contents(laws, rm["blocks"]["stat"] + rm["blocks"]["normalization"] + C_mabs, C)', '        null = fn.null_contents(laws, rm["blocks"]["stat"] + rm["blocks"]["normalization"], C)'),
 ("B1 (audit): null U check dropped", '    if not np.allclose(U, s1["U"], rtol=0, atol=1e-6):\n        raise Refusal("the definition\'s functional is not S1\'s")\n    frac, minus', '    if False:\n        raise Refusal("the definition\'s functional is not S1\'s")\n    frac, minus'),
 ("B1 (audit): cmodel rebuild unchecked", '    if np.max(np.abs(full - frac)) > 1e-12 * np.max(np.abs(frac)):', '    if False:'),
 ("B1 (audit): toy truth nonfinite unchecked", '        if not np.all(np.isfinite(x_true)):', '        if False:'),
 ("B1 (audit): plugin push size unchecked", '        if push.size != int(m.sum()):', '        if False:'),
 ("B1 (audit): push digest unchecked", '        if a.push is None or inv.sha256_noatime(a.push) != a.expect_push_sha256:', '        if a.push is None:'),
 ("B1 (audit): flux table digest unchecked", '        if inv.sha256_noatime(a.flux_table) != a.expect_flux_table_sha256:', '        if False:'),
 ("B1 (audit): weights pins unchecked", '        if inv.sha256_noatime(p) != world["pins"]["files"][str(p)]["sha256"]:', '        if False:'),
 ("B1 (audit): input digests unchecked", '    if (npz_sha, bkg_sha) != (sa.INPUT_NPZ_SHA256, sa.BKG_SHA256):', '    if False:'),
 ("B2: the all-draws bound keeps the max", 'np.exp(logsum[k] - np.log(np.where(top[k] > 0, top[k], 1.0)))', 'np.exp(logsum[k])'),
 ("B2: an unevaluated row does not stop", '    stop = any(not v["declared"]["evaluated"] or v["declared"]["rows_above"] for v in arrays.values())', '    stop = any(bool(v["declared"]["rows_above"]) for v in arrays.values())'),
 ("B2: the exact pass takes the first draw only", '            for tags in draws:\n                v = V[k]', '            for tags in draws[:1]:\n                v = V[k]'),
 ("B2: receipt ignores the composite", '"verdict": "STOP" if comp["stop"] else "PASS", "atime"', '"verdict": "PASS", "atime"'),
 ("B2: n1 ignores the toys above", '"toys_with_rows_above": above, "verdict": "STOP" if above else "PASS"}', '"toys_with_rows_above": above, "verdict": "PASS"}'),
 ("B3: readout U check dropped", '    if not np.allclose(U, s1["U"], rtol=0, atol=1e-6):\n        raise Refusal("the definition\'s functional is not S1\'s")\n    if nl.get', '    if False:\n        raise Refusal("the definition\'s functional is not S1\'s")\n    if nl.get'),
 ("B3: readout ignores what the null was made from", '    if nl.get("made_from") != made_from(a, U):', '    if False:'),
 ("B3: the null does not record the cmodel json", '"cmodel_json_sha256": sa.sha256(a.cmodel_json),', ''),
 ("B4: clause S's leave-out list on C_T", '"C_T_minus_mec": model_dominant(rm["C_e"] + C_mabs_minus, C_mabs_minus)', '"C_T_minus_mec": model_dominant(rm["C_T"], C_mabs_minus)'),
 ("B4: clause S's threshold at the whole", 'return [f"R{c:02d}" for c in range(C.shape[0]) if C_mabs[c, c] > 0.5 * C[c, c]]', 'return [f"R{c:02d}" for c in range(C.shape[0]) if C_mabs[c, c] > C[c, c]]'),
 ("C1 (audit): the CV-zero all-draws bound halved", "0.0), nonzero[k])", "0.0), nonzero[k] / 2)"),
 ("C1 (audit): the exact pass's CV-zero rows as a product", "comp = np.where(m, np.prod(np.abs(v), axis=1), np.abs(v.sum(axis=1)))", "comp = np.prod(np.abs(v), axis=1)"),
 ("C1 (audit): declared draws hold one truth", "for t in TRUTHS for s in TOY_SEEDS[t]]", "for t in (\"g18\",) for s in TOY_SEEDS[t]]"),
 ("C1 (audit): N2's threshold at 0.25", "if C_mabs[c, c] > 0.5 * C[c, c]]", "if C_mabs[c, c] > 0.25 * C[c, c]]"),
 ("C1 (audit): N2's C_T^- list is C_T's", '"C_T_minus_mec": model_dominant(rm["C_e"] + C_mabs_minus, C_mabs_minus)', '"C_T_minus_mec": model_dominant(rm["C_T"], rm["C_model_abs"])'),
 ("minor: partial products not refused", '    if left:\n        raise Refusal(f"partial', '    if False:\n        raise Refusal(f"partial'),
 ("D1: readout reads the assembly plainly", "        raise Refusal(\"the null was not made from these products\")\n    s1 = via_noatime(fs.load_s1, ", "        raise Refusal(\"the null was not made from these products\")\n    s1 = fs.load_s1("),
]
rows = []
try:
    for name, old, new in M:
        assert orig.count(old) == 1, name
        src.write_text(orig.replace(old, new))
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", str(tests)], capture_output=True, text=True)
        state = "KILLED" if r.returncode == 1 else "SURVIVED" if r.returncode == 0 else f"ERROR rc={r.returncode}"
        rows.append((name, state))
        print(f"{state:8s} {name}", flush=True)
finally:
    src.write_text(orig)
r = subprocess.run([sys.executable, "-m", "pytest", "-q", str(tests)], capture_output=True, text=True)
print("unmutated:", r.stdout.strip().splitlines()[-1])
print(f"{sum(1 for _, k in rows if k == 'KILLED')} of {len(rows)} killed")
