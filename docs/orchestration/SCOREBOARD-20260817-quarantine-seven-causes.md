# SCOREBOARD 2026-08-17 — the seven quarantine causes, all four legs, candidate vs quoted product

> ## The one thing to take from this board
>
> **THE QUOTED COLUMN CANNOT MOVE BY REMEDIATION.** `receipt_candidate_stamps_5d.json` runs both July
> products as **negative controls, named by the macro each feeds**, and every named stamp comes back
> **`ABSENT`** — 4 keys where the candidate arms carry 13. X predates the stamping, so
> **"X gets replaced, not repaired."** That is a structural fact about the deliverable, not a grading
> opinion. A reader who takes one line from this board should take that one and not *"1 of 7"*.
> Promoted to the top on the mediator's instruction; detail in §1.

**Written by lane C (PET) on the mediator's dispatch** (`HANDOFF-20260817-1133Z.md` §"The four dispatches"
item 4). **Nothing here adopts anything, discharges anything, or lifts the 2026-07-12 quarantine.**
`docs/analysis-note/` untouched; `values.tex` untouched.

**Why it was commissioned, in the mediator's words:** it has *"reported GBDT to Joseph cause-by-cause as
lanes finished and has never seen the whole board at once — so the board's value is precisely in the cells
that turn out weaker than the running narrative implied."* Graded on that instruction. **A cell whose only
evidence is a lane saying so is `OPEN`, including where the lane was the mediator, and including where it
was me.**

**Legs** per `CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md` §0: **C** code, **P** provenance
(*"prove the artifact under test is the artifact you loaded"*, BEN-083), **M** magnitude *measured on the
artifact's own inputs*, **T** test *power-tested in both directions*. **All four must hold; any one
failing leaves the cause OPEN.** `UNRESOLVED` is a permitted per-leg verdict and must not be re-read as
the nearer of PASS/FAIL.

**Discharge is a property of a (cause × artifact) pair** — §0. So every cell below names its artifact.

| col | artifact |
|---|---|
| **CAND** | the footing-matched, stamp-verified candidate: `uq_5d/readopt_20260811_footing/stamped_bkgaware_meancentered_20260812.root` (`4f168e83…`), CV arm `dbcd5359…`, job `56720356` |
| **QUOTED** | what `values.tex:57-60` actually quotes — the July products behind `\gbdtFiveAdoptTrace` `5.81e-38` and `\gbdtFiveCVTrace` `6.24e-38` |

---

## The board

| # | cause | leg | **CAND** | **QUOTED** |
|---|---|---|---|---|
| **1** | one-sided endpoint interpolation | C | **MET** — `Cause1PathAuditTests`, `nd-unfolding/tests/test_uq_remediation.py` | **MET** — same audited path |
| | | P | **MET** — stamps (`receipt_candidate_stamps_5d.json`, S1) **plus** census (`receipt_cause1_endpoint_census_5d.json`, C1) | **OPEN** — every named stamp `ABSENT` |
| | | M | **MEASURED, not MET** — `receipt_cause1_endpoint_census_5d.json` | **MEASURED** (on X's own bank) |
| | | T | **MET** — N1/N2, re-verified M1/M2 | **MET** |
| **2** | CV centering | C | **MET** | **MET** |
| | | P | **MET** — job `56720356`, path+sha256 | **OPEN** — stamps `ABSENT` |
| | | M | **MET** — `5.3478×` floor (corrected from `4.83×`, BEN-109) | **OPEN** |
| | | T | **MET** — `f7_cv_centered_required`, N3/N4 | **MET** |
| **3** | varying estimator seeds | C | **PARTIAL — scoped; INAPPLICABLE to the dominant block** | **PARTIAL — same scope** |
| | | P | **WITHDRAWN from MET → PARTIAL — see §2d** | **OPEN** — stamps `ABSENT` |
| | | M | **OPEN and NOT CURRENTLY MEASURABLE — see §2 and §2b** | **OPEN, same** |
| | | T | **MET** — N5, re-derived | **MET** |
| **4** | scalar jitter subtraction | C | **MET** | **MET** |
| | | P | **MET** — `receipt_candidate_stamps_5d.json`, S1 | **OPEN** — stamps `ABSENT` |
| | | M | **OPEN — reason corrected today; see §3** | **OPEN** |
| | | T | **MET** — N6 (caught a defect nothing else did), N7 | **MET** |
| **5** | frozen PET weights | all | **N/A — and undeclared; see §4** | **N/A — undeclared** |
| **6** | incomplete statistical projection | C | **PARTIAL** — BEN-110 detects all-zero rows; ensemble leg + corrected upstream input untouched | **PARTIAL** |
| | | P | **OPEN** — no product rebuilt at all | **OPEN** |
| | | M | **OPEN** | **OPEN** |
| | | T | **MET** — coverage guard, P1/P2 | **MET** |
| **7** | CV-support-limited lateral selection | all | **OPEN — discharged for a THIRD artifact; see §5** | **OPEN** |

### Counts

| artifact | causes with four METs | discharged by decision |
|---|---|---|
| **CAND** | **0** — causes 1 and 2 reach four METs *on the letter of §0*, both **ROUTED not declared**; cause 1's `M` is MEASURED-not-accepted | **1 of 7** (cause 2, Joseph, 2026-08-12, candidate only) |
| **QUOTED** | **0** | **0 of 7** |

**`1 of 7` and `0 of 7` both reproduce.** Neither is *"one down, six to go"* on the other's artifact.

---

## 1. The single fact that sets the entire QUOTED column, and it is measured at HEAD

Every `P` cell in the QUOTED column is `OPEN` for one reason, and it is not inherited from 2026-08-11
prose. `nd-unfolding/uq_5d/receipt_candidate_stamps_5d.json` runs the two July products as **negative
controls** and names them by the macro each feeds:

```
X_july_meancentered_negative_control   -> feeds \gbdtFiveAdoptTrace 5.81e-38   -> every named stamp ABSENT
X_july_cvcentered_negative_control     -> feeds \gbdtFiveCVTrace    6.24e-38   -> every named stamp ABSENT
```

4 keys found where the candidate arms carry 13. **So the QUOTED column cannot move by remediation.** The
ledger states the consequence and it is worth repeating because it is the most load-bearing sentence on
this board: **X predates the stamping — "X gets replaced, not repaired."**

## 2. Cause 3's `M` is graded two different ways inside one document, so it is not MET

`CRITERIA-20260811` §2 splits `M` into **M(i)** the fixed-seed null — measured, `1.9706e-50` pre-J28 /
`5.8223e-50` J28 — and **M(ii)** *"the magnitude of what varying seeds would have contributed"*, which §2
itself says *"is what the criterion is about"* and flags **UNRESOLVED**. **§3's table grades `M` MET,
citing only M(i).**

`MAP-20260817-gbdt-note-section-blockers.md` §2 inherited §3's grade and records cause 3 as *"OPEN —
provenance only."* **That is the drift this board was commissioned to find:** with `P` now MET for the
candidate, "provenance only" reads as *nothing left*, when M(ii) is untouched.

**And the judgement I was about to record as untaken HAS been taken — I had this cell stale in my own
first draft.** `DETERMINATION-20260817-causes-3-4` §5 left it as *"does `\gbdtAiEstTrace` serve as M(ii)?
— a decision, not a lookup."* **Lane B answered it the same day** in
[`FOOTING-20260817-gbdtaiesttrace-12-seeds.md`](FOOTING-20260817-gbdtaiesttrace-12-seeds.md), and the
answer is **no, on footing**:

| | the candidate | `\gbdtAiEstTrace` (AI1) |
|---|---|---|
| date | post-J28 | **2026-07-14 — seventeen days BEFORE J28 was found** |
| input | the bkgaware universe sweep | **`of_inputs_5d.npz`, one fixed data/MC draw** |
| construction | systematic covariance over the universe sweep | 12 varied estimator seeds, **no flux universes at all** |
| re-rolled since? | — | **NO** |

**So it is not the same quantity, and cause 3 discharges on three legs and needs its own measurement** —
costed at **~1 GPU-node-hour**. **Graded `OPEN`, both columns.** That is a *different* cell state from
`UNRESOLVED`: unresolved says nobody has decided, open-and-costed says the decision is made and the work
is small and unstarted.

**A bar for that measurement is proposed and awaiting a second lane** —
[`PROPOSAL-20260817-mii-bar-for-cause-3.md`](PROPOSAL-20260817-mii-bar-for-cause-3.md), σ inflation ≤ 0.5%
primary with `sd(block_sum)/block_sum ≤ 0.10` as its consequence, six rejected alternatives given. Under
Joseph's 2026-08-17 rule that **two agreeing sessions authorize a run**, this is one confirm away from
being runnable, and it is the cheapest open cell on the board.

**How I caught my own stale cell, because it is the argument for the rule that caught it:** I found the
`FOOTING` document while adding this board's pointer row to `CATALOG.md` — the very step the pre-commit
hook refused to let me skip. **The index requirement surfaced a correction to the document being
indexed.** That is a stronger argument for the rule than the one the hook gives.

**AND THE "COSTED" HALF OF MY OWN CELL WAS ALSO WRONG — corrected 2026-08-17.** I wrote *"`OPEN` — costed
at ~1 GPU-node-hour … the cheapest open cell on the board."* **Wrong twice.** That figure prices **AI1's
footing** — `of_inputs_5d.npz`, fixed-data-seed 0, no flux universes — which is precisely the footing
`FOOTING-20260817` **disqualified**. The measured unit on the candidate footing is **28.50 A100-h per
re-seed**, ~28.5×. And "costed" implies configurable, which §2b shows it is not. **So the cell is not
cheap and not runnable, and I had it as both.** I took the figure from a `CATALOG` row rather than from a
measurement, which is the thing this board grades other cells down for.

## 2b. Cause 3's `C` leg is scoped, and `M(ii)` is not currently MEASURABLE on either leg

**`C` corrected from MET to PARTIAL.** I graded it MET both columns off `CRITERIA` §2's citation
(`unified_throw_cov.py:330-331, 370-371` — `do_combine` rejects mixed-seed slabs). Lane B established that
the guard's coverage **excludes the dominant block**:
[`FINDING-20260817-cause3-C-leg-does-not-cover-the-dominant-block.md`](FINDING-20260817-cause3-C-leg-does-not-cover-the-dominant-block.md)
— *"the dominant block's products are not in the guard's population at all, and there is no seed provenance
anywhere on that path to be present or absent."* Nothing stamps the sweep seed into its products, and
`analyze_universes_5d.py` has **zero** occurrences of `seed`. **So the single-seed property of the dominant
block holds by hardcoding and is checked by nothing** — it would not be noticed if it stopped holding.
`MET` for the throw/block units, **inapplicable** to `C_syst`. Graded `PARTIAL`.

**And `M(ii)` cannot be configured on either leg. Both verified from the tree, not from relay:**

| leg | seed | why `M(ii)` cannot be run |
|---|---|---|
| per-**universe** (`C_syst`, 169 universes — the dominant block) | **`42`** | `sweep_bank_5d.py:252` carries it as a **literal**; the module has **14** `add_argument` calls and **none for seed**. Unreachable, and unstamped, so a scan could not even prove which seed a product used. |
| per-**throw** (throw/CV/ML blocks) | **`1000`** | `unified_throw_cov.py:525` has **exactly one** `--seed`, and `:223` does `rng = np.random.default_rng(args.seed + gj)` to draw **which band shifts** — one flag, two roles. Varying it moves the **draw**, so *"estimator seed varied with the draw held fixed"* is **unsatisfiable**. |

**Consequence for the board's own language:** cause 3's `M` is **not** *"unmeasured pending a cost
decision."* It is **blocked on two code changes** — lane B's specified stamping repair for the sweep, and a
seed/draw separation in the throw path — **and only after those is it a cost question.** Joseph's cost
decision is **downstream** of that, not parallel to it. **Pricing a run that cannot be configured is what
produced both wrong figures on this cell**, mine (~1 GPU-node-hour, wrong footing) and the 28.50 A100-h
one (right footing, unsatisfiable condition).

## 2c. `M(ii)`'s referent — PROPOSAL, awaiting a second or a dissent

The mediator asked: **which leg's seed does `M(ii)` mean?** My answer has two parts and the second is the
one I think is actually open.

**Part 1 — "which leg" is already answered, and not by me.** `VL141` records it as consequence (b):
**`M(ii)` must vary BOTH seeds.** That is not a fresh choice — it is grounded in the criterion's own defect
statement, which says *"per-throw **or** per-universe unfolds drawn with different estimator seeds."* Both
ensembles are named in the defect, so a magnitude covering only one measures only part of it. **I am not
re-deciding this; I am pointing at it**, and `VL141` also states the reason it needed its own row: *"a
false quotable claim about the candidate, independent of cause 3."*

**Part 2 — the real gap, and it is a SPECIFICATION GAP rather than an ambiguity.** `CRITERIA` §2 asks for
*"**the** magnitude of what varying seeds would have contributed"* — **singular magnitude, two seeds** — and
it does **not** say whether that is:

* **(A) per-leg and summed** — scan the sweep's seed, scan the throw path's seed, add the two contributions; or
* **(B) jointly on the composite** — vary both together in one scan and take the resulting spread.

**These are different numbers, and choosing between them is a physics decision, not a reading.** (A)
treats the two legs' estimator noises as independent contributions to be added; (B) does not, and would
capture any correlation between them. The covariance sums blocks, so (A) is the construction-shaped answer
and (B) is the ensemble-shaped one. **The criterion is silent, and no amount of careful reading makes it
speak** — which is the test the mediator set for calling something a gap rather than an ambiguity.

**So: recorded as a specification gap that needs a decision, not papered.** And note the ordering it
implies: **the gap is answerable now, on paper, at zero cost**, whereas the *measurement* it governs is
blocked behind two code changes. So answering it does not unblock the run — but leaving it unanswered means
the code changes would be made without knowing what they must enable, and (A) and (B) do not require the
same instrumentation. **(A) needs each leg's seed independently variable. (B) needs both variable in one
process.** That is a real difference in what lane B's stamping repair has to support.

**My recommendation, offered for second-or-dissent and not taken:** **(A), per-leg and summed**, on the
ground that `CRITERIA` §0 defines `M` as *"measured on X's own inputs"* and X is constructed as a **sum of
blocks** — so a per-block magnitude is the one that composes the way the artifact does, and it is also the
only one that can be reported per leg when one leg's instrumentation lands before the other's. **If the
mediator or Assistant dissents toward (B), the dissent should say what correlation between the two legs'
estimator noise it expects to be non-negligible**, because that is the only thing (B) buys over (A).

**The two code changes §2b names are better-precedented than I said.** Verified: `bootstrap_nd.py:19,21`
and `seedscan_split.py:36` **already carry `--estimator-seed` alongside `--fixed-data-seed`**, with
`:25` stating the split in its own help text — *"`--seed` varies data+MC, `--estimator-seed` fixed."*
**So the two-role separation is an existing pattern in this repo, not a new design**, and only
`sweep_bank_5d.py` and `unified_throw_cov.py` lack it. That makes gate 1 smaller than "two code changes"
sounds — and it does **not** make it cheap, because those two modules are where the cost lives.

**And the cost figure now has two unreconciled values.** B measures **0.44 node-h** for the stat estimator
axis against `FOOTING-20260817:66-69`'s **~1 GPU-node-h** — the very figure I quoted this morning as *"the
cheapest open cell."* B says its own is the conservative one and **did not reconcile them.** So the cell I
first priced at ~1 GPU-node-hour on the wrong footing now has, on the *right* footing, **two independent
values disagreeing by ~2× with neither reconciled.** Recorded rather than averaged.

## 2d. Cause 3's `P` leg: WITHDRAWN from MET, and I had the disconfirming evidence on screen

**This withdraws a `MET` I published on this board this morning.** Lane B measured it and filed a pointer
**without grading**, correctly, because `BEN-381` bars the lane that measured a leg from grading it. So the
grade is mine. **I verified every code claim from the tree before regrading**, and I am grading on
`CRITERIA` §2's **own two clauses** rather than on B's one-line recommendation — which makes my grade
slightly *harsher* than B's.

§2's `P` for cause 3 asks for two things:

> *"X's receipt records **the single seed value**, and `fixed_seed_null_norm` is **PRESENT** in X and ≤ tol."*

| clause | grade | evidence, verified at HEAD |
|---|---|---|
| (ii) `fixed_seed_null_norm` PRESENT and ≤ tol | **MET** | written at `unified_throw_cov.py:491`; candidate carries `upstream_fixed_seed_null_norm = 5.8223488501140625e-50` against tol `1e-12` |
| (i) the receipt records **the seed value** | **NOT MET — on any leg** | `--out-root` writes six `TParameter`s (`:479-492`): `sqrt_tr_unified`, `sqrt_tr_block`, `joint_mean_shift_norm`, `fixed_seed_null_checked`, `fixed_seed_null_norm`, `n_throws`. **None is a seed.** The candidate's 13 keys contain no seed key either. |

**So `P` is `PARTIAL`, and the reason is stronger than "scoped".** B recommended *"PARTIAL — MET for
uthrow, ABSENT for `combined_source`."* I grade it **PARTIAL with clause (i) failing on *both* legs**,
because no product anywhere records a seed *value* — not the uthrow arm either. The scoping is a second,
independent problem on top:

* the census reads **`.npz` slabs** via `np.load` (`:326-332`, `if "seed" in z.files`), so
  `combined_source`'s **188 ROOT universes are not in its population at all**;
* `analyze_universes_5d.py`, **which writes `combined_source` itself**, contains `seed` **zero** times and
  writes no `TParameter`;
* `sweep_bank_5d.py` contains `seed` **exactly once** — `:252`, the hardcoded `42`.

**So the dominant block's single-seed property holds by hardcoding and is recorded nowhere and checked by
nothing**, and `BEN-106`'s stamp-propagation fix — the thing three causes were said to be waiting on —
**has nothing to propagate.**

**NO NUMBER MOVES.** Every leg is internally single-seeded, so nothing is mis-computed. What fails is a
**verification claim** (B's phrasing, and it is exact). `BEN-246`.

**The consequence for this row, which is the point of the board:** on the **candidate**, cause 3 now has
**exactly one unqualified MET leg — `T`.** `C` is PARTIAL (§2b), `P` is PARTIAL (here), and `M` is OPEN and
not currently measurable, with its M(i) half being the one `CRITERIA` §2 says *is not what the criterion is
about*. **This morning I shipped that row as "P MET, provenance done."** It was the row I was most confident
about and it is now the weakest of the five.

**And I should not have been confident.** I printed the candidate's 13 keys **in this session**, read them,
and graded `P` MET anyway — the list has no seed key in it, and clause (i) asks for exactly that. **The
disconfirming evidence was on my own screen.** Same shape as the array-stall near-miss I filed this morning:
holding the number that refutes you and not applying it. The difference is that one I caught before
publishing.

## 3. Cause 4: the REASON the `M` cell was unreachable is false, and the cell still does not move

`CRITERIA-20260811` §2 grounds cause 4's `M` on *"no committed document records which scalar or how it was
estimated"*, so that constructing one now would be *"the success condition invented after the fact."*
**That reason is false as written, and I verified the correction from the commits rather than from the
retraction that reported it:**

* **`a0cdc01`** (2026-06-08) **added the full specification with its derivation in the comment** —
  `nd-unfolding/unified_throw_cov.py`: *"With two CV unfolds at different seeds,
  `E||x_cv2 - x_cv1||^2 = 2*sum_bin sigma_jit^2` … the jitter-free systematic trace is
  `tr(C_uni) - ||Dcv||^2`"*, implemented as `jit_trace = float(np.sum((x_cv2 - base) ** 2))` from a second
  CV unfold at `args.seed + 7`, gated on `--null`, subtracted as `max(tr_uni - jit_trace, 0.0)`.
* **`07c18ae`** (2026-07-14) **removed it by editing the file in place.**
* `jit_trace` occurs **0** times at HEAD.

**There was never a literal scalar** — it was computed at runtime — which is why every value-shaped search
for one returned empty.

**The cell stays `OPEN` and I am declining to move it in either direction.** What an artifact establishes
right now is: the specification **exists and is recoverable at `a0cdc01`**; the machinery is **absent at
HEAD**; **re-runnability is unmeasured** and nobody claims `M` is MET. **What changes is the remediation
path, not the grade** — and that is the useful part:

> `M` for cause 4 was recorded as **permanently inapplicable** (no surviving counterfactual). It is
> actually **measurable-but-unmeasured**, pending re-runnability. Those have different costs and different
> owners, and the board carried the first for six days.

**How the false reason survived, because it bears on how every other cell should be read:** the search that
established it was `git log -S'jitter' --diff-filter=D --all -- '*.py'`, which returned zero.
**`--diff-filter=D` matches only commits that DELETE A FILE**, and cause 4's method was retired by an
in-place edit — the normal way. Same query without the restriction: 71 commits. **The restriction produced
the answer, not the history.** This is `BEN-235`'s class exactly (a search structurally incapable of
finding what its silence was taken to deny), and it is the second instance in this campaign in three days.
The corroboration offered alongside it was **one sentence cited twice** — `DETERMINATION:190` quotes
`CRITERIA:171` verbatim — presented as two independent documents.

## 4. Cause 5 is mine, and it is the weakest-evidenced row on this board

**It has two different names in two live documents.** `VALIDATION_LEDGER` VL66 calls it **"frozen PET
weights"**, scoped *"OPEN for the recoil-PET budget"*. `MAP-20260817` §2 calls it **"the binding half"** and
explicitly declines to re-derive or summarise it. Those are not obviously the same object, and no document
reconciles them.

**Its binding half is established, by my own lane, from the artifact:**
`DETERMINATION-20260811-cause5-binding-half.md` — *"the JOINT NUISANCE-RETRAINING CONSTRUCTION is binding.
The selection-complete detector samples already exist, are Gate-3 promoted, and have been since
2026-07-20."* The distinction it turns on is that inputs and products are different objects: the
full-event PET estimator's **products** do not exist; the selection-shifted detector **samples** do, and
they are the more expensive object.

**But for X — the 5D GBDT covariance — cause 5's applicability has never been written down by anyone.** X
is a GBDT covariance; frozen PET weights are a PET-estimator construct; VL66 scopes the cause to a
different artifact entirely. **So I grade it `N/A — and undeclared`, not `N/A`.** §0's rule is per
(cause × artifact), and the X-side statement does not exist. Asserting `N/A` would be me doing on my own
cause exactly what §4.1 caught in the tally: reading a true statement about one artifact as settled for
another.

**What would close it:** one sentence in the ledger stating whether cause 5 is on X's construction path.
Cheap, and it is mine to propose rather than to write into another lane's row.

## 5. Cause 7 needs a third column, which is a finding about the board's shape

Cause 7 is **DISCHARGED 2026-08-07 for the FPS covariance** — `…_activelat.root`, **266** reported bins,
job `56431823`. **X is 10,694 of 65,856.** `266 ≠ 10,694`; different objects, different grids
(`CRITERIA` §4.1). So cause 7's only discharge is against an artifact that appears in **neither** column of
this board.

**And its X-side state changed materially on 2026-08-16, after `CRITERIA` was written.** §4.1 grounded X's
zero-of-seven partly on the lateral replacement *"not existing"*. It now exists: `std_final5_candidate.root`,
rewritten by the authorized stages-4-6 run `57128458` (rc 0), covariance content bit-identical
(`f26b3bfe…` 5D, `c1fe11b1…` 4D). **But it carries `publication_gate_rejects_this: true` and
`p4_adopt_standard.py` refuses it outright.**

**So the state change is `does not exist` → `exists, non-adoptable`.** That is progress on the path and
**not** a discharge, and stating it as one would be precisely the tally error §4.1 was written about.
I note independently, having verified this flag's semantics on 2026-08-14 for a different purpose, that
`publication_gate_rejects_this` is not a label but an **assertion**: `fps_build_control_manifest.py:202-204`
*dies* if the publication gate fails to reject the manifest. It is a fail-closed statement about the class.

## 6. Two citation defects found while grading, both the same shape

1. **`VALIDATION_LEDGER.md:65-88`** — the citation `CRITERIA-20260811`'s own header uses for *"the seven
   construction causes"* — **no longer resolves.** Those lines now carry Gate-6 trajectory rows; the cause
   list is at roughly `:690-733`. The ledger is append-only, so any line-number citation into it decays.
2. **`(§4.8)`** in cause 1's `C` cell **does not resolve** — §4 runs 4.1–4.7. Lane E already caught this;
   the audit is real and lives in `Cause1PathAuditTests`.

**Both are `CRITERIA` §4.4's own finding** — *"the only predeclared discharge criterion any of these five
causes has is cited by a line number that no longer contains it"* — **recurring inside and around the
document that filed it, now three times.** The remedy is the one this repo already uses elsewhere: cite a
committed test, a receipt key, or a commit, never a line number in a growing file.

## 7. What this board does NOT do

- It **discharges nothing** and **lifts nothing**. Causes 1 and 2 reach four METs on the letter of §0 for
  the candidate; both are **ROUTED, not declared**, and I am not the decider for either.
- It **does not take the two `M` judgements** that `DETERMINATION-20260817-causes-3-4` routed (cause 3's
  M(ii); cause 4's bound-vs-inapplicable), nor the one `DETERMINATION-20260817-cause1` routed (does a
  `+3.1%`/`+5.9%` √Tr difference with a `1.7–2.0×` median per-band ratio constitute `M` MET under §0's
  *"measured, not necessarily small"* rule).
- It **does not touch** `values.tex`, `docs/analysis-note/`, any receipt-bound launcher, or
  `gate6traj-reconcile-56847059`. No `scancel`, no `scontrol`, no run submitted, no compute spent.
- It **does not re-derive** cause 5's determination beyond reading it, and does not assert cause 5's
  X-side applicability — see §4.

## 8. The one structural recommendation

**Every future cause-state report should carry the artifact in the same row as the state.** The ledger
already did this on 2026-08-11 (VL62–VL68) and it is the single change that stops the tally being
misread. This board's contribution is to extend it one step: **the artifact belongs in the same row as
each *leg*, not just each cause** — because cause 1 currently has `M` measured on X's own bank while `P`
holds only for the candidate, and a per-cause artifact column cannot express that.
