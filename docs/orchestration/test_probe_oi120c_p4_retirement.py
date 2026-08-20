"""OI-124 disposition (a): P4 is RETIRED, and the two BEN-290 vocabulary residues are closed.

THREE CHANGES TO THE PROBE, PINNED HERE. Written before the edit and observed RED against the probe
as it stood at `143f859`.

1. **P4 retired.** `w_truth` x1.05 could not fail where it ran -- `event_reco` is finished before the
   loader reads `w_truth` -- so the arm sampled nothing. It is replaced by a proof, kept executable in
   `test_loader_ordering_reco_before_truth_weight.py`. Retirement must be VISIBLE IN THE CODE: an arm
   left in the list and reported VOID reads as "we tried and it did not work", which invites making it
   perturb harder, and at that capture point there is nothing to perturb harder AT.

2. **Residue: the all-void branch said REFUSED.** VOID and REFUSED are different outcomes -- a
   perturbation that did not change the array versus a loader that rejected the input -- and the branch
   asserted the second while reachable from the first. The conclusion (UNRESOLVED) was right and its
   stated reason could be wrong, which is the worse defect of the two: a right answer with a wrong
   reason survives review.

3. **Residue: the per-arm print labelled a void arm REFUSED** while its own `observed` column read
   VOID. Two columns of one line disagreeing in vocabulary.

WHAT MUST NOT MOVE, and is asserted here rather than assumed: retiring an arm changes the DENOMINATOR
and nothing else. Job 56975592's three real truth perturbations still left `event_reco` bit-identical
against a control that fired. `test_science_of_56975592_survives_retirement` pins exactly that, so a
future reader can see the negative result is the same result under a different count.

THE VERDICT STRING CHANGES, deliberately and with a cost. At `143f859` the replay read
`NO TRUTH LEAKAGE DEMONSTRATED on 3 of 4 truth perturbations`; that string is quoted in BEN-290 and in
`FINDING-20260814-a-sentinel-that-collided-with-a-result.md`, and it is TRUE OF THAT COMMIT -- neither
is edited. After retirement the same recorded arms read `... on 3 of 3 live truth perturbations`. Same
three arms, same hashes, same control; the retired arm is no longer counted in a denominator it never
contributed to. Both strings are pinned below so the pair is greppable from either direction.

Run: `python3 -m pytest docs/orchestration/test_probe_oi120c_p4_retirement.py -v`
"""
import pytest

from test_probe_oi120c_verdict import load_probe, recorded_arms, run_main, void

HISTORICAL_VERDICT_AT_143f859 = "NO TRUTH LEAKAGE DEMONSTRATED on 3 of 4 truth perturbations"
LIVE_TRUTH_ARMS = ("P1", "P2", "P3")


@pytest.fixture
def probe():
    return load_probe("probe_oi120c_retirement_under_test")


def arm_ids(mod):
    return [a[0] for a in mod.ARMS]


# --------------------------------------------------------------------------------------------
# 1. RETIREMENT
# --------------------------------------------------------------------------------------------

def test_p4_is_not_a_live_arm(probe):
    """RED before: `P4` was in ARMS and would be executed by any re-run."""
    assert "P4" not in arm_ids(probe), "P4 still executes; it cannot fail where it runs"
    assert arm_ids(probe) == ["P0", *LIVE_TRUTH_ARMS], arm_ids(probe)


def test_p4_is_recorded_as_retired_with_its_reason(probe):
    """Retired, not deleted. A silently vanished arm is indistinguishable from one nobody wrote."""
    retired = {a[0]: a for a in probe.RETIRED_ARMS}
    assert "P4" in retired, "P4 was removed without being recorded as retired"
    reason = " ".join(str(x) for x in retired["P4"]).lower()
    for token in ("oi-124", "w_truth", "event_reco"):
        assert token in reason, f"retirement reason does not mention {token!r}: {reason}"


def test_receipt_publishes_the_retirement(probe):
    """A receipt that silently drops an arm cannot be checked against the run that had it (BEN-077)."""
    baseline, details = recorded_arms()
    _, receipt = run_main(probe, baseline, details)
    assert "retired_arms" in receipt, "the receipt does not disclose that an arm was retired"
    assert "P4" in receipt["retired_arms"]
    blob = str(receipt["retired_arms"]).lower()
    assert "oi-124" in blob
    assert "test_loader_ordering_reco_before_truth_weight" in blob, (
        "the retirement must point at the check that replaced the arm, or the proof is unlocatable")


def test_verdict_counts_only_live_arms(probe):
    """RED before: read `3 of 4`, counting an arm that could not be scored even in principle."""
    baseline, details = recorded_arms()
    out, receipt = run_main(probe, baseline, details)
    assert receipt["VERDICT"].startswith(
        "NO TRUTH LEAKAGE DEMONSTRATED on 3 of 3 live truth perturbations"), receipt["VERDICT"]
    assert "3 of 4" not in receipt["VERDICT"]
    assert "=== NO TRUTH LEAKAGE DEMONSTRATED on 3 of 3 live" in out, "stdout headline disagrees"


def test_science_of_56975592_survives_retirement(probe):
    """THE INVARIANT. Retirement changes the denominator; it must change nothing else.

    Three real truth perturbations, each confirmed to have landed, each leaving `event_reco`
    bit-identical to baseline, against a control that moved it. That is the result, before and after.
    """
    baseline, details = recorded_arms()
    _, receipt = run_main(probe, baseline, details)

    assert receipt["p0_control_fired"] is True
    assert "LEAKAGE --" not in receipt["VERDICT"]
    for aid in LIVE_TRUTH_ARMS:
        arm = receipt["arms"][aid]
        assert arm["observed"] == "IDENTICAL", aid
        assert arm["as_predeclared"] is True, aid
        assert arm["detail"]["sha256"] == baseline["sha256"], f"{aid} is not bit-identical"
        assert all(arm["detail"]["arrays_actually_changed"].values()), (
            f"{aid} did not actually perturb -- it is not evidence of anything")
    assert HISTORICAL_VERDICT_AT_143f859.startswith("NO TRUTH LEAKAGE DEMONSTRATED on 3 of 4"), (
        "the pre-retirement string is pinned so citations of it stay resolvable")


def test_retirement_did_not_disarm_the_detector(probe):
    """A live truth arm that really moved `event_reco` must STILL produce LEAKAGE.

    Retiring an arm is one edit away from narrowing the scored set to nothing. This is the same guard
    `test_genuine_truth_change_still_produces_leakage` makes, re-asserted on the post-retirement arm
    set, because that is the set a future run will use.
    """
    baseline, details = recorded_arms()
    details = dict(details)
    details["P1"] = dict(details["P1"], sha256="0" * 64)
    _, receipt = run_main(probe, baseline, details)
    assert receipt["VERDICT"] == "LEAKAGE -- event_reco changed when only a truth array changed"
    assert receipt["arms"]["P1"]["as_predeclared"] is False


# --------------------------------------------------------------------------------------------
# 2 + 3. VOCABULARY RESIDUES
# --------------------------------------------------------------------------------------------

def test_all_void_branch_does_not_call_it_refused(probe):
    """RED before: `UNRESOLVED -- the loader refused every truth perturbation`, on arms it did not refuse.

    The distinction is not pedantic. REFUSED means a fail-closed guard rejected the perturbed input --
    a real, informative outcome about the loader. VOID means the perturbation never changed the array,
    which is a fact about the PROBE. Reporting the second as the first sends a reader to look for a
    guard that does not exist.
    """
    baseline, details = recorded_arms()
    details = {aid: void(details[aid]) for aid in LIVE_TRUTH_ARMS} | {"P0": details["P0"]}
    _, receipt = run_main(probe, baseline, details)

    v = receipt["VERDICT"]
    assert v.startswith("UNRESOLVED"), v
    assert "LEAKAGE --" not in v
    assert "refused every" not in v.lower(), f"VOID is still reported as REFUSED: {v}"
    assert "void" in v.lower(), f"the verdict does not say what actually happened: {v}"


def test_all_void_branch_ships_its_counts(probe):
    """The reason must be derivable from operands, not asserted (BEN-077)."""
    baseline, details = recorded_arms()
    details = {aid: void(details[aid]) for aid in LIVE_TRUTH_ARMS} | {"P0": details["P0"]}
    _, receipt = run_main(probe, baseline, details)
    v = receipt["VERDICT"]
    assert "3 VOID" in v, f"the verdict does not count the void arms: {v}"
    assert "0 REFUSED" in v, f"the verdict does not count the refused arms: {v}"


def test_a_refused_arm_is_still_called_refused(probe):
    """The other direction: narrowing REFUSED's wording must not delete REFUSED.

    A genuinely refused arm -- the loader raised on the perturbed input -- must still read REFUSED in
    both columns. Without this, the residue fix is passed by renaming everything VOID.
    """
    baseline, details = recorded_arms()
    details = dict(details)
    details["P1"] = {"ok": False, "refused": "ValueError: [B1] non-finite w_truth / w_bkg (fail closed)",
                     "proxy_hits": 1, "arrays_actually_changed": {"truth_scalars": True}}
    out, receipt = run_main(probe, baseline, details)

    assert receipt["arms"]["P1"]["observed"] == "REFUSED"
    assert receipt["arms"]["P1"]["as_predeclared"] is None
    line = next(l for l in out.splitlines() if l.strip().startswith("[P1]"))
    assert "REFUSED" in line, line
    assert receipt["VERDICT"].startswith("NO TRUTH LEAKAGE DEMONSTRATED on 2 of 3 live"), (
        receipt["VERDICT"])


def test_per_arm_print_agrees_with_the_observed_column(probe):
    """RED before: a VOID arm printed `observed=VOID ...` and was labelled `REFUSED` on the same line."""
    baseline, details = recorded_arms()
    details = dict(details)
    details["P3"] = void(details["P3"])
    out, receipt = run_main(probe, baseline, details)

    line = next(l for l in out.splitlines() if l.strip().startswith("[P3]"))
    assert "VOID" in line, line
    assert "REFUSED" not in line, f"a void arm is still labelled REFUSED: {line}"
    assert "NOT SCORED" in line, f"a void arm must be visibly excluded from scoring: {line}"
    assert receipt["arms"]["P3"]["as_predeclared"] is None
    assert receipt["VERDICT"].startswith("NO TRUTH LEAKAGE DEMONSTRATED on 2 of 3 live")


def test_scored_arms_keep_their_labels(probe):
    """The label change must not touch the two labels that were already right."""
    baseline, details = recorded_arms()
    details = dict(details)
    details["P2"] = dict(details["P2"], sha256="0" * 64)          # contradicts its predeclaration
    out, _ = run_main(probe, baseline, details)

    ok_line = next(l for l in out.splitlines() if l.strip().startswith("[P1]"))
    bad_line = next(l for l in out.splitlines() if l.strip().startswith("[P2]"))
    assert "as predeclared" in ok_line, ok_line
    assert "*** NO ***" in bad_line, bad_line
