# V_F Phase 1 run receipt (2026-11-26)

**Under** FD-VF BINDING 1 (#1352, merge `ac9edf46c07953f6d26c4d4eb6992e651bf5bb1c`): the code merged in #1345
(`c0fa0d01`, `fd_vf_addition.py` sha256 `3ba320bd…`), amendments A1–A3, `connect-vf-p1.sh` (`9cda83f0…`) and
`stage-vfp1.sh` (`f05a3e85…`), merged in #1350. The run directory is `/pscratch/sd/j/josephrb/vf-20261125-p1`, on
login02, at 0 node-h.

## Fences and checks

- **Acks** (each pasted from the peer's `date -u`): cov2d at 00:10:33Z, director-helper-3 at 00:10:36Z, and
  limitation-resolver at 00:12:32Z.
- **Window:** it ended at 00:25:33Z, the oldest ack plus 900 s, computed by command.
- **Before the start:** limitation-resolver was told at 00:12:44Z.
- **Cert:** `TZ=UTC ssh-keygen -L` gave "valid to 2026-11-26T15:19:52". It was checked before the start (907 min
  left), before each of the 8 polls, and before the finish.
- **Stager:** the local `stage-vfp1.sh` was `f05a3e85…` before each ssh.

## The run

| step | UTC | result |
|---|---|---|
| start (`bash -s -- start`) | 00:12:58 | node copy sha256 `9cda83f0…`, "worker start 742359" |
| deploy | | "deploy ok at c0fa0d01…: 22 blobs"; env "3.11.14 1.26.4 3.10.8" |
| tests (A3 selection) | to 00:26:15 | `tests rc=0 PASS`, a closing block of "Ran 541 tests … OK" |
| chain | 00:26:15–00:36:58 | rc 0, "[chain] done: 161 records in …/run/chain.json" |
| receipts | | `run.sha256`: 214 files, sha256 `86d59c3c3711c44fcdd355fa4a98b59e1bd7fd65c507cd88882604ff8caa0f71` |
| deploy porcelain afterwards | | "porcelain after: empty" |
| finish (`bash -s -- finish`) | 00:38:15 | "worker exit=0"; `receipts/vfp1.log` sha256 `81dfbaab0e5b3a47c48aa6f2f414febb5947477cb37f10dce18b5dd5ee981de2`; removed only `/dev/shm/vfp1.sh` and `/dev/shm/vfp1.log` |

**EVW5D:** `grep -rlE "of_inputs_5d|bkg_dump|data_b-_j-"` over `logs/`, `run/logs/` and `receipts/` matched 0 files.

## What is here

- **`run/run/`, `run/receipts/`, `run/logs/`:** the run directory's `run/` (without `tmp/` and `mpl/`), `receipts/`
  and `logs/`, fetched with rsync. In `run/run/`, `shasum -a 256 -c ../receipts/run.sha256` gives all 214 OK.
- **`run/run/vf/block/`:** the chain's rebuild of the block. It is byte-identical to the committed
  `fd/with-vf/block/`, and the chain required that.
- **The experiment tables** (`S/*/fd_f0*_experiments.npz`, `fd_f1_experiments.npz`): there are two distinct contents,
  `7384c651…` (F0 and F0b) and `997c7dae…` (F1). Every arm, OLD and V_F, wrote the same bytes, and the chain required
  that (`check_table`).

**The V_F outputs** were copied from `run/run/` into `fd/with-vf/`:
- `readout/vf-f0`, `vf-with-S`, `vf-with-E`, `vf-nopl-S`, `vf-nopl-E`;
- `data-product/` and `deposit-candidate/` from `vf/`;
- `figures/` from `E/vf-with/figures`;
- `table/`.

**Companions added after the fetch, not in `run.sha256`:** each of the six `fd_g_followup_readout.json` (four in
`run/run/E/*/readout/`, two in `fd/with-vf/readout/vf-*-E/`) has an `fd_g_followup_readout/` directory beside it.
Each directory holds 20 relative symlinks to S1's tracked `data_b<b>_j<100+b>.npz` and a README, as the with-block
companion does. The links are where item 5's key-name matches resolve. The run read none of them.

The readings come separately, to the director first. Nothing goes to the note before the director has reviewed them.
