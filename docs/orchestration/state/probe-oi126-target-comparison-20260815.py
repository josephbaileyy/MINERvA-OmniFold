"""Read-only cluster probe: target-level comparison of the nominal vs replica Stay-Positive targets.
Emits JSON on stdout so no number is transcribed by hand. Writes nothing."""
import numpy as np, json, math
from math import exp, factorial

R = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding"
NOM = R + "/g2_fullevent/gate2/final/G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy"
B = R + "/pet/fullevent_cstat_n50/replicas"

n = np.load(NOM)
N = len(n)
out = {"rows": int(N),
       "nominal_target": {"sum": float(n.sum()), "mean": float(n.mean()),
                          "min": float(n.min()), "max": float(n.max()),
                          "n_zero": int((n == 0).sum()),
                          "zero_fraction": float((n == 0).sum() / N)}}
sums, zfs = [], []
for i in range(8):
    a = np.load(f"{B}/replica_{i:02d}/target/GATE5_REPLICA_TARGET.npy")
    sums.append(float(a.sum())); zfs.append(float((a == 0).sum() / N))
    if i == 0:
        first = {"sum": float(a.sum()), "min": float(a.min()), "max": float(a.max()),
                 "n_zero": int((a == 0).sum())}
        m = n > 0
        r = a[m] / n[m]
        tot = int(m.sum())
        out["multiplicity"] = {
            "k": list(range(6)),
            "observed_fraction": [float(((r > k - 0.4) & (r < k + 0.4)).sum() / tot) for k in range(6)],
            "poisson1_pmf": [exp(-1) / factorial(k) for k in range(6)],
            "unassigned_fraction": float(1 - sum(((r > k - 0.4) & (r < k + 0.4)).sum() / tot for k in range(6))),
        }
        out["multiplicity"]["obs_over_pmf"] = [
            o / p for o, p in zip(out["multiplicity"]["observed_fraction"], out["multiplicity"]["poisson1_pmf"])]
        k1 = r[(r > 0.6) & (r < 1.4)]
        out["shared_renormalisation_on_multiplicity_1_rows"] = float(k1.mean())
        out["refinements_agree_to_percent"] = float(100 * abs(k1.mean() - 1))
out["replica_00_target"] = first
sums = np.array(sums); zfs = np.array(zfs)
out["replica_target_sums"] = {"n_replicas_read": len(sums), "mean": float(sums.mean()),
                              "sd": float(sums.std(ddof=1)),
                              "rel_sd": float(sums.std(ddof=1) / sums.mean()),
                              "nominal_over_mean": float(n.sum() / sums.mean())}
out["replica_zero_fraction"] = {"mean": float(zfs.mean()), "sd": float(zfs.std(ddof=1)),
                                "exp_minus_1": exp(-1),
                                "ratio_to_exp_minus_1": float(zfs.mean() / exp(-1))}
print(json.dumps(out))
