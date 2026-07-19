#!/usr/bin/env python3
"""Login-safe unit tests for the pure classification logic of the additive
exhaustive domain validator (validate_g2_fullevent_domain.py). No ROOT needed:
the module imports ROOT only inside its ROOT-backed functions, so importing it
here is safe. Covers the 1D upstream-corruption scenario and the fail-closed vs
census split.

Run: python3 test_g2_domain_validator.py   (exit 0 = all pass)
"""
import math
import sys

import validate_g2_fullevent_domain as V

P = 0
F = []


def eq(name, got, want):
    global P
    if got == want:
        P += 1
    else:
        F.append(f"{name}: got {got!r} want {want!r}")


def main():
    # ---- is_finite / is_sentinel ----
    eq("finite_num", V.is_finite(3.5), True)
    eq("finite_nan", V.is_finite(float("nan")), False)
    eq("finite_inf", V.is_finite(float("inf")), False)
    eq("sentinel_true", V.is_sentinel(-9999.0), True)
    eq("sentinel_false", V.is_sentinel(0.734), False)
    eq("sentinel_nan_false", V.is_sentinel(float("nan")), False)

    # ---- in_domain boundaries (extended-FPS: pT<=30, p_par<=120) ----
    eq("in_domain_typical", V.in_domain(0.734, 5.0), True)
    eq("in_domain_pt_edge", V.in_domain(30.0, 120.0), True)
    eq("in_domain_pt_over", V.in_domain(30.0001, 5.0), False)
    eq("in_domain_ppar_over", V.in_domain(1.0, 120.0001), False)
    eq("in_domain_negative", V.in_domain(-0.1, 5.0), False)

    # ---- classify_scalar_pair (verdict, fatal, in_domain) ----
    eq("cls_ok", V.classify_scalar_pair(0.734, 5.0), ("ok", False, True))
    eq("cls_nan_fatal", V.classify_scalar_pair(float("nan"), 5.0), ("nonfinite", True, False))
    eq("cls_inf_fatal", V.classify_scalar_pair(1.0, float("inf")), ("nonfinite", True, False))
    # THE 1D CORRUPTION: finite but far out of domain -> censused, NOT fatal.
    eq("cls_1D_corrupt", V.classify_scalar_pair(2960428.0, 31233701.0),
       ("out_of_domain", False, False))
    # Playlist 1E data corruption is likewise finite but far outside FPS.
    eq("cls_1E_data_corrupt", V.classify_scalar_pair(239964.9294, 961714.0188),
       ("out_of_domain", False, False))
    eq("cls_negative_ood", V.classify_scalar_pair(-5.0, 5.0), ("out_of_domain", False, False))

    # ---- selected reco row (background/data/pass-signal) ----
    eq("sel_ok", V.selected_reco_row_verdict(0.734, 5.0), ("ok", False, True))
    # sentinel on a SELECTED row = missing muon => FATAL
    eq("sel_sentinel_fatal", V.selected_reco_row_verdict(-9999.0, -9999.0),
       ("sentinel_on_selected", True, False))
    eq("sel_sentinel_one_fatal", V.selected_reco_row_verdict(-9999.0, 5.0),
       ("sentinel_on_selected", True, False))
    # 1D corrupt background row: finite out-of-domain => censused, recoverable
    eq("sel_1D_corrupt_censused", V.selected_reco_row_verdict(2960428.0, 31233701.0),
       ("out_of_domain", False, False))
    # non-finite on a selected row => FATAL (cannot be domain-filtered)
    eq("sel_nan_fatal", V.selected_reco_row_verdict(float("nan"), 5.0),
       ("nonfinite", True, False))

    # ---- truth row: non-finite fatal; out-of-domain is prior tail (not fatal) ----
    eq("truth_ok", V.truth_row_verdict(0.5, 3.0), ("ok", False, True))
    eq("truth_nan_fatal", V.truth_row_verdict(float("nan"), 3.0), ("nonfinite", True, False))
    eq("truth_ood_not_fatal", V.truth_row_verdict(50.0, 200.0), ("out_of_domain", False, False))

    # ---- policy invariants that make the recovery sound ----
    # A fatal verdict must never be in-domain-accepted; a censused verdict must be non-fatal.
    for pt, pp in [(float("nan"), 1.0), (1.0, float("inf")), (-9999.0, -9999.0)]:
        v, fatal, ind = V.selected_reco_row_verdict(pt, pp)
        eq(f"fatal_not_accepted[{pt},{pp}]", (fatal and not ind), True)
    v, fatal, ind = V.selected_reco_row_verdict(2960428.0, 31233701.0)
    eq("censused_is_nonfatal_and_outofdomain", (not fatal and not ind), True)

    if F:
        print(f"FAIL: {len(F)} of {P + len(F)} checks failed:")
        for x in F:
            print("  -", x)
        return 1
    print(f"PASS: {P} domain-classification unit checks passed "
          "(incl. the 1D corrupt-row census vs fail-closed split).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
