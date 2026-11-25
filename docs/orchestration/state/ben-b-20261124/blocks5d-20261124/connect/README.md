# (b) part 3: the LL5D read connect package (tier3-design, 2026-11-24), for the director's binding

One login read connect fetches what B5D-DECLARATION.md §2 names, and nothing else. **Nothing has run.**

**The sources: 1,655 files, about 498 MB.**
- LL5D's 1,200 toys (300 per reading at G18 and AR23);
- the 454 products those toys were graded against: central_T and seed_T, the 175 block universes and the 50 stat
  replicas at each truth;
- the flux constraint LL5D's Flux band was weighted with.

Each file is fetched at its committed pin: LL5D's manifest (`hpss_ll5d_u_list.tsv`, 980bb95e…) for the 1,654, and
`s1_assemble.CONSTRAINT_SHA256` (e38ad7d2…) for the constraint. **Not fetched:** LL5D's 4 data-control products
(data), its 4 clipmeans, and its 97 atime sidecars.

| file | sha256 | role |
|---|---|---|
| `b5d_read.sh` | `309d166d062c71c224a37e85aa2a7c1854107d28f587ccdc6041b5749d891e50` | the connect |
| `b5d_launch.sh` | `200d5d570889c884c5b82b3a5762ae1f8bf667e9349ce29a36e65b0aaca34a74` | the launcher; it holds the read's sha once |
| `gen_b5d_read.py` | (generator) | writes both from the **bound** BSEL read connect (199cc946) and launcher template, with only the source list and the names changed. Rerunning it gives the same bytes |

**Behaviour, exactly as the bound BSEL read** (BSEL-BINDING-1):
- window, sacct fence, `$OUT` absent, every source present (a purged file BAILs before any copy);
- per file: stat, a dd iflag=noatime read equal to its pin, a dd iflag=noatime copy equal to its pin, stat unmoved;
- strict sums and one tar.
- **Writes:** only `/pscratch/sd/j/josephrb/b5d-20261124` and the launcher's `/dev/shm/b5dc.*`. **0 node-h.**
- An HPSS htar fallback, on a loginNN, would be its own amendment.

**Stand-ins** (`standin/`; Debian; `/pscratch` and `/tmp` on named volumes; the only stubs are sacct and sha256sum,
on planted pins):

| variant | result |
|---|---|
| ok | rc 0; the tar's RECORDS.SHA256SUMS OK, 1,655 lines for 1,655 files |
| missing (one toy) | rc 9, BAIL source missing |
| pin_bad | rc 4, STOP |
| out_exists | rc 9, BAIL |
| window_ended | rc 9, BAIL |
| fence_running | rc 9, BAIL |

Every variant made no squeue call, wrote nothing outside `$OUT`, and removed its /dev/shm copy.

**The overlap check** (`b5d_overlap.py`, output `overlap-b5d.txt`, self-test `overlap-b5d-selftest.txt`): S2R's prefix
rule and IBUB's composition, plus IBUB's 19 ibub-20261124 entries, s2r-20261124 and rdx-20261112b.
- LL5D's products hit nothing.
- **The flux constraint is cov2d-protected and an rpd flux2 staged original.** It is declared as one acked read,
  O_NOATIME and never written, allowed only against those two owners.
- **cov2d's and limitation-resolver's acks should name it.**
