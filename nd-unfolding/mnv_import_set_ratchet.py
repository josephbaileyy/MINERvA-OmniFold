#!/usr/bin/env python3
"""P-2 and P-4: read the verdict off the P-1 inventories, never off an exit code.

WHY THIS EXISTS AT ALL, AND WHY ITS ABSENCE WAS THE HOLE.
`mnv_guarded_run.py --inventory` now WRITES a resolved-origin record per process. A record nobody
reads is the `OI-64` shape -- "an unwired check is a check nobody runs" -- and the contract is
explicit that the positive arm is not the exit code:

  * P-2: for every guarded process, every repository origin's `checkout_root` equals
    `MNV_CODE_ROOT`, every `sha256` matches that path's entry in the A-2(f) source manifest, and
    `checked > 0`.
  * P-3: `repo_origin_count == 0` is a REPORTABLE STATE, never a pass. An entrypoint may be empty
    only if it is DECLARED empty in the pins, with a disclosure sentence; an undeclared empty set
    is a failure, because "no repository import occurred" and "the inventory did not run" are the
    two states the whole mechanism exists to separate.
  * P-4: per entrypoint, the sorted set of repository-origin module names is pinned as an IDENTITY,
    NOT A FLOOR -- the discipline `test_oi136_failopen_inventory_ratchet.py` already applies to the
    fail-open set, and for the stated reason: a floor catches collapse but permits erosion. A run
    whose set differs IN EITHER DIRECTION aborts and is reported.

THE PINS ARE MEASURED, NOT AUTHORED. `--write-pins` records what a clean run actually resolved;
there is no hand-maintained expected list anywhere, because a list written from reading the source
would agree with the source by construction and disagree with the interpreter silently.

WHAT IT CANNOT SEE, inherited from the inventory and restated so it is not rediscovered: namespace
packages (`spec.origin` is None and the guard returns before `checkout_root_of`), modules already
in `sys.modules` before `install()`, anything in a further subprocess that is not itself wrapped,
and the `.sh` route entirely.

EXIT CODES
    0 -- every inventory read, every P-2/P-3/P-4 assertion held
    2 -- COULD NOT LOOK (no inventories, unreadable pins, malformed record)
    3 -- MEASURED VIOLATION
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

OK_EXIT = 0
CANNOT_CHECK_EXIT = 2
VIOLATION_EXIT = 3

SCHEMA = "mnv_import_set_pins/1"
INVENTORY_SCHEMA = "mnv_guard_inventory/1"


def load_inventories(inv_dir: str) -> list[dict]:
    """Every JSON object on every line of every *.jsonl under `inv_dir`, recursively.

    A MALFORMED LINE RAISES rather than being skipped. Skipping is how an inventory that failed
    half-way through becomes indistinguishable from one that had nothing to say.
    """
    recs = []
    paths = sorted(glob.glob(os.path.join(inv_dir, "**", "*.jsonl"), recursive=True))
    for p in paths:
        with open(p, encoding="utf-8") as fh:
            for n, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                except ValueError as err:
                    raise ValueError(f"{p}:{n} is not JSON: {err}") from err
                if rec.get("schema") != INVENTORY_SCHEMA:
                    raise ValueError(f"{p}:{n} is not a {INVENTORY_SCHEMA} record")
                rec["_inventory_file"] = p
                recs.append(rec)
    return recs


def entrypoint_key(rec: dict) -> str:
    """The entrypoint an inventory belongs to, as a path RELATIVE TO ITS OWN EXPECT-ROOT.

    Relative, so pins survive a code root that moves between runs -- which it does by design, since
    `MNV_CODE_ROOT` is constituted fresh at a named sha. A basename would collide across
    directories; an absolute path would make every pin single-use.
    """
    script, root = rec.get("script"), rec.get("expect_root")
    if not script:
        return "<no-script>"
    if root and os.path.abspath(script).startswith(os.path.abspath(root) + os.sep):
        return os.path.relpath(os.path.abspath(script), os.path.abspath(root))
    return os.path.abspath(script)


def import_set(rec: dict) -> list[str]:
    return sorted({o["fullname"] for o in rec.get("repo_origins", [])})


def check(recs, pins, manifest=None, require_empty_allow=()):
    """Returns (violations, observed_sets). Every check runs; none short-circuits, because the
    first failure is rarely the only one and a reviewer needs the whole list."""
    v = []
    observed: dict[str, set] = {}
    man_files = (manifest or {}).get("files", {})

    for rec in recs:
        key = entrypoint_key(rec)
        where = f"{rec.get('_inventory_file')} (pid {rec.get('pid')}) {key}"
        observed.setdefault(key, set()).update(import_set(rec))

        # ---- P-2 -------------------------------------------------------------------------
        if rec.get("allow"):
            v.append(f"{where}: --allow was used and names {rec['allow']}; forbidden on a "
                     f"production arm, for every leg")
        expect = rec.get("expect_root")
        for o in rec.get("repo_origins", []):
            if o.get("checkout_root") != expect:
                v.append(f"{where}: {o['fullname']} resolved under {o.get('checkout_root')}, "
                         f"not the expected {expect} ({o.get('origin')})")
            if man_files:
                rel = None
                if expect and str(o.get("origin", "")).startswith(os.path.abspath(expect) + os.sep):
                    rel = os.path.relpath(o["origin"], os.path.abspath(expect))
                if rel is None or rel not in man_files:
                    v.append(f"{where}: {o['fullname']} origin {o.get('origin')} is not in the "
                             f"A-2(f) source manifest at all")
                elif man_files[rel] != o.get("sha256"):
                    v.append(f"{where}: {o['fullname']} sha256 {o.get('sha256')} != manifest "
                             f"{man_files[rel]} for {rel}")
        sr = rec.get("script_checkout_root")
        if sr != expect:
            v.append(f"{where}: the SCRIPT resolves under {sr}, not {expect}")
        # A REFUSAL SITTING IN A PRODUCTION INVENTORY SET IS A VIOLATION, not a curiosity. The
        # verdict is checked as well as the outcome because the two are written by different lines
        # and disagreed once already: a B-4 refusal recorded itself as an empty GREEN run until
        # 2026-08-22, found by running the real N-1 arm.
        if str(rec.get("outcome", "")).startswith(("refused", "cannot-check")) \
                or str(rec.get("verdict", "")).startswith(("REFUSED", "COULD NOT LOOK")):
            v.append(f"{where}: this record is a REFUSAL or a CANNOT-LOOK "
                     f"(outcome={rec.get('outcome')!r}, verdict={str(rec.get('verdict'))[:60]!r}). "
                     f"A production inventory set contains only runs that happened.")
        if not rec.get("guard_installed"):
            v.append(f"{where}: no guard was installed, so this record measures nothing")
        if rec.get("checked", 0) <= 0:
            v.append(f"{where}: checked == {rec.get('checked')}; the guard resolved no absolute "
                     f"origin at all, so its silence is not evidence")

        # ---- P-3 -------------------------------------------------------------------------
        if "repo_origin_count" not in rec or "repo_origin_inventory_is_empty" not in rec:
            v.append(f"{where}: the emptiness flags are ABSENT. An absent key cannot distinguish "
                     f"'no repository import occurred' from 'the inventory did not run'.")
        elif rec["repo_origin_count"] == 0 and key not in require_empty_allow:
            v.append(f"{where}: repo_origin_count == 0 and {key} is not a DECLARED empty "
                     f"entrypoint. A zero is a reportable state, never a pass; declare it in the "
                     f"pins with its disclosure or find out why nothing resolved.")

    # ---- P-4: identity in BOTH directions ----------------------------------------------
    pinned = pins.get("entrypoints", {})
    for key, got in sorted(observed.items()):
        if key not in pinned:
            v.append(f"{key}: no pinned import set. A new entrypoint on the path is a change that "
                     f"has to be looked at, not absorbed.")
            continue
        want = set(pinned[key].get("modules", []))
        if got != want:
            v.append(f"{key}: import set MOVED. missing={sorted(want - got)} "
                     f"unexpected={sorted(got - want)}. Identity, not a floor: a set that shrank "
                     f"is as much a finding as one that grew.")
    for key in sorted(set(pinned) - set(observed)):
        v.append(f"{key}: pinned but NO inventory was produced for it. A missing inventory is a "
                 f"failure, not a gap.")
    return v, observed


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="mnv_import_set_ratchet.py",
                                 description=__doc__.splitlines()[0])
    ap.add_argument("--inventory-dir", required=True)
    ap.add_argument("--pins", required=True)
    ap.add_argument("--source-manifest", help="A-2(f) record; enables the sha256 half of P-2")
    ap.add_argument("--write-pins", action="store_true",
                    help="record what THIS run resolved as the pin set (measured, not authored)")
    ap.add_argument("--declare-empty", action="append", default=[],
                    help="an entrypoint whose repository-origin set is legitimately EMPTY, "
                         "relative to the code root. Requires --empty-disclosure.")
    ap.add_argument("--empty-disclosure", default="",
                    help="the P-3 sentence recorded beside a declared-empty entrypoint")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)

    if not os.path.isdir(a.inventory_dir):
        print(f"[p4] COULD NOT LOOK: no inventory directory {a.inventory_dir}", file=sys.stderr)
        return CANNOT_CHECK_EXIT
    try:
        recs = load_inventories(a.inventory_dir)
    except (OSError, ValueError) as err:
        print(f"[p4] COULD NOT LOOK: {err}", file=sys.stderr)
        return CANNOT_CHECK_EXIT
    if not recs:
        print(f"[p4] COULD NOT LOOK: zero inventory records under {a.inventory_dir}. A run that "
              f"emitted no record establishes nothing; this is never a clean result.",
              file=sys.stderr)
        return CANNOT_CHECK_EXIT

    manifest = None
    if a.source_manifest:
        try:
            with open(a.source_manifest, encoding="utf-8") as fh:
                manifest = json.load(fh)
        except (OSError, ValueError) as err:
            print(f"[p4] COULD NOT LOOK: cannot read {a.source_manifest}: {err}", file=sys.stderr)
            return CANNOT_CHECK_EXIT

    if a.write_pins:
        if a.declare_empty and not a.empty_disclosure:
            print("[p4] COULD NOT LOOK: --declare-empty without --empty-disclosure. A declared "
                  "empty set without its disclosure sentence is the silent zero this forbids.",
                  file=sys.stderr)
            return CANNOT_CHECK_EXIT
        _, observed = check(recs, {"entrypoints": {}}, manifest, tuple(a.declare_empty))
        pins = {"schema": SCHEMA, "entrypoints": {}}
        for key, mods in sorted(observed.items()):
            entry = {"modules": sorted(mods)}
            if key in a.declare_empty:
                entry["declared_empty"] = True
                entry["disclosure"] = a.empty_disclosure
            pins["entrypoints"][key] = entry
        os.makedirs(os.path.dirname(os.path.abspath(a.pins)) or ".", exist_ok=True)
        with open(a.pins, "w", encoding="utf-8") as fh:
            json.dump(pins, fh, indent=2, sort_keys=True)
        print(f"[p4] wrote {len(pins['entrypoints'])} pinned import set(s) to {a.pins} "
              f"from {len(recs)} inventory record(s)")
        for key, e in sorted(pins["entrypoints"].items()):
            print(f"[p4]   {key}: {len(e['modules'])} module(s) {e['modules']}"
                  + ("  [DECLARED EMPTY]" if e.get("declared_empty") else ""))
        return OK_EXIT

    try:
        with open(a.pins, encoding="utf-8") as fh:
            pins = json.load(fh)
    except (OSError, ValueError) as err:
        print(f"[p4] COULD NOT LOOK: cannot read pins {a.pins}: {err}", file=sys.stderr)
        return CANNOT_CHECK_EXIT
    if pins.get("schema") != SCHEMA:
        print(f"[p4] COULD NOT LOOK: {a.pins} is not a {SCHEMA} record", file=sys.stderr)
        return CANNOT_CHECK_EXIT

    declared_empty = tuple(k for k, e in pins.get("entrypoints", {}).items()
                           if e.get("declared_empty"))
    violations, observed = check(recs, pins, manifest, declared_empty)

    print(f"[p4] {len(recs)} inventory record(s) over {len(observed)} entrypoint(s); "
          f"source manifest {'IN USE' if manifest else 'NOT SUPPLIED (sha256 half of P-2 is OFF)'}")
    for key in sorted(observed):
        e = pins.get("entrypoints", {}).get(key, {})
        tag = "  [DECLARED EMPTY: " + e.get("disclosure", "") + "]" if e.get("declared_empty") else ""
        print(f"[p4]   {key}: {len(observed[key])} repository origin(s){tag}")
    if violations:
        print(f"\n[p4] {len(violations)} VIOLATION(S):", file=sys.stderr)
        for x in violations:
            print(f"[p4]   {x}", file=sys.stderr)
        return VIOLATION_EXIT
    print("[p4] P-2, P-3 and P-4 HOLD for every inventory record read.")
    return OK_EXIT


if __name__ == "__main__":
    sys.exit(main())
