"""The campaign scope guard (no TensorFlow)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import authorization_scope as scope  # noqa: E402


def test_historical_output_dir_is_refused(tmp_path):
    root = tmp_path / "campaign-20260920"
    (root / "final").mkdir(parents=True)
    for bad in (root, root / "final" / "x", tmp_path / "other" / ".." / "campaign-20260920"):
        with pytest.raises(scope.ScopeViolation):
            scope.refuse_historical_output(bad, root=root)
    link = tmp_path / "link"
    link.symlink_to(root)
    with pytest.raises(scope.ScopeViolation):
        scope.refuse_historical_output(link / "new", root=root)
    assert scope.refuse_historical_output(tmp_path / "campaign-20260920-new", root=root)


def test_the_real_historical_root_is_refused():
    with pytest.raises(scope.ScopeViolation):
        scope.refuse_historical_output("/pscratch/sd/j/josephrb/campaign-20260920/tuning/x")


@pytest.mark.parametrize("kwargs", [
    {"bkg_mode": "negweight-refined", "measured_leg_is_real": False},
    {"bkg_mode": "mc-only", "measured_leg_is_real": True},
    {"bkg_mode": "mc-only", "measured_leg_is_real": False, "npz_keys_read": ["measured_pc"]},
    {"bkg_mode": "mc-only", "measured_leg_is_real": False,
     "input_paths": ["/pscratch/sd/j/josephrb/theirs_inputs/1A_Data/x.theirs.npz"]},
    {"bkg_mode": "mc-only", "measured_leg_is_real": False,
     "input_paths": ["/pscratch/sd/j/josephrb/campaign-20260920/join/join_data.npz"]},
])
def test_real_data_inputs_are_refused(kwargs):
    with pytest.raises(scope.ScopeViolation):
        scope.refuse_real_data_inputs(**kwargs)


def test_simulation_inputs_pass():
    scope.refuse_real_data_inputs(
        bkg_mode="mc-only", measured_leg_is_real=False,
        npz_keys_read=["reco_scalars", "truth_scalars", "part_reco"],
        input_paths=["/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/"
                     "G2_FPS_MEFHC_P12.npz", "/pscratch/sd/j/josephrb/campaign-20260920/join"])


def test_thresholds_come_from_the_frozen_design_and_cannot_move():
    historical = scope.historical_thresholds()
    assert scope.check_like_for_like_thresholds(historical) == historical
    key = sorted(historical)[0]
    lowered = dict(historical)
    lowered[key] = historical[key] * 0.9 if isinstance(historical[key], float) else "x"
    with pytest.raises(scope.ScopeViolation):
        scope.check_like_for_like_thresholds(lowered)
    with pytest.raises(scope.ScopeViolation):
        scope.check_like_for_like_thresholds({k: v for k, v in historical.items() if k != key})


class _FakeNpz:
    files = ["w_truth", "measured_scalars", "data_muon", "data_new_member"]

    def __getitem__(self, key):
        return f"array:{key}"


def test_signal_only_view_refuses_real_data_members_and_records_reads():
    view = scope.SignalOnlyNpz(_FakeNpz())
    assert "measured_scalars" in view                     # a presence check reads nothing
    for key in ("measured_scalars", "data_muon", "data_new_member"):
        with pytest.raises(scope.ScopeViolation):
            view[key]
    assert view["w_truth"] == "array:w_truth"
    assert view.keys_read == ["w_truth"]


def test_real_data_member_prefixes_are_refused():
    for key in ("measured_anything", "data_anything"):
        with pytest.raises(scope.ScopeViolation):
            scope.refuse_real_data_inputs(bkg_mode="mc-only", measured_leg_is_real=False,
                                          npz_keys_read=[key])
