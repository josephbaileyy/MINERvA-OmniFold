import subprocess, sys
from pathlib import Path
D = Path(sys.argv[1]); A = D / "nd-unfolding/b5d/b5d_build.py"; orig = A.read_text()
M = [
 ("    raw = sum(np.outer(beta[t], beta[t]) - Sigma[t] for t in FAMILY)", "    raw = sum(np.outer(beta[t], beta[t]) for t in FAMILY)", "no debias"),
 ("    w = np.clip(w, 0.0, None)\n", "    w = np.abs(w)\n", "abs not positive part"),
 ('FAMILY = ("nominal", "A7_genie_mec", "A7_nuwro", "A7_gibuu")', 'FAMILY = ("A7_genie_mec", "A7_nuwro", "A7_gibuu")', "family minus nominal"),
 ("    return float(np.mean(v[idx]) / ((N - 1) / N))", "    return float(np.mean(v[idx]))", "no (N-1)/N"),
 ("        active = bool(f[r] - 1.0 > TRIGGER_K * se[r])", "        active = bool(f[r] - 1.0 >= TRIGGER_K * se[r])", "trigger >="),
 ("TRIGGER_K = 3.0", "TRIGGER_K = 2.0", "trigger 2 SE"),
 ("        out[r] = {\"active\": active, \"phi\": float(f[r]) if active else 1.0}", "        out[r] = {\"active\": active, \"phi\": float(f[r])}", "phi below 1 allowed"),
 ("            L = L + (np.sqrt(trig[r][\"phi\"]) - 1.0) * P", "            L = L + (trig[r][\"phi\"] - 1.0) * P", "phi not sqrt"),
 ("BANDS = ((0, 4), (4, 8), (8, 16))", "BANDS = ((0, 5), (5, 10), (10, 16))", "band edges"),
 ("MIN_MODES = 4", "MIN_MODES = 2", "min modes 2"),
 ("    Z = (E - E.mean(axis=0)) @ V / np.sqrt(np.where(w > 0, w, np.nan))", "    Z = E @ V / np.sqrt(np.where(w > 0, w, np.nan))", "not centred"),
 ("            res[key] = (E[rng.integers(0, E.shape[0], E.shape[0])], w, V)", "            res[key] = (E, w, V)", "bootstrap no resample"),
 ("    if abs(w_flux.sum() / meta[\"sum\"] - 1) > TOL or abs(n_eff / meta[\"n_eff\"] - 1) > TOL:", "    if abs(w_flux.sum() / meta[\"sum\"] - 1) > TOL:", "n_eff unchecked"),
 ("        D = D + sa.mat_cov(X, w_flux if band == sa.FLUX else None)", "        D = D + sa.mat_cov(X, None)", "flux unweighted"),
 ("    return D + np.cov(R, rowvar=False, ddof=1)", "    return D", "stat block dropped"),
 ("        E.append(cells(ll5d_dir, U, n) - cells(ll5d_dir, U, n, \"xtrue_flat\"))", "        E.append(cells(ll5d_dir, U, n))", "error not minus truth"),
 ("    keep = w > KEEP_REL * w[0]\n    out, dropped", "    keep = w > 0.5 * w[0]\n    out, dropped", "keep rule"),
 ("        Sigma[t] = np.diag(R[t]) @ N @ np.diag(R[t])", "        Sigma[t] = N", "Sigma not in Tune v1 units"),
 ("        if j - i > 1:\n", "        if False:\n", "tie rule off"),
 ("            if a in kept:  # A1 item 6", "            if True:  # A1 item 6", "fhat over all ensembles"),
 ("            idx = [i for i in range(a, min(b, N_CELLS)) if keep[i]]  # only C_e's kept modes", "            idx = list(range(a, min(b, N_CELLS)))  # only C_e's kept modes", "L on unkept modes"),
 ("            if w.min() < -KEEP_REL * w[0]:", "            if False:", "indefinite D passes"),
 ("    if not np.all(np.isfinite(C_b)):\n", "    if False:\n", "NaN C_b passes"),
 ("            if v is not None and not (np.isfinite(v) and v > 0):", "            if False:", "per_ens unchecked"),
 ("            if not (np.all(np.isfinite(X_T)) and np.all(X_T > 0)):", "            if False:", "X_T unchecked"),
 ("            mean_err[(t, rd)] = E.mean(axis=0) / X_T * R[f\"F1_genie_v3_{t}\"]", "            mean_err[(t, rd)] = E.mean(axis=0) / X_T", "mean err not through R"),
 ("            mean_err[(t, rd)] = E.mean(axis=0) / X_T * R[f\"F1_genie_v3_{t}\"]", "            mean_err[(t, rd)] = E.mean(axis=0) * R[f\"F1_genie_v3_{t}\"]", "mean err not relative"),
 ("        elif isinstance(x, float) and x != 0.0 and abs(x) < LEAK_FLOOR:", "        elif False:", "C-LEAK off"),
 ('LEAK_EXEMPT = (("bias_block", "C_b_abs"), ("fluctuation", "V_F"))', 'LEAK_EXEMPT = (("bias_block", "C_b_abs"), ("fluctuation", "V_F"), ("fluctuation", "L"))', "L exempt"),
 ("        check_leak(out)\n", "        pass\n", "main skips C-LEAK"),
 ('    rec = {**rec, "matrices_sha256": {p.name: sha256_path(p) for p in sorted(out_dir.glob("*.csv"))}}\n', "", "no digests"),
 ("json.dumps(rec, indent=1, allow_nan=False)", "json.dumps(rec, indent=1)", "NaN json allowed"),
 ("        stops = stops + (B.Stop, ll5d_b.Refusal)", "        pass", "B/LL5D refusals uncaught"),
 ("    stops = (Stop, OSError, ImportError, SystemExit)", "    stops = (Stop, ImportError)", "OSError/SystemExit uncaught"),
 ("    q = float(np.sum(proj ** 2 / wk)) if keep.any() else None", "    q = float(np.sum(proj ** 2 / wk)) if keep.any() else float('inf')", "zero rank inf"),
 ("    if V_F is not None and not (np.all(np.isfinite(V_F)) and np.all(np.isfinite(L))):", "        if False:", "V_F unchecked"),
]
for old, new, name in M:
    assert orig.count(old) == 1, name
    A.write_text(orig.replace(old, new))
    p = subprocess.run([sys.executable, "-B", "-X", "pycache_prefix=/dev/null", "-W", "ignore", "-m", "unittest", "nd-unfolding/b5d/test_b5d.py"], cwd=D, capture_output=True, text=True)
    print(f"{name}: {'KILLED' if p.returncode else 'SURVIVED'}")
    A.write_text(orig)
