"""INDEPENDENT REVIEWER PROBE -- not part of the subject. Complete-ARRAY behaviour.

Joseph's framing: assess the complete ARRAY, not individual calls. The suite's control-2 arm
spawns SEVEN concurrent tasks; the block arm's real declared array is TWENTY-ONE at `%10`. This
drives the whole declared population in waves of the launcher's own throttle, so wave 2 starts
after wave 1's siblings have COMPLETED -- control 1 and control 2 composed, at full array width.
"""
import glob as globmod, os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_z_campaign_ownership import CampaignFixture, ND  # noqa: E402
import z_precursor as ZP  # noqa: E402


class TheCompleteBlockArrayRunsToCompletion(CampaignFixture):
    def test_ALL_21_BLOCK_TASKS_SUCCEED_in_waves_of_the_launchers_own_throttle(self):
        declared = self.campaign["body"]["arms"]["block"]["task_ids"]
        self.assertEqual(len(declared), 21, "the declared block array is not 21 tasks")
        waves, throttle = [], 10
        for i in range(0, len(declared), throttle):
            waves.append(list(declared)[i:i + throttle])
        self.assertEqual([len(w) for w in waves], [10, 10, 1])
        for n, wave in enumerate(waves, 1):
            outcomes = self.spawn("block", wave)
            bad = [(t, c, e) for t, (c, _o, e) in zip(wave, outcomes) if c != 0]
            self.assertEqual(bad, [], f"wave {n} of the real array refused: {bad}")
        expected = {self.campaign["body"]["arms"]["block"]["outputs"][str(t)] for t in declared}
        got = {os.path.basename(p) for p in globmod.glob(self.plan["arms"]["block"]["product_glob"])}
        self.assertEqual(got, expected, "the complete array did not produce exactly its declared population")
        self.assertEqual(ZP.claimed_task_ids(self.paths["claims"], "block"), set(declared))
        self.assertEqual(len(got), 21)



class TheCompleteRunArrayRunsAtItsRealConcurrency(CampaignFixture):
    def test_ALL_40_RUN_TASKS_SUCCEED_CONCURRENTLY_which_is_its_real_throttle(self):
        """`--array=0-39%40` means the run arm has NO effective throttle: all 40 may be in flight
        at once. The suite's concurrency arm is seven. This is the real width."""
        declared = list(self.campaign["body"]["arms"]["run"]["task_ids"])
        self.assertEqual(len(declared), 40)
        outcomes = self.spawn("run", declared)
        bad = [(t, c, e) for t, (c, _o, e) in zip(declared, outcomes) if c != 0]
        self.assertEqual(bad, [], f"the full-width run array refused: {bad[:3]}")
        expected = {self.campaign["body"]["arms"]["run"]["outputs"][str(t)] for t in declared}
        got = {os.path.basename(q) for q in globmod.glob(self.plan["arms"]["run"]["product_glob"])}
        self.assertEqual(got, expected)
        self.assertEqual(ZP.claimed_task_ids(self.paths["claims"], "run"), set(declared))


class ARequeuedTaskFromAnEarlierWaveRefuses(CampaignFixture):
    def test_RERUNNING_a_COMPLETED_task_after_the_array_finished_REFUSES(self):
        """The node-failure/requeue shape, at array scale: the whole block array completes, then
        one already-finished task is started again, as a Slurm requeue would."""
        declared = list(self.campaign["body"]["arms"]["block"]["task_ids"])
        for i in range(0, len(declared), 10):
            for code, _o, err in self.spawn("block", declared[i:i + 10]):
                self.assertEqual(code, 0, err)
        (code, _out, err) = self.spawn("block", [7])[0]
        self.assertNotEqual(code, 0, "a requeued completed task was permitted to run again")
        print("\n    REQUEUE REFUSAL SAYS: " + " / ".join(
            l.strip() for l in err.strip().splitlines() if l.strip())[:400])
        after = {os.path.basename(q) for q in globmod.glob(self.plan["arms"]["block"]["product_glob"])}
        self.assertEqual(len(after), 21, "the refusal must not have disturbed the population")


if __name__ == "__main__":
    unittest.main(verbosity=2)
