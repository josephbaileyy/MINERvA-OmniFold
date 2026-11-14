# History restructure, §10 (sec_fived16.tex): cut log

**Under** DECISION-20261113-joseph-note-n4-n5-role.md, the addendum recording Joseph's go of 2026-11-13, and the
director's ruling (A) of 2026-11-14 (recorded in sec_5d.md): "declared" is the project's word for "specified before it
ran". Each timing use is written out with its object, taken from its records, and each method use becomes "specified".

**The rule, verbatim as adopted:** history stays in the note only if removing it would change a reader's understanding
of the reported object, its reproducibility, its evidential independence or its limitations. Everything else goes to
the ledger. Each "fixed before" names its object, and "declared" alone is replaced.

**Referee:** for §10 it gave "10–20%, Compress / appendix, especially §§10.4–10.5. Keep the data-informed run-period
term, failed controls, algorithm dependence, and both unsuccessful coverage attempts."

**Base:** `docs/analysis-note/sec_fived16.tex` at `aa0ff83f5`. Line numbers are the base's. Records are under
`docs/orchestration/state/measurement-paper/5d-community-20261024/` unless a path is given, and each date is the
record's first commit.

**Outcome for §10:** ten wording changes, all timing or method uses of "declared" and "in advance". No passage is cut.
§§10.4–10.5 hold what the referee lists to keep: the run-period term, the failed controls, the algorithm dependence and
both unsuccessful coverage attempts, with the earlier calibrated-term route as the limitation on $C_{\mathrm{model}}$.
Both coverage attempts and the earlier route go to App. I.

## The changes

| id | base line | old text | new text | ledger home and the records for the object |
|---|---|---|---|---|
| T1 | :72 | "The rule, fixed in advance, is that the results agree if …" | "The rule, fixed before the comparison was made, is that …" (the wording of :47) | aa0ff83f5:sec_fived16.tex:72. FD-GENCMP-X-DECLARATION.md:27-28 and :258-261, the rule (a293dc3de, 2026-11-01 22:07 -0800); FD-GENCMP-X-BINDING.md (9c636cb61, 22:43); FD-GENCMP-X-REPORT.md (acd062947, 2026-11-02 09:06) |
| T2 | :244 | "As fixed in advance, the six power alternatives built on that correction are therefore descriptive" | "As fixed before any of the tests was graded, …" (the object of :203) | aa0ff83f5:sec_fived16.tex:244. FD-F0-DECLARATION.md:210, control 7: "On FAIL, row 6 is printed as 'descriptive and ungraded'" (7d7dac1d3, 2026-10-25 13:43 -0700); FD-F0-REPORT.md (28c4870f4, 15:04); FD-F0b-DECLARATION.md:44-45 carries it ("row 6 stays descriptive") |
| T3 | :279 | "A coverage test at these two tunes, declared in advance for the covariance without the run-period block, …" | "A coverage test at these two tunes, specified before any pseudo-experiment was generated, for the covariance without the run-period block, …" (the rule's own object, "before generating the pseudo-experiments"; a first wording, "before any of its stages ran", was failed by the read: the protocol was declared and bound in stages) | aa0ff83f5:sec_fived16.tex:279. FD-1B-DECLARATION.md, "the coverage protocol, fixed before any toy, and the stages that follow" (fcdc1afed, 2026-10-30 09:31 -0700), which fixes the matrix 1B tests; FD-1B-STAGE1-REPORT.md (c0ce80981, 16:59); FD-1B-STAGE2-DECLARATION.md (2026-10-31 10:44) and FD-1B-STAGE2-REPORT.md (1a4815a8a, 18:38), the gate |
| T4 | :287 | "its first stage stopped under a fail-closed rule declared in advance" | "… under a fail-closed rule fixed before that stage ran" (as §9's F3) | aa0ff83f5:sec_fived16.tex:287. FD-1B-STAGED-AMENDMENT-2.md:204 at its first commit 2b8859efc (2026-11-03), unchanged at :222 @ b3f27fab3; the stage's receipt, job 60893641 (receipt.txt @ b3f27fab3, connect 2026-11-06T08:15Z) |
| T5 | :304 | "A comparison declared before it ran" | "A comparison specified before it ran" | aa0ff83f5:sec_fived16.tex:304. REF-G1-DECLARATION.md (716e86df5, 2026-11-04 15:07 -0800; :5 "declared, audited and bound before it runs"); REF-G1-BINDING-1.md (1c3a1bda3, 22:01); OUTCOME-20261106-ref-g1-r1-differ.md (ed27964aa, 2026-11-05 21:54) |
| T6 | :455 | "compared cell by cell with the combination under a rule fixed in advance" | "… under a rule fixed before the comparison was made" | aa0ff83f5:sec_fived16.tex:455. FD-GENCMP-DECLARATION.md §5 :317, the rule (0aa1ab93d, 2026-11-01 10:50 -0800); FD-GENCMP-BINDING.md (90ba8a8ac, 11:52); FD-GENCMP-REPORT.md and fd/gencmp/readout/native.json (e87dbda54, 13:05) |
| T7 | :455 | "A diagnostic that was not a declared test" | "A diagnostic that was not a test specified before it ran" | as T6: the probe chunk is outside the declaration's rule |
| M1 | :281 | "under this declared swap" | "under this specified swap" | a method use: no timing |
| M2 | :287 | "if any declared draw", "of the … declared draws", "the declared composition of the natures" | "specified draw", "specified draws", "the specified composition" | as M1 |
| M3 | :380 | "($\alpha$ of the declared grid;" | "($\alpha$ of the specified grid;" | as M1 |

## The gate investigation moved to the N-D appendix (the director's go of 2026-11-14, after 1fcb3713d)

| id | base line (1fcb3713d) | old text | new text | ledger home |
|---|---|---|---|---|
| G1 | :281–285, with the source comments :292–296 | three paragraphs: "For the interaction uncertainties, a later investigation at the nominal truth found that the gate compared unlike objects. …", "This concerns the test; it neither validates nor undermines the reported interaction block, …" and "A later pre-check of those two groups at the nominal truth found that, …" | moved verbatim to `app_statmethods_nd.tex` as `\subsection{Investigation of the gate of the sixteen-cell coverage test}` (`sec:cov1b-gate`), after an opening paragraph that restates :279, so that the moved text keeps the antecedents it had in §10: "The coverage test at the two tunes for the covariance without the run-period block (\S\ref{sec:fived16-fd}) was stopped before any coverage pseudo-experiment ran." followed by :279's gate sentence verbatim ("At one of its gates, the ratio of each cell's uncertainty reproduced through the pseudo-experiments to that of the drawn covariance lay outside … in \fvval{cov1b-ncells-out} of the 16 cells, ranging from … to ….") and "This subsection gives the investigation of that gate." (A first opening sentence, without the test's identity or the gate's ratio, was failed by the first read: §10.5 holds two coverage tests at the two tunes, and the moved text's "the gate's departure" then had only kappa as an antecedent.) In §10, :279 keeps the gate's result (outside the window in \fvval{cov1b-ncells-out} of the 16 cells) and is followed by the pointer "A later investigation of that gate at the nominal truth, which concerns the test and neither validates nor undermines the reported interaction block, and a pre-check of the flux and detector uncertainties are in App.~\ref{sec:cov1b-gate}." | no text leaves the note; 1fcb3713d:sec_fived16.tex:281-296 |

The move is checked byte for byte: the base's lines 281–285 and 292–296 appear contiguous and unchanged in the
appendix, and none remains in §10. The appendix's opening paragraph, which lists its contents, is unchanged, as §5's
V2 left App. A's. `numdiff.py` over §10 plus the N-D appendix, base against new: no number, key or macro removed or
added.

**G1's meaning read:** pass 1 (a fresh Claude subagent, claude-opus-5-5, blind, while codex-school refused for its
usage limit) FAIL on the opening sentence and the antecedent it left (above), reads/sec_fived16-g1-pass1.txt; pass 2
(codex-school gpt-6.1-sol) PASS, reads/sec_fived16-g1-pass2.txt. Prompt: reads/sec_fived16-g1-prompt.txt.

**F3's pointer in §9:** the director asked to retarget sec_5d.tex:237's "(\S\ref{sec:fived16-fd})" at the subsection
that states the stop. That is already §10.5: `sec:fived16-fd` opens at :201, and the next subsection opens at :302, so
:287 lies inside it. No change.

**Kept as they are:**
- **:47** "The rule was fixed before the comparison was made", **:191** "fixed before any playlist result was read" and
  **:203** "fixed before any of the tests was graded against them": each names its object.
- **:182** "the inverted dimension $p$ equals the number of cells and is fixed in advance": a property of the
  construction (no truncation), not when a test was specified.
- **:110–113, the earlier route to a calibrated model term** and its two tests: the reason the coverage of
  $C_{\mathrm{model}}$ is not validated, a limitation. In App. I as D11.
- **:277** "Rerunning the tests with the two tunes added reproduces every earlier fake-data result exactly": a
  reproducibility statement.
- **:279–281, the coverage test at the two tunes and the later investigation of its gate**, and **:287, the staged
  test's stop**: the two unsuccessful coverage attempts the referee keeps, with their limits ("The stop concerns … not
  the estimator's coverage"; "neither validates nor undermines").
- **The run-period block** (§10.3, :185 onward), data-informed: the referee's keep list.

**Numbers and keys:** `numdiff.py` on the base and new files, comments stripped: none removed, none added; value keys
and macros unchanged.

## The Development-history appendix: new rows

| row | from | content |
|---|---|---|
| D11 | :110–115 | the earlier route to a calibrated model term with validated coverage: it did not pass its first two tests (Stage 0 failed its first part on both sets of cells and stopped; the reconstruction-information test, incomplete, had no configuration meet its residual requirement) and was not pursued further; $C_{\mathrm{model}}$ was then adopted unscaled, and its coverage is not validated |
| D12 | :279 | the coverage test at the two tunes for the covariance without the run-period block: stopped before any coverage pseudo-experiment ran, at the gate whose ratio lay outside the window in \fvval{cov1b-ncells-out} of the 16 cells (a first wording without the count was failed by the read as widening the failure to every cell) |

D10 (from §9) is the staged test of :287. "Already seen" is "--" for both, because §10 does not state what had been
seen.

## Disclosure checklist

| disclosure | in §10? | survives |
|---|---|---|
| the 2D adoption after the published distance was known | no (§3) | — |
| the post-observation run-period term | yes, §10.3: the run-period groups differ by more than their scatter, with the cause not known (:187), and the playlist study's readings were fixed before any playlist result was read (:191) | ✓ unchanged |
| reused samples and seeds | no change: the fake-data truths "are not held-out truths" (:203) | ✓ unchanged |
| the invalid q3 deformation | no (§9) | — |
| the stopped coverage tests | yes: :279 and :287 | ✓ unchanged in substance (T3, T4 name the objects), and in D10 and D12 |
| the data-informed joint-test design and budget extension | no (§11) | — |
| the missing response uncertainty | yes: what $C_{\mathrm{resp}}$ does not cover (:119) | ✓ unchanged |
| the generator-sample problems | in part: :455, the native CH NuWro check and the probe chunk's cross-section offset (the rest is App. C) | ✓ unchanged (T6, T7 name the objects) |
| the target-correction sensitivity | no (§11) | — |
| also found: the failed control 7 and the six power alternatives made descriptive (:244) | yes | ✓ unchanged (T2 names the object) |
| also found: $C_{\mathrm{model}}$ adopted unscaled after the calibrated route failed (:110) | yes | ✓ unchanged, and in D11 |

## Unreleased support

No site in §10 changes its citation. `UNRELEASED-SUPPORT.md` is unchanged.

## Meaning read (codex-school gpt-6.1-sol, high, read-only; reads/sec_fived16-prompt.txt, the form of §9's pass 3, with reads/sec_fived16-records.txt)

- **Pass 1:** OVERALL FAIL.
  - Question 1 failed T3 ("before any of its stages ran": the protocol was declared and bound in stages, the stage-2
    declaration after the stage-1 report) and D12 (without the count, it widened the gate's failure to every cell).
  - Everything else passed. Nothing was removed, and no disclosure was lost.
  - reads/sec_fived16-pass1.txt.
- **Pass 2, T3 and D12 fixed as above:** OVERALL PASS, with no FAILs. T1–T7, M1–M3, D11 and D12 pass; no NEEDED item
  lost; no disclosure lost. reads/sec_fived16-pass2.txt.
