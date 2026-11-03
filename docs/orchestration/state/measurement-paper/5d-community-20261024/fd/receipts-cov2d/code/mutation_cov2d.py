"""cov2d, cov2d_receipt and cov2d_writer mutants. Run from a scratchpad: TMPDIR=<dir> python mutation_cov2d.py
<worktree>, with an interpreter that has PyROOT, uproot 5.6.9 and pytest. Each mutant rewrites one file, runs both
test files, and restores it. A kill counts only on a test failure (pytest rc != 0)."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

WT = Path(sys.argv[1])
D = WT / "2d-unfolding/cov2d"
TESTS = [str(D / "tests/test_cov2d.py"), str(D / "tests/test_cov2d_writer.py")]
M = [
    ("cov2d.py", "flux not first", "ORDER = (FLUX,) + tuple(sorted(b for b in BANDS if b != FLUX))",
     "ORDER = tuple(sorted(BANDS))"),
    ("cov2d.py", "2p2h has 2 universes", 'BANDS = {FLUX: 100, "2p2h": 3,', 'BANDS = {FLUX: 100, "2p2h": 2,'),
    ("cov2d.py", "flux drawn uniformly", "univ = [(FLUX, int(rng.choice(BANDS[FLUX], p=p)))]",
     "univ = [(FLUX, int(rng.choice(BANDS[FLUX])))]"),
    ("cov2d.py", "salt dropped", "rng = np.random.default_rng([int(seed), DRAW_SALT])",
     "rng = np.random.default_rng(int(seed))"),
    ("cov2d.py", "pair band always endpoint 0", "univ.append((band, int(rng.integers(BANDS[band]))))",
     "univ.append((band, 0))"),
    ("cov2d.py", "product composition", "out += np.asarray(a, np.float64) - cv",
     "out *= np.where(cv != 0, np.asarray(a, np.float64) / np.where(cv != 0, cv, 1), 1)"),
    ("cov2d.py", "composition from the CV", "out = np.array(univ[0], dtype=np.float64, copy=True)",
     "out = np.array(cv, dtype=np.float64, copy=True) + (np.asarray(univ[0]) - cv)"),
    ("cov2d.py", "0/0 is NaN", "    out = np.ones_like(num)\n", "    out = np.full_like(num, np.nan)\n"),
    ("cov2d.py", "x/0 is 1", "    out[(den == 0) & (num > 0)] = math.inf\n", "    pass\n"),
    ("cov2d.py", "bound uses the max |a_u|", "den = np.maximum(den, np.min(np.abs(b), axis=0))",
     "den = np.maximum(den, np.max(np.abs(b), axis=0))"),
    ("cov2d.py", "bound drops |a_CV|", "    num = np.abs(cv).astype(np.float64)\n",
     "    num = np.zeros_like(cv, dtype=np.float64)\n"),
    ("cov2d.py", "lambda not clipped", "return np.where(neg, 0.0, lam), rec", "return lam, rec"),
    ("cov2d.py", "negative mass unrecorded", '"sum_lambda_neg": float(lam[neg].sum())', '"sum_lambda_neg": 0.0'),
    ("cov2d.py", "weakened at or below", "cells[ratio < WEAKENED_BELOW]", "cells[ratio <= WEAKENED_BELOW]"),
    ("cov2d.py", "weakened below 0.8", "WEAKENED_BELOW = 0.9", "WEAKENED_BELOW = 0.8"),
    ("cov2d.py", "outlier cell off by one", "OUTLIER_CELL = 216 ", "OUTLIER_CELL = 217 "),
    ("cov2d.py", "weakened accepts NaN", " or not np.all(np.isfinite(ratio))", ""),
    ("cov2d.py", "flux weights accept negatives", "np.any(w < 0) or ", ""),
    ("cov2d.py", "digest without O_NOATIME", "os.open(path, os.O_RDONLY | os.O_NOATIME)", "os.open(path, os.O_RDONLY)"),
    ("cov2d_receipt.py", "certify at 10 x 1.01", "CERTIFY = c.N1_BOUND * (1 - 1e-9)", "CERTIFY = c.N1_BOUND * 1.01"),
    ("cov2d_receipt.py", "exact pass skips the last block row", "rows = cand[k:k + EXACT_BLOCK]",
     "rows = cand[k:k + EXACT_BLOCK][:-1]"),
    ("cov2d_receipt.py", "exact pass drops the CV term", "ad += G[:, :, j] - cvr", "ad += G[:, :, j]"),
    ("cov2d_receipt.py", "peak lower bound uses max", "m = np.maximum(m, np.min(np.abs(U[:, s]), axis=1))",
     "m = np.maximum(m, np.max(np.abs(U[:, s]), axis=1))"),
    ("cov2d_receipt.py", "only G18's draws", "all_draws = draws[\"G18\"] + draws[\"AR23\"]",
     "all_draws = draws[\"G18\"]"),
    ("cov2d_receipt.py", "rows above not a stop", "            if agg[\"rows_above\"]:\n",
     "            if False:\n"),
    ("cov2d_receipt.py", "negative rows uncounted", '"neg_rows": int(np.sum(np.any(A < 0, axis=1)))',
     '"neg_rows": 0'),
    ("cov2d_receipt.py", "nonfinite uncounted",
     'agg["nonfinite_zeroed"] += int(np.sum(~np.isfinite(cv)) + np.sum(~np.isfinite(U)))', "pass"),
    ("cov2d_receipt.py", "truth cell ignores the phase space", "    ok = ok.astype(bool)\n",
     "    ok = np.ones(pt.shape, bool)\n"),
    ("cov2d_receipt.py", "truth cell keeps the upper edge", "(i < pe.size - 1)", "(i < pe.size)"),
    ("cov2d_receipt.py", "truth cells not a stop", "            if bad.size:\n", "            if False:\n"),
    ("cov2d_receipt.py", "truth cells without r_T",
     "h_t[tune] += cell_hists(cell[start:stop], W * r_t[tune][start:stop, None], n_cells)",
     "h_t[tune] += cell_hists(cell[start:stop], W, n_cells)"),
    ("cov2d_receipt.py", "atime move not a stop", '    if rec["atime_moved"]:\n', "    if False:\n"),
    ("cov2d_writer.py", "background drawn first", "    return rng.poisson(ls), rng.poisson(lb), ",
     "    kb = rng.poisson(lb)\n    return rng.poisson(ls), kb, "),
    ("cov2d_writer.py", "failing rows kept", "keep = np.asarray(passed, bool) & (k > 0)", "keep = k > 0"),
    ("cov2d_writer.py", "count ignored", "np.repeat(np.asarray(pt, np.float64)[keep], n)",
     "np.asarray(pt, np.float64)[keep]"),
    ("cov2d_writer.py", "pass leaf as int", '"measured_pass": ("B", "b")', '"measured_pass": ("i", "I")'),
    ("cov2d_writer.py", "POT not written", '    ROOT.TParameter("double")("dataPOTUsed", float(data_pot)).Write()\n', ""),
    ("cov2d_writer.py", "control skips the parameter",
     '        if fw["dataPOTUsed"].member("fVal") != fcv["dataPOTUsed"].member("fVal"):',
     "        if False:"),
]
bak = Path(os.environ["TMPDIR"])
for f in {m[0] for m in M}:
    shutil.copy(D / f, bak / f)
try:
    for f, name, a, b in M:
        src = (bak / f).read_text()
        if src.count(a) != 1:
            print(f"NOMATCH {f}: {name}", flush=True)
            continue
        (D / f).write_text(src.replace(a, b))
        r = subprocess.run([sys.executable, "-B", "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", *TESTS],
                           cwd=WT, capture_output=True, text=True)
        print(f"{'KILLED ' if r.returncode else 'SURVIVED'} {f}: {name}", flush=True)
        shutil.copy(bak / f, D / f)
finally:
    for f in {m[0] for m in M}:
        shutil.copy(bak / f, D / f)
