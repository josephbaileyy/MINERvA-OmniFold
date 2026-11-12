#!/usr/bin/env python3
"""RDX's timing probe for the merge job's limit (coverage-5b-audit's low z3, 2026-11-12), on a login node at 0 node-h.

    rdx_probe_walk.py OMNIFILE [--scale 12.25] [--out probe.json]

It reads one omnifile's mc_signal_reco columns as rdx_dump.build does, runs the vectorized walk (kept_walk_np, the
dump's path) and then the loop (kept_walk, the reference), requires them bitwise equal (exit 1 otherwise), and records
the rows, the seconds and the peak resident memory of each. --scale (default 32.8M / 2.68M = 12.25, the merged tree over
1A's) projects the merged vectorized walk. The merge job's limit is set from that, at 1.5 times the projection, before
its connect (the director's ruling on z3, 2026-11-12).
"""
from __future__ import annotations

import argparse
import json
import resource
import sys
import time
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ND = _HERE.parent
for _p in (str(_ND.parent / "2d-unfolding"), str(_ND), str(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import rdx_dump as DP  # noqa: E402

SCALE = 32.8e6 / 2.68e6


def _rss_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 ** 2 if sys.platform != "darwin" else 1024 ** 3)


def probe(omnifile: str, reader, bounds, pot_scale, in_ps, ex_t, ex_r, theta_max, scale=SCALE) -> dict:
    """Both walks on one omnifile: the vectorized one first (so its peak memory is measured before the loop's lists
    exist), then the loop; they must agree bitwise. The merge limit is set from the vectorized timing."""
    cols = ["MC", "MC_pz", "sim", "sim_pz", "sim_pass", "w_truth", "w_reco", *ex_t, *ex_r, *DP.TRUTHX, *DP.IDS]
    t0 = time.time()
    c = reader(omnifile, "mc_signal_reco", cols)
    t1 = time.time()
    rss_read = _rss_gb()
    ent_v, arr_v = DP.kept_walk_np(c, ex_t, ex_r, bounds, pot_scale, in_ps, theta_max)
    t2 = time.time()
    rss_v = _rss_gb()
    ent_l, arr_l = DP.kept_walk(c, ex_t, ex_r, bounds, pot_scale, in_ps)
    t3 = time.time()
    rss_l = _rss_gb()
    equal = bool(np.array_equal(ent_v, ent_l) and all(arr_v[k].dtype == arr_l[k].dtype and np.array_equal(arr_v[k], arr_l[k])
                                                      for k in arr_l))
    rows = len(c["MC"])
    return {"omnifile": omnifile, "rows": rows, "kept": int(len(ent_v)), "walks_bitwise_equal": equal,
            "read_s": round(t1 - t0, 1), "vectorized_s": round(t2 - t1, 1), "loop_s": round(t3 - t2, 1),
            "peak_rss_gb_after_read": round(rss_read, 2), "peak_rss_gb_after_vectorized": round(rss_v, 2),
            "peak_rss_gb_after_loop": round(rss_l, 2), "scale": scale,
            "projected_merged_vectorized_s": round((t2 - t0) * scale, 0),
            "projected_merged_vectorized_rss_gb": round(rss_v * scale, 1),
            "verdict": "PASS" if equal else "FAIL"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("omnifile")
    ap.add_argument("--scale", type=float, default=SCALE)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args(argv)
    import ROOT
    import s5p_input_dumps as D
    u2d, und, extras, edges = D.setup()
    f = ROOT.TFile.Open(a.omnifile, "READ")
    _, _, pot_scale = u2d.get_pot_scales(f)
    f.Close()
    rec = probe(a.omnifile, DP.root_reader, (edges[0][0], edges[0][-1], edges[1][0], edges[1][-1]), pot_scale,
                u2d.in_truth_phase_space, [und.EXTRA_AXES[x]["truth"] for x in DP.AXES],
                [und.EXTRA_AXES[x]["reco"] for x in DP.AXES], u2d.MAX_MUON_THETA_RAD, a.scale)
    text = json.dumps(rec, indent=1)
    print(text)
    if a.out:
        a.out.write_text(text + "\n")
    return 0 if rec["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
