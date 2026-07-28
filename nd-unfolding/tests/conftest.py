"""Pytest configuration for the nd-unfolding suite.

Added 2026-07-28 to resolve a conflict between two things that are both correct:

  * `test_p3f_pet_fullevent_launcher.py` is SHA-bound in the Gate-3 launch-code
    gate (`docs/orchestration/state/p3f-pet-gate3-launch-code-gate-20260720.json`,
    `be387126...`) and independently agy-verified. It must stay byte-identical.
  * That file opens the launcher at MODULE level via an absolute Perlmutter path,
    so off Perlmutter it raises FileNotFoundError during COLLECTION, which aborts
    the entire run -- not one failure, zero tests.

Editing the frozen file to derive its root would break the gate binding; that is
exactly the mistake this file exists to avoid repeating. Instead we skip
collection of frozen, absolute-path-bound modules when their target is absent.
On Perlmutter the path resolves, nothing is skipped, and the frozen tests gate as
designed.

Keep this list minimal and justified: an entry here means a module is
unrunnable off-cluster BY DESIGN because a gate froze it that way. It is not a
place to park failing tests.
"""
import os

# module -> the absolute path whose absence makes it uncollectable
_FROZEN_ABSOLUTE_PATH_BOUND = {
    "test_p3f_pet_fullevent_launcher.py":
        "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/"
        "sbatch_p3f_pet_fullevent_evloop_array.sh",
}

collect_ignore = [
    mod for mod, target in _FROZEN_ABSOLUTE_PATH_BOUND.items()
    if not os.path.exists(target)
]
