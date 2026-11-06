# The B0-sentence round (2026-11-06)

**Under** `DECISION-20261106-joseph-b0-reconciliation-sentence.md` (#807). Joseph: "Add it as written".

The round builds the decision's items 1 and 2:
- PR #804's three sentences, verbatim, in paper IV F;
- the two note counterparts.

It changes no result, covariance or claim.

## What changes

**Paper IV F.** After "…so the estimator fails a data-stability requirement of at most 0.3 (median) and 1.0 (maximum)
statistical standard deviations." it adds:
> The training-seed block of Sec. IV A is zero because, in the unfolds we ran, the result is bitwise independent of
> the training seed and of input row order; this is distinct from the sensitivity to rounding-level input changes
> quoted above. That sensitivity enters the reported statistical block by construction: each of its 50 bootstrap
> replicas refits the whole unfolding with its own rounding-level perturbation of the inputs. On the finer joint cells
> (this share was not measured on the 16 reported cells), the rounding spread is about 37% of the statistical variance
> and below a tenth of any total uncertainty (Ref. [14]); the quoted 2.6 statistical standard deviations is the
> largest shift, over 153 quantities (the joint cells, the (E_avail, W) cells and two totals) under two such
> perturbations of the data, not the typical one. A declared probe on simulated pseudo-data of two-fold cross-fitting
> and of two tree regularisations found no variant that met the data-stability requirement, so the estimator is
> unchanged (Ref. [14]).
> <!-- Search: (jitter|rounding) with (R00|R15|sixteen|16 cells|16-cell), git grep over docs/orchestration and nd-unfolding/*.json @ 5551cbbeb013 (the 16-cell hits construct the statistical block from jittered replicas, PROVENANCE-20261031-declaration-v-fd-16-cell-blocks.md :114, or quote the B0 draft; VL155 measures the J cells and FD-STAB s5e's 153 functionals; none measures the rounding share on R00-R15; b0-reconciliation-20261105/DRAFT.md) -->

Three pieces print through macros: "Sec. IV A" through `\ref{sec:cov16}`, "37%" through `\SI{37}{\percent}`, and
"(E_avail, W)" through `$(\Eavail,W)$`. "Ref. [14]" is `Ref.~\cite{AnalysisNote2026}`. `check_round.py` renders the
paper's LaTeX back to this plain form. It then requires it to equal `b0-reconciliation-20261105/DRAFT.md`'s approved
block, printed once, straight after the data-stability sentence.

**The note, sec:fived16-cov (B0-2):**
- *Before:* "C_e sums the statistical bootstrap of configuration (e); …"
- *After:* "C_e sums the statistical bootstrap of configuration (e), 50 replicas, each of which refits the whole unfolding
  with its own rounding-level perturbation of the inputs; …"

**The note, sec_5d.tex's stability paragraph (B0-5).** After "…tests whether the bootstrap contains this variability,
for this candidate only." it adds "A declared probe on simulated pseudo-data of two-fold cross-fitting and of two tree
regularisations found no variant that met the data-stability requirement, so the estimator is unchanged."

The note already stated B0-1 (sec:fived16-cov), B0-3 and B0-4 (sec_5d.tex).

**The float move.** The added sentences moved Limitation 1 across a page break. Table III, floating to the top of the
next page, then split held sentence G1b:paper-g-20 in the blinded rater copy. Table III's environment is moved,
verbatim, to just before the Sec. V heading. It prints on p. 10, with Sec. V B starting on p. 8, and check_held is back
to its 3 known flags (ledger row F1).

## Checks

| check | result | record |
|---|---|---|
| ledger (`check_ledger.py`, step2's checks with base 0700cd7e3) | 6 rows, 13 probes, 3 changed base sentences (FV42, PB249, PB253), 0 failures | LEDGER-CHECK.txt |
| round (`check_round.py`) and its self-test | PASS; 6/6 planted defects caught, each by its intended check | ROUND-CHECK.txt |
| values (`make_values_fived16.py --check`) | PASS | — |
| rater copy, and `check_held.py` on the blinded copy | PASS; the 3 known flags (G1:paper-g-08, G1:paper-s-08, G1b:paper-s-07), after the Table III move | RATER-COPY.txt, CHECK-HELD.txt |
| builds (`build_all.sh`) | paper 13 pp, note 136 pp; SEC4 17/17 | — |
