# COVFIX PG follow-ups (not blocking)

The current list. Each item was ruled non-blocking under the director's rule: blocking means a false STOP of a
correct run, or a gate that can miss something correct producers really emit. The source of each item is named.

## From round 6's confirm read (delta-read-r6/confirm/DISPOSITIONS.md; the director, 2026-11-26)

- **Codex 4: the 4 bytes after a whole freed record.** If no freed record follows, the header search starts 4 bytes
  late. In ROOT's layout every record or gap in a free gap starts with its own 4-byte length, so no block header can
  begin there. Deferred: search from the record's end when the next one does not parse.
- **Codex 6: the order of K1's walks.** Explicit and basename probes are split without regard to trace order, and
  the explicit walk's phase is applied first. GENIE's real order passes. Deferred: consume the walks in trace order
  and apply the pid's phase at each completed walk.
- **Codex 7: a tuned walk with no read.** It never binds the pid, so a later untuned read can pass. Only a wrong
  producer emits this. Deferred: let walks that end without a read bind the phase.
- **Codex 8: the drain's deadline.** Quiet can be accepted up to one poll past 30 s (two empty scans are still
  required). A process that forks and exits between enumeration and inspection on two polls in a row escapes any
  snapshot scan; that is C10's containment. After a quiesce STOP the runner still sweeps W1's public-seed files.
  Deferred: check the deadline before accepting quiet.
- **Codex 9: a write through a pre-existing link in W, unlinked before verification.** Links made during the run
  are STOPs (B10). This is C10's enforcement at execution, with a checklist row that W's staged inputs hold no
  links.
- **Codex 11: nested bash subscripts** (`TUNE[1+arr[0]]=x`) escape F12's pattern. The wrapper's bytes are fixed by
  its sha (5c3fd520…). Deferred: parse assignments, or refuse forms the pattern does not cover.

## From round 5's confirm read (delta-read-r5/confirm/DISPOSITIONS.md; the director, 2026-11-25)

- **K5 (F7): a duplicated zip member name.** `_members` reads each name in `namelist()`, so a name stored twice is
  read twice as its last member. numpy and gzip never write such files, and every published file is ours. Deferred:
  iterate `infolist()` and STOP on a duplicate name. Also deferred: requiring gzip magic for `.gz` and zip magic for
  `.npz`.
- **K10 (F11): an XML comment inside a spline's knot.** ElementTree joins `1<!-- c -->2` into one value, while
  GENIE's libxml2 reader sees two text nodes. The source splines are pinned CVMFS files, hashed at both ends (Q1(c)),
  so a comment there is already a hash STOP. Deferred: keep comments in the parse and STOP on one inside a spline.
- **F9 (B8): record each gated link's resolved target with the trace receipt** and compare it at the revision
  check. Today `pin_hash` checks every manifest link's target at both ends, and that covers it.

## From round 5's delta reads (delta-read-r5/DISPOSITIONS.md)

- C2: bind the traced launch's own environment, not the setup's GXMLPATH. pg_generate refuses GXMLPATHS and
  GALGCONF, and every launch inherits its shell.
- C11:
  - Bind each role to its exec epoch.
  - Allow dirfd-relative lookups and track cwd per process. Today these STOP, which fails closed.
  - Replace `ROOT_GENIE_LIB` with a list (S9: it matches libEGL and misses libGenVector). The proposal is to
    allowlist the system-directory libraries B3 observes, confirmed with root-schemas.json.
- C6: compare parsed TTree branch and leaf declarations.
- C10: enforce writes at execution (Landlock or a mount namespace). strace only verifies.
- C12: interaction strings in the coverage log carry no tune identity. The coverage run's argv and its spline read
  bind the tune.
- S9, S11 (a symlinked directory in W refused at publish), S12 (cosmetic).
