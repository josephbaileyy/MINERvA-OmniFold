"""Element-wise comparison: lane D's cross-check vs lane B's C_stat.

KEY NAMES DIFFER BETWEEN THE TWO ARTIFACTS AND THE NAIVE MATCH THROWS. Lane D ships
`C_stat` (285x285) and `C_stat_reduced` (262x262); lane B ships `C_full` (285x285) and
`C` (262x262). So a comparison that pairs by key name compares D's `C` -- which does not
exist -- or, worse, pairs a 262 against a 285 and raises on shape. The pairing below is
explicit for that reason:

    D["C_stat"]          <->  B["C_full"]       (285, 285)
    D["C_stat_reduced"]  <->  B["C"]            (262, 262)

The mediator hit this on an independent re-run before it was written down. It is here so
the next person does not.

Tolerance is the PREDECLARED one from COMPARATOR-PREDECLARATION-20260814-cstat.md sec 1:
absolute 1e-12 on the CORRELATION matrix (not relative on the covariance -- an off-diagonal's
relative error scales as n*eps/|rho| and diverges as a pair decorrelates), and 1e-12 relative on
the diagonal. Written before either artifact existed; not adjusted now.
"""
import json
import pathlib

import numpy as np

R = pathlib.Path("/Users/josephbailey/local-research/MINERvA-OmniFold/.claude/worktrees/lane-d")
TOL = 1e-12

D = np.load(R / "docs/orchestration/state/laned-cstat-crosscheck/LANED_CSTAT_CROSSCHECK.npz",
            allow_pickle=False)
B = np.load(R / "docs/orchestration/state/gate5-cstat-n50/GATE5_CSTAT_N50.npz",
            allow_pickle=False)

out = {}


def sc(x):
    return x.item() if getattr(x, "shape", None) == () else x


print("=== metadata (above the kernel -- where the bugs actually are) ===")
meta = [
    ("dof", sc(D["dof"]), sc(B["dof"])),
    ("centering", str(sc(D["centering"])), str(sc(B["centering"]))),
    ("ravel_order", str(sc(D["ravel_order"])), str(sc(B["ravel_order"]))),
    ("layout_fingerprint", str(sc(D["layout_fingerprint"])), str(sc(B["layout_fingerprint"]))),
    ("n_replicas / n_members", int(sc(D["n_replicas"])), int(sc(B["n_members"]))),
    ("asym_before_symm", float(sc(D["asymmetry_before_symmetrisation"])),
     float(sc(B["asymmetry_before_symmetrisation"]))),
]
for name, d, b in meta:
    ok = (d == b)
    print(f"  {name:24s} D={str(d)[:34]:36s} B={str(b)[:34]:36s} {'OK' if ok else '*** DIFFER ***'}")
    out[name] = {"D": d, "B": b, "equal": bool(ok)}

# --- the 50 inputs: did we read the same bytes? ------------------------------------------
dm = sorted(str(x) for x in np.asarray(D["member_sha256"]).ravel())
bm = sorted(str(x) for x in np.asarray(B["member_xsec_sha256"]).ravel())
same_members = dm == bm
print(f"\n  member digests           {len(dm)} vs {len(bm)}, identical set: {same_members}")
out["member_digests_identical"] = bool(same_members)
di = sorted(int(x) for x in np.asarray(D["replica_ids"]).ravel())
bi = sorted(int(x) for x in np.asarray(B["replica_index"]).ravel())
print(f"  replica ids identical    {di == bi}")
out["replica_ids_identical"] = bool(di == bi)

# --- mask --------------------------------------------------------------------------------
dmask = np.asarray(D["reported_mask"], bool).ravel()
bmask = np.asarray(B["reported_mask"], bool).ravel()
mask_same = np.array_equal(dmask, bmask)
print(f"\n  reported_mask            D {int(dmask.sum())}/285  B {int(bmask.sum())}/285  "
      f"bit-identical: {mask_same}")
out["mask_bit_identical"] = bool(mask_same)
out["mask_counts"] = [int(dmask.sum()), int(bmask.sum())]
if not mask_same:
    diff = np.flatnonzero(dmask != bmask)
    out["mask_differing_cells"] = [[int(c) // 19, int(c) % 19] for c in diff]
    print(f"    differing cells: {out['mask_differing_cells']}")

# --- B carries knobs I do not; check they are no-ops ---------------------------------------
for k in ("width_weighting_applied", "normalization", "rank_treatment", "reduction_is_exact"):
    if k in B.files:
        print(f"  B-only: {k:26s} = {sc(B[k])}")
        out[f"B_only_{k}"] = str(sc(B[k]))


def compare(tag, a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != b.shape:
        print(f"\n  {tag}: SHAPE MISMATCH {a.shape} vs {b.shape}")
        return {"shape_mismatch": [list(a.shape), list(b.shape)]}
    d = np.abs(a - b)
    wa = np.unravel_index(int(np.argmax(d)), d.shape)
    dg = np.clip(np.diag(a), 0, None)
    scale = np.sqrt(np.outer(dg, dg))
    live = scale > 0
    cs = np.zeros_like(d)
    np.divide(d, scale, out=cs, where=live)
    wc = np.unravel_index(int(np.argmax(cs)), cs.shape)
    di_ = np.abs(np.diag(a) - np.diag(b))
    dn = np.maximum(np.abs(np.diag(a)), np.abs(np.diag(b)))
    dr = np.zeros_like(di_)
    np.divide(di_, dn, out=dr, where=dn > 0)
    r = {"shape": list(a.shape),
         "bit_identical": bool(np.array_equal(a, b)),
         "worst_abs": float(d[wa]), "worst_abs_at": [int(wa[0]), int(wa[1])],
         "worst_corr_scaled": float(cs[wc]), "worst_corr_at": [int(wc[0]), int(wc[1])],
         "worst_diag_rel": float(dr.max()) if dr.size else 0.0,
         "within_tol": bool(float(cs[wc]) <= TOL and float(dr.max() if dr.size else 0) <= TOL)}
    print(f"\n  {tag}  {a.shape}")
    print(f"    bit-identical      : {r['bit_identical']}")
    print(f"    worst |A-B|        : {r['worst_abs']:.6e}  at {r['worst_abs_at']}")
    print(f"    worst corr-scaled  : {r['worst_corr_scaled']:.6e}  (tol {TOL:.0e})")
    print(f"    worst diag rel     : {r['worst_diag_rel']:.6e}  (tol {TOL:.0e})")
    print(f"    WITHIN TOLERANCE   : {r['within_tol']}")
    return r


print("\n=== element-wise ===")
out["full_grid"] = compare("C_stat (285x285) vs C_full", D["C_stat"], B["C_full"])
out["reduced"] = compare("C_stat_reduced (262x262) vs C", D["C_stat_reduced"], B["C"])

for t in ("full_grid", "reduced"):
    a = out[t]
    print(f"\n  trace check {t}: ", end="")
    print("n/a" if "shape_mismatch" in a else f"within_tol={a['within_tol']}")

out["VERDICT"] = ("AGREE" if all(out[t].get("within_tol") for t in ("full_grid", "reduced"))
                  and mask_same and same_members else "DISAGREE")
out["tolerance"] = {"corr_abs": TOL, "diag_rel": TOL,
                    "source": "COMPARATOR-PREDECLARATION-20260814-cstat.md sec 1, unchanged"}
print(f"\n=== VERDICT: {out['VERDICT']} ===")
print("\n<<<RECEIPT_JSON>>>")
print(json.dumps(out, indent=1, sort_keys=True, default=str))
