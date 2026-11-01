# Step 4 part 2: the independent two-direction review, with dispositions

**The reviewer:** a fresh general-purpose subagent with no stake in the text, read-only.

**What it reviewed:** the caption and primer diff `70eaad8fc..002bd65bc`, against the installed figures, the rendered
note and primer, and the producers.

**The two directions:** truth (each caption statement checked against the figure and the code) and loss (no true
fact dropped).

**The result:** no false colour, marker, legend name or panel label. One Medium and four Low findings. All of them are
fixed in the next commit, apart from finding 5, which concerns a comment.

| # | sev. | finding | disposition |
|---|---|---|---|
| 1 | Medium | Fig. 7's "combined with the uncertainty of the completeness correction" names an error-propagation artifact as an uncertainty. c = hOFInputTruth / hTruthDen is one by construction (`driver_p1.py:772-774`), and ROOT's default `Divide` (`:1219-1224`) still gives it a bin error, which `:1305-1310` adds in quadrature | FIXED: "combined in quadrature with the bin error propagated for the completeness ratio, which is one by construction". The size of the term is not measured here; `xsec.root` is on the cluster |
| 2 | Low | the body paragraph (`sec_results.tex:5`) still said the slices "carry statistical errors only" | FIXED: "carry the same bin errors as the unfolded points" (ledger C2, RE1) |
| 3 | Low | "statistical uncertainty of the reweighted simulated sample" may be read as the measurement's statistical uncertainty. The bars are simulation-sample weight statistics and hold no data fluctuation | FIXED in both captions: "the weight statistics of the reweighted simulated sample … neither the data's statistical uncertainty nor the reported covariance" |
| 4 | Low | both series also have horizontal half-bin bars, and "error bars" described only the vertical ones | FIXED: "The vertical error bars …"; Fig. 7 adds "Horizontal bars span the bins." |
| 5 | Low, comment | `primer_body.tex:156`'s old comment still cites "color red" | KEPT. The appended restyle note in the same comment corrects it. Comments are not printed, and the old part is its own history |
<!-- absence-ok: row 1 scopes this round, not a result: the completeness term's size needs the cluster's xsec.root, which this round did not read -->

**Checks that passed** (the reviewer's):
- Fig. 7: the published bars are √diag of `StatOnlyCovariance`, and the projections carry no published series;
- Figs. 9 and 10: no published series, and the same bin errors;
- Fig. 13: red circles, black squares, a blue solid step with the full legend name, and no error bars ("Uncertainties
  are not drawn" is true);
- Fig. 14: "(a) This work" and "(b) Published data" print;
- the primer's Tune curve is blue;
- no true fact was lost;
- no other caption for the eleven figures names a now-false colour, marker, line style or legend name;
- the installed `figures/*.pdf` equal `figs-a2/`, 11 of 11.
