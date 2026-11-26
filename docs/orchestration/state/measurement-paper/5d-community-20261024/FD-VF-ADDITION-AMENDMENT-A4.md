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
   - **e2sens:** the removed, carbon, doubled and CH chi2 of each corner prediction in both arms, from the same Stage G
     records. Each is compared on its carbon chi2's scale.
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

## xk's local replay: three input substitutions (the director's rulings (i)–(iii), 2026-11-26)

xk is GENCMP X step K, replayed through `fd_xcov_steps.cmd_k` under `--products g2r` (route (1)). No arithmetic
changes. Only inputs are substituted, and only in the replaying process:

- **(i) I/O remap.** `fd_gencmp.read_noatime` is wrapped so that only the exact prefix `/pscratch/sd/j/josephrb/`
  maps to the verified fetch at `/Users/josephbailey/vf-p2-fetch-20261126/`.
  - A remapped path that is missing, or not a regular file, raises. Nothing falls through to another path.
  - Every remapped read is logged (path, size, sha256). The logged set must be a subset of the bound fetch list's xk
    entries, at their pins; listed entries the replay never reads are named.
  - Every pin, key and sha check is the producer's own.
  - **One exact-path entry (FD-VF BINDING 2b, the director's ruling 1).** The NuE flux constraint's path,
    `/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt`,
    maps to the committed byte-identical copy
    `docs/orchestration/state/ben-b-20261124/blocks5d-20261124/run-20261124/session/records/fetch-b5d/sorted_NuEConstraint_FHC_RHC_IMD.txt`
    (B5D's fetch record; sha256 `e38ad7d2…`, equal to the pin).
    - That NERSC path runs through a symlinked directory (`MParamFiles`); the fetch's first attempt stopped on it by
      design, so the file is not fetched.
    - K's own pin check still applies, and the read is logged like every other remapped read.
- **(ii) A local run directory.** It holds hardlinks to the fetched `cov2d-xk-g2r-20261116/run` copy, plus the
  committed `fd/xcov/run/v0-a1/v0.json` and `v1-a2/v1.json`. Their sha256 must equal `NODE-SHA256.txt`'s run copy.
  - The file list and shas are recorded before and after.
  - K may only add files under `k/`.
- **(iii) The V_F inputs.** `read_committed` returns two substituted objects, each recorded by sha256:
  - for `CPL_BLOCK`, the block with `C_total_plus_C_resp_plus_C_PL5D` replaced by C_rep,F, so that
    C16q = A (C + ΔC_e) Aᵀ + box variance. That is declaration §4.1's "A dF Aᵀ added to the 16-cell side";
  - for `CR_G2R`, Phase 2's `cr.vf.json`, so that K0's own 1e-12 check holds against the V_F σ16.

  The code asserts that the V_F replay differs from the OLD replay only in those two returns: the same
  `read_committed` call sequence, the same other returns by sha, and the same remapped reads.
- **OLD control.** The replay with only (i) and (ii) must reproduce G2R's committed `k.json` (`204e4c89`) at 1e-12 in
  every field except `inputs` and `atime_deviations`, which record the run's paths and atimes.
  - Anything above 1e-12 for bit-identical inputs is a STOP to the director.
  - Round-tripped values, if K reads any, are named with their achieved differences first.
  - The result: (to be filled in from the replay).

**CANNOT AUTHORIZE:** anything beyond the changes above.
