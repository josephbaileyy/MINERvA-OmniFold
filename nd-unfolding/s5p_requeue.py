#!/usr/bin/env python3
"""s5p production: a resumed copy of a lane's queue with a new array throttle (a scheduling change only).

The resumed queue starts at the WAIT line of the batch whose job is currently queued or running (``--resume-label``)
and keeps every later line byte for byte except the value of ``--throttle`` in the meter's submit commands; nothing
before that wait line is kept, so no batch that was already submitted can be submitted again (the old runner is
stopped between batches; the new runner first waits for the same job to leave the scheduler). Fixed batches,
seeds, tables, estimator settings, stopping rules and terminal statuses are untouched by construction.

MEASURES: nothing. CANNOT AUTHORIZE: a launch (the meter admits).
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

THROTTLE = re.compile(r"--throttle \d+ ")


def requeue(lines: list[str], resume_label: str, throttle: int, note: str) -> list[str]:
    wait = [i for i, ln in enumerate(lines) if ln.startswith("until out=$(squeue") and f"-n s5p-{resume_label} " in ln]
    if len(wait) != 1:
        raise SystemExit(f"expected exactly one wait line for {resume_label}, found {len(wait)}")
    body = lines[wait[0]:]
    out = [f"# {note}"]
    for ln in body:
        new = THROTTLE.sub(f"--throttle {throttle} ", ln)
        if ln.startswith("#") and new != ln:
            raise SystemExit("a comment line carries a throttle")
        out.append(new)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--queue", type=Path, required=True)
    ap.add_argument("--resume-label", required=True)
    ap.add_argument("--throttle", type=int, required=True)
    ap.add_argument("--note", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    lines = a.queue.read_text().splitlines()
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text("\n".join(requeue(lines, a.resume_label, a.throttle, a.note)) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
