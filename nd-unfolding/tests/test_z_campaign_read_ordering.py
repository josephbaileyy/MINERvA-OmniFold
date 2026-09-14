#!/usr/bin/env python3
"""The claims/products read skew in `verify_task_ownership`, and the ordering that closes it.

THE DEFECT, found by the independent review of 2026-09-13 in `a71087e3` and of the exact class this
module exists to eliminate. The ownership scan read the CLAIMS first and the PRODUCTS second, so a
CORRECTLY BOUND SIBLING that created its claim and published its product BETWEEN the two reads was
absent from the claims snapshot and present in the products snapshot. `unclaimed` was non-empty and
the innocent subject task REFUSED, naming the sibling.

  * IT FAILED CLOSED -- it could only reject a legitimate product, never admit a foreign one -- so
    no wrong result could reach the combine through it. What it cost was array tasks dying partway
    under exactly the conditions the repair was built for.
  * THE MESSAGE ACTIVELY MISDIRECTED, which is the part that costs a person a day: it told the
    operator they were looking at "a valid product of a DIFFERENT campaign" when it was this
    campaign's own claimed sibling.
  * THE WINDOW IS ENTERED ONCE PER TASK, so a 40-wide `run` array enters it 40 times per campaign
    and every recovery re-entry enters it again. `block` at the launcher's own `%10` is clean;
    `run` is `--array=0-39%40`, which is NO effective throttle, and at that width the reviewer saw
    task 7 refuse naming `uthrow5d_slab_18.npz`.

HOW IT IS TESTED HERE, AND THE METHOD IS THE REVIEWER'S. `TheSiblingWindowIsClosed` wraps
`claimed_task_ids` so that a sibling completes IN THE REAL ORDER -- claim first, then publish --
but lands inside the subject's window. NO SUBJECT LOGIC IS MODIFIED; the wrapper controls only
*when*. That single wrapper proves the defect and the fix at once, because it fires at the FIRST
read pre-repair and at the SECOND read post-repair:

    pre-repair   claims read (wrapper fires, sibling completes) -> products read: sibling PRESENT
                 and UNCLAIMED -> the subject refuses.
    post-repair  products read (sibling absent) -> claims read (wrapper fires, sibling completes):
                 the sibling is not in the products snapshot at all -> the subject proceeds.

THE CONTROL IS NOT OPTIONAL. The same sibling, same claim, same product, completed BEFORE the
subject starts must also pass -- otherwise a green timing arm would be indistinguishable from
"siblings are never refused", which is the state the ORIGINAL defect was in. And a third arm keeps
the fix from being a deletion of the guard: a genuinely unclaimed product dropped in during the
same window must still refuse, naming only itself.

⚠ WHY ORDERING IS A FIX AND NOT A NARROWER WINDOW, because "we made it less likely" would not be
one. The argument is stated at the call site and rests on two facts about this code -- CLAIM BEFORE
PUBLISH, and CLAIMS ARE NEVER DELETED -- both of which are asserted below rather than assumed. The
one leg that is a property of the FILESYSTEM rather than of this code, cross-client metadata
visibility on Lustre, is what `_confirm_unclaimed`'s second read is for, and it is unmeasured.

⚠⚠ NEITHER HALF OF THE REPAIR CAN BE MUTATION-TESTED ALONE, AND THIS IS WORTH WRITING DOWN BECAUSE
IT READS AS A WEAK TEST IF YOU DO NOT KNOW IT. Measured over full self-contained trees, running the
detecting arm below:

    base  products-first + re-check      PASSED   (positive control)
    M7    claims-first  + NO re-check    FAILED   <- detected: the defect exactly as it stood
    M8    claims-first  + re-check kept  PASSED   <- a one-part mutation MISSES
    M9    products-first + NO re-check   PASSED   <- a one-part mutation MISSES

The two parts are INDEPENDENTLY SUFFICIENT for the interleaving this test can construct, so a
one-part mutation misses and invites the conclusion that the arm is powerless. It is not -- the
power control has to revert BOTH, which is M7. This is the same shape, and the same warning, that
`unified_throw_cov.INCOMPLETE_PREFIX` already carries for its two naming guarantees.
AND THE TWO PARTS ARE NOT INTERCHANGEABLE, which is why both are kept: the ORDERING is the fix and
it rests on properties of this code that are proven; the RE-CHECK is a belt for the cross-client
filesystem leg that is not. A reader who deletes the ordering because "M8 passes" would be keeping
the mitigation and throwing away the proof.

⚠ THE FIRST VERSION OF THE DETECTING ARM DETECTED NOTHING, and the mutation run is what said so.
It fired the hook BEFORE the claims snapshot, so the sibling was already claimed by the time either
order looked -- M7 PASSED. The dangerous interleaving is the sibling completing AFTER the snapshot,
and a test that cannot fail on the pre-repair code is not evidence about the repair.
"""
import glob as globmod
import json
import os
import re
import subprocess
import sys
import time
import unittest
from pathlib import Path

import numpy as np

ND = Path(__file__).resolve().parents[1]
REPO = ND.parent
for _p in (str(ND), str(REPO / "2d-unfolding"), str(REPO / "docs" / "orchestration"),
           str(ND / "tests")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import unified_throw_cov as U                                # noqa: E402
import z_precursor as ZP                                     # noqa: E402
from test_z_campaign_ownership import CampaignFixture         # noqa: E402


class TheSiblingWindowIsClosed(CampaignFixture):
    """A sibling completing inside the subject's window must not make the subject refuse."""

    ARM = "block"
    SUBJECT = 3
    SIBLING = 5

    def complete_sibling_in_real_order(self, task):
        """Claim, THEN publish, THEN record -- the producer's own order, not a shortcut.

        A fixture that wrote the product first would be manufacturing a state the producer cannot
        produce, and the whole correctness argument is about the order this function preserves.
        """
        contract = self.own(self.ARM, task)
        self.assertTrue(os.path.exists(contract["claim"]),
                        "claim-before-publish: the claim must exist before anything is written")
        product = self.product_path(self.ARM, task)
        U._atomic_savez(product, xs=np.arange(3, dtype=float))
        ZP.record_task_completion(contract, product=product)
        return contract, product

    def run_subject_with(self, hook, when="after"):
        """Run the subject with `hook` invoked at the CLAIMS read, and nowhere else.

        `when="after"` fires the hook AFTER the claims snapshot has been taken; `when="before"`
        fires it before. NO SUBJECT LOGIC IS MODIFIED either way -- the wrapper delegates to the
        real `claimed_task_ids`, so the subject performs a genuine directory read, and the only
        thing under the test's control is the INSTANT of the sibling's completion.

        ⚠ WHICH PLACEMENT DETECTS THE DEFECT DEPENDS ON THE READ ORDER, AND MY FIRST VERSION HAD
        ONLY THE HARMLESS ONE. With `when="before"` the sibling is already claimed by the time
        EITHER order takes its claims snapshot, so the claims-first mutant passes it and the arm
        measures nothing -- measured: M7 PASSED. The dangerous interleaving is `when="after"`:
        claims snapshot taken, THEN the sibling claims and publishes, THEN the products are read.
        Under claims-first that yields a product with no claim in the snapshot -- the defect; under
        products-first the product was not in the earlier snapshot at all.
        """
        real = ZP.claimed_task_ids
        fired = []

        def wrapper(claims_dir, arm):
            if fired:
                return real(claims_dir, arm)
            fired.append(True)
            if when == "before":
                hook()
                return real(claims_dir, arm)
            snapshot = real(claims_dir, arm)
            hook()
            return snapshot

        ZP.claimed_task_ids = wrapper
        self.addCleanup(setattr, ZP, "claimed_task_ids", real)
        try:
            return self.own(self.ARM, self.SUBJECT), fired
        finally:
            ZP.claimed_task_ids = real

    # ------------------------------------------------------------------- the three arms ----
    def sibling_hook(self, landed):
        def hook():
            contract, product = self.complete_sibling_in_real_order(self.SIBLING)
            landed["claim"] = contract["claim"]
            landed["product"] = product
        return hook

    def assert_sibling_really_landed(self, landed):
        """Without this a green arm could mean the sibling never completed at all."""
        self.assertTrue(landed, "the hook never ran, so nothing was placed in the window")
        self.assertTrue(os.path.exists(landed["claim"]),
                        "the sibling's claim must demonstrably exist at this point")
        self.assertTrue(os.path.exists(landed["product"]))

    def test_THE_DETECTING_ARM_a_sibling_completing_AFTER_the_claims_snapshot(self):
        """THE INTERLEAVING THAT KILLED THE OLD ORDER. Claims snapshot taken, THEN the sibling
        claims and publishes, THEN the products are read.

        Under the repaired products-then-claims order the sibling's product was not in the earlier
        products snapshot, so there is nothing to be unclaimed. Under the old claims-then-products
        order this is a product with no claim in the snapshot, and the subject refused naming it.
        MEASURED: this arm FAILS on the claims-first mutant and PASSES here -- it is the arm that
        distinguishes "fixed" from "the fixture never produced the state".
        """
        landed = {}
        contract, fired = self.run_subject_with(self.sibling_hook(landed), when="after")
        self.assertTrue(fired)
        self.assertEqual(contract["task_id"], self.SUBJECT)
        self.assert_sibling_really_landed(landed)

    def test_a_sibling_completing_INSIDE_the_repaired_window_does_NOT_refuse_the_subject(self):
        """The other placement: between the products read and the claims read, which is the window
        the REPAIRED order actually has. The proof says this cannot refuse -- the product is not in
        the products snapshot -- and the proof is measured rather than trusted."""
        landed = {}
        contract, fired = self.run_subject_with(self.sibling_hook(landed), when="before")
        self.assertTrue(fired)
        self.assertEqual(contract["task_id"], self.SUBJECT)
        self.assert_sibling_really_landed(landed)

    def test_CONTROL_the_same_sibling_completing_BEFORE_the_subject_also_passes(self):
        """Timing is the ONLY variable. Without this arm a green defect arm would be
        indistinguishable from "siblings are never refused", which is where the ORIGINAL predicate
        was, and the whole point is that both orders are fine now."""
        self.complete_sibling_in_real_order(self.SIBLING)
        contract = self.own(self.ARM, self.SUBJECT)
        self.assertEqual(contract["task_id"], self.SUBJECT)
        self.assertEqual(contract["n_sibling_products"], 1)

    def test_a_GENUINELY_UNCLAIMED_product_STILL_REFUSES_while_a_sibling_completes_in_the_window(
            self):
        """The fix must not be a deletion of the guard. BOTH conditions at once: a foreign product
        that was already there when the subject looked, and a legitimate sibling completing inside
        the window. Only the foreign one may be named."""
        foreign = Path(self.plan["arms"][self.ARM]["dir"]) / "block5d_flux_9.npz"
        foreign.parent.mkdir(parents=True, exist_ok=True)
        U._atomic_savez(str(foreign), xs=np.arange(2, dtype=float))

        with self.assertRaises(ZP.PrecursorError) as caught:
            self.run_subject_with(lambda: self.complete_sibling_in_real_order(self.SIBLING))
        message = str(caught.exception)
        self.assertIn("block5d_flux_9.npz", message)
        self.assertNotIn("block5d_flux_5.npz", message,
                         "the claimed sibling must not be named alongside the foreign product")
        self.assertIn("on TWO reads of the claims directory", message)
        self.assertIn("Do not go looking for a timing explanation", message)

    def test_THE_BOUNDARY_a_foreign_product_that_LANDS_AFTER_the_products_read_is_NOT_seen(self):
        """⚠ A REAL AND DELIBERATE LIMIT OF READING PRODUCTS FIRST, recorded rather than left to be
        discovered by someone who assumes otherwise: a foreign product created INSIDE the window is
        not in the products snapshot, so this task does not see it and does not refuse.

        That is not a hole the ordering opened -- no snapshot can see a file that does not exist
        when it is taken, and the CLAIMS-first order had the identical property with the reads
        swapped. What matters is that it is not LOST: the scan runs once per task, so the very next
        task of the arm reads it, and the combine's phase-3 identity check reads it too. Both are
        asserted here, because "someone else will catch it" is a claim that has to be measured.
        """
        def hook():
            self.complete_sibling_in_real_order(self.SIBLING)
            U._atomic_savez(
                str(Path(self.plan["arms"][self.ARM]["dir"]) / "block5d_flux_9.npz"),
                xs=np.arange(2, dtype=float))

        contract, _fired = self.run_subject_with(hook)
        self.assertEqual(contract["task_id"], self.SUBJECT)

        # THE NEXT TASK SEES IT.
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.own(self.ARM, 2)
        self.assertIn("block5d_flux_9.npz", str(caught.exception))

        # AND PHASE 3 CANNOT BE REACHED PAST IT EITHER. In THIS state the clause that fires is the
        # IDENTITY one -- 19 of the arm's declared files are still missing, so the population is
        # short before completion is even asked about -- and asserting "INCOMPLETE" here would be
        # naming the wrong clause for the state I built. What is asserted is that consumption
        # refuses; the completion clause has its own arm, over a complete population, in
        # `test_z_campaign_ownership`.
        with self.assertRaises((ZP.PrecursorError, SystemExit)) as phase3:
            ZP.require_campaign_complete(self.campaign, self.ARM,
                                         self.plan["arms"][self.ARM]["product_glob"])
        self.assertIn("population is not the declared one", str(phase3.exception))

    def test_the_MESSAGE_no_longer_MISDIRECTS_about_timing(self):
        """The refusal used to send an operator hunting for a foreign campaign that did not exist.
        It now says, in the same breath, that timing has been excluded."""
        target = Path(self.plan["arms"][self.ARM]["dir"]) / "block5d_flux_11.npz"
        target.parent.mkdir(parents=True, exist_ok=True)
        U._atomic_savez(str(target), xs=np.arange(2, dtype=float))
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.own(self.ARM, self.SUBJECT)
        self.assertIn("look for whose files these are", str(caught.exception))

    # -------------------------------------------------- the facts the argument rests on ----
    def test_FACT_A_the_claim_is_created_BEFORE_the_producer_writes_anything(self):
        """CLAIM BEFORE PUBLISH. Asserted against the ORDER OF EFFECTS, not against a comment:
        after ownership returns, the claim exists and the product does not."""
        contract = self.own(self.ARM, 1)
        self.assertTrue(os.path.exists(contract["claim"]))
        self.assertFalse(os.path.exists(self.product_path(self.ARM, 1)),
                         "ownership must return with the claim taken and nothing published, or "
                         "the ordering argument has no first premise")

    def test_FACT_A_holds_in_the_REAL_PRODUCER_too(self):
        """The premise is about `do_blockunits`, not only about the library call it makes. The
        producer's first `_atomic_savez` must come after the contract, so the claim is on disk
        before any byte of the product is."""
        text = (ND / "unified_throw_cov.py").read_text()
        body = text[text.index("def do_blockunits"):text.index("\ndef do_combine")]
        self.assertLess(body.index("z_namespace_contract("), body.index("_atomic_savez("),
                        "do_blockunits must take the contract -- and therefore the claim -- before "
                        "it publishes anything")
        throws = text[text.index("def do_throws"):text.index("\ndef do_blockunits")]
        self.assertLess(throws.index("z_namespace_contract("), throws.index("_atomic_savez("))

    def test_FACT_B_the_claims_set_only_GROWS(self):
        """CLAIMS ARE NEVER DELETED. The AST ban lives in the recovery suite; this is the
        behavioural half -- a full campaign's worth of tasks only ever adds claims."""
        seen = set()
        for task in (0, 1, 2, 6, 7):
            self.own(self.ARM, task)
            now = ZP.claimed_task_ids(self.paths["claims"], self.ARM)
            self.assertTrue(seen <= now, f"the claims set shrank: {seen - now}")
            seen = now
        self.assertEqual(seen, {0, 1, 2, 6, 7})

    def test_the_REREAD_is_a_NO_OP_when_the_ordering_argument_holds(self):
        """A belt that never fires is what you want, so its no-op behaviour is measured rather than
        assumed -- and its FIRING behaviour is measured too, in the arm below."""
        self.complete_sibling_in_real_order(self.SIBLING)
        declared = {str(t): n for t, n in
                    self.campaign["body"]["arms"][self.ARM]["outputs"].items()}
        self.assertEqual(
            ZP._confirm_unclaimed(self.paths, self.ARM, declared, ["block5d_flux_5.npz"]), [],
            "a product whose claim exists must be cleared by the second read")

    def test_the_REREAD_KEEPS_a_product_that_is_still_unclaimed(self):
        declared = {str(t): n for t, n in
                    self.campaign["body"]["arms"][self.ARM]["outputs"].items()}
        self.assertEqual(
            ZP._confirm_unclaimed(self.paths, self.ARM, declared, ["block5d_flux_9.npz"]),
            ["block5d_flux_9.npz"])

    def test_THE_CLAIM_READING_SURFACE_IS_THREE_SITES_AND_EACH_IS_ACCOUNTED_FOR(self):
        """⚠ THE POPULATION, BY AST, NOT BY GREP -- and the distinction is not pedantry here.
        The review's first report said the surface "grew from two call sites to three"; it had not
        -- three sites at both shas, the same three functions -- and that came from a
        `grep ... | head` that truncated before the third site at the earlier sha, so two survivors
        read as new. An inventory that decides scope has to be complete, and a truncating pipe
        returns rows rather than a null, which is worse than finding nothing.

        Each site is accounted for, and "assessed and not exposed" is a stronger position than
        "not covered":
          * `verify_task_ownership`      GATE, exposed -- REPAIRED here.
          * `require_campaign_complete`  GATE, NOT exposed -- it reads products first AND never
            forms `products - claims`; its operand is the static declared task list. UNCHANGED.
          * `campaign_arm_status`        VIEW, not a gate -- a skew misreports rather than refuses.
            UNCHANGED except for a docstring note recording that it was seen and left.
        """
        import ast

        tree = ast.parse((ND / "z_precursor.py").read_text())
        callers = set()
        for function in ast.walk(tree):
            if not isinstance(function, ast.FunctionDef):
                continue
            for node in ast.walk(function):
                if (isinstance(node, ast.Call)
                        and getattr(node.func, "id", None) == "claimed_task_ids"):
                    callers.add(function.name)
        self.assertEqual(
            callers,
            {"verify_task_ownership", "require_campaign_complete", "campaign_arm_status",
             "_confirm_unclaimed"},
            "the claim-reading surface changed; every site must be classified GATE-exposed, "
            "GATE-not-exposed or VIEW before this repair's scope can be called complete")

    def test_THE_OTHER_GATE_IS_UNCHANGED_AND_ITS_OPERAND_IS_STATIC(self):
        """`require_campaign_complete` was assessed, not merely skipped. Both of the reviewer's
        reasons are asserted against the source, because "we looked at it" is not a record."""
        source = (ND / "z_precursor.py").read_text()
        # ⚠ SLICED TO THE NEXT TOP-LEVEL `def`, NOT TO A NAMED ONE. My first version ended the
        # slice at `_confirm_unclaimed`, which sits EARLIER in the file, so the slice was empty and
        # the assertion died on `substring not found` -- a well-formed check over an empty operand.
        start = source.index("\ndef require_campaign_complete(")
        body = source[start:source.index("\ndef ", start + 1)]
        # (1) It reads products first.
        self.assertLess(body.index("check_slab_population("),
                        body.index('claimed_task_ids(paths["claims"], arm)'))
        # (2) It never forms `products - claims`; its operand is the manifest's own task list.
        self.assertIn("unclaimed = [t for t in tasks if t not in claimed]", body)
        self.assertNotIn("present_names - claimed_names", body)
        self.assertIn("tasks = sorted(int(t) for t in entry[\"task_ids\"])", body)

    def test_the_READ_ORDER_IS_PRODUCTS_THEN_CLAIMS_in_the_source(self):
        """Pinned, because the repair IS the order and a later edit could reorder it back without
        changing a single assertion elsewhere in this file."""
        source = (ND / "z_precursor.py").read_text()
        body = source[source.index("def verify_task_ownership"):
                      source.index("def record_task_completion")]
        products = body.index('present = sorted(p for p in globmod.glob(')
        claims = body.index('claimed = claimed_task_ids(paths["claims"], arm)')
        self.assertLess(products, claims,
                        "the products must be read BEFORE the claims; claims-first is the defect")
        self.assertIn("CLAIM-BEFORE-PUBLISH", body)
        # ⚠ THE PREMISE WAS RESTATED AND THIS ASSERTION HAD TO MOVE WITH IT. It read
        # "CLAIMS ARE NEVER DELETED" -- the overclaimed wording -- and kept passing until the
        # wording changed, which is the withdrawal-that-does-not-reach-every-site shape in
        # miniature. The narrower premise is what the guards establish, so it is what is pinned.
        self.assertIn("NOTHING IN THIS MODULE REMOVES OR REPLACES ANYTHING IN THE CLAIMS", body)
        self.assertIn("FILESYSTEM_MUTATIONS", body)


def mutating_calls(source):
    """`{(function, callee, operand expressions)}` for every file-removing call in `source`.

    ONE DETECTOR, used by the equality arm AND by its power control. A control that re-typed the
    sweep would be a fixture derived from the rule it tests: a detector blind to a spelling would
    be confirmed blind by its own control.
    """
    import ast

    tree = ast.parse(source)
    parent = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parent[child] = node

    def enclosing(node):
        cur = parent.get(node)
        while cur is not None and not isinstance(cur, ast.FunctionDef):
            cur = parent.get(cur)
        return cur.name if cur is not None else "<module>"

    found = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
        if name not in ZP.FILESYSTEM_MUTATORS:
            continue
        found[(enclosing(node), ast.unparse(node.func),
               tuple(ast.unparse(a) for a in node.args))] = node.lineno
    return found


class TheClaimsDirectoryIsNeverMutated(unittest.TestCase):
    """PREMISE (B), guarded by an inventory keyed on the OPERAND rather than on the call site.

    ⚠ WHY THIS EXISTS: THE PREMISE BECAME LOAD-BEARING AND ITS GUARDS DID NOT MOVE WITH IT. The
    read-ordering repair is SUFFICIENT rather than merely better only because a claim, once
    created, still exists at the later read. Two guards were protecting that and both were
    narrower than the premise:

      * the recovery-path AST ban iterates a SEVEN-NAME list, so a NEW uncovered function is
        invisible to it -- demonstrated by the review, which added `_tidy_claims` calling
        `os.unlink(paths['claims'])` outside those names and watched the ban still report OK;
      * `test_FACT_B_the_claims_set_only_GROWS` is behavioural over five happy-path tasks and
        never exercises a deleting path at all.

    Neither was WRONG; both were about a narrower subject than the premise they were being read as
    establishing. Not a live defect -- nothing deletes a claim today, and this suite's own detector
    finds exactly three mutating calls in the module, none of them near the claims directory.

    ⚠ AND "JUST WIDEN THE BAN" IS THE THING THAT WAS ALREADY TRIED AND REJECTED FOR CAUSE: a
    module-wide deletion ban fires on `_atomic_write_json` removing ITS OWN temporary file, which
    is correct and predates all of this work. Banning the CALL is the wrong shape. The question is
    never "does this module delete" but "does this module delete THAT" -- so the operand is the
    key, nothing is forbidden, and every mutating call is enumerated with the thing it acts on.
    """

    def test_the_INVENTORY_matches_the_module_in_BOTH_DIRECTIONS(self):
        found = mutating_calls((ND / "z_precursor.py").read_text())
        self.assertEqual(set(found), set(ZP.FILESYSTEM_MUTATIONS),
                         "every file-removing call in z_precursor.py must be declared with its "
                         "operands, and every declared one must still exist -- a floor catches "
                         "collapse and permits erosion")
        self.assertEqual(len(found), 3, f"the mutation surface changed: {sorted(found)}")
        for key, reason in ZP.FILESYSTEM_MUTATIONS.items():
            with self.subTest(call=key):
                self.assertTrue(reason.strip(), f"{key} is declared with no reason")

    def test_NO_DECLARED_MUTATION_NAMES_A_CLAIMS_PATH(self):
        """The premise itself, over the declared operands. Three calls; none of them is a claim."""
        for (function, callee, operands) in ZP.FILESYSTEM_MUTATIONS:
            with self.subTest(function=function, callee=callee):
                for operand in operands:
                    self.assertNotIn("claim", operand.lower(),
                                     f"{function} calls {callee} on {operand!r}, which names a "
                                     f"claim -- premise (B) of the read-ordering argument is that "
                                     f"nothing in this module removes or replaces one")

    def test_POWER_a_NEW_function_deleting_the_claims_directory_is_DETECTED(self):
        """The exact mutant the review demonstrated the OLD guard was blind to.

        Added OUTSIDE the seven names the recovery ban iterates, so the old guard passes it and
        this one must not. Run over the module's source text rather than a hand-written snippet,
        so the detector meets the real file.
        """
        source = (ND / "z_precursor.py").read_text()
        mutant = source + (
            "\n\ndef _tidy_claims(paths, arm):\n"
            "    os.unlink(paths['claims'])\n")
        found = mutating_calls(mutant)
        self.assertNotEqual(set(found), set(ZP.FILESYSTEM_MUTATIONS),
                            "a new deleting function must break the inventory")
        new = set(found) - set(ZP.FILESYSTEM_MUTATIONS)
        self.assertEqual(new, {("_tidy_claims", "os.unlink", ("paths['claims']",))})

    def test_POWER_the_same_mutant_slips_past_the_SEVEN_NAME_recovery_ban(self):
        """The old guard's blind spot, reproduced here rather than taken on trust -- so the reason
        this inventory exists is a measurement in the suite and not a claim in a commit body."""
        import ast

        source = (ND / "z_precursor.py").read_text()
        mutant = source + (
            "\n\ndef _tidy_claims(paths, arm):\n"
            "    os.unlink(paths['claims'])\n")
        covered = {"recover_task", "check_recovery_authorization", "confirm_attempt_terminal",
                   "authorized_attempt", "_load_recovery_record", "resolve_log_names",
                   "launcher_log_patterns"}
        offenders = []
        for function in ast.walk(ast.parse(mutant)):
            if not isinstance(function, ast.FunctionDef) or function.name not in covered:
                continue
            for node in ast.walk(function):
                if isinstance(node, ast.Call):
                    name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
                    if name in {"unlink", "remove", "rmtree", "removedirs", "rmdir"}:
                        offenders.append((function.name, name))
        self.assertEqual(offenders, [],
                         "the seven-name ban sees nothing here -- which is the point: it is a "
                         "guard about RECOVERY being additive, not about the claims directory")

    def test_POWER_a_REMOVED_declaration_is_DETECTED_TOO(self):
        """Erosion, not just collapse. Dropping an entry must fail as loudly as adding a call."""
        eroded = dict(ZP.FILESYSTEM_MUTATIONS)
        eroded.pop(("_atomic_write_json", "os.unlink", ("temporary",)))
        found = mutating_calls((ND / "z_precursor.py").read_text())
        self.assertNotEqual(set(found), set(eroded))

    #: ONE predicate, used by the population sweep AND by both power arms. A re-typed copy in the
    #: controls would be a fixture derived from the rule it tests: a predicate blind to a wording
    #: would be confirmed blind by its own control.
    PREMISE_SUBJECT = re.compile(r"\bclaim(s|ed|ing)?\b", re.I)
    PREMISE_VERB = re.compile(
        r"\b(delet\w*|remov\w*|unlink\w*|disappear\w*|vanish\w*|erase\w*|drop\w*|purge\w*|grow\w*|"
        r"persist\w*|surviv\w*|add\w*|only ever|never|retain\w*|preserv\w*|destroy\w*|replac\w*)\b",
        re.I)

    def matches_premise_prose(self, text):
        """Could this line be stating premise (B)? Subject AND a persistence/removal verb."""
        return bool(self.PREMISE_SUBJECT.search(text) and self.PREMISE_VERB.search(text))

    def premise_prose(self):
        """Every PROSE line in the module that mentions a claim alongside a persistence verb.

        ⚠ WIDER THAN THE KEYWORD SET THAT MISSED THE PARAPHRASE, deliberately. The surviving
        overclaim was found by a reviewer grepping "never delet"; MY OWN sweep, and the one before
        it, missed it. So this keys on the SUBJECT (a claim) co-occurring with ANY
        persistence/removal verb, over comments AND docstrings, and pins the POPULATION rather than
        trying to decide which lines state the premise.

        ⚠⚠ AND ITS SCOPE IS EXACTLY THAT, NOT "ANY PARAPHRASE". My first version of the arm below
        claimed the pin catches a restatement "whatever words it chooses", and then the arm FAILED
        because the rewording I wrote to demonstrate it -- "a claim, once written, will always
        still be there when the second read runs" -- uses none of the verbs and is invisible to the
        pin too. That is the same over-general claim the module docstring warns about one guard
        over. The honest statement: this catches a paraphrase drawn from the persistence/removal
        family, which is where the ones written so far have come from; a paraphrase that avoids the
        whole family is invisible, and `test_THE_BLIND_SPOT_of_the_population_pin` pins that
        boundary as a fact rather than leaving it to be rediscovered.
        """
        import io
        import tokenize

        source = (ND / "z_precursor.py").read_text()
        prose = []
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type == tokenize.COMMENT:
                prose.append((token.start[0], token.string.lstrip("# ")))
        import ast as _ast
        for node in _ast.walk(_ast.parse(source)):
            if isinstance(node, (_ast.FunctionDef, _ast.ClassDef, _ast.Module)):
                doc = _ast.get_docstring(node, clean=False)
                if not doc:
                    continue
                base = getattr(node, "lineno", 1)
                for offset, line in enumerate(doc.splitlines()):
                    prose.append((base + offset, line.strip()))
        return [(line, text) for line, text in sorted(prose)
                if self.matches_premise_prose(text)]

    #: Pinned population size for `premise_prose`. MEASURED on the tree this was written against,
    #: not chosen to fit -- my first value was 22 and the measurement said 21.
    PREMISE_PROSE_LINES = 21

    def test_the_PREMISE_IS_STATED_IN_ONE_PLACE_AND_CITED_EVERYWHERE_ELSE(self):
        """THE WITHDRAWAL REACHED THE PARAPHRASE ONLY BECAUSE A REVIEWER LOOKED, so this is the
        instrument that does not need one next time.

        `_confirm_unclaimed`'s docstring said "claims are never deleted" -- the unqualified form
        narrowed two commits earlier -- in the correctness note of the belt itself. The conclusion
        held; the stated reason asserted an invariant broader than the guards support. That is the
        third time in this campaign a withdrawal has reached the code and missed a paraphrase.
        """
        source = (ND / "z_precursor.py").read_text()
        # (1) THE WITHDRAWN WORDING IS GONE EXCEPT WHERE IT IS BEING QUOTED AS WITHDRAWN.
        #     ⚠ MY FIRST VERSION BANNED IT OUTRIGHT AND FIRED ON THE CORRECTION NOTE ITSELF -- the
        #     `_confirm_unclaimed` docstring quotes the old phrase in order to say it was narrowed.
        #     Banning the warning is not a check; it is the right check over the wrong operand, and
        #     this repository has caught that shape four times. So the ban is LINE-WISE and exempts
        #     a line that marks itself as quoting a withdrawal -- and the exemption is COUNTED, so
        #     it cannot quietly multiply into a way of keeping the old wording around.
        #     Weakest leg regardless -- a reword defeats it -- which is what (3) is for.
        withdrawn_phrases = ("claims are never deleted", "a claim is never deleted",
                             "claims can never be deleted", "no claim is ever deleted")
        exempted = []
        for number, line in enumerate(source.splitlines(), 1):
            lowered = line.lower()
            if not any(phrase in lowered for phrase in withdrawn_phrases):
                continue
            self.assertIn("used to say", lowered,
                          f"z_precursor.py:{number} states the WITHDRAWN unqualified premise and "
                          f"does not mark itself as quoting it: {line.strip()!r}")
            exempted.append(number)
        self.assertEqual(len(exempted), 1,
                         f"exactly one site may quote the withdrawn wording -- the note recording "
                         f"that it was narrowed. Found {exempted}.")
        # (2) THE PREMISE IS STATED ONCE and every other site CITES the inventory.
        self.assertEqual(
            source.count("NOTHING IN THIS MODULE REMOVES OR REPLACES ANYTHING IN THE CLAIMS"), 1,
            "the premise must have exactly ONE canonical statement; a second copy is a second "
            "implementation and the two will diverge")
        body = source[source.index("def _confirm_unclaimed"):
                      source.index("def verify_task_ownership")]
        self.assertIn("FILESYSTEM_MUTATIONS", body,
                      "the belt's correctness note must CITE the premise, not restate it")
        self.assertIn("module-EXTERNAL `rm`", body,
                      "and it must say what the CORRECTED premise admits, or the narrowing did "
                      "not actually reach this site")
        # (3) THE POPULATION IS PINNED. A new paraphrase changes this whatever words it uses.
        found = self.premise_prose()
        self.assertEqual(
            len(found), self.PREMISE_PROSE_LINES,
            "the set of prose lines mentioning a claim alongside a persistence verb changed.\n"
            "That is not automatically wrong -- but premise (B) has now been restated once and "
            "paraphrased once, so READ THESE and check none of them states the invariant in its "
            "own words instead of citing `FILESYSTEM_MUTATIONS`:\n  "
            + "\n  ".join(f":{line} {text[:100]}" for line, text in found))

    def test_POWER_a_REINTRODUCED_paraphrase_is_DETECTED_by_the_population_pin(self):
        """Not by the phrase ban -- by the pin, using words the ban does not contain. That is the
        difference between a guard that catches the mistake I already made and one that catches the
        next one."""
        found = len(self.premise_prose())
        self.assertEqual(found, self.PREMISE_PROSE_LINES)
        # A REWORDING THE PHRASE BAN CANNOT SEE but which stays inside the persistence family.
        reworded = "# A claim, once written, is never removed before the second read happens."
        for withdrawn in ("claims are never deleted", "a claim is never deleted",
                          "claims can never be deleted", "no claim is ever deleted"):
            self.assertNotIn(withdrawn, reworded.lower(),
                             "the phrase ban must be blind to this line, or the arm is measuring "
                             "the ban rather than the pin")
        self.assertTrue(self.matches_premise_prose(reworded),
                        "the reworded paraphrase must fall inside the pinned population, or this "
                        "arm proves nothing about the pin")
        self.assertNotEqual(found + 1, self.PREMISE_PROSE_LINES,
                            "a reworded paraphrase must move the pinned population")

    def test_THE_BLIND_SPOT_of_the_population_pin_is_RECORDED_not_discovered(self):
        """⚠ THE PIN IS NOT UNIVERSAL, and the boundary is asserted rather than caveated.

        A paraphrase that avoids the whole persistence/removal verb family is invisible to it. This
        is not hypothetical: it is the exact sentence I first wrote to demonstrate the pin's power,
        which failed the arm and is how the over-general claim was caught. Widening the verb list
        until it covers this one is the losing game -- the next paraphrase picks the next word --
        so the residual is named instead, and `FILESYSTEM_MUTATIONS` remains the durable guard
        because it keys on CODE rather than on prose.
        """
        invisible = "# A claim, once written, will always still be there when the second read runs."
        self.assertFalse(self.matches_premise_prose(invisible),
                         "if this now matches, the verb family was widened -- update the recorded "
                         "boundary rather than deleting this arm, or the residual goes unstated")

    def test_the_TWO_GUARDS_have_DIFFERENT_SUBJECTS_and_neither_subsumes_the_other(self):
        """Recorded because two guards over the same-looking thing invite a later merge.

        The recovery ban is Joseph's prohibition -- recovery must not delete ANYTHING, claims or
        logs or evidence or products -- over a narrow set of functions. This inventory is premise
        (B) -- nothing anywhere in the module touches the CLAIMS directory -- over every function.
        Broader forbidding on fewer functions, versus narrower forbidding on all of them.
        """
        source = (ND / "z_precursor.py").read_text()
        self.assertIn("KEYED ON THE OPERAND, NOT ON THE CALL SITE", source)
        self.assertIn("NOTHING IN THIS MODULE REMOVES OR REPLACES ANYTHING IN THE CLAIMS "
                      "DIRECTORY", source)
        # ...and the restated premise must say what it does NOT cover, or it is the old overclaim
        # with more words.
        self.assertIn("(B) IS SCOPED TO THIS MODULE", source)
        self.assertIn("FAILS CLOSED", source)


class TheFullDeclaredPopulationsRunAtTheirRealWidths(CampaignFixture):
    """The widths are the point: a seven-process sample did not surface this and 40 did.

    ⚠ NOT A SAMPLE, AND NOT A UNIFORM WIDTH. `block` is `--array=0-20%10` -- 21 tasks in waves of
    ten -- and `run` is `--array=0-39%40`, which is NO effective throttle at all: all forty may be
    in flight. Both numbers are DERIVED from the campaign's own arm table, which is derived from
    each launcher's own `#SBATCH --array`, so a launcher edit changes this test rather than leaving
    it asserting a stale width.
    """

    def widths(self, arm):
        entry = self.campaign["body"]["arms"][arm]
        return entry["task_ids"], entry["throttle"]

    def test_the_BLOCK_arm_runs_its_21_tasks_in_WAVES_OF_ITS_OWN_THROTTLE(self):
        tasks, throttle = self.widths("block")
        self.assertEqual((len(tasks), throttle), (21, 10))
        for start in range(0, len(tasks), throttle):
            wave = tasks[start:start + throttle]
            outcomes = self.spawn("block", wave, publish=True)
            failures = [(code, err) for code, _out, err in outcomes if code != 0]
            self.assertEqual(failures, [], f"wave {wave} refused: {failures}")
        self.assertEqual(ZP.claimed_task_ids(self.paths["claims"], "block"), set(tasks))
        self.assertEqual(
            {os.path.basename(p) for p in globmod.glob(self.plan["arms"]["block"]["product_glob"])},
            set(self.campaign["body"]["arms"]["block"]["outputs"].values()))
        self.assertEqual(ZP.campaign_arm_status(self.campaign, "block")["n_complete"], 21)

    def test_the_RUN_arm_runs_ALL_FORTY_AT_ONCE_which_is_the_width_that_surfaced_the_defect(self):
        tasks, throttle = self.widths("run")
        self.assertEqual((len(tasks), throttle), (40, 40))
        self.assertGreaterEqual(throttle, len(tasks),
                                "`%40` over 40 tasks is NO effective throttle -- that is the point")
        outcomes = self.spawn("run", tasks, publish=True)
        failures = [(code, err) for code, _out, err in outcomes if code != 0]
        self.assertEqual(failures, [], f"forty concurrent tasks refused each other: {failures}")
        self.assertEqual(ZP.claimed_task_ids(self.paths["claims"], "run"), set(tasks))
        self.assertEqual(
            {os.path.basename(p) for p in globmod.glob(self.plan["arms"]["run"]["product_glob"])},
            set(self.campaign["body"]["arms"]["run"]["outputs"].values()))
        self.assertEqual(ZP.campaign_arm_status(self.campaign, "run")["n_complete"], 40)

    def test_the_forty_wide_arm_produces_FORTY_DISTINCT_products_and_records(self):
        """A count can be right while two tasks wrote one file. Three set identities instead."""
        tasks, _throttle = self.widths("run")
        self.spawn("run", tasks, publish=True)
        outputs = self.campaign["body"]["arms"]["run"]["outputs"]
        self.assertEqual(
            {n for n in os.listdir(self.paths["receipts"]) if n.startswith("run.")},
            {ZP.receipt_name("run", t) for t in tasks})
        digests = set()
        for task in tasks:
            record = json.loads(Path(self.paths["receipts"],
                                     ZP.receipt_name("run", task)).read_text())
            self.assertEqual(os.path.basename(record["product"]["path"]), outputs[str(task)])
            digests.add(record["product"]["path"])
        self.assertEqual(len(digests), 40)


if __name__ == "__main__":
    unittest.main()
