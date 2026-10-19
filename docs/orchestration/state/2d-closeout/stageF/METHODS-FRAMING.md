# Methods-paper framing: brief

**Owner:** the paper-tighten lane, as director (Stage F), 2026-10-19, under
[`DECISION-20261019-joseph-methods-first-and-measurement-compute`](../../../DECISION-20261019-joseph-methods-first-and-measurement-compute.md).
**Base:** `main` `a148f22f` (plain-language pass 2, PR #162).

**CITABLE FOR:** the scope, work items, workflow, stopping rule and acceptance of the methods-paper revision.
**NOT CITABLE FOR:**
- any claim (claims are Joseph's; every changed claim is listed for him, provisional until the Ben review);
- any physics-measurement result (those belong to the separate session, [`../../measurement-paper/HANDOFF-20261019.md`](../../measurement-paper/HANDOFF-20261019.md));
- any outward act (J6).

## 1. What the paper becomes

The paper reports what an unbinned unfolding of public MINERvA data achieves and where it fails, and how calibrating
the whole analysis chain allows hypothesis tests with a biased estimator. Concretely:
- **Observed results:** the 2D reproduction; the 3D–5D central values, presented as outputs of a specified estimator
  for qualitative comparison.
- **Demonstrated validation properties:** the regularization bias under plausible truth changes; the failed 5D
  coverage test; the model dependence against the precision target; the null calibration of the joint tests.
- **Interpretive assumptions:** stated once, in one scope statement. These are the hybrid null hypotheses, the
  implemented nuisance and response model (no calorimetric response uncertainty), and the carbon targets of NuWro and
  GiBUU.

The generator tests are conditional tests of the stated hybrid hypotheses under the stated model. They are not
physical exclusions of the generators. The repeated caveats collapse into the scope statement wherever a claim is
already worded conditionally.

## 2. Work items

The source is the outside referee report P20 (GPT-6.1-sol, major comments 1–12) and the triage P7, in
[`plain-language/PLAIN-LANGUAGE-PASS2-REPORTS.md`](plain-language/PLAIN-LANGUAGE-PASS2-REPORTS.md).

| # | item | kind |
|---|---|---|
| M1 | **Framing.** Title, abstract (about 150 words), introduction and conclusions recast around §1. Keep observed results, validation properties and assumptions apart within each paragraph | writing |
| M2 | **Statistics of the tests.** Replace "the Monte Carlo p values remain valid at the number reached" with an argument that holds under the actual stopping rule (`nd-unfolding/s5p_inference.py:89-114`). The director's bound (Holm familywise rate at most 0.89α) is a scratch calculation: it needs an independent derivation and a record before it is used. State whether "calibrated" means nuisance-averaged. Specify the Holm ranking, ties, shared ensembles and unequal stopping counts. Say what the half-simulation pseudo-experiments approximate, and use any null-size check the records hold | analysis; a computation only if no record covers test size |
| M3 | **Show the failures.** One compact bias/closure figure and one coverage figure in the paper, from existing outputs | figures from existing outputs |
| M4 | **Self-contained definitions.** The signal and fiducial definition; W, and the fact that it is fixed by (pT, p∥, q3) at reconstruction level and nearly fixed at truth level, so the result is "five simultaneous observables", not five independent constraints; the available energy's 135 MeV pion convention; a short generative description of one pseudo-experiment; the integrated flux and target normalization | writing |
| M5 | **Why unfold before testing.** An argument, or a comparison, against a test at reconstruction level | writing; a small computation if a comparison is wanted |
| M6 | **Release and placeholders.** The quoted results reproducible from the release; the figures' current inputs (not the obsolete 2D curve). These are the existing checklist items K1–K4 and B1–B5, coordinated with the publication-preparation session | existing items |
| M7 | **Points Joseph and Ben must be able to defend directly:** the null hypotheses, the nuisance ensemble, the stopping rule, the detector assumptions and the physical interpretation. A short brief for the review, not deliverable text | brief |
| M8 | **Claim changes for Joseph.** Every narrowed or added claim is listed with its old and new wording. They include GPT-6.1-sol's §11 overreach points (the low-recoil mechanism, the 52% gap filled by 2p2h, "separates the remaining discrepancy") | list |

## 3. Workflow

1. **X4, framing round.** Both outside models propose a methods-paper outline from the pass-2 text: title, abstract,
   sections, which results become figures, and the scope statement. The director chooses, and records why.
2. **Analysis items** M2–M5, each with its source. A computation goes through a committed grant record.
3. **Rewrite** by Claude writers from the chosen outline. Pass 2's rules still apply: the abstract budget, review in
   both directions, and each number from a record.
4. **Review.**
   - An independent Claude preservation review, in both directions.
   - X5: both outside models write the referee report and outline analysis on the rebuilt PDF, with the same prompts
     as X1 and X3.
   - A triage of every outside major comment: addressed, scoped by §1, deferred to the measurement session, or
     Joseph's decision.
5. **Stopping rule (agreed up front).** At most three X5 rounds. The loop stops when every outside major comment is
   triaged into one of those four classes, or after the third round, whichever is first. Whatever is left goes to
   Joseph with the record. Adversarial reviewers can always find something, so the loop is capped rather than run to
   convergence.
6. Fix, build in a scratch copy, merge. Joseph receives the PDFs, the M8 claim list and the M7 brief.

## 4. Acceptance

1. Four builds: rc 0, both gates PASS, pytest passes, no unresolved references. Pages and abstract word counts are
   reported.
2. The preservation review's MATERIAL findings are fixed and verified.
3. Each number traces to a record. Each changed claim is in the M8 list.
4. The X5 triage table and the before and after against X3 are reported.

**Model caveat:** the integration and preservation review are Claude Opus 5.5 on claude-school. The outside models
reduce single-model bias, and Ben is the first human outside reader.
