You are the independent publication-plan verifier for the MINERvA OmniFold takeover. Work read-only in the current repository. Do not edit files, submit/cancel jobs, use compute holders, or start subagents.

Audit whether the following currently untracked control documents can be committed as a coherent publication-grade plan, or must be blocked and repaired first:

- `docs/PUBLICATION_COMPLETION_RUNBOOK.md`
- `docs/RESULT_DEPENDENCY_AND_RERUN_MAP.md`
- `nd-unfolding/PET_UQ_REMEDIATION_STATUS.md`

Cross-check them against the current authoritative constraints and state:

- `AGENTS.md`
- `KNOWN_ISSUES.md`
- `docs/OPEN_ITEMS.md`
- `nd-unfolding/pet/FULL_EVENT_FEATURE_CONTRACT.md`
- `docs/orchestration/ROLLOUT-PLAN.md`
- `docs/orchestration/MIGRATION-HANDOFF.md`
- `docs/orchestration/MIGRATION-TAKEOVER-STATUS.md`
- `2d-unfolding/HANDOFF_bkg_negweight/bkg_negweight_state.md`, especially the locked 2026-07-11 user decisions

The latest reconciled constraints are mandatory:

1. Publication FPS/N-D/PET background treatment is `negweight-refined`; PET uses literal aligned background-cloud negative injection followed by Stay-Positive. Purity products are matched controls only. This is a hard gate before scalar FPS/P6 and full-event P5A/P5B production.
2. Existing ten scalar-FPS active endpoint unfolds are purity-footed controls because their launchers omitted `--bkg-mode`; no adoption from them.
3. Publication PET is the full-schema `pet-fullevent-fps-v1` estimator over the extended FPS domain. Reduced/recoil products transfer no central or covariance components.
4. F7 covers full data, signal-MC, and background-MC inventories before subsetting; background factors apply before per-replica Stay-Positive refinement; exact MC draws are reused wherever those inventories participate.
5. G2 full-event branches/CV regeneration precede fresh full-schema P3F endpoints; current reduced-schema endpoints are controls.
6. Project commit gate is literal: uncommitted controls/results do not exist. One canonical home per fact must be preserved.

Check requirement and dependency completeness, internal contradictions, stale reuse/rerun decisions, target/estimator ambiguity, missing provenance/validation gates, impossible or circular ordering, ownership/writer collisions, and whether P0–P8 would actually yield a reproducible publication freeze. Distinguish the legacy recoil-PET remediation plan from the new full-event estimator; it may remain a labeled cross-check but must not masquerade as the publication chain.

Return exactly one top-level verdict, `PASS` or `BLOCK`. A PASS means the three documents can land as-is without permitting a non-publication-grade result. A BLOCK must list every publication-material defect with exact file/line evidence, the smallest correction, and whether the defect blocks committing the plan, blocks production only, or is nonblocking. End with a compact independent post-repair checklist. Do not infer intent from filenames or existing outputs.
