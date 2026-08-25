# SPEC — the F-17(b) tree-comparison instrument

**CITABLE FOR:** what a third lane must build so that F-17(b)'s "differences reported as findings"
is a machine statement instead of two column sets diffed by eye.
**NOT CITABLE FOR:** any F-number's verdict, the far-end evidence, or authority to grade. This
document specifies an instrument. It grades nothing and asserts no measurement.

**Authority.** Joseph's ruling of 2026-08-25, relayed: the instrument is to be authored by a third
lane, not by the lane that produces the far-end evidence. This spec is the deliverable he asked
that lane's author to be handed.

---

## 0. Independence disclosure, read this first

**This spec was written by the lane that produces the F-17(b) evidence.** That is the same lane
§7.0.10 keeps away from grading. Joseph's ruling separates the two roles deliberately: I specify,
you build and you may reject.

Three consequences, and they are binding on you, not favours:

1. **Every clause below is rejectable.** If a requirement is wrong, drop it and record that you
   dropped it. A spec from the evidence-producing lane is exactly the artifact that would be shaped
   to flatter the evidence, and the only defence is that you are free to refuse it.
2. **I must not grade your instrument, and I will not.** If you ask me whether it passes, the
   answer is that I am disqualified.
3. **Do not treat my numbers as inputs.** Everything in §4 is a pointer to something you should
   re-measure. I have been wrong twice today about my own recorded defects (see §3).

---

## 1. What F-17(b) actually obliges

Quoted from the operative rubric on `main`,
`docs/orchestration/REVIEW-CONTRACT-20260822-k0-execution-integrity.md`. **Re-read it at your own
HEAD and quote it by digest**; the deployed tree at `aa67c426` carries a *superseded* 575-line
rubric with zero occurrences of `7.0` and zero of `F-1(b)`, so "the contract" is an ambiguous
referent and must never be used as one.

- **`:621`, the F-17 split row.** Pre-submission half: *"M-1…M-6 re-measured on `MNV_CODE_ROOT` at
  the pinned sha **and** on the canonical checkout, at submission time; differences reported as
  findings."* Post-rehearsal half: *"re-measured **again after the path runs**; M-2's inventory
  claim over the untracked set is the perishable one and is re-tested here."*
- **`:1471`, Freshness.** *"any difference from this document is reported as a finding."*

**The gap this instrument fills.** `measure_m1_m6.py` measures one tree per invocation and does it
well. Nothing turns two of its outputs into a verdict. "Differences reported as findings" is
therefore performed by a human reading two columns into a receipt — no negative control, and no
record of what was compared. F-17(a) was discharged that way at candidate `30ec0707`.

---

## 2. Do NOT build an F-7(b) exclusion instrument

I previously listed "F-7(b) has no exclusion instrument" as a defect and asked for it to be
specified alongside this one. **That was wrong on both halves, and building it would be worse than
leaving it alone.** The corrected finding, with citations you should check:

- **§7.0.9 rules that F-7(b) cannot be tested by this rehearsal, by construction.** P-4 pins the
  per-entrypoint import set as an *identity* taken from the first clean run; the k=0 rehearsal **is**
  that run, so it can only establish the pin. *"F-7's ratchet is never exercised inside this
  contract's scope."* Disposition: F-7(b) is discharged by **recording and committing** the sets,
  and the reviewer must say **in those words** that the pin is recorded and untested.
- **The widening detector already exists**, built for F-7(a) at candidate `b49bc360`:
  `mnv_preflight_exclusions.json` (schema `mnv_preflight_exclusions/1`),
  `mnv_preflight_census.py` (enumerate first, classify second; exit codes 0/2/3), and
  `tests/test_k0_preflight_exclusion_census.py` (13 arms). §7.0.13 requirement 1 is precisely
  *"a test must fail when a production invocation appears that is neither guarded nor on the list."*
- **§7.0.13's three requirements are all PRE-SUBMISSION and were graded at Gate 1**, which passed
  18/0/0.

**An instrument built for F-7(b) would have nothing it could fail on, and would therefore
manufacture a green.** That is the failure mode this campaign already has a name for. If you think
I am wrong, the argument you must defeat is §7.0.9's, not mine.

---

## 3. Two things I recorded that dissolved on re-derivation — read this as calibration

Both were in the deferred-defect list in
`docs/orchestration/measure_k0_farend_f1b_f17b.sh`, and both were written from a remembered *shape*
rather than from the clause.

1. *"`measure_m1_m6.py` computes M-1 non-transitively."* **False.** The tool has no cross-tree
   comparison surface at all — `--tree` is required with no default, one tree per invocation, and
   its own docstring says *"the defect is measuring one tree and reporting about another."*
   Transitivity cannot arise at the n=2 F-17(b) obliges.
2. *"F-7(b) has no exclusion instrument."* **False**, per §2.

**The mechanism, because it will operate on you too:** both were filed under a cause-name that
sort-of fit, and a cause-name displaces the finding it stands in for. The cost is not the mislabel,
it is that the *real* defect never gets written down. Re-derive every claim in this spec from the
artifact before you implement against it.

**One I checked today that HELD**, so that §3 is not read as "distrust everything": the contract
calls M-2 *"an inventory claim about 717 untracked files"* while the tool's `m2()` counts importable
top-level names against the stdlib. These are the same measurement, not a discrepancy.
`repo_modules()` globs `nd-unfolding/*.py` and `2d-unfolding/*.py`, and a glob does not consult git,
so the untracked population is what M-2's zero **rests on**: drop one untracked `.py` whose stem
collides with a stdlib name into either directory and M-2 flips. The 717 is the population, not the
quantity.

---

## 4. Requirements

Numbered so you can reject one by number. Each carries the control that would catch it being wrong.

**R1 — Consume `--json`, do not re-implement any measurement.** Input is two or more
`measure_m1_m6.py --json` documents. The instrument must not compute M-1…M-6 itself. *Rationale: a
rule retyped is a second implementation of it, and this repo has already had one detector rebuild a
bug the campaign's own scanner was fixed for.*
*Control:* feeding it a hand-edited json must change the verdict; the instrument having no
measurement code of its own is checkable by inspection.

**R2 — No default inputs, and fail closed on absence.** Mirror `--tree`'s no-default discipline. A
missing, unreadable, or empty input is a **refusal with a distinct nonzero exit**, never "no
differences found."
*Control:* three arms — absent path, empty file, valid-json-missing-the-`M-4`-key. All three must
exit nonzero, and with a code distinguishable from "differences found."

**R3 — Report per measurement and per tree, and name both sides with their populations.** Output a
matrix, not a boolean. Every row states the measurement id, each tree's value, each tree's identity
(resolved path, `git rev-parse HEAD`, detached-or-branch, porcelain count), and the unit.
*Rationale: the recurring defect here is asymmetric comparison — a delta believed without naming
the unit of each side and the population each was drawn from.*
*Control:* an arm asserting that swapping the two inputs produces the same finding set with the
sides relabelled, not a different finding set.

**R4 — Classify each difference, and make "expected" a declared list rather than a judgement.**
Two classes minimum: `EXPECTED-BY-RULING` (with the citation as data, not prose) and `UNEXPECTED`.
The expected list is an input file, not a literal in the code, so that widening it is a diff someone
can review. At least these are already known to be expected and you should verify each before
declaring it:
- **M-4's behind-count drifts by design.** The measurement doc records it as having *"moved twice"*,
  and `--upstream` defaults to `origin/main`.
- **M-1, M-5 and P-6 are falsified by any commit to `build-k0-execution-integrity`.** Measured
  2026-08-25: that branch is **46 ahead of and 164 behind** `origin/main`, merge-base `8c156a37`.
  Re-measure this; it is the number I was most recently wrong about, having carried "one amendment
  behind" for a day.
*Control:* an `EXPECTED` entry whose citation does not resolve must be a hard error, so the expected
list cannot become a silent suppressor. This is the arm that matters most — an expected-differences
file is a whitelist, and a whitelist with no failing arm is how a gate stops being able to fail.

**R5 — Refuse to report "all pairs agree" as "all agree" at n ≥ 3.** At n=2 pairwise is total and
transitivity does not arise; the instrument must still refuse the inference rather than not
implement it, because the n=3 use is one command away.
*Control:* a fixture of three trees, pairwise-consistent and jointly inconsistent, on which the
instrument must NOT emit a global agreement verdict.

**R6 — Record what was compared, in the artifact.** The output must carry each input's sha256, each
tree's identity from R3, the instrument's own version, and the wall-clock of each measurement. A
comparison whose operands cannot be recovered later is not evidence.
*Control:* an arm that reads the emitted record back and reconstructs which two files were compared.

**R7 — M-2 gets an explicit perishability arm.** F-17(b) singles M-2 out as the perishable claim.
The instrument must flag an M-2 difference distinctly from the other five, and must not let an M-2
change be absorbed into a summary count.
*Control:* per §3's held finding, a fixture that adds an untracked `.py` whose stem collides with a
stdlib name and asserts the flag fires.

**R8 — Exit codes are a documented, disjoint vocabulary.** At minimum: no differences; differences,
all expected; differences, some unexpected; refusal. Distinct codes, documented in `--help`.
*Control:* one arm per code, each asserting the exact integer.

---

## 5. Boundaries

- **Do not run it against the far-end data and report a verdict.** Building and self-testing on
  fixtures is your job; grading F-17(b) is the F-18(b) reviewer's, who must be a fresh non-builder
  (`:1478` — *"A summary attesting 'all controls passed' is a FAIL of F-18"*).
- **The deployment is frozen at `aa67c426` until F-1(b) is filed** (§7.0.19). Do not touch the
  frozen tree. You do not need to: A-2(f) is scoped to the tree named by `--repo`, measured
  2026-08-25 with a discriminating control — same instrument, frozen deploy 782 files
  `listing_sha256 fa3489e2…`, the other checkout 756 / `c2354e6f…`. So work on `main` cannot
  perturb F-1(b), the baseline, or the 782-file listing.
- **Prohibited outright, and none of it is needed here:** leg 6 / `sbatch_finalize_5d_bkgaware_gpu.sh`;
  any member k≠0; the family; adoption, consumption or quoting of any rehearsal product while Gate 2
  is open; re-pointing any receipt-bound file to make a check pass (OI-123); OI-136 sweeps.
- **Never `git add -A`, never `git stash`** — the checkout and the stash stack are shared with peer
  sessions.
- **Do not add `set -u`** to any launcher. `activate-binutils_linux-64.sh` references `ADDR2LINE`
  unbound and killed job `57235710`.
- **File ids:** the close-out lane's OPEN_ITEMS block 120–139 is exhausted. Claim your own
  ten-block and allocate the **first free id in it**, never `max(existing)+1` — that habit produced
  the OI-64/OI-65 collisions and the pre-commit hook will refuse it.
- **A new doc is born ARCHIVAL and invisible to the router.** To be found, a doc needs a `LIVE` row
  in `docs/orchestration/MANIFEST-overrides.tsv`, a regenerated `MANIFEST.tsv`, **and** an entry in
  `CATALOG.md` — `live_doc_indexed.py` enforces the last one for anything newly LIVE. Commit the
  coupled set together; the generated files are digest-bound to the source ones.

---

## 6. When you are done

**Contact the close-out lane** (this spec's author, the 5D publication close-out session) with:

1. Which requirements you implemented, and **which you rejected and why** — the rejections are the
   more useful half, and a spec from the evidence-producing lane that came back with zero
   rejections is a result I would not trust.
2. The commit sha, and confirmation it is an ancestor of pushed `main`.
3. The control matrix: for each of R1–R8, the arm that fires on bad input and the arm that stays
   silent on good input.
4. Anything in §1–§4 you found to be false. Two of the four defects I recorded yesterday dissolved
   when re-derived; assume this document has the same defect rate.

I will read it, I will not grade it, and I will route the grading to the F-18(b) reviewer.
