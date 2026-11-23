"""Decode a coarse joint cell name J<c> of the s5c 3^5 grid into its five coarse bins (note figure redraw, 2026-11-23).

Source of the decoding (committed):
  - axis order: nd-unfolding/s5c_coverage.py:30  AXES = ["pt", "pz", "eavail", "q3", "W"]
  - flat index: nd-unfolding/s5c_coverage.py:55-59  cshape = (3,3,3,3,3) over AXES; cell = np.ravel_multi_index(
    coarse_idx, cshape) (C order: pt slowest, W fastest); a row "J{c}" for each c in partition_J.supported_cells
  - coarse edges and the supported cells: docs/orchestration/state/s5c/contract.json:73-... measurement.partition_J
    (edges :76-..., hierarchy level H3 = 3 x 3 x 3 x 3 x 3, nd-unfolding/s5c_partition.py:13)
decode(c) is np.unravel_index(c, (3,) * 5) over that order. verify() asserts the decoding against the committed code
itself: it builds s5c_coverage.reported_functionals(contract) (the rows the receipts' functionals are), and for every
J<c> row checks that the fine cells it integrates are exactly the fine cells whose bin centres lie in the decoded
coarse box on all five axes. It also checks that the receipts' J names are the contract's supported cells, in order.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

AXES = ("pt", "pz", "eavail", "q3", "W")
CONTRACT = ("docs/orchestration/state/s5c/contract.json",
            "d54fd7c9641901736e58430e666db1ee782a54d9c95bf4439541872567c39c93")
UNIT = {"pt": r"GeV/$c$", "pz": r"GeV/$c$", "eavail": "GeV", "q3": r"GeV/$c$", "W": "GeV"}
SYM = {"pt": r"$p_T$", "pz": r"$p_\parallel$", "eavail": r"$E_{\rm avail}$", "q3": r"$q_3$", "W": r"$W$"}


def contract(repo: Path) -> dict:
    p = repo / CONTRACT[0]
    got = hashlib.sha256(p.read_bytes()).hexdigest()
    if got != CONTRACT[1]:
        raise SystemExit(f"sha256 mismatch for {p}: {got} != {CONTRACT[1]}")
    return json.loads(p.read_text())


def edges(repo: Path) -> dict:
    return {ax: list(contract(repo)["measurement"]["partition_J"]["edges"][ax]) for ax in AXES}


def decode(c: int) -> dict:
    """{axis: coarse bin 0..2} of the flat cell index c."""
    idx = np.unravel_index(int(c), (3,) * 5)
    return {ax: int(i) for ax, i in zip(AXES, idx)}


def rng(e: list, i: int) -> str:
    lo, hi = e[i], e[i + 1]
    return rf"$\geq${lo:g}" if hi >= 100 else f"{lo:g}–{hi:g}"


def verify(repo: Path, names: list) -> dict:
    """Assert the decoding against nd-unfolding/s5c_coverage.reported_functionals; return a summary."""
    sys.path.insert(0, str(repo / "nd-unfolding"))
    import s5c_coverage as sc  # noqa: E402  (ROOT-free)
    import project_cov_nd as pc  # noqa: E402
    assert tuple(sc.AXES) == AXES, sc.AXES
    con = contract(repo)
    J = con["measurement"]["partition_J"]
    assert J["hierarchy_level"] == "H3" and all(len(J["edges"][ax]) == 4 for ax in AXES)
    jn = [n for n in names if n.startswith("J")]
    assert jn == [f"J{c}" for c in J["supported_cells"]], "receipt J names are not the contract's supported cells"
    U, unames = sc.reported_functionals(con)
    assert unames == names, "receipt functional names differ from s5c_coverage.reported_functionals"
    shape = tuple(len(pc.AXIS_EDGES[a]) - 1 for a in AXES)
    fidx = np.unravel_index(np.arange(int(np.prod(shape))), shape)
    centres = [0.5 * (np.asarray(pc.AXIS_EDGES[a])[:-1] + np.asarray(pc.AXIS_EDGES[a])[1:])[fidx[k]]
               for k, a in enumerate(AXES)]
    for n in jn:
        b = decode(int(n[1:]))
        inbox = np.ones(len(centres[0]), bool)
        for k, a in enumerate(AXES):
            e = J["edges"][a]
            inbox &= (centres[k] >= e[b[a]]) & (centres[k] < e[b[a] + 1])
        support = U[unames.index(n)] != 0
        assert np.array_equal(support, inbox), f"{n}: decoded box {b} is not the fine cells it integrates"
    return {"n_J_checked": len(jn), "against": "nd-unfolding/s5c_coverage.py reported_functionals (rows J<c>)",
            "contract_sha256": CONTRACT[1]}


def verify_ew(repo: Path, names: list, eavail_edges: list, w_edges: list) -> dict:
    """ROUND 3: assert EW<k> is the (E_avail bin k // 6, W bin k % 6) cell of the projection, and that the edges a
    figure labels are the committed fine edges (nd-unfolding/project_cov_nd.py AXIS_EDGES).

    s5c_coverage.reported_functionals builds EW<k> as row k of pc.build_projection onto (eavail, W) with the dense
    index np.ravel_multi_index((i_eavail, i_W)) (s5c_coverage.py:39-46). Here: for every EW<k>, the fine cells the row
    integrates are exactly the fine cells with eavail bin k // n_W and W bin k % n_W."""
    sys.path.insert(0, str(repo / "nd-unfolding"))
    import s5c_coverage as sc  # noqa: E402
    import project_cov_nd as pc  # noqa: E402
    assert list(pc.AXIS_EDGES["eavail"]) == list(eavail_edges), "E_avail edges differ from project_cov_nd.AXIS_EDGES"
    assert list(pc.AXIS_EDGES["W"]) == list(w_edges), "W edges differ from project_cov_nd.AXIS_EDGES"
    n_w = len(w_edges) - 1
    U, unames = sc.reported_functionals(contract(repo))
    assert unames == names
    shape = tuple(len(pc.AXIS_EDGES[a]) - 1 for a in AXES)
    fidx = np.unravel_index(np.arange(int(np.prod(shape))), shape)
    ew = [n for n in names if n.startswith("EW") and n != "EW_all_ones"]
    assert ew == [f"EW{k}" for k in range((len(eavail_edges) - 1) * n_w)]
    for k, n in enumerate(ew):
        support = U[unames.index(n)] != 0
        assert np.array_equal(support, (fidx[2] == k // n_w) & (fidx[4] == k % n_w)), f"{n} is not cell {divmod(k, n_w)}"
    return {"n_EW_checked": len(ew), "against": "nd-unfolding/s5c_coverage.py reported_functionals (rows EW<k>)",
            "edges": "nd-unfolding/project_cov_nd.py AXIS_EDGES eavail, W"}


def blocks(names_in_order: list) -> list:
    """Consecutive runs of J cells sharing (pt, pz) bins: [(pt bin, pz bin, first position, last position)]."""
    out = []
    for k, n in enumerate(names_in_order):
        b = decode(int(n[1:]))
        key = (b["pt"], b["pz"])
        if out and out[-1][:2] == key:
            out[-1] = (*key, out[-1][2], k)
        else:
            assert not any(o[:2] == key for o in out), "a (pt, pz) block is not contiguous"
            out.append((*key, k, k))
    return out
