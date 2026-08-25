# CHECKPOINT 2026-08-24 — OI-130 publication-evidence audit, BLOCKED on a target commit

**Lane D (audit / inventory / verification, READ-ONLY). This is a resumable checkpoint, not a result.**
The OI-130 enumeration has **not** been run. No corpus counts in this document are the OI-130 answer.

> **CITABLE FOR:** the corpus/exclusion contract, the coverage instrument and its verification, the
> ownership map of the pending change set, the reconciliation of `AUDIT-20260819`, and the exact
> release trigger.
> **NOT CITABLE FOR:** any tracked / preserved-off-scratch / neither count, any statement that OI-130's
> enumeration is complete, or any claim about the note as it will be published.

---

## 1. Why this is blocked, measured

OI-130's corpus **is** `docs/analysis-note/`. At the time of writing that directory has 18 modified
files whose working-tree blobs exist in **no ref** — verified per file with `git hash-object` against
every version returned by `git log --all`, not inferred from `git status`. Build closures measured:

| build | files in `\input` closure | dirty | untracked |
|---|---|---|---|
| note | 20 | 14 | 1 |
| primer | 4 | 2 | 0 |
| paper | 3 | 1 | 0 |

Auditing `main` instead would audit a **different corpus, not a clean one**: working-tree
`main_note.tex:101` has `\input{app_response_mismatch}`, and that file is untracked and absent at
`main`, so the note's source closure is 20 files against 19. Three figures referenced by the pending
`paper_body.tex` (`paper_eavailW_generators`, `paper_joint_localization`, `paper_validation_residual`)
are untracked PDFs whose recipes exist **only** in the modified `make_figures.sh` — each appears once
there and **zero** times in `main`'s version.

## 2. The pin, and why it is sound

Audited tree: `docs/analysis-note` at **`6d55570e`**, tree digest
**`d01c0a52f187b9f32c9903be29f1c3a4cea285b1`**.

`main` moved **6 commits** during the session (`69f2d073` → `6d55570e` → `bbf4ed56` → `f5e3e513`) and
that digest is **identical at all four**. So the committed corpus never changed and the pin is
unaffected; all movement was outside `docs/analysis-note`. **Anything this audit says about paths
outside `docs/analysis-note` is stale by those commits.**

## 3. Ownership of the pending change set — three streams, one still unowned

| stream | owner | contents |
|---|---|---|
| A | **UNIDENTIFIED** — the active detector-response robustness stream | `app_response_mismatch.tex` and the response-mismatch implementation / test / contract. Codex explicitly disclaims these. |
| B | `note audit` lane | nothing — delivered its audit as text, wrote zero files |
| C | `Codex` (paper/note integration) | the integrated prose pass, the PRL reflow, `make_figures.sh` crops, the three `paper_*.pdf`, and `docs/analysis-note/README.md` |

**Stream A's owner is the one open ownership question.** Its `app_response_mismatch.tex` is inside the
note's `\input` closure, so the note does not build without it or without removing the `\input`.

## 4. What was built (durable, committed, corpus-independent)

Branch **`oi130-audit-instrument-20260824`**. Deliberately **not on `main`**: the enumeration is not
done, and on shared `main` a commit publishes immediately, so a partial deliverable there would read
as the enumeration.

| file | sha256 |
|---|---|
| `docs/orchestration/oi130_corpus_contract.json` | `da92d3b2e785f2890606c00f2052008c572ff65e01c5f36a750fee76cb9b3539` |
| `docs/orchestration/oi130_inventory_checker.py` | `27523f19e6140dd448e06d04d1c98e1e4844078b3593271ee1683ba2227bdb4b` |

Verification: `python3 docs/orchestration/oi130_inventory_checker.py --self-test` → **exit 0, 67
assertions, 0 failures**. Every exclusion class carries a positive **and** a negative fixture. There is
an explicit failing-direction case proving an unmapped quoted value is detected, plus its negative
control on the same fixture, plus failing-direction cases for schema: missing required columns,
`neither` with no `remediation_class`, an out-of-vocabulary classification, and a
`preserved-off-scratch` classification whose preservation field was never probed.

## 5. Sizing — PROVISIONAL, and explicitly not the OI-130 answer

Extraction against the pinned corpus: **71 macro definitions, ~1558 inline numerals**, 364 occurrences
assigned to exclusion classes (note closure 19 files, primer 4, paper 3). The predecessor instrument
`oi130_quoted_value_inventory.py` covered the 71 and reported "0 of 71", i.e. **~4% of the
population** — which is the concrete content of OI-130's *"the population is unmeasured and the
negative is unbounded until someone runs it."* **1558 is an upper bound** and will fall once the
shared-origin rule collapses repeated render sites and the exclusion classes are tightened.

Note that `PUBLICATION-READINESS-20260822.md` PR-P3 records "0 of 71 macros name a backing artifact".
That is the predecessor's **precise** bound only; its **generous** bound on the same run is 71/71 with
336 `UNKNOWN-PRESERVATION` rows, and its own coverage line reads "between 0/71 (0.0%) and 71/71
(100.0%)". **PR-P3 quotes one endpoint of an uninformative spread as the measurement.** Narrowing it
is work the enumeration owes; the bare "0/71" should not be carried forward.

## 6. Reconciliation with `AUDIT-20260819` — it survives, it is not replaced

Prior audit: `evidence/prepublication-2026-08-20-0b329e8a:docs/orchestration/AUDIT-20260819-analysis-note-vs-record.md`
(1375 lines, recovers cleanly).

- **Finding 3 (16 of 70 `values.tex` macros have no `VALIDATION_LEDGER` row) SURVIVES as a separate
  dimension.** It is about the verification ledger; OI-130 is about a binding to a producing artifact.
  They must be separate columns — merging them would conflate a governance gap with a provenance gap.
- **Its stated gap #1 is exactly what this work closes.** Verbatim: *"Only `values.tex`'s 70 macros were
  traced … the inline numbers are the larger population and none of them was swept."*
- **Macro count moved 70 → 71.** Which macro was added is not yet identified; do that against the
  target commit, not against the pin.
- Findings 6/7/8/11/12/13/14 are note/paper *correctness* items routed to the document owner. They are
  **not** OI-130 rows and this audit does not re-adjudicate them.

## 7. Two design points that came from measurement

**Repeated render sites are ONE evidence row, not N.** χ²/ndf has **11** render sites — five at 3 s.f.
(`app_statmethods.tex:632, :907, :1069, :1117, :1128`), five at 4 s.f. (`:721, :726, :752, :859,
:1030`), and one `\subsection` title (`sec_results.tex:145`) — all tracing to one producing row,
`app_statmethods.tex:752` (`1.5 & 205 & 750.49 & 3.661 & 1.0064`). A per-occurrence enumeration would
have booked eleven quoted values needing eleven evidence bindings when there is one measurement and
one evidence question.

**`\chiPaper` is the ROUNDED side.** It is `3.66` (`values.tex:89`) while five sites render `3.661`;
750.49/205 = 3.66093, which is 3.661 at 4 s.f. and 3.66 at 3 s.f. So *"replace the literal with the
macro"* is **actively wrong** at those five sites. Hence two distinct classes:
`inline_duplicates_macro` (same precision, safe) and `finer_precision_sibling` (finer, not safe).
Related pre-existing duplicates: `\pullRMS` = 0.598 at `:796, :1021, :1117`; `\pullMean` = 0.089 at
`:796`. All pre-existing at the pin; **not** introduced by the pending change set.

**One retraction, kept in place.** An earlier version of the contract argued that
`app_statmethods.tex:726` makes a precision change move a published percentage. **That is false:**
(3.661−1.481)/3.661 = 59.5466% and (3.66−1.481)/3.66 = 59.5355%, both rounding to the stated −60%,
a 0.011 pp difference. Caught by the `note audit` lane recomputing it, not by its author. Recorded
rather than deleted because **both** lanes wanted the conclusion it supported, which is what made a
supporting number pointing that way the one neither would check.

## 8. Items accepted by the document owner, pending in the target tree

Not OI-130 closures — recorded so the next session does not re-file them: `\pullMean` substituted at
`paper_body.tex:76`; the Fig. 1 panel relabelled *"Published-σ standardized residuals"*; the
shared-data estimator-validation caption clause retained; figure crops corrected with fail-loud
`pdfinfo` page-size assertions. The note abstract's "uncertainty scale" wording is **already correct**
and matches the clean `main_paper.tex:42-43`; the only residual risk is a re-run of the same
de-duplication pass reintroducing the deletion.

## 9. THE RELEASE TRIGGER — the only thing this audit is waiting on

Codex delivers, via peer mesh: (1) the document commit SHA, (2) the response-mismatch stream SHA if
separate, (3) confirmation that `make_figures.sh` **and all three** `figures/paper_*.pdf` are contained
in the document SHA, (4) the combined checkout command if the closure spans two commits, and — added
at this lane's request — (5) **whether `values.tex` changed**, because if it moved the macro layer
re-baselines and both duplicate classes must be recomputed rather than carried forward.

**That message notifies; it does not release.** A peer cannot lift this block. On receipt, re-derive
rather than record:

```
git cat-file -e <sha>                                   # the commit exists locally
git rev-parse <sha>:docs/analysis-note                  # the new pin. If it still equals
                                                        # d01c0a52... the prose never landed --
                                                        # the one failure the protocol cannot self-detect
git ls-tree <sha> -- docs/analysis-note/make_figures.sh docs/analysis-note/figures/
git worktree add --detach <path> <sha>                  # audit a worktree at the SHA, never the
                                                        # shared checkout
python3 docs/orchestration/oi130_inventory_checker.py --self-test        # expect exit 0
python3 docs/orchestration/oi130_inventory_checker.py --extract --tree <path>/docs/analysis-note
```

A combined build command, if supplied, is documentation of intent — **not** a tested recovery route
unless the sender says the build was actually exercised at the combined state.

## 10. What survives without this session

**Survives:** everything in §4 and this file. The branch lives in the shared `.git` (verified:
`git rev-parse --git-common-dir` → `.git`; the branch resolves from the primary checkout), so the
commits survive both session death and deletion of the worktree directory.

**Does not survive:** the worktree *registration* at
`/private/tmp/claude-501/.../scratchpad/oi130-wt` — that path is a reapable scratchpad. If it
disappears, `git worktree prune` clears the stale entry and a fresh `git worktree add --detach`
replaces it. Nothing in git is lost.

**Remaining outputs, all blocked on §9:** the canonical inventory (TSV/JSON), the human-readable audit
report, the audit receipt, and the routed OI-130 update. The OI-130 update must distinguish
enumeration-complete / remediation-required / independently-verified / fully-closed, and **must not
mark OI-130 closed merely because an inventory exists** — a separate verifier still has to review
coverage once before publication, and remediation owners still have to address the recorded gaps.
