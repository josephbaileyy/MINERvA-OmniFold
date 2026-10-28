# DECLARATION 3D, AMENDMENT 1: Stage G's own χ² arithmetic, a matrix-level swap check, and the fixture in the real regime (2026-10-28)

**By** the measurement session, for the director to merge and re-bind.

**Amends** [`FD-FLUX-BOOT-DECLARATION.md`](FD-FLUX-BOOT-DECLARATION.md) (sha256 `a5166316…`), as bound by
[`FD-FLUX-BOOT-BINDING.md`](FD-FLUX-BOOT-BINDING.md) (PR #430). The declaration's text is unchanged. This record
replaces the parts named in §6.

**After** the STOP at the bound deploy's tests (`fd/flux-boot-report`, `79c013ac`) and the director's ruling on it:
option (a), repair the fixture, under eight constraints. Each constraint is quoted where it is met. One independent
review of this amendment's first head, `5d0105f8`, is folded in (§9).

**MEASURES:** nothing on real inputs. Everything below ran on synthetic fixtures, locally and on Perlmutter login
nodes, apart from the read-only probes of the real flux block in §3.
<!-- absence-ok: a scoping statement: this amendment's tool and tests have run only on synthetic fixtures; the real run is the re-binding's -->

**CANNOT AUTHORIZE:**
- the run, which needs the director's amendment binding;
- any change to B2's tolerance, which stays 10⁻¹⁰ in the tool and the declaration;
- any reading, claim or printed wording.

**CITABLE FOR:**
- the cause of the STOP and the fix;
- the new control B6, and what B2 now tests;
- the fixture's regime and the measured margins;
- the new digests, test count and receipts.

**NOT CITABLE FOR:** B2's margin on real inputs, which is measured for the first time in the run.

## 1. The cause

**The STOP.** On login12, B2 refused the synthetic `BootTree` fixture at worst 1.025 × 10⁻¹⁰, against its tolerance
of 10⁻¹⁰. Locally the same fixture passed at 9.4 × 10⁻¹¹.
- Both platforms are OpenBLAS:
  - login12's root_6_28 links `libblas`, `libcblas` and `liblapack` to `libopenblasp-r0.3.30.so` (x86-64);
  - the laptop runs OpenBLAS64 0.3.23.dev (arm64).
- So the STOP came from a difference in OpenBLAS version, CPU architecture or threading, not in BLAS family. The
  conda `blas` metapackage's version, 3.9.0, is not the library's.
- All seven failing tests had the one cause.

**Where it is: the shape-only χ², not the total.** Measured by
[`fd/receipts-flux-boot/amendment-1/diagnose.py`](fd/receipts-flux-boot/amendment-1/diagnose.py) and `.log` on the
pre-amendment fixture:

| prediction | pre-amendment against Stage G, total | the same, shape-only | κ(M) | κ(shape-only matrix) |
|---|---:|---:|---:|---:|
| genie_cv | 1.0e-14 | 3.9e-11 | 3.7e+02 | 9.3e+06 |
| genie_mec | 6.2e-15 | 1.0e-12 | 4.9e+02 | 1.2e+07 |
| nuwro | 1.1e-14 | 6.2e-11 | 4.7e+02 | 1.1e+07 |
| gibuu | 4.4e-16 | 1.9e-11 | 2.2e+01 | 4.8e+05 |
| mnvtune_v1 | 3.1e-15 | 9.4e-11 | 2.8e+02 | 6.9e+06 |

**What produces it.**
- **Stage G** computes the shape-only χ² in absolute units: it forms M + 100 f fᵀ, then takes a Cholesky
  (`fd_g_compare.compare`). The free-normalization term is about 10⁴–10⁵ times M's entries.
- **The pre-amendment tool** first re-expressed Stage G's matrix relative to f, dividing it by f fᵀ entry by entry. It
  then added 100·11ᵀ.
- **Exact rational arithmetic shows the two are different problems.** Run on each representation's own float problem,
  the two exact χ² differ by up to 8.0 × 10⁻¹¹ (the pre-amendment fixture) and 1.1 × 10⁻¹⁰ (the amended one).
- No arithmetic inside the relative representation can reproduce Stage G's value to better than about 10⁻¹⁰.

**The shape-only χ² is not well conditioned in M; the free-normalization term limits it.**
- A relative perturbation of M of 10⁻¹⁶ is absorbed when the term is added, and does not move the shape-only χ².
- Larger ones do. The reviewer's sweep (`amendment-1/review/perturb.py`, `.log`) moved the shape-only χ² by:
  - a median 1.6 × 10⁻¹¹ at 10⁻¹³ relative;
  - a median 2.5 × 10⁻¹¹ at 10⁻¹².
- Stage G's own float value is itself up to 4.3 × 10⁻¹¹ from its exact value (`diagnose.log`, amended fixture).
- **The fix (§2) does not reduce that error.** It copies Stage G's rounding, so that 3D's identity reproduces Stage G's
  committed value.

**Making the fixture more degenerate makes the old path worse.** On the amended fixture, the pre-amendment arithmetic
refuses locally too, at up to 1.3 × 10⁻¹⁰ (`diagnose.log`; the review measured 1.309 × 10⁻¹⁰). So de-correlating was
never the repair.

## 2. The fix (constraint 1: B2's tolerance stays 10⁻¹⁰)

### 2.1 Every χ² by Stage G's own arithmetic

Every χ² is now Stage G's own `compare()`, in absolute units. It is taken on a matrix from one helper,
`swapped(C_stage_g, C, C0) = C_stage_g + (C − C0)`:
- C_stage_g is the matrix Stage G's reported comparison passed, C_total + C_resp, which D5 checks;
- C is the block swapped in: the identity's rebuild, a replicate's variant, or `uniform`;
- C₀ is S1's block.

The new `chi2s(f, g, Vg, C, cells)` calls `fd_g_compare.compare`, and returns None if a Cholesky fails.

Unchanged:
- the correlations (`correlation_band`, `correlation_s1`), still relative to f;
- `fd_g_followup`, which is no longer imported; `code_sha256` drops it.

### 2.2 B6, a new declared control: every swap is the declared swap

**The check.** Every matrix passed to `chi2s` is compared with an independent sum of its parts:
- S1's other blocks;
- C_model_abs, as diag(f) SᵀS diag(f);
- C_resp;
- the swapped block.

Its largest relative difference must be at most 10⁻¹² (`TOL`). It covers the identity, the 4,000 replicate variants
and `uniform`. B6 runs after B5. It refuses like the other controls: exit 1, with nothing written.
- Fixture worst: **1.5 × 10⁻¹⁶**, locally and on login38.
- **Tests:**
  - `test_b6_a_swap_that_scales_the_difference_by_one_plus_1e_6` is a swap error too small for B2 or B4, which only B6
    sees;
  - `test_gross_swap_errors_refuse_before_b6`: a doubled difference refuses at B4, and a swap without C_resp at B2.
- **What B6 adds, and what it doesn't** (the focused re-review's finding 1):
  - It is in effect "the swap helper is the declared swap", plus a re-check of D2's identity: S1's other blocks + C_model
    + C_resp = Stage G's matrix less S1's flux block.
  - D2 already checks that identity and refuses first, so B6's independent sum of parts is never what fails. A mutant
    that builds B6's parts as `C_stage_g − C0` survives every test.
  - On the real inputs the re-review measured that identity's residual at 3.1 × 10⁻¹⁶ of max |C_total|, from the
    fetched `s1_assembly.npz`, so B6 is expected to pass there.

### 2.3 What B2 now tests

**Its clause and tolerance are unchanged.** It still requires the rebuilt block, swapped in, to reproduce Stage G's
committed total and shape-only χ² for every prediction, to 10⁻¹⁰.

**What it can catch has changed:**
- It runs Stage G's own code on Stage G's matrix plus the difference between the rebuild and S1's block, C₁ − C₀. It is
  a reproduction check: the committed Stage G χ², the swap path and `compare()` must agree on these inputs.
- **It catches gross errors in the swap path.** A swap that drops C_resp refuses at B2 (`test_gross_swap…`).
- **It does not add power over B1 for the rebuild itself.** A rebuild at B1's edge, max |C₁ − C₀| = 10⁻¹² of the
  largest entry, moves B2 by only 2.5 × 10⁻¹¹ (`review/perturb.log`). B1 is the rebuild's guard, and B6 the swap's.
- **It cannot see an ulp-level misrouting of the identity.** Mutants that drop the rebuild or flip its sign on B2's own
  line change the identity's matrix by C₁ − C₀ only, which is a few ulp.
  - On the fixture, they are caught by a new test, `test_the_identity_is_stage_gs_compare_on_the_declared_swap_bit_for_bit`.
    It checks the identity record against `compare()` on the declared swap, bit for bit.
  - On real inputs, no control can see them.

**In the first round of this amendment, B2's 0.0 was by construction, not measured.** The fixture's rebuild equalled
S1's block bit for bit, so B2 ran D5's code on D5's bits. The fixture now has the real block's last-bit difference (§3),
and B2 carries it: **worst 3.9 × 10⁻¹⁴ locally and 3.5 × 10⁻¹⁴ on login38**.

**On real inputs:**
- The real rebuild differs from S1's block by up to 27 ulp, 1.75 × 10⁻¹⁵ of its largest entry
  (`review/realblock.log`).
- Carried through the swap on the fixture, that real difference pattern moves the total χ² by at most 9.1 × 10⁻¹⁵, and
  the shape-only χ² by 0 (`review/realdelta.log`).
- That is the expectation. B2's margin on real inputs is measured in the run.
  <!-- absence-ok: a scoping statement: B2 has not yet run on real inputs -->
- **If B2 refuses the real inputs, that is a STOP to the director.** The tolerance is never widened after the real
  inputs have been seen.

## 3. The fixture, in the real regime (constraint 2)

**The real flux block** was computed exactly, read-only, from the 100 committed universes and the constraint file's
weights (`e38ad7d2…`). Its σ/f matches the S1 readout's to 6.2 × 10⁻¹⁷ absolute, 1.8 × 10⁻¹⁵ relative
(`review/sigma.log`).

**The amended fixture** keeps the declaration's construction: a common scale, a tilt and noise per universe, with
lognormal weights.
- Its widths are 0.0325, 0.0092 and 0.00093, against 0.035, 0.01 and 0.004 before.
- S1's block in the fixture is the rebuild plus k ulp per entry, with k a symmetric random integer in [−27, 27]. It
  therefore differs from its rebuild by **at least as much as the real block does**: up to 27 ulp, with a mean of about
  13.7 ulp and 4.4 × 10⁻¹⁵ of its largest entry (B1's worst).
  - The re-review measured the real rebuild against S1's block: 96 % of entries differ, with a median of 5 ulp, a mean
    of 6.3, a maximum of 27, and 1.75 × 10⁻¹⁵ of the largest entry.
  - So the fixture errs on the harsher side.

| | real block | amended fixture | pre-amendment fixture |
|---|---:|---:|---:|
| correlation range | 0.913–0.998 | 0.913–0.999 | 0.900–0.993 |
| median correlation | 0.978 | 0.990 | — |
| pairs at or above 0.97 | 65.8 % | 77.5 % | — |
| 95th percentile | 0.9965 | 0.9991 | — |
| λ_min (relative to f) | 2.19e-07 | 2.32e-07 | 4.30e-06 |
| λ_max | 2.08e-02 | 2.12e-02 | 2.48e-02 |
| n_eff | 19.06 | 19.00 | 19.00 |
| rebuild against S1's block | 27 ulp, 1.75e-15 | ≤ 27 ulp, 4.4e-15 | bit for bit |

Sources: the real block's row is from `review/realblock.log`, `diagnose.log` and §1's computation; the fixtures' rows
are from `diagnose.log` and the Regime test.

**A correction.** The range quoted in correspondence, 0.97–0.998, is only the real block's upper part. Its minimum is
0.913.

**The fixture errs toward more degenerate,** which is the safe direction: its median correlation and its share of
pairs at or above 0.97 are both higher than the real block's.

**Pinned by `Regime.test_the_fixtures_flux_block_is_in_the_real_blocks_regime`:**
- maximum correlation at least 0.997;
- minimum between 0.90 and 0.93;
- λ_min between 1 and 5 × 10⁻⁷;
- λ_max between 1.5 and 3 × 10⁻²;
- n_eff 19 ± 0.3;
- the rebuild not bit-identical to S1's block, and at most 28 ulp from it.

## 4. The measured margins (constraint 3)

| platform | BLAS | declared suite | B1 worst | B2 worst | B6 worst | receipt |
|---|---|---|---:|---:|---:|---|
| Perlmutter login38, root_6_28 | OpenBLAS 0.3.30 | **Ran 207 tests, OK** | 4.4e-15 | **3.5e-14** | 1.5e-16 | `login-suite-2.sh`, `login-suite-2.out` |
| laptop | OpenBLAS64 0.3.23.dev | **Ran 207 tests, OK** | 4.4e-15 | **3.9e-14** | 1.5e-16 | `tests-local.log`, `diagnose.log` |

**B2's worst is at most 10⁻¹² on both platforms,** now with a non-zero difference carried through the swap.

**The login-node run** (2026-10-28T04:26:25–04:29:57Z) used a clean detached clone of `a7b288ea`, this round's code
commit.
- Its porcelain was 0 before and after.
- The clone was in `/pscratch/sd/j/josephrb/scratch-3d-amend-20261028T042625Z`, outside both `$B` roots, with TMPDIR
  inside it. It was removed afterwards and confirmed gone.
- The first round's run, at `d8f706fc` on login12, is kept as `login-suite.sh` and `.out`.

**The end-to-end test asserts B2 ≤ 10⁻¹² for every prediction.** That assertion holds on the platforms where the suite
has run: the two above. It is not a guarantee on any other.

**Later commits change no code.** The tool and test digests in §5 are the ones the login node measured.

## 5. New §8 digests, test count and mutants (constraint 5)

| file | sha256 | changed |
|---|---|---|
| `nd-unfolding/fd_flux_boot.py` | `f82bd4f461ac05eb6080da403a94a06dc7e9ba5c169bf3000b678178befbbbd9` | **yes** (§2); was `48c6eb04…` |
| `nd-unfolding/tests/test_fd_flux_boot.py` | `00b3ba426b5aefa68a36ed5790d698b2576968430876a3febb339c753d020614` | **yes** (§2, §3); was `84d724ce…` |
| `nd-unfolding/fd_g_followup.py` | `ec8cbc6880f7a3f67eea5703ddeff958acb10462053696d2cfdb64de0ee5f60d` | no; not imported by the tool, still in the deploy's test set |
| `nd-unfolding/fd_g_diag.py` | `241bfd0228907e5488f13b7fd50bd490edd97a77cf283a8fb88d3dc6d8bdcc03` | no |
| `nd-unfolding/fd_g_compare.py` | `0a3c09cdf2e27821c488c8a0d783af1537714144cce5415c6cb226ec8096df1f` | no |
| `nd-unfolding/s1_assemble.py` | `b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7` | no |
| `…/s1/readout/s1_assembly.json` | `81e5ef3fe8e7b055360dc43b8a8240c9b5c39c8aa6e7c507b3211d305b326b21` | no |
| `…/fd/readout/fd_g_readout.json` | `75a9ddee19a7affe7e3bc10bf0cba8e5ebaa71132686e5ae116f1454d7bafcee` | no |

**The tool's bytes changed.** The ruling expected only the test file to. The cause is the tool's arithmetic path (§1).
A test-only repair would have had to de-correlate the fixture (forbidden by constraint 2) or widen B2 (constraint 1).

**Tests:** `test_fd_flux_boot` has **33**: Pure 7, Regime 1, EndToEnd 4, Controls 17, Invocation 2 and CommittedPins 2.
The deploy's suite becomes **"Ran 207 tests"**.

**Mutants** (`amendment-1/mutants.py`, `.log`; 2026-10-28T02:48–03:40Z, on `f82bd4f4…`): **39 of 39 killed.**
- They are the declaration's second-round 30, less "shape-only λ 10", whose code now lives in `fd_g_compare`.
- Ten are new:
  - the review's four on B2's line (B2 without the rebuild, its sign flipped, S1's block swapped for itself, the
    difference doubled), killed on the fixture by the bit-for-bit identity test (§2.3);
  - the review's C_stage_g without C_resp, and `uniform`'s difference with its sign flipped;
  - replicates not swapped;
  - the helper scaling the difference by 1 + 10⁻⁶;
  - B6 always passing;
  - B6's parts without C_resp.
- The first head's "three new mutants touch B2" is withdrawn: only one did, a trivial mismatch of units.
- After every mutant the tool was restored, and its sha256 checked.

## 6. Parts of the declaration this replaces

- **§0, "The two variants" and "The statistic and its bands":** each swapped block enters through `swapped()` and
  Stage G's `compare()`, in absolute units. Everything else is as declared.
- **§2.1:** "Ran 203 tests" becomes **"Ran 207 tests"**. The commands are unchanged.
- **§2.2:** the argv is unchanged. The deploy root becomes **`B=/pscratch/sd/j/josephrb/fd-flux-boot-20261028`**
  (constraint 7). It was absent on login12 at 2026-10-28T00:59:39Z.
  <!-- absence-ok: `ls -d /pscratch/sd/j/josephrb/fd-flux-boot-20261028` on login12 at 2026-10-28T00:59:39Z printed 'No such file or directory' -->
  `/pscratch/sd/j/josephrb/fd-flux-boot-20261027` stays untouched as the STOP's evidence. Both join the retention list.
- **§3:** B0–B5's clauses and tolerances are unchanged. **B6 is added** (§2.2). **What B2 can catch is §2.3's.**
- **§4.4:** G-FOLLOWUP's `prediction_blocks` is no longer used. Stage G's `compare` is.
- **§5:** `controls_passed` ends with `B6`, and `code_sha256` lists `fd_flux_boot.py`, `fd_g_diag.py`, `fd_g_compare.py`
  and `s1_assemble.py`.
- **§6.2:** the counts in §5 above, with `Regime` and the amended `BootTree`.
- **§6.3:** "30 one-line mutants … the four non-pin test classes" becomes 39 mutants and the five non-pin classes
  (`Regime` is added).
- **§8:** the digests in §5 above.
- **§11's mutation outcome:** superseded by §5 above.

## 7. Receipts

`fd/receipts-flux-boot/amendment-1/`:
- `diagnose.py` and `diagnose.log`: §1's measurements on both fixtures, at `a7b288ea`;
- `login-suite-2.sh` and `login-suite-2.out`: §4's login-node suite with B1, B2 and B6, at `a7b288ea`;
- `login-suite.sh` and `login-suite.out`: the first round's run, at `d8f706fc`;
- `tests-local.log`: the local suite, at `a7b288ea`;
- `mutants.py` and `mutants.log`: §5;
- `review/`: the reviewer's probes as they ran here. The logs are from this session, against the reviewer's copy of
  `5d0105f8`:
  - `realblock.py` and `.log`: the real block's regime, and its 27-ulp rebuild;
  - `realdelta.py` and `.log`: that difference carried on the fixture;
  - `perturb.py` and `.log`: B2's response to rebuild differences;
  - `sigma.py` and `.log`: σ against the readout;
  - `my_mutants.py`: the reviewer's mutant list.

  The probes read fetched, read-only copies of `s1_assembly.npz` (`db000707…`) and the constraint file (`e38ad7d2…`).
  Neither is committed.

The STOP's receipts stay on `fd/flux-boot-report` (`79c013ac`), with its ledger row (constraint 8).

## 8. Constraints, as met

1. **B2's tolerance is unchanged at 10⁻¹⁰,** in the tool and the declaration. A refusal on real inputs is a STOP.
2. **The fixture is in the real regime (§3),** and its rebuild differs from S1's block by at least as much as the real one
   does. The cause
   is fixed at its source (§1–2).
3. **B2's worst is at most 10⁻¹² on both platforms (§4):** 3.9 × 10⁻¹⁴ locally and 3.5 × 10⁻¹⁴ on login38, measured
   with a non-zero difference. The suite ran on a login node, in a scratch clone at the amendment's code head, and its
   log is committed.
4. **Constraints 2 and 3 are both met.**
5. **All 39 mutants are killed on the final bytes.** The tool's bytes changed; its new digest is in §5.
6. **This record; the PR follows after review.**
7. **The deploy roots,** as in §6.
8. **The report branch,** as in §7.

## 9. Review dispositions (the independent review of `5d0105f8`)

**The review found no blocker and no rule violation.** It reproduced the diagnosis: with the old tool, B2 was
9.382 × 10⁻¹¹ on the old fixture and 1.309 × 10⁻¹⁰ on the new one; with the new tool, 0.0 on both. It found the
routing algebraically right for all three variants, and the digests, the login-node log, the roots and the counts
verified.

1. **Medium-high: B2 could no longer fail on its own.** Done.
   - The fixture's S1 block now differs from its rebuild by up to 27 ulp (§3).
   - B6 is added (§2.2).
   - A bit-for-bit identity test is added.
   - The review's four B2-line survivors, and two more of its mutants, are in the set, and all are killed.
   - The overclaims are corrected (§2.3, §4, §5): constraint 3's earlier 0.0 was by construction, the margin test holds
     only where it has run, "three new mutants touch B2" is withdrawn, and "every control's clause unchanged" is
     replaced by §2.3's statement of what B2 now tests.
2. **Medium: "reference BLAS 3.9.0" was wrong.** Both platforms are OpenBLAS (0.3.30 against 0.3.23.dev), and the STOP
   was a version, architecture or threading difference (§1). The CATALOG row is corrected too.
3. **Low-medium: "well conditioned" misread its probe.** §1 now gives the reviewer's sweep, and says that the fix
   copies Stage G's rounding rather than reducing the error. The real-input expectation uses the real 27-ulp
   difference (§2.3).
4. **Low: the fixture's bulk** is added to §3's table.
5. **Low: declaration §6.3 and §11's outcome** are listed as replaced (§6).
6. **Trivial: σ's unit** is given (§3).

**A focused re-review of `80a7d3eb`** found every finding above resolved, with nothing blocking. It ran ten mutants of
its own: nine die, and the survivor is item 1 below. Three low findings, folded in:
1. **B6's independent sum of parts is never what fails,** because D2 refuses first. §2.2 now says what B6 adds and what it
   doesn't. It also gives the re-review's real-input residual, 3.1 × 10⁻¹⁶.
2. **The fixture's last-bit difference is harsher than the real one,** not "as the real block does". §3 gives both
   distributions.
3. **"A relative 4.9" had no source.** It is dropped. The test asserts that B2 refuses.
