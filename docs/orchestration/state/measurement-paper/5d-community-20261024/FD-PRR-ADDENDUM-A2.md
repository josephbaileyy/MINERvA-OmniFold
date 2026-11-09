# FD-PRR ADDENDUM A2: the readout emits each truth's departure d beside b and r (2026-11-09, for coverage-5b-audit and the director's binding; nothing runs)

**By:** the valid-region lane (session director-helper-2), at the director's ruling of 2026-11-09 on V-HALF's input
(option B).

**Amends:** `FD-PRR-DECLARATION.md` rev 2 and Addendum A1, bound at M_A1 = `6727020a7c58b00dd00806151c627c8a24f72402`
(FD-PRR BINDING 1, addendum A1). Only `prr_read.py`, its test and its mutation harness change. Every reading, class,
control, price, licence and job is unchanged.

**CITABLE FOR:** the change to `prr_read.py`, its test, its required mutant, the fixture comparison and the new
digests.

**NOT CITABLE FOR:** anything the declaration does not license; any cluster result; any V-HALF class, which is
declared and licensed separately.

## 1. Why

V-HALF (`DECISION-20261109-joseph-bias-half-rule.md`) needs each graded truth's departure from the prior,
d_c = (X_c − P_c)/P_c, on R00–R15, with FD-PRR §4.1's definitions.
- **What the readout already has.** `prr_read.quantities` computes d inside `rho()` and writes b and r per cell,
  but not d (`prr_read.py:262` and `:276-285` @ `6727020a`).
- **Why d cannot be recovered from them.** d = b/r − 1 is unstable exactly where r ≈ 0, which are the cells that pass.
- **The director's ruling.** For V-HALF's input the director ruled option (B): the bias from F0b's committed readout,
  and d from FD-PRR's own computation. That ruling requires the readout to emit d.

## 2. The change

One line in `prr_read.quantities`, plus one key in its record:

    d = (x - p) / p
    ... "grade": table_ii(xh / x - 1, mats[t]), "d": d.tolist()}

- **What d is.** x is the entry's truth integral X on R00–R15, and p is the nominal truth's X at the entry's own
  split. That is §4.1's d, the same expression `rho()` uses.
- **d is dimensionless.** No P, X or X̂ value is emitted. The readout still passes F0b's `LeakGuard` before it is
  written, and the existing test `test_the_readout_carries_no_absolute_value` covers it.
- **Where d appears.** It is added to every `table` entry: all 181 products, B0 at every truth and floor seed among
  them. Route 2's `ibu` entries and `readout.txt` are unchanged.
- **Nothing else changes:**
  - no reading, class, control or label reads d;
  - `prr_probe.py`, `prr_ibu.py` and `sbatch_prr.sh` are byte-identical to M_A1;
  - the jobs keep running from the M_A1 deploy, and no connect changes.

## 3. The test, the mutant and the fixture comparison

- **`test_the_table_carries_each_truths_departure_d`** (REQUIRED, in `EndToEnd`). On the 40-cell synthetic run:
  - every table entry's d equals (X − P)/P computed from the fixture, to a relative 10⁻¹²;
  - d is exactly 0 at B0/nominal;
  - at B0/A7_gibuu, b = −0.3 d, which is the planted retention;
  - d is the only key added.
- **The required mutant, "d over the truth, not the prior,"** changes the denominator to x. The new test kills it.
- **The counts:** 105 tests (104 + 1) and 64 mutants (63 + 1).
- **The fixture comparison** (`fd/receipts-prr/a2/fixture_read.py` and `compare.py`):
  - **The run.** `prr_read.main` is run on test_planted_classes' fixture in a clean clone at M_A1 and in one at this
    addendum's code commit, with PYTHONHASHSEED=0.
  - **What must hold:**
    - `readout.txt` is byte-identical;
    - M_A1's `readout.json` has no "d" key;
    - every A2 table entry has a 16-value d, and no "d" key appears anywhere else;
    - A2's `readout.json`, with each table entry's "d" deleted, is byte-identical to M_A1's.

## 4. The new digests (sha256; the other three files are M_A1's)

| file | at M_A1 | after A2 |
|---|---|---|
| `prr_read.py` | `f35bc328…` | `d7c7c2c0d6cbe4a13d445a779335699de3d5275c4bcd3efc9f4e84a166868fbe` |
| `test_prr.py` | `44223143…` | `59e6fcf8d6a56c05fde47e3c1bc2aab96d7af81f18f70115eadbe34c74c31154` |
| `prr_mutation.py` | `4666aa06…` | `a6f673cdc4ab8bcb6b873bfd82ca20a886cfb7fae570a363cdc5230acb1bd3ad` |
| `prr_probe.py`, `prr_ibu.py`, `sbatch_prr.sh` | unchanged | `f87ee90c…`, `17acad82…`, `10290087…` |

## 5. Receipts

- **Where they are made.** In a clean clone at this addendum's code commit, which the receipt README names. A
  following commit adds only the receipt files.
- **How.** Each run is one serial process under `nice -n 19`, with every thread cap at 1. The runs are:
  - every class but `JobScript`;
  - the `JobScript` class alone;
  - the 64-mutant run;
  - the fixture comparison against a clean clone at M_A1.
- **Where:** `fd/receipts-prr/a2/`.

## 6. Where it runs

- **The PRR read runs at M_A2,** the commit that binds this addendum, after the full jobs end. It runs from a fresh
  clone, as every read does.
- **The cluster jobs are unchanged.** prr_iter (61024185), and prr_cap, prr_misc and prr_ibu when the director gives
  each its go, run `sbatch_prr.sh` and `prr_probe.py` from the M_A1 deploy. Neither file changes here.
