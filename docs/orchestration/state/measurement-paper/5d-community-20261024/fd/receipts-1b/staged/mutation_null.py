"""Mutation receipt for nd-unfolding/fd_1b_null.py (the staged declaration's section 5.2 rule). Run from nd-unfolding/:

    python3 ../docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/mutation_null.py

KILLED means the suite exits 1 (a test failed); any other non-zero exit is ERROR, not a kill.
"""
import hashlib, subprocess, sys
from pathlib import Path
src, tests = Path("fd_1b_null.py"), Path("tests/test_fd_1b_null.py")
orig = src.read_text()
for p in (src, tests):
    print(f"sha256 {hashlib.sha256(p.read_bytes()).hexdigest()}  {p}")
print("KILLED means the suite exits 1 (a test failed); any other non-zero exit is ERROR, not a kill")
M = [
 ("laws not centred", "return cls(v - p @ v, p)", "return cls(v, p)"),
 ("two-point at full delta", "np.stack([d / 2, -d / 2])", "np.stack([d, -d])"),
 ("law covariance unweighted", "(self.values * self.probs[:, None]).T @ self.values", "self.values.T @ self.values / self.values.shape[0]"),
 ("match check skipped", "if rel > MATCH_TOL:", "if False:"),
 ("probabilities not checked", "not math.isclose(p.sum(), 1.0, abs_tol=1e-12)", "False"),
 ("Gaussian part dropped", "E = rng.multivariate_normal(np.zeros(dim), gauss, size=n, method=\"eigh\") if np.any(gauss) else np.zeros((n, dim))", "E = np.zeros((n, dim))"),
 ("one law draw shared", "E += law.values[rng.choice(law.probs.size, size=n, p=law.probs)]", "E += law.values[np.zeros(n, int)]"),
 ("content strict", "np.abs(E) <= sigma", "np.abs(E) < 0.99 * sigma"),
 ("joint cut at 0.5", "cut = chi2_ppf(P0, ndf)", "cut = chi2_ppf(0.5, ndf)"),
 ("null space kept", "keep = lam > RANK_REL * lam.max()", "keep = lam > -1.0"),
 ("chi2 not divided", "np.sum(Z * Z / lam[keep], axis=1)", "np.sum(Z * Z, axis=1)"),
 ("flag at the cdf, not below", "binom_cdf(k + 1, n, p) < alpha", "binom_cdf(k + 1, n, p) <= alpha + 0.01"),
 ("no Bonferroni", "a_cell = ALPHA_CELLS / len(p_use)", "a_cell = ALPHA_CELLS"),
 ("margin raises the null", "null[\"p_cell\"] - SE_MARGIN * null[\"se_cell\"]", "null[\"p_cell\"] + SE_MARGIN * null[\"se_cell\"]"),
 ("size omits the joint", "\"per_truth_union_bound\": float(sum(cells) + joint)", "\"per_truth_union_bound\": float(sum(cells))"),
 ("attribution uncentred", "centred = int(np.sum(np.abs(z - mean) <= 1.0))", "centred = int(np.sum(np.abs(z) <= 1.0))"),
 ("width needs no zero mean", "elif abs(mean) <= 2 * se_mean:", "elif True:"),
 ("binomial pmf flipped", "p ** i * (1 - p) ** (n - i)", "p ** (n - i) * (1 - p) ** i"),
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
