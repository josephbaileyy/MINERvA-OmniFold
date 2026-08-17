#!/usr/bin/env python3
"""The three PET diagnostics' runtime identity guards, exercised — because none of them ever was.

WHAT THIS IS AND IS NOT. `inversion_screen.py`, `push_vs_acceptance.py` and `leg_mismatch.py` each
hardcode `pet/fullevent_nominal/…_weights.npz`, the 2026-08-08 pre-anneal artifact, and each already
carries a `_assert_artifact_identity` that refuses to run unless the loaded artifact's own
fold-forward ratio matches `0.7367462501305516`. **Those guards were added 2026-08-12 and are correct
in design — this file is not a fix for a missing guard.** Measured 2026-08-14: **no test anywhere
referenced `_assert_artifact_identity` or `EXPECTED_FOLD_FORWARD`.** A guard nobody has watched fire
is the `assert_no_truth_leakage` shape one step removed: not provably inert, merely unobserved. So
this battery observes it.

WHY IT MATTERS THAT THE PATH IS HARDCODED AND THE GUARD IS NOT COSMETIC. Promotion in this campaign is
by DESIGNATION and moves no bytes (`check_canonical_designation.py`), so `fullevent_nominal/` is no
longer a claim about which estimator is there. `56563761` was designated canonical 2026-08-13
(`6b68d12`) and these three were deliberately dispositioned `STAYS-DIAG08`: retargeting them would
change what the diagnostic measures while its name stayed the same. **The path is therefore load-
bearing in the wrong direction, and the fold-forward assertion is the only thing standing between
"reads the 08-08 artifact" and "reads whatever is at that path."**

AXES.
  1. THE GUARD ACCEPTS THE RIGHT ARTIFACT — a positive control, so "refuses everything" cannot pass.
  2. THE GUARD REFUSES EACH KNOWN WRONG ARTIFACT BY ITS REAL FINGERPRINT: the 08-06 superseded arm and
     the 08-10 annealed arm — the one that is now canonical, i.e. the live confusion.
  3. THE TOLERANCE BOUNDARY, both sides. `tol=1e-9` is asserted to actually bind, so a later widening
     is a test failure and not a silent change of what "identity" means.
  4. A MALFORMED ARTIFACT MUST REFUSE, NOT TRACEBACK. An npz lacking the two fold-forward fields is
     exactly the case a schema change produces — lane C measured 2026-08-14 that the pre-anneal and
     annealed artifacts differ by SCHEMA, not merely by field value. `KeyError` from inside a guard
     reads as a broken diagnostic; this is a predeclared condition and must read as one.
  5. THE THREE COPIES DO NOT DRIFT. One constant, three files, no shared module: a legitimate retarget
     of one silently disagrees with the other two.

STATED GAPS at the foot of the file.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
PET = REPO / "nd-unfolding/pet"
MODULES = ("inversion_screen", "push_vs_acceptance", "leg_mismatch")

# Two of the three do `sys.path.insert` then `import fullevent_fps_dataloader` at module scope, so
# importing them from outside `pet/` is a ModuleNotFoundError rather than a finding. Put the directory
# on the path once, here, rather than papering over the failure with a skip.
if str(PET) not in sys.path:
    sys.path.insert(0, str(PET))

# Measured fold-forward ratios of the three real artifacts, transcribed from the guards' own reference
# table and cross-checked against the committed receipts. NOT recomputed here -- the artifacts are on
# /pscratch and this suite runs locally, which is precisely why the guard reads the value from the
# artifact at runtime instead of trusting a path.
FF_08_08_CANONICAL_AT_THE_TIME = 0.7367462501305516
FF_08_06_SUPERSEDED = 0.7464834064182863
# The annealed arm, now canonical by designation. CORRECTED 2026-08-17 with OI-82's resolution: this
# was 1.0840529829474115, taken from the guards' own comment, which did not match either committed
# measurement. It was never a measurement -- it is the numerator over a ROUNDED denominator. See the
# resolved note at the foot of the file. Used here only as "some wrong artifact" relative to the 08-08
# value the guards require, and the corrected value serves that purpose identically.
FF_08_10_ANNEALED = 1.0840529523112135
# Retained under its own name so a reader meeting the old number anywhere can identify it rather than
# treat it as a fourth measurement. NOT a candidate for any guard's expected value.
FF_08_10_ANNEALED_ARITHMETIC_SLIP = 1.0840529829474115


def _load(name):
    path = REPO / "nd-unfolding/pet" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"_pet_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _artifact(ff_ratio, denom=2.0):
    """A minimal stand-in carrying only what the guard reads. `dict` is deliberate: the guard's
    contract is two `__getitem__` lookups, and using a real npz would test numpy, not the guard."""
    return {"fold_forward_sum_w_reco": denom,
            "fold_forward_sum_w_push_reco": ff_ratio * denom}


@pytest.mark.parametrize("name", MODULES)
def test_guard_accepts_the_08_08_artifact_it_is_about(name):
    """Positive control. Without it, axes 2-4 are satisfied by a guard that refuses everything."""
    mod = _load(name)
    got = mod._assert_artifact_identity(_artifact(FF_08_08_CANONICAL_AT_THE_TIME))
    assert got == pytest.approx(FF_08_08_CANONICAL_AT_THE_TIME, abs=1e-12)


@pytest.mark.parametrize("name", MODULES)
@pytest.mark.parametrize("ff,label", [
    (FF_08_06_SUPERSEDED, "08-06 superseded"),
    (FF_08_10_ANNEALED, "08-10 annealed, canonical by designation"),
    (FF_08_10_ANNEALED_ARITHMETIC_SLIP, "OI-82's old comment value; must also be refused"),
])
def test_guard_refuses_each_known_wrong_artifact(name, ff, label):
    """The live confusion is the annealed one: it IS the canonical nominal, so a future lane
    'helpfully' retargeting `fullevent_nominal/` is the failure this guard exists for."""
    mod = _load(name)
    with pytest.raises(SystemExit) as exc:
        mod._assert_artifact_identity(_artifact(ff))
    msg = str(exc.value)
    assert "REFUSING TO RUN" in msg, f"{name} refused {label} without saying so: {msg}"
    assert repr(ff) in msg or f"{ff!r}" in msg, (
        f"{name}'s refusal must print the value it SAW, or the operator cannot tell which artifact "
        f"they have: {msg}")


@pytest.mark.parametrize("name", MODULES)
def test_the_tolerance_binds_on_both_sides(name):
    """`tol=1e-9` must be a real threshold. A guard whose tolerance is wide enough to admit a
    different artifact is an existence check wearing an identity check's name."""
    mod = _load(name)
    assert mod._assert_artifact_identity(
        _artifact(FF_08_08_CANONICAL_AT_THE_TIME + 5e-10)) == pytest.approx(
            FF_08_08_CANONICAL_AT_THE_TIME, abs=1e-8)
    with pytest.raises(SystemExit):
        mod._assert_artifact_identity(_artifact(FF_08_08_CANONICAL_AT_THE_TIME + 2e-9))


@pytest.mark.parametrize("name", MODULES)
def test_a_malformed_artifact_refuses_rather_than_tracebacks(name):
    """An artifact lacking the two fold-forward fields is what a schema change looks like, and lane C
    measured 2026-08-14 that the pre-anneal and annealed artifacts differ by SCHEMA. A guard that
    raises `KeyError` reports itself as broken instead of reporting the artifact as wrong."""
    mod = _load(name)
    with pytest.raises(SystemExit) as exc:
        mod._assert_artifact_identity({"weights_push": [1.0]})
    assert "REFUSING TO RUN" in str(exc.value)
    # And the half-malformed case: the numerator present, the denominator absent.
    with pytest.raises(SystemExit):
        mod._assert_artifact_identity({"fold_forward_sum_w_push_reco": 1.0})


@pytest.mark.parametrize("name", MODULES)
def test_a_zero_denominator_refuses_rather_than_dividing_by_zero(name):
    """An artifact whose `sum_w_reco` is zero has no fold-forward ratio at all. `ZeroDivisionError`
    is the same defect as `KeyError`: the guard reporting itself broken instead of the artifact."""
    mod = _load(name)
    with pytest.raises(SystemExit) as exc:
        mod._assert_artifact_identity(_artifact(1.0, denom=0.0))
    assert "REFUSING TO RUN" in str(exc.value)


@pytest.mark.parametrize("name", MODULES)
def test_the_expected_constant_has_not_drifted_between_the_three_copies(name):
    """One constant, three files, no shared module. A legitimate retarget of one copy leaves the other
    two asserting a different artifact, and nothing else would notice."""
    assert _load(name).EXPECTED_FOLD_FORWARD == FF_08_08_CANONICAL_AT_THE_TIME


# --- STATED GAPS ---------------------------------------------------------------------------------
# 1. ~~THE GUARDS' ANNEALED REFERENCE VALUE DISAGREES WITH BOTH COMMITTED MEASUREMENTS OF IT~~
#    **RESOLVED 2026-08-17 (lane E, OI-82), AND IT WAS NEVER A THIRD MEASUREMENT.** The gap was:
#        guards' comment        1.0840529829474115
#        production 56563761    1.0840529523112135   (annealed-nominal-complete receipt)
#        trajectory 56818470    1.0840529523260116   (step-1 decomposition harness)
#    Closed by the method this item prescribed -- a login-node read of the annealed NPZ's own stored
#    fields (sha256 559a1020570929169a83e26dd9eea937bb34d6f4ecb230e332b792165ef6eb3e):
#        fold_forward_sum_w_push_reco = 1084052.9829474115
#        fold_forward_sum_w_reco      = 1000000.0282607947
#        num / den                    = 1.0840529523112135   == production, BIT-IDENTICAL
#        num / 1e6                    = 1.0840529829474115   == the old comment, BIT-IDENTICAL
#    So the third value is the NUMERATOR OVER A ROUNDED DENOMINATOR. 1e6 against 1000000.0282607947
#    is 2.826e-8 relative, which reproduces the observed 3.064e-8 gap to the last digit. The guards'
#    comments now carry the correct value; the slip is retained above under its own name so a reader
#    meeting it elsewhere can identify it instead of filing a fourth value. `BEN-244`, `OI-82`.
#    NOT re-derived here: the production and trajectory numbers, which are quoted from their receipts.
# 2. NOT COVERED: that the artifact at ART is actually the 08-08 one. Nothing local can check that --
#    it is the runtime assertion's whole job, and this battery verifies the assertion, not the tree.
# 3. NOT COVERED: class 5 proper. `inference_contract.step2_checkpoint` is an ABSOLUTE path written at
#    training time (BEN-133), so a swapped artifact resolves to a different network. These three
#    diagnostics read stored arrays only and never load a checkpoint, so they do not exercise it.
# 4. `dict` stands in for an npz. If a guard ever reads a field only a real npz provides (dtype,
#    shape, `.files`), this stand-in stops being faithful -- which is why axis 4 exists.
