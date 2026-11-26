# EVW5D steps 4–5 receipts (BINDING 3): the HPSS copy and the deposit fetch

This ran from `launch/bound/` at 9b8dd322 (the BINDING 3 merge) against the bound SHA256SUMS digest `31075af667c6cda13d76b0e09831a5e40180069615853a30ae34a325b8be8718`. The cert was checked before each step (lane/*-launcher.out).

## Step 4: hpss (login31)
- Launcher: `launcher rc=0`, with `script rc=0`.
- The archive is `/home/j/josephrb/mnv-evw5d-20261125-r2/evw5d-20261125-r2.tar`.
- `HTAR Create complete for /home/j/josephrb/mnv-evw5d-20261125-r2/evw5d-20261125-r2.tar. 1744094208 bytes written for 7 member files, max threads: 7 Transfer time: 10.768 seconds (161.971 MB/s) wallclock/user/sys: 11.035 15.140 3.226 seconds`
- `HTAR: Verify complete. 0 total errors, 8 total objects (8 Files,0 Dirs,0 Hard Links,0 symlinks) wallclock/user/sys: 9.890 10.147 1.296 seconds`
- Pass lines from hpss/hpss.log:
  - `accepted() on scratch: ACCEPTED rc=0`
  - `htar rc=0`
  - `hashcreate rc=0`
  - `hashverify rc=0`
  - `htar -xf rc=0`
  - `retrieved and equal to their pins: 7 of 7; files retrieved: 7`
  - `accepted() on the retrieved bundle: ACCEPTED rc=0`
  - `hpss rc=0 2026-11-26T00:31:56Z`
- hashcreate: `83e087aca5c98935e62effd34279a91a (md5) /home/j/josephrb/mnv-evw5d-20261125-r2/evw5d-20261125-r2.tar`
- hashverify: `/home/j/josephrb/mnv-evw5d-20261125-r2/evw5d-20261125-r2.tar: (md5) OK`
- hpss/hpss.log's listing shows only the `.tar.idx` line. `evw5d_hpss.sh:66` pipes `hsi ls -l $TAR ${TAR}.idx` through `tail -2`, which keeps the directory header and the idx line. The archive itself is shown by hashverify OK and the full retrieval.
- The HPSS quota line reads the same before and after (hpss/quota-*.txt).

## Step 5: fetch-products (Mac)
- `accepted rc=0` (ACCEPTED), and `launcher rc=0`.
- The deposit copy is at `/Users/josephbailey/evw5d-deposit-20261125-r2/evw5d/`, outside the repository and outside /private/tmp.
- shas recomputed there (lane/deposit-shas.txt):
```
8f009d828163161418e94997428c80a8c723fa3a015fcb63165861aa3312c3aa  constants.json
d2aac0664f8677b29414a0be9cfdf570af54f3df80a851297ccef21ebdf98e01  constants.npz
83436d151d45a2ba01947a7d780a649fd250e1adec60e9003bf78ac351bb951a  product/data_b-_j-.npz
c2ec93fb529769b5b8cdb56966ac115a4e02da90880e83b8fd23513de9b500f6  run.json
0fceefcdcfcd5c48070453707b55f40e55787909f98481dadcdc82dd0897aba6  weights.npz
a985eb3752f615c2e58886f76c70515cc7e976532daa63bc09d810384062fbdf  evw5d.done
31075af667c6cda13d76b0e09831a5e40180069615853a30ae34a325b8be8718  SHA256SUMS
```

## Files
- `hpss.tar.gz` (sha256 `3181b83e599de355da85bd8530c20c6ff32098c3b87a95e617c26050edce1e4e`) is the HPSS step's receipt archive as fetched. `hpss/` is its extraction.
- `lane/` holds the Mac side: the launcher outputs for hpss, the receipt fetch and fetch-products, the hpss session directory, and deposit-shas.txt.
- The receipt fetch (launcher `fetch` mode, scp only) also re-copied post.tar.gz. It is byte-identical to the merged `receipts/attempt2/post.tar.gz` (3a4dc3cf…).
