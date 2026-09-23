#!/usr/bin/env python3
"""KNOWN_ISSUES #26 / OI-31: sensitivity of the unfolded result to the 1.17 reco-E_avail scale.

The C++ event loop writes reco E_avail = 1.17 * (fuzz-subtracted tracker + ECAL recoil)
(`CVUniverse::NewEavail`, MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h) into exactly
three branches -- `sim_eavail` (signal MC reco), `sim_background_eavail` (background MC reco) and
`measured_eavail` (data) -- and into nothing else (no cut, no other derived variable reads it:
`runEventLoopOmniFold.cpp:1178,1460,1591`). Because the constant is a pure multiplicative factor,
changing it from 1.17 to k is EXACTLY equivalent to multiplying those three columns by
r = k / 1.17 after reading. This wrapper does that and then runs the unmodified production driver.

    python eavail_scale_study.py --driver 3d --scale-mc R --scale-data R -- <3D driver args>
    python eavail_scale_study.py --driver nd --scale-mc R --scale-data R -- <N-D driver args>

`--scale-mc` scales signal-MC reco and background-MC reco; `--scale-data` scales data. The
COMMON-SCALE study (the question of issue 26) sets both equal. Setting them unequal is a
NONQUOTABLE power control only (it proves the pipeline responds to reco E_avail at all).

Only reco-PASSING entries are scaled: the -9999 sentinel on non-passing signal entries is left as
is. Truth E_avail (`MC_eavail`) is never touched. Every patched reader counts its calls and the
wrapper refuses to report success unless each was called exactly once by the driver's main() --
so an alias that bypassed the patch fails loudly instead of producing an unscaled "result".
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
DRIVERS = {
    "3d": REPO / "3d-unfolding" / "unfold_3d_omnifold_unbinned.py",
    "nd": REPO / "nd-unfolding" / "unfold_nd_omnifold_unbinned.py",
}


def load_driver(path):
    spec = importlib.util.spec_from_file_location("eavail_scale_target", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _stats(x):
    x = np.asarray(x, float)
    ok = x > -9000.0
    return dict(n=int(x.size), n_valid=int(ok.sum()),
                sum_valid=float(x[ok].sum()), n_negative_valid=int((x[ok] < 0).sum()))


def patch_3d(mod, r_mc, r_data, log):
    orig_sig, orig_data, orig_bkg = mod.collect_signal_3d, mod.collect_data_3d, mod.collect_bkg_3d

    def sig(*a, **k):
        out = orig_sig(*a, **k)
        before = _stats(out["reco_ea"])
        m = out["pass_reco"] & (out["reco_ea"] > -9000.0)
        out["reco_ea"] = out["reco_ea"].copy()
        out["reco_ea"][m] *= r_mc
        log["signal_reco"] = dict(before=before, after=_stats(out["reco_ea"]), factor=r_mc)
        log["calls"]["signal"] += 1
        return out

    def data(*a, **k):
        pt, pz, ea = orig_data(*a, **k)
        before = _stats(ea)
        ea = np.asarray(ea, float) * r_data
        log["data"] = dict(before=before, after=_stats(ea), factor=r_data)
        log["calls"]["data"] += 1
        return pt, pz, ea

    def bkg(*a, **k):
        pt, pz, ea, w = orig_bkg(*a, **k)
        before = _stats(ea)
        ea = np.asarray(ea, float) * r_mc
        log["background_reco"] = dict(before=before, after=_stats(ea), factor=r_mc)
        log["calls"]["background"] += 1
        return pt, pz, ea, w

    mod.collect_signal_3d, mod.collect_data_3d, mod.collect_bkg_3d = sig, data, bkg


def patch_nd(mod, r_mc, r_data, log):
    orig_sig, orig_data, orig_bkg = mod.collect_signal_nd, mod.collect_data_nd, mod.collect_bkg_nd

    def ea_index(extras):
        idx = [i for i, ax in enumerate(extras) if ax.get("name") == "eavail"]
        if len(idx) != 1:
            raise RuntimeError(f"expected exactly one eavail axis, got {len(idx)}")
        return idx[0]

    def sig(t, extras, *a, **k):
        out = orig_sig(t, extras, *a, **k)
        i = ea_index(extras)
        col = np.asarray(out["reco_extras"][i], float).copy()
        before = _stats(col)
        m = out["pass_reco"] & (col > -9000.0)
        col[m] *= r_mc
        out["reco_extras"][i] = col
        log["signal_reco"] = dict(before=before, after=_stats(col), factor=r_mc)
        log["calls"]["signal"] += 1
        return out

    def data(t, extras, *a, **k):
        pt, pz, exs = orig_data(t, extras, *a, **k)
        i = ea_index(extras)
        before = _stats(exs[i])
        exs = list(exs)
        exs[i] = np.asarray(exs[i], float) * r_data
        log["data"] = dict(before=before, after=_stats(exs[i]), factor=r_data)
        log["calls"]["data"] += 1
        return pt, pz, exs

    def bkg(t, extras, *a, **k):
        out = list(orig_bkg(t, extras, *a, **k))
        i = ea_index(extras)
        before = _stats(out[2][i])
        exs = list(out[2])
        exs[i] = np.asarray(exs[i], float) * r_mc
        out[2] = exs
        log["background_reco"] = dict(before=before, after=_stats(exs[i]), factor=r_mc)
        log["calls"]["background"] += 1
        return tuple(out)

    mod.collect_signal_nd, mod.collect_data_nd, mod.collect_bkg_nd = sig, data, bkg


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--driver", choices=sorted(DRIVERS), required=True)
    ap.add_argument("--scale-mc", type=float, required=True,
                    help="r applied to signal-MC and background-MC reco E_avail (k/1.17)")
    ap.add_argument("--scale-data", type=float, required=True,
                    help="r applied to data reco E_avail (k/1.17)")
    ap.add_argument("--log", required=True, help="JSON log of the applied scaling")
    ap.add_argument("driver_args", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    dargs = a.driver_args[1:] if a.driver_args[:1] == ["--"] else a.driver_args
    for r in (a.scale_mc, a.scale_data):
        if not (np.isfinite(r) and r > 0):
            ap.error("scales must be finite and positive")

    mod = load_driver(DRIVERS[a.driver])
    log = dict(driver=str(DRIVERS[a.driver]), scale_mc=a.scale_mc, scale_data=a.scale_data,
               driver_args=dargs, calls=dict(signal=0, data=0, background=0))
    (patch_3d if a.driver == "3d" else patch_nd)(mod, a.scale_mc, a.scale_data, log)

    sys.argv = [str(DRIVERS[a.driver])] + dargs
    rc = mod.main()
    bad = {k: v for k, v in log["calls"].items() if v != 1}
    log["driver_return"] = rc
    log["all_readers_patched_once"] = not bad
    # Which files actually executed (OI-136: the tree that launched is not proof of the tree run).
    log["imported_files"] = {name: getattr(sys.modules.get(name), "__file__", None)
                             for name in ("omnifold", "unfold_2d_omnifold_unbinned",
                                          "xsec_3d", "xsec_nd", "flux_universe")}
    for key in ("signal_reco", "data", "background_reco"):
        e = log.get(key)
        if e:
            want = e["before"]["sum_valid"] * e["factor"]
            got = e["after"]["sum_valid"]
            e["sum_scaled_as_intended"] = bool(np.isclose(got, want, rtol=1e-9, atol=1e-9))
            e["valid_count_preserved"] = e["before"]["n_valid"] == e["after"]["n_valid"]
    with open(a.log, "w") as f:
        json.dump(log, f, indent=1)
    if bad:
        print(f"[FAIL] patched readers not called exactly once: {bad}", file=sys.stderr)
        return 5
    for key in ("signal_reco", "data", "background_reco"):
        if not (log[key]["sum_scaled_as_intended"] and log[key]["valid_count_preserved"]):
            print(f"[FAIL] scaling check failed for {key}: {log[key]}", file=sys.stderr)
            return 6
    print(f"[eavail-scale] OK: r_mc={a.scale_mc} r_data={a.scale_data} log={a.log}")
    return 0 if rc in (None, 0) else int(rc)


if __name__ == "__main__":
    sys.exit(main())
