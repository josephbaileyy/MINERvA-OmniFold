"""Reco-response distortions R1 / R2 on PET2-small's STORED step-1 inputs (pseudodata only).

The study's ours-path runner (`final_design/runner/design_inputs.py`) implements:

* **R1** (reco energy scale x s, predecessor amendment 3 item 3): every stored reco cluster energy
  (`part_reco[..., 0]`) and reco E_avail of the reco-passing pseudodata rows x s, at the raw-array
  level before the cloud is built; muon quantities, reco q3, the prior and the selection unchanged;
* **R2** (muon momentum scale x s): reco muon momentum x s at fixed angle -- px, py, pz x s,
  E -> sqrt(E^2 + (s^2 - 1) p^2), q/p / s; reco pT and p|| x s and reco q3 recomputed from the
  scaled muon and the unchanged recoil; E_avail, the cluster cloud, the prior and the selection
  unchanged.

This module applies the SAME physical change to PET2's inputs, on the values the shards STORE
(`configuration_comparison/build_theirs_inputs.py`), before the historical conversion
(`theirs_token_schema.convert_packed`) -- so the converted inputs are exactly what PET2 would see
had the build read a detector with that response. Stored layout and every field's treatment:

    token    [px, py, pz, log(E + 1e-3), PID]      PID: 0 muon, 1 photon, 2 blob, 3/4/5 prong,
                                                        6 aggregate blob, 7 aggregate prong
    add_info [dE/dx, x, y, z, t]                   (dE/dx: photons and prongs; 0 elsewhere;
                                                    -999 = "none" sentinel)
    globals  [log(muon_fuzz_E + 1e-5), log(muon_iso_blobs_E + 1e-5), log(hadron_recoil + 1e-5),
              log(passive_id/1e4 + 1e-3), log(passive_od/1e4 + 1e-3),
              log(passive_id/1e4 + passive_od/1e4 + 1e-3), n_michel, muon_present,
              diphoton_mass, charged_pion_prongs,
              log(sum E over tokens of PID 2..7 + 1e-3) x 6]   (the sums as the build forms them:
                                                               sum of exp(stored log E) per PID)

| field | R1 (calorimetric energy x s) | R2 (muon momentum x s) |
|---|---|---|
| non-muon token px, py, pz | x s (energy x s at fixed direction; blob momenta are unit(xyz) E by construction; aggregates are sums) -> converted log pT + log s, eta and phi unchanged | unchanged |
| non-muon token log E | E -> s E: log(s (exp(v) - 1e-3) + 1e-3) | unchanged |
| muon token (PID 0) | unchanged (as the ours path leaves muon quantities) | px, py, pz x s; E -> sqrt(E^2 + (s^2-1) p^2); converted eta, phi unchanged |
| PID | unchanged | unchanged |
| dE/dx (photons, prongs) | x s (an energy per length; the -999 sentinel and non-finite values untouched; the conversion's 100 clip then applies) | unchanged |
| x, y, z, t | unchanged | unchanged |
| globals 0-1: muon fuzz / isolated-blob calorimetric energy | x s (calorimetric energies) | unchanged |
| global 2: hadron recoil (the PET2 analogue of reco E_avail) | x s | unchanged |
| globals 3-5: passive-corrected recoil energies (inner / outer / sum) | x s (sum recomputed from the scaled parts) | unchanged |
| global 6 n_michel, 7 muon_present, 9 charged-pion prongs | unchanged (counts / flags) | unchanged |
| global 8 diphoton mass | x s (both photon four-momenta x s) | unchanged |
| globals 10-15: per-PID energy sums | recomputed from the scaled tokens exactly as the build forms them | unchanged (PID 0 is not summed) |

PET2's inputs carry no q/p, no reco q3 and no reco E_avail field, so R2's q/p and q3 changes and
R1's E_avail change have no further PET2 counterpart beyond the rows above. Only the rows a caller
passes (the reco-passing pseudodata) are transformed; the prior is never touched.
"""

from __future__ import annotations

import hashlib
import inspect
import json
from typing import Any, Callable

import numpy as np

LOG_E_EPS = 1e-3            # build_theirs_inputs.EPS (stored log E = log(max(E, 0) + 1e-3))
FUZZ_EPS = 1e-5             # globals 0-2
PASSIVE_EPS = 1e-3          # globals 3-5 and 10-15
DEDX_NONE = -999.0
SUM_PIDS = (2, 3, 4, 5, 6, 7)


def _inv_log(v: np.ndarray, eps: float) -> np.ndarray:
    return np.maximum(np.exp(np.asarray(v, np.float64)) - eps, 0.0)


def _log(x: np.ndarray, eps: float) -> np.ndarray:
    return np.log(np.maximum(x, 0.0) + eps)


def energy_sums(tokens: np.ndarray) -> np.ndarray:
    """Per-PID energy sums exactly as `build_theirs_inputs.build_file` forms them."""
    tok = np.asarray(tokens, np.float32)
    energies = np.exp(tok[..., 3]) * (tok[..., 3] != 0)
    return np.stack([np.where(tok[..., 4] == code, energies, 0.0).sum(axis=-1)
                     for code in SUM_PIDS], axis=-1).astype(np.float64)


def r1(tokens: np.ndarray, add: np.ndarray, glob: np.ndarray, s: float
       ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """R1 x s on stored arrays `(n, 33, 5)`, `(n, 33, 5)`, `(n, 16)`; returns new float32 arrays."""
    s = float(s)
    tok = np.array(tokens, dtype=np.float64)
    ad = np.array(add, dtype=np.float64)
    gl = np.array(glob, dtype=np.float64)
    real = tok[..., 3] != 0
    nonmu = real & (tok[..., 4] != 0)
    for c in range(3):
        tok[..., c] = np.where(nonmu, tok[..., c] * s, tok[..., c])
    tok[..., 3] = np.where(nonmu, _log(s * _inv_log(tok[..., 3], LOG_E_EPS), LOG_E_EPS),
                           tok[..., 3])
    dedx = ad[..., 0]
    scal = nonmu & np.isfinite(dedx) & (dedx != DEDX_NONE)
    ad[..., 0] = np.where(scal, dedx * s, dedx)
    for c in (0, 1, 2):
        gl[:, c] = _log(s * _inv_log(gl[:, c], FUZZ_EPS), FUZZ_EPS)
    pid_in, pod = s * _inv_log(gl[:, 3], PASSIVE_EPS), s * _inv_log(gl[:, 4], PASSIVE_EPS)
    gl[:, 3], gl[:, 4], gl[:, 5] = (_log(pid_in, PASSIVE_EPS), _log(pod, PASSIVE_EPS),
                                    _log(pid_in + pod, PASSIVE_EPS))
    gl[:, 8] = gl[:, 8] * s
    tok32 = tok.astype(np.float32)
    gl[:, 10:16] = np.log(energy_sums(tok32) + PASSIVE_EPS)
    return tok32, ad.astype(np.float32), gl.astype(np.float32)


def r2(tokens: np.ndarray, add: np.ndarray, glob: np.ndarray, s: float
       ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """R2 x s: the muon token's momentum at fixed direction, its energy recomputed."""
    s = float(s)
    tok = np.array(tokens, dtype=np.float64)
    mu = (tok[..., 3] != 0) & (tok[..., 4] == 0)
    p2 = (tok[..., 0:3] ** 2).sum(axis=-1)
    energy = _inv_log(tok[..., 3], LOG_E_EPS)
    new_e = np.sqrt(np.maximum(energy ** 2 + (s * s - 1.0) * p2, 0.0))
    for c in range(3):
        tok[..., c] = np.where(mu, tok[..., c] * s, tok[..., c])
    tok[..., 3] = np.where(mu, _log(new_e, LOG_E_EPS), tok[..., 3])
    return (tok.astype(np.float32), np.array(add, dtype=np.float32),
            np.array(glob, dtype=np.float32))


FAMILIES: dict[str, Callable] = {"R1": r1, "R2": r2}


def transform_for(distortion: Any) -> tuple[str, float, Callable] | None:
    """(family, factor, fn) for a `design_inputs.DistortionSpec`, or None (truth-only)."""
    e = getattr(distortion, "reco_energy_scale", None)
    m = getattr(distortion, "muon_momentum_scale", None)
    if e is not None and m is not None:
        raise SystemExit("[pet2] two reco-response distortions at once are not implemented")
    if e is not None:
        s, fam = float(e), "R1"
    elif m is not None:
        s, fam = float(m), "R2"
    else:
        return None

    def fn(tokens: np.ndarray, add: np.ndarray, glob: np.ndarray, fam=fam, s=s):
        return FAMILIES[fam](tokens, add, glob, s)
    return fam, s, fn


def transform_record(fam: str, s: float) -> dict[str, Any]:
    source = inspect.getsource(FAMILIES[fam]) + inspect.getsource(_inv_log) + \
        inspect.getsource(_log) + inspect.getsource(energy_sums)
    return {"family": fam, "factor": s, "applied_to": "stored PET2 inputs of the reco-passing "
            "pseudodata rows, before the historical conversion",
            "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
            "treatment": "pet2_response module docstring (field table)"}


def transform_key(fam: str | None, s: float | None) -> str:
    if fam is None:
        return "none"
    return hashlib.sha256(json.dumps(transform_record(fam, s), sort_keys=True).encode()
                          ).hexdigest()
