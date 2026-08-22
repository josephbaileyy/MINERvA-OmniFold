# BRIEF — `OI-137`: finite-`N` precision bias, measured exposure and the decision it needs

**Filed 2026-08-22. Measured at `HEAD = 57d9f3fbdb72282f8da1ca70192de0d7566c3f8c`.**

> **Count correction, recorded rather than amended.** Commit `0aa13221`'s message says
> *"20 inversion primitives"*. The correct figure is **19 call sites plus one docstring mention**
> (§4). The commit is pushed and a force-push is not mine to make, so the correction lives here and
> this brief is the authoritative count.
**This is a decision brief, not a patch. No estimator, covariance, uncertainty model or
published number is touched by it.** The one thing it asks Joseph for is at §8.

Owner of `OI-137` as of this brief: this lane. The row was `UNOWNED`.

---

## 1. Bottom line

Three findings, in order of how much they change the picture.

**(a) The claim on file is half false at `HEAD`, and the false half is already fixed in the
note.** `OI-137`'s basis cell asserts two things. The second — *"the note's N-D chi-square
protocol does not require the ensemble size to be declared"* — **was true when written on
2026-08-20 and is false now.** The protocol gained **declaration (v)** on 2026-08-21, and it
mandates exactly what the row asked for: per sample-covariance block, its ensemble size `N`,
its normalization convention, the effective dimension `p` inverted after truncation, and the
finite-ensemble treatment applied or an explicit statement that none was
(`docs/analysis-note/app_statmethods.tex:650-657`). The row's arithmetic was also corrected in
the note, **and corrected against the row's own stated direction** — see (c).

**(b) The first half survives, but only on a narrower reading than the row's words.** There is
**no Hartlap-style debiasing factor implemented anywhere** — that null is real and now rests on
a covering search (§3), not on three terms over two extensions. But the row says *"no finite-`N`
precision-bias **correction** exists anywhere in the repository"*, and that is too strong:
a **diagonal-target Ledoit–Wolf-style shrinkage** estimator is implemented at
`2d-unfolding/uq/analyze_universes.py:153-160,277-286` and its result is **reported in the note**
at `app_statmethods.tex:936` (`λ=0.05`, rank `178→204`, `χ²/205 = 3.29`). Shrinkage is a different
object from a debiasing factor — it regularizes an ill-conditioned sample covariance rather than
removing the bias in its inverse — but it treats the same finite-ensemble pathology, and the
repository is not bare of finite-`N` machinery the way the row reads. The filed grep missed it
because it searched for `hartlap`, `N-p-2` and `(N - p` only.

**(c) The measured exposure on the publication critical path is small, and the direction of the
effect is the opposite of what the row says.** The row states the bias *"makes χ² too SMALL"* —
*"an error in the flattering direction."* That is backwards for a fixed residual: the inverse of a
noisy sample covariance is biased **upward**, so a χ² on a fixed residual is **inflated** and
tension is **overstated**. The note already carries the correction
(`app_statmethods.tex:666-670`). What actually becomes over-optimistic is a confidence region
drawn from the same over-tight covariance. **`OI-93` carries the same reversed sentence and is
also wrong on this point** (`docs/OPEN_ITEMS.md:166`), as does the PET Gate-5 contract
(`nd-unfolding/pet/gate5_cstat_contract.json:294-300`) and
`docs/orchestration/state/gate5-cstat-spec-measurements-20260814.json:258`.

**Recommendation: disclose, do not correct.** Reasons at §8. This is a recommendation; the call
is Joseph's and the note's statistics appendix's.

### The hold

`HOLD-20260821-clause-c-verification.md` **has expired by its own terms.** Its expiry clause reads
*"This hold ends when the clause (c) verifier files its verdict… If the verdict is filed and this
file is still here, the hold has expired and the file is stale — delete it."* The clause (c)
verdict is filed (`2b6bf689`). `docs/orchestration/MANIFEST.tsv:50` already carries the file as
`ARCHIVAL` / `terminal`. Nothing in this brief touches `nd-unfolding/` in any case — it is
documentation only. **I did not delete the hold file**: it is another lane's record and its own
instruction to delete is addressed to its author, not to me.

---

## 2. What was asked, and the discipline applied

The instruction was to not take the filed null on trust, because a null grep is evidence about
the search and not about the world. Two axes were widened: the **file set** (the filed grep
covered `.py` and `.tex`; this covers eleven extensions including `.md`, `.json`, `.tsv`, `.sh`
and the notebooks) and the **term set** (three terms → sixteen).

Two harness defects were found and fixed during this work, and both are worth recording because
each would have produced a **false null**:

1. **The harness matched its own term list.** The first run reported `kaufman hits=1`,
   `sellentin hits=1`, `percival hits=1`, `wishart hits=1` — every one of them the search script
   itself, which necessarily names every term it looks for. The true count is `0`. An absence
   test that spells the thing it seeks cannot find its own null. Fixed by self-exclusion.
2. **There was no positive control.** A null from a broken harness is indistinguishable from a
   null from a clean world. The script now asserts that `hartlap` matches `docs/OPEN_ITEMS.md`
   and **exits 1** if it does not, so every null below is void unless that arm passed.

---

## 3. The search set, stated so it can be falsified

Harness: **`docs/orchestration/state/oi137-covering-search-20260822.sh`** — committed, re-runnable
from the repository root, prints its own inventory. Results below are its output at
`57d9f3fb`, positive control **OK**.

**File set: 1403 files.** `git ls-files -c -o --exclude-standard` (tracked **and** untracked,
gitignored excluded), filtered to
`.py .tex .md .ipynb .json .tsv .sh .cxx .C .h .txt .yaml .yml .cfg .toml`, minus
`.claude/worktrees/` (a peer's live audit checkout there would otherwise be counted as repository
content), minus the harness itself.

| ext | n | | ext | n | | ext | n |
|---|---|---|---|---|---|---|---|
| `.py` | 434 | | `.md` | 211 | | `.tsv` | 16 |
| `.sh` | 320 | | `.txt` | 119 | | `.h` | 3 |
| `.json` | 272 | | `.tex` | 23 | | `.ipynb` / `.C` / `.yaml` | 2 / 2 / 1 |

**Explicitly NOT searched — the boundary of the null:**

- **Binary ROOT payloads.** A correction applied inside a `.root` `TNamed` would not be found by
  any text search. Checked by a different route instead, and the answer matters — see §7(b):
  the adopted 5D roots carry **no `n_throws` key at all**.
- `.git` internals, gitignored build products, PDFs.
- **The cluster checkout.** This measures *this* tree at *this* sha. The launcher hardcodes
  `REPO` and `cd`s there, so the tree that executes is not necessarily the tree searched here.

**Term results** (all case-insensitive; the separator class carries both the ASCII hyphen and
`U+2212`, because the note and `OPEN_ITEMS.md` use a real minus sign and an ASCII-only pattern
misses every prose occurrence):

| term | hits | verdict |
|---|---|---|
| `hartlap` | 17 | in `.md`/`.json` only — **never in `.py` or `.tex`**. No implementation, no citation at a point of use. |
| `(N−p−2)` family | 7 | now includes **`app_statmethods.tex`** (was zero on 08-20). Prose, not code. |
| `(N − p` | 7 | same set. |
| `kaufman` | **0** | |
| `sellentin` / `heavens` | **0** | |
| `percival` | **0** | |
| `wishart` / `anderson-hartlap` | **0** | |
| `effective ndf` / `effective dof` | **0** | |
| `unbiased … inverse` | **0** | |
| `dodelson` / `schneider` | 2 | **not the Dodelson–Schneider literature** — both are the "Schneider" in *Hartlap, Simon & Schneider 2007*. Effective null. |
| `shrink` | 67 | **one real estimator** (`analyze_universes.py`), one note table row; the remaining ~65 are unrelated ("the set can only shrink", learning-rate anneal, "leverage shrinks it"). |
| `ledoit` / `wolf` | 15 | **1 real** (`analyze_universes.py:154`); the rest are "cry wolf" in gate prose, plus a base64 blob in a notebook. |
| `debias` | 7 | prose only, all in the `OI-93`/`OI-137`/PET-SPEC/note cluster. |
| `dof` | 33 | includes the `C_delta` site of §5. |
| `finite-N` / `finite ensemble` | 15 | includes `compare_3d_fullcov.py:10-14`, which names the hazard as its *reason* for truncating. |
| `ddof` | 112 | the operand for §7(a). |

---

## 4. Exposure inventory — every site that inverts a covariance or forms a χ²

Found by searching the same file set for `np.linalg.{pinv,inv,solve,cholesky,lstsq}`,
`scipy.linalg.*`, `pinvh`, and χ² definitions/uses. **19 inversion call sites across 14 modules.**
(The raw grep returns 20 lines; `receipt_model_chi2_2d.py:30` is a docstring naming `np.linalg.pinv`,
not a call. Counted separately because a comment is not an inversion — the same distinction that
made this brief's own search harness match its own term list, §2.)

The classification that matters is **pure sample covariance** vs **block sum**, because a single
debiasing factor is only defined for the former. The note makes this point and it is correct
(`app_statmethods.tex:671-676`).

**Which blocks are genuinely finite-ensemble.** Of the 44 MAT bands in the 2D systematic
covariance, **43 are `±1σ` pairs at `N=2`** — deterministic endpoint shifts, rank-1 outer
products, **no sampling noise, so no Hartlap exposure at all**
(`nd-unfolding/uq_math.py:96-104`; `unified_throw_cov.py:436`). The exception is the **PPFX flux
band at `N=100`**, which *is* a random multiverse draw. This is the single most important
distinction in the whole question and it is why the largest-variance contributor is the part the
hazard does not touch.

| # | Site | Covariance inverted | Kind | `N` | `p` inverted | conv. | Quoted? |
|---|---|---|---|---|---|---|---|
| 1 | `compare_to_paper_fullcov.py:95-108` `chi2_with_cov` | paper `TotalCov` + `C^syst` + `C^boot` + `C^ML` | **block sum** | mixed (§7a) | 205, `pinv` default `rcond`, `ndf=205` | **mixed** | **YES — `\chiCombined` = 1.481** |
| 2 | `compare_to_paper_fullcov.py:111-127` log-normal | same, `/(x_i x_j)` | block sum | mixed | 205 | mixed | YES — 1.468 |
| 3 | `receipt_model_chi2_2d.py:132-134` | paper `TotalCovariance` **only** | external | — | reduced grid | — | YES — 33.0 / 26.5 (`sec_results.tex:171`) |
| 4 | `normalize_xsec_shape.py:148` | paper cov, shape-projected | external | — | 205 | — | YES — 3.60 |
| 5 | `compare_to_paper_interior.py:99,176` | paper cov, interior mask | external | — | subset | — | diagnostic |
| 6 | `diagnose_tension.py:194` | paper `TotalCov` | external | — | 205 | — | diagnostic |
| 7 | `uq/_ours_only_chi2.py:128` **direct `inv`** | `C^syst`(shrunk) + `C^boot` | **block sum** | 300 / 100 | **205, direct inverse** | mixed | **NO** — note reports pulls + scan instead |
| 8 | `uq/analyze_uq.py:160-165` | `C^boot` alone, Cholesky **PD check only, not a χ²** | pure sample | 300 | — | 1/(N−1) | n/a |
| 9 | **`ibu_omnifold_paired_cdelta.py:190-198`** | `C_delta` = `Cov(x_OF − x_IBU)` | **PURE SAMPLE** | **200** | declared rank or `rcond=1e-10` | 1/(N−1) | **NO** (no `.tex` hit) |
| 10 | `genie/compare_3d_fullcov.py:101-107` truncated-spectral | 3D block sum, 1431 bins, rank ~247 | block sum | 187 + 100 + 10 | truncation scan | mixed | **NO — quarantined** (`sec_3d.tex:181`) |
| 11 | `genie/overlay_generators_band.py:170-177` | 3D block sum | block sum | as above | `solve`, else `pinv` | mixed | **NO — quarantined** |
| 12 | `compare_ascencio_fullcov.py:186`, `compare_ascencio_fine.py:93` | ours + Ascencio published | block sum | mixed | `solve` | mixed | **NO** — *"No pulls or full-covariance χ² are reported"* (`sec_3d.tex:374-375`) |
| 13 | `eavail_generator_significance.py:106-107` | `C_y`, `E_avail` | block sum | mixed | `pinv`, full + hi subset | mixed | **NO — quarantined** |
| 14 | `eavailW_covariance.py:543,548` | `(E_avail,W)` total | block sum | mixed | `pinv`, full + subset | mixed | **NO — quarantined** |

Sites 3–6 invert the **paper's published covariance**. Its finite-`N` properties belong to
Ruterbories *et al.*, not to us; there is nothing for us to correct, only to note.

The `E_avail` marginal number `χ²/ndf = 4.98` (`sec_3d.tex:81`) also uses the *published*
covariance and is already declared *"not a calibrated goodness-of-fit statistic"*.

---

## 5. Bias factors, per block, with both operands

`f = (N−p−2)/(N−1)` for the unbiased `1/(N−1)` convention; `f = (N−p−2)/N` for the biased `1/N`
MAT convention. Precision inflation is `1/f`. **`f ≤ 0` is not "a large correction" — it is the
singularity restated, and the formula is meaningless there.** These are algebra on recorded `N`
and rank. **No matrix was loaded, inverted or measured**; the row forbids that without
authorization and I did not seek it.

| Block | `N` | conv. | `p` | `f` | precision too large by |
|---|---|---|---|---|---|
| **2D `C^boot`** (Poisson bootstrap) | 300 | 1/(N−1) | 205 | 0.3110 | **3.22×** |
| | | | 140 | 0.5284 | 1.89× |
| | | | 100 | 0.6622 | 1.51× |
| | | | 50 | 0.8294 | 1.21× |
| | | | 20 | 0.9298 | 1.08× |
| **2D `C^ML`** (lgbm seedscan) | 10 | 1/(N−1) | ≥8 | ≤0 | meaningless; rank ≤ 9 |
| | | | 5 | 0.3333 | 3.00× |
| **2D flux band** (PPFX) | 100 | 1/N | 99 | −0.010 | meaningless |
| | | | **1** (effective) | **0.9700** | **1.03×** |
| **5D uthrow** (joint throws) | 160 | 1/N | 263 | −0.656 | meaningless — *the withdrawn pairing* |
| | | | 159 | −0.006 | meaningless |
| | | | **100** | **0.3625** | **2.76×** — the note's figure, reproduced |
| | | | 50 | 0.6750 | 1.48× |
| **5D `C_stat`** (bootstrap) | 100 | 1/(N−1) | ≥98 | ≤0 | meaningless; rank ≤ 99 |
| | | | 50 | 0.4849 | 2.06× |
| **5D `C_ML`** (seed splits) | 24 | 1/(N−1) | ≥22 | ≤0 | meaningless; rank ≤ 23 |
| | | | 10 | 0.5217 | 1.92× |
| **3D `C_boot`** | 100 | 1/(N−1) | 1431 / 247 / 99 | ≤0 | meaningless at every rank the 3D object uses |
| **PET `C_stat`** *(off critical path)* | 50 | 1/(N−1) | 262 | −4.367 | meaningless — matches the contract's `−4.37` |
| | | | 257 | −4.265 | meaningless — **the quotable sub-block is also negative** |
| **`C_delta`** paired IBU/OF | 200 | 1/(N−1) | 100 | 0.4925 | 2.03× |

Two things fall out. **The `p` at which each block's factor turns negative is below the rank that
block actually contributes**, for every block except the 2D bootstrap (`N=300 > 205`) and
`C_delta`. And **the note's `58/160 = 0.3625` reproduces exactly** from the recorded operands,
including its convention: `joint_throw_covariance` calls `mat_covariance`, which is biased `1/N`
(`uq_math.py:104`), and `N=160` is corroborated twice — a predeclared constant at
`nd-unfolding/receipt_candidate_stamps_5d.py:107` and a slab census of 40 files with
`n_throws_union=160` (`uq_5d/receipt_construction_contract_5d.json`).

---

## 6. Why the trace share is **not** the deciding number

The tempting argument is that the finite-ensemble blocks are a negligible fraction of the
inverted matrix. Here is that fraction, computed from the recorded `√tr` values at
`2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md:98-100`. My sum reproduces the recorded combined
`√tr = 3.220e-39` to `3.2195e-39`, which is the check that the arithmetic is on the right objects:

| block | `N` | `Tr(C)` | share of ours-only | share of headline sum |
|---|---|---|---|---|
| `C^ML` | 10 | 2.561e-81 | 0.025 % | **0.015 %** |
| `C^boot` | 300 | 3.302e-80 | 0.319 % | **0.188 %** |
| `C^syst` (44 bands) | 187+1 | 1.033e-77 | 99.66 % | 58.94 % |
| — of which flux band | 100 | ≈5.514e-78 | 53.19 % | 31.46 % |
| paper `TotalCov` | external | 7.161e-78 | — | 40.86 % |

The flux band is 31 % of the headline trace and *is* a finite-`N` sample block — but **99.6 % of
its variance sits in one normalization mode** (`app_statmethods.tex:857-861`), where the factor is
0.97. Its ≤98 poorly-determined directions carry `0.4 % × 31.46 % = 0.126 %`. Total headline trace
in poorly-determined finite-ensemble directions: **≈0.33 %**.

**Do not stop there.** The trace weights eigenvalues by `λ`; a precision matrix weights them by
`1/λ`. A block holding 0.2 % of the trace can dominate the inverse if it supplies the *smallest
retained* eigenvalues — and in the ours-only construction **that is exactly what happens**:
`rank(C^syst) = 140/205`, and adding the 300-replica bootstrap takes it to `201` with
`cond = 3.8e14` (`app_statmethods.tex:853,872-873`). **The finite-`N` blocks are precisely what
fill the 65 null directions.** The repository already demonstrates the consequence:
`pinv(C^syst + C^boot)` gives **`χ²/ndf = 252`**, *"dominated by poorly-determined directions"*
(`:882`), against the paper's `3.661` with its larger stat floor.

**So the argument that the headline is safe is not the trace share.** It is this: the headline sum
includes the paper's external `StatOnlyCov`, which is **rank 205 and near-diagonal**, with
`√tr = 4.6e-40` against our bootstrap's `1.817e-40` — a **6.41× larger trace**. In the headline
sum the small-eigenvalue floor is set by an external published block, not by any ensemble of ours.
That is why site 1 behaves (`1.481`) where site 7 does not (`252`), and it is the reason the
exposure on the *quoted* number is genuinely small rather than merely small-looking.

---

## 7. Two findings not on any record

**(a) The block sums mix normalization conventions, and the note's own prose does not say so.**
Declaration (v) requires each block's convention. Measured:

- `C^boot` and `C^ML`, 2D: `np.cov(..., rowvar=False)` → **unbiased `1/(N−1)`**
  (`2d-unfolding/uq/analyze_uq.py:146`; both built by that same module per
  `uq/final_rollup_full.sh:100,109`).
- 5D `C_stat` and `C_ML`: `C=(Z.T@Z)/(Xr.shape[0]-1)` → **unbiased `1/(N−1)`**
  (`nd-unfolding/combine_cov_nd.py:20`).
- MAT bands and the joint throws: `(Z.T @ Z) / X.shape[0]` → **biased `1/N`**
  (`nd-unfolding/uq_math.py:104`).

So both the 2D headline covariance and the 5D candidate are sums that **mix the two
conventions**. The note's paragraph reads *"for this analysis's biased `1/N` production
convention"* (`app_statmethods.tex:664-665`) as though it were uniform; it is the MAT/throw
convention only, and the statistical and ML blocks in the same sum use `1/(N−1)`.
**Numerically this is small** — `1/N` vs `1/(N−1)` is 0.33 % at `N=300`, 1 % at `N=100`, 4.3 % at
`N=24`, 11 % at `N=10`, and the two largest-`N` blocks are the ones that matter — **so no quoted
number moves.** What is wrong is a *description* that declaration (v) now specifically requires
to be right. Cheap to fix in prose; I have not touched the note.

**(b) The "cheap, safe half" is done for 2D and NOT done for 5D.** `OI-137` says the
no-ruling-needed half is to record `N` beside each block in the construction receipts.
For 2D that **already exists**: `2D_OMNIFOLD_STUDY_STATUS.md:96-101` is a table with an explicit
`N` column. For 5D it **does not**: `receipt_construction_contract_5d.json` reports
`n_throws → present: False` on **every one of the six adopted roots**. The only place `N=160`
exists as an assertion is a hardcoded constant, `receipt_candidate_stamps_5d.py:107`, which is
why `mii_anchor_comparator.py:725-735` has to check `upstream_n_throws` against a *predeclared*
value rather than recount the throws. **Consequence for declaration (v): on the adopted 5D
artifacts it is satisfiable today only by citing a constant in code, not by reading the
artifact.** That is the gap to close first, and it needs no physics ruling.

---

## 8. The decision, and what it is not

**Reserved for Joseph and the note's statistics appendix.** Declaration (v) exists, so the
question the row raised — *does the protocol mandate the declaration?* — is answered **yes**. What
remains is narrower:

> **Does any quoted χ² receive a finite-ensemble correction, or is the treatment disclosure only?**

**Recommendation: disclosure only, plus the §7(b) receipt work.** Four reasons, in order of
weight:

1. **There is no correct single factor to apply.** Every quoted covariance is a block sum mixing
   ~43 deterministic rank-1 bands with two or three finite-`N` blocks at different `N` and now
   **different normalization conventions** (§7a). The note's refusal to mandate a generic factor
   is right, and §7(a) makes it *more* right than the note itself states.
2. **The standard factor's own preconditions fail here.** It assumes independent Gaussian
   realizations and a truncation dimension chosen **independently of the data**. Every truncation
   in this repository is a `rcond` or an eigenvalue scan — i.e. data-dependent. The note says this
   (`:673-676`); the measurement in §4 confirms it at all 20 sites.
3. **On the one quoted number, the floor is external.** §6: the headline's small eigenvalues are
   set by the paper's rank-205 `StatOnlyCov`, 6.41× our bootstrap by trace; our finite-`N` blocks
   are 0.2 % of the trace and are not what regularizes the inverse.
4. **The quoted number is already declared non-calibrated.** `sec_results.tex:63` says the
   combined χ² *"is not a calibrated goodness-of-fit"* because the two sides share systematics and
   double-count. A finite-`N` correction would be a second-order refinement of a number that is
   explicitly not a test statistic. **The first-order defect is the double-count, not the bias.**

**If instead a correction is wanted**, the only site where a single factor is *exactly* valid is
**`C_delta`** (§4 site 9): one pure sample covariance, one ensemble, `N=200`, a declared
truncation rank, and it already converts to a `p`-value via `stats.chi2.sf`
(`ibu_omnifold_paired_cdelta.py:198`). At `p=100` the factor is 0.4925 — the `p`-value is
currently computed from a `T` inflated by ~2×. **It is not quoted in the note**, so nothing
published moves; but it is the cleanest place to demonstrate the correction if a demonstration is
wanted, and the cheapest.

**Also needing a ruling, and smaller:** the direction sentence in `OI-93`,
`gate5_cstat_contract.json:299-300` and
`docs/orchestration/state/gate5-cstat-spec-measurements-20260814.json:258` is **backwards** (§1c). The note is right and those
three are wrong. Correcting them is record hygiene, but the PET contract is a frozen gate operand
and I will not edit it without a ruling on whether that file may move.

**What this brief deliberately does not do:** it does not quantify the bias on any candidate
matrix (the row forbids it without authorization, and no authorization was sought); it does not
edit the note, the PET contract, `OPEN_ITEMS.md` or any covariance; it does not touch
`nd-unfolding/`; and it does not resolve whether the `OI-137` row itself should be rewritten —
that follows the ruling, not this brief.

---

## 9. Evidence route

Everything below was opened and read at `57d9f3fb`; volatile fields were re-measured, not quoted
from a summary.

| Claim | Evidence |
|---|---|
| Declaration (v) exists | `docs/analysis-note/app_statmethods.tex:650-657` |
| Direction is *inflated*, not flattered; `58/160` | `app_statmethods.tex:658-677` |
| No generic factor mandated, and why | `app_statmethods.tex:671-676` |
| Shrinkage estimator implemented | `2d-unfolding/uq/analyze_universes.py:153-160,277-286` |
| Shrinkage result reported | `app_statmethods.tex:936`; MAT does none: `:462` |
| 2D per-block `N` and `√tr` | `2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md:96-101` |
| 2D headline production chain | `2d-unfolding/uq/final_rollup_full.sh:100,109,122,132`; `compare_to_paper_fullcov.py:95-108,218-243` |
| `C^boot`/`C^ML` unbiased `1/(N−1)` | `2d-unfolding/uq/analyze_uq.py:146` |
| 5D `C_stat`/`C_ML` unbiased `1/(N−1)` | `nd-unfolding/combine_cov_nd.py:20` |
| MAT / joint throws biased `1/N` | `nd-unfolding/uq_math.py:96-116`; `unified_throw_cov.py:389,436,443` |
| `N=160`, two sources | `nd-unfolding/receipt_candidate_stamps_5d.py:107`; `uq_5d/receipt_construction_contract_5d.json` slab census |
| Adopted 5D roots carry no `n_throws` | `uq_5d/receipt_construction_contract_5d.json`; `nd-unfolding/mii_anchor_comparator.py:658-660,725-735` |
| Ranks, conds, `χ²/ndf = 252` | `app_statmethods.tex:853-882` |
| No 3D χ²/significance quoted | `docs/analysis-note/sec_3d.tex:181-182`; quarantined-figure caption `:188-191` |
| No Ascencio χ² quoted | `sec_3d.tex:374-375`; `values.tex:105` |
| Headline not a calibrated GoF | `docs/analysis-note/sec_results.tex:63` |
| `C_delta` is a pure sample cov with a `p`-value | `2d-unfolding/ibu_omnifold_paired_cdelta.py:190-198` |
| 3D truncation motivated by finite ensemble | `3d-unfolding/genie/compare_3d_fullcov.py:10-14` |
| PET `−4.37`, and the reversed direction | `nd-unfolding/pet/gate5_cstat_contract.json:294-300` |
| Reversed direction in `OI-93` | `docs/OPEN_ITEMS.md:166` |
| Hold expiry, and that it is satisfied | `docs/orchestration/HOLD-20260821-clause-c-verification.md` "Expiry"; verdict `2b6bf689`; `MANIFEST.tsv:50` |
| The covering search itself | `docs/orchestration/state/oi137-covering-search-20260822.sh` |
