# Independent scientific-scope review — dispositions (commit `b8f8e0aa`)

**Reviewer:** an independent read-only Claude specialist (not involved in the design) in an isolated detached
worktree at `b8f8e0aa`; afterwards `git status --short` was empty and the worktree was removed. No final-bank data
opened. The orchestrator supplied provisional DEV numbers (P2preS1 screens, pilot, costs, throughput), which the
reviewer treated as provisional because they were not yet committed.
**This file is the orchestrator's restatement and disposition.** Every finding was checked against the code and
the protocol text. Rule changes are in `PROTOCOL-20260925.md` Amendment 3a and the finalist-rule addendum
(`dev/FINALIST_RULE-20260926.md`, "Addendum").

| # | sev | finding (restated) | verified | disposition |
|---|---|---|---|---|
| Q1-a | MAJOR | UNRESOLVED has no practical default, although §10(c) and the handoff promise one and the goal requires one executable recommendation; the §6.6.3 tie-break used as a default could pick the smaller package without comparability. | yes | **Fixed** (3a.1): terminal default = the costlier package unless it is decisively inferior while the cheaper is decisively inferior on none; eligible; labelled; `UNRESOLVED_WITH_DEFAULT` in `decide.py`, tested. |
| Q1-b | NOTE | The UNRESOLVED stop is a quantified limit only with the bank effect quantified. | yes | **Fixed** (3a.7): bank-effect bound reported beside every contrast. |
| Q1-c | NOTE | The last tie-break key "then cost" could pick the smaller package on a saving below 2× (reached only on an exact N2 tie). | yes | **Accepted, labelled**: unchanged (the handoff's rule for proven equivalence); reported if reached. |
| Q2-a | BLOCK (if frozen now) | Large-slot inputs incomplete (P2preS1 D4d from 1 of 2 draws; L128S1E16 incomplete); the rule script accepted a k with one draw. | yes | **Fixed** (addendum 1): a k counts only on both draws; a package is chosen only when no member is incomplete. The same check found that the Amendment 2 compact choice rested on stale DEV post-hoc files (15 dev1 files computed before their runs finished, e.g. H2S1's second D1 −0.35 draw at k ≥ 5); all development post-hoc files are recomputed with the committed tool (`posthoc_iterations.py` now refreshes stale outputs) and the compact choice is re-checked in the development record. |
| Q2-b | MAJOR | The report/handoff said PET2-pretrained "diverges from k = 3" while it passes the screens at k = 4 and diverges at k = 5. | yes | **Fixed**: per-iteration pull/push tails tabulated for every P2preS1 draw (development record); the step-1 weights grow from k = 3 (max 24–29), reach 334–1,217 at k = 4 on the development tilt and 1.1–5.5 × 10⁵ at k = 5, where the result diverges; wording corrected. |
| Q2-c | MAJOR | N1 checks only truth (push) weights although §6.3 says "all weights"; no stability proxy in the finalist rule. | partly | **Ruled** (3a.3): §4 defines E9, which N1 tests, as final truth-weight tails, so N1 is unchanged; pull tails are recorded and reported. **Added** a development screen S-N1 at K\* (addendum 2) that gates both pull and push with the frozen N1 thresholds, committed before any per-design pull tail was tabulated. The sequence (instruction to gate pull in N1, then the ruling after the tails were seen) is disclosed in 3a.3. |
| Q2-d | MAJOR / BLOCK if PET2 | Cost definition ambiguous (charged vs wall × 1 GPU) and decisive for the cost branch; packing regimes mixed. | yes | **Fixed** (3a.2): charged A100-hours at the declared packing, `analysis/cost_from_receipts.py`, tested. |
| Q2-e | MAJOR | dev2Q configs reused the ids P2preS1/P2scrS1 with a different step-1 policy; no D1 −0.35 rows, so the arm could not pass the rule. | yes | **Fixed** (addendum 4): ids P2preA1/P2scrA1, D1 −0.35 rows added (16 runs) before any dev2Q run started; content-identical configs. |
| rule-code | — | "Applied mechanically" was not literally true: the script computed K\* only. | yes | **Fixed**: `apply_finalist_rule.choose` implements the between-design step, fallback and challenger condition; 8 tests. |
| Q3-a | MAJOR | As coded, both finalists' coverage is required before any ranking output; propose ordering. | yes | **Fixed** (3a.5): provisional ranking (`--provisional`) orders coverage; development-tilt coverage before D4c. |
| Q3-b | MINOR | Look-2 futility. | yes | **Fixed** (3a.6): non-binding projection reported. |
| Q4 (larger contender) | MAJOR | L128S1 at 8 epochs and the compact learning rate; learning curves thin. | yes | **Addressed**: L128S1E16 completed before the freeze; closures for learning-rate magnitude (untuned for every family), events axis (scale fixed by §3) recorded in 3a. |
| Q4 (PET2) | MAJOR | Pretraining contrast at one policy only. | yes | **Fixed** with Q2-e (dev2Q). |
| Q4 (truth step) | MINOR | Truth-step enlargement neither run nor closed. | yes | **Closed** in 3a with the fixed-target evidence. |
| Q4 (response) | NOTE | No response-only library case. | yes | **Justified** in 3a (recovery undefined without a truth change; B4/E8 isolates the response effect). |
| Q4 (B1) | MINOR | B1 anti-conservative. | yes | **Labelled** (3a.9, 2c.5). |
| Q4-a | MAJOR | E4/E5 draw count stated two ways (declaration 8 vs 2c.6's rule); a single sizing over all contrasts would push FINAL to 60. | yes | **Fixed** (3a.4): two sizing groups; library group fixes the D4c/D3 draw count. |
| Q5-a | MINOR | FB receipts hold FB-derived statistics; reading wall times from them is a leak path. | yes | **Fixed** (3a.8): field-restricted reader only. |
| Q5-b | NOTE | Pilot reuse before the freeze and the default rule. | yes | **Disclosed** (3a.1). |
| Q5-c | NOTE | m = 3 with a third finalist. | yes | **Noted**; set by the freeze amendment with the decision set. |
| Q5-d | MINOR | Bank-effect bound not implemented. | yes | **Fixed** (3a.7). |
| Q5-e | NOTE | Topology screen vs oracle, U4 vs pseudodata truth. | yes | **Noted** in the development record. |
| Q5-f | NOTE | N2 tie-break is noisy. | yes | **Labelled** (3a.9). |
| Q5-g | MINOR | `coverage.py` docstring stale. | yes | **Fixed** (`6bc626db`). |

**Found while merging the 3a code (not a reviewer finding):** the §6.5 cost-ratio part had no upper bound, so a
settled ratio below 2 could never fail decisively and §6.5 returned CONTINUE at look 1 (forcing a look 2 for a
settled cost). Fixed (3a.9, `57c82ee9`) with tests. A decisively unresolved look-1 pair is carried and never
reaches the final look, so the 3(v) default applies to any terminal UNRESOLVED (3a.1, `57c82ee9`).

Analysis tests after the 3a code: 100/100 (`analysis/`), 8/8 (`dev/test_apply_finalist_rule.py`).
