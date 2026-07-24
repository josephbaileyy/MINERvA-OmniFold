# Conditional continuation: Gregor checkpoint-compatibility design audit

Resume the existing durable `gregor_source_archaeologist` session
`67e5b4d2-64d5-4bd9-a4e6-9debbfad30cd`. Read-only only: do not edit files,
delegate, submit compute, download or open unverified weights, commit, or
start another role.

Audit `docs/GREGOR_PET2_CHECKPOINT_COMPATIBILITY_DESIGN.md` against the exact
pinned/upstream source archaeology and your prior continuation response.
Check:

- source SHAs and relevant file/symbol list;
- PET2 preset dimensions, forward tensors, padding, conditional/PID/add-info
  widths and state-dict prefixes/shapes;
- whether legacy-exact and corrected PID/mask paths are technically coherent
  and correctly fingerprint-separated;
- whether the proposed PID embedding migration is the only permitted
  shape-changing remap and is information-preserving;
- strict manifest/deserialization/key/shape/license/provenance gates;
- matched random/pretrained experiment cells and negative controls;
- licensing/attribution boundaries and every unresolved checkpoint fact;
- explicit separation from
  `independent-pet2-small-concept-match-v1` and the no-pretrained-evidence
  conclusion.

Return BLOCKER/MAJOR/MINOR findings with exact source evidence and repairs.
State whether the document is a concrete, honest integration design while the
weights remain inaccessible/unlicensed/unhashed.
