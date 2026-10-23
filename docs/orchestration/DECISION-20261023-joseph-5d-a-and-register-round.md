# DECISION 2026-10-23 (third) — Joseph: 5D stays configuration (a) for now; one register round under the corpus rules

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- **The 5D integration.** The RE-1 integration (branch `stageF/re1-integration-20261023`; review ADOPT-AFTER-FIXES)
  moved the 3D and 4D central values to configuration (e). It left 5D in (a), for two reasons:
  - the 5D covariance is paired with the (a) central values by checksum (`sec_5d.tex:649-652`), and no (e)
    covariance exists;
  - several printed 5D numbers have no (e) value.

  That defers part of DECISION-20261020 item 1.
- **The register study.** The PRD register study (`state/2d-closeout/stageF/methods/register-prd-study/REPORT.md`,
  PR #273) measured our paper outside the corpus range on every qualifier measure, and proposed rewrite rules R1–R10
  and a KEEP list.
- **The three questions.** The director put them to Joseph:
  1. 5D (a) for now, or not;
  2. one register round under the corpus rules;
  3. (a) whether to remove the NuWro clause from the abstract, and (b) whether to keep the out-of-scope sentence in
     the CLAIM-ADDITION block (`paper_body.tex:725-753`) only if its record requires it.

Joseph's answer, verbatim:

> decision 1: 5d stays (a) for now, decision 2: yes decision 3: a) yes remove it b) yes keep it only if the record requires it

sha256 of the text plus a final newline begins `421d61d06b4c37c4`.

## What is decided

1. **5D central values stay configuration (a) for now,** labelled as such, until an (e) covariance exists. This
   defers that part of DECISION-20261020 item 1. The joint tests keep their configuration (e) data unfold.
2. **One register round on the methods paper,** after the RE-1 integration merges.
   - **The standard:** every printed sentence is true when read with the paper's stated scope. Scope is stated once,
     positively, in the abstract and §I; limitations sit in one numbered subsection.
   - **The KEEP list stands:** qualifiers whose removal makes a sentence false even under the stated scope stay where
     they are.
   - **The note:** the analysis note is the fully qualified companion, and the paper points to it about once per
     subsection.
   - **Method:** the round uses rules R1–R10 as the writer's brief, the independent two-direction review, and a blind
     pairwise comparison against the current version.
   - This replaces, for the paper, the sentence-level guardrail of `register-method/HANDOFF.md` §3. The note keeps
     the sentence-level standard.
3. **(a)** The NuWro clause leaves the abstract. It stays in Sec. VIII F, which `DECISION-20261020-joseph-nuwro-ch-claim.md` also names (the
   paper's source comment, `main_paper.tex:86`). This changes that decision's abstract placement. **(b)** The out-of-scope sentence in the CLAIM-ADDITION block stays only if the record that
   created the block requires it. The writer checks that record and cites it either way.

## Not changed

- Claims and numbers; protected text; the note's text, apart from pointers the paper rewrite needs. No submission,
  deposit or tag.
