#!/usr/bin/env python3
"""Does the estimator seed move the CENTRAL VALUES, or only the covariance?

Everything measured so far is about the uncertainty. This asks the other half, on the same
functionals and with the same reporting shape as `s_proj`.

THE OPERANDS ARE ALREADY ON DISK AND ARE THE RIGHT ONES. Each member's throw combine computes its
OWN genuine CV execution at its OWN estimator seed and persists it; `z_build` copies both executions
into the member's null slab. So `x_cv(k=0)` and `x_cv(k=1200)` are two central values produced by
the same pipeline differing ONLY in the estimator seed. No production is needed and none is run.

⚠ NOT the products' `hXSecND_flat`. That field is the DECLARED archive central, the same file for
both members by construction, so comparing it across members would measure nothing and would look
like a null result. The distinction is the whole point of choosing this operand.

THE CONTROL IS BUILT IN. Each slab carries a SECOND execution at the SAME seed in the same run, so
the within-member movement is measurable from the same bytes and is the scale at which "no seed
change" registers. A between-member number is only meaningful beside it.

IT GRADES NOTHING.
"""
import json, sys
from pathlib import Path
import numpy as np

ND = Path(__file__).resolve().parents[3] / "nd-unfolding"
sys.path.insert(0, str(ND))
import z_grade as zg            # noqa: E402
import z_receipt as zrec        # noqa: E402

EXPECT = {"k0": "ff0d8ec06850abb94cb840eb29aa3be096624eaf0a4e99de73446ec5028bc9e3",
          "k1200": "74444bb0056f33ea5bdf2ea2010fcfa55c9c808957880c8a81949903390f06c2"}


def rel_move(a, b):
    """|b - a| / |a|, elementwise, on a strictly positive baseline."""
    a = np.asarray(a, float); b = np.asarray(b, float)
    assert np.all(a > 0), "baseline has non-positive entries"
    return np.abs(b - a) / a


def describe(v):
    return {"median": float(np.median(v)), "p90": float(np.percentile(v, 90)),
            "max": float(np.max(v)), "argmax": int(np.argmax(v))}


def main(argv):
    paths = {"k0": Path(argv[0]), "k1200": Path(argv[1])}
    out = {"subject": "does the estimator seed move the CENTRAL VALUES", "grades_nothing": True,
           "operand": "each member's own persisted CV execution (hCvExecution0), NOT the "
                      "declared archive central, which is the same file for both members"}

    slabs, digests = {}, {}
    for tag, p in paths.items():
        digests[tag] = zrec.sha256_file(p)
        assert digests[tag] == EXPECT[tag], f"{tag}: slab digest {digests[tag]} != recorded"
        slabs[tag] = zrec.load_null_operands(p)          # the production loader, declaration checked
    out["slab_digests"] = digests

    (x0, x0b, m0), (x1, x1b, m1) = slabs["k0"], slabs["k1200"]
    assert np.array_equal(m0, m1), "the two members do not share a support mask"
    mask = np.asarray(m0, bool)
    sup = np.flatnonzero(mask)
    n = int(mask.sum())
    out["n_reported"] = n

    U, uprov = zg.m1_functionals(mask)
    out["functionals"] = uprov
    n_u = U.shape[0]

    def per_functional(a, b):
        pa, pb = U @ np.asarray(a, float)[mask], U @ np.asarray(b, float)[mask]
        assert np.all(pa > 0), "a projected baseline is non-positive"
        return np.abs(pb - pa) / pa

    def block(a, b, label):
        pf = per_functional(a, b)
        pb_ = rel_move(np.asarray(a, float)[mask], np.asarray(b, float)[mask])
        d = describe(pb_)
        return {"label": label,
                "per_functional": {"max": float(pf.max()), "argmax": int(np.argmax(pf)),
                                   "median": float(np.median(pf)),
                                   "all_ones_index": n_u - 1,
                                   "all_ones": float(pf[-1]),
                                   "functional_2": float(pf[2]),
                                   "values": [float(v) for v in pf]},
                "per_bin_on_support": {**d, "argmax_grid_index": int(sup[d["argmax"]])}}

    out["between_members_SEED_CHANGED"] = block(x0, x1, "x_cv(k=0) vs x_cv(k=1200)")
    out["control_within_k0_SAME_SEED"] = block(x0, x0b, "x_cv vs x_cv2, k=0, same run same seed")
    out["control_within_k1200_SAME_SEED"] = block(x1, x1b, "x_cv vs x_cv2, k=1200, same run same seed")

    b = out["between_members_SEED_CHANGED"]
    print(f"n_reported = {n};  functionals = {n_u} (all-ones is index {n_u-1})")
    print("\nBETWEEN MEMBERS -- estimator seed 1000 vs 2200, same throws pipeline")
    print(f"  per-functional  max {b['per_functional']['max']:.6e} at index "
          f"{b['per_functional']['argmax']}   median {b['per_functional']['median']:.6e}")
    print(f"  functional 2 (the s_proj offender) {b['per_functional']['functional_2']:.6e}")
    print(f"  all-ones (total rate)              {b['per_functional']['all_ones']:.6e}")
    pbn = b["per_bin_on_support"]
    print(f"  per-bin         median {pbn['median']:.6e}  p90 {pbn['p90']:.6e}  "
          f"max {pbn['max']:.6e} at grid {pbn['argmax_grid_index']}")
    for key in ("control_within_k0_SAME_SEED", "control_within_k1200_SAME_SEED"):
        c = out[key]
        print(f"\nCONTROL {c['label']}")
        print(f"  per-functional  max {c['per_functional']['max']:.6e}")
        print(f"  per-bin         max {c['per_bin_on_support']['max']:.6e}")
    print(f"\nratio between/within (per-functional max): "
          f"{b['per_functional']['max'] / max(out['control_within_k0_SAME_SEED']['per_functional']['max'], 1e-300):.3e}")
    if len(argv) > 2:
        Path(argv[2]).write_text(json.dumps(out, indent=2, sort_keys=True))
        print("wrote " + argv[2])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
