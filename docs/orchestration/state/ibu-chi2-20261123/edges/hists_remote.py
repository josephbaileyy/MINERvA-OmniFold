# Run read-only on login02 (root_6_28 env), cwd /dev/shm, stdout -> hists.json. Reads this lane's merged evloop output only.
import ROOT, numpy as np, json
f = "/pscratch/sd/j/josephrb/ibuchi-evloop-20261123/out/runEventLoopOmniFold_MEFHC.root"
a = ROOT.RDataFrame("data", f).Define("mp_i", "(int)measured_pass").AsNumpy(["measured", "measured_pz", "mp_i"])
pt, pz, ok = np.asarray(a["measured"], float), np.asarray(a["measured_pz"], float), np.asarray(a["mp_i"]) != 0
PZ = [1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 15, 20, 40, 60]
out = {}
for name, PT in (("ours", [0, .07, .15, .25, .33, .40, .47, .55, .70, .85, 1.00, 1.25, 1.50, 2.50, 4.50]),
                 ("E", [0, .075, .15, .25, .325, .40, .475, .55, .70, .85, 1.00, 1.25, 1.50, 2.50, 4.50])):
    H, _, _ = np.histogram2d(pt[ok], pz[ok], bins=[PT, PZ]); out[name] = H.ravel().tolist()
print(json.dumps(out))
