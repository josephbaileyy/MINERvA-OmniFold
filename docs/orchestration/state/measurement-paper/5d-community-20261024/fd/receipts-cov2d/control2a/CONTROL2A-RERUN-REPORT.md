# COV2D control (2a) rerun after addendum A1. **CONTROL-2A PASS** (2026-11-04)

**By** the `cov2d` session, under `COV2D-BINDING-1.md` and `COV2D-BINDING-1-A1.md` (merged at
`be43e3bdd7780ec8c6b6dd6b7a11e9957e3ae8da`, ruling 2).
**MEASURES:** control (2a) of `COV2D-DECLARATION.md` §2 on `$CV`'s real data tree, with the writer bound at `bb3892e5`.
**CANNOT AUTHORIZE:** (2b), the pilot or any toy. The STOP count stays at one (A1 ruling 4). This PASS does not reset
it.

## The kept file: what the pilot re-checks

`/pscratch/sd/j/josephrb/cov2d-2a/writer_control.root`, 62,784,801 bytes, sha256
**`7eb39088a42844b48ec1f8e1b6b586b8d8d4363611d68b726112f9f75c99b9db`**. That digest was checked three times:
- by the script after its copy;
- by the listing (`2a2_node_listing.txt`);
- again after the /dev/shm removals (`2a2_removal.log.txt`).

The director's ruling of 2026-11-03: the pilot's (2b) and §9.12 runs re-check this sha256 before using the file. If the
file has been purged or changed, the pilot STOPS and does not regenerate it. A (2a) rerun is a new connect, sent to the
director first.

## The connect

- **Script:** `connect-2a2.sh`, sha256 `7d8970382a8609b38148dae11c6dfde0975de3006d908da599296194804ee433`, approved before
  it ran; the copy on login02 had the same digest.
- **Changes from the first run's `connect-2a.sh`** (`b8c7656f…`), checked by diff:
  - a 3-line header;
  - M = M_A1 = `c30f9ae216c1273a6c91cdfe3a9d13ddc8925c89`;
  - the writer blob check, `2402ed4b` replaced by `bb3892e5`;
  - the work directory, `/dev/shm/josephrb-cov2d-2a2`.
- **Unchanged:** the embedded harness `control2a_split.py` (`841ff1f6…`) is byte-identical, and so are the design and
  the verdict rules (`CONTROL2A-REPORT.md`).
- **Before the sha went to the director**, checked at M_A1:
  - c30f9ae2 is on main;
  - re2_driver `97f26a1d`, cov2d `7dafdd3f`, cov2d_receipt `d5718bf4` and fd_1b_null `1810161d` are unchanged;
  - the harness's import `control1_content_check.py` is `dfac9ecc`, the same as at `c96c97f3`.

## A full-size local dry run first

`2a2_fullsize_dryrun.py`, output `2a2_fullsize_dryrun.txt`. This was the lesson of the first run: the chain had been
tested only at fixture size.
- **Setup:** code exported from c30f9ae2 (writer blob `bb3892e5` confirmed), and a synthetic $CV of 4,119,797 rows built
  by `test_cov2d_writer.write_cv`, including a -0.0.
- **Run:** the three harness steps in one local interpreter with ROOT 6.28/12 and uproot 5.6.9, with O_NOATIME set to 0
  (macOS).
- **Result:** EQUAL ×3 over 4,119,797 rows, `WRITER-CONTROL PASS failures=0`, `CHECK rc=0 stub_calls=1`.
- **Not covered:** the cluster's split across envs, the real $CV and O_NOATIME.

## The run (`2a2_connect.log.txt`)

login02, 2026-11-04T04:06:33Z to 04:07:17Z, 0 node-h, no job. Every step ran under nice 19 and `taskset -c 8-11`, with
OMP, OPENBLAS, MKL and NUMEXPR threads at 1.

- **The checkout:** a fresh clone at M_A1; porcelain 0 before and after; 5 of 5 bound blobs before and after, writer
  `bb3892e5` (`2a2_bound.blobs.{before,after}.txt`).
  - REACH PASS: `def write_data_file` at `:60`, one reference, the Load at `:100` in writer_control. cov2d.py and
    control1 have none.
- **Step 1, read** (omnifold_py310: 3.10.19, numpy 2.2.6, uproot 5.6.9):
  - 4,119,797 rows, dataPOTUsed 1.057394261158926e+21;
  - $CV's atime_ns was 1792770770214610703 before and after;
  - npz `6e19e645…`, manifest `578c3e95…`, both **identical to the first run's**.
- **Step 2, write** (root_6_28, ROOT 6.28/12):
  - both expected digests were logged first and matched;
  - every array was equal to step 1's in dtype, shape and bytes;
  - the output sha256 was `7eb39088…`.
- **Step 3, check:**
  - the expected sha256 was logged first; the stub was called once, with that file and digest;
  - compare_tree: all three branches EQUAL over 4,119,797 rows, bitwise_diff 0 and value_diff 0. The per-branch digests
    match the first run's (`d66df76a…`, `21fa0375…`, `f8c5755a…`);
  - no unexpected keys;
  - `WRITER-CONTROL PASS failures=0`, `CHECK rc=0 stub_calls=1`.
- **Verdict:** CONTROL-2A PASS.

## Removals

- **By the script, 04:07:16Z**, each with its sha256 and rc 0:
  - `cv_data.npz` (`6e19e645…`);
  - `cv_data.json` (`578c3e95…`);
  - the /dev/shm `writer_control.root` (`7eb39088…`), after the copy to pscratch;
  - the clone (1.2G).
- **By me, 04:10:17Z** (`2a2_removal.log.txt`), after fetching the logs, whose sha256s match the node's
  (`2a2_node_listing.txt`):
  - `/dev/shm/josephrb-cov2d-2a2` (40K), rc 0;
  - `/dev/shm/josephrb-cov2d-2a2.sh` (`7d897038…`, checked first), rc 0;
  - /dev/shm then holds no file of mine.
- **No process remains** (`2a2_ps_after.txt`). The listing's `pgrep -f` printed "STILL_RUNNING", but that was the check
  matching its own command line; `ps -u josephrb` shows only systemd, sd-pam and the check itself.

## Files

| file | what |
|---|---|
| `connect-2a2.sh` | the connect as run |
| `2a2_fullsize_dryrun.py`, `2a2_fullsize_dryrun.txt` | the local full-size dry run and its output |
| `2a2_connect.log.txt`, `2a2_step{1,2,3}.log.txt`, `2a2_bound.blobs.{before,after}.txt` | the node's logs |
| `2a2_node_listing.txt` | the node's listing and sha256s, including the kept file's |
| `2a2_ps_after.txt`, `2a2_removal.log.txt` | the process listing; the removals |
