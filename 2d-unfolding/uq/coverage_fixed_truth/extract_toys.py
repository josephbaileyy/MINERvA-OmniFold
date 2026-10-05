#!/usr/bin/env python3
"""Extract fixed-truth toy outputs and the production statistical band to one npz.

Reads every ``toy<T>.root`` in ``--toy-dir`` that has a ``.done`` marker, plus the
production bootstrap rollup (``uq/bootstrap_MEFHC_300/uq_covariance_boot300.root``,
ledger VL162). Writes ``--out`` (npz) and ``--out``.manifest.json (sha256 per toy file,
keyed by its absolute path on the compute host).

npz contents (arrays are ``[n_pt=14, n_pz=16]`` per toy):

* ``toy_index`` (N,), ``U`` (N,14,16) unfolded ``hXSec2D``;
* ``T`` (14,16) the fixed truth ``hTruthFixedXSec2D`` of the first toy, and
  ``T_max_abs_diff`` (N,) each toy's maximum absolute difference from it;
* ``P`` (N,14,16) each toy's bootstrapped MC truth prior ``hTruthXSec2D``, used by
  the replica-form secondary (amendment 1);
* ``prod_mean``, ``prod_sigma`` (14,16): the production rollup's ``hMean2D`` and
  ``sqrt(diag(hCov2D_reported))`` on its reported bins (zero elsewhere);
* ``reported`` (14,16) bool: ``prod_mean > 0`` (the 205 paper-reported bins).

The extraction does no scoring. A toy whose truth differs from the first toy's is
kept and flagged; the scorer refuses the whole set in that case.
"""

import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)
TOY_RE = re.compile(r"^toy(\d+)\.root$")


def th2_to_array(h):
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    a = np.zeros((nx, ny))
    for ix in range(1, nx + 1):
        for iy in range(1, ny + 1):
            a[ix - 1, iy - 1] = h.GetBinContent(ix, iy)
    return a


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_hist(path, name):
    f = ROOT.TFile.Open(str(path), "READ")
    if not f or f.IsZombie():
        raise RuntimeError(f"cannot open {path}")
    h = f.Get(name)
    if not h:
        raise RuntimeError(f"{path}: missing {name}")
    a = th2_to_array(h)
    meta = f.Get("toyMetadata")
    meta = json.loads(meta.GetTitle()) if meta else None
    f.Close()
    return a, meta


def production_band(rollup):
    mean, _ = read_hist(rollup, "hMean2D")
    cov, _ = read_hist(rollup, "hCov2D_reported")
    reported = mean > 0
    n_rep = int(reported.sum())
    if cov.shape != (n_rep, n_rep):
        raise RuntimeError(f"covariance {cov.shape} does not match {n_rep} reported bins")
    sigma = np.zeros_like(mean)
    # hCov2D_reported is ordered as the C-order ravel of the reported mask.
    sigma.ravel(order="C")[reported.ravel(order="C")] = np.sqrt(np.diag(cov))
    return mean, sigma, reported


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--toy-dir", required=True)
    ap.add_argument("--rollup", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-index", type=int, default=1)
    ap.add_argument("--max-index", type=int, default=200)
    args = ap.parse_args()

    toys = []
    for p in sorted(Path(args.toy_dir).iterdir()):
        m = TOY_RE.match(p.name)
        if m and args.min_index <= int(m.group(1)) <= args.max_index:
            if Path(str(p) + ".done").exists():
                toys.append((int(m.group(1)), p))
    toys.sort()
    if not toys:
        raise SystemExit("[FAIL] no completed toys found")

    U, P, idx, T0, dT, metas, files = [], [], [], None, [], [], {}
    for t, p in toys:
        u, meta = read_hist(p, "hXSec2D")
        tr, _ = read_hist(p, "hTruthFixedXSec2D")
        prior, _ = read_hist(p, "hTruthXSec2D")
        if meta is None or meta.get("toy") != t:
            raise SystemExit(f"[FAIL] {p}: metadata toy index {meta and meta.get('toy')} != {t}")
        if T0 is None:
            T0 = tr
        U.append(u)
        P.append(prior)
        idx.append(t)
        dT.append(float(np.max(np.abs(tr - T0))))
        metas.append(meta)
        files[str(p.resolve())] = sha256(p)

    mean, sigma, reported = production_band(args.rollup)
    np.savez(args.out, toy_index=np.array(idx), U=np.stack(U), P=np.stack(P), T=T0,
             T_max_abs_diff=np.array(dT), prod_mean=mean, prod_sigma=sigma,
             reported=reported)
    manifest = {"toy_dir": str(Path(args.toy_dir).resolve()), "n_toys": len(idx),
                "toy_index": idx, "toy_sha256": files,
                "rollup": str(Path(args.rollup).resolve()), "rollup_sha256": sha256(args.rollup),
                "npz_sha256": sha256(args.out), "toy_metadata": metas}
    Path(args.out + ".manifest.json").write_text(json.dumps(manifest, indent=1, sort_keys=True))
    print(f"[OK] {len(idx)} toys -> {args.out}; max truth diff {max(dT):.3e}; "
          f"reported bins {int(reported.sum())}")


if __name__ == "__main__":
    main()
