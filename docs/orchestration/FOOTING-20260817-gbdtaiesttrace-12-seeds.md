# FOOTING of `\gbdtAiEstTrace`'s 12 seeds — established: it DIFFERS, and cannot serve as cause 3's M(ii)

**Lane B, 2026-08-17. Read-only; no cluster, no GPU.** Answers the one question dispatched: *which product,
which sweep, which J28 state* was `\gbdtAiEstTrace = 1.306e-39` computed on, compared against the
candidate's footing. **Does not adjudicate whether the scoped decision should be taken** — lane C ruled it
available *provided footing matches*, and it does not.

---

## VERDICT: footing differs. It cannot serve as M(ii). Cause 3 needs its own measurement.

The provenance was fully recoverable, so this is not the third ("unsourceable") outcome — the number has a
date, a launcher, a recorded input, an artifact, and a completion log.

| | the candidate | `\gbdtAiEstTrace` (AI1) |
|---|---|---|
| **date** | post-J28. J28 was found in the **2026-07-31** four-account audit; code fixed `081ae4a`; *"numbers NOT re-rolled, ledger scales QUARANTINED"* | **2026-07-14, 21:04 PDT** — **seventeen days before J28 was found** |
| **input** | the bkgaware universe sweep | **`of_inputs_5d.npz`**, `--fixed-data-seed 0` (`sbatch_ai1_estimator_scan.sh:23-24`) |
| **construction** | systematic covariance over the universe sweep, block sum **`4.357790406860002e-38`** | 12 varied estimator seeds on **one fixed data/MC draw**, `--iters 5`; **no flux universes at all** |
| **artifact** | `universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware{,_uthrow,_uthrow_cvcentered}.root` | **`uq_cov_ai1est_5d.root:hCov_ai1est5d_reported`** |
| **re-rolled since?** | — | **NO** |

**Sources, each read rather than recalled:** `nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md:738-743` (the
completion entry: *"AI1 estimator-only (fixed data, 12 varied estimator seeds) sqrt-trace=1.306e-39 (10694
bins, median 0.564%/bin) vs ML-split band 1.493e-39"*); `nd-unfolding/sbatch_ai1_estimator_scan.sh`
(`--array=1-12%1`, the input and both seeds); `nd-unfolding/ai1_packed_loop.sh` (the run that actually
produced it, `CONC=6` on one interactive GPU node); `KNOWN_ISSUES-ARCHIVE-2026-08.md:11` (J28's date,
fix commit, and that numbers were not re-rolled); `VALIDATION_LEDGER.md:1053-1070` (the candidate's block
sum and artifacts).

**Covering search for a re-roll, since the verdict rests on an absence.** `git grep -I -- "uq_cov_ai1est_5d"`
unrestricted returns exactly six sites: the 2026-07-16 presentation table, one 2026-07-18 verifier
`jsonl`, `state/cluster-ignored-set-walk-20260812.tsv`, three lines of the 2026-07-14 status log, and
`run_ai1_combine.sh`. **No post-J28 recomputation exists.** Also searched the value itself in four
spellings (`1.306e-39`, `1.306E-39`, `1.3060e-39`, `1.306e-039`) — five files, all citations of the same
July-14 result, and **no `VALIDATION_LEDGER` row at all.**

---

## The nuance that decides it, stated rather than buried

**AI1 uses no flux universes, so J28's flux-normalisation bug plausibly does not corrupt AI1's own
number.** That is worth saying, because it is the strongest argument *for* using it and it survives
scrutiny: J28 divided PPFX flux universes by the CV integral at five ND/5D sites, and AI1 varies only an
estimator seed on one fixed draw.

**But "not corrupted by J28" is a different claim from "same footing", and M(ii) needs the second.** The
criterion asks for *the magnitude of what varying seeds would have contributed* — to **this** budget. That
requires commensurability with the candidate, and AI1 was computed on a different input
(`of_inputs_5d.npz`, not the bkgaware sweep), by a different construction (one fixed draw, no universes),
before the correction that defines the candidate. **Its own July-14 log states the comparison it was built
for in budget-fraction terms — *"~3% of the 4.35e-38 total"* — and that denominator is exactly the
J28-affected quantity.** So the number may be valid about its own object while being non-transferable to
this one, which is `BEN-312`'s shape and the thing the dispatch asked to be checked.

**A second-order exposure found on the way, not the basis of the verdict:** `uq_cov_ai1est_5d.root` appears
in `cluster-ignored-set-walk-20260812.tsv`, i.e. it is **untracked and gitignored on purgeable scratch**.
Even had the footing matched, the artifact backing a published macro is one purge from unverifiable.

---

## Cost of cause 3's own measurement — DERIVED, not estimated

The dispatch asked for a derived cost only if the footing differed. It does.

**The original run is the recipe and it is recorded.** `ai1_packed_loop.sh` ran the 12 seeds at `CONC=6`
on **one interactive GPU node**, and the status log measures the tail directly: seeds 9-12 relaunched under
`salloc 55923713` completed in **~20 min**, with 12/12 at `21:01` and the combine finishing at `21:04`.
So **12 seeds ≈ 2 waves ≈ 1 GPU-node-hour, plus a ~3-minute combine.**

**The `--time=01:30:00` in `sbatch_ai1_estimator_scan.sh` is a per-task ceiling, not a measurement** —
reading it as 12 × 1.5 h = 18 GPU-h would overstate the cost ~18×.

**Stated limit on this derivation:** the ~20 min/wave was measured on `of_inputs_5d.npz`. A re-run *on the
candidate footing* would consume the bkgaware input, whose per-seed cost **is not measured here** and could
differ. So the figure is *"the measured cost of the same scan on its original input"*, which is the honest
form of the answer and is what a proposal should quote.

**Either way it is ~1 GPU-node-hour, far under the 24 GPU-h threshold — so the approval is the mediator's
with a peer confirm/deny, and does not go to Joseph.**

---

## What this does and does not settle

**Settles:** the footing question as posed — product, sweep and J28 state — and therefore that
`\gbdtAiEstTrace` cannot serve as cause 3's M(ii). Cause 3 discharges on **three** legs, not four.

**Does not settle:** whether `\gbdtAiEstTrace` should stay in `sec_systematics.tex:129` at all. It is cited
there as the estimator-seed scan's √Tr and inherits the July-14 footing; that is a note-text question, it
is outside this dispatch, and **nothing here goes into `docs/analysis-note/`.**

**Does not adjudicate** the scoped-use decision — C ruled it available on a matching footing, the footing
does not match, and so the option C described is simply not reached.
