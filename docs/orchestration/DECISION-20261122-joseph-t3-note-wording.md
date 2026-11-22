# DECISION 2026-11-22 — Joseph: the Tier 3 paragraph in the note's Sec. 4

**Recorded by** journal-editor, for the director, who relayed Joseph's approval.

## What led to it

- **Tier 3.** The noise-free pipeline tests at the two flagged truths
  ([`T3-PIPELINE-TESTS-DECLARATION.md`](state/measurement-paper/5d-community-20261024/fd/tier3-20261110/T3-PIPELINE-TESTS-DECLARATION.md),
  rev 4) completed with one read, verdict COMPLETE. The receipt PR #1241 is merged on `main` as `b4336c477`.
- **The readout.** `state/measurement-paper/5d-community-20261024/fd/tier3-20261110/run-20261121/cluster/read/readout.json`,
  sha256 `b0362c387ec3d8fd48616abe5dcf589407fd007b62214d6297b47418d1a9ecce`. The rewrite branch does not contain #1241,
  so the note's branch carries a byte-identical copy of that one file, at main's path.

## The final text

Joseph accepted it through the rewrite helper on 2026-11-22, and the director relayed it. It is the text the
note prints. The text is quoted as relayed, with each number as relayed rather than as its key. The sha256 is of the
text plus a final newline:

> A second prespecified study replaced one part of the procedure at a time on the same noise-free samples, with the iterations continued to 50, where $\rho$ levels off. At the GiBUU hybrid, where the baseline $\rho$ is 0.094, giving the events that fail the selection their true weights, an oracle input that no data analysis has, lowers $\rho$ to 0.026, about the value reached when every event receives its true weight before the second step. Letting the missed events keep their previous weights instead of the regressor's prediction, weighting the regressor, or removing the background with its refinement each change $\rho$ by less than 0.002, against a threshold of 0.05. The retention there is consistent with a limit set by the weights of the missed events. At the $q_3$ tilt, where the baseline $\rho$ is 0.16, no replacement lowers $\rho$ by 0.05, and true weights for every event still leave $\rho=0.10$ after the second, truth-level step, consistent with a limit set by that step's representation. At both truths the result matches the pseudo-data at reconstruction level but not at truth level, consistent with directions the reconstructed inputs constrain weakly.

(`4d358c86175e9f3fc09a2baf9ff2f288f305aa6d9e06e39a7ce26a06a6f7404f`)

## The first approved text (superseded)

Joseph first approved this text on 2026-11-22. It was committed at `51dc0d8d8` and replaced the same day by the
final text above. The sha256 is of the text plus a final newline:

> A second study, specified before it ran, replaced one part of the procedure at a time on the same noise-free samples, with the iterations continued to 50, where $\rho$ levels off. At the GiBUU hybrid, where $\rho$ levels off at 0.094, giving the events that fail the selection their true weights, which no data analysis has, lowers it to 0.026, about the value reached when every event receives its true weight. Letting the missed events keep their previous weights instead of the regressor's prediction, weighting the regressor, or removing the background with its refinement each change $\rho$ by less than 0.002. The retention there is consistent with a limit set at the missed events. At the $q_3$ tilt, where $\rho$ levels off at 0.16, no replacement lowers $\rho$ by \fvval{prr-floor}, and true weights for every event still leave $\rho=0.10$ after the second step, consistent with a limit set by that step's representation. At both truths the result matches the pseudo-data at reconstruction level but not at truth level, consistent with directions the reconstructed inputs constrain weakly.

(`97bdb8542385d1b9277700e6ec62230379db9efdcad40164bf50e7d6745eea8c`)

## What it decides

1. **Placement.** The final text goes in `docs/analysis-note/sec4_higherdim.tex`, in the retained-fraction paragraph
   (`sec:fived16-prr`). It follows the sentence ending "reduces retention by \fvval{prr-floor} or removes either bias
   flag."
2. **Numbers.** Each printed number is a `\fvval` key from `make_values_fived16.py`'s `t3_values()`. The keys read
   `table["<arm>/<truth>/s991000"]["per_k"]` at k = 50, and OP at k = 2, its last iteration:

   | key | printed | readout |
   |---|---|---|
   | `t3-kmax` | 50 | the last k of every arm except OP |
   | `t3-rho-b0-gibuu` | 0.094 | B0, A7_gibuu: 0.0943 |
   | `t3-rho-mo-gibuu` | 0.026 | MO, A7_gibuu: 0.0258. OP, A7_gibuu: 0.0257, the "about the value" comparison, not printed |
   | `t3-dmax-gibuu` | 0.002 | a bound: the largest \|ρ_arm − ρ_B0\| over MU, MW and SO at A7_gibuu is 0.0018 |
   | `t3-rho-b0-q3` | 0.16 | B0, q3: 0.1628 |
   | `t3-rho-op-q3` | 0.10 | OP, q3: 0.1020 |

   Both occurrences of 0.05 print `\fvval{prr-floor}`, the existing key: "against a threshold of 0.05" and "no
   replacement lowers $\rho$ by 0.05". `t3_values()` asserts that every Tier 3 arm's bar equals it. The final text adds
   no key.
3. **Wording limits.** Each "consistent with" clause is one of the declaration's §5.5 composite labels, which
   `t3_values()` asserts from the readout:
   - at A7_gibuu, "a limit set at the misses", which the text prints as "a limit set by the weights of the missed events";
   - at q3, "a limit set by step 2's representation";
   - at both, "weakly constrained directions".

   The readout's NOT-CITABLE list (`labels.not`) still holds: no cause beyond "consistent with", no estimator change, no
   held-out claim and no data quantity.

## Scope

Only the one paragraph in the note's Sec. 4, plus its value keys. Table II, its grades and every reported result are
unchanged (declaration §8).
