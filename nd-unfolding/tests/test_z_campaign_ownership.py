#!/usr/bin/env python3
"""The Z precursor's campaign ownership, tested as ARRAY BEHAVIOUR rather than as single calls.

WHAT THIS SUITE IS FOR. `z_precursor.check_namespace_fresh` is correct for ONE invocation and wrong
for an ARRAY: the contract is enforced per invocation inside the producer while the launcher passes
`--z-namespace-arm` for every task, so in the authorized 21-task block array task 0 writes
`block5d_knobs.npz` and tasks 1-20 glob `block5d_*.npz`, match it, and refuse. A SINGLE-TASK PROBE
PASSED (array index 0, 3.3253 h) because index 0 is the one case that cannot hit it. So the unit
under test here is the composition, and every control below is stated over two or more tasks.

FIVE INTEGRATION CONTROLS, in the order Joseph named them, each with the fault it would catch:

  1. `ASiblingsCompletionDoesNotRefuseTheNextTask` -- a valid task starts AFTER a sibling has
     completed, and succeeds. Catches the defect itself; the pre-repair predicate fails it.
  2. `ConcurrentDistinctTasksDoNotCollide` -- REAL concurrency, `subprocess.Popen` children
     released by one barrier file, never sequential calls asserted to be equivalent. Catches a
     claim or output collision under the `%10` throttle's actual interleaving.
  3. `DuplicatesAndForeignArtifactsRefuse` -- duplicate execution (sequentially AND concurrently),
     a foreign product, a stale undeclared product, an overwrite. Catches a bypass of the thing
     emptiness was standing in for.
  4. `AnIncompletePopulationCannotBeConsumed` -- combination refuses until the exact declared
     population has claimed AND recorded AND published.
  5. `ADelayedTaskKeepsTheSameCampaignIdentity` -- the maintenance case: a task starting long after
     its siblings binds the same campaign digest, code revision, inputs and seeds.

POSITIVE CONTROLS ARE FIRST-CLASS HERE, not an afterthought. A guard that refuses everything passes
every negative arm, so each refusal below is paired with a healthy input that passes SILENTLY, and
`TheGuardsHaveAPositiveControlEach` walks the whole set in one place.

FIXTURES COME FROM THE PRODUCER, NEVER FROM THE PREDICATE UNDER TEST. Products are written by
`unified_throw_cov._atomic_savez`; populations come from `write_block_slabs`, which is built from
`do_blockunits`'s own shape; the A-2(f) record is built by `mnv_source_manifest.build`; the foreign
artifact is a real product of a second, separately initialized campaign -- structurally identical
to `uq_5d/z_probe_20260912/block_slabs_5d/block5d_knobs.npz`, which is the live instance of that
shape and is deliberately left untouched.
"""
import glob as globmod
import json
import os
import re
import subprocess
import sys
import tempfile
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
from test_uq_remediation import _StubbedRoot                 # noqa: E402
from test_z_precursor import (SyntheticBank, combine_args,    # noqa: E402
                             kernel, source_manifest_record, write_block_slabs,
                             write_throw_slabs)

LAUNCHER = {name: ND / Path(rel).name for name, rel in ZP.ARM_LAUNCHERS.items()}


class CampaignFixture(unittest.TestCase):
    """One synthetic bank, one data root and one initialized campaign per test.

    THE ENVIRONMENT IS INJECTED, NOT MUTATED, wherever the unit accepts it: `verify_task_ownership`
    takes `environ`, so the unit-level arms never touch `os.environ` and cannot blame -- or be
    blamed by -- another process sharing it. The integration arms that go through the real producer
    DO have to set `os.environ`, because `enforce_namespace_contract` reads it; those save and
    restore it explicitly.
    """

    ARMS = ("block", "run", "combine")

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.work = Path(self._tmp.name).resolve()
        self.bank = SyntheticBank(self.work)
        self.data_root = self.work / "data"
        self.data_root.mkdir()
        self.srcman = source_manifest_record()
        self.namespace = "zcamp_a"
        started = self.init_campaign(self.namespace)
        self.campaign = started["campaign"]
        self.plan = started["plan"]
        self.paths = started["paths"]

    # -------------------------------------------------------------------------- helpers ----
    def init_campaign(self, namespace, *, data_root=None, arms=None, bank=None):
        """Phase 1, through the real entry point."""
        return ZP.initialize_campaign(
            data_root=str(data_root or self.data_root), namespace=namespace,
            code_root=str(REPO), source_manifest=self.srcman,
            bank=str(bank or self.bank.path), arms=arms or list(self.ARMS),
            label="test", environ={})

    def task_env(self, task_id=None, **extra):
        """The environment a producer task sees: the A-2(f) record and its array task id."""
        env = {ZP.SOURCE_MANIFEST_ENV: self.srcman}
        if task_id is not None:
            env[ZP.ARRAY_TASK_ENV] = str(task_id)
        env.update(extra)
        return env

    def plan_for(self, namespace=None):
        return ZP.namespace_plan(str(self.data_root), namespace=namespace or self.namespace)

    def product_path(self, arm, task_id, namespace=None):
        plan = self.plan_for(namespace)
        campaign = ZP.load_campaign(
            ZP.campaign_paths(str(self.data_root), namespace or self.namespace)["manifest"])
        name = campaign["body"]["arms"][arm]["outputs"][str(task_id)]
        return os.path.join(plan["arms"][arm]["dir"], name)

    def own(self, arm, task_id, *, namespace=None, product=None, bank=None,
            estimator_seed=1000, draw_seed=1000, env=None):
        """Phase 2 for one task, with the environment injected."""
        plan = self.plan_for(namespace)
        return ZP.verify_task_ownership(
            arm=arm, plan=plan,
            product=product if product is not None
            else self.product_path(arm, task_id, namespace),
            bank=str(bank or self.bank.path), estimator_seed=estimator_seed,
            draw_seed=draw_seed,
            environ=self.task_env(task_id) if env is None else env)

    def publish(self, contract, *, units=2):
        """Write the product with the PRODUCER's own atomic publisher, then record completion."""
        product = os.path.join(
            self.plan_for(contract["campaign"]["body"]["namespace"])
            ["arms"][contract["arm"]]["dir"], contract["output"])
        U._atomic_savez(product, xs=np.arange(units, dtype=float),
                        labels=np.array([f"u{i}" for i in range(units)], dtype=object))
        return ZP.record_task_completion(contract, product=product), product

    def run_task(self, arm, task_id, **kw):
        """Ownership then publication: what one array task does, end to end."""
        contract = self.own(arm, task_id, **kw)
        return self.publish(contract)

    def complete_consumed_arms(self):
        """Run every task of every arm the combine consumes, in staggered order.

        The combine cannot take its claim until phase 3 passes over `z_precursor.CONSUMED_ARMS`,
        so any arm exercising the combine's PASSING direction has to bring those populations to
        completion first. That is not fixture overhead -- it is the property under test.
        """
        for arm in ZP.CONSUMED_ARMS["combine"]:
            for task in self.campaign["body"]["arms"][arm]["task_ids"]:
                self.run_task(arm, task)

    def spawn(self, arm, tasks, *, namespace=None, publish=True):
        """Start one REAL child per task, release them together, collect every outcome.

        The barrier is a file the parent creates only after every child has announced itself, so
        the children are provably inside the ownership check concurrently rather than merely
        started in a loop. `ready.*` markers are how the parent knows; a timeout in the child turns
        a hung barrier into a failure instead of a hang.

        `publish=False` keeps the winner from writing its product, which ISOLATES the `O_EXCL`
        clause: with no product on disk every loser must refuse as a DUPLICATE rather than as an
        overwrite. With `publish=True` the winner often publishes before the slowest loser arrives,
        and that loser legitimately meets the overwrite clause first -- measured, and the reason
        the two arms exist separately.
        """
        script = self.work / "campaign_child.py"
        if not script.exists():
            script.write_text(_CHILD.format(nd=str(ND), two_d=str(REPO / "2d-unfolding")),
                              encoding="utf-8")
        tag = f"{arm}_{'-'.join(str(t) for t in tasks)}_{int(publish)}"
        barrier = self.work / f"go_{tag}"
        env = dict(os.environ)
        env["MNV_SOURCE_MANIFEST"] = self.srcman
        env.pop("MNV_EST_SEED_OFFSET", None)
        children = [subprocess.Popen(
            [sys.executable, str(script), arm, str(task), str(self.data_root),
             namespace or self.namespace, str(self.bank.path), str(barrier),
             "1" if publish else "0"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
            for task in tasks]
        deadline = time.time() + 180
        pattern = f"{barrier}.ready.*"
        while len(globmod.glob(pattern)) < len(children) and time.time() < deadline:
            time.sleep(0.01)
        self.assertEqual(len(globmod.glob(pattern)), len(children),
                         "not every child reached the barrier; the concurrency claim would be "
                         "about a population that never assembled")
        barrier.write_text("go", encoding="utf-8")
        return [(child.wait(timeout=240), *child.communicate()) for child in children]


# ============================================== CONTROL 1: a sibling's completion is permitted ==
class ASiblingsCompletionDoesNotRefuseTheNextTask(CampaignFixture):
    """CONTROL 1. A valid task starts after a sibling has completed, and SUCCEEDS.

    This is the defect itself, as an executable statement. `test_the_PRE_REPAIR_predicate_FAILS_
    control_1` is the power control: it runs the retired predicate over the same state and shows it
    refusing, so a green control 1 is evidence that something changed rather than evidence that the
    fixture is too weak to provoke anything.
    """

    def test_task_1_SUCCEEDS_after_task_0_has_published_and_recorded(self):
        self.run_task("block", 0)
        contract = self.own("block", 1)
        self.assertEqual(contract["output"], "block5d_flux_1.npz")
        self.assertEqual(contract["n_sibling_products"], 1)
        self.assertEqual(contract["n_sibling_claims"], 1)

    def test_the_WHOLE_21_TASK_BLOCK_ARRAY_completes_STAGGERED(self):
        """Every task of the real declared population, in order, each starting after the last one
        finished. The population is DERIVED from the launcher's own `--array=0-20%10`."""
        declared = self.campaign["body"]["arms"]["block"]
        self.assertEqual(declared["n_tasks"], 21)
        self.assertEqual(declared["array_spec"], "0-20%10")
        for task in declared["task_ids"]:
            self.run_task("block", task)
        products = sorted(os.path.basename(p) for p in globmod.glob(
            self.plan["arms"]["block"]["product_glob"]))
        self.assertEqual(products, sorted(declared["outputs"].values()))
        self.assertEqual(len(ZP.claimed_task_ids(self.paths["claims"], "block")), 21)
        status = ZP.campaign_arm_status(self.campaign, "block")
        self.assertEqual(status["n_complete"], 21)

    def test_the_40_TASK_RUN_ARRAY_completes_STAGGERED_too(self):
        """The other array arm, whose shape is identical and whose population is 40."""
        declared = self.campaign["body"]["arms"]["run"]
        self.assertEqual((declared["n_tasks"], declared["array_spec"]), (40, "0-39%40"))
        for task in declared["task_ids"]:
            self.run_task("run", task)
        self.assertEqual(ZP.campaign_arm_status(self.campaign, "run")["n_complete"], 40)

    def test_POWER_the_PRE_REPAIR_predicate_FAILS_control_1(self):
        """The retired per-invocation predicate, run over the SAME state control 1 passes.

        `check_namespace_fresh` is still live -- it is what `initialize_campaign` uses -- so this
        is not a reconstruction: it is the same function, at the same call site's operand, showing
        why it cannot be the task-level predicate. Without this arm a passing control 1 could mean
        the fixture never produced the state that used to refuse.
        """
        self.run_task("block", 0)
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.check_namespace_fresh(self.plan, ["block"])
        self.assertIn("NOT FRESH", str(caught.exception))
        self.assertIn("block5d_knobs.npz", str(caught.exception))
        # ...and the ownership predicate passes on that exact state, which is the repair.
        self.assertEqual(self.own("block", 1)["task_id"], 1)


# ================================================ CONTROL 2: real concurrency, no collisions ====
#: The child of control 2 and of the concurrent duplicate arm. A REAL interpreter, started as a
#: real process, released by a barrier FILE so that all children are inside the ownership check at
#: the same time. Threads would share one interpreter and one `os` module and could not exercise
#: `O_EXCL` against a different process at all; sequential calls asserted to be equivalent would be
#: the claim this control exists to avoid making.
_CHILD = r'''
import json, os, sys, time
sys.path.insert(0, {nd!r})
sys.path.insert(0, {two_d!r})
import numpy as np
import unified_throw_cov as U
import z_precursor as ZP

arm, task, data_root, namespace, bank, barrier, publish = sys.argv[1:8]
plan = ZP.namespace_plan(data_root, namespace=namespace)
campaign = ZP.load_campaign(ZP.campaign_paths(data_root, namespace)["manifest"])
# A task the campaign does not declare has no declared basename, so the child SYNTHESIZES one in
# the arm's own layout. Resolving it out of the manifest instead would make the child die with a
# KeyError before reaching the guard -- a refusal the guard never issued, reported as if it had.
outputs = campaign["body"]["arms"][arm]["outputs"]
name = outputs.get(task) or "block5d_flux_" + task + ".npz"
product = os.path.join(plan["arms"][arm]["dir"], name)
env = {{ZP.SOURCE_MANIFEST_ENV: os.environ["MNV_SOURCE_MANIFEST"],
        ZP.ARRAY_TASK_ENV: task}}
open(barrier + ".ready." + arm + "." + task + "." + str(os.getpid()), "w").close()
deadline = time.time() + 120
while not os.path.exists(barrier):
    if time.time() > deadline:
        print("BARRIER-TIMEOUT", file=sys.stderr)
        sys.exit(4)
    time.sleep(0.005)
try:
    contract = ZP.verify_task_ownership(arm=arm, plan=plan, product=product, bank=bank,
                                        estimator_seed=1000, draw_seed=1000, environ=env)
except ZP.PrecursorError as exc:
    print("REFUSED: " + str(exc), file=sys.stderr)
    sys.exit(2)
if publish == "1":
    U._atomic_savez(product, xs=np.arange(3, dtype=float))
    ZP.record_task_completion(contract, product=product)
print("OWNED " + arm + " " + task + " " + os.path.basename(contract["claim"]))
'''


class ConcurrentDistinctTasksDoNotCollide(CampaignFixture):
    """CONTROL 2. Distinct tasks running AT THE SAME TIME all succeed, with no collision."""

    def test_SEVEN_CONCURRENT_DISTINCT_block_tasks_ALL_SUCCEED(self):
        tasks = [0, 1, 2, 3, 4, 5, 6]
        outcomes = self.spawn("block", tasks)
        failures = [(code, out, err) for code, out, err in outcomes if code != 0]
        self.assertEqual(failures, [], f"concurrent distinct tasks refused each other: {failures}")
        expected = {self.campaign["body"]["arms"]["block"]["outputs"][str(t)] for t in tasks}
        # NO COLLISION, stated as three independent set identities rather than as a count: a count
        # can be right while two tasks wrote one file and a third wrote nothing.
        self.assertEqual({os.path.basename(p) for p in globmod.glob(
            self.plan["arms"]["block"]["product_glob"])}, expected)
        self.assertEqual(ZP.claimed_task_ids(self.paths["claims"], "block"), set(tasks))
        self.assertEqual(
            {n for n in os.listdir(self.paths["receipts"]) if n.startswith("block.")},
            {ZP.receipt_name("block", t) for t in tasks})

    def test_the_products_are_DISTINCT_FILES_with_distinct_content(self):
        """A collision that left one file per task but the same bytes in each would pass a
        name-only check. The products are compared by digest as well as by name."""
        self.spawn("block", [1, 2, 3])
        paths = sorted(globmod.glob(self.plan["arms"]["block"]["product_glob"]))
        self.assertEqual(len(paths), 3)
        for path in paths:
            with np.load(path, allow_pickle=True) as handle:
                self.assertIn("xs", handle.files)
        receipts = [json.loads(Path(self.paths["receipts"], ZP.receipt_name("block", t))
                               .read_text()) for t in (1, 2, 3)]
        self.assertEqual(len({r["product"]["path"] for r in receipts}), 3)
        self.assertEqual({r["extra"]["campaign_digest"] for r in receipts},
                         {self.campaign["campaign_digest"]})

    def test_POSITIVE_CONTROL_the_concurrent_children_are_capable_of_refusing(self):
        """The children of control 2 must be able to fail, or control 2 proves nothing about them.

        Same script, same barrier, one task id that the campaign does not declare: every child
        refuses. Without this arm a child that silently exited 0 on any input would make control 2
        vacuous.
        """
        outcomes = self.spawn("block", [99, 100])
        self.assertTrue(all(code != 0 for code, _out, _err in outcomes))
        self.assertTrue(all("not a declared task" in err for _c, _o, err in outcomes),
                        [err for _c, _o, err in outcomes])


# ================================ CONTROL 3: duplicates and foreign artifacts refuse ============
class DuplicatesAndForeignArtifactsRefuse(CampaignFixture):
    """CONTROL 3. Duplicate execution, foreign products, stale products and overwrites.

    THE THREE REFUSALS ARE CHECKED AS THREE DISTINCT FINDINGS, not as three non-zero exits. A
    mutation aimed at the overwrite guard that is refused first by the foreign scan -- with the
    same exception type -- is an untested guard reported as a proven one, so each arm asserts the
    message that only its own clause produces, and `test_the_three_refusals_are_DISTINGUISHABLE`
    pins that they cannot be confused for one another.
    """

    def test_a_DUPLICATE_task_refuses_SEQUENTIALLY_after_publishing(self):
        self.run_task("block", 4)
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.own("block", 4)
        self.assertIn("ALREADY EXISTS", str(caught.exception))

    def test_a_DUPLICATE_task_refuses_when_the_first_attempt_NEVER_PUBLISHED(self):
        """The mid-run duplicate, which is the state the `%10` race produced. The first attempt
        holds a claim and no product; the old predicate passed BOTH attempts here."""
        self.own("block", 5)
        self.assertFalse(os.path.exists(self.product_path("block", 5)))
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.own("block", 5)
        self.assertIn("DUPLICATE EXECUTION", str(caught.exception))

    def test_CONCURRENT_duplicates_of_ONE_task_leave_EXACTLY_ONE_winner(self):
        """Real processes, one task id, one `O_EXCL` create. THIS is the exclusivity claim.

        Publication is switched OFF so the clause under test is isolated. With it on, the winner
        usually publishes before the slowest loser arrives and that loser meets the overwrite
        clause instead -- a correct refusal from a different guard, which would make this arm pass
        while proving nothing about `O_EXCL`. Measured, not anticipated: the first version of this
        test failed exactly that way.
        """
        outcomes = self.spawn("block", [3] * 6, publish=False)
        codes = [code for code, _out, _err in outcomes]
        self.assertEqual(codes.count(0), 1, f"exactly one attempt may win the claim: {outcomes}")
        losers = [err for code, _out, err in outcomes if code != 0]
        self.assertEqual(len(losers), 5)
        for err in losers:
            self.assertIn("DUPLICATE EXECUTION", err)
        self.assertEqual(ZP.claimed_task_ids(self.paths["claims"], "block"), {3})

    def test_CONCURRENT_duplicates_that_DO_publish_still_leave_ONE_winner(self):
        """The same race with publication on: still exactly one winner, and every loser refuses --
        as a duplicate or as an overwrite, depending on whether the winner had published yet. Both
        are correct findings; what is asserted here is that no second attempt ever proceeds."""
        outcomes = self.spawn("block", [4] * 6, publish=True)
        codes = [code for code, _out, _err in outcomes]
        self.assertEqual(codes.count(0), 1, f"exactly one attempt may proceed: {outcomes}")
        for code, _out, err in outcomes:
            if code != 0:
                self.assertTrue("DUPLICATE EXECUTION" in err or "ALREADY EXISTS" in err, err)
        self.assertEqual(len(globmod.glob(self.plan["arms"]["block"]["product_glob"])), 1)

    def test_a_FOREIGN_product_of_ANOTHER_CAMPAIGN_refuses(self):
        """The probe's shape, manufactured from the producer rather than described.

        A second campaign is initialized in its own namespace and runs its own task 0. Its product
        is a REAL, VALID `block5d_knobs.npz` -- at a basename campaign A also declares -- and
        moving it into campaign A's arm directory is exactly the state
        `uq_5d/z_probe_20260912/block_slabs_5d/block5d_knobs.npz` is in with respect to any new
        campaign. The identity check alone PASSES it: the basename is declared.
        """
        other = self.init_campaign("zcamp_b")
        other_plan, other_campaign = other["plan"], other["campaign"]
        foreign_contract = ZP.verify_task_ownership(
            arm="block", plan=other_plan,
            product=os.path.join(other_plan["arms"]["block"]["dir"], "block5d_knobs.npz"),
            bank=str(self.bank.path), estimator_seed=1000, draw_seed=1000,
            environ=self.task_env(0))
        self.assertNotEqual(other_campaign["campaign_digest"],
                            self.campaign["campaign_digest"])
        _receipt, foreign_product = self.publish(foreign_contract)
        landed = Path(self.plan["arms"]["block"]["dir"]) / "block5d_knobs.npz"
        landed.parent.mkdir(parents=True, exist_ok=True)
        landed.write_bytes(Path(foreign_product).read_bytes())
        # The basename IS declared, so a name-only check sees nothing wrong -- asserted, so the
        # claim that identity cannot close this is measured here and not argued.
        self.assertIn(landed.name, set(
            self.campaign["body"]["arms"]["block"]["outputs"].values()))
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.own("block", 1)
        message = str(caught.exception)
        self.assertIn("no task of this campaign has CLAIMED", message)
        self.assertIn("block5d_knobs.npz", message)

    def test_a_STALE_UNDECLARED_product_refuses_and_NAMES_it(self):
        target = Path(self.plan["arms"]["block"]["dir"])
        target.mkdir(parents=True, exist_ok=True)
        U._atomic_savez(str(target / "block5d_flux_44.npz"), xs=np.arange(2, dtype=float))
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.own("block", 1)
        self.assertIn("never declared", str(caught.exception))
        self.assertIn("block5d_flux_44.npz", str(caught.exception))

    def test_a_task_writing_a_SIBLINGS_basename_refuses(self):
        """The overwrite that ownership exists to stop: task 2 invoked with task 3's `--out`."""
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.own("block", 2, product=self.product_path("block", 3))
        self.assertIn("owns 'block5d_flux_2.npz'", str(caught.exception))
        self.assertIn("would destroy that sibling's output", str(caught.exception))

    def test_a_product_written_OUTSIDE_the_arm_directory_refuses(self):
        elsewhere = self.work / "elsewhere" / "block5d_flux_2.npz"
        elsewhere.parent.mkdir(parents=True, exist_ok=True)
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.own("block", 2, product=str(elsewhere))
        self.assertIn("is not the campaign's arm directory", str(caught.exception))

    def test_the_three_refusals_are_DISTINGUISHABLE(self):
        """FOREIGN, OVERWRITE and DUPLICATE are three states of (claim present?, product present?)
        and each must produce its own finding. One message that half-fits all three would send the
        reader after the wrong action, and would let a mutation aimed at one be absorbed by another.
        """
        messages = {}
        # (claim absent, product present) -> FOREIGN
        target = Path(self.plan["arms"]["block"]["dir"])
        target.mkdir(parents=True, exist_ok=True)
        U._atomic_savez(str(target / "block5d_flux_7.npz"), xs=np.arange(2, dtype=float))
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.own("block", 7)
        messages["foreign"] = str(caught.exception)
        os.unlink(str(target / "block5d_flux_7.npz"))
        # (claim present, product absent) -> DUPLICATE
        self.own("block", 8)
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.own("block", 8)
        messages["duplicate"] = str(caught.exception)
        # (claim present, product present) -> OVERWRITE / already ran
        self.run_task("block", 9)
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.own("block", 9)
        messages["overwrite"] = str(caught.exception)
        self.assertIn("has CLAIMED", messages["foreign"])
        self.assertIn("DUPLICATE EXECUTION", messages["duplicate"])
        self.assertIn("ALREADY EXISTS", messages["overwrite"])
        self.assertNotIn("DUPLICATE EXECUTION", messages["foreign"])
        self.assertNotIn("DUPLICATE EXECUTION", messages["overwrite"])
        self.assertNotIn("ALREADY EXISTS", messages["duplicate"])

    def test_an_INCOMPLETE_WRITE_is_not_read_as_a_foreign_product(self):
        """A killed sibling leaves a temp, and a temp is not an artifact. The predicate is
        IMPORTED from the producer, so the two spellings cannot drift apart."""
        target = Path(self.plan["arms"]["block"]["dir"])
        target.mkdir(parents=True, exist_ok=True)
        temp = target / U.incomplete_name("block5d_flux_3.npz", "tok")
        temp.write_bytes(b"PARTIAL")
        self.assertTrue(U.is_incomplete_write(temp.name))
        self.assertEqual(self.own("block", 1)["task_id"], 1)

    def test_an_UNCLAIMED_CAMPAIGN_claims_directory_REFUSES_rather_than_reading_EMPTY(self):
        """A could-not-look is not a clean result. If this returned an empty set, every present
        product would read as unclaimed -- and a duplicate would find no claim to collide with."""
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.claimed_task_ids(str(self.work / "no-such-claims-dir"), "block")
        self.assertIn("could not look", str(caught.exception))


# ================================== CONTROL 4: an incomplete population cannot be consumed ======
class AnIncompletePopulationCannotBeConsumed(CampaignFixture):
    """CONTROL 4. Combination requires the exact completed population and its bindings."""

    def stage(self, *, skip_tasks=(), skip_records=()):
        """Populate both consumed arms, optionally leaving gaps of two different kinds."""
        for arm, tasks in (("block", self.campaign["body"]["arms"]["block"]["task_ids"]),
                           ("run", self.campaign["body"]["arms"]["run"]["task_ids"])):
            for task in tasks:
                if (arm, task) in skip_tasks:
                    continue
                contract = self.own(arm, task)
                if (arm, task) in skip_records:
                    # PUBLISHED BUT NEVER RECORDED: the state a wall-clock kill leaves, because
                    # `do_blockunits` publishes after every unit. The file is present and loads.
                    product = self.product_path(arm, task)
                    U._atomic_savez(product, xs=np.arange(2, dtype=float))
                    continue
                self.publish(contract)

    def test_POSITIVE_CONTROL_the_COMPLETE_population_passes_SILENTLY(self):
        self.stage()
        for arm in ("block", "run"):
            result = ZP.require_campaign_complete(
                self.campaign, arm, self.plan["arms"][arm]["product_glob"])
            self.assertEqual(result["n_tasks"],
                             self.campaign["body"]["arms"][arm]["n_tasks"])
            self.assertEqual(len(result["bindings"]), result["n_tasks"])

    def test_a_MISSING_task_refuses_and_the_refusal_names_the_FILE(self):
        self.stage(skip_tasks={("block", 13)})
        with self.assertRaises(SystemExit) as caught:
            ZP.require_campaign_complete(self.campaign, "block",
                                         self.plan["arms"]["block"]["product_glob"])
        self.assertIn("block5d_flux_13.npz", str(caught.exception))
        self.assertIn("MISSING", str(caught.exception))

    def test_a_PUBLISHED_but_UNRECORDED_task_refuses_even_though_the_GLOB_IS_COMPLETE(self):
        """The state identity alone cannot see: every declared file present, one task never
        finished. A short slab at the declared name loads cleanly and passes every content check.
        """
        self.stage(skip_records={("block", 14)})
        present = {os.path.basename(p) for p in globmod.glob(
            self.plan["arms"]["block"]["product_glob"])}
        self.assertEqual(present, set(self.campaign["body"]["arms"]["block"]["outputs"].values()),
                         "the glob population must be COMPLETE, or this arm is testing the "
                         "identity check instead of the completion check")
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.require_campaign_complete(self.campaign, "block",
                                         self.plan["arms"]["block"]["product_glob"])
        self.assertIn("INCOMPLETE", str(caught.exception))
        self.assertIn("never recorded a completion", str(caught.exception))
        self.assertIn("14", str(caught.exception))

    def test_a_completion_record_whose_PRODUCT_CHANGED_refuses(self):
        """A binding is re-read from disk, never trusted from the record."""
        self.stage()
        product = self.product_path("block", 2)
        U._atomic_savez(product, xs=np.arange(99, dtype=float))
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.require_campaign_complete(self.campaign, "block",
                                         self.plan["arms"]["block"]["product_glob"])
        self.assertIn("CHANGED since it was measured", str(caught.exception))

    def test_a_completion_record_bound_to_ANOTHER_CAMPAIGN_refuses(self):
        """A foreign record is a foreign artifact however internally correct it is."""
        self.stage()
        path = Path(self.paths["receipts"], ZP.receipt_name("block", 6))
        receipt = json.loads(path.read_text())
        receipt["extra"]["campaign_digest"] = "0" * 64
        path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.require_campaign_complete(self.campaign, "block",
                                         self.plan["arms"]["block"]["product_glob"])
        self.assertIn("binds campaign", str(caught.exception))

    def test_the_REAL_do_combine_REFUSES_an_incomplete_campaign_and_ACCEPTS_a_complete_one(self):
        """Through the producer, not through the gate alone, and in BOTH directions.

        `do_combine` is where the gate is wired, and a gate that exists but is not called is the
        `OI-64` shape. Both arms run against the same fixture so the difference is the population
        and not the setup.
        """
        saved = dict(os.environ)
        os.environ[ZP.NAMESPACE_ENV] = self.namespace
        os.environ["MNV_DATA_ROOT"] = str(self.data_root)
        os.environ[ZP.SOURCE_MANIFEST_ENV] = self.srcman
        os.environ.pop("MNV_EST_SEED_OFFSET", None)
        os.environ.pop(ZP.ARRAY_TASK_ENV, None)
        self.addCleanup(lambda: (os.environ.clear(), os.environ.update(saved)))
        saved_kernel = U._xsec_for_weights
        U._xsec_for_weights = kernel()
        self.addCleanup(setattr, U, "_xsec_for_weights", saved_kernel)

        run_dir = Path(self.plan["arms"]["run"]["dir"])
        block_dir = Path(self.plan["arms"]["block"]["dir"])
        out = Path(self.plan["arms"]["combine"]["dir"]) / "unified_throw_cov_5d.root"
        # THE COMBINE'S OWN COMPLETION RECORD IS RECORDED RATHER THAN WRITTEN, FOR THIS TEST ONLY,
        # AND THE CALL IS STILL ASSERTED. `_StubbedRoot` stands in for `TFile`, so nothing lands at
        # `out` and the real `record_task_completion` correctly refuses an absent product -- which
        # is the subject of `TheGuardsHaveAPositiveControlEach::test_a_completion_record_REFUSES_
        # before_the_product_exists`, not of this one. Here the subject is the phase-3 gate, so the
        # recorder proves the call site runs while leaving the gate's two directions readable.
        recorded = []
        saved_recorder = U.z_record_completion
        U.z_record_completion = lambda contract, product: recorded.append((contract, product))
        self.addCleanup(setattr, U, "z_record_completion", saved_recorder)

        def combine():
            args = combine_args(bank=str(self.bank.path),
                                combine=str(run_dir / "uthrow5d_slab_*.npz"),
                                block_slabs=str(block_dir / "block5d_*.npz"),
                                expected_throws="0-159", out_root=str(out),
                                z_namespace_arm="combine")
            with _StubbedRoot() as rec:
                return U.do_combine(args), rec

        # THE SLABS ARE PRODUCED INTO A STAGING DIRECTORY, NOT INTO THE ARM DIRECTORY, and the
        # order is a finding rather than a convenience -- measured when the first version of this
        # test wrote all 40 slabs into the arm directory and then claimed them one at a time. The
        # other 39 were then present and UNCLAIMED, which IS the foreign-artifact state, and the
        # ownership check refused -- correctly. A staggered array never produces that state: a
        # product appears only after its own task has claimed it. So the producer's OWN content is
        # staged aside (re-writing the slabs here would make the fixture agree with my code about
        # content) and each file is moved in only after its task holds the claim.
        staged_run, staged_block = self.work / "staged-run", self.work / "staged-block"
        write_throw_slabs(staged_run, n_slabs=40, per=4)
        write_block_slabs(staged_block)

        # (1) The slabs are all there in the producer's own shape, and no task ever claimed them.
        for source, destination in ((staged_run, run_dir), (staged_block, block_dir)):
            destination.mkdir(parents=True, exist_ok=True)
            for path in sorted(source.glob("*.npz")):
                (destination / path.name).write_bytes(path.read_bytes())
        with self.assertRaises(ZP.PrecursorError) as caught:
            combine()
        self.assertIn("INCOMPLETE", str(caught.exception))
        for destination in (run_dir, block_dir):
            for path in sorted(destination.glob("*.npz")):
                os.unlink(path)

        # (2) The same populations, claimed first and moved in second, pass.
        for arm, source in (("run", staged_run), ("block", staged_block)):
            for task in self.campaign["body"]["arms"][arm]["task_ids"]:
                contract = self.own(arm, task)
                product = Path(self.product_path(arm, task))
                product.write_bytes((source / contract["output"]).read_bytes())
                ZP.record_task_completion(contract, product=str(product))
        result, _rec = combine()
        self.assertTrue(result["throw_population_declared"])
        self.assertTrue(result["block_population_declared"])
        self.assertEqual(len(recorded), 1,
                         "the combine's claim must be closed by a completion record at the end")


# ============================ CONTROL 5: a delayed task keeps the campaign's identity ===========
class ADelayedTaskKeepsTheSameCampaignIdentity(CampaignFixture):
    """CONTROL 5. The maintenance case: a task starting long after its siblings.

    "A week later" is not simulated with a clock. What makes a delayed task different is that the
    world moved: siblings finished, the manifest has been read and re-read, and nothing about this
    task's bindings may have drifted. So the arms below assert IDENTITY of the bound values across
    the gap, and the two negative arms move the code revision and the inputs under the campaign to
    show the binding is load-bearing rather than recorded.
    """

    def test_a_task_run_LAST_binds_the_SAME_campaign_as_the_task_run_FIRST(self):
        first, _p = self.run_task("block", 0)
        for task in (1, 2, 3):
            self.run_task("block", task)
        last, _p = self.run_task("block", 20)
        self.assertEqual(first["extra"]["campaign_digest"], last["extra"]["campaign_digest"])
        self.assertEqual(first["extra"]["code_listing_sha256"],
                         last["extra"]["code_listing_sha256"])
        self.assertEqual(first["extra"]["bank_cv_sha256"], last["extra"]["bank_cv_sha256"])
        self.assertEqual(first["extra"]["bank_listing_sha256"],
                         last["extra"]["bank_listing_sha256"])
        self.assertEqual(first["namespace"], last["namespace"])

    def test_the_MANIFEST_is_BYTE_IDENTICAL_after_the_whole_arm_has_run(self):
        """An immutable manifest is immutable in fact, not by intention: the tasks write claims and
        receipts into `_campaign/`, and none of them touches the manifest."""
        before = Path(self.paths["manifest"]).read_bytes()
        for task in self.campaign["body"]["arms"]["block"]["task_ids"]:
            self.run_task("block", task)
        self.assertEqual(Path(self.paths["manifest"]).read_bytes(), before)
        reloaded = ZP.load_campaign(self.paths["manifest"])
        self.assertEqual(reloaded["campaign_digest"], self.campaign["campaign_digest"])
        self.assertEqual(reloaded["body"]["created_at_utc"],
                         self.campaign["body"]["created_at_utc"])

    def test_an_EDITED_manifest_refuses_the_delayed_task(self):
        self.run_task("block", 0)
        path = Path(self.paths["manifest"])
        document = json.loads(path.read_text())
        document["body"]["label"] = "edited"
        path.write_text(json.dumps(document, indent=2), encoding="utf-8")
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.own("block", 1)
        self.assertIn("has been EDITED since it was written", str(caught.exception))

    def test_a_MOVED_CODE_REVISION_refuses_the_delayed_task(self):
        """The composition's task-side half. A tree edited between task 0 and task 20 gives a
        different A-2(f) listing digest, and the campaign refuses rather than mixing revisions."""
        self.run_task("block", 0)
        drifted = Path(self.work) / "drifted-source-manifest.json"
        record = json.loads(Path(self.srcman).read_text())
        record["listing_sha256"] = "1" * 64
        drifted.write_text(json.dumps(record), encoding="utf-8")
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.own("block", 1, env=self.task_env(1, **{ZP.SOURCE_MANIFEST_ENV: str(drifted)}))
        self.assertIn("The code revision moved under the campaign", str(caught.exception))

    def test_a_MOVED_INPUT_refuses_the_delayed_task(self):
        self.run_task("block", 0)
        np.save(self.bank.path / "flux_univ_ratio.npy",
                np.full((U.EXPECTED_FLUX_UNIVERSES, 2), 1.05))
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.own("block", 1)
        self.assertIn("has CHANGED", str(caught.exception))
        self.assertIn("different normalization", str(caught.exception))

    def test_an_ADDED_BANK_ENTRY_refuses_the_delayed_task(self):
        self.run_task("block", 0)
        np.save(self.bank.path / "sig_extra_t_0.npy", np.ones(4))
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.own("block", 1)
        self.assertIn("has CHANGED since the campaign was initialized", str(caught.exception))

    def test_a_DIFFERENT_BANK_refuses_the_delayed_task(self):
        self.run_task("block", 0)
        other = SyntheticBank(self.work / "second")
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.own("block", 1, bank=str(other.path))
        self.assertIn("is not a member of this production", str(caught.exception))

    def test_a_MOVED_SEED_refuses_the_delayed_task_in_BOTH_roles(self):
        self.run_task("block", 0)
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.own("block", 1, estimator_seed=1005)
        self.assertIn("--estimator-seed 1005", str(caught.exception))
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.own("block", 2, draw_seed=1005)
        self.assertIn("--draw-seed 1005", str(caught.exception))

    def test_the_bound_seeds_come_from_the_POLICY_MODULE_not_from_a_literal(self):
        """`seed_offset_policy` is the single source of the group-2 baseline and the pinned draw
        seed, and THE BASELINES ARE NOT SHARED -- group 1's is 42. A literal here would be a second
        statement of the grouping, silently plausible if wrong."""
        import seed_offset_policy as policy

        group, baseline = policy.LEG_BASELINES["unified_throw_cov"]
        seeds = self.campaign["body"]["seeds"]
        self.assertEqual((seeds["estimator_group"], seeds["estimator_baseline"]),
                         (group, baseline))
        self.assertEqual(seeds["draw_seed"], policy.ARCHIVE_DRAW_SEED)
        self.assertNotEqual(baseline, policy.LEG_BASELINES["sweep_bank_5d"][1])


# ============================================ PHASE 1: the initialization is atomic and fresh ===
class InitializationIsAtomicAndFresh(CampaignFixture):
    """Phase 1: freshness did not disappear, it moved here and became atomic."""

    def test_POSITIVE_CONTROL_a_fresh_namespace_INITIALIZES_and_binds_all_four_things(self):
        started = self.init_campaign("zcamp_fresh")
        body = started["campaign"]["body"]
        self.assertEqual(body["namespace"], "zcamp_fresh")
        # THE FOUR THINGS JOSEPH NAMED, each asserted as a value and not as a key's presence.
        self.assertEqual(sorted(body["arms"]), ["block", "combine", "run"])
        self.assertEqual(body["arms"]["block"]["n_tasks"], 21)
        self.assertEqual(len(body["arms"]["run"]["outputs"]), 40)
        self.assertEqual(body["code"]["listing_sha256"],
                         json.loads(Path(self.srcman).read_text())["listing_sha256"])
        self.assertEqual(len(body["inputs"]["bank_cv_sha256"]), 64)
        self.assertEqual(body["inputs"]["entry_count"], 374)
        self.assertEqual(body["seeds"]["estimator_seed"], 1000)

    def test_a_NON_FRESH_namespace_refuses_with_the_ARM_and_the_PRODUCT_named(self):
        target = Path(ZP.arm_directory(str(self.data_root), "zcamp_dirty", "block"))
        target.mkdir(parents=True, exist_ok=True)
        U._atomic_savez(str(target / "block5d_knobs.npz"), xs=np.arange(2, dtype=float))
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.init_campaign("zcamp_dirty")
        self.assertIn("NOT FRESH", str(caught.exception))
        self.assertIn("block5d_knobs.npz", str(caught.exception))

    def test_an_EXISTING_but_EMPTY_namespace_refuses_because_the_CREATE_is_EXCLUSIVE(self):
        """The glob sweep passes on an empty directory; the exclusive create is what refuses it,
        and that is the clause that makes freshness atomic rather than instantaneous."""
        Path(ZP.arm_directory(str(self.data_root), "zcamp_empty", "combine")).mkdir(parents=True)
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.init_campaign("zcamp_empty")
        self.assertIn("ALREADY EXISTS", str(caught.exception))

    def test_RE_INITIALIZING_the_SAME_namespace_refuses(self):
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.init_campaign(self.namespace)
        self.assertIn("ALREADY EXISTS", str(caught.exception))

    def test_a_STALE_A2f_RECORD_refuses_initialization(self):
        record = json.loads(Path(self.srcman).read_text())
        record["files"]["nd-unfolding/z_precursor.py"] = "2" * 64
        stale = self.work / "stale-source-manifest.json"
        stale.write_text(json.dumps(record), encoding="utf-8")
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.initialize_campaign(data_root=str(self.data_root), namespace="zcamp_stale",
                                   code_root=str(REPO), source_manifest=str(stale),
                                   bank=str(self.bank.path), arms=list(self.ARMS), environ={})
        self.assertIn("is NOT the code root", str(caught.exception))

    def test_a_bank_with_NO_FLUX_RATIO_TABLE_refuses_initialization(self):
        """`flux_univ_ratio.npy` is a REQUIRED validated input; its absence sends
        `_flux_ratio_table` to a ROOT-dependent rebuild from a different file."""
        import flux_universe

        os.unlink(self.bank.path / flux_universe.BANKED_RATIO_NAME)
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.init_campaign("zcamp_noratio")
        self.assertIn("REQUIRED validated input", str(caught.exception))

    def test_a_DECLARED_MEMBER_AXIS_refuses_initialization_including_at_ZERO(self):
        for value in ("0", "1200", ""):
            with self.subTest(value=value):
                with self.assertRaises(ZP.PrecursorError) as caught:
                    ZP.initialize_campaign(
                        data_root=str(self.data_root), namespace=f"zcamp_m{len(value)}",
                        code_root=str(REPO), source_manifest=self.srcman,
                        bank=str(self.bank.path), arms=list(self.ARMS),
                        environ={ZP.MEMBER_OFFSET_ENV: value})
                self.assertIn("mii/member_kNNNNNN", str(caught.exception))

    def test_a_RELATIVE_data_root_refuses(self):
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.initialize_campaign(data_root="data", namespace="zcamp_rel", code_root=str(REPO),
                                   source_manifest=self.srcman, bank=str(self.bank.path),
                                   environ={})
        self.assertIn("is relative", str(caught.exception))

    def test_the_DUMP_arm_cannot_be_campaign_owned_and_the_refusal_says_WHY(self):
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.init_campaign("zcamp_dump", arms=["dump"])
        message = str(caught.exception)
        self.assertIn("addressed by CONTENT", message)
        self.assertIn("--ngroups", message)
        self.assertNotIn("dump", ZP.campaign_arms())

    def test_the_DUMP_arm_KEEPS_the_pre_existing_freshness_predicate_UNCHANGED(self):
        """The residual, as an executable fact. Its per-invocation predicate is what it always was,
        which means its 8-task array still has the composition defect -- named rather than hidden.
        """
        saved = dict(os.environ)
        os.environ[ZP.NAMESPACE_ENV] = self.namespace
        os.environ.pop("MNV_EST_SEED_OFFSET", None)
        self.addCleanup(lambda: (os.environ.clear(), os.environ.update(saved)))
        bank_dir = Path(self.plan["arms"]["dump"]["dir"])
        contract = ZP.enforce_namespace_contract("dump", str(self.data_root), str(bank_dir))
        self.assertIsNone(contract["campaign"])
        self.assertTrue(contract["fresh"]["fresh"])
        bank_dir.mkdir(parents=True, exist_ok=True)
        (bank_dir / "cv.npz").write_bytes(b"x")
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.enforce_namespace_contract("dump", str(self.data_root), str(bank_dir))
        self.assertIn("NOT FRESH", str(caught.exception))

    def test_the_campaign_directory_is_INVISIBLE_to_EVERY_arm_glob(self):
        """Asserted over `ARM_LAYOUT`, not over today's four literals: a campaign directory its own
        freshness sweep selected would refuse the namespace it had just created."""
        for arm, (_sub, pattern) in ZP.ARM_LAYOUT.items():
            with self.subTest(arm=arm):
                self.assertEqual(
                    globmod.glob(os.path.join(self.paths["root"], "..", pattern)),
                    [p for p in globmod.glob(os.path.join(self.paths["root"], "..", pattern))
                     if os.path.basename(p) != ZP.CAMPAIGN_DIR])
                self.assertNotIn(ZP.CAMPAIGN_DIR, [os.path.basename(p) for p in globmod.glob(
                    os.path.join(os.path.dirname(self.paths["root"]), pattern))])
        # ...and the sweep itself passes on a freshly initialized namespace, which is the
        # positive control that matters: initialization must not refuse its own output.
        self.assertTrue(ZP.check_namespace_fresh(self.plan)["fresh"])


# ================================================= the bindings, the compositions, the shape ====
class TheCodeBindingComposesWithTheLaunchersOwnPreflight(unittest.TestCase):
    """Two rulings that each hold only under the other's precondition compose into a defect when
    only prose joins them, so the composition is pinned here.

    THE CLAIM: `verify_campaign_code` establishes manifest == A-2(f) RECORD, and the launcher's own
    preflight establishes RECORD == live tree. Neither half is sufficient. Both halves are measured
    -- the second by reading the launcher text, in the order the lines actually run.
    """

    LAUNCHERS = ("block", "run", "combine")

    def test_every_covered_arms_launcher_compares_the_record_against_the_TREE_before_the_producer(
            self):
        for arm in self.LAUNCHERS:
            with self.subTest(arm=arm):
                text = LAUNCHER[arm].read_text()
                self.assertIn('SRCMAN_RECORD="${MNV_SOURCE_MANIFEST:?', text,
                              "the record path must be mandatory with no default")
                compare = text.index('--compare "$SRCMAN_RECORD"')
                self.assertIn("--require-clean", text[compare:compare + 400])
                self.assertIn("--require-readonly", text[compare:compare + 400])
                producer = text.index("unified_throw_cov_5d.py")
                self.assertLess(compare, producer,
                                "the A-2(f) comparison must run BEFORE the producer; a check "
                                "after use cannot bind the bytes that already ran")

    def test_the_variable_the_LAUNCHER_sets_is_the_variable_z_precursor_READS(self):
        self.assertEqual(ZP.SOURCE_MANIFEST_ENV, "MNV_SOURCE_MANIFEST")
        for arm in self.LAUNCHERS:
            with self.subTest(arm=arm):
                self.assertIn(f"${{{ZP.SOURCE_MANIFEST_ENV}:?", LAUNCHER[arm].read_text())

    def test_the_TASK_PATH_imports_NO_new_repository_module(self):
        """`mnv_import_set_ratchet.py` pins each guarded entrypoint's resolved repository-origin
        module set as an IDENTITY and not a floor, and the pin can only be rewritten from a clean
        guarded run -- which is cluster work. So the ownership check must not pull in a module the
        producer did not already import. `mnv_source_manifest` is READ as JSON on the task path and
        IMPORTED only by `campaign_code_binding`, which runs at initialization.
        """
        probe = Path(tempfile.mkdtemp(prefix="zcampaign-importset.")) / "probe.py"
        probe.write_text(
            "import sys\n"
            f"sys.path.insert(0, {str(ND)!r})\n"
            f"sys.path.insert(0, {str(REPO / '2d-unfolding')!r})\n"
            "import unified_throw_cov, z_precursor\n"
            "before = set(sys.modules)\n"
            "z_precursor.verify_campaign_code({'body': {'code': {'listing_sha256': 'x',\n"
            "    'file_count': 0, 'head': 'h', 'source_manifest_sha256': 's'}}},\n"
            "    {'MNV_SOURCE_MANIFEST': __file__}) if False else None\n"
            "print('mnv_source_manifest' in sys.modules)\n", encoding="utf-8")
        out = subprocess.run([sys.executable, str(probe)], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(out.stdout.strip(), "False",
                         "importing the producer and z_precursor must not resolve "
                         "mnv_source_manifest; that would move the P-4 import-set pin")


class TheContractAddsNoInterpreterInvocationToAnyLauncher(unittest.TestCase):
    """Ruling 21's pin, re-asserted for this repair: the campaign's task half travels on a flag,
    not on a new `python3` line, because `mnv_preflight_census.py` pins unclassified interpreter
    invocations in the declared launchers at zero and `z_precursor.py` still cannot be a declared
    preflight tool (criterion (5): its repository imports must be a subset of {mnv_guarded_run}).
    """

    def test_no_launcher_INVOKES_z_precursor_py(self):
        """⚠ NOT A SEARCH FOR THE FILENAME, and the difference is measured rather than guessed:
        `sbatch_uthrow_dump_5d.sh:234` names `z_precursor.py` in a `--pair` deployment-parity
        BINDING, which is the opposite of an invocation, and a filename search reports it as a
        violation. Only a line that hands the file to an interpreter can be one.

        The census itself is the instrument for this rule and is run by `test_z_precursor.py::
        test_the_PREFLIGHT_CENSUS_itself_is_CLEAN_on_this_tree`; this arm is the narrower statement
        that THIS repair added no such line to the four arms' launchers.
        """
        for arm, path in LAUNCHER.items():
            with self.subTest(arm=arm):
                for number, line in enumerate(path.read_text().splitlines(), 1):
                    stripped = line.strip()
                    if stripped.startswith("#") or "z_precursor.py" not in stripped:
                        continue
                    self.assertNotIn("python3", stripped,
                                     f"{path.name}:{number} invokes z_precursor.py: {stripped!r}")
                    self.assertIn("--pair", stripped,
                                  f"{path.name}:{number} names z_precursor.py outside a parity "
                                  f"binding: {stripped!r}")

    def test_the_producer_receives_the_contract_as_a_FLAG_it_already_had(self):
        block = LAUNCHER["block"].read_text()
        self.assertIn("--z-namespace-arm block", block)
        self.assertIn('"${ZARM[@]}"', block)

    def test_the_launchers_still_pass_the_OUTPUT_PATH_the_ownership_check_binds(self):
        """The task-side half needs no new argument: the `--out` expression the launcher already
        builds IS the operand, and the task id comes from Slurm's own variable."""
        self.assertIn('--out "${BLOCK_DIR}/block5d_knobs.npz"', LAUNCHER["block"].read_text())
        self.assertIn('--out "${BLOCK_DIR}/block5d_flux_${T}.npz"', LAUNCHER["block"].read_text())
        self.assertIn('--out "${SLAB_DIR}/uthrow5d_slab_${SLURM_ARRAY_TASK_ID}.npz"',
                      LAUNCHER["run"].read_text())
        self.assertIn("--out-root", LAUNCHER["combine"].read_text())


class TheDeclarationsAreDerivedFromTheLaunchersOwnLines(unittest.TestCase):
    """The campaign's task table is DERIVED. A range literal would be a second implementation."""

    def test_the_task_outputs_MAPPING_and_the_population_LIST_are_ONE_implementation(self):
        for arm in ("block", "run"):
            with self.subTest(arm=arm):
                mapping = ZP.declare_arm_task_outputs(arm, LAUNCHER[arm])
                self.assertEqual(ZP.declare_arm_files(arm, LAUNCHER[arm]),
                                 [mapping[t] for t in sorted(mapping)])

    def test_the_derived_names_match_the_launchers_OWN_write_expressions(self):
        mapping = ZP.declare_arm_task_outputs("block", LAUNCHER["block"])
        text = LAUNCHER["block"].read_text()
        self.assertEqual(mapping[0], "block5d_knobs.npz")
        self.assertIn("block5d_knobs.npz", text)
        self.assertIn("block5d_flux_${T}.npz", text)
        self.assertEqual(mapping[7], "block5d_flux_7.npz")

    def test_the_THROTTLE_is_not_mistaken_for_the_population(self):
        block = ZP.parse_sbatch_arm(LAUNCHER["block"])
        self.assertEqual((block["n_tasks"], block["throttle"]), (21, 10))

    def test_the_COMBINE_arm_is_declared_from_ARM_LAYOUT_and_NOT_from_declare_arm_files(self):
        """Two derivations kept apart so neither borrows the other's warrant: a task-derived
        basename list for the combine arm would be a fiction, and `declare_arm_files` still says so.
        """
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.declare_arm_files("combine", LAUNCHER["combine"])
        self.assertIn("no per-task file layout", str(caught.exception))
        table = ZP.campaign_arm_table(str(REPO), ["combine", "run", "block"])
        self.assertEqual(table["combine"]["outputs"], {"0": ZP.ARM_LAYOUT["combine"][1]})
        self.assertIsNone(table["combine"]["array_spec"])

    def test_a_campaign_declaring_the_CONSUMER_must_declare_what_it_CONSUMES(self):
        """Otherwise phase 3 has no declared population to require and the combine's inputs go
        ungated -- an absence caused by the declaration, not by the data."""
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.campaign_arm_table(str(REPO), ["combine"])
        self.assertIn("but not ['block', 'run']", str(caught.exception))
        # ...and the consumed arms on their own are fine: the requirement is one-directional.
        self.assertEqual(sorted(ZP.campaign_arm_table(str(REPO), ["run", "block"])),
                         ["block", "run"])

    def test_a_launcher_MISSING_from_the_code_root_refuses_rather_than_being_invented(self):
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.campaign_arm_table(str(Path(tempfile.mkdtemp(prefix="zcampaign-empty."))),
                                  ["block"])
        self.assertIn("is absent from the code root", str(caught.exception))


class TheCampaignDigestIsSelfVerifying(CampaignFixture):
    """The identity and the tamper check are the same question, asked on every read."""

    def test_the_digest_is_RECOMPUTED_on_read_and_not_trusted(self):
        path = Path(self.paths["manifest"])
        document = json.loads(path.read_text())
        document["campaign_digest"] = "3" * 64
        path.write_text(json.dumps(document, indent=2), encoding="utf-8")
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.load_campaign(str(path))
        self.assertIn("has been EDITED", str(caught.exception))

    def test_the_digest_is_STABLE_across_reads(self):
        for _ in range(3):
            self.assertEqual(ZP.load_campaign(self.paths["manifest"])["campaign_digest"],
                             self.campaign["campaign_digest"])

    def test_TWO_campaigns_over_the_SAME_inputs_have_DIFFERENT_identities(self):
        """Two productions from one tree and one bank are still two productions. If their digests
        collided, a product of one would bind cleanly to the other."""
        other = self.init_campaign("zcamp_twin")
        self.assertNotEqual(other["campaign"]["campaign_digest"],
                            self.campaign["campaign_digest"])
        self.assertEqual(other["campaign"]["body"]["code"]["listing_sha256"],
                         self.campaign["body"]["code"]["listing_sha256"])

    def test_a_FOREIGN_SCHEMA_VERSION_is_refused_rather_than_migrated(self):
        path = Path(self.paths["manifest"])
        document = json.loads(path.read_text())
        document["body"]["schema_version"] = "z-campaign/99"
        document["campaign_digest"] = ZP.campaign_digest(document["body"])
        path.write_text(json.dumps(document, indent=2), encoding="utf-8")
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.load_campaign(str(path))
        self.assertIn("refused rather than migrated", str(caught.exception))

    def test_an_ABSENT_manifest_refuses_and_says_freshness_MOVED(self):
        plan = ZP.namespace_plan(str(self.data_root), namespace="zcamp_none")
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.verify_task_ownership(arm="block", plan=plan,
                                     product="/tmp/nope/block5d_knobs.npz",
                                     bank=str(self.bank.path), estimator_seed=1000,
                                     draw_seed=1000, environ=self.task_env(0))
        self.assertIn("must be a MEMBER of a declared campaign", str(caught.exception))
        self.assertIn("Freshness has not been bypassed", str(caught.exception))


class TheTaskIdentityIsNotInferredFromTheOutput(CampaignFixture):
    """A criterion that cannot disagree with the thing it checks is not a criterion."""

    def test_an_ARRAY_arm_with_NO_task_id_refuses_rather_than_inferring_one(self):
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.own("block", 0, env={ZP.SOURCE_MANIFEST_ENV: self.srcman})
        self.assertIn("holds vacuously", str(caught.exception))

    def test_an_UNDECLARED_task_id_refuses(self):
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.verify_task_ownership(
                arm="block", plan=self.plan_for(),
                product=os.path.join(self.plan["arms"]["block"]["dir"], "block5d_flux_21.npz"),
                bank=str(self.bank.path), estimator_seed=1000, draw_seed=1000,
                environ=self.task_env(21))
        self.assertIn("not a declared task", str(caught.exception))

    def test_a_MALFORMED_task_id_refuses(self):
        for bad in ("x", "-1", "1.5", " "):
            with self.subTest(value=bad):
                with self.assertRaises(ZP.PrecursorError):
                    ZP.verify_task_ownership(
                        arm="block", plan=self.plan_for(),
                        product=self.product_path("block", 0), bank=str(self.bank.path),
                        estimator_seed=1000, draw_seed=1000,
                        environ={ZP.SOURCE_MANIFEST_ENV: self.srcman, ZP.ARRAY_TASK_ENV: bad})

    def test_the_COMBINE_arm_needs_no_task_id_because_it_declares_no_array(self):
        self.complete_consumed_arms()
        contract = self.own("combine", 0, env={ZP.SOURCE_MANIFEST_ENV: self.srcman})
        self.assertEqual(contract["task_id"], 0)
        self.assertEqual(contract["output"], "unified_throw_cov_5d.root")
        self.assertEqual(sorted(contract["consumed"]), ["block", "run"])

    def test_the_COMBINE_arm_CANNOT_CLAIM_until_its_inputs_are_COMPLETE(self):
        """The consumption gate runs BEFORE the `O_EXCL` create, so a premature combine leaves NO
        claim behind and a later attempt is not a duplicate of it.

        This is the ordinary case rather than an error: the combine is normally submitted while the
        arrays are still draining. The first version of this repair gated after the claim, and the
        second attempt then refused itself.
        """
        # (a) NOTHING PRODUCED YET: the identity half of phase 3 is what refuses, naming the files.
        with self.assertRaises(SystemExit) as empty:
            self.own("combine", 0, env={ZP.SOURCE_MANIFEST_ENV: self.srcman})
        self.assertIn("MISSING (40)", str(empty.exception))
        self.assertEqual(ZP.claimed_task_ids(self.paths["claims"], "combine"), set(),
                         "a refused combine must leave no claim, or every retry is a duplicate")
        # (b) EVERY FILE PRESENT, ONE TASK NEVER RECORDED: the completion half is what refuses, and
        #     the identity half passes -- two clauses of phase 3 with two different findings.
        for arm in ZP.CONSUMED_ARMS["combine"]:
            for task in self.campaign["body"]["arms"][arm]["task_ids"]:
                contract = self.own(arm, task)
                if (arm, task) == ("block", 5):
                    U._atomic_savez(self.product_path(arm, task), xs=np.arange(2, dtype=float))
                    continue
                self.publish(contract)
        with self.assertRaises(ZP.PrecursorError) as partial:
            self.own("combine", 0, env={ZP.SOURCE_MANIFEST_ENV: self.srcman})
        self.assertIn("is INCOMPLETE", str(partial.exception))
        self.assertIn("never recorded a completion", str(partial.exception))
        self.assertEqual(ZP.claimed_task_ids(self.paths["claims"], "combine"), set())
        # (c) COMPLETE: the missing record is written and the combine may now claim its output.
        #     The contract is rebuilt from the campaign rather than re-taken, because block task 5
        #     already holds its claim and `verify_task_ownership` would -- correctly -- refuse it
        #     as a duplicate. That refusal has its own arm in
        #     `DuplicatesAndForeignArtifactsRefuse`; all that is needed here is the record.
        ZP.record_task_completion(
            {"campaign": self.campaign, "arm": "block", "task_id": 5,
             "claim": os.path.join(self.paths["claims"], ZP.claim_name("block", 5)),
             "receipt": os.path.join(self.paths["receipts"], ZP.receipt_name("block", 5))},
            product=self.product_path("block", 5))
        self.assertEqual(
            self.own("combine", 0, env={ZP.SOURCE_MANIFEST_ENV: self.srcman})["task_id"], 0)

    def test_the_COMBINE_arm_refuses_a_task_id_it_did_not_declare(self):
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.own("combine", 3, product=self.product_path("combine", 0))
        self.assertIn("single non-array task", str(caught.exception))

    def test_a_CLAIM_FILENAME_carries_the_identity_so_a_reader_need_not_PARSE_it(self):
        """The claim is created by `O_EXCL` at its final name and only then filled, so a concurrent
        reader can legitimately see it empty. If attribution needed the body, that window would be
        a hole in the ownership scan."""
        contract = self.own("block", 11)
        path = Path(contract["claim"])
        self.assertEqual(path.name, "block.task-11.claim.json")
        path.write_bytes(b"")
        self.assertEqual(ZP.claimed_task_ids(self.paths["claims"], "block"), {11})

    def test_a_claim_for_an_UNDECLARED_task_refuses_the_whole_arm(self):
        Path(self.paths["claims"], "block.task-77.claim.json").write_text("{}", encoding="utf-8")
        with self.assertRaises(ZP.PrecursorError) as caught:
            self.own("block", 1)
        self.assertIn("UNDECLARED tasks", str(caught.exception))

    def test_an_ARM_the_campaign_does_not_cover_refuses(self):
        narrow = self.init_campaign("zcamp_blockonly", arms=["block"])
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.verify_task_ownership(
                arm="run", plan=narrow["plan"],
                product=os.path.join(narrow["plan"]["arms"]["run"]["dir"],
                                     "uthrow5d_slab_0.npz"),
                bank=str(self.bank.path), estimator_seed=1000, draw_seed=1000,
                environ=self.task_env(0))
        self.assertIn("is not covered by this campaign", str(caught.exception))


class TheGuardsHaveAPositiveControlEach(CampaignFixture):
    """One place that walks the whole guard set with HEALTHY input and requires SILENCE.

    A guard that refuses everything passes every negative arm in this file. So each clause is
    exercised here in its passing direction, and the arm asserts that nothing was raised AND that
    the run produced the record it was supposed to -- a green gate must prove it did the work.
    """

    def test_a_HEALTHY_task_passes_every_clause_and_leaves_exactly_ONE_claim(self):
        contract = self.own("block", 0)
        self.assertEqual(contract["task_id"], 0)
        self.assertEqual(contract["campaign"]["campaign_digest"],
                         self.campaign["campaign_digest"])
        self.assertTrue(os.path.exists(contract["claim"]))
        self.assertEqual(sorted(os.listdir(self.paths["claims"])),
                         [ZP.claim_name("block", 0)])
        self.assertFalse(os.path.exists(contract["receipt"]),
                         "the completion record must not exist before the product does")

    def test_a_HEALTHY_completion_writes_a_record_that_GATES_CLEAN(self):
        contract = self.own("block", 0)
        receipt, product = self.publish(contract)
        self.assertEqual(receipt["extra"]["arm"], "block")
        checked = ZP.check_task_completion(self.campaign, "block", 0, self.paths["receipts"])
        self.assertEqual(checked["product"], str(Path(product).resolve()))

    def test_a_completion_record_REFUSES_before_the_product_exists(self):
        """The ordering IS the content: the record is an observation, not an intention."""
        contract = self.own("block", 0)
        with self.assertRaises(ZP.PrecursorError) as caught:
            ZP.record_task_completion(contract, product=self.product_path("block", 0))
        self.assertIn("does not exist", str(caught.exception))
        self.assertFalse(os.path.exists(contract["receipt"]))

    def test_every_ARM_of_the_campaign_has_a_PASSING_direction(self):
        """Every covered arm, in its passing direction, so a guard that refuses one of them
        silently cannot hide behind the others' negative arms."""
        self.complete_consumed_arms()
        contract = self.own("combine", 0, env=self.task_env())
        self.assertEqual(contract["arm"], "combine")
        for arm in ZP.CONSUMED_ARMS["combine"]:
            with self.subTest(arm=arm):
                self.assertEqual(
                    ZP.campaign_arm_status(self.campaign, arm)["n_complete"],
                    self.campaign["body"]["arms"][arm]["n_tasks"])

    def test_the_status_view_NEVER_refuses_on_an_unfinished_campaign(self):
        self.run_task("block", 0)
        status = ZP.campaign_arm_status(self.campaign, "block")
        self.assertEqual(status["n_complete"], 1)
        self.assertEqual(status["n_tasks"], 21)
        self.assertEqual([r["task_id"] for r in status["tasks"] if r["claimed"]], [0])

    def test_the_CLI_exits_0_on_a_fresh_init_and_2_on_a_repeat(self):
        """Both directions through `main`, because an exit code is the only thing a launcher or an
        operator shell sees."""
        argv = ["campaign-init", "--data-root", str(self.data_root),
                "--namespace", "zcamp_cli", "--code-root", str(REPO),
                "--source-manifest", self.srcman, "--bank", str(self.bank.path),
                "--arm", "block"]
        self.assertEqual(ZP.main(argv), 0)
        self.assertEqual(ZP.main(argv), 2)
        self.assertEqual(ZP.main(["campaign-status", "--data-root", str(self.data_root),
                                  "--namespace", "zcamp_cli", "--arm", "block"]), 0)
        self.assertEqual(ZP.main(["campaign-show", "--data-root", str(self.data_root),
                                  "--namespace", "zcamp_cli"]), 0)


class TheExclusiveWriterIsNotTheAtomicPublisher(CampaignFixture):
    """`_write_json_exclusive` and `_atomic_write_json` are two mechanisms with opposite duties.

    `os.replace` publishes over whatever is there, which is right for a receipt and catastrophic for
    a claim; `O_CREAT|O_EXCL` fails when somebody got there first, which is the whole mechanism
    behind the duplicate refusal. Both directions are measured here so a later "simplification"
    into one helper has to disagree with a test.
    """

    def test_the_EXCLUSIVE_writer_REFUSES_an_existing_path(self):
        path = self.work / "excl.json"
        ZP._write_json_exclusive(str(path), {"a": 1})
        with self.assertRaises(ZP.PrecursorError):
            ZP._write_json_exclusive(str(path), {"a": 2})
        self.assertEqual(json.loads(path.read_text()), {"a": 1})

    def test_the_ATOMIC_writer_REPLACES_an_existing_path(self):
        path = self.work / "atomic.json"
        ZP._atomic_write_json(path, {"a": 1})
        ZP._atomic_write_json(path, {"a": 2})
        self.assertEqual(json.loads(path.read_text()), {"a": 2})

    def test_a_CONCURRENT_exclusive_create_has_exactly_one_winner(self):
        """Real processes racing on one path, which is the property the duplicate refusal rests on.
        ⚠ MEASURED ON A LOCAL FILESYSTEM. `/pscratch` is Lustre (measured 2026-09-13) and writing
        there was outside this repair's authorization, so the Lustre claim rests on POSIX `O_EXCL`
        semantics rather than on an observation."""
        target = self.work / "race.json"
        barrier = self.work / "race-go"
        script = self.work / "race_child.py"
        script.write_text(
            "import os, sys, time\n"
            f"sys.path.insert(0, {str(ND)!r})\n"
            "import z_precursor as ZP\n"
            "target, barrier = sys.argv[1:3]\n"
            "open(barrier + '.ready.' + str(os.getpid()), 'w').close()\n"
            "deadline = time.time() + 60\n"
            "while not os.path.exists(barrier):\n"
            "    if time.time() > deadline: sys.exit(4)\n"
            "    time.sleep(0.005)\n"
            "try:\n"
            "    ZP._write_json_exclusive(target, {'pid': os.getpid()})\n"
            "except ZP.PrecursorError:\n"
            "    sys.exit(2)\n", encoding="utf-8")
        children = [subprocess.Popen([sys.executable, str(script), str(target), str(barrier)])
                    for _ in range(8)]
        deadline = time.time() + 60
        while len(globmod.glob(f"{barrier}.ready.*")) < 8 and time.time() < deadline:
            time.sleep(0.01)
        self.assertEqual(len(globmod.glob(f"{barrier}.ready.*")), 8)
        barrier.write_text("go", encoding="utf-8")
        codes = [child.wait(timeout=120) for child in children]
        self.assertEqual(codes.count(0), 1, f"exactly one create may succeed: {codes}")
        self.assertEqual(sorted(set(codes)), [0, 2])


class TheRepairIsRecordedWhereItsNextReaderWillMeetIt(unittest.TestCase):
    """The defect, the relocation and the residual, asserted in the files a reader opens."""

    def test_z_precursor_states_that_FRESHNESS_MOVED_rather_than_relaxed(self):
        text = (ND / "z_precursor.py").read_text()
        self.assertIn("FRESHNESS IS RELOCATED, NOT WEAKENED AND NOT BYPASSED", text)
        self.assertIn("ARRAY DEFECT, NOT A CALL DEFECT", text)

    def test_the_RETIRED_predicates_call_site_says_WHY_it_left(self):
        """A reader arriving at `enforce_namespace_contract` must find the reason there, not only
        in a section header two hundred lines away."""
        text = (ND / "z_precursor.py").read_text()
        marker = text.index("def enforce_namespace_contract")
        body = text[marker:text.index("def declare_arm_files", marker)]
        self.assertIn("THE FRESHNESS CLAUSE MOVED", body)
        self.assertIn("refuses every task of an ARRAY", body)

    def test_the_UNREPAIRED_dump_residual_is_stated_AT_ITS_OWN_BRANCH(self):
        text = (ND / "z_precursor.py").read_text()
        self.assertIn("THE ONE ARM THE CAMPAIGN DOES NOT COVER, AND ITS RESIDUAL IS LIVE", text)
        self.assertIn("--array=0-7", text)

    def test_the_PROBE_is_never_an_OPERAND_anywhere_in_the_repair(self):
        """Joseph requires the probe preserved separately and no artifact reuse. It appears here
        only as PROSE naming the shape the foreign-artifact clause refuses.

        ⚠ A SUBSTRING BAN ON THE PATH WOULD FIRE ON THE REFUSAL MESSAGE THAT NAMES IT -- banning
        the warning is not a check, which is the same right-check/wrong-operand shape this suite
        has caught before. So the check is by AST: the path may appear inside a `require` message
        or a comment, and nowhere that a value flows from it.
        """
        import ast

        allowed_callees = {"require", "PrecursorError", "print", "SystemExit"}
        for name in ("z_precursor.py", "unified_throw_cov.py", "unified_throw.py"):
            source = (ND / name).read_text()
            with self.subTest(module=name):
                for node in ast.walk(ast.parse(source)):
                    if not isinstance(node, ast.Call):
                        continue
                    strings = [child.value for child in ast.walk(node)
                               if isinstance(child, ast.Constant)
                               and isinstance(child.value, str)]
                    if not any("z_probe" in s for s in strings):
                        continue
                    callee = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
                    self.assertIn(callee, allowed_callees,
                                  f"{name}: the probe path reaches {callee!r}, which is not a "
                                  f"refusal message -- it must never be an operand")
        self.assertIn("z_probe_20260912", (ND / "z_precursor.py").read_text(),
                      "the clause must still NAME the artifact whose shape it refuses")

    def test_the_producers_completion_call_is_AFTER_the_last_publish_in_ALL_THREE_arms(self):
        text = (ND / "unified_throw_cov.py").read_text()
        for start, label in ((text.index("def do_throws"), "do_throws"),
                             (text.index("def do_blockunits"), "do_blockunits")):
            end = text.index("\ndef ", start + 10)
            body = text[start:end]
            with self.subTest(arm=label):
                self.assertGreater(body.rindex("z_record_completion"),
                                   body.rindex("_atomic_savez"),
                                   "the completion record must be written after the last publish")
        combine = text[text.index("def do_combine"):]
        self.assertGreater(combine.index("z_record_completion"), combine.index("fo.Close()"),
                           "the combine's completion record must follow TFile::Close()")

    def test_there_is_NO_os_exit_on_the_campaign_PATH(self):
        """A record emitted from a bypassed `finally` would assert a completion that did not
        happen; `os._exit` skips `finally`, so it must not appear on either file."""
        for name in ("z_precursor.py", "unified_throw_cov.py"):
            with self.subTest(module=name):
                text = (ND / name).read_text()
                self.assertNotIn("os._exit(", text.replace("`os._exit`", ""))

    def test_the_COMPLETION_check_re_asserts_the_provenance_it_turned_OFF(self):
        """`check_receipt(require_population=False)` also disables the provenance gate, because
        both live in one branch. A relaxation wider than it reads is the shape this catches."""
        text = (ND / "z_precursor.py").read_text()
        body = text[text.index("def check_task_completion"):text.index("def campaign_arm_status")]
        self.assertIn("require_population=False", body)
        self.assertIn("REQUIRED_PROVENANCE", body)
        self.assertIn("relaxation wider than it reads", body)

    def test_the_MESSAGES_a_guard_raises_are_not_one_message_reused(self):
        """Each refusal must be attributable to the clause that produced it.

        The phrases are the ones this suite's negative arms assert on, so a phrase shared by two
        clauses would let a mutation aimed at one be absorbed by the other and still look tested.
        ⚠ TWO MEASUREMENTS SHAPED THIS LIST. `ALREADY EXISTS` alone appears TWICE and both are
        correct -- the namespace root's exclusive create and the task's overwrite refusal -- so the
        asserted phrase is the longer one each clause owns. And a phrase has to be contiguous IN
        THE SOURCE, not only in the rendered message: `... has CLAIMED` is split across two f-string
        fragments and a search for it over the file finds ZERO, which reads as a missing clause.
        """
        text = (ND / "z_precursor.py").read_text()
        for phrase in ("DUPLICATE EXECUTION", "ALREADY EXISTS and ",
                       "no task of this campaign has", "this campaign never declared",
                       "holds vacuously", "has been EDITED",
                       "The code revision moved under the campaign",
                       "is not a member of this production", "is INCOMPLETE"):
            with self.subTest(phrase=phrase):
                self.assertEqual(len(re.findall(re.escape(phrase), text)), 1,
                                 f"{phrase!r} must identify exactly one clause")
        self.assertEqual(len(re.findall("ALREADY EXISTS", text)), 2,
                         "two clauses legitimately share the bare phrase; if that changes, the "
                         "narrowing above is measuring something else")


if __name__ == "__main__":
    unittest.main()
