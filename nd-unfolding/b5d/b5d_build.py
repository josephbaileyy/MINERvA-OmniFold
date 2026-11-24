#!/usr/bin/env python3
"""(b) part 3: the 5D bias block C_b^5D and fluctuation block V_F^5D (B5D-DECLARATION.md rev 1, sha256 676c17fc...).

Implements the declaration's §3-§5 exactly. Reuses, unchanged: B-SEL's input layer (bsel_select.check_pins/prepare for
b, noise, R and the F0b/F1 tables), LL5D's naming, layout and digest (ll5d, ll5d_b), S1's matrix helpers (s1_assemble:
EXPECT, mat_cov, functional_matrix, fine_map, flux_weights). Reads no data, no seal and no S1 product.

Every control is a STOP (exit 5, nothing written). MEASURES: candidate blocks for Joseph's adoption decision.
CANNOT AUTHORIZE: a change to the reported covariance, a coverage or support claim, a data statement.
usage: b5d_build.py --repo REPO --ll5d DIR --out DIR      (DIR holds the 1,655 fetched copies, flat)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

SCHEMA = "b5d-blocks/1"
DECLARATION_SHA256 = "676c17fc5982a01c21f4c7feae2f6c8cd32b0b8ecdc69ec93882e5e30c0f0b1b"
N_CELLS = 16
FAMILY = ("nominal", "A7_genie_mec", "A7_nuwro", "A7_gibuu")
DIAGNOSTICS = ("W1", "W2", "W3", "stage0c_gibuu", "closure_nuwro", "F1_genie_v3_g18", "F1_genie_v3_ar23")
TRUTHS_LL5D = ("g18", "ar23")
PRIMARY, SECONDARY = "minus2", "all"
BANDS = ((0, 4), (4, 8), (8, 16))  # eigen-rank 1-4, 5-8, 9-16 (0-based slices)
MIN_MODES = 4
BOOT_N, BOOT_SEED = 2000, 9_991_000
TRIGGER_K = 3.0
UNRESOLVED_SE = 0.5
KEEP_REL = 1e-12
TOL = 1e-12
FD = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd"
COMMITTED = {
    f"{FD}/with-cpl/data-product/fd_data_product_cpl_C_e.csv": "222c4dd4efef0780c408b82caa8d360723bc8b73b784885789f374a624e6c715",
    "docs/orchestration/state/measurement-paper/5d-community-20261024/s1/readout/s1_assembly.json":
        "81e5ef3fe8e7b055360dc43b8a8240c9b5c39c8aa6e7c507b3211d305b326b21",
    f"{FD}/receipts-ll5d/hpss-u/hpss_ll5d_u_list.tsv": "980bb95e20eac386a220bb7d0dbb16a5a3477248688f9a72bc07671a7ad5842d",
    f"{FD}/receipts-ll5d/null/node/null-g18.json": "73dbaf9517374646c719ff589015cb12c1a6a2eafd5579e1074ef700bde703c2",
    f"{FD}/receipts-ll5d/null/node/null-ar23.json": "a0544ab9f6f0ec55c9866bee689d2563b13c9d07f4b3fdc37ce4762718a23933",
}
SELECTION_INPUTS = "docs/orchestration/state/ben-b-20261124/selection-20261124/record/selection"
CONSTRAINT_NAME = "sorted_NuEConstraint_FHC_RHC_IMD.txt"
GROUPS = ("toys", "null_roles")


class Stop(RuntimeError):
    def __init__(self, control: str, why: str):
        super().__init__(f"{control}: {why}")
        self.control = control


def sha256_path(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ------------------------------------------------------------------------------------------------ linear algebra
def eig_sorted(M: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Eigenpairs by descending eigenvalue; each eigenvector signed so its largest-|component| is positive."""
    w, V = np.linalg.eigh((M + M.T) / 2)
    order = np.argsort(w)[::-1]
    w, V = w[order], V[:, order]
    for i in range(V.shape[1]):
        k = int(np.argmax(np.abs(V[:, i])))
        if V[k, i] < 0:
            V[:, i] = -V[:, i]
    return w, V


def positive_part(M: np.ndarray) -> np.ndarray:
    w, V = np.linalg.eigh((M + M.T) / 2)
    w = np.clip(w, 0.0, None)
    return (V * w) @ V.T


def bands_kept(w: np.ndarray) -> tuple[list, list]:
    keep = w > KEEP_REL * w[0]
    out, dropped = [], []
    for a, b in BANDS:
        idx = [i for i in range(a, min(b, len(w))) if keep[i]]
        (out if len(idx) >= MIN_MODES else dropped).append((a, b, idx))
    return out, dropped


# ------------------------------------------------------------------------------------------------ §3 the bias block
def bias_block(beta: dict, Sigma: dict) -> tuple[np.ndarray, np.ndarray]:
    """C_b = [sum_t (beta beta^T - Sigma_t)]_+ over FAMILY; also the undebiased C_b0 = sum beta beta^T."""
    C0 = sum(np.outer(beta[t], beta[t]) for t in FAMILY)
    raw = sum(np.outer(beta[t], beta[t]) - Sigma[t] for t in FAMILY)
    return positive_part(raw), C0


def against(beta: np.ndarray, C: np.ndarray) -> dict:
    """beta^T C^+ beta and the fraction of ||beta||^2 outside C's span."""
    w, V = np.linalg.eigh((C + C.T) / 2)
    keep = w > KEEP_REL * max(w.max(), 0.0) if w.max() > 0 else np.zeros_like(w, bool)
    Vk, wk = V[:, keep], w[keep]
    proj = Vk.T @ beta
    q = float(np.sum(proj ** 2 / wk)) if keep.any() else float("inf")
    nb = float(beta @ beta)
    out_frac = float(1.0 - np.sum(proj ** 2) / nb) if nb > 0 else 0.0
    return {"quad": q, "fraction_outside_span": out_frac, "rank": int(keep.sum())}


# ------------------------------------------------------------------------------------------------ §4 the fluctuation
def mode_spreads(E: np.ndarray, w: np.ndarray, V: np.ndarray) -> np.ndarray:
    """v_i = (1/N) sum_s z_{s,i}^2, z = u_i^T (e_s - e_bar)/sqrt(lambda_i)."""
    Z = (E - E.mean(axis=0)) @ V / np.sqrt(np.where(w > 0, w, np.nan))
    return np.mean(Z ** 2, axis=0)


def band_factor(v: np.ndarray, idx: list, N: int) -> float:
    return float(np.mean(v[idx]) / ((N - 1) / N))


def fhat(ensembles: dict, bands: dict) -> dict:
    """ensembles[key] = (E (N,16), w, V); bands[key] = kept bands. f-hat per band = mean over ensembles of F~_R."""
    out = {}
    for r in range(len(BANDS)):
        vals = []
        for key, (E, w, V) in ensembles.items():
            kept = {a: idx for a, b, idx in bands[key]}
            a = BANDS[r][0]
            if a not in kept:
                vals = None
                break
            vals.append(band_factor(mode_spreads(E, w, V), kept[a], E.shape[0]))
        out[r] = None if vals is None else float(np.mean(vals))
    return out


def bootstrap_se(ensembles: dict, bands: dict, n: int = BOOT_N, seed: int = BOOT_SEED) -> dict:
    """SD of f-hat over n joint replicates: toys resampled within each ensemble; eigenbases fixed."""
    rng = np.random.default_rng(seed)
    keys = sorted(ensembles)
    reps = {r: [] for r in range(len(BANDS))}
    for _ in range(n):
        res = {}
        for key in keys:
            E, w, V = ensembles[key]
            res[key] = (E[rng.integers(0, E.shape[0], E.shape[0])], w, V)
        f = fhat(res, bands)
        for r, v in f.items():
            reps[r].append(np.nan if v is None else v)
    return {r: (None if np.all(np.isnan(v)) else float(np.std(np.asarray(v), ddof=1))) for r, v in reps.items()}


def trigger(f: dict, se: dict) -> dict:
    out = {}
    for r in f:
        if f[r] is None or se[r] is None:
            out[r] = {"active": False, "phi": 1.0, "why": "band dropped"}
            continue
        active = bool(f[r] - 1.0 > TRIGGER_K * se[r])
        out[r] = {"active": active, "phi": float(f[r]) if active else 1.0}
    return out


def fluctuation_block(C_e: np.ndarray, trig: dict) -> tuple[np.ndarray, np.ndarray]:
    w, V = eig_sorted(C_e)
    L = np.eye(N_CELLS)
    for r, (a, b) in enumerate(BANDS):
        if trig[r]["active"]:
            P = V[:, a:b] @ V[:, a:b].T
            L = L + (np.sqrt(trig[r]["phi"]) - 1.0) * P
    return L @ C_e @ L.T, L


# ------------------------------------------------------------------------------------------------ inputs
def read_csv_matrix(p: Path) -> np.ndarray:
    import csv
    with open(p, newline="") as fh:
        rows = list(csv.reader(fh))
    M = np.array([[float(x) for x in r[1:]] for r in rows[1:]])
    if M.shape != (N_CELLS, N_CELLS):
        raise Stop("C-PIN", f"{p.name} is not 16 x 16")
    return M


def manifest_pins(repo: Path) -> dict:
    out = {}
    for line in (repo / f"{FD}/receipts-ll5d/hpss-u/hpss_ll5d_u_list.tsv").read_text().splitlines():
        if not line.strip():
            continue
        g, sha, path = line.split("\t")
        if g in GROUPS:
            out[Path(path).name] = sha
    return out


def check_ll5d_pins(repo: Path, ll5d_dir: Path, sa) -> None:
    pins = manifest_pins(repo)
    if len(pins) != 1654:
        raise Stop("C-PIN", f"the manifest gives {len(pins)} pinned products, not 1654")
    have = {p.name for p in ll5d_dir.glob("ll5d_*.npz")}
    if have != set(pins):
        raise Stop("C-PIN", f"the fetched set differs from the manifest's: {sorted(have ^ set(pins))[:4]}")
    for name, pin in pins.items():
        if sha256_path(ll5d_dir / name) != pin:
            raise Stop("C-PIN", f"{name} is not its pin")
    if sha256_path(ll5d_dir / CONSTRAINT_NAME) != sa.CONSTRAINT_SHA256:
        raise Stop("C-PIN", "the flux constraint is not its pin")


def cells(ll5d_dir: Path, U: np.ndarray, name: str, key: str = "xsec_flat") -> np.ndarray:
    with np.load(ll5d_dir / name, allow_pickle=False) as z:
        return U @ np.asarray(z[key], float)


def drawn_block(ll5d_dir: Path, U: np.ndarray, truth: str, reading: str, w_flux: np.ndarray, sa, ll5d_b) -> np.ndarray:
    """D = sum_{band in reading} mat_cov(band universes at T) + Cov(stat replicas), as ll5d_b.remade forms them."""
    D = np.zeros((N_CELLS, N_CELLS))
    for band in ll5d_b.bands_of(reading):
        n = sa.EXPECT[band]
        X = np.array([cells(ll5d_dir, U, ll5d_b.product_name(truth, "block", f"{band}_{i}")) for i in range(n)])
        D = D + sa.mat_cov(X, w_flux if band == sa.FLUX else None)
    R = np.array([cells(ll5d_dir, U, ll5d_b.product_name(truth, "stat", str(b))) for b in ll5d_b.STAT_REPLICAS])
    return D + np.cov(R, rowvar=False, ddof=1)


def toy_errors(ll5d_dir: Path, U: np.ndarray, truth: str, reading: str, ll5d, ll5d_b) -> np.ndarray:
    names = sorted(p.name for p in ll5d_dir.glob(f"ll5d_{truth}_toy_{reading}_*.npz"))
    want = sorted(ll5d_b.product_name(truth, "toy", f"{reading}_{s}") for s in ll5d.TOY_SEEDS[truth])
    if names != want:
        raise Stop("C-LL5D", f"{truth}/{reading}: the toys are not exactly the declared seeds ({len(names)} of 300)")
    E = []
    for s in ll5d.TOY_SEEDS[truth]:
        n = ll5d_b.product_name(truth, "toy", f"{reading}_{s}")
        E.append(cells(ll5d_dir, U, n) - cells(ll5d_dir, U, n, "xtrue_flat"))
    return np.array(E)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="b5d_build.py", allow_abbrev=False)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--ll5d", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        print(f"refusing: {a.out} exists", file=sys.stderr)
        return 2
    for p in (a.repo / "nd-unfolding", a.repo / "nd-unfolding/bsel"):
        sys.path.insert(0, str(p))
    try:
        import s1_assemble as sa
        import ll5d
        import ll5d_b
        import bsel_select as B
        out = build(a.repo, a.ll5d, sa, ll5d, ll5d_b, B)
    except Stop as e:
        print(f"STOP {e}", file=sys.stderr)
        return 5
    a.out.mkdir(parents=True)
    write_record(a.out, out)
    print(json.dumps({"verdict": "COMPLETE"}))
    return 0


def build(repo: Path, ll5d_dir: Path, sa, ll5d, ll5d_b, B) -> dict:
    for rel, pin in COMMITTED.items():
        if sha256_path(repo / rel) != pin:
            raise Stop("C-PIN", f"{rel} is not its pin")
    sel = repo / SELECTION_INPUTS
    B.check_pins(repo, sel)
    check_ll5d_pins(repo, ll5d_dir, sa)
    # C-FLUX
    w_flux = sa.flux_weights(ll5d_dir / CONSTRAINT_NAME)
    meta = json.loads((repo / "docs/orchestration/state/measurement-paper/5d-community-20261024/s1/readout/s1_assembly.json").read_text())["meta"]["flux_weights"]
    n_eff = float(w_flux.sum() ** 2 / (w_flux ** 2).sum())
    if abs(w_flux.sum() / meta["sum"] - 1) > TOL or abs(n_eff / meta["n_eff"] - 1) > TOL:
        raise Stop("C-FLUX", "the constraint's weights do not reproduce S1's sum and n_eff")
    U = sa.functional_matrix(sa.fine_map(repo / "nd-unfolding/pv-ladder/readouts/h2_definition.json"))
    # C-LL5D, C-SEED
    for t in TRUTHS_LL5D:
        rec = json.loads((repo / f"{FD}/receipts-ll5d/null/node/null-{t}.json").read_text())
        if ll5d_b.products_digest(ll5d_dir, t, ll5d_b.BLOCK_ROLES) != rec["products_sha256"]:
            raise Stop("C-LL5D", f"{t}: the fetched central/seed/block/stat products are not those LL5D graded against")
        if not np.array_equal(cells(ll5d_dir, U, ll5d_b.product_name(t, "central", "T")),
                              cells(ll5d_dir, U, ll5d_b.product_name(t, "seed", "T"))):
            raise Stop("C-SEED", f"{t}: central_T and seed_T differ")
    # §3 the bias block (B-SEL's checked layer: b, noise, R, tables)
    M16 = __import__("estimator_stability_analyze").cell_matrix(str(repo / "nd-unfolding/pv-ladder/readouts/h2_definition.json"))
    b, sig, R, split_r, g = B.prepare(repo, sel, M16)
    with np.load(sel / "fd_f0b_experiments.npz", allow_pickle=False) as z:
        tab = {k: np.asarray(z[k]) for k in z.files}
    beta = {t: b[t] * R[t] for t in B.TRUTHS}
    Sigma = {}
    for t in FAMILY:
        r = np.asarray(tab[f"r_{t}"], float)
        N = np.cov(r, rowvar=False, ddof=1) / r.shape[0]
        if not np.allclose(np.sqrt(np.diag(N)), sig[t], rtol=TOL, atol=0):
            raise Stop("C-TAB", f"{t}: the table's noise does not reproduce the readout")
        Sigma[t] = np.diag(R[t]) @ N @ np.diag(R[t])
    C_b, C_b0 = bias_block(beta, Sigma)
    if np.linalg.eigvalsh(C_b).min() < -TOL * max(1e-300, abs(np.linalg.eigvalsh(C_b)).max()):
        raise Stop("C-PSD", "C_b is not positive semidefinite")
    g_tv1 = np.asarray(g["mnvtune_v1"], float)
    C_b_abs = np.diag(g_tv1) @ C_b @ np.diag(g_tv1)
    printed = {t: against(beta[t], C_b) for t in DIAGNOSTICS}
    members = {t: {**against(beta[t], C_b), "undebiased_bound": against(beta[t], C_b0)["quad"]} for t in FAMILY}
    # §4 the fluctuation block
    ens, bands, dropped, Ds, mean_err = {}, {}, {}, {}, {}
    for t in TRUTHS_LL5D:
        for rd in (PRIMARY, SECONDARY):
            D = drawn_block(ll5d_dir, U, t, rd, w_flux, sa, ll5d_b)
            w, V = eig_sorted(D)
            if not w[0] > 0:  # §5 C-PSD: positive on the kept modes (lambda_i > 1e-12 lambda_1); weaker modes are dropped
                raise Stop("C-PSD", f"{t}/{rd}: D has no positive mode")
            E = toy_errors(ll5d_dir, U, t, rd, ll5d, ll5d_b)
            ens[(t, rd)] = (E, w, V)
            kb, dr = bands_kept(w)
            bands[(t, rd)], dropped[(t, rd)] = kb, dr
            Ds[(t, rd)] = D
            X_T = cells(ll5d_dir, U, ll5d_b.product_name(t, "central", "T"), "xtrue_flat")
            mean_err[(t, rd)] = E.mean(axis=0) / X_T  # truth-relative mean error (printed)
    prim = {k: v for k, v in ens.items() if k[1] == PRIMARY}
    f = fhat(prim, bands)
    se = bootstrap_se(prim, bands)
    for r in f:
        if f[r] is not None and not (np.isfinite(f[r]) and se[r] is not None and np.isfinite(se[r])):
            raise Stop("C-FIN", f"band {r + 1}: f-hat or its SE is not finite")
    per_ens = {f"{t}/{rd}": {f"R{r + 1}": (band_factor(mode_spreads(*ens[(t, rd)]), dict((a, i) for a, _, i in bands[(t, rd)])[BANDS[r][0]],
                                                      ens[(t, rd)][0].shape[0]) if BANDS[r][0] in dict((a, i) for a, _, i in bands[(t, rd)]) else None)
                             for r in range(len(BANDS))} for (t, rd) in ens}
    unresolved = all(s is None or s > UNRESOLVED_SE for s in se.values())
    C_e = read_csv_matrix(repo / f"{FD}/with-cpl/data-product/fd_data_product_cpl_C_e.csv")
    trig = trigger(f, se)
    V_F, L = (None, None) if unresolved else fluctuation_block(C_e, trig)
    # the cal-set cross-check (printed)
    rs = json.loads((repo / "docs/orchestration/state/measurement-paper/5d-community-20261024/s1/readout/s1_assembly.json").read_text())["relative_sigma"]
    pred = np.sqrt(np.asarray(rs["flux"]) ** 2 + np.asarray(rs["stat"]) ** 2)
    cal = {k[len("r_cal_"):]: (np.std(np.asarray(v, float), axis=0, ddof=1) / pred).tolist() for k, v in tab.items() if k.startswith("r_cal_")}
    return {"schema": SCHEMA, "declaration_sha256": DECLARATION_SHA256,
            "bias_block": {"family": list(FAMILY), "C_b_tune_v1_units": C_b.tolist(), "C_b_abs": C_b_abs.tolist(),
                           "rank": int(np.sum(np.linalg.eigvalsh(C_b) > KEEP_REL * max(np.linalg.eigvalsh(C_b).max(), 1e-300))),
                           "members": members, "printed_against_C_b": printed,
                           "ll5d_toy_mean_error_truth_relative": {f"{t}/{rd}": v.tolist() for (t, rd), v in mean_err.items()}},
            "fluctuation": {"bands": [f"ranks {a + 1}-{b}" for a, b in BANDS], "f_hat": {f"R{r + 1}": f[r] for r in f},
                            "se": {f"R{r + 1}": se[r] for r in se}, "trigger": {f"R{r + 1}": trig[r] for r in trig},
                            "per_ensemble": per_ens, "dropped": {f"{t}/{rd}": [f"ranks {a + 1}-{b}" for a, b, _ in d] for (t, rd), d in dropped.items()},
                            "unresolved_stop": unresolved, "bootstrap": {"n": BOOT_N, "seed": BOOT_SEED},
                            "V_F": None if V_F is None else V_F.tolist(), "L": None if L is None else L.tolist()},
            "cal_cross_check_sd_over_s1_flux_stat": cal,
            "flux_weights": {"sum": float(w_flux.sum()), "n_eff": n_eff}}


def write_record(out_dir: Path, rec: dict) -> None:
    (out_dir / "blocks5d.json").write_text(json.dumps(rec, indent=1) + "\n")
    hdr = "cell," + ",".join(f"R{c:02d}" for c in range(N_CELLS))
    for key, M in (("C_b_abs", rec["bias_block"]["C_b_abs"]), ("C_b_tune_v1_units", rec["bias_block"]["C_b_tune_v1_units"]),
                   ("V_F", rec["fluctuation"]["V_F"])):
        if M is None:
            continue
        rows = [hdr] + [f"R{c:02d}," + ",".join(repr(float(x)) for x in M[c]) for c in range(N_CELLS)]
        (out_dir / f"{key}.csv").write_text("\n".join(rows) + "\n")
    fl = rec["fluctuation"]
    lines = [f"B5D blocks: C_b rank {rec['bias_block']['rank']} (family {', '.join(rec['bias_block']['family'])})"]
    for r in ("R1", "R2", "R3"):
        lines.append(f"{r}: f_hat {fl['f_hat'][r]}, SE {fl['se'][r]}, trigger {fl['trigger'][r]}")
    lines.append(f"unresolved stop: {fl['unresolved_stop']}")
    for t, v in rec["bias_block"]["printed_against_C_b"].items():
        lines.append(f"{t} vs C_b: quad {v['quad']:.4g}, outside span {v['fraction_outside_span']:.4g}")
    (out_dir / "blocks5d.txt").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    sys.exit(main())
