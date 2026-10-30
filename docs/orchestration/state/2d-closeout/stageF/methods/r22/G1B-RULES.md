# r22 G1b — the paper diagnosis with one gap per passage: prompt, control and rules, fixed before any run

**Why.** The paper's planted control failed for both raters under G1 (REPORT.md §3): each folded the plants into one
"pattern" gap and quoted only one. The director ruled that G1b recovers the paper's resolution as a new, pre-declared
diagnosis, not a retry. **No text change.**

## 1. The prompt

`prompts/G1b.prompt.txt` (sha256 `a3d33594…`) is G1 with three changes, all in the question and answer format:
1. "Name every change that is needed" becomes "Name every passage that needs to change". It then adds: "List each
   passage as its own gap: where several passages share a problem, give each one its own entry with its own quote,
   rather than one entry for all of them."
2. "GAPS (at most 12, …)" becomes "GAPS (at most 20, the most important first, one passage each; …)".
3. SCOPE's only allowed value is "this passage".

Everything before "The question:" (the header, the references' description and P1's scale) is byte-identical to G1.
`tools/make_g1b_inputs.py` asserts this.

## 2. Inputs and the planted control

- `g1b/inputs/paper/`: G1's paper inputs, unchanged. The manuscript is sha256 `a945a490…`, byte-identical to G1's.
- `g1b/inputs/paper-ctl/`: the same, with the same three plants (`tools/plants.py`). They are placed by G1's rule (each
  on its own line, after the first line ending in a period at or past a fraction of the text) at new fractions: 12.5 %,
  37.5 % and 62.5 %, G1's 25/50/75 % moved back by one eighth.
  - The sites fall after lines 101, 344 and 671, against G1's 214, 558 and 1,092. The script asserts that no new site is
    within 100 lines of an old one.
  - The control is sha256 `23b2b259…`, 7,519 words.
- The script asserts that each plant occurs once in the control and never in the real input, and that the control
  minus its plant lines equals the real input. `g1b/INPUTS.SHA256SUMS` pins all eight files.

**Pass rule (unchanged from G1):** a control run passes when the rater quotes at least 2 of the 3 plants, counted by
`tools/parse_gaps.py`. If it fails, the real run is reported as "control failed, low power", and the director is told
before any classification.

## 3. Runs

Four runs, one each, through `register-method/tools/run_x.sh` (unchanged), by `tools/gapjob.sh` with
`GAP_SUB=g1b GAP_PAPER_PROMPT=prompts/G1b.prompt.txt`:
- the inputs are `paper` and `paper-ctl`;
- the raters are sol2 and gemini;
- each attempt has the 15-min timeout and one retry.

## 4. Classification and counting

- The rules are RULES.md §5 in the state after #521 and #522 (REPORT.md §4), applied by both classifications from
  `CLASSIFY-BRIEF.md`.
- The FROZEN reading is the director's (2026-10-29): the sentence may move or be consolidated, not reworded or
  replaced.
- Counting is RULES.md §5 for the paper's one run per rater. G1b's gaps are compared with G1's by quote, and both are
  reported.

## 5. What it feeds

The paper's Step 2 gap list is the G1b gaps that both classifications call WORDING or STRUCTURE (STEP2-PLAN.md §1). G1's
paper gaps are reported beside them.
