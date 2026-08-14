"""Lane D's INDEPENDENT C_stat cross-check build (OI-121 §4.F). Authorized 2026-08-14.

METHOD DECLARED IN ADVANCE:
docs/orchestration/METHOD-DECLARATION-20260814-lane-d-cstat-crosscheck.md
committed at 68868bf, BEFORE any C_stat artifact existed on origin/main. This file implements
exactly those eight steps and nothing else. If it departs from them, the declaration wins and
the departure is a defect.

WHY THIS EXISTS. With one builder, nothing recomputes C_stat's values -- every surviving check
either tests the artifact against an external fact that is not the covariance (member digests,
edges, rank, layout fingerprint) or against the builder's own declarations. See
COMPARATOR-PREDECLARATION-20260814-cstat.md §4.F.

WHAT IT WILL AND WILL NOT BE EVIDENCE OF, fixed here so a clean agreement cannot be inflated:
  * WEAK about the kernel. Per BEN-188, `Xc.T @ Xc` and `np.einsum` agree BIT-FOR-BIT because
    both dispatch to the same BLAS. Step 4 below is the obvious construction and is very likely
    the one the other builder reached.
  * MEANINGFUL above the kernel: which 50 files were consumed, the centring, the mask, `dof`,
    the ravel order, the reduction. That is where bugs actually live -- a spec pinning a
    decision is not a builder implementing it.
  * NO evidence that the replica products are themselves correct. Both builds read the same 50
    files; `member_sha256` proves we read the same bytes, not that those bytes are right.

I DO NOT READ combine_cstat_bkgsub.py. It is committed prior art rather than the other
builder's code, so reading it breaks no constraint -- but lane B's REQUIREMENTS cites it as the
precedent for this exact construction, so if B builds on it, reading it pre-loads B's approach.
The distinction between prior art and the other implementation collapses when the second derives
from the first.
"""
import argparse
import glob
import hashlib
import json
import os
import sys

import numpy as np

REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
FAMILY = os.path.join(REPO, "nd-unfolding/pet/fullevent_cstat_n50/replicas")
PATTERN = os.path.join(FAMILY, "*/extraction/GATE5_REPLICA_XSEC.npz")
N_PT, N_PP = 15, 19
N_CELLS = N_PT * N_PP
N_REPLICAS = 50
METHOD = ("METHOD-DECLARATION-20260814-lane-d-cstat-crosscheck.md @68868bf: replica-mean "
          "centred, C = Z.T@Z/(N-1) with dof=49, C-order ravel, mask DERIVED as the union of "
          "xsec>0 rather than adopted, explicit symmetrisation with the pre-symmetrisation "
          "asymmetry recorded, full grid plus the reduction shipped together.")


def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    # --- step 1: enumerate, digest, and REFUSE anything that is not exactly 50 --------------
    files = sorted(glob.glob(PATTERN))
    print(f"[xcheck] products found: {len(files)}")
    if len(files) != N_REPLICAS:
        raise SystemExit(
            f"[xcheck] REFUSING: {len(files)} products, need exactly {N_REPLICAS}. A missing "
            f"replica invalidates the declared ensemble manifest -- 49 of 50 is not a "
            f"49-replica ensemble (PREDECLARATION-20260813 branch BLOCK, adopted verbatim).")
    digests = [sha256_file(p) for p in files]
    if len(set(digests)) != len(digests):
        raise SystemExit("[xcheck] REFUSING: duplicate member digests -- two products are the "
                         "same bytes, so the ensemble has fewer than 50 distinct draws.")

    # --- step 2: load, ravel C-order, stack -------------------------------------------------
    X = np.zeros((N_REPLICAS, N_CELLS), dtype=np.float64)
    ids = np.zeros(N_REPLICAS, dtype=np.int64)
    edges_pt = edges_pp = None
    for i, p in enumerate(files):
        with np.load(p, allow_pickle=True) as z:
            x = np.asarray(z["xsec"], dtype=np.float64)
            if x.shape != (N_PT, N_PP):
                raise SystemExit(f"[xcheck] {p}: xsec shape {x.shape}, expected {(N_PT, N_PP)}")
            X[i] = x.ravel(order="C")
            ids[i] = int(z["replica_index"]) if "replica_index" in z.files else -1
            if edges_pt is None:
                edges_pt = np.asarray(z["edges_pt"], float)
                edges_pp = np.asarray(z["edges_pparallel"], float)
            elif not (np.array_equal(edges_pt, np.asarray(z["edges_pt"], float))
                      and np.array_equal(edges_pp, np.asarray(z["edges_pparallel"], float))):
                raise SystemExit(f"[xcheck] {p}: edges differ from the first member")
    if len(set(ids.tolist())) != N_REPLICAS:
        raise SystemExit(f"[xcheck] REFUSING: replica_index not distinct across the 50 members "
                         f"({len(set(ids.tolist()))} distinct)")
    print(f"[xcheck] stacked {X.shape}, replica_index {ids.min()}..{ids.max()}")

    # --- steps 3-4: replica-mean centring, dof = N-1 ----------------------------------------
    mean = X.mean(axis=0)
    Z = X - mean
    dof = N_REPLICAS - 1
    C = (Z.T @ Z) / dof

    # --- step 5: symmetrise EXPLICITLY and record what was symmetrised away -----------------
    # A value far above roundoff here is a real bug that symmetrising would hide, which is why
    # the number is shipped rather than merely used. It is also what makes the comparator's
    # symmetry check non-vacuous: post-symmetrisation both artifacts are symmetric by
    # construction, so the only informative quantity is this one.
    asym = float(np.max(np.abs(C - C.T)))
    dg = np.sqrt(np.clip(np.diag(C), 0, None))
    scale = float(np.max(np.outer(dg, dg))) if dg.size else 0.0
    asym_scaled = asym / scale if scale > 0 else asym
    C = (C + C.T) / 2.0
    print(f"[xcheck] pre-symmetrisation |C-C^T|max = {asym:.6e}  (scaled {asym_scaled:.3e})")

    # --- step 6: DERIVE the mask; do not adopt one ------------------------------------------
    # C_stat is a mask CONSUMER in production and that is correct there. But a cross-check that
    # adopts the mask under test cannot detect a mask error, so this derives its own and any
    # difference becomes a finding instead of something the method hides.
    mask = (X > 0).any(axis=0)
    n_rep = int(mask.sum())
    print(f"[xcheck] derived reported mask: {n_rep}/{N_CELLS} "
          f"(union of xsec>0 over the {N_REPLICAS} members)")

    ev = np.linalg.eigvalsh(C)
    lmax = float(np.max(np.abs(ev)))
    rank = int((np.abs(ev) >= 1e-10 * lmax).sum()) if lmax > 0 else 0
    print(f"[xcheck] rank at 1e-10*lambda_max = {rank}  (ceiling {dof}/{N_REPLICAS})")

    # --- step 7: emit the full contract, BOTH forms ------------------------------------------
    sys.path.insert(0, os.path.join(REPO, "nd-unfolding"))
    import fps_provenance as FP
    idx = np.flatnonzero(mask)
    payload = {
        "C_stat": C,
        "C_stat_reduced": C[np.ix_(idx, idx)],
        "reported_mask": mask,
        "cv": mean,
        "edges_pt": edges_pt, "edges_pparallel": edges_pp,
        "layout_fingerprint": FP.layout_fingerprint(edges_pt, edges_pp),
        "central_sha256": hashlib.sha256(np.ascontiguousarray(mean).tobytes()).hexdigest(),
        "n_replicas": N_REPLICAS,
        "replica_ids": ids,
        "dof": dof,
        "rank_at_1em10_lambda_max": rank,
        "ravel_order": "C",
        "centering": "replica_mean",
        "units": "(cm^2/nucleon/GeV^2)^2",
        "member_sha256": np.array(digests),
        "asymmetry_before_symmetrisation": asym,
        "method_declaration": METHOD,
        "built_by": "lane D independent cross-check, OI-121 section 4.F",
    }
    np.savez_compressed(a.out, **payload)
    print(f"[xcheck] wrote {a.out} ({os.path.getsize(a.out)} bytes)")

    summary = {
        "what": "lane D independent C_stat cross-check artifact",
        "method_declaration": METHOD,
        "n_replicas": N_REPLICAS, "dof": dof,
        "n_reported_derived": n_rep, "rank_at_1em10_lambda_max": rank,
        "asymmetry_before_symmetrisation": asym,
        "asymmetry_scaled": asym_scaled,
        "trace": float(np.trace(C)), "sqrt_trace": float(np.sqrt(max(np.trace(C), 0.0))),
        "layout_fingerprint": payload["layout_fingerprint"],
        "member_sha256": digests,
        "member_paths": files,
        "artifact_sha256": sha256_file(a.out),
        "CLAIM_BOUND": ("If this agrees with the other build, the honest claim is 'two "
                        "independent assemblies of the same 50 products agree above the "
                        "kernel' -- NOT 'C_stat is verified'. Per BEN-188, agreement on the "
                        "covariance kernel is evidence about BLAS."),
        "DISAGREEMENT_PRESUMPTION": ("If the two disagree, the presumption is NOT that the "
                                     "other build is wrong. Lane B owns the P5B assembly "
                                     "conventions; this is a verifier writing assembly code "
                                     "against a spec it did not author. First hypothesis "
                                     "tested is that THIS one is defective."),
    }
    print("\n<<<RECEIPT_JSON>>>")
    print(json.dumps(summary, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
