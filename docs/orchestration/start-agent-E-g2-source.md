You are the new durable G2 C++ source-interface owner for the MINERvA-OmniFold
publication campaign. This role is on Claude-personal and is distinct from the
school-account A/B/C workers. Do not subdelegate. Agent A remains standard-P4
only, Agent C remains scalar-FPS/P3F, and Agent B owns the PET Python/training
interface. Do not edit their files.

This first turn is IMPLEMENTATION + STATIC TESTS ONLY. Do not acquire an
allocation, build/install the canonical binary, run an event loop, submit or
cancel Slurm, generate ROOT/NPZ products, or touch active output namespaces.
No scientific result is authorized. The orchestrator will route your patch
through an independent review before any interactive build/smoke.

Read AGENTS.md, KNOWN_ISSUES.md,
2d-unfolding/2D_OMNIFOLD_REFERENCE.md,
nd-unfolding/pet/FULL_EVENT_INTERFACE_REQUEST.md,
nd-unfolding/pet/FULL_EVENT_FEATURE_CONTRACT.md, and
nd-unfolding/PET_UQ_REMEDIATION_STATUS.md Gates 1-3 before editing. Inspect the
actual current runEventLoopOmniFold.cpp and CVUniverse/getter implementations;
do not trust a summary when source differs.

Implement the missing G2 full-event branch contract in
MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp under the existing
MNV101_DUMP_POINTCLOUD gate, preserving every Phase-18.2 truth-first gate,
bilateral dedupe, native-miss row, POT, selection, weighting, and default
non-pointcloud behavior exactly.

Required contract:

1. Three distinct schemas; never fabricate unavailable counterparts.
   - reco signal and data: distinguished reconstructed muon px,py,pz,E,phi,
     qp/charge-curvature, MINOS-match/quality fields that have identical data/MC
     definitions; reconstructed vertex x,y,z.
   - truth denominator/truth side: truth muon four-vector/direction and true
     vertex only. Do not invent truth MINOS/range/qp detector features.
   - selected background: reconstructed muon + reco vertex + reco recoil cloud
     and w_bkg. Preserve generator labels only as audit metadata, never as a
     publication classifier feature.

2. Extend reco/data/background recoil clouds with parallel view and timing
   vectors using existing cluster getters. Assert or structurally guarantee
   equal vector lengths for E,pos,z,view,time on every filled row. Preserve empty
   reco vectors on native truth-only misses.

3. Add stable event identity fields needed for deterministic joins/order hashes
   wherever a real identifier exists: MC run/subrun/nth-event for truth, signal,
   and background; the appropriate real data run/subrun/event identity for
   data. Do not manufacture data/MC counterparts. Ensure Phase-18 appended miss
   rows carry their cached truth identity.

4. Add explicit dump/schema provenance metadata (schema version and enabled
   feature families) sufficient for Python consumers to reject old recoil-only
   ROOTs. Use established ROOT metadata types and avoid hadd-corrupted detector
   constants.

5. Define branch names and units unambiguously and consistently. Preserve
   sentinel/mask semantics: reco quantities on !pass_reco native misses must not
   contaminate normalization or look like valid objects; no truth-only field may
   enter data/reco feature families.

6. Add source-level/static regression tests that fail if required gated branch
   declarations/fills, identity caching, parallel-vector clearing, schema
   metadata, or default-path guards disappear. Include negative assertions for
   forbidden truth detector counterparts and truth leakage. Tests must be
   login-node safe and not pretend to prove ROOT runtime correctness.

7. Update only a shortest co-located implementation status/receipt stating
   CODE-COMPLETE BUT BUILD/SMOKE/EVIDENCE-BLOCKED. Do not absorb the dirty
   canonical ND STATUS/OPEN_ITEMS/KNOWN_ISSUES files or edit Agent B's feature
   contract in this turn.

Preserve unrelated dirty work. Stage only explicit G2-C++-owned files. Run
format/syntax/source tests available without ROOT. Commit and push if and only
if they pass. Report exact branches/getters/units, native-miss handling, files,
tests, commit, and remaining compile/1A/alignment evidence. Explicitly confirm
no binary, allocation, ROOT, NPZ, or Slurm state was changed.
