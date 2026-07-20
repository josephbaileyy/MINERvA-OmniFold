Resume the same agy-publication-redteam UUID
440f42ef-c271-4f77-a410-a4a999166f44. This is a read-only recheck after the
orchestrator rejected an overclaim in your prior PASS. Do not edit, launch,
commit, push, or discuss nominal PET.

Your prior response said the per-task receipt embedded a terminal COMPLETED
`sacct` status. That was false: a task cannot truthfully record its own terminal
accounting before it exits. It also said the receipt bound comprehensive nested
report evidence, but the then-current `pick(...)` calls returned null because
the P3F report keys are `domain_validator` and `base_validator`. Treat these as
verification misses and inspect the corrected bytes rather than repeating the
prior conclusion.

Current exact files:

- nd-unfolding/pet/validate_p3f_pet_fullevent.py
  sha256 d782a47868863f2fc9a743f25f91549f0ab70a3ce7ff64f4db946b36a2df38ed
- nd-unfolding/pet/sbatch_p3f_pet_fullevent_evloop_array.sh
  sha256 7c9018edf6cb20424a8ea116640b31dbf56c95de53f3087a045535abfd8dde5d
- nd-unfolding/tests/test_p3f_pet_fullevent_validator.py
  sha256 bbb1771390a4a5868b5fbb8445e9e19eab489d081e1592d7b18cbd2e7e3acc67
- nd-unfolding/tests/test_p3f_pet_fullevent_launcher.py
  sha256 be387126546cc01fe5cd7cb15afd661aaa7ab36fffea4bcd232c0abb8417fa47

The corrected launcher now:

1. validates build-commit/source-blob ancestry and exact working source;
2. performs a complete P3F/domain/base integration check before ROOT publication;
3. embeds the complete atomic P3F validation report in the final receipt;
4. copies actual domain/base/inventory/counts evidence, with no null fallback;
5. deep-resume revalidates root hash, full inventory/active/census identities,
   P3F zero-failure component verdicts, domain PASS/exit 0, allowed-only base
   supersession, validators, manifests, binary/source/launcher and duplicate
   top-level copies;
6. explicitly omits terminal `sacct` state from the running task receipt;
   terminal accounting belongs to the later complete Gate-3 manifest.

The orchestrator ran 146 frozen contract/validator regressions plus 29 launcher
tests. The latter now byte-compile every embedded Python block and execute a
synthetic receipt-build/deep-resume round trip plus a tamper rejection.

Return PASS TO COMMIT/SUBMIT or BLOCK on one concrete remaining defect. Verify
the exact current code and do not claim any field absent from it. Runtime ROOT
content remains future evidence produced by each fail-closed task, not a reason
to block correct launch code. Nominal PET remains prohibited until the complete
committed Gate-3 manifest PASS.
