#!/usr/bin/env python3
"""Gates A and B: can the SAVED checkpoint reproduce the artifact's own `weights_push`?

Joseph's memo, item 5, is a step-1 pull/push decomposition of the nominal's fold-forward failure
(`sum(w_reco*push|pass_reco)/sum(w_reco|pass_reco) = 0.746483` where the identity wants R = 1.124080).
The memo puts two gates in front of it, and this file is those gates ONLY. It computes no pull weight
and draws no conclusion about step 1: if the gates do not hold, the decomposition is not worth writing,
and a plausible-looking wrong number on the campaign's headline failure is worse than no number.

WHY THE GATES ARE NOT A FORMALITY HERE. Reading the engine while building this turned up a specific
reason Gate B may FAIL for a structural reason rather than a coding one:

    omnifold.py:272-275   ModelCheckpoint(model_name, save_best_only=True, save_weights_only=True)
    omnifold.py:266-268   EarlyStopping(patience=self.patience, restore_best_weights=True)
    omnifold.py:128       self.patience = early_stop            (engine default 10)

With `epochs=8` the patience-10 EarlyStopping can never fire, and Keras 2.15 restores best weights only
inside the `wait >= patience` stop branch -- so the model IN MEMORY at reweight time holds the LAST
epoch, while the file on disk holds the BEST-val-loss epoch. The nominal's own histories say those are
different for the checkpoint that matters:

    OmniFold_fe_nominal_nominal_iter2_step2.pkl   argmin(val_loss) = epoch 4 of 8   BEST_IS_LAST=False

`train_fullevent_nominal.py:497` stores `of.weights_push`, i.e. the LAST-epoch model's output, while
`inference_contract["step2_checkpoint"]` -- what `extract_fullevent_fps.py:253` loads -- is the
BEST-epoch file. If that is right, the artifact's weights and the extractor's cross section come from
two different networks, and `check_subsample_agreement` (`extract_fullevent_fps.py:347`, tol 1e-3) has
never run on this artifact to catch it: the only products in `products/pet/fullevent_fps/` are the
acceptance map and a closure.

SO THIS SCRIPT IS A REAL EXPERIMENT WITH TWO OUTCOMES, BOTH INFORMATIVE:
  * Gate B passes  -> the checkpoint IS the trained model, my reading above is wrong, and the memo's
                      decomposition can proceed on this footing.
  * Gate B fails   -> the reproduction is broken, and Gate A tells you WHICH KIND of broken. A2 in
                      particular isolates the failure `check_subsample_agreement`'s docstring names:
                      "a re-derived rather than reproduced normalization".

GATE A -- is this the same subsample, in the same input space?
  A1. Rebuild the loaders with the nominal's exact call and assert the rebuilt `imc` equals the stored
      `mc_indices` BIT-EXACTLY. This is the memo's Gate A.
  A2. Assert the rebuilt loader's `truth_norm_mean` / `truth_norm_std` equal the contract's bit-exactly.
      Stronger than the memo asked for and cheap: A1 proves the same ROWS, A2 proves the same
      normalization derived from them, and together they pin the step-2 input space. Reported
      separately so a failure names its own cause.

GATE B -- does the checkpoint reproduce the stored push? TWO PARTS, and part (ii) is not toleranced.
  B(i).  On `pass_gen`, rebuilt vs stored to `--tol-onshell` (default 1e-6).
  B(ii). Off `pass_gen`, the STORED push must be identically 1.0 -- `==`, no tolerance -- because
         `RunStep2` writes `new_weights = np.ones_like(...)` and fills only `[pass_gen]`
         (omnifold.py:218-220). A tolerance here would hide a real defect, and the memo says so.

The push is rebuilt through the ENGINE's own `reweight` via the committed extractor's
`_engine_reweighter`, so the F3 logit cap, the fail-closed non-finite check and the saturation
accounting are the same code that trained -- not a second implementation. The truth cloud and event
block come from the REBUILT LOADER (`mc.gen`, `mc.gen_evt`), which is what `RunStep2` itself evaluates,
so no preprocessing is re-implemented here at all. That is the whole reason Gate A runs first.

Writes a JSON receipt so the gate outputs can be handed to a fresh-context review, per the memo.

DEFECT IN THIS TOOL, FOUND BY USING IT (2026-08-08). The default batch size was 1000 while
`MultiFold.RunStep2` reweights at `BATCH_SIZE = 512`. A gate whose entire purpose is to reproduce a
computation must match that computation's configuration; any parameter it defaults differently is a FLOOR
on its own resolution. Worse, this tool's own Control 1 had already measured that floor at **2.901e-06**
between batch 1000 and 512 -- above the 1e-6 tolerance the gate declares -- so it was mis-specified
against a number it had itself produced.

The cost was real: on the 2026-08-08 re-run the gate reported `max rel dev 1.744800e-06` at batch 1000
and I nearly recorded a repaired pipeline as a residual failure. At batch 512 the deviation is
**identically 0.000000e+00 at every percentile** -- bit-exact over all 1,999,928 `pass_gen` rows. The
tolerance was never needed. Default corrected to 512; the tolerance is UNCHANGED at 1e-6 and was not
touched (BEN-072).

Usage (GPU node -- 2M rows of PET inference):
  srun -A m3246_g -q interactive -C gpu -N1 -n1 -c32 --gpus=1 -t 60 \
      python3 -u gate_ab_push_provenance.py --json GATE_AB.json
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# CANONICAL as of the 2026-08-12 designation promotion of job 56563761 (the annealed nominal).
# Promotion here is by DESIGNATION, not by moving bytes: artifacts embed an ABSOLUTE
# inference_contract["weights_folder"], so relocating one silently re-points it at whatever now
# occupies its old path (BEN-133, with a live instance in
# fullevent_nominal/superseded-20260806/NOTE.md). Overridable with --artifact; the pre-anneal  # NS-EXEMPT: prose, not a reference
# artifact remains at fullevent_nominal/ and its diagnostics still name it explicitly.  # NS-EXEMPT: prose, not a reference
DEFAULT_ART = os.path.join(HERE, "fullevent_nominal_annealed",
                           "pet_fullevent_nominal_weights.npz")


def jsonable(o):
    if isinstance(o, (np.floating, float)):
        return float(o)
    if isinstance(o, (np.integer, int)):
        return int(o)
    if isinstance(o, (np.bool_, bool)):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--artifact", default=DEFAULT_ART)
    ap.add_argument("--json", default=None, help="write the gate receipt here")
    ap.add_argument("--tol-onshell", type=float, default=1e-6,
                    help="Gate B(i) relative tolerance on pass_gen rows. NOT to be raised to make "
                         "the gate pass -- if it fails, report the failure.")
    ap.add_argument("--batch-size", type=int, default=512,
                    help="engine reweight batch. MUST match MultiFold.BATCH_SIZE (512), which is what "
                         "RunStep2 reweights at. See the note below on why the default was wrong.")
    # --- the two controls that turn "leading explanation" into "only surviving explanation" -------
    # Run 1 (2026-08-07, log gate_ab_20260807.log) measured Gate B(i) failing at max rel dev 0.866
    # with Gate A bit-exact, which excludes a wrong subsample and a wrong input space. Two knobs
    # remain that are MINE rather than the pipeline's, and both are excluded by measurement here:
    ap.add_argument("--batch-size-control", type=int, default=None,
                    help="repeat Gate B(i) at a second batch size, to measure how much of any "
                         "deviation is float32 batching non-associativity rather than a weights "
                         "difference. On 2026-08-07 it measured 2.901e-06 between 1000 and 512 -- the "
                         "number that later explained a 1.744e-06 near-miss and forced the default to 512.")
    ap.add_argument("--extra-artifact", default=None,
                    help="repeat Gate B for a SECOND artifact sharing this subsample (the matched "
                         "floor run). An independent training reproducing the same "
                         "large-per-event / tiny-aggregate signature makes it a structural property "
                         "of how checkpoints are saved, not a one-off in this run.")
    a = ap.parse_args()

    rec = {"gate": "A+B push provenance", "artifact": os.path.abspath(a.artifact),
           "tol_onshell": a.tol_onshell, "batch_size": a.batch_size}

    with np.load(a.artifact, allow_pickle=True) as d:
        stored_push = np.asarray(d["weights_push"], np.float64)
        stored_imc = np.asarray(d["mc_indices"])
        contract = d["inference_contract"].item()
        policy = d["seed_policy"].item()
        target_meta = d["target"].item()
        inputs_path = str(d["inputs_path"])
        ff = {"sum_w_push_reco": float(d["fold_forward_sum_w_push_reco"]),
              "sum_w_reco": float(d["fold_forward_sum_w_reco"]),
              "n_pass_reco": int(d["fold_forward_n_pass_reco"])}
    ff["ratio"] = ff["sum_w_push_reco"] / ff["sum_w_reco"]
    rec["stored"] = {"n_rows": int(stored_push.size), "fold_forward": ff, "policy": policy}
    print(f"[gate] artifact {a.artifact}")
    print(f"[gate] stored push {stored_push.size} rows; fold-forward ratio {ff['ratio']:.6f}")

    import train_fullevent_nominal as T
    import fullevent_fps_dataloader as fe

    target_npy = target_meta.get("consumed_precomputed_target")
    print(f"[gate] rebuilding loaders: max_events={policy['train_events']} "
          f"seed={policy['subsample_seed']} bkg_mode={T.BKG_MODE} target={target_npy}")
    # EXACTLY train_fullevent_nominal.py:358-360. Any deviation here (mc-only, a different target,
    # a different max_events) can move the subsample or the normalization, which is precisely what
    # Gate A exists to detect -- so the call is copied, not adapted.
    _data, mc, imc, _cr, _cg, meta = fe.build_fullevent_loaders(
        inputs_path, max_events=int(policy["train_events"]),
        seed=int(policy["subsample_seed"]), bkg_mode=T.BKG_MODE,
        precomputed_target=target_npy)
    imc = np.asarray(imc)

    # ---------------- GATE A ----------------------------------------------------------------
    print("\n=== GATE A: same subsample, same input space? ===")
    a1 = bool(imc.shape == stored_imc.shape and np.array_equal(imc, stored_imc))
    n_diff = int((imc != stored_imc).sum()) if imc.shape == stored_imc.shape else -1
    print(f"  A1 mc_indices bit-exact: {a1}   (shapes {imc.shape} vs {stored_imc.shape}, "
          f"differing rows {n_diff})")

    got_mu = np.asarray(meta["truth_norm_mean"], np.float64)
    got_sd = np.asarray(meta["truth_norm_std"], np.float64)
    want_mu = np.asarray(contract["truth_norm_mean"], np.float64)
    want_sd = np.asarray(contract["truth_norm_std"], np.float64)
    a2 = bool(np.array_equal(got_mu, want_mu) and np.array_equal(got_sd, want_sd))
    print(f"  A2 truth normalization bit-exact: {a2}")
    print(f"     mean rebuilt {got_mu.tolist()}  contract {want_mu.tolist()}")
    print(f"     std  rebuilt {got_sd.tolist()}  contract {want_sd.tolist()}")
    if not a2:
        print(f"     max |delta| mean {np.abs(got_mu-want_mu).max():.3e}  "
              f"std {np.abs(got_sd-want_sd).max():.3e}")
    rec["gate_A"] = {"A1_mc_indices_bit_exact": a1, "A1_differing_rows": n_diff,
                     "A2_truth_norm_bit_exact": a2,
                     "truth_norm_mean_rebuilt": got_mu.tolist(),
                     "truth_norm_mean_contract": want_mu.tolist(),
                     "truth_norm_std_rebuilt": got_sd.tolist(),
                     "truth_norm_std_contract": want_sd.tolist()}
    if not (a1 and a2):
        rec["verdict"] = "GATE_A_FAILED"
        if a.json:
            json.dump(rec, open(a.json, "w"), indent=1, default=jsonable)
        raise SystemExit("[gate] GATE A FAILED -- the rebuilt subsample or its input space is not the "
                         "trained one, so nothing downstream would be about the same estimator. "
                         "Refusing to run Gate B (fail closed).")
    print("  GATE A PASSED -- same rows, same normalization.")

    # ---------------- GATE B ----------------------------------------------------------------
    pass_gen = np.asarray(mc.pass_gen).astype(bool)
    print(f"\n=== GATE B: does the SAVED checkpoint reproduce the stored push? ===")
    print(f"  pass_gen {int(pass_gen.sum())} of {pass_gen.size}")

    # B(ii) FIRST: it needs no model, no GPU, and no tolerance. If the stored push is not exactly 1.0
    # off pass_gen then the artifact does not match the engine that supposedly wrote it, and that is
    # worth knowing before spending 2M rows of inference.
    off = stored_push[~pass_gen]
    n_off = int(off.size)
    n_exact = int((off == 1.0).sum())
    bii = bool(n_off == n_exact)
    print(f"  B(ii) stored push == 1.0 EXACTLY on !pass_gen: {n_exact}/{n_off}  -> {bii}")
    if n_off and not bii:
        print(f"        max |push-1| off-shell {np.abs(off-1.0).max():.3e}")
    rec["gate_B"] = {"n_pass_gen": int(pass_gen.sum()), "n_off_shell": n_off,
                     "Bii_off_shell_exactly_one": bii, "Bii_n_exactly_one": n_exact}

    from extract_fullevent_fps import build_step2_model, _engine_reweighter
    ckpt = contract["step2_checkpoint"]
    print(f"  loading step-2 checkpoint {ckpt}")
    rec["gate_B"]["step2_checkpoint"] = ckpt
    rec["gate_B"]["step2_checkpoint_exists"] = os.path.exists(ckpt)
    model2 = build_step2_model(contract)
    of = _engine_reweighter(model2, a.batch_size)

    print(f"  running the ENGINE reweight on {pass_gen.size} rows (batch {a.batch_size}) ...")
    w = np.asarray(of.reweight((np.asarray(mc.gen), np.asarray(mc.gen_evt)), model2,
                               batch_size=a.batch_size), np.float64)
    # Mirror RunStep2 exactly: ones everywhere, classifier value only on pass_gen.
    rebuilt = np.ones_like(stored_push)
    rebuilt[pass_gen] = w[pass_gen]

    on_r, on_s = rebuilt[pass_gen], stored_push[pass_gen]
    dev = np.abs(on_r - on_s) / np.maximum(np.abs(on_s), 1e-12)
    worst = float(dev.max()) if dev.size else 0.0
    med = float(np.median(dev)) if dev.size else 0.0
    bi = bool(worst <= a.tol_onshell)
    print(f"  B(i)  on pass_gen: max rel dev {worst:.6e}  median {med:.6e}  "
          f"tol {a.tol_onshell:.0e}  -> {bi}")
    for q in (50, 90, 99, 99.9):
        print(f"        rel dev p{q}: {np.percentile(dev, q):.6e}")
    print(f"        stored  mean {on_s.mean():.6f}  min {on_s.min():.6f}  max {on_s.max():.6f}")
    print(f"        rebuilt mean {on_r.mean():.6f}  min {on_r.min():.6f}  max {on_r.max():.6f}")
    rec["gate_B"].update({
        "Bi_max_rel_dev": worst, "Bi_median_rel_dev": med, "Bi_pass": bi,
        "Bi_rel_dev_p90": float(np.percentile(dev, 90)),
        "Bi_rel_dev_p99": float(np.percentile(dev, 99)),
        "stored_mean_on_shell": float(on_s.mean()), "rebuilt_mean_on_shell": float(on_r.mean()),
        "stored_min": float(on_s.min()), "stored_max": float(on_s.max()),
        "rebuilt_min": float(on_r.min()), "rebuilt_max": float(on_r.max())})

    # ---- CONTROL 1: is the deviation mine, via float32 batching non-associativity? ---------------
    if a.batch_size_control:
        wc = np.asarray(of.reweight((np.asarray(mc.gen), np.asarray(mc.gen_evt)), model2,
                                    batch_size=a.batch_size_control), np.float64)
        rc = np.ones_like(stored_push)
        rc[pass_gen] = wc[pass_gen]
        d_batch = float((np.abs(rc[pass_gen] - on_r) /
                         np.maximum(np.abs(on_r), 1e-12)).max())
        d_stored = float((np.abs(rc[pass_gen] - on_s) /
                          np.maximum(np.abs(on_s), 1e-12)).max())
        print(f"\n=== CONTROL 1: batch size {a.batch_size} vs {a.batch_size_control} ===")
        print(f"  checkpoint@{a.batch_size} vs checkpoint@{a.batch_size_control}: "
              f"max rel dev {d_batch:.3e}")
        print(f"  checkpoint@{a.batch_size_control} vs STORED:                 "
              f"max rel dev {d_stored:.3e}")
        print(f"  -> batching accounts for {100.0*d_batch/max(worst,1e-30):.4f}% of the "
              f"{worst:.3e} Gate B(i) deviation")
        rec["control_batch"] = {"batch_a": a.batch_size, "batch_b": a.batch_size_control,
                                "max_rel_dev_between_batches": d_batch,
                                "max_rel_dev_b_vs_stored": d_stored,
                                "fraction_of_gate_deviation": d_batch / max(worst, 1e-30)}
        del wc, rc

    # ---- CONTROL 2: does an INDEPENDENT training show the same signature? ------------------------
    if a.extra_artifact:
        print(f"\n=== CONTROL 2: repeat Gate B on {a.extra_artifact} ===")
        with np.load(a.extra_artifact, allow_pickle=True) as d2:
            push2 = np.asarray(d2["weights_push"], np.float64)
            imc2 = np.asarray(d2["mc_indices"])
            contract2 = d2["inference_contract"].item()
        same_rows = bool(np.array_equal(imc2, stored_imc))
        print(f"  shares this subsample bit-exactly: {same_rows}")
        rec["control_extra"] = {"artifact": os.path.abspath(a.extra_artifact),
                                "shares_subsample": same_rows}
        if not same_rows:
            print("  -> different subsample; the rebuilt loader does not apply, SKIPPING rather "
                  "than reporting a number about the wrong rows")
        else:
            m2b = build_step2_model(contract2)
            of2 = _engine_reweighter(m2b, a.batch_size)
            w2 = np.asarray(of2.reweight((np.asarray(mc.gen), np.asarray(mc.gen_evt)), m2b,
                                         batch_size=a.batch_size), np.float64)
            r2 = np.ones_like(push2)
            r2[pass_gen] = w2[pass_gen]
            o2r, o2s = r2[pass_gen], push2[pass_gen]
            d2v = np.abs(o2r - o2s) / np.maximum(np.abs(o2s), 1e-12)
            off2 = push2[~pass_gen]
            print(f"  B(ii) stored push == 1.0 exactly off-shell: "
                  f"{int((off2 == 1.0).sum())}/{int(off2.size)}")
            print(f"  B(i)  max rel dev {float(d2v.max()):.6e}  median "
                  f"{float(np.median(d2v)):.6e}  p90 {float(np.percentile(d2v,90)):.6e}")
            print(f"        stored mean {o2s.mean():.6f}   rebuilt mean {o2r.mean():.6f}   "
                  f"aggregate rel gap {abs(o2r.mean()/o2s.mean()-1):.3e}")
            rec["control_extra"].update({
                "Bii_n_exactly_one": int((off2 == 1.0).sum()), "n_off_shell": int(off2.size),
                "Bi_max_rel_dev": float(d2v.max()),
                "Bi_median_rel_dev": float(np.median(d2v)),
                "Bi_rel_dev_p90": float(np.percentile(d2v, 90)),
                "stored_mean": float(o2s.mean()), "rebuilt_mean": float(o2r.mean()),
                "aggregate_rel_gap": float(abs(o2r.mean() / o2s.mean() - 1))})
            print("  -> a second, independently trained run showing the same signature (large "
                  "per-event, tiny aggregate) makes this structural, not a one-off.")
            del w2, r2

    # What the discrepancy, if any, would do to the number the campaign actually reports. This is the
    # consequence that matters and it is free once both vectors are in hand.
    with np.load(inputs_path, allow_pickle=True) as d:
        w_reco = np.asarray(d["w_reco"], np.float64)[imc]
        pass_reco = np.asarray(d["pass_reco"]).astype(bool)[imc]
    # The artifact's own sum_w_reco is the RENORMALIZED leg; recover the scale from it so the
    # comparison below is in the same units the gate reports, rather than a differently-normalized one.
    raw_sum = float(w_reco[pass_reco].sum())
    scale = ff["sum_w_reco"] / raw_sum if raw_sum else 1.0
    wr = w_reco * scale
    r_stored = float((wr[pass_reco] * stored_push[pass_reco]).sum() / wr[pass_reco].sum())
    r_rebuilt = float((wr[pass_reco] * rebuilt[pass_reco]).sum() / wr[pass_reco].sum())
    print(f"\n=== consequence for the reported fold-forward ratio ===")
    print(f"  artifact telemetry            {ff['ratio']:.6f}")
    print(f"  recomputed from stored push   {r_stored:.6f}  (checks my w_reco handling)")
    print(f"  recomputed from CHECKPOINT    {r_rebuilt:.6f}")
    print(f"  R (required)                  1.124080")
    rec["consequence"] = {"ratio_artifact": ff["ratio"], "ratio_from_stored": r_stored,
                          "ratio_from_checkpoint": r_rebuilt,
                          "w_reco_renorm_scale": scale}

    verdict = "GATE_AB_PASSED" if (bi and bii) else (
        "GATE_B_FAILED_ONSHELL" if not bi else "GATE_B_FAILED_OFFSHELL")
    rec["verdict"] = verdict
    print(f"\n[gate] VERDICT {verdict}")
    if not bi:
        print("[gate] Gate B(i) FAILED. Gate A passed, so the subsample and the input space ARE the")
        print("       trained ones -- this is NOT a preprocessing failure. The leading explanation is")
        print("       the best-vs-last checkpoint gap documented in this file's header. Do NOT raise")
        print("       --tol-onshell; the deviation is the result.")
    if a.json:
        json.dump(rec, open(a.json, "w"), indent=1, default=jsonable)
        print(f"[gate] receipt -> {a.json}")
    # A failed gate is a successful measurement here, so exit 0 when the receipt was written; the
    # verdict field is the machine-readable outcome. Exit non-zero only if we could not measure.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
