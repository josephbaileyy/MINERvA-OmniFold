#!/usr/bin/env python3
"""
Signal-only split-sample closure and iteration-scan study for MINERvA pTmu.

This script is intentionally separate from the production unfolding script. It
uses the existing OmniFold input ROOT file, splits the signal MC into a train
(response) half and a pseudo-data half, optionally applies a truth-level stress
reweight to the pseudo-data half, and then compares:

- reconstructed pseudo-data (before unfolding)
- IBU on the train-half response
- unbinned OmniFold on the train-half response

to the known pseudo-data truth target.

Outputs:
- ROOT file with closure histograms
- CSV table of iteration metrics
- Markdown summary with recommended iterations
- PDF/PNG comparison and iteration-scan plots
"""

import argparse
import csv
import math
from array import array
from pathlib import Path

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.TH1.AddDirectory(False)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(0)

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OMNI = SCRIPT_DIR / "runEventLoopOmniFold.root"
DEFAULT_DATA = SCRIPT_DIR / "runEventLoopData.root"
DEFAULT_OUTDIR = SCRIPT_DIR / "ptmu_closure_study_outputs"


# -----------------------------------------------------------------------------
# Helpers: I/O, histograms, vectors
# -----------------------------------------------------------------------------
def parse_iterations(spec):
    vals = []
    for tok in spec.split(","):
        tok = tok.strip()
        if not tok:
            continue
        it = int(tok)
        if it < 1:
            raise ValueError(f"Iteration counts must be >= 1, got {it}")
        vals.append(it)
    if not vals:
        raise ValueError("No iterations were parsed from --iterations")
    return sorted(set(vals))


def tagged_name(name, tag):
    p = Path(name)
    if not tag:
        return p.name
    return f"{p.stem}_{tag}{p.suffix}"


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


def clone_detached(h, name):
    c = h.Clone(name)
    c.SetDirectory(0)
    return c


def integral_inrange(h):
    return float(h.Integral(1, h.GetNbinsX()))


def np_to_tvector(mask):
    v = ROOT.TVector(len(mask))
    for i, x in enumerate(mask):
        v[i] = 1.0 if bool(x) else 0.0
    return v


def np_to_tvectord(vals):
    v = ROOT.TVectorD(len(vals))
    for i, x in enumerate(vals):
        v[i] = float(x)
    return v


def tvectord_to_np(v):
    return np.asarray([float(v[i]) for i in range(v.GetNoElements())], dtype=float)


def make_rdataframe(column_name, values):
    arr = np.asarray(values, dtype=np.float64)
    return ROOT.RDF.MakeNumpyDataFrame({column_name: arr})


# -----------------------------------------------------------------------------
# Helpers: reading current OmniFold inputs
# -----------------------------------------------------------------------------
def require_tree(f_in, name):
    obj = f_in.Get(name)
    if not obj:
        raise RuntimeError(f"Missing required TTree: {name}")
    return obj


def require_branch(tree, name):
    if not tree.GetListOfBranches().FindObject(name):
        raise RuntimeError(f"{tree.GetName()} missing required branch: {name}")


def get_pot_scale(f_in, use_weights):
    data_par = f_in.Get("dataPOTUsed")
    mc_par = f_in.Get("mcPOTUsed")
    if not data_par or not mc_par:
        raise RuntimeError("Missing required POT metadata: dataPOTUsed and mcPOTUsed")
    data_pot = float(data_par.GetVal())
    mc_pot = float(mc_par.GetVal())
    if not (math.isfinite(data_pot) and math.isfinite(mc_pot) and mc_pot > 0.0):
        raise RuntimeError(f"Invalid POT values: dataPOT={data_pot}, mcPOT={mc_pot}")
    pot_scale = data_pot / mc_pot if use_weights else 1.0
    return data_pot, mc_pot, pot_scale


def collect_signal_records(t_sig, pt_lo, pt_hi, pot_scale, use_weights=True, pt_guard_max=1e3, verbose=False):
    for name in ("MC", "sim", "sim_pass", "w_truth", "w_reco"):
        require_branch(t_sig, name)

    mc_true = array("d", [0.0])
    sim_reco = array("d", [0.0])
    sim_pass = array("B", [0])
    wt_arr = array("d", [1.0])
    wr_arr = array("d", [1.0])

    t_sig.SetBranchAddress("MC", mc_true)
    t_sig.SetBranchAddress("sim", sim_reco)
    t_sig.SetBranchAddress("sim_pass", sim_pass)
    t_sig.SetBranchAddress("w_truth", wt_arr)
    t_sig.SetBranchAddress("w_reco", wr_arr)

    truth_vals = []
    reco_vals = []
    pass_truth = []
    pass_reco = []
    w_truth = []
    w_reco = []
    entries = []

    dropped = 0
    bad_weight = 0
    bad_reco = 0

    for i in range(t_sig.GetEntries()):
        t_sig.GetEntry(i)

        tru = float(mc_true[0])
        rec = float(sim_reco[0])
        passed = sim_pass[0] != 0

        wt = float(wt_arr[0]) * pot_scale if use_weights else 1.0
        wr = float(wr_arr[0]) * pot_scale if use_weights else 1.0
        if not (math.isfinite(wt) and math.isfinite(wr) and 0.0 <= wt < 1e6 and 0.0 <= wr < 1e6):
            bad_weight += 1
            continue

        tru_ok = math.isfinite(tru) and (pt_lo <= tru <= pt_hi)
        rec_ok = passed and math.isfinite(rec) and abs(rec) <= pt_guard_max and (pt_lo <= rec <= pt_hi)
        if passed and not rec_ok:
            bad_reco += 1

        if not (tru_ok or rec_ok):
            dropped += 1
            continue

        truth_vals.append(tru if math.isfinite(tru) else -9999.0)
        reco_vals.append(rec if rec_ok else -9999.0)
        pass_truth.append(tru_ok)
        pass_reco.append(rec_ok)
        w_truth.append(wt)
        w_reco.append(wr)
        entries.append(i)

    if verbose:
        print(
            f"[INFO] signal records: kept={len(entries)}, dropped={dropped}, "
            f"bad-weight={bad_weight}, bad-reco={bad_reco}"
        )

    return {
        "entry": np.asarray(entries, dtype=np.int64),
        "truth": np.asarray(truth_vals, dtype=float),
        "reco": np.asarray(reco_vals, dtype=float),
        "pass_truth": np.asarray(pass_truth, dtype=bool),
        "pass_reco": np.asarray(pass_reco, dtype=bool),
        "w_truth": np.asarray(w_truth, dtype=float),
        "w_reco": np.asarray(w_reco, dtype=float),
    }


# -----------------------------------------------------------------------------
# Study construction
# -----------------------------------------------------------------------------
def split_masks(entries, train_split):
    even = (entries % 2) == 0
    train = even if train_split == "even" else ~even
    pseudo = ~train
    return train, pseudo


def morph_weight(x, args, pt_lo, pt_hi):
    if not math.isfinite(x):
        return 1.0

    if args.stress_mode == "nominal":
        w = 1.0
    elif args.stress_mode == "tilt":
        center = args.tilt_center if args.tilt_center is not None else 0.5 * (pt_lo + pt_hi)
        span = max(pt_hi - pt_lo, 1e-12)
        w = 1.0 + args.tilt_strength * ((x - center) / span)
    elif args.stress_mode == "bump":
        center = args.bump_center if args.bump_center is not None else 0.55 * pt_hi + 0.45 * pt_lo
        width = args.bump_width if args.bump_width is not None else max(0.12 * (pt_hi - pt_lo), 1e-12)
        w = 1.0 + args.bump_amplitude * math.exp(-0.5 * ((x - center) / width) ** 2)
    elif args.stress_mode == "tail":
        threshold = args.tail_threshold if args.tail_threshold is not None else pt_lo + 0.7 * (pt_hi - pt_lo)
        frac = 0.0 if x <= threshold else (x - threshold) / max(pt_hi - threshold, 1e-12)
        w = 1.0 + args.tail_amplitude * frac
    else:
        raise RuntimeError(f"Unknown stress mode: {args.stress_mode}")

    return max(args.min_morph_weight, w)


def fill_hist_from_arrays(h, values, weights):
    for x, w in zip(values, weights):
        h.Fill(float(x), float(w))


def build_closure_inputs(sig, train_mask, pseudo_mask, edges, args):
    pt_lo, pt_hi = edges[0], edges[-1]

    morph = np.asarray([morph_weight(x, args, pt_lo, pt_hi) for x in sig["truth"]], dtype=float)

    pseudo_truth_mask = pseudo_mask & sig["pass_truth"]
    pseudo_reco_mask = pseudo_mask & sig["pass_reco"]
    train_truth_mask = train_mask & sig["pass_truth"]
    train_reco_mask = train_mask & sig["pass_reco"]

    hPseudoTruth = make_th1d("hPseudoTruth", "Pseudo-data truth target;p_{T}^{#mu,true};Events", edges)
    hPseudoReco = make_th1d("hPseudoReco", "Pseudo-data reco signal;p_{T}^{#mu,reco};Events", edges)
    hTrainTruth = make_th1d("hTrainTruth", "Train-sample truth;p_{T}^{#mu,true};Events", edges)
    hTrainReco = make_th1d("hTrainReco", "Train-sample reco;p_{T}^{#mu,reco};Events", edges)
    hMorph = ROOT.TH1D("hTruthMorphWeights", "Truth morph weights;w_{morph};Events", 120, 0.0, 3.0)
    hMorph.SetDirectory(0)

    fill_hist_from_arrays(
        hPseudoTruth,
        sig["truth"][pseudo_truth_mask],
        sig["w_truth"][pseudo_truth_mask] * morph[pseudo_truth_mask],
    )
    fill_hist_from_arrays(
        hPseudoReco,
        sig["reco"][pseudo_reco_mask],
        sig["w_reco"][pseudo_reco_mask] * morph[pseudo_reco_mask],
    )
    fill_hist_from_arrays(
        hTrainTruth,
        sig["truth"][train_truth_mask],
        sig["w_truth"][train_truth_mask],
    )
    fill_hist_from_arrays(
        hTrainReco,
        sig["reco"][train_reco_mask],
        sig["w_reco"][train_reco_mask],
    )

    for w in morph[pseudo_truth_mask]:
        hMorph.Fill(float(w))

    measured_vals = sig["reco"][pseudo_reco_mask]
    measured_weights = sig["w_reco"][pseudo_reco_mask] * morph[pseudo_reco_mask]

    train_sig = {
        "truth": sig["truth"][train_mask],
        "reco": sig["reco"][train_mask],
        "pass_truth": sig["pass_truth"][train_mask],
        "pass_reco": sig["pass_reco"][train_mask],
        "w_truth": sig["w_truth"][train_mask],
        "w_reco": sig["w_reco"][train_mask],
    }

    return {
        "morph": morph,
        "measured_vals": np.asarray(measured_vals, dtype=float),
        "measured_weights": np.asarray(measured_weights, dtype=float),
        "train_sig": train_sig,
        "hPseudoTruth": hPseudoTruth,
        "hPseudoReco": hPseudoReco,
        "hTrainTruth": hTrainTruth,
        "hTrainReco": hTrainReco,
        "hMorph": hMorph,
    }


def build_response(train_sig, edges):
    hRecoTemplate = make_th1d("hResponseRecoTemplate", "Reco template", edges)
    hTruthTemplate = make_th1d("hResponseTruthTemplate", "Truth template", edges)
    response = ROOT.RooUnfoldResponse(hRecoTemplate, hTruthTemplate)

    for tru, rec, pass_truth, pass_reco, w_truth in zip(
        train_sig["truth"],
        train_sig["reco"],
        train_sig["pass_truth"],
        train_sig["pass_reco"],
        train_sig["w_truth"],
    ):
        w_evt = float(w_truth)
        if pass_truth and pass_reco:
            response.Fill(float(rec), float(tru), w_evt)
        elif pass_truth:
            response.Miss(float(tru), w_evt)
        elif pass_reco:
            response.Fake(float(rec), w_evt)

    return response, hRecoTemplate, hTruthTemplate


# -----------------------------------------------------------------------------
# Unfolding backends
# -----------------------------------------------------------------------------
def run_unbinned_omnifold(train_sig, measured_vals, measured_weights, iterations, edges):
    results = {}

    if measured_vals.shape[0] == 0:
        raise RuntimeError("Pseudo-data reco sample is empty after the split")

    if not hasattr(ROOT, "RooUnfoldOmnifold"):
        raise RuntimeError("ROOT.RooUnfoldOmnifold is not available in this environment")

    for niter in iterations:
        df_MCgen = make_rdataframe("ptmu", train_sig["truth"])
        df_MCreco = make_rdataframe("ptmu", train_sig["reco"])
        df_measured = make_rdataframe("ptmu", measured_vals)

        unb = ROOT.RooUnfoldOmnifold()
        unb.SetModelSaving(False)
        unb.SetMCgenDataFrame(df_MCgen)
        unb.SetMCrecoDataFrame(df_MCreco)
        unb.SetMeasuredDataFrame(df_measured)
        unb.SetMCPassReco(np_to_tvector(train_sig["pass_reco"]))
        unb.SetMCPassTruth(np_to_tvector(train_sig["pass_truth"]))
        unb.SetMeasuredPassReco(np_to_tvector(np.ones(measured_vals.shape[0], dtype=bool)))
        unb.SetMCgenWeights(np_to_tvectord(train_sig["w_truth"]))
        unb.SetMCrecoWeights(np_to_tvectord(train_sig["w_reco"]))
        unb.SetMeasuredWeights(np_to_tvectord(measured_weights))
        unb.SetNumIterations(int(niter))

        result = unb.UnbinnedOmnifold()
        step1_weights = tvectord_to_np(ROOT.std.get[0](result))
        step2_weights = tvectord_to_np(ROOT.std.get[1](result))

        if step1_weights.shape[0] != train_sig["truth"].shape[0] or step2_weights.shape[0] != train_sig["truth"].shape[0]:
            raise RuntimeError(
                f"Unexpected OmniFold weight sizes at iteration {niter}: "
                f"step1={step1_weights.shape[0]}, step2={step2_weights.shape[0]}, train={train_sig['truth'].shape[0]}"
            )

        hStep1Reco = make_th1d(
            f"hOmniStep1Reco_iter{niter}",
            f"OmniFold step1 reco iter {niter};p_{{T}}^{{#mu,reco}};Events",
            edges,
        )
        hUnfold = make_th1d(
            f"hOmniTruth_iter{niter}",
            f"OmniFold truth iter {niter};p_{{T}}^{{#mu,true}};Events",
            edges,
        )
        hWstep1 = ROOT.TH1D(f"hOmniStep1Weights_iter{niter}", f"OmniFold step1 weights iter {niter};w;Events", 120, 0.0, 6.0)
        hWstep2 = ROOT.TH1D(f"hOmniStep2Weights_iter{niter}", f"OmniFold step2 weights iter {niter};w;Events", 120, 0.0, 6.0)
        hWstep1.SetDirectory(0)
        hWstep2.SetDirectory(0)

        for x, passed, w in zip(train_sig["reco"], train_sig["pass_reco"], step1_weights):
            if passed:
                hStep1Reco.Fill(float(x), float(w))
                hWstep1.Fill(float(w))
        for x, passed, w in zip(train_sig["truth"], train_sig["pass_truth"], step2_weights):
            if passed:
                hUnfold.Fill(float(x), float(w))
                hWstep2.Fill(float(w))

        results[int(niter)] = {
            "h_truth": hUnfold,
            "h_step1_reco": hStep1Reco,
            "h_wstep1": hWstep1,
            "h_wstep2": hWstep2,
        }

    return results


def run_ibu(response, measured_hist, iterations):
    if not hasattr(ROOT, "RooUnfoldBayes"):
        raise RuntimeError("ROOT.RooUnfoldBayes is not available in this environment")

    results = {}
    for niter in iterations:
        ibu = ROOT.RooUnfoldBayes(response, measured_hist, int(niter))
        h = ibu.Hunfold()
        results[int(niter)] = clone_detached(h, f"hIBUTruth_iter{niter}")
    return results


# -----------------------------------------------------------------------------
# Metrics and summary tables
# -----------------------------------------------------------------------------
def compute_metrics(h_result, h_truth, iteration, method, previous=None):
    chi2 = 0.0
    ndf = 0
    frac_bias = []
    pulls = []
    prev_changes = []

    for ib in range(1, h_truth.GetNbinsX() + 1):
        t = float(h_truth.GetBinContent(ib))
        u = float(h_result.GetBinContent(ib))
        et = float(h_truth.GetBinError(ib))
        eu = float(h_result.GetBinError(ib))

        if t > 0.0:
            frac_bias.append(abs(u - t) / t)

        sigma = math.hypot(eu, et)
        if sigma > 0.0:
            pulls.append((u - t) / sigma)
            chi2 += ((u - t) / sigma) ** 2
            ndf += 1

        if previous is not None:
            prev = float(previous.GetBinContent(ib))
            if prev != 0.0:
                prev_changes.append(abs(u / prev - 1.0))

    chi2_ndf = chi2 / ndf if ndf > 0 else float("nan")
    integral_truth = integral_inrange(h_truth)
    integral_result = integral_inrange(h_result)

    return {
        "method": method,
        "iteration": int(iteration),
        "integral_truth": integral_truth,
        "integral_result": integral_result,
        "integral_ratio": integral_result / integral_truth if integral_truth else float("nan"),
        "mean_abs_frac_bias": float(np.mean(frac_bias)) if frac_bias else float("nan"),
        "max_abs_frac_bias": float(np.max(frac_bias)) if frac_bias else float("nan"),
        "pull_mean": float(np.mean(pulls)) if pulls else float("nan"),
        "pull_rms": float(np.std(pulls)) if pulls else float("nan"),
        "chi2": chi2,
        "ndf": ndf,
        "chi2_ndf": chi2_ndf,
        "prev_frac_change_rms": float(np.sqrt(np.mean(np.square(prev_changes)))) if prev_changes else float("nan"),
        "prev_frac_change_max": float(np.max(prev_changes)) if prev_changes else float("nan"),
    }


def choose_best_iteration(rows, method):
    candidates = [r for r in rows if r["method"] == method and r["iteration"] > 0 and math.isfinite(r["chi2_ndf"])]
    if not candidates:
        return None
    return min(candidates, key=lambda r: (r["chi2_ndf"], r["iteration"]))["iteration"]


def format_float(val, digits=4):
    if val is None or not math.isfinite(val):
        return "nan"
    return f"{val:.{digits}g}"


def write_metrics_csv(path, rows):
    fields = [
        "method",
        "iteration",
        "integral_truth",
        "integral_result",
        "integral_ratio",
        "mean_abs_frac_bias",
        "max_abs_frac_bias",
        "pull_mean",
        "pull_rms",
        "chi2",
        "ndf",
        "chi2_ndf",
        "prev_frac_change_rms",
        "prev_frac_change_max",
    ]
    with path.open("w", newline="") as f_csv:
        writer = csv.DictWriter(f_csv, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_summary_markdown(path, args, rows, best_omni, best_ibu):
    reco_row = next((r for r in rows if r["method"] == "reco"), None)
    omni_rows = [r for r in rows if r["method"] == "omnifold"]
    ibu_rows = [r for r in rows if r["method"] == "ibu"]

    def table(rows_in):
        lines = [
            "| Iteration | Integral ratio | Mean abs frac bias | Max abs frac bias | Pull mean | Pull RMS | chi2/ndf | Prev change RMS |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        for row in rows_in:
            lines.append(
                "| {iteration} | {integral_ratio} | {mean_abs_frac_bias} | {max_abs_frac_bias} | {pull_mean} | {pull_rms} | {chi2_ndf} | {prev_frac_change_rms} |".format(
                    iteration=row["iteration"],
                    integral_ratio=format_float(row["integral_ratio"]),
                    mean_abs_frac_bias=format_float(row["mean_abs_frac_bias"]),
                    max_abs_frac_bias=format_float(row["max_abs_frac_bias"]),
                    pull_mean=format_float(row["pull_mean"]),
                    pull_rms=format_float(row["pull_rms"]),
                    chi2_ndf=format_float(row["chi2_ndf"]),
                    prev_frac_change_rms=format_float(row["prev_frac_change_rms"]),
                )
            )
        return "\n".join(lines)

    text = f"""# pTmu closure and iteration scan summary

## Configuration
- OmniFold input: `{args.omnifile}`
- Reference binning file: `{args.datafile}`
- Reference histogram: `{args.datahist}`
- Iterations scanned: `{args.iterations}`
- Train split: `{args.train_split}`
- Pseudo-data split: `{'odd' if args.train_split == 'even' else 'even'}`
- Stress mode: `{args.stress_mode}`
- Use MC weights: `{args.use_weights}`
- Study scope: `signal-only closure in event-count units`

## Recommended iterations
- OmniFold: `{best_omni}`
- IBU: `{best_ibu}`

## Reco-only baseline
- Integral ratio (`reco / truth`): `{format_float(reco_row['integral_ratio']) if reco_row else 'nan'}`
- Mean absolute fractional bias: `{format_float(reco_row['mean_abs_frac_bias']) if reco_row else 'nan'}`
- Pull RMS: `{format_float(reco_row['pull_rms']) if reco_row else 'nan'}`
- `chi2/ndf`: `{format_float(reco_row['chi2_ndf']) if reco_row else 'nan'}`

## OmniFold iteration table
{table(omni_rows)}

## IBU iteration table
{table(ibu_rows)}

## Interpretation template
- This is a **split-sample signal-only closure test**. The OmniFold response is trained on the `{args.train_split}` MC half, while the pseudo-data truth target is taken from the complementary half.
- The purpose of the nominal study is to test **implementation correctness** and quantify the residual detector bias before and after unfolding.
- The purpose of a stressed study is to test **usefulness**: whether unfolding recovers a deliberately distorted pseudo-data truth distribution better than reco-only.
- The recommended OmniFold iteration is chosen here by the smallest `chi2/ndf`, with ties broken toward lower iteration counts.
- This summary is in **event-count units**. Flux normalization and cross-section conversion are intentionally left out so the metric reflects the unfolding itself.
"""
    path.write_text(text)


# -----------------------------------------------------------------------------
# Plotting
# -----------------------------------------------------------------------------
def style_truth(h):
    h.SetLineColor(ROOT.kGreen + 2)
    h.SetFillColorAlpha(ROOT.kGreen + 2, 0.25)
    h.SetFillStyle(1001)
    h.SetLineWidth(2)


def style_reco(h):
    h.SetLineColor(ROOT.kOrange + 7)
    h.SetLineWidth(2)
    h.SetFillStyle(0)


def style_ibu(h):
    h.SetLineColor(ROOT.kGray + 2)
    h.SetLineWidth(2)
    h.SetMarkerStyle(0)


def style_omni(h):
    h.SetLineColor(ROOT.kAzure + 1)
    h.SetLineWidth(3)
    h.SetMarkerStyle(0)


def make_ratio(num, den, name):
    r = clone_detached(num, name)
    r.Divide(den)
    return r


def max_bin_content(*hists):
    m = 0.0
    for h in hists:
        for ib in range(1, h.GetNbinsX() + 1):
            m = max(m, h.GetBinContent(ib) + h.GetBinError(ib))
    return m


def draw_best_comparison(h_truth, h_reco, h_ibu, h_omni, best_ibu, best_omni, outbase):
    truth = clone_detached(h_truth, "truth_plot")
    reco = clone_detached(h_reco, "reco_plot")
    ibu = clone_detached(h_ibu, "ibu_plot")
    omni = clone_detached(h_omni, "omni_plot")

    truth.SetTitle(";p_{T}^{#mu};Events")
    style_truth(truth)
    style_reco(reco)
    style_ibu(ibu)
    style_omni(omni)

    c = ROOT.TCanvas("c_closure", "c_closure", 900, 900)
    p1 = ROOT.TPad("p1_closure", "p1_closure", 0.0, 0.30, 1.0, 1.0)
    p2 = ROOT.TPad("p2_closure", "p2_closure", 0.0, 0.00, 1.0, 0.30)
    p1.SetBottomMargin(0.02)
    p2.SetTopMargin(0.04)
    p2.SetBottomMargin(0.30)
    for pad in (p1, p2):
        pad.SetLeftMargin(0.12)
        pad.SetRightMargin(0.05)
    p1.Draw()
    p2.Draw()

    p1.cd()
    ymax = 1.35 * max_bin_content(truth, reco, ibu, omni)
    truth.SetMaximum(ymax)
    truth.SetMinimum(0.0)
    truth.GetXaxis().SetLabelSize(0)
    truth.GetXaxis().SetTitleSize(0)
    truth.Draw("E2")
    truth.Draw("HIST SAME")
    reco.Draw("HIST SAME")
    ibu.Draw("HIST SAME")
    omni.Draw("HIST SAME")
    leg = ROOT.TLegend(0.54, 0.58, 0.88, 0.88)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.AddEntry(truth, "Pseudo-data truth target", "f")
    leg.AddEntry(reco, "Reco-only", "l")
    leg.AddEntry(ibu, f"IBU (iter={best_ibu})", "l")
    leg.AddEntry(omni, f"OmniFold (iter={best_omni})", "l")
    leg.Draw()

    p2.cd()
    frame = p2.DrawFrame(truth.GetXaxis().GetXmin(), 0.7, truth.GetXaxis().GetXmax(), 1.3)
    frame.SetTitle(";p_{T}^{#mu};Ratio to truth")
    frame.GetYaxis().SetNdivisions(505)
    frame.GetYaxis().SetTitleSize(0.09)
    frame.GetYaxis().SetLabelSize(0.08)
    frame.GetYaxis().SetTitleOffset(0.55)
    frame.GetXaxis().SetTitleSize(0.11)
    frame.GetXaxis().SetLabelSize(0.09)

    line = ROOT.TLine(truth.GetXaxis().GetXmin(), 1.0, truth.GetXaxis().GetXmax(), 1.0)
    line.SetLineStyle(2)
    line.Draw()
    make_ratio(reco, truth, "r_reco").Draw("HIST SAME")
    make_ratio(ibu, truth, "r_ibu").Draw("HIST SAME")
    make_ratio(omni, truth, "r_omni").Draw("HIST SAME")

    c.SaveAs(str(outbase.with_suffix(".png")))
    c.SaveAs(str(outbase.with_suffix(".pdf")))


def make_graph(rows, method, metric):
    xs = []
    ys = []
    for row in rows:
        if row["method"] != method or row["iteration"] <= 0:
            continue
        val = row[metric]
        if not math.isfinite(val):
            continue
        xs.append(float(row["iteration"]))
        ys.append(float(val))
    if not xs:
        return None
    return ROOT.TGraph(len(xs), array("d", xs), array("d", ys))


def style_graph(g, color):
    g.SetLineColor(color)
    g.SetMarkerColor(color)
    g.SetLineWidth(2)
    g.SetMarkerStyle(20)
    g.SetMarkerSize(1.0)


def draw_metric_scan(rows, outbase):
    metrics = [
        ("chi2_ndf", "chi2/ndf"),
        ("mean_abs_frac_bias", "Mean |U-T|/T"),
        ("pull_rms", "Pull RMS"),
        ("prev_frac_change_rms", "RMS(|U_{n}/U_{n-1}-1|)"),
    ]
    c = ROOT.TCanvas("c_metrics", "c_metrics", 1100, 900)
    c.Divide(2, 2)

    for ipad, (metric, title) in enumerate(metrics, start=1):
        c.cd(ipad)
        pad = ROOT.gPad
        pad.SetLeftMargin(0.14)
        pad.SetRightMargin(0.05)
        g_omni = make_graph(rows, "omnifold", metric)
        g_ibu = make_graph(rows, "ibu", metric)
        mg = ROOT.TMultiGraph()
        leg = ROOT.TLegend(0.55, 0.72, 0.88, 0.88)
        leg.SetBorderSize(0)
        leg.SetFillStyle(0)
        if g_omni is not None:
            style_graph(g_omni, ROOT.kAzure + 1)
            mg.Add(g_omni, "LP")
            leg.AddEntry(g_omni, "OmniFold", "lp")
        if g_ibu is not None:
            style_graph(g_ibu, ROOT.kGray + 2)
            mg.Add(g_ibu, "LP")
            leg.AddEntry(g_ibu, "IBU", "lp")
        mg.Draw("A")
        mg.SetTitle(f";Iteration;{title}")
        leg.Draw()

    c.SaveAs(str(outbase.with_suffix(".png")))
    c.SaveAs(str(outbase.with_suffix(".pdf")))


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def parse_args():
    ap = argparse.ArgumentParser(
        description="Signal-only split-sample closure and iteration scan for MINERvA pTmu unbinned OmniFold."
    )
    ap.add_argument("--omnifile", default=str(DEFAULT_OMNI))
    ap.add_argument("--datafile", default=str(DEFAULT_DATA))
    ap.add_argument("--datahist", default="pTmu_data")
    ap.add_argument("--iterations", default="1,2,3,4,5,6,7,8")
    ap.add_argument("--train-split", choices=("even", "odd"), default="even")
    ap.add_argument("--stress-mode", choices=("nominal", "tilt", "bump", "tail"), default="nominal")
    ap.add_argument("--tilt-strength", type=float, default=1.0)
    ap.add_argument("--tilt-center", type=float, default=None)
    ap.add_argument("--bump-amplitude", type=float, default=0.35)
    ap.add_argument("--bump-center", type=float, default=None)
    ap.add_argument("--bump-width", type=float, default=None)
    ap.add_argument("--tail-amplitude", type=float, default=0.6)
    ap.add_argument("--tail-threshold", type=float, default=None)
    ap.add_argument("--min-morph-weight", type=float, default=1e-3)
    ap.add_argument("--use-weights", dest="use_weights", action="store_true")
    ap.add_argument("--no-use-weights", dest="use_weights", action="store_false")
    ap.set_defaults(use_weights=True)
    ap.add_argument("--outdir", default=str(DEFAULT_OUTDIR))
    ap.add_argument("--outroot", default="ptmu_closure_iteration_study.root")
    ap.add_argument("--outcsv", default="ptmu_closure_iteration_metrics.csv")
    ap.add_argument("--outmd", default="ptmu_closure_iteration_summary.md")
    ap.add_argument("--tag", default="")
    ap.add_argument("--verbose", action="store_true")
    return ap.parse_args()


def main():
    args = parse_args()
    iterations = parse_iterations(args.iterations)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    outroot = outdir / tagged_name(args.outroot, args.tag)
    outcsv = outdir / tagged_name(args.outcsv, args.tag)
    outmd = outdir / tagged_name(args.outmd, args.tag)
    best_plot_base = outdir / tagged_name("ptmu_closure_best_iteration.png", args.tag)
    metric_plot_base = outdir / tagged_name("ptmu_closure_iteration_metrics.png", args.tag)
    best_plot_base = best_plot_base.with_suffix("")
    metric_plot_base = metric_plot_base.with_suffix("")

    f_ref = ROOT.TFile.Open(args.datafile, "READ")
    if not f_ref or f_ref.IsZombie():
        raise RuntimeError(f"Could not open {args.datafile}")
    h_ref = f_ref.Get(args.datahist)
    if not h_ref:
        raise RuntimeError(f"Could not find {args.datahist} in {args.datafile}")
    edges = get_edges_from_hist(h_ref)
    pt_lo, pt_hi = edges[0], edges[-1]

    f_in = ROOT.TFile.Open(args.omnifile, "READ")
    if not f_in or f_in.IsZombie():
        raise RuntimeError(f"Could not open {args.omnifile}")
    t_sig = require_tree(f_in, "mc_signal_reco")

    data_pot, mc_pot, pot_scale = get_pot_scale(f_in, args.use_weights)
    if args.verbose:
        print(f"[INFO] dataPOT={data_pot:.6g}, mcPOT={mc_pot:.6g}, applied potScale={pot_scale:.6g}")
        print(f"[INFO] pTmu range = [{pt_lo}, {pt_hi}]")

    sig = collect_signal_records(t_sig, pt_lo, pt_hi, pot_scale, use_weights=args.use_weights, verbose=args.verbose)
    train_mask, pseudo_mask = split_masks(sig["entry"], args.train_split)

    if not np.any(train_mask):
        raise RuntimeError("Train split is empty")
    if not np.any(pseudo_mask):
        raise RuntimeError("Pseudo-data split is empty")

    closure = build_closure_inputs(sig, train_mask, pseudo_mask, edges, args)
    response, hRespRecoTemplate, hRespTruthTemplate = build_response(closure["train_sig"], edges)

    omni_results = run_unbinned_omnifold(
        closure["train_sig"],
        closure["measured_vals"],
        closure["measured_weights"],
        iterations,
        edges,
    )
    ibu_results = run_ibu(response, closure["hPseudoReco"], iterations)

    rows = []
    rows.append(compute_metrics(closure["hPseudoReco"], closure["hPseudoTruth"], 0, "reco"))

    prev_omni = None
    prev_ibu = None
    for niter in iterations:
        rows.append(compute_metrics(omni_results[niter]["h_truth"], closure["hPseudoTruth"], niter, "omnifold", previous=prev_omni))
        rows.append(compute_metrics(ibu_results[niter], closure["hPseudoTruth"], niter, "ibu", previous=prev_ibu))
        prev_omni = omni_results[niter]["h_truth"]
        prev_ibu = ibu_results[niter]

    best_omni = choose_best_iteration(rows, "omnifold")
    best_ibu = choose_best_iteration(rows, "ibu")
    if best_omni is None:
        best_omni = iterations[0]
    if best_ibu is None:
        best_ibu = iterations[0]

    draw_best_comparison(
        closure["hPseudoTruth"],
        closure["hPseudoReco"],
        ibu_results[best_ibu],
        omni_results[best_omni]["h_truth"],
        best_ibu,
        best_omni,
        best_plot_base,
    )
    draw_metric_scan(rows, metric_plot_base)

    write_metrics_csv(outcsv, rows)
    write_summary_markdown(outmd, args, rows, best_omni, best_ibu)

    f_out = ROOT.TFile.Open(str(outroot), "RECREATE")
    if not f_out or f_out.IsZombie():
        raise RuntimeError(f"Could not create output ROOT file: {outroot}")
    f_out.cd()

    to_write = [
        closure["hPseudoTruth"],
        closure["hPseudoReco"],
        closure["hTrainTruth"],
        closure["hTrainReco"],
        closure["hMorph"],
        hRespRecoTemplate,
        hRespTruthTemplate,
    ]
    for niter in iterations:
        to_write.append(ibu_results[niter])
        to_write.extend(omni_results[niter].values())

    failures = []
    for obj in to_write:
        if obj.Write() <= 0:
            failures.append(obj.GetName())
    f_out.Close()

    if failures:
        raise RuntimeError("Failed to write some ROOT objects: " + ", ".join(failures))

    print(f"[OK] wrote ROOT output: {outroot}")
    print(f"[OK] wrote metrics CSV: {outcsv}")
    print(f"[OK] wrote summary markdown: {outmd}")
    print(f"[OK] wrote plots: {best_plot_base.with_suffix('.png')}, {metric_plot_base.with_suffix('.png')}")
    print(f"[INFO] recommended OmniFold iteration = {best_omni}")
    print(f"[INFO] recommended IBU iteration = {best_ibu}")


if __name__ == "__main__":
    main()
