# A blockers array that vetoed authorized work for two days, in the first file every session reads

**Filed 2026-08-15 by the propagation-correction lane** (`BEN-321`, block `320-329`). Subject items
`OI-70`, `OI-73`, `OI-13`, `OI-121`, `OI-126`. Corrective write authorized by Joseph, relayed by the
mediator with the verbatim grant committed at `2266840` before being acted on.

## 1. What was wrong

`docs/orchestration/state/live-state.json` is the hand-authored input to `generate_live_state.py`, which
renders `LIVE-STATE.md` — **the file `CLAUDE.md` routes every new session to first**, on the grounds that
it is "the only file here that answers *what is happening right now*". **Three of its four `blockers` were
false, and two more fields beside them were false**, for at least two days:

| field | what it asserted | why it was wrong |
|---|---|---|
| `blockers[1]` | *"`C_stat` remains prohibited until array `56936015` and validator `56936016` return … 50/50"* | Both terminal; the family returned `FAMILY_COMPLETE_PASS` and **`C_stat` was constructed** (`VL132`, sha256 `6c3b4e00…`). |
| `blockers[2]` | *"Gate 6 Leg 1 is durably BLOCKED …: **no retry**, …"* | The real prohibition is `do_not_retry_unchanged`. Dropping *unchanged* **forbids the CHANGED retry Joseph authorized at `043d572`.** |
| `blockers[3]` | *"Gate 4's estimator-arm disposition remains an independent user decision"* | Decided 2026-08-13 — Joseph selected the annealed arm on physics grounds. |
| `state` | *"task 0 is complete and tasks 1-49 are pending … `C_stat` remains null"* | 50/50, and `C_stat` exists. |
| `next_authorized_action` | *"Let changed array `56936015` and after-any validator `56936016` execute…"* | **Instructs a session to wait for work that finished.** |

**`blockers[2]` is the one that cost something.** A blocker list is read as a veto, so a context-less
session reading `LIVE-STATE.md` would have refused the Gate-6 retry *that Joseph had authorized* — and
`next_authorized_action`, eleven lines below in the same file, stated the qualifier correctly. **The file
contradicted itself**, which is the only reason the defect was findable without an external reference.

## 2. The mechanism, which is the reusable part

**`MANIFEST.tsv` classifies this hand-authored input as `event_status: generated`, with `consumer:
generate_live_state.py` — a script that only ever *reads* it — and `immutable: yes`.**

So the array *looks machine-owned*. A lane that would happily correct a stale sentence in a `*_STATUS.md`
will not touch a file the manifest calls generated and immutable, because editing a generated artifact is
the thing this repo most consistently forbids. **Nobody edits it, so it rots** — and it rots invisibly,
because the renderer keeps producing a fresh-looking document around stale content.

The generator says so itself, in the output of its own freshness check:

> `NOTE: regeneration fixes the sha and timestamp; it does NOT revalidate 'Declared state', which is
> authored prose the generator carries forward.`

**A freshness indicator that certifies only the parts nobody doubted is worse than none**, because
`Observed:` and `Git:` update on every regeneration and thereby vouch for prose that never changed. The
`FRESH` verdict is true and answers a different question than the reader is asking.

## 3. THE AUTHORIZED REMEDY IS A NO-OP, AND IT REPORTS AS APPLIED

`OI-73` prescribes fixing the classification via `MANIFEST-overrides.tsv`, which is the documented
mechanism for exactly this. **It cannot work for this file, and the failure is silent.**

`generate_manifest.py`:

```python
override = overrides.get(rel)
if override is not None:
    classification = override["class"]
    event_status  = override["event_status"]    # <- the override lands here
    successor     = override["canonical_successor"]
    applied_overrides.add(rel)                  # <- and is recorded as APPLIED

if is_runs_or_state(rel):                       # <- runs AFTER, unconditionally
    classification = "MACHINE"
    event_status   = "generated"                # <- discards the override's value
    successor      = ""
```

Measured, not read: appending `docs/orchestration/state/live-state.json → MACHINE / open` to the
overrides file and regenerating produced `overrides=49` and **`event_status=generated`**. The row was
unchanged. The generator exited 0 and printed `wrote docs/orchestration/MANIFEST.tsv`.

**Two distinct defects here, and the second is worse than the first:**

1. `is_runs_or_state()` clobbers any override for a path under `state/` or `RUNS`. So the overrides file
   is inert for **every** `state/` artifact — 45+ ignored and hundreds of tracked rows.
2. **The clobbered override is still added to `applied_overrides`, so it is counted in the `overrides=N`
   summary and is excluded from the "unused overrides" warning at `:389`.** The one diagnostic that exists
   to catch a dead override is blind to this case *by construction*: the entry is not unused, it is
   *used and then discarded*. **A no-op that reports as applied is indistinguishable from success**, and
   the only reason this was caught is that the resulting row was re-read from the file afterwards.

`immutable: yes` is additionally unreachable: `derive_immutable()` returns `"yes"` for
`is_runs_or_state(rel)` regardless of class or event_status, and the overrides file has no `immutable`
column. **So the root cause cannot be fixed from data at all — it needs a code change**, either moving
the `is_runs_or_state` block above the override block or having it yield to an explicit override. That
change touches the classification of every `state/` and `RUNS` row and was **deliberately not made here**:
it is a control-plane code change, it was not authorized, and it should not ride a documentary commit.

## 4. The fix that did work, and why it generalises

`blockers[2]` now enumerates the prohibition **keys** instead of paraphrasing them:

```
do_not_select_passing_subset, do_not_construct_C_ML, do_not_move_central,
do_not_start_leg_2, do_not_retry_unchanged
```

**A paraphrase can drop a qualifier; a key cannot.** *"no retry"* is a lossy rendering of
`do_not_retry_unchanged` and the loss inverted the meaning — but the word `unchanged` lives *inside* the
key, so any faithful copy of the key carries it. The keys are also a content address into
`state/gate6-member-trajectories-result-56847059.json → prohibitions_applied`, so the claim is
falsifiable by set comparison rather than by reading.

**Every blocker now carries a `WITNESS:` naming the artifact that would falsify it.** That is the cheap
half of a check nobody has to write: a reader can refute any row without asking a lane, which is the
property the array lacked while it was wrong.

## 5. What was deliberately not done

* **The witness-field *schema* was not adopted retroactively.** Recommended for new blockers only and
  agreed as such; retrofitting 4 rows into a typed structure would change the file's contract for every
  consumer, for no gain tonight.
* **`log_test.txt` was left in place**, untracked. The hazard raised against it — that
  `generate_manifest.py` walks the filesystem and would inventory it — **does not apply**: the walk is
  rooted at `ORCHESTRATION = REPO/docs/orchestration` (`:24`, `:83`) and the file is at the repo root.
  Verified by set-differencing the manifest's paths before and after: **0 rows dropped, 7 added, all 7
  real files committed by other lanes today, and `log_test.txt` is not among them.** It is not this
  lane's file and was not deleted.
* **`worktree entries: 2` in the committed output is a transient and is not a defect to chase.** The
  field counts the *generating* session's own dirty tree, and a session correcting `live-state.json`
  necessarily has that edit in flight — so the value can never describe the post-commit tree. Here it is
  `log_test.txt` plus this lane's own `live-state.json` edit. Structural, already noted in `OI-73`.

## 6. A `BEN-228` instance found in passing

`OI-73` cites the defective manifest row as `MANIFEST.tsv:616`. **At `HEAD` that line is a different
row** (`state/gate5-extraction-manifest-active-56935553.json`); the manifest has grown by 7 rows since
the citation was written. The row was located by content — `awk -F'\t' '$1=="…/live-state.json"'` — not by
coordinate. `BEN-228`'s rule, met by the finding that cites it: **search for the content, never reuse the
coordinate.**

## 7. What this finding does not establish

* **Why `C_stat` ended up with one builder** against an authorization scoped to two blind builders. The
  ledger records the outcome and the prohibition on claiming independence; it does not record the
  decision. That answer is lane B's or the mediator's.
* **None of the physics** was reproduced — `VL132`'s rank and eigenvalues, `OI-126`'s z-scores and the
  26.5% mass share are cited from the ledger row and the receipts, not re-measured.
* **`blockers[0]` was checked and is believed still true** — a terminal 0/50 does not become untrue — but
  what was verified is that its validator receipt exists, **not** that no subset has since been promoted.
  A blocker asserting a negative cannot be discharged by finding its receipt.
