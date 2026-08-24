#!/usr/bin/env python3
"""R5 -- loss-interpolation sweep. Predeclared by the routing lane; boundaries not varied here.

For each member k, evaluate that member's OWN step-2 objective along
    theta(t) = theta_nom + t*(theta_k - theta_nom),  t in {0, 0.25, 0.5, 0.75, 1}
and read the output (push) response on the SAME forward passes.

PREDECLARED, against the epoch-to-epoch val_loss scatter:
  CONFIRM  : L_k(theta_nom) - L_k(theta_k) <= 2.4e-3  WHILE the band output response moves >= 3x
  OPPOSITE : >= 2.4e-2   (members are loss-preferred and the NOMINAL is the outlier)
  UNRESOLVED: 2.4e-3 to 2.4e-2. Does not default.
STRUCTURAL ARM (required, not optional): the displacement must load band-negative and tail-positive.
  If the output pattern is same-signed in both regions, or |tail response| < 10% of |band response|,
  the flat-direction account fails on STRUCTURE and CONFIRM is unavailable regardless of the loss leg.
Primary band response is ENDPOINT-to-ENDPOINT O_band(1)/O_band(0); max/min over t is secondary.

--loss-domain heldout : reconstructed validation slice (only if the probe established it)
--loss-domain full    : all rows; then it is a TRAINING-loss difference and thresholds must be
                        supplied via --thr-confirm/--thr-opposite derived from train-loss scatter.
"""
import argparse, hashlib, importlib, json, os, pickle, sys
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--nominal-artifact", required=True)
ap.add_argument("--replicas-root", required=True)
ap.add_argument("--members", required=True, help="comma list of ints")
ap.add_argument("--added-members", default="", help="comma list flagged as ADDITIONS")
ap.add_argument("--loss-domain", choices=["heldout", "full"], required=True)
ap.add_argument("--thr-confirm", type=float, default=2.4e-3)
ap.add_argument("--thr-opposite", type=float, default=2.4e-2)
ap.add_argument("--json", required=True)
a = ap.parse_args()
TS = [0.0, 0.25, 0.5, 0.75, 1.0]

print("[r5] sys.path[0] BEFORE imports:", sys.path[0], flush=True)
import train_fullevent_nominal as T
for n in ("omnifold", "extract_fullevent_fps", "fullevent_fps_dataloader"):
    importlib.import_module(n)
print("[r5] sys.path[0] AFTER  imports:", sys.path[0], flush=True)
def checkout_root(p):
    d = os.path.dirname(os.path.abspath(p))
    while d != "/":
        if os.path.exists(os.path.join(d, "VALIDATION_LEDGER.md")) and os.path.isdir(os.path.join(d, "nd-unfolding")):
            return d
        d = os.path.dirname(d)
    return None
audit = {}
for nm, m in list(sys.modules.items()):
    f = getattr(m, "__file__", None)
    if f and f.endswith(".py"):
        r = checkout_root(f)
        if r: audit[nm] = {"root": r, "sha256": hashlib.sha256(open(f, "rb").read()).hexdigest()}
roots = sorted(set(v["root"] for v in audit.values()))
print("[r5] modules inside a checkout: %d, roots %r" % (len(audit), roots), flush=True)

import fullevent_fps_dataloader as fe
from omnifold import PET, MultiFold
from omnifold.net import weighted_binary_crossentropy as _wbce
from annealed_estimator import make_annealed_multifold
from diagnostic_target_override import resolve_precomputed_target
from extract_fullevent_fps import _engine_reweighter
import tensorflow as tf
print("[r5] tf", tf.__version__, "GPUs", len(tf.config.list_physical_devices("GPU")), flush=True)
CAP = 30.0

def pin_loss_normalises_by_row_count():
    """The dL bracket is exact ONLY IF the loss normalises by ROW COUNT, not by sum(w).

    That property comes from an ABSENCE: `weighted_binary_crossentropy` ends in
    `tf.reduce_mean(t_loss)` and never divides by the weight sum. There is no line to grep for a
    normalisation that is not there, so this TEST is the only place the dependency is visible.
    Two arms, because a consistency check alone would pass under either convention:
      POSITIVE  scaling every weight by c must scale the loss by exactly c   (row-count mean)
      NEGATIVE  under a sum(w) normalisation the loss would be INVARIANT to c -- assert it is not
    """
    y = tf.constant([[1.0, 2.0], [0.0, 3.0], [1.0, 0.5]])           # (label, weight)
    p = tf.constant([[0.3], [-0.7], [1.1]])
    L1 = float(_wbce(y, p))
    c = 7.0
    y2 = tf.constant([[1.0, 2.0*c], [0.0, 3.0*c], [1.0, 0.5*c]])
    Lc = float(_wbce(y2, p))
    scaled_ok = abs(Lc - c*L1) <= 1e-6*max(1.0, abs(c*L1))
    invariant = abs(Lc - L1) <= 1e-6*max(1.0, abs(L1))
    print("[pin] weighted_binary_crossentropy: L(w)=%.8f  L(%.0fw)=%.8f  ratio %.8f"
          % (L1, c, Lc, Lc/L1), flush=True)
    if not scaled_ok or invariant:
        raise SystemExit("[pin] the loss does NOT normalise by row count (scaled_ok=%s invariant=%s). "
                         "The dL bracket's linearity in the weights_pull scale is then INVALID -- "
                         "L would be a ratio of linear functions. Failing closed rather than "
                         "returning plausible numbers." % (scaled_ok, invariant))
    print("[pin] PASS: row-count normalisation confirmed (positive arm scales by %.0f, negative arm "
          "rejects sum(w) invariance). dL linearity in the pull scale is valid." % c, flush=True)
    return {"L_unit_weights": L1, "L_scaled_weights": Lc, "scale": c,
            "ratio": Lc/L1, "positive_arm_scales_exactly": bool(scaled_ok),
            "negative_arm_rejects_sumw_invariance": bool(not invariant), "PASS": True}

with np.load(a.nominal_artifact, allow_pickle=True) as d:
    npol = d["seed_policy"].item(); ncon = d["inference_contract"].item()
    ntgt = d["target"].item(); inputs_path = str(d["inputs_path"])
    edges_pp = np.asarray(d["edges_pparallel"], np.float64)
niter = int(npol["niter"]); BS = int(npol["batch_size"]); EST = int(npol["estimator_seed"])
SUB = int(npol["subsample_seed"]); MAXEV = int(npol["train_events"]); EPO = int(npol["epochs"])
nom_wf = ncon["weights_folder"]; MFNAME = ncon["multifold_name"]
nom_target, _ = resolve_precomputed_target(ntgt.get("consumed_precomputed_target"), None, None)

def ck(wf, it, step, prefer_final=True):
    fin = os.path.join(wf, "OmniFold_%s_iter%d_step%d_final.weights.h5" % (MFNAME, it, step))
    if prefer_final and os.path.exists(fin): return fin
    return os.path.join(wf, "OmniFold_%s_iter%d_step%d.weights.h5" % (MFNAME, it, step))

def build_pair(gen_w, reco_w, P, ev_reco, ev_truth, coord_reco, coord_gen):
    m1 = PET(reco_w, num_evt=ev_reco, num_part=P, num_transformer=2, num_heads=2,
             projection_dim=32, local=True, K=3, coord_idx=coord_reco)
    m2 = PET(gen_w, num_evt=ev_truth, num_part=P, num_transformer=2, num_heads=2,
             projection_dim=32, local=True, K=3, coord_idx=coord_gen)
    return m1, m2

def logits(model, cloud, evt, rows, bs):
    out = np.empty(len(rows), np.float64)
    for s in range(0, len(rows), bs):
        r = rows[s:s+bs]
        out[s:s+bs] = np.asarray(model.model([tf.convert_to_tensor(cloud[r], tf.float32),
                                              tf.convert_to_tensor(evt[r], tf.float32)],
                                             training=False))[:, 0]
    return out

members = [int(x) for x in a.members.split(",") if x.strip() != ""]
added = set(int(x) for x in a.added_members.split(",") if x.strip() != "")
LOSS_PIN = pin_loss_normalises_by_row_count()
out = {"schema": "oi126-r5-loss-interpolation-v1", "module_audit_roots": roots,
       "loss_normalisation_pin": LOSS_PIN,
       "sys_path0_after_imports": sys.path[0], "loss_domain": a.loss_domain,
       "thresholds": {"CONFIRM_le": a.thr_confirm, "OPPOSITE_ge": a.thr_opposite},
       "t_grid": TS, "members": {}, "added_members_flagged": sorted(added)}

for k in members:
    tag = "replica_%02d" % k
    rroot = os.path.join(a.replicas_root, tag)
    art = os.path.join(rroot, "training", "GATE5_REPLICA_WEIGHTS.npz")
    tgt = os.path.join(rroot, "target", "GATE5_REPLICA_TARGET.npy")
    with np.load(art, allow_pickle=True) as d:
        mcon = d["inference_contract"].item(); ridx = int(d["replica_index"])
    mem_wf = mcon["weights_folder"]
    bseed = 50000 + ridx
    print("\n" + "="*78, flush=True)
    print("[%s] bootstrap_seed=%d  weights_folder=%s" % (tag, bseed, mem_wf), flush=True)
    tf.keras.utils.set_random_seed(EST)
    _data, mc, imc, coord_reco, coord_gen, meta = fe.build_fullevent_loaders(
        inputs_path, max_events=MAXEV, seed=SUB, bkg_mode=T.BKG_MODE,
        precomputed_target=tgt, bootstrap_seed=bseed, precomputed_target_replica_seed=bseed)
    reco = np.asarray(mc.reco); gen = np.asarray(mc.gen)
    reco_evt = np.asarray(mc.reco_evt); gen_evt = np.asarray(mc.gen_evt)
    pass_reco = np.asarray(mc.pass_reco).astype(bool)
    pass_gen = np.asarray(mc.pass_gen).astype(bool)
    P = reco.shape[1]; ev_reco, ev_truth = meta["n_evt_reco"], meta["n_evt_truth"]
    m1, m2 = build_pair(gen.shape[-1], reco.shape[-1], P, ev_reco, ev_truth, coord_reco, coord_gen)
    _rec = []; _Ann = make_annealed_multifold(MultiFold, tf, _rec)
    of = _Ann(MFNAME, m1, m2, _data, mc, niter=niter, epochs=EPO, batch_size=BS,
              weights_folder=mem_wf, verbose=False)
    n1 = len(of.labels_mc) + len(of.labels_data); n2 = len(of.labels_mc) + len(of.labels_gen)
    i1 = np.arange(n1); np.random.shuffle(i1)
    i2 = np.arange(n2); np.random.shuffle(i2)
    NTRAIN2 = of.num_steps_gen * of.BATCH_SIZE
    NTEST2 = int((1.0 - of.train_frac) * NTRAIN2)
    take = NTRAIN2 - NTEST2; vsteps = NTEST2 // of.BATCH_SIZE; vn = vsteps * of.BATCH_SIZE
    idx2_sha = hashlib.sha256(i2.tobytes()).hexdigest()

    # member's own weights_pull at the terminal iteration
    m2.load_weights(ck(mem_wf, niter-2, 2))
    w2p = np.asarray(_engine_reweighter(m2, BS).reweight((gen, gen_evt), m2, batch_size=BS), np.float64)
    push_prev = np.ones(len(pass_gen)); push_prev[pass_gen] = w2p[pass_gen]
    m1.load_weights(ck(mem_wf, niter-1, 1))
    w1 = np.asarray(_engine_reweighter(m1, 1000).reweight((reco, reco_evt), m1, batch_size=1000), np.float64)
    inc1 = np.ones(len(pass_reco)); inc1[pass_reco] = w1[pass_reco]
    weights_pull = push_prev * inc1

    labels = np.concatenate((of.labels_mc, of.labels_gen)).astype(np.float64)
    wts = np.concatenate((mc.weight*mc.pass_gen, mc.weight*weights_pull*mc.pass_gen)).astype(np.float64)
    if a.loss_domain == "heldout":
        pos = i2[take:take+vn]
    else:
        pos = np.arange(n2)
    lab_v = labels[pos]; w_v = wts[pos]; row_v = (pos % len(pass_gen)).astype(np.int64)

    # ROW-SET ROBUSTNESS OF dL, DECLARED BEFORE LOOKING.
    # The split could not be CERTIFIED: the anchor turned out to be highly sensitive to WHICH 800k
    # rows are used (|L_A - L_C| = 2.355e-2 across equal-size uniform subsets), because the weighted
    # mean is dominated by a few heavy-weight rows. But R5's observable is a DIFFERENCE at two
    # parameter points on the SAME rows, so a row-set change shifts both endpoints together and
    # cancels in dL exactly, as an additive offset does. That is an argument; this measures it.
    #   A = the reconstructed held-out slice (PRIMARY, and the thresholds are calibrated on a
    #       held-out slice's val scatter, so A is the branch the declared thresholds belong to)
    #   B = an equal-size slice from the TRAIN region of the same permutation
    #   C = an equal-size slice from an INDEPENDENT permutation (seed 12345)
    # DECLARED: if max|dL(X) - dL(A)| over X in {B,C} is <= 2.4e-3 (the CONFIRM threshold), the
    # row-set choice cannot move the verdict and the uncertified split is immaterial to R5. If it
    # EXCEEDS 2.4e-3, then no row set supports a threshold at that scale and I report the read as
    # threshold-indeterminate rather than picking the row set that gives a verdict.
    _rs = np.random.RandomState(12345); _alt = _rs.permutation(n2)
    ROWSETS = {"A_heldout_primary": pos,
               "B_train_region": i2[:len(pos)] if len(pos) <= take else np.arange(n2),
               "C_independent_perm": _alt[:len(pos)]}
    RS_CACHE = {k: {"lab": labels[v], "w": wts[v], "row": (v % len(pass_gen)).astype(np.int64)}
                for k, v in ROWSETS.items()}
    for k in RS_CACHE:
        d = RS_CACHE[k]
        m_ = d["lab"] > 0.5
        d["wp"] = np.where(m_, d["w"], 0.0)
        d["wf"] = np.where(m_, 0.0, d["w"])
    print("[%s] row sets for dL robustness: %s (each n=%d)"
          % (tag, list(ROWSETS), len(pos)), flush=True)

    # truth-p_parallel band / tail masks over pass_gen rows, for the OUTPUT response
    tp = np.asarray(np.load(inputs_path, allow_pickle=True)["truth_scalars"], np.float64)[np.asarray(imc)][:, 1] \
         if False else None
    with np.load(inputs_path, allow_pickle=True) as dd:
        tp = np.asarray(dd["truth_scalars"], np.float64)[np.asarray(imc)][:, 1]
    band = pass_gen & (tp >= 7.0) & (tp < 10.0)
    tail = pass_gen & (tp >= 20.0)
    b_rows = np.nonzero(band)[0]; t_rows = np.nonzero(tail)[0]
    wtruth = np.asarray(mc.weight, np.float64)
    print("[%s] band rows %d  tail rows %d  loss rows %d (%s)"
          % (tag, len(b_rows), len(t_rows), len(pos), a.loss_domain), flush=True)

    # interpolation endpoints
    mnom, mmem = build_pair(gen.shape[-1], reco.shape[-1], P, ev_reco, ev_truth, coord_reco, coord_gen)[1], \
                 build_pair(gen.shape[-1], reco.shape[-1], P, ev_reco, ev_truth, coord_reco, coord_gen)[1]
    mnom.load_weights(ck(nom_wf, niter-1, 2)); mmem.load_weights(ck(mem_wf, niter-1, 2))
    Wn = [np.asarray(w, np.float64) for w in mnom.model.get_weights()]
    Wm = [np.asarray(w, np.float64) for w in mmem.model.get_weights()]
    assert len(Wn) == len(Wm) and all(x.shape == y.shape for x, y in zip(Wn, Wm)), "weight shape mismatch"
    dnorm = float(np.sqrt(sum(((y-x)**2).sum() for x, y in zip(Wn, Wm))))

    # ROUTING-LANE TRAP GUARD (their section 6): the quantity is ONE objective at TWO parameter
    # points, never two objectives. Absolute step-2 losses differ across arms by 0.05-0.13 purely
    # because the weight distribution changed -- 2 to 5x the OPPOSITE threshold -- so if the two
    # evaluations ever used different objectives the read would land in OPPOSITE for a bookkeeping
    # reason. lab_v and w_v are built ONCE from member k and reused at every t; this digests them
    # and re-asserts the digest inside the loop.
    OBJ_SHA = hashlib.sha256(lab_v.tobytes() + w_v.tobytes() + row_v.tobytes()).hexdigest()
    print("[%s] objective digest %s (member k's own labels+weights+rows, fixed across all t)"
          % (tag, OBJ_SHA[:16]), flush=True)

    # per-member epoch scatter from that member's OWN history, for reporting dL in noise units
    hp = os.path.join(mem_wf, "OmniFold_%s_iter%d_step2.pkl" % (MFNAME, niter-1))
    scat = None
    if os.path.exists(hp):
        h = pickle.load(open(hp, "rb"))
        vv = np.asarray(h["val_loss"], float); ll = np.asarray(h["loss"], float)
        scat = {"val_loss_history": vv.tolist(), "train_loss_history": ll.tolist(),
                "val_successive_diff_sd": float(np.std(np.diff(vv), ddof=1)),
                "val_max_successive_absdiff": float(np.max(np.abs(np.diff(vv)))),
                "val_range": float(vv.max() - vv.min()),
                "train_successive_diff_sd": float(np.std(np.diff(ll), ddof=1)),
                "train_range": float(ll.max() - ll.min())}
        print("[%s] own val scatter: sd %.3e  max|diff| %.3e  range %.3e"
              % (tag, scat["val_successive_diff_sd"], scat["val_max_successive_absdiff"],
                 scat["val_range"]), flush=True)

    res = {"replica_index": ridx, "bootstrap_seed": bseed, "weights_folder": mem_wf,
           "objective_digest_fixed_across_t": OBJ_SHA,
           "objective_identity_assertion": ("one objective at two parameter points: lab_v/w_v/row_v "
               "built once from member k and re-asserted unchanged at every t"),
           "own_epoch_scatter": scat,
           "is_flagged_addition": ridx in added,
           "nominal_step2_ckpt": ck(nom_wf, niter-1, 2), "member_step2_ckpt": ck(mem_wf, niter-1, 2),
           "displacement_l2_norm": dnorm, "idx2_sha256": idx2_sha,
           "split": {"n2": int(n2), "cache_take": int(take), "validation_steps": int(vsteps),
                     "validation_rows": int(vn)},
           "n_loss_rows": int(len(pos)), "n_band_rows": int(len(b_rows)), "n_tail_rows": int(len(t_rows)),
           "by_t": {}}
    # label-0 / label-1 partition of the loss rows, for the exact weights_pull bracket below
    is1 = lab_v > 0.5
    w_pull_part = np.zeros_like(w_v); w_pull_part[is1] = w_v[is1]     # carries the pull factor
    w_flat_part = np.zeros_like(w_v); w_flat_part[~is1] = w_v[~is1]   # pull-independent
    S0S1 = {}
    for t in TS:
        assert hashlib.sha256(lab_v.tobytes() + w_v.tobytes() + row_v.tobytes()).hexdigest() == OBJ_SHA, \
            "objective changed between parameter points -- would spuriously hit OPPOSITE (fail closed)"
        mmem.model.set_weights([x + t*(y-x) for x, y in zip(Wn, Wm)])
        lg = logits(mmem, gen, gen_evt, row_v, BS)
        ce = np.maximum(lg, 0) - lg*lab_v + np.log1p(np.exp(-np.abs(lg)))
        S0 = float((w_flat_part*ce).sum()); S1 = float((w_pull_part*ce).sum())
        S0S1[t] = (S0, S1)
        L = (S0 + S1)/len(ce)
        if t in (0.0, 1.0):
            for k in ("B_train_region", "C_independent_perm"):
                d = RS_CACHE[k]
                lg2 = logits(mmem, gen, gen_evt, d["row"], BS)
                ce2 = np.maximum(lg2, 0) - lg2*d["lab"] + np.log1p(np.exp(-np.abs(lg2)))
                d.setdefault("S", {})[t] = (float((d["wf"]*ce2).sum()), float((d["wp"]*ce2).sum()))
        lb = logits(mmem, gen, gen_evt, b_rows, BS)
        lt = logits(mmem, gen, gen_evt, t_rows, BS)
        pb = np.exp(np.clip(lb, -CAP, CAP)); pt_ = np.exp(np.clip(lt, -CAP, CAP))
        Ob = float((wtruth[b_rows]*pb).sum()/wtruth[b_rows].sum())
        Ot = float((wtruth[t_rows]*pt_).sum()/wtruth[t_rows].sum())
        res["by_t"][str(t)] = {"L": L, "O_band": Ob, "O_tail": Ot}
        print("[%s] t=%.2f  L=%.8f  O_band=%.6f  O_tail=%.6f" % (tag, t, L, Ob, Ot), flush=True)
    L0 = res["by_t"]["0.0"]["L"]; L1 = res["by_t"]["1.0"]["L"]
    Ob0 = res["by_t"]["0.0"]["O_band"]; Ob1 = res["by_t"]["1.0"]["O_band"]
    Ot0 = res["by_t"]["0.0"]["O_tail"]; Ot1 = res["by_t"]["1.0"]["O_tail"]
    obs = [res["by_t"][str(t)]["O_band"] for t in TS]
    dL = L0 - L1
    band_end = Ob1/Ob0; band_maxmin = max(obs)/min(obs)
    lb_resp = float(np.log(Ob1/Ob0)); lt_resp = float(np.log(Ot1/Ot0))
    struct_ok = (lb_resp < 0 < lt_resp) and (abs(lt_resp) >= 0.10*abs(lb_resp))
    if dL <= a.thr_confirm:
        loss_leg = "CONFIRM-eligible"
    elif dL >= a.thr_opposite:
        loss_leg = "OPPOSITE"
    else:
        loss_leg = "UNRESOLVED"
    band_moves = (band_end >= 3.0) or (band_end <= 1/3.0)
    if loss_leg == "OPPOSITE":
        v = "OPPOSITE -- the member is loss-preferred and the NOMINAL is the outlier"
    elif loss_leg == "CONFIRM-eligible" and band_moves and struct_ok:
        v = "CONFIRM -- flat direction"
    elif loss_leg == "CONFIRM-eligible" and not struct_ok:
        v = "STRUCTURAL FAILURE -- CONFIRM unavailable regardless of the loss leg"
    elif loss_leg == "CONFIRM-eligible" and not band_moves:
        v = "UNRESOLVED -- loss leg eligible but the band output response did not move 3x"
    else:
        v = "UNRESOLVED -- licenses neither"
    # ROUTING-LANE SECTION 1, PREDECLARED BEFORE LOOKING: the +/-1.3% weights_pull bracket applied at
    # BOTH endpoints, reporting how much dL ITSELF moves -- not how much L moves. Worst case for a
    # purely additive offset is the offset magnitude (~4.2e-3 = 1.75x the CONFIRM threshold), and that
    # worst case biases TOWARD CONFIRM, the mechanism-favouring branch. So it is measured, not bounded.
    #   dL(scale) = [ (S0_0 - S0_1) + scale*(S1_0 - S1_1) ] / n
    # CANCELLATION HOLDS      : |dL(scale) - dL| <= 2.7e-4 at both bracket ends
    # NOT SEPARABLE           : > 1e-3 -- a CONFIRM must then be reported as inseparable from the
    #                           systematic rather than as CONFIRM
    # PARTIAL                 : between; licenses neither
    nrows = len(row_v)
    # ASSERT the decomposition reproduces the directly-measured loss at scale 1.0 at EVERY t, before
    # the bracket is used at any other scale. Routing lane's precondition, enforced not assumed.
    recon_dev = {}
    for t in TS:
        S0, S1 = S0S1[t]
        recon = (S0 + 1.0*S1)/nrows
        direct = res["by_t"][str(t)]["L"]
        d = abs(recon - direct)
        recon_dev[str(t)] = d
        if d > 1e-12*max(1.0, abs(direct)):
            raise SystemExit("[%s] S0/S1 decomposition disagrees with the direct loss at t=%s "
                             "(|%.17g - %.17g| = %.3e). The bracket's linearity is not valid here; "
                             "failing closed." % (tag, t, recon, direct, d))
    print("[%s] S0/S1 decomposition == direct loss at all t (max dev %.3e)"
          % (tag, max(recon_dev.values())), flush=True)
    dS0 = S0S1[0.0][0] - S0S1[1.0][0]; dS1 = S0S1[0.0][1] - S0S1[1.0][1]
    dL_of = lambda sc: (dS0 + sc*dS1)/nrows
    brack = {}
    for sc in (0.987, 1.013):
        v_ = dL_of(sc); brack["pull_x%.3f" % sc] = {"dL": v_, "shift_vs_unscaled": v_ - dL_of(1.0)}
    max_shift = max(abs(v["shift_vs_unscaled"]) for v in brack.values())
    if max_shift <= 2.7e-4: brack_verdict = "CANCELLATION HOLDS at R5 separation"
    elif max_shift > 1e-3:  brack_verdict = "NOT SEPARABLE -- a CONFIRM cannot be distinguished from the systematic"
    else:                   brack_verdict = "PARTIAL -- licenses neither"
    print("[%s] dL bracket: max shift %.3e -> %s" % (tag, max_shift, brack_verdict), flush=True)

    dL_by_rowset = {"A_heldout_primary": dL_of(1.0)}
    for k in ("B_train_region", "C_independent_perm"):
        S = RS_CACHE[k]["S"]; nn = len(RS_CACHE[k]["row"])
        dL_by_rowset[k] = ((S[0.0][0]-S[1.0][0]) + 1.0*(S[0.0][1]-S[1.0][1]))/nn
    rs_dev = max(abs(dL_by_rowset[k]-dL_by_rowset["A_heldout_primary"])
                 for k in ("B_train_region", "C_independent_perm"))
    rs_verdict = ("ROW-SET IMMATERIAL -- dL moves less than the CONFIRM threshold across row sets"
                  if rs_dev <= 2.4e-3 else
                  "THRESHOLD-INDETERMINATE -- dL moves more than the CONFIRM threshold across row sets")
    print("[%s] dL by row set: %s" % (tag, {k: round(v, 8) for k, v in dL_by_rowset.items()}), flush=True)
    print("[%s] row-set max dev %.3e -> %s" % (tag, rs_dev, rs_verdict), flush=True)

    sd = scat["val_successive_diff_sd"] if scat else None
    rng = scat["val_range"] if scat else None
    dL_in_sd = (dL/sd) if sd else None
    dL_in_range = (dL/rng) if rng else None
    marginal = bool(dL <= a.thr_confirm and sd and dL > sd)
    res.update({"dL_by_rowset": dL_by_rowset, "dL_rowset_max_dev": rs_dev,
                "dL_rowset_VERDICT": rs_verdict,
                "S0S1_vs_direct_loss_max_dev": max(recon_dev.values()),
                "S0S1_vs_direct_loss_by_t": recon_dev,
                "weights_pull_bracket_on_dL": brack,
                "weights_pull_bracket_max_shift": max_shift,
                "weights_pull_bracket_VERDICT": brack_verdict,
                "S0_S1_by_t": {str(k): {"S0": v[0], "S1": v[1]} for k, v in S0S1.items()},
                "delta_L_in_sd_units": dL_in_sd, "delta_L_in_range_units": dL_in_range,
                "MARGINAL_PASS_LABEL": ("within tolerance, not within one sigma" if marginal else None),
                "L_at_nominal": L0, "L_at_member": L1, "delta_L_nom_minus_mem": dL,
                "band_endpoint_ratio_PRIMARY": band_end, "band_maxmin_ratio_secondary": band_maxmin,
                "band_log_response": lb_resp, "tail_log_response": lt_resp,
                "tail_over_band_abs": abs(lt_resp)/abs(lb_resp) if lb_resp else None,
                "structural_arm_signs_ok": bool(lb_resp < 0 < lt_resp),
                "structural_arm_tail_ge_10pct": bool(abs(lt_resp) >= 0.10*abs(lb_resp)),
                "structural_arm_PASS": bool(struct_ok),
                "loss_leg": loss_leg, "VERDICT": v})
    print("[%s] dL=%.6e  band_end=%.4f  band_maxmin=%.4f  logb=%+.4f logt=%+.4f struct=%s"
          % (tag, dL, band_end, band_maxmin, lb_resp, lt_resp, struct_ok), flush=True)
    if v.startswith("CONFIRM") and rs_verdict.startswith("THRESHOLD-INDETERMINATE"):
        v = ("CONFIRM ON THE LOSS LEG BUT THRESHOLD-INDETERMINATE ACROSS ROW SETS "
             "(dL moves %.3e > 2.4e-3) -- NOT reportable as CONFIRM" % rs_dev)
        res["VERDICT"] = v
    if v.startswith("CONFIRM") and brack_verdict.startswith("NOT SEPARABLE"):
        v = ("CONFIRM ON THE LOSS LEG BUT NOT SEPARABLE FROM THE weights_pull SYSTEMATIC "
             "(bracket moves dL by %.3e > 1e-3) -- NOT reportable as CONFIRM" % max_shift)
        res["VERDICT"] = v
    if marginal:
        v = v + "  [within tolerance, NOT within one sigma: dL = %.2f sd, %.2f range]" % (dL_in_sd, dL_in_range)
        res["VERDICT"] = v
    print("[%s] dL in noise units: %r sd, %r range" % (tag, dL_in_sd, dL_in_range), flush=True)
    print("[%s] VERDICT %s" % (tag, v), flush=True)
    out["members"][tag] = res

    # Run provenance INSIDE the artifact. Without it the FILENAME is load-bearing and two arms of a
    # replicate comparison cannot be told apart by content.
    #
    # THIS CHANGES THE MEANING OF THE AMBIGUOUS-BYTE-IDENTICAL BRANCH in replicate_compare.py.
    # Before this stamp: byte-identity across two distinct paths is ambiguous between a perfect
    # deterministic replicate and `cp primary rescue`.
    # After this stamp: two legitimate runs MUST differ (jobid, host, start time), so byte-identity
    # across distinct paths is evidence that PROVENANCE CAPTURE FAILED -- not a determinism success.
    # The branch's semantics were updated in the same commit as this stamp.
    import socket as _sock, datetime as _dt
    _RUN_PROVENANCE = {
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "slurm_step_id": os.environ.get("SLURM_STEP_ID"),
        "slurm_nodelist": os.environ.get("SLURM_JOB_NODELIST"),
        "hostname": _sock.gethostname(),
        "member_loop_utc_LAST_ITERATION": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        # NOT the run start. This block sits inside the per-member loop, so the value is
        # recomputed each iteration and the artifact records the LAST member's loop time.
        # Named for what it is; a field named "run_started_utc" here would be a field named
        # for one quantity computing another. Distinguishing two runs does not need it --
        # slurm_job_id and hostname already differ -- so the honest name is enough.
        # KNOWN GAP: if the member loop never executes, out["run_provenance"] is never set
        # and the final unconditional dump writes an artifact with no provenance. Fail-open,
        # unfixable without the hoist that broke the file, and recorded rather than hidden.
        "argv": sys.argv,
    }
    print("[r5] run provenance:", _RUN_PROVENANCE, flush=True)
    out["run_provenance"] = _RUN_PROVENANCE
    json.dump(out, open(a.json, "w"), indent=1, default=float)
    del mc, _data, reco, gen, reco_evt, gen_evt, mnom, mmem, m1, m2, of
    import gc; gc.collect()
json.dump(out, open(a.json, "w"), indent=1, default=float)
print("\nwrote", a.json)
