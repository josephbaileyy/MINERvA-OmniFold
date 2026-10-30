# Independent synthesis of the coverage cheap tier (gpt-6-astra, 2026-10-30)

**By** the paper-tighten lane, as director. It is for Joseph, who decides 1B and 4B after the cheap tier reports
(`DECISION-20261028-joseph-d2-approved-and-cheap-tier.md` item 3). **It rules nothing.**

- **Model:** `gpt-6-astra`, reasoning effort high, on account codex-school2, read-only and ephemeral.
- **Inputs:** only the committed reports. Their sha256 are in `INPUTS.SHA256SUMS`: the coverage consult of 2026-10-28,
  `LIMITATION-PLAN-ADDENDUM-20261028.md`, and the F1, readers (3a, 4C), 5A, 3b and 5B reports.
- **Prompt and answer:** `prompt.txt` and `answer.txt`, verbatim. The answer marks each of its inferences.

**CITABLE FOR:** what an independent reader concluded from the committed reports, and its recommendations.
**NOT CITABLE FOR:** any result, any adoption, or a claim that the reported covariance is wrong.

**Its recommendations, in short** (from `answer.txt`):
- **Fund 1B with 4A.** Validate the nominal control first. The cost is 44.5–145 CPU node-h, 22.5 of them production.
  Report per-cell coverage with its standard error of about 0.027 at 300 toys.
- **Do not fund 4B now.** Present the generator χ² as uncalibrated distances.
- **Keep 3a, 3b, 4C and 5A beside the covariance.**
- **Before publication, pursue an audited covariance revision based on 5B,** publishing the original and revised
  comparisons. Until then, print 5B separately and state that the reported uncertainties omit a dedicated
  run-period component.
- **Two corrections it flags:**
  - F1's text says expected exceedance counts require independence. They do not.
  - "C_model is not drawn, therefore overcoverage" is over-claimed.
