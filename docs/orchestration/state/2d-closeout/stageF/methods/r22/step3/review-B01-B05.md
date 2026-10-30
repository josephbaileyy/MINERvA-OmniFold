# r22 Step 3 review, pieces B01-B05 (two directions)

Reviewer: independent and read-only. Worktree `wt-con`, base `14a0415f`. I read the diffs
(`git diff 14a0415f -- docs/analysis-note/...`, run with `GIT_OPTIONAL_LOCKS=0`), the five briefs, the five ledgers,
`abstract-pairs.md`, both writer briefs, and the homes the ledgers name. I did not re-run the machine checks.

Files: B01 `sec_execsummary.tex` (`sec_intro.tex` is unchanged); B02 `sec_method.tex`, `selection_features.tex`
(`sec_experiment.tex` is unchanged); B03 `sec_systematics.tex`; B04 `sec_validation.tex`; B05 `sec_results.tex`.

**Counts:** 7 findings. LOST 1, WEAKENED 1, AMBIGUOUS 5, MOVED-AWAY 0, ADDED 0, BEYOND-NARROWED 0.
I also note 3 narrowed-form parts that were not made and 2 rule observations. None of these is a meaning defect.

## Findings

### F1 (LOST, medium-high): B02-g-01, `sec_method.tex` §"The exact-split cross-check"
- **Base:** "Its seed was not fixed: the driver version it ran had no seed option, and its production job script passed
  no seed. The run's own log was not found."
- **New:** "Its seed was not fixed, and its run log was not found; two driver revisions regenerate it to $7\times10^{-15}$."
- **Why:** The reason the seed was not fixed is gone from the note and from the records document. A grep of the printed
  note and the `records_*.tex` sources finds no "seed option" and no "passed no seed". Only "seed not fixed" survives,
  in `records_estimators.tex:11` and `sec_method.tex:130`. Two parts of the reason differ:
  - "its production job script passed no seed" is script mechanics. The narrowed form lets it move to the ledger.
  - "the driver version it ran had no seed option" is different. It is the cause of the limitation: the seed could not
    have been fixed by that run. It is not a detail of how the script ran.
  - The round-n2 director ruling (`note-n2/ledger.md` row ME-B1) kept exactly this clause: "(B) stays in the note;
    'its seed was not fixed' and the missing seed option kept".
  - The r22 narrowed form neither cites nor overrides that ruling. The source comment at `sec_method.tex:89-91` still
    says the reason is kept, so it now contradicts the text.
- **Fix:** restore the driver clause. Leave the job-script clause in the ledger. Suggested wording, still shorter than
  the base:
  "Its seed was not fixed, because the driver version it ran had no seed option, and its run log was not found; …".
  If the director rules instead that r22 supersedes n2, record that ruling and update the stale comment at :89-91.

### F2 (WEAKENED, medium): B04-g-01, `sec_validation.tex:152`
- **Base:** "Under this rule the primary undercoverage is attributed to the completeness term of the band. […] The band
  was then rebuilt without this term. The resulting undivided band was rescored only post hoc (below), and the quoted
  statistical block has not been tested."
- **New:** "Two bands were scored: the completeness-divided band above and, only post hoc (below), the undivided band.
  The quoted statistical block has not been tested for coverage."
- **Why:** The base told the reader that the undivided band was built after the attribution, by removing the very term
  the attribution blamed. The rule's undercoverage clause was itself written post hoc, as the held sentence B04-g-03
  says. That sequence is part of what makes the undivided band's rescoring post hoc and partly circular.
  - The ledger's `N:` home is the section opening: "The undivided band is the rebuilt band, without the division,
    since superseded." That sentence says the band was rebuilt. It does not say the rebuild followed the attribution or
    removed the attributed term.
  - The narrowed form asked for "a compact account identifying the tested bands, retaining … post hoc status". The
    bands and the post hoc status are kept. The rebuild fact now prints only by implication.
- **Fix (reword, about 4 words):** "… and, only post hoc (below), the undivided band, rebuilt without this term."
<!-- absence-ok: quotes printed note sentences, the raters' flags or the reviewers' findings; not a claim that something has not been run -->

### F3 (AMBIGUOUS, medium): B01-g-03, `sec_execsummary.tex`, 2D paragraph
- **Base:** "Whether it is ready for publication as a measurement has not been established."
  Here "it" is the unbinned 2D result.
- **New:** "The comparison is descriptive; the covariance lacks independent validation, validated coverage and
  calibrated significance (\S\ref{sec:uq-2d-scope}), and publication readiness as a measurement has not been
  established."
- **Why:** There are two problems.
  1. The readiness clause has lost its subject. It now follows "the comparison" and "the covariance", so it can be
     read as the readiness of the covariance or of the comparison. The phrase was also reordered: "publication
     readiness as a measurement" does not say "ready for publication as a measurement". Step 2's brief required
     "exactly that meaning" for this fact (B01-s-06).
  2. "the covariance" is unqualified. The executive summary's first paragraph introduced the sixteen-cell
     covariance, so a reader could take this as a statement about the principal result's covariance. The `\S` pointer
     resolves it only on the reader's click.
- **Strength is kept:** "has not been established" survives. The three validation gaps print at `sec:uq-2d-scope`.
- **Fix (reword):** "The comparison is descriptive; its covariance lacks independent validation, validated coverage and
  calibrated significance (\S\ref{sec:uq-2d-scope}), and its readiness for publication as a measurement has not been
  established." Optionally write "the 2D covariance".

### F4 (AMBIGUOUS, low): B04-g-10, `sec_validation.tex`, `fig:eff` caption
- **Base:** "Efficiency is diagnostic only; OmniFold's miss treatment natively corrects acceptance (\S\ref{sec:method-algo})."
- **New:** "…, shown as a diagnostic only; OmniFold's unmatched-event treatment corrects acceptance (\S\ref{sec:method-algo})."
- **Why:**
  - "Unmatched-event" is not a term the note defines. The note's term, at `sec:method-algo`, is "Truth events without
    a reconstructed partner (``misses'')", and "unmatched" prints nowhere in the note's sources.
  - "Unmatched" also covers reconstructed events without a truth partner (fakes). Fakes are handled by background
    subtraction, not by the acceptance treatment.
  - Dropping "natively" is acceptable. "Diagnostic only" plus `sec_method.tex` ("requires no separate efficiency
    correction") keep that fact.
  - The wording follows the reviewer's narrowed form, so this is a precision note, not a breach.
- **Fix (reword):** "OmniFold's treatment of misses (truth events without a reconstructed partner) corrects
  acceptance". Or keep "miss treatment".

### F5 (AMBIGUOUS, low): B03-g-10, `sec_systematics.tex`, new `tab:pl-added`
- **New:** header "& Increase in $\sigma$ & Share of variance"; caption "The run-period block added to the other blocks."
- **Why:**
  - The values and row labels match the base exactly (see the ruling below).
  - The base said which σ and which share: "raises the per-bin σ" of the total, and "carries … of the per-bin
    variance". The caption does not say that the first column is the relative increase of the total σ when the block
    is added, or that the second column is the block's share of the total variance. Read alone, "Share of variance"
    could mean a share of the block's own variance.
  - The prose sentence just above it ("Added to the other blocks, it raises the per-bin σ …") carries the meaning, but
    a float can drift away from it.
- **Fix (reword, no length cost):** header "Increase in total $\sigma$ & Block's share of total variance".

### F6 (AMBIGUOUS, low): B02-g-10, `sec_method.tex`
- **Base:** "The spread over seeds is unmeasured. The agreement of that median with the LightGBM seed-1 to seed-42
  median above is a coincidence."
- **New:** "The spread over seeds is unmeasured. This median agrees with the \SI{0.18}{\percent} LightGBM seed-1 to
  seed-42 median above, but the agreement is coincidental."
- **Why:**
  - The referent is two sentences back: the reseeded run's median, 0.18 %. "This" points at the immediately
    preceding sentence, which has no median. Base "that" had the same distance but read as anaphoric.
  - The added `\SI{0.18}{\percent}` prints twice above in the same subsection, so it is supported.
  - "Coincidental" keeps the strength of "a coincidence".
- **Fix (reword):** "The reseeded run's median agrees with …".
<!-- absence-ok: quotes printed note sentences, the raters' flags or the reviewers' findings; not a claim that something has not been run -->

### F7 (AMBIGUOUS, low): B05-g-05, `sec_results.tex` §uncertainty budget
- **Base:** "The public release does not let us determine the origin of this difference; our leading hypothesis is the
  FHC-only constraint file."
- **New:** "The public release cannot establish the origin of this difference, for which the FHC-only constraint file
  remains the leading, unconfirmed hypothesis."
- **Why:**
  - Strength is kept: the origin is unresolved and the hypothesis is tentative.
  - The hypothesis was the authors' ("our"). The impersonal "remains the leading … hypothesis" can read as an
    accepted or field-wide leading explanation with a history ("remains").
  - The narrowed form asked for exactly this wording, so it is within the allowed form. It is noted only because
    attribution is a new-to-old concern.
- **Fix (optional):** "… the leading, unconfirmed hypothesis of this analysis."

## Not made: narrowed-form parts left out (no meaning loss; for the director)

- **B01-g-02:** The narrowed form asks to "distinguish primary from recovered ensemble totals". The new sentence
  distinguishes the two qualitatively ("The decisions use completed pseudo-experiments; lost ones, recovered for
  reporting only, change none"). It gives no totals. The totals print in `sec:joint5d-lost` and in the `tab:joint5d`
  caption. The facts the summary dropped print there:
  - "every submitted draw has been observed";
  - the cause, time limits;
  - "for reporting only".
  The change is OK as made.
- **B01-g-03:** The narrowed form says "calibrated goodness-of-fit significance". The note prints "calibrated
  significance", which is broader. `sec_results.tex` ("not a calibrated goodness-of-fit test") and the held B03-g-02
  support it.
- **B05-g-04:** The narrowed form asks to retain that the scan "supplies no standalone calibrated goodness-of-fit
  test". The new text keeps the base content: the scan is attached to the earlier covariance, it was not repeated for
  the quoted one, and an unconstrained pseudo-inverse is not used as a goodness-of-fit test on its own. It does not add
  the "calibrated" clause. The `App.~\ref{sec:rank}` pointer moved from the whole sentence to the scan sentence. Both
  topics are in `sec:rank` (`app_statmethods.tex:474`, `:476`), so this is OK.

## Rule observations (not meaning)

- **Length:** `sec_systematics.tex` grew from 7296 to 7315 words (`wc -w`, base vs. worktree). That is the table
  markup. WRITER-BRIEF says "Do not lengthen your files overall." The printed word count is about neutral. The other
  files are equal or shorter: execsummary 1158→1158, method 4381→4368, selection_features 235→235, validation
  3586→3585, results 2179→2172.
- **Stale comment:** `sec_method.tex:89-91` (the n2 comment says the seed reason is kept) now contradicts the printed
  text. See F1.

## Rulings on the specific points in my range

- **B02-g-01: partly.**
  - The narrowed form ("move script mechanics to the internal ledger") allows the job-script clause to move.
  - It does not clearly allow the driver's missing seed option to move. That clause is the cause of the disclosed
    limitation, and the n2 director ruling kept it by name. Fix: F1.
  - The ledger home is adequate in content. `uncertainty-preparation-20261008/a/pairings.tsv` row P01, committed at
    `cc9eed270`, holds "driver has no backend/seed option; launcher sbatch_unfold_2d_MEHFC.sh passes neither" and
    "UNAVAILABLE (job log not found …)" for the same run (job 53116554).
  - That home is an internal TSV. It is not printed with the note or the records document, and B02's list names no
    specific home.
- **B05-g-08 (code as home for a presentation fact): OK for this case.**
  - The fact "the panels have no printed titles" is self-evident in the printed figure. I opened
    `figures/model_comp_ratio_maps.pdf`: two panels, colour bars, axis labels, no titles. The figure is the real home.
  - The code homes hold the fact as stated. `2d-unfolding/compare_to_models.py:22` imports `technote_style`, whose
    `set_title`/`suptitle` are no-ops (`technote_style.py:101-106`). The producer writes `{prefix}_ratio_maps.png`.
  - In general, code at HEAD is an adequate home only for a fact that the printed artifact itself displays, or a fact
    pinned to a sha. Code can change after the note is frozen. B07-g-03, a storage fact, is outside my range, so I do
    not rule on it.
- **B03-g-10 (six values): OK on values and labels; caption wording is F5.**
  - Per bin, median: 5.8 % and 10.6 % (base: "a median of 5.8 %", "a median 10.6 % of the per-bin variance").
  - Per bin, maximum: 39.1 % ("at most 39.1 %").
  - p∥ projections, maximum: 21 % ("by at most 21 %").
  - Integrated cross section: 9.9 % and 17.1 % ("the integral by 9.9 %", "17.1 % of the integral's").
  - The "---" cells have no base value, and none was invented.
  - No value is lost. The prose keeps the 5.8 % median and points to the table.
- **B01-g-03 ("has not been established" as a clause): kept at full strength, but needs the F3 rewording.** The
  validation-status clause is supported by `sec:uq-2d-scope` ("intervals, bias and covariance have not been
  independently validated"; "coverage … has not been validated"; "no calibrated significance").
- **B01-g-07 (abstract pair): OK as a proposal.**
  - `before` occurs exactly once in `main_note.tex`, and `main_note.tex` is unchanged in the worktree.
  - `after` is a pure reorder. The multiset of words is identical (57→57) apart from "A"/"a" and the ";"→"." at the
    old clause boundary.
  - Every macro and number is kept. "The coverage of the result's intervals has not been validated" is verbatim, as a
    standalone sentence. "but does not test interval widths" stays attached to the bias test, so the distinction
    between the bias test and interval-width validation is retained.
  - I recomputed the pin, sha256(before + NUL + after)[:16], as `6f0fb222b469a666`, matching the file.
  - Nothing moves toward the refused request: no limit is stated as a bounded uncertainty.
- **B04-g-01 ("Two bands were scored: …"): the rebuild fact is not printed as strongly. Fix: F2.**
  - The bands, the post hoc status of the rescoring and the untested quoted block are all kept.
  - "Tested for coverage" narrows the base's "tested", as the narrowed form asked.
  - The base's bare "has not been tested" overstated the case, because the quoted block has had another check: the
    nested-half (150-replica) stability check in `sec:uq-boot`. So the narrowing is accurate, not a weakening.
  - The gate phrases are untouched.
<!-- absence-ok: quotes printed note sentences, the raters' flags or the reviewers' findings; not a claim that something has not been run -->
