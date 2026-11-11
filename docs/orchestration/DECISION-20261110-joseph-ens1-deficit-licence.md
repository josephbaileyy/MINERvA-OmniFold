# DECISION 2026-11-10 — Joseph: the ENS1 OUTCOME's licence is amended so the paper may report the size of the ensemble average's one bias deficit, in one stated sentence

**Recorded by** the paper-tighten lane, as director.

## What led to it

- **The confirming round's Claude referee** (PR #1029, `referee-methods-confirm-20261110/claude.txt:108-109`, :172)
  asked for the magnitude of the ensemble average's one deficit.
- **The magnitude is committed:** `ens1_stage2.json` (sha256 `c2ee701d…`), key `bias.stage0c_gibuu`. The director
  re-measured it: the RMS excess is 0.000512 (0.056467 against 0.055955), 1.225 times the floor `delta_rms` 0.000418;
  the MAX excess is 0.000929, within the floor `delta_max` 0.001783.
- **The licence excluded it.** `OUTCOME-20261109-ens1-stab-pass-bias-worse.md`'s NOT CITABLE FOR excludes "Any use of
  the GiBUU bias magnitudes beyond 'no worse'" and "Any absolute statement about E₉₆'s bias". That goes further than
  FD-STAB §5.3 (`FD-STAB-DECLARATION.md:206-209`), which binds only the criteria: no decision may use a GiBUU bias
  magnitude. The licence note is `fd/tier2-20261110/T2C-ENS1-DEFICIT-LICENCE-NOTE.md` (PR #1032).
- **Joseph asked** whether the referee could still be asked:

  > can you ask that referee still or is its session over

  (sha256 of the text plus a final newline begins `af3e9fa368347b57`). The director resumed the referee's saved session
  (`407b8304…`) with a neutral follow-up giving both options. Its answer
  (`referee-methods-confirm-20261110/claude-followup-ens1.txt`) is that reporting the numbers answers its request, and
  that the verdict alone would leave it unmet: "That record limits which decisions and readings may be made. It does not
  forbid publishing measured values that are already labelled descriptive." It accepts no data run, and asks instead
  for two sentences: the ensemble was evaluated only on simulated pseudo-data, and the data result's instability is not
  mitigated.

## Joseph's answer, verbatim

> Amend, report it (Recommended)

(sha256 begins `bef5f0b0d7c06185`).

## What is decided

1. **The OUTCOME's CITABLE FOR gains one sentence,** and only that sentence:
   > At the one truth where it was worse (Stage 0c GiBUU), the ensemble average's RMS closure bias over the 16 cells
   > exceeded the reported estimator's by 0.000512 (0.056467 against 0.055955), 1.23 times the declared floor of
   > 0.000418; its maximum-bias excess, 0.000929, was within its floor of 0.001783.
2. **Every other exclusion stays:** that E₉₆ is a stabilised variant; that the instability is fixed; any statement
   about the real data; any reading of whether the excess is noise; any ranking beyond the verdict.
3. **The paper (#977)** may carry the sentence, its numbers from keys read from `ens1_stage2.json`, with the referee's
   two pseudo-data-only sentences, through the paper lane and a meaning read.
4. **The ensemble average on data** stays on the post-LL5D list. A data run is not a condition of this revision.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the amendment; the one sentence.
- **Not citable for:** any reading of noise or significance, any ranking, or any data statement.

Nothing is submitted, deposited or tagged.
