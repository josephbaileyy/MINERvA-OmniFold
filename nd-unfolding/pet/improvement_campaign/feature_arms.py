"""Feature arms: named, versioned, hashed transforms of the closure inputs (Phase C plugs in here).

A feature arm never edits the loader. It declares which per-event scalar columns it appends to the
step-1 (detector) event block and which to the step-2 (truth) event block, and `apply` reads those
columns for exactly the rows each leg uses. The leakage rule is structural: step-1 columns are read
only from `reco_scalars`, step-2 columns only from `truth_scalars`, so no truth quantity can reach
the detector-side classifier. Appended columns are standardized with the MC-half statistics of the
rows that pass the leg's selection and set to 0 elsewhere (the loader's own convention for rows
without a record).

The arm's hash covers its declaration and the source of `apply`, so a run config naming an arm
names exactly one transform. The arms beyond `baseline` are Phase C CANDIDATES, not validated.
"""

from __future__ import annotations

import hashlib
import inspect
import json
from dataclasses import asdict, dataclass
from typing import Any, Callable

SCALAR_COLUMNS = ("pt", "pparallel", "eavail", "q3")   # fullevent_fps_dataloader.SCALAR_COLS order


@dataclass(frozen=True)
class FeatureArm:
    name: str
    version: int
    description: str
    step1_reco_scalars: tuple = ()
    step2_truth_scalars: tuple = ()
    applies_to_arms: tuple = ("ours", "theirs")

    def content_hash(self) -> str:
        payload = json.dumps({"declaration": asdict(self),
                              "apply_source": inspect.getsource(apply)}, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()


REGISTRY: dict[str, FeatureArm] = {arm.name: arm for arm in (
    FeatureArm("baseline", 1, "the historical inputs, unchanged"),
    FeatureArm("reco_eavail", 1, "step 1 += reconstructed E_avail (Phase C candidate)",
               step1_reco_scalars=("eavail",), applies_to_arms=("ours",)),
    FeatureArm("truth_eavail", 1, "step 2 += true E_avail (Phase C candidate)",
               step2_truth_scalars=("eavail",)),
    FeatureArm("reco_and_truth_eavail", 1, "both of the above (Phase C candidate)",
               step1_reco_scalars=("eavail",), step2_truth_scalars=("eavail",),
               applies_to_arms=("ours",)),
)}


def get(name: str) -> FeatureArm:
    if name not in REGISTRY:
        raise KeyError(f"unknown feature arm {name!r}; known: {sorted(REGISTRY)}")
    return REGISTRY[name]


def _standardize(np: Any, values: Any, mask_fit: Any, *others: tuple) -> list[Any]:
    """Standardize by mean/std over `values[mask_fit]`; returns [values, *others] transformed."""
    ref = np.asarray(values, dtype=np.float64)[np.asarray(mask_fit, bool)]
    mu = float(ref.mean())
    sd = float(ref.std())
    if not np.isfinite(sd) or sd <= 0:
        raise ValueError("an appended feature is constant on the MC half; it carries nothing")
    out = []
    for arr, mask in ((values, mask_fit), *others):
        z = (np.asarray(arr, dtype=np.float64) - mu) / sd
        out.append(np.where(np.asarray(mask, bool), z, 0.0).astype(np.float32))
    return out


def apply(arm: FeatureArm, closure_arm: str, blocks: dict[str, Any],
          read_scalars: Callable[[str, str, Any], Any], np: Any) -> dict[str, Any]:
    """Return new event blocks with the arm's columns appended.

    `blocks` holds `pdata_reco_evt`, `mc_reco_evt`, `mc_gen_evt`, the absolute dump rows
    `pdata_rows`, `mc_rows`, and the masks `pdata_pass_reco`, `mc_pass_reco`, `mc_pass_gen`.
    `read_scalars(which, column, rows)` reads one column of `reco_scalars` / `truth_scalars`.
    """
    if closure_arm not in arm.applies_to_arms:
        raise ValueError(f"feature arm {arm.name!r} is not defined for the {closure_arm!r} arm")
    out = dict(blocks)
    added: dict[str, list[str]] = {"step1": [], "step2": []}
    for column in arm.step1_reco_scalars:
        mc_vals = read_scalars("reco", column, blocks["mc_rows"])
        pd_vals = read_scalars("reco", column, blocks["pdata_rows"])
        mc_z, pd_z = _standardize(np, mc_vals, blocks["mc_pass_reco"],
                                  (pd_vals, blocks["pdata_pass_reco"]))
        out["mc_reco_evt"] = np.concatenate([out["mc_reco_evt"], mc_z[:, None]], axis=1)
        out["pdata_reco_evt"] = np.concatenate([out["pdata_reco_evt"], pd_z[:, None]], axis=1)
        added["step1"].append(f"reco_scalars:{column}")
    for column in arm.step2_truth_scalars:
        vals = read_scalars("truth", column, blocks["mc_rows"])
        (z,) = _standardize(np, vals, blocks["mc_pass_gen"])
        out["mc_gen_evt"] = np.concatenate([out["mc_gen_evt"], z[:, None]], axis=1)
        added["step2"].append(f"truth_scalars:{column}")
    out["added_columns"] = added
    return out
