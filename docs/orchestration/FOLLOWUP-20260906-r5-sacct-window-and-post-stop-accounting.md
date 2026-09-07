# FOLLOW-UP 2026-09-06 — the 30-day `sacct` window, and accounting for jobs that finish after it

**CITABLE FOR:** the deadline on preserving R5 accounting evidence; the route by which jobs finishing
after that deadline are metered; the ownership of both acts.

**NOT CITABLE FOR:** any spend figure, any authorization to run, or any relaxation of R5. Nothing
here permits omitting anyone's expenditure.

**Status:** OPEN. Opened by the landing of
`FINDING-20260906-r5-meter-undercounted-requeue-attempts.md` (§7), on the decision owner's
instruction of 2026-09-06.

---

## 1. The ruling this record exists to satisfy

> *"Record the 30-day query-window follow-up with an owner: preserve accounting before
> 2026-10-02T13:44:27Z, and identify how any later-finishing jobs will be accounted for. **This is a
> query limitation, not permission to omit their expenditure.**"* — the decision owner, 2026-09-06.

That last sentence governs everything below. A job whose accounting is harder to retrieve has not
spent less.

## 2. The limitation

NERSC rejects any `sacct` window wider than 30 days:

```
sacct: error: Too wide of a date range in query
```

Measured by bisection: 30 days accepted, 31 rejected; the limit is on the **span**, not the lookback;
`-j <jobid>` bypasses it; `--name=` does not.

`r5_meter._sacct_argv()` queries **t0 → now**. Its span therefore reaches 30 days at

> ### `2026-10-02T13:44:27Z`

which is **2 d 13 h 44 m 27 s after** the R5 stop date of `2026-09-30T00:00:00Z`. The meter is inside
the limit for the whole campaign. From that instant the unmodified query errors, no receipt is
produced, and everything downstream fails **closed** (`r5_meter check` returns 4; `campaignctl`
refuses every compute item). Nothing silently under-reports. What is lost is the *ability to measure*,
not the correctness of what was measured.

## 3. Owner

**The orchestration lane** — the owner named for R5 accounting in
`DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md` §4 item 6 ("a `WAKER`/accounting entry
that meters `R5` from t0, since a stop nobody measures is not a stop"). The repair that this record
follows was that item's execution; these two acts are its remainder.

The owner holds **two dated obligations**, below. Neither is discharged by this record, and neither
is assigned to the integration lane that wrote it.

## 3a. Concrete owner — ACCEPTED 2026-09-07

**The orchestration lane's ownership in §3 is institutional. This section names the session that
holds it.**

**Accepted by:** session **`preflight [e11e6d]`**, on the decision owner's assignment of 2026-09-07.
Transcript: `https://claude.ai/code/session_01Kv6jeUoFeyXewZsG6am3by`.

**Acceptance is not durability, and this session is not the mechanism.** A chat session ends. The
obligations below are dated, and the deadline is three weeks out, so the continuation is carried by a
scheduled agent and by this record — not by anyone remembering.

### Durable continuation

**Reminder:** Claude Code routine **`trig_01Qog2yDeBo9k8fTv7BHUDd9`**, one-shot, fires
**`2026-10-01T09:00:00Z`** — `1 d 9 h` after the R5 stop, `1 d 4 h 44 m` before the §2 deadline. It
reads this record, reports whether it is still OPEN, lists the §4.3 ids, and alerts the decision owner
that Obligation B needs a host with `sacct`. Manage it at
`https://claude.ai/code/routines/trig_01Qog2yDeBo9k8fTv7BHUDd9`.

**That routine cannot discharge anything.** It is a cloud agent with no NERSC access; it cannot run
`sacct`. It raises the alarm and hands over the commands. **Whoever performs Obligation B needs SSH to
a host with `sacct`.**

**Connector state — measured 2026-09-07, and it changes what “alerts” above can mean.** The routine
has **zero connectors attached**: `mcp_connections: []`, and in its session config `mcp_servers: []`
and `owner_tagged_mcp_servers: []`. Otherwise it is unchanged and still armed — `enabled: true`,
one-shot, `run_once_at` / `next_run_at` `2026-10-01T09:00:00Z`, model `claude-sonnet-5`,
`allowed_tools: [Bash, Read, Glob, Grep]`, source the GitHub repository, same trigger id throughout.

*Provenance, because the two halves have different authors.* **The removal is the decision owner's**,
authorized at the routine level only and performed by session `preflight [e11e6d]` with a
`RemoteTrigger` `update` carrying `clear_mcp_connections: true` at `2026-09-07T11:07:14Z`. **The empty
state is `preflight`'s measurement**, confirmed by three reads that are not the write's own echo: a
separate `get` on the trigger, an account-wide `list`, and a further `get` after a prompt-only update
at `2026-09-07T17:34:08Z`. All three returned `mcp_connections: []`. I have no way to observe connector
state from here and did not re-derive it; it is recorded as their measurement and attributed.

**The consequence for this record: the routine cannot notify anyone.** With no connectors it can read
the repository and write a final report, and nothing else. “Alerts the decision owner” above therefore
means *it produces a report that someone must open* — the alarm is pull, not push. Whoever relies on
this reminder should plan to look at
`https://claude.ai/code/routines/trig_01Qog2yDeBo9k8fTv7BHUDd9` on or after the fire time rather than
expect a message to arrive.

**Two limits, so this is not read as more than it is.** The removal was routine-scoped, so the account's
own connectors are untouched and were *not* verified — the routine API gives no way to. And this is a
measurement at an instant, not a guarantee about `2026-10-01`: the five write-capable connectors
(Gmail, Slack, Drive, M365, Claude_Code_Remote) were attached without being asked for in the first
place, which is precisely why the state is worth re-checking at fire time rather than assumed. The
routine's prompt now also forbids contacting anyone through any connected tool; that is belt-and-braces
behind the detachment and the weaker of the two, since it depends on a model reading an instruction
correctly while the detachment does not.

**This supersedes the open item that read “five write-capable connectors attached to
`trig_01Qog2yDeBo9k8fTv7BHUDd9`; detaching them is the decision owner's call.”** It was his call, he
made it, and it was carried out and then measured. The blocker is closed; only the re-check at fire
time survives it.

**Merged head — verified 2026-09-07.** This section and the preserved snapshot reached the
repository's default branch (`refs/heads/main`, which is what the routine clones) at
**`0feab57d7aebf176a77275c7b2eec1abf3db90a5`**. Verified independently of the landing lane, by
reading the default branch itself: `e81e146d` is an ancestor; §3a is present and names the owner;
all three files of `docs/orchestration/state/preflight-20260907-r5-followup/` are present with the
snapshot at `ed86508e…` and the capture at `31c74b42…`, byte-identical to the branch; and
`docs/orchestration/state/r5-meter-receipt.json` is **still absent**, with **0** commits touching it
on any ref. Landing this evidence armed nothing.

**The routine clones the repository's default branch, so it can only see what has been merged there.**
Its first step is therefore a precondition check: if this section or the preserved snapshot directory
is absent from the branch it clones, it must lead its output with `MISSING CONTEXT`, name
`lane/r5-followup-ownership-20260907` as pushed-but-unmerged, and continue with the alert regardless —
the deadline is real whether or not the record reached `main`. It fails loudly rather than reminding
successfully about a record that is not there.

**Instructions to whoever picks this up, in order:**

1. Read §4 and §5 of this record. They carry the exact commands.
2. Take the **final** Obligation A capture before `2026-10-02T13:44:27Z`. The 2026-09-07 snapshot
   under `docs/orchestration/state/preflight-20260907-r5-followup/` is **insurance, not discharge** —
   spend continued accruing after it.
3. Re-read §4.3's outstanding ids from the *final* capture, not from the snapshot.
4. Meter later finishers per §5, and heed its trap: remove the superseded `RUNNING` rows for exactly
   those ids before concatenating, and nothing else.
5. **Do not write `docs/orchestration/state/r5-meter-receipt.json`.** Preserving evidence does not
   authorize arming compute admission; that is a separate decision belonging to the decision owner.

### Obligation A — early snapshot PERFORMED 2026-09-07, record still OPEN

Committed at `docs/orchestration/state/preflight-20260907-r5-followup/`, measured with the **landed
repaired meter** (`383eec66…`, byte-verified, run from isolated scratch; the cluster checkout was not
modified):

| | |
|---|---:|
| capture sha256 | `31c74b422aa1889e351042e93ab567035b5907bd0279362e3666fb6dbc246e86` |
| snapshot sha256 | `ed86508e35b0f1dc0999cf95a3a6d1199682d8309bfc9475500039a876369b9b` |
| CPU task-hours | **`13.064722222222223`** |
| GPU task-hours | `0.0` |
| attempts / task ids | `1155` / `1` |
| **§4.3 outstanding** | **`57712764`** |
| rows with `End=Unknown` | `0` — §5's trap does not apply to *this* capture |

**Status remains OPEN.** `57712764` is non-terminal and still accruing at `0.67`–`0.69` CPU
task-hours/day (per-tick cost `8.4`–`8.9` s at 288 ticks/day; see the snapshot README and
`FINDING-20260906-r5-meter-undercounted-requeue-attempts.md`), so both the final capture and Obligation B are outstanding.

## 4. Obligation A — preserve the accounting **before `2026-10-02T13:44:27Z`**

Before that instant, on a host with `sacct`:

1. Capture the full window with the meter's own field layout and flags:

   ```bash
   TZ=UTC SLURM_TIME_FORMAT=%Y-%m-%dT%H:%M:%S sacct --user "$USER" -X -D \
     --parsable2 --noheader \
     --starttime 2026-09-02T13:44:27 --endtime now \
     --format=JobID,JobName,State,ElapsedRaw,Partition,Start,End,AllocTRES \
     > r5-window-preserved.psv
   ```

2. **Commit that capture as evidence**, with its sha256 recorded. Once the deadline passes it cannot
   be reconstructed by this query, so an uncommitted capture is a capture that does not exist.
3. **Record the JobIDs of every task not in a terminal state** at capture time — the jobs R5 §3 lets
   run to completion with their spend counted. Those ids are the input to Obligation B, and a job
   whose id was never written down is a job whose spend cannot later be demonstrated.

## 5. Obligation B — meter the jobs that finish afterwards

`-j <jobid>` bypasses the span limit, so a later-finishing job remains measurable indefinitely:

```bash
TZ=UTC SLURM_TIME_FORMAT=%Y-%m-%dT%H:%M:%S sacct -j <ids from §4.3> -X -D \
  --parsable2 --noheader \
  --format=JobID,JobName,State,ElapsedRaw,Partition,Start,End,AllocTRES \
  > r5-residual.psv
```

Feed the result to `r5_meter.py measure --from-file`, which accepts any dump in that layout.

### ⚠ The combining step has a trap, and it is the repaired meter working correctly

A job that was **running** at the preservation capture appears there with `State` `RUNNING` and `End`
`Unknown`. The same job appears in the residual capture as `COMPLETED`, with the **same `Start`** and
a real `End`. Concatenating the two files naively gives the meter two rows sharing `(JobID, Start)`
that disagree about `End`, and it **refuses the whole dump**:

```
conflicting End for execution attempt of task identity <id> started <ts>
```

That refusal is deliberate — it is the defect the review caught, failing closed as designed, because
those fields cannot distinguish "two observations of one execution" from "two executions that started
in the same second". **The operator's act is to remove the superseded `RUNNING` rows for exactly the
ids in §4.3 from the preserved capture before concatenating**, so each execution is represented once,
by its final observation. Removing anything else, or removing a row whose id is not in that list, is
falsifying the evidence.

The alternative — re-querying the whole window in chunks — is **not** available from the tool today:
chunking is deliberately not implemented, and implementing it would be a change to the meter, not an
operator action.

## 6. What this record does not do

It authorizes no run, no submission and no spend. It does not write, and does not permit writing, an
operational receipt at `docs/orchestration/state/r5-meter-receipt.json` — doing so and committing it
arms compute admission queue-wide, which is a separate decision (see
`FINDING-20260906-r5-meter-undercounted-requeue-attempts.md` §8). It does not extend the stop date,
alter t0, or move either ceiling. It does not discharge itself: it is open until the owner performs
Obligation A, and until every id recorded under §4.3 has either reached a terminal state and been
metered under Obligation B, or been shown never to have existed.
