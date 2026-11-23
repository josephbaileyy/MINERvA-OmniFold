# MSR connect P, attempt 1: BAIL at cov2d's fence rev 2 (2026-11-23, tier3-design)

Under the director's GO for connect P (Joseph via the director, 2026-11-22), at package head `28a3c6c3`: connect
`msr_probe_connect.sh` 44f8ad7a, launcher 4475d249, M `83d7aee5`.

- **Acks** (`acks.tsv`, each time from `date -u`): director-helper-3 03:13:18Z, cov2d 03:13:19Z, limitation-resolver
  03:13:36Z. The window end is the oldest plus 900 s, 1795404498 (03:28:18Z; `wend.txt`). limitation-resolver was told
  before the connect.
- **The session** was on login38, 03:14:13Z–03:14:26Z, with ssh rc 0. The /dev/shm copy was checked at its sha256 on the
  node.
- **The outcome:** the embedded cov2d_fence.sh rev 2 (3fbc9cbd) ran first, as declared. Its sacct query
  `-S <60 days ago> -E now` was refused by Perlmutter: `sacct: error: Too wide of a date range in query`. The fence
  printed `FENCE REFUSED: sacct failed` and exited 3. The connect then printed `BAIL cov2d fence rev 2 not clear (rc 3)`,
  and the script rc was 9 (`session.out.txt`).
- **Nothing was written.** The BAIL comes before `$OUT` (/pscratch/sd/j/josephrb/msr-p-20261122) is created. The bail
  path removed `/dev/shm/msr-connect` and the self-copy, and the launcher removed its `.out`. The launcher made no fetch
  (`launcher.out.txt`, rc 9). No input was read, the IBUKT root was not touched, and nothing went to CFS.
- **Disposition:** terminal for this attempt, by the director's condition 2. There is no repair round, and the defect
  goes to the director and to cov2d, whose fence it is.

The login banner in `session.err.txt` is the site's own notice.
<!-- absence-ok: the record of a bail; "nothing was written" describes this attempt's own outputs -->
