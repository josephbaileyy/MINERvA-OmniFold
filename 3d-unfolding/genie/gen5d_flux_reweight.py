#!/usr/bin/env python3
"""Exact flux reweight of the s5p gen5d truth 5D predictions (KNOWN_ISSUES 83).

The GENIE CV, GENIE+MEC and NuWro samples behind `gen_to_xsec5d.py` were drawn
from `flux_mefhc_numu.root:flux_numu` (and its NuWro copy), a variable-width TH1D
whose contents are MINERvA flux DENSITIES (`flux_E_unweighted`, non-PPFX). Both
generators pick a flux bin in proportion to its CONTENT and draw E uniformly
inside it (GENIE: `TH1::GetRandom` on the clone gevgen makes, bins with an upper
edge above 50 GeV zeroed; NuWro 21.09 beam_type 5: `EnergyProfile::shoot`, with
the E-weighted RES/DIS proposal removed by the `bias` factor). So the sampled
density is, per flux bin i of the generation range,

    phi_s(E) = c_i / (w_i * sum_range c)

The data are normalized by the PPFX (nu-e constrained) CV flux integrated over
0-100 GeV (`util::GetFluxIntegral` -> `FluxReweighter::GetIntegratedFluxReweighted`),
POT-weighted over the 12 ME FHC playlists. `phi-t` rebuilds that flux phi_t(E)
through the same PlotUtils call and checks its integral against
`flux_integral_universes_MEFHC.root:hFluxCV`. The per-event weight is

    r(E) = (phi_t(E) / Phi_t) / phi_s(E),    Phi_t = int_0^100 phi_t dE

and the repaired predictions are (sigma_CC = (C12+H1) tot_cc graphs / 13,
integrated exactly within each flux bin; the graphs are piecewise linear):

  genie_cv   pred = <sigma_CC>_t,<50 * sum_{bin} r / sum_{all CC} r
  genie_mec  pred = sum_{bin} r * (<sigma_CC>_t,<50 / sum_{nonMEC CC} r)
  nuwro      pred = sum_{bin} w_e r_e / N_total     (w_e = NuWro event weight)

with <sigma_CC>_t,<50 = int_0^50 phi_t sigma_CC dE / Phi_t. Neutrino energies
outside the generation range (GENIE > 50 GeV; NuWro < 0.5 or > 50 GeV) are absent
from the samples; that fraction is quantified, not patched.

Subcommands (run in order, in the analysis env: source setup_salloc_env.sh):
  phi-t       build phi_t and check 3 (needs PlotUtils: libMAT, libMAT-MINERvA)
  reweight    --generator {genie_cv,genie_mec,nuwro}: checks 1 and 2, then product
  gibuu-flux  check 5 (report only)
  marginals   checks 4 and 6
  receipt     machine receipt from the products' meta
"""
import argparse
import datetime
import glob
import hashlib
import json
import math
import os
import platform
import sys
from pathlib import Path

import numpy as np

S5P = "/pscratch/sd/j/josephrb/s5p-20260926"
REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DEFAULTS = {
    "out_dir": f"{S5P}/gen5d_fluxfix",
    "gen5d_dir": f"{S5P}/gen5d",
    "gen5d_tree": f"{S5P}/gen5d/code/tree",
    "genie_dir": f"{REPO}/3d-unfolding/genie",
    "baseline_flux": f"{REPO}/2d-unfolding/baseline_flux",
    "mat_lib": f"{REPO}/MINERvA101/opt/lib",
    "cvmfs_flux": ("/cvmfs/minerva.opensciencegrid.org/minerva/CentralizedFluxAndReweightFiles/"
                   "MATFluxAndReweightFiles/flux/flux-g4numiv6-pdg14-minervame1D1M1NWeightedAve.root"),
    "gibuu_flux": ("/cvmfs/nova.opensciencegrid.org/externals/gibuu/v2019/Linux64bit+2.6-2.12-e15/"
                   "GiBUU/buuinput2019/neutrino/MINERvA_MEflux.dat"),
    "gibuu_jobcard": f"{REPO}/3d-unfolding/genie/work_gibuu/gibuu_mefhc_numu.job",
}
PLAYLISTS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
N_NUCLEONS_CH = 13.0
GEN_RANGE = {"genie_cv": (0.0, 50.0), "genie_mec": (0.0, 50.0), "nuwro": (0.5, 50.0)}
P_MIN = 1e-3            # sampling-model pass threshold on every chi2 p-value
N_SUB = 5               # sub-bins per flux bin for the within-bin uniformity test
POLY_DEG = 3            # smooth sigma-shape factor for the proxy test (in log E)
MIN_EXPECTED = 5.0      # bins/sub-bins with fewer expected events are left out of chi2


# ---------------------------------------------------------------------------
# small utilities
# ---------------------------------------------------------------------------
def sha256(path, chunk=1 << 24):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def file_record(path, role):
    p = os.path.abspath(path)
    return {"path": p, "role": role, "bytes": os.path.getsize(p), "sha256": sha256(p)}


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def environment():
    env = {"python": sys.version.split()[0], "executable": sys.executable,
           "numpy": np.__version__, "host": platform.node(),
           "PLOTUTILSROOT": os.environ.get("PLOTUTILSROOT"), "cwd": os.getcwd()}
    if "ROOT" in sys.modules:
        env["ROOT"] = sys.modules["ROOT"].gROOT.GetVersion()
    return env


def self_record():
    p = Path(__file__).resolve()
    return {"path": str(p), "sha256": sha256(p)}


def dump_json(obj, path):
    with open(path, "w") as f:
        json.dump(obj, f, indent=1)


def chi2_sf(x, k):
    """Upper tail of chi2(k); scipy if present, else Wilson-Hilferty."""
    try:
        from scipy.stats import chi2
        return float(chi2.sf(x, k))
    except Exception:  # noqa: BLE001
        if k <= 0:
            return float("nan")
        z = ((x / k) ** (1 / 3) - (1 - 2 / (9 * k))) / math.sqrt(2 / (9 * k))
        return 0.5 * math.erfc(z / math.sqrt(2))


def import_root():
    import ROOT
    ROOT.gROOT.SetBatch(True)
    ROOT.gErrorIgnoreLevel = ROOT.kError
    return ROOT


def read_th1(ROOT, path, name):
    f = ROOT.TFile.Open(path)
    h = f.Get(name)
    if not h:
        raise SystemExit(f"{name} not in {path}")
    n = h.GetNbinsX()
    e = np.array([h.GetBinLowEdge(i) for i in range(1, n + 2)], float)
    c = np.array([h.GetBinContent(i) for i in range(1, n + 1)], float)
    f.Close()
    return e, c


def load_g5(tree):
    """Import gen_to_xsec5d from the sha-pinned export the gen5d build ran from."""
    gdir = str(Path(tree) / "3d-unfolding" / "genie")
    sys.path.insert(0, gdir)
    import gen_to_xsec5d as g5
    got = Path(g5.__file__).resolve()
    if not str(got).startswith(str(Path(tree).resolve())):
        raise SystemExit(f"gen_to_xsec5d imported from {got}, not from {tree}")
    return g5


def code_files_of(g5):
    mods = [g5, g5.u3d, g5.u3d.u2d, g5.g3d, g5.gew, g5.gibew, g5.gib3d,
            sys.modules["gst_reader"], sys.modules["xsec_3d"]]
    out = [self_record()]
    for m in mods:
        p = Path(m.__file__).resolve()
        out.append({"path": str(p), "sha256": sha256(p)})
    return out


# ---------------------------------------------------------------------------
# cross-section graphs: exact integrals of the piecewise-linear TGraphs
# ---------------------------------------------------------------------------
class SigmaCC:
    """sigma_CC(E) per nucleon from GENIE xsec_graphs.root tot_cc (TGraph::Eval,
    linear, linearly extrapolated beyond the last knot at 50 GeV).
    target 'CH' -> (C12 + H1)/13 (the existing converters); 'C12' -> C12/12."""

    def __init__(self, ROOT, graphs_file, target="CH"):
        self.f = ROOT.TFile.Open(graphs_file)
        self.graphs = []
        species = ("C12", "H1") if target == "CH" else ("C12",)
        for sp in species:
            g = None
            for k in self.f.GetListOfKeys():
                nm = k.GetName()
                if sp in nm and nm.startswith("nu_mu"):
                    g = self.f.Get(nm).Get("tot_cc")
                    break
            if not g:
                raise SystemExit(f"tot_cc for {sp} not in {graphs_file}")
            self.graphs.append(g)
        self.norm = (N_NUCLEONS_CH if target == "CH" else 12.0)
        g0 = self.graphs[0]
        self.knots = np.array([g0.GetX()[i] for i in range(g0.GetN())], float)
        for g in self.graphs[1:]:
            kk = np.array([g.GetX()[i] for i in range(g.GetN())], float)
            self.knots = np.union1d(self.knots, kk)
        self.x_max = float(self.knots.max())

    def __call__(self, E):
        E = np.atleast_1d(np.asarray(E, float))
        v = np.array([sum(g.Eval(float(e)) for g in self.graphs) for e in E])
        return v / self.norm * 1.0e-38      # cm^2 / nucleon

    def integral(self, lo, hi):
        """int_lo^hi sigma dE, exact (trapezoid on every knot inside [lo,hi])."""
        k = self.knots[(self.knots > lo) & (self.knots < hi)]
        x = np.concatenate([[lo], k, [hi]])
        y = self(x)
        return float(np.sum(0.5 * (y[1:] + y[:-1]) * np.diff(x)))

    def bin_integrals(self, edges):
        return np.array([self.integral(a, b) for a, b in zip(edges[:-1], edges[1:])])


# ---------------------------------------------------------------------------
# phi_t: the flux the data normalization integrates
# ---------------------------------------------------------------------------
def cmd_phi_t(args):
    ROOT = import_root()
    for lib in ("libMAT.so", "libMAT-MINERvA.so"):
        rc = ROOT.gSystem.Load(os.path.join(args.mat_lib, lib))
        if rc < 0:
            raise SystemExit(f"cannot load {lib} from {args.mat_lib}")
    pu = os.environ.get("PLOTUTILSROOT")
    if not pu:
        raise SystemExit("PLOTUTILSROOT unset: source setup_salloc_env.sh first")
    B = args.baseline_flux
    groups, dens, phi_int, pot, frw_integral, per_pl = {}, {}, {}, {}, {}, []
    edges = None
    for pl in PLAYLISTS:
        # util/GetFluxIntegral.cpp: flux_reweighter(univ.GetPlaylist(), 14,
        # univ.UseNuEConstraint(), univ.GetNFluxUniverses()); runEventLoop.cpp:348-351
        # sets NuEConstraint=true, AnalysisNuPDG=14, NFluxUniverses=100.
        frw = ROOT.PlotUtils.flux_reweighter("minervame" + pl, 14, True, 100)
        h = frw.GetFluxReweighted(14)
        n = h.GetNbinsX()
        e = np.array([h.GetBinLowEdge(i) for i in range(1, n + 2)], float)
        c = np.array([h.GetBinContent(i) for i in range(1, n + 1)], float)
        if edges is None:
            edges = e
        elif not np.array_equal(e, edges):
            raise SystemExit(f"flux edges differ for {pl}")
        dens[pl] = c
        # the exact call GetIntegratedFluxReweighted makes (FluxReweighter.cxx:1321-1326)
        frw_integral[pl] = float(h.Integral(h.FindBin(0.0), h.FindBin(100.0), "width"))
        phi_int[pl] = float(np.sum(c * np.diff(e)))
        fd = ROOT.TFile.Open(f"{B}/runEventLoopData_{pl}.root")
        pot[pl] = float(fd.Get("POTUsed").GetVal())
        fd.Close()
        fm = ROOT.TFile.Open(f"{B}/runEventLoopMC_{pl}.root")
        hm = fm.Get("pTmu_reweightedflux_integrated")
        stored = np.array([hm.GetBinContent(i) for i in range(1, hm.GetNbinsX() + 1)])
        fm.Close()
        per_pl.append({"playlist": pl, "data_POT": pot[pl], "Phi_frw_Integral_width": frw_integral[pl],
                       "Phi_sum_c_w": phi_int[pl],
                       "stored_pTmu_reweightedflux_integrated_bin1": float(stored[0]),
                       "stored_all_bins_equal": bool(np.all(stored == stored[0])),
                       "rel_diff_frw_vs_stored": float(abs(frw_integral[pl] - stored[0]) / stored[0])})
        groups.setdefault(c.tobytes(), []).append(pl)
    opened = sorted({ROOT.gROOT.GetListOfFiles().At(i).GetName()
                     for i in range(ROOT.gROOT.GetListOfFiles().GetSize())})
    W = sum(pot.values())
    phi_t = sum(pot[pl] * dens[pl] for pl in PLAYLISTS) / W        # density, m^-2/POT/GeV
    w = np.diff(edges)
    Phi_t = float(np.sum(phi_t * w))
    Phi_pot = sum(pot[pl] * frw_integral[pl] for pl in PLAYLISTS) / W
    fc = ROOT.TFile.Open(f"{B}/flux_integral_universes_MEFHC.root")
    hcv = fc.Get("hFluxCV")
    hfcv = np.array([hcv.GetBinContent(i) for i in range(1, hcv.GetNbinsX() + 1)])
    fc.Close()

    # the generation flux (non-PPFX) and its cvmfs source
    eg, cg = read_th1(ROOT, os.path.join(args.genie_dir, "flux_mefhc_numu.root"), "flux_numu")
    en, cn = read_th1(ROOT, os.path.join(args.genie_dir, "flux_mefhc_numu_nuwro.root"), "flux_numu")
    ec, cc = read_th1(ROOT, args.cvmfs_flux, "flux_E_unweighted")
    if not (np.array_equal(eg, edges) and np.array_equal(en, edges) and np.array_equal(ec, edges)):
        raise SystemExit("generation flux edges differ from phi_t edges")
    phi_u = cg / np.sum(cg * w)
    ratio = (phi_t / Phi_t) / phi_u
    bands = [(0, 0.5), (0.5, 2), (2, 5), (5, 10), (10, 15), (15, 20), (20, 30), (30, 50), (50, 100)]
    band_rows = []
    for a, b in bands:
        m = (edges[:-1] >= a) & (edges[1:] <= b)
        band_rows.append({"E_lo": a, "E_hi": b,
                          "frac_phi_t": float(np.sum(phi_t[m] * w[m]) / Phi_t),
                          "frac_phi_unweighted": float(np.sum(phi_u[m] * w[m])),
                          "ratio_of_fracs": float(np.sum(phi_t[m] * w[m]) / Phi_t / np.sum(phi_u[m] * w[m]))})
    flux_files = []
    for g in ("minervame1D", "minervame1M", "minervame1N"):
        for pdg in ("14", "-14"):
            for fv in ("gen2thin", "g4numiv6"):
                p = f"{pu}/data/flux/flux-{fv}-pdg{pdg}-{g}_rearrangedUniverses.root"
                if os.path.exists(p):
                    flux_files.append(file_record(p, "PlotUtils FluxReweighter input"))
    out = os.path.join(args.out_dir, "phi_t.npz")
    np.savez(out, edges=edges, phi_t_density=phi_t, Phi_t=np.float64(Phi_t),
             phi_unweighted_contents=cg, phi_nuwro_contents=cn,
             **{f"density_{pl}": dens[pl] for pl in PLAYLISTS},
             pot=np.array([pot[pl] for pl in PLAYLISTS]), playlists=np.array(PLAYLISTS))
    meta = {
        "schema": "gen5d-fluxfix-phi-t/v1", "created_utc": now(),
        "definition": ("phi_t = sum_p POT_p * FluxReweighter(minervame<p>, nu_pdg 14, nuE constraint "
                       "true, 100 universes).GetFluxReweighted(14) / sum_p POT_p; the 12 ME FHC "
                       "playlists; POT_p = runEventLoopData_<p>.root:POTUsed. Units m^-2/POT/GeV "
                       "(density; integral with bin widths). Same edges as flux_numu."),
        "histogram": ("PlotUtils::FluxReweighter::GetFluxReweighted(14) = flux_E_cvweighted of "
                      f"{pu}/data/flux/flux-gen2thin-pdg14-<group>_rearrangedUniverses.root "
                      "(group minervame1D/1M/1N) after the nu-e Constrainer"),
        "Phi_t_0_100_m2_per_POT": Phi_t,
        "Phi_t_pot_weighted_frw_integrals": Phi_pot,
        "hFluxCV_path": f"{B}/flux_integral_universes_MEFHC.root",
        "hFluxCV_values_all_equal": bool(np.all(np.abs(hfcv - hfcv[0]) <= 1e-15 * hfcv[0])),
        "hFluxCV_bin1": float(hfcv[0]),
        "rel_diff_Phi_t_vs_hFluxCV_max_over_bins": float(np.max(np.abs(Phi_t - hfcv) / hfcv)),
        "rel_diff_Phi_pot_vs_hFluxCV_max_over_bins": float(np.max(np.abs(Phi_pot - hfcv) / hfcv)),
        "per_playlist": per_pl,
        "distinct_playlist_flux_shapes": [sorted(v) for v in groups.values()],
        "generation_flux": {
            "flux_numu_equals_cvmfs_flux_E_unweighted_bitwise": bool(np.array_equal(cg, cc)),
            "nuwro_copy_equals_generation_flux_where_nonzero": bool(np.array_equal(cn[cn > 0], cg[cn > 0])),
            "nuwro_nonzero_bins_E_range": [float(edges[:-1][cn > 0].min()), float(edges[1:][cn > 0].max())],
            "integral_width_unweighted_0_100": float(np.sum(cg * w)),
            "integral_width_over_Phi_t": float(np.sum(cg * w) / Phi_t),
        },
        "shape_ratio_bands": band_rows,
        "shape_ratio_per_bin": {"E_lo": edges[:-1].tolist(), "E_hi": edges[1:].tolist(),
                                "phi_t_norm_over_phi_unweighted_norm": ratio.tolist()},
        "inputs": ([file_record(f"{B}/runEventLoopData_{pl}.root", "data POT") for pl in PLAYLISTS]
                   + [file_record(f"{B}/runEventLoopMC_{pl}.root", "stored flux integral") for pl in PLAYLISTS]
                   + [file_record(f"{B}/flux_integral_universes_MEFHC.root", "hFluxCV"),
                      file_record(os.path.join(args.genie_dir, "flux_mefhc_numu.root"), "generation flux (GENIE)"),
                      file_record(os.path.join(args.genie_dir, "flux_mefhc_numu_nuwro.root"), "generation flux (NuWro)"),
                      file_record(args.cvmfs_flux, "cvmfs source of the generation flux")]
                   + flux_files),
        "root_files_open_after_frw": opened,
        "npz": os.path.abspath(out), "npz_sha256": sha256(out),
        "code": [self_record()], "environment": environment(), "argv": sys.argv,
    }
    dump_json(meta, os.path.join(args.out_dir, "phi_t.json"))
    print(json.dumps({k: meta[k] for k in ("Phi_t_0_100_m2_per_POT", "hFluxCV_bin1",
                                          "rel_diff_Phi_t_vs_hFluxCV_max_over_bins",
                                          "generation_flux", "shape_ratio_bands")}, indent=1))


def load_phi_t(out_dir):
    p = os.path.join(out_dir, "phi_t.npz")
    z = np.load(p)
    meta = json.load(open(os.path.join(out_dir, "phi_t.json")))
    if sha256(p) != meta["npz_sha256"]:
        raise SystemExit("phi_t.npz does not match phi_t.json")
    return z, meta, p


# ---------------------------------------------------------------------------
# check 1: sampling model
# ---------------------------------------------------------------------------
def sampling_test(E, edges, contents, lo, hi, sig, strict, label):
    """Tests: E is drawn with bin mass ~ c_i * int_bin sigma / w_i, uniform x sigma inside.
    strict: sigma is the generator's own sigma (no free shape); otherwise a smooth
    factor exp(poly_POLY_DEG(log E)) absorbs the generator/graph sigma-shape ratio."""
    w = np.diff(edges)
    rng = (edges[:-1] >= lo - 1e-12) & (edges[1:] <= hi + 1e-12) & (contents > 0)
    idx = np.where(rng)[0]
    ib = np.searchsorted(edges, E, side="right") - 1
    outside = int(np.sum(~np.isin(ib, idx)))
    n = np.bincount(ib[np.isin(ib, idx)], minlength=w.size)[idx].astype(float)
    I = np.array([sig.integral(edges[i], edges[i + 1]) for i in idx])
    xc = np.log(0.5 * (edges[idx] + edges[idx + 1]))

    def across(mass):
        e = n.sum() * mass / mass.sum()
        if not strict:
            # weighted LSQ of log(n/e) on a poly in log E (var ~ 1/n), then renormalize
            ok = n > 0
            A = np.vander(xc[ok], POLY_DEG + 1)
            wt = np.sqrt(n[ok])
            coef, *_ = np.linalg.lstsq(A * wt[:, None], np.log(n[ok] / e[ok]) * wt, rcond=None)
            for _ in range(5):      # a few Poisson IRLS steps
                f = np.exp(np.vander(xc, POLY_DEG + 1) @ coef)
                ef = e * f * n.sum() / np.sum(e * f)
                wt = np.sqrt(ef[ok])
                coef, *_ = np.linalg.lstsq(A * wt[:, None],
                                           (np.log(ef[ok] / e[ok]) + (n[ok] - ef[ok]) / ef[ok]) * wt,
                                           rcond=None)
            f = np.exp(np.vander(xc, POLY_DEG + 1) @ coef)
            e = e * f * n.sum() / np.sum(e * f)
        m = e >= MIN_EXPECTED
        pull = (n - e) / np.sqrt(np.maximum(e, 1e-300))
        chi2 = float(np.sum(pull[m] ** 2))
        ndf = int(m.sum()) - 1 - (0 if strict else POLY_DEG)
        return {"chi2": chi2, "ndf": ndf, "p": chi2_sf(chi2, ndf),
                "max_abs_pull": float(np.max(np.abs(pull[m]))),
                "E_lo_of_max_pull": float(edges[idx][m][np.argmax(np.abs(pull[m]))]),
                "n_bins_used": int(m.sum()), "n_bins_low_expectation": int((~m).sum()),
                "pull_per_bin": pull.tolist()}

    null = across(contents[idx] / w[idx] * I)            # content-proportional bin masses
    alt = across(contents[idx] * I)                       # density x width (the other reading)
    # within-bin: N_SUB equal sub-bins, expected ~ int_sub sigma, conditional on the bin count
    chi2_in, ndf_in, max_in, chi2_wide, ndf_wide = 0.0, 0, 0.0, 0.0, 0
    for k, i in enumerate(idx):
        a, b = edges[i], edges[i + 1]
        sub = np.linspace(a, b, N_SUB + 1)
        Ei = E[ib == i]
        if Ei.size == 0:
            continue
        o = np.histogram(Ei, sub)[0].astype(float)
        si = np.array([sig.integral(sub[j], sub[j + 1]) for j in range(N_SUB)])
        e = Ei.size * si / si.sum()
        if np.min(e) < MIN_EXPECTED:
            continue
        c2 = float(np.sum((o - e) ** 2 / e))
        chi2_in += c2
        ndf_in += N_SUB - 1
        max_in = max(max_in, float(np.max(np.abs(o - e) / np.sqrt(e))))
        if w[i] >= 0.5 - 1e-9:
            chi2_wide += c2
            ndf_wide += N_SUB - 1
    within = {"chi2": chi2_in, "ndf": ndf_in, "p": chi2_sf(chi2_in, ndf_in) if ndf_in else None,
              "max_abs_pull": max_in, "wide_bins_chi2": chi2_wide, "wide_bins_ndf": ndf_wide,
              "wide_bins_p": chi2_sf(chi2_wide, ndf_wide) if ndf_wide else None}
    passed = bool(null["p"] >= P_MIN and (within["p"] is None or within["p"] >= P_MIN)
                  and outside == 0)
    return {"population": label, "n_events": int(E.size), "n_outside_generation_bins": outside,
            "mode": "strict (generator sigma graphs, no free shape)" if strict else
                    f"proxy (GENIE graph sigma x smooth exp(poly{POLY_DEG}(log E)) factor)",
            "E_range": [lo, hi], "n_flux_bins": int(idx.size),
            "across_bins_content_proportional": null,
            "across_bins_alternative_density_x_width": {k: v for k, v in alt.items() if k != "pull_per_bin"},
            "within_bin_uniform_x_sigma": within,
            "flux_bin_E_lo": edges[idx].tolist(),
            "pass_rule": f"p >= {P_MIN} for across-bin and within-bin chi2, and no event outside "
                         "the generation bins",
            "pass": passed}


# ---------------------------------------------------------------------------
# reweight
# ---------------------------------------------------------------------------
def flux_weights(edges, contents, phi_t, Phi_t, lo, hi):
    w = np.diff(edges)
    rng = (edges[:-1] >= lo - 1e-12) & (edges[1:] <= hi + 1e-12) & (contents > 0)
    c = np.where(rng, contents, 0.0)
    phi_s = c / (w * c.sum())
    r = np.zeros_like(phi_s)
    r[rng] = (phi_t[rng] / Phi_t) / phi_s[rng]
    return phi_s, r, rng


def r_of(E, edges, rbin, rng):
    """r at each E; 0 outside the generation bins (such events fail check 1 first)."""
    ib = np.searchsorted(edges, E, side="right") - 1
    ok = (ib >= 0) & (ib < rbin.size)
    ibc = np.clip(ib, 0, rbin.size - 1)
    return np.where(ok & rng[ibc], rbin[ibc], 0.0)


def compare_arrays(a, ref):
    nz = ref != 0
    return {"bitwise_equal": bool(np.array_equal(a, ref)),
            "max_rel_diff_nonzero": float(np.max(np.abs(a[nz] - ref[nz]) / np.abs(ref[nz]))) if nz.any() else 0.0,
            "n_zero_mismatch": int(np.sum((a == 0) != (ref == 0)))}


def cmd_reweight(args):
    ROOT = import_root()
    g5 = load_g5(args.gen5d_tree)
    gen = args.generator
    G = args.genie_dir
    AX, E5 = g5.AXES, g5.EDGES
    dV5 = g5.widths(*AX)
    z, phit_meta, phit_path = load_phi_t(args.out_dir)
    edges, phi_t, Phi_t = z["edges"], z["phi_t_density"], float(z["Phi_t"])
    old_npz = os.path.join(args.gen5d_dir, f"{'nuwro_cv' if gen == 'nuwro' else gen}_xsec5d.npz")
    old = np.load(old_npz, allow_pickle=True)
    old_meta = json.loads(str(old["meta_json"]))
    graphs = os.path.join(G, "xsec_graphs.root")
    sig = SigmaCC(ROOT, graphs, "CH")
    lo, hi = GEN_RANGE[gen]
    inputs = [file_record(old_npz, "pre-fix product (identity reference)"),
              file_record(phit_path, "phi_t"), file_record(graphs, "sigma_CC graphs")]

    if gen in ("genie_cv", "genie_mec"):
        gst = os.path.join(G, "genie_mefhc_cv_ALL.gst.root" if gen == "genie_cv"
                           else "genie_mefhc_mec_ALL.gst.root")
        flux = os.path.join(G, "flux_mefhc_numu.root")
        e_s, c_s = read_th1(ROOT, flux, "flux_numu")
        inputs += [file_record(gst, "events"), file_record(flux, "generation flux")]
        ev, norm, diag = g5.extract_genie(gst, gen == "genie_mec", graphs, flux, "flux_numu",
                                          args.parity_n)
        d = ROOT.RDataFrame("gst", gst).AsNumpy(["cc", "mec", "Ev", "pxl", "pyl", "pzl"])
        cc = d["cc"].astype(bool)
        mec = d["mec"].astype(bool)
        pt = np.hypot(d["pxl"], d["pyl"])
        pz = d["pzl"]
        in_ps = g5.u3d.u2d.in_truth_phase_space
        PT, PZ = E5["pt"], E5["pz"]
        inps = np.fromiter((c and in_ps(float(a), float(b), PT[0], PT[-1], PZ[0], PZ[-1])
                            for c, a, b in zip(cc.tolist(), pt.tolist(), pz.tolist())),
                           dtype=bool, count=cc.size)
        sel = np.where(inps)[0]
        if not (np.array_equal(pt[sel], ev["pt"]) and np.array_equal(pz[sel], ev["pz"])):
            raise SystemExit("event alignment with extract_genie failed")
        Ev = d["Ev"]
        E_ps = Ev[sel]
        nonmec_cc = cc & ~mec
        pop_B = cc if gen == "genie_cv" else nonmec_cc
        # ---- check 1
        samp = [sampling_test(Ev[nonmec_cc], e_s, c_s, lo, hi, sig, True,
                              "non-MEC CC events (all, not only in PS)")]
        if gen == "genie_mec":
            samp.append(sampling_test(Ev[cc & mec], e_s, c_s, lo, hi, sig, False,
                                      "MEC CC events (no MEC graph: mec_cc graph is 0)"))
        phi_s, rbin, rng = flux_weights(e_s, c_s, phi_t, Phi_t, lo, hi)
        r_all = r_of(Ev, e_s, rbin, rng)
        r_ps = r_all[sel]
        w_i = np.diff(e_s)
        I = sig.bin_integrals(e_s)
        sigma_s = float(np.sum(phi_s * I))
        sigma_t50 = float(np.sum(np.where(rng, phi_t / Phi_t, 0.0) * I))
        sigma_t100 = float(np.sum(phi_t / Phi_t * I))
        n_pop = int(pop_B.sum())
        Bsum = float(np.sum(r_all[pop_B]))
        # ---- check 2: identity with r == 1 and the old constants
        x_id, v_id = build_genie(g5, gen, ev, np.ones(sel.size),
                                 norm["sigma_totcc_flux_avg_per_nucleon_cm2"],
                                 float(norm["N_cc"] if gen == "genie_cv" else norm["N_nonMEC_cc"]), dV5)
        # ---- repaired
        x5, v5 = build_genie(g5, gen, ev, r_ps, sigma_t50, Bsum, dV5)
        A_over_B = sigma_t50 / Bsum
        cross = {"form": "unnormalized: <sigma_CC>_s x sum_bin r / N_pop "
                         "(N_pop = N_cc for genie_cv, N_nonMEC for genie_mec)",
                 "sigma_s_cm2": sigma_s, "N_pop": n_pop,
                 "factor_unnormalized_over_selfnormalized": (sigma_s / n_pop) / A_over_B,
                 "mc_rel_error_of_mean_r": float(np.std(r_all[pop_B]) / np.mean(r_all[pop_B])
                                                 / math.sqrt(n_pop))}
        cross["pull"] = (cross["factor_unnormalized_over_selfnormalized"] - 1) / cross["mc_rel_error_of_mean_r"]
        cross["integrated_sigma_unnormalized_form_cm2"] = float(
            np.sum(x5 * g5.widths(*AX)) * cross["factor_unnormalized_over_selfnormalized"])
        normalisation = {
            "convention": ("genie_cv: pred = <sigma_CC>_t,<50 * sum_bin r / sum_allCC r"
                           if gen == "genie_cv" else
                           "genie_mec: pred = sum_bin r * (<sigma_CC>_t,<50 / sum_nonMEC-CC r) "
                           "(weighted analogue of "
                           f"{Path(args.gen5d_tree).resolve()}/3d-unfolding/genie/genie_mec_to_xsec3d.py)"),
            "sigma_CC_t_lt50_per_nucleon_cm2": sigma_t50,
            "sigma_CC_t_0_100_per_nucleon_cm2_graph_extrapolated_above_50": sigma_t100,
            "sigma_CC_s_per_nucleon_cm2": sigma_s,
            "sigma_CC_oldcode_per_nucleon_cm2": norm["sigma_totcc_flux_avg_per_nucleon_cm2"],
            "sum_r_normalising_population": Bsum, "N_normalising_population": n_pop,
            "N_events_in_file": int(cc.size), "N_cc": int(cc.sum()),
            "N_nonMEC_cc": int(nonmec_cc.sum()),
            "sum_r_allCC": float(np.sum(r_all[cc])), "sum_r_nonMEC_CC": float(np.sum(r_all[nonmec_cc])),
            "graphs": graphs, "flux": flux, "flux_hist": "flux_numu",
        }
        if gen == "genie_mec":
            normalisation["factor_to_eavailW_band_convention"] = float(
                np.sum(r_all[nonmec_cc]) / np.sum(r_all[cc]))
            normalisation["factor_to_eavailW_band_convention_unweighted_prefix"] = norm[
                "factor_to_eavailW_band_convention"]
        r_pop = r_all[pop_B]
        extra = {"n_events_E_outside_generation_range": int(np.sum((Ev < lo) | (Ev > hi))),
                 "r_min_max_in_range": [float(rbin[rng].min()), float(rbin[rng].max())]}
    else:
        new = sorted(glob.glob(os.path.join(args.gen5d_dir, "nuwro_flat5d", "nuwro_flat5d_p*.root")))
        oldf = sorted(glob.glob(os.path.join(G, "work_nuwro_p*/nuwro_flat.root")))
        flux = os.path.join(G, "flux_mefhc_numu_nuwro.root")
        e_s, c_s = read_th1(ROOT, flux, "flux_numu")
        inputs += [file_record(p, "events (nuwro_to_flat_5d.C output)") for p in new]
        inputs += [file_record(flux, "generation flux (NuWro)")]
        ev, norm, diag = g5.extract_nuwro(new, oldf)
        cols = ["cc", "pt", "pz", "Enu", "weight", "dyn"]
        acc = {k: [] for k in cols}
        for fn in new:
            dd = ROOT.RDataFrame("nuwro_obs", fn).AsNumpy(cols)
            for k in cols:
                acc[k].append(dd[k])
        d = {k: np.concatenate(v) for k, v in acc.items()}
        ccm = d["cc"].astype(bool)
        PT, PZ = E5["pt"], E5["pz"]
        ptc, pzc = d["pt"][ccm], d["pz"][ccm]
        m = (np.isfinite(ptc) & np.isfinite(pzc) & (ptc >= PT[0]) & (ptc <= PT[-1])
             & (pzc >= PZ[0]) & (pzc <= PZ[-1])
             & (np.arctan2(ptc, pzc) < g5.u3d.u2d.MAX_MUON_THETA_RAD))
        if not (np.array_equal(ptc[m], ev["pt"]) and np.array_equal(pzc[m], ev["pz"])
                and np.array_equal(d["weight"][ccm][m], ev["weight_raw"])):
            raise SystemExit("event alignment with extract_nuwro failed")
        Ev = d["Enu"]
        E_ps = Ev[ccm][m]
        sigC = SigmaCC(ROOT, graphs, "C12")
        dyn = d["dyn"]
        dism = (dyn > 1) & (dyn < 6)
        samp = [sampling_test(Ev[ccm], e_s, c_s, lo, hi, sigC, False, "all CC events"),
                sampling_test(Ev[ccm & dism], e_s, c_s, lo, hi, sigC, False,
                              "CC RES/DIS (dyn 2-5; E-weighted proposal + bias)"),
                sampling_test(Ev[ccm & ~dism], e_s, c_s, lo, hi, sigC, False,
                              "CC QEL/COH/MEC (dyn 0,1,6-9; plain proposal)")]
        phi_s, rbin, rng = flux_weights(e_s, c_s, phi_t, Phi_t, lo, hi)
        r_all = r_of(Ev, e_s, rbin, rng)
        r_ps = r_all[ccm][m]
        N_total = float(ev["divisor"])
        # ---- check 2: identity
        x_id, v_id = build_weighted_nuwro(g5, ev, np.ones(r_ps.size), N_total, dV5)
        x5, v5 = build_weighted_nuwro(g5, ev, r_ps, N_total, dV5)
        IC = sigC.bin_integrals(e_s)
        sC_s = float(np.sum(phi_s * IC))
        sC_t = float(np.sum(np.where(rng, phi_t / Phi_t, 0.0) * IC))
        mean_r = float(np.mean(r_all))
        cross = {"form": ("self-normalized: w_mean x (<sigma_G,C12>_t,range / <sigma_G,C12>_s) x "
                          "sum_bin r / sum_all r, with GENIE C12 graphs as the sigma-shape proxy; the "
                          "ratio primary/self-normalized = mean(r) / (<sigma_G>_t/<sigma_G>_s), a global "
                          "constant that tests sampling + the proxy shape"),
                 "mean_r_all_events": mean_r,
                 "genie_C12_proxy_expected_mean_r": sC_t / sC_s,
                 "factor_primary_over_selfnormalized": mean_r / (sC_t / sC_s),
                 "mc_rel_error_of_mean_r": float(np.std(r_all) / mean_r / math.sqrt(r_all.size))}
        cross["pull"] = (cross["factor_primary_over_selfnormalized"] - 1) / cross["mc_rel_error_of_mean_r"]
        normalisation = {
            "convention": "nuwro: pred = sum_bin w_e r_e / N_total (w_e = NuWro flux-avg sigma "
                          "over its sampled spectrum; N_total all events)",
            "N_total": int(N_total), "N_cc": int(ccm.sum()),
            "weight_mean_cm2": float(np.mean(d["weight"])),
            "weighted_sigma_total_estimate_cm2": float(np.sum(d["weight"] * r_all) / N_total),
            "flux": flux, "flux_hist": "flux_numu",
        }
        r_pop = r_all
        extra = {"n_events_E_outside_generation_range": int(np.sum((Ev < lo) | (Ev > hi))),
                 "r_min_max_in_range": [float(rbin[rng].min()), float(rbin[rng].max())],
                 "dyn_counts_cc": {str(int(k)): int(v) for k, v in
                                   zip(*np.unique(dyn[ccm], return_counts=True))}}

    ident = {"xsec_flat": compare_arrays(x_id.reshape(-1), np.asarray(old["xsec_flat"])),
             "sumw2_flat": compare_arrays(v_id.reshape(-1), np.asarray(old["sumw2_flat"])),
             "nevt_flat": compare_arrays(g5.hist([ev[a] for a in AX], None, [E5[a] for a in AX]).reshape(-1),
                                         np.asarray(old["nevt_flat"]))}
    ident["pass"] = bool(all(v["bitwise_equal"] or v["max_rel_diff_nonzero"] <= 1e-12
                             for v in ident.values()) and all(v["n_zero_mismatch"] == 0
                                                              for v in ident.values()))
    samp_pass = all(s["pass"] for s in samp)
    check_path = os.path.join(args.out_dir, f"{'nuwro_cv' if gen == 'nuwro' else gen}_checks.json")
    dump_json({"sampling_model": samp, "identity": ident, "created_utc": now()}, check_path)
    if not (samp_pass and ident["pass"]):
        print(json.dumps({"sampling_pass": [s["pass"] for s in samp], "identity": ident}, indent=1))
        raise SystemExit(f"STOP: check failed; see {check_path}")

    nevt5 = g5.hist([ev[a] for a in AX], None, [E5[a] for a in AX])
    vol = g5.widths(*AX)
    tot_new = float(np.sum(x5 * vol))
    tot_old = float(np.sum(np.asarray(old["xsec_flat"]).reshape(x5.shape) * vol))
    pzi = AX.index("pz")
    hi_pz = np.asarray(E5["pz"][:-1]) >= 6.0
    def frac_hi(x):
        s = (x * vol).sum(axis=tuple(i for i in range(5) if i != pzi))
        return float(s[hi_pz].sum() / s.sum())
    neff = lambda rr: float(rr.sum() ** 2 / np.sum(rr ** 2))
    # delta-method variance including the normalization-sum fluctuation (diagnostic only)
    diag_var = None
    if gen in ("genie_cv", "genie_mec"):
        S2 = g5.hist([ev[a] for a in AX], r_ps ** 2, [E5[a] for a in AX])
        S1 = g5.hist([ev[a] for a in AX], r_ps, [E5[a] for a in AX])
        p_b = S1 / Bsum
        v_delta = (A_over_B ** 2) * (S2 * (1 - 2 * p_b) + p_b ** 2 * np.sum(r_pop ** 2)) / dV5 ** 2
        mnz = v5 > 0
        diag_var = {"max_rel_diff_delta_method_vs_sumw2": float(np.max(np.abs(v_delta[mnz] - v5[mnz]) / v5[mnz]))}
    key = "nuwro_cv" if gen == "nuwro" else gen
    out = os.path.join(args.out_dir, f"{key}_xsec5d.npz")
    meta = {
        "schema": "gen5d-fluxfix/v1", "created_utc": now(), "generator": key,
        "generator_label": old_meta["generator_label"],
        "quantity": old_meta["quantity"], "axes": list(AX), "shape": list(g5.SHAPE), "order": "C",
        "edges": {a: E5[a].tolist() for a in AX},
        "phase_space": old_meta["phase_space"], "definitions": old_meta["definitions"],
        "fix": {
            "issue": "KNOWN_ISSUES.md row 83 (s5p review round 1 F1)",
            "phi_s": "c_i / (w_i * sum_range c) on the generation flux bins "
                     f"(E in [{lo},{hi}] GeV, content > 0), zero elsewhere",
            "phi_t": "POT-weighted PPFX nu-e-constrained CV flux density (phi_t.json), / Phi_t over 0-100 GeV",
            "r": "r(E) = (phi_t(E)/Phi_t) / phi_s(E), piecewise constant on the flux bins",
            "sumw2_flat": "sum over events in the cell of (per-event contribution)^2 / dV^2, "
                          "normalization constants treated as exact (the gen5d convention)",
            "nevt_flat": "raw event counts (unchanged)",
            "effective_N": "per cell (sum r)^2/sum r^2 = xsec_flat^2/sumw2_flat",
        },
        "phi_t": {"json": os.path.join(args.out_dir, "phi_t.json"),
                  "json_sha256": sha256(os.path.join(args.out_dir, "phi_t.json")),
                  "npz": phit_path, "npz_sha256": phit_meta["npz_sha256"],
                  "Phi_t_0_100_m2_per_POT": Phi_t,
                  "rel_diff_vs_hFluxCV": phit_meta["rel_diff_Phi_t_vs_hFluxCV_max_over_bins"]},
        "normalisation": normalisation,
        "range_limitation": range_limitation(sig, edges, phi_t, Phi_t, gen,
                                             SigmaCC(ROOT, graphs, "C12") if gen == "nuwro" else None),
        "checks": {"sampling_model": samp, "identity_r1_old_normalisation": ident,
                   "cross_check_normalisation": cross, "variance_diagnostic": diag_var},
        "weights": {"r_sum_in_ps": float(r_ps.sum()), "r2_sum_in_ps": float(np.sum(r_ps ** 2)),
                    "effective_N_in_ps": neff(r_ps), "n_in_ps": int(r_ps.size),
                    "effective_N_normalising_population": neff(r_pop),
                    "n_normalising_population": int(r_pop.size),
                    "r_quantiles_in_ps_1_50_99": np.percentile(r_ps, [1, 50, 99]).tolist(), **extra},
        "integrated_sigma_cm2": {"before_fix_5d_grid": tot_old, "after_fix_5d_grid": tot_new,
                                 "after_over_before": tot_new / tot_old,
                                 "after_stat_rel_err": float(np.sqrt(np.sum(v5 * vol ** 2)) / tot_new),
                                 "frac_pz_ge_6_before": frac_hi(np.asarray(old["xsec_flat"]).reshape(x5.shape)),
                                 "frac_pz_ge_6_after": frac_hi(x5)},
        "pre_fix_product": {"path": old_npz, "sha256": inputs[0]["sha256"],
                            "normalisation": old_meta["normalisation"]},
        "gen5d_extract_diagnostics": diag,
        "inputs": inputs,
        "code": {"files": code_files_of(g5), "gen5d_tree": str(Path(args.gen5d_tree).resolve())},
        "environment": environment(), "argv": sys.argv,
        "checks_json": check_path,
    }
    np.savez(out, xsec_flat=x5.reshape(-1), sumw2_flat=v5.reshape(-1), nevt_flat=nevt5.reshape(-1),
             n_events=np.int64(nevt5.sum()), **{f"edges_{a}": E5[a] for a in AX},
             shape=np.asarray(g5.SHAPE), meta_json=np.asarray(json.dumps(meta)))
    dump_json(meta, os.path.splitext(out)[0] + ".meta.json")
    print(json.dumps({"generator": key, "normalisation": normalisation,
                      "integrated_sigma_cm2": meta["integrated_sigma_cm2"],
                      "cross_check": cross, "identity": ident,
                      "sampling": [{k: s[k] for k in ("population", "pass")} |
                                   {"across_p": s["across_bins_content_proportional"]["p"],
                                    "within_p": s["within_bin_uniform_x_sigma"]["p"],
                                    "alt_chi2": s["across_bins_alternative_density_x_width"]["chi2"]}
                                   for s in samp]}, indent=1))


def build_genie(g5, gen, ev, r, A, B, dV5):
    """genie_cv: A*(S/B)/dV (gen_to_xsec5d.build order); genie_mec: S*(A/B)/dV.
    With r == 1 and the old (A, B) this is the pre-fix arithmetic statement for statement."""
    AX, E5 = g5.AXES, g5.EDGES
    cols = [ev[a] for a in AX]
    e5 = [E5[a] for a in AX]
    S = g5.hist(cols, r, e5)
    S2 = g5.hist(cols, r * r, e5)
    pe = A / B
    x5 = A * (S / B) / dV5 if gen == "genie_cv" else S * pe / dV5
    v5 = S2 * (pe ** 2) / dV5 ** 2
    return x5, v5


def build_weighted_nuwro(g5, ev, r, div, dV5):
    AX, E5 = g5.AXES, g5.EDGES
    cols = [ev[a] for a in AX]
    e5 = [E5[a] for a in AX]
    wr = ev["weight_raw"] * r
    sc = ev["scale"]
    x5 = g5.hist(cols, wr, e5) / div / dV5 * sc
    v5 = g5.hist(cols, wr * wr, e5) / div ** 2 / dV5 ** 2 * sc ** 2
    return x5, v5


def range_limitation(sig, edges, phi_t, Phi_t, gen, sigC=None):
    s = sigC if sigC is not None else sig
    I = s.bin_integrals(edges)
    part = phi_t / Phi_t * I
    lo, hi = GEN_RANGE[gen]
    tot = float(part.sum())
    above = float(part[edges[:-1] >= hi - 1e-12].sum())
    below = float(part[edges[1:] <= lo + 1e-12].sum())
    return {"sigma_graph": "C12 tot_cc/12 (NuWro proxy)" if sigC is not None else "(C12+H1) tot_cc/13",
            "graph_last_knot_GeV": s.x_max,
            "note": "sigma above the last graph knot is TGraph::Eval's linear extrapolation",
            "frac_sigma_phi_t_E_above_gen_max": above / tot,
            "frac_sigma_phi_t_E_below_gen_min": below / tot,
            "frac_sigma_phi_t_E_absent": (above + below) / tot,
            "gen_range_GeV": [lo, hi],
            "frac_phi_t_above_gen_max": float(np.sum((phi_t * np.diff(edges))[edges[:-1] >= hi - 1e-12]) / Phi_t),
            "frac_phi_t_below_gen_min": float(np.sum((phi_t * np.diff(edges))[edges[1:] <= lo + 1e-12]) / Phi_t)}


# ---------------------------------------------------------------------------
# check 5: GiBUU flux (report only)
# ---------------------------------------------------------------------------
def cmd_gibuu_flux(args):
    z, phit_meta, phit_path = load_phi_t(args.out_dir)
    edges, phi_t, Phi_t = z["edges"], z["phi_t_density"], float(z["Phi_t"])
    cu = z["phi_unweighted_contents"]
    w = np.diff(edges)
    d = np.loadtxt(args.gibuu_flux, comments="#")
    Eg, fg = d[:, 0], d[:, 1]
    dE = np.diff(Eg)
    step = float(np.median(dE))
    uniform = bool(np.allclose(dE, step))
    glo = Eg - 0.5 * step                       # esample.eneut: bin = [enu - bin/2, enu + bin/2]
    cut = {}
    for line in open(args.gibuu_jobcard):
        s = line.split("!")[0].strip()
        for k in ("Enu_lower_cut", "Enu_upper_cut", "nuExp", "FileNameFlux"):
            if s.startswith(k):
                cut[k] = s.split("=", 1)[1].strip().strip("'")
    up = float(cut.get("Enu_upper_cut", 200.0))
    lo_c = float(cut.get("Enu_lower_cut", 0.0))

    def cum_phi_t(x):
        """int_0^x phi_t dE for the piecewise-constant phi_t."""
        x = np.atleast_1d(x)
        cw = np.concatenate([[0], np.cumsum(phi_t * w)])
        i = np.clip(np.searchsorted(edges, x, side="right") - 1, 0, w.size - 1)
        return cw[i] + phi_t[i] * (np.clip(x, edges[0], edges[-1]) - edges[i])

    def cum_gibuu(x, flux):
        x = np.atleast_1d(x)
        cw = np.concatenate([[0], np.cumsum(flux * step)])
        i = np.clip(np.floor((x - glo[0]) / step).astype(int), 0, flux.size - 1)
        return cw[i] + flux[i] * (np.clip(x, glo[0], glo[-1] + step) - glo[i])

    grid = np.unique(np.concatenate([np.arange(0, 10.0001, 0.5), edges[edges >= 10], [glo[-1] + step]]))
    grid = grid[grid <= min(100.0, glo[-1] + step) + 1e-9]
    Pt = np.diff(cum_phi_t(grid))
    Pg = np.diff(cum_gibuu(grid, fg))
    tot_g = float(cum_gibuu(np.array([glo[-1] + step]), fg)[0])
    tot_t = float(cum_phi_t(np.array([100.0]))[0])
    fgc = np.where((Eg >= lo_c) & (Eg <= up), fg, 0.0)     # esample.read_fluxfile zeroes outside cuts
    rows = []
    for a, b, pt_, pg_ in zip(grid[:-1], grid[1:], Pt, Pg):
        rows.append({"E_lo": float(a), "E_hi": float(b), "frac_phi_t": float(pt_ / tot_t),
                     "frac_gibuu_file": float(pg_ / tot_g),
                     "ratio_gibuu_over_phi_t": float((pg_ / tot_g) / (pt_ / tot_t)) if pt_ > 0 else None})
    # the same ratio to the non-PPFX generation flux
    Pu = np.diff(np.interp(grid, edges, np.concatenate([[0], np.cumsum(cu * w)])))
    Pu_tot = float(np.sum(cu * w))
    bands = [(0, 2), (2, 5), (5, 10), (10, 20), (20, 50), (50, 100)]
    brow = []
    for a, b in bands:
        m = (grid[:-1] >= a) & (grid[1:] <= b)
        brow.append({"E_lo": a, "E_hi": b, "frac_phi_t": float(Pt[m].sum() / tot_t),
                     "frac_gibuu": float(Pg[m].sum() / tot_g),
                     "frac_phi_unweighted": float(Pu[m].sum() / Pu_tot),
                     "gibuu_over_phi_t": float((Pg[m].sum() / tot_g) / (Pt[m].sum() / tot_t)),
                     "gibuu_over_phi_unweighted": float((Pg[m].sum() / tot_g) / (Pu[m].sum() / Pu_tot))})
    m20 = grid[1:] <= up + 1e-9
    ROOT = import_root()
    sig = SigmaCC(ROOT, os.path.join(args.genie_dir, "xsec_graphs.root"), "CH")
    part = phi_t / Phi_t * sig.bin_integrals(edges)
    frac_sig_above_cut = float(part[edges[:-1] >= up - 1e-12].sum() / part.sum())
    enu_max = []
    for fn in sorted(glob.glob(os.path.join(args.genie_dir, "work_gibuu_arr/task*/FinalEvents.dat"))):
        col = np.loadtxt(fn, comments="#", usecols=(14,))
        enu_max.append(float(col.max()))
    out = {
        "schema": "gen5d-fluxfix-gibuu-flux/v1", "created_utc": now(),
        "gibuu_flux_file": file_record(args.gibuu_flux, "GiBUU user flux (nuExp=99)"),
        "jobcard": file_record(args.gibuu_jobcard, "base jobcard (per-task job = &initRandom + this)"),
        "jobcard_settings": cut,
        "gibuu_flux_points": int(Eg.size), "gibuu_flux_E_first_last": [float(Eg[0]), float(Eg[-1])],
        "gibuu_flux_uniform_step_GeV": step if uniform else None,
        "gibuu_sampling": ("esample.read_fluxfile zeroes flux(j) with enu(j) outside "
                           "[Enu_lower_cut, Enu_upper_cut] and normalizes the cumulative sum to 1 "
                           "over what remains; eneut draws a point by content and uniform in "
                           "[enu - step/2, enu + step/2] (equal widths, so content = density)"),
        "frac_phi_t_E_le_cut": float(Pt[m20].sum() / tot_t),
        "frac_sigma_phi_t_E_above_cut_genie_CH_graphs": frac_sig_above_cut,
        "frac_sigma_note": ("int_cut^100 phi_t sigma_CC / int_0^100 phi_t sigma_CC with GENIE (C12+H1) "
                            "tot_cc (linear extrapolation above 50 GeV): the part of sigma_CC a "
                            "GiBUU sample cut at Enu_upper_cut cannot contain (GENIE sigma shape, "
                            "not GiBUU's; before any phase-space cut)"),
        "frac_gibuu_file_E_le_cut": float(Pg[m20].sum() / tot_g),
        "implied_normalisation_factor_to_data_convention": {
            "definition": ("GiBUU's sigma is averaged over its flux renormalized within the cut; the "
                           "data convention divides by the 0-100 GeV integral, so the E<=cut part of "
                           "a GiBUU prediction carries a factor int_0^cut phi / int_0^100 phi"),
            "with_gibuu_file_shape": float(Pg[m20].sum() / tot_g),
            "with_phi_t_shape": float(Pt[m20].sum() / tot_t)},
        "max_Enu_in_FinalEvents_over_tasks": {"n_files": len(enu_max),
                                              "max": max(enu_max) if enu_max else None,
                                              "min_of_task_maxima": min(enu_max) if enu_max else None},
        "bands": brow, "per_bin": rows,
        "code": [self_record()], "environment": environment(), "argv": sys.argv,
    }
    dump_json(out, os.path.join(args.out_dir, "gibuu_flux_check.json"))
    print(json.dumps({k: out[k] for k in ("jobcard_settings", "frac_phi_t_E_le_cut",
                                          "frac_gibuu_file_E_le_cut", "bands",
                                          "max_Enu_in_FinalEvents_over_tasks")}, indent=1))


# ---------------------------------------------------------------------------
# checks 4 and 6: marginals and ratios
# ---------------------------------------------------------------------------
def cmd_marginals(args):
    ROOT = import_root()
    g5 = load_g5(args.gen5d_tree)
    AX, E5 = g5.AXES, g5.EDGES
    vol = g5.widths(*AX)
    shape = tuple(g5.SHAPE)

    def load(p):
        z = np.load(p, allow_pickle=True)
        for a in AX:
            if not np.array_equal(np.asarray(z[f"edges_{a}"], float), E5[a]):
                raise SystemExit(f"edges {a} differ in {p}")
        return np.asarray(z["xsec_flat"], float).reshape(shape), np.asarray(z["sumw2_flat"], float).reshape(shape)

    def axis_int(x, keep):
        return (x * vol).sum(axis=tuple(i for i in range(5) if i not in keep))

    mnv_p = os.path.join(args.gen5d_dir, "mnvtune_v1_xsec5d.npz")
    mnv, _ = load(mnv_p)
    gib_p = os.path.join(args.gen5d_dir, "gibuu_cv_xsec5d.npz")
    gib, _ = load(gib_p)
    inputs = [file_record(mnv_p, "MnvTune v1 truth 5D"), file_record(gib_p, "GiBUU 5D (not rebuilt)")]
    pz_e = E5["pz"]
    ref = (pz_e[:-1] >= 2.0) & (pz_e[1:] <= 5.0)
    mnv_pz = axis_int(mnv, (1,))
    mnv_tot = float(mnv_pz.sum())
    res = {"pz_edges": pz_e.tolist(), "mnvtune_v1": {
        "integrated_sigma_cm2": mnv_tot,
        "frac_pz_ge_6": float(mnv_pz[pz_e[:-1] >= 6].sum() / mnv_tot)}}
    arrays = {"edges_" + a: E5[a] for a in AX}
    committed = {"genie_cv": ("genie_cv_xsec3d.root", "genie_cv_xsec_eavailW.root"),
                 "genie_mec": ("genie_mec_cv_xsec3d.root", "genie_mec_xsec_eavailW.root"),
                 "nuwro_cv": ("nuwro_cv_xsec3d.root", "nuwro_cv_xsec_eavailW.root")}
    dq3W = g5.widths("q3", "W")
    for key in ("genie_cv", "genie_mec", "nuwro_cv", "gibuu_cv"):
        if key == "gibuu_cv":
            before = after = gib
            v_after = None
        else:
            new_p = os.path.join(args.out_dir, f"{key}_xsec5d.npz")
            old_p = os.path.join(args.gen5d_dir, f"{key}_xsec5d.npz")
            after, v_after = load(new_p)
            before, _ = load(old_p)
            inputs += [file_record(new_p, "repaired 5D"), file_record(old_p, "pre-fix 5D")]
        row = {}
        for tag, x in (("before", before), ("after", after)):
            pzm = axis_int(x, (1,))
            with np.errstate(divide="ignore", invalid="ignore"):
                row[f"pz_ratio_to_mnvtune_{tag}"] = (pzm / mnv_pz).tolist()
                row[f"pz_shape_ratio_to_mnvtune_{tag}_norm_pz2to5"] = (
                    (pzm / mnv_pz) / (pzm[ref].sum() / mnv_pz[ref].sum())).tolist()
            row[f"integrated_sigma_{tag}_cm2"] = float(pzm.sum())
            row[f"frac_pz_ge_6_{tag}"] = float(pzm[pz_e[:-1] >= 6].sum() / pzm.sum())
            for i, a in enumerate(AX):
                m = axis_int(x, (i,))
                with np.errstate(divide="ignore", invalid="ignore"):
                    row.setdefault(f"axis_ratio_to_mnvtune_{tag}", {})[a] = (m / axis_int(mnv, (i,))).tolist()
        if v_after is not None:
            vpz = (v_after * vol ** 2).sum(axis=(0, 2, 3, 4))
            pza = axis_int(after, (1,))
            nraw = np.asarray(np.load(new_p, allow_pickle=True)["nevt_flat"]).reshape(shape).sum(axis=(0, 2, 3, 4))
            row["pz_after_stat_rel_err"] = (np.sqrt(vpz) / pza).tolist()
            row["pz_after_effective_N"] = (pza ** 2 / vpz).tolist()
            row["pz_raw_event_count"] = nraw.astype(int).tolist()
        row["integrated_after_over_before"] = row["integrated_sigma_after_cm2"] / row["integrated_sigma_before_cm2"]
        res[key] = row
        if key == "gibuu_cv":
            continue
        # 3D (pt,pz,eavail) and (eavail,W) marginals of the repaired 5D, vs the committed products
        m3 = (after * dq3W[None, None, None]).sum(axis=(3, 4))
        mew = (after * g5.widths("pt", "pz")[:, :, None, None, None]
               * np.diff(E5["q3"])[None, None, None, :, None]).sum(axis=(0, 1, 3))
        v3 = (v_after * (dq3W ** 2)[None, None, None]).sum(axis=(3, 4))
        vew = (v_after * (g5.widths("pt", "pz")[:, :, None, None, None]
                          * np.diff(E5["q3"])[None, None, None, :, None]) ** 2).sum(axis=(0, 1, 3))
        b3 = (before * dq3W[None, None, None]).sum(axis=(3, 4))
        bew = (before * g5.widths("pt", "pz")[:, :, None, None, None]
               * np.diff(E5["q3"])[None, None, None, :, None]).sum(axis=(0, 1, 3))
        f3, few = committed[key]
        ref3 = g5.read_th(os.path.join(args.genie_dir, f3), "hXSec3D")
        refew = g5.read_th(os.path.join(args.genie_dir, few), "hXSec_eavailW")
        inputs += [file_record(os.path.join(args.genie_dir, f3), "committed 3D"),
                   file_record(os.path.join(args.genie_dir, few), "committed (E_avail,W)")]
        conv = 1.0
        if key == "genie_mec":
            meta = json.loads(str(np.load(os.path.join(args.out_dir, f"{key}_xsec5d.npz"),
                                          allow_pickle=True)["meta_json"]))
            conv = meta["normalisation"]["factor_to_eavailW_band_convention"]
        with np.errstate(divide="ignore", invalid="ignore"):
            r3c = np.where(ref3 != 0, m3 / ref3, np.nan)
            rewc = np.where(refew != 0, mew * conv / refew, np.nan)
            r3b = np.where(b3 != 0, m3 / b3, np.nan)
            rewb = np.where(bew != 0, mew / bew, np.nan)
        arrays.update({f"{key}_m3": m3, f"{key}_m3_var": v3, f"{key}_mew": mew, f"{key}_mew_var": vew,
                       f"{key}_committed_3d": ref3, f"{key}_committed_eavailW": refew,
                       f"{key}_ratio_3d_to_committed": r3c, f"{key}_ratio_eavailW_to_committed": rewc,
                       f"{key}_ratio_3d_to_prefix_5d_marginal": r3b,
                       f"{key}_ratio_eavailW_to_prefix_5d_marginal": rewb})
        dV3 = g5.widths("pt", "pz", "eavail")
        dew = g5.widths("eavail", "W")
        res[key]["marginals"] = {
            "eavailW_convention_factor_applied_to_repaired": conv,
            "eavailW_ratio_repaired_to_committed": rewc.tolist(),
            "eavailW_ratio_repaired_to_prefix_5d": rewb.tolist(),
            "eavailW_repaired_stat_rel_err": (np.sqrt(vew) / np.where(mew > 0, mew, np.nan)).tolist(),
            "3d_integrated_repaired_over_committed": float((m3 * dV3).sum() / (ref3 * dV3).sum()),
            "eavailW_integrated_repaired_over_committed": float((mew * conv * dew).sum() / (refew * dew).sum()),
            "3d_ratio_to_committed_quantiles_5_50_95": np.nanpercentile(r3c[np.isfinite(r3c)], [5, 50, 95]).tolist(),
            "3d_committed_is_different_sample": key == "genie_cv",
            "3d_ratio_to_prefix_5d_pz_projection": (
                (m3 * dV3).sum(axis=(0, 2)) / (b3 * dV3).sum(axis=(0, 2))).tolist(),
            "3d_ratio_to_prefix_5d_eavail_projection": (
                (m3 * dV3).sum(axis=(0, 1)) / (b3 * dV3).sum(axis=(0, 1))).tolist(),
        }
    out_npz = os.path.join(args.out_dir, "gen5d_fluxfix_marginals.npz")
    np.savez(out_npz, **arrays)
    res.update({"schema": "gen5d-fluxfix-marginals/v1", "created_utc": now(),
                "npz": out_npz, "npz_sha256": sha256(out_npz), "inputs": inputs,
                "notes": ["(E_avail,W) ratio for genie_mec applies the weighted band-convention factor "
                          "to the repaired marginal (committed file is the band convention, KNOWN_ISSUES 81)",
                          "genie_cv committed 3D is the Stage-A sample (gen5d README deviation 1); its "
                          "ratio mixes the fix with a sample difference; use the pre-fix 5D ratio for "
                          "the fix alone",
                          "gibuu_cv is not rebuilt: before == after"],
                "code": [self_record()], "environment": environment(), "argv": sys.argv})
    dump_json(res, os.path.join(args.out_dir, "gen5d_fluxfix_marginals.json"))
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk.startswith(("pz_ratio", "integrated", "frac"))}
                      for k, v in res.items() if isinstance(v, dict) and k in
                      ("genie_cv", "genie_mec", "nuwro_cv", "gibuu_cv")}, indent=1))


# ---------------------------------------------------------------------------
def cmd_receipt(args):
    O = args.out_dir
    rec = {"schema": "gen5d-fluxfix-receipt/v1", "created_utc": now(),
           "created_by": f"{Path(__file__).resolve()} receipt (machine-generated from the products' meta)",
           "output_dir": os.path.abspath(O), "products": {}}
    code_copy = os.path.join(O, "code", "gen5d_flux_reweight.py")
    rec["code_copy"] = file_record(code_copy, "code that produced every product") if os.path.exists(code_copy) else None
    ph = json.load(open(os.path.join(O, "phi_t.json")))
    rec["phi_t"] = {"json": os.path.join(O, "phi_t.json"), "json_sha256": sha256(os.path.join(O, "phi_t.json")),
                    **{k: ph[k] for k in ("definition", "histogram", "Phi_t_0_100_m2_per_POT",
                                           "Phi_t_pot_weighted_frw_integrals", "hFluxCV_path", "hFluxCV_bin1",
                                           "hFluxCV_values_all_equal", "rel_diff_Phi_t_vs_hFluxCV_max_over_bins",
                                           "rel_diff_Phi_pot_vs_hFluxCV_max_over_bins", "per_playlist",
                                           "distinct_playlist_flux_shapes", "generation_flux",
                                           "shape_ratio_bands", "npz", "npz_sha256")}}
    for key in ("genie_cv", "genie_mec", "nuwro_cv"):
        p = os.path.join(O, f"{key}_xsec5d.npz")
        m = json.loads(str(np.load(p, allow_pickle=True)["meta_json"]))
        samp = [{"population": s["population"], "mode": s["mode"], "n_events": s["n_events"],
                 "n_outside_generation_bins": s["n_outside_generation_bins"],
                 "across": {k: v for k, v in s["across_bins_content_proportional"].items() if k != "pull_per_bin"},
                 "across_alternative": s["across_bins_alternative_density_x_width"],
                 "within": s["within_bin_uniform_x_sigma"], "pass": s["pass"]}
                for s in m["checks"]["sampling_model"]]
        rec["products"][key] = {
            "npz": p, "npz_sha256": sha256(p),
            "meta_json": os.path.splitext(p)[0] + ".meta.json",
            "meta_json_sha256": sha256(os.path.splitext(p)[0] + ".meta.json"),
            "code_sha256": {c["path"]: c["sha256"] for c in m["code"]["files"]},
            "normalisation": m["normalisation"], "range_limitation": m["range_limitation"],
            "sampling_model": samp,
            "identity_r1_old_normalisation": m["checks"]["identity_r1_old_normalisation"],
            "cross_check_normalisation": m["checks"]["cross_check_normalisation"],
            "variance_diagnostic": m["checks"]["variance_diagnostic"],
            "weights": m["weights"], "integrated_sigma_cm2": m["integrated_sigma_cm2"],
            "pre_fix_product": {k: m["pre_fix_product"][k] for k in ("path", "sha256")},
            "inputs": m["inputs"]}
    mj = os.path.join(O, "gen5d_fluxfix_marginals.json")
    mg = json.load(open(mj))
    rec["marginals"] = {"json": mj, "json_sha256": sha256(mj), "npz": mg["npz"],
                        "npz_sha256": sha256(mg["npz"]), "pz_edges": mg["pz_edges"],
                        "mnvtune_v1": mg["mnvtune_v1"], "notes": mg["notes"]}
    for key in ("genie_cv", "genie_mec", "nuwro_cv", "gibuu_cv"):
        rec["marginals"][key] = {k: v for k, v in mg[key].items() if not k.startswith("axis_ratio")}
        rec["marginals"][key]["eavail_ratio_to_mnvtune_before"] = mg[key]["axis_ratio_to_mnvtune_before"]["eavail"]
        rec["marginals"][key]["eavail_ratio_to_mnvtune_after"] = mg[key]["axis_ratio_to_mnvtune_after"]["eavail"]
        rec["marginals"][key]["W_ratio_to_mnvtune_after"] = mg[key]["axis_ratio_to_mnvtune_after"]["W"]
    gj = os.path.join(O, "gibuu_flux_check.json")
    gb = json.load(open(gj))
    rec["gibuu_flux_check"] = {"json": gj, "json_sha256": sha256(gj),
                               **{k: v for k, v in gb.items() if k not in ("per_bin", "code", "environment", "argv")}}
    rec["environment"] = environment()
    rec["argv"] = sys.argv
    dump_json(rec, os.path.join(O, "gen5d-fluxfix.json"))
    print(os.path.join(O, "gen5d-fluxfix.json"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["phi-t", "reweight", "gibuu-flux", "marginals", "receipt"])
    ap.add_argument("--generator", choices=["genie_cv", "genie_mec", "nuwro"])
    ap.add_argument("--parity-n", type=int, default=20000)
    for k, v in DEFAULTS.items():
        ap.add_argument("--" + k.replace("_", "-"), default=v)
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    if args.command == "reweight" and not args.generator:
        ap.error("reweight needs --generator")
    {"phi-t": cmd_phi_t, "reweight": cmd_reweight, "gibuu-flux": cmd_gibuu_flux,
     "marginals": cmd_marginals, "receipt": cmd_receipt}[args.command](args)


if __name__ == "__main__":
    main()
