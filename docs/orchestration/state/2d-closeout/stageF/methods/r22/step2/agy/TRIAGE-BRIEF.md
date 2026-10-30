# r22 Step 2: triage of the agy agreement flags

A register rewrite of a physics analysis note (LaTeX) was checked passage by passage by a rater (gemini) that saw only
each passage's BEFORE and AFTER. The rater was told to answer DIFFERS even when it suspected a fact had only moved to a
neighbouring passage. Two independent runs were made (`real` and `control`; the control run is the same pairs with
three planted negations per chunk, which it caught 26 of 26). Your job: for each flagged passage in your range, decide
whether the rewrite really changed what the note says.

Paths:
- `A=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/4834bf2d-a370-41b8-ae11-7b9d48874031/scratchpad/r22/step2/agy`
- `$A/differs.tsv`: one row per flagged passage, tab-separated: chunk, Q, `file tag`, real verdict, control verdict
  (PLANT = that pair was planted in the control run; ignore its control verdict), real DETAIL, control DETAIL.
- `$A/chunkNN/pairs.txt`: the BEFORE and AFTER text of each Q (comment-stripped LaTeX).
- `WT=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/796e7ecc-51d8-4fd5-a926-09de706955fd/scratchpad/wt-con`:
  the repository worktree with the rewrite. Base commit `9d3054f9`. See a file's change with
  `git -C $WT diff 9d3054f9 -- docs/analysis-note/<file>`.
- The writers' rules: `$A/../WRITER-BRIEF.md`. The fact ledgers: `$A/../ledger-Bxx.md` (each changed fact and where it
  now prints; probes `N:` note file, `R:` records file, `L:` repository file).

## Classify each flagged row as one of

- **MOVED-OK:** every fact, number and qualifier the DETAIL says is missing still prints in the note (or at its ledger
  home), and any qualifier is still attached to the claim it qualifies. Give the file and a short quote where it now
  prints; verify by `grep` in `$WT/docs/analysis-note/`.
- **SUPPORTED:** text the DETAIL calls an addition is stated in the BEFORE text of a neighbouring passage of the same
  file, or elsewhere in the base note (`git -C $WT show 9d3054f9:docs/analysis-note/<file>`). Quote the base source.
- **RATER-WRONG:** the DETAIL misreads the pair (e.g. the words it quotes are in both). Say why in one line.
- **REAL:** the rewrite lost, weakened, detached or overstated a fact, qualifier, limitation or disclosure, or added a
  fact, definition, gloss, cause or claim that the base note does not state. Quote base and new text and propose the
  minimal fix (normally: restore the base wording for that clause). A gloss or definition written from general
  knowledge, not stated in the base note, is REAL.
- **UNSURE:** you cannot decide; say what would decide it.

Be strict in the direction of REAL: when the base note does not support an added word, it is REAL, even if the word is
probably true. Wording-only changes (splitting, reordering, replacing an internal label by a term the base defines) are
not REAL.

## Rules

- Read-only. Write only your output file `$A/triage-<range>.md`. No git command that writes, no build, no model, CLI
  or network call.
- Output: one markdown table `| chunk | Q | file tag | class | evidence | fix |`, one row per flagged row in your range,
  in order; then a list of the REAL rows with the exact base and new text and the fix, as an old_str/new_str pair on the
  current file in `$WT` where you can (old_str must occur exactly once in the current file).
- Report back in under 200 words: counts per class, and each REAL row in one line.
