# PG probe: line trace against COVFIX-DECLARATION.md §4.1 and §4.2

By the PG session (tune-generator). Each requirement the probe implements, the line in `pg-probe.py` (or the
launcher) that does it, and the test that fails without it. `mutants.py` plants 33 defects; `mutants.log` records
33 of 33 killed. `tests-local.log` is the verbose run of `test_pg_probe.py` (42 tests). References are to functions,
not line numbers.

| requirement (source) | code | test / mutant |
|---|---|---|
| list the genie_xsec `v3_04_00` product's tune qualifiers (§4.1 probe, bullet 1) | `probe`: `os.listdir(xsec_root)`; `XSEC_ROOT` | `test_go_with_02b` (`SomeOther` listed); `test_missing_product_stops` |
| the product, path and qualifier convention (§4.1, citing FD-F1-DECLARATION.md:76) | `qualifier()`, `catalog()` | `test_names`; M12 |
| print CCQE and 2p2h model class names from GENIE's own tune configuration (§4.1 probe, bullet 2) | `model_classes()`: `config/<CMC>/ModelConfiguration.xml`, overridden by the tune's own directory, nested (`config/<CMC>/<tune>/`) or beside it (`config/<tune>/`); override files that disagree are unresolved | `test_tune_subdir_overrides_cmc`, `test_peer_tune_dir_overrides_and_conflicts`; M11, overrides-conflict and peer-dir mutants |
| CCQE = `XSecModel@genie::EventGenerator/QEL-CC`, 2p2h = `.../MEC-CC`, exact key | `_PARAM` regex, `SLOTS` | `test_other_slots_are_not_read_as_qel` (QEL-NC, QEL-CC-CHARM); M10 |
| commented-out entries do not count | `_COMMENT.sub` | `test_comments_are_ignored`; M08 |
| an ambiguous entry is not guessed | `len(vals) > 1` → `problems` → "unresolved" | `test_duplicate_entry_is_unresolved`; M09 |
| raw context lines are printed, so a parse can be checked by eye | `rec["lines"]` | `test_context_lines_without_xsecmodel_are_kept`, `test_go_with_02b`; M18 |
| the same for the spent tunes (director's message) | `ALL_TUNES` includes `SPENT` | `test_spent_class_control` |
| **positive control**: the spent tunes' parsed classes equal FD-F1-REPORT.md §1.3's | `decide`; `SPENT_CLASSES` | `test_spent_class_control`, `test_spent_classes_are_f1_reports`; M07 |
| **positive control**: the hash path reproduces F1's pinned spline, README and version line | `decide`; `SPENT_PINS` (equal to `gen5d_v3.SPLINE_PINS`) | `test_spent_pin_control`, `test_spent_version_line_control`, `test_spent_pins_are_f1s`; M05, M06 |
| novelty: qualifies only if at least one of CCQE and 2p2h is used by neither spent tune; both among the spent classes, even in a new pairing, excludes (§4.1) | `novel()`, on the pooled spent set | `test_new_pairing_of_spent_classes_is_excluded`, `test_one_novel_class_suffices`, `test_cross_slot_class_counts_as_spent`; M01, M02 |
| slot 1 is G21_11b_00_000, required, no fallback (§4.1 list item 1, "Both are required") | `decide` | `test_slot1_absent_stops`; M04 |
| 02a only on 02b's **absence**; a novelty exclusion of 02b excludes 02a (§4.1) | `decide` | `test_fallback_only_on_absence`, `test_02b_excluded_excludes_02a`, `test_both_02_absent_stops`; M03 |
| present in the product but unparsable config, or a qualifier directory without its spline file or README, is a STOP, not an absence | `catalog` (`present` = the directory, `complete` = both files); `judge` → "unresolved" / "incomplete" | `test_present_without_config_is_unresolved_not_fallback`, `test_incomplete_02b_is_a_stop_not_a_fallback`; incomplete mutants |
| 02a shares 02b's classes (§4.1's premise); a fallback whose configured classes differ is a STOP | `decide` | `test_fallback_whose_classes_differ_from_02b_stops`; mismatch mutant |
| the overlap record (§4.1, "the overlap record ... committed") | `overlap_with_spent`, `02a_02b_same_classes` | `test_go_with_02b` |
| GENIE_XSEC_TUNE handling (director: for setup_genie_v3.sh) | `ups_lines()` | `test_go_with_02b`; M19 |
| gpg exists (§4.2 item 2, "PG stops if the probe does not find gpg") | `gpg_check` | `test_no_gpg`; M17 |
| the pinned flags, verbatim, passphrase on fd 3 (§4.2 item 2; director 2026-11-23) | `ENCRYPT`/`DECRYPT`, `_run_gpg` (`dup2` to 3, `pass_fds=(3,)`) | `test_flags_are_section_42s` (parsed from the declaration); M13 |
| synthetic round trip reproduces the payload (§4.2 items 2–3) | `gpg_check` | `test_round_trip_and_controls` (real local gpg 2.4.8) |
| a non-zero exit on an integrity failure (§4.2 item 2) is observed, not assumed | tampered-ciphertext and wrong-passphrase decrypts must exit non-zero | `test_a_gpg_without_integrity_fails` (XOR fake gpg); M14 |
| GNUPGHOME: a fresh mode-700 throwaway dir; `gpgconf --kill gpg-agent` must exit 0; removed; no surviving agent, with `ps` required to work so that "none" is measured; ~/.gnupg neither created nor touched (director 2026-11-23, (b)). **The dir is node-local** (the login node's temp dir), not under `$SCRATCH`: see `AGY-READ-1.md` finding 1 | `gpg_check`, `_agents` | `test_round_trip_and_controls` (real agent seen before the kill, none after), `test_a_surviving_agent_fails`, `test_failed_kill_fails`, `test_a_blind_agent_check_fails`, `test_a_failing_ps_is_not_read_as_no_agents`, `test_a_touched_user_gnupg_fails`, `test_honest_gpg_passes` (an HMAC fake gpg with no agent); the gpg mutants |
| the probe never clobbers an fd it does not own | `_fd_open(3)` before the pipe | `test_fd3_already_open_fails_cleanly`; fd mutant |
| the passphrase is synthetic and never printed | `secrets.token_hex(32)`, not in `rec` | by inspection: no `pw` in any record |
| reads catalog and configuration only, writes nothing else | `catalog`, `model_classes`, `ups_lines` open read-only; only `mkdtemp` writes | `test_probe_writes_nothing_in_cwd` |
| the launcher runs exactly the reviewed bytes, once | `pg-probe-launch.sh`: sha256 check, refuses an existing output, `python3.11 -I -B -` on ssh stdin, rc preserved | `Launcher.*`; M20–M23 |

## Limits of these tests

- The real CVMFS layout. If GENIE's configuration does not use the `XSecModel@genie::EventGenerator/QEL-CC` key
  form, the spent-tune class control fails and the probe STOPs; the printed context lines then show the actual form.
  That failure mode is safe (a STOP), but it would cost a second connect.
- Perlmutter's gpg version and `ps`. A gpg older than 2.2.7 rejects `--no-symkey-cache`, which the probe reports as
  a failed round trip (a STOP), as §4.2 intends.
- gpg-agent's socket-path limit: a long GNUPGHOME makes the agent fail to start (seen locally with a 130-character
  path). The login node's temp dir is short. The real seal must also use a short, node-local GNUPGHOME.
