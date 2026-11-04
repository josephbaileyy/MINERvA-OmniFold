# DECISION 2026-11-04 (later) — Joseph: commission five of the referee-analysis designs; flag the low-stability cells

**Recorded by** the paper-tighten lane, as director.

## What led to it

**The second two-referee read** (`secondary-results/referee-rerun-20261104/`, #757) left both verdicts unchanged: major
revision, or recast as a methods study. Sonnet added analysis requests.

**limitation-resolver scoped and priced them** in `secondary-results/scope-referee-analysis-20261104/REPORT.md` (#758,
merged `9b1f470c`), with an independent Gemini read beside it. Its judgement, which the consult shares: none of (a)–(g)
moves either verdict, since coverage and the rounding instability are untouched.

It also found:
- the 2D shape difference is partly decomposed already (`app_statmethods.tex:540-557`);
- exact binned iteration lowers the GiBUU-like residual (8.3% to 3.3%) but not W3 or q3. The paper's "persists over
  iterations" ground is therefore weak.

## Joseph's answers, verbatim

Asked which of the scoped analyses should be commissioned now:

> Zero-cost items (Recommended), 2D binned cross-check (Recommended), 16-cell binned head-to-head (Recommended), Flux-swap run-period test

sha256 of the text plus a final newline begins `1b4d8a744aad9c24`.

Asked how the paper should treat the four low-stability cells (R02, R06, R10, R15):

> Flag them in Table II (Recommended)

sha256 of the text plus a final newline begins `c9c131150a9e6ebc`.

## What is decided

1. **Commissioned.** Each is declared, audited and bound before it runs, within the standing CPU grant, using the
   report's designs and prices:
   - **The zero-cost items:**
     - b0, the 3b detector-mismatch closures printed as a bounded statement. The director reads "bounded" as
       descriptive, with no pass threshold set; Joseph can set one when he reads the wording.
     - The paper's bias-attribution sentence is corrected to what D-ID and IBU-1 show.
     - d1, five-observable reconstruction-level data/MC per playlist, from RPD's dumps, with a frozen recipe and a go.
   - **c2 with c1:** this analysis's own binned unfolding on the 2D inputs, and the joint-test estimator run in the 2D
     configuration, against the published result. About 12.5 node-h, or about 33 with universes.
   - **g1:** the 16-cell binned head-to-head. About 1–5 node-h.
   - **d2:** the reconstruction-level flux-swap test. About 0.33 node-h plus code, before 2026-12-15 if it reads the
     zero loops.
2. **Not commissioned:** a1/a2 (the data-driven prior; A is not reopened), b1/b2, e1–e5 and f2/f3.
3. **The low-stability cells:** Table II flags R02, R06, R10 and R15 as reconstruction-stability limited
   (0.16–0.25), beside their values. All 16 cells stay as reported, with no after-the-fact change to the result.
   This joins the paper lane's presentation round.
4. **The paper's wording** for b0, the attribution sentence and the flags goes through the PRD-referee read and to
   Joseph before merge. Each analysis's result goes to Joseph before any paper text that uses it.

Nothing is submitted, deposited or tagged.
