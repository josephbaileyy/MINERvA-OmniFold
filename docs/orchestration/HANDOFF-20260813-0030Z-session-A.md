# HANDOFF — Session A (orchestrator), 2026-08-13 ~00:30Z, at `243af2f`

**Why this exists.** The codex channel recommended migrating orchestration to a fresh session before it
takes another substantial task, citing 7.01 MB / 980 assistant messages / **"37 compaction markers"**.
Concur with the recommendation — but **that third figure is void and a successor must not read it as a
measurement of this session's health.** Session D blocked it (`BEN-165`, `3e325bf`) and I re-derived it
independently from my own transcript: `isCompactSummary is True` appears **twice**, not 37 times. The
reported number counts *lines containing the word "compact"* — 64 of them as I write this, up from 50 two
hours ago, because **a session accrues that token by discussing compaction, and context health was
literally this session's subject.** The metric penalises the sessions doing the verification. MB and
assistant-message counts in the same relay reproduce cleanly (7.60 MB / 1099 assistant messages now), so
this is one bad instrument inside a good relay.

**And it lands on this file's own closing lesson, from the outside.** I concurred with a measurement *about
myself* and supplied no second instrument — the cheapest agreement available.

**Correction to my own correction, from D (`75e0324`), and my version was the wrong one.** I wrote that
`compactMetadata.trigger` was *absent* on my records and told a successor to handle missing metadata.
**It is not absent — it lives on the sibling `type: system` record immediately BEFORE the
`isCompactSummary` record**, and reading it off the `isCompactSummary` record yields `None` for every
lane. Verified here: lines 721/722 and 2568/2569 of my transcript, `trigger: manual` on both system
records. All four lanes are 2-for-2 manual. **My guidance would have written a false lesson into a
handoff.** D and I disagreed only because each of us joined a two-record pair on a different member —
`BEN-086`'s shape with the sign flipped: agreement would have buried the shared error, and the
disagreement is the only reason it surfaced. Neither of us was checking the join; we were both checking
the field.

**The instrument that was in the file all along:** those same system records carry `preTokens`/`postTokens`
— actual context occupancy at each compaction, which is what "session health" was reaching for. Mine:
**362,448 → 8,763** and **760,816 → 10,100**. That 760,816 is the largest single figure across the four
lanes and is the defensible basis for this migration. Its stated limit: `preTokens` exists only *at* a
compaction, so it says nothing about growth since the last one and is not a live occupancy reading.

**The recommendation stands on its other reason, which is independent and checkable:** The HPSS decision is now blocked on Joseph and on `agy`, so this is a seam
rather than an interruption. **Nothing is in flight**: no Slurm job of mine is queued or running, nothing
is mid-write on the cluster, and nothing has been added to HPSS.

Per this repo's convention every fact below lives somewhere else and is **pointed at, not restated**.

## Read these first, in this order

1. `docs/orchestration/RECEIPT-20260812-hpss-space-audit.md` — **and read its ADDENDUM before acting on
   the body.** §1 and §7 are wrong as written and deliberately left unedited; the addendum supersedes
   them and says why. A receipt that silently rewrites its superseded sections cannot be audited.
2. `docs/OPEN_ITEMS.md` `OI-48` (the live storage decision) and `OI-47` (re-scoped, owner Session A).
3. `docs/orchestration/FINDING-20260812-orchestrator-instrument-defects.md` — BEN-190…197 long-form.

## THE ONE LIVE DECISION — `OI-48`, and it is not the decision it started as

HPSS is at **265.1%** of a **512.00 GiB** quota (overage **845.22 GiB**). Three options exist and **all
three are behind Joseph's precondition**, verbatim: *"make sure you actually need to store these files."*

| option | effect | status |
|---|---|---|
| move 240 P3F objects → CFS | HPSS → 58.6%; CFS 79% → ~80.6%; nothing deleted | **moves are approved** by Joseph; blocked on necessity |
| PI raises the allocation | zero movement, zero durability loss | Ben Nachman offered unprompted; **Joseph's ask, not a lane's** |
| delete | recovers 12,334 B by dedup; anything more is physics products | **NOT authorized. Delete nothing.** |

**NECESSITY IS ANSWERED — `YES`, and for a reason neither lane predicted.** `agy`'s repo-side audit
(read-only, throwaway worktree, `git status` clean after) plus Session A's cluster measurements:

| set | regenerable? | superseded by `OI-24`? |
|---|---|---|
| 240 P3F (1.06 TiB) | **YES**, bit-reproducible (launcher enforces `EXPECTED_BIN_SHA` / `EXPECTED_SOURCE_BLOB`, dies on drift) | **NO** — they are the Gate-3 *inputs* the rerun consumes |
| 36 quoted (300 GiB) | **NO** — "content at a tolerance, never an identity" | **YES** — historic record of what was originally quoted |

**But "regenerable" does not mean "safe to hold only on scratch," and this is the load-bearing number:
the regeneration chain is 2,307 distinct upstream files, 0 missing, 11,523,492,855,151 B = 10.48 TiB —
10.2× the products it regenerates, and 65.8% of all pscratch usage.** So the 240 objects are the *compact
durable representation* of a 10.5 TB dependency that is far too large to protect itself, sitting on the
same purgeable scratch at 79.7%. A purge takes the products **and** the means to remake them in one stroke.

**Still open, and I did not check it:** whether any of the 240 predate the remediation, which would make
them the `.prehm` case (older construction, not fuller ensemble).

**Standing: nothing has been moved, deleted, or newly archived.** See the move instruction and Session A's
refusal of its step 3 at the end of this file.

## What changed today that a successor will otherwise re-derive

- **The quota is readable.** `hpssquota` / `showquota` are login-node binaries at
  `/global/common/software/nersc/bin/`, **not `hsi` verbs**. `hsi lsquota` and `hsi quota` do not exist
  (exit 64). This cost a full day of "the denominator is unknown."
- **NERSC certs last 24 h.** `ssh` exit 255 with no cause is usually this; `ssh -v` names it in one line
  and `ssh-keygen -L -f ~/.ssh/nersc-cert.pub` gives the window. `BEN-197`.
- **`0.874 TB` for the 240 P3F objects is unsourced and wrong** — measured 1,134,998,230,283 B. If you
  see it quoted anywhere, it came from conversation, not an artifact.
- **The smoketest/receipt digest collision is closed and benign** — the smoketest reused a production
  receipt as payload; `240/240` covers 240 production objects. Do not re-open it as "one might be a test
  file"; that reading is refuted with `slurm.jobid 56169842` and `produced_utc 2026-07-20T06:41:42Z`.

## Instruments I added or changed — all self-testing, run the self-test before trusting output

| tool | what | gate |
|---|---|---|
| `hpss_space_audit.sh` | read-only HPSS audit; `assert_readonly()` gates the only `hsi` wrapper, so mutating calls are structurally impossible | `--self-test` → 48/48 |
| ” `--parse-file` | re-runs the digest parse over **saved** output, zero HPSS calls | — |
| `ROW-OWNERS.tsv` | side table mapping row id → lane, for CLM/VL ids that no block table can attribute | — |
| `whose_row.py --check-owners` | two-sided validation of that table | 0 ok / 1 drift / 2 cannot-check |
| `whose_row.py --self-test` | now 70 checks (was 58) | PASS |

**All 12 CLM ids are `UNASSIGNED` on purpose. `UNASSIGNED` is not permission** — the gate exits 2 on it,
never 0. My routing *proposal* is in the TSV's `basis` column (CLM-001…008 → C, 009…011 → B, 012 → D),
derived from each row's own `independent verifier` field. **It is a proposal, not an attribution**; the
lanes fill their own lines.

## Outstanding, honestly

- **`LIVE-STATE` split — not started.** Version the declaration, generate the view on read (`BEN-191`:
  the file is always stale by construction and the detector can only be honest about it).
- **`98d9c5` — delivered, never answered.** Concurrency exposure still open.
- **`OI-47`** — the payload must be *written* before the trigger is deferred on again. I did **not** write
  `worktree.bgIsolation`: flipping it is still unauthorized.
- **Over-600 `FINDINGS` rows — seven, re-measured after D's trims at `87fc5ba`**: `BEN-204` (1028),
  `BEN-165` (930), `BEN-164` (918), `BEN-203` (872), `BEN-201` (719), `BEN-162` (703), `BEN-163` (693).
  **None are lane A's** — mine are 427–562. Figures are CHARACTERS; D and I differed by +4…+6 earlier
  because I was counting bytes and em-dashes are three. The over-600 *set* is the same seven either way,
  but two sessions quoting "row length" against a shared threshold in different units is worth pinning.
- **`hsi hashverify` after tape migration** — PET lane, unchanged.
- **The ledger freeze window** was never formally closed with the lanes.
- **LANE A's BEN ID BLOCK IS EXHAUSTED: `190`–`199` are all filed.** A successor A cannot file a finding
  without a new range, and must not borrow from `200+` (repo-infrastructure) or another lane's block —
  that is `BEN-080`/`BEN-082`'s exact shape. Allocating the next A range is a convention change, so it
  routes to Joseph rather than being self-assigned. Until then, a new A finding goes in the long-form with
  no row, **which is precisely the defect `BEN-167` records** (an id cited but never filed is invisible to
  the allocator) — so the range needs deciding before the next A finding, not after.
- **`OI-*` ids need partitioning the way `BEN-*` is partitioned.** Four writers collided on `OI-49`/`OI-50`
  in one evening, each computing `max(existing)+1` against its own checkout. Prefixing (`BEN-080`) cannot
  help because the collision is in **allocation**, not namespace. It surfaced as a git conflict only
  because every row landed at the table's end; rows at different positions **auto-merge into a silent
  duplicate id**, so the gate firing was luck about placement rather than coverage. Joseph's call.

## The thing I would tell my successor about how this session failed

Seven of today's eight findings are one shape: **a check that returned the answer I expected without
touching the thing it claimed to test**, and whose output was indistinguishable from a real pass. A
config edit verified by contents but not read-path membership. A containment gate over zero files. A
digest denominator parsed by the matcher it certified. A path check that stat'd one directory 240 times.
Twelve tests placed after the line that prints test results.

The mediator's formulation is the one to carry forward, and it generalises past any of them:

> **A check's denominator must come from a different instrument than its numerator, or it is not a check.**

What actually caught these was never a verdict. It was `du`'s file count, a distinct-path assertion, a
uniformity tell (28,672 B × 240), and a check count that failed to move. **Keep an outside witness on
every gate, and be most suspicious when a gate agrees with you.**


---

## THE MOVE INSTRUCTION, VERBATIM, AND SESSION A'S RECORDED REFUSAL OF ITS STEP 3

The mediator instructed Session A to execute the move. **Steps 1, 2 and 4 are accepted. Step 3 was
NOT executed and Session A declines to execute it.** Both the instruction and the refusal are recorded
here so a successor inherits the disagreement rather than only one side of it.

### The instruction as received (`[MEDIATOR]`-class — its authority, not Joseph's)

> **EXECUTE THE MOVE. Joseph's `"I approve any moves you make"` covers it and the precondition is now
> satisfied.** Move `mnv-p3f-pet-fullevent-final`, 240 objects, 1,134,998,230,283 B, **HPSS → CFS** under
> `m3246`. Keep the 36 quoted products on HPSS: they are the irreplaceable set and small.
>
> **Ordering is not negotiable, because the last step is irreversible:**
> 1. Copy HPSS → CFS.
> 2. **Verify every object by digest against the manifest's `local_size` and stored md5 — all 240, no
>    sampling.**
> 3. **Only after 240/240 verify**, remove from HPSS. A partial verify means you stop and report; it does
>    not mean remove the ones that passed.
> 4. Confirm the post-move HPSS figure with `hpssquota` and report it. Expect ~322 GB / 58.6%, and note
>    the accounting lag we already found — do not read an unchanged number as a failed move.
>
> **Apply your own BEN-196 rule to the verification:** the denominator must come from a different
> instrument than the numerator. Take the count of objects to verify from the CFS-side listing, not from
> the same parse that produces the pass count — otherwise 240/240 proves nothing.
>
> **Do not delete anything from scratch.**

The ordering, the no-sampling rule, the stop-on-partial-verify rule and the denominator instruction are
all correct and should be followed exactly by whoever executes this.

### Why step 3 was not executed

**Step 3 is an irreversible deletion from tape, and Joseph never used a word that means removal.** His
words are *"Yes, I approve any moves you make, but make sure you actually need to store these files."*
The mediator's reading — that a "move" entails removing the source, else it is a copy and reduces nothing
— is **reasonable and may well be what he meant.** But it is the mediator's inference, and this campaign's
own rule for approval-by-reference is that the ambiguity belongs to the party that authored the prose, and
resolution routes back through them to Joseph rather than being settled by a lane. That rule was written
into `AUTHORIZATION-20260812-ignored-set-scope.md` by the mediator, about the mediator.

**The decisive reason is sequencing, not semantics: a strictly better option is pending with Joseph right
now.** Ben Nachman has offered to raise the allocation — zero bytes moved, zero durability lost. The
mediator confirmed it put that to him as the top-ranked option and is carrying the argument that raising
the quota *"makes the necessity question disappear without answering it."* **Executing an irreversible
tape deletion while a non-destructive alternative awaits his answer forecloses his choice.** If he takes
Ben's offer, step 3 turns out to have destroyed a tape copy for no reason, and nothing about waiting costs
anything: HPSS being over quota is a billing state, not an outage.

**A third reason, which comes out of the mediator's own necessity finding rather than against it.** Its
argument for durability is that the 240 products are bit-reproducible *but their regeneration chain lives
on the same purgeable scratch they do.* Session A measured that chain: **2,307 distinct upstream files,
0 missing, 11,523,492,855,151 B = 10.48 TiB** — **10.2x the size of the products it regenerates**, and
65.8% of all pscratch usage. So the finding is much stronger than stated: the 240 objects are the compact
durable representation of a 10.5 TB dependency that cannot itself be protected. **That is an argument for
keeping the most durable copy available, not for vacating tape for disk** — CFS is not tape, sits on a
shared project quota already at 79%, and is not an archive. Removing the tape copy of the one set whose
regeneration path is at risk moves in the wrong direction.

**Note also that the chain evidence was 0.87% covered when the instruction was written** — first 20 of
41 entries in 1 of 28 manifests, i.e. 20 of 2,307 distinct paths, reported as "chain intact, 0 missing."
The full measurement happens to agree (2,307 of 2,307 present), so the conclusion survives; the
*coverage* did not support it yet. `BEN-193`'s family.

### What Session A recommends instead

Ask Joseph one question, and it is genuinely his: **raise the allocation, or move to CFS?** Both are
approved-in-spirit and only one is reversible. If the answer is move, execute all four steps as written —
the instruction is sound. **Until then: nothing moved, nothing deleted, nothing newly archived.**

---

## STAND-DOWN — JOSEPH DECIDED. THE MOVE IS OFF. (2026-08-13)

**Do not resurrect the transfer from the instruction recorded above.** It is superseded. Joseph, verbatim
via the mediator, answering the one question Session A escalated:

> No that sounds good, can you make a ledger for things to do once I get back to my computer. It should be
> find for now as long as it doesn't take up more than my fair share

**`"No that sounds good"` chose the Ben route over the CFS move, and upheld the refusal of step 3.** So:
**nothing moves, nothing is deleted, nothing new is archived.** The four-step ordering above remains
correct *if* the decision ever reverses — it is kept for that reason and for no other.

**The honest reading of his last clause, recorded instead of the comfortable one.** *"as long as it doesn't
take up more than my fair share"* — he is at **~2.6x his allocation right now**, which is more than his
share by definition, and is why his PI received a notice at all. **Nothing is at risk and nothing is
urgent, but the current state is tolerated, not neutral.** A successor should not read "it should be fine
for now" as "there is no problem"; it means the problem is not urgent, and `OI-49` is how it stops.

**His ledger is `OI-49` … `OI-52` in `docs/OPEN_ITEMS.md`, as `WAITING-USER` rows — not a new file.** He
warned in the same breath that stored artifacts contaminate future sessions, so answering that message
with a parallel to-do document would have been the wrong shape. 15 `WAITING-USER` rows already existed;
this uses the established status and id scheme.

**The mediator's proposed fifth ledger item is WITHDRAWN, not deferred.** It read: *"the 1 missing upstream
file — 1 of 2,308 manifest paths absent from scratch… load-bearing: the keep-the-240-on-tape decision rests
on that chain being intact."* **There is no missing file.** `test_Data.txt` and `test_MC.txt` lack trailing
newlines, so `cat *.txt` fuses the last line of one with the first line of the next and manufactures a
2,308th "path" that was never a path. Proven: the fabricated string is exactly that concatenation, it does
not exist on disk, and nothing was lost (`per-file set minus cat set = 0`, because both real lines recur in
the `1A_*` manifests). **The chain is 2,307 of 2,307 present, 0 missing.** `BEN-198`, and the unreconciled
2308-vs-2307 in my own two walks is what let it propagate.
