# Decision calibration, 2026-08-17 — a ledger of grounds, so refusals can be falsified later

**Why this file exists.** Every spend decision taken this session pointed the same way, and every
outcome pointed the same way with it. That is not evidence of calibration — it is a description of the
prior two agents shared. This file records each decision **with the ground it rested on**, so a future
session can check whether the ground was later falsified. Absent such a record, "we were right every
time" is unfalsifiable, which is exactly the property this campaign's receipt convention exists to
prevent (`CONVENTION-receipt-ingredients.md`, `BEN-077`).

**Origin.** `Assistant` (second key) asked for a discount against its own three sustained dissents on
the grounds that all three were arguments *against spending*, so its scepticism and its conclusions
pointed the same direction and nothing tested whether it had priced its own alternatives honestly. It
then applied the same test to the mediator's record and corrected the mediator's self-assessment twice.
The corrective below is Assistant's; the instances are the mediator's.

## The correction that produced this file

The mediator wrote: *"the single exception went against the direction I was defaulting to."*
**True of the act, false of the outcome, and only the outcome tests a bias.** `OI-61(b)` was
authorized, attempted, and refuted — its finding was *"this is costlier than the row said"*
(`BEN-386`). So the one departure from the default **vindicated** the default. An authorization that
discovers hidden cost is a confirmation of a refusal bias, not a test of it.

This was itself the eighth species (`verification effort allocated by suspicion`) one more time: the
**act** is the flattering framing, the **outcome** is the unflattering one, and the mediator reached
for the act *while deliberately trying to discount its own record*. Third instance across two agents,
all parties aware of the species at the time — which is the evidence for the row's conclusion that
**naming the bias does not fix it.**

## What is NOT claimed here

Not that the session was too cautious. A bias toward *"do not spend on an unmeasured basis"* is the
correct bias for a publication closeout under quarantine, and each decision below was argued on its
own grounds — including `M(ii)`, where the mediator moved **against** its initial lean once the jitter
citation landed, and `OI-96`, where E's premise turned out to understate the defect.

The claim is narrower and it is the honest one: **there is no measurement of whether the bias was
correctly calibrated, and the record's shape cannot supply one.** No refusal in this set was later
shown unnecessary, and no authorization went cleanly. Both absences are needed to test it.

## The ledger

`GROUND FALSIFIED?` is the column a future session fills. `—` means nobody has checked.

| # | Decision | Disposition | Ground it rests on | Ground falsified? |
|---|---|---|---|---|
| 1 | `OI-126` re-centred Exponential(1) tiebreaker | REFUSED | `DECISION-20260815` §7, unanimous 4/4: Poisson(1) *is* the sampling distribution; Exponential gives the wrong distribution in the zero atom, and **both outcomes support `C_stat`** | — |
| 2 | Composite seed scan at the quoted `28.50 A100-h` | REFUSED | Wrong extent. **Three figures within 0.4% of each other are in play and the scope word is the whole content — recorded rather than averaged.** `39.078 A100-h` = `C_syst` re-seed, **MEASURED**, 189 tasks (`23.840` sweep + `14.2075` lateral+CV + `1.030` finalize). `39.22 A100-h + 55.34 CPU task-h` = one seed across **all four blocks**, a wider scope that lands coincidentally close on the GPU term. `39.23 A100-h` = **SUPERSEDED**, a FORECAST that scaled a 14-task mean to 19 (`14.36`) where all 19 universes had a realized elapsed; B replaced it with the measured `14.2075`. The near-collision is itself the hazard: someone quotes *39.2-ish* and the scope does not travel. **The decision rests on none of the three — it rests on the CPU term being the larger half, which an A100 grant does not reach** | — |
| 3 | `OI-60` Gate-2 re-run | DOCUMENTARY CLOSE (retrospective half) | Gate-2 is a **CPU** job (`sbatch_gate2_target_validator.sh:5`); the real blocker is 151.175 A100-h; and the published family's array identity **is not recoverable by any run at any price** — the fix instruments the loader and can only evidence families built after it lands | — |
| 4 | Laterals-only `M(ii)` scan (~15.4 A100-h, inside grant) | REFUSED | `CRITERIA` §0:53-54 — *"what is forbidden is an unmeasured one"*; a bound leaves the difference unmeasured, so *"a bound is not the M leg"* is entailed. Also weighting-independent: holding the vertical arm at 42 makes 169 of 188 universes a constant | — |
| 5 | Repin of a receipt-bound launcher | FORECLOSED ON MERITS | Would make the Gate-2 receipt assert that a loader which did not produce the archived target did produce it. **Joseph granted permission for this on 2026-08-17; the objection is not permission** | — |
| 6 | In-place cross-reference in the RUN_LOG at `:7922` | DECLINED | 443 line-number citations point into that file, ≥3 below the insertion point (`:8805`, `:8864`, `:9546`). One inserted line breaks them silently — the realised failure being `CRITERIA`'s own header citing `VALIDATION_LEDGER.md:65-88` | — |
| 7 | Defining a fourth leg grade so `INAPPLICABLE` can discharge | CONSERVATIVE READING KEPT | §3:246 closes the vocabulary at MET/OPEN/UNRESOLVED, four METs to discharge. The favourable reading would retroactively ease discharge for causes already graded under three | — |
| 8 | Reopening the bound ruling to close cause 4's `M` for free | DECLINED | The branch's attraction *is* that it moves a cell at zero cost. C read §0 and reported **no merits case** against the ruling | — |
| 9 | Wiring the fired unlock trigger as pre-commit check 10 | DECLINED | Trigger says *"no judgement call"* and the command exits 0 — but the guard is **inverted** (silent on the in-directory repoint it exists to catch, RED on a prose deletion), violating the dispatcher's own admitting rule 11 lines above the trigger | — |
| 10 | `56978466` re-run | MOOT ON MEASUREMENT | The repair already ran and succeeded as `56989462` (2026-08-14); products on disk, cited by seven files. A re-run would regenerate the push and yield a **different** nominal than the one every `OI-126` receipt rests on | — |
| 11 | `M(ii)` specification: (A) per-leg-and-summed vs (B) joint | (B), `M(ii)` UNMEASURED | Four legs share estimator seed 42, so their noise moves coherently; the named correlation is the retired jitter term (`a0cdc01:224-227`). (A)'s compositional ground is the block-sum assumption, which the campaign measured and rejected **on the systematic-band axis** (jitter-corrected `2.01`, `docs/HIGHER_DIM_OMNIFOLD_DESIGN.md:153-155`) — **precedent, not a measurement of estimator-noise cross-terms**, which remain unmeasured. The `2.01` is *jitter-corrected*, i.e. measured with the estimator-noise term already subtracted, so it cannot measure the quantity (A) drops | — |
| 12 | `OI-61(b)` | **AUTHORIZED** | E's sweep: routes entirely to unpinned files, clean on two independent instruments | **YES — refuted on attempt.** Pinned callee's `argparse choices=["nominal","floor"]` at `train_fullevent_nominal.py:325` rejects the caller's one-liner (`BEN-386`) — **but this CONFIRMS the refusal bias rather than testing it: an authorization refuted on attempt is not a test of a bias toward refusing** |
| 13 | `OI-96` | **AUTHORIZED** | Row called the occurrence count *"a crude proxy"*; change confined to pre-commit check 6 | Premise understated the defect: guard was **inverted**, not crude — **again a confirmation, not a test: the surprise was in the direction of *more* hidden trouble, which is the direction the default already assumed** |

## How to use this

**A `YES` in an `AUTHORIZED` row does not test the bias. Only a falsified `REFUSED` row does.** The column is per-row and honest, but it is not the bias instrument, and the two diverge exactly on rows 12-13: both YESes point the *same* direction as the ten dashes. A reader who counts `2 YES of 13` and infers self-correction has read the opposite of this file's thesis.

**Fill the last column when a ground turns out wrong.** A refusal whose ground is later falsified is the
only thing that measures the bias, and it will surface weeks from now rather than today. Zero
falsified refusals in one session by two agents sharing a prior is a description of the prior.

Note that rows 12 and 13 — the two authorizations — are the only ones whose grounds were tested at all,
and both were tested **by attempting the work**. That is the session's own evidence for E's standing
change: *attempt before costing; "cheap" is a hypothesis only an attempt tests.*

## Session identity: `Assistant` names two different sessions in today's record

**This file, `BEN-396`, `BEN-248` and `VL66` all credit a party called `Assistant`. That name is
ambiguous, and the ambiguity is the mediator's.**

The party meant, in every case, is **`Assistant [28640e]`** — the second-key session that produced the
`M(ii)` (B) dissent, the cause-5 `N/A` declaration, the species-eight formulation, and both corrections
to the mediator's self-assessment. Pin the ref, not the name.

**Why the name collides.** Two distinct sessions have been called `Assistant` on 2026-08-17, either
side of the machine restart that `HANDOFF-20260817-1133Z.md` was written for:

| | |
|---|---|
| pre-restart `Assistant` | held dispatch 1 of the handoff; was at its usage cap; **died in the restart having produced nothing that reached the record** |
| `Assistant [28640e]` | a different process — named `G`, renamed `F`, then renamed `Assistant` by Joseph. `ListAgents` still reported *"says it was G until 16s ago"* at first enumeration. **Everything attributed to `Assistant` in the record is this one** |

**Why it matters, and it is not pedantry.** Lane `A [84e2e8]` holds `BEN-390`–`BEN-396`. A reader who
maps the name `Assistant` onto the holder of that block manufactures a misattribution — and lane B
flagged that the *only* mechanism which caught it today was **the mislabelled party declining credit**:
A refused the gate-1 derivation, having no record of touching `bootstrap_nd.py`, `seedscan_split.py`, or
gate 1's leg structure. That mechanism fired once. It will not always.

**Standing convention, adopted here:** in any relay or attribution, write the ref — `Assistant [28640e]`,
`A [84e2e8]` — never the bare name. A session name is mutable and has been mutated three times today;
a ref is not. This is `BEN-248`'s *carry the route* rider applied to the identity of the party rather
than the provenance of the claim.

## One decision row updated

Row 11's `(B)` disposition has a further consequence B established after this file was first written,
and it strengthens the ground rather than weakening it: **the decorrelation argument — the one C
considered and declined — is not merely unmeasured but UNMEASURABLE on this footing.** Testing whether
two legs' estimator perturbations decorrelate requires varying one leg's seed independently of the
other, and for the sweep leg that is `sweep_bank_5d.py:252`, hardcoded with no flag. **So the argument
that would excuse the code change cannot be evaluated without the code change.** Recorded at B's
`EXTENT` §4.
