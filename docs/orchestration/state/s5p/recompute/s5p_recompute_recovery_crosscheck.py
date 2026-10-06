"""s5p recompute lane: independent cross-check of the recovered lost seeds under the frozen-S reading (report side).

NOT part of the reviewed evaluator or comparer; it changes no primary output and gates nothing. Every statistic is
computed by the reviewed ``s5p_recompute`` (imported, deployed beside this file) and nothing of the campaign's
recovery tool is read. Definitions agreed with the campaign 2026-10-05 (handoff §5.11):

1. identity: the recovered products of each null and power set are exactly this lane's lost seeds
   (``seed-disposition.json``: interrupted + never started), finished, with matching meta and no overlap with the
   retained products;
2. determinism (independent): every determinism rerun's ``xsec_flat`` equals its original production product bit
   for bit, and its statistics are therefore identical;
3. frozen S: the process shift is computed from the RETAINED terminal ensemble only; recovered draws are scored
   against the same frozen variant shifts. Per null, test and variant: ``k_frozen`` (must reproduce the terminal
   ``recompute.json``), ``k_rec`` = #{recovered T_v >= T_obs} (ties count), ``k' = k_frozen + k_rec``, ``B' = B + M``,
   and the resolved claim p = max over the family's variants of (k' + 1)/(B' + 1). Families: the claim variants;
   the kappa = 3 REPLACE family (ruled: c S and +-3 delta_M1); the keep-both family (claim variants and +-3 delta_M1);
4. Holm with determinacy (95% CP, family order) on the resolved claims of each family; the ruled labels from the
   primary and replace decisions (``robust_labels``);
5. power: each complete power set (retained + recovered alternatives) against the null's RETAINED ensemble (the
   reviewed ``power_of_set``), and the retained-only power reproduced from the terminal record.

Exit 0 written and every identity/reproduction check holds; 3 written with ``failures`` listed; 2 input error.
"""
from __future__ import annotations

import argparse
import copy
import glob
import json
import os
import sys
import tempfile
import time
from pathlib import Path

import s5p_recompute as R  # the reviewed module, deployed beside this file; imported BEFORE numpy so its single-thread
# BLAS pin takes effect (reproducible rounding; ~250x faster under login-node contention)

import numpy as np  # noqa: E402


def rec_files(root: str, kind: str, name: str) -> list[str]:
    return R.finished_products(os.path.join(root, kind, name, "*.npz"))


def lost_seeds(disp_rec: dict) -> list[int]:
    return sorted(int(s) for s, v in disp_rec["seeds"].items()
                  if v["disposition"] in ("submitted_interrupted", "submitted_never_started"))


def families(ev, ctx):
    _, claim = ev.shifts_for(ctx)
    rob = ev.shifts_for(ctx, "kappa_robust")[1] if "none" not in ctx["m1"] else {}
    m1_3 = {k: v for k, v in rob.items() if k.startswith("m1=") and k not in claim}
    return {"claim": claim,
            "kappa3_replace": {**{k: v for k, v in claim.items() if not k.startswith("m1=")}, **m1_3},
            "kappa3_keep_both": {**claim, **m1_3}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    for a in ("--design", "--v", "--s5c-contract", "--recompute", "--disposition", "--recovered-root",
              "--determinism-root", "--out"):
        ap.add_argument(a, required=True)
    a = ap.parse_args(argv)
    try:
        design = json.load(open(a.design))
        term = json.load(open(a.recompute))
        disp = json.load(open(a.disposition))
        contract = json.load(open(a.s5c_contract))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    ev = R.Evaluator(design, a.v, contract, log=lambda *x: None)
    fails, out = [], {"schema": "s5p-recompute-recovery-crosscheck/1", "not_part_of_reviewed_code": True,
                      "report_only": True, "reading": "frozen S (agreed 2026-10-05, handoff 5.11)",
                      "inputs": {k: getattr(a, k.replace("-", "_")) for k in
                                 ("design", "v", "s5c_contract", "recompute", "disposition", "recovered_root",
                                  "determinism_root")},
                      "input_sha256": {"design": R.sha256(a.design), "recompute": R.sha256(a.recompute),
                                       "disposition": R.sha256(a.disposition)},
                      "code_sha256": {"crosscheck": R.sha256(__file__), "s5p_recompute": R.sha256(R.__file__)},
                      "nulls": {}, "power": {}, "determinism": {}, "family": {}}
    fam_order = [tuple(d["test"].split(":")) for d in term["family"]["decisions"]]
    state = {}
    # ---- calibration nulls
    t0 = time.time()
    for key, spec in design["nulls"].items():
        print(f"[{time.time() - t0:7.0f}s] null {key}", flush=True)
        tn = term["nulls"][key]
        prods = ev.load_ensemble(spec["calibration_glob"])
        files = rec_files(a.recovered_root, "cal", key)
        recs = [R.load_product(p, ev.geom, ev.bands) for p in files]
        want = lost_seeds(disp["nulls"][key])
        got = sorted(p.seed for p in recs)
        ident = {"recovered": len(recs), "lost": len(want), "equal_to_lost_set": got == want,
                 "overlap_with_retained": sorted(set(got) & {p.seed for p in prods}),
                 "retained_B": len(prods), "terminal_B": tn["B"]}
        if got != want or ident["overlap_with_retained"] or len(prods) != tn["B"]:
            fails.append(f"{key}: identity {ident}")
        ctx = ev.null_context(key, prods)
        ctx["key"] = key
        fams = families(ev, ctx)
        allv = {**fams["claim"], **fams["kappa3_keep_both"]}
        ens_f = R.null_ensembles(ctx["f_cal"], ctx["eps"], ctx["ts"], allv)
        f_rec = np.array([ev.sur.apply(p) for p in recs]) if recs else np.zeros((0, ev.geom.n))
        e_rec = (np.array([R.prediction_error(ctx["seed0"], p.seed, ctx["var"]) for p in recs]) if recs
                 else np.zeros((0, ev.geom.n)))
        ens_r = R.null_ensembles(f_rec, e_rec, ctx["ts"], allv)
        obs = R.stats_of(ev.f_data[ctx["ts"].dom], ctx["ts"].mu, ctx["ts"])
        B, M = len(prods), len(recs)
        rec_out = {"identity": ident, "B": B, "M": M, "B_prime": B + M, "T_obs": obs, "tests": {}}
        for t in R.TESTS:
            per_v = {}
            for v in allv:
                kf = int(R.rank_counts(obs[t], ens_f[v][t])[0])
                kr = int(R.rank_counts(obs[t], ens_r[v][t])[0]) if M else 0
                per_v[v] = {"k_frozen": kf, "k_recovered": kr, "k_prime": kf + kr,
                            "max_recovered_T": float(ens_r[v][t].max()) if M else None,
                            "margin_T_obs_minus_max_recovered": float(obs[t] - ens_r[v][t].max()) if M else None}
            # k_frozen must reproduce the terminal record (claim family, and the replace family's m1 +-3)
            tt = tn["tests"][t]
            for v, rec in tt["variants"].items():
                if per_v[v]["k_frozen"] != rec["k"]:
                    fails.append(f"{key}:{t}:{v} k_frozen {per_v[v]['k_frozen']} != terminal {rec['k']}")
            rr = (tt.get("robust_kappa3_replace_kappa2") or {}).get("variants") or {}
            for v, rec in rr.items():
                if per_v[v]["k_frozen"] != rec["k"]:
                    fails.append(f"{key}:{t}:{v} (replace) k_frozen {per_v[v]['k_frozen']} != terminal {rec['k']}")
            claims = {}
            for fname, shifts in fams.items():
                kmax = max(per_v[v]["k_prime"] for v in shifts)
                kfrz = max(per_v[v]["k_frozen"] for v in shifts)
                any_draw = int(np.sum(np.any(np.vstack([ens_r[v][t] >= obs[t] for v in shifts]), axis=0))) if M else 0
                claims[fname] = {"variants": sorted(shifts), "k_frozen_claim": kfrz, "k_prime_claim": kmax,
                                 "B_prime": B + M, "p_resolved": R.mc_p(kmax, B + M),
                                 "interval_resolved": list(R.cp_interval(kmax, B + M)),
                                 "draws_exceeding_under_any_variant_upper_bound": any_draw}
            rec_out["tests"][t] = {"T_obs": obs[t], "per_variant": per_v, "claims": claims}
        out["nulls"][key] = rec_out
        state[key] = {"ctx": ctx, "ens_claim": {v: ens_f[v] for v in fams["claim"]}}
    # ---- resolved Holm per family, ruled labels
    for fname in ("claim", "kappa3_replace", "kappa3_keep_both"):
        ents = []
        for key, t in fam_order:
            c = out["nulls"][key]["tests"][t]["claims"][fname]
            ents.append({"test": f"{key}:{t}", "p": c["p_resolved"], "k": c["k_prime_claim"], "B": c["B_prime"]})
        out["family"][f"decisions_resolved_{fname}"] = R.holm_determined(ents, float(term["alpha_family"]))
    out["family"]["labels_resolved"] = R.robust_labels(out["family"]["decisions_resolved_claim"],
                                                       out["family"]["decisions_resolved_kappa3_replace"])
    prim = {d["test"]: d["decision"] for d in term["family"]["decisions"]}
    out["family"]["primary_decisions_changed"] = [d["test"] for d in out["family"]["decisions_resolved_claim"]
                                                  if d["decision"] != prim[d["test"]]]
    out["family"]["ruled_labels_changed"] = [k for k, v in out["family"]["labels_resolved"].items()
                                             if v != term["family"]["robust_labels"][k]]
    # ---- power: complete sets against the retained null ensemble (the reviewed power_of_set)
    tmp = Path(tempfile.mkdtemp(prefix="s5p_rec_pow_"))
    try:
        for sk, spec in design.get("power", {}).items():
            print(f"[{time.time() - t0:7.0f}s] power {sk}", flush=True)
            null = spec["null"]
            frozen = R.finished_products(spec["glob"])
            recf = rec_files(a.recovered_root, "pow", sk)
            want = lost_seeds(disp["power"][sk])
            got = sorted(R.seed_of(p) for p in recf)
            if got != want or set(got) & {R.seed_of(p) for p in frozen}:
                fails.append(f"power {sk}: recovered seeds {len(got)} != lost {len(want)} or overlap")
            d = tmp / sk
            d.mkdir()
            for p in frozen + recf:
                os.symlink(os.path.abspath(p), d / os.path.basename(p))
            ev_c = copy.copy(ev)
            ev_c.design = copy.deepcopy(ev.design)
            ev_c.design["power"][sk]["glob"] = str(d / "*.npz")
            st = state[null]
            complete = R.power_of_set(ev_c, sk, st["ctx"], st["ens_claim"])
            retained = R.power_of_set(ev, sk, st["ctx"], st["ens_claim"])
            for t in R.TESTS:
                for lvl in ("0.05", "0.005"):
                    for rule in ("rank_unshifted", "rank_claim", "determined_claim"):
                        if retained[t][lvl][rule]["count"] != term["power"][sk][t][lvl][rule]["count"]:
                            fails.append(f"power {sk}:{t}:{lvl}:{rule} retained count does not reproduce the terminal")
            out["power"][sk] = {"null": null, "n_retained": len(frozen), "n_recovered": len(recf),
                                "n_complete": complete["n_present"], "n_declared": complete["n_declared"],
                                "complete_set": {t: complete[t] for t in R.TESTS},
                                "retained_only": {t: retained[t] for t in R.TESTS},
                                "conditional_on": "the null's retained calibration ensemble (frozen S)"}
    finally:
        for p in tmp.rglob("*"):
            if p.is_symlink():
                p.unlink()
        for p in sorted(tmp.rglob("*"), reverse=True):
            p.rmdir()
        tmp.rmdir()
    print(f"[{time.time() - t0:7.0f}s] determinism", flush=True)
    # ---- determinism, independently: rerun xsec_flat == original product, bit for bit
    for kind in ("cal", "pow"):
        for d in sorted(glob.glob(os.path.join(a.determinism_root, kind, "*"))):
            name = os.path.basename(d)
            src = (design["nulls"][name]["calibration_glob"] if kind == "cal" else design["power"][name]["glob"])
            orig = {R.seed_of(p): p for p in R.finished_products(src)}
            for p in R.finished_products(os.path.join(d, "*.npz")):
                s = R.seed_of(p)
                with np.load(p, allow_pickle=False) as z1, np.load(orig[s], allow_pickle=False) as z2:
                    same = bool(np.array_equal(z1["xsec_flat"], z2["xsec_flat"]))
                    m1, m2 = json.loads(str(z1["meta"])), json.loads(str(z2["meta"]))
                out["determinism"][f"{kind}:{name}:{s}"] = {
                    "xsec_flat_bitwise_equal": same, "pseudo_seed_equal": m1["pseudo_seed"] == m2["pseudo_seed"],
                    "nuisance_draw_equal": m1.get("nuisance_draw") == m2.get("nuisance_draw")}
                if not (same and m1["pseudo_seed"] == m2["pseudo_seed"] and m1.get("nuisance_draw") == m2.get("nuisance_draw")):
                    fails.append(f"determinism {kind}:{name}:{s}")
    out["determinism_summary"] = {"n": len(out["determinism"]),
                                  "all_equal": all(all(v.values()) for v in out["determinism"].values())}
    out["headline"] = {
        "k_recovered_all_zero": all(v["k_recovered"] == 0 for n in out["nulls"].values()
                                    for tr in n["tests"].values() for v in tr["per_variant"].values()),
        "primary_decisions_changed": out["family"]["primary_decisions_changed"],
        "ruled_labels_changed": out["family"]["ruled_labels_changed"]}
    out["failures"] = fails
    out["status"] = "complete" if not fails else "FAILED CHECKS"
    Path(a.out).write_text(json.dumps(R.jsonable(out), indent=1, sort_keys=True) + "\n")
    print(json.dumps(out["headline"]), "| determinism", out["determinism_summary"], "| status", out["status"])
    for f in fails:
        print("  -", f)
    return 3 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
