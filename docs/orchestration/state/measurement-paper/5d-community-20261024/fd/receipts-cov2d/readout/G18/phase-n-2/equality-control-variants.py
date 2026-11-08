import json, sys, numpy as np
T = sys.argv[1]; old = json.load(open(f"{T}/old.json")); M = "b1d56e4f08e62983784e34b2278f38a09a68eca0"
def w(name, d): json.dump(d, open(f"{T}/{name}.json", "w"), indent=1)
base = dict(old, M=M, utc="2026-11-08T03:00:00Z"); w("equal", base)
w("host", dict(base, host="login01"))
import copy; n = copy.deepcopy(base); n["null"]["q_joint"] += 1e-12; w("nested", n)
w("wrongM", dict(base, M="0"*40))
n = copy.deepcopy(base); n["code"]["driverSha256"] = "x"; w("code", n)
n = copy.deepcopy(base); n["extra"] = 1; w("extra", n)
z = dict(np.load(f"{T}/old.npz")); k = sorted(z)[0]; z[k] = z[k].copy(); z[k].flat[0] += 1
np.savez(f"{T}/bad.npz", **z); print("perturbed array", k)
