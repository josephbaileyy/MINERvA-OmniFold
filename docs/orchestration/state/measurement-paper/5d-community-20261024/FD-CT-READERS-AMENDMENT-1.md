# AMENDMENT 1 to the cheap tier's readers: 5A's leak-guard table (2026-10-29)

**By** the measurement session (`coverage`), for the director to re-bind.

**Under** the director's ruling of 2026-10-29 on the 5A STOP, option (c): the diagnostic (a) first, then, "if (a)
confirms the mechanism", (b): "the code fix with a two-direction test … a mutation check on the new branch … an
amendment declaration, FD-CT-READERS-AMENDMENT-1.md, with new §8 pins. Run nothing until I re-bind it."

**Amends** [`FD-CT-READERS-DECLARATION.md`](FD-CT-READERS-DECLARATION.md) (`0571c973…`), bound by
[`FD-CT-READERS-BINDING.md`](FD-CT-READERS-BINDING.md) at `28ea789e`. Everything not named here stands as declared and
bound.

**MEASURES:** nothing new. The 5A STOP and the diagnostic are in [`FD-CT-READERS-REPORT.md`](FD-CT-READERS-REPORT.md) §4.

**CANNOT AUTHORIZE:** running anything, which needs the director's re-binding; a rerun of 3a or 4C, whose bound runs
stand; any covariance component, change to the reported matrix, claim or wording.

**CITABLE FOR:** what changed in the tool, why, how it is tested, and what the 5A rerun will be.

**NOT CITABLE FOR:** any 5A result.

## 1. What failed, and why

- **The bound 5A run** exited 3 at the leak guard, refusing "22 number(s)", with nothing written (`FD-CT-READERS-REPORT.md` §4).
- **The diagnostic** that the ruling authorized found:
  - all 22 numbers were tokens inside strings;
  - each matched only the role "f/central X_sup" (≈ 1) for cell R09;
  - R09 is the one cell whose central partial integral over the 2D term's support, X_sup, is f to within
    LEAK_REL = 10⁻¹³ but not exactly.
- **The cause** is the bound tool's rule (`fd_ct_readers.py` at `cccc47aa`, `run_period`). It dropped a central X_sup
  from the guard's table only where the cell's outside share was exactly 0. R09's share is non-zero but below the
  guard's precision. So f/X_sup ≈ 1 entered the table, and every "1" in a string was refused. No written number
  carried f or an absolute value.

## 2. The change

**In `run_period`:** a central X_sup is dropped wherever it is f to the guard's own precision, |X_sup/f − 1| < LEAK_REL,
by a new pure function `near_f`. That covers the exact case the bound rule handled and R09's case:

```python
def near_f(x, f):
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.abs(x / f - 1.0) < f0.LEAK_REL
...
partial.append(np.where(near_f(sup_int, f), np.nan, sup_int) if vn == "central" else sup_int)
```

- **The fix changes only which near-f integral the guard's table omits.** Any value the guard no longer checks
  against is a central X_sup, or a form of one, that is already f to within LEAK_REL. Every other entry of the table
  is unchanged: f, the prior's integrals, the prior's partial integrals, and every central partial integral off f.
- **Why this is the right boundary:** an X_sup within LEAK_REL of f is f, to the guard. f is already in the table, and
  every form the guard derives from such an X_sup (f/X, X/f, f − X, …) is either f itself, about 1, or below the floor.
  So dropping it removes nothing the guard protects.
- **The prior's partial integrals** still all enter the table, unchanged. They involve no f.
- **Nothing else changes:** no statistic, control, readout key, label, constant or threshold. The 3a and 4C code paths
  are untouched.

## 3. Tests

Three new tests in `test_fd_ct_readers.py`, now 62 tests in all:

| test | direction |
|---|---|
| `test_near_f_is_the_guards_precision` | `near_f` at its boundary: 5 × 10⁻¹⁴ in, 2 × 10⁻¹³ and 10⁻¹² out, NaN out |
| `test_a_central_partial_integral_within_leak_rel_of_f_is_dropped` | the fixed direction: R12's central content outside the support is made tiny, so its X_sup is f to within LEAK_REL but its outside share is not 0. The run writes its readout. **On the bound tool `cccc47aa` this test fails exactly as the field run did:** exit 3, "REFUSED leak guard … 24 number(s)" |
| `test_a_planted_partial_integral_off_f_is_still_refused_after_the_fix` | the other direction: with R12 dropped, R08's X_sup, and its share 1 − X_sup/f, planted in the readout, are still refused (exit 3) |

The fixture method `Tree.shrink_central_outside` builds the near-f cell.

## 4. Mutation check

`fd/receipts-ct/declaration/mutants.py` adds four mutants of the change to the 78 of round 3: reverting to the
outside-share rule; `near_f` at threshold 0; at threshold 1, which would also drop off-f integrals; and every central
partial dropped. The round ran all 82 on the amended tool `32e9b061…` and tests `9c543aee…`: **82 of 82 killed**,
none unapplied, with the tool restored and its sha256 checked after every mutant and at the end
(`fd/receipts-ct/declaration/mutants-am1.log`).

## 5. The rerun: 5A only

**Deploy and tests,** as the declaration's §2.1, at the new pin, into a new directory:
- `B=/pscratch/sd/j/josephrb/fd-ct-readers-am1-20261029`, which must not exist beforehand;
- `D=$B/deploy/<pin8>`.

The bound run's `fd-ct-readers-20261028/` stays as it is: its deploy, logs and 3a and 4C readouts are the bound run's
evidence.

**It must show:** HEAD equal to the pin; 0 porcelain lines before and after; the §6 digests; `tests rc=0` with
"Ran 153 tests … OK" (150 + 3, run locally with `-B` and a TMPDIR at these digests).

**The run:** the declaration's §2.2 `period` command, unchanged except for `$B` and `$D`. Its timeout is 75 s, and its
exit codes are as declared. **3a and 4C are not rerun.**

**The report** is `FD-CT-READERS-5A-REPORT.md`, with the fields binding §3 condition 4 sets for 5A. It states that 5A's
central-value weighting departs from the addendum's "the cell's prior weight", and why (binding ruling 6).

**Stop rule:** as declared. Any refusal, non-zero exit or timeout is reported unrepaired.

## 6. Pinned bytes

At this amendment's commit:

| file | sha256 |
|---|---|
| `nd-unfolding/fd_ct_readers.py` | `32e9b061c0102fba5f8c03badceabc02135b5ee4f3a573522d4701126a7eb8b2` (was `cccc47aa…`) |
| `nd-unfolding/tests/test_fd_ct_readers.py` | `9c543aee844907e677fa3820f005424b80a9e09939e78b6d7e6a71e972c94d7c` (was `c68d412a…`) |
| `nd-unfolding/fd_f0_regrade.py` | `0dfa722c2b74abed09fb255ccb7c0e80e6c55eb922ea1326dd74e6c880697aa2` (unchanged) |
| `nd-unfolding/s1_assemble.py` | `b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7` (unchanged) |
| `nd-unfolding/s5p_stage1_inspect.py` | `26569afc0da46f21167e0908014712cd800c1e14ac63a4b245a0b493c76d3d71` (unchanged) |
| `nd-unfolding/pv-ladder/readouts/h2_definition.json` | `b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89` (unchanged) |

## 7. For the director

1. **The boundary is LEAK_REL,** the guard's own tolerance, so the table and the guard agree on what "equals f" means.
2. **Only 5A reruns.** 3a's and 4C's bound runs stand. Their code is unchanged, as the diff shows.
3. **A new `$B`** keeps the bound run's evidence untouched.

## 8. Not changed

Every statistic, control, label and constant of the declaration; the 3a and 4C readouts; every covariance, cell,
readout and κ; `docs/analysis-note/**`.
