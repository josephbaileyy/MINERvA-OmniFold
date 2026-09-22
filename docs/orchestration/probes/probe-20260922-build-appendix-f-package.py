#!/usr/bin/env python3
"""Assemble the Appendix F result package, by EXECUTING its own worked example.

`docs/analysis-note/app_release.tex` specifies a release package and records that it does not
exist. This builds it from the products on /pscratch and, in the same pass, RUNS the minimal
worked example the appendix specifies -- so the package is validated by the check it ships.

⚠ IT DOES NOT SHIP ANYTHING. It writes files. Uploading or sending the package anywhere is
reserved to Joseph (this session's D3).

⚠ THE 5-AXIS COVARIANCE C_Z IS NOT INCLUDED. 890,500,272 bytes cannot go in a git repository;
it is identified by digest, which is what the appendix itself specifies.
"""
import hashlib, json, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import project_cov_nd as P          # AXIS_EDGES + build_projection; ROOT stays out of import


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def sha_arr(a, dt):
    return hashlib.sha256(np.ascontiguousarray(np.asarray(a, dt)).tobytes()).hexdigest()


def main():
    src = sys.argv[1]          # z-cv.npz
    proj = sys.argv[2]         # cov_5d_to_eavailW_publication.root
    receipt = sys.argv[3]      # its receipt json
    out = sys.argv[4]          # package dir
    os.makedirs(out, exist_ok=True)
    rep = {}

    SRC_AXES = ["pt", "pz", "eavail", "q3", "W"]
    KEEP = ["eavail", "W"]
    src_shape = tuple(len(P.AXIS_EDGES[a]) - 1 for a in SRC_AXES)
    dst_shape = tuple(len(P.AXIS_EDGES[a]) - 1 for a in KEEP)

    z = np.load(src, allow_pickle=False)
    meta = json.loads(str(z["metadata_json"]))
    x = np.asarray(z["hXSecND_flat"], float).ravel()
    support = np.asarray(z["hSupportMask"]).ravel()
    pinned = np.asarray(z["hPinnedMask"]).ravel()
    row5d = np.asarray(z["hRowIndex5D"], np.int64).ravel()

    assert x.size == int(np.prod(src_shape)), (x.size, src_shape)
    src_report = np.where(x > 0)[0]
    rep["src_dense"] = int(x.size)
    rep["src_reported"] = int(src_report.size)
    rep["src_report_equals_producer_hRowIndex5D"] = bool(
        row5d.size == src_report.size and np.array_equal(row5d, src_report))

    # destination mask: receiving-cells, exactly as the publication run declared
    n_dense = int(np.prod(dst_shape))
    dst_index_of = -np.ones(n_dense, dtype=int)
    idx = np.unravel_index(src_report, src_shape)
    keep_pos = [SRC_AXES.index(a) for a in KEEP]
    dst_hit = np.unique(np.ravel_multi_index(tuple(idx[p] for p in keep_pos), dst_shape))
    dst_index_of[dst_hit] = np.arange(dst_hit.size)

    M, dropped = P.build_projection(SRC_AXES, KEEP, src_report, src_shape, dst_shape, dst_index_of)
    rep["n_dst"] = int(M.shape[0])
    rep["src_cells_dropped"] = int(dropped)
    rep["M_shape"] = list(M.shape)
    rep["M_content_sha256"] = sha_arr(M, np.float64)

    # --- worked example, executed ---
    y = M @ x[src_report]
    yC = y.reshape(dst_shape, order="C")
    yF = y.reshape(dst_shape, order="F")
    rep["y_C_vs_F_max_rel_disagreement"] = float(
        np.max(np.abs(yC - yF) / np.where(np.abs(yC) > 0, np.abs(yC), np.nan)))

    import ROOT
    ROOT.gROOT.SetBatch(True)
    f = ROOT.TFile.Open(proj)
    h = f.Get("hCov_proj_eavail_W")
    n = h.GetNbinsX()
    C_EW = np.empty((n, n))
    for i in range(n):
        for j in range(n):
            C_EW[i, j] = h.GetBinContent(i + 1, j + 1)
    hri = f.Get("hRowIndex")
    row_index = np.array([int(hri.GetBinContent(i + 1)) for i in range(hri.GetNbinsX())], np.int64)
    hcv = f.Get("hCV_marginal")
    cv_marg = np.array([hcv.GetBinContent(i + 1) for i in range(hcv.GetNbinsX())], float)
    accept_q = str(f.Get("acceptanceQuestion").GetTitle())
    run_class = str(f.Get("runClass").GetTitle())

    rep["row_index_sha256_readback"] = sha_arr(row_index, np.int64)
    rep["row_index_equals_receiving_cells"] = bool(np.array_equal(row_index, dst_hit))
    ev = np.linalg.eigvalsh(C_EW)
    rep["sqrt_trace_C_EW"] = float(np.sqrt(max(np.trace(C_EW), 0)))
    rep["symmetry_max_abs"] = float(np.abs(C_EW - C_EW.T).max())
    rep["lambda_min"] = float(ev[0]); rep["lambda_max"] = float(ev[-1])
    rep["lambda_min_over_max"] = float(ev[0] / ev[-1])
    rep["lambda_min_positive"] = bool(ev[0] > 0)
    rep["y_vs_hCV_marginal_max_abs"] = float(np.abs(y - cv_marg).max())
    # the appendix's step 4 reproduction: C_EW from M C M^T is NOT recomputed here (C_Z is 890 MB
    # and is identified by digest); what IS checked is that the shipped C_EW has the stated
    # properties and that M reproduces the receipt's own content digest.
    r = json.load(open(receipt))
    rep["M_digest_matches_receipt"] = bool(rep["M_content_sha256"] == r["M_content_sha256"])
    rep["row_index_digest_matches_receipt"] = bool(
        rep["row_index_sha256_readback"] == r["row_index_sha256_readback"])
    rep["acceptance_question_VERBATIM"] = accept_q
    rep["run_class"] = run_class

    # --- write the package ---
    # M is sparse by construction: exactly one destination per source cell.
    nz = np.nonzero(M)
    np.savez_compressed(os.path.join(out, "projection_matrix_M_eavailW.npz"),
                        rows=nz[0].astype(np.int32), cols=nz[1].astype(np.int32),
                        values=M[nz].astype(np.float64),
                        shape=np.array(M.shape, np.int64))
    np.savez_compressed(os.path.join(out, "central_values_5d.npz"),
                        hXSecND_flat_dense=x, reported_index=src_report.astype(np.int64))
    np.savez_compressed(os.path.join(out, "masks_5d.npz"),
                        support_mask=support, pinned_mask=pinned,
                        producer_row_index_5d=row5d)
    np.savez_compressed(os.path.join(out, "covariance_eavailW.npz"),
                        C_eavailW=C_EW, row_index=row_index, cv_marginal=cv_marg)
    rep["files"] = {}
    for fn in sorted(os.listdir(out)):
        if fn.endswith(".npz"):
            fp = os.path.join(out, fn)
            rep["files"][fn] = {"bytes": os.path.getsize(fp), "sha256": sha256_file(fp)}
    rep["src_cov_sha256"] = sha256_file(src)
    rep["proj_sha256"] = sha256_file(proj)
    rep["edges"] = {a: [float(v) for v in P.AXIS_EDGES[a]] for a in SRC_AXES}
    rep["src_metadata_variant"] = meta.get("variant")
    rep["src_metadata_adoptable"] = meta.get("adoptable")
    rep["src_metadata_scientific_acceptance"] = meta.get("scientific_acceptance")
    json.dump(rep, open(os.path.join(out, "_build_report.json"), "w"), indent=2, sort_keys=True)
    print(json.dumps({k: v for k, v in rep.items() if k not in ("edges", "files")},
                     indent=2, sort_keys=True))
    print("\nFILES:")
    for k, v in rep["files"].items():
        print(f"  {k:38s} {v['bytes']:>9d} B  {v['sha256'][:16]}")


if __name__ == "__main__":
    main()
