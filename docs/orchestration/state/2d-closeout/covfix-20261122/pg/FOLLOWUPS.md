# COVFIX PG follow-ups (not blocking)

The current list. Each item was ruled non-blocking under the director's rule: blocking means a false STOP of a
correct run, or a gate that can miss something correct producers really emit. The source of each item is named.

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
