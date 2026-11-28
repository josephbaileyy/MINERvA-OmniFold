# PG probe: codex-school2 read 2 (NO-GO) and the rev 3 dispositions

cov2d ran codex-school2's confirm of the rev 2 probe (`93e94459`). The report is
`~/cov2d-work/reads-for-director/codex2-tgprobe-93e94459-r2-REPORT.md`, sha256
`fcb4fe270ed0561b3025a698cc359af49430b50f506bff666643e197bdb059ca`. It judged round 1's items 3, 5 and 8 correct and
items 1, 2, 4, 6 and 7 narrowed but still blocking. It gave 6 blocking and 2 non-blocking items. They are restated
below by the PG session, not quoted, and each disposition is the PG session's. Rev 3 changes `pg-probe.py`,
`pg-probe-launch.py`, `test_pg_probe.py` and `mutants.py`. The director's relay tightened item 1 beyond the hybrid
rule it had accepted, and item 6 superseded its looser socket acceptance.

**Public sources used.** These were fetched on 2026-11-23, by curl, into the session's scratchpad.
- GENIE-MC/Generator at tag `R-3_04_00`:
  - `config/master_config.xml` has one `<config alg="genie::X">` entry each for HybridXSecAlgorithm,
    LwlynSmithQELCCPXSec, NievesQELCCPXSec, SuSAv2QELPXSec, RosenbluthPXSec, EmpiricalMECPXSec2015,
    NievesSimoVacasMECPXSec2016 and SuSAv2MECPXSec.
  - Each of those files has root `<alg_conf>` and holds the param_set the tunes use: Dipole for LwlynSmith, Dipole
    and ZExp for Nieves QE, and Default for the others.
  - `HybridXSecAlgorithm.xml`'s set `SuSAv2-QEL` has default `SuSAv2QELPXSec/Default`, six free-nucleon CC branches
    `LwlynSmithQELCCPXSec/Dipole`, and two EM branches `RosenbluthPXSec/Default`.
  - `Algorithm::FindConfig` looks a registry up by `<alg>/<set>` and reports "No Configuration available" when it is
    missing.
- GnuPG `common/homedir.c` at gnupg-2.2.27 and gnupg-2.4.5, `_gnupg_socketdir_internal`:
  - For a non-default homedir, the socket dir is `<prefix>/d.` + zbase32 of the first 120 bits of SHA-1(homedir).
    The prefix is `/run/user/<uid>/gnupg`, the first of `/run`, `/var/run` with a `user/<uid>` directory.
  - `gnupg_socketdir()` creates `gnupg/` and `d.*` mode 0700 when they are missing, so `gpgconf --list-dirs` creates
    them. gpg falls back to the homedir when `/run/user/<uid>` is missing or not the user's.
- GnuPG `common/zb32.c` and its test vectors `common/t-zb32.c`, and `tools/gpgconf.c` `--remove-socketdir`. That
  removes gpg's known socket files, then rmdirs the `d.*` directory.

| # | finding, restated | rev 3 |
|---|---|---|
| 1 | G21_11b passes with a plain LwlynSmith CCQE, or with a hybrid that has a novel default and a spent branch: the tune-wide ORs hide branch disagreement | **Fixed.** u0 is held to §4.1's description, as `DECLARED`: CCQE `genie::HybridXSecAlgorithm/SuSAv2-QEL` with default `SuSAv2QELPXSec`, and 2p2h `SuSAv2MECPXSec` alone, used by `AR23_20i_00_000` only. Novelty is now recorded per branch (`novelty.branches`), and within each slot every branch must agree on spent or novel. A disagreement is a STOP for the director, decided before the tune-level OR, which is then taken on the slot classes. Tests: `test_g21_with_a_plain_ccqe_is_not_section_41s`, `test_g21_hybrid_with_a_spent_branch_stops`, `test_branch_disagreement_is_a_director_stop`, `test_g21_needs_the_declared_hybrid_set_and_default`, `test_g21_needs_the_declared_2p2h_and_overlap`, `test_g21_2p2h_must_be_susav2mec_itself` |
| 2 | an unresolved reference (`genie::NoSuchClass/NoSuchSet`) counts as novel; the set name is discarded; `lexists()` lets a failed lookup fall through to the next directory | **Fixed.** Every reference used, including the hybrid default and each branch, resolves as GENIE's registry would (`resolve_ref`). It needs exactly one `master_config.xml` entry, found by the same search order with root `<genie_config>`, then its file on the search path with root `<alg_conf>`, then exactly one param_set of that name. Otherwise it is unresolved, never novel. Sets are recorded (`sources.*.alg`, `registry`, `hybrid.default`, `hybrid.branches`). `find_config` passes over a directory only when lstat reports it absent or its listing lacks the name; any other error is unresolved. Tests: `test_unregistered_class_or_set_is_unresolved_not_novel`, `test_unregistered_hybrid_leaf_is_unresolved`, `test_registry_rules`, `test_an_unreadable_directory_does_not_fall_through`, `test_an_unsearchable_directory_does_not_fall_through`, and the NoSuchClass case of `test_fallback_with_unresolved_02b_config_is_not_chosen` |
| 3 | a tune tag only in a comment, or a README qualifier matched as a substring, counts as present; a 02b entry under another qualifier counts as absent | **Fixed.** The spline is parsed structurally by expat in the same pass as its hash (no DOCTYPE or entity declarations). It needs root `<genie_xsec_spline_list>` and exactly one top-level `<genie_tune>`, which names the tune. The README needs exactly one line matching `version v<N_N_N> qualifier <Q>` as a whole, with Q equal to the qualifier. absent now also needs no other entry naming the tune: a listing name or UPS qualifier containing it, or a UPS entry setting `GENIE_XSEC_TUNE` to it. Such an entry makes the status unresolved. For 02b it does so even when the bound entry is present, so there is no fallback. Tests: `test_spline_header_rules` (8 cases), `test_spline_nested_tune_name_is_not_the_header`, `test_readme_qualifier_is_a_whole_field`, `test_02b_under_another_qualifier_is_not_absent`, `test_02b_with_a_second_entry_is_unresolved`, `test_other_tunes_entries_do_not_touch_02b` |
| 4 | product roots that resolve outside CVMFS move the read boundary | **Fixed.** Before any content read, `verify_roots` checks the repository path `/cvmfs/larsoft.opensciencegrid.org`. Its mount (`/proc/mounts`, the longest match) must be the repository's own or `/cvmfs`'s, and of a type that is not node-local. Each root's real path must lie beneath the repository path, on that same mount, and be a directory. Failure is a STOP with nothing read. Reads use only the verified real roots, and every open is relative to a descriptor of the verified root (`_open_beneath`). Tests: the `Roots` class, `test_reads_are_relative_to_the_verified_root` |
| 5 | exit 0 can carry no evidence (a bare `{"verdict":"GO"}` passed); the footer hashes by pathname | **Fixed.** `receipt_problems` requires schema `covfix-pg-probe/3`, a verdict matching the rc, a list of stops and an identity. A STOP needs at least one stop. A GO also needs no stops, a passed identity, verified roots, and every gpg check (`GPG_REQUIRED`, with types: 1 is not True). It needs all five tunes' catalog and classes, four passing controls, and u0 = G21_11b. u1 must be 02b or 02a, with the fallback flag consistent with 02b's status. Both chosen slots must be eligible, present with spline and README digests and a version, and resolved with sources. The output is opened `O_RDWR`, and the footer's sha256 is read back through that descriptor. Tests: `test_an_incomplete_go_is_invalid` (20 cases), `test_invalid_receipts_are_kept`, and `test_the_footer_hash_is_read_through_the_reserved_descriptor`, which moves the path while ssh runs |
| 6 | the `/run/user` socket exception accepts an unverified hash and filesystem, and confinement is checked after gpg ran | **Fixed.** `gpgconf --list-dirs` now runs first, and must exit 0. `check_sockets` accepts a socket dir inside the homedir. Otherwise it accepts only exactly `socketdir_for(home, uid)`, `/run/user/<uid>/gnupg/d.` + zbase32(SHA-1(home)[:15]), with these conditions:<br>- `/run/user/<uid>`, `gnupg/` and `d.*` are real directories (lstat) owned by the user, the last two with no group or other bits;<br>- `d.*` is its own real path, on tmpfs;<br>- every reported `*-socket` lies in that dir.<br>Anything else is a STOP before any other gpg call. After the agent is killed and gone, success or failure, a verified dir is removed with `gpgconf --remove-socketdir`. An lstat must then find that canonical path absent (`socketdir_absent`), and the homedir too. Nothing unverified is removed. Tests: `test_zbase32_vectors_from_gnupg` (GnuPG's vectors), `test_socketdir_for` (an independent transcription of zb32_encode), `test_check_sockets_rules`, `test_a_verified_run_user_socket_dir_is_used_and_removed`, `test_a_socket_dir_left_behind_fails`, `test_cleanup_runs_when_the_crypto_check_fails`, `test_an_unverified_socket_dir_stops_before_gpg_runs`, `test_a_failing_list_dirs_stops_before_gpg_runs`, `test_unconfined_sockets_fail` |
| non-blocking 1 | AGY-READ-2's fallback finding is closed; the docstring should say both configurations must resolve and match | done: step 5 of the docstring |
| non-blocking 2 | the spent-class control uses the full `NievesSimoVacasMECPXSec2016`; keep the full class and the negative test | kept. The negative case now registers the prefix as a class, so the control fails on the class name itself and not on resolution |

**Removed rather than fixed.** Rev 3 at first also checked that the repository path is its own real path. That check
can never fire alone: a root's real path contains no link, so it lies beneath a repository path that goes through a
link only if the check above has already failed. It was removed, and `test_the_repository_must_be_its_own_real_path`
still shows the STOP. A "CCQE branch in the spent pool" check for u0 was dropped for the same reason: branch
agreement plus novelty already exclude it.

**Changes from the mutant run.** The first full run killed 95 of 98 mutants. Each survivor was a check shadowed by
another one:
- The separate empty-spline branch was dead, because an empty file fails the root check. It was removed.
- The socket-dir real-path check could not fire alone, because `_inside` compared a resolved socket path with an
  unresolved dir. `_inside` now resolves both.
- The receipt-shape mutant survived because every bad-shape case also carried an incomplete record. Two cases now
  use a complete one.

The final run, on the committed files, killed 97 of 97 (`mutants.log`). One mutant was dropped with the dead branch.
