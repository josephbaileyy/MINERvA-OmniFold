"""The campaign scope guard that the 2026-09-22 authorization record promises.

`docs/orchestration/AUTHORIZATION-20260922-pet-improvement-campaign.md`, "Enforcement": the guard
refuses (1) real-data inputs to any unfolding stage, (2) the historical comparison's output
directory as a write target, and (3) thresholds other than the historical ones for like-for-like
verdicts. Each check raises `ScopeViolation`; none of them warns.

The historical thresholds are IMPORTED from `configuration_comparison/frozen_design.THRESHOLDS`
(loaded by file path, so no `sys.path` entry can substitute another copy), never retyped.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from typing import Any, Iterable, Mapping

HISTORICAL_OUTPUT_ROOT = Path("/pscratch/sd/j/josephrb/campaign-20260920")
FROZEN_DESIGN_PATH = (Path(__file__).resolve().parent.parent / "configuration_comparison" /
                      "frozen_design.py")

# Keys of the full-event inventory npz that hold REAL measured data. The mc-only closure never
# reads them; an unfolding stage that asks for one is refused.
REAL_DATA_NPZ_KEYS = frozenset({
    "measured_pc", "measured_scalars", "data_muon", "data_vertex", "data_view", "data_time",
    "data_pot", "data_identity_hash"})
# Path fragments naming real-data streams of his built inputs and their identity joins.
# Any member whose name starts with one of these is a real-data member as well (the G2 dump names
# its measured-side arrays `measured_*` / `data_*`), so a future member is refused without an edit.
REAL_DATA_NPZ_PREFIXES = ("measured_", "data_")
REAL_DATA_PATH_MARKERS = ("_Data/", "/join_data.", "Data_", "/data/")
ALLOWED_BKG_MODE = "mc-only"


class ScopeViolation(RuntimeError):
    """An action outside the 2026-09-22 authorization."""


def historical_thresholds() -> dict[str, Any]:
    """`frozen_design.THRESHOLDS`, loaded from its file (the comparison's own record)."""
    spec = importlib.util.spec_from_file_location("_frozen_design_for_scope", FROZEN_DESIGN_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return dict(module.THRESHOLDS)


def refuse_historical_output(path: os.PathLike | str,
                             root: Path = HISTORICAL_OUTPUT_ROOT) -> Path:
    """Refuse `path` as a write target if it is, or lies under, the historical output root.

    Resolved without requiring existence, and symlinks are followed where they exist, so
    `../campaign-20260920` and a link into it are both caught.
    """
    target = Path(os.path.realpath(os.fspath(path)))
    guarded = Path(os.path.realpath(os.fspath(root)))
    if target == guarded or guarded in target.parents:
        raise ScopeViolation(
            f"{target} is inside the historical comparison's outputs {guarded}; those are "
            "preserved unmodified and are never a write target")
    return target


def refuse_real_data_inputs(*, bkg_mode: str, measured_leg_is_real: bool,
                            npz_keys_read: Iterable[str] = (),
                            input_paths: Iterable[os.PathLike | str] = ()) -> None:
    """Refuse any sign that an unfolding stage would consume real measured data."""
    if bkg_mode != ALLOWED_BKG_MODE:
        raise ScopeViolation(
            f"bkg_mode {bkg_mode!r}: only {ALLOWED_BKG_MODE!r} (simulated pseudo-data) is "
            "authorized; any other mode builds a measured leg from real data")
    if measured_leg_is_real:
        raise ScopeViolation("the measured leg is real data; unfold simulated pseudo-data only")
    real_keys = sorted({k for k in npz_keys_read
                        if k in REAL_DATA_NPZ_KEYS or k.startswith(REAL_DATA_NPZ_PREFIXES)})
    if real_keys:
        raise ScopeViolation(f"real-data arrays requested from the inventory: {real_keys}")
    for path in input_paths:
        text = os.fspath(path)
        hits = [m for m in REAL_DATA_PATH_MARKERS if m in text]
        if hits:
            raise ScopeViolation(f"input {text} names a real-data stream ({hits})")


class SignalOnlyNpz:
    """A read-through view of an opened inventory npz that REFUSES every real-data member.

    `refuse_real_data_inputs` trusts its caller's list of keys; this makes the list true by
    construction: every member access goes through `refuse_real_data_inputs`, so a code path that
    asks for `measured_scalars` (as the historical loader does even in mc-only mode) raises
    `ScopeViolation` instead of reading it. `keys_read` records what was actually read.
    Presence checks (`key in view.files`) read nothing and are allowed.
    """

    def __init__(self, npz: Any) -> None:
        self._npz = npz
        self.keys_read: list[str] = []

    @property
    def files(self) -> list[str]:
        return list(self._npz.files)

    def __contains__(self, key: str) -> bool:
        return key in self._npz.files

    def __getitem__(self, key: str) -> Any:
        refuse_real_data_inputs(bkg_mode=ALLOWED_BKG_MODE, measured_leg_is_real=False,
                                npz_keys_read=[key])
        if key not in self.keys_read:
            self.keys_read.append(key)
        return self._npz[key]

    def close(self) -> None:
        close = getattr(self._npz, "close", None)
        if close is not None:
            close()


def check_like_for_like_thresholds(thresholds: Mapping[str, Any]) -> dict[str, Any]:
    """A like-for-like verdict must use EXACTLY the historical thresholds.

    Returns the historical thresholds when `thresholds` equals them key for key; otherwise
    refuses, naming every key that differs. A new reference is a prospective recommendation and
    is not reported through a like-for-like verdict.
    """
    historical = historical_thresholds()
    given = dict(thresholds)
    differing = {k: (given.get(k), historical.get(k))
                 for k in set(given) | set(historical) if given.get(k) != historical.get(k)}
    if differing:
        raise ScopeViolation(
            f"like-for-like verdict with thresholds other than the historical ones: {differing} "
            "(given, historical). The historical thresholds are not lowered or re-derived")
    return historical
