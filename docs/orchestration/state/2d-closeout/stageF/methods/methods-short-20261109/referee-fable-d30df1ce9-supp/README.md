# Supplement accuracy fixes from the independent referee read of d30df1ce9 (2026-11-16)

The director relayed eight Supplement items (A1, A2, B8, D6, D7, D8, D9, F5) from an independent referee read of
draft d30df1ce9, which is kept outside the repository. The items are restated here, not quoted.

| Item | What was wrong | Change (commit) |
|---|---|---|
| A1 | Table S1 said the publication had "the same exposure" | Publication's 10.61e20 POT stated, from arXiv:2106.16210 abstract and section II (cbd405125) |
| A2 | S4.3 called the prior-data difference "mainly normalization" beside a pT-dependent ratio, and offered integral checks as support for n=5 | Shape and normalization; integral checks named as such; the 1.54 % RMS per-bin shape difference (new key status-iter-shape-rms, the note's sec_validation.tex:204) and the one-learner chi2/ndf added; neither establishes shape convergence (cbd405125, e1bd8dc8c, d6a886361) |
| B8 | S6.2's statement about the published iteration choice and uncertainty was unverified | Checked against arXiv:2106.16210v2 sections IV and V; replaced by what those sections say (cbd405125) |
| D6 | S4.1 step 3 still divided by the completeness c | Removed, as from the paper's equation (cbd405125) |
| D7 | S7's kappa paragraph: an unused classification, a data value outside its range | Paragraph removed (cbd405125) |
| D8 | S10 named a withheld rule | Name removed; the disclosure stays (cbd405125) |
| D9 | Two 1G-1M p-parallel chi2 values (34.4, 34.8) without saying what differs | Same raw shift, two covariances (VL175, S5's other blocks) (cbd405125) |
| F5 | Figure S2's axes are bin indices | Not changed: a hash-pinned restyle figure shared with the note (make_figures.sh:264); listed for the figure lane |

Also: the published Stay Positive reference in technote.bib (f33f091c0, from de419684f); the push gate tracked
(22ff217ad) and its holddiff pattern fixed (ced3544d7).

Meaning reads (gpt-6.1-sol, high, read-only): read1/ FAIL (the chi2/ndf sentence's configuration and scope),
fixed in d6a886361; read2/ PASS. Each holds its prompt, the diff, the evidence (records.txt) and the output; the
rendered pages it read are gitignored PNGs.
