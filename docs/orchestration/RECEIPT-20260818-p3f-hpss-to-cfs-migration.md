# RECEIPT 2026-08-18 — `mnv-p3f-pet-fullevent-final` migrated HPSS → CFS and deleted from tape

**Verdict: `HPSS_DELETE_ISSUED` for 240/240 objects. The CFS copy is now the only copy.**

This receipt exists because the deletion is irreversible and the working directory that produced
the evidence (`/global/cfs/cdirs/m3246/josephrb/p3f-move-20260818/`) reads as disposable. Every
file cited below is committed beside this one under
[`state/p3f-hpss-to-cfs-20260818/`](state/p3f-hpss-to-cfs-20260818/) — see `BEN-490`.

## Authorization

Joseph, this session, in three steps: *"I think the right move is to go through with the move"* →
*"okay can you do the move?"* → *"yes run the deletion"*. The deletion was held for the third of
these and was not folded into the copy. Independently recorded by the mediator at `ffa32007`
("the HPSS duplicates are being deleted on the advisor's judgement that CFS is safe as the
resident tier").

**This REVERSES `OI-48`'s 2026-08-13 decision** (`d2c7699`, "Joseph chose to have Ben raise the
allocation rather than move to CFS"). The trigger was Ben Nachman asking, in reply to the headroom
request, why HPSS rather than the group's CFS allocation.

## Operands

| quantity | value | source |
|---|---|---|
| objects | **240** (120 `.root`, 120 `.json`) | `p3f_files.txt` |
| bytes on HPSS before | **1,134,998,230,283** | `hsi ls -l`, summed |
| bytes on CFS after | **1,134,998,230,283** | `find -printf %s`, summed |
| difference | **0** | derived from the two rows above |
| stored HPSS md5s available | **240 / 240**, 0 missing | `hsi hashlist` |
| copy-leg verification | 240 OK, 0 MISMATCH, 0 MISSING | `move_57199158.log.txt` |
| re-verify leg (immediately pre-deletion) | 240 OK, 0 MISMATCH, 0 ABSENT | `reverify.txt` |
| distinct md5s | **240** | `reverify.txt`, `awk` + `sort -u` |
| HPSS quota before | **1.33 TiB / 512.00 GiB = 265.1%** | `hpssquota`, in `delete_57214668.log.txt` |
| HPSS quota 1 s after deletion | **1.33 TiB / 512.00 GiB = 265.1% — UNCHANGED** | same file |
| CFS m3246 before | 77,418 / 102,400 GB = 75% | `cfsquota` |

**A 32,768 B discrepancy appeared once and is explained, not waved away:** `du -sb` on the CFS
destination returned 1,134,998,263,051 against HPSS's 1,134,998,230,283. The delta is the
directory inode's apparent size (`stat -c %s` on the directory = 32,768). Summing *file* bytes
only, both sides are 1,134,998,230,283 — equal, not approximately equal.

## THE QUOTA HAS NOT MOVED YET, AND NOTHING HERE CLAIMS IT HAS

The post-deletion `hpssquota` read **265.1%, identical to the pre-deletion read**, taken one
second after the last `hsi rm` and re-read again at 13:20:52Z with the same result. HPSS quota
accounting is lazy; the directory listing is the evidence that the deletion took, and it is empty
(`hsi ls -l mnv-p3f-pet-fullevent-final` returns no entries; the directory's own size dropped
4096 → 512 and its mtime moved to 2026-08-18 06:19).

**Do not quote 58.6% as an achieved state.** It is the *predicted* post-accounting figure
(1,357.22 GiB residency − 1,057.02 GiB removed = 300.17 GiB = 58.6% of 512 GiB) and it is a
prediction until `hpssquota` says otherwise. This is the same failure family as `BEN-323`
(a declared state rendered as an observed one) and the lazy-block-accounting rule in
`AUTONOMOUS_LOG_20260805.md`.

## Method, and the two guards that mattered

Copy (`57199158`, xfer queue, COMPLETED 00:51:29) and re-verify-then-delete (`57214668`, xfer
queue, COMPLETED 00:38:44, exit 0:0). Both scripts are committed here.

1. **Verification is against the digest HPSS stored at write time**, not one computed from the
   copy. A copy checked against its own hash proves nothing about the transfer.
2. **The resume guard keys on a post-verification `.ok` marker, never on file existence**
   (`BEN-023`): each object is fetched into a staging directory, md5'd, and only then renamed
   into place. A truncated fetch cannot satisfy its own guard and block its repair.
3. **The re-verify and the deletion are in one job**, so the last check precedes the irreversible
   step by seconds rather than by the ~15 h that separated the copy from the decision to delete.
   The deletion is gated on `PASS == 240`; any failure exits 1 with nothing removed.
4. `hsi` path arguments chunked at 6 (segfaults above ~36); `ssh -n` throughout; full streams
   redirected to files and never piped through `tail` (`BEN-026`).

**The evidence was very nearly not committed at all, which is `BEN-490` happening to itself.** Both Slurm
logs are `*.out`, and `.gitignore:13` ignores `*.out` repo-wide — `git add` on the directory took the
manifests and silently skipped the two files that record the deletion actually issuing. They are committed
here as `*.log.txt`. A rule that says *promote the verification record in the same commit* is not enough on
its own; the promotion has to be **verified to have landed**, because the failure is silent.

## What is NOT covered

- `mnv-quoted-products-20260812` (300.17 GiB) **stays on tape, untouched and unverified** — see
  the narrowed `OI-50`.
- `mnv-p3f-smoketest` (12,334 B) and `backups` (3,360 B) are untouched.
- **Durability tier dropped.** These 240 objects were tape + CFS during the window between the two
  jobs; they are now CFS only. CFS is not purged, but it is not an archive and is not backed up.
  The regeneration chain remains 2,307 files / 10.48 TiB on purgeable pscratch at 79.9%, which is
  why the products were worth protecting in the first place — that argument is unchanged by the
  tier change and is the open exposure, recorded as `OI-131`.
