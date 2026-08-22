# PROVENANCE — declaration (v) of the N-D χ² protocol, for the scalar-5D covariance blocks

**Filed 2026-08-22 by the standard-P4 lane, acting as the scalar-5D adoption / statistics owner on
Joseph's ruling 10 of 2026-08-22.** Measured against
`HEAD = 064496cd6b3435d4da47f280d04cf195b7ace893`, branch `standardp4-declaration-v-provenance`.

> **Ruling 10, verbatim, and it is the whole of my authority here:** *"Assign the remaining
> declaration-(v) work to the standard-P4 lane, acting as the scalar-5D adoption/statistics owner.
> Its scope is to record, for each 5D sample-covariance block, ensemble size, normalization
> convention, effective inversion dimension, and finite-ensemble treatment. This assignment
> authorizes record/provenance completion only—not adoption or an uncertainty-model change."*
> Recorded at [`DECISION-20260822-joseph-b1-lift-and-clause-c.md`](DECISION-20260822-joseph-b1-lift-and-clause-c.md).

**What this document is not.** No covariance was loaded, modified, projected or inverted. No Hartlap
or other debiasing factor is applied or recommended here — Joseph accepted *disclose, do not correct*
(ruling 11). Nothing here adopts anything: per `AGENTS.md`, every corrected scalar-5D covariance
candidate remains `QUARANTINED`, and this record does not move that. **No `.tex` file is edited by
this commit**; where note prose must change, §7 records the required change and who should make it.

**On the filename date.** The assignment suggested `20260823`. The measured date is 2026-08-22
(`HEAD`'s committer date is `2026-08-22T01:47:34-05:00`; `date -u` at filing is
`2026-08-22T14:54Z`). A provenance record dated a day into its own future is a defect in exactly the
class this campaign files, so it is named for the day it was measured.

---

## 1. Bottom line, before the table

**Three of the four declaration-(v) fields are satisfiable today for every 5D block. One is not, and
the one that is not is `p`, which cannot be satisfied by any record because no 5D χ² exists to have
truncated anything.**

**The briefed gap has moved, and the direction is favourable.** The assignment (and `OI-137`'s row,
and `BRIEF-20260822-oi137` §7b) states that `N = 160` *"exists only as a hardcoded constant at
`nd-unfolding/receipt_candidate_stamps_5d.py:107`"*. **That was true of the six roots it measured and
is no longer true of the construction path.** Two things falsify it, both dated:

1. `unified_throw_cov.py:388,540` **recounts and stamps** the ensemble: `T = X.shape[0]` from the
   concatenated slabs, written as `TParameter("int")("n_throws", T)`. Both throw roots carry
   `n_throws = 160` present-with-value in the construction-contract receipt.
2. `adopt_unified_5d.py:198-204` **propagates it onto the adopted product** as `upstream_n_throws`,
   and has done since 2026-08-11. The 2026-08-12 stamped candidate arms carry
   `upstream_n_throws = 160`, measured. The six roots the briefed claim rests on were all written
   on 2026-07-14 or 2026-08-07 — i.e. **before that writer changed** — and the writer's own comment
   at `:180-190` says so in as many words.

The writer's key is an **f-string** (`f"upstream_{key}"`), which is why a literal grep for
`upstream_n_throws` over `*.py` returns readers only and no writer. That is the same
literal-matcher defect `mii_root_payload_classes.py:200-210` already records against a different
count. My own first search hit it; it is noted here so the next reader does not conclude from a null
grep that nothing writes the key.

**What survives as a real gap is a different block.** `C_stat` and `C_ML` carry **no ensemble-size
key on any artifact and are covered by no receipt** — `combine_cov_nd.py` writes one `TH2D` and not
one scalar. Their `N` exists only as an `--expected-ids` range in the launcher. §6.

---

## 2. Which object — because "the 5D candidate" is a definite description, not a citation

Three distinct 5D covariance families are in play, they have **different** declaration-(v) fields,
and the note's (v) rationale paragraph names two of them in adjacent sentences.

| family | artifact | what it is | where its (v) fields come from |
|---|---|---|---|
| **T** the throw roots | `uq_5d/unified_throw_cov_5d.root` (`sha256 038c6132…`), `uq_5d/unified_throw_cov_5d_fluxfix_20260806_full160.root` (`4cb02ae7…`) | the `N = 160` joint-throw sample covariance itself, plus its block-sum and cross terms | stamped in the file: `n_throws = 160` |
| **A** the adopted roots | six roots enumerated in `receipt_construction_contract_5d.json`; and the 2026-08-12 stamped arms `stamped_bkgaware_{mean,cv}centered_20260812.root` (`4f168e83…`, `dbcd5359…`) | `C_syst + C_stat + C_ML`, **diagonally inflated** toward T — see §3 | six older roots: nothing. 08-12 arms: `upstream_n_throws = 160` |
| **P** the P4 candidate | `std_final5_candidate.root` (`sha256 602bbcf2…`, 42 326 583 908 bytes) | the audited block-sum candidate; **the only 5D object whose rank has ever been measured** | product audit, §5 |

**The note's `\texttt{app\_statmethods.tex}:665-667` worked example pairs `N=160` with "the
unified-throw 5D candidate".** Read as family **T** that is exact. Read as family **A** — which is
what the `_uthrow` filenames and the word *candidate* both suggest — it is wrong, because in **A**
the 160-throw ensemble is not a block of the sum at all (§3). The example is illustrative and no
quoted number depends on it, so this is a **naming** defect, not an arithmetic one. Recorded in §7.

**All artifact-level facts below are read from committed ROOT-reading receipts, not from the ROOT
files.** `*.root` is gitignored (`.gitignore:2`) and no 5D `.root` exists in this checkout; the
payloads are cluster-side. Each receipt's own measurement date is given, because a receipt is a
snapshot and the writers have moved under two of them.

---

## 3. The block decomposition, proved rather than asserted

The identity is **executable, not prose**, and is checked at `1e-6` by a prover:

```
p4_build_components.py:120   P.prove_identity(Csyst_total, syst_sum, 1e-6, "C_syst == sum(all per-band)")
p4_build_components.py:124   P.prove_identity(Ccomb_total, Csyst_total + C_stat + C_ml, 1e-6,
                                              "C_combined == C_syst + C_stat + C_ML")
```

and independently re-measured by the 5D product audit, which reports
`C_total = C_syst + C_stat + C_ML` at Frobenius-relative `6.681166920728552e-17`.

**The adoption step is not a fourth block.** `adopt_unified_5d.py:13-15` (docstring) and `:143-144`
(code):

```
g_i = sqrt( max(sigma_uni_i^2, sigma_block_i^2) ) / sigma_block_i   >= 1
C_new = C_comb + (g_i g_j - 1) * C_vert          # C_vert = sum of the 13 VERT_BANDS, :42,:130
```

So the `N = 160` ensemble enters family **A** **only through the per-bin diagonal** `sigma_uni_i`
— never as a matrix. `C_unified` is not summed into anything. This is the single most important
structural fact for declaration (v) on the adopted product, and it is why "the 160-throw sample
covariance is a block of the adopted sum" would be false if anyone wrote it.

---

## 4. Declaration (v), per block

`p` is the **effective dimension actually inverted after truncation**. It is `—` for every row for
one reason given once in §5: nothing inverts a 5D covariance, so no truncation has been chosen.

### 4a. `C_syst` — 44 bands plus a normalization band. Only ONE of them is a sample covariance.

Per-band `N` is read from the artifact bank by
[`nd-unfolding/uq_5d/receipt_cause1_endpoint_census_5d.json`](../../nd-unfolding/uq_5d/receipt_cause1_endpoint_census_5d.json)
(`written_at_utc 2026-08-17T08:15:39Z`, `positive_control.all_targets_reproduced: true`). Its
arithmetic closes exactly: `42×2 + 3 + 100 = 187 = census.n_files_grouped`, and
`n_files_matched_glob = 188` less the one CV file that matches no band.

| block | `N` | convention | `p` | finite-ensemble treatment | citation |
|---|---|---|---|---|---|
| 42 × two-endpoint knob bands | **2** each | biased `1/N` | — | **none, and none applicable** — a `±1σ` endpoint pair is a deterministic rank-1 outer product with no sampling noise | `census.summary.n_pm_pair_bands = 42`, `per_band[*].n = 2`, `pair_bands_missing_an_endpoint: []`; estimator `analyze_universes_5d.py:220` |
| `2p2h` | **3** | biased `1/N` | — | **none applied**; the receipt does not classify it random-vs-deterministic, so "none applicable" is *not* claimed here | `census.summary.non_pair_bands.2p2h = 3` |
| `Flux` (PPFX) | **100** | biased `1/N` | — | **none applied.** The one genuine multiverse draw in `C_syst` | `census.summary.non_pair_bands.Flux = 100`, `flux_exactly_100_contiguous: true` |
| `__Normalization_flat` | **n/a** (`per_band.n = null`) | n/a | — | **none, and none applicable** — `np.outer(v, v)` with `v = 0.014 · CV`, deterministic rank-1 | `analyze_universes_5d.py:229-232`; `--add-norm 0.014` at `sbatch_finalize_5d_bkgaware_gpu.sh:204` |

**Convention citation, corrected against the operand I was given.** The assignment cites
`nd-unfolding/uq_math.py:104` for the 5D MAT bands. `uq_math.py:104` is
`return (Z.T @ Z) / X.shape[0]` and *is* biased `1/N`, but **`analyze_universes_5d.py` does not
import `uq_math`** — it computes `cov = (Z.T @ Z) / D.shape[0]` inline at `:220`. Same convention,
**different line**, and a reader who checks only `uq_math.py:104` has not checked the code that
built `C_syst`. `uq_math.py:104` *is* the right citation for the joint throws (§4c), reached through
`unified_throw_cov.py:389 → joint_throw_covariance → mat_covariance`.

### 4b. `C_stat` and `C_ML` — the two blocks with a real record gap

| block | `N` | convention | `p` | finite-ensemble treatment | citation |
|---|---|---|---|---|---|
| `C_stat` (5D bootstrap) | **100** | **unbiased `1/(N−1)`** | — | **none applied** | `sbatch_finalize_5d_bkgaware_gpu.sh:167` `--expected-ids 1-100`; estimator `combine_cov_nd.py:20` `C=(Z.T@Z)/(Xr.shape[0]-1)` |
| `C_ML` (5D seedscan splits) | **24** | **unbiased `1/(N−1)`** | — | **none applied** | `sbatch_finalize_5d_bkgaware_gpu.sh:168` `--expected-ids 1-24`; same estimator line |

`N` here is **enforced, not merely declared**: `--expected-ids` is passed to
`replica_manifest.load_replica_manifest`, which raises on `got != expected_ids` and separately on
duplicate ids (`replica_manifest.py:41-47`). A partial replica set refuses rather than combining
what it has, and the launcher comment at `:163-165` says that is the point. The same two ranges
appear at `run_budget_5d.sh:15,17` and `sbatch_combine_5d_budget.sh:14,16` — three concordant
invocations, no disagreement found.

**But `N` for these two blocks reaches no artifact.** `combine_cov_nd.py:23-26` opens the output
`RECREATE`, writes exactly one `TH2D`, and closes. No `TParameter`, no `TNamed`. There is therefore
**no key that could carry `N`**, and no receipt in this tree reads `uq_cov_stat_5d.root` or
`uq_cov_mlsplit_5d.root` for one. The 5D product audit hashes both as declared inputs
(`891732011 B / sha256 6580016f…` and `892078834 B / 27b2e456…`) but records no ensemble size.

### 4c. The unified-throw ensemble — a diagonal input, not a block

| object | `N` | convention | `p` | finite-ensemble treatment | citation |
|---|---|---|---|---|---|
| joint throws (family **T**) | **160** | **biased `1/N`** | — | **none applied** | recount `unified_throw_cov.py:388`; estimator `:389 → uq_math.py:104`; stamp `:540`; receipt `throw_roots.*.parameters.n_throws = {present: true, value: 160}` |
| its contribution to family **A** | 160, via `sigma_uni` only | see §3 | — | **none applied**; the `max()` in `g_i` is a one-sided selection on a noisy per-bin variance, **raised here and not resolved** | `adopt_unified_5d.py:13-15,108-113,143-144` |

**Corroboration of 160, from a second and independent route**, as briefed and here re-measured:
`receipt_construction_contract_5d.json` `slab_census.throw_slabs_sb` gives `n_throws_union = 160`
over `n_files = 40` slabs, `throws_contiguous_from_zero: true`, `throws_min 0`, `throws_max 159`.

**One census figure looks like a contradiction and is not.** The same receipt's
`j28_union_rescaled_half` reports `n_throws_union = 120` over 30 slabs under a directory named
`rescaled_20260806_full160`. That is the **flux-rescaled subset**: `throw_slabs_sb` has 30
`flux_normalized`-unstamped slabs and 10 stamped ones, so `120` rescaled `+ 40` already-normalized
`= 160`. The key's own name says `half`. Recorded because "a directory called full160 whose slabs
count 120" is exactly the shape of a real defect and will be re-found by the next reader.

---

## 5. The effective inversion dimension `p` — why every row above is `—`

**No 5D χ², likelihood or pull is quoted anywhere, so no 5D covariance has ever been inverted or
truncated in a quoted result.** `RANK-AND-INVERSION-20260810.md` §3 enumerates every `χ²/ndf` in
`docs/analysis-note/` and traces each to its covariance; not one is 5D. `sec_3d.tex:181-183`
withholds the 3D generator significances outright — *"no 3D generator $\chi^{2}$, $p$-value or
significance is quoted here"* — and there is no 5D counterpart to withhold.
`BRIEF-20260822-oi137` §4's 19-site inversion inventory contains no 5D site. **`p` is therefore not "unrecorded" — it does not yet exist**, and declaration (v) is
satisfied for it by that statement rather than by a number.

**The only rank ever measured on a 5D object**, re-measured for this record from the receipt itself
rather than quoted from the summary:

```
git show evidence/prepublication-2026-08-20-0b329e8a:\
docs/orchestration/runs/standard-p4-verifier/20260810T0600Z-product-audit-5d-verdict.json
  -> "numerical_null_count=10431; effective_positive_rank=263; numerical condition=infinity;
      effective-nonnull condition=29971212.710634403"
```

on `std_final5_candidate.root` (family **P**), `utc 2026-08-10T03:00:56Z`, verdict `CORRECT`.

**Two citation facts about that receipt, both load-bearing.**

1. **`RANK-AND-INVERSION-20260810.md:16` cites it as `runs/standard-p4-verifier/…`. The real path is
   `docs/orchestration/runs/standard-p4-verifier/…`** — the `docs/orchestration/` prefix is missing.
   `PROVENANCE-DEBT-20260810-standard-p4.md:142` repeats the same truncated path.
2. **Neither path resolves on `main`.** The file is absent from the working tree at `064496cd` and
   is not gitignored (`git check-ignore` exits 1). It is reachable through the pushed evidence tag
   `evidence/prepublication-2026-08-20-0b329e8a`, which is the sanctioned pre-freeze discovery route
   in `CLAUDE.md`, and through 30-odd other refs. **So this is compaction working as designed plus a
   stale citation, not lost evidence** — but a reader following the note's `(v)` pointer chain
   (`app_statmethods.tex:654` → `RANK-AND-INVERSION-20260810.md:16` → that path) hits a
   `No such file or directory` today. Recorded in §7 for the doc's owner.

**Per-block ranks do not exist and the audit says so in its own scope section:** *"A separate full
eigenspectrum for each of the 45 recorded systematic component matrices"* is listed under
`what_this_audit_does_not_cover`. So even if a `p` were chosen tomorrow, the per-block contributed
ranks that a block-wise treatment would need are unmeasured.

---

## 6. What is NOT satisfiable from the artifacts today, and what would change it

Ordered by how much it costs to fix. **None of these is a blocker on anything currently runnable** —
the B1 pause is lifted but no member is runnable, so nothing here is racing a submission.

| # | not satisfiable | why | what would make it so |
|---|---|---|---|
| 1 | **`N` for `C_stat` and `C_ML`, from the artifact** | `combine_cov_nd.py` writes one `TH2D` and no scalar, so the products have no key that could hold it; no receipt reads them for one | Two lines in `combine_cov_nd.py` beside the existing write: `TParameter("int")("n_replicas", Xr.shape[0])` and the id range. **A recount, not a restatement** — `Xr.shape[0]` is the array actually reduced. Applies to future products only; the existing ones cannot gain a key without a rewrite |
| 2 | **`N` on the six pre-2026-08-11 adopted roots** | they predate `adopt_unified_5d.py`'s propagation block; measured absent in `receipt_construction_contract_5d.json` | Nothing, for those bytes. The path is already fixed for anything rebuilt: the 08-12 arms carry `upstream_n_throws = 160`. **Recommend retiring the six as (v)-citable rather than backfilling them**, consistent with ruling 12's *"marker backfill remains unauthorized"* |
| 3 | **Per-band `N` for `C_syst`, from the adopted artifact** | the combined intermediate has carried `n_universes` (a whole-sweep **file count**, 188) only since remedy (A) at `5afb7947`, 2026-08-19; the adopt step does not forward it, and `STAMPED_SCALAR_KEYS` (`mii_adopt_unified_5d_stamped.py:172-179`) is six **seed**-identity keys with no ensemble-size member | Add the count to that tuple — but its own comment warns *"ADDING A KEY HERE IS A TRIGGER, NOT A ONE-LINE CHANGE"* and `Q1_TheIntReaderGuardIsVALUE_BASED` fails if `LEG_IDENTITY_KEYS` changes. **Price it before calling it cheap.** Meanwhile the per-band census receipt (§4a) *is* artifact-read and *is* committed, so (v) is satisfiable for `C_syst` **by receipt**, just not by the product |
| 4 | **`p`, for every block** | no 5D χ² exists (§5) | It becomes answerable only when a 5D χ² is specified. Declaration (v) is satisfied today by the explicit statement that no truncation has been chosen |
| 5 | **Per-block contributed rank** | explicitly outside the 5D product audit's scope | A per-component eigenspectrum run. **Not proposed**: it is a measurement on a quarantined object, and nothing consumes it |
| 6 | **Whether `2p2h`'s `N = 3` is a random ensemble** | the endpoint census records the count and excludes it from the counterfactual as *"N != 2"*, but classifies it no further | Read the three universe names out of the bank. Cheap, and it is the only row in §4a whose "none applicable" I declined to assert |

**Finite-ensemble treatment, the fourth field, is uniform and needs no table: NONE IS APPLIED TO ANY
5D BLOCK.** The covering search at
[`state/declaration-v-5d-covering-search-20260822.sh`](state/declaration-v-5d-covering-search-20260822.sh)
is the falsifiable form of that claim — see §8. Its run at `064496cd` returns `0` over the 206
non-test `.py` files under `nd-unfolding/` for `hartlap`, `ledoit`, `n-p-2`, `n - p - 2`, `debias`,
`sellentin`, `percival`, `kaufman` and `wishart`, with both positive controls passing. **`shrink`
returns 9 and every one was opened and adjudicated**: all are ordinary English — *"leverage shrinks
it"*, *"the trend shrinks"*, *"a basis that silently shrinks"*, *"averaging N runs shrinks the
scatter"* — and not one is an estimator. The single real shrinkage implementation in the repository
is `2d-unfolding/uq/analyze_universes.py:154`, which is 2D and outside this path. This is the *"or
the explicit statement that none was"* limb of (v), and per ruling 11 it is the intended end state,
not a deficiency.

---

## 7. Recorded, not fixed — three items belonging to other owners

**I hold none of these files' authorizations and have edited none of them.**

**(a) The note calls the analysis uniformly "biased `1/N`" and the block sums are mixed.**
`app_statmethods.tex:663-665` reads *"for this analysis's biased `1/N` production convention
(`nd-unfolding/uq_math.py`, 'universe-mean centered, biased 1/N')"*. Measured on the 5D path: `C_syst`
is biased `1/N` (`analyze_universes_5d.py:220`) and so are the joint throws (`uq_math.py:104`), but
`C_stat` and `C_ML` are **unbiased `1/(N−1)`** (`combine_cov_nd.py:20`). **The 5D sum mixes the two
conventions.** Numerically nothing moves — `1/N` vs `1/(N−1)` is 1.0% at `N=100` and 4.3% at `N=24`,
and no 5D number is quoted at all — but declaration (v) *specifically requires the convention to be
stated per block*, so a description the protocol demands be right is wrong. First recorded at
`BRIEF-20260822-oi137` §7a; **re-measured here on the 5D path and confirmed.**
**Owner: the analysis-note statistics-appendix lane.** A separate lane is editing
`app_statmethods.tex` concurrently under its own authorization; two lanes in one file is how correct
changes compose into a defect.
**Required change, minimal:** qualify the phrase to the MAT/joint-throw blocks it describes, and say
that the statistical and ML blocks in the same sum use `1/(N−1)`.

**(b) "The unified-throw 5D candidate" resolves to two artifacts with different (v) fields.** §2.
`app_statmethods.tex:665-667` pairs `N=160` with that phrase; it is exact for family **T** and wrong
for family **A**, where the throws enter only as a diagonal (§3). No quoted number depends on it.
**Owner: same lane.** **Required change:** name the artifact, or say "the 160-throw joint ensemble".

**(c) The `(v)` evidence pointer is a broken path.** §5. `app_statmethods.tex:654` routes to
`RANK-AND-INVERSION-20260810.md`, whose `:16` cites
`runs/standard-p4-verifier/20260810T0600Z-product-audit-5d-verdict.json` — wrong prefix, and absent
from `main` either way. Same at `PROVENANCE-DEBT-20260810-standard-p4.md:142`.
**Owner: `RANK-AND-INVERSION-20260810.md`'s lane** (it is `LIVE` and routed to by `OI-137`).
**Required change:** cite `docs/orchestration/runs/…` **and** the evidence tag
`evidence/prepublication-2026-08-20-0b329e8a`, since the path alone no longer resolves on `main`.

**Deliberately not touched, on ruling 9 and the `OI-93` note in my assignment:** the two pinned
Gate-5 records (`SPEC-20260814-gate5-cstat-construction-v1.md`, `pet/gate5_cstat_contract.json`) keep
their reversed direction sentence byte-for-byte; the erratum lives at
`nd-unfolding/PET_UQ_REMEDIATION_STATUS.md`. And `OI-93`'s `(N−p−2)/(N−1)` form is **not** a typo
against the note's `(N−p−2)/N`: the PET `C_stat` it scopes to is built with `np.cov(…, ddof=1)`, so
the unbiased denominator is right there while the note's biased `1/N` is right for the MAT/joint-throw
convention it describes. **Two conventions, each correct in scope; not reconciled to one number.**

**The bias direction, restated so this record cannot be quoted backwards:** the inverse of a noisy
sample covariance is biased **upward**, so a χ² on a fixed residual is **INFLATED** and tension is
**OVERSTATED**, never flattered. What becomes over-optimistic is any confidence region drawn from
the same over-tight covariance.

---

## 8. The search set, stated so it can be falsified — and what expires this record

Harness: [`state/declaration-v-5d-covering-search-20260822.sh`](state/declaration-v-5d-covering-search-20260822.sh),
committed, re-runnable from the repository root, prints its own file set and exclusions.

* **File set:** `git ls-files -c -o --exclude-standard` (tracked **and** untracked, gitignored
  excluded), filtered to `.py .sh .json .tsv .md .tex .txt`, minus `.claude/worktrees/` (a peer's
  live audit checkout there is another commit's content, not this tree's).
* **Self-reference:** the script and **this document** are both excluded, the exclusion set is
  printed, and a rename of either member makes the script **exit 1** rather than silently restoring
  the self-hits. Negative control run before this file existed: the guard fired, exit 1.
* **Positive controls, both of which must pass or every null is void:** `ledoit` must match
  `2d-unfolding/uq/analyze_universes.py` — the real shrinkage estimator that the original `OI-137`
  grep missed, so a harness that cannot find it is not measuring the claim; and `upstream_n_throws`
  must match `nd-unfolding/uq_5d/receipt_candidate_stamps_5d.json`, proving the search reaches the
  receipt layer.
* **NOT searched, and this is the boundary of the null:** binary `.root` payloads — a `TNamed`
  inside one is invisible to any text search, which is exactly why every artifact claim above is
  read from a ROOT-reading **receipt** and dated. Also `.git` internals, gitignored products, PDFs,
  and **the cluster checkout**: the launcher hardcodes `REPO` and `cd`s there, so the tree that
  executes is not necessarily the tree searched here.

**What would expire this record.** Every claim below is dated, and the authorized work is what
falsifies it:

1. **Any rebuild of a 5D covariance product.** A rebuilt adopted root gains `upstream_n_throws`; a
   rebuilt `C_stat`/`C_ML` under a patched `combine_cov_nd.py` would close gap 1. **Re-measure §4
   after running the path, not before** — that is the failure mode `OI-147` filed.
2. **Any 5D χ² being specified.** `p` stops being `—` the moment a truncation is chosen, and §5's
   "nothing inverts a 5D covariance" is a covering claim over `docs/analysis-note/` at `064496cd`.
3. **Any change to `STAMPED_SCALAR_KEYS` or `LEG_IDENTITY_KEYS`.** Gap 3's price is quoted against
   the tuple as it stands.
4. **A note edit by the concurrent `app_statmethods.tex` lane.** All `:NNN` line citations into that
   file are pinned to `064496cd` and will drift.

---

## 9. Evidence route

Every row was opened and re-measured at `064496cd`; nothing is quoted from a generated summary.

| claim | evidence |
|---|---|
| declaration (v) text, five limbs | `docs/analysis-note/app_statmethods.tex:645-657` |
| the "biased `1/N`" prose, and the `N=160` worked example | `app_statmethods.tex:662-667` |
| ruling 10, verbatim | `DECISION-20260822-joseph-b1-lift-and-clause-c.md`, ruling 10 |
| `C_combined == C_syst + C_stat + C_ML`, executable | `nd-unfolding/p4_build_components.py:120,124` |
| the same identity, independently audited | product audit `checks[].name == "full total reconstruction"` |
| adoption is a diagonal inflation, not a block | `nd-unfolding/adopt_unified_5d.py:13-15,42,108-113,125,130,143-144` |
| per-band `N` for `C_syst`, artifact-read | `nd-unfolding/uq_5d/receipt_cause1_endpoint_census_5d.json` `census.summary`, `per_band` |
| `C_syst` estimator, biased `1/N`, inline | `nd-unfolding/analyze_universes_5d.py:220` |
| normalization band is deterministic rank-1 | `analyze_universes_5d.py:229-232` |
| `C_stat`/`C_ML` `N`, enforced | `nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh:167,168`; `nd-unfolding/replica_manifest.py:41-47` |
| `C_stat`/`C_ML` estimator, unbiased `1/(N−1)` | `nd-unfolding/combine_cov_nd.py:20` |
| `C_stat`/`C_ML` products carry no scalar | `nd-unfolding/combine_cov_nd.py:23-26` |
| joint throws recounted and stamped | `nd-unfolding/unified_throw_cov.py:388,389,540`; `uq_math.py:104` |
| `n_throws = 160` on both throw roots | `receipt_construction_contract_5d.json` `throw_roots.*.parameters.n_throws` |
| `n_throws` absent on the six older adopted roots | same receipt, `adopted_roots.*.parameters.n_throws` |
| `upstream_n_throws = 160` on the 08-12 arms | `nd-unfolding/uq_5d/receipt_candidate_stamps_5d.json` `files.*.parameters` |
| the propagation writer, and its dated comment | `nd-unfolding/adopt_unified_5d.py:180-190,198-204` |
| the current adopt path runs that pinned writer | `nd-unfolding/mii_adopt_unified_5d_stamped.py:152,711-712`; `sbatch_finalize_5d_bkgaware_gpu.sh:347,352` |
| `upstream_n_throws` compared against a predeclared value | `nd-unfolding/mii_anchor_comparator.py:658-660,725-735`; `receipt_candidate_stamps_5d.py:107` |
| slab census, `n_throws_union = 160` | `receipt_construction_contract_5d.json` `slab_census.throw_slabs_sb` |
| the `120` in a `full160` directory | same, `slab_census.j28_union_rescaled_half` |
| rank 263, condition, nulls | product audit `checks[].name == "rank and condition diagnostics"`, at the evidence tag |
| per-component eigenspectra not measured | same receipt, `what_this_audit_does_not_cover[2]` |
| no 5D χ² is quoted | `RANK-AND-INVERSION-20260810.md` §3; `docs/analysis-note/sec_3d.tex:181-183` |
| no 5D inversion site | `BRIEF-20260822-oi137-finite-N-precision-bias-exposure.md` §4 |
| `n_universes` stamp, and its date | `analyze_universes_5d.py:278`; commit `5afb7947`, 2026-08-19 |
| `STAMPED_SCALAR_KEYS` has no ensemble-size member | `nd-unfolding/mii_adopt_unified_5d_stamped.py:172-179` |
| 5D `.root` payloads absent from this checkout | `.gitignore:2`; `find nd-unfolding/uq_5d -name '*.root'` returns nothing |
