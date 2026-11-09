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
