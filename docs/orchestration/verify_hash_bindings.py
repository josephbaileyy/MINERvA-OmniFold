#!/usr/bin/env python3
"""Verify every file-hash binding recorded in any receipt against the checkout.

WHY THIS EXISTS. Gate receipts freeze code by sha256: Gate-2's canonical runtime
receipt binds `fullevent_fps_dataloader.py` and `gate2_target_runtime.py`, the
Gate-3 and Gate-4 launch-code gates each bind a launcher/driver/validator/test
set. Those freezes are the evidence that a gate passed against specific code, and
an ordinary-looking refactor can silently void them.

On 2026-07-28 a repo-root de-rooting refactor (commit 2732304) did exactly that,
breaking six bindings at once -- including both Gate-4 entry points and the
Gate-2 dataloader -- while every test still passed. Nothing in the suite noticed,
because the edits were behaviourally inert on Perlmutter (the derived root equals
the old literal there). Only the hashes changed. Run this before and after any
sweeping edit.

PATH REMAPPING. Receipts written on Perlmutter record absolute
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/...` paths. A naive existence check
skips those, which is how the Gate-2 dataloader binding was missed on a first
pass. Absolute paths under the known Perlmutter root are therefore remapped onto
the local checkout before hashing.

Exit 0 if every resolvable binding matches, 1 otherwise.
"""
import argparse
import glob
import hashlib
import json
import os
import sys

PERLMUTTER_ROOT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/"

# Bindings known to have drifted before 2026-07-28 and deliberately not "fixed":
# these receipts record what ran at submit time, and rewriting their hashes would
# falsify history. Listed so real regressions stay visible above the noise.
KNOWN_PREEXISTING = {
    "docs/orchestration/wakerctl.py",
    "docs/orchestration/test_wakerctl.py",
    "docs/orchestration/gate2_queue_hedge_controller.sh",
    "nd-unfolding/pet/sbatch_dump_g2_mefhc.sh",
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def collect(obj, src, out):
    """Harvest (path, sha256) pairs from the two shapes receipts actually use."""
    if isinstance(obj, dict):
        p = obj.get("path") or obj.get("file") or obj.get("script")
        s = obj.get("sha256") or obj.get("sha")
        if isinstance(p, str) and isinstance(s, str) and len(s) == 64:
            out.append((p, s, src))
        for k, v in obj.items():
            if k.endswith("_sha256") and isinstance(v, str) and len(v) == 64:
                base = k[:-len("_sha256")]
                for cand in (base, base + "_path", base + "_file"):
                    if isinstance(obj.get(cand), str):
                        out.append((obj[cand], v, src))
                        break
        for v in obj.values():
            collect(v, src, out)
    elif isinstance(obj, list):
        for v in obj:
            collect(v, src, out)


def localize(p, root):
    if p.startswith(PERLMUTTER_ROOT):
        p = p[len(PERLMUTTER_ROOT):]
    cand = os.path.join(root, p.lstrip("/"))
    return cand if os.path.isfile(cand) else None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
    ap.add_argument("--strict", action="store_true",
                    help="also fail on the known pre-existing drift")
    a = ap.parse_args()

    pairs = []
    for f in (glob.glob(os.path.join(a.root, "docs/**/*.json"), recursive=True)
              + glob.glob(os.path.join(a.root, "nd-unfolding/**/*.json"), recursive=True)):
        try:
            collect(json.load(open(f)), os.path.relpath(f, a.root), pairs)
        except (json.JSONDecodeError, OSError):
            continue

    seen, ok, new_bad, known_bad, unresolved = set(), 0, [], [], 0
    for p, want, src in pairs:
        lp = localize(p, a.root)
        if lp is None:
            unresolved += 1
            continue
        rel = os.path.relpath(lp, a.root)
        if (rel, want) in seen:
            continue
        seen.add((rel, want))
        if sha256(lp) == want:
            ok += 1
        elif rel in KNOWN_PREEXISTING:
            known_bad.append((rel, src))
        else:
            new_bad.append((rel, want, sha256(lp), src))

    print(f"resolved {ok + len(new_bad) + len(known_bad)} bindings "
          f"({unresolved} unresolvable: data files, off-repo artifacts, binaries)")
    print(f"  {ok} OK")
    if known_bad:
        print(f"  {len(known_bad)} known pre-existing drift (submit-time provenance):")
        for rel, src in known_bad:
            print(f"      {rel}  <- {os.path.basename(src)}")
    for rel, want, got, src in new_bad:
        print(f"\nMISMATCH {rel}\n  want {want}\n  got  {got}\n  from {src}")

    failed = bool(new_bad) or (a.strict and bool(known_bad))
    print("\n" + ("*** BINDINGS BROKEN ***" if failed else "ALL BINDINGS INTACT"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
