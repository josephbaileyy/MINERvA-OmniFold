#!/usr/bin/env python3
"""OI-61(b): probe the edit that WORKS, not the edit the row names. They are in different
files, and only one of them is pinned.

WHY THIS EXISTS. `SWEEP-20260817` graded `OI-61(b)` -- *"pass a replica-specific tag"* --
as ROUTABLE to the unpinned side, because the row names `train_fullevent_replica.py` as
the edit site and that file is clean on both instruments. That grading is WRONG, and the
reason generalises past this item:

    THE FILE AN EDIT LIVES IN IS NOT NECESSARILY THE FILE THAT VALIDATES IT.

`train_fullevent_replica.py` calls `nominal.main([... "--tag", "nominal" ...])`, and
`train_fullevent_nominal.py` DECLARES the tag's domain:
`ap.add_argument("--tag", default="nominal", choices=["nominal", "floor"])`. So the
one-line change in the unpinned caller is REJECTED BY THE PINNED CALLEE -- measured, not
argued:

    $ python3 nd-unfolding/pet/train_fullevent_nominal.py --tag replica_07 ...
    error: argument --tag: invalid choice: 'replica_07' (choose from 'nominal', 'floor')
    exit 2

The working edit is therefore in the pinned file. This script applies the REAL MINIMAL
DIFF for each candidate -- not a comment append, because a comment cannot show that one
of the two diffs is the one that has to happen -- runs the real gate, and restores
byte-exactly.

Expected, and asserted at the end so a silent inversion cannot pass unnoticed:
  the edit the row names   -> gate stays GREEN   (and does not work)
  the edit that works      -> gate goes RED      (train_fullevent_nominal.py is pinned)
"""
import os
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[3]
GATE = REPO / "docs/orchestration/verify_hash_bindings.py"

EDITS = [
    ("the edit the ROW names", False,
     "nd-unfolding/pet/train_fullevent_replica.py",
     '            "--tag", "nominal",\n',
     '            "--tag", f"replica_{int(args.replica_index):02d}",\n'),
    ("the edit that makes it WORK", True,
     "nd-unfolding/pet/train_fullevent_nominal.py",
     '    ap.add_argument("--tag", default="nominal", choices=["nominal", "floor"],\n',
     '    ap.add_argument("--tag", default="nominal",\n'),
]


def gate_red():
    r = subprocess.run([sys.executable, str(GATE)], cwd=REPO,
                       capture_output=True, text=True)
    return "ALL BINDINGS INTACT" not in r.stdout


def main():
    if gate_red():
        print("BASELINE ALREADY RED -- every result below would be meaningless. Stopping.")
        return 1
    print("baseline: ALL BINDINGS INTACT\n")

    wrong = 0
    for label, expect_red, rel, old, new in EDITS:
        p = REPO / rel
        orig = p.read_bytes()
        # A missing anchor means the code moved. Fail loudly: a probe that silently
        # applies no diff reports GREEN and reads as "this edit is free" (BEN-344).
        assert old.encode() in orig, f"anchor not found in {rel} -- re-read the file"
        try:
            p.write_bytes(orig.replace(old.encode(), new.encode(), 1))
            red = gate_red()
        finally:
            p.write_bytes(orig)
            assert p.read_bytes() == orig, f"RESTORE FAILED for {rel} -- STOP AND FIX"
        ok = (red == expect_red)
        wrong += (not ok)
        print(f"{label:28} {rel:46} gate -> {'RED' if red else 'green':5} "
              f"{'ok' if ok else '*** NOT AS EXPECTED ***'}")

    print(f"\n{len(EDITS) - wrong}/{len(EDITS)} as expected")
    print("re-check after all probes:", "RED -- INVESTIGATE" if gate_red() else "INTACT")
    return 1 if wrong else 0


if __name__ == "__main__":
    sys.exit(main())
