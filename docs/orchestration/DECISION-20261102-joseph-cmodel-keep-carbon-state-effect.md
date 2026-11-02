# DECISION 2026-11-02 — Joseph: keep C_model on carbon, and state its measured target effect

**Recorded by** the paper-tighten lane, as director.

## What led to it

- **The measurement.** GENCMP addendum E2 (bound in `FD-GENCMP-AMENDMENT-E-BINDING.md`, #675 and #677) rebuilt C_model
  with NuWro's and GiBUU's shape ratios from CH (12/13 carbon + 1/13 hydrogen) in place of carbon, with everything else
  fixed.
- **Its controls.** Every control passed, at 0.22 node-h.
- **Its result,** in the with-arm total χ², from carbon C_model to CH C_model, as the lane reported it (to be verified
  against E2's committed readout before any paper edit):

  | prediction | carbon C_model | CH C_model | Δ |
  |---|---|---|---|
  | GENIE CV | 107.18 | 106.27 | −0.92 |
  | GENIE+MEC | 229.09 | 223.53 | −5.56 |
  | NuWro | 127.69 | 127.86 | +0.17 |
  | GiBUU | 47.78 | 45.10 | −2.68 |

  The largest change over both arms and both kinds is 6.07.
- **The flag.** The pre-declared flag (a with-arm total above 2.3) was exceeded. Binding ruling 4 then brings Joseph the
  question of whether to rebuild the reported C_model on CH.
- **The seed check.** The estimator is seed-invariant: the seed-43 unfolds are bitwise equal to seed 42. So Δ is the
  exact effect of the target change on this data, not a noise draw.
- **The consult.** An independent Sonnet consult is verbatim in
  `state/measurement-paper/5d-community-20261024/FD-GENCMP-E2-CMODEL-CONSULT-{PROMPT,ANSWER}.txt` (#678). It recommended
  keeping the carbon C_model and stating the measured change, with two no-cost sensitivity readouts. The director
  agreed.

## Joseph's answer, verbatim

Asked whether the paper should keep the carbon C_model and state the measured change, or rebuild C_model on CH:

> Keep carbon, state it (Recommended)

sha256 of the text plus a final newline begins `9b4ae7f04c86db55`.

## What is decided

1. **The reported covariance is unchanged.** C_model stays built from the carbon NuWro and GiBUU shape ratios.
2. **#651 item 6's caveat becomes a measured statement.**
   - It gives the signed χ² change per prediction from taking those ratios from CH, in the reported matrix.
   - It is quoted from E2's committed readout.
   - It does not use the seed-variation clause: the estimator is seed-invariant, so there is no seed noise floor to
     compare against.
3. **GiBUU's "χ² rises with the CH correction" sentence (#651 item 1) is revised.**
   - **The fact behind the revision.** With C_model on CH, GiBUU's CH total is 45.10, against 45.49 for carbon in the
     analysis definitions. So the +2.3 rise comes mostly from pairing a CH prediction with a carbon-built C_model.
   - **What the revised text does.** It states this. It does not leave the rise standing as a property of GiBUU. The
     wording goes through the paper lane's report.
4. **Two sensitivity readouts are added,** computed from existing products with no new unfold:
   - χ² with C_model removed, and with C_model doubled, for the four corner predictions;
   - the largest per-cell σ change when C_model moves to CH.

   They go in the note. The paper's sentence may cite them as the scale of C_model's own arbitrariness.
5. **The order.** E2's report merges first. Then the readouts in item 4. Then the paper round, reviewed by the director
   against this record.

Nothing is submitted, deposited or tagged.
