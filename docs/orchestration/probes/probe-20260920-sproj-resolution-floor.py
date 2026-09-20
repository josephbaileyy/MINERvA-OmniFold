#!/usr/bin/env python3
"""The s_proj RESOLUTION FLOOR: what the statistic returns when only the throw subset changes.

THE QUESTION. `s_proj = 6.145%` was measured between two members at DIFFERENT estimator seeds. Is
that a real seed sensitivity, or is it at or below what `s_proj` returns when nothing physical
moves at all? The 5% bound was grounded on a `~5.6%` ensemble-precision figure, so the two
possibilities are not far apart and cannot be separated by argument.

THE DESIGN. Every subset below is combined at the SAME estimator seed (1000) and the SAME draw seed
(1000) from the SAME member's slabs. **Nothing differs but which throws are in the subset.** Any
`s_proj` that comes back is therefore finite-ensemble sampling noise and nothing else.

  Q1 Q2 Q3 Q4   N = 40 throws each, disjoint  -> 6 pairs, giving SCATTER
  HA HB         N = 80 throws each, disjoint  -> 1 pair,  the primary floor

Two sizes, because a floor quoted at one `N` cannot be transported to another by assertion: if the
values scale as `1/sqrt(N)` between 40 and 80, that is measured evidence they are sampling noise and
the extrapolation to the members' `N = 160` is supported rather than assumed.

THE CONTROL THAT MAKES THE SHORTCUT LEGITIMATE. This assembles `C_Z` directly from `z_assembly`
rather than re-running `z_build` six times. That is only admissible if the two agree, so the first
thing it does is assemble the FULL 160-throw member by this path and require the result to be
**bitwise identical** to the covariance inside the `z_build` product `361090f9...`. If it is not,
the script refuses and measures nothing.

IT GRADES NOTHING. No boundary is read, no verdict is emitted, no token is produced.
"""
import json, sys
from pathlib import Path
import numpy as np

ND = Path(sys.argv[1]) / "nd-unfolding"
sys.path.insert(0, str(ND))
import p4_lib as p4                 # noqa: E402
import z_assembly as assembly       # noqa: E402
import z_build as zb                # noqa: E402
import z_contract as contract       # noqa: E402
import z_grade as zg                # noqa: E402
import z_receipt as zrec            # noqa: E402
import z_statistics as zs           # noqa: E402

DATA = Path("/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding")
MEMBER = sys.argv[2] if len(sys.argv) > 2 else "member_k000000"
SUFFIX = "" if MEMBER == "member_k000000" else "-k1200"
MEM = DATA / "mii" / MEMBER
FLOOR = Path(f"/pscratch/sd/j/josephrb/z2m-floor-20260920{SUFFIX}")
PROD = Path("/pscratch/sd/j/josephrb/z2m-products") / MEMBER
SUBSETS = ["Q1", "Q2", "Q3", "Q4", "HA", "HB"]
NTHROWS = {"Q1": 40, "Q2": 40, "Q3": 40, "Q4": 40, "HA": 80, "HB": 80}


def src(path, fmt):
    p = Path(path)
    return zb.Source({"path": str(p), "format": fmt, "sha256": zrec.sha256_file(p)}, p.parent)


def main():
    out = {"subject": "s_proj resolution floor at a FIXED estimator seed", "grades_nothing": True,
           "member": MEMBER, "member_path": str(MEM), "draw_seed": 1000,
           "estimator_seed": 1000 if MEMBER == "member_k000000" else 2200}

    with src(DATA / "products/5d/xsec_5d_MEFHC_5iter_lgbm.root", "root") as s:
        central = s.read("hXSecND_flat")
    mask = zs.support_mask(central)
    n = int(mask.sum())
    out["n_reported"] = n
    print(f"[floor] n_reported = {n}", flush=True)

    sup = MEM / "uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root"
    with src(sup, "root") as s:
        inv = sorted(k[len(zb.SUPPORT_PREFIX):] for k in s.keys()
                     if k.startswith(zb.SUPPORT_PREFIX) and k != zb.SUPPORT_PREFIX + "total")
        residual = tuple(sorted(set(inv) - set(contract.VERT_BANDS) - set(contract.LATERAL_BANDS)))
        contract.check_declared_residual(residual)
        parts = {"cov_vert_sum": zb._sum_bands(s, contract.VERT_BANDS, zb.SUPPORT_PREFIX, n),
                 "cov_residual_sum": zb._sum_bands(s, residual, zb.SUPPORT_PREFIX, n)}
    print("[floor] support bands read", flush=True)

    with src(DATA / "active_universe_5d/standard/candidate/std_final5_candidate.root", "root") as s:
        active = {b: s.read(p4.candidate_band_key(b), (n, n)) for b in contract.LATERAL_BANDS}
        total = s.read(p4.CANDIDATE_ACTIVE_TOTAL_KEY, (n, n))
    p4.check_component_sum(total, active)
    parts["cov_lateral_sum"] = sum(active.values())
    del active, total
    with src(MEM / "uq_cov_stat_5d.root", "root") as s:
        parts["cov_stat"] = s.read("hCov_stat5d_reported", (n, n))
    with src(MEM / "uq_cov_mlsplit_5d.root", "root") as s:
        parts["cov_ml"] = s.read("hCov_mlsplit5d_reported", (n, n))
    print("[floor] fixed parts read: vert, residual, lateral, stat, ML", flush=True)

    def assemble_cv(throw_root):
        with src(throw_root, "root") as s:
            raw = {"diag_c_unified_mean": s.diagonal("C_unified", n),
                   "diag_c_blocksum": s.diagonal("C_blocksum", n),
                   "joint_mean_shift": s.read("hJointMeanShift", (n,))}
        op = assembly.derive_variant_diagonals(**raw)
        g, pinned = assembly.compute_g(op["v_uni_cv"], op["v_blk"])
        return assembly.assemble(g, **parts), g, pinned

    # ---- THE CONTROL. This path must reproduce z_build exactly, or nothing below is admissible.
    full, _, _ = assemble_cv(MEM / "uq_5d/unified_throw_cov_5d.root")
    with np.load(PROD / "z-cv.npz", allow_pickle=False) as s:
        built = np.asarray(s[zg.TOTAL_KEY], float)
    identical = bool(np.array_equal(full, built))
    out["control_reproduces_z_build"] = {
        "bitwise_identical": identical,
        "product": str(PROD / "z-cv.npz"),
        "product_cov_sha256": zrec.sha256_array(built),
        "reassembled_cov_sha256": zrec.sha256_array(full),
        "max_abs_difference": float(np.abs(full - built).max()),
    }
    print(f"[floor] CONTROL: reassembled == z_build product : {identical}", flush=True)
    contract.require(identical,
                     "the diagnostic assembly path does not reproduce the z_build product "
                     "bitwise; the subset measurements below would not be comparable to the grade")
    del full, built

    U, uprov = zg.m1_functionals(mask)
    out["functionals"] = uprov
    print(f"[floor] functionals: {uprov['n_functionals']}", flush=True)

    covs, gates = {}, {}
    for name in SUBSETS:
        C, g, pinned = assemble_cv(FLOOR / "out" / name / "unified_throw_cov_5d.root")
        gates[name] = assembly.gate_symmetry_psd(C)
        covs[name] = C
        print(f"[floor] assembled {name} (N={NTHROWS[name]})  sqrt_tr={np.sqrt(np.trace(C)):.6e}",
              flush=True)
    out["per_subset"] = {k: {"n_throws": NTHROWS[k], "sqrt_tr": float(np.sqrt(np.trace(covs[k]))),
                             "symmetry_psd": gates[k]} for k in SUBSETS}

    def pair(a, b):
        d = {0: covs[a], 1: covs[b]}
        prj = zs.s_proj(d, U, baseline_key=0)          # called ONCE; it is the expensive one
        return {"pair": f"{a}|{b}", "n_throws": NTHROWS[a],
                "s_agg": zs.s_agg(d, baseline_key=0)["s_agg"],
                "s_med": zs.s_med(d, central, mask, baseline_key=0)["s_med"],
                "s_proj": prj["s_proj"],
                "s_proj_argmax_functional": prj["argmax_functional"]}

    q = ["Q1", "Q2", "Q3", "Q4"]
    out["pairs_N40"] = [pair(q[i], q[j]) for i in range(4) for j in range(i + 1, 4)]
    out["pairs_N80"] = [pair("HA", "HB")]
    for row in out["pairs_N40"] + out["pairs_N80"]:
        print(f"[floor] {row['pair']:7s} N={row['n_throws']:3d}  s_agg={row['s_agg']:.6f}  "
              f"s_med={row['s_med']:.6f}  s_proj={row['s_proj']:.6f}", flush=True)

    for key, rows in (("N40", out["pairs_N40"]), ("N80", out["pairs_N80"])):
        for st in ("s_agg", "s_med", "s_proj"):
            v = [r[st] for r in rows]
            out.setdefault("summary", {}).setdefault(key, {})[st] = {
                "n_pairs": len(v), "mean": float(np.mean(v)), "max": float(np.max(v)),
                "min": float(np.min(v)),
                "sd": float(np.std(v, ddof=1)) if len(v) > 1 else None}
    Path(FLOOR / "FLOOR.json").write_text(json.dumps(out, indent=2, sort_keys=True))
    print("[floor] wrote " + str(FLOOR / "FLOOR.json"), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
