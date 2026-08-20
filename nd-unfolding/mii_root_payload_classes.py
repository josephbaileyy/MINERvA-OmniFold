#!/usr/bin/env python3
"""R3's three classes, per ROOT key, for the four `M(ii)` stage-1 artifacts. THE COMPARATOR'S TABLE.

Long-form reasoning, provenance split and the rows that are NOT the obvious class:
`docs/orchestration/ENUMERATION-20260818-mii-root-payload-three-classes.md`.

WHY THIS IS CODE AND NOT ONLY THAT DOCUMENT. `CLAUDE.md`: *a document costs tokens in every future
session forever; a check costs zero and cannot be skipped -- prefer the executable form of any rule
you are tempted to write down.* A classification table is the most skippable kind of prose there is
(long, tabular, easy to skim-agree with) and the most consequential to get wrong, because B2's
comparator either reads a machine-checkable table or re-derives one from memory.

THREE CLASSES, from C's ruling:
    PAYLOAD        bit-exact between the archive and the k=0 anchor. Difference = the member differs.
    CONFIGURATION  must be EQUAL. A difference is a HARD FAILURE, not a finding.
    PROVENANCE     MAY DIFFER from the archive. It may NOT be absent from the member -- C's
                   clarification, and the distinction is load-bearing: provenance is superset-allowed
                   on the ARCHIVE side only.

Any key in either file that this table does not name FAILS CLOSED. That is the whole point; an
unclassified key is the one a future writer adds without telling the comparator.
"""

import re
import sys



# ===================================================================================================
#: WHY A KEY IS ABSENT FROM THE ARCHIVE -- A CLOSED VOCABULARY, C's section 19d. `derive: None` used to
#: mean one thing and had to cover two, which is why a PERFECT ANCHOR FAILED with nine findings.
#:   PREDATES_ARCHIVE  the archive has no counterpart because the key landed AFTER it was written.
#:                     Not a finding -- and NOT a verification either (see below).
#:   EXPECTED_PRESENT  the archive should carry it. Absence is a HARD FINDING.
#: C's section 11f-v(1) ruled that PROVENANCE means "may DIFFER from the archive", not "may be ABSENT
#: from the member". The converse -- present in the member, absent from the archive, for a NON-provenance
#: class -- was never ruled, and my code demanded PROVENANCE there. A class is a COMPARISON RULE; it has
#: no content when one side cannot hold the key at all.
PREDATES_ARCHIVE, EXPECTED_PRESENT = "PREDATES_ARCHIVE", "EXPECTED_PRESENT"


def _landed_date(landed):
    """The YYYY-MM-DD inside a `landed` string, or None. The map already carries its own operand."""
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", str(landed))
    return tuple(int(g) for g in m.groups()) if m else None


def assert_absence_excuses_are_dated(archive_date):
    """THE EXCUSE IS MACHINE-CHECKED, NOT NARRATED -- C's requirement, and the map already had the operand.

    Every row carries a `landed` string ("5856eeb1 BEN-106 2026-08-11", "lane D 2026-08-18") and the
    archive's own date is readable. So a row claiming PREDATES_ARCHIVE is only excused if it landed AFTER
    the archive was written -- AND A ROW CLAIMING IT WHILE LANDING BEFORE IS ITSELF THE FINDING. The
    comparator verifies its own exemption, so the nine keys at 2026-08-11 against an archive at 2026-07-14
    classify automatically with NO hand-maintained exception list.

    `archive_date` is a required (y, m, d). An excuse without its operand is a narration.
    """
    if not (isinstance(archive_date, tuple) and len(archive_date) == 3):
        fail_closed("assert_absence_excuses_are_dated needs the ARCHIVE's date as (y, m, d). The "
                    "PREDATES_ARCHIVE excuse is only checkable against it, and an unchecked excuse is "
                    "the hand-maintained exception list this mechanism exists to avoid.")
    problems = []
    for key, entry in sorted(ARCHIVE_KEY_MAP.items()):
        if entry.get("derive") is not None:
            # A DERIVABLE row needs no absence excuse: the archive's value is OBTAINABLE, so the key is
            # not uncompared. Demanding a reason here was my own category error -- the vocabulary is
            # about keys that CANNOT be compared, not keys the archive happens not to store literally.
            continue
        why = entry.get("absence")
        if why not in (PREDATES_ARCHIVE, EXPECTED_PRESENT):
            problems.append(f"{key}: absence reason {why!r} is not in the closed vocabulary "
                            f"({PREDATES_ARCHIVE} / {EXPECTED_PRESENT})")
            continue
        if why is not PREDATES_ARCHIVE:
            continue
        landed = _landed_date(entry.get("landed"))
        if landed is None:
            problems.append(f"{key}: claims PREDATES_ARCHIVE but its `landed` carries no date "
                            f"({entry.get('landed')!r}) -- the excuse has no operand")
        elif landed <= archive_date:
            problems.append(
                f"{key}: CLAIMS PREDATES_ARCHIVE BUT LANDED {landed} <= archive {archive_date}. The "
                "archive was written after this key existed, so its absence is NOT explained by age -- "
                "this row is itself the finding.")
    if problems:
        fail_closed("absence excuses:\n  " + "\n  ".join(problems))
    return len(ARCHIVE_KEY_MAP)

def fail_closed(msg):
    """Fail closed with THE EXIT CODE THE CALLER DEFINES AS FAIL, which is 2, not 1.

    H4, lane D: every `raise SystemExit("[FAIL] ...")` across these modules exited **1**, while
    `mii_anchor_comparator.main` maps {"PASS": 0, "INCOMPLETE": 1, "FAIL": 2}. So an unclassified key, a
    ZOMBIE OR kRecovered ROOT FILE, a stale acknowledgement list and a malformed declaration ALL EXITED 1
    WHILE PRINTING [FAIL] -- and a driver treating rc 2 as stop and rc 1 as continue walks straight past
    a corrupt archive. THE MESSAGE SAID FAIL AND THE EXIT CODE SAID INCOMPLETE; only the code is
    machine-read, and the human-readable half was the one that was right.

    ONE definition, used by both modules, because two copies of an exit convention drift and the drift is
    invisible -- each copy prints the word FAIL.
    """
    print(f"[FAIL] {msg}", file=sys.stderr)
    # THE CODE *AND* THE MESSAGE. `SystemExit(2)` alone gives the right exit status and makes the
    # exception object carry only "2" -- so any in-process caller that catches it loses the reason
    # entirely, and the reason is the whole value of a fail-closed guard. Printing to stderr serves the
    # CLI; `fail_message` serves every programmatic caller, including this repo's own tests.
    # A guard that cannot report its own reason is a guard whose failures get re-diagnosed, which is the
    # same objection that made `TFile.Open`'s dead `zombie/unopenable` branch worth fixing.
    exc = SystemExit(2)
    exc.fail_message = msg
    raise exc


PAYLOAD = "PAYLOAD"
CONFIGURATION = "CONFIGURATION"
PROVENANCE = "PROVENANCE"

#: Keys whose value is DERIVED FROM other keys in the same file, so BEN-077's ingredient rule applies:
#: they are payload by C's test, and a comparator that only checks equality on them cannot catch a
#: file whose scalar disagrees with its own matrix. Equality is necessary and not sufficient here.
RECOMPUTE_REQUIRED = frozenset({
    "sqrt_tr_unified", "sqrt_tr_block", "sqrt_tr_old", "sqrt_tr_new",
    "joint_mean_shift_norm", "fixed_seed_null_norm", "globalCompleteness",
    "upstream_joint_mean_shift_norm", "upstream_fixed_seed_null_norm",
})

#: THE GRID, WHICH IS *NOT* THE SIZE OF ANY ARTIFACT. 65,856 is the full 5D (pt,pz,Eavail,q3,W) grid.
#: Every matrix and per-bin array in these products is on the REPORTED SUPPORT -- the `cv > 0` mask,
#: measured by lane D against the real archive at 10,694, and 10694/65856 = 16.24%.
#:
#: THIS CONSTANT WAS WRONG AND ITS OWN COMMENT SAID WHY. The previous version recorded 65,856 as "the"
#: length, on the stated grounds that C had sized a per-bin array off the 285-bin extended-FPS grid and
#: been wrong by 230x. I CORRECTED A WRONG GRID BY SUBSTITUTING A DIFFERENT WRONG GRID -- and it is the
#: SAME DENOMINATOR ERROR as the stage-0 headline (`changed 10510/65856`), on the same day, in two lanes,
#: inside the fix for the first instance. Consequences, both verified by lane D:
#:     "34.7 GB matrix"         -> 10694^2 x 8 B = 0.915 GB     (I was 37.9x over)
#:     "0.527 MB per-bin array" -> 10694   x 8 B = 0.0856 MB    (I was 6.2x over)
#: SO C's `diag(C_old)` RETENTION REMEDY COSTS 0.0856 MB, NOT 0.527 MB.
#: The lesson is narrower than "check your arithmetic": A GRID IS NOT AN ARTIFACT SIZE. Sparse binning
#: makes them differ by 6x here, and the reported support is the only one any product materialises.
FLAT_NBINS = 65856          #: the GRID -- do not size anything from this
REPORTED_NBINS = 10694      #: the cv>0 SUPPORT -- the real dimension of every matrix and per-bin array
SUPPORT_FRACTION = REPORTED_NBINS / FLAT_NBINS       #: 0.1624


#: EXPECTED ELEMENT COUNT PER KEY, derived from each writer's own construction line. THREE DIFFERENT
#: DIMENSIONS LIVE IN THESE FILES and a single global constant was wrong about all of them -- which is
#: how `FLAT_NBINS = 65856` came to be quoted as "the" length:
#:     hXSecND_flat        len(xsec.ravel())        -> 65,856   THE FULL GRID   (sweep_bank_5d.py:278,291)
#:     hJointMeanShift     nrep = int(rep.sum())    -> 10,694   the support     (unified_throw_cov.py:348,552)
#:     C_unified/_blocksum/_cross   nrep x nrep     -> 10,694^2                 (unified_throw_cov.py:522)
#:     hInflation_g        n = vu.size              -> 10,694   the support     (adopt_unified_5d.py:110,173)
#:     hCov_combined5d_total_uthrow n x n           -> 10,694^2                 (adopt_unified_5d.py:170)
#: A KEY NOT LISTED HERE HAS ITS COVERAGE *PRINTED* AND NOT *ASSERTED* -- the lateral product's per-axis
#: `hXSec_*` marginals have binning-dependent lengths I have not derived, and asserting a number I have
#: not read out of a writer is how the wrong constant got here in the first place.
EXPECTED_ELEMENTS = {
    "hXSecND_flat": FLAT_NBINS,
    "hJointMeanShift": REPORTED_NBINS,
    "hInflation_g": REPORTED_NBINS,
    "C_unified": REPORTED_NBINS ** 2,
    "C_blocksum": REPORTED_NBINS ** 2,
    "C_cross": REPORTED_NBINS ** 2,
    "hCov_combined5d_total_uthrow": REPORTED_NBINS ** 2,
}


def artifact_sizes():
    """Sizes of what this comparator actually reads, from REPORTED_NBINS rather than the grid."""
    return {
        "covariance_TH2D_bytes": REPORTED_NBINS ** 2 * 8,
        "per_bin_array_bytes": REPORTED_NBINS * 8,
        "diag_C_old_remedy_bytes": REPORTED_NBINS * 8,
    }

UNIFIED_THROW_COV = {
    "C_unified": PAYLOAD, "C_blocksum": PAYLOAD, "C_cross": PAYLOAD,
    "hJointMeanShift": PAYLOAD,
    "sqrt_tr_unified": PAYLOAD, "sqrt_tr_block": PAYLOAD,
    "joint_mean_shift_norm": PAYLOAD, "fixed_seed_null_norm": PAYLOAD,
    "fixed_seed_null_checked": CONFIGURATION,
    "n_throws": CONFIGURATION,
    # `draw_seed` IS CONFIGURATION, NOT PROVENANCE -- the row most worth attacking. Spec (B) needs the
    # throw REALIZATIONS common to all 50 members so the scan varies the estimator and nothing else. A
    # member that drew different throws is not a member of this scan, so a difference here is a hard
    # failure. Classifying it as provenance because the name contains "seed" would let the single
    # difference that invalidates the entire scan pass as expected variation. The two roles land in
    # two different classes; the word "seed" predicts neither.
    "draw_seed": CONFIGURATION,
    "estimator_seed": PROVENANCE,
    "est_seed_offset": PROVENANCE, "est_seed_offset_declared": PROVENANCE,
}

ADOPTED_UTHROW = {
    "hCov_combined5d_total_uthrow": PAYLOAD,
    "hInflation_g": PAYLOAD,
    "sqrt_tr_old": PAYLOAD, "sqrt_tr_new": PAYLOAD,
    "upstream_fixed_seed_null_norm": PAYLOAD,
    "upstream_joint_mean_shift_norm": PAYLOAD,
    "upstream_n_throws": CONFIGURATION,
    "fixed_seed_null_norm_checked": CONFIGURATION,
    "joint_mean_shift_norm_checked": CONFIGURATION,
    "n_throws_checked": CONFIGURATION,
    # These two differ between the mean-centered and cv-centered products and in NOTHING ELSE except
    # payload. Comparing the wrong pair across members yields a plausible number; equality here is
    # what stops it, and it is the cheapest silent-swap detector in the set.
    "centering_convention": CONFIGURATION,
    # BASENAMES, and they pass an equality check ONLY because of member-root-first. Under
    # `mii/member_k001200/uq_5d/...` the basename is byte-identical to the archive's -- only
    # directories change. Under a filename-suffix scheme every member would differ here and the
    # difference would be INDISTINGUISHABLE FROM A GENUINE WRONG-INPUT MISMATCH, which is the failure
    # these keys exist to catch. A third independent argument for C's path ruling, reached from the
    # ROOT keys rather than from globs or the preflight.
    "uthrow_source": CONFIGURATION, "combined_source": CONFIGURATION,
    # ================= REMEDY (A) ON THIS ARTIFACT, 2026-08-20: THE KEYS ARE CLASSIFIED ============
    # THESE SEVEN WERE COMMENTED OUT UNTIL 2026-08-20 and the reason they are now live is a CORRECTION
    # to the argument that commented them, not a change of mind about it. The old note said "a table
    # describing a writer that does not exist yet is worse than one admitting the gap", which was right
    # about the writer and wrong about the table: THIS TABLE IS A REQUIREMENT ON THE ARTIFACT AND IS
    # AGNOSTIC ABOUT WHICH FILE WRITES IT. `identity_is_checkable` reads ARTIFACTS (`:431-432`), not
    # STAMP_COVERAGE, so "the writer stamps nothing" was never the property this table asserted.
    #
    # WHO WRITES THEM: `mii_adopt_unified_5d_stamped.py`, the remedy (A) WRAPPER. `adopt_unified_5d.py`
    # is receipt-bound (`state/ben106-stamp-verify-active-56695424.json`) and IS NOT TOUCHED -- C ruled
    # at `783d648a` §25 that (A) here is a new unpinned wrapper invoking the pinned writer as a
    # subprocess and reopening its output `UPDATE`. See `STAMP_COVERAGE` for the capability claim and
    # for what is still CLUSTER-UNVERIFIED.
    #
    # THE COST, STATED: every adopted root built BEFORE the wrapper now FAILS CLOSED here
    # (`anchor_identity:448-450`, `compare():514`). That is an unavoidable FAIL, not a false green, and
    # it is the direction this campaign chose -- an absent stamp is not a weak yes.
    "est_seed_offset": PROVENANCE, "est_seed_offset_declared": PROVENANCE,
    # BY GROUP, AND NEVER A SINGLE `estimator_seed` -- VL141 (`VALIDATION_LEDGER.md:1974`). This product
    # mixes the sweep leg's g1 seed (42+k, via the combined intermediate) with the throw leg's g2 seed
    # (1000+k), so one key would be the exact false quotable claim VL141 exists to correct. Note the
    # asymmetry with SWEEP_UNIVERSE/LATERAL_CV above, which DO carry a single `estimator_seed`: those
    # products have one leg.
    "upstream_estimator_seed_g1": PROVENANCE, "upstream_estimator_seed_g2": PROVENANCE,
    "upstream_estimator_seed_g1_checked": CONFIGURATION,
    "upstream_estimator_seed_g2_checked": CONFIGURATION,
    # C's 11g precondition: 10,694 x 8 B = 0.0856 MB, the cv>0 SUPPORT and not the 65,856 grid. It is
    # `sqrt_tr_old`'s only ingredient, and `sqrt_tr_old` is the predeclared bar's own operand, so
    # without it BEN-077 could never again be satisfied for the bar once 11g releases the 41.44 GB
    # intermediate.
    "hDiagCombinedOld": PAYLOAD,
}

SWEEP_UNIVERSE = {
    "hXSecND_flat": PAYLOAD,
    "globalCompleteness": PAYLOAD,
    # dataPOT is CONFIGURATION, not provenance -- C corrected the mediator here, and the reason
    # generalises: it ENTERS THE ARITHMETIC, so a member normalised to a different POT would have
    # PASSED as provenance. C's heuristic: a scalar that enters the arithmetic looks like a stamp
    # because it is recorded once and never varies. CONSTANCY IS NOT CIRCUMSTANCE. Ask what breaks if
    # it changes, not how often it changes.
    "dataPOT": CONFIGURATION,
    "ndim": CONFIGURATION,
    "estimator_seed": PROVENANCE,
    "est_seed_offset": PROVENANCE, "est_seed_offset_declared": PROVENANCE,
}

#: The 19 lateral + CV. SAME classes, and NO identity key of any kind -- see `STAMP_COVERAGE`.
LATERAL_CV = {
    "hXSecND_flat": PAYLOAD, "globalCompleteness": PAYLOAD,
    "dataPOT": CONFIGURATION, "ndim": CONFIGURATION,
    # REMEDY (A), 2026-08-19. C widened (A) to this artifact on D's enumeration -- I had listed WRITERS
    # needing stamps, D listed ARTIFACTS THE GATE CANNOT READ, and D's direction found more.
    "est_seed_offset": PROVENANCE, "est_seed_offset_declared": PROVENANCE,
    "estimator_seed": PROVENANCE,
    # `--seed` defaults to None on this writer, so "nobody passed one" must be READABLE rather than
    # inferred from a missing key. An absent stamp is not a weak yes.
    "estimator_seed_checked": CONFIGURATION,
}

#: The 41.44 GB combined intermediate. It carried NO scalars before remedy (A) -- which is why g1's
#: estimator seed could not reach adopt -- and now carries the propagated g1 identity plus the universe
#: count it was verified over. Listed even though 11g releases it, because it is comparable while it
#: exists and an unlisted artifact cannot be compared at all.
COMBINED_INTERMEDIATE = {
    "hCov_universe5d_total": PAYLOAD,
    "hCov_combined5d_total": PAYLOAD,
    "estimator_seed": PROVENANCE,
    "est_seed_offset": PROVENANCE, "est_seed_offset_declared": PROVENANCE,
    "n_universes": CONFIGURATION,
}

ARTIFACTS = {
    "uq_5d/unified_throw_cov_5d.root": UNIFIED_THROW_COV,
    "adopted_uthrow.root": ADOPTED_UTHROW,
    "adopted_uthrow_cvcentered.root": ADOPTED_UTHROW,
    "sweep_universe.root": SWEEP_UNIVERSE,
    "lateral_cv.root": LATERAL_CV,
    "combined_intermediate.root": COMBINED_INTERMEDIATE,
}

# =====================================================================================================
#: THE ARCHIVE PREDATES ITS OWN WRITERS' PROVENANCE BLOCKS, and this map is what keeps stage 1 from
#: reddening for that reason instead of a real one. Each entry: a key the CURRENT writer emits that the
#: ARCHIVE's copy lacks, with the dated cause and how the archive-side value is obtained.
#:
#: `derive` is a callable taking the archive's key->value dict and returning the value, or None meaning
#: "the archive genuinely has no counterpart; the key is member-only and must be PROVENANCE-class".
ARCHIVE_KEY_MAP = {
    # `fixed_seed_null_checked` landed 2026-08-11 (null-as-absent closure). The archive lacks the flag
    # but HAS `fixed_seed_null_norm` -- and the writer emits the norm ONLY when the check ran. So the
    # archive's value is DERIVABLE as 1, not unknown. This is the shape every row should take: derive
    # from a dated writer property, or declare the key member-only and fail on anything else.
    "fixed_seed_null_checked": {
        "landed": "2026-08-11 null-as-absent closure",
        "derive": lambda keys: 1 if "fixed_seed_null_norm" in keys else 0,
    },
    # `estimator_seed`: PROVENANCE, member-only, no archive counterpart. But note what IS derivable
    # and is used by `anchor_identity` below -- before the two-role split ONE `--seed` served both
    # roles at 1000 (VL141, `unified_throw_cov.py:525`), so the archive's ESTIMATOR seed was 1000 too.
    # Provenance may differ, so no equality is imposed here; at k=0 specifically it must NOT differ,
    # which is a property of the anchor rather than of the class.
    "estimator_seed": {"landed": "gate 1, this campaign, 2026-08-17", "derive": None,
                       "absence": PREDATES_ARCHIVE,
                       "archive_value_known_to_be": 1000},
    # `draw_seed` WAS THE ROW MY OWN TABLE CAUGHT, WITHIN SECONDS OF BEING EXECUTABLE, AND IT IS THE
    # REASON THIS FILE IS CODE RATHER THAN ONLY THE ENUMERATION DOCUMENT.
    #
    # I classified it CONFIGURATION -- must be EQUAL, difference is a hard failure -- and argued the
    # case at length: spec (B) needs the throw realizations common to all 50 members. That argument is
    # correct. But `compare()` immediately reported the contradiction: THE ARCHIVE CARRIES NO
    # `draw_seed` KEY, AND NO `seed` KEY EITHER (the mediator's 9-key read has neither). So "must equal
    # the archive" was UNENFORCEABLE AGAINST THE ARCHIVE, and my table asserted a check that could
    # never run. The prose read fine; running it did not.
    #
    # THE FIX IS A THIRD KIND OF MAP ENTRY, which I had not anticipated: not "derive from the archive's
    # other keys", not "member-only provenance", but A DECLARED CONSTANT EXTERNAL TO BOTH FILES. The
    # archive's draw seed is 1000 because every g2 launcher pins the literal, and that is sourced from
    # the policy module rather than retyped here so there is ONE place it can be wrong.
    "draw_seed": {"landed": "gate 1, this campaign, 2026-08-17",
                  "derive": lambda keys: _g2_baseline(),
                  "source": "declared constant: the pinned g2 literal. The archive file itself "
                            "carries NO seed key of any kind, so this value cannot come from it."},
    "est_seed_offset": {"landed": "lane D 2026-08-18", "derive": None, "absence": PREDATES_ARCHIVE},
    "est_seed_offset_declared": {"landed": "lane D 2026-08-18", "derive": None, "absence": PREDATES_ARCHIVE},
    "fixed_seed_null_norm_checked": {"landed": "5856eeb1 BEN-106 2026-08-11", "derive": None, "absence": PREDATES_ARCHIVE},
    "joint_mean_shift_norm_checked": {"landed": "5856eeb1 BEN-106 2026-08-11", "derive": None, "absence": PREDATES_ARCHIVE},
    "n_throws_checked": {"landed": "5856eeb1 BEN-106 2026-08-11", "derive": None, "absence": PREDATES_ARCHIVE},
    "upstream_fixed_seed_null_norm": {"landed": "5856eeb1 BEN-106 2026-08-11", "derive": None, "absence": PREDATES_ARCHIVE},
    "upstream_joint_mean_shift_norm": {"landed": "5856eeb1 BEN-106 2026-08-11", "derive": None, "absence": PREDATES_ARCHIVE},
    "upstream_n_throws": {"landed": "5856eeb1 BEN-106 2026-08-11", "derive": None, "absence": PREDATES_ARCHIVE},
    "centering_convention": {"landed": "5856eeb1 BEN-106 2026-08-11", "derive": None, "absence": PREDATES_ARCHIVE},
    "uthrow_source": {"landed": "5856eeb1 BEN-106 2026-08-11", "derive": None, "absence": PREDATES_ARCHIVE},
    "combined_source": {"landed": "5856eeb1 BEN-106 2026-08-11", "derive": None, "absence": PREDATES_ARCHIVE},
    # ===== THE FIVE ROWS NOBODY ENUMERATED, AND THEY WOULD HAVE REDDENED THE WRAPPER'S FIRST RUN =====
    # `compare():522-526` FAILS a key that is present in the member and absent from the archive with no
    # map row -- "unexplained; the map is dated and derivable, so add a row or fail". Remedy (A)'s seven
    # keys were classified above WITHOUT these rows, so the wrapper's first real product would have
    # failed stage 1 for a reason that has nothing to do with the wrapper. Found by enumerating the
    # OTHER table the flip touches rather than by running anything -- the cluster is down.
    #
    # PREDATES_ARCHIVE IS CODE-JUSTIFIED HERE, not assumed: the archive's adopted roots were written by
    # `adopt_unified_5d.py` at 5856eeb1, whose only upstream loop covers exactly
    # `fixed_seed_null_norm`/`joint_mean_shift_norm`/`n_throws` (`:198-204`), and
    # `grep -c est_seed_offset nd-unfolding/adopt_unified_5d.py` is 0. No adopted root in existence
    # carries any of these five, and none can until it is rebuilt through the wrapper.
    "upstream_estimator_seed_g1": {"landed": "lane B remedy (A) wrapper 2026-08-20", "derive": None,
                                   "absence": PREDATES_ARCHIVE},
    "upstream_estimator_seed_g2": {"landed": "lane B remedy (A) wrapper 2026-08-20", "derive": None,
                                   "absence": PREDATES_ARCHIVE},
    "upstream_estimator_seed_g1_checked": {"landed": "lane B remedy (A) wrapper 2026-08-20",
                                           "derive": None, "absence": PREDATES_ARCHIVE},
    "upstream_estimator_seed_g2_checked": {"landed": "lane B remedy (A) wrapper 2026-08-20",
                                           "derive": None, "absence": PREDATES_ARCHIVE},
    # NOT `derive`-able from the archive's own keys, and the near-miss is worth naming: the archive DOES
    # carry `sqrt_tr_old`, whose square is this histogram's SUM. A sum does not determine 10,694 bins,
    # so there is no derivation -- only the reverse check the wrapper performs before writing.
    "hDiagCombinedOld": {"landed": "lane B remedy (A) wrapper 2026-08-20", "derive": None,
                         "absence": PREDATES_ARCHIVE},
}

#: Measured 2026-08-18 from source: which ROOT writers on a member's chain stamp the four identity
#: keys. Remedy (B) -- never resume a ROOT product -- must cover every writer with 0 here; its scope
#: NARROWS as (A) lands, so this table is the thing to re-measure rather than the prose.
#: WAS A COUNT, AND THE COUNT WAS THE WRONG SHAPE. It tallied literal
#: `TParameter("int")("estimator_seed", ...)` occurrences -- and after remedy (A) two writers stamp
#: through a LOOP over a variable key (`TParameter("int")(_k, ...)`) or an f-string
#: (`f"upstream_estimator_seed_{_name}"`). Both are correct and both are INVISIBLE to a literal matcher,
#: so the tally read 0 for a writer that stamps three keys. A COUNT OF LITERAL OCCURRENCES MEASURES THE
#: SPELLING, NOT THE CAPABILITY -- BEN-482's family, arriving in a measurement table this time.
#: So: a boolean capability plus HOW, with the mechanism stated so the boolean is falsifiable.
STAMP_COVERAGE = {
    "sweep_bank_5d.py": {
        "stamps": True, "how": "three literal TParameter writes; no draws, so no draw_seed",
        "products": "169 vertical universes"},
    "unified_throw_cov.py": {
        "stamps": True, "how": "four literal TParameter writes -- both seed roles and both offset keys",
        "products": "unified_throw_cov_5d.root"},
    "unfold_nd_omnifold_unbinned.py": {
        "stamps": True, "how": "remedy (A) 2026-08-19: the offset pair unconditionally, plus "
                               "estimator_seed_checked and estimator_seed when --seed was given. "
                               "--seed DEFAULTS TO None, so absence has to be a READABLE state",
        "products": "19 lateral + CV"},
    "analyze_universes_5d.py": {
        "stamps": True, "how": "remedy (A) 2026-08-19: PROPAGATES the g1 identity from the 188 universes "
                               "via a loop over a variable key, AFTER asserting all 188 agree. THE LINK "
                               "NOBODY ENUMERATED -- it wrote zero scalars, so g1's seed could not reach "
                               "adopt at all, however carefully adopt was patched",
        "products": "the 41.44 GB combined intermediate"},
    "adopt_unified_5d.py": {
        # `stamps: False` IS PERMANENT UNLESS THIS FILE'S BYTES CHANGE, and that is now a statement
        # about a receipt rather than about a backlog. C ruled at `783d648a` §25 that remedy (A) here is
        # a WRAPPER, so nothing will ever be added to this file: its bytes are bound by
        # `state/ben106-stamp-verify-active-56695424.json` and the pre-commit hook refuses any edit.
        # `grep -c est_seed_offset nd-unfolding/adopt_unified_5d.py` is 0 and will stay 0.
        # NOT "BLOCKED" ANY MORE. "Blocked" says the work is waiting on a receipt re-issue; C refused
        # the re-issue AND the edit, so the work is DONE ELSEWHERE. Leaving the word would misdirect the
        # next reader toward a gate re-run that has been explicitly declined.
        "stamps": False,
        "covered_by": "mii_adopt_unified_5d_stamped.py",
        "how": "STAMPS NOTHING AND NEVER WILL: receipt-bound bytes "
               "(state/ben106-stamp-verify-active-56695424.json), so C REFUSED the edit, the receipt "
               "re-issue and the hash update alike (783d648a §25). Identity on this writer's products "
               "is supplied by the wrapper named in `covered_by`, which runs these exact bytes as a "
               "subprocess and then reopens the output UPDATE. The preserved specification is "
               "docs/orchestration/pending/"
               "PENDING-20260819-remedy-A-adopt-blocked-on-ben106-rebinding.patch -- kept as the spec "
               "of WHAT to stamp, NOT to be applied to this file",
        "products": "the PAYLOAD of the two 892 MB citable adopted roots (identity is the wrapper's)"},
    "mii_adopt_unified_5d_stamped.py": {
        "stamps": True,
        "covers": "adopt_unified_5d.py",
        "how": "remedy (A) 2026-08-20, as a WRAPPER because the writer it wraps is receipt-bound. Runs "
               "adopt_unified_5d.py as a SUBPROCESS -- C's preference, because that executes the exact "
               "bytes the receipt's sha256 names -- then reopens the output UPDATE and writes the "
               "offset pair, upstream_estimator_seed_g1/_g2 BY GROUP with _checked flags (never a "
               "single estimator_seed, per VL141), and C's 11g hDiagCombinedOld. Refuses a product "
               "whose two legs are different members. *** ROOT WRITE PATH CLUSTER-UNVERIFIED as of "
               "2026-08-20: `import ROOT` raises ModuleNotFoundError on the lane-B host, so this "
               "boolean is a SOURCE-VERIFIED CAPABILITY CLAIM and not a demonstration. Every pure "
               "function is executed by tests/test_remedy_a_adopt_wrapper.py; the ROOT readers, "
               "_read_diagonal and _stamp_output have never run. ***",
        "products": "the IDENTITY of the two 892 MB citable adopted roots"},
}


def writers_without_identity_stamps():
    """Writers remedy (A) has not reached AND nothing else covers. Empty is the goal.

    `covered_by` EXISTS BECAUSE §25 MADE "EMPTY" UNREACHABLE BY CONSTRUCTION. `adopt_unified_5d.py`'s
    bytes are frozen by a receipt, so it can never stamp anything, so a function that only reads
    `stamps` would have reported an open gap forever while the gap was closed by design -- a permanent
    red that teaches its caller to ignore it, which is the exact failure mode D named for
    `identity_is_checkable`.
    THE EDGE IS NOT A DEFINITE DESCRIPTION. A `covered_by` naming a file that does not exist, does not
    name the identity keys, or does not name the writer it claims to cover would be an unfalsifiable
    excuse; `test_uq_remediation.py`'s producer-derived test re-reads the covering file's source for all
    three, so the exemption is checked against code rather than asserted here.
    """
    return sorted(k for k, v in STAMP_COVERAGE.items()
                  if not v["stamps"] and not v.get("covered_by"))



def _g2_baseline():
    """The pinned draw seed, from the policy module -- ONE place it can be wrong, not two.

    `seed_offset_policy.LEG_BASELINES` is the campaign's single source of truth for which coherence
    group each leg sits in and at what baseline. Retyping 1000 here would create a second copy that
    drifts silently, which is the same defect as a second copy of a completeness rule.
    """
    import seed_offset_policy
    group, baseline = seed_offset_policy.LEG_BASELINES["unified_throw_cov"]
    if group != "g2":
        fail_closed(
            f"unified_throw_cov is in group {group!r}, not g2 -- the draw-seed derivation "
            "below assumed g2 and must be re-derived, not patched.")
    return baseline


#: WHAT MEMBER IDENTITY ACTUALLY REQUIRES: the OFFSET PAIR, and nothing else.
#: `estimator_seed` was in this tuple and it made `identity_is_checkable` FALSE for the adopted roots even
#: after remedy (A) stamped them -- because VL141 forbids a single `estimator_seed` on that product: it
#: mixes a g1 seed (42+k) with a g2 one (1000+k), and one key would be a false quotable claim. So the
#: predicate was demanding the very key the physics says must not be there.
#: THE OFFSET IS THE MEMBER IDENTITY AND IT IS SINGLE-VALUED EVERYWHERE. The estimator seed is per-LEG,
#: so it is checked where it exists and not required where it cannot.
IDENTITY_KEYS = ("est_seed_offset", "est_seed_offset_declared")
OPTIONAL_IDENTITY_KEYS = ("estimator_seed",)


def identity_is_checkable(artifact):
    """Does THIS ARTIFACT'S TABLE declare the identity keys? H3, lane D.

    IT IS A QUESTION ABOUT THE ARTIFACT, NOT ABOUT A WRITER, and the previous sentence of this
    docstring said "writer" -- which was wrong in a way that mattered as soon as remedy (A) became a
    WRAPPER. The predicate reads `ARTIFACTS` (below); it cannot see writers at all, and under §25 the
    file that stamps these keys is not the file that writes the payload. Asking it about a writer
    invites exactly the inference that held the adopted roots out of this set for a day.

    THE EVIDENCE THIS DOCSTRING USED TO CITE NO LONGER EXISTS, WHICH IS WHY THE CITATION WAS REPLACED
    RATHER THAN REWORDED. It read *"`STAMP_COVERAGE` records `adopt_unified_5d.py: 0` and
    `unfold_nd_omnifold_unbinned.py: 0`"* -- a TALLY schema deleted in the same commit that converted
    that table to a boolean plus a `how` string, so the quoted numbers were doubly stale: the counts
    are gone AND both writers' products now carry identity. Read `STAMP_COVERAGE` for the current
    state; do not read it here.

    THE HISTORY IS KEPT BECAUSE IT IS WHY THE BRANCH EXISTS: on 2026-08-18 three of five artifacts
    carried no identity key, `anchor_identity` was called unconditionally, and the check emitted three
    problems every run and FAILED regardless of payload. All six declare the keys as of 2026-08-20, so
    the relaxation is currently unreachable for every real artifact -- and is retained anyway, because
    a predicate that can no longer answer NO is not a predicate.

    D'S REASON THIS MATTERS MORE THAN IT LOOKS, and it is the pressure-toward-green risk arriving from
    the other side: AT STAGE 1 AN UNAVOIDABLE FAIL IS THE THING MOST LIKELY TO GET THE GATE ROUTED
    AROUND. A check that cannot pass teaches its caller to skip it, and then it protects nothing.
    """
    table = ARTIFACTS.get(artifact, {})
    return all(k in table for k in IDENTITY_KEYS)


def anchor_identity(member_keys, offset):
    """At k=0 the anchor's PROVENANCE keys are NOT free, and the class alone does not say so.

    PROVENANCE means "may differ from the archive" -- across the scan. The k=0 anchor is the member
    that must reproduce the archive, so its estimator seed must equal the archive's baseline exactly.
    Leaving this to the class would let an anchor built at the wrong seed pass on the grounds that
    seeds are allowed to vary, which is true of members 1-49 and false of member 0.

    C's asymmetry, which is why this check is not redundant with the digests: at stage 1 a bit-exact
    pass and "you compared the archive to itself" are THE SAME OBSERVATION. Section 4's cross-member
    digest-distinctness backstop needs more than one member and stage 1 has one.
    """
    problems = []
    if "est_seed_offset_declared" not in member_keys:
        problems.append("est_seed_offset_declared ABSENT -- an absent stamp is not a weak yes, it is "
                        "a no; nothing can be concluded about which member this is")
    elif not member_keys["est_seed_offset_declared"]:
        problems.append("est_seed_offset_declared == 0 -- this product may have come from an UNHOOKED "
                        "launcher stamping its baseline, which is indistinguishable from a deliberate "
                        "k=0 anchor. That is precisely the ambiguity the two keys exist to remove.")
    if member_keys.get("est_seed_offset") != offset:
        problems.append(f"est_seed_offset {member_keys.get('est_seed_offset')!r} != declared {offset!r}")
    if offset == 0 and "estimator_seed" in member_keys:
        # ONLY WHERE A SINGLE ESTIMATOR SEED EXISTS. On the adopted roots it deliberately does not
        # (VL141), so demanding it would fail an artifact for lacking a key it must not have.
        known = ARCHIVE_KEY_MAP["estimator_seed"].get("archive_value_known_to_be")
        if member_keys.get("estimator_seed") != known:
            problems.append(
                f"k=0 ANCHOR: estimator_seed {member_keys.get('estimator_seed')!r} != the archive's "
                f"{known!r}. Provenance may differ ACROSS the scan; the anchor is the member that "
                "must not differ.")
    return problems

def classify(artifact, key):
    """Class of `key` in `artifact`, or raise. FAILS CLOSED on an unclassified key."""
    try:
        table = ARTIFACTS[artifact]
    except KeyError:
        fail_closed(
            f"unknown artifact {artifact!r}; known: {sorted(ARTIFACTS)}")
    if key not in table:
        fail_closed(
            f"{artifact}: key {key!r} has NO CLASS.\n"
            "        An unclassified key is exactly the one a future writer added without telling the\n"
            "        comparator, so it must fail rather than default. Classify it in\n"
            "        mii_root_payload_classes.py and say why in the enumeration document.")
    return table[key]


def compare(artifact, archive_keys, member_keys):
    """Apply the three classes plus the archive key map. Returns (verdict, findings).

    `archive_keys`/`member_keys` are dicts key -> value (scalars) or key -> digest (histograms).
    verdict is "PASS" only when every payload matches, every configuration is equal, and every
    mandatory provenance key is PRESENT in the member.
    """
    findings, owed, uncomparable = [], [], []
    # ITERATE THE TABLE TOO, NOT JUST THE TWO FILES' KEYS -- MY OWN TEST CAUGHT THIS AND IT WAS A REAL
    # DEFECT, NOT A TEST ERROR. The first version iterated `set(archive_keys) | set(member_keys)`, so a
    # key absent from BOTH never entered the loop and the "ABSENT FROM MEMBER" branch never fired. That
    # is not a corner case: `est_seed_offset_declared` IS NEVER IN THE ARCHIVE, by construction, so a
    # member that omitted its own offset stamp was INVISIBLE to the comparator -- verdict INCOMPLETE,
    # reading as "nearly fine".
    #
    # This is exactly C's invariant, violated by the check written to enforce it: every layer that
    # could satisfy a member from pre-existing bytes must fail closed on an absent positive
    # declaration; AN ABSENT STAMP IS NOT A WEAK YES, IT IS A NO. The union of two files cannot express
    # a requirement, because a requirement is about what SHOULD be there. The table is the domain.
    table_keys = set(ARTIFACTS.get(artifact, {}))
    for key in sorted(table_keys | set(archive_keys) | set(member_keys)):
        cls = classify(artifact, key)                     # fails closed on an unknown key
        in_a, in_m = key in archive_keys, key in member_keys

        if not in_m:
            # PROVENANCE MEANS "MAY DIFFER FROM THE ARCHIVE"; IT DOES NOT MEAN "MAY BE ABSENT FROM THE
            # MEMBER". C's clarification, and it is why provenance is the class that is MANDATORY here.
            if cls is PROVENANCE:
                findings.append(
                    f"{key}: ABSENT FROM MEMBER (PROVENANCE, MANDATORY) -- inadmissible. Provenance "
                    "may differ from the archive; it may not be missing. An absent stamp is not a "
                    "weak yes, it is a no.")
            elif in_a:
                findings.append(f"{key}: ABSENT FROM MEMBER ({cls}) -- the archive has it")
            # else: absent from BOTH and not provenance. Legitimate for a conditionally-written key --
            # `fixed_seed_null_norm` is only emitted when `--null` ran, and its `_checked` companion is
            # what makes that a readable state rather than an inference. Not a finding.
            continue

        if not in_a:
            entry = ARCHIVE_KEY_MAP.get(key)
            if entry is None:
                findings.append(
                    f"{key}: present in member, absent from archive, AND NOT IN THE ARCHIVE KEY MAP "
                    f"({cls}) -- unexplained; the map is dated and derivable, so add a row or fail")
                continue
            if entry["derive"] is None:
                # H2, LANE D, AGAINST THE REAL ARCHIVE: THIS BRANCH USED TO REQUIRE `cls is PROVENANCE`
                # AND FAILED A PERFECT ANCHOR WITH NINE FINDINGS. Nine of the thirteen `derive: None`
                # rows are CONFIGURATION or PAYLOAD, so the map written to stop the archive's AGE from
                # reddening stage 1 was itself what reddened it.
                #
                # THE ERROR WAS CONFLATING TWO REASONS A KEY CAN BE MEMBER-ONLY:
                #   (a) the ARCHIVE predates the writer that emits it -- dated, expected, admissible,
                #       AND IT SAYS NOTHING ABOUT THE KEY'S CLASS. `upstream_fixed_seed_null_norm` is
                #       PAYLOAD and legitimately absent from a 2026-07-14 file.
                #   (b) the MEMBER is missing something it should have -- fatal, and handled above.
                # A CLASS IS A COMPARISON RULE. It governs what to do WHEN BOTH SIDES HAVE THE KEY, and
                # has no content when one side cannot have it at all. Demanding PROVENANCE here was
                # demanding that the archive's age be a property of the key's physics.
                uncomparable.append(
                    f"{key}: {cls} -- NOT COMPARABLE on this artifact; the archive predates the writer "
                    f"(landed: {entry['landed']}). Admissible member-only, and NOT verified.")
                continue
            derived = entry["derive"](archive_keys)
            if member_keys[key] != derived:
                findings.append(
                    f"{key}: {cls} -- member {member_keys[key]!r} != archive-derived {derived!r} "
                    f"(landed: {entry['landed']})")
            continue

        if cls is PROVENANCE:
            continue                                       # may differ, and it is present
        if archive_keys[key] != member_keys[key]:
            what = "HARD FAILURE" if cls is CONFIGURATION else "member differs"
            findings.append(
                f"{key}: {cls} {what} -- archive {archive_keys[key]!r} != "
                f"member {member_keys[key]!r}")
        if key in RECOMPUTE_REQUIRED:
            owed.append(
                f"{key}: RECOMPUTATION NOT PERFORMED -- equality alone cannot catch a file whose "
                "scalar disagrees with its own matrix (BEN-077). The comparator must recompute it "
                "from the ingredients in the same file.")
    # THREE VERDICTS, NOT TWO, AND THE THIRD IS THE POINT. A correct k=0 anchor produces no mismatch
    # and still cannot be called PASS, because 9 keys are derived from other keys in the same file and
    # nothing has recomputed them yet. Folding that into FAIL invites the reader to treat a real
    # mismatch and an unfinished comparator as the same state -- and folding it into PASS is worse,
    # because the pressure at stage 1 is toward green. INCOMPLETE cannot be mistaken for either, and it
    # names what is missing rather than how bad it is.
    # UNCOMPARABLE keys are RECORDED, never silent -- "admissible" is not "checked". They do not fail
    # the gate (the archive cannot supply them) and they do not let it claim more than it verified.
    owed = owed + [f"UNCOMPARABLE {u}" for u in uncomparable]
    if findings:
        return "FAIL", findings + owed
    if owed:
        return "INCOMPLETE", owed
    return "PASS", []
