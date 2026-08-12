# AUTHORIZATION RECORD — HPSS copy of the quoted set, and delegation of the remaining issues (2026-08-12)

## The authorization, verbatim and complete

> yes, authorize it. also try fix the other issues in the way you or the other sessions decide is best. can you send me push notifications since I am using remote control when I need to make an input

**Transcription:** same chain as the two prior receipts — transcribed by `personal-orchestrator`, session
`5f7d4b75-b1dd-4c6e-8f95-912b3b045c66`, from Joseph's typed message; Session A copy-pasted it and **cannot
see the original**. The mediator verified the first receipt character-for-character by sha256 and is
expected to do the same here.

**THE THIRD SENTENCE IS NOT ADDRESSED TO SESSION A.** It concerns how the mediator notifies Joseph on
Remote Control and is **not an instruction to any lane**. It is recorded here rather than dropped because
the mediator relayed the block whole — *"a transcription step that decides what to omit is a transcription
step that can omit the wrong thing"* — which is the same reasoning that preserved `informaron`. Handled on
the mediator's side: input-needed notifications enabled on its account. **Practical consequence, and it is
not a licence: the escalation bar has not moved, but the cost of clearing it has dropped.**

## 1. The HPSS copy is AUTHORIZED

*"yes, authorize it"* answers the STOP as framed: **36 files, 0.322 TB**, destination **HPSS** via the PET
lane's existing path — the `56692312` pattern, server-side `hashcreate` against a local md5, marker written
only on a verified digest match.

**Conditions carried forward, unchanged and still binding:**
- **Home is NOT a destination** (~40 GB, and the set is 8.05× that).
- **The receipt is written LOCALLY** (Session C's amendment), so the copy does not perturb the inventory
  just taken. The cluster tree stays read-only.
- **Report the incremental figure after overlap** with the 0.874 TB already HPSS-protected at 240/240 by
  job `56692312`. **Do not assume the overlap is zero or total** — measure it.
- Ingredients ship with it.

## 2. The remaining issues are DELEGATED to the sessions

*"try fix the other issues in the way you or the other sessions decide is best."* That is real latitude and
is recorded as such rather than narrowed. **It is latitude over METHOD, not over the freeze:**
`docs/POST_PUBLICATION_REORG_PLAN.md`'s freeze tag still governs deletions and top-level reorgs, and
nothing in the list below needs either.

### Session A's ordering call, with two corrections to the mediator's framing

The mediator supplied a recommended order as `[MEDIATOR]`, explicitly for A to accept or reorder. Two of its
premises do not survive measurement, and one of the corrections changes an item's cost by an order of
magnitude.

**CORRECTION 1 — "incremental by row-owner" IS NOT AN AVAILABLE OPTION for the ledger, and the reason is
circular.** The mediator offered re-iding `VALIDATION_LEDGER.md` *"incrementally by row-owner"* as the
alternative to a quiet window. Measured: **0 of its table rows carry a prefixed id**, which is precisely
why `whose_row.py:41` documents it as unattributable. **So rows cannot be assigned to owners, because
assignment is what the id scheme would provide.** The author-merges-own-row rule cannot be applied to the
one file that most needs it, *because applying it requires the thing being added.* Therefore the ledger
re-id must be done by **one session**, with **no other session writing that file** during it.

**CORRECTION 2 — `CLAIMS.md` already has ids; what it lacks is a LANE MAPPING, and that is a tenth of the
work.** The mediator described it as having *"no scheme at all"*. Measured: **`CLM-001` … `CLM-012`,
contiguous, all 12 prefixed.** `whose_row.py` recognises them and returns owner `None` because no block
table maps a `CLM` id to a lane. **So the fix is a header addition, not a row rewrite — zero edits to the
12 rows, and no quiet window required.** It is therefore **not a rehearsal for the ledger**, because it is a
different operation: the ledger needs ids created, `CLAIMS` needs existing ids mapped.

**CORRECTION 3, against my own number as much as the mediator's.** It reported 152 ledger rows; I measured
130. **Both are right and the predicate was unstated:** `startswith("| ")` with ≥3 pipes gives 130; any
line beginning with a pipe gives 152. Same class as 114-vs-153 and the two walks — **a bare row count needs
its predicate the way a divergence count needs its revision.**

### The order, and the sequencing insight that matters

**A FILE-SCOPED FREEZE, NOT A LANE STOP.** The mediator observed that four items all want the same quiet
window and urged not letting them wait separately — correct, and the conclusion it did not draw is that
**three of the four do not need the lanes stopped at all, only a freeze on the specific files.** Lanes keep
working; they simply do not write `VALIDATION_LEDGER.md`, `CLAIMS.md` or `LIVE-STATE.md` during the
respective step. That is dramatically cheaper than a campaign stop, and a campaign stop costs context —
which this campaign has already paid for once today when three lanes were cleared while the read path was
six days stale.

1. **`CLAIMS.md` lane mapping** — header addition, no freeze, actionable immediately. **But the 12
   existing assignments are NOT Session A's to make by judgement** — that is the error A instructed C
   against on the quoted set. Structure now; the assignments route to the lanes that own each claim.
2. **`OI-47` respawn-time `bgIsolation`** — batch with the **next natural** lane restart. Do not force one;
   it is the only item that genuinely requires a stop, and forcing a stop to fix an isolation setting is
   the tail wagging the dog. Verify by re-reading the new jobs' `state.json`, never by diffing settings.
3. **`VALIDATION_LEDGER.md` per-row ids** (`VL1`, prefixed with the document's short name per the repo
   rule) — one session, file-scoped freeze, after the copy and digest work lands so it is not competing
   with the thing whose *definition* the ledger supplies.
4. **The `LIVE-STATE` split** — version the declaration, generate the view on read. Independent of the
   others; file-scoped freeze on that one file only.
5. **Long rows in `FINDINGS.md`** owned by B and D — already routed to their authors; author-merges-own-row
   applies and A's own two rows were compressed first.
6. **The `scp`/worktree-guard message** — cheapest item, most likely to burn a future session's hour.

## Not authorized by this, and unchanged

Deletions and top-level reorgs (freeze tag). Salvage before Joseph's review. Adoption of anything,
including the `.prehm`, which failed on the merits. A cluster worktree until `p4_evidence.py` stops
hardcoding `REPO` and the replacement is power-tested. Any write to the cluster tree beyond the authorized
HPSS copy path.
