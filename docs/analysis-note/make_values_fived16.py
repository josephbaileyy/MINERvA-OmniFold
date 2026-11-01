#!/usr/bin/env python3
"""Generate values_fived16.tex: every printed number of the sixteen-cell five-observable result, from committed readouts.

usage: make_values_fived16.py [--check | --self-test]     (run from the repository root or anywhere inside it)

Each readout is pinned by sha256 in READOUTS; a mismatch stops the run. Every number becomes one key of \\fvval{<key>},
formatted at its printed precision here, so no printed number is typed by hand.
The reported covariance is C_total + C_resp + C_PL,5D (DECISION-20261030-joseph-4b-not-now-5b-audit-then-add.md item 2;
PROPOSAL-20261031-5b-with-without.md): READOUTS pins the with-block readouts (fd/with-cpl/, FD-CT-5B-ADDITION-REPORT.md),
and NOPL_READOUTS the committed ones without the block. Every key whose value differs without the block is also written
with the suffix "-nopl", and a key outside the matrix-dependent families that differs stops the run. --check fails unless the committed
values_fived16.tex equals a fresh generation (the build and CI run it, as for records_entry_numbers.tex).
"""
import hashlib
import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

_top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, cwd=Path(__file__).parent)
# outside a git checkout (an exported copy) the repository root is two levels above docs/analysis-note
ROOT = Path(_top.stdout.strip()) if _top.returncode == 0 else Path(__file__).resolve().parents[2]
OUT = Path(__file__).with_name("values_fived16.tex")
FD = "docs/orchestration/state/measurement-paper/5d-community-20261024"
READOUTS = {
    "h2": ("nd-unfolding/pv-ladder/readouts/h2_definition.json", "b6790761"),
    "stage1": ("docs/orchestration/state/s5p/stage1/stage1_inspect.json", "def4c67c"),
    "cmodel": ("nd-unfolding/pv-ladder/readouts/cmodel_5d.json", "3cfdc6a5"),
    "s1": (f"{FD}/s1/readout/s1_assembly.json", "81e5ef3f"),
    "cresp": ("docs/orchestration/state/measurement-scoping/assigned-uncertainties/cresp/cresp.json", "19bb2ee1"),
    "f0": (f"{FD}/fd/readout/fd_f0_readout.json", "6e7d718b"),
    # with the run-period block: the with arm of FD-CT-5B-ADDITION-REPORT.md section 3
    "f0b": (f"{FD}/fd/with-cpl/readout/fd_f0b_readout.json", "5f542830"),
    "g": (f"{FD}/fd/with-cpl/readout/fd_g_readout.json", "b55366b3"),
    "diag": (f"{FD}/fd/with-cpl/readout/fd_g_diag_readout.json", "bfd529ab"),
    "fup": (f"{FD}/fd/with-cpl/readout/fd_g_followup_readout.json", "5c95c6d0"),
    "sens2": (f"{FD}/fd/with-cpl/readout/fd_g_sens2_readout.json", "cff60b63"),
    "dp": (f"{FD}/fd/with-cpl/data-product/fd_data_product_cpl.json", "d6752d2c"),
    "gagg": (f"{FD}/fd/readout/fd_gibuu_enu_aggregate.json", "66dcbd6d"),
    "fboot": (f"{FD}/fd/with-cpl/readout/fd_flux_boot_readout.json", "7d117515"),   # 3D (PR #438), with the block
    "f1": (f"{FD}/fd/with-cpl/readout/fd_f1_readout.json", "5ccc89e5"),              # 1A (PR #446), with the block
    # the two tunes' generation records, for their names; their digests are the F1c pin's f1b3-SHA256SUMS
    "f1meta-g18": (f"{FD}/fd/receipts-f1/run/cluster/f1b3/gen5d/genie_v3_g18_xsec5d.meta.json", "4fe333b8"),
    "f1meta-ar23": (f"{FD}/fd/receipts-f1/run/cluster/f1b3/gen5d/genie_v3_ar23_xsec5d.meta.json", "d7d136e5"),
    # the pion-constant departure of Eq. (1), as full-covariance norms of its first-order shift under each arm's matrix
    # (ASSESSMENT-20261031-eavail-charged-pion-mass-switch-pricing.md section 7.3; JSON despite the suffix)
    "eav": ("docs/orchestration/state/eavail-switch-pricing-20261031/step0/step0_metric.txt", "3e8bd546"),
    # the same switch at prior level on the analysis's seven fine E_avail bins (that record's section 7.2)
    "eav0": ("docs/orchestration/state/eavail-switch-pricing-20261031/step0/step0.json", "c284a6b3"),
    # the stopped 1B coverage test: gate D (FD-1B-STAGE2-REPORT.md section 4.1) and its diagnosis (FD-1B-DIAG-REPORT.md)
    "gated": (f"{FD}/fd/receipts-1b/stage2/run/score/gate-d.json", "e1838c0a"),
    "diag1b": (f"{FD}/fd/receipts-1b/diag/diag.json", "6fd6669e"),
    # why C_model's coverage is not validated (DECISION-20261024-joseph-5d-community-standard-route.md item 3): the binding
    # Stage 0 (5d-design-20261023/STAGE0-REPORT.md) and the reconstruction-information test R10 (measurement-scoping/r10)
    "stage0": ("docs/orchestration/state/measurement-paper/5d-design-20261023/stage0/receipts-A/stage0-binding.json", "df70af43"),
    "r10": ("docs/orchestration/state/measurement-scoping/r10/outputs/r10_results.json", "dafcc55e"),
}
# the committed readouts without the run-period block, for the "-nopl" keys
NOPL_READOUTS = dict(READOUTS, **{
    "f0b": (f"{FD}/fd/readout/fd_f0b_readout.json", "b9db935a"),
    "g": (f"{FD}/fd/readout/fd_g_readout.json", "75a9ddee"),
    "diag": (f"{FD}/fd/readout/fd_g_diag_readout.json", "680dc5ef"),
    "fup": (f"{FD}/fd/readout/fd_g_followup_readout.json", "cd82517a"),
    "sens2": (f"{FD}/fd/readout/fd_g_sens2_readout.json", "0f6568ab"),
    "dp": (f"{FD}/fd/data-product/fd_data_product.json", "b79556f0"),
    "fboot": (f"{FD}/fd/readout/fd_flux_boot_readout.json", "b7b5652c"),
    "f1": (f"{FD}/fd/readout/fd_f1_readout.json", "cbe411a9"),
})
# each arm's names for its reported matrix and for the block the chain adds to C_total
ARMS = {"with": {"dp": "C_total_plus_C_resp_plus_C_PL5D", "rep": "C_total + C_resp + C_PL5D", "x": "C_resp + C_PL5D",
                 "f1sig": "relative_sigma_plus_C_resp + C_PL5D"},
        "without": {"dp": "C_total_plus_C_resp", "rep": "C_total + C_resp", "x": "C_resp",
                    "f1sig": "relative_sigma_plus_C_resp"}}
# the key families whose values depend on the reported matrix; any other key must be equal in the two arms
MATRIX_KEYS = re.compile(r"^(g-|f0b-|f1-|fb-|sens-|diag-|r04-|corr-|eav-|sig(med|min|max)?-(reported|C_PL5D)|trig-)")
# the figures the note and the paper print, copied into figures/: each must equal its committed source (with the block)
# and the digest its sidecar records (FD-G-FIGURES-REPORT.md section 1; FD-CT-5B-ADDITION-REPORT.md section 3)
FIGURES = {"fd_g_fig_ratio.pdf": "b57cbb2c", "fd_g_fig_modes.pdf": "980351ed"}
FIGURE_SRC = "fd/with-cpl/figures"
CELLS = [f"R{i:02d}" for i in range(16)]
BLOCK = {"stat": "statistical", "interaction": "interaction", "flux": "flux", "detector": "detector",
         "lateral": "lateral", "normalization": "normalization", "seed": "training seed", "C_resp": r"$C_{\mathrm{resp}}$",
         "V_g": r"$V_g$", "C_model:genie_mec": r"$C_{\mathrm{model}}$ (GENIE + MEC)",
         "C_model:nuwro": r"$C_{\mathrm{model}}$ (NuWro)", "C_model:gibuu": r"$C_{\mathrm{model}}$ (GiBUU)"}
PRED = {"genie_cv": "gcv", "genie_mec": "gmec", "nuwro": "nuwro", "gibuu": "gibuu", "mnvtune_v1": "tune"}
# each graded fake-data truth's printed name (for the generated list) and the words a sentence uses for it (for the check)
TRUTH_LABEL = {"nominal": ("the simulation prior", "simulation prior"),
               "W1": (r"the NuWro $\Eavail$ shape", r"NuWro $\Eavail$ shape"),
               "W2": (r"the GENIE + MEC $(\Eavail,W)$ shape", r"$(\Eavail,W)$ shape"),
               "W3": (r"the NuWro $(\pT,\pPar,\Eavail)$ shape", r"$(\pT,\pPar,\Eavail)$ shape"),
               "q3": (r"the synthetic $q_3$ tilt", r"$q_3$ tilt"),
               "stage0c_gibuu": (r"the GiBUU $\Eavail$ shape", r"GiBUU $\Eavail$ shape"),
               "closure_nuwro": ("the NuWro closure", "NuWro closure"),
               "A7_mnvtune": (r"the Tune~v1 hybrid truth", r"Tune~v1 hybrid"),
               "A7_genie_cv": ("the GENIE CV hybrid truth", "GENIE CV hybrid"),
               "A7_genie_mec": ("the GENIE + MEC hybrid truth", "GENIE + MEC hybrid"),
               "A7_nuwro": ("the NuWro hybrid truth", "NuWro hybrid"),
               "A7_gibuu": ("the GiBUU hybrid truth", "GiBUU hybrid")}
# Every printed sentence that states which F0b truths are listed, under the reported covariance or without the run-period
# block. A re-pinned readout changes those sets while the hand-typed names stay, so generation and --check fail unless
# each sentence agrees with the pinned F0b readouts' triggers.listed (with the block: READOUTS; without: NOPL_READOUTS):
#   "keys": the truths its \fvval{f0b-<truth>-...} keys name, and the names it types, equal the listed set with the block;
#   "without": it names (types) every truth listed only without the block, and every truth it names or keys is listed
#              without the block;
#   "both": the truths it types (of the family, if given) equal the truths listed with or without the block;
#   "count": exactly `gibuu` GiBUU truths are listed with the block, and every truth in `also`.
# The anchor is the sentence's distinguishing clause; a missing anchor fails, so a moved sentence must be re-declared.
LISTED_CLAIMS = [
    ("paper_body.tex", "the listed truths ($p<", {"kind": "keys"}),
    ("paper_body.tex", "also meets the listing criterion", {"kind": "without"}),
    ("paper_body.tex", "Thus the fake-data bias exceeds the stated thresholds", {"kind": "both"}),
    ("sec_fived16.tex", "truths meet the listing criterion ($p<", {"kind": "keys"}),
    ("sec_fived16.tex", "truths meet it: the GiBUU", {"kind": "without"}),
    ("sec_fived16.tex", "The fake-data bias therefore exceeds the stated thresholds", {"kind": "both"}),
    ("sec_fived16.tex", "so the GiBUU comparison carries that limitation", {"kind": "both", "family": "gibuu"}),
    ("main_paper.tex", "at a GiBUU-like truth and a synthetic momentum-transfer tilt", {"kind": "count", "gibuu": 1, "also": ["q3"]}),
    ("main_note.tex", "At a GiBUU-like truth and a synthetic momentum-transfer tilt", {"kind": "count", "gibuu": 1, "also": ["q3"]}),
]


def load(readouts=None):
    data = {}
    for key, (rel, pin) in (READOUTS if readouts is None else readouts).items():
        raw = (ROOT / rel).read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        if not sha.startswith(pin):
            sys.exit(f"make_values_fived16: {rel} has sha256 {sha[:12]}, pinned {pin}: refusing")
        data[key] = json.loads(raw)
    return data


def pct(x):              # a relative sigma (fraction) as a percent, two decimals
    return f"{100 * x:.2f}"


def p_tex(p):            # a p-value: two significant figures, scientific below 1e-3
    if p == 0:           # underflow: F0's readout records it as below its 1e-30 floor (FD-F0-REPORT section 0)
        return r"<10^{-30}"
    if p >= 1e-3:
        return f"{p:.2g}" if p < 0.1 else f"{p:.2f}"
    m, e = f"{p:.1e}".split("e")
    return rf"{m}\times10^{{{int(e)}}}"


def values(d, arm="with"):
    A = ARMS[arm]
    v = {}
    # the cells: boxes and central values (f in 10^-40 cm^2/nucleon, three significant figures)
    g0 = d["g"]["predictions"][0]
    assert g0["cells"] == CELLS and d["g"]["cells"] == CELLS
    f = dict(zip(CELLS, g0["f"]))
    for p in d["g"]["predictions"]:   # GiBUU carries 8 of the 16 cells: compare by cell name
        assert max(abs(x / f[c] - 1) for c, x in zip(p["cells"], p["f"])) < 1e-12, "f differs across predictions"
    boxes = {f"R{c['id']:02d}": c["box"] for c in d["h2"]["reporting_cells"] if c["reported"]}
    assert sorted(boxes) == CELLS
    for c in CELLS:
        v[f"f-{c}"] = f"{f[c] / 1e-40:#.3g}".rstrip(".")      # three significant figures, trailing zeros kept
        for ax, (lo, hi) in boxes[c].items():
            v[f"box-{c}-{ax}"] = f"{lo:g}--{hi:g}"
    # the data product (FD-G-FIGURES-REPORT.md section 2) carries the same cells, boxes, f and reported sigma
    dp = d["dp"]
    assert [c["cell"] for c in dp["cells"]] == CELLS and dp["correlation_of"] == A["dp"]
    assert all(c["box"] == boxes[c["cell"]] for c in dp["cells"]), "the data product's boxes differ from H2's"
    assert max(abs(x / f[c] - 1) for c, x in zip(CELLS, dp["f"])) < 1e-12, "the data product's f differs"
    crt = d["cresp"]["relative_sigma"]["C_total_resp"]
    crt = [crt[c] for c in CELLS] if isinstance(crt, dict) else crt
    assert max(abs(a / b - 1) for a, b in zip(dp["relative_sigma"]["C_total_plus_C_resp"], crt)) < 1e-10
    for grp, key in (("reported", A["dp"]),) + ((("C_PL5D", "C_PL5D"),) if arm == "with" else ()):
        vals = dp["relative_sigma"][key]                 # the reported matrix's sigma, and the block's alone
        assert len(vals) == 16
        for c, x in zip(CELLS, vals):
            v[f"sig-{grp}-{c}"] = pct(x)
        srt = sorted(vals)
        v[f"sigmed-{grp}"], v[f"sigmin-{grp}"], v[f"sigmax-{grp}"] = pct((srt[7] + srt[8]) / 2), pct(srt[0]), pct(srt[-1])
    if arm == "with":                                     # the block's effect on the reported sigma (proposal section 1)
        wo, wi = dp["relative_sigma"]["C_total_plus_C_resp"], dp["relative_sigma"][A["dp"]]
        sw, so = sorted(wi), sorted(wo)
        v["pl-medrise"] = f"{100 * ((sw[7] + sw[8]) / (so[7] + so[8]) - 1):.1f}"      # of the median, about 7.8 %
        ratio = [b / a for a, b in zip(wo, wi)]
        r = sorted(ratio)
        v["pl-cellrise-med"] = f"{100 * ((r[7] + r[8]) / 2 - 1):.1f}"
        i = max(range(16), key=lambda j: ratio[j])
        v["pl-cellrise-max"], v["pl-cellrise-maxcell"] = f"{100 * (ratio[i] - 1):.1f}", CELLS[i]
        share = sorted(1 - (a / b) ** 2 for a, b in zip(wo, wi))
        v["pl-share-med"], v["pl-share-max"] = f"{100 * (share[7] + share[8]) / 2:.1f}", f"{100 * share[-1]:.1f}"
        # the block's own label, which travels with every use (FD-CT-5B-ADDITION-DECLARATION.md section 2)
        m = re.search(r"68% interval on sigma_true/sigma_hat is \[([\d.]+), ([\d.]+)\]\. Noise-dominated cells: "
                      r"((?:R\d\d(?:, )?)+)\. Rank (\d); undebiased", dp["labels"]["block"])
        assert m and "added after the data were seen" in dp["labels"]["block"], "the block's label changed"
        v["pl-sigratio-lo"], v["pl-sigratio-hi"], v["pl-noise-cells"], v["pl-rank"] = m.groups()
        assert min(range(16), key=lambda j: wi[j]) == CELLS.index("R04"), "R04 is no longer the smallest-sigma cell"
    rho = dp["correlation"]
    assert all(abs(rho[i][j] - rho[j][i]) < 1e-12 for i in range(16) for j in range(16))
    assert all(abs(rho[i][i] - 1) < 1e-12 for i in range(16))
    for i in range(16):                    # the correlation matrix of the reported covariance, two decimals
        for j in range(i):
            x = f"{rho[i][j]:.2f}"
            v[f"corr-{CELLS[i]}-{CELLS[j]}"] = ("$-$" + x[1:]) if x.startswith("-") else x
    # what GiBUU's sample cannot hold: GENIE CV's and NuWro's E_nu > 20 GeV shares, each a lower bound on the
    # full-flux share because both samples stop at 50 GeV (the readout's range label); never a GiBUU number
    ga = d["gagg"]
    assert "lower bound" in ga["labels"]["range"] and "not a GiBUU number" in ga["labels"]["not"]
    pz_edges = sorted({e for c in dp["cells"] for e in c["box"]["pz"]})
    for g in ("genie_cv", "nuwro"):
        gg = ga["generators"][g]
        assert gg["generation_range_gev"][1] == 50.0
        assert gg["pz_4.5_60"]["bands"][0][0] == pz_edges[1] and gg["pz_4.5_60"]["bands"][-1][1] == pz_edges[2]
        v[f"gagg-{g}-hi"] = f"{100 * gg['pz_4.5_60']['share_E_gt_20']:.2f}"
        v[f"gagg-{g}-lo"] = f"{100 * gg['pz_1.5_4.5']['share_E_gt_20']:.2f}"
    v["gagg-ecut"] = f"{ga['e_cut_gev']:g}"
    v["gagg-range-max"] = f"{ga['generators']['genie_cv']['generation_range_gev'][1]:g}"
    v["gagg-pz-lo"] = f"{pz_edges[0]:g}"
    v["f-unit"] = r"10^{-40}"     # f is printed in units of 10^-40 cm^2/nucleon
    # per-cell relative sigma by group, and the medians
    s1, cr = d["s1"]["relative_sigma"], d["cresp"]["relative_sigma"]
    for grp, src in [(k, s1) for k in ("stat", "interaction", "flux", "detector", "lateral", "normalization", "C_e",
                                       "C_model", "C_total")] + [(k, cr) for k in ("C_resp", "C_total_resp")]:
        vals = src[grp]
        vals = [vals[c] for c in CELLS] if isinstance(vals, dict) else vals
        assert len(vals) == 16
        for c, x in zip(CELLS, vals):
            v[f"sig-{grp}-{c}"] = pct(x)
        srt = sorted(vals)
        v[f"sigmed-{grp}"] = pct((srt[7] + srt[8]) / 2)
        v[f"sigmin-{grp}"] = pct(srt[0])
        v[f"sigmax-{grp}"] = pct(srt[-1])
    # the fake-data grades: each graded truth under C_total (F0) and C_total + C_resp (F0b)
    for tag in ("f0", "f0b"):
        n_cells = n_p = n_truth = 0
        for t in d[tag]["truths"]:
            k = f"{tag}-{t['name']}"
            for var in ("in_sample", "model_only"):          # descriptive variants, labelled in the readout
                if var in t:
                    v[f"{k}-{var}-chi2"] = f"{t[var]['chi2']:.2f}"
                    v[f"{k}-{var}-p"] = p_tex(t[var]["p"])
            if not t.get("graded"):                          # row 6: descriptive and ungraded (control 7 failed)
                v[f"{k}-chi2"], v[f"{k}-p"], v[f"{k}-n"] = (f"{t['grade']['chi2']:.2f}", p_tex(t["grade"]["p"]),
                                                            str(t["n_experiments"]))
                continue
            gr = t["grade"]
            n_truth += 1
            n_cells += len(gr["cells_abs_z_gt_2"])
            n_p += bool(gr["p_lt_0.01"])
            v[f"{k}-chi2"] = f"{gr['chi2']:.2f}"
            v[f"{k}-p"] = p_tex(gr["p"])
            v[f"{k}-cells"] = ", ".join(gr["cells_abs_z_gt_2"]) or "---"
            v[f"{k}-zmax"] = f"{max(abs(z) for z in gr['z']):.2f}"
            v[f"{k}-n"] = str(t["n_experiments"])
            v[f"{k}-listed"] = "yes" if t["listed"] else "no"
        v[f"{tag}-ncells"], v[f"{tag}-np"], v[f"{tag}-ntruths"] = str(n_cells), str(n_p), str(n_truth)
    # Stage G: chi2 with ndf, shape-only, p, and the variant without C_resp
    for p in d["g"]["predictions"]:
        k = f"g-{PRED[p['name']]}"
        for part in ("total", "shape_only"):
            q = p[part]
            v[f"{k}-{part}-chi2"] = f"{q['chi2']:.2f}"
            v[f"{k}-{part}-chi2int"] = f"{q['chi2']:.0f}"
            v[f"{k}-{part}-ndf"] = str(q["ndf"])
            v[f"{k}-{part}-p"] = p_tex(q["p"])
        v[f"{k}-nocresp-chi2"] = f"{p['variant']['total']['chi2']:.2f}"
        v[f"{k}-nocresp-chi2int"] = f"{p['variant']['total']['chi2']:.0f}"
        name = p["label"].split(";")[0].split(",")[0]                    # the readout's own name
        v[f"label-{PRED[p['name']]}"] = ("MINERvA Tune~v1" if name == "MINERvA Tune v1" else name.replace(" ", "~", 1))
        v[f"{k}-ncells"] = str(p["n_cells"])
        WORDS = {7: "seven", 8: "eight", 9: "nine", 16: "sixteen"}   # the abstracts print the count in words
        v[f"{k}-ncells-word"] = WORDS[p["n_cells"]]
    # G-SENS: chi2 at each alpha per family, and the sentence's bounds (16-cell predictions only)
    recs = d["sens2"]["sens"]["records"] + d["fup"]["sens"]["records"]
    for r in recs:
        v[f"sens-{r['family']}-{PRED[r['prediction']]}-a{r['alpha']:g}"] = f"{r['chi2']:.2f}"
    def ratios(fam, alpha):
        return [r["chi2"] / r["chi2_at_alpha_0"] for r in recs
                if r["family"] == fam and abs(r["alpha"] - alpha) < 1e-12 and len(r["cells"]) == 16]
    fl = ratios("flux", 0.1)
    other = ratios("detector", 0.1) + ratios("lateral", 0.1)
    assert len(fl) == 4 and len(other) == 8
    v["sens-flux-fall-lo"] = f"{100 * (1 - max(fl)):.0f}"
    v["sens-flux-fall-hi"] = f"{100 * (1 - min(fl)):.0f}"
    v["sens-detlat-fall-max"] = f"{math.ceil(100 * (1 - min(other))):.0f}"
    joint = [r["chi2"] for r in recs if r["family"] == "c_e_systematic" and r["alpha"] == 1.0 and len(r["cells"]) == 16]
    assert len(joint) == 4
    v["sens-joint-chi2-min"] = f"{math.floor(min(joint)):.0f}"
    # C_resp by species, the sigma ratio, and the trace shares
    for sp in ("C_resp_proton", "C_resp_meson", "C_resp_em", "C_resp_other", "C_resp_xtalk"):
        vals = [cr[sp][c] for c in CELLS] if isinstance(cr[sp], dict) else cr[sp]
        for c, x in zip(CELLS, vals):
            v[f"sig-{sp}-{c}"] = pct(x)
        srt = sorted(vals)
        v[f"sigmed-{sp}"] = pct((srt[7] + srt[8]) / 2)
    tot = [cr["C_total"][c] for c in CELLS] if isinstance(cr["C_total"], dict) else cr["C_total"]
    tr = [cr["C_total_resp"][c] for c in CELLS] if isinstance(cr["C_total_resp"], dict) else cr["C_total_resp"]
    rat = sorted(b / a for a, b in zip(tot, tr))
    v["sigratio-med"], v["sigratio-min"], v["sigratio-max"] = (f"{(rat[7] + rat[8]) / 2:.3f}", f"{rat[0]:.3f}",
                                                                f"{rat[-1]:.3f}")
    # declaration (v) at the sixteen-cell chi2 (app_statmethods_nd.tex:12; PROVENANCE-20261031-declaration-v-fd-16-cell-
    # blocks.md section 3): the statistical block's replicas and the flux block's effective number of weighted universes
    meta = d["s1"]["meta"]
    v["s1-stat-replicas"] = str(meta["stat_replicas"])
    v["s1-flux-neff"] = f"{meta['flux_weights']['n_eff']:.0f}"
    for k, x in d["s1"]["trace_share"].items():
        v[f"trace-{k}"] = f"{x:.3f}"
    for k, x in d["cresp"]["trace_share_of_C_total_resp"].items():
        v[f"trace-resp-{k}"] = f"{x:.4f}"
    # the grid: H2's boxes before and after the purity merge
    h2 = d["h2"]
    v["h2-tau"] = f"{h2['tau']:g}"
    v["h2-nmerge"] = str(len(h2["steps"]))
    v["h2-nunreported"] = str(len(h2["unreported_boxes"]))
    v["h2-nboxes"] = str(sum(len(c["h2_cells"]) for c in h2["reporting_cells"]) + len(h2["unreported_boxes"]))
    for ax in ("pt", "pz", "eavail", "q3", "W"):
        edges = sorted({e for c in h2["reporting_cells"] for e in c["box"][ax]})
        v[f"h2-edges-{ax}"] = ", ".join(f"{e:g}" for e in edges)
    v["h2-nsupported"] = str(d["stage1"]["mc"]["H2"]["n_reported"])       # before the merge: the support rule
    # unsupported boxes absorbed into a reporting cell by the merge (box 17 into R09), and the others left unreported
    v["h2-nabsorbed"] = str(int(v["h2-nboxes"]) - int(v["h2-nsupported"]) - int(v["h2-nunreported"]))
    # the printed H2 counts come from the data product's h2 fields (director, 2026-10-27), and must equal the
    # definition's and Stage 1's
    dh = d["dp"]["h2"]
    from_dp = {"h2-nboxes": len(dh["h2_to_reporting_cell"]), "h2-nunreported": len(dh["unreported_boxes"]),
               "h2-nabsorbed": len(dh["absorbed"]),
               "h2-nsupported": len(dh["h2_to_reporting_cell"]) - len(dh["unsupported_stage1"])}
    for k, n in from_dp.items():
        assert v[k] == str(n), f"{k}: the data product gives {n}, the definition and Stage 1 {v[k]}"
        v[k] = str(n)
    assert sum(len(c["h2_boxes"]) for c in d["dp"]["cells"]) == len(dh["in_cells"])
    for ax in ("pt", "pz", "eavail", "q3", "W"):                             # H2 divides each axis at one interior edge
        edges = sorted({e for c in h2["reporting_cells"] for e in c["box"][ax]})
        assert len(edges) == 3
        v[f"h2-mid-{ax}"] = f"{edges[1]:g}"
    assert d["stage1"]["mc"]["H2"]["n_cells"] == int(v["h2-nboxes"])
    # The four low-stability cells, disclosed in the paper's limitations (DECISION-20261024-joseph-h2-16-cell-definition.md
    # item 3; DECISION-20261028-joseph-protections-remade-and-r21.md item 1). A cell's stability is the fraction of the
    # simulated signal events generated in it, and reconstructed, that are reconstructed in it (pv-ladder
    # h2_definition.py, Stats.of). The decided cells must be the four lowest and print the decided 0.16-0.25.
    lowstab = ("R02", "R06", "R10", "R15")
    stab = {f"R{c['id']:02d}": c["stability"] for c in h2["reporting_cells"]}
    assert set(sorted(stab, key=stab.get)[:len(lowstab)]) == set(lowstab), "the decided cells are not the lowest-stability cells"
    v["h2-lowstab-cells"] = ", ".join(lowstab[:-1]) + " and " + lowstab[-1]
    v["h2-lowstab-min"], v["h2-lowstab-max"] = (f"{min(stab[k] for k in lowstab):.2f}", f"{max(stab[k] for k in lowstab):.2f}")
    assert (v["h2-lowstab-min"], v["h2-lowstab-max"]) == ("0.16", "0.25"), "the printed range differs from the decision's"
    # C_model,5D: its vertices' trace shares, and the numbers its labels state (parsed, so a changed label stops here)
    for k, x in d["cmodel"]["trace_share_by_vertex"].items():
        v[f"cmodel-trace-{k}"] = f"{x:.3f}"
    lab = d["cmodel"]["labels"]
    m = re.search(r"applied on p_parallel < (\d+) GeV/c.*At (\d+) <= p_parallel < \d+ GeV/c GiBUU's sample lacks the "
                  r"E_nu > (\d+) GeV part, ([\d.]+)-([\d.]+) %", lab["gibuu"])
    assert m, "cmodel_5d.json's gibuu label changed"
    (v["cmodel-gibuu-pz-max"], v["cmodel-gibuu-pz-lack"], v["cmodel-gibuu-enu"], v["cmodel-gibuu-lack-lo"],
     v["cmodel-gibuu-lack-hi"]) = m.groups()
    m = re.search(r"(\d+)-(\d+) % of the prior weight lies beside a step in r > ([\d.]+)", lab["step_adjacent"])
    assert m, "cmodel_5d.json's step_adjacent label changed"
    v["cmodel-step-lo"], v["cmodel-step-hi"], v["cmodel-step-r"] = m.groups()
    m = re.fullmatch(r"a cell with \|z\| > ([\d.]+), or a truth with P\(chi2_16 > chi2\) < ([\d.]+), against the grade matrix",
                     d["f0b"]["triggers"]["rule"])
    assert m and d["f0"]["triggers"]["rule"] == d["f0b"]["triggers"]["rule"], "the trigger rule changed"
    v["trig-z"], v["trig-p"] = m.groups()
    alphas = d["sens2"]["constants"]["alphas"]
    assert alphas == d["fup"]["constants"]["alphas"] and 0.1 in alphas
    v["sens-alpha-pct"] = f"{100 * 0.1:.0f}"      # the sentence's weakening: alpha = 0.1 of the declared grid
    for a in alphas:
        v["sens-alpha-" + f"{a:g}".replace(".", "p")] = f"{a:g}"
    fr = d["diag"]["constants"]["fractions"]
    assert len(fr) == 3
    v["diag-fractions"] = "/".join(f"{100 * x:g}" for x in fr)
    # the fake-data controls and the trigger counts by group, with their Gaussian references
    for tag in ("f0", "f0b"):
        ctl = d[tag]["controls"]
        v[f"{tag}-controls-passed"] = ", ".join(str(i) for i in ctl["passed"])
        v[f"{tag}-control7-chi2"] = f"{ctl['offset_control_7']['chi2']:.2f}"
        for grp, gt in d[tag]["triggers"]["by_group"].items():
            k = f"{tag}-grp-{grp}"
            v[f"{k}-truths"], v[f"{k}-cells"] = str(gt["truths"]), str(gt["cells"])
            v[f"{k}-zcells"], v[f"{k}-ptruths"] = str(gt["cells_abs_z_gt_2"]), str(gt["truths_p_lt_0.01"])
            v[f"{k}-refcells"], v[f"{k}-reftruths"] = (f"{gt['gaussian_reference_cells']:.2f}",
                                                       f"{gt['gaussian_reference_truths']:.2f}")
        ag = d[tag]["triggers"]["all_graded"]    # denominators only: the counts are read by group, never pooled
        v[f"{tag}-all-truths"], v[f"{tag}-all-cells"] = str(ag["truths"]), str(ag["cells"])
        v[f"{tag}-nlisted"] = str(len(d[tag]["triggers"]["listed"]))
        names = [TRUTH_LABEL[x["truth"]][0] for x in d[tag]["triggers"]["listed"]]
        v[f"{tag}-listed-names"] = (", ".join(names[:-1]) + " and " + names[-1]) if len(names) > 1 else "".join(names) or "none"
        v[f"{tag}-nunlisted"] = str(ag["truths"] - len(d[tag]["triggers"]["listed"]))
        v[f"{tag}-nungraded"] = str(sum(1 for t in d[tag]["truths"] if not t.get("graded")))
    # Stage G per cell: pulls and g/f - 1 (percent)
    for p in d["g"]["predictions"]:
        for c, z, r in zip(p["cells"], p["pulls"], p["g_over_f_minus_1"]):
            v[f"g-{PRED[p['name']]}-pull-{c}"] = f"{z:.2f}"
            v[f"g-{PRED[p['name']]}-gf-{c}"] = f"{100 * r:.1f}"
    # G-DIAG: per prediction and comparison, the modes carrying 50/90/99 % and the top mode
    for p in d["diag"]["predictions"]:
        for cmpn in p["comparisons"]:
            k = f"diag-{PRED[p['name']]}-{cmpn['comparison']}"
            rel = cmpn["relative_to_f"]
            for q, n in rel["modes_needed"].items():
                v[f"{k}-modes{q.rstrip('%')}"] = str(n)
            top = rel["top_modes"][0]
            v[f"{k}-top-share"] = f"{100 * top['fraction']:.1f}"
            v[f"{k}-top-sigma"] = f"{100 * top['sigma']:.2f}"
            v[f"{k}-top-block"] = BLOCK[top["dominant"]]
    # the R04 look
    r04 = d["fup"]["r04"]
    rs = r04["item2_relative_sigma"]["R04"]
    v["r04-sigma-flux"] = pct(rs["flux"])
    corr = list(r04["item3_correlation_with_R04"]["under"][A["rep"]].values())
    v["r04-ncorr"] = str(len(corr))
    v["r04-corr-min"], v["r04-corr-max"] = f"{min(corr):.2f}", f"{max(corr):.2f}"     # under C_total + C_resp
    cf = list(r04["item3_correlation_with_R04"]["under"]["flux"].values())            # under the flux block alone
    v["r04-corrflux-min"], v["r04-corrflux-max"] = f"{min(cf):.3f}", f"{max(cf):.3f}"
    v["r04-sigma-total"] = pct(rs[A["rep"]])
    assert min(range(16), key=lambda i: tr[i]) == CELLS.index("R04"), "R04 is no longer the smallest-sigma cell"
    assert v["gagg-ecut"] == v["cmodel-gibuu-enu"], "the aggregate's E_nu cut is not GiBUU's sample limit"
    # the abstracts' range: the three EXTERNAL predictions compared on all 16 cells. MINERvA Tune v1 is the unfolding's
    # own prior ("prior (not an independent prediction)", Stage G) and is not in the range; GiBUU, on 8 cells, is printed
    # on its own (director, 2026-10-27)
    ext = [k for k in ("gcv", "gmec", "nuwro") if v[f"g-{k}-total-ndf"] == "16"]
    assert len(ext) == 3 and v["g-gibuu-total-ndf"] == "8" and "tune" not in ext
    v["g-ext-chi2int-min16"] = str(min(int(v[f"g-{k}-total-chi2int"]) for k in ext))
    v["g-ext-chi2int-max16"] = str(max(int(v[f"g-{k}-total-chi2int"]) for k in ext))
    # 3D, the flux-correlation bootstrap (FD-FLUX-BOOT-REPORT.md; DECISION-20261027 limitation plan item 3). Under
    # FD-FLUX-BOOT-BINDING ruling 2 only the correlation variant's 16-84% percentile band of the total chi2 may be
    # described, beside Stage G's chi2 and the offset (median - chi2), as estimation scatter given these universes under
    # PPFX and the nu-e + IMD constraint: never as an interval for the true chi2, never the basic band. The summary keys
    # range over the four 16-cell predictions, as sens-flux-fall-lo/hi do; edges are floored/ceiled to bound the values.
    fb = d["fboot"]
    assert fb["schema"] == "fd-flux-boot-readout/1"
    band = fb["bands"]["correlation"]
    edge, off = [], []
    for name, k in PRED.items():
        b = band[name]; t = b["total"]; hat = b["chi2_stage_g"]
        assert abs(hat - float(v[f"g-{k}-total-chi2"])) < 0.005, f"3D's chi2 for {name} is not Stage G's"
        lo, hi = t["percentiles"]["16"], t["percentiles"]["84"]
        assert lo < hat < hi
        v[f"fb-{k}-lo"], v[f"fb-{k}-hi"] = f"{lo:.0f}", f"{hi:.0f}"
        v[f"fb-{k}-offset"] = f"{t['offset_median_minus_centre']:.2f}"
        if b["ndf"] == 16:
            edge.append(max(hat - lo, hi - hat) / hat)
            off.append(t["offset_median_minus_centre"] / hat)
    assert len(edge) == 4 and min(off) > 0, "expected the four 16-cell predictions, each with a positive offset"
    v["fb-edge-min"] = f"{math.floor(1000 * min(edge)) / 10:.1f}"
    v["fb-edge-max"] = f"{math.ceil(1000 * max(edge)) / 10:.1f}"
    v["fb-offset-relmax"] = f"{math.ceil(1000 * max(off)) / 10:.1f}"
    v["fb-replicates"] = str(fb["constants"]["replicates"])
    v["fb-universes"] = str(fb["constants"]["universes"])
    pcts = fb["constants"]["percentiles"]
    assert 16 in pcts and 84 in pcts, "the 16-84% band is not in the readout's percentiles"
    v["fb-plo"], v["fb-phi"] = "16", "84"                  # the band ruling 2 allows (FD-FLUX-BOOT-BINDING.md section 2)
    # 1A, the GENIE v3 held-out bias test (FD-F1-REPORT.md; DECISION-20261027 limitation plan item 1): "a bias test at
    # two held-out GENIE v3 truths, not a coverage test" (the readout's labels.f1). Per tune, the ensemble (row 7) and the
    # noise-free closure (row 8) are graded against the full C_total + C_resp; the leave-out-GENIE+MEC and model-only
    # grades are descriptive (FD-F1-BINDING.md ruling 2). The held-out group is never pooled with the F0b groups.
    f1 = d["f1"]
    assert f1["schema"] == "fd-f1-readout/1" and "not a coverage test" in f1["labels"]["f1"]
    assert f1["triggers"]["rule"] == d["f0b"]["triggers"]["rule"], "F1's trigger rule is not F0b's"
    f0b_truths = {t["name"]: t for t in d["f0b"]["truths"]}
    rest = {t["name"]: t for t in f1["truths"] if t["group"] != "held-out"}
    assert 9 in f1["controls"]["passed"] and rest == f0b_truths, "control 9: F1 does not re-grade F0b's truths as recorded"
    held = {t["name"]: t for t in f1["truths"] if t["group"] == "held-out"}
    sig = f1[A["f1sig"]]["C_total"]          # the per-cell relative sigma of the reported matrix
    zmax, bsig, mo = [], [], []
    for tune in ("g18", "ar23"):
        v[f"f1-tune-{tune}"] = d[f"f1meta-{tune}"]["generator"].removeprefix("genie_v3_").replace("_", r"\_")
        for rec, k in ((f"F1_genie_v3_{tune}", f"f1-{tune}"), (f"F1_closure_genie_v3_{tune}", f"f1-closure-{tune}")):
            t = held.pop(rec)
            assert t["graded"] and t["own_vertex"] is None and t["grade_matrix"] == A["rep"]
            gr, se, md = t["grade"], t["sensitivity"], t["model_only"]
            assert gr["cells"] == CELLS and se["matrix"] == "C_total minus genie_mec + " + A["x"]
            assert not t["listed"] and not gr["cells_abs_z_gt_2"] and not gr["p_lt_0.01"], f"{rec} is listed"
            v[f"{k}-chi2"], v[f"{k}-p"] = f"{gr['chi2']:.2f}", p_tex(gr["p"])
            i = max(range(16), key=lambda j: abs(gr["z"][j]))
            v[f"{k}-zmax"], v[f"{k}-zcell"] = f"{abs(gr['z'][i]):.2f}", CELLS[i]
            v[f"{k}-sens-chi2"], v[f"{k}-sens-p"] = f"{se['chi2']:.2f}", p_tex(se["p"])
            v[f"{k}-mo-chi2"] = f"{md['chi2']:.2f}"
            v[f"{k}-mo-cells"] = ", ".join(md["cells_abs_z_gt_2"]) or "---"
            v[f"{k}-n"] = str(t["n_experiments"])
            zmax.append(max(abs(z) for z in gr["z"]))
            bsig.append(max(abs(b) / s for b, s in zip(t["bias"], sig)))
            assert bsig[-1] < 1, f"{rec}: a cell's bias is not below its reported sigma"
            v[f"{k}-bsig"] = f"{math.ceil(100 * bsig[-1]) / 100:.2f}"   # per record, ceiled: the ledger probes all four
            mo.append(md["chi2"])
    assert not held, f"unexpected held-out records: {sorted(held)}"
    assert v["f1-g18-n"] == v["f1-ar23-n"] and v["f1-closure-g18-n"] == v["f1-closure-ar23-n"] == "1"
    v["f1-n"] = v["f1-g18-n"]
    # the note prints the model-only cells once, for AR23's "both its records", and none at G18 (review of 589f0780, SF2)
    assert v["f1-ar23-mo-cells"] == v["f1-closure-ar23-mo-cells"] != "---", "AR23's two records differ in model-only cells"
    assert v["f1-g18-mo-cells"] == v["f1-closure-g18-mo-cells"] == "---", "a G18 record has a model-only cell beyond 2 sigma"
    # "below the reported uncertainty in every cell": |b| / sigma, sigma from C_total + C_resp alone, under one in all
    # four records; z's denominator also carries the noise of the mean, so |b| / sigma >= |z|. Ceiled to bound them.
    assert max(bsig) < 1 and max(bsig) >= max(zmax)
    v["f1-zmax-ceil"] = f"{math.ceil(100 * max(zmax)) / 100:.2f}"
    v["f1-bsig-ceil"] = f"{math.ceil(100 * max(bsig)) / 100:.2f}"
    v["f1-mo-chi2-min"], v["f1-mo-chi2-max"] = f"{math.floor(min(mo))}", f"{math.ceil(max(mo))}"
    gt = f1["triggers"]["by_group"]["held-out"]
    v["f1-grp-truths"], v["f1-grp-cells"] = str(gt["truths"]), str(gt["cells"])
    v["f1-grp-zcells"], v["f1-grp-ptruths"] = str(gt["cells_abs_z_gt_2"]), str(gt["truths_p_lt_0.01"])
    v["f1-grp-refcells"] = f"{gt['gaussian_reference_cells']:.2f}"
    v["f1-grp-reftruths"] = f"{gt['gaussian_reference_truths']:.2f}"
    # the held-out group stays out of all_graded, so F0b's pooled denominators are unchanged
    assert gt["truths"] == 4 and f1["triggers"]["all_graded"] == d["f0b"]["triggers"]["all_graded"]
    # Eq. (1)'s pion constant against the charged-pion mass, first order in the unfolding, under this arm's matrix:
    # "at most" the largest |shift| / sigma over the cells (ceiled), and the shift's full-covariance norm
    em = d["eav"]["first_order_unfolded"][ARMS[arm]["dp"]]
    v["eav-cellmax"] = f"{math.ceil(100 * em['max_abs_over_sigma']) / 100:.2f}"
    v["eav-coherent"] = f"{em['norm_sqrt_dCinvd']:.2f}"
    # at prior level, on the completeness denominator (control C1: bitwise the 135 denom_nd): the weight share that
    # changes fine E_avail bin, and "no bin by more than" the largest |relative change| of the seven (ceiled)
    td = d["eav0"]["truth_denom"]
    assert d["eav0"]["control_C1"]["bitwise_equal"] and len(td["ebins_all_rel_change"]) == 7
    v["eavbin-share"] = f"{100 * td['weight_share_changing_fine_eavail_bin']:.2f}"
    v["eavbin-max"] = f"{math.ceil(10000 * max(abs(x) for x in td['ebins_all_rel_change'])) / 100:.2f}"
    # the stopped 1B test: the sentence says gate D failed, the diagnosis localized nothing within its K_MAX bands, and
    # the count of cells whose sigma ratio lies outside the window; each is asserted so a changed readout stops the run
    gd, dg = d["gated"], d["diag1b"]
    lo, hi = gd["window"]
    assert gd["verdict"] == "FAIL" and dg["verdict"] == "NOT LOCALIZED" and dg["L1_named_bands"]["n_sets"] == 0
    assert dg["rho"] == gd["rho"] and dg["window"] == gd["window"] and len(gd["rho"]) == 16
    v["cov1b-ncells-out"] = str(sum(not lo <= r <= hi for r in gd["rho"]))
    v["cov1b-win-lo"], v["cov1b-win-hi"] = f"{lo:.1f}", f"{hi:.1f}"
    v["cov1b-rho-min"], v["cov1b-rho-max"] = f"{min(gd['rho']):.2f}", f"{max(gd['rho']):.2f}"
    v["cov1b-kmax-word"] = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}[dg["k_max"]]
    v["cov1b-nbands"] = str(len(dg["per_band"]))
    # Stage 0 stopped: both definitions fail 0a and pass 0b. The note names the families below the per-family bar and
    # says whether each pooled value meets its bar, so both are asserted here
    s0 = d["stage0"]
    rl, rs = s0["rules"], s0["results"]
    assert s0["mode"] == "binding" and s0["verdict"] == "STOP" and rl["form"] == "M2"
    assert all(not rs[k]["0a"]["pass"] and rs[k]["0b"]["pass"] for k in ("J", "H2"))
    v["s0-cfam-min"], v["s0-pooled-min"] = f"{rl['c_family_min']:.2f}", f"{rl['pooled_min']:.2f}"
    low = {"J": ("NuWro", "GiBUU"), "H2": ("GiBUU",)}
    for k, fams in low.items():
        c = {f: x["c_M2"] for f, x in rs[k]["0a"]["families"].items()}
        assert {f for f in c if c[f] < rl["c_family_min"]} == set(fams), f"Stage 0 {k}: the families below the bar changed"
        for f in fams:
            v[f"s0-{k.lower()}-{f.lower()}"] = f"{c[f]:.3f}"
        v[f"s0-{k.lower()}-pooled"] = f"{rs[k]['0a']['pooled_M2']:.3f}"
    assert rs["J"]["0a"]["pooled_M2"] < rl["pooled_min"] <= rs["H2"]["0a"]["pooled_M2"], "the pooled clauses changed"
    # R10 ended INCOMPLETE: no configuration passed, and none met the residual leg at any departure
    rv = d["r10"]["verdict"]
    assert rv["verdict"] == "INCOMPLETE" and rv["passing"] == [] and rv["n_decisive"] == len(rv["per_config"])
    assert all(x["leg_b_departures"] == 0 for x in rv["per_config"].values())
    v["r10-nconfig"] = str(rv["n_decisive"])
    return v


def all_values(d=None, d_nopl=None):
    """The with-block values, and each matrix-dependent value without the block under the suffix "-nopl"."""
    v = values(load() if d is None else d, "with")
    w = values(load(NOPL_READOUTS) if d_nopl is None else d_nopl, "without")
    assert set(w) <= set(v), f"keys only without the block: {sorted(set(w) - set(v))[:5]}"
    moved = sorted(k for k in w if w[k] != v[k])
    stray = [k for k in moved if not MATRIX_KEYS.match(k)]
    assert not stray, f"values outside the matrix-dependent families differ without the block: {stray[:8]}"
    # every matrix-dependent key, moved or not, so a table printing both arms never lacks a key
    v.update({f"{k}-nopl": w[k] for k in w if MATRIX_KEYS.match(k)})
    for part in ("total", "shape_only"):              # ndf is printed once per block of Table IV and Table 16
        ndf16 = {v[f"g-{k}-{part}-ndf"] for k in PRED.values() if k != "gibuu"}
        assert len(ndf16) == 1, f"the 16-cell predictions' {part} ndf differ: {ndf16}"
    # the total and shape-only chi2 falls with the block, over the five predictions (the referee's corrections, #610)
    gw = {p["name"]: p for p in (load() if d is None else d)["g"]["predictions"]}
    go = {p["name"]: p for p in (load(NOPL_READOUTS) if d_nopl is None else d_nopl)["g"]["predictions"]}
    for part in ("total", "shape_only"):
        fall = [1 - gw[n][part]["chi2"] / go[n][part]["chi2"] for n in PRED]
        assert min(fall) > 0, f"a {part} chi2 rises with the block"
        v[f"pl-chi2fall-{part}-lo"], v[f"pl-chi2fall-{part}-hi"] = f"{100 * min(fall):.1f}", f"{100 * max(fall):.1f}"
    return v


def render(v):
    lines = ["% Generated by make_values_fived16.py from the committed readouts it pins by sha256. Do not edit.",
             "% Regenerate: python3 docs/analysis-note/make_values_fived16.py",
             "% \\fvval{key} prints a value and stops the build on an unknown key. \\fvpending{what} marks an input that has",
             "% not landed; it prints [PENDING: what], which build_all.sh refuses (the PDF text check), so it never ships.",
             r"\makeatletter",
             r"\providecommand{\fvval}[1]{\@ifundefined{fv@#1}{\errmessage{values_fived16: no value '#1'}}{\@nameuse{fv@#1}}}",
             r"\providecommand{\fvpending}[1]{\textbf{[PENDING: #1]}}"]
    for k in sorted(v):
        lines.append(rf"\@namedef{{fv@{k}}}{{{v[k]}}}")
    lines.append(r"\makeatother")
    return "\n".join(lines) + "\n"


def check_figures():
    """The figures the note and the paper print equal their committed sources and the sidecars' digests."""
    bad = []
    for name, pin in FIGURES.items():
        got = OUT.parent / "figures" / name
        src = ROOT / FD / FIGURE_SRC / name
        side = json.loads(src.with_suffix(".json").read_text())["pdf_sha256"]
        h = [hashlib.sha256(x.read_bytes()).hexdigest() if x.exists() else "missing" for x in (got, src)]
        if not (h[0] == h[1] == side and side.startswith(pin)):
            bad.append(f"{name}: installed {h[0][:12]}, source {h[1][:12]}, sidecar {side[:12]}, pinned {pin}")
    return bad


def _sentence(text, anchor):
    """The sentence of `text` that contains `anchor` (sentences end at a full stop followed by a space and a capital)."""
    i = text.index(anchor)
    # a full stop before the anchor ends the previous sentence; the lookahead reads the whole text, so an anchor that
    # opens its sentence is found (a search of text[:i] cannot see the capital at i)
    start = max([m.end() for m in re.finditer(r"\.\s+(?=[A-Z\\])", text) if m.end() <= i] + [text.rfind("\n", 0, i) + 1])
    m = re.search(r"\.(\s+(?=[A-Z\\])|\s*$)", text[i:], re.M)
    return text[start:i + (m.start() + 1 if m else len(text) - i)]


def check_listed_claims(f0b, texts, f0b_nopl=None):
    """Each LISTED_CLAIMS sentence agrees with these F0b readouts' listed truths; returns the failures."""
    f0b_nopl = load(NOPL_READOUTS)["f0b"] if f0b_nopl is None else f0b_nopl
    listed = {x["truth"] for x in f0b["triggers"]["listed"]}
    without = {x["truth"] for x in f0b_nopl["triggers"]["listed"]}
    graded = {t["name"] for t in f0b["truths"] if t.get("graded")}
    bad = []
    for name, anchor, rule in LISTED_CLAIMS:
        text = texts[name]
        if text.count(anchor) != 1:
            bad.append(f"{name}: {anchor!r} occurs {text.count(anchor)} times, not once; re-declare the sentence")
            continue
        sent = _sentence(text, anchor)
        keyed = set(re.findall(r"\\fvval\{f0b-([A-Za-z0-9_]+)-(?:zmax|p|cells|chi2)\}", sent))
        keyed_nopl = set(re.findall(r"\\fvval\{f0b-([A-Za-z0-9_]+)-(?:zmax|p|cells|chi2)-nopl\}", sent))
        typed = {t for t in graded if TRUTH_LABEL[t][1] in sent}
        unknown = (keyed | keyed_nopl) - graded
        if unknown:
            bad.append(f"{name}: {anchor!r} keys truths the readout does not grade: {sorted(unknown)}")
        got = {"keyed": sorted(keyed), "keyed without": sorted(keyed_nopl), "typed": sorted(typed),
               "listed with": sorted(listed), "listed without": sorted(without)}
        kind = rule["kind"]
        if kind == "keys":
            ok = keyed == listed and typed == listed and not keyed_nopl
        elif kind == "without":
            ok = (without - listed) <= typed and (typed | keyed | keyed_nopl) <= without
        elif kind == "both":
            fam = (lambda t: rule["family"] in t.lower()) if "family" in rule else (lambda t: True)
            ok = typed == {t for t in listed | without if fam(t)}
        else:
            ok = sum("gibuu" in t for t in listed) == rule["gibuu"] and all(t in listed for t in rule["also"])
        if not ok:
            bad.append(f"{name}: {anchor!r} ({kind}) disagrees with the pinned F0b readouts: {got}")
    return bad


def read_claim_texts():
    return {name: (OUT.parent / name).read_text() for name in {c[0] for c in LISTED_CLAIMS}}


def check_file(path, text):
    """--check's comparison: the committed file equals a fresh generation."""
    return path.exists() and path.read_text() == text


def self_test():
    """A wrong pin must be refused, and a committed file differing in one value must fail --check."""
    ok = True
    key = next(iter(READOUTS))
    rel, pin = READOUTS[key]
    READOUTS[key] = (rel, "0" * 8)
    try:
        load()
        print("  FAIL a wrong sha256 pin was not refused"); ok = False
    except SystemExit:
        print("  ok   a wrong sha256 pin is refused")
    READOUTS[key] = (rel, pin)
    text = render(all_values())
    stale = text.replace(r"\@namedef{fv@f0b-stage0c_gibuu-zmax}{1.76}", r"\@namedef{fv@f0b-stage0c_gibuu-zmax}{1.8}")
    if stale == text:
        print("  FAIL the plant did not apply (R06's z is not 1.76)"); ok = False
    else:
        with tempfile.TemporaryDirectory() as tmp:          # run --check's own comparison against the stale file
            f = Path(tmp) / OUT.name
            f.write_text(stale)
            if check_file(f, text):
                print("  FAIL --check passed a file with R06's z printed as 1.8"); ok = False
            else:
                print("  ok   --check fails on a file with R06's z printed as 1.8")
            f.write_text(text)
            if not check_file(f, text):
                print("  FAIL --check failed a fresh file"); ok = False
            else:
                print("  ok   --check passes a fresh file")
    d = load()                                               # the data product's H2 counts must agree with H2's
    d["dp"]["h2"]["unreported_boxes"] = d["dp"]["h2"]["unreported_boxes"][:-1]
    try:
        values(d)
        print("  FAIL a data product with one unreported box fewer was accepted"); ok = False
    except AssertionError:
        print("  ok   a data product whose H2 counts differ from the definition's is refused")
    d = load()
    d["dp"]["cells"][3]["box"] = dict(d["dp"]["cells"][3]["box"], W=[0.0, 1.8])
    try:
        values(d)
        print("  FAIL a data product with a changed box was accepted"); ok = False
    except AssertionError:
        print("  ok   a data product whose boxes differ from H2's is refused")
    # 1A: an F1 readout that re-grades an F0b truth differently (control 9), or lists a held-out record, is refused
    for what, plant in (("re-grades an F0b truth differently",
                         lambda d: next(t for t in d["f1"]["truths"] if t["name"] == "A7_gibuu")["grade"].update(chi2=1.0)),
                        ("lists a held-out record",
                         lambda d: next(t for t in d["f1"]["truths"] if t["name"] == "F1_genie_v3_ar23").update(listed=True)),
                        ("gives AR23's closure no model-only cell beyond 2 sigma",
                         lambda d: next(t for t in d["f1"]["truths"] if t["name"] == "F1_closure_genie_v3_ar23")["model_only"]
                         .update(cells_abs_z_gt_2=[])),
                        ("gives a G18 record a model-only cell beyond 2 sigma",
                         lambda d: next(t for t in d["f1"]["truths"] if t["name"] == "F1_genie_v3_g18")["model_only"]
                         .update(cells_abs_z_gt_2=["R00"])),
                        ("has a held-out cell with |b| above its sigma",
                         lambda d: next(t for t in d["f1"]["truths"] if t["name"] == "F1_closure_genie_v3_g18")["bias"]
                         .__setitem__(11, 2 * d["f1"][ARMS["with"]["f1sig"]]["C_total"][11]))):
        d = load()
        plant(d)
        try:
            values(d)
            print(f"  FAIL an F1 readout that {what} was accepted"); ok = False
        except AssertionError:
            print(f"  ok   an F1 readout that {what} is refused")
    d = load()                                               # a fifth cell below the decided four must be refused
    next(c for c in d["h2"]["reporting_cells"] if c["id"] == 11)["stability"] = 0.15
    try:
        values(d)
        print("  FAIL an H2 definition whose four lowest-stability cells differ from the decided ones was accepted"); ok = False
    except AssertionError:
        print("  ok   an H2 definition whose four lowest-stability cells differ from the decided ones is refused")
    # the listed-truth sentences: silent on the committed tree, and each plant must fail at the sentence it changed
    d, dn, texts = load(), load(NOPL_READOUTS), read_claim_texts()
    if check_listed_claims(d["f0b"], texts, dn["f0b"]):
        print("  FAIL the committed listed-truth sentences disagree with the pinned F0b readouts"); ok = False
    else:
        print(f"  ok   the {len(LISTED_CLAIMS)} committed listed-truth sentences agree with the pinned F0b readouts")
    # the world fixture: the two arms' readouts exchanged, as a re-pin to the wrong arm would leave them. The sentences
    # that state the reported list, the without-only addition or the abstracts' single GiBUU truth must fail; the
    # sentences that name the union cannot tell the arms apart and must stay silent
    fails = check_listed_claims(dn["f0b"], texts, d["f0b"])
    swapped = {f"{n}: {a!r}" for n, a, r in LISTED_CLAIMS if any(b.startswith(f"{n}: {a!r}") for b in fails)}
    want = {f"{n}: {a!r}" for n, a, r in LISTED_CLAIMS if r["kind"] != "both"}
    if swapped == want:
        print(f"  ok   the arms' readouts exchanged fail exactly the {len(want)} sentences that tell them apart")
    else:
        print(f"  FAIL the arms' readouts exchanged failed {sorted(swapped)}, not {sorted(want)}"); ok = False
    for what, name, anchor, edit in (
            ("keys a truth the readout does not list", "paper_body.tex", "the listed truths ($p<",
             lambda t: t.replace(r"by $p$ alone ($p=\fvval{f0b-q3-p}$)", r"by $p$ alone ($p=\fvval{f0b-q3-p}$, $\fvval{f0b-W3-p}$)", 1)),
            ("drops a listed truth's keys", "paper_body.tex", "the listed truths ($p<",
             lambda t: t.replace(r"($p=\fvval{f0b-A7_gibuu-p}$; cells \fvval{f0b-A7_gibuu-cells})", "", 1)),
            ("names the wrong truth as listed only without the block", "paper_body.tex", "also meets the listing criterion",
             lambda t: t.replace(r"the GiBUU $\Eavail$ shape also meets", r"the NuWro $\Eavail$ shape also meets", 1)),
            ("drops the truth listed only without the block", "sec_fived16.tex",
             "The fake-data bias therefore exceeds the stated thresholds",
             lambda t: t.replace(r"and also at the GiBUU $\Eavail$ shape without $C_{\mathrm{PL,5D}}$; the bias", "; the bias", 1)),
            ("drops a GiBUU truth of its family", "sec_fived16.tex", "so the GiBUU comparison carries that limitation",
             lambda t: t.replace(r"thresholds at the GiBUU hybrid truth under the reported covariance, and also",
                                 r"thresholds under the reported covariance, and also", 1)),
            ("loses its anchor", "main_paper.tex", "at a GiBUU-like truth and a synthetic momentum-transfer tilt",
             lambda t: t.replace("at a GiBUU-like truth and a synthetic", "at GiBUU-like truths and a synthetic", 1))):
        planted = dict(texts, **{name: edit(texts[name])})
        if planted[name] == texts[name]:
            print(f"  FAIL the plant that {what} did not apply"); ok = False
            continue
        hit = [b for b in check_listed_claims(d["f0b"], planted, dn["f0b"]) if b.startswith(f"{name}: {anchor!r}")]
        if hit:
            print(f"  ok   a {name} sentence that {what} fails")
        else:
            print(f"  FAIL a {name} sentence that {what} passed"); ok = False
    d = load()                                               # a readout listing one more truth fails the "keys" sentences
    d["f0b"]["triggers"]["listed"].append({"truth": "W3", "cells": [], "p_lt_0.01": True})
    if len([b for b in check_listed_claims(d["f0b"], texts, dn["f0b"]) if "(keys)" in b]) == 2:
        print("  ok   a readout that lists one more truth fails both enumerating sentences")
    else:
        print("  FAIL a readout that lists one more truth did not fail both enumerating sentences"); ok = False
    v = all_values()
    if (v["f0b-listed-names"], v["f0b-listed-names-nopl"]) != (r"the synthetic $q_3$ tilt and the GiBUU hybrid truth",
                                                                r"the synthetic $q_3$ tilt, the GiBUU $\Eavail$ shape and the GiBUU hybrid truth"):
        print(f"  FAIL f0b-listed-names are {v['f0b-listed-names']!r} and {v['f0b-listed-names-nopl']!r}"); ok = False
    else:
        print("  ok   f0b-listed-names name the listed truths with and without the block, in the readouts' order")
    dn = load(NOPL_READOUTS)                                 # a value outside the matrix-dependent families must not move
    dn["s1"]["trace_share"] = {k: x * 1.01 for k, x in dn["s1"]["trace_share"].items()}
    try:
        all_values(load(), dn)
        print("  FAIL a without-block value outside the matrix-dependent families that differs was accepted"); ok = False
    except AssertionError:
        print("  ok   a without-block value outside the matrix-dependent families that differs is refused")
    name = next(iter(FIGURES))                               # a figure that is not its source must fail --check
    with tempfile.TemporaryDirectory() as tmp:
        fig = OUT.parent / "figures" / name
        keep = Path(tmp) / name
        keep.write_bytes(fig.read_bytes())
        try:
            fig.write_bytes(keep.read_bytes() + b"%")
            if check_figures():
                print("  ok   an installed figure that differs from its committed source fails --check")
            else:
                print("  FAIL a changed installed figure passed"); ok = False
        finally:
            fig.write_bytes(keep.read_bytes())
    if check_figures():
        print("  FAIL the installed figures do not equal their sources"); ok = False
    print("VALUES-FIVED16 SELF-TEST ::", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv):
    if not (ROOT / "docs/orchestration").is_dir():   # the standalone note repository carries no readouts
        print("VALUES-FIVED16 :: SKIP (no docs/orchestration: the standalone note repository; the canonical build enforces it)")
        return 0
    if argv[:1] == ["--self-test"]:
        return self_test()
    d = load()
    text = render(all_values(d))
    bad = check_listed_claims(d["f0b"], read_claim_texts())
    if bad:
        sys.exit("VALUES-FIVED16 :: FAIL (a sentence's listed fake-data truths disagree with the pinned F0b readout)\n  "
                 + "\n  ".join(bad))
    if argv[:1] == ["--check"]:
        if not check_file(OUT, text):
            sys.exit("VALUES-FIVED16 :: FAIL (values_fived16.tex differs from a fresh generation; regenerate it)")
        bad = check_figures()
        if bad:
            sys.exit("VALUES-FIVED16 :: FAIL (a printed figure differs from its committed source)\n  " + "\n  ".join(bad))
        print(f"VALUES-FIVED16 :: PASS ({sum(1 for l in text.splitlines() if l.startswith(chr(92) + "@namedef"))} values, "
              f"readouts pinned, {len(FIGURES)} figures equal their sources, {len(LISTED_CLAIMS)} listed-truth sentences agree)")
        return 0
    OUT.write_text(text)
    print(f"wrote {OUT.name}: {sum(1 for l in text.splitlines() if l.startswith(chr(92) + "@namedef"))} values")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
