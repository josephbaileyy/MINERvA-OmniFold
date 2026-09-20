#!/usr/bin/env python3
"""THE DIRECT COMPARISON: the seed effect and the resampling floor, at the SAME N, no extrapolation.

The floor run answered "how much does `s_proj` move when only the throw subset changes". It left one
inference to do: the members are at `N = 160` and the floor was measured at 40 and 80, so comparing
them needed a scaling law -- and the measured exponent (~1.47) is not the 0.5 that sampling noise
demands, so the extrapolation was the weakest step in the argument.

This removes that step. The twelve subset products already exist -- six throw subsets built at BOTH
estimator seeds -- so for each subset the two members can be compared to each other DIRECTLY:

    SEED EFFECT at N   :  s_proj( C_Z[k=0, S] , C_Z[k=1200, S] )   same throws, different seed
    RESAMPLE FLOOR at N:  s_proj( C_Z[k, S_a] , C_Z[k, S_b]   )   same seed, different throws

Both at the same `N`, both from the same code. Whether the seed effect exceeds the floor is then a
comparison of two measured numbers rather than of one measured number and one extrapolated one.

CONTROL. Before any subset is touched, the full `N = 160` cross-member `s_proj` is recomputed by
this path and required to reproduce the graded `0.06145388...` exactly. If it does not, this script
is not measuring the same thing the grade measured and it refuses.

IT GRADES NOTHING.
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
OUT = Path("/pscratch/sd/j/josephrb/z2m-floor-20260920/SEED_EFFECT.json")
GRADED_S_PROJ = 0.06145388143592225
MEMBERS = {"k0": ("member_k000000", Path("/pscratch/sd/j/josephrb/z2m-floor-20260920")),
           "k1200": ("member_k001200", Path("/pscratch/sd/j/josephrb/z2m-floor-20260920-k1200"))}
SUBSETS = ["Q1", "Q2", "Q3", "Q4", "HA", "HB"]
NTHROWS = {"Q1": 40, "Q2": 40, "Q3": 40, "Q4": 40, "HA": 80, "HB": 80}


def src(path, fmt):
    p = Path(path)
    return zb.Source({"path": str(p), "format": fmt, "sha256": zrec.sha256_file(p)}, p.parent)


def load_parts(member, n, lateral_sum):
    mem = DATA / "mii" / member
    sup = mem / "uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root"
    with src(sup, "root") as s:
        inv = sorted(k[len(zb.SUPPORT_PREFIX):] for k in s.keys()
                     if k.startswith(zb.SUPPORT_PREFIX) and k != zb.SUPPORT_PREFIX + "total")
        residual = tuple(sorted(set(inv) - set(contract.VERT_BANDS) - set(contract.LATERAL_BANDS)))
        contract.check_declared_residual(residual)
        parts = {"cov_vert_sum": zb._sum_bands(s, contract.VERT_BANDS, zb.SUPPORT_PREFIX, n),
                 "cov_residual_sum": zb._sum_bands(s, residual, zb.SUPPORT_PREFIX, n)}
    parts["cov_lateral_sum"] = lateral_sum
    with src(mem / "uq_cov_stat_5d.root", "root") as s:
        parts["cov_stat"] = s.read("hCov_stat5d_reported", (n, n))
    with src(mem / "uq_cov_mlsplit_5d.root", "root") as s:
        parts["cov_ml"] = s.read("hCov_mlsplit5d_reported", (n, n))
    return parts


def assemble_cv(parts, throw_root, n):
    with src(throw_root, "root") as s:
        raw = {"diag_c_unified_mean": s.diagonal("C_unified", n),
               "diag_c_blocksum": s.diagonal("C_blocksum", n),
               "joint_mean_shift": s.read("hJointMeanShift", (n,))}
    op = assembly.derive_variant_diagonals(**raw)
    g, _ = assembly.compute_g(op["v_uni_cv"], op["v_blk"])
    return assembly.assemble(g, **parts)


def main():
    with src(DATA / "products/5d/xsec_5d_MEFHC_5iter_lgbm.root", "root") as s:
        central = s.read("hXSecND_flat")
    mask = zs.support_mask(central)
    n = int(mask.sum())
    with src(DATA / "active_universe_5d/standard/candidate/std_final5_candidate.root", "root") as s:
        active = {b: s.read(p4.candidate_band_key(b), (n, n)) for b in contract.LATERAL_BANDS}
        tot = s.read(p4.CANDIDATE_ACTIVE_TOTAL_KEY, (n, n))
    p4.check_component_sum(tot, active)
    lateral = sum(active.values())
    del active, tot
    print(f"[seed] n={n}; shared lateral sum read once", flush=True)

    parts = {tag: load_parts(m, n, lateral) for tag, (m, _) in MEMBERS.items()}
    print("[seed] both members' fixed parts loaded", flush=True)
    U, uprov = zg.m1_functionals(mask)

    out = {"subject": "seed effect vs resampling floor, at matched N", "grades_nothing": True,
           "n_reported": n, "functionals": uprov, "graded_s_proj_N160": GRADED_S_PROJ}

    # ---- CONTROL: reproduce the graded full-N cross-member s_proj exactly -------------------
    full = {t: assemble_cv(parts[t], DATA / "mii" / MEMBERS[t][0] / "uq_5d/unified_throw_cov_5d.root", n)
            for t in MEMBERS}
    got = zs.s_proj({0: full["k0"], 1: full["k1200"]}, U, baseline_key=0)["s_proj"]
    out["control_reproduces_the_grade"] = {"recomputed": got, "graded": GRADED_S_PROJ,
                                           "exact": bool(got == GRADED_S_PROJ),
                                           "abs_difference": abs(got - GRADED_S_PROJ)}
    print(f"[seed] CONTROL full-N cross-member s_proj = {got!r}  (graded {GRADED_S_PROJ!r})",
          flush=True)
    contract.require(abs(got - GRADED_S_PROJ) < 1e-12,
                     f"this path gives {got} for the full-N cross-member s_proj but the grade "
                     f"recorded {GRADED_S_PROJ}; the subset numbers would not be comparable")
    del full

    # ---- the seed effect at each N: same throws, different estimator seed -------------------
    rows = []
    for sname in SUBSETS:
        cz = {t: assemble_cv(parts[t], MEMBERS[t][1] / "out" / sname / "unified_throw_cov_5d.root", n)
              for t in MEMBERS}
        d = {0: cz["k0"], 1: cz["k1200"]}
        prj = zs.s_proj(d, U, baseline_key=0)
        rows.append({"subset": sname, "n_throws": NTHROWS[sname],
                     "s_agg": zs.s_agg(d, baseline_key=0)["s_agg"],
                     "s_med": zs.s_med(d, central, mask, baseline_key=0)["s_med"],
                     "s_proj": prj["s_proj"], "argmax_functional": prj["argmax_functional"]})
        print(f"[seed] SEED EFFECT {sname} N={NTHROWS[sname]:3d}  s_agg={rows[-1]['s_agg']:.6f}  "
              f"s_med={rows[-1]['s_med']:.6f}  s_proj={rows[-1]['s_proj']:.6f}", flush=True)
        del cz, d
    out["seed_effect_same_throws"] = rows
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True))
    print("[seed] wrote " + str(OUT), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
