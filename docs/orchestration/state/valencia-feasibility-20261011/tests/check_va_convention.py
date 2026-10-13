#!/usr/bin/env python3
"""Checks C1-C7 of REPAIR.md: the fixed VA-interference convention of the integrator.

The lepton tensor is rebuilt from an explicit Dirac-matrix trace in a frame
constructed independently of ``lepton_contraction`` (lab frame, then rotated so
that q lies along +z). C1-C6 use identical kinematics and tensor input for both
beams; no nuclear energy shift enters them. Writes one JSON document.

Usage: check_va_convention.py NUWRO_SRC JSON_OUT
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "code"))
import valencia_tensor_xsec as vx  # noqa: E402

RNG = np.random.default_rng(20261011)
G = np.diag([1.0, -1.0, -1.0, -1.0])

# Dirac representation; gamma5 = i g0 g1 g2 g3
I2, Z2 = np.eye(2), np.zeros((2, 2))
SIG = [np.array([[0, 1], [1, 0]], complex), np.array([[0, -1j], [1j, 0]]), np.array([[1, 0], [0, -1]], complex)]
GAM_UP = [np.block([[I2, Z2], [Z2, -I2]]).astype(complex)] + [np.block([[Z2, s], [-s, Z2]]) for s in SIG]
GAM5 = 1j * GAM_UP[0] @ GAM_UP[1] @ GAM_UP[2] @ GAM_UP[3]
GAM_LO = [G[m, m] * GAM_UP[m] for m in range(4)]
ONE = np.eye(4)


def slash(p):
    """gamma^mu p_mu for contravariant p."""
    return sum(G[m, m] * p[m] * GAM_UP[m] for m in range(4))


def trace_lepton(k, kp, m, beam):
    """L_{mu sigma} = (1/8) sum over spins of l_mu l_sigma^*, lower indices (complex 4x4)."""
    P = ONE - GAM5
    if beam == "nu":   # nu(k) -> l-(k'): l_mu = ubar(k') g_mu (1-g5) u(k)
        A, B = slash(kp) + m * ONE, slash(k)
    else:              # nubar(k) -> l+(k'): l_mu = vbar(k) g_mu (1-g5) v(k')
        A, B = slash(k), slash(kp) - m * ONE
    return np.array([[np.trace(A @ GAM_LO[a] @ P @ B @ GAM_LO[b] @ P) for b in range(4)]
                     for a in range(4)]) / 8.0


def levi_civita_lower():
    eps = np.zeros((4,) * 4)
    for perm in np.array(np.meshgrid(*[range(4)] * 4, indexing="ij")).reshape(4, -1).T:
        if len(set(perm)) == 4:
            p, sign = list(perm), 1
            for i in range(4):
                while p[i] != i:
                    j = p[i]
                    p[i], p[j] = p[j], p[i]
                    sign = -sign
            eps[tuple(perm)] = sign
    return eps  # eps_{0123} = +1


EPS_LO = levi_civita_lower()


def nieves_lepton(k, kp, beam):
    """eq:lep of arXiv:1102.2777 (eps_{0123} = +1), L^a reversed for nubar (sec:anti)."""
    kl, kpl = G @ k, G @ kp
    sym = np.outer(kpl, kl) + np.outer(kl, kpl) - G * (k @ G @ kp)
    anti = np.einsum("msab,a,b->ms", EPS_LO, kp, k)
    return sym + (1j if beam == "nu" else -1j) * anti


def kinematics(E, omega, q, m=vx.M_MU):
    """Lab frame (beam along z, lepton in the x-z plane), rotated so that q is along +z."""
    Ep = E - omega
    kpm = np.sqrt(Ep ** 2 - m ** 2)
    cos = (E ** 2 + kpm ** 2 - q ** 2) / (2 * E * kpm)
    sin = np.sqrt(1 - cos ** 2)
    k = np.array([E, 0.0, 0.0, E])
    kp = np.array([Ep, kpm * sin, 0.0, kpm * cos])
    qv = (k - kp)[1:]
    th = np.arctan2(qv[0], qv[2])  # rotate about y by -th: q -> +z
    R = np.array([[np.cos(th), 0, -np.sin(th)], [0, 1, 0], [np.sin(th), 0, np.cos(th)]])
    k[1:], kp[1:] = R @ k[1:], R @ kp[1:]
    assert np.allclose((k - kp)[1:], [0, 0, q], atol=1e-9 * q)
    return k, kp


def full_contraction(L, w):
    W = np.zeros((4, 4), complex)
    W[0, 0], W[0, 3], W[3, 0] = w["W00"], w["W03"], w["W03"]
    W[1, 1], W[2, 2], W[3, 3] = w["W11"], w["W11"], w["W33"]
    W[1, 2], W[2, 1] = 1j * w["W12"], -1j * w["W12"]  # W = W_s + i W_a, table W12 = W_a^{12}
    return np.sum(L * W)


def random_points(n, E):
    om = RNG.uniform(20, min(0.85 * E, E - vx.M_MU - 10), n)
    kpm = np.sqrt((E - om) ** 2 - vx.M_MU ** 2)
    q = RNG.uniform(np.abs(E - kpm) * 1.001 + 1e-3, (E + kpm) * 0.999)
    return om, q


def main() -> int:
    nuwro_src, out_path = Path(sys.argv[1]), Path(sys.argv[2])
    res: dict = {"w12_encoding": vx.W12_ENCODING}
    ok_all = True

    # C1, C2, C3, C6 at 200 random points, E from 0.3 to 20 GeV
    c1 = c2 = c2im = c3s = c3i = c6 = 0.0
    for _ in range(200):
        E = float(np.exp(RNG.uniform(np.log(300), np.log(20000))))
        om, q = random_points(1, E)
        om, q = float(om[0]), float(q[0])
        k, kp = kinematics(E, om, q)
        w = {c: float(RNG.normal()) for c in vx.COMPONENTS}
        wa = {c: np.array([v]) for c, v in w.items()}
        per_beam = {}
        for beam in ("nu", "nubar"):
            Lt, Ln = trace_lepton(k, kp, vx.M_MU, beam), nieves_lepton(k, kp, beam)
            c1 = max(c1, np.abs(Lt - Ln).max() / np.abs(Ln).max())
            full = full_contraction(Lt, w)
            s, i = vx.lepton_contraction(E, np.array([om]), np.array([q]), wa, beam)
            code = float(s[0] + i[0])
            c2 = max(c2, abs(full.real - code) / max(abs(code), abs(full.real)))
            c2im = max(c2im, abs(full.imag) / abs(full.real))
            per_beam[beam] = (float(s[0]), float(i[0]))
            only12 = {c: np.array([w["W12"] if c == "W12" else 0.0]) for c in vx.COMPONENTS}
            nuw = float(vx.nuwro_formula_contraction(E, np.array([om]), np.array([q]), only12, beam)[0])
            _, i12 = vx.lepton_contraction(E, np.array([om]), np.array([q]), only12, beam)
            c6 = max(c6, abs(nuw - i12[0]) / max(abs(nuw), abs(i12[0])))
        (sn, inu), (sb, inb) = per_beam["nu"], per_beam["nubar"]
        c3s = max(c3s, abs(sn - sb) / abs(sn))
        c3i = max(c3i, abs(inu + inb) / abs(inu))
    res["C1_trace_vs_eqlep_max_dev_over_max_L"] = c1
    res["C2_code_vs_full_complex_contraction_max_rel"] = c2
    res["C2_imag_over_real_max"] = c2im
    res["C3_beam_reversal_sym_max_rel"] = c3s
    res["C3_beam_reversal_interference_sum_max_rel"] = c3i
    res["C6_nuwro_W12_only_vs_code_max_rel"] = c6
    grades = {"C1": c1 <= 1e-9, "C2": c2 <= 1e-9 and c2im <= 1e-9, "C3": c3s <= 1e-12 and c3i <= 1e-12,
              "C6": c6 <= 1e-9}

    # C4, C5 on the real tables; n_sub = 2 at 1 GeV; one forced common shift for both beams
    tables = vx.load_tables(nuwro_src, "C12")
    def variant(f):
        return {ch: {c: (f(a) if c == "W12" else a) for c, a in comps.items()} for ch, comps in tables.items()}
    t0, tneg = variant(np.zeros_like), variant(np.negative)
    B = 15.0
    tot = lambda t, beam: sum(vx.sigma(t, 1000.0, beam, "C12", 2, shift=B).values())  # noqa: E731
    s0nu, s0nb = tot(t0, "nu"), tot(t0, "nubar")
    snu, snb, snu_neg = tot(tables, "nu"), tot(tables, "nubar"), tot(tneg, "nu")
    res["C4_W12_zero_nu_minus_nubar_rel"] = abs(s0nu - s0nb) / s0nu
    res["C5_interference_nu"] = snu - s0nu
    res["C5_interference_nu_W12_negated"] = snu_neg - s0nu
    res["C5_reversal_rel"] = abs((snu - s0nu) + (snu_neg - s0nu)) / abs(snu - s0nu)
    res["C5_nubar_equals_nu_with_W12_negated_rel"] = abs(snb - snu_neg) / snb
    src = (HERE / "code/valencia_tensor_xsec.py").read_text()
    scan = re.findall(r".*(?:sum\(anti|>= 0 else|np\.sign\(|nu_sign).*", src)
    res["C5_source_scan_hits"] = scan
    grades["C4"] = res["C4_W12_zero_nu_minus_nubar_rel"] <= 1e-12
    grades["C5"] = res["C5_reversal_rel"] <= 1e-9 and not scan

    # C7: committed 1 GeV n_sub = 8 values, recomputed with the fixed convention
    c7 = {}
    for beam in ("nu", "nubar"):
        old = json.loads((HERE / f"results/integrator-C12-{beam}-1GeV-n8.json").read_text())[0]
        new = vx.sigma(tables, 1000.0, beam, "C12", 8)
        c7[beam] = {"committed_total": old["total_per_nucleon_cm2"], "recomputed_total": sum(new.values()),
                    "rel_change": sum(new.values()) / old["total_per_nucleon_cm2"] - 1,
                    "committed_selected_nu_sign": old.get("nu_sign_of_raw_W12_term")}
    res["C7"] = c7
    grades["C7_unchanged"] = all(abs(v["rel_change"]) <= 1e-12 for v in c7.values())
    # descriptive only, never used to choose the convention
    res["descriptive_fraction_of_nonzero_W12_cells_negative"] = {
        ch: float((tables[ch]["W12"] < 0).sum() / max((tables[ch]["W12"] != 0).sum(), 1)) for ch in vx.CHANNELS}
    res["grades"] = {k: bool(v) for k, v in grades.items()}
    ok_all = all(grades.values())
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(res, indent=1, default=float) + "\n")
    print(json.dumps(res, indent=1, default=float))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
