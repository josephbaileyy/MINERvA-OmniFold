"""Gregor's token construction, read out of his preprocessing rather than inferred.

`PET2` receives three tensors per event and the freeze pins their widths: tokens
`input_dim=4`, a categorical `pid`, and `add_info` of width 5. This file records
WHAT goes in each slot, derived from his code, so the extraction that builds them
can be reviewed against him instead of against a paraphrase.

Derivation, file and line:

* `train.py:1312-1313` --- `pid = X[:, :, pid_idx]`, then that column is dropped
  from `X`. So the stored token is 5 wide and the encoder sees 4.
* `train.py:2196-2198` --- `concat_additional_info` is False for OmniLearned, so
  `add_info` is a separate tensor and not appended to the token.
* `preprocessing.py:596` --- `E = np.exp(event_features[:, 3])` and
  `pid = event_features[:, 4]`, fixing index 3 as log-energy and 4 as PID.
* `preprocessing.py:380` --- `muon_four_momentum = muons.data[:, :4]`, fixing
  0..3 as the four-momentum.
* `preprocessing.py:390-400` --- the additional-info comment is explicit:
  "[dE/dx, x, y, z, t]", with zeros where a category has no such quantity.

CORRECTED 2026-09-20. The derivation above describes the INTERMEDIATE stored
form and stops one function too early. `preprocessing.py:239-288`
(`convert_to_eta_phi_pt`) converts `[px, py, pz, E]` to
`[delta_eta, delta_phi, log(pT+1e-6), log(E+1e-6)]` and line 287 stacks exactly
those four as what the encoder sees; `eta` is clipped to [-10, 10] and `phi` is
raw `arctan2`. `preprocessing.py:343-344` (`preprocess_coords`) divides the
positions by 10000.

Building the intermediate form and feeding it to the model is not his
configuration, and it is not a subtle difference: raw momenta and raw
millimetre positions reach 8.2e4, and his network has no input normalisation
that would absorb them. Measured, job 58602446: the first step-1 fit returned
`Last val loss nan` and the engine's reweight gate refused 10,000 non-finite
logits.

So:

    stored intermediate         [px, py, pz, E]        <- NOT what the model sees
    token  (5 stored, 4 seen)   [eta, phi, log pT, log E, PID]
    add_info (5)                [dE/dx, x/1e4, y/1e4, z/1e4, t/1e4]

NOT CITABLE FOR any performance claim. This is a schema, not a measurement.
"""

from __future__ import annotations

from typing import Any

TOKEN_COLUMNS: tuple[str, ...] = ("px", "py", "pz", "log_E", "pid")
TOKEN_PID_INDEX = 4
TOKEN_LOG_E_INDEX = 3
ENCODER_INPUT_DIM = 4          # after PID is pulled out
ADD_INFO_COLUMNS: tuple[str, ...] = ("dEdx", "x_over_1e4", "y_over_1e4",
                                     "z_over_1e4", "t_over_1e4")
TOKEN_COLUMNS: tuple[str, ...] = ("delta_eta", "delta_phi", "log_pt", "log_E",
                                  "pid")
COORD_DIVISOR = 10000.0
ETA_CLIP = 10.0
LOG_EPSILON = 1e-6

# PID codes, from the energy-sum comment at `preprocessing.py:589`:
# "2=blob, 3=prong(3), 4=prong(8), 5=prong(13), 6=agg_blob, 7=agg_prong".
# Muon and photon occupy the remaining low codes; the aggregate codes exist
# because overflow beyond the cap is MERGED into one token rather than dropped.
# RESOLVED 2026-09-20 from `preprocessing.py:423` verbatim: "muon = 0,
# photon = 1, blob = 2 (no PID), prong PIDs: 3=3, 8=4, 13=5, aggregated_blob = 6,
# aggregated_prong = 7". The first two were missing from the earlier reading,
# which had only the codes the energy-sum comment happened to list.
PID_CODES: dict[str, int] = {
    "muon": 0,
    "photon": 1,
    "blob": 2,
    "prong_3": 3,
    "prong_8": 4,
    "prong_13": 5,
    "aggregate_blob": 6,
    "aggregate_prong": 7,
}
ENERGY_SUM_PIDS: tuple[int, ...] = (2, 3, 4, 5, 6, 7)

# Which source columns fill each slot, per category. `None` means his code puts a
# zero there, and the zeros are part of the schema rather than missing data --
# `preprocessing.py:391` says so: "Put zeros for muon dedx, blob dedx, and muon
# and photon coords."
CATEGORY_SOURCES: dict[str, dict[str, Any]] = {
    "muon": {
        "four_momentum": "muons.data[:, :4]",
        "dEdx": None,
        "coords": None,
        "time": "muons.data[:, -1] via preprocess_coords",
    },
    "photon": {
        "four_momentum": "gamma{1,2}_{px,py,pz,E}",
        "dEdx": "gamma{1,2}_dEdx",
        "coords": None,
        "time": "gamma{1,2}_time via preprocess_coords",
    },
    "blob": {
        "four_momentum": "MasterAnaDev_BlobTotalE into the log-E slot",
        "dEdx": None,
        "coords": "MasterAnaDev_Blob{X,Y,Z} via preprocess_coords",
        "time": "MasterAnaDev_BlobT via preprocess_coords",
    },
    "prong": {
        "four_momentum": "prong_part_E[0:4]",
        "dEdx": "prong_dEdXMean via preprocess_dEdX  (SUBSTITUTED: his key list "
                "says prong_part_dEdXMean, which is absent from our tuples)",
        "coords": "prong_part_pos[0:3] via preprocess_coords",
        "time": "prong_part_pos[3] via preprocess_coords",
    },
}

OVERFLOW_POLICY = (
    "beyond the cap, his code AGGREGATES rather than truncates: the surplus blobs "
    "become one token at PID 6 and the surplus prongs one at PID 7. So a cap of 33 "
    "does not simply discard the 11.87 % of events that exceed it -- it merges "
    "their tail. Any comparison that truncates instead would be running a "
    "different model, and the aggregate PIDs are the tell that his does not."
)

# RESOLVED: `preprocessing.py:546` concatenates in a fixed order.
CATEGORY_ORDER: tuple[str, ...] = ("muon", "photon", "blob", "prong")

# And the cap has TWO paths, which is the part that would have been easy to get
# wrong. With `max_objects` alone he sorts by ENERGY DESCENDING --
# `event_features[:, 3].argsort()[::-1]` -- and keeps the top N, so the cap drops
# the softest objects rather than the last-listed ones. With `max_blobs` and
# `max_prongs` set he takes the aggregate path instead, and asserts
# `n <= max_prongs + max_blobs + 2 + 1`: two photons and one muon always have
# reserved slots.
CAP_PATHS = {
    "max_objects_only": ("sort by log-energy DESCENDING and keep the top N; the "
                         "softest objects are dropped, not the last-listed"),
    "max_blobs_and_max_prongs": ("aggregate the surplus into PID 6 and 7; the "
                                 "budget is max_blobs + max_prongs + 2 photons "
                                 "+ 1 muon"),
}

# BLOBS HAVE NO MOMENTUM, so he builds one: the blob position is normalised to a
# unit vector from the origin and scaled by the blob energy -- `preprocessing.py`
# comments it as "assume a massless particle originating from the origin", with a
# guard against a zero-length position. An extraction that put the blob's
# coordinates straight into the momentum slots would be a different model, and
# the difference would be invisible in any shape check.
BLOB_FOUR_MOMENTUM = (
    "unit(blob_xyz) * blob_total_E in slots 0..2, blob_total_E in slot 3; "
    "positions with |xyz| <= 1e-6 are guarded against division by zero"
)

# Prong dense-matrix layout implied by `prong_keys`: pos 0:4, E 4:8, score 8,
# mass 9, charge 10, pid 11, dEdX 12 -- and his code reads the four-momentum as
# `prongs.data[:, 4:8]` and the PID as `prongs.data[:, -2]`, which agrees.
PRONG_DENSE_LAYOUT = {"pos": (0, 4), "four_momentum": (4, 8), "score": 8,
                      "mass": 9, "charge": 10, "pid": 11, "dEdX": 12}

UNRESOLVED = (
    "the max_blobs / max_prongs split that sums to the 33-token cap. His assertion "
    "fixes the budget as max_blobs + max_prongs + 3, so 33 admits several splits "
    "and they are not equivalent: the split decides WHICH surplus gets aggregated. "
    "It has to be read from the paper's own run configuration, not chosen by us.",
)


def schema() -> dict[str, Any]:
    return {
        "token_columns": list(TOKEN_COLUMNS),
        "token_pid_index": TOKEN_PID_INDEX,
        "encoder_input_dim": ENCODER_INPUT_DIM,
        "add_info_columns": list(ADD_INFO_COLUMNS),
        "pid_codes": dict(PID_CODES),
        "energy_sum_pids": list(ENERGY_SUM_PIDS),
        "category_sources": CATEGORY_SOURCES,
        "overflow_policy": OVERFLOW_POLICY,
        "unresolved": list(UNRESOLVED),
    }


def convert_to_eta_phi_pt(four_momentum):
    """`[px, py, pz, E]` -> `[delta_eta, delta_phi, log pT, log E]`.

    Transcribed from `preprocessing.py:239-288`, including the guards, because
    they are part of the definition: `eta` is zero where `p`, `p+pz` or `p-pz`
    is below 1e-6 and clipped to +/-10 elsewhere, `phi` is raw `arctan2` with
    NO periodic encoding, and both logs carry his 1e-6.

    The clip and the zero-fill are not defensive padding around his formula --
    they ARE his formula at the edges, and a version without them would differ
    from his exactly on the forward-going tracks the detector sees most of.
    """
    import numpy as np

    fm = np.asarray(four_momentum, dtype=np.float64)
    if fm.ndim != 2 or fm.shape[1] != 4:
        raise ValueError(f"expected (n, 4) four-momenta, got {fm.shape}")
    px, py, pz, energy = fm[:, 0], fm[:, 1], fm[:, 2], fm[:, 3]
    pt = np.sqrt(px ** 2 + py ** 2)
    p = np.sqrt(px ** 2 + py ** 2 + pz ** 2)
    eta = np.zeros_like(pz)
    valid = (p > 1e-6) & (np.abs(p + pz) > 1e-6) & (np.abs(p - pz) > 1e-6)
    with np.errstate(divide="ignore", invalid="ignore"):
        eta[valid] = np.clip(
            0.5 * np.log((p[valid] + pz[valid]) / (p[valid] - pz[valid])),
            -ETA_CLIP, ETA_CLIP)
    phi = np.arctan2(py, px)
    log_pt = np.log(np.maximum(pt, 0.0) + LOG_EPSILON)
    log_e = np.log(np.maximum(energy, 0.0) + LOG_EPSILON)
    return np.stack([eta, phi, log_pt, log_e], axis=1)


def preprocess_coords(coord):
    """`preprocessing.py:343-344`. Positions and time divided by 10000."""
    import numpy as np

    return np.asarray(coord, dtype=np.float64) / COORD_DIVISOR


def convert_packed(packed):
    """Stored `[px,py,pz,logE,pid | dEdx,x,y,z,t]` -> what his model sees.

    Applied at GATHER time rather than in the build, because his own pipeline
    converts AFTER capping and aggregation -- which operate on four-momenta in
    both his code and ours -- so the stage is equivalent and 65 GB of built
    shards do not have to be rebuilt to be correct.

    NO ROUND TRIP. `eta`, `phi` and `log pT` need only `px, py, pz`, which are
    stored exactly, and `log E` is already column 3. Nothing is recovered by
    exponentiating and re-logging.

    PADDING STAYS ZERO. His `_pad_or_truncate` pads with literal zeros after
    conversion, and the arm's mask reads `log E != 0`, so a row that is
    identically zero must come back identically zero -- converting it would
    give `[0, 0, -13.8, -13.8, 0]` and turn every pad into a token.
    """
    import numpy as np

    packed = np.asarray(packed, dtype=np.float64)
    if packed.ndim != 3 or packed.shape[-1] != 10:
        raise ValueError(f"expected (n, tokens, 10), got {packed.shape}")
    out = np.array(packed, copy=True)
    padding = np.all(packed == 0.0, axis=-1)

    flat = packed.reshape(-1, 10)
    px, py, pz = flat[:, 0], flat[:, 1], flat[:, 2]
    pt = np.sqrt(px ** 2 + py ** 2)
    p = np.sqrt(px ** 2 + py ** 2 + pz ** 2)
    eta = np.zeros_like(pz)
    valid = (p > 1e-6) & (np.abs(p + pz) > 1e-6) & (np.abs(p - pz) > 1e-6)
    with np.errstate(divide="ignore", invalid="ignore"):
        eta[valid] = np.clip(
            0.5 * np.log((p[valid] + pz[valid]) / (p[valid] - pz[valid])),
            -ETA_CLIP, ETA_CLIP)
    converted = out.reshape(-1, 10)
    converted[:, 0] = eta
    converted[:, 1] = np.arctan2(py, px)
    converted[:, 2] = np.log(np.maximum(pt, 0.0) + LOG_EPSILON)
    # column 3 is already log E; column 4 is the PID code
    converted[:, 5 + 1:5 + 5] /= COORD_DIVISOR        # x, y, z, t
    out = converted.reshape(packed.shape)
    out[padding] = 0.0
    return out
