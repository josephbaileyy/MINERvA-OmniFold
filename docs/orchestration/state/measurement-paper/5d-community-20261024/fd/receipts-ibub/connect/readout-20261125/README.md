# IBUB connect O, the readout, under BINDING 3: rc 0, both tunes PASS (2026-11-25)

**By** `director-helper-3`. The run was under the director's GO for IBUB BINDING 3 (`../../../../IBUB-BINDING-3.md`, #1332,
merge `0659f8ab037e09a19c6491eb352ac0fa96d3d06e`). The connect and launcher were extracted byte for byte from that
merge with `git cat-file blob` and checked by `shasum`. Every bound file's sha256 at the merge equalled the binding's.
The node cloned M `b43a5b984b28e68b6ea478b8a63329505c8f78be`, for job 61924744 at `d12c4f2a3`.

**Preconditions** (ruling 3), all met before the launcher ran:
- the fresh acks after the merge, in `acks.txt`: cov2d ACK YES at 13:13:52Z, limitation-resolver ACK YES at 13:14:01Z;
- the NERSC certificate, checked with `ssh-keygen -L` and converted to UTC by command: valid until 2026-11-26T03:28:45Z.
  The window ended an hour earlier, at 1795660125 (02:28:45Z, `window.txt`), to leave time for the fetch;
- the director's GO by message, naming BINDING 3.

**The verdict lines** (verbatim from `connect-readout.log.txt`):

```
READOUT G18 rc=0: IBUB-READOUT G18 PASS reading={'K10': 'DIFFER', 'K5': 'DIFFER'} controls_failed=0 stops=0
READOUT AR23 rc=0: IBUB-READOUT AR23 PASS reading={'K10': 'DIFFER', 'K5': 'DIFFER'} controls_failed=0 stops=0
```

The director reviewed this record before the PR (ruling 5).

| step | record |
|---|---|
| launcher | `launch-start-utc.txt` 2026-11-25T13:14:18Z; staged `sha256 5b3cdf7b…` on login38; `launcher.out.txt` ends `launcher rc=0`; `launch-end-utc.txt` 13:16:31Z |
| connect start | `connect-readout.log.txt`: 13:14:27Z on login38 |
| fences | cov2d rev 3 `FENCE CLEAR`; the sacct fence (prefixes ibub_, ibuchi_, cov2d, t2a, rpd, msr) `fence clear` |
| the job | `61924744\|ibub_run\|COMPLETED\|0:0 (terminal: COMPLETED)`, read before anything was fetched |
| fetch | 8 records with O_NOATIME; IBUB-DONE `de4ff546…` and `units/refcheck.json` `784163284dec…` equal the job-end records (`../run-61924744/job-end/`) |
| clone | HEAD `b43a5b98…`; porcelain `--ignored` empty before; the 6 ibub sums OK; P0's records present in M |
| overlap, MAT | `OVERLAP: CLEAR (pairs checked 1040, hits 0)`; `{"mat_setup_scripts": 6, "mismatches": 0}` |
| readouts | G18 then AR23, each about 20 s wall and 0.5 GB RSS (`/usr/bin/time`); `readout rcs: G18 0, AR23 0` |
| deploy after | porcelain `--ignored` empty after, checked before anything was published |
| copy-out | `$N/readout/{G18,AR23}/`, each file `sha256 -c` OK on the node |
| records | `fetch-readout.tar`, 19 records; its sha256 equals the log's line; `RECORDS.SHA256SUMS` holds (`records-check.txt`, empty under `--quiet`) |
| the end | `/dev/shm/ibub-connect` removed (`left=no`); `ibub readout rc=0` at 13:16:07Z; `connect-readout.done.txt` 0 |

`session.err.txt` and `fetch.err.txt` hold only NERSC's login banner (1 and 3 copies).

**The files and their sha256** (computed with `shasum -a 256` here; the tunes' files are copies from the fetched tar):

```
d78ed2367dbaf37ae2957c18c6a12f9092dd7db9fee7f48cea420ae41be5f440  fetch-readout.tar
53f1266f274d1b650316eb4d3129b50d1de73141e19125e05247894b4562fab2  RECORDS.SHA256SUMS.txt
dd5c718bcff4c57d5254780e9c520e051e6e89a1aa4b5e279899beb0e253ca39  G18/ibub_G18.json
ea95ec81a8633c61d1cf64493e865a7bba4b0f262280317ec3b369d4f82ff078  G18/ibub_G18_errors.npz
13320b21534a7ce46696b0ec8134af61924e8e0ff746b1b4bf8d1d910b9915b8  AR23/ibub_AR23.json
f5fabeac61f54d821d0e0db14711b471349daee1f0fde9ea73430df5c2470a98  AR23/ibub_AR23_errors.npz
05b3c50605b4481142e88cdabea4ed346d348b883d4817e9c1c3fcd7b39cc501  connect-readout.log.txt
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  connect-readout.done.txt
edaf29b5089e0d9113b29c5581ccd7d0f740ce4bb22bccabba3d7eef3d7de5a7  launcher.out.txt
6e6c3fa3aaf849eb5e44fbbf15c7b579b1c1c7d25209049761e56628a4340ec4  session.out.txt
e42ad52c9bd85228170cedf4cee5db9cf3ff240c0269d14cf56414a038d61e75  session.err.txt
870a2c3d1469b10ccfa9b77292f7085d138a187dadb4485b57f63ee754d9f622  fetch.err.txt
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  records-check.txt
97ced391c2f8e9317ab4e1d8429aacbe7ab993f7a4cbb32b1a874410661e1db2  acks.txt
```

`RECORDS.SHA256SUMS.txt` is the tar's top-level `fetch-readout/RECORDS.SHA256SUMS`. The `*_errors.npz` files are
gitignored by pattern and were force-added by explicit path.

**MEASURES:** that connect O ran once as bound, and what the readout printed and wrote. **NOT CITABLE FOR:** any IBU bias
value, any comparison with OmniFold, or any note wording. Joseph writes the wording after the director's review.
