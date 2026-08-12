#!/usr/bin/env python3
"""Memo item 5: decompose the nominal's fold-forward failure into its step-1 (pull) and step-2 (push) parts.

THE FAILURE. `train_fullevent_nominal.py` reports
`sum(w_reco*push | pass_reco)/sum(w_reco | pass_reco) = 0.746483` where the step-1 normalization implies
R = 1.1240802949941018. The deficit is deterministic (the matched floor repeat reproduced it), monotonic in
acceptance, and worst where acceptance is HIGHEST -- which inverts against every difficulty-based
explanation.

WHAT THIS SEPARATES, and why the leg matters more than the step. OmniFold's two steps normalize DIFFERENT
functionals (omnifold.py:179-220):

    step 1  trains data vs reco MC on the RECO leg:   weights_push * mc_weight_reco * pass_reco
            pull := weights_push * classifier1(reco)      on pass_reco, 1 elsewhere
    step 2  trains gen vs gen on the TRUTH leg:       mc.weight * {1, weights_pull} * pass_gen
            push := classifier2(gen)                      on pass_gen, 1 elsewhere

So R is a property of the RECO leg over `pass_reco`, which is exactly what step 1 is fitted to -- while the
number the gate reads is `push`, a step-2 quantity fitted on the TRUTH leg over `pass_gen`. `leg_mismatch.py`
already measured that the truth-leg mean is 0.888234 against the reco-leg 0.746483, ratio 1.189891, so the
leg accounts for ~19% and NOT the whole gap. This script asks the remaining question: does the PULL weight,
which is the thing step 1 actually normalizes, satisfy the identity that `push` fails?

    mean_w_reco(pull | pass_reco)  ~ R   and  mean_w_reco(push | pass_reco) << R
        -> step 1 works; the loss is in step 2's transport from the truth leg back to reco. The gate is
           reading a quantity no step ever normalized, and the identity it asserts is not one the
           algorithm guarantees.
    both << R
        -> step 1 genuinely under-achieves, and the defect is upstream of the leg choice.

Predeclared before running, per BEN-038. Either outcome is a result; neither is a repair.

TWO HAZARDS THIS FILE IS BUILT AROUND.

(1) CUMULATIVE vs INCREMENTAL, which is easy to get backwards and I did at first. `weights_push` is NOT a
    product over iterations -- `RunStep2` does `self.weights_push = new_weights` (omnifold.py:218-220), a
    plain overwrite, so the stored push is ONE model2 evaluation. `weights_pull` IS cumulative:
    `self.weights_pull = self.weights_push * new_weights` (omnifold.py:200), and the `weights_push` on the
    right-hand side is the push from the PREVIOUS iteration, not the final one. So

        pull_final = push_{iter niter-2} * classifier1_{iter niter-1}(reco)

    which needs model2 from iteration 1 AND model1 from iteration 2, not the final step-2 checkpoint. Using
    the final push here would silently multiply the wrong iteration's weights.

(2) THE CHECKPOINTS MAY NOT BE THE TRAINED MODELS. `ModelCheckpoint(save_best_only=True)` writes the
    best-val-loss epoch while `EarlyStopping(patience=10)` cannot fire inside `epochs=8`, so the in-memory
    model at reweight time is the LAST epoch. `gate_ab_push_provenance.py` measures whether that matters.
    THIS SCRIPT REFUSES TO RUN WITHOUT THAT RECEIPT, and copies its verdict into its own output, so the
    caveat travels with the number instead of being remembered separately.

Every input space comes from the REBUILT LOADER (`mc.reco`, `mc.reco_evt`, `mc.gen`, `mc.gen_evt`) and every
reweight goes through the ENGINE's own `reweight`, so nothing here re-implements preprocessing -- which is
the specific risk that kept this task held. Gate A of the receipt is what licenses that.

Usage (GPU node):
  srun -A m3246_g -q interactive -C gpu -N1 -n1 -c32 --gpus=1 -t 90 \
      python3 -u step1_pull_push_decomposition.py --gate-receipt GATE_AB_PUSH_PROVENANCE.json \
              --json STEP1_DECOMPOSITION.json
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
# CANONICAL as of the 2026-08-12 designation promotion of job 56563761 (the annealed nominal).
# By DESIGNATION, not by moving bytes -- see BEN-133. Overridable with --artifact.
DEFAULT_ART = os.path.join(HERE, "fullevent_nominal_annealed",
                           "pet_fullevent_nominal_weights.npz")


def jsonable(o):
    if isinstance(o, (np.floating, float)):
        return float(o)
    if isinstance(o, (np.integer, int)):
        return int(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--artifact", default=DEFAULT_ART)
    ap.add_argument("--gate-receipt", required=True,
                    help="the JSON written by gate_ab_push_provenance.py. Required: without Gate A "
                         "this script cannot claim its rebuilt input space is the trained one.")
    ap.add_argument("--json", default=None)
    # PER-STEP batch sizes, read off the engine's actual call sites rather than shared (BEN-072).
    # The engine does NOT use one batch size:
    #     omnifold.py:199  RunStep1: reweight(..., self.model1, batch_size=1000)   <- explicitly 1000
    #     omnifold.py:219  RunStep2: reweight(..., self.model2)                    <- no arg -> 512
    # A single shared default would reproduce step 1 correctly and BOTH step-2 reweights wrongly. That is
    # the same defect BEN-072 records in gate_ab_push_provenance.py, where batch 1000 against the engine's
    # 512 produced a 1.744e-06 deviation and nearly inverted a verdict; at 512 the same comparison is
    # bit-exact. So these are separate flags with the engine's own values as defaults.
    ap.add_argument("--batch-size-step1", type=int, default=1000,
                    help="must match omnifold.py:199's explicit batch_size=1000")
    ap.add_argument("--batch-size-step2", type=int, default=512,
                    help="must match MultiFold.BATCH_SIZE, which omnifold.py:219 falls through to")
    a = ap.parse_args()

    # ---- the receipt is a precondition, not a formality ------------------------------------------
    g = json.load(open(a.gate_receipt))
    ga = g.get("gate_A", {})
    if not (ga.get("A1_mc_indices_bit_exact") and ga.get("A2_truth_norm_bit_exact")):
        raise SystemExit(f"[step1] Gate A did not pass in {a.gate_receipt} "
                         f"(A1={ga.get('A1_mc_indices_bit_exact')}, "
                         f"A2={ga.get('A2_truth_norm_bit_exact')}). The rebuilt subsample or input "
                         "space is not the trained one, so every number below would describe a "
                         "different estimator (fail closed).")
    gate_verdict = g.get("verdict", "<absent>")
    gb = g.get("gate_B", {})
    print(f"[step1] gate receipt {a.gate_receipt}: verdict {gate_verdict}")
    print(f"[step1]   Gate A passed. Gate B(i) max rel dev "
          f"{gb.get('Bi_max_rel_dev')!r}, pass={gb.get('Bi_pass')!r}")
    if not gb.get("Bi_pass"):
        print("[step1]   *** Gate B(i) FAILED: the saved checkpoints are NOT bit-faithful to the "
              "models that produced the stored weights. Every number below is therefore a "
              "CHECKPOINT-BASED reconstruction, not the run's own weights, and is reported as such. "
              "It is still the right comparison -- both legs are reconstructed the same way -- but "
              "it must not be quoted as the run's pull/push. ***")

    rec = {"gate_receipt": os.path.abspath(a.gate_receipt), "gate_verdict": gate_verdict,
           "batch_size_step1": a.batch_size_step1, "batch_size_step2": a.batch_size_step2,
           "gate_Bi_pass": bool(gb.get("Bi_pass")),
           "gate_Bi_max_rel_dev": gb.get("Bi_max_rel_dev"),
           "reconstruction_is_checkpoint_based": not bool(gb.get("Bi_pass"))}

    with np.load(a.artifact, allow_pickle=True) as d:
        stored_push = np.asarray(d["weights_push"], np.float64)
        stored_imc = np.asarray(d["mc_indices"])
        contract = d["inference_contract"].item()
        policy = d["seed_policy"].item()
        target_meta = d["target"].item()
        inputs_path = str(d["inputs_path"])
        ff_ratio = float(d["fold_forward_sum_w_push_reco"]) / float(d["fold_forward_sum_w_reco"])
        sum_w_reco_art = float(d["fold_forward_sum_w_reco"])
    R = float(target_meta["step1_class_ratio"])
    niter = int(policy["niter"])
    print(f"[step1] R = {R:.16f}   niter = {niter}   stored fold-forward ratio {ff_ratio:.6f}")

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
        raise SystemExit("[step1] the rebuilt subsample no longer matches the artifact, even though "
                         "the receipt says Gate A passed -- something changed between the two runs "
                         "(fail closed)")

    reco = np.asarray(mc.reco)
    gen = np.asarray(mc.gen)
    reco_evt = np.asarray(mc.reco_evt)
    gen_evt = np.asarray(mc.gen_evt)
    pass_reco = np.asarray(mc.pass_reco).astype(bool)
    pass_gen = np.asarray(mc.pass_gen).astype(bool)
    P = reco.shape[1]
    ev_reco, ev_truth = meta["n_evt_reco"], meta["n_evt_truth"]

    wf = contract["weights_folder"]
    name = contract["multifold_name"]

    def ckpt(it, step):
        """Prefer the BEN-043 `_final` weights for the LAST iteration when the driver wrote them.

        Post-fix artifacts carry `_final.weights.h5` for `iter{niter-1}` only -- those are the weights that
        actually produced `weights_push`, and Gate B(i) is bit-exact against them. Earlier iterations have
        only the best-epoch files, which is a real and stated limitation: `increment1` (model1 @ iter2) and
        `push_prev` (model2 @ iter1) come from different provenance tiers.
        """
        fin = os.path.join(wf, f"OmniFold_{name}_iter{it}_step{step}_final.weights.h5")
        if os.path.exists(fin):
            return fin
        p = os.path.join(wf, f"OmniFold_{name}_iter{it}_step{step}.weights.h5")
        if not os.path.exists(p):
            raise SystemExit(f"[step1] missing checkpoint {p} (fail closed)")
        return p

    # Architectures exactly as train_fullevent_nominal.py:383-388 builds them, with the widths taken
    # from the rebuilt loader rather than restated as literals.
    def build(step):
        if step == 1:
            return PET(reco.shape[-1], num_evt=ev_reco, num_part=P, num_transformer=2,
                       num_heads=2, projection_dim=32, local=True, K=3, coord_idx=coord_reco)
        return PET(gen.shape[-1], num_evt=ev_truth, num_part=P, num_transformer=2,
                   num_heads=2, projection_dim=32, local=True, K=3, coord_idx=coord_gen)

    def engine_reweight(step, it, events):
        bs = a.batch_size_step1 if step == 1 else a.batch_size_step2
        m = build(step)
        m.load_weights(ckpt(it, step))
        # `model1` must differ from the model passed in so `reweight` selects step2_models; for the
        # step-1 case we hand the same object in both slots deliberately -- see below.
        # `_engine_reweighter` is model-agnostic despite its step-2 naming: it sets `model1 = None`
        # and `step2_models = [m]`, and `reweight`'s selector is
        # `self.step1_models if model == self.model1 else self.step2_models` -- so a step-1 model
        # passed here is `!= None` and resolves to the single-model list. That is what makes it
        # legitimate to run the RECO leg through the committed step-2 helper: the helper only ever
        # evaluates the one model it was handed, with the engine's F3 cap and non-finite guard.
        of = _engine_reweighter(m, bs)
        return np.asarray(of.reweight(events, m, batch_size=bs), np.float64)

    # ---- the two pieces of pull_final, per omnifold.py:200 --------------------------------------
    # pull_final = push_{niter-2} * classifier1_{niter-1}(reco), each pinned to 1 off its own mask.
    print(f"\n[step1] (1/3) push_{{iter {niter-2}}} = model2 @ iter{niter-2} on gen  "
          f"[the push RunStep1 multiplied by, NOT the final one]")
    w2_prev = engine_reweight(2, niter - 2, (gen, gen_evt))
    push_prev = np.ones_like(stored_push)
    push_prev[pass_gen] = w2_prev[pass_gen]

    print(f"[step1] (2/3) classifier1 @ iter{niter-1} on reco")
    w1 = engine_reweight(1, niter - 1, (reco, reco_evt))
    inc1 = np.ones_like(stored_push)
    inc1[pass_reco] = w1[pass_reco]

    pull_final = push_prev * inc1

    print(f"[step1] (3/3) push_final = model2 @ iter{niter-1} on gen  [for a like-for-like compare]")
    w2_fin = engine_reweight(2, niter - 1, (gen, gen_evt))
    push_final = np.ones_like(stored_push)
    push_final[pass_gen] = w2_fin[pass_gen]

    # ---- the comparison the memo specifies -----------------------------------------------------
    with np.load(inputs_path, allow_pickle=True) as d:
        w_reco_raw = np.asarray(d["w_reco"], np.float64)[imc]
        w_truth_raw = np.asarray(d["w_truth"], np.float64)[imc]
    # Put the reco leg on the artifact's own normalization so ratios are comparable to the telemetry.
    scale = sum_w_reco_art / float(w_reco_raw[pass_reco].sum())
    w_reco = w_reco_raw * scale

    def wmean(x, w, m):
        return float((x[m] * w[m]).sum() / w[m].sum())

    out = {}
    for label, v in (("pull_final", pull_final), ("push_final", push_final),
                     ("push_prev", push_prev), ("increment1", inc1),
                     ("push_stored", stored_push)):
        out[label] = {
            "mean_w_reco_over_pass_reco": wmean(v, w_reco, pass_reco),
            "mean_w_truth_over_pass_gen": wmean(v, w_truth_raw, pass_gen),
        }
        out[label]["dev_vs_R_reco"] = out[label]["mean_w_reco_over_pass_reco"] / R - 1.0

    print("\n=== THE DECOMPOSITION ===")
    print(f"  R = {R:.6f}")
    print(f"  {'quantity':<14} {'mean_w_reco|pass_reco':>22} {'dev vs R':>10} "
          f"{'mean_w_truth|pass_gen':>22}")
    for label in ("push_stored", "push_final", "pull_final", "push_prev", "increment1"):
        o = out[label]
        print(f"  {label:<14} {o['mean_w_reco_over_pass_reco']:22.6f} "
              f"{o['dev_vs_R_reco']:+10.4f} {o['mean_w_truth_over_pass_gen']:22.6f}")
    rec["quantities"] = out
    rec["R"] = R

    pull_r = out["pull_final"]["mean_w_reco_over_pass_reco"]
    push_r = out["push_final"]["mean_w_reco_over_pass_reco"]
    print("\n=== PREDECLARED READING ===")
    if abs(pull_r / R - 1.0) < 0.02 and abs(push_r / R - 1.0) > 0.10:
        verdict = "STEP1_OK_LOSS_IN_STEP2_TRANSPORT"
        print("  pull satisfies the identity and push does not -> STEP 1 WORKS. The gate reads a")
        print("  step-2 quantity that no step ever normalized on the reco leg, so the identity it")
        print("  asserts is not one the algorithm guarantees.")
    elif abs(pull_r / R - 1.0) > 0.10 and abs(push_r / R - 1.0) > 0.10:
        verdict = "STEP1_UNDER_ACHIEVES"
        print("  BOTH legs are far from R -> step 1 genuinely under-achieves, and the defect is")
        print("  upstream of the leg choice.")
    else:
        verdict = "INDETERMINATE"
        print("  Neither predeclared branch fired cleanly; report the numbers and do not pick a")
        print("  story for them. See the table above.")
    rec["verdict"] = verdict
    print(f"\n[step1] VERDICT {verdict}")
    if rec["reconstruction_is_checkpoint_based"]:
        print("[step1] REMINDER: checkpoint-based reconstruction (Gate B(i) failed). Both legs are")
        print("        reconstructed identically, so the COMPARISON is sound; the absolute values")
        print("        are not the run's own weights.")
    if a.json:
        json.dump(rec, open(a.json, "w"), indent=1, default=jsonable)
        print(f"[step1] receipt -> {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
