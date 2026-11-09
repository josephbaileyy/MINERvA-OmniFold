# The fifth methods-draft referee round, PRD and JINST, paper plus Supplemental Material, 2026-11-09

**What was read.** `draft/methods-round5-20261108` at `bc8673186ba945460dfee4e4ee78ec1012ec9174`. It is unmerged, and no
wording is approved. Round 5 brings in the records landed since round 4 (per-period 2D benchmark, COV2D under-covers at
both tunes, RS1's rounding mechanism, the 1B pre-check Part 1, the staged 1B receipt stop, the valid-region readings),
the new Supplemental Material, and ENS1's result from `OUTCOME-20261109-ens1-stab-pass-bias-worse.md` (the two
placeholders are filled through new `make_values_fived16.py` keys `ens1-*`, pinned to `ens1_stage1.json` `7f5a9ce4` and
`ens1_stage2.json` `c2ee701d`).

**The rater copies**, built at that commit by the committed scripts:
- `manuscript-methods-r5.blind.txt` (`make_rater_copy.sh`, rc 0): 12,701 words, sha256 `7470a0e93e36ee7c…`; Tables I–VII
  and Figs. 1–4 present; no `[HOLD`, no placeholder;
- `supplement-methods-r5.blind.txt` (`make_supp_rater_copy.sh`, rc 0): 10,143 words, sha256 `85da3867fad44da5…`;
  6 of 6 table captions; sections S1–S9.

**Procedure.** As round 4 (`../referee-methods-round4-20261106/README.md`), with two changes:
1. **The Supplement is included.** Each input is the prompt, the paper's blind copy, a line `SUPPLEMENTAL MATERIAL`,
   then the Supplement's blind copy. The prompts are round 4's, with one sentence replaced: "It cites a companion
   analysis note as Ref. [14]; you do not have it." becomes "The manuscript's Supplemental Material follows the
   manuscript; you have it. It cites a companion analysis note as Ref. [14]; you do not have it."
   (`referee-prompt-prd-r5.txt`, from `referee-framing-comparison-20261106/referee-prompt-neutral.txt`;
   `referee-prompt-jinst-r5.txt`, from `referee-jinst-test-20261106/referee-prompt-jinst.txt`). **So round 5 is not
   strictly comparable with rounds 1–4.**
2. **How Sonnet was run.** Round 4 used read-only subagents. Here each Sonnet read is a separate `claude -p --model
   sonnet --strict-mcp-config --tools "" --disable-slash-commands` call, with the whole input on stdin, from an empty
   directory that was still empty afterwards. The reader had no tools at all and saw only the input. All four exited 0
   with empty stderr.

Gemini via agy as before (`gemini-3.8-flash-high`, `--sandbox`), from an empty directory that was still empty
afterwards, each input prefixed with `gemini-preamble.txt`; all four exited 0 with empty stderr.

**Did each read reach the end?** Sonnet received the whole input on stdin; two of its reports cite S9, the Supplement's
last section. No Gemini report claims the input was cut short, and they cite the Supplement up to S7; none cites S8 or
S9 by number, so the director cannot confirm from the reports that Gemini read to the end.

## Scores

| draft | PRD: Sonnet | PRD: Gemini | PRD mean | JINST: Sonnet | JINST: Gemini | JINST mean |
|---|---|---|---|---|---|---|
| **round 5** (`bc867318`, with the Supplement) | 4, 3 | 3, 5 | **3.75** | 3, 3 | 5, 5 | **4.0** |
| round 4 (`33cdc4e5`) | 3, 4 | 3, 4 | 3.5 | 4, 4 | 5, 4 | 4.25 |
| round 2 (`0de103f7`) | 3, 4 | 3, 3 | 3.25 | 4, 4 | 5, 5 | 4.5 |
| round 1 (`09ef9ebb`) | 4, 4 | 4, 4 | 4.0 | — | — | — |

Every read in this round recommends major revision. The changes from round 4 are within the spread between repeat
reads.

## What the reads agree on

These are the referees' findings, not verified facts.
1. **The rounding instability is unresolved** (all eight). Several read it as a defect of the estimator, not a reported
   limitation. One Gemini PRD read calls it "retention of a numerically fragile estimator over a working alternative",
   reading ENS1's stability pass as a reason to adopt it; the paper's reason for not adopting (the bias criterion at one
   truth) does not persuade it.
2. **Coverage is not validated and the five-observable coverage test did not run** (all eight).
   <!-- absence-ok: reporting what the referees wrote, not a claim by this record that a result does not exist -->
3. **The run-period block is ad hoc or circular** (all eight): the period difference is unexplained and absorbed by a
   data-driven term.
4. **The 2D benchmark does not validate the method** (all eight): the shape difference is unexplained, and the
   estimator choices were made with the published distance known.
5. **Prior retention is the central finding and is not resolved or isolated** (all four Sonnet reads, two Gemini).

Also raised: redundancy among the five observables (W is fixed by p_T, p_∥ and q_3; four reads); that printing the
illustrative sixteen-cell output and generator χ² is hazardous (three Gemini reads); dependence on Ref. [14] (one).

**CITABLE FOR:** these referees' reports on the round-5 rater copies (paper and Supplement), and the scores they gave.

**NOT CITABLE FOR:** any physics claim, any venue decision, a comparison with rounds 1–4 beyond the noted change of
inputs, or approval of any wording.

Nothing is submitted, deposited or tagged.
