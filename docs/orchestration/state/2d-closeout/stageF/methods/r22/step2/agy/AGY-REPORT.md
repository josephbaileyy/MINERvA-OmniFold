# r22 Step 2, note round: the agy agreement check and its fixes (2026-10-30)

STEP2-PLAN.md requires agy agreement on every changed passage before the adoption runs. This file records the run,
its control, the triage of every flag, and the fixes made to the note as a result. The fixes are in the commit that
adds this file. They are applied before the adoption runs, so the adoption runs measure the fixed text.

## The run

- **Pairs.** 326 BEFORE/AFTER pairs cover every changed passage of the note, in 9 chunks
  (`chunkNN/pairs.txt`). Each pair is one passage of comment-stripped LaTeX, before and after the rewrite (base
  `9d3054f9`). They were built from the rewrite at `ee520a19`. That commit's only later source change, before this
  run, was waiver comment lines, which do not print.
- **Prompt.** `prompt.txt`. The rater sees each pair alone and is told to answer DIFFERS even when it suspects a fact
  has only moved to a neighbouring passage. A high flag rate is therefore expected, and every flag needs triage.
- **Rater.** gemini (agy) through `register-method/tools/run_x.sh`, launched by `r22/tools/agy_runs.sh` with a 900 s
  timeout and one retry. `status.tsv` lists every attempt. An rc=124 attempt timed out after it had already printed
  a complete answer ending in `END`. Every output file is complete.
- **Two runs.** Each chunk was rated twice: once on the real pairs (`agy-real.txt`) and once on a control copy
  (`pairs-control.txt`, `agy-control.txt`). The control copy has one negation removed from AFTER in three pairs (two
  in chunk09). `KEY.txt` names those pairs.

## The control

The control flagged every planted pair: 26 of 26, against a pass rule of at least 2 of 3 per chunk. Each DETAIL
quotes the removed negation. All 9 chunks pass.

## The flags

The real run and the control run each rate every pair, and the control run's planted pairs are excluded. A pair is
flagged when either run answers DIFFERS:

| real \ control | DIFFERS | SAME | missing | planted |
|---|---|---|---|---|
| DIFFERS | 139 | 30 | 1 | 17 |
| SAME | 4 | 123 | 1 | 9 |
| missing | 2 | | | |

That gives 193 flagged pairs (`differs.tsv`). Four pairs lack a verdict in one run: chunk03 Q27, chunk06 Q38,
chunk07 Q36 and chunk08 Q16. Each was rated in the other run, and the three of them that one run flagged are triaged.
<!-- absence-ok: counts verdicts missing from one rater output; each pair is rated in the other run -->

## Triage

Three read-only agents triaged the 193 flags with `TRIAGE-BRIEF.md`, checking each one against the base text, the
diff and the fact ledgers. Their results are in `triage-01-03.md`, `triage-04-05.md` and `triage-06-09.md`:

| class | count |
|---|---|
| MOVED-OK (the fact prints at a named place) | 73 |
| SUPPORTED (the base note states the "added" text) | 71 |
| RATER-WRONG | 27 |
| REAL | 22 |
| UNSURE | 0 |

The rule was strict: a word the base note does not state counts as REAL even when it is probably true.

## The REAL rows and their fixes

`apply_fixes.py` holds every substitution. Each old_str must occur once, and the fixes apply all or none. Summary:

- **Glosses written from general knowledge, removed or replaced by base wording.**
  - "single-pion" for Rvn1pi and Rvp1pi, at three places in sec_systematics.tex. SY118 was not flagged by agy;
    triage found it.
  - "neutral-current elastic" and "neutral-current resonant normalization" for EtaNCEL and NormNCRES.
  - $M_A^{\mathrm{RES}}$, $M_V^{\mathrm{RES}}$, $M_A^{\mathrm{CCQE}}$ for MaRES, MvRES, MaCCQE, in the prose and in
    Table tab:band-medians together.
  - "(the look-elsewhere effect)".
  - The edge-safe jitter definition now uses the base wording of app_statmethods_nd.tex ("fine-grid membership
    fixed").
  - "proxy significance" and "relative shift" in sec_joint.tex.
- **Populations narrowed.** "interaction-model" was added to the band sets: "Detector and interaction-model
  systematics" (the 44 bands include flux), and the unified throw's "all reweightable interaction-model bands" in
  sec_systematics.tex and sec_3d.tex. The base wording, or a neutral one, is restored.
- **Mechanism added.** "a cell set to one by the statistical-noise gate" for the 2D $C_{\mathrm{model}}$ became "a
  noise-gated cell".
- **Mislabel.** "the fixed metric $V$" became "$V$ fixed", twice. The metric is $\Sigma$, not $V$.
- **Ranking changed.** "holds the largest share" became "The largest cell, the corner ... holds 22%".
- **Subject changed.** "The analysis distinguishes" became "The companion journal article distinguishes". The
  file's comments say that this text moved from the article.
- **Facts or qualifiers lost, restored.**
  - "processed", together with "was extracted from" for Tune v1.
  - "and spread" in the coarser-cells disclaimer.
  - The non-claim "We therefore do not claim that our definition matches ``the published definition.''"
    <!-- absence-ok: quotes a printed non-claim of the note -->
- **Strength changed, restored.**
  - "recovers the feature" became "neither removes the injected feature nor creates a spurious one" (base: "neither
    manufactures nor destroys").
  - "We therefore attribute" became "This is direct evidence that".
  - "The reporting convention ... is to state" became "must state".
  - "That amplitude remains to be specified" became "should justify that amplitude".
  - "rather than inclusion in a non-closure error" became "would not be absorbed silently into a non-closure error".

## Two further sweeps, outside the agy flags

- **References.** A multiset comparison of every `\label`, `\ref`, `\pageref`, `\eqref` and `\cite` between the base
  and the new note files found the following losses.
  - The two `\pageref` calls in sec_summary.tex were dropped, against the writer brief's "keep every `\ref`". Both
    are restored.
  - `\ref{sec:intro}` (sec_execsummary.tex) and `\ref{sec:rank}` (app_statmethods.tex) left with sentences the
    ledger records as cut repetitions. B01-3 is the summary's scope sentence, which prints in sec:intro's Scope
    paragraph. B12-35 is a limitation bullet whose content prints in sec:rank and in limit (i) of sec:chisq.
  - The added references are cross-references. The one added `\cite`, the sec_results.tex comparison caption, names
    the published measurement that the caption already compared against.
- **The joint-test conditions** (sec_joint.tex). The base quoted the six conditions verbatim from the test
  specification and said so. The rewrite restates them in prose, and the verbatim text is in the records document
  (app_provenance.tex, entry joint-5d). The note now says they "are restated here in the terms of this note". A
  first version also cited the records entry, which the records-move gate refused (P7/P8: the note's citation of
  joint-5d is a listed drop), so the citation was removed.

## Gates after the fixes

- Fact ledger `check_ledger.py --no-n4-frozen`: 541 rows, 910 probes, 0 failures. `fix_ledger.py` carried the
  substitutions into the probes, and three probes flipped from X: to N:.
- RECORDS-MOVE PASS. The L-thin-C58 probe in records-move-ledger.md now follows the Rvp1pi wording.
- REFLOW PASS.
- build_all.sh PASS: SEC4 15/15, main_note.pdf 127 pages, no undefined reference or citation.
- Out-of-scope check: 67 quotes, 1 failure, the known B09-g-09 table renumbering exception.
- Words (pdftotext of main_note.pdf): base 64,925, new 64,965. split_base.py piece total: 56,329.

## Limits of this check

- agy sees one passage at a time, so it cannot see a meaning change that spans passages unless one side shows it.
- The triage was done by Claude agents in this lane, not by an independent rater. The 22 REAL rows were judged
  against quoted base text, which a reader can re-check from the triage files.
- Only flagged pairs were triaged. A meaning change in a pair that both runs rated SAME would not be caught here.
  The SY118 case shows that such changes can occur.
  <!-- absence-ok: states a limit of the method's coverage, not a result -->
