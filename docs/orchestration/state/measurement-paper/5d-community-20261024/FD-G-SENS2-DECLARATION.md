# DECLARATION G-SENS2: flux, detector and lateral each shrunk alone (2026-10-26)

**By** the measurement session, for the director to bind.

**Under:**
- Joseph's approval: `DECISION-20261026-joseph-gsens-per-group-split.md` (PR #393, main `c1987263`), item 2, "(a) is
  approved: the same shrinkage applied to flux alone, detector alone and lateral alone".
- The director's request of 2026-10-26, which sets the items below.

**After:** G-FOLLOWUP ([`FD-G-FOLLOWUP-REPORT.md`](FD-G-FOLLOWUP-REPORT.md), PR #392). Its readout `cd82517a…` holds
interaction alone and the joint family (interaction, flux, detector and lateral).

**An amendment-style follow-up to G-FOLLOWUP.** It uses the same tool, `nd-unfolding/fd_g_followup.py`, behind a new
declared option, `--part sens2`. It uses the same shrinkage, record and label, and the same pinned inputs, with role
`adopted`.

**Declares:**
- the option and its code, which reuses G-FOLLOWUP's shrink and record functions;
- the tests;
- a byte-for-byte identity receipt for the G-FOLLOWUP part;
- the exact argv, the controls, the readout schema and the stop rule.

**MEASURES:** nothing. The new part has not run on Stage G's inputs.
<!-- absence-ok: a scoping statement about this session's own work: the option is new in this commit and has run only on synthetic fixtures -->

**CANNOT AUTHORIZE:**
- running it: the director binds first;
- any reading, claim or printed wording, which are Joseph's;
- any change to a covariance, cell or readout.

**CITABLE FOR:** what G-SENS2 will compute, from which inputs, and what makes it stop.

**NOT CITABLE FOR:** any result.

## 0. Summary

**The families.** There are three new families. Each shrinks one S1 group alone, with G-FOLLOWUP's diagonal-keeping
shrinkage C_g(α) = D^½[(1 − α)ρ + αI]D^½:
- `flux`;
- `detector`;
- `lateral`.

**The α values:** 0 (the reference and control S0), 0.1, 0.25, 0.5 and 1.

**Unchanged in each:** the other six S1 groups (interaction, the two other systematic groups, normalization, stat and
seed), the three C_model vertices, C_resp and V_g. Each record's role is `single group`.

**Not recomputed.** Interaction alone and the joint family are referenced from G-FOLLOWUP's pinned readout
(`cd82517a…`). Control H0 recomputes exactly two of their χ² values from the pinned inputs, as an identity check against
that readout:
- interaction at α = 1, NuWro;
- the joint family at α = 0.25, GiBUU (8 cells).

**For each prediction, family and α,** the record is G-FOLLOWUP's (`sens_record`):
- the χ², ndf, condition number and λ_min;
- the modes carrying 50 %, 90 % and 99 % of the χ²;
- the top mode's relative σ, χ² and fraction, its three leading cells with signed loadings, and all its loadings;
- the stability record and flags;
- the χ² at α = 0;
- the shrunk group's smallest eigenvalue.

Everything is relative to f. There is no p-value, and every record carries the label "descriptive sensitivity of the
reported χ², not an alternative result".

**The addition.** For the flux family, for each prediction:
- **At α = 0 and at α = 0.1,** that matrix's own top mode (the largest χ² contribution, chosen as `sens_record`
  chooses it):
  - its index, σ, χ², fraction and loadings;
  - each block's share vᵀBv/λ, over G-DIAG's 12 blocks (11 without C_resp): S1's seven groups, with flux shrunk at
    that α, the three vertices, C_resp and V_g;
  - the shares' sum and the dominant block;
  - `flux_ratio` = vᵀFv / vᵀdiag(F)v for the unshrunk flux block F. This is the part of flux's variance along v that
    flux's correlations leave; it is 1 for uncorrelated cells.
- **α = 0's top mode followed into the α = 0.1 blocks** (§7 item 1):
  - its direction's variance vᵀMv;
  - each block's share vᵀBv/vᵀMv;
  - the χ² along it alone, (vᵀd)²/vᵀMv, which is descriptive because v is not an eigenvector there;
  - its `flux_ratio`;
  - `overlap_abs` = |v₀ · v₀.₁|, which says whether the two top modes are the same direction.

**Cost:** 0 node-h, on a login node, with no Slurm job and nothing written to CFS.

**Stop rule:** any refusal, any non-zero exit, or a run past 1.25 × its projected wall is reported unrepaired.

## 1. Inputs

G-FOLLOWUP's inputs and pins, unchanged ([`FD-G-FOLLOWUP-DECLARATION.md`](FD-G-FOLLOWUP-DECLARATION.md) §1), checked
by G-DIAG's D0–D5. The G-DIAG readout is replaced by G-FOLLOWUP's:

| input | where | checked against |
|---|---|---|
| G-FOLLOWUP's committed readout | `$T/fd/readout/fd_g_followup_readout.json` | `cd82517afdfb1dc8383580c8a4c57e82d9b87864e75d28528cb35c4455f6e379`, pinned in the tool (`SENS2_PINS`, control H0) |

The G-DIAG readout is not read by this part, and `--g-diag-readout` given to it is an argparse error (exit 2).

## 2. Exact commands

**Definitions:**
- `P=/pscratch/sd/j/josephrb`.
- `B=$P/fd-g-sens2-20261026`. It does not exist yet (login09, 2026-10-26T20:10Z).
  <!-- absence-ok: `ls -d /pscratch/sd/j/josephrb/fd-g-sens2-20261026` on login09 at 2026-10-26T20:10:49Z printed 'No such file or directory' -->
- `D=$B/deploy/<pin8>`: a clean clone of the binding commit.
- `T=$D/docs/orchestration/state/measurement-paper/5d-community-20261024`.
- `PY` as for Stage G: `env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B`.

### 2.1 Deploy and tests (login node)

```bash
mkdir -p $B/logs $B/tmp
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $D && git -C $D checkout --quiet --detach <pin>
{ date -u +%FT%TZ; hostname; git -C $D rev-parse HEAD
  echo "porcelain_ignored_lines $(git -C $D status --porcelain --ignored | wc -l)"
  cd $D && sha256sum nd-unfolding/fd_g_followup.py nd-unfolding/tests/test_fd_g_followup.py nd-unfolding/fd_g_diag.py \
    nd-unfolding/tests/test_fd_g_diag.py nd-unfolding/fd_g_compare.py nd-unfolding/tests/test_fd_g_compare.py \
    nd-unfolding/s1_assemble.py nd-unfolding/s5p_stage1_inspect.py nd-unfolding/pv-ladder/readouts/h2_definition.json \
    docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_g_readout.json \
    docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_g_followup_readout.json \
    docs/orchestration/state/measurement-paper/5d-community-20261024/FD-G-SENS2-DECLARATION.md; } > $B/logs/deploy.log 2>&1
cd $D/nd-unfolding/tests && TMPDIR=$B/tmp env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -B -m unittest \
  test_fd_g_followup test_fd_g_diag test_fd_g_compare test_s1_assemble test_s1_scripts_isolated > $B/logs/deploy-tests.log 2>&1; echo "tests rc=$?" >> $B/logs/deploy.log
echo "porcelain_ignored_lines_after_tests $(git -C $D status --porcelain --ignored | wc -l)" >> $B/logs/deploy.log
```

**It must show:**
- HEAD equal to the pin;
- 0 porcelain lines before and after;
- the §8 digests;
- `tests rc=0` with "Ran 174 tests … OK" (84 G-FOLLOWUP and G-SENS2 + 41 G-DIAG + 27 Stage G + 22 S1,
  locally on 2026-10-26).

Anything else is a STOP.

### 2.2 The run (login node, after §2.1)

```bash
cd $B && TMPDIR=$B/tmp timeout 375 $PY $D/nd-unfolding/fd_g_followup.py --part sens2 \
  --definition $D/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --s1-npz $P/s1-20261024/s1_assembly.npz --s1-json $T/s1/readout/s1_assembly.json \
  --cmodel-json $D/nd-unfolding/pv-ladder/readouts/cmodel_5d.json \
  --s5p-sums $D/docs/orchestration/state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt --s5p-root $P/s5p-20260926 \
  --g-readout $T/fd/readout/fd_g_readout.json --g-followup-readout $T/fd/readout/fd_g_followup_readout.json \
  --extra-block $P/cresp-20261026/out/cresp.npz \
  --extra-block-sha256 4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a \
  --extra-block-key C_resp --extra-block-name C_resp --extra-block-role adopted \
  --out-json $B/fd_g_sens2_readout.json > $B/logs/sens2.out 2> $B/logs/sens2.err; echo "rc=$?" >> $B/logs/sens2.out
```

- **Projected wall:** 5 minutes, as for G-FOLLOWUP, which took about 1 s. The timeout is 375 s, 1.25 × that.
- **Exit codes:**
  - 0: every control passed and the readout was written;
  - 1: a control refused, an overwrite was refused, or an unexpected error occurred (nothing written);
  - 2: argparse, including `--part sens2` without `--g-followup-readout`;
  - 124: past the timeout.
  Any exit other than 0 is a STOP.
- **What is committed** (the report's PR):
  - `$B/fd_g_sens2_readout.json`, as `fd/readout/fd_g_sens2_readout.json`;
  - the logs and step scripts under `fd/receipts-g-sens2/`;
  - ledger rows.
- **The results index:** if the readout enters the index population, it is regenerated in-branch under the
  director's standing ruling (a).

## 3. Controls

All run before anything is written, and each refuses: exit 1, nothing written.

| control | checks | tests |
|---|---|---|
| **D0–D5** | G-DIAG's, unchanged, through `fd_g_diag.load` | G-DIAG's; `Sens2Invocation` (the real pins refuse at D0); `test_the_default_pins_are_sens2s` (the part's default pins are `SENS2_PINS`) |
| **H0** | **The referenced readout.** <ul><li>Its digest is the pin.</li><li>Its schema is `fd-g-followup-readout/1`.</li><li>It ran on this Stage G readout and extra block, on every shared input pin of G-DIAG's D0, and on the same five predictions with the same digests.</li><li>Its families, α and reported matrix are G-FOLLOWUP's.</li><li>It holds both `IDENTITY` records with a χ².</li></ul> **The identity:** the two `IDENTITY` χ² values, recomputed from the pinned inputs with G-FOLLOWUP's families, equal the readout's to 10⁻¹⁰ relative. A recomputed χ² that is none refuses | `test_h0_the_pin`; `test_h0_each_sub_check` (10 sub-checks, each alone, each asserting its own clause); `test_identity_recomputed_with_the_wrong_family` (the wrong group in H0's own two calls); `test_identity_against_a_tampered_readout` (× (1 + 10⁻⁸)); `test_identity_fields_below_the_tolerance` (× (1 + 10⁻¹³) passes, with the fields written as they are); `test_h0_refuses_a_recomputed_chi2_that_is_none` |
| **H1** | **The families.** Each new family shrinks exactly its own S1 group, and none is stat, seed, normalization or interaction | `test_flux_family_names_detector`; `test_lateral_family_shrinks_normalization_too` (its first half); `test_h1_refuses_a_family_named_for_a_forbidden_group` (normalization, stat, interaction) |
| **S0** | **α = 0 reproduces Stage G.** For every new family and prediction, the reported χ² is reproduced to 10⁻¹⁰ relative | `test_s0_runs_on_the_new_families` (C_resp dropped after H0) |
| **S1** | every shrunk M is positive definite | `test_s1_an_indefinite_shrunk_matrix` (on the flux family only) |
| **S2** | **The shrinkage is the declared one.** Every shrunk group's diagonal, and every shrunk M's, is bit-identical. Every shrunk off-diagonal is exactly (1 − α) times. Every block outside the family is bit-identical, normalization included | `test_detector_family_scales_the_diagonal`; `test_lateral_family_shrinks_normalization_too` (its second half: normalization shrunk inside `shrunk_blocks`); `test_s2_one_ulp_on_a_diagonal_an_off_diagonal_and_an_extra_block`; `test_normalization_and_every_other_block_bit_identical` |
| **H2** | **The addition.** Every top mode's, and every followed mode's, block shares sum to 1, to 10⁻¹⁰. **The modes are the records':** each top mode is the one its record carries, by index, σ and loadings to 10⁻¹⁰. At α = 0 that record is G-FOLLOWUP's α = 0 record for the prediction, which is the same matrix for every family. At α = 0.1 it is this run's flux record | `test_shares_not_divided_by_lambda`; `test_shares_of_the_mode_with_the_least_chi2`; `test_shares_from_the_unshrunk_blocks`; `test_h2_tolerance_followed_shares_and_a_flipped_loading` |

`sens_records` is G-FOLLOWUP's G-SENS loop with its S0–S2, moved into a function that both parts call (§6.1).

## 4. Statistics, as built

**Reused:**
- the shrinkage, `shrink` and `shrunk_blocks`;
- the record, `sens_record`;
- G-DIAG's blocks and residual (`comparison_blocks`, `residual`), eigen sign rule (`eigen`), per-mode χ² (`mode_chi2`),
  shares (`block_shares`) and stability (`chi2_ways`).

**The top mode** of the addition is the one with the largest χ² contribution, in that matrix's own eigen-order, as in
G-SENS. **A share** is vᵀBv/λ over that matrix's blocks, which partition M.

## 5. The readout, `fd-g-sens2-readout/1`

```text
schema, labels{what, sens, units, shares, referenced, not}, controls_passed[D0..D5, H0, H1, S0, S1, S2, H2],
constants{families{flux, detector, lateral}, role, alphas, lead, fractions, identity[2], shares[family, alphas],
          reproduction},
referenced{g_followup_readout (sha256), families{interaction, c_e_systematic}},
identity[2 x {family, alpha, prediction, chi2_g_followup_readout, chi2_recomputed, relative_difference}],
sens{reported_matrix, label, mode_index, unchanged{family: [11 blocks]}, records[3 families x 5 alphas x 5 predictions
  x G-FOLLOWUP's record, with family_role "single group" and shrunk_group_lambda_min{family}]},
flux_top_mode_shares{family, alphas, label, predictions{prediction: {
  "0" | "0.1": {mode, sigma, chi2, fraction, loadings, block_shares{12 blocks}, share_sum, dominant, flux_ratio},
  "alpha_0_mode_at_0.1": {variance_along, chi2_along, block_shares{12 blocks}, share_sum, dominant, flux_ratio},
  overlap_abs}}},
inputs_sha256, code_sha256{fd_g_followup.py, fd_g_diag.py, fd_g_compare.py, s1_assemble.py}, argv,
non_finite_written_as_null
```

No key `p` appears anywhere in the readout, and a test asserts this.

**What stdout prints:**
- the PASS lines;
- the label line, then G-FOLLOWUP's `[G-SENS]` line for each of the 75 records;
- one `[G-SENS2] flux alpha` line per prediction and α of the addition: the top mode, its σ, fraction and
  `flux_ratio`, and the four largest shares;
- one `[G-SENS2] flux alpha-0 mode at 0.1` line per prediction: the followed mode's χ² along it, its overlap and its
  `flux_ratio`;
- a `wrote` line.

## 6. Code and tests

### 6.1 Changes to `fd_g_followup.py`

**What changed:**
- **A refactor:** G-FOLLOWUP's G-SENS loop and its S0–S2 move, unchanged line for line, into `sens_records`. The
  per-prediction setup moves into `prediction_blocks`.
- **New:**
  - the option `--part {followup,sens2}`, default `followup`;
  - `--g-followup-readout`, and `run_sens2`, `top_mode_shares`, `followed_mode` and `flux_ratio`;
  - the constants `SENS2_FAMILIES`, `SENS2_ROLE`, `IDENTITY`, `SHARES` and `SENS2_PINS`.
- **The required inputs:** each part requires its own readout argument and refuses the other's, through `ap.error`
  (exit 2).
  - `--g-diag-readout` is required by the followup part only. It still exits 2 when missing, but its message changes:
    from main's "the following arguments are required: --g-diag-readout" to "--part followup requires
    --g-diag-readout", reported once the always-required arguments are present.
  - `--help` lists `--g-diag-readout` as optional, and lists `--part` and `--g-followup-readout`.
  - Main refused those two new arguments as unrecognized (exit 2); this tool accepts them.
- **`PINS` is unchanged,** so G-FOLLOWUP's readout carries the same `inputs_sha256`.

**The identity receipt.**
[`fd/receipts-g-sens2/declaration/followup_identity.py`](fd/receipts-g-sens2/declaration/followup_identity.py) and its
log run main's `fd_g_followup.py` (`820b67c2…`, the bytes G-FOLLOWUP ran) and this one, with the G-FOLLOWUP part. They
use the same six synthetic trees (seeds 0–2, roles adopted and sensitivity) and the same argv.
- **The readouts are byte-identical** once the one field that must differ is substituted. That field is
  `code_sha256["fd_g_followup.py"]`, since the readout embeds its own tool's digest. The digest occurs exactly once.
- **The stdout is identical** line for line, apart from the final `wrote` line, whose sha256 is of that readout.
- **The comparison's control:** the same comparison reports a difference when one label of this tool is changed.
- **Review B's check:** a planted `chi2_at_alpha_0` change made the receipt report DIFFERS on all six trees. The
  stdout stayed identical for that defect (two-decimal formatting), so the byte comparison is what catches it.
- **The log** was regenerated at this declaration's code (`followup_identity.log`), and shows "identical on all 6,
  control fires".

The real readout `cd82517a…` is not re-run here (§7 item 4).

### 6.2 Tests

`test_fd_g_followup.py` has 84 tests: G-FOLLOWUP's 58, unchanged in what they assert, and 26 new. The new ones run on
`Sens2Tree`, which is G-FOLLOWUP's synthetic tree with G-FOLLOWUP run on it, so its readout is the one G-SENS2 pins.

| class | what it shows |
|---|---|
| `Sens2` (4) | **The declared constants.** **End to end, as invoked:** <ul><li>D0–D5, H0, H1, S0, S1, S2 and H2 PASS, and no G-R04 control runs.</li><li>H0's two records equal G-FOLLOWUP's readout to 10⁻¹², and no interaction or joint record is computed.</li><li>75 records are each recomputed by hand from the tree with only the named group shrunk: χ², ndf, condition number, top-mode index and σ, mode counts, role, label, `shrunk_group_lambda_min`, and `chi2_at_alpha_0` equal to that family's α = 0 χ² exactly. α = 0 equals Stage G to 10⁻¹⁰, and α = 1 moves the χ² in each family.</li><li>The `unchanged` lists name normalization, and the readout's `referenced`, `constants`, `identity`, `labels` and `reported_matrix` fields are the declared ones.</li><li>The flux addition by hand: shares, mode, σ, χ², fraction, dominant block, `flux_ratio`, the followed mode's variance, shares, χ² along it and `flux_ratio`, and the overlap.</li><li>Stdout against the records, and no p.</li></ul> **The block sets:** every block set the tool sums keeps every non-shrunk block, normalization included, bit-identical across α, with the shrunk group's diagonal bit-identical. **No overwrite** |
| `Sens2PlantedDefects` (8) | **At least one per new item:** <ul><li>**the families:** flux names detector (H1); lateral shrinks normalization too, as a constant (H1) and inside `shrunk_blocks` (S2); the detector family scales the diagonal (S2);</li><li>**the identity:** the wrong group in H0's two recomputations (H0's χ² clause); a readout tampered by 10⁻⁸ (H0);</li><li>**the addition:** shares not divided by λ (H2's sum); the mode with the least χ² (H2's mode clause); shares from the unshrunk blocks (H2's mode clause).</li></ul> |
| `Sens2Controls` (4) | H0's pin, and each of its 10 sub-checks alone, asserting its own clause; S0 on the new families; S1 |
| `Sens2Coverage` (7) | **Review B's survivors:** <ul><li>the part's default pins are `SENS2_PINS`;</li><li>identity fields below the tolerance;</li><li>a recomputed χ² that is none (H0);</li><li>one ulp on a diagonal, an off-diagonal × (1 + 10⁻⁹), and an extra block (S2);</li><li>H2's tolerance, a followed-mode share defect, and a flipped loading;</li><li>H1 on normalization, stat and interaction;</li><li>the sensitivity role leaves C_resp out of `unchanged`.</li></ul> |
| `Sens2Invocation` (2) | **Argparse:** `--part sens2` without `--g-followup-readout`, followup without `--g-diag-readout`, and sens2 given `--g-diag-readout` each exit 2 with their messages. **The real script:** it reaches D0 and refuses synthetic records, with no traceback |
| `Sens2CommittedPins` (1) | The pin is the committed G-FOLLOWUP readout's. Its families are G-FOLLOWUP's. It holds both `IDENTITY` records. Its shared input pins are G-DIAG's D0 pins |

**Locally** (2026-10-26: Python 3.12.2, numpy 1.26.4, scipy 1.15.2), the five modules ran 174 tests, OK
([`fd/receipts-g-sens2/declaration/tests-local.log`](fd/receipts-g-sens2/declaration/tests-local.log)).

## 7. For the director

1. **"The top mode's per-group block shares at α = 0 and at α = 0.1"** is given two ways. A choice is needed only if
   one should be dropped.
   - **(a) Each matrix's own top mode,** with its shares over G-DIAG's blocks. This is the request read literally.
   - **(b) α = 0's top mode followed into the α = 0.1 blocks,** with its shares, the χ² along it alone, and
     `overlap_abs`. This is added after review A's finding:
     - in G-FOLLOWUP's committed readout, the joint family's top mode changes direction between α = 0 and α = 0.1 for
       GENIE+MEC (mode 13 at 1.15 % to mode 7 at 3.5 %), NuWro and MnvTune v1;
     - so (a) alone could compare two different directions;
     - the question "is the mode that carries the χ² the one flux's correlation protects" is about α = 0's direction.
   - **`flux_ratio`,** vᵀFv / vᵀdiag(F)v for the unshrunk flux block, is added to both. It is the part of flux's
     variance along the mode that flux's correlation leaves. It is descriptive, and it can be dropped.
   - **"Per-group"** is read as all 12 blocks, so the shares sum to 1. S1's seven groups are a subset of them.
2. **The two identity records** cover both families, a 16-cell and the 8-cell prediction, and an interior and an end
   α: interaction at α = 1 for NuWro, and the joint family at α = 0.25 for GiBUU.
3. **H0's tolerance** is 10⁻¹⁰ relative, as S0. The same arithmetic on the same inputs is expected to agree exactly,
   and the end-to-end test asserts 10⁻¹² on the synthetic tree.
4. **The byte-for-byte identity** is shown on six synthetic trees with one field substituted (§6.1), as for the G-DIAG
   refactor.
   - **A stronger option, recommended by review A,** is a bound step §2.3. It would re-run G-FOLLOWUP's exact argv
     with this code into a new file and compare it to the committed `cd82517a…` byte for byte, substituting the
     tool's own sha256 and the deploy prefix in `argv`.
   - **Its cost and its risks:** it takes about 1 s, but it is a second run on real inputs, so it needs the binding.
     It also needs a small comparison script. A different login node than G-FOLLOWUP's (login33) could differ in the
     last bits of an eigen-decomposition, which would be a STOP without a defect.
   - **It is not declared.** Say if wanted, and it comes as an amendment.
5. **Seed** stays as in G-FOLLOWUP: unchanged, and exactly zero in S1.
6. **No family repeats G-FOLLOWUP's.** Interaction alone is not re-run as a single-group record. The report sets the
   three new families beside G-FOLLOWUP's two, citing its readout.
7. **`shrunk_group_lambda_min`** at α = 0 for detector and lateral will print about −2 × 10⁻¹⁸. These are
   rank-deficient positive semidefinite groups (ranks 4 and 5), as in G-FOLLOWUP's readout (−1.3 × 10⁻¹⁸ for
   lateral). The report states this beside the numbers.
8. **The argparse changes** in the followup part (§6.1) change no exit code. They change one message and `--help`.

## 8. Pinned bytes

Their sha256 at this declaration's commit:

| file | sha256 |
|---|---|
| `nd-unfolding/fd_g_followup.py` | `ec8cbc6880f7a3f67eea5703ddeff958acb10462053696d2cfdb64de0ee5f60d` (§6.1; was `820b67c2…`) |
| `nd-unfolding/tests/test_fd_g_followup.py` | `f57c58b4bf94fbd712706cad5686f60fd8acd72c180fa45468bf899634c994c7` (was `6697e63d…`) |
| `nd-unfolding/fd_g_diag.py` | `241bfd0228907e5488f13b7fd50bd490edd97a77cf283a8fb88d3dc6d8bdcc03` (unchanged) |
| `nd-unfolding/tests/test_fd_g_diag.py` | `870564f5bf85c17b6e68212ab95663f6fd201969abc6d9f9d1b08261f368d525` (unchanged) |
| `nd-unfolding/fd_g_compare.py` | `0a3c09cdf2e27821c488c8a0d783af1537714144cce5415c6cb226ec8096df1f` (unchanged) |
| `nd-unfolding/tests/test_fd_g_compare.py` | `b4d0ff2611bcc6226e215e57023002025682aebea49ec1f2c06f3c61a9d7d9a8` (unchanged) |
| `nd-unfolding/s1_assemble.py` | `b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7` (unchanged) |
| `nd-unfolding/s5p_stage1_inspect.py` | `26569afc0da46f21167e0908014712cd800c1e14ac63a4b245a0b493c76d3d71` (unchanged) |
| `nd-unfolding/pv-ladder/readouts/h2_definition.json` | `b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89` (unchanged) |
| `…/fd/readout/fd_g_readout.json` | `75a9ddee19a7affe7e3bc10bf0cba8e5ebaa71132686e5ae116f1454d7bafcee` (input) |
| `…/fd/readout/fd_g_followup_readout.json` | `cd82517afdfb1dc8383580c8a4c57e82d9b87864e75d28528cb35c4455f6e379` (input) |

## 9. Ledger, storage and stops

- **Ledger:** rows in `fd/LEDGER.tsv` for §2.1 and §2.2. There is no Slurm job, so 0 node-h.
- **Storage:** `$B` holds the deploy clone (about 580 MB), the logs and the readout. Nothing goes to HPSS or CFS.
- **Stops:** any STOP is reported to the director unrepaired. Nothing is rerun without the director.

## 10. Not changed

- G-FOLLOWUP's, G-DIAG's and Stage G's readouts and reports, S1's covariance, C_model,5D, C_resp, R00–R15, κ = 1 and the
  route decision.
- No GPU and no premium QOS.
- The reading of any of this, claims, printed wording and publication are Joseph's. The report gives numbers only.

## 11. Review dispositions

Two independent read-only reviews ran on the first draft:
- **A** checked it against the request and the records;
- **B** attacked the code with mutations in a mirror: 81 mutants on the first draft, then 105 on the second.

| # | finding | disposition |
|---|---|---|
| A-M1 | A family constant that wrongly included normalization passed every control (S2 checks only outside what the family names), and its planted-defect test asserted nothing refused | New control **H1**: each family is exactly its own group, never stat, seed, normalization or interaction. The test now plants the defect both as a constant (H1) and inside `shrunk_blocks` (S2), and both refuse |
| A-M2 | H1 (now H2) checked only that shares sum to 1, which holds for any eigenpair, so the wrong mode or the wrong α passed | H2 now also requires each top mode to be the one its record carries: at α = 0, G-FOLLOWUP's α = 0 record; at α = 0.1, this run's flux record. The least-χ² mode and the unshrunk blocks are planted and refuse |
| A-M3 | Each matrix's own top mode may be a different direction at α = 0 and α = 0.1 (G-FOLLOWUP's joint family changes it for three predictions), so the reading may not answer the question | The followed α = 0 mode, the overlap and `flux_ratio` are added (§0; §7 item 1) |
| A-m1 | The wrong-family identity defect stopped on H0's metadata clause, not its χ² clause | Planted only in H0's two recomputations, and the test asserts the χ² clause |
| A-m2 | H0 did not check the shared input pins or the predictions | Both are checked; a test sub-checks each |
| A-m3 | A null χ² in the referenced record would raise a traceback | It refuses (H0) |
| A-m4 | The argparse changes | Each part refuses the other's readout argument; the message and `--help` change is recorded (§6.1) |
| A-m5 | Draft errors: 14/13 blocks (12/11), "six groups" double-counting, two overstated tests | Corrected |
| A-m6, B-4 | The identity log is gitignored, and recorded the first draft's sha | Regenerated at this code, and force-added |
| A-m7 | Two different tie-breaks chose the top mode | `top_mode_shares` now chooses as `sens_record` does |
| B-A3 | The part's default pins (`SENS2_PINS`) were untested; the real run would have passed D0 and then raised a KeyError had they been `PINS` | `test_the_default_pins_are_sens2s`; a mirror mutant to `PINS` fails it |
| B-gaps | Identity fields below tolerance; a None recomputed χ²; `chi2_at_alpha_0`; S2's one-ulp diagonal, off-diagonal tolerance and extra block; `check_shares` missing dominant, fraction, χ² and variance; H2's tolerance, the followed share sum and a flipped loading; H1's forbidden names; the readout's `referenced`, `constants`, `labels` and `reported_matrix` fields; C_resp in `unchanged` under the sensitivity role | Each has a test (`Sens2Coverage` and the end-to-end test). A mirror mutant to `dominant = min` fails the end-to-end test |
| B-3 | Two H0 sub-check messages were matched by the control's own name | Every sub-test asserts "differs in <clause>" |
| B-1 | `shrunk_group_lambda_min` prints about −2 × 10⁻¹⁸ for rank-deficient groups | §7 item 7 |
| B equivalents | Residual sign, the `--part` comparison, `fu0` from either family at α = 0, a redundant H0 or H2 clause, PD without `lambda_min > 0` | No change |
<!-- absence-ok: these rows restate the two reviews' findings on the uncommitted drafts of 2026-10-26 (each named gap passed every test there); they describe those drafts' coverage, now closed, not the absence of a result -->
