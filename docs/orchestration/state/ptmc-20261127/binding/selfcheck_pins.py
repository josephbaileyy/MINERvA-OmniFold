#!/usr/bin/env python3
"""PTMC-BINDING-1 self-check: the scorer's own check_bytes, imported from the merge commit's bytes (a git archive of M's
2d-unfolding/ptmc), run on the deploy tree built at M with the bound PINS.json. It must pass; one flipped tree digest
and one flipped own digest must each STOP with C-PINS. Also: PINS.txt's make_tree.sh value equals own["make_tree.sh"].

  python3 selfcheck_pins.py --repo REPO --merge M --tree BUILT_TREE --pins PINS.json --pins-txt PINS.txt [--rows ROWS]

check_bytes also hashes the rows file. r3's rows file lives on pscratch. Without --rows, that one clause runs on a
stand-in file whose digest temporarily replaces CONST["ROWS_SHA"] and the copy's "rows". It is labelled as such, and
the PINS.json rows value is checked statically against CONST["ROWS_SHA"] instead.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    for k in ("--repo", "--tree", "--pins", "--pins-txt"):
        ap.add_argument(k, type=Path, required=True)
    ap.add_argument("--merge", required=True)
    ap.add_argument("--rows", type=Path)
    a = ap.parse_args()
    tmp = Path(tempfile.mkdtemp(prefix="ptmc-selfcheck-"))
    tar = subprocess.run(["git", "-C", str(a.repo), "archive", a.merge, "2d-unfolding/ptmc"], check=True,
                         capture_output=True).stdout
    tarfile.open(fileobj=io.BytesIO(tar)).extractall(tmp)
    sys.path.insert(0, str(tmp / "2d-unfolding" / "ptmc"))
    import ptmc_score as S
    assert Path(S.__file__).resolve().parent == (tmp / "2d-unfolding" / "ptmc").resolve()
    print(f"ptmc_score imported from git archive {a.merge} 2d-unfolding/ptmc: {S.__file__}")
    pins = json.loads(a.pins.read_text())
    results = []

    def run(label, p, want_stop=None):
        if a.rows is not None:
            args, ctx = SimpleNamespace(tree=a.tree, rows=a.rows, rows_sha256=p["rows"]), mock.patch.dict(S.CONST, {})
        else:
            stand = tmp / "rows-standin.npz"
            stand.write_bytes(b"stand-in for r3's oofvc_rows.npz (not on this machine)\n")
            d = hashlib.sha256(stand.read_bytes()).hexdigest()
            p = dict(p, rows=d)
            args, ctx = SimpleNamespace(tree=a.tree, rows=stand, rows_sha256=d), mock.patch.dict(S.CONST, {"ROWS_SHA": d})
        try:
            with ctx:
                S.check_bytes(args, p)
            got = "PASS"
        except S.Stop as e:
            got = f"STOP: {e}"
        ok = (got == "PASS") if want_stop is None else got.startswith("STOP: " + want_stop)
        results.append(ok)
        print(f"[{'ok' if ok else 'FAIL'}] {label}: {got}")

    run("check_bytes on the built tree with the bound PINS.json", pins)
    flip = copy.deepcopy(pins)
    flip["tree"]["2d-unfolding/re2/re2_driver.py"] = "0" * 64
    run("one flipped tree digest (the driver)", flip, "C-PINS: the deploy tree's 2d-unfolding/re2/re2_driver.py")
    flip = copy.deepcopy(pins)
    flip["own"]["make_tree.sh"] = "0" * 64
    run("one flipped own digest (make_tree.sh)", flip, "C-PINS: the scorer's own make_tree.sh")
    rows_static = pins["rows"] == S.CONST["ROWS_SHA"]
    results.append(rows_static)
    print(f"[{'ok' if rows_static else 'FAIL'}] PINS.json rows == M's CONST['ROWS_SHA'] ({S.CONST['ROWS_SHA'][:8]})"
          + ("" if a.rows is not None else "; the rows clause above ran on a stand-in (r3's file is on pscratch)"))
    txt = {ln.split()[0]: ln.split()[-1] for ln in a.pins_txt.read_text().splitlines() if ln.strip()}
    same = txt.get("make_tree.sh") == pins["own"]["make_tree.sh"]
    results.append(same)
    print(f"[{'ok' if same else 'FAIL'}] PINS.txt make_tree.sh {txt.get('make_tree.sh', '')[:8]} == PINS.json "
          f"own make_tree.sh {pins['own']['make_tree.sh'][:8]}")
    print(f"SELF-CHECK: {sum(results)} of {len(results)} ok")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
