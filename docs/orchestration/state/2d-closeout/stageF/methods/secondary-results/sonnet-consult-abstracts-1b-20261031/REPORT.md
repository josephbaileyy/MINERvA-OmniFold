# Independent referee's consult on the 5B abstracts and 1B after gate D (Sonnet, 2026-10-31)

**By** the paper-tighten lane, as director, under Joseph's standing practice of an independent recommendation before
each decision put to him (10-31). **It rules nothing.**

- **Model:** Sonnet (claude-school), a general-purpose subagent, read-only, working only from the five input files.
- **Inputs:**
  - `abstracts-input.txt`: the old paper abstract, and the new paper and note abstracts of PR #619 (not on `main`);
  - four records on `main`, byte-identical to the copies the referee read: `FD-1B-DECLARATION.md`,
    `FD-1B-STAGE2-DECLARATION.md`, `FD-1B-STAGE2-REPORT.md` and `LIMITATION-PLAN-ADDENDUM-20261028.md`, all under
    `state/measurement-paper/5d-community-20261024/`.

  Their sha256 are in `INPUTS.SHA256SUMS`.
- **Prompt and answer:** `prompt.txt`, verbatim, and `answer.txt`, the final answer verbatim plus a final newline.

**Its recommendations:**
<!-- absence-ok: quotes the referee's proposed abstract wording verbatim; it is no claim of the record's own -->
- **Abstracts (Part A):**
  - add "The coverage of the reported intervals has not been validated." to the paper abstract;
  - name the run-period component in the abstract, for example "7.86% (7.29% without a run-period component added
    after the data were examined)";
  - replace the opaque "thresholds set against the reported uncertainty" with what the thresholds are;
  - add "for 8 degrees of freedom" to GiBUU's χ²;
  - check that the fake-data exceedance was re-evaluated against the covariance with the block.
- **Supplemental Material:** ship three files: the reported total, the total without the block, and C_PL,5D alone,
  labelled and hashed.
- **1B (Part B):** a 0 node-h diagnosis of gate D now, time-boxed, with a fork declared in advance: a redesign and a
  rerun of gate D if the cause is localized, otherwise a stop. The [0.9, 1.1] window is not relaxed. The failed
  attempt is disclosed in every case.

**The director's view:** the same on every point.
