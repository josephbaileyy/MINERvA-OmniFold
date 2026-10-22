# Brief: the re-1 lane (2026-10-22)

Read [`COMMON-RULES.md`](COMMON-RULES.md) first; it binds.

## Why this lane exists

Joseph decided (DECISION-20261020-joseph-refined-estimator-shorten-delta item 1) that the higher-dimensional central
values use the refined estimator, configuration (e), with a 2D closure check.

It also bears on an open obligation:
- **The obligation.** Joseph decided on 2026-08-07 to revisit the purity background treatment before submission
  (`RUNBOOK-20260807-gbdt-closeout.md` §2; `DECISION-20260815-joseph-oi6-oi8-oi126.md`; OI-6).
- **Where it stands.** The note now states it as unmet (App. C.6, the executive summary, §12).
- **RE-1's part.** RE-1 is the planned route to it.

## Where RE-1 stands

**Spec:** [`../methods/RE1-SPEC.md`](../methods/RE1-SPEC.md). **Report so far:**
[`../methods/RE1-REPORT.md`](../methods/RE1-REPORT.md) (2026-10-20, 0.0531 of 30 node-h).
- **P5 (5D):** the existing s5p data unfold is already configuration (e) on the full fine grid. No rerun was needed,
  and Figs. 2 and 3 were regenerated from it.
- **C2 (2D closure) and P3/P4 (3D/4D) need new code:**
  - the frozen 2D and ND paths support the refinement only at 100/8 (`refine_stay_positive`, reached only by
    `--bkg-mode negweight-refined`, with no capacity flag);
  - no frozen 2D path draws pseudo-data that include background (RE1-REPORT §2–3).
- **Side finding:** Fig. 1 and four of its numbers did not reproduce from current inputs. This was later traced in
  `../methods/FIG1-CHECK.md`. Read it before touching 2D.

## Task: finish RE-1

1. **Write the code RE-1 needs, as new paths.** Do not edit existing producers; copy and extend them.
   - (a) A 2D path with the refinement at 400/31 and pseudo-data that include background, drawn as in the s5c/s5n
     studies.
   - (b) 3D and 4D data unfolds with the configuration (e) refinement.
   - Each needs unit tests, and a K1-style control: one declared case reproduces a recorded product bitwise, or to its
     recorded rounding.
2. **Declare.** Write `RE1-AMENDMENT-DECLARATION.md` at `docs/orchestration/state/2d-closeout/stageF/methods/re1/`.
   It holds the code shas, seeds (C2: at least 20 per arm, the same in both arms), inputs with sha256, the controls,
   the readouts as RE1-SPEC fixes them, and the compute cap. Open a PR, and message the director.
3. **After binding:** run C2, P3 and P4 and ledger them. Regenerate the higher-dimensional figures and numbers as
   RE1-SPEC (F) says, into your own output directory. Do not write into `docs/analysis-note/`; the director integrates.
   Then write `RE1-REPORT-2.md` in `re1/`, with the independent review, and open a PR.

**Also report, as a fact for Joseph:** how far the refined central values move from the purity ones, per cell,
relative to the total σ. This is what the background-treatment revisit needs. Do not judge whether the obligation is
met; the director takes it to Joseph.

**Inputs:** use the existing ME-FHC inputs that every product was made from. Do not switch to the newer open-data FHC
release. That is an open question for Joseph and the director, and it is not part of RE-1.

**Grant:** RE-1's remaining ≤ 30 CPU node-h ceiling (RE1-SPEC §4; 0.0531 used), regular or debug QOS.

**Done when:** C2, P3 and P4 are produced and reported against RE1-SPEC, the figures and numbers are regenerated into
your output directory, the movement table exists, the review is done and the director has merged it.

## Your file set (disjoint from the other lanes)

- `docs/orchestration/state/2d-closeout/stageF/methods/re1/**`
- New code paths you create (for example `2d-unfolding/re1/`, `nd-unfolding/re1/`) and their tests.
- Coupled generated files: `CATALOG.md`, `MANIFEST-overrides.tsv` and `MANIFEST.tsv`, for your own rows only.

## In flight, do not touch

- The measurement session's work and its jobs (GiBUU F_fallback 60122488).
- The validation lane's file set (`VALIDATION-LANE-BRIEF.md`).
- `docs/analysis-note/` (the director's).
