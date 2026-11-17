# The fresh cold read of 7264f975a: the Supplement-side fixes (2026-11-17)

**Asked by** the director, relaying Joseph 2026-11-16. The cold read is `~/codex-reports/paper-coldread-fable-fresh-7264f975a.md`,
which is not tracked. director-helper-3 fixed the paper-side items, except 3.6's paper clause, which journal-editor made at the
director's request.

**Fixed:**
- **3.2:** S4.2's refinement study is the lower-capacity variant (d). The source is
  `OUTCOME-20260925-s5n-stage1-development-fail.md`: family N, its refinement at the F2 parameters, the C3 closure FAIL. The
  reported estimator's closure is stated.
- **3.3:** the smaller-matrix comparison's baseline is stated: C_total + C_resp, less the truth's own component (T2B
  `t2b.json` records.*.existing.matrix).
- **3.4:** S4.4 lists the six candidates K1–K6, with K6 not testable (`OUTCOME-20261108-rs1-rounding-mechanism.md`).
- **3.6:** S8.5 gives one reason for "descriptive": the repair chosen after the stop. The paper's section 6.2 pointer names
  the later trial-run stop. The status is unchanged (`DECISION-20261109-joseph-coverage-case-wording.md` item 2).
- **3.7:** the two-observable estimator with deterministic training, in S7 and in table S11 test 5.
- **3.8:** S8.2 gives the six labels in the class conditions of `FD-PRR-DECLARATION.md` sec. 5.4, and which hold.
- **3.12:** S8.7's count of rejected tests is cut. The rejection and its limits stay.
- **3.13:** the band count is dropped.
- **3.15:** table S11 test 2 gives the supported-cell range beside the all-cell one, and the other maxima are marked all-cell.
- **3.16:** "withheld shapes", "held out of the analysis", and "153 quantities".

**Left for the director:**
- 3.12: cut S8.7 to a pointer, or list the tests in the paper's table;
- 3.13: reconcile the band inventories (33 against 34);
- 3.14: the 0.31 fraction;
- 3.16: whether S7's "q3 stress test" is the fake-data q3 tilt;
- table S11 test 2's one-clause criterion.

| read | what it read | verdict |
|---|---|---|
| `read9/` | the fixes at `b79e46011` | FAIL: the labels' conditions, held-out scope, the S11 range qualifier, test 5's column |
| `read10/` | the fixes at `8a0225d80` | PASS |
| `read11/` | 3.6: the paper clause at `5c7589bb5`, and S8.5's single reason | PASS |

**CITABLE FOR:** the wording as read against its cited records.
**NOT CITABLE FOR:** any result; a locked wording.
