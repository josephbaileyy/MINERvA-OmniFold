# Round r12 writer report (first pass, before the review fixes; saved by the director from the writer's reply)

**Worktree:** `S/wt-reg2`, branch `stageF/register-r12-20261021`, based on 1a74560c. Nothing is committed.

## Build and checks (final run, as the writer reported them)
**`build_copy.sh r12 S/wt-reg2`:**
- build_all rc=0;
- BODY-POINTERS PASS;
- SEC4-RECEIPTS PASS (15/15);
- page counts: main_note 136, main_paper 13, main_primer 15, pet_note 26;
- `log-undefined=0` and `pdf-??=0` for all four PDFs.

**Other checks:**
- `swallowed_text.py`: flagged 0.
- `check_ledger.py`: 333 rows, 436 probes, 0 failures. A planted bad probe gives rc=1.

## Files changed
- `paper_body.tex`: rewritten.
- `main_paper.tex`: loads xr-hyper, adds `\externaldocument[N-]{main_note}`, and changes "adopted" to "specified" in the abstract.
- `sec_eavailw.tex:136`, `sec_5d.tex:118`, `sec_5d.tex:308` and `sec_joint.tex:580`: additions to the note.

## Word counts
Printed prose falls from 7,535 to 6,434 words.
- VII C–D: 1,304 → 991.
- VIII: 281 → 154.
- The abstract stays at 135 words.

## Moves to the note
Each moved item already prints in the note, and a probe in the ledger checks it.
- **Sec. II:**
  - the 135 MeV effect, not compared with the covariance → §7.1;
  - the neutron-mass W evaluation → §8.1;
  - the pT axis of the predictions → §8.2.
- **Sec. III:** the timing of (e); the central values not regenerated after the purity bias was found → §3.2.
- **Sec. IV A:** the exact-split seed spread; the LightGBM replacement → §3.2.
- **Sec. IV B:**
  - the run-period block's limits → §4.5;
  - the timing of the 2D pseudo-experiments and the post-hoc rescoring → §5.2;
  - the rebuilt band, never independently tested → §4.2;
  - validated intervals need samples not available → §4.6.
- **Sec. V:**
  - no prior criterion for the 3D/4D closures → §5.1, §9.1;
  - the timing of the coverage criterion; the separating test not run → §9.5, §9.1;
  - the timing of the 5D covariance criteria → §9.6;
  - the study's rules and budget → §9.4.
- **Sec. VII:**
  - conditioning and the declared shifts → §10.2;
  - the 0.8902α bound → §10.3, App. B.5;
  - the lost draws, design timing, extension and post-hoc studies → §10.3;
  - the rerun procedure → §10.6;
  - the design-review rate, the surrogate check and D → §10.4;
  - the untested response effects → §10.8;
  - GiBUU hydrogen → §10.9;
  - the projection criterion → §10.7.

## Additions to the note
- **§8.2:** the near-degenerate directions are consistent with the W redundancy (not shown); W's added information is not measured.
- **§9.2:** the cell holding the 74% residual; its cross-section share was not recorded.
- **§9.4:** the joint-test estimator keeps five iterations under a rule fixed beforehand.
- **§10.7:** the powers of the joint and projected tests have not been compared.

## New in the paper
- **Table III:** the D-ID comparison with exact binned unfolding, using numbers from note §9.3.
- **Sec. VI:** "15 of the 144" and "(121)".

## Qualifiers kept under the guardrail
- the FWER assumptions, including averaging over the nuisance priors;
- "provided the calibration is exact";
- "to the extent the simulated chain reproduces";
- the W²=0 clamp;
- "where this was evaluated";
- LightGBM chosen after the comparison;
- the rescoring is not an independent coverage test;
- "inferred from a Gaussian fit";
- "rests on one seed pair";
- "under the specified envelope prescription";
- the scope of the binned diagnostic;
- "carry over to G only if";
- "against the original null distributions";
- the κ-scan scope;
- power not compared with a reconstruction-level test.

## Note citations
- Implementation:
  - all 37 descriptive pointers become "Ref. [14], Sec. N" or "App. X";
  - they use `\nsec`/`\napp` with `\ref*`;
  - `build_all.sh` already builds main_note first.
- A missing label, or a missing aux file, gives undefined references, which build_all fails on.
- **Carry-forward:**
  - the paper's arXiv source must include `main_note.aux`, or have the numbers written in;
  - the hold-free rater build must build the note first.

## Writer's open items
1. The 2D band-coverage history stays in the paper, compressed, because `check_sec4_receipts.py` requires exact phrases.
2. The iteration-rule addition attributes the rule to the joint-test estimator. The source (`RECORD-20260927-s5p-stage2-exit.md` §3) states it for the baseline-capacity configuration. Reviewer to confirm.
3. One sentence on the data-informed design review and the budget extension is kept in VII C. It may move to §10.3.
4. "15 of 144" replaces "small share". The note also prints 2 identified, share 0.014.
5. The pointer for the 135 MeV numbers (0.67%, 1.05%) was dropped, because §7.1 does not print them. They still print in the paper.
6. The protected data-availability text is unchanged; GPT objects to its "candidate release" wording.
7. The abstract is unchanged apart from one word; its NuWro clause follows the 2026-10-20 provisional decision.

**Work files:** `S/wt-reg2-work/`:
- outline-before.md
- ledger.md
- outline-after.md
- check_ledger.py
- sentence_diff.py
- sentence_diff.txt
