#!/usr/bin/env python3
"""RE-2 J0 readout: the K1 controls, the refined-arm checks and the refinement health, as declared.

    re2_k1.py --runs j0_runs.tsv --checks j0_checks.tsv --out-dir OUT --eu E_U.root --expect-eu-sha256 S \
        --result k1.json

Each check compares the hXSec2D of a J0 output with a reference, on E_U's 205 reported cells
(``hXSec2D > 0``, C order over (pT, p||)):

* PASS when the largest relative difference is at most 1e-8 and both report the same cell set. This is the XR
  frozen-repeat criterion, which RE-1's K1-2D also used. Configuration (a) is LightGBM's non-deterministic
  mode, so equality bit for bit is reported but does not decide.
* A reference given with a sha256 is re-hashed first; a mismatch fails the check.
* ``kind = differs``: a power check. It PASSES when the largest relative difference exceeds the row's
  ``min_shift`` (1e-6 unless the row says otherwise), far above run-to-run noise, between runs on the same CPU
  count.
* ``kind = stream``: the refined background stream on the data. The test run's ``re2Refinement`` signed sum must
  equal its own ``p1Streams`` data-factor sum minus the in-range integral of the reference run's
  ``hBkgRecoStar2D`` (the purity arm's resampled background, same bootstrap seed), to 1e-9 relative.
* a row may name another histogram (``hist``, default ``hXSec2D``); it is compared the same way.

Every ``re2_driver.py`` output that ran ``--bkg-mode negweight-refined`` has its refinement health read from
``re2Refinement``. It PASSES when the clipped fraction is at most 0.01, refined/signed lies in [0.99, 1.01], and
``random_state`` is the run's ``--seed`` + 3 (the driver's rule, ``re2_driver.py:2182``; 45 at seed 42); a run with no
``--seed`` fails. A run that declares a size must also record 400 trees and 31 leaves.

The outputs are first checked against the jobs' own ``SHA256SUMS`` files beside ``--out-dir`` (``--sums-glob``:
``SHA256SUMS.J0*`` for J0, ``SHA256SUMS.J[1-8]*`` for part B).

MEASURES: the declared controls. CANNOT AUTHORIZE: a production job (the director binds J1-J8 after J0).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np

TOL = 1e-8
MIN_SHIFT = 1e-6
STREAM_TOL = 1e-9
CLIP_MAX = 0.01
RATIO_BAND = (0.99, 1.01)


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def xsec(path: Path, name: str = "hXSec2D") -> np.ndarray:
    """A 14 x 16 histogram [ix, iy] from a driver ROOT file (hXSec2D by default), or 'xsec' from an RE-1 npz."""
    if path.suffix == ".npz":
        if name != "hXSec2D":
            raise RuntimeError(f"{path} carries hXSec2D only")
        return np.asarray(np.load(path, allow_pickle=False)["xsec"], float)
    import ROOT
    f = ROOT.TFile.Open(str(path))
    if not f or f.IsZombie():
        raise RuntimeError(f"cannot open {path}")
    h = f.Get(name)
    if not h:
        raise RuntimeError(f"no {name} in {path}")
    out = np.array([[h.GetBinContent(i, j) for j in range(1, h.GetNbinsY() + 1)] for i in range(1, h.GetNbinsX() + 1)])
    f.Close()
    return out


def named_json(path: Path, name: str) -> dict | None:
    import ROOT
    f = ROOT.TFile.Open(str(path))
    t = f.Get(name)
    out = json.loads(t.GetTitle()) if t else None
    f.Close()
    return out


def refinement(path: Path) -> dict | None:
    return named_json(path, "re2Refinement")


def in_range_integral(path: Path, name: str) -> float:
    import ROOT
    f = ROOT.TFile.Open(str(path))
    h = f.Get(name)
    if not h:
        raise RuntimeError(f"no {name} in {path}")
    v = float(h.Integral())
    f.Close()
    return v


def outputs_match_sums(out_dir: Path, pattern: str = "SHA256SUMS.J0*") -> dict:
    """Every output against the jobs' SHA256SUMS files (written by the job scripts from out/)."""
    want = {}
    for p in sorted(out_dir.parent.glob(pattern)):
        for line in p.read_text().splitlines():
            digest, name = line.split(None, 1)
            want[name.strip()] = digest
    got = {n: sha256_path(out_dir / n) for n in want if (out_dir / n).is_file()}
    return {"n_listed": len(want), "mismatched": sorted(n for n in want if got.get(n) != want[n])}


def compare(a: np.ndarray, b: np.ndarray, cells: np.ndarray) -> dict:
    fa, fb = a.ravel(order="C"), b.ravel(order="C")
    rel = np.abs(fa[cells] / fb[cells] - 1.0)
    return {"max_rel": float(rel.max()), "median_rel": float(np.median(rel)),
            "same_cell_set": bool(np.array_equal(np.flatnonzero(fa > 0), cells)
                                  and np.array_equal(np.flatnonzero(fb > 0), cells)),
            "bitwise_224": bool(np.array_equal(fa, fb))}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--runs", type=Path, required=True)
    ap.add_argument("--checks", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--eu", type=Path, required=True)
    ap.add_argument("--expect-eu-sha256", required=True)
    ap.add_argument("--result", type=Path, required=True)
    ap.add_argument("--sums-glob", default="SHA256SUMS.J0*", help="the jobs' SHA256SUMS files, beside --out-dir")
    a = ap.parse_args(argv)
    if sha256_path(a.eu) != a.expect_eu_sha256:
        print("E_U digest differs", file=sys.stderr)
        return 4
    eu = xsec(a.eu)
    cells = np.flatnonzero(eu.ravel(order="C") > 0)
    if cells.size != 205:
        raise RuntimeError(f"E_U reports {cells.size} cells, not 205")
    runs = {r["label"]: r for r in csv.DictReader(open(a.runs), delimiter="\t")}
    out_of = lambda label: a.out_dir / label / "xsec.root"  # noqa: E731
    result = {"schema": "re2-j0-k1/2", "eu_sha256": a.expect_eu_sha256, "code_sha256": sha256_path(Path(__file__)),
              "tolerance": TOL, "checks": [], "health": [], "sums": outputs_match_sums(a.out_dir, a.sums_glob)}
    for c in csv.DictReader(open(a.checks), delimiter="\t"):
        test = out_of(c["test"])
        ref = out_of(c["ref"][4:]) if c["ref"].startswith("run:") else Path(c["ref"])
        row = {"id": c["id"], "kind": c["kind"], "test": c["test"], "ref": c["ref"]}
        if c.get("ref_sha256"):
            got = sha256_path(ref) if ref.is_file() else None
            row["ref_sha256_ok"] = got == c["ref_sha256"]
        try:
            check_row(row, c, test, ref, cells)
        except Exception as exc:  # an unreadable or malformed file fails its check; it never stops the readout
            row.update(verdict="FAIL", reason=f"{type(exc).__name__}: {exc}")
        result["checks"].append(row)
    for label, r in runs.items():
        if r["script"] != "re2" or "negweight-refined" not in r["args"]:
            continue
        p = out_of(label)
        try:
            ev = refinement(p) if p.is_file() else None
        except Exception:
            ev = None
        result["health"].append({"label": label, "refinement": ev, "verdict": health(ev, r["args"])})
    verdicts = [x["verdict"] for x in result["checks"] + result["health"]]
    sums_ok = result["sums"]["n_listed"] > 0 and not result["sums"]["mismatched"]
    result["verdict"] = "PASS" if verdicts and all(v == "PASS" for v in verdicts) and sums_ok else "FAIL"
    a.result.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"verdict": result["verdict"], "n_checks": len(result["checks"]),
                      "n_health": len(result["health"]),
                      "failed": [x.get("id", x.get("label")) for x in result["checks"] + result["health"]
                                 if x["verdict"] != "PASS"]}))
    return 0 if result["verdict"] == "PASS" else 1


def health(ev: dict | None, args: str) -> str:
    ok = ev is not None and ev["clipped_fraction"] <= CLIP_MAX and \
        RATIO_BAND[0] <= ev["refined_over_signed"] <= RATIO_BAND[1]
    if ok:
        seed = re.search(r"--seed\s+(\d+)", args)
        ok = seed is not None and ev["params"].get("random_state") == int(seed.group(1)) + 3
    if ok and "--refine-n-estimators" in args:
        ok = ev["params"].get("n_estimators") == 400 and ev["params"].get("num_leaves") == 31
    return "PASS" if ok else "FAIL"


def check_row(row: dict, c: dict, test: Path, ref: Path, cells: np.ndarray) -> None:
    if not test.is_file() or not ref.is_file():
        row.update(verdict="FAIL", reason="missing file")
    elif c["kind"] == "stream":
        ev, st = refinement(test), named_json(test, "p1Streams")
        b_star = in_range_integral(ref, "hBkgRecoStar2D")
        if ev is None or st is None:
            row.update(verdict="FAIL", reason="no re2Refinement or p1Streams")
        else:
            want = st["sum"]["data"] - b_star
            row.update(signed_sum=ev["signed_sum"], expected=want,
                       rel=abs(ev["signed_sum"] / want - 1.0))
            row["verdict"] = "PASS" if row["rel"] <= STREAM_TOL and ev["background_stream"] else "FAIL"
    else:
        hist = c.get("hist") or "hXSec2D"
        row["hist"] = hist
        row.update(compare(xsec(test, hist), xsec(ref, hist), cells))
        if c["kind"] == "differs":
            ok = row["max_rel"] > float(c.get("min_shift") or MIN_SHIFT)
        else:
            # the reported-cell set is a property of hXSec2D; another histogram is compared on E_U's cells only
            ok = row["max_rel"] <= TOL and (row["same_cell_set"] or hist != "hXSec2D")
        ok = ok and row.get("ref_sha256_ok", True)
        row["verdict"] = "PASS" if ok else "FAIL"


if __name__ == "__main__":
    sys.exit(main())
