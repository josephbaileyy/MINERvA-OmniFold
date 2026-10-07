"""Build Gregor's complete-arm inputs from the slim tuples.

Implements `theirs_token_schema.py`, which was read out of his preprocessing
rather than inferred:

    token    (5 stored, 4 seen)   [px, py, pz, log E, PID]
    add_info (5)                  [dE/dx, x, y, z, t]
    globals  (16)                 7 + 3 + 6 energy sums

Category order is his: muon, photon, blob, prong. PID codes are his: muon 0,
photon 1, blob 2, prong 3/8/13 -> 3/4/5, aggregate blob 6, aggregate prong 7.
Blobs get a CONSTRUCTED four-momentum -- unit(xyz) * E -- because a blob has no
momentum and his code assumes a massless particle from the origin.

Overflow AGGREGATES rather than truncates, which is the whole point of PID 6 and
7: surplus blobs sum into one token and surplus prongs into another, so the tail
energy stays in the event.

Every event carries its identity so the downstream join is by event and not by
position.

NOT CITABLE FOR any performance claim; this writes model inputs, not results.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from theirs_token_schema import PID_CODES

# Where this construction is known to differ from his, so that a result carries
# its own caveats rather than relying on someone remembering them.
DECLARED_DIFFERENCES = {
    "muon_presence": (
        "his get_muons selects on the MINOS match; this uses "
        "MasterAnaDev_muon_E > 0, because the slim carries no MINOS-match flag"),
    "prong_dEdX_branch": (
        "his key list names prong_part_dEdXMean, which is absent from our "
        "tuples; prong_dEdXMean is substituted and the two have NOT been shown "
        "to be the same quantity"),
    "cap_split": (
        "his cap is governed by max_blobs/max_prongs, whose values are not in "
        "the repository. The remaining budget is split in proportion to the "
        "event's own multiplicities, with one aggregate slot reserved per "
        "category. This split is OURS"),
}

CAP = 33
RESERVED_MUON = 1
RESERVED_PHOTONS = 2
TOKEN_WIDTH = 5          # px, py, pz, logE, pid  (pid split out at train time)
ADD_WIDTH = 5            # dEdx, x, y, z, t
GLOBAL_WIDTH = 16
PRONG_PID_MAP = {3: 3, 8: 4, 13: 5}
EPS = 1e-3


def _log(x: np.ndarray) -> np.ndarray:
    return np.log(np.maximum(x, 0.0) + EPS)


def _unit_scaled(xyz: np.ndarray, energy: np.ndarray) -> np.ndarray:
    """His blob momentum: a massless particle from the origin, with his guard."""
    norm = np.linalg.norm(xyz, axis=-1, keepdims=True)
    norm = np.where(norm > 1e-6, norm, 1.0)
    return (xyz / norm) * energy[:, None]


def build_event(muon: dict[str, Any], photons: list[dict[str, Any]],
                blobs: dict[str, np.ndarray], prongs: dict[str, np.ndarray],
                cap: int = CAP) -> tuple[np.ndarray, np.ndarray]:
    """One event's (cap, 5) token block and (cap, 5) auxiliary block."""
    tokens: list[np.ndarray] = []
    extras: list[np.ndarray] = []

    if muon is not None:
        p = muon["four_momentum"]
        tokens.append(np.array([p[0], p[1], p[2], _log(np.array([p[3]]))[0],
                                PID_CODES["muon"]], dtype=np.float32))
        extras.append(np.array([0.0, 0.0, 0.0, 0.0, muon["t"]], dtype=np.float32))

    for photon in photons:
        p = photon["four_momentum"]
        tokens.append(np.array([p[0], p[1], p[2], _log(np.array([p[3]]))[0],
                                PID_CODES["photon"]], dtype=np.float32))
        extras.append(np.array([photon["dedx"], 0.0, 0.0, 0.0, photon["t"]],
                               dtype=np.float32))

    # Blobs, energy-descending so that what overflows is the softest.
    be = np.asarray(blobs["E"], dtype=np.float64)
    bxyz = np.stack([blobs["x"], blobs["y"], blobs["z"]], axis=-1).astype(np.float64) \
        if len(be) else np.zeros((0, 3))
    order = np.argsort(-be) if len(be) else np.array([], dtype=int)
    be, bxyz = be[order], bxyz[order]
    bt = np.asarray(blobs["t"], dtype=np.float64)[order] if len(be) else np.zeros(0)
    bmom = _unit_scaled(bxyz, be) if len(be) else np.zeros((0, 3))

    pe = np.asarray(prongs["E"], dtype=np.float64)          # (n, 4) four-momentum
    porder = np.argsort(-pe[:, 3]) if len(pe) else np.array([], dtype=int)
    pe = pe[porder] if len(pe) else pe
    ppos = np.asarray(prongs["pos"], dtype=np.float64)[porder] if len(pe) else \
        np.zeros((0, 4))
    ppid = np.asarray(prongs["pid"])[porder] if len(pe) else np.zeros(0, dtype=int)
    pdedx = np.asarray(prongs["dedx"], dtype=np.float64)[porder] if len(pe) else \
        np.zeros(0)

    budget = cap - len(tokens)
    # Split the remaining budget between blobs and prongs in proportion to what
    # the event actually has, so neither category is starved by the other's
    # multiplicity. The surplus of each is AGGREGATED, never dropped.
    n_blob, n_prong = len(be), len(pe)
    if n_blob + n_prong <= budget:
        keep_b, keep_p = n_blob, n_prong
    else:
        share = budget - 2                       # reserve one aggregate slot each
        keep_b = max(0, min(n_blob, int(round(share * n_blob /
                                              max(n_blob + n_prong, 1)))))
        keep_p = max(0, min(n_prong, share - keep_b))

    for index in range(keep_b):
        tokens.append(np.array([bmom[index, 0], bmom[index, 1], bmom[index, 2],
                                _log(be[index:index + 1])[0], PID_CODES["blob"]],
                               dtype=np.float32))
        extras.append(np.array([0.0, bxyz[index, 0], bxyz[index, 1], bxyz[index, 2],
                                bt[index]], dtype=np.float32))
    if keep_b < n_blob:
        tail_e = be[keep_b:].sum()
        tail_p = bmom[keep_b:].sum(axis=0)
        tokens.append(np.array([tail_p[0], tail_p[1], tail_p[2],
                                _log(np.array([tail_e]))[0],
                                PID_CODES["aggregate_blob"]], dtype=np.float32))
        extras.append(np.zeros(ADD_WIDTH, dtype=np.float32))

    for index in range(keep_p):
        code = PRONG_PID_MAP.get(int(ppid[index]), 3)
        tokens.append(np.array([pe[index, 0], pe[index, 1], pe[index, 2],
                                _log(pe[index:index + 1, 3])[0], code],
                               dtype=np.float32))
        extras.append(np.array([pdedx[index], ppos[index, 0], ppos[index, 1],
                                ppos[index, 2], ppos[index, 3]], dtype=np.float32))
    if keep_p < n_prong:
        tail = pe[keep_p:].sum(axis=0)
        tokens.append(np.array([tail[0], tail[1], tail[2],
                                _log(np.array([tail[3]]))[0],
                                PID_CODES["aggregate_prong"]], dtype=np.float32))
        extras.append(np.zeros(ADD_WIDTH, dtype=np.float32))

    token_block = np.zeros((cap, TOKEN_WIDTH), dtype=np.float32)
    extra_block = np.zeros((cap, ADD_WIDTH), dtype=np.float32)
    used = min(len(tokens), cap)
    if used:
        token_block[:used] = np.stack(tokens[:used])
        extra_block[:used] = np.stack(extras[:used])
    return token_block, extra_block


def globals_row(source: dict[str, float], energy_sums: np.ndarray) -> np.ndarray:
    """His 16: 7 from get_global_features, 3 extra, 6 log energy sums."""
    passive_id = max(source["passive_id"], 0.0) / 10000.0
    passive_od = max(source["passive_od"], 0.0) / 10000.0
    row = np.array([
        np.log(max(source["muon_fuzz_energy"], 0.0) + 1e-5),
        np.log(max(source["muon_iso_blobs_energy"], 0.0) + 1e-5),
        np.log(max(source["hadron_recoil"], 0.0) + 1e-5),
        np.log(passive_id + 1e-3),
        np.log(passive_od + 1e-3),
        np.log(passive_id + passive_od + 1e-3),
        source["n_michel"],
        source["muon_present"],
        source["diphoton_mass"],
        source["charged_pion_prongs"],
    ], dtype=np.float32)
    return np.concatenate([row, np.log(energy_sums + 1e-3).astype(np.float32)])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        print(json.dumps({"cap": CAP, "token_width": TOKEN_WIDTH,
                          "add_width": ADD_WIDTH, "global_width": GLOBAL_WIDTH,
                          "pid_codes": PID_CODES}, indent=2))


if __name__ == "__main__":
    main()


# --------------------------------------------------------------------------- #
# Driving it over a slim file
# --------------------------------------------------------------------------- #

def _photon_list(tree: Any) -> list[dict[str, Any]]:
    out = []
    for tag in ("gamma1", "gamma2"):
        energy = float(getattr(tree, f"{tag}_E"))
        if energy <= 0.0:
            continue                      # his `remove_overflows` drops empty slots
        out.append({
            "four_momentum": [float(getattr(tree, f"{tag}_px")),
                              float(getattr(tree, f"{tag}_py")),
                              float(getattr(tree, f"{tag}_pz")), energy],
            "dedx": float(getattr(tree, f"{tag}_dEdx")),
            "t": float(getattr(tree, f"{tag}_time")),
        })
    return out


def _as_array(value: Any) -> np.ndarray:
    try:
        return np.asarray([v for v in value], dtype=np.float64)
    except TypeError:
        return np.asarray([float(value)], dtype=np.float64)


def build_file(slim: Path, identity_fields: tuple[str, ...],
               limit: int | None = None) -> dict[str, np.ndarray]:
    """Build his inputs for every row of one slim file, keyed by identity."""
    import ROOT

    ROOT.gROOT.SetBatch(True)
    handle = ROOT.TFile.Open(str(slim))
    tree = handle.Get("MasterAnaDev")
    total = int(tree.GetEntries())
    rows = total if limit is None else min(limit, total)

    tokens = np.zeros((rows, CAP, TOKEN_WIDTH), dtype=np.float32)
    extras = np.zeros((rows, CAP, ADD_WIDTH), dtype=np.float32)
    glob = np.zeros((rows, GLOBAL_WIDTH), dtype=np.float32)
    identity = np.zeros((rows, len(identity_fields)), dtype=np.int64)

    for index in range(rows):
        tree.GetEntry(index)
        blob = {
            "E": _as_array(tree.MasterAnaDev_BlobTotalE),
            "x": _as_array(tree.MasterAnaDev_BlobX),
            "y": _as_array(tree.MasterAnaDev_BlobY),
            "z": _as_array(tree.MasterAnaDev_BlobZ),
            "t": _as_array(tree.MasterAnaDev_BlobT),
        }
        n_prong = int(tree.prong_part_E_n)
        flat_e = _as_array(tree.prong_part_E_flat)
        flat_pos = _as_array(tree.prong_part_pos_flat)
        prong = {
            "E": flat_e.reshape(n_prong, 4) if n_prong else np.zeros((0, 4)),
            "pos": flat_pos.reshape(n_prong, 4) if n_prong else np.zeros((0, 4)),
            "pid": _as_array(tree.prong_part_pid)[:n_prong] if n_prong
            else np.zeros(0),
            "dedx": _as_array(tree.prong_dEdXMean)[:n_prong] if n_prong
            else np.zeros(0),
        }
        # DECLARED DIFFERENCE. His `get_muons(only_keep_minos_matched=True)`
        # selects on the MINOS match; this uses E > 0 as the presence test,
        # because the slim does not carry a MINOS-match flag. The two agree
        # wherever a reconstructed muon has positive energy iff it is
        # MINOS-matched, which is NOT established. Recorded in
        # `DECLARED_DIFFERENCES` so it travels with any result.
        muon = None
        muon_e = float(tree.MasterAnaDev_muon_E)
        if muon_e > 0.0:
            muon = {"four_momentum": [float(tree.MasterAnaDev_muon_Px),
                                      float(tree.MasterAnaDev_muon_Py),
                                      float(tree.MasterAnaDev_muon_Pz), muon_e],
                    "t": float(tree.muon_trackVertexTime)}
        photons = _photon_list(tree)

        token_block, extra_block = build_event(muon, photons, blob, prong)
        tokens[index] = token_block
        extras[index] = extra_block

        pids = token_block[:, 4]
        energies = np.exp(token_block[:, 3]) * (token_block[:, 3] != 0)
        sums = np.array([energies[pids == code].sum()
                         for code in (2, 3, 4, 5, 6, 7)], dtype=np.float64)
        glob[index] = globals_row({
            "muon_fuzz_energy": float(tree.muon_fuzz_energy),
            "muon_iso_blobs_energy": float(tree.muon_iso_blobs_energy),
            "hadron_recoil": float(tree.MasterAnaDev_hadron_recoil),
            "passive_id": float(
                tree.part_response_total_recoil_passive_allNonMuonClusters_id),
            "passive_od": float(
                tree.part_response_total_recoil_passive_allNonMuonClusters_od),
            "n_michel": float(tree.improved_nmichel),
            "muon_present": 1.0 if muon is not None else 0.0,
            "diphoton_mass": _diphoton_mass(photons),
            "charged_pion_prongs": float(np.isin(prong["pid"], (8, 9)).sum()),
        }, sums)
        identity[index] = [int(getattr(tree, f)) for f in identity_fields]

    handle.Close()
    return {"tokens": tokens, "add_info": extras, "globals": glob,
            "identity": identity}


def _diphoton_mass(photons: list[dict[str, Any]]) -> float:
    """His rule: only when there are EXACTLY two reconstructed photons."""
    if len(photons) != 2:
        return 0.0
    a, b = photons[0]["four_momentum"], photons[1]["four_momentum"]
    px, py, pz, e = (a[0] + b[0], a[1] + b[1], a[2] + b[2], a[3] + b[3])
    m2 = e * e - px * px - py * py - pz * pz
    return float(np.sqrt(m2)) if m2 > 0 else 0.0
