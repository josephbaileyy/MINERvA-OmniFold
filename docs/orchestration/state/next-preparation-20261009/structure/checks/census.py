#!/usr/bin/env python3
"""Semantic-duplication census of scientific conventions at a git revision.

Counts conventions by meaning, not by file type. Every row is computed from
`git grep`/`git show` at --rev, so the census can be re-run at any commit:

  python3 census.py --rev 5ac9706a > census-5ac9706a.tsv

Classes: live (tracked code outside the classes below), test, publication
(docs/analysis-note, publication, docs/publication, reproduction),
historical (docs/orchestration, docs/sep-09-presentation), and handoff
(*/HANDOFF_*).
"""
import argparse
import ast
import re
import subprocess
import sys
from collections import Counter

PUB = ("docs/analysis-note/", "publication/", "docs/publication/", "reproduction/")
HIST = ("docs/orchestration/", "docs/sep-09-presentation/")


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, check=False).stdout


def grep_files(rev, pattern, *paths):
    out = git("grep", "-l", "-E", pattern, rev, "--", *paths)
    return sorted({line.split(":", 1)[1] for line in out.splitlines() if ":" in line})


def grep_lines(rev, pattern, *paths):
    out = git("grep", "-n", "-E", pattern, rev, "--", *paths)
    return [line.split(":", 1)[1] for line in out.splitlines() if ":" in line]


def klass(path):
    if path.startswith(PUB):
        return "publication"
    if path.startswith(HIST):
        return "historical"
    if "/HANDOFF_" in path:
        return "handoff"
    if "/tests/" in path or path.split("/")[-1].startswith("test_"):
        return "test"
    return "live"


def literal(rev, path, name):
    try:
        tree = ast.parse(git("show", f"{rev}:{path}"))
    except SyntaxError:
        return None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name
                                                for t in node.targets):
            v = node.value
            if isinstance(v, ast.Call) and v.args:  # np.array([...])
                v = v.args[0]
            try:
                return [float(x) for x in ast.literal_eval(v)]
            except (ValueError, TypeError):
                return None
    return None


def row(convention, metric, n, detail=""):
    print(f"{convention}\t{metric}\t{n}\t{detail}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev", required=True)
    rev = ap.parse_args().rev
    print("convention\tmetric\tcount\tdetail")
    print(f"# rev {git('rev-parse', rev).strip()}")

    # 1. 2D bin-edge literals (top-level PT_EDGES/PZ_EDGES assignments in .py).
    drv = "2d-unfolding/unfold_2d_omnifold_unbinned.py"
    ref = {n: literal(rev, drv, n) for n in ("PT_EDGES", "PZ_EDGES")}
    files = grep_files(rev, r"^(PT_EDGES|PZ_EDGES) *=", "*.py")
    by = Counter()
    differ = []
    for f in files:
        by[klass(f)] += 1
        for n in ("PT_EDGES", "PZ_EDGES"):
            v = literal(rev, f, n)
            if v is not None and ref[n] is not None and v != ref[n]:
                differ.append(f"{f}:{n}")
    row("bin edges (2D pT/p_par)", "files defining a top-level literal", len(files),
        " ".join(f"{k}={by[k]}" for k in sorted(by)))
    row("bin edges (2D pT/p_par)", "literals whose values differ from the driver", len(differ),
        " ".join(differ))
    imp = grep_files(rev, r"from reported_cells import", "*.py")
    row("bin edges (2D pT/p_par)", "files importing the reported-cell contract", len(imp), " ".join(imp))

    # 2. Reported-cell selection in the 2D chain (assignments of a '> 0' mask
    #    named reported*/mask in 2d-unfolding live code).
    lines = [l for l in grep_lines(rev, r"(reported[a-z_0-9]*|mask[a-z_0-9]*) *= *.*> *0([^.0-9]|$)",
                                   "2d-unfolding/*.py", "2d-unfolding/uq/*.py")
             if klass(l.split(":", 1)[0]) == "live"]
    row("reported-cell selection (2D)", "'> 0' mask assignments in live 2D code", len(lines),
        " | ".join(lines))

    def operand(line):
        code = line.split(":", 2)[2]
        rhs = code.split("=", 1)[1] if "=" in code else code
        for key, name in (("cov_stat", "paper StatOnly diagonal"), ("diag", "a covariance diagonal"),
                          ("mean", "replica-ensemble mean"), ("cv", "matched CV"),
                          ("xsec", "central cross section")):
            if key in rhs:
                return name
        return "other (closure/diagnostic reference)"
    ops = Counter(operand(l) for l in lines)
    for name in sorted(ops):
        row("reported-cell selection (2D)", f"mask operand: {name}", ops[name])
    chk = grep_files(rev, r"require_same_cells", "2d-unfolding")
    row("reported-cell selection (2D)", "files that compare cell identity (not only count)",
        len(chk), " ".join(chk))

    # 3. Covariance normalization conventions in live code.
    unb = grep_files(rev, r"np\.cov\(", "2d-unfolding/*.py", "3d-unfolding/*.py", "nd-unfolding/*.py")
    unb = [f for f in unb if klass(f) == "live"]
    mat = grep_files(rev, r"\(Z\.T @ Z\) */ *N|/ *N_u\b", "2d-unfolding/*.py", "3d-unfolding/*.py", "nd-unfolding/*.py")
    mat = [f for f in mat if klass(f) == "live"]
    row("covariance normalization", "live files using np.cov (1/(N-1), bootstrap)", len(unb), " ".join(unb))
    row("covariance normalization", "live files using a MAT 1/N mean-centered sum", len(mat), " ".join(mat))

    # 4. 2D launcher estimator/seed arguments.
    for f in sorted(grep_files(rev, r"unfold_2d_omnifold_unbinned\.py", "2d-unfolding/sbatch_unfold_2d*.sh")):
        txt = git("show", f"{rev}:{f}")
        est = sorted(set(re.findall(r"--estimator[ =]+([A-Za-z]+)", txt))) or ["(default exact)"]
        seed = sorted(set(re.findall(r"--seed[ =]+\"?([0-9$A-Za-z_{}]+)", txt))) or ["(default None)"]
        boot = "yes" if "--bootstrap-seed" in txt else "no"
        row("2D launcher arguments", f, 1, f"estimator={','.join(est)} seed={','.join(seed)} bootstrap_seed={boot}")

    # 5. Hardcoded checkout root.
    root = r"/pscratch/sd/j/josephrb/MINERvA-OmniFold"
    f_all = grep_files(rev, root, "*.py", "*.sh")
    c = Counter(klass(f) for f in f_all)
    row("hardcoded checkout root", f"tracked .py/.sh naming {root}", len(f_all),
        " ".join(f"{k}={c[k]}" for k in sorted(c)))
    tops = Counter(f.split("/")[0] for f in f_all if klass(f) == "live")
    row("hardcoded checkout root", "live files by top directory", sum(tops.values()),
        " ".join(f"{k}={tops[k]}" for k in sorted(tops)))

    # 6. Dimensional cross-imports.
    u2d = grep_files(rev, r"import unfold_2d_omnifold_unbinned|from unfold_2d_omnifold_unbinned import", "*.py")
    c = Counter((f.split("/")[0], klass(f)) for f in u2d)
    row("dimensional cross-imports", "files importing the 2D driver", len(u2d),
        " ".join(f"{d}/{k}={n}" for (d, k), n in sorted(c.items())))
    u3d = grep_files(rev, r"import unfold_3d_omnifold_unbinned|from unfold_3d_omnifold_unbinned import", "*.py")
    row("dimensional cross-imports", "files importing the 3D driver", len(u3d),
        " ".join(sorted({f.split('/')[0] for f in u3d})))

    # 7. Generator code outside its dimension.
    g5 = [f for f in git("ls-tree", "-r", "--name-only", rev, "3d-unfolding/").splitlines()
          if "gen5d" in f]
    row("generator code location", "5D (s5p) predictor files under 3d-unfolding/", len(g5), " ".join(g5))

    # 8. Duplicated ROOT readers.
    for fn in ("th2_to_array", "tmatrix_to_numpy", "flatten_ours", "flatten_paper"):
        fs = grep_files(rev, rf"^def {fn}\(", "*.py")
        c = Counter(klass(f) for f in fs)
        row("ROOT reader helpers", f"files defining {fn}()", len(fs),
            " ".join(f"{k}={c[k]}" for k in sorted(c)))

    # 9. Normalization constant.
    lit = [f for f in grep_files(rev, r"3\.2353e\+?30", "*.py") if klass(f) == "live"]
    row("normalization constant", "live .py with a literal tracker-nucleon count", len(lit), " ".join(lit))


if __name__ == "__main__":
    sys.exit(main())
