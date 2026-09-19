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

So:

    token  (5 stored, 4 seen)  [px, py, pz, log E, PID]
    add_info (5)               [dE/dx, x, y, z, t]

NOT CITABLE FOR any performance claim. This is a schema, not a measurement.
"""

from __future__ import annotations

from typing import Any

TOKEN_COLUMNS: tuple[str, ...] = ("px", "py", "pz", "log_E", "pid")
TOKEN_PID_INDEX = 4
TOKEN_LOG_E_INDEX = 3
ENCODER_INPUT_DIM = 4          # after PID is pulled out
ADD_INFO_COLUMNS: tuple[str, ...] = ("dEdx", "x", "y", "z", "t")

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
