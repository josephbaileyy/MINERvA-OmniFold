#!/usr/bin/env python3
"""Regenerate the canonical-namespace FIELD pin file consumed by `verify_hash_bindings.py`.

WHY THIS EXISTS (OI-96). The canonical-nominal DESIGNATION moves no bytes, so its whole
safety argument is that the receipts naming the protected artifacts keep naming them. Until
now that was enforced by `check_canonical_designation.py`'s WHOLE-FILE occurrence count of
the namespace -- a proxy for pinning a path FIELD, and **wrong in both directions.**
Measured by mutating the receipt and running the incumbent guard, not argued:

    repoint `products/canonical_baseline/path` to a SIBLING in the same protected
    directory  ->  count stays 2, guard SILENT   <- the BEN-133 repoint class it exists for
    delete the prose sentence at :245            ->  count falls to 1, guard RED
                                                     <- an edit that is entirely legitimate

So it is silent on the defect and loud on the innocent edit. These pins replace the proxy
at field level: a repoint is loud, and prose is invisible to them.

DERIVED, NOT HAND-LISTED. A hand-list of 23 receipts is how an inventory goes stale, and
this namespace already has a finding about exactly that (`BEN-228`). The rule is
`check_canonical_designation.py`'s own: the namespace as a PATH SEGMENT with
`fullevent_nominal_annealed` excluded -- the sibling-directory trap that file documents.

REGENERATION IS NOT A REMEDY FOR A RED. If `verify_hash_bindings.py` reports a field-pin
mismatch, re-running this script makes it green by adopting whatever the receipt now says,
which is the same move the verifier's own docstring forbids for hashes: *"A stale pin is not
repaired by editing the hash."* Regenerate only when a receipt is legitimately added to or
removed from the RECORD-FROZEN inventory, and say so in the commit.
"""
import json
import os
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[3]
CHECK_REL = "nd-unfolding/pet/check_canonical_designation.py"
OUT_REL = "docs/orchestration/state/canonical-namespace-field-pins-20260817.json"

# The namespace as a PATH SEGMENT, `_annealed` excluded. Kept identical to
# check_canonical_designation.py's rule rather than imported: importing that module would
# make this generator depend on another lane's script loading cleanly, and the rule is two
# lines. If that file's rule changes, this comment is the place the divergence shows up.
NS = re.compile(r"fullevent_nominal(?!_annealed)/")


def namespace_path_fields(doc):
    """Every (pointer, value) in `doc` that is a FIELD naming a path in the namespace.

    THE ONE PLACE THIS RULE LIVES. `verify_hash_bindings.py` imports this function rather
    than re-implementing it, because the first version of its coverage check DID
    re-implement it -- as a regex over the raw file -- and immediately produced five false
    positives on receipts whose only namespace occurrence is a SENTENCE. That is the exact
    prose-versus-field confusion this whole item is about, reproduced inside the guard
    written to fix it, within the hour. Two predicates for one concept is `OI-65`'s (lane
    A's) shape, and the cheapest defence is that there be only one.
    """
    out = []

    def walk(o, ptr):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, ptr + [k])
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, ptr + [i])
        elif isinstance(o, str) and NS.search(o):
            # A FIELD naming a path, not a SENTENCE that mentions the namespace.
            if " " not in o.strip() and "/" in o:
                out.append((ptr, o))

    walk(doc, [])
    return out


def frozen_json_receipts(repo=REPO):
    """The RECORD-FROZEN JSON receipts in the designation inventory. Also the one place."""
    src = (pathlib.Path(repo) / CHECK_REL).read_text()
    return sorted(p for p, _n in re.findall(
        r'^\s*"([^"]+)":\s*\("RECORD-FROZEN",\s*(\d+)\)', src, re.M) if p.endswith(".json"))


def field_pins():
    frozen = frozen_json_receipts()
    if not frozen:
        raise SystemExit(
            "no RECORD-FROZEN entries parsed from the inventory -- the label or its "
            "formatting changed. Refusing to write an EMPTY pin file, which would read as "
            "'nothing to protect' and pass forever.")
    pins, scanned = [], 0
    for rel in frozen:
        full = REPO / rel
        if not full.is_file():
            raise SystemExit(f"RECORD-FROZEN receipt absent: {rel}")
        scanned += 1
        for ptr, val in namespace_path_fields(json.loads(full.read_text())):
            pins.append({"receipt": rel, "pointer": ptr, "expected": val})
    return pins, scanned


def main():
    pins, scanned = field_pins()
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                          capture_output=True, text=True).stdout.strip()
    doc = {
        "schema": "canonical-namespace-field-pins/v1",
        "why": (
            "OI-96. Pin the FIELD, not the file. The whole-file occurrence count it replaces "
            "is silent on an in-directory repoint and red on a prose deletion; both measured "
            "by mutation. See this generator's docstring."
        ),
        "scope": {
            "derived_from": CHECK_REL + " INVENTORY, entries labelled RECORD-FROZEN",
            "rule": ("every string field whose value names a path inside `fullevent_nominal/` "  # NS-EXEMPT: pattern literal, not a reference
                     "as a PATH SEGMENT, `fullevent_nominal_annealed` excluded"),
            "NOT_a_digest_pin": (
                "these pin the VALUE OF THE FIELD, not the bytes of the artifact. Most targets "
                "are cluster products under /pscratch and are absent from this checkout, so a "
                "digest pin cannot run here at all. A green run says the receipts still POINT "
                "where they pointed and says NOTHING about whether the artifacts changed -- the "
                "same disclaimer BEN-325 makes about the count."
            ),
            "regenerate": "docs/orchestration/state/regen_canonical_namespace_field_pins.py",
        },
        "derived_at_head": head,
        "receipts_scanned": scanned,
        "pin_count": len(pins),
        "pins": pins,
    }
    (REPO / OUT_REL).write_text(json.dumps(doc, indent=1) + "\n")
    print(f"wrote {len(pins)} field pins across {scanned} RECORD-FROZEN JSON receipts")
    print(f"  -> {OUT_REL}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
