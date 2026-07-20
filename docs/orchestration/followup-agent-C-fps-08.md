Continue as the existing Agent-C FPS worker with UUID 4580f42d-77db-4f59-88c4-1b2854f24d82. Preserve your identity and edit only:

- nd-unfolding/pet/sbatch_p3f_pet_fullevent_evloop_array.sh
- nd-unfolding/tests/test_p3f_pet_fullevent_launcher.py

Integrate the now-final Gate-3 validator interface. The validator is
nd-unfolding/pet/validate_p3f_pet_fullevent.py with sha256
36e1a7d1c6ceea48eaccdf71e4cb93d96770d524f666944ee03b17b616a85458.
Its CLI is:

  python VALIDATOR --root ROOT --band BAND --endpoint IDX --playlist PL \
    --work JSON --domain-validator DOMAIN --base-validator BASE

Its atomic JSON uses top-level `verdict`, not `status`. It composes the exhaustive
domain validator itself. The domain validator is
nd-unfolding/pet/validate_g2_fullevent_domain.py sha256
32634d6832b4c1f6e5f9036a425b7412f004e2de0aa77828106646d7fc6e3739 and
the forwarded base validator is nd-unfolding/pet/validate_g2_fullevent_smoke.py
sha256 3b5c4ae9b954a6db2ac8dadf25abb433cc0024f9ee182e589de654ba44b5f1f8.

Repair the launcher and its tests so that:

1. The unresolved P3F hash placeholder is replaced with the exact final hash above.
2. The launcher invokes the exact named-option CLI above and requires `verdict == PASS`.
3. It never invokes the base smoke validator directly. Known finite out-of-domain
   rows in 1D/1E/1F/1P mean a direct smoke invocation is invalid; only the P3F ->
   domain -> base composition is authoritative.
4. It binds and rechecks the P3F, domain, and base validator paths and exact hashes
   before generation, before validation/publication, and in resume validation.
5. Receipts bind the P3F report's actual fields (`expected_active`,
   `observed_active`, `observed_census`, nested domain/base metadata and receipts),
   not nonexistent `identity`/`census` fields.
6. Remove any obsolete standalone base-validator JSON artifact.
7. Use an absolute #SBATCH stdout/stderr path under
   /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/p3f_pet_fullevent/logs
   so submission from the repository root cannot fail before the wrapper starts.
8. Record the full active-interface commit
   2e8c214abc4b3ffc4ef371e8da6b5f107611862f, the installed binary sha256
   61d7dfbf7ee38f39e51c656b48702056c773c3d1c5d1b2d9bf08a6da42d2e19b,
   source git blob b7e1edbce21545f1f824fe706047bd0f943a60ea, and source sha256
   57792e42fe3f5a663016f94b91a5631fc50349135c92b35a08eaefcb85812be3.
   Fail closed if the current source blob/hash differs; do not rebuild or launch.
9. Retain collision isolation, locks, no-clobber hardlink publication, work
   quarantine, fsync, exact 5x2x12 mapping, raw manifest bindings, and the exact
   `MNV101_ACTIVE_UNIVERSE`, `MNV101_DUMP_POINTCLOUD=1`,
   `MNV101_FULL_PHASE_SPACE=1` runtime contract.
10. Update the launcher tests for the bound production form: no unresolved token,
    exact validator hashes, correct CLI/report composition, no direct base call,
    and dry-run/static fail-closed behavior.

Run the focused launcher tests with the root_6_28 Python 3.11 interpreter and report
file hashes plus test totals. Do not submit Slurm, commit, push, or edit documentation.
