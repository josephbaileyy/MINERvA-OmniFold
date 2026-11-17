# Consult on the B0, RS1 and RSN drafts (codex-school, 2026-11-12)

**What it is:** an external referee read of three uncommitted drafts. The director commissioned it. It ran on
codex-school (Codex v0.166.0, model gpt-6.1-sol, reasoning high, read-only sandbox, session 01a1d14c; `run-header.txt`).

**The drafts read:**
- the B0 and RS1 controlled rewrite under D3 (DECISION-20261112-joseph-consult-d1-d7.md);
- journal-editor's Supplement S4.4 RS1 paragraph;
- the RSN paper and Supplement text (RSN-BINDING-1 ruling 5).

**Files:**
- `input.txt`: the prompt with the three drafts and their claim tables. The referee saw these and no records.
- `out.txt`: its report.
- `run-header.txt`: the run's header lines.

**Not citable.** The draft sentences in `input.txt` are proposals that Joseph has not approved. None is paper text, and
none may be quoted as a result.

**Verdicts:**
- B0, paper RS1, S4.4 and every RSN paper passage: accept with edits.
- RSN Supplement S4: revise. Its two maxima (2.9 floors and 0.09 σ) were stated as one "largest move", and the
  bound was applied to every cell.

**Its top three:**
1. S4's separate maxima;
2. RS1's tie mechanism kept apart from refinement-stage sufficiency;
3. one smoothing-neighbourhood definition, and flagging against agreement criteria for the held-out tunes.

**How the drafts used it (v3; director-helper-3):** every edit was applied, and none was applied on the referee's
word alone. Its two open record questions were settled from the records:
- **Smoothing unit:** RSN-DECLARATION.md §2.2, "the region cells within R fine bins on every axis".
- **Held-out tunes:** P3 (:240, :309) means the bias criteria. The paper says "Both tunes satisfy the bias criteria",
  so v3 says "satisfy both bias criteria".

Two further questions were also settled from the records:
- **"NuWro shape":** the declaration's "noise-free closure at NuWro's shape" (:123), not the NuWro hybrid truth.
- **S4.4's 1.35:** journal-editor traced it to nd-unfolding/rounding_mechanism_analyze.py:368-377. It is the median
  over the 153 quantities of the seed-to-seed spread after iteration k, divided by that after iteration 1.

An independent meaning read checked each v3 change against its record before v3 went to the director.
