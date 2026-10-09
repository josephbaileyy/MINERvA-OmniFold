import json, sys, numpy as np
W = sys.argv[1]
d = np.load(W + "/docs/orchestration/state/coverage-2d-20261005/interim.npz")
band = json.load(open(W + "/docs/orchestration/state/ki84-rebuild-20261006/vl170_band.json"))
U, T, rep = d["U"], d["T"], d["reported"].astype(bool)
def score(mean, sigma):
    r = np.where(rep, sigma / np.where(mean > 0, mean, 1), np.nan)
    z = (U - T) / (r * T)
    z = z[:, rep]
    return dict(C1=float((abs(z) <= 1).mean()), C2=float((abs(z) <= 2).mean()),
                pull_mean=float(z.mean()), pull_rms=float(np.sqrt((z*z).mean())), n_bins=int(rep.sum()), n_toys=int(U.shape[0]))
print("VL162(prod in npz)", score(d["prod_mean"], d["prod_sigma"]))
print("VL170", score(np.array(band["mean_vl170"]), np.array(band["sigma_vl170"])))
