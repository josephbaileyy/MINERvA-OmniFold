#!/usr/bin/env python3
"""Per-field cross-member validity for the L2 released-lateral pair.

l2_stage6_measure.sh printed only the all-true boolean. It came out True for the CONTROL pair and
False for the PROBE pair, and the script's verdict branch does not consult it -- so the released
number was printed under a 'FAIL CONFIRMED' caption without the validity flag being read. This
reports the nine fields individually, for both pairs, so the qualification can be stated exactly.

READ-ONLY. Builds nothing, writes one JSON summary.
"""
import json, sys
import z_grade as G


def load(d):
    return G.Member(f"{d}/z-cv.npz", f"{d}/z-receipt-cv.json", "cv")


def fields(val):
    if hasattr(val, "__dataclass_fields__"):
        return {f: bool(getattr(val, f)) for f in val.__dataclass_fields__}
    return {k: bool(v) for k, v in vars(val).items()}


def main():
    m0_dir, m1_dir, l2_dir, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    base = load(m0_dir)
    res = {}
    for label, d in (("CONTROL_graded_pair", m1_dir), ("PROBE_released_laterals", l2_dir)):
        other = load(d)
        val, ev = G.cross_member_validity([base, other], [0, 1200])
        f = fields(val)
        res[label] = {"all_true": all(f.values()), "fields": f}
        print(f"\n=== {label} ===")
        for k, v in f.items():
            print(f"  {'PASS' if v else '*** FAIL ***':14s} {k}")
        # detail for whatever failed
        for k, v in f.items():
            if not v and k in ev:
                res[label].setdefault("evidence_for_failures", {})[k] = ev[k]
                print(f"\n  --- evidence: {k} ---")
                print("  " + json.dumps(ev[k], indent=2, default=str)[:2600].replace("\n", "\n  "))
    json.dump(res, open(out, "w"), indent=2, sort_keys=True, default=str)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
