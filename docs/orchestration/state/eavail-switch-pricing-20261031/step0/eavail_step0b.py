#!/usr/bin/env python3
"""Step 0b of the E_avail 139.57 MeV pricing (the referee's additions): read-only, login node, no Slurm, O_NOATIME.

(a) First-order UNFOLDED effect. The S1 products store no per-event OmniFold weight (s5p_numerics.py:214 writes
    xsec_flat and shape; s5c_unfold.py:124-138 histograms wpush x w_truth without saving wpush). So each truth event e
    carries its nominal 135 fine cell k's unfolded-to-prior ratio: u_e = w_e * X_k / D_k, with X_k = xsec_flat_k * vol_k
    from the central product (data_b-_j-, = data_R = P5, fb5cc679...) and D_k the 135 truth denominator (bitwise
    of_inputs_5d.npz's denom_nd, step 0's control C1). Every MCgen row passes truth, so completeness is 1 and the flux
    factor cancels (the shift leaves p_T unchanged). Under 135, sum_{e in cell} u_e = sum_{k in cell} X_k = f_cell
    (control C2, checked offline against the data product). The shift moves e with its u_e.
(c) Exactness: the multiset of (MC, MC_pz, MC_eavail, MC_q3, MC_W, MC_npip, w_truth) tuples of mc_truth_denom equals
    that of mc_signal_reco; min of E_avail - 0.00457 * MC_npip.
(e) Branch presence (MC_npip, MC_eavail in mc_signal_reco and mc_truth_denom) in the 10 lateral omnifiles, the 5B merges,
    MP-1's zero loops (5B's source), the 12 per-playlist universe loops and their merge; the bank cv.npz's keys.
Every opened file's atime is checked unchanged (exit 4 otherwise). Usage: python step0b.py --out DIR --fine-map F
"""
import argparse
import glob
import hashlib
import json
import os
import sys
import time

import numpy as np
import uproot

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eavail_step0 as s0  # noqa: E402  (FINE, DM, fine_index, select, read_tree, open_noatime, check_atime, STATS)

P = "/pscratch/sd/j/josephrb"
N = f"{P}/MINERvA-OmniFold/nd-unfolding"
CENTRAL = f"{P}/s5p-20260926/runs/s2/num/data/data_b-_j-.npz"
CENTRAL_SHA = "fb5cc6798b97b5902ad8f0fecbc49990271f7772f98d3063c1dc8596340e680c"   # s1_assemble.CENTRAL_SHA256
LAT = sorted(glob.glob(f"{N}/active_universe_5d/standard/merged/runEventLoopOmniFold_5D_MEFHC_active_*.root"))
B5 = sorted(glob.glob(f"{P}/fd-ct-5b-20261030/merged/runEventLoopOmniFold_5D_*_zero.root"))
MP1Z = sorted(glob.glob(f"{P}/measurement-paper/phase1/mp1/s1/evloop/zero/runEventLoopOmniFold_5D_*_zero.root"))
UNI = sorted(glob.glob(f"{N}/runEventLoopOmniFold_5D_*_universes_full_bkgaware.root"))
BANK = f"{N}/bank_sweep_5d_bkgaware/cv.npz"


def vol():
    shape = [len(e) - 1 for e in s0.FINE]
    idx = np.unravel_index(np.arange(int(np.prod(shape))), shape)
    v = np.ones(idx[0].size)
    for k, e in enumerate(s0.FINE):
        v *= np.diff(np.asarray(e))[idx[k]]
    return v


def branches(path):
    with s0.open_noatime(path) as fh:
        f = uproot.open(fh, object_cache=None, array_cache=None)
        out = {}
        for t in ("mc_signal_reco", "mc_truth_denom"):
            if t in f:
                ks = set(f[t].keys())
                out[t] = {"MC_npip": "MC_npip" in ks, "MC_eavail": "MC_eavail" in ks, "n_entries": int(f[t].num_entries)}
            else:
                out[t] = None
    s0.check_atime(path)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--fine-map", required=True)
    a = ap.parse_args()
    t0 = time.time()
    fm = np.load(a.fine_map)
    rec = {"schema": "eavail-step0b/1", "host": os.uname().nodename, "start_utc": time.strftime("%FT%TZ", time.gmtime()),
           "code_sha256": {"eavail_step0b.py": hashlib.sha256(open(__file__, "rb").read()).hexdigest(),
                           "eavail_step0.py": hashlib.sha256(open(s0.__file__, "rb").read()).hexdigest()}}

    # (e) first: metadata only
    rec["branches"] = {"lateral": {p: branches(p) for p in LAT}, "5B_merged": {p: branches(p) for p in B5},
                       "mp1_zero_loops": {p: branches(p) for p in MP1Z}, "universe_loops": {p: branches(p) for p in UNI}}
    with s0.open_noatime(BANK) as fh:
        rec["bank_cv_keys"] = sorted(np.load(fh).files)
    s0.check_atime(BANK)
    print(f"[e] branches read: {len(LAT)} lateral, {len(B5)} 5B, {len(MP1Z)} MP-1 zero, {len(UNI)} universe; "
          f"bank keys {len(rec['bank_cv_keys'])} ({time.time() - t0:.0f} s)", flush=True)

    # central product
    h = hashlib.sha256()
    with s0.open_noatime(CENTRAL) as fh:
        for b in iter(lambda: fh.read(1 << 24), b""):
            h.update(b)
    s0.check_atime(CENTRAL)
    rec["central_sha256_ok"] = h.hexdigest() == CENTRAL_SHA
    if not rec["central_sha256_ok"]:
        print("[STOP] central digest", flush=True); sys.exit(3)
    with s0.open_noatime(CENTRAL) as fh:
        xs = np.asarray(np.load(fh)["xsec_flat"], np.float64)
    s0.check_atime(CENTRAL)
    X = xs * vol()

    with s0.open_noatime(s0.OMNI) as fh:
        f = uproot.open(fh, object_cache=None, array_cache=None)
        pot_scale = float(f["dataPOTUsed"].member("fVal")) / float(f["mcPOTUsed"].member("fVal"))
        td = s0.read_tree(f, "mc_truth_denom")
        sg = s0.read_tree(f, "mc_signal_reco")
    s0.check_atime(s0.OMNI)
    print(f"[a] read central and trees ({time.time() - t0:.0f} s)", flush=True)

    # (c) tuple multiset identity, and the shifted minimum
    def tuples(t):
        m = np.column_stack([t[k] for k in s0.BRANCHES])
        return m[np.lexsort(m.T[::-1])]
    ta, tb = tuples(td), tuples(sg)
    rec["c_tuple_multiset_equal"] = bool(np.array_equal(ta, tb, equal_nan=True))
    rec["c_rows_nonfinite"] = {"truth_denom": int((~np.isfinite(ta)).any(axis=1).sum()),
                               "signal_reco": int((~np.isfinite(tb)).any(axis=1).sum())}
    rec["c_column_multiset_equal"] = {k: bool(np.array_equal(np.sort(td[k]), np.sort(sg[k]), equal_nan=True))
                                      for k in s0.BRANCHES}
    rec["c_sorted_tuple_rows_differing"] = int((~((ta == tb) | (np.isnan(ta) & np.isnan(tb)))).any(axis=1).sum())
    del ta, tb
    sh = td["MC_eavail"] - s0.DM * td["MC_npip"]
    fin = np.isfinite(sh)
    rec["c_min_eavail_139p57"] = float(np.min(sh[fin]))
    rec["c_rows_eavail_139p57_negative"] = int((sh[fin] < 0).sum())
    rec["c_rows_eavail_135_negative"] = int((td["MC_eavail"][fin] < 0).sum())
    del sg
    print(f"[c] tuple multiset equal: {rec['c_tuple_multiset_equal']}; min E' {rec['c_min_eavail_139p57']:.6g}", flush=True)

    # (a) first-order unfolded effect
    keep, w = s0.select(td, pot_scale)
    cols0 = [td["MC"][keep], td["MC_pz"][keep], td["MC_eavail"][keep], td["MC_q3"][keep], td["MC_W"][keep]]
    k0 = s0.fine_index(cols0)
    n = X.size
    wk = w[keep]
    D = np.bincount(k0[k0 >= 0], weights=wk[k0 >= 0], minlength=n)
    r = np.divide(X, D, out=np.zeros(n), where=D > 0)
    rec["a_fine_cells_X_nonzero_D_zero"] = int(((D == 0) & (X != 0)).sum())
    u = np.where(k0 >= 0, wk * r[np.maximum(k0, 0)], 0.0)
    cols1 = list(cols0); cols1[2] = cols0[2] - s0.DM * td["MC_npip"][keep]
    k1 = s0.fine_index(cols1)
    ea = np.unravel_index(np.arange(n), [len(e) - 1 for e in s0.FINE])[2]
    res = {}
    for tag, kk in (("135", k0), ("139.57", k1)):
        fine = np.bincount(kk[kk >= 0], weights=u[kk >= 0], minlength=n)
        res[tag] = {"cells": np.bincount(fm[fm >= 0], weights=fine[fm >= 0], minlength=16),
                    "ebins": np.bincount(ea, weights=fine, minlength=7)}
    rec["a_unfolded_cells_135"] = res["135"]["cells"].tolist()
    rec["a_unfolded_cells_139p57"] = res["139.57"]["cells"].tolist()
    rec["a_unfolded_cells_rel_change"] = ((res["139.57"]["cells"] - res["135"]["cells"]) / res["135"]["cells"]).tolist()
    rec["a_unfolded_ebins_rel_change"] = ((res["139.57"]["ebins"] - res["135"]["ebins"]) / res["135"]["ebins"]).tolist()
    rec["a_unfolded_net_16cell_rel"] = float((res["139.57"]["cells"].sum() - res["135"]["cells"].sum())
                                             / res["135"]["cells"].sum())
    rec["stat"] = s0.STATS
    rec["wall_s"] = time.time() - t0
    json.dump(rec, open(os.path.join(a.out, "step0b.json"), "w"), indent=1)
    print(f"[done] {rec['wall_s']:.0f} s; every atime unchanged", flush=True)


if __name__ == "__main__":
    main()
