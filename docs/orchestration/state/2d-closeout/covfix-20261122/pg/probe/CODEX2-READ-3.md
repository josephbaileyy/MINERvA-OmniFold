# PG probe: codex-school2 read 3 (NO-GO) and rev 4

cov2d ran codex-school2's confirm of rev 3 (`954bf0c6`). The report is
`~/cov2d-work/reads-for-director/codex2-tgprobe-954bf0c6-r3-REPORT.md`, sha256
`e61f85d6d5b91aacd4bf1b4be6d8b1dcc3082dc3d3ebe3181fafa5d3b1628616`. It found a remaining variant of each of round 2's six
cases and two regressions, and it judged the 97/97 mutant receipt unsound. The items are restated here by the PG
session, not quoted.

The director answered by closing the class rather than patching it: verify, don't interpret. Rev 4 is that
redesign.
- Novelty and every reading of GENIE's configuration moved offline, into `../record/` (`PG-RECORD.json`, built by
  `build_record.py` from SciSoft's build and cross-checked against the GitHub tag).
- On the node, the probe only checks that bytes, links and listings equal the record's pins. It has no XML parser,
  no registry emulation and no search path.
- Most of the items below therefore no longer have code to apply to.

| # | finding, restated | rev 4 |
|---|---|---|
| 1 | a nested hybrid could hide a spent CCQE branch | **Closed by the redesign.** The node interprets nothing. Offline, `build_record.py` refuses a nested hybrid outright, and the record lists every leaf of every hybrid. |
| 2 | a registered but non-instantiable class could give GO | **Closed, now checked.** The record lists each class's `.rootmap` entry and its defined default-constructor symbols in the build's libraries. The probe pins those libraries' bytes (`.so` target, `.rootmap`, `_rdict.pcm`) and the `.so` links. |
| 3 | a nested `<genie_tune>` inside 02b's element was accepted | **Closed by the redesign.** The probe parses no spline. Slot 1's spline is pinned by sha from SciSoft's tarball; slot 2's and the spent tunes' are pinned by sha on CVMFS. |
| 4 | any export mounted at the CVMFS path passed, and opens could cross mounts | **Fixed** as the director ruled. `user.fqrn` must be `larsoft.opensciencegrid.org`, with `user.revision` and `user.root_hash` recorded, and unreadable xattrs are a STOP. Every pinned read walks from a descriptor of the genie root, one component at a time with `O_NOFOLLOW`. |
| 5 | `validate()` accepted a GO lacking spent evidence, sources and the fallback result | **Rebuilt for schema 4.** The launcher parses the pins from the probe bytes it sends. A GO needs their sha, every pinned file, link, listing and genie_xsec file present and matching, the fqrn, the three qualifiers, data/ listings with nothing config-like, dbconfig's hash, every tool hashed with no RPM mismatch, the strace self-test, and every gpg field. There is no fallback any more. |
| 6 | `socketdir=$home/sub` with `agent-socket=$home/S.gpg-agent` was accepted; a failed preflight still reached `--kill`; the agent went unidentified after a crypto failure; an outside dir could be removed before the agent was gone | **Fixed.** Every non-empty reported socket must lie directly in the reported socket dir. After a failed preflight nothing else runs, not even `--kill`. Once gpg has run, the agent is identified even if crypto failed. A verified outside dir is removed only after the agent is gone. |
| non-blocking | the mutant receipt counted an import error and any non-zero exit as kills | **Fixed** (`../mutrun.py`). Every suite must pass clean first, and every mutant must compile. A kill needs at least one unittest FAIL, an assertion failure, and the log names the failing tests. ERRORs alone, timeouts and other exits are INVALID, listed, and count against the receipt. |

**Found while rebuilding.**
- **fd 3.** `open_tools` took the lowest free descriptors, so the first tool landed on fd 3, gpg's `--passphrase-fd`,
  and the probe would have refused its own gpg check on the node. The tools now sit at fd 10 or above, and a test
  and a mutant cover it.
- **R1.** strace, gpg, gpgconf and gpg-connect-agent are each opened once, hashed through the descriptor and run as
  that descriptor (`/proc/self/fd/<n>`). Each is checked against RPM's recorded digest where RPM has one; a tool with
  no RPM record is recorded as first-use.
- **What the laptop can't test.** macOS can't execute a descriptor, so the tests map each descriptor back to its
  path. The kernel's descriptor execution is exercised on the node by the probe's own strace self-test and every
  gpg call.
