#!/usr/bin/env python3
"""RS1-BINDING-2 addendum A1: the resume of RS1's full run in a fresh root, after attempt 1's teardown crash.

Python 3.6-compatible (the cluster's /usr/bin/python3 is 3.6.15): no `from __future__ import annotations` and no
subscripted builtins in annotations, which 3.6 evaluates when a function is defined.

Attempt 1 (job 60972000, receipt fd/rounding-stability-20261106/receipts/full-attempt-1/) stays intact as evidence.
This module stages a fresh root from it and names each task's outputs; it never runs a fit, and the bound RS1 code
(``rounding_mechanism_probe.py``, ``rounding_mechanism_analyze.py``, ``sbatch_rs1.sh``) is unchanged.

    rs1_a1_plan.py stage --old OLD --new NEW     NEW already holds queue.tsv and dry.tsv (the bound probe's ``tasks``
                                                 with --runs NEW/runs); writes NEW/log-dry (verbatim), NEW/runs (the
                                                 verified products), NEW/runs-attempt1, NEW/plan.tsv, NEW/copies.sha256
    rs1_a1_plan.py verify --root NEW             every 'done' task's files still at their copies.sha256 lines
    rs1_a1_plan.py expect <task argv>            the products and sidecars a queue line writes, one path per line

A task is **done** only if every product and sidecar it declares verifies by digest: a dry task against attempt 1's
``log-dry/SHA256SUMS``, a full task that ended in attempt 1 against attempt 1's ``log-full/SHA256SUMS``. Its files are
copied (O_NOATIME where the platform has it) into NEW/runs and re-hashed. Every other task is **todo**; any of its
files attempt 1 left are copied to NEW/runs-attempt1/<id>/ for the comparison only (the director's ruling 4), never
into NEW/runs, where the runner would skip them.
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Tuple

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))

SCHEMA = "rs1-a1-plan/1"


class Refusal(RuntimeError):
    pass


def sha256_path(p: Path) -> str:
    h = hashlib.sha256()
    flags = os.O_RDONLY | getattr(os, "O_NOATIME", 0)
    fd = os.open(p, flags)
    with os.fdopen(fd, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 22), b""):
            h.update(block)
    return h.hexdigest()


def copy_noatime(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(src, os.O_RDONLY | getattr(os, "O_NOATIME", 0))
    with os.fdopen(fd, "rb") as fi, open(dst, "wb") as fo:
        shutil.copyfileobj(fi, fo, 1 << 22)


def product_name(tag: str, b, j) -> str:
    """s5p_numerics.product_name, for one experiment (RS1's tasks carry no --pseudo-seeds)."""
    return f"{tag}_b{'-' if b is None else b}_j{'-' if j is None else j}.npz"


def expected(argv: List[str]) -> List[Path]:
    """Every file one RS1 queue line writes: per pair, the product and its trace sidecar (rounding_mechanism_probe
    ``write_product``), under the runner's --out with its --tag."""
    if "--" not in argv:
        raise Refusal("not an RS1 task line")
    rest = argv[argv.index("--") + 1:]

    def opt(name):
        if rest.count(name) != 1:
            raise Refusal(f"{name} must appear once")
        return rest[rest.index(name) + 1]
    pairs = [t.split("=", 1)[1] for t in rest if t.startswith("--pairs=")]
    if len(pairs) != 1:
        raise Refusal("an RS1 task carries exactly one --pairs=")
    out, tag = Path(opt("--out")), opt("--tag")
    files = []
    for item in pairs[0].split(","):
        b, j = item.split(":")
        p = out / product_name(tag, None if b == "-" else int(b), None if j == "-" else int(j))
        files += [p, p.with_name(p.name[:-4] + ".trace.json.gz")]
    return files


def read_queue(path: Path) -> List[Tuple[str, List[str]]]:
    out = []
    for line in Path(path).read_text().splitlines():
        if line and not line.startswith("#"):
            cols = line.split("\t")
            out.append((cols[0], cols[3:]))
    return out


def read_sums(path: Path) -> Dict[str, str]:
    out = {}
    for line in Path(path).read_text().splitlines():
        if line.strip():
            h, name = line.split(None, 1)
            out[name] = h
    return out


def stage(old: Path, new: Path) -> dict:
    """Copy log-dry verbatim and every verified task's files; plan the rest."""
    old, new = Path(old), Path(new)
    for need in (old / "log-dry" / "DONE", old / "log-dry" / "SHA256SUMS", old / "log-full" / "SHA256SUMS",
                 new / "queue.tsv", new / "dry.tsv"):
        if not need.is_file():
            raise Refusal(f"missing {need}")
    for x in ("log-dry", "runs", "runs-attempt1", "plan.tsv", "copies.sha256", "log-full"):
        if (new / x).exists():
            raise Refusal(f"{new / x} exists: staging is once only")
    if (old / "log-dry" / "FAILED").exists() or (old / "log-dry" / "STOP").exists():
        raise Refusal("attempt 1's dry run left FAILED or STOP")
    dry_ids = {i for i, _ in read_queue(new / "dry.tsv")}
    sums = {"dry": read_sums(old / "log-dry" / "SHA256SUMS"), "full": read_sums(old / "log-full" / "SHA256SUMS")}
    shutil.copytree(old / "log-dry", new / "log-dry")
    for f in (old / "log-dry").rglob("*"):
        if f.is_file() and sha256_path(f) != sha256_path(new / "log-dry" / f.relative_to(old / "log-dry")):
            raise Refusal(f"log-dry copy of {f.name} differs")
    plan, copies = [], []
    for tid, argv in read_queue(new / "queue.tsv"):
        rel = [p.relative_to(new) for p in expected(argv)]     # runs/<arm>/<file>
        kind = "dry" if tid in dry_ids else "full"
        ended = (old / ("log-dry" if kind == "dry" else "log-full") / f"{tid}.end").is_file()
        ok = ended and all(str(r) in sums[kind] and (old / r).is_file() and sha256_path(old / r) == sums[kind][str(r)]
                           for r in rel)
        if ok:
            for r in rel:
                copy_noatime(old / r, new / r)
                h = sha256_path(new / r)
                if h != sums[kind][str(r)]:
                    raise Refusal(f"copy of {r} does not match its line")
                copies.append(f"{h}  {r}")
            plan.append((tid, "done", f"attempt1-{kind}"))
        else:
            left = [r for r in rel if (old / r).is_file()]
            for r in left:
                copy_noatime(old / r, new / "runs-attempt1" / tid / r.name)
            plan.append((tid, "todo", "not ended" if not ended else "did not verify"))
    (new / "copies.sha256").write_text("\n".join(copies) + "\n")
    (new / "plan.tsv").write_text("# id\tstatus\tsource (RS1-BINDING-2 addendum A1)\n"
                                  + "\n".join("\t".join(p) for p in plan) + "\n")
    summary = {"schema": SCHEMA, "tasks": len(plan), "done": sum(p[1] == "done" for p in plan),
               "todo": [p[0] for p in plan if p[1] == "todo"], "copied_files": len(copies),
               "attempt1_left": sorted(d.name for d in (new / "runs-attempt1").iterdir())
               if (new / "runs-attempt1").exists() else []}
    (new / "stage.json").write_text(json.dumps(summary, indent=1) + "\n")
    return summary


def verify(root: Path) -> List[str]:
    """Problems with the staged files: each copies.sha256 line must still hold."""
    root = Path(root)
    bad = []
    for name, h in read_sums(root / "copies.sha256").items():
        p = root / name
        if not p.is_file() or sha256_path(p) != h:
            bad.append(name)
    return bad


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["expect"]:
        try:
            print("\n".join(str(p) for p in expected(argv[1:])))
        except Refusal as exc:
            print(f"refusing: {exc}", file=sys.stderr)
            return 2
        return 0
    ap = argparse.ArgumentParser(prog="rs1_a1_plan.py", allow_abbrev=False)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("stage", allow_abbrev=False)
    s.add_argument("--old", type=Path, required=True)
    s.add_argument("--new", type=Path, required=True)
    v = sub.add_parser("verify", allow_abbrev=False)
    v.add_argument("--root", type=Path, required=True)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "stage":
            print(json.dumps(stage(a.old, a.new)))
            return 0
        bad = verify(a.root)
        print(json.dumps({"verified": not bad, "bad": bad}))
        return 0 if not bad else 4
    except Refusal as exc:
        print(f"refusing: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
