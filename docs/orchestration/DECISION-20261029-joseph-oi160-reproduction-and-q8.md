# DECISION 2026-10-29 — Joseph: the OI-160 reproduction runs, and the paper carries machine-readable files (Q8)

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- **OI-160.** The close-items session asked which replicas the adopted trunk's `C_stat` and `C_ML` rest on
  ([`QUESTION-20261028-trunk-stat-ml-replica-provenance.md`](QUESTION-20261028-trunk-stat-ml-replica-provenance.md)).
  - The director's read-only checks ([`RECORD-20261029-director-oi160-readonly-checks.md`](RECORD-20261029-director-oi160-readonly-checks.md))
    found the combine allocation 55878359 COMPLETED. The top-level replicas were regenerated 07-11..13, after the
    late-June archived set.
  - Those checks cannot show which seed contract's code ran. Only check 4, a one-replica reproduction, decides it.
- **Q8.** The paper's Data Availability draft (d2 B7) names machine-readable files that do not exist. Whether the article
  carries them was Joseph's open question Q8.
  <!-- absence-ok: the paper rewrite lane's claim check of the Data Availability draft on 2026-10-29 found the files absent; a statement about a draft, not about a result -->

The director asked two questions.

> OI-160: shall we run the one-replica reproduction that settles whether C_stat/C_ML came from the corrected seed code?

Joseph's answer, verbatim:

> Yes, run it (Recommended)

sha256 of the text plus a final newline begins `897ce01f408a6381`.

> Q8: should the paper carry the 16-cell cross section, covariance matrix and cell definitions as machine-readable Supplemental Material (typical for PRD)?

Joseph's answer, verbatim:

> Yes, prepare them (Recommended)

sha256 of the text plus a final newline begins `b7c2a6a1513c288f`.

## What is decided

1. **The OI-160 reproduction runs** under the standing approval for jobs under 12 h, declared and bound as usual.
   - The option offered was "One CPU job, well under 12 h, under the standing approval … re-runs one bootstrap
     replica with each contract's code to compare with the stored file."
   - The close-items session, OI-160's owner, writes the declaration: one replica (`res_boot_1`, `--seed 1`), with
     `07c18aee`'s `bootstrap_nd.py` (estimator seed 42) and with `07c18aee^`'s, each compared with the stored
     `xsec_flat` in `boot_nd_5d/` and in `boot_nd_5d_prehm_20260711/`.
   - It runs on CPU, with no GPU, no premium QOS and no write to CFS, from a clean clone on pscratch. The director binds
     it before anything runs.
   - The outcome goes to Joseph as a report. Any change to `C_stat`, `C_ML` or the adopted trunk is a separate decision.
2. **The paper carries the 16-cell cross section, its covariance matrix and the cell definitions as machine-readable
   Supplemental Material.**
   - The option offered was "The lane generates the three files from the pinned data product into the repo. Nothing is
     deposited or submitted, and the Data Availability statement then says they are provided."
   - The paper rewrite lane generates them from the pinned products, with a check that each one reproduces the printed
     table and covariance. It then applies d2 B7's first sentence.

## Not changed

- Nothing is submitted, deposited or tagged. The files live in the repository only.
- `C_stat`, `C_ML`, the reported matrix and every published value.
- Claims, KI-85 and publication are Joseph's.
