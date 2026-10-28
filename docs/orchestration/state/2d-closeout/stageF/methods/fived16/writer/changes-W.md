# Changes W: per edit, before, after, group and scope-sites.tsv rows

Sites are 1-based data-row numbers of scope-sites.tsv. Groups: A-F as in outline.md §2; G = Stage G; AMB-* = the ambiguous kind; list = a list of uses or products that now names the sixteen-cell result.

## RS-1 (result_status_rows.tex; group A/F/G; sites 20, 21, 24)

Before:

```tex
5D: LightGBM, five iterations, purity subtraction} & \rsB{One scalar-5D covariance, used although it has not met the validation criteria set before it was built}
```

After:

```tex
5D: LightGBM, five iterations, purity subtraction (configuration (a))} & \rsB{The five-axis covariance of the configuration-(a) 5D central value, used although it has not met the validation criteria set before it was built}
```

## RS-2 (result_status_rows.tex; group G; sites 24)

Before:

```tex
the covariance's four measured limitations apply. No covariance-based generator significance.} \\
```

After:

```tex
the covariance's four measured limitations apply. No generator significance based on this covariance (sixteen-cell comparison: \S\ref{sec:fived16-gen}).} \\
\addlinespace
\rsA{5D, sixteen cells: deterministic LightGBM, five iterations, refined negative-weight subtraction (configuration (e)); \S\ref{sec:fived16}} & \rsB{The reported covariance on the sixteen cells (\S\ref{sec:fived16-cov})} & \rsC{Fake-data study (\S\ref{sec:fived16-fd}).} & \rsD{Comparison with generator predictions on the sixteen cells (\S\ref{sec:fived16-gen}).} \\
```

## ES-1 (sec_execsummary.tex; group AMB-regbias; sites 15)

Before:

```tex
The high-$\Eavail$, high-$W$ region carries the largest regularization bias.
```

After:

```tex
The high-$\Eavail$, high-$W$ region carries the largest regularization bias measured in \S\ref{sec:5d}.
```

## ES-2 (sec_execsummary.tex; group list; sites —)

Before:

```tex
\S\ref{sec:val-fiveaxis}, \S\ref{sec:eavailw-adopted} and \S\ref{sec:joint5d}.}
```

After:

```tex
\S\ref{sec:val-fiveaxis}, \S\ref{sec:eavailw-adopted}, \S\ref{sec:fived16} and \S\ref{sec:joint5d}.}
```

## ES-3 (sec_execsummary.tex; group AMB-estimator/F; sites 17, 19)

Before:

```tex
the five-dimensional estimator's regularization bias (\S\ref{sec:val-departure}) and purity-subtraction bias (\S\ref{sec:val-negweight}); five-dimensional intervals and their coverage (\S\ref{sec:gbdt-model-dependence}, \S\ref{sec:coverage-5d}); the five-dimensional covariance (\S\ref{sec:eavailw-adopted});
```

After:

```tex
the five-dimensional estimator's regularization bias (\S\ref{sec:val-departure}) and the purity-subtraction bias of configurations (a) and (c) (\S\ref{sec:val-negweight}); five-dimensional intervals and their coverage (\S\ref{sec:gbdt-model-dependence}, \S\ref{sec:coverage-5d}); the five-axis covariance of the configuration-(a) central value (\S\ref{sec:eavailw-adopted});
```

## IN-1 (sec_intro.tex; group A/B; sites 27, 28)

Before:

```tex
Background subtraction is unbinned too in the 2D result and its covariance and in the 3D and 4D central values, which use refined negative-weight subtraction (\S\ref{sec:method-algo}). The five-dimensional central value and its covariance, and the extended-fiducial value, use the binned purity weight,
```

After:

```tex
Background subtraction is unbinned too in the 2D result and its covariance, in the 3D and 4D central values and in the sixteen-cell five-dimensional result (\S\ref{sec:fived16}), which use refined negative-weight subtraction (\S\ref{sec:method-algo}). The configuration-(a) five-dimensional central value and its five-axis covariance, and the extended-fiducial value, use the binned purity weight,
```

## IN-2 (sec_intro.tex; group list; sites 29)

Before:

```tex
The validation and uncertainty of the five-dimensional estimator (\S\ref{sec:5d}) and the calibrated generator tests built on it (\S\ref{sec:joint5d}) follow these central values.
```

After:

```tex
The validation and uncertainty of the five-dimensional estimator (\S\ref{sec:5d}), the sixteen-cell result (\S\ref{sec:fived16}) and the calibrated generator tests built on the estimator (\S\ref{sec:joint5d}) follow these central values.
```

## IN-3 (sec_intro.tex; group AMB-centralonly; sites 30)

Before:

```tex
Above two dimensions the results are central values without intervals of validated coverage (\S\S\ref{sec:3d}--\ref{sec:5d}).
```

After:

```tex
Above two dimensions the results are central values without intervals of validated coverage (\S\S\ref{sec:3d}--\ref{sec:5d}); the sixteen-cell result also has total uncertainties, whose coverage is not validated (\S\ref{sec:fived16}).
```
<!-- absence-ok: quotes or summarizes the note's printed text, before or after this PR, as the writer's record; not a new absence claim -->

## IN-4 (sec_intro.tex; group F/list; sites 32)

Before:

```tex
The five-axis covariance used in this note & \S\ref{sec:eavailw-construction} \\

```

After:

```tex
The five-axis covariance of the configuration-(a) central value & \S\ref{sec:eavailw-construction} \\
Sixteen-cell five-observable result & \S\ref{sec:fived16} \\

```

## ME-1 (sec_method.tex; group A/B; sites 33)

Before:

```tex
The quoted 2D result and its covariance and the 3D and 4D central values use its refined form; every other quoted cross section and uncertainty, including the 5D central value and the extended-fiducial value, uses the binned correction.
```

After:

```tex
The quoted 2D result and its covariance, the 3D and 4D central values and the sixteen-cell 5D result (\S\ref{sec:fived16}) use its refined form; every other quoted cross section and uncertainty, including the configuration-(a) 5D central value and the extended-fiducial value, uses the binned correction.
```

## ME-2 (sec_method.tex; group B; sites 33)

Before:

```tex
the generator tests and the 3D and 4D central values; and (f)
```

After:

```tex
the generator tests, the 3D and 4D central values and the sixteen-cell result; and (f)
```

## ME-3 (sec_method.tex; group B; sites 35, 36)

Before:

```tex
It gives the 3D and 4D central values (\S\ref{sec:3d}).
```

After:

```tex
It gives the 3D and 4D central values (\S\ref{sec:3d}) and the sixteen-cell five-dimensional result (\S\ref{sec:fived16}).
```

## ME-4 (sec_method.tex; group A; sites 37)

Before:

```tex
The five-dimensional central value and its covariance use configuration~(a):
```

After:

```tex
The five-dimensional central value of \S\ref{sec:eavailw} and its five-axis covariance use configuration~(a):
```

## ME-5 (sec_method.tex; group B; sites 38)

Before:

```tex
A refined five-dimensional data unfold exists (configuration~(e)), but it is not the quoted central value, and no covariance has been built for it.
```

After:

```tex
A refined five-dimensional data unfold exists (configuration~(e)); it gives the sixteen-cell result, whose reported covariance on the sixteen cells is described in \S\ref{sec:fived16-cov}.
```

## ME-6 (sec_method.tex; group A; sites 39)

Before:

```tex
\pcell{0.30\textwidth}{five-observable central value and covariance (\S\ref{sec:eavailw-adopted});
```

After:

```tex
\pcell{0.30\textwidth}{five-observable central value of \S\ref{sec:eavailw} and its five-axis covariance (\S\ref{sec:eavailw-adopted});
```

## ME-7 (sec_method.tex; group B; sites 40)

Before:

```tex
\pcell{0.30\textwidth}{three- and four-observable central values (\S\ref{sec:3d}); generator shapes held out of development;
```

After:

```tex
\pcell{0.30\textwidth}{three- and four-observable central values (\S\ref{sec:3d}); sixteen-cell five-observable result (\S\ref{sec:fived16}); generator shapes held out of development;
```

## SY-1 (sec_systematics.tex; group AMB-F; sites 41)

Before:

```tex
The 5D result uses the strict joint ensemble and matched-endpoint comparator.
```

After:

```tex
The configuration-(a) 5D result uses the strict joint ensemble and matched-endpoint comparator.
```

## SY-2 (sec_systematics.tex; group AMB-F; sites 42)

Before:

```tex
In the five-axis covariance the per-source decomposition
```

After:

```tex
In the five-axis covariance of the configuration-(a) central value the per-source decomposition
```

## SY-3 (sec_systematics.tex; group AMB-F; sites 43)

Before:

```tex
the lateral-band block of the five-axis covariance used in this note;
```

After:

```tex
the lateral-band block of the five-axis covariance of the configuration-(a) central value;
```

## SY-4 (sec_systematics.tex; group AMB-F; sites 45)

Before:

```tex
The ML term $C_{\mathrm{ML}}$ of the five-axis covariance used in this note
```

After:

```tex
The ML term $C_{\mathrm{ML}}$ of the five-axis covariance of the configuration-(a) central value
```

## SY-5 (sec_systematics.tex; group AMB-F; sites 46)

Before:

```tex
The five-axis covariance used in this note is a separate, later build
```

After:

```tex
The five-axis covariance of the configuration-(a) central value is a separate, later build
```

## SY-6 (sec_systematics.tex; group AMB-F; sites 48, 49)

Before:

```tex
and the covariance \emph{used in this note} by \SI{0.18}{\percent}
```

After:

```tex
and the five-axis covariance \emph{of the configuration-(a) central value} by \SI{0.18}{\percent}
```

## SY-7 (sec_systematics.tex; group AMB-F; sites 49)

Before:

```tex
and the 5D covariance is not transferred to them.
```

After:

```tex
and the configuration-(a) 5D covariance is not transferred to them.
```

## VA-1 (sec_validation.tex; group C; sites 51)

Before:

```tex
  regularization bias outside every quoted uncertainty \\
```

After:

```tex
  regularization bias outside every uncertainty quoted for the configuration-(a) central value (sixteen-cell result: \S\S\ref{sec:fived16-cov}, \ref{sec:fived16-fd}) \\
```

## VA-2 (sec_validation.tex; group AMB-F; sites 52)

Before:

```tex
within total uncertainty in 20 of 42 $(\Eavail,W)$ cells
```

After:

```tex
within the configuration-(a) total uncertainty in 20 of 42 $(\Eavail,W)$ cells
```

## VA-3 (sec_validation.tex; group AMB; sites 53)

Before:

```tex
which remain the main five-dimensional recovery evidence.
```

After:

```tex
which remain the main five-dimensional recovery evidence of \S\ref{sec:5d}.
```

## TD-1 (sec_3d.tex; group AMB-F; sites 57)

Before:

```tex
against the projection of the five-dimensional covariance used in this note,
```

After:

```tex
against the projection of the five-dimensional covariance of the configuration-(a) central value,
```

## EW-1 (sec_eavailw.tex; group AMB-marginal; sites 62)

Before:

```tex
The five-dimensional unfolding in $(\pT,\pPar,\Eavail,q_{3},W)$ passes the marginalization checks
```

After:

```tex
The configuration-(a) five-dimensional unfolding in $(\pT,\pPar,\Eavail,q_{3},W)$ passes the marginalization checks
```

## EW-2 (sec_eavailw.tex; group G; sites 66)

Before:

```tex
no compatibility metric is quoted, for the reason given in \S\ref{sec:eavailw-adopted}, item~1.
```

After:

```tex
no compatibility metric based on the configuration-(a) covariance is quoted, for the reason given in \S\ref{sec:eavailw-adopted}, item~1 (comparison on the sixteen cells: \S\ref{sec:fived16-gen}).
```

## FD-1 (sec_5d.tex; group F/list; sites 69)

Before:

```tex
and the status of the one five-axis covariance used in this note (\S\ref{sec:eavailw-construction}). The calibrated generator tests built on a variant of this estimator follow in \S\ref{sec:joint5d}.
```

After:

```tex
and the status of the five-axis covariance of the configuration-(a) central value (\S\ref{sec:eavailw-construction}). The sixteen-cell result of configuration (e) follows in \S\ref{sec:fived16}, and the calibrated generator tests built on a variant of this estimator in \S\ref{sec:joint5d}.
```

## FD-2 (sec_5d.tex; group AMB-F; sites 71)

Before:

```tex
\pcell{0.23\textwidth}{compared with the quoted total $\sigma$}
```

After:

```tex
\pcell{0.23\textwidth}{compared with the configuration-(a) total $\sigma$}
```

## FD-3 (sec_5d.tex; group AMB-F; sites 72)

Before:

```tex
Relative to these cells' quoted total uncertainty, the bias is
```

After:

```tex
Relative to these cells' total uncertainty in the configuration-(a) covariance, the bias is
```

## FD-4 (sec_5d.tex; group A; sites 74)

Before:

```tex
Negative-weight subtraction is not used for the quoted five-dimensional central value.
```

After:

```tex
Negative-weight subtraction is not used for the configuration-(a) five-dimensional central value; the sixteen-cell result uses it (\S\ref{sec:fived16}).
```

## FD-5 (sec_5d.tex; group C; sites 76)

Before:

```tex
The $\Eavail$ and $q_3$ residuals, a regularization (unfolding-model) bias of the estimator, enter no quoted uncertainty.
```

After:

```tex
The $\Eavail$ and $q_3$ residuals, a regularization (unfolding-model) bias of the estimator, enter no uncertainty quoted for the configuration-(a) central value. For the sixteen-cell result (\S\ref{sec:fived16}), the model term of its reported covariance is the change in the unfolded data when the prior is reweighted to each generator (GENIE + MEC, NuWro, GiBUU; \S\ref{sec:fived16-cov}); \S\ref{sec:fived16-fd} gives the fake-data study's measured comparison of the estimator's bias with the reported covariance.
```

## FD-6 (sec_5d.tex; group AMB-F; sites 80)

Before:

```tex
within the quoted total uncertainty in 20 of the 42 $(\Eavail,W)$ cells.
```

After:

```tex
within the configuration-(a) total uncertainty in 20 of the 42 $(\Eavail,W)$ cells.
```

## FD-7 (sec_5d.tex; group B; sites 81)

Before:

```tex
No estimator or uncertainty from this assessment is used for the quoted results.
```

After:

```tex
This candidate is configuration (e), which gives the sixteen-cell result (\S\ref{sec:fived16}); no uncertainty from this assessment is used for a quoted result.
```

## FD-8 (sec_5d.tex; group E; sites 84)

Before:

```tex
With the study's precision targets and computing budget, no five-dimensional measurement with total uncertainties was constructed (next paragraph).
```

After:

```tex
With the study's precision targets and computing budget, none of its reporting definitions (RD1--RD3, next paragraph) met a precision target. The sixteen-cell result is the same H2 grid after a purity merge of its supported boxes, with total uncertainties (\S\ref{sec:fived16-result}).
```

## FD-9 (sec_5d.tex; group AMB-E; sites 85)

Before:

```tex
The five-dimensional measurement study assessed three reporting definitions
```

After:

```tex
The five-dimensional precision study assessed three reporting definitions
```

## FD-10 (sec_5d.tex; group AMB-E; sites 87)

Before:

```tex
No reporting definition can meet these precision targets
```

After:

```tex
None of the three reporting definitions can meet these precision targets
```

## FD-11 (sec_5d.tex; group AMB-F; sites 95)

Before:

```tex
\subsection{The five-axis covariance used in this note and its $(\Eavail,W)$ projection}
```

After:

```tex
\subsection{The five-axis covariance of the configuration-(a) central value and its $(\Eavail,W)$ projection}
```

## JT-1 (sec_joint.tex; group AMB-F; sites 103)

Before:

```tex
They do not use, and do not validate, the five-axis covariance used elsewhere in this note (\S\ref{sec:eavailw-adopted}).
```

After:

```tex
They do not use, and do not validate, the five-axis covariance of the configuration-(a) central value (\S\ref{sec:eavailw-adopted}).
```

## SU-1 (sec_summary.tex; group AMB-regbias; sites 108)

Before:

```tex
The regularization bias is largest in the high-$\Eavail$, high-$W$ region (\S\ref{sec:eavailw-map}).
```

After:

```tex
The regularization bias measured in \S\ref{sec:5d} is largest in the high-$\Eavail$, high-$W$ region (\S\ref{sec:eavailw-map}).
```

## SU-2 (sec_summary.tex; group D; sites 109)

Before:

```tex
The quoted five-dimensional central value keeps this bias, and no quoted uncertainty includes it. The refined negative-weight subtraction largely removes it.
```

After:

```tex
The configuration-(a) five-dimensional central value keeps this bias, and no uncertainty quoted for it includes the bias. The refined negative-weight subtraction, which the sixteen-cell result uses (\S\ref{sec:fived16}), largely removes it.
```

## SU-3 (sec_summary.tex; group C; sites 112)

Before:

```tex
No quoted uncertainty includes this residual bias, which is interpreted as regularization bias (\S\ref{sec:val-departure}).
```

After:

```tex
No uncertainty quoted for the configuration-(a) central value includes this residual bias, which is interpreted as regularization bias (\S\ref{sec:val-departure}). For the sixteen-cell result (\S\ref{sec:fived16}), the model term of its reported covariance is the change in the unfolded data when the prior is reweighted to each generator (GENIE + MEC, NuWro, GiBUU; \S\ref{sec:fived16-cov}); \S\ref{sec:fived16-fd} gives the fake-data study's measured comparison of the estimator's bias with the reported covariance.
```

## SU-4 (sec_summary.tex; group AMB-centralonly/E; sites 113, 114)

Before:

```tex
Above two dimensions the results are central values without intervals of validated coverage. No five-dimensional measurement with total uncertainties was constructed (\S\ref{sec:gbdt-model-dependence}).
```

After:

```tex
Above two dimensions the results are central values without intervals of validated coverage; the sixteen-cell result also has total uncertainties, whose coverage is not validated (\S\ref{sec:fived16}). None of the precision study's reporting definitions (RD1--RD3) met a precision target (\S\ref{sec:gbdt-model-dependence}); the sixteen-cell result is the precision study's H2 grid after a purity merge of its supported boxes (\S\ref{sec:fived16-result}).
```
<!-- absence-ok: quotes or summarizes the note's printed text, before or after this PR, as the writer's record; not a new absence claim -->

## SU-5 (sec_summary.tex; group F/G; sites 116, 117)

Before:

```tex
The one five-dimensional covariance used in this note does not meet its specification's acceptance criteria. Two companion covariances, built at different estimator seeds, show a seed sensitivity above the limit set before production, so no covariance-based significance is quoted (\S\ref{sec:eavailw-adopted}).
```

After:

```tex
The five-axis covariance of the configuration-(a) central value does not meet its specification's acceptance criteria. Two companion covariances, built at different estimator seeds, show a seed sensitivity above the limit set before production, so no significance based on the configuration-(a) covariance is quoted (\S\ref{sec:eavailw-adopted}; the comparison on the sixteen cells: \S\ref{sec:fived16-gen}).
```

## SU-6 (sec_summary.tex; group AMB-F; sites 118)

Before:

```tex
have no bearing on the choice of covariance (\S\ref{sec:eavailw-adopted}).
```

After:

```tex
have no bearing on the choice of the five-axis covariance of the configuration-(a) central value (\S\ref{sec:eavailw-adopted}).
```

## AG-1 (app_guide.tex; group AMB-F; sites 119)

Before:

```tex
the fixed identities and audit record of the five-axis covariance,
```

After:

```tex
the fixed identities and audit record of the five-axis covariance of the configuration-(a) central value,
```

## AA-1 (app_statmethods.tex; group AMB-F; sites 121)

Before:

```tex
its use in the five-axis covariance of this note is in
```

After:

```tex
its use in the five-axis covariance of the configuration-(a) central value is in
```

## AA-2 (app_statmethods.tex; group AMB-F; sites 122)

Before:

```tex
The five-axis covariance used in this note deliberately retains
```

After:

```tex
The five-axis covariance of the configuration-(a) central value deliberately retains
```

## AC-1 (app_negweight.tex; group A/B; sites 126)

Before:

```tex
The 2D result and its covariance and the 3D and 4D central values use its refined form (\S\ref{sec:method-algo}); binned purity remains the treatment of the five-dimensional central value and its covariance and of the extended-fiducial value.
```

After:

```tex
The 2D result and its covariance, the 3D and 4D central values and the sixteen-cell five-dimensional result (\S\ref{sec:fived16}) use its refined form (\S\ref{sec:method-algo}); binned purity remains the treatment of the configuration-(a) five-dimensional central value and its five-axis covariance and of the extended-fiducial value.
```

## AC-2 (app_negweight.tex; group AMB-A; sites 127)

Before:

```tex
The entire standard five-dimensional chain uses binned purity
```

After:

```tex
The entire standard five-dimensional chain, that of the configuration-(a) central value and its five-axis covariance, uses binned purity
```

## AC-3 (app_negweight.tex; group A; sites 128)

Before:

```tex
For the five-dimensional central value, which still uses purity, the revisit is open.
```

After:

```tex
For the configuration-(a) five-dimensional central value, which still uses purity, the revisit is open; the sixteen-cell result (\S\ref{sec:fived16}) uses the refined estimator.
```

## AC-4 (app_negweight.tex; group A/B; sites 134)

Before:

```tex
That estimator is configuration (e), which gives the 3D and 4D central values but not the quoted 5D central value;
```

After:

```tex
That estimator is configuration (e), which gives the 3D and 4D central values and the sixteen-cell result (\S\ref{sec:fived16}) but not the configuration-(a) 5D central value;
```

## AC-5 (app_negweight.tex; group AMB-A; sites 135)

Before:

```tex
direct evidence for revisiting the five-dimensional background treatment (\S\ref{sec:negweight-footing}).
```

After:

```tex
direct evidence for revisiting the background treatment of the configuration-(a) five-dimensional central value (\S\ref{sec:negweight-footing}).
```

## AC-6 (app_negweight.tex; group AMB-A; sites 136)

Before:

```tex
this result does not close the revisit of the five-dimensional background treatment (\S\ref{sec:negweight-footing}).
```

After:

```tex
this result does not close the revisit of the background treatment of the configuration-(a) five-dimensional central value (\S\ref{sec:negweight-footing}).
```

## AC-7 (app_negweight.tex; group AMB-F; sites 138)

Before:

```tex
listed in the record of the covariance used in this note.
```

After:

```tex
listed in the record of the five-axis covariance of the configuration-(a) central value.
```

## PB-1 (paper_body.tex; group AMB-marginal; sites 146)

Before:

```tex
\pcell{0.50\columnwidth}{4D and 5D marginal normalizations agree at about 1--2\%;
```

After:

```tex
\pcell{0.50\columnwidth}{4D and 5D (a) marginal normalizations agree at about 1--2\%;
```

## PB-2 (paper_body.tex; group AMB-F; sites 149)

Before:

```tex
\pcell{0.50\columnwidth}{seed-dependent covariance; rounding-level instability}
```

After:

```tex
\pcell{0.50\columnwidth}{seed-dependent (a) covariance; rounding-level instability}
```

## PB-3 (paper_body.tex; group AMB-E; sites 150)

Before:

```tex
\pcell{0.50\columnwidth}{no tested reporting definition meets the 10\% target}
```

After:

```tex
\pcell{0.50\columnwidth}{no reporting definition tested in the precision study meets the 10\% target}
```

## PB-4 (paper_body.tex; group AMB-centralonly (Scope); sites 151)

Before:

```tex
with the observable definitions, simulated detector response, background treatment, and regularization given there.  The paper does not deliver
```

After:

```tex
with the observable definitions, simulated detector response, background treatment, and regularization given there.  The sixteen-cell result of Sec.~\ref{sec:result16} also has total uncertainties, whose coverage is not validated.  The paper does not deliver
```
<!-- absence-ok: quotes or summarizes the note's printed text, before or after this PR, as the writer's record; not a new absence claim -->

## PB-5 (paper_body.tex; group A; sites 154)

Before:

```tex
The five-observable central value uses configuration~(a), with the purity-based subtraction, whose bias is given in Sec.~\ref{sec:closure}.
```

After:

```tex
The configuration-(a) five-observable central value and its covariance use the purity-based subtraction, whose bias is given in Sec.~\ref{sec:closure}; the sixteen-cell result (Sec.~\ref{sec:result16}) uses configuration~(e), with refined negative-weight subtraction.
```

## PB-6 (paper_body.tex; group A; sites 156)

Before:

```tex
\pcell{0.38\columnwidth}{5D central value and covariance; 3D and 4D closures;
```

After:

```tex
\pcell{0.38\columnwidth}{5D central value and covariance of Sec.~\ref{sec:cov5d}; 3D and 4D closures;
```

## PB-7 (paper_body.tex; group B; sites 157)

Before:

```tex
\pcell{0.38\columnwidth}{3D and 4D central values; held-out shapes
```

After:

```tex
\pcell{0.38\columnwidth}{3D and 4D central values; sixteen-cell 5D result (Sec.~\ref{sec:result16}); held-out shapes
```

## PB-8 (paper_body.tex; group AMB-F; sites 160, 161)

Before:

```tex
about one quoted standard deviation in one $(\Eavail,W)$ cell.  This bias is not included in the quoted uncertainties.
```

After:

```tex
about one standard deviation of the covariance of Sec.~\ref{sec:cov5d} in one $(\Eavail,W)$ cell.  This bias is not included in the uncertainties quoted for the configuration-(a) central value.
```

## PB-9 (paper_body.tex; group C; sites 163)

Before:

```tex
No quoted uncertainty includes the regularization bias, and the five-observable covariance omits it.
```

After:

```tex
No uncertainty quoted for the configuration-(a) central value includes the regularization bias, and its five-observable covariance omits it.  For the sixteen-cell result, the model term of its reported covariance is the change in the unfolded data when the prior is reweighted to each generator (GENIE + MEC, NuWro, GiBUU), and Sec.~\ref{sec:result16} gives the fake-data study's measured comparison of the estimator's bias with the reported covariance.
```

## PB-10 (paper_body.tex; group AMB-F; sites 165)

Before:

```tex
the grey band is $\pm$ the quoted total uncertainty of the $(\Eavail,W)$ projection.
```

After:

```tex
the grey band is $\pm$ the total uncertainty of the $(\Eavail,W)$ projection of the covariance of Sec.~\ref{sec:cov5d}.
```

## PB-11 (paper_body.tex; group AMB-F/G; sites 166, 168, 169)

Before:

```tex
The covariance of the five-observable central value, which has a
```

After:

```tex
The covariance of the configuration-(a) five-observable central value, which has a
```

## PB-12 (paper_body.tex; group G; sites 168)

Before:

```tex
We therefore quote no covariance-based generator significance.  The seed dependence of the five-observable covariance rests on one seed pair,
```

After:

```tex
We therefore quote no generator significance based on this covariance; the comparison on the sixteen reported cells is in Sec.~\ref{sec:gen16}.  The seed dependence of this five-observable covariance rests on one seed pair,
```

## PB-13 (paper_body.tex; group list; sites 173)

Before:

```tex
the higher-dimensional central values usable for qualitative comparison.
```

After:

```tex
the higher-dimensional central values usable for qualitative comparison, and the sixteen-cell result usable for the comparison of Sec.~\ref{sec:gen16}.
```

## PB-14 (paper_body.tex; group AMB-centralonly/C (Limitations); sites 177, 178)

Before:

```tex
The higher-dimensional results are central values without intervals of validated coverage, and no quoted uncertainty includes their regularization bias (Sec.~\ref{sec:departure}).
```

After:

```tex
The higher-dimensional results are central values without intervals of validated coverage, and no uncertainty quoted for the configuration-(a) five-observable central value includes its regularization bias (Sec.~\ref{sec:departure}).  The sixteen-cell result also has total uncertainties, whose coverage is not validated; Sec.~\ref{sec:result16} gives the fake-data study's measured comparison of the estimator's bias with its reported covariance.
```
<!-- absence-ok: quotes or summarizes the note's printed text, before or after this PR, as the writer's record; not a new absence claim -->
