# GENIE spline product listing on CVMFS, 2026-11-24 (login05)

**By** limitation-resolver, at the director's request (2026-11-24), before Joseph decides a COVFIX amendment: the
node's own listing of the GENIE cross-section (spline) product on CVMFS. Two read-only ssh sessions to login05 ran
listings and extended-attribute reads only. There were no file contents, no find over the tree, and no stat of a
spline file. Nothing was written on the cluster.

## Session 1: [`listing.out`](listing.out) (11:14:42Z to 11:14:43Z; ssh rc 0)

The exact remote line is in [`remote-command.txt`](remote-command.txt). [`listing.err`](listing.err) holds only the
login banner. The four requested items, verbatim in `listing.out`:

1. **`ls -la …/products/genie_xsec/v3_04_00/NULL/`** (rc 0) lists five tune directories:
   - `AR2320i00000-k250-e1000`
   - `G1802a00000-k250-e1000`
   - `G1810a0211a-k250-e1000`
   - `G1810a0211b-k250-e1000`
   - `GDNu2001a00000-k120-e200`
2. **`ls -la …/products/genie_xsec/`** (rc 0) lists these versions, each with a matching `.version` directory:
   R-2_8_0, v2_10_2, v2_10_6a, v2_12_0, v2_12_10, v2_12_8,
   v3_00_02, v3_00_04, v3_00_04a, v3_00_04_ub2, v3_02_00, v3_04_00, v3_06_00, v3_06_02_sbn1 and v3_06_02_sbn2.
3. **The repository attributes:** `getfattr` is available. Given three `-n` options in one call, it printed only the
   last, `user.root_hash`, rc 0 (getfattr honours a single `-n`).
4. **`ls …/products/genie/v3_04_00/`** (rc 0, one level) lists: `Linux64bit+3.10-2.17-c7-debug`,
   `Linux64bit+3.10-2.17-c7-prof`, `Linux64bit+3.10-2.17-e20-debug`, `Linux64bit+3.10-2.17-e20-prof` and `ups`.

## Session 2: [`listing-2.out`](listing-2.out) (11:15:00Z; ssh rc 0)

The exact remote line is in [`remote-command-2.txt`](remote-command-2.txt). It is item 3 again, one attribute per
`getfattr` call, each rc 0:

| attribute | value |
|---|---|
| `user.fqrn` | `larsoft.opensciencegrid.org` |
| `user.revision` | `1249` |
| `user.root_hash` | `ea35e3340c01bfaaf1eb70be6d1bed654dedb642` (the same in both sessions) |

**CITABLE FOR:** what login05's CVMFS client listed at those times, at repository revision 1249. **NOT CITABLE FOR:**
whether any tune's splines are complete or correct, or any physics result. This receipt lists directories only.
Matching these names against COVFIX's chosen validation tunes is the director's and Joseph's reading, not this
receipt's.
