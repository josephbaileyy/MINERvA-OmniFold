#!/usr/bin/env python3
"""P7 covariance marginalization: project an N-D cross-section covariance onto a
lower-dimensional subset of axes as C_low = M C_high M^T (uq_math.project_covariance).

The stored cross section is a DIFFERENTIAL DENSITY per unit bin-volume
(xsec_nd.extract_cross_section_nd divides by prod_a dx_a). Marginalizing over an
axis is therefore a WIDTH-WEIGHTED sum: M's nonzero entries are the product of the
bin widths of the DROPPED axes, grouped into the destination (kept-axis) bin.
Unit-weight M would be WRONG for this convention. This mirrors the validated maps in
eavail_generator_significance.py:83-89 (4D->E_avail) and eavailW_covariance.py:290-304
(5D->(E_avail,W)); the only generalization here is arbitrary keep-axis subsets.

Axis order is the C-order ravel convention (pt, pz, eavail, q3[, W]). The reported
mask is CV>0. When --dst-cv is given, the destination reported mask/shape is taken
from that frozen lower-D central product (so masks match a real result); otherwise
the destination reports every bin that receives a reported source cell.

  # 5D adopted covariance -> exact 4D marginal (drop W), reporting onto the 4D CV mask
  python project_cov_nd.py \
      --src-cov uq_5d/.../uq_universe_5d_covariance_combined_bkgaware_uthrow.root \
      --src-hist hCov_combined5d_total_uthrow \
      --src-cv products/5d/xsec_5d_MEFHC_5iter_lgbm.root --src-axes pt,pz,eavail,q3,W \
      --keep-axes pt,pz,eavail,q3 \
      --dst-cv products/4d/xsec_4d_MEFHC_5iter_lgbm.root \
      --out uq_4d/corrected/projections_candidate/cov_5d_to_4d_marginal.root
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

# OI-136: root derived from __file__, never the hardcoded cluster root
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from uq_math import project_covariance              # noqa: E402  (ROOT-free)

# Canonical analysis bin edges (C-order axes pt,pz,eavail,q3,W). Hardcoded so the
# M-construction stays ROOT-free/testable; _verify_canonical_edges() below fails
# closed if these ever drift from unfold_2d/unfold_nd (which import ROOT).
AXIS_EDGES = {
    "pt": np.array([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
                    0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50], float),
    "pz": np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
                    6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0], float),
    "eavail": np.array([0.0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0], float),
    "q3": np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.2, 2.0, 100.0], float),
    "W": np.array([0.0, 1.1, 1.4, 1.8, 2.2, 3.0, 100.0], float),
}


def _verify_canonical_edges():
    """Fail closed if the hardcoded edges drift from the canonical modules."""
    import unfold_2d_omnifold_unbinned as u2d       # imports ROOT
    import unfold_nd_omnifold_unbinned as und
    ref = {"pt": u2d.PT_EDGES, "pz": u2d.PZ_EDGES,
           "eavail": und.EXTRA_AXES["eavail"]["edges"],
           "q3": und.EXTRA_AXES["q3"]["edges"], "W": und.EXTRA_AXES["W"]["edges"]}
    for a, e in ref.items():
        if not np.allclose(np.asarray(e, float), AXIS_EDGES[a]):
            raise SystemExit(f"[FAIL] canonical edge drift on axis {a}: "
                             f"{np.asarray(e, float)} != {AXIS_EDGES[a]}")


def _th1(h):
    return np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())])


def _th2(h):
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    b = np.frombuffer(h.GetArray(), dtype=np.float64,
                      count=(nx + 2) * (ny + 2)).reshape(ny + 2, nx + 2)
    return b[1:ny + 1, 1:nx + 1].T.copy()


def _sha256_file(path):
    """Digest of the bytes actually on disk. Must be called AFTER the writer closes the file."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_int64(a):
    """Digest of an integer index vector, in a byte layout that does not depend on the caller."""
    return hashlib.sha256(np.ascontiguousarray(np.asarray(a, np.int64)).tobytes()).hexdigest()


def build_projection(src_axes, keep_axes, src_report, src_shape, dst_shape, dst_index_of):
    """M (n_dst x n_src_reported): entries = product of dropped-axis bin widths,
    grouped into the destination flat index. dst_index_of maps a dense dst flat index
    to the destination reported row (or -1 to drop)."""
    drop_axes = [a for a in src_axes if a not in keep_axes]
    keep_pos = [src_axes.index(a) for a in keep_axes]
    idx = np.unravel_index(src_report, src_shape)          # C-order, tuple of arrays
    # width weight = product over dropped axes of that axis's bin width
    w = np.ones(src_report.size)
    for a in drop_axes:
        pos = src_axes.index(a)
        w = w * np.diff(AXIS_EDGES[a])[idx[pos]]
    # destination dense flat index from the kept-axis coordinates
    dst_coords = tuple(idx[p] for p in keep_pos)
    dst_dense = np.ravel_multi_index(dst_coords, dst_shape)
    dst_row = dst_index_of[dst_dense]                       # reported row or -1
    n_dst = int((dst_index_of >= 0).sum())
    M = np.zeros((n_dst, src_report.size))
    keep = dst_row >= 0
    M[dst_row[keep], np.arange(src_report.size)[keep]] = w[keep]
    dropped = int((~keep).sum())
    return M, dropped


def main():
    import ROOT
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src-cov", required=True)
    ap.add_argument("--src-hist", required=True)
    ap.add_argument("--src-cv", required=True, help="source CV product (hXSecND_flat) for mask+shape")
    ap.add_argument("--src-axes", required=True, help="comma list, C-order, e.g. pt,pz,eavail,q3,W")
    ap.add_argument("--keep-axes", required=True, help="comma list subset to keep")
    ap.add_argument("--dst-cv", default=None,
                    help="frozen lower-D CV product; its CV>0 mask defines the destination "
                         "reported bins. If omitted, report every bin that receives a source cell.")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    _verify_canonical_edges()

    src_axes = args.src_axes.split(",")
    keep_axes = args.keep_axes.split(",")
    if not set(keep_axes).issubset(set(src_axes)):
        raise SystemExit(f"[FAIL] keep-axes {keep_axes} not a subset of src-axes {src_axes}")
    if list(keep_axes) != [a for a in src_axes if a in keep_axes]:
        raise SystemExit("[FAIL] keep-axes must preserve the source C-order")
    for a in src_axes:
        if a not in AXIS_EDGES:
            raise SystemExit(f"[FAIL] unknown axis {a}")

    src_shape = tuple(len(AXIS_EDGES[a]) - 1 for a in src_axes)
    dst_shape = tuple(len(AXIS_EDGES[a]) - 1 for a in keep_axes)

    fcv = ROOT.TFile.Open(args.src_cv)
    xsrc = _th1(fcv.Get("hXSecND_flat")); fcv.Close()
    if xsrc.size != int(np.prod(src_shape)):
        raise SystemExit(f"[FAIL] src CV size {xsrc.size} != prod(src_shape) {np.prod(src_shape)}")
    src_report = np.where(xsrc > 0)[0]

    fc = ROOT.TFile.Open(args.src_cov)
    C = _th2(fc.Get(args.src_hist)); fc.Close()
    if C.shape != (src_report.size, src_report.size):
        raise SystemExit(f"[FAIL] src cov {C.shape} != reported mask {(src_report.size,)*2}")

    # destination reported mask / index map
    n_dense = int(np.prod(dst_shape))
    dst_index_of = -np.ones(n_dense, dtype=int)
    if args.dst_cv:
        fd = ROOT.TFile.Open(args.dst_cv)
        xdst = _th1(fd.Get("hXSecND_flat")); fd.Close()
        if xdst.size != n_dense:
            raise SystemExit(f"[FAIL] dst CV size {xdst.size} != prod(dst_shape) {n_dense}")
        dst_report = np.where(xdst > 0)[0]
        dst_index_of[dst_report] = np.arange(dst_report.size)
        x_dst_cv = xdst[dst_report]
        dst_rows_dense = dst_report          # row r of C_low is destination dense index [r]
        dst_mask_basis = "destination CV > 0 (--dst-cv supplied)"
    else:
        # provisional: fill after we know which dense bins receive a source cell
        idx = np.unravel_index(src_report, src_shape)
        keep_pos = [src_axes.index(a) for a in keep_axes]
        dst_dense_hit = np.unique(np.ravel_multi_index(tuple(idx[p] for p in keep_pos), dst_shape))
        dst_index_of[dst_dense_hit] = np.arange(dst_dense_hit.size)
        x_dst_cv = None
        dst_rows_dense = dst_dense_hit
        dst_mask_basis = "dense destination bins receiving >= 1 source cell (no --dst-cv)"

    M, dropped = build_projection(src_axes, keep_axes, src_report, src_shape,
                                  dst_shape, dst_index_of)
    n_dst = M.shape[0]
    C_low = project_covariance(C, M)
    C_low = 0.5 * (C_low + C_low.T)

    # --- CV reproduction: y = M x_src should match the frozen dst CV (density) ---
    y = M @ xsrc[src_report]
    print(f"[proj] {src_axes} -> keep {keep_axes}")
    print(f"[proj] src reported = {src_report.size}  dst reported = {n_dst}  "
          f"src cells dropped (dst bin not reported) = {dropped}")
    if x_dst_cv is not None:
        # count dst-reported bins that received zero source cells
        received = np.asarray(M != 0).any(axis=1)
        n_empty = int((~received).sum())
        with np.errstate(divide="ignore", invalid="ignore"):
            rel = np.where(x_dst_cv > 0, np.abs(y - x_dst_cv) / x_dst_cv, 0.0)
        print(f"[proj] dst-reported bins receiving NO source cell = {n_empty}")
        print(f"[proj] CV reproduction M x_src vs frozen dst CV: "
              f"max|rel|={rel.max():.3e} median={np.median(rel):.3e} "
              f"(expected ~<=3% -- independent lower-D central vs marginal)")

    ev = np.linalg.eigvalsh(C_low)
    sym = float(np.abs(C_low - C_low.T).max())
    rc = 1e-12
    rank = int((ev > ev.max() * rc).sum()) if ev.size else 0
    print(f"[proj] C_low {C_low.shape}  sqrt-tr={np.sqrt(max(np.trace(C_low),0)):.4e}")
    print(f"[proj] symmetry max|C-C^T|={sym:.2e}  min-eig={ev[0]:.3e}  "
          f"most-neg/max={ev[0]/ev[-1]:.2e}  rank~{rank}/{n_dst}")
    psd_ok = ev[0] >= -1e-10 * ev[-1]
    print(f"[proj] PSD (to machine tol): {'OK' if psd_ok else 'FAIL'}")

    # `n_empty` is RECORDED and WARNED, not raised. Declaring it a pass condition is a criterion
    # change and belongs to the criteria owner plus Joseph, not to this writer -- see
    # PLAN-20260918 D-series. A writer that invented the gate would be setting a boundary.
    n_empty_recorded = (int((~np.asarray(M != 0).any(axis=1)).sum()))
    if n_empty_recorded:
        print(f"[proj] WARNING: {n_empty_recorded} destination row(s) receive NO source cell; "
              f"their projected variance is ZERO, so any correlation-based criterion is UNDEFINED "
              f"on them. Recorded as `n_empty`; this writer does not gate on it.")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    fo = ROOT.TFile.Open(args.out, "RECREATE")
    hn = "_".join(keep_axes)
    h = ROOT.TH2D(f"hCov_proj_{hn}", f"projected cov ({'->'.join([''.join(src_axes), hn])})",
                  n_dst, 0, n_dst, n_dst, 0, n_dst)
    for i in range(n_dst):
        for j in range(n_dst):
            h.SetBinContent(i + 1, j + 1, float(C_low[i, j]))
    h.Write()
    hy = ROOT.TH1D("hCV_marginal", "M x_src (marginalized CV density)", n_dst, 0, n_dst)
    for i in range(n_dst):
        hy.SetBinContent(i + 1, float(y[i]))
    hy.Write()
    # ROW LABELS. Added 2026-09-18 (OI-129 family). Without this the rows of a projected covariance
    # cannot be bound to physical bins at all, and `p4_project_4d.py` already carries the same array
    # for the stated reason that both product-audit legs could otherwise test row alignment only
    # INDIRECTLY. It travels IN the product, not only in the sidecar, so a lost sidecar does not
    # lose the binding -- the same argument `p4_project_4d.py` makes for its non-adoptable marker.
    hidx = ROOT.TH1D("hRowIndex", "row r of the covariance is destination dense grid index [r]",
                     n_dst, 0, n_dst)
    for _i, _g in enumerate(dst_rows_dense):
        hidx.SetBinContent(_i + 1, float(_g))
    hidx.Write()
    ROOT.TParameter("double")("sqrt_tr", float(np.sqrt(max(np.trace(C_low), 0)))).Write()
    ROOT.TParameter("int")("n_dst", n_dst).Write()
    ROOT.TParameter("int")("src_cells_dropped", dropped).Write()
    ROOT.TParameter("int")("n_empty", n_empty_recorded).Write()
    fo.Close()

    # DIGESTS, all computed AFTER the close, and the row index is READ BACK OUT of the stored object
    # rather than re-hashed from the in-memory array. Two digests of one array are not two digests --
    # that is precisely OI-129's residual, recorded at
    # docs/orchestration/state/RECEIPT-20260816-hrowindex4d-readback.json.
    fchk = ROOT.TFile.Open(args.out)
    _stored = _th1(fchk.Get("hRowIndex")).astype(np.int64)
    fchk.Close()
    if not np.array_equal(_stored, np.asarray(dst_rows_dense, np.int64)):
        raise SystemExit(f"[FAIL] hRowIndex read back out of {args.out} does not equal the row "
                         f"labels written ({_stored.size} vs {len(dst_rows_dense)} entries); the "
                         f"write did not land as intended and the product must not be used")
    receipt = {
        "product": os.path.abspath(args.out),
        "proj_sha256": _sha256_file(args.out),
        "src_cov_sha256": _sha256_file(args.src_cov),
        "src_cv_sha256": _sha256_file(args.src_cv),
        "dst_cv_sha256": _sha256_file(args.dst_cv) if args.dst_cv else None,
        "M_content_sha256": hashlib.sha256(np.ascontiguousarray(M, float).tobytes()).hexdigest(),
        "M_shape": list(M.shape),
        "row_index_key": "hRowIndex",
        "row_index_sha256_readback": _sha256_int64(_stored),
        "row_index_basis": (
            "row r of the covariance is destination dense grid index hRowIndex[r], on the "
            f"({','.join(keep_axes)}) grid in C order. Digest is of the array READ BACK OUT of the "
            "closed file, not of the in-memory source."),
        "dst_mask_basis": dst_mask_basis,
        "src_axes": list(src_axes), "keep_axes": list(keep_axes),
        "src_reported": int(src_report.size), "n_dst": int(n_dst),
        "src_cells_dropped": int(dropped), "n_empty": n_empty_recorded,
        "weight_basis": ("entries are the product of the DROPPED axes' bin widths, so the "
                         "destination is a DIFFERENTIAL DENSITY in the kept axes"),
        "paired_central_estimate": ("hCV_marginal = M x_src, the marginalised 5D central value. "
                                    "NOT the independently unfolded lower-D estimator."),
        "status": "CANDIDATE -- not adoptable; construction is not adoption",
    }
    with open(args.out + ".receipt.json", "w") as fh:
        json.dump(receipt, fh, indent=2, sort_keys=True)
    print(f"[proj] wrote {args.out}  (CANDIDATE -- do not quote until governing 5D cov is final)")
    print(f"[proj] receipt {args.out}.receipt.json  proj_sha256={receipt['proj_sha256'][:16]}...")
    print(f"[proj] hRowIndex readback OK: {_stored.size} labels, digest "
          f"{receipt['row_index_sha256_readback'][:16]}...")


if __name__ == "__main__":
    main()
