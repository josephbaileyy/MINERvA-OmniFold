Independently review committed G2 source packet `486e53e` for the publication
gate. READ ONLY: do not edit, build, acquire an allocation, run ROOT/event loops,
submit/cancel Slurm, or message another worker. Review the committed diff, not
the owner's prose.

Read AGENTS.md, KNOWN_ISSUES.md, 2d-unfolding/2D_OMNIFOLD_REFERENCE.md,
nd-unfolding/pet/FULL_EVENT_INTERFACE_REQUEST.md,
nd-unfolding/pet/FULL_EVENT_FEATURE_CONTRACT.md, and the relevant Gate 1-3
sections of nd-unfolding/PET_UQ_REMEDIATION_STATUS.md. Inspect actual getter
definitions and tuple-branch conventions available in the repo.

Audit at minimum:

- exact three-schema separation and whether every contract-required feature
  family is implemented or explicitly/deferably absent (including any residual
  energy/MINOS quality detail the source owner may have overclaimed);
- truth/reco coordinate and unit correctness for the muon components and phi;
- data/MC getter symmetry and whether `ev_run/ev_subrun/ev_gate`,
  `cluster_view`, and `cluster_time` are defensible enough to compile/smoke;
- stable identity caching and Phase-18 native-miss behavior, including all new
  dangling branch addresses and explicitNames exclusions;
- vector type/address correctness and structural E/pos/z/view/time alignment;
- default-path preservation, Phase-18.2 truth-first gate/dedupe/completeness,
  selection, POT, universe dump, and full-phase-space behavior;
- ROOT metadata construction/merge semantics and whether Python can actually
  reject old recoil-only products;
- strength and truthfulness of the 474-check static test (look for substring or
  brace-span false confidence and missing negative/integration assertions);
- compile hazards visible from source and any publication-blocking semantic gap.

Return PASS or BLOCK for authorizing an OWNER-HELD INTERACTIVE compile + 1A
full-event FPS smoke. If BLOCK, give minimal exact repairs and tests. If PASS,
give an exact runtime smoke acceptance checklist; do not authorize the
12-playlist array or PET training yet. Preserve Agent E as the durable source
owner and do not propose replacement workers.
