#!/usr/bin/env python3
"""Build the methods paper's reproducible result package from committed records only.

usage (from anywhere inside a git checkout of the repository):
    python3 build_package.py              write package/, README.txt and SHA256SUMS next to this script
    python3 build_package.py --check      rebuild in a temporary directory; fail unless every file equals the committed one
    python3 build_package.py --self-test  plant a wrong value in each check family and confirm that the build refuses it

What it does, in order (any failure exits 1 and names the value):
  1. Reads each source record and refuses it unless its sha256 equals the pin in SOURCES.
  2. Imports docs/analysis-note/make_values_fived16.py, the paper's own values producer, and runs its all_values().
     That re-verifies the producer's own readout pins. It then requires values_fived16.tex to equal that fresh
     generation, so the package is checked against the values the paper prints, not against a copy.
  3. Writes each package file from the records, at full precision, and checks every value in it against its
     \\fvval key (values_fived16.tex), its values.tex macro or, for a value with no key, the paper's printed text at
     PAPER_REF, formatted the producer's way.
  4. Requires each file's LaTeX \\label to exist in the paper at PAPER_REF, and each quoted licence line to occur
     verbatim in the record it is quoted from.
  5. Writes a placeholder for every input that has not landed. While any placeholder is pending, the README and
     the last line of output say INCOMPLETE.

It contacts no cluster, reads no file outside the repository, and recomputes no result: it copies, subsets and
formats committed values, and computes only what the producer computes from them (ratios, differences, counts).
Python 3 standard library only.
"""
import csv
import hashlib
import importlib.util
import io
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True   # importing the producer must leave no __pycache__ in the checkout
HERE = Path(__file__).resolve().parent
_top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, cwd=HERE)
if _top.returncode != 0:
    sys.exit("RESULT-PACKAGE :: FAIL (not inside a git checkout; the build reads the paper at PAPER_REF through git)")
ROOT = Path(_top.stdout.strip())
NOTE = ROOT / "docs/analysis-note"
FD = "docs/orchestration/state/measurement-paper/5d-community-20261024"
RE2 = "docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partc_r2/partc-r2"

# The paper whose labels and printed text the package is keyed to. bc867318 is the methods draft, round 5
# (draft/methods-round5-20261108), which director-helper-3's restructure (PR #977) starts from. When the restructure
# lands, PAPER_REF and LABELS move to its commit and its label map.
PAPER_REF = "bc8673186ba945460dfee4e4ee78ec1012ec9174"
PAPER_PATH = "docs/analysis-note/paper_body.tex"

# Every record the package reads, pinned by full sha256 (measured at origin/main 8a627954; each equal at PAPER_REF).
SOURCES = {
    "dp": (f"{FD}/fd/with-cpl/data-product/fd_data_product_cpl.json",
           "d6752d2c64aad4426375c03a3171a7015f031e2027928cf89aea6cd3bbb84d50"),
    "s1": (f"{FD}/s1/readout/s1_assembly.json",
           "81e5ef3fe8e7b055360dc43b8a8240c9b5c39c8aa6e7c507b3211d305b326b21"),
    "cresp": ("docs/orchestration/state/measurement-scoping/assigned-uncertainties/cresp/cresp.json",
              "19bb2ee12827207fa346242ac901af48f6c80785eff5a14ff54133dff1ea01f0"),
    "f0b": (f"{FD}/fd/with-cpl/readout/fd_f0b_readout.json",
            "5f542830561731b567f2b97d78e5e9677a9802a35ef9c21855828bf184e6f3d6"),
    "f0": (f"{FD}/fd/readout/fd_f0_readout.json",
           "6e7d718bd393dd0600e974d0ce9b5c389486890cb7112550b22289008d6d312b"),
    "f1": (f"{FD}/fd/with-cpl/readout/fd_f1_readout.json",
           "5ccc89e58096a14ab8dc0e3e6f508ca4b2b546b629077560a09a4596cde40395"),
    "f1meta-g18": (f"{FD}/fd/receipts-f1/run/cluster/f1b3/gen5d/genie_v3_g18_xsec5d.meta.json",
                   "4fe333b8a2a220e37925a2989dfe38a95700197b98e6d8ecd130d7bc7d7d1963"),
    "f1meta-ar23": (f"{FD}/fd/receipts-f1/run/cluster/f1b3/gen5d/genie_v3_ar23_xsec5d.meta.json",
                    "d7d136e5cd2708617fb7fa5c0fe7333f39a1d9e3f21cff60e7f1df2578fd9579"),
    "valid": ("docs/orchestration/state/2d-closeout/valid-region-20261107/receipts/read/readout.json",
              "91bb604e3a62e2654e611750830e225061e5c0b0255b12455a23ac9be4eec84c"),
    "g": (f"{FD}/fd/gencmp-e/rerun1/chain/chdefs/with/readout/fd_g_readout.json",
          "a19009e0bd83b9bb8f9ad65fb65804e6f62c8953310103fbfe6fce5f84995875"),
    "g-nopl": (f"{FD}/fd/gencmp-e/rerun1/chain/chdefs/nopl/readout/fd_g_readout.json",
               "d9a1ce38040b8cd3c2a6deb787f8a7dc90aca5c4d3a5a8d25a60b7f8ab582ed9"),
    "gdefs": (f"{FD}/fd/gencmp/readout/defs.json",
              "544f4f4343095b5e78b59e0782ac3ce5ef5974b2e24dbb59be3708b5937556f8"),
    "e2": (f"{FD}/fd/gencmp-e2/rerun1/chi2/e2.json",
           "0aa73ebf654242ca07aa754f92670d582b097ae50fbcbc2a33e38b588d94985e"),
    "e2sens": (f"{FD}/fd/gencmp-e2/rerun1/sens/x_e2_sens.out.txt",
               "223f3f885b78b099b9e7ae34813fc94fc1830afd44e71e7c56590735d7a63f22"),
    "figratio": (f"{FD}/fd/gencmp-e/rerun1/chain/chdefs/with/figures-a2/fd_g_fig_ratio.json",
                 "271a68f41d9c2573d58d2810fc6a532d9d4a02898e580fe9ba22abced2295b90"),
    "vt2d": (f"{RE2}/values_table.tsv",
             "d0a8f47b084b786db8a45416e9b636cdf95f5e0a37e818586344fd0963a64d65"),
    "tension": (f"{RE2}/receipts/figs/tension_report.txt",
                "dee699e5ea767803f48ae457707bacd79948b5580fe40b294ea101c4f2306945"),
    "period": ("docs/orchestration/state/2d-closeout/per-period-benchmark-20261106/receipts/read/readout.json",
               "4872df322a4e2e49ef009c4fa7eb78f273b8bea75a8a97855fd57451d229dca1"),
    "ens1s1": (f"{FD}/fd/rounding-stability-20261106/ensemble/receipts/stage1-a1-analysis/ens1_stage1.json",
               "7f5a9ce4da8f59f3284715ff6f14f8106034b42c0301ad04979a8ed6b461ad99"),
    "ens1s2": (f"{FD}/fd/rounding-stability-20261106/ensemble/receipts/stage2-a1-analysis/ens1_stage2.json",
               "c2ee701d7c23643b257f633410c8416d4ca4e8ce5eb8b8ad38ff3afd244c01fd"),
}
PINS = {k: v[1] for k, v in SOURCES.items()}
TEXT_SOURCES = {"e2sens", "vt2d", "tension"}
CELLS = [f"R{i:02d}" for i in range(16)]
DP_CSV = {  # the data product's own CSVs, copied byte for byte; each is pinned by the product's files_sha256
    "cells": "fd_data_product_cpl_cells.csv",
    "C_e": "fd_data_product_cpl_C_e.csv",
    "C_model_abs": "fd_data_product_cpl_C_model_abs.csv",
    "C_resp": "fd_data_product_cpl_C_resp.csv",
    "C_PL5D": "fd_data_product_cpl_C_PL5D.csv",
    "C_total_plus_C_resp": "fd_data_product_cpl_C_total_plus_C_resp.csv",
    "reported": "fd_data_product_cpl_C_total_plus_C_resp_plus_C_PL5D.csv",
    "corr": "fd_data_product_cpl_corr_C_total_plus_C_resp_plus_C_PL5D.csv",
}


class Mismatch(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise Mismatch(msg)


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def norm(s):
    """Whitespace collapsed and markdown emphasis removed, for matching a quoted line against its record."""
    return re.sub(r"\s+", " ", s.replace("**", "").replace("`", "")).strip()


# ---------------------------------------------------------------------------------------------------------- inputs
def load_sources():
    d, raw = {}, {}
    for k, (rel, _) in SOURCES.items():
        need((ROOT / rel).is_file(), f"source missing from this checkout: {rel}")
        b = (ROOT / rel).read_bytes()
        got = sha256(b)
        need(got == PINS[k], f"source {rel}: sha256 {got[:16]}, pinned {PINS[k][:16]}")
        raw[k] = b
        d[k] = b.decode() if k in TEXT_SOURCES else json.loads(b)
    return d, raw


def load_producer():
    spec = importlib.util.spec_from_file_location("make_values_fived16", NOTE / "make_values_fived16.py")
    mv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mv)
    return mv


def parse_fvval(text):
    return {m[1]: m[2] for m in re.finditer(r"^\\@namedef\{fv@([^}]+)\}\{(.*)\}$", text, re.M)}


def parse_values_tex(text):
    out = {}
    for line in text.splitlines():
        m = re.match(r"\\newcommand\{\\([A-Za-z]+)\}\{([^}]*)\}", line)
        if m:
            need(m[1] not in out, f"values.tex defines \\{m[1]} twice")
            out[m[1]] = m[2]
    return out


def paper_text():
    r = subprocess.run(["git", "show", f"{PAPER_REF}:{PAPER_PATH}"], capture_output=True, cwd=ROOT)
    need(r.returncode == 0, f"cannot read {PAPER_PATH} at {PAPER_REF}: {r.stderr.decode().strip()}")
    return r.stdout.decode()


class Ctx:
    """Everything a file builder needs, and the record of what it checked."""

    def __init__(self, d, raw, mv, fv, vt, paper):
        self.d, self.raw, self.mv, self.fv, self.vt, self.paper = d, raw, mv, fv, vt, paper
        self.paper_flat = norm(paper)
        self.n_checked = {}
        self.asym = {}

    def key(self, fname, k, got):
        """got (the value formatted the producer's way) must equal \\fvval{k}."""
        need(k in self.fv, f"{fname}: values_fived16.tex has no key {k}")
        need(self.fv[k] == got, f"{fname}: {k} is {self.fv[k]!r} in values_fived16.tex, the record gives {got!r}")
        self.n_checked[fname] = self.n_checked.get(fname, 0) + 1

    def macro(self, fname, m, got):
        need(m in self.vt, f"{fname}: values.tex has no macro \\{m}")
        need(self.vt[m] == got, f"{fname}: \\{m} is {self.vt[m]!r} in values.tex, the record gives {got!r}")
        self.n_checked[fname] = self.n_checked.get(fname, 0) + 1

    def printed(self, fname, phrase):
        """A value with no key: the phrase, built from the record, must occur in the paper at PAPER_REF."""
        need(norm(phrase) in self.paper_flat, f"{fname}: the paper at {PAPER_REF[:8]} does not print {phrase!r}")
        self.n_checked[fname] = self.n_checked.get(fname, 0) + 1


def write_csv(rows, header):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue().encode()


def num(x):
    return repr(float(x))


def read_csv_bytes(b):
    return list(csv.reader(io.StringIO(b.decode())))


# ------------------------------------------------------------------------------------------------------ the files
def build_cov16(c):
    """tab:result16, tab:corr16 and sec:cov16: the data product's own CSVs, byte for byte."""
    dp, mv = c.d["dp"], c.mv
    base = (ROOT / SOURCES["dp"][0]).parent
    out = {}
    for k, name in DP_CSV.items():
        b = (base / name).read_bytes()
        need(sha256(b) == dp["files_sha256"][name], f"{name}: sha256 differs from the data product's files_sha256")
        out[k] = b
    need([c_["cell"] for c_ in dp["cells"]] == CELLS, "the data product's cells are not R00-R15")
    # cells.csv: boxes, f and the reported sigma equal the JSON and the paper's keys (tab:result16)
    rows = read_csv_bytes(out["cells"])
    hdr, body = rows[0], rows[1:]
    need([r[0] for r in body] == CELLS, "cells.csv: rows are not R00-R15")
    col = {h: i for i, h in enumerate(hdr)}
    fn = "tab-result16_cells.csv"
    rep = dp["relative_sigma"]["C_total_plus_C_resp_plus_C_PL5D"]
    for i, (cell, r) in enumerate(zip(CELLS, body)):
        f = float(r[col["f"]])
        need(f == dp["f"][i], f"{fn}: {cell} f differs from the JSON")
        c.key(fn, f"f-{cell}", f"{f / 1e-40:#.3g}".rstrip("."))
        for ax in ("pt", "pz", "eavail", "q3", "W"):
            lo, hi = float(r[col[f"{ax}_lo"]]), float(r[col[f"{ax}_hi"]])
            need([lo, hi] == dp["cells"][i]["box"][ax], f"{fn}: {cell} {ax} box differs from the JSON")
            c.key(fn, f"box-{cell}-{ax}", f"{lo:g}--{hi:g}")
        s = float(r[col["rel_sigma_C_total_plus_C_resp_plus_C_PL5D"]])
        need(s == rep[i], f"{fn}: {cell} reported sigma differs from the JSON")
        c.key(fn, f"sig-reported-{cell}", mv.pct(s))
        c.key(fn, f"sig1-reported-{cell}", mv.pct1(s))
    srt = sorted(rep)
    c.key(fn, "sigmed-reported", mv.pct((srt[7] + srt[8]) / 2))
    # each matrix equals the JSON; the reported matrix's diagonal gives the reported sigma; corr gives tab:corr16
    for k in ("C_e", "C_model_abs", "C_resp", "C_PL5D", "C_total_plus_C_resp", "reported"):
        fn = f"sec-cov16_{k}.csv"
        rows = read_csv_bytes(out[k])
        need(rows[0] == ["cell"] + CELLS and [r[0] for r in rows[1:]] == CELLS, f"{fn}: not a 16 x 16 cell matrix")
        jk = "C_total_plus_C_resp_plus_C_PL5D" if k == "reported" else k
        m = [[float(x) for x in r[1:]] for r in rows[1:]]
        need(m == dp["matrices"][jk], f"{fn}: differs from the data product's matrices[{jk}]")
        asym = max(abs(m[i][j] - m[j][i]) / (m[i][i] * m[j][j]) ** 0.5 for i in range(16) for j in range(16))
        need(asym < 1e-12, f"{fn}: not symmetric (largest |C_ij - C_ji| / sqrt(C_ii C_jj) = {asym:.2e})")
        c.asym[fn] = asym
        sig = [m[i][i] ** 0.5 / dp["f"][i] for i in range(16)]
        need(max(abs(a / b - 1) for a, b in zip(sig, dp["relative_sigma"][jk])) < 1e-12,
             f"{fn}: its diagonal does not give the data product's relative sigma")
        c.n_checked[fn] = c.n_checked.get(fn, 0) + 1
        if k == "C_PL5D":
            for cell, x in zip(CELLS, sig):
                c.key(fn, f"sig1-C_PL5D-{cell}", mv.pct1(x))
    fn = "tab-corr16.csv"
    rows = read_csv_bytes(out["corr"])
    rho = [[float(x) for x in r[1:]] for r in rows[1:]]
    need(rho == dp["correlation"], f"{fn}: differs from the data product's correlation")
    for i in range(16):
        for j in range(i):
            x = f"{rho[i][j]:.2f}"
            c.key(fn, f"corr-{CELLS[i]}-{CELLS[j]}", ("$-$" + x[1:]) if x.startswith("-") else x)
    return {"tab-result16_cells.csv": out["cells"], "tab-corr16.csv": out["corr"],
            **{f"sec-cov16_{k}.csv": out[k] for k in ("C_e", "C_model_abs", "C_resp", "C_PL5D",
                                                         "C_total_plus_C_resp", "reported")}}


GROUPS = [("stat", "s1"), ("flux", "s1"), ("interaction", "s1"), ("detector", "s1"), ("lateral", "s1"),
          ("normalization", "s1"), ("C_e", "s1"), ("C_model", "s1"), ("C_resp", "cresp"), ("C_PL5D", "dp"),
          ("reported", "dp")]


def build_groups16(c):
    """tab:groups16: each group's relative sigma, sqrt(diag)/f, per cell (the records hold no per-group matrices)."""
    fn = "tab-groups16.csv"
    cols = {}
    for grp, src in GROUPS:
        if src == "dp":
            vals = c.d["dp"]["relative_sigma"]["C_PL5D" if grp == "C_PL5D" else "C_total_plus_C_resp_plus_C_PL5D"]
        else:
            vals = c.d[src]["relative_sigma"][grp]
            vals = [vals[x] for x in CELLS] if isinstance(vals, dict) else vals
        need(len(vals) == 16, f"{fn}: {grp} has {len(vals)} cells")
        for cell, x in zip(CELLS, vals):
            c.key(fn, f"sig1-{grp}-{cell}", c.mv.pct1(x))
        srt = sorted(vals)
        c.key(fn, f"sigmed1-{grp}", c.mv.pct1((srt[7] + srt[8]) / 2))
        cols[grp] = vals
    for src in ("s1", "cresp"):
        need(c.d[src]["meta"]["cells"] == CELLS, f"{fn}: {src}'s cells are not R00-R15")
    rows = [[cell] + [num(cols[g][i]) for g, _ in GROUPS] for i, cell in enumerate(CELLS)]
    return {fn: write_csv(rows, ["cell"] + [f"rel_sigma_{g}" for g, _ in GROUPS])}


FD16_ROWS = ["nominal", "A7_mnvtune", "A7_genie_cv", "A7_genie_mec", "W2", "A7_nuwro", "W1", "W3", "closure_nuwro",
             "stage0c_gibuu", "A7_gibuu", "q3"]


def build_fd16(c):
    """tab:fd16: the fake-data grades under the reported covariance (F0b) and under C_total (F0)."""
    fn = "tab-fd16.csv"
    mv = c.mv
    tr = {tag: {t["name"]: t for t in c.d[tag]["truths"]} for tag in ("f0b", "f0")}
    trig = c.d["f0b"]["triggers"]
    rows = []
    for name in FD16_ROWS:
        row = [name]
        for tag in ("f0b", "f0"):
            t = tr[tag][name]
            need(t["graded"], f"{fn}: {tag} {name} is not graded")
            g = t["grade"]
            k = f"{tag}-{name}"
            c.key(fn, f"{k}-chi2", f"{g['chi2']:.2f}")
            c.key(fn, f"{k}-chi2int", f"{g['chi2']:.0f}")
            c.key(fn, f"{k}-p", mv.p_tex(g["p"]))
            cells = ", ".join(g["cells_abs_z_gt_2"]) or "---"
            c.key(fn, f"{k}-cells", cells)
            zmax = max(abs(z) for z in g["z"])
            c.key(fn, f"{k}-zmax", f"{zmax:.2f}")
            c.key(fn, f"{k}-n", str(t["n_experiments"]))
            row += [t["grade_matrix"], t["own_vertex"] or "", num(g["chi2"]), g["ndf"], num(g["p"]),
                    " ".join(g["cells_abs_z_gt_2"]), num(zmax), t["n_experiments"]]
        need(tr["f0b"][name]["own_vertex"] == tr["f0"][name]["own_vertex"], f"{fn}: {name}'s own vertex differs")
        rows.append(row)
    hdr = ["truth"] + [f"{a}_{b}" for a in ("reported", "C_total") for b in
                       ("matrix", "without_component", "chi2", "ndf", "p", "cells_abs_z_gt_2", "max_abs_z",
                        "n_pseudo_experiments")]
    need(trig["rule"] == c.d["f0"]["triggers"]["rule"], f"{fn}: F0 and F0b trigger rules differ")
    return {fn: write_csv(rows, hdr)}


def build_tunes(c):
    """sec:fd16 and tab:outcomes: the two held-out GENIE v3 tunes (F1), a bias test, not a coverage test."""
    fn = "sec-fd16_tunes.csv"
    mv, f1 = c.mv, c.d["f1"]
    need("not a coverage test" in f1["labels"]["f1"], f"{fn}: F1's label no longer says it is not a coverage test")
    held = {t["name"]: t for t in f1["truths"] if t["group"] == "held-out"}
    rows = []
    for tune in ("g18", "ar23"):
        gen = c.d[f"f1meta-{tune}"]["generator"]
        c.key(fn, f"f1-tune-{tune}", gen.removeprefix("genie_v3_").replace("_", r"\_"))
        for rec, k, kind in ((f"F1_genie_v3_{tune}", f"f1-{tune}", "ensemble"),
                             (f"F1_closure_genie_v3_{tune}", f"f1-closure-{tune}", "noise-free closure")):
            t = held.pop(rec)
            gr = t["grade"]
            c.key(fn, f"{k}-chi2", f"{gr['chi2']:.2f}")
            c.key(fn, f"{k}-chi2int", f"{gr['chi2']:.0f}")
            c.key(fn, f"{k}-p", mv.p_tex(gr["p"]))
            i = max(range(16), key=lambda j: abs(gr["z"][j]))
            c.key(fn, f"{k}-zmax", f"{abs(gr['z'][i]):.2f}")
            c.key(fn, f"{k}-zcell", CELLS[i])
            c.key(fn, f"{k}-n", str(t["n_experiments"]))
            rows.append([gen, kind, t["grade_matrix"], num(gr["chi2"]), gr["ndf"], num(gr["p"]),
                         " ".join(gr["cells_abs_z_gt_2"]), num(abs(gr["z"][i])), CELLS[i], t["n_experiments"]])
    need(not held, f"{fn}: unexpected held-out records {sorted(held)}")
    hdr = ["tune", "record", "matrix", "chi2", "ndf", "p", "cells_abs_z_gt_2", "max_abs_z", "max_abs_z_cell",
           "n_pseudo_experiments"]
    return {fn: write_csv(rows, hdr)}


def build_validity(c):
    """sec:fd16 and tab:outcomes: each cell's V-ATLAS and V-PRIOR class (no fvval keys; checked against the text)."""
    fn = "sec-fd16_validity.csv"
    r = c.d["valid"]["readings"]
    va, vp = r["V-ATLAS"]["cells"], r["V-PRIOR"]["cells"]
    need(sorted(va) == CELLS and sorted(vp) == CELLS, f"{fn}: the readout's cells are not R00-R15")
    rho_keys = ["b_raw/g_raw", "b_raw/g_sub", "b_sub/g_raw", "b_sub/g_sub"]
    rows = []
    for cell in CELLS:
        a, p = va[cell], vp[cell]
        need(a["class"] == ("valid" if a["A1"] and a["A2"] and a["A3"] else "not valid"),
             f"{fn}: {cell}'s V-ATLAS class is not A1 and A2 and A3")
        rows.append([cell, a["A1"], a["A2"], a["A3"], num(a["mc_neff_truth"]), num(a["stat_rel"]), a["class"],
                     num(p["S_b"]["raw"]), num(p["S_b"]["sub"]), num(p["S_g"]["raw"]), num(p["S_g"]["sub"])]
                    + [num(p["rho"][k]) for k in rho_keys] + [p["class"]])
    not_a = [x for x in CELLS if va[x]["class"] != "valid"]
    not_p = [x for x in CELLS if vp[x]["class"] != "valid"]
    both = [x for x in CELLS if x not in not_a and x not in not_p]
    need(sorted(r["V-ATLAS"]["valid"]) == sorted(set(CELLS) - set(not_a)), f"{fn}: V-ATLAS's valid list differs")
    need(sorted(r["V-PRIOR"]["valid"]) == sorted(set(CELLS) - set(not_p)), f"{fn}: V-PRIOR's valid list differs")
    need(len(not_a) == len(not_p), f"{fn}: the paper prints one count for both rules")
    c.printed(fn, f"{16 - len(not_a)} of 16 cells under each (not {', '.join(not_a)}; not {', '.join(not_p)}), "
                  f"{len(both)} under both")
    hdr = ["cell", "atlas_A1", "atlas_A2", "atlas_A3", "atlas_mc_neff_truth", "atlas_stat_rel", "atlas_class",
           "prior_S_b_raw", "prior_S_b_sub", "prior_S_g_raw", "prior_S_g_sub"] + \
          [f"prior_rho_{k.replace('/', '_over_')}" for k in rho_keys] + ["prior_class"]
    return {fn: write_csv(rows, hdr)}


VT_MACROS = ["sigTwoD", "ratioTot", "chiPaper", "pullRMS", "uqMedian", "uqIntegral", "fluxBand"]
VT_PRINTED = ["tens-chi2-shape", "tens-chi2-norm", "tens-73-modes", "tens-73-chi2"]


def build_benchmark2d(c):
    """sec:repro2d and tab:outcomes: the 2D benchmark's scalars (the per-bin result and its covariance are not in the
    repository; see README)."""
    fn = "sec-repro2d_benchmark.csv"
    vt = {r["id"]: r for r in csv.DictReader(io.StringIO(c.d["vt2d"]), delimiter="\t")}
    rows = []
    for m in VT_MACROS:
        r = vt[f"m-{m}"]
        need(r["status"] == "control PASS", f"{fn}: m-{m} status is {r['status']!r}")
        need(r["where"] == f"N/values.tex:\\{m}", f"{fn}: m-{m} is not the row for \\{m}")
        c.macro(fn, m, r["refined_rendered"])
        rows.append([f"m-{m}", f"values.tex \\{m}", r["refined_value"], r["refined_rendered"], "values_table.tsv",
                     r["note"]])
    for k in VT_PRINTED:
        r = vt[k]
        need(r["status"] == "control PASS", f"{fn}: {k} status is {r['status']!r}")
        rows.append([k, r["where"], r["refined_value"], r["refined_rendered"], "values_table.tsv", r["note"]])
    v = {k: vt[k]["refined_rendered"] for k in VT_PRINTED}
    c.printed(fn, rf"shape part {v['tens-chi2-shape']}, normalization part {v['tens-chi2-norm']}; the "
                  rf"{v['tens-73-modes']} best-determined directions hold ${v['tens-73-chi2']}\times205$")
    c.printed(fn, rf"$\chi^2/\mathrm{{ndf}}=\chiPaper$ over 205 bins")
    # the 73-direction chi2/ndf is the tension report's own rank-truncation row (rcond 1e-4)
    m = re.search(r"^\s*1e-04\s+([\d.]+)\s+(\d+)\s*$", c.d["tension"], re.M)
    need(m and float(m[1]) == float(vt["tens-73-chi2"]["refined_value"]) and m[2] == vt["tens-73-modes"]["refined_rendered"],
         f"{fn}: the tension report's rcond 1e-4 row does not give the 73-direction values")
    # the per-period benchmark's R5 (replica noise model), as Table I prints it
    pr = c.d["period"]["readings"]["by_model"]["replica"]
    k73, kbar = pr["R5"], pr["R5bar"]
    need(k73["class"] == "no change" and kbar["class"].startswith("farther without"), f"{fn}: R5's classes changed")
    need(k73["ABC"]["k"] == 73 and kbar["ABC"]["k"] == 132, f"{fn}: R5's direction counts changed")
    s73, dbar = f"{k73['resolved_3sigma']:.2f}", f"{-kbar['delta']:.2f}"
    c.printed(fn, f"no change without 1G--1M (smallest resolved change {s73} per direction); other 132: farther "
                  f"without it, by {dbar}")
    rows.append(["period-R5-K73-resolved_3sigma", "tab:outcomes", num(k73["resolved_3sigma"]), s73,
                 "per-period readout.json", f"class: {k73['class']}"])
    rows.append(["period-R5-K132-delta", "tab:outcomes", num(kbar["delta"]), dbar, "per-period readout.json",
                 f"class: {kbar['class']}; the paper prints -delta"])
    return {fn: write_csv(rows, ["id", "printed_at", "value", "printed", "record", "note"])}


GEN = ["genie_cv", "genie_mec", "nuwro", "mnvtune_v1", "gibuu"]   # tab:gen16's row order


def build_gen16(c):
    """tab:gen16 (Supplement S10 in the restructure): chi2 of each prediction, with and without C_PL5D."""
    fn = "tab-gen16.csv"
    mv = c.mv
    d_nopl = mv.load(mv.NOPL_READOUTS)
    arms = {"with": mv.table4(mv.load(), "with"), "nopl": mv.table4(d_nopl, "without")}
    rows = []
    for name, k in ((n, mv.PRED[n]) for n in GEN):
        row = [name, c.fv[f"label-{k}"].replace("~", " ")]
        for arm, suf in (("with", ""), ("nopl", "-nopl")):
            p = arms[arm][name]
            for part in ("total", "shape_only"):
                q = p[part]
                c.key(fn, f"g-{k}-{part}-chi2int{suf}", f"{q['chi2']:.0f}")
                c.key(fn, f"g-{k}-{part}-ndf{suf}", str(q["ndf"]))
                c.key(fn, f"g-{k}-{part}-p{suf}", mv.p_tex(q["p"]))
                row += [num(q["chi2"]), q["ndf"], num(q["p"])]
        row.append(len(arms["with"][name]["cells"]))
        rows.append(row)
    hdr = ["prediction", "label"] + [f"{arm}_{part}_{x}" for arm in ("reported", "without_C_PL5D")
                                     for part in ("total", "shape_only") for x in ("chi2", "ndf", "p")] + ["n_cells"]
    return {fn: write_csv(rows, hdr)}


def build_cmodel16(c):
    """tab:cmodel16 (Supplement S10 in the restructure): change of each total chi2 under C_model's variations."""
    fn = "tab-cmodel16.csv"
    e2 = c.d["e2"]
    head, _, body = c.d["e2sens"].partition("\n{")
    need(all(x.startswith(("PASS ", "[PASS ")) for x in head.splitlines()), f"{fn}: the sensitivity receipt failed")
    s = json.loads("{" + body)
    rows = []
    for a, arm in (("with", "reported"), ("nopl", "without_C_PL5D")):
        for n in ("genie_cv", "genie_mec", "nuwro", "gibuu"):
            for part in ("total", "shape_only"):
                r, q = e2["chi2"][a][n][part], s["chi2"][a][n][part]
                need((q["carbon"], q["CH"]) == (r["carbon"], r["CH"]), f"{fn}: E2 and its sensitivity receipt differ")
                k = f"e2-{a}-{c.mv.PRED[n]}-{part}"
                dch, dx2, dx0 = r["CH"] - r["carbon"], q["doubled"] - q["carbon"], q["removed"] - q["carbon"]
                for tag, x in (("dch", dch), ("dx2", dx2), ("dx0", dx0)):
                    c.key(fn, f"{k}-{tag}r1", f"{x:+.1f}")
                rows.append([arm, n, part, num(q["carbon"]), num(r["CH"]), num(q["doubled"]), num(q["removed"]),
                             num(dch), num(dx2), num(dx0)])
    hdr = ["matrix", "prediction", "chi2_kind", "chi2_carbon_ratios", "chi2_CH_ratios", "chi2_C_model_doubled",
           "chi2_C_model_removed", "delta_CH", "delta_doubled", "delta_removed"]
    return {fn: write_csv(rows, hdr)}


def build_ratio16(c):
    """fig:ratio16: the data behind Fig. fd_g_fig_ratio, f/g per cell and the bar (f/g) sigma/f."""
    fn = "fig-ratio16.csv"
    side = c.d["figratio"]
    need(side["inputs_sha256"]["g_readout"] == PINS["g"], f"{fn}: the figure was not drawn from the pinned readout")
    items = {it["gid"]: it for it in side["plotted"]["items"]}
    rows = []
    for p in c.d["g"]["predictions"]:
        name, k = p["name"], c.mv.PRED[p["name"]]
        line, err = items[f"ratio:{name}"], items[f"ratio:{name}:err"]
        need(line["cells"] == p["cells"], f"{fn}: {name}'s plotted cells differ from the readout's")
        for i, cell in enumerate(p["cells"]):
            f, g, s = p["f"][i], p["g"][i], p["sigma_total_over_f"][i]
            r, half = f / g, (f / g) * s
            need(abs(line["y"][i] / r - 1) < 1e-12, f"{fn}: {name} {cell}: the plotted f/g differs")
            need(abs(err["lo"][i] - (r - half)) < 1e-12 and abs(err["hi"][i] - (r + half)) < 1e-12,
                 f"{fn}: {name} {cell}: the plotted bar differs from (f/g) sigma/f")
            c.key(fn, f"g-{k}-gf-{cell}", f"{100 * p['g_over_f_minus_1'][i]:.1f}")
            rows.append([name, cell, num(f), num(g), num(r), num(s), num(half)])
    hdr = ["prediction", "cell", "f_data", "g_prediction", "f_over_g", "sigma_reported_over_f", "bar_half_width"]
    return {fn: write_csv(rows, hdr)}


ENS1_KEYS = ["ens1-n", "ens1-median", "ens1-max", "ens1-bar-median", "ens1-bar-max", "ens1-ntruths", "ens1-nnoworse"]


def build_ens1(c):
    """sec:cov5d and tab:outcomes: the ensemble-averaged variant (ENS1). Pending until values_fived16.tex carries
    the ens1-* keys (the round-5 branch)."""
    fn = "sec-cov5d_ens1.csv"
    if not all(k in c.fv for k in ENS1_KEYS):
        return {}, ("ENS1", "the ens1-* keys of values_fived16.tex, which land with the round-5 paper branch "
                            "(draft/methods-round5-20261108 at bc867318); its sources are already pinned here")
    e1, e2 = c.d["ens1s1"], c.d["ens1s2"]
    st = e1["stability_E96"]
    need(e1["verdict"] == "STAB_PASS" and e2["verdict"] == "BIAS_WORSE", f"{fn}: a verdict changed")
    vals = {"ens1-n": str(e1["N"]), "ens1-median": f"{st['mean_median']:.2f}", "ens1-max": f"{st['mean_max']:.2f}",
            "ens1-bar-median": f"{e1['bars']['median']:.1f}", "ens1-bar-max": f"{e1['bars']['max']:.1f}",
            "ens1-ntruths": str(len(e2["truths_judged"])),
            "ens1-nnoworse": str(len(e2["truths_judged"]) - len(e2["worse"]))}
    for k, x in vals.items():
        c.key(fn, k, x)
    rows = [["n_fits", e1["N"]], ["stability_median", num(st["mean_median"])], ["stability_max", num(st["mean_max"])],
            ["bar_median", num(e1["bars"]["median"])], ["bar_max", num(e1["bars"]["max"])],
            ["stage1_verdict", e1["verdict"]], ["truths_judged", len(e2["truths_judged"])],
            ["truths_worse", " ".join(e2["worse"])], ["stage2_verdict", e2["verdict"]]]
    return {fn: write_csv(rows, ["quantity", "value"])}, None


PENDING = [
    ("FD-PRR", "the FD-PRR outcome record and its committed readout (FD-PRR-DECLARATION.md, FD-PRR-BINDING-1.md); "
               "the plan's step 2, within its 27.0 node-h cap"),
    ("LL5D", "the LL5D outcome record and its committed readout (LL5D-DECLARATION.md); the plan's step 3, within its "
             "148.0 node-h cap"),
    ("V-HALF", "the V-HALF declaration and its committed readout (DECISION-20261109-joseph-bias-half-rule.md: "
               "|bias| <= 1/2 x the truth's departure from the prior, per cell)"),
    ("2D-ARRAYS", "the 2D per-bin result E_R and its 205 x 205 covariance Q_R with blocks (cov2d_Q_205.npz, sha256 "
                  "7153b194...), on pscratch and in the HPSS bundle re2-2d-rebuild-partc-20261024; a read-only copy "
                  "needs the director's go"),
]

# ----------------------------------------------------------------------------------------------------- licences
# Each file's licence, quoted from its record. Every quote must occur verbatim (whitespace and markdown emphasis
# aside) in the record named, or the build stops.
LIC = {
    "cov16": [
        (f"{FD}/FD-CT-5B-ADDITION-REPORT.md", "CITABLE FOR", [
            "the revised products and their digests;",
            "the with-and-without numbers, each labelled with its matrix."]),
        (f"{FD}/fd/with-cpl/data-product/fd_data_product_cpl.json", "NOT CITABLE FOR", [
            "coverage",
            "a validated size for C_PL,5D: a block built from the observed differences contains them by construction",
            "the cause of a period difference, or which period is right",
            "a coverage or calibration statement"]),
        (f"{FD}/fd/with-cpl/data-product/fd_data_product_cpl.json", "LABEL", [
            "no reading, claim or release text; whether it ships is Joseph's",
            "added after the data were seen; published with and without"]),
        (PAPER_PATH, "THE PAPER'S OWN SCOPE (at PAPER_REF)", [
            "The sixteen-cell cross section the estimator gives on the data is therefore not a measurement",
            "Illustrative output on data: not for fitting or for constraining models"]),
    ],
    "groups16": [
        ("docs/orchestration/state/measurement-scoping/assigned-uncertainties/cresp/cresp.json", "LABEL (C_resp)", [
            "neutron and muon energy deposits are not shifted (D1: neutrons out)"]),
    ],
    "fd16": [
        (f"{FD}/FD-F0b-REPORT.md", "CITABLE FOR", ["the counts, χ² and p below, each beside its matrix"]),
        (f"{FD}/FD-F0b-REPORT.md", "NOT CITABLE FOR", [
            "any data-against-generator quantity, since F0b reads only fake-data products;",
            "coverage, held-out truths or the detector response, exactly as for F0",
            "any reading of the difference between the two columns."]),
    ],
    "tunes": [
        (f"{FD}/FD-F1-REPORT.md", "WHAT THIS IS", [
            "a bias test at two held-out GENIE v3 truths, not a coverage test",
            "CANNOT AUTHORIZE: a reading, a claim, paper text, or any statement about coverage."]),
    ],
    "validity": [
        ("docs/orchestration/OUTCOME-20261107-valid-region.md", "CITABLE FOR", [
            "each cell's V-ATLAS and V-PRIOR class, with its inputs, as defined in the declaration;"]),
        ("docs/orchestration/OUTCOME-20261107-valid-region.md", "NOT CITABLE FOR", [
            "coverage. No interval is validated, and the fake-data tests grade bias, not coverage;",
            "a measurement. These are diagnostics of the estimator on committed products. No reported value changes;",
            "V-PRIOR, or its threshold of 0.5, as ATLAS's, or as the advisor's own formulation;",
            "a non-valid cell as excluded, wrong or unreported;",
            "ATLAS guide item 5, which is not met;"]),
    ],
    "benchmark2d": [
        ("docs/orchestration/DECISION-20261024-joseph-adopt-re2-2d-refined.md", "DECIDED", [
            "The adopted 2D result is E_R, with Q_R as its headline uncertainty.",
            "No coverage validation is claimed for them."]),
        ("docs/orchestration/DECISION-20261109-joseph-methods-baseline-and-plan.md", "THE PAPER DOES NOT CLAIM", [
            "that 5D validates the full distribution, beyond the 2D benchmark with its stated limits;"]),
        ("docs/orchestration/OUTCOME-20261107-per-period-2d-benchmark.md", "NOT CITABLE FOR (the per-period rows)", [
            "which run period is right, that 1G–1M is wrong, or that the published result is right;",
            "a cause of the 2D shape difference or of the run-period step;"]),
    ],
    "illustrative": [
        (PAPER_PATH, "THE PAPER'S OWN SCOPE (at PAPER_REF)", [
            "Illustrative output on data: not for fitting or for constraining models"]),
        (f"{FD}/FD-GENCMP-AMENDMENT-E-REPORT.md", "NOT CITABLE FOR", [
            "a validation of the reported covariance or of Q_R;", "a generator exclusion;"]),
        (f"{FD}/FD-GENCMP-AMENDMENT-E-ADDENDUM-E2-REPORT.md", "NOT CITABLE FOR", [
            "a new C_model;", "a validation of C_model's coverage;"]),
        (f"{FD}/FD-G-FIGURES-REPORT.md", "NOT CITABLE FOR (the figure)", ["any reading of a figure;"]),
        (PAPER_PATH, "THE PAPER'S FOOTNOTES ON TWO PREDICTIONS (at PAPER_REF)", [
            "In NuWro's free-proton sample, the supplement generated at neutrino energies of 50--100~GeV is flagged: "
            "the events lost to generator aborts there were not shown to be negligible",
            "Corrected to CH with GiBUU's own free-proton sample",
            "That sample failed its sampling-closure check"]),
    ],
    "every": [
        (PAPER_PATH, "THE PAPER (at PAPER_REF)", [
            "Interval coverage has not been validated.",
            "The sixteen-cell cross section the estimator gives on the data is therefore not a measurement"]),
    ],
    "ens1": [
        ("docs/orchestration/OUTCOME-20261109-ens1-stab-pass-bias-worse.md", "CITABLE FOR", [
            "The consequence: the reported estimator, configuration (e), is unchanged."]),
        ("docs/orchestration/OUTCOME-20261109-ens1-stab-pass-bias-worse.md", "NOT CITABLE FOR", [
            "That E₉₆ is a stabilised variant",
            "That the rounding instability is fixed or removed for the reported result."]),
    ],
}
DESCRIPTIVE = "illustrative, descriptive; not for fitting or constraining models"
LIC_TITLE = {"cov16": "the 16-cell result and its covariance", "groups16": "the per-group uncertainties",
             "fd16": "the fake-data tests", "tunes": "the held-out tunes", "validity": "the per-cell validity rules",
             "benchmark2d": "the 2D benchmark", "illustrative": "the generator comparisons (descriptive)",
             "ens1": "the ensemble-averaged variant", "every": "every file"}


def check_licences(paper):
    for blocks in LIC.values():
        for rel, _, quotes in blocks:
            need(rel == PAPER_PATH or (ROOT / rel).is_file(), f"licence record missing from this checkout: {rel}")
            hay = norm(paper if rel == PAPER_PATH else (ROOT / rel).read_text())
            for q in quotes:
                need(norm(q) in hay, f"licence quote not found in {rel}: {q!r}")


# Each package file: its label at PAPER_REF, a description, its sources and its licence block.
FILES = [
    ("tab-result16_cells.csv", "tab:result16", "the 16 cells: box edges (GeV/c for pT, p_par, q3; GeV for E_avail, "
     "W), f in cm^2/nucleon (an integral over the box), and each matrix's relative sigma sqrt(diag)/f; the "
     "data product's own cells CSV", ["dp"], "cov16"),
    ("sec-cov16_reported.csv", "sec:cov16", "the reported covariance C_total + C_resp + C_PL,5D, (cm^2/nucleon)^2",
     ["dp"], "cov16"),
    ("sec-cov16_C_total_plus_C_resp.csv", "sec:cov16", "the covariance without C_PL,5D (published with and without)",
     ["dp"], "cov16"),
    ("sec-cov16_C_e.csv", "sec:cov16", "C_e, the sum of the statistical, flux, interaction, detector, lateral and "
     "normalization groups", ["dp"], "cov16"),
    ("sec-cov16_C_model_abs.csv", "sec:cov16", "C_model, the generator-model component", ["dp"], "cov16"),
    ("sec-cov16_C_resp.csv", "sec:cov16", "C_resp, the calorimetric response component", ["dp"], "cov16"),
    ("sec-cov16_C_PL5D.csv", "sec:cov16", "C_PL,5D, the run-period block, added after the data were seen", ["dp"],
     "cov16"),
    ("tab-corr16.csv", "tab:corr16", "the correlation matrix of the reported covariance", ["dp"], "cov16"),
    ("tab-groups16.csv", "tab:groups16", "each group's relative sigma sqrt(diag)/f per cell (fraction, not %)",
     ["s1", "cresp", "dp"], "groups16"),
    ("tab-fd16.csv", "tab:fd16", "fake-data grades at 12 truths: chi2 (16 dof), p, cells with |z| > 2 and max |z|, "
     "under the reported covariance (F0b) and under C_total (F0), each without the truth's own generator component "
     "where without_component names it", ["f0b", "f0"], "fd16"),
    ("sec-fd16_tunes.csv", "sec:fd16", "the two held-out GENIE v3 tunes: ensemble and noise-free closure grades",
     ["f1", "f1meta-g18", "f1meta-ar23"], "tunes"),
    ("sec-fd16_validity.csv", "sec:fd16", "per-cell validity: V-ATLAS (A1-A3 and class) and V-PRIOR (S_b, S_g, rho "
     "and class)", ["valid"], "validity"),
    ("sec-repro2d_benchmark.csv", "sec:repro2d", "the 2D benchmark's scalars against the published result, and the "
     "per-period R5 rows", ["vt2d", "tension", "period"], "benchmark2d"),
    ("tab-gen16.csv", "tab:gen16", "chi2 of each generator prediction, total and shape-only, with and without "
     f"C_PL,5D, each plus V_g. {DESCRIPTIVE}", ["g", "g-nopl", "gdefs"], "illustrative"),
    ("tab-cmodel16.csv", "tab:cmodel16", "chi2 under C_model with CH shape ratios, doubled and removed. "
     f"{DESCRIPTIVE}", ["e2", "e2sens"], "illustrative"),
    ("fig-ratio16.csv", "fig:ratio16", f"the data behind the ratio figure: f, g, f/g and the bar (f/g) sigma/f. "
     f"{DESCRIPTIVE}", ["g", "figratio"], "illustrative"),
    ("sec-cov5d_ens1.csv", "sec:cov5d", "the ensemble-averaged variant (96 fits): stability and bias verdicts",
     ["ens1s1", "ens1s2"], "ens1"),
]
BUILDERS = [build_cov16, build_groups16, build_fd16, build_tunes, build_validity, build_benchmark2d, build_gen16,
            build_cmodel16, build_ratio16]


# ------------------------------------------------------------------------------------------------------ assemble
def assemble():
    """Return ({package path: bytes}, [pending], ctx). Raises Mismatch on any disagreement."""
    d, raw = load_sources()
    mv = load_producer()
    # the producer pins the same files: same path, and its short pin a prefix of the full one here
    for k, (rel, pin) in SOURCES.items():
        theirs = mv.NOPL_READOUTS.get("g") if k == "g-nopl" else mv.READOUTS.get(k)
        if theirs:
            need(theirs[0] == rel and pin.startswith(theirs[1]),
                 f"source {k}: make_values_fived16.py pins {theirs[0]} {theirs[1]}, the package {rel} {pin[:8]}")
    fresh = mv.all_values()
    fv = parse_fvval((NOTE / "values_fived16.tex").read_text())
    need(fv == fresh, "values_fived16.tex is not a fresh generation of make_values_fived16.py; regenerate it first")
    vt = parse_values_tex((NOTE / "values.tex").read_text())
    paper = paper_text()
    if "fv" in PLANT:                      # --self-test only: a wrong value after the freshness check
        fv[PLANT["fv"][0]] = PLANT["fv"][1]
    if "vt" in PLANT:
        vt[PLANT["vt"][0]] = PLANT["vt"][1]
    if "paper" in PLANT:
        need(PLANT["paper"][0] in paper, f"self-test: {PLANT['paper'][0]!r} is not in the paper")
        paper = paper.replace(*PLANT["paper"])
    c = Ctx(d, raw, mv, fv, vt, paper)
    for _, label, *_ in FILES:
        need(f"\\label{{{label}}}" in paper, f"the paper at {PAPER_REF[:8]} has no \\label{{{label}}}")
    check_licences(paper)
    out = {}
    for b in BUILDERS:
        out.update(b(c))
    files, pend = build_ens1(c)
    out.update(files)
    pending = [p for p in [pend] if p] + PENDING
    for name, what in pending:
        out[f"pending/{name}.txt"] = (f"PENDING: {name}\nWaits for: {what}\nNothing in this package stands in for "
                                      f"it.\n").encode()
    pkg = {f"package/{k}": v for k, v in out.items()}
    pkg["README.txt"] = readme(c, out, pending).encode()
    return pkg, pending, c


def readme(c, out, pending):
    code = {p: sha256((ROOT / p).read_bytes()) for p in (
        "docs/orchestration/state/2d-closeout/stageF/methods/result-package-20261109/build_package.py",
        "docs/analysis-note/make_values_fived16.py", "docs/analysis-note/values_fived16.tex",
        "docs/analysis-note/values.tex")}
    status = "INCOMPLETE" if pending else "COMPLETE"
    L = []
    w = L.append
    w("RESULT PACKAGE: the methods paper's tables and figures as data (generated by build_package.py; do not edit)")
    w("")
    w(f"STATUS: {status}." + (f" Pending: {', '.join(p for p, _ in pending)} (package/pending/)." if pending else ""))
    w("Nothing here is deposited, tagged or uploaded. Whether and where it is released is Joseph's decision.")
    w("")
    w("WHAT THIS IS")
    w("  Every file is written by build_package.py from committed records only. The build contacts no cluster and")
    w("  recomputes no result. Each record is pinned by sha256, and every written value is checked against the")
    w("  paper's own values: its \\fvval key in docs/analysis-note/values_fived16.tex (which must equal a fresh run of")
    w("  make_values_fived16.py), its macro in docs/analysis-note/values.tex, or, for a value with no key, the paper's")
    w(f"  printed text at {PAPER_REF}. Any disagreement stops the build.")
    w(f"  Files are named by the paper's LaTeX \\label at {PAPER_REF[:8]} (':' written '-'), not by table number,")
    w("  because the restructure renumbers the tables. The label map moves with the restructure (PR #977).")
    w("")
    w("REPRODUCE (from the repository root, at the commit that holds this README)")
    w("  python3 docs/orchestration/state/2d-closeout/stageF/methods/result-package-20261109/build_package.py --check")
    w("  It exits 0 only if a rebuild equals every committed file here byte for byte; --self-test plants a wrong")
    w("  value in each check family and confirms that the build refuses it. Python 3, standard library only; git is")
    w(f"  needed to read the paper at {PAPER_REF[:8]}.")
    w("")
    w("CODE (sha256)")
    for p, h in code.items():
        w(f"  {h}  {p}")
    w("  The records name the code that produced them (e.g. fd_data_product_cpl.json code_sha256:")
    for k, h in c.d["dp"]["code_sha256"].items():
        w(f"    {h}  {k}")
    w("  ).")
    w("")
    w("FILES (package/; each with its paper label, its sources, the values checked and its licence block)")
    srcmap = {k: SOURCES[k][0] for k in SOURCES}
    used = []
    for fn, label, desc, srcs, lic in FILES:
        if fn not in out:
            continue
        used += [lic] if lic not in used else []
        w("")
        w(f"* {fn}  [{label}]")
        for line in wrap(desc, 108):
            w(f"    {line}")
        for s_ in srcs:
            w(f"    source: {srcmap[s_]}")
            w(f"            sha256 {PINS[s_]}")
        n = c.n_checked.get(fn, 0)
        w(f"    checked: {n} value{'s' if n != 1 else ''} against the paper (see WHAT THIS IS)")
        if c.asym.get(fn):
            w(f"    symmetric to {c.asym[fn]:.1e} of sqrt(C_ii C_jj): floating-point rounding in the record, kept as "
              "committed")
        w(f"    licence: L-{lic}, {LIC_TITLE[lic]}")
    w("")
    w("LICENCES (each line quoted verbatim from the record named; the build stops if a quote is not there)")
    for lic in used + ["every"]:
        w("")
        w(f"L-{lic}: {LIC_TITLE[lic]}")
        for rel, head, quotes in LIC[lic]:
            where = f"{rel} at {PAPER_REF[:8]}" if rel == PAPER_PATH else rel
            w(f"  {head}")
            w(f"    {where}")
            for q in quotes:
                for i, line in enumerate(wrap(q, 102)):
                    w(f"      {'- ' if i == 0 else '  '}{line}")
    w("")
    w("IN EVERY FILE (L-every)")
    w("  No file is a coverage statement, and no file makes a measurement claim beyond the paper's.")
    w("")
    w("NOT IN THIS PACKAGE")
    w("  - The 2D per-bin result and its 205 x 205 covariance. The committed export (re2/run/partc_r2/partc-r2/outA/")
    w("    cov2d_Q_205.json.gz) holds only their shapes and sqrt-traces; the arrays are in cov2d_Q_205.npz (sha256")
    w("    7153b194b95c27f80db5997bdde35fe2475f2b1c40c9ff456edd409850cf47d2) on pscratch and in the HPSS bundle")
    w("    re2-2d-rebuild-partc-20261024. A read-only copy is drafted separately and waits for the director's go.")
    w("  - The published MINERvA result (arXiv:2106.16210), which is cited, not redistributed.")
    w("  - Table tab:outcomes as a table: it is prose drawn from about twenty records. Its numeric rows come from the")
    w("    files above.")
    w("  - Per-group 16 x 16 matrices: the committed records hold each group's relative sigma only (tab-groups16.csv).")
    w("  - Figure PDFs, and anything not committed.")
    if pending:
        w("")
        w("PENDING")
        for name, what in pending:
            for i, line in enumerate(wrap(f"{name}: {what}", 106)):
                w(f"  {'- ' if i == 0 else '  '}{line}")
    w("")
    w("SHA256SUMS lists every file here, this README and build_package.py.")
    return "\n".join(L) + "\n"


def wrap(s, n):
    words, lines, cur = s.split(), [], ""
    for x in words:
        if cur and len(cur) + 1 + len(x) > n:
            lines.append(cur)
            cur = x
        else:
            cur = f"{cur} {x}" if cur else x
    return lines + ([cur] if cur else [])


def sums(pkg, script_bytes):
    allf = dict(pkg)
    allf["build_package.py"] = script_bytes
    return "".join(f"{sha256(allf[k])}  {k}\n" for k in sorted(allf)).encode()


def write_tree(dest, pkg):
    for k, v in pkg.items():
        p = dest / k
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(v)
    (dest / "SHA256SUMS").write_bytes(sums(pkg, (HERE / "build_package.py").read_bytes()))


def committed_tree():
    got = {}
    for p in sorted((HERE / "package").rglob("*")):
        if p.is_file():
            got[str(p.relative_to(HERE))] = p.read_bytes()
    for k in ("README.txt", "SHA256SUMS"):
        if (HERE / k).exists():
            got[k] = (HERE / k).read_bytes()
    return got


PLANT = {}


def self_test():
    """Plant one wrong value per check family; each must be refused."""
    ok = True
    cases = [
        ("a source whose sha256 differs", lambda: PINS.__setitem__("g", "0" * 64)),
        ("an fvval key in the 16-cell table", lambda: PLANT.__setitem__("fv", ("f-R00", "99.9"))),
        ("an fvval key in the fake-data table", lambda: PLANT.__setitem__("fv", ("f0b-A7_gibuu-cells", "R99"))),
        ("an fvval key in the correlation table", lambda: PLANT.__setitem__("fv", ("corr-R05-R04", "0.00"))),
        ("a values.tex macro", lambda: PLANT.__setitem__("vt", ("ratioTot", "9.999"))),
        ("a printed phrase the paper does not hold", lambda: PLANT.__setitem__("paper", ("12 under both",
                                                                                          "11 under both"))),
        ("a label missing from the paper", lambda: PLANT.__setitem__("paper", (r"\label{tab:gen16}",
                                                                               r"\label{tab:genX}"))),
        ("a licence quote missing from its record", lambda: LIC["fd16"][0][2].append("a sentence no record holds")),
    ]
    for what, plant in cases:
        pins, lic = dict(PINS), {k: [(a, b, list(q)) for a, b, q in v] for k, v in LIC.items()}
        PLANT.clear()
        plant()
        try:
            assemble()
            print(f"  FAIL {what} was not refused")
            ok = False
        except Mismatch as e:
            print(f"  ok   {what} is refused: {str(e)[:110]}")
        finally:
            PINS.clear()
            PINS.update(pins)
            LIC.clear()
            LIC.update(lic)
            PLANT.clear()
    print("RESULT-PACKAGE SELF-TEST ::", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv):
    if argv[:1] == ["--self-test"]:
        return self_test()
    try:
        pkg, pending, c = assemble()
    except Mismatch as e:
        print(f"RESULT-PACKAGE :: FAIL ({e})")
        return 1
    n = sum(c.n_checked.values())
    status = f"INCOMPLETE, pending: {', '.join(p for p, _ in pending)}" if pending else "COMPLETE"
    if argv[:1] == ["--check"]:
        with tempfile.TemporaryDirectory() as t:
            write_tree(Path(t), pkg)
            fresh = {str(p.relative_to(t)): p.read_bytes() for p in sorted(Path(t).rglob("*")) if p.is_file()}
        got = committed_tree()
        diff = sorted(k for k in set(fresh) | set(got) if fresh.get(k) != got.get(k))
        if diff:
            print(f"RESULT-PACKAGE :: FAIL (the committed package differs from a rebuild: {diff[:6]})")
            return 1
        print(f"RESULT-PACKAGE :: PASS ({len(pkg) - 1} files equal a rebuild; {n} values checked) :: {status}")
        return 0
    if argv:
        print(__doc__)
        return 2
    for k in committed_tree():           # a file the new build does not write is removed, one file at a time
        if k.startswith("package/") and k not in pkg:
            (HERE / k).unlink()
    write_tree(HERE, pkg)
    print(f"RESULT-PACKAGE :: wrote {len(pkg) - 1} files and README.txt; {n} values checked :: {status}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
