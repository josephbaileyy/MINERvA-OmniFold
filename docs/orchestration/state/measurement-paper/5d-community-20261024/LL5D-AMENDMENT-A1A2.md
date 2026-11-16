# AMENDMENT A1a.2: vi keyed at one precision on both sides, the test that would have caught it, and a real-data preflight (2026-11-10)

**By** the `cov2d` session, at the director's request, for `coverage-5b-audit` to audit and the director to bind as an
addendum to LL5D binding 2. **DRAFT: nothing has run.** Joseph has decided the relaunch
(`DECISION-20261110-joseph-ll5d-rerun-16-cells.md`, #1018): once this amendment is audited and bound, the gates rerun
on R00–R15, the sixteen reporting cells. Each step still takes the director's go on its connect's sha256.

**Under:**
- **The STOP of both LL5D gates** (ll5d_gate_G18 61040163, ll5d_gate_AR23 61040235; receipts `fd/receipts-ll5d/gate-g18/`
  and `gate-ar23/`). Each read option (3) in every evaluation because vi read every row unmatched. Every other
  reading passed: the variance gates, gate_n, the backstop, and D1, D2 and D3.
- **The read-only diagnosis** (`fd/receipts-ll5d/gate-vi-diagnosis/`, PR #1015) classifies it as an implementation
  defect. `fd_1b_c2.row_match` keys rows on the bit patterns of five coordinates plus the weight. The npz's `w_truth`
  is float64 and the bank's tdw is float32, so no key can match.
- **LL5D BINDING 2** (A1a, now at A1a.1 `a95cc39f7437170af0b65ba042934fad079e0ee2`) and **BINDING 3** (A1b). Each file
  this amendment changes is named in §1.

**The cells.** R00–R15 are the sixteen cells the gates already read (`N_CELLS = 16` at `s1_assemble.py:51`, through
the H2 definition's map). This amendment changes no cell, and a merged-cell run is outside it (#1018 item 2).

**MEASURES:** nothing. **CANNOT AUTHORIZE:**
- any step (the preflight, the calibration or the gates) before this amendment is bound and the director gives the go
  on that step's connect;
- the preflight (§5) under #1018 alone. #1018 authorizes the rerun "and nothing beyond it", so whether `vicheck`
  counts as part of that rerun or needs its own decision is the director's call;
- any change to the gate's rule, thresholds or mismatch bound;
- opening the sealed clip-prep files.

**CITABLE FOR:**
- the fix;
- its tests and mutants;
- the preflight's design and the rerun's price, at the digests in §1.

**NOT CITABLE FOR:**
- whether vi is bounded on the real inputs (only the preflight or a rerun measures that);
- any coverage statement.

## 1. What changes

| file | change |
|---|---|
| `nd-unfolding/ll5d.py` | **`vi_inputs(P, cv)`** (`:454`) hands `c2.c2_vi` the keys it reads, each of the six row-key columns rounded to `VI_KEY_DTYPE = np.float32` (`:450`); the weights are handed on as float64 holding float32 values. The gate calls it (`:996`): `c2.c2_vi(*vi_inputs(P, cv), fm, geo)`. **`vicheck`**, a new subcommand (`vicheck_main`, `:1071`; `vi_terms`, `:1050`; `SCHEMA_VICHECK`, `:73`), is the preflight of §5. Nothing else in the gate or the calibration changes. |
| `nd-unfolding/fd_1b_c2.py` | **unchanged.** It stays the verbatim copy from 342c0ce5 (blob `0cb72761…`, sha256 `522d7edd…`). |
| `nd-unfolding/tests/test_ll5d.py` | `MatchedRows` (§3); RealChain's denominator rows behind a hook (`denominator_rows`), whose default is RealChain's draws unchanged; the preflight test, run on both worlds; A21Equality's vi made explicit (§4); `gate(out=)` |
| `nd-unfolding/tests/test_ll5d_b.py` | RealUnfold nulls the newly inherited preflight test, as it already nulls RealChain's other tests |
| `nd-unfolding/tests/ll5d_a1a_mutation.py` | eight A1a.2 mutants (§3); `EXPECTED_TESTS` 72 → 82 |

Digests (sha256) at the code commit `9d906bf40994e9814ee63a2386e7fd7e14da5b4e`, the commit the receipts were made at:

| file | sha256 |
|---|---|
| `nd-unfolding/ll5d.py` | `2b0224c6fe52c5bb2d3fe64d461ac9edb80ebd191b0ab2f892dec605a0b56a14` |
| `nd-unfolding/tests/test_ll5d.py` | `6fa5510efd8fde01b1879cd8a1ec984f5e28699445a022450d2166af7c6c493c` |
| `nd-unfolding/tests/test_ll5d_b.py` | `5391a42f82d5690c488a7b7d1309f5298ad2b55730d559d26da003779266f5d7` |
| `nd-unfolding/tests/ll5d_a1a_mutation.py` | `584216348761248026734ada1ad3d25eab355cdbfab20db66416cf9a518346c1` |
| `nd-unfolding/ll5d_b.py` (unchanged) | `24312ca86f9e70ed86699772d634c19d9bcacb2bb87bff5aaa8c9f7c2661f3cb` |
| `nd-unfolding/fd_1b_c2.py` (unchanged) | `522d7edd71643df61d0c5ef5a7488834e664eb36d20c3e0c0b46e10a5808f02f` |

## 2. The choice: key at float32, the denominator's stored precision

The fix rounds both sides' key columns to float32 before `row_match` hashes them. It does this in what `ll5d.py`
passes, not in the vendored file.

**The grounds:**
- **It compares like with like at the only precision both sides hold.** The bank stores td_* and every tdw as float32
  (`sweep_bank_5d.py:114,165,185`). That information is gone, so float32 is the finest precision the two sides share.
- **It reproduces the bank writer's own rounding.** The bank's tdw is `float32(w × pot_scale)`, the product formed in
  float64 (`sweep_bank_5d.py:183`). The npz's `w_truth` is that same float64 product (`unfold_nd_omnifold_unbinned.py:438`).
  Rounding it to float32 gives the bank's value bitwise, provided the two products come from the same double weight.
  **INFERENCE:** that GEANT_Neutron_0's truth weight is bitwise the CV truth weight on every row. The declaration's
  §3.4 calls tdw_ref the CV-equal per-row weight, and all six GEANT tdw and EtaNCEL's share one digest. The
  preflight (§5) measures this on the real files.
- **Rounding is idempotent on the float32 side.** The coordinates are already float32 on both sides
  (`nn_dump_inputs.py:84`; `sweep_bank_5d.py:114`), so their rounding is a no-op. It is kept so that the key does not
  depend on that.
- **It keeps the vendored file verbatim** (the director's preference). `row_match`'s exact-hash design is unchanged; only
  its inputs are put at one precision.
- **It loses no meaningful sensitivity.** Rows whose weights differ below float32 resolution (relative 6e-8) now share a
  key. Against a 5 % bound per cell, that is no loss.

**Rejected:**
- **A weight tolerance.** `row_match` hashes exact bits, so a tolerance means rewriting it in the vendored file. The
  amendment would then have to argue a new matching rule.
- **Coordinates only.** Dropping the weight from the key stops vi seeing rows whose weights disagree, which is part of
  what it exists to catch.
- **Re-dumping either input at the other's precision.** That changes bound inputs and needs cluster work for no gain
  over the above.

## 3. The missing test and its mutants

**`MatchedRows`** (`test_ll5d.py:1446`) is RealChain's real-file world with the bank's truth-denominator rows **being** the
npz's truth-passing signal rows in the phase space. They are stored as the writers store them:
- `MCgen`, the bank's copy of it, and td_* in float32;
- `w_truth` in float64;
- every bank tdw in float32, with tdw_ref = float32(w_truth).

`test_the_world_is_stored_as_the_writers_store_it` pins those dtypes, and pins that no `w_truth` value is float32-exact.

- **REQUIRED: `test_vi_finds_every_matched_row_and_the_read_is_not_forced`** (`:1474`).
  - It requires:
    - vi to find every row on both sides (`(0, 0)` unmatched, share 0.0);
    - `mismatch_bounded` to be true;
    - `option_3_applies` to be false;
    - this world's gate to read option (1) in both evaluations and PASS.
  - **At a95cc39f it fails:** `AssertionError: Tuples differ: (2980, 2980) != (0, 0)`. That was run with a95cc39f's
    `ll5d.py` (sha256 `b49f5d5f…`) first on `sys.path`, as the mutation harness places a copy (receipt in
    `fd/receipts-ll5d/a1a2/`).
- **The control: `test_the_unrounded_key_cannot_match_here`** (`:1499`). With `vi_inputs` replaced by the identity
  (a95cc39f's call), the same world reads share 1.0 and option (3) everywhere. So the world discriminates.
- **`test_vi_inputs_rounds_the_key_and_nothing_else`** (`:1507`) checks four things:
  - only the keys `c2_vi` reads are handed on;
  - each key column has float32 values, and the weights are float64;
  - `pass_truth` and `cells` are passed by identity;
  - the caller's P and cv are untouched.
- **The preflight, on both worlds:**
  - `test_the_vi_preflight_over_the_real_chain` (`:1427`): STOP on RealChain, whose rows are drawn apart, and PASS on
    MatchedRows. The phase-space terms must add up, and no atime may move.
  - `test_the_vi_preflight_reads_both_keys` (`:1490`): on MatchedRows, share 0.0 with the gate's key and 1.0 with the
    unrounded key; the npz dtypes; and the share of each weight that float32 holds exactly (`w_truth` 0.0, `tdw_ref`
    1.0).

**The mutants** (`ll5d_a1a_mutation.py`) are all killed. Their named tests:

| mutant | killed by |
|---|---|
| vi keyed on the inputs as given (the gate's call reverted) | `test_vi_finds_every_matched_row_…` |
| `VI_KEY_DTYPE = np.float64` (the key at the signal weight's precision) | `test_vi_finds_every_matched_row_…` |
| the signal weight left unrounded | `test_vi_finds_every_matched_row_…` |
| the denominator weight left unrounded | `test_vi_inputs_rounds_…` |
| the bank coordinates left unrounded | `test_vi_inputs_rounds_…` |
| the signal coordinates left unrounded | `test_vi_inputs_rounds_…` |
| the preflight reads the unrounded key | `MatchedRows.test_the_vi_preflight_over_the_real_chain` |
| the preflight passes an unbounded vi (bound widened to 2.0) | `RealChain.test_the_vi_preflight_over_the_real_chain` |

Three of these mutants are equivalent on data stored as the real writers store it: the denominator weight, the bank
coordinates and the signal coordinates are already float32 there. They are killed by the unit test, which feeds
float64 values on purpose, so that the key never depends on a writer's dtype.

## 4. A21Equality

`A21Equality.test_the_all_path_equals_a21s_bitwise` compares ll5d's builders, and the vi they produce, with A2.1's
path at 342c0ce5. On its fixture the td rows are drawn apart from the signal rows, so vi is all-unmatched on any key.
The reference pinned exactly that: share 1.0, 2980/2980 and 50/50 (the diagnosis, `run_a21_vi.out.txt`).

**The change:** the test keeps its equality, because that is a statement about the builders, which still hold. It
now also asserts the fixture's all-unmatched vi explicitly (`:1599`), with a comment that it is a property of the
fixture and not vi coverage. vi coverage is MatchedRows'. The reference generator is unchanged. Its call is A2.1's raw
`c2_vi`, which is the right comparison for the builders.

## 5. The 2,801 rows, and a preflight on the real inputs

**Can the 2,801 matter after the fix?** Possibly, and the committed records cannot settle it.
- After the fix, vi's unmatched rows are signal rows without a partner and truth rows without one.
- The truth side has 32,849,103 rows and the signal side 32,846,302 in the phase space, so at least 2,801 truth rows
  lack a partner.
- Truth rows outside the 5D cells, or in a fine cell the H2 map leaves out, carry cell -1 and enter no share
  (`fd_1b_c2.py:1098`, and the per-cell `share` in `row_match`, `:562-564`). So the 2,801 count against the bound only
  if they lie in mapped cells, have no signal partner there, and gather in one cell enough to exceed 0.05 of its weight.
- The 16 cells' weight totals are not in any committed record this lane could read.

<!-- absence-ok: a scoping statement about which committed records were available to this lane; not a claim that a result does not exist -->
**The preflight: `ll5d.py vicheck`.** It reads the world through `load_world`, with the same digests, pins and
O_NOATIME. It reads the H2 definition's map and nothing else: no universe weights, no truth and no draws. It records:
- vi exactly as the gate now computes it, beside the unrounded call the gates made;
- the 2,801 rows term by term (`vi_terms`): the npz's signal rows, those passing truth, and those in the 5D cells; the
  truth-passing rows outside the cells by the axis they leave (pT, pz, eavail, q3, W, or two or more); the rows inside
  the cells that do not pass truth; and the truth rows and those outside the cells;
- the npz dtypes, and the share of `w_truth` and of tdw_ref that float32 holds exactly.

Its verdict is PASS when vi's largest cell share is within `clip_probe2.MISMATCH_BOUND`, as `reading_1b` reads it. A
STOP is a genuine mismatch, and it goes to Joseph.
- **Price:** one exclusive regular CPU node with `--time 01:00:00`, so 1.0 node-h reserved. The gates' one-off setup,
  which includes `load_world` and every universe's read, took 1,174 s and 1,231 s. vicheck does less, so the measured
  cost should be about 0.3 node-h. That is INFERENCE, to be read from the job.
- **What it buys:** it decides, at about 1 % of a gate pair's cost, whether the fix holds on the real files, before
  about 23 node-h is spent.

## 6. What reruns, and its price

Under #1018 the rerun is the two gates on R00–R15, preceded by the calibration that A1a.2's code change requires. The
preflight is optional and listed first.

| step | why | measured, run 2 / gates | reserved |
|---|---|---|---|
| vicheck (§5) | the fix on the real inputs and the 2,801 terms | about 0.3 node-h (INFERENCE) | 1.0 |
| ll5d_calib | `read_calibration` refuses a calibration computed by other code (`ll5d.py:920`: `cal["code_sha256"] != code_digests()`). The calibration does not use vi, so its numbers should reproduce bitwise under the same seeds, N and one thread. That is INFERENCE, checkable against run 2's `calibration.json`. | 01:10:37, 1.18 node-h | 5.0 |
| ll5d_gate_G18, ll5d_gate_AR23 | the STOPped gates, after the fix | 10:52:09 and 11:00:23, 21.88 node-h | 31.0 + 31.0 |

- **Total measured:** about 23.4 node-h. With the 23.06 already charged to LL5D, that is about 46.4 of the 148.0 cap.
- **Peak projection:** with the gates back to back, the second gate's projection is about 24.5 charged + 31.0 held +
  31.0, about 86.5. That is within the cap.
- **Also reruns:** the connects. Each moves its M and its bound `ll5d.py` digest to this amendment's merge. The gate
  connect also takes the new calibration's digests from its merged receipt. Each sha256 goes to the director for its
  own go. A1b's code is unchanged; its products bind A1a's digest through `ll5d_b.code_digests()`.
- **Does not rerun:** anything already PASSED that does not depend on `ll5d.py`'s digest.

## 7. Results

**Receipts:** `fd/receipts-ll5d/a1a2/`, made at `9d906bf40994e9814ee63a2386e7fd7e14da5b4e` from a clean checkout.
- **The suites:** test_ll5d.py, 82 tests, OK, and test_ll5d_b.py, 29 tests, OK, each at numpy 1.26 (seeds 0, 1 and 2)
  and at numpy 2.
- **The mutation checks:**
  - `ll5d_a1a_mutation.py`: the control passes (82 tests), and 58 mutants are all killed, 8 of them A1a.2's;
  - `ll5d_a1b_mutation.py`: the control passes (29 tests), and 27 mutants are all killed.
- **At a95cc39f** the REQUIRED test fails, `(2980, 2980) != (0, 0)`, as it should on the code that ran the gates.
- **A disclosure** (the receipt README): a first set of numpy 1.26 suite runs did not import its module, so no test
  ran. Those outputs were discarded and the suites remade.
