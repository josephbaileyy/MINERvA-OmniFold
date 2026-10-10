#!/usr/bin/env python3
"""Old-vs-new equivalence and negative controls for the 2D reported-cell family.

Builds small synthetic ROOT inputs (fixed seed), then runs the pinned scripts
(--old-uq, extracted with `git show <pin>:2d-unfolding/uq/<f>`) and the edited
ones (--new-uq) on identical operands, each as a subprocess:

  analyze_uq.py         30 replicas            -> uq_covariance.root
  analyze_universes.py  CV + 9 universes + boot -> uq_universe_covariance.root
  _ours_only_chi2.py    universe + boot vs a synthetic paper file

Compares stdout text, every ROOT object (class, title, axis edges, every bin
content and error including flow bins, entries) and every PNG byte for byte.
Then runs the negative controls (a permuted and an omitted reported cell, a
transposed identity grid, a bootstrap file with no identity) on both versions
and records exit status and whether a combined covariance was written.

The reported set of the fixture is the paper's own (StatOnly diagonal > 0 in the
tracked minerva_paper_anc text file). No production product is read.

  PYTHONPATH=$(root-config --libdir) python3.13 equivalence.py \
      --old-uq OLD/uq --new-uq REPO/2d-unfolding/uq --work SCRATCH --out result.json
"""
import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[6]
STAT_TXT = REPO / "2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV_stat.txt"
PT = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
               0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50])
PZ = np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
               6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0])
NX, NY = 14, 16
SEED = 20261009


def paper_mask():
    diag = np.zeros(NX * NY)
    with open(STAT_TXT) as f:
        r = csv.reader(f)
        next(r)
        for i, j, v in r:
            if i == j:
                diag[int(i)] = float(v)
    return (diag > 0).reshape(NX, NY)


def write_xsec(ROOT, path, a2, pt=None, pz=None):
    f = ROOT.TFile.Open(str(path), "RECREATE")
    h = ROOT.TH2D("hXSec2D", "", NX, PT, NY, PZ)
    for ix in range(NX):
        for iy in range(NY):
            h.SetBinContent(ix + 1, iy + 1, float(a2[ix, iy]))
    h.Write()
    if pt is not None:
        hp = ROOT.TH1D("hXSec_pt", "", NX, PT)
        hz = ROOT.TH1D("hXSec_pz", "", NY, PZ)
        for i in range(NX):
            hp.SetBinContent(i + 1, float(pt[i]))
        for i in range(NY):
            hz.SetBinContent(i + 1, float(pz[i]))
        hp.Write()
        hz.Write()
    f.Close()


def build(ROOT, work):
    rng = np.random.default_rng(SEED)
    P = paper_mask()
    base = np.where(P, rng.lognormal(-88.5, 1.0, (NX, NY)), 0.0)
    rep_cells = np.flatnonzero(P.ravel())
    unrep_cells = np.flatnonzero(~P.ravel())
    p0, u0 = int(rep_cells[100]), int(unrep_cells[0])

    def replicas(d, mutate=None, n=30):
        d.mkdir(parents=True)
        for i in range(1, n + 1):
            x = base * (1 + 0.05 * rng.standard_normal((NX, NY)))
            if mutate:
                x = mutate(x)
            write_xsec(ROOT, d / f"2d_xsec_TEST_5iter_lgbm_boot{i}.root", x,
                       rng.lognormal(-80, 0.5, NX), rng.lognormal(-80, 0.5, NY))

    def set_cell(x, c, v):
        x = x.copy()
        x.ravel()[c] = v
        return x

    replicas(work / "boot")
    replicas(work / "boot_perm",
             lambda x: set_cell(set_cell(x, p0, 0.0), u0, abs(x.ravel()[p0]) + 1e-40))
    replicas(work / "boot_omit", lambda x: set_cell(x, p0, 0.0))

    def sweep(d, cv):
        d.mkdir(parents=True)
        write_xsec(ROOT, d / "2d_xsec_TEST_5iter_lgbm_uni_full_CV.root", cv)
        for band, n in (("Flux", 5), ("GENIE_MaCCQE", 2), ("Muon_Energy_MINOS", 2)):
            for k in range(n):
                write_xsec(ROOT, d / f"2d_xsec_TEST_5iter_lgbm_uni_full_{band}_{k}.root",
                           cv * (1 + 0.02 * rng.standard_normal((NX, NY))))

    sweep(work / "sweep", base)
    perm_cv = set_cell(set_cell(base, p0, 0.0), u0, base.ravel()[p0])
    sweep(work / "sweep_perm", perm_cv)

    anc = work / "anc"
    anc.mkdir()
    f = ROOT.TFile.Open(str(anc / "cov_ptpl_minerva_inclusive_6GeV.root"), "RECREATE")
    hp = ROOT.TH2D("pt_pl_cross_section", "", NX, PT, NY, PZ)
    paper = base * 1.01
    for ix in range(NX):
        for iy in range(NY):
            hp.SetBinContent(ix + 1, iy + 1, float(paper[ix, iy]))
    hp.Write()
    m = ROOT.TMatrixD(NX * NY, NX * NY)
    for g in rep_cells:
        m[int(g)][int(g)] = float((0.03 * paper.ravel()[g]) ** 2)
    m.Write("StatOnlyCovariance")
    f.Close()
    write_xsec(ROOT, work / "ours.root", base)

    # A bootstrap-covariance file with neither hReportedCells nor hMean2D.
    f = ROOT.TFile.Open(str(work / "boot_noid.root"), "RECREATE")
    h = ROOT.TH2D("hCov2D_reported", "", 205, 0, 205, 205, 0, 205)
    for i in range(205):
        h.SetBinContent(i + 1, i + 1, 1e-80)
    h.Write()
    f.Close()
    return {"p0": p0, "u0": u0}


def env():
    e = dict(os.environ)
    e["PYTHONPATH"] = os.pathsep.join(filter(None, [str(REPO), e.get("PYTHONPATH", "")]))
    for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
        e[k] = "2"
    return e


def run(argv, cwd):
    p = subprocess.run(argv, cwd=cwd, env=env(), capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def ours_only(uq, work, extra):
    code = ("import sys; sys.path.insert(0, sys.argv[1]); import _ours_only_chi2 as oo; "
            "oo.ANC = sys.argv[2]; sys.argv = ['_ours_only_chi2.py'] + sys.argv[3:]; oo.main()")
    return run([sys.executable, "-c", code, str(uq), str(work / "anc"),
                "--ours", str(work / "ours.root")] + extra, work)


def dump_root(ROOT, path):
    out = {}
    f = ROOT.TFile.Open(str(path))
    for key in f.GetListOfKeys():
        o = key.ReadObj()
        rec = {"class": o.ClassName(), "title": o.GetTitle()}
        if o.InheritsFrom("TH1"):
            axes = [o.GetXaxis(), o.GetYaxis()] if o.GetDimension() == 2 else [o.GetXaxis()]
            rec["edges"] = [[a.GetBinLowEdge(i) for i in range(1, a.GetNbins() + 2)] for a in axes]
            rec["content"] = np.array([o.GetBinContent(i) for i in range(o.GetNcells())])
            rec["error"] = np.array([o.GetBinError(i) for i in range(o.GetNcells())])
            rec["entries"] = o.GetEntries()
        out[key.GetName()] = rec
    f.Close()
    return out


def compare_root(ROOT, a, b):
    da, db = dump_root(ROOT, a), dump_root(ROOT, b)
    differ = []
    for k in sorted(set(da) & set(db)):
        x, y = da[k], db[k]
        same = (x["class"] == y["class"] and x["title"] == y["title"]
                and x.get("edges") == y.get("edges") and x.get("entries") == y.get("entries"))
        for f in ("content", "error"):
            if f in x:
                same = same and np.array_equal(x[f], y[f], equal_nan=True)
        if not same:
            differ.append(k)
    return {"common": len(set(da) & set(db)), "only_old": sorted(set(da) - set(db)),
            "only_new": sorted(set(db) - set(da)), "differ": differ}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def compare_dirs(ROOT, a, b, stdout_a, stdout_b, path_a, path_b):
    files = sorted({p.name for p in Path(a).iterdir()} | {p.name for p in Path(b).iterdir()})
    res = {"stdout_equal_modulo_paths": stdout_a.replace(str(path_a), "<X>") == stdout_b.replace(str(path_b), "<X>"),
           "files": {}}
    for n in files:
        pa, pb = Path(a) / n, Path(b) / n
        if not (pa.exists() and pb.exists()):
            res["files"][n] = "only_old" if pa.exists() else "only_new"
        elif n.endswith(".root"):
            res["files"][n] = compare_root(ROOT, pa, pb)
        elif n.endswith(".txt"):
            ta = pa.read_text().replace(str(path_a), "<X>")
            tb = pb.read_text().replace(str(path_b), "<X>")
            res["files"][n] = "text_equal" if ta == tb else "text_differ"
        elif n.endswith(".pdf"):
            # matplotlib embeds the wall-clock /CreationDate; nothing else may differ.
            stamp = re.compile(rb"/CreationDate \(D:[0-9+\-Z']+\)")
            same = stamp.sub(b"", pa.read_bytes()) == stamp.sub(b"", pb.read_bytes())
            res["files"][n] = "bytes_equal_except_CreationDate" if same else "bytes_differ"
        else:
            res["files"][n] = "bytes_equal" if sha(pa) == sha(pb) else "bytes_differ"
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old-uq", required=True, type=Path)
    ap.add_argument("--new-uq", required=True, type=Path)
    ap.add_argument("--work", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()
    import ROOT
    ROOT.gROOT.SetBatch(True)
    work = a.work
    work.mkdir(parents=True, exist_ok=False)
    os.environ.setdefault("MPLCONFIGDIR", str(work / "mpl"))
    cells = build(ROOT, work)
    result = {"fixture": {"seed": SEED, **cells, "reported": int(paper_mask().sum())}}
    py = sys.executable

    # --- equivalence: analyze_uq
    outs = {}
    for tag, uq in (("old", a.old_uq), ("new", a.new_uq)):
        for b in ("boot", "boot_perm", "boot_omit"):
            od = work / f"uq_{tag}_{b}"
            rc, so, se = run([py, str(uq / "analyze_uq.py"), "--glob", str(work / b / "*.root"),
                              "--outdir", str(od)], work)
            outs[(tag, b)] = (rc, so, se, od)
    result["analyze_uq"] = {
        b: {"rc_old": outs[("old", b)][0], "rc_new": outs[("new", b)][0],
            **compare_dirs(ROOT, outs[("old", b)][3], outs[("new", b)][3],
                           outs[("old", b)][1], outs[("new", b)][1],
                           outs[("old", b)][3], outs[("new", b)][3])}
        for b in ("boot", "boot_perm", "boot_omit")}

    # --- equivalence and controls: analyze_universes
    def universes(tag, uq, sweep, boot_root, name):
        od = work / f"uni_{tag}_{name}"
        argv = [py, str(uq / "analyze_universes.py"),
                "--cv", str(work / sweep / "2d_xsec_TEST_5iter_lgbm_uni_full_CV.root"),
                "--glob", str(work / sweep / "2d_xsec_TEST_5iter_lgbm_uni_full_*.root"),
                "--add-norm", "0.014", "--outdir", str(od)]
        if boot_root:
            argv += ["--bootstrap-cov", str(boot_root)]
        rc, so, se = run(argv, work)
        root = od / "uq_universe_covariance.root"
        combined = False
        if root.exists():
            f = ROOT.TFile.Open(str(root))
            combined = bool(f.Get("hCov_combined"))
            f.Close()
        return {"rc": rc, "root_written": root.exists(), "hCov_combined": combined,
                "stdout": so, "stderr_tail": se.strip().splitlines()[-1:] if se.strip() else [],
                "dir": od}

    uni_cases = {
        # name: (sweep, bootstrap file per version)
        "matched_new_boot": ("sweep", lambda tag: work / "uq_new_boot/uq_covariance.root"),
        "matched_legacy_boot": ("sweep", lambda tag: work / "uq_old_boot/uq_covariance.root"),
        "no_boot": ("sweep", lambda tag: None),
        "perm_boot": ("sweep", lambda tag: work / f"uq_{tag}_boot_perm/uq_covariance.root"),
        "omit_boot": ("sweep", lambda tag: work / f"uq_{tag}_boot_omit/uq_covariance.root"),
        "noid_boot": ("sweep", lambda tag: work / "boot_noid.root"),
        "perm_cv_no_boot": ("sweep_perm", lambda tag: None),
    }
    uni = {}
    for name, (sweep, bootf) in uni_cases.items():
        r_old = universes("old", a.old_uq, sweep, bootf("old"), name)
        r_new = universes("new", a.new_uq, sweep, bootf("new"), name)
        rec = {"old": {k: v for k, v in r_old.items() if k not in ("stdout", "dir")},
               "new": {k: v for k, v in r_new.items() if k not in ("stdout", "dir")}}
        if r_old["root_written"] and r_new["root_written"]:
            rec["compare"] = compare_dirs(ROOT, r_old["dir"], r_new["dir"], r_old["stdout"],
                                          r_new["stdout"], r_old["dir"], r_new["dir"])
        uni[name] = rec
    result["analyze_universes"] = uni

    # --- equivalence and controls: _ours_only_chi2
    def oo_case(tag, uq, uni_dir, boot):
        extra = ["--universe-cov", str(work / uni_dir / "uq_universe_covariance.root")]
        if boot:
            extra += ["--bootstrap-cov", str(boot)]
        rc, so, se = ours_only(uq, work, extra)
        return rc, so, se

    oo_cases = {
        "matched_stored_identity": ("uni_new_no_boot", work / "uq_new_boot/uq_covariance.root"),
        "matched_legacy_universe": ("uni_old_no_boot", work / "uq_old_boot/uq_covariance.root"),
        "perm_boot_vs_paper": ("uni_new_no_boot", work / "uq_new_boot_perm/uq_covariance.root"),
        "perm_universe_vs_paper": ("uni_new_perm_cv_no_boot", work / "uq_new_boot/uq_covariance.root"),
        "noid_boot": ("uni_new_no_boot", work / "boot_noid.root"),
    }
    oo = {}
    for name, (ud, boot) in oo_cases.items():
        ro = oo_case("old", a.old_uq, ud, boot)
        rn = oo_case("new", a.new_uq, ud, boot)
        oo[name] = {"rc_old": ro[0], "rc_new": rn[0], "stdout_equal": ro[1] == rn[1],
                    "new_only_lines": [l for l in rn[1].splitlines() if l not in ro[1].splitlines()],
                    "old_last": ro[1].strip().splitlines()[-1:], "new_err": rn[2].strip().splitlines()[-1:]}
    result["ours_only_chi2"] = oo

    a.out.write_text(json.dumps(result, indent=1, default=str) + "\n")
    print(json.dumps(result, indent=1, default=str))


if __name__ == "__main__":
    main()
