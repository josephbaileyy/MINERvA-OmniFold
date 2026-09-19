"""Slim the MasterAnaDev tuples to the R4 manifest, at C++ speed.

The pilot read 20,000 entries with a PyROOT loop in 39 s. At that rate the full
inventory is about 29 hours PER FILE SET, which is not an extraction, it is a
reason to give up. `RDataFrame::Snapshot` does the same work in compiled code
with implicit multithreading and writes only the requested branches, so the read
is columnar: 46 branches of 4,102.

What this produces is a SLIM ROOT per input file -- the same rows, the same
order, fewer columns. It applies no selection and computes nothing. Selection,
the identity join and his token construction all happen downstream, against the
inventory, so that this step cannot silently change which events exist.

NOT CITABLE FOR any performance claim.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time
from typing import Any

from r4_manifest import (GLOBAL_SOURCE_BRANCHES, MUON_COUNT_SOURCE_BRANCHES,
                         TYPED_OBJECT_BRANCHES)

IDENTITY = ("ev_run", "ev_subrun", "ev_gate")
MC_IDENTITY = ("mc_run", "mc_subrun", "mc_nthEvtInFile")
# DELIBERATELY EMPTY. The first version listed six selection-context branches I
# had guessed the names of rather than read -- `mc_current`, `mc_intType` and so
# on. Some of them exist in the branch list but carry no readable address, and
# `Snapshot` failed with "Trying to insert a null branch address", which is the
# kindest possible outcome: it refused rather than writing a column of garbage.
#
# Nothing goes in this tuple that has not been read out of the file first. The
# downstream join reproduces the inventory's selection from the INVENTORY, which
# is where the selection actually lives.
SELECTION_CONTEXT: tuple[str, ...] = ()


def wanted_branches(available: set[str]) -> tuple[list[str], list[str]]:
    requested = (tuple(TYPED_OBJECT_BRANCHES) + tuple(GLOBAL_SOURCE_BRANCHES)
                 + tuple(MUON_COUNT_SOURCE_BRANCHES) + IDENTITY + MC_IDENTITY
                 + SELECTION_CONTEXT)
    seen: list[str] = []
    for name in requested:
        if name in available and name not in seen:
            seen.append(name)
    missing = [n for n in requested if n not in available]
    return seen, missing


# Two of the 21 typed branches are `vector<vector<double>>`: `prong_part_E` and
# `prong_part_pos`. `Snapshot` refuses them -- "does not have a compiled
# CollectionProxy ... to avoid to write corrupted data" -- which is the right
# refusal, and it named the branches rather than writing garbage.
#
# Measured, not assumed: the outer dimension is the prong count and the inner is
# CONSTANT 4 for both. So they flatten losslessly to a flat vector plus the prong
# count, and the extractor ASSERTS the inner width rather than trusting it, because
# a single event with a different width would silently misalign every prong after
# it.
NESTED_BRANCHES = {"prong_part_E": 4, "prong_part_pos": 4}


def _flatten_definitions() -> dict[str, str]:
    definitions: dict[str, str] = {}
    for name, width in NESTED_BRANCHES.items():
        definitions[f"{name}_flat"] = (
            f"ROOT::RVec<double> out;"
            f" for (const auto &v : {name}) {{"
            f"   if ((int)v.size() != {width}) return ROOT::RVec<double>{{-1}};"
            f"   for (auto x : v) out.push_back(x);"
            f" }} return out;"
        )
        definitions[f"{name}_n"] = f"(int){name}.size()"
        definitions[f"{name}_inner_ok"] = (
            f"bool ok = true;"
            f" for (const auto &v : {name}) if ((int)v.size() != {width}) ok = false;"
            f" return ok;"
        )
    return definitions


def slim(source: Path, destination: Path, threads: int) -> dict[str, Any]:
    import ROOT

    ROOT.gROOT.SetBatch(True)
    if threads > 1:
        ROOT.EnableImplicitMT(threads)

    handle = ROOT.TFile.Open(str(source))
    if not handle or handle.IsZombie():
        raise SystemExit(f"[slim] cannot open {source}")
    tree = handle.Get("MasterAnaDev")
    if not tree:
        raise SystemExit(f"[slim] no MasterAnaDev tree in {source}")
    available = {b.GetName() for b in tree.GetListOfBranches()}
    entries = int(tree.GetEntries())
    keep, missing = wanted_branches(available)
    # A branch can be listed and still have no readable address. Ask for each one
    # individually and drop the ones that cannot be read, recording which --
    # silently keeping them makes Snapshot fail for the whole file.
    unreadable = []
    readable = []
    for name in keep:
        branch = tree.GetBranch(name)
        if branch is None or branch.GetNleaves() == 0:
            unreadable.append(name)
        else:
            readable.append(name)
    keep = readable
    handle.Close()

    started = time.perf_counter()
    frame = ROOT.RDataFrame("MasterAnaDev", str(source))
    written = [n for n in keep if n not in NESTED_BRANCHES]
    for column, expression in _flatten_definitions().items():
        if column.rsplit("_", 1)[0].rsplit("_", 1)[0] in NESTED_BRANCHES or \
                any(column.startswith(b) for b in NESTED_BRANCHES):
            frame = frame.Define(column, expression)
            written.append(column)
    inner_ok = {name: frame.Filter(f"!{name}_inner_ok").Count()
                for name in NESTED_BRANCHES}
    destination.parent.mkdir(parents=True, exist_ok=True)
    frame.Snapshot("MasterAnaDev", str(destination), written)
    violations = {name: int(count.GetValue()) for name, count in inner_ok.items()}
    elapsed = time.perf_counter() - started
    if any(violations.values()):
        raise SystemExit(
            f"[slim] nested inner width is not constant: {violations}. "
            "Flattening would misalign every prong after the offending event."
        )

    check = ROOT.TFile.Open(str(destination))
    out_tree = check.Get("MasterAnaDev")
    out_entries = int(out_tree.GetEntries())
    out_branches = sorted(b.GetName() for b in out_tree.GetListOfBranches())
    check.Close()

    return {
        "source": str(source),
        "destination": str(destination),
        "source_entries": entries,
        "destination_entries": out_entries,
        # Row count preserved EXACTLY: this step must not select. A mismatch here
        # means the slim is a different population from the inventory.
        "rows_preserved": out_entries == entries,
        "branches_kept": len(out_branches),
        "branches_requested": len(keep),
        "branches_missing_from_source": missing,
        "branches_listed_but_unreadable": unreadable,
        "seconds": elapsed,
        "entries_per_second": entries / elapsed if elapsed else None,
        "bytes_out": destination.stat().st_size,
        "threads": threads,
        "applies_no_selection": True,
        "nested_branches_flattened": dict(NESTED_BRANCHES),
        "nested_inner_width_violations": violations,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True,
                        help="a playlist manifest listing tuple paths")
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=16)
    parser.add_argument("--limit", type=int, help="first N files only")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    sources = [Path(line.strip()) for line in
               args.manifest.read_text().splitlines() if line.strip()]
    if args.limit:
        sources = sources[: args.limit]

    # ONE FILE IS THE UNIT OF FAILURE, not one playlist. The first version raised
    # out of the loop, so a single unreadable file killed a whole task and took
    # every file after it: ten of twenty-four array tasks died that way, all of
    # them Data, while the same code succeeded on the first Data file when run
    # alone. A failure is recorded and the loop continues, exactly as the GPU
    # per-cell isolation does, and the report names what failed rather than
    # leaving it as an absence.
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for index, source in enumerate(sources, 1):
        destination = args.outdir / (source.stem + ".slim.root")
        if destination.exists():
            print(f"[{index}/{len(sources)}] exists, skipping {destination.name}")
            continue
        try:
            record = slim(source, destination, args.threads)
        except Exception as error:                        # noqa: BLE001 - recorded
            import traceback
            failures.append({"source": str(source), "error": repr(error)[:400],
                             "traceback": traceback.format_exc()[-1200:]})
            print(f"[{index}/{len(sources)}] FAILED {source.name}: {error!r:.160}")
            if destination.exists():
                destination.unlink()          # never leave a partial slim behind
            continue
        rows.append(record)
        print(f"[{index}/{len(sources)}] {source.name}: "
              f"{record['source_entries']:,} rows, "
              f"{record['branches_kept']} branches, "
              f"{record['seconds']:.1f}s, "
              f"{record['bytes_out'] / 2**20:.0f} MiB, "
              f"preserved={record['rows_preserved']}")
        args.report.write_text(json.dumps(
            {"manifest": str(args.manifest), "files": rows,
             "failures": failures}, indent=2) + "\n")

    args.report.write_text(json.dumps(
        {"manifest": str(args.manifest), "files": rows, "failures": failures,
         "files_ok": len(rows), "files_failed": len(failures),
         "all_rows_preserved": all(r["rows_preserved"] for r in rows),
         "total_source_entries": sum(r["source_entries"] for r in rows),
         "total_bytes_out": sum(r["bytes_out"] for r in rows)}, indent=2) + "\n")
    if failures:
        print(f"{len(failures)} file(s) failed; see the report. The task does NOT "
              "fail on them, so the rest of the playlist is extracted.")


if __name__ == "__main__":
    main()
