#!/usr/bin/env python3
"""OI-136 ratchet: no tracked `.py` may feed the canonical-root literal into `sys.path.insert(0, …)`.

WHY A RATCHET AND NOT A ONE-TIME SWEEP. An absolute `insert(0, …)` executes THAT tree's modules
whichever checkout launched the entrypoint, and `PYTHONPATH` cannot outrank position 0 — so a
deployment-parity check can report every pinned file CURRENT while the interpreter loads a different
file entirely. That is OI-136's measured cause on run `57266000_0`: 3 h 08 m of A100 against a tree
211 commits behind. A sweep fixes today's instances; only a ratchet stops them growing back.

THE COUNT THIS PINS IS NOT ZERO, AND SAYING SO IS THE POINT. Eight files remain, every one of them
named below with the reason it is still here. A ratchet asserting 0 would have to either fail on
commit or license someone to edit files outside the authorization that produced it.

**THE COUNT MOVED 46 -> 10 ON 2026-09-03 UNDER AN EXPLICIT AUTHORIZATION.** "Eight" above is a
2026-08-23 figure and is left as an as-of referent rather than re-typed; the live number is the
listed set below. Joseph authorized the repair of 36 named sites on 2026-09-03 -- *"I authorize
it"* -- against the request in
`docs/orchestration/INTEGRATION-20260903-wave1-routing-freeze-and-ledger.md` section 7.1, which
asked for exactly this or for a ruling that the guard is the accepted mechanism. Those 36 now
derive their import root from `__file__` and are delisted below, measured not assumed. The
sentence above still holds in its substance: the residual is 10, not 0, and every one of the 10
carries its class.

**HOW THIS COUNTS, because three different numbers have been quoted for it and all three were about
different populations.** On `main`, 2026-08-23:

    111  tracked .py contain the canonical-root literal ANYWHERE
     61  ...AND also call sys.path.insert(0, ...) somewhere    <-- co-occurrence, NOT causation
     15  ...where the literal ACTUALLY REACHES a position-0 insert   <-- what this test counts

The 61 is the number previously circulated as OI-136's "59" and as a 72-file grep upper bound. Both
were right about co-occurrence. **Only the third population is the hazard**, and grep cannot compute
it — reaching requires resolving the argument expression, which is why this walks the AST.

Re-measured on this branch after the 2026-09-03 repair, the same three populations read:

    106  tracked .py contain the canonical-root literal ANYWHERE
     56  ...AND also call sys.path.insert(0, ...)      <-- co-occurrence, still NOT causation
     10  ...where the literal ACTUALLY REACHES a position-0 insert

The first two barely move because 24 of the 36 repaired files KEEP the literal as a DATA root and
so remain in both co-occurrence populations. That divergence is the whole point of counting the
third population separately, and it is why "the literal is gone" is not this repair's claim.

**AN EARLIER VERSION OF THIS SCANNER RETURNED 9, AND 9 WAS WRONG.** It matched the insert argument
with an `elif` chain over `Name` / `Constant` / `JoinedStr` / `BinOp`, so it silently skipped `Call`
arguments — `sys.path.insert(0, os.path.join(_REPO, "x"))` and friends. Six files were invisible.
The argument walk below is deliberately unconditional for that reason: **enumerate the expression,
do not enumerate the shapes you thought of.**
"""
import ast
import pathlib
import subprocess
import unittest

CANONICAL = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
REPO = pathlib.Path(__file__).resolve().parents[2]

# Each entry MUST carry a reason. A bare path list decays into an allowlist nobody revisits.
_R = {
    # MERGE 2026-08-26: both classes below are real and each side recorded the OTHER as pending.
    # The build branch's own words were 'Awaiting merge, not repair.' This is that merge; both
    # strings are retained as history rather than collapsed into one.
    'branch_repaired':
        'REPAIRED on build-k0-execution-integrity by the round-5/6 B-1 sweep and NOT YET on main. Executing correctly on the deployed candidate. Awaiting merge, not repair.',
    'main_repaired':
        "REPAIRED ON main by the 2026-08-23 authorized sweep (c752f73e, a0a84a2e) and NOT YET on this branch. Awaiting merge, not repair. The mirror of this list on main names the six B-1 files repaired HERE and not there -- the two refs are symmetric and each is missing the other's six.",
    'pet':
        "PET lane's file. Not this lane's to edit; routed, not owned.",
    'probe':
        'One-off probe artifact. A probe is a RECORD of what was run; editing it falsifies the record. Retire by classification, never by patching.',
    'twod':
        'THE PUBLISHED 2D ARM. Joseph ruled 2026-08-23 to leave it: reachable in the k=0 static closure but DORMANT -- its insert is inside main(), which the k=0 route never calls, and that dormancy is executed as a test in test_k0_5ab_separated_roots.py rather than asserted. Its sha256 is pinned in three places needing three different treatments; advancing the live one needs a Gate-2 RE-RUN, not a commit.',
    # RETIRED AS AN ACTIVE CLASS 2026-09-03, kept defined as history exactly as the
    # `branch_repaired` key above is. Every file that carried it has either been repaired under
    # Joseph's 2026-09-03 authorization or been re-classified `receipt_bound` below, so the
    # sentence "NEITHER REPAIRED NOR AUTHORIZED" is no longer true of anything and must not be
    # re-attached to a file. The 2026-08-23 scope statement inside it stays accurate about
    # 2026-08-23 and is why it is retained rather than deleted.
    'other_nd':
        'OFF THE k=0 IMPORT CLOSURE. Real, unrepaired, and NEITHER REPAIRED NOR AUTHORIZED -- listed so the count is honest, not because anyone has decided about them. Fixing them was explicitly not authorised on 2026-08-23; the authorisation covered the one file the k=0 route actually executes.',
    'receipt_bound':
        "receipt-bound: verify_hash_bindings.py pins its bytes; needs the binding owner's process. MEASURED, not inferred: editing any one of these five turns that checker's verdict to BINDINGS BROKEN, and the pre-commit hook runs it -- so a repair here cannot land as a code change at all. Joseph's 2026-09-03 authorization covered 36 named sites and deliberately excluded these; advancing a pinned digest is the owning gate's act, not a commit's.",
}

KNOWN_UNREPAIRED = {
    # --- twod: THE PUBLISHED 2D ARM. Joseph ruled 2026-08-23 to leave it: reachable in the k=0 static closure b...
    '2d-unfolding/unfold_2d_omnifold_unbinned.py':
        _R['twod'],
    # --- DELISTED 2026-08-26 BY THE MERGE, and this is the ratchet working, not a check being
    # silenced. Six entries classified _R['branch_repaired'] read 'REPAIRED on
    # build-k0-execution-integrity ... and NOT YET on main'. Merging that branch IS the event
    # that clears them, so test_the_known_set_only_shrinks fired with exactly those six and its
    # message instructed 'delete their entries'. Delisted here, measured not assumed:
    #     nd-unfolding/bootstrap_nd.py            nd-unfolding/unfold_nd_omnifold_unbinned.py
    #     nd-unfolding/seedscan_split.py          nd-unfolding/unified_throw_cov.py
    #     nd-unfolding/sweep_bank_5d.py           nd-unfolding/unified_throw_cov_5d.py
    # KNOWN_UNREPAIRED 52 -> 46, matching the scanner's 46 on the merged tree; and the forward
    # arm measured NEW-unlisted = 0, so nothing was hidden by the delisting. The _R key itself is
    # left defined but unreferenced, as history rather than as an active class.
    # --- DELISTED 2026-09-03 BY THE AUTHORIZED OI-136 ENTRYPOINT REPAIR, and this is again the
    # ratchet working rather than a check being silenced. Authorization: Joseph, 2026-09-03,
    # "I authorize it", against the request in
    # docs/orchestration/INTEGRATION-20260903-wave1-routing-freeze-and-ledger.md section 7.1.
    # 36 sites now derive the root that feeds sys.path.insert(0, ...) from __file__:
    #
    #   nd-unfolding/adopt_unified_4d.py                nd-unfolding/nn_dump_inputs.py
    #   nd-unfolding/build_fps_prior_genie_5d.py        nd-unfolding/pet/d2_oracle.py
    #   nd-unfolding/build_fps_prior_nuwro.py           nd-unfolding/pet/inversion_screen.py
    #   nd-unfolding/build_fps_prior_nuwro_5d.py        nd-unfolding/pet/push_vs_acceptance.py
    #   nd-unfolding/compare_ascencio_fine.py           nd-unfolding/pet_lateral_band.py
    #   nd-unfolding/compare_ascencio_fullcov.py        nd-unfolding/pet_lateral_band_5d.py
    #   nd-unfolding/compare_le_evolution.py            nd-unfolding/pet_lateral_correction.py
    #   nd-unfolding/dump_td_q3.py                      nd-unfolding/pet_systematics.py
    #   nd-unfolding/dump_w_source_fps.py               nd-unfolding/pet_systematics_5d.py
    #   nd-unfolding/eavailW_covariance.py              nd-unfolding/pet_unified_throw_5d.py
    #   nd-unfolding/eavail_generator_significance.py   nd-unfolding/plot_control_corner.py
    #   nd-unfolding/excess_eavail_W.py                 nd-unfolding/project_cov_nd.py
    #   nd-unfolding/fps_3prior_envelope_5d.py          nd-unfolding/q3_excess_projection.py
    #   nd-unfolding/fps_acceptance.py                  nd-unfolding/q3_vs_ascencio_metrics.py
    #   nd-unfolding/fps_extension_validation.py        nd-unfolding/rescale_flux_universes.py
    #   nd-unfolding/fps_gbdt_prior_reunfold_5d.py      nd-unfolding/sweep_bank.py
    #   nd-unfolding/fps_pilot_compare.py               nd-unfolding/unified_throw.py
    #   nd-unfolding/fps_prior_envelope.py
    #   nd-unfolding/make_control_plots.py
    #
    # KNOWN_UNREPAIRED 46 -> 10, matching this scanner's 10 on the repaired tree; the forward arm
    # measured NEW-unlisted = 0, so nothing was hidden by the delisting. THE 36 ARE THE 36, NOT
    # "the rest": three of them (compare_ascencio_fullcov, q3_excess_projection,
    # q3_vs_ascencio_metrics) needed their loop tuple written with os.path.join rather than an
    # f-string, because in those files a local `f = ROOT.TFile.Open(f"{_REPO}/...")` makes the
    # one-letter name `f` rooted and the 08-26 probe's `\bf\b` then matches the `f"` prefix of
    # every f-string, tainting the LOOP VARIABLE. The defect was already gone in all three; the
    # instrument could not see it. Mutation-tested rather than argued: re-planting the literal on
    # the derived assignment in each of the 36 is still CAUGHT by this scanner and by the probe,
    # so the repaired form is not a new blind spot.
    # --- pet: PET lane's file. Not this lane's to edit; routed, not owned....
    # gate2_target_runtime.py is the one file this scanner reports that the 08-26 probe does not:
    # its root is a pathlib `REPO = Path(<literal>)` reaching an insert through a `value` binding
    # the probe's regex does not follow. Outside the 2026-09-03 authorization's 36 named sites and
    # outside the excluded five, so it is neither repaired nor re-classified here.
    'nd-unfolding/pet/gate2_target_runtime.py':
        _R['pet'],
    # --- receipt_bound: verify_hash_bindings.py pins its bytes; needs the binding owner's proc...
    # The five the 2026-09-03 authorization explicitly excluded. `adopt_unified_5d.py` moved here
    # from _R['other_nd']: that class said "NEITHER REPAIRED NOR AUTHORIZED", which understated it
    # -- this file cannot be repaired by a commit at all. It is also the 08-26 probe's surviving
    # positive control, so it must stay in the fail-open set for that probe to be able to report.
    'nd-unfolding/adopt_unified_5d.py':
        _R['receipt_bound'],
    'nd-unfolding/pet/dump_pointcloud_inputs.py':
        _R['receipt_bound'],
    'nd-unfolding/pet/fullevent_fps_dataloader.py':
        _R['receipt_bound'],
    'nd-unfolding/pet/train_fullevent_nominal.py':
        _R['receipt_bound'],
    'nd-unfolding/pet/validate_pet_nominal_gate4.py':
        _R['receipt_bound'],
    # --- probe: One-off probe artifact. A probe is a RECORD of what was run; editing it falsifies the record. Re...
    'docs/orchestration/state/probe-oi120c-loader-purity-perturbation-20260814.py':
        _R['probe'],
    'docs/orchestration/state/probe-oi22-leakage-real-input-20260814.py':
        _R['probe'],
    'docs/orchestration/state/probe-oi22-schema-parity-real-input-20260814.py':
        _R['probe'],
}

def _canonical_form(value):
    """"exact" / "subpath" / None. Bounded at exact-or-separator: a bare startswith would match
    `…/MINERvA-OmniFold-Analysis-Note`, a different repository."""
    if not isinstance(value, str) or not value.startswith(CANONICAL):
        return None
    rest = value[len(CANONICAL):]
    if rest == "":
        return "exact"
    return "subpath" if rest.startswith("/") else None


def _rooted_names(tree):
    """Names bound, at some line, from an expression mentioning a canonical literal or an
    already-rooted name. Returns {name: first line it became rooted}.

    DATAFLOW TO A FIXPOINT, because direct-reference matching is not enough and the miss was live:
    compare_unified_throw.py does
        for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"): sys.path.insert(0, _p)
    so the insert argument is `_p`, never `_REPO`. Three rounds of this scanner called that file
    clean, and the RUNTIME guard caught it when the k=0 rehearsal's legs 5a/5b refused with
    `uq_math resolved to .../MINERvA-OmniFold`. A static check that only follows direct references
    is not a covering question about reachability.

    ORDER IS RECORDED, because ignoring it is wrong in the other direction. An earlier draft marked
    names rooted from assignments occurring AFTER an insert, which flagged unified_throw_cov.py --
    whose root IS derived and whose only canonical literal is a `_DATA_ROOT` declared eight lines
    below the insert. That turned an undercount of 15 into an overcount of 53. Both directions are
    defects; only the overcount is loud.
    """
    bound = {}
    for _ in range(6):
        grew = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                targets, value = node.targets, node.value
            elif isinstance(node, ast.For):
                targets, value = [node.target], node.iter
            else:
                continue
            if value is None:
                continue
            mentions = any(isinstance(x, ast.Constant) and _canonical_form(x.value)
                           for x in ast.walk(value)) or \
                       any(isinstance(x, ast.Name) and x.id in bound
                           for x in ast.walk(value))
            if not mentions:
                continue
            for tgt in targets:
                for nm in ast.walk(tgt):
                    if isinstance(nm, ast.Name) and nm.id not in bound:
                        bound[nm.id] = nm.lineno
                        grew = True
        if not grew:
            break
    return bound


def rooted_insert_files(read):
    """Tracked .py where a canonical-root literal REACHES sys.path.insert(0, ...)."""
    listed = subprocess.run(["git", "-C", str(REPO), "ls-files", "*.py"],
                            capture_output=True, text=True, check=True).stdout.split()
    hazard = []
    for rel in listed:
        try:
            tree = ast.parse(read(rel))
        except (SyntaxError, ValueError, OSError):
            continue
        bound = _rooted_names(tree)
        hit = False
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "insert"):
                continue
            base = node.func.value
            if not (isinstance(base, ast.Attribute) and base.attr == "path"
                    and isinstance(base.value, ast.Name) and base.value.id == "sys"):
                continue
            if not (node.args and isinstance(node.args[0], ast.Constant)
                    and node.args[0].value == 0):
                continue
            arg = node.args[1] if len(node.args) > 1 else None
            if arg is None:
                continue
            if isinstance(arg, ast.Constant) and _canonical_form(arg.value):
                hit = True
                break
            # UNCONDITIONAL over the expression, ORDER-AWARE on the binding: a name taints only an
            # insert at or after the line where that name became rooted.
            if any(isinstance(n, ast.Name) and n.id in bound and node.lineno >= bound[n.id]
                   for n in ast.walk(arg)):
                hit = True
                break
        if hit:
            hazard.append(rel)
    return sorted(hazard)


# THE 2D ARM IS LEFT UNREPAIRED ON PURPOSE, AND THIS IS THE CONDITION THAT MAKES THAT SAFE.
# Joseph ruled 2026-08-23: leave 2d-unfolding/unfold_2d_omnifold_unbinned.py alone rather than
# spend a Gate-2 re-run on it. The reasoning rests on two facts and only one is structural:
#   (1) the insert is inside main() at :1679, so importers do not trigger it -- script runs only;
#   (2) unbinned_unfolding/python/omnifold.py is byte-identical between the canonical checkout's
#       HEAD and main, so even when it fires it loads identical bytes.
# (2) IS AN OBSERVATION ABOUT TODAY and expires silently. Asserted here so the decision returns to
# Joseph at the moment it starts mattering. Do not update the constant to make the test pass.
OMNIFOLD_HELPER = "unbinned_unfolding/python/omnifold.py"
OMNIFOLD_SHA256 = "e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a"


class TheLatencyOfTheUnrepaired2DArmIsAsserted(unittest.TestCase):

    def test_the_omnifold_helper_has_not_moved(self):
        """FIRES when omnifold.py changes -- which converts the 2D hazard from latent to real."""
        import hashlib
        blob = (REPO / OMNIFOLD_HELPER).read_bytes()
        self.assertEqual(hashlib.sha256(blob).hexdigest(), OMNIFOLD_SHA256,
                         f"{OMNIFOLD_HELPER} has changed. The 2D arm's rooted insert at "
                         "unfold_2d_omnifold_unbinned.py:1679 is no longer a no-op: a script run "
                         "from a non-canonical tree now loads DIFFERENT bytes. Joseph's 2026-08-23 "
                         "decision to leave that file unrepaired rested on this digest holding. "
                         "Do not update this constant to make the test pass -- take the decision "
                         "back to him.")

    def test_the_2D_driver_still_confines_its_insert_to_a_function(self):
        """The other half. If the insert reaches module level, every importer is exposed and the
        'only fires as a script' half of the reasoning is void."""
        tree = ast.parse((REPO / "2d-unfolding/unfold_2d_omnifold_unbinned.py")
                         .read_text(encoding="utf-8", errors="replace"))
        spans = [(f.lineno, f.end_lineno) for f in ast.walk(tree)
                 if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))]
        for node in ast.walk(tree):
            if (isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant)
                    and _canonical_form(node.value.value)):
                self.assertTrue(any(a <= node.lineno <= (b or a) for a, b in spans),
                                f"the rooted literal at :{node.lineno} is now at MODULE level; "
                                "every importer of this module is exposed")


class TheCanonicalRootMustNotReachPositionZero(unittest.TestCase):

    def setUp(self):
        self.found = rooted_insert_files(
            lambda rel: (REPO / rel).read_text(encoding="utf-8", errors="replace"))

    def test_no_file_outside_the_named_set_feeds_a_rooted_insert(self):
        """FIRES on a new instance. This is the ratchet."""
        new = [f for f in self.found if f not in KNOWN_UNREPAIRED]
        self.assertEqual(new, [], "a NEW rooted sys.path.insert(0, ...) appeared:\n  " +
                         "\n  ".join(new) + "\nDerive the root from __file__; do not add it here.")

    def test_the_known_set_only_shrinks(self):
        """FIRES when a listed file is repaired but not delisted — so the list cannot rot into an
        allowlist that outlives its reasons."""
        stale = [f for f in KNOWN_UNREPAIRED if f not in self.found]
        self.assertEqual(stale, [], "these are listed as unrepaired but are now clean — delete "
                                    "their entries:\n  " + "\n  ".join(stale))

    def test_every_listed_file_carries_a_reason(self):
        for path, why in KNOWN_UNREPAIRED.items():
            with self.subTest(path=path):
                self.assertGreater(len(why), 40, f"{path} needs a real reason, not a placeholder")

    def test_the_scanner_FIRES_on_a_synthetic_rooted_insert(self):
        """Power. Without this the two arms above pass on a scanner that returns [] for everything."""
        src = f'import sys\n_R = "{CANONICAL}"\nsys.path.insert(0, _R)\n'
        self.assertTrue(rooted_insert_files(lambda rel: src),
                        "scanner found nothing in a file that is nothing but the defect")

    def test_the_scanner_FIRES_through_a_CALL_argument(self):
        """The exact shape the first version of this scanner missed, which made 15 look like 9."""
        src = (f'import os, sys\n_R = "{CANONICAL}"\n'
               'sys.path.insert(0, os.path.join(_R, "nd-unfolding"))\n')
        self.assertTrue(rooted_insert_files(lambda rel: src),
                        "scanner is blind to Call arguments again")

    def test_the_scanner_is_SILENT_on_a_derived_root(self):
        """The repair's own shape. If this fires, the fix reports as the defect."""
        src = ('import sys\nfrom pathlib import Path\n'
               '_R = str(Path(__file__).resolve().parents[1])\nsys.path.insert(0, _R)\n')
        self.assertEqual(rooted_insert_files(lambda rel: src), [])

    def test_the_scanner_is_SILENT_on_a_SIBLING_repository(self):
        """Over-broad is not the safe direction: it would report a hazard in a tree that has none."""
        src = (f'import sys\n_R = "{CANONICAL}-Analysis-Note"\nsys.path.insert(0, _R)\n')
        self.assertEqual(rooted_insert_files(lambda rel: src), [])

    def test_the_scanner_is_SILENT_on_a_rooted_literal_that_never_reaches_an_insert(self):
        """The 61-vs-15 distinction. A literal used as an OUTPUT path is not this hazard, and
        counting it is what produced the '59' and '72' figures."""
        src = (f'import sys\n_OUT = "{CANONICAL}/products"\n'
               'sys.path.insert(0, "/somewhere/else")\nopen(_OUT)\n')
        self.assertEqual(rooted_insert_files(lambda rel: src), [])


if __name__ == "__main__":
    unittest.main()
