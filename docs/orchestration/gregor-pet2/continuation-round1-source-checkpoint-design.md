# Conditional-information continuation: Gregor checkpoint-compatible design

You are the existing durable `gregor_source_archaeologist`, session
`67e5b4d2-64d5-4bd9-a4e6-9debbfad30cd`. This is a continuation of the same
read-only source/provenance role. Do not delegate, start another provider,
edit campaign files, or download/checkpoint-execute untrusted artifacts.

Using the exact Gregor commits and sources already audited, produce a concrete
checkpoint-compatible integration design that is explicitly distinct from
the campaign's independent `independent-pet2-small-concept-match-v1` backend.

The design must enumerate:

- exact upstream classes/modules/presets and preprocessing transforms that a
  bit-compatible backend would need to reproduce or vendor;
- input tensor order, shapes, categorical vocabulary, padding/mask behavior,
  globals, conditional inputs, output head, and state-dict naming/shape
  expectations;
- an explicit adapter boundary from audited MINERvA reconstructed
  data/signal/background objects and truth objects into those tensors,
  including where the upstream PID-0/padding and transformed-pT mask hazards
  must be corrected or emulated;
- whether correcting those hazards necessarily breaks raw checkpoint
  compatibility and, if so, safe migration strategies that preserve a
  separately labeled legacy-exact path versus a corrected path;
- strict manifest fields for source SHA, architecture config, preprocessing
  revision, tensor schema, framework versions, weight license, immutable
  checksum, and safe loading;
- permitted transfer/fine-tuning experiments and negative controls that
  separate architecture, preprocessing, and initialization;
- legal/provenance boundary: what may be independently reimplemented, what
  may be vendored under MIT with attribution, and why no pretrained-evidence
  claim is allowed without licensed, hashed, accessible weights.

Use exact file/symbol references from the pinned and inspected upstream.
Return a design suitable for inclusion in the assessment, plus unresolved
questions that only an actual checkpoint manifest or author response can
settle. Do not claim that a design is validated initialization evidence.
