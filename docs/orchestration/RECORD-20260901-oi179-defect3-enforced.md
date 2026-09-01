# RECORD 2026-09-01 — `OI-179` defect 3 ENFORCED across the eight k=0 launchers

**CITABLE FOR:** what the eight launchers now require and assert about the submission environment,
and the measurements that decided the shape. **NOT CITABLE FOR:** any gate movement, leg 6, adoption
of any covariance, or authorization to launch. **Gate 2 remains FAIL. Nothing is adopted. CAND
`1 of 7`, QUOTED `0 of 7`.** No compute was authorized by this change and none was run under it.

## Authority

Joseph, 2026-09-01, in his own turn: **"go ahead with defect-3 enforcement"**. Direct, not relayed.
The trade-off he was given when he chose the instrument-only shape on 2026-08-31 — *"an inlined
emitter could not be skipped but would edit eight pinned launchers"* — was re-measured before acting,
and **the cost it was avoiding does not exist**. See §2.

## 1. What the launchers now do

One block, **byte-identical in all eight**, inside the existing `OI-136` span so the pre-existing
byte-identity assertion carries it as well as the new one:

- **`MNV_ENV_PROVENANCE` is mandatory with no default** (`${VAR:?…}`, so an exported-but-empty value
  refuses too). It names the submission baseline written by `mnv_env_provenance.py --emit` before the
  first `sbatch`. **A submitter can no longer forget the step: every arm refuses without it.**
- **The task records its own environment** to
  `${MNV_GUARD_INVENTORY_DIR}/env-provenance.<jobname>.<jobid>.<task>.json`, **written even when the
  check then fails** — a refused task is exactly the one whose environment matters.
- **Every `MNV_*` variable the baseline DECLARES must have reached the task with the same value.**
  Dropped or changed is a refusal naming the variable.
- **Exit codes are propagated, not collapsed:** `2` could-not-look, `3` measured-drift. A check that
  could not run is not a check that passed.

`mnv_env_provenance.py` is added to each launcher's tool-existence loop and to each launcher's A-3
`--pair` set, so the tool cannot be deleted to skip the step and its executing copy is bound.

## 2. The cost the 2026-08-31 shape was avoiding does not exist — measured, not argued

| claim | measurement |
|---|---|
| *"edits eight PINNED launchers"* | The pre-source loop compares each library against **`HEAD`**, not a hardcoded digest, so a committed edit keeps it green |
| *"`OI-123` pin supersession"* | `verify_hash_bindings.py`: **`ALL BINDINGS INTACT`**, and **none of the eight** is bound by an active run receipt — which is precisely what blocks the `OI-123` launchers and does not apply here |
| A-3 parity would break | Each launcher's `--pair` set already includes **itself**; the new tool got its own entry |
| `F-14` / §7.0.7 | Applies exactly as to any commit (`generate_manifest.py --check` = 0 at the graded sha). A condition on this change, not a cost peculiar to it |

## 3. THREE THINGS THE MEASUREMENT CHANGED, and none of them was a preference

### 3a. The search paths cannot be asserted, and the reason is an interpreter floor

Probe job **`57819105`** (2026-09-01, `--qos=debug`, one minute, outside every production path,
directory removed afterwards):

- a compute node's **pre-activation** environment is **byte-identical** to the login node's for
  `HOME`, `PATH` and `PYTHONPATH`, and gains exactly one `LD_LIBRARY_PATH` entry,
  `/opt/cray/libfabric/default/lib64`;
- that node's `python3` is **`/usr/bin/python3`, Python `3.6.15`** — so this tool, which needs 3.7+,
  **cannot run at the point where the comparison would be exact.**

It therefore runs post-activation, where the paths legitimately differ (round 2: 47 entries against
the submitter's 27). **They are observed and printed, never asserted. A guard that fires on every
correct run is not a guard.**

### 3b. HOME cannot be asserted — three launchers would have refused themselves

The first draft asserted `HOME` equality. **Six of the eight launchers carry
`#SBATCH --export=ALL,HOME=/global/homes/j/josephrb` and three additionally `export HOME=…` in the
body**, deliberately, against a conda-by-prefix trap. Asserting it would have made those three fail
every correct run. Reported as an observation instead, with a test arm pinning that decision so it
cannot be quietly reversed.

### 3c. An ADDED `MNV_*` is what activation does

Also asserted in the first draft, also wrong. The launcher fixture's activator sets
`MNV_TEST_ACTIVATED`; **the fixture caught this, which is what the fixture is for.** The real
activator sets none today — but a rule that holds only while that stays true breaks every task the
day it changes. Additions are observed, not asserted.

**Stated plainly because it superficially resembles the bad pattern:** three assertions were removed
after tests failed. **They were removed because measurement showed each contradicted deliberate,
documented behaviour of the system under test** — not because they were inconvenient. The question
this guard answers is *did a declaration the submitter made reach this task*, and that is exactly
DROPS and CHANGES against the baseline. The submitter-side `--check` still compares everything, and
it remains the only thing that can see defect 1's `mkdir`, because that is a login-environment fact.

## 4. ⚠ THIS WIDENS RULING 21's GUARDING BOUNDARY — flagged, not absorbed

`mnv_preflight_exclusions.json` records *"Joseph, ruling 21 of 2026-08-22 — the 14/30 guarding
boundary is ACCEPTED"*. Adding a preflight tool call to eight launchers moves it:

| | before | after |
|---|---:|---:|
| guarded | 14 | **14 — unchanged** |
| declared-preflight | 16 | **24** |
| interpreter-probe | 16 | 16 |
| unclassified | 0 | **0** |
| **guarding boundary** | **30** | **38** |

**The guarded count did not move — no science invocation changed, which is what ruling 21 was about.**
But the declared exclusion set grew, and `F-7(a)`'s complaint was precisely that *a seventeenth
exclusion could appear with nothing failing*. **Something did fail: the census refused this change
until the declaration was updated, which is the check working.** The widening follows from the
enforcement Joseph authorized, but ruling 21 accepted a boundary and this moves it, so it is recorded
here, in the declaration's `authority` field, and in `OI-179` **for him to see rather than treated as
covered**.

**It was also minimized rather than accepted at face value.** The first draft made **two** `python3`
calls per launcher (`--emit` then `--check-inherited`), which would have taken the boundary to **46**.
The tool grew a `--record` companion so one invocation does both. **A second, smaller instance of the
same discipline:** the new comment block mentioned the literal token `python3` twice per launcher,
which inflated the census's `commented_out_python3_lines` tripwire from 18 to 34. That is a tripwire
for *a call commented out to hide it*; rather than raise the pin by 89% with prose, the two sentences
were reworded and **the pin stays at 18**.

## 5. What was NOT done

`PROPOSAL-20260830-forward-only-rehearsal.md` is untouched — `ARCHIVAL`, `immutable:yes`.
`PROPOSAL-20260830-k0r2-resubmission.md` §3 is updated in place, marking the superseded paragraph
rather than deleting it. **No launcher's science invocations, populations, directives, dependencies
or budgets changed.** Nothing was submitted. `OI-179` does not close here — see the row.
