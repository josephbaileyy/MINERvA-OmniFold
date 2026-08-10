#!/usr/bin/env python3
"""ADVERSARIAL CASES for Packet B item B1 -- `C_syst` band-set completeness.

BUILT BY THE PET LANE AT JOSEPH'S REQUEST (2026-08-10), deliberately NOT by the author of the fix. The
reason is BEN-040 and repair-7's self-guard: an author's negative case tends to match their fix rather
than the defect, so three of six new defects in repair-7 were in guards written that session. This file
is the case only. **It does not implement the check.**

WHAT IT ASSERTS. Every case below is one that the CURRENT code accepts -- so each test asserts the
DEFECT is real (the omission is invisible to the reconstruction identity, and the systematic budget is
under-counted). When B1's check lands, `must_be_rejected_by_B1` marks exactly which cases have to flip
to FAIL. A case that the current code already rejects would be worthless as an acceptance test, so each
one is checked to pass today.

------------------------------------------------------------------------------------------------------
THE DEFECT, located precisely (p4_validate_active_lateral.py, as of 2026-08-10)

    :187  retained_keys = [k for k in comp.get("candidate_keys", []) if k.startswith("hCov_retained5d_")]
    :193  for k in retained_keys: P.require(blk is not None, "candidate is missing declared component")
    :199  P.prove_identity(Csyst, retained_sum + active_total_blk, 1e-9, "C_syst == sum(retained) + active")
    :201  out["n_retained_components"] = len(retained_keys)

Four independent reasons the omission survives:

  1. `retained_keys` comes from the manifest's OWN `candidate_keys`. The identity at :199 then compares
     `C_syst` against a sum built from that same list -- both sides derive from the declaration, so the
     declaration cannot be wrong by this test.
  2. :193 is ONE-DIRECTIONAL. It checks declared -> exists. It never checks exists -> declared, which is
     the direction an omission travels.
  3. `n_retained_components` at :201 is RECORDED and never compared to anything.
  4. `P.require_exact_bands` exists (p4_lib:874) but guards the 5 ACTIVE lateral bands, not the retained
     set. There is no equivalent for the ~40.

And the band universe itself is DISCOVERED, not declared: `all_bands = _band_keys(a.support_family)`
lists `hCov_universe5d_*` keys out of the support ROOT (p4_build_components.py:53-58,103). So nothing
anywhere in the chain states how many retained bands there are supposed to be.

------------------------------------------------------------------------------------------------------
THREE LEVELS, AND LEVEL 2 IS THE ONE THAT DISCRIMINATES A REAL FIX FROM A PLAUSIBLE ONE

The manifest also records `all_syst_bands` and `retained_bands` (p4_build_components.py:151), which the
validator never reads. That makes a cross-field check the NATURAL fix -- and it is not sufficient:

  LEVEL 1  declaration-only omission.  Dropped from `candidate_keys`; still listed in `retained_bands`;
           block still present in the candidate file. The manifest CONTRADICTS ITSELF and the validator
           passes anyway. Caught by a cross-field check.

  LEVEL 2  self-consistent omission.   Dropped from `candidate_keys` AND `retained_bands` AND
           `all_syst_bands`, with `C_syst` rebuilt as the sum of what remains. The manifest is now
           perfectly self-consistent. A cross-field check passes it. **Only an inventory declared
           OUTSIDE the manifest rejects this**, which is exactly what B1's acceptance criterion says
           ("against a declared required inventory, not against the manifest's own list") -- this case
           demonstrates why that wording is load-bearing rather than stylistic.

  LEVEL 3  source omission.            The band is absent from the support-family ROOT, so `_band_keys`
           never discovers it and the builder never knew it existed. Every artifact downstream is
           consistent. Out of B1's stated scope, and noted because a REQUIRED INVENTORY IN CODE closes
           it for free while a manifest cross-check cannot touch it. If the inventory is declared in
           `p4_lib`, Level 3 costs nothing extra; if it is derived from the support file, Level 3 stays
           open.

------------------------------------------------------------------------------------------------------
WHY THE OMITTED BAND IS THE SMALLEST ONE

Each case drops the band with the smallest trace. That is the adversarial choice on purpose: it moves
`sqrt(trace(C_syst))` -- the number that gets quoted -- by the least, so any "does the total look about
right" heuristic is defeated. A check that only rejects large omissions would pass these and still
certify an under-counted budget. The under-count is asserted to be real but small.
"""
import os
import sys
import unittest

import numpy as np

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ND not in sys.path:
    sys.path.insert(0, ND)

RTOL = 1e-9                      # p4_validate_active_lateral.py:199's identity tolerance
N = 6                            # tiny grid; the arithmetic under test is dimension-independent

# The 5 active laterals, from p4_lib.BANDS. Retained = everything else.
ACTIVE = ("BeamAngleX", "BeamAngleY", "MuonResolution",
          "Muon_Energy_MINERvA", "Muon_Energy_MINOS")
# A stand-in retained universe. Names are illustrative; the case turns on set ALGEBRA, not on the
# specific labels, and the real run has ~40.
RETAINED = tuple(f"Syst_{i:02d}" for i in range(40))


def _psd(seed, scale):
    """A symmetric positive-definite block, like a per-band covariance."""
    rng = np.random.default_rng(seed)
    A = rng.normal(size=(N, N))
    return scale * (A @ A.T + N * np.eye(N))


def build_truth():
    """The COMPLETE, correct component set: 40 retained + 5 active, and the C_syst they imply."""
    retained = {b: _psd(1000 + i, 1e-3 if i else 1e-6) for i, b in enumerate(RETAINED)}
    #                                        ^ band Syst_00 is deliberately the SMALLEST (1e-6)
    active = {b: _psd(2000 + i, 1e-3) for i, b in enumerate(ACTIVE)}
    active_total = sum(active.values())
    c_syst = sum(retained.values()) + active_total
    return retained, active, active_total, c_syst


def smallest_band(retained):
    return min(retained, key=lambda b: float(np.trace(retained[b])))


def manifest(retained_declared, all_syst, retained_bands):
    """The shape the validator actually reads: candidate_keys, plus two fields it never reads."""
    return {"candidate_keys": [f"hCov_retained5d_{b}" for b in retained_declared]
                              + ["hCov_active5d_total"],
            "all_syst_bands": list(all_syst),
            "retained_bands": list(retained_bands)}


def current_identity_relerr(c_syst, man, retained_blocks, active_total):
    """EXACTLY what p4_validate_active_lateral.py:187-199 does, transcribed.

    retained_keys from the manifest's own candidate_keys; sum those blocks; compare to C_syst.
    """
    keys = [k for k in man["candidate_keys"] if k.startswith("hCov_retained5d_")]
    assert keys, "pre-repair-4 candidate; not the case under test"
    s = None
    for k in keys:
        b = k[len("hCov_retained5d_"):]
        blk = retained_blocks.get(b)
        # :193 -- declared must EXIST. One-directional, and every case here satisfies it.
        assert blk is not None, f"declared component {k} absent from the candidate"
        s = blk if s is None else s + blk
    recon = s + active_total
    denom = float(np.max(np.abs(c_syst))) or 1.0
    return float(np.max(np.abs(c_syst - recon)) / denom), len(keys)


def quoted_scale(C):
    """sqrt(trace) -- the systematic budget as it would be quoted."""
    return float(np.sqrt(np.trace(C)))


class CompleteSetMustStillPass(unittest.TestCase):
    """The other direction of B1's acceptance: the real 40-band set must PASS after the fix."""

    must_be_rejected_by_B1 = False       # CLASS attribute: the contract test reads it off the class

    def test_complete_set_reconstructs_and_is_the_full_budget(self):
        retained, _active, active_total, c_syst = build_truth()
        man = manifest(RETAINED, RETAINED + ACTIVE, RETAINED)
        relerr, n = current_identity_relerr(c_syst, man, retained, active_total)
        self.assertLessEqual(relerr, RTOL)
        self.assertEqual(n, 40, "the complete case must declare all 40 retained components")


class Level1DeclarationOnlyOmission(unittest.TestCase):
    """Dropped from `candidate_keys` only. The manifest CONTRADICTS ITSELF and still passes.

    must_be_rejected_by_B1 = True. A cross-field check (candidate_keys vs retained_bands) catches this
    one, which is why it is NOT sufficient as the whole acceptance test -- see Level 2.
    """

    must_be_rejected_by_B1 = True

    def test_omission_is_invisible_to_the_current_identity(self):
        retained, _a, active_total, _c = build_truth()
        drop = smallest_band(retained)
        kept = [b for b in RETAINED if b != drop]
        # C_syst as the CANDIDATE would carry it if built from the reduced set
        c_syst_short = sum(retained[b] for b in kept) + active_total
        # ...while the manifest still LISTS the dropped band in retained_bands / all_syst_bands
        man = manifest(kept, RETAINED + ACTIVE, RETAINED)
        relerr, n = current_identity_relerr(c_syst_short, man, retained, active_total)
        self.assertLessEqual(relerr, RTOL,
                             "the reconstruction identity must PASS -- that is the defect")
        self.assertEqual(n, 39)
        # the self-contradiction is present in the manifest and unread
        self.assertEqual(len(man["retained_bands"]), 40)
        self.assertEqual(len([k for k in man["candidate_keys"]
                              if k.startswith("hCov_retained5d_")]), 39)

    def test_the_manifest_contradicts_itself_and_nothing_reads_it(self):
        drop = "Syst_00"
        kept = [b for b in RETAINED if b != drop]
        man = manifest(kept, RETAINED + ACTIVE, RETAINED)
        declared = {k[len("hCov_retained5d_"):] for k in man["candidate_keys"]
                    if k.startswith("hCov_retained5d_")}
        self.assertEqual(set(man["retained_bands"]) - declared, {drop},
                         "retained_bands vs candidate_keys already disagree by exactly the omission; "
                         "the validator reads neither retained_bands nor all_syst_bands")


class Level2SelfConsistentOmission(unittest.TestCase):
    """THE CASE THAT DISCRIMINATES. Dropped from ALL THREE manifest lists, C_syst rebuilt to match.

    must_be_rejected_by_B1 = True, and a check built against the manifest's own fields WILL NOT DO IT.
    Only an inventory declared outside the manifest rejects this.
    """

    must_be_rejected_by_B1 = True

    def test_manifest_is_fully_self_consistent_and_still_under_counted(self):
        retained, _a, active_total, c_syst_true = build_truth()
        drop = smallest_band(retained)
        kept = [b for b in RETAINED if b != drop]
        c_syst_short = sum(retained[b] for b in kept) + active_total
        # every list agrees with every other list; nothing internal is wrong
        man = manifest(kept, kept + list(ACTIVE), kept)

        relerr, n = current_identity_relerr(c_syst_short, man, retained, active_total)
        self.assertLessEqual(relerr, RTOL, "identity passes -- as it must for this to be the defect")
        self.assertEqual(n, 39)

        declared = {k[len("hCov_retained5d_"):] for k in man["candidate_keys"]
                    if k.startswith("hCov_retained5d_")}
        self.assertEqual(declared, set(man["retained_bands"]),
                         "NO internal inconsistency: a cross-field check passes this case")
        self.assertNotIn(drop, man["all_syst_bands"])

        # and it is a real under-count, not a cosmetic one
        self.assertLess(quoted_scale(c_syst_short), quoted_scale(c_syst_true),
                        "the quoted systematic budget must be SMALLER than truth")

    def test_the_under_count_is_small_enough_to_defeat_a_magnitude_heuristic(self):
        """Dropping the SMALLEST band is the adversarial choice: a check that only rejects large
        omissions passes this and still certifies an under-counted budget."""
        retained, _a, active_total, c_syst_true = build_truth()
        drop = smallest_band(retained)
        kept = [b for b in RETAINED if b != drop]
        c_syst_short = sum(retained[b] for b in kept) + active_total
        shift = 1.0 - quoted_scale(c_syst_short) / quoted_scale(c_syst_true)
        self.assertGreater(shift, 0.0, "must actually under-count")
        self.assertLess(shift, 1e-3,
                        "and by so little that no plausible magnitude tolerance would fire -- so "
                        "completeness must be checked as SET EQUALITY, never as a total-size test")


class Level3SourceOmissionOutOfScope(unittest.TestCase):
    """NOTED, not required by B1. The band never enters the chain at all.

    `all_bands = _band_keys(a.support_family)` DISCOVERS the universe from the support ROOT, so a band
    missing there is missing from every artifact consistently and no downstream check can see it. The
    point for B1's design: a required inventory DECLARED IN CODE closes this for free, while one derived
    from the support file leaves it open. That is a reason to prefer the former, at no extra cost.
    """

    must_be_rejected_by_B1 = False       # out of stated scope; recorded so the choice is deliberate

    def test_a_source_omission_is_consistent_everywhere(self):
        retained, _a, active_total, _c = build_truth()
        drop = smallest_band(retained)
        kept = [b for b in RETAINED if b != drop]
        discovered = kept                              # _band_keys never sees `drop`
        c_syst_short = sum(retained[b] for b in discovered) + active_total
        man = manifest(discovered, discovered + list(ACTIVE), discovered)
        relerr, _n = current_identity_relerr(c_syst_short, man, retained, active_total)
        self.assertLessEqual(relerr, RTOL)
        self.assertNotIn(drop, man["all_syst_bands"] + man["retained_bands"])


class TheContractForB1(unittest.TestCase):
    """What B1's check must do to these cases. Stated here so the acceptance test is not the fix's own."""

    def test_contract_is_explicit(self):
        required_fail = [Level1DeclarationOnlyOmission, Level2SelfConsistentOmission]
        required_pass = [CompleteSetMustStillPass]
        for cls in required_fail:
            self.assertTrue(getattr(cls, "must_be_rejected_by_B1", False), cls.__name__)
        for cls in required_pass:
            self.assertFalse(getattr(cls, "must_be_rejected_by_B1", True), cls.__name__)
        # The discriminator, restated as an assertion so it cannot be skimmed past:
        # a fix that only compares candidate_keys against retained_bands rejects Level 1 and PASSES
        # Level 2. B1's acceptance therefore requires the inventory to be declared OUTSIDE the manifest.
        self.assertTrue(Level2SelfConsistentOmission.must_be_rejected_by_B1)


if __name__ == "__main__":
    unittest.main()
