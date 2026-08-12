## Resetting the step-1 model AND refreshing the training split together DIVERGES (found 2026-08-09)

**This is a negative result about the estimator, not a failed diagnostic.** It is recorded here because it
is a standing warning against a plausible repair, not because an arm did not work.

The 2026-08-09 step-1 dynamics factorial (`56534116`) ran three interventions against the nominal
warm-model/fixed-split baseline. Individually, each *helps* the fold-forward deficit:

    baseline  warm model, fixed split      push 0.736746   dev -34.46%
    arm 0     warm model, FRESH split           0.873181       -22.32%
    arm 1     COLD model, fixed split           0.968892       -13.81%
    arm 2     COLD model, FRESH split          17.669132     +1471.87%   <-- DIVERGES

Applying both together does not compose — it **diverges by three orders of magnitude**, with the step-1
ratio's `ach/req` reaching `25.07`. Each intervention alone reduces the coupling between successive
iterations (a fresh split decorrelates the training sample; a cold model discards the previous
representation). Applied together they remove essentially all of it, and the iteration loses the anchoring
that kept it bounded. Nothing damps the feedback.

**The practical rule:** these two are **not** independent knobs to be stacked. Any future repair that
touches iteration-to-iteration coupling must be tested *alone* before being combined, and a combination
must be shown bounded rather than assumed additive. "Both fixes help, so both fixes help more" fails
here by **~107x**: the better single intervention leaves `|dev| = 0.1381`, and the combination leaves
`|dev| = 14.7187`.

Cross-reference: the *dominant* term turned out to be neither of these but the dead learning-rate anneal
(previous entry), which took the deficit to −1.17% on its own. See
`FINDING-20260810-criteria-that-answer-a-different-question.md` for why the factorial's own repair
criterion scored that arm as "no information" rather than a pass.

