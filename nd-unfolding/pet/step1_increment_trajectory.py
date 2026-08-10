#!/usr/bin/env python3
"""Was step 1's increment EVER right? The per-iteration trajectory of the step-1 classifier ratio.

WHAT THIS ANSWERS. `step1_pull_push_decomposition.py` established on bit-faithful checkpoints that the
step-1 increment at the LAST iteration has the WRONG SIGN: its reco-weighted mean is 0.648331 where
~1.16 is required to carry `push_prev` (0.967659) up to R = 1.1240802949941018. Step 1 applies a ~35%
reduction where a ~16% increase is needed. A merely non-converged classifier would under-correct
TOWARD 1, not correct past it in the opposite direction, so non-convergence has to explain a sign --
which raises the bar on that hypothesis rather than confirming it.

THE DISCRIMINATOR IS ITERATION 0, and it is a clean binary. At iteration 0 `weights_push` is
identically 1 (omnifold.py:168), so RunStep1's two training classes are exactly

    MC   (label 0):  mc_weight_reco * pass_reco          -- normalized by the loader to 1e6
    DATA (label 1):  data.weight    * data.pass_reco     -- 1.1240802949941018e6

and the ideal classifier ratio therefore has reco-weighted mean EXACTLY R. So:

  * measured mean_w_reco(r1 @ iter0) ~ 1.124  =>  step 1 starts CORRECT and something degrades it
    across iterations. The defect is in the iteration dynamics (what push feeds back, or the
    `cached=i>start` training-data reuse at omnifold.py:194/335).
  * measured mean_w_reco(r1 @ iter0) ~ 0.65   =>  step 1 is broken with push == 1, i.e. before any
    feedback exists. The defect is in step 1's own class normalization or training, and the whole
    iteration story is a red herring.

Those two readings point at disjoint parts of the code, which is why this measurement is worth a job.

WHAT ELSE IT REPORTS, because each kills a specific alternative:
  * `required[i] = R / mean_w_reco(push[i-1])` against the END-TO-END achieved factor
    `mean_w_reco(push[i]) / mean_w_reco(push[i-1])`. BOTH SIDES ARE END-TO-END, which matters: an
    earlier version of this harness compared `required` against `mean_w_reco(r1)` alone -- the first
    leg's average -- omitting `Cov_w(push_prev, r1)` and step 2's re-estimation (measured at +4.22%
    and +5.85% on the annealed arm). That is BEN-077's defect class and it inflated the apparent
    shortfall. `mean_w_reco(r1)` is still reported, explicitly labelled as a first-leg decomposition
    diagnostic that is NOT comparable to `required`.
  * the ratio distribution (percentiles) and the F3 logit-cap saturation fraction. If the mean is low
    because a large weight-mass is pinned at the cap floor, that is a saturation artifact rather than
    a learned ratio, and the cap telemetry says so directly.
  * mean_w_reco(push[i]) for every i, so "is it converging or diverging" is answered from the
    trajectory rather than from two endpoints.

PROVENANCE CAVEAT, stated because it bounds the conclusion. Only `iter{niter-1}` carries the BEN-043
`_final` (last-epoch) checkpoints. Earlier iterations have ONLY best-epoch files, so r1 @ iter0 and
iter1 are best-epoch weights, not the weights that actually fed the next iteration. BEN-043 measured
that gap at ~1.3% on the fold-forward ratio -- far too small to blur a 1.124-versus-0.65
discrimination, which is why this measurement survives the caveat. It would NOT survive it if the
question were a few-percent one.

GATED. Reproduces the three committed STEP1_DECOMPOSITION numbers first and refuses to print the
trajectory unless it does, so a silent environment or checkpoint change cannot masquerade as a result.

    python3 -u step1_increment_trajectory.py \
        --weights fullevent_nominal/pet_fullevent_nominal_weights.npz \
        --decomposition-receipt fullevent_nominal/STEP1_DECOMPOSITION.slurm-56445883.json \
        --json fullevent_nominal/STEP1_TRAJECTORY.slurm-$SLURM_JOB_ID.json
"""
import argparse
import json
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (_HERE, os.path.dirname(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Reproduction tolerance for the gate below. Loose enough for GPU nondeterminism between this run and
# 56445883 (measured floor ~1.3%), tight enough that a different checkpoint or dump cannot pass.
REPRO_RTOL = 0.02


def jsonable(o):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", required=True)
    ap.add_argument("--decomposition-receipt", required=True,
                    help="the committed STEP1_DECOMPOSITION receipt this run must reproduce first")
    ap.add_argument("--json", required=True)
    # Per-step batch sizes, matching the engine: omnifold.py:199 RunStep1 passes an explicit 1000;
    # omnifold.py:219 RunStep2 passes nothing and falls through to MultiFold.BATCH_SIZE = 512.
    # A single shared value reproduces one step and silently mis-reproduces the other (BEN-072).
    ap.add_argument("--batch-size-step1", type=int, default=1000)
    ap.add_argument("--batch-size-step2", type=int, default=512)
    a = ap.parse_args(argv)

    with np.load(a.weights, allow_pickle=True) as d:
        def item(k):
            v = d[k]
            try:
                return v.item()
            except Exception:
                return v
        contract = item("inference_contract")
        target_meta = item("target")
        policy = item("seed_policy")
        stored_push = np.asarray(d["weights_push"], np.float64)
        stored_imc = np.asarray(d["mc_indices"])
        inputs_path = str(item("inputs_path"))
        sum_w_reco_art = float(d["fold_forward_sum_w_reco"])
        cap = float(np.asarray(item("reweight_logit_cap")).ravel()[0]) if "reweight_logit_cap" in d.files else None
    R = float(target_meta["step1_class_ratio"])
    niter = int(policy["niter"])
    sem = str(contract.get("checkpoint_semantics", ""))
    if "BEN-043" not in sem:
        raise SystemExit(f"[traj] checkpoint_semantics={sem!r} lacks the BEN-043 marker: this "
                         f"artifact's checkpoints are not the trained model (fail closed)")
    print(f"[traj] R = {R:.16f}  niter = {niter}  logit_cap = {cap}")

    ref = json.load(open(a.decomposition_receipt))

    import train_fullevent_nominal as T
    import fullevent_fps_dataloader as fe
    from omnifold import PET
    from extract_fullevent_fps import _engine_reweighter

    _data, mc, imc, coord_reco, coord_gen, meta = fe.build_fullevent_loaders(
        inputs_path, max_events=int(policy["train_events"]),
        seed=int(policy["subsample_seed"]), bkg_mode=T.BKG_MODE,
        precomputed_target=target_meta.get("consumed_precomputed_target"))
    imc = np.asarray(imc)
    if not np.array_equal(imc, stored_imc):
        raise SystemExit("[traj] rebuilt subsample != the artifact's mc_indices (fail closed)")

    reco, gen = np.asarray(mc.reco), np.asarray(mc.gen)
    reco_evt, gen_evt = np.asarray(mc.reco_evt), np.asarray(mc.gen_evt)
    pass_reco = np.asarray(mc.pass_reco).astype(bool)
    pass_gen = np.asarray(mc.pass_gen).astype(bool)
    P = reco.shape[1]
    ev_reco, ev_truth = meta["n_evt_reco"], meta["n_evt_truth"]
    wf, name = contract["weights_folder"], contract["multifold_name"]

    def ckpt(it, step):
        fin = os.path.join(wf, f"OmniFold_{name}_iter{it}_step{step}_final.weights.h5")
        if os.path.exists(fin):
            return fin, "final(BEN-043)"
        p = os.path.join(wf, f"OmniFold_{name}_iter{it}_step{step}.weights.h5")
        if not os.path.exists(p):
            raise SystemExit(f"[traj] missing checkpoint {p} (fail closed)")
        return p, "best-epoch"

    def build(step):
        if step == 1:
            return PET(reco.shape[-1], num_evt=ev_reco, num_part=P, num_transformer=2,
                       num_heads=2, projection_dim=32, local=True, K=3, coord_idx=coord_reco)
        return PET(gen.shape[-1], num_evt=ev_truth, num_part=P, num_transformer=2,
                   num_heads=2, projection_dim=32, local=True, K=3, coord_idx=coord_gen)

    prov = {}

    def engine_reweight(step, it, events):
        bs = a.batch_size_step1 if step == 1 else a.batch_size_step2
        path, tier = ckpt(it, step)
        prov[f"step{step}_iter{it}"] = {"checkpoint": path, "provenance_tier": tier}
        m = build(step)
        m.load_weights(path)
        of = _engine_reweighter(m, bs)
        return np.asarray(of.reweight(events, m, batch_size=bs), np.float64)

    with np.load(inputs_path, allow_pickle=True) as d:
        w_reco_raw = np.asarray(d["w_reco"], np.float64)[imc]
        w_truth_raw = np.asarray(d["w_truth"], np.float64)[imc]
    w_reco = w_reco_raw * (sum_w_reco_art / float(w_reco_raw[pass_reco].sum()))

    def wmean(x, w, m):
        return float((x[m] * w[m]).sum() / w[m].sum())

    def pinned(vals, mask):
        out = np.ones_like(stored_push)
        out[mask] = vals[mask]
        return out

    # ---- gate: reproduce the committed decomposition before measuring anything new ---------------
    print(f"\n[traj] GATE: reproducing {os.path.basename(a.decomposition_receipt)}")
    r1_last = pinned(engine_reweight(1, niter - 1, (reco, reco_evt)), pass_reco)
    push_prev = pinned(engine_reweight(2, niter - 2, (gen, gen_evt)), pass_gen)
    push_last = pinned(engine_reweight(2, niter - 1, (gen, gen_evt)), pass_gen)
    got = {"increment1": wmean(r1_last, w_reco, pass_reco),
           "push_prev": wmean(push_prev, w_reco, pass_reco),
           "push_final": wmean(push_last, w_reco, pass_reco)}
    # The committed receipt nests the five measured quantities under "quantities" (verified against
    # STEP1_DECOMPOSITION.slurm-56445883.json). Read that key explicitly rather than guessing at a
    # shape: a lookup that silently misses would make this gate vacuous, which is the BEN-032/040
    # family this repo keeps rediscovering.
    qs = ref.get("quantities")
    if not isinstance(qs, dict):
        raise SystemExit(f"[traj] {a.decomposition_receipt} has no 'quantities' block (fail closed)")
    gate = {}
    for k, v in got.items():
        want = (qs.get(k) or {}).get("mean_w_reco_over_pass_reco")
        if want is None:
            raise SystemExit(f"[traj] receipt has no quantities.{k}.mean_w_reco_over_pass_reco")
        rel = abs(v / float(want) - 1.0)
        gate[k] = {"receipt": float(want), "reproduced": v, "rel_dev": rel,
                   "ok": rel <= REPRO_RTOL}
        print(f"  {k:<12} receipt {float(want):.6f}  here {v:.6f}  rel {rel:.3e}  "
              f"{'OK' if rel <= REPRO_RTOL else 'MISMATCH'}")
    if not all(g["ok"] for g in gate.values()):
        json.dump({"verdict": "GATE_FAILED", "gate": gate}, open(a.json, "w"),
                  indent=2, default=jsonable)
        raise SystemExit("[traj] reproduction gate FAILED -- refusing to print a trajectory")
    print("[traj] GATE PASSED\n")

    # ---- the trajectory --------------------------------------------------------------------------
    r1, push = {}, {}
    for it in range(niter):
        print(f"[traj] iter {it}: step-1 ratio")
        r1[it] = pinned(engine_reweight(1, it, (reco, reco_evt)), pass_reco)
        print(f"[traj] iter {it}: step-2 push")
        push[it] = pinned(engine_reweight(2, it, (gen, gen_evt)), pass_gen)

    rows = []
    for it in range(niter):
        base = 1.0 if it == 0 else wmean(push[it - 1], w_reco, pass_reco)
        m_r1 = wmean(r1[it], w_reco, pass_reco)
        required = R / base if base else None
        v = r1[it][pass_reco]
        ww = w_reco[pass_reco]
        # BEN-077: `required` = R/mean_w(push_prev) is an END-TO-END requirement -- it asks what factor
        # carries mean_w(push_prev) to R. `mean_w(r1)` is only the FIRST LEG's average, and reaching the
        # requirement through r1 also passes through Cov_w(push_prev, r1) and step 2's re-estimation
        # (measured at +4.22% and +5.85% respectively on the annealed arm). Comparing them is
        # apples-to-oranges, and the original version of this harness did exactly that. Both are now
        # reported, with the END-TO-END pair carrying the sign/ratio verdict and the first-leg average
        # retained as a decomposition diagnostic.
        m_push = wmean(push[it], w_reco, pass_reco)
        e2e = (m_push / base) if base else None
        rows.append({
            "iteration": it,
            "push_prev_mean_w_reco": base,
            "r1_mean_w_reco": m_r1,
            "r1_required_mean": required,
            # --- the like-for-like comparison: both sides end-to-end (BEN-077) ---
            "end_to_end_achieved": e2e,
            "end_to_end_achieved_over_required": (e2e / required) if (required and e2e) else None,
            "end_to_end_sign_is_wrong": bool(required is not None and e2e is not None
                                             and (e2e - 1.0) * (required - 1.0) < 0),
            # --- first-leg decomposition, NOT comparable to `r1_required_mean` ---
            "r1_achieved_over_required_FIRST_LEG_ONLY_NOT_LIKE_FOR_LIKE":
                (m_r1 / required) if required else None,
            "r1_is_below_one": bool(m_r1 < 1.0),
            "correction_sign_is_wrong": bool(required is not None
                                             and (m_r1 - 1.0) * (required - 1.0) < 0),
            "pull_mean_w_reco": wmean(push[it - 1] * r1[it] if it else r1[it], w_reco, pass_reco),
            "push_mean_w_reco": wmean(push[it], w_reco, pass_reco),
            "push_dev_vs_R": wmean(push[it], w_reco, pass_reco) / R - 1.0,
            "r1_percentiles_w_unweighted": {p: float(np.percentile(v, p))
                                            for p in (1, 5, 25, 50, 75, 95, 99)},
            "r1_weight_mass_below_one": float(ww[v < 1.0].sum() / ww.sum()),
            "r1_cap_saturated_frac": (float(ww[np.abs(np.log(np.clip(v, 1e-300, None))) >= 0.999 * cap].sum()
                                            / ww.sum()) if cap else None),
            "checkpoint_tier_step1": prov[f"step1_iter{it}"]["provenance_tier"],
        })

    print("=== STEP-1 INCREMENT TRAJECTORY ===")
    print(f"  R = {R:.6f}\n")
    print(f"  {'it':>2} {'push_prev':>10} {'e2e ach':>9} {'required':>10} {'ach/req':>8} "
          f"{'sign':>6} {'push':>10} {'push dev':>9} | {'r1 mean':>9} {'(1st leg)':>9}")
    for r in rows:
        print(f"  {r['iteration']:>2} {r['push_prev_mean_w_reco']:10.6f} "
              f"{r['end_to_end_achieved']:9.6f} {r['r1_required_mean']:10.6f} "
              f"{r['end_to_end_achieved_over_required']:8.4f} "
              f"{'WRONG' if r['end_to_end_sign_is_wrong'] else 'ok':>6} "
              f"{r['push_mean_w_reco']:10.6f} {r['push_dev_vs_R']:+9.4f} | "
              f"{r['r1_mean_w_reco']:9.6f} "
              f"{r['r1_achieved_over_required_FIRST_LEG_ONLY_NOT_LIKE_FOR_LIKE']:9.4f}")

    it0 = rows[0]
    # The discriminator. At iteration 0 push == 1, so required == R exactly and the two readings are
    # far apart; `verdict` names which part of the code the evidence points at.
    if it0["end_to_end_sign_is_wrong"]:
        verdict = "BROKEN_AT_ITER0"
        reading = ("step 1's ratio is already wrong-signed at iteration 0, where push == 1 and the "
                   "ideal ratio's reco-weighted mean is EXACTLY R. No feedback exists yet, so the "
                   "defect is in step 1's own class normalization or training, NOT in the iteration "
                   "dynamics.")
    elif abs(it0["end_to_end_achieved_over_required"] - 1.0) <= 0.10:
        verdict = "RIGHT_SIGN_AT_ITER0_INVERTS_LATER"
        reading = ("step 1's correction has the RIGHT SIGN at iteration 0 and inverts only later, so "
                   "the defect is in the iteration dynamics -- what push feeds back, or the cached "
                   "training-data reuse at omnifold.py:194/335. NOTE the sign is the claim, not "
                   "accuracy: end-to-end at iteration 0 the correction UNDERSHOOTS by ~2.8% "
                   "(0.9721 of required). The predecessor label CORRECT_AT_ITER0_DEGRADES_LATER "
                   "overstated this and is retired; receipt STEP1_TRAJECTORY.slurm-56525829.json "
                   "carries the old string and means exactly this.")
    else:
        verdict = "UNDER_ACHIEVES_AT_ITER0_SAME_SIGN"
        reading = ("step 1 under-achieves at iteration 0 but with the CORRECT sign, so the sign "
                   "inversion is an iteration effect layered on a step-1 capacity/convergence "
                   "shortfall present from the start.")
    print(f"\n[traj] VERDICT: {verdict}\n  {reading}")

    payload = {"schema": "pet-fullevent-step1-trajectory-v1", "verdict": verdict,
               "verdict_label_history": {
                   "CORRECT_AT_ITER0_DEGRADES_LATER": "RETIRED 2026-08-10 -- 'CORRECT' overstated a "
                   "correction that end-to-end UNDERSHOOTS by ~2.8% at iteration 0; the load-bearing "
                   "claim was always the SIGN. Renamed RIGHT_SIGN_AT_ITER0_INVERTS_LATER. Same meaning, "
                   "honest name."},
               "reading": reading, "R": R, "niter": niter, "logit_cap": cap,
               "reproduction_gate": gate, "trajectory": rows, "checkpoints": prov,
               "weights": os.path.abspath(a.weights),
               "decomposition_receipt": os.path.abspath(a.decomposition_receipt),
               "batch_size_step1": a.batch_size_step1, "batch_size_step2": a.batch_size_step2,
               "caveat": ("iterations below niter-1 use BEST-epoch checkpoints; only iter{niter-1} "
                          "has the BEN-043 _final weights. The ~1.3% best-vs-final gap cannot blur "
                          "the 1.124-vs-0.65 discrimination this script turns on.")}
    with open(a.json, "w") as fh:
        json.dump(payload, fh, indent=2, default=jsonable)
        fh.write("\n")
    print(f"[traj] wrote {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
