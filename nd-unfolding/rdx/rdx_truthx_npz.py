#!/usr/bin/env python3
"""RDX C-TRUTHX-NPZ (RDX-DECLARATION.md rev 3 §3, D6): the per-row join of the merged dump and its sidecar back to
the per-playlist omnifiles, before stage 3.

    rdx_truthx_npz.py NPZ SIDECAR [--out x.json]

PASS requires:
- the sidecar's schema and its npz_sha256 equal to NPZ's sha256, and one sidecar row per MCgen row;
- every mc_id (playlist index, run, subrun, event) unique;
- for every MCgen row, the row of that event in its playlist's omnifile mc_signal_reco (the sidecar's meta names the
  per-playlist files, in index order) has: float32(MC), float32(MC_pz) equal to MCgen[:, 0], MCgen[:, 1] (the dump's
  cast); w_truth x pot_scale equal to the npz's w_truth (float64, as the collector computes it; pot_scale from the
  sidecar's meta); and its five truthx doubles equal to the sidecar's truthx, bitwise (float64, uncast: y5).
A row whose event is not in its playlist's omnifile fails. Exit 0 PASS, 1 FAIL, 2 could not check.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import rdx_common as C  # noqa: E402
import rdx_truthx_rows as R  # noqa: E402


def check(npz: Path, sidecar: Path, reader) -> dict:
    bad = []
    with np.load(sidecar, allow_pickle=False) as s:
        meta = json.loads(str(s["meta"]))
        tx = np.asarray(s["truthx"])
        mc_id = np.asarray(s["mc_id"])
        names = tuple(str(x) for x in s["truthx_names"])
    if meta.get("schema") != C.SIDECAR_SCHEMA:
        raise C.CheckError(f"the sidecar's schema is {meta.get('schema')!r}")
    if meta.get("npz_sha256") != C.sha256(npz):
        raise C.CheckError("the sidecar does not name this npz's sha256")
    if names != C.TRUTHX or tx.dtype != np.float64 or mc_id.dtype != np.int64:
        raise C.CheckError("the sidecar's columns or dtypes are not the declared ones")
    with np.load(npz, allow_pickle=True) as z:
        gen = np.asarray(z["MCgen"])
        w = np.asarray(z["w_truth"])
    n = len(gen)
    if tx.shape != (n, len(C.TRUTHX)) or mc_id.shape != (n, 4) or w.shape != (n,):
        raise C.CheckError(f"the sidecar has {tx.shape}/{mc_id.shape} rows for {n} MCgen rows")
    full = np.empty(n, dtype=[("p", "i8"), ("k", "i8")])
    full["p"], full["k"] = mc_id[:, 0], C.pack(mc_id[:, 1], mc_id[:, 2], mc_id[:, 3])
    if np.unique(full).size != n:
        bad.append("mc_id values are not unique")
    pot = float(meta["pot_scale"])
    playlists = meta["playlists"]
    seen = np.zeros(n, bool)
    per = {}
    for p, (name, path) in enumerate(playlists):
        rows = np.flatnonzero(mc_id[:, 0] == p)
        if rows.size == 0:
            continue
        c = reader(path, "mc_signal_reco", [*C.IDS, "MC", "MC_pz", "w_truth", *C.TRUTHX])
        sk, order = C.index_of(C.pack(*(c[k] for k in C.IDS)), f"{name}'s mc_signal_reco")
        j = C.lookup(sk, order, C.pack(mc_id[rows, 1], mc_id[rows, 2], mc_id[rows, 3]))
        lost = int((j < 0).sum())
        if lost:
            bad.append(f"{name}: {lost} rows have no event in the playlist's omnifile")
        r, jj = rows[j >= 0], j[j >= 0]
        seen[r] = True
        fails = {
            "MC": int((np.asarray(c["MC"], np.float64)[jj].astype(np.float32) != gen[r, 0]).sum()),
            "MC_pz": int((np.asarray(c["MC_pz"], np.float64)[jj].astype(np.float32) != gen[r, 1]).sum()),
            "w_truth": int((np.asarray(c["w_truth"], np.float64)[jj] * pot != w[r]).sum()),
            **{k: int((np.asarray(c[k], np.float64)[jj] != tx[r, i]).sum()) for i, k in enumerate(C.TRUTHX)},
        }
        for k, v in fails.items():
            if v:
                bad.append(f"{name}: {v} rows differ in {k}")
        per[name] = {"rows": int(rows.size), "joined": int(jj.size), "differing": fails}
    if not seen.all():
        bad.append(f"{int((~seen).sum())} rows were not joined (unknown playlist index or no event)")
    return {"mode": "rdx-truthx-npz", "rows": n, "per_playlist": per, "pot_scale": pot, "failures": bad,
            "verdict": "PASS" if not bad else "FAIL"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("npz", type=Path)
    ap.add_argument("sidecar", type=Path)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args(argv)
    try:
        res = dict(check(a.npz, a.sidecar, R.uproot_reader), npz=str(a.npz), sidecar=str(a.sidecar),
                   npz_sha256=C.sha256(a.npz), sidecar_sha256=C.sha256(a.sidecar))
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"verdict": "COULD_NOT_CHECK", "error": repr(exc)}))
        return 2
    text = json.dumps(res, indent=1)
    print(text)
    if a.out:
        a.out.write_text(text + "\n")
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
