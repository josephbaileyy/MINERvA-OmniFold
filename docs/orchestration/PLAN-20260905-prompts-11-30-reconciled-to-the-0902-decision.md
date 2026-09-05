# PLAN 2026-09-05 — prompts #11–#30 reconciled to Joseph's 2026-09-02 decision

**CITABLE FOR:** the disposition of each prompt in §3 and the session prompts in §4.
**NOT CITABLE FOR:** any authorization. **A row marked AUTHORIZED NOW authorizes drafting, reading and
measuring only** — never construction, compute, grading, adoption, or a publication change. No row here
grants spend.

**Controlling authority:** `DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md`, sha256
`0836139b1c9a057c194a81a94d45c9f979209a9ac293d4bc8434e6b43fc1a064`, verified at `origin/main`
`c71b319a`. Where this plan and that record conflict, the record wins.

## 1. The three corrections that reshape the whole list

**1. #11's premise is false.** It opens *"Assuming Joseph has ruled that G is rejected and Y is the sole
new subject."* He ruled the opposite on both halves. `R1`: **G is RETAINED** — not deleted, not moved,
not overwritten — and remains causes 1–6's grading subject. `R2`: Y is a **cause-7-only** subject, a
**separate** cell, **specification only**. So "write the complete Y predeclaration … give each
quarantine cause exactly one disposition" describes an object no ruling permits: **Y has no causes 1–6
dispositions to give**, because those causes are graded against G.

**2. "Adopt Y" is not an available outcome, so every prompt built on it needs rewriting.** `R2(iii)`
forbids combining Y's cause-7 grade with G's causes 1–6 grades or rolling it into the counts, Gate 2,
or any adoption case. #20's *"adopt Y, or reject Y"*, #21's *"If Y is adopted"*, and #14's *"do not
publish projections before Y adoption"* all presuppose a terminal action that does not exist. The
successor question they were reaching for is real, but it is **Z**'s, and Z needs a ruling
(`PACKET-20260905-full-scalar5d-successor-scope-question.md`).

**3. Much of the real critical path is not in #11–#30 at all.** The decision record's §4 lists **six
owner applications** that apply the rulings to the control documents. §5 reconciles each against
committed evidence at `origin/main` `c71b319a` rather than repeating the list: **five are genuinely
unapplied, and the sixth is substantially done.** They outrank most of this list, but they are **five
edits with five owners, not six sessions to dispatch**.

## 2. The stop, preserved exactly as ruled — not reopened, not re-optioned

| field | value |
|---|---|
| date | **`2026-09-30`**, UTC, inclusive — fires at the first instant `now >= 2026-09-30T00:00:00Z` |
| GPU ceiling | **`500` GPU task-hours** |
| CPU ceiling | **`500` CPU task-hours** |
| unit | task-hours — `ElapsedRaw` summed over **distinct task identities**; `.batch`/`.extern` and array-bracket rows excluded |
| t0 | **`2026-09-02T13:44:27Z`** — the instant of the decision's **original** commit **`9ce59a59`**, the value `r5_meter.py:31-34` uses. Spend before t0 is not metered; tasks straddling t0 are clipped at t0. **Not `dae18f22`/`14:40:06Z`, which only renamed the record and changed none of its bytes** |
| trigger | **OR** — any one firing stops the campaign |
| remaining | **25 days** as of 2026-09-05 |

**A ceiling is a prohibition and an accounting boundary, not authorization to spend up to it.** No
prompt below may be read as spending against these. **No option in this plan resets the date, the
ceilings, or the accounting start**, and none proposes alternatives to them.

## 3. The dependency list

**Legend.** **NOW** — authorized under existing authority, drafting/reading/measuring only.
**AWAITING ⟨decision⟩** — blocked on one named ruling. **OPTIONAL** — off the Letter's critical path;
may run, may be dropped, and its absence is not a publication blocker.

The named decisions referenced:

- **`D-Y-CONSTRUCT`** — a committed authorization to construct Y (`R2(iv)`).
- **`D-Z-SCOPE`** — the four-part complete-successor ruling requested in the Z packet §1.
- **`D-C3-VOI`** — a value-of-information note **signed by Joseph** (`R4`).
- **`D-C3-RUN`** — a **separate** committed reauthorization naming the seed-scan run (`R4`). *A VOI
  signature does not by itself revive compute authority.*
- **`D-RESOURCE`** — an exact resource authorization naming a run (`R5`).

| # | original subject | disposition | why |
|---|---|---|---|
| **11** | Y contract + all seven cause dispositions | **NOW, rewritten — DELIVERED** as `PREDECLARE-20260905-cause7-only-successor-Y.md` | `R2` authorizes drafting Y's producing path, receipt schema and test contract. The seven-cause part is **struck**: cause-7-only |
| **12** | cause-3 VOI + derive stop options | **NOW, rewritten** (§4.2) | `R4` suspends the scan pending `D-C3-VOI` **and** `D-C3-RUN`. The *"derive two or three date/resource-stop options"* half is **struck** — `R5` already fixed them |
| **13** | cause-1 note disclosure | **NOW**, if no note session is active | The obligation is real but is **cause 1's**, from `DECISION-20260901-…-oi172-oi173` `RULING 1` (*"MATERIAL ENOUGH TO NEED ITS OWN STATEMENT IN THE NOTE"*). **`R3` creates no cause-7 note obligation** — do not merge them |
| **14** | corrected 5D statistical component | **AWAITING `D-Z-SCOPE`** | This is **cause 6**, outside Y's cause-7-only scope. Its *"before Y adoption"* clause is void |
| **15** | selection-complete lateral component | **AWAITING `D-Y-CONSTRUCT`** | The closest match to Y as ruled; scope is right. `R2(iv)` blocks implementation-to-production, and the spec it must build against is #11's deliverable |
| **16** | Y assembler + terminal validator | **AWAITING `D-Z-SCOPE`**; reduced form folds into #15 | An assembler integrating statistical **and** lateral components is a **total-covariance** build — `R2` says Y is not that. Y's own writer/validator belong to #15 |
| **17** | two independent pre-launch reviews | **AWAITING #15**, then required before `D-Y-CONSTRUCT` is exercised | Keep **both** reviews and their independence; the static and validator prompts stand as written |
| **18** | pilot + production | **AWAITING `D-Y-CONSTRUCT` + `D-RESOURCE` + both #17 PASSes** | Its own text already requires *"Joseph's exact resource authorization"*. `R5`'s ceilings are not it |
| **19** | independent replay | **AWAITING #18** | Stands as written; cold checkout, no producer helpers |
| **20** | one-shot adopt/reject packet | **AWAITING #19, rewritten** | **"Adopt Y" is not an outcome** (`R2(iii)`). Becomes a **grading packet for `(cause 7, Y)`** — four legs, routed to a lane `BEN-381` does not disqualify. Joseph alone grades |
| **21** | projections + deliverables | **AWAITING `D-Z-SCOPE` or the stop** | Projections require an **adopted trunk**; Y can never be one. The stop branch — preserve the central-only Letter, state the quarantine plainly — is live and correct |
| **22** | publication release review | **AWAITING #21 or the stop** | Read-only, valid as written. Keep its "external states the repository cannot establish" clause: co-author review, collaboration review, submission authority |
| **23** | PET scope, three meanings | **OPTIONAL, rewritten** | `R6` **already ruled** PET diagnostic. Asking Joseph to "select scope" among three meanings reopens a settled question. Rewrite as: accept diagnostic status; document reconsideration criteria **only** via `OI-126`'s ladder — estimator-equivalence **plus** coverage, where coverage is a different object from verifying the construction |
| **24** | authoritative typed semantics | **NOW, OPTIONAL** | Evidence work within existing access. Both prompts stand, including `BLOCKED` rather than choosing conventions |
| **25** | freeze PET-v2 contract | **AWAITING #23 + #24** | Preserve the five Gate-6 prohibition keys **exactly**; a proposed contract cannot supersede them |
| **26** | recover the fixed-draw attempt | **NOW, OPTIONAL** | Bounded evidence recovery, no retraining, no validator repair, no branch merge. Note the gap: the salvage manifest is **not in the repository** (`INTEGRATION-20260903-wave1-routing-freeze-and-ledger.md:218`) |
| **27** | independent equivalence replay | **AWAITING #26** | Add: **historical recovery does not validate PET-v2.** Its outcome validates only the estimator and contract actually tested; any changed estimator, semantics or inference needs an explicit applicability assessment |
| **28** | comparative benefit campaign | **OPTIONAL, DEFERRED** | Three sessions, GPU-scale, no authorization, no prerequisite met |
| **29** | coverage campaign | **OPTIONAL, DEFERRED** | Gated on #27 **and** #28 passing |
| **30** | PET terminal decision | **OPTIONAL, DEFERRED** | Keep its refusals: do not treat the partial `C_stat` as verified or paired, do not infer Gate-6 permission |

**A completion criterion that must be written down now, because #28–#30 will otherwise re-enter as
blockers:** *completing PET coverage is not required to finish the publication.* Retaining PET as
diagnostic is a **valid terminal disposition** under `R6`, not a deferral of an obligation.

## 3b. The recommended cause-disposition map, checked against evidence

#11 offered a "recommended starting map". It is a **proposal**, and four of its seven rows do not
survive contact with the board. Checked against `SCOREBOARD-20260817` (CAND column) and the rulings:

| cause | #11's proposed disposition | verdict |
|---|---|---|
| 1 | measure-and-disclose | **Right conclusion, wrong owner.** Already ruled: `RULING 1` made it a **note obligation** and cause 1 **does not close**. It is #13's work against G, not a Y disposition |
| 2 | demonstrate inapplicability / correct construction | **Unnecessary.** Cause 2 is **all four legs MET** on CAND — the one discharged cause |
| 3 | resolve by value-of-information | **Right, and already ruled** — `R4`. But the unit is wrong: see §4.2 |
| 4 | demonstrate inapplicability to Y, no log sweep | **Misdescribed.** Cause 4's `M` for G is `OPEN` **and cannot become MET** (a history property, verified in the Z packet §5). That is not "inapplicability" — it is permanent unmeetability, for which `§0` has no token |
| 5 | demonstrate inapplicability to scalar GBDT | **Already done.** `N/A` on its merits, landed in `VL66` at `d1c5f90`. Nothing to do |
| 6 | repair the complete 5D statistical block and exact projections | **Out of scope for Y** — cause 6, and `P` is OPEN because *"no product rebuilt at all"*. Belongs to Z |
| 7 | replace support-limited laterals with the five selection-complete active blocks | **Confirmed by evidence** — and the five is a *kinematic-migration* subset of nine detector laterals, justified by `VALIDATION_LEDGER.md:790` (`MinosEfficiency` and `GEANT_*` are weight-only). Re-measure on G's own `combined_source` before construction |

**Net: only row 7 is Y's, and only rows 1 and 3 name live work — both against G, neither via Y.**

## 4. Session prompts

Each inherits the shared preamble and the authority addendum unchanged. **Each ends with the Wave 1
return envelope.**

### 4.1 #13 — cause-1 note disclosure — *previous note owner if active, else fresh*

> Implement the cause-1 disclosure **already ruled** in
> `DECISION-20260901-joseph-oi172-oi173-magnitude-legs.md` `RULING 1`: the `+3.1%`/`+5.9%` √Tr
> difference with a `1.7–2.0×` median per-band ratio is **material enough to need its own statement in
> the note**, and cause 1 **does not close**. Read that ruling and its three grounds before drafting a
> sentence. Disclose the magnitude **without** presenting a large systematic as a construction failure
> and **without** claiming a settled mechanism. `R3` creates **no** cause-7 note obligation — do not
> import one.
> Audit note, primer and paper **independently** for PET's diagnostic-only status (`R6`) and for any
> old adopted/quarantined covariance language. **Change no numbers.** Build all three twice, inspect
> logs for unresolved references, render and check the text, then synchronize and verify the standalone
> analysis-note repository, recording **both** remote heads.
> If a note session is already active, do **not** overlap it — return the exact edit proposal to that
> session instead.

### 4.2 #12 — cause-3 value of information — *fresh session, parallel with everything*

> Read `R4` and `PREDECLARE-20260901-cause3-mii-estimator-seed-magnitude.md` completely.
> **Start from the corrected premise.** The packet's rev-1 claim that the scan changes nothing was
> **false and was withdrawn before the ruling**. §4 has **six exhaustive branches** — two INCONCLUSIVE,
> **one MET**, **three NOT MET** — so the scan **does** change a named decision: it grades cause 3's
> `M(ii)` for this candidate.
> Build the value-of-information table on the **correct unit**. Distinguish (a) the `M(ii)` **leg
> grade**, (b) cause-3 **discharge**, (c) covariance **adoption**, (d) **publication** consequence. **Do
> not dismiss a measurable change to (a) merely because it cannot alone deliver (b), (c) or (d)** —
> §5 already records that it cannot, and that is not an argument against the measurement.
> If a scan is justified, derive the smallest defensible design and its cost from **committed run
> accounting**; §6c's suspended figure is ≈`8.7` GPU task-hours over 13 scheduler tasks, `18` worst
> case against a ratified arm-1 envelope of `20`. Otherwise recommend skipping it and state exactly
> which leg stays OPEN as a result.
> **Preserve** the ruled stop — `2026-09-30`, `500` GPU task-hours, `500` CPU task-hours, t0
> `2026-09-02T13:44:27Z` (commit `9ce59a59`). **Propose no new cap options and no new accounting
> start.** Do not retune
> §3's thresholds `f_agg <= 0.0415` / `f_med <= 0.0274`.
> **Produce a packet only.** `D-C3-VOI` **and** `D-C3-RUN` both remain prerequisites to execution, and a
> VOI signature alone does not revive compute authority. Launch nothing.

### 4.3 #24 — typed semantics — *previous typed-evidence session, then a fresh reviewer*

Both original prompts stand. Add to the originating prompt:

> PET's status is **ruled** (`R6`): diagnostic and method-development. A favourable typed-descriptor
> result is **explicitly not a promotion** and must not be reported as one. Note that
> `nd-unfolding/pet/TYPED_DESCRIPTOR_SEMANTIC_AUDIT-20260901.md` is **untracked** at `c71b319a` — bind
> what you rely on to committed bytes or say plainly that it is uncommitted.

### 4.4 #26 — recover the fixed-draw attempt — *previous equivalence session*

Original prompt stands. Add:

> The salvage manifest is **not in the repository** (`INTEGRATION-20260903-…:218`); its 21/21 digest
> matches and the `57644535` outcome are S8.1's facts as consolidated by S9. Recover **evidence**, not
> conclusions: bind each item to code, branch, inputs, sizes and digests. **Do not retrain, do not rerun
> GPU work, do not repair the validator in place, do not merge the strategy branch, and announce no
> equivalence result.** Recovery of the historical attempt **does not validate PET-v2**.

### 4.5 #23 — PET value proposition — *optional, fresh*

> `R6` has **already ruled** PET diagnostic and method-development. **Do not ask Joseph to re-select
> among three scopes** — that reopens a settled ruling. Instead: document the value proposition and the
> **reconsideration criteria only**, via the ladder `OI-126` already names — **estimator-equivalence
> plus coverage**, where coverage is a **different object** from verifying the existing construction.
> State plainly that architectural novelty, classifier AUC and "full event" are **not** sufficient, that
> passing a Gate-6 leg is not a promotion, and that **retaining PET as diagnostic is a valid terminal
> disposition** — completing PET coverage is not a publication prerequisite. Preserve the five Gate-6
> prohibition keys verbatim. Ask for no compute.

## 5. The decision record's §4 applications — RECONCILED against committed evidence, not relisted

The 2026-09-02 record listed six. **A list written then is a statement about then.** Each row below was
re-measured at `origin/main` `c71b319a` before being called outstanding, because dispatching six
sessions for a list of six would be routing from the record instead of from the tree.

**Result: five are unapplied and need an owner; one is substantially done.**

| # | application | measured state at `c71b319a` | still needed? |
|---|---|---|---|
| 1 | `SCOREBOARD:85` — annotate cause 7 **permanently OPEN** for G; add a **new** `(cause 7, Y)` row without editing `:85`'s grade | `:85` still reads *"**OPEN** — discharged for a THIRD artifact; see §5"*. No `permanently OPEN`, no `(cause 7, Y)` row. The board cites `DECISION-20260902-joseph-applies-oi173-cause4-m` and `RULING-20260902`, but **not** the cause-7 ruling | **YES** — the board's owner |
| 2 | `DECISION-20260831` §1 — amendment note recording `R2`'s cause-7-only prospective amendment | no reference to `R2` or 2026-09-02 in that record | **YES** — lane C (rulings) |
| 3 | `PREDECLARE-20260901-cause7` §1 `M` and §2 — appended dated ruling section closing the three reserved questions | `:153` and `:186` still carry the **original** *"Joseph must rule …"* text; no appended ruling section | **YES** — that predeclaration's author lane |
| 4 | `PREDECLARE-20260901-cause3-mii` §6c — record `R4`'s suspension **on the authorization**, not on the criterion | no `SUSPEND`/`R4`/2026-09-02 marking anywhere in the file | **YES** — the cause-3 lane |
| 5 | `DECISION-20260901-…-oi187` half (b) and `OI-187`'s row — record `R5`'s conditional supersession and the stop's three values | no `R5` supersession note in that record; **no `2026-09-30`, `500` GPU or `500` CPU value anywhere in `docs/OPEN_ITEMS.md`** | **YES** — the publication-scope lane |
| 6 | a `WAKER`/accounting entry metering `R5` from t0 | **substantially applied by Wave 1.** `docs/orchestration/r5_meter.py` implements `R5`'s unit, both ceilings, the inclusive boundary and the correct t0 (`:31-34`), alongside fail-closed admission in `campaignctl.py`. **Residual:** no operational receipt (`state/r5-meter-receipt.json` absent), no standing `WAKER.md` entry, no unattended tick configured | **PARTLY** — residual only; **do not rebuild the meter** |

**What changed since the record was written, stated precisely.** Item 6's premise — *"the campaign has
no working spend meter today"*, `RUNS.tsv` 12 days behind — **described 2026-09-02 and no longer
describes `main`.** The instrument now exists. What has never happened is a measurement: per
`ACCEPTANCE-20260905-wave1-review-pass-and-closeout.md`, **no operational accounting receipt is
committed and no unattended execution is configured**, and *"the queue admits no item at all until a
receipt measured on Perlmutter is committed, and none is."*

**Two cautions for whoever picks up item 6's residual.** Taking a first receipt requires cluster
contact, so it is not a documentation task and must be costed against `R5` itself. And nothing here
establishes that the meter behaves correctly against real `sacct` output — **deployment readiness is
unmeasured, not demonstrated.**

**Sequencing.** Items 1–5 are five independent document edits with five distinct owners and no shared
file; they can run concurrently. Item 6's residual is the only one that is not a document edit.

## 6. Parallelization

**Runnable concurrently now, no shared files, no interface dependency:**

- **#12** cause-3 VOI packet — touches `docs/orchestration/` only, its own new file.
- **#13** cause-1 note disclosure — the **only** publication-editor lane; must not overlap another.
- **#24** typed semantics — `nd-unfolding/pet/`, optional.
- **#26** fixed-draw recovery — optional, evidence only.
- **§5 items 1–5** — five distinct owners, five distinct files. **Not six**: item 6 is
  substantially applied and carries only a residual (§5).

**Contention to manage.** #13 and §5 item 5 both touch publication scope: #13 edits note/primer/paper,
item 5 edits `OI-187`'s row. Adjacent, not overlapping — but run them in a known order rather than
blind. §5 items 1 and 3 both concern cause 7: item 1 edits the board, item 3 edits the predeclaration;
**both must leave `PREDECLARE-20260905`'s Y spec alone**, which is this lane's.

**Strictly serial, and no amount of parallelism helps:** #15 → #17 → #18 → #19 → #20, each on the
previous plus a named authorization.

**Do not start** #14, #16, #21, #25, #28, #29, #30 — each is blocked on a ruling that does not exist.

## 7. What this plan does not do

It authorizes nothing, grades nothing, discharges nothing, constructs nothing, launches nothing, spends
nothing, adopts nothing, moves no count and no gate, changes no publication claim, does not reopen or
re-option `R5`, does not alter PET's status, and does not widen Y beyond `R2`. It performs none of §5's
owner applications. It regenerates no state; `OI-73`'s hold stands.
