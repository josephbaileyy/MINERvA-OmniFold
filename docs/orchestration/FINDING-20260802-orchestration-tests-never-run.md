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

### And a landmine for anyone widening collection more broadly

The 2026-08-02 coverage survey found four more `test_*.py` files, in
`omnifold_nn/omnifold/tests/`. **Do not add that directory to collection.** They are vendored
upstream *demo scripts*, not tests: module-level script bodies with **zero assertions**, where the
"check" is a `print()`. They are referenced by no file anywhere in this repo. Two cannot be
imported here at all (the TF 2.16/Keras 3 vs vendored Keras-2 mismatch), and importing
`test_omnifold.py` **runs a real MultiFold training at module scope** — measured at 118 s, and it
writes `omnifold_nn/log_test.txt` into the working tree. Collection alone trains a model and
dirties the checkout; there is no assertion at the end of it to be worth that.

The general rule this suggests: *pytest-shaped* and *is a test* are different properties, and
widening `testpaths` conflates them. `docs/orchestration/` is the case where widening is right
(real tests, real failures, blocked only on triage). `omnifold_nn/omnifold/tests/` is the case
where it is wrong. `nd-unfolding/uq_fps/corrected/` (4 real tests, but they only import from an
`nd-unfolding/` cwd) is a third case again, and needs a `conftest.py` `sys.path` entry before
collection from the repo root would even work.


---

# ADDENDUM — a second instance of the same class: a binding the verifier cannot see

Found the same afternoon, by asking the same question of a different artifact.

`nd-unfolding/active_universe_5d/fps/covariance/fps_control_manifest.json` binds
`unfold_nd_omnifold_unbinned.py` at sha256 `9431d56a…`. It records the path as a **bare
filename**, with no directory. `verify_hash_bindings.localize()` joins a relative path to the repo
root, so it looks for `./unfold_nd_omnifold_unbinned.py`; the file lives at
`nd-unfolding/unfold_nd_omnifold_unbinned.py`. The binding therefore resolves to `None` and is
counted in the verifier's `303 unresolvable (data files, off-repo artifacts, binaries)` — a
parenthetical nobody has ever enumerated.

**It had already drifted, invisibly.** The frozen sha is `9431d56a…`; the file was `3b107b67…`
before the J33 fix landed today and is `3f6d3e06…` after. So the freeze was stale before this
session touched the file, and nothing could report it.

Scope: `fps_control_manifest.json` is the **purity-control** lane
(`fps_provenance.CONTROL_LABEL = "purity-control"`), not a publication endpoint, so the blast
radius is a control product rather than a reported number. That is why this is an addendum and not
its own finding.

**Do not "fix" `localize()` to accept bare filenames right now.** It would resolve an unknown
number of the other 302 in one step and could turn the verifier red, un-triaged, two days before a
restore — the same objection as wiring `docs/orchestration/` into collection. Enumerate the 303
first, decide which are genuinely off-repo (154 `.root`, 121 `.out`, 10 `.log` almost certainly
are), and land the resolver change together with whatever it exposes.

Counted properly, of the 303 exactly **one** is a code path. That is the good news: the
unresolvable bucket really is mostly data. It is also the whole point — one real binding was
hiding in a bucket labelled "data files, off-repo artifacts, binaries", and the label was doing
the work of a check.

### Correction, same day — the enumeration was done, and it moves three numbers

`COVERAGE-SURVEY-20260802.md` §4 enumerated all of them. Three claims above need amending:

1. **The count is 308, not 303.** 303 was right when this was written; receipts landed the same
   afternoon. Not a defect — a reminder that the number is a moving target and citing it without a
   date is meaningless.
2. **The resolver bug affects three bindings, not one.** All three come from the same receipt,
   `fps_control_manifest.json`, which writes paths relative to `nd-unfolding/`:
   `unfold_nd_omnifold_unbinned.py` (**drifted**, as above),
   `active_universe_5d/fps/covariance/audit_merged_fps.json` (MATCH) and
   `.../fps_reported_mask.json` (MATCH). "Exactly one is a code path" is still true — only one is
   a `.py` — but that framing undercounted the resolver's blast radius. The two JSON bindings
   happen to match, which is luck, not verification: nothing would have reported them if they had
   drifted, and they are the *reported mask* and the *merge audit*.
3. **One member of the bucket is not a file path at all.** `g2-attempt2-terminal`, from
   `qp5-wake-reconciliation-20260719.json`, is an event *name*; `collect`'s `<base>_sha256` +
   sibling `<base>` rule harvests it as a binding. So the unresolvable count is not a clean measure
   of anything and should not be treated as one.

**The precondition set above is now satisfied** — "enumerate the 303 first, then land the resolver
change together with whatever it exposes." The exposure is known exactly: three bindings, one of
which goes red. The resolver fix is therefore no longer blocked on triage; it is blocked only on
deciding how the one drifted binding is handled, which is a re-issue of the purity-control lane,
not a hand-edited hash.

Also worth naming, because the label hides it: **4 bindings pin `runEventLoopOmniFold`**, the
canonical compiled analysis binary. It is built in-tree and untracked, so all four are unresolvable
*in this checkout* and would resolve on Perlmutter. The single most load-bearing executable in the
2D/PET pipeline has four hash pins that have never been checked anywhere. See RESTORE Step 0.
