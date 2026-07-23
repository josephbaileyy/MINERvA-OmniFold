"""Machine-auditable arm and representation manifests."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any, Mapping

import numpy as np

from .contracts import PAD_CATEGORY, TokenBatch
from .utils import fingerprint

TYPE_GENERIC = 1
TYPE_RECO_CLUSTER = 2
TYPE_MUON = 3
TYPE_TRACK = 4
TYPE_OVERFLOW = 5

VIEW_X = 1
VIEW_U = 2
VIEW_V = 3
VIEW_AGGREGATE = 4

BASELINE_GLOBALS = ("mu_pt", "mu_pparallel")
MUON_OBJECT_GLOBALS = ("mu_energy", "mu_cos_phi", "mu_sin_phi")
RICH_GLOBALS_NO_CHARGE = (
    "eavail",
    "q3",
    "minos_ok",
    "vertex_x",
    "vertex_y",
    "vertex_z",
)
CHARGE_GLOBAL = ("mu_charge",)


@dataclass(frozen=True)
class FeatureCapabilities:
    real_object_types: bool
    object_type_source: str
    detector_view: bool
    muon_token: bool
    muon_token_coordinates_audited: bool
    overflow_aggregate: bool
    audited_globals: tuple[str, ...]
    unsupported_reasons: Mapping[str, str]
    source_kind: str = "unknown"


@dataclass(frozen=True)
class ArmManifest:
    arm: str
    comparison_parent: str
    initialization: str
    use_real_types: bool
    use_detector_view: bool
    muon_representation: str
    use_overflow_aggregate: bool
    active_globals: tuple[str, ...]
    disabled_features: Mapping[str, str]
    architecture_family: str = "independent-pet2-small-concept-match-v1"
    category_zero: str = "pad_or_unknown_only"

    def payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["fingerprint"] = fingerprint(payload)
        return payload


def build_arm_manifest(
    arm: str,
    capabilities: FeatureCapabilities,
    *,
    use_detector_view: bool | None = None,
    muon_representation: str | None = None,
    use_overflow_aggregate: bool = False,
) -> ArmManifest:
    """Build frozen, non-confounded random-arm feature manifests.

    ``D`` and ``E`` remain accepted as compatibility spellings for
    ``D-typed`` and ``E-rich``; receipts always carry the canonical name.
    """
    aliases = {
        "c": "C",
        "d": "D-typed",
        "d-view": "D-view",
        "d-typed": "D-typed",
        "e": "E-rich",
        "e-muon": "E-muon",
        "e-rich-no-charge": "E-rich-no-charge",
        "e-rich": "E-rich",
    }
    canonical_arm = aliases.get(str(arm).lower())
    if canonical_arm is None:
        raise ValueError(
            "random arm must be C, D-view, D-typed, E-muon, "
            "E-rich-no-charge, or E-rich"
        )
    arm = canonical_arm
    default_view = arm == "D-view"
    if use_detector_view is None:
        use_detector_view = default_view
    elif arm == "D-view" and not use_detector_view:
        raise ValueError("D-view cannot disable its sole declared detector-view feature")
    elif arm != "D-view" and use_detector_view:
        raise ValueError("detector view belongs only to the explicit D-view arm")
    # C is frozen on the current TF-B numeric footing: the baseline muon
    # (pT,pparallel) summaries are present.  E-muon adds the remaining audited
    # reconstructed-muon object block without changing token/type capacity.
    default_muon = "global"
    if muon_representation is None:
        muon_representation = default_muon
    if muon_representation not in {"global", "token", "disabled"}:
        raise ValueError("muon_representation must be global, token, or disabled")
    disabled = dict(capabilities.unsupported_reasons)
    use_types = arm == "D-typed"
    if use_types and not capabilities.real_object_types:
        raise ValueError(
            "D-typed requires real reconstructed object types; detector view "
            "and generic G2 clusters are not object types"
        )
    if use_detector_view and not capabilities.detector_view:
        raise ValueError("detector-view ablation requested but view is unavailable")
    if muon_representation == "token" and not capabilities.muon_token:
        raise ValueError("muon-token ablation requested but aligned muon fields are unavailable")
    if (
        muon_representation == "token"
        and not capabilities.muon_token_coordinates_audited
    ):
        raise ValueError(
            "muon-token KNN coordinates are unaudited; this ablation is "
            "synthetic-only until physical coordinates are supplied"
        )
    if use_overflow_aggregate and not capabilities.overflow_aggregate:
        raise ValueError("overflow aggregate requested but pre-truncation evidence is unavailable")
    active_globals: list[str] = []
    if muon_representation == "global":
        active_globals.extend(BASELINE_GLOBALS)
        if arm.startswith("E-"):
            missing = [
                name
                for name in MUON_OBJECT_GLOBALS
                if name not in capabilities.audited_globals
            ]
            if missing:
                raise ValueError(
                    f"{arm} reconstructed-muon globals are not audited/available: {missing}"
                )
            active_globals.extend(MUON_OBJECT_GLOBALS)
    if arm in {"E-rich-no-charge", "E-rich"}:
        missing = [
            name
            for name in RICH_GLOBALS_NO_CHARGE
            if name not in capabilities.audited_globals
        ]
        if missing:
            raise ValueError(
                f"{arm} richer globals are not audited/available: {missing}"
            )
        active_globals.extend(RICH_GLOBALS_NO_CHARGE)
    if arm == "E-rich":
        missing = [name for name in CHARGE_GLOBAL if name not in capabilities.audited_globals]
        if missing:
            raise ValueError(f"E-rich charge global is not audited/available: {missing}")
        active_globals.extend(CHARGE_GLOBAL)
    if not use_types:
        disabled["object_type"] = "generic-token control; D-typed is a separate arm"
    if not use_detector_view:
        disabled["detector_view"] = "disabled outside the distinct D-view arm"
    if not use_overflow_aggregate:
        disabled["overflow_aggregate"] = (
            "separate overflow ablation disabled or source lacks pre-truncation evidence"
        )
    return ArmManifest(
        arm=arm,
        comparison_parent={
            "C": "TF-B",
            "D-view": "C",
            "D-typed": "C",
            "E-muon": "C",
            "E-rich-no-charge": "E-muon",
            "E-rich": "E-rich-no-charge",
        }[arm],
        initialization="random",
        use_real_types=use_types,
        use_detector_view=use_detector_view,
        muon_representation=muon_representation,
        use_overflow_aggregate=use_overflow_aggregate,
        active_globals=tuple(active_globals),
        disabled_features=disabled,
    )


def materialize_feature_view(batch: TokenBatch, manifest: ArmManifest) -> TokenBatch:
    """Apply only the feature changes declared by an arm manifest."""
    batch = batch.validated()
    type_id = batch.type_id.copy()
    view_id = batch.view_id.copy()
    continuous = batch.continuous.copy()
    coords = batch.coords.copy()
    token_mask = batch.token_mask.copy()
    overflow = batch.type_id == TYPE_OVERFLOW
    if not manifest.use_real_types:
        type_id[token_mask] = TYPE_GENERIC
    if not manifest.use_detector_view:
        view_id[...] = PAD_CATEGORY
    if not manifest.use_overflow_aggregate:
        token_mask[overflow] = False
        type_id[overflow] = PAD_CATEGORY
        view_id[overflow] = PAD_CATEGORY
        continuous[overflow] = 0.0
        coords[overflow] = 0.0
    names = batch.global_names
    globals_ = batch.globals.copy()
    active = set(manifest.active_globals)
    for index, name in enumerate(names):
        if name not in active:
            globals_[:, index] = 0.0
    result = replace(
        batch,
        continuous=continuous,
        coords=coords,
        token_mask=token_mask,
        type_id=type_id,
        view_id=view_id,
        globals=globals_,
        provenance=f"{batch.provenance}|arm={manifest.arm}",
    )
    if manifest.muon_representation == "token":
        if batch.muon_present is None:
            raise ValueError("muon token seam is unavailable")
        n = batch.n_rows
        mu_mask = batch.muon_present[:, None]
        mu_type = np.where(mu_mask, TYPE_MUON, PAD_CATEGORY).astype(np.int64)
        mu_view = np.zeros((n, 1), dtype=np.int64)
        result = replace(
            result,
            continuous=np.concatenate([batch.muon_continuous[:, None, :], continuous], axis=1),
            coords=np.concatenate([batch.muon_coords[:, None, :], coords], axis=1),
            token_mask=np.concatenate([mu_mask, token_mask], axis=1),
            type_id=np.concatenate([mu_type, type_id], axis=1),
            view_id=np.concatenate([mu_view, view_id], axis=1),
        )
    return result.validated()


def exact_arm_diff(left: ArmManifest, right: ArmManifest) -> dict[str, tuple[Any, Any]]:
    """Machine-readable declared differences, excluding derived fingerprints."""
    a = asdict(left)
    b = asdict(right)
    return {
        key: (a[key], b[key])
        for key in a
        if key != "comparison_parent" and a[key] != b[key]
    }
