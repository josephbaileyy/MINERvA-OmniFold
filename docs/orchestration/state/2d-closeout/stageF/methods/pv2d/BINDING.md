# PV-2D binding: the 2D prior-variation test (2026-10-23)

**By** the paper-tighten lane, as director, under [`ASSIGNMENT.md`](ASSIGNMENT.md) and
`AUTHORIZATION-20261012-2d-closeout-delegation.md` §3 item 2.

**Binds** [`DECLARATION.md`](DECLARATION.md), merged in PR #288 (`082020fc`). The file's sha256 begins
`858116210b2ad808`; the run pin is `3631ea3f`.

## The two deviations

1. **Vertex convention: accepted.** Each vertex is the generator's shape ratio to GENIE 2.12 CV, applied to the Tune v1
   prior. This is the s5p D1–D4 convention, and Joseph's spec says "following the s5p design".
   - The literal form, r = generator/prior, ran from 0.06 to 3.06 on inputs alone.
   - That range is driven by generator MC noise and by artifacts the standalone generators share against the analysis
     MC (no E_ν above 100 GeV, under-sampling at high p∥). Taking the ratio to GENIE CV cancels them to first order,
     which KNOWN_ISSUES 83 itself notes.
   - The report must state the convention in its first paragraph, as "the Tune v1 prior reweighted by each generator's
     shape relative to GENIE CV", and must not describe it as the prior reweighted to the generator itself.
2. **Noise gate: accepted as declared,** before any output. A cell keeps its own ratio if the ratio's statistical
   error is at most 5 %; otherwise it takes its coarse s5p cell's pooled ratio under the same bound; otherwise r = 1.
   The report must give, per vertex, the number of cells and the share of prior weight in each of the three tiers.

## Options

- **(a) The refined arm: admitted.** The adopted 2D result is moving to the refined estimator (RE-2,
  DECISION-20261023 second), so the envelope on that estimator is the one the paper will need.
  - It is four unfolds.
  - The 400/31 override goes into this lane's own copy; RE-2's files are not edited.
  - Its own nominal control reproduces RE-1's refined 2D data unfold D2 (`71ca3e5f…`, `re1/RE1-REPORT-2.md` §3) at
    ≤ 1e-8 relative, the tolerance RE-2 bound for the non-deterministic (a) learner (`re2/RE2-BINDING-J0.md`, A2).
  - It is submitted only after the (a) nominal control passes.
- **(b) The literal reference: not admitted.** The lane recommends against it, and the director agrees.

## Controls and compute

- The nominal control, positive control, integrity checks and readouts are bound as declared.
- If the positive control is not passed, h is reported under the label "positive control not passed" and is not
  evidence, as declared.
- **Cap:** at most **17 CPU node-h** in all: the declared 12, plus 5 for option (a).
- Regular QOS on m3246, each job under 12 h, with the pilot submitted first and alone.
- Stop and report past 1.25× any job's projection. The lane asks the director before exceeding the cap.
- Products go to `$PSCRATCH/pv2d-20261023` only, and every job is ledgered.

The pilot may be submitted once this record is on `main`.
