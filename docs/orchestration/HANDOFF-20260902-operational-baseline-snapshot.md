# Operational baseline snapshot — measured 2026-09-02, window 11:52Z–12:10Z

**CITABLE FOR:** the measurements in §1–§9, each of which names its command and its denominator;
the "cannot be established" list in §10; and the fact that at `52cbda90` the local checkout was
clean apart from six untracked paths.

**NOT CITABLE FOR:** any authorization. Not a Gate-1 or Gate-2 clause, a readiness or fitness
finding, discharge of `F-1(b)`, expiry of `FREEZE-20260830-k0-deployment-7ac0edec.md`, closure of
any `OI-*`, adoption of any covariance, a pin move, a scheduler write, or a publication claim.
**Gate 2 remains FAIL.** PET `C_stat` remains `EXISTS — UNVERIFIED, PAIRING DECLINED`. The five
Gate-6 prohibitions in §8 are reproduced as keys and must not be paraphrased.

**STATUS: UNTRACKED and UNCOMMITTED, deliberately.** Under `AGENTS.md`'s rule that a result is live
only once its records land in a commit, **nothing here is live evidence** — it is a measurement
report for routing. It sits at the repository root alongside the other untracked `HANDOFF-*` files
rather than in `docs/orchestration/`, because `MANIFEST.tsv` covers only `docs/orchestration`
(measured: 706 of 706 rows) and a new document there would need an override row and a `CATALOG.md`
route to be visible to the router at all.

**Every field below is volatile.** `origin/main` had moved 124 commits in the 5 days before this was
taken. Re-measure before quoting; the commands are given so you can.

**Anchor:** `main` at `52cbda906bfeb239aa47afbdb3ba829023e61607`, which was also live
`origin/main` at 11:52Z.

Read-only. Zero repository mutations by the measuring session (verified after the fact: HEAD
unchanged, the same 6 untracked paths, 0 stashes, 6 worktrees, local ref set md5
`c5576547563bc4ada04b4fb95630ed87`). This file is the 7th untracked path and was written
afterwards, on request, so that other sessions have a durable pointer. No worktree was created —
see §0.

Clock: the measuring shell was **UTC+02:00**. `ssh-keygen -L` and `ls -la` print LOCAL; `sacct` and
`squeue` were asked in UTC explicitly.

---

## 0. Method and its limits

- **No isolated worktree was created**, deliberately. This task requires zero writes, and
  `git worktree add` would (a) write the shared `.git/config` and `.git/worktrees/`, and (b) perturb
  the worktree inventory that §3 measures. Every read below ran in the canonical checkout with no
  write path. Flagging it because `CLAUDE.md` prescribes an isolated worktree for audit work.
- Remote refs were read with `git ls-remote` (writes nothing), **not** `git fetch`, so no
  remote-tracking ref moved. A cached `origin/main` can only understate a push; `ls-remote` removes
  that failure mode entirely.
- Every "zero" below is accompanied by a positive control, because a well-formed wrong query and a
  dead transport both return zero rows.

---

## 1. Local repository — MEASURED 11:52Z

```
git rev-parse HEAD; git symbolic-ref -q HEAD
git status --porcelain=v1 -uall
git for-each-ref refs/heads refs/remotes refs/tags
git ls-remote origin ; git ls-remote analysis-note
```

| field | value |
|---|---|
| HEAD | `52cbda906bfeb239aa47afbdb3ba829023e61607` on `refs/heads/main` |
| HEAD commit | 2026-09-02T12:46:36+02:00 — `[ruling] Regenerate MANIFEST after OI-188…` |
| `origin/main` **live** (`ls-remote`) | `52cbda906bfe` — **identical to local main** |
| `analysis-note/main` **live** | `d0c3768ea1e53ec80b84b92eccc9244a45fa3a8c` — identical to the cached ref |
| dirty paths | **6 of 6 untracked (`??`), 0 tracked modifications** |

Everything committed on `main` is pushed. Denominator: 707 MANIFEST rows / 706 tracked files
(control-plane count).

### 1.1 The six untracked paths — audit-reported, NOT committed, therefore NOT live evidence

*(Six as measured at 11:52Z. This file is a seventh, written afterwards on request; if you
count seven, that is why. Re-run the command — do not adjust the number by hand.)*

| path | bytes | mtime (local) | sha256 |
|---|---:|---|---|
| `nd-unfolding/pet/TYPED_DESCRIPTOR_SEMANTIC_AUDIT-20260901.md` | 45901 | 2026-09-01T20:13:08 | `68d044161ec0be6f…` |
| `PROJECT_STATE_PILOT_PROPOSAL.tmp.md` | 17781 | 2026-08-31T19:06:29 | `adccb907e6c32db4…` |
| `HANDOFF-20260902-k0-continuity.md` | 11306 | 2026-09-02T03:24:18 | `934191232cddfd03…` |
| `docs/orchestration/measure_k0_farend_f1b_f17b_round2.sh` | 8776 | 2026-09-01T19:08:18 | `e777c55928887e46…` |
| `HANDOFF-20260902-clean-lane-permanence-scope.md` | 7403 | 2026-09-02T03:23:19 | `d620b7b7015a583e…` |
| `HANDOFF-polish-categories-3-6-9.md` | 5763 | 2026-08-31T19:06:29 | `32018911ad541938…` |

`measure_k0_farend_f1b_f17b_round2.sh` is the instrument for the pending round-2 F-1(b) filing
(§6). It is uncommitted, so it is not live and its round-1 sibling's MANIFEST pin is untouched.

### 1.2 Refs: local-only vs remote-only

| ref | sha | vs `origin/main` | pushed? |
|---|---|---|---|
| `main` | `52cbda906bfe` | 0/0 | yes |
| `worktree-permanence-scope-ruling` | `52cbda906bfe` | 0 ahead / 0 behind | local-only, but == main |
| `codex/gate1-round2-f17a-20260830` | `077d81750bae` | 0 ahead / 94 behind, **ancestor** | local-only, fully merged |
| `codex/gate1-round2-f17a-20260830-personal` | `22fc4e84d27c` | 0 ahead / 93 behind, **ancestor** | local-only, fully merged |
| `pet-typed-semantic-evidence-integration-20260902` | `32a0bb8a047a` | **2 ahead** / 19 behind | **local-only** — see §5 |
| `codex/pet-gate6-gap1-full-inventory-20260830` | `310d7e63d369` | 17 ahead / 283 behind | pushed (local == remote) |
| `pet-gate6-strategy-20260825` | `a05baab141e7` | 34 ahead / 283 behind | pushed (local == remote) |
| `origin/codex/pet-gate6-strategy-20260825` | `0969e787c777` | 14 ahead / 283 behind | remote-only |
| `origin/pet-typed-keras-adapter` | `9064d59f6c93` | 0 ahead / 52 behind | remote-only, fully merged |
| `origin/pet-typed-semantic-evidence-integration-r2-20260902` | `462d68bef6e0` | 0 ahead / 5 behind | remote-only, fully merged |

Tags: **28 local / 27 on origin**. The single local-only tag is `freeze/k0-aa67c426` →
`aa67c426afaa` (2026-08-23T22:59:37-05:00). That commit **is an ancestor of `origin/main`**, so the
provenance is published; only the tag ref is unpushed.

---

## 2. Generated state — MEASURED 11:53Z, and it is STALE

```
python3 docs/orchestration/generate_live_state.py --check-freshness   # EXIT=1
```
```
STALE :: Git: 712de1b, HEAD 52cbda90, HEAD^ c3873132.
```

Verified read-only first: `main()` returns from `check_freshness()` at
`generate_live_state.py:973-974`, before the `atomic_write` path; the flag's own help says
"writes nothing".

| quantity | value |
|---|---|
| recorded `Git:` | `712de1b9091d37bb285bfe5b1effd1caaacd32df` (**ancestor** of HEAD) |
| **staleness** | **124 commits**, 2026-08-28T14:06:22+02:00 → 2026-09-02T12:46:36+02:00 |
| `Observed:` in the file | `2026-08-28T12:09:37Z` on `login35` — **5.0 days old** |
| last commit touching `LIVE-STATE.md` | `6a96cc62` 2026-08-28 |
| last commit touching the **authored input** `state/live-state.json` | `73a67ef0` **2026-08-31** — `[fix] OI-181: defuse the freshness trap` |

**The authored input is 3 days newer than the rendered view.** The OI-181 fix is in
`state/live-state.json` and is *not* in `LIVE-STATE.md`. Any field quoted from `LIVE-STATE.md`
predates that fix.

`state/live-state.json` re-measured: 14312 bytes, sha256
`7a5759129ae2f5b7fd7a031234e83f2809f69381b2c06c153c248f789698a74a`, 3 blockers (all carry
`WITNESS:`), `scope_notes` present as a list. The dead Gate-4 blocker is gone from the array.

### 2.1 The authored-input defect (OI-73) — re-measured, and the artifact half no longer reproduces

OI-73's blocker text is: *"`live-state.json` IS THE HAND-AUTHORED INPUT … AND `MANIFEST.tsv:616`
CALLS IT `generated`"*, reading `MACHINE / state-artifact / generated`.

Re-measured today (line re-derived, not reused):

```
grep -n 'state/live-state.json' docs/orchestration/MANIFEST.tsv
527:docs/orchestration/state/live-state.json  tracked  LIVE  state-artifact  ""  ""  open  ""  route-only  …  no  25  120  14312
```

Against the header `path tracking class kind campaign event_date event_status canonical_successor
read_policy consumer immutable inbound_count lines bytes`: `class=LIVE` (not `MACHINE`),
`event_status=open` (**not `generated`**), `read_policy=route-only`. For contrast,
`LIVE-STATE.md` at `:125` still carries `event_status=generated`.

The row's own state cell closes with *"item (2) is fixed in code at the commit carrying this note."*
So: **the concrete MANIFEST misclassification OI-73 cites is not present in `MANIFEST.tsv` as of
`52cbda90`.** The OI row is nevertheless still `OPEN`, and `docs/CURRENT_WORK.md` still renders it
`BLOCKED-EXTERNAL` — which that same row documents as a **keyword artifact**: `policy.json`'s
`explicit-blocker` rule matches the bare word `BLOCKED` in the state cell, and the cell says
"BLOCKED BY A CODE DEFECT" about a file this repo owns. Blast radius stated in-row: 20 rows.

**Not repaired here.** The instruction to withhold regeneration is honoured; recorded as a
discrepancy between the routed record and the artifact for OI-73's owner
(`repo infrastructure / control plane`) to settle.

---

## 3. Worktrees — MEASURED 11:57Z

```
git worktree list --porcelain ; git -C <wt> status --porcelain=v1 -uall
```

| worktree | HEAD | branch | dirty entries |
|---|---|---|---:|
| `/Users/josephbailey/local-research/MINERvA-OmniFold` | `52cbda906bfe` | `main` | 6 (all `??`) |
| `/private/tmp/minerva-gap1-launch-rCenMq` | `310d7e63d369` | `codex/pet-gate6-gap1-full-inventory-20260830` | **0** |
| `/private/tmp/minerva-gap3-authorized-W8m3Bw` | `a05baab141e7` | `pet-gate6-strategy-20260825` | **0** |
| `/private/tmp/minerva-gate1-r2-codex-school2-20260830` | `077d81750bae` | `codex/gate1-round2-f17a-20260830` | **0** |
| `/private/tmp/minerva-gate1-r2-personal-p02ohE/repo` | `22fc4e84d27c` | `codex/gate1-round2-f17a-20260830-personal` | **0** |
| `.claude/worktrees/permanence-scope-ruling` | `52cbda906bfe` | `worktree-permanence-scope-ruling` | **0** |

`core.hooksPath = /Users/josephbailey/local-research/MINERvA-OmniFold/.githooks` (absolute, shared
across every lane). Hooks present: `commit-msg`, `pre-commit`.

**A peer session is live.** The `permanence-scope-ruling` worktree is `locked` by
`claude session permanence-scope-ruling (pid 39222 …)`, and `ps -p 39222` confirms
`claude --dangerously-skip-permissions`, elapsed **10:45:37**, started 2026-09-02 03:25:50 local.
(The worktree lock string records 01:25:50 — the same instant in UTC, not a second process.)
43 `claude|codex` processes are running on this Mac. Treat `main` as concurrently written.

This checkout commits as `MINERvA-OmniFold agent (unattributed)
<agent-unattributed@minerva-omnifold.invalid>`; the global identity is `Joseph Bailey`.

---

## 4. Control plane — MEASURED 11:54Z, PASS

```
python3 docs/orchestration/control_plane_lint.py                    # EXIT=0
python3 docs/orchestration/control_plane_lint.py --adoption-check   # EXIT=0
python3 docs/orchestration/control_plane_lint.py --coverage-report   # EXIT=0
python3 docs/orchestration/control_plane_lint.py --entrypoint-report # EXIT=0
```

Read-only confirmed: `check_or_write(write=False)` only compares; `--write` is the sole mutator.

```
CONTROL-PLANE PASS: 13 selected; 0 overflow; 92 backlog; 137 source records;
                    25 playbook rules; 68106 prose / 34456 instrument lines over 706 tracked files
CONTROL-PLANE COVERAGE: 137/137 source records classified
promoted source records: 12; active unpromoted backlog: 92
```

| queue | rows | share of 137 |
|---|---:|---:|
| `NOW` | 65 | 47.4% |
| `BLOCKED-EXTERNAL` | 20 | 14.6% |
| `WAITING-JOSEPH` | 19 | 13.9% |
| retired | 31 | 22.6% |
| deferred | 2 | 1.5% |

`docs/OPEN_ITEMS.md` holds **137 `| OI-` rows / 135 distinct ids**. The two duplicates, `OI-64` and
`OI-65`, are **documented ID COLLISIONS** dated 2026-08-13, flagged in their own state cells
("this is LANE A's OI-64" / "this is LANE C's OI-64"). Not a new defect. Highest id: `OI-188`.

`docs/CURRENT_WORK.md` selects 13: OI-71, 125, 93, 130, 75, 131(a), 123, 129, 131(b), 127, 128, 70,
73. Reading cost, measured: 4576 words prescribed path + a median 431-word OI record = **5007**;
largest record **7888**; full `OPEN_ITEMS.md` 78220.

---

## 5. PET branch divergence — MEASURED, and nothing substantive is unpushed

`pet-typed-semantic-evidence-integration-20260902` (`32a0bb8a`) is the only ref with commits on no
remote: 2 ahead / 19 behind `origin/main`. One is a merge; `git cherry -v` reports exactly one
non-upstream patch-id.

Content-diffed against `origin/main` rather than trusting the counts:

- `docs/orchestration/FINDING-20260901-pscratch-read-stalls-block-a2b.md` — blob
  `5c85e236cf47a6091a616c39d12583235c377fba` on **both**. **Byte-identical.**
- `VALIDATION_LEDGER.md` — `git diff origin/main <branch> -- VALIDATION_LEDGER.md` is **empty**.
- Excluding `MANIFEST*` and `source-record-inventory.tsv`, the branch-side deltas are 1-line and
  5-line differences in `docs/OPEN_ITEMS.md`, `docs/CURRENT_WORK_BACKLOG.md` and
  `SCOREBOARD-20260817-…md` — i.e. the branch's *older* text, against main's 1777 additional lines.

**Conclusion: the unique patch-id is MANIFEST bookkeeping only, and main's MANIFEST is newer
(regenerated at `52cbda90` today). No at-risk unpushed PET work exists.** The branch is a spent
local integration branch.

Other PET refs: `codex/pet-gate6-gap1-full-inventory-20260830` 17 ahead / 283 behind (pushed);
`pet-gate6-strategy-20260825` 34 ahead / 283 behind (pushed);
`origin/codex/pet-gate6-strategy-20260825` 14 ahead / 283 behind (remote-only — no local ref);
`origin/pet-typed-keras-adapter` fully merged.

---

## 6. Scheduler and cluster — MEASURED 11:55Z–12:10Z

Read-only cluster access is authorized by the routed instruction ("query the scheduler/source
directly") and needed no compute. NERSC cert: `Valid: from 2026-09-02T11:53:00 to
2026-09-03T11:54:14` (local) — ~22 h remaining, renewed ~2 h before this window.

### 6.1 A false negative that ControlMaster nearly published

My `~/.ssh/config` pins `ControlMaster auto` / `ControlPersist 12h` for `login*.nersc.gov`, so every
plain `ssh saul.nersc.gov` reused **one** connection to **login24**. On login24:

```
scontrol ping   -> "Slurmctld(primary) at slurmctld is DOWN"   rc=1
squeue --me     -> rc=124 (timeout 25s)          # BLIND, not "0 jobs"
sacct  --me     -> rc=1, header printed, ZERO ROWS
                   "_open_persist_conn: failed to open persistent connection to
                    host:slurmdbd_service.local:6819"
```

**`sacct` printed an empty table with rc=1** — the exact shape that reads as "no jobs ran".

Re-probed with `-o ControlPath=none -o ControlMaster=no`, three fresh connections:

| node | `scontrol ping` |
|---|---|
| login03 | **UP** rc=0 |
| login11 | **UP** rc=0 |
| login23 | **UP** rc=0 |

**The outage is login24-local, not cluster-wide.** Every scheduler figure below was taken through
`ControlPath=none`. `sinfo` from three nodes agrees: 882 planned, 394 `drained$`, 62 `draining@`,
42 `down$`, 25 reserved, 3 `mixed-`, 1 `down*`.

### 6.2 Live queue — exactly one job, and it is infrastructure

```
squeue --me -r -o '%.14i %.9P %.36j %.10T %.11M %.11l %.5D %.8q %R'
```
```
      57712764      cron WAKER_STATE_DIR=/pscratch/sd/j/josep COMPLETING  0:09  12:00:00  1  cron login05
```
rows = **1**. Positive control: `squeue -p regular_milan_ss11 -h -o '%i'` → **4668 rows**, rc=0.
So the instrument returns rows; the 1 is real.

**No science job is queued or running.** `scontrol show job 57712764`: `JobState=PENDING`,
`Reason=BeginTime`, `CronJob=Yes`, `QOS=cron`,
`StdOut=…/state/waker/logs/cron-tick.log`.

`scrontab -l` — the `wakerctl` managed block is intact: `*/5 * * * *`, `-q cron`, `-t 12:00:00`,
`--open-mode=append`.

### 6.3 Supervision net — healthy, but NOT by the mechanism the docs name

| probe | result |
|---|---|
| `state/waker/last-tick.json` | `at_utc 2026-09-02T12:03:52Z`, `node login32`, `pid 389138`, `watch_errors 0` — **42 s before my read** |
| `state/waker/logs/cron-tick.log` mtime | **Aug 27 19:18** — the `#SCRON -o` target has not been appended in 6 days |
| `wakerctl.py status` | `"watches": []` — **zero armed watches**, 87 archived |

`pgrep -a -u josephrb -f wakerctl`, run **from inside** NERSC against the daemon-lock nodes:

- **login32**: pid 389137 `tmux new-session -d -s minerva-waker-20260829 … wakerctl.py run --poll-seconds 60`; pid 389138 the python child.
- login02, login05: no `wakerctl.py` line. (Scope: `pgrep` matched its own `bash -c` on every node,
  so absence is established by the missing `wakerctl.py` line, not by `pgrep`'s exit status.)

**The ticks come from a tmux-hosted long-running daemon on one login node, not from the scrontab
job**, which is `PENDING/BeginTime`. `WAKER.md`/`LIVE-STATE.md` call scrontab "the supervision net".
The net in effect dies with a login32 reboot and is not itself supervised. Nothing currently needs
supervising (no science job, no armed watch), so this is latent, not active.

Also observed in `cron-tick.log`: `ValueError: Invalid isoformat string:
'1784527278\nRUNNING|1784527278'` — a real parse defect, but it predates this window (last write
Aug 27) and belongs to the log's own history.

### 6.4 Storage — `hpssquota` from login16

| filesystem | used | quota | % | inodes |
|---|---:|---:|---:|---|
| home | 20.41 GiB | 40.00 GiB | 51.0% | 230.38K / 1.00M (23%) |
| **pscratch** | **16.00 TiB** | **20.00 TiB** | **80.0%** | 203.23K / 10.00M (2%) |
| HPSS (charged to m3246) | 300.20 GiB | 512.00 GiB | 58.6% | — |

pscratch is the number to watch: **80.0%**, up from the 79.9% recorded in `OI-131`. HPSS 58.6%
matches OI-131's discharged measurement.

### 6.5 Cluster checkouts

```
git -C <path> rev-parse HEAD ; git -C <path> status --porcelain
```

| path | HEAD | vs `origin/main` | dirty |
|---|---|---|---|
| `/pscratch/sd/j/josephrb/MINERvA-OmniFold` | `32e403b84e9e` (2026-08-29T23:47:01+02:00) | **116 behind, 0 ahead, ancestor** | **726** default-`-u` / **3473** `-uall`, **all untracked, 0 tracked modifications** |
| `/pscratch/sd/j/josephrb/k0r2/clean` | `7ac0edecf45b` **detached** | (frozen — see §7) | **0** |

The 726/3473 split is the denominator that matters: the cluster tree has **no** modified tracked
file. (726 is also the figure `OI-144` recorded on 2026-08-21.)

The cluster `.git` has **no `refs/remotes/origin/*`** — `refs/remotes/origin/main` is an unknown
revision there. Its remotes are named `github` and `analysis-note` (43 remote-tracking refs,
including a `bundle/*` family); `FETCH_HEAD` is dated Aug 29 16:24. So "behind" was computed against
**this** checkout's `origin/main`, with `32e403b8` confirmed present in the local object DB and an
ancestor of `52cbda90`.

### 6.6 THE STALL HAS CLEARED — `FINDING-20260901-pscratch-read-stalls-block-a2b.md` does not reproduce

That FINDING (tracked on `origin/main`) records: *"Hangs and does not return: `git status
--porcelain`, on **both** cluster checkouts"*, measured 2026-09-01 across several login nodes, and
concludes the round-2 `F-1(b)` filing "cannot be completed" because of it.

Re-measured 2026-09-02T12:08:57Z–12:09:26Z, `timeout 90/120`, three fresh login nodes:

| node | `k0r2/clean` | `MINERvA-OmniFold` |
|---|---|---|
| login24 | rc=0, 0 s, 0 entries | rc=0, 1 s, 726 entries |
| login16 | rc=0, 0 s, 0 entries | rc=0, 1 s, 726 entries |
| login06 ×6 samples | rc=0, **90–298 ms**, 0 entries | rc=0, **168–459 ms**, 726 entries |

Plus the bulk-content read that failed: `git diff --stat HEAD` on `k0r2/clean` → rc=0, 0 s.

**14 successful measurements, 0 timeouts, across 3 login nodes.** Scope, stated at the strength
measured: the fault was described as *intermittent*, so this establishes that **the signature does
not reproduce in this window** — not that the fault is permanently gone. The correct next step is a
producer re-measurement under its own authorization, not an inference from these 14 reads.

**Not acted on.** The filing is a producer action inside a live freeze (§7).

---

## 7. Active campaign records

### 7.1 The freeze is live and is being honoured

`FREEZE-20260830-k0-deployment-7ac0edec.md` §1, verbatim:

> *"The deployed tree `/pscratch/sd/j/josephrb/k0r2/clean` stays detached at
> `7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b` … No checkout, reset, fetch-and-merge,
> re-declaration, or branch repoint may occur in that directory during this interval. It expires
> when that rehearsal's F-1(b) producer filing is committed — not when its jobs merely look
> terminal."*

Measured: that directory is detached at exactly `7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b` with
**0 dirty entries** and 1804 indexed files. **Compliant.**

Expiry status, measured rather than read:

```
git ls-files | grep -iE 'RECEIPT.*k0.*f1b|f1b.*producer'
-> docs/orchestration/RECEIPT-20260830-k0-f1b-producer-filing.md      (the ONLY one)
```

`DECISION-20260901-joseph-authorizes-k0r2-redeploy.md` §3 scopes that receipt to the **prior**
rehearsal: a measurement at `2026-08-29T22:08:01Z` against deploy `aa67c426`, naming combine job
`57527875`. **No round-2 F-1(b) producer filing is tracked.** Therefore the freeze has **not**
expired and §2's redeploy authorization has **not** taken effect. The §3 ordering constraint "is
part of the ruling and does not travel separately from it."

### 7.2 THREE k=0 job families total 374 tasks. Only the jobid separates them.

`sacct -X -u josephrb -S 2026-08-29T00:00:00 -o JobID,JobName,State,Start,End,ExitCode,Elapsed,Partition`
(417 lines; positive control `sacct … -S 2026-08-30 -E 2026-09-01T12:00 -X -n -o JobID` → 389 rows, rc=0)

| family | run_id | arms | tasks | outcome | window |
|---|---|---:|---:|---|---|
| `575278xx` | `k0-aa67c426-20260824T145751Z` | 7 | **374** | COMPLETE (per `LIVE-STATE.md`, 2026-08-28) | ended 2026-08-25T16:24:42 |
| `577425xx` | `k0-7ac0edec-20260830T000215Z` **round 1** | 5 base ids / 12 rows | — | **8 FAILED `3:0` + 4 CANCELLED** | last End **2026-08-30T09:23:17** |
| `577532xx` | `k0-7ac0edec-20260830T000215Z` **round 2** | 7 | **374** | **374/374 COMPLETED, ExitCode `0:0`, zero other states** | 2026-08-30T14:29:20 → **2026-09-01T01:55:58** |

Per-arm, identical in both 374-task families: `boot5dG` 100, `ssplit5d` 24, `det5dBKG` 19,
`uthrow5d_runF` 40, `uthrow5d_block` 21, `sweep5dBKGrun` 169, `uthrow5d_comb` 1 → **374**.

So **"374/374" alone does not identify a run.** Nor does the run directory: rounds 1 and 2 share
`k0-7ac0edec-20260830T000215Z`. Committed corroboration:
`RECORD-20260901-k0r2-round2-outcome.md` §1 — 374 declared / 374 COMPLETED / 0 failed / 0 queued,
counted as distinct `jobid_task` identities with `.batch`/`.extern` and array-bracket rows excluded
("counting `sacct` ROWS gives 447 against 374 declared"); round 1 "died with six tasks failing in
8–15 s on `OI-179`", the only change being `MNV_ENV_SYSTEM_PREFIXES` widened to three entries, with
no code, launcher or MANIFEST pin altered.

### 7.3 …and the generator cannot see the completed run

```
python3 -c "json.load(open('docs/orchestration/state/live-state.json'))['jobs']"   -> 8 entries
grep -ln '577532' docs/orchestration/state/*.json                                  -> rc=1, NONE
grep -ln '5752786' docs/orchestration/state/*.json                                 -> 6 files (control)
```

`live-state.json`'s `jobs` array is `57266000` plus the seven `575278xx` receipts. Every
`state/k0r2-*-active-*.json` file — despite the `k0r2-` prefix — carries
`run_id = "k0-aa67c426-20260824T145751Z"`, summing to `task_count` **374**.

**No `state/*.json` names any `577532xx` jobid.** Regenerating `LIVE-STATE.md` would still print
only the `aa67c426` arms; its Compute table structurally cannot show the 374/374 `7ac0edec`
round-2 run. This is independent of §2's staleness and is not fixed by regeneration.

### 7.4 Other terminal jobs in the window

| job | name | state | exit | end |
|---|---|---|---|---|
| `57727774_[1-5]` | `g6gap1push` | COMPLETED ×5 | `0:0` | 2026-08-29T23:05 |
| `57727775_[1-5]` | `g6gap1xsec` | COMPLETED ×5 | `0:0` | 2026-08-29T23:42 |
| `57727806` | `pet_g6_gap3_trunc` | **FAILED** | `3:0` | 2026-08-29T22:16:42 |
| `57729539` | `pet_g6_gap3_r1` | **FAILED** | `3:0` | 2026-08-29T23:01:09 |
| `57743781` | `pet_g6_gap3_nfd` | **FAILED** | `1:0` | 2026-08-30T09:50:37 |
| `57772777` | `pet_g6_gap3_nfdr` | **FAILED** | `1:0` | 2026-08-31T06:04:24 |
| `57819105` | `probe.sh` | COMPLETED | `0:0` | 2026-09-01T03:58:02 |
| `57668375` | waker ticker | CANCELLED | `1:0` | 2026-08-29T13:56:40 |

Four consecutive PET Gate-6 gap-3 failures. `57819105` (4 s) is the last non-cron job on the
cluster — **nothing has run since 2026-09-01T03:58:02Z.**

### 7.5 `RUNS.tsv` has no row for any of it

```
grep -c '577532|577425|577277|577437|57772|57819' docs/orchestration/RUNS.tsv  -> 0 for every prefix
grep -c '57266000' docs/orchestration/RUNS.tsv                                 -> 1   (positive control)
```

`RUNS.tsv`: 346 rows; latest `end_utc` **2026-08-21T21:58:58Z**; last commit `e1821a9c`
**2026-08-21**. The append-only run history is **12 days behind the scheduler** and contains no row
for the 374-task round-2 run, the dead round-1 arms, the gap-1 pushes, or the four gap-3 failures.

Per `AGENTS.md` — *"a result is live only after its evidence and required ledger/RUN_LOG/STATUS
records land in a commit"* — the 374/374 run has a committed **RECORD** but no committed **RUNS.tsv**
row. Reported, not repaired.

---

## 8. Gate 6 — the five prohibitions, verbatim

`docs/orchestration/state/gate6-member-trajectories-result-56847059.json`, 7178 bytes, sha256
`8f40541f1d8fec92b0e37885b1d24b851843d06f4c220f8de5ad1bc47265b6a5`.
`prohibitions_applied` is a **list of 5**:

1. `do_not_select_passing_subset`
2. `do_not_construct_C_ML`
3. `do_not_move_central`
4. `do_not_start_leg_2`
5. `do_not_retry_unchanged`

Reproduced as keys, not prose. `do_not_retry_unchanged` carries `unchanged` inside the identifier,
which is why the key form is the citable one (OI-73 item (1)).

Routed states, unchanged by anything measured here: no scalar-5D covariance candidate is adopted;
**Gate 2 remains FAIL**; no PET total covariance is adopted; PET `C_stat` is
`EXISTS — UNVERIFIED, PAIRING DECLINED` per `OI-126`'s 2026-08-20 ruling and `VL132` — its
existence, digest and ledger row supply neither the independent check nor the central pairing.
`VALIDATION_LEDGER.md`: 2106 lines / 172374 bytes, 141 distinct `VL\d+` ids, last commit
`1df84dfc` 2026-09-01. `KNOWN_ISSUES.md`: 96 lines / 58740 bytes, last commit `d8d499a2`
2026-08-23.

---

## 9. Committed historical state — the 124 commits `712de1b..origin/main`

By day: 08-28 **5**, 08-29 **3**, 08-30 **34**, 08-31 **18**, 09-01 **40**, 09-02 **24**.

By author: `MINERvA-OmniFold agent (unattributed)` **107**, `status dashboard lane` 7,
`stale blocker sweep` 2, `rehearsal producer (claude-school)` 2, `checkout reconcile` 2,
`Joseph Bailey` 1, `deployment producer (claude-school)` 1,
`codex-school2 STEP-3 independent grader` 1, `Claude (stale-blocker sweep lane)` 1.

By subject tag (top): `pet` 13, `decision` 12, `oi173` 7, `f17b` 7, `dashboard` 7, `finding` 6,
`ruling` 5, `orchestration` 5, `k0` 5, `fix` 5, `census` 5, `predeclare` 4, `oi185` 4, `k0r2` 4.

107 of 124 under one unattributed identity: **`git log` does not partition authorship here.**

---

## 10. Facts that cannot be established from this session

1. **Whether the pscratch stall recurs.** 14 clean reads in a ~90 s window bound the *present*, not
   an intermittent fault's future. Needs sampling over hours, by the producer.
2. **Why login24's Slurm clients cannot resolve `slurmctld` / `slurmdbd_service.local`** while
   login03/11/23 can. Node-local, and diagnosing it is NERSC's.
3. **Whether the login32 tmux waker daemon is intentional or drift**, and whether the scrontab job's
   `PENDING/BeginTime` with a `StartTime=2026-09-02T05:05:00` already past is the designed cycle or
   a stuck state. No committed record names the daemon.
4. **Whether `cron-tick.log` stopping on Aug 27 is expected** under `--quiet`, or a lost stdout path.
5. **Authorship of the 6 untracked paths.** No trailer, no commit; mtimes only.
6. **Whether OI-73 may be closed.** The artifact defect no longer reproduces at `52cbda90`, but the
   row is `OPEN` and closure is its owner's classification call, not a measurement.
7. **What `probe.sh` (`57819105`) measured.** 4 s, `regular_milan_ss11`; not matched to a receipt.
8. **The 577425xx arm count.** 5 base ids / 12 task rows inside my window
   (`-S 2026-08-29T00:00:00`); whether round 1 declared 7 arms with 2 never reaching the DB is not
   decidable from `sacct` alone. `sacct -X` brackets truncate throttled low tasks.
9. **Whether the 3473 untracked cluster paths are products or scratch.** Counted and typed
   (0 tracked modifications); not classified. `OI-75` and `OI-130` govern.
10. **Any `refs/notes/commits` content** (`03b6b58880cc` on origin) — not fetched, so unread.
11. **The standalone `MINERvA-OmniFold-Analysis-Note` build state.** Remote head measured
    (`d0c3768e`); no build run, so note/primer/paper freshness is unestablished.
12. **Provider capacity.** `LIVE-STATE.md`'s percentages are 5 days stale and were not re-probed.

---

## 11. What this snapshot does NOT authorize

No compute, submission, redeploy, repair, regeneration, adoption, covariance construction, pin
move, freeze expiry, readiness or fitness finding, OI closure, or publication claim. Gate 2 remains
FAIL. The five Gate-6 prohibitions stand. PET `C_stat` remains unverified and unpaired.
