# RE-2 HPSS receipt: J0's and part B's products on tape (2026-10-24, re-1 lane)

**Status.** J0's and part B's outputs and records are on HPSS as one bundle, tape-resident and verified.
- `hashverify` passed.
- Recovery into fresh directories reproduced every member's sha256, and opened all 678 ROOT files.
- `du` reconciles to the byte.

This is R9 (a) (`DECISION-20261023-joseph-r8-r9-and-5d-scoping.md`), by the procedure RE2-BINDING-B binds
(RE2-DECLARATION-B.md §8). The director asked for it now, before part C, because pscratch purges idle files. Part C's
final products get their own bundle after part C, by the same procedure.

**MEASURES:** that these bytes are on tape and can be recovered.
**CANNOT AUTHORIZE:** any claim, or deleting the pscratch copies (they are part C's inputs).

## The archive

| | |
|---|---|
| HPSS directory | `/home/j/josephrb/mnv-re2-2d-rebuild-20261024/` |
| bundle | `re2-2d-rebuild-20261024.tar`, 59,473,920 B, sha256 `0a64d4ff6b8c1be56d1975a103b686d383512817c79448aad2f6103b431ea484` |
| manifest | `members.sha256`, 2,134 members, file sha256 `8ae9abe17beaa83cc020a76537b65e8a9ce8fdb6639ed47fb46bd521eb3fbb8c` |
| bundle digest file | `re2-2d-rebuild-20261024.tar.sha256`, file sha256 `34f9bfb5d73e0c8cd41c4133cb3769dfaaa2f79db44b6c6732b36971a6753c21` |
| source | `/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/`: `submissions.log`, `j0/` and `partb/`, every file |
| script | [`run/launch/re2_hpss.sh`](run/launch/re2_hpss.sh), sha256 `40d5ae10d338310b7b098c9f42246246f69bd4aa61c8b91fb2bb6067c689acb8`; run on login12, 12:54:16–12:57:10Z |
| records | [`run/hpss/`](run/hpss/): `members.list`, `members.sha256`, the bundle digest, and `logs/` with every step's output and `rc.tsv` |

**Note (director, 2026-10-24, RE2-BINDING-C.md).** PR #320 later parameterized `run/launch/re2_hpss.sh` in place for
part C's bundle, so the link above now opens a later version. The version this receipt ran is at commit `1442f1d2`,
whose sha256 is `40d5ae10…`, equal to the pin above.

**What the bundle holds:**
- 678 `xsec.root` files: J0's 34 and part B's 644. All 678 manifest digests equal the job-time digests committed
  in `run/j0_readout/SHA256SUMS.J0a`/`.J0b` and `run/partb_readout/sums/` (a sorted diff of the two lists is
  empty).
- Every run log, OI-136 inventory, readout record, preflight record, gate record and `SHA256SUMS` file of J0 and
  part B.
- `partb/deletions.tsv` and the quota records.

The staged inputs are not in it: they were deleted under B9, and their CFS originals remain.

## The steps (`run/hpss/logs/rc.tsv`, every exit status captured unpiped)

1. **Bundle.**
   - The member list is every file under the source, sorted. It must hold 678 `xsec.root` files.
   - The manifest gives each member's sha256.
   - `tar -tf` of the bundle equals the member list.
2. **Put:** `put -c on` for the bundle, the manifest and the bundle digest, so an md5 is stored for each (`2-put.log`).
3. **Migrate:** `migrate -R` reported all three objects migrated (`3-migrate.log`).
4. **Residency:** `ls -V` shows each object's full size at the tape level, on PV AB040200 (`4-lsV.log`):
   - the bundle, 59,473,920 bytes;
   - the manifest, 201,745 bytes;
   - the digest file, 94 bytes.

   `DISK` in the mode line is the class of service (cos 4), not residency.
5. **hashverify** `-R` exited 0 and printed `(md5) OK` for all three objects.
   - The OK set equals `hashlist -R`'s stored-hash set.
   - Both sets are non-empty, with 3 members each.
6. **Recovery.**
   - `get` into a fresh, empty directory; the bundle's sha256 matched.
   - The retrieved manifest is byte-identical to the local one.
   - Untarred into another fresh directory, every member re-hashed to the manifest.
   - The path sets agree both ways, and both are non-empty.
   - All 678 ROOT files opened, none zombie or recovered, each with keys (`6-root-open.log`).
   - **The check was first shown to fail,** on a scratch copy of the recovered tree. Each case exited with its own
     code and named the failure (`6-controls.log`):

     | case | exit |
     |---|---|
     | a tampered member | 4 |
     | a missing member | 4 |
     | an extra member | 6 |
     | an empty manifest | 3 |
7. **Reconcile.**
   - `du` gives 3 files and 59,675,759 bytes. That equals the three objects' sizes summed.
   - `ls -l` lists exactly those 3 objects.

## Caveats

- **The quota did not move.** `hpssquota` read 353.98 GiB of 512 both before and after. The 0.056 GiB added does not
  show yet, so the quota-used check is not yet closed.
  - The lane re-reads it at part C's HPSS step, and expects about 354.04 GiB, plus anything else added by then.
  - The directory itself reconciles by `du` and `ls`.
- **A recorded set file was overwritten.** The script's `verify_tree` writes `logs/6-got.set` and `6-want.set` on
  every call, so the negative controls overwrote the real recovery's path-set files. The extra-member control left
  2,135 against 2,134.
  - The real recovery's pass is recorded by its exit status (`rc.tsv` `6-verify 0`) and `6-verify.log`.
  - Its set files are not preserved.
  - Part C's run of the script will name the files per call.
- **The pscratch copies stay in place.** Part C reads them, and nothing here deletes them.
