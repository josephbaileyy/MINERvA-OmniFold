#!/usr/bin/env python3
"""The run-period diagnosis's readers (state/measurement-paper/5d-community-20261024/FD-RPD-DECLARATION.md, part 1
revision 4, bound by FD-RPD-BINDING-1.md). Login node, 0 node-h. Every rule here is part 1's; section numbers are its.

    fd_rpd.py stage0   --r <R> --definition ... --out-json <R>/control/stage0.json        section 3
    fd_rpd.py staged   --r <R> --definition ... --out-json <R>/control/stageD.json        section 5, stage D
    fd_rpd.py controls --r <R> --definition ... --out-json <R>/control/controls.json      section 4: C1, K2', N0-P
    fd_rpd.py gate     --r <R> --stage a|b                                                 the submit stages' gate
    fd_rpd.py readout  --r <R> --definition ... --out-json <R>/readout/fd_rpd.json        N0, R1, R2, R3

S1's assembly and C_resp are always the staged copies (<R>/staged/s1, <R>/staged/cresp). Nothing written or printed
carries f, an absolute cell value or f - g: every output passes fd_f0_regrade.LeakGuard (exit 3, nothing written).
A control that refuses exits 1 with nothing written.

MEASURES: arithmetic on the declared products. CANNOT AUTHORIZE: a covariance component, a change to the reported
matrix, a cause, which period is right, a claim or printed wording; section 6's table decides what wording an outcome
licenses, and the paper lane, the director and Joseph act on it.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_ct_periods as cp  # noqa: E402  (BOOT, guarded)
import fd_ct_readers as ct  # noqa: E402  (common, summary, cells, write, code_sha)
import fd_f0_regrade as f0  # noqa: E402  (Stop, report, require, sa_call)
import fd_rpd_inputs as ri  # noqa: E402  (PLAYLISTS, PERIODS, paths, staged, N0 constants)
import s1_assemble as sa  # noqa: E402  (fine_map, functional_matrix, check_meta, sha256, xs)

PL = ri.PLAYLISTS
NPL = len(PL)
N_CELLS = 16
GROUP = {pl: per for per, pls in ri.PERIODS.items() for pl in pls}
A_SET, B_SET, C_SET = ri.PERIODS["PA"], ri.PERIODS["PB"], ri.PERIODS["PC"]
# section 2: replica seeds 4000 + 100 i + k, i the production-order index 1..12, k = 1..30
N_REP = 30
REP = {pl: tuple(4000 + 100 * (i + 1) + k for k in range(1, N_REP + 1)) for i, pl in enumerate(PL)}
K2_SEEDS = (None, 3001)
# section 3
REF_2D_STEP = 0.0694
SEES_MIN, SEES_Z, ABSENT_Z = REF_2D_STEP / 2, 5.0, 3.0
L_REGION, H_REGION = (1.5, 8.0), (8.0, 15.0)
# section 4
N0_T_CELL, N0_T_STEP = 3.835, 2.756        # t_29 two-sided quantiles at 0.01/16 and 0.01
N0_SMALL = ri.N0_SMALL
# section 5
R1_Z, R1_RES, R1_GATE = 2.0, 4.0, 3.0      # classes at 2 sigma; UNRESOLVED if sigma >= tbar/4; computed if tbar/sigma >= 3
R2_ALPHA, R2_GATE_N, R2_BETA = 0.05, 2000, 0.80
R2_SCALES = (0.0, 0.5, 1.0, 2.0)
SEED = 20261102
STAGE_D_R1_DRAWS, STAGE_D_OUTER, STAGE_D_INNER = 20000, 500, 200
STAGE_D_RULE_PW, STAGE_D_RULE_EC = 0.5, 0.2
STAGE_D_BUDGET_S, STAGE_D_MIN_OUTER = 7200.0, 200
STAGE_D_ALPHA_OUTER = 25       # part 2 deviation 2: S0's alpha at 200 inner, printed for the first 25 outer per truth
FLUX_PI = (("PA", A_SET), ("PB", B_SET), ("PC", C_SET))
ERA_PI = (("1A-1E", ("1A", "1B", "1C", "1D", "1E")), ("1F-1G", ("1F", "1G")), ("1L-1M", ("1L", "1M")),
          ("1N-1P", ("1N", "1O", "1P")))
READOUT_5B = ("docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_ct_5b_periods.json",
              "a5b17895b1189543d773e94717e14cd9b1409535e366c96788f94bf6f40759db")
CHECK_REL = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/5b/run/inputs"
LABELS = {
    "stage0": "the dr_PB/PA step r[8,15)/r[1.5,8) - 1 of 5B's existing period unfolds on the fine cells that map to a "
              "reporting cell, sigma the RMS about s0 of the 10 replica-pair steps (no ddof); the 5D analogue of 2D's "
              "+6.94 +- 0.41% (period-unfold-20261014 REPORT.md:57), which differs in phase space and estimator",
    "staged": "design-time simulations (no playlist number): R1's operating characteristics under the declared truths "
              "at stage 0's s0, and R2's reachability under T1-T3 with the calibration gate off; their rules are part "
              "1's and are reported to the director before job A",
    "controls": "C1 (the per-playlist inputs are a partition of MP-1's lat_zero, renormalized per playlist), K2' (this "
                "deploy reproduces 5B's PC s42 and b3001 unfolds bitwise) and N0-P (the N0 partitions)",
    "r1": "where the step is, on the fine p_parallel regions; not a cause",
    "r2": "whether the 16-cell playlist offsets differ between the flux-file groups by more than playlist-to-playlist "
          "scatter would give; the permutation is approximate and its validity rests on the simulated null",
    "r3": "the 12-playlist block, from the same events as C_PL,5D: not an independent check; its interval depends on the "
          "exposure shares only and assumes iid equal-variance offsets",
    "not_citable_for": ["a cause of a period difference, or which period is right", "a validated size or coverage",
                        "an independent check of C_PL,5D", "a covariance component or a change to the reported matrix"],
}


class Grid:
    """The fine grid's reporting-cell functional U and the two p_parallel region functionals (section 3)."""

    def __init__(self, definition: Path):
        self.fm = f0.sa_call("S", sa.fine_map, definition)
        self.U = sa.functional_matrix(self.fm)
        vol = sa.s1.fine_volume()
        shape = sa.s1.fine_shape()
        ipz = np.unravel_index(np.arange(self.fm.size), shape)[sa.s1.AXES.index("pz")]
        e = np.asarray(sa.s1.FINE["pz"], float)
        lo, hi = e[ipz], e[ipz + 1]
        rep = self.fm >= 0
        self.wL = np.where(rep & (lo >= L_REGION[0]) & (hi <= L_REGION[1]), vol, 0.0)
        self.wH = np.where(rep & (lo >= H_REGION[0]) & (hi <= H_REGION[1]), vol, 0.0)
        for name, edge in (("8", 8.0), ("15", 15.0), ("1.5", 1.5)):
            if not np.any(np.isclose(e, edge)):
                raise f0.Stop("S", f"the fine p_parallel grid has no edge at {name}")

    def regions(self, x: np.ndarray) -> np.ndarray:
        return np.array([self.wL @ x, self.wH @ x])

    def region_var(self, v: np.ndarray) -> np.ndarray:
        return np.array([(self.wL ** 2) @ v, (self.wH ** 2) @ v])

    def cells(self, x: np.ndarray) -> np.ndarray:
        return self.U @ x

    def cell_var(self, v: np.ndarray) -> np.ndarray:
        return (self.U ** 2) @ v


# ---------------------------------------------------------------- arithmetic shared by the readers and the tests


def step(dn: np.ndarray, dd: np.ndarray) -> float:
    """s = [D_n(H)/D_d(H)] / [D_n(L)/D_d(L)] - 1, each D a (L, H) pair of double ratios X/T."""
    return float((dn[1] / dd[1]) / (dn[0] / dd[0]) - 1.0)


def combo(D: dict, e: dict, members) -> np.ndarray:
    """The exposure-weighted mean of the members' double ratios (R2's m form), per region or per cell."""
    w = np.array([e[m] for m in members])
    return sum(e[m] * D[m] for m in members) / w.sum()


def ref_set(X: str) -> tuple:
    return tuple(m for m in A_SET if m != X)


def r1_quantities(D: dict, e: dict) -> dict:
    """t_X against A*_X, tbar = s(PB*/A*), h_X = t_X - tbar/2 (section 5, R1)."""
    tbar = step(combo(D, e, B_SET), combo(D, e, A_SET))
    t = {X: step(D[X], combo(D, e, ref_set(X))) for X in PL}
    return {"t": t, "tbar": tbar, "h": {X: t[X] - tbar / 2 for X in PL}}


def classify(t, s, h, sh, tbar, unres_forced=False) -> str:
    """R1's classes: UNRESOLVED if sigma_X >= tbar/4 (or forced by N0); FREE if |t| <= 2 sigma; CARRIES if
    h >= 2 sigma_h; PARTIAL otherwise. For a resolved X, FREE and CARRIES are disjoint (part 1 section 5)."""
    if unres_forced or not s < tbar / R1_RES:
        return "UNRESOLVED"
    free = abs(t) <= R1_Z * s
    carries = h >= R1_Z * sh
    if free and carries:
        raise AssertionError("FREE and CARRIES both hold for a resolved playlist")
    return "FREE" if free else ("CARRIES" if carries else "PARTIAL")


def pattern(cls: dict) -> str:
    """R1's patterns, an ordered partition over the classes of 1A-1M."""
    rb = [cls[X] for X in B_SET if cls[X] != "UNRESOLVED"]
    ra = [cls[X] for X in A_SET if cls[X] != "UNRESOLVED"]
    a_ok = len(ra) >= 1 and all(c == "FREE" for c in ra)
    if len(rb) >= 2 and all(c == "CARRIES" for c in rb) and a_ok:
        return "PERIOD-WIDE"
    if "CARRIES" in rb and "FREE" in rb and "PARTIAL" not in rb and a_ok:
        return "SUBSET"
    return "OTHER"


def partitions(sizes: tuple[int, ...]) -> np.ndarray:
    """Every distinct partition of the 12 playlists into groups of the given sizes, groups of equal size unordered:
    an (n, n_groups, 12) bool membership array, with groups in the order of `sizes`."""
    out = []
    idx = tuple(range(NPL))

    def rec(rest, sz, acc):
        if not sz:
            out.append(acc)
            return
        k = sz[0]
        for comb in itertools.combinations(rest, k):
            # equal-sized consecutive groups are unordered: require increasing first members
            if acc and len(acc[-1]) == k and len(sz) and comb[0] < acc[-1][0]:
                continue
            rec(tuple(x for x in rest if x not in comb), sz[1:], acc + [comb])

    rec(idx, tuple(sizes), [])
    A = np.zeros((len(out), len(sizes), NPL), bool)
    for n, p in enumerate(out):
        for g, members in enumerate(p):
            A[n, g, list(members)] = True
    return A


def membership(groups) -> np.ndarray:
    a = np.zeros((len(groups), NPL), bool)
    for g, (_, members) in enumerate(groups):
        a[g, [PL.index(m) for m in members]] = True
    return a


def find(A: np.ndarray, obs: np.ndarray) -> int:
    A = A.astype(bool)
    hit = [n for n in range(len(A)) if all(any(np.array_equal(A[n, g], obs[h]) for g in range(A.shape[1]))
                                           for h in range(len(obs)))]
    if len(hit) != 1:
        raise f0.Stop("R2", f"the observed grouping is matched by {len(hit)} enumerated partitions")
    return hit[0]


def gram(g: np.ndarray, e: np.ndarray, Mi: np.ndarray) -> np.ndarray:
    y = e[:, None] * g
    return y @ Mi @ y.T


def F_all(G: np.ndarray, e: np.ndarray, A: np.ndarray) -> np.ndarray:
    """F(pi) = Q_b(pi) / Q_tot for every partition, from the Gram matrix G_XY = e_X e_Y g_X^T M^-1 g_Y:
    Q_b = sum_g (1_g^T G 1_g) / E_g and Q_tot = sum_X G_XX / e_X."""
    q_tot = float(np.sum(np.diag(G) / e))
    Af = A if A.dtype == float else A.astype(float)
    num = ((Af @ G) * Af).sum(axis=-1)
    E = Af @ e
    return (num / E).sum(axis=1) / q_tot


def p_value(F: np.ndarray, i_obs: int) -> float:
    """The share of partitions with F >= F(pi_obs), ties counted (relative 1e-12) and pi_obs included."""
    return float(np.mean(F >= F[i_obs] * (1.0 - 1e-12)))


def offsets(r: np.ndarray, e: np.ndarray) -> np.ndarray:
    """g_X = r_X / m - 1 with m = sum_X e_X r_X (rows X, columns cells)."""
    m = (e[:, None] * r).sum(axis=0)
    return r / m - 1.0


def sigma_delta(g: np.ndarray, e: np.ndarray) -> np.ndarray:
    V2 = float(np.sum(e ** 2))
    return (e[:, None, None] * np.einsum("xi,xj->xij", g, g)).sum(axis=0) / (1.0 - V2)


def psd(C: np.ndarray) -> tuple[np.ndarray, float]:
    lam, Q = np.linalg.eigh((C + C.T) / 2)
    lost = float(-lam[lam < 0].sum())
    return (Q * np.clip(lam, 0, None)) @ Q.T, lost


def sqrt_psd(C: np.ndarray) -> np.ndarray:
    """A square root L of a PSD matrix (L L^T = C), by its eigendecomposition, so a singular C is fine."""
    lam, Q = np.linalg.eigh((C + C.T) / 2)
    return Q * np.sqrt(np.clip(lam, 0, None))


def q_b(G: np.ndarray, e: np.ndarray, obs: np.ndarray) -> float:
    Af = obs.astype(float)
    return float((np.einsum("gi,ij,gj->g", Af, G, Af) / (Af @ e)).sum())


def nu_eff(e: np.ndarray) -> float:
    V2 = float(np.sum(e ** 2))
    return (1 - V2) ** 2 / (V2 - 2 * float(np.sum(e ** 3)) + V2 ** 2)


def sigma_interval(nu: float) -> list[float]:
    from scipy import stats
    return [float(math.sqrt(nu / stats.chi2.ppf(0.84, nu))), float(math.sqrt(nu / stats.chi2.ppf(0.16, nu)))]


class R2:
    """R2's permutation test and its simulated datasets (section 5)."""

    def __init__(self, e: np.ndarray, Mi: np.ndarray):
        self.e, self.Mi = e, Mi
        self.A = partitions((6, 3, 3)).astype(float)
        self.obs = membership(FLUX_PI)
        self.i_obs = find(self.A, self.obs)

    def test(self, g: np.ndarray) -> tuple[float, float]:
        F = F_all(gram(g, self.e, self.Mi), self.e, self.A)
        return float(F[self.i_obs]), p_value(F, self.i_obs)

    def qb_obs(self, g: np.ndarray) -> float:
        return q_b(gram(g, self.e, self.Mi), self.e, self.obs)

    def g_of(self, delta: np.ndarray, eps: np.ndarray) -> np.ndarray:
        """A dataset: r_X = mu o (1 + delta_X + eps_X); mu is common to the playlists and cancels in g."""
        return offsets(1.0 + delta + eps, self.e)

    def period_offsets(self, g: np.ndarray) -> np.ndarray:
        """G_hat per playlist: its period's per-playlist-recombined double ratio over m, minus 1 (rows X)."""
        out = np.zeros_like(g)
        for _, members in FLUX_PI:
            i = [PL.index(m) for m in members]
            w = self.e[i] / self.e[i].sum()
            out[i] = (w[:, None] * (1.0 + g[i])).sum(axis=0) - 1.0
        return out

    def run(self, g_obs: np.ndarray, noise, rng: np.random.Generator, n: int, scales=R2_SCALES,
            gate: bool = True) -> dict:
        """The calibration, S1 and S2 for observed offsets g_obs. noise(rng) returns one (12, 16) noise draw."""
        noise_g = [self.g_of(0.0, noise(rng)) for _ in range(n)]
        sd0 = sigma_delta(g_obs, self.e) - np.mean([sigma_delta(h, self.e) for h in noise_g], axis=0)
        sd, lost = psd(sd0)
        qn = float(np.mean([self.qb_obs(h) for h in noise_g]))
        qo = self.qb_obs(g_obs)
        c = math.sqrt(max(0.0, 1.0 - qn / qo)) if qo > 0 else 0.0
        G1 = c * self.period_offsets(g_obs)
        Ls = sqrt_psd(sd)
        Lh = Ls / math.sqrt(2.0)

        def share(make):
            return float(np.mean([self.test(self.g_of(make(), noise(rng)))[1] < R2_ALPHA for _ in range(n)]))

        alpha = {}
        if gate:
            for a in scales:
                La = Ls * math.sqrt(a)
                alpha[str(a)] = share(lambda: rng.standard_normal((NPL, N_CELLS)) @ La.T)
        beta1 = share(lambda: G1)
        beta2 = share(lambda: G1 / math.sqrt(2.0) + rng.standard_normal((NPL, N_CELLS)) @ Lh.T) if gate else None
        return {"alpha": alpha, "beta1": beta1, "beta2": beta2, "c": c, "q_noise_mean": qn, "q_obs": qo,
                "sigma_delta": sd, "psd_discarded_trace": lost}


def r2_outcome(p: float, cal: dict, beta1: float, size_bias_g: bool, gate: bool = True) -> str:
    """R2's outcomes, an ordered partition: INCONCLUSIVE / CLUSTERED / EXCHANGEABLE-COMPATIBLE."""
    thr = R2_ALPHA + 3.0 * math.sqrt(R2_ALPHA * (1 - R2_ALPHA) / R2_GATE_N)
    calibrated = (not gate) or all(v <= thr for v in cal.values())
    if size_bias_g or not calibrated:
        return "INCONCLUSIVE"
    if p < R2_ALPHA:
        return "CLUSTERED"
    if beta1 >= R2_BETA:
        return "EXCHANGEABLE-COMPATIBLE"
    return "INCONCLUSIVE"


def r2_gate_threshold() -> float:
    return R2_ALPHA + 3.0 * math.sqrt(R2_ALPHA * (1 - R2_ALPHA) / R2_GATE_N)


# ---------------------------------------------------------------- products


def read_unfold(p: Path, control: str, lat_sha: str, bkg_sha: str, b) -> np.ndarray:
    m = f0.sa_call(control, sa.check_meta, p, "s5p-numerics/1", 42, False,
                   {"construction": "data", "truth": "nominal", "bootstrap_seed": b, "jitter_seed": None,
                    "coords": "float32", "input_npz_sha256": lat_sha, "bkg_dump_sha256": bkg_sha})
    if (m.get("code_sha256") or {}).get("s5p_numerics.py") != sa.sha256(_ND / "s5p_numerics.py"):
        raise f0.Stop(control, f"{p.name}: not made by this deploy's s5p_numerics.py")
    x = sa.xs(p)
    if x.shape != (int(np.prod(sa.s1.fine_shape())),) or not np.all(np.isfinite(x)):
        raise f0.Stop(control, f"{p.name}: xsec_flat shape {x.shape} or non-finite")
    return x


def read_truth(p: Path, control: str, lat_sha: str) -> tuple[np.ndarray, np.ndarray]:
    with np.load(p, allow_pickle=False) as z:
        m = json.loads(str(z["meta_json"]))
        t, v = np.asarray(z["xsec_flat"], float), np.asarray(z["sumw2_flat"], float)
    if (m.get("schema"), m.get("npz_sha256")) != ("s5p-mc-truth-pred/1", lat_sha):
        raise f0.Stop(control, f"{p.name}: not the MC truth of its npz")
    if m.get("code_sha256") != sa.sha256(_ND / "s5p_mc_truth_pred.py"):
        raise f0.Stop(control, f"{p.name}: not made by this deploy's s5p_mc_truth_pred.py")
    return t, v


def staged_path(R: Path, name: str, control: str) -> Path:
    try:
        return ri.staged(R, name)[0]
    except ri.Refuse as e:
        raise f0.Stop(control, str(e)) from None


def common(a, U):
    """S1's assembly and C_resp, from their staged copies (control S)."""
    ns = argparse.Namespace(s1_npz=staged_path(a.r, "s1/s1_assembly.npz", "S"),
                            cresp=staged_path(a.r, "cresp/cresp.npz", "S"))
    return ct.common(ns, U)


def check_5b(deploy: Path, per: str) -> dict:
    return json.loads((deploy / CHECK_REL / f"check_{per}.json").read_text())


def five_b(a, grid: Grid, control: str, pers=("PA", "PB", "PC")) -> dict:
    """5B's staged period unfolds (seed 42 and the period's replicas) and MC truths, meta-checked against 5B's
    committed check receipts."""
    out = {}
    for per in pers:
        rec = check_5b(a.deploy, per)
        ls, bs = rec["files"]["lat_npz"][1], rec["files"]["lat_bkg"][1]
        xs = {}
        for b in (None, *cp.BOOT[per]):
            name = f"5b/unf/{per}/5b_{per}_b{'-' if b is None else b}_j-.npz"
            xs[b] = read_unfold(staged_path(a.r, name, control), control, ls, bs, b)
        t, v = read_truth(staged_path(a.r, f"5b/truth/truth_{per}.npz", control), control, ls)
        out[per] = {"x": xs, "t": t, "tv": v}
    return out


def flux_rec(R: Path, control: str) -> dict:
    try:
        return ri.flux_record(R)
    except ri.Refuse as e:
        raise f0.Stop(control, str(e)) from None


def shares(R: Path, control: str) -> np.ndarray:
    e = flux_rec(R, control)["exposure_share"]
    v = np.array([e[pl] for pl in PL], float)
    if abs(v.sum() - 1.0) > 1e-12 or np.any(v <= 0):
        raise f0.Stop(control, "the exposure shares do not sum to 1")
    return v


# ---------------------------------------------------------------- stage 0


def stage0_branch(s0: float, sig0: float) -> str:
    z = s0 / sig0 if sig0 > 0 else math.inf
    if s0 >= SEES_MIN and z >= SEES_Z:
        return "SEES"
    if abs(z) < ABSENT_Z:
        return "ABSENT"
    return "OTHER"


def run_stage0(a) -> int:
    grid = Grid(a.definition)
    S = common(a, grid.U)
    fb = five_b(a, grid, "Q0", ("PA", "PB"))
    T = {per: grid.regions(fb[per]["t"]) for per in fb}
    D = {per: {b: grid.regions(x) / T[per] for b, x in fb[per]["x"].items()} for per in fb}
    s0 = step(D["PB"][None], D["PA"][None])
    pairs = [step(D["PB"][bb], D["PA"][ba]) for ba, bb in zip(cp.BOOT["PA"], cp.BOOT["PB"])]
    sig0 = float(np.sqrt(np.mean(np.square(np.array(pairs) - s0))))
    branch = stage0_branch(s0, sig0)
    ints = [grid.cells(x) for per in fb for x in fb[per]["x"].values()] + [grid.cells(fb[per]["t"]) for per in fb]
    guard = cp.guarded(S["f"], ints)
    out = {"schema": "fd-rpd-stage0/1", "labels": {"what": LABELS["stage0"]}, "branch": branch, "s0": s0,
           "sigma0": sig0, "z": s0 / sig0 if sig0 > 0 else None, "replica_pair_steps": pairs,
           "rule": {"SEES": f"s0 >= {SEES_MIN} and s0/sigma0 >= {SEES_Z}", "ABSENT": f"|s0|/sigma0 < {ABSENT_Z}",
                    "OTHER": "neither"},
           "regions": {"L": list(L_REGION), "H": list(H_REGION)}, "reference_2d": REF_2D_STEP,
           "inputs_sha256": staged_digests(a.r, [f"5b/unf/{p}/" for p in ("PA", "PB")] + ["5b/truth/", "s1/", "cresp/"]),
           "code_sha256": code_sha(), "argv": sys.argv}
    return ct.write(a, out, guard, [f"[RPD stage 0] s0 {100 * s0:+.3f}% sigma0 {100 * sig0:.3f}%: {branch}"])


def staged_digests(R: Path, prefixes) -> dict:
    rec = json.loads((R / "staged/STAGED.json").read_text())["files"]
    return {k: v["sha256"] for k, v in sorted(rec.items()) if any(k.startswith(p) for p in prefixes)}


# ---------------------------------------------------------------- stage D


def oc_model(e: np.ndarray, s0: float, sig0: float):
    """Section 5's linear-Gaussian model: u_X ~ N(mu_X, sigma_u^2 / e_X); t, tbar and h are linear in u, so their
    covariance is exact. sigma_u reproduces stage 0's sigma0 at the period shares."""
    E = {per: float(sum(e[PL.index(m)] for m in ms)) for per, ms in ri.PERIODS.items()}
    su2 = sig0 ** 2 / (1.0 / E["PB"] + 1.0 / E["PA"])
    ed = dict(zip(PL, e))

    def mean_vec(members):
        v = np.zeros(NPL)
        w = sum(ed[m] for m in members)
        for m in members:
            v[PL.index(m)] = ed[m] / w
        return v
    rows = {}
    for X in PL:
        rows[("t", X)] = np.eye(NPL)[PL.index(X)] - mean_vec(ref_set(X))
    rows["tbar"] = mean_vec(B_SET) - mean_vec(A_SET)
    for X in PL:
        rows[("h", X)] = rows[("t", X)] - rows["tbar"] / 2
    keys = list(rows)
    Amat = np.vstack([rows[k] for k in keys])
    cov = Amat @ np.diag(su2 / e) @ Amat.T
    sig = dict(zip(keys, np.sqrt(np.diag(cov))))
    return keys, Amat, su2, sig, E


def oc_truths(e: np.ndarray, s0: float, E: dict) -> dict:
    ed = dict(zip(PL, e))
    z = {X: 0.0 for X in PL}
    return {"PW": {**z, **{X: s0 for X in B_SET}},
            "S-1G": {**z, "1G": s0 * E["PB"] / ed["1G"]},
            "S-1M": {**z, "1M": s0 * E["PB"] / ed["1M"]},
            "S-1G1M": {**z, "1G": s0 * E["PB"] / (ed["1G"] + ed["1M"]), "1M": s0 * E["PB"] / (ed["1G"] + ed["1M"])}}


def oc_table(e: np.ndarray, s0: float, sig0: float, n: int, seed: int) -> dict:
    keys, Amat, su2, sig, E = oc_model(e, s0, sig0)
    rng = np.random.default_rng(seed)
    out = {}
    for name, mu in oc_truths(e, s0, E).items():
        muv = np.array([mu[X] for X in PL])
        u = muv + rng.standard_normal((n, NPL)) * np.sqrt(su2 / e)
        vals = u @ Amat.T
        idx = {k: i for i, k in enumerate(keys)}
        counts = {"PERIOD-WIDE": 0, "SUBSET": 0, "OTHER": 0, "NOT COMPUTED": 0}
        for row in vals:
            tbar = row[idx["tbar"]]
            if not (tbar > 0 and tbar / sig["tbar"] >= R1_GATE):
                counts["NOT COMPUTED"] += 1
                continue
            cls = {X: classify(row[idx[("t", X)]], sig[("t", X)], row[idx[("h", X)]], sig[("h", X)], tbar)
                   for X in PL}
            counts[pattern(cls)] += 1
        out[name] = {k: v / n for k, v in counts.items()}
    return out


def five_b_readout(deploy: Path) -> dict:
    p = deploy / READOUT_5B[0]
    f0.require("D", p, READOUT_5B[1], "5B period readout")
    return json.loads(p.read_text())


def stage_d_reachability(e: np.ndarray, Mi: np.ndarray, ro5: dict, seed: int, outer: int, inner: int,
                         budget_s: float, clock=time.monotonic) -> dict:
    """R2's reachability under T1-T3 (section 5): Gaussian noise from 5B's committed per-period noise scaled by
    sqrt(E_P / e_X), the real M, the gate off."""
    r2 = R2(e, Mi)
    V2 = float(np.sum(e ** 2))
    C5 = np.asarray(ro5["C_PL5D"]["C_PL5D_rel"], float)
    sT1, _ = psd(C5 / V2)
    LT1 = sqrt_psd(sT1)
    E = {per: float(sum(e[PL.index(m)] for m in ms)) for per, ms in ri.PERIODS.items()}
    g5 = {per: np.asarray(ro5["g_vs_5A"]["periods"][per]["g_5b"], float) for per in ri.PERIODS}
    sn = {per: np.asarray(ro5["g_vs_5A"]["periods"][per]["g_5b_noise_sigma"], float) for per in ri.PERIODS}
    noise_sd = np.vstack([sn[GROUP[X]] * math.sqrt(E[GROUP[X]] / e[i]) for i, X in enumerate(PL)])
    T2 = np.vstack([g5[GROUP[X]] for X in PL])

    def noise(rng):
        return rng.standard_normal((NPL, N_CELLS)) * noise_sd

    truths = {"T1": lambda rng: rng.standard_normal((NPL, N_CELLS)) @ LT1.T,
              "T2": lambda rng: T2,
              "T3": lambda rng: T2 / math.sqrt(2.0) + rng.standard_normal((NPL, N_CELLS)) @ LT1.T / math.sqrt(2.0)}
    rng = np.random.default_rng(seed)
    t0 = clock()
    res = {k: {"CLUSTERED": 0, "EXCHANGEABLE-COMPATIBLE": 0, "INCONCLUSIVE": 0, "n": 0} for k in truths}
    alphas = {k: [] for k in truths}
    stopped = False
    for i in range(outer):
        for name, make in truths.items():
            if clock() - t0 > budget_s:
                stopped = True
                break
            g = r2.g_of(make(rng), noise(rng))
            _, p = r2.test(g)
            gate_here = i < STAGE_D_ALPHA_OUTER
            sim = r2.run(g, noise, rng, inner, gate=gate_here)
            if gate_here:
                alphas[name].append(sim["alpha"])
            res[name][r2_outcome(p, {}, sim["beta1"], False, gate=False)] += 1
            res[name]["n"] += 1
        if stopped:
            break
    probs = {k: {o: (v[o] / v["n"] if v["n"] else None) for o in ("CLUSTERED", "EXCHANGEABLE-COMPATIBLE",
                                                                   "INCONCLUSIVE")} | {"n": v["n"]}
             for k, v in res.items()}
    alpha = {k: ({str(a): float(np.mean([d[str(a)] for d in v])) for a in R2_SCALES} | {"n_outer": len(v)} if v else None)
             for k, v in alphas.items()}
    return {"probabilities": probs, "stopped_at_budget": stopped, "seconds": round(clock() - t0, 1),
            "alpha_at_inner_descriptive": alpha,
            "noise_sd_rel_median": float(np.median(noise_sd)), "T1_sigma_rel_median": float(np.median(np.sqrt(np.diag(sT1))))}


def run_staged(a) -> int:
    s0p = a.r / "control/stage0.json"
    s0rec = json.loads(s0p.read_text()) if s0p.is_file() else {}
    if s0rec.get("schema") != "fd-rpd-stage0/1":
        raise f0.Stop("D", "no stage 0 record")
    grid = Grid(a.definition)
    S = common(a, grid.U)
    e = shares(a.r, "D")
    s0, sig0 = float(s0rec["s0"]), float(s0rec["sigma0"])
    oc = oc_table(e, s0, sig0, STAGE_D_R1_DRAWS, SEED + 2000)
    oc7 = oc_table(e, REF_2D_STEP, sig0, STAGE_D_R1_DRAWS, SEED + 2000)
    rule_pw = oc["PW"]["PERIOD-WIDE"] < STAGE_D_RULE_PW
    best_sub = max(oc[k]["SUBSET"] for k in ("S-1G", "S-1M", "S-1G1M"))
    rule_sub = best_sub < STAGE_D_RULE_PW
    ro5 = five_b_readout(a.deploy)
    M = S["M"] / S["ff"]
    reach = stage_d_reachability(e, np.linalg.inv(M), ro5, SEED + 3000, a.outer, a.inner, a.budget)
    n_t1 = reach["probabilities"]["T1"]["n"]
    p_ec = reach["probabilities"]["T1"]["EXCHANGEABLE-COMPATIBLE"]
    ec_verdict = None if n_t1 < STAGE_D_MIN_OUTER else bool(p_ec < STAGE_D_RULE_EC)
    out = {"schema": "fd-rpd-stageD/1", "labels": {"what": LABELS["staged"]},
           "stage0": {"branch": s0rec["branch"], "s0": s0, "sigma0": sig0},
           "R1_operating_characteristics": {"at_s0": oc, "at_7pct": oc7, "draws": STAGE_D_R1_DRAWS,
                                            "seed": SEED + 2000, "note": "N0's UNRESOLVED clause is not modelled"},
           "R1_rules": {"drop_PERIOD_WIDE": rule_pw, "drop_SUBSET": rule_sub, "P_PW_given_PW": oc["PW"]["PERIOD-WIDE"],
                        "best_P_SUBSET_given_subset_truth": best_sub, "threshold": STAGE_D_RULE_PW},
           "R2_reachability": {**reach, "outer": a.outer, "inner": a.inner, "seed": SEED + 3000, "gate": "off"},
           "R2_rule": {"flag_12_playlist_wording_not_expected": ec_verdict, "P_EC_given_T1": p_ec,
                       "threshold": STAGE_D_RULE_EC, "min_outer_for_a_verdict": STAGE_D_MIN_OUTER},
           "exposure_share": dict(zip(PL, e.tolist())),
           "inputs_sha256": {"stage0": sa.sha256(a.r / "control/stage0.json"), "flux_record": sa.sha256(a.r / "flux/F1.json"),
                             "readout_5b": READOUT_5B[1]},
           "code_sha256": code_sha(), "argv": sys.argv}
    guard = cp.guarded(S["f"], [])
    lines = [f"[RPD stage D] P(PW|PW) {oc['PW']['PERIOD-WIDE']:.3f} drop {rule_pw}; best P(SUBSET) {best_sub:.3f} "
             f"drop {rule_sub}; P(EC|T1) {p_ec} (n {n_t1}) flag {ec_verdict}"]
    return ct.write(a, out, guard, lines)


# ---------------------------------------------------------------- controls (C1, K2', N0-P)


C1_CONCAT = ("MCgen", "MCreco", "measured", "pass_reco", "pass_truth")
C1_SCALED = ("w_truth", "w_reco")
C1_EQUAL = ("axes", "edges_0", "edges_1", "edges_2", "edges_3", "edges_4", "nedges", "n_nucleons")
C1_HIST_REL, C1_W_REL = 1e-9, 1e-12
C1_MW_SHARE = 0.999            # part 2's deviation 1: measured_weights agreement share (config R does not read it)


def receipt(R: Path, X: str, control: str) -> dict:
    p = R / ri.playlist_paths(X)["receipt"]
    if not p.is_file():
        raise f0.Stop(control, f"no check receipt {p}")
    r = json.loads(p.read_text())
    if (r.get("schema"), r.get("playlist")) != ("fd-rpd-inputs/1", X):
        raise f0.Stop(control, f"{p.name}: schema or playlist")
    if (r.get("code_sha256") or {}).get("fd_rpd_inputs.py") != sa.sha256(Path(ri.__file__).resolve()):
        raise f0.Stop(control, f"{p.name}: not made by this deploy's fd_rpd_inputs.py")
    for k in ("lat_npz", "lat_bkg", "truth", "flux", "loop"):
        f0.require(control, Path(r["files"][k][0]), r["files"][k][1], f"{X} {k}")
    return r


def scaled_equal(a: np.ndarray, b: np.ndarray, ratio: float) -> bool:
    """a == b * ratio to C1_W_REL relative per entry, exactly where b is 0."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != b.shape:
        return False
    z = b == 0
    if np.any(a[z] != 0):
        return False
    return bool(np.all(np.abs(a[~z] / (b[~z] * ratio) - 1.0) <= C1_W_REL))


def hist_equal(a: np.ndarray, b: np.ndarray) -> bool:
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != b.shape:
        return False
    z = b == 0
    return bool(np.all(a[z] == 0) and np.all(np.abs(a[~z] / b[~z] - 1.0) <= C1_HIST_REL))


def load_all(p: Path) -> dict:
    """Every array of an npz, read once (an NpzFile decompresses on every access)."""
    with np.load(p, allow_pickle=True) as z:
        return {k: z[k] for k in z.files}


def c1(R: Path, recs: dict, fr: dict) -> dict:
    """C1 (section 4): per key, the predicate part 1 fixes."""
    lat0 = load_all(staged_path(R, "mp1/lat_zero.npz", "C1"))
    bkg0 = load_all(staged_path(R, "mp1/lat_zero_bkg.npz", "C1"))
    lats = {X: load_all(Path(recs[X]["files"]["lat_npz"][0])) for X in PL}
    bkgs = {X: load_all(Path(recs[X]["files"]["lat_bkg"][0])) for X in PL}
    s = {X: recs[X]["data_pot"] / recs[X]["mc_pot"] for X in PL}
    s_all = sum(recs[X]["data_pot"] for X in PL) / sum(recs[X]["mc_pot"] for X in PL)
    res = {}
    for k in C1_CONCAT:
        res[k] = ri.pi.same_array(np.concatenate([lats[X][k] for X in PL]), lat0[k])
    res["bkg_reco"] = ri.pi.same_array(np.concatenate([bkgs[X]["bkg_reco"] for X in PL]), bkg0["bkg_reco"])
    for k, src, ref in (("w_truth", lats, lat0), ("w_reco", lats, lat0), ("bkg_w", bkgs, bkg0)):
        n = [len(src[X][k]) for X in PL]
        if sum(n) != len(ref[k]):
            res[k] = False
            continue
        cuts = np.cumsum([0] + n)
        res[k] = all(scaled_equal(src[X][k], ref[k][cuts[i]:cuts[i + 1]], s[X] / s_all) for i, X in enumerate(PL))
    res["denom_nd"] = hist_equal(sum(lats[X]["denom_nd"] * (s_all / s[X]) for X in PL), lat0["denom_nd"])
    res["bkg_nd"] = hist_equal(sum(bkgs[X]["bkg_nd"] * (s_all / s[X]) for X in PL), bkg0["bkg_nd"])
    res["data_pot"] = abs(sum(float(lats[X]["data_pot"]) for X in PL) / float(lat0["data_pot"]) - 1.0) <= ri.POT_REL
    res["global_equal"] = all(all(ri.pi.same_array(lats[X][k], lat0[k]) for X in PL) for k in C1_EQUAL)
    res["flux"] = all(ri.rel_max(lats[X]["flux"], fr["per_playlist"][X]["contents"]) <= ri.REL_FLUX for X in PL)
    mw = {}
    for X in PL:
        z = lats[X]
        edges = [np.asarray(z[f"edges_{i}"], float) for i in range(int(z["nedges"]))]
        mw[X] = measured_weights_agreement(z, bkgs[X], edges)
    res["measured_weights_self_consistent"] = all(v >= C1_MW_SHARE for v in mw.values())
    return {"pass": all(bool(v) for v in res.values()), "keys": {k: bool(v) for k, v in res.items()},
            "measured_weights_share_equal": mw, "measured_weights_share_required": C1_MW_SHARE,
            "s_all": s_all, "s_ratio": {X: s[X] / s_all for X in PL}}


def measured_weights_agreement(z, b, edges) -> float:
    """The share of data rows whose measured_weights equals its recomputation from the playlist's own data and
    background histograms (unfold_nd_omnifold_unbinned.build_measured_training_nd's rule, vectorized) to 1e-12.
    The dump bins float64 coordinates and stores them as float32, so a row on a bin edge can move bin here: an exact
    recomputation is not available from the npz alone (part 2's deviation 1)."""
    meas = np.asarray(z["measured"], float)
    data_nd = ri.histnd_counts([meas[:, i] for i in range(meas.shape[1])], np.ones(len(meas)), edges)
    bkg_nd = np.asarray(b["bkg_nd"], float)
    target = np.maximum(0.0, data_nd - bkg_nd)
    idx = [np.digitize(meas[:, i], e) - 1 for i, e in enumerate(edges)]
    inside = np.all([(ix >= 0) & (ix < len(e) - 1) for ix, e in zip(idx, edges)], axis=0)
    w = np.zeros(len(meas))
    ii = tuple(np.clip(ix, 0, len(e) - 2) for ix, e in zip(idx, edges))
    d = data_nd[ii]
    ok = inside & (d > 0)
    w[ok] = target[ii][ok] / d[ok]
    got = np.asarray(z["measured_weights"], float)
    if got.shape != w.shape:
        return 0.0
    return float(np.mean(np.isclose(got, w, rtol=1e-12, atol=0.0)))


def k2(R: Path) -> dict:
    """K2' (section 4): this deploy's PC unfolds against 5B's, np.array_equal on xsec_flat."""
    out = {}
    lat_sha = ri.staged(R, "5b/dumps/lat_PC.npz")[1]
    bkg_sha = ri.staged(R, "5b/dumps/lat_PC_bkg.npz")[1]
    for b in K2_SEEDS:
        tag = f"b{'-' if b is None else b}_j-"
        mine = R / "unf-k2" / f"rpd_k2_PC_{tag}.npz"
        ref = staged_path(R, f"5b/unf/PC/5b_PC_{tag}.npz", "K2")
        if not mine.is_file():
            raise f0.Stop("K2", f"missing {mine}")
        x = read_unfold(mine, "K2", lat_sha, bkg_sha, b)
        out[str(b)] = bool(np.array_equal(x, sa.xs(ref)))
    return {"pass": all(out.values()), "by_seed": out}


def n0p(R: Path, fr: dict) -> dict:
    """N0-P (section 4) for every partition."""
    lat0 = load_all(staged_path(R, "mp1/lat_zero.npz", "N0P"))
    bkg0 = load_all(staged_path(R, "mp1/lat_zero_bkg.npz", "N0P"))
    edges = [np.asarray(lat0[f"edges_{i}"], float) for i in range(int(lat0["nedges"]))]
    o_all = ri.truth_sum(lat0["MCgen"], lat0["pass_truth"], lat0["w_truth"], edges)
    dn_all = np.asarray(lat0["denom_nd"], float)
    e = np.array([fr["exposure_share"][pl] for pl in PL])
    parts = {}
    for p in range(1, ri.N_PART + 1):
        rp = R / ri.n0_paths(p, 0)["receipt"]
        if not rp.is_file():
            raise f0.Stop("N0P", f"no N0 receipt {rp}")
        rec = json.loads(rp.read_text())
        f0.require("N0P", Path(rec["assign"][0]), rec["assign"][1], f"partition {p} assignment")
        asg = load_all(Path(rec["assign"][0]))
        z = [load_all(Path(q["npz"][0])) for q in rec["pseudo"]]
        b = [load_all(Path(q["bkg"][0])) for q in rec["pseudo"]]
        for q in rec["pseudo"]:
            f0.require("N0P", Path(q["npz"][0]), q["npz"][1], f"p{p} k{q['k']} npz")
            f0.require("N0P", Path(q["bkg"][0]), q["bkg"][1], f"p{p} k{q['k']} bkg")
        chk = {}
        for tree, keys, src, ref in (("data", ri.DATA_KEYS, z, lat0), ("signal", ri.SIGNAL_KEYS, z, lat0),
                                     ("background", ("bkg_reco", "bkg_w"), b, bkg0)):
            a_ = asg[tree]
            ok = len(a_) == len(ref[keys[0]])
            for key in keys:
                back = np.empty_like(np.asarray(ref[key]))
                for k in range(NPL):
                    sel = a_ == k
                    part = np.asarray(src[k][key])
                    if part.shape[0] != int(sel.sum()):
                        ok = False
                        break
                    back[sel] = part
                ok = ok and ri.pi.same_array(back, ref[key])
            chk[f"{tree}_rows_bitwise_in_order"] = bool(ok)
        chk["data_pot_sum"] = abs(sum(float(x["data_pot"]) for x in z) / float(lat0["data_pot"]) - 1.0) <= ri.POT_REL
        chk["denom_sum"] = hist_equal(sum(np.asarray(x["denom_nd"], float) for x in z), dn_all)
        chk["bkg_nd_sum"] = hist_equal(sum(np.asarray(x["bkg_nd"], float) for x in b), np.asarray(bkg0["bkg_nd"], float))
        n_data = len(lat0["measured"])
        shares_ok = []
        comp_ok = []
        for k in range(NPL):
            nk = int(np.sum(asg["data"] == k))
            sd = math.sqrt(n_data * e[k] * (1 - e[k]))
            shares_ok.append(abs(nk - n_data * e[k]) <= 5 * sd)
            o_k = ri.truth_sum(z[k]["MCgen"], z[k]["pass_truth"], z[k]["w_truth"], edges)
            dk = np.asarray(z[k]["denom_nd"], float)
            pos = o_k > 0
            with np.errstate(divide="ignore", invalid="ignore"):
                same = np.abs((o_k[pos] / dk[pos]) / (o_all[pos] / dn_all[pos]) - 1.0) <= 1e-12
            comp_ok.append(bool(np.all(same) and np.all(o_k[dk == 0] == 0)))
        chk["shares_within_5_sigma"] = all(shares_ok)
        chk["completeness_equal"] = all(comp_ok)
        chk["globals_equal"] = all(all(ri.pi.same_array(x[k], lat0[k]) for k in ri.GLOBAL_KEYS) for x in z)
        chk["measured_weights_present"] = all("measured_weights" in x for x in z)
        chk["bkg_meta"] = all(json.loads(str(bb["meta"]))["npz_sha256"] == q["npz"][1] for bb, q in zip(b, rec["pseudo"]))
        parts[str(p)] = {"pass": all(chk.values()), "checks": chk}
    return {"pass": all(v["pass"] for v in parts.values()), "partitions": parts}


def run_controls(a) -> int:
    grid = Grid(a.definition)
    S = common(a, grid.U)
    fr = flux_rec(a.r, "C1")
    recs = {X: receipt(a.r, X, "C1") for X in PL}
    c1r, k2r, n0r = c1(a.r, recs, fr), k2(a.r), n0p(a.r, fr)
    verdict = "PASS" if (c1r["pass"] and k2r["pass"] and n0r["pass"]) else "FAIL"
    out = {"schema": "fd-rpd-controls/1", "labels": {"what": LABELS["controls"]}, "verdict": verdict,
           "C1": c1r, "K2prime": k2r, "N0P": n0r,
           "inputs_sha256": {"receipts": {X: sa.sha256(a.r / ri.playlist_paths(X)["receipt"]) for X in PL},
                             "flux_record": sa.sha256(a.r / "flux/F1.json")},
           "code_sha256": code_sha(), "argv": sys.argv}
    rc = ct.write(a, out, cp.guarded(S["f"], []), [f"[RPD controls] C1 {c1r['pass']} K2' {k2r['pass']} "
                                                   f"N0-P {n0r['pass']}: {verdict}"])
    return rc if verdict == "PASS" else 1


def run_gate(a) -> int:
    """Job A only after F1's PASS and the stage 0 and stage D records; job B only after this deploy's controls PASS."""
    if a.stage == "a":
        flux_rec(a.r, "G")
        for name, schema in (("stage0.json", "fd-rpd-stage0/1"), ("stageD.json", "fd-rpd-stageD/1")):
            p = a.r / "control" / name
            if not p.is_file() or json.loads(p.read_text()).get("schema") != schema:
                raise f0.Stop("G", f"no {name}")
    else:
        p = a.r / "control/controls.json"
        if not p.is_file():
            raise f0.Stop("G", f"no {p}")
        r = json.loads(p.read_text())
        if (r.get("schema"), r.get("verdict")) != ("fd-rpd-controls/1", "PASS"):
            raise f0.Stop("G", "controls.json does not record a PASS")
        if (r.get("code_sha256") or {}).get("fd_rpd.py") != sa.sha256(Path(__file__).resolve()):
            raise f0.Stop("G", "controls.json was not made by this deploy's fd_rpd.py")
        for X in PL:
            if r["inputs_sha256"]["receipts"][X] != sa.sha256(a.r / ri.playlist_paths(X)["receipt"]):
                raise f0.Stop("G", f"{X}'s receipt is not the one the controls read")
    print(f"PASS gate {a.stage}", flush=True)
    return 0


# ---------------------------------------------------------------- readout


def load_playlists(a, grid: Grid, recs: dict) -> dict:
    """Each playlist's seed-42 unfold and its 30 replicas, and its MC truth with its finite-MC variance."""
    out = {}
    for X in PL:
        ls, bs = recs[X]["files"]["lat_npz"][1], recs[X]["files"]["lat_bkg"][1]
        d = a.r / ri.playlist_paths(X)["unf"]
        want = sorted(f"rpd_{X}_b{'-' if b is None else b}_j-.npz" for b in (None, *REP[X]))
        have = sorted(p.name for p in d.glob("*.npz"))
        if have != want:
            raise f0.Stop("Q1", f"{X}: the unfold directory holds {len(have)} files, not the declared {len(want)}")
        xs = {b: read_unfold(d / f"rpd_{X}_b{'-' if b is None else b}_j-.npz", "Q1", ls, bs, b) for b in (None, *REP[X])}
        t, v = read_truth(Path(recs[X]["files"]["truth"][0]), "Q2", ls)
        out[X] = {"x": xs, "t": t, "tv": v}
    return out


def load_n0(a, grid: Grid) -> list[dict]:
    parts = []
    for p in range(1, ri.N_PART + 1):
        rec = json.loads((a.r / ri.n0_paths(p, 0)["receipt"]).read_text())
        ks = []
        for q in rec["pseudo"]:
            k = q["k"]
            x = read_unfold(a.r / ri.n0_paths(p, k)["unf"] / f"rpd_n0_p{p:02d}_k{k:02d}_b-_j-.npz", "N0",
                            q["npz"][1], q["bkg"][1], None)
            t, v = read_truth(Path(q["truth"][0]), "N0", q["npz"][1])
            ks.append({"x": x, "t": t, "tv": v})
        parts.append(ks)
    return parts


def t_noise(grid: Grid, prod: dict, e: dict, f) -> float:
    """First-order T noise of a quantity f(D) computed from regions: sum over members and regions of
    (d f / d ln T_{Y,R})^2 relvar(T_{Y,R})."""
    T = {X: grid.regions(prod[X]["t"]) for X in prod}
    rv = {X: grid.region_var(prod[X]["tv"]) / T[X] ** 2 for X in prod}
    X0 = {X: grid.regions(prod[X]["x"][None]) for X in prod}
    base = f({X: X0[X] / T[X] for X in prod})
    var = 0.0
    for Y in prod:
        for r in (0, 1):
            Tp = T[Y].copy()
            Tp[r] *= 1 + 1e-6
            D = {X: X0[X] / (Tp if X == Y else T[X]) for X in prod}
            der = (f(D) - base) / 1e-6
            var += der ** 2 * rv[Y][r]
    return var


def run_readout(a) -> int:
    grid = Grid(a.definition)
    S = common(a, grid.U)
    f = S["f"]
    cj = json.loads((a.r / "control/controls.json").read_text())
    if (cj.get("schema"), cj.get("verdict")) != ("fd-rpd-controls/1", "PASS"):
        raise f0.Stop("Q0", "the controls did not PASS")
    s0rec = json.loads((a.r / "control/stage0.json").read_text())
    sdrec = json.loads((a.r / "control/stageD.json").read_text())
    ev = shares(a.r, "Q2")
    e = dict(zip(PL, ev))
    recs = {X: receipt(a.r, X, "Q1") for X in PL}
    prod = load_playlists(a, grid, recs)
    n0 = load_n0(a, grid)
    ints = [grid.cells(x) for X in prod for x in prod[X]["x"].values()] + [grid.cells(prod[X]["t"]) for X in prod]
    ints += [grid.cells(k["x"]) for part in n0 for k in part] + [grid.cells(k["t"]) for part in n0 for k in part]
    for v in ints:
        if not np.all(v > 0):
            raise f0.Stop("Q3", "a non-positive unfold or MC-truth cell integral")
    for X in prod:
        if not np.all(grid.regions(prod[X]["x"][None]) > 0) or not np.all(grid.regions(prod[X]["t"]) > 0):
            raise f0.Stop("Q3", f"{X}: a non-positive region integral")
    guard = cp.guarded(f, ints)
    M = S["M"] / S["ff"]
    Mi = np.linalg.inv(M)
    r2 = R2(ev, Mi)
    small = [i for i, X in enumerate(PL) if ev[i] < N0_SMALL]

    # ---- the 16-cell double ratios and their replica noise
    Tc = {X: grid.cells(prod[X]["t"]) for X in PL}
    tcv = {X: grid.cell_var(prod[X]["tv"]) / Tc[X] ** 2 for X in PL}
    r = np.vstack([grid.cells(prod[X]["x"][None]) / Tc[X] for X in PL])
    g = offsets(r, ev)
    dev = {X: np.vstack([grid.cells(prod[X]["x"][b]) / Tc[X] for b in REP[X]]) for X in PL}
    dev = {X: (v / v.mean(axis=0) - 1.0) * math.sqrt(N_REP / (N_REP - 1)) for X, v in dev.items()}

    def noise(rng):
        k = rng.integers(0, N_REP, NPL)
        eps = np.vstack([dev[X][k[i]] for i, X in enumerate(PL)])
        return eps + rng.standard_normal((NPL, N_CELLS)) * np.sqrt(np.vstack([tcv[X] for X in PL]))

    # ---- N0
    n0r = n0_reading(grid, n0, ev, Mi, r2, small)
    # ---- R2
    F_obs, p_flux = r2.test(g)
    A_era = partitions((5, 3, 2, 2))
    era = membership((ERA_PI[0], ERA_PI[3], ERA_PI[1], ERA_PI[2]))
    i_era = find(A_era, era)
    F_era = F_all(gram(g, ev, Mi), ev, A_era)
    p_era = p_value(F_era, i_era)
    rng = np.random.default_rng(SEED)
    sim = r2.run(g, noise, rng, R2_GATE_N)
    outcome = r2_outcome(p_flux, sim["alpha"], sim["beta1"], n0r["SIZE_BIAS_g"])
    if n0r["SIZE_BIAS_g"]:
        gb = g.copy()
        gb[small] -= np.asarray(n0r["b_cells"])
        n0r["effect"] = {"p_flux_with_bias_removed": r2.test(gb)[1], "F_with_bias_removed": r2.test(gb)[0]}
    # ---- R3
    V2 = float(np.sum(ev ** 2))
    k12 = V2 / (1 - V2)
    C12 = k12 * (ev[:, None, None] * np.einsum("xi,xj->xij", g, g)).sum(axis=0)
    noise_g = [r2.g_of(0.0, noise(rng)) for _ in range(R2_GATE_N)]
    C12n = np.mean([k12 * (ev[:, None, None] * np.einsum("xi,xj->xij", h, h)).sum(axis=0) for h in noise_g], axis=0)
    C12d, lost12 = psd(C12 - C12n)
    c5, c5n = five_b_block(a, grid)
    C5d, lost5 = psd(c5 - c5n)
    nu = nu_eff(ev)
    rho_raw = math.sqrt(np.trace(Mi @ C12) / np.trace(Mi @ c5))
    rho_deb = math.sqrt(np.trace(Mi @ C12d) / np.trace(Mi @ C5d)) if np.trace(Mi @ C5d) > 0 else None
    # ---- R1 (only under SEES, if not NOT COMPUTED)
    r1 = r1_reading(grid, prod, e, n0r, small, s0rec, sdrec)
    out = {"schema": "fd-rpd-readout/1",
           "labels": {k: LABELS[k] for k in ("r1", "r2", "r3", "not_citable_for")},
           "stage0": {k: s0rec[k] for k in ("branch", "s0", "sigma0")},
           "stageD_rules": {"R1": sdrec["R1_rules"], "R2": sdrec["R2_rule"]},
           "exposure_share": e, "cells": ct.cells(),
           "N0": n0r,
           "R1": r1,
           "R2": {"outcome": outcome, "F_flux": F_obs, "p_flux": p_flux, "p_era": p_era, "F_era": float(F_era[i_era]),
                  "n_partitions": {"flux": int(len(r2.A)), "era": int(len(A_era))},
                  "alpha": sim["alpha"], "calibration_threshold": r2_gate_threshold(), "beta1": sim["beta1"],
                  "beta2": sim["beta2"], "c": sim["c"], "psd_discarded_trace_sigma_delta": sim["psd_discarded_trace"],
                  "g": g.tolist(), "median_abs_g_small": float(np.median(np.abs(g[small]))) if small else None,
                  "datasets": R2_GATE_N, "seed": SEED},
           "R3": {"read": outcome == "EXCHANGEABLE-COMPATIBLE", "label": LABELS["r3"],
                  "C_PL12_rel_raw": C12.tolist(), "C_PL12_rel_debiased": C12d.tolist(),
                  "psd_discarded_trace": lost12, "sigma_rel_raw": np.sqrt(np.diag(C12)).tolist(),
                  "sigma_ratio_raw_to_5d": (np.sqrt(np.diag(C12)) / np.sqrt(np.diag(c5))).tolist(),
                  "sigma_ratio_raw_to_5d_summary": ct.summary(np.sqrt(np.diag(C12)) / np.sqrt(np.diag(c5))),
                  "rho_raw": rho_raw, "rho_deb": rho_deb, "C_PL5D_psd_discarded_trace": lost5,
                  "nu12": nu, "interval_68": sigma_interval(nu), "k12": k12},
           "inputs_sha256": {"controls": sa.sha256(a.r / "control/controls.json"),
                             "stage0": sa.sha256(a.r / "control/stage0.json"),
                             "stageD": sa.sha256(a.r / "control/stageD.json"),
                             "flux_record": sa.sha256(a.r / "flux/F1.json")},
           "code_sha256": code_sha(), "argv": sys.argv}
    lines = [f"[RPD] N0 SIZE-BIAS-g {n0r['SIZE_BIAS_g']} SIZE-BIAS-t {n0r['SIZE_BIAS_t']}",
             f"[RPD] R1 {r1['outcome']}", f"[RPD] R2 {outcome}: p_flux {p_flux:.4f} beta1 {sim['beta1']:.3f} "
             f"p_era {p_era:.4f}", f"[RPD] R3 rho_raw {rho_raw:.4f} nu12 {nu:.3f}"]
    return ct.write(a, out, guard, lines)


def five_b_block(a, grid: Grid) -> tuple[np.ndarray, np.ndarray]:
    """C_PL,5D and its replica-noise expectation, rebuilt from 5B's staged products exactly as fd_ct_periods.py
    builds them, and required equal to 5B's committed block to 1e-9 relative."""
    fb = five_b(a, grid, "Q5")
    ro5 = five_b_readout(a.deploy)
    e5 = ro5["constants"]["exposure_share"]
    T = {P: grid.cells(fb[P]["t"]) for P in fb}
    x = {P: grid.cells(fb[P]["x"][None]) for P in fb}
    D = {P: [grid.cells(fb[P]["x"][b]) / x[P] - 1.0 for b in cp.BOOT[P]] for P in fb}
    rr = {P: x[P] / T[P] for P in fb}
    mbar = sum(e5[P] * rr[P] for P in fb)
    g5 = {P: rr[P] / mbar - 1.0 for P in fb}
    V2 = sum(v * v for v in e5.values())
    k = V2 / (1 - V2)
    C = k * sum(e5[P] * np.outer(g5[P], g5[P]) for P in fb)
    gn = [{P: D[P][i] - sum(e5[Y] * D[Y][i] for Y in fb) for P in fb} for i in range(cp.N_BOOT)]
    Cn = np.mean([k * sum(e5[P] * np.outer(h[P], h[P]) for P in fb) for h in gn], axis=0)
    ref = np.asarray(ro5["C_PL5D"]["C_PL5D_rel"], float)
    if not np.allclose(C, ref, rtol=1e-9, atol=1e-9 * np.abs(ref).max()):
        raise f0.Stop("Q5", "C_PL,5D rebuilt from the staged 5B products is not the committed block")
    return C, Cn


def n0_reading(grid: Grid, n0: list, ev: np.ndarray, Mi: np.ndarray, r2: R2, small: list) -> dict:
    """N0's reading (section 4): the small pseudo-playlists' mean 16-cell offset and mean R1 step over the
    partitions, against t_29 thresholds; the slopes against e; N0's F values."""
    e = dict(zip(PL, ev))
    gs, ts, Fs, all_g, all_t = [], [], [], [], []
    for part in n0:
        T = {X: grid.cells(part[i]["t"]) for i, X in enumerate(PL)}
        r = np.vstack([grid.cells(part[i]["x"]) / T[X] for i, X in enumerate(PL)])
        g = offsets(r, ev)
        Dr = {X: grid.regions(part[i]["x"]) / grid.regions(part[i]["t"]) for i, X in enumerate(PL)}
        q = r1_quantities(Dr, e)
        gs.append(g[small])
        ts.append([q["t"][PL[i]] for i in small])
        all_g.append(g)
        all_t.append([q["t"][X] for X in PL])
        Fs.append(r2.test(g)[0])
    G = np.concatenate(gs)                # (30, 16)
    Tt = np.concatenate([np.asarray(t) for t in ts])
    n = len(Tt)
    b, se = G.mean(axis=0), G.std(axis=0, ddof=1) / math.sqrt(n)
    bt, set_ = float(Tt.mean()), float(Tt.std(ddof=1) / math.sqrt(n))
    zc = np.where(se > 0, b / np.where(se > 0, se, 1), 0.0)
    zt = bt / set_ if set_ > 0 else 0.0
    eall = np.tile(ev, len(n0))
    gall = np.concatenate(all_g)
    tall = np.concatenate([np.asarray(t) for t in all_t])
    slope_g = [float(np.polyfit(eall, gall[:, c], 1)[0]) for c in range(N_CELLS)]
    slope_t = float(np.polyfit(eall, tall, 1)[0])
    return {"small": [PL[i] for i in small], "n_draws": n, "b_cells": b.tolist(), "se_cells": se.tolist(),
            "z_cells": zc.tolist(), "b_step": bt, "se_step": set_, "z_step": zt,
            "single_draw_sigma_cells": G.std(axis=0, ddof=1).tolist(), "single_draw_sigma_step": float(Tt.std(ddof=1)),
            "SIZE_BIAS_g": bool(np.any(np.abs(zc) > N0_T_CELL)), "SIZE_BIAS_t": bool(abs(zt) > N0_T_STEP),
            "thresholds": {"cell": N0_T_CELL, "step": N0_T_STEP}, "slope_g_vs_e": slope_g, "slope_t_vs_e": slope_t,
            "F_flux_per_partition": Fs,
            "note": "the t_29 reference is approximate: 3 playlists of unequal variance x 10 partitions; not firing "
                    "is not a clearance"}


def r1_reading(grid: Grid, prod: dict, e: dict, n0r: dict, small: list, s0rec: dict, sdrec: dict) -> dict:
    """R1 (section 5), only under stage 0's SEES; classes, the pattern, and stage D's drops applied."""
    if s0rec["branch"] != "SEES":
        return {"outcome": "NOT COMPUTED", "why": f"stage 0 is {s0rec['branch']}"}
    T = {X: grid.regions(prod[X]["t"]) for X in PL}
    D0 = {X: grid.regions(prod[X]["x"][None]) / T[X] for X in PL}
    q0 = r1_quantities(D0, e)
    reps = [r1_quantities({X: grid.regions(prod[X]["x"][REP[X][k]]) / T[X] for X in PL}, e) for k in range(N_REP)]

    def sd(vals):
        return float(np.std(np.asarray(vals), ddof=1))
    tn = {X: t_noise(grid, prod, e, lambda D, X=X: r1_quantities(D, e)["t"][X]) for X in PL}
    hn = {X: t_noise(grid, prod, e, lambda D, X=X: r1_quantities(D, e)["h"][X]) for X in PL}
    tbn = t_noise(grid, prod, e, lambda D: r1_quantities(D, e)["tbar"])
    sig = {X: math.sqrt(sd([q["t"][X] for q in reps]) ** 2 + tn[X]) for X in PL}
    sigh = {X: math.sqrt(sd([q["h"][X] for q in reps]) ** 2 + hn[X]) for X in PL}
    sig_tbar = math.sqrt(sd([q["tbar"] for q in reps]) ** 2 + tbn)
    tbar = q0["tbar"]
    base = {"tbar": tbar, "sigma_tbar": sig_tbar, "t": q0["t"], "sigma": sig, "h": q0["h"], "sigma_h": sigh}
    if not (tbar > 0 and tbar / sig_tbar >= R1_GATE):
        return {"outcome": "NOT COMPUTED", "why": "tbar <= 0 or tbar/sigma(tbar) < 3", **base}
    forced = set(PL[i] for i in small) if (n0r["SIZE_BIAS_g"] or n0r["SIZE_BIAS_t"]) else set()
    cls = {X: classify(q0["t"][X], sig[X], q0["h"][X], sigh[X], tbar, X in forced) for X in PL}
    pat = pattern(cls)
    dropped = (pat == "PERIOD-WIDE" and sdrec["R1_rules"]["drop_PERIOD_WIDE"]) or \
              (pat == "SUBSET" and sdrec["R1_rules"]["drop_SUBSET"])
    return {"outcome": pat, "sentence_dropped_at_stage_D": bool(dropped), "classes": cls, **base,
            "forced_unresolved_by_N0": sorted(forced)}


# ---------------------------------------------------------------- main


def code_sha() -> dict:
    return {**ct.code_sha(), "fd_rpd.py": sa.sha256(Path(__file__).resolve()),
            "fd_rpd_inputs.py": sa.sha256(Path(ri.__file__).resolve()),
            "fd_ct_periods.py": sa.sha256(Path(cp.__file__).resolve())}


def build_args(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="reader", required=True)
    g = sub.add_parser("gate")
    g.add_argument("--r", type=Path, required=True)
    g.add_argument("--stage", choices=("a", "b"), required=True)
    for name in ("stage0", "staged", "controls", "readout"):
        p = sub.add_parser(name)
        p.add_argument("--r", type=Path, required=True)
        p.add_argument("--definition", type=Path, required=True)
        p.add_argument("--out-json", type=Path, required=True)
        p.add_argument("--deploy", type=Path, default=_ND.parent)
        if name == "staged":
            p.add_argument("--outer", type=int, default=STAGE_D_OUTER)
            p.add_argument("--inner", type=int, default=STAGE_D_INNER)
            p.add_argument("--budget", type=float, default=STAGE_D_BUDGET_S)
    return ap.parse_args(argv)


def main(argv=None) -> int:
    a = build_args(argv)
    if a.reader != "gate" and a.out_json.exists():
        print(f"FAIL refusing to overwrite {a.out_json}", file=sys.stderr)
        return 1
    if a.reader != "gate":
        a.out_json.parent.mkdir(parents=True, exist_ok=True)
    try:
        return {"stage0": run_stage0, "staged": run_staged, "controls": run_controls, "gate": run_gate,
                "readout": run_readout}[a.reader](a)
    except f0.Stop as e:
        print(e.code, file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
