# AMENDMENT A4 to FD-VF-ADDITION-DECLARATION.md: control P's tolerance on this platform, for round-tripped inputs (2026-11-26)

**By** tier3-design. **Ruled by** the director on 2026-11-26: option (a), then the p-value check by function identity.
The amendment is for binding with the Phase 2 code.
**Amends** `FD-VF-ADDITION-DECLARATION.md` (sha256 `31662736e85f83e3772722fa9ec633ae4f8a9add2fd37c111b801f058dcfe39f`)
§6, control P. Nothing else changes.

## Widened after a failure, and why

**This tolerance was widened after the declared 1e-10 check failed.** Phase 2 runs locally (macOS, Python 3.12.2,
numpy 1.26.4 with OpenBLAS). Its first two recomputes against NERSC-computed readouts missed §6 P's 1e-10 for fields
whose input was round-tripped through a readout.

The evidence that the miss is a platform effect, not an error:
- **e2:** `fd_gencmp_e2.chi2_rows`, imported unchanged, reproduces the committed chi2 to at most 2.49e-10 relative.
  The deltas reproduce to 3.2e-10 on their chi2's scale; relative to the deltas themselves that is 2.6e-8, because a
  small difference of two chi2 values cancels.
- **E2's own control C3** (carbon S against E-1's Stage G chi2, at 1e-10) passed on login37 and gives 1.56e-10 on this
  Mac.
- **Threads don't matter:** with single-threaded BLAS the result is unchanged, 2.49e-10. The difference comes from the
  platform's linear-algebra kernels.
- **The platform control:** gch, which was originally computed on this Mac, reproduces bit for bit, 0 in every field
  of its 28 records. gdefs and gnat were computed on NERSC. Their pulls, which use only diag(M), are exact; only the
  Cholesky-solved chi2 differs, at ≤ 1.95e-10.
- **The margin to every decision rule and printed digit is many orders of magnitude.** That covers E2's
  "Δmax ≤ 2 Δnoise,max", the 2.3 flag, and p = 0.01.

## The change

1. **Bit-identical inputs keep 1e-12.** eav's exact pass is the precedent; so are gover's, cr's and gch's.
2. **Fields whose input was round-tripped through a readout get 1e-9 relative on this platform.** Those fields are:
   - **e2:** the chi2 of each corner prediction (carbon, CH, carbon seed 43) in both arms, where V_g = (σ_Vg/f · f)²
     comes from E-1's Stage G records. Each delta and Δ field is compared on its chi2's scale, and its delta-relative
     figure is recorded so the cancellation stays visible.
   - **gdefs and gnat:** the total and shape-only chi2 of every embedded `fd_g_compare.compare` record, where V_g comes
     from σ_Vg/f.
3. **p is derived through its chi2.** The chi2 tolerance is not widened for p.
   - Each committed p must equal `fd_g_compare.chi2_sf(committed chi2, ndf)` **bitwise**, in every record. That proves
     the function and its inputs.
   - Each reproduced p must give the committed p's printed strings: `make_values_fived16.p_tex` and its paper form.
   - The reproduced p's remaining difference comes only through chi2, since d ln p/dχ² ≈ −½. It is recorded: up to
     2.18e-8 in gdefs and 1.77e-8 in gnat.
4. **The Table IV corner.** gdefs' "CH, analysis definitions" records for the four GENCMP predictions take Phase 1's V_F
   Stage G records, which were computed on login02.
   - E-1's control XC makes the two the same computation, and `make_values_fived16.table4` asserts their equality at
     1e-12.
   - The local recompute must first agree with them within 1e-9. Achieved: 5.9e-11.
5. **Every field's achieved difference is recorded in `vf_patch`.** The Phase 2 receipt names the platform, the numpy
   build and BLAS.
6. **The hard limit.** Any field above 1e-9, or any field a printed value depends on at more than 1e-6 of its last
   printed digit, is a STOP to the director. Nothing is widened further.

**CANNOT AUTHORIZE:** anything beyond the change above.
