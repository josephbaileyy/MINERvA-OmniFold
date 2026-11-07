Per-period 2D benchmark: the operand copies deleted under two ledger rows (the director's rulings of 2026-11-07).

The rulings: keep the copies until the outcome record is merged, then delete them under a ledger row, as REF-C2C1
stage 4 did (#846). The 2 smoke-test copies follow as a second row. Run after #879 and #880 were on origin/main
(merge 31be8f55, checked by this lane). Both rows ran on login36 under /usr/bin/python3 3.6.15, at nice 19 and 0 node-h.
Each script's sha256 was sent to the director before launch, and compared on the cluster before it ran.

What each script does, in order:
1. Refuse unless on a login node with a new ledger dir.
2. The root must hold exactly its declared files, all regular.
3. Every file's sha256, read with O_NOATIME, must equal its declared digest.
4. Only when every check passes is anything removed: rm by literal path, then rmdir.
5. Every path must then be absent.
Exit: 0 done; 4 STOP with nothing deleted; 8 something still present; 9 an rm failed.

ROW 1 (delete_copies.py, sha256 31cc5838476dbb382a9ec45010f6330146eb6f48fb26aeda1404d9c28626b92d; connect3.sh 3a00f583...):
  root /pscratch/sd/j/josephrb/per-period-benchmark-20261106/read/copies
  - The 39 operand copies, with their digests from receipts/read/verify.json, which equal INPUTS.sha256.
  - copies.json and verify.json, byte-identical to the committed receipts/read/ copies (SHA256SUMS), removed so that
    the directory could be removed.
  - 2026-11-07T07:03:47Z: 41 entries before, exactly the declared ones; 41/41 digests equal, 0 differ; 41 rm; rmdir;
    42 paths absent after; rc 0.
  - Files: row1-read-copies/ledger.log and ledger.json, with each path, its declared and measured digest, and the
    removal timestamp.

ROW 2 (delete_smoke_copies.py, sha256 1e50a3eef5823788258c5a89d6bb1e7d1fe5ab58a7e25058fbdc954b65b15f42; connect3b.sh d1422b86...):
  root /pscratch/sd/j/josephrb/per-period-benchmark-20261106/connect1/smoke-copies
  - The connect-1 smoke-test copies of the published ROOT and pu_PA_b01.
  - The script is the row-1 code with only TARGETS and LEDGER changed (`diff delete_copies.py delete_smoke_copies.py`).
  - 2026-11-07T07:04:36Z: 2 entries before; 2/2 digests equal; 2 rm; rmdir; 3 paths absent after; rc 0.
  - Files: row2-smoke-copies/ledger.log and ledger.json.

Not touched: the originals the copies were made from, the code deploys (connect1/code, read/code, delete-code*), the
R/ receipt dirs on the cluster, and every COV2D path.
Tests: test_delete_copies.py, 11 tests, OK (each guard in both directions; PPB_INPUTS points at INPUTS.sha256 for the
digest cross-check).

CITABLE FOR: the removal of these 43 files and 2 directories, with their digests.
NOT CITABLE FOR: anything about the readings. Those are in OUTCOME-20261107-per-period-2d-benchmark.md.
