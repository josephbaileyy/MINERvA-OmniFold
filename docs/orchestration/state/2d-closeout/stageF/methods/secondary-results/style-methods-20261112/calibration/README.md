# Calibration of the style-only rater on published papers (2026-11-12)

**What was run:** the director ran the style-only referee prompt on two published unfolding-methods papers, to see
where this rater places published work. The prompt is byte-identical to rounds 1–3 (`../round1/prompt.txt`, sha256
`8ee711db…`). The rater is the same: gpt-6.1-sol, high, on codex-school.

| arXiv | paper | published | style score |
|---|---|---|---|
| 2404.18807 | Huetsch et al., "The Landscape of Unfolding with Machine Learning" | SciPost Phys. 18, 070 (2025) | **7/10** |
| 1705.03568 | Tang et al., "Data Unfolding with Wiener-SVD Method" | JINST 12, P10002 (2017) | **6/10** |

Each directory holds:
- `gpt.txt`, the reader's report, byte-identical to its run's output;
- `inputs.sha256`, the digests of the arXiv PDF and of the reader's input (the prompt followed by the PDF's text
  extraction).

The papers' texts are not committed, since they are other authors' work. Each can be regenerated from the arXiv PDF
with that sha256.

**Reading (the director):**
- Under this rater, the paper's 6/10 equals a published JINST methods paper.
- 9/10 may be above what the rater gives published work.
- Both reports ask for the same kinds of edits as ours: a results-bearing abstract, consolidated qualifications, one
  job per paragraph, and consistent terminology.
- The target becomes at least the best reference, 7/10 under this rater, with the referee's concrete items cleared.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** how this rater scores two published papers under this prompt.
- **Not citable for:** any judgement of those papers' science; any finding of this paper.
