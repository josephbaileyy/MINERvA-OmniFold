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
separately, and count against the receipt. *Superseded 2026-11-25 by the director's ruling, which mutrun.RULE prints at
the head of every receipt:* an import or collection error (`_FailedTest`, ImportError, ModuleNotFoundError,
SyntaxError) is INVALID; otherwise a FAIL or an ERROR with a non-zero exit kills; a timeout, or a FAIL with exit 0, is
INVALID.

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

## Round 4: the director's rulings on the codex-school and Sonnet 5.5 reads of 12604016 (2026-11-25)

<!-- absence-ok: "never", "untestable" and "no allocation" here state rules, this host's test coverage and a login node's setup, not a claim that a result does not exist -->

The reads and their dispositions are in `delta-read-r4/`. The director gave a GO on the whole fix list, failing tests
first, and ruled six items. cov2d gave its no-objection to the C3 and C4 design, and on 2026-11-25 to both as built
at cd21bafb, including the C3 node record's move from B1 to the compute node. It set one condition and two wiring notes:
- **Condition, for the director's confirm of `record/root-schemas.json` after B3.** Counting int32 only is safe only if
  GENIE stores no seed as a 4-byte int in a published file. The confirm checks (i) that B3's decoded scan gives, for
  every allowlisted file type, an int32 count consistent with its chance expectation (a per-event seed would give
  about the entry count, not about 0), and (ii) that B3's gst schema has no branch or object carrying the run number.
  If either fails, int32 becomes a STOP for that file type before PG.
- **Wiring, publish_guard (JE's call site; cov2d copies JE).** `export_allowlist()` leaves out `out/leak_scan.json`,
  which PG-PUBLISH-SHA256SUMS lists, so the guard's allowlist is `export_allowlist() + ["out/leak_scan.json"]`.
- **Wiring, the gen-spec's env_keep.** It must name SLURM_JOB_ID and SLURM_CPUS_ON_NODE, or `node_check.json` records
  `slurm_job` and `all_cpus_allocated` false on every run. That is a wrong record, not a failure; cov2d's cgroup steps
  gate the job either way.

**C2, ROOT's RECREATE.** ROOT's RECREATE unlinks the file, then opens it `O_RDWR|O_CREAT`. Such an open counts as an
output only at the role's exact expected output path, and only after the same process probed that path for ENOENT or
unlinked it: gevgen's `gntp.<run>.ghep.root` and `input-flux.root`, gntpc's `genie_v3.gst.root`, the graphs' `--output`.
Every other `O_CREAT` open without TRUNC or EXCL stays a read. `unlink` and `unlinkat` are traced for it.

**C3, the seed in live argv.** Option (a). The threat model is D2's: other users are excluded by the exclusive
allocation, and same-account processes are out of scope. F1's argv stays byte-identical.
- B1's probe records `/proc`'s mount options and hidepid. B1 runs on a login node, which has no allocation.
- pg_generate's `node-record` records, on the compute node, `/proc`'s options, whether it runs in a Slurm job, the
  job's CPUs against the node's, and other users' visible processes. It is a record, never a gate.
- The director's check: no seed may reach anything Slurm records and keeps (the sbatch line, --comment, the job name,
  the stored batch script, the exported environment). pg_generate takes only `--workdir W --seeds W/seeds.json`,
  reads seeds only from that file, calls no srun, sbatch or scontrol, and exports only G, O, NEV and TO
  (`test_end_to_end` and the stubs). cov2d confirmed the same for its wrapper and binary.

**C4, the publication.** The ruling as cov2d and the director amended it:
- an explicit export allowlist: the inventory less the seed-bearing; any other file outside W/tmp is a STOP;
- STOPs on every seed's decimal, hex (both cases) and int64 (both byte orders), over raw bytes and over every ROOT
  object inflated (ZLIB, LZMA, ZSTD and LZ4 when their modules exist; any other codec, or a missing module, STOPs);
- int32 forms are counted only, against their chance expectation (28 B / 2³²), because a big-endian seed near 1e9
  reads as a float32 in the dense kinematic range;
- each published gst's schema (its keys' class, name and title, and its streamer info's sha) equals B3's gst, which
  `record/root-schemas.json` holds once B3 has run; pg_generate refuses at its start while it is unset;
- out/leak_scan.json and out/PG-PUBLISH-SHA256SUMS are scanned after they are written. The sums file is public and
  lists only allowlisted, published files (cov2d's publish_guard is amended to pass exactly those hashes).
  *Later (the director's ruling 4, 2026-11-25): at PG nothing leaves W but ciphertext. The seal takes all of W,
  `out/` included, so these two files are sealed too, and the publish set leaves only at PV's decrypt step.*
- B3's public-seed files are decoded the same way, as the positive control.

**The trace set** adds execveat, rename, renameat, renameat2, link, linkat, symlink, symlinkat, unlink and unlinkat.
run_gevgen_v3.sh, pg_verify.py and pg-probe.py carry it, and their new shas go to the director before anything runs.

**S7, D2's revision.** A revision or root-hash change between the run's start and end passes only if every CVMFS file
the run read (each trace check's gated files, ROOT configs, libraries and programs) re-hashes to its pin at the end.
Both revisions are recorded; any mismatch is a STOP.

**C13, process isolation.** The generation runs in its own session and process group (setsid). The survivor scan finds
processes by that group as well as by cwd, and excludes this shell's ancestor chain (S6). The drain before
publication KILLs any survivor and polls 30 s; a survivor then is a STOP, and a STOP withdraws the publication set.

**Untestable on this host, recorded on the node:** the job reaped only once dead (a process in uninterruptible sleep),
and the 30 s poll after KILL (a SIGKILL that does not take effect at once). Both need the kernel to delay a kill. The
director accepted them as disclosed (2026-11-25). Each logs a count-only line when it fires, and
`REHEARSAL-CHECKLIST.md` records what the first real run's log shows.
S9: `--rc 0` is the status of a step that has already passed (`need`), so trace-check's rc rule is documentation.


## Round 5: the director's rulings on the codex-school and Sonnet 5.5 reads of 7415d0c4 (2026-11-25)

<!-- absence-ok: "never", "no core" and "not killed" here state rules, not a claim that a result does not exist -->

The reads and their dispositions are in `delta-read-r5/`. The director gave a GO on all 16 blocking fixes, failing
tests first, with fixtures from the real format for every gate that compares GENIE or cluster output. A deterministic
false STOP of a correct run counts as blocking. The three rejections are accepted as reasoned.

**Q1, the CVMFS revision.** Option (c). Every pinned CVMFS file (the genie manifest's files and links, and each CVMFS
tune's spline and README) is hashed at the run's start, before anything is traced, and again at its end. Both must
equal the pins, any difference is a STOP, and both hash sets are recorded (`pin_hash_start.json`,
`pin_hash_end.json`). S7's re-hash of the files the run read stays. A gated link is re-hashed by its real path.

**Q2, crash collection.** `ulimit -c 0` is set in the job before GENIE starts (pg_generate and B3), so a crash writes
no core under W or anywhere. B1 and `node-record` record core_pattern and the core limit. Site collectors are outside
C3's scope beyond that record: if core_pattern pipes to one, it is recorded and the run continues.

**Q3, the trace set.** It adds mkdir, mkdirat, mknod, mknodat and truncate. A successful one outside W is a write
outside W. No role makes a link, so any successful link or symlink is a STOP. run_gevgen_v3.sh's new sha goes to the
director before it runs.

**D6 revised (B9).** The generation's session (setsid), not its process group, is scanned: GNU timeout gives each
task a process group of its own. Every survivor in the session is KILLed at each poll until none is left or 30 s
(monotonic) have passed. A process outside the session with a cwd under W, other than this shell's parent chain, is
a STOP and is not killed. A process list that cannot be read is a STOP.

**C4 revised (B5-B7).**
- A ROOT file's keys and free gaps must tile fBEGIN to fEND exactly, with nothing after it.
- A free gap's old blocks are inflated and scanned, and each block must be exactly one complete stream.
- int32 forms are a STOP in every ROOT object but a TBasket's payload.
- gzip and zip members are inflated, and any other compressed container is a STOP.
- A file's path and bytes are scanned apart.
- hadd's `*_ALL.gst.root` has its own schema, `gst_merged`, recorded by B3 from its own hadd.

**The gen-spec (cov2d, the director, 2026-11-25).** Six keys. pg_generate's environment is exactly env_keep's
inherited names, env_set's pinned literals, and TMPDIR=W/tmp. publish_guard's call site is cov2d's binary. The split
proposed for the gen-spec is in README-pg.md.

## Round 6: the director's GO on round 5's confirm read of 63466b61..dc341d3f (2026-11-25)

**Scope.** A finding is blocking if it makes a correct run STOP, or if a gate can miss something correct producers
really emit. Built: K1–K4, K6–K9, K11, K12, and the hardenings F4, F12, F13, F17 and F18. K5 and K10 are deferred
to FOLLOWUPS.md. The rejections of F15's thread-exec marker and of F2/B2's staged messenger stand.

**The XML search (K1, K9).**
- An explicit-path read may follow a complete basename walk that ended at that path. This is Messenger's own
  sequence (Messenger.cxx:103, :132): `GetXMLFilePath("Messenger.xml")`, then `GetXMLFilePath` of the path it found.
- Once a process has walked the tuned list, every later walk in it, basename or explicit, must use the tuned list.
  GENIE's callers all use the default `add_tune`, and the tune stays configured.

**Traces (K11, K12, F4).**
- A complete syscall on a process whose last call is still unfinished is a `resume-mismatch`.
- A write counts as inside W only if it is lexically inside W and also inside W with links resolved. An open or a
  truncate resolves its last component; a mkdir, mknod, unlink or rename resolves only the directories leading to it.
- gntpc's GHEP is the one gevgen's initial process created.

**Drain and quiesce (K7, K8).**
- Quiet means two scans in a row, 0.5 s apart, find no process in the session, within the 30 s.
- A process whose state cannot be read counts unless getsid says it has gone.
- The node runner KILLs the driver's session the same way. Any straggler, or a session that is not quiet by the
  deadline, is a STOP before the event files are swept.

**ROOT (K3, K4).**
- A live key's blocks must use all of its data bytes.
- Each whole freed record still in a free gap (its key header intact after the overwritten length) is read as
  strictly as a live key, keeping its class.
- In gap bytes that are no whole record, a well-formed block header whose codec module is missing is a STOP.
- Schemas are taken from live keys only.

**B3 (K2, K6, F13).**
- t0 has no GHEP after the wrapper. The driver checks this, and both validators expect t0's three names.
- Each coverage GHEP (the public seed is its run number) is decoded even after a raw hit. Both validators require
  that its seed was found in decoded bytes (`inflated`, or `int32-object`, which is how an int64 run number shows)
  and that `bytes_inflated > 0`.
- A prior deletion record of the wrong shape is noted as `_prior: unreadable`. Each save is written to a temporary
  file, then renamed over the record.

**Q2, restated (F18).** `ulimit -c 0` suppresses ordinary core files only. A piped core handler ignores the limit.
That route is recorded in B1 and node-record and is out of scope beyond the record. Round 5's wording above ("no
core under W or anywhere") overstated this.

## Round 7: round 6's confirm read (the director's ruling, 2026-11-26)

The confirm read (codex-school, gpt-6.2-sol) is in `delta-read-r6/confirm/`. The director ruled R1–R4 blocking:
each is a false STOP of a correct run. Codex 4 and 6–11 are not blocking and go to `FOLLOWUPS.md`, except codex 10,
which is built with R1. After this round there are no more codex rounds on this package.

**R1, B3's control.**
- With `decode_all`, every key is read; nothing breaks at the first hit.
- `seed_objects` names each ROOT object the seed was found in: its class, whether it was inflated, and the kind.
  The scan records it in both modes, and both validators check its shape.
- The control needs at least one seed object, as well as `holds_seed`, `bytes_inflated > 0`, and an `inflated` or
  `int32-object` hit.
- There is no object-local witness rule: B3's record shows whether GENIE's header was stored or compressed, and the
  director decides then.
- In production, the first hit is still the STOP.

**R2, the session scans.** `/proc/PID/stat` is read as bytes. The state is the first field after the last `)`, so
a command name holding any bytes, `)` included, does not break the scan. This covers pg_verify's `survivor_scan`
and the node runner's `session_pids`.

**R3, ROOT's freed baskets.** A freed record of class `TBasket` may have an `fKeylen` longer than its strings. The
basket's own fields follow them, and its payload starts at the record's start plus `fKeylen`, as in a live key.

**R4, block headers in a gap.** In gap bytes that are no whole record, a candidate counts as a header only if its
method byte is ROOT's: ZL 8, XZ 0, ZS 1 (RZip.cxx:251–274). ROOT checks none for L4, so a missing LZ4 module
remains a STOP there.

**Codex 10.** The driver checks first that t0's directory can be listed; a listing error is a STOP. It then tests
for a GHEP with `compgen -G`, which succeeds only on a match.

**Logs.** From this round on, every suite run writes its full output to its log, not only the summary line. If the
unexplained "8 failed, 325 passed" run recurs, that is a STOP to the director.


## Round 8: the compat-lib shim (B3 run 2's exe-check STOP; the director's rulings, 2026-11-26)

**The STOP.** B3's second run (receipt install/pg-replay-g2111a.py.out, e8a58f9d…) STOPped at exe-check, before any
GENIE program. Its one problem: `ld-library-path: /global/homes/j/josephrb/.genie_compatlibs -> … is outside CVMFS and
the system library directories` (install/b3-diag/b3-diag.out). setup_genie_v3.sh puts F1's compat-lib shim first on
LD_LIBRARY_PATH, and no test modelled it.

**The evidence** (read-only, install/b3-diag/, each script's sha to the director before it ran):
- b3-libs.out: GENIE's NEEDED closure (125 ELF files, none unresolved) loads three of the shim's seven names:
  libssl.so.10 and libcrypto.so.10 (ROOT's libNet.so), whose targets are on minerva CVMFS's sl6_fnal_python3, and
  libxxhash.so.0 (ROOT's libCore.so), whose target is the conda env's. SLES 15-SP6 provides libssl and libcrypto only as
  .so.1.0.0, .so.1.1 and .so.3, and no libxxhash, so (c), the system libraries, fails.
- b3-xxhash.out: no larsoft product and no minerva container holds a libxxhash.so*. The conda file's SONAME is
  libxxhash.so.0, and it defines libCore's three undefined XXH symbols.

**Rulings.**
- libssl.so.10 and libcrypto.so.10: pinned at their minerva real paths and shas, with minerva revision-tracked as
  larsoft is (revision and root hash at start and end, the libraries re-hashed on a change). The two libpcre names are
  neither pinned nor allowed.
- libxxhash.so.0: (i), pinned at the conda env's real file and sha, hashed at the start and the end, allowed only at
  that real path. It is the only provider, and it gives F1 parity with no new install step. The home-filesystem risk
  is stated in REHEARSAL-CHECKLIST.md and README-pg.md.

**As built.**
- pg_pins.json gains `compat_libs` (the shim's real directory, each pinned name's real target and sha) and
  `minerva_repo` (the repository, with revision 2719 and root hash aa0fa0c9… as the observed baseline). Both drivers
  refuse without `compat_libs`.
- exe-check (`--compat-pins`): an LD_LIBRARY_PATH entry outside the roots passes only if it is the pinned shim
  directory and each pinned name in it resolves to its pinned target with matching bytes (`compat-target`,
  `compat-sha`).
- trace-check (`--compat-pins`): a library outside the roots passes only at a pinned real path whose bytes match
  (`so-pin-mismatch`); a gated read of the shim is pinned by real path (`library pin`).
- pin-hash: both drivers add the three pinned libraries, at the start and the end.
- revision and revision-compare take several `--repo`: larsoft's values stay the record's own, and minerva's sit under
  `repos`, compared with the same re-hash rule (`revision-repo-missing` if a repository is not in both records).
- Tests: the four planted cases (an unpinned shim entry, a pinned name pointing elsewhere, a pinned target with other
  bytes, a minerva revision change) and the director's fifth (the conda file changed between start and end), plus the
  shim outside a gated name, the CLI wiring, the refusals, and the pins held to the b3-diag evidence. 27 mutants.
