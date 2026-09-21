import numpy as np, hashlib
F="/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/uq_5d/z_pilot_20260916_a5/z-null.npz"
h=hashlib.sha256()
with open(F,'rb') as f:
    for b in iter(lambda: f.read(1<<22), b''): h.update(b)
d=h.hexdigest()
EXP="cb82fc3285c981b91625530d48c14ff5554db5154db298a3144a57520633d77e"
print("digest        :", d)
print("matches claim :", d==EXP)
z=np.load(F, allow_pickle=True)
print("keys present  :", sorted(z.files))
x1,x2,mp = z["x_cv"], z["x_cv2"], z["support_mask"].astype(bool)
m = x1 > 0.0                                   # recompute the predicate, do not apply theirs
print()
print("C1  n bins with x_cv > 0        : %d        (claim 10694)" % int(m.sum()))
print("C2  mask == persisted support   : %s     (claim: equal)" % bool(np.array_equal(m, mp)))
a,b = x1[m], x2[m]
rel = np.abs(b-a)/a                            # per-bin |x_cv2-x_cv|/x_cv on the reported support
print()
print("C3  max per-bin rel             : %.6e   (claim 1.755272e-12)" % rel.max())
print("C4  99.9th percentile           : %.6e   (claim 1.318750e-12)" % np.percentile(rel,99.9))
print("C5  median                      : %.6e   (claim 6.341524e-14)" % np.median(rel))
print("C6  n bins above 1e-10          : %d            (claim 0)" % int((rel>1e-10).sum()))
i=int(np.argmin(a))
print()
print("C7  smallest reported bin x_cv  : %.6e   (claim 1.009379e-50)" % a[i])
print("    its per-bin rel movement    : %.6e   (claim 4.880054e-14)" % rel[i])
q=float((rel<rel[i]).mean())
print("    'among the most stable'     : it is at the %.1f percentile of |rel| (lower = more stable)" % (100*q))
print("    bins strictly more stable   : %d of %d" % (int((rel<rel[i]).sum()), rel.size))
num=float(np.linalg.norm(b-a)); den=float(np.linalg.norm(a))
print()
print("C8  global r_null               : %.6e   (claim 4.452000e-14)" % (num/den))
print("    full precision              : %.17e" % (num/den))
print()
print("--- context for the judgement question, not part of the claim ---")
print("    five significant figures  => ~5e-6 relative (half a unit in the 5th)")
print("    max per-bin rel / 5e-6    = %.3e" % (rel.max()/5e-6))
print("    max per-bin rel / 0.05    = %.3e" % (rel.max()/0.05))
import numpy as np
from scipy.stats import spearmanr
F="/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/uq_5d/z_pilot_20260916_a5/z-null.npz"
z=np.load(F, allow_pickle=True)
x1,x2 = z["x_cv"], z["x_cv2"]
m = x1>0.0; a,b = x1[m], x2[m]
rel = np.abs(b-a)/a
print("=== THE CHECK THAT ACTUALLY ANSWERS THE BLOCK: does instability concentrate in SMALL bins? ===")
print("    (the blocking lane's concern was a large relative move in ONE SMALL bin)")
rho,p = spearmanr(a, rel)
print("    Spearman rho(x_cv, rel) = %+.4f   p = %.3g" % (rho, p))
print("    -> %s" % ("NEGATIVE: smaller bins ARE less stable" if rho<-0.1 else
                     "POSITIVE: larger bins are less stable" if rho>0.1 else
                     "no monotone size-instability relationship of consequence"))
print()
print("    %-22s %-10s %-13s %-13s" % ("decile of x_cv","n","median rel","max rel"))
q=np.quantile(a, np.linspace(0,1,11))
for k in range(10):
    sel=(a>=q[k]) & (a<=q[k+1] if k==9 else a<q[k+1])
    if sel.sum():
        print("    %-22s %-10d %-13.3e %-13.3e" % ("%d (%s)"%(k+1,"smallest" if k==0 else "largest" if k==9 else ""),
              sel.sum(), np.median(rel[sel]), rel[sel].max()))
print()
i=int(np.argmax(rel))
print("    the WORST bin: x_cv = %.6e, rel = %.6e, at the %.1f percentile of bin SIZE"
      % (a[i], rel[i], 100*float((a<a[i]).mean())))
print("    -> the largest relative movement sits in a bin of %s size, not the smallest"
      % ("below-median" if (a<a[i]).mean()<0.5 else "above-median"))
print()
print("=== and the 443-fold shape the blocking lane raised: is any bin near it? ===")
print("    bins with rel > 1e-9 : %d     > 1e-10 : %d     > 1e-11 : %d" %
      (int((rel>1e-9).sum()), int((rel>1e-10).sum()), int((rel>1e-11).sum())))
print("    max rel overall      : %.6e  -- a 443-fold move would be rel ~ 4.4e+02" % rel.max())
