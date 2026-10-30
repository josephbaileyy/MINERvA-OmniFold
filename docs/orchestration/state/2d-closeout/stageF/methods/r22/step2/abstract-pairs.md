# r22 Step 2: proposed abstract pairs (main_note.tex), from writer B01

Not applied: main_note.tex is unchanged. Each `before` is the exact current source text (main_note.tex line 72 at the round's start) and occurs once in the file. Each `after` keeps every fact, macro and number; it only splits the sentence. The director pins each pair (check_ledger.py ABSTRACT / ABSTRACT_PINS) and passes it to Joseph before adoption. `pin` below is sha256(before + NUL + after)[:16], as check_ledger.py's pin() computes it, for the director to verify, not to copy.

## B01-s-04

before:

```latex
We report a simultaneous measurement of the $\nu_{\mu}$ charged-current inclusive cross section in five observables, the muon transverse and longitudinal momenta, available hadronic energy, three-momentum transfer and hadronic invariant mass, unfolded without binning with OmniFold from MINERvA medium-energy open data and reported in sixteen cells with a covariance whose median per-cell uncertainty is \fvval{sigmed-C_total_resp}\%.
```

after:

```latex
We report a simultaneous measurement of the $\nu_{\mu}$ charged-current inclusive cross section in five observables: the muon transverse and longitudinal momenta, available hadronic energy, three-momentum transfer and hadronic invariant mass. The cross section is unfolded without binning with OmniFold from MINERvA medium-energy open data. It is reported in sixteen cells, with a covariance whose median per-cell uncertainty is \fvval{sigmed-C_total_resp}\%.
```

pin: `d2075a04421dcc5e`; words 54 -> 59

## B01-s-10

before:

```latex
Three external generator predictions compared on all sixteen cells give $\chi^{2}$ between \fvval{g-ext-chi2int-min16} and \fvval{g-ext-chi2int-max16} for 16 degrees of freedom, and GiBUU, on its 8 cells, \fvval{g-gibuu-total-chi2int}.
```

after:

```latex
Three external generator predictions, compared on all sixteen cells, give $\chi^{2}$ between \fvval{g-ext-chi2int-min16} and \fvval{g-ext-chi2int-max16} for 16 degrees of freedom. GiBUU, compared only on the 8 cells its sample covers, gives $\chi^{2}=\fvval{g-gibuu-total-chi2int}$ on those cells.
```

pin: `2b0420a3ab1e1432`; words 27 -> 35

The same splits are applied to the executive summary's copies of these sentences (sec_execsummary.tex; ledger-B01.md rows B01-1, B01-2), so the summary and the proposed abstract word the GiBUU comparison alike.
