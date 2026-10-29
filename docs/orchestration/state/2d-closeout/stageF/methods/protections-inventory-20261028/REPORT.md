# Joseph's requirements and protections on printed text: inventory, rater evidence and options (2026-10-28)

**Under:** `DECISION-20261028-joseph-protections-n4-release-retrospective.md` item 1 (:24-29). Joseph's words (:18):
"I think we need to readdress the strength of my requirements and protections. If the raters quote them it, I think it
is a strong indication that this is a problem that needs to be addressed and may require me remaking these decisions."

**Measured at:** origin/main `371cccecb` (merge of #460). Every file:line below is at that head.

**Written by** a read-only research subagent for the director. It made no compute job and no model, CLI or API call.
The director reviewed it and committed it.

**MEASURES:** nothing. It counts quotes that already sit in committed rater files, and it reads decisions and printed
text.

**CITABLE FOR:**
- the list of Joseph's requirements and protections on the paper's and the note's printed text, each with the record
  that set it;
- where each one prints at `371cccecb`;
- how often the committed rater outputs quote the text each one governs;
- the reason recorded when each was set, or that none was recorded;
- the options and what each would cost, as options.

**NOT CITABLE FOR:**
- a recommendation. None is made;
- any physics claim, or the truth of any rewrite;
- rater counts for runs whose raw outputs are not committed (r8–r11, r15–r18, the note's P1N runs). For those, this
  file repeats the round reports' own tallies and says so;
- a ruling. Until Joseph remakes a decision, it stands (`DECISION-20261028-…-retrospective.md:29`).

---

## 0. How to read this

**Where the rater evidence comes from.**
- **Paper, raw P1 outputs (committed):** 30 runs, 3 quotes each, 90 quotes.
  - r12: `r12/scores/P1__r12__{sol,gemini}__r{1,2,3}.txt` (6 runs);
  - r13: `r13/scores/P1__r12check__sol2__r{1,2}.txt`, `P1__r13__{sol,gemini}__r{1,2,3}.txt` (8);
  - r14: `r14/scores/P1__m__{sol2,gemini}__r*.txt` (main, after the shortened Data Availability) and
    `P1__r14__{sol2,gemini}__r*.txt` (12);
  - r19: `r19/measure/P1__r{1,2,3}__sol2.txt` (3), the paper's text as kept;
  - r20: `r20/measure/P1__r1__sol2.txt` (1), not adopted.
- **Paper, raw pairwise reasons (committed):** 20 files, `r12/scores/P2__*`, `r13/scores/P2__*`, `r14/scores/P2__*`,
  `r19/measure/P2__*`, `r20/measure/P2__*`.
- **Paper, round-report tallies only:** the raw outputs of r15–r18 and of the r17 baseline stayed in scratchpads
  (`r15/REPORT.md:114`). Their counts below are the reports' own, from `r15/REPORT.md:107-113`, `r16/REPORT.md:47-58`,
  `r17/REPORT.md:121-147`, `r18/REPORT.md:149-172` and `DECISION-20261025-joseph-r18-history-to-note.md:6-13`.
- **Note:** `note-n3/sol2-quotes-located.tsv`, 69 passages that sol2 quoted on n2's delivered text, located at
  `0d919b1a` (`note-n3/REPORT.md:47`). Each piece had 2 sol2 runs; the file does not record which run quoted what.
- **Proposal reads (choices, not quotes):** `fived16/d2/REPORT.md` (the d2 batteries) and `fived16/prd-read/`
  (rounds 2–6). They show what raters chose when offered a protected text and an alternative.
- All `rN/`, `note-*/`, `fived16/` paths are under `docs/orchestration/state/2d-closeout/stageF/methods/`.

**What raters never see.** A zero for these is by construction, not evidence:
- `\pubhold` renders nothing in rater copies (`rater-calibration/make_rater_copy.sh:46`), as
  `DECISION-20261021-joseph-register-loop-2.md:43-45` directs;
- the acknowledgments, the AI statement and the funding hold are cut by `blind.py --cut '^ACKNOWLEDGMENTS$'
  '^DATA AVAILABILITY$'` (`make_rater_copy.sh:101`);
- the title and authors are stripped by blinding (`register-method/HANDOFF.md:58-62`).

**Counting rule.** A quote counts for an item when it contains the governed text. One quote can count for several
items: the joint-test sentence of r12–r14 carried the design, the budget and the lost draws together. The tally regexes
were run on the extracted quotes and checked by hand; three false matches were removed (DA quotes that mention "the
recovery of the lost pseudo-experiments", and the binned-diagnostic quote that mentions "five iterations"), and one
missed rounding quote was added.

**Categories used in §5:**
- **HONESTY:** a fact the documents must state so that what they print is not false or misleading (a post hoc choice,
  data seen before a design, an untested property, a missing input);
- **PRE-REG:** a fact about what was fixed before the data or a statistic was seen, or a decision rule's outcome;
- **OWNERSHIP:** text whose wording Joseph reserved to himself;
- **EXTERNAL:** an obligation outside the analysis (journal policy, funders, the collaboration);
- **STYLE:** a presentation choice.
<!-- absence-ok: defines the inventory's category labels; not a claim that a result is absent -->

---

## 1. The inventory

Each item gives: what it requires; the record that set it, with its date; how it is enforced; where it prints now; the
rater evidence (§2 has the tables); what it protects, as recorded (§3); and the options with their costs (§4).
"Options" always means: **keep** as is; **relax** the wording under the guardrail; move it to the **note** with a
pointer; drop it from the **abstract** only; **remove** it.

### A. Text whose wording is Joseph's

**A1. The Data Availability paragraph** (paper).
- **Requires:** the wording is Joseph's; lanes propose and do not edit.
- **Set by:**
  - `DECISION-20261021-joseph-da-and-note-records.md:7-9` (2026-10-21): "It is Joseph's protected text." and "Its
    release bookkeeping was quoted by GPT-6.1-sol in 3 of 3 rubric runs on round r13." Joseph adopted the shorter r13
    draft (:25, "Decision 1. I think its a good idea to adopt."; :33-36);
  - restated: `DECISION-20261025-joseph-r18-history-to-note.md:53` ("**Data availability:** that text is Joseph's. r18
    proposes wording for Joseph and does not change it."); `DECISION-20261025-joseph-f0-limitation-stage-g-and-paper-scope.md:63`;
    `DECISION-20261028-joseph-result-table-and-deposit-package.md:49-50` ("The data-availability text stays his.");
  - still in force: `DECISION-20261028-…-retrospective.md:47-48`.
- **Enforced by:** a rule. On main no check freezes it. `r19/check_ledger.py:179-183` (lane ledger, run by hand only)
  holds `\begin{acknowledgments}` to `\end{document}` byte-identical to its base. `make_rater_copy.sh:104-110` fails if
  the DA heading, first or last sentence is lost from a rater copy.
- **Prints now:** `main_paper.tex:77`: "A candidate release package of about \SI{16}{MB}, not yet deposited, requires
  only numpy, scipy, and matplotlib.  It recomputes every $p$ value, decision, robustness result, and power figure of
  the joint tests and the numbers quoted in Sec.~\ref{sec:central}, and it regenerates the analysis note's figures of
  the joint-test null distributions and the $(\Eavail,W)$ map."
- **Raters:**
  - 13 raw P1 quotes, in 13 of 30 runs: r12 sol 3/3; r13 sol2 (r12 check) 2/2, sol 3/3, gemini 1/3; r14 main gemini
    1/3; r19 sol2 2/3; r20 sol2 1/1.
  - Round reports add the r17 baseline (passage 4 of `DECISION-20261025-…-r18…:12`) and r18 sol2 2/3
    (`r18/REPORT.md:170-171`).
  - After the shortening, sol2 quoted it in 0 of 6 runs in r14, then again in r18, r19 and r20.
  - In the d2 battery, raters chose "the typical draft" over the current text 4 of 4, strength 3
    (`fived16/d2/REPORT.md`, row B7). It stays a proposal (`DECISION-20261028-joseph-d2-approved-and-cheap-tier.md:27-29`).
  - Example, r19 sol2 run 2 (`r19/measure/P1__r2__sol2.txt`): "A candidate release package of about 16 MB, not yet
    deposited, requires only numpy, scipy, and matplotlib. It recomputes every p value, decision, robustness result,
    and power figure of the joint tests …".
- **Protects (recorded):** no reason recorded for the protection itself. The 2026-10-21 record gives the rater quote as
  the reason to shorten it (:9). A source comment says a DA statement is "required for PRD since 2024-09-04"
  (`main_paper.tex:73`); that is a comment, not a decision.
- **Category:** OWNERSHIP; EXTERNAL that a DA section exists.
- **Options:**
  - keep: none to truth. "of the joint tests" now describes tests the paper reports only through its Scope pointer
    (§6, item 3);
  - relax (let lanes reword, e.g. the d2 "typical draft"): no truth cost if every package claim is checked against the
    package manifest, as retrospective item 3 now requires for `app_release.tex`. The cost is that Joseph's sign-off on
    outward release wording becomes a check;
  - note (move the package detail to `app_release.tex`, keep one sentence): none to truth; the note already carries it
    (`app_release.tex:9`);
  - abstract only: not applicable;
  - remove: EXTERNAL cost, since PRD requires a DA statement (per the source comment).

**A2. The `\pubhold` text and the funding text.**
- **Requires:** the hold text is byte-identical; the funding text is Joseph's.
- **Set by:** `DECISION-20261021-joseph-da-and-note-records.md:43` (2026-10-21): "**Unchanged:** the `\pubhold` text is
  byte-identical. \"Candidate\" and \"not yet deposited\" stay." and :66 "The `\pubhold` text, the funding text and the
  release decision, which are Joseph's." Restated at `DECISION-20261021-joseph-register-loop-2.md:90` and in every later
  "Not changed" list through retrospective :47.
- **Enforced by:** a rule on main. `r19/check_ledger.py:197-201` (lane ledger, by hand) holds every `\pubhold` line to
  its base. `make_rater_copy.sh:29` runs `check_holds.py`.
- **Prints now:** `main_paper.tex:54` "\pubhold{funding and grant acknowledgments}"; `main_paper.tex:77` "\pubhold{deposit
  identifier and access route, after the separately authorized release decision.}"; the note's `\depositsnapshot` and
  `\fundingpending` (`main_note.tex:35-36`, `:97`).
- **Raters:** 0, by construction.
- **Protects (recorded):** no reason recorded beyond "which are Joseph's". Source comment `main_paper.tex:4`: "Do not
  submit a build that renders any \pubhold."
- **Category:** OWNERSHIP; EXTERNAL (funders, deposit).
- **Options:**
  - keep: none;
  - relax: none to truth; raters never see the holds, so relaxing gains no score;
  - note, abstract: not applicable;
  - remove: EXTERNAL cost before the funding text and deposit exist; a hold is replaced, not removed.

**A3. The acknowledgments, the AI-use disclosure and the author details.**
- **Requires:** the AI statement's approved content (tools, what they did, that the authors directed and verified, the
  figure statement, "AI tools are not authors", responsibility, a pointer to the note's full statement); the author list
  as approved.
- **Set by:**
  - `docs/publication/DECISION-20261006-joseph-publication-approvals.md:113-117` (2026-10-06): "**The AI-use
    disclosure:** the text proposed in `docs/publication/submission/AI-DISCLOSURE-PROPOSED.md` is approved, with
    placement in the Acknowledgments and a pointer from the method section, as proposed." and "**The author details:**
    approved as currently in `main_paper.tex`";
  - condensed at Joseph's instruction, `DECISION-20261021-joseph-ai-ack-and-register-loop.md:19-29`. Joseph's words
    (:11): "you can condense it (maybe just say the note will have a more full acknowledgement and make sure its
    there?)";
  - protected in register rounds: `DECISION-20261025-joseph-register-rounds-paper-rewrite.md:54-55`.
- **Enforced by:** a rule on main; `r19/check_ledger.py:179-183` by hand.
- **Prints now:** `main_paper.tex:54` "AI tools are not authors, and the authors take responsibility for the content.";
  the note's full statement, `main_note.tex:114-128`.
- **Raters:** 0, by construction.
- **Protects (recorded):** no reason recorded in the decisions. Source comments record APS requirements:
  `main_paper.tex:60-61` ("APS requires \"AI tool name and version\"") and `:64-65` (images).
- **Category:** EXTERNAL; authorship duty; OWNERSHIP.
- **Options:**
  - keep: none;
  - relax: no score gain (unseen); EXTERNAL risk if an APS element is lost;
  - note: done for the versions;
  - remove: EXTERNAL and authorship-duty cost.

**A4. The abstracts' final wording** (paper and note).
- **Requires:** the final wording is Joseph's; lanes draft.
- **Set by:**
  - `DECISION-20261027-joseph-f1-reprice-and-scope-review-before-r19.md:49` (2026-10-27): "Claims, KI-85, `\pubhold`,
    data-availability and release text, the abstracts' final wording and the title are Joseph's.";
  - earlier, `DECISION-20261025-…-f0-limitation…:39-40`; `caveat-study/REPORT.md:310` (R-P8, "the abstract is
    protected text");
  - Joseph delegated the choice: `DECISION-20261028-joseph-final-draft-d.md:21-24` (typical form), then approved d2
    (`d2-approved…:21`), whose abstracts are the raters' candidates PB and NA;
  - still listed as his: retrospective :47.
- **Enforced by:** a rule; `r19/check_ledger.py:186-192` (by hand) allows only sha-pinned pairs.
- **Prints now:** `main_paper.tex:46` ("… In a fake-data study, the reported uncertainty does not cover the estimator's
  bias at GiBUU-like truths or at a synthetic $q_{3}$ tilt. …"); `main_note.tex:72`.
- **Raters:**
  - raw P1 quoted no abstract sentence in 30 runs;
  - one pairwise reason, r20 sol2 A/B (`r20/measure/P2__AB__sol2.txt`): "\"Additional discrimination beyond matched
    coarse projections\" is more precise and informative than A's \"gain over matched coarse projections.\"". "gain"
    was then the protected abstract's word (`r19/REPORT.md:111-112`);
  - note: 1 sol2 quote of the n2 note abstract (`main_note.tex:52` at `0d919b1a`);
  - proposal reads: PB 8 of 8, NA 3 of 4.
- **Protects:** no reason recorded.
- **Category:** OWNERSHIP.
- **Options:**
  - keep: none;
  - relax: no truth cost under the guardrail as `final-draft-d.md:26-28` states it ("reducing limitations means
    removing sentences from the abstract, not weakening the ones that stay").

**A5. The title.**
- **Set by:** `f1-reprice…:49`; T1 at `DECISION-20261028-joseph-final-draft-d.md:19-20`. Not named in retrospective
  :47-48.
- **Enforced by:** `r19/check_ledger.py` `D2_PINS 'T1'`, by hand.
- **Prints now:** `main_paper.tex:36`, "Simultaneous measurement of the $\nu_{\mu}$ charged-current inclusive cross section
  on hydrocarbon in five observables from MINERvA open data".
- **Raters:** 0 quotes (blinded); raters chose T1 4 of 4 (`fived16/HANDOFF.md:75`).
- **Protects:** no reason recorded.
- **Category:** OWNERSHIP.
- **Options:** keep or relax: none.

**A6. `app_release.tex` (release text): released on 2026-10-28.**
- **Set by:** `DECISION-20261021-joseph-ai-ack-and-register-loop.md:43`; `DECISION-20261021-joseph-register-loop-2.md:90`;
  `fived16/HANDOFF.md:31`.
- **Released by:** retrospective :37-39: "It is no longer protected text. Every claim in it must be checked against the
  release package's actual manifest and contents." The director had reported (:12) that it "is protected by decision,
  not for a technical reason".
- **Stale enforcement:** `check_note_records.py:1181-1182` (self-test comment, "app_release.tex is a protected file");
  `fived16/check_ledger.py:47`; `note-n3/check_ledger.py:38`.
- **Prints now:** `app_release.tex:9` ("RC7, a local release candidate … has not been deposited or released under a
  publication tag. …").
- **Raters (note):**
  - 5 sol2 quotes of App. G (`app_release.tex:4`, `:42`, `:50` ×2, `:88`) and 1 of the §12 release sentence
    (`sec_summary.tex:78`): 6 of 69;
  - example: "A ✓ marks identities or values already fixed …; the rest are packaging.";
  - proposal reads: R1–R4 accepted 4/4 (prd-read r2); "scoped" 4/4 (d2 B5); the `:9` figure list "keep" 4/4 (d2 B4).
- **Protects:** "not for a technical reason".
- **Category:** was OWNERSHIP; now none.
- **Options:** already relaxed; the stale mentions (§6, item 5) remain.

**A7. Claims, and KI-85 as an item.**
- **Set by:** every 2026-10-14..28 "Not changed" list, e.g. `DECISION-20261024-joseph-adopt-re2-2d-refined.md:68` ("**No
  claim change.** Claims and KI-85 are Joseph's."); `director-handoff-20261027/HANDOFF.md:16` and :36; retrospective
  :47.
- **Enforced by:** the two-direction review (`register-method/HANDOFF.md:115-117`) and agy.
- **Raters:** counted under C1–C23.
- **Protects:** no reason recorded; it is the division of roles.
- **Category:** OWNERSHIP.
- **Options:**
  - keep: none;
  - relax: claim wording could change under the guardrail, but not the claim. The cost is the author's sign-off;
  - remove: authorship-duty cost.

**A8. Protected files, byte-identical** (a lane rule).
- **Requires:**
  - `values.tex`, `values_inference.tex`, `app_history.tex` and `app_release.tex` byte-identical;
  - `main_*.tex` changed only by approved `\input` lines and inside the abstract blocks.
- **Set by:** `fived16/HANDOFF.md:30-33` (lane handoff, 2026-10-27; "ABSTRACT_OPEN, the director's exception"). No
  Joseph decision names these files except `app_release.tex`.
  <!-- absence-ok: from a full read of the 2026-10-06..28 decisions; not a claim that a result does not exist -->
- **Enforced by:** `fived16/check_ledger.py:47`, `:173-189` and `note-n3/check_ledger.py:38`, lane ledgers that no hook,
  CI step or build calls. Their base defaults to the merge base with origin/main, so on main they compare main with
  itself.
- **Protects:** no reason recorded. It stops a register round changing a number.
- **Category:** process, with an HONESTY function.
- **Options:** relax or remove: no truth cost while `check_sec4_receipts.py` and `make_values_fived16.py --check` run
  in CI.

### B. Rules over every printed sentence

**B1. The guardrail: a qualifier stays where leaving it out would make a printed sentence false as read.**
- **Set by:**
  - first as "The director's reading, stated for Joseph to confirm or override"
    (`DECISION-20261021-joseph-register-loop-2.md:56-59`);
  - restated as decided in `DECISION-20261025-joseph-prd-caveat-convention.md:58-61`, r18 :56,
    `DECISION-20261027-…-5d-wording-q2-q5…:55-56` and `final-draft-d.md:26-28`;
  - for the paper, `DECISION-20261023-joseph-5d-a-and-register-round.md:33-42` ("every printed sentence is true when
    read with the paper's stated scope").
- **Enforced by:** ledger GUARD rows with plants, the two-direction review, agy.
- **Raters:** it governs most quotes. `register-method/HANDOFF.md:26`: "The guardrail-kept qualifiers are what the
  raters still flag at the end: that cost is the price of accuracy. Do not trade it for score."
  `METHODS-IMPLEMENTATION.md:760-763`: "Most of these are qualifiers the independent reviews required for accuracy".
- **Protects:** the truth of each printed sentence as read.
- **Category:** HONESTY.
- **Options:**
  - relax or remove: truth risk by definition;
  - a qualifier may move with its sentence, not without it.

**B2. No fact leaves both documents.**
- **Set by:**
  - `DECISION-20261021-joseph-register-loop-2.md:53-54`. Joseph's words (:22-23): "I think the limitations and
    after-the-fact disclosures don't need to be in the paper as long as they are mentioned somewhere, like in the note
    or another supplementary material.";
  - `DECISION-20261027-joseph-n4-after-content-cuts-and-paper-scope-consult.md:43`: "'No fact leaves both documents'
    stands until Joseph lifts it for a named fact."
- **Enforced by:** ledger `N:` probes (`r19-variant-b…:44-45`) and `check_note_records.py`.
- **Raters:** `note-n3/REPORT.md:164-169`: reaching P1N 2.5 "needs about 270–315 more distinct caveats removed", and
  "Every DROP row needs Joseph to lift 'no fact leaves both documents'".
- **Protects:** a disclosure must be "mentioned somewhere" (Joseph).
- **Category:** HONESTY.
- **Options:**
  - lift per named fact: an integrity cost for HONESTY or PRE-REG facts; none for history that bears on no quoted
    result;
  - remove wholesale: integrity risk.

**B3. The KEEP list** (14 qualifiers, `register-prd-study/REPORT.md` §5).
- **Set by:** `DECISION-20261023-joseph-5d-a-and-register-round.md:35-36` (Joseph :24 "decision 2: yes"): "**The KEEP list
  stands:** qualifiers whose removal makes a sentence false even under the stated scope stay where they are."; carried
  into `DECISION-20261025-joseph-register-rounds-paper-rewrite.md:34`, :54.
- **Enforced by:** KEEP ledger rows (r19: 14).
- **Where each prints now, with its raw P1 count:**
  - "hybrid null" (:443): `paper_body.tex:27` "they test hybrid null hypotheses, are calibrated within the implemented
    simulation model, and are not physical exclusions of the generators"; `:372`. 0 quotes;
  - "no evidence of" (:449): `paper_body.tex:27` "They show no evidence of additional discrimination beyond matched
    coarse projections." 1 pairwise reason;
  - "descriptive", 2D (:492): `paper_body.tex:127` "the descriptive covariance-weighted distance". 0;
  - the post-selection disclosure (:496): `paper_body.tex:130` (C8). 3;
  - "has not been tested", 2D (:514): `paper_body.tex:150`, `:372` (C2);
  - "provides no calibrated significance" (:536): `paper_body.tex:146`. 0;
  - the omission list (:540): `paper_body.tex:146` (C1). 0;
  - "except in the highest-W cells" (:557): `paper_body.tex:167`. 0;
  - "the quoted uncertainties omit this bias" (:558): its sentence qualified the purity-subtracted result, which left
    the paper (`move-nonfinal…:30-35`);
  - "rests on one seed pair" (:577): note only, `sec_5d.tex:306` ("Companion covariances at seed offsets $\{0,1200\}$
    …"). 1;
  - the envelope's definition (:441, :597): `paper_body.tex:97`. 0;
  - the binned diagnostic's population (:618): `paper_body.tex:210` (C11). 4;
  - "provided the calibration is exact" (:651): left with the joint tests; the note prints "under the stated
    calibration assumptions" (`sec_summary.tex:36`). 0.
  <!-- absence-ok: zero counts are of the committed raw quotes listed in section 0; moved qualifiers' homes are quoted -->
- **Search:** omit this bias; omits this bias; bias not included in uncertainty; in no quoted uncertainty, over
  docs/analysis-note/*.tex @ 371cccecb. No printed sentence of that form was found for the purity bias.
- **Protects:** each entry's reason is beside it in §5 of the PRD study, e.g. :443-444 ("Without it, \"tests ... of five
  generator predictions all reject\" reads as rejecting the generators.").
- **Category:** HONESTY.
- **Options:**
  - relax or remove: truth risk per item;
  - move with its sentence: done for three (seed pair, the calibration hypothesis, the purity bias);
  - none of the 14 is in the current abstract.

**B4. Gate-bound text.**
- **Set by:** `DECISION-20261025-joseph-register-rounds-paper-rewrite.md:54-55`: "Protected text stays as it is: holds,
  the KEEP list, gate-bound text, authors, acknowledgments, funding and release text."
- **Enforced on main:**
  - `check_sec4_receipts.py` (CI, `build_all.sh`) binds `paper_body.tex:150` ("with a median statistical uncertainty of
    \SI{0.676}{\percent}"), `:167` (4, 0.3, 1, 1.4 %), `:188` (74 %, 16–31 %, "within the quoted total uncertainty in
    about half of those cells"), five `values.tex` macros and two `sec_validation.tex` phrases;
  - `check_registry.py` (hook and CI) pins `paper_body.tex:72` ("This reproducible central value is that of its own
    systematic-universe ensemble, so its covariance is built with the same estimator.") and `:86`.
- **Raters:** the registry-cited (f) lines: r18 3/3, r17 1/3 by report; 0 in raw r19–r20. The `check_sec4` rescoring
  values sat in the earlier-band paragraph (C2, 12 quotes).
- **Protects:** no reason recorded in the decision; the gates keep numbers matched to receipts and citations resolvable.
- **Category:** HONESTY (numbers).
- **Options:**
  - reword and re-pin "with a record" (`director-handoff…:57`): no truth cost if numbers are unchanged;
  - r18 :39-40 already allows repointing `check_sec4`;
  - removing a gate is an integrity cost.

**B5. The caveat convention.**
- **Set by:** `DECISION-20261025-joseph-prd-caveat-convention.md:26-56`. Joseph's words (:16, :20): "at least the paper
  should handle it the same way similar length PRD papers do and the note should handle it the same way similar length
  notes do". The brief is `caveat-study/REPORT.md:300-310` (R-P1..R-P8).
- **Prints now:** `paper_body.tex:372` "The limitations of these results are stated with the results they qualify, …"
  (R-P2).
- **Raters:** 1 raw quote (r19 run 1). `r19/REPORT.md:131-132` says 2 of 3 (§6, item 7).
- **Protects:** Joseph's words.
- **Category:** STYLE. Its kind (b), "a deviation from a predeclared procedure | one sentence where the result is
  reported, with its consequence" (:53), is PRE-REG.
- **Options:** it is the yardstick for the other options; its guardrail (:58-61) binds.

### C. Facts that must print

**C1. The 2D endpoint: not independently validated; no coverage claim; no calibrated significance; what lies outside
every block.**
- **Set by:**
  - `DECISION-20261014-joseph-2d-endpoint-and-open-items.md:49` ("**Full scientific closeout is NOT ACHIEVED, and the
    package must say so.**"), :55-56 ("no coverage claim is made") and :65-67 ("It may not say: validated coverage,
    calibrated intervals or goodness-of-fit significance beyond what the construction supports.");
  - `DECISION-20261018-joseph-2d-j3-j5-provisional.md:25`, `:32-33` (W1(c); provisional until the Ben review, :13-14);
  - `DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md:77` ("the endpoint sentence names what is outside every block:
    G2, the learner dependence and C09/C10").
- **Enforced by:** a rule.
- **Prints now:**
  - paper `paper_body.tex:146`: "The covariance omits the approximation in the systematic-universe unfoldings for events
    that fail reconstruction, the learner dependence of Sec.~\ref{sec:repro2d-pub}, and the dependence on the
    regularization; … The covariance has not been independently validated.  It provides no calibrated significance for
    generator comparisons.";
  - paper `:150`: "We make no coverage claim on independent simulated samples or simultaneously over all reported bins
    and projections.";
  - note `sec_systematics.tex:198`: "We therefore make no claim about coverage, and goodness-of-fit values computed with
    this covariance are indicative only.", with the list at `:205`.
  <!-- absence-ok: quotes printed limitation wording; not a new absence claim -->
- **Raters:** 0 raw P1 quotes; note 1 (`main_note.tex:52`).
- **Protects:** `:49-53`: "Its inputs do not exist: - no independent production-size MC; - no validated continuous
  nuisance generator; - only truth-level, already-inspected independent-generator samples."
- **Category:** HONESTY.
- **Options:**
  - relax: already done ("closeout" became plain words, `plain-language-pass.md:30-32`);
  - note: truth risk while the paper quotes the 2D covariance;
  - remove: truth and integrity cost ("must say so").

**C2. KI-85 (2D statistical block's coverage untested; the re-test deferred and not pre-registered) and the earlier
band's history.**
- **Set by:**
  - `DECISION-20261014-…:64` ("**KI-85 is not lifted.**");
  - `DECISION-20261018-…-j3-j5…:43-44` (J5) and :29 (C7, "keep the regularization scan and rescoring, labelled
    historical");
  - `KNOWN_ISSUES.md:75` ("Joseph ruled 2026-10-06 that the held-out-MC re-test is deferred until after the publication
    package and is not pre-registered."; "S1 has not been coverage-tested.");
  - `DECISION-20261025-…-r18…:29-36` (the history "remains printed in the note, at `sec:coverage`").
- **Enforced by:** `check_sec4_receipts.py` (rescoring values, now in the note).
- **Prints now:**
  - `paper_body.tex:150`: "The coverage of this block and of the total covariance has not been tested.";
  - `:372`: "The two-dimensional covariance has not been independently validated, and its coverage has not been tested";
  - note `sec_validation.tex:162`: "The rebuilt band was only rescored post hoc (below), and the quoted block has not
    been tested.".
  <!-- absence-ok: quotes printed limitation wording; not a new absence claim -->
- **Raters:**
  - the history: 12 raw P1 quotes (r12 gemini 3/3, sol 1/3; r13 gemini 3/3; r14 main gemini 2/3; r14 gemini 2/3, sol2
    1/3);
  - by report: r16 and r17 3/3, the r17 baseline passage 1;
  - pairwise: r19 gemini B/A ("superseded preliminary bands");
  - 0 in r19–r20, after the move;
  - note: 6 of 69;
  - example, r14 sol2 run 1: "… so a post hoc rescoring of them against it is not an independent coverage test …".
- **Protects:** for "not lifted", the packet (`DECISION-PACKET-J3-J6.md:95`): lifting "reverses the endpoint ruling, and
  no test supports it". For the history, r18 :30-34: "The history adds nothing true about the quoted result."
- **Category:** HONESTY; PRE-REG; the history is caveat kind (a).
- **Options:**
  - history to the note: done;
  - moving "has not been tested" too would leave the 2D covariance unqualified (truth risk);
  - removing the history from the note needs a B2 lift and remakes C7; an integrity cost only if "not pre-registered"
    leaves both documents.

**C3. The universe law is a declared convention.**
- **Set by:** `DECISION-20261014-joseph-stage-d-input-answers.md:25` (Joseph: "declare them a convention for now"; "Any
  Stage D statement that rests on it must say so.").
- **Prints now:** note `sec_systematics.tex:198` ("under the conventions stated below").
- **Raters:** 0.
- **Protects:** no reason recorded.
- **Category:** HONESTY.
- **Options:** keep: none. Remove: truth risk for any sentence that rests on the law.

**C4. NormDISCC is zero and unconfirmed; the POT term is omitted.**
- **Set by:** `docs/publication/DECISION-20261012-joseph-2d-closeout-recipe.md:19-20` ("keep it null, disclose that it is
  zero and unconfirmed, and record the question for Joseph or Ben to ask MINERvA"); reaffirmed 2d-endpoint :30.
- **Prints now:** note `sec_systematics.tex:227`.
- **Raters:** 0.
- **Protects:** "whether that is intended is a collaboration question".
- **Category:** HONESTY; EXTERNAL.
- **Options:** keep (note only): none. Remove: truth risk.

**C5. The run-period term: an observed inconsistency of unknown cause.**
- **Set by:** `DECISION-20261015-joseph-playlist-consistency-term.md:52-53`; `DECISION-20261017-…:74-76`;
  `j3-j5…:34` (W2).
- **Prints now:** `paper_body.tex:153`: "The cause is not known, and these data cannot establish which period is correct.
  … its size is not validated and its own consistency check cannot fail."
- **Raters:** 0; note 1.
- **Protects:** NOT CITABLE FOR "a cause for the spread, or a statement about which run period is right" (:22).
- **Category:** HONESTY.
- **Options:**
  - relax: shorten the last clause if the check is not claimed as evidence;
  - note: truth risk while the paper quotes the 2D total.
<!-- absence-ok: quotes printed limitation wording; not a new absence claim -->

**C6. G2 is a disclosed approximation.**
- **Set by:** `DECISION-20261015-joseph-g2-carry.md:10` ("yes you can carry G2 as a disclosed approximation.") and
  :38-43.
- **Prints now:** `paper_body.tex:146`; note `sec_systematics.tex:203`.
  <!-- absence-ok: quotes printed text -->
- **Raters:** 0.
- **Protects:** :34-36 ("It does not bound a smaller one.").
- **Category:** HONESTY.
- **Options:** keep.

**C7. The published flux block is larger for a reason the inputs cannot determine.**
- **Set by:** `docs/publication/DECISION-20261012-joseph-adopt-2d-c04-repair.md:12-14`; W7 (`j3-j5…:39`).
- **Enforced by:** `check_sec4` binds `\uqMedian`.
- **Prints now:** `paper_body.tex:146`.
- **Raters:** 0.
- **Category:** HONESTY.
- **Options:** keep. Moving it to the note is a truth risk.

**C8. The post hoc choice of the 2D learner, and the seed disclosures.**
- **Set by:**
  - `docs/publication/DECISION-20261011-joseph-2d-central-lightgbm-seed42.md:73-75`: "**Post hoc choice.** The switch was
    decided after both learners' comparisons with the publication were known, and it lowers the published-covariance
    χ²/ndf from 3.66 to 2.65.";
  - KEEP E3;
  - KI-88 "keep and disclose" (`KNOWN_ISSUES.md:78`).
- **Prints now:** `paper_body.tex:130`: "The learner was selected after the LightGBM and exact-split comparisons with the
  published result, so this benchmark is a reproduction rather than an independent validation."
- **Raters:**
  - 3 raw P1 quotes (r13 gemini 1/3; r14 gemini 2/3);
  - note: 4 of 69 (`sec_method.tex:46`, `:76` ×2, `:99`);
  - example: "… was chosen after both comparisons were known, so the benchmark is a reproduction rather than an
    independent validation."
- **Protects:** PRD study :496-497: "It prevents \"we quote the LightGBM result\" from implying a blind choice."
- **Category:** HONESTY; PRE-REG.
- **Options:**
  - relax: the printed form already follows R-P4 (`caveat-study/REPORT.md:306`);
  - note or remove: truth and integrity cost.

**C9. The joint tests' data-informed elements and lost draws.**
- **Set by:**
  - `DECISION-20261004-s5p-production-budget-extension.md:64-73` ("The decision was made during production, after the
    controllers' looks had become visible …"; "The motivation is retrospective, as the authorization requires.");
  - `DECISION-20261021-joseph-ai-ack-and-register-loop.md:36-37` ("**No rewrite that drops a fact is adopted.** That
    covers a limitation, a post-hoc disclosure or a number, whatever score it would earn.");
  - `DECISION-20261025-…-r18…:41-47` ("**The budget extension and the lost pseudo-experiments keep one short statement
    each in the paper.** They bear on the validity of the joint tests' error control, a result the paper reports");
  - r17 ledger KEEP id D1 (`r17/ledger.md:317-319`, a round record);
  - moved to the note: `DECISION-20261028-joseph-r19-variant-b-and-moves.md:34-35` (Joseph: "Move them (Recommended)").
- **Prints now (note only):** `sec_joint.tex:118` ("First, the design's reviewers had seen descriptive per-cell residuals
  of the data before it was fixed. Second, a bounded extension of the production budget was decided during production,
  while the calibration's monitoring output showed observed claim $p$ values …"); `:232`; `sec_summary.tex:36`. The
  paper prints none of it.
- **Raters:**
  - 25 raw P1 quotes, in 25 of the 26 r12–r14 runs (all except r14 sol2 run 1): data seen 19, budget 16, lost draws 17;
  - by report: r15, r16, r17 3/3, r18 2/3, the r17 baseline;
  - pairwise: r12 gemini ("by people who had seen"); r18 ("its reviewers had already seen …", "predeclared design");
    r19 gemini B/A ("recounting cluster computing timeouts");
  - 0 in r19–r20;
  - note: 4 of 69;
  - example, r12 sol run 1: "The test design was fixed before any observed statistic was computed; its reviewers had
    seen descriptive per-cell residuals of the data before it was fixed, and a bounded extension of the calibration's
    computing budget was decided with observed p values visible, which the result above covers, since it holds for any
    stopping rule (Ref. [14], Sec. 10.3)."
- **Protects:** the error control of a reported result (r18 :41-42); the authorization's required retrospective
  disclosure (2026-10-04 :73).
- **Category:** PRE-REG; HONESTY.
- **Options:**
  - keep (note only): none;
  - relax in the note under R-P7 (`caveat-study/REPORT.md:309`): no truth cost if both data-informed elements stay
    named;
  - paper: already removed;
  - remove from the note: integrity and pre-registration cost.

**C10. NuWro on CH: the ten recorded decisions stand; the target-corrected evaluations are descriptive.**
- **Set by:**
  - `DECISION-20261020-joseph-nuwro-ch-claim.md:26-31` (provisional; Joseph :19-20). Joseph's words: "if it makes sense
    and sounds good, it never hurts to give a high-level claim and refer to the note, right?";
  - the clause left the abstract (`5d-a…:43-45`, Joseph "a) yes remove it");
  - the tests left the paper (variant B).
- **Prints now (note):** `sec_joint.tex:320` "These target-corrected evaluations are descriptive; the decisions of
  Table~\ref{tab:joint5d} are unchanged."
- **Raters:**
  - 9 raw P1 quotes (r12 sol 2/3; r13 sol2 1/2; r14 main sol2 3/3; r14 sol2 3/3);
  - by report: r15, r17 2/3;
  - pairwise: "re-grade" in 3 of 4 r13 reasons, in r16, and "and they stand" in r18;
  - 0 in r19–r20;
  - example: "These target-corrected evaluations are descriptive and do not re-grade the decisions of Table IV, which
    concern each prediction on the target it was generated for and stand (Ref. [14], Sec. 10.9)."
- **Protects:** :7 ("**NuWro total:** stays rejected only through the Holm re-sort"); readability (Joseph).
- **Category:** PRE-REG.
- **Options:**
  - keep in the note;
  - the printed form already drops "re-grade";
  - remove: pre-registration cost.

**C11. The CLAIM-ADDITION out-of-scope sentence.**
- **Set by:** `5d-a…:45-46` (Joseph "b) yes keep it only if the record requires it"); r15 found the record requires it
  (`r15/ledger.md:160`, L-5); r19 restored it with guard G22 (`r19/REPORT.md:73`).
- **Prints now:** `paper_body.tex:210`: "What unbinned information could recover, the coverage failure, and the validity
  of any interval lie outside its scope."
- **Raters:** 4 raw P1 quotes (r13 sol 3/3; r19 1/3); note 1.
- **Protects:** the source record's "Limits that travel with this outcome" (d-id/REPORT.md §11).
- **Category:** HONESTY.
- **Options:**
  - relax: needs the record's owner. The PRD study judged it unneeded (`register-prd-study/REPORT.md:623-626`), but r15
    found the record requires it;
  - note: the paper keeps the diagnostic sentence, so moving only this leaves an unscoped result;
  - remove: truth risk.

**C12. The 5D intervals' coverage is not validated, and why.**
- **Set by:** `DECISION-20261024-joseph-5d-community-standard-route.md:46-47` (Joseph "okay I agree"): "The paper states
  plainly that coverage was not validated, and why: Stage 0 and R10 are reported."; `measurement-framing…:26-27`.
- **Prints now:** `paper_body.tex:23` "Interval coverage has not been validated."; `:27` (Scope); `:372`; note abstract
  `main_note.tex:72`.
  <!-- absence-ok: quotes printed limitation wording; not a new absence claim -->
- **Raters:** Scope paragraph, 5 raw P1 quotes (r14 main gemini 1, sol2 1; r14 gemini 1; r19 1; r20 1); the r17 baseline's
  "repeated scope qualifications".
- **Protects:** :21-22 ("This drops validated coverage as the 5D publication requirement, and the paper states that as a
  limitation").
- **Category:** HONESTY.
- **Options:**
  - relax: the Scope words ("rather than of multidimensional OmniFold in general", "configurations, and deformations
    tested") are kind (d) scope, which the convention states once. No truth cost if Sec. I keeps "Interval coverage has
    not been validated.";
  - abstract: already gone from the paper abstract;
  - remove: truth risk.

**C13. The fake-data bias is not covered at GiBUU-like truths or the q3 tilt.**
- **Set by:**
  - `f0-limitation…:24-28` (Joseph :18 "Yes I accept the limitation but coordinate with the paper rewriter to make sure
    its presented in a typical way for PRD.");
  - `5d-generator-comparison…:28`;
  - `limitation-plan…:40-41` (Joseph "Keep as stated (Recommended)").
- **Prints now:** `main_paper.tex:46`; `paper_body.tex:23`, `:264`, `:312`; `main_note.tex:72`.
- **Raters:** 0 (+1 quote of the adjacent listing rule).
- **Protects:** the F0 report reading.
- **Category:** HONESTY.
- **Options:**
  - relax: it prints four times; one copy can go without truth cost;
  - abstract only: no truth cost while `:23` keeps it. It is the only limitation the paper abstract states;
  - remove: truth risk.

**C14. F1 is a bias test, not a coverage test.**
- **Set by:** `limitation-plan…:36` ("Poisson-only pseudo-data cannot test interval width. The paper says so.").
- **Prints now:** `paper_body.tex:23`, `:267`.
- **Raters:** 0 (it printed after r20).
- **Category:** HONESTY.
- **Options:** drop one of the two copies (no truth cost). Remove: truth risk.

**C15. The χ² depends on the flux correlations.**
- **Set by:** `measurement-framing…:29`; `limitation-plan…:43-48`; `final-draft-d.md:31`.
- **Prints now:** `paper_body.tex:23`, `:338`.
- **Raters:** 0; d2 "keep both" 4/4.
- **Protects:** no reason recorded.
- **Category:** HONESTY.
- **Options:** drop one copy (no truth cost).

**C16. The C_model label; the MINERvA comparison.**
- **Set by:** `DECISION-20261024-joseph-2d-model-dependence-component.md:43`, :49-53 ("must not say that MINERvA 'assumes
  its model is true'"); approved wording, `approve-integration-wording…:34-36`.
- **Prints now:** `paper_body.tex:157`, `:118`, `:188`.
- **Raters:** 0.
- **Protects:** :20-21 ("So 'assume their model as true' is not accurate.").
- **Category:** HONESTY.
- **Options:** one fewer repeated copy (no truth cost).

**C17. C_resp's scope.**
- **Set by:** `DECISION-20261026-joseph-adopt-cresp.md:42-43` ("what `C-RESP-SPEC.md` §7 states, and nothing more").
- **Prints now:** `paper_body.tex:118`.
- **Raters:** 0.
- **Category:** HONESTY.
- **Options:** keep. Moving it to the note is a truth risk.

**C18. The four low-stability cells, disclosed in the paper's limitations: NOT PRINTED.**
- **Set by:** `DECISION-20261024-joseph-h2-16-cell-definition.md:42-43` (Joseph :29 "3. no for now"): "The four
  low-stability cells (R02, R06, R10 and R15, stability 0.16–0.25) are disclosed in the paper's limitations."
- **Prints now:** nowhere.
- **Search:** R02, R06; R10 and R15; low-stability; stability 0.16; stabilit (printed lines), over
  docs/analysis-note/*.tex @ 371cccecb. The only stability sentences are `paper_body.tex:230` and `sec_5d.tex:88-90`,
  `:306`, about other things.
- **Raters:** 0.
- **Protects:** :25 ("disclose the four low-stability cells instead" of a stability rule).
- **Category:** HONESTY.
- **Options:** print one sentence; or the note; or Joseph remakes item 3.

**C19. Q5's decided wording.**
- **Set by:** `DECISION-20261027-…-5d-wording-q2-q5…:41-43` (Joseph "State the criteria (Recommended)").
- **Prints now:** `paper_body.tex:264` "the bias passes both criteria"; a recorded truth fix (`prd-read/REPORT.md:167`).
- **Raters:** 0.
- **Category:** HONESTY (the fix).
- **Options:** keep the printed form. Reverting is a truth risk per agy (`prd-read/REPORT.md:133`).

**C20. The (a) 5D covariance used under exception: its defect is stated where it is used.**
- **Set by:** `DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md:29-31` ("The defect, in the same place as
  the decision", "not in an appendix").
- **Prints now:** `paper_body.tex:188` ("an earlier purity-subtracted five-observable covariance that fails its specified
  acceptance criteria"); note `sec_5d.tex:250`.
- **Raters:** note 4 of 69.
- **Protects:** a permanent predeclaration failure.
- **Category:** PRE-REG.
- **Options:** keep while Fig. 3's band prints.

**C21. The inputs are an earlier production.**
- **Set by:** `DECISION-20261022-joseph-open-items-and-rewrite-timing.md:34-36`.
- **Prints now:** `paper_body.tex:35`, `main_paper.tex:77`.
- **Raters:** 0.
- **Category:** HONESTY.
- **Options:** keep.

**C22. Fig. 3: neither seed set was held out.**
- **Set by:** `DECISION-20261025-…-r18…:51`.
- **Prints now:** `paper_body.tex:193`, "Neither seed set was held out from the estimator's development."
- **Raters:** r17 baseline only.
- **Category:** HONESTY.
- **Options:** keep. Removing it is a truth risk beside "not used while it was chosen".

**C23. The extended-fiducial scope fix (note).**
- **Set by:** `DECISION-20261026-joseph-fps-scope-r04-sensitivity-and-tex-reflow.md:21-35`.
- **Prints now:** `sec_fps.tex:57`.
- **Raters:** note 1; three P2N reasons named "the battery of 2026-06-10" (`note-n2/REPORT.md:144`).
- **Protects:** :8-9 (the old sentence "is false as read").
- **Category:** HONESTY; the date is STYLE.
- **Options:** drop the date (no truth cost).

### D. Presentation rulings (all STYLE, 0 raw quotes)

- **D1. The χ² table:** χ² with ndf, shape-only, no p-values, no ratio, no diagonal-only χ²
  (`5d-generator-comparison…:35`; `chi2-table-format…:28-31`; `5d-wording…:39-40`).
- **D2. Only the final configurations:** the configuration letters print only in the note
  (`move-nonfinal-configurations…:30-40`, `:50`; reason :17-18, "presenting only the final method is PRD practice").
- **D3. Measurement framing:** the three limitations stated up front (`measurement-framing…:22-29`).
- **D4. The abstracts' typical form; the NuWro clause out** (`plain-language-pass2…:48-52`; `final-draft-d…:21-24`;
  `5d-a…:43-45`).
- **D5. The result table's form** (`result-table-and-deposit-package…:34-40`).
- **D6. The labels:** "GENIE CV" and the legend labels (`j3-j5…:42`; `pass2…:25`; no reason recorded).
- **D7. The note's front matter in n4** (retrospective :30-33).

### E. Quoted passages that no Joseph protection governs

- **The five-iteration sentence:** 7 quotes. R-P7 removed its pre-specification wording (`r18/outline.md:193`).
- **The rounding instability:** 4 quotes, all gemini. Q4 is open.
- **The 135 MeV materiality:** 3 quotes, gemini. Moved by O6.
- **One quote each:** the Gaussian-fit diagnosis, the note's-tests sentence, the listing rule.
- **The note:** 41 of its 69 quotes fall under no item.

---

## 2. The rater evidence, by round and rater

**Raw P1 quotes per item** (paper; column headers give the runs in each cell; "—" means 0):

| item | r12 sol (3) | r12 gem (3) | r13 sol2 chk (2) | r13 sol (3) | r13 gem (3) | r14 main sol2 (3) | r14 main gem (3) | r14 sol2 (3) | r14 gem (3) | r19 sol2 (3) | r20 sol2 (1) | total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C9 joint-test disclosures (any part) | 3 | 3 | 2 | 3 | 3 | 3 | 3 | 2 | 3 | — | — | **25** |
| A1 Data Availability | 3 | — | 2 | 3 | 1 | — | 1 | — | — | 2 | 1 | **13** |
| C2 earlier band / KI-85 | 1 | 3 | — | — | 3 | — | 2 | 1 | 2 | — | — | **12** |
| C10 NuWro decisions stand | 2 | — | 1 | — | — | 3 | — | 3 | — | — | — | **9** |
| (E) five-iteration | — | — | 1 | — | — | 2 | — | 1 | — | 2 | 1 | 7 |
| C12 Scope paragraph | — | — | — | — | — | 1 | 1 | — | 1 | 1 | 1 | 5 |
| C11 / B3 binned diagnostic | — | — | — | 3 | — | — | — | — | — | 1 | — | 4 |
| (E) rounding | — | 1 | — | — | 1 | — | 1 | — | 1 | — | — | 4 |
| C8 / B3 post-selected learner | — | — | — | — | 1 | — | — | — | 2 | — | — | 3 |
| (E) 135 MeV | — | 2 | — | — | — | — | 1 | — | — | — | — | 3 |
| B3 one seed pair | — | — | — | — | — | — | — | 1 | — | — | — | 1 |
| B5 Limitations lead | — | — | — | — | — | — | — | — | — | 1 | — | 1 |
| (E) Gaussian fit; note's tests; listing rule | — | — | — | — | — | — | — | 1 | — | 2 | — | 3 |

C9's parts (one quote may hold several): data seen 19, budget 16, lost draws 17. A2, A3 and A5 cannot be quoted
(§0).

**The sol/sol2 subset (54 quotes)**, one primary item per quote:

| item | quotes |
|---|---|
| C9 | 13 |
| A1 | 11 |
| C10 | 9 |
| C11 | 4 |
| C12 | 3 |
| C2 | 2 |
| B3 seed pair | 1 |
| B5 Limitations lead | 1 |
| E (five-iteration 7; Gaussian fit, note's tests, listing rule 1 each) | 10 |
| **total** | **54** |

- **One split consistent with the sibling retrospective's 27 / 24 / 3:**
  - (a) 27 = A1 11 + C10 9 + C11 4 + C2 2 + B3 1;
  - (b) 24 = C9 13 + five-iteration 7 + C12 3 + B5 1;
  - (c) 3 = the remaining E quotes.
- **Under this inventory, C9 is also set by Joseph's decisions** (DECISION-20261004 §3; r18 item 2; ai-ack :36-37).
  Counted as (a), (a) is 40.

**Round reports (P1 sol2; raw outputs not committed):**

| round | what the report says P1 quoted | items |
|---|---|---|
| r15 | rerun pseudo-experiments; "descriptive … do not re-grade"; five-iteration rule; seed panels; budget extension | C9, C10, E |
| r16 | post hoc rescoring (bound by Table I and `check_sec4`); budget; design-fixed sentence; "is being moved to the refined estimator" (decision wording, `2d-refined-integrate-ci.md:35-36`) | C2/B4, C9 |
| r17 baseline | earlier band; budget and lost draws; Fig. 3 seeds; DA; repeated scope | C2, C9, C22, A1, C12 |
| r17 | VII C design and budget 3/3; IV B rescoring 3/3; VII E target-corrected 2/3; III configuration 1/3 | C9, C2, C10, B4 |
| r18 | III (f) sentences 3/3; VII C 2/3; DA 2/3; V D covariance 1/3 | B4, C9, A1 |

**Pairwise reasons that name governed text:**
- **C9:** r12 gemini A/B; the r18 report; r19 gemini B/A.
- **C10:** r13 gemini A/B, sol A/B, sol2 B/A; the r16 and r18 reports.
- **C2:** r19 gemini B/A.
- **A4:** r20 sol2 A/B.
- **E (135 MeV):** r13 ×3; r15.

**Note (n2, sol2, 69 quotes):** A6 6; C2 6; C9 4; C8 4; C20 4; C1 1; C5 1; C11 1; C23 1; ungoverned 41.

**Proposal reads:**
- **d2:** DA "typical draft" 4/4 (B7); R1–R4 "scoped" 4/4; `app_release.tex:9` "keep" 4/4; abstracts PB 8/8, NA 3/4.
- **prd-read r2:** R1–R4 accepted 4/4; the 635-word note abstract "too long" 4/4.
- **prd-read r3:** T1 4/4.

---

## 3. What each protects, in one view

| reason recorded at the setting | items |
|---|---|
| a truth (else a printed sentence is false or misleading) | B1, B3, C1, C5–C8, C11–C17, C19 (the fix), C21–C23 |
| a pre-registration or decision-rule fact | C2, C8, C9, C10, C20 |
| a missing input or untested property | C1, C2, C3, C4, C6, C12, C14, C18 |
| an external obligation | A1 (source comment), A2, A3 (source comments), C4 |
| ownership of wording or claims | A1–A5, A7; A6 until 2026-10-28 |
| no reason recorded | the A1 protection itself, A2, A4, A5, A7, A8, B4, C3, C15, D6 |
| "not for a technical reason" | A6 |
| comparator practice | B5, D1, D2, D4 |
<!-- absence-ok: a category label in the summary of reasons; not a claim that a result is absent -->

Joseph's own words on the trade-off:
- "I think the limitations and after-the-fact disclosures don't need to be in the paper as long as they are mentioned
  somewhere" (`register-loop-2.md:22-23`);
- "Or is it necessary in order to present the truth?" (`r18-history-to-note.md:23`);
- "caveats matter in a close read, which is what the note is for, but would people reading the short paper care about
  them?" (`f0-limitation…:18`).

---

## 4. The options, in one view

- **Keep** costs no truth; its cost is the score, which `register-method/HANDOFF.md:26` already prices.
- **Relax under the guardrail** has no truth cost only where the governed text is wording: A1, A4, A8, B4, B5, C12's
  scope words, the repeated copies in C13, C14, C15 and C16, C23's date, and D1–D7.
- **Move to the note** has no truth cost where the qualified result leaves too (already done for C2's history, C9, C10
  and three KEEP qualifiers). It is a truth risk where the result stays: C1, C5, C7, C8, C11, C12, C17, C20.
- **Drop from the abstract only** applies to C13 (paper abstract) and C12 (note abstract). It has no truth cost while
  the body keeps the sentence.
- **Remove** costs truth or integrity for every HONESTY and PRE-REG item, and needs a B2 lift. It is an EXTERNAL cost
  for A1, A2 and A3.

**HONESTY-required facts, as distinct from wording preferences:** B1, B2, B3, C1–C9, C11–C17, C20–C22. Their wording
may change; the fact may not leave both documents.

---

## 5. Summary table

| item | set by (decision, date) | enforced by | raw P1 quotes + other | category | options with no truth cost |
|---|---|---|---|---|---|
| A1 Data Availability | da-and-note-records :7-9, 2026-10-21 | rule; r19 ledger by hand | **13** (13/30 runs); r17b, r18 2/3; d2 typical 4/4 | OWNERSHIP; EXTERNAL | keep; relax under manifest check; detail to note |
| A2 `\pubhold`, funding | da-and-note-records :43, :66, 2026-10-21 | rule; r19 ledger | 0 (never shown) | OWNERSHIP; EXTERNAL | keep; relax |
| A3 Acknowledgments, AI statement, authors | publication-approvals :113-117, 2026-10-06; ai-ack :19-29, 2026-10-21 | rule; r19 ledger | 0 (never shown) | EXTERNAL; authorship | keep |
| A4 Abstracts' final wording | f1-reprice :49, 2026-10-27; final-draft-d :21-24, 2026-10-28 | rule; ledger pins | 0; 1 pairwise; note 1 | OWNERSHIP | keep; relax |
| A5 Title | f1-reprice :49; final-draft-d :19-20, 2026-10-28 | ledger pin | 0 (blinded) | OWNERSHIP | keep |
| A6 app_release.tex | register-loop-2 :90, 2026-10-21; **released** retrospective :37-39, 2026-10-28 | stale comments | note 6 | was OWNERSHIP | released |
| A7 Claims | adopt-re2 :68 and every "Not changed" | review; agy | — | OWNERSHIP | keep |
| A8 Protected files | fived16/HANDOFF :30-33, 2026-10-27 (lane) | lane ledgers only | n/a | process | relax |
| B1 Guardrail | register-loop-2 :56-59, 2026-10-21; caveat-convention :58-61, 2026-10-25 | ledgers; review; agy | most quotes | HONESTY | keep |
| B2 No fact leaves both | register-loop-2 :53-54; n4 :43, 2026-10-27 | N: probes | note: 270–315 caveats | HONESTY | lift per non-disclosure fact |
| B3 KEEP list | 5d-a :35-36, 2026-10-23 | KEEP rows | 9 across entries | HONESTY | move with its sentence |
| B4 Gate-bound text | register-rounds :54-55, 2026-10-25 | check_sec4 (CI); check_registry (hook, CI) | r18 3/3, r17 1/3 | HONESTY | reword and re-pin |
| B5 Caveat convention | caveat-convention :26-56, 2026-10-25 | rule | 1 | STYLE; PRE-REG (b) | — |
| C1 2D endpoint | 2d-endpoint :49-56, :64-67, 2026-10-14; j3-j5 | rule | 0; note 1 | HONESTY | keep |
| C2 KI-85 and history | 2d-endpoint :64; j3-j5 :29, :43-44, 2026-10-18; r18 :29-36 | check_sec4 (note) | **12**; r16, r17 3/3; note 6 | HONESTY; PRE-REG | history already in note |
| C3 Convention | stage-d :25, 2026-10-14 | rule | 0 | HONESTY | keep |
| C4 NormDISCC, POT | closeout-recipe :19-20, 2026-10-12 | rule | 0 | HONESTY; EXTERNAL | keep |
| C5 Run-period term | playlist :52-53, 2026-10-15 | rule | 0; note 1 | HONESTY | keep |
| C6 G2 | g2-carry :10, :38-43, 2026-10-15 | rule | 0 | HONESTY | keep |
| C7 Flux block | c04-repair :12-14, 2026-10-12 | check_sec4 | 0 | HONESTY | keep |
| C8 Post hoc learner | lightgbm-seed42 :73-75, 2026-10-11 | KEEP rows | 3; note 4 | HONESTY; PRE-REG | R-P4 form (done) |
| C9 Joint-test disclosures | budget-extension :64-73, 2026-10-04; r18 :41-47, 2026-10-25; to note 2026-10-28 | ledger rows | **25** (25/26 r12–r14 runs); r15–r18; note 4 | PRE-REG; HONESTY | note only (done); R-P7 form |
| C10 NuWro decisions stand | nuwro-ch :26-31, 2026-10-20 | rule | 9; 5 pairwise | PRE-REG | note only (done) |
| C11 CLAIM-ADDITION sentence | 5d-a :45-46, 2026-10-23 | r19 B2j, G22 | 4; note 1 | HONESTY | keep |
| C12 5D coverage not validated | community-standard :46-47, 2026-10-24 | rule | 5 | HONESTY | shorten scope words |
| C13 Fake-data bias | f0-limitation :24-28, 2026-10-25; limitation-plan :40-41 | rule | 0 | HONESTY | drop a copy; abstract only |
| C14 F1 is a bias test | limitation-plan :36, 2026-10-27 | rule | 0 | HONESTY | drop one copy |
| C15 χ² depends on flux | framing :29, 2026-10-27 | rule | 0 | HONESTY | drop one copy |
| C16 C_model label | 2d-model-dependence :43, :49-53, 2026-10-24 | approved wording | 0 | HONESTY | drop a copy |
| C17 C_resp scope | adopt-cresp :42-43, 2026-10-26 | rule | 0 | HONESTY | keep |
| C18 Low-stability cells | h2-16 :42-43, 2026-10-24 | rule | **not printed** | HONESTY | print, or note |
| C19 Q5 wording | 5d-wording :41-43, 2026-10-27 | agy | 0 | truth-fixed | keep printed form |
| C20 (a) covariance's defect at use | z-cv adoption :29-31, 2026-09-20 | rule | 0; note 4 | PRE-REG | keep |
| C21 Earlier production | open-items :34-36, 2026-10-22 | rule | 0 | HONESTY | keep |
| C22 Fig. 3 seeds | r18 :51, 2026-10-25 | rule | r17b | HONESTY | keep |
| C23 FPS scope fix | fps-scope :21-35, 2026-10-26 | agy | note 1 | HONESTY; STYLE | drop the date |
| D1–D7 | see §1 D | rule | 0 | STYLE | all |

---

## 6. Where a protection and the current print or record disagree

1. **C18 does not print.** The four low-stability cells required by `h2-16-cell-definition.md:42-43` print in neither
   document (Search line under C18).
2. **C19 prints a changed form.** `paper_body.tex:264` reads "passes both criteria", not the decided "stays within the
   reported uncertainty by both criteria". It is a recorded truth fix (`prd-read/REPORT.md:167`). No decision names the
   new wording; d2, which Joseph approved, carries it.
3. **Data Availability is stale after variant B.** `main_paper.tex:77` still says the package recomputes "every $p$
   value, decision, robustness result, and power figure of the joint tests", which the paper no longer reports. It is
   protected and stays a proposal (`r19-variant-b…:46-49`; `d2-approved…:27-29`). It is not false of the package.
4. **Stale ledger justifications.** `r19/ledger.md` rows B3f-S1, K4d and B3-K9b cite "the protected abstract's 'no
   evidence of gain over matched coarse projections'" and "the protected abstract still states the rejections".
   `main_paper.tex:46` says neither.
5. **A6 is still called protected after its release** in `check_note_records.py:1181-1182`, `fived16/HANDOFF.md:16`
   and `:31`, `fived16/check_ledger.py:47`, `note-n3/check_ledger.py:38` and `director-handoff-20261027/HANDOFF.md:36`.
6. **The title** is Joseph's in `f1-reprice…:49` but not on the retrospective's list (:47-48). `fived16/HANDOFF.md:33`
   ("not edited") predates T1.
7. **Two round reports overstate their raw counts.**
   - `r19/REPORT.md:130-132` gives the five-iteration sentence 3 of 3 and the Limitations lead 2 of 3. The committed
     outputs give 2 of 3 and 1 of 3 (`r19/measure/P1__r3__sol2.txt` quotes Scope, the binned diagnostic and DA).
   - `METHODS-IMPLEMENTATION.md:591` says DA was quoted "2 of 3" in r12. The committed outputs give 3 of 3.
8. **C1's paper list omits the response-family assumption.** `paper_body.tex:146` names G2, the learner and the
   regularization; only the note adds "departures of the detector response from its parametrized family"
   (`sec_systematics.tex:205`). B2 holds. Whether the provisional J2 condition (`s5-plus-playlist…:77`) is still met is
   for the director.
9. **Nothing on main enforces A1–A5 or A8.** Their byte rules live only in lane ledgers that no hook, CI step or build
   calls (`.githooks/pre-commit:237-333`; `.github/workflows/record-checks.yml`).
