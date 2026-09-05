# PACKET 2026-09-05 — one question for Joseph: does a COMPLETE scalar-5D successor become a
# grading and adoption subject, and if so under what ruling?

**CITABLE FOR:** the scope question in §1 and the option set in §7.
**NOT CITABLE FOR:** any authorization, any grade, any construction, any adoption, any count, any
spend, or a claim that a complete successor has been approved, recommended for approval, or begun.

**This packet asks one question and takes no decision.** It does not construct, does not grade, does
not launch, does not adopt, and does not alter PET's status. Gate 2 remains FAIL; CAND `1 of 7`,
QUOTED `0 of 7`; `R5`'s stop is unchanged and is **not** reopened here.

**Controlling authority:** `DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md`, sha256
`0836139b1c9a057c194a81a94d45c9f979209a9ac293d4bc8434e6b43fc1a064`, verified at `origin/main`
`c71b319a`. It overrides this packet wherever they conflict.

## 1. The question, and the exact ruling that would answer it

> **Should exactly one COMPLETE scalar-5D successor — a new artifact intended as the grading subject
> for ALL SEVEN quarantine causes and therefore as a possible adoption subject for the publication
> trunk — be specified? If so, is its specification authorized now, and does its construction remain a
> separate later authorization?**

**A ruling that answers it must say four things.** Fewer leaves the next lane inferring one:

1. **Subject.** That a named complete successor — called **Z** here, deliberately not "Y" — may be
   named as the grading subject for **all seven** causes, with G as its digest-bound parent.
2. **Cell discipline.** Whether Z's seven cells are **new and distinct** from G's, and that G's cells
   and `(cause 7, G)`'s permanent OPEN are untouched — the `R2(ii)`/`R1` treatment, applied to seven
   cells instead of one.
3. **Combination rule.** Whether Z's grades may be tallied as a **self-contained** `n of 7`, and the
   restatement that they may never be mixed with G's — the `R2(iii)` prohibition, which today forbids
   exactly the arithmetic a seven-cause Z would otherwise invite.
4. **Stage gate.** Whether this ruling authorizes **specification only** (the `R2(iv)` posture), with
   construction and compute each requiring their own committed authorization.

**Nothing here asks to change `R5`.** The stop stands at the first of `2026-09-30T00:00:00Z`, `500` GPU
task-hours, `500` CPU task-hours, metered from t0 = the decision record's commit instant
`2026-09-02T14:40:06Z` (commit `dae18f22`). **25 days remain** as of 2026-09-05. A Z ruling that
arrives too late to be executed before the stop is still a meaningful ruling — it fixes what the next
campaign is — but it should be taken knowing the date binds.

## 2. Y and Z are different objects — the distinction this packet exists to protect

`R2` permits **Y**. It does not permit Z, and Y must not be quietly widened into it.

| | **Y — permitted today** | **Z — requires the §1 ruling** |
|---|---|---|
| authority | `R2`, already ruled | none; this packet asks for it |
| causes it is a subject for | **cause 7 only** (`R2(i)`) | all seven |
| construction | swap G's five-band lateral block; everything else bit-identical to G | a full rebuild: whatever causes 1, 3, 4, 6 require, plus cause 7's replacement |
| what a full PASS yields | cause 7 discharged **for Y**, and nothing else | a self-contained `n of 7` for Z, and only then a possible adoption case |
| adoption | **never** — not a covariance candidate (`R2`) | the point of it |
| status now | **specified** — `PREDECLARE-20260905-cause7-only-successor-Y.md` | not specified, not authorized |

**The one-sentence version:** Y answers *"can this defect be corrected?"*; Z answers *"is there an
adoptable trunk?"* Y cannot answer the second question **no matter how well it goes**, because Y has no
causes 1–6 grades at all — those causes are graded against G, and `R2(iii)` forbids borrowing them.

## 3. Why `R2` does not already permit Z, read against its own words

`R2(i)`: *"**Exactly one** cause-7-only successor **Y** … may be named as a grading subject **for cause
7 and no other cause**."* Both bounds are explicit. `R2(iii)` then forbids the combination that would
otherwise let Y's cause-7 grade complete G's set. `R2`'s "LEAVES UNCHANGED" adds: *"Y does not exist, is
not adopted, and is not a covariance candidate."*

So the gap is not an oversight to be read around. `R2` **decided** that the successor permitted on
2026-09-02 is cause-7-only. Z is a larger subject, and larger subjects are Joseph's to name.

## 4. The seven causes as they stand for G — checked against the board, not summarized from it

From `SCOREBOARD-20260817-quarantine-seven-causes.md`, CAND column (G). The right-hand column is this
lane's **assessment**, offered for challenge, of whether a **new artifact at a new revision** could
reach a different leg state — it is not a grade and not a prediction of one.

| cause | CAND state for G | could a new artifact plausibly differ? |
|---|---|---|
| **1** one-sided endpoint interpolation | `C` MET, `P` MET, **`M` MEASURED, not MET**, `T` MET | Yes in principle — `M` was ruled **material**, so the construction choice, not the measurement, is what stands in the way |
| **2** CV centering | **all four MET** | No change needed; already the one discharged cause |
| **3** varying estimator seeds | `C` PARTIAL, `P-i` PARTIAL, `P-ii` OPEN, **`M` OPEN and NOT CURRENTLY MEASURABLE**, `T` MET | Partly — `P-ii`'s premise is **false at HEAD** (four write sites exist, POINTER 4); `M(ii)` is gated by `R4`'s suspension, not by the artifact |
| **4** scalar jitter subtraction | `C` MET, `P` MET, **`M` OPEN — AND IT CANNOT BECOME MET**, `T` MET | **Yes — see §5.** This is the single strongest ground for Z |
| **5** frozen PET weights | **`N/A` on its merits**, landed in `VL66` | Already disposed; needs nothing |
| **6** incomplete statistical projection | `C` PARTIAL, **`P` OPEN — "no product rebuilt at all"**, `M` OPEN, `T` MET | Yes — `P` is open precisely because nothing was rebuilt; a rebuild is the remedy |
| **7** CV-support-limited lateral | **permanently OPEN for G** (`R1`) | Yes — this is exactly what Y's replacement algebra does, on a full rebuild instead of a lateral-only swap |

**Read the table honestly in both directions.** It says a new artifact has a plausible route on causes
1, 3, 4, 6 and 7. It does **not** say any of them would succeed, how much they would cost, or that the
sum is achievable before `R5`'s date. Four of the five routes are unquantified.

## 5. The cause-4 finding, which is the strongest ground for Z and is measured, not argued

The board records cause 4's `M` for G as **`OPEN` — and unable to become `MET`**: no **committed**
revision of `unified_throw_cov.py` carries both the jitter-floor print and the flux fix `081ae4ac`, so
no revision able to produce G's fluxfix input could print the unified/block ratio. The board adds that
`OPEN` is merely *"the nearest token `§0` defines; there is none for permanently unmeetable."*

**Re-measured for this packet, because a conclusion this load-bearing should not be inherited:**

- the jitter-floor print lived at the retired `a0cdc019:232-252`, committed **2026-06-08**
  (`FINDING-20260901-cause4-jitter-floor-recovered.md`);
- the flux fix `081ae4ac` was committed **2026-07-31**;
- `git merge-base --is-ancestor 081ae4ac a0cdc019` is **false** — the print revision **predates** the
  flux fix, so the board's "no committed revision carries both" holds;
- at `origin/main` `c71b319a`, `unified_throw_cov.py` contains one `jitter` occurrence and it is a
  **comment** at `:476`, not the print.

**The consequence, stated as an assessment and not a grade.** The obstruction is a property of the
*committed history*, not of physics or of the data: a **new** revision that re-adds the print on top of
current HEAD would carry both. G can never benefit — G's bytes were produced by a path that did not
print. A **new artifact built at that new revision could**. **Verification this would need before it is
relied on:** that the re-added print is the same quantity the retired code printed, that its operands
are the new build's own, and that adding it does not change the covariance content.

**This is the honest core of the case for Z, and also its limit.** It shows a cause that is permanently
unmeetable for G is *not* permanently unmeetable in principle. It does not show the other four routes
close, and it is not a recommendation.

## 6. What a Z campaign would run into — the two facts that should be on the table before the ruling

**6.1 There is no working spend meter.** The decision record's §4 item 6 names it and calls it *"the one
that fails silently"*: `RUNS.tsv` is 12 days behind the scheduler and carries no row for the round-2
374-task run or the four gap-3 failures, so **`R5`'s ceilings cannot fire against an unmaintained
ledger. The date can.** A multi-cause campaign is exactly the workload that would need the ceilings to
be real. **Item 6 is a prerequisite to a Z campaign, not a parallel chore.**

**6.2 The only existing complete construction is refused by the publication gate.** S —
`std_final5_candidate.root`, run `57128458` — carries `publication_gate_rejects_this: true`, and
`p4_adopt_standard.py` refuses it outright; `fps_build_control_manifest.py:202-204` **dies** if the gate
fails to reject it (`SCOREBOARD` §5). So Z is a **new build**, not a promotion of S, and any plan that
reads S as "most of the way there" is wrong about the gate.

**Cost anchor, for scale only and not a bid:** a complete seven-arm k=0 rehearsal round is ratified at
**70 GPU / 113 CPU task-hours** (`AMENDMENT-20260831-oi177-per-arm-ceilings.md` §5). `500/500` is about
seven GPU rehearsal-equivalents and 4.4 CPU ones. **No Z cost estimate exists**, and this lane does not
manufacture one; deriving it from committed run accounting is work a Z specification would have to do.

## 7. The options, with what each forecloses

Presented as alternatives. **This lane does not select one**, and none is marked recommended.

| option | what it rules | what it forecloses | cost before the stop |
|---|---|---|---|
| **A — no Z** | the campaign finishes as scoped; Y stands as the cause-7 answer | any scalar-5D adoption this cycle; the Letter is central-value-only per `R5`'s default | none |
| **B — specify Z only** | Z is named as a seven-cause subject; **specification only**, construction a separate later authorization (the `R2(iv)` posture) | nothing irreversibly; produces a costed contract Joseph can then accept or decline | drafting only, no compute |
| **C — specify and authorize Z's construction** | B, plus a construction authorization, plus a named resource grant | requires §6.1's meter first; commits real GPU/CPU inside a 25-day window against an uncosted campaign | unknown — this is the objection to C |
| **D — defer** | revisit after the stop with the campaign's measured costs in hand | a Z result this cycle | none |

**One observation about B, offered as reasoning and not as advocacy.** B is the only option that makes
the cost of C knowable, because a Z specification is what would produce the estimate §6 says does not
exist. B also matches the shape Joseph has already used twice — `R2(iv)` for Y, and `R4`'s split of VOI
from run authority.

## 8. What this packet does not do

It authorizes nothing, grades no leg, discharges no cause, constructs nothing, launches nothing, spends
nothing, adopts nothing, moves no count and no gate, changes no publication claim, does not reopen `R5`
or propose new caps or a new accounting start, does not alter PET's diagnostic status, and does not
widen Y. It performs none of the decision record's §4 owner applications. It regenerates no state.
