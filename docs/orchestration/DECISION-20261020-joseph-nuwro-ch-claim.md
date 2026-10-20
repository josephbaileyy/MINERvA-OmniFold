# DECISION 2026-10-20 — Joseph: how the methods paper states the generator rejections after the hydrocarbon replays

**Recorded by** the paper-tighten lane, as director (Stage F). The director reported the following.

- **The replays (main `7adb001d`):** the measurement session's beside-A7 replays with NuWro and GiBUU corrected from
  carbon to CH (`state/measurement-paper/phase1/mp3b/`, `mp3c/`). Both are descriptive, not re-grades.
  - **NuWro total:** stays rejected only through the Holm re-sort. At its frozen position it would be undetermined,
    and in the κ = 3 family it is not rejected.
  - **NuWro shape, and both GiBUU tests:** stay rejected. GiBUU's replay carries the label "B3 (sampling closure)
    failed on hydrogen; a post-hoc bias check of its premise passed at ≤ 0.1 σ_c".
- **The director's recommendation:**
  - keep the ten recorded decisions;
  - say in the abstract and body that NuWro's total-rate rejection is not robust to correcting its carbon prediction
    to CH;
  - report the CH replays beside the recorded results.

Joseph's answer, verbatim:

> I agree with your recommendation for NuWro's total-rate rejection for now, but consider the readability of the paper
> as well. if it makes sense and sounds good, it never hurts to give a high-level claim and refer to the note, right?

sha256 of the text plus a final newline begins `579d0caecab94ca5`.

## What is decided, as the director reads it

- **The recommendation is adopted "for now", so it is provisional** (like J3–J5) until the review with Ben.
- **The paper states the result at a high level and refers to the note for the detail.**
  - The abstract and the generator-test results keep the ten recorded decisions.
  - They add one plain sentence: correcting the two carbon-only predictions to the hydrocarbon target moves both
    toward the data, and NuWro's total-rate rejection does not survive that correction robustly.
  - The paper carries no Holm re-sort mechanics, κ variants or gate labels. Those belong in the note.
- **The note carries the detail.** It gets a subsection in `sec_joint.tex` with the CH replays for NuWro and GiBUU:
  - the per-cell target ratios and the shifts of T;
  - the frozen-position and re-sorted readings, and the κ = 3 result;
  - GiBUU's B3 label and its bias check;
  - the NuWro hydrogen-generation exclusions;
  - the statement that the replays are descriptive and do not re-grade A7.
- **The same principle applies to the rest of the rewrite, at the director's judgement.** Where a statement makes
  sense at a high level, the paper gives it and points to the note. No limitation a reader needs to read a result
  correctly leaves the paper.

## Not changed

- The ten recorded decisions, amendment 7 and the frozen records.
- Claims beyond this item; J3–J5 stay provisional.
- No outward act.
