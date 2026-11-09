# BINDING 3: LL5D amendment A1b, the unfolds, walls, clipcheck, null and readout (director, 2026-11-09)

**Binds** [`LL5D-AMENDMENT-A1B.md`](LL5D-AMENDMENT-A1B.md) and its code, as merged in PR #951 at
**M_A1b = `585ccb84c3249b6606d1198b3c64eb398324b396`**. The audited head is `ea0ac43d`; the branch's later commit
`11981686` merged main and changed only the index files. The amendment and every A1b file are identical at `ea0ac43d`
and M_A1b.

| file | sha256 (prefix) |
|---|---|
| `LL5D-AMENDMENT-A1B.md` | `30c28721ce25d32f` |
| `nd-unfolding/ll5d_b.py` (new module; imports `ll5d.py` unchanged) | `24312ca86f9e70ed` |
| `nd-unfolding/tests/test_ll5d_b.py` | `642a45b84fd2b701` |
| `nd-unfolding/tests/ll5d_a1b_mutation.py` | `f5e683bb1892b7f6` |
| `nd-unfolding/ll5d.py` (A1a, unchanged since binding 2) | `9dbf9cf499f2c709` |

**Under:** [`LL5D-BINDING-1.md`](LL5D-BINDING-1.md) ruling 4 (A1b implements the declaration as bound at `1acdee66` and
responds to nothing A1a's jobs produce) and [`LL5D-BINDING-2.md`](LL5D-BINDING-2.md) ruling 3 (the seal).

## What the director checked

coverage-5b-audit's GO at `ea0ac43d` (https://github.com/josephbaileyy/MINERvA-OmniFold/pull/951#issuecomment-6728823757):
- 28 tests, A1a's 69 with A1b tracked, and 26 of 26 mutants reproduce at the head; every sha in the receipts was checked
  against git (`cfe67afb` is a real ancestor of the head, and the file digests match there and at the head);
- **ruling 4:** A1b reads exactly three A1a outputs, each by digest and O_NOATIME: `gate_ratios` (only the clipped
  variance ratio r_c, behind GATE_KEYS, and only on a gate PASS), `read_clip_prep` (the sealed file by the gate record's
  sha256, 300 draws per reading) and the clipmean's digest check; the readout's clipping fields come from A1b's own toy
  meta;
- **the weakened label** is Joseph's 11-03 clip rule item 4: strict < 0.9 per cell and per evaluation, descriptive, with
  all six mutants killed;
- the named choices (c), (d), (e) and (g) are sound: (c) is a descriptive realization check; for (d), the four
  `fd_1b_mc` functions that differ from `342c0ce5` are exact on A1b's one-universe calls.

The director ran `test_ll5d_b.py` from a `git archive` of M_A1b (one thread, `PYTHONHASHSEED=0`, own TMPDIR): 28 passed.

## Rulings

1. **A1b is bound at M_A1b** for §11's remaining steps: the pilot (walls), the rebuild of C_T at each truth, the toys,
   clipcheck, the null and the grading readout.
2. **The new module `ll5d_b.py`** is a named departure from §12's single-module wording, accepted.
3. **The seal holds until this binding is on main.** From then on, A1b may read `<out>.clipprep.npz` only through
   `read_clip_prep`, by the sha256 the gate record carries. Nobody opens or summarizes it outside that call.
4. **The pilot and bulk connects** are drafted against M_A1b and sent to the director with their sha256 before launch.
   They run only after the gate jobs read PASS for the reading concerned. A gate STOP goes to Joseph under #939, and
   POWER_SHORT comes to the director (binding 2 ruling 4).
5. **The price** stays inside LL5D's 148.0 CPU node-h cap; `iris` is read before each connect.
6. The audit's two lows (guard `mc.compose` to a single tag; §3c's "realization check" naming) are held for the
   follow-up list.

Nothing is submitted, deposited or tagged.

## Binding 3, note: two test files move under binding 2's addendum A1a.1 (director, 2026-11-09)

Amendment A1a.1 (PR #967, merged at `a95cc39f`) changes `nd-unfolding/tests/test_ll5d_b.py` (to `918d75bfd9c2c89f`,
adding `RealUnfold`) and `nd-unfolding/tests/ll5d_a1b_mutation.py` (to `1b09bf22969b2698`, adding the install mutant),
and `ll5d.py` (to `b49f5d5f793265ef`). It leaves `ll5d_b.py` unchanged. Those digests are bound in
[`LL5D-BINDING-2.md`](LL5D-BINDING-2.md), addendum A1a.1, and supersede the three rows above for the pilot and bulk
connects. Rulings 1–6 stand.

Nothing is submitted, deposited or tagged.
