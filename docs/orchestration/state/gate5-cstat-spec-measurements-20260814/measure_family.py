"""Cross-replica structure of the object C_stat would covary, measured on what exists so far.

Answers, with numbers a spec can pin: the dimension, the flattening, whether edges are shared,
how many directions carry zero variance structurally, and whether the nominal extraction that
centring might use even exists.
"""
import glob, json, os
import numpy as np

ROOT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50/replicas"
paths = sorted(glob.glob(os.path.join(ROOT, "replica_*/extraction/GATE5_REPLICA_XSEC.npz")))
print(f"xsec artifacts present: {len(paths)} of 50")
print(f"markers (.done) present: {sum(os.path.exists(p + '.done') for p in paths)}")

X, idx, seeds, e0ref, e1ref, tots = [], [], [], None, None, []
for p in paths:
    with np.load(p, allow_pickle=True) as z:
        X.append(np.asarray(z["xsec"], float))
        idx.append(int(np.asarray(z["replica_index"])))
        seeds.append(int(np.asarray(z["bootstrap_seed"])))
        tots.append(float(np.asarray(z["total_sigma_cm2_per_nucleon"])))
        e0 = np.asarray(z["edges_pt"], float); e1 = np.asarray(z["edges_pparallel"], float)
        if e0ref is None: e0ref, e1ref = e0, e1
        assert np.array_equal(e0, e0ref) and np.array_equal(e1, e1ref), f"EDGES DIFFER at {p}"
X = np.stack(X)
print(f"\nedges identical across all {len(paths)}: True")
print(f"stack shape = {X.shape}  (members, n_pt, n_pparallel)")

N, npt, npp = X.shape
D = npt * npp
print(f"\n*** DIMENSION D = {npt} x {npp} = {D} bins ***")
print(f"*** MEMBERS N = 50 (declared) -> covariance rank <= N-1 = 49 ***")
print(f"*** D ({D}) > N-1 (49): SINGULAR by a factor of {D/49:.1f} ***")

print(f"\nreplica_index present: {sorted(idx)}")
print(f"seed == 50000+index for all: {all(s == 50000+i for s,i in zip(seeds,idx))}")
print(f"replica indices distinct: {len(set(idx))} of {len(idx)}")

F = X.reshape(N, D)
print(f"\n--- flattening check (telemetry says pt-major row-major) ---")
print(f"C-order reshape reproduces cell = i_pt*n_pp + i_pp: "
      f"{np.array_equal(F[0], X[0].ravel(order='C'))}")

zero_all = np.all(F == 0.0, axis=0)
nz_any  = ~zero_all
print(f"\n--- zero-variance directions ---")
print(f"bins exactly zero in EVERY member : {int(zero_all.sum())}")
print(f"bins nonzero in at least one      : {int(nz_any.sum())}")
sd = F.std(axis=0, ddof=1)
print(f"bins with zero sample sd          : {int((sd == 0).sum())}")
print(f"bins with sd > 0                  : {int((sd > 0).sum())}   <-- effective varying directions")
print(f"still >> 49: {int((sd>0).sum()) > 49}")

print(f"\n--- scale of the object ---")
print(f"total_sigma across members: min {min(tots):.6e} max {max(tots):.6e} "
      f"spread {(max(tots)-min(tots))/np.mean(tots)*100:.3f}%")
print(f"distinct totals: {len(set(tots))} of {len(tots)}  <-- draw live in the extracted xsec")
m = F.mean(axis=0)
with np.errstate(divide="ignore", invalid="ignore"):
    rel = np.where(m > 0, sd/m, np.nan)
print(f"per-bin relative sd (varying bins): median {np.nanmedian(rel[sd>0]):.4f} "
      f"max {np.nanmax(rel[sd>0]):.4f}")

print(f"\n--- what an N={len(paths)} covariance looks like RIGHT NOW (illustrative only) ---")
C = np.cov(F, rowvar=False, ddof=1)
print(f"C shape {C.shape}, numpy matrix_rank = {np.linalg.matrix_rank(C)} "
      f"(expected <= {len(paths)-1})")

print(f"\n--- cell counts from telemetry ---")
with np.load(paths[0], allow_pickle=True) as z:
    tel = z["extraction_telemetry"].item()
for k in ("n_cells", "n_cells_populated", "n_cells_masked_zero_acceptance",
          "n_cells_no_denominator", "shape", "bin_order", "truth_denominator_coverage",
          "data_pot", "n_nucleons"):
    print(f"  {k} = {str(tel.get(k))[:110]}")

print(f"\n--- does a NOMINAL extraction exist for the centring choice? ---")
for pat in ("/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/**/*XSEC*.npz",
            "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/**/*XSEC*.npz"):
    hits = [h for h in glob.glob(pat, recursive=True) if "cstat_n50" not in h]
    for h in hits[:12]:
        print(f"  {h}  {os.path.getsize(h)}")
