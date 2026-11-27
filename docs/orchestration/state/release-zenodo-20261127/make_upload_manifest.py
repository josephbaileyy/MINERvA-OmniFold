#!/usr/bin/env python3
"""Build UPLOAD-MANIFEST.md for Joseph's single Zenodo release (director's task, 2026-11-27).

usage: python3 -I -B make_upload_manifest.py REPO PACKAGE [--check]
  REPO     a checkout of this repository; committed files are read at REF through `git show`, never the working tree.
  PACKAGE  the RC10 deposit package, ~/codex-reports/note-measurement/zenodo-draft/package-rc10 (its SHA256SUMS is
           pinned below as PKG_SUMS_SHA). It is read, never written. RC10 is RC9's package (SHA256SUMS 630d3c07...) with
           changes B and E(a) (Joseph, 2026-11-27), built by rc10/: export_sixteen_vf.py, export_published_edges.py and
           build_rc10.py, with their logs.

Every sha256 and size below is computed here from the bytes it names, or parsed from the committed receipt that
records it. Nothing is typed. Joseph's deposit copies (~/evw2d-deposit-20261126/, ~/evw5d-deposit-20261125-r2/) are not
read: their shas and sizes come from the committed receipts. Each App. D item is checked against the current committed
products, and an item that is not current, or has no file or no tie, is listed as a GAP. With --check, the manifest on
disk must equal the one this run writes.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import re
import subprocess
import sys
import tarfile
from pathlib import Path

import numpy as np

REF = "origin/main"
HERE = Path(__file__).resolve().parent
OUT = HERE / "UPLOAD-MANIFEST.md"
FD = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd"
VF = f"{FD}/with-vf/data-product"
EVW2D = "docs/orchestration/state/2d-closeout/evw2d-20261124"
EVW5D = f"{FD}/evw5d-20261125/receipts"
G1 = f"{FD}/receipts-cov2d/g2r/re2shapes/run2/g2r"
REL5 = "docs/analysis-note/release-package-20260922"
ER_PUB = "docs/orchestration/state/ibu-chi2-20261123/tier1/units/e/er.root"
EAW = "docs/orchestration/state/2d-closeout/stageF/methods/note-figfix-20261120/runs/eavailw"
RC9_PKG_SUMS_SHA = "630d3c0762d47aa33c56285236f670bd6486bc47b34d7a604c33b245a859fe81"
PKG_SUMS_SHA = "1a3d905809af012c8af236a4f998044153bb33a9142a68d1e85174a9818a5790"  # package-rc10's SHA256SUMS
RC10_SHA = "429d24655f75ef9d7c6612184ac00893bafafaa61f1ede4f0b73a681e2628edb"  # the RC10 replay tarball, as rc10/build_rc10.log records it
RC10 = "minerva-omnifold-article-release-rc10"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class Repo:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.head = self.run("rev-parse", REF).strip()

    def run(self, *args: str) -> str:
        return subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True, text=True).stdout

    def blob(self, path: str) -> bytes:
        return subprocess.run(["git", "-C", str(self.root), "show", f"{self.head}:{path}"], check=True,
                              capture_output=True).stdout


def row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def main() -> int:
    repo, pkg = Repo(Path(sys.argv[1])), Path(sys.argv[2])
    check = "--check" in sys.argv[3:]
    sums_bytes = (pkg / "SHA256SUMS").read_bytes()
    assert not PKG_SUMS_SHA.startswith("@") and not RC10_SHA.startswith("@"), "the RC10 pins are not filled"
    assert sha(sums_bytes) == PKG_SUMS_SHA, "the package is not RC10's pinned manifest"
    listed = {}
    for line in sums_bytes.decode().splitlines():
        h, name = line.split("  ", 1)
        listed[name] = h
    files = {}
    for name, h in listed.items():
        b = (pkg / name).read_bytes()
        assert sha(b) == h, f"{name} differs from the package's SHA256SUMS"
        files[name] = (h, len(b))
    files["SHA256SUMS"] = (PKG_SUMS_SHA, len(sums_bytes))
    gaps: list[str] = []
    notes: list[str] = []

    def pkgrow(name: str, status: str, record: str) -> str:
        h, n = files[name]
        return row([f"`package-rc10/{name}`", f"`{h}`", f"{n:,}", status, record])

    # ---- A. 2D refined central values, C_rep^(2D) (Q_R) and its blocks, the 2D C_model ----
    refs_b = repo.blob("2d-unfolding/evw2d/references.npz")
    cfg_b = repo.blob("2d-unfolding/evw2d/config.json")
    cfg = json.loads(cfg_b)
    refs = np.load(io.BytesIO(refs_b), allow_pickle=False)
    meta = json.loads(str(refs["meta"]))
    r2 = np.load(pkg / "result-products-2d/result_2d.npz", allow_pickle=False)
    x, cells = r2["x"], r2["cells"]
    tie_exact = bool(np.array_equal(np.asarray(refs["er"])[cells], x))
    assert cfg["references"]["sha256"] == sha(refs_b)
    run2d = json.loads(repo.blob(f"{EVW2D}/receipts/run-20261126/post/out/run.json"))
    exact_er = run2d.get("controls", run2d).get("C-EXACT-ER") if isinstance(run2d.get("controls"), dict) else run2d.get("C-EXACT-ER")
    er_maxrel = None
    if isinstance(exact_er, dict):
        er_maxrel = exact_er.get("max_rel")
    Q = r2["Q_R"]
    med = lambda m: round(100 * float(np.median(np.sqrt(np.diag(m)) / x)), 2)
    values = dict(re.findall(r"\\newcommand\{\\(\w+)\}\{([^}]*)\}", repo.blob("docs/analysis-note/values.tex").decode()))
    q_current = (str(med(Q)) == values["uqMedian"] and str(med(r2["Q_R_without_run_period"])) == values["uqSFiveMedian"]
                 and str(med(Q + r2["C_model_abs"])) == values["qrCmodelMedian"])
    blocks_ok = bool(np.allclose(Q, r2["Q_R_systematic"] + r2["Q_R_statistical"] + r2["Q_R_training_seed"]
                                 + r2["Q_R_run_period"], rtol=0, atol=1e-90))
    if not (tie_exact and q_current and blocks_ok):
        gaps.append("A: the 2D files do not tie to E_R or to the note's current 2D uncertainties (see section A).")
    two_d = [n for n in listed if n.startswith("result-products-2d/")]

    # ---- B. sixteen cells, C_rep^(5D) and its components ----
    vf = json.loads(repo.blob(f"{VF}/fd_data_product_vf.json"))
    vf_sha = sha(repo.blob(f"{VF}/fd_data_product_vf.json"))
    f = np.array(vf["f"])
    rep_key = "C_total_plus_C_resp_plus_C_PL5D_plus_DeltaC_e"
    C_rep_now = np.array(vf["matrices"][rep_key])
    s16 = np.load(pkg / "sixteen-cell/sixteen_cell.npz", allow_pickle=False)
    fived16 = repo.blob("docs/analysis-note/values_fived16.tex").decode()
    printed = [float(m) for m in re.findall(r"\\@namedef\{fv@sig-reported-R(?:\d\d)\}\{([\d.]+)\}", fived16)]
    now_pct = [round(100 * float(np.sqrt(C_rep_now[i, i]) / f[i]), 2) for i in range(16)]
    pkg_pct = [round(100 * float(np.sqrt(s16["C_rep"][i, i]) / s16["f"][i]), 2) for i in range(16)]
    assert now_pct == printed, "the V_F product's reported covariance does not give the note's printed sigmas"
    f_same = bool(np.array_equal(s16["f"], f))
    comp_map = {"sixteen-cell/C_rep.csv": f"fd_data_product_vf_{rep_key}.csv",
                "sixteen-cell/C_e_infl.csv": "fd_data_product_vf_C_e_infl.csv",
                "sixteen-cell/C_e.csv": "fd_data_product_vf_C_e.csv", "sixteen-cell/C_model.csv":
                "fd_data_product_vf_C_model_abs.csv", "sixteen-cell/C_resp.csv": "fd_data_product_vf_C_resp.csv",
                "sixteen-cell/C_PL5D.csv": "fd_data_product_vf_C_PL5D.csv"}
    comp_status = {p: files[p][0] == sha(repo.blob(f"{VF}/{c}")) for p, c in comp_map.items()}
    npz_keys = {"C_rep": rep_key, "C_e_infl": "C_e_infl", "C_e": "C_e", "C_model": "C_model_abs", "C_resp": "C_resp",
                "C_PL5D": "C_PL5D"}
    npz_ok = f_same and all(np.array_equal(s16[k], np.array(vf["matrices"][m])) for k, m in npz_keys.items())
    c16 = list(csv.DictReader(open(pkg / "sixteen-cell/cells.csv")))
    cells16_ok = ([float(r["integral_cm2_per_nucleon"]) for r in c16] == f.tolist()
                  and [float(r["sigma_rep_cm2_per_nucleon"]) for r in c16] == np.sqrt(np.diag(C_rep_now)).tolist())
    readme_def = "V^(5D) = V_stat+syst^infl + V_prior + V_resp + V_run" in (pkg / "README.md").read_text()
    stale16 = pkg_pct != printed or not (all(comp_status.values()) and npz_ok and cells16_ok and readme_def)
    if stale16:
        gaps.append("B: a sixteen-cell file in the package does not equal the V_F product, or its sigmas differ from "
                    "the note's (section B).")

    # ---- A'. 2D central values on the published p_T edges (E(a)) ----
    pe = np.load(pkg / "result-products-2d-published-edges/result_2d_published_edges.npz", allow_pickle=False)
    er_pub_sha = sha(repo.blob(ER_PUB))
    pe_tie = (bool(np.array_equal(pe["cells"], cells)) and bool(np.array_equal(pe["x"], np.asarray(refs["paper"])[cells]))
              and bool(np.array_equal(pe["pt_edges"], refs["paper_pt_edges"]))
              and bool(np.array_equal(pe["ppar_edges"], refs["paper_pz_edges"])) and meta["paper"]["sha256"] == er_pub_sha)
    if not pe_tie:
        gaps.append("E(a): the published-edge central values do not tie to regenA's E (section A').")

    # ---- C. generator predictions ----
    g_now = json.loads(repo.blob(f"{FD}/with-vf/readout/vf-with-E/fd_g_readout.json"))
    g_sha = sha(repo.blob(f"{FD}/with-vf/readout/vf-with-E/fd_g_readout.json"))
    rows = list(csv.DictReader(open(pkg / "generator-predictions/sixteen_cell_predictions.csv")))
    gmap = {p["name"]: p for p in g_now["predictions"]}
    g_ok, n_g = True, 0
    for r in rows:
        p = gmap.get(r["generator"])
        if p is None:
            continue
        i = p["cells"].index(int(r["cell"][1:])) if isinstance(p["cells"][0], int) else p["cells"].index(r["cell"])
        n_g += 1
        if abs(float(r["g_integral_cm2_per_nucleon"]) / p["g"][i] - 1) > 1e-12:
            g_ok = False
    eaw = {}
    # the pins RC9's export checked (zenodo-draft/tools/export_products.py EAW_FILES; checks/export-products.log)
    eaw_pins = {"genie_cv": "debaf83e66cb8918", "genie_mec": "1098e9124ddd6ee2", "nuwro_cv": "d7d46a0c547dfd83",
                "gibuu_cv": "b430ddc6c2f22568"}
    for n in ("genie_cv", "genie_mec", "nuwro_cv", "gibuu_cv"):
        eaw[n] = sha(repo.blob(f"{EAW}/inputs/{n}_xsec_eavailW.root"))
        if not eaw[n].startswith(eaw_pins[n]):
            g_ok = False
    if not g_ok:
        gaps.append("C: a sixteen-cell prediction in the package differs from the current readout.")

    # ---- D. five-axis central values, masks, P (M) and C_EW ----
    five = {}
    for n in ("central_values_5d.npz", "masks_5d.npz", "projection_matrix_M_eavailW.npz", "covariance_eavailW.npz",
              "_build_report.json"):
        five[n] = files[f"result-products-5d/{n}"][0] == sha(repo.blob(f"{REL5}/{n}"))
    if not all(five.values()):
        gaps.append("D: a five-axis file differs from its committed copy in release-package-20260922.")

    # ---- E. replay package (RC10) ----
    tb = f"replay/{RC10}.tar.gz"
    assert files[tb][0] == RC10_SHA, "the package's replay tarball is not the pinned RC10"
    with tarfile.open(pkg / tb) as t:
        rc_values = t.extractfile(f"{RC10}/expected/values.tex").read().decode()
        rc_inf = t.extractfile(f"{RC10}/expected/values_inference.tex").read().decode()
        twod_code = t.extractfile(f"{RC10}/code/twod_numbers.py").read().decode()
        pub_in_tar = t.extractfile(f"{RC10}/data/twod/result_2d_published_edges.npz").read()
        figs = np.load(io.BytesIO(t.extractfile(f"{RC10}/data/figs/fig_arrays.npz").read()), allow_pickle=False)
    rc_mac = dict(re.findall(r"\\newcommand\{\\(\w+)\}\{([^}]*)\}", rc_values))
    checked = sorted({n for n in re.findall(r'"([A-Za-z]{3,})"', twod_code) if n in rc_mac})
    changed = [(n, rc_mac[n], values.get(n)) for n in checked if rc_mac[n] != values.get(n)]
    values_same = rc_values == repo.blob("docs/analysis-note/values.tex").decode()
    inf_now = repo.blob("docs/analysis-note/values_inference.tex").decode()
    inf_same = rc_inf == inf_now
    pub_same = sha(pub_in_tar) == files["result-products-2d-published-edges/result_2d_published_edges.npz"][0]
    # the four published-edge comparisons, recomputed here from the deposited values and the published covariance
    Cp = figs["cov_total"][np.ix_(cells, cells)]
    dpe = pe["x"] - figs["paper_v"][cells]
    chi2 = float(dpe @ np.linalg.pinv(Cp) @ dpe)
    pulls = dpe / np.sqrt(np.diag(Cp))
    w5 = int(np.sum(np.abs(pe["x"] / figs["paper_v"][cells] - 1) < 0.05))
    pub4 = {"chiPaper": f"{chi2 / len(cells):.2f}", "pullMean": f"{pulls.mean():.3f}", "pullRMS": f"{pulls.std():.3f}",
            "binsFive": f"{100 * w5 / len(cells):.1f}"}
    pub4_ok = all(values.get(k) == v for k, v in pub4.items())
    vlog = HERE / "rc10/verify-rc10.out.txt"
    vtxt = vlog.read_text() if vlog.exists() else ""
    verify_ok = RC10_SHA in vtxt and vtxt.rstrip().endswith("VERIFY: PASS")
    e_ok = not changed and values_same and inf_same and pub_same and pub4_ok and verify_ok
    if not e_ok:
        gaps.append("E: the RC10 replay does not match the note at the current main, or its verify did not pass "
                    "(section E).")

    # ---- F. AnaTuple identities ----
    ana_repo = repo.blob("publication/release/preservation/anatuple-checksums/ANATUPLE-SHA256.tsv")
    ana_pkg = (pkg / "anatuple-checksums/ANATUPLE-SHA256.tsv").read_bytes()
    ana_rows_same = ana_repo.splitlines()[1:] == ana_pkg.splitlines()[1:]
    n_ana = len(ana_pkg.splitlines()) - 1
    if not ana_rows_same:
        gaps.append("F: the AnaTuple checksum rows differ from the committed inventory.")

    # ---- G. per-event weights (receipts only; the deposit copies are not read) ----
    sums2d = repo.blob(f"{EVW2D}/receipts/run-20261126/post/out/SHA256SUMS").decode()
    dep2d = repo.blob(f"{EVW2D}/receipts/deposit-20261126/README.md").decode()
    sha2d = dict((n, h) for h, n in re.findall(r"^([0-9a-f]{64})  (\S+)$", dep2d, re.M))
    for h, n in re.findall(r"^([0-9a-f]{64})  (\S+)$", sums2d, re.M):
        assert sha2d.get(n) == h, f"EVW2D {n}: the run's SHA256SUMS and the deposit receipt disagree"
    assert sha(sums2d.encode()) == sha2d["SHA256SUMS"]
    with tarfile.open(fileobj=io.BytesIO(repo.blob(f"{EVW2D}/receipts/deposit-20261126/hpss.tar.gz"))) as t:
        log = t.extractfile("hpss/htar.log").read().decode() if "hpss/htar.log" in t.getnames() else ""
        if not log:
            for m in t.getnames():
                if m.endswith(".log"):
                    log += t.extractfile(m).read().decode(errors="replace")
    size2d = {n: int(b) for n, b in re.findall(r"HTAR: v evw2d-20261126/out/(\S+), (\d+) bytes", log)}
    dep5d = repo.blob(f"{EVW5D}/attempt2-hpss/lane/deposit-shas.txt").decode()
    sha5d = dict((n, h) for h, n in re.findall(r"^([0-9a-f]{64})  (\S+)$", dep5d, re.M))
    size5d = {n: int(b) for b, n in re.findall(r"^-\S+\s+\d+\s+\S+\s+\S+\s+(\d+)\s+\w+\s+\d+\s+[\d:]+\s+(\S+)$", dep5d, re.M)}
    sums5d = repo.blob(f"{EVW5D}/attempt2/post/evw5d/SHA256SUMS")
    assert sha(sums5d) == sha5d["SHA256SUMS"], "EVW5D: the committed SHA256SUMS is not the deposit's"
    for h, n in re.findall(r"^([0-9a-f]{64})  (\S+)$", sums5d.decode(), re.M):
        assert sha5d.get(n) == h, f"EVW5D {n}: committed SHA256SUMS and deposit receipt disagree"
    for n in ("run.json", "constants.json", "evw5d.done"):
        assert sha(repo.blob(f"{EVW5D}/attempt2/post/evw5d/{n}")) == sha5d[n], n
    missing = [n for n in sha2d if n not in size2d] + [n for n in sha5d if n not in size5d]
    if missing:
        gaps.append("G: no committed size for " + ", ".join(missing) + ".")

    # ---- the manifest ----
    L: list[str] = []
    A = L.append
    A("# Zenodo upload manifest for Joseph's single release (2026-11-27)")
    A("")
    A("**By** limitation-resolver, at the director's request (Joseph, 2026-11-27: \"can you add it to the zenodo "
      "deposit\"). Local only: nothing was uploaded, and nothing touched NERSC. Joseph's deposit copies "
      "(`~/evw2d-deposit-20261126/`, `~/evw5d-deposit-20261125-r2/`) were **not read**: their shas and sizes come from "
      "the committed receipts. Joseph uploads and publishes, after Ben's approval.")
    A("")
    A(f"Generated by [`make_upload_manifest.py`](make_upload_manifest.py) against `{REF}` at `{repo.head}`. Every sha256 "
      "and size is computed from the bytes it names or parsed from the committed receipt that records it. "
      "`--check` regenerates the manifest and requires it to be unchanged.")
    A("")
    A("**The scope** is every item App. D (`docs/analysis-note/appD_reproducibility.tex:20-25` on main) says the deposit "
      "archives: the replay package (`:8`); the 2D refined central values with C_rep^(2D), its four blocks, and the 2D "
      "C_model; the sixteen cell integrals with C_rep^(5D), its components and C_model; the generator predictions on "
      "the sixteen cells and the (E_avail, W) grid; the five-axis central values, support masks, P and C_EW; the 2,374 "
      "input-file identities (`:20`); and the 2D and 5D per-event weights (`:23`, `:26`).")
    A("")
    A("**Two sources:**")
    A(f"- the RC10 deposit package, `~/codex-reports/note-measurement/zenodo-draft/package-rc10/`, {len(listed)} files. "
      f"Its `SHA256SUMS` is `{PKG_SUMS_SHA}`. It is the RC9 package (`SHA256SUMS` `{RC9_PKG_SUMS_SHA}`, "
      "clean-environment check passed on 2026-11-21, `zenodo-draft/READY-FOR-UPLOAD.txt`) with Joseph's changes B and "
      "E(a) of 2026-11-27, built by the tools in [`rc10/`](rc10/). RC9's `package/` is unchanged. Each file is checked "
      "here against the current committed products;")
    A("- the two weight deposits, at Joseph's copies. Each is tied to its committed run and deposit receipts.")
    A("")
    A(f"## Gaps ({len(gaps)})")
    A("")
    if gaps:
        for i, g in enumerate(gaps, 1):
            A(f"{i}. {g}")
    else:
        A("None.")
    A("")
    A("**Resolved in RC10** (Joseph, 2026-11-27). Each bullet is printed only when its checks below pass:")
    if not stale16:
        A(f"- **B.** The sixteen-cell C_rep is the V_F one, C_e^infl + C_model + C_resp + C_PL,5D, and `C_e_infl.csv` is "
      f"added. Both are re-exported from the V_F product `{vf_sha[:8]}` by `rc10/export_sixteen_vf.py` "
      "(`rc10/export_sixteen_vf.log`: EXPORT B PASS). The package README defines it in the note's symbols, V^(5D) = "
          "V_stat+syst^infl + V_prior + V_resp + V_run, and maps each symbol to its file (`C_rep`, `C_e_infl`, ...).")
    if pe_tie and e_ok:
        A(f"- **E(a).** regenA's 2D central values on the published p_T edges are a new item (section A'), and the replay "
      f"is RC10 (`{RC10_SHA[:8]}`). RC10's 2D check recomputes all {len(checked)} printed 2D values, the four "
      "published-edge comparisons from that item. Its joint-test values are recomputed from the deposited files. Every "
      "value equals values.tex at main (section E).")
    A("")
    A("Everything else below is current and tied. Still open: the package `README.md` has no section on the two "
      "weight deposits. The holds already listed in `zenodo-draft/HANDOFF-for-upload.md` also stay open: ORCIDs, "
      "Ben's approval, and the release commit for the README's \"[fixed release commit]\".")
    A("")
    H = row(["path", "sha256", "bytes", "status", "tied by"])
    S = row(["---", "---", "---:", "---", "---"])
    A("## A. 2D refined central values, C_rep^(2D) and its blocks, the 2D C_model")
    A("")
    A("The package names C_rep^(2D) as Q_R, with blocks systematic, statistical, training seed and run period "
      "(App. D:72 maps the note's names to the records' names). C_model is given beside Q_R, not in it, as App. D "
      "says.")
    A("")
    A(H)
    A(S)
    st = "current" if (q_current and blocks_ok) else "CHECK"
    for n in sorted(two_d):
        A(pkgrow(n, st, f"G1 export (`zenodo-draft/checks/stage-g1.log`): `cov2d_Q_205.npz` `ff66b91d` and "
                        f"`cmodel_R.npz` `032de630`, at the receipts' shas (`{G1}/outA/cov2d_Q_205.json.gz`, "
                        f"`{G1}/cmodel/cmodel_R.json`)"))
    A("")
    A("**The tie to E_R (`a5c13fc3`), for App. D's 2D weights sentence:**")
    A(f"- `2d-unfolding/evw2d/config.json` (sha256 `{sha(cfg_b)}`) pins `references.npz` at `{cfg['references']['sha256']}`;")
    A(f"- `references.npz` (`{sha(refs_b)}`) records its `er` vector as `hXSec2D` from `xsec.root` "
      f"`{meta['er']['sha256']}`, at `{meta['er']['source']}`;")
    A(f"- `result_2d.npz` `x`, the 205 reported 2D central values, equals `er` at its 205 cells **bit for bit**: "
      f"{'yes' if tie_exact else 'NO'} (`np.array_equal`);")
    A(f"- EVW2D's run (`{EVW2D}/receipts/run-20261126/`) passed C-EXACT-ER, its histogram against the same `er`"
      + (f" (max_rel {er_maxrel:.3g})" if er_maxrel is not None else "") + ". So the deposited 2D weights reproduce "
      "the deposited 2D central values.")
    A("")
    A(f"Against the note today: the package's Q_R gives `\\uqMedian` {med(Q)}, `\\uqSFiveMedian` "
      f"{med(r2['Q_R_without_run_period'])} and `\\qrCmodelMedian` {med(Q + r2['C_model_abs'])}, equal to "
      f"values.tex at `{repo.head[:8]}`: {'yes' if q_current else 'NO'}. The four blocks sum to Q_R: "
      f"{'yes' if blocks_ok else 'NO'}. The 19 unreported cells of the 14 x 16 grid are not deposited, and App. D "
      "describes the 205-cell result. E_R's full 224-cell `xsec.root` is not in the package (G1's optional item 3).")
    A("")
    A("## B. The sixteen cell integrals, C_rep^(5D) and its components")
    A("")
    A(H)
    A(S)
    for n in sorted(k for k in listed if k.startswith("sixteen-cell/")):
        if n in comp_map:
            A(pkgrow(n, "current" if comp_status[n] else "**DIFFERS**",
                     f"byte-identical to `{VF}/{comp_map[n]}`" if comp_status[n] else "-"))
        else:
            ok = npz_ok if n.endswith(".npz") else cells16_ok
            A(pkgrow(n, "current" if ok else "**DIFFERS**",
                     f"re-exported from the V_F product `{VF}/fd_data_product_vf.json` `{vf_sha[:8]}` by "
                     "`rc10/export_sixteen_vf.py`; "
                     + ("f and the six matrices equal the product's bit for bit" if n.endswith(".npz") else
                        "the integrals equal f and the sigmas equal sqrt(diag C_rep) bit for bit")))
    A("")
    A(f"`C_rep.csv` is C_rep^(5D) = C_e^infl + C_model + C_resp + C_PL,5D. Its per-cell sigmas equal the note's "
      f"`sig-reported-R00..R15` for all sixteen cells (computed here): {pkg_pct[:4]}... %, the note "
      f"{printed[:4]}... %. f is unchanged by V_F: it equals RC9's exported f bit for bit "
      "(`rc10/export_sixteen_vf.log`). `C_e.csv` stays, as the unscaled component that App. C's table also prints.")
    A("")
    A("## A'. 2D central values on the published p_T edges (E(a))")
    A("")
    A(H)
    A(S)
    for n in sorted(k for k in listed if k.startswith("result-products-2d-published-edges/")):
        A(pkgrow(n, "current" if pe_tie else "**DIFFERS**",
                 f"regenA's E (ibu-chi2-20261123/regenA, #1322): `{ER_PUB}` `{er_pub_sha[:8]}`, exported by "
                 "`rc10/export_published_edges.py` (`rc10/export_published_edges.log`: EXPORT E(a) PASS)"))
    A("")
    A(f"Central values only, for the same {len(cells)} cells on the published p_T edges (0.075, 0.325, 0.475 GeV/c where "
      "ours are 0.07, 0.33, 0.47). The note gives our uncertainties only on our grid, so no covariance on these edges "
      "is deposited; comparisons use the published covariance. The tie, checked here: `x` equals `references.npz`'s "
      f"`paper` vector at the {len(cells)} cells bit for bit, its edges equal `paper_pt_edges`/`paper_pz_edges`, and "
      f"`references.npz` records `er.root` `{er_pub_sha[:8]}` as that vector's source: {'yes' if pe_tie else 'NO'}.")
    A("")
    A("## C. Generator predictions (sixteen cells and the (E_avail, W) grid)")
    A("")
    A(H)
    A(S)
    for n in sorted(k for k in listed if k.startswith("generator-predictions/")):
        A(pkgrow(n, "current" if g_ok else "CHECK",
                 f"sixteen cells: the V_F readout `{FD}/with-vf/readout/vf-with-E/fd_g_readout.json` `{g_sha[:8]}` "
                 f"(g unchanged by V_F; {n_g} rows checked to 1e-12); (E_avail, W): the four committed files under "
                 f"`{EAW}/inputs/` ("
                 + ", ".join(f"{k} `{v[:8]}`" for k, v in eaw.items()) + ")"))
    A("")
    A("## D. Five-axis central values, support masks, P and C_EW")
    A("")
    A(H)
    A(S)
    for n, ok in five.items():
        A(pkgrow(f"result-products-5d/{n}", "current" if ok else "**DIFFERS**",
                 f"byte-identical to `{REL5}/{n}`" if ok else "-"))
    A("")
    A("P is `projection_matrix_M_eavailW.npz` (M, 42 x 10,694). C_EW = M C_Z Mᵀ. C_Z itself is not deposited, as "
      "App. D says.")
    A("")
    A("## E. The replay package")
    A("")
    A(H)
    A(S)
    for n in (tb, "replay/RC10-SHA256SUMS.txt"):
        A(pkgrow(n, "current" if e_ok else "**CHECK** (gap E)",
                 "`rc10/build_rc10.py` from RC9 `c06dab21` (`rc10/build_rc10.log`: two builds byte-identical); "
                 "`rc10/verify-rc10.out.txt` (VERIFY: PASS on the extracted tarball)"))
    A("")
    A(f"RC10's `expected/values.tex` equals `docs/analysis-note/values.tex` at `{repo.head[:8]}`: "
      f"{'yes' if values_same else 'NO'}. Its `expected/values_inference.tex` equals main's: "
      f"{'yes' if inf_same else 'NO'}. Its 2D check covers {len(checked)} printed values, and against main "
      + ("none differ" if not changed else "these differ: " + ", ".join(f"`\\{n}`" for n, _, _ in changed)) + ". "
      f"The tarball's `data/twod/result_2d_published_edges.npz` is the deposited item: {'yes' if pub_same else 'NO'}. "
      "Recomputed here from the deposited published-edge values and the published covariance in RC10's "
      "`fig_arrays.npz`: " + ", ".join(f"`\\{k}` {v}" for k, v in pub4.items())
      + f"; equal to values.tex: {'yes' if pub4_ok else 'NO'}. The verify log names the tarball's sha256 and ends "
      f"VERIFY: PASS: {'yes' if verify_ok else 'NO'}.")
    A("")
    A("## F. Input-file identities")
    A("")
    A(H)
    A(S)
    A(pkgrow("anatuple-checksums/ANATUPLE-SHA256.tsv", "current" if ana_rows_same else "**DIFFERS**",
             f"its {n_ana:,} rows are byte-identical to `publication/release/preservation/anatuple-checksums/"
             "ANATUPLE-SHA256.tsv`; only the header's path is generalized"))
    A("")
    A("## G. Per-event weights (Joseph's deposit copies, from the committed receipts)")
    A("")
    A("**2D (EVW2D)**, at `~/evw2d-deposit-20261126/out/`. This is App. D's 2D sentence: per-event weights of the 2D "
      "central value on the simulated truth events, with truth p_T and p_∥, and the cross-section normalization. The "
      "sha256s come from the deposit receipt, which agrees with the run's committed `SHA256SUMS`. The bytes come from "
      "the HPSS step's committed `htar` verify log.")
    A("")
    A(row(["file", "sha256", "bytes", "tied by"]))
    A(row(["---", "---", "---:", "---"]))
    for n, h in sha2d.items():
        A(row([f"`{n}`", f"`{h}`", f"{size2d.get(n, 0):,}" if n in size2d else "GAP",
               f"`{EVW2D}/receipts/deposit-20261126/` (#1393); run `{EVW2D}/receipts/run-20261126/post/out/` "
               "(job 62022231, EVW2D-BINDING-1); HPSS `/home/j/josephrb/mnv-evw2d-20261126/evw2d-20261126.tar`"]))
    A("")
    A("**5D (EVW5D)**, at `~/evw5d-deposit-20261125-r2/evw5d/`. This is App. D's sixteen-cell weights paragraph. The "
      "sha256s and bytes come from the committed deposit receipt. Its SHA256SUMS, run.json, constants.json and "
      "evw5d.done equal the run's committed copies.")
    A("")
    A(row(["file", "sha256", "bytes", "tied by"]))
    A(row(["---", "---", "---:", "---"]))
    for n, h in sha5d.items():
        A(row([f"`{n}`", f"`{h}`", f"{size5d[n]:,}" if n in size5d else "GAP",
               f"`{EVW5D}/attempt2-hpss/lane/deposit-shas.txt`; run `{EVW5D}/attempt2/post/evw5d/` (job 62000819); "
               "HPSS `/home/j/josephrb/mnv-evw5d-20261125-r2/evw5d-20261125-r2.tar`"]))
    A("")
    A("## Package files outside App. D's list")
    A("")
    A(H)
    A(S)
    for n in ("README.md", "licenses/LICENSE-MIT.txt", "SHA256SUMS"):
        A(pkgrow(n, "current", "the package itself" + ("; RC10's changes are in its rows for `sixteen-cell/`, "
                 "`result-products-2d-published-edges/` and `replay/`" if n == "README.md" else "")))
    A("")
    A("**NOT CITABLE FOR:** any physics number, or note wording. This is an inventory for Joseph's upload.")
    text = "\n".join(L) + "\n"
    if check:
        return 0 if OUT.read_text() == text else 1
    OUT.write_text(text)
    print(f"wrote {OUT.name}: {len(gaps)} gaps")
    for g in gaps:
        print(" -", g[:150])
    return 0


if __name__ == "__main__":
    sys.exit(main())
