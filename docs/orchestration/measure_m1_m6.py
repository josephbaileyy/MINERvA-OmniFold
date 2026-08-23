#!/usr/bin/env python3
"""Re-measure M-1..M-6 on a named tree, and print them.

WHY THIS IS A TOOL AND NOT A PARAGRAPH. `MEASUREMENT-20260822-m1-m6-at-pinned-sha.md` calls itself
"the fastest-expiring document in the package" and instructs the reader to re-run all six before the
first `sbatch`. An instruction to re-measure that ships no instrument gets satisfied by re-reading,
which is how F-17(a) happened: the filing dropped an entrypoint and kept a count sentence that the
file below it already contradicted.

THE TREE IS AN ARGUMENT, ALWAYS. Every number here is tree-dependent, and this campaign's recurring
defect is measuring one tree and reporting about another. There is no default.

M-4 is measured only where a checkout exists; --canonical is separate from --tree for exactly that
reason -- the candidate and the canonical checkout are different subjects and must never share a
column.
"""
import argparse
import ast
import json
import pathlib
import subprocess
import sys

# REFUSE, DO NOT DEGRADE. On CPython < 3.8 a string literal parses to `ast.Str`, not `ast.Constant`,
# so M-1's literal scan would find NOTHING and print a clean "no root literals" table. The pre-conda
# interpreter on saul is 3.6.15, which is exactly the shell someone would run this from. A silent
# zero here is worse than the defect it is looking for, and `sys.stdlib_module_names` (M-2) does not
# exist before 3.10 either. Run this AFTER activation.
if sys.version_info < (3, 10):
    sys.exit(f"REFUSING: this measurement needs CPython >= 3.10, found {sys.version.split()[0]} at "
             f"{sys.executable}. On 3.6 the M-1 literal scan returns a silent, wrong zero and M-2 "
             f"has no stdlib list. Source the activator first; do not read this as 'no literals'.")

CANONICAL_LITERAL = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"

# The M-1 population: the entrypoints and modules the review contract's B-1 covers. unified_throw_cov
# .py is the TENTH row -- it was dropped from the 2026-08-22 filing, which is the F-17(a) fail.
M1_FILES = (
    "nd-unfolding/bootstrap_nd.py",
    "nd-unfolding/seedscan_split.py",
    "nd-unfolding/unified_throw_cov.py",
    "nd-unfolding/unified_throw_cov_5d.py",
    "nd-unfolding/unfold_nd_omnifold_unbinned.py",
    "nd-unfolding/sweep_bank_5d.py",
    "nd-unfolding/combine_cov_nd.py",
    "nd-unfolding/analyze_universes_5d.py",
    "nd-unfolding/mii_adopt_unified_5d_stamped.py",
    "nd-unfolding/adopt_unified_5d.py",
)

LAUNCHERS = (
    "sbatch_bootstrap_5d_gpu.sh", "sbatch_finalize_5d_bkgaware_gpu.sh",
    "sbatch_seedscan_split_5d.sh", "sbatch_sweep_bank_5d_run_bkgaware_gpu.sh",
    "sbatch_unfold_5d_detector_bkgaware_gpu.sh", "sbatch_uthrow_block_5d.sh",
    "sbatch_uthrow_combine_5d_fast.sh", "sbatch_uthrow_run_5d_fast.sh",
)


def repo_modules(tree):
    """Top-level importable names the repo itself provides."""
    out = set()
    for d in ("nd-unfolding", "2d-unfolding"):
        p = tree / d
        if p.is_dir():
            out |= {f.stem for f in p.glob("*.py")}
    return out


def m1(tree):
    """Root literals, the first sys.path insert, and repository modules imported AFTER it."""
    mods = repo_modules(tree)
    rows = []
    for rel in M1_FILES:
        f = tree / rel
        if not f.is_file():
            rows.append({"file": rel, "present": False})
            continue
        src = f.read_text(encoding="utf-8", errors="replace")
        t = ast.parse(src)
        literals = []          # (name, lineno) for assignments of the canonical absolute path
        first_insert = None    # lineno of the first sys.path.insert/append
        for node in ast.walk(t):
            if isinstance(node, ast.Assign):
                v = node.value
                if isinstance(v, ast.Constant) and v.value == CANONICAL_LITERAL:
                    for tgt in node.targets:
                        if isinstance(tgt, ast.Name):
                            literals.append({"name": tgt.id, "line": node.lineno})
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in ("insert", "append"):
                    base = node.func.value
                    if (isinstance(base, ast.Attribute) and base.attr == "path"
                            and isinstance(base.value, ast.Name) and base.value.id == "sys"):
                        if first_insert is None or node.lineno < first_insert:
                            first_insert = node.lineno
        after = []
        if first_insert is not None:
            for node in ast.walk(t):
                if isinstance(node, ast.Import):
                    for a in node.names:
                        if node.lineno > first_insert and a.name.split(".")[0] in mods:
                            after.append({"module": a.name.split(".")[0], "line": node.lineno})
                elif isinstance(node, ast.ImportFrom):
                    if node.level == 0 and node.module and node.lineno > first_insert:
                        if node.module.split(".")[0] in mods:
                            after.append({"module": node.module.split(".")[0], "line": node.lineno})
        after.sort(key=lambda r: r["line"])
        rows.append({"file": rel, "present": True, "literals": literals,
                     "first_insert": first_insert, "repo_modules_after": after,
                     "n_after": len(after)})
    return rows


def m2(tree):
    """Importable top-level names vs the stdlib. A collision would let a rooted insert shadow a
    non-repository name, which is a strictly worse failure than importing the wrong repo module."""
    names = repo_modules(tree)
    std = set(getattr(sys, "stdlib_module_names", ()))
    return {"importable": len(names), "stdlib_collisions": sorted(names & std),
            "python": sys.version.split()[0]}


def m3(tree):
    """Read the status directly. NEVER through a pipe -- $? would be the pipe's."""
    t = tree / "docs" / "orchestration" / "verify_hash_bindings.py"
    if not t.is_file():
        return {"present": False}
    cp = subprocess.run([sys.executable, str(t)], capture_output=True, text=True, cwd=str(tree))
    return {"present": True, "rc": cp.returncode,
            "all_intact": "ALL BINDINGS INTACT" in cp.stdout}


def git(tree, *a):
    cp = subprocess.run(["git", "-C", str(tree), *a], capture_output=True, text=True)
    return cp.returncode, cp.stdout.strip()


def m4(tree, upstream):
    """Identity holds; the behind-count DRIFTS and is never quotable without its date."""
    rc, head = git(tree, "rev-parse", "HEAD")
    if rc != 0:
        return {"is_git": False}
    _, porc = git(tree, "status", "--porcelain")
    lines = [l for l in porc.splitlines() if l.strip()]
    out = {"is_git": True, "head": head, "dirty": len(lines),
           "untracked": sum(1 for l in lines if l.startswith("??")),
           "modified": sum(1 for l in lines if not l.startswith("??"))}
    rc, cnt = git(tree, "rev-list", "--left-right", "--count", f"{upstream}...HEAD")
    if rc == 0 and cnt:
        b, a = cnt.split()
        out["behind"] = int(b); out["ahead"] = int(a); out["upstream"] = upstream
    return out


def m5(tree):
    """The .sh half: unconditional REPO= assignments, and the activator's source root."""
    nd = tree / "nd-unfolding"
    repo_assign, code_root_activator, env_root_activator, missing = [], [], [], []
    import re
    pat = re.compile(r"^\s*(export\s+)?REPO=")
    for name in LAUNCHERS:
        f = nd / name
        if not f.is_file():
            missing.append(name); continue
        txt = f.read_text(encoding="utf-8", errors="replace")
        if any(pat.match(l) for l in txt.splitlines()):
            repo_assign.append(name)
        if 'source "${CODE_ROOT}/setup_salloc_env.sh"' in txt:
            code_root_activator.append(name)
        if 'source "${ENV_ROOT}/setup_salloc_env.sh"' in txt:
            env_root_activator.append(name)
    return {"n": len(LAUNCHERS), "missing": missing, "repo_assign": repo_assign,
            "activator_from_code_root": code_root_activator,
            "activator_from_env_root": env_root_activator}


def m6(tree):
    """Does the guard emit evidence that it LOOKED, and is a zero a measurement or a default?

    THREE STATES, NOT TWO, and they must never collapse into one boolean. A substring test for the
    `else 0` default reports "no hits" both when the default was removed AND when the whole inventory
    write is absent -- and the canonical checkout is the second case: its `mnv_guarded_run.py` counts
    resolutions but writes no inventory at all, so "hole closed" would be exactly backwards. That is
    this campaign's named substring failure, committed by this very function's first version.
    """
    f = tree / "nd-unfolding" / "mnv_guarded_run.py"
    if not f.is_file():
        return {"present": False, "state": "FILE ABSENT"}
    txt = f.read_text(encoding="utf-8", errors="replace")
    lines = txt.splitlines()
    counts = "self.checked" in txt
    writes = [i + 1 for i, l in enumerate(lines) if '"checked"' in l and ":" in l]
    defaulted = [i + 1 for i, l in enumerate(lines)
                 if "guard.checked" in l and "else 0" in l]
    if not writes:
        state = "NO INVENTORY WRITE -- the guard counts but emits nothing; the vacuity question " \
                "cannot even be asked of this tree"
    elif defaulted:
        state = "WRITTEN BUT DEFAULTED -- a containment-path zero is a default, not a measurement"
    else:
        state = "WRITTEN AND MEASURED"
    return {"present": True, "n_lines": len(lines), "counts_resolutions": counts,
            "inventory_write_lines": writes, "else_zero_default_lines": defaulted,
            "state": state}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tree", required=True, help="the tree to measure. No default, deliberately.")
    ap.add_argument("--upstream", default="origin/main", help="for M-4's drifting behind-count")
    ap.add_argument("--label", default="", help="what this tree IS, printed with every number")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    tree = pathlib.Path(a.tree).resolve()
    if not tree.is_dir():
        sys.exit(f"no such tree: {tree}")
    res = {"label": a.label, "tree": str(tree), "M-1": m1(tree), "M-2": m2(tree),
           "M-3": m3(tree), "M-4": m4(tree, a.upstream), "M-5": m5(tree), "M-6": m6(tree)}
    if a.json:
        print(json.dumps(res, indent=2)); return
    print(f"=== {a.label or 'tree'}: {tree}")
    print(f"--- M-1 ({len(M1_FILES)} files)")
    for r in res["M-1"]:
        if not r["present"]:
            print(f"    {r['file']:<52} ABSENT"); continue
        lit = ",".join(f"{l['name']}@{l['line']}" for l in r["literals"]) or "-"
        print(f"    {r['file']:<52} literal={lit:<18} insert={r['first_insert']} "
              f"repo_mods_after={r['n_after']}")
    print(f"--- M-2  importable={res['M-2']['importable']} "
          f"stdlib_collisions={len(res['M-2']['stdlib_collisions'])} py={res['M-2']['python']}")
    print(f"--- M-3  {res['M-3']}")
    print(f"--- M-4  {res['M-4']}")
    print(f"--- M-5  {res['M-5']}")
    print(f"--- M-6  {res['M-6']}")


if __name__ == "__main__":
    main()
