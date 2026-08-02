# FINDING 2026-08-02 — 99 control-plane tests exist, are never collected, and 20 are red

*Found while surveying for stale docs/scripts, not by a test failure — nothing could fail, because
nothing runs them.*
*Status: CONFIRMED. Not a science-restore blocker; a PORTING.md §4 blocker.*
*Severity: the control plane is restored on 08-03 against a test suite that has been dark since at
least 2026-07-20.*

## Claim

`docs/orchestration/` contains six test files — `test_agentctl.py`,
`test_generate_live_state.py`, `test_slurm_array_status.py`, `test_usagectl.py`,
`test_wakerctl.py`, `test_watch_slurm_array_resume.py` — totalling **99 tests**.

The project's test command is `pytest nd-unfolding/tests`. There is no `pytest.ini`, no
`setup.cfg`, no `[tool.pytest]` section, and no `testpaths` anywhere, so nothing widens collection
to `docs/`. These 99 tests have therefore never been part of any recorded baseline: the
`8 failed / 602 passed / 1 skipped` figure quoted throughout the campaign does not include them.

Run explicitly, **20 fail**:

```
python3 -m pytest docs/orchestration/ -q
20 failed, 79 passed in 1.12s

  17  test_wakerctl.py
   2  test_watch_slurm_array_resume.py
   1  test_usagectl.py
```

## These are not platform artifacts

The seven known off-Perlmutter failures in the science suite are ImportError/FileNotFoundError on
an absent `/pscratch` path. These are not that. Sampled:

```
test_wakerctl.py::...  AssertionError: Lists differ:
    [('evt-w1', 'blocked')] != [('evt-w1', 'resumed')]
```

That is a behavioural disagreement about what the waker does with an event — the code and its test
have different ideas about the outcome. Nothing about it depends on the filesystem.

## It corroborates something already on the books

`wakerctl.py` and `test_wakerctl.py` are the first two entries in
`verify_hash_bindings.KNOWN_PREEXISTING` — bindings that drifted before 2026-07-28 and are
deliberately not "fixed" because the receipts record what ran at submit time. Both files last
changed together at `7e69926` (2026-07-20, "Cut over to interim Claude root"). So: a file drifted
from the receipt that froze it, its tests drifted with it or not at all, and **nothing has been
able to notice for two weeks** because the suite is not collected.

The pattern is the one this campaign keeps re-finding, one level out: a check that does not run.
`verify_hash_bindings.py` grew a `SHELL_PIN_FLOOR` for exactly this reason, and
`test_hash_bindings.py` grew a discovery floor on 07-31. Neither covers an entire uncollected
directory.

## Why it matters on 08-03, and why it is not urgent today

`PORTING.md` §4 restores the control plane — wakerctl preflight, scrontab, the mail check — and
`RESTORE-2026-08-03.md` explicitly says that lane "does not gate anything here". True for the
science, and it is also the lane that drives every wake-and-act step of the restore.
`FINDINGS.md` BEN-024 already records that delegate-session watchers are "the weakest link in
multi-hour chains", with four independent deaths in one day. Restoring that machinery against 20
red tests nobody has seen is avoidable.

## What to do, and what NOT to do

**Do not simply add `docs/orchestration/` to the default collection.** That would move the
campaign's baseline from `8 failed` to `28 failed` in one commit and bury the science failures
that the baseline exists to make visible. The baseline contract is load-bearing: every session
this week has checked its work against "8 failed, and this exact set".

The sequence that keeps the contract intact:

1. Triage the 20 — decide per test whether the code or the test is wrong. 17 are one file.
2. Fix them, or delete the ones that describe behaviour that was deliberately removed at
   `7e69926`, with the reason recorded.
3. **Then** wire the directory into collection, in the same commit that lands the green result, so
   the baseline moves once, deliberately, from `8 failed / 602 passed` to `8 failed / 701 passed`.
4. Note that step 2 may move `wakerctl.py`, which is `KNOWN_PREEXISTING`-drifted. Changing it does
   not void a live gate — no current receipt binds it — but the drift entry should then be
   re-examined rather than left describing a file that has moved again.

Owner: whoever takes `PORTING.md` §4. Not the science restore.
