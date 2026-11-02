# BINDING: generator comparisons, CH, the analysis definitions and the lower-dimensional overlap (director, 2026-11-01)

**Binds** [`FD-GENCMP-DECLARATION.md`](FD-GENCMP-DECLARATION.md), with its inputs file `fd/gencmp/INPUTS.sha256`, as
merged in PR #643 at **M = `3410ed0c2a1847ddf590d3869f624bd974f2dce7`** (PR head
`f2cbc54cbdaa9393e0dfe1fbcdb6d2fbec5432d3`).

**Under** `DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md` (#640), item 2 (compute to resolve
limitations), for the inventory's Q08, Q10 and Q26
(`state/2d-closeout/stageF/methods/secondary-results/referee-and-qualifications-20261101/`).

## The code bound (git blob digests at M)

| blob | path |
|---|---|
| `640180613f0ca299a8f77b9be47d5c7c2d0495cf` | `nd-unfolding/fd_gencmp.py` |
| `b5fbcef304f1c46e0c02e5e08d83a902840bd313` | `nd-unfolding/fd_gencmp_kin.py` |
| `fc714e72b2ea0f590db4205598f0f372fa4abe19` | `nd-unfolding/fd_gencmp_rebuild.py` |
| `dc8bb2040c6a9fe073461c604b763b1b5aa2999b` | `nd-unfolding/tests/test_fd_gencmp.py` |
| `b1030df724923a5cad58a302567e6f1af4523110` | `nd-unfolding/tests/test_fd_gencmp_rebuild.py` |

## What the director checked

- **The digests.** `git rev-parse <head>:<path>` gives the five blobs above, matching the lane's list.
- **The tests.** At that head, `python3 -B -m pytest tests/test_fd_gencmp.py tests/test_fd_gencmp_rebuild.py` ran
  locally (own TMPDIR): 96 passed and 3 skipped (ROOT- or Linux-only). The lane reports 47 of 47 under root_6_28 and
  52 of 52 under omnifold_py310 on a Perlmutter login node.
- **The review.** A fresh Sonnet subagent (not sol) reviewed the declaration and the code read-only. Its prompt and
  answer are verbatim in `FD-GENCMP-REVIEW-PROMPT.txt` and `FD-GENCMP-REVIEW-ANSWER.txt`. Every should-fix finding is
  fixed, and §11 answers every finding.
- **The outcome table (§7).** It fixes the paper's minimum text for every adverse branch before any number is read:
  A0 or A1 failing, step D disagreeing, B0 or B2 failing, a quadrant differing. Every outcome is reported, including
  any that makes a χ² worse.
- **Nothing read.** Before this binding, the lane read only listings, stat, receipt JSON and one O_NOATIME sha256 on
  pscratch.

## Rulings

1. **Steps 0, A, B, C and D are bound as declared**, with caps of 2.0 node-h for steps 0–C and 4.0 for D (the 0.25
   node-h probe first, enforced by its job script), 6.0 in all.
2. **Step D's route choice is bound:** the paper uses step A's combination in every outcome. Step D's
   generator-definitions route decides "agree", and its analysis-definitions route is always formed and named if it
   disagrees. GiBUU stays on the correction route, with its hydrogen label carried in every output.
3. **Step C reads its outcome from the reported matrix only.** The 3D comparison is descriptive, at the scale of σ16,
   in either outcome. No 3D covariance is adopted, and its clause must read as no validation in either direction.
4. **No paper edit follows from a readout until Joseph rules on the report.**
   - Any change to a Table IV number or a claim goes to Joseph first.
   - A "differ" in step C is a new problem for the director and Joseph.
   - The paper rewrite lane makes the edits.
5. **The connects are authorized:**
   - **Login node:** step 0's O_NOATIME verification and steps A1 and C.
   - **Jobs:** steps B and D on regular CPU nodes (`-q regular -C cpu`), wall limits of 3 h, from a fresh clone
     detached at M with empty porcelain.
   - **Writes:** only under `/pscratch/sd/j/josephrb/gencmp-20261101/`. Nothing is written to CFS. No GPU, no premium
     QOS, no limit of 12 h or more, and no edits to any existing checkout.
   - **Reads:** every pscratch read uses O_NOATIME. A moved atime is a deviation, reported unprompted and not
     restored.
   - **HPSS:** the step products and receipts get an HPSS copy at the campaign's end. Check `hpssquota` first.
6. **The report** gives each step's readouts, its controls, the outcome it reads under §7, its measured cost from
   `sacct`, and any deviation. It proposes the §7 wording and nothing beyond it.

## Fixed, unchanged

Every claim, number and the abstract until Joseph rules; Table IV as printed; the reported covariance. Nothing is
submitted, deposited or tagged.
