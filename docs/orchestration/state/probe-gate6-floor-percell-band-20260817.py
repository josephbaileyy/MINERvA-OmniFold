import numpy as np

D = "nd-unfolding/pet/fullevent_floor_42_0"
NPP = 19
X = []
for n in (2, 3, 4, 5):
    z = np.load(f"{D}/draw_{n}/pet_fullevent_floor_draw{n}_weights.npz", allow_pickle=True)
    X.append(np.asarray(z["central_vector"]))
    m = np.asarray(z["reported_bin_mask"], bool)
    z.close()
X = np.array(X)
r = X.max(0) - X.min(0)
mu = X.mean(0)
liv = mu > 0
rel = np.full(285, np.nan)
rel[liv] = r[liv] / mu[liv]
print(f"  GLOBAL                 live {int(liv.sum()):3d}  median {np.nanmedian(rel[liv]):.4%}"
      f"  max {np.nanmax(rel[liv]):.4%}")


def band(lo, hi, label):
    c = [k for k in range(285) if lo <= (k % NPP) <= hi and liv[k]]
    tot = sum(1 for k in range(285) if lo <= (k % NPP) <= hi)
    print(f"  {label:22s} bins {lo}-{hi}  live {len(c):3d} of {tot:3d} grid cells"
          f"  median {np.median(rel[c]):.4%}  max {np.nanmax(rel[c]):.4%}")


band(10, 15, "6-20 GeV  CORRECT")
band(9, 16, "5-40 GeV  my error")
