# Binding: the 5D figures and the 16×16 data-product readout (2026-10-27)

**By** the paper-tighten lane, as director.

**Under** `DECISION-20261027-joseph-5d-integration-then-second-scope-review.md` (PR #408) item 2, and the presentation
decisions (`DECISION-20261026-joseph-5d-generator-comparison-presentation.md` and
`DECISION-20261027-joseph-chi2-table-format.md`).

**Binds,** both merged in PR #411:
- [`FD-G-FIGURES-DECLARATION.md`](FD-G-FIGURES-DECLARATION.md), file sha256 beginning `91ea240616f5dbe2`;
- [`FD-DATA-PRODUCT-DECLARATION.md`](FD-DATA-PRODUCT-DECLARATION.md), file sha256 beginning `6444fb77b1ac40cb`.

**MEASURES:** nothing. It authorizes their shared deploy, the two tools' runs and the independent figure check, at 0
node-h on a login node.

**CANNOT AUTHORIZE:**
- a new statistic;
- a χ² or p value drawn on a figure;
- any caption, axis label or legend wording as final, since those are Joseph's;
- whether the paper ships the data product as supplemental material, which is Joseph's;
- any Slurm job, GPU use, premium QOS or write to CFS.

## 1. The bound code

**The deploy pin** is `933cfe354ba6a3505c5b232df33d3d905de1de40`, main after PR #411.
- `B=/pscratch/sd/j/josephrb/fd-g-figures-20261027` and `D=$B/deploy/933cfe35`.

**At the PR head `0811272d`, the director checked:**
- the pins: `fd_g_figures.py` `06233dd9`, `fd_g_figures_check.py` `95cf2681`, `test_fd_g_figures.py`
  `fb3dcc86`, `fd_data_product.py` `1a42264f`, `test_fd_data_product.py` `1595ff05`;
- the two new suites, locally with `-B`: Ran 58 tests, OK. The deploy runs them with `test_fd_g_compare`, the
  declared "Ran 85 tests".

The tools have the same digests at `main`.

## 2. Rulings on the figure declaration's §7

1. **The ratio form is (a), data/prediction.** It matches the article's 2D figure. V_g is not drawn.
2. **GiBUU has its own axis,** `separate`, the default.
3. **The colours:** the article's colours, MnvTune v1 in grey as the prior, and markers that can be told apart in
   greyscale.
4. **The labels:** Stage G's names and qualifiers, as declared. The final wording is Joseph's, when he sees the figures.
5. **The modes:** three per 16-cell prediction, with the fraction of χ² printed. GiBUU is not drawn.
6. **The sensitivity figure** runs, for the note.
7. **The style** is the article's for all three figures.
8. **All three figures run,** as in the declared argv.
9. **The ordering** is as declared.
10. **No χ² on the ratio figure.** The caption, which is Joseph's, should say that the χ² uses the full covariance.
11. **A cosmetic rerun after Joseph sees the figures is covered** under five conditions:
    - the same pinned inputs;
    - the code change lands first as an amendment PR that the director reviews and merges;
    - a new `--out-dir`, with nothing overwritten;
    - K0–K8 and the independent checker of §2.3 re-run and pass;
    - a ledger row.

    Anything else is a new declaration.
12. **K2–K5 on the committed readouts at run time** are accepted as declared.

The data-product declaration's own choices are accepted as declared.

## 3. Conditions

1. **The deploy and tests** follow the figure declaration's §2.1, with `<pin>` = `933cfe35…`.
   - `$B` must not exist beforehand.
   - It must show HEAD equal to the pin, porcelain 0 before and after, the §8 digests, and "Ran 85 tests". Anything
     else is a STOP.
2. **The data product** follows its §2.2, then **the figures** follow the figure declaration's §2.2, with the declared
   argv exactly. The independent check (§2.3) follows. Any non-zero exit is a STOP, reported unrepaired.
3. **No step is rerun or repaired** without the director, except under ruling 11.
4. **The report is one PR to the director.** It carries:
   - the data-product readout;
   - the three figure PDFs and their sidecars;
   - the logs and ledger rows.

   It gives numbers only. The paper rewrite lane then replaces its `\fvpending` placeholders.
5. **Retention:** `fd-g-figures-20261027` joins the pscratch list.

The steps may start once this record is on `main`.

## Not changed

- Claims, KI-85, `\pubhold`, data-availability and release text are Joseph's. Nothing is submitted, deposited or
  tagged.
