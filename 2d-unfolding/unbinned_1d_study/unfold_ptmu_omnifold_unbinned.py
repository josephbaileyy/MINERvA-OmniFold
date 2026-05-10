#!/usr/bin/env python3
import argparse
import math
from array import array

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)

def get_edges_from_hist(h):
    ax = h.GetXaxis()
    nb = ax.GetNbins()
    edges = [ax.GetBinLowEdge(1)]
    for i in range(1, nb + 1):
        edges.append(ax.GetBinUpEdge(i))
    return edges


def make_th1d(name, title, edges):
    h = ROOT.TH1D(name, title, len(edges) - 1, array("d", edges))
    h.Sumw2()
    h.SetDirectory(0)
    return h


def integral_inrange(h):
    return float(h.Integral(1, h.GetNbinsX()))


def integral_with_ufof(h):
    return float(h.Integral(0, h.GetNbinsX() + 1))


def get_pot_scales(f_in):
    data_par = f_in.Get("dataPOTUsed")
    mc_par = f_in.Get("mcPOTUsed")
    if not data_par or not mc_par:
        raise RuntimeError("Missing required POT metadata: dataPOTUsed and mcPOTUsed")
    data_pot = float(data_par.GetVal())
    mc_pot = float(mc_par.GetVal())
    if not (math.isfinite(data_pot) and math.isfinite(mc_pot) and mc_pot > 0.0):
        raise RuntimeError(f"Invalid POT values: dataPOT={data_pot}, mcPOT={mc_pot}")
    return data_pot, mc_pot, data_pot / mc_pot, "input file metadata"


def fill_data_reco(t_data, h_data, pt_lo, pt_hi, pt_guard_max=1e3, verbose=False):
    measured = array("d", [0.0])
    measured_pass = array("B", [0])
    t_data.SetBranchAddress("measured", measured)
    t_data.SetBranchAddress("measured_pass", measured_pass)

    vals = []
    n_pass_skip = 0
    n_guard_skip = 0
    n_range_skip = 0

    for i in range(t_data.GetEntries()):
        t_data.GetEntry(i)
        if measured_pass[0] == 0:
            n_pass_skip += 1
            continue
        x = float(measured[0])
        if not math.isfinite(x) or abs(x) > pt_guard_max:
            n_guard_skip += 1
            continue
        if not (pt_lo <= x <= pt_hi):
            n_range_skip += 1
            continue
        vals.append(x)
        h_data.Fill(x)

    if verbose:
        print(f"[INFO] data filled: pass-skipped={n_pass_skip}, "
              f"guard-skipped={n_guard_skip}, range-skipped={n_range_skip}")
    return np.asarray(vals, dtype=float)


def build_measured_training(meas_pt, h_data, h_bkg, verbose=False):
    """Per-event measured weights = max(0, data-bkg)/data in the reco bin.

    Mirrors the 2D contract: OmniFold's measured-side accepts per-event sample
    weights but not negative weights. Floor any negative reco-space bins to
    zero before passing to ohf.omnifold.
    """
    h_train = h_data.Clone("hMeasTrain")
    h_train.SetTitle("Measured (training, floored);p_{T}^{#mu,reco};Events")
    h_train.Reset("ICES")

    xaxis = h_data.GetXaxis()
    weights = np.zeros(meas_pt.shape[0], dtype=float)
    n_zero = 0

    for i, pt in enumerate(meas_pt):
        ix = xaxis.FindFixBin(float(pt))
        data_bin = h_data.GetBinContent(ix)
        if data_bin <= 0.0:
            n_zero += 1
            continue
        target_bin = max(0.0, data_bin - h_bkg.GetBinContent(ix))
        w = target_bin / data_bin
        weights[i] = w
        h_train.Fill(float(pt), w)
        if w <= 0.0:
            n_zero += 1

    if verbose:
        print(f"[INFO] measured training: effective sum={weights.sum():.6g}, "
              f"zero-weight events={n_zero}/{weights.size}")
    return weights, h_train


def fill_bkg_reco(t_bkg, h_bkg, pot_scale, pt_guard_max=1e3, verbose=False):
    if not t_bkg.GetListOfBranches().FindObject("w_bkg"):
        raise RuntimeError("mc_background missing required branch: w_bkg")

    sim_bkg = array("d", [0.0])
    sim_bkg_pass = array("B", [0])
    w_bkg = array("d", [1.0])
    t_bkg.SetBranchAddress("sim_background", sim_bkg)
    t_bkg.SetBranchAddress("sim_background_pass", sim_bkg_pass)
    t_bkg.SetBranchAddress("w_bkg", w_bkg)

    n_pass_skip = 0
    n_guard_skip = 0
    n_w_skip = 0
    for i in range(t_bkg.GetEntries()):
        t_bkg.GetEntry(i)
        if sim_bkg_pass[0] == 0:
            n_pass_skip += 1
            continue
        x = float(sim_bkg[0])
        if not math.isfinite(x) or abs(x) > pt_guard_max:
            n_guard_skip += 1
            continue
        w = float(w_bkg[0])
        if not (math.isfinite(w) and 0.0 <= w < 1e6):
            n_w_skip += 1
            continue
        h_bkg.Fill(x, w * pot_scale)

    if verbose:
        print(f"[INFO] bkg filled: pass-skipped={n_pass_skip}, guard-skipped={n_guard_skip}, weight-skipped={n_w_skip}")


def collect_signal_arrays(t_sig, pt_lo, pt_hi, response_pot_scale, use_weights=False, verbose=False):
    for b in ("MC", "sim", "sim_pass"):
        if not t_sig.GetListOfBranches().FindObject(b):
            raise RuntimeError(f"mc_signal_reco missing required branch: {b}")

    mc_true = array("d", [0.0])
    sim_reco = array("d", [0.0])
    sim_pass = array("B", [0])
    t_sig.SetBranchAddress("MC", mc_true)
    t_sig.SetBranchAddress("sim", sim_reco)
    t_sig.SetBranchAddress("sim_pass", sim_pass)

    wt_arr = array("d", [1.0])
    wr_arr = array("d", [1.0])
    has_wt = False
    has_wr = False
    if use_weights:
        if not t_sig.GetListOfBranches().FindObject("w_truth"):
            raise RuntimeError("mc_signal_reco missing required branch: w_truth")
        if not t_sig.GetListOfBranches().FindObject("w_reco"):
            raise RuntimeError("mc_signal_reco missing required branch: w_reco")
        has_wt = True
        has_wr = True
        t_sig.SetBranchAddress("w_truth", wt_arr)
        t_sig.SetBranchAddress("w_reco", wr_arr)

    truth_vals = []
    reco_vals = []
    pass_reco = []
    pass_truth = []
    w_truth = []
    w_reco = []

    bad_weight = 0
    dropped = 0
    for i in range(t_sig.GetEntries()):
        t_sig.GetEntry(i)
        tru = float(mc_true[0])
        rec = float(sim_reco[0])
        passed = sim_pass[0] != 0

        wt = float(wt_arr[0]) if has_wt else 1.0
        wr = float(wr_arr[0]) if has_wr else wt
        if not (math.isfinite(wt) and math.isfinite(wr) and 0.0 <= wt < 1e4 and 0.0 <= wr < 1e4):
            bad_weight += 1
            continue
        wt *= response_pot_scale
        wr *= response_pot_scale

        tru_ok = math.isfinite(tru) and (pt_lo <= tru <= pt_hi)
        rec_ok = math.isfinite(rec) and (pt_lo <= rec <= pt_hi)

        # Keep events relevant for unbinned training. True-mask is handled by MCPassTruth.
        if not (tru_ok or (passed and rec_ok)):
            dropped += 1
            continue

        truth_vals.append(tru if math.isfinite(tru) else -9999.0)
        reco_vals.append(rec if (passed and rec_ok) else -9999.0)
        pass_reco.append(passed and rec_ok)
        pass_truth.append(tru_ok)
        w_truth.append(wt)
        w_reco.append(wr)

    if verbose:
        print(f"[INFO] signal arrays: kept={len(truth_vals)}, dropped={dropped}, bad-weight={bad_weight}")

    return {
        "truth": np.asarray(truth_vals, dtype=float),
        "reco": np.asarray(reco_vals, dtype=float),
        "pass_reco": np.asarray(pass_reco, dtype=bool),
        "pass_truth": np.asarray(pass_truth, dtype=bool),
        "w_truth": np.asarray(w_truth, dtype=float),
        "w_reco": np.asarray(w_reco, dtype=float),
    }


def main():
    ap = argparse.ArgumentParser(description="Unbinned OmniFold unfolding for MINERvA pTmu via the omnifold.py helper, mirroring the 2D contract.")
    ap.add_argument("--omnifile", default="runEventLoopOmniFold.root")
    ap.add_argument("--datafile", default="runEventLoopData.root")
    ap.add_argument("--datahist", default="pTmu_data")
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--use-weights", action="store_true")
    ap.add_argument("--out", default="pTmu_crossSection_omnifold.root")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    args.rescale_unfold_to_meas = False

    f_ref = ROOT.TFile.Open(args.datafile, "READ")
    if not f_ref or f_ref.IsZombie():
        raise RuntimeError(f"Could not open {args.datafile}")
    h_ref = f_ref.Get(args.datahist)
    if not h_ref:
        raise RuntimeError(f"Could not find {args.datahist} in {args.datafile}")
    edges = get_edges_from_hist(h_ref)
    pt_lo, pt_hi = edges[0], edges[-1]
    print(f"[INFO] Using pTmu range from reference binning: [{pt_lo}, {pt_hi}]")

    f_in = ROOT.TFile.Open(args.omnifile, "READ")
    if not f_in or f_in.IsZombie():
        raise RuntimeError(f"Could not open {args.omnifile}")

    t_sig = f_in.Get("mc_signal_reco")
    t_bkg = f_in.Get("mc_background")
    t_data = f_in.Get("data")
    if not t_sig or not t_bkg or not t_data:
        raise RuntimeError("Missing required TTrees: mc_signal_reco, mc_background, data")

    data_pot, mc_pot, pot_scale, pot_src = get_pot_scales(f_in)
    response_pot_scale = pot_scale
    print(f"[INFO] POT source={pot_src}: dataPOT={data_pot:.6g}, mcPOT={mc_pot:.6g}, potScale={pot_scale:.6g}")
    print(f"[INFO] unbinned MC weight scale mode: data/MC (responsePotScale={response_pot_scale:.6g})")

    hDataReco = make_th1d("hDataReco", "Data reco;p_{T}^{#mu,reco};Events", edges)
    hBkgReco = make_th1d("hBkgReco", "Sim. (bkg reco, POT-scaled);p_{T}^{#mu,reco};Events", edges)
    hMeasSub = make_th1d("hMeasSub", "Measured (data-bkg);p_{T}^{#mu,reco};Events", edges)
    hSigReco = make_th1d("hSigReco", "Sim. (signal reco);p_{T}^{#mu,reco};Events", edges)
    hTruthSel = make_th1d("hTruthSel", "Truth prior (MC truth);p_{T}^{#mu,true};Events", edges)
    hUnfold = make_th1d("hUnfoldTruthSel", "Unfolded (unbinned OmniFold);p_{T}^{#mu,true};Events", edges)
    hUnfoldScaled = make_th1d("hUnfoldTruthSel_rescaled", "Unfolded rescaled;p_{T}^{#mu,true};Events", edges)
    hStep1Reco = make_th1d("hStep1RecoReweighted", "Reco MC with step1 weights;p_{T}^{#mu,reco};Events", edges)
    hWstep1 = ROOT.TH1D("hStep1WeightDist", "Step1 weights;w;Events", 120, 0.0, 6.0)
    hWstep2 = ROOT.TH1D("hStep2WeightDist", "Step2 weights;w;Events", 120, 0.0, 6.0)
    hWstep1.SetDirectory(0)
    hWstep2.SetDirectory(0)

    measured_entries = fill_data_reco(t_data, hDataReco, pt_lo, pt_hi, verbose=args.verbose)
    fill_bkg_reco(t_bkg, hBkgReco, pot_scale, verbose=args.verbose)

    sig = collect_signal_arrays(t_sig, pt_lo, pt_hi, response_pot_scale, use_weights=args.use_weights, verbose=args.verbose)
    if sig["truth"].size == 0:
        raise RuntimeError("No signal events survived for unbinned OmniFold input.")
    if measured_entries.size == 0:
        raise RuntimeError("No measured entries available for unbinned OmniFold.")

    # Signal fakes (reco in PS, truth out of PS): omnifold.py drops ~pass_truth
    # events from MCreco before step-1 training, but they remain in measured.
    # Treat them as background by adding their POT-scaled reco weights into
    # hBkgReco so both sides are fake-free. See 2D contract §3.
    is_fake = sig["pass_reco"] & (~sig["pass_truth"])
    n_fakes = int(is_fake.sum())
    if n_fakes:
        fake_reco = sig["reco"][is_fake]
        fake_wr = sig["w_reco"][is_fake]
        fake_sum = 0.0
        for x, w in zip(fake_reco, fake_wr):
            hBkgReco.Fill(float(x), float(w))
            fake_sum += float(w)
        if args.verbose:
            print(f"[INFO] signal fakes added to bkg: n={n_fakes}, sum(w_reco)={fake_sum:.6g}")

    hMeasSub.Add(hDataReco)
    hMeasSub.Add(hBkgReco, -1.0)

    measured_weights, hMeasTrain = build_measured_training(
        measured_entries, hDataReco, hBkgReco, verbose=args.verbose)

    # --- Run OmniFold via direct Python helper to pass measured_weights. ---
    import sys
    _OF_PY = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/python"
    if _OF_PY not in sys.path:
        sys.path.insert(0, _OF_PY)
    from omnifold import OmniFold_helper_functions as ohf

    MCgen = sig["truth"].reshape(-1, 1)
    MCreco = sig["reco"].reshape(-1, 1)
    measured = measured_entries.reshape(-1, 1)

    step1_weights, step2_weights = ohf.omnifold(
        MCgen, MCreco, measured,
        sig["pass_reco"], sig["pass_truth"],
        np.ones(measured_entries.shape[0], dtype=bool),
        int(args.iters),
        MCgen_weights=sig["w_truth"] if args.use_weights else None,
        MCreco_weights=sig["w_reco"] if args.use_weights else None,
        measured_weights=measured_weights,
    )

    truth_in = sig["truth"][sig["pass_truth"]]
    reco_in = sig["reco"][sig["pass_truth"]]
    pass_reco_in = sig["pass_reco"][sig["pass_truth"]]
    truth_w_in = sig["w_truth"][sig["pass_truth"]]

    if truth_in.shape[0] != step1_weights.shape[0] or truth_in.shape[0] != step2_weights.shape[0]:
        raise RuntimeError(
            f"Weight/vector size mismatch: truth_in={truth_in.shape[0]}, step1={step1_weights.shape[0]}, step2={step2_weights.shape[0]}"
        )

    for x, w in zip(truth_in, truth_w_in):
        hTruthSel.Fill(float(x), float(w))
    # hUnfold is a truth-space event yield: step2 returns a truth-side density
    # ratio, multiply by the original truth weights to get event counts. See
    # 2D contract §4.
    for x, ratio, wt in zip(truth_in, step2_weights, truth_w_in):
        hUnfold.Fill(float(x), float(ratio) * float(wt))
        hWstep2.Fill(float(ratio))
    for x, p, w in zip(reco_in, pass_reco_in, step1_weights):
        if p:
            hStep1Reco.Fill(float(x), float(w))
            hWstep1.Fill(float(w))
    for x, p, w in zip(sig["reco"], sig["pass_reco"], sig["w_reco"]):
        if p:
            hSigReco.Fill(float(x), float(w))

    target = integral_inrange(hMeasSub)
    curr = integral_inrange(hUnfold)
    hUnfoldScaled.Add(hUnfold)
    if curr > 0.0:
        hUnfoldScaled.Scale(target / curr)

    hWbin = hUnfold.Clone("hWbin_final")
    hWbin.Reset("ICES")
    for ib in range(1, hWbin.GetNbinsX() + 1):
        t = hTruthSel.GetBinContent(ib)
        u = hUnfold.GetBinContent(ib)
        hWbin.SetBinContent(ib, (u / t) if t > 0.0 else 0.0)

    hWlog = ROOT.TH1D("hWlog_final", "log10(weight);log10(w);# truth bins", 80, -6, 6)
    hWlog.SetDirectory(0)
    for ib in range(1, hWbin.GetNbinsX() + 1):
        w = hWbin.GetBinContent(ib)
        if w > 0.0:
            hWlog.Fill(math.log10(w))

    print(f"[CHECK] hMeasSub in-range={target:.6g}")
    print(f"[CHECK] hTruthSel in-range={integral_inrange(hTruthSel):.6g}")
    print(f"[CHECK] hUnfoldTruthSel in-range={curr:.6g}")
    print(f"[CHECK] hUnfoldTruthSel(UF/OF)={integral_with_ufof(hUnfold):.6g}")
    if curr > 0.0:
        print(f"[CHECK] ratio data-bkg / unfolded = {target / curr:.6g}")

    f_out = ROOT.TFile.Open(args.out, "RECREATE")
    if not f_out or f_out.IsZombie():
        raise RuntimeError(f"Could not create output file: {args.out}")
    f_out.cd()

    failures = []
    if ROOT.TParameter("double")("dataPOT", data_pot).Write() <= 0:
        failures.append("dataPOT")
    if ROOT.TParameter("double")("mcPOT", mc_pot).Write() <= 0:
        failures.append("mcPOT")
    if ROOT.TParameter("double")("potScale", pot_scale).Write() <= 0:
        failures.append("potScale")
    if ROOT.TParameter("int")("iters", int(args.iters)).Write() <= 0:
        failures.append("iters")
    if ROOT.TParameter("int")("isUnbinnedOmniFold", 1).Write() <= 0:
        failures.append("isUnbinnedOmniFold")

    out_objs = [hDataReco, hBkgReco, hMeasSub, hMeasTrain, hSigReco, hTruthSel, hUnfold, hWbin, hWlog, hStep1Reco, hWstep1, hWstep2]
    if args.rescale_unfold_to_meas:
        out_objs.append(hUnfoldScaled)
    for obj in out_objs:
        if obj.Write() <= 0:
            failures.append(obj.GetName())

    if failures:
        raise RuntimeError("Failed to write ROOT objects: " + ", ".join(failures))

    f_out.Close()
    print(f"[OK] wrote {args.out}")


if __name__ == "__main__":
    main()
