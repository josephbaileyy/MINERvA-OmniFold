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
