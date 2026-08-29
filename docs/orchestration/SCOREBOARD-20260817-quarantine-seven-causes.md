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

> ### ⚠ THIS BOARD USES TWO GRADES ITS OWN CRITERIA DO NOT DEFINE. Read this before reading a cell.
>
> `CRITERIA` §3:246 defines the whole vocabulary: **"Legs are graded MET / OPEN / UNRESOLVED. A cause is
> discharged only with four METs."** This board also uses **`PARTIAL`** and reports lane B's
> **`INAPPLICABLE`**. **Neither is in that vocabulary** — `INAPPLICABLE` is defined **zero** times in
> `CRITERIA`, and `PARTIAL` occurs four times there without ever being defined either.
>
> **They are kept rather than collapsed, deliberately.** Cause 3's `P` genuinely is **MET on one clause and
> ABSENT on the other** (§2d); flattening that to `OPEN` would destroy information the grading worked to
> produce. But **a board using a grade its criteria do not define must say so on its face, or it inherits an
> authority it has not got.** So: **wherever this board reads `PARTIAL`, read "extra-vocabulary — see §7b",
> and do not treat it as a fourth defined grade.**
>
> **RULED 2026-08-17, and deliberately the UNFAVOURABLE reading** — mediator and lane C agreeing, which
> settles it under Joseph's rule: **§3 as written is OPERATIVE.** A leg graded `INAPPLICABLE` is none of the
> three, so **a cause carrying one CANNOT discharge**, however sound the reasoning for its inapplicability.
> The conservative reading is also the **status quo**, so adopting it costs nothing and changes nothing —
> whereas admitting a fourth grade would retroactively make discharge **easier** for causes already graded
> under the three. **Nothing waits on this**, and the definition question is left open on purpose: resolving
> a specification gap in the favourable direction, at the end of a day whose whole record is of numbers
> drifting toward more-favourable-until-checked, would be the wrong reason at the wrong time. See §7b.

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
| | | P-i | value not RECORDED anywhere — **PARTIAL**, remedy = add a stamp (§2d) | **OPEN** |
| | | P-ii | value CANNOT be recorded on the dominant arm — **OPEN**, remedy = a new write site; **survives P-i's fix** (§2d) | **OPEN** |
| | | M | **OPEN and NOT CURRENTLY MEASURABLE — see §2 and §2b** | **OPEN, same** |
| | | T | **MET** — N5, re-derived | **MET** |
| **4** | scalar jitter subtraction | C | **MET** | **MET** |
| | | P | **MET** — `receipt_candidate_stamps_5d.json`, S1 | **OPEN** — stamps `ABSENT` |
| | | M | **OPEN — reason corrected today; see §3** | **OPEN** |
| | | T | **MET** — N6 (caught a defect nothing else did), N7 | **MET** |
| **5** | frozen PET weights | all | **N/A ON ITS MERITS** — established 2026-08-17, declaration **LANDED** in `VL66` at `d1c5f90` (§4) | **N/A, same** |
| **6** | incomplete statistical projection | C | **PARTIAL** — BEN-110 detects all-zero rows; ensemble leg + corrected upstream input untouched | **PARTIAL** |
| | | P | **OPEN** — no product rebuilt at all | **OPEN** |
| | | M | **OPEN** | **OPEN** |
| | | T | **MET** — coverage guard, P1/P2 | **MET** |
| **7** | CV-support-limited lateral selection | all | **OPEN — discharged for a THIRD artifact; see §5** | **OPEN** |

> **POINTER 4, added 2026-08-30 by the stale blocker sweep lane — three cells above are measured
> differently at HEAD `32e403b8`, and NONE of them is regraded here.** `BEN-381`: this lane measured
> them, so the regrade is not its to make. Row text left as written.
>
> 1. **Cause 3 `P-ii`'s PREMISE IS FALSE at HEAD.** *"`sweep_bank_5d.py` and `analyze_universes_5d.py`
>    have nowhere to put one"* — both have write sites now: `sweep_bank_5d.py:309-311` and
>    `analyze_universes_5d.py:273-278`, plus `unified_throw_cov.py:569-575` and
>    `mii_adopt_unified_5d_stamped.py:168`, wired into the only declared-member adoption path at
>    `sbatch_finalize_5d_bkgaware_gpu.sh:557,563`. Landed `3dd5e66e`/`214acdbb` (08-18),
>    `5afb7947` (08-19), `bd72112b` (08-20). `analyze_universes_5d.py`'s seed-line count is **8**, not
>    zero; `sweep_bank_5d.py`'s is **13**, not one. **`P-i` is unchanged and still NOT MET** — no
>    receipt records a value, and the wrapper's one real execution (`RUNS.tsv:308`, job `57294218`)
>    recorded the keys as ABSENT because its inputs predate the producers. So §2d's *"graded as two, so
>    a fix to one cannot silently discharge the other"* did exactly its job: `P-ii` moved and `P-i` did
>    not.
> 2. **§1's *"THE QUOTED COLUMN CANNOT MOVE BY REMEDIATION"* is sound for causes 2/3/4 and does not
>    extend to cause 1.** Cause 1's `P` criterion is a **bank inventory**, not a stamp, and
>    `receipt_cause1_endpoint_census_5d.json` satisfies it on X's own bank
>    (`inputs.glob = uq_5d/universe_sweep_bkgaware/…`), pinned to X by reproducing eight of X's
>    committed summary numbers. So cause 1's QUOTED `P` cell is `OPEN` for a reason that belongs to
>    other causes.
> 3. **Cause 4's `M`: §3's "measurable-but-unmeasured pending re-runnability" is narrowed, not
>    contradicted.** Measured from committed bytes: the deflation never entered a stored object on X's
>    path — `a0cdc019` writes raw `C_uni`/`C_block`/`C_cross` and the **raw** `sqrt_tr_unified`
>    (`:265`, `:271`), the corrected trace is printed only (`:236-239`), and
>    `adopt_unified_5d.py:89-90` reads only the raw diagonals, with
>    `git log --all -S "sqrt_tr_unified" -- adopt_unified_5d.py` returning **nothing** against a working
>    `C_unified` control. So `M`'s referent for X is a **specification** question, not a recovery or a
>    cost question.
>
> Full measurements, dates, limits and the routed decisions:
> [`FINDING-20260830-quarantine-nocompute-legs-measured.md`](FINDING-20260830-quarantine-nocompute-legs-measured.md)
> (`OI-170`–`OI-173`).

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
[`FOOTING-20260817-gbdtaiesttrace-12-seeds.md`](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/0b329e8ae8482e6334a68faf947fc80ae7265ac9/docs/orchestration/FOOTING-20260817-gbdtaiesttrace-12-seeds.md "evidence/prepublication-2026-08-20-0b329e8a:docs/orchestration/FOOTING-20260817-gbdtaiesttrace-12-seeds.md"), and the
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
[`PROPOSAL-20260817-mii-bar-for-cause-3.md`](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/0b329e8ae8482e6334a68faf947fc80ae7265ac9/docs/orchestration/PROPOSAL-20260817-mii-bar-for-cause-3.md "evidence/prepublication-2026-08-20-0b329e8a:docs/orchestration/PROPOSAL-20260817-mii-bar-for-cause-3.md"), σ inflation ≤ 0.5%
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
`FOOTING-20260817` **disqualified**. And "costed" implies configurable, which §2b shows it is not. **So the
cell is not cheap and not runnable, and I had it as both.**

> **⚠ MY REPLACEMENT FIGURE WAS ALSO WRONG, AND IN A WAY I HAVE A NAMED HABIT OF — corrected 2026-08-17 on
> lane B's measurement.** I wrote *"the measured unit on the candidate footing is **28.50 A100-h per
> re-seed**, ~28.5×."* **Three defects, and only the first is B's:**
>
> 1. **The numerator was stale.** `28.50` → **`39.078 A100-h`** (+37.1%). Its lateral term costed a
>    *truncated* attempt — 5 of 19 universes, job `55891346` — and the completion run `55894759` was
>    missing from the table. Corrected from all 19 measured productions, no extrapolation:
>    `23.840 + 14.2075 + 1.030 = 39.078` over 189 tasks. **B's defect, B's correction, `BEN-247`.**
> 2. **`~28.5×` was CROSS-UNIT — mine.** It divides **A100-hours** by **GPU-node-hours** as though they were
>    the same unit. **A Perlmutter GPU node is 4 A100s**, verified in-repo rather than recalled:
>    `sbatch_boot5d_gpu_interactive.sh:4` requests `--nodes=1 --gpus=4`, and `--gpus-per-node=4` appears in
>    `sbatch_pet_conv_fps_xps2.sh:8` and `sbatch_pet_train_fps_delta.sh:7`. **The same-unit ratio of my own
>    operands was `7.12×`. It was wrong by a factor of 4 before its numerator was ever found to be stale.**
> 3. **And no unit conversion repairs it, because the operands are NON-COMMENSURABLE — also mine.** The
>    numerator is **ONE estimator seed of `C_syst`**; the denominator (~1 GPU-node-hour) is **TWELVE seeds
>    of `C_stat`**. Different block, different member count. **A ratio of "1 seed of one thing" to "12 seeds
>    of another" measures nothing**, whatever units it is expressed in.
>
> **This is my named recurring failure and I should have caught it here.** My own record of it reads: *five
> misreads in one session, all two-conditions-differ; **name both sides before believing a delta.*** I
> quoted a delta without naming either side's unit or member count — in a cell whose entire subject is that
> two figures were priced on incommensurate footings. **The board was grading that exact error in others
> while committing it.**
>
> **THE NUMBER THE CELL ACTUALLY WANTS** — how much dearer the candidate footing is than AI1's — is the
> **per-seed, like-for-like** ratio, and B measured it: **`268×`**. `39.078 A100-h` per `C_syst` seed against
> **`0.1458 A100-h`** per `C_stat` seed (`55919500_1/_2`, `00:08:44` and `00:08:46` on 1 A100). Same unit,
> same operation shape, both measured.
>
> **A COMPOSITE arm — which is what §2b is about, since a composite moves `unified_throw_cov.py`'s seed too
> — is `39.078 A100-hours` PLUS `55.182` CPU task-hours (`2759.1` CPU-core-hours).** The uthrow leg is
> **0 A100-h** and **re-runs in full**, because `:417-419` raises `SystemExit` on a mixed-seed combine, so
> **not one slab is reusable.** **The CPU half is the larger half, and the 24 A100-h grant does not reach
> it.**
>
> **CORRECTED AGAIN 2026-08-17 — and the clause I had here was itself an asymmetric comparison, carried
> verbatim from lane B, who then found and withdrew it.** I had written that `FOOTING`'s ~1 node-hour and
> B's `1.750 A100-h` *"do not agree"* and that **the spread between them IS the unreconciled footing
> disagreement.** **There was never a disagreement to reconcile.** They are **different quantities**:
> `FOOTING`'s is **ALLOCATION** — a 4-GPU node held for a wall-clock interval — and B's is **WORK**, 12 tasks
> × measured per-task GPU time. **A unit-of-account difference, plus a wasted hour.** So the clause asserted
> a delta across two conditions it had not named — *the exact error this cell exists to record*, committed by
> B while correcting my instance of it and by me while carrying it.
>
> **The 12-seed comparison has THREE denominators, and none is `FOOTING`'s ~1 node-h exactly.** All four
> jobs verified by `sacct` — name, state, elapsed, and `gres/gpu=4` — and every ratio re-derived from its
> operands:
>
> | denominator | value | ratio to `39.078 A100-h` |
> |---|---|---|
> | AI1 **as-run allocation**, including a `TIMEOUT` | `1.5122` node-h = `6.049` A100-h | **`6.5×`** |
> | AI1 **clean completing pass + combine** (`55923713` + `55924460`) | `0.4894` node-h = `1.958` A100-h | **`20.0×`** |
> | AI1 **work** (12 × `0.1458`) | `0.4374` node-h = `1.750` A100-h | **`22.3×`** |
>
> `55922613 ai1int TIMEOUT 01:00:20` = `1.0056` node-h is where `FOOTING`'s *"~1"* lands almost exactly —
> **it was pricing a timed-out hour.** And `55923713` is a **lower** bound, because `rg_skip_if_complete`
> means it only finished what the timeout had not.
>
> **Which is why per-seed `268×` is the figure this cell should use: it needs no denominator choice at all.**
> And it is no longer `n=2`. B raised it to **`n=11`** by pooling `boot5dG 55871150`'s 9 replicas — sound
> because `bootstrap_nd.py`'s per-task cost does not depend on **which** seed role varies (same npz, same
> `--iters 5`, same lgbm estimator, same 1-A100 hardware; `--fixed-data-seed` changes only which RNG seeds
> the weight draw):
>
> ```
> ai1est5d  n=2   524-526 s   mean 525.0 s = 0.1458 A100-h
> boot5dG   n=9   505-519 s   mean 509.7 s = 0.1416 A100-h, sd 4.2 s
> POOLED    n=11  505-526 s   mean 512.5 s = 0.1423 A100-h, sd 7.3 s = 1.4%
> ratio: 268x (ai1-only) | 275x (pooled) | 267-279x across the per-task range
> ```
>
> **So `268×` is good to about ±4% and now carries a measured spread instead of none** — my `n=2` caveat is
> answered, and it was answered by raising `n` rather than by dropping the caveat.
>
> **`0.1458` stays the headline, on B's own argument against its own pooling, recorded rather than buried:**
> the two `ai1est5d` tasks are **the two slowest of the eleven** (526 and 524 s against a `boot5dG` maximum
> of 519), which under random assignment is `1/C(11,2)` = **1.8%**. Suggestive of a small real systematic in
> the `--fixed-data-seed` path — or in the node/day — but it is a **post-hoc test on a noticed pattern at
> `n=2`, so not a finding.** Its practical effect is that **pooling would UNDERSTATE the fixed-draw cost**,
> so `0.1458` is both the conservative choice and the exact operation, with the pooled set serving as
> **spread evidence rather than as the estimate**. That is the right way round.
>
> **THE CLASS FIRED THREE TIMES TODAY AND ONCE ON EACH OF US, WHICH IS THE ACTUAL FINDING HERE.** My
> `~28.5×`; B withdrawing a correct CPU/GPU claim on evidence from an abandoned path; B's allocation-vs-work
> comparison above. **So "the board grading the error while committing it" is not a lane-specific failure —
> it is a property of comparing numbers that arrive from different runs**, and the remedy is structural:
> **name both sides' unit and member count in the same breath as the ratio, or do not state the ratio.**
> Per-seed `268×` satisfies that; every 12-seed figure requires its denominator named. I took the figure from a `CATALOG` row rather than from a
measurement, which is the thing this board grades other cells down for.

## 2b. Cause 3's `C` leg is scoped, and `M(ii)` is not currently MEASURABLE on either leg

**`C` corrected from MET to PARTIAL.** I graded it MET both columns off `CRITERIA` §2's citation
(`unified_throw_cov.py:330-331, 370-371` — `do_combine` rejects mixed-seed slabs). Lane B established that
the guard's coverage **excludes the dominant block**:
[`FINDING-20260817-cause3-C-leg-does-not-cover-the-dominant-block.md`](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/0b329e8ae8482e6334a68faf947fc80ae7265ac9/docs/orchestration/FINDING-20260817-cause3-C-leg-does-not-cover-the-dominant-block.md "evidence/prepublication-2026-08-20-0b329e8a:docs/orchestration/FINDING-20260817-cause3-C-leg-does-not-cover-the-dominant-block.md")
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
produced every wrong figure on this cell**: mine (~1 GPU-node-hour, wrong footing), the `28.50 A100-h` one
(right footing, stale by 37.1%, and pricing an unsatisfiable condition), and my `~28.5×` ratio (cross-unit
by 4× *and* non-commensurable). **Four wrong numbers on one cell in one day, three of them mine.**

## 2c. `M(ii)`'s referent — **RESOLVED BELOW: `(B)` ADOPTED, `M(ii)` recorded UNMEASURED** *(was "PROPOSAL, awaiting a second or a dissent"; the proposal was seconded on independent grounds by lane A and the resolution is at the CONCEDED block further down this section — the heading described the state BEFORE the resolution inside its own section, and two lanes spent a round trip on a question already answered here. `BEN-460`.)*

The mediator asked: **which leg's seed does `M(ii)` mean?** My answer has two parts and the second is the
one I think is actually open.

**Part 1 — "which leg" is already answered, and not by me.** `VL141` records it as consequence (b):
**`M(ii)` must vary BOTH seeds.** That is not a fresh choice — it is grounded in the criterion's own defect
statement, which says *"per-throw **or** per-universe unfolds drawn with different estimator seeds."* Both
ensembles are named in the defect, so a magnitude covering only one measures only part of it. **I am not
re-deciding this; I am pointing at it**, and `VL141` also states the reason it needed its own row: *"a
false quotable claim about the candidate, independent of cause 3."*

**⚠ PART 2 STATES THE PROBLEM, NOT THE OUTCOME — `(B)` IS ADOPTED FURTHER DOWN THIS SECTION.** Read to the CONCEDED block before treating anything here as open. *(Left as written because the gap it describes was real and its statement is what the resolution answers; a reader who stops here concludes the gap is live, which is exactly what happened. `BEN-460`.)*

**Part 2 — the real gap, and it is a SPECIFICATION GAP rather than an ambiguity.** `CRITERIA` §2 asks for
*"**the** magnitude of what varying seeds would have contributed"* — **singular magnitude, two seeds** — and
it does **not** say whether that is:

* **(A) per-leg and summed** — scan the sweep's seed, scan the throw path's seed, add the two contributions; or
* **(B) jointly on the composite** — vary both together in one scan and take the resulting spread.

**These are different numbers, and choosing between them is a physics decision, not a reading.** (A)
treats the two legs' estimator noises as independent contributions to be added; (B) does not, and would
capture any correlation between them. The covariance sums blocks, so (A) is the construction-shaped answer
and (B) is the ensemble-shaped one. **The criterion is silent, and no amount of careful reading makes it  **← AND THAT IS WHY A SPECIFICATION WAS CHOSEN RATHER THAN READ: see the CONCEDED block below, `(B)` adopted.**
speak** — which is the test the mediator set for calling something a gap rather than an ambiguity.

**So: recorded as a specification gap that needs a decision, not papered.** And note the ordering it
implies: **the gap is answerable now, on paper, at zero cost**, whereas the *measurement* it governs is
blocked behind two code changes. So answering it does not unblock the run — but leaving it unanswered means
the code changes would be made without knowing what they must enable, and (A) and (B) do not require the
same instrumentation. **(A) needs each leg's seed independently variable. (B) needs both variable in one
process.** That is a real difference in what lane B's stamping repair has to support.

> ### CONCEDED 2026-08-17: **(B)** is the specification. My recommendation of (A) was wrong, and the
> decisive objection was against my own ground.
>
> **I set the bar — *name the inter-leg correlation you expect to be non-negligible* — and it was met.**
> **The correlation is the retired jitter term itself.** `a0cdc01:unified_throw_cov.py:225-227`:
>
> > *"the block units + `x_cv` all share one seed, **so their jitter cancels in `(x_b - x_cv)`.** That makes
> > the raw unified trace jitter-inflated relative to the block sum."*
>
> **That is a statement about inter-leg estimator-noise covariance, and it says the covariance is SET BY
> WHETHER THE LEGS SHARE A SEED.** So the term (A) would drop is not one anybody *expects* — it is one this
> repo **measured, built a correction for** (`tr(C_uni) - ||Dcv||^2`), and then **retired along with the
> correction.** And B's seed map makes it bite: four legs run at estimator seed **42** with uthrow alone at
> **1000**, so varying 42→43 moves all four **coherently**. **(A) assumes zero covariance under precisely
> the condition that creates it.**
>
> **THE OBJECTION THAT DECIDES IT GOES TO MY GROUND, AND I VERIFIED IT RATHER THAN ACCEPTED IT.** I argued
> (A) because *"X is a sum of blocks, so a per-block magnitude composes the way the artifact does."* **That
> IS the block-sum assumption, and this campaign already refuted it by measurement.**
> `docs/HIGHER_DIM_OMNIFOLD_DESIGN.md:153-157`, read this turn:
>
> > *"block-sum **underestimates** the vertical systematic **~2×** (jitter-corrected unified/block
> > sqrt-trace **2.01**) … **adopted** as the published 4D systematic via PSD-safe fractional-inflation
> > transfer (`adopt_unified_4d.py`)."*
>
> **A sum of blocks composes VALUES additively; it does not compose VARIANCES additively unless the blocks
> are independent.** My argument conflated the two, and (A) would re-adopt on the estimator-seed axis exactly
> the inference this campaign measured, rejected, and **rebuilt the construction to avoid** on the band axis.
>
> **And (A) is not even uniformly conservative**, which is worse than being wrong by a factor: zero
> covariance is *right* for 42-vs-1000 and *wrong* within the 42-group, so the error is **structured and
> directional** — not boundable by one correction factor and not labellable conservative.
>
> **THE ARGUMENT I CONSIDERED FOR INDEPENDENCE, AND WHY IT DOES NOT RESCUE (A) — recorded as
> `CONSIDERED-AND-DECLINED` with its mechanism, not as absent, so that a later measurement of the decorrelation has a stated argument to revisit `(B)` against rather than one to re-derive.** The four legs at seed 42
> operate on **different inputs**, so a shared seed initialises the same RNG state but consumes draws against
> different data — perhaps the perturbations decorrelate. **That is an empirical claim nobody has measured**,
> which puts it in exactly `M(ii)`'s own position. **Using it to choose the specification would be letting an
> unmeasured convenience pick the criterion — the very thing I would be conceding against.** So I do not
> offer it, and I have no a priori argument for independence.
>
> **Adopted: *do not let measurability choose the specification.* (A) is cheaper BECAUSE it assumes away the
> term that requires the joint measurement, and that is the tell rather than the recommendation.** `(B)` is
> the specification; **`M(ii)` is recorded UNMEASURED.**
>
> ### A COST OF (B) THAT I SHOULD STATE, SINCE I AM THE ONE ADOPTING IT: GATE 1 BECOMES SERIAL
>
> **This corrects my own §2b.** I wrote that `M(ii)` is *"blocked on two code changes … and only after those
> is it a cost question."* Under **(B)** that is wrong in a specific way: a **coherent** variation of the
> shared seed across four legs requires **all four legs seed-variable at once.**
>
> B verified that **stat and ML can run a clean estimator-only scan today, with no code change** —
> `bootstrap_nd.py:19-29` has `--fixed-data-seed` that pins the draw and routes `--seed` to the estimator
> (`_est_seed = a.seed if a.fixed_data_seed is not None else a.estimator_seed`, read this turn), and
> `seedscan_split.py:36` exposes `--estimator-seed` directly. **Under (A) that capability could have produced
> a partial `M(ii)`, reported per leg as instrumentation landed. Under (B) it buys nothing**, because a joint
> measurement needs the joint capability.
>
> **So `sweep_bank_5d.py:252`'s hardcoded `42` stops being one of two parallel edits and becomes THE blocking
> dependency.** Gate 1 is smaller than anyone said in module count — **two modules, not four legs** — and
> **more serial than I said** in sequencing. Both corrections belong on the record together, because the
> first sounds like good news and the second is why it is not.

**My superseded recommendation, left as written:** **(A), per-leg and summed**, on the
ground that `CRITERIA` §0 defines `M` as *"measured on X's own inputs"* and X is constructed as a **sum of
blocks** — so a per-block magnitude is the one that composes the way the artifact does, and it is also the
only one that can be reported per leg when one leg's instrumentation lands before the other's. **If the
mediator or Assistant dissents toward (B), the dissent should say what correlation between the two legs'
estimator noise it expects to be non-negligible**, because that is the only thing (B) buys over (A).

**The two code changes §2b names are better-precedented than I said — and my first phrasing of that was
`BEN-386`-shaped, so here it is re-grounded.** Verified: `bootstrap_nd.py:19,21` and `seedscan_split.py:36`
**already carry `--estimator-seed` alongside `--fixed-data-seed`**, `:25` stating the split in its own help
text — *"`--seed` varies data+MC, `--estimator-seed` fixed."* So the two-role separation is an existing
pattern here, not a new design.

**But a precedent in one file says nothing about feasibility in another, which is exactly `BEN-386`: the
file an edit lives in is not the file that validates it, so a pin sweep can tell you an item is expensive
and can NEVER tell you it is cheap.** So I checked the **callees**, which is the instrument that can
answer it:

| module | what the edit is | callee constraint |
|---|---|---|
| `sweep_bank_5d.py` | add `--estimator-seed`; replace the literal at `:252` | **none** — the call is `omnifold_loop(…, seed=42, …)` and the callee **already takes `seed` as a kwarg**. No receipt references this file at all. |
| `unified_throw_cov.py` | split the single `--seed` (`:525`) into two roles | **none** — `args.seed` is the **estimator** seed at `:254`, `:285`, `:302` (`seed=np.int64(args.seed)`) and the **draw** base at `:223` (`default_rng(args.seed + gj)`). Adding `--estimator-seed` defaulting to `args.seed` and using it at the three estimator sites, leaving `:223` alone, is caller-side only. |

**So the CONFIGURATION change is small and unblocked at the callee — evidence from the callee, not from a
pin sweep.** And per `BEN-386`'s asymmetry, that is the most this can establish: **I have shown no blocking
constraint, which is not the same as showing it is cheap.** Cost is GPU time to re-run the sweep, and that
is the axis where the two figures disagree. **Feasible to configure, expensive to run, and those are
different questions** — conflating them is what produced every wrong cost figure on this cell today.

**And the cost figure now has two unreconciled values.** B measures **0.44 node-h** for the stat estimator
axis against `FOOTING-20260817:66-69`'s **~1 GPU-node-h** — the very figure I quoted this morning as *"the
cheapest open cell."* B says its own is the conservative one and **did not reconcile them.** So the cell I
first priced at ~1 GPU-node-hour on the wrong footing now has, on the *right* footing, **two independent
values disagreeing by ~2× with neither reconciled.** Recorded rather than averaged.

### The bound-vs-`M` judgement, which the mediator put closer to my desk than theirs

**A laterals-only scan would land cause 3's `M(ii)` in cause 4's CURRENT position** — a **bound** where the
criterion asks for a **measurement**. `CRITERIA` already rules on that shape for cause 4: *"a bound is not
the `M` leg"*, and `DETERMINATION-20260817-causes-3-4` routes the judgement without taking it.

**So the ordering matters more than the price.** ~15.4 A100-h buys **arrival at an already-open,
already-routed judgement**, not a discharge. **And if the bound-vs-`M` judgement is taken FIRST and comes
back "a bound cannot stand in for `M`", the scan's value drops to documentary before it is run.** Spending
compute to reach a question that is already on the table, and might be answered against you on paper, is
the worst available order.

> ### RULED 2026-08-17: the laterals-only scan DOES NOT RUN
>
> **Taken by the mediator and lane C agreeing, which settles it under Joseph's 2026-08-17 rule — and it
> settles in the direction of NOT spending.** The ground is **not** cost and **not** B's construction
> argument alone: **`CRITERIA` has already ruled, for cause 4, that a bound is not the `M` leg, and by §0's
> own consistency that ruling extends to cause 3.** The scan would arrive at a question the criterion has
> already answered.
>
> **The ordering sentence, for the record:** *spending compute to reach a question already on the table,
> which might be answered against you on paper, is the worst available order.*
>
> **I CHECKED THE RULING ON THE MERITS RATHER THAN ACCEPTING IT, and it is entailed rather than
> stylistic.** §0:53-54 reads: *"A measured large difference discharges the cause just as well as a measured
> small one; **what is forbidden is an unmeasured one.**"* A bound leaves the difference **unmeasured** — it
> is an upper limit on the quantity, not a measurement of it. **So "a bound is not the `M` leg" follows from
> §0's own wording and needs no separate justification. I have no merits case against it**, and I record
> that so the branch is closed rather than left dangling for someone to reopen as an open question.
>
> **And the branch the mediator DECLINED should stay declined, for the reason given.** It was mine —
> *"if a bound is admissible, cause 4's `M` may be closable for free on the existing `<0.1%` bound"* — and
> the mediator declined it because **its attraction is that it moves a cell at zero cost, which is the shape
> of motivated reasoning.** That is right, and it is right about my argument specifically. Today's record is
> of numbers and grades that drifted toward cheaper-and-more-favourable until someone checked them; an
> argument whose payoff is its own premise belongs nowhere near a discharge decision.

**My position, superseded by the ruling above and left as written:** the judgement
should be taken **once, for both causes 3 and 4, before either scan is priced.** `CRITERIA` has already
answered it for cause 4 in the negative — *"a bound is not the `M` leg"* — and if that ruling stands, then
by §0's own consistency it stands for cause 3, and **the laterals-only scan should not be run at all.** If
instead a bound IS admissible, then cause 4's `M` may be closable on the existing `<0.1%` bound **without
any run**, which would move a cell for free. **Either way the paper judgement dominates the compute
decision, and it is one decision rather than two.** Not mine to take; stated so it can be answered in one
move rather than twice.

**A correction I should carry rather than inherit:** the refusal ground first relayed to me for that scan
— *"18 of 188 is the minor leg"* — was **a member count doing duty as a variance share**, and B caught it.
The refusal now rests on B's weighting-independent ground: holding the vertical arm at `42` makes 169 of
188 a **constant**, so the result is **a partial derivative reported as a total**. Same conclusion, sound
reason. **I note it because the unsound version reached me and Joseph before the correction did**, and a
board that inherited the first version would have recorded the right answer for the wrong reason.

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

**AND THIS IS TWO DEFECTS WITH DIFFERENT REMEDIES, NOT ONE — B's point, and it is the most important thing
anyone has said about this board's SHAPE.** I had them in a single `P` cell, which is a trap:

| | defect | remedy | survives the other's fix? |
|---|---|---|---|
| **P-i** | **nothing RECORDS the seed value** — no product, no receipt. B ran a covering search over every tracked `*.json`/`*.tsv`/`*.txt`/`*.md`: **zero hits.** | **add a stamp** | — |
| **P-ii** | **nothing COULD record it on the dominant arm** — `sweep_bank_5d.py` and `analyze_universes_5d.py` have **nowhere to put one** | a **new write site**, not a stamp | **YES — P-ii survives P-i's fix** |

**Why one cell was dangerous:** a future *"stamp added, `P` satisfied"* would close the cell **while the
dominant arm is still ungraded.** P-i is satisfiable by an edit; P-ii is not, and the arm it concerns is the
dominant block. **Graded as two, so a fix to one cannot silently discharge the other.**

**B also confirms my harsher grade and calls its own recommendation too generous** — its covering search
shows no receipt records the seed for the **uthrow** arm either, so clause (i) fails there as I graded it,
**and the obvious rescue is foreclosed by B's own `BEN-245`**: the launchers hardcoding `--seed 1000`/`42`
are **committed intent, not provenance.**

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

## 3. Cause 4: HALF the REASON the `M` cell was unreachable is false — the method half — and the cell still does not move

`CRITERIA-20260811` §2 grounds cause 4's `M` on *"no committed document records which scalar or how it was
estimated"*, so that constructing one now would be *"the success condition invented after the fact."*
**HALF of that reason is false, and I verified the correction from the commits rather than from the
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

**NARROWED 2026-08-17, and the narrowing is the point — the sentence is a CONJUNCTION and only ONE half
is refuted.** §2 reads: *"The retired procedure subtracted a scalar, and no committed document records
**which scalar** or **how it was estimated**."* Those are two claims:

| half | status | why |
|---|---|---|
| *"how it was estimated"* — the **method** | **REFUTED** | `a0cdc01` carries the derivation in the comment, and code is a committed record |
| *"which scalar"* — the **value, per artifact** | **SURVIVES, untouched** | nothing found today shows what any *given archived artifact* had subtracted |

**This is `BEN-245`/`BEN-083`'s distinction — a committed specification is INTENT, not PROVENANCE** — and it
is the same distinction lane B used to withdraw its own uthrow MET. Code history shows the method existed
and was active across a commit range. **It does not show that any particular artifact was built with it
applied, nor at what value.** Credit to Assistant for constraining the finding before I did.

**And the surviving half is STRONGER than when it was written, which I do not think anyone has said yet.**
The specification we recovered shows the scalar was **never a stored quantity**: `jit_trace` was computed
at runtime as `float(np.sum((x_cv2 - base) ** 2))` and emitted only to stdout —
`print(f"\n[null] jitter floor ||x_cv(s+7)-x_cv||^2 = {jit_trace:.3e}")`. **So "which scalar" for a given
archived artifact is recoverable only if that run's LOG survives**, not from any artifact or receipt. That
is a sharper claim than *"no document records it"* and it names a **checkable, unchecked** next step: does
any surviving run log carry a printed jitter floor for a product still in play?

**ANSWERED 2026-08-17 by lane D, and the answer is a third one — neither of the two I anticipated.**
**No** surviving log carries a jitter floor for a product still in play. But **one value did survive,
attached to a product that no longer exists**: `[null] jitter floor = 3.731e-78`, `sqrt = 1.932e-39`, in
`uthrow5d_comb_55286276.out` (2026-07-01, **purgeable scratch only**). That run wrote
`uq_5d/unified_throw_cov_5d.root`; the file now at that path is the landed headline, mtime 2026-07-13 —
**overwritten 12 days later.** *A path joined them; it did not make them the same object.*

**Three constraints D attached, and the first is a methodological point worth more than the result.**
The **durable** corpus returned **"0 reachable, not 0 hits"** — `.gitignore` excludes `*.log`/`*.out`/`*.err`,
so run logs are **absent by construction** and a null there means nothing. **D established reachability by
finding a known script's stdout in the scratch corpus before counting.** That is `BEN-235`'s class —
a search structurally incapable of finding what its silence would deny — and it is **the first time today
someone pre-empted it instead of filing it afterwards.** Second: **M = 1 against N ≥ 3** runs known to have
written that path, so it is a completeness gap, not an answer. Third: the one value exists **only on
purgeable scratch** — the *third state* between recorded and unrecoverable.

### The branch, CLOSED as open-and-immaterial — and the reason is not "both branches land the same grade"

D correctly declined to assert whether the 07-13 headline run passed `--null`, leaving two readings:
**UNRECOVERABLE-BECAUSE-LOST** (a floor was printed for the live product, log gone) or **NEVER-COMPUTED**
(none ever existed for it). **I was asked whether that distinction changes my wording or my routing. It
does not, and the reason is stronger than the grade coinciding:**

**Neither branch was ever a route to a number.** Read the recovered specification's own derivation:

> *"With two CV unfolds at different seeds, **`E||x_cv2 - x_cv1||^2 = 2*sum_bin sigma_jit^2`**"*

and the implementation is `x_cv2 = _xsec_for_weights(…, args.seed + 7)` then
`jit_trace = float(np.sum((x_cv2 - base) ** 2))`. **So `jit_trace` is a ONE-SAMPLE ESTIMATE OF A
VARIANCE** — the comment writes it as an expectation, and a single evaluation is one draw from it. Two
consequences:

1. **A recovered log value is one noisy realization**, not *the* scalar. D's `3.731e-78` is one draw, for a
   superseded product. **Doubly unusable, and the second reason is the durable one** — even the right
   product's log would have given a single draw of a noisy quantity.
2. **A recomputation would be a different draw.** Both unfolds carry GPU/process non-determinism, so the
   value is environment-dependent. Recomputing today yields *today's* realization, not the historical
   subtraction. **This is `VL130`'s species measured from the other side**, and the campaign already knows
   that floor is not small.

**So the distinction is immaterial to the grade, to the wording, and to the routing, and I close it.** It
should not sit looking unfinished.

**One thing this DOES surface, flagged with its brake because it would otherwise move a cell.** The
recovered specification makes the counterfactual **recomputable in principle** — a route to `M` that is
neither recovering a record nor inventing a success condition, since the recipe is the documented one. **I
am not proposing it**, and the brake is the point: because `jit_trace` is a one-sample variance estimate,
a recomputation measures *a* realization of the quantity the defective construction would have subtracted,
**not the one it did**. Whether that satisfies §0's `M` is a **judgement of the same species as the `M(ii)`
gap** (§2c) — not a lookup — and it would need the machinery restored, since the code is absent at HEAD.
**I flag it because burying it would be worse than naming it, and I name the brake first because the
argument's payoff is otherwise its own premise.**

**So the correction to land is NOT "the stated reason is false."** It is: **one of two conjoined claims is
false, the other stands, and the sentence should be rewritten to assert only the surviving one.** A blanket
refutation would overshoot in the direction that flatters the morning's claim — and per the mediator, that
is the direction it has been wrong in twice today.

**The cell does not move**, and Assistant's read is that **the surviving claim may be the one cause 4's `M`
leg actually needs.** If so, the finding narrows the *reason* without touching the *grade* — which is what I
said this morning when I declined to move it.

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

> ### RESOLVED 2026-08-17: cause 5 is **N/A for X ON ITS MERITS** — and the gap was a READING gap, not an
> evidentiary one
>
> **Established by Assistant, not by me, which is what makes it usable** — I am the cause's owner, and my own
> reason for grading it `UNDECLARED` was that a quorum containing its owner is thin. The route was to read
> `DETERMINATION-20260811-cause5-binding-half.md` **against the question**, where §7 already answers it:
> recoil is *"a different estimator"* (`:233-237`, *"What this determination does not do"* — read this turn).
> Assistant then traced the one route by which cause 5 could reach X and found it **absent**:
> X's background is **MC-derived** (`sweep_bank_5d.py:171-177`, `mc_background` plus per-universe
> `w_bkg_*`), the estimator is **lgbm on every leg**, and **the recoil-PET budget is a DOWNSTREAM CONSUMER of
> the shared bkgaware bank rather than an input to it.**
>
> **LANDED 2026-08-17 in `VL66` at `d1c5f90`** — routed to B as clerical, attributed to Assistant, and
> explicitly not me and not Assistant, per my own reason. The board's `pending` clause is retired.
>
> **⚠ AND MY OWN §4 CARRIED THE SAME BAD CITATION, WHICH I AM RECORDING RATHER THAN QUIETLY DROPPING.** The
> sentence above read *"`OPEN_ITEMS` item 6 states no recoil-PET component is transferable."* **`OI-6` is the
> standard-P4 purity decision (`docs/OPEN_ITEMS.md:74`) and says nothing about transferability.** Found by
> lane B while landing the declaration; **B corrected it in the ledger row and recorded that it failed rather
> than silently repairing the address**, which is the reason it reached me at all. Re-derived here rather than
> accepted: the claim's live home is **`OI-3`, `docs/OPEN_ITEMS.md:71`** — *"Recoil-only covariance cannot be
> transferred and the joint full-event construction is not built"* — and its original phrasing is
> **archived** at `docs/OPEN_ITEMS-ARCHIVE-2026-08.md:834` (*"…automatically transferable to the new
> estimator."*), which is the sentence the `DETERMINATION` quotes. A covering `grep -ciE 'transferab'` over
> the live `docs/OPEN_ITEMS.md` returns **`0`**, so the bare ordinal had **no** referent there to be
> mis-numbered against — it was pointing at a document that no longer contains the claim in any form.
> **A renumbered/archived item plus a bare ordinal is `CLAUDE.md`'s own rule broken in transit** (*item ids
> are prefixed with their document's short name*) and it is the same decay class as this board's `POINTER 3`
> on `CRITERIA-20260811`'s line-range header citation. **I received the citation and repeated it without
> resolving it, which is the very failure §4 is about, committed in §4's own paragraph.**
>
> **AND A CAVEAT ON WEIGHT, WHICH PROTECTS MY GRADE RATHER THAN WEAKENING IT — B's, and it is right.**
> `OI-3`'s owner cell reads **`PET / cause 5 owner`**. So the transferability claim is **the owning lane's
> own statement**: it corroborates the declaration's background and **must not be counted as a second
> outside voice.** My `UNDECLARED` grade's entire content was that nobody outside the owning lane had said
> the cause does not reach X — **so a corroboration sourced to the owner cannot be what discharges it.**
> **The outside evidence is Assistant's `sweep_bank_5d.py` trace, and it stands alone.** That is a thinner
> footing than the two-source reading, and it is the correct one.
>
> **AND THE PROCESS LESSON IS ABOUT MY GRADING, NOT IN ITS DEFENCE.** Assistant's note: *the weakness was
> never in the evidence — the answering document existed and nobody had read it against the question.* **Two
> documents declining to RE-DERIVE cause 5 produced the appearance of an evidentiary gap where there was a
> READING gap**, and I inherited that appearance: I graded `UNDECLARED` partly *because* `MAP` §2 said *"I did
> not re-derive it and do not summarise its verdict."* **"Not re-derived" and "not read" got conflated, and
> only the second is free to fix.** That is a distinct failure from the ones this board has been collecting —
> not a claim outrunning its evidence, but **evidence sitting unread behind a correctly-stated refusal to
> re-derive it.** A lane declining to re-derive is being careful; a board reading that as *unavailable* is not.

**What would have closed it, and did:** one sentence in the ledger stating whether cause 5 is on X's construction path.
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

## 7b. `INAPPLICABLE` is in USE as a leg grade, and `§3` does not define it — and as written that
forecloses a cause-4 option rather than opening one

**Surfaced while checking the declined branch, and reported because its as-written resolution goes
AGAINST the outcome I would have preferred.** That asymmetry is the only evidence I can offer that raising
it is not the motivated reasoning the mediator just declined.

**`§3:246` states the vocabulary and the rule:** *"Legs are graded **MET / OPEN / UNRESOLVED**. A cause is
discharged only with four METs."* **`INAPPLICABLE` is not among the three.**

**But it is already in use, twice:**

1. **Cause 3's `C` leg.** Lane B's finding is titled *"Cause 3's `C` leg is **INAPPLICABLE** to the dominant
   block"* — the guard's population excludes `combined_source` entirely, so there is nothing for the leg to
   be MET or OPEN *about* on that path. This board carries it as `PARTIAL`, which is my own coinage and is
   also not in §3's vocabulary.
2. **Cause 4's `M` leg.** `DETERMINATION-20260817-causes-3-4` §5 routes three options, and the middle one is
   *"cause 4 is discharged on three legs with `M` declared **inapplicable**."*

**Under §3 as written, option 2 is not available.** A leg graded `INAPPLICABLE` is neither `MET`, `OPEN`, nor
`UNRESOLVED`; and *"discharged only with four METs"* means a cause carrying an inapplicable leg **can never
discharge**, however sound the reasoning for its inapplicability. **So the criteria as written foreclose the
`DETERMINATION`'s own middle option** — and nobody has noticed, because the option was routed rather than
exercised.

**This cuts both ways and I am not proposing which way.**

* Treat `INAPPLICABLE` as **satisfying** the leg → causes discharge more easily. **Favourable direction**,
  and it would immediately make cause 4's middle option live.
* Leave §3 as written → a cause with an inapplicable leg is **permanently undischargeable**. **Unfavourable
  direction**, and it is the reading that currently holds.

**As written, the unfavourable reading is the one in force.** So naming this gap **closes** an option that
was being kept open for cause 4; it does not open one. **That is the test the mediator set for the declined
branch, applied to this one before offering it.**

**RULED 2026-08-17 — the conservative branch, taken by the mediator with lane C agreeing.** **§3 as
written is operative.** Consequence, and it is a *foreclosure* rather than an opening:
**`DETERMINATION-20260817-causes-3-4` §5's middle option for cause 4 — *"discharged on three legs with `M`
declared inapplicable"* — IS NOT AVAILABLE**, and has been recorded as such on that determination rather
than left as a routed option that reads live. The definition question below is **left open deliberately**,
because the favourable reading is the one that moves cells and the conservative one is already the status
quo, so adopting it costs nothing.

**What is needed is a definition, not a decision about any cause:** does §3's vocabulary admit a fourth
grade, and if so does a cause discharge on three METs plus one justified `INAPPLICABLE`? **That is the same
species as §2c's `M(ii)` gap** — a criterion that cannot be read without a substantive choice — and it
should be recorded as needing one rather than settled inside a cause's row. **Routed, not taken.**

## 8. The one structural recommendation

**Every future cause-state report should carry the artifact in the same row as the state.** The ledger
already did this on 2026-08-11 (VL62–VL68) and it is the single change that stops the tally being
misread. This board's contribution is to extend it one step: **the artifact belongs in the same row as
each *leg*, not just each cause** — because cause 1 currently has `M` measured on X's own bank while `P`
holds only for the candidate, and a per-cause artifact column cannot express that.
