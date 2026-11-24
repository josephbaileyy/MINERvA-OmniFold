# PG probe rev 3: line trace against COVFIX-DECLARATION.md §4.1 and §4.2

By the PG session (tune-generator). Rev 3 answers codex-school2's read 2 (`CODEX2-READ-2.md`). Earlier reads and
their dispositions are kept in `CODEX2-READ-1.md`, `AGY-READ-1.md` and `AGY-READ-2.md`. The tests are
`test_pg_probe.py` (`tests-local.log`), and `mutants.py` plants defects (`mutants.log` gives the count). References
are to functions and test classes. "codex a.b" is read a, item b.

| requirement (source) | code | tests |
|---|---|---|
| run on a Perlmutter login node only, and read nothing otherwise (codex 1.5) | `identity`, first in `probe` | `test_identity_failure_reads_nothing`, `test_identity_rules` |
| the product roots are on CVMFS before any content read (codex 1.4, 2.4) | `verify_roots`, `mount_entry`, second in `probe` | `Roots.*` |
| reads only public catalog and configuration files, beneath the verified roots, opened relative to them, regular files only (§4.1 "public configuration, not generated content"; codex 1.4) | `_beneath`, `_open_beneath`, `_open_regular`, `read_file`, `list_dir`, `is_regular`, `_absent` | `Boundary.*` |
| list the genie_xsec v3_04_00 qualifiers (§4.1 probe, bullet 1) | `list_dir(XSEC_ROOT)`; `ups_table` | `test_go_with_02b`, `test_ups_table_rules`, `test_missing_product_stops` |
| the product, path and qualifier convention (§4.1, citing FD-F1-DECLARATION.md:76) | `qualifier`, `catalog` | `test_tunes_and_names` |
| absent, present and unresolved kept apart, by structural and exact matches; fallback only on confirmed absence (§4.1; codex 1.2, 2.3) | `catalog`, `spline_scan`, `VERSION_LINE`, `other_entries` | `Catalog.*`, `test_fallback_only_on_confirmed_absence` |
| CCQE and 2p2h classes from GENIE's own tune configuration, as v3_04_00 loads it (§4.1 probe, bullet 2; codex 1.1) | `find_config` (tune dir, CMC dir, `config/`; the first wins; no fall-through on errors), `parse_xml`, `param_set` (`Default` only), `alg_value`, `model_classes` | `Config.*` |
| every reference resolves through GENIE's registry, hybrid leaves included; unresolved is never novel (codex 2.2) | `master_entries`, `resolve_ref`, `resolve_hybrid` | `test_unregistered_class_or_set_is_unresolved_not_novel`, `test_unregistered_hybrid_leaf_is_unresolved`, `test_registry_rules`, `test_tune_directory_registry_file_replaces_the_default` |
| every effective value records its file, set and raw text (codex 1.1) | `rec["sources"]`: `raw`, `alg`, `registry` or `hybrid` (`default`, `branches`) | `test_go_with_02b`, `test_wrong_root_type_and_value_form` |
| novelty: one of CCQE and 2p2h outside both spent tunes' classes; a new pairing of spent classes is excluded (§4.1) | `decide.novelty`, on the pooled spent classes and branches | `test_new_pairing_of_spent_classes_is_excluded`, `test_cross_slot_class_counts_as_spent`, `test_one_novel_class_suffices`, `test_character_reference_is_decoded` |
| within a slot, branches that disagree on novelty go to the director, before the tune-level rule (director; codex 2.1) | `decide.novelty` (`branches_agree`), `decide.eligible` | `test_branch_disagreement_is_a_director_stop`, `test_g21_hybrid_with_a_spent_branch_stops` |
| u0 is G21_11b_00_000 as §4.1 describes it: SuSAv2 QE through the hybrid, SuSAv2 2p2h shared with AR23 only (§4.1; codex 2.1) | `DECLARED`, `decide.undeclared` | `test_g21_with_a_plain_ccqe_is_not_section_41s`, `test_g21_needs_the_declared_hybrid_set_and_default`, `test_g21_needs_the_declared_2p2h_and_overlap`, `test_g21_2p2h_must_be_susav2mec_itself`, `test_slot1_absent_stops` |
| 02a only on 02b's absence; 02b's exclusion excludes 02a; §4.1's premise that they share classes, checked only on two resolved configurations (codex 1.3; agy 2.1) | `decide`: `same_02 is True` | `test_02b_excluded_excludes_02a`, `test_both_02_absent_stops`, `test_fallback_whose_classes_differ_is_not_chosen`, `test_fallback_with_unresolved_02b_config_is_not_chosen` |
| eligibility separate from novelty; the overlap record against the same pool (codex 1.3) | `decide` → `novelty`, `eligibility`, `overlap_with_spent_pool` (`users`) | `test_go_with_02b`, `test_overlap_is_against_the_pool_not_the_slot` |
| positive controls: F1's pins and the R-3_04_00 classes for the spent tunes | `decide` controls; `SPENT_PINS`, `SPENT_CLASSES` | `test_spent_controls`, `test_spent_pins_are_f1s`, `test_f1_report_names_are_grep_prefixes_of_the_classes`, `test_inactive_set_supplies_nothing` |
| gpg exists, with the pinned flags and the passphrase on fd 3 (§4.2 item 2) | `GPG_BINS`, `ENCRYPT`, `DECRYPT`, `_run_gpg` | `test_flags_are_section_42s`, `test_missing_executable`, `test_fd3_already_open_fails_cleanly` |
| a synthetic round trip reproduces the payload (§4.2 items 2–3) | `gpg_check` | `RealGpg.test_round_trip_and_controls` (GnuPG 2.4.8), `test_honest_fake_passes` |
| a non-zero exit on an integrity failure, with the evidence and the packet aimed at (§4.2 item 2; codex 1.8) | `packets` (partial lengths), `tamper_seipd`, `TAMPER_TEXT`, `WRONG_TEXT` | `test_a_crashing_gpg_is_not_a_refusal`, `test_a_refusal_without_evidence_fails`, `test_a_wrong_passphrase_accepted_fails`, `test_not_seipd`, `test_tamper_hits_the_last_seipd_byte` |
| GNUPGHOME fresh, mode 700, short and node-local; the agent killed; the dir removed (director, 2026-11-23 (b) as amended; codex 1.7) | `gpg_check`, `mount_fs`, `_pid_alive`, `_confirmed_absent` | `test_mode_700_is_required`, `test_a_closed_stdin_is_reopened`, `test_network_parent_is_refused`, `test_failed_kill_fails`, `test_unknown_agent_fails`, `test_surviving_agent_fails` |
| the agent's sockets verified before any gpg use: in the homedir, or gpg's own `/run/user/<uid>/gnupg/d.<hash>` for it, private, on tmpfs; afterwards removed and lstat-absent, on failure too (director's relay of codex 2.6) | `zb32`, `socketdir_for`, `_owned_dir`, `check_sockets`, the `finally` of `gpg_check` | `test_zbase32_vectors_from_gnupg`, `test_socketdir_for`, `test_check_sockets_rules`, `test_a_verified_run_user_socket_dir_is_used_and_removed`, `test_a_socket_dir_left_behind_fails`, `test_cleanup_runs_when_the_crypto_check_fails`, `test_an_unverified_socket_dir_stops_before_gpg_runs`, `test_a_failing_list_dirs_stops_before_gpg_runs`, `test_unconfined_sockets_fail` |
| the launcher sends the bytes it hashed, once, to a reserved output, through a reviewed ssh (codex 1.5, 1.6) | `pg-probe-launch.py`: `main`, `SSH_OPTS`, `REMOTE` | `test_valid_stop_and_go`, `test_refusals_before_ssh`, `test_the_sent_bytes_are_the_hashed_bytes` |
| the launcher accepts only a complete receipt, and hashes it through the reserved descriptor (codex 2.5) | `receipt_problems`, `validate`, `GPG_REQUIRED`, `_sha_through` | `test_an_incomplete_go_is_invalid`, `test_invalid_receipts_are_kept`, `test_the_footer_hash_is_read_through_the_reserved_descriptor`, `test_tunes_and_names` (the launcher's schema and tunes equal the probe's) |

## Limits of these tests

- The CVMFS tree is a stub built to the R-3_04_00 layout, including its `master_config.xml` registry. The real build is
  checked at run time by the positive controls on the spent tunes, which go through the same registry resolution: an
  unexpected layout, registry or class gives a STOP, never a GO.
- The identity check, `/proc/mounts` and `/run/user` are Linux facts the laptop cannot exercise. Their rules are
  tested with injected mount tables and a stand-in `/run/user` tree. On the laptop, the real gpg keeps its sockets in
  the homedir.
- On Perlmutter, the CVMFS mount's type is not known in advance. Any type that is not node-local is accepted at the
  repository's own mount point or at `/cvmfs`, and the type is recorded in `roots_verified.mount`.
- The probe tests the fd-3 passphrase handoff only. The bound PG binary's two-line stdin frame is cov2d's.
