#!/usr/bin/env python3
"""Independent 42x42 cutoff scan on the standard-P4 (E_avail,W) PUBLICATION projection.

WHAT THIS MEASURES, AND WHAT IT DOES NOT AUTHORIZE
--------------------------------------------------
It reads the bytes of `cov_5d_to_eavailW_publication.root` and reports the retained
rank AS A FUNCTION OF THE RELATIVE EIGENVALUE CUTOFF, plus the spectrum, the trace
and the symmetry residual. Every rank is reported WITH the cutoff that produced it;
a bare rank is not a property of this matrix (PLAN-20260918 s16.1a).

It does NOT discharge M1-M4, does not bear on cause 3, and does not make the
projection publication-ready. A spectral scan confirms a spectrum, nothing else.

WHY IT EXISTS: every prior spectral statement about the PUBLICATION product rested on
that run's own stdout agreeing with the DIAGNOSTIC product's. The diagnostic is a
DIFFERENT FILE (17,120 B, job 58510024) from the publication product (17,101 B, job
58655509). This scan is on the publication bytes, independently, from the file.
"""
import argparse, hashlib, json, sys
import numpy as np


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--product", required=True)
    ap.add_argument("--hist", default="hCov_proj_eavailW")
    ap.add_argument("--expect-sha256", required=True,
                    help="refuse unless the bytes read are these bytes")
    ap.add_argument("--out-json", required=True)
    args = ap.parse_args()

    got = sha256_file(args.product)
    if got != args.expect_sha256:
        print(f"[FAIL] digest mismatch: read {got}, expected {args.expect_sha256}")
        return 3

    import ROOT
    ROOT.gROOT.SetBatch(True)
    f = ROOT.TFile.Open(args.product)
    if not f or f.IsZombie():
        print(f"[FAIL] cannot open {args.product}")
        return 3
    h = f.Get(args.hist)
    if not h:
        print(f"[FAIL] no object {args.hist!r}; keys = "
              f"{[k.GetName() for k in f.GetListOfKeys()]}")
        return 3
    n = h.GetNbinsX()
    m = h.GetNbinsY()
    if n != m:
        print(f"[FAIL] not square: {n}x{m}")
        return 3
    C = np.empty((n, n), dtype=float)
    for i in range(n):
        for j in range(n):
            C[i, j] = h.GetBinContent(i + 1, j + 1)

    keys = sorted(k.GetName() for k in f.GetListOfKeys())
    # TParameter / TNamed provenance carried in the product itself
    prov = {}
    for name in ("sqrt_tr", "n_dst", "src_cells_dropped", "n_empty"):
        o = f.Get(name)
        if o:
            try:
                prov[name] = o.GetVal()
            except Exception:
                prov[name] = str(o.GetTitle())
    for name in ("runClass", "runClassStatus", "acceptanceQuestion"):
        o = f.Get(name)
        if o:
            prov[name] = str(o.GetTitle())

    ev = np.linalg.eigvalsh(C)          # ascending
    lam_max = float(ev[-1])
    lam_min = float(ev[0])
    sym = float(np.abs(C - C.T).max())
    tr = float(np.trace(C))

    rows = []
    for rc in (1e-1, 1e-2, 1e-3, 1e-4, 1e-6, 1e-8, 1e-10, 1e-12, 1e-14, 1e-16, 0.0):
        keep = ev > lam_max * rc
        rank = int(keep.sum())
        excluded = ev[~keep]
        largest_excl = float(excluded.max() / lam_max) if excluded.size else None
        rows.append({"rcond": rc, "rank": rank,
                     "largest_excluded_lambda_over_lambda_max": largest_excl})

    np_default_rc = n * np.finfo(float).eps
    np_rank = int(np.linalg.matrix_rank(C))

    out = {
        "what_this_is": "independent retained-rank-vs-cutoff scan on the PUBLICATION "
                        "(E_avail,W) projection, read from the product's own bytes",
        "what_it_does_not_authorize": [
            "it does not discharge M1-M4 of the 3d7465f6 adoption",
            "it does not bear on cause 3",
            "it does not make the projection publication-ready",
            "no rank here may be quoted without the cutoff that produced it",
        ],
        "product": args.product,
        "product_sha256": got,
        "hist": args.hist,
        "n": n,
        "keys_in_product": keys,
        "provenance_in_product": prov,
        "lambda_max": lam_max,
        "lambda_min": lam_min,
        "lambda_min_over_max": lam_min / lam_max if lam_max else None,
        "condition_number_abs": abs(lam_max / lam_min) if lam_min else None,
        "trace": tr,
        "sqrt_trace": float(np.sqrt(max(tr, 0.0))),
        "symmetry_max_abs_C_minus_CT": sym,
        "n_negative_eigenvalues": int((ev < 0).sum()),
        "cutoff_scan": rows,
        "numpy_matrix_rank_default": {"rcond": float(np_default_rc), "rank": np_rank},
        "eigenvalues_descending": [float(x) for x in ev[::-1]],
        "numpy_version": np.__version__,
        "root_version": str(ROOT.gROOT.GetVersion()),
    }
    with open(args.out_json, "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)

    print(f"[scan] product {args.product}")
    print(f"[scan] sha256  {got}")
    print(f"[scan] n={n}  trace={tr:.6e}  sqrt_trace={np.sqrt(max(tr,0)):.6e}")
    print(f"[scan] symmetry max|C-C^T| = {sym:.3e}")
    print(f"[scan] lambda_max={lam_max:.6e}  lambda_min={lam_min:.6e}  "
          f"ratio={lam_min/lam_max:.3e}  cond={abs(lam_max/lam_min):.3e}")
    print(f"[scan] n_negative = {int((ev<0).sum())}")
    print("")
    print("| relative cutoff `rc` | rank | largest excluded `lambda/lambda_max` |")
    print("|---|---:|---|")
    for r in rows:
        le = ("`%.2e`" % r["largest_excluded_lambda_over_lambda_max"]
              if r["largest_excluded_lambda_over_lambda_max"] is not None else "—")
        print(f"| `{r['rcond']:.0e}` | **{r['rank']}** | {le} |")
    print("")
    print(f"[scan] numpy.linalg.matrix_rank default rc = {np_default_rc:.3e} -> rank {np_rank}")
    print(f"[scan] wrote {args.out_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
