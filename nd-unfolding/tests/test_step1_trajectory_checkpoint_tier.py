#!/usr/bin/env python3
"""`--checkpoint-tier` on step1_increment_trajectory.py: does it select what it says it selects?

WHY THIS FILE EXISTS. Gate 6 reads the trajectory metric at iterations 0, 1, 2 from checkpoints of
two different provenance tiers -- best-epoch at 0 and 1, BEN-043 `_final` at 2 -- and member 3's
FAIL is a `+0.001098` rise at exactly the step that crosses that boundary, against a best-vs-final
systematic BEN-043 measured at ~1.3% on the fold-forward ratio. Leg 0 measures that systematic on
the Gate-6 metric itself by forcing the whole trajectory to one tier. The control is therefore
load-bearing for a verdict, and the two ways it can be silently wrong are:

  * `auto` stops meaning what it meant, which would change every existing caller; and
  * an explicit tier FALLS BACK to the other tier when its file is missing, which would compare a
    tier against itself, measure a gap of zero, and read as "no tier artifact" -- the exact
    conclusion the leg is trying to test.

Both are checked below on the real eight-checkpoint member inventory. Because a guard that cannot
fail proves nothing (the BEN-032/BEN-040 family), `test_the_guards_have_power` reconstructs the
pre-flag resolver and requires the no-fallback assertions to fire against it.

    python3 -m pytest nd-unfolding/tests/test_step1_trajectory_checkpoint_tier.py -q
"""
import os
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_PET = os.path.join(os.path.dirname(_HERE), "pet")
if _PET not in sys.path:
    sys.path.insert(0, _PET)

# Import the module by file, not by package: importing the package would drag in the TensorFlow
# stack that main() needs and this resolver deliberately does not.
import importlib.util

_SPEC = importlib.util.spec_from_file_location(
    "_step1_traj_under_test", os.path.join(_PET, "step1_increment_trajectory.py"))
_MOD = importlib.util.module_from_spec(_SPEC)
try:
    _SPEC.loader.exec_module(_MOD)
except Exception as exc:  # pragma: no cover - surfaces an env problem instead of silently skipping
    pytest.skip(f"could not load step1_increment_trajectory.py: {exc}", allow_module_level=True)

resolve_checkpoint = _MOD.resolve_checkpoint
CHECKPOINT_TIERS = _MOD.CHECKPOINT_TIERS

NAME = "pet_fullevent_ml_member3"


@pytest.fixture
def member_inventory(tmp_path):
    """The exact inventory sbatch_gate6_member_trajectory_array.sh asserts for every member:
    six best-epoch files (iterations 0,1,2 x steps 1,2) plus `_final` for iteration 2 only."""
    wf = tmp_path / "w_nominal"
    wf.mkdir()
    for it in range(3):
        for step in (1, 2):
            (wf / f"OmniFold_{NAME}_iter{it}_step{step}.weights.h5").write_bytes(b"best")
    for step in (1, 2):
        (wf / f"OmniFold_{NAME}_iter2_step{step}_final.weights.h5").write_bytes(b"final")
    return str(wf)


def _tiers(wf, tier):
    return {(it, step): resolve_checkpoint(wf, NAME, it, step, tier)[1]
            for it in range(3) for step in (1, 2)}


def test_auto_is_the_historical_mixed_tier_reading(member_inventory):
    """auto must still produce best-epoch at 0 and 1 and _final at 2 -- the table in
    PLAN-20260813-gate6-cml-retry-design.md section 1a. If this moves, every committed trajectory
    number was produced by a different rule than the one in the tree."""
    assert _tiers(member_inventory, "auto") == {
        (0, 1): "best-epoch", (0, 2): "best-epoch",
        (1, 1): "best-epoch", (1, 2): "best-epoch",
        (2, 1): "final(BEN-043)", (2, 2): "final(BEN-043)",
    }


def test_auto_is_the_default_so_no_existing_caller_changes():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint-tier", choices=CHECKPOINT_TIERS, default="auto")
    assert ap.parse_args([]).checkpoint_tier == "auto"
    assert set(CHECKPOINT_TIERS) == {"auto", "best-epoch", "final"}


def test_best_epoch_is_tier_clean_and_changes_only_iteration_2(member_inventory):
    """The Leg 0 reading. Forcing best-epoch must move iteration 2 and nothing else, because
    iterations 0 and 1 were already best-epoch -- so the difference against the committed `auto`
    run is attributable to the tier at iteration 2 alone."""
    forced = _tiers(member_inventory, "best-epoch")
    assert set(forced.values()) == {"best-epoch"}
    auto = _tiers(member_inventory, "auto")
    assert {k for k in forced if forced[k] != auto[k]} == {(2, 1), (2, 2)}


def test_best_epoch_returns_the_file_without_the_final_suffix(member_inventory):
    path, tier = resolve_checkpoint(member_inventory, NAME, 2, 2, "best-epoch")
    assert tier == "best-epoch"
    assert os.path.basename(path) == f"OmniFold_{NAME}_iter2_step2.weights.h5"
    assert open(path, "rb").read() == b"best"


def test_final_reads_the_final_file_where_it_exists(member_inventory):
    path, tier = resolve_checkpoint(member_inventory, NAME, 2, 1, "final")
    assert tier == "final(BEN-043)"
    assert os.path.basename(path) == f"OmniFold_{NAME}_iter2_step1_final.weights.h5"
    assert open(path, "rb").read() == b"final"


@pytest.mark.parametrize("it,step", [(0, 1), (0, 2), (1, 1), (1, 2)])
def test_final_fails_closed_where_no_final_exists_it_does_not_fall_back(member_inventory, it, step):
    """THE LOAD-BEARING ONE. Iterations 0 and 1 have no `_final`. A fallback here would hand back
    best-epoch weights while the receipt recorded `final`, and a best-vs-final contrast built from
    that would measure zero by construction."""
    with pytest.raises(SystemExit) as exc:
        resolve_checkpoint(member_inventory, NAME, it, step, "final")
    assert "does not fall back" in str(exc.value)


def test_best_epoch_fails_closed_when_the_best_epoch_file_is_absent(tmp_path):
    wf = tmp_path / "w_nominal"
    wf.mkdir()
    (wf / f"OmniFold_{NAME}_iter2_step2_final.weights.h5").write_bytes(b"final")
    with pytest.raises(SystemExit) as exc:
        resolve_checkpoint(str(wf), NAME, 2, 2, "best-epoch")
    assert "does not fall back" in str(exc.value)


def test_auto_still_fails_closed_when_neither_tier_exists(tmp_path):
    wf = tmp_path / "w_nominal"
    wf.mkdir()
    with pytest.raises(SystemExit) as exc:
        resolve_checkpoint(str(wf), NAME, 0, 1, "auto")
    assert "missing checkpoint" in str(exc.value)


def test_an_unknown_tier_is_rejected_rather_than_treated_as_auto(member_inventory):
    with pytest.raises(SystemExit) as exc:
        resolve_checkpoint(member_inventory, NAME, 2, 1, "last-epoch")
    assert "unknown checkpoint tier" in str(exc.value)


def test_the_guards_have_power(member_inventory):
    """Power proof: reconstruct the PRE-FLAG resolver (auto-only, silent fallback) and require the
    no-fallback guards to reject it. Without this, all of the above could pass vacuously."""
    def pre_flag_resolver(weights_folder, multifold_name, it, step, tier):
        fin = os.path.join(weights_folder,
                           f"OmniFold_{multifold_name}_iter{it}_step{step}_final.weights.h5")
        if os.path.exists(fin):
            return fin, "final(BEN-043)"
        p = os.path.join(weights_folder, f"OmniFold_{multifold_name}_iter{it}_step{step}.weights.h5")
        if not os.path.exists(p):
            raise SystemExit(f"[traj] missing checkpoint {p} (fail closed)")
        return p, "best-epoch"

    # The old resolver ignores the tier argument entirely, which is exactly the silent-fallback bug.
    assert pre_flag_resolver(member_inventory, NAME, 0, 1, "final")[1] == "best-epoch"
    assert pre_flag_resolver(member_inventory, NAME, 2, 2, "best-epoch")[1] == "final(BEN-043)"
    # And it would therefore report a tier-clean best-epoch trajectory that is not tier-clean.
    old = {(it, step): pre_flag_resolver(member_inventory, NAME, it, step, "best-epoch")[1]
           for it in range(3) for step in (1, 2)}
    assert set(old.values()) == {"best-epoch", "final(BEN-043)"}
    assert set(_tiers(member_inventory, "best-epoch").values()) == {"best-epoch"}
