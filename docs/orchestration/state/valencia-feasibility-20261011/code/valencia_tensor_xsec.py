#!/usr/bin/env python3
"""Independent inclusive cross section from tabulated Valencia hadron tensors.

Reads the per-nucleon tensor grids that NuWro 25.11.1 ships for its ``mec_kind=6``
(Valencia 2020) model, builds W^{mu nu} in the frame q || z, contracts it with an
explicitly constructed charged-current lepton tensor, and integrates by quadrature
on a grid aligned with the table.

Shared with NuWro, and declared rather than re-derived:

* the table values and their grid (q0 and |q| from 10 to 1200 MeV in 10 MeV steps,
  upper-triangular storage, zero row at q0 = 0, zero above the diagonal q0 > |q|);
* NuWro's energy-shift convention: tensors are looked up at q0_eff = omega - B
  while the lepton kinematics use the physical omega; B = 16.827 MeV (nu, 12C),
  13.878 MeV (anti-nu, 12C) from ``E_corr`` in ``mecevent_2020Valencia.h``;
* the hard cut |q| <= 1.2 GeV.

Not shared: the contraction. NuWro uses structure functions w1..w5; this code
contracts four-vectors directly.

Convention (the authors', fixed; REPAIR.md section 1). Nieves, Ruiz Simo and
Vicente Vacas 2011 (arXiv:1102.2777), repeated in Sobczyk, Nieves and Sanchez 2020:

* eq:sec   d2sigma/(dOmega dE') = (|k'|/|k|) G^2/(4 pi^2) L_{mu sigma} W^{mu sigma},
           with cos^2(theta_C) inside W (W per nucleon, MeV^-1);
* footnote eps_{0123} = +1, g = diag(+1, -1, -1, -1);
* eq:lep   L_{mu sigma} = k'_mu k_sigma + k'_sigma k_mu - g_{mu sigma} k.k'
                          + i eps_{mu sigma alpha beta} k'^alpha k^beta   (neutrino);
* eq:wmunu W^{mu sigma} ~ sum_f <f|j^mu|i> <f|j^sigma|i>^*, j = V - A, and
           W = W_s + i W_a with W_s, W_a real symmetric / antisymmetric;
* sec:anti antineutrino: reverse the sign of L^a.

Hence L.W = L^s.W_s - L^a.W_a. With q along +z the antisymmetric part has only
W_a^{12} = -W_a^{21}, and L^a_{12} = eps_{1203} k'^0 k^3 + eps_{1230} k'^3 k^0
= E'k_z - (k_z - |q|)E = E|q| - omega k_z. The interference is therefore
-2 s (E|q| - omega k_z) W_a^{12}, s = +1 (nu), -1 (nubar).

Table encoding (not documented by the authors): the column W12 is read as
W_a^{12} = Im W^{12}. NuWro, which distributes the tables, contracts them the same
way (REPAIR.md check C6); the encoding is distributor-corroborated, not
author-confirmed. The sign is never chosen from the data.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np

GF_MEV = 1.1663787e-11  # MeV^-2
VUD = 0.97373  # used only for the diagnostic "extra V_ud^2" variant
# The Valencia hadron tensor already contains cos^2(theta_C): Nieves et al. 2011
# (arXiv:1102.2777, Eqs. for W^{mu nu} carry -2 cos^2(theta_C)), and the 2020 paper's
# prefactor is G^2/(4 pi^2) with no V_ud. Corrected after review (REVIEW.md, finding 1).
PREFACTOR_VUD2 = 1.0
HBARC2_CM2_MEV2 = 0.3893794e-21  # (hbar c)^2 in cm^2 MeV^2
M_MU = 105.6583755  # MeV
NGRID = 120
STEP = 10.0  # MeV
BEAM_SIGN = {"nu": +1.0, "nubar": -1.0}  # sign of L^a (eq:lep, sec:anti)
W12_ENCODING = "W12 = W_a^{12} = Im W^{12} (distributor-corroborated, not author-confirmed)"
QMAX = 1200.0  # MeV
B_SHIFT = {("C12", "nu"): 16.827, ("C12", "nubar"): 13.878,
           ("O16", "nu"): 14.906, ("O16", "nubar"): 10.931}
CHANNELS = ("pp", "np", "pn", "3p3h")
COMPONENTS = ("W00", "W03", "W11", "W12", "W33")


def read_header_arrays(path: Path) -> dict[str, np.ndarray]:
    """Return every ``static double NAME[] = {...};`` array in a C header."""
    text = path.read_text()
    out = {}
    for name, body in re.findall(r"static\s+double\s+(\w+)\s*\[\]\s*=\s*\{(.*?)\};",
                                 text, re.S):
        vals = [float(v) for v in body.replace("\n", "").split(",") if v.strip()]
        out[name] = np.asarray(vals)
    return out


def load_tables(nuwro_src: Path, nucleus: str = "C12") -> dict[str, dict[str, np.ndarray]]:
    """Dense (NGRID+1, NGRID) grids per channel and component.

    Row i is q0 = i*STEP (row 0 is the declared zero row); column j is
    |q| = (j+1)*STEP. Storage index k(n, m) = n*(2N - n + 1)/2 + m - n, m >= n,
    for q0 = (n+1)*STEP and |q| = (m+1)*STEP.
    """
    files = {"pp": f"{nucleus}_pp.h", "np": f"{nucleus}_np.h",
             "pn": f"{nucleus}_pn.h", "3p3h": f"{nucleus}_3p3h.h"}
    suffix = {"pp": "pp", "np": "np", "pn": "pn", "3p3h": "_3p3h"}
    tables: dict[str, dict[str, np.ndarray]] = {}
    expected = NGRID * (NGRID + 1) // 2
    for ch, fname in files.items():
        arrays = read_header_arrays(nuwro_src / "MEC_data" / nucleus / fname)
        tables[ch] = {}
        for comp in COMPONENTS:
            flat = arrays[f"{nucleus}_{comp}{suffix[ch]}"]
            if flat.size != expected:
                raise ValueError(f"{fname}:{comp} has {flat.size} values, expected {expected}")
            dense = np.zeros((NGRID + 1, NGRID))
            for n in range(NGRID):
                start = n * (2 * NGRID - n + 1) // 2
                dense[n + 1, n:] = flat[start:start + NGRID - n]
            tables[ch][comp] = dense
    return tables


def interp(dense: np.ndarray, q0: np.ndarray, q: np.ndarray) -> np.ndarray:
    """Bilinear interpolation on the declared grid; zero outside the table."""
    inside = (q0 >= 0) & (q0 <= q) & (q >= STEP) & (q <= QMAX)
    y = np.clip(q0 / STEP, 0, NGRID - 1e-9)
    x = np.clip(q / STEP - 1.0, 0, NGRID - 1 - 1e-9)
    i0 = np.floor(y).astype(int)
    j0 = np.floor(x).astype(int)
    fy = y - i0
    fx = x - j0
    i1 = np.minimum(i0 + 1, NGRID)
    j1 = np.minimum(j0 + 1, NGRID - 1)
    val = ((1 - fy) * (1 - fx) * dense[i0, j0] + (1 - fy) * fx * dense[i0, j1]
           + fy * (1 - fx) * dense[i1, j0] + fy * fx * dense[i1, j1])
    return np.where(inside, val, 0.0)


def lepton_contraction(E, omega, q, w: dict[str, np.ndarray], beam: str) -> tuple[np.ndarray, np.ndarray]:
    """Symmetric part and VA interference of L_{mu sigma} W^{mu sigma}.

    Explicit four-vectors, q along +z, k in the x-z plane. The interference
    carries the fixed convention of the module docstring: -2 s (E|q| - omega k_z) W12.
    """
    Ep = E - omega
    kp = np.sqrt(np.maximum(Ep ** 2 - M_MU ** 2, 0.0))
    kz = (E ** 2 - kp ** 2 + q ** 2) / (2 * q)
    kx = np.sqrt(np.maximum(E ** 2 - kz ** 2, 0.0))
    k = np.stack([np.full_like(q, E), kx, np.zeros_like(q), kz])
    kprime = np.stack([Ep, kx, np.zeros_like(q), kz - q])
    metric = np.array([1.0, -1.0, -1.0, -1.0])
    kdotkp = sum(metric[i] * k[i] * kprime[i] for i in range(4))

    def l_low(mu: int, nu: int) -> np.ndarray:
        """L^s_{mu nu} = k'_mu k_nu + k_mu k'_nu - g_{mu nu} k.k' (lower indices)."""
        g = metric[mu] if mu == nu else 0.0
        return metric[mu] * metric[nu] * (kprime[mu] * k[nu] + k[mu] * kprime[nu]) - g * kdotkp

    # W_s^{mu nu} is nonzero only in 00, 03 = 30, 11 = 22, 33.
    total = (l_low(0, 0) * w["W00"] + 2.0 * l_low(0, 3) * w["W03"]
             + (l_low(1, 1) + l_low(2, 2)) * w["W11"] + l_low(3, 3) * w["W33"])
    # -L^a_{mu nu} W_a^{mu nu} = -2 L^a_{12} W_a^{12}, L^a_{12} = s (E|q| - omega k_z)
    interference = -2.0 * BEAM_SIGN[beam] * (E * q - omega * kz) * w["W12"]
    return total, interference


def sigma(tables, E: float, beam: str = "nu", nucleus: str = "C12",
          n_sub: int = 8, channels=CHANNELS, shift: float | None = None) -> dict[str, float]:
    """Per-nucleon cross section in cm^2, by channel, at neutrino energy E (MeV).

    Quadrature: midpoint rule with ``n_sub`` sub-points per 10 MeV table cell in
    both omega and |q| (the integrand is bilinear within a cell up to kinematic
    factors, so the rule converges quickly). ``shift`` overrides the energy
    shift B (tests only: identical kinematics for both beams).
    """
    B = B_SHIFT[(nucleus, beam)] if shift is None else shift
    h = STEP / n_sub
    # the tensor vanishes for q0_eff > |q| and |q| > QMAX, so omega <= QMAX + B suffices
    omega = np.arange(B + h / 2, min(E - M_MU, QMAX + B), h)
    if omega.size == 0:
        return {ch: 0.0 for ch in channels}
    q_all = np.arange(h / 2, QMAX, h)
    Om, Q = np.meshgrid(omega, q_all, indexing="ij")
    Ep = E - Om
    kp = np.sqrt(np.maximum(Ep ** 2 - M_MU ** 2, 0.0))
    allowed = (Q > np.abs(E - kp)) & (Q < E + kp) & (Q <= QMAX)
    pref = GF_MEV ** 2 * PREFACTOR_VUD2 / (2 * np.pi) * Q / E ** 2
    norm = h * h * HBARC2_CM2_MEV2
    out = {}
    for ch in channels:
        w = {c: interp(tables[ch][c], Om - B, Q) for c in COMPONENTS}
        s_part, i_part = lepton_contraction(E, Om, Q, w, beam)
        out[ch] = float(np.where(allowed, pref * (s_part + i_part), 0.0).sum() * norm)
    return out


def nuwro_formula_contraction(E, omega, q, w, beam):
    """NuWro's structure-function expression (mecevent_2020Valencia.cc), transcribed
    only as an algebra cross-check of lepton_contraction; returns the same object
    L.W up to the common prefactor, for diagnosis, not as a benchmark."""
    Ep = E - omega
    lp = np.sqrt(np.maximum(Ep ** 2 - M_MU ** 2, 0.0))
    ct = (E ** 2 + lp ** 2 - q ** 2) / (2 * E * lp)
    ap = 1 if beam == "nubar" else 0
    w1 = 0.5 * w["W11"]
    w2 = 0.5 * (w["W00"] + w["W11"] + omega ** 2 / q ** 2 * (w["W33"] - w["W11"]) - 2 * omega / q * w["W03"])
    w3 = (1 - 2 * ap) * w["W12"] / q
    w4 = 0.5 * (w["W33"] - w["W11"]) / q ** 2
    w5 = (w["W03"] - omega / q * (w["W33"] - w["W11"])) / q
    st2 = 0.5 * (1 - ct)
    ct2 = 0.5 * (1 + ct)
    sts = 1 - ct ** 2
    r = 2 * w1 * st2 + w2 * ct2 - w3 * (E + Ep) * st2
    r += M_MU ** 2 / ((Ep + lp) * Ep) * (w1 * ct - 0.5 * w2 * ct + 0.5 * w3 * (Ep * (1 - ct) + lp - E * ct)
                                         + 0.5 * w4 * (M_MU ** 2 * ct + 2 * Ep * (Ep + lp) * sts) - 0.5 * w5 * (Ep + lp))
    # NuWro: dsigma/dE'dcos = r * 2 G^2 Ep lp / pi.  Ours: (G^2/(2 pi)) (lp/E)(2pi)... -> L.W = 4 E Ep r
    return 4.0 * E * Ep * r


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--nuwro-src", type=Path, required=True)
    ap.add_argument("--nucleus", default="C12")
    ap.add_argument("--energies", type=float, nargs="+", default=[1000.0])
    ap.add_argument("--beam", choices=["nu", "nubar"], default="nu")
    ap.add_argument("--n-sub", type=int, default=8)
    ap.add_argument("--json-out", type=Path)
    args = ap.parse_args()
    tables = load_tables(args.nuwro_src, args.nucleus)
    rows = []
    for E in args.energies:
        s = sigma(tables, E, args.beam, args.nucleus, args.n_sub)
        rows.append({"E_MeV": E, "beam": args.beam, "per_nucleon_cm2": s,
                     "total_per_nucleon_cm2": sum(s.values()),
                     "w12_convention": W12_ENCODING, "n_sub": args.n_sub})
        print(json.dumps(rows[-1]))
    if args.json_out:
        args.json_out.write_text(json.dumps(rows, indent=1) + "\n")


if __name__ == "__main__":
    main()
