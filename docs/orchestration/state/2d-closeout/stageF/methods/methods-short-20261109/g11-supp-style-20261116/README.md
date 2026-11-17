# G11: the Supplement in the paper's terms (2026-11-16)

Item G11 of the independent referee read of d30df1ce9 (kept outside the repository; restated, not quoted): the
Supplement still read as the analysis note. director-helper-2 shortlisted the places (at 78a80554f); the director
approved the treatments. Commits c75ed1e3a, 8e849345a and 6160c3016, pushed as 6160c3016 on GATE PASS at that head.

| Id | Treatment |
|---|---|
| G11-1, -2, -3 | Configuration letters outside tab:configs become role names: five-observable and two-observable estimator (the paper's terms); superseded central-value estimator, exact-split cross-check, deterministic purity-based variant, lower-capacity variant (tab:configs's names). The letters stay in tab:configs, labelled as the note's |
| G11-4, -5 | S6's block symbols become the paper's words (paper_body.tex:178) |
| G11-6 | S6's unified-throw procedure and block-sum comparator detail cut to a pointer to the note (see the ruling below) |
| G11-7, -9 | Held: tab:codemap (caption trimmed) and the prior-retention caption's runner options stay until the reproduction package's README holds them (the director: a re-pin row for #981 via limitation-resolver); then cut with a pointer to the deposit |
| G11-8, -12 | The CVUniverse function names and the Keras cross-check move to footnotes, content unchanged |
| G11-10 | GradientBoosting / num_leaves kept (learner settings). "fixed a priori" (an unnamed timing) becomes "No hyperparameter search was performed on data" |
| G11-11 | W1-W3 labels dropped; the shapes are named in words |
| Kept | The three CSV deliverable names |

## Meaning reads (gpt-6.1-sol, high, read-only) and the cut rule

The rule (the director, from the addendum to DECISION-20261113-joseph-note-n4-n5-role.md): detail stays if
removing it would change a reader's understanding of the reported object, its reproducibility, its evidential
independence or its limitations (NEEDED); otherwise it may go if the note or a record holds it (LEDGER).

- read1/ FAIL: S6 dropped limitations; the hyperparameter sentence was narrowed; one letter outside the table.
  All fixed (8e849345a): S6 keeps the joint ensemble, its scope (the superseded estimator's 5D result), why a
  single throw would not do, and what is not stored, quoted or reported for the 2D result.
- read2/ FAIL: "no jitter floor is subtracted" also NEEDED. Restored (6160c3016).
- read3/ FAIL: asks to restore the throw-mean centering (with the separately stored displacement) and the fixed
  estimator seed. **Ruled LEDGER by the director (2026-11-16):** they describe how the note's own test of a
  superseded estimator's 5D result was run and bear on no reported object; the pointer reaches them. Not restored.

Each read directory holds its prompt, the diff, the evidence and the output; the rendered pages are gitignored PNGs.
