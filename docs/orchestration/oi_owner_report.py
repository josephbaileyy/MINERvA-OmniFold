#!/usr/bin/env python3
"""Report which `docs/OPEN_ITEMS.md` rows can actually be routed from their own row.

WHY (BEN-395). The table's third column is named `lane/owner`, and **65 of 93 rows fill it with an
AREA** ("PET diagnostics", "storage", "repo infrastructure") rather than a lane or a person. A
populated cell in a column named `lane/owner` reads as ownership, so an unowned row is
indistinguishable from an owned one without reading the whole row — and the row is the thing a lane
is dispatched from. `OI-58` sat ambient for a session on exactly that.

The vocabulary for all three states already exists in the table and is used inconsistently:
  * a lane or person       — `C (PET)`, `lane D`, `Joseph`, `peer session B`
  * explicitly unowned     — `OI-130`: "analysis-note evidence / unowned"
  * subject vs filer split — `OI-124`: "lane D (subject — probe owner); verdict-repair lane (filing)"

NOT A HOOK CHECK, and it must not become one until the backlog is dispositioned: it fails on 65
pre-existing rows, so a committer editing an unrelated row could not make it pass. That violates the
dispatcher's admitting rule at `.githooks/pre-commit:11` — *a check belongs here iff a committer who
did nothing wrong can always make it pass* (lane D, `OI-64`). This is a report, run on demand.

Usage: python3 docs/orchestration/oi_owner_report.py [--list-area-only]
Exit 0 always — it reports, it does not gate.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROW = re.compile(r"^\| (OI-\d+) \|([^|]*)\|([^|]*)\|")
# A cell routes the row iff it names a lane, a person, or is explicitly marked unowned.
OWNER = re.compile(
    r"(?i)(lane [A-E]\b|session [A-E]\b|agent[- ][A-E]\b|\b[A-E] \(PET\)|Joseph|mediator"
    r"|peer session|verdict-repair lane|standard-P4 lane|propagation)"
)
EXPLICIT_NONE = re.compile(r"(?i)\bunowned\b")
CLOSED = re.compile(r"(?i)closed|no action")


def classify(cell: str) -> str:
    if EXPLICIT_NONE.search(cell):
        return "explicitly-unowned"
    if OWNER.search(cell):
        return "routable"
    if CLOSED.search(cell):
        return "closed"
    return "area-only"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Report routability of OPEN_ITEMS rows (BEN-395).")
    ap.add_argument("--list-area-only", action="store_true", help="print every unroutable row id")
    ap.add_argument("--path", type=Path, default=Path("docs/OPEN_ITEMS.md"))
    args = ap.parse_args(argv)

    if not args.path.exists():
        print(f"[oi-owner] {args.path} not found — run from the repo root", file=sys.stderr)
        return 0

    buckets: dict[str, list[str]] = {}
    for line in args.path.read_text(errors="replace").splitlines():
        m = ROW.match(line)
        if not m:
            continue
        oid, _state, cell = m.group(1), m.group(2), m.group(3)
        buckets.setdefault(classify(cell), []).append(oid)

    total = sum(len(v) for v in buckets.values())
    print(f"[oi-owner] {total} rows in {args.path}")
    for kind in ("routable", "explicitly-unowned", "closed", "area-only"):
        ids = buckets.get(kind, [])
        note = "  <-- cannot be routed from the row" if kind == "area-only" else ""
        print(f"[oi-owner]   {kind:20} {len(ids):3}{note}")
    if args.list_area_only:
        for oid in buckets.get("area-only", []):
            print(f"[oi-owner]   AREA-ONLY {oid}")
    print("[oi-owner] REPORT ONLY — never a gate; see the module docstring for why.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
