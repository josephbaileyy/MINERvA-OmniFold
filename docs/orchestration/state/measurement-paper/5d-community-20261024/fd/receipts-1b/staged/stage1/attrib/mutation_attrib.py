"""Connect 34 attribution mutants: coverage-5b-audit's mut_attrib.py (review of connect 34 at 1ef3d855), carried
verbatim below this docstring. Run from a scratchpad: TMPDIR=<dir> python3 mutation_attrib.py <worktree>. It rewrites
n1_attrib.py per mutant and restores it."""
import subprocess, sys, shutil, os
from pathlib import Path
WT = Path(sys.argv[1]); S = WT / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/stage1/attrib"
src = (S / "n1_attrib.py").read_text()
M = [
 ("first/second swapped", "first[band(rj[0][1])] += 1", "first[band(rj[-1][1])] += 1"),
 ("second from first", "second[band(rj[1][1])] += 1", "second[band(rj[0][1])] += 1"),
 ("top unsorted", "for t in tags), reverse=True)", "for t in tags), reverse=False)"),
 ("a_cv of wrong row", '"a_cv": float(cv[k][i[j]])', '"a_cv": float(cv[k][j])'),
 ("truth label off by one", "truth, seed = labels[arg[j]]", "truth, seed = labels[max(arg[j] - 1, 0)]"),
 ("label order truths reversed", "for t in mc.TRUTHS for s", "for t in reversed(list(mc.TRUTHS)) for s"),
 ("cv-zero count inverted", '"rows_above_cv_zero": int(np.sum(~m[above]))', '"rows_above_cv_zero": int(np.sum(m[above]))'),
 ("a_cv quantile on all candidates", "a_cv = np.abs(cv[k][i[above]])", "a_cv = np.abs(cv[k][i])"),
 ("band max over drawn only->first univ", "band_r.setdefault(b, []).append(float(max(abs(V[k][j, col[t]]) for t in ts)))", "band_r.setdefault(b, []).append(float(abs(V[k][j, col[ts[0]]])))"),
 ("n_gt_1 wrong", '"n_universes_r_gt_1": int(sum(r > 1 for r, _ in rj))', '"n_universes_r_gt_1": 0'),
 ("pairs wrong", 'pairs[f"{band(rj[0][1])}+{band(rj[1][1])}"] += 1', 'pass'),
 ("band() wrong", 'return tag.rpartition("_")[0]', 'return tag'),
 ("check skips declared", 'for key in ("evaluated", "rows", "max", "rows_above"):', 'for key in ():'),
 ("arg ties last", "arg[r > worst] = d", "arg[r >= worst] = d"),
]
orig = S / "n1_attrib.py"; bak = Path(os.environ["TMPDIR"]) / "n1_attrib.orig"; shutil.copy(orig, bak)
try:
    for name, a, b in M:
        if src.count(a) != 1: print(f"NOMATCH {name}"); continue
        orig.write_text(src.replace(a, b))
        r = subprocess.run([sys.executable, "-B", "-m", "pytest", "-q", "-x", str(S / "test_n1_attrib.py")], cwd=WT, capture_output=True, text=True)
        print(f"{'KILLED ' if r.returncode else 'SURVIVED'} {name}", flush=True)
finally:
    shutil.copy(bak, orig)
