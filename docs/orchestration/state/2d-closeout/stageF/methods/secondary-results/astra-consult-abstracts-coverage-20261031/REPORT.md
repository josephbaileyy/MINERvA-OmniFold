# Independent PRD referee's consult on the abstracts and the coverage issue (gpt-6-astra, 2026-10-31)

**By** the paper-tighten lane, as director, under
[`DECISION-20261031-joseph-restyle-install-and-astra-abstract-consult.md`](../../../../../../DECISION-20261031-joseph-restyle-install-and-astra-abstract-consult.md)
item 2. **It rules nothing.**

- **Model:** `gpt-6-astra`, effort high, on codex-school, read-only.
- **Its inputs:** the repository itself, in a checkout detached at PR #619's head `039596e09`. It was not shown the
  Sonnet referee's view.
  - It reports reading against a local `origin/main` at `c7f8c4cff`, and recovering the 1B stage-2 report from
    `1a4815a8a`. That report is on `main` since #618.
- **Prompt and answer:** `prompt.txt` and `answer.txt`, verbatim.

**Its recommendations:**
- **Diagnosis:**
  - The paper's first sentence is overloaded.
  - "With a covariance whose median per-cell uncertainty" is bookkeeping register.
  - The paper abstract is missing the coverage statement.
  - In the note, "but does not test interval widths" repeats the coverage qualifier.
<!-- absence-ok: quotes the consultant's proposed abstract wording verbatim; it is no claim of the record's own -->
- **Whole abstracts, sourced line by line.** Each states the following:
  - the 7.86 % "including a run-period contribution estimated after differences between periods were observed";
  - "These comparisons do not establish generator exclusions" (`paper_body.tex:264`);
  - the bias "exceeding predeclared uncertainty-based thresholds";
  - "The coverage of the reported uncertainty intervals has not been validated."
- **Coverage:**
  - PRD papers commonly neither claim nor disclaim coverage in the abstract. Here the affirmative bias evidence
    warrants one sentence.
  - "Coverage failed" would be false.
  - No general validation is possible.
  - Diagnose gate D before funding toys. A restarted study could at most narrow the gap.

**The director's check:** the paper lines it cites (`paper_body.tex:87, 193, 196, 264, 291`; `values_fived16.tex:2244`)
say what it quotes at `039596e09`.
