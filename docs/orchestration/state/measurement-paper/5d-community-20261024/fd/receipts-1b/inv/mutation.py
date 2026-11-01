import subprocess, sys, shutil
from pathlib import Path
src = Path("fd_1b_inv.py"); orig = src.read_text()
M = [
 ("B1: noise if EITHER side under its floor", "return (np.asarray(M_bb) < k * np.asarray(N_data)) & (np.asarray(E_bb)", "return (np.asarray(M_bb) < k * np.asarray(N_data)) | (np.asarray(E_bb)"),
 ("resolution threshold 4 -> 1", "RESOLVE_K = 4.0 ", "RESOLVE_K = 1.0 "),
 ("fallback may read SUPPORTED", 'return "OPEN" if fallback else "SUPPORTED"', 'return "SUPPORTED"'),
 ("all-SUPPORTED skips I1 (M2)", 'return {"verdict": verdict, "outcome": "O3 pending I1" if sup else None, "o3_cells_pending_I1": sup, "next": "I1"}', 'return {"verdict": verdict, "outcome": "O3 pending I1" if sup else None, "o3_cells_pending_I1": sup, "next": "I2" if verdict == "SUPPORTED" else "I1"}'),
 ("upper floor = point floor", "return (n - 1) / chi2_ppf(level, n - 1)", "return 1.0"),
 ("B2: F_truth not gated", '    if k == "F_truth":\n        tr = None', '    if False:\n        tr = None'),
 ("half-of-the-log test weakened", "mag < 0.5 * abs(tot)", "mag < 0.1 * abs(tot)"),
 ("opposite-side factors counted", "if math.log(F[k][c]) * tot > 0]", "]"),
 ("headline account at 4 (M3)", "ACCOUNT_MIN, REFUTED_MAX = 8, 3", "ACCOUNT_MIN, REFUTED_MAX = 4, 3"),
 ("rho reproduction control skipped", 'if json.loads(gate_d.read_text()).get("rho") != diag["rho"]:', 'if False:'),
 ("S1 block reproduction skipped", 'if not np.array_equal(sa.mat_cov(X, w if b == sa.FLUX else None), s1["blocks"][f"band:{b}"]):', 'if False:'),
 ("S1_CV vs jitter base skipped", 'if not np.array_equal(base, sa.xs(staged / "uni" / f"{S1_TAG}_CV.npz")):', 'if False:'),
 ("mode CV control skipped", 'if not np.array_equal(_xs(cvp), cv_flat):', 'if False:'),
 ("O_NOATIME flag dropped", "fd = os.open(path, os.O_RDONLY | NOATIME_FLAG)", "fd = os.open(path, os.O_RDONLY)"),
 ("atime-moved refusal in stage skipped", "if (after.st_atime_ns, after.st_mtime_ns, after.st_size) != (before.st_atime_ns, before.st_mtime_ns, before.st_size):", "if False:"),
 ("prior factor applied after the product", "ui[\"denom_nd\"] = np.asarray(inputs[\"denom_nd\"], float) * factor", "ui[\"denom_nd\"] = np.where(of0 > 0, np.asarray(inputs[\"denom_nd\"], float) * of1 / np.where(of0 > 0, of0, 1.0), np.asarray(inputs[\"denom_nd\"], float))"),
 ("mode B background not applied", 'dict(bkg, bkg_w=np.asarray(bkg["bkg_w"], float) * k_b), rec)', 'dict(bkg), rec)'),
 ("template not taken from the mode", 'MC_KEYS = ("w_truth", "w_reco", "denom_nd", "tmpl_w")', 'MC_KEYS = ("w_truth", "w_reco", "denom_nd")'),
 ("mode A non-finite kept", 'w = universe_weights(bank, tag, "zero")', 'w = universe_weights(bank, tag, "keep")'),
 ("noise factor for pairs 1", "return (n - 1) / n", "return 1.0"),
]
rows = []
try:
    for name, old, new in M:
        assert orig.count(old) == 1, name
        src.write_text(orig.replace(old, new))
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "tests/test_fd_1b_inv.py"], capture_output=True, text=True)
        killed = r.returncode != 0
        rows.append((name, "KILLED" if killed else "SURVIVED"))
        print(f"{'KILLED  ' if killed else 'SURVIVED'} {name}", flush=True)
finally:
    src.write_text(orig)
print(f"{sum(1 for _, k in rows if k == 'KILLED')} of {len(rows)} killed")
