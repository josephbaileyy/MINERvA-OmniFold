# Brief: the validation lane (2026-10-22)

Read [`COMMON-RULES.md`](COMMON-RULES.md) first; it binds.

## Why this lane exists

Joseph's goal is a measurement-results paper, "ideally 5D", but he will defer to what is possible (2026-10-22). The
blocker on the record is that the five-observable statistical intervals do not cover. A residual bias grows with W
after the nominal-truth correction:
- s5c coverage test: `OUTCOME-20260925-s5c-tier-s-futility-fail.md`;
- the diagnosis: `state/2d-closeout/stageF/methods/M2-RATEFAIL-DIAGNOSIS.md`;
- the W-bias test: `state/ki98-wbias-test/REPORT.md`, UNDETERMINED;
- the measurement plan rates MP-4 (validated 5D uncertainties) as having "no feasible route on the record" at the
  frozen targets (`state/measurement-paper/PLAN.md` §0).

D-ID showed that exact binned unfolding leaves about the same residual as the boosted trees
(`state/next-preparation-20261009/d-id/REPORT.md` §11). This lane establishes what can be validated, and at what
dimensionality.

## Task 1: IBU-1

**Spec:** [`../methods/IBU1-SPEC.md`](../methods/IBU1-SPEC.md), frozen 2026-10-21. A binned iterative unfolding
baseline under matched conditions:
- the same simulation, background treatment, data, cells and iteration count;
- truths: nominal, GiBUU E_avail, W1–W3, and the ~10% rate reduction;
- at least 400 pseudo-experiments per truth for coverage;
- the reading rule is fixed in the spec.

**Steps:**
1. Read the spec, D-ID's code (`d-id/did.py`) and the s5c/s5n pseudo-data code.
2. Write `DECLARATION.md` at `docs/orchestration/state/2d-closeout/stageF/methods/ibu1/`. It holds the code shas,
   seeds (the OmniFold studies' seeds where recorded), inputs with sha256, and the readout as the spec fixes it. Open a
   PR, and message the director.
3. After binding: run, ledger, then write `REPORT.md` in the same directory. Open a PR.

**Grant:** ≤ 10 CPU node-h on m3246 (spec §4). Delta (`bhvk`) only after a reproduction control there. Local
machines are allowed, as D-ID used them.

**Done when:** the REPORT reads the spec's rule ("inverse-problem limited", "implementation specific" or "mixed") per
truth, with the independent review, and the director has merged it.

## Task 2: a coverage scoping memo (0 node-h; after IBU-1, or in parallel if it does not depend on it)

**The question.** For a measurement paper, which dimensionality (2D, 3D, 4D, 5D) and which interval construction can
reach validated coverage? What would each cost?

**Read:**
- `state/measurement-paper/PLAN.md` §5 (MP-4) and its phase-0 records;
- the s5c and s5n records, D-ID, IBU-1 and the M2 diagnosis;
- the note's §9 (`docs/analysis-note/sec_5d.tex`);
- the 2D coverage history (§5.2).

**Deliverable:** `SCOPING.md` in a new directory, `docs/orchestration/state/measurement-scoping/`. For each
dimensionality, give:
- what is measured, and what is missing;
- the candidate routes, for example:
  - coarser cells;
  - a different regularization or iteration choice under a declared rule;
  - interval constructions that include the bias (bias-aware or prior-free intervals, MP-4's untested premise);
  - IBU;
- each route's decisive cheap test;
- the cost in node-h and storage.

The memo ends with a recommendation and its uncertainties, for Joseph through the director. It proposes; it does not
decide. Any claim change is Joseph's.

## Your file set (disjoint from the other lanes)

- `docs/orchestration/state/2d-closeout/stageF/methods/ibu1/**`
- `docs/orchestration/state/measurement-scoping/**`
- New code under a new `ibu1/` tool directory you create (for example `nd-unfolding/ibu1/`), or under
  `state/.../ibu1/tools/`. Do not edit existing producer code: copy it if you need to change it.
- Coupled generated files: `docs/orchestration/CATALOG.md`, `MANIFEST-overrides.tsv` and `MANIFEST.tsv`, for your own
  rows only.

## In flight, do not touch

- The measurement session's GiBUU F_fallback (60122488) and its PRs.
- The re-1 lane's file set (`RE1-LANE-BRIEF.md`).
- `docs/analysis-note/`.
