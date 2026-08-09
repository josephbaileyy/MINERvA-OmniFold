# FINDING 2026-08-09 — Quantities DERIVED from merged extensives: J36 is not one site, it is eight

**Headline.** J36 has been carried since 2026-08-01 as a scoping decision owed on one function in
one file. It is one member of a class, and the class has **8 live members across two lanes**, all
computing the same thing the same wrong way: a global Data/MC POT ratio recovered by dividing one
`hadd`-summed extensive by another. Nothing is fixed here — the instruction was to size the class
first.

**Status:** class sized, not repaired. No new *kind* of defect; a new *count*.
**Generator:** `docs/orchestration/audit_derived_from_merged_extensives.py`, AST taint over every
tracked `.py`. `--power` pins J36 itself as a live positive control.

---

## 1. Why a second sweep was needed at all

`FINDING-20260809-tparameter-merge-semantics.md` swept every `TParameter` and concluded, correctly,
that `hadd`'s default summing is right for extensive quantities and wrong only for intensives and
flags — 12 of the 15 hadd-transiting fields merge correctly.

That per-field result has a structural blind spot:

> **Two extensive fields can each merge correctly while a quantity DERIVED from them does not.**

`sum(dataPOTUsed) / sum(mcPOTUsed)` is a POT-weighted mean of the per-playlist ratios, not the
per-playlist ratio. Both operands are impeccable. A per-field review asks "is this field
merge-sensitive?", gets `no` twice, and never looks at the quotient. That is exactly how J36 came
to sit **two functions away** from an explicit, correct, well-commented trap-#8 defence of
`pTmu_fiducial_nucleons` in the same file: the defence answers a per-field question, and this is a
two-field question.

The physics, from `AUDIT-FINDINGS-20260731.md` §7 (already measured, not re-derived here):
per-playlist Data/MC ratios span **0.1707 (1B) to 0.2371 (1D)**, `max/min − 1 = 38.9 %`, against a
global 0.2124. Playlist 1M (18.0 % of MC POT) is over-weighted by 17.1 %, 1D+1F (26.4 %) are
under-weighted by ~11 %, and the POT-weighted mean absolute mixture error is **9.4 %**. Total
normalisation is **not** biased — global and per-playlist scaling agree exactly when MC rate per
POT is playlist-independent — so this cannot be detected or excluded by the 2D paper reproduction
at 1.011. The error is purely in the playlist *mixture*.

## 2. The class, sized

30 sites in 10 files carry taint from a merged extensive. Broken down by shape:

| shape | n | verdict |
|---|---|---|
| **`RATIO_OF_TWO_MERGED`** | **8** | **the J36 class — defective by construction** |
| `RATIO_COMMON_SCALE` | 5 | benign; same field on both sides, the scale cancels |
| `SCALED_BY_MERGED` | 10 | benign; applying a merged total to a quantity over the same inventory |
| `OFFSET_BY_MERGED` | 7 | benign; `1 ± rel_mc` style plotting arithmetic |

### The 8 members

Every one reads a `hadd` product (`runEventLoopOmniFold_MEFHC.root` / `..._5D_MEFHC.root` are the
outputs of `sbatch_hadd_MEFHC.sh` — verified, not assumed) and every one computes the same global
ratio. Post-merge semantics are identical in all eight: **a POT-weighted mean over 12 playlists,
used as though it were a per-playlist correction.**

| # | site | function | severity |
|---|---|---|---|
| 1 | `2d-unfolding/unfold_2d_omnifold_unbinned.py:123` | `get_pot_scales` | **production 2D unfolder — this is J36 as originally filed** |
| 2 | `2d-unfolding/unbinned_1d_study/unfold_ptmu_omnifold_unbinned.py:44` | `get_pot_scales` | **production 1D unbinned unfolder** |
| 3 | `2d-unfolding/binned_study/scripts/unfold_ptmu_omnifold_binned.py:354` | `get_pot_scales` | **production binned pT study** |
| 4 | `2d-unfolding/ibu_omnifold_paired_cdelta.py:109` | `make_response_measured` | IBU/OmniFold paired comparison — feeds a published cross-check |
| 5 | `2d-unfolding/unbinned_1d_study/ptmu_closure_iteration_study.py:141` | `get_pot_scale` | closure study |
| 6 | `2d-unfolding/binned_study/scripts/trace_binned_omnifold.py:58` | `main` | diagnostic trace |
| 7 | `nd-unfolding/make_control_plots.py:68` | `main` | control plots (ND lane) |
| 8 | `nd-unfolding/plot_control_corner.py:74` | `load` | control corner plots (ND lane) |

**What the count changes.** As one site in one file, J36 read as a local wart in the 2D lane. As
eight, three of them production unfolders and two in a lane that had no idea it was affected, it
is a shared idiom: the ratio is recomputed from scratch in every consumer rather than obtained
once from a vetted helper, so there was never a single place to fix it. That is the reason it
propagated, and it is the thing a repair has to address — a corrected `get_pot_scales` in one file
leaves seven copies.

**Bound.** Taint is intraprocedural, so a helper returning a ratio and a caller consuming it count
as one site, not two; and taint arriving via a dict argument is invisible. The 8 is a **floor**.
`.C`/`.cpp` consumers are not swept at all.

## 3. What is NOT claimed

- **No published number is withdrawn.** Total normalisation is unaffected (§1), and no result here
  is re-derived. Sites 1–4 touch published or cross-checked quantities and the mixture error
  propagates only through playlist-dependent flux shape and detector conditions; quantifying that
  propagation is the scoping question, and it is still open.
- **Nothing was repaired.** Explicitly out of scope for this pass by instruction: size the class,
  then decide.
- **The benign 22 are benign by shape, not by audit.** `RATIO_COMMON_SCALE`, `SCALED_BY_MERGED` and
  `OFFSET_BY_MERGED` are argued safe from the operator and the field sets, not from reading each
  one's physics.

## 4. Rules

1. **After any per-field audit of merged metadata, sweep the DERIVED quantities separately.** The
   per-field question is structurally incapable of reaching a two-field answer, and the derived
   site can be in a different file, a different lane, and written by someone who never saw the
   per-field result.
2. **A defect found in one file is a hypothesis about the codebase, not a fact about that file.**
   J36 was filed against `get_pot_scales` in `unfold_2d_omnifold_unbinned.py`; the identical
   function name appears in three files and the identical computation in eight. The cheap check —
   grep the *computation*, not the symbol — was never run in eight days.
3. **When a derived quantity is recomputed in every consumer, the duplication is the defect.**
   Fixing the arithmetic in one place cannot work; the repair has to be a single vetted producer.
4. **"Scoping decision owed" is a state that hides a size.** An item parked pending scope should
   carry the count of its instances, because the scope question usually *is* the count question.
