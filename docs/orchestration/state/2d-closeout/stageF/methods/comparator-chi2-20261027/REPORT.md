# Comparator check: how published neutrino cross-section papers present data-versus-generator χ² (2026-10-27)

**Authority:** `DECISION-20261026-joseph-5d-generator-comparison-presentation.md`, item 4. The check is read-only and comes before any wording is written. It compares published practice with the decision:
- option 1 in the paper: a χ²/ndf table under the reported covariance, with shape-only beside it, a ratio figure and one quantified correlation-sensitivity sentence;
- option 4 in the note: option 1 plus a figure of the modes that carry the χ²;
- no diagonal-only χ².

**Who did it:**
- **Paper selection, reading and quote extraction:** a Claude Opus 5.5 subagent of the paper rewrite lane's claude-school session.
- **The checks below:** the lane itself, Claude Opus 5.5.

## The papers

Each was checked on its arXiv abstract page (title, collaboration, DOI) and read in full from its arXiv PDF. The PDF digests are in `pdf-sha256.txt`. Word counts are the reader's estimate (main text with captions, without references or appendices, ±15%). The target is the paper's roughly 8,800 words.

| arXiv | experiment | title (abstract page) | journal (abstract page) | words |
|---|---|---|---|---:|
| 2002.12496 | MINERvA | Double-Differential Inclusive Charged-Current νμ Cross Sections on Hydrocarbon in MINERvA at ⟨Eν⟩ ∼ 3.5 GeV | Phys. Rev. D 101, 112007 (2020) | ~7.2k |
| 2106.16210 | MINERvA | Measurement of inclusive charged-current νμ cross sections as a function of muon kinematics at ⟨Eν⟩ ∼ 6 GeV on hydrocarbon | DOI 10.1103/PhysRevD.104.092007 | ~6.7k |
| 1802.05078 | T2K | Characterisation of nuclear effects in muon-neutrino scattering on hydrocarbon with a measurement of final-state kinematics and correlations in charged-current pionless interactions at T2K | Phys. Rev. D 98, 032003 (2018) | ~16.5k |
| 2004.05434 | T2K | Simultaneous measurement of the muon neutrino charged-current cross section on oxygen and carbon without pions in the final state at T2K | Phys. Rev. D 101, 112004 (2020) | ~10.8k |
| 2109.12220 | NOvA | Measurement of the Double-Differential Muon-neutrino Charged-Current Inclusive Cross Section in the NOvA Near Detector | DOI 10.1103/PhysRevD.107.052011 | ~8.6k |
| 2402.19216 | MicroBooNE | Inclusive cross section measurements in final states with and without protons for charged-current νμ-Ar scattering in MicroBooNE | Phys. Rev. D 110, 013006 (2024) | ~33k |

**Selection is not a random sample.** Two papers (2106.16210, 1802.05078) were picked partly because they discuss correlation sensitivity, through Peelle's Pertinent Puzzle (PPP). The highest dimensionality among them is 3D, and none is 5D. Three papers are near the target length.

**The quotes:** `quotes.tsv` holds 46 verbatim quotes with section, table or figure, and PDF page, each under item (a)–(d) below. The lane re-checked every one against the text extracted from its PDF, ignoring whitespace and hyphenation and normalizing ligatures: 46 of 46 found. Misspellings that are the paper's own are marked in the location field.

## What each paper does

| paper | (a) χ² table form | (b) diagonal-only χ² printed? | (c) correlation-sensitivity statement, and where | (d) sensitivity variant or decomposition |
|---|---|---|---|---|
| MINERvA 2002.12496 | Table I: standard and log-normal χ² per model, ndf 144 in the caption; no shape-only, no p-values | no | qualitative, in the comparison text (Sec. VII.B): the covariance χ² "partially accounts for such overall normalization effects" | log-normal χ² beside standard; shape-only only as ratio figures |
| MINERvA 2106.16210 | Table I: standard and log-normal χ², ndf 205 | no | PPP: the log-normal χ² "increases significantly for models where the dominant difference with data is the normalization" (Sec. VII); a per-bin metric is distorted by unfolding anti-correlations | per-bin Δχ² against a reference model (Eqs. 1–2, Fig. 19) |
| T2K 1802.05078 | χ² in figure legends, plus appendix tables of full and shape-only χ², regularized and not; no ndf, no p-values | no | PPP: χ² "may therefore not accurately characterise the agreement" (Sec. V); correlations sized | shape and normalization split of the covariance |
| T2K 2004.05434 | Table V: total χ² and shape-only χ², with ndof; also without the last bin, per target, and the O/C ratio | per-target χ² are labelled as "neglecting the correlations between the two measurements" | quantified: normalization is "between 20% and 60%" of the uncertainty, so PPP applies, so shape-only (Sec. V.A) | partial χ² (bin removed, per target); shape-only |
| NOvA 2109.12220 | Table IV: total χ², shape-only scale factor, shape-only χ²; ndf 158 in the text | no | none explicit; full against shape-only is interpreted in the text (Sec. 9) | shape-only |
| MicroBooNE 2402.19216 | Table II: ndf column and χ² per generator and channel, up to 3D (ndf 249); legends print "χ2/ndf=8.70/26" | sub-channel χ² use a subset of bins | yes: a discrepancy along one eigenvector, or a rate mismodel, "may not be apparent from the overall χ2" (Sec. VI.A) | eigenvector decomposition with local and global p-values (Eqs. 24–28, Fig. 15e–h). Used in reconstructed-space model validation, not in the unfolded generator comparisons |

## Against the decision

**1. Paper, option 1: agrees, with two presentation differences.**
- All six papers give a full-covariance χ² per generator, and five state the ndf.
- Shape-only beside full is the T2K and NOvA convention (3 of 6). T2K 2004.05434 Table V and NOvA Table IV are the closest templates.
- **Difference (i): no paper prints χ²/ndf as a ratio.** They print χ² with ndf, either as a column or as a pair such as "8.70/26". The decision's "χ²/ndf table" can follow either form; this is presentation, for Joseph's wording.
- **Difference (ii): both MINERvA papers pair the standard χ² with a log-normal χ²,** motivated by PPP. They do not pair it with a shape-only χ². A MINERvA reader may expect the log-normal column. The decision's shape-only column is the T2K and NOvA practice instead.
- **The quantified correlation-sensitivity sentence fits practice, and is somewhat stronger than it.**
  - Five of six papers carry a correlation or normalization caveat, but only the two T2K papers put a number in it: the normalization fraction, or the correlation sizes.
  - None states how far the χ² itself moves under a change of covariance.
  - Two of the five were selected for discussing PPP, so the rate is inflated.

**2. Note, option 4's mode figure: no direct precedent in this sample, which supports keeping it in the note only.**
- MicroBooNE 2402.19216 publishes an eigenvector decomposition, and states the point the figure relies on: a rate mismodel shows "in the first ϵi, but not necessarily in the overall χ2".
- It uses it for reconstructed-space model validation, not for the unfolded data-versus-generator χ².
- MINERvA 2106.16210's per-bin Δχ² is a weaker relative.
- No sampled paper decomposes an unfolded data-versus-generator χ² into modes. Analysis notes are not public, so this sample cannot say what internal notes do.

**3. No diagonal-only χ²: agrees.**
- None of the six prints one.
- Two print labelled partial-correlation χ² (T2K per target, MicroBooNE per channel). If any sub-block χ² is printed, the convention is to say which correlations it drops.
- All six draw error bars from the square root of the covariance diagonal.

**Does practice differ from the decision?** Not on the three points decided:
- a full-covariance table with a sensitivity sentence in the paper;
- a mode figure only in the note;
- no diagonal-only χ².

Two presentation details are reported to the director for Joseph:
- χ² with ndf rather than a χ²/ndf ratio;
- whether to add MINERvA's log-normal χ² as the PPP-motivated companion. The decision prints shape-only instead.

## Limits

- **Six papers from four experiments, not sampled.** The highest dimensionality is 3D.
- **Only arXiv versions were read,** not the journal versions or supplements.
- **Opened but not profiled:** MINERvA 1811.02774 (standard and log-normal χ² with a PPP paragraph), MINERvA 1910.08658 and MicroBooNE 2301.03700.
- **An absence over six papers is not an absence in the field.** One search for a counter-example, a paper that prints a diagonal-only χ², found none.

## Files

- `quotes.tsv`: 46 verbatim quotes (paper, arXiv id, item, location, quote).
- `pdf-sha256.txt`: the digests of the six PDFs read.
