# A seed census that cannot reach the product it grades — cause 3's `P` leg

**Lane B, 2026-08-17. Read-only. Measured against `91fc4e9`.** This is the `C_syst` `seed`-key check the
mediator asked for first, on the ground that **it can withdraw a MET**. It does. `BEN-246`.

**Recommendation, not a re-grade:** cause 3's `P` cell should read **PARTIAL — MET for the `uthrow` leg
only, ABSENT for `combined_source`**. I have added a POINTER to `CRITERIA` and **have not edited the verdict
cell.** Lane B measures this leg and `BEN-381` forbids the same lane grading what it measures; the cell
belongs to lane C or the mediator.

---

## THE ONE PARAGRAPH

Cause 3 is *varying estimator seeds*. Its `P` leg is graded **MET for the candidate**
(`CRITERIA…:239`, re-cited 2026-08-17 by lane E to `receipt_candidate_stamps_5d.json`, branch `S1`).
**Measured: the candidate carries no seed key of any kind** — not `seed`, not `slab_seeds`, not
`upstream_seed`. Its 13 stamped keys are listed below and **none of them is a seed.** The census that the
grade's language comes from (*"one seed `1000`, 40 throw + 36 block slabs"*) lives in
`unified_throw_cov.py`, is **complete and correct for the `uthrow` leg**, is **never written into any
product**, and **globs `.npz` slabs only** — so it is structurally incapable of seeing
`combined_source`'s 188 universes, which are ROOT files carrying no seed stamp, produced at estimator seed
`42` hardcoded. **The grade is true of one upstream, silent about the other, and the other is the dominant
block.**

**Lane E's receipt is not wrong about anything it measured.** It verified nine propagation stamps and both
negative controls came back absent, as required. The defect is one level out: **cause 3's criterion is about
seeds, and none of the nine stamps is a seed.** That is `BEN-106`'s own shape — *"predeclaring outcomes does
not protect you from predeclaring them over the wrong object"* — recurring over the wrong **quantity** this
time rather than the wrong number of objects.

## 1. The candidate carries no seed key — from lane E's own receipt

`nd-unfolding/uq_5d/receipt_candidate_stamps_5d.json`, `A1_candidate_meancentered.all_keys` and
`A2_candidate_cvcentered.all_keys`, **identical 13-key sets on both arms**:

    centering_convention          fixed_seed_null_norm_checked   joint_mean_shift_norm_checked
    combined_source               n_throws_checked               sqrt_tr_new
    uthrow_source                 sqrt_tr_old                    upstream_n_throws
    hCov_combined5d_total_uthrow  hInflation_g
    upstream_fixed_seed_null_norm upstream_joint_mean_shift_norm

The three propagated **values** are `n_throws`, `joint_mean_shift_norm`, `fixed_seed_null_norm`. **No seed.**

**The one seed-adjacent stamp is disclaimed by the code that computes it.**
`unified_throw_cov.py:449-451`, in the failure message of the `--null` check itself:

> *"CV re-unfold is non-deterministic at the fixed estimator seed; the throws cannot be cleanly separated
> from `C_ML` **(this checks CV determinism only; per-slab seed provenance is enforced separately below)**"*

So `fixed_seed_null_norm = 5.8223488501140625e-50` establishes **determinism at one seed**, not **which
seed**, and not **that one seed was used throughout.** The code says so in the sentence a reader would
reach for.

## 2. The per-slab census — complete for one leg, and it dies at the combine

    :326       slab_seeds = set()
    :330-331   if "seed" in z.files: slab_seeds.add(int(z["seed"]))     <- over glob.glob(args.combine)
    :370-371   if "seed" in z.files: slab_seeds.add(int(z["seed"]))     <- over glob.glob(args.block_slabs)
    :417-419   if slab_seeds and slab_seeds != {int(args.seed)}: SystemExit  ("refusing mixed-seed combine")
    :430-433   if not slab_seeds: SystemExit  ("slabs carry no estimator-seed stamp")

Three measured properties, each load-bearing:

1. **Its scope is the two `.npz` globs and nothing else.** `combined_source`'s universes are ROOT files and
   are not read by this module at all. The census is not *incomplete* over its inputs — it is complete, and
   its inputs are one of the candidate's two upstreams.
2. **`slab_seeds` is never stamped into any product.** Its six occurrences are the five above plus `:418`'s
   message. The `--out-root` block (`:470-497`) writes `sqrt_tr_unified`, `sqrt_tr_block`,
   `joint_mean_shift_norm`, `fixed_seed_null_checked`, `fixed_seed_null_norm`, `n_throws`,
   `hJointMeanShift`. **The census result cannot propagate downstream, by construction** — so no consumer of
   any product can ever check it, and `BEN-106`'s stamp-propagation fix does not reach it because there is
   no stamp to propagate.
3. **The guard is silent on an unstamped slab.** `:417` compares only the seeds it **found**; a slab lacking
   the key is skipped at `:330`. `:430` fires only when **no** slab carries one. So *stamped-and-agreeing
   mixed with unstamped* passes. Every `uthrow` slab does stamp (`:254`, `:285`, `:302`), so **no live defect
   follows on this path** — but the guard's shape is what makes the blindness invisible rather than loud.

## 3. The other upstream: seed `42`, hardcoded, stamped nowhere, checked by nothing

    sweep_bank_5d.py:252   omnifold_loop(..., kind="lgbm", ..., seed=42, verbose=False)

`grep -n seed sweep_bank_5d.py` returns **exactly this one line** — no `add_argument`, no flag, no stamp.
`do_run`'s ROOT output (`:280-288`) writes `ndim`, `globalCompleteness`, `dataPOT`, `hXSecND_flat`. **No
seed.** And the combiner one hop up, `analyze_universes_5d.py` — which writes
`uq_universe_5d_covariance_combined_bkgaware.root`, i.e. `combined_source` itself — contains the string
`seed` **zero times** (`grep -n seed` exits 1) and writes only `TH2D` covariances plus a summary `.txt`:
**no `TParameter` at all.**

So on the `combined_source` half there is **no seed flag, no seed stamp, no seed census and no seed guard,
at any of the three hops.** The 169 universes agree on estimator seed `42` **by hardcoding**, which is a real
property of the code and **not** a verified property of the artifact: nothing in the chain could report a
disagreement if one existed.

## 4. Why this withdraws the MET rather than merely narrowing it

`CRITERIA` §2 states cause 3's `P` criterion as: *"X's receipt records the single seed value, and
`fixed_seed_null_norm` is PRESENT in X and <= tol."*

Measured against the candidate:

| clause | verdict |
|---|---|
| *"records the single seed value"* | **FAILS.** No seed key on either arm. Nothing records it, for either upstream. |
| *"`fixed_seed_null_norm` PRESENT and <= tol"* | **HOLDS.** `5.8223488501140625e-50` vs an absolute floor `1e-12`, 37 orders of margin — as lane E measured. |

**The first clause is the one the cause is named for, and it is the one that fails.** A grade of MET on a
two-clause criterion where the load-bearing clause is unsatisfied is not a narrow scoping issue; the leg's
evidence for *"one seed"* is a census over 76 `.npz` slabs belonging to the **smaller** upstream, which
never reaches the artifact and was never claimed by its author to cover the other one.

**What a MET would require, stated so it can be built rather than argued:** either (a) propagate the census
result — the census exists and is correct, it simply has no stamp; **and** add a census on the
`combined_source` side, which needs `sweep_bank_5d.py` to stamp a seed it currently hardcodes; or (b) re-word
the criterion to be explicitly per-upstream and grade each. **(a) is the honest fix and it overlaps the
seed-separation change already specified-not-written.** (b) is cheaper and leaves the dominant block ungraded.

**Reach of the withdrawal.** Cause 3's `C`, `M(i)` and `T` legs are untouched by this — `T`'s `N5` mutation
was independently re-derived by lane E and does fail its test. Cause 4's `P` leg is **not** withdrawn: its
criterion is *"key present, and <= tol, with tol and its source both stated"*, which is about the null and
not about a seed, and it is satisfied. **This finding moves one cell.**

**No number moves.** Every leg is internally single-seeded, so nothing in the candidate is mis-computed. What
is wrong is a **verification claim** — and unlike `VL141`'s wrong *description*, this one is load-bearing for
a discharge decision, which is why it is filed as a MET withdrawal and not as a ledger correction.
