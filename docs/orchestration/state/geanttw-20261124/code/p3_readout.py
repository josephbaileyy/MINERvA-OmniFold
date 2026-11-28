#!/usr/bin/env python3
"""geanttw P3's readout: C3 and R3 (../DECLARATION.md §4 P3; p2p3/AMENDMENT-P2P3.md A3, D2 ruling (a)).

    python3 p3_readout.py extract --repo REPO --outs P3_OUT --out VECTORS.npz [--slims pin ...]   (cluster, ROOT)
    python3 p3_readout.py c3 --repo REPO --vectors VECTORS.npz --json C3.json      (numpy only)
    python3 p3_readout.py r3 --repo REPO --vectors VECTORS.npz --c3 C3.json --json R3.json

extract: each unfold's 205 reported-cell vector, by S5's own `Cells` (s5_rollup.py, imported from REPO, which
         reads E_U and checks its sha256), from P3_OUT/<slim>/GEANT_<b>_<i>/xsec.root for the named slims. With pin,
         it also reads S5's own July GEANT unfolds (sweeps.json's pn/GEANT_*). sweeps.json and each July file are
         sha-checked through O_NOATIME. A sidecar VECTORS.npz.json records every xsec.root's sha256 and the July
         files.
c3:      C3 PASS needs both of these, each with rel = max|a - b| / max|b| <= 1e-10:
         (i) each pinned universe vector equals S5's July vector for that universe;
         (ii) for each GEANT band, C = build_repair.wcov(X, 1) over the pinned pair (s5_rollup's band_cov) equals
         production_cov.npz's band_GEANT_<b>.
         A covariance alone cannot see a common shift or a swapped pair, so (i) is required too.
         NOT REPRODUCED if the run completes but misses either. FAIL if a band is non-finite or not PSD, or if the
         cells or areas are not S5's. On PASS it records the pinned outputs' sha256s, which the override unfolds
         require.
r3:      only on C3 PASS (the director's term 1: no patched number is read otherwise). The pinned side is S5's bands.
         R3a: per cell, sigma_c of each band and of G = their sum, for pinned+override and patched+override, with
         the 13 tail cells named and recomputed. R3b: the patch's effect, with T' = T + (G_patov - G_pinov), giving
         dmedian and dintegral, and the same per band and for G. The proxy's removal, G_pinov - G_pin, is reported
         separately. Caveat 1 is discharged only if, in all 13 tail cells, sigma_c(G_patov) <= 1.10 x
         sigma_c(G_pinov); a 0 pinned cell needs a 0 patched cell. The sanity STOP is a non-finite sigma_c of either
         G, a patched G with sigma_c 0 where the pinned G's is > 0, or any override band that is not finite and
         PSD. r3 also refuses unless the vectors' six pinned outputs are the ones c3.json recorded.
sigma_c = sqrt(C_cc) / x_c x 100 and sigma_int = sqrt(a'Ca) / (x.a) x 100 (2D-CLOSURE-A1 §1), with x = cells_x_EU
and a = area. Exit 0 done, 1 a STOP or FAIL, 2 unusable.
"""
import argparse
import importlib.util
import json
import sys
import types
from pathlib import Path

import numpy as np

BANDS = ("Neutron", "Pion", "Proton")
NOATIME_OPTIONAL = False   # set by the tests only
SLIMS = ("pin", "pinov", "patov")
PROD = "docs/orchestration/state/2d-closeout/stageC/production/evidence/production/results/production_cov.npz"
PROD_SHA = "6689d2fc2a795a72e66ee953a32d94c7906dd81a866771979f379c5f163a9ddc"
S5 = "docs/orchestration/state/2d-closeout/stageC/production/s5_rollup.py"
BR = "docs/orchestration/state/2d-closeout/c04-repair/scripts/build_repair.py"
TOL = 1e-10
TAIL = (195, 203, 193, 1, 0, 194, 182, 183, 201, 202, 184, 196, 192)   # ../DECLARATION.md R3a
TAIL_RATIO = 0.3
CAVEAT_REL = 1.10


class Unusable(Exception):
    pass


def npz(path):
    """Every array of an npz, read now, so an object (pickled) array refuses here rather than never being looked at."""
    with np.load(path, allow_pickle=False) as z:
        return {k: z[k] for k in z.files}


def load(name, path, stub_root):
    saved = sys.modules.get("ROOT")
    if stub_root:
        class _Any:
            def __getattr__(self, n):
                return _Any()

            def __call__(self, *a, **k):
                return _Any()
        m = types.ModuleType("ROOT")
        m.__getattr__ = lambda n: _Any()
        sys.modules["ROOT"] = m
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        if stub_root:
            if saved is None:
                sys.modules.pop("ROOT", None)
            else:
                sys.modules["ROOT"] = saved
    return mod


def prod(repo):
    import hashlib
    p = Path(repo) / PROD
    if hashlib.sha256(p.read_bytes()).hexdigest() != PROD_SHA:
        raise Unusable(f"{p} is not production_cov.npz {PROD_SHA[:8]}")
    return npz(p)


def sig_c(C, x):
    return np.sqrt(np.diag(C)) / x * 100


def sig_int(C, x, a):
    return float(np.sqrt(a @ C @ a) / (x @ a) * 100)


def sha_noatime(path):
    import hashlib
    import os
    flag = getattr(os, "O_NOATIME", None)
    if flag is None and not NOATIME_OPTIONAL:
        raise Unusable("this Python has no O_NOATIME")
    h = hashlib.sha256()
    with os.fdopen(os.open(str(path), os.O_RDONLY | (flag or 0)), "rb") as fh:
        for b in iter(lambda: fh.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def extract(a):
    s5 = load("s5_rollup", Path(a.repo) / S5, stub_root=False)
    if s5.sha(s5.PIN["E_U"][0]) != s5.PIN["E_U"][1]:
        raise Unusable("E_U is not S5's")
    cells = s5.Cells()
    vec = {"cells_x": cells.x, "area": cells.area}
    side = {"xsec_sha256": {}, "july": {}}
    if not set(a.slims) <= set(SLIMS):   # argparse's nargs="+" makes it non-empty
        raise Unusable(f"--slims must be among {SLIMS}, got {a.slims}")
    if set(a.slims) - {"pin"}:   # the director's term 1: no override vector is read without C3 bound to its outputs
        if not a.c3:
            raise Unusable("extracting an override slim needs --c3, a PASSing c3.json")
        c3rep = json.loads(Path(a.c3).read_text())
        want = c3rep.get("pin_xsec_sha256") or {}
        live = {f"pin:{b}_{i}": sha_noatime(Path(a.outs) / "pin" / f"GEANT_{b}_{i}" / "xsec.root")
                for b in BANDS for i in (0, 1)}
        if c3rep.get("verdict") != "PASS" or len(want) != 6 or want != live:
            raise Unusable("C3 is not PASS, or the pinned outputs are not the ones it passed: no override is read")
    for s in a.slims:
        for b in BANDS:
            for i in (0, 1):
                x = Path(a.outs) / s / f"GEANT_{b}_{i}" / "xsec.root"
                side["xsec_sha256"][f"{s}:{b}_{i}"] = sha_noatime(x)
                vec[f"{s}:{b}_{i}"] = cells.vec(x)
    if "pin" in a.slims:   # S5's own July unfolds, for C3's per-universe comparison (sweeps.json, sha-checked)
        sj, sj_sha = s5.PIN["sweeps_json"]
        if sha_noatime(sj) != sj_sha:
            raise Unusable("sweeps.json is not S5's")
        recs = json.loads(Path(sj).read_text())
        for b in BANDS:
            for i in (0, 1):
                r = recs[f"pn/GEANT_{b}_{i}"]
                if sha_noatime(r["path"]) != r["sha256"]:
                    raise Unusable(f"the July file {r['path']} is not sweeps.json's {r['sha256'][:8]}")
                side["july"][f"{b}_{i}"] = {"path": r["path"], "sha256": r["sha256"]}
                vec[f"july:{b}_{i}"] = cells.vec(r["path"])
    np.savez(a.out, **vec)
    side["npz_sha256"] = sha_noatime(a.out)   # binds the sidecar's hashes to these arrays
    Path(str(a.out) + ".json").write_text(json.dumps(side, indent=1, sort_keys=True))
    print(f"extracted {len(vec) - 2} vectors to {a.out}")
    return 0


def finite_psd(C):
    finite = bool(np.isfinite(C).all())
    return finite, finite and float(np.linalg.eigvalsh(C).min()) >= -1e-12 * float(np.abs(C).max())


def bands_of(v, slim, wcov):
    return {b: wcov(np.stack([v[f"{slim}:{b}_0"], v[f"{slim}:{b}_1"]]), np.ones(2)) for b in BANDS}


def vectors_and_side(path):
    """The vectors and their sidecar, only if the sidecar's npz_sha256 is this npz's."""
    side = json.loads(Path(str(path) + ".json").read_text())
    if side.get("npz_sha256") != sha_noatime(path):
        raise Unusable(f"{path} is not the npz its sidecar recorded")
    return npz(path), side


def c3(a):
    v, side = vectors_and_side(a.vectors)
    z = prod(a.repo)
    br = load("build_repair", Path(a.repo) / BR, stub_root=True)
    rep = {"bands": {}}
    if not (np.array_equal(v["cells_x"], z["cells_x_EU"]) and np.array_equal(v["area"], z["area"])):
        rep["verdict"] = "FAIL"
        rep["reason"] = "the extracted cells or areas are not S5's"
    else:
        C = bands_of(v, "pin", br.wcov)
        bad, far = [], []
        rep["universes"] = {}
        for b in BANDS:   # each pinned unfold against S5's own July unfold: a covariance cannot see a shift or a swap
            for i in (0, 1):
                j, x = v[f"july:{b}_{i}"], v[f"pin:{b}_{i}"]
                r = float(np.abs(x - j).max() / np.abs(j).max())
                rep["universes"][f"{b}_{i}"] = r
                if not (np.isfinite(r) and r <= TOL):
                    far.append(f"{b}_{i}")
        for b in BANDS:
            S = z[f"band_GEANT_{b}"]
            finite, psd = finite_psd(C[b])
            r = float(np.abs(C[b] - S).max() / np.abs(S).max()) if finite else float("nan")
            rep["bands"][b] = {"rel": r, "finite": finite, "psd": psd}
            if not psd:   # finite_psd's psd is False whenever finite is
                bad.append(b)
        if bad:
            rep["verdict"], rep["reason"] = "FAIL", f"non-finite or non-PSD band(s) {bad}"
        else:
            rep["verdict"] = "PASS" if all(rep["bands"][b]["rel"] <= TOL for b in BANDS) and not far else "NOT REPRODUCED"
            rep["pin_xsec_sha256"] = {k: h for k, h in side["xsec_sha256"].items() if k.startswith("pin:")}
            rep["july"] = side["july"]
    for b, r in rep["bands"].items():
        print(f"C3 band_GEANT_{b}: rel {r['rel']:.3e} finite {r['finite']} psd {r['psd']}")
    for u, r in rep.get("universes", {}).items():
        print(f"C3 GEANT_{u} vs S5's July unfold: rel {r:.3e}")
    print(f"C3 {rep['verdict']}" + (f": {rep['reason']}" if "reason" in rep else ""))
    Path(a.json).write_text(json.dumps(rep, indent=1, sort_keys=True))
    return 0 if rep["verdict"] != "FAIL" else 1


def r3(a):
    c3rep = json.loads(Path(a.c3).read_text())
    if c3rep.get("verdict") != "PASS":
        raise Unusable(f"C3 is {c3rep.get('verdict')!r}, not PASS: no patched number is read (the director's term 1)")
    v, side = vectors_and_side(a.vectors)
    want = c3rep.get("pin_xsec_sha256") or {}
    got = {k: h for k, h in side.get("xsec_sha256", {}).items() if k.startswith("pin:")}
    if len(want) != 6 or got != want:
        raise Unusable("the vectors' pinned outputs are not the six C3 passed: no patched number is read")
    z = prod(a.repo)
    br = load("build_repair", Path(a.repo) / BR, stub_root=True)
    x, ar, T = z["cells_x_EU"], z["area"], z["total"]
    B = {s: bands_of(v, s, br.wcov) for s in SLIMS}
    bad_bands = [f"{s}:{b}" for s in ("pinov", "patov") for b in BANDS if not all(finite_psd(B[s][b]))]
    B["pin"] = {b: z[f"band_GEANT_{b}"] for b in BANDS}   # C3 PASSed: the pinned side is S5's own
    G = {s: sum(B[s][b] for b in BANDS) for s in SLIMS}
    # the tail cells, recomputed from S5's G and T, must be the declaration's
    gS = sig_c(sum(z[f"band_GEANT_{b}"] for b in BANDS), x)
    tail = sorted(int(c) for c in np.flatnonzero(gS / sig_c(T, x) > TAIL_RATIO))
    rep = {"c3": c3rep["verdict"], "pinned_side": "S5",
           "tail_recomputed": tail, "tail_matches_declaration": tail == sorted(TAIL)}
    sp, so = sig_c(G["pinov"], x), sig_c(G["patov"], x)
    Tp = T + (G["patov"] - G["pinov"])
    stp = sig_c(Tp, x)
    nonfinite = ~(np.isfinite(sp) & np.isfinite(so) & np.isfinite(stp))   # stp also catches a negative T' variance
    stop = [int(c) for c in range(len(x)) if nonfinite[c] or (sp[c] > 0 and not so[c] > 0)]
    rep["R3a"] = {"sigma_c": {s: {k: sig_c(m, x).tolist() for k, m in {**B[s], "G": G[s]}.items()} for s in SLIMS}}
    rep["R3b_patch"] = {
        "dmedian": float(np.median(sig_c(Tp, x)) - np.median(sig_c(T, x))),
        "dintegral": sig_int(Tp, x, ar) - sig_int(T, x, ar),
        "per_band_dmedian": {k: float(np.median(sig_c(B["patov"][k] if k != "G" else G["patov"], x))
                                      - np.median(sig_c(B["pinov"][k] if k != "G" else G["pinov"], x)))
                             for k in BANDS + ("G",)},
    }
    rep["proxy_removal"] = {"per_cell_G_sigma_c_delta": (sig_c(G["pinov"], x) - sig_c(G["pin"], x)).tolist(),
                            "dmedian_G": float(np.median(sig_c(G["pinov"], x)) - np.median(sig_c(G["pin"], x)))}
    open_cells = [c for c in TAIL if not ((sp[c] == 0 and so[c] == 0) or (sp[c] > 0 and so[c] <= CAVEAT_REL * sp[c]))]
    rep["caveat1"] = {"discharged": not open_cells, "open_cells": open_cells,
                      "ratio": {c: (float(so[c] / sp[c]) if sp[c] > 0 else None) for c in TAIL}}
    rep["sanity_stop_cells"] = stop
    rep["nonfinite_or_not_psd_bands"] = bad_bands
    Path(a.json).write_text(json.dumps(rep, indent=1, sort_keys=True))
    print(f"R3 pinned side {rep['pinned_side']}; tail recomputed == declared {rep['tail_matches_declaration']}")
    print(f"R3b patch: dmedian {rep['R3b_patch']['dmedian']:+.6f} pp, dintegral {rep['R3b_patch']['dintegral']:+.6f} pp")
    print(f"proxy removal: G dmedian {rep['proxy_removal']['dmedian_G']:+.6f} pp")
    print(f"caveat 1 {'DISCHARGED' if not open_cells else 'OPEN ' + str(open_cells)}")
    if stop or bad_bands or not rep["tail_matches_declaration"]:
        print(f"R3 STOP: sanity cells {stop}; bands not finite and PSD {bad_bands}; "
              f"tail matches {rep['tail_matches_declaration']}")
        return 1
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("extract")
    for n in ("--repo", "--outs", "--out"):
        e.add_argument(n, required=True)
    e.add_argument("--slims", nargs="+", default=list(SLIMS))
    e.add_argument("--c3", help="c3.json; required for any override slim")
    c = sub.add_parser("c3")
    for n in ("--repo", "--vectors", "--json"):
        c.add_argument(n, required=True)
    r = sub.add_parser("r3")
    for n in ("--repo", "--vectors", "--c3", "--json"):
        r.add_argument(n, required=True)
    a = ap.parse_args(argv)
    try:
        return {"extract": extract, "c3": c3, "r3": r3}[a.cmd](a)
    except Unusable as err:
        print(f"UNUSABLE: {err}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
