import subprocess, sys
from pathlib import Path
D = Path(sys.argv[1]); A = D / "bsel/bsel_select.py"; orig = A.read_text()
M = [
 ("Z = 1.96", "Z = 1.645", "z 1.645"),
 ("    return worst <= KAPPA * S\n", "    return worst < KAPPA * S\n", "kappa strict (labels)"),
 ("    at_means = worst <= KAPPA * S\n", "    at_means = worst < KAPPA * S\n", "kappa strict (select)"),
 ("KAPPA = 1.0\n", "KAPPA = 0.9\n", "kappa 0.9"),
 ("KAPPA_DISC = 0.5\n", "KAPPA_DISC = 0.6\n", "kappa_disc 0.6"),
 ("    disc = measured & (worst <= KAPPA_DISC * S)\n", "    disc = at_means & (worst <= KAPPA_DISC * S)\n", "disc ignores flips"),
 ("    measured = at_means & ~fl\n", "    measured = at_means\n", "flips ignored"),
 ("    return {t: np.abs(beta[t]) + Z * se[t] for t in beta}", "    return {t: beta[t] + Z * se[t] for t in beta}", "abs dropped"),
 ("    se = {t: sig[t] * R[t] for t in TRUTHS}", "    se = {t: sig[t] for t in TRUTHS}", "se not in Tune v1 units"),
 ("    beta = {t: b[t] * R[t] for t in TRUTHS}", "    beta = {t: b[t] for t in TRUTHS}", "beta not in Tune v1 units"),
 ('    se["closure_nuwro"] = np.sqrt(se["closure_nuwro"] ** 2 + s2)', '    se["closure_nuwro"] = se["closure_nuwro"]', "closure split term dropped"),
 ("np.var(split_beta[t], axis=0, ddof=1)", "np.var(split_beta[t], axis=0, ddof=0)", "split var ddof 0"),
 ("    s = np.sqrt(sum(((np.asarray(g[a], float) - np.asarray(g[b], float)) / t) ** 2 for a, b in pairs) / len(pairs))",
  "    s = np.sqrt(sum(((np.asarray(g[a], float) - np.asarray(g[b], float)) / t) ** 2 for a, b in pairs) / 2)", "sg divisor"),
 ('PANEL = ("genie_cv", "genie_mec", "nuwro")', 'PANEL = ("genie_cv", "genie_mec")', "panel shrunk"),
 ("GIBUU_CELLS = (0, 1, 2, 3, 8, 9, 10, 11)", "GIBUU_CELLS = (0, 1, 2, 3, 4, 5, 6, 7)", "gibuu cells"),
 ("        if not np.array_equal(R[t], np.ones(N_CELLS)):", "        if False:", "R=1 check off"),
 ("        if not (rel_close(mean, b[t]) and rel_close(noise, sig[t])):", "        if not rel_close(mean, b[t]):", "noise unchecked"),
 ("    split_U = {t: np.abs(split_beta[t]) + Z * se[t][None, :] for t in split_beta}", "    split_U = {t: np.abs(split_beta[t]) for t in split_beta}", "split U without SE"),
 ("        if sorted(seeds.tolist()) != list(ROW4_SEEDS):", "        if len(seeds) != 16:", "seed set unchecked"),
 ("    if np.any((v > 0) & (v < 1e-30)):", "    if False:", "tiny-value leak check off"),
]
for old, new, name in M:
    assert orig.count(old) == 1, name
    A.write_text(orig.replace(old, new))
    p = subprocess.run([sys.executable, "-B", "-m", "unittest", "bsel/test_bsel.py"], cwd=D, capture_output=True, text=True)
    print(f"{name}: {'KILLED' if p.returncode else 'SURVIVED'}")
    A.write_text(orig)
