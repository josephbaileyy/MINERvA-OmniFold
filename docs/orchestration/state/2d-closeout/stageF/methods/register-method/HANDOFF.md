# Handoff: register revision rounds with calibrated outside raters

**For:** a future session asked to revise a paper or a long technical note until it reads like published work in its
genre, scored by outside models against published comparison papers.

**From:** the paper-tighten lane (Stage F), 2026-10-22, after running this method on the methods paper (rounds
r8–r14) and on the analysis note (batch 0, b3–b8, bhi, and the citation thinning).

**This is a method record.** It is not authority for any claim. The governing decisions are
`DECISION-20261021-joseph-register-loop-2.md`, `DECISION-20261021-joseph-da-and-note-records.md`,
`DECISION-20261022-joseph-mp2-gate-rules.md` (for a related calibration point) and
`DECISION-20261022-joseph-note-records-refs-and-stop.md`.

---

## 1. What worked and what did not

| finding | evidence |
|---|---|
| **An absolute 1–5 rating saturates.** sol gave 3.0 to almost everything near the target: the paper was 3.00 for five versions, and 24 of 28 note runs were 3.0. It cannot drive a loop by itself. | `METHODS-IMPLEMENTATION.md` §§16, 17, 19, 23 |
| **A blind pairwise comparison (new against previous) resolves what the rating cannot.** The paper's r12 and r13 each won 4/4; the note won 48/48 (12/12 pieces per model, p = 5e-4). It also detects regressions: r14 lost 1/4 and was not adopted. | §16, §19; `note-rating/P2N-pairwise-analyze.txt` |
| **Calibrate before setting a target.** Published PRD papers score 3.5–4.0 with sol on P1 (mean 3.67), and no published anchor exceeded 4.0 on any prompt. "Get to 4.5/5" was unreachable for published work. The calibrated target is the anchors' mean. | `rater-calibration/REPORT.md` |
| **Gemini's rewrites invent facts.** It called a 135 MeV effect "well below the experimental uncertainties" when its materiality is not established, called the note "private" or "informal", and called the analysis "unblinded". Never adopt a model rewrite without checking every fact in it. | §§12, 13, 16 |
| **Most of the improvement came from structure, not line edits.** Moving the records out of the note (Apps. G and J into an internal records document) gained more than any line-editing batch. The remaining internal-record tone came from citations pointing at those records; thinning them from 71 to 19 addressed that. | §§20, 23 |
| **Fresh writers rewriting from a one-sentence-per-paragraph outline beat sentence patching.** | r12 against r9–r11 |
| **Every round's independent two-direction review found real errors.** The guardrail-kept qualifiers are what the raters still flag at the end: that cost is the price of accuracy. Do not trade it for score. | §§15–22 |

**Stop rule that worked:** stop when the blind pairwise comparison no longer prefers the new version in both models,
or when the calibrated target is reached. Then hand the document to the human readers.

---

## 2. Accounts and safety

- **Raters run only through `tools/run_x.sh`** (in this directory):
  - `sol2` is gpt-6.1-sol through codex-school2;
  - `sol` is the same model through codex-school, which ran out of credits on 2026-10-21;
  - `gemini` is agy gemini-3.8-flash-high.
- **Never use the bare `codex` command.** In zsh it is aliased to a personal account.
- **Allowed delegation accounts:** codex-school2, codex-school, claude-school and agy only.
- **Before a long run:** smoke-test the route ("Reply with exactly: OK"), and check that the log says `model: gpt-6.1-sol`.
- **Sending text to the raters is the only outbound act.** Never post, upload, deposit or contact anyone.
- **Concurrency:** at most 3 rater runs per model at a time. The session usage limit is hit with about 4–5 parallel
  subagents. Resume stopped agents with SendMessage; their work survives.
- **Shared checkout:** never write to `/Users/josephbailey/local-research/MINERvA-OmniFold`. Use `git worktree add`
  under the scratchpad.
- **Committing:** explicit-path `git add` only, with the lane's identity on every commit.

---

## 3. The procedure

### Step 0. Calibrate once per genre (about 110 runs; one agent, about 1 hour)

1. **Pick anchors.** Pick 2–3 published papers of the same genre and length. Verify each arXiv id and journal-ref
   from the abs page, from the labelled "Journal reference" row. `cal/tools/absparse.py` once took a report number
   for the journal-ref.
2. **Blind every document the same way**, ours included (`rater-calibration/tools/blind.py`). Strip:
   - the title, authors, affiliations, date and journal headers;
   - DOIs and arXiv stamps;
   - acknowledgments and references.

   Keep the abstract, body, captions and data-availability text.
3. **Strip placeholders** (`[HOLD …]`) from rater copies with `rater-calibration/make_rater_copy.sh <worktree> <out.txt>`.
   - It builds the paper twice (normal, and holds rendering nothing).
   - It derives the rater text from the normal build minus the hold spans, because dropping a hold reflows the page.
   - It restores the data-availability heading order, blinds, and fails loudly on `??`, a surviving `HOLD`, or lost
     data-availability text.
4. **Run these prompts** (`rater-calibration/prompts/`):
   - **P1** (rubric-anchored absolute): 3 runs per document per model.
   - **P2** (blind pairwise A/B): both orders.
   - **P3** (flagged-sentence list): a source of flags for writers, not a metric.

   For long companion documents, use **P1N** and **P2N** (the framing is "one chapter of a long technical companion
   note"). Rate them chapter by chapter, in pieces of 3,000–8,000 words: `tools/note-pieces/split_note.py` and
   `heads.py`.
5. **Record:**
   - each anchor's mean score (the target);
   - the run-to-run sd (sol about 0.12–0.16);
   - the framing sensitivity;
   - whether the prompt resolves an old version from the current one.

### Step 1. Baseline

Rate the current document with the calibrated prompt. Cluster the quoted complaints (BOOK, HEDGE, JARG, HIST, CODE,
META, PROC, DENSE: `tools/note-pieces/clusters.py` and `labels.py`). Use them to plan batches, worst first, with the
summaries last, because they restate the body.

### Step 2. A glossary batch first, if jargon is spread across chapters

Fix one vocabulary for the whole document before chapter batches. Otherwise each batch renames terms differently.

### Step 3. Writer batches

- **Each batch gets a fresh writer** under `../WRITER-BRIEF.md`, adapted to the genre. Batches run in parallel only on
  disjoint files: no two writers edit the same file.
- **Writer method:**
  1. reverse-outline, one sentence per paragraph;
  2. a fact ledger with one probe per number, claim, limitation and disclosure, plus a checker in which a planted bad
     probe must fail;
  3. rewrite from the outline, results first, with scope inside the claim (not a trailing disclaimer);
  4. re-check every ledger row.
- **Binding rules:**
  - no fact leaves both documents;
  - a qualifier stays wherever leaving it out makes a printed sentence false as read (the guardrail);
  - protected text (holds, funding, acknowledgments, AI statement, data availability) stays byte-identical;
  - no label, section or subsection changes;
  - the companion document's text and label numbers stay unchanged.

### Step 4. An independent two-direction review per batch

The reviewer works under `../REVIEWER-BRIEF.md`, read-only, and builds its own inventory rather than trusting the
writer's ledger.
- **Direction A, nothing lost:** script a comparison of every number, and check that every cross-document pointer
  still lands on its fact.
- **Direction B, nothing strengthened:** check stronger verbs, lost scope, status changes and unsupported timing
  claims.
- **Fixes:** the writer fixes; for a substantial fix, the reviewer re-reviews.
- **Expect findings:** expect 1–4 blocking findings per batch. They are usually a strengthened claim or a fact that
  became unanchored.

### Step 5. Measure each round

- P1 with sol2, 3 runs, for the absolute score.
- P2, new against previous, both orders and both models, as the go/no-go: adopt if the new version wins at least 3 of
  4 with no order flip.
- Stop by the rule in §1.

---

## 4. Pitfalls met (and their fixes)

| pitfall | fix |
|---|---|
| zsh does not word-split `$var` (`git add -- $files`, job lists) | `git add --pathspec-from-file`; build job lists in bash |
| A pipe rewrites `$?` | Never pipe a command whose status you will read |
| biber returns code 2 (macOS ages out its PAR cache; parallel builds share it) | `PAR_GLOBAL_TMPDIR=<private dir>` for every build |
| `build_copy.sh` with a relative worktree path breaks the receipts symlink | Always pass an absolute path |
| GitHub stops updating a PR's head after a push (it shows the old sha as CONFLICTING) | Push the same commit to a fresh branch name and open a replacement PR; close the stale one with a pointer |
| MANIFEST.tsv conflicts on every rebase | `git checkout --ours docs/orchestration/MANIFEST.tsv`, then `generate_manifest.py`, then `git add` |
| Each new `.md` under `docs/orchestration` needs registering | Add a CATALOG.md row and a MANIFEST-overrides.tsv row; data files named in a JSON under `state/` trigger the receipt-artifact hook, so keep inventories beside their tool |
| The harness refuses subagents' REPORT.md writes | Ask for the report in the reply, and save it yourself |
| A truncated `sinfo` or status read leads to a false conclusion | Read the full output before stating a fact in a record |
| Subagent scheduler printed ALL-DONE early | Wait on the processes, not a scheduler's message |
| `swallowed_text.py` flags source comments that quote removed printed text | Paraphrase in comments |

---

## 5. Commands

```bash
S=<this session's scratchpad>
M=docs/orchestration/state/2d-closeout/stageF/methods

# one rater run (prompt, output, inputs)
XMODEL_DIR=$S/xmodel bash $M/register-method/tools/run_x.sh sol2 $M/rater-calibration/prompts/P1.prompt.txt out.md manuscript.txt

# a hold-free, blinded rater copy of the paper in a worktree
bash $M/rater-calibration/make_rater_copy.sh <abs-worktree> $S/xmodel/rN/inputs/paper.txt   # writes paper.blind.txt

# build all PDFs from a worktree (scratch copy), with a private biber cache
SCRATCH=$S PAR_GLOBAL_TMPDIR=$S/partmp bash $M/register-method/tools/build_copy.sh <name> <abs-worktree>

# the checks every batch must pass
python3 $M/register-method/tools/swallowed_text.py <worktree> origin/main   # flagged 0
(cd <worktree>/docs/analysis-note && python3 check_note_records.py probe records-inventory-base.json . \
   && python3 check_note_records.py --self-test records-inventory-base.json . && python3 check_note_records.py pin)
```

`tools/build_copy.sh` (run it with `SCRATCH=<scratch dir>`) and `tools/swallowed_text.py` are committed here.
- `build_copy.sh` rsyncs `docs/analysis-note` into a scratch repo layout, symlinks `docs/orchestration/state`, and
  runs `build_all.sh`;
- `swallowed_text.py` flags printed text that the diff turned into a LaTeX comment.

Several copied tools name the old scratchpad in a `C=` or `X=` line. Set it before use.

---

## 6. Files

**In this directory:**

| file | what |
|---|---|
| `tools/run_x.sh` | the rater wrapper (sol, sol2, gemini) |
| `tools/build_copy.sh`, `tools/swallowed_text.py` | the scratch build of all PDFs; the swallowed-text check |
| `tools/note-pieces/` | splitting a long document into blinded pieces; clustering quotes |
| `tools/pairwise/` | the pooled runner and the analysis for P2 and P2N |

**Elsewhere in `methods/`:**

| path | what |
|---|---|
| `rater-calibration/REPORT.md`, `NOTE-BASELINE.md` | the calibrations; prompts in `prompts/` (P0, P0n, P1, P1N, P2, P3) |
| `rater-calibration/make_rater_copy.sh`, `tools/` | rater copies, blinding, hold checks |
| `note-rating/` | the P1N re-rating table and the P2N pairwise result for the note; the P2N prompt |
| `WRITER-BRIEF.md`, `REVIEWER-BRIEF.md` | the shared briefs for chapter batches |
| `r12/`, `r13/`, `r14/`, `note-g0/`, `note-b3/` … `note-bhi/`, `note-thin/` | outlines, ledgers and checkers, changes and reviews for each round |
| `METHODS-IMPLEMENTATION.md` §§10–24 | the chronological record, with every score |

---

## 7. What stays the human's

- The target and the stopping rule. Propose both from the calibration.
- Any claim change.
- Protected text.
- Moving limitations out of the main document. Joseph allowed it with the guardrail, as a ruling.
- What the companion document may contain.
- Deposit, posting and release.
- The final read.
