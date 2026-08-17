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

FIELD PINS (OI-96, added 2026-08-17). A hash binding freezes CONTENT. It cannot
freeze a POINTER, and the canonical-nominal designation is a pointer: promotion
there moves no bytes, so the safety argument is entirely that the receipts naming
the protected artifacts keep naming them. That was enforced by
`check_canonical_designation.py`'s WHOLE-FILE occurrence count of the namespace --
a proxy for pinning a path field, and MEASURED WRONG IN BOTH DIRECTIONS by mutating
the receipt and running that guard:

    repoint `products/canonical_baseline/path` to a SIBLING inside the same
    protected directory   -> count stays 2, guard SILENT   <- the BEN-133 repoint
                                                              class it exists for
    delete the prose sentence at :245
                          -> count falls to 1, guard RED   <- a legitimate edit

Silent on the defect, loud on the innocent edit. So this file now also checks 44
declared FIELD values across the 22 RECORD-FROZEN JSON receipts, derived by
`state/regen_canonical_namespace_field_pins.py` and stored in
`state/canonical-namespace-field-pins-20260817.json`. A repoint is loud; prose is
invisible to them.

These pin the VALUE OF A FIELD, not the bytes of an artifact -- most targets are
cluster products under /pscratch and are absent from any checkout, so a digest pin
cannot run here at all. Green means the receipts still POINT where they pointed. It
says NOTHING about whether the artifacts changed, exactly as BEN-325 says of the
count this replaces.

Exit 0 if every resolvable binding matches, 1 otherwise.
"""
import argparse
import glob
import hashlib
import importlib.util
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
# Raised 13 -> 15 on 2026-08-07: `sbatch_powered_closure_budget_probe.sh` (the D2 under-fitting
# probe) pins BOTH `closure_powered_truth_reweight.py` and `preflight_powered_closure.py` in the
# one-line idiom collect_shell can see, and both are tracked source files every checkout holds, so
# the tracked count grew by exactly two. Counted before raising, by running the collector over the
# same three globs the test uses against `git ls-files`: 15, itemised. Raising to match is what the
# test prescribes; the direction that is forbidden is lowering it to make a red test pass, which
# would be deleting a guard.
SHELL_PIN_FLOOR = 15


# Minimum RECEIPT bindings the json collector must still resolve. Added 2026-08-13
# (lane A, on lane D's BEN-184) because until then `failed` consulted no receipt
# count at all -- `failed = bool(new_bad) or blind or (strict and known_bad)`, where
# `blind` covered only shell pins. Resolve ZERO receipt bindings and this file
# printed ALL BINDINGS INTACT, which is the exact failure its own docstring says it
# exists to catch, one layer in.
#
# WHY IT IS NOT THE EXACT COUNT, unlike SHELL_PIN_FLOOR. Shell pins only ever grow:
# launchers add guards, so an exact floor fires only when a guard is deleted.
# Receipt bindings also SHRINK, legitimately -- retiring a superseded receipt means
# renaming `sha256` -> `sha256_at_issue`, which is precisely what drops it from
# collect(). An exact floor would therefore go red on a lane doing the documented
# right thing, whose only remedy would be lowering the floor: the one move forbidden
# here. So this floor is set BELOW the current count on purpose.
#
# THE ARITHMETIC, so the margin is auditable rather than a vibe. 152 resolve today
# and all 152 are git-tracked (measured against `git ls-files`; no scratch-only
# artifact inflates it, so a fresh clone resolves 152 too -- the hazard
# SHELL_PIN_FLOOR's note is about does not apply). Erosion per legitimate retirement
# is ~1, not the ~17 pins a receipt carries, because the successor re-pins the same
# files at the same hashes and receipts dedupe on (path, hash): retiring
# ...gate4-...20260812.json removed exactly one binding, the driver's superseded
# digest. 140 therefore leaves ~12 retirements of headroom, while a collector that
# has gone blind resolves ~0 and trips this immediately.
#
# WHAT THIS FLOOR DOES NOT DO, stated because the gap is the reason it was asked for.
# A floor catches COLLAPSE, not EROSION. Coverage sliding 152 -> 140 one correct
# retirement at a time is invisible to it, and at 140 the pressure to lower returns.
# Erosion needs a different instrument -- a per-commit coverage delta, or requiring a
# retirement to state the bindings it removes. Tracked as OI-66; do not read a green
# here as evidence that coverage held.
#
# Raise this when receipts add durable bindings. Lowering it needs the same
# justification as deleting a receipt, because that is what it launders.
RECEIPT_BINDING_FLOOR = 140


FIELD_PIN_FILE = "docs/orchestration/state/canonical-namespace-field-pins-20260817.json"

# Minimum FIELD pins that must resolve. Same device as the two floors above and for the
# same reason: the pin file is DATA, so a truncation, a bad merge, or a regeneration that
# parsed nothing yields `pins: []`, and a loop over an empty list reports success. Zero
# pins is the state this check exists to make impossible, not a quiet pass.
#
# BELOW the current count on purpose, like RECEIPT_BINDING_FLOOR and unlike
# SHELL_PIN_FLOOR: field pins legitimately SHRINK when a receipt leaves the RECORD-FROZEN
# inventory, and an exact floor would go red on a lane doing the documented right thing,
# whose only remedy would be lowering it. 44 resolve today across 22 receipts; 30 leaves
# room for real retirements while a collector that has gone blind resolves ~0 and trips it.
FIELD_PIN_FLOOR = 30


FIELD_PIN_GENERATOR = "docs/orchestration/state/regen_canonical_namespace_field_pins.py"
# Minimum RECORD-FROZEN JSON entries the coverage parse must find. Without this, a
# reformat of that INVENTORY makes the regex match nothing, the "uncovered receipts" set
# is empty, and the coverage check reports success by seeing no receipts at all -- the
# same shape as the two collector floors above, in the guard that was added to fix that
# shape. 22 parse today; 15 leaves room for legitimate retirement.
FROZEN_JSON_FLOOR = 15


def _pin_rules(root):
    """Load the GENERATOR's rules rather than re-implementing them.

    The first version of the coverage check below re-implemented "does this receipt carry a
    namespace path" as a regex over the raw file, and immediately produced FIVE false
    positives on receipts whose only occurrence is a SENTENCE -- the prose-versus-field
    confusion this whole check exists to fix, reproduced inside it within the hour. Two
    predicates for one concept is exactly what `OI-65` (lane A's) is about; importing makes
    divergence impossible instead of merely unlikely.
    """
    path = os.path.join(root, FIELD_PIN_GENERATOR)
    spec = importlib.util.spec_from_file_location("_cnfp", path)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check_field_pins(root):
    """Verify each declared FIELD value still reads as declared. Returns (ok, bad, missing).

    Three distinguishable failures, kept separate because they need different remedies:
      MISMATCH      the field moved -- a repoint. Do NOT regenerate the pin file to match.
      UNRESOLVED    the pointer no longer exists in the receipt (a rename or a deletion).
      NO RECEIPT    the receipt itself is gone.
    A pointer that resolves to a non-string is UNRESOLVED, not a silent skip: `if the key is
    present, check it` is the vacuous form (PB2), and absence is what this check is about.
    """
    pin_path = os.path.join(root, FIELD_PIN_FILE)
    try:
        doc = json.load(open(pin_path))
    except (OSError, json.JSONDecodeError) as e:
        return 0, [(FIELD_PIN_FILE, "", f"pin file unreadable: {e}", "")], 0
    ok, bad, missing = 0, [], 0
    for pin in doc.get("pins", []):
        rel, ptr, want = pin.get("receipt"), pin.get("pointer"), pin.get("expected")
        full = os.path.join(root, rel or "")
        if not rel or not os.path.isfile(full):
            bad.append((rel, "", "NO RECEIPT", want))
            continue
        try:
            node = json.load(open(full))
        except (OSError, json.JSONDecodeError) as e:
            bad.append((rel, "", f"receipt unreadable: {e}", want))
            continue
        cur = node
        for key in ptr or []:
            try:
                cur = cur[key]
            except (KeyError, IndexError, TypeError):
                cur = None
                break
        loc = "/".join(str(x) for x in (ptr or []))
        if not isinstance(cur, str):
            bad.append((rel, loc, "UNRESOLVED", want))
            missing += 1
        elif cur != want:
            bad.append((rel, loc, cur, want))
        else:
            ok += 1
    return ok, bad, missing


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
    receipt_resolved = 0
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
        if not src.endswith(".sh"):
            receipt_resolved += 1
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

    # Same device, for the receipt side, which had none until 2026-08-13.
    # `receipt_resolved` is incremented inside the comparison loop above, so it counts
    # comparisons ACTUALLY PERFORMED on receipt bindings, post-dedup. Deriving it as
    # `total - shell_resolved` would be wrong: shell_resolved is counted pre-dedup off
    # `shell_pairs`, and mixing the two agrees on this tree only by coincidence.
    receipt_blind = receipt_resolved < RECEIPT_BINDING_FLOOR

    print(f"resolved {ok + len(new_bad) + len(known_bad)} bindings "
          f"({unresolved} unresolvable: data files, off-repo artifacts, binaries)")
    print(f"  {ok} OK")
    print(f"  {shell_resolved} of them from EXPECTED_*_SHA guards in *.sh "
          f"({len(shell_pairs)} pins seen, floor {SHELL_PIN_FLOOR})")
    print(f"  {receipt_resolved} of them from receipt bindings "
          f"(floor {RECEIPT_BINDING_FLOOR})")

    field_ok, field_bad, _field_missing = check_field_pins(a.root)
    field_blind = (field_ok + len(field_bad)) < FIELD_PIN_FLOOR

    # COVERAGE, not just correctness. A receipt ADDED to the RECORD-FROZEN inventory and
    # never pinned is invisible to the loop above -- it checks the pins it has, so
    # under-coverage reports as a clean pass. That is BEN-322's shape reproduced inside the
    # guard written to fix it, so it is checked rather than trusted.
    rules = _pin_rules(a.root)
    frozen = rules.frozen_json_receipts(a.root) if rules else []
    try:
        covered = {p.get("receipt") for p in json.load(
            open(os.path.join(a.root, FIELD_PIN_FILE))).get("pins", [])}
    except (OSError, json.JSONDecodeError):
        covered = set()
    # A receipt with NO namespace path FIELD legitimately contributes no pins, so absence
    # from `covered` is a defect only for receipts that DO carry one -- re-derived with the
    # generator's own rule, not with a cheaper proxy.
    uncovered = []
    for rel in frozen:
        full = os.path.join(a.root, rel)
        if rel in covered or not os.path.isfile(full):
            continue
        try:
            if rules.namespace_path_fields(json.load(open(full))):
                uncovered.append(rel)
        except (OSError, json.JSONDecodeError):
            continue
    frozen_blind = len(frozen) < FROZEN_JSON_FLOOR

    print(f"{field_ok} canonical-namespace FIELD pins verified "
          f"(floor {FIELD_PIN_FLOOR}) over {len(covered)} of {len(frozen)} RECORD-FROZEN "
          f"JSON receipts -- these pin a POINTER, not bytes; "
          f"green says the receipts still point where they pointed")
    if frozen_blind:
        print(f"\n*** RECORD-FROZEN INVENTORY PARSE WENT BLIND ***\n"
              f"  parsed {len(frozen)} JSON entries from {DESIGNATION_INVENTORY}, expected\n"
              f"  at least {FROZEN_JSON_FLOOR}. The label or its formatting changed, and an\n"
              f"  empty parse makes the coverage check below pass by seeing nothing.")
    if uncovered:
        print(f"\n*** RECORD-FROZEN RECEIPTS CARRY NAMESPACE PATHS AND ARE NOT PINNED ***")
        for rel in uncovered:
            print(f"      {rel}")
        print(f"  Regenerate with state/regen_canonical_namespace_field_pins.py -- this is\n"
              f"  the ONE case where regenerating is the correct remedy, because the pin set\n"
              f"  grew. It is NOT the remedy for a FIELD PIN mismatch below.")
    if field_blind:
        print(f"\n*** FIELD PIN COLLECTOR WENT BLIND ***\n"
              f"  saw {field_ok + len(field_bad)}, expected at least {FIELD_PIN_FLOOR}.\n"
              f"  The pin file is data: a truncation or a regeneration that parsed nothing\n"
              f"  yields an empty list, and a loop over it reports success. Do NOT lower\n"
              f"  this floor -- regenerate only for a real inventory change (OI-96).")
    for rel, loc, got, want in field_bad:
        print(f"\nFIELD PIN {rel}  {loc}\n  want {want}\n  got  {got}\n"
              f"  A repoint is NOT repaired by regenerating the pin file -- that adopts\n"
              f"  whatever the receipt now says, which is this file's own forbidden move\n"
              f"  one level out. Re-issue the receipt, or justify the move in the commit.")
    if receipt_blind:
        print(f"\n*** RECEIPT BINDING COLLECTOR WENT BLIND ***\n"
              f"  resolved {receipt_resolved}, expected at least "
              f"{RECEIPT_BINDING_FLOOR}.\n"
              f"  Either receipts were retired en masse or collect() no longer sees\n"
              f"  their shape. Do NOT lower the floor to make this pass -- resolving\n"
              f"  zero receipt bindings printed ALL BINDINGS INTACT until 2026-08-13,\n"
              f"  which is this file's own failure mode one layer in (BEN-184).")
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

    failed = (bool(new_bad) or blind or receipt_blind
              or bool(field_bad) or field_blind
              or bool(uncovered) or frozen_blind
              or (a.strict and bool(known_bad)))
    print("\n" + ("*** BINDINGS BROKEN ***" if failed else "ALL BINDINGS INTACT"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
