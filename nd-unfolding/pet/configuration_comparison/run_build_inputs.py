"""Build his complete-arm inputs for every slim file in one playlist/stream."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

import numpy as np

from build_theirs_inputs import build_file

MC_FIELDS = ("mc_run", "mc_subrun", "mc_nthEvtInFile")
DATA_FIELDS = ("ev_run", "ev_subrun", "ev_gate")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slimdir", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--stream", choices=("MC", "Data"), required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--limit-files", type=int)
    args = parser.parse_args()

    fields = MC_FIELDS if args.stream == "MC" else DATA_FIELDS
    files = sorted(args.slimdir.glob("*.slim.root"))
    if args.limit_files:
        files = files[: args.limit_files]
    args.outdir.mkdir(parents=True, exist_ok=True)

    done, failed, rows_total = [], [], 0
    for index, slim in enumerate(files, 1):
        out = args.outdir / (slim.stem.replace(".slim", "") + ".theirs.npz")
        if out.exists():
            continue
        started = time.perf_counter()
        try:
            blocks = build_file(slim, fields)
        except Exception as error:                        # noqa: BLE001 - recorded
            failed.append({"slim": str(slim), "error": repr(error)[:300]})
            print(f"[{index}/{len(files)}] FAILED {slim.name}: {error!r:.120}")
            continue
        # float16 would halve this and lose the log-energy tail; float32 is the
        # production precision and the inputs are what the comparison consumes.
        np.savez_compressed(out, **blocks)
        rows = len(blocks["identity"])
        rows_total += rows
        done.append({"slim": str(slim), "out": str(out), "rows": rows,
                     "seconds": time.perf_counter() - started})
        print(f"[{index}/{len(files)}] {slim.name}: {rows:,} rows, "
              f"{time.perf_counter() - started:.1f}s")
        args.report.write_text(json.dumps(
            {"done": done, "failed": failed, "rows": rows_total}, indent=2) + "\n")

    args.report.write_text(json.dumps(
        {"done": done, "failed": failed, "rows": rows_total,
         "files_built": len(done), "files_failed": len(failed)}, indent=2) + "\n")


if __name__ == "__main__":
    main()
