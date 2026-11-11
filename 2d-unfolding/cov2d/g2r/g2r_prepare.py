#!/usr/bin/env python3
"""COV2D-G2R §6 step 1, the prepare: the miss map from $UNI, P5's checks, and the per-universe checks for all 175
universe columns in one pass. Every read goes through O_NOATIME (cov2d_receipt.open_noatime, as COV2D's step A reads
$UNI); the stat-before and stat-after of each input must agree on atime, or the step is a STOP.

  python g2r_prepare.py --omnifile $UNI --blocks <per-playlist omnifiles in hadd order> --out DIR

Writes DIR/g2r_map.npz (miss_rows, truth_rows, n_signal, n_truth, omnifile, omnifile_size) and DIR/g2r_prepare.json.
Exit 0 on PASS; 5 on a refusal (INVALID, the record says why); 7 if a per-playlist file is missing (the director's
STOP: "a STOP to me if P5's per-playlist block-size files are gone"); 8 if an atime moved.

Controls: G4 (P5's five alignment checks, in build_map and, per universe, universe_check) and G5 ($UNI's size by stat;
the declaration §8). The per-universe count of miss rows whose weight changes is recorded (the cheaper variant's count,
§7); it gates nothing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import cov2d as c  # noqa: E402
import cov2d_receipt as rc  # noqa: E402
import g2r  # noqa: E402

UNI_SIZE = 171_117_087_867        # COV2D-DECLARATION §7; P5's sbatch_p5.sh:61
S_COLS = ("MC", "MC_pz", "w_truth", "w_reco", "sim", "sim_pass")
T_COLS = ("MC", "MC_pz", "w_truth")
RC_INVALID, RC_STOP_BLOCKS, RC_ATIME = 5, 7, 8


def universes() -> list[tuple[str, int]]:
    """The 175 universes in COV2D's draw order (cov2d.ORDER, then each band's indices)."""
    return [(b, i) for b in c.ORDER for i in range(c.BANDS[b])]


def read_tree(f, tree: str, cols) -> dict:
    a = f[tree].arrays(list(cols), library="np")
    return {k: np.asarray(a[k]) for k in cols}


def block_sizes(paths: list[str]) -> list[tuple[str, int, int]]:
    import uproot
    out = []
    for p in paths:
        with rc.open_noatime(p) as fh:
            f = uproot.open(fh)
            n_s, n_t = f["mc_signal_reco"].num_entries, f["mc_truth_denom"].num_entries
            m = int(f["nTruthOnlyMisses"].member("fVal"))
        if n_s != n_t:
            raise g2r.Refusal(f"{p}: mc_signal_reco {n_s} != mc_truth_denom {n_t}")
        out.append((os.path.basename(p), int(n_s), m))
    return out


def run(omnifile: str, blocks: list[str], out: Path) -> tuple[dict, dict | None]:
    import uproot
    rec = {"schema": g2r.SCHEMA, "step": "prepare", "omnifile": os.path.realpath(omnifile), "stop": [],
           "universes": {}}
    rec["omnifile_size"] = os.path.getsize(omnifile)
    rec["G5"] = {"size": rec["omnifile_size"], "want": UNI_SIZE, "pass": rec["omnifile_size"] == UNI_SIZE}
    if not rec["G5"]["pass"]:
        raise g2r.Refusal(f"G5: $UNI is {rec['omnifile_size']} B, not {UNI_SIZE}")
    sizes = block_sizes(blocks)
    rec["blocks"] = [{"file": n, "entries": e, "misses": m} for n, e, m in sizes]
    with rc.open_noatime(omnifile) as fh:
        f = uproot.open(fh)
        merged = f.get("nTruthOnlyMisses")
        if merged is not None and int(merged.member("fVal")) != sum(m for _, _, m in sizes):
            raise g2r.Refusal(f"merged nTruthOnlyMisses {int(merged.member('fVal'))} != the blocks' sum")
        S = read_tree(f, "mc_signal_reco", S_COLS)
        T = read_tree(f, "mc_truth_denom", T_COLS)
        miss, truth, rec["map"] = g2r.build_map(S, T, sizes)
        for b, i in universes():
            cols = {k: c.column(k, b, i) for k in ("w_truth", "w_reco")}
            s = f["mc_signal_reco"].arrays([cols["w_truth"], cols["w_reco"]], library="np")
            t = f["mc_truth_denom"].arrays([cols["w_truth"]], library="np")
            rec["universes"][f"{b}:{i}"] = g2r.universe_check(
                S, T, s[cols["w_truth"]], s[cols["w_reco"]], t[cols["w_truth"]], miss, truth, sizes)
    ids = sorted(k for k, v in rec["universes"].items() if v["identity"])
    rec["identity_universes"] = {"count": len(ids), "labels": ids, "label": "the cheaper variant's count (§7); gates nothing"}
    path = out / "g2r_map.npz"
    np.savez(path, miss_rows=miss, truth_rows=truth, n_signal=np.array(len(S["MC"])), n_truth=np.array(len(T["MC"])),
             omnifile=np.array(rec["omnifile"]), omnifile_size=np.array(rec["omnifile_size"]))
    rec["map_npz_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return rec, {"miss": miss, "truth": truth}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--omnifile", required=True)
    ap.add_argument("--blocks", nargs="+", required=True)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    rec_path = a.out / "g2r_prepare.json"
    if rec_path.exists():
        raise SystemExit(f"refusing to overwrite {rec_path}")
    missing = [b for b in a.blocks if not os.path.exists(b)]
    if missing:
        rec_path.write_text(json.dumps({"schema": g2r.SCHEMA, "step": "prepare", "verdict": "STOP",
                                        "why": "P5's per-playlist block-size files are missing", "missing": missing},
                                       indent=1))
        print(f"G2R-PREPARE STOP: {len(missing)} per-playlist files missing")
        return RC_STOP_BLOCKS
    inputs = [a.omnifile, *a.blocks]
    before = {p: os.stat(p).st_atime_ns for p in inputs}
    try:
        rec, _ = run(a.omnifile, a.blocks, a.out)
        rec["verdict"] = "PASS"
        rc_ = 0
    except (g2r.Refusal, c.Refusal) as exc:
        rec, rc_ = {"schema": g2r.SCHEMA, "step": "prepare", "verdict": "INVALID", "why": str(exc)}, RC_INVALID
    moved = [p for p in inputs if os.stat(p).st_atime_ns != before[p]]
    rec["atime"] = {"checked": len(inputs), "moved": moved}
    if moved:
        rec["verdict"], rc_ = "STOP", rc_ | RC_ATIME
    rec_path.write_text(json.dumps(rec, indent=1, sort_keys=True))
    print(f"G2R-PREPARE {rec['verdict']}" + (f" ({rec.get('why')})" if rec.get("why") else ""))
    return rc_


if __name__ == "__main__":
    sys.exit(main())
