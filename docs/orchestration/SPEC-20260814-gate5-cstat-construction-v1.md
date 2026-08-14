# SPEC — Gate-5 `C_stat` construction, v1

**Status:** SPEC, LIVE. **Author:** lane C (PET), owner of Gate 5 / P5B.1 / `C_stat`.
**Authorized by:** `OI-121`, Joseph's *"go ahead"* relayed by `personal-orchestrator` 2026-08-14.
**Companion machine contract:** [`nd-unfolding/pet/gate5_cstat_contract.json`](../../nd-unfolding/pet/gate5_cstat_contract.json)

**What this document is.** The single written specification that two builders who have never spoken
each implement independently, so their outputs can be compared element-wise. Builder 1 is lane B
(which owns the P5B assembly conventions). Builder 2 is a cold `codex` session. Comparator is D,
judge is `codex` background.

**What this document is not.** It contains **no implementation** — no covariance code, no snippets a
builder could paste. Lane C wrote the family and the extractor and deliberately kept covariance code
out of both (`extract_fullevent_replica.py:350,412`, `validate_gate5_extraction_family.py:194,260`,
`submit_gate5_extraction_r2_n50.sh:34` all assert `C_stat: None`). C authors the spec and does not
build, so that property is not eroded by the person who installed it.

**Ids in this document are prefixed `CSTAT-`** per `CLAUDE.md`'s namespace rule. `CSTAT-R*` are
requirements a builder must satisfy. `CSTAT-D*` are declarations the spec makes so a builder does not.
`CSTAT-O*` are open items that **return to Joseph** and that no builder may resolve in code.

> **TWO ESCALATIONS ARE OPEN AND BOTH ARE UPSTREAM OF BUILD.** `CSTAT-O1` (rank) and `CSTAT-O2`
> (whether this object is entitled to the name `C_stat` at all). `CSTAT-O2` was found while writing this
> spec and is, in C's judgement, the more serious of the two. Neither blocks *writing* a builder; both
> block *publishing* a number. Read them before starting.

---

## 0. Provenance of every number in this document

Every quantity below was measured from the published replica artifacts on
2026-08-14 ~05:00 PDT, on **14 of 50** members (the extraction array `56936015` was mid-flight). Scripts
are `$CLAUDE_JOB_DIR/tmp/{measure_bins,measure_family,spread_and_nominal,centring,flicker}.py`; their
outputs are quoted verbatim in the receipt
[`state/gate5-cstat-spec-measurements-20260814.json`](state/gate5-cstat-spec-measurements-20260814.json).

**Numbers marked `[N=14]` are provisional and MUST be re-measured at 50/50 before publication.** They
are quoted because the *decisions* they drive are stable under the remaining 36 members, and each
decision below says explicitly whether it is.

---

## 1. `CSTAT-R1` — WHAT QUANTITY IS COVARIED

**The array is the `xsec` key, and nothing else in the file.**

| property | value | how known |
|---|---|---|
| file, per member | `<root>/replicas/replica_<II>/extraction/GATE5_REPLICA_XSEC.npz` | launcher `sbatch_gate5_replica_extract_array.sh` |
| `<root>` | `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet/fullevent_cstat_n50` | `state/gate5-extraction-r2-active-56936015.json` |
| NPZ key | **`xsec`** | measured; `sorted(z.files)` in the receipt |
| shape | **`(15, 19)`** | measured on 14 of 14 |
| dtype | **`float64`** | measured |
| quantity | **d²σ / d`pT` d`p∥`** — a **DENSITY, not a bin-integrated yield** | `extract_fullevent_fps.py:459` |
| units | **cm² / nucleon / (GeV/c)²** | `total_xsec_2d` at `:561-565` multiplies by both bin widths to reach `cm²/nucleon` |
| schema string | `pet-fullevent-fps-gate5-replica-xsec-v1` | key `xsec_schema` |

**`CSTAT-R1a`** A builder MUST assert `xsec_schema == "pet-fullevent-fps-gate5-replica-xsec-v1"` and
refuse on mismatch. The nominal-path artifacts carry `pet-fullevent-fps-xsec-v1` — a different string
for a differently-produced object, and they are the files most likely to be picked up by a loose glob.

**`CSTAT-R1b` — the density trap, stated because it is silent.** Because `xsec` is a density, a
covariance built from it has units of cm⁴/nucleon²/(GeV/c)⁴ and is **not** the covariance of the
bin-integrated cross section. The two differ by `diag(w) C diag(w)` with `w = outer(Δpt, Δpp)` flattened.
Bin widths here span **0.07 → 25.5 GeV/c in `pT`** and **0.5 → 60 GeV/c in `p∥`**, so the two matrices
differ by more than three orders of magnitude in places. **The spec's object is the DENSITY covariance.**
A builder MUST record `width_weighting_applied: false` in its receipt so a downstream consumer cannot
mistake which one it holds.

## 2. `CSTAT-R2` — BINNING, and the flattening string

**Bin edges are read from the member file, never from `AGENTS.md`.** The source dump is the
**extended-FPS** grid, which is **not** the paper grid in `AGENTS.md:345-351`:

```
edges_pt        16 edges → 15 bins  [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
                                     0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50, 30.0]
edges_pparallel 20 edges → 19 bins  [0, 0.75, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
                                     6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0, 120.0]
```

`AGENTS.md` documents 14×16 = 224 paper bins. **The artifacts carry 15×19 = 285.** The extra edges are
the overflow/underflow extensions (`pT` to 30.0; `p∥` 0→0.75 and 60→120). **A builder that trusts the
documented paper grid produces a 224-cell object and every element of the comparison is misaligned.**
This is the single most likely way for the two builders to diverge, so it is stated first.

**`CSTAT-R2a`** A builder MUST verify `edges_pt` and `edges_pparallel` are **bit-identical across all
50 members** and refuse otherwise. Measured identical across 14 of 14.

**`CSTAT-R2b` — FLATTENING: pin the declared STRING, not a convention.**

```
bin_order = "pt-major row-major: cell = i_pt * n_pparallel_bins + i_pparallel"
```

This string is published in each member's `extraction_telemetry` and **five existing consumers already
fail closed on it** — `validate_pet_nominal_gate4.py:102,514`, `preflight_powered_closure.py:188`,
`acceptance_map_fullevent_fps.py:201`, `test_pet_nominal_gate4_validator.py:68` (located by D).
It is equivalent to NumPy C-order; verified by measurement, `F[0] == X[0].ravel(order="C")` on 14 of 14.

A builder MUST **assert the string** and MUST NOT infer order from the shape. Credit to D for the
reason, which is decisive: two builders disagreeing on C-order vs F-order produce covariances that are
**both symmetric, both positive-semidefinite, and both wrong**, and no structural check and no
element-wise comparison of two same-order builders can see it. Since `15 != 19` a transpose would be
caught by shape, but the *flatten* order would not be.

## 3. `CSTAT-R3` — REPLICA ORDERING, and how to prove you have 50 distinct members

**Ordering is by the `replica_index` scalar INSIDE each NPZ. Never by filename, never by glob order,
never by `readdir`.**

**`CSTAT-R3a`** For each member, read `replica_index` and `bootstrap_seed` from the file and assert
`bootstrap_seed == 50000 + replica_index` — the predeclared `gate5-cstat-n50-v1` policy, independently
enforced at `extract_fullevent_replica.py:443-446` and `train_fullevent_replica.py:319-321`.

**`CSTAT-R3b`** Assert `sorted(replica_index for all members) == list(range(50))` — i.e. **exactly 50
members, each index present exactly once**. This is the check that distinguishes "50 files" from "50
distinct replicas": a doubled symlink or a re-run leaving two copies passes a count and fails this.

**`CSTAT-R3c`** Assert the row order of the assembled `(50, D)` matrix is ascending `replica_index`, and
record that assertion in the receipt. Covariance is invariant to member permutation, so this cannot
change the matrix — it exists so that any **per-member** quantity the receipt publishes (residuals,
`n_replicas_reported` contributions, outlier ids) refers to the member a reader thinks it does.

**`CSTAT-R3d`** Assert `is_complete(path)` (the `atomic_write` marker) for every member.
**Known limit, not repaired here:** `atomic_write.is_complete` compares recorded size and
`int(st_mtime)` at **whole-second** resolution, so a same-size same-second rewrite is invisible to it
(lane C residual, carried in `state/gate5-family-complete-pass-20260814.json`). A marker is the only
integrity evidence these artifacts carry — **no receipt in this campaign is hashed against anything.**

**`CSTAT-R3e`** Assert the 50 members are mutually distinct in content, by `xsec` digest. Measured
14 of 14 distinct, and `total_sigma` 14 of 14 distinct.

## 4. `CSTAT-D1` — CENTRING: **the replica mean. Decided, not deferred.**

**The estimator is centred on the sample mean of the 50 replicas.**

Two reasons, the second decisive:

1. **Measured consequence.** Centring on the only 285-cell nominal-like artifact that exists inflates
   the trace by **6.0×** `[N=14]`:

   | | trace |
   |---|---|
   | mean-centred, 1/(N−1) | `1.848970e-76` |
   | nominal-centred, 1/(N−1) | `1.111802e-75` |
   | ratio | **6.013×** |

   The excess is **exactly** the offset term `N/(N-1)·‖mean − nominal‖²` = `9.269051e-76`, which equals
   `trace_nom − trace_mean` to all printed digits. That offset is a **bias**, not a statistical
   fluctuation: the replica mean sits **+7.56%** above that nominal in total cross section. Calling it
   variance would put a systematic shift inside the statistical component.

2. **The nominal alternative does not exist in quotable form.** The only 285-cell nominal artifact on
   disk is
   `nd-unfolding/pet/fullevent_diagnostic_nonquotable/NONQUOTABLE-DIAGNOSTIC.xsec.slurm-56527676.npz`
   — schema `pet-fullevent-fps-xsec-v1`, and **its own filename declares it non-quotable**. There is no
   Gate-5-schema nominal extraction. So nominal-centring is not a methodological option that was
   weighed and rejected; **it is unavailable from quotable evidence.**

**`CSTAT-D1a`** A builder MUST NOT read that non-quotable file. It is named here so that a builder who
finds it by glob knows to refuse, which is the opposite of the usual reason for naming a path.

**`CSTAT-D1b`** Centring on a point other than the sample mean would raise the rank ceiling from
`N−1` to `N` (measured: 13 → 14 at `[N=14]`), and **the extra direction is the bias direction.** Anyone
tempted to prefer nominal-centring for the extra rank is buying a rank whose content is the offset in
`CSTAT-O2`. Stated so the temptation is refused in writing rather than in review.

## 5. `CSTAT-D2` — NORMALIZATION: **1/(N−1). `ddof=1`.**

Unbiased for a covariance about an **estimated** mean, which is what `CSTAT-D1` makes this. `1/N` would
bias every element low by a factor `49/50` = **2.0%** — small, systematic, in the same direction for
every element, and therefore exactly the kind of error that survives an element-wise comparison of two
builders who both chose `1/N`. Declared here so neither has to choose.

## 6. `CSTAT-D3` — THE REPORTING DOMAIN, and the replica-dependent mask

**The reporting mask is drawn per replica. This is measured, not hypothetical.**

Mechanism, found by D: `extract_fullevent_replica.py:190-196` monkey-patches `completeness_2d` so the
replica's **signal Poisson factor multiplies the weights inside the completeness computation**;
`extract_fullevent_fps.py:517-518` then hard-zeroes unreported cells
(`reported = comp > 0; xsec = np.where(reported, xsec, 0.0)`). So `comp > 0` is a **per-replica draw**,
and a thinly-populated cell can be reported in one member and hard zero in another.

**Lane C measured the occurrence on the 14 published members. It occurs:**

| `n_replicas_reported` (of 14) | cells |
|---|---|
| 14 (all) | **259** |
| 13 | 2 |
| **9** | **1** |
| 0 (never) | 23 |

`n_cells_populated` in the telemetry varies **260 / 261 / 262** across members, so the artifacts already
record the flicker. **One cell is reported in only 9 of 14 draws** — in that cell, roughly a third of
the across-replica spread is the mask switching off, i.e. hard zeros, **not fluctuation of the cross
section.** D's point stands exactly as put: both builders, given identical member vectors, compute the
identical wrong variance there and agree with each other perfectly. **Element-wise agreement has no
power over this**, which is why it is declared here and not left to code.

**The declaration:**

- **`CSTAT-D3a` — CONSTRUCT over the UNION**: all cells reported in **≥ 1** member. `[N=14]` that is
  **262** cells. The union is used rather than the intersection because the intersection *silently
  deletes* cells and its deletion set depends on `N`, so the published dimension would change with the
  member count — indefensible in a technote.
- **`CSTAT-D3b` — PUBLISH per-cell `n_replicas_reported`**, an integer array of length `D`, in the
  output contract. Cheap now, expensive to retrofit; without it nobody downstream can distinguish a
  genuinely quiet cell from a flickering one. D asked for this and it is adopted verbatim.
- **`CSTAT-D3c` — the QUOTABLE sub-block is `n_replicas_reported == 50`.** Cells with
  `n_replicas_reported < 50` are **present in the published matrix, flagged, and excluded from any
  downstream inversion or χ², with their cell list recorded by index.** They are not deleted, because
  deleting them would hide that the question was ever asked.
- **`CSTAT-D3d` — the answer is recorded either way.** The receipt MUST publish the flicker cell count
  **even when it is zero**, as an explicit `0` with the union and intersection sizes alongside. A zero
  result must not let the question disappear — the whole point of `CSTAT-D3` is that the *absence* of
  flicker at 50 members would itself be a finding, and an omitted field cannot state it.

**`CSTAT-D3e`** The 23 never-reported cells (`n_cells_no_denominator = 23`, matching exactly) carry
**identically zero variance** and are structurally singular directions. They are retained in the
published `D`-dimensional object for grid alignment and flagged; they are not evidence of precision.

**Out of scope and explicitly untouched:** the acceptance-supported vs model-dependent **tiering**
decision of `OPEN_ITEMS:430-438`. The extractor's own telemetry says
`reporting_mask_is_not_the_tiering_decision`. This spec inherits the reporting mask and decides
nothing about tiering.

## 7. `CSTAT-O1` — RANK. **OPEN. Returns to Joseph. No builder may resolve this.**

**Measured, at the dimension that matters:**

| domain | `D` | rank ceiling at `N=50` | singular by |
|---|---|---|---|
| full grid | 285 | 49 | 5.82× |
| union / reported (`CSTAT-D3a`) | **262** | **49** | **5.35×** |
| intersection | 259 | 49 | 5.29× |
| nominal's reported count | 262 | — | — |

The rank deficit was raised against 285; the mediator correctly asked for the count against the
**reported** dimension, since that is the number that decides whether it is a problem. **Lane C has now
measured it and it does not change the answer: 262 ≫ 49.** The matrix is singular against every
candidate domain, by a factor above five. `[N=14]`, `numpy.linalg.matrix_rank` on the 14-member
mean-centred matrix returns exactly `13 = N−1`, confirming the ceiling binds tightly and is not slack.

**What is therefore true:** every downstream step that **inverts** `C_stat` — χ², a GoF, a profile
likelihood, any weighted fit — needs a **declared** treatment.

**But the ask is narrower than that, and `OI-122` is why.** `OI-122` records that **two agents have
already re-opened the rank question and escalated it to Joseph as novel**, when *"rank is not the
criterion … the rank-deficient GoF treatment is already disclosed under `OI-29`."* This spec is **not a
third instance.** `OI-29` covers a **different object** — the **1431-bin** 3D-plus covariance, owned by
*collaborators*, awaiting **endorsement of a treatment that already exists.** The object here is the
**285-cell / 262-reported full-event Gate-5 `C_stat`**, whose dimension was **unknown until measured
today** and which has **no declared treatment of its own.**

So the single question returning to Joseph is: **does `OI-29`'s already-disclosed treatment extend to
this 262-cell object, or does this object need its own declaration?** If it extends, `OI-91` closes by
reference and nothing new is decided. If it does not, candidates exist (rebinning to ≤ 49 cells; a
shrinkage or diagonal-loading estimator with a declared and justified regularizer; restricting inference
to a declared low-dimensional projection; raising `N`; using only the diagonal and declaring
correlations unmeasured) — **this spec names them and chooses none.** Either way the treatment is not
decided inside a script, in a builder, or in this document.

**`CSTAT-O1a`** A builder MUST produce the singular matrix as specified, MUST NOT regularize,
condition, pseudo-invert, shrink, or diagonal-load it, and MUST record `rank_treatment: "UNDECLARED —
see CSTAT-O1"` in its receipt. A builder that silently returns an invertible matrix has resolved a
question reserved for Joseph, and that is the specific failure this clause exists to prevent.

## 8. `CSTAT-O2` — **IS THIS OBJECT ENTITLED TO THE NAME `C_stat`? OPEN. Returns to Joseph.**

**This was found while writing this spec, it is not in anyone's dispatch, and C considers it more
serious than `CSTAT-O1`.**

The across-replica spread of the extracted cross section is **~90× larger than counting statistics can
account for**:

| quantity | value |
|---|---|
| relative sd of `total_sigma` across members `[N=14]` | **4.478 %** |
| (max − min) / mean `[N=14]` | 18.187 % |
| median abs deviation / mean `[N=14]` | 1.676 % |
| Poisson expectation, `n_data = 4,116,128` | **0.0493 %** |
| Poisson expectation, `n_sig = 49,152,885` | 0.0143 % |
| per-cell relative sd, median / max `[N=14]` | 0.151 / 0.794 |

A counting-only spread on an integrated quantity over 4.1M data events is **~0.05%**. The measured
spread is **4.5%**. The distribution is heavy-tailed rather than uniformly wide — median deviation
1.68% with `replica_08` at **+9.96%** and `replica_09` at **−8.23%** — which is itself a shape that
counting statistics does not produce.

**And the network is not seeded.** `grep` for `set_seed` across `nd-unfolding/` and `omnifold_nn/`
returns **nothing**; no `tf.random.set_seed`, no `np.random.seed`, no `TF_DETERMINISTIC_OPS` in
`train_fullevent_replica.py` or the extractor. The `bootstrap_seed` plumbing that *is* present
(`:150-173`, `:315-321`) governs the **draw and its provenance validation**, not weight
initialization, batch shuffling, or GPU reduction order.

**Consequence:** each member differs from every other in **two** ways at once — its Poisson draw *and*
its free-running training stochasticity. The published matrix is therefore
**`C_stat` + `C_train` + cross terms**, and **the two are not separable from this family**, because no
two members share a draw and no member was repeated under a different initialization. Naming that
matrix `C_stat` asserts a decomposition the family cannot support. This repo has a name for the shape —
`BEN-149`, a field named for one thing carrying another.

C is **not** claiming which term dominates, and will not: an alternative explanation is genuine
amplification of the data fluctuation by the iterative unfolding, which would be legitimately
statistical and would itself be a significant result. **Both readings are consistent with every number
above, and distinguishing them is one measurement, not an argument:**

**`CSTAT-O2a` — the discriminating test.** Re-**train** one replica index twice at the **same**
`bootstrap_seed`, then extract both. Extraction is deterministic given weights, so a repeat of
extraction alone measures nothing — **the repeat must be of training.** Non-zero spread between that
pair is `C_train` with the draw held fixed, measured directly and at the cost of a couple of
14-minute tasks. A small pair (3–5 same-seed retrains) bounds `C_train` well enough to state what
fraction of the published matrix is not statistical.

**This does not block writing the builders** — the construction is identical whatever the matrix turns
out to be entitled to be called. **It blocks publishing the number under the name `C_stat`,** and it
should be settled before the technote quotes it.

## 9. `CSTAT-R4` — OUTPUT CONTRACT

One NPZ, written with `atomic_write.atomic_savez_compressed(..., overwrite=False, fsync=True,
mark=True)`, plus one JSON receipt published **last**. Builders write to **separate** paths so the
comparison has two independent objects:

```
<root>/cstat/BUILDER_<B1|B2>/GATE5_CSTAT.npz        + .done marker
<root>/cstat/BUILDER_<B1|B2>/GATE5_CSTAT_RECEIPT.json
```

| key | dtype | shape | meaning |
|---|---|---|---|
| `cstat_schema` | str | scalar | **`pet-fullevent-fps-gate5-cstat-v1`** |
| `C` | float64 | `(D, D)` | the covariance, density units (`CSTAT-R1b`) |
| `mean` | float64 | `(D,)` | the centring vector actually used |
| `n_members` | int64 | scalar | **must be 50** |
| `D` | int64 | scalar | cells in the constructed domain |
| `cell_index` | int64 | `(D,)` | flat cell ids into the 285-cell grid, `CSTAT-R2b` order |
| `n_replicas_reported` | int64 | `(D,)` | per-cell, `CSTAT-D3b` |
| `quotable_mask` | bool | `(D,)` | `n_replicas_reported == 50`, `CSTAT-D3c` |
| `replica_index` | int64 | `(50,)` | ascending, `CSTAT-R3c` |
| `bootstrap_seed` | int64 | `(50,)` | row-aligned to `replica_index` |
| `edges_pt`, `edges_pparallel` | float64 | `(16,)`, `(20,)` | copied from the members |
| `bin_order` | str | scalar | the pinned string, `CSTAT-R2b` |
| `member_xsec_sha256` | str | `(50,)` | per-member `xsec` digest, row-aligned |
| `centring` | str | scalar | `"replica_mean"` |
| `normalization` | str | scalar | `"1/(N-1)"` |
| `width_weighting_applied` | bool | scalar | `false`, `CSTAT-R1b` |
| `rank_treatment` | str | scalar | `"UNDECLARED — see CSTAT-O1"` |

**`CSTAT-R4a`** `C` MUST be exactly symmetric — `C == C.T` bitwise, not within tolerance. Enforce it by
construction, not by symmetrizing a nearly-symmetric result: `(F−mean).T @ (F−mean)` is symmetric up to
floating-point summation order, and a builder that symmetrizes is hiding whether its two triangles
agreed. Report `max|C − C.T|` as a number.

**`CSTAT-R4b`** All entries finite. `diag(C) >= 0`. Eigenvalues computed and reported; the smallest
will be zero or numerically negative and **that is expected** (`CSTAT-O1`) — report it, do not clip it.

**`CSTAT-R4c`** No overwrite, no clobber, marker written last, receipt published last.

## 10. `CSTAT-R5` — RECEIPT INGREDIENTS

Per [`CONVENTION-receipt-ingredients.md`](CONVENTION-receipt-ingredients.md) (BEN-077): **every derived
quantity ships its ingredients, enough that the reported numbers can contradict each other.** A
verdict-only receipt is unfalsifiable. Required, at minimum:

1. **Inputs:** all 50 member paths, their `xsec` sha256, their `replica_index`/`bootstrap_seed`, and the
   `is_complete` result per member.
2. **The centring vector** `mean`, and separately `total_sigma` **per member** — so a reader can
   recompute the mean and the sd independently of `C`.
3. **`trace(C)`, and `diag(C)` in full.** `trace` must be re-derivable from `diag`.
4. **The offset term** `‖mean − x‖²·N/(N−1)` against any comparison point the receipt mentions, so the
   `CSTAT-D1` decision stays auditable rather than becoming a claim. Its exact identity
   (`trace_alt − trace_mean`) is the check.
5. **`n_replicas_reported`** with union size, intersection size, flicker count (**even if 0**), and the
   flickering cell ids.
6. **Rank:** `numpy.linalg.matrix_rank(C)`, the full eigenvalue spectrum, and `D`. `rank <= 49` must be
   stated as an expectation that was checked, not discovered.
7. **Code identity:** sha256 of the builder script, and of every module it imports from this repo.
8. **`max|C − C.T|`** as a measured number.
9. **The three code digests of the producing extraction**, copied from the member receipts:
   `replica_extractor_sha256`, `gate4_pinned_nominal_extractor_sha256`, `loader_sha256`.

**`CSTAT-R5a` — source identity.** Cite `state/gate5-source-npz-verified-20260813.json` and the
recomputed `fa6b3463…` in `state/gate5-family-complete-pass-20260814.json`. **Do NOT quote
`inputs_sha256` out of a replica artifact as verified provenance** — `train_fullevent_replica.py:112`
copies a claim into a field named for a measurement (`BEN-149`, `OI-57`/`OI-58`), and that line is
**deliberately unrepaired**, riding the next launch with a CODE_ROOT sync.

**`CSTAT-R5b`** `artifact.completion_marker_valid` in the member receipts is a **hardcoded producer
literal** (lane C's `OI-66`) and MUST NOT be read as evidence. Call `is_complete` yourself.

## 11. Out of scope — named explicitly

A builder that does any of these has exceeded the spec:

1. **No inversion, pseudo-inversion, regularization, shrinkage, diagonal loading, or conditioning.** `CSTAT-O1a`.
2. **No χ², GoF, p-value, or fit.** This deliverable is a covariance and its receipt.
3. **No `C_syst`, no other uncertainty component, no combination with any.** `C_stat` alone, one of five.
4. **No tiering decision** (`OPEN_ITEMS:430-438`). §6.
5. **No rebinning, no projection to the 224-cell paper grid, no width-weighting.** `CSTAT-R1b`, `CSTAT-R2`.
6. **No promotion, no Gate-5 sign-off, no ledger promotion, no `VALIDATION_LEDGER` entry.** Construction
   is not promotion; `FAMILY_COMPLETE_PASS` was the completeness gate and this is the next separate step.
7. **Do not touch `/pscratch/sd/j/josephrb/gate6traj-reconcile-56847059`.** It is `GATE5_CODE_ROOT`, it
   is **named for a different, already-complete job**, and it therefore looks disposable and is not.
   No clean, no pull, no write, no `git` operation inside it.
8. **No repair of `train_fullevent_replica.py:112`**, and no re-use of the withdrawn
   "it would break `GATE5_EXPECTED_TRAIN_DRIVER_SHA`" reason — the pin floats by design.
9. **No `scancel`, `scontrol update`, or resubmission** of `56936015` / `56936016`.
10. **Do not construct anything from a partial family.** `CSTAT-R3b` — exactly 50, each index once.
    The extraction array was at 14/50 when this spec was written; **the spec is written during the wait
    precisely so that no one is tempted to start early.**

## 12. Preconditions before either builder starts

| # | precondition | state 2026-08-14 ~05:00 PDT |
|---|---|---|
| 1 | extraction array `56936015` terminal at 50/50 | **NOT MET** — 14 COMPLETED, 1 RUNNING, 35 PENDING |
| 2 | family validator `56936016` reports `GATE5_EXTRACTION_FAMILY_COMPLETE_PASS`, exactly 50/50 | **NOT MET** — PENDING on `afterany:56936015` |
| 3 | `[N=14]` numbers in this spec re-measured at 50/50 | **NOT MET** |
| 4 | `CSTAT-O1` rank treatment declared by Joseph | **OPEN** — blocks publication, not build |
| 5 | `CSTAT-O2` naming settled, or `CSTAT-O2a` run | **OPEN** — blocks publication, not build |

Preconditions 1–3 gate **construction**. 4–5 gate **publication**. Builders may be written and their
harnesses tested against fixtures while 1–3 are outstanding; nothing may be constructed from the
partial family.
