#!/usr/bin/env python3
"""REGRADE's sixteen-cell capture (REGRADE-DECLARATION.md rev 2, section 5), on a Perlmutter login node.

Calls ``ll5d_b.setup``, ``ll5d_b.remade`` and ``ll5d_b.toy_errors`` of the deploy at LL5D's readout commit M_L, each
imported unchanged from ``<deploy>/nd-unfolding`` (the T2A capture pattern; nothing is patched), and writes per
evaluation (g18/ar23 x minus2/all) the operands the local driver needs: E (300 x 16), X_T, s1's f, C_T, C_e,
C_model_abs, the Gaussian sum, and each draw law's values and probabilities in ``remade``'s order.

Read discipline (section 5):
* before anything is read, every listed path is stat'ed (size, mtime, atime, inode);
* the S1 assembly and the flux constraint are hashed through ``fd_1b_inv.sha256_noatime`` against their pins; every
  ``null_roles`` and ``toys`` row of hpss_ll5d_u_list.tsv is hashed the same way against its pin;
* the deploy is at M_L, clean, and its bound files (ll5d_b.py, ll5d.py, fd_1b_*.py, s1_assemble.py, the definition
  and the cmodel json) are at the readout's bound digests;
* the bound functions then read the products themselves (O_NOATIME); afterwards every listed path is stat'ed again
  and nothing may have moved (atime moved [] is required).
Any failure writes STOP.json and exits 8, and no capture is kept.

  python3 -B ll5d_regrade_capture.py --deploy D --staged S --unfolds U --constraint C --list L --out OUT

MEASURES: the capture only. CANNOT AUTHORIZE: a grade, a reading, any wording.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

M_L = "4231b14de5ea693e92cb31b1358a816b5c2f6625"
S1_SHA = "db000707780d4d6da65389be9adedfd9a3ba6552a255f6ce81ccbdd0b8eb72a4"
CONSTRAINT_SHA = "e38ad7d28354d071577113a18c8c569f88b6239f7fb193d20285273f172fc0c2"
LIST_SHA = "980bb95e20eac386a220bb7d0dbb16a5a3477248688f9a72bc07671a7ad5842d"
BOUND = {   # the LL5D readout's bound.sha256 lines (receipts-ll5d/readout/package/connect-readout.sh:81-104), the ones read
    "nd-unfolding/ll5d.py": "2b0224c6fe52c5bb2d3fe64d461ac9edb80ebd191b0ab2f892dec605a0b56a14",
    "nd-unfolding/ll5d_b.py": "24312ca86f9e70ed86699772d634c19d9bcacb2bb87bff5aaa8c9f7c2661f3cb",
    "nd-unfolding/fd_1b_mc.py": "936e1957d330e24d3eaab5f6c53d30b5be42a96f76daac07d527be97c0af30e2",
    "nd-unfolding/fd_1b_null.py": "ec1402db5cbb5ca3002d7e45a714319d90a8b93654005d688b304a69caab4d38",
    "nd-unfolding/fd_1b_inv.py": "71b3903aa1329807af7e48b29b4ffd3336ad637d4b8c7e43ae0a6cbe28bcdf1f",
    "nd-unfolding/fd_1b_score.py": "c6c9a45fa93c6590c4fdf0d9b7d29f01cccf97b281e469fa29a3d2f34b4618fd",
    "nd-unfolding/fd_1b_toys.py": "869a65c3bcce1a3b56ecd197ecdf3b6cf2741e0611f91b582c3064f67967bc08",
    "nd-unfolding/s1_assemble.py": "b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7",
    "nd-unfolding/pv-ladder/readouts/h2_definition.json":
        "b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89",
    "nd-unfolding/pv-ladder/readouts/cmodel_5d.json": "3cfdc6a5b8c6cea5f99b4678e27f6ca5f7973ee57a79b9d139798f0751cfcd60",
}
TRUTHS = ("g18", "ar23")
N_TOYS, N_CELLS = 300, 16


class Stop(RuntimeError):
    pass


def sha256_plain(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def stat4(p: str) -> list[int]:
    s = os.stat(p)
    return [s.st_size, s.st_mtime_ns, s.st_atime_ns, s.st_ino]


def read_list(path: Path) -> list[tuple[str, str, str]]:
    if sha256_plain(path) != LIST_SHA:
        raise Stop(f"the list {path} is not {LIST_SHA}")
    with open(path) as fh:
        rows = [tuple(l.rstrip("\n").split("\t")) for l in fh if l.strip()]
    return [r for r in rows if r[0] in ("null_roles", "toys")]


def check_deploy(deploy: Path) -> dict:
    head = subprocess.run(["git", "-C", str(deploy), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    if head != M_L:
        raise Stop(f"deploy HEAD {head} is not M_L {M_L}")
    dirty = subprocess.run(["git", "-C", str(deploy), "status", "--porcelain", "--untracked-files=no"],
                           capture_output=True, text=True).stdout.strip()
    if dirty:
        raise Stop(f"deploy has tracked changes: {dirty[:200]}")
    bad = {k: sha256_plain(deploy / k) for k in BOUND if sha256_plain(deploy / k) != BOUND[k]}
    if bad:
        raise Stop(f"bound files differ: {bad}")
    return {"head": head, "bound_ok": sorted(BOUND)}


def capture(a) -> dict:
    import numpy as np
    rec = {"schema": "regrade-crep/capture/1", "M_L": M_L, "host": os.uname().nodename,
           "start_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    rec["deploy"] = check_deploy(a.deploy)
    sys.path.insert(0, str(a.deploy / "nd-unfolding"))
    import fd_1b_inv as inv
    import ll5d
    import ll5d_b
    rows = read_list(a.list)
    s1_path = a.staged / "s1" / "s1_assembly.npz"
    watched = [str(s1_path), str(a.constraint)] + [r[2] for r in rows]
    before = {p: stat4(p) for p in watched}
    if inv.sha256_noatime(s1_path) != S1_SHA:
        raise Stop("C-PIN: s1_assembly.npz")
    if inv.sha256_noatime(a.constraint) != CONSTRAINT_SHA:
        raise Stop("C-PIN: the flux constraint")
    bad = [r[2] for r in rows if inv.sha256_noatime(Path(r[2])) != r[1]]
    if bad:
        raise Stop(f"C-PIN: {len(bad)} products differ from their pins, e.g. {bad[:3]}")
    want = {f"ll5d_{t}_toy_{rd}_{s}.npz" for t in TRUTHS for rd in ll5d.READINGS for s in ll5d.TOY_SEEDS[t]}
    have = {Path(r[2]).name for r in rows if r[0] == "toys"}
    if have != want:
        raise Stop(f"the list's toys are not the declared {len(want)}")
    rec["pins"] = {"s1_assembly": S1_SHA, "constraint": CONSTRAINT_SHA, "list": LIST_SHA, "products_checked": len(rows)}
    ns = argparse.Namespace(staged=a.staged, definition=a.deploy / "nd-unfolding/pv-ladder/readouts/h2_definition.json",
                            cmodel_json=a.deploy / "nd-unfolding/pv-ladder/readouts/cmodel_5d.json",
                            flux_constraint=a.constraint, unfolds=a.unfolds)
    s1, U, frac, minus, w = ll5d_b.setup(ns)
    outs = {}
    for t in TRUTHS:
        for rd in ll5d.READINGS:
            rm = ll5d_b.remade(a.unfolds, t, s1, U, w, frac, rd)
            E, draws, X_true, nat = ll5d_b.toy_errors(a.unfolds, t, rd, U, rm, s1["f"])
            E = np.asarray(E, np.float64)
            if E.shape != (N_TOYS, N_CELLS) or not np.all(np.isfinite(E)):
                raise Stop(f"{t}/{rd}: E is {E.shape} or not finite")
            arrays = {"E": E, "X_T": np.asarray(rm["X_T"], np.float64), "f": np.asarray(s1["f"], np.float64),
                      "C_T": rm["C_T"], "C_e": rm["C_e"], "C_model_abs": rm["C_model_abs"], "gauss": rm["gauss"],
                      "law_names": np.array([n for n, _, _ in rm["laws"]])}
            for i, (_, law, _) in enumerate(rm["laws"]):
                arrays[f"law_{i}_values"], arrays[f"law_{i}_probs"] = law.values, law.probs
            p = a.out / f"capture_{t}_{rd}.npz"
            tmp = a.out / f".capture_{t}_{rd}.tmp.npz"
            np.savez(tmp, **arrays)
            os.replace(tmp, p)
            outs[p.name] = sha256_plain(p)
    after = {p: stat4(p) for p in watched}
    moved = [p for p in watched if before[p][2] != after[p][2]]
    changed = [p for p in watched if before[p][:2] != after[p][:2] or before[p][3] != after[p][3]]
    rec.update({"outputs": outs, "watched": len(watched), "atime_moved": moved, "changed": changed,
                "end_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "code_sha256": sha256_plain(Path(__file__))})
    if moved or changed:
        raise Stop(f"atime moved {len(moved)}, changed {len(changed)}: {(moved + changed)[:3]}")
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="ll5d_regrade_capture.py", allow_abbrev=False)
    for k in ("deploy", "staged", "unfolds", "constraint", "list", "out"):
        ap.add_argument(f"--{k}", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        print(f"refusing: {a.out} exists", file=sys.stderr)
        return 2
    a.out.mkdir(parents=True)
    try:
        rec = capture(a)
    except Exception as e:                       # noqa: BLE001 - any failure is a STOP with no capture kept
        for p in a.out.glob("capture_*.npz"):
            p.unlink()
        (a.out / "STOP.json").write_text(json.dumps({"stop": f"{type(e).__name__}: {e}"}, indent=1) + "\n")
        print(f"STOP: {type(e).__name__}: {e}", file=sys.stderr)
        return 8
    (a.out / "capture-manifest.json").write_text(json.dumps(rec, indent=1) + "\n")
    print(json.dumps({"outputs": rec["outputs"], "atime_moved": rec["atime_moved"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
