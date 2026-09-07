#!/usr/bin/env python3
"""Guard firing census -- WHICH protection has actually refused, and how often.

WHY THIS EXISTS. `mnv_guarded_run.py` declares eight `LAUNCH_REASON_*` values and three refusal
sites, and `test_mnv_guarded_run.py` proves every one of them is reachable. REACHABLE IS NOT
EXERCISED. A refusal reason that has never fired against real work is a branch whose cost is paid on
every run and whose value has never once been observed, and until this file nothing could tell the
two apart. The guard already writes `refusal_site` and `launch_refusal.reason` into every inventory
it emits; the only existing reader, `mnv_import_set_ratchet.py`, treats ANY refusal as a violation to
report rather than as a sample in a distribution. The records were therefore sufficient and unread.

A ZERO IS NOT SELF-EXPLANATORY. This is the discipline `mnv_guarded_run.py` already applies to
`checked` via CHECKED_MEASURED/CHECKED_NOT_MEASURED, restated here because it is the whole reason
this file REFUSES rather than prints when its population is empty. Two completely different states
produce a zero count for a reason:

  * inventories were read, and the reason did not appear in them  -> a MEASURED zero
  * no inventory was read at all                                  -> NOT MEASURED

A census that printed "0 firings" for both would report a guard as unexercised when in fact nobody
looked, which is the precise failure this repository has hit before with monitors whose transport
had died. `--inventory-dir` pointed at an empty or wrong directory is the expected way to reach it.

THE DECLARED SET IS IMPORTED, NEVER RETYPED. Reasons and sites come from `mnv_guarded_run` itself.
A reason added there shows up here as never-fired on the next run, instead of silently falling
outside the census; a hand-copied list would agree with itself and disagree with the guard.

WHAT THIS DOES NOT DO. It does not judge. A never-fired reason is not thereby dead: the kernel-floor
and preexec reasons exist for launch shapes that are rare by construction, and a guard nothing has
violated yet is not a guard that is not working. The census reports a distribution and names its own
population; the judgement is a human one and belongs in a record, not in this file.
"""
import argparse
import collections
import json
import math
import os
import pathlib
import sys

#: The guard is the authority on what refusals exist. Imported by path rather than assumed to be on
#: `sys.path`, because an earlier import owning `sys.path[0]` is how a stale checkout gets read as
#: current: this resolves the sibling next to THIS file and nothing else.
_HERE = pathlib.Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import mnv_guarded_run as mgr  # noqa: E402

#: Duplicated from `write_inventory`'s record, which spells it as a literal and exports no constant.
#: `test_mnv_guard_firing_census.py` asserts this string against a record produced by RUNNING the
#: guard, so the duplication is checked rather than trusted.
SCHEMA = "mnv_guard_inventory/1"

CENSUS_BLIND_EXIT = 2
SCHEMA_DRIFT_EXIT = 3


def assert_schema_still_matches_the_guard() -> "str | None":
    """Fail LOUDLY if the guard no longer writes the schema this census pins.

    WHY THIS IS NOT PARANOIA. `SCHEMA` is retyped here because `write_inventory` spells it as a bare
    literal and exports no constant to import. If the guard bumps it, every real record becomes
    `foreign_schema`, the record count falls to zero, and the census reports BLIND -- which reads as
    "nobody looked" when the truth is "the reader is stale". A silent BLIND is strictly worse than a
    loud stop, because BLIND is a state this tool is designed to report calmly.

    THE RIGHT FIX IS UPSTREAM and is not ours to make: a one-line `INVENTORY_SCHEMA` constant in
    `mnv_guarded_run.py` would turn this back into the import-over-retype discipline used for the
    reason constants. That file is a shared protected tool -- proposing a change to it is in scope,
    editing it is not -- so this tripwire stands in until its owner lands the constant.

    Returns None when the guard's source still contains the literal, else a message saying so.
    """
    src = getattr(mgr, "__file__", None)
    if not src or not os.path.isfile(src):
        return f"cannot read the guard's source to check the schema pin (mgr.__file__={src!r})"
    if SCHEMA not in pathlib.Path(src).read_text(encoding="utf-8", errors="replace"):
        return (f"{src} no longer contains the literal {SCHEMA!r} that this census pins. Every "
                f"record would be counted as foreign and the census would report BLIND. Re-read "
                f"write_inventory's record and update SCHEMA, or import a constant if one now "
                f"exists.")
    return None


def declared_reasons() -> "dict[str, str]":
    """Every `LAUNCH_REASON_*` the guard defines, as {constant name: recorded value}."""
    return {n: getattr(mgr, n) for n in dir(mgr) if n.startswith("LAUNCH_REASON_")}


def declared_sites() -> "dict[str, str]":
    """Every refusal SITE the guard defines. `SITE_NONE` is excluded: it is the absence of one."""
    return {n: getattr(mgr, n) for n in dir(mgr)
            if n.startswith("SITE_") and getattr(mgr, n) is not None}


def inventory_files(paths, directories) -> "list[pathlib.Path]":
    """The population, named explicitly so a report can state what it read.

    Directories are walked for `*.jsonl` because that is what `write_inventory` appends to. A
    directory that contains none contributes nothing and is NOT an error here -- it becomes the
    blind state in `main`, which is reported rather than defaulted away.
    """
    found = [pathlib.Path(p) for p in paths]
    for d in directories:
        for root, _dirs, names in os.walk(d):
            found.extend(pathlib.Path(root) / n for n in sorted(names) if n.endswith(".jsonl"))
    return found


class Census:
    """Counts over a set of inventory records, plus the provenance of the counting itself."""

    def __init__(self):
        self.files_read = []
        self.records = 0
        self.malformed = 0            #: lines that are not JSON. Counted, never skipped silently.
        self.foreign_schema = collections.Counter()
        self.outcomes = collections.Counter()
        self.sites = collections.Counter()
        self.reasons = collections.Counter()

    @property
    def refusals(self) -> int:
        return sum(self.sites.values())

    @property
    def is_blind(self) -> bool:
        """No record was read. Every zero below is NOT MEASURED rather than measured."""
        return self.records == 0

    def add_file(self, path: pathlib.Path) -> None:
        self.files_read.append(str(path))
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    #: A truncated final line is the normal way this happens -- the guard appends,
                    #: and a killed process can leave half a line. It is reported, not dropped,
                    #: because a silently-skipped record is a firing this census did not see.
                    self.malformed += 1
                    continue
                schema = rec.get("schema")
                if schema != SCHEMA:
                    self.foreign_schema[schema] += 1
                    continue
                self.add_record(rec)

    def add_record(self, rec: dict) -> None:
        self.records += 1
        self.outcomes[rec.get("outcome")] += 1
        site = rec.get("refusal_site")
        if site is not None:
            self.sites[site] += 1
        refusal = rec.get("launch_refusal") or {}
        reason = refusal.get("reason")
        if reason is not None:
            self.reasons[reason] += 1

    def never_fired_reasons(self) -> "list[str]":
        return sorted(v for v in declared_reasons().values() if v not in self.reasons)

    def never_fired_sites(self) -> "list[str]":
        return sorted(v for v in declared_sites().values() if v not in self.sites)

    def undeclared_reasons(self) -> "list[str]":
        """Reasons in the records that the CURRENT guard does not declare.

        Non-empty means the records predate a rename, or were written by a different guard. Either
        way the distribution below mixes two populations and the reader has to be told.
        """
        known = set(declared_reasons().values())
        return sorted(r for r in self.reasons if r not in known)


def entropy_bits(counts) -> float:
    """Shannon entropy of a firing distribution, in bits. Empty and single-valued both give 0.0."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return -sum((c / total) * math.log2(c / total) for c in counts.values() if c)


def effective_count(counts) -> float:
    """2**H -- the number of reasons that fire often enough to matter, as a continuous count."""
    return 2 ** entropy_bits(counts) if sum(counts.values()) else 0.0


def report(c: Census) -> str:
    reasons_declared = declared_reasons()
    lines = []
    lines.append("GUARD FIRING CENSUS")
    lines.append(f"  files read        : {len(c.files_read)}")
    lines.append(f"  records           : {c.records}")
    lines.append(f"  malformed lines   : {c.malformed}")
    if c.foreign_schema:
        for schema, n in sorted(c.foreign_schema.items(), key=lambda kv: -kv[1]):
            lines.append(f"  NOT COUNTED       : {n} record(s) of schema {schema!r}")
    lines.append(f"  refusals          : {c.refusals}")
    lines.append("")
    lines.append(f"  reasons declared by the guard : {len(reasons_declared)}")
    lines.append(f"  reasons ever observed         : {len(c.reasons)}")
    h = entropy_bits(c.reasons)
    lines.append(f"  firing entropy H              : {h:.2f} bits "
                 f"(max {math.log2(len(reasons_declared)):.2f} over the declared set)")
    lines.append(f"  effective reasons 2**H        : {effective_count(c.reasons):.1f}")
    lines.append("")
    if c.sites:
        lines.append("  by refusal site:")
        for site, n in c.sites.most_common():
            lines.append(f"    {n:8d}  {site}")
    if c.reasons:
        lines.append("  by launch reason:")
        for reason, n in c.reasons.most_common():
            lines.append(f"    {n:8d}  {reason}")
    never_r, never_s = c.never_fired_reasons(), c.never_fired_sites()
    lines.append("")
    lines.append(f"  NEVER FIRED in this population -- {len(never_r)} reason(s), "
                 f"{len(never_s)} site(s):")
    for v in never_s:
        lines.append(f"    site   {v}")
    for v in never_r:
        lines.append(f"    reason {v}")
    undeclared = c.undeclared_reasons()
    if undeclared:
        lines.append("")
        lines.append("  OBSERVED BUT NOT DECLARED by the current guard -- these records were "
                     "written by a different version, and the distribution above mixes "
                     "populations:")
        for v in undeclared:
            lines.append(f"    {v}")
    lines.append("")
    lines.append("  POPULATION -- every count above is scoped to these files and to no other run:")
    for p in c.files_read:
        lines.append(f"    {p}")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Census of which mnv_guarded_run protections have actually refused.")
    ap.add_argument("--inventory", action="append", default=[],
                    help="an inventory JSONL written by mnv_guarded_run --inventory; repeatable")
    ap.add_argument("--inventory-dir", action="append", default=[],
                    help="a directory walked recursively for *.jsonl; repeatable")
    ap.add_argument("--json", action="store_true", help="emit the census as JSON")
    args = ap.parse_args(argv)

    drift = assert_schema_still_matches_the_guard()
    if drift is not None:
        #: Reported BEFORE anything is read, so the operator never sees a BLIND that was really a
        #: stale pin. This exit is distinct from CENSUS_BLIND_EXIT for exactly that reason.
        print("GUARD FIRING CENSUS -- SCHEMA DRIFT, REFUSING TO COUNT.", file=sys.stderr)
        print(f"  {drift}", file=sys.stderr)
        return SCHEMA_DRIFT_EXIT

    files = inventory_files(args.inventory, args.inventory_dir)
    c = Census()
    missing = []
    for p in files:
        if not p.is_file():
            missing.append(str(p))
            continue
        c.add_file(p)

    if c.is_blind:
        #: THE WHOLE POINT OF THIS BRANCH. Printing a table of zeros here would say "no guard has
        #: ever fired", which is a claim about the guard; the true claim is about this invocation.
        print("GUARD FIRING CENSUS -- BLIND, NOT MEASURED.", file=sys.stderr)
        print(f"  {len(files)} file(s) named, {len(missing)} missing, "
              f"{c.malformed} malformed line(s), 0 records of schema {SCHEMA!r}.", file=sys.stderr)
        for m in missing:
            print(f"  missing: {m}", file=sys.stderr)
        print("  No distribution is reported. A zero count here would be indistinguishable from "
              "a guard that has never fired, and those are different facts.", file=sys.stderr)
        return CENSUS_BLIND_EXIT

    if args.json:
        print(json.dumps({
            "files_read": c.files_read, "records": c.records, "malformed": c.malformed,
            "foreign_schema": {str(k): v for k, v in c.foreign_schema.items()},
            "refusals": c.refusals,
            "outcomes": dict(c.outcomes), "sites": dict(c.sites), "reasons": dict(c.reasons),
            "entropy_bits": entropy_bits(c.reasons),
            "effective_reasons": effective_count(c.reasons),
            "never_fired_reasons": c.never_fired_reasons(),
            "never_fired_sites": c.never_fired_sites(),
            "undeclared_reasons": c.undeclared_reasons(),
        }, indent=2))
    else:
        print(report(c))
    if missing:
        for m in missing:
            print(f"  NAMED BUT ABSENT: {m}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
