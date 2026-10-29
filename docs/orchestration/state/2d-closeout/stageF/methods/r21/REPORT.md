# Round r21 on the paper: ADOPTED (2026-10-29)

**Governed by:**
- `DECISION-20261028-joseph-protections-remade-and-r21.md` item 5: one more scored round;
- the method, adoption and stop rules of `DECISION-20261025-joseph-register-rounds-paper-rewrite.md`;
- the director's rulings on `outline.md` (recorded there);
- the adoption rule, committed in `outline.md` at `b70156a1` before any r21 score.

**Written by** the paper rewrite lane, for the director, who merges. After r21 the paper's register rounds close
(item 5), whatever the score.

**Records** (this directory):
- `outline.md`, with the rulings and the adoption rule;
- `reverse-outline.md` and `fact-ledger.md`, from step 1, built by an independent read-only agent;
- `WRITER-BRIEF.md`;
- `writer/`: the four batches, their ledgers with `after`, the writer's notes and `check_batch.py`;
- `ledger.md` (the fact ledger with each row's `after` sentence) and `check_ledger.py`;
- `assemble.py`;
- `agy/`;
- `measure/base/` and `measure/new/`: the blinded copies, their digests and the rater outputs.

## The operation

A whole-text rewrite from a reverse outline and a fact ledger, by a writer with no history of the text (the
retrospective's §4 item 2). It is a single Opus 5.5 writer session (ruling 3), which never saw the base's prose. The
writer brief also carried the **APS mechanical conventions** the director added (ruling 1): numerals, the serial
comma, `Fig.`/`Sec.` forms, no splice of a result to its caveat, and hyphenated compound modifiers. **This round's
measured effect cannot be split between the rewrite and those conventions.**

**What the writer could not change:** the ledger's atoms quote the base's load-bearing wording exactly. The bound
phrases, the KEEP qualifiers, the FROZEN sentence and many ORDINARY facts are among them. So sentences built around
an atom often keep most of the base's words, and some APS deviations survive because an atom forces them: a missing
serial comma inside an atom, "neighbour", and small counts written as numerals. In Sec. V, about 13 places changed.

## Steps

0. **Baseline.** Main `78df7327`: blinded copy `d6138225…`, 7,384 words. P1 with sol2: **3, 3, 3**.
1. **Reverse outline and fact ledger,** by an independent read-only agent:
   - 6 sections and 48 paragraphs;
   - 373 rows over all 255 base sentences;
   - 640 atoms, each verified in its own base sentence;
   - the 8 phrases `check_sec4_receipts.py` binds, quoted in full;
   - one planted row.
2. **The writer, b1–b4,** with a fresh two-direction reviewer after each batch. Every BLOCKER and MAJOR is fixed:
   - **b1:** the III A envelope sentence had become a paper-wide definition of "the total interval" (BLOCKER), and
     "the same estimator's" was dropped (MAJOR). Eleven MINOR fixes.
   - **b2:**
     - the 74% sentence's population ("the result" could be read as the data result);
     - "below 0.3% in those cells";
     - the IV H order, which keeps "partial evidence and not independent" beside its cause;
     - Table II's preamble (MAJOR).
     Fourteen MINOR fixes.
   - **b3:** two MINOR fixes.
   - **b4:** the Limitations lead's "of these results". Also a MAJOR inherited from the base: the lead said every
     limitation is stated with its result in Secs. III–V, but the four low-stability cells (added in #492) are stated
     only in the Limitations. A truth-fix sentence now follows the lead: "The low stability of four of the sixteen
     cells is stated only here."
   - **The Limitations subsection is now a numbered list,** following R2, with every atom unchanged.
3. **Assembly** (`assemble.py`):
   - the batches are concatenated;
   - the five FIVED16 blocks are re-wrapped with the base's own marker lines, which three fived16 tools read;
   - each table's lines between its `\label` and `\begin{tabular}` are restored from the base. The ledger's table rows
     start at `\begin{tabular}`, so the writer never saw them;
   - the six absence claims get their Search lines back: the base's own line for the claim, or the note's line for the
     same claim;
   - `reflow_text` runs, as `reflow_tex.py --note` does. The base's per-number source comments are not carried; a
     header line points to them at `78df7327`.
4. **Gates:**
   - `check_ledger.py --require-after`: 373 rows, 0 failures. The checks:
     - every atom prints in its row's `after` sentence;
     - the planted row fails;
     - every base sentence is covered;
     - the bound phrases print once each;
     - no number the base does not print;
     - every label survives;
     - the title, the abstract and the acknowledgments-to-end span, Data Availability included, are byte-identical;
     - the `\pubhold` holds are unchanged.
   - Its self-test catches 7 plants and is silent on the base.
   - The registry: `ALIASES.tsv` rows 38 and 47 and `ATTRIBUTION.tsv` row 17 are re-cited to the new lines (52, 64),
     and `records_estimators.tex` is regenerated. The first registry run passed only because it ran before the new
     body was staged; on the staged body it failed as it should, and the re-cite fixed it.
   - SEC4 15/15; the values and Supplemental Material checks pass; reflow passes; absence-claims shows 0 bare claims.
   - `build_all.sh`: rc 0, paper 11 pp, no undefined reference.
   - agy (`agy/run1`, six section pairs, control 6 of 6): SAME on Secs. I–V in both runs. Sec. VI DIFFERS in both runs,
     only on the truth-fix sentence, which the base's (false) lead did not support. The sentence is true and stands.

## Measurement (the rule fixed in `outline.md`)

| | revision | blinded copy sha256 | words |
|---|---|---|---|
| OLD | main `78df7327` | `d6138225fd83f7f9…` | 7,384 |
| NEW | `43ef36a0` | `a945a490871f7dd4…` | 7,465 |

| model | order | winner | strength |
|---|---|---|---|
| sol2 | A = OLD, B = NEW | B (NEW) | 1 |
| sol2 | A = NEW, B = OLD | A (NEW) | 1 |
| gemini | A = OLD, B = NEW | B (NEW) | 2 |
| gemini | A = NEW, B = OLD | A (NEW) | 3 |

- **P1, sol2, three runs:** NEW 3, 3, 3, against the base's 3, 3, 3. All five sol2 runs logged `gpt-6.1-sol`.
- **Adoption:** **ADOPTED.** All three conditions hold:
  - NEW wins 4 of 4 (the rule asks for at least 3);
  - sol2 picks NEW in both orders, so there is no flip;
  - P1's mean (3.00) and minimum (3) are each at least the base's.

**The raters' reasons:**
- **sol2:** NEW "more often divides overloaded sentences into manageable units", "clarifies referents", and has
  "explicit subjects and referents". It also avoids the base's "the bias is listed at".
- **gemini:** NEW has formal diction where the base was colloquial ("times", "puts", "which is what makes"). It fixes a
  comma splice and a dangling modifier, defines "the support rule" before using it, enumerates the Limitations, and
  opens no sentence with a symbol.

**What P1 quotes (all three runs), for Joseph's read:**
- the Limitations lead with the truth-fix sentence;
- "The note's calibrated tests show the same pull: …";
- the Data Availability package sentence, which is out of r21 by ruling 2.

P1 stays at 3, as in 39 of 39 earlier runs. The retrospective expected that, and the pairwise is where r21 won.

## What follows

- The paper's register rounds are closed (item 5). The paper goes to Joseph's and Ben's read.
- The paper-protections ledger (`../paper-protections/check_ledger.py`) is a record of #492, pinned to its base; it
  does not hold at r21's head, as r19's did not after r20.
