"""P4 retry walltime projection from measured loop rates (director decision 2026-10-12 ~21:45Z).
Entry counts (M) from each job's own progress counters; elapsed minutes from sacct.
Model: elapsed = s + a*N_truth + b*N_sig_done [+ c*N_reco_bkg + d*N_data for completed jobs].
"""
import numpy as np
# complete: (N_truth, N_reco, N_data, T)
done = {"1B": (6.044672, 2.050050, 0.584997, 35 + 37/60), "1C": (11.545183, 3.914293, 1.344315, 63 + 56/60),
        "1L": (3.269023, 1.056661, 0.395771, 14 + 16/60)}
# partial: (N_truth done, N_sig done, elapsed)  [truth loop finished in all of these]
part = {"1A": (22.191105, 7.601356, (13*60+40+57/60) - (12*60+34+7/60)),     # sig loop end ~ log mtime
        "1D": (33.578119, 7.65, 69 + 1/60), "1E": (28.117140, 5.46, 56 + 40/60), "1F": (39.082827, 5.18, 55 + 27/60),
        "1G": (32.462689, 3.72, 42 + 14/60), "1M": (50.435976, 1.56, 20 + 42/60)}
rows, y = [], []
for k, (nt, nr, nd, T) in done.items(): rows.append([1, nt, nr, nr, nd]); y.append(T)
for k, (nt, ns, T) in part.items(): rows.append([1, nt, ns, 0, 0]); y.append(T)
A, y = np.array(rows), np.array(y)
from scipy.optimize import nnls
coef, res = nnls(A, y)
s, a, b, c, d = coef
print(f"fit (min, min/M entries): setup {s:.2f}  truth {a:.3f}  sig {b:.3f}  bkg {c:.3f}  data {d:.3f}  rss {res:.2f}")
for k, r, t in zip(list(done) + list(part), A, y): print(f"  {k}: measured {t:6.1f}  fitted {r @ coef:6.1f}")
# 1M-own signal rate (director: use 1M's rate): all of 1M's elapsed after the truth loop at the fitted truth rate
b1M = (part["1M"][2] - s - a * part["1M"][0]) / part["1M"][1]
print(f"1M own sig rate (elapsed - setup - fitted truth)/N_sig: {b1M:.3f} min/M; conservative (all elapsed)/N_sig: {part['1M'][2]/part['1M'][1]:.2f}")
# post-signal (bkg + data) per reco entry, from completed jobs, model-free upper bound: (T - s - a Nt - b Nr)/Nr
for k, (nt, nr, nd, T) in done.items(): print(f"  {k} post-signal per reco entry: {(T - s - a*nt - b*nr)/nr:.2f} min/M")

# Per-job projection: T = a*N_truth + max(b_fit, b_1M)*N_reco + post*N_reco, post = worst completed post-signal rate.
post = max((T - s - a*nt - b*nr)/nr for nt, nr, nd, T in done.values())
bs = max(b, b1M)
# 1N never ran: entries from its MC size (1.102725 TB) at the worst measured entries/TB (1A: reco 7.601356/0.707,
# truth 22.191105/0.707); 1O (0.331 TB) and 1P (0.438 TB) the same way.
tb = {"1A": 0.706929, "1N": 1.102725, "1O": 0.331082, "1P": 0.438316}
per_tb_r, per_tb_t = 7.601356 / tb["1A"], 22.191105 / tb["1A"]
jobs = {"1A": (22.191105, 7.601356), "1D": (33.578119, 11.360928), "1E": (28.117140, 9.498175),
        "1F": (39.082827, 12.905280), "1G": (32.462689, 10.935664), "1M": (50.435976, 16.317862),
        "1N": (per_tb_t * tb["1N"], per_tb_r * tb["1N"]), "1O": (per_tb_t * tb["1O"], per_tb_r * tb["1O"]),
        "1P": (per_tb_t * tb["1P"], per_tb_r * tb["1P"])}
cap = {"1A": 6, "1D": 6, "1E": 6, "1F": 6, "1G": 6, "1M": 8, "1N": 6, "1O": 2, "1P": 2}
print(f"projection rates: truth {a:.3f}, signal {bs:.3f}, post {post:.2f} min/M")
for k, (nt, nr) in jobs.items():
    T = a*nt + bs*nr + post*nr
    print(f"  {k}: N_truth {nt:6.2f} M  N_reco {nr:6.2f} M  projected {T:6.1f} min = {T/60:.2f} h; x1.5 = {1.5*T/60:.2f} h;"
          f" cap {cap[k]} h {'OK' if 1.5*T/60 <= cap[k] else 'SHORT'}")
