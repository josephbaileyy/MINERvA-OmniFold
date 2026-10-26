# TeX reflow: one source line per paragraph and per comment block (2026-10-26)

**By** the paper-tighten lane, as director.

**Under** Joseph's request, `DECISION-20261026-joseph-fps-scope-r04-sensitivity-and-tex-reflow.md` §3 (PR #387): "it
is easiest to read the tex if the paragraphs and comments are all one line".

**Base:** main `6c320dae`, after note round n2 (PR #391).

**MEASURES:** that the reflow changes no typeset text, and which checks needed a change to stay meaningful.

**CANNOT AUTHORIZE:** any change of wording, number or claim. The reflow makes none.

## 1. What changed

- **The sources.** The 44 hand-written `docs/analysis-note/*.tex` sources go from 13,860 to 6,418 lines
  (`reflow.log`). Each prose paragraph is one line, and each run of full-line comments is one comment line.
- **Lines kept as they are:**
  - tables, alignments, displayed math, verbatim and pictures;
  - lines opening or closing an environment, sectioning commands, `\label`, `\input` and definitions;
  - lines ending in `\\`;
  - `\item`, `\caption` and `\paragraph`, which each start a line.

  The rules are in the docstring of `docs/analysis-note/reflow_tex.py`.
- **Generated files are untouched:** `records_results_index.tex`, `records_estimators.tex` and
  `records_entry_numbers.tex`. Their generators own them.
- **The records closure keeps every comment line in place.** That is `app_provenance`, `app_release_records`,
  `app_codebase_records`, `app_history` and `main_records`. `check_note_records.py` P5 splits record paragraphs at
  comment-only lines.
- **Elsewhere, a comment inside a paragraph moves** to the line after the paragraph's text. A trailing comment on a
  joined line moves the same way.
- **Line references in live TeX comments.** 38 references of the form `file.tex:N` were re-pointed through the reflow's
  line map (`remap.log`). 18 were left as they are, because their comment also cites a commit and so names a dated
  version.
  - Line citations in Markdown records stay as written. Each is dated by its commit.

## 2. Proof that the typeset text is unchanged

Every PDF was built with `build_all.sh` before and after, and its text extracted with `pdftotext`, both raw and with
`-layout` (`pdftext-digests.txt`, raw digests):

| document | before | after |
|---|---|---|
| main_note | `c95f3496e788db31` | `c95f3496e788db31` |
| main_paper | `63cd99e4c2cb1c29` | `63cd99e4c2cb1c29` |
| main_primer | `cfa2cc0e691f5b0e` | `cfa2cc0e691f5b0e` |
| pet_note | `4e06e12a97d3c0f7` | `4e06e12a97d3c0f7` |
| main_records | `abd7c6ae1da58283` | `4cd98b7b9b2494e8` |

The four posted documents are identical, layout text included. The records document differs only in numbers: every
differing hunk is equal once digits are masked. Those numbers are the registry's printed `file:line` citations, which
moved with the lines (§3).

## 3. Checks that depended on physical lines

The paper rewrite lane listed them, reading the code (2026-10-26).

1. **The registry (`check_registry.py` rule 1).** A citation is resolved by the digest of its whole line.
   - `recite_registry.py` re-cited the 29 rows whose cited line was joined (`recite.log`). For each, it took the
     pre-reflow line by digest, mapped it to its new line, checked that the quote is on that line and that the new
     digest is unique, and rewrote the line and digest. Nothing else in the row changed.
   - `results_index.py --write` ran twice, with staging between.
   - **Rule 7's citation granularity for prose is now a paragraph.** Its self-test planted a wrong-estimator case on
     the paper-label line, which is now a paragraph that also names configuration (e), so the case could not fail. The
     fixture now uses the paper-table line, which names configuration (a) alone, and fails as before. The same case in CI's registry fixture suite (`tools/registry/test_registry.py`, which is over the hook's time budget) was moved the same way. CI caught it on the first push, and the suite gives 28 tests OK.
2. **`check_note_records.py`.** Two self-test plants anchored on a newline, `"\n(Ref.~\cite{NoteRecords2026}, superseded
   values)."`. Both now anchor on its space form. probe PASS, `--self-test` 35 of 35 and 3 of 3, pin PASS,
   `--self-test-pin` 11 of 11, and `entry-numbers --check` PASS.
3. **`absence_claims.py` (rule 4).** A reflow changes every line of a paragraph, so every earlier absence claim would
   be judged as new.
   - **The TeX-only rule.** A `.tex` paragraph whose printed text a parent already printed, with no less support (its
     Search shas and waivers), is not re-judged. It counts as "reflowed" in the summary. 48 paragraphs are counted so
     here.
   - Markdown keeps the strict rule, so a re-wrap is still judged.
   - **New self-test cases:**
     - a joined, grandfathered bare claim is silent;
     - a reflow that also changes a word fires;
     - a reflow that drops the paragraph's Search line fires;
     - without the rule the same reflow fires;
     - a Markdown re-wrap still fires.
4. **The CI layout check.** `reflow_tex.py --note --check` is now a CI step (`record-checks.yml`, listed in
   `RECORDS-RULES.md`). A hard-wrapped paragraph in a note source fails it. It passes on this tree, and it fails when
   one source is put back hard-wrapped.

**Unaffected,** as the lane read them: SEC4-RECEIPTS, the round ledgers' sentence ids, R-EDIT digests, P9 and
entry-numbers, `check_dead_containment` and `check_body_pointers`.

**n2's round checker** (`note-n2/check_ledger.py`) now reports 7 PROTECTED files as changed. It requires the protected
files to be byte-identical to n2's base, so any later byte change fails it. Its 461 probes still pass. It is a closed
round's tool, and n3's base is this tree.

**At this tree:**
- `check_registry`, `absence_claims` and its self-test, `results_index` with `--self-test` and `--check --base`, and
  `verify_hash_bindings` all pass;
- the tree hook passes;
- pytest on `docs/analysis-note/` gives 97 passed.

## 4. A finding: 20 grandfathered absence claims

Rule 4 judges only added or changed lines, so absence claims printed before the rule are not checked. Judged under the
old rule, the reflow surfaced 20 of them in the note, paper and primer sources that carry no Search line and no waiver
(`grandfathered-absence-claims.txt`).
- That is the kind of sentence in which `sec_fps.tex`'s false "no extended-fiducial production … has been run" was
  found (`DECISION-20261026-joseph-fps-scope-r04-sensitivity-and-tex-reflow.md` §1).
- They are listed here for an audit by the paper rewrite lane. Each gets a real search, by meaning, and then either a
  Search line or a scoping waiver. A false one is fixed under the guardrail, or goes to Joseph if it is a claim.

## Files

- `reflow_tex.py`: the transform and its `--check`. It is committed at `docs/analysis-note/reflow_tex.py`.
- `remap_comment_refs.py` and `recite_registry.py`: the two one-shot repointing steps.
- `apply_reflow.sh`: the driver as run, from the director's scratch directory.
- `reflow.log`, `remap.log` and `recite.log`: every change those steps made.
- `pdftext-digests.txt`: the table in §2.
- `grandfathered-absence-claims.txt`: the list in §4.
