# BINDING 2: LL5D amendment A1a, the calibration and the clipping gate (director, 2026-11-08)

**Binds** [`LL5D-AMENDMENT-A1A.md`](LL5D-AMENDMENT-A1A.md) and its code, as merged in PR #945 at
**M_A1a = `e92e946759772d13e21055b21c69189c8b007183`**. The audited head is `0231d1d2`, and the amendment and every code
and test file are identical at the two commits.

| file | sha256 (prefix) |
|---|---|
| `LL5D-AMENDMENT-A1A.md` | `2615cc3d956c0b14` |
| `nd-unfolding/ll5d.py` | `9dbf9cf499f2c709` |
| `nd-unfolding/fd_1b_c2.py` (verbatim from `342c0ce5`, blob `0cb72761`) | `522d7edd71643df6` |
| `nd-unfolding/tests/test_ll5d.py` | `f7ee9aed4bf666f2` |
| `nd-unfolding/tests/ll5d_a1a_mutation.py` | `d43ed9f3bf063345` |
| `nd-unfolding/tests/ll5d_a21_reference.py` | `8fbecaae657fa400` |
| `nd-unfolding/tests/data/fd_1b_mc_at_342c0ce5.py.txt` | `062628b69976f730` |

**Under:** [`LL5D-BINDING-1.md`](LL5D-BINDING-1.md) (the design at `1acdee66`), ruling 4: A1a → binding 2, A1b → binding 3.

## What the director checked

coverage-5b-audit's GO at `0231d1d2` (https://github.com/josephbaileyy/MINERvA-OmniFold/pull/945#issuecomment-6726406977),
after a NO-GO at `73684077` on one receipt defect (the seed-range test failed on the PR's own tracked files, so the
unmutated mutation control failed):
- 69 tests and 47 of 47 mutants reproduce at the head, at one thread, with the unmutated control passing;
- the seed check's exclusion is by exact path over 9 files, and its positive control is correct;
- the all-path equality test runs `342c0ce5`'s own path, with only loaders patched;
- the cross terms (the director's option B) equal `fd_1b_mc.crossterm` to 1e-12, hold only row-sized arrays and move no
  verdict;
- the exact float64 receipt follows §2d (ii) / exact_n1, with the near-zero recompute for exact clip signs;
- the sealed clip-prep products: the record carries only their path, bytes, sha256 and key names; their equality test
  uses an independent path; removing them leaves the verdict, reads, backstop and reading detail identical.

The director ran `test_ll5d.py` from a `git archive` of M_A1a (one thread, `PYTHONHASHSEED=0`, own TMPDIR): 68 passed
and 1 skipped. The skipped test is the tracked-file seed check (`test_ll5d.py:933`, "not a git checkout"), which needs a
git checkout; the auditor ran it in one and it passed.

## Rulings

1. **A1a is bound at M_A1a** for §11's steps 3–4: the calibration job and the two gate jobs, with the receipt (D1–D3,
   N1, T ≤ 0) at the start of each gate job, the gate, the cross terms and the sealed clip-prep products.
2. **The five named departures** (layout_minus2, drop2, restrict, ll5d's own input builders with tdw_ref, the
   four-evaluation joint rule) and §5c–j's implementation choices are bound as written.
3. **The seal (§5j).** Nobody, the lane, the auditor or the director, opens or summarizes `<out>.clipprep.npz` before
   binding 3. No readout prints it. A1b reads it only by the sha256 the gate record carries, and refuses a mismatch. It
   gates nothing.
4. **POWER_SHORT** comes to the director. A rerun at a larger N ≤ 9,000 is inside the declared design and is the
   director's operational go; the director tells Joseph.
5. **STOPs** are under #939: each goes to the director and Joseph unrepaired, and nothing relaunches until Joseph
   decides. An INVALID may be rerun unchanged under the director's authority.
6. **The price** is as A1a §5a states it, inside LL5D's 148.0 CPU node-h cap. `iris` is read before each connect.
7. **Sequencing with other campaigns.** The first ll5d_ go waits until:
   - ENS1's stage 2 and its post-run have ended (ENS1's fence refuses unknown families);
   - a realpath overlap check of LL5D's inputs against the band diagnosis and FD-PRR, the two campaigns sequenced after
     ENS1, is recorded. Shared inputs are sequenced, not fenced open.
   The director names `ll5d_*` to every fenced lane before that go.
8. **Each connect** sends its sha256 and path to the director before launch, from a fresh clone at M_A1a with empty
   porcelain. ssh's rc is read unpiped, every `--time` is HH:MM:SS with scontrol's TimeLimit checked, and each receipt
   goes in as a PR.

Nothing is submitted, deposited or tagged.

## Binding 2, addendum A1a.1: the candidate's install at the entry points (director, 2026-11-09)

**Binds** [`LL5D-AMENDMENT-A1A1.md`](LL5D-AMENDMENT-A1A1.md) and its code, as merged in PR #967 at
**M_A1a.1 = `a95cc39f7437170af0b65ba042934fad079e0ee2`**. The audited head is `7e6172e9`; the amendment and every file
below are identical at the two commits. This **supersedes M_A1a above** for the calibration and gate jobs.

| file | sha256 (prefix) |
|---|---|
| `LL5D-AMENDMENT-A1A1.md` | `59850812f83bd816` |
| `nd-unfolding/ll5d.py` | `b49f5d5f793265ef` |
| `nd-unfolding/tests/test_ll5d.py` | `9ef0f23838e5dd0e` |
| `nd-unfolding/tests/ll5d_a1a_mutation.py` | `b5849b1d9a9a795b` |
| `nd-unfolding/tests/test_ll5d_b.py` | `918d75bfd9c2c89f` |
| `nd-unfolding/tests/ll5d_a1b_mutation.py` | `1b09bf22969b2698` |
| `nd-unfolding/ll5d_b.py` (unchanged since binding 3) | `24312ca86f9e70ed` |
| `nd-unfolding/fd_1b_c2.py` (unchanged) | `522d7edd71643df6` |

**What led to it.** ll5d_calib run 1 (job 61014290, receipt #963) was INVALID: `calibration.json` was never written.
The cause is that A1a's entry points never installed configuration (e)'s candidate, so the "ratio_nd" truth model was
unregistered, and A1a's tests mocked `fd_1b_mc.truth_weight`, so no test ran the real path. Nothing was computed that
could inform a choice, so this is an implementation defect, not a STOP under #939 (ruling 5).
<!-- absence-ok: run 1's receipt #963 records that calibration.json was never written; this restates that record, not a search result -->

**What the director checked:**
- coverage-5b-audit's GO at `7e6172e9` (https://github.com/josephbaileyy/MINERvA-OmniFold/pull/967#issuecomment-6742995391):
  - test_ll5d 72 at hash seeds 0 and 17, test_ll5d_b 29, A1a's 50 of 50 and A1b's 27 of 27 mutants killed, every
    install mutant killed by its named test;
  - `RealChain` mocks nothing in `fd_1b_mc`, `s5n_pseudo` or `s5c_pseudo`, and `pristine_s5n` restores exactly the
    four attributes the install rebinds;
  - the §3 mock inventory is complete;
  - the install precedes every path to `truths_r`, and the calibration's fork pool inherits it;
  - the receipt-tree exclusion hides none of today's seed-range hits.
- The director ran both suites from a `git archive` of M_A1a.1 (one thread, `PYTHONHASHSEED=0`, own TMPDIR):
  test_ll5d 71 passed and 1 skipped (the tracked-file seed check, which needs a git checkout, as before); test_ll5d_b
  29 passed.

**Rulings:**
1. **The calibration and both gate jobs run from M_A1a.1.** Rulings 1–8 above stand otherwise, and the design is
   unchanged: the rerun uses the same declared seeds and N = 3,000.
2. **The rerun is an INVALID rerun under ruling 5,** inside the director's authority. Run 1's charge counts against
   LL5D's 148.0 CPU node-h cap.
3. **Each connect** pins M_A1a.1 and `ll5d.py`'s digest above, ends its job step with `exit $rc` so sacct's state is
   the step's (the amendment §1, and the audit's low), and sends its sha256 and path to the director before launch.
4. **The LL5D receipt-tree exclusion** from the seed collision check (`OWN_RECEIPT_PREFIX`) is bound as written,
   with its positive control.
5. The audit's other lows (the vendored-copy note; the deprecated `load_module`; install wrappers stacking) are held
   for the follow-up list.

Nothing is submitted, deposited or tagged.

## Binding 2, addendum A1a.2: vi keys both sides at float32 (director, 2026-11-10)

**Binds** [`LL5D-AMENDMENT-A1A2.md`](LL5D-AMENDMENT-A1A2.md) and its code, as merged in PR #1019 at
**M_A1a.2 = `639ef907250a2a7909b7b9ba89b2e85e70c9b767`**. The audited head is `12d37105` (code `9d906bf4`); the
amendment and every file below are identical at the two commits. This **supersedes M_A1a.1** for the vicheck,
calibration and gate jobs.

| file | sha256 (prefix) |
|---|---|
| `LL5D-AMENDMENT-A1A2.md` | `ac909e63535493b6` |
| `nd-unfolding/ll5d.py` | `2b0224c6fe52c5bb` |
| `nd-unfolding/tests/test_ll5d.py` | `6fa5510efd8fde01` |
| `nd-unfolding/tests/test_ll5d_b.py` | `5391a42f82d5690c` |
| `nd-unfolding/tests/ll5d_a1a_mutation.py` | `5842163487612480` |
| `nd-unfolding/tests/ll5d_a1b_mutation.py` (unchanged) | `1b09bf22969b2698` |
| `nd-unfolding/ll5d_b.py` (unchanged) | `24312ca86f9e70ed` |
| `nd-unfolding/fd_1b_c2.py` (vendored, unchanged) | `522d7edd71643df6` |

**What led to it.** Both gates of 2026-11-10 STOPped (receipts #1013 and #1014): every reading was overridden to option
(3) because c2_vi reported 100 % of rows unmatched. The diagnosis (#1015) found an implementation defect. vi keys each
row on its coordinates and weight together, the signal side holds the weight in float64 and the bank's denominator in
float32, so no key can match. A local reproduction with both controls confirmed it.

**What the director checked:**
- coverage-5b-audit's GO at `12d37105`, with no blockers
  (https://github.com/josephbaileyy/MINERvA-OmniFold/pull/1019#issuecomment-6760011626):
  - rounding does not weaken vi: a ±1 float32 ulp bank-weight change, a signal weight just outside its float32
    interval, and a 1-ulp coordinate change all stay unmatched;
  - the REQUIRED MatchedRows test uses the writers' dtypes and fails at `a95cc39f`;
  - the vendored `fd_1b_c2.py` is byte-identical;
  - vicheck opens no truth, draws or flux constraint;
  - 82 and 29 tests pass on numpy 1.26 and 2; 58 of 58 and 27 of 27 mutants are killed.
- The director ran both suites from a `git archive` of M_A1a.2 (one thread, `PYTHONHASHSEED=0`, own TMPDIR):
  test_ll5d 81 passed and 1 skipped (the git-checkout seed test, as before); test_ll5d_b 29 passed.

**Rulings:**
1. **The rerun** authorized by `DECISION-20261110-joseph-ll5d-rerun-16-cells.md` runs from M_A1a.2 on R00–R15, in
   order:
   - `ll5d.py vicheck`, the preflight, part of that rerun. A PASS within MISMATCH_BOUND continues; a STOP goes to the
     director and Joseph unrepaired, as a genuine-mismatch finding;
   - `ll5d_calib`, required because read_calibration refuses a calibration made by other code. It reports whether its
     numbers reproduce run 2's bitwise;
   - both gates, back to back.
   Each connect pins M_A1a.2 and `ll5d.py` at `2b0224c6…`, and goes to the director with its sha256 before launch.
2. **The price** is about 23.4 node-h measured, with a peak projection of about 86.5 against LL5D's 148.0 node-h cap.
3. Rulings 1–8 of binding 2, and its addenda, stand otherwise. The seal on clip-prep products is unchanged.
4. The audit's lows L-1019-a to d (vicheck's edges, which gate nothing) are on the follow-up list.

Nothing is submitted, deposited or tagged.
