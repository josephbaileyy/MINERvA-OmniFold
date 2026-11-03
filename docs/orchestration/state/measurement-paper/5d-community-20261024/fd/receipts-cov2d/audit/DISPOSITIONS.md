# COV2D audit: dispositions (2026-11-03)

**By** the `cov2d` session, for the director's binding 1.

**The audit.** A fresh Sonnet subagent, read-only, on `decl/cov2d-20261102` at `2372f800`.
- `PROMPT.txt` is the prompt it was sent, byte for byte.
- `ANSWER.txt` is its answer, verbatim. One transport artifact is undone: the notification that carried the answer
  escaped `<` as `&lt;`, twice (findings 6 and the §5.2 check), and `ANSWER.txt` has `<`.
- Verdict: **READY AFTER MINOR FIXES**, with no BLOCKING finding.

**MEASURES:** nothing. **CANNOT AUTHORIZE:** any run. The director binds.

Section numbers are the declaration's (`COV2D-DECLARATION.md`). Each disposition is one of:
- **accepted**: the declaration or the code changed;
- **accepted in part**: what changed and what did not, with the reason;
- **for the director**: the choice is a ruling.

| # | finding | disposition | where |
|---|---|---|---|
| 1 | §12–§13 claim more than the test supports | **accepted** | §5.2 size, §12, §13 |
| 2 | §6 (ii)'s 0.5 σ_c reading cannot fire | **accepted in part; the threshold is for the director** | §6 (ii), §14 item 2 |
| 3 | no control of the drawn pseudo-data, or of universe and lateral unfolds via `--data-file` | **accepted** | §9 items 11–12, §10 step 5 |
| 4 | the receipt ran on an earlier `cov2d.py` blob | **accepted** | §9.2 |
| 5 | the receipt's text says it calls `compose` and `peak` | **accepted in part** | §9.2 |
| 6 | `--no-pins` still allows PASS; a NaN ratio passes `<= 0` | **accepted in part** | §9.2 |
| 7 | rounded figures; the cap's arithmetic | **accepted** | §9.2, §8 |
| 8 | a driver citation off by six lines | **accepted in part** | §4.3 |
| 9 | the weakened lists are not fully pinned in code | **accepted** | `test_cov2d.py` |
| 10 | the outlier cell looks like a single-row effect | **accepted in part** | §5.2 |
| 11 | nine things not fixed in advance | **accepted** (one line each) | §4.2, §5.2, §6 (ii), §8, §9.13, §10 |
| 12 | the weakened label rests on a proxy | **accepted** | §5.2 |

## 1. Accepted

- **§13** now licenses coverage "at least at the nominal rate". It names the graded matrix: the model term included,
  the run-period term excluded.
- **§13 states the masking.** C_model is in C_T but is not drawn. At the data it raises the median per-cell relative
  σ from 6.41 % to 7.90 % (`RE2-PARTC-REPORT.md:254-258`), so a pass can hide a shortfall of roughly that size in the
  drawn blocks. §6's spread-alone readout shows it, beside the verdict.
- **§5.2's size claim is now conditional** on the toys' errors following the null's law, with three departures named.
  Un-centred draws and clipping can move the flag rate either way. The undrawn C08, C_model and simulation statistics
  can only lower it.
- **§12's UNDER-COVER text** calls the rate the test's false-flag rate under its null's law.
- I kept the auditor's citation range `:254-256` out of the text. The 7.90 % row is line 258, so the declaration
  cites `:254-258`.

## 2. Accepted in part; the threshold is the director's

**The auditor is right that the reading will not fire.**
- The toys' natures are C2's 300 declared draws per tune.
- C2's largest per-cell median |R| is 0.043 σ_Q (G18) and 0.042 σ_Q (AR23), far below 0.5.
- §6 (ii) now says so, and gives the condition under which it could fire: C_T's σ_c about ten times smaller than
  Q_R's.

**The auditor's claim that 0.5 "was chosen after C2's numbers were known" is not right.**
- `git log -S'exceeds 0.5 σ_c'` puts the threshold in the declaration's first draft, `fc2cd112` (2026-11-02 18:06
  −0800).
- That is before the first clipping probe's code, `d94d4820` (2026-11-02 22:55 −0800), and before either probe ran.
- §6 (ii) now cites both commits.

**I did not change the threshold.** Lowering it to 0.2 σ_c or a p90 rule, as suggested, would pick a number after
C2's distribution was read, which is the defect the auditor warns about. The director rules on §6 (ii) at binding 1
(their message of 2026-11-03), and §14 item 2 puts this finding before them.

Also added: where S_c ≤ 0 or N_c ≤ 0, R_c is missing and counted; medians are taken over the defined toys.

## 3. Accepted

- **§9 item 11:** every pseudo-data file is read back and checked:
  - exactly Σk rows;
  - a per-reco-cell histogram equal to the counts' per-cell sums;
  - every row a reco-passing row's (`sim`, `sim_pz`);
  - at d̃_T, the total within 5 Poisson σ of Σλ⁺.

  It is INVALID on failure.
- **§9 item 12:** in the pilot, one universe unfold (`$UNI`, `MaRES:0`) and one lateral unfold (the first lateral
  omnifile of part B's J3) run with `--data-file` set to control (2a)'s file. Each must reproduce part B's product to
  ≤ 1e-8 relative on the 205 cells.
  - Part B's product sha256 is checked against `RE2/run/partb_readout/sums` first, through `O_NOATIME`.
  - A missing product is INVALID.
  - About 0.3 node-h, inside the 2.0 pilot reserve.
- §10 step 5 lists it.

## 4. Accepted

§9.2 now states both digests:
- the receipt ran `cov2d.py` sha256 `4b0744d7…`, equal to `53e50a6e~1`'s blob;
- the bound file is now `0d852a69…`.

Their diff adds `WEAKENED_BELOW`, `OUTLIER_CELL`, `weakened_cells` and docstrings, and the receipt references none of
them (`grep -c` gives 0 in `cov2d_receipt.py` and `cov2d_writer.py`).

## 5. Accepted in part

The declaration's text is corrected. `n1_chunk` computes the first-order sum and the peak inline (`ad += G[:, :, j] -
cvr`), the same arithmetic as `cov2d.compose` and `cov2d.peak`. §9.2 says so, and names the docstring at
`cov2d_receipt.py:11` as wrong.

**Not changed:** the receipt's code and docstring. The receipt ran once, as R1, on blob `c085b51f…`, and its result
is bound with that blob. Editing it now would bind a blob that never ran.

## 6. Accepted in part

Both defects are real in the code. Neither touched R1:
- **R1's argv had no `--no-pins`** (`R/receipt/receipt.time`: `cov2d_receipt.py --out …/receipt.json`).
- **No truth-cell ratio was NaN.** R1's `min_cell_ratio_to_cv` is 0.379 (G18) and 0.369 (AR23), both finite, and
  `np.min` propagates NaN. Non-finite weights were zeroed before accumulation (36 in `w_reco`).

§9.2 records this. The receipt is not changed after its run, for the reason in 5. Any rerun is an amendment that fixes
both first.

## 7. Accepted

- **§9.2 now gives each array's figures,** recomputed from the declaration's own receipt table:
  - `w_reco`: 11,358,837 / 32,849,103 = 34.6 % of rows; 331,386,043 / (32,849,103 × 600) = 1.68 % of pairs;
  - `w_truth`: 37.9 % of rows; 1.82 % of pairs;
  - `w_bkg`: 258,026 / 658,227 = 39.2 % of rows; 1.91 % of pairs.
- **§8's cap** is 1.25 × 126.2 + 6.0 + 2.0 = 165.75, written 165.8.

## 8. Accepted in part

The declaration cites code at `108040f8` unless a sha is given (its header). There, `if args.closure:` is line 1698,
and the refusal runs to 1702. The auditor read the hooked driver, where the hook's 21 lines move it to 1703–1708. The
range is corrected to `:1698-1702`, at the stated base.

## 9. Accepted

`test_c2_weakened_cells_and_outlier` now pins:
- both full lists (`C2_WEAKENED`, equal to §5.2's text, checked by a parse of the declaration);
- each tune's smallest ratio and its cell: 0.865 in cell 127 at G18, 0.761 in cell 43 at AR23.

The suite gives 40 passed (`R/code/tests_cov2d.out`). The mutation harness was rerun against the strengthened test
(`R/code/mutation_cov2d.out`).

## 10. Accepted in part

§5.2 now reports the bit-identical option (a) maximum, 4.23984232307767 σ_Q at both tunes. It says r_T cancels there,
so few rows, perhaps one, drive it, and names this as the auditor's inference.

**Not done before binding:** identifying the row. That needs a read of `$UNI`, which is a connect the director approves
and which moves nothing in the design. Instead the pseudo-data job records, for cell 216, each toy's negative-composite
rows and their weights, and the report states them.

## 11. Accepted, one line each

- **The Poisson generator** (§4.2): `default_rng([seed, DRAW_SALT, 1])`, separate from the draw's stream; d̃_T the same
  at its seed.
- **A failed run** (§9 item 13): no toy or block run is dropped, replaced or re-seeded. A crash, OOM, kill or time-out
  is INVALID and goes to the director (the standing rule).
- **"Data size"** (§4.2): Σλ⁺ at the POT scale, not forced to 4,119,797. Each toy records Σλ⁺ and the ratio.
- **R_c where S_c ≤ 0 or N_c ≤ 0** (§6 (ii)): missing, counted, excluded from the medians.
- **Σλ⁻ per reco cell** (§4.2): restored for signal and for background. The revision of 53e50a6e had dropped the
  signal's per-reco-cell record.
- **Joint level** (§5.2): the label is per cell. The joint reading carries none, and the report gives each tune's
  weakened share beside it. A joint label would be a new rule, which is for the director if wanted.
- **The re-price baseline for toys** (§8): the central run's part B wall per run.
- **The pseudo-data reserve** (§8): stated as a reservation, 2 × 3 node-h, against the receipt's 44:45 login-node pass
  over `$UNI`. Above it is REPRICE.
- **Binding 2's window** (§10): the amendment's code is written while binding 1 is pending, so the seven days are for
  its audit and binding.

## 12. Accepted

§5.2 now says three things:
- the ratio is a truth-level proxy, not the variance of e;
- the toys use the same draws, so it is this ensemble's realized value;
- AR23's first-order control has median 0.953 and minimum 0.793 over these draws.

"Some listed cells are there by sampling" is replaced: part of what the label marks is this draw set's own shortfall,
which the toys see too. The director accepted the lists as fixed (2026-11-03).

## The director's messages, applied in the same commit

- **§14 item 6** (each tree clipped on its own composite) is marked confirmed. The director will add a clarification
  to the decision record.
- **§14 item 2** is marked for ruling at binding 1.
