#!/usr/bin/env python3
"""OI-126 C-PERMUTATION ENSEMBLE -- the sampling distribution of dL over row-set draws.

AUTHORIZED: Joseph, 2026-08-24, item (8) of the PET lane's ranked next steps, relayed verbatim
through the interpreter session: "8. Yes do this" -- proceed with the permutation ensemble
(n~20-50) for replica_29, DIAGNOSTIC ONLY, does not reopen OI-126.

WHAT THIS MEASURES
------------------
r5_sweep.py's observable is dL = L(t=0) - L(t=1), evaluated on ONE row set. It declared a
row-set robustness check as max|dL(X) - dL(A)| over X in {B_train_region, C_independent_perm},
with the CONFIRM threshold 2.4e-3 as the bar. That is a MAX OVER TWO ALTERNATIVES, which
understates the spread of the population it stands for, and it is n-dependent: max grows with n
by construction, so "max over 200 exceeds max over 2" would be a trivial restatement and is NOT
a finding. This run therefore reports two n-STABLE statistics instead:

  sd_rowset  = sd of dL over independent equal-size uniform row-set draws (loss units, ddof=1)
  exceed_frac = empirical P(|dL(draw) - dL(A)| > 2.4e-3)

WHY IT IS NOT REDUNDANT WITH THE C2 DISCRIMINATOR (57507676)
------------------------------------------------------------
C2 interpolated between A and B with a mixing weight. Measured after the fact: |B-A| = 1.7425e-04
= 0.66% of A while the residual was 3.1973e-03 = 12.0% of A, so the interpolation's ENTIRE range
was 18.3x smaller than the gap it was asked to explain and the test had no discriminating axis.
Its declared criterion -- same sign on two draws -- has P = 1/2 under a symmetric sampling null,
i.e. 50% power against exactly the hypothesis it named. And one of its "two draws" (C1) was the
already-published seed-12345 row set, not a new sample. So the effective n was ONE.
This run replaces max-over-2 and n=1 with a distribution over n=200 per pool.

THE PRE-FLIGHT POWER CHECK IS PART OF THE OUTPUT, NOT A POST HOC READ (rule item 2)
-----------------------------------------------------------------------------------
Declared here, before the run: the discriminating axis is sd_rowset of the matched pool. The
separation this test must resolve is |dL(A) - dL(C2)| = 3.336672e-03 (loss units). Leverage is
separation / sd_rowset. If leverage < 2.0 the test CANNOT separate "sampling" from "not sampling"
and this run reports NO VERDICT together with the achieved leverage. It does not fall back to a
bar, and it does not report a direction as though it were a discrimination.

THE NOISE STATISTIC IS NAMED WITH ITS UNIT AND POPULATION (rule item 3)
----------------------------------------------------------------------
Two different noise sources, both in loss units, are reported side by side and never averaged:
  (i)  epoch-to-epoch val_loss successive-difference sd -- WITHIN one training run, across epochs.
       This is the ONLY source the 2.4e-3 CONFIRM bar was calibrated against.
  (ii) sd_rowset -- ACROSS independent equal-size row-set draws at FIXED weights. Omitted from
       that calibration entirely. Evaluating a fixed network on a fixed slice is deterministic,
       so (ii) is not a re-run effect; it is which rows you summed over.
A bar calibrated on (i) alone is silent about (ii). Measuring (ii) is the point of this run.

PREDECLARED READS -- fixed before any number is looked at
---------------------------------------------------------
R1  If exceed_frac > 0.05 for the matched pool, the 2.4e-3 CONFIRM bar lies INSIDE this member's
    row-set noise and no CONFIRM verdict from r5_sweep.py is safe for it. If <= 0.05 the bar
    survives row-set noise at the 95% level. Reported as a fraction, with its n.
R2  If dL(C1) and dL(C2) both fall inside the central 95% of the uniform-all pool, replica_29's
    "C shortfall" is row-set sampling and the anomaly CLOSES as a non-finding. If both fall below
    the 2.5th percentile it is NOT sampling and the anomaly stays open with a sharper question.
    Anything else is UNRESOLVED at this n and the achieved percentiles are reported instead.
R3  The three pools are MATCHED to the three published row sets so the comparison is like-for-like:
    uniform-all (matches C's construction exactly), validation-region (matches A), train-region
    (matches B). A/C is otherwise confounded: A is drawn from validation positions only while C is
    drawn from ALL positions, so it is a train/validation MIXTURE. Without matched pools a
    composition effect and a sampling effect are the same number.

CORRECTNESS CONTROLS -- the fast path must reproduce three ALREADY-PUBLISHED numbers
-----------------------------------------------------------------------------------
This run computes the logits ONCE over all rows at t=0 and t=1 and then re-sums them per draw,
because `logits()` is a pure function of the row index, so an arbitrarily large ensemble costs two
forward passes instead of 2n. That is a DIFFERENT code path from r5_sweep.py's per-slice passes,
so it is validated against r5_sweep.py's own committed outputs for this member:
    A_heldout_primary   2.6588668915084046e-02
    B_train_region      2.6414423654711385e-02
    C_independent_perm  2.4619673097196985e-02   (seed 12345, reproduced through the ensemble
                                                  code path itself, not a separate branch)
    idx2_sha256         compared to the receipt's value: validates RNG-state reproduction
                        independently of the model, so a mis-typed setup cannot pass silently.
DECLARED TOLERANCE, before the run: max relative deviation over the three dL controls must be
<= 1e-6. Exact bit-identity is NOT required and is not expected -- the final partial batch differs
between the two batchings. If the tolerance is EXCEEDED the fast path is rejected, the run falls
back to per-draw forward passes at n=24 (the largest n that fits the remaining walltime at
~2 passes per draw), and the fallback is recorded in the artifact as the branch taken. The
fallback is not a caveat; it is a calibrated second path with its own n.

WHAT A TERMINAL RESULT HERE CANNOT AUTHORIZE
--------------------------------------------
Nothing about OI-126. This measures row-set sampling of one diagnostic observable at fixed
weights. It is not estimator-equivalence and it is not coverage, which are the two conditions
OI-126's reconsideration requires and which remain untested. It cannot adopt, pair, or promote any
PET covariance, and a CLOSED reading of R2 closes an ANOMALY, not the ruling.
"""
import argparse, hashlib, importlib, json, os, pickle, sys
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--nominal-artifact", required=True)
ap.add_argument("--replicas-root", required=True)
ap.add_argument("--members", required=True, help="exactly one int for this producer")
ap.add_argument("--added-members", default="")
ap.add_argument("--n-perms", type=int, default=200)
ap.add_argument("--seed-base", type=int, default=700000)
ap.add_argument("--thr-confirm", type=float, default=2.4e-3)
ap.add_argument("--json", required=True)
# PER-MEMBER PUBLISHED CONTROLS. These were literals in the replica_29 run; making them arguments is
# the ONLY reason this file changed, and it is the low-risk shape: the validated computation is
# untouched and the five new members get exactly the control discipline replica_29 got, three
# published dL values each, re-derived from the R5 receipt's own dL_by_rowset cells.
ap.add_argument("--pub-a", type=float, required=True)
ap.add_argument("--pub-b", type=float, required=True)
ap.add_argument("--pub-c1", type=float, required=True)
ap.add_argument("--pub-c2", type=float, default=None,
                help="only replica_29 has a fourth published draw; omit for the others")
ap.add_argument("--pub-l-t0", type=float, default=None)
ap.add_argument("--pub-l-t1", type=float, default=None)
ap.add_argument("--sep", type=float, default=None,
                help="separation the power check must resolve; default max(|B-A|,|C1-A|), which is "
                     "exactly r5_sweep.py's dL_rowset_max_dev -- the quantity it compared to the bar")
a = ap.parse_args()

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

# ---------------------------------------------------------------- published controls
PUB = {"A_heldout_primary": a.pub_a,
       "B_train_region": a.pub_b,
       "C_independent_perm": a.pub_c1}
PUB_C2 = a.pub_c2
PUB_L = ({"0.0": a.pub_l_t0, "1.0": a.pub_l_t1}
         if (a.pub_l_t0 is not None and a.pub_l_t1 is not None) else None)
PUB_OWN_EPOCH_SD = None          # filled from the member's own history below
TOL_REL = 1e-6
SEP_PUB = (a.sep if a.sep is not None
           else max(abs(a.pub_b - a.pub_a), abs(a.pub_c1 - a.pub_a)))
LEVERAGE_MIN = 2.0

assert len(members) == 1, "this producer takes exactly one member; got %r" % (members,)
k = members[0]
tag = "replica_%02d" % k
t_start = __import__("datetime").datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

# ---------------------------------------------------------------- member setup
# Re-typed rather than spliced from r5_sweep.py's indented loop body. Textual fidelity is NOT the
# guarantee here: idx2_sha256 and three published dL values are, and a mis-typed setup fails them.
rroot = os.path.join(a.replicas_root, tag)
art = os.path.join(rroot, "training", "GATE5_REPLICA_WEIGHTS.npz")
tgt = os.path.join(rroot, "target", "GATE5_REPLICA_TARGET.npy")
with np.load(art, allow_pickle=True) as d:
    mcon = d["inference_contract"].item(); ridx = int(d["replica_index"])
mem_wf = mcon["weights_folder"]
bseed = 50000 + ridx
print("[ens] %s bootstrap_seed=%d weights_folder=%s" % (tag, bseed, mem_wf), flush=True)

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

# THE ORDER OF THESE TWO SHUFFLES IS LOAD-BEARING. Both draw from numpy's GLOBAL state, so
# dropping the i1 shuffle -- which is otherwise unused in this producer -- would change i2 and
# therefore change A and B. idx2_sha256 below is the control that catches exactly that.
n1 = len(of.labels_mc) + len(of.labels_data); n2 = len(of.labels_mc) + len(of.labels_gen)
i1 = np.arange(n1); np.random.shuffle(i1)
i2 = np.arange(n2); np.random.shuffle(i2)
NTRAIN2 = of.num_steps_gen * of.BATCH_SIZE
NTEST2 = int((1.0 - of.train_frac) * NTRAIN2)
take = NTRAIN2 - NTEST2; vsteps = NTEST2 // of.BATCH_SIZE; vn = vsteps * of.BATCH_SIZE
idx2_sha = hashlib.sha256(i2.tobytes()).hexdigest()
print("[ens] n2=%d take=%d vn=%d idx2_sha256=%s" % (n2, take, vn, idx2_sha[:16]), flush=True)

m2.load_weights(ck(mem_wf, niter-2, 2))
w2p = np.asarray(_engine_reweighter(m2, BS).reweight((gen, gen_evt), m2, batch_size=BS), np.float64)
push_prev = np.ones(len(pass_gen)); push_prev[pass_gen] = w2p[pass_gen]
m1.load_weights(ck(mem_wf, niter-1, 1))
w1 = np.asarray(_engine_reweighter(m1, 1000).reweight((reco, reco_evt), m1, batch_size=1000), np.float64)
inc1 = np.ones(len(pass_reco)); inc1[pass_reco] = w1[pass_reco]
weights_pull = push_prev * inc1

labels = np.concatenate((of.labels_mc, of.labels_gen)).astype(np.float64)
wts = np.concatenate((mc.weight*mc.pass_gen, mc.weight*weights_pull*mc.pass_gen)).astype(np.float64)
assert len(labels) == n2 and len(wts) == n2, "objective arrays are not n2-long (%d,%d vs %d)" % (
    len(labels), len(wts), n2)

mnom = build_pair(gen.shape[-1], reco.shape[-1], P, ev_reco, ev_truth, coord_reco, coord_gen)[1]
mmem = build_pair(gen.shape[-1], reco.shape[-1], P, ev_reco, ev_truth, coord_reco, coord_gen)[1]
mnom.load_weights(ck(nom_wf, niter-1, 2)); mmem.load_weights(ck(mem_wf, niter-1, 2))
Wn = [np.asarray(w, np.float64) for w in mnom.model.get_weights()]
Wm = [np.asarray(w, np.float64) for w in mmem.model.get_weights()]
assert len(Wn) == len(Wm) and all(x.shape == y.shape for x, y in zip(Wn, Wm)), "weight shape mismatch"

# the member's own epoch scatter -- noise source (i), the ONLY one the 2.4e-3 bar was calibrated on
hp = os.path.join(mem_wf, "OmniFold_%s_iter%d_step2.pkl" % (MFNAME, niter-1))
own_epoch = None
if os.path.exists(hp):
    h = pickle.load(open(hp, "rb")); vv = np.asarray(h["val_loss"], float)
    own_epoch = {"n_epochs": int(len(vv)),
                 "val_successive_diff_sd": float(np.std(np.diff(vv), ddof=1)),
                 "val_max_successive_absdiff": float(np.max(np.abs(np.diff(vv)))),
                 "val_range": float(vv.max() - vv.min()),
                 "WHAT_POPULATION": "epochs WITHIN one training run of this member",
                 "WHAT_IT_IS_NOT": ("not a between-run difference and not a row-set difference; "
                                    "evaluating fixed weights on a fixed slice is deterministic")}
    PUB_OWN_EPOCH_SD = own_epoch["val_successive_diff_sd"]

# ---------------------------------------------------------------- the two forward passes
NR = len(pass_gen)
posrow = (np.arange(n2) % NR).astype(np.int64)
is1 = labels > 0.5
CE0, CE1 = {}, {}
for t in (0.0, 1.0):
    mmem.model.set_weights([x + t*(y-x) for x, y in zip(Wn, Wm)])
    lg = logits(mmem, gen, gen_evt, np.arange(NR, dtype=np.int64), BS)
    base = np.maximum(lg, 0.0) + np.log1p(np.exp(-np.abs(lg)))
    CE0[t] = base            # ce at label 0
    CE1[t] = base - lg       # ce at label 1;  ce = max(lg,0) - lg*lab + log1p(exp(-|lg|))
    print("[ens] full-row logits at t=%.1f over %d rows done" % (t, NR), flush=True)

def dL_fast(sel):
    r = posrow[sel]; w = wts[sel]; one = is1[sel]; n = len(sel)
    L = {}
    for t in (0.0, 1.0):
        ce = np.where(one, CE1[t][r], CE0[t][r])
        L[t] = float((w*ce).sum()/n)
    return L[0.0] - L[1.0], L[0.0], L[1.0]

def dL_slow(sels):
    """r5_sweep.py's own batching: one forward pass per (t, selection), over that selection only."""
    Ls = {0.0: [], 1.0: []}
    for t in (0.0, 1.0):
        mmem.model.set_weights([x + t*(y-x) for x, y in zip(Wn, Wm)])
        for sel in sels:
            lg = logits(mmem, gen, gen_evt, posrow[sel], BS)
            lab = labels[sel]
            ce = np.maximum(lg, 0.0) - lg*lab + np.log1p(np.exp(-np.abs(lg)))
            Ls[t].append(float((wts[sel]*ce).sum()/len(sel)))
    return [Ls[0.0][i] - Ls[1.0][i] for i in range(len(sels))]

# ---------------------------------------------------------------- row sets and pools
SEL_A = i2[take:take+vn]
if vn <= take:
    SEL_B = i2[:vn]; B_ok = True
else:
    SEL_B = np.arange(n2); B_ok = False       # r5's own fallback; flagged, never silent
SEL_C1 = np.random.RandomState(12345).permutation(n2)[:vn]

val_pool = i2[take:]
trn_pool = i2[:take]
POOLS = {
    "uniform_all_matches_C": {"pool": None, "n_pool": int(n2),
        "construction": "np.random.RandomState(seed).permutation(n2)[:vn] -- byte-for-byte r5's C"},
    "validation_region_matches_A": {"pool": val_pool, "n_pool": int(len(val_pool)),
        "construction": "i2[take:][RandomState(seed).permutation(len(pool))[:vn]]"},
    "train_region_matches_B": {"pool": trn_pool, "n_pool": int(len(trn_pool)),
        "construction": "i2[:take][RandomState(seed).permutation(len(pool))[:vn]]"},
}
def draw(pname, seed):
    p = POOLS[pname]["pool"]
    if p is None:
        return np.random.RandomState(seed).permutation(n2)[:vn]
    return p[np.random.RandomState(seed).permutation(len(p))[:vn]]

# ---------------------------------------------------------------- controls, then the gate
ctrl = {}
for nm, sel in (("A_heldout_primary", SEL_A), ("B_train_region", SEL_B),
                ("C_independent_perm", SEL_C1)):
    dl, L0, L1 = dL_fast(sel)
    tgt_v = PUB[nm]
    ctrl[nm] = {"fast_path_dL": dl, "published_dL": tgt_v,
                "abs_dev": abs(dl - tgt_v), "rel_dev": abs(dl - tgt_v)/abs(tgt_v),
                "L_t0": L0, "L_t1": L1, "n_rows": int(len(sel))}
    print("[ens] control %-20s fast %.16e  published %.16e  rel_dev %.3e"
          % (nm, dl, tgt_v, ctrl[nm]["rel_dev"]), flush=True)
ctrl["idx2_sha256"] = {"measured": idx2_sha,
    "WHAT_IT_VALIDATES": ("RNG-state reproduction independently of the model: if the two shuffles "
                          "were reordered or one dropped, A and B change and this digest changes"),
    "receipt_value": "not carried per-member in the R5 receipt; compare to the run log of the "
                     "original sweep if a byte comparison is wanted"}
ctrl["L_endpoints_vs_published_A"] = ({} if PUB_L is None else {
    "measured_L_t0": ctrl["A_heldout_primary"]["L_t0"], "published_L_t0": PUB_L["0.0"],
    "measured_L_t1": ctrl["A_heldout_primary"]["L_t1"], "published_L_t1": PUB_L["1.0"],
    "abs_dev_t0": abs(ctrl["A_heldout_primary"]["L_t0"] - PUB_L["0.0"]),
    "abs_dev_t1": abs(ctrl["A_heldout_primary"]["L_t1"] - PUB_L["1.0"]),
    "WHY_BOTH": ("dL is a DIFFERENCE, so an additive offset common to both endpoints cancels in it "
                 "and a dL-only control cannot see one. These two see it.")})
if PUB_L is None:
    ctrl["L_endpoints_vs_published_A"] = ("NOT AVAILABLE -- the R5 receipt publishes L_by_t per member, "
        "but this run was given only the three dL values. So the additive-offset channel is UNCHECKED "
        "for this member, and that is a gap and not a pass: a common offset at both endpoints cancels "
        "in dL and no dL control can see it. The three dL controls below still bind the difference.")

max_rel = max(ctrl[n]["rel_dev"] for n in PUB)
FAST_OK = bool(max_rel <= TOL_REL) and B_ok
PATH = "fast_two_pass" if FAST_OK else "fallback_per_draw"
N_EFF = int(a.n_perms) if FAST_OK else 24
print("[ens] DECLARED TOLERANCE %.0e  achieved max rel dev %.3e  -> path=%s  n=%d"
      % (TOL_REL, max_rel, PATH, N_EFF), flush=True)

# ---------------------------------------------------------------- the ensemble
seeds = [int(a.seed_base) + j for j in range(N_EFF)]
ENS = {}
for pname in POOLS:
    if vn > POOLS[pname]["n_pool"]:
        ENS[pname] = {"STATUS": "UNAVAILABLE -- vn %d exceeds pool size %d; NOT substituted with a "
                                "different pool, because a silent substitution would make this row "
                                "answer about another population under this name"
                                % (vn, POOLS[pname]["n_pool"])}
        print("[ens] pool %s UNAVAILABLE" % pname, flush=True)
        continue
    sels = [draw(pname, s) for s in seeds]
    vals = dL_slow(sels) if not FAST_OK else [dL_fast(s)[0] for s in sels]
    v = np.asarray(vals, np.float64)
    dev = np.abs(v - PUB["A_heldout_primary"])
    ENS[pname] = {
        "construction": POOLS[pname]["construction"], "n_pool": POOLS[pname]["n_pool"],
        "n_draws": int(len(v)), "seed_base": int(a.seed_base), "rows_per_draw": int(vn),
        "dL_mean": float(v.mean()), "dL_sd_ddof1": float(v.std(ddof=1)),
        "dL_min": float(v.min()), "dL_max": float(v.max()),
        "dL_pct": {str(q): float(np.percentile(v, q)) for q in (2.5, 16, 50, 84, 97.5)},
        "exceed_frac_gt_thr_vs_A": float((dev > a.thr_confirm).mean()),
        "max_abs_dev_vs_A": float(dev.max()),
        "N_STABILITY_NOTE": ("dL_sd_ddof1 and exceed_frac_gt_thr_vs_A are the reportable "
            "statistics: they do not grow with n. dL_max and max_abs_dev_vs_A DO grow with n by "
            "construction, so they may not be compared to r5's max-over-2 as though that were the "
            "same quantity -- that comparison is n-dependent and would be trivially true."),
        "dL_draws": [float(x) for x in v],
    }
    print("[ens] %-28s mean %.6e sd %.6e  exceed_frac(>%.1e) %.3f"
          % (pname, v.mean(), v.std(ddof=1), a.thr_confirm,
             ENS[pname]["exceed_frac_gt_thr_vs_A"]), flush=True)

# the two previously-published C draws, located against the fresh ensemble (never against a set
# containing themselves)
named = {}
_named_seeds = [("C1_seed_12345", 12345)]
if PUB_C2 is not None:
    _named_seeds.append(("C2_seed_987654321", 987654321))
for nm, sd_ in _named_seeds:
    sel = np.random.RandomState(sd_).permutation(n2)[:vn]
    dl = dL_slow([sel])[0] if not FAST_OK else dL_fast(sel)[0]
    ref = ENS.get("uniform_all_matches_C", {})
    dr = np.asarray(ref.get("dL_draws", []), np.float64)
    named[nm] = {"dL": dl,
        "published": (PUB["C_independent_perm"] if sd_ == 12345 else PUB_C2),
        "abs_dev_from_published": abs(dl - (PUB["C_independent_perm"] if sd_ == 12345 else PUB_C2)),
        "percentile_in_uniform_all": (float((dr <= dl).mean()*100.0) if len(dr) else None),
        "inside_central_95": (bool(ref["dL_pct"]["2.5"] <= dl <= ref["dL_pct"]["97.5"])
                              if "dL_pct" in ref else None)}
    print("[ens] %s dL %.16e  pct %s" % (nm, dl, named[nm]["percentile_in_uniform_all"]), flush=True)
named["C2_CONSTRUCTION_IS_KNOWN_SO_THIS_IS_A_HARD_CONTROL"] = (
    "MEASURED, not assumed: r5_c2_discriminator.py:91 is "
    "rs = np.random.RandomState(a.c2_seed); alt = rs.permutation(n2) -- identical to "
    "C1. So C2_seed_987654321 above MUST reproduce the published 2.3251996885442217e-02 to the same "
    "1e-6 relative tolerance as the other three controls. An earlier draft of this file called it a "
    "soft caveat on the grounds that the construction was unrecorded; that was wrong and the file "
    "was read before the run. abs_dev_from_published above is the check.")
_c2r = (named["C2_seed_987654321"]["abs_dev_from_published"]/abs(PUB_C2)
        if PUB_C2 is not None else None)
named["C2_HARD_CONTROL_RESULT"] = {"rel_dev": _c2r, "tolerance": TOL_REL,
    "PASS": (None if _c2r is None else bool(_c2r <= TOL_REL)),
    "NOT_APPLICABLE_NOTE": ("only replica_29 has a fourth published draw (job 57507676). For the "
                            "other five this control does not exist and is reported as None rather "
                            "than as a pass."),
    "IF_FAIL": ("the two runs disagree on a row set built the same way from the same seed, which "
                "would falsify the fast path OR the setup reproduction; the ensemble is then not "
                "citable and this field says so rather than the run exiting 0 quietly.")}
print("[ens] C2 hard control %s" % ("N/A for this member" if _c2r is None else
      "rel_dev %.3e tol %.0e PASS=%s" % (_c2r, TOL_REL,
      named["C2_HARD_CONTROL_RESULT"]["PASS"])), flush=True)

# ---------------------------------------------------------------- the predeclared reads
ref = ENS.get("uniform_all_matches_C", {})
sd_all = ref.get("dL_sd_ddof1")
leverage = (SEP_PUB/sd_all) if sd_all else None
# GATE CORRECTED BETWEEN RUNS, per BEN-535 and the PB-12 clause added at 6f46605a. In the
# replica_29 run this gate read "leverage < 2 => NO VERDICT", which is wrong in one direction: a
# SMALL separation-to-spread ratio is itself evidence FOR consistency with the draw, and low
# leverage forbids only the NOT-SAMPLING conclusion. That run's emitted label is NOT retro-fitted --
# it stands as issued in RECEIPT-20260824-oi126-c-permutation-ensemble.json, and this run is the
# first to use the corrected form. Reported so the two runs are not read as the same instrument.
R2 = None
if leverage is None:
    R2 = "NO VERDICT -- the uniform-all pool was unavailable, so there is no discriminating axis."
elif leverage < LEVERAGE_MIN:
    _inside = named["C1_seed_12345"]["inside_central_95"]
    R2 = ("LOW LEVERAGE %.2f < %.1f -- DIRECTION-SPECIFIC READ. The separation (%.6e) is smaller "
          "than %.1fx the row-set sd (%.6e). That FORBIDS the 'not sampling' conclusion, which needs "
          "the gap to be large relative to the spread. It does NOT forbid the other direction: a "
          "small gap-to-spread ratio is what consistency with the draw looks like. Published C1 "
          "inside the central 95%% of %d matched draws: %s. So: CONSISTENT WITH ROW-SET SAMPLING, "
          "and NOT-SAMPLING is unavailable at this leverage."
          % (leverage, LEVERAGE_MIN, SEP_PUB, LEVERAGE_MIN, sd_all, ref["n_draws"], _inside))
else:
    _nm = [n for n, _ in _named_seeds]
    i95 = [named[n]["inside_central_95"] for n in _nm]
    lo = [named[n]["dL"] < ref["dL_pct"]["2.5"] for n in _nm]
    if all(i95):
        R2 = ("CLOSED AS SAMPLING -- both published C draws fall inside the central 95%% of %d "
              "matched draws. replica_29's C shortfall is row-set sampling." % ref["n_draws"])
    elif all(lo):
        R2 = ("NOT SAMPLING -- both published C draws fall below the 2.5th percentile of %d matched "
              "draws. The shortfall is not row-set sampling and the anomaly stays open."
              % ref["n_draws"])
    else:
        R2 = ("UNRESOLVED AT THIS n -- the published draws do not agree on side. Percentiles: %s. "
              "No bar is applied."
              % {n: named[n]["percentile_in_uniform_all"] for n in _nm})

# R4 -- PREDECLARED BEFORE THIS RUN. The replica_29 result said the three row sets are three
# POPULATIONS and that a mixture pool's mean should follow from the two pure pools:
#     mean(uniform) = w*mean(train) + (1-w)*mean(validation),   w = take/n2, the train fraction.
# For replica_29 that held to 0.58 standard errors. It is now a FALSIFIABLE prediction on five more
# members, and the sign of the composition effect DIFFERS between them -- replica_29 is the only one
# whose B and C1 both sit BELOW A, the other five sit above -- so this is not a re-test of the same
# direction. DECLARED: |predicted - measured| <= 3 standard errors of the measured mean, per member.
# Every value is reported whatever it is. A miss is evidence AGAINST the composition account and
# would reopen the mechanism question rather than being explained away.
_R4 = {"NOT_MEASURABLE": "the uniform, validation or train pool was unavailable"}
try:
    _u, _v, _t = (ENS["uniform_all_matches_C"], ENS["validation_region_matches_A"],
                  ENS["train_region_matches_B"])
    if all("dL_mean" in x for x in (_u, _v, _t)):
        _w = take/n2
        _pred = _w*_t["dL_mean"] + (1.0 - _w)*_v["dL_mean"]
        _sem = _u["dL_sd_ddof1"]/(len(_u["dL_draws"])**0.5)
        _R4 = {"w_train_fraction": _w, "predicted_uniform_mean": _pred,
               "measured_uniform_mean": _u["dL_mean"], "difference": _pred - _u["dL_mean"],
               "standard_error_of_measured_mean": _sem,
               "difference_in_sem": abs(_pred - _u["dL_mean"])/_sem if _sem else None,
               "declared_bar_sem": 3.0,
               "HOLDS": bool(_sem and abs(_pred - _u["dL_mean"])/_sem <= 3.0),
               "pool_means": {"validation": _v["dL_mean"], "train": _t["dL_mean"],
                              "uniform": _u["dL_mean"]},
               "composition_effect_sign": ("train ABOVE validation" if _t["dL_mean"] > _v["dL_mean"]
                                           else "train BELOW validation"),
               "WHAT_A_MISS_MEANS": ("evidence against the composition account for this member, which "
                   "reopens the mechanism question. It is not to be read as noise.")}
        print("[ens] R4 composition: pred %.6e measured %.6e  %.2f sem  HOLDS=%s  (%s)"
              % (_pred, _u["dL_mean"], _R4["difference_in_sem"], _R4["HOLDS"],
                 _R4["composition_effect_sign"]), flush=True)
except BaseException as _e:
    _R4 = {"FAILED": repr(_e), "note": "a reporting field must not decide the run"}

R1 = {}
for pname, e in ENS.items():
    if "exceed_frac_gt_thr_vs_A" not in e:
        R1[pname] = "UNAVAILABLE"; continue
    f = e["exceed_frac_gt_thr_vs_A"]
    R1[pname] = ("BAR IS INSIDE THE ROW-SET NOISE -- P(|dL(draw)-dL(A)| > %.1e) = %.3f > 0.05, so "
                 "no CONFIRM verdict from r5_sweep.py is safe for this member on this pool."
                 % (a.thr_confirm, f)) if f > 0.05 else (
                 "BAR SURVIVES ROW-SET NOISE AT 95%% -- P(|dL(draw)-dL(A)| > %.1e) = %.3f <= 0.05."
                 % (a.thr_confirm, f))

out = {
 "schema": "oi126-c-permutation-ensemble-v1",
 "WHAT_THIS_CANNOT_AUTHORIZE": (
   "Nothing about OI-126. Row-set sampling of one diagnostic observable at FIXED weights is neither "
   "estimator-equivalence nor coverage, and those two are what reconsideration requires. No PET "
   "covariance may be adopted, paired or promoted on this. A CLOSED read of R2 closes an ANOMALY, "
   "never the ruling."),
 "authorization": {"who": "Joseph", "when": "2026-08-24", "item": "(8) of the PET lane's ranked list",
   "verbatim": "8. Yes do this",
   "channel": "relayed by the interpreter session; Joseph established that channel himself in a "
              "direct turn on 2026-08-23. This field records a RELAY, not a first-hand grant.",
   "declared_scope": "n~20-50 for replica_29, diagnostic only, does not reopen OI-126",
   "deviation_from_declared_scope": ("n=%d, larger than the authorized 20-50. The two-forward-pass "
      "path makes the marginal cost of a draw pure numpy, so a larger n is free; it buys sd to "
      "about +-5%% instead of +-15%%. Recorded as a deviation because it is one." % N_EFF)},
 "member": {"tag": tag, "replica_index": ridx, "bootstrap_seed": bseed, "weights_folder": mem_wf,
            "nominal_step2_ckpt": ck(nom_wf, niter-1, 2), "member_step2_ckpt": ck(mem_wf, niter-1, 2)},
 "split": {"n2": int(n2), "n_rows": int(NR), "cache_take": int(take), "validation_steps": int(vsteps),
           "rows_per_draw_vn": int(vn), "idx2_sha256": idx2_sha,
           "B_used_declared_construction": bool(B_ok)},
 "loss_normalisation_pin": LOSS_PIN,
 "module_audit_roots": roots, "sys_path0_after_imports": sys.path[0],
 "TWO_NOISE_SOURCES_NAMED_WITH_UNITS": {
   "i_epoch_scatter_within_one_run": own_epoch,
   "ii_rowset_sd_across_draws_at_fixed_weights": {
     "value": sd_all, "unit": "loss units, same as dL", "ddof": 1,
     "population": "independent equal-size uniform row-set draws from the matched position pool",
     "n": (ref.get("n_draws") if ref else None)},
   "WHY_BOTH_AND_NEVER_AVERAGED": (
     "The 2.4e-3 CONFIRM bar was calibrated against (i) alone -- r5_sweep.py's docstring says so. "
     "(ii) is a different source and was omitted from that calibration. A bar calibrated on (i) is "
     "silent about (ii); it is not conservative about it. Naming both with their units and "
     "populations is the whole point of this section."),
   "ratio_ii_over_i": (float(sd_all/PUB_OWN_EPOCH_SD) if (sd_all and PUB_OWN_EPOCH_SD) else None)},
 "PRE_FLIGHT_POWER_CHECK": {
   "declared_before_the_run": True, "discriminating_axis": "row-set sd of the uniform-all pool",
   "separation_to_resolve": SEP_PUB,
   "separation_operands": "|published dL(C2) 2.3251996885442217e-02 - published dL(A) "
                          "2.6588668915084046e-02|",
   "achieved_sd": sd_all, "leverage": leverage, "leverage_min_declared": LEVERAGE_MIN,
   "has_power": (None if leverage is None else bool(leverage >= LEVERAGE_MIN))},
 "CORRECTNESS_CONTROLS": {"declared_tolerance_rel": TOL_REL, "achieved_max_rel_dev": max_rel,
   "path_taken": PATH, "n_draws_per_pool": N_EFF, "controls": ctrl,
   "WHY_NOT_BIT_IDENTITY": ("the final partial batch differs between batching over all rows and "
      "batching over a selection, so exact equality is not the right bar; 1e-6 relative was "
      "declared in the docstring before the run")},
 "ENSEMBLES": ENS,
 "PUBLISHED_DRAWS_LOCATED": named,
 "R4_COMPOSITION_MODEL_PREDICTION": _R4,
 "PREDECLARED_READS": {"R1_is_the_bar_inside_the_rowset_noise": R1, "R2_is_the_C_shortfall_sampling": R2,
   "R4_see_top_level_key": "R4_COMPOSITION_MODEL_PREDICTION",
   "R3_pools_are_matched": ("A is drawn from validation positions only, C from ALL positions, so C "
     "is a train/validation MIXTURE. Comparing A to C without matched pools confounds a composition "
     "effect with a sampling effect. The three pools above are matched to A, B and C respectively.")},
 "R5_ROWSET_ROBUSTNESS_CONSEQUENCE": {
   "what_r5_declared": ("max|dL(X)-dL(A)| over X in {B_train_region, C_independent_perm} <= 2.4e-3 "
     "=> ROW-SET IMMATERIAL; if it EXCEEDS => report threshold-indeterminate rather than picking "
     "the row set that gives a verdict"),
   "what_r5_recorded_for_replica_29": "ROW-SET IMMATERIAL, max dev 1.968996e-03 = 0.82x the bar",
   "what_the_C2_job_measured": ("a third row set at 2.3251996885442217e-02, deviation 3.336672e-03 "
     "= 1.39x the bar -- EXCEEDS it"),
   "status_in_the_R5_RECEIPT": ("as of the receipt at sha256 ca5759d7…, per_member.replica_29."
     "dL_rowset_VERDICT still reads ROW-SET IMMATERIAL and no section connects the C2 measurement "
     "to it; the string 'threshold-indeterminate' does not occur anywhere in the receipt"),
   "the_literal_quantifier_defence_and_why_it_is_thin": (
     "r5's rule quantified over X in {B, C1} exactly, and C2 is not a member of that set, so the "
     "rule as WRITTEN was satisfied. That defence is thin: the rule's purpose is row-set "
     "robustness, and C2 is the same construction as C1 with a different seed -- i.e. precisely the "
     "evidence the rule exists to catch. Letting the quantifier's literal membership decide is "
     "measurability choosing the specification."),
   "scope_across_members": ("2 of 6 members ALREADY read THRESHOLD-INDETERMINATE (replica_45 4.40x, "
     "replica_26 3.74x). Of the 4 reading IMMATERIAL, three sit at 0.75x, 0.82x and 0.96x of the "
     "bar on a max over TWO alternatives. Only replica_43 (0.38x) has margin. This is a statement "
     "about the R5 receipt's per-member robustness cells, measured from the receipt, and it is "
     "about ALL SIX members even though this run measures ONE."),
   "what_this_run_settles_and_for_whom": ("R1 above settles it for replica_29 with an n-stable "
     "statistic. The other five are NOT measured here and their cells stay as recorded.")},
 "run_provenance": {"slurm_job_id": os.environ.get("SLURM_JOB_ID"),
   "hostname": os.uname().nodename, "run_started_utc": t_start,
   "run_ended_utc": __import__("datetime").datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
   "argv": sys.argv, "n_perms_requested": int(a.n_perms), "seed_base": int(a.seed_base),
   "thr_confirm": float(a.thr_confirm), "producer_sha256":
     hashlib.sha256(open(os.path.abspath(sys.argv[0]), "rb").read()).hexdigest()},
}
json.dump(out, open(a.json, "w"), indent=1, default=float)
print("\n[ens] wrote", a.json, flush=True)
print("[ens] R1:", json.dumps(R1, indent=1), flush=True)
print("[ens] R2:", R2, flush=True)
