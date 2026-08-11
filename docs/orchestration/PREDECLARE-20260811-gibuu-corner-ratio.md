# PREDECLARATION — the GiBUU (E_avail,W) corner ratio

**Written 2026-08-11 BEFORE the run.** Recovers the one uncomputed generator ratio named in
`docs/INTEGRATION_CHECKLIST.md` #6, by re-running `make_figures.sh:55` and reading the
`hiE-hiW corner … data/gen=` stdout line, per the recorded recipe.

## Scope: this is NOT gated by quarantine causes 1–6, and here is why

Read at `3d-unfolding/genie/overlay_eavailW_band.py:88-108`, the corner ratio is

    corner    = outer(EAVAIL_EDGES[:-1] >= 0.8, W_EDGES[:-1] >= 1.8)      # 3 x 3 = 9 cells
    data/gen  = (data2d * dEa * dW)[corner].sum() / (g2d * dEa * dW)[corner].sum()

**A ratio of two central-value integrals. No covariance appears anywhere in it.** The 2026-07-12
quarantine's own scope says *"Central cross sections, closure tests, dimensional anchors … were never
invalidated by this quarantine"*, and `INTEGRATION_CHECKLIST` gates the `(E_avail,W)` **significances**,
which are covariance-dependent, separately from the **ratios**, which are not. So this number is
recoverable now, and the significances remain gated. **Stating the distinction because the checklist row
bundles them in one line and the easy error is to treat the ratio as blocked — or, worse, to treat the
significance as unblocked once the ratio lands.**

## Why it was uncomputed — measured, not guessed

    genie_cv_xsec_eavailW.root    2026-06-08 19:50:54Z
    genie_mec_xsec_eavailW.root   2026-06-08 20:04:09Z
    nuwro_cv_xsec_eavailW.root    2026-06-08 20:04:24Z
    gibuu_cv_xsec_eavailW.root    2026-06-09 17:47:49Z   <- ONE DAY LATER
    excess_eavail_W.root (data)   2026-07-14 04:22:19Z   <- FIVE WEEKS LATER

The three-generator band run of 2026-06-08 could not have included GiBUU: **its input did not exist yet.**
`ND_OMNIFOLD_RUN_LOG.md:988-990` records *"GiBUU excluded (FinalEvents.dat lacks per-event Enu)"*, and the
file landed the following day. And `overlay_eavailW_band.py:97-98` **fails open** — a missing `--gen` file
prints `[band] MISSING <label>` and `continue`s — so the script has always been able to produce a complete-
looking three-generator table with the fourth silently dropped to one line.

## THE TRAP, and it is BEN-102's shape again

**The data file post-dates the note's three ratios by five weeks.** So a re-run today computes all four
ratios against a **different data central value** than the one that produced `1.54 / 1.58 / 1.56`
(`sec_eavailw.tex:64`). **I therefore expect the three not to reproduce exactly, and that is not a defect.**

**Consequence for the deliverable: the correct output is FOUR ratios computed together on one data file,
replacing the note's three — not a fourth number appended to three older ones.** Appending would put four
magnitudes in one sentence with one of them footed on different data, which is precisely the defect just
found in the `\gbdtFive*` block. **I am recording this before seeing the numbers so that the "just append
GiBUU" reading cannot be adopted afterwards on grounds of convenience.**

## PREDECLARED BRANCH SET

**G1 — FOUR RATIOS, THREE REPRODUCE.** GiBUU computes, and GENIE-CV / GENIE+MEC / NuWro come out at
`1.54 / 1.58 / 1.56` to the printed precision. → The three are a positive control, the data file's change
was inert for this corner, and all four may be quoted together. Report the set.

**G2 — FOUR RATIOS, THREE DO NOT REPRODUCE.** GiBUU computes but the three move. → **Expected, given the
five-week gap, and it is the branch I consider most likely.** The four are internally consistent and
`sec_eavailw.tex:64`'s three are stale. Report all four as a replacement set, with the old three and the
delta stated, and **do not** quote the new GiBUU number beside the old three.

**G3 — GiBUU STILL DOES NOT COMPUTE.** The file exists but lacks `hXSec_eavailW`, or the ratio is
non-finite (zero corner integral → division by zero, which the code does not guard). → **UNRESOLVED**, and
*not* "GiBUU has no excess". A zero or missing corner integral is a statement about the artifact, not about
GiBUU's physics, and the difference matters because GiBUU is the generator the note reports as worst-fitting
— a spuriously large or infinite ratio would be *directionally consistent with the expected answer*, which
is exactly when a broken number is most likely to be believed.

**G4 — THE SCRIPT FAILS.** Import, ROOT, or a missing `hData2D`. → UNRESOLVED. Not G3.

## Reported on every branch

The whole stdout stream redirected to a file, never piped through `tail`/`head` (BEN-026), with the
per-generator `total`, `data`, `ratio`, `hiE-hiW corner` and `data/gen` lines quoted intact — operands
beside every ratio, so each reported ratio can be recomputed from its own numerator and denominator and the
numbers can contradict each other (`CONVENTION-receipt-ingredients.md`, BEN-077). Plus the mtimes above, so
a reader can see which data file each ratio belongs to without trusting this document.
