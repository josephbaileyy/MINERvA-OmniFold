"""KNOWN_ISSUES 84: compare the candidate rebuilt 2D statistical band with VL162, per bin.

Read-only on the production tree. The band definitions are analyze_uq.py's, imported
unchanged: per-bin mean and std (ddof = 1) of hXSec2D over replicas, reported bins = mean > 0,
and the reported-bin covariance np.cov. No rollup ROOT, figure or chi2 is produced; this
writes one JSON file.

  python compare_ki84_band.py --stage pilot --seeds 1-3
  python compare_ki84_band.py --stage full  --seeds 1-300
"""
import argparse, hashlib, json, os, sys
sys.dont_write_bytecode = True
import numpy as np

PROD_UQ = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/uq"
ROLLUP = os.path.join(PROD_UQ, "bootstrap_MEFHC_300/uq_covariance_boot300.root")
ROLLUP_SHA = "f7c734b1"
OUTROOT = "/pscratch/sd/j/josephrb/ki84-rebuild-20261006"
sys.path.insert(0, PROD_UQ)
import analyze_uq as au  # noqa: E402
import ROOT  # noqa: E402
ROOT.gROOT.SetBatch(True)


def seeds(spec):
    a, _, b = spec.partition("-")
    return list(range(int(a), int(b or a) + 1))


def load(path, names):
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise SystemExit(f"[FAIL] cannot open {path}")
    out = {}
    for n in names:
        h = f.Get(n)
        if not h:
            raise SystemExit(f"[FAIL] {n} missing from {path}")
        out[n] = au.th2_to_array(h)
    f.Close()
    return out


def stats(X):
    mean = X.mean(0)
    std = X.std(0, ddof=1)
    rep = mean > 0
    rel = np.where(rep, std / np.where(rep, mean, 1), np.nan)
    Xrep = X.reshape(X.shape[0], -1)[:, rep.ravel(order="C")]
    cov = np.cov(Xrep, rowvar=False)
    return mean, std, rel, rep, cov


def q(a):
    a = np.asarray(a, float)
    return {"n": int(a.size), "median": float(np.median(a)), "p16": float(np.percentile(a, 16)),
            "p84": float(np.percentile(a, 84)), "min": float(a.min()), "max": float(a.max())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["pilot", "full"], required=True)
    ap.add_argument("--seeds", required=True)
    ap.add_argument("--binsets", default=os.path.join(OUTROOT, "tools/ki84_binsets.json"))
    args = ap.parse_args()
    S = seeds(args.seeds)
    newdir = os.path.join(OUTROOT, "pilot" if args.stage == "pilot" else "replicas")
    names = ["hXSec2D", "hUnfold2D", "hOFCompleteness2D"]
    new, old = [], []
    for s in S:
        pn = os.path.join(newdir, f"2d_xsec_MEFHC_5iter_lgbm_boot{s}.root")
        if not os.path.exists(pn + ".done"):
            raise SystemExit(f"[FAIL] {pn} has no .done marker")
        new.append(load(pn, names))
        old.append(load(os.path.join(PROD_UQ, f"2d_xsec_MEFHC_5iter_lgbm_boot{s}.root"), names))

    Xn = np.stack([d["hXSec2D"] for d in new])
    Xo = np.stack([d["hXSec2D"] for d in old])
    Un = np.stack([d["hUnfold2D"] for d in new])
    Uo = np.stack([d["hUnfold2D"] for d in old])
    Cn = np.stack([d["hOFCompleteness2D"] for d in new])
    Co = np.stack([d["hOFCompleteness2D"] for d in old])
    sup = Co[0] > 0

    per_seed = []
    for k, s in enumerate(S):
        same_u = bool(np.array_equal(Un[k], Uo[k]))
        du = np.abs(Un[k][sup] / np.where(Uo[k][sup] != 0, Uo[k][sup], 1) - 1)
        # If U is unchanged, the new xsec is the old one times the old completeness.
        xr = Xn[k][sup] / np.where(Xo[k][sup] != 0, Xo[k][sup], 1)
        per_seed.append({
            "seed": s,
            "new_c_max_abs_dev_from_1": float(np.abs(Cn[k][sup] - 1).max()),
            "old_c_range": [float(Co[k][sup].min()), float(Co[k][sup].max())],
            "hUnfold2D_bit_identical_to_VL162": same_u,
            "hUnfold2D_max_rel_diff": float(du.max()),
            "xsec_ratio_over_old_c_max_abs_dev": float(np.abs(xr / Co[k][sup] - 1).max()),
        })
    out = {"stage": args.stage, "seeds": [S[0], S[-1]], "n": len(S),
           "new_dir": newdir, "old_dir": PROD_UQ, "per_seed": per_seed}

    if args.stage == "full":
        rsha = hashlib.sha256(open(ROLLUP, "rb").read()).hexdigest()
        f = ROOT.TFile.Open(ROLLUP)
        cov_roll = au.th2_to_array(f.Get("hCov2D_reported"))
        f.Close()
        mo, so, relo, repo, covo = stats(Xo)
        mn, sn, reln, repn, covn = stats(Xn)
        out["control_old_reproduces_rollup"] = {
            "rollup_sha256": rsha, "sha_prefix_ok": rsha.startswith(ROLLUP_SHA),
            "cov_max_abs_diff_over_max": float(np.abs(covo - cov_roll).max() / np.abs(cov_roll).max()),
        }
        if not np.array_equal(repo, repn):
            raise SystemExit("[FAIL] reported-bin sets differ")
        ratio = sn[repo] / so[repo]
        relratio = reln[repo] / relo[repo]
        mshift = mn[repo] / mo[repo]
        grid_ratio = np.full(so.shape, np.nan)
        grid_ratio[repo] = ratio
        bs = json.load(open(args.binsets))
        def sub(key):
            idx = [tuple(b) for b in bs[key]]
            return [float(grid_ratio[i, j]) for i, j in idx]
        out["band"] = {
            "n_reported": int(repo.sum()),
            "sigma_new_over_old": q(ratio),
            "rel_new_over_old": q(relratio),
            "mean_new_over_old": q(mshift),
            "frac_bins_sigma_ratio_gt_1": float((ratio > 1).mean()),
            "sqrt_trace_cov": {"old": float(np.sqrt(np.trace(covo))), "new": float(np.sqrt(np.trace(covn))),
                               "new_over_old": float(np.sqrt(np.trace(covn) / np.trace(covo)))},
            "median_rel_spread_pct": {"old": float(100 * np.median(relo[repo])),
                                      "new": float(100 * np.median(reln[repo]))},
            "binsets": {k: {"bins": bs[k], "sigma_new_over_old": sub(k), "summary": q(sub(k))}
                        for k in ("low_c2_lt_0p85", "rms_gt_2", "pz_40_60_column")},
            "per_bin_sigma_new_over_old_grid": [[None if np.isnan(v) else float(v) for v in row]
                                                for row in grid_ratio],
        }
        out["all_new_c_unit"] = bool(max(p["new_c_max_abs_dev_from_1"] for p in per_seed) < 1e-12)
        out["n_hUnfold2D_bit_identical"] = int(sum(p["hUnfold2D_bit_identical_to_VL162"] for p in per_seed))
    path = os.path.join(OUTROOT, f"compare_{args.stage}.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "band"}, indent=1)[:4000])
    if "band" in out:
        b = out["band"]
        print(json.dumps({k: b[k] for k in b if k not in ("binsets", "per_bin_sigma_new_over_old_grid")}, indent=1))
        print(json.dumps({k: b["binsets"][k]["summary"] for k in b["binsets"]}, indent=1))
    print(f"[OK] wrote {path}")


if __name__ == "__main__":
    main()
