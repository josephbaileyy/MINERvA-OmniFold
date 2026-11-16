#!/usr/bin/env python3
"""T2A (fd/tier2-20261110/T2A-COV2D-SPLIT-DECLARATION.md §3-4, bound by T2-BINDING-1.md): at one tune, from the captured
error matrix E (300 x 205) and the committed blocks_<T>.npz, the mean chi2 split into e-bar^T C+ e-bar and tr(C+ S)
(S at ddof 0), the whitened components by eigen-rank of C_T, and the joint test truncated to C_T's top 73 and 139
eigenpairs against nulls drawn on the bound null's own draw stream.

Controls, each fail-closed (exit 8 and <out stem>.STOP.json; no reading is written):
  pins  every input at its sha256; the null modules at their sha256; E_<T>.npz's sha256 is capture_<T>.json's, whose
        status is OK with A0 equal;
  A1    from E: chi2_nonnull(E, C_T)'s ndf equals the score's grade.ndf exactly; its mean / ndf equals
        grade.chi2_mean_over_ndf to A1_CHI2_TOL (relative; see the constant); per-cell pull mean and sd (ddof 1) equal
        grade.pull_mean / pull_sd to 1e-12 (absolute floor 1e-12 x the largest |value|); in-interval counts exact;
  A2    e-bar^T C+ e-bar + tr(C+ S) equals the mean of chi2_nonnull(E, C_T), and sum_k b_k, sum_k f_k equal the two
        parts, all to 1e-12 relative;
  A4    E is 300 finite rows of 205 in TOY_SEEDS order (the npz's seeds);
  A1's chi2 tolerance is COV2D A5's rule (T2-BINDING-1 addendum 1); the pulls stay at 1e-12, counts and ndf exact.
  A3    (before any truncated number is written) the full-rank null rebuilt here reproduces null_<T>.json's q_joint
        within one se_joint, with chi2_cut and ndf exactly equal; the size it was checked at is recorded (N_MC draws in
        chunks of nl.CHUNK).

The null (T2-BINDING-1 ruling 2): one pass over fd_1b_null.null_contents' own loop: default_rng(cov2d.NULL_SEED), chunks
of fd_1b_null.CHUNK, fd_1b_null.simulate on cov2d_null.laws_at_T's laws and the same Gaussian (C_stat + C_norm + C08 +
C_model_abs). Each chunk gives the full-rank statistic (for A3) and the rank-73 and rank-139 statistics on the SAME
draws, so the draw sequence is exactly the bound null's, and no array holds more than one chunk (100,000 x 205 float64,
164 MB). Run under python -I from outside the input directories.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

PINS = {
    "AR23": {"blocks": "abaebaeae6c9cb075dcb974a420dbf148809d01b2cabc8deda31f318bf6715ee",
             "score": "fe5263e904f65892ce26b75fb279441230713c38675c2a3615c59d561c4f5ce1",
             "null": "80274e52c23365e5c6f84fad977576e54507bf186e1d04a8da8d596a75b0ac76",
             "capture": "e30f6b9301a3a7db94953e1a8e2a5b767483e80b4f8cca637caf5c3381e0600c"},
    "G18": {"blocks": "7eb657b82ae953bdf0584eda27264c52a64bcb48baea52dfc194f5efe440ea3d",
            "score": "849766942b3ecd9e6e72fd5db9d1a59815796b3f917875f8d0122b0c639088ec",
            "null": "6bd5259d61b062af7b3a8b09af78fc544e3eba48e35a062a28fdcd923b90f6e0",
            "capture": "3e954247c48115c953c6aa62bb33f47cbaca2193bf75ca3169e022fc40bc1da4"},
}
MODULE_PINS = {"nd-unfolding/fd_1b_null.py": "ec1402db5cbb5ca3002d7e45a714319d90a8b93654005d688b304a69caab4d38",
               "2d-unfolding/cov2d/cov2d_null.py": "a92c0506d1ff86f497ee9d2c5bbb884aaed93320d2b7d5551f84885ad8a561b2",
               "2d-unfolding/cov2d/cov2d.py": "76cbceba395bc6bbf8fc5cce9cf44fc0f21354dff8591cbdee578e0fddcaf8ed"}
RANKS = (73, 139)
REL = 1e-12
N_MC = None             # None: fd_1b_null.N_MC (2,000,000), as T2A §3 declares; a test may lower it on the module
A1_CHI2_TOL = "A5"      # T2-BINDING-1 addendum 1: COV2D A5's max(1e-9, 10 kappa_2(C_T) eps) for A1's chi2 comparison
UNRESOLVED = 0.01       # addendum 1's precision readout: a rank whose driver difference exceeds 1% is marked unresolved


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def allclose(a, b, rel=REL) -> bool:
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != b.shape or not (np.all(np.isfinite(a)) and np.all(np.isfinite(b))):
        return False
    return bool(np.allclose(a, b, rtol=rel, atol=rel * (float(np.max(np.abs(b))) if b.size else 0.0)))


def relerr(a, b) -> float:
    return abs(float(a) / float(b) - 1.0) if float(b) != 0 else abs(float(a))


def a1_chi2_tol(C):
    """The A1 chi2 tolerance as ruled: either a number, or "A5" for COV2D's max(1e-9, 10 kappa_2(C_T) eps)."""
    if A1_CHI2_TOL == "A5":
        lam = np.linalg.eigvalsh(np.asarray(C, np.float64))
        eps = float(np.finfo(np.float64).eps)
        kappa = float(lam[-1] / lam[0]) if lam[0] > 0 else float("inf")
        return {"rule": "max(1e-9, 10 kappa_2(C_T) eps)", "kappa2": kappa, "tol": max(1e-9, 10 * kappa * eps)}
    if isinstance(A1_CHI2_TOL, float):
        return {"rule": f"{A1_CHI2_TOL:g} relative", "tol": A1_CHI2_TOL}
    raise SystemExit(f"A1_CHI2_TOL is not set: {A1_CHI2_TOL!r}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--truth", required=True, choices=sorted(PINS))
    ap.add_argument("--e-npz", required=True, type=Path)
    ap.add_argument("--capture", required=True, type=Path)
    ap.add_argument("--blocks", required=True, type=Path)
    ap.add_argument("--score", required=True, type=Path)
    ap.add_argument("--null", required=True, type=Path)
    ap.add_argument("--code", required=True, type=Path, help="a git archive of the score M (nd-unfolding, 2d-unfolding)")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--fig", type=Path)
    a = ap.parse_args(argv)
    T = a.truth
    controls, stop = {}, []

    def control(name, ok, detail=None):
        controls[name] = {"pass": bool(ok), **({"detail": detail} if detail is not None else {})}
        if not ok:
            stop.append(name)

    rec = {"schema": "t2a/1", "truth": T, "declaration": "T2A-COV2D-SPLIT-DECLARATION.md", "binding": "T2-BINDING-1.md",
           "label": "descriptive only: no new verdict, no cause, no coverage statement at the data's point",
           "inputs_sha256": {}, "inputs_paths": {}}

    def finish(rc):
        rec["controls"] = controls
        p = a.out if rc == 0 else a.out.with_name(a.out.stem + ".STOP.json")
        p.write_text(json.dumps(rec, indent=1) + "\n")
        print(f"T2A {T} {'OK' if rc == 0 else 'STOP'} rc={rc} -> {p}; controls failed: {stop}")
        return rc

    # pins
    for key, path in (("blocks", a.blocks), ("score", a.score), ("null", a.null), ("capture", a.capture)):
        got = sha(path)
        rec["inputs_sha256"][key] = got
        rec["inputs_paths"][key] = str(path)
        control(f"pin {key}", got == PINS[T][key])
    for rel_, s in MODULE_PINS.items():
        got = sha(a.code / rel_)
        rec["inputs_sha256"][rel_] = got
        control(f"pin {rel_}", got == s)
    cap = json.loads(a.capture.read_text())
    e_sha = sha(a.e_npz)
    rec["inputs_sha256"]["E_npz"] = e_sha
    rec["inputs_paths"]["E_npz"] = str(a.e_npz)
    control("E_npz is the capture's, and the capture is OK with A0 equal",
            e_sha == cap.get("e_npz_sha256") and cap.get("status") == "OK" and cap.get("A0", {}).get("equal") is True
            and cap.get("truth") == T)
    if stop:
        return finish(8)

    for p in (a.code / "nd-unfolding", a.code / "2d-unfolding" / "cov2d"):
        sys.path.insert(0, str(p))
    import cov2d as c          # noqa: E402
    import cov2d_null as cn    # noqa: E402
    import fd_1b_null as nl    # noqa: E402
    n_mc = nl.N_MC if N_MC is None else int(N_MC)

    B = np.load(a.blocks, allow_pickle=False)
    C = np.asarray(B["C_T"], np.float64)
    with np.load(a.e_npz, allow_pickle=False) as z:
        E = np.asarray(z["E"], np.float64)
        seeds = [int(s) for s in z["seeds"]]
    score = json.loads(a.score.read_text())
    g = score["grade"]
    nrec = json.loads(a.null.read_text())

    # A4
    control("A4", E.shape == (300, 205) and bool(np.all(np.isfinite(E))) and seeds == list(c.TOY_SEEDS[T]),
            {"shape": list(E.shape), "seeds_first_last": [seeds[0], seeds[-1]] if seeds else None})
    if stop:
        return finish(8)

    # A1
    chi2, ndf = nl.chi2_nonnull(E, C)
    sigma = np.sqrt(np.diag(C))
    Zc = E / sigma
    inside = np.sum(np.abs(E) <= sigma, axis=0)
    tol = a1_chi2_tol(C)
    a1 = {"ndf": [int(ndf), int(g["ndf"])],
          "chi2_mean_over_ndf_rel_diff": relerr(chi2.mean() / ndf, g["chi2_mean_over_ndf"]), "chi2_tol": tol,
          "pull_mean": allclose(Zc.mean(axis=0), g["pull_mean"]),
          "pull_sd": allclose(Zc.std(axis=0, ddof=1), g["pull_sd"]),
          "counts": [int(x) for x in inside] == [int(x) for x in g["counts"]]}
    control("A1", ndf == g["ndf"] and a1["chi2_mean_over_ndf_rel_diff"] <= tol["tol"] and a1["pull_mean"]
            and a1["pull_sd"] and a1["counts"], a1)
    if stop:
        return finish(8)

    # the eigenbasis: the non-null subspace of chi2_nonnull, ordered by descending eigenvalue
    lam, V = np.linalg.eigh(C)
    keep = lam > nl.RANK_REL * lam.max()
    order = np.argsort(lam[keep])[::-1]
    lk, Vk = lam[keep][order], V[:, keep][:, order]
    if lk.size != ndf:
        control("eigenbasis rank equals ndf", False, {"rank": int(lk.size), "ndf": int(ndf)})
        return finish(8)
    Z = (E @ Vk) / np.sqrt(lk)
    zbar = Z.mean(axis=0)
    b_k = zbar ** 2
    f_k = Z.var(axis=0)                                   # ddof 0
    ebar = E.mean(axis=0)
    R = E - ebar
    S = R.T @ R / E.shape[0]                              # ddof 0
    Cp = (Vk / lk) @ Vk.T
    part_mean = float(ebar @ Cp @ ebar)
    part_spread = float(np.trace(Cp @ S))
    m = float(chi2.mean())
    a2 = {"sum_rel_diff": relerr(part_mean + part_spread, m), "b_k_rel_diff": relerr(b_k.sum(), part_mean),
          "f_k_rel_diff": relerr(f_k.sum(), part_spread)}
    control("A2", all(v <= REL for v in a2.values()), a2)
    if stop:
        return finish(8)

    # A3 and the truncated nulls, on the bound null's draw stream
    laws = cn.laws_at_T({k[len("band__"):]: B[k] for k in B.files if k.startswith("band__")}, B["minos_x"], B["w_flux"])
    gauss = B["C_stat"] + B["C_norm"] + B["C08"] + B["C_model_abs"]
    match = nl.check_matched(laws, gauss, C)
    cut = nl.chi2_ppf(nl.P0, ndf)
    cuts = {k: nl.chi2_ppf(nl.P0, k) for k in RANKS}
    top = max(RANKS)
    Vt, lt = Vk[:, :top], lk[:top]
    rng = np.random.default_rng(c.NULL_SEED)
    joint, jk, done = 0, {k: 0 for k in RANKS}, 0
    while done < n_mc:
        mm = min(nl.CHUNK, n_mc - done)
        Ed = nl.simulate(laws, gauss, mm, rng)
        joint += int(np.sum(nl.chi2_nonnull(Ed, C)[0] <= cut))
        Zd = (Ed @ Vt) / np.sqrt(lt)
        Zd *= Zd
        for k in RANKS:
            jk[k] += int(np.sum(np.sum(Zd[:, :k], axis=1) <= cuts[k]))
        done += mm
        del Ed, Zd
    q = joint / n_mc
    se = float(np.sqrt(q * (1 - q) / n_mc))
    nn = nrec["null"]
    a3 = {"q_joint_rebuilt": q, "se_joint_rebuilt": se, "q_joint_record": nn["q_joint"], "se_joint_record": nn["se_joint"],
          "abs_diff": abs(q - nn["q_joint"]), "chi2_cut": [cut, nn["chi2_cut"]], "ndf": [int(ndf), int(nn["ndf"])],
          "checked_at": {"n_mc": n_mc, "chunk": int(nl.CHUNK), "seed": int(c.NULL_SEED)}, "match_rel": match}
    control("A3", abs(q - nn["q_joint"]) <= nn["se_joint"] and cut == nn["chi2_cut"] and ndf == nn["ndf"], a3)
    if stop:
        return finish(8)

    # the results
    counts_1e4 = int(np.sum(lam / lam.max() > 1e-4))
    counts_1e6 = int(np.sum(lam / lam.max() > 1e-6))
    trunc = {}
    for k in RANKS:
        qk = jk[k] / n_mc
        null_k = {"p_cell": np.asarray(nn["p_cell"], float), "se_cell": np.asarray(nn["se_cell"], float), "q_joint": qk,
                  "se_joint": float(np.sqrt(qk * (1 - qk) / n_mc))}
        thr = nl.thresholds(null_k, n=E.shape[0])
        size = nl.size(null_k, thr)
        x = np.sum(Z[:, :k] ** 2, axis=1)
        cnt = int(np.sum(x <= cuts[k]))
        trunc[str(k)] = {"rank": k, "chi2_cut": cuts[k], "in_region_count": cnt, "of": int(E.shape[0]),
                         "k_joint": int(thr["k_joint"]), "at_or_below_k_joint": bool(cnt <= thr["k_joint"]),
                         "null_q": qk, "null_se": null_k["se_joint"], "null_size_joint": size["joint"],
                         "mean_chi2_over_rank": float(x.mean() / k),
                         "mean_part_over_rank": float(b_k[:k].sum() / k), "spread_part_over_rank": float(f_k[:k].sum() / k)}
    unresolved = None
    rec["split"] = {"ndf": int(ndf), "mean_chi2": m, "mean_chi2_over_ndf": m / ndf,
                    "ebar_Cplus_ebar": part_mean, "trace_Cplus_S": part_spread,
                    "ebar_Cplus_ebar_over_ndf": part_mean / ndf, "trace_Cplus_S_over_ndf": part_spread / ndf,
                    "share_of_ebar_Cplus_ebar": part_mean / m,
                    "label": "mean chi2 = ebar^T C+ ebar (the mean error's part) + tr(C+ S) (the spread's part), S ddof 0"}
    rec["by_rank"] = {"label": "k = 1..ndf by descending eigenvalue of C_T; b_k = mean(z_k)^2, f_k = var(z_k) (ddof 0)",
                      "lambda_over_lambda1": (lk / lk[0]).tolist(), "b_k": b_k.tolist(), "f_k": f_k.tolist(),
                      "cumulative_at": {str(k): {"b": float(b_k[:k].sum()), "f": float(f_k[:k].sum())}
                                        for k in (*RANKS, int(ndf))}}
    # addendum 1, descriptive: the precision readout, numpy eigh against scipy eigh(driver="evr") on the same C_T and E
    import scipy
    import scipy.linalg as sl
    lam2, V2 = sl.eigh(C, driver="evr")
    keep2 = lam2 > nl.RANK_REL * lam2.max()
    o2 = np.argsort(lam2[keep2])[::-1]
    lk2, Vk2 = lam2[keep2][o2], V2[:, keep2][:, o2]
    prec = {"label": "descriptive (T2-BINDING-1 addendum 1): numpy eigh against scipy.linalg.eigh(driver='evr'); per rank "
                     "d_k = max(|b_k - b_k'|, |f_k - f_k'|) / (b_k + f_k), the component's mean square under numpy's "
                     "basis (b_k, f_k are invariant to an eigenvector's sign); a rank with d_k > 1% is numerically "
                     "unresolved, and no reading is made from it",
            "numpy": np.__version__, "scipy": scipy.__version__, "ndf_numpy": int(ndf), "ndf_evr": int(lk2.size)}
    if lk2.size == ndf:
        Z2 = (E @ Vk2) / np.sqrt(lk2)
        b2, f2 = Z2.mean(axis=0) ** 2, Z2.var(axis=0)
        d = np.maximum(np.abs(b_k - b2), np.abs(f_k - f2)) / (b_k + f_k)
        unresolved = [int(i + 1) for i in np.flatnonzero(d > UNRESOLVED)]
        prec.update(d_k=d.tolist(), unresolved_ranks=unresolved, n_unresolved=len(unresolved),
                    max_d=float(d.max()), lambda_rel_diff_max=float(np.max(np.abs(lk2 / lk - 1))),
                    split_rel_diff={"ebar_Cplus_ebar": relerr(float(b2.sum()), part_mean),
                                    "trace_Cplus_S": relerr(float(f2.sum()), part_spread)})
        prec["truncated_counts"] = {}
        for k in RANKS:
            c1 = int(np.sum(np.sum(Z[:, :k] ** 2, axis=1) <= cuts[k]))
            c2 = int(np.sum(np.sum(Z2[:, :k] ** 2, axis=1) <= cuts[k]))
            prec["truncated_counts"][str(k)] = {"numpy": c1, "evr": c2, "agree": c1 == c2,
                                                "unresolved_ranks_within": [r for r in unresolved if r <= k]}
    else:
        unresolved = None
        prec["note"] = "the two drivers give different ranks; no per-rank comparison is made"
    rec["precision"] = prec
    rec["C_T_counts"] = {"above_1e-4": counts_1e4, "above_1e-6": counts_1e6,
                         "label": "C_T's own eigenvalue counts at the published covariance's thresholds; the ranks "
                                  "used are fixed at 73 and 139 (the director's ruling)"}
    rec["truncated"] = trunc
    if a.fig:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        k = np.arange(1, ndf + 1)
        fig, ax = plt.subplots(figsize=(7.5, 4.2))
        ax.plot(k, b_k, ".", ms=3, label=r"$\bar z_k^2$ (mean error)")
        ax.plot(k, f_k, ".", ms=3, label=r"var$(z_k)$ (spread)")
        if unresolved:
            u = np.asarray(unresolved) - 1
            ax.plot(k[u], (b_k + f_k)[u], "x", color="red", ms=5, label="numerically unresolved (> 1% between drivers)")
        ax.axhline(1, color="0.5", lw=0.8)
        for r in RANKS:
            ax.axvline(r, color="0.7", lw=0.8, ls="--")
        ax.set_yscale("log"); ax.set_xlabel("eigen-rank k of C_T (descending eigenvalue)")
        ax.set_ylabel("per-component mean square"); ax.set_title(f"T2A {T}: whitened error components")
        ax2 = ax.twinx(); ax2.plot(k, lk / lk[0], color="0.3", lw=0.8); ax2.set_yscale("log")
        ax2.set_ylabel(r"$\lambda_k/\lambda_1$")
        ax.legend(loc="upper left", fontsize=8); fig.tight_layout(); fig.savefig(a.fig, dpi=150)
        rec["figure"] = {"path": str(a.fig)}
    return finish(0)


if __name__ == "__main__":
    sys.exit(main())
