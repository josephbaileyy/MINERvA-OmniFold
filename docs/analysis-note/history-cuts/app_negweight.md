# History restructure, App. C (app_negweight.tex): cut log

**Under** DECISION-20261113-joseph-note-n4-n5-role.md, the addendum recording Joseph's go of 2026-11-13, and the
director's ruling (A) of 2026-11-14 (recorded in sec_5d.md).

**The rule, verbatim as adopted:** history stays in the note only if removing it would change a reader's understanding
of the reported object, its reproducibility, its evidential independence or its limitations. Everything else goes to
the ledger. Each "fixed before" names its object, and "declared" alone is replaced.

**Referee:** for App. C it gave "15–25%, Compress. Keep derivations, comparisons, bias findings, and actual background
treatments; remove production archaeology." Its item 9 (§C.6, the second ground at :126) offers the rewrite
"Purity subtraction was retained to preserve the existing covariance and consistent treatment across its components;
its observed subtraction bias remains in configuration (a)". It marks the passage "**Decision-basis disclosure—stay.**"
and adds "Job-script reconstruction belongs in the ledger."

**Base:** `docs/analysis-note/app_negweight.tex` at `6b9b5be5c`. Line numbers are the base's.

## The change

| id | base line | old text | new text | ledger home |
|---|---|---|---|---|
| C1 | :122 | "The existing endpoint unfolds, produced in July 2026, used purity, as established by elimination from their job scripts and logs (Ref.~[34], bkg-mode-elimination). Current production fixes the background treatment in a configuration object that rejects every other mode. The standard job script passes the driver's background-mode option (\texttt{-{}-bkg-mode}) explicitly from that configuration, and the value is written into the record of every endpoint unfold as it is produced, so the background treatment of each new component can be read from the component itself; this changes how the treatment is recorded, not the treatment itself." | "The existing endpoint unfolds used purity, as established by elimination from their job scripts and logs (Ref.~[34], bkg-mode-elimination). Current production writes the background treatment into the record of every endpoint unfold as it is produced, so the background treatment of each new component can be read from the component itself; this changes how the treatment is recorded, not the treatment itself." The job-script mechanics leave (referee item 9): the production date, the configuration object that rejects every other mode, and the job script's `--bkg-mode` option. Kept: that the existing unfolds' treatment was established by elimination rather than recorded, which bears on reproducibility; that new components record it; and that only the recording changed. | 6b9b5be5c:app_negweight.tex:122; the record bkg-mode-elimination |

**Not changed: the decision basis at :126** (referee item 9). The referee's rewrite would replace "Second, switching
would have required rerunning every unfold above and would have invalidated the flux-corrected covariance then just
chosen for use; this consequence, rather than the computing cost, decided the choice." That sentence states what
decided the choice and what did not. The rewrite keeps neither the invalidated covariance nor "rather than the
computing cost", and the referee itself marks the passage as a disclosure that stays. The rest of :126 already states
the open revisit for configuration (a) and the refined estimator of the 2D and sixteen-cell results.

**Kept as they are:**
- **:120** the standard chain's components (169 vertical-band, 18 detector and 10 endpoint unfolds): the actual
  background treatment.
- **:136–140** the 2D closure test with backgrounds and the data movement: bias findings and comparisons.
- **:145** "the extended-fiducial ME~FHC battery of 2026-06-10": the date identifies which battery the quoted
  $\sigma_{\mathrm{ext}}$ comes from (record fps-battery), and the paragraph's disclosure is that the quoted number used
  purity, not the intended baseline.
- **:153–161** the designated treatments, the displacement argument, and the scope and limits of the 5D evidence.

**Numbers and keys:** `numdiff.py` on the base and new files, comments stripped:
- Removed: "2026", from "produced in July 2026".
- Added: none.
- Value keys and macros: unchanged.

## The Development-history appendix

No new row. The purity-subtracted configuration (a) is already row D2 (2D) and D3 (5D).

## Disclosure checklist

| disclosure | in App. C? | survives |
|---|---|---|
| the 2D adoption after the published distance was known | the 2D result uses the refined treatment, rebuilt for it (:140); the adoption timing is §3's and D2's | ✓ unchanged |
| the post-observation run-period term | no | — |
| reused samples and seeds | the 2D closure test's pseudo-experiments, both treatments on the same pseudo-data (:136) | ✓ unchanged |
| the invalid q3 deformation | no | — |
| the stopped coverage tests | no; "not a coverage test" (:138) | ✓ unchanged |
| the data-informed joint-test design and budget extension | no | — |
| the missing response uncertainty | no | — |
| the generator-sample problems | no | — |
| the target-correction sensitivity | no | — |
| also found: the decision basis for keeping purity in the standard chain (:126) | yes | ✓ unchanged |
| also found: the quoted extended-fiducial number used purity, not the intended baseline (:145) | yes | ✓ unchanged |
| also found: the existing endpoint unfolds' treatment established by elimination (:122) | yes | ✓ kept in C1 |

## Unreleased support

No site in App. C changes its citation. `UNRELEASED-SUPPORT.md` is unchanged.

## Meaning read (codex-school gpt-6.1-sol, high, read-only; reads/app_negweight-prompt.txt)

- **Pass 1:** OVERALL PASS, with no FAILs. C1 passes; its three removed details are LEDGER; the NEEDED content of the
  shortened passage survives; no disclosure lost. reads/app_negweight-pass1.txt.
