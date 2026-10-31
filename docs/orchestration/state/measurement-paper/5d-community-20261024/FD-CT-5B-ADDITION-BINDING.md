# Binding: the 5B run-period block's addition, C_total + C_resp + C_PL,5D (2026-10-31)

**By** the paper-tighten lane, as director.

**Under** `DECISION-20261030-joseph-4b-not-now-5b-audit-then-add.md` (#542), item 2, after the audit's `stop` = false
(`FD-CT-5B-AUDIT-REPORT.md`, #555).

**Binds** [`FD-CT-5B-ADDITION-DECLARATION.md`](FD-CT-5B-ADDITION-DECLARATION.md), merged in PR #560 with its code.
Its file sha256 begins `881e7ad80aa308e3`.

**AUTHORIZES:**
- the deploy and the nine test modules;
- one run of `fd_cpl_addition.py chain` on a login node, at 0 node-h, writing the revised products beside the current
  ones.

**CANNOT AUTHORIZE:**
- overwriting any committed product;
- any change to the paper or note text. That comes through the paper lane's usual checks, with results printed with and
  without the block;
- a rerun after a failed control;
- any Slurm job or write to CFS.

## 1. The bound code

**The deploy pin** is `3b12c451d617b860450f516b3b63266379308f80`, main after PR #560.
- `BA=/pscratch/sd/j/josephrb/fd-ct-5b-addition-20261031`, which must not exist beforehand.

**At the PR head `54ca7340`, the director checked:**
- all 15 §8.1 code pins, each against its file;
- the nine declared test modules, locally with single-threaded BLAS: **Ran 419 tests, OK**, with 0 porcelain lines
  after;
- the mutation receipt: pass 3 killed 63 of 63;
- the review's one High (control T on the shape-only rows) is fixed, with a two-direction Table test.

## 2. Rulings

1. **Control R's exclusions,** as §5 names them:
   - readouts compare numbers and structure, not strings, excluding argv, code_sha256, code and versions;
   - the data product's CSVs are byte-exact, and its JSON equal except argv;
   - the deposit's CSVs are byte-exact, and its JSONs equal by `without_code`;
   - the figures' PDFs are byte-exact, and their sidecars equal except argv, code and versions.
2. **Every revised product is labelled with its matrix** and written beside today's. The results are published both with
   and without the block, and the record says the addition followed the data (decision item 2).
3. **1B keeps its declared matrix,** `fd_data_product.json` `b79556f0…`, as its binding states.

## 3. Conditions

- **Deploy and tests** as §6. Anything but HEAD = pin, 0/0 porcelain lines, the §8 pins and "Ran 419 tests … OK" with no
  skip is a STOP.
- **One chain run.** A failed control R or any other refusal is reported unrepaired.
- **The report** is `FD-CT-5B-ADDITION-REPORT.md`, as a PR to the director, giving every product's digest before and
  after and the with/without numbers, with no reading.

The steps may start once this record is on `main`. Tell the director before connecting.
