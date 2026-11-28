# The sidecar probe's run, 2026-11-26 (RPD-RECO amendment 1, §2 and §8)

**The binding constraint: lat_zero's purge exposure begins 2026-12-25T08:53:42Z.** Its atime is 2026-10-30T08:53:42Z,
and the exposure is atime + 56 days. That is about 2.5 weeks earlier than §8's estimate of about 2027-01-12, which used
the sidecar's and the omnifiles' write dates. The e1 chain through P0 is planned to finish well before 2026-12-20 (the
director, 2026-11-26). lat_zero is not to have its atime refreshed or to be copied; if a copy is ever needed, the
director takes it to Joseph.

**The run.** One run, under the director's run GO, from #1386's merge 44532294 (wrapper `sidecar-probe.sh`
`54f149ce…`, reader `5de764bd…`). Conditions before it:
- geanttw P0's jobs 62042572 and 62042575 COMPLETED 0:0 in sacct;
- acks from tier3-design (16:23:23Z) and minerva-lib (16:23:53Z);
- the certificate checked by `TZ=UTC ssh-keygen -L`.

It ran on login02, 16:24:28–16:24:32Z, with rc 0 and verdict **PASS**:
- **The sidecar:** sha256 `641ba34c5ebde6d1881c705b862fab144a6fbb8a58ef3d84e59f1c8ba030a79e`, equal to the pin, over
  2,364,943,114 bytes. Its atime (2026-11-17T17:45:29Z) did not move, so O_NOATIME held on the cluster. Its purge
  exposure begins 2027-01-12T17:45:29Z.
- **The 12 omnifiles:** present, stat only, never opened. Their atimes are 2026-11-17T05:08Z, so their purge exposure
  begins 2027-01-12T05:08Z.
- **lat_zero.npz:** present, stat only, 1,548,311,762 bytes, purge exposure from **2026-12-25T08:53:42Z**.
- Nothing was written on the cluster. Both lanes received END.

`probe.json` is the report as written to stdout. `probe.err` is its stderr (NERSC's login banner, then the probe's
start and end lines). `rc.txt` is the exit status.

**Existing copies of lat_zero's bytes** (sha256 `6ca02c3d8b09dfd168b5184c03d433a7bd65749f5f6fc4cefecdbed7b6ce052f`),
found in the records on 2026-11-26. Nothing was read or touched to find them.
- **HPSS:** `/home/j/josephrb/mnv-5d-ct-3b-inputs-20261028/stage0-inputs.tar` (22,076,692,480 bytes; sha256
  `32c8b826…`) holds `/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/s1/lateral/lat_zero.npz`. It is line 22 of
  its `INVENTORY.sha256`; the 42 files were verified before the tar was made. It was put on 2026-10-28 and verified by
  hashverify and a full retrieval (`fd/receipts-ct/preserve/preserve.log`, `run.log`).
- **CFS:** `/global/cfs/cdirs/m3246/josephrb/prd-release-preservation-20261008/pscratch/sd/j/josephrb/w2-recoil-20261006/w2b/lateral/lat_w2b_rrzero.npz`
  is 1,548,311,762 bytes, lat_zero's size (`fd/receipts-ct/preserve/ret7.out`). That area's `W2-SHA256SUMS` records
  `6ca02c3d…` for it, which matched in the CT preservation's cross-check (`run.log`, 2026-10-28). Its CFS bytes have
  not been rehashed since.
- **Other scratch files with the same digest,** each on its own purge clock, atimes unknown:
  `w2-recoil-20261006/w2b/lateral/lat_w2b_rrzero.npz`, `fd-ct-5b-20261030/dumps/lat_ALL.npz` and RDX's staged
  `rdx-20261112b/out/stage/lat_zero.npz`.
