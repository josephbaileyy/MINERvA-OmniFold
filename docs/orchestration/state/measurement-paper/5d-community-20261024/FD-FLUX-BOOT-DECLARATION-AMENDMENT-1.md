# DECLARATION 3D, AMENDMENT 1: Stage G's own χ² arithmetic, and the fixture in the real regime (2026-10-28)

**By** the measurement session, for the director to merge and re-bind.

**Amends** [`FD-FLUX-BOOT-DECLARATION.md`](FD-FLUX-BOOT-DECLARATION.md) (sha256 `a5166316…`, bound by
[`FD-FLUX-BOOT-BINDING.md`](FD-FLUX-BOOT-BINDING.md), PR #430). The declaration's text is unchanged. This record
replaces the parts named in §6.

**After** the STOP at the bound deploy's tests, recorded on `fd/flux-boot-report` at `79c013ac`, and the director's
ruling on it: option (a), repair the fixture, under eight constraints. Those constraints are quoted where each one is
met.

**MEASURES:** nothing on real inputs. Everything below ran on synthetic fixtures, locally and on a Perlmutter login
node.
<!-- absence-ok: a scoping statement: this amendment's tool and tests have run only on synthetic fixtures; the real run is the re-binding's -->

**CANNOT AUTHORIZE:**
- the run, which needs the director's amendment binding;
- a change to B2's tolerance, which stays 10⁻¹⁰ in the tool and the declaration;
- any reading, claim or printed wording.

**CITABLE FOR:** the cause of the STOP, the fix, the fixture's regime, the measured margins, and the new digests, test
count and receipts.

**NOT CITABLE FOR:** B2's margin on real inputs. That is measured for the first time in the run.

## 1. The cause

**The STOP.** On login12, B2 refused the synthetic `BootTree` fixture: worst 1.025 × 10⁻¹⁰ against 10⁻¹⁰. Locally,
under OpenBLAS, the same fixture passed at 9.4 × 10⁻¹¹. All seven failing tests had this one cause.

**Where it is: the shape-only χ², not the total.** Measured by
[`fd/receipts-flux-boot/amendment-1/diagnose.py`](fd/receipts-flux-boot/amendment-1/diagnose.py) and its `.log`, on
the pre-amendment fixture:

| prediction | pre-amendment against Stage G, total | the same, shape-only | κ(M) | κ(shape-only matrix) |
|---|---:|---:|---:|---:|
| genie_cv | 1.0e-14 | 3.9e-11 | 3.7e+02 | 9.3e+06 |
| genie_mec | 6.2e-15 | 1.0e-12 | 4.9e+02 | 1.2e+07 |
| nuwro | 1.1e-14 | 6.2e-11 | 4.7e+02 | 1.1e+07 |
| gibuu | 4.4e-16 | 1.9e-11 | 2.2e+01 | 4.8e+05 |
| mnvtune_v1 | 3.1e-15 | 9.4e-11 | 2.8e+02 | 6.9e+06 |

**What produces it: the tool, not the fixture.**
- **Stage G's computation.** Stage G computes the shape-only χ² in absolute units: M + 100 f fᵀ, then Cholesky
  (`fd_g_compare.compare`). The free-normalization term is about 10⁴–10⁵ times M's entries. So forming M + 100 f fᵀ in
  floating point rounds M at about 10⁻¹¹ relative.
- **The pre-amendment tool's computation.** It re-expressed Stage G's matrix relative to f, by dividing by f fᵀ entry
  by entry. It then added 100·11ᵀ. Each representation rounds M differently when that term is added.
- **Exact rational arithmetic confirms it.** On each representation's own float problem, the two exact χ² differ by up
  to 8.0 × 10⁻¹¹. Stage G's float value is within 2.0 × 10⁻¹¹ of its own exact one. No arithmetic inside the relative
  representation can reproduce Stage G's value to better than about 10⁻¹⁰.
- **The χ² itself is well conditioned in M.** A 10⁻¹⁶ relative perturbation of M per entry moves the total χ² by
  10⁻¹⁶ to 7 × 10⁻¹⁵, and the shape-only χ² by 0. The loss is in the representation in which the term is added, not
  in the problem.
- **Making the fixture more degenerate makes it worse under the old path.** The pre-amendment arithmetic on the amended
  fixture (§3) would refuse locally too, at up to 1.3 × 10⁻¹⁰. That is why de-correlating the fixture was never the
  repair.

## 2. The fix (constraint 1: B2's tolerance stays 10⁻¹⁰)

**Every χ² is now Stage G's own `compare()`, in Stage G's absolute units, on Stage G's matrix with the flux block's
difference added:** C_stage_g + (C − C₀).
- C_stage_g is the matrix Stage G's reported comparison passed: C_total + C_resp, as D5 checks.
- C is the swapped block (the identity, a replicate's variant, or `uniform`), and C₀ is S1's block.
- The new `chi2s(f, g, Vg, C, cells)` calls `fd_g_compare.compare` and returns its total and shape-only χ², or None if
  a Cholesky fails. It replaces the relative-unit `chi2s(d, M)`.

**Why this removes the cause.**
- For the identity, C − C₀ is S1's block against its rebuild. B1 measures that difference, and on both fixtures it is
  0 exactly. So B2 compares Stage G's own matrix, through Stage G's own code, with Stage G's committed value.
- On the real inputs, S1 built C₀ on compute nodes, so the rebuild may differ from it in the last bits. A perturbation
  of that size leaves the shape-only χ² unchanged (§1).
- That is the expectation. The real-input margin is not measured: B2 measures it in the run, for the first time. <!-- absence-ok: a scoping statement: B2 has not yet run on real inputs; the director's correction of 2026-10-28 says the same -->
- On real inputs, G-DIAG's, G-FOLLOWUP's and G-SENS2's D5 each reproduced Stage G's total and shape-only χ² with
  `compare()`, worst 0.0 (`FD-G-DIAG-REPORT.md:62`; `FD-G-FOLLOWUP-REPORT.md:38`; `FD-G-SENS2-REPORT.md:32`). G-DIAG
  ran on login37, as Stage G did, and G-SENS2 on login09 (`fd/LEDGER.tsv`).

**Also changed in the tool:**
- the `units` label;
- the docstring;
- `fd_g_followup` is no longer imported, since `prediction_blocks` is unused, so `code_sha256` no longer lists
  `fd_g_followup.py`.

The correlations (`correlation_band`, `correlation_s1`) are unchanged, and still relative to f.

**Not changed:**
- B2's tolerance, 10⁻¹⁰ (`REPRO`);
- every control's clause;
- the replicate scheme, seed, B, percentiles, variants, pair and argv;
- the readout's keys, except `code_sha256`.

**If B2 refuses the real inputs, that is a STOP to the director.** The tolerance is never widened after the real inputs
have been seen.

## 3. The fixture, in the real regime (constraint 2)

**The real flux block** was computed exactly from the 100 committed universes and the constraint file's weights. Its σ
matches the S1 readout's to 8 × 10⁻¹⁷.
- Correlations: **0.913–0.998**.
- λ_min: **2.19 × 10⁻⁷** relative to f; λ_max 2.08 × 10⁻².
- n_eff: 19.06.
- The constraint file was fetched read-only; its sha256 is `e38ad7d2…`, the pin.
- **A correction:** the range quoted in correspondence, 0.97–0.998, is its upper part. The measured minimum is 0.913.

**The amended fixture** keeps the declaration's construction (a common scale, a tilt and noise per universe, with
lognormal weights). Its widths are set to the real block's: common 0.0325, tilt 0.0092 and noise 0.00093, against
0.035, 0.01 and 0.004 before.

| | correlation range | λ_min (relative to f) | λ_max | n_eff |
|---|---|---:|---:|---:|
| **real block** | 0.913–0.998 | 2.19e-07 | 2.08e-02 | 19.06 |
| **amended fixture** | 0.913–0.999 | 2.32e-07 | 2.12e-02 | 19.00 |
| pre-amendment fixture | 0.900–0.993 | 4.30e-06 | 2.48e-02 | 19.00 |

**Pinned by the new test `Regime.test_the_fixtures_flux_block_is_in_the_real_blocks_regime`:**
- maximum correlation at least 0.997;
- minimum between 0.90 and 0.93;
- λ_min between 1 × 10⁻⁷ and 5 × 10⁻⁷;
- λ_max between 1.5 × 10⁻² and 3 × 10⁻²;
- n_eff 19 ± 0.3.

## 4. The measured margin (constraint 3: B2 at most 10⁻¹² on both platforms)

| platform | numpy, BLAS | declared suite | B2 worst on the fixture | receipt |
|---|---|---|---:|---|
| Perlmutter login12, root_6_28 | 1.26.4, `blas` 3.9.0 | **Ran 204 tests, OK** | **0.0** for all five | `login-suite.sh`, `login-suite.out` |
| laptop | 1.26.4, OpenBLAS64 0.3.23.dev | **Ran 204 tests, OK** | **0.0** for all five | `tests-local.log`, `diagnose.log` |

**The login-node run** (2026-10-28T00:56:36–00:59:09Z):
- It used a clean detached clone of `d8f706fc`, the amendment's code commit, with porcelain 0 before and after.
- The clone was in `/pscratch/sd/j/josephrb/scratch-3d-amend-20261028T005636Z`, outside both `$B` roots, with TMPDIR
  inside it. It was removed afterwards, and confirmed gone.
- The full suite log is in `login-suite.out`.

**The end-to-end test now asserts B2 ≤ 10⁻¹²** for every prediction, so the margin is a test on every platform it runs
on.

**The amendment's later commits change no code.** The tool and test digests in §5 are the ones the login node measured.

## 5. New §8 digests, test count and mutants (constraint 5)

| file | sha256 | changed |
|---|---|---|
| `nd-unfolding/fd_flux_boot.py` | `2be933e14b8ea055fb63750f63d57024849f301a0cec8ad1e43aa02324d46784` | **yes** (§2); was `48c6eb04…` |
| `nd-unfolding/tests/test_fd_flux_boot.py` | `4648b9d18f43fb0c39f73c1237ba43217fa568a2a3da7e2d5adee9768c5afae1` | **yes** (§3, §4); was `84d724ce…` |
| `nd-unfolding/fd_g_followup.py` | `ec8cbc6880f7a3f67eea5703ddeff958acb10462053696d2cfdb64de0ee5f60d` | no; no longer imported by the tool, still in the deploy's test set |
| `nd-unfolding/fd_g_diag.py` | `241bfd0228907e5488f13b7fd50bd490edd97a77cf283a8fb88d3dc6d8bdcc03` | no |
| `nd-unfolding/fd_g_compare.py` | `0a3c09cdf2e27821c488c8a0d783af1537714144cce5415c6cb226ec8096df1f` | no |
| `nd-unfolding/s1_assemble.py` | `b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7` | no |
| `…/s1/readout/s1_assembly.json` | `81e5ef3fe8e7b055360dc43b8a8240c9b5c39c8aa6e7c507b3211d305b326b21` | no |
| `…/fd/readout/fd_g_readout.json` | `75a9ddee19a7affe7e3bc10bf0cba8e5ebaa71132686e5ae116f1454d7bafcee` | no |

**The tool's bytes changed.** The ruling expected only the test file to change. The cause is the tool's arithmetic
path (§1), so a test-only repair would have meant de-correlating the fixture, which constraint 2 forbids, or widening
B2, which constraint 1 forbids.

**Tests:** `test_fd_flux_boot` has **30** tests, one more than before (`Regime`): Pure 7, Regime 1, EndToEnd 3,
Controls 15, Invocation 2, CommittedPins 2. The deploy's suite becomes **"Ran 204 tests"**.
- `test_chi2s_by_hand…` is replaced by `test_chi2s_is_stage_gs_compare_in_absolute_units_and_none_when_not_positive_definite`.
- B2's planted defect is adapted to the new signature.

**Mutants** (`amendment-1/mutants.py` and `.log`, 2026-10-28T00:56:58Z–2026-10-28T01:08:48Z, on `2be933e1…`): **32 of 32 killed**.
- They are the 30 from the declaration's second round, less "shape-only λ 10", whose code now lives in
  `fd_g_compare`.
- Three new mutants touch B2 and the swap: the swap difference's sign flipped, the replicates not swapped, and B2
  computed in the relative representation.
- The `Regime` class runs with the others.
- The tool was restored, and its sha256 checked after every mutant.

## 6. Parts of the declaration this replaces

- **§0, "The two variants" and "The statistic and its bands":** each swapped block enters as C_stage_g + (C − C₀),
  through Stage G's `compare()`, in absolute units. Everything else is as declared.
- **§2.1:** "Ran 203 tests" becomes **"Ran 204 tests"**. The commands are unchanged.
- **§2.2:** the argv is unchanged. The deploy root changes to **`B=/pscratch/sd/j/josephrb/fd-flux-boot-20261028`**
  (constraint 7). It was absent on login12 at 2026-10-28T00:59:39Z.
  <!-- absence-ok: `ls -d /pscratch/sd/j/josephrb/fd-flux-boot-20261028` on login12 at 2026-10-28T00:59:39Z printed 'No such file or directory' -->
  `/pscratch/sd/j/josephrb/fd-flux-boot-20261027` stays untouched as the STOP's evidence. Both join the retention list.
- **§3, B2:** the clause and the tolerance are unchanged. Its computation is §2's.
- **§4.4:** G-FOLLOWUP's `prediction_blocks` is no longer used, and Stage G's `compare` is.
- **§5:** `code_sha256` lists `fd_flux_boot.py`, `fd_g_diag.py`, `fd_g_compare.py` and `s1_assemble.py`.
- **§6.2:** the counts in §5 above, with `Regime` and the amended `BootTree`.
- **§8:** the digests in §5 above.

## 7. Receipts

`fd/receipts-flux-boot/amendment-1/`:
- `diagnose.py` and `diagnose.log`: §1's measurements on both fixtures;
- `login-suite.sh` and `login-suite.out`: §4's login-node suite and B2 measurement;
- `tests-local.log`: the local suite at `d8f706fc`;
- `mutants.py` and `mutants.log`: §5.

The STOP's receipts stay on `fd/flux-boot-report` (`79c013ac`), with its ledger row (constraint 8).

## 8. Constraints, as met

1. **B2's tolerance is unchanged at 10⁻¹⁰,** in the tool and the declaration. A refusal on real inputs is a STOP.
2. **The fixture is in the real regime (§3).** The cause is fixed at its source, the arithmetic's representation
   (§1–2), not by de-correlating.
3. **B2's worst is 0.0, at most 10⁻¹², on both platforms (§4).** The suite ran on a login node in a scratch clone at
   the amendment's code head, and its log is committed.
4. **2 and 3 are both met,** so no STOP back is needed.
5. **All 32 mutants are killed on the final bytes.** The tool's bytes changed, and the new digest is in §5.
6. **This record;** the PR follows after review.
7. **The deploy roots,** as in §6.
8. **The report branch,** as in §7.

## Not changed

- B2's tolerance, every control's clause, the argv, the replicate scheme and every declared constant.
- G-SENS2's α results, every covariance, cell, readout and κ.
- `docs/analysis-note/**`.
