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
import gzip
import hashlib
import importlib.util
import io
import json
import math
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
C2A_DIR = "docs/orchestration/state/2d-closeout/stageF/methods/result-package-20261109/receipts/c2a-20261109/transcription"

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
    "proj2d": ("2d-unfolding/pv2d/ratios/projections.json",
               "8241807f4dddf678a5b1473112f6f36b614d43cc5a4b3e932bb2d3f7d32f05c3"),
    "export2d": (f"{RE2}/outA/cov2d_Q_205.json.gz",
                 "16f663e103afeffd4cb335d9536974974243e6e310f47187517567082700d629"),
    "budget2d": (f"{RE2}/outA/budget_Q.json.gz",
                 "971e8a9d648e186212bedbfaec49642a24e0fe7f65a5e514e2a70ca78c4a5920"),
    "fig67": (f"{RE2}/fig67/fig67_projections.json",
              "85f8a194bdfd01b60abc6783e74bdeb504a3d78de20be77b6fb1b926beb30bb9"),
    "c2a-x": (f"{C2A_DIR}/cov2d_x.csv",
              "f0612bcc3bc432e90b6a1546a106043a7c525d4cae69e29ebdcec6a4505df723"),
    "c2a-Q": (f"{C2A_DIR}/cov2d_Q.csv",
              "4f07aa887c5896161f82297431a12cbdd30bdc3e11d86befb3c76648078b2d74"),
    "c2a-universe": (f"{C2A_DIR}/cov2d_universe.csv",
                     "69a0737b476866770cd27b6ca9f5e391b3e86e10ce2681f2318d2bf216cb0cb4"),
    "c2a-stat": (f"{C2A_DIR}/cov2d_stat.csv",
                 "e5f376e8f222c4ef17305ef6ba2c9b2e887d30d4e23a22109d4fc90d812e7944"),
    "c2a-c08": (f"{C2A_DIR}/cov2d_c08.csv",
                "e63cf0077477d20bc0df19fa3374bd7b983f4bac1a8fe9d678be289f95732a64"),
    "c2a-C_PL": (f"{C2A_DIR}/cov2d_C_PL.csv",
                 "6f59d683feba557c9b8fe1c035c8d208e0244ccb3e5a54b374f6124f96177483"),
    "c2a-s5_total": (f"{C2A_DIR}/cov2d_s5_total.csv",
                     "9279482548e0cd58921209cd3b9d51a98eec3e538cf2e7f215ff1f1afdb5a153"),
}
PINS = {k: v[1] for k, v in SOURCES.items()}
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
        if rel.endswith(".json.gz"):
            d[k] = json.loads(gzip.decompress(b))
        elif rel.endswith(".json"):
            d[k] = json.loads(b)
        else:
            d[k] = b.decode()
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
    cm = c.d["dp"]["relative_sigma"]["C_model_abs"]
    need(max(abs(a_ / b_ - 1) for a_, b_ in zip(cm, cols["C_model"])) < 1e-12,
         f"{fn}: C_model's relative sigma differs from the data product's C_model_abs")
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


# (quantity id, values_table row, description, unit, check): the 2D benchmark's scalars as the paper prints them
BENCH = [
    ("total_cross_section", "m-sigTwoD", "this analysis's 2D cross section integrated over the 205 reported bins",
     "cm^2/nucleon", ("macro", "sigTwoD")),
    ("ratio_to_published_total", "m-ratioTot", "that integral divided by the published one", "1",
     ("macro", "ratioTot")),
    ("chi2_over_205", "m-chiPaper", "chi^2 of the difference from the published result under the published covariance, "
     "divided by 205 (the reported bins; nothing is fitted, so 205 is the ndf)", "1", ("macro", "chiPaper")),
    ("chi2_shape_part", "tens-chi2-shape", "the shape part of that chi^2 (normalization along the published spectrum "
     "removed)", "1", ("printed", None)),
    ("chi2_normalization_part", "tens-chi2-norm", "the normalization part of that chi^2", "1", ("printed", None)),
    ("n_best_determined_directions", "tens-73-modes", "the number of best-determined eigen-directions of the published "
     "covariance kept (eigenvalues above 1e-4 of the largest)", "1", ("printed", None)),
    ("chi2_best_determined_over_205", "tens-73-chi2", "the chi^2 carried by those directions, divided by 205 "
     "(the paper's 0.66 x 205)", "1", ("printed", None)),
    ("pull_rms", "m-pullRMS", "RMS of the bin differences divided by the published uncertainties", "1",
     ("macro", "pullRMS")),
    ("median_relative_uncertainty", "m-uqMedian", "median over the 205 bins of this analysis's relative uncertainty "
     "(four-block covariance)", "percent", ("macro", "uqMedian")),
    ("integral_relative_uncertainty", "m-uqIntegral", "relative uncertainty of the integrated cross section "
     "(four-block covariance)", "percent", ("macro", "uqIntegral")),
    ("flux_band_median", "m-fluxBand", "median relative uncertainty from the leading flux band", "percent",
     ("macro", "fluxBand")),
]


def build_benchmark2d(c):
    """sec:repro2d and tab:outcomes: the 2D benchmark's scalars and the run-period rows."""
    fn = "sec-repro2d_benchmark.csv"
    vt = {r["id"]: r for r in csv.DictReader(io.StringIO(c.d["vt2d"]), delimiter="\t")}
    rows = []
    for qid, row, desc, unit, (kind, m) in BENCH:
        r = vt[row]
        need(r["status"] == "control PASS", f"{fn}: {row} status is {r['status']!r}")
        if kind == "macro":
            need(r["where"] == f"N/values.tex:\\{m}", f"{fn}: {row} is not the row for \\{m}")
            c.macro(fn, m, r["refined_rendered"])
        rows.append([qid, desc, r["refined_value"], r["refined_rendered"], unit])
    v = {k: vt[k]["refined_rendered"] for k in ("tens-chi2-shape", "tens-chi2-norm", "tens-73-modes", "tens-73-chi2")}
    c.printed(fn, rf"shape part {v['tens-chi2-shape']}, normalization part {v['tens-chi2-norm']}; the "
                  rf"{v['tens-73-modes']} best-determined directions hold ${v['tens-73-chi2']}\times205$")
    c.printed(fn, rf"$\chi^2/\mathrm{{ndf}}=\chiPaper$ over 205 bins")
    m = re.search(r"^\s*1e-04\s+([\d.]+)\s+(\d+)\s*$", c.d["tension"], re.M)
    need(m and float(m[1]) == float(vt["tens-73-chi2"]["refined_value"]) and m[2] == v["tens-73-modes"],
         f"{fn}: the tension report's rcond 1e-4 row does not give the 73-direction values")
    pr = c.d["period"]["readings"]["by_model"]["replica"]
    k73, kbar = pr["R5"], pr["R5bar"]
    need(k73["class"] == "no change" and kbar["class"].startswith("farther without"), f"{fn}: the classes changed")
    need(k73["ABC"]["k"] == 73 and kbar["ABC"]["k"] == 132, f"{fn}: the direction counts changed")
    s73, dbar = f"{k73['resolved_3sigma']:.2f}", f"{-kbar['delta']:.2f}"
    c.printed(fn, f"no change without 1G--1M (smallest resolved change {s73} per direction); other 132: farther "
                  f"without it, by {dbar}")
    rows.append(["run_periods_73_directions_smallest_resolved_change",
                 "in the 73 best-determined directions, removing the run periods 1G-1M changes the distance from the "
                 "published result by no more than noise; this is the smallest change resolvable (3 sigma), per "
                 "direction", num(k73["resolved_3sigma"]), s73, "chi^2 per direction"])
    rows.append(["run_periods_132_directions_distance_increase",
                 "in the other 132 directions, the distance from the published result without 1G-1M minus the distance "
                 "with all run periods (positive: farther without them)", num(-kbar["delta"]), dbar,
                 "chi^2 per direction"])
    return {fn: write_csv(rows, ["quantity", "description", "value", "printed", "unit"])}


C2A = "docs/orchestration/state/2d-closeout/stageF/methods/result-package-20261109/receipts/c2a-20261109/transcription"
MAT2D = [("Q", "the four-block covariance: universe + stat + training seed + run period"),
         ("universe", "systematic universes (including the normalization)"), ("stat", "statistical"),
         ("c08", "training seed"), ("C_PL", "run period"),
         ("s5_total", "universe + stat + training seed, the covariance without the run-period block")]
BUDGET_NAME = {"Q": "Q", "s5_total": "S5_total", "universe": "universe", "stat": "stat", "c08": "c08", "C_PL": "C_PL"}


def build_arrays2d(c):
    """fig:validation, fig:tension2d and sec:uq2d: the 2D result per bin and its covariance blocks, from the lossless
    transcription of cov2d_Q_205.npz, checked against the committed export, budget and projections."""
    mats = {}
    out = {}
    raw_x = c.raw["c2a-x"]
    rows = read_csv_bytes(raw_x)
    need(rows[0] == ["global_id", "x"], "cov2d_x.csv: unexpected header")
    ids = [int(r[0]) for r in rows[1:]]
    x = [float(r[1]) for r in rows[1:]]
    proj = c.d["proj2d"]
    pe, ze = proj["pt_edges"], proj["pz_edges"]
    need(ids == list(proj["reported_cells"]), "the 2D cells differ from projections.json's reported cells")
    need(len(pe) == 15 and len(ze) == 17, "the 2D grid is not 14 x 16 bins")
    n = len(ids)
    for k, _ in MAT2D:
        b = c.raw[f"c2a-{k}"]
        r_ = read_csv_bytes(b)
        need([int(v) for v in r_[0][1:]] == ids and [int(q[0]) for q in r_[1:]] == ids, f"cov2d_{k}.csv: ids")
        mats[k] = [[float(v) for v in q[1:]] for q in r_[1:]]
        out[f"sec-uq2d_{k}.csv"] = b
    exp, bud = c.d["export2d"], c.d["budget2d"]
    fnx = "sec-repro2d_result2d.csv"
    for k, _ in MAT2D:
        fn = f"sec-uq2d_{k}.csv"
        M = mats[k]
        st = math.sqrt(sum(M[i][i] for i in range(n)))
        need(abs(st / exp["arrays"][k]["sqrt_trace"] - 1) < 1e-12, f"{fn}: sqrt(trace) differs from the export's")
        rel = sorted(100 * math.sqrt(M[i][i]) / x[i] for i in range(n))
        bk = bud[BUDGET_NAME[k]]
        med = (rel[n // 2] if n % 2 else (rel[n // 2 - 1] + rel[n // 2]) / 2)
        for name, got in (("median_pct", med), ("min_pct", rel[0]), ("max_pct", rel[-1])):
            need(abs(got / bk[name] - 1) < 1e-12, f"{fn}: {name} {got!r} differs from budget_Q's {bk[name]!r}")
        c.n_checked[fn] = c.n_checked.get(fn, 0) + 4
    # Q is the sum of its blocks, s5_total of its three, exactly as the export built them
    Q, S5 = mats["Q"], mats["s5_total"]
    need(all(Q[i][j] == S5[i][j] + mats["C_PL"][i][j] for i in range(n) for j in range(n)),
         "Q is not s5_total + C_PL")
    need(all(S5[i][j] == mats["universe"][i][j] + mats["stat"][i][j] + mats["c08"][i][j]
             for i in range(n) for j in range(n)), "s5_total is not universe + stat + c08")
    # the area row, the integral and the projections against the budget, fig67 and values.tex
    pt = [i // 16 for i in ids]
    pz = [i % 16 for i in ids]
    dpt = [pe[a + 1] - pe[a] for a in pt]
    dpz = [ze[b + 1] - ze[b] for b in pz]

    def quad(f, M):
        return sum(f[i] * M[i][j] * f[j] for i in range(n) for j in range(n) if f[i] and f[j])

    area = [a * b for a, b in zip(dpt, dpz)]
    tot = sum(a * v for a, v in zip(area, x))
    vt = {r["id"]: r for r in csv.DictReader(io.StringIO(c.d["vt2d"]), delimiter="\t")}
    need(abs(tot / float(vt["m-sigTwoD"]["refined_value"]) - 1) < 1e-12, f"{fnx}: the area-weighted total differs")
    c.macro(fnx, "sigTwoD", f"{tot:.3e}")
    integ = 100 * math.sqrt(quad(area, Q)) / tot
    need(abs(integ / bud["Q"]["integral_sigma_pct"] - 1) < 1e-12, f"{fnx}: the integral sigma differs from budget_Q's")
    c.macro(fnx, "uqIntegral", f"{integ:.2f}")
    relq = sorted(100 * math.sqrt(Q[i][i]) / x[i] for i in range(n))
    c.macro(fnx, "uqMedian", f"{relq[n // 2]:.2f}")
    fig = c.d["fig67"]
    for axis, nb, sel, w, key in (("pt", 14, pt, dpz, "pt_sigma_pct"), ("pz", 16, pz, dpt, "pz_sigma_pct")):
        for k_ in range(nb):
            f = [w[i] if sel[i] == k_ else 0.0 for i in range(n)]
            if not any(f):
                continue
            s = 100 * math.sqrt(quad(f, Q)) / sum(a * v for a, v in zip(f, x))
            need(abs(s / bud["Q"][key][k_] - 1) < 1e-12, f"{fnx}: {axis} projection {k_} differs from budget_Q's")
            need(abs(s / (100 * fig[axis]["Total"][k_]) - 1) < 1e-12, f"{fnx}: {axis} projection {k_} differs from fig67")
            c.n_checked[fnx] = c.n_checked.get(fnx, 0) + 2
    rows = [[g, a, b, pe[a], pe[a + 1], ze[b], ze[b + 1], num(v)] for g, a, b, v in zip(ids, pt, pz, x)]
    out[fnx] = write_csv(rows, ["global_id", "pt_bin", "ppar_bin", "pt_lo", "pt_hi", "ppar_lo", "ppar_hi",
                                "d2sigma_dpt_dppar"])
    return out


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
    ("FD-PRR", "a study in simulation of what moves the estimator's retained prior on the 16 cells, with binned "
               "unfolding (IBU) on the same fake data"),
    ("LL5D", "the like-for-like five-observable coverage test at the two held-out GENIE v3 tunes"),
    ("V-HALF", "a per-cell validity rule: the bias at most half of the truth's departure from the prior"),
]
ENS1_PENDING = ("ENS1", "the ensemble-averaged variant of the estimator (96 fits): its stability and bias results")


def pending_text(what):
    return f"Not yet available: {what}; to be added in a later version.\n"


# ------------------------------------------------------------------------------------------------- scope of use
# SCOPE: what the README tells a reader, per file family. PROV: the verbatim lines each rests on, with the record they
# are quoted from; the build stops if a quote is not in its record (or, for the paper, in the paper at PAPER_REF).
P_ = PAPER_PATH
SCOPE = {
    "cov16": [
        "Illustrative output of the estimator on data, not a measurement; not for fitting or for constraining models.",
        "Not a coverage or calibration statement: interval coverage has not been validated.",
        "C_PL,5D was added after the data were seen and is given with and without; its size is not validated, since a "
        "block built from the observed differences contains them by construction.",
        "No statement of the cause of the run-period difference, or of which period is right."],
    "groups16": [
        "As for the 16-cell result above.",
        "C_resp does not shift neutron or muon energy deposits."],
    "fd16": [
        "Bias tests on simulated pseudo-data: no statement about data against generators, coverage, held-out truths "
        "or the detector response.",
        "No reading of the difference between the two covariance columns."],
    "tunes": [
        "A bias test at two held-out GENIE v3 tunes, not a coverage test. The paper's status for it: \"Pass; not "
        "independent\"."],
    "validity": [
        "Per-cell diagnostics of the estimator at simulated truths: not a measurement and not a coverage statement; no "
        "reported value changes, and a cell that is not valid is not thereby excluded, wrong or unreported.",
        "A1-A3 (the atlas_* columns) are this analysis's implementation of the ATLAS User Guide's thresholds, the usage "
        "recommendations the paper cites (ATLAS Collaboration, Phys. Rev. Lett. 133, 261803 (2024), arXiv:2405.20041). "
        "The guide's recommended test of correlation assumptions on pseudo-data (its item 5) is not met here.",
        "The prior_* rule and its threshold of 0.5 are this analysis's own, not ATLAS's."],
    "benchmark2d": [
        "The adopted two-dimensional result. Its coverage has been tested and not established. A fixed-truth coverage "
        "test of an earlier version of the 2D statistical band alone failed. At two held-out GENIE v3 tunes (AR23 and "
        "G18_10a_02_11b), the analysis procedure's 2D covariance, remade at each tune's truth, under-covers jointly (0 "
        "of 300 pseudo-experiments in the joint region at each). Neither test measures the reported intervals at the "
        "data's point.",
        "It does not show that the five-observable result reproduces the full distribution, beyond this benchmark with "
        "its stated limits. The paper's status for the comparison: \"Descriptive; source not identified\".",
        "The run-period rows do not say which period is right, nor the cause of the shape difference or of the "
        "run-period step."],
    "arrays2d": [
        "As for the 2D benchmark above.",
        "The four-block covariance does not include the generator-shape dependence C_model, which the paper reports as "
        "a separate covariance."],
    "illustrative": [
        "Illustrative, descriptive; not for fitting or constraining models.",
        "Not a validation of the reported covariance or of C_model, and not a generator exclusion; no reading of the "
        "figure.",
        "NuWro: the part of its free-proton sample generated at 50-100 GeV is flagged, because the events lost to "
        "generator aborts there were not shown to be negligible. GiBUU: corrected to CH with its own free-proton sample, "
        "which failed its sampling-closure check."],
    "ens1": [
        "The variant meets the stability requirement and is worse in bias at one of 17 truths, so it is not adopted; "
        "the reported estimator is unchanged. It is not a stabilised variant, and the rounding instability of the "
        "reported result is not fixed."],
}
PROV = {
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
            "added after the data were seen; published with and without"]),
        (P_, "THE PAPER", [
            "The sixteen-cell cross section the estimator gives on the data is therefore not a measurement",
            "Illustrative output on data: not for fitting or for constraining models"]),
    ],
    "groups16": [
        ("docs/orchestration/state/measurement-scoping/assigned-uncertainties/cresp/cresp.json", "LABEL (C_resp)", [
            "neutron and muon energy deposits are not shifted (D1: neutrons out)"]),
        (P_, "THE PAPER", [
            "$C_{\\mathrm{resp}}$ does not cover neutron or muon deposits, nor species, energy-dependence or resolution "
            "effects beyond a scale."]),
    ],
    "fd16": [
        (f"{FD}/FD-F0b-REPORT.md", "CITABLE FOR", ["the counts, χ² and p below, each beside its matrix"]),
        (f"{FD}/FD-F0b-REPORT.md", "NOT CITABLE FOR", [
            "any data-against-generator quantity, since F0b reads only fake-data products;",
            "coverage, held-out truths or the detector response, exactly as for F0",
            "any reading of the difference between the two columns."]),
    ],
    "tunes": [
        (f"{FD}/FD-F1-REPORT.md", "WHAT THIS IS", ["a bias test at two held-out GENIE v3 truths, not a coverage test"]),
        (P_, "THE PAPER (Table tab:outcomes, status)", ["Pass; not independent"]),
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
        (P_, "THE PAPER", [
            "The second rule is ours, not taken from Ref.~\\cite{ATLAS:2024jets}",
            "its recommended test of correlation assumptions on pseudo-data is not met here"]),
    ],
    "benchmark2d": [
        ("docs/orchestration/DECISION-20261024-joseph-adopt-re2-2d-refined.md", "DECIDED", [
            "The adopted 2D result is E_R, with Q_R as its headline uncertainty.",
            "No coverage validation is claimed for them."]),
        ("docs/orchestration/DECISION-20261109-joseph-methods-baseline-and-plan.md", "THE PAPER DOES NOT CLAIM", [
            "that 5D validates the full distribution, beyond the 2D benchmark with its stated limits;"]),
        ("docs/orchestration/OUTCOME-20261107-per-period-2d-benchmark.md", "NOT CITABLE FOR (the run-period rows)", [
            "which run period is right, that 1G–1M is wrong, or that the published result is right;",
            "a cause of the 2D shape difference or of the run-period step;"]),
        (P_, "THE PAPER (Table tab:outcomes, status)", ["Descriptive; source not identified"]),
        ("docs/orchestration/OUTCOME-20261108-cov2d-both-tunes-under-cover.md", "CITABLE FOR", [
            "At each of two held-out GENIE v3 tunes (AR23 and G18_10a_02_11b), with 300 pseudo-experiments each and the "
            "analysis procedure's 2D covariance remade at each tune's truth (model term included, run-period term "
            "excluded), the declared test reads UNDER-COVERS:",
            "the joint in-region count is 0 of 300 at both tunes;"]),
        ("docs/orchestration/OUTCOME-20261108-cov2d-both-tunes-under-cover.md", "NOT CITABLE FOR", [
            "Coverage of the reported intervals at the data's point (Q_R is made at the data, not at T)."]),
        ("docs/orchestration/OUTCOME-20261005-2d-fixed-truth-coverage-fail.md", "THE VERDICT", [
            "The verdict is FAIL-undercoverage, by the interim futility rule at toys 1–100."]),
        ("docs/orchestration/OUTCOME-20261005-2d-fixed-truth-coverage-fail.md", "NOT CITABLE FOR", [
            "the coverage of the systematic or total uncertainty;"]),
    ],
    "arrays2d": [
        ("docs/orchestration/OUTCOME-20261108-cov2d-both-tunes-under-cover.md", "CITABLE FOR", [
            "At each of two held-out GENIE v3 tunes (AR23 and G18_10a_02_11b), with 300 pseudo-experiments each and the "
            "analysis procedure's 2D covariance remade at each tune's truth (model term included, run-period term "
            "excluded), the declared test reads UNDER-COVERS:",
            "the joint in-region count is 0 of 300 at both tunes;"]),
        ("docs/orchestration/OUTCOME-20261108-cov2d-both-tunes-under-cover.md", "NOT CITABLE FOR", [
            "Coverage of the reported intervals at the data's point (Q_R is made at the data, not at T)."]),
        ("docs/orchestration/OUTCOME-20261005-2d-fixed-truth-coverage-fail.md", "THE VERDICT", [
            "The verdict is FAIL-undercoverage, by the interim futility rule at toys 1–100."]),
        ("docs/orchestration/OUTCOME-20261005-2d-fixed-truth-coverage-fail.md", "NOT CITABLE FOR", [
            "the coverage of the systematic or total uncertainty;"]),
        (P_, "THE PAPER", [
            "We report the dependence on the prior's generator shape as a separate covariance beside the four-block "
            "covariance"]),
    ],
    "illustrative": [
        (P_, "THE PAPER", ["Illustrative output on data: not for fitting or for constraining models"]),
        (f"{FD}/FD-GENCMP-AMENDMENT-E-REPORT.md", "NOT CITABLE FOR", [
            "a validation of the reported covariance or of Q_R;", "a generator exclusion;"]),
        (f"{FD}/FD-GENCMP-AMENDMENT-E-ADDENDUM-E2-REPORT.md", "NOT CITABLE FOR", [
            "a new C_model;", "a validation of C_model's coverage;"]),
        (f"{FD}/FD-G-FIGURES-REPORT.md", "NOT CITABLE FOR (the figure)", ["any reading of a figure;"]),
        (P_, "THE PAPER'S FOOTNOTES ON TWO PREDICTIONS", [
            "In NuWro's free-proton sample, the supplement generated at neutrino energies of 50--100~GeV is flagged: "
            "the events lost to generator aborts there were not shown to be negligible",
            "Corrected to CH with GiBUU's own free-proton sample",
            "That sample failed its sampling-closure check"]),
    ],
    "ens1": [
        ("docs/orchestration/OUTCOME-20261109-ens1-stab-pass-bias-worse.md", "CITABLE FOR", [
            "The consequence: the reported estimator, configuration (e), is unchanged."]),
        ("docs/orchestration/OUTCOME-20261109-ens1-stab-pass-bias-worse.md", "NOT CITABLE FOR", [
            "That E₉₆ is a stabilised variant",
            "That the rounding instability is fixed or removed for the reported result."]),
    ],
    "every": [
        (P_, "THE PAPER", [
            "Interval coverage has not been validated.",
            "The sixteen-cell cross section the estimator gives on the data is therefore not a measurement"]),
    ],
}
LIC = PROV          # the self-test plants a quote here
SCOPE_TITLE = {"cov16": "the 16-cell result and its covariance", "groups16": "the per-group uncertainties",
               "fd16": "the fake-data tests", "tunes": "the held-out tunes", "validity": "the per-cell validity rules",
               "benchmark2d": "the 2D benchmark", "arrays2d": "the 2D result per bin and its covariance",
               "illustrative": "the generator comparisons", "ens1": "the ensemble-averaged variant"}
DESCRIPTIVE = "Illustrative, descriptive; not for fitting or constraining models."


def check_licences(paper):
    for blocks in PROV.values():
        for rel, _, quotes in blocks:
            need(rel == PAPER_PATH or (ROOT / rel).is_file(), f"record missing from this checkout: {rel}")
            hay = norm(paper if rel == PAPER_PATH else (ROOT / rel).read_text())
            for q in quotes:
                need(norm(q) in hay, f"scope quote not found in {rel}: {q!r}")


# --------------------------------------------------------------------------------------------------- glossary
# (term, the README's sentence, the paper's own sentence(s) it rests on, verified at PAPER_REF)
GLOSSARY = [
    ("cell (R00-R15)", "one of the 16 reporting cells: a box in the five observables p_T, p_par, E_avail, q3 and W. "
     "The cells are boxes, not a product grid; tab-result16_cells.csv gives each box.",
     ["The largest edge on each axis is the outer edge of the analysis grid, which contains every signal event"]),
    ("f", "a cell's cross section integrated over its box, in cm^2/nucleon.",
     ["the cell-integrated cross section $f$ (an integral over the box, not a differential density)"]),
    ("g", "a generator's prediction for the same cell and quantity as f; f/g is data over prediction.",
     ["Data over prediction, $f/g$"]),
    ("C_e, C_total", "C_e holds the statistical, flux, interaction, detector, lateral and normalization groups; C_total "
     "= C_e + C_model.",
     ["The statistical, flux, interaction, detector, lateral and normalization groups, with a training-seed block that "
      "is zero in every cell, form $C_{\\mathrm{e}}$, and $C_{\\mathrm{total}}=C_{\\mathrm{e}}+C_{\\mathrm{model}}$."]),
    ("lateral", "uncertainties that shift the reconstructed muon kinematics and beam angle instead of reweighting events.",
     ["the lateral uncertainties shift the reconstructed muon kinematics and beam angle rather than reweighting events"]),
    ("C_model (C_model_abs)", "the dependence on the prior's generator shape. The data product names the matrix "
     "C_model_abs (an absolute covariance, like every matrix here); tab-groups16.csv's rel_sigma_C_model is the same "
     "matrix (checked by the build).",
     ["The model term $C_{\\mathrm{model}}$ is built from the change in the unfolded data when the prior is reweighted "
      "to GENIE + MEC, NuWro and GiBUU in turn."]),
    ("C_resp", "the response to a one-standard-deviation scale of the reconstructed recoil energy.",
     ["The response term $C_{\\mathrm{resp}}$ is the response of the result to a one-standard-deviation scale of the "
      "reconstructed recoil energy in the simulation."]),
    ("C_PL,5D", "the run-period block, added after the data were seen; files are given with and without it.",
     ["The run-period block $C_{\\mathrm{PL,5D}}$ includes this inconsistency in the reported covariance."]),
    ("reported", "the reported covariance, C_total + C_resp + C_PL,5D.",
     ["The reported covariance of the sixteen-cell result is "
      "$C_{\\mathrm{total}}+C_{\\mathrm{resp}}+C_{\\mathrm{PL,5D}}$."]),
    ("V_g", "a prediction's own finite-sample covariance (diagonal), added in every comparison with a prediction.",
     ["$V_g$, the diagonal covariance from the finite size of the prediction's own simulated sample"]),
    ("shape-only", "a chi^2 with the normalization freed (one fewer degree of freedom).",
     ["Shape-only $\\chi^2$ frees the normalization"]),
    ("fake-data chi^2, z", "the mean unfolded result at a truth against that truth, on the 16 cells; z is a cell's "
     "bias over its uncertainty under the same covariance. A truth is flagged at p < 0.01 or a cell with |z| > 2.",
     ["compare the mean unfolded result with each truth on the 16 cells through $\\chi^2$ with 16 degrees of freedom",
      "where $z$ is the cell's bias divided by its uncertainty under the same covariance"]),
    ("2D four-block covariance", "the two-dimensional result's covariance: systematic universes (with the "
     "normalization), statistical, run period and training seed.",
     ["The two-dimensional covariance is the sum of four blocks, each from LightGBM unfoldings with the central value's "
      "estimator: systematic universes (187 universes, including the normalization), statistical (300 bootstrap "
      "replicas), run period (three period groups), and training seed (five seed settings, so that its own size is "
      "poorly determined)."]),
]

# the tab-fd16 truths: each row's name as the paper's table prints it (verified); * marks the paper's closure tests
TRUTH_ROWS = {"nominal": r"simulation prior$^{*}$", "A7_mnvtune": r"Tune~v1, hybrid$^{*}$",
              "A7_genie_cv": "GENIE CV, hybrid", "A7_genie_mec": "GENIE + MEC, hybrid",
              "W2": r"GENIE + MEC, $(\Eavail,W)$ shape", "A7_nuwro": "NuWro, hybrid", "W1": r"NuWro, $\Eavail$ shape",
              "W3": r"NuWro, $(\pT,\pPar,\Eavail)$ shape", "closure_nuwro": "NuWro shape, noise-free closure",
              "stage0c_gibuu": r"GiBUU, $\Eavail$ shape", "A7_gibuu": "GiBUU, hybrid", "q3": r"synthetic $q_3$ tilt"}
CLOSURE = {"nominal", "A7_mnvtune"}

# ---------------------------------------------------------------------------------------------- the file list
# (file, label, what it is, columns {name: meaning}, sources, scope family)
CELL_HDR = {"cell": "R00-R15", "pt_lo, pt_hi; pz_lo, pz_hi; q3_lo, q3_hi": "box edges in GeV/c (pz is p_par)",
            "eavail_lo, eavail_hi; W_lo, W_hi": "box edges in GeV",
            "f": "cell-integrated cross section, cm^2/nucleon",
            "rel_sigma_<M>": "sqrt(diag M)/f for each matrix M (fraction)"}
MAT_HDR = {"cell, R00-R15": "a 16 x 16 matrix in (cm^2/nucleon)^2, rows and columns in the order R00-R15"}
FILES = [
    ("tab-result16_cells.csv", "tab:result16", "The 16 cells: each box, f, and each matrix's relative uncertainty.",
     CELL_HDR, ["dp"], "cov16"),
    ("sec-cov16_reported.csv", "sec:cov16", "The reported covariance C_total + C_resp + C_PL,5D.", MAT_HDR, ["dp"],
     "cov16"),
    ("sec-cov16_C_total_plus_C_resp.csv", "sec:cov16", "The covariance without C_PL,5D.", MAT_HDR, ["dp"], "cov16"),
    ("sec-cov16_C_e.csv", "sec:cov16", "C_e.", MAT_HDR, ["dp"], "cov16"),
    ("sec-cov16_C_model_abs.csv", "sec:cov16", "C_model.", MAT_HDR, ["dp"], "cov16"),
    ("sec-cov16_C_resp.csv", "sec:cov16", "C_resp.", MAT_HDR, ["dp"], "cov16"),
    ("sec-cov16_C_PL5D.csv", "sec:cov16", "C_PL,5D.", MAT_HDR, ["dp"], "cov16"),
    ("tab-corr16.csv", "tab:corr16", "The correlation matrix of the reported covariance.",
     {"cell, R00-R15": "a dimensionless 16 x 16 matrix, rows and columns in the order R00-R15"}, ["dp"], "cov16"),
    ("tab-groups16.csv", "tab:groups16", "Each group's relative uncertainty per cell.",
     {"cell": "R00-R15", "rel_sigma_<group>": "sqrt(diag)/f of that group (fraction; the paper prints percent); "
      "reported = C_total + C_resp + C_PL,5D"}, ["s1", "cresp", "dp"], "groups16"),
    ("tab-fd16.csv", "tab:fd16", "Fake-data tests at the 12 graded truths (see TRUTHS), under the reported covariance "
     "and under C_total.",
     {"truth": "the truth's id (see TRUTHS)",
      "<cov>_matrix": "the covariance the test uses; <cov> is reported or C_total",
      "<cov>_without_component": "when the truth is a generator that also enters C_model, that generator's component is "
                                 "removed from the covariance; this names it (empty otherwise)",
      "<cov>_chi2, _ndf, _p": "chi^2 of the mean unfolded result against the truth on the 16 cells, its degrees of "
                              "freedom and p-value",
      "<cov>_cells_abs_z_gt_2": "the cells with |z| > 2, space-separated (empty when none): a list, not a count",
      "<cov>_max_abs_z": "the largest |z| over the cells",
      "<cov>_n_pseudo_experiments": "pseudo-experiments averaged; 1 marks a noise-free closure"},
     ["f0b", "f0"], "fd16"),
    ("sec-fd16_tunes.csv", "sec:fd16", "The two held-out GENIE v3 tunes, under the reported covariance.",
     {"tune": "the GENIE v3 tune", "record": "the test: an ensemble of pseudo-experiments, or a noise-free closure",
      "matrix, chi2, ndf, p, cells_abs_z_gt_2, max_abs_z, n_pseudo_experiments": "as in tab-fd16.csv",
      "max_abs_z_cell": "the cell with the largest |z| (tab-fd16.csv has no such column)"},
     ["f1", "f1meta-g18", "f1meta-ar23"], "tunes"),
    ("sec-fd16_validity.csv", "sec:fd16", "Each cell's class under the two validity rules.",
     {"atlas_A1": "at least 5000 effective simulated events (here those of the simulation's weights)",
      "atlas_A2": "a data statistical uncertainty below 15 %",
      "atlas_A3": "|z| <= 2 at each of the 12 graded truths under the reported covariance",
      "atlas_mc_neff_truth, atlas_stat_rel": "the effective number of simulated events, and the data's relative "
                                             "statistical uncertainty (fraction), behind A1 and A2",
      "atlas_class": "valid if A1, A2 and A3 hold, else not valid",
      "prior_S_b, prior_S_g (_raw, _sub)": "the spread of the cell's fake-data bias over the graded truths (S_b) and of "
                                           "the generator predictions (S_g), each in two noise treatments",
      "prior_rho_<b>_over_<g>": "S_b / S_g in the four combinations of the two treatments",
      "prior_class": "valid if rho < 0.5 in all four, else not valid"},
     ["valid"], "validity"),
    ("sec-repro2d_benchmark.csv", "sec:repro2d", "The two-dimensional benchmark against the published result, and the "
     "run-period rows.",
     {"quantity": "an id", "description": "what it is", "value": "the full-precision value",
      "printed": "the value as the paper prints it", "unit": "its unit (1 is dimensionless)"},
     ["vt2d", "tension", "period"], "benchmark2d"),
    ("sec-repro2d_result2d.csv", "fig:validation", "The two-dimensional result on the 205 reported bins.",
     {"global_id": "pt_bin * 16 + ppar_bin", "pt_bin, ppar_bin": "bin indices from 0",
      "pt_lo, pt_hi, ppar_lo, ppar_hi": "bin edges in GeV/c",
      "d2sigma_dpt_dppar": "d^2 sigma / (dp_T dp_par) in cm^2/nucleon per (GeV/c)^2"},
     ["c2a-x", "proj2d", "export2d", "budget2d", "fig67", "vt2d"], "arrays2d"),
    *[(f"sec-uq2d_{k}.csv", "sec:uq2d", f"2D covariance block: {d}.",
       {"global_id, then the 205 ids": "a 205 x 205 matrix in (cm^2/nucleon per (GeV/c)^2)^2, rows and columns in "
                                       "the order of sec-repro2d_result2d.csv"},
       [f"c2a-{k}", "export2d", "budget2d"], "arrays2d") for k, d in MAT2D],
    ("tab-gen16.csv", "tab:gen16", f"chi^2 of each generator prediction. {DESCRIPTIVE}",
     {"prediction, label": "the prediction", "<cov>_<kind>_chi2, _ndf, _p": "<cov> is reported or without_C_PL5D; "
      "<kind> is total or shape_only (normalization freed); V_g is added to the covariance in every chi^2",
      "n_cells": "cells compared (GiBUU: the 8 cells below p_par 4.5 GeV/c)"},
     ["g", "g-nopl", "gdefs"], "illustrative"),
    ("tab-cmodel16.csv", "tab:cmodel16", f"How each prediction's chi^2 changes with C_model. {DESCRIPTIVE}",
     {"matrix, prediction, chi2_kind": "as in tab-gen16.csv",
      "chi2_carbon_ratios": "the chi^2 as reported: C_model's NuWro and GiBUU shape ratios taken from carbon (equals "
                            "tab-gen16.csv's chi^2)",
      "chi2_CH_ratios, chi2_C_model_doubled, chi2_C_model_removed": "the chi^2 with those ratios from CH, with "
                                                                    "C_model doubled, and with C_model removed",
      "delta_CH, delta_doubled, delta_removed": "each minus chi2_carbon_ratios"},
     ["e2", "e2sens"], "illustrative"),
    ("fig-ratio16.csv", "fig:ratio16", f"The data behind the ratio figure. {DESCRIPTIVE}",
     {"f_data, g_prediction": "cm^2/nucleon", "f_over_g": "data over prediction",
      "sigma_reported_over_f": "sqrt(diag reported)/f (fraction)",
      "bar_half_width": "f_over_g x sigma_reported_over_f: the data's reported uncertainty only, without V_g"},
     ["g", "figratio"], "illustrative"),
    ("sec-cov5d_ens1.csv", "sec:cov5d", "The ensemble-averaged variant (96 fits): stability and bias results.",
     {"quantity, value": "one result per row"}, ["ens1s1", "ens1s2"], "ens1"),
]
BUILDERS = [build_cov16, build_groups16, build_fd16, build_tunes, build_validity, build_benchmark2d, build_arrays2d,
            build_gen16, build_cmodel16, build_ratio16]


# ------------------------------------------------------------------------------------------------------ assemble
def assemble():
    """Return ({package path: bytes}, [pending], ctx). Raises Mismatch on any disagreement."""
    d, raw = load_sources()
    mv = load_producer()
    for k, (rel, pin) in SOURCES.items():   # the producer pins the same files: same path, its short pin a prefix
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
    for _, _, quotes in GLOSSARY:
        for q in quotes:
            need(norm(q) in c.paper_flat, f"glossary: the paper at {PAPER_REF[:8]} does not hold {q!r}")
    need(fv["f0b-all-truths"] == str(len(FD16_ROWS)), "the paper's count of graded truths is not tab-fd16's rows")
    need(list(TRUTH_ROWS) == FD16_ROWS, "TRUTH_ROWS is not tab-fd16's row order")
    for t, row in TRUTH_ROWS.items():
        need(f"\n{row} & " in paper, f"the paper's tab:fd16 has no row {row!r}")
    need(fv["trig-p"] == "0.01" and fv["trig-z"] == "2", "the flagging thresholds the README states changed")
    out = {}
    for b in BUILDERS:
        out.update(b(c))
    files, pend = build_ens1(c)
    out.update(files)
    pending = ([ENS1_PENDING] if pend else []) + PENDING
    for name, what in pending:
        out[f"pending/{name}.txt"] = pending_text(what).encode()
    pkg = {f"package/{k}": v for k, v in out.items()}
    pkg["README.txt"] = readme(c, out, pending).encode()
    pkg["PROVENANCE.txt"] = provenance(c, out, pending).encode()
    return pkg, pending, c


def detex(s):
    s = re.sub(r"\$C_\{\\mathrm\{([^}]*)\}\}\$?", r"C_\1", s)
    s = re.sub(r"C_\{\\mathrm\{([^}]*)\}\}", r"C_\1", s)
    for a, b in ((r"\Eavail", "E_avail"), (r"\pT", "p_T"), (r"\pPar", "p_par"), ("$q_3$", "q3"), ("$q_{3}$", "q3"),
                 (r"\chi^2", "chi^2"), (r"\leq", " <= "), ("Ref.~\\cite{ATLAS:2024jets}", "the ATLAS reference"),
                 ("~", " "), ("--", "-"), ("$", ""), (r"\mathsf{T}", "T")):
        s = s.replace(a, b)
    s = re.sub(r"\\SI\{([^}]*)\}\{\\percent\}", r"\1 %", s)
    return re.sub(r"\s+", " ", s).strip()


def readme(c, out, pending):
    L = []
    w = L.append
    w("RESULT PACKAGE: the tables and figures of the five-observable OmniFold methods paper, as data files")
    w("")
    w("A five-observable unbinned unfolding of MINERvA medium-energy muon-neutrino data, with a two-dimensional "
      "benchmark")
    w("against the published (p_T, p_par) result (arXiv:2106.16210). Version 1." + (
        f" Not yet included: {len(pending)} results (see pending/)." if pending else ""))
    w("")
    w("SCOPE OF USE (read first)")
    for line in wrap("The paper: \"" + detex(PROV["every"][0][2][0]) + "\" and \"" + detex(PROV["every"][0][2][1])
                     + ".\" No file in this package is a coverage statement, and no file makes a measurement claim beyond"
                     " the paper's. Each file's own scope is given with it below.", 112):
        w(f"  {line}")
    w("")
    w("LICENCE")
    w("  To be set at deposit.")
    w("")
    w("CONVENTIONS")
    for line in (
            "Cells R00-R15 are always in that order, in rows and columns alike.",
            "p_par (the muon momentum along the beam) is written pz in tab-result16_cells.csv and ppar elsewhere; momenta "
            "are in GeV/c, E_avail and W in GeV.",
            "Every rel_sigma_* and *_over_f column is a fraction, not a percent. In sec-repro2d_benchmark.csv the unit "
            "column gives each row's unit.",
            "The largest edge on each axis of a cell (4.5 GeV/c for p_T, 60 GeV/c for p_par, 100 for E_avail, q3 and W) "
            "is the outer edge of the analysis grid, which contains every signal event; it is not a cut.",
            "Numbers are written at full float64 precision. Values such as p = 1.0000000000000002 and matrices that are "
            "symmetric only to about 3e-16 of sqrt(C_ii C_jj) are floating-point rounding in the source records, kept "
            "as they are.",
            "Files are named by the paper's LaTeX label; the label-to-number map is below, to be completed at release."):
        for i, l_ in enumerate(wrap(line, 108)):
            w(f"  {'- ' if i == 0 else '  '}{l_}")
    w("")
    w("GLOSSARY")
    for term, plain, quotes in GLOSSARY:
        w(f"  {term}")
        for l_ in wrap(plain, 106):
            w(f"      {l_}")
        for q in quotes:
            for i, l_ in enumerate(wrap(f"Paper: \"{detex(q)}\"", 106)):
                w(f"      {l_}")
    w("")
    w("TRUTHS (tab-fd16.csv; * marks the paper's closure tests, where the truth is the simulation's own)")
    for t in FD16_ROWS:
        w(f"  {t:<15} {detex(TRUTH_ROWS[t]).replace('^{*}', '')}{' *' if t in CLOSURE else ''}")
    w("  All 12 are the paper's graded truths.")
    w("")
    w("FILES (package/)")
    for fn, label, what, cols, _, fam in FILES:
        if fn not in out:
            continue
        w("")
        w(f"* {fn}   [paper label {label}; table or figure number: to be completed at release]")
        for l_ in wrap(what, 108):
            w(f"    {l_}")
        for col, meaning in cols.items():
            for i, l_ in enumerate(wrap(f"{col}: {meaning}", 104)):
                w(f"    {'- ' if i == 0 else '  '}{l_}")
        w(f"    Scope: see \"{SCOPE_TITLE[fam]}\" below.")
    w("")
    w("SCOPE OF USE, BY FILE")
    seen = []
    for *_, fam in FILES:
        if fam in seen or not any(f[0] in out for f in FILES if f[5] == fam):
            continue
        seen.append(fam)
        w(f"  {SCOPE_TITLE[fam]}:")
        for line in SCOPE[fam]:
            for i, l_ in enumerate(wrap(line, 104)):
                w(f"    {'- ' if i == 0 else '  '}{l_}")
    w("")
    w("NOT INCLUDED")
    for line in ("The published MINERvA result, which is cited, not redistributed.",
                 "The paper's validation-programme table (tab:outcomes) as a table: it is a text table, and its "
                 "numerical entries are in the files above.",
                 "Per-group 16 x 16 matrices for the groups inside C_e: the source records give their relative "
                 "uncertainties only (tab-groups16.csv)."):
        for i, l_ in enumerate(wrap(line, 108)):
            w(f"  {'- ' if i == 0 else '  '}{l_}")
    if pending:
        w("")
        w("NOT YET AVAILABLE (pending/)")
        for name, what in pending:
            for i, l_ in enumerate(wrap(f"{name}.txt: {what}.", 108)):
                w(f"  {'- ' if i == 0 else '  '}{l_}")
    w("")
    w("REBUILD AND CHECK")
    w("  From the root of the source repository, at the version that holds this package:")
    w("    python3 docs/orchestration/state/2d-closeout/stageF/methods/result-package-20261109/build_package.py --check")
    for l_ in wrap("This rebuilds every file from the source records and requires each to equal the file here byte for "
                   "byte, and every value to equal the paper's printed value. It is a transcription check, not a test of "
                   "the results; it recomputes no physics. --self-test plants a wrong value in each kind of check and "
                   "confirms that the build refuses it. Python 3, standard library only. PROVENANCE.txt lists the source "
                   "records, their sha256 digests and the statements each scope rests on. SHA256SUMS lists every file.",
                   108):
        w(f"  {l_}")
    return "\n".join(L) + "\n"


def provenance(c, out, pending):
    code = {p: sha256((ROOT / p).read_bytes()) for p in (
        "docs/orchestration/state/2d-closeout/stageF/methods/result-package-20261109/build_package.py",
        "docs/analysis-note/make_values_fived16.py", "docs/analysis-note/values_fived16.tex",
        "docs/analysis-note/values.tex")}
    L = []
    w = L.append
    w("PROVENANCE: where every file of this package comes from (generated by build_package.py)")
    w("")
    w(f"PAPER: {PAPER_PATH} at commit {PAPER_REF}; file names follow its LaTeX labels.")
    w("")
    w("HOW EACH VALUE IS CHECKED")
    for l_ in wrap("Each source record is pinned by sha256. Every value written is checked against the paper's values: "
                   "its \\fvval key in docs/analysis-note/values_fived16.tex, which must equal a fresh run of "
                   "make_values_fived16.py; its macro in docs/analysis-note/values.tex; or, for a value with no key, the "
                   "paper's printed text at the commit above. The 2D arrays are also checked against the committed "
                   "export's sqrt-traces, the per-block uncertainty summary, and the pT and p_par projection "
                   "uncertainties.", 110):
        w(f"  {l_}")
    w("")
    w("CODE (sha256)")
    for p, h in code.items():
        w(f"  {h}  {p}")
    w("  The 16-cell data product names the code that produced it:")
    for k, h in c.d["dp"]["code_sha256"].items():
        w(f"    {h}  {k}")
    w("")
    w("FILES")
    for fn, label, _, _, srcs, fam in FILES:
        if fn not in out:
            continue
        n = c.n_checked.get(fn, 0)
        w(f"* {fn}  [{label}]  {n} value{'s' if n != 1 else ''} checked; scope: {SCOPE_TITLE[fam]}")
        for s_ in srcs:
            w(f"    {PINS[s_]}  {SOURCES[s_][0]}")
        if c.asym.get(fn):
            w(f"    symmetric to within {c.asym[fn]:.1e}, as |C_ij - C_ji| / sqrt(C_ii C_jj)")
    w("")
    w("THE 2D ARRAYS")
    for l_ in wrap("sec-repro2d_result2d.csv and sec-uq2d_*.csv come from cov2d_Q_205.npz (sha256 "
                   "7153b194b95c27f80db5997bdde35fe2475f2b1c40c9ff456edd409850cf47d2), the two-dimensional analysis's "
                   "export of the result and its covariance blocks on the 205 reported bins. Its lossless CSV "
                   "transcription (Python repr of each float64; every array bitwise equal after the round trip) is "
                   f"committed at {C2A}/ and pinned above. The bin edges are those of "
                   "2d-unfolding/pv2d/ratios/projections.json. Q equals s5_total + C_PL, and s5_total equals universe "
                   "+ stat + c08, exactly.", 110):
        w(f"  {l_}")
    w("")
    w("STATEMENTS EACH SCOPE RESTS ON (quoted verbatim; the build stops if a quote is not in its record)")
    fams = []
    for *_, fam in FILES:
        if fam not in fams and any(f[0] in out for f in FILES if f[5] == fam):
            fams.append(fam)
    for fam in fams + ["every"]:
        w("")
        w(f"{SCOPE_TITLE.get(fam, 'every file')}:")
        for rel, head, quotes in PROV[fam]:
            where = f"{rel} at {PAPER_REF[:8]}" if rel == PAPER_PATH else rel
            w(f"  {head} -- {where}")
            for q in quotes:
                for i, l_ in enumerate(wrap(q, 104)):
                    w(f"    {'- ' if i == 0 else '  '}{l_}")
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
    for k in ("README.txt", "PROVENANCE.txt", "SHA256SUMS"):
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
        print(f"RESULT-PACKAGE :: PASS ({len(pkg)} files equal a rebuild; {n} values checked) :: {status}")
        return 0
    if argv:
        print(__doc__)
        return 2
    for k in committed_tree():           # a file the new build does not write is removed, one file at a time
        if k.startswith("package/") and k not in pkg:
            (HERE / k).unlink()
    write_tree(HERE, pkg)
    print(f"RESULT-PACKAGE :: wrote {len(pkg)} files (package/, README.txt, PROVENANCE.txt); {n} values checked :: {status}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
