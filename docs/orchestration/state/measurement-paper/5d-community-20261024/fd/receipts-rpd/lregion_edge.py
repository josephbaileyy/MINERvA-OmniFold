#!/usr/bin/env python3
"""The audit's L-region edge mutant (L_REGION lower edge 1.5 -> 1.0; FD-RPD-DECLARATION-PART2.md section 9, the
director's ask (2) of 2026-11-03): on the pinned H2 definition and the fine grid, the L-region weights wL under the
lower edge 1.0 are bitwise those under 1.5, because no fine p_parallel edge lies below 1.5. The mutant is equivalent
in every number the readers compute; it changes only the stage-0 record's printed "regions", and the declared-constants
test kills it there.

    python3 -I -B lregion_edge.py <repo>
"""
import sys
from pathlib import Path

import numpy as np

REPO = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(REPO / "nd-unfolding"))
import fd_rpd as rp  # noqa: E402
import s1_assemble as sa  # noqa: E402

g = rp.Grid(REPO / "nd-unfolding/pv-ladder/readouts/h2_definition.json")
ipz = np.unravel_index(np.arange(g.fm.size), sa.s1.fine_shape())[sa.s1.AXES.index("pz")]
e = np.asarray(sa.s1.FINE["pz"], float)
lo, hi = e[ipz], e[ipz + 1]
rep = g.fm >= 0
print(f"L_REGION {rp.L_REGION}; fine p_parallel edges {e.tolist()}")
print(f"reporting fine cells {int(rep.sum())} of {g.fm.size}; lowest p_parallel edge of a reporting cell {lo[rep].min()}")
print(f"reporting fine cells with lower edge in [1.0, 1.5): {int((rep & (lo >= 1.0) & (lo < 1.5)).sum())}")
mut = np.where(rep & (lo >= 1.0) & (hi <= rp.L_REGION[1]), sa.s1.fine_volume(), 0.0)
same = bool(np.array_equal(mut, g.wL))
print(f"wL under 1.0 equals wL under 1.5 bitwise: {same}; nonzero entries {int((g.wL != 0).sum())}")
raise SystemExit(0 if same and rp.L_REGION == (1.5, 8.0) else 1)
