# e1 cleanup: removing the three unused e1 scratch roots (2026-11-27)

**By** limitation-resolver. The director assigned this on 2026-11-27, after e1's d2 ended at the C-E3 STOP. It falls
under Joseph's 2026-11-27 rule "remove things that are unused". It proceeds only through a listing-sha handshake with
the director, and the removal runs only after the C-E3 diagnostic's receipts merge.

## What goes, and what stays

| root (literal path) | holds | why it is unused now |
|---|---|---|
| `/pscratch/sd/j/josephrb/rpd-reco-p0e1-20261126/` | P0's clone and tools; `dry/staged` and `run/staged` (14.75 GB of omnifile copies, plus dump and product copies); the step records | e1's d2 ended; P0's records are committed (`../p0e1-20261126/run-20261127/`) |
| `/pscratch/sd/j/josephrb/rpd-reco-flux4-20261126/` | flux4's clone; the staged originals, including the 2.36 GB sidecar copy; the 12 factor products; the private record | the products were read only by P0, d2s0e1 and the C-E3 diagnostic. Their sha256s and records are committed (`../flux4-20261126/run-62051670/`). They can be rebuilt with flux4 (about 0.006 node-h) |
| `/pscratch/sd/j/josephrb/rpd-reco-d2s0e1-20261127/` | d2s0e1's clone, tools, staged copies and records | its records are committed (`../d2s0e1-20261127/run-20261127/`) |

**Not touched** (they are not ours): the RDX sidecar and the 12 omnifiles under `rdx-20261112b/`, `lat_zero.npz`, and
the S1 dumps `fd-rpd-20261103/dumps/`. No script here names them.

## The handshake

1. **`e1-list.sh`** (read-only, one login02 session). It refuses any root that is not a real directory. It prints one
   line per entry, `<type> <bytes> <path>`, sorted in the C locale, then a summary per root (entries, file bytes,
   symlinks) and `listing_sha256`. It writes nothing.
2. **The listing and its sha go to the director**, who approves that exact sha.
3. **`build_remove.sh <listing.txt>`** recomputes the sha from the listing's lines (never typed). It checks that sha
   against the node's own `listing_sha256` line, and writes `e1-remove.sh` from `e1-remove.sh.in` with that sha.
4. **`e1-remove.sh`** (one login02 session, run once):
   - it refuses off a login node, or if sacct shows any unended rpd* job;
   - it regenerates the listing and refuses unless it hashes to the approved sha, has no symlink, has no missing root,
     and has every line under the three roots;
   - it then deletes the omnifile copies in P0's `{dry,run}/staged/` first, each by its literal path;
   - then it removes each root by its literal path, checking that each is gone.

A fence round (acks, and ibu-chi told) comes before each session.

## Tests

`test_cleanup.sh` runs the three scripts on temporary roots. GNU `find -printf`, `sha256sum`, `date -d`, `sacct` and
`hostname` are PATH shims. The cases are:
- the approved listing removes the 4 omnifile copies first, then the 3 roots, and keeps their parent;
- step 3 removes only omnifile copies;
- each of these refuses with nothing removed: a file added after the listing, a symlink, an unended rpd* job, a
  non-login host, and a missing root;
- `build_remove.sh` refuses a listing whose sha line does not match its lines.

All pass ([`tests.txt`](tests.txt)).
