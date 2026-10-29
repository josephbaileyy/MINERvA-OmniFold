# Note round n4: report (in progress, 2026-10-28)

**Lane:** paper rewrite, for the director.

**Base:** origin/main `371cccec`. The branch is `note/n4-front-matter-20261028`.

**Under:** `outline.md`, as approved, with the director's rulings recorded at its end.

**Records** (this directory):
- `apply_n4.py`: every edit, by batch;
- `ledger.md`, checked by `check_ledger.py`;
- `agy/`: the batch reads;
- `release-claims.md`: the release appendix's claim table, built by an independent read-only agent from the RC7 tarball (`release-verify-run.txt`, `release-jitter-check.json`); its FALSE claims are with the director;
- `compose_f.py`, `map-doubtful.md`, `tools/`, `scores/`: batch F.

This is the first round in which the structure is not on trial (ruling 3). Joseph decided the front matter's
structure, so the pairwise and P1N judge only its wording.

## Batch C: the interval-sense "calibration" sites and the main-result sentence

These are accuracy and consistency fixes, unscored, under rulings 2a and 2b. There are nine edits in six files.

| id | site | before | after |
|---|---|---|---|
| C1 | `sec_5d.tex` sec:val-departure | "a pooled calibration test of its statistical intervals" | "a pooled test of its statistical intervals" |
| C2 | same | "does not establish calibration for every functional" | "does not establish coverage and width for every functional" |
| C3 | `sec_5d.tex` sec:coverage-5d | "a pooled calibration pass" | "a pooled pass" |
| C4 | `sec_validation.tex` lead | "checks neither interval calibration nor" | "checks neither the coverage and width of the intervals nor" |
| C5 | `sec_pet_campaigns.tex` | "H2S1T24 fails interval calibration" | "H2S1T24 fails the frozen coverage rule" |
| C6 | same | "the measured PET procedure failed calibration" | "… failed the frozen coverage rule" |
| C7 | `app_statmethods_nd.tex` | "constructs calibrated intervals" | "constructs confidence intervals" (the cited paper's title) |
| M1 | `sec_execsummary.tex` | "The main results are the validation findings. They hold …" | "The principal result is the sixteen-cell cross section of §…, with its covariance and generator comparison. The results hold …" |
| M2 | `sec_summary.tex` | "The main results are the validation findings, within the scope …" | the same sentence, then "The results hold within the scope …" |

**Evidence:**
- **C1–C3:** the candidate's test is row A2 of `OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md`. It gives
  pooled pull SD 1.023, pooled coverage 0.680 / 0.942, a Mahalanobis distance, and "a pooled pass, not per-functional
  calibration".
- **C5–C6:** H2S1T24 is ineligible under the PET campaign's coverage rule, with C1 and C4 FAIL
  (`nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md:47`, `:49`). The rule is named "the coverage
  rule" there, not "calibration", so the sentences use that name.
- **M1–M2:** the sentence is the paper's printed Conclusions (`paper_body.tex:355`), retargeted. It agrees with the
  note abstract's first sentence.

**The six sites are all of them.** A sweep of every file `main_note.tex` inputs found each remaining "calibrat…"
sentence that mentions an interval, a pull, a width, a band or the bootstrap. All of them use the test sense:
- the joint tests' calibration;
- "classifier-calibration tests" (`sec_method.tex`);
- the extended-fiducial study's "calibration–evaluation split" and "a calibrated test" (`sec_fps.tex`);
- the ES's "the calibration and nuisance model of the generator tests".

**agy** (`agy/c` … `agy/c5`; pairs built by `agy/make_pairs_c.py` from `apply_n4.C` and the sources, nothing retyped):
- **The control** (one strengthening planted per pair) caught 9 of 9 in each of the five reads.
- **C5–C7** were SAME in the first read.
- **C1–C4 took three revisions.** agy's substantive points, each now met:
  - a pull width measures dispersion, not containment, so "coverage test" narrowed what was tested. C1 and C3 drop
    the adjective;
  - "coverage" alone narrows the interval sense of "calibration", which also covers width. C2 and C4 name coverage
    and width;
  - "coverage or width" reads as "neither". C2 says "and";
  - "failed its coverage test" split. C5 and C6 use the record's rule name.
- **The final read (`agy/c5`, two runs):**
  - run 1 is SAME on all of C1–C7;
  - run 2 is SAME on C5–C7. On C1–C4 its stated reasons are only that the word "calibration" was removed. Any
    terminology fix trips that when BEFORE is accepted as correct.
- **agy is noisy here (the director accepted stopping at this point):** the same C5 text was SAME in one read and DIFFERS in the next (`agy/c` Q5, `agy/c2` Q5). So
  the reads were stopped at that point, and the director decides.
- **M1 and M2 are DIFFERS in every read:** "AFTER drops BEFORE's statement that the main results are the validation
  findings". That is the change ruling 2a decided, so it stands.

**The primer (ruling 5) is not edited; the director ruled (a), leave it and flag it for Joseph:**
- `primer_body.tex:13` and `:57` say its main results are the tests of the method.
- The primer prints no sixteen-cell result: no sentence names it, and it predates the five-dimensional integration.
  It also says "the study does not deliver a validated five-quantity cross-section measurement".
- So "The principal result is the sixteen-cell cross section …", retargeted to the note, would announce a principal
  result the primer never describes.
- Making the primer consistent needs a paragraph on that result, which is a content addition beyond n4's scope.
- The primer is 15 pp before, and is unchanged.
- **For Joseph:** the primer is stale against the five-dimensional integration. It predates the sixteen-cell result and says the study "does not deliver a validated five-quantity cross-section measurement". That is a content question, outside n4.

**Checks:**
- `check_ledger.py .`: 9 rows, 15 probes, 10 changed base sentences, 0 failures.
- `--self-test`: PASS. Its plants:
  - a missing probe, a dropped sentence, a removed label, a false `R:` probe, an `R:` probe naming a note file;
  - an undeclared `app_release.tex` edit, and a declared but unpinned pair;
  - a frozen sentence edited, and the readiness sentence duplicated instead of moved: each caught;
  - a pinned pair and the declared verbatim move: each silent.
- `printed_diff`: exactly the 21 intended sentence lines.
- `reflow_tex.py --note --check`: PASS.
- `build_all.sh`: rc 0; note 130 pp, paper 11, primer 15; SEC4 15/15; no undefined reference.

## Batch F: the front-matter fold

These edits are under ruling 1, the length ruling (b)+(c), and ruling 2. They are written by `compose_f.py`, which
cuts every sentence it keeps out of the sources at `a2e89c5f` by its anchors, so nothing kept is retyped.

**What changed:**
- **The executive summary is now about one page.** It is 651 printed words and runs from below the abstract on p. 1 to
  the foot of p. 2.
  - It opens with the framing paragraph.
  - Each of seven results gets its headline sentences and a pointer to its body home. The first is the sixteen-cell
    result, using the abstract's numbers.
  - The limitations paragraph is the base ES's pointer list, as it stood at the base, with two additions:
    - the frozen 2D sentence;
    - one new clause, "No result's intervals have validated coverage", pointing to its three homes.
  - The readiness sentence moved verbatim from the status table into the 2D paragraph.
  - The joint-test paragraph keeps both frozen recovery disclosures and the NuWro-CH sentences verbatim.
- **The status table and `result_status_rows.tex` are deleted.** Its label, `tab:result-status`, had no reference.
- **§12 (sec_summary.tex)** keeps the two conclusions the ES does not state: the refined subtraction's effect, and the
  joint tests' design and reach. Its limitations paragraph is a pointer plus the frozen sentence, which is the one
  recorded exception to "limitations once" (ruling 2). Outlook and "Reusing" are unchanged.
- **§1:** Scope points to the list, the Topic → Section table is cut, and the companion-article sentence closes
  "Analysis strategy".
- **Three body sentences give homes to facts that only the front matter carried:**
  - the Valencia 2p2h citations, at the model's sentence in sec_3d.tex;
  - "Beyond this methodological band, the source of the shape difference has not been identified." in
    sec:results-tension, from the paper's wording;
  - "The coverage of the result's intervals has not been validated." in sec:fived16-fd, from the note abstract's
    wording.
- **The note:** 130 → 126 pp.
<!-- absence-ok: quotes the limitation sentences the fold gave body homes; not a claim that a result does not exist -->

**The fact-to-home map (the director's two conditions):**
- An independent read-only agent built the rows twice: once for the first composition, and again after the length
  ruling.
- Every changed sentence is covered: 79 rows and 334 probes, 0 failures. Every limitation of §12's former list is
  probed at its body home, not in the ES or §12.
- **Its LOST findings, each settled:**
  - the Valencia citations: moved to the body;
  - the 2D shape difference's unknown source: body home added;
  - the sixteen-cell coverage status, judged near-lost: body home added;
  - the roadmap's organizing rule ("each topic is treated in full in the section listed below"): metatext about the
    cut table, removed with it.
- **Its doubtful homes, accepted:**
  - the low-$W$ excess "in ratio": sec:eavailw-map with the figure's ratio panel;
  - the 4D closure "not graded", stated only as "no predeclared threshold";
  - rounding only: 0.10 against 0.102, and "a fifth" against 22%.
  The agent's full list is `map-doubtful.md`.

**The two-direction review** (a fresh read-only agent; 2 BLOCKER, 4 MAJOR, 7 MINOR), all fixed within the
structure:
- **B1:** the PDF predated the two body sentences. Rebuilt and checked in the PDF text.
- **B2:** Scope's "including the coverage status of each result … listed once" was false. Scope now just points to
  the list, and the list gained the coverage clause.
- **M1:** the post-hoc learner sentence is restored, verbatim.
- **M2 and M4:** the excess sentence is restored with its bias and generator context, verbatim.
- **M3:** the $W$-redundancy sentence is restored, verbatim.
- **The MINORs:** "part of tier~1"; the dip's pointer §7.6; which unfolds are central values; the §12 antecedent; the
  tension sentence placed after the methodological band, with a current Search line; the unified-throw sentence. The
  review's optional GiBUU clause was added, then removed on agy's objection (below).

**agy** (`agy/f`, `agy/f2`; four pairs built by `agy/make_pairs_f.py`):
- **First read:** both runs DIFFERS on the ES, for the same reason: the added "GiBUU comparison carries the fake-data
  limitation" made a result-wide limitation read as GiBUU's alone. It was removed.
- **Second read:** both runs SAME on all four pairs. The control caught 4 of 4 in each read.
- One run came back empty, because agy's headless mode denied a tool call. It was re-run unchanged.

**Scoring.** This is the first round in which the structure is not on trial (ruling 3): Joseph decided the front
matter's structure, so P2N and P1N judge only its wording within it.
- OLD is the note at `371cccec`.
- The pieces are cut by `tools/split_front.py`, which uses the n1–n3 pieces and blinding.
- The runs use `tools/p2n_pieces.sh` and `tools/p1n_pieces.sh`, copied from the lane scratchpad so that they survive.
- The base P1N was re-scored at `371cccec`, because the note changed after n3's baseline (the 5D integration and d2's
  abstract). sol2's first base runs hit codex-school2's usage limit and were re-run on the same account after the reset.

| piece | content | sol2 AB | sol2 BA | gemini AB | gemini BA | NEW wins | P2N |
|---|---|---|---|---|---|---:|---|
| N01 | abstract, ES, §1 | NEW 2 | NEW 2 | OLD 2 | NEW 2 | 3 | yes |
| N10b | §12, first wording | NEW 2 | NEW 1 | OLD 2 | OLD 2 | 2 | no: revised once |
| N10b | §12, revised once | NEW 1 | NEW 1 | OLD 2 | OLD 2 | 2 | **no: to the director, structure kept (ruling 3)** |

| piece | sol2 base | sol2 n4 | Δ (2-run) | gemini base → n4 | noise rule |
|---|---|---|---:|---|---|
| N01 | 3, 3 | 3.5, 3.5 | +0.50 | 2 → 2.5 | holds |
| N10b (revised) | 3, 3 | 3, 3.5 | +0.25 | 2.5 → 3 | holds |

**The N10b revision** (ruling 3: revise the wording once inside the same structure, then re-measure). Gemini's
reasons, in both orders, named three things, and each was revised:
- the opening, "This section adds the conclusions it does not state", became "The executive summary … gives each
  result with its scope and lists the principal limitations. Two further conclusions follow from the body.";
- "the purity-subtraction bias" had no antecedent, so it now reads "the bias that purity-based background
  subtraction leaves in the highest-$W$ cells";
- the limitations pointer read as a placeholder. It now reads "The executive summary lists the principal limitations
  (p. …), each with the section that states it."
The frozen sentence after it is unchanged.

**N10b still loses P2N after the revision,** 2 of 4 both times, split by model: sol2 prefers NEW in both orders in
both reads, and gemini prefers OLD in both. Gemini's second-read reasons no longer name a wording defect. Both
orders object to the structure itself:
- §12 "defers to an executive summary" instead of being "self-contained";
- the bullets do not restate "the hypotheses or baseline analyses";
- the limitations paragraph is a pointer "alongside a single disconnected remark". That remark is the frozen 2D
  sentence (ruling 2's recorded exception).
Under ruling 3 the structure is not reverted, and both runs go to the director. P1N on N10b holds (+0.25).

**The director accepted N10b as it stands** (2026-10-28): gemini's remaining reasons concern the structure that ruling
3 fixed, not the wording, and P1N fell for neither rater. The split is recorded verbatim:
- the first wording: sol2 AB NEW 2, BA NEW 1; gemini AB OLD 2, BA OLD 2;
- the revision: sol2 AB NEW 1, BA NEW 1; gemini AB OLD 2, BA OLD 2.

Gemini's two structural reasons, verbatim from the revision's reads:
- AB: "In the \"Principal limitations\" section, Document A delivers a cohesive, dense, and self-contained technical synthesis characteristic of a PRD companion note, whereas Document B reads like an unedited draft that inappropriately defers to an executive summary before trailing off with an isolated, orphaned sentence." (`scores/p2n-rev/N10b.gemini.AB.txt`);
- BA: "In the \"Principal limitations\" section, Document B uses precise, publication-grade passive and active
  constructions to articulate methodological caveats, while Document A reads like an unfinished outline that merely
  defers to another section alongside a single disconnected remark."

It is not revised again.
The reads are in `scores/` (P2N, P2N after the revision, and the base, n4 and revised P1N).

**Checks:**
- `check_ledger.py .`: 79 rows, 334 probes, 90 changed base sentences, 0 failures.
- `--self-test`: PASS. The move plants are now built on the base files, so they hold before and after the move.
- `compose_f.py --check`: OK.
- printed_diff on every body addition.
- `reflow_tex.py --note --check`: PASS.
- `check_body_pointers.py`: PASS.
- `build_all.sh`: rc 0; note 126 pp, paper 11, primer 15; no undefined reference.

## Batch R: `app_release.tex` (outline sec. 3; the director's rulings A–D)

**The claim table** (`release-claims.md`, built by an independent read-only agent):
- 95 atomic claims: 90 TRUE, 4 FALSE, 1 UNVERIFIABLE (the deposit snapshot, `\depositsnapshot`, which stays: ruling D).
- How it was checked:
  - the RC7 tarball matches its recorded sha256, and its 32 inner checksums pass;
  - `verify_rc.py` printed `VERIFY: PASS` (exit 0, 277 s) in a fresh environment built from `requirements-lock.txt`
    (`release-verify-run.txt`);
  - the jitter recomputation was retried single-threaded and finished in 35 s, matching the recorded
    `observed_jitter_p` in 10 of 10 tests (`release-jitter-check.json`).
- **Two runs were stopped after about 5 h each:** a standalone Fig. 4 regeneration and the first jitter recomputation.
  Both were thrashing in OpenBLAS's thread pool and contending with each other. The Fig. 4 claim is graded from the
  verifier's own `[ok] Fig. 4 … regenerated` line.

**What is applied** (8 pairs, each pinned by sha256 in `check_ledger.REL_PINS`):
- **R2–R4:** d2's scoped "five-axis covariance of the configuration-(a) central value", imported from
  `fived16/d2/options.py`. Each is TRUE in the table (ruling A).
- **R1 is not applied** (ruling A). "the quoted closure, bias and covariance-status measurements of the
  configuration-(a) central value" is FALSE as read: the closure and bias numbers come from configurations (c)–(e).
- **RL-21, RL-27 and RL-39:** RC7 regenerates the figures of the earlier version of the article it was assembled for.
  The article cites no note figure. Neither document now prints the one-dimensional projections, and today's Figs.
  1–3 are not RC7's (ruling B).
- **RL-59:** "2,374 inventoried input files (2,307 AnaTuples and 67 flux, reweight and parameter files)". This was
  re-measured at the n4 head from `ANATUPLE-SHA256.tsv` (sha256 `913e004d…`, the record's): 1,818 data and 489
  simulation AnaTuples, 58 MAT flux and reweight files and 9 parameter files. RC7's own inventory has 2,374 rows.
- **Line 45:** "NERSC project storage" for "collaboration storage". The copies are in
  `/global/cfs/cdirs/m3246/josephrb` (ruling C).

**agy** (`agy/r`; `agy/make_pairs_r.py`; the CONTEXT of each pair is its claim-table row):
- The control caught 8 of 8.
- **RL-21, RL-27, RL-39, RL-59 and line 45:**
  - run 1 is SAME on all five;
  - run 2's five DIFFERS each describe the correction itself ("correcting the repository where the copies actually
    reside"), and none calls a fix unsupported. A truth fix contradicts its BEFORE by design.
- **R2–R4:**
  - run 2 is SAME;
  - run 1 is DIFFERS: "of the configuration-(a) central value" is not supported by the single CONTEXT sentence given,
    which says "used with that central value".
  - At `371cccec` the note already prints "five-axis covariance of the configuration-(a) central value" 15 times, in
    nine files, so the objection comes from the narrow CONTEXT, not from the note. They stand.
- Run 1 first came back empty (agy's headless tool denial) and was re-run unchanged.

**Records:**
- `check_note_records.py`'s comment no longer calls `app_release.tex` protected. Its reader-paragraph plant on the
  scope heading still holds, because n4 does not edit that heading.
- `fived16/HANDOFF.md` records the release. The fived16 and r19 checkers stay records of their rounds (ruling 4).
- **The records-move ledger** (`records-move-ledger.md`): six of its probes read the folded front matter or the
  edited release lines, and each is updated in place with the round named (L9b, L11, L16, L-bhi6, L-thin-C55,
  L-thin-C56). `check_note_records.py probe` and `--self-test` now pass.
- The pre-commit hook does not run that check, and only CI does. So every `record-checks.yml` step is now run locally
  before a push.
