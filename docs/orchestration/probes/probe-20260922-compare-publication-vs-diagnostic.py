#!/usr/bin/env python3
"""Compare the PUBLICATION (E_avail,W) projection against the DIAGNOSTIC one, elementwise.

s5 of HANDOFF-20260922 records that every spectral statement about the publication
product rested on that run's stdout agreeing with the diagnostic's -- on a DIFFERENT
FILE (17,120 B vs 17,101 B). Agreement of reported statistics is not identity of
operands. This measures the operands.
"""
import hashlib, json, sys
import numpy as np


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def read(path, hist):
    import ROOT
    ROOT.gROOT.SetBatch(True)
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise SystemExit(f"[FAIL] cannot open {path}")
    h = f.Get(hist)
    if not h:
        raise SystemExit(f"[FAIL] no {hist!r} in {path}; keys="
                         f"{[k.GetName() for k in f.GetListOfKeys()]}")
    n = h.GetNbinsX()
    C = np.empty((n, n))
    for i in range(n):
        for j in range(n):
            C[i, j] = h.GetBinContent(i + 1, j + 1)
    keys = sorted(k.GetName() for k in f.GetListOfKeys())
    meta = {}
    for nm in ("runClass", "runClassStatus", "acceptanceQuestion"):
        o = f.Get(nm)
        if o:
            meta[nm] = str(o.GetTitle())
    ri = f.Get("hRowIndex")
    rows = [int(ri.GetBinContent(i + 1)) for i in range(ri.GetNbinsX())] if ri else None
    return C, keys, meta, rows


def main():
    pub, diag = sys.argv[1], sys.argv[2]
    out = sys.argv[3]
    A, ka, ma, ra = read(pub, "hCov_proj_eavail_W")
    B, kb, mb, rb = read(diag, "hCov_proj_eavail_W")
    same_shape = A.shape == B.shape
    d = {
        "publication": {"path": pub, "sha256": sha256_file(pub), "shape": list(A.shape),
                        "keys": ka, "meta": ma,
                        "matrix_sha256": hashlib.sha256(
                            np.ascontiguousarray(A, dtype="<f8").tobytes()).hexdigest()},
        "diagnostic": {"path": diag, "sha256": sha256_file(diag), "shape": list(B.shape),
                       "keys": kb, "meta": mb,
                       "matrix_sha256": hashlib.sha256(
                           np.ascontiguousarray(B, dtype="<f8").tobytes()).hexdigest()},
        "same_shape": same_shape,
        "row_index_identical": (ra == rb),
        "keys_only_in_publication": sorted(set(ka) - set(kb)),
        "keys_only_in_diagnostic": sorted(set(kb) - set(ka)),
    }
    if same_shape:
        diff = np.abs(A - B)
        with np.errstate(divide="ignore", invalid="ignore"):
            rel = np.where(np.abs(B) > 0, diff / np.abs(B), 0.0)
        d["max_abs_diff"] = float(diff.max())
        d["max_rel_diff"] = float(rel.max())
        d["bitwise_identical_matrix"] = bool(
            d["publication"]["matrix_sha256"] == d["diagnostic"]["matrix_sha256"])
        d["n_differing_elements"] = int((diff != 0).sum())
    json.dump(d, open(out, "w"), indent=2, sort_keys=True)
    print(json.dumps({k: v for k, v in d.items()
                      if k not in ("publication", "diagnostic")}, indent=2, sort_keys=True))
    print("pub  matrix_sha256 =", d["publication"]["matrix_sha256"])
    print("diag matrix_sha256 =", d["diagnostic"]["matrix_sha256"])
    print("pub  meta =", d["publication"]["meta"])
    print("diag meta =", d["diagnostic"]["meta"])
    print("wrote", out)


if __name__ == "__main__":
    main()
