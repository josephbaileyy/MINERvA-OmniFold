#!/usr/bin/env python3
"""Build an ND covariance (reported bins = CV>0) from a glob of xsec_flat npz replicas.
Reported mask from the 4D CV product (hXSecND_flat). Writes hCov_<tag>_reported.
  python combine_cov_nd.py --glob 'seedscan_split_4d/res_*.npz' --cv products/4d/xsec_4d_MEFHC_5iter_lgbm.root --tag ml4d --out uq_cov_ml_4d.root
"""
import argparse, glob, hashlib, json, os, numpy as np, ROOT
from replica_manifest import load_replica_manifest

# The nine config-fingerprint fields of `docs/ESTIMATOR_REGISTRY.md:17-22`. That convention says
# "every covariance component must carry the identical estimator fingerprint as its central product
# (reject on mismatch)" -- but this writer stored ONE TH2D and nothing else, so for the scalar stat
# and ML components the rule was UNEXECUTABLE against the payload: five of the nine fields were not
# merely mismatched, they were absent. A reject-on-mismatch rule cannot run without operands.
# That is a WRITER gap, not a verification gap, and this closes it.
#
# Five fields are properties of the UPSTREAM unfolding and cannot be derived here, so they are
# supplied on the command line. When one is not supplied the artifact records the literal
# "UNDECLARED" with the reason -- deliberately NOT a missing key. A missing key reads as "not
# checked"; an explicit UNDECLARED reads as "the writer was never told", and those are different
# findings. Same distinction the campaign draws between a non-check and a failed check.
_SUPPLIED = ("estimator_id", "backend_version", "feature_schema", "preprocessing",
             "iters", "estimator_seed", "train_frac", "input_bank")
_UNDECLARED = "UNDECLARED"


def _sha256_file(path, _bufsz=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(_bufsz), b""):
            h.update(chunk)
    return h.hexdigest()
ROOT.gROOT.SetBatch(True)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--glob",required=True); ap.add_argument("--cv",required=True)
    ap.add_argument("--tag",required=True); ap.add_argument("--out",required=True)
    ap.add_argument("--expected-ids", required=True,
                    help="required inclusive replica id range LO-HI, e.g. 1-100")
    for _f in _SUPPLIED:
        ap.add_argument(f"--{_f.replace('_', '-')}", default=None,
                        help=f"ESTIMATOR_REGISTRY fingerprint field `{_f}`; recorded as "
                             f"{_UNDECLARED} if omitted, never silently absent")
    a=ap.parse_args()
    lo, hi = (int(v) for v in a.expected_ids.split("-", 1))
    if hi < lo: ap.error("--expected-ids must be LO-HI with HI>=LO")
    paths=sorted(glob.glob(a.glob)); X, ids=load_replica_manifest(paths, set(range(lo, hi+1)))
    f=ROOT.TFile.Open(a.cv); h=f.Get("hXSecND_flat"); cv=np.array([h.GetBinContent(i+1) for i in range(h.GetNbinsX())]); f.Close()
    rep=cv>0; Xr=X[:,rep]; cvr=cv[rep]; Z=Xr-Xr.mean(0); C=(Z.T@Z)/(Xr.shape[0]-1)
    diag=np.sqrt(np.maximum(np.diag(C),0)); rel=np.where(cvr>0,diag/cvr,0)
    print(f"[{a.tag}] {Xr.shape[0]} replicas, reported {int(rep.sum())} bins, sqrt-trace={np.sqrt(max(C.trace(),0)):.3e} median rel={100*np.median(rel):.3f}%")
    rf=ROOT.TFile.Open(a.out,"RECREATE"); n=C.shape[0]; hh=ROOT.TH2D(f"hCov_{a.tag}_reported",a.tag,n,0,n,n,0,n)
    for i in range(n):
        for j in range(n): hh.SetBinContent(i+1,j+1,float(C[i,j]))
    hh.Write()

    # ROW LABELS, so a row of this covariance can be bound to a physical bin without re-deriving
    # the mask from a CV product that may since have moved.
    rows = np.flatnonzero(rep).astype(np.int64)
    hri = ROOT.TH1D("hRowIndex", "row r is dense grid index hRowIndex[r] (C order)", n, 0, n)
    for i, g in enumerate(rows): hri.SetBinContent(i+1, float(g))
    hri.Write()

    # THE ENSEMBLE-COUNT SCALAR. The audit records that this writer "still stores no ensemble-count
    # scalar", so a reader could not tell N from the product and the launcher range is not
    # independent readback of a particular one. N and the divisor now travel IN the artifact.
    n_members = int(Xr.shape[0])
    ROOT.TParameter("int")("n_members", n_members).Write()
    ROOT.TParameter("int")("n_reported", int(rep.sum())).Write()
    ROOT.TNamed("centering", "mean-centered over members").Write()
    ROOT.TNamed("divisor", f"N-1 = {n_members - 1} (unbiased; NOT the MAT 1/N joint-throw "
                           f"convention, which applies to a different ensemble)").Write()
    fp = {f: (getattr(a, f) if getattr(a, f) is not None else _UNDECLARED) for f in _SUPPLIED}
    for k, v in fp.items(): ROOT.TNamed(f"fingerprint_{k}", str(v)).Write()
    rf.Close()

    undeclared = sorted(k for k, v in fp.items() if v == _UNDECLARED)
    receipt = {
        "product": os.path.abspath(a.out), "tag": a.tag,
        "product_sha256": _sha256_file(a.out),
        "cv_sha256": _sha256_file(a.cv),
        "n_members": n_members, "member_ids": [int(i) for i in ids],
        "expected_ids": a.expected_ids,
        "n_reported": int(rep.sum()),
        "row_index_key": "hRowIndex",
        "row_index_sha256": hashlib.sha256(np.ascontiguousarray(rows).tobytes()).hexdigest(),
        "centering": "mean-centered over members", "divisor": "N-1",
        "replica_sha256": {os.path.basename(q): _sha256_file(q) for q in paths},
        "fingerprint": fp,
        "fingerprint_undeclared": undeclared,
        "fingerprint_basis": (
            "docs/ESTIMATOR_REGISTRY.md:17-22. Fields not supplied are recorded as UNDECLARED, "
            "not omitted, so a reject-on-mismatch consumer can distinguish 'the writer was never "
            "told' from 'not checked'."),
        "status": "CANDIDATE -- construction is not adoption",
    }
    with open(a.out + ".receipt.json", "w") as fh: json.dump(receipt, fh, indent=2, sort_keys=True)
    print(f"[wrote] {a.out}  n_members={n_members}  sha256={receipt['product_sha256'][:16]}...")
    if undeclared:
        print(f"[{a.tag}] WARNING: {len(undeclared)} of {len(_SUPPLIED)} fingerprint field(s) "
              f"UNDECLARED and recorded as such: {', '.join(undeclared)}. A reject-on-mismatch "
              f"check cannot be executed against them until they are supplied.")
if __name__=="__main__": main()
