#!/usr/bin/env python3
"""GENCMP step B kinematics (state/measurement-paper/5d-community-20261024/FD-GENCMP-DECLARATION.md section 3):
the analysis definitions of pT, p_par and W applied to a generator event whose neutrino is along +z.

Pure numpy, no ROOT, so the definitions are tested apart from the I/O (tests/test_fd_gencmp.py).

* The lepton is rotated from the generator frame into the MAT beam frame by a neutrino direction n drawn from the
  analysis MC's pool in the event's E_nu bin: MP-5's ``rotate`` and ``draw_directions``
  (measurement-paper/phase1/mp5/mp5_genie.py), imported, not restated.
* NuWro's flat trees keep pT and p_par but not the lepton azimuth, so it is drawn uniformly (``lepton_from_pt_pz``).
* W = sqrt(M^2 + 2 M (E_nu - E_mu) - Q^2), Q^2 = 4 E_nu E_mu sin^2(theta/2), theta from the beam axis, with M the
  struck nucleon's mass, as CVUniverse::GetTrueExperimentersW (MINERvA101/.../event/CVUniverse.h:392-410);
  W^2 < 0 gives NaN, and such an event enters no cell (the analysis excludes it from its truth sample).
* The masses are gen_to_xsec5d.py's CVU_M_N, CVU_M_P and CVU_M_NUCLEON; that module imports ROOT, so they are
  restated here and the test reads them back from its source.

Draws: one SeedSequence per (seed, sample tag), so each sample's draws do not depend on which other samples ran.
"""
from __future__ import annotations

import sys
import zlib
from pathlib import Path

import numpy as np

_REPO = Path(__file__).resolve().parents[1]
_MP5 = _REPO / "measurement-paper" / "phase1" / "mp5"
for _p in (str(_REPO / "3d-unfolding" / "genie"), str(_REPO / "nd-unfolding"), str(_MP5)):
    if _p not in sys.path:
        sys.path.append(_p)
from mp5_genie import draw_directions, rotate  # noqa: E402,F401  (MP-5's declared rotation and draw)

CVU_M_N, CVU_M_P = 0.93956536, 0.938272013
CVU_M_NUCLEON = (1.5 * CVU_M_N + CVU_M_P) / 2.5
GEN_M_FIXED = 0.939565          # the generators' converters' fixed M (gen_to_xsec5d.py meta; gibuu_to_xsec_eavailW)
M_MU = 0.1056583745
ENU_BINS_GEV = (0.0, 3.0, 5.0, 8.0, 15.0, 30.0, np.inf)     # MP-5 PREP section 2
SEEDS = (202611011, 202611012, 202611013, 202611014, 202611015)
PDG_N, PDG_P = 2112, 2212


def struck_mass(hitnuc: np.ndarray) -> np.ndarray:
    """M_n for 2112, M_p for 2212, otherwise M_nucleon (CVUniverse's branch for an unidentified nucleon)."""
    h = np.asarray(hitnuc)
    return np.where(h == PDG_N, CVU_M_N, np.where(h == PDG_P, CVU_M_P, CVU_M_NUCLEON))


def w_analysis(enu, emu, costh, m) -> np.ndarray:
    """CVUniverse::GetTrueExperimentersW in GeV; NaN where W^2 < 0. costh is cos(theta) about the beam axis."""
    c = np.clip(np.asarray(costh, float), -1.0, 1.0)
    q2 = 4.0 * enu * emu * np.sin(np.arccos(c) / 2.0) ** 2
    w2 = m * m + 2.0 * (enu - emu) * m - q2
    with np.errstate(invalid="ignore"):
        return np.where(w2 >= 0, np.sqrt(np.maximum(w2, 0.0)), np.nan)


def lepton_from_pt_pz(pt, pz, phi):
    """The lepton 3-momentum from (pT, p_par) about the generator's nu axis and an azimuth phi."""
    pt = np.asarray(pt, float)
    return pt * np.cos(phi), pt * np.sin(phi), np.asarray(pz, float)


def beam_frame(px, py, pz, n):
    """pT, p_par and cos(theta) about the beam axis after the rotation R(n); n = z returns the input bitwise."""
    qx, qy, qz = rotate(np.asarray(px, float), np.asarray(py, float), np.asarray(pz, float), n)
    pt = np.hypot(qx, qy)
    p = np.sqrt(qx * qx + qy * qy + qz * qz)
    costh = np.where(p > 0, qz / np.where(p > 0, p, 1.0), 1.0)
    return pt, qz, costh


def draws(seed: int, tag: str, n_entries: int) -> tuple[np.ndarray, np.ndarray]:
    """(u_direction, phi) for a sample's entries, in entry order, from SeedSequence([seed, crc32(tag)])."""
    rng = np.random.default_rng(np.random.SeedSequence([int(seed), zlib.crc32(tag.encode())]))
    u = rng.random(n_entries)
    phi = 2.0 * np.pi * rng.random(n_entries)
    return u, phi


def unit_z(n_entries: int) -> np.ndarray:
    return np.tile([0.0, 0.0, 1.0], (n_entries, 1))
