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

SHELL PINS. Receipts are not the only place code is frozen by hash. Launchers and
final-writers carry their own `EXPECTED_<ROLE>_SHA=` constants and abort on
mismatch, and until 2026-07-31 nothing walked them -- so when b3751cc and f6a9e8e
rewrote `gate2_target_runtime.py` and `fullevent_fps_dataloader.py`, the pins in
`run_gate2_target_validator.sh` went stale silently and made that route
unrunnable. The receipt-backed Gate-4 pair broke in the same commits and was
loud, because this file already covered it. Shell pins are now collected from the
comparison sites themselves, which is the only place the pin is unambiguously
tied to the file it pins (the constant names do not map to the variable names --
`EXPECTED_BASE_G2_VAL_SHA` guards `$BASE_G2_VALIDATOR`).

A stale pin is not repaired by editing the hash. The constant records what the
gate ran against; moving it to match the working tree converts the guard into a
no-op and destroys the evidence. Re-issue the owning gate and record the move.

Exit 0 if every resolvable binding matches, 1 otherwise.
"""
import argparse
import glob
import hashlib
import json
import os
import re
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


# Minimum EXPECTED_*_SHA guards the shell collector must still resolve to files in
# the checkout. Raise it when launchers add pins; lowering it needs the same
# justification as deleting a guard, because that is what it does.
#
# COUNT ONLY PINS ON TRACKED FILES. This host resolves 17, but 5 of those are pins
# on artifacts that are NOT in git -- G2_FPS_MEFHC_P12.npz twice and the compiled
# MINERvA101/opt/bin/runEventLoopOmniFold three times -- which localize() resolves
# here only because this scratch checkout happens to hold them. A fresh clone, or
# this one after a scratch purge, resolves 12. Setting the floor to the observed 17
# would therefore make the guard fail on any checkout without a 9.9 GB dump and a
# built binary, and the obvious way out of THAT is lowering the floor, which is the
# one move the docstring forbids. 12 is the count every checkout can honour.
# Was 10, which was likewise exactly the tracked count before
# sbatch_powered_closure.sh started pinning its driver and preflight in the one-line
# idiom collect_shell can actually see (2026-08-05).
# Raised 12 -> 13 on 2026-08-06: the concurrent session's `sbatch_b1_niter4_scan48.sh`
# (committed in 82968d4) pins `closure_b1_rate_injection.py`, a tracked source file that
# every checkout holds, so the tracked count grew by one and
# test_powered_closure_preflight.py::test_pin_floor_covers_these_pins went red on
# `13 != 12`. Raising to match is what that test prescribes; verified locally that the
# verifier still resolves 13 and reports ALL BINDINGS INTACT rather than going BLIND.
SHELL_PIN_FLOOR = 13


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


# A pin is only credible where it is USED, so pairing is read off the comparison
# line rather than from the constant's name. Both hashing idioms in the tree are
# accepted, and the indirection through a temporary (`g=$(sha_of "$BIN"); [[ "$g"
# == ... ]]`) stays on one line in every current site.
_SHA_OF = re.compile(r'(?:sha_of|sha256sum)\s+"\$\{?(\w+)\}?"')
_PIN_USE = re.compile(r'\$\{?(EXPECTED_[A-Z0-9_]*_SHA)\}?')
_PIN_DEF = re.compile(r'^\s*(EXPECTED_[A-Z0-9_]*_SHA)=["\']?([0-9a-f]{64})["\']?\s*$', re.M)
_VAR_DEF = re.compile(r'^\s*(\w+)=["\']?([^"\'\s|;]+)["\']?\s*$', re.M)


def _expand(value, env, depth=0):
    """Resolve ${REPO}/... style assignments against the script's own constants."""
    if depth > 5:
        return value
    out = re.sub(r'\$\{(\w+)\}|\$(\w+)',
                 lambda m: env.get(m.group(1) or m.group(2), m.group(0)), value)
    return _expand(out, env, depth + 1) if out != value else out


def collect_shell(text, src, out):
    """Harvest (path, sha256, src) from `EXPECTED_*_SHA` guards in a shell script."""
    pins = dict(_PIN_DEF.findall(text))
    if not pins:
        return
    env = {k: v for k, v in _VAR_DEF.findall(text) if not k.startswith("EXPECTED_")}
    for line in text.splitlines():
        # Deduped, because the guards restate both operands in their failure text
        # (`[[ "$g" == "$EXPECTED_BIN_SHA" ]] || die "drift: $g != $EXPECTED_BIN_SHA"`).
        # Counting raw occurrences reads that as two pins and drops the line, which
        # silently cost the entire evloop launcher family on the first pass -- the
        # collector reported a clean 6 while walking none of them.
        files, used = set(_SHA_OF.findall(line)), set(_PIN_USE.findall(line))
        # One file against one pin is what a real comparison looks like. Anything
        # else is an echo, an argv splat, or a self-comparison of two staged
        # copies -- none of which bind a pin to a file.
        if len(files) != 1 or len(used) != 1 or not used <= set(pins):
            continue
        target = _expand(env.get(next(iter(files)), ""), env)
        if target:
            out.append((target, pins[next(iter(used))], src))


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

    shell_pairs = []
    for f in (glob.glob(os.path.join(a.root, "docs/**/*.sh"), recursive=True)
              + glob.glob(os.path.join(a.root, "nd-unfolding/**/*.sh"), recursive=True)
              + glob.glob(os.path.join(a.root, "2d-unfolding/**/*.sh"), recursive=True)):
        try:
            collect_shell(open(f).read(), os.path.relpath(f, a.root), shell_pairs)
        except OSError:
            continue
    pairs += shell_pairs

    seen, ok, new_bad, known_bad, unresolved = set(), 0, [], [], 0
    for p, want, src in pairs:
        lp = localize(p, a.root)
        if lp is None:
            unresolved += 1
            continue
        rel = os.path.relpath(lp, a.root)
        # Receipts that pin the same file to the same hash are deduped as noise,
        # but a shell pin is a SEPARATE remediation site: repairing the receipt
        # leaves the launcher's constant stale, and collapsing them would hide
        # exactly that. Dedupe within a source kind, never across.
        # ...and never across shell SITES either: two launchers pinning the same
        # runner are two constants to edit, so collapsing them hides half the
        # remediation. Receipts still dedupe, where repeats are genuinely noise.
        key = (rel, want, src if src.endswith(".sh") else "")
        if key in seen:
            continue
        seen.add(key)
        if sha256(lp) == want:
            ok += 1
        elif rel in KNOWN_PREEXISTING:
            known_bad.append((rel, src))
        else:
            new_bad.append((rel, want, sha256(lp), src))

    # The shell collector parses source rather than reading a schema, so it can go
    # blind if the launchers change idiom -- and a collector that silently matches
    # nothing reports ALL BINDINGS INTACT, which is the failure mode this whole
    # file exists to catch. Resolving zero shell pins is therefore an error, not a
    # quiet zero. The floor is deliberately the count that exists today.
    shell_resolved = sum(1 for p, _, _ in shell_pairs if localize(p, a.root))
    blind = shell_resolved < SHELL_PIN_FLOOR

    print(f"resolved {ok + len(new_bad) + len(known_bad)} bindings "
          f"({unresolved} unresolvable: data files, off-repo artifacts, binaries)")
    print(f"  {ok} OK")
    print(f"  {shell_resolved} of them from EXPECTED_*_SHA guards in *.sh "
          f"({len(shell_pairs)} pins seen, floor {SHELL_PIN_FLOOR})")
    if blind:
        print(f"\n*** SHELL PIN COLLECTOR WENT BLIND ***\n"
              f"  resolved {shell_resolved}, expected at least {SHELL_PIN_FLOOR}.\n"
              f"  Either pins were deleted, or a launcher changed hashing idiom and\n"
              f"  the parser no longer sees its guards. Do NOT lower the floor to\n"
              f"  make this pass -- an unwalked pin is how the Gate-2 pair went stale.")
    if known_bad:
        print(f"  {len(known_bad)} known pre-existing drift (submit-time provenance):")
        for rel, src in known_bad:
            print(f"      {rel}  <- {os.path.basename(src)}")
    for rel, want, got, src in new_bad:
        print(f"\nMISMATCH {rel}\n  want {want}\n  got  {got}\n  from {src}")

    failed = bool(new_bad) or blind or (a.strict and bool(known_bad))
    print("\n" + ("*** BINDINGS BROKEN ***" if failed else "ALL BINDINGS INTACT"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
