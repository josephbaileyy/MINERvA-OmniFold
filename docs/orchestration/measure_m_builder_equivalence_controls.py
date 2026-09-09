"""Two controls the agreement result is worthless without."""
import sys
import numpy as np
sys.path.insert(0, "nd-unfolding")
import project_cov_nd as pcn
import p4_lib

AXES = ["pt","pz","eavail","q3","W"]
EDGES = [np.asarray(pcn.AXIS_EDGES[a], float) for a in AXES]
NB = [e.size-1 for e in EDGES]; DROP=4
KEEP=[a for i,a in enumerate(AXES) if i!=DROP]
NB_LOW=[n for i,n in enumerate(NB) if i!=DROP]
TH, TL = int(np.prod(NB)), int(np.prod(NB_LOW))

def derived(seed, frac):
    rng=np.random.default_rng(seed); mh=rng.random(TH)<frac
    idx=np.unravel_index(np.nonzero(mh)[0], tuple(NB))
    lc=tuple(idx[i] for i in range(5) if i!=DROP)
    ml=np.zeros(TL,bool); ml[np.ravel_multi_index(lc,tuple(NB_LOW))]=True
    return mh, ml

def b2(mh, ml):
    sr=np.nonzero(mh)[0]; di=np.full(TL,-1,np.int64); di[np.nonzero(ml)[0]]=np.arange(int(ml.sum()))
    return pcn.build_projection(AXES,KEEP,sr,tuple(NB),tuple(NB_LOW),di)

print("=== CONTROL 1: can the comparison DETECT a difference at all? ===")
mh, ml = derived(7, 0.02)
M1 = p4_lib.build_projection_M(EDGES, DROP, mh, ml)
M2, _ = b2(mh, ml)
print("  unperturbed exact-equal :", np.array_equal(M1, M2))
saved = pcn.AXIS_EDGES["W"]
try:
    pert = np.asarray(saved, float).copy(); pert[1] += 1e-9      # one W edge, 1 nanometre
    pcn.AXIS_EDGES["W"] = pert
    M2p, _ = b2(mh, ml)
    d = np.abs(M1 - M2p).max()
    print("  after perturbing ONE W edge by 1e-9: max|diff| = %.3e  -> detected %s" % (d, d > 0))
finally:
    pcn.AXIS_EDGES["W"] = saved
print("  restored:", np.array_equal(np.asarray(pcn.AXIS_EDGES["W"],float), np.asarray(saved,float)))

print()
print("=== CONTROL 2: where the SUPPORT MASKS BITE -- a high bin whose low image is UNREPORTED ===")
mh, ml = derived(7, 0.02)
drop_rows = np.nonzero(ml)[0][:5]            # un-report five low bins that ARE hit
ml_bitten = ml.copy(); ml_bitten[drop_rows] = False
print("  un-reported %d low bins that receive source cells" % len(drop_rows))
try:
    M1b = p4_lib.build_projection_M(EDGES, DROP, mh, ml_bitten)
    print("  builder1: returned M %s" % (M1b.shape,))
except Exception as e:
    print("  builder1: RAISED %s -- %s" % (type(e).__name__, str(e)[:90]))
M2b, dropped = b2(mh, ml_bitten)
print("  builder2: returned M %s, silently dropped %d source cells" % (M2b.shape, dropped))
