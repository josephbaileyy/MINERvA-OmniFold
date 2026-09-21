# PROPOSAL 2026-09-21 — the statistical-methods appendix, and how test consolidation should be done

**CITABLE FOR:** two proposals and the measurements behind them.
**NOT CITABLE FOR:** any change to the note or the suite. **Nothing here is executed.** Both items
were reached in the prose-polish plan and both were deliberately stopped at a proposal, for reasons
given per item.

---

## 1. `app_statmethods.tex` — 1,765 lines, of which 216 are in the wrong document

**Measured 2026-09-21:** the appendix is **1,765 lines across 110 headings** — 29% of the note's
`.tex`. It is the largest single file in the deliverable, larger than `sec_3d` (481) and `sec_pet`
(446) combined.

**Most of it is genuinely statistical methods and should stay:** numerical conventions for
inverting a covariance, the three variance-source procedures, MINERvA's published-covariance
construction, block-sum combination, the covariance-aware `chi^2/ndf` with its
dimension-conditional justification, ill-conditioning and rank deficiency, the closure tests. A
reader checking the statistics needs these, and they are in the right place.

### The one block that is misfiled

Seven consecutive subsections, **lines 1,550–1,765 (216 lines, 12% of the file)** — `10 + 48 + 25 + 34 + 55 + 25 + 19 = 216`, and `1765 − 1550 + 1 = 216`, so the block is contiguous with nothing interleaved:

| subsection | lines |
|---|---|
| The full-event `C_stat` construction: what it is, and what it is not | 10 |
| Construction, stated as a method choice | 48 |
| The measured spread | 25 |
| What is established | 34 |
| Why the two readings of the band are not a live fork | 55 |
| Limitations of the covariance object itself | 25 |
| Recomputing these numbers | 19 |

**These are about PET**, and PET is *diagnostic and method development, not a publication
uncertainty product* — Joseph's 2026-08-20 ruling, which `AGENTS.md` requires to read that way in
note, primer **and** paper. `OI-126` declined the central/statistical pairing; no PET covariance is
adopted. So a reader who opens *Statistical methods* to check how the published uncertainty was
built currently finds, in its last eighth, the construction of an object that is explicitly not a
publication uncertainty.

**PROPOSED:** move those seven subsections to sit with the PET material — either into
`sec_pet.tex`'s own methods discussion or into a `app_pet_cstat.tex` beside it — leaving
`app_statmethods.tex` at roughly **1,550 lines of statistical methods**, and leaving a one-line
pointer where they were.

⚠ **What this is NOT.** It is not a deletion, not a downgrade of the `C_stat` material, and not a
re-litigation of `OI-126`. Every word moves. The claim is only that the material is filed under the
wrong heading, and that the heading is the one a reader trusts to describe the published
uncertainty.

### Why it is proposed and not done

`app_statmethods.tex` carries the `\dead{}` struck-value markup that `check_dead_containment.py`
enforces — the note is required to render **10/10** struck literals as a positive control, and
`\dead{0.069}` in this file is one of the two the PDF stage cannot cover. A move that crossed a
`\dead{}` boundary, or changed which file the containment walk reaches, would be caught late and
confusingly. More importantly, **what belongs in a physics note is a judgement about what the note
is for**, which is not this lane's.

### A second, smaller observation, offered without a proposal

`\subsection{How the pieces fit together}` (70 lines, at 1,412) reads as campaign narrative rather
than method. It may be exactly what a reader wants; it may be the audit trail that commit
`95d03169` took out of the physics argument, returning by a different door. Flagged for the note's
owner rather than judged here.

---

## 2. Test consolidation — the rule, before anyone consolidates

**Measured 2026-09-21: 126 test files, 63,611 lines** against a 5,998-line note. The suite grew
**one test per finding**, which is why it is large and also why it is valuable.

### The hazard, stated first

**A finding-driven suite is a set of point constraints, not a specification.** Green certifies the
findings someone happened to encode, not the behaviour. That cuts both ways, and the second way is
what governs consolidation: **each of those point constraints is the only remaining record of a
defect that actually happened.** Deleting one silently un-encodes it.

Three from this session, each of which a plausible consolidation would have removed as redundant:

- `test_the_UNCLASSIFIED_REMAINDER_IS_PINNED` looks like an arbitrary count assertion. It is the
  ratchet that forces a new launcher to be classified instead of defaulting to unfenced, and it
  caught three files on 2026-09-21.
- `test_s_proj_has_no_UNSANCTIONED_caller` looks like a lint rule. It is a trigger armed for a
  future event, and it fired correctly on two probes that had gone undeclared for a day.
- `test_a_DECOY_library_in_the_spool_would_be_used_and_that_is_CORRECT` looks like a test of
  behaviour nobody wants. Its docstring says *"recorded so nobody 'fixes' it"*.

### The rule

1. **Additive first.** Write the spec-level test that states the behaviour. Land it, green, beside
   the point constraints. Only then consider removing any of them.
2. **Every deletion names the finding it retires** — `BEN-*`, `OI-*` or the commit — in the commit
   message. A deletion that cannot name one is not a consolidation; it is a reduction in coverage
   with a tidier diff.
3. **Never consolidate against a red suite.** A red suite cannot tell you whether the consolidation
   broke something, because it looked the same before. This is not hypothetical here: whole-suite
   collection was impossible on a developer Mac until 2026-09-21, and two test files carried
   standing failures, one of them *deliberately* unable to pass.
4. **Re-run whole-directory, not per-file.** The `sys.modules["ROOT"]` leak repaired on 2026-09-21
   was invisible per-file and fatal to whole-suite collection — a defect that only exists in the
   interaction between files is exactly what consolidation perturbs.

### Sequencing

⚠ **CORRECTED 2026-09-21, SAME DAY. The first version of this paragraph said preconditions 3 and 4
were "now satisfied", and that was premature — I wrote it before the first whole-suite run had
finished.** That run then returned **22 failures**, so precondition 3 was false at the moment I
asserted it. The failures were real and led to the deeper repair described at `root_probe.py`.

**Where they actually stand, measured after that repair:**

| precondition | state |
|---|---|
| **4** — whole-directory runs are possible | **satisfied.** 3,798 tests collect; the run used to abort at collection. |
| **3** — the suite is not red | **substantially, with 8 named exceptions.** Four chunks give 719 + 886 + 888 + 1278 passed and **8 failed**, and all 8 reproduce **by name** at `c34553e5` — two multiprocessing guard tests, six P4 ones. They are standing findings this work did not create and did not close. |

⚠ **And one limitation of that verification, because it is the kind this document is about.** A
single-process full run was killed twice for memory, so the suite was run in **four chunks** —
which does **not** exercise cross-chunk pollution, the very class of defect the `root_probe` repair
addresses. That class was therefore tested directly instead: all five stub installers followed by
every previously-failing module, in one process, worst-case ordering → **745 passed, 8 skipped, 0
failed**. Chunked coverage plus a targeted worst-case ordering is not the same thing as one clean
whole-suite run, and it should not be quoted as one.

Consolidation itself remains unstarted and is **not** recommended before the note's publication
deliverables are settled — it is cost reduction, and it competes with the critical path for the
same attention.

**Co-Authored-By: Claude Opus 5 (1M context)**
