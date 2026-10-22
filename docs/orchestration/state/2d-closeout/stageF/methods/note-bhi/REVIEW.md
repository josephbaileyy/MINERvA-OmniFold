# REVIEW, batch bhi: App. G (`app_release.tex`) and App. H (`app_codebase.tex`)

Reviewer: read-only, adversarial. Before = `b603f9cf` (worktree HEAD; `origin/main` has since moved to `250025b5`, which
touches no file under `docs/analysis-note/`). After = the uncommitted edits in `S/wt-note-bhi`. Line numbers are from
the after files unless marked "before". My scratch copies are in `S/wt-note-bhi-work/rv-scratch/` and
`rv_app_*.before.tex`. I edited no worktree file and made no commit.

## Findings

### F1 BLOCKING: the new tolerance sentence overstates how tightly the verifier checks
- After, `app_release.tex:56-59`: "`code/verify_rc.py` ... performs every replay and figure check and prints
  `VERIFY: PASS` if all agree. Floating-point values must agree to a relative $10^{-12}$; integers and decisions must
  agree exactly."
- The writer's own source contradicts the universal reading:
  - RC7-README.md:109 gives the 1e-12 tolerance;
  - but RC7-README.md:63-64 says `fig_numbers.py` checks each quoted figure number "to within half a unit of its
    last printed digit".
- The code agrees with the README:
  - `rtol=1e-12` exists only in `publication/release/replay_inference.py:158` (the two replays);
  - `verify_rc.py:109` checks the condition-(i) L2 range by comparing two-decimal strings (`f"{lo:.2f}" ==
    macros["jtMoneMin"]`);
  - `verify_rc.py:88` checks Figs. 1-3 only by requiring that the three PDFs are made.
- The sentence follows directly after "every replay and figure check", so a reader takes 1e-12 as the tolerance of
  every check. That is a stronger verification than the package performs.
- Fix: "In the two replays, floating-point values must agree to a relative $10^{-12}$, and integers and decisions
  must agree exactly. Each quoted figure number must agree with its printed value to within half a unit of its last
  printed digit."

### F2 BLOCKING (lost scope): "under reading (a)" became "with the recovered pseudo-experiments added"
- Before, `app_release.tex:24-25`: "the lost-seed resolution under reading~(a),"
- After, `app_release.tex:26-27`: "the same results with the recovered pseudo-experiments added
  (\S\ref{sec:joint5d-lost})". The same wording is at `:50-51` ("as evaluated for the decisions and with the
  recovered pseudo-experiments added").
- `sec:joint5d-lost` (`sec_joint.tex:532-535`) has two readings with the recovered draws:
  - one with the variant shifts of the primary evaluation;
  - one with "the recovered draws added to the calibration (the shift recomputed on all draws)".
- RC7 replays only the first: `expected/resolved-evaluate.json`, from `data/recovery-union/`, which RC7-README:143
  calls "reading (a)". The second reading's tests are not replayed; W1 uses it for the projections only.
- The new pointer therefore covers both readings, and the claim widens to one that RC7 does not reproduce.
- "reading (a)" is not defined anywhere in the note, so dropping the label is right. Its scope must go back in, in
  the note's own terms.
- Fix: at `:26-27`, "the same results with the recovered pseudo-experiments added and the variant shifts of the
  primary evaluation (\S\ref{sec:joint5d-lost})". At `:50-51`, write "... and with the recovered
  pseudo-experiments added, at the primary evaluation's variant shifts".

### F3 SHOULD-FIX (Q3, decided): `code/verify_rc.py` makes the protected snapshot hold false as read
- The hold (protected, `app_release.tex:12-13`) reads: "The code paths and file names in this appendix and in
  App.~\ref{app:codebase} refer to the snapshot of the code repository".
- The new `\texttt{code/verify\_rc.py}` (`:56`) is a package path. At the snapshot that file is
  `publication/release/verify_rc.py`, and no `code/verify_rc.py` exists in the repository (`git ls-files`).
- "run from the unpacked package" does not override the hold. Read literally, the hold now gives a reader a path
  that does not exist.
- The hold cannot be edited, so the new text must conform to it.
- Fix: "the package's verifier (\texttt{publication/release/verify\_rc.py} in the repository), run from the top
  directory of the unpacked package, ...". Then delete the source comment at `:49`, "Package paths are relative to
  the unpacked package, not to the repository", which states the opposite of the hold.
- Pre-existing, NIT, not this batch: `z-cv.npz` (`:188`) is also not a tracked repository file. Only its
  `get-`/`put-...log` files are tracked.

### F4 SHOULD-FIX (Q4, decided: state it): the protected verifier sentence is false as read for one recorded value
- The writer argues that the protected sentence "is scoped to 'every figure number that it checks', so nothing
  printed is false". That misreads the sentence.
  - It has two objects: "reproduces **every value recorded in the package** and every figure number that it
    checks". The scope "that it checks" binds only the second.
  - `observed_jitter_p` is a value recorded in the packaged `expected/joint-evaluate.json`. Its source,
    `docs/orchestration/state/s5p/stage7/joint/joint-evaluate.json` (`build_rc.py:43`), has 5 occurrences.
  - `replay_inference.compare` does not read it, and RC7-README.md:114-115 says the rounding statement "is
    therefore not checked by `verify_rc.py`".
  - The note prints that statement as a result in `sec:joint5d-conditions` (`sec_joint.tex:386-388`, "unchanged
    except NuWro's shape test (2/1752 to 3/1752)").
- The protected sentence cannot change, so the limitation should be stated beside it, in "Contents and use".
- Fix: add "The verifier does not recompute the stability of the observed $p$ values under the data's rounding
  noise (\S\ref{sec:joint5d-conditions}); the package carries the 20 rounding jitters from which it can be
  recomputed." Source: RC7-README.md:111-117 and :142.
- Joseph should also know that the protected DA sentence overstates by this one field.

### F5 SHOULD-FIX: two descriptions in `records-move-ledger.patch` are not accurate
- **L-bhi4** says "merged with the next sentence".
  - The ancillary-files paragraph was one sentence before (`before :50-53`) and is one sentence after (`:64-67`).
  - The next paragraph (`:71-84`) is verbatim and still a separate paragraph.
  - Fix: "REWRITE: the files attributed to Ref. MINERvA:2021owq; articles added".
- **L1, L2, L4, L5 and L6** are rows that record the earlier records move.
  - The patch rewrites their probe strings to bhi's wording ("digests" -> "checksums"; "production rollup ... not by
    \texttt{seedscan}" -> "production ... not by the \texttt{seedscan} scripts").
  - It leaves their edit and reason columns untouched. L5 still says "mechanical tag rewrite".
  - Read alone, the ledger now credits bhi's wording to the earlier move.
  - Fix: append to each row's edit column "(probe text updated for the bhi register pass: digest -> checksum)", or for
    L5 "(...: rollup -> aggregation step)".
- **L-bhi2** does not mention the dropped "reading (a)". This becomes moot once F2 is fixed.
- The mechanics pass (see "Checks I ran"). The patch has 34 lines (`wc -l`), 20 of them +/- lines.

### F6 SHOULD-FIX (Q2, decided: yes, say so): "an independent reader" hides that the reader was an AI agent
- `app_release.tex:80-82` (verbatim, unchanged): "An earlier version of the package was also replayed from an empty
  directory by an independent reader."
- RC1-REPLAY-RECEIPT-20261006.md:13-14 says: "a fresh Opus 5.5 agent acting as an outside reader. It had no
  repository access and used only the tarball and its README."
- A specialist reading "independent reader" assumes a person outside the analysis. The note's AI-use statement
  (`main_note.tex:160-171`) mentions "independent read-only reviews" only in general terms, so it does not cure this
  sentence.
- Not this batch's defect: the paragraph is held verbatim because `check_note_records.py --self-test` anchors its
  reader-paragraph plant there (REPORT Q5). Rewriting it needs a new self-test anchor, which is a check-script change.
- Fix, for the author and the owner of the check script: "... by a separate AI agent (Opus 5.5) given only the
  package and its README, without repository access."

### F7 NIT: the reason for keeping the acceptance field is weaker
- Before (`:198-200`): "because a silent default would let the data format make a scientific choice."
- After (`:224-225`): "so that no default answers the question."
- The scientific stake is gone.
- Fix: "so that no default in the data format makes that scientific choice."

### F8 NIT: App. H drops the code option names `exact` and `hist`
- Before (`app_codebase.tex:26-27`): "\texttt{exact} cross-check, \texttt{hist} alternate".
- After (`:27-29`): "scikit-learn's exact-split gradient boosting ... its histogram gradient boosting".
- The descriptions are correct: `omnifold.py:159-184` builds sklearn `GradientBoosting*` for `exact` and
  `HistGradientBoosting*` for `hist`.
- No fact is lost, because `sec_method.tex:135,152` still print both names.
- The appendix is the terminology map, though, and the option names are what a reader greps for.
- Fix: "... exact-split gradient boosting (\texttt{exact}) for the cross-check, its histogram gradient boosting
  (\texttt{hist}) as an alternate ...".

### F9 NIT: the "RC7 does not contain all of them" sentence is now asserted, not disclaimed
- Before (`:43-44`): "not a claim that RC7 contains them all".
- After (`:102-103`): "RC7 does not contain all of them".
- This is a positive statement. It is true: by RC7-README:210 and the Contents table, RC7 lacks the five-axis central
  values, the covariance, the masks and $M$.
- I accept it. It is listed because it is a definite claim that the old text did not make.

## The writer's account and the requested checks

1. **The new facts in "Contents and use"**, checked against `docs/publication/release/RC7-README.md` and the
   code:
   - the contents list (:138-150) is correct;
   - the pinned packages: `publication/release/requirements.txt` pins exactly numpy==1.26.4, scipy==1.15.2 and
     matplotlib==3.11.2, so correct;
   - "fresh environment" (:75) and "run from" the package (:75) are correct;
   - `VERIFY: PASS` (:78; `verify_rc.py:123`) is correct;
   - the 1e-12 relative tolerance and exact integers come from :109, but are overstated as universal (F1).
2. **The five facts the paper relies on.** All five still print under `app:release`, the only label the paper
   cites (`main_paper.tex:158,166`; `paper_body.tex` has no pointer into App. G or H):
   - 2,374 inputs identified by SHA256: `:89-90`;
   - what the package does and does not reproduce: `:4-6` and `:71-79`;
   - the multiplier-scan exception: `:77-79`, verbatim;
   - the earlier AnaTuple production: `:82-83`, verbatim;
   - the exact-split 2D curve, with the article's figure regenerated separately: `:41-45`;
   - the paper's other App. G facts also still print in `:21-33`: the empty directory, the joint-test p values,
     decisions, robustness and power, the null-distribution figure and the $(\Eavail,W)$ map;
   - the 2,374-file record facts check against RECORD-20261010-ost61 (2,374 of 2,374 hashed; 1,885 files copied and
     verified; no simulation copy).
3. **Protected text**, checked with my own byte comparison against `git show HEAD`:
   - the hold sentence is byte-identical;
   - its clause from "refer to" on is byte-identical to `app_provenance.tex:9-10`;
   - the RC7 verifier sentence is byte-identical;
   - the verifier sentence sits in "Release status" (`:21-23`), and the RC1 replay is in G.1 (`:80-82`). They are not
     adjacent and not merged;
   - the G.1 paragraph 2 is byte-identical.
4. **The moved qualifiers are attached.**
   - "RC7 does not contain all of them" and "A fixed identity ... does not qualify the object scientifically" are the
     first and last sentences of the schema lead (`:102-106`), directly around the definition of the check marks
     they limit.
   - Moving them out of "Release status" is an improvement.
5. **`records-move-ledger.patch`**, applied with `patch` to a scratch copy (`rv-scratch/new/`). The patched file is
   byte-equal to the writer's `records-move-ledger.patched.md`.
   - Probe against `records-inventory-base.json`: `RECORDS-MOVE :: PASS (... 0 failure(s))`.
   - Self-test: `RECORDS-MOVE SELF-TEST :: PASS (delivered move silent: True; 12 of 12 planted defects fired their
     probe)`.
   - Unpatched: `FAIL (... 15 failure(s))`. On the base HEAD tree: `PASS`.
   - The descriptions: see F5.
6. **The open questions**:
   - Q2: yes, say it (F6);
   - Q3: conform to the hold by using the repository path (F3);
   - Q4: state the limitation, because the protected sentence is not scoped as the writer believes (F4).

## Checks I ran (counts)

- **Numbers**, comment-stripped multiset, before against after: 0 lost in either file. The added ones come from
  the new `\S\ref{sec:joint5d-*}` keys and $10^{-12}$.
- **References and citations**: 0 lost. 3 gained (`sec:joint5d-lost`, `-projections`, `-conditions`), and all
  three resolve to the claimed content.
- **`\label`, `\section` and `\subsection` sequences**: identical in both files.
- **`\texttt`, `\href` and `\repopath`**: lost `exact`, `hist` (F8) and bare `xsec_nd.py`, which became
  `nd-unfolding/xsec_nd.py`. That file exists, and `extract_cross_section_2d` is defined in
  `2d-unfolding/unfold_2d_omnifold_unbinned.py:1207`.
- **pdftotext of all 5 PDFs** against `builds/rec3` and `builds/note-bhi-base`:
  - paper, primer, PET note and records: byte-identical;
  - note: the differences are confined to App. G and App. H and to 2 table-of-contents page numbers;
  - `??` = 0 in all five.
- **Logs**: 0 undefined references or citations in any log (the "undefined" lines are font-shape warnings).
- **Build log**: build_all rc=0; RESULT PASS; BODY-POINTERS PASS; SEC4 15/15; struck-value containment ok;
  RECORDS-PIN SKIP in the copy.
- **`swallowed_text.py`**: flagged 0.
- **The writer's checker**: 66 rows, 101 probes, 0 failures. Its `--plant` 3/3 fire. My own two planted rows (a wrong
  tolerance exponent, and a B-probe on removed text) both FAIL.
- **Its `base/`** is byte-equal to HEAD.
- **Codebase claims** checked against the code: the backends (`omnifold.py`), the driver location and the
  `xsec_nd.py` path. "omnifile" appears nowhere else in the note, so renaming the list item loses no
  cross-reference.
- **`variance-sources`**: the records print `s5_rollup.py` under `2d-closeout/stageC/production/`, which covers the
  "aggregation step of the 2D production" wording.

## Register (E): surviving bookkeeping or history passages

1. "This appendix describes the local replay package that exists, RC7, and specifies ..." (`:4`). "that exists" is
   meta.
2. "An earlier version of the package was also replayed from an empty directory by an independent reader."
   (`:80-82`). This is history, held verbatim (see F6).
3. "The pseudo-experiment products are archived (about \SI{2.3}{GB})." (`:80`). A stand-alone status sentence.
4. "The same record, dated 2026-10-10, verifies copies of all 1,885 ..." (`:91-92`). Record-keeping tone; the date
   is kept on purpose.
5. "Of these, only the assembling revision and job of $C_{Z}$, job of $C_{EW}$ and read-back row-index checksum are
   fixed (Ref.~\cite{NoteRecords2026}, identities already fixed). No producing revision or job is recorded for the
   other objects, and the assembled package carries none." (`:142-146`)
6. "GENIE and NuWro require the flux-repaired predictions of 2026-09-27" (`:134-135`). The date is bookkeeping.
7. "The record of the projection carries \texttt{acceptance\_question: UNDECLARED}: when the projection was built,
   it had not been decided ..." (`:221-223`). Process narrative.

Overall, the register improved: the "RC7 was assembled before ..." and "must retain this field ... until a decision
is made" passages that P1N flagged in N14 are rewritten.

## Verdict: ADOPT-AFTER-FIXES

- Must fix: F1 and F2, which are one-clause repairs, and F3, which is needed to keep the protected hold true.
- Should fix: F4 (a one-sentence addition), F5 (ledger descriptions) and F6 (the author and the owner of the check
  script).
- Optional: F7-F9.

## Not checked

- The rendered PDF pages, visually.
- Records-document text beyond the `variance-sources` entry and the App. G records section headings.
- Whether the RC7 tarball on CFS matches the README. I read the repository's README and code, not the package.
- The glossary compliance of the whole batch, beyond the "adopted" and "digest" terms.
- Other batches' interaction with `records-move-ledger.md`. A parallel batch that also patches it will conflict on
  rows L1-L6.

---

# Re-review (round 2)

I re-checked the round-2 worktree read-only. The build in `builds/note-bhi` is the current tree: its
`app_release.tex`, `app_codebase.tex` and `check_note_records.py` are byte-equal to the worktree. Line numbers below
refer to the round-2 files. My scratch copy is `rv-scratch2/`.

## 1. F2: the writer is right, and my round-1 F2 was wrong

- **(a) is the union with S recomputed.** `RECORD-20261006-s5p-lost-seed-recovery-resolution.md` §3 labels its
  columns "(a) union, S recomputed" and "(b) frozen S".
- **RC7 replays (a).** `phaseC.txt:4` "(a) evaluate" writes `resolved-evaluate.json`. `build_rc.py` maps
  `expected/resolved-evaluate.json` to `state/s5p/recovery/phaseC/resolved-evaluate.json`, and `verify_rc.py` replays
  `data/recovery-union/` against it.
- **(b) is built at run time for W1 only.** `make_reading_b.py` builds (b) from the frozen and union inputs, and only
  W1 uses it.
- **Where my round-1 F2 went wrong:**
  - §10.6 (`sec:joint5d-lost`, `sec_joint.tex:532-535`) describes two readings. "The reading with the variant shifts
    of the primary evaluation" is (b). "The reading with the recovered draws added to the calibration (the shift
    recomputed on all draws)" is (a).
  - I mapped them the other way round, so my proposed fix would have named the reading RC7 does not replay.
  - Withdrawn.
- **The new wording at `:35-36`:** "in the reading with the recovered pseudo-experiments added to the calibration and
  the variant shifts recomputed on all draws (\S\ref{sec:joint5d-lost})".
  - It matches §10.6 in substance. §10.6 is the number the aux file gives for `sec:joint5d-lost`.
  - It is not character-exact. §10.6 has "draws" and "(the shift recomputed on all draws)". The plural "variant
    shifts recomputed on all draws" matches §10.7's own wording ("with the shifts recomputed on all draws") and changes
    no meaning.
  - Accepted.
- **NIT, `:63-65`:** "in the reading with the recovered pseudo-experiments added" relies on the definite article to
  point back to `:35-36`, and both readings add the recovered draws. Fix: "... and in the reading with the shifts
  recomputed on all draws". Optional.

## 2. F4: the verifier sentence (`:26-31`), the limitation (`:78-80`), and the paper

- **Each item, checked against `replay_inference.compare` (`:158-192`) and `verify_rc.py`:**
  - "the recorded observed statistics of the joint tests": `T_total_obs` and `T_shape_obs`. Correct.
  - "the $p$ value, count ... of every test and variant": `p`, `k` and `B` for `variants`, `robustness_variants`,
    `total`, `shape`, `total_robust` and `shape_robust`. Correct.
  - "... and decision of every test **and variant**": **overstated**. Decisions are compared only per test, in the
    `decisions` and `decisions_robust_kappa` families (with their thresholds). No per-variant decision is compared or
    recorded. See SHOULD-FIX R2 below.
  - "the robustness results": `robustness_variants` and `decisions_robust_kappa`. Correct.
    `robust_to_the_sub_fine_residual` is not compared field by field, but it is the per-test κ=3 decision that
    `replay_inference.py:205` prints. Acceptable.
  - "the power figures": `power[...]["claim_rule_determined"]["power"]`. Correct.
  - "every figure number that it checks": `fig_numbers.py`. Correct.
  - "It does not recompute the recorded stability ... under the data's rounding noise". Correct.
- **No packaged script computes `observed_jitter_p`. Confirmed.**
  - Of the nine packaged code files that `build_rc.py:33-47` maps, only `make_reading_b.py:28` mentions `jitters`,
    and it only copies the array through.
  - The field is never compared.
  - The only recomputation is `docs/publication/audit-20261008/checks/agentC_checks.py` (J13, line 51), which is not
    packaged.
  - The sentence at `:78-80` ("carries the 20 rounding jitters ... but no packaged script does so") is correct.
    Sources: RC7-README:111-117 and :142.
- **The paper's Data availability does not overstate.** "It recomputes every $p$ value, decision, robustness
  result, and power figure of the joint tests and the numbers quoted in Sec.~\ref{sec:central}" is true for what the
  paper prints:
  - The paper's joint-test $p$ values are the per-test k/B of its table (`paper_body.tex:1041-1050`). They are
    compared.
  - The paper never prints the rounding-stability statement. Its rounding mentions (`:95`, `:647`, `:759`, `:855`)
    concern the null's noise term and the estimators.
  - The numbers of Sec. `central` are checked to their printed precision.
  - No change is needed in the paper. That is consistent with its byte-identical pdftotext.
- **BLOCKING-UNTIL-RECORDED: the sentence was protected text adopted by Joseph.**
  - `DECISION-20261021-joseph-da-and-note-records.md:38-40` adopts it in Joseph's Decision 1 and quotes it
    verbatim. Round 1 listed it as byte-identical.
  - The rewording is correct and closes a real false-as-read claim, so I support it on the merits.
  - A director's message cannot stand in for Joseph's approval of a change to text he adopted, and the ledger row's
    "AUTHORIZED (director F4)" does not record his.
  - Before landing, two things are needed:
    - Joseph confirms the rewording;
    - an addendum to the DECISION (or a successor record) quotes the new sentence, so that the decision record and
      the note agree.
  - Without his confirmation, the fallback is to restore the original sentence byte-for-byte and keep `:78-80`
    beside it. That fallback leaves "every value recorded in the package" false as read.

## 3. F3, F1, F6 and the moved self-test anchor

- **F3:** `:69-71`, "the package's verifier (\texttt{publication/release/verify\_rc.py} in the repository), run from
  the top directory of the unpacked package".
  - `build_rc.py:35` maps `code/verify_rc.py` to that path, so the hold is now true as read.
  - The contradicting source comment is gone.
  - Resolved.
- **F1:** `:72-78`. Resolved. Each claim checked against the code:
  - The 1e-12 tolerance now applies to "the two replays": `replay_inference.py:158`.
  - "Integers and decisions exactly": decisions are compared with `!=`. Integers go through `np.isclose(rtol=1e-12)`,
    which is exact for k, B ≤ 1800.
  - Figure numbers are checked to half a unit of the last printed digit: `fig_numbers.py:5,20-24,162-170`.
  - The L2 range is checked against its printed values: `verify_rc.py:109`.
  - For Figs. 1-3, "the check is that the three figure files are produced": `verify_rc.py:88`.
  - NIT: Fig. 4, the null distributions that `:41-42` says are regenerated, is checked the same way, by its file
    being produced (`verify_rc.py:96`). Fix: "for the article's Figs.~1--4 themselves". Optional.
- **F6:** `:101-104`, "RC1, was replayed from an empty directory by a separate AI agent session (Opus~5.5) that had
  no access to the repository and used only the package and its README; its verifier passed". Checked against
  RC1-REPLAY-RECEIPT-20261006.md:13-19:
  - "fresh Opus 5.5 agent acting as an outside reader", with no repository access, using only the tarball and its
    README. Correct.
  - `VERIFY: PASS`. Correct.
  - The receipt's overall result is "REPLAY PASS WITH DEFECTS". The defects were in the README only and are fixed in
    the current RC1 tarball. "Its verifier passed" is true and makes no claim about the defects. Acceptable.
  - The sentence is still in G.1, apart from the RC7 verifier sentence in "Release status". The two are not adjacent
    and not merged.
  - Resolved.
- **The self-test anchor** (`check_note_records.py:545-549`; the plant is now `app_codebase.tex`, "supports future
  work" -> "supports later work"). Its meaning is intact:
  - The plant still edits a base READER paragraph that prints verbatim. With the moved anchor, P5 fires on hash
    `dbf0faa3ea9a`.
  - The new self-test passes 12/12 on the round-2 tree. It also passes 12/12 on the HEAD tree, so the plant is not
    tuned to this batch.
  - The old self-test fails on the round-2 tree: 11/12, with "edited reader paragraph" silent. The old anchor
    sentence still exists, but its paragraph `06f284f7a786` is now a ledger REWRITE. So the move was necessary, not
    cosmetic.
- **Fragility:** moderate, and it fails loudly.
  - A missing anchor gives "UNAPPLIED ... not found" and a FAIL (`:587-589`).
  - So does a later ledger REWRITE row for `dbf0faa3ea9a`.
  - The PET paragraph is reader text in a batch-editable appendix, so the next register pass on App. H will break it
    the same way.
  - Better, for whoever owns the check: choose the plant target at run time as the first base READER paragraph
    that prints verbatim and is not in the ledger.
- **Scope note:** `check_note_records.py` is a check script, which the writer brief's rule 4 places outside the
  writer's files. The edit is sound. It should land as its own commit, with the authorization named in the message.

## 4. The regenerated `records-move-ledger.patch`

- Applied with `patch` in `rv-scratch2/`, the result is byte-equal to `records-move-ledger.patched.md`.
- `RECORDS-MOVE :: PASS (... 0 failure(s))` against `records-inventory-base.json`.
- `RECORDS-MOVE SELF-TEST :: PASS (... 12 of 12 ...)`.
- With the unpatched repository ledger: 17 FAIL lines.
- The round-1 F5 descriptions are fixed:
  - L-bhi4 now reads "the files attributed to ... articles added";
  - L1, L2, L4, L5 and L6 each carry "(probe text updated for the bhi register pass: ...)";
  - L-bhi2 names the verifier-sentence correction and the reading-(a) rewrite;
  - L-bhi5 is now used, for the RC1 sentence.
- The descriptions are honest.

## Other round-2 checks

- **pdftotext** of the paper, primer, PET note and records: byte-identical to `builds/rec3`. The note's differences
  are in App. G, App. H and four table-of-contents lines. `??` = 0 everywhere, and every log has 0 undefined
  references or citations.
- **The hold:** still byte-identical.
- **`swallowed_text.py`:** flagged 0.
- **The writer's checker:** 69 rows, 107 probes, 0 failures. `--plant` fires 3/3.
- **The round-1 NITs F7 and F8:** applied. "so that no default in the data format makes that scientific choice";
  `\texttt{exact}` and `\texttt{hist}` restored in App. H.

## Re-review verdict: ADOPT-AFTER-FIXES

Remaining fixes:
1. **BLOCKING-UNTIL-RECORDED.** Joseph confirms the reworded verifier sentence (`:26-31`), and a DECISION addendum
   quotes the new text. Otherwise restore the original byte-for-byte.
2. **SHOULD-FIX R2.** At `:28`, change "the $p$ value, count and decision of every test and variant" to "the $p$ value
   and count of every test and variant, and the decision of every test". This is a one-clause change to the same
   sentence, so do it before Joseph confirms.
3. **Process.** Land the `check_note_records.py` anchor move as its own commit with its authorization. Apply the
   patched `records-move-ledger.md` in the same landing. Otherwise the canonical RECORDS-MOVE probe fails with 17
   failures.

Optional NITs: `:63-65` (name the reading), and Figs. 1-4 at `:77`.

Once 1-3 are done, I would ADOPT.
