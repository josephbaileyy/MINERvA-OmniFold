"""COVFIX P0 (COVFIX-DECLARATION.md rev 11.4 section 3.1; COVFIX-BINDING-1 ruling 2): what the committed records give.
Local, 0 node-h, descriptive, on committed spent records only. "These validate nothing."

  python3 covfix_p0.py --q-rep <cov2d_Q_205.npz> --g2r-dir <dir holding <T>/blocks_g2r_<T>.npz> --out <p0.json>

This is P0's pre-W1 part. Section 3.1's second carry vector, round(lambda+), comes from two unfolds that run in W1; the
readings that need it are completed after W1 by a step whose input contract (the W1 receipt, its aligned digest and
section 2's rounding check) is written with the W1 code. Until then the record says "pending W1".

Stages, in order; each control stage STOPS P0 before any reading:
  1 inputs        every input pinned by sha256 (a missing or changed input is a C-PIN STOP)
  2 controls      Q_rep's two block identities (exact numerical equality, summed in the declared order); C_model's
                  matrix sha256; the cell and frame map across files; the A0-type control (COV2D's committed mean chi2
                  at G18 and AR23 from E_<T> against C_T, to max(1e-9, 10 kappa_2 eps)); C-PSD on every block P0 uses
                  or forms (lambda_min >= -1e-12 lambda_max; A FAILURE STOPS AT P0)
  3 residual      per tune: section 5.2's rule on the regrade pair (old C_T, fluctuation reference C_T - C_model_abs(T);
                  new C_T + C_run(T), reference F_T + C_run(T); C_run = diag(x_T/x_R) C_PL diag(x_T/x_R), REGRADE's
                  carry). IF IT FIRES AT EITHER TUNE, P0 STOPS HERE AND GOES TO THE DIRECTOR
  4 readings      carry_check (K0 carried with COV2D's x_hat_T against C_T: E_<T> under each, the eigenvalue ratio per
                  band, principal angles between kept spans); profiles (m_i, v_i, q_i under carried K0, C_T, G2R's
                  C_T'); ibukt_a2 (m_i only); c2 (T2A's mean error on C_PL's two directions, carried to the tune)

Exit 0 when the pre-W1 part ran, 3 on a STOP (the record is still written), 2 if --out exists.
MEASURES: the section 3.1 readings. CANNOT AUTHORIZE: any reading as validation, any bar, any wording.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for p in (HERE, REPO / "nd-unfolding", REPO / "2d-unfolding" / "pv2d" / "cmodel"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import covfix_core as cc  # noqa: E402
import fd_1b_null as fn  # noqa: E402
import build_cmodel as bcm  # noqa: E402

FD = REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd"
TUNES = ("G18", "AR23")
Q_REP_SHA = "ff66b91d6d2c574a1786b057ce7566e8ed7184700a45b989fa41ae0eb8cb0295"   # declaration section 2
C_MODEL_SHA = "11fe68188bd31a35103f5eb4708bd6a7cdab8965164680caa6671c509dcd3470"  # declaration section 2
PINS = {   # sha256 of the committed bytes (REGRADE's pins for E, blocks and score)
    "E_AR23": (FD / "tier2-20261110/t2a/AR23/E_AR23.npz",
               "ccda9c50c6bb1cbbdd2206c8954652f4f77c6cf2b4451e8488601e9896b0a85e"),
    "E_G18": (FD / "tier2-20261110/t2a/G18/E_G18.npz",
              "846b9d852218b531d605bd955ca9a9037d187e74723077bdfff4557efafc3ba6"),
    "blocks_AR23": (FD / "receipts-cov2d/readout/AR23/blocks_AR23.npz",
                    "abaebaeae6c9cb075dcb974a420dbf148809d01b2cabc8deda31f318bf6715ee"),
    "blocks_G18": (FD / "receipts-cov2d/readout/G18/blocks_G18.npz",
                   "7eb657b82ae953bdf0584eda27264c52a64bcb48baea52dfc194f5efe440ea3d"),
    "score_AR23": (FD / "receipts-cov2d/readout/AR23/score_AR23.json",
                   "fe5263e904f65892ce26b75fb279441230713c38675c2a3615c59d561c4f5ce1"),
    "score_G18": (FD / "receipts-cov2d/readout/G18/score_G18.json",
                  "849766942b3ecd9e6e72fd5db9d1a59815796b3f917875f8d0122b0c639088ec"),
    "cmodel_json": (REPO / "2d-unfolding/pv2d/cmodel/cmodel_2d.json",
                    "aabc66d106a49484d486fb055bfb4280187898f98ca406e010f153af57702dd0"),
    "ibukt_readout": (REPO / "docs/orchestration/state/2d-closeout/ibukt-a2/readout.json",
                      "dfae50f595ac37b5179722a6a9d264f758cce91c163ca6cc1ab3b03462da8da6"),
}
G2R_SHA = {   # not committed; listed by sha256 in receipts-cov2d/g2r/readout/<T>/README.md:32 and out.sha256.txt:1
    "AR23": "c060cb40232e0112ec440951f94841e87fc98b542a165eed2c8242898508a70a",
    "G18": "55ad7cc4faa4680b49391a9d68f52fcaa707150bd1300915063d66a16be9bfbe",
}
E_R_METHOD = "omnifold"   # IBUKT A2's E_R arm (refined-target OmniFold; readout.json primary_methods[0])


class Stop(RuntimeError):
    """A P0 control failed, or the residual rule fired: P0 stops and goes to the director."""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def pinned(path: Path, want: str) -> Path:
    try:
        got = sha256(path)
    except OSError as e:
        raise Stop(f"C-PIN: {path} cannot be read ({e})") from e
    if got != want:
        raise Stop(f"C-PIN: {path} is {got}, pinned {want}")
    return path


def load_npz(path: Path) -> dict:
    with np.load(path, allow_pickle=False) as z:
        return {k: np.asarray(z[k]) for k in z.files}


# ------------------------------------------------------------------------------------------------- controls
def q_identities(Z: dict) -> dict:
    """Q = s5_total + C_PL and s5_total = universe + stat + c08, exact numerical equality, summed in the declared
    order (np.array_equal)."""
    rec = {"Q = s5_total + C_PL": bool(np.array_equal(Z["Q"], Z["s5_total"] + Z["C_PL"])),
           "s5_total = universe + stat + c08": bool(np.array_equal(Z["s5_total"],
                                                                   Z["universe"] + Z["stat"] + Z["c08"]))}
    if not all(rec.values()):
        raise Stop(f"C-ID: {rec}")
    return rec


def c_model() -> tuple[np.ndarray, dict]:
    M = json.loads(pinned(*PINS["cmodel_json"]).read_text())
    C = bcm.cmodel(np.asarray(M["S"], np.float64))
    got = bcm.matrix_sha256(C)
    if got != C_MODEL_SHA:
        raise Stop(f"C-MODEL: matrix sha256 {got} != {C_MODEL_SHA}")
    return C, {"matrix_sha256": got, "vertices": list(M["vertices"])}


def psd_all(blocks: dict) -> list:
    recs = [cc.psd_check(C, name) for name, C in blocks.items()]
    bad = [r for r in recs if not r["pass"]]
    if bad:
        raise Stop(f"C-PSD: {[(r['name'], r['lambda_min'], r['lambda_max']) for r in bad]}")
    return recs


def a0_tol(C: np.ndarray) -> dict:
    """max(1e-9, 10 kappa_2 eps), kappa_2 on C's non-null subspace (REGRADE amendment 1's form of COV2D A5)."""
    lam = np.linalg.eigvalsh(np.asarray(C, np.float64))
    keep = lam > fn.RANK_REL * lam.max()
    kappa = float(lam.max() / lam[keep].min())
    return {"kappa2": kappa, "tol": max(1e-9, 10 * kappa * cc.EPS)}


def a0_control(E: np.ndarray, C_T: np.ndarray, committed: dict) -> dict:
    """COV2D's legacy grading path (fd_1b_null.chi2_nonnull on the raw C_T), as COV2D and REGRADE graded."""
    chi2, ndf = fn.chi2_nonnull(E, C_T)
    got = float(chi2.mean() / ndf)
    t = a0_tol(C_T)
    rel = abs(got / committed["chi2_mean_over_ndf"] - 1.0)
    rec = {"ndf": ndf, "ndf_committed": committed["ndf"], "chi2_mean_over_ndf": got,
           "committed": committed["chi2_mean_over_ndf"], "rel": rel, **t}
    rec["pass"] = bool(ndf == committed["ndf"] and rel <= t["tol"])
    if not rec["pass"]:
        raise Stop(f"A0: {rec}")
    return rec


def cell_map(Z: dict, B: dict, G: dict) -> dict:
    """Every P0 reading pairs cells across Q_rep, COV2D's blocks and G2R's blocks, and carries by x_T / x_R: the cell
    order (Q's cells = rep's reported cells, G2R's rep = COV2D's rep) and the frame vectors must be the same."""
    rec = {"Q cells = blocks rep": bool(np.array_equal(Z["cells"], np.flatnonzero(B["rep"]))),
           "G2R rep = blocks rep": bool(np.array_equal(G["rep"], B["rep"])),
           "Q x = blocks x_R": bool(np.array_equal(Z["x"], B["x_R"])),
           "G2R x_R = blocks x_R": bool(np.array_equal(G["x_R"], B["x_R"])),
           "G2R x_T = blocks x_T": bool(np.array_equal(G["x_T"], B["x_T"]))}
    if not all(rec.values()):
        raise Stop(f"C-MAP: {rec}")
    return rec


# ------------------------------------------------------------------------------------------------ readings
def summary(rd: dict) -> dict:
    """A mode_readings record without its matrices; the per-mode arrays are kept."""
    return {k: v for k, v in rd.items() if not k.startswith("_")}


def eig_ratio_by_band(lam_a: np.ndarray, lam_b: np.ndarray) -> dict:
    """lambda_i(a) / lambda_i(b), paired by common rank over the ranks kept in both, banded by b's (the remade C_T's)
    spectrum; a band with fewer than 10 common ranks is dropped and named. Per-rank ratios are kept."""
    n = min(lam_a.size, lam_b.size)
    r = lam_a[:n] / lam_b[:n]
    band = cc.band_of(lam_b[:n])
    out = {"pairing": "common rank, banded by C_T's kept spectrum", "n_compared": n, "ratio": r}
    for b, (name, _, _) in enumerate(cc.BAND_EDGES):
        s = band == b
        k = int(s.sum())
        out[name] = ({"n": k, "mean": float(r[s].mean()), "min": float(r[s].min()), "max": float(r[s].max())}
                     if k >= cc.BAND_MIN else {"n": k, "dropped": f"{name} holds {k} common ranks, fewer than "
                                                                  f"{cc.BAND_MIN}"})
    return out


def angles(A: np.ndarray, B: np.ndarray) -> dict:
    """Principal angles between two kept spans; never empty, since mode_readings refuses a reading with no kept mode."""
    th = cc.principal_angles_deg(A, B)
    return {"n": int(th.size), "max_deg": float(th.max()), "median_deg": float(np.median(th)),
            "n_above_1deg": int(np.sum(th > 1.0)), "n_above_10deg": int(np.sum(th > 10.0)), "deg": th}


def carry_compare(E, K0_T, Q_T, C_T, F_T) -> dict:
    rk, rt = cc.mode_readings(E, K0_T, Q_T), cc.mode_readings(E, C_T, F_T)
    return {"K0_carried": summary(rk), "C_T": summary(rt),
            "eigenvalue_ratio_K0_over_C_T": eig_ratio_by_band(rk["lambda_kept"], rt["lambda_kept"]),
            "principal_angles_kept_spans": angles(rk["_U"], rt["_U"])}


def ibukt(K0: np.ndarray, Q: np.ndarray, x_R: np.ndarray, cells: np.ndarray) -> dict:
    R = json.loads(pinned(*PINS["ibukt_readout"]).read_text())
    lam, U = cc.eig_basis(K0)
    keep = cc.kept_mask(lam, cc.lambda_1(Q))
    lk, Uk = lam[keep], U[:, keep]
    out = {"method": E_R_METHOD, "ndf": int(keep.sum()),
           "convention": "an E_R-scaled residual: IBUKT's residual is estimate / truth - 1 per cell "
                         "(2d-unfolding/ibukt/ibukt.py:182); b = mean residual x x_R (E_R's reported spectrum), "
                         "equal to the absolute error only where x_R equals the truth; m_i = u_i^T b / sqrt(lambda_i) "
                         "in K0's basis at x_R, kept under Q_rep's lambda_1; m_i only (five draws)", "truths": {}}
    for t, rec in R["truths"].items():
        if [int(c) for c in rec["cells"]] != [int(c) for c in cells]:
            raise Stop(f"C-MAP: IBUKT {t} cells differ from Q_rep's")
        b = np.asarray(rec[E_R_METHOD]["mean"], np.float64) * x_R
        out["truths"][t] = {"m": (Uk.T @ b) / np.sqrt(lk)}
    return out


def c2(E: np.ndarray, C_PL: np.ndarray, d: np.ndarray) -> dict:
    """T2A's mean error on C_PL's two directions (the declared rank-two block's top two eigenvectors, whatever their
    size), carried to the tune; the uncarried directions are printed and read by nothing."""
    ebar = E.mean(axis=0)
    n2 = float(ebar @ ebar)
    out = {}
    for name, C in (("carried_to_tune", cc.carry(C_PL, d)), ("uncarried_read_by_nothing", C_PL)):
        lam, U = cc.eig_basis(C)
        dirs = []
        for mu, w in zip(lam[:2], U[:, :2].T):
            p = float(w @ ebar)
            dirs.append({"mu": float(mu), "projection": p, "in_sigma": p / math.sqrt(mu) if mu > 0 else None,
                         "share_of_ebar2": p * p / n2 if n2 > 0 else None})
        out[name] = {"directions": dirs, "third_over_first": float(lam[2] / lam[0]) if lam[0] > 0 else None}
    return out


# ----------------------------------------------------------------------------------------------------- run
def run(q_rep: Path, g2r_dir: Path) -> dict:
    out = {"schema": "covfix/p0/2", "part": "pre-W1", "validates": "nothing (declaration section 3.1)",
           "status": "running", "inputs": {}, "controls": {}}
    try:
        # 1 inputs
        Z = load_npz(pinned(q_rep, Q_REP_SHA))
        out["inputs"]["Q_rep"] = {"path": str(q_rep), "sha256": Q_REP_SHA}
        C_model, rec_cm = c_model()
        T_in = {}
        for T in TUNES:
            gp = g2r_dir / T / f"blocks_g2r_{T}.npz"
            T_in[T] = {"E": load_npz(pinned(*PINS[f"E_{T}"]))["E"].astype(np.float64),
                       "B": load_npz(pinned(*PINS[f"blocks_{T}"])),
                       "G": load_npz(pinned(gp, G2R_SHA[T])),
                       "score": json.loads(pinned(*PINS[f"score_{T}"]).read_text())["grade"]}
            out["inputs"][f"G2R_{T}"] = {"path": str(gp), "sha256": G2R_SHA[T]}
        out["inputs"]["committed"] = {k: {"path": str(p), "sha256": s} for k, (p, s) in PINS.items()}
        # 2 controls
        out["controls"]["Q_identities"] = q_identities(Z)
        out["controls"]["C_model"] = rec_cm
        x_R = np.asarray(Z["x"], np.float64)
        Cm_R = cc.absolute(C_model, x_R)
        K0 = Z["Q"] + Cm_R
        blocks = {k: Z[k] for k in ("Q", "s5_total", "universe", "stat", "c08", "C_PL")}
        blocks |= {"C_model": C_model, "C_model_abs(x_R)": Cm_R, "K0(x_R)": K0}
        derived = {}
        for T, t in T_in.items():
            B, G = t["B"], t["G"]
            out["controls"][f"map_{T}"] = cell_map(Z, B, G)
            out["controls"][f"A0_{T}"] = a0_control(t["E"], B["C_T"], t["score"])
            out["controls"][f"C_model_abs_blocks_vs_rebuilt_{T}"] = float(
                np.max(np.abs(B["C_model_abs"] - cc.absolute(C_model, B["x_T"]))) / np.max(np.abs(B["C_model_abs"])))
            d = cc.carry_factor(B["x_T"], x_R)
            dv = {"d": d, "F_T": B["C_T"] - B["C_model_abs"], "K0_T": cc.carry(K0, d), "Q_T": cc.carry(Z["Q"], d),
                  "C_run": cc.carry(Z["C_PL"], d), "F_G": G["C_T"] - G["C_model_abs"]}
            derived[T] = dv
            blocks |= {f"C_T({T})": B["C_T"], f"C_model_abs({T})": B["C_model_abs"], f"F_T({T})": dv["F_T"],
                       f"C_T_prime({T})": G["C_T"], f"C_model_abs_G2R({T})": G["C_model_abs"],
                       f"F_T_prime({T})": dv["F_G"], f"K0 carried({T})": dv["K0_T"], f"Q carried({T})": dv["Q_T"],
                       f"C_run({T})": dv["C_run"], f"C_T + C_run({T})": B["C_T"] + dv["C_run"],
                       f"F_T + C_run({T})": dv["F_T"] + dv["C_run"]}
        out["controls"]["C_PSD"] = psd_all(blocks)
        # 3 the residual rule's go/no-go control
        out["residual_rule"] = {}
        for T, t in T_in.items():
            B, dv = t["B"], derived[T]
            args = (B["C_T"], dv["F_T"], B["C_T"] + dv["C_run"], dv["F_T"] + dv["C_run"])
            rr = cc.residual_rule(*args)
            rr["cut_diagnostic"] = cc.cut_diagnostic(*args)
            out["residual_rule"][T] = rr
        fired = [T for T, rr in out["residual_rule"].items() if rr["fires"]]
        if fired:
            raise Stop(f"the residual rule fires on the regrade pair at {fired} "
                       f"({[round(out['residual_rule'][T]['residual'], 6) for T in fired]} > 0.1); P0 stops before "
                       f"its readings and goes to the director (section 3.1)")
        # 4 readings
        out |= {"carry_check": {}, "profiles": {}, "c2": {}}
        for T, t in T_in.items():
            E, B, G, dv = t["E"], t["B"], t["G"], derived[T]
            out["carry_check"][T] = {
                "xhat_committed": carry_compare(E, dv["K0_T"], dv["Q_T"], B["C_T"], dv["F_T"]),
                "xhat_round": "pending W1 (section 3.1: the round(lambda+) vector's unfolds run in W1)"}
            prof = {}
            for name, V, VF in (("K0_carried", dv["K0_T"], dv["Q_T"]), ("C_T", B["C_T"], dv["F_T"]),
                                ("C_T_prime_G2R", G["C_T"], dv["F_G"])):
                rd = cc.mode_readings(E, V, VF)
                prof[name] = summary(rd) | {"evr": cc.evr_agreement(E, V, VF, rd)}
            out["profiles"][T] = prof
            out["c2"][T] = c2(E, Z["C_PL"], dv["d"])
        out["ibukt_a2"] = ibukt(K0, Z["Q"], x_R, Z["cells"])
        out["status"] = "done (pre-W1 part)"
    except (Stop, cc.Refusal) as e:
        out["status"], out["stop"] = "STOP", f"{type(e).__name__}: {e}"
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="covfix_p0.py", allow_abbrev=False)
    ap.add_argument("--q-rep", type=Path, required=True)
    ap.add_argument("--g2r-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        print(f"refusing: {a.out} exists", file=sys.stderr)
        return 2
    rec = run(a.q_rep, a.g2r_dir)
    rec["code_sha256"] = {"covfix_p0.py": sha256(Path(__file__)), "covfix_core.py": sha256(HERE / "covfix_core.py")}
    a.out.write_text(json.dumps(cc.jsonable(rec), indent=1, allow_nan=False) + "\n")
    print(json.dumps({"status": rec["status"], **({"stop": rec["stop"]} if "stop" in rec else {})}))
    return 0 if rec["status"] == "done (pre-W1 part)" else 3


if __name__ == "__main__":
    sys.exit(main())
