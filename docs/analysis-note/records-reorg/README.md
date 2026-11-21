# Records reorganization (`records_reorg.py`)

This is the handoff for the reorganization of the records document (`main_records.tex`), branch
`records/reorg-20261121`. The plan, its rulings and its report live outside the repository, in
`~/codex-reports/note-measurement/records-reorg-plan/` (PLAN.md, DROPPED.md).

## What it does

The records files that hold text moved out of the note (`app_compression_records.tex` and the seven
`records_compression_*.tex`, including helper-3's `h3_rw`) were organized by the lane that moved them, mostly one heading per moved sentence.
`records_reorg.py` cuts them into blocks (one per heading, each with its `%` comment lines), routes every block to a
table of contents that follows the note, and writes one file per section:

- Part I, R1-R10: `records_r01_intro.tex` ... `records_r10_reproducibility.tex`, for the note's Sections 1-6 and
  Appendices A-D. The section headings are printed by `main_records.tex` between `% RECORDS-REORG BEGIN/END`, so that
  `check_note_records.py`'s count of `\section` before `app_provenance` stays right.
- Part II, R11-R14: `app_provenance`, `app_history`, `app_verification` and the generated estimator registry and
  results index, unchanged. `app_release_records` and `app_codebase_records` are input whole in R10. These six file
  names are pinned by `check_note_records.py` and are never edited here.

## Phases (each its own commit)

| Phase | `--phase` | What changes |
|---|---|---|
| B | `B` | Mechanical move. Each block keeps its old heading, as a run-in `\paragraph`. |
| C | `C` | Blocks from the same note paragraph become one paragraph under a run-in title (`titles.tsv`). Lead-ins are demoted to comments (Option B, Joseph 2026-11-21), both forms, unless they hold a register re-anchor or the next sentence would dangle (Option B', `keep-leadin-context.tsv`). The lane preambles in `demote.tsv` are demoted. |
| D | `D` | Duplicate resolution (Joseph 2026-11-21): `drops.tsv` (copies not printed), `cuts.tsv` (repeated sentences not printed), `carries.tsv` (a sentence only the dropped copy had, carried verbatim). |

Nothing is deleted from the sources: whatever stops printing stays as a `%` comment beside its text.

## Commands (from `docs/analysis-note`)

```
python3 records_reorg.py --self-test
python3 records_reorg.py inventory --out /tmp/inv.tsv            # every block, its source and destination
python3 records_reorg.py assemble --phase D --rev BASE --out-dir .  # writes R1-R10, main_records.tex, the move manifest
git rm app_compression_records.tex records_compression_*.tex
python3 records_reorg.py check --phase D --base BASE             # the invariance gate (must PASS)
python3 records_reorg.py rekey --write --base BASE               # limitations-export.tsv reanchor_file, ledger R: probes,
                                                                 # registry source columns (all bookkeeping; the checks
                                                                 # that need them are file-keyed or cite file:line)
(cd ../.. && git add -A docs/analysis-note docs/orchestration/registry \
  && python3 tools/registry/check_registry.py --repoint \
  && git add -A docs/orchestration/registry && python3 tools/registry/results_index.py --write \
  && git add -A docs/analysis-note docs/orchestration/registry)   # repoint and the generator read the INDEX: stage first
python3 check_note_records.py entry-numbers .                     # provenance entries become R11.n
python3 records_reorg.py dropped --phase D --base BASE --out <path>/DROPPED.md
```

`assemble` always reads the moved files from `--rev BASE` (git), so it can be re-run after the files are removed.
Then build `main_note` and `main_records` (`latexmk -g -pdf`), and run `limitations_export.py --check` and
`check_note_records.py probe records-inventory-base.json .`. The probe already fails at the base (the rewrite's new
note structure, to be rewired at the end of the check stage); done for this branch means its failure set is
identical to the base's.

## Landed

Base `ab0596ac3` (rewrite/journal-voice-20261121), merged at `fc13d84cc`; phase B `a9f23dfaa`, C `b3882a810`,
D `26cb6d4f2`. Each phase commit passed: `check` against the base, `limitations_export.py --check` (90 rows), the
probe failure set identical to the base's, pin, entry numbers (`--check`, `--check-aux`), and main_note / main_records
builds with 0 errors, 0 undefined, 0 multiply defined, no `??` (main_records 168 -> 145 -> 144 pp; 195 at the base,
whose results index is no longer in the comparison because it is generated).

Joseph's rulings on the three flags (2026-11-21, via the rewrite helper and the director), branch
`records/flags-20261121`: (a) n21 and n33 print once, in R6.2; their R3 copies, lead-ins kept printed only because
they held the re-anchors, are demoted (`demote-leadin.tsv`); (b) the extended-fiducial study has one heading, R4.8
(`toc.tsv`; `sec_fps.tex`'s own `\subsection` is a comment, its `\label{sec:fps}` kept); (c) n01 and n03 keep their
text in R6.2, each followed by "Retired (Joseph, 2026-11-21, DECISION-20261121a)." (`inserts.tsv`).

## The invariance gate

`check --base` compares the printed lines (comments, heading commands, `\label` and `\input` removed; whitespace
collapsed) of the whole records closure at the base with the working tree, leaving out the generated files
(`records_entry_numbers.tex`, `records_results_index.tex`, `records_estimators.tex`, `records_earlier_labels.tex`). Every base line must still print, or be
declared (drop, demote, lead-in, cut) and then appear as a comment. Every new printed line must be declared
(`adds.tsv`, `carries.tsv`). Every base comment line must survive. Every register re-anchor that printed must still
print. A re-wrapped line fails, because it is one lost line and one new line. Headings are not compared: run-in
titles are new text by design.

## Data (`records-reorg/`)

| File | Rows |
|---|---|
| `toc.tsv` | the table of contents (part, section, subsection; a `-` subsection prints no heading; `inputs` names whole files) |
| `rules.tsv` | routing rules, first match wins; a block no rule matches inherits its parent's destination |
| `splits.tsv` | anchors that split one block into paragraphs placed apart (`<key>#n`) |
| `titles.tsv` | run-in title and order of each paragraph group, keyed by its first block. Titles of the one-sentence moves were drafted by a claude-school delegate (Opus, high effort) from the paragraph text only, and checked against format rules; the R7.5 order and the split-part titles are the orchestrator's. `-` means the group continues the previous paragraph. |
| `demote.tsv` | blocks printed as comments (the seven lane preambles) |
| `drops.tsv`, `cuts.tsv`, `carries.tsv` | the duplicate resolution, listed for Joseph in DROPPED.md |
| `adds.tsv`, `opening.tex` | the new opening paragraph of `main_records.tex` |
| `demote-leadin.tsv`, `inserts.tsv` | Joseph's rulings on the reorganized records (see Landed) |
| `keep-leadin.tsv` | the five register rows whose re-anchor lies inside a lead-in (documentation; the test is the text itself) |
| `keep-leadin-context.tsv` | Option B' (Joseph, 2026-11-21): the 42 lead-ins whose following sentence opens with an anaphor ("These are...", "It moves...") stay printed. `assemble` warns about any further such lead-in at a new base |

Block keys are content hashes (file, heading line, first printed line), so the data survives a change of base unless
the named block itself changes; `assemble` stops on any key it cannot find.
