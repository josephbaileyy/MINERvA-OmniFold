# Review: batch "thin" (records-citation thinning)

**Reviewer:** independent and read-only. I made no edits in any worktree. The only things I wrote were this file and
`S/review-thin/plant.py`, my plant harness.
**Before:** `563715b8`. Note sources are byte-identical at origin/main `e0180c60`: `git diff --stat HEAD origin/main --
docs/analysis-note/` is empty.
**After:** the uncommitted tree in `S/wt-thin`, 16 files.
**Authority:** `docs/orchestration/DECISION-20261022-joseph-note-records-refs-and-stop.md`.

## Verdict: ADOPT-AFTER-FIXES

- No BLOCKING finding:
  - no fact or number is lost;
  - no claim is strengthened;
  - no paper pointer is broken;
  - protected text is intact;
  - the paper text and the label numbers are unchanged.
- Four SHOULD-FIX items:
  - S1: the probe prints PASS when its P8 is skipped;
  - S2: C07 should stay;
  - S3: the guide no longer explains tags;
  - S4: README:137.
- Two consistency items: S5 (C71) and S6 (an un-probed KEEP position).

---

## 1. The six whole-text removals: each record is printed at the cited heading or tag (verified at HEAD)

I confirmed that the records sources are unchanged: `git diff --quiet HEAD -- app_history.tex app_provenance.tex
app_release_records.tex app_codebase_records.tex main_records.tex technote.bib`.

| id | removed text | where the records print it (HEAD) | ok |
|---|---|---|---|
| C14 | "The supporting internal records, including the checksums of the fixed identities, are kept in Ref.~\cite{NoteRecords2026}." | `app_release_records.tex:6` "Identities already fixed" (the digest table). The pointer survives in the same appendix as C15 (`app_release.tex:125`, "checksums: Ref.~…, identities already fixed"). | yes |
| C24 | "its closure, its data-only stream and its structure comparison are given in Ref.~…, superseded values: retired material" | `app_history.tex:324` "The VL175 construction: retired material", items (i) closure 1.07/0.95, (ii) data stream 0.356, (iii) structure 0.108/0.46/0.009/76.7 | yes |
| C49 | "The earlier direct 42-bin $(\Eavail,W)$ block sum is superseded and quoted nowhere in this note (…)" | `app_history.tex:498` "The earlier direct $(\Eavail,W)$ block sum": "This subsection is historical … superseded construction" and "It is not adopted and is not quoted anywhere in this note." No posted sentence still refers to the block sum or to a "replacement": a grep of `sec_5d.tex` and `sec_eavailw.tex` finds none. | yes |
| C59 | "The earlier budget's values without the constraint weights and with the CV $\Phi$ are in Ref.~…, superseded values: retired material." | `app_history.tex:404` "Other VL175-era values": "the Flux band was 4.99% without MAT's constraint weights, against ~1% when all universes used the CV Φ" | yes |
| C60 | "The split data/MC streams of that earlier, rebuilt bootstrap are in Ref.~…, superseded values: retired material, and \texttt{coverage-fixed-truth}." | The split streams are in `app_history.tex:348` (VL170 bootstrap, split-bootstrap paragraph). The band identities (VL162 scored, superseded by VL170) are in `app_provenance.tex`, the `coverage-fixed-truth` item. | yes |
| C56 | roadmap row "Provenance of records, fixed identities, superseded values and withdrawn arguments & internal records, Ref.~…" | Replaced by the guide statement C01, which names every category of the row. | yes |

All 24 tags that are dropped or kept are defined in `app_provenance.tex` at HEAD.

## 2. KEEP and DROP judgments

- I read the context of all 17 KEEPs, all 54 DROPs and the 4 shortened KEEPs.
- All 17 KEEPs are justified: each sits on a number or claim that only the record lets a reader check. I propose no
  KEEP→DROP.
- C66: see Q3.

### S2 (SHOULD-FIX): C07 should be a KEEP

`app_negweight.tex:282`.

- Before: "Purity is \textbf{a recorded choice, not a silent default} (Ref.~\cite{NoteRecords2026},
  \texttt{gbdt-closeout} and \texttt{oi6-oi8-oi126}), made on two grounds."
- After: "Purity is \textbf{a recorded choice, not a silent default}, made on two grounds."

The writer's reason was "decision records (who decided when)". But the paragraph makes claims about the decision
itself, and only those records can check them:
- that the choice is *recorded*;
- "This consequence, not the computing cost, decided the choice";
- the open obligation to revisit.

The `oi6-oi8-oi126` entry is what prints "answered in favour of purity on 2026-08-07 … and again, after the
alternative was costed, on 2026-08-15". Without the citation, "recorded" points nowhere. That is exactly Joseph's
keep criterion.

**Fix:** restore `(Ref.~\cite{NoteRecords2026}, \texttt{oi6-oi8-oi126})`. The `gbdt-closeout` tag can stay dropped,
because the `oi6` entry cites it. Remove the `D:…oi6-oi8-oi126` probe from L-thin-C07. The count becomes 18.

### S5 (SHOULD-FIX, consistency): C71

`sec_validation.tex:335`.

- Before: "An earlier ensemble of $N_{\text{toy}}=200$ 2D closure unfolds (Ref.~\cite{NoteRecords2026},
  \texttt{coverage-toys})"
- After: the citation is gone.

The writer called this "launcher and rollup paths only". But `coverage-toys` also names
`uq/coverage/coverage_summary.txt`, the only source of the numbers printed two sentences later:
- 68.50% median;
- +0.006 ± 0.082σ;
- 97.6%;
- 5 of 205.

C64 was kept on exactly this ground ("prints the numbers of an exact test … whose record is the only source").

**Fix:** keep C71 for consistency, or record that the diagnostic is explicitly "not a coverage test", so its numbers
need no record. This is Joseph's call. It is not a loss, since the path is still in the source comment.

### Acceptable drops (NIT, no action)

- C06 and C10 (`bkg-mode-pins`) back claims about code behaviour. Dropping them is consistent with the other
  code-pointer drops (C03, C18, C28).
- C52 ("exactly symmetric"): the writer's reason, "checkable from the released file", is weak, because the release is
  not deposited. But C47's identity table prints max|C−Cᵀ|=0, and C47 cites it in the same subsection.

### No DROP leaves a printed number uncheckable

Apart from C71 above, every DROP carrying a number points to a different, superseded value, not to the number
printed:
- C20 2.137%;
- C25 1431;
- C26 0.1707–0.2371 (J36 does not print the range);
- C33 −7.2→−2.6%;
- C34 1.09.

## 3. The guide statement (C01)

`app_guide.tex:18-20`, after: "Provenance, the fixed identities and audit record of the five-axis covariance, the
test-suite discipline, and superseded values and withdrawn results are kept in the analysis repository's records
document, Ref.~\cite{NoteRecords2026}."

- It is said once and in the right place. It is the only records statement in the posted closure (grep:
  1 hit), and it matches the bib title.

### S3 (SHOULD-FIX): the guide no longer says that citations name a tag or a heading

The writer dropped "the note cites its entries by tag or by heading". The 16 remaining citations print as
"Ref. [41], negweight-hpss" or "Ref. [41], superseded values: retired material". No sentence of the note now tells
the reader what the trailing words are.

**Fix:** end the sentence "…, Ref.~\cite{NoteRecords2026}; each citation names the entry's tag or heading."

### NIT: "Provenance" lost its object

- Before: "the provenance of the repository records it cites".
- After: bare "Provenance,". This reads as if all provenance is outside the note.

**Fix:** "The provenance of the records the note cites, …".

## 4. The amended checker (`check_note_records.py`)

I ran everything from `/tmp` with `python3 -B`, so no bytecode was written.

| run | result |
|---|---|
| `probe records-inventory-base.json <wt>/docs/analysis-note` | `RECORDS-MOVE :: PASS (… thinning: 76 citation keys at 563715b8, 17 now, 59 listed drops, targets checked in the tree and at HEAD; 0 failure(s))`, rc 0 |
| `--self-test` (canonical checkout) | `RECORDS-MOVE SELF-TEST :: PASS (delivered move silent: True; 20 of 20 planted defects fired their probe; 2 of 2 listed drops stayed silent)`, rc 0 |
| `pin` | `RECORDS-PIN :: PASS -- 17 citations, 9 tag and 10 heading references, pinned to 7986273b…, 29 tags and 55 headings at the pin` |

My own plants, run with `S/review-thin/plant.py` against `probe_fails` with the real THIN_BASE and HEAD:

| plant | result |
|---|---|
| control | 0 failures |
| A: unlisted heading drop (C66) | P8 fires |
| B: unlisted tag drop (C39) | P6, P7 and P8 fire |
| C: unlisted whole-guide drop (C01) | P6 and P7 fire |
| E: unlisted drop of C13 | P6 and P8 fire |
| G: a listed drop of a citation still printed (C62) | P8 fires ("lists 3 … only 2 … gone") |
| I: a listed drop with a nonsense heading path | P8 fires both ways, so a D: key must equal the citation's own printed key |
| HEAD-only target loss (I passed a modified HEAD dict with `rvp1pi` or "retired material" removed) | P7 fires "in HEAD" ×3 |

**Answers to the brief's checks.**
- P6 accepts only listed drops: **yes**.
- P7 checks the targets in the tree and at HEAD: **yes**. The HEAD leg works but no self-test plant exercises it (NIT).
- P8 fails an unlisted drop and a listed drop that is still printed: **yes**.

### S1 (SHOULD-FIX): outside git the probe reports PASS, not SKIP

`check_note_records.py:342-352`. I ran the probe on an rsync copy outside git, with C66's citation removed and no
ledger row for the drop. It prints:

```
RECORDS-MOVE :: PASS (… P8 SKIP (THIN_BASE 563715b8 not readable from git here), 59 listed drops checked in the tree only; 0 failure(s))
rc=0
```

- P6 covers only tags and whole-document pointers, so outside git an unlisted *heading* drop is guarded by nothing.
- Yet the verdict word is PASS. That is a green gate that did not do the work.
- The self-test does fail closed outside git: `FAIL (… 17 of 20 …)`. Good.

**Fix:** when `info["thin"]` is false, print `RECORDS-MOVE :: SKIP (P8 …)` as the verdict word, so that it cannot be
read as PASS. Optionally, also exit with a distinct non-zero status unless `--allow-skip` is passed.

### S6 (SHOULD-FIX): the position of an unchanged KEEP is not probed

P8 counts per (file, key). The 12 unchanged KEEPs have no ledger row. So moving a KEEP to another sentence in the
same file passes: in plant H, I removed C62's citation from the 0.99% sentence and appended the same
"superseded values: retired material" citation to "The dependence on the learner is in no block". The result was
**0 failures**.

The delivered tree is correct: I checked all 17 positions by hand against `citations.md`.

**Fix:** add one `N:` row per unchanged KEEP that pins the citation to its sentence, as the 58 L-thin rows already do
for the edited ones.

### Q2: headings are checked against all five records files

This is acceptable. A citation names heading words without a file, so the check has to span the five files. Each part
is a substring test and nesting is not required. But plant I shows that P8 ties every D: key to the citation's own
printed key, and RECORDS-PIN Q4 checks those words at the pin. No change is needed.

## 5. The writer's questions

- **Q1: was C49 protected? No.**
  - The marker was `% Note register batch b3 (2026-10-21): the next sentence is kept verbatim; records-move-ledger.md
    row L12 probes it.`
  - The b3 ledger gives the same reason (`note-b3/ledger.md:155`: "KEEP (verbatim: records-move-ledger.md L12 probes
    it)").
  - So it was a checker pin, not an authority's protection. It is not an acknowledgment, AI-use text, a hold, or
    director-authorized wording.
  - The sentence is a pure record that the records print (§1). L12 was correctly re-pointed to `X:` plus
    `R:app_history.tex::It is not adopted and is not quoted anywhere in this note.`
  - Removing it is allowed under writer rule 1.
- **Q2:** see §4. No change is needed.
- **Q3: C66's scope. Keep the citation as delivered.** The text is unchanged by this batch.
  - The body prints "…by 0.28% and the covariance *used in this note* by 0.18%, a numerically negligible bound…".
  - The record (`app_history.tex:758`) says that these "are ratios taken against the superseded products … so they
    bound the size … rather than describing a current covariance". In the same quote it also calls 0.18% "the effect
    on the adopted covariance … after the flux (J28) correction".
  - So the "bound" scope lives only in the record, and the record is itself ambiguous about which product 0.18% is
    taken against. The source it cites is `RESULT-20260923-issue26-issue5.md:80`.
  - Put this to the human read (Joseph and Ben) as an open item. If the 0.18% is on a superseded product, the body
    should say so beside the number. It is not a defect of this batch.
- **Q4: README:137 — SHOULD-FIX (S4), update it in this batch.**
  - It reads "Proof that the records move lost nothing, and the pin of its citation | `check_note_records.py` (probe
    and `--self-test`; `pin` and `--self-test-pin`, run by `build_all.sh`) …".
  - The checker's contract has changed: P6–P8 and the `D:` probes now enforce the thinning, and probe/self-test need
    the canonical checkout.
  - Proposed text: "Proof that the records move lost nothing, that every citation dropped by the thinning
    (DECISION-20261022) is listed with a target that exists, and the pin of its citation | `check_note_records.py`
    (probe and `--self-test`, run in the canonical checkout, where P8 reads THIN_BASE; `pin` and `--self-test-pin`,
    run by `build_all.sh`) …".

## 6. Invariants and mechanics

- **Count.** 71 citations at base in the posted closure; I re-counted per file, comments stripped. 17 after. The
  decision's "70" was a rounded count: the base PDF has 72 "[38]" tokens, which is 71 citations plus the bibliography
  label.
- **The paper's text.** The sha of `pdftotext main_paper.pdf` is identical for the base build
  (`builds/note-thin-base`) and the thin build: `398b23cbc6f8`. Primer, PET note and records are identical too.
  Against rec3 the paper differs only at line 12, "(Dated: October 22, 2026)" against "October 21".
- **Build copies.** Both build copies are byte-identical to HEAD and to the worktree sources respectively.
- **Label numbers.** 0 differences in main_note (184), main_paper (34) and main_records (22). Only page fields moved:
  the note is 119 pages, against 120.
- **Logs.** 0 real undefined references in all 5 final logs, 0 multiply defined labels, and no `??` in the note or
  paper text.
- **Gates in `build.log`:**
  - BODY-POINTERS PASS;
  - RECORDS-PIN SKIP in the copy, and PASS in the worktree;
  - struck-value containment RESULT PASS;
  - SEC4 15/15.
- **`swallowed_text.py <wt> origin/main`:** flagged 0. Against `563715b8`: flagged 0.
- **The writer's `check_ledger.py`:** 89 rows, 177 probes, 0 failures. `--plant`: all 3 planted probes fail.
- **The writer's `base/` copies** equal HEAD byte for byte.
- **Protected text.** The deposit-hold sentence (`app_release.tex:10-13`) and `sec_joint.tex`'s "six conditions
  verbatim" are untouched. The only verbatim-marked span that was edited is C49 (Q1).
- **Paper pointers.** The paper's pointers into touched labels still find their facts:
  - `\napp{app:release}`: the AnaTuple checksums sit under AnaTuplePreservation2026, which is untouched;
  - `\napp{app:negweight}`;
  - `\nsec{sec:coverage}`: "specified in advance" is still printed, with C68 kept;
  - `\nsec{sec:eavailw-construction}`.

### NIT: side effects outside the batch's files

1. **The records number moved from [38] to [41].** The first records citation now comes later in the note, so the
   references formerly numbered 39–41 renumber to 38–40. No source hard-codes a number. Only the decision record
   quotes "Ref. [38]", as history.
2. **The records' "Cited at" column is stale for 16 tags** that the posted note no longer cites:
   - bin-mapping, coverage-toys, q3-excess, eavailw-excess, joint-5d, variance-sources;
   - closure-scripts, negweight-toy, negweight-audit, gbdt-closeout, oi6-oi8-oi126, p4-verifier;
   - rvp1pi, statband-retest, pot-ratio, bkg-mode-pins.

   The records intro says "Rows are ordered by the section that cites them". The records are frozen by the decision
   ("Not changed: the records document itself"), so this needs a separate authorization. Record it as known.
3. **An ignored, writer-era `docs/analysis-note/__pycache__/`** (10:00) sits in the worktree.

## 7. Register (E): surviving passages that still read as history or meta-text

The batch's scope was the citations, so this is for the human read.

1. `app_statmethods.tex:804` "The data/MC split bootstrap was run on the earlier rebuilt bootstrap." This now stands
   alone under its heading, with no result.
2. `sec_systematics.tex:119` "That band was later rebuilt, and neither it nor the rebuilt band is the block quoted
   here."
3. `sec_validation.tex:268` "The band was then rebuilt without this term. The quoted statistical block is a third,
   different ensemble"
4. `app_negweight.tex:282` "Purity is \textbf{a recorded choice, not a silent default}"
5. `sec_3d.tex:265` "The comparisons here and in \S\ref{sec:eavailw-band} are made with unchanged figure code from the
   repaired inputs."
6. `sec_3d.tex:294/418/428` "…because the 3D covariance that would be quoted is not used for any result in this note."
   This is the same disclaimer in three captions.
7. `app_codebase.tex:38` "training-seed block is assembled by the aggregation step of the 2D production, not by the
   \texttt{seedscan} scripts."

## Counts

- 71 base citations classified and checked: 17 KEEP, of which 4 were shortened, and 54 DROP. All 58 edits were read
  in the word-diff.
- 6 whole-text removals verified against the records text at HEAD.
- 24 tags verified at HEAD.
- 5 PDFs compared by pdftotext sha, and 3 aux files by label number.
- 10 plants of my own (A–J), plus a HEAD-only pair and an outside-git plant, and the 22-case self-test re-run:
  - D and F were swaps near probed sentences, and both were caught;
  - J was C66 correctly listed under "superseded values", and it stayed silent, as it should.
- 4 writer questions decided.

## Not checked

- I did not re-run `build_copy.sh`; I used the existing build directories after verifying their sources.
- I did not read the P1N rating quotes (`complaints.json`).
- The 16 re-pointed pre-existing ledger rows were checked only through P7 passing, not read one by one.
- I did not check whether the repository named in `NoteRecords2026` is publicly reachable.
- I did not trace the source of C66's 0.18% beyond `RESULT-20260923-issue26-issue5.md:80`.
- I did not do a full number-multiset audit of the note beyond the PDF text diff. That diff showed only the [38]→[41]
  change and page-number shifts.
