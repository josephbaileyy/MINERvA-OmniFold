#!/usr/bin/env python3
"""RDX's timing probe for the merge job's limit (coverage-5b-audit's low z3, 2026-11-12), on a login node at 0 node-h.

    rdx_probe_walk.py OMNIFILE [--scale 12.25] [--out probe.json]

It reads one omnifile's mc_signal_reco columns as rdx_dump.build does and runs rdx_dump.kept_walk on them, recording
the rows, the read and walk seconds, and the peak resident memory. --scale (default 32.8M / 2.68M = 12.25, the merged
tree over 1A's) projects the merged walk's seconds and memory. The merge job's limit is set from this record, at 1.5
times the projection, before its connect.
"""
from __future__ import annotations

import argparse
import json
import resource
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ND = _HERE.parent
for _p in (str(_ND.parent / "2d-unfolding"), str(_ND), str(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import rdx_dump as DP  # noqa: E402

SCALE = 32.8e6 / 2.68e6


def probe(omnifile: str, reader, bounds, pot_scale, in_ps, ex_t, ex_r, scale=SCALE) -> dict:
    cols = ["MC", "MC_pz", "sim", "sim_pz", "sim_pass", "w_truth", "w_reco", *ex_t, *ex_r, *DP.TRUTHX, *DP.IDS]
    t0 = time.time()
    c = reader(omnifile, "mc_signal_reco", cols)
    t1 = time.time()
    ent, _ = DP.kept_walk(c, ex_t, ex_r, bounds, pot_scale, in_ps)
    t2 = time.time()
    rss_gb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 ** 2 if sys.platform != "darwin" else 1024 ** 3)
    rows = len(c["MC"])
    return {"omnifile": omnifile, "rows": rows, "kept": int(len(ent)), "read_s": round(t1 - t0, 1),
            "walk_s": round(t2 - t1, 1), "peak_rss_gb": round(rss_gb, 2), "scale": scale,
            "projected_merged_s": round((t2 - t0) * scale, 0), "projected_merged_rss_gb": round(rss_gb * scale, 1)}


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
                [und.EXTRA_AXES[x]["reco"] for x in DP.AXES], a.scale)
    text = json.dumps(rec, indent=1)
    print(text)
    if a.out:
        a.out.write_text(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
