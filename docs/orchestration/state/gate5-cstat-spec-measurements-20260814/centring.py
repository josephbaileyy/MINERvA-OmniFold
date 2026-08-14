"""Quantify the CENTRING consequence, so the spec's choice is made on a number not a preference.

Compares trace/diagonal of the replica-mean-centred second moment against the same object
centred on the only 285-bin nominal-like artifact that exists -- which is explicitly marked
NONQUOTABLE-DIAGNOSTIC.
"""
import glob, os
import numpy as np

ROOT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50/replicas"
NOM = ("/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/"
       "fullevent_diagnostic_nonquotable/NONQUOTABLE-DIAGNOSTIC.xsec.slurm-56527676.npz")

paths = sorted(glob.glob(os.path.join(ROOT, "replica_*/extraction/GATE5_REPLICA_XSEC.npz")))
X = []
for p in paths:
    with np.load(p, allow_pickle=True) as z:
        X.append(np.asarray(z["xsec"], float).ravel(order="C"))
F = np.stack(X); N, D = F.shape
print(f"members N={N}  dimension D={D}")

with np.load(NOM, allow_pickle=True) as z:
    nom = np.asarray(z["xsec"], float).ravel(order="C")
    ne0 = np.asarray(z["edges_pt"], float); ne1 = np.asarray(z["edges_pparallel"], float)
with np.load(paths[0], allow_pickle=True) as z:
    re0 = np.asarray(z["edges_pt"], float); re1 = np.asarray(z["edges_pparallel"], float)
print(f"nominal edges identical to replica edges: "
      f"{np.array_equal(ne0,re0) and np.array_equal(ne1,re1)}")
print(f"nominal zero-pattern identical: "
      f"{np.array_equal(nom==0, F[0]==0)}")

mean = F.mean(axis=0)
Cm = (F-mean).T @ (F-mean) / (N-1)          # mean-centred, 1/(N-1)
Cn = (F-nom ).T @ (F-nom ) / (N-1)          # nominal-centred, same normalisation
off = mean - nom
print(f"\n--- centring consequence ---")
print(f"trace mean-centred    = {np.trace(Cm):.6e}")
print(f"trace nominal-centred = {np.trace(Cn):.6e}")
print(f"ratio                 = {np.trace(Cn)/np.trace(Cm):.3f}x")
print(f"  the excess is the offset term N/(N-1)*|mean-nominal|^2:")
print(f"  |mean-nom|^2 * N/(N-1) = {(off@off)*N/(N-1):.6e}")
print(f"  trace_nom - trace_mean = {np.trace(Cn)-np.trace(Cm):.6e}")
tot_mean = F.sum(axis=1).mean(); tot_nom = nom.sum()
print(f"\ntotal xsec: replica mean {tot_mean:.6e}  nominal {tot_nom:.6e}  "
      f"offset {100*(tot_mean-tot_nom)/tot_mean:+.3f}%")
print(f"\n=> nominal-centring inflates the variance by {100*(np.trace(Cn)/np.trace(Cm)-1):.1f}% "
      f"purely from a bias offset that is NOT a statistical fluctuation.")
print(f"\n--- rank, stated for the record ---")
print(f"rank(mean-centred)    = {np.linalg.matrix_rank(Cm)}  (<= N-1 = {N-1})")
print(f"rank(nominal-centred) = {np.linalg.matrix_rank(Cn)}  (<= N   = {N}, centring on a")
print(f"    point NOT the sample mean buys one extra rank and it is the bias direction)")
