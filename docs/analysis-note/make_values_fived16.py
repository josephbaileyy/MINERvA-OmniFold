#!/usr/bin/env python3
"""Generate values_fived16.tex: every printed number of the sixteen-cell five-observable result, from committed readouts.

usage: make_values_fived16.py [--check | --self-test]     (run from the repository root or anywhere inside it)

Each readout is pinned by sha256 in READOUTS; a mismatch stops the run. Every number becomes one key of \\fvval{<key>},
formatted at its printed precision here, so no printed number is typed by hand. --check fails unless the committed
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
    "f0b": (f"{FD}/fd/readout/fd_f0b_readout.json", "b9db935a"),
    "g": (f"{FD}/fd/readout/fd_g_readout.json", "75a9ddee"),
    "diag": (f"{FD}/fd/readout/fd_g_diag_readout.json", "680dc5ef"),
    "fup": (f"{FD}/fd/readout/fd_g_followup_readout.json", "cd82517a"),
    "sens2": (f"{FD}/fd/readout/fd_g_sens2_readout.json", "0f6568ab"),
    "dp": (f"{FD}/fd/data-product/fd_data_product.json", "b79556f0"),
    "gagg": (f"{FD}/fd/readout/fd_gibuu_enu_aggregate.json", "66dcbd6d"),
    "fboot": (f"{FD}/fd/readout/fd_flux_boot_readout.json", "b7b5652c"),   # 3D, FD-FLUX-BOOT-REPORT.md (PR #438)
}
# the figures the note and the paper print, copied into figures/: each must equal its committed source and the digest
# its sidecar records (FD-G-FIGURES-REPORT.md section 1)
FIGURES = {"fd_g_fig_ratio.pdf": "6372244f", "fd_g_fig_modes.pdf": "5421815f"}
CELLS = [f"R{i:02d}" for i in range(16)]
BLOCK = {"stat": "statistical", "interaction": "interaction", "flux": "flux", "detector": "detector",
         "lateral": "lateral", "normalization": "normalization", "seed": "training seed", "C_resp": r"$C_{\mathrm{resp}}$",
         "V_g": r"$V_g$", "C_model:genie_mec": r"$C_{\mathrm{model}}$ (GENIE + MEC)",
         "C_model:nuwro": r"$C_{\mathrm{model}}$ (NuWro)", "C_model:gibuu": r"$C_{\mathrm{model}}$ (GiBUU)"}
PRED = {"genie_cv": "gcv", "genie_mec": "gmec", "nuwro": "nuwro", "gibuu": "gibuu", "mnvtune_v1": "tune"}


def load():
    data = {}
    for key, (rel, pin) in READOUTS.items():
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


def values(d):
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
    assert [c["cell"] for c in dp["cells"]] == CELLS and dp["correlation_of"] == "C_total_plus_C_resp"
    assert all(c["box"] == boxes[c["cell"]] for c in dp["cells"]), "the data product's boxes differ from H2's"
    assert max(abs(x / f[c] - 1) for c, x in zip(CELLS, dp["f"])) < 1e-12, "the data product's f differs"
    crt = d["cresp"]["relative_sigma"]["C_total_resp"]
    crt = [crt[c] for c in CELLS] if isinstance(crt, dict) else crt
    assert max(abs(a / b - 1) for a, b in zip(dp["relative_sigma"]["C_total_plus_C_resp"], crt)) < 1e-10
    rho = dp["correlation"]
    assert all(abs(rho[i][j] - rho[j][i]) < 1e-12 for i in range(16) for j in range(16))
    assert all(abs(rho[i][i] - 1) < 1e-12 for i in range(16))
    for i in range(16):                    # the correlation matrix of C_total + C_resp, two decimals
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
    corr = list(r04["item3_correlation_with_R04"]["under"]["C_total + C_resp"].values())
    v["r04-ncorr"] = str(len(corr))
    v["r04-corr-min"], v["r04-corr-max"] = f"{min(corr):.2f}", f"{max(corr):.2f}"     # under C_total + C_resp
    cf = list(r04["item3_correlation_with_R04"]["under"]["flux"].values())            # under the flux block alone
    v["r04-corrflux-min"], v["r04-corrflux-max"] = f"{min(cf):.3f}", f"{max(cf):.3f}"
    v["r04-sigma-total"] = pct(rs["C_total + C_resp"])
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
        src = ROOT / FD / "fd/figures" / name
        side = json.loads(src.with_suffix(".json").read_text())["pdf_sha256"]
        h = [hashlib.sha256(x.read_bytes()).hexdigest() if x.exists() else "missing" for x in (got, src)]
        if not (h[0] == h[1] == side and side.startswith(pin)):
            bad.append(f"{name}: installed {h[0][:12]}, source {h[1][:12]}, sidecar {side[:12]}, pinned {pin}")
    return bad


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
    text = render(values(load()))
    stale = text.replace(r"\@namedef{fv@f0b-stage0c_gibuu-zmax}{2.01}", r"\@namedef{fv@f0b-stage0c_gibuu-zmax}{2.0}")
    if stale == text:
        print("  FAIL the plant did not apply (R06's z is not 2.01)"); ok = False
    else:
        with tempfile.TemporaryDirectory() as tmp:          # run --check's own comparison against the stale file
            f = Path(tmp) / OUT.name
            f.write_text(stale)
            if check_file(f, text):
                print("  FAIL --check passed a file with R06's z printed as 2.0"); ok = False
            else:
                print("  ok   --check fails on a file with R06's z printed as 2.0")
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
    text = render(values(load()))
    if argv[:1] == ["--check"]:
        if not check_file(OUT, text):
            sys.exit("VALUES-FIVED16 :: FAIL (values_fived16.tex differs from a fresh generation; regenerate it)")
        bad = check_figures()
        if bad:
            sys.exit("VALUES-FIVED16 :: FAIL (a printed figure differs from its committed source)\n  " + "\n  ".join(bad))
        print(f"VALUES-FIVED16 :: PASS ({sum(1 for l in text.splitlines() if l.startswith(chr(92) + "@namedef"))} values, "
              f"readouts pinned, {len(FIGURES)} figures equal their sources)")
        return 0
    OUT.write_text(text)
    print(f"wrote {OUT.name}: {sum(1 for l in text.splitlines() if l.startswith(chr(92) + "@namedef"))} values")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
