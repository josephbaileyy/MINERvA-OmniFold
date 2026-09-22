"""Build (or check) the committed D5 generator-ratio tables, `calibration/d5_tables.json`.

    python build_d5_calibration.py --directory <dir with the *_xsec3d.root files> [--check]

The ROOT files are the standalone generator predictions of `3d-unfolding/genie/` (README there),
canonically at `distortions.D5_DIR_DEFAULT` on Perlmutter. `--check` rebuilds from ``--directory``
and refuses unless every table digest and source sha256 equals the committed file's -- the Phase-E
preparation job runs this against the canonical directory so the committed table is shown to be
reproducible from the canonical files, not just from a copy.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import distortions as dist  # noqa: E402


def build(directory: Path) -> dict:
    tables = {gen: dist.build_d5_table(gen, directory) for gen in dist.D5_GENERATORS}
    post_hoc = {gen: dist.build_d5_table(gen, directory, "per_pparallel_slice")
                for gen in dist.D5_GENERATORS}
    return {"schema": "phase-e-d5-tables/1", "canonical_directory": dist.D5_DIR_DEFAULT,
            "built_from": str(directory), "tables": tables, "tables_post_hoc": post_hoc}


def digests(payload: dict) -> dict:
    return {f"{kind}/{gen}": {"table_sha256": t["table_sha256"],
                              "generator_sha256": t["sources"]["generator"]["sha256"],
                              "reference_sha256": t["sources"]["reference"]["sha256"]}
            for kind in ("tables", "tables_post_hoc") for gen, t in payload[kind].items()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=Path(dist.D5_DIR_DEFAULT))
    parser.add_argument("--output", type=Path, default=dist.D5_CALIBRATION)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--check-output", type=Path, default=None,
                        help="with --check: where to write the comparison record")
    args = parser.parse_args()
    payload = build(args.directory)
    if args.check:
        committed = json.loads(dist.D5_CALIBRATION.read_text())
        got, want = digests(payload), digests(committed)
        record = {"schema": "phase-e-d5-check/1", "directory": str(args.directory),
                  "rebuilt": got, "committed": want, "agrees": got == want}
        if args.check_output is not None:
            args.check_output.parent.mkdir(parents=True, exist_ok=True)
            args.check_output.write_text(json.dumps(record, indent=1) + "\n")
        if got != want:
            raise SystemExit(f"[d5] rebuilt tables differ from the committed ones: {record}")
        print(f"[d5] {len(got)} tables rebuilt from {args.directory} equal the committed ones")
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")
    for gen, t in list(payload["tables"].items()) + list(payload["tables_post_hoc"].items()):
        s = t["stats"]
        print(f"[d5] {gen:11s} {t['normalization']:20s} merged-bins={s['bins_in_merged_groups']:4d} groups={s['groups']:4d}"
              f" unresolved-cols={len(s['unresolved_columns']):3d} clipped lo/hi="
              f"{s['clipped_low']}/{s['clipped_high']} w in [{s['weight_min']:.3f}, "
              f"{s['weight_max']:.3f}] total ratio={s['total_x_over_total_tunev1']:.4f} "
              f"TuneV1 mass clipped low={s['tunev1_mass_fraction_clipped_low']:.4f}")


if __name__ == "__main__":
    main()
