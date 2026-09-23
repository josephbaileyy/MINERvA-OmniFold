# OUTCOME 2026-09-22 — a 3D `(p_T, p_∥, E_avail)` covariance now EXISTS, projected from the adopted trunk

**CITABLE FOR:** the existence, identity and measured properties of a `(pt, pz, eavail)` covariance
projected from `3d7465f6…`.
**NOT CITABLE FOR:** adoption of that object, any figure built from it, any significance, or the
retirement of the historical 3D quarantine. **Construction is not adoption.**

| | |
|---|---|
| product | `/pscratch/sd/j/josephrb/z2m-products/PROJ3D/cov_5d_to_ptpzeavail_from_adopted_trunk.root` |
| `sha256` | `20c16e16a35a837b09d7fe39bcf6bb8ee5828d5283fc5c2f756e3a5371e1f69e`, `15,937,290` B |
| receipt | `docs/orchestration/state/PROJ3D-20260922-ptpzeavail-from-adopted-trunk-receipt.json` |
| spectrum source | `docs/orchestration/state/PROJ3D-20260922-job58736728-stdout.txt` — ⚠ **the receipt carries NO eigenvalue field**, so `λ_min`, `most-neg/max`, `√Tr` and the symmetry residual below come from the producing job's stdout. Committed 2026-09-22 after round 11 found them cited from an uncommitted source |
| job / code | `58736728`, worktree at `9e78a8cf`, under `mnv_guarded_run.py` (1 checkout root) |
| authorization | `HANDOFF-20260922` §9.2 / §12 item 5, this session's **D6** |

## 1. Why it was built

`HANDOFF-20260922` §9.2: four live figures read the **QUARANTINED** `hCov_combined3d_total`, and
*"they cannot be regenerated correctly yet: the quotable 3D covariance must be projected from the
adopted 5D trunk and **that projection has not been built**."* It is built now. That removes the
stated blocker; it does **not** by itself authorize regenerating anything.

## 2. What was measured

| quantity | value |
|---|---|
| source | `3d7465f66fbe66b0…`, `variant: cv`, metadata still `adoptable: false` / `NON-PASSING`, carried unedited |
| adoption exception | `AMENDMENT-20260918-spec-6.4-…md`, `sha256 318cc1b4834a0348…` — **byte-identical** to the record the adopted `(E_avail,W)` publication run used |
| axes | `pt,pz,eavail,q3,W` → keep `pt,pz,eavail` |
| destination | **1,431 reported cells** of a dense `14×16×7 = 1,568` grid |
| `src_cells_dropped` | **0** |
| `n_empty` | **0** — ⚠ zero **by construction** in receiving-cells mode; this is **not** a check and may not be cited as one |
| `√Tr C` | `6.1289e-39` |
| symmetry `max\|C − Cᵀ\|` | **exactly `0.00e+00`** (structural: the `M C Mᵀ` form symmetrises) |
| `λ_min` | computes **`−4.326e-93`**; most-negative/max `−2.32e-16` — ⚠ **a relative size at machine epsilon, so the SIGN IS NOT MEANINGFUL**: it is far inside the `1e-9` relative PSD allowance `VL142` applies to the trunk itself (whose own negatives, at `7.3147e-16`, are *"arithmetic-implementation dependent"*). This row read *"— NEGATIVE"* in bold, as if the sign were a property of the object ⚠ **And the value itself is one run's:** re-solved on a Perlmutter login node from the same `20c16e16…` product, `λ_min` came out `−5.818e-93` with 1 BLAS thread and `−4.512e-93` with 4 (this lane), and `−2.76e-93` to `−5.82e-93` across seven solver configurations (review #11a); **583–587 of the 1,431 eigenvalues compute negative**, which no earlier revision stated. The retained count `263 at rc = 1e-12` is stable across all of them. |
| retained count | **`263` of `1431` at `rc = 1e-12`** (the projector's hardcoded cutoff, from `state/PROJ3D-20260922-job58736728-stdout.txt`). ⚠ **This table omitted it**, while §5 asserted no scan existed — the two halves of one record disagreeing about whether a rank exists. Quote it **only** with its cutoff, and read §5 before citing it: a single count at one hardcoded cutoff is **not** a cutoff scan, and this `263` is **not** the withdrawn *"rank 263 is Z's"* attribution. |
| PSD to machine tolerance | OK — the projector's own test, `psd_ok = ev[0] >= -1e-10 * ev[-1]` in `project_cov_nd.py` (⚠ this row said *"the `1e-9` relative allowance"*, which is `VL142`'s standard for the trunk, not the test that printed this OK). An OK at this threshold is not evidence the covariance is definite: see the `λ_min` row |
| row index readback | `856469c41a8484be…`, 1,431 labels, digested after the file was closed |
| `M` | shape `1431 × 10694`, content digest `6147e1543e3d6077…` |
| `run_class` | `publication-under-exception` |
| `acceptance_question` | **`UNDECLARED`** — carried verbatim, never defaulted |

## 3. ⚠ TWO THINGS THAT DIFFER FROM THE `(E_avail,W)` PRODUCT AND WILL BE GOT WRONG BY ANALOGY

1. **The two objects' `λ_min` compute with OPPOSITE SIGNS, and NEITHER sign means anything.** The
   `(E_avail,W)` projection computes `λ_min = +4.359104e-92` (`n_negative = 0`); this one computes
   `−4.326e-93` in one run (it varies with the BLAS configuration; see §2), most-negative/max `−2.32e-16`. Both sit at the double-precision noise floor, and
   `PLAN-20260918` §16.1a rules for the first that *"their sign is not meaningful"* — the same holds
   here, at a relative size even closer to machine epsilon and far inside the `1e-9` relative PSD
   allowance `VL142` uses. The analogy trap is therefore **copying EITHER sign across as a
   property**: labelling this one "most-negative/max" is accurate about the computed value, and must
   not be read as evidence the covariance is indefinite, just as the other's positive minimum is not
   evidence it is definite. ⚠ **This item read *"`λ_min` IS NEGATIVE HERE … the minimum genuinely
   is negative"*, which asserted a meaningful sign; withdrawn 2026-09-22 (self-round 39), after the
   release README was found asserting the opposite sign as meaningful for the other object.**
2. **The destination is 1,431 of 1,568, not all of them.** 137 dense `(pt,pz,eavail)` bins receive
   no source cell. The `(E_avail,W)` case had `42 = 7×6` with no shortfall, so the two are not
   analogous and a reader assuming a dense destination here will mis-index.

## 4. ⚠ THE DESTINATION MASK IS A DECLARATION, AND THE ONE A FIGURE NEEDS IS **NOT** THE ONE BUILT

This run declares **`receiving-cells`** (no `--dst-cv`) — the **same** declaration the adopted
`(E_avail,W)` publication product used, chosen to follow precedent rather than to invent policy.

`run_m1_projection.sh` states the rule: *"project_cov_nd.py offers two destination masks and … which
one is used changes the population every downstream criterion is stated over, so it is declared
prospectively or not at all."*

**A figure pairing this covariance with the frozen 3D central value would need the
`declared-dst-cv` variant**, bound to `3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root`, so that the
covariance's rows and the central value's bins are the same population. **That declaration was not
made and is not made here.** It is a prospective choice, and choosing it silently in order to make a
figure work is exactly the failure the rule exists to prevent.

## 5. What this does NOT authorize — read before touching any figure

- **It does NOT adopt this covariance.** Adoption is a Joseph decision (`AGENTS.md`, *Decisions
  reserved for Joseph*; this session's **D7** forbids anything constituting a new publication
  adoption). The object exists; nothing has adopted it.
- **No figure is regenerated here.** ⚠ **CORRECTED 2026-09-22 by an independent reviewer: the
  enumeration below was wrong in BOTH directions, and it was taken from `HANDOFF-20260922` §9.2's
  table rather than measured.** Measured with `grep -rn hCov_combined3d_total`:
  `overlay_generators_band.py` (note Fig. 20, via `--cov` at `make_figures.sh:48`),
  `compare_mec_eavail.py`, `mode_decomp_eavail.py`, `compare_ascencio_eavail.py` and
  **`compare_3d_fullcov.py`** read it — and `compare_3d_fullcov` is a **live note figure**
  (`sec_3d.tex`, `\label{fig:3dfullcov}`) that the handoff's list and this record's first version
  both omitted. ⚠ **AND THE "OTHER DIRECTION" CLAUSE THAT STOOD HERE WAS ITSELF WRONG — corrected
  2026-09-22 by a SECOND independent reviewer.** It read: *"`make_figures.sh:48` builds
  `generators_vs_unfolded_band` (note Fig. 20) with `--cov … :hCov_universe3d_total`, a different
  key, so naming it as a reader of `hCov_combined3d_total` was wrong at the invocation level."*
  **Measured, line 48 passes BOTH flags:**

      --cov      …/uq_universe_3d_covariance.root:hCov_combined3d_total
      --syst-cov …/uq_universe_3d_covariance.root:hCov_universe3d_total

  The key I named is carried by `--syst-cov`; the **primary** `--cov` **is**
  `hCov_combined3d_total`. **So `generators_vs_unfolded_band` (note Fig. 20) DOES read the
  quarantined covariance, the handoff's §9.2 table was right about it, and I "corrected" a true
  entry into a false one.** It belongs in the readers list and is restored to it. This also removes
  a contradiction with `sec_3d.tex`'s own `fig:3dmodels` caption — *"the SUPERSEDED historical 3D
  covariance … (`hCov_combined3d_total`)"* — which I edited in the same commit while asserting the
  opposite here. `ascencio_fullcov_compare` reads the historical unified-throw **4D** object, which
  this projection does **not** replace.
- ⚠ **AND THE OMITTED FIGURE CARRIES TWO SENTENCES THIS PROJECTION FALSIFIES.** `sec_3d.tex` states
  *"The first has happened; **the 3D projection has not been built**, so the gate still holds"*
  (the `fig:3dfullcov` caption) and *"…but **the 3D projection itself has not been built**, so all
  covariance-dependent 3D comparisons remain gated on a product that does not yet exist"* (§3d-syst
  body). **Both are now false on their stated ground.** The gate SHOULD still hold — on
  non-adoption and on the missing `declared-dst-cv` variant (§4) — but not on non-existence.
  Corrected in `sec_3d.tex` and synced to the standalone repository.
- ⚠ **If these are ever regenerated, do NOT silently reintroduce them to the primer.** Fig. 3 was
  swapped to `eavailW_band` (central-value only, no `--cov`) and Fig. 4 to `paper_joint_localization`;
  that leakage was blocker 2 of the manuscript review.
- **`M1`–`M4` travel with this object**, because they travel with `3d7465f6…` and this is projected
  from it. In particular **no generator significance may be quoted from it**, and `M4` is much
  larger per individual bin than per projection.
- **A rank exists for this object and may be quoted ONLY as `263 of 1431 at rc = 1e-12`.** ⚠ This
  bullet opened *"No rank is quoted here and none may be inferred"* — a bolded prohibition that the
  rest of the same bullet contradicts three times over. The retraction landed INSIDE the bullet and
  left its topic sentence standing: the one-of-two-sites defect performed on a single paragraph.
  The projector printed a retained count at its
  hardcoded `rc = 1e-12`; on the `(E_avail,W)` object the analogous count moves from **2 to 42** across
  the cutoffs `VL145` actually scans (`1e-1 → 2` … `0 → 42`; the narrower `26 → 42` is `VL143`
  item (3)'s abridgement, which starts at `1e-6`). ⚠ **THIS READ *"nothing has scanned this object's
  spectrum ... no scan exists yet"*, AND THE RECORD'S OWN CITED LOG REFUTES IT.**
  `state/PROJ3D-20260922-job58736728-stdout.txt` — the file §2 names as this record's spectrum
  source — prints `min-eig=-4.326e-93  most-neg/max=-2.32e-16  rank~263/1431`.
  `nd-unfolding/project_cov_nd.py` calls `np.linalg.eigvalsh`, which returns
  **eigenvalues only** — no eigenvectors — and **nothing persists the spectrum** (§2 is right that
  the receipt carries no eigenvalue field; it was computed and discarded). ⚠ This read *"A full
  eigendecomposition was run"*, naming an operation the code does not perform. A retained count of **263 of 1431 at the projector's hardcoded
  `rc = 1e-12`** exists; §2's "What was measured" table omitted it. The corrected claim: **what is
  absent is a cutoff SCAN** of the kind `VL145` performs for the `(E_avail,W)` object — a single
  retained count at one hardcoded cutoff is not one. **Any rank for this product must still be
  reported with its cutoff, and `263` may be quoted only as `263 of 1431 at rc = 1e-12`.**
  ⚠ **DO NOT CONFLATE THIS `263` WITH THE WITHDRAWN ONE.**
  `state/check-withdrawal-completeness-20260910.py` registers, as WITHDRAWN, a claim attributing
  a rank of this magnitude to Z, to G, or to the trunk used in production; the registry records
  that the value belongs to S, the component donor. **The claim string is deliberately NOT quoted here** —
  that checker's docstring forbids its audited documents from reproducing its match strings, and
  an earlier revision of this very paragraph quoted one and took the checker from 2 discrepancies
  to 3, which is the exact failure its docstring records having happened once before. Read the
  registry for the wording.
  The `263` here is the retained count of **this 1431-cell destination object** at `rc = 1e-12`,
  measured on `M C Mᵀ`. ⚠ **It may be inherited from the source rather than being a property of
  the destination, and which it is has NOT been measured.** (An earlier revision cited
  `rank(M C Mᵀ) ≤ rank(C)` as the licence for that. **That is withdrawn as stated:** the
  inequality governs EXACT rank, while `263` is a retained count at a RELATIVE cutoff
  `ev > ev.max()*rc`, and `λ_max` itself changes under `M C Mᵀ` — so the exact-rank bound does not
  transfer to the thresholded count. The same paragraph insists a rank is a step function of its
  cutoff; that applies here too.) It is not a claim about Z's rank and must not be cited as one.
  The corrected wording had already reached `REPORT-20260922-review-residue.md` §3 item 7 and was
  **not** carried to this record, which is the CITABLE artifact — one-of-two-sites again.

**Co-Authored-By: Claude Opus 5 (1M context)**
