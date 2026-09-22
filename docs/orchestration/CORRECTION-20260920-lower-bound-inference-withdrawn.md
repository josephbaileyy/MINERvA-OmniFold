# CORRECTION 2026-09-20 — the seed-sensitivity "lower bound" is withdrawn, and the C7 summary regains its qualifier

**CITABLE FOR:** the withdrawal of one inference, the repair of one dropped qualifier, and the
complete list of sites each reached.
**NOT CITABLE FOR:** any re-grade, any change to a measured value, or any withdrawal of the
adoption. **No number moved.** Two sentences about what numbers mean did.

Source: [`VERDICT-20260920-third-lane-c5-c7-verification.md`](VERDICT-20260920-third-lane-c5-c7-verification.md),
findings `P1` and `P2` — the third-lane independent verification of `(5, Z)` and `(7, Z)`,
commissioned because `DISCLOSURE-20260920`'s `V2` left clause (c) inert for those two rows.

---

## 1. `P1` — WITHDRAWN: *"it is a LOWER bound"* / *"letting them vary could only add"*

### The measurement, which stands unchanged

Five of `C_Z`'s 45 bands — `BeamAngleX`, `BeamAngleY`, `MuonResolution`, `Muon_Energy_MINERvA`,
`Muon_Energy_MINOS` — are produced at a literal `--seed 42` the offset hook cannot reach
(`MNV_EST_SEED_OFFSET` appears **0** times in all six files of that chain). They carry **26.0% of
`√Tr C_Z`** and **6.75% of the trace**, and contribute **zero** movement by construction.
[`EVIDENCE-20260919-lateral-bands-are-seed-pinned.md`](EVIDENCE-20260919-lateral-bands-are-seed-pinned.md).

### The inference, which does not follow

`s_proj` is the **maximum** of `|Δ√(uᵀCu)| / √(uᵀCu)` over the declared functional set
(`z_statistics.s_proj` (`z_statistics.py:319` at `2a2196e3`; it was cited as `:203` and the line moved)). It is **not** a sum of nonnegative per-component magnitudes.
Releasing a component that was held fixed does not append a sample to the maximum of the same
statistic — it **changes the statistic's operands**. Two positive-semidefinite components can move
in opposite directions between seeds, so the total can move **less**.

**The verifier's one-dimensional counterexample, on strictly positive components:**

| | baseline | lateral held fixed | lateral also varying |
|---|---|---|---|
| vertical `V` | `1` | `1.2` | `1.2` |
| lateral `L` | `1` | `1` | `0.8` |
| total `C` | `2` | `2.2` | `2` |
| `s_proj` | — | **`4.880885%`** | **`0`** |

Releasing the held-fixed block took the measured movement to zero. That is a counterexample to the
inference, **not** a measurement of this analysis.

### The distinction that must survive, because half of the one-sided reasoning is VALID

| statement | status |
|---|---|
| *"`s_proj` is a maximum over the declared offset set, so **more seed pairs can only raise it**"* | **VALID and retained.** More pairs append samples to the maximum of the **same** statistic over the **same** operands. |
| *"the five fixed-seed bands contribute zero, so **letting them vary could only add**"* | **WITHDRAWN.** This changes **which components vary**, so it changes the operands, and the monotonicity above does not transfer. |

These two were collapsed into one bullet in `EVIDENCE-20260920` §"what it does not do" — *"for the
same reason the covariance result is"* — which is exactly the shape that made the error invisible.

### The replacement wording, used verbatim at every prose site

> The seed variation does not probe the seed sensitivity of the five fixed-seed lateral bands; its
> effect on the total covariance when those bands also vary has not been measured.

### ⚠ WHAT IS **NOT** WITHDRAWN

- **`M1`'s `s_proj = 6.145%` against the `5%` bound.** Measured directly on the graded object. It
  never rested on this inference, and `(cause 3, Z)`'s `M(ii)` **branch 5, NOT MET — PER-BIN**
  stands. Receipt `state/GRADE-20260920-cause3-two-member.json`.
- **`M2`'s flatness in `N`** (`6.04% ± 0.39%` at `N = 40/80/160`, exponent `0.000`, against the
  resampling floor's `20.91% → 7.57%`, exponent `1.467`).
- **`M4`'s central-value movement** (`≤ 6.02%` of quoted `σ` on the 42 destinations).
- **The adoption itself.** The verifier states this explicitly: *"this audit does not withdraw
  Joseph's adoption."*

**What IS newly open:** whether the FAIL would survive *any* release of the five bands.
`OUTCOME-20260920` had claimed *"the FAIL is robust to the limitation; a PASS would not have
been."* The first clause is now an **open question**, not a settled robustness argument. It does
not disturb the FAIL, which was measured without it.

### Every site reached — enumerated, because a withdrawal that misses a paraphrase survives in the paraphrase

| # | site | what it said |
|---|---|---|
| 1 | `DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md` §4 `M3` | *"It is a LOWER bound … Letting them vary could only add"* |
| 2 | `RECORD-20260920-PROJ-m1-publication-under-exception.md` §4.3 | *"It is a LOWER bound"* |
| 3 | `EVIDENCE-20260920-sproj-resolution-floor-and-seed-effect.md` §closing | *"It is a lower bound, for the same reason the covariance result is"* |
| 4 | `OUTCOME-20260920-cause3-two-member-assessable-FAIL.md` §4 | *"could only add movement, not remove it. The FAIL is robust to the limitation"* |
| 5 | `docs/analysis-note/sec_eavailw.tex` | measurement 3's heading, *"It is a lower bound."* |
| 6 | `docs/analysis-note/paper_body.tex` | *"so the figure is a lower bound"* |
| 7 | `docs/analysis-note/primer_body.tex` | *"the figure above is a floor rather than a ceiling"* |
| 8 | `docs/analysis-note/values.tex` | the block-(3) comment governing `\pinnedBandsSqrtTr` |
| **9** | **`docs/orchestration/CATALOG.md`**, the entry for `DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md` | ⚠ **MISSED BY THIS TABLE UNTIL 2026-09-22.** It asserted *"five seed-pinned bands make it a **lower bound**"* in the catalogue's own voice, unmarked, on the entry a reader reaches the adoption THROUGH — and contradicting this same file's own `WITHDRAWN` marking further up. Site 1 is the decision record; its `CATALOG.md` entry was a ninth site, and *"every site reached"* was false for two days. Found by the eighth independent review, not by this sweep. |

**`values.tex` is site 8 and it is the one a search for the claim would miss**, because it is a
LaTeX comment above a macro rather than rendered text. A correction that fixed the three `.tex`
bodies and left the comment would leave the next author the withdrawn reasoning as the macro's
stated justification. Sites 1–4 carry an inline `⚠ CORRECTED 2026-09-20` block; sites 5–8 are
prose and are corrected in place, with this record as their route.

**Swept by CLAIM, not by wording.** `grep -rn "lower bound\|could only add\|floor rather"` over
`docs/` returns, after this correction, only: historical records that predate and do not depend on
it, `SPEC`'s own two *earlier* lower-bound withdrawals, the surviving and valid *more-pairs*
statement at two sites, and the verdict's own statement of the finding.

---

## 2. `P2` — REPAIRED: the C7 summary dropped its top-1% qualifier

`OPERATIVE-SHEET-scalar5d.md` §4i stated *"The per-bin ratios run `0.687`–`1.153`"* with no
qualifier. **§4g:578 of the same document declares that range to be the top 1% of bins by support
variance**, and §4g:557-558 gives the full range over all 10,694 bins as `0.177248` – `3.061947`.

So the document contradicted itself nine lines apart, and **the wrong number was in the summary** —
the half a reader quotes.

**Independently re-derived by the third lane from the five support and five active matrices
themselves**, not from the sheet:

| quantity | third lane | §4g |
|---|---|---|
| `min sqrt(diag_active/diag_support)` on positive-support-variance bins | `0.17724803760759691` | `0.177248` |
| `max` | `3.0619466845725776` | `3.061947` |
| aggregate lateral `√tr` change | `−0.02877337862288165%` | `−0.0288%` |

§4i now gives the full range first and labels `0.687`–`1.153` as the top-1%-by-variance subset
(carrying `74.11%` of total variance, median `0.999`), under Joseph's 2026-09-19 §3 rule that
**small aggregate variance share does not make a bin irrelevant to a quoted result**.

**This defect never reached the deliverables** — `0.687` and `1.153` return zero hits across every
`.tex` file. It was a repository-record defect only.

---

## 3. What this correction does NOT do

- It does not re-grade cause 3, cause 5 or cause 7.
- It does not withdraw or qualify the adoption of `3d7465f6…`.
- It does not discharge §6.4 clause (c); that is
  [`DECISION-20260920-joseph-rules-clause-c-disposition.md`](DECISION-20260920-joseph-rules-clause-c-disposition.md).
- It commissions no compute. The verifier: *"No new campaign is required to correct this wording."*

**Co-Authored-By: Claude Opus 5 (1M context)**
