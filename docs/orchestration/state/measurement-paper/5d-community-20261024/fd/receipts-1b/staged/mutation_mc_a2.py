"""Mutation receipt for nd-unfolding/fd_1b_mc.py at amendment 2 (for binding 3). Binding 2's mutants (mutation_mc.py)
are carried; those whose target code amendment 2 replaced are printed NOT APPLICABLE, by name. Run from nd-unfolding/ with TMPDIR set:

    python3 ../docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/mutation_mc_a2.py

KILLED means the suite exits 1 (a test failed); any other non-zero exit is ERROR, not a kill.
"""
import hashlib, os, shutil, subprocess, sys
from pathlib import Path
# No bytecode anywhere: a mutant written in the same second and at the same size as the file before it would
# otherwise be imported from a stale __pycache__ entry, in either direction (binding 2's mutation_mc.py had this flaw).
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
PYTEST = [sys.executable, "-B", "-m", "pytest", "-p", "no:cacheprovider", "-q"]


def purge():
    for d in (Path("__pycache__"), Path("tests/__pycache__")):
        shutil.rmtree(d, ignore_errors=True)
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
 ("D1: a toy reads the constraint plainly", "declared range\")\n        d = toys.draw_for_seed(seed, via_noatime(toys.flux_probabilities, a.flux_constraint)", "declared range\")\n        d = toys.draw_for_seed(seed, toys.flux_probabilities(a.flux_constraint)"),
 ("A2: clipmean reads the constraint plainly", "declared toy seed\")\n        d = toys.draw_for_seed(seed, via_noatime(toys.flux_probabilities, a.flux_constraint)", "declared toy seed\")\n        d = toys.draw_for_seed(seed, toys.flux_probabilities(a.flux_constraint)"),
 ("D1: receipt reads the constraint plainly", "    flux_p = via_noatime(toys.flux_probabilities, a.flux_constraint)", "    flux_p = toys.flux_probabilities(a.flux_constraint)"),
 ("D1: remade reads the constraint plainly", "    w = via_noatime(sa.flux_weights, constraint)", "    w = sa.flux_weights(constraint)"),
 ("D1: null reads the assembly plainly", "from the remade products only.\"\"\"\n    refuse_mixed_estimator(a.unfolds, a.tag, a.truth, a.estimator, a.clip_rule)\n    s1 = via_noatime(fs.load_s1, ", "from the remade products only.\"\"\"\n    refuse_mixed_estimator(a.unfolds, a.tag, a.truth, a.estimator, a.clip_rule)\n    s1 = fs.load_s1("),
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
 ("D1: readout reads the assembly plainly", "these products\")\n    refuse_mixed_estimator(a.unfolds, a.tag, a.truth, a.estimator, a.clip_rule)\n    s1 = via_noatime(fs.load_s1, ", "these products\")\n    refuse_mixed_estimator(a.unfolds, a.tag, a.truth, a.estimator, a.clip_rule)\n    s1 = fs.load_s1("),
 # ---- amendment 2 (first order, lambda+, the exact screened receipt, clipmean, the clipping readout)
 ("A2: compose back to the product", "            acc[k] += a_u - cv[k]", "            acc[k] *= np.where(cv[k] != 0, a_u / np.where(cv[k] != 0, cv[k], 1.0), 1.0)"),
 ("A2: compose drops the CV subtraction", "            acc[k] += a_u - cv[k]", "            acc[k] += a_u"),
 ("A2: compose's first term is the CV", "                acc[k], peak[k] = a_u.copy(), np.abs(a_u)", "                acc[k], peak[k] = cv[k] + (a_u - cv[k]), np.abs(a_u)"),
 ("A2: 2b not checked", "        if bad:\n            raise Refusal(f\"the composite denominator", "        if False:\n            raise Refusal(f\"the composite denominator"),
 ("A2: 2b at < 0 only", "bad = int(np.sum((cv[\"denom\"] > 0) & (acc[\"denom\"] <= 0)))", "bad = int(np.sum((cv[\"denom\"] > 0) & (acc[\"denom\"] < 0)))"),
 ("A2: 2b on k = 1 too", "    if len(tags) > 1:\n        bad = ", "    if len(tags) > 0:\n        bad = "),
 ("A2: n1_ratio 0/0 as 0", "np.where(a_D == 0, 1.0, np.inf))", "np.where(a_D == 0, 0.0, np.inf))"),
 ("A2: clip on w_reco alone", "    lam = w * r\n    neg = reco & (lam < 0)\n    bw", "    lam = w * r\n    neg = reco & (w < 0)\n    bw"),
 ("A2: background not clipped", "dict(ub, bkg_w=np.where(negb, 0.0, bw)), clip", "dict(ub), clip"),
 ("A2: signal not clipped", "    du = dict(ui, w_reco=np.where(neg, 0.0, w))", "    du = dict(ui)"),
 ("A2: clipped mass signed", "_flat_hist(ui[\"MCreco\"][neg], -lam[neg], edges)", "_flat_hist(ui[\"MCreco\"][neg], lam[neg], edges)"),
 ("A2: truth cells over all clipped rows", "    tneg = neg & np.asarray(ui[\"pass_truth\"], bool)", "    tneg = neg"),
 ("A2: the toy draws the unclipped nature", "    exp, x_true, _ = toys.build_full(du, db, r, ones_s, ones_b, seed, expectation=False)\n    exp = with_mc", "    exp, x_true, _ = toys.build_full(ui, ub, r, ones_s, ones_b, seed, expectation=False)\n    exp = with_mc"),
 ("A2: the stat replica draws unclipped", "    exp, _, _ = toys.build_full(du, db, r, ones_s, ones_b, seed, expectation=False)\n    return s5n_pseudo.bootstrap_replica(exp, b), clip", "    exp, _, _ = toys.build_full(ji, jb, r, ones_s, ones_b, seed, expectation=False)\n    return s5n_pseudo.bootstrap_replica(exp, b), clip"),
 ("A2: clipmean adds nothing", "    exp = dict(exp, obs=np.concatenate([exp[\"obs\"], coords[keep]]),", "    exp = dict(exp, obs_unused=np.concatenate([exp[\"obs\"], coords[keep]]),"),
 ("A2: clipmean outside the window", "    keep = s5n_pseudo.fid_mask(coords, inputs[\"edges\"])\n    exp = dict(exp", "    keep = np.ones(coords.shape[0], bool)\n    exp = dict(exp"),
 ("A2: the screen floor tightened", "        np.maximum(L, np.min(np.abs(V[cs]), axis=0), out=L)", "        np.maximum(L, np.max(np.abs(V[cs]), axis=0), out=L)"),
 ("A2: the floor check always passes", "    return bool(np.array_equal(ref, L))", "    return True"),
 ("A2: the screen at >= 10 L", "        rows = np.flatnonzero(np.abs(a) > lim)", "        rows = np.flatnonzero(np.abs(a) > 1.5 * lim)"),
 ("A2: the matmul's CV correction off by one", "    A = Sb @ Vm - (k[d0:d0 + block, None] - 1.0) * cm[None, :]", "    A = Sb @ Vm - k[d0:d0 + block, None] * cm[None, :]"),
 ("A2: exact pass's CV correction off by one", "        A = S[d0:d0 + block] @ V - (k[d0:d0 + block, None] - 1.0) * cv[None, :]\n        for i in range(A.shape[0]):", "        A = S[d0:d0 + block] @ V - k[d0:d0 + block, None] * cv[None, :]\n        for i in range(A.shape[0]):"),
 ("A2: the peak from the first universe only", "            for c in cs[1:]:\n                np.maximum(peak, np.abs(V[c, rows]), out=peak)", "            for c in cs[1:1]:\n                np.maximum(peak, np.abs(V[c, rows]), out=peak)"),
 ("A2: the pair budget ignored", "    if pairs > max_pairs:\n        raise InvalidReceipt", "    if False:\n        raise InvalidReceipt"),
 ("A2: near-bound pairs not recomputed", "            if np.any(close):\n                near += int(close.sum())", "            if False:\n                near += int(close.sum())"),
 ("A2: the validation ignores pairs", "    if want != res[\"sample_above\"]:", "    if False:"),
 ("A2: the validation ignores worsts", "        if w_ref > N1_BOUND and abs(res[\"worst\"][row] - w_ref) > 1e-12 * w_ref:", "        if False:"),
 ("A2: the sample's pairs not recorded", "            for row in rows[hit & in_sample[rows]]:\n                sample_above.add((d, int(row)))", "            for row in rows[hit & in_sample[rows]][:0]:\n                sample_above.add((d, int(row)))"),
 ("A2: a draw missing a band allowed", "        if sorted(t.rpartition(\"_\")[0] for t in tags) != sorted(bands):", "        if False:"),
 ("A2: the denominator check at d_D < 0", "        n = int(np.sum(pos & (acc <= 0)))", "        n = int(np.sum(pos & (acc < 0)))"),
 ("A2: the denominator check without the CV", "            acc += D[c] - dcv", "            acc += D[c]"),
 ("A2: crossterm sign parity dropped", "        P = np.where(nz[None, :], cm[None, :] * np.exp(Sb @ logs) * sign * ((Sb @ zf) == 0), A)", "        P = np.where(nz[None, :], cm[None, :] * np.exp(Sb @ logs) * ((Sb @ zf) == 0), A)"),
 ("A2: crossterm zero factors dropped", "        P = np.where(nz[None, :], cm[None, :] * np.exp(Sb @ logs) * sign * ((Sb @ zf) == 0), A)", "        P = np.where(nz[None, :], cm[None, :] * np.exp(Sb @ logs) * sign, A)"),
 ("A2: flat_cells' closed last edge", "        i = np.where(coords[:, dim] == e[-1], e.size - 2, i)        # histogramdd's closed last edge", "        i = i"),
 ("A2: cross_z without the relative sigma", "        z = np.where(H_cv > 0, (H_p - H_a) / H_cv, 0.0) / rel_sigma[None, :]", "        z = np.where(H_cv > 0, (H_p - H_a) / H_cv, 0.0)"),
 ("A2: the loader hashes nothing", "        if hashlib.sha256(raw).hexdigest() != world[\"pins\"][\"files\"][str(p)][\"sha256\"]:", "        if False:"),
 ("A2: the loader keeps non-finite values in zero", "        zero[k] = np.nan_to_num(keep[k].copy(), nan=0.0, posinf=0.0, neginf=0.0)", "        zero[k] = keep[k].copy()"),
 ("A2: the receipt's STOP ignores 2b", "    if denom[\"draws_with_nonpositive_cells\"]:\n        reasons.append", "    if False:\n        reasons.append"),
 ("A2: the receipt's STOP ignores N1", "    reasons = [f\"N1: {k} {v['rows_above']} rows above\" for k, v in exact.items() if v[\"rows_above\"]]", "    reasons = []"),
 ("A2: N_clip from the signal alone", "    neg_total = np.abs(exact[\"wr\"][\"_neg_sum\"]) + np.abs(exact[\"bkgw\"][\"_neg_sum\"])", "    neg_total = np.abs(exact[\"wr\"][\"_neg_sum\"]) + 0 * exact[\"bkgw\"][\"_neg_sum\"]"),
 ("A2: the clipping offset unscaled", "    o = (U @ np.asarray(zc[\"xsec_flat\"], float) - rm[\"X_T\"]) / sigma", "    o = U @ np.asarray(zc[\"xsec_flat\"], float) - rm[\"X_T\"]"),
 ("A2: the reading ignores the flag", "                                                       if cell_flag[c] and abs(o[c]) >= CLIP_DELTA_STAR]", "                                                       if abs(o[c]) >= CLIP_DELTA_STAR]"),
 ("A2: the reading at the strict >", "if cell_flag[c] and abs(o[c]) >= CLIP_DELTA_STAR]", "if cell_flag[c] and abs(o[c]) > 0.9]"),
 ("A2: two clipmean products accepted", "    if len(cm) != 1:\n        raise Refusal", "    if len(cm) < 1:\n        raise Refusal"),
 ("A2: clipped fraction over the wrong total", "            frac[comp].append(abs(rec[comp][\"sum_negative\"]) / tot if tot else 0.0)", "            frac[comp].append(abs(rec[comp][\"sum_negative\"]) if tot else 0.0)"),
 ("A2+: negative rows in some draw not accumulated", "            neg_any |= negd", "            neg_any = negd"),
 ("A2+: the composite sum over every row", "            comp_sum[d] = float(np.sum(a[rmask]))", "            comp_sum[d] = float(np.sum(a))"),
 ("A2+: the negative sum unsigned", "            neg_sum[d] = float(np.sum(np.minimum(a[rmask], 0.0)))", "            neg_sum[d] = float(np.sum(np.maximum(a[rmask], 0.0)))"),
 ("A2+: the clipped fraction not divided", "        return np.where(total != 0, np.abs(neg_sum) / np.abs(total), 0.0)", "        return np.where(total != 0, np.abs(neg_sum), 0.0)"),
 ("A2+: the spread's q95 at the median", '"q95": float(np.quantile(x, 0.95)),', '"q95": float(np.quantile(x, 0.5)),'),
 ("A2+: pilot_b drops the central values", "    return [(t, \"clipmean\", str(clip_seed)) for t in truths] + [(t, \"central\", \"T\") for t in truths if t != \"g18\"]", "    return [(t, \"clipmean\", str(clip_seed)) for t in truths]"),
 ("A2+: walls_of ignores a missing product", "        if not p.exists():\n            return {\"verdict\": \"REPRICE\"", "        if False:\n            return {\"verdict\": \"REPRICE\""),
 ("A2+: S1-0b walls without a seed allowed", "            if a.stage == \"s1-0b\" and a.clip_seed is None:", "            if False:"),
 ("A2+: clipcheck against a sigma of 1", "    sigma = np.sqrt(np.diag(fs.reported_matrix(s1)))\n    raw = a.receipt.read_bytes()", "    sigma = np.ones(s1[\"f\"].size)\n    raw = a.receipt.read_bytes()"),
 ("A2+: clipcheck's rule at the strict >", "        cells = [f\"R{c:02d}\" for c in range(o.size) if abs(o[c]) >= CLIP_DELTA_STAR]", "        cells = [f\"R{c:02d}\" for c in range(o.size) if abs(o[c]) > 2 * CLIP_DELTA_STAR]"),
 ("A2+: clipcheck always proceeds", "            \"verdict\": \"TO_JOSEPH\" if hit else \"PROCEED\", \"cells\": hit}", "            \"verdict\": \"PROCEED\", \"cells\": hit}"),
 ("A2+: clipcheck accepts two clipmeans", "        if len(cm) != 1:\n            raise Refusal(f\"{truth}: {len(cm)} clipmean products, not exactly one\")\n        zc = np.load(cm[0], allow_pickle=False)\n        xc", "        if len(cm) < 1:\n            raise Refusal(f\"{truth}: {len(cm)} clipmean products, not exactly one\")\n        zc = np.load(cm[0], allow_pickle=False)\n        xc"),
 ("A2e: the estimator ignored at install", "    s5e_candidate.install(a.estimator)", "    s5e_candidate.install(toys.CONFIG)"),
 ("A2e: the meta records the fixed config", "\"config\": a.estimator,", "\"config\": toys.CONFIG,"),
 ("A2e: a mixed estimator accepted", "        if meta.get(\"config\") != estimator:", "        if False:"),
 ("A2e: a mixed clip rule accepted", "        if meta.get(\"clip_rule\") != clip_rule:", "        if False:"),
 ("A2e: the meta drops the clip rule", "                \"clip_rule\": a.clip_rule,", "                \"clip_rule\": \"data\","),
 ("A2c: the nature rule keeps the truth", "        du = dict(du, w_reco=np.where(row, 0.0, w), w_truth=np.where(row, 0.0, wt))", "        du = dict(du, w_reco=np.where(row, 0.0, w))"),
 ("A2c: the nature rule ignores negative truths", "        row = neg | (np.asarray(ui[\"pass_truth\"], bool) & (wt * r < 0))", "        row = neg"),
 ("A2c: an unknown clip rule accepted", "    if rule not in CLIP_RULES:\n        raise Refusal", "    if False:\n        raise Refusal"),
 ("A2c: the toy ignores the clip rule", "seed,\n                                           a.clip_rule)", "seed,\n                                           \"data\")"),
 ("A2c: the source split at < 0", "    nonpos = {k: (np.min(V[k], axis=0) <= 0) & (cv[k] > 0) for k in V}", "    nonpos = {k: (np.min(V[k], axis=0) < 0) & (cv[k] > 0) for k in V}"),
 ("A2c: the truth clip signed", "            tru = np.bincount(ft[rows], weights=np.abs(A_t[i][rows]), minlength=n_bins) * k_flat", "            tru = np.bincount(ft[rows], weights=A_t[i][rows], minlength=n_bins) * k_flat"),
 ("A2c: the truth clip without the xsec factor", "minlength=n_bins) * k_flat\n            out[\"reco_clip\"]", "minlength=n_bins)\n            out[\"reco_clip\"]"),
 ("A2c: the truth clip over every truth row", "            rows = mt & (ar < 0)", "            rows = mt"),
 ("A2c: reco plus from the negatives", "            pos = np.bincount(fs_[ms], weights=np.maximum(ar[ms], 0.0), minlength=n_bins) + \\", "            pos = np.bincount(fs_[ms], weights=np.maximum(-ar[ms], 0.0), minlength=n_bins) + \\"),
 ("A2c: clipcheck takes any receipt", "    if hashlib.sha256(raw).hexdigest() != a.expect_receipt_sha256:\n        raise Refusal(\"the receipt's digest", "    if False:\n        raise Refusal(\"the receipt's digest"),
 ("A2c: clipcheck takes a STOP receipt", "    if rc.get(\"verdict\") != \"PASS\":", "    if False:"),
 ("A2d: the receipt reads the assembly plainly", "    inputs, bkg = world[\"inputs\"], world[\"bkg\"]\n    s1 = via_noatime(fs.load_s1, ", "    inputs, bkg = world[\"inputs\"], world[\"bkg\"]\n    s1 = fs.load_s1("),
 ("A2d: clipcheck reads the assembly plainly", "goes to Joseph before any bulk.\"\"\"\n    s1 = via_noatime(fs.load_s1, ", "goes to Joseph before any bulk.\"\"\"\n    s1 = fs.load_s1("),
 ("A2: O5 push_min not recorded", "        meta.update(ev, push_min=float(arrays[\"push\"].min()) if arrays[\"push\"].size else None,", "        meta.update(ev, push_min=None,"),

]
# binding 2's mutants whose target code amendment 2 replaced: the product composition and composite_n1
REPLACED = {"ratio composition inverted", "zero-CV rows not added", "B1 (audit): N1 composite stat constant",
            "B1 (audit): zero mask from acc", "B2: the all-draws bound keeps the max",
            "B2: an unevaluated row does not stop", "B2: the exact pass takes the first draw only",
            "B2: receipt ignores the composite", "C1 (audit): the CV-zero all-draws bound halved",
            "C1 (audit): the exact pass's CV-zero rows as a product"}
rows = []
try:
    for name, old, new in M:
        if orig.count(old) == 0:
            # only a NAMED replacement is N/A; any other missing target stops the run (a moved anchor once
            # mislabelled two live O_NOATIME guards as replaced)
            assert name in REPLACED, f"{name}: its target is missing and it is not a declared replacement"
            rows.append((name, "N/A"))
            print(f"N/A      {name}  (its target code was replaced by amendment 2)", flush=True)
            continue
        assert orig.count(old) == 1, name
        src.write_text(orig.replace(old, new))
        purge()
        r = subprocess.run(PYTEST + ["-x", str(tests)], capture_output=True, text=True, env=ENV)
        state = "KILLED" if r.returncode == 1 else "SURVIVED" if r.returncode == 0 else f"ERROR rc={r.returncode}"
        rows.append((name, state))
        print(f"{state:8s} {name}", flush=True)
finally:
    src.write_text(orig)
purge()
r = subprocess.run(PYTEST + [str(tests)], capture_output=True, text=True, env=ENV)
print("unmutated:", r.stdout.strip().splitlines()[-1])
applicable = [k for _, k in rows if k != "N/A"]
print(f"{sum(1 for k in applicable if k == 'KILLED')} of {len(applicable)} applicable killed; "
      f"{len(rows) - len(applicable)} not applicable")
