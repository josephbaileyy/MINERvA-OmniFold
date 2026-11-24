# The q0 extract connect: the run (2026-11-24, tier3-design)

**Approval.** The director gave the GO for `q0_connect.sh` sha256 `9fc0f3c0…` through `q0_launch.sh` `b0f60d5f…`, once,
at branch head `1fd6f922`.

**The fence ruling** (the director's, recorded as asked). `ibuchi_` was dropped from the fence prefixes, because
ibuchi_ana 61908135 was RUNNING and a refusing fence on it would have stopped the connect for no reason.
ibu-chi-squared-issue declared its job disjoint from the omnifile (`../overlap-local.txt`); this is the same ruling as
for RPD-RECO P0 (FD-RPD-RECO-BINDING-2-ADDENDUM-3.md:83). The prefixes used were `cov2d,rpd_,ibub_,d2s0,covfix`. They
are a launch argument, so the connect's sha is unchanged.

## Acks and the window (each UTC time is from the peer's `date -u`)

- **Acks:** cov2d 08:10:20Z, director-helper-3 08:10:59Z, limitation-resolver 08:14:18Z.
- **The window** ended at 08:25:20Z, which is the oldest ack + 900 s, computed with `date`. limitation-resolver was told
  right before the connect, and all three got END messages afterwards.

## The run

- **On login38**, 08:14:55Z to 08:15:38Z, script rc 0. The /dev/shm copy's sha256 was checked on the node, and both
  the cov2d fence (rev 3) and the sacct fence were clear. The extractor's sha256 `9ef4a1f2…` was checked; it ran in
  29 s with a peak RSS of 6.4 GB.
- **The extract's checks:**
  - the omnifile's sha256 equalled the pin `b6d2651c…`;
  - every named branch was present;
  - 20,498,013 rows passed, of 32,849,103 entries;
  - the omnifile's atime was unchanged (stat before equalled stat after);
  - the recovery control's max |W − W(q0)| was 3.2e-10 GeV over 20,181,786 rows, against a tolerance of 1e-6; W² < 0
    occurred on 316,227 rows. Both agree with M4-W-RECORD.md:108.
- **The fetch** finished at 08:16:44Z. The tar's sha256 `197f835c…` equals the one in the connect's log, and all 6
  entries of RECORDS.SHA256SUMS check.

## The product

The product, `q0_extract.npz` (sha256 `91d013793fae94a363bc3e515fa600474c0d9218e412cd0766b42535c7f152b5`,
778,927,176 bytes), is **not committed** because of its size. It is kept at
`~/msr-work/q0study-session-20261124/records/extract/` on the laptop. Its sha256 is in `records/RECORDS.SHA256SUMS` and
in `records/extract/q0_extract.json`, and `q0_analyze.py` checks it before use. The cluster copy under
`/pscratch/sd/j/josephrb/q0study-20261124` is static; removing it is Joseph's call.

## Files

- `launcher.out.txt`, `session.out.txt`
- `session.err.txt` and `fetch.err.txt` (the NERSC login banner only)
- `connect-q0.log`, `connect-q0.done.txt`, `records-check.txt` (empty, meaning every sum held)
- `records/`: the tar's contents without the npz, namely the logs (the connect script and extractor as run, and the
  extractor's output and stderr) and `q0_extract.json`
