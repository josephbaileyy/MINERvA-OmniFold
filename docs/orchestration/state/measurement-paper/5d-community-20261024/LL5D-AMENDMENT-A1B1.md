# AMENDMENT A1b.1: the procedure controls' bitwise check against S1's committed products (2026-11-10)

**By** the `cov2d` session, at the director's ruling of 2026-11-10, for `coverage-5b-audit` to audit and the director to
bind as an addendum to LL5D binding 3. **DRAFT: nothing has run.**

**Under:**
- [`LL5D-DECLARATION.md`](LL5D-DECLARATION.md) §10: "The procedure controls (in the pilot). Each re-runs a block's path
  on the real data and must reproduce S1's product bitwise", for set-A replica b = 1, MaRES_0, Flux_0 and
  GEANT_Pion_0. §11 step 6 submits the bulk only after "every control passing".
- [`LL5D-BINDING-3.md`](LL5D-BINDING-3.md) (A1b at M_A1b), as its note moves A1b's test files under binding 2's
  addendum A1a.1, and binding 2's addendum A1a.2 (M_A1a.2 = `639ef907250a2a7909b7b9ba89b2e85e70c9b767`).
- **The gap this fills.** While drafting the pilot and bulk connects, the lane found no code at M_A1a.2 that performs
  §10's comparison. `ll5d_b.py`'s `control` role writes the four products and nothing reads
  them. `fd_1b_mc.py`'s docstring names the comparison ("bitwise against S1's or Stage 0's product"), but its code has
  none either. The 1B S1-0 connect (`fd/receipts-1b/staged/stage1/connect32-s1-0.sh`) names S1's committed products
  as the reference, but 1B stopped before its pilot ran. The director ruled on 2026-11-10: a small bound comparison
  that names the reference products by path and sha256, compares the four products bitwise (dtype, shape, bytes), and
  writes a record the bulk's connect pins, with a mutant in which one flipped ulp reads FAIL.

**MEASURES:** nothing. No job has run for A1b.1. Every number below is a test result on synthetic fixtures, or a
digest of a committed file.

**CANNOT AUTHORIZE:**
- any job, including the pilot, before this amendment is bound and the director gives the go on that step's connect;
- any change to `ll5d_b.py`, `ll5d.py` or any bound function. Neither changes here;
- any repair after a FAIL. A FAIL is §10's INVALID, reported unrepaired, and the bulk is not submitted.

**CITABLE FOR:**
- the comparison's code, tests and mutants at the digests in §1;
- the four references, by path and sha256.

**NOT CITABLE FOR:**
- whether the controls reproduce S1 on the cluster (only the pilot measures that);
- any coverage statement.

## 1. What changes

| file | change |
|---|---|
| `nd-unfolding/ll5d_ctl.py` | **new.** `controls(unfolds, repo)` reads the four control products and their references through O_NOATIME, checks each reference's sha256 against its pin, and compares `xsec_flat` bitwise (`compare`: dtype, shape, `tobytes`). It writes `controls.json` with verdict `PASS` (rc 0) or `FAIL` (rc 6). A refusal is INVALID (rc 5). Exit 8 is OR-ed in on an atime move. |
| `nd-unfolding/tests/test_ll5d_ctl.py` | **new.** 16 tests (§3). |
| `nd-unfolding/tests/ll5d_a1b1_mutation.py` | **new.** 12 mutants (§3). |
| `nd-unfolding/ll5d_b.py`, `nd-unfolding/ll5d.py` | **unchanged**: `24312ca86f9e70ed86699772d634c19d9bcacb2bb87bff5aaa8c9f7c2661f3cb` and `2b0224c6fe52c5bb2d3fe64d461ac9edb80ebd191b0ab2f892dec605a0b56a14`. |

Digests (sha256) at the code commit (to fill from git), the commit the receipts were made at:

| file | sha256 |
|---|---|
| `nd-unfolding/ll5d_ctl.py` | `a9f09557ec1b6022b1205f14e8d2241257336d9028b166061a3b33118243a936` |
| `nd-unfolding/tests/test_ll5d_ctl.py` | `fb91b93edef2f37c96ab88200d6c22caa75dd05f943769424b87c55fd50a1f1d` |
| `nd-unfolding/tests/ll5d_a1b1_mutation.py` | `aa7c3abed4f9b529e3976097531dd4ddcce524b943c4c61083241579dfec397f` |

## 2. The references

These are S1's committed products, under
`docs/orchestration/state/measurement-paper/5d-community-20261024/s1/readout/s1_assembly/`. Each digest is the one
S1's `SHA256SUMS` records, and the one the committed file hashes to. A test checks both (`Pins`).

| control (`ll5d_b.CONTROLS`) | reference | sha256 | what it is (its own meta) |
|---|---|---|---|
| `setA_b1` | `data_b1_j101.npz` | `95a9f09c44b1fa997242c3fa4740400084fa98ce78ca6e99f38f6970e65fbabf` | the data, set A's replica: bootstrap seed 1, jitter seed 101 |
| `MaRES_0` | `S1_MaRES_0.npz` | `aa3ed226ed866a92a9b41fcd5e9f94b32c8928364f9986f1bddde3a317644667` | S1's universe MaRES:0 |
| `Flux_0` | `S1_Flux_0.npz` | `17e872735e5c9df7926b27215155b2b701dde20959498cb0345d230b99636d27` | S1's universe Flux:0 |
| `GEANT_Pion_0` | `S1_GEANT_Pion_0.npz` | `2972f5a33a8464da9d9f7e8b98d2c3a428f5a1c35db02eda7e5f73309a7b817a` | S1's universe GEANT_Pion:0 |

Each holds `xsec_flat` as `<f8` of shape (65856,). The pilot's control product holds `xsec_flat` as
`np.asarray(xs, float).ravel(order="C")` (`ll5d_b.run_item`). The comparison reads `xsec_flat` only; the products'
`meta` differs by construction (job, timing, digests).

**The thread count.** The four references' metas record `threads` 32 and `estimator_seed` 42. The pilot and bulk
connects run each lane as an srun step of 32 CPUs and 56G at `--threads 32`, as 1B staged ran its lanes
(`fd/receipts-1b/staged/stage1/tables/make_stage1_tables.py`, `"--threads", "32"`). §9's one-thread rule binds the gate
and the calibration only (936-C2). Whether the bits reproduce at that configuration on the cluster is what the pilot
measures.

## 3. The rule and its tests

**The rule.** A control passes only if its product's `xsec_flat` has the reference's dtype, the reference's shape, and
the same bytes. The verdict is `PASS` only if all four pass. The record also carries, for description only, the count
of differing elements and the largest absolute difference.

| rule | test(s) | mutant(s) |
|---|---|---|
| equal bytes pass, all four | `Bitwise.test_equal_bytes_pass` | (the control) |
| **one flipped ulp fails** (the director's REQUIRED case) | `Bitwise.test_one_flipped_ulp_fails` | a tolerance (`np.allclose`) in place of the bytes; one control enough (`any`); the product compared with itself |
| a dtype change fails, with every value equal | `Bitwise.test_a_dtype_change_fails_even_with_equal_values` | the dtype unchecked |
| a shape change fails, with the same bytes | `Bitwise.test_a_shape_change_fails_with_the_same_bytes` | the shape unchecked |
| only `xsec_flat` is compared | `Bitwise.test_the_comparison_is_of_xsec_flat_only` | |
| a reference whose digest differs is INVALID | `Refusals.test_a_reference_digest_mismatch_is_invalid` | the digest unchecked |
| a missing product or reference is INVALID | `Refusals.test_a_missing_product_is_invalid`, `…_reference_is_invalid` | |
| the references are exactly `ll5d_b.CONTROLS`, in order | `Refusals.test_the_references_must_be_exactly_the_declared_controls` | the list unchecked |
| PASS rc 0, FAIL rc 6, INVALID rc 5 with its `.invalid.json`; an atime move ORs 8; no overwrite | `ExitCodes.*` | FAIL exits 0; the atime move dropped |
| every read through O_NOATIME (eight files) | `NoAtime.test_every_read_goes_through_o_noatime` | a plain read |
| the pins are the committed files and S1's `SHA256SUMS`; set A's reference is replica 1 at jitter 101; each universe reference is that universe | `Pins.*` | MaRES_0 against MaRES_1; set A at replica 2 |

**Results** (`fd/receipts-ll5d/a1b1/`, from a clean checkout of the code commit):
- `test_ll5d_ctl.py`: 16 tests, OK, at PYTHONHASHSEED 0, 1 and 2 under numpy 1.26.4, and under numpy 2.
- `ll5d_a1b1_mutation.py`: 12 mutations, all killed. The unmutated control runs all 16 tests, none skipped, rc 0.
- `test_ll5d.py` and `test_ll5d_b.py` pass unchanged with `ll5d_ctl.py` tracked.

## 4. Where it runs, and how the bulk pins it

- **In the pilot job**, after the 13 unfolds and `walls`, before `clipcheck`:
  `python3 -B $DD/nd-unfolding/ll5d_ctl.py --unfolds $U --repo $DD --out $W/controls.json`. It reads four products of
  about 0.5 MB each and four committed references, so it adds seconds to the pilot's 01:00:00, and no node-h.
- **The pilot connect** binds `ll5d_ctl.py` among its blobs and deploys at the merge that carries this amendment. The
  pilot's receipt commits `controls.json`.
- **The bulk connect** pins `controls.json` by the sha256 in the pilot's merged receipt (`CTLSHA`, with
  `CTLREC=$PW/controls.json`), and requires its `verdict` to read `PASS`, beside walls PASS and clipcheck PROCEED.

## 5. For the auditor

- `ll5d_ctl.py` reads nothing from A1a's jobs, and nothing sealed. It reads the four control products (this lane's)
  and four committed files.
- The comparison is `a.tobytes() == b.tobytes()` with equal dtype and shape. There is no tolerance anywhere in the rule.
- `REFERENCES` must equal `ll5d_b.CONTROLS` in order, so a control added to or dropped from A1b refuses here.

Nothing is submitted, deposited or tagged.
