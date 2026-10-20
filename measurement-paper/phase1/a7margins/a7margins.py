#!/usr/bin/env python3
"""A7 decision-boundary margins: a DESCRIPTIVE receipt (not a re-grade; A7 stands) of how far each of the ten
frozen joint-5D generator tests sits from the boundary of A7's own decision rule.

The decision rule is the frozen one: s5p_joint.test_null (the claim k = the largest exceedance count over the
declared shift variants), then s5p_inference.holm_determined (Holm step-down; at position i, REJECTED iff the
exact 95% Clopper-Pearson upper end of k/B is below alpha/(m - i); the first non-rejection STOPS the procedure and
every later test inherits that state). Everything goes through those functions, imported from copies
byte-identical to the frozen modules, and through mp3b_eval.kstar / t_critical / same (reused, not retyped).

Per test, at its FROZEN Holm position (the order is held fixed: a changed T changes p and could re-order the
family; the re-sorted crossing is reported separately, labelled):
  k_max = largest k with CP upper < threshold;  rejected iff claim k <= k_max
  T_crit(claim variants) = max over the claim variants of the (k_max+1)-th largest null T;  rejected iff T > T_crit
  T_crit(unshifted c = 0) = the (k_max+1)-th largest T of the c = 0 null alone
  margins in the c = 0 null SD (np.std, ddof 0, as s5p_joint reports null_T_*_sd), and over the c = 0 median.
The kappa_robust family adds the kappa_robust M1 variants to the claim variants (s5p_joint: report only).

Usage: python3 a7margins.py --design D --s5c-contract C --v V --frozen-eval J --out OUT_DIR
Exit codes: 0 done; 3 a control failed (results written with the control record, no margins trusted).
"""
from __future__ import annotations

import argparse
import json
import resource
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402

import mp3b_eval as e  # noqa: E402
import s5p_inference as si  # noqa: E402
import s5p_joint as sj  # noqa: E402

LABEL = "DESCRIPTIVE receipt of A7's frozen decision margins; not a re-grade (A7 stands)"
NUWRO_SHAPE_EXPECTED = {"threshold": 0.05, "k_star": 69, "B": 1751, "T_critical_2dp": 8672.55,
                        "T_frozen_2dp": 9660.01, "margin_in_null_sd_2dp": 1.11}
SIDES = ("total", "shape")


def claim_k(T: float, nulls: list) -> int:
    """The claim rule's exceedance count at T: the largest #{null >= T} over the variants (s5p_inference.mc_pvalue)."""
    return max(int(np.sum(np.asarray(t, float) >= T)) for t in nulls)


def run_null(model, design, key, V, names, pz_index) -> dict:
    """The frozen test of one null through s5p_joint.test_null, plus its kappa_robust M1 nulls."""
    spec = design["nulls"][key]
    files = sj.product_files(spec["calibration_glob"])
    B = sj.calibration_count(spec)
    if len(files) != B:
        raise SystemExit(f"{key}: {len(files)} calibration products, {B} declared")
    coefs = [float(c) for c in design.get("shift_coefficients", [0.0])]
    entry = sj.test_null(model, design, key, V, names, pz_index, files, coefs)
    nulls = entry.pop("_nulls")
    robust = {}
    m1 = design["m1_shift"][key]
    if "none" not in m1:
        F, seeds = sj.ensemble(model, files)
        mu, var = sj.prediction(spec["prediction"], model.U)
        dom = np.ones(len(names), bool) if spec.get("domain") != "pz_lt_6" else (pz_index <= 1)
        d1, _ = sj.load_shift({k: v for k, v in m1.items() if k in ("path", "sha256")}, len(names))
        kr = m1["kappa_robust"]
        for nm, sv in ((f"m1+{kr}", kr * d1), (f"m1-{kr}", -kr * d1)):
            robust[nm] = sj.statistics(F + sv, mu, var, V, dom, spec["surrogate_seed0"], seeds=seeds)
    return {"entry": entry, "nulls": nulls, "vnames": list(entry["variants"].keys()), "robust": robust,
            "n_files": len(files)}


def stop_position(order: list, dec: dict):
    for i, key in enumerate(order):
        if dec[key]["decision"] != "rejected":
            return i
    return None


def resorted_crossing(fam: dict, key: str, alpha: float, level: float) -> dict:
    """With every other test held at its frozen claim and the order RE-SORTED by holm_determined itself, the
    smallest claim k (>= the frozen k) at which this test is no longer 'rejected', and the smallest at which any
    decision of the family changes."""
    base = si.holm_determined(fam, alpha, level)
    B = int(fam[key]["B"])
    k_self = k_any = None
    changed_at_any = None
    for k in range(int(fam[key]["k"]), B + 1):
        f2 = dict(fam)
        f2[key] = {"p": (k + 1) / (B + 1), "k": k, "B": B}
        d = si.holm_determined(f2, alpha, level)
        if k_any is None and any(d[x]["decision"] != base[x]["decision"] for x in d):
            k_any = k
            changed_at_any = {x: [base[x]["decision"], d[x]["decision"]] for x in d if d[x]["decision"] != base[x]["decision"]}
        if d[key]["decision"] != "rejected":
            k_self = k
            self_state = d[key]["decision"]
            pos = sorted(f2, key=lambda x: f2[x]["p"]).index(key)
            break
    if k_self is None:
        return {"k_first_not_rejected": None}
    return {"k_first_not_rejected": k_self, "decision_there": self_state, "position_there": pos,
            "threshold_there": d[key]["threshold"], "k_first_any_family_change": k_any,
            "family_changes_at_that_k": changed_at_any}


def margins_family(fam: dict, frozen_dec: dict, per_null: dict, frozen_tests: dict, alpha: float, robust: bool) -> dict:
    order = sorted(fam, key=lambda x: fam[x]["p"])   # = holm_determined's order (stable sort, same dict order)
    m = len(order)
    dec = si.holm_determined(fam, alpha)
    i_stop = stop_position(order, dec)
    out = {}
    for i, key in enumerate(order):
        null_key, s = key.split(":")
        si_ = SIDES.index(s)
        pn = per_null[null_key]
        claim_nulls = [pn["nulls"][j][si_] for j in range(len(pn["vnames"]))]
        vnames = list(pn["vnames"])
        if robust:
            claim_nulls += [pn["robust"][nm][si_] for nm in pn["robust"]]
            vnames += list(pn["robust"])
        e_ = fam[key]
        B, k_obs = int(e_["B"]), int(e_["k"])
        level = frozen_dec[key]["level"]
        th = alpha / (m - i)
        if th != frozen_dec[key]["threshold"]:
            raise SystemExit(f"{key}: threshold {th} != frozen {frozen_dec[key]['threshold']}")
        ks = e.kstar(B, th, level)
        T_obs = float(frozen_tests[null_key]["T_total_obs" if s == "total" else "T_shape_obs"])
        tc = e.t_critical(claim_nulls, ks)
        per_var = [float(np.sort(np.asarray(t, float))[::-1][ks]) for t in claim_nulls]
        bind = int(np.argmax(per_var))
        base = np.asarray(pn["nulls"][pn["vnames"].index("0.0")][si_], float)
        tc0 = e.t_critical([base], ks)
        sd0, med0 = float(np.std(base)), float(np.median(base))
        sd_bind = float(np.std(np.asarray(claim_nulls[bind], float)))
        sd_pool = float(np.std(np.concatenate([np.asarray(t, float) for t in claim_nulls])))
        # direction checks of the boundary: at T_crit the claim k is k_max + 1 (not rejected); just above, <= k_max
        k_at = claim_k(tc, claim_nulls)
        k_above = claim_k(float(np.nextafter(tc, np.inf)), claim_nulls)
        hi_at = si.cp_interval(k_at, B, level)[1]
        hi_above = si.cp_interval(k_above, B, level)[1]
        row = {"holm_position_0based": i, "holm_position_1based": i + 1, "m": m, "threshold": th, "B": B,
               "level": level, "k_obs_claim": k_obs, "p_claim": e_["p"], "k_max": ks,
               "cp_upper_at_k_max": si.cp_interval(ks, B, level)[1], "cp_upper_at_k_max_plus_1": si.cp_interval(ks + 1, B, level)[1],
               "T_obs": T_obs,
               "claim_k_recomputed_at_T_obs": claim_k(T_obs, claim_nulls),
               "variants_in_claim_ensemble": vnames,
               "T_crit_claim_variants": tc, "T_crit_binding_variant": vnames[bind],
               "T_crit_per_variant": dict(zip(vnames, per_var)),
               "T_crit_unshifted_c0": tc0,
               "boundary_check": {"claim_k_at_T_crit": k_at, "cp_upper_at_T_crit": hi_at,
                                  "claim_k_just_above_T_crit": k_above, "cp_upper_just_above": hi_above,
                                  "pass": bool(k_at == ks + 1 and hi_at >= th and k_above <= ks and hi_above < th)},
               "null_c0_sd_ddof0": sd0, "null_c0_median": med0,
               "null_c0_sd_equals_frozen_record": sd0 == frozen_tests[null_key]["variants"]["0.0"][f"null_T_{s}_sd"],
               "null_c0_median_equals_frozen_record": med0 == frozen_tests[null_key]["variants"]["0.0"][f"null_T_{s}_median"],
               "sd_binding_variant_ddof0": sd_bind, "sd_pooled_claim_variants_ddof0": sd_pool,
               "margin_claim_in_c0_sd": (T_obs - tc) / sd0,
               "margin_unshifted_in_c0_sd": (T_obs - tc0) / sd0,
               "margin_claim_in_binding_variant_sd": (T_obs - tc) / sd_bind,
               "margin_claim_in_pooled_sd": (T_obs - tc) / sd_pool,
               "margin_over_c0_median_in_c0_sd": (T_obs - med0) / sd0,
               "T_drop_to_cross_claim": T_obs - tc,
               "decision_recomputed": dec[key]["decision"], "decision_frozen": frozen_dec[key]["decision"],
               "inherited_from_earlier_stop": bool(i_stop is not None and i > i_stop),
               "resorted_crossing": resorted_crossing(fam, key, alpha, level)}
        rc = row["resorted_crossing"]
        if rc.get("k_first_not_rejected") is not None:
            row["resorted_crossing"]["T_crit_claim_variants"] = e.t_critical(claim_nulls, rc["k_first_not_rejected"] - 1)
            row["resorted_crossing"]["margin_in_c0_sd"] = (T_obs - row["resorted_crossing"]["T_crit_claim_variants"]) / sd0
        if i_stop is not None and i > i_stop:
            th_s = alpha / (m - i_stop)
            ks_s = e.kstar(B, th_s, level)
            tcs = e.t_critical(claim_nulls, ks_s)
            row["at_stop_position"] = {"stop_position_0based": i_stop, "stopping_test": order[i_stop],
                                       "threshold": th_s, "k_max": ks_s, "T_crit_claim_variants": tcs,
                                       "margin_claim_in_c0_sd": (T_obs - tcs) / sd0,
                                       "note": "an inherited decision is set by the stop, not by this test's own threshold"}
        out[key] = row
    return {"order": order, "stop_position_0based": i_stop, "tests": out}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    for k in ("design", "s5c-contract", "v", "frozen-eval", "out"):
        ap.add_argument(f"--{k}", type=Path, required=True)
    a = ap.parse_args(argv)
    t0 = time.time()
    mods = {m.__name__: str(Path(m.__file__).resolve()) for m in (e, si, sj, sj.s1)}
    print("modules", json.dumps(mods), flush=True)
    for n, p in mods.items():
        if Path(p).parent != HERE:
            raise SystemExit(f"{n} imported from {p}, not from {HERE}")
    a.out.mkdir(parents=True, exist_ok=False)
    res = {"schema": "a7margins/1", "label": LABEL, "argv": sys.argv,
           "modules": {n: {"file": p, "sha256": e.sha256(p)} for n, p in mods.items()},
           "numpy": np.__version__, "python": sys.version,
           "inputs": {k: e.sha256(p) for k, p in (("design", a.design), ("s5c_contract", a.s5c_contract), ("v", a.v),
                                                   ("frozen_eval", a.frozen_eval))},
           "order_note": "margins hold the frozen Holm ORDER fixed; a changed T changes p and could re-order the family. "
                         "'resorted_crossing' lets holm_determined re-sort (others held at their frozen claims).",
           "sd_note": "SD = np.std (ddof 0) of the c = 0 null, as s5p_joint records null_T_*_sd",
           "controls": {}}
    import scipy
    res["scipy"] = scipy.__version__

    def finish(code: int, msg: str) -> int:
        ru = resource.getrusage(resource.RUSAGE_SELF)
        res.update(verdict=msg, exit_code=code, cpu_s=ru.ru_utime + ru.ru_stime, maxrss_kb=ru.ru_maxrss, wall_s=time.time() - t0)
        (a.out / "a7margins.json").write_text(json.dumps(res, indent=1, default=lambda o: o.item()) + "\n")
        print(msg, flush=True)
        return code

    design = json.loads(a.design.read_text())
    sj.check_v(design, a.v)
    V = np.asarray(np.load(a.v, allow_pickle=False)["V"], float)
    supported = json.loads(a.s5c_contract.read_text())["measurement"]["partition_J"]["supported_cells"]
    U, names, pz_index = sj.j_matrix({}, supported)
    model = sj.Model(design, U)
    frozen = json.loads(a.frozen_eval.read_text())
    if frozen["names"] != names:
        return finish(3, "STOP: J cell names differ from the frozen evaluation's")
    al = design["alpha_family"]
    per_null, ctl = {}, {}
    for key in design["nulls"]:
        t1 = time.time()
        pn = run_null(model, design, key, V, names, pz_index)
        per_null[key] = pn
        fz = frozen["tests"][key]
        T_o = {"total": fz["T_total_obs"], "shape": fz["T_shape_obs"]}
        rob_p = {nm: {s: si.mc_pvalue(T_o[s], rn[i]) for i, s in enumerate(SIDES)} for nm, rn in pn["robust"].items()}
        ctl[key] = {"test_null_vs_frozen": e.same(pn["entry"], fz), "robust_nulls_vs_frozen": e.same(rob_p, fz["robustness_variants"]),
                    "B": pn["n_files"], "variants": pn["vnames"], "robust_variants": list(pn["robust"]), "s": time.time() - t1}
        print("NULL", key, json.dumps({k: ctl[key][k] for k in ("B", "variants", "robust_variants", "s")}),
              "identical", ctl[key]["test_null_vs_frozen"]["identical"], ctl[key]["robust_nulls_vs_frozen"]["identical"],
              "bitwise", ctl[key]["test_null_vs_frozen"]["bitwise"], ctl[key]["robust_nulls_vs_frozen"]["bitwise"], flush=True)
    fam = {f"{k}:{s}": {x: frozen["tests"][k][s][x] for x in ("p", "k", "B")} for k in design["nulls"] for s in SIDES}
    fam_r = {f"{k}:{s}": {x: frozen["tests"][k][s + "_robust"][x] for x in ("p", "k", "B")} for k in design["nulls"] for s in SIDES}
    # the family as recomputed (not as read): the claims of the recomputed entries
    fam_re = {f"{k}:{s}": {x: per_null[k]["entry"][s][x] for x in ("p", "k", "B")} for k in design["nulls"] for s in SIDES}
    fam_re_r = {f"{k}:{s}": {x: per_null[k]["entry"][s + "_robust"][x] for x in ("p", "k", "B")} for k in design["nulls"] for s in SIDES}
    ctl["holm_determined"] = {"decisions_from_recomputed_claims": e.same(si.holm_determined(fam_re, al), frozen["decisions"]),
                              "decisions_robust_kappa_from_recomputed_claims": e.same(si.holm_determined(fam_re_r, al), frozen["decisions_robust_kappa"]),
                              "holm_point_from_recomputed_p": e.same(si.holm({k: v["p"] for k, v in fam_re.items()}, al), frozen["holm_point"])}
    res["controls"] = ctl
    ok = all(ctl[k]["test_null_vs_frozen"]["identical"] and ctl[k]["robust_nulls_vs_frozen"]["identical"] for k in design["nulls"]) \
        and all(v["identical"] for v in ctl["holm_determined"].values())
    res["controls_bitwise_everywhere"] = bool(all(ctl[k]["test_null_vs_frozen"]["bitwise"] and ctl[k]["robust_nulls_vs_frozen"]["bitwise"]
                                                  for k in design["nulls"]) and all(v["bitwise"] for v in ctl["holm_determined"].values()))
    print("CONTROL_FAMILY", json.dumps(ctl["holm_determined"]), flush=True)
    if not ok:
        return finish(3, "STOP: the frozen tests or decisions were not reproduced")

    res["family"] = margins_family(fam, frozen["decisions"], per_null, frozen["tests"], al, robust=False)
    res["family_robust_kappa"] = margins_family(fam_r, frozen["decisions_robust_kappa"], per_null, frozen["tests"], al, robust=True)
    nw = res["family"]["tests"]["NuWro_21_09:shape"]
    got = {"threshold": nw["threshold"], "k_star": nw["k_max"], "B": nw["B"], "T_critical_2dp": round(nw["T_crit_claim_variants"], 2),
           "T_frozen_2dp": round(nw["T_obs"], 2), "margin_in_null_sd_2dp": round(nw["margin_claim_in_c0_sd"], 2)}
    ctl["NuWro_shape_vs_mp3b_reported"] = {"expected": NUWRO_SHAPE_EXPECTED, "got": got, "pass": got == NUWRO_SHAPE_EXPECTED}
    checks = [r["boundary_check"]["pass"] and r["decision_recomputed"] == r["decision_frozen"]
              and r["claim_k_recomputed_at_T_obs"] == r["k_obs_claim"]
              and r["null_c0_sd_equals_frozen_record"] and r["null_c0_median_equals_frozen_record"]
              for f in ("family", "family_robust_kappa") for r in res[f]["tests"].values()]
    ctl["per_test_internal_checks_pass"] = bool(all(checks))
    for f in ("family", "family_robust_kappa"):
        print("FAMILY", f, "stop", res[f]["stop_position_0based"], flush=True)
        for key in res[f]["order"]:
            r = res[f]["tests"][key]
            print(f"  {r['holm_position_1based']:2d} {key:24s} th={r['threshold']:.6g} B={r['B']} kmax={r['k_max']} "
                  f"Tobs={r['T_obs']:.4f} Tc={r['T_crit_claim_variants']:.4f}({r['T_crit_binding_variant']}) Tc0={r['T_crit_unshifted_c0']:.4f} "
                  f"sd0={r['null_c0_sd_ddof0']:.4f} m={r['margin_claim_in_c0_sd']:.4f} m0={r['margin_unshifted_in_c0_sd']:.4f} "
                  f"mmed={r['margin_over_c0_median_in_c0_sd']:.4f} {r['decision_recomputed']} inh={r['inherited_from_earlier_stop']} "
                  f"resort_k={r['resorted_crossing'].get('k_first_not_rejected')}", flush=True)
    print("CONTROL_NUWRO_SHAPE", json.dumps(ctl["NuWro_shape_vs_mp3b_reported"]), "internal", ctl["per_test_internal_checks_pass"], flush=True)
    if not (ctl["NuWro_shape_vs_mp3b_reported"]["pass"] and ctl["per_test_internal_checks_pass"]):
        return finish(3, "STOP: the NuWro-shape control or a per-test internal check failed")
    return finish(0, "DONE: controls passed; margins written")


if __name__ == "__main__":
    raise SystemExit(main())
