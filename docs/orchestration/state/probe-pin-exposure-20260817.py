#!/usr/bin/env python3
"""BEN-384 in executable form: for each candidate file, perturb it, run the real gate, revert.

A grep for the filename is NOT the test -- verify_hash_bindings.py decides what a binding is, and
BEN-384's whole lesson is that the pin is invisible from the row and from the code. So this asks
the gate the question it answers, once per file, and restores byte-exactly afterwards.
"""
import pathlib
import subprocess
import sys

REPO = pathlib.Path("/Users/josephbailey/local-research/MINERvA-OmniFold/.claude/worktrees/lane-e-causes-3-4")
GATE = REPO / "docs/orchestration/verify_hash_bindings.py"

CANDIDATES = {
    "OI-96":  ["nd-unfolding/pet/check_canonical_designation.py",
               "docs/orchestration/verify_hash_bindings.py"],
    "OI-12":  ["nd-unfolding/uq_fps/corrected/test_fps_corrected_uq.py",
               "nd-unfolding/p4_lib.py"],
    "OI-61":  ["nd-unfolding/pet/train_fullevent_nominal.py",
               "nd-unfolding/pet/train_fullevent_replica.py"],
    "OI-64C": ["nd-unfolding/pet/check_canonical_designation.py"],
    "OI-60":  ["nd-unfolding/pet/fullevent_fps_dataloader.py"],   # known-pinned positive control
}


def gate_ok():
    r = subprocess.run([sys.executable, str(GATE)], cwd=REPO, capture_output=True, text=True)
    return "ALL BINDINGS INTACT" in r.stdout


def probe(rel):
    p = REPO / rel
    if not p.is_file():
        return "ABSENT"
    original = p.read_bytes()
    try:
        p.write_bytes(original + b"\n# pin-probe\n")
        return "PINNED" if not gate_ok() else "not pinned"
    finally:
        p.write_bytes(original)
        assert p.read_bytes() == original


def main():
    if not gate_ok():
        print("BASELINE IS ALREADY BROKEN -- probe results would be meaningless. Stopping.")
        return 1
    print("baseline: ALL BINDINGS INTACT\n")
    seen = {}
    for item, files in CANDIDATES.items():
        for rel in files:
            if rel not in seen:
                seen[rel] = probe(rel)
            print(f"{item:8} {seen[rel]:12} {rel}")
    print()
    print("re-check after all probes:", "INTACT" if gate_ok() else "BROKEN -- INVESTIGATE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
