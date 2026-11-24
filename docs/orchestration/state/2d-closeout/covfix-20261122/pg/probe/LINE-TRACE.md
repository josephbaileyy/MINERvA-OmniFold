# PG probe rev 2: line trace against COVFIX-DECLARATION.md §4.1 and §4.2

By the PG session (tune-generator). Rev 2 answers codex-school2's read 1 (`CODEX2-READ-1.md`) and agy's read 2
(`AGY-READ-2.md`). Rev 1's agy read and its dispositions are kept in `AGY-READ-1.md`. The tests are `test_pg_probe.py` (`tests-local.log`), and
`mutants.py` plants defects (`mutants.log` gives the count). References are to functions and test classes.

| requirement (source) | code | tests |
|---|---|---|
| run on a Perlmutter login node only, and read nothing otherwise (codex 5) | `identity`, first in `probe` | `test_identity_failure_reads_nothing`, `test_identity_rules` |
| list the genie_xsec v3_04_00 qualifiers (§4.1 probe, bullet 1) | `list_dir(XSEC_ROOT)`; `ups_table` | `test_go_with_02b`, `test_ups_table_rules`, `test_missing_product_stops` |
| the product, path and qualifier convention (§4.1, citing FD-F1-DECLARATION.md:76) | `qualifier`, `catalog` | `test_tunes_and_names` |
| absent, present and unresolved kept apart; fallback only on confirmed absence (§4.1; codex 2) | `catalog` | `Catalog.*`, `test_fallback_only_on_confirmed_absence` |
| reads only public catalog and configuration files, beneath the approved roots, regular files only (§4.1 "public configuration, not generated content"; codex 4) | `_contained`, `_open_regular`, `read_file`, `sha256_file`, `list_dir`, `is_file` | `Boundary.*` |
| CCQE and 2p2h classes from GENIE's own tune configuration, as v3_04_00 loads it (§4.1 probe, bullet 2; codex 1) | `find_config` (tune dir, CMC dir, `config/`; the first wins), `parse_xml`, `param_set` (`Default` only), `alg_value`, `resolve_hybrid`, `model_classes` | `Config.*` |
| every effective value records its source (codex 1) | `rec["sources"]`, `rec["file"]`, hybrid `file`/`set`/`master_config` | `test_go_with_02b`, `test_tune_directory_file_replaces_the_cmc_file` |
| novelty: one of CCQE and 2p2h outside both spent tunes' classes; a new pairing of spent classes is excluded (§4.1) | `decide.novelty`, on the pooled spent classes and components | `test_new_pairing_of_spent_classes_is_excluded`, `test_cross_slot_class_counts_as_spent`, `test_one_novel_class_suffices`, `test_character_reference_is_decoded` |
| a hybrid whose class and component novelty disagree goes to the director | `decide.eligible` | `test_component_disagreement_is_a_director_stop` |
| slot 1 is G21_11b_00_000, required (§4.1) | `decide` | `test_slot1_absent_stops` |
| 02a only on 02b's absence; 02b's exclusion excludes 02a; §4.1's premise that they share classes (codex 3) | `decide` | `test_02b_excluded_excludes_02a`, `test_both_02_absent_stops`, `test_fallback_whose_classes_differ_is_not_chosen`, `Catalog.test_listed_but_unreadable_02b_is_unresolved_not_absent` |
| the 02a fallback only when §4.1's premise is checked (agy 2.1) | `decide`: `same_02 is True` | `test_fallback_with_unresolved_02b_config_is_not_chosen` |
| eligibility separate from novelty; the overlap record against the same pool (codex 3) | `decide` → `novelty`, `eligibility`, `overlap_with_spent_pool` | `test_go_with_02b` |
| positive controls: F1's pins and the R-3_04_00 classes for the spent tunes | `decide` controls; `SPENT_PINS`, `SPENT_CLASSES` | `test_spent_controls`, `test_spent_pins_are_f1s`, `test_f1_report_names_are_grep_prefixes_of_the_classes`, `test_inactive_set_supplies_nothing` |
| gpg exists, with the pinned flags and the passphrase on fd 3 (§4.2 item 2) | `GPG_BINS`, `ENCRYPT`, `DECRYPT`, `_run_gpg` | `test_flags_are_section_42s`, `test_missing_executable`, `test_fd3_already_open_fails_cleanly` |
| a synthetic round trip reproduces the payload (§4.2 items 2–3) | `gpg_check` | `RealGpg.test_round_trip_and_controls` (GnuPG 2.4.8), `test_honest_fake_passes` |
| a non-zero exit on an integrity failure, with the evidence and the packet aimed at (§4.2 item 2; codex 8) | `packets` (partial lengths), `tamper_seipd`, `TAMPER_TEXT`, `WRONG_TEXT` | `test_a_crashing_gpg_is_not_a_refusal`, `test_a_refusal_without_evidence_fails`, `test_a_wrong_passphrase_accepted_fails`, `test_not_seipd`, `test_tamper_hits_the_last_seipd_byte` |
| GNUPGHOME fresh, mode 700, short and node-local; the agent killed; the dir removed (director, 2026-11-23 (b) as amended; codex 7) | `gpg_check`, `mount_fs`, `confinement`, `_pid_alive` | `test_mode_700_is_required`, `test_a_closed_stdin_is_reopened`, `test_network_parent_is_refused`, `test_unconfined_sockets_fail`, `test_confinement_rules`, `test_failed_kill_fails`, `test_unknown_agent_fails`, `test_surviving_agent_fails` |
| the launcher sends the bytes it hashed, once, to a reserved output, through a reviewed ssh, and accepts only a valid receipt (codex 5, 6) | `pg-probe-launch.py`: `main`, `validate`, `SSH_OPTS`, `REMOTE` | `Launcher.*` |

## Limits of these tests

- The CVMFS tree is a stub built to the R-3_04_00 layout. The real build is checked at run time by the positive
  controls on the spent tunes: an unexpected layout or class gives a STOP, never a GO.
- The identity check and `/proc/mounts` are Linux facts the laptop cannot exercise. Their pure parts are tested.
- On a node with `/run/user/<uid>`, gpg's sockets go to its per-homedir runtime directory, which the probe accepts
  and then removes. The laptop's gpg keeps them in the homedir, so only the rule is tested for that case.
- The probe tests the fd-3 passphrase handoff only. The bound PG binary's two-line stdin frame is cov2d's.
