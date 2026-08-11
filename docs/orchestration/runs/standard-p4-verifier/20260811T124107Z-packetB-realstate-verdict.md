# Packet B real-state verifier verdict — BLOCK on PB2 only

Persistent role `standard-p4-verifier`, UUID
`019f74cb-b85d-7ba0-96c5-dfbd09e59159`, returned **BLOCK** after the real-cluster run on
allocation/step `56636802/56636802.0`.

- **PB1 PASS:** the production validator enumerated the support family, recomputed all 45 band
  hashes, required 40 retained + 5 active/replaced bands and all 48 covariance keys. Stages 5+6
  measured 17m00s; this supports “minutes, not hours,” not a precise PB1 overhead.
- **PB2 BLOCK:** `producing_closure()` and `check_resume_surface()` correctly derived the six-module
  producer surface, but production did not call them. The launcher wrote no `surface_blobs`; the
  checker validated only `unfold_blob`; direct helper fixtures therefore did not establish
  fail-closed resume behavior.
- **PB3 PASS:** three `.PENDING` products are published only after all blockers; the real directory
  ended with exactly the three consumable files and no `.PENDING`/`.FAILED` residue.
- **PB4 PASS:** the projected rejection marker binds parent component-manifest sha256
  `a76904e3b07ec2d74a27c5f745524d716ebef5fa02790ccfc582c5b0f268590c`, propagates through the
  validation/projection sidecars, and is embedded in the projected ROOT.
- **PB5 PASS:** the J36 C++ site is swept, bounded, and documented at the IBU verdict; it is not
  repaired.

The candidate remains self-declared non-adoptable and publication-rejected. The earlier no-email
outcome is expected: `wakerctl emit` has no mail path. It is not a scientific artifact failure. The raw
agentctl receipt is
`docs/orchestration/runs/standard-p4-verifier/20260811T124107Z-send-8202f78f.jsonl` in the live
campaign state.
