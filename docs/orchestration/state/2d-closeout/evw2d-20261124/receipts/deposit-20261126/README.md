# EVW2D's HPSS copy and deposit fetch, 2026-11-26 (EVW2D-BINDING-2)

The steps of EVW2D-BINDING-2 (#1391, merge c9b485ce), each run once under the director's GO, from
`launch/bound-deposit/` in a clean checkout at c9b485ce. The bound files are `evw2d_deposit.sh` 91fc4e1b,
`evw2d_hpss.sh` 5c674c6c and `PINS.txt` 7966ec11. The products are the run accepted under BINDING 1: job 62022231,
SHA256SUMS digest e60867ef, evw2d.done 830d7d76, config bee02d38.

| step | when (UTC) | result |
|---|---|---|
| hpss (login02) | 18:57:22–18:58:32 | rc 0; the archive verified by retrieval and renamed to its final name |
| fetch | 18:59:34 | rc 0; `hpss.tar.gz` (sha256 `1a262ac777ebf8ff3818f791a64bcffe8f6f9396ba6958ee2a6e9486d0624a62`) VERIFIED |
| fetch-products | 18:59:54–19:01:28 | rc 0; the six files copied to the Mac and ACCEPTED |

Before the hpss step, cov2d, director-helper-3, tier3-design, minerva-lib and ibu-chi each acked (18:56:50–18:57:08Z),
and each received END. The certificate was checked by `TZ=UTC ssh-keygen -L` before each step.

**The HPSS copy:** `/home/j/josephrb/mnv-evw2d-20261126/evw2d-20261126.tar` (1,182,663,168 bytes) and its `.idx`
(4,392 bytes). From `hpss.tar.gz`'s `hpss/hpss.log`:
- `htar -Hcrc -Hverify=1` to the part name gave "0 total errors, 7 total objects", and hashcreate and hashverify
  (md5 OK) passed;
- a full retrieval into a private /dev/shm directory was "equal to their pins: 6 of 6; files retrieved: 6", and the
  checker accepted the retrieved copy;
- `htar -tf` of the part archive listed 6 of 6 names, then the index and the archive were renamed;
- the final pair listed, and `htar -tf (final)` listed 6 of 6 names.

**The deposit copy:** `/Users/josephbailey/evw2d-deposit-20261126/out/`, a new directory on the Mac. From now on it is
Joseph's copy, and no lane touches it. The six sha256s were recomputed on the Mac after the copy:

```
e60867ef66eb47172a0e90140abc7a366d780dfc3aa3f9beb426a40a48d1416e  SHA256SUMS
830d7d7641c1a5bca96fda4bde47094cf047abc8df183304aa99986414e1f133  evw2d.done
1fe4449ee7ec34067f5d2a20aa841f2c97fd2f678eaa7f554ab583ad75daf2ba  constants.json
445482fe642a36b1330214bd019deb6938047d932009cc2c3110aa5b192f4ade  run.json
928e6f7fd434fe558bf6c35e60ef05386ad668b5bdaa11cb1309f443248c17ce  xsec.root
bf452352da52f12a2788f76c4caf9e8402600ba06d352fc99e9344d87367b108  weights.npz
```

The Mac checker ran evw2d.py 6106b23a as the very bytes hashed, with python3 and numpy 1.26.4. It gave `ACCEPTED`:
`accepted_pass` true, acceptance names, manifest, present and rehash all true, with the SHA256SUMS, evw2d.done, config
and job bindings holding.

**The HPSS quota:** after the archive, josephrb's usage charged to m3246 is 462.90 GiB of 512 GiB (90.4%), in both the
before and after reads. Roughly 49 GiB remains.

**Here:** `hpss.tar.gz` (the hpss step's receipts, as fetched) and `session/`, the Mac-side output of each step: the
launcher's output for the three steps, and the hpss step's ssh session stdout and stderr (stderr is NERSC's login
banner). weights.npz and the deposit copy are not committed here.
