#!/usr/bin/env python3
"""Clause (c) RERUN: build the PRODUCTION-DIMENSION base payload for the adopt segment's inputs.

WHY PRODUCTION DIMENSION IS NOT A CHOICE. `mii_root_payload_classes.EXPECTED_ELEMENTS` asserts
10694 and 10694**2, `mii_anchor_comparator.DECLARED_REDUCTIONS` is EMPTY, and
`assert_reduction_is_declared` refuses any PAYLOAD-class reduction outright -- so a fixture at any
other dimension sets `class_failed` on the coverage branch and NO product of that dimension can pass
the complete gate. The previous clause (c) run used N=4 and named the payload axis as unverified;
arm 1 of this rerun is required to PASS the COMPLETE gate, which forces N=10694.

WHAT IS SYNTHETIC, STATED SO NOBODY READS IT AS PHYSICS. The VALUES. Every matrix here is DIAGONAL
with a chosen spectrum. Nothing reproduces the real archive's correlations and no number derived from
these fixtures is a measurement of anything. What the dimension buys is the coverage assertion, the
row-loop reader, and the raw/clipped diagonal pair exercised at the size the real product has.

WHY THE MAGNITUDES ARE WHAT THEY ARE:
  * sum(c_comb) is tuned so `sqrt_tr_old` lands on the VL1 order 4.36e-38, i.e. the anchor's real
    magnitude -- the int-reader truncation defect (`_read_int_scalars`'s docstring) is only reachable
    at that magnitude, so a fixture at O(1) would test a different arithmetic regime.
  * vu = 4*vb makes g EXACTLY 2.0 everywhere (sqrt(4x) == 2*sqrt(x) in IEEE, both exactly rounded),
    so `adopt_unified_5d` takes its real inflation path rather than the g==1 no-op.
  * hJointMeanShift is 1e-50 per bin: nonzero, so `joint_mean_shift_norm` is a real norm of a real
    histogram rather than an invented scalar, and small enough that `vu + ms**2 == vu` BIT-EXACTLY,
    so the launcher's SECOND (cv-centered) invocation also gets g == 2 and is not a different test.

WRITES ONLY UNDER --out. Nothing here opens, reads, moves or regenerates the 41.44 GB combined
intermediate, and nothing here writes inside any git checkout.
"""
import argparse
import os
import numpy as np

N = 10694        # classes.REPORTED_NBINS -- the cv>0 support. THE DEFAULT IS THE ONLY VALID
                 # VALUE FOR A VERDICT: --n exists so the harness itself can be rehearsed end to
                 # end at a small size, and every run below production dimension is a HARNESS test,
                 # never an arm. The driver stamps which one it used into the log.
FLAT = 65856     # classes.FLAT_NBINS -- the grid; hXSecND_flat only
VERT_BANDS = ["2p2h", "CCQEPauliSupViaKF", "FrAbs_pi", "FrElas_N", "HighQ2", "LowQ2",
              "MaCCQE", "MaRES", "MFP_N", "MvRES", "Rvn2pi", "Rvp2pi", "Flux"]
SEED = 20260821


def spectra(N, FLAT):
    """The per-bin arrays. Deterministic: one seed, printed, so the fixture is reproducible."""
    rng = np.random.default_rng(SEED)
    support = np.sort(rng.choice(FLAT, size=N, replace=False))
    xsec = np.zeros(FLAT, dtype=np.float64)
    xsec[support] = 1.0e-38 * (0.5 + rng.random(N))
    c_abs = 1.776e-79 * (0.5 + rng.random(N))     # |diag(C_comb)|
    vb = 0.25 * c_abs                             # block-sum per-bin variance
    vu = 4.0 * vb                                 # -> g == 2.0 exactly
    v_vert = 0.5 * c_abs                          # the 13 vertical bands sum to this
    ms = np.full(N, 1e-50, dtype=np.float64)      # vu + ms**2 == vu bit-exactly
    return xsec, c_abs, vb, vu, v_vert, ms


# WHY `del` AND NEVER `.Delete()` ON A HISTOGRAM THIS FILE CREATED.
# Measured on ROOT 6.28/12 / python 3.11.14: Delete() frees the C++ object while the Python proxy
# still holds it, and cppyy frees it AGAIN at dealloc -- SIGSEGV inside op_dealloc_nofree.
# `read_keys_pyroot` calls Delete() safely because its objects come from `key.ReadObj()`, which is a
# DIFFERENT ownership. `ROOT.TH1.AddDirectory(False)` puts ownership in Python, so plain `del`
# releases the buffer immediately by refcount -- which is what keeps peak memory at ONE live
# 915 MB TH2D without the double free.


def _diag_th2(name, title, diag):
    """A square TH2D whose diagonal is `diag`, written straight into ROOT's own buffer.

    No 915 MB numpy temporary: `TH2D` already owns the array, so the fixture writes into it in
    place. Same buffer route `adopt_unified_5d._write_th2` uses, which is the route that has run in
    production -- a fixture builder that used a different one would be testing its own writer.
    """
    import ROOT
    n = diag.size
    h = ROOT.TH2D(name, title, n, 0, n, n, 0, n)
    arr = np.frombuffer(h.GetArray(), dtype=np.float64, count=(n + 2) * (n + 2)).reshape(n + 2, n + 2)
    arr.setflags(write=True)
    arr[:, :] = 0.0
    i = np.arange(n)
    arr[1:n + 1, 1:n + 1][i, i] = diag
    return h


def _th1(name, title, arr):
    import ROOT
    h = ROOT.TH1D(name, title, arr.size, 0, arr.size)
    for i, v in enumerate(arr):
        h.SetBinContent(i + 1, float(v))
    return h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="base directory (created)")
    ap.add_argument("--n", type=int, default=N,
                    help="support dimension. 10694 (default) is the ONLY value a verdict may quote; "
                         "anything else rehearses the harness and is labelled as such.")
    ap.add_argument("--neg-bin", type=int, default=4242, help="bin carrying the negative raw entry")
    a = ap.parse_args()
    n_sup = a.n
    flat = FLAT if a.n == N else max(FLAT, a.n * 2)
    import ROOT
    ROOT.gErrorIgnoreLevel = ROOT.kError
    ROOT.TH1.AddDirectory(False)
    os.makedirs(a.out, exist_ok=True)

    xsec, c_abs, vb, vu, v_vert, ms = spectra(n_sup, flat)
    print(f"[base] N={n_sup} FLAT={flat} seed={SEED}"
          + ("" if n_sup == N else "   *** NOT PRODUCTION DIMENSION: HARNESS REHEARSAL ONLY ***"))
    print(f"[base] sum(|c_comb|) = {float(np.sum(c_abs))!r}  -> sqrt = {float(np.sqrt(np.sum(c_abs)))!r}")
    print(f"[base] joint_mean_shift_norm = {float(np.linalg.norm(ms))!r}")

    # ---- the throw leg's payload (adopt reads only the DIAGONALS of these two) ----
    p = os.path.join(a.out, "uthrow_payload.root")
    f = ROOT.TFile.Open(p, "RECREATE")
    f.cd()
    for name, title, d in (("C_unified", "unified throw cov (fixture, diagonal)", vu),
                           ("C_blocksum", "bank block-sum cov (fixture, diagonal)", vb)):
        h = _diag_th2(name, title, d)
        h.Write(name)
        del h
        print(f"[base]   wrote {name}")
    h = _th1("hJointMeanShift", "joint mean shift (fixture)", ms)
    h.Write("hJointMeanShift")
    del h
    ROOT.TParameter("double")("fixed_seed_null_norm", 5.8223488501140625e-50).Write()
    ROOT.TParameter("double")("joint_mean_shift_norm", float(np.linalg.norm(ms))).Write()
    # 160 is receipt_candidate_stamps_5d.EXPECT_UPSTREAM["upstream_n_throws"], the PREDECLARED
    # ensemble size verify_configuration_identity checks against. Imported below rather than trusted.
    import sys
    sys.path.insert(0, os.environ["MNV_ND"])
    import receipt_candidate_stamps_5d as rc
    n_throws = int(rc.EXPECT_UPSTREAM["upstream_n_throws"])
    print(f"[base]   n_throws = {n_throws} (imported from receipt_candidate_stamps_5d.EXPECT_UPSTREAM)")
    ROOT.TParameter("int")("n_throws", n_throws).Write()
    f.Close()
    print(f"[base] wrote {p}")

    # ---- the combined intermediate's payload, in two variants ----
    for tag, c_comb, negbin in (("pos", c_abs.copy(), None),
                                ("neg", None, a.neg_bin)):
        if c_comb is None:
            c_comb = c_abs.copy()
            c_comb[negbin] = -c_abs[negbin]      # ONE legitimately negative raw diagonal entry
        p = os.path.join(a.out, f"combined_payload_{tag}.root")
        f = ROOT.TFile.Open(p, "RECREATE")
        f.cd()
        h = _diag_th2("hCov_combined5d_total", f"old combined cov (fixture, diagonal, {tag})", c_comb)
        h.Write("hCov_combined5d_total")
        del h
        band = v_vert / len(VERT_BANDS)
        for b in VERT_BANDS:
            h = _diag_th2(f"hCov_universe5d_{b}", f"vertical band {b} (fixture, diagonal)", band)
            h.Write(f"hCov_universe5d_{b}")
            del h
        f.Close()
        cnew = c_comb + 3.0 * (band * len(VERT_BANDS))
        print(f"[base] wrote {p}")
        print(f"[base]   trace(C_comb) = {float(np.sum(c_comb))!r}  sqrt = {float(np.sqrt(np.sum(c_comb)))!r}")
        print(f"[base]   negative raw diag entries = {int(np.count_nonzero(c_comb < 0))}"
              + (f" at bin {negbin} value {c_comb[negbin]!r}" if negbin is not None else ""))
        print(f"[base]   predicted min diag(C_new) = {float(cnew.min())!r}  (PSD needs >= 0)")

    # ---- the reported CV ----
    p = os.path.join(a.out, "prod_payload.root")
    f = ROOT.TFile.Open(p, "RECREATE")
    f.cd()
    h = _th1("hXSecND_flat", "reported 5D xsec, flat (fixture)", xsec)
    h.Write("hXSecND_flat")
    del h
    f.Close()
    print(f"[base] wrote {p}  ({int(np.count_nonzero(xsec > 0))} of {flat} bins > 0)")


if __name__ == "__main__":
    main()
