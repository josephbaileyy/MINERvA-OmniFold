#!/usr/bin/env python3
"""Decompose the Part 2 `masks_and_padding` FAIL into its individual conjuncts.

`a2_recover.py` scored that check as a single AND over seven conditions and recorded only the
aggregate verdict, so the receipt says FAIL without saying which condition broke. This re-runs the
same conditions one at a time over the same rows (the union of the final stage's halves, taken from
a run's own `dump_rows_a`/`dump_rows_b`) and, for each one that fails, reports how many rows and
which token columns are involved plus a worked example.

Reads only; writes one JSON receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any

import numpy as np


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def jsonable(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [jsonable(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return jsonable(obj.tolist())
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    return obj


def pad_report(name: str, block: np.ndarray, real: np.ndarray) -> dict[str, Any]:
    """Are the slots the mask calls 'pad' actually all-zero, column by column?"""
    pad = ~real
    if block.ndim == 2:                       # (rows, tokens) -> one implicit column
        block = block[:, :, None]
    bad = (block != 0) & pad[:, :, None]
    per_col = bad.reshape(-1, block.shape[2]).sum(0)
    rows_bad = np.flatnonzero(bad.any(axis=(1, 2)))
    out = {
        "pad_slots": int(pad.sum()),
        "pad_slots_with_a_nonzero_column": int(bad.any(2).sum()),
        "rows_with_any_nonzero_pad": int(rows_bad.size),
        "nonzero_pad_entries_per_column": per_col,
        "all_zero": bool(bad.sum() == 0),
    }
    if rows_bad.size:
        r = int(rows_bad[0])
        t = int(np.flatnonzero(bad[r].any(1))[0])
        out["example"] = {"row_in_used": r, "token_slot": t,
                          "token_values": block[r, t].astype(float),
                          "n_real_tokens_in_that_row": int(real[r].sum())}
    return out


def order_report(real: np.ndarray) -> dict[str, Any]:
    """Do real tokens all precede pads, with no real token after a pad?"""
    rises = np.diff(real.astype(np.int8), axis=1) > 0      # pad -> real == out of order
    rows_bad = np.flatnonzero(rises.any(1))
    out = {"rows_out_of_order": int(rows_bad.size), "in_order": bool(rows_bad.size == 0)}
    if rows_bad.size:
        r = int(rows_bad[0])
        out["example"] = {"row_in_used": r, "real_token_pattern": real[r].astype(int),
                          "n_real_tokens": int(real[r].sum())}
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--closure-npz", type=Path, required=True)
    ap.add_argument("--run-weights", type=Path, required=True,
                    help="any final-stage run npz; supplies dump_rows_a/dump_rows_b")
    ap.add_argument("--outdir", type=Path, required=True)
    args = ap.parse_args(argv)
    args.outdir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    with np.load(args.run_weights) as blob:
        rows_a = np.asarray(blob["dump_rows_a"]).astype(np.int64)
        rows_b = np.asarray(blob["dump_rows_b"]).astype(np.int64)
    used = np.union1d(rows_a, rows_b)
    print(f"[mask] used rows: {used.size}", flush=True)

    with np.load(args.closure_npz, allow_pickle=False) as h:
        part_reco = np.asarray(h["part_reco"])[used]
        reco_view = np.asarray(h["reco_view"])[used]
        reco_time = np.asarray(h["reco_time"])[used]
        part_gen = np.asarray(h["part_gen"])[used]
        pass_reco = np.asarray(h["pass_reco"]).astype(bool)[used]
        pass_truth = np.asarray(h["pass_truth"]).astype(bool)[used]
    print(f"[mask] loaded ({time.time() - t0:.0f}s) part_reco{part_reco.shape} "
          f"part_gen{part_gen.shape}", flush=True)

    # The mask exactly as PET reads it: energy column non-zero.
    real_r = part_reco[:, :, 0] != 0
    real_g = part_gen[:, :, 0] != 0

    conj = {
        "tail_order_reco": order_report(real_r),
        "tail_order_gen": order_report(real_g),
        "pads_all_zero_part_reco": pad_report("part_reco", part_reco, real_r),
        "pads_all_zero_part_gen": pad_report("part_gen", part_gen, real_g),
        "pads_all_zero_reco_view": pad_report("reco_view", reco_view, real_r),
        "pads_all_zero_reco_time": pad_report("reco_time", reco_time, real_r),
        "no_reco_token_on_not_pass_reco": {
            "rows": int((real_r.sum(1)[~pass_reco] != 0).sum()),
            "ok": bool((real_r.sum(1)[~pass_reco] != 0).sum() == 0)},
    }
    passed = {
        "tail_order_reco": conj["tail_order_reco"]["in_order"],
        "tail_order_gen": conj["tail_order_gen"]["in_order"],
        "pads_all_zero_part_reco": conj["pads_all_zero_part_reco"]["all_zero"],
        "pads_all_zero_part_gen": conj["pads_all_zero_part_gen"]["all_zero"],
        "pads_all_zero_reco_view": conj["pads_all_zero_reco_view"]["all_zero"],
        "pads_all_zero_reco_time": conj["pads_all_zero_reco_time"]["all_zero"],
        "no_reco_token_on_not_pass_reco": conj["no_reco_token_on_not_pass_reco"]["ok"],
    }

    # A zero-energy real token is indistinguishable from a pad under this mask. Measure how many
    # slots that ambiguity could involve, using the other columns as the witness of a real token.
    other_nonzero_r = (part_reco[:, :, 1:] != 0).any(2)
    other_nonzero_g = (part_gen[:, :, 1:] != 0).any(2)
    ambiguity = {
        "reading": ("slots whose energy column is 0 but some other column is not: under "
                    "mask = (energy != 0) these are read as padding"),
        "reco_slots_zero_energy_other_columns_nonzero": int((other_nonzero_r & ~real_r).sum()),
        "gen_slots_zero_energy_other_columns_nonzero": int((other_nonzero_g & ~real_g).sum()),
        "reco_rows_affected": int((other_nonzero_r & ~real_r).any(1).sum()),
        "gen_rows_affected": int((other_nonzero_g & ~real_g).any(1).sum()),
    }

    receipt = {
        "scope": ("Phase A2 Part 2: which conjunct of the masks_and_padding check fails "
                  "(a2_recover.py:831-835 recorded only the AND)"),
        "inputs": {
            "closure_npz": {"path": str(args.closure_npz), "sha256": sha256(args.closure_npz)},
            "run_weights": {"path": str(args.run_weights), "sha256": sha256(args.run_weights)},
        },
        "rows_checked": int(used.size),
        "pass_reco_rows": int(pass_reco.sum()),
        "pass_truth_rows": int(pass_truth.sum()),
        "part_reco_shape": list(part_reco.shape),
        "part_gen_shape": list(part_gen.shape),
        "conjunct_passed": passed,
        "aggregate_would_be": "PASS" if all(passed.values()) else "FAIL",
        "failing_conjuncts": [k for k, v in passed.items() if not v],
        "detail": conj,
        "zero_energy_token_ambiguity": ambiguity,
        "seconds": time.time() - t0,
    }
    out = args.outdir / "mask_conjuncts.json"
    out.write_text(json.dumps(jsonable(receipt), indent=1, sort_keys=False))
    print(f"[mask] failing: {receipt['failing_conjuncts']}", flush=True)
    print(f"[mask] wrote {out} ({time.time() - t0:.0f}s)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
