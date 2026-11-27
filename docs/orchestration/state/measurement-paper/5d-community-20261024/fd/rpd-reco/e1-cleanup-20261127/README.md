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
   - it regenerates the listing and refuses unless it hashes to the approved sha, has no missing root, and has every
     line (`<f|d|l> <bytes> <path>`, the path possibly with spaces) under the three roots;
   - it allows symlinks only inside each root's `clone/`, and only the clone's own committed ones. Per root, their
     sorted relative paths must hash to the sha of the git tree at S's symlink list (241 paths, `a53113c7`), which
     `build_remove.sh` computes from git. `rm -rf` removes a symlink and never follows it;
   - it then deletes the omnifile copies in P0's `{dry,run}/staged/` first, each by its literal path;
   - then it removes each root by its literal path, checking that each is gone.

A fence round (acks, and ibu-chi told) comes before each session.

## Revision after the listing (2026-11-27)

The first `e1-remove.sh.in` (`ba8227d2`) refused any symlink. The listing (step 1, `listing_sha256` `2ac64747…`)
showed 241 symlinks in each root, all inside `clone/`. They are exactly the 241 symlinks committed in the git tree at
S, and the three sets compare equal. Three lines also hold a path with spaces (`clone/docs/MINERvA with OmniFold --
3D+.pdf`), which the strict three-field check would have refused.

The template now:
- allows only the clones' committed symlinks, by sha, with any other symlink still refused;
- parses each line as type, size, then the rest of the line as the path.

Applied to the real listing, these checks give: per root, links sha `a53113c7` (equal to git's), 0 stray symlinks, 0
malformed lines and 0 missing roots. The 24 omnifile copies are 14,746,873,018 bytes.

## Step 1's record ([`step1/`](step1/))

- `listing.txt.gz`: e1-list.sh's stdout from one login02 session (05:35:00Z to 05:35:54Z, ssh rc 0), gzip -9 -n.
  Unzipped, it is 16,607,481 bytes with sha256 `e74f1cbfdac09080259865073d1860b24929380ceed9c25eb4ea7e4897d527ff`.
  Its listing lines hash to `listing_sha256` `2ac64747d2a85ad611d33c04a1649869ef57f746408dabd36fe5a7afb8be6f0a`.
- The per-root summary:
  - rpd-reco-p0e1-20261126: 35,260 entries, 21,241,300,042 file bytes, 241 symlinks;
  - rpd-reco-flux4-20261126: 35,263 entries, 6,509,214,663 file bytes, 241 symlinks;
  - rpd-reco-d2s0e1-20261127: 35,179 entries, 4,055,885,538 file bytes, 241 symlinks.
- `list.err.txt`: NERSC's login banner.

## Step 2's record ([`step2/`](step2/)): all three roots removed

The director approved listing `2ac64747…` and the revised template and build (2026-11-27). `build_remove.sh` then
wrote `e1-remove.sh`, sha256 `3b60ecc7d10c70f11116a326b932071aadc410dd6f9c02538e2bce84bd34e862`, which the director
also approved.
- A first build from the package directory refused: "S has 0 symlinks, not 241". Run in a subdirectory, `git ls-tree`
  lists paths relative to that directory.
- It was rebuilt with `REPO_FOR_LINKS` set to the repository root, the build's existing option, so no approved byte
  changed.
- `e1-remove.sh` differs from the template only in its two filled values (APPROVED, and CLONE_LINKS `a53113c7…`).
- `ls-tree --full-tree` is on the tidy-up list.

**The run:** one login02 session, 05:56:07Z to 05:58:41Z, ssh rc 0, after #1421's merge
([`step2/removal.log.txt`](step2/removal.log.txt)).
- The cert was re-read. cov2d acked at 05:45:22Z and tier3-design at 05:45:25Z, and ibu-chi was told. END followed.
- sacct showed no unended rpd* job.
- `listing_sha256` was `2ac64747…`, equal to the approved one.
- The symlinks were only the clones' committed ones.
- The 24 omnifile copies were removed first, all rc 0: 14,746,873,018 bytes.
- Then each root:
  - `rpd-reco-p0e1-20261126`: rc 0, gone;
  - `rpd-reco-flux4-20261126`: rc 0, gone;
  - `rpd-reco-d2s0e1-20261127`: rc 0, gone.

**Space freed:** 31,806,400,243 bytes of files (29.62 GiB), the approved listing's per-root totals. The RDX sidecar, the
omnifiles, lat_zero and the S1 dumps were not named and were not touched.

## Tests

`test_cleanup.sh` runs the three scripts on temporary roots. GNU `find -printf`, `sha256sum`, `date -d`, `sacct` and
`hostname` are PATH shims. The cases are:
- the approved listing removes the 4 omnifile copies first, then the 3 roots, and keeps their parent;
- step 3 removes only omnifile copies;
- each of these refuses with nothing removed: a file added after the listing, a symlink outside `clone/`, a clone
  missing one of S's symlinks, a clone with an extra symlink, an unended rpd* job, a non-login host, and a missing root;
- the clones in the fixture hold S's 241 symlinks and a file with spaces;
- `build_remove.sh` refuses a listing whose sha line does not match its lines.

All pass ([`tests.txt`](tests.txt)).
