#!/usr/bin/env python3
"""Re-measure the OI-136 rooted-import populations on one tree, by the two existing instruments.

Read-only. It runs no producer, no ratchet test and no job. It reuses, by import, the AST scanner in
`nd-unfolding/tests/test_oi136_rooted_insert_ratchet.py` (`rooted_insert_files`, tracked `.py`) and
the classifier in `docs/orchestration/state/probe-oi136-sys-path-hijack-20260826.py` (by running its
CLI, which scans the working tree including untracked files). Neither instrument is re-typed here, so
this script cannot disagree with the ratchets about what a site is.

    python3 inventory.py <tree> <out.json>

Populations reported, each named by what it counts:

* `ast_sites`: tracked `.py` where the canonical literal REACHES `sys.path.insert(0, ...)`
  (the rooted ratchet's population).
* `probe_failopen`: `.py` in the working tree classified FAIL-OPEN by the probe (the fail-open
  ratchet's population), plus the probe's candidate / insert-but-not-rooted / no-insert counts.
* `rooted_listed` / `failopen_recorded`: what each ratchet currently names or pins.
* `insert_call_sites`: per AST site, the line of every position-0 insert the literal reaches. This is
  an occurrence count, not a file count.
* `adjacent_shapes`: tracked `.py` where the literal reaches `sys.path.insert(k != 0, ...)`,
  `sys.path.append(...)` or `site.addsitedir(...)`. These are outside both ratchets' definitions and
  are reported, not classified.
"""
import ast
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def insert_lines(tree, scanner, attrs=("insert",), position_zero=True):
    """Lines of `sys.path.<attr>(...)` / `site.addsitedir(...)` calls the literal reaches."""
    bound = scanner._rooted_names(tree)
    hits = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        base, attr = node.func.value, node.func.attr
        if attr == "addsitedir" and isinstance(base, ast.Name) and base.id == "site":
            args = node.args[:1]
        elif attr in attrs and isinstance(base, ast.Attribute) and base.attr == "path" \
                and isinstance(base.value, ast.Name) and base.value.id == "sys":
            if attr == "insert":
                if len(node.args) < 2:
                    continue
                zero = isinstance(node.args[0], ast.Constant) and node.args[0].value == 0
                if zero != position_zero:
                    continue
                args = node.args[1:2]
            else:
                args = node.args[:1]
        else:
            continue
        for arg in args:
            if (isinstance(arg, ast.Constant) and scanner._canonical_form(arg.value)) or any(
                    isinstance(n, ast.Name) and n.id in bound and node.lineno >= bound[n.id]
                    for n in ast.walk(arg)):
                hits.append(node.lineno)
    return sorted(set(hits))


def main():
    tree_root = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2])
    scanner = load(tree_root / "nd-unfolding/tests/test_oi136_rooted_insert_ratchet.py",
                   "_rooted_ratchet_under_measurement")
    failopen = load(tree_root / "nd-unfolding/tests/test_oi136_failopen_inventory_ratchet.py",
                    "_failopen_ratchet_under_measurement")
    if Path(scanner.REPO) != tree_root or Path(failopen.REPO) != tree_root:
        raise SystemExit(f"instrument REPO mismatch: {scanner.REPO} / {failopen.REPO} vs {tree_root}")

    read = lambda rel: (tree_root / rel).read_text(encoding="utf-8", errors="replace")
    ast_sites = scanner.rooted_insert_files(read)

    probe = subprocess.run([sys.executable, failopen.PROBE], cwd=tree_root,
                           capture_output=True, text=True)
    if probe.returncode != 0:
        raise SystemExit(f"probe exit {probe.returncode}; CANNOT CHECK\n{probe.stdout}{probe.stderr}")
    m = re.search(r"\[(\d+) \.py contain the hardcoded root; (\d+) FAIL-OPEN, (\d+) "
                  r"insert-but-not-rooted, (\d+) no insert", probe.stdout)
    probe_set = [p[2:] if p.startswith("./") else p for p in failopen.failopen_set(probe.stdout)]
    probe_digest = hashlib.sha256("".join("./" + r + "\n" for r in probe_set).encode()).hexdigest()

    listed = sorted(scanner.KNOWN_UNREPAIRED)
    reason_key = {v: k for k, v in scanner._R.items()}
    tracked = subprocess.run(["git", "-C", str(tree_root), "ls-files", "*.py"],
                             capture_output=True, text=True, check=True).stdout.split()
    call_sites, adjacent = {}, {}
    for rel in tracked:
        try:
            t = ast.parse(read(rel))
        except (SyntaxError, ValueError, OSError):
            continue
        if rel in ast_sites:
            call_sites[rel] = insert_lines(t, scanner)
        other = insert_lines(t, scanner, attrs=("insert",), position_zero=False) + \
            insert_lines(t, scanner, attrs=("append", "addsitedir"))
        if other:
            adjacent[rel] = sorted(set(other))

    union = sorted(set(ast_sites) | set(probe_set))
    record = {
        "tree": str(tree_root),
        "head": subprocess.run(["git", "-C", str(tree_root), "rev-parse", "HEAD"],
                               capture_output=True, text=True).stdout.strip(),
        "dirty_tracked": bool(subprocess.run(
            ["git", "-C", str(tree_root), "status", "--porcelain", "--untracked-files=no"],
            capture_output=True, text=True).stdout.strip()),
        "ast_sites": ast_sites,
        "ast_sites_n": len(ast_sites),
        "probe_counts": dict(zip(("candidates", "failopen", "insert_not_rooted", "no_insert"),
                                 map(int, m.groups()))) if m else None,
        "probe_failopen": probe_set,
        "probe_failopen_digest_as_ratchet_digests_it": probe_digest,
        "rooted_listed": {p: reason_key.get(scanner.KNOWN_UNREPAIRED[p], "?") for p in listed},
        "rooted_listed_n": len(listed),
        "failopen_recorded": [failopen.FAILOPEN_COUNT, failopen.FAILOPEN_SHA256],
        "ast_unlisted": [p for p in ast_sites if p not in scanner.KNOWN_UNREPAIRED],
        "ast_listed_but_clean": [p for p in listed if p not in ast_sites],
        "ast_only": sorted(set(ast_sites) - set(probe_set)),
        "probe_only": sorted(set(probe_set) - set(ast_sites)),
        "union_n": len(union),
        "insert_call_sites": call_sites,
        "insert_call_sites_n": sum(len(v) for v in call_sites.values()),
        "adjacent_shapes": adjacent,
    }
    out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
    for k in ("head", "dirty_tracked", "ast_sites_n", "probe_counts", "rooted_listed_n",
              "failopen_recorded", "ast_unlisted", "ast_listed_but_clean", "ast_only", "probe_only",
              "union_n", "insert_call_sites_n", "probe_failopen_digest_as_ratchet_digests_it"):
        print(f"{k}: {record[k]}")
    print(f"adjacent_shapes: {len(adjacent)} files")


if __name__ == "__main__":
    main()
