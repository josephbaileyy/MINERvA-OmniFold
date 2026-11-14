# History restructure, App. B (app_statmethods_nd.tex): cut log

**Under** DECISION-20261113-joseph-note-n4-n5-role.md, the addendum recording Joseph's go of 2026-11-13, and the
director's ruling (A) of 2026-11-14 (recorded in sec_5d.md).

**The rule, verbatim as adopted:** history stays in the note only if removing it would change a reader's understanding
of the reported object, its reproducibility, its evidential independence or its limitations. Everything else goes to
the ledger. Each "fixed before" names its object, and "declared" alone is replaced.

**Referee:** for App. B it gave "15–25%, Compress / ledger, chiefly B.1's retired-covariance examples. Preserve
applicable inverse and finite-ensemble qualifications."

**Base:** `docs/analysis-note/app_statmethods_nd.tex` at `ae4285e94`. Line numbers are the base's. B.6 (`sec:cov1b-gate`,
moved from §10 as G1) is not changed.

## The changes

| id | base line | old text | new text | ledger home and records |
|---|---|---|---|---|
| B1 | :16 | "The superseded unified-throw 5D covariance has $N=160$, truncated $p=100$, giving $58/160\simeq0.363$: uncorrected precision is too large by $\simeq2.76$. For fixed residuals this inflates $\chi^{2}$ and overstates tension." | "For fixed residuals an uncorrected bias inflates $\chi^{2}$ and overstates tension." The retired covariance's worked example leaves (referee). The qualification stays: the debiasing factors $(N-p-2)/(N-1)$ and $(N-p-2)/N$, "For fixed residuals …", "Confidence regions from the same over-tight covariance become over-optimistic", and "No generic correction is prescribed …". | ae4285e94:app_statmethods_nd.tex:16 |
| B2 | :12 | "the requirement that N-D difference statistics use a rank cut fixed in advance" | "… a rank cut fixed before the results are seen", the record's own object (a first wording, "before any observed statistic is computed", was failed by the read as an earlier deadline than the record's "before looking at results") | ae4285e94:app_statmethods_nd.tex:12. docs/STATVAL_REPAIR.md:31, "Predeclared contract (fixed BEFORE looking at results)" (first commit 6964af371, 2026-07-16); docs/orchestration/RANK-AND-INVERSION-20260810.md:110, "requires a **PREDECLARED rank/pseudoinverse cut** for the difference statistics", and :118 (b04470d22, 2026-08-09). The record is the one `rank-inversion` names (app_provenance.tex:56-58). |

**Kept as they are:**
- **:10, the earlier 5D covariance from the standard production chain** (10 694 bins, rank 263, its 4D projection,
  and "would understate tension by roughly $40\times$ in 5D or $18\times$ in 4D"): this is the evidence for "The 2D
  justification … does not transfer to N-D". It is also the inverse qualification the referee keeps, and items (iii)
  and (iv) of the requirements rely on it.
- **:19** "such as the earlier 5D covariance from the standard production chain": the example of a sum with no single
  debiasing factor, the same object as :10.
- **:47** "only the iterations that reproduce the originally recorded values are used": a reproducibility rule.
- **The section title and :5 "declarations"**, as in "Rank, ndf and finite-ensemble declarations": this is a noun for
  what each N-D $\chi^2$ must state (items (i)–(v)), not a timing claim. Renaming it would change a printed section title, so it
  is left for the director.

**Numbers and keys:** `numdiff.py` on the base and new files, comments stripped:
- Removed: "5" (from "5D"), "160" (twice), "100", "58", "363" and "76", all from B1's worked example (0.363 and 2.76
  are read as "363" and "76" after their leading digits).
- Added: none.
- Value keys and macros: unchanged.

## The Development-history appendix

No new row. B1's example is a worked illustration on a superseded covariance, and no released result rests on it.

## Disclosure checklist

| disclosure | in App. B? | survives |
|---|---|---|
| the 2D adoption after the published distance was known | no (§3) | — |
| the post-observation run-period term | no | — |
| reused samples and seeds | no | — |
| the invalid q3 deformation | no | — |
| the stopped coverage tests | B.6, the gate investigation (G1) | ✓ unchanged |
| the data-informed joint-test design and budget extension | the familywise bound covers "stops decided with results visible, irregular looks, lost draws, and the budget extensions" (B.5) | ✓ unchanged |
| the missing response uncertainty | no | — |
| the generator-sample problems | no | — |
| the target-correction sensitivity | no | — |
| also found: the finite-ensemble bias and "No generic correction is prescribed" (B.1) | yes | ✓ unchanged |

## Unreleased support

No site in App. B changes its citation. `UNRELEASED-SUPPORT.md` is unchanged.

## Meaning read (codex-school gpt-6.1-sol, high, read-only; reads/app_statmethods_nd-prompt.txt, with reads/app_statmethods_nd-records.txt)

- **Pass 1:** OVERALL FAIL on B2, whose first wording strengthened the record's timing. B1 passed, and its worked
  example was classed LEDGER. No NEEDED item was lost, and no disclosure. reads/app_statmethods_nd-pass1.txt.
- **Pass 2, B2 reworded:** OVERALL PASS, with no FAILs. reads/app_statmethods_nd-pass2.txt.
