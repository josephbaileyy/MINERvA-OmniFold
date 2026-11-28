#!/usr/bin/env python3
"""PTMC-BINDING-1: write the scorer's PINS.json (ptmc_score.py --pins) with every value computed from the merge
commit's objects and the deploy tree built from them, none typed.

  python3 write_pins_json.py --repo REPO --merge M --tree BUILT_TREE --make-tree-log LOG --out PINS.json

- own:  sha256 of `git show M:2d-unfolding/ptmc/<f>` for ptmc_score.py's OWN_FILES (read from M's ptmc_score.py).
- tree: sha256 of each of ptmc_score.py's TREE_FILES in BUILT_TREE: make_tree.sh's output at M, built with
        ptmc_remote.sh's staging root, as the remote setup builds it. Each value must equal make_tree's own listing.
        The driver must be make_tree's PTMC_SHA; config.json must carry ptmc_remote.sh's $R/stage and LIB_SHA.
- rows: ptmc_score.py's CONST["ROWS_SHA"], equal to ptmc_run.py's PINS["rows"] and ptmc_remote.sh's ROWS_SHA.
- join: ptmc_run.py's PINS["join"], equal to ptmc_remote.sh's JOIN_SHA.
- roounfold_lib_sha256: the built config.json's inputs.roounfold_lib_sha256, equal to ptmc_remote.sh's LIB_SHA.
Any disagreement is a refusal (exit 3) and nothing is written.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

PT = "2d-unfolding/ptmc"


def show(repo: Path, rev: str, path: str) -> bytes:
    return subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"], check=True, capture_output=True).stdout


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def assigned(src: str, name: str):
    """The value assigned to a module-level name, by the AST."""
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return node.value
    raise SystemExit(f"REFUSED: no module-level {name}")


def dict_constant(node, key: str) -> str:
    for k, v in zip(node.keys, node.values):
        if isinstance(k, ast.Constant) and k.value == key:
            return ast.literal_eval(v)
    raise SystemExit(f"REFUSED: no {key!r} in the dict")


def shell_value(text: str, name: str) -> str:
    vals = re.findall(rf"^{name}=(\S+)$", text, re.M)
    if len(vals) != 1:
        raise SystemExit(f"REFUSED: {name} is assigned {len(vals)} times")
    return vals[0]


def need(cond, why):
    if not cond:
        print(f"REFUSED: {why}", file=sys.stderr)
        sys.exit(3)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--merge", required=True)
    ap.add_argument("--tree", type=Path, required=True)
    ap.add_argument("--make-tree-log", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    m = subprocess.run(["git", "-C", str(a.repo), "rev-parse", "--verify", f"{a.merge}^{{commit}}"], check=True,
                       capture_output=True, text=True).stdout.strip()
    score = show(a.repo, m, f"{PT}/ptmc_score.py").decode()
    run = show(a.repo, m, f"{PT}/ptmc_run.py").decode()
    remote = show(a.repo, m, f"{PT}/launch/ptmc_remote.sh").decode()
    make_tree = show(a.repo, m, f"{PT}/make_tree.sh").decode()
    tree_files = ast.literal_eval(assigned(score, "TREE_FILES"))
    own_files = ast.literal_eval(assigned(score, "OWN_FILES"))
    rows_const = dict_constant(assigned(score, "CONST"), "ROWS_SHA")
    run_pins = ast.literal_eval(assigned(run, "PINS"))
    r, lib_sha = shell_value(remote, "R"), shell_value(remote, "LIB_SHA")
    ptmc_sha = shell_value(make_tree, "PTMC_SHA")
    print(f"merge commit {m}")
    print(f"OWN_FILES {list(own_files)}; TREE_FILES {len(tree_files)} files; ptmc_remote.sh R={r}")

    own = {f: sha(show(a.repo, m, f"{PT}/{f}")) for f in own_files}
    listing = {}
    for line in a.make_tree_log.read_text().splitlines():
        mm = re.fullmatch(r"([0-9a-f]{64})  (\S+)", line)
        if mm:
            listing[mm.group(2)] = mm.group(1)
    tree = {f: sha((a.tree / f).read_bytes()) for f in tree_files}
    for f in tree_files:
        need(listing.get(f) == tree[f], f"the built {f} ({tree[f][:8]}) is not make_tree's listed {listing.get(f)}")
    need(tree[tree_files[0]] == ptmc_sha, f"the built driver is not make_tree's PTMC_SHA {ptmc_sha[:8]}")
    cfg = json.loads((a.tree / "2d-unfolding/ref_c2c1/config.json").read_text())
    need(cfg["inputs"]["staging"]["root"] == f"{r}/stage", f"config.json's staging root is not {r}/stage")
    roounfold = cfg["inputs"]["roounfold_lib_sha256"]
    need(roounfold == lib_sha, f"config.json's roounfold_lib_sha256 is not ptmc_remote.sh's LIB_SHA")
    need(cfg["code_sha256"].get(tree_files[0]) == ptmc_sha, "config.json does not pin the built driver")
    need(rows_const == run_pins["rows"] == shell_value(remote, "ROWS_SHA"), "the rows pins disagree")
    need(run_pins["join"] == shell_value(remote, "JOIN_SHA"), "the join pins disagree")
    pins = {"tree": tree, "own": own, "rows": rows_const, "join": run_pins["join"], "roounfold_lib_sha256": roounfold}
    need(not a.out.exists(), f"{a.out} exists")
    a.out.write_text(json.dumps(pins, indent=1, sort_keys=True) + "\n")
    print(f"checks passed: tree = make_tree's listing (8/8); driver = PTMC_SHA {ptmc_sha[:8]}; config staging root "
          f"{r}/stage; roounfold = LIB_SHA {lib_sha[:8]}; rows = CONST = ptmc_run = ptmc_remote; join = ptmc_run = "
          f"ptmc_remote")
    print(f"wrote {a.out} sha256 {sha(a.out.read_bytes())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
