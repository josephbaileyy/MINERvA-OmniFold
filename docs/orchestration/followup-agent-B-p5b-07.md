Narrow same-UUID repair to your uncommitted Gate-3 validator. Do not touch any
other files, launch compute, commit/push, or start PET.

The orchestrator review found a deterministic production issue: playlists
1D/1E/1F/1P contain known finite upstream-corrupt reco muons outside the frozen
extended PET domain `[0,30] x [0,120]` GeV. The sampled base smoke validator can
fail its two reco-muon heuristics on these rows. G2 already solved this with the
committed additive exhaustive validator
`nd-unfolding/pet/validate_g2_fullevent_domain.py`, SHA-256
`32634d6832b4c1f6e5f9036a425b7412f004e2de0aa77828106646d7fc6e3739`.
It runs every domain/content check and composes the base smoke validator
`3b5c4ae9...`, superseding only `bkg_reco_muon_valid` and
`data_reco_muon_valid` with an exhaustive bound census. Four G2 recovery
receipts already prove the intended semantics.

Repair only:

- `nd-unfolding/pet/validate_p3f_pet_fullevent.py`
- `nd-unfolding/tests/test_p3f_pet_fullevent_validator.py`

The Gate-3 validator must compose the exhaustive domain validator, not invoke
the smoke validator directly. Fail unless the domain receipt has `status=PASS`,
an empty `fatal` list, no structural non-superseded failures, a complete
untruncated out-of-domain census, exact retained bounds 30/120, and a nested
base validator receipt/hash/result. Bind both domain and base validator paths,
hashes, receipts and results in the Gate-3 work receipt. Preserve your active
identity/census/inventory checks. Add ROOT-free tests for PASS, fatal,
non-superseded base failure, wrong bounds, truncated census/failure evidence,
and the known-domain-recovery semantic shape. Populate a real UTC timestamp in
the runtime receipt. Return changed hashes and full focused+regression results;
leave edits uncommitted.
