# The director's rulings on slot 1, the probe and the trace (2026-11-24), restated

The PG session's restatement, for reviewers who have not seen the director's messages. It is a summary, not the
director's wording, and the director's messages govern. The plan they amend is `PLAN-SLOT1-PROBE.md` (approved at
`85283a33`).

**Slot 1 and slot 2.**
- Joseph chose route A, as relayed by the director. Slot 1 is G21_11a_00_000, from a sha-pinned private copy of
  SciSoft's G2111a00000 product. Slot 2 is G18_02a_00_000, from CVMFS.
- Neither the declared G21_11b nor the declared 02b, nor 02a_02_11b, is on CVMFS: PR #1281's listing, CVMFS revision
  1249.
- Generating splines with gmkspl is out.
- The changes are SLOT1-PRIVATE-PRODUCT.md's items 1–8, plus the trace prefix below.

**The three conditions for slot 1.** If any can't be shown, slot 1 is dropped, with no workaround.
1. Every extracted file is checked by sha256 against a pinned member listing. The listing refuses absolute names,
   `..` and links leaving the tree, and records every link's target.
2. The GENIE configuration actually loaded is shown from the run, as an open-trace, with every file pinned by sha256.
3. The spline the generator actually opens is shown from the run, by sha256.

**The trace (answers Q-A, Q-B, Q-C and the tightenings).**
- **The traced calls.** The open, access, stat, readlink and chdir families only. These are path-only, so no argv and
  no seed is traced.
- **Gated files.** Every `.xml` and `.xml.gz`, every path containing genie or GENIE, and the genie libraries'
  `.rootmap` and `.pcm` files are checked against the manifests at their own path.
- **ROOT's own files** are recorded with their sha256 and gated on location only: they must be under CVMFS. ROOT is
  pinned by CVMFS revision and a recorded sha, not by an offline download.
- **Location.** Any config-type file opened from outside CVMFS, the private product or W fails. That covers `.rootrc`,
  `rootlogon*`, `.rootmap`, `.pcm`, `.xml` and non-system `etc/` files.
- **Completeness.** The trace fails if it is empty, if strace exits non-zero, if a process was killed, if the last
  line is truncated, or if the generator's own spline open is missing.
- **The search order.** Every probe of a config basename is listed. A probe that found the file somewhere other than
  where it was opened fails. Every defining file must be opened at the record's expected path, and none may be read
  through a link (readlink).
- **The prefix in F1's run_gevgen_v3.sh** is pre-approved in principle. It is never inherited, and is built only from
  a pinned strace descriptor and a trace directory under W. It is empty with neither, so F1's argv stays
  byte-identical. Tests and mutants cover each rule, and rev 12 §4.2 lists it (cov2d, 6cc2fad6).
- **The compute-node trace is required.** The binary checks strace (its pinned sha through the descriptor, and the
  self-test) as its first compute step, before any seal is consumed. A missing strace there sends slot 1 back to the
  director; there is no fallback to B3.

**B3, the login-node replay** (rev 12 §4.1, 783188cd).
- It runs reduce, spline-check and gspl2root, then one gevgen under the same strace: seed 123456789, passed to both
  `--seed` and `-r`, public and below the sealed range; 100 events; G21_11a_00_000; F1's flux, target and energy
  range unchanged.
- The event and status files are deleted unread. Only trace-check's booleans and the opened files' shas are kept.

**R1 and the tools.**
- gpg, gpgconf and strace are pinned and checked through the descriptor.
- The probe records each one's hash through the fd, its `rpm -qf` package and RPM's recorded digest. The pin must
  equal RPM's digest; without an RPM record it is first-use, and that is disclosed.
- The director pins them in a confirm, and the pins live in the probe's receipt once it is merged.

**The probe (verify, don't interpret).**
- Offline pins only, with no XML, registry or search path on the node.
- The live qualifier listing, exact names.
- `user.fqrn` == `larsoft.opensciencegrid.org`, required; unavailable xattrs are a STOP.
- Any byte mismatch STOPs and records the node's hashes.
- The override directories' listings are pinned, `genie.table` by sha, and the libraries for instantiability.
- Each used tune's `data/` listing is recorded by names, because every genie_xsec table prepends its `data/` to
  `GXMLPATH`; F1's own runs inherit the same prepend.

**dbconfig and the purge.**
- B2 copies CVMFS's `.upsfiles/dbconfig` byte for byte, checked against the probe's recorded sha, and makes it
  read-only. Nothing else is authored in the product directory.
- The roughly 8-week pscratch purge is treated as unverified. B2 runs shortly before generation, the binary
  re-verifies every member and STOPs on any missing or changed one, and the records note the install date.

**Mutants.** Only a test-assertion failure kills. Import errors, collection errors and timeouts are INVALID, listed
separately, and count against the receipt.

**Process.**
- The scripts for B1, B2 and B3 each come to the director with their sha before they run, and nothing runs on NERSC
  before then.
- A changed byte in anything already approved comes back to the director first.
- The blinding is unchanged.
