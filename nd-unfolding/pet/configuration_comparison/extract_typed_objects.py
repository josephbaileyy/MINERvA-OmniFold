"""Pilot extraction of the R4 branches from the MasterAnaDev tuples.

This is the step that was wrongly reported as blocked. The tuples are at
`/pscratch/sd/j/josephrb/minerva/minerva_large_files/`, they carry all 21
typed-object branches and all 14 global source branches, and they carry the
identity branches the join needs.

**What this pilot answers, before anyone spends 11 TB of reads:**

* do the enumerated branches read, at their declared multiplicities;
* what the typed-object multiplicity distribution IS, which is what decides
  whether Gregor's 33-token cap binds and how often -- a number the comparison
  has so far only assumed;
* whether the event identity needed for the join is present and well-formed on
  both the MC and data sides.

It deliberately reads a BOUNDED number of entries. A pilot that reads everything
is not a pilot, and the multiplicity distribution converges long before 54 M
events.

NOT CITABLE FOR any performance claim, and it writes no training input. It
measures what an extraction would find.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from r4_manifest import (GLOBAL_SOURCE_BRANCHES, MUON_COUNT_SOURCE_BRANCHES,
                         TYPED_OBJECT_BRANCHES)

# The token vocabulary his arm builds from: blobs, prongs and the two gammas.
# `prong_part_*` and `MasterAnaDev_Blob*` are vectors per event; the gammas are
# at most one each.
MULTIPLICITY_BRANCHES = {
    "blobs": "MasterAnaDev_BlobTotalE",
    "prongs": "prong_part_E",
}
IDENTITY_BRANCHES = ("ev_run", "ev_subrun", "ev_gate")
MC_IDENTITY_BRANCHES = ("mc_run", "mc_subrun", "mc_nthEvtInFile")


def pilot(path: Path, entries: int, cap: int) -> dict[str, Any]:
    import ROOT

    ROOT.gROOT.SetBatch(True)
    handle = ROOT.TFile.Open(str(path))
    if not handle or handle.IsZombie():
        raise SystemExit(f"[extract] cannot open {path}")
    tree = handle.Get("MasterAnaDev")
    if not tree:
        raise SystemExit(f"[extract] no MasterAnaDev tree in {path}")

    available = {b.GetName() for b in tree.GetListOfBranches()}
    wanted = (tuple(TYPED_OBJECT_BRANCHES) + tuple(GLOBAL_SOURCE_BRANCHES)
              + tuple(MUON_COUNT_SOURCE_BRANCHES) + IDENTITY_BRANCHES
              + MC_IDENTITY_BRANCHES)
    present = {name: name in available for name in wanted}
    missing = sorted(n for n, ok in present.items() if not ok)

    total = tree.GetEntries()
    scanned = min(entries, total)
    counts = {label: [] for label in MULTIPLICITY_BRANCHES}
    identity_ok = 0
    for index in range(scanned):
        tree.GetEntry(index)
        for label, branch in MULTIPLICITY_BRANCHES.items():
            if present.get(branch):
                try:
                    counts[label].append(len(getattr(tree, branch)))
                except TypeError:
                    counts[label].append(1)
        if all(present.get(b) for b in IDENTITY_BRANCHES):
            if int(getattr(tree, "ev_run")) > 0:
                identity_ok += 1

    def summarize(values: list[int]) -> dict[str, Any]:
        if not values:
            return {"n": 0}
        ordered = sorted(values)
        n = len(ordered)
        return {
            "n": n,
            "mean": sum(ordered) / n,
            "median": ordered[n // 2],
            "p90": ordered[int(0.90 * (n - 1))],
            "p99": ordered[int(0.99 * (n - 1))],
            "max": ordered[-1],
            "zero_fraction": sum(1 for v in ordered if v == 0) / n,
        }

    blobs = counts.get("blobs", [])
    prongs = counts.get("prongs", [])
    combined = [b + p for b, p in zip(blobs, prongs)] if blobs and prongs else []
    over_cap = (sum(1 for v in combined if v > cap) / len(combined)
                if combined else None)

    return {
        "file": str(path),
        "tree_entries": int(total),
        "entries_scanned": int(scanned),
        "branches_requested": len(wanted),
        "branches_present": sum(present.values()),
        "branches_missing": missing,
        "identity_branches_present": {b: present.get(b) for b in
                                      IDENTITY_BRANCHES + MC_IDENTITY_BRANCHES},
        "rows_with_positive_ev_run": identity_ok,
        "multiplicity": {label: summarize(values) for label, values in counts.items()},
        "combined_blob_plus_prong": summarize(combined),
        "cap": cap,
        "fraction_over_cap": over_cap,
        "cap_reading": (
            f"fraction of scanned events whose blob+prong count exceeds {cap}. "
            "This is what decides whether his 33-token cap binds, and it has "
            "been assumed rather than measured until now"),
        "scope": ("BOUNDED pilot over one file. It measures what an extraction "
                  "would find; it writes no training input and makes no "
                  "performance claim"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tuple", type=Path, required=True)
    parser.add_argument("--entries", type=int, default=20000)
    parser.add_argument("--cap", type=int, default=33)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = pilot(args.tuple, args.entries, args.cap)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"branches present {report['branches_present']}/{report['branches_requested']}"
          f"  missing {report['branches_missing']}")
    for label, stats in report["multiplicity"].items():
        if stats.get("n"):
            print(f"  {label}: mean {stats['mean']:.2f} median {stats['median']} "
                  f"p99 {stats['p99']} max {stats['max']} "
                  f"zero {stats['zero_fraction']:.1%}")
    combined = report["combined_blob_plus_prong"]
    if combined.get("n"):
        print(f"  blob+prong: mean {combined['mean']:.2f} p99 {combined['p99']} "
              f"max {combined['max']}")
    if report["fraction_over_cap"] is not None:
        print(f"  over cap {report['cap']}: {report['fraction_over_cap']:.3%}")


if __name__ == "__main__":
    main()
