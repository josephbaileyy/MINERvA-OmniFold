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
   - **The same rule covers rsnregrade and rsn** (the director's ruling 1, 2026-11-26). There the inputs are
     bit-identical, chi2 and z stay at 1e-12 and pass (chi2 9.06e-13, z about 4e-16), and the p function is
     `fd_f0_regrade.chi2_sf_even`. The achieved p difference is 1.71e-11, at rsnregrade
     nominal/records[2]/model_only/p, where p is about 1.7e-17.
   - **prr's IBU grades** (the director's ruling 2). route2.npz's truths are recorded equal to (e)'s B0 truths at
     ≤ 1e-12 (C-IBU), so they are not bit-identical. Outputs graded against them are held to 1e-11 (achieved
     1.07e-12), and above 1e-11 is a STOP. The (e) records keep their own figures under the existing rules: chi2 2.1e-14,
     p 5.5e-13.
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
  - **A second exact-path entry: the MINOS rescale.** It was never fetched, because fetch-list excludes its role as
    committed. `/pscratch/sd/j/josephrb/2d-closeout-c04repair-20261012/build/minos_rescaled.npz` maps to the committed
    copy `docs/orchestration/state/2d-closeout/c04-repair/products/minos_rescaled.npz`, sha256 `8912376e…`. That is the
    pin at `fd/xcov/INPUTS.sha256:13` and the run copy's `NODE-SHA256.txt:233`.
- **(ii) A local run directory.** It holds hardlinks to the fetched `cov2d-xk-g2r-20261116/run` copy, plus the
  committed `fd/xcov/run/v0-a1/v0.json` and `v1-a2/v1.json`. Their sha256 must equal `NODE-SHA256.txt`'s run copy.
  - The file list and shas are recorded before and after.
  - K may add only its readout under `k/` and its own staging copies under `inputs/` (`fd_xcov_steps.stage`). Each
    staging copy must be the bytes of a logged remapped read, at its pin.
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
  - **The result (the director's ruling, 2026-11-26).** The 1e-12 check failed: 360 floats differ from `k.json`, up to
    1.03e-8, and no non-float field differs. The OLD control is therefore held under a named category:
    **"bit-identical inputs; cross-platform rounding (about 1e-16 in the bounded blocks, about 1e-11 in the crosses)
    amplified through the r = 1 bound's psd_sqrt of near-singular blocks (condition up to 1.1e17)"**.
    - Tolerance 1e-7 relative. Every non-float field is exact, and every printed xk string must be identical in the
      readings. Above 1e-7 is a STOP.
    - Achieved: max 1.03e-8 at `/shares/r1/cross:bounded (r = 1)[1]`. Each group's figures are recorded in `vf_patch`,
      as max relative / max |difference| over the group's largest magnitude: shares 1.03e-8 / 7.63e-9; primary
      4.55e-9 / 2.44e-9; Q_R_alone 3.96e-9 / 1.65e-9; C_PL_pair_zero 3.76e-9 / 3.76e-9; rho_q 9.59e-11 / 9.57e-11;
      crosses 1.04e-11 / 4.45e-15.
    - **Evidence: two local tests.** Both are in `fd/receipts-vf/p2/xk-conditioning/`.
      - Thread order: two OLD replays on this Mac with 1 and 3 BLAS threads are bitwise identical, so local summation
        order moves nothing.
      - Conditioning: seeded relative noise, three seeds each, at the measured levels. Noise of 1e-16 on the own blocks
        entering `fd_xcov.bound_matrix` moves the groups by 4.0e-9 to 6.2e-9 (shares), 1.8e-9 to 2.7e-9 (primary),
        1.5e-9 to 2.4e-9 (Q_R_alone), up to 2.5e-9 (C_PL_pair_zero) and 4.8e-11 to 6.8e-11 (rho_q). That is the k.json
        gap within a factor of about 2 in every group. Noise of 1e-11 on the crosses moves them about 10 times less.
        No run changes a non-float field, and the primary outcome is "agree" in all six.
      - The bounded blocks' condition numbers reach 1.13e17 (16-cell side) and 2.08e16 (2D side). V_d at r = 1 is
        benign: 17.7 to 217.
    - **A statement of fact, not a rule:** these r = 1 outputs carry about 1e-8 relative numerical precision on any
      platform, because of the near-singular square roots. Their printed two-decimal and two-significant-figure values
      are far coarser.
    - **The listed run-copy files** (`cov2d-xk-g2r-20261116/run/...`: boot lanes and replicas, `inputs/`) reach K
      through the local run directory, ruling (ii), not through the remap. So they appear among the listed entries not
      read through the remap (110).

**CANNOT AUTHORIZE:** anything beyond the changes above.
