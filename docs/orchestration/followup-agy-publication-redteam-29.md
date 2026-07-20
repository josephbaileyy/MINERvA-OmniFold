Resume the existing agy-publication-redteam worker with UUID
440f42ef-c271-4f77-a410-a4a999166f44 for one read-only pre-launch verdict.
Do not edit files, launch compute, commit, push, or recommend PET training.

Review the exact current files:

- nd-unfolding/pet/validate_p3f_pet_fullevent.py
  sha256 d782a47868863f2fc9a743f25f91549f0ab70a3ce7ff64f4db946b36a2df38ed
- nd-unfolding/pet/sbatch_p3f_pet_fullevent_evloop_array.sh
  sha256 4bda48cc48c321c0091f204e576bc6de3fb61f032b8d768a5da0449ad027e3e1
- nd-unfolding/tests/test_p3f_pet_fullevent_validator.py
  sha256 bbb1771390a4a5868b5fbb8445e9e19eab489d081e1592d7b18cbd2e7e3acc67
- nd-unfolding/tests/test_p3f_pet_fullevent_launcher.py
  sha256 f100167b688d9bdea30fcf13f9d0d666760c619ba97e051692fae303147acfae

The orchestrator has reproduced bash syntax plus 146/146 tests covering those
files and the frozen full-event/G2 contracts. The nested domain validator is
sha256 32634d6832b4c1f6e5f9036a425b7412f004e2de0aa77828106646d7fc6e3739;
the base smoke validator is sha256
3b5c4ae9b954a6db2ac8dadf25abb433cc0024f9ee182e589de654ba44b5f1f8.

Important correction to your prior turn: the historical scalar P3F ROOTs were
produced by the older MD5-e63c binary and cannot be repacked or promoted as
`g2-fullevent-v1`. The required action is fresh 5 bands x 2 endpoints x 12
playlists generation from the frozen raw manifests using the current installed
binary sha256 61d7dfbf7ee38f39e51c656b48702056c773c3d1c5d1b2d9bf08a6da42d2e19b,
source blob b7e1edbce21545f1f824fe706047bd0f943a60ea, and the simultaneous runtime flags
`MNV101_ACTIVE_UNIVERSE=BAND:IDX`, `MNV101_DUMP_POINTCLOUD=1`, and
`MNV101_FULL_PHASE_SPACE=1`. Evaluate that path only.

Check concretely:

1. exact band-major 120-task mapping and 24 raw-manifest hash bindings;
2. current binary/source/interface and three-validator hash gates;
3. exact runtime environment and output naming;
4. per-task collision isolation, dangling-symlink/existence handling, flock,
   work quarantine, receipt-last no-clobber publication, and resume semantics;
5. validator CLI/report compatibility and P3F -> exhaustive-domain -> base
   composition, including known 1D/1E/1F/1P out-of-domain rows;
6. final receipt's ability to bind root, active identity/census, schema/content,
   validators, launcher, source/binary, manifests, and task identity;
7. Slurm resource/absolute-log footing and submit-time self-hash gate.

Return one verdict: PASS TO COMMIT/SUBMIT or BLOCK. BLOCK only on a concrete
scientific, provenance, collision, or executable defect in these exact bytes;
give file/line and a minimal repair. Distinguish remaining runtime evidence
(which each array task's fail-closed validator is designed to produce) from a
pre-launch code defect. Gate 3 remains open and nominal PET remains prohibited.
