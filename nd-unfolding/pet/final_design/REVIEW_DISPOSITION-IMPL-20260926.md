# Independent implementation review — dispositions (commit `ec475e7b`)

**Reviewer:** an independent read-only Claude specialist that wrote none of the reviewed code (two forked
sub-reviewers for the job scripts and the PET2 path; their MAJOR findings were re-verified by the lead
reviewer). Isolated detached worktree `MINERvA-OmniFold-pfd-review-impl` at `ec475e7b`; afterwards
`git status --porcelain` was empty (confirmed by the reviewer and re-checked by the orchestrator). No
final-bank run directory was opened. **This file is the orchestrator's restatement and disposition; no
reviewer wording is committed.** Every finding was checked against the code before acceptance.

Tests at review time: analysis 57/57, runner 23 passed/3 failed/2 skipped, pet2 44/1/4, scalar 12/12,
banks 11/11 (the 4 failures: tests used the live protocol, which now releases FB, as their "unreleased" baseline).

| # | sev | finding (restated) | verified | disposition |
|---|---|---|---|---|
| 1 | BLOCK | The coverage scorer multiplied a bootstrap member's prior weight by k although the runner already stores w×k (effective w×k²); the fixture hid it. No bootstrap member had run. | yes (`score_design.py` / `design_inputs.apply_bootstrap`) | **Fixed**: the scorer uses the stored resampled weight once and refuses arrays where it is not `unresampled × k`; fixture built as the runner writes members; refusal test added. |
| 2 | MAJOR | FB access granted by one heading regex; the release's manifests were not enforced. | yes | **Fixed**: row-level `check_release_listing` (config hash, selection, distortion, bootstrap member must be a row of a sha256-pinned `RELEASED-MANIFEST`; Amendment 2b lists them), in both the PET and PET2 runners; tests in both directions incl. a tampered manifest. |
| 3 | MAJOR | Blinding relied on `SCORE=0` whose default is "score". | yes (the queued jobs all carried SCORE=0 — checked) | **Fixed**: the launcher forces `SCORE=0` for FB/RB rows until Amendment 3. |
| 4 | MAJOR | `harvest.sh` would copy FB-derived receipt statistics. | yes | **Fixed**: refuses S4/S5 stages before Amendment 3. |
| 5 | MAJOR | FINAL's development-tilt runs and the library's copy shared a case key (collision or silent pooling into E0). | yes | **Fixed**: library-stage development-tilt runs are keyed `D1_p0.350@library`; E0/E1/E2/U/§6.5 use FINAL only; B1/B2/B4 use the library copy; test added. |
| 6 | MAJOR | E4/E5 sample size, U4/U5 sequential status, m and the library lived only in an uncommitted evidence file. | yes | **Fixed**: frozen `freeze/EVIDENCE_DECLARATION-20260926.json` committed before Amendment 3 (n_required E4/E5 = 8; U4/U5 two-look; m = 2; library). |
| 7 | MINOR | Blinding guard keyed on the directory name only. | yes | **Fixed**: also refuses runs whose receipt records a FB/RB pseudodata bank. |
| 8 | MINOR | Coverage did not check that members are distinct. | yes | **Fixed**: distinct bootstrap identities, same prior and pseudodata rows; duplicate test. |
| 9 | MINOR | B1's Clopper–Pearson treats (case, replicate) units as independent. | yes (protocol definition) | **Reported**: a replicate-cluster companion bound is now computed beside it (report only; the rule is unchanged). |
| 10 | MINOR | Diagnostic `E_avail` binning clipped out-of-range values into edge bins. | yes | **Fixed** (masked); scoring was unaffected. |
| 11 | MINOR | A permanently crashing row is re-claimed by every chain. | yes | **Fixed**: skipped after 3 recorded failures. |
| 12 | MINOR | PET2 recipe audit was advisory. | yes | **Fixed**: a failed audit leaves the run INCOMPLETE and exits non-zero. |

**Checked and found correct by the reviewer** (not re-litigated): bank definitions and the 46/46 digest
reconstruction; disjoint, deterministic, in-bank draws; (stage, replicate)-only salts and seeds (designs paired);
null, products, R1 and R2 transforms consistent between loader, arms and phase_e; bootstrap weights on both legs
before normalization with an unresampled target and per-member seeds; lock held per row; exact-status completion
tests; scorer endpoints, the 3F rule, regions, joint histograms and Amendment 1's edges; decide rules; coverage
interval form; sizing; the finalist rule reproduces `SCREENS-20260926.json`; all 312 final configs and both
manifests regenerate byte-identically.

**Not verifiable by the reviewer:** PET2 resume on GPU; PET2's R1 treatment of muon-fuzz energies relative to the
ours path; runtime behaviour of S4 jobs (none had started); the bash-4 dispatch test.

Tests after the fixes: analysis 59/59; runner + pet2 + banks + scalar 95 passed, 6 skipped.
