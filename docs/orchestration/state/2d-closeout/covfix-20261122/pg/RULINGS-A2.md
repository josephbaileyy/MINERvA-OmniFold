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

## Round 3 (2026-11-25): the director's rulings on agy's and codex-school's reads of 5f141f7a

Restated, as above. The director's messages govern.

**The seed in the traces (codex 11).** gevgen names its outputs by the run number, which is the seed, so the traces
are not seed-free even though they are path-only.
- Raw traces, task logs and their hashes are seed-bearing. They stay in W and never leave it.
- The published sums omit them (`pg_lib.SEED_BEARING`, `out/PG-PUBLISH-SHA256SUMS`).
- A leak scan, run where the seed is known, checks every outgoing file's path and bytes for each seed: decimal (any
  zero-padding contains it) and hex in both cases. Any hit is a STOP.
- How this fits the seal is cov2d's to review.
- No redaction at write time: it would change what the trace proves. F1's argv stays.

**D1, binding the programs.** The path-only rule (PLAN-SLOT1-PROBE.md:16, and the Q-C bullet above) was the director's,
and is lifted. Since the traces are seed-bearing and stay in W, the argv in them no longer leaks.
- `execve` is traced, and gntpc runs under the trace prefix.
- Every successful exec must be a genie-manifest file with the manifest's bytes and real path, or a pinned system tool
  (`pg_pins.json` `system_tools`, from the probe's awk).
- run_gevgen_v3.sh's new sha goes to the director before anything runs it.

**D2, threat model and links.** The threat model is environmental or accidental change, not a hostile process under
the lane's own uid.
- CVMFS is read-only. Its `user.revision` and `user.root_hash` are recorded at the start and end of every run and must
  be equal, and its content is pinned by sha.
- The private product is read-only and checked at the start.
- The defining-link rule is now `realpath(p) == p`. The kernel follows links without a readlink call.

**D3′, spline use, not just spline opens.** F1's laconic messenger sets GEVGDriver to WARN, so GENIE never logs its
spline lookups (GEVGDriver.cxx:646-657 at R-3_04_00).
- (i) The reduce must keep, for every (probe, target) pair in F1's argv (gevgen_cmd's `-p` and `-t`), exactly the
  source's splines, knot counts included.
- (ii) Each slot gets a one-event coverage run before any sealed seed is used:
  - the public seed 123456789;
  - Messenger_laconic.xml with only GEVGDriver raised to DEBUG, pinned by sha;
  - an argv equal to the sealed run's except the event count, the seed and the messenger, checked by `argv-check`.
  Its log must answer every "Need xsec spline for X" with "Spline was found", with no spline built. Its outputs are
  deleted after the log check, and the log's hash is kept.
- O_PATH opens are not reads.
- Any read under a genie_xsec data directory other than the pinned spline is a STOP.

**D4, search order.** A GENIE config basename must be read at the first existing path of the tune's search order.
- The order is the run's GXMLPATH, captured from its own setup and equal to the tune's genie_xsec data directory,
  then the record's search_dirs.
- What exists comes from the manifest.
- ROOT's .rootmap and .pcm files are exempt from the order, but stay bound by location and hash.

**D5, B3's event files.** A trap deletes the event and status files on every exit, STOP included, after the writers
end. Hashing them for deleted.json is allowed.

**D6, cleanup.** After the process trees are killed, a scan finds any live process whose cwd lies under W. A survivor
30 s past SIGKILL is a STOP with no publication, and seedfree still runs.

**D7, `..` paths.** A `..` path is resolved on the node, after the run, while W is unchanged.
- The resolved path must lie under an allowed root, and is then gated.
- Both the raw and the resolved path are recorded.
- A path that fails to resolve is a STOP.

**D8.** The deploy check counts ignored files too.

**The node checks this laptop cannot run** are recorded in B3 as named checks, PASS before slot 2 (`host-check`):
- a final directory on another mount, as a positive control;
- no mount point inside a walked root;
- the real strace format of a path holding `) = -1`.
