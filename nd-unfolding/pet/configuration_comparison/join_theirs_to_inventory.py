"""Align his built inputs to the inventory, by event identity and never by position.

The inventory defines which events the comparison uses, in which order, with
which weights. The extraction is a superset of it -- the tuples are
pre-selection -- so this step SELECTS and REORDERS the built rows to match the
inventory, using the identity the sidecar verified.

Three things it refuses to do:

* it never falls back to positional alignment. A positional join would succeed
  silently on a superset and be wrong for every row;
* it never invents a row for an inventory event it cannot find. Unmatched rows
  are counted and reported, and the caller decides;
* it never uses one stream's identity fields for another. Data joins on
  (ev_run, ev_subrun, ev_gate) and MC on (mc_run, mc_subrun, mc_nthEvtInFile) --
  crossing them gives a clean zero overlap, which looks exactly like a broken
  extraction and is in fact a broken query.

NOT CITABLE FOR any performance claim.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

STREAM_FIELDS = {
    "sig": ("mc_run", "mc_subrun", "mc_nthEvtInFile"),
    "bkg": ("mc_run", "mc_subrun", "mc_nthEvtInFile"),
    "data": ("ev_run", "ev_subrun", "ev_gate"),
}


def _pack(identity: np.ndarray) -> np.ndarray:
    """Three int32 fields into one int64 key, so lookups are a single hash."""
    a = identity.astype(np.int64)
    if a.shape[1] != 3:
        raise ValueError(f"expected three identity fields, got {a.shape[1]}")
    # 21 bits each is ample: runs < 2^21, subruns < 2^21, gate/nth < 2^21 both
    # observed well below. Overflow would silently merge events, so it is checked.
    if a.max() >= (1 << 21) or a.min() < 0:
        raise ValueError(
            f"identity value outside the packable range [0, 2^21): "
            f"min {a.min()}, max {a.max()}. Packing would merge distinct events."
        )
    return (a[:, 0] << np.int64(42)) | (a[:, 1] << np.int64(21)) | a[:, 2]


def build_index(input_dir: Path) -> tuple[np.ndarray, list[Path], np.ndarray]:
    """Every built row's key, with the file and row it came from."""
    files = sorted(input_dir.glob("*.theirs.npz"))
    keys, origin = [], []
    for file_index, path in enumerate(files):
        with np.load(path) as blob:
            identity = blob["identity"]
        keys.append(_pack(identity))
        origin.append(np.stack([np.full(len(identity), file_index, dtype=np.int32),
                                np.arange(len(identity), dtype=np.int32)], axis=1))
    if not keys:
        raise SystemExit(f"[join] no built inputs in {input_dir}")
    return np.concatenate(keys), files, np.concatenate(origin)


def reco_coverage(matched: np.ndarray, pass_reco: np.ndarray) -> dict[str, Any]:
    """Coverage over the rows that CAN be matched: the pass_reco rows.

    An event that failed reconstruction has no reconstructed object, so no token
    can be built from it -- it exists only in the AnaTuple's `Truth` tree and
    enters the comparison through the truth leg. Requiring his inputs to cover
    it was a gate on the wrong population: it demanded a reco input for events
    with no reco, and reported 59.5% for a join that covers everything it can.

    The requirement that matters is that no `pass_reco` row is missing, because
    a missing one WOULD be an event his arm cannot see and ours can.
    """
    matched = np.asarray(matched, dtype=bool)
    reco = np.asarray(pass_reco, dtype=bool)
    if matched.shape != reco.shape:
        raise ValueError(
            f"pass_reco has {reco.shape} rows and the join {matched.shape}; "
            "they must describe the same inventory")
    total = int(reco.sum())
    covered = int((matched & reco).sum())
    return {
        "pass_reco_rows": total,
        "pass_reco_matched": covered,
        "pass_reco_unmatched": total - covered,
        "pass_reco_fraction": (covered / total) if total else 0.0,
        "matched_without_reco": int((matched & ~reco).sum()),
        "unmatched_without_reco": int((~matched & ~reco).sum()),
        "criterion": (
            "every pass_reco row must have a built input. Rows without reco "
            "have no reconstructed object to build a token from and are zeroed "
            "for BOTH arms, exactly as the production loader zeroes ours"
        ),
    }


def join(sidecar: Path, stream: str, input_dirs: list[Path],
         pass_reco: np.ndarray | None = None) -> dict[str, Any]:
    blob = np.load(sidecar, mmap_mode="r")
    fields = [str(x) for x in blob[f"{stream}_identity_fields"]]
    expected = list(STREAM_FIELDS[stream])
    if fields != expected:
        raise SystemExit(
            f"[join] the sidecar says {stream} joins on {fields}, this expects "
            f"{expected}. Using the wrong fields gives a clean zero overlap.")
    inventory = np.asarray(blob[f"{stream}_event_id"])
    inventory_keys = _pack(inventory)

    all_keys, all_files, all_origin = [], [], []
    offset = 0
    for directory in input_dirs:
        keys, files, origin = build_index(directory)
        origin = origin.copy()
        origin[:, 0] += offset
        offset += len(files)
        all_keys.append(keys)
        all_files.extend(files)
        all_origin.append(origin)
    built_keys = np.concatenate(all_keys)
    built_origin = np.concatenate(all_origin)

    order = np.argsort(built_keys, kind="stable")
    sorted_keys = built_keys[order]
    position = np.searchsorted(sorted_keys, inventory_keys)
    position = np.clip(position, 0, len(sorted_keys) - 1)
    matched = sorted_keys[position] == inventory_keys
    resolved = np.where(matched, order[position], -1)

    duplicates = int(len(built_keys) - len(np.unique(built_keys)))
    coverage = (reco_coverage(matched, pass_reco) if pass_reco is not None
                else None)
    return {
        "reco_coverage": coverage,
        "stream": stream,
        "identity_fields": fields,
        "inventory_rows": int(len(inventory_keys)),
        "built_rows": int(len(built_keys)),
        "built_files": len(all_files),
        "matched": int(matched.sum()),
        "unmatched": int((~matched).sum()),
        "match_fraction": float(matched.mean()),
        "duplicate_built_keys": duplicates,
        "row_index": resolved,
        "origin": built_origin,
        "files": [str(f) for f in all_files],
        "positional_fallback": "never",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sidecar", type=Path, required=True)
    parser.add_argument("--stream", choices=sorted(STREAM_FIELDS), required=True)
    parser.add_argument("--input-dirs", nargs="+", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--target-npz", type=Path, default=None,
                        help="the production inputs, for their pass_reco flags")
    args = parser.parse_args()
    pass_reco = None
    if args.target_npz is not None:
        with np.load(args.target_npz, mmap_mode="r") as target:
            pass_reco = (np.ones(len(np.asarray(target["measured_pc"])), bool)
                         if args.stream == "data"
                         else np.asarray(target["pass_reco"]).astype(bool))
    result = join(args.sidecar, args.stream, args.input_dirs, pass_reco)
    np.savez_compressed(args.output, row_index=result.pop("row_index"),
                        origin=result.pop("origin"))
    args.report.write_text(json.dumps(result, indent=2) + "\n")
    print(f"{result['stream']}: {result['matched']:,}/{result['inventory_rows']:,} "
          f"matched ({100*result['match_fraction']:.2f}%), "
          f"{result['unmatched']:,} unmatched, "
          f"{result['duplicate_built_keys']:,} duplicate built keys")
    if result.get("reco_coverage") is not None:
        c = result["reco_coverage"]
        print(f"{result['stream']}: pass_reco {c['pass_reco_matched']:,}/"
              f"{c['pass_reco_rows']:,} ({100*c['pass_reco_fraction']:.4f}%), "
              f"{c['unmatched_without_reco']:,} unmatched rows have no reco")


if __name__ == "__main__":
    main()
