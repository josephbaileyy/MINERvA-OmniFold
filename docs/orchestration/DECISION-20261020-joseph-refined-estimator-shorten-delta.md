# DECISION 2026-10-20 — Joseph: refined estimator for the 3D–5D central values; shorten the paper into the note; Delta

**Recorded by** the paper-tighten lane, as director (Stage F). After the methods-paper rewrite merged (PR #190), the
director answered three questions from Joseph:
- **The central values.** Use the negative-weight refinement for the 3D–5D central values, the configuration whose
  nominal background-subtraction bias is smallest. That gives the one primary configuration both referees asked for.
  It removes only the background part of the bias, not the regularization part. Leave the adopted 2D result alone
  until a 2D closure check shows whether the refinement matters there.
- **Moving material to the note.** As much as possible, as the referees also advise. The paper must keep the
  definitions and every limitation that qualifies a headline result. Leaning on the note requires the note to be
  citable, and depositing it is Joseph's act.
- **Consensus.** The outside referees agree on substance.

Joseph's answer, verbatim:

> 1. go 2. do it. 3. agree. We also have delta access and you and any session you want can use it as much as you want

sha256 of the text plus a final newline begins `de50516f3a8fba34`.

## What is decided, as the director reads it

1. **Refined estimator (RE-1).** The higher-dimensional central values in the deliverables are regenerated with the
   refined configuration (e), with a 2D closure check of the refinement. The specification is
   [`state/2d-closeout/stageF/methods/RE1-SPEC.md`](state/2d-closeout/stageF/methods/RE1-SPEC.md), frozen before any
   run. Whether to change the adopted 2D result stays Joseph's decision, informed by the check.
2. **Shortening.** A pass moves detail from the paper into the note: tables, the hydrocarbon replays, the generative
   model, the appendix derivation, and most of Secs. VI and VIII. Every limitation that qualifies a headline result
   stays in the paper. Target: about 12 pages.
   - The note is to be made depositable, meaning complete, self-contained and with no internal-only pointers in
     printed text.
   - **Depositing it, or tagging or submitting anything, is not authorized by this decision and stays Joseph's
     explicit act.**
3. **Delta (NCSA, `bhvk`).** The director, and any session the director directs, may use Delta "as much as you want".
   - Measured 2026-10-20 19:27 CDT (`accounts`): bhvk-delta-cpu balance 1,480 h of 6,000, and bhvk-delta-gpu 640 h of
     1,000.
   - Access goes through Joseph's persistent ssh session (ControlPersist 12 h, Duo MFA). When it lapses, renewing it
     is Joseph's act.
   - The standing rules hold: each job under 12 h, ledgered, with grants through committed records.
   - Delta holds no MINERvA inputs. The analysis environment with ROOT is being checked; any use of Delta starts by
     copying inputs from NERSC and confirming that the environment reproduces a known product bitwise.

## Not changed

- J3–J5 are provisional until the review with Ben.
- No outward act.
- Claims stay Joseph's.
