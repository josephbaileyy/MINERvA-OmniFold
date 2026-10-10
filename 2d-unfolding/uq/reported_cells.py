"""Identity of the 2D (pT, p_parallel) reported cells.

A cell is one (pT bin, p_parallel bin) pair of the grid below. Its flat index
is its position in the C-order ravel of a (14, 16) array indexed [pt, pz],
which is the paper's GlobalID = (Ptbin - 1) * 16 + (P||bin - 1)
(``minerva_paper_anc/bin_mapping.txt``). A reported set is the sorted array of
the flat indices of its cells, and a covariance "over the reported bins" is
ordered by that array.

Two such covariances may be added, or embedded in the 224-cell grid, only when
their reported sets are equal. Equal counts are not enough: two sets with the
same size but one different cell misalign every element after it without
changing any shape.

Producers store the set as a TH2D named ``IDENTITY_HIST`` on this grid, with
content 1 on reported cells and 0 elsewhere. ``analyze_uq.py`` outputs written
before that object existed still carry their reported set implicitly, as
``hMean2D > 0``, which is the rule that selected them.
"""

import numpy as np

PT_EDGES = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
                     0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50])
PZ_EDGES = np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
                     6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0])
GRID_SHAPE = (len(PT_EDGES) - 1, len(PZ_EDGES) - 1)
N_CELLS = GRID_SHAPE[0] * GRID_SHAPE[1]

IDENTITY_HIST = "hReportedCells"


class CellIdentityError(ValueError):
    """Two reported-cell sets, or a grid, do not match."""


def reported_indices(mask):
    """Sorted flat indices of the True cells of a (14, 16) [pt, pz] mask."""
    mask = np.asarray(mask, dtype=bool)
    if mask.shape != GRID_SHAPE:
        raise CellIdentityError(
            f"reported mask has shape {mask.shape}, expected {GRID_SHAPE} [pt, pz]")
    return np.flatnonzero(mask.ravel(order="C"))


def _cell_list(indices, limit=8):
    cells = [f"{i}(pt{i // GRID_SHAPE[1] + 1},pz{i % GRID_SHAPE[1] + 1})"
             for i in indices[:limit]]
    more = f" and {len(indices) - limit} more" if len(indices) > limit else ""
    return (", ".join(cells) or "none") + more


def require_same_cells(a, b, a_name, b_name):
    """Raise CellIdentityError unless two reported sets are identical."""
    a = np.asarray(a, dtype=np.int64)
    b = np.asarray(b, dtype=np.int64)
    if np.array_equal(a, b):
        return
    raise CellIdentityError(
        f"reported cells differ: {a_name} has {a.size}, {b_name} has {b.size}; "
        f"only in {a_name}: {_cell_list(np.setdiff1d(a, b))}; "
        f"only in {b_name}: {_cell_list(np.setdiff1d(b, a))}")


def _axis_edges(axis):
    n = axis.GetNbins()
    return np.array([axis.GetBinLowEdge(i) for i in range(1, n + 2)])


def grid_hist_to_array(h):
    """Contents of a TH2D on the grid, after checking its exact bin edges."""
    for label, axis, edges in (("x (pT)", h.GetXaxis(), PT_EDGES),
                               ("y (p_parallel)", h.GetYaxis(), PZ_EDGES)):
        got = _axis_edges(axis)
        if got.shape != edges.shape or not np.array_equal(got, edges):
            raise CellIdentityError(
                f"{h.GetName()}: {label} edges {got.tolist()} are not the 2D grid "
                f"{edges.tolist()}")
    a = np.zeros(GRID_SHAPE)
    for ix in range(GRID_SHAPE[0]):
        for iy in range(GRID_SHAPE[1]):
            a[ix, iy] = h.GetBinContent(ix + 1, iy + 1)
    return a


def identity_hist(indices, name=IDENTITY_HIST):
    """TH2D on the grid: 1 on the given flat indices, 0 elsewhere."""
    import ROOT
    h = ROOT.TH2D(name, "Reported cells (1 = reported); flat index = C-order [pt, pz]",
                  GRID_SHAPE[0], PT_EDGES, GRID_SHAPE[1], PZ_EDGES)
    for i in np.asarray(indices, dtype=np.int64):
        h.SetBinContent(int(i) // GRID_SHAPE[1] + 1, int(i) % GRID_SHAPE[1] + 1, 1.0)
    return h


def read_cells(rf, mean_fallback=None):
    """Reported set stored in an open ROOT file, and where it came from.

    Reads ``IDENTITY_HIST`` if present. Otherwise, if ``mean_fallback`` names a
    histogram (``"hMean2D"`` for ``analyze_uq.py`` outputs), uses its cells with
    content > 0. Returns ``(None, None)`` when neither object exists.
    """
    h = rf.Get(IDENTITY_HIST)
    if h:
        a = grid_hist_to_array(h)
        if not np.all((a == 0.0) | (a == 1.0)):
            raise CellIdentityError(f"{IDENTITY_HIST} holds values other than 0 and 1")
        return reported_indices(a == 1.0), IDENTITY_HIST
    if mean_fallback:
        h = rf.Get(mean_fallback)
        if h:
            return reported_indices(grid_hist_to_array(h) > 0), f"{mean_fallback} > 0"
    return None, None
