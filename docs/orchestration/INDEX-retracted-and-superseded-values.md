# INDEX — retracted and superseded values

**Why this exists.** A retracted number does not stop being readable. Every value below still appears in the
corpus, presented with the same confidence as a live one, and **nothing at the point of use marks it dead**.
A fresh session writing the analysis-note update reads artifacts, not this session's context — so a value that
is only known-dead inside one agent's head is, operationally, alive.

**READ THIS AT WRITE TIME, NOT ONLY AT QUOTE TIME.** Consulted when you find a suspicious number, this file
catches **quotation** errors. Consulted **before you commit a number**, it catches **derivation** errors — and only
the second would have caught the `0.0383` row below, which was written into a decision file by the same session
that had retracted its parent value eight hours earlier. Treat it as a checklist for writers.

**THE RULE THAT MAKES THAT NECESSARY: a retraction propagates by STRING MATCH, and derived quantities do not
string-match.** `188.4×` was caught because it *is* the retracted number. `0.0383` was missed because it is
`0.05 −` the retracted number. **So grepping the retracted value does not find its descendants.** Before
committing any number, ask what it was computed *from* and whether that operand is on this list — not whether
the number itself is.

**AND THE SECOND WRITE-TIME RULE, distinct from the first: CHANGING A NUMBER RE-POINTS ANY SOURCE CLAIM IN THE SAME
SENTENCE.** The derived-quantity rule above is about a *number* downstream of a retraction. This is about a *citation*
downstream of a value swap: a sentence reading *"the median `4.822%` is taken directly from the matcorr rollup
summary"* was **true**, and became **false** when the value was correctly updated to `6.865%` — which is not in that
summary at all (it reports `6.830%` and `6.845%`; `6.865%` is the block sum, in `2D_OMNIFOLD_STUDY_STATUS.md:101`).
**Nothing about the edit looked wrong; the attribution was collateral.** So: after changing a number in prose, `grep`
the new value against the file the sentence names. And be suspicious wherever two quantities have historically agreed
at the printed precision — pre-fix the block sum and universe+bootstrap printed identically, which is what let one
sentence describe two things. **This applies to the `\gbdtFive*` update still ahead:** `sec_systematics.tex:163-168`
is prose-with-sources of exactly this shape. (BEN-087.)

**Also read it before quoting any number from `VALIDATION_LEDGER.md`, a `PREDECLARATION-*`, a `*_RUN_LOG.md`, a
receipt JSON, `docs/INTEGRATION_CHECKLIST.md`, or a commit message.**

**Sourced from `git grep`, not from recall.** Every "where it still appears" entry below was located by search
at `2026-08-11`. Where I could not source a location, the row says so rather than listing it from memory — an
index built from memory has exactly the defect it exists to fix. *Requested by the oversight session; the
`VALIDATION_LEDGER` exposure was found while building it and is the most serious entry here.*

## A failure mode this index found that a consistency check CANNOT catch — it EXONERATES it

Most rows here fail a check: a wrong denominator, a stale threshold, a retracted verdict. **One row passes
one.** `\petRatio = 0.912` is *correctly computed* from the operands quoted beside it —
`2.796\text{e-}38 / 3.066\text{e-}38 = 0.91194` → `0.912`. So a reader told *"0.912 is suspect"* reproduces the
arithmetic, finds no error, and **concludes it is fine.** The consistency check does not merely fail to catch it;
it actively exonerates it.

**Name for the class: a correctly derived value whose OPERANDS went stale.** The derivation is sound, every
internal check agrees, and the inputs describe a configuration that no longer exists. The only thing that
catches it is asking *where each operand came from and whether that source is still current* — which is the
`MATCHES / SUPERSEDED / UNSOURCEABLE` question, not an arithmetic one.

**And the structural version, which generalises past this row:** `2.796e-38` and `3.066e-38` are **inline
`\SI{}` literals** in `sec_pet.tex:41-42`, not entries in `values.tex`. **Any derived macro whose operands are
inline literals looks managed while its inputs sit outside the marking convention entirely** — marking the macro
cannot reach them, even in principle. That is a hole in the mechanism rather than an oversight in one entry, and
it is why an audit keyed on *"every quoted value's canonical source"* will land such operands as UNSOURCEABLE by
construction, which is the right outcome.

## The two kinds of entry, which a reader will otherwise conflate

- **DEAD** — replaced, and must not be quoted in any form.
- **ALIVE-AS-CITED-ARTIFACT-ONLY** — the value is a real, validated artifact number and must keep being cited
  *as that*, but must **not** be used as the best estimate or as *the* value of the quantity.

Same distinction as `PROCESSED.txt`'s grandfathered-vs-verified split, and for the same reason: two different
claims that look identical on the page.

## Index

| dead value | where it still appears | what supersedes it | why it died |
|---|---|---|---|
| **`28.50 A100-h`** (the `C_syst` re-seed cost) **and its descendant ratio `~28.5×`** — the ratio is listed SEPARATELY and deliberately: it does not string-match `28.50`, so this file's own first write-time rule applies to it | **STILL LIVE at six sites owned by four lanes, NOT edited by the indexer — their owners were notified instead:** `COST-20260817-mii-seed-scan-derivation.md:154,160,166` (**the ORIGIN**: the derivation table that produced it, and `:160` is the sentence that routes the request to Joseph); `SCOREBOARD-20260817-quarantine-seven-causes.md:133-134,161` (the `~28.5×` descendant, in the cell that disqualifies `FOOTING-20260817`); `HANDOFF-20260817-1133Z.md:39,41,98`; `PREDECLARATION-20260817-mii-seed-scan-cause-3.md:88,92` (already warns the figure does not cover a composite arm — **correct, and for a different reason than this one**); `FINDING-20260817-cause3-C-leg-does-not-cover-the-dominant-block.md:71` (*"until Joseph rules on the `28.50 A100-h`"*). **Corrected in situ 2026-08-17 by their author:** `FINDINGS.md` `BEN-392` and `FINDING-20260817-unqualified-transport-of-good-measurement.md`. | **`39.078` A100-h over 189 tasks, `+37.1 %`** — `BEN-247`, `6afda0e`, `EXTENT-20260817-2850-a100h-scope-and-missing-legs.md` §0. Arithmetic re-derived by a second lane: `23.840 + 14.2075 + 1.030 = 39.0775`; `14.2075` is a measurement over all 19 universes, not the `14.36` forecast (they agree to `1.07 %`). The descendant ratio becomes **~39×** on the same denominator. | **Not a bad measurement — a leg measured over 5 of its 19 members.** The lateral term `3.626` came from job `55891346`, a truncated attempt (`_5,_6` FAILED, `_7,_8` CANCELLED mid-run, `_[10-18]` never started at `00:00:00`); the completion run `55894759` (19 `COMPLETED`) was absent from the table. **`3.626` reproduces to the digit — for 5 of 19 universes** — so `BEN-077`'s ingredients rule performed exactly as designed and is BLIND to an omitted operand. **A `CANCELLED` id forces the search; a partially-`COMPLETED` id silently satisfies it.** Cross an id set against the design's own member count before trusting any per-leg total. |
| **`602bbcf2…`** — the 5D candidate ROOT's whole-file sha256 (`std_final5_candidate.root`) | **Still recorded, correctly, as what three audits verified:** `20260810T0630Z-cross-object-verdict.json` and the two product-audit legs; `p4_build_components.py:213-220`'s comment. **These are receipts and audit records — do NOT edit them.** The object itself is preserved intact at `/pscratch/sd/j/josephrb/PRESERVE-p4-candidate-20260816/std_final5_candidate.root`, digest re-verified 2026-08-16 | **`950f8cb1…`** for *"the current 5D candidate file"*. **But the audits' SCIENTIFIC conclusions transfer unchanged**, because the covariance CONTENT is bit-identical across the rewrite — TH2D content hashes `f26b3bfe…` (5D total) and `c1fe11b1…` (4D stored) match the audited values, measured by lane B. **Only the whole-file digest BINDINGS are stale** | **The file was rewritten by the authorized stages-4-6 run on 2026-08-16** (`57128458`, `rc=0`). It grew 23,969 bytes: **49 keys where the audited object had 47**, the addition being `hRowIndex5D` — the row-index array those same audits asked for. `p4_build_components.py:213-220` says the audited artifact is *"deliberately NOT rewritten"* because *"invalidating three passing audits to add a convenience array would be a bad trade"*; **the authorization postdates that comment and made the trade.** **NOT a defect** — the rewrite added exactly what the audits requested and changed no covariance content — but the comment now describes a decision that has been superseded, and a reader quoting `602bbcf2…` as the live object would be wrong. Found by lane B while closing the audits' own `gaps_remaining[0]` |
| **`~105 draw-sd`** / **`~105-sd`** (the `BEN-360` disagreement, gap ÷ draw sd) | **STILL LIVE, deliberately not rewritten:** `docs/orchestration/state/RECEIPT-foldforward-instrumented-closure-20260815.json:27` (a recorded artifact — indexed, not edited) and `nd-unfolding/ND_OMNIFOLD_RUN_LOG.md:8864` (append-only chronology). **Corrected in situ 2026-08-16:** `FINDINGS.md` (4 sites, `BEN-360` ledger + index rows), `FINDING-20260815-an-instrument-recorded-the-neighbouring-quantity.md:37`, `FINDING-20260815-a-predeclared-pessimism-is-the-least-checked-claim.md:12`. **Code sites** — `closure_foldforward_instrumented.py:196,:561`, `tests/test_closure_foldforward_recording.py:564`, `pet/sbatch_foldforward_instrumented_closure.sh:117` — corrected by lane B under the wrapper pin. Quoted-as-wrong (correct usage, leave alone) in `FINDING-20260816-a-fixture-degenerate-on-the-axis-under-test.md:98` | **`75.8 draw-sd`** — gap `0.981165 − 1.011418 = −0.030253` ÷ the arm-0 3-draw sd `0.000399` (`VL134`). **Always carry the operands**, since the sole defect here was a figure with none. If the standard error is meant instead, it is **`131.3`** (`0.000399/√3`) — state which, because the two differ by `√3` and both are defensible readings of "distance" | **MIS-NORMALISED, NOT FABRICATED** — and this cell said *"derives from nothing"* until 2026-08-16, which was itself wrong. `104.7` is real and correctly computed: it is the receipt's own field at `:23`, `in_draw_sd_of_that_row: 104.7181920082435`, over `sd: 0.0002888930898171582` — the spread of the **substituted (consumed-push) rows**. **So it was divided by the sd of the very quantity that was the mistake, and its own key says so.** `BEN-360`'s shape a third time: the receipt disambiguated itself in a key beside the number, the reader dropped the qualifier `of_that_row`, and the first correction then asserted the operand did not exist without grepping for it. Found by lane B (`BEN-342`) while checking the successor instrument; re-derived independently by the mediator. **The aggravating fact: it propagated to 8 sites, two of them inside the very finding pair that states `BEN-361` — *re-derive a predeclaration's own amplitude estimate before repeating it*. The rule failed on its own author, in the document declaring it** |
| **`FINDING — code paths disagree`** (the verdict) | `VALIDATION_LEDGER.md` §2026-08-10 (**now bannered**); `docs/orchestration/RUNS.tsv:267` row `P5A-ANNEALED-NOMINAL-A2-COMPLETE`; `docs/orchestration/state/annealed-nominal-complete-56563761.json`; commit `b1414df` message | **REFUTED.** No established code-path difference — `KNOWN_ISSUES.md` struck-through entry; `PREDECLARATION-20260810-designA-diagnostic-reproduction.md` §RESULT; `535668d` | Production `-0.035546` sits **inside** the diagnostic configuration's own 3-run range, `0.48` sd from its mean |
| **`188.4x` / `188x`** (gap ÷ scatter) | `docs/orchestration/state/annealed-nominal-complete-56563761.json` **— the ORIGIN: it is the live JSON field `predeclared_reproduction.nominal_gap_over_measured_scatter`, and the receipt's `interpretation` built "code paths disagree" directly on it; bannered and superseded in situ 2026-08-13, added here because the adjacent verdict row cited this file and this row did not**; `VALIDATION_LEDGER.md:~1055` (bannered); `RUNS.tsv:267`; `PREDECLARATION-20260810-annealed-production-reproduction.md:102`; `KNOWN_ISSUES.md:511`; `AUTONOMOUS_LOG_20260805.md:3387,3892`; commit messages `7b2198a`, `b1414df` | **`0.967x`** — the SAME ratio with the correct denominator: gap `0.023884971` ÷ the three-point diagnostic sd `0.024701703`. **`0.48` sd is a DIFFERENT statistic** — \|production − diagnostic **mean**\| ÷ sd — which is what the verdict row above quotes. Both are under 1 sd; the stated derivation must match whichever is meant. **Corrected 2026-08-13:** this cell read *"`0.48x` — gap ÷ the three-point diagnostic sd"*, and that division yields `0.9669`, not `0.48` — the distance-from-mean VALUE attached to the gap-over-sd DERIVATION, i.e. this index's own subject-matter error in the row recording it. **Prefer the two figures that need no n=3 sd at all:** the diagnostic's 3-run range `0.0447882` is **`2.239×`** the predeclared window's full width `0.02`, and **`1 of 3`** diagnostic runs falls OUTSIDE the window centred on another (`56611394`). Those are realized containment, not a fitted tail (BEN-025). | Denominator was the **production** scatter, a population the diagnostic configuration does not belong to — the two denominators differ by `194.85×`, and that factor is the whole discrepancy. Superseded twice: `188x` → `6.0x` (two-point difference) → the corrected ratio |
| **`6.0x`** (gap ÷ two-point diagnostic difference) | `AUTONOMOUS_LOG_20260805.md:4127`; commit message at `7b2198a` era | **The corrected ratio as in the row above** — `0.967x` for gap ÷ diagnostic sd, or `0.48` sd for distance from the diagnostic mean; do not carry a bare `0.48x` labelled "gap ÷ sd" | Two points give a **difference, not a spread**. This is the same error as the row above, one step less wrong |
| **`-0.011724321` / `-1.17%`** labelled *"diagnostic expectation"* or *"expected"* | `VALIDATION_LEDGER.md:1051,1055,1062` (bannered); `PREDECLARATION-20260810-annealed-production-reproduction.md:34,96`; `KNOWN_ISSUES.md:480,505,552`; `PREDECLARATION-20260810-designA-diagnostic-reproduction.md` (as the REPRODUCED window centre) | **Nothing** replaces it as an expectation. The configuration's distribution is `mean -0.023761959, sd 0.024701703` (n=3) | It was **one draw** from an `sd≈0.025` distribution and was never a property of anything. **Standing constraint:** no one-shot measurement through the `diagnose_step1_annealed_lr.py` wrapper family may be quoted as a point value |
| **`142 scatters` / `142 production scatters`** (D2 margin) | `nd-unfolding/pet/sbatch_powered_closure_stability_repeat.sh:138` — **hardcoded in the launcher's STABLE verdict text, and it printed at full confidence in `56626305`'s log hours after retraction**; `PREDECLARATION-20260811-powered-closure-stability.md:22,43`; `CLAIMS.md` CLM-012 (ix); `AUTONOMOUS_LOG_20260805.md:4174,4422,4489` | **`22.0`** — margin ÷ the three-run closure sd (`0.000820128`). And preferably **no ratio at all**: all 3/3 draws clear the bar individually | Same wrong-population error. Retracted at `98d502d`. **The launcher instance is the dangerous one** — verdict text should emit the *comparison*, not a derived number that lives elsewhere, or it prints stale claims automatically |
| **`14.7`** (margin ÷ two-point closure difference) | `CLAIMS.md` CLM-012 (ix); `AUTONOMOUS_LOG_20260805.md` 08:25Z entry; commit `98d502d` message | **`22.0`** as above | Two-point difference used as a spread, again |
| **`0.0383` expected fold-forward headroom**, and any phrasing calling production's `0.0144` a *"loss of headroom"* | `KNOWN_ISSUES.md:551` (**fixed**); `AUTONOMOUS_LOG_20260805.md:3323,3433,3882,4786`; and — worst — an earlier version of `state/waker/BLOCKED-ON-USER.json`, the file used to decide promotion (**fixed 2026-08-11T12:35Z**, with a `correction_history` entry) | **Production `|dev| = 0.035609` consumes 71.2% of FROZEN's `0.05` tolerance, `0.014391` remaining.** Tight, worth seeing, **not a regression** | `0.0383 = 0.05 − 0.011724` — headroom implied by the diagnostic arm's **retracted single draw**. There was never a validated `0.0383` expectation, so nothing was lost. **The dangerous part is where it sat:** in a decision file, it biased a promotion decision against promotion on a retracted basis. Raised by the oversight session retracting its own original phrasing |
| **the four `\gbdtFive*` macros** — see **`PROCEDURE-gbdtFive-macro-update.md`** for the enumerated update procedure (written cold 2026-08-11: the four consumption sites, the six relational claims a number-only edit breaks, and the inline `0.30%` at `sec_systematics.tex:171` that a macro sweep will miss) — — `\gbdtFiveBlockMedian` 13.36, `\gbdtFiveAdoptTrace` 5.81e-38, `\gbdtFiveCVTrace` 6.24e-38, `\gbdtFiveMeanShift` 1.65e-38 | `docs/analysis-note/values.tex:57-60`, **all four unmarked**; and **all four print as prose** — `sec_systematics.tex:163` (block median), `:165` (adopt trace), `:166` (mean shift), `:168` (CV trace) | pending adoption of the corrected products; **not this lane's to supply** | dead on **two independent grounds** — the 2026-07-12 quarantine class *and* the J28 flux correction. **`\gbdtFiveMeanShift` moves UP 13.6% while the other three move DOWN ~9%, so no uniform scale factor patches them** and anyone assuming one gets the mean shift backwards. Raised by the oversight session; located here by grep, which found **four** consumed in prose rather than the three reported |
| **`5.8077e-38` / `6.2367e-38`** (5D GBDT adopted covariance) **and `3.8777e-38`** (recoil PET C_total) | `docs/INTEGRATION_CHECKLIST.md:61` and `:62`, both under the heading **"## Verified / quotable (ledger) — safe to keep"** | the corrected post-J28 products, pending adoption | Same shape as the `VALIDATION_LEDGER` row: dead values under a heading that is **an explicit safety claim**. The first pair is the `\gbdtFive*` covariance at full precision. **The second is worse and was not previously reported: `3.8777e-38` is the value `values.tex:70` marks `QUARANTINED` as `\petTotalTrace` (3.878e-38) — so the checklist lists as "safe to keep" a number the note's own macro file marks dead.** Found here while sourcing the row above |
| **`recovery_criteria_met`** (report field) | Every `POWERED_CLOSURE_*.json`: `slurm-56552326`, `slurm-56611837`, `slurm-56626305`, and the graded closure's; documented at `KNOWN_ISSUES.md:447-467` | The **validator** `validate_pet_nominal_gate4.check_powered_closure`, which reads the adopted `residual_over_gap_max` | Computed against the **retired** `recovery >= 0.80` bar, so it reads `false` for results the campaign has adopted as passing. **A self-report, never the gate** |
| **`RESIDUAL_OVER_GAP_MAX = 0.20`** (the retired bar, still executing) | `nd-unfolding/pet/closure_powered_truth_reweight.py:105` — **live code, deliberately not fixed** | Adopted criterion `recovery >= f × ceiling(k)`; at k=3, `0.4945824` | CLM-012 retired the absolute `0.80` bar on 2026-08-09. Not patched because editing a threshold inside a closure is the prohibited act and the validator already governs — it also causes the **expected exit 3** that makes completed runs read `FAILED` |
| **`0.5126032761517403`** used as *the* D2 recovery | `CLAIMS.md` CLM-010 (vi) and CLM-012; both powered-closure predeclarations | **ALIVE-AS-CITED-ARTIFACT-ONLY.** Keep citing it as job `56552326`'s validated value (finalizer `56562169`, 31/31). Best estimate is the three-run mean **`0.5123048`, sd `0.000820128`** | Not wrong — one of three draws, and the only one with a finalizer behind it. Quoting it as *the* recovery overstates precision; replacing it in the gate would break a validated provenance chain |
| **`recovery >= 0.80`** as Gate-4's D2 criterion | Widely, in pre-08-09 text; `CLM-012`'s own status line records the retirement | `recovery >= f × ceiling`, `f = 0.80`, `ceiling = 0.618228` (per-cell) → `0.4945824` | Retired as a **bug**, not a re-specification: `φ(E[a]) = 0.808415` rounds to `0.80`, i.e. a ceiling computed in the wrong scope. See CLM-012 |
| **`1.09735` / `0.88965` / `0.55811`** quoted as *achieved/required* — and the verdict label **`CORRECT_AT_ITER0_DEGRADES_LATER`** | `VALIDATION_LEDGER.md` §2026-08-09 full-event Step-1 increment trajectory (**now bannered, 2026-08-11**); the committed receipt `nd-unfolding/pet/fullevent_nominal/STEP1_TRAJECTORY.slurm-56525829.json` (old schema, left as written); `FINDING-20260807-step1-under-achieves.md`; `PROMPTS-20260811-four-session-closeout.md` §SESSION C, which hands the numbers to the PET lane in this form | **The end-to-end field** `end_to_end_achieved_over_required`. At iteration 0 it is **`0.9721`** — an UNDERSHOOT of ~2.8%, not an overshoot. Iterations 1-2 end-to-end are **not in the old-schema receipt** and are being measured by job `56691812`. Label → **`RIGHT_SIGN_AT_ITER0_INVERTS_LATER`**, retired and renamed 2026-08-10 in `step1_increment_trajectory.py`'s own `verdict_label_history` | The three values are the field the current harness renames `r1_achieved_over_required_FIRST_LEG_ONLY_NOT_LIKE_FOR_LIKE` (`:249`): a first-leg average `mean_w(r1)` divided by an **end-to-end** requirement, omitting a covariance term and step 2's re-estimation (+4.22% and +5.85% on the annealed arm). BEN-077's class, and it **inflates the apparent shortfall**. `'CORRECT'` overstated a correction that undershoots. **The SIGN survives; the magnitudes do not.** Note the shape: the harness was fixed and RENAMED THE FIELD, while the ledger row copied from the old artifact kept the old heading — a retraction that propagated into code but not into prose |
| **`~34%` fold-forward deficit** read as a property of the ESTIMATOR rather than of the canonical artifact | `state/p3f-pet-gate4-launch-code-gate-20260810c.json` `gate_state.quotability` (*"branch C STILL GOVERNS: the fold-forward deficit (~34%) is untouched"*) — **live gate receipt, deliberately not edited** | **Still true of the canonical artifact** (`-0.34458`). The annealed artifact `56563761` measures **`-0.03561`**. Nothing to replace *yet* — but the sentence is **falsified the moment a `-3.56%` artifact becomes canonical**, so promotion owes a Gate-4 re-issue, not just a ledger row | Not wrong when written (`2026-08-10T13:20:00Z`, 4 h 40 m BEFORE the annealed nominal's completion marker at `18:00:43Z`). Listed here as a **write-time trap for the promotion commit**, which is what this index is for: the number is correct and its SCOPE decays on an event we are actively considering |

## The 2026-07-12 quarantine — PET class, and one LIVE number

Content supplied by the oversight session; **every location and value below re-verified here by `git grep`
before writing**, per the rule that a relayed claim carries the relay's confidence and not its evidence. Its
grep reproduced exactly. The quarantine names **object classes**, not values — *"the old 4D/5D/FPS
unified-throw adoptions, PET statistical/total budgets and precision comparisons, `(E_avail,W)` covariance, and
every significance derived from those objects are **SUPERSEDED AND UNQUOTABLE**"* (`VALIDATION_LEDGER.md:20-30`)
— so its rows have to be derived per class rather than looked up.

### The marking is inverted: the three macros nobody uses are marked; the two consumed in prose are not

| macro (`docs/analysis-note/values.tex`) | value | marked `QUARANTINED`? | consumed in note prose? |
|---|---|---|---|
| `\petTotalMedian` :69 | 15.10 | **yes** | no |
| `\petTotalTrace` :70 | 3.878e-38 | **yes** | no |
| `\petFourMedian` :71 | 12.37 | **yes** | no |
| `\petRetrainMedian` :72 | 4.18 | no | no |
| `\petLateralMedian` :73 | 2.11 | no | no |
| `\petGbdtGap` :68 | 9 | **no** | **yes — `sec_pet.tex:45`** |
| `\petRatio` :66 | **0.912** | **no** | **yes — `sec_pet.tex:42` and `:59`** |

**Protection is applied to the harmless cases and absent from the live ones.** The marker was the failure here,
not the number — the same shape as the `VALIDATION_LEDGER` section above, one level apart.

### `\petRatio` = 0.912 — three independent reasons, SPLIT BY DISPOSITION

**Do not action these as one item.** They have different dispositions, and bundled as *"three reasons to doubt
0.912"* the factual one inherits the latency of the two judgement calls. *Split at the oversight session's
request, which is correct.*

| reason | kind | disposition | blocked on |
|---|---|---|---|
| **`niter` mismatch** | **FACTUAL — no adjudication** | Re-run at `niter=3`, **or** label the quoted values explicitly as `niter=2` legacy | **nobody.** It is already true |
| **J21** background subtraction / unit measured weights | needs a **decision** | Qualify as a non-background-subtracted historical diagnostic, or re-extract on the `bkgsub` input | whoever decides what the PET central value is |
| **quarantine coverage** | needs an **owner's ruling** | In or out of the 2026-07-12 class | whoever owns the quarantine |

The factual row can be actioned today and does not depend on the other two resolving.

1. **J21** (`AUDIT-FINDINGS-20260731.md:800-804`): *"The quoted 4D ratio has unit measured weights and no
   background subtraction"*, and the prescription is *"either qualify the 0.912 as a non-background-subtracted
   historical diagnostic, or re-extract on the `bkgsub` input."* Same file at `:366-370` adds the **direction**:
   at the note's ~3% background scale, leaving background in biases PET **high**, so the gap behind the ratio is
   *larger* than 8.8%, and explicitly *"not a quotable number."*
2. **`niter`.** `sec_pet.tex:47` discloses that *"The PET run used a 2M-event, two-iteration training."* The
   campaign's pinned policy is `niter = 3` (CLM-010, CLM-012, FROZEN). `STEP2-20260806-niter3-budget-classification.md:89`
   flags exactly this: *"If full-event PET moves to `niter=3`, `\petRatio` (0.912, used at `sec_pet.tex:42,59`)
   and `\petClosure` change."* **It moved.** This is the strongest of the three because it is mechanical rather
   than judgemental.
3. **Estimator change.** J21 notes the interaction: *"pre-08-01 PET numbers are a different estimator"* — the
   full-event schema landed 2026-08-01 and the loader now reads the whole event, so a pre-08-01 PET total is not
   the same quantity.

**It is internally consistent, which is worth stating so nobody looks for the wrong defect.** Applying the
receipt-ingredients heuristic: `sec_pet.tex:41-42` quotes PET `2.796e-38` against GBDT `3.066e-38`, and
`2.796/3.066 = 0.91194`, which rounds to the quoted `0.912`. **So this is not a mislabel or an arithmetic slip —
it is a correctly computed ratio of operands that have since gone stale.** A different failure mode from every
other row in this index, and the one a consistency check cannot catch.

**A separate defect found while checking that: the operands are not macros.** `2.796e-38` and `3.066e-38` appear
**only as inline `\SI{}` literals** at `sec_pet.tex:41-42` — they are not in `values.tex`. So the ratio has a
macro and therefore *looks* managed, while **its inputs sit outside the marking convention entirely and cannot
be quarantined even in principle.** Marking `\petRatio` would not reach them.

**What I am NOT claiming, and the oversight session was right to hedge it:** that the quarantine *formally*
covers `\petRatio`. It is a PET precision comparison by description, and `sec_pet.tex:42` compares against a
GBDT total, so the PET side plausibly derives from a quarantined budget — but I did not source a statement
saying so, and inferring coverage from a class description is not sourcing. **Whoever owns the quarantine
adjudicates.** The three reasons above are independent of that question, so the decision is needed regardless,
**before the note freezes.**

### Still not indexed from this quarantine

The `(E_avail,W)` covariance rows, the 4D/5D/FPS unified-throw adoptions, and *"every significance derived from
those objects"* are **not indexed** — same reason as before, that would be listing from a description rather
than a search. Open, and explicitly so.

## Not included, and why — the honesty column

- **The 2026-07-12 quarantine is now PARTIALLY indexed** — corrected 2026-08-11, because an earlier version of
  this column said it was *"not indexed"* after `6dff2fa` had already indexed part of it. **A file whose value
  is a trustworthy self-description cannot be wrong about itself**, even in the safe direction of understating
  coverage. **Indexed:** the PET macro class (`\petRatio`, `\petGbdtGap`, and the marking inversion) and the
  `\gbdtFive*` class. **Still NOT indexed:** the `(E_avail,W)` covariance rows, the 4D/5D/FPS unified-throw
  adoptions, and *"every significance derived from those objects"* — I have not sourced those and will not list
  them from a description.
- **Commit messages are immutable and are not fixable.** `7b2198a`, `b1414df` and `98d502d` carry retracted
  figures in their bodies and will forever. They are indexed above so a reader following `git log` finds the
  correction; they are not errors to be repaired.
- **Superseded values inside `PREDECLARATION-*` documents are deliberately left as written.** A predeclaration
  records what was fixed *in advance*; editing its body to match the outcome would destroy the only property
  that makes it worth anything. Each carries a §RESULT section stating what happened instead.

## The generalisation, which is why this file is worth more than its rows

**A retraction that does not say where the corpse is leaves the reader to find it by accident.** Every row's
load-bearing column is *"where it still appears"* — not the correction, which was already recorded at the time
in every case. The corrections existed; the map to the stale copies did not, and the map is what a fresh reader
needs. Same argument as leaving a struck-through headline rather than deleting an entry.
