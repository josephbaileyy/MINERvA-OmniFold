#!/usr/bin/env python3
"""Step 2 pin exposure for the C_stat^data route, DIFFERENTIALLY.

The absolute condition ("run verify_hash_bindings.py and check it passes") is unavailable:
the gate is red on the cluster for two pre-existing reasons (BEN-255 / D's baseline), so
green is unreachable and BROKEN carries no information. LOCALLY it is green, which is the
same finding from the other side -- the gate returns different verdicts in different trees.

So: capture the LOCAL baseline mismatch set, perturb each candidate, and ask whether the set
GREW. Growth is the signal; the absolute verdict is not.
"""
import os
import re
import subprocess
import sys

import pathlib
REPO = str(pathlib.Path(__file__).resolve().parents[3])
GATE = os.path.join(REPO, "docs/orchestration/verify_hash_bindings.py")

CANDIDATES = [
    "nd-unfolding/pet/train_fullevent_replica.py",
    "nd-unfolding/pet/build_fullevent_replica_target.py",
    "nd-unfolding/pet/extract_fullevent_replica.py",
    "nd-unfolding/pet/fullevent_fps_dataloader.py",
    "nd-unfolding/pet/reconcile_gate5_family.py",
]

MISMATCH = re.compile(r"^MISMATCH (\S+)", re.M)
FIELDPIN = re.compile(r"^FIELD PIN (\S+)", re.M)


def verdict():
    r = subprocess.run([sys.executable, GATE], cwd=REPO, capture_output=True, text=True)
    return (set(MISMATCH.findall(r.stdout)) | set(FIELDPIN.findall(r.stdout)),
            "ALL BINDINGS INTACT" in r.stdout)


base_set, base_green = verdict()
print(f"LOCAL baseline: {'green' if base_green else 'RED'}; "
      f"mismatch set = {sorted(base_set) or '{}'}")
print("(D's CLUSTER baseline for the same gate: {std_final5_candidate.root, "
      "train_fullevent_nominal.py} -- BEN-255, do not regenerate)\n")

print(f"{'file':52} {'digest':7} {'grew?':6} new members")
for rel in CANDIDATES:
    p = os.path.join(REPO, rel)
    if not os.path.isfile(p):
        print(f"{rel:52} ABSENT")
        continue
    d = subprocess.run(["shasum", "-a", "256", rel], cwd=REPO,
                       capture_output=True, text=True).stdout.split()[0]
    sites = subprocess.run(["git", "grep", "-l", d], cwd=REPO,
                           capture_output=True, text=True).stdout.split()
    orig = open(p, "rb").read()
    try:
        open(p, "wb").write(orig + b"\n# step2-probe\n")
        new_set, _ = verdict()
    finally:
        open(p, "wb").write(orig)
        assert open(p, "rb").read() == orig, f"RESTORE FAILED {rel}"
    grew = sorted(new_set - base_set)
    print(f"{rel:52} {len(sites):<7} {'YES' if grew else 'no':6} "
          f"{[os.path.basename(x) for x in grew] if grew else ''}")

after, _ = verdict()
print(f"\nre-check: set is {'unchanged' if after == base_set else 'CHANGED -- INVESTIGATE'}")
