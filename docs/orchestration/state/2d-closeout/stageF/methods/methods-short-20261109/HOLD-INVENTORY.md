# Hold inventory of the short methods paper (draft only)

This sheet goes with every draft of the paper and its Supplemental Material (branch `draft/methods-short-20261109`). It
is never submitted. From 2026-11-11 to 2026-11-16 the record inventory below printed as a red hold in section 7 of the
paper. It now lives here, and section 7 prints nothing in its place (the director, relaying Joseph 2026-11-16: "1. (the
inventory) I like your recommendation."). Its text is the hold's, with section numbers resolved. Row 7 was corrected and
extended before the move (the director, 2026-11-16).

**Rule.** Do not submit a build of the paper or the Supplement that renders any `\pubhold` (`main_paper.tex:4`). The gates
below are what the inventory and the two printed holds wait on.

`check_hold_inventory.py`, run by `check_round.py` (check 14), fails unless the sheet agrees with the tree:
- the printed holds listed below are exactly the `\pubhold` texts that the paper and the Supplement print;
- every section number below is the one its label gives at this tree (paper and Supplement) or at the note's release
  revision (`note_release_labels.tex`);
- every record path below exists;
- the release revision named below is `NOTE_RELEASE_REV`.

## Gates still open

1. **Where each record below is published.** The Data availability hold's deposit identifier and access route wait on the
   separately authorized release decision.
2. **The note's release revision.** `NOTE_RELEASE_REV` (`check_round.py`) is `87cee1c86`. The note's numbers below are
   that revision's. It moved there on 2026-11-17, after the note's cutdown (the director), and moves again only at a later note freeze.
3. **Funding and grant acknowledgments**, to be supplied by the authors.
4. **The bias-half rule**, which row 12 lists as pending, in the paper and Supplement only.

## Holds the paper still prints

- `funding and grant acknowledgments`: `main_paper.tex`, Acknowledgments. Gate 3.
- `deposit identifier and access route, after the separately authorized release decision.`: `main_paper.tex`, the last
  sentence of Data availability. Gate 1.

The Supplement prints no hold.

## Where each record this paper relies on is published, with the note at its release revision

Each row gives the item, its places in the paper, in the Supplement (S) and in the note, and its records. Record paths
are relative to `docs/orchestration/`. "Only" means that the note at its release revision carries none of the item.

1. The two-dimensional comparisons with IBU and of the five-observable estimator on the two-dimensional inputs: section
   4.2 (`sec:paired2d`) and S7 (`supp:ibu`) only. Record `OUTCOME-20261106-ref-c2c1-read.md`.
2. The sixteen-cell IBU comparison: section 4.5 (`sec:ibu`), S7 (`supp:ibu`) and the note's section 10.6
   (`N-sec:fived16-ibu`). Record `OUTCOME-20261106-ref-g1-r1-differ.md`.
3. The run-period step's per-period unfolding and the per-period benchmark: section 4.3 (`sec:closure2d`) and S6
   (`supp:cov2d`), with the note's section 4.5 (`N-sec:uq-combine`) giving the period-group step against 1A--1F only.
   Records `state/2d-closeout/period-unfold-20261014/REPORT.md` and `OUTCOME-20261107-per-period-2d-benchmark.md`.
4. The 1A triage: section 2 (`sec:data`) and S1 (`supp:selection`) only. Record
   `state/2d-closeout/stageD-inputs/q2-opendata-20261014/triage/REPORT.md`.
5. The rounding floor, the stabilization probe and the rounding-mechanism study: section 6.1 (`sec:cov5d`), S4
   (`supp:estimators`), the note's section 9.3 (`N-sec:val-departure`) and its appendix B.2
   (`N-sec:gbdt-diagnostic-definitions`). Records `OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md`,
   `OUTCOME-20261105-fd-stab-none-pass.md` and `OUTCOME-20261108-rs1-rounding-mechanism.md`.
6. The ensemble average: section 6.1 (`sec:cov5d`), S4.4 (`supp:diagnostics`) and S8 (`supp:tests`) only. Record
   `OUTCOME-20261109-ens1-stab-pass-bias-worse.md`.
7. The first five-observable coverage test's preliminary check and its stop: section 6.2 (`sec:calib`), S8.6
   (`supp:study-cov1`) and the note's section 10.5 (`N-sec:fived16-fd`). The check's diagnosis and the staged redesign's
   stop: S8.6 (`supp:study-cov1`) and the note's section 10.5 (`N-sec:fived16-fd`). The investigation of that check and
   the pre-check of the test's flux and detector groups: S8.6 (`supp:study-cov1`) and the note's appendix B.5
   (`N-sec:cov1b-gate`). Records for these three sentences:
   `state/measurement-paper/5d-community-20261024/FD-1B-DIAG-REPORT.md`,
   `state/measurement-paper/5d-community-20261024/FD-1B-INV-I2-REPORT.md`, `OUTCOME-20261108-1b-precheck-part1.md` and
   `OUTCOME-20261106-1b-stage1-receipt-stop.md`.
8. The two-dimensional covariance's held-out-tune coverage test: section 6.2 (`sec:calib`), S8.4 (`supp:study-cov2d`)
   and the note's section 5.3 (`N-sec:coverage-tunes`). Record `OUTCOME-20261108-cov2d-both-tunes-under-cover.md`.
9. The usage-recommendation and prior-spread rules: section 5.2 (`sec:vhalf`), S10 (`supp:validity`) and the note's
   section 10.5 (`N-sec:fived16-fd`), which also prints the prior-spread rule's results that this paper withholds.
   Records `OUTCOME-20261107-valid-region.md` and the decision withholding the prior-spread results.
10. The prior-retention study: section 5.3 (`sec:prr`) and S8.2 (`supp:study-prr`) only. Record
    `state/measurement-paper/5d-community-20261024/fd/receipts-prr/read/cluster/readout.json`.
11. The second five-observable coverage test, a completed descriptive result: section 6.2 (`sec:ll5d`), S8.5
    (`supp:study-ll5d`) and the note's section 10.5 (`N-sec:fived16-fd`). Records
    `state/measurement-paper/5d-community-20261024/fd/receipts-ll5d/readout/node/readout-g18.json` and
    `state/measurement-paper/5d-community-20261024/fd/receipts-ll5d/readout/node/readout-ar23.json`, and its decision
    record on the rerun on the sixteen cells.
12. Pending, and in the paper and Supplement only: the bias-half rule, section 5.2 (`sec:vhalf`) (its decision record).

<!--
Provenance (not printed). The decision records are named here, not above, as in the hold, where a printed file name
could not contain the author's first name (check_round check 8). The withholding:
DECISION-20261110-joseph-vprior-withhold.md. The bias-half rule: DECISION-20261109-joseph-bias-half-rule.md. The second
test's rerun: DECISION-20261110-joseph-ll5d-rerun-16-cells.md. check_hold_inventory.py checks that these exist.

The hold was rewritten 2026-11-11 (afdb26f35, replacing an earlier section 7 hold; the director, on Joseph's adoption of
the independent consult's "full record" recommendation: reword, adding no study to the note), and edited after that. Its
"only" statements were searched in the note at acf934d71 for each item's printed numbers and terms. Search: 382.8; 13.87; kappa; 6.94; 1A--1E; 132 poorly; predates;
ensemble average; retained fraction; bias-half; preliminary check; staged; second five-observable (sec_*.tex and
app_*.tex). At the pin 8342963c1 (2026-11-16) the same terms were searched again, and only "staged" changed (from a comment
line into printed text). Row 7's "only" was already false at acf934d71 for part of the item: sec_fived16.tex:258 there
printed the gate, the band-set diagnosis and the investigation in words the term search did not match (the independent
read of the move, 2026-11-16).

Row 11 (2026-11-16, the director, from codex-reports/crossdoc-numbers-3d4d33144-8342963c1.md row 13): the test is
complete and descriptive, and the note reports it in its section 10.5 at the pin 8342963c1.

Row 7 (2026-11-16, the director; corrected before the move, approved with the move). At the pin 8342963c1 the note
prints the check, its band-set diagnosis and the staged redesign's stop in section 10.5 (sec_fived16.tex:279, :286 at 8342963c1;
the stop paragraph was added in note commit 4297bd33f), and the investigation (I2) and the pre-check in App. B.6, sec:cov1b-gate (app_statmethods_nd.tex:90-100).
The pre-check is OUTCOME-20261108-1b-precheck-part1.md's: the same flux and detector groups, the same window, and
GEANT_Neutron in R00 R02 R08 R09 R10 R11 and GEANT_Proton in R01 R05 R07 R08 (its :41-42, which equal the note's
values_landed p1-neutron-cells and p1-proton-cells). The row's "only" is dropped and "the staged stops" became "the
staged redesign's stop" (one stop, at its first stage). The director's rulings on the read of the move
(2026-11-16): section 6.2 is listed only for the preliminary check and its stop (the paper does not print the diagnosis
or the staged redesign's stop), "the test's flux and detector groups", and "Records for these three sentences". Records (the director, 2026-11-16): FD-1B-INV-I0-REPORT.md is
replaced by FD-1B-DIAG-REPORT.md (the band-set diagnosis, its :40; fd/receipts-1b/diag/diag.json, which
make_values_fived16.py reads) and FD-1B-INV-I2-REPORT.md (the investigation). Neither the paper nor the note prints I0's
result (H2 rejected), and the row cites what supports the printed text.

Pin move (2026-11-17, the director: the note draft 87cee1c86, the cutdown merged). Of the 49 cited labels, only
N-sec:cov1b-gate changed number (B.6 -> B.5, the same title; its text still prints the investigation and the pre-check).
Three titles changed "measurement" to "result" with the same objects, and the rest changed page only. The hold's
search terms were searched again at 87cee1c86, and no count changed from 8342963c1.
-->
