# FINDING 2026-08-14 — Two numbers inferred from symptoms, and one was a seven-hour collapse that never happened

**`BEN-233`.** Lane C (PET).
**Status:** mitigated by two flags, not by vigilance. The mediator's throttle figure is corrected.
**Evidence:** measured commands and their output in
[`state/gate5-cstat-spec-measurements-20260814.json`](state/gate5-cstat-spec-measurements-20260814.json)
under `ARRAY_STATE_MEASURED_THIS_TURN_not_recalled`.

---

## Half one: the collapse that wasn't

Diagnosing extraction array `56936015`, I ran `date -u` (`11:56:46Z`) and read `sacct` completion
timestamps in the same turn. The last `End` was `04:56:39`. Read as UTC, that is **seven hours with no
completions** on an array with 35 tasks pending — a stalled array, and the kind of thing a lane escalates
immediately. I was one step from reporting it to the mediator, who would have taken it to Joseph.

What stopped it was that **the gap was suspiciously round.** Seven hours is exactly `UTC-0700`, and a
genuine stall has no reason to land on the hour. `sacct` prints **local time**; `date -u` prints UTC; I
had asked for the two clocks and then compared them as one.

Verified before use, rather than assumed:

```
SLURM_TIME_FORMAT="%Y-%m-%dT%H:%M:%S UTC%z" sacct -j 56936015_13,56936015_14 -X -n -P \
  -o JobID,State,Elapsed,Start,End
56936015_13|COMPLETED|00:13:44|...T04:42:55 UTC-0700|...T04:56:39 UTC-0700
```

Task 13 finished at `04:56:39 PDT` = `11:56:39Z` — **two minutes before I looked.** Throughput was
healthy: 14 tasks over `02:55:52 → 04:56:39 PDT`, ~8.6 min/task wall-clock at ~2 concurrent, ~14 min
each, except task 0 at `00:02:05` because it reused the predecessor's complete push.

There was a second, independent tell available and I had already printed it: task 14's `Elapsed` read
`00:09:10` against a `Start` of `04:48:11`. Under the UTC misreading those are inconsistent by exactly
the same 7 h. **The evidence contradicted itself on screen and I nearly read past it** — which is the
`BEN-077` ingredients heuristic working, in a case where the operands were already on the page.

## Half two: the throttle

The array's concurrency limit was reported to me as **2**. It is **10**:

```
scontrol show job 56936015 | grep -o "ArrayTaskThrottle=[0-9]*"
ArrayTaskThrottle=10
```

confirmed by the launcher (`--array=0-49%10`) and the submission receipt (`concurrency_cap: 10`). Two
concurrent tasks was **observed occupancy**, not a configured cap. Every pending task reports
`(Priority)`, so the constraint is queue priority and not our own throttle — and the proposed remedy,
raising the cap, would have bought **nothing**. Worth noting because it was offered as worth ~hours.

## The common shape, and why it is not "be careful"

Both halves are the same error: **a number inferred from a symptom rather than read from the thing that
sets it.** Two running tasks is a symptom; `ArrayTaskThrottle` is the setting. A stale-looking timestamp
is a symptom; the timezone offset is the fact. In both cases the authoritative value was one command
away and the inferred value was wrong.

This repo already has the rule — *"every ID, rank, count, and queue name in a status report must come
from a command run in the same turn"* (`BEN-027`). Both numbers here **did** come from commands run in
the same turn. That is what makes this a distinct finding rather than a repeat: `BEN-027` is satisfied by
a fresh `squeue`, and a fresh `squeue` is exactly what produces "2 running." **The rule has to extend
from freshness to authority: run the command that reads the setting, not one that exhibits its
consequences.**

Also note which side the near-miss fell on. Both errors pointed toward **false alarm** — a collapse that
had not happened, a cap that was not binding. A lane that escalates a phantom stall spends the
mediator's and Joseph's attention and, worse, makes the next real stall report cheaper to discount.

## Third and fourth instances the same day, and the general form

**This finding was filed on the first instance. Three more followed within hours, two of them mine.**

2. **A validator that looked like it passed a partial family.** I compared an array measurement taken
   at **06:27 PDT** against a validator start at **07:30 PDT** and read the gap as "nothing happened",
   concluding the Gate-5 completeness gate had certified an incomplete family with exit 0. **False:**
   the array's last task ended **07:24:12** and the validator started **07:30:39** — six minutes later,
   `afterany` behaving correctly. Twenty remaining tasks at ~14.5 min and ~7 concurrent is ~41 min,
   *entirely consistent with the 45–65 minute ETA I had published myself an hour earlier.* I had the
   number that refuted me and did not apply it.

3. **The mediator, one message after I reported instance 2, checking my work.** It read commit times
   with `TZ=UTC git log --date=format:…` — and **`format:` renders in the commit's own offset;
   only `format-local:` honours `TZ`.** A `-04:00` timestamp became an apparent UTC one, manufacturing
   a **four-hour** gap that looked like `C_stat` being built before its own extraction family
   validated. **Also false:** with `%cI`, build `14:41:14Z`, validator done `14:31:33Z`, array last
   task `14:24:12Z` — build 9m41s *after* validation, correct order.

**The git mechanism, verified by lane A on commit `6b68d12` in its own tree rather than relayed:**

```
%ci                          2026-08-12 22:53:04 -0400
TZ=UTC --date=format:        2026-08-12T22:53:04          <-- TZ IGNORED, offset STRIPPED
TZ=UTC --date=format-local:  2026-08-13T02:53:04          <-- TZ honoured
%cI                          2026-08-12T22:53:04-04:00    <-- frame carried, cannot be misread
```

**`TZ` has no effect on `--date=format:`** — that renders in the **commit's own** offset, and only
`format-local:` honours `TZ`. So `TZ=UTC git log --date=format:…` *looks* like it produced UTC and
produced a `-04:00` wall clock instead.

**And the git variant is strictly nastier than the `sacct` one, in a specific way lane A identified:**
`format:` **strips the offset** unless the format string asks for `%z`, so **there is nothing printed
to compare against.** My 7-hour discrepancy was catchable because it landed exactly on `UTC-0700` and
a round number is a tell. The mediator's 4 hours was also exactly the offset — but with no offset
displayed anywhere, the tell was unavailable. **A mitigation that depends on noticing a suspiciously
round number does not survive a formatter that hides the number.**

**THE GENERAL FORM, which is what makes this more than three anecdotes:**

> **Establish the frame before comparing two timestamps, and prefer a representation that has no frame
> to get wrong.** Epoch seconds or `%cI`/ISO-8601-with-offset cannot be misread; `sacct`'s default
> display and `git --date=format:` both render in a frame the reader supplies from assumption. Every
> instance here was two correct numbers subtracted in the wrong frame.

**What actually stopped all four was the same act: checking before escalating rather than after.** In
instances 2 and 3 the check took one command and the escalation would have cost a lane's attention and
Joseph's. Worth noticing that it worked twice inside ten minutes — the reflex is functioning even
though the underlying error keeps recurring, which is the argument for making the *representation*
safe rather than relying on the reflex.

## Mitigation

Neither half needs vigilance; both need a flag.

- **Prefer a representation that cannot omit the frame, over remembering to ask for it.** For git,
  `%cI` (ISO-8601 with offset) or `%ct` (epoch); for Slurm, epoch or `SLURM_TIME_FORMAT` with `%z`.
  This is lane A's generalisation and it is better than the tool-specific rule this finding shipped
  with: the original said *print the offset*, which is right for `sacct` and cannot help with
  `--date=format:`, because that formatter drops the offset whether or not you remember to want it.
- **Never mix `date -u` with a tool's default time display in one turn** — ask both clocks in the same
  representation, or convert both to epoch before subtracting.
- **Read `ArrayTaskThrottle` from `scontrol show job`** before reasoning about concurrency, and treat
  the running count as occupancy. Cross-check the pending **reason**: `(JobArrayTaskLimit)` means the cap
  binds, `(Priority)` means it does not.

One more that earned its place this turn: `sacct -X` **compresses a pending array range into a single
row** and reported `PENDING 1` where `squeue -j <id> -r` showed **35**. The campaign already knows this
(`squeue -r` for per-task truth) and it held again here.
