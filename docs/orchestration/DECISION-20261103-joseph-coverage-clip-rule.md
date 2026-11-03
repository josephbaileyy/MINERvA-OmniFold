# DECISION 2026-11-03 — Joseph: both coverage tests clip the nature consistently; 1B gated on its own probe

**Recorded by** the paper-tighten lane, as director.

## What led to it

**The rule in force.** Option (a) of `DECISION-20261102-joseph-1b-redesign.md` item 3 clips a negative expected count
to zero in the pseudo-data, λ⁺ = max(λ, 0). The graded truth keeps its negative weights. The 2D coverage campaign
(cov2d) adopted the same rule.

**C1, the clipping probe.** At the expected counts, under first-order composition:
- about 0.27% of truth rows have a single universe weight ≤ 0;
- many more go negative in some draw, because several downward band shifts sum past −100%.

C1's truth-cell offsets were m_seen/N_c. cov2d found that this understates the first-order unfolded offset by about
1/ε_c and recorded an erratum (`fd/receipts-cov2d/clip/C1-ERRATUM.txt`).

**The independent consult (Sonnet).** `fd/receipts-cov2d/clip/consult/` holds PROMPT, ANSWER-1, ERRATUM-RELAY and
ANSWER-2, verbatim.
- It ranked consistent clipping (option 1) first, gated on its residual R_c and on a variance check.
- Multiplicative composition came second, gated on a ±20% variance check.
- Reporting coverage as not tested came third.
- Labelling the affected cells came last.
- It gave thresholds for each.

**C2, the corrected probe.**
- Code and reading were fixed before the run: `clip_probe2.py` (sha256 b95c5629…) and `c2_reading.txt` (b5b4fc4b…)
  at `1a07b07c` on `decl/cov2d-20261102`.
- Receipts are at `bc4965c4`.
- Login node, 0 node-h, wall 1:13, peak 9.52 GB.

What it found:
- **The control passed:** the first-order variance ratio is within 1 ± 0.2 in 100% of cells (G18) and 99.0% (AR23).
- **Every row matched** between the truth and signal trees.
- **Option (a)'s efficiency-corrected offset:** largest per-cell median 0.30 σ_Q, largest p90 0.58. The coherent
  offset bᵀQ⁻¹b has a median of about 42 per draw.
- **Option (1)'s residual R_c:** largest median 0.043 σ_Q, largest p90 0.10, signed positive; bᵀQ⁻¹b median about 1.4.
  - One cell (p_T 2.5–4.5 GeV/c, p∥ 6–7 GeV/c) reaches |R| = 4.27 σ_Q in a few draws, while its median and p90 are 0.
  - The clipped-composition variance ratio is within ±20% in 100% of cells (G18) and 97.1% (AR23); the AR23 median
    is 0.922.
- **Multiplicative composition fails its gate** at G18 (80.0% of cells).
- **The fixed reading gives option (1)** at both tunes.

## Joseph's answer, verbatim

Asked how the coverage tests should treat negative expected counts, now that the corrected probe has measured both
rules:

> Option 1, both tests (Recommended)

sha256 of the text plus a final newline begins `f9bc56468b825347`.

The option as put to him: clip the nature consistently, in pseudo-data and truth, for 2D coverage now. 1B uses the
same rule only if its own pre-bulk probe passes the same fixed reading, as a hard stop; otherwise 1B comes back to
him. The high-p_T outlier cell and the over-coverage lean are stated in the note.

## What is decided

1. **cov2d uses consistent clipping (option 1).**
   - A signal row with a negative composite weight is zeroed in both the pseudo-data and the graded truth, and a
     background row with a negative composite is zeroed.
   - This supersedes option (a) for cov2d.
   - cov2d's declaration (§9.2, §6 (ii), §14) is revised to it, then audited and bound by the usual two steps.
2. **1B uses the same rule, gated.**
   - Before its bulk, 1B's clipcheck runs C2's quantities, through cov2d's code imported or copied verbatim with an
     equality test (addendum A2.1 to amendment 2, #717).
   - It applies C2's fixed reading (`c2_reading.txt`) unchanged, as a hard stop.
   - If that reading gives option (1), 1B runs with `--clip-rule nature`.
   - Otherwise nothing launches, and 1B returns to Joseph.
   - Option (a) of `DECISION-20261102-joseph-1b-redesign.md` item 3 is superseded for 1B only once that reading has
     given option (1). Until then, no clip rule is bound for 1B's bulk.
3. **1B's other gate is unchanged:** stage 1 still waits for the B4 estimator probe
   (`DECISION-20261102-joseph-bias-and-stabilisation-routes.md`).
4. **To the note, not the paper,** per `DECISION-20261102-joseph-1b-redesign.md` item 4:
   - the clipping rule;
   - the outlier cell;
   - the expected lean toward over-coverage in cells where clipping narrows the spread (a false-pass risk).

   **The director's ruling, not Joseph's:** cov2d's declaration fixes, before any toy, the consult's reading that a pass
   in a cell whose clipped variance ratio is below 0.9 counts as weakened.

Nothing is submitted, deposited or tagged.
