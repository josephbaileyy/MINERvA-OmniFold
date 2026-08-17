#!/usr/bin/env python3
"""Pin exposure for a candidate file, measured three ways -- because one way is wrong.

ORIGINALLY (2026-08-17, first pass) this file did one thing: perturb a candidate, run
`verify_hash_bindings.py`, restore. That found `BEN-384`'s second pinned file and it was
worth the seconds it cost. It was also INCOMPLETE IN TWO DIRECTIONS, and both were found
by extending it rather than by reading:

  1. Its coverage was bounded by the file list fed to it -- the files an OPEN_ITEMS row
     happens to NAME. `OI-64C`'s row names its edit site as `verify_executing_copy_is_committed.py`;
     the first pass probed `check_canonical_designation.py`, which is not that item's edit
     site at all, and reported it clean. A clean answer about the wrong file.
  2. It reported a BINARY -- pinned / not pinned -- and there are at least three states.
     `verify_hash_bindings.py` TOLERATES drift on four files (`KNOWN_PREEXISTING`), which
     are pinned and yet leave the gate green; and it CANNOT SEE role-keyed digests at all
     (`BEN-322`), so a file can be bound by an active comparator and probe "not pinned".

So the question "is this file pinned" has no single instrument. This file now runs three,
and reports what each one is FOR:

  INSTRUMENT 1 -- PATH SIDE, complete. Imports `verify_hash_bindings.py`'s OWN collectors
      and enumerates every file carrying a resolving binding, in one pass, for the whole
      tree. Answers: "will editing this turn the pre-commit gate red?"
  INSTRUMENT 2 -- DIGEST SIDE. `git grep <sha256 of the file>`. A pin IS a digest, so if a
      file's content hash is written down anywhere, something can compare against it --
      including the role-keyed receipts and hardcoded launcher constants instrument 1
      structurally cannot resolve. Answers: "who else has frozen this content?"
  INSTRUMENT 3 -- PERTURBATION. The original probe. It is now the VALIDATOR: instrument 1
      predicts each outcome in advance and the probe checks the prediction. A prediction
      that is merely printed alongside an observation is not a test; a disagreement here
      is a defect in instrument 1 and the run says so.

INSTRUMENT 2'S BLIND SPOT IS MEASURED, NOT ASSUMED. A file that has ALREADY drifted from
its pin has its OLD content recorded, so a digest search on its CURRENT content finds
nothing and it reads clean while being pinned. The four `KNOWN_PREEXISTING` files are
exactly that case and the run reports them, so the limit is visible in the output rather
than in a caveat nobody reads.

Nothing here writes: every perturbation is restored and byte-compared, and the gate is
re-checked at the end.
"""
import hashlib
import importlib.util
import json
import os
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[3]
GATE = REPO / "docs/orchestration/verify_hash_bindings.py"

# The files each remaining PET item's fix must actually TOUCH -- taken from the item's
# stated edit site, not from every path its row mentions. Where the map and the row name
# different sites, both are listed; that disagreement is the thing worth measuring.
CANDIDATES = {
    "OI-12":  ["nd-unfolding/uq_fps/corrected/test_fps_corrected_uq.py",
               "nd-unfolding/p4_lib.py"],
    "OI-57":  ["nd-unfolding/pet/train_fullevent_replica.py",
               "nd-unfolding/pet/train_fullevent_nominal.py",
               "nd-unfolding/pet/sbatch_gate5_replica_train_array.sh"],
    "OI-58":  ["nd-unfolding/pet/train_fullevent_replica.py",
               "nd-unfolding/pet/extract_fullevent_fps.py",
               "nd-unfolding/pet/train_fullevent_nominal.py"],
    "OI-60":  ["nd-unfolding/pet/fullevent_fps_dataloader.py",
               "nd-unfolding/pet/build_fullevent_replica_target.py",
               "nd-unfolding/pet/run_gate2_target_validator.sh"],
    "OI-61":  ["nd-unfolding/pet/train_fullevent_nominal.py",
               "nd-unfolding/pet/train_fullevent_replica.py",
               "nd-unfolding/tests/test_reconcile_gate5_family.py"],
    "OI-64A": ["docs/orchestration/verify_hash_bindings.py",
               "nd-unfolding/tests/test_hash_bindings.py"],
    "OI-65A": ["nd-unfolding/tests/test_hash_bindings.py",
               "docs/orchestration/verify_hash_bindings.py"],
    "OI-64C": ["nd-unfolding/pet/verify_executing_copy_is_committed.py",
               "nd-unfolding/pet/reconcile_gate5_family.py",
               "nd-unfolding/pet/sbatch_gate5_replica_train_array.sh"],
    "OI-65C": ["nd-unfolding/pet/reconcile_gate5_family.py",
               "nd-unfolding/pet/atomic_write.py",
               "nd-unfolding/pet/sbatch_gate5_target_family_reconcile.sh"],
    "OI-96":  ["nd-unfolding/pet/check_canonical_designation.py",
               "docs/orchestration/verify_hash_bindings.py"],
}

# Probed in the validation stage regardless of whether an item names them. The first two
# are KNOWN pinned (a negative from this run would mean the probe is broken); the next two
# are KNOWN pinned AND tolerated, so they must come back GREEN -- the case the original
# binary could not express; the last is expected clean on both instruments.
VALIDATION_EXTRAS = [
    "nd-unfolding/pet/fullevent_fps_dataloader.py",
    "nd-unfolding/pet/train_fullevent_nominal.py",
    "docs/orchestration/wakerctl.py",
    "docs/orchestration/test_wakerctl.py",
    "nd-unfolding/p4_lib.py",
]


def _load_gate():
    spec = importlib.util.spec_from_file_location("vhb", GATE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["vhb"] = mod
    spec.loader.exec_module(mod)
    return mod


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def build_inventory(vhb):
    """INSTRUMENT 1: every file carrying a binding the gate can resolve, whole tree."""
    import glob
    root = str(REPO)
    pairs = []
    for f in (glob.glob(os.path.join(root, "docs/**/*.json"), recursive=True)
              + glob.glob(os.path.join(root, "nd-unfolding/**/*.json"), recursive=True)):
        try:
            vhb.collect(json.load(open(f)), os.path.relpath(f, root), pairs)
        except (json.JSONDecodeError, OSError):
            continue
    receipt_pairs = list(pairs)
    shell_pairs = []
    for f in (glob.glob(os.path.join(root, "docs/**/*.sh"), recursive=True)
              + glob.glob(os.path.join(root, "nd-unfolding/**/*.sh"), recursive=True)
              + glob.glob(os.path.join(root, "2d-unfolding/**/*.sh"), recursive=True)):
        try:
            vhb.collect_shell(open(f).read(), os.path.relpath(f, root), shell_pairs)
        except OSError:
            continue
    inv = {}
    for kind, plist in (("receipt", receipt_pairs), ("shell", shell_pairs)):
        for p, _want, src in plist:
            lp = vhb.localize(p, root)
            if lp is None:
                continue
            rel = os.path.relpath(lp, root)
            e = inv.setdefault(rel, {"receipt": set(), "shell": set()})
            e[kind].add(src)
    for rel, e in inv.items():
        e["tolerated"] = rel in vhb.KNOWN_PREEXISTING
    return inv


def digest_sites(rel):
    """INSTRUMENT 2: who has recorded THIS content's digest, anywhere in the tree."""
    p = REPO / rel
    if not p.is_file():
        return None, []
    d = sha256(p)
    r = subprocess.run(["git", "grep", "-l", d], cwd=REPO,
                       capture_output=True, text=True)
    return d, sorted(s for s in r.stdout.split() if s)


def gate_red():
    r = subprocess.run([sys.executable, str(GATE)], cwd=REPO,
                       capture_output=True, text=True)
    return "ALL BINDINGS INTACT" not in r.stdout


def probe(rel):
    """INSTRUMENT 3: perturb, ask the real gate, restore byte-exactly."""
    p = REPO / rel
    if not p.is_file():
        return None
    original = p.read_bytes()
    try:
        p.write_bytes(original + b"\n# pin-probe\n")
        return gate_red()
    finally:
        p.write_bytes(original)
        assert p.read_bytes() == original, f"RESTORE FAILED for {rel} -- STOP AND FIX"


def main():
    vhb = _load_gate()
    if gate_red():
        print("BASELINE IS ALREADY RED -- every result below would be meaningless. Stopping.")
        return 1
    print("baseline: ALL BINDINGS INTACT\n")

    inv = build_inventory(vhb)
    print(f"### INSTRUMENT 1 -- {len(inv)} files in the tree carry a binding the gate resolves "
          f"({sum(1 for e in inv.values() if e['tolerated'])} of them tolerated-drift)\n")

    files = sorted({f for fs in CANDIDATES.values() for f in fs})
    dig = {f: digest_sites(f) for f in files}

    print("### PER-ITEM EXPOSURE")
    print(f"{'item':8} {'gate':10} {'digest':7} file")
    for item, fs in CANDIDATES.items():
        for rel in fs:
            e = inv.get(rel)
            if e is None:
                g = "clean"
            elif e["tolerated"]:
                g = "TOLERATED"
            else:
                g = "PINNED"
            n = len(dig[rel][1]) if dig[rel][0] else "-"
            print(f"{item:8} {g:10} {str(n):7} {rel}")
    print()

    print("### INSTRUMENT 2 detail -- where each candidate's CURRENT digest is recorded")
    for rel in files:
        d, sites = dig[rel]
        if d is None:
            print(f"  {rel}  ABSENT")
            continue
        print(f"  {rel}  sha256={d[:16]}...  {len(sites)} site(s)")
        for s in sites:
            print(f"      <- {s}")
    print()

    print("### INSTRUMENT 3 -- validating instrument 1 against the real gate")
    print("### prediction: perturbing F turns the gate RED iff F has a binding AND is not tolerated")
    print(f"{'file':58} {'pred':6} {'obs':6} verdict")
    disagree = 0
    probed = 0
    for rel in files + [f for f in VALIDATION_EXTRAS if f not in files]:
        e = inv.get(rel)
        pred = bool(e) and not e["tolerated"]
        obs = probe(rel)
        if obs is None:
            print(f"{rel:58} ABSENT")
            continue
        probed += 1
        ok = (pred == obs)
        disagree += (not ok)
        print(f"{rel:58} {str(pred):6} {str(obs):6} {'ok' if ok else '*** DISAGREE ***'}")
    # Counted from probes actually RUN, not from len(files)+len(extras) -- the two lists
    # overlap, and a denominator that overstates the work is the shape of BEN-077.
    print(f"\ninstrument 1 predicted the gate correctly on "
          f"{probed - disagree}/{probed} probes; {disagree} disagreement(s)")

    print("\n### INSTRUMENT 2'S BLIND SPOT, MEASURED")
    print("### these four ARE pinned and have ALREADY drifted, so a digest search on their")
    print("### CURRENT content cannot find the pin. A 0 here is the false negative, exhibited.")
    for rel in sorted(vhb.KNOWN_PREEXISTING):
        d, sites = digest_sites(rel)
        if d is None:
            print(f"  {rel:52} ABSENT")
            continue
        print(f"  {rel:52} in_inventory={rel in inv}  digest_sites={len(sites)}")

    print("\nre-check after all probes:", "RED -- INVESTIGATE" if gate_red() else "INTACT")
    return 0


if __name__ == "__main__":
    sys.exit(main())
