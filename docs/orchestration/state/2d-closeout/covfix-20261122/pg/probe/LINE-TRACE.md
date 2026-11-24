# PG probe rev 4: line trace

By the PG session. Rev 4 is the director's verify-only redesign, after codex-school2's read 3 (`CODEX2-READ-3.md`).
Its sources:
- `../PLAN-SLOT1-PROBE.md` (approved), and the director's rulings;
- COVFIX rev 12 §4.1 (the tunes) and §4.2 (the gpg flags).

The interpretation is in `../record/`; the probe compares the node with its pins, embedded as `PINS_JSON` by
`make_pins.py`. Earlier reads are in `CODEX2-READ-1.md`, `CODEX2-READ-2.md` and `AGY-READ-1.md` to `-3.md`. The tests
are in `test_pg_probe.py` (results in `tests-local.log`), and the mutants in `mutants.py` (results in `mutants.log`).

| requirement (source) | code | tests |
|---|---|---|
| run on a login node only; read nothing otherwise | `identity`, first in `probe` | `Probe.test_identity_failure_reads_nothing`, `Constants.test_identity_rules` |
| the repository's mount is CVMFS's, and `user.fqrn` is `larsoft.opensciencegrid.org`; revision and root_hash recorded; unreadable xattrs STOP (director, gap 3) | `verify_repo` | `Repo.*`, `Probe.test_each_failure_stops` |
| pins only, from the offline record; no XML, no registry, no search path on the node (director's redesign) | `PINS_JSON`, `make_pins.pins` | `Constants.test_pins_are_the_records` |
| every pinned file opened relative to a verified root descriptor, each component `O_NOFOLLOW`, hashed through its descriptor; links by `readlink`; listings by name (director's redesign; codex 3.4) | `_walk`, `_open_final`, `sha_rel`, `link_rel`, `list_rel`, `verify_genie` | `Genie.*` |
| the override directories' listings pinned: no earlier copy of a pinned file (director, gap 1) | `genie_listings` in the pins, `verify_genie` | `Genie.test_every_difference_stops_and_records_the_node_value` (an extra file, an absent directory present) |
| a byte mismatch STOPs, and the node's sha is recorded for every pinned path, hash only (director, gap 4) | `verify_genie`, `verify_xsec` | `Genie.test_every_difference_stops_and_records_the_node_value` |
| the live qualifier listing, exact names, with the three used qualifiers required; their splines and READMEs pinned | `verify_xsec` | `Xsec.*` |
| each used `data/` listing recorded by names; a config-like name STOPs (`GXMLPATH` searches `data/` first) | `verify_xsec` | `Xsec.test_refusals` |
| CVMFS's `.upsfiles/dbconfig` hashed and recorded, for B2 (director, answer 3) | `verify_xsec` | `Xsec.test_matching`, `Xsec.test_refusals` |
| instantiability: the class libraries pinned (director, gap 5) | the `lib/` entries of `genie_files` and `genie_links` | `Constants.test_pins_are_the_records` |
| R1: each tool opened once, at fd 10 or above, hashed through the descriptor and run as that descriptor; RPM's recorded digest must equal it, otherwise first-use is recorded | `open_tools`, `exe`, `_run` | `Tools.*` |
| strace's self-test through its descriptor, with a complete trace (director's ruling, answer 2) | `strace_self_test`, `trace_complete` | `SelfTest.test_modes` |
| gpg (§4.2): sockets verified before use; nothing after a failed preflight; the agent identified even after a crypto failure; outside sockets removed only once the agent is gone; lstat absence at the end (codex 3.6) | `check_sockets`, `gpg_check` | `Gpg.*`, `RealGpg` |
| the launcher: the bytes it hashed, sent once; the output reserved; a GO receipt complete against the pins in the bytes sent; the footer hashed through the descriptor (codex 3.5) | `pg-probe-launch.py`: `main`, `pins_of`, `receipt_problems`, `validate` | `Launcher.*` |

## Limits of these tests

- **Stub trees.** The CVMFS tree is a stub. The real check is the node's bytes against pins taken from SciSoft's
  build, which matches the GitHub tag file for file. A real difference is a STOP that records the node's hashes.
- **Linux-only facts.** Descriptor execution, `/proc/mounts`, `/run/user` and CVMFS xattrs are Linux facts. Their
  rules are tested with injected stand-ins; the node exercises the real things.
- **The seal frame.** The probe tests the fd-3 passphrase handoff only. The bound PG binary's stdin frame is
  cov2d's.
