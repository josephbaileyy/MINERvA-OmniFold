#!/usr/bin/env python3
"""C2 DISCRIMINATOR for replica_29's unexplained low C. Predeclared by the routing lane.

replica_29's independent-permutation row set C sat 6.9% below the composition prediction
w*B + (1-w)*A, an absolute residual of -1.83e-03 against 3-5e-04 for the other three members --
and 10.5x its own leverage range |B-A|, so no choice of w can produce it. Two hypotheses:

  SAMPLING NOISE : heavy-tailed rows, a property of THE DRAW -> a second independent permutation
                   at a different seed must give a DIFFERENT C.
  SPLIT ERROR    : a property of the MEMBER -> C stays low across seeds.

PREDECLARED on |C2 - C_pred| where C_pred = w*B + (1-w)*A from the ORIGINAL A and B:
    SAMPLING NOISE : <= 5.5e-04
    NOT SAMPLING   : >= 1.4e-03 AND same sign as C1's residual -> split-error branch live
    UNRESOLVED     : between, or opposite sign at large magnitude. Licenses neither.

One extra pair of loss evaluations (t=0, t=1) on one member. No new machinery.
"""
import argparse, hashlib, importlib, json, os, sys
import numpy as np
ap = argparse.ArgumentParser()
ap.add_argument("--nominal-artifact", required=True); ap.add_argument("--replicas-root", required=True)
ap.add_argument("--member", type=int, required=True)
ap.add_argument("--c1-seed", type=int, default=12345)
ap.add_argument("--c2-seed", type=int, required=True)
ap.add_argument("--sweep-json", required=True); ap.add_argument("--json", required=True)
a = ap.parse_args()
assert a.c2_seed != a.c1_seed, "C2 seed must differ from C1's"

import train_fullevent_nominal as T
for n in ("omnifold", "extract_fullevent_fps", "fullevent_fps_dataloader"): importlib.import_module(n)
import fullevent_fps_dataloader as fe
from omnifold import PET, MultiFold
from omnifold.net import weighted_binary_crossentropy as _wbce
from annealed_estimator import make_annealed_multifold
from diagnostic_target_override import resolve_precomputed_target
from extract_fullevent_fps import _engine_reweighter
import tensorflow as tf

# same two-armed pin as the sweep: the S0/S1 linearity needs row-count normalisation
y = tf.constant([[1.0,2.0],[0.0,3.0],[1.0,0.5]]); p = tf.constant([[0.3],[-0.7],[1.1]])
L1 = float(_wbce(y,p)); c = 7.0
Lc = float(_wbce(tf.constant([[1.0,2.0*c],[0.0,3.0*c],[1.0,0.5*c]]), p))
assert abs(Lc-c*L1) <= 1e-6*abs(c*L1) and abs(Lc-L1) > 1e-6, "loss is not row-count normalised"
print("[c2] loss pin PASS (ratio %.8f, predicted 0.82064543 -> measured %.8f)" % (Lc/L1, L1), flush=True)

with np.load(a.nominal_artifact, allow_pickle=True) as d:
    pol = d["seed_policy"].item(); ncon = d["inference_contract"].item(); inputs_path = str(d["inputs_path"])
niter = int(pol["niter"]); BS = int(pol["batch_size"]); MF = ncon["multifold_name"]
nom_wf = ncon["weights_folder"]
tag = "replica_%02d" % a.member
root = os.path.join(a.replicas_root, tag)
mwf = os.path.join(root, "training", "w_nominal")
tgt = os.path.join(root, "target", "GATE5_REPLICA_TARGET.npy")
bseed = 50000 + a.member

tf.keras.utils.set_random_seed(int(pol["estimator_seed"]))
_data, mc, imc, cr, cg, meta = fe.build_fullevent_loaders(
    inputs_path, max_events=int(pol["train_events"]), seed=int(pol["subsample_seed"]),
    bkg_mode=T.BKG_MODE, precomputed_target=tgt, bootstrap_seed=bseed,
    precomputed_target_replica_seed=bseed)
reco = np.asarray(mc.reco); gen = np.asarray(mc.gen)
reco_evt = np.asarray(mc.reco_evt); gen_evt = np.asarray(mc.gen_evt)
pass_reco = np.asarray(mc.pass_reco).astype(bool); pass_gen = np.asarray(mc.pass_gen).astype(bool)
P = reco.shape[1]
m1 = PET(reco.shape[-1], num_evt=meta["n_evt_reco"], num_part=P, num_transformer=2, num_heads=2,
         projection_dim=32, local=True, K=3, coord_idx=cr)
m2 = PET(gen.shape[-1], num_evt=meta["n_evt_truth"], num_part=P, num_transformer=2, num_heads=2,
         projection_dim=32, local=True, K=3, coord_idx=cg)
_r = []; Ann = make_annealed_multifold(MultiFold, tf, _r)
of = Ann(MF, m1, m2, _data, mc, niter=niter, epochs=int(pol["epochs"]), batch_size=BS,
         weights_folder=mwf, verbose=False)
n1 = len(of.labels_mc)+len(of.labels_data); n2 = len(of.labels_mc)+len(of.labels_gen)
i1 = np.arange(n1); np.random.shuffle(i1)
i2 = np.arange(n2); np.random.shuffle(i2)
NT = of.num_steps_gen*of.BATCH_SIZE; NTE = int((1-of.train_frac)*NT)
take = NT-NTE; vn = (NTE//of.BATCH_SIZE)*of.BATCH_SIZE
def ck(wf,it,st):
    f = os.path.join(wf,"OmniFold_%s_iter%d_step%d_final.weights.h5"%(MF,it,st))
    return f if os.path.exists(f) else os.path.join(wf,"OmniFold_%s_iter%d_step%d.weights.h5"%(MF,it,st))
m2.load_weights(ck(mwf,niter-2,2))
w2p = np.asarray(_engine_reweighter(m2,BS).reweight((gen,gen_evt),m2,batch_size=BS),np.float64)
pp = np.ones(len(pass_gen)); pp[pass_gen] = w2p[pass_gen]
m1.load_weights(ck(mwf,niter-1,1))
w1 = np.asarray(_engine_reweighter(m1,1000).reweight((reco,reco_evt),m1,batch_size=1000),np.float64)
ic = np.ones(len(pass_reco)); ic[pass_reco] = w1[pass_reco]
pull = pp*ic
labels = np.concatenate((of.labels_mc, of.labels_gen)).astype(np.float64)
wts = np.concatenate((mc.weight*mc.pass_gen, mc.weight*pull*mc.pass_gen)).astype(np.float64)

rs = np.random.RandomState(a.c2_seed); alt = rs.permutation(n2)
pos = alt[:vn]
lab = labels[pos]; wv = wts[pos]; rows = (pos % len(pass_gen)).astype(np.int64)
OBJ = hashlib.sha256(lab.tobytes()+wv.tobytes()+rows.tobytes()).hexdigest()
print("[c2] %s C2 seed %d, %d rows, objective digest %s" % (tag, a.c2_seed, len(rows), OBJ[:16]), flush=True)

Wn = [np.asarray(x,np.float64) for x in
      (lambda m: (m.load_weights(ck(nom_wf,niter-1,2)) or m.model.get_weights()))(m2)]
Wm = [np.asarray(x,np.float64) for x in
      (lambda m: (m.load_weights(ck(mwf,niter-1,2)) or m.model.get_weights()))(m2)]
def loss_at(t):
    assert hashlib.sha256(lab.tobytes()+wv.tobytes()+rows.tobytes()).hexdigest() == OBJ, "objective changed"
    m2.model.set_weights([x + t*(y2-x) for x, y2 in zip(Wn, Wm)])
    tot = 0.0
    for s in range(0, len(rows), BS):
        r = rows[s:s+BS]
        lg = np.asarray(m2.model([tf.convert_to_tensor(gen[r],tf.float32),
                                  tf.convert_to_tensor(gen_evt[r],tf.float32)],training=False))[:,0].astype(np.float64)
        z = lab[s:s+BS]
        tot += float((wv[s:s+BS]*(np.maximum(lg,0)-lg*z+np.log1p(np.exp(-np.abs(lg))))).sum())
    return tot/len(rows)
L0 = loss_at(0.0); L1t = loss_at(1.0)
C2 = L0 - L1t
sw = json.load(open(a.sweep_json))["members"][tag]["dL_by_rowset"]
A, B, C1 = sw["A_heldout_primary"], sw["B_train_region"], sw["C_independent_perm"]
w = float(take)/float(n2)
Cpred = w*B + (1-w)*A
r1_ = C1 - Cpred; r2_ = C2 - Cpred
same_sign = (r1_ > 0) == (r2_ > 0)
if abs(r2_) <= 5.5e-04: v = "SAMPLING NOISE -- C2 in family with the other members' residuals"
elif abs(r2_) >= 1.4e-03 and same_sign: v = "NOT SAMPLING -- C is stably low; the SPLIT-ERROR branch is live"
else: v = "UNRESOLVED -- licenses neither"
out = {"schema":"r5-c2-discriminator-v1","member":tag,"c1_seed":a.c1_seed,"c2_seed":a.c2_seed,
       "A":A,"B":B,"w":w,"C_pred":Cpred,"C1":C1,"C2":C2,
       "residual_C1":r1_,"residual_C2":r2_,"same_sign":bool(same_sign),
       "leverage_abs_B_minus_A":abs(B-A),"residual_C2_over_leverage":abs(r2_)/abs(B-A),
       "objective_digest":OBJ,"L_at_t0":L0,"L_at_t1":L1t,"VERDICT":v}
print("[c2] C_pred %.6e  C1 %.6e (resid %+.3e)  C2 %.6e (resid %+.3e)  same sign %s"
      % (Cpred, C1, r1_, C2, r2_, same_sign), flush=True)
print("[c2] VERDICT: %s" % v, flush=True)

# Run provenance INSIDE the artifact. Without it the FILENAME is load-bearing: two arms
# cannot be told apart by content, so byte-identity is ambiguous between a perfectly
# reproducible pair and a copy of one arm over the other. Recording it here makes the
# overwrite hazard detectable after the fact rather than only preventable before it.
import socket as _sock, datetime as _dt
_RUN_PROVENANCE = {
    "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
    "slurm_step_id": os.environ.get("SLURM_STEP_ID"),
    "slurm_nodelist": os.environ.get("SLURM_JOB_NODELIST"),
    "hostname": _sock.gethostname(),
    "run_started_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
    "argv": sys.argv,
}
print("[c2] run provenance:", _RUN_PROVENANCE, flush=True)
out["run_provenance"] = _RUN_PROVENANCE
json.dump(out, open(a.json,"w"), indent=1, default=float)
print("[c2] wrote", a.json)
