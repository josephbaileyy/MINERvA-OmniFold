Resume your exact PET/F7 role after the Claude-school reset for a small
repair-only round on commit 9d7a4c6. Do not subdelegate and do not run GPU,
Slurm, C++, G2, P3F, nominal, replicas, or covariance.

The independent agy F7 audit PASSed code/control readiness, and its later G2
downstream audit found that the current ROOT→NPZ/launcher interface is not yet
publication-ready. This is still a code/static-test round only; the G2 ROOT does
not exist. Complete these durability/interface repairs without fabricating
runtime evidence:

1. Extend test_mismatch_fails_closed to persist and deliberately tamper the
   background bootstrap factor and background indices, and to fail when
   n_bkg_full or required background inventory/order evidence is omitted.
   Confirm exact global-before-subset data/signal/background replay and no
   nominal-refinement reuse remain intact.

2. Land the F7 implementation's EVIDENCE-BLOCKED state in the canonical
   ND_OMNIFOLD_RUN_LOG and shortest safe STATUS receipt under the repository
   commit gate. If canonical ND STATUS still contains another owner's dirty
   edits, do not absorb them; use the PET co-located status plus RUN_LOG and
   report the PG0 ownership blocker.

3. Inspect the ACTUAL current `dump_pointcloud_inputs.py` and loader key
   contracts. Repair the dumper so a future G2 ROOT must carry exact
   `petSchemaVersion=g2-fullevent-v1`, `hasFullEventSchema=1`, and
   `fullPhaseSpace=1`; old/recoil-only inputs fail closed. Persist the distinct
   reco/data/truth feature schemas, view/time vectors and real stable identities
   without inventing cross-schema counterparts. Add a selected-background loop
   carrying aligned recoil cloud, reco muon/vertex scalars, view/time, `w_bkg`
   and its own MC identity/order hash. Generator labels remain audit metadata,
   never classifier features. Output keys/order/fingerprints must match
   `build_fullevent_loaders` and F7 three-inventory replay exactly. Use a
   transactional temporary NPZ plus atomic rename and strict complete manifest.
   Add login-safe fake/source tests for schema rejection, missing/tampered
   background, identity/order mismatch, vector-length mismatch, interrupted
   output, and forbidden purity fallback. Mark actual PyROOT integration as
   runtime-blocked, not passed.

4. Audit the actual nominal/replica launcher call graph. agy flagged
   `sbatch_pet_nominal_bkgsub.sh` as potentially routing through the quarantined
   recoil loader; verify this rather than blindly replacing an entry point with
   a library module. Patch every real publication launcher/config that can
   select old xps2/recoil-only/purity inputs so it requires the full estimator
   fingerprint, full-schema manifest, and `bkg_mode=negweight-refined`. Add a
   no-GPU dry-run/config test proving missing background/full-schema inputs abort.

Keep the test-only binned Stay-Positive surrogate explicitly impossible to
mistake for production. Production remains hard-blocked on Agent E's reviewed,
built and smoke-validated G2 ROOT plus Agent-B-aligned full-schema NPZ carrying
literal background clouds/scalars/w_bkg. Do not fabricate that evidence.

Run the login-safe test suite, preserve unrelated dirty work, stage only B-owned
files, commit/push the repair, and report exact tests/docs/commit and the named
runtime blocker. Do not edit Agent E's C++/G2 status or Agent C's endpoint paths.
