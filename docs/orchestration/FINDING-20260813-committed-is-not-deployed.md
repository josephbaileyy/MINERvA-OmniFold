# FINDING 2026-08-13 — "committed" and "running" are two different facts, and the obvious check confuses them

**BEN-156.** Lane C (PET). Second instance of this class in one day; the first nearly shipped an
unrepaired training driver.

**One-line version:** a commit lands and everyone believes the executing copy changed. Nothing
copied it. And the natural defence — *"check that the running file's content is in the repo"* —
**passes on exactly the file you were trying to catch**, because the stale version is also
committed.

## The two instances

| | what was committed | what was executing | how it surfaced |
|---|---|---|---|
| `OI-57` | the `train_fullevent_replica.py:112` repair, on `main` | `GATE5_CODE_ROOT` = `/pscratch/sd/j/josephrb/gate6traj-reconcile-56847059`, which no commit reaches | noticed while reading the launcher for an unrelated reason |
| this one | `reconcile_gate5_family.py` extended by a peer at `ac540d5` | `/pscratch/sd/j/josephrb/gate5-reconcile-lanec/reconcile_gate5_family.py`, still at `69c577b`'s content | noticed by hashing the deployed copy on a hunch |

Both were caught by attention rather than by mechanism, which is the part that does not scale. And
both have the same signature: **a git sha in a receipt is evidence about the repo, not about what
ran.** Every report we write conflates the two, because the repo sha is the one that is easy to get.

The consequence of the second one, had it gone unnoticed, is worse than it first looks. A run
against the stale reconciler would not have crashed or produced anything odd. It would have written
a confidently-formatted family artifact — same schema, same field names, `tool_sha256` present and
correct — computed from **superseded checks**, and nothing in the output would have said so. The
`tool_sha256` field would have recorded the stale hash faithfully, and nobody compares that field
against anything.

## The trap inside the fix

The reflexive check is a boolean: *is this content in the repo?* It is wrong, and it is wrong in the
worst available direction.

The stale reconciler **was** committed. It is in the repo's history. It hashes to a real blob that
`git cat-file -e` finds instantly. A boolean check returns **true** on it. The check passes on
precisely the input it exists to reject, and now you have a green light with a stale binary behind
it.

So the tool committed here reports **three** states and refuses to collapse them:

```
CURRENT              content == the blob at that path in HEAD.  The only good state.
STALE_BUT_COMMITTED  content is committed, but is NOT HEAD's.   <-- the trap state
UNCOMMITTED          content is in no commit at all.
```

`STALE_BUT_COMMITTED` and `UNCOMMITTED` are kept apart because **they have different repairs**:
re-deploy, versus find out who hand-edited a file on scratch. Collapsing them into `FAIL` would
lose the only piece of information that tells you what to do next.

There is a fourth state that looks like pedantry and is not. `git cat-file -e` succeeds on a blob
that someone `git add`ed and never committed — the object is in the database, no commit contains it.
A tool that tested object *existence* would report that as committed provenance. That is
`IN_ODB_UNREACHABLE`, and there is a test for it, because **object existence is not reachability**.

Exit codes are separated on the same principle as the states: **`2` for "could not look"** (bad
usage, `--repo` is not a git tree) and **`3` for "looked and found drift"**. One status for both
would let a mistyped path read as a clean bill of health — the write-condition rule applied to an
exit code.

## Power-tested on the real artifact, not only on fixtures

Twenty fixture tests prove the logic. They do **not** prove the tool would have caught *today's*
drift, so the actually-drifted file was reconstructed and fed in:

```
$ git show 69c577b:nd-unfolding/pet/reconcile_gate5_family.py > /tmp/what_was_running
$ sha256sum /tmp/what_was_running
e536540df5dce1f4c8947f7ccb57193be935c5b5d701296c3ef1440d4de90467
```

That sha is not a synthetic old version. `e536540d` is the exact value recorded as `tool_sha256` in
`state/gate5-throughput-collapse-20260813.json` — **it is the file that was executing at 14:55 PDT
today.**

```
$ verify_executing_copy_is_committed.py --repo . --pair /tmp/what_was_running=nd-unfolding/pet/reconcile_gate5_family.py
STALE_BUT_COMMITTED  /tmp/what_was_running  (nd-unfolding/pet/reconcile_gate5_family.py)
  head=590affaf0e61beaeb8bf5374c69301ae03a8b25f executing=40b50547a8b0bf5909cf7d889f83d8a93efc8ee8
exit 3
```

And the other direction, on all three copies that actually exist on scratch today: **3 of 3
`CURRENT`, exit 0.** A checker that only ever passed would have shown the second result and nothing
else, which is why both halves are recorded.

The three copies were found by `find /pscratch/sd/j/josephrb -maxdepth 6 -name
reconcile_gate5_family.py`, not from memory. **There are three, not one** — two of them
(`gate5-target-recon.IQaLcx`, `gate5-target-validator-frozen-70be58a`) are not this lane's
deployments and nobody owns re-deploying them. A report naming only the copy I deployed would have
been incomplete in the direction that matters.

## A name I had to fix inside the tool that exists to catch bad names

The helper was first written as `commits_containing_blob`, docstring claiming *"commits whose tree
contains this blob."* The live negative control listed **`ac540d5`** — the commit that **removed**
that content. `git log --find-object` searches **diffs, not trees**, so it names both the commit
that introduced the content and the commit that replaced it.

The output contradicted the name. Renamed to `commits_whose_diff_touches_blob`. The reachability
conclusion is unchanged and still sound — if a diff touches the blob, some tree held it — but the
name asserted more than the command measures, which is `BEN-149`'s shape appearing *inside a tool
written to catch that class*. Recorded rather than quietly renamed, because the interesting part is
that it was caught by reading output against a name, not by review.

## Two zeros in this same pass that were about my search, not about the tree

Worth recording because they are the same shape as the defect fixed at `69c577b`:

- `find /pscratch/sd/j/josephrb/gate5_replicas/... -name GATE5_REPLICA_TRAINING_RECEIPT.json` → **0**.
  The path was **inferred**. The real root is
  `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50`, read out of the
  previous run's own artifact, where there are 23.
- Two guessed reconciler paths → **ABSENT** for both. An unbounded `find` located three.

Neither zero was reported as anything. **An absent-verdict is a statement about the search until it
names the path it searched** — which is the standing rule, and it earned its keep twice in twenty
minutes.

## The habit, and why the tool exists instead of just this paragraph

> **Before trusting a run, hash the file that is about to execute and compare it to HEAD's blob for
> that path — and treat "committed but not current" as a distinct failure, not a pass.**

`CLAUDE.md` says it better than this finding can: *a document costs tokens in every future session
forever; a check costs zero and cannot be skipped. Prefer the executable form of any rule you are
tempted to write down.* So the deliverable is
`nd-unfolding/pet/verify_executing_copy_is_committed.py`, and this file exists to explain why its
middle state is the whole point.

**It has no caller yet.** That is a real gap and it is `OI-64` rather than left implied — an
unwired check is a check nobody runs, which is how this class of defect got two instances in one
day in the first place.

## A third instance turned up while filing this one

Registering these two files meant running `docs/orchestration/generate_manifest.py`. It indexes what
it can **see** — including gitignored and untracked files — so run from this worktree it deleted
**39 rows** for `__pycache__/`, `.pytest_cache/`, `runs/*.log` and `state/locks/*.lock` that exist in
the main checkout and not here. All 39 verified gitignored or untracked, none in `HEAD`.

Same class, one level up: **a generated index whose content depends on which tree generated it**, so
*"just regenerate it"* is a silent deletion in every other tree, and whoever regenerates last wins.
Committed as a **superset** instead — regenerated rows plus every `HEAD` row the regeneration
dropped, asserted to lose nothing (`+48 / −24`, the 24 being metadata-only updates for files edited
today, and 24 tracked files newly registered — including nine `FINDING-20260813-*.md`, eight of them
other lanes', that the manifest had never listed; 5 of the 14 findings dated today were registered
before this pass, 14 of 14 are now). Not filed as its own `BEN`: it is this finding's mechanism
applied to a generated file, and
it belongs with the deployment-parity story rather than beside it.

## Related

- `OI-57` — the first instance: a repair committed to a tree the executing array does not read.
- `OI-64` — wiring this check into the Gate-5 launcher and the reconciler's own startup.
- `BEN-149` — a name that claims verification and thereby suppresses the check.
- [`state/gate5-deployment-parity-20260813.json`](state/gate5-deployment-parity-20260813.json) — the
  measurement, with every operand.
