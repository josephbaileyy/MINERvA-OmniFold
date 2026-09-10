# The null-only plan — REVISED 2026-09-10 on Joseph's four corrections

**Supersedes `Z_BUILD_PACKET.md` §7.3–§7.5 on the null. Slab migration is WITHDRAWN and is not
proposed here in any form.** Prepared, not launched. Authorizes nothing.

---

## 1. WITHDRAWN: the re-stamp migration

`Z_BUILD_PACKET.md` §7.3 offered a branch B that re-stamped `estimator_seed`/`draw_seed` onto the
archived slabs. **Withdrawn, and Joseph's reason is the right one: missing seed-role provenance
cannot be repaired by adding fields.**

The warrant I would have leaned on makes the point against itself. The driver's own comment —
*"DAY-ONE IDENTITY: pass `--draw-seed 1000 --estimator-seed 1000` to reproduce every pre-split
product bit-for-bit"* — tells you which values would make the combine succeed. That is deriving
the stamp from the desired outcome, which is what a provenance record exists to prevent.

**Standing constraint for any future migration proposal:** the seed-role values must be
established from historical evidence *independently of the outcome they enable* — a producing
log, a scheduler record, a receipt written at the time. `unified_throw_cov.py:496`'s refusal
stays exactly as it is.

---

## 2. THE NULL-ONLY ROUTE — feasible, by EXPOSING the procedure rather than copying it

**It is not a reimplementation.** The 5D kernel is installed into the shared module by import
(`unified_throw_cov_5d` replaces `_xsec_for_weights` in `unified_throw_cov` at `:89`), so an
entrypoint that imports both modules and calls `base._xsec_for_weights` is calling **the same
function object the producer calls**. The five things Joseph named are preserved by construction:

| | how it is preserved |
|---|---|
| same 5D kernel | the same function object, via the same import side effect |
| same bank | `base._load_bank(args.bank)` — the producer's own loader, same `d`, `edges`, `w_truth`, `w_reco`, `td_cv` |
| same estimator seed | `args.estimator_seed`, the same argument the producer passes |
| same iteration count | `args.iters`, likewise |
| same support rule | `z_statistics.support_mask`, which `NULL_OPERAND_CONSTRUCTION` already names as the one implementation of `unified_throw_cov.py:370`'s `x_cv > 0` |

**Both calls execute.** Nothing is copied into either slot; `x_cv` and `x_cv2` are two invocations
of the kernel, exactly as `:369` and `:514` are. **Full operands are persisted** on the full
65,856 grid — the `[rep]` mask that `:515` applies inline moves after the persist, which is the
one producer-side edit and is Tier-2 code.

**Binding.** `persist_null_operands` records the schema, construction contract, writer identity
and code identity today; it records **no** bank, seed, iters or run id. The entrypoint must
therefore write those into a sidecar the receipt binds — bank path and digest, `estimator_seed`,
`iters`, the estimator settings actually in force, the producing revision, and the Slurm job id.
Without that the operands are byte-indistinguishable from any other pair, which is the schema gap
`Z_BUILD.md` requirement 3's *"verify their seed/run provenance"* is pointing at.

### 2a. The governing requirement, its exact scientific purpose, and the narrow amendment

`Z_BUILD.md` requirement 3: *"Capture both same-run internal fixed-seed CV vectors and the
predicate **in the throw producer**. Verify their seed/run provenance; copying an external CV into
either slot is not a substitute."*

Three of its four clauses are satisfied by the route above and need no amendment: both vectors are
**internally re-unfolded**, in the **same run**, at the **same fixed seed**, and nothing external
is copied in.

**The fourth — "in the throw producer" — carries one thing the other three do not, and it is
real.** Between `:369` and `:514` the producer loads 76 slabs, accumulates the flux and knob
inventories, and builds a `10,694²` block matrix: several GB allocated and freed between the two
calls. The estimator is not claimed deterministic — `omnifold_nn_core.py:203-204` says LightGBM at
these settings is *"**nearly** deterministic in `seed` alone"* — and its residual nondeterminism
comes from thread scheduling and reduction order, which process state can influence. **A tight
standalone loop removes exactly that intervening state.**

So the purpose is: **the null is measured under the producer's process conditions.** And the
direction matters. A standalone null plausibly measures a *smaller* difference than production
would, so:

- **For §3.3 condition 11b — auditability, reconstructing `r_null` from persisted operands — a
  standalone null is adequate, provided the process-state difference is disclosed in the
  receipt.** The obligation is that the operands exist and the ratio is reconstructible, and it is
  discharged by operands that are genuinely computed.
- **For `B`, a determinism BOUND — it is the wrong direction and must not be used.** An
  understated null would claim better determinism than production has. §3.7a already gates `B`
  separately and §6.4 requires it fixed before production; nothing here touches that.

**THE NARROW AMENDMENT, and it is one sentence:** permit the null operands to be produced by a
null-only entrypoint that calls the producer's own kernel on the producer's own bank at the same
seed and iteration count, executing both calls, **on condition that the receipt records the
absence of the producer's intervening process state and that the resulting `r_null` is carried as
a LOWER BOUND on the production null rather than as equal to it.**

That amendment is `Z_BUILD.md`'s to make. It changes no gate, declares no boundary, and leaves
`null_epsilon` withheld.

---

## 3. ESTIMATOR SETTINGS — recommended explicitly, and a claim of mine withdrawn

**⚠ I OVERCLAIMED, AND JOSEPH IS RIGHT TO SPLIT IT.** I wrote that pinning
`num_threads`/`deterministic`/`force_row_wise` *"changes `x_cv` itself, and therefore the support
mask, `nrep`, and every downstream covariance."* That conflates two different statements:

- **"Pinning changes the execution configuration."** True by definition, and it is what SPEC
  §3.7a means when it says pinning *"could make `B` a design property rather than a
  measurement"* — a pinned envelope has no between-envelope shift to bound.
- **"Pinning necessarily changes the central vector, the mask, and every covariance."**
  **NOT ESTABLISHED. It requires measurement and I did not have one.** Pinning constrains
  reduction order; whether the constrained result differs from an unpinned draw, and by how much,
  is unmeasured. It may equal one of them.

**And the available evidence argues against my version.** The perturbation at issue is the null
itself, `5.8223e-50` against a CV whose relative scale puts it near `1e-12`. Investigation 1
measured three nominal CVs spanning the bkgaware change — median relative difference
`6.76e-03`, roughly **nine orders of magnitude larger** — and all three produced *identical*
masks, symmetric difference zero. A mask that survived a `1e-3`-scale change moving under a
`1e-12` one would be surprising. That is an inference, not a measurement of this perturbation,
and it is stated as such.

**RECOMMENDATION: do NOT pin for this run. Produce the operands under the CURRENT, unpinned
configuration, and record the settings in force.**

Three reasons:

1. **The null being produced is a measurement of the existing configuration**, which is the
   configuration every archived product — including G — was built under. That is the number that
   makes `r_null` comparable to what exists.
2. **Pinning is a proposed NEW Z configuration.** A null measured under it would describe a
   configuration nothing else in the campaign shares, and it would read as `~0` by construction —
   which is a design property, not evidence about the estimator.
3. **It is reversible in the useful direction.** Operands from the unpinned configuration remain
   valid evidence about the unpinned configuration after a pinning decision; the converse fails.

### What transfers between the two configurations

| | transfers? |
|---|---|
| `r_null` measured unpinned → a bound on the pinned configuration | **NO.** Different envelope; pinning is expected to reduce it |
| `r_null` measured pinned → a bound on the unpinned configuration | **NO**, and this is the dangerous direction — it would understate |
| the support mask and `nrep` | **PROBABLY**, on the `1e-3`-vs-`1e-12` argument above — but **unmeasured**, and one cheap check settles it: compare the masks of the two `x_cv` draws |
| the operand SCHEMA and the persistence machinery | **YES**, fully — configuration-independent |
| provenance binding of bank, seed, iters | **YES** |

**So the recommendation is not "pin later"; it is "decide pinning on its own evidence, and do not
let this run be the thing that decides it."** If pinning is later adopted, these operands remain
a correct record of what the unpinned estimator did, and a second pinned pair would then be the
comparison — which is `r_cross`, Gap 1's quantity, not `r_null`.

---

## 4. RESOURCE BOUND

One CPU invocation, `ntasks=1`, `shared` queue, `constraint=cpu`.

| | figure | evidence class |
|---|---|---|
| upper bound | **≤ 0.37 CPU task-hours, 0 GPU** | **DERIVED** — job `56429334` ran the full combine *including* this null in 1,319 s at 32 cores; a null-only run is a strict subset (drops 76 slab loads, three `10,694²` assemblies, and the 343 M-call `SetBinContent` loop) |
| expected | **well under the bound, unmeasured** | the two unfolds are an unknown fraction of the 1,319 s and no timestamped line separates them |
| memory | `bank_uthrow_5d` is 26 GB on disk; request as the producer does | **TRANSFERRED** from `--mem=90G` in the combine launcher |

**≈ 0.07 % of R5's CPU ceiling.** No GPU. No slab reads.

---

## 5. WHAT THIS BUYS AND WHAT IT DOES NOT

**Buys:** §3.3 condition 11b's auditability — operands persisted on the full grid so `r_null` is
independently reconstructible, with bank, seed, iters, settings, revision and run id bound.

**Does not buy, and none of these is close:** `B` or `S`; a discharge of §6.4, which requires the
bound fixed *before* production; anything about between-envelope portability, which is Gap 1's
`r_cross`; or any acceptance whatever — `null_epsilon` is withheld, so `z_validator.assess_null`
returns `NOT ASSESSABLE` with reject conditions `4c` and `11` in every case.

**One thing it cannot settle in advance:** `z_build.py:519` requires the null mask to equal the
production CV's mask **elementwise**. Cardinality agreement is known (both 10,694); elementwise is
unmeasured and only the unfold settles it. If they disagree, the build refuses and that refusal is
itself the finding.
