# REPORT: 3b's npz inputs copied to HPSS (2026-10-28)

**By** the measurement session (`coverage`), for the director.

**Under** the director's ruling (2) of 2026-10-28, given in a message after PR #460: "The HPSS copy of 3b's npz inputs,
about 21.5 GiB: approved now, as a preservation step under the standing practice … with hashcreate, hashverify, a
get-back and a sha256 compare, as stage0_preserve.sh does … Leave evloop/ and merged/ on pscratch only." The need is
[`FD-CT-RETENTION.md`](FD-CT-RETENTION.md) §4 item 2.

**MEASURES:** the copy's inventory, tar digest, HPSS listing, hashverify, retrieval compare and `hpssquota`.

**CANNOT AUTHORIZE:** a deletion, a declaration or a run of 3b.

**CITABLE FOR:** where the 42 files are on HPSS, and that the stored copy equals the pscratch sources by sha256.

**NOT CITABLE FOR:** the HPSS space used by this copy, since `hpssquota` did not change (§3).

**Receipts:** [`fd/receipts-ct/preserve/`](fd/receipts-ct/preserve/).
- the wrapper `ct_preserve_run.sh` (`180c24ae…`), its `run.log` and `nohup.out`;
- `preserve.log` from the committed `docs/orchestration/state/measurement-paper/5d-design-20261023/stage0/stage0_preserve.sh`,
  run verbatim (`27ccc04a…`, equal to main's copy);
- `INVENTORY.sha256` (`52eaa265…`), `stage0-inputs.tar.sha256` and `hsi_ls_after.out`;
- `ret7.*` and `decl1.*`, the CFS name search and digest re-measures behind `FD-CT-RETENTION.md` §0.

## 1. What was copied

42 npz, 22,076,611,454 B (`run.log`), on login08, 0 node-h, no Slurm job:

| source on pscratch | files |
|---|---:|
| `$P/measurement-paper/phase1/mp1/s1/lateral/` (11 variants and their `_bkg`) | 22 |
| `$P/measurement-paper/phase1/mp1/s1/unf/` | 11 |
| `$P/w2-recoil-20261006/w2b/lateral/` | 6 |
| `$P/w2-recoil-20261006/w2b/unf/` | 3 |

The wrapper refuses unless it finds exactly 42 sources and writes the inventory by `sha256sum`. `stage0_preserve.sh`
then re-verifies every inventoried file before the tar is made (`preserve.log`: "inventory verified: 42 files").

`evloop/` and `merged/` stay on pscratch only, as ruled.

## 2. The copy

- **HPSS directory:** `/home/j/josephrb/mnv-5d-ct-3b-inputs-20261028/`, holding `stage0-inputs.tar`,
  `stage0-inputs.tar.sha256` and `INVENTORY.sha256` (`hsi_ls_after.out`).
- **The tar:** 22,076,692,480 B, sha256 `32c8b826da5c9b9d72b0a502ef683709770d651b966d67bd37c4e07b5ffd6ef5`
  (`preserve.log`). Its member count equals the inventory's, which the script checks.
- **hashcreate / hashverify:** md5 `2e1b9b2b5599c00576d7859f4b0dad6f`, "(md5) OK" (`preserve.log`).
- **Retrieval:** the tar was fetched back to pscratch, its sha256 equalled `32c8b826…`, and the retrieved copy was
  removed: "PASS: HPSS copy verified by hashverify and by retrieval" at 2026-10-28T22:19:14Z, rc 0 (`preserve.log`,
  `run.log`).
- The tar on pscratch, `$P/fd-ct-preserve-20261028/stage0-inputs.tar`, is kept beside the inventory. Deleting it is
  not proposed here.
- The two `tar: Removing leading '/'` lines are tar's notices for absolute member names; the inventory has no links.

**W2b is now held twice.** Its lateral and unf npz were already on CFS (`FD-CT-RETENTION.md` §0). The director kept them
in this copy as a second, independent one.

## 3. hpssquota

| when | reading |
|---|---|
| before, 2026-10-28T22:09Z | 422.79 of 512.00 GiB (`run.log`) |
| after, 22:19Z | 422.79 GiB (`run.log`) |
| again, 2026-10-29T00:22Z | 422.79 GiB (`hsi_ls_after.out`) |

<!-- absence-ok: a scoping statement about the instrument: hpssquota's three readings in the table above did not change across the write -->
The reading did not move for a 22.08 GB write, as it did not for F1's 1.23 GB (`FD-F1-REPORT.md` §4). So `hpssquota`
lags writes here, and the space this copy uses is not measured by it. The arithmetic expectation is about 443.4 GiB used
and 68.6 GiB free **(arithmetic: 422.79 + 22,076,692,480 B / 2³⁰ = 422.79 + 20.56)**.

## 4. Ledger and storage

- **Ledger:** one row in `fd/LEDGER.tsv`, 0 node-h, login node.
- **pscratch:** `$P/fd-ct-preserve-20261028/` joins the retention list. It holds the tar and the logs.
- Nothing was written to CFS, and nothing was deleted.
