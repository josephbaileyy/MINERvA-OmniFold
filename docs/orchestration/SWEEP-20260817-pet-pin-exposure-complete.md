# SWEEP — pin exposure across every remaining PET candidate, measured three ways

**Lane E, 2026-08-17.** Completes the partial sweep in
[`RECOST-20260817-pet-items-pin-exposure.md`](RECOST-20260817-pet-items-pin-exposure.md), on the
mediator's instruction to finish it **before writing a line of any fix**.

**No batch job, no compute submitted. Every perturbation restored and byte-compared; the gate
re-checked `INTACT` afterwards.** Executable form: `state/probe-pin-exposure-20260817.py` (extended
in place; the original probe is now its validation stage).

---

## The partial sweep was wrong in two ways, and both were found by extending it

The first pass probed eight files and reported a **binary**: pinned / not pinned. It found `OI-61`'s
second pinned file, which was worth having. It was also incomplete in two directions that its own
"bounded negative" section did not anticipate:

**1. It answered about the wrong file for `OI-64C`.** That row's edit sites are
`verify_executing_copy_is_committed.py` and the two places that must *call* it —
`reconcile_gate5_family.py`'s startup and the next Gate-5 launcher. The first pass probed
`check_canonical_designation.py`, **which is not that item's edit site at all**, and reported it
clean. A correct measurement of an irrelevant file. Both real sites are **PINNED**.

**2. "Pinned / not pinned" is not the state space.** There are at least three states, and the second
pass exhibits all of them:

| state | what it means | how many files, tree-wide |
|---|---|---|
| **PINNED** | a binding the gate resolves; editing turns pre-commit red | 169 |
| **TOLERATED** | pinned *and already drifted*; in `KNOWN_PREEXISTING`, so the gate stays **green** | 4 |
| **clean on the gate** | no binding the gate can resolve — which is **not** the same as unpinned | everything else |

The third row is the dangerous one, and `BEN-322` is why: `verify_hash_bindings.py` cannot resolve a
**role-keyed** digest (`"loader": "<sha>"` with no sibling path), so a file can be compared
fail-closed by live code and still probe "not pinned".

---

## Three instruments, because one instrument answers one question

**INSTRUMENT 1 — path side, complete.** Import `verify_hash_bindings.py`'s **own** collectors and
enumerate every file in the tree carrying a resolving binding, in one pass. **173 files** (169 +
4 tolerated), all git-tracked. Answers *"will editing this turn the pre-commit gate red?"*

This is what removes the first pass's stated limit. That sweep could only answer for *the files a row
happened to name*; membership in a 173-file set is a lookup, so the same question is now answerable
for **any** file, including one no row mentions yet.

**INSTRUMENT 2 — digest side.** `git grep` for the file's **current sha256**. A pin *is* a digest, so
if the content hash is written down anywhere, something can compare against it — including the
role-keyed receipts and hardcoded launcher constants instrument 1 structurally cannot resolve.
Answers *"who else has frozen this content?"*

**INSTRUMENT 3 — perturbation.** The original probe, **demoted to validator.** Instrument 1 predicts
each outcome *in advance*; the probe checks the prediction. Printing a prediction beside an
observation is not a test — a disagreement here is a defect in instrument 1 and the run says so.

```
instrument 1 predicted the gate correctly on 19/19 probes; 0 disagreement(s)
re-check after all probes: INTACT
```

The 19 include two known-pinned positives, **both tolerated-drift files** (predicted green *because*
pinned-and-drifted — the case the old binary could not express), the files instrument 2 flagged that
instrument 1 cannot see, and files clean on both.

### Instrument 2's blind spot is measured, not caveated

A file that has **already drifted** from its pin has its *old* content recorded, so a digest search on
its *current* content finds nothing and it reads clean while being pinned. Exhibited rather than
asserted:

```
docs/orchestration/wakerctl.py        in_inventory=True   digest_sites=0
docs/orchestration/test_wakerctl.py   in_inventory=True   digest_sites=0
```

So instrument 2 both under-reports (drifted pins) and over-reports (a digest can be recorded as
history rather than enforced). **It is a lead generator, not a verdict.** Use it to find what
instrument 1 cannot see, then read the site to learn whether the digest is *compared* or merely
*recorded*.

---

## THE TABLE

`gate` is instrument 1; `digest` is the number of files recording that content's current sha256.

| item | file it must touch | gate | digest sites | routable to an unpinned side? |
|---|---|---|---|---|
| `OI-12` | `uq_fps/corrected/test_fps_corrected_uq.py` | clean | 0 | **n/a — free** |
| `OI-12` | `p4_lib.py` | clean | 0 | **n/a — free** |
| `OI-57` | `pet/train_fullevent_replica.py` | clean | 0 | **YES — this is the unpinned side** |
| `OI-57` | `pet/train_fullevent_nominal.py` | **PINNED** | 15 | avoid; the row already says so |
| `OI-57` | `pet/sbatch_gate5_replica_train_array.sh` | **PINNED** | 1 | avoid |
| `OI-58` | `pet/train_fullevent_replica.py` | clean | 0 | **YES — hop 1 is the whole fix** |
| `OI-58` | `pet/extract_fullevent_fps.py` | **PINNED** | 18 | avoid |
| `OI-58` | `pet/train_fullevent_nominal.py` | **PINNED** | 15 | avoid |
| `OI-60` | `pet/fullevent_fps_dataloader.py` | **PINNED** | 25 † | **NO — see the determination** |
| `OI-60` | `pet/build_fullevent_replica_target.py` | clean | **5** | **NO — instrument 2 catches what 1 misses** |
| `OI-60` | `pet/run_gate2_target_validator.sh` | **PINNED** | 2 | NO |
| `OI-61` | `pet/train_fullevent_nominal.py` | **PINNED** | 15 | **NO — and this is BOTH halves, corrected below** |
| `OI-61` | `pet/train_fullevent_replica.py` | clean | 0 | ~~yes, for the replica-tag half~~ **NO** ‡ |
| `OI-61` | `tests/test_reconcile_gate5_family.py` | clean | 0 | free, but nothing to do there alone |
| `OI-64` (A's) | `docs/orchestration/verify_hash_bindings.py` | clean | 0 | **n/a — free** |
| `OI-64` (A's) | `tests/test_hash_bindings.py` | clean | 0 | **n/a — free** |
| `OI-65` (A's) | same two files | clean | 0 | **n/a — free** |
| `OI-64` (C's) | `pet/verify_executing_copy_is_committed.py` | clean | 0 | the check itself is free… |
| `OI-64` (C's) | `pet/reconcile_gate5_family.py` | **PINNED** | 5 | **…but its CALLER is not** |
| `OI-64` (C's) | `pet/sbatch_gate5_replica_train_array.sh` | **PINNED** | 1 | **…nor is the other caller** |
| `OI-65` (C's) | `pet/reconcile_gate5_family.py` | **PINNED** | 5 | NO |
| `OI-65` (C's) | `pet/atomic_write.py` | **PINNED** | 16 | NO |
| `OI-65` (C's) | `pet/sbatch_gate5_target_family_reconcile.sh` | clean | 4 | instrument-2 exposure only |
| `OI-96` | `pet/check_canonical_designation.py` | clean | 0 | **n/a — free** |
| `OI-96` | `docs/orchestration/verify_hash_bindings.py` | clean | 0 | **n/a — free** |

**† and this is instrument 2 measuring the observer.** That cell read **24** when first run and **25**
after the sibling determination landed, because that document quotes the loader's digest in its
eleven-sites table. **Writing about a pin increments its digest count.** Caught by re-running the
sweep against the rebased tree rather than quoting the pre-rebase number — the count is bound to the
tree being pushed, and both other headline figures (173 bound files, 19/19 predictions) reproduced
unchanged there. It is one more reason the digest count is a lead, not a verdict: it counts
*mentions of a digest*, and a mention is not a comparator.

### What the table changes

**`OI-64C` is not cheap and the first pass said it was.** Its own diagnosis — *"an unwired check is a
check nobody runs"* — is right, and **wiring is the expensive half**: both callers are pinned. The
check file being free is irrelevant, because a check nothing calls is exactly the defect.

**`OI-65C` is the most exposed item on the list**: two of its three files are pinned and one of them,
`atomic_write.py`, has its digest in **16** receipts. Its own row already says the repaired tool
*"has never run against the campaign"* and that promotion needs a deployment — so it is blocked
behind `OI-64C`, whose wiring is blocked behind two pins.

**`OI-58` is confirmed genuinely cheap, on the strongest evidence in this sweep.** Its row's claim —
*"the fix is available entirely on the unpinned side and needs no re-issue and no repin"* —
**reproduces on both instruments**: `train_fullevent_replica.py` is clean on the gate **and records
zero digest sites**. That is a fact its row asserted from a pin-list read; it is now measured two
independent ways.

**`OI-96`, `OI-12`, and A's `OI-64`/`OI-65` are clean on both instruments.** Not free — `OI-96`
changes pre-commit check 6, `OI-12` is the FPS lane's by its own audit, A's `OI-64` records itself
`RESOLVED / INSTALLED` — but none carries hidden pin cost.

**~~`OI-61` splits.~~ ‡ IT DOES NOT, AND THIS TABLE SAID IT DID.** Struck the same day, by attempting
the fix — see the correction below, which is the more useful half of this document.

### ‡ THE CORRECTION: the file an edit LIVES IN is not the file that VALIDATES it

This table graded `OI-61(b)` — *"pass a replica-specific tag"* — **routable**, because the row names
`train_fullevent_replica.py` as the edit site and that file is clean on both instruments. **Wrong.**

`train_fullevent_replica.py` calls `nominal.main([… "--tag", "nominal" …])`, and
`train_fullevent_nominal.py:325` **declares the tag's domain**:

```
ap.add_argument("--tag", default="nominal", choices=["nominal", "floor"], …)
```

So the one-line change in the unpinned caller is **rejected by the pinned callee.** Measured rather
than argued:

```
$ python3 nd-unfolding/pet/train_fullevent_nominal.py --tag replica_07 …
train_fullevent_nominal.py: error: argument --tag: invalid choice: 'replica_07'
                            (choose from 'nominal', 'floor')          exit 2
```

`state/probe-oi61b-tag-route-20260817.py` then applies the **real minimal diff** for each candidate —
not a comment append, because a comment cannot distinguish the edit that works from the edit that
compiles — and asks the gate:

```
the edit the ROW names        train_fullevent_replica.py    gate -> green   (and does not work)
the edit that makes it WORK   train_fullevent_nominal.py    gate -> RED
2/2 as expected
```

**And the second-order cost is the same one that priced `OI-60`.**
`validate_gate5_training_artifacts.py:189-191` compares every replica receipt's recorded code digest
against `EXPECTED_CODE`, whose key for this file is — with no irony intended by its author —
**`nominal_driver_unmodified`**. Editing the driver falsifies the name of the constant that pins it,
and invalidates the archived 50 the same way a loader edit does.

**So `OI-61` does not split: both halves are in the pinned driver, and both ride whatever re-issue
`OI-60` rides.** The useful output is not a fix but a corrected specification — the next lane must
edit the driver's `choices`, not just the caller, or argparse will reject the diff at exit 2.

**What this does to the sweep's method, stated because it is a real limit and not a slip:**
instruments 1 and 2 answer *"is this file frozen?"*. Neither answers *"does this edit work?"* — a
question that can reach a second file through an argument contract, an import, a schema, or a
declared enum, none of which is a hash. **The probe must apply the diff that achieves the goal, not
the diff the row describes**, and the two are only the same when nobody has checked.

---

## The bounded negative, restated where it now actually sits

The first pass's limit was *"the files the rows name."* That limit is gone for the pin question:
instrument 1 covers the tree. **Two limits replace it, and they are narrower and stated so they can
be attacked:**

1. **The item→file mapping is still mine.** I read each row and the map for the site the fix must
   touch. If an item's fix reaches a file neither names, this table does not cover it — but checking
   that file is now a set lookup, not a new sweep.
2. **`digest sites > 0` with `gate = clean` means "look", not "blocked."** Instrument 2 cannot tell an
   enforced comparison from a historical record. For `OI-60`'s `build_fullevent_replica_target.py` I
   read the sites and found a live comparator; I have **not** done that read for `OI-65C`'s
   `sbatch_gate5_target_family_reconcile.sh` (4 sites), and it is the one cell in the table where
   "routable?" is answered *unknown* rather than yes or no.

**And the rule the first pass got right stands unchanged, because instrument 1 does not see
everything either:** probe before writing, **and run the real gate again after writing** — the second
run is the only one that sees the file you actually had to touch.
