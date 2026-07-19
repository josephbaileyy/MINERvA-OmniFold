Resume as the same independent G2 verifier UUID. Read-only audit the new
additive recovery implementation; do not edit, publish, submit/retry/cancel
jobs, inspect nonfailed playlist artifacts, or replace roles.

New failed evidence:
- Array task 5 / playlist 1E failed only at post-loop validation:
  data_reco_muon_valid=19999/20000; final ROOT and receipt absent; preserved
  work ROOT is 11,651,881,243 bytes.
- Exact data row: tree entry 18278, identity (ev_run,ev_subrun,ev_gate)=
  (16019,40,323), E=991199788.8276 MeV, px=137438994.5772,
  py=-196707117.6083, pz=961714018.8350; measured pT=239964.9294 GeV,
  p_parallel=961714.0188 GeV.
- Direct source AnaTuple run00016019 entry 12886 contains the same native
  MasterAnaDev muon/MINOS values. It is upstream corruption and far outside
  the canonical extended FPS domain pT<=30, p_parallel<=120 GeV.
- Unchanged task-5 retry is deterministic and BLOCKED, as for task 4/1D.

Audit ONLY these additive files plus their referenced canonical hashes:
- nd-unfolding/pet/validate_g2_fullevent_domain.py
- nd-unfolding/pet/recover_g2_playlist.sh
- nd-unfolding/pet/test_g2_domain_validator.py

The canonical production binary, base validator, and launcher remain
byte-identical. Check fail-closed semantics, exhaustive coverage, ROOT formula
correctness, census completeness/caps, exact manifest/base/launcher/binary
binding, locking, no-clobber atomicity, structural-check composition, 1D+1E
recovery-receipt truthfulness, and whether validate-only then --publish can be
authorized. Flag any defect that could admit corrupt in-domain data, omit an
inventory row, race publication, or misstate evidence. Return PASS or BLOCK
with exact required changes. Preserve your UUID.
