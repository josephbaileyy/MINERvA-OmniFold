"""Regression: the OI-120(c) probe's VERDICT must not be produced by a sentinel collision.

WHAT WENT WRONG, AND WHY A TEST HERE RATHER THAN A CAREFUL READ. Job 56975592 COMPLETED exit 0 and
printed `VERDICT: "LEAKAGE -- event_reco changed when only a truth array changed"` while its own four
truth arms said the opposite: P1/P2/P3 left `event_reco` BIT-IDENTICAL under real truth perturbations,
against a P0 control that fired. Only P4 failed, and it failed by NOT PERTURBING (`proxy_hits: 0`) --
i.e. it did not run.

The cause is one token. `probe-...-perturbation-20260814.py` scores arms with a THREE-VALUED flag:

    as_predeclared = True   arm ran and matched its predeclaration
                     False  arm ran and CONTRADICTED it        <- the only thing that means leakage
                     None   arm did not run; EXCLUDE from scoring

and the scoring filter is `[v for v in truth_arms if v["as_predeclared"] is not None]`. A VOID arm --
a perturbation that did not perturb -- was assigned `False`, the value reserved for "contradicted".
`False is not None`, so the void arm entered the scored set, forced `clean` False, and dropped the
verdict into the `LEAKAGE` else-branch. The file's own docstring (:41-44) states the intended
semantics -- *"a perturbation that did not perturb turns 'no leakage' into 'no test'"* -- so VOID must
be excluded exactly like REFUSED. `ok = None`, not `ok = False`.

WHY THESE FOUR TESTS AND NOT ONE. A test that only asserts "VOID does not produce LEAKAGE" is
satisfied by deleting the LEAKAGE branch. So the suite pins both directions: a void arm must NOT
produce LEAKAGE, and a genuinely CHANGED truth arm MUST still produce it. The second test is GREEN
both before and after the fix by design -- it is there to prove the fix did not disarm the detector.

The arms are not hand-written. `recorded_arms()` parses them out of the PRESERVED STDOUT of job
56975592 (`state/oi120c-loader-purity-perturbation-56975592.txt`), so test 1 is a replay of the real
run rather than a re-enactment of it. Synthetic arms are derived from those by mutation.

Run: `python3 -m pytest docs/orchestration/test_probe_oi120c_verdict.py -v`
"""
import importlib.util
import io
import json
import contextlib
import os
import re
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
PROBE = HERE / "state" / "probe-oi120c-loader-purity-perturbation-20260814.py"
RECEIPT = HERE / "state" / "oi120c-loader-purity-perturbation-56975592.txt"

TRUTH_ARMS = ("P1", "P2", "P3", "P4")


def load_probe(name="probe_oi120c_under_test"):
    """Import the probe module by path.

    Importing is safe and does not touch the cluster: the module's top level only imports numpy and
    inserts two `/pscratch` paths into `sys.path` (absent locally, and an absent sys.path entry is
    inert). `fullevent_fps_dataloader` is imported INSIDE `run_pass`, which every test replaces.
    """
    assert PROBE.is_file(), f"probe not found: {PROBE}"
    os.environ.pop("LEGC_MAX_EVENTS", None)          # else the module declares itself a SMOKE TEST
    spec = importlib.util.spec_from_file_location(name, PROBE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def recorded_arms():
    """(baseline_detail, {arm_id: detail}) as job 56975592 actually recorded them."""
    assert RECEIPT.is_file(), f"preserved stdout not found: {RECEIPT}"
    text = RECEIPT.read_text(encoding="utf-8")
    _, _, blob = text.partition("<<<RECEIPT_JSON>>>")
    receipt = json.loads(blob)
    return receipt["baseline"], {k: v["detail"] for k, v in receipt["arms"].items()}


def run_main(mod, baseline, details):
    """Drive the probe's real scoring/verdict code with pre-recorded pass results.

    Substituting `run_pass` is what makes this runnable off-cluster: everything downstream of it --
    the `really_changed` assertion, the three-valued scoring, the filter, and the verdict ladder --
    is the production code path under test, unmodified.
    """
    def fake_run_pass(label, perturb):
        aid = label.split()[0]
        return dict(baseline if aid == "BASE" else details[aid])

    real = mod.run_pass
    mod.run_pass = fake_run_pass
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            mod.main()
    finally:
        mod.run_pass = real
    out = buf.getvalue()
    _, _, blob = out.partition("<<<RECEIPT_JSON>>>")
    return out, json.loads(blob)


def void(detail):
    """A pass whose perturbation did not perturb: loader ran, proxy substituted nothing."""
    d = dict(detail)
    d["arrays_actually_changed"] = {}
    d["proxy_hits"] = 0
    return d


@pytest.fixture
def probe():
    return load_probe()


def test_recorded_arms_replay_to_no_leakage(probe):
    """THE REPLAY. Job 56975592's own arms must not yield LEAKAGE.

    RED before the fix: this printed `LEAKAGE -- event_reco changed when only a truth array changed`,
    which is what the job reported.
    """
    baseline, details = recorded_arms()
    out, receipt = run_main(probe, baseline, details)

    assert receipt["p0_control_fired"] is True, "the control must have fired or nothing is scorable"
    assert receipt["VERDICT"].startswith("NO TRUTH LEAKAGE DEMONSTRATED on 3 of 4 truth perturbations")
    assert "LEAKAGE --" not in receipt["VERDICT"], f"still alarming: {receipt['VERDICT']}"
    # the headline and the arms must agree -- disagreement between them is the whole defect
    assert receipt["arms"]["P4"]["observed"].startswith("VOID")
    assert receipt["arms"]["P4"]["as_predeclared"] is None, (
        "a VOID arm must carry the EXCLUDE sentinel (None), not the CONTRADICTED value (False)")
    for aid in ("P1", "P2", "P3"):
        assert receipt["arms"][aid]["observed"] == "IDENTICAL"
        assert receipt["arms"][aid]["as_predeclared"] is True
    assert re.search(r"=== NO TRUTH LEAKAGE DEMONSTRATED on 3 of 4 ", out), "stdout headline disagrees"


def test_void_arm_does_not_produce_leakage(probe):
    """A void arm among otherwise-clean arms is a MISSING TEST, not a positive detection.

    Synthetic and stricter than the replay: three clean arms, one void, nothing else wrong.
    RED before the fix.
    """
    baseline, details = recorded_arms()
    details = dict(details)
    details["P4"] = void(details["P4"])
    _, receipt = run_main(probe, baseline, details)

    assert "LEAKAGE --" not in receipt["VERDICT"], f"void arm manufactured a positive: {receipt['VERDICT']}"
    assert receipt["VERDICT"].startswith("NO TRUTH LEAKAGE DEMONSTRATED on 3 of 4")


def test_genuine_truth_change_still_produces_leakage(probe):
    """THE OTHER DIRECTION. A truth arm that really did change `event_reco` MUST still say LEAKAGE.

    GREEN before AND after the fix, deliberately: it is the guard that the fix narrowed the sentinel
    rather than removing the detector. A suite without it is passed by deleting the LEAKAGE branch.
    """
    baseline, details = recorded_arms()
    details = dict(details)
    leaked = dict(details["P1"])
    leaked["sha256"] = "0" * 64                      # != baseline -> event_reco moved
    details["P1"] = leaked
    _, receipt = run_main(probe, baseline, details)

    assert receipt["VERDICT"] == "LEAKAGE -- event_reco changed when only a truth array changed"
    assert receipt["arms"]["P1"]["observed"] == "CHANGED"
    assert receipt["arms"]["P1"]["as_predeclared"] is False, "a CONTRADICTED arm is the False case"


def test_leakage_survives_alongside_a_void_arm(probe):
    """A void arm must not MASK a real detection either -- the fix must not swallow the positive."""
    baseline, details = recorded_arms()
    details = dict(details)
    leaked = dict(details["P1"])
    leaked["sha256"] = "0" * 64
    details["P1"] = leaked
    details["P4"] = void(details["P4"])
    _, receipt = run_main(probe, baseline, details)

    assert receipt["VERDICT"] == "LEAKAGE -- event_reco changed when only a truth array changed"


def test_all_truth_arms_void_is_unresolved_not_leakage(probe):
    """Nothing tested is UNRESOLVED, never a verdict about leakage in either direction.

    RED before the fix (it read LEAKAGE off four arms that never ran). NB the branch it now lands in
    is worded "the loader refused every truth perturbation"; VOID is not REFUSED, and that wording
    imprecision is recorded in OI-124 rather than patched here -- this repair is one token.
    """
    baseline, details = recorded_arms()
    details = {aid: void(details[aid]) for aid in TRUTH_ARMS} | {"P0": details["P0"]}
    _, receipt = run_main(probe, baseline, details)

    assert receipt["VERDICT"].startswith("UNRESOLVED"), receipt["VERDICT"]
    assert "LEAKAGE --" not in receipt["VERDICT"]
    for aid in TRUTH_ARMS:
        assert receipt["arms"][aid]["as_predeclared"] is None


def test_dead_control_is_unresolved(probe):
    """Pre-existing guard, pinned so this repair cannot regress it: no control, no meaning.

    GREEN before and after.
    """
    baseline, details = recorded_arms()
    details = dict(details)
    dead = dict(details["P0"])
    dead["sha256"] = baseline["sha256"]              # control did NOT move event_reco
    details["P0"] = dead
    _, receipt = run_main(probe, baseline, details)

    assert receipt["p0_control_fired"] is False
    assert receipt["VERDICT"].startswith("UNRESOLVED -- the P0 control did not fire")
