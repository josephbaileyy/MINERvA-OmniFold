# Independent editor's consult on the remaining strict protections (gpt-6-astra, 2026-10-31)

**By** the paper-tighten lane, as director, for Joseph's question "is there still protected text with strict ruling that
hasn't been relaxed, is this a good idea?". **It rules nothing.**

- **Model:** `gpt-6-astra`, effort high, on codex-school, read-only.
- **Inputs:** the protections inventory, five relaxation decisions and the director's summary (`state-now.txt`), with
  their sha256 in `INPUTS.SHA256SUMS`.
- **Prompt and answer:** `prompt.txt` and `answer.txt`, verbatim.

**Its recommendation:** keep strict control of scientific meaning, and relax routine wording locks and literal build
checks.
- **Keep strict:**
  - the title (A5);
  - `\pubhold`, the acknowledgments and named credit;
  - the truth guardrail;
  - the C items' mandatory publication (wording flexible).
- **Relax:**
  - **A1 Data Availability:** editorial changes checked against the package manifest. Joseph approves release
    commitments only.
  - **A4 abstracts:** Joseph approves the complete revised abstract, not each edit.
  - **A7 claim-scoping sentences:** equivalent wording after a documented equivalence review, with anything unresolved
    going to Joseph.
  - **The FROZEN coverage sentence:** meaning-fixed rather than byte-fixed.
  - **B4 gate-bound phrases:** reworded together with their gate updates.
- **Its caveat:** the repeated 3.0 scores do not show that relaxing will raise quality. Rater comments are diagnostic,
  not grounds for deleting disclosures.
- **Its inconsistency flag:** DECISION-20261028 released Data Availability, while the 10-30 decisions required pinned
  approval for edits to it.
