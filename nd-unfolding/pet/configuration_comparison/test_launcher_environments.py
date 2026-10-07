"""A launcher whose driver reaches the vendored engine must load TensorFlow.

`sbatch_prematerialize.sh` called `build_fullevent_loaders` under
`module load python`, which has no TensorFlow. It failed in 101 seconds and
took the whole campaign chain with it -- every downstream stage went
`DependencyNeverSatisfied`, so a one-line environment error cost the queue
wait for six jobs.

The same defect had been found and fixed in the smoke launcher hours earlier.
It recurred because this launcher was written afterwards and nothing checked
the class. That is the third "repaired in one place, left in the other" of
the day, after `flat_projection` and the `-inf` attention surrogate, so it
gets a structural check rather than a third individual fix.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Importing any of these pulls in `omnifold`, which imports TF at module load.
ENGINE_MARKERS = ("build_fullevent_loaders", "from omnifold", "import omnifold")


def _drivers_invoked(script: str) -> set[str]:
    return set(re.findall(r"configuration_comparison/(\w+\.py)", script))


def _needs_tensorflow(driver: str) -> bool:
    path = HERE / driver
    if not path.exists():
        return False
    text = path.read_text()
    return any(marker in text for marker in ENGINE_MARKERS)


class LauncherEnvironments(unittest.TestCase):
    def test_every_launcher_reaching_the_engine_loads_tensorflow(self):
        offenders = {}
        for script in sorted(HERE.glob("sbatch_*.sh")):
            text = script.read_text()
            needy = sorted(d for d in _drivers_invoked(text) if _needs_tensorflow(d))
            if needy and "module load tensorflow" not in text:
                offenders[script.name] = needy
        self.assertEqual(offenders, {},
                         msg="these call the engine without loading TensorFlow")

    def test_the_check_can_actually_fire(self):
        """A guard that cannot fail is not a guard."""
        self.assertTrue(_needs_tensorflow("run_arm_evaluation.py"))
        self.assertTrue(_needs_tensorflow("prematerialize_theirs.py"))

    def test_it_does_not_demand_tensorflow_where_it_is_not_needed(self):
        """`select_learning_rate` and `make_final_deck` never touch the engine."""
        for driver in ("select_learning_rate.py", "make_final_deck.py"):
            self.assertFalse(_needs_tensorflow(driver), msg=driver)

    def test_the_gather_loads_it(self):
        text = (HERE / "sbatch_prematerialize.sh").read_text()
        self.assertIn("module load tensorflow", text)
        self.assertNotIn("module load python\n", text)
