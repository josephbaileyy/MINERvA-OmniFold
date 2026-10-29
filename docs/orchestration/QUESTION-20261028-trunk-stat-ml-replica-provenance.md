# QUESTION for Joseph — which replicas do the adopted trunk's `C_stat` and `C_ML` rest on?

**Asked by** the close-items session, written up at the director's request (2026-10-28) and put
to Joseph by the director. **It rules nothing**, classifies no launcher, and runs nothing. It
arose while working `OI-160`, which asks for two launchers to be classified as superseded. The
director ruled that a provenance question and not housekeeping.

**CITABLE FOR:** the evidence on both sides, with file:line and sha, and the checks that would
settle it. **NOT CITABLE FOR:** any claim that the adopted covariance is wrong, or that it is right.

## The question

The scalar-5D trunk adopted on 2026-09-20 (`3d7465f6…`) takes its stat and ML blocks from
`uq_cov_stat_5d.root` (`6580016f…`, 891,732,011 B) and `uq_cov_mlsplit_5d.root` (`27b2e456…`,
892,078,834 B), as the Z pilot manifest's `sources.stat` / `sources.ml` declare
(`DECISION-PACKET-20260918-scalar5d-publication-blockers.md:435`).

**Were the 100 bootstrap and 24 split replicas behind those two files produced under the
corrected seed contract — one fixed estimator seed — or under the old one, where the estimator
seed varied with the bootstrap or split seed?**

## Reading 1 — pre-correction (as `OI-160` frames it)

- `OI-160` (`docs/OPEN_ITEMS.md`, filed 2026-08-28) measured on pscratch that the top-level replicas
  `boot_nd_5d/res_boot_1.npz` and `seedscan_split_5d/res_split_1.npz` carry only `seed` and **no
  `estimator_seed` key**. Their mtimes (2026-07-11..13) also **predate** commit `07c18aee`
  (2026-07-14), which changes `bootstrap_nd.py` to `seed=a.estimator_seed` (default 42), with
  a matching change in `seedscan_split.py`.
- `run_budget_5d.sh:15,17` and `sbatch_combine_5d_budget.sh:14,16` glob those top-level replicas
  (`PACKET-20260910-z-endpoint-A-acceptance-and-cause3-corr-amendment.md:445`).

## Reading 2 — post-correction, run before it was committed

- **The key test does not discriminate.** At `07c18aee`, the corrected `bootstrap_nd.py:36` still
  writes only `seed=` (`np.savez_compressed(a.out,seed=a.seed,…)`). The `estimator_seed` key first
  appears at `214acdbbc` (2026-08-18; `git log -S est_seed_offset -- nd-unfolding/bootstrap_nd.py`).
  So a replica made by the corrected July code also lacks it.
- **The commit post-dates the run.** `07c18aee` adds
  `nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md`, which calls itself an *"UNCOMMITTED
  working-tree tracking doc"* for a *"Corrected UQ Production"* launched 2026-07-11 (`:1-6` at
  that commit). Before the commit, `KNOWN_ISSUES.md` #14 (at `07c18aee^`) already read *"Replacement
  code uses … one fixed estimator seed … 20 tests pass. No corrected pro[duction]…"*.
- **The old replicas were set aside first.** At `07c18aee`, the status doc's `:39-41` reads *"Stale
  pre-remediation replicas/slabs archived to `*_prehm_20260711/` (boot_nd_5d, seedscan_split_5d,
  …)"*. The top-level replicas were then regenerated 07-11..13.
- **The run said the split scan fixes the estimator seed.** `:207-208`, 2026-07-12: *"seedscan_split
  fixes the estimator seed, so C_ML captures split-response only"*.
- **An execution record of the combine survives, which the 2026-09-10 search did not find.**
  `:334`: *"18:02 PDT STAGE1 DONE: boot5d 100/100 …, ssplit 24/24 … STAGE2 LAUNCHED: budget via
  interactive fallback (salloc 55878359 nid001021, …, run_budget_5d.sh) -> uq_cov_stat_5d.root +
  uq_cov_mlsplit_5d.root"*. Then `:335`, 18:26 PDT: *"+stat 1.806e-39 +mlsplit 1.493e-39"*, which
  matches the released products' `1.8063e-39` and `1.4934e-39`
  (`PACKET-20260910-…:416`). That packet searched `sacct` by job name and window and concluded *"No
  execution record survives for the rebuild"* (`:419`, and `DECISION-PACKET-20260918-…:803`). An
  interactive `salloc` allocation would not carry the name it searched for.

## Limits of Reading 2, stated so it is not over-read

- "pre-remediation" in `:39` refers to the `unfold_nd` non-finite-edge remediation (`:34-38`), not
  to the seed contract. The archive shows that the replicas were regenerated, not which seed code
  regenerated them.
- The status doc is a narrative log written by the running session. It is not a scheduler record,
  and it records no hash of the code that ran.
- The log's times are PDT. The product mtimes (`2026-07-13 18:04/18:05`,
  `DECISION-PACKET-20260918-…:436`) do not state a zone. If they are PDT, they fit a STAGE2 launch
  at 18:02.

## What would settle it (none of these were run here)

1. **Read-only scheduler:** `sacct -j 55878359 --format=JobID,JobName,Start,End,State,ExitCode`,
   for the STAGE2 allocation the log names.
2. **Read-only, local:** a search of the July session transcripts for the background tasks the log
   names (STAGE2 `brx2cua11`; packed loops `bqh1ukq75`, `bj3x6bysv`). They may record the exact
   command lines, and the `bootstrap_nd.py` that ran.
3. **Read-only, cluster:** whether `boot_nd_5d_prehm_20260711/` exists beside the top-level set,
   with older mtimes. That needs a read of the canonical cluster checkout, which is outside the
   close-items session's limits.
4. **Conclusive, but compute:** reproduce one replica (for example `res_boot_1`) with `07c18aee`'s
   `bootstrap_nd.py` (`--seed 1`, estimator seed 42) and with `07c18aee^`'s, then compare with the
   stored `xsec_flat`. This is about one 5D unfold, and it needs Joseph's compute authorization.

**Why it matters, without ruling.** Under the old contract, the bootstrap ensemble would also carry
estimator-seed variance. Under the corrected one, `C_stat` is data-only, and `C_ML` is split-response
only, which the July log itself notes (`:207-208`). That bears on how the trunk's blocks relate to
the estimator-seed sensitivity `AGENTS.md` names as the principal open question (`s_proj`).
