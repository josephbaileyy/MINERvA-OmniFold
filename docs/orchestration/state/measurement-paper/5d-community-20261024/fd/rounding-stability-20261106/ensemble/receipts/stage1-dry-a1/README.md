# ENS1 A1 stage-1 dry rerun: the receipt (job 60993979, 2026-11-08)

**Recorded by** the rounding-instability lane (`director-helper-3`). The rerun was made under `ENS1-BINDING-2.md`
(addendum A1) at M_A1 = `f4d2d7f3833834390b7b031df61ba1a5765e9900`, on the director's go on both connects' sha256.
It relaunched the SUBMIT connect unchanged after the fence stop receipted in `../stage1-dry-a1-stop1/`.

**Result: the job COMPLETED, and the POST-RUN connect read PASS.**
- **Products:** all 9 dry tasks ended with rc 0, and every product exists.
- **Gate E5:** every product records 0 moved rows on all four inputs, and so does every task log.
- **The F₆₄ comparison:** `xsec_flat` and `xtrue_flat` are bitwise identical to attempt 1's.
- **The charge:** 0.3036 node-h, so stage 1 has now spent 0.4622 of its 55.0 cap.

**CITABLE FOR:**
- the dry rerun's execution: the connects' checks, A1's preconditions on the npz's own edges, the job and its charge;
- gate E5 at the dry run (0 moved rows ×9);
- the F₆₄ bitwise comparison with attempt 1;
- the timing readout that the director's projection gate (declaration §8) reads.

**NOT CITABLE FOR:**
- any ENS1 reading, any stage-1 gate other than E5 at the dry run, or any product value. The dry products are listed by
  sha256 and stay on pscratch, unread here beyond the post-run's checks.
- the projection verdict. That gate is the director's, and this receipt records only its inputs.

## The SUBMIT connect (`connect/`)

**The scripts and their rcs:**
- `ens1_a1_dry_submit.sh` is the copy the connect wrote, sha256 `48805783…`. It is the same sha as the stop's, unchanged.
- The launcher is `ens1_a1_dry_submit_launch.sh`, `4a7c5875…`.
- The launcher rc and ssh rc were both 0, read unpiped (`launch-submit.out.txt`).

**Waiting for the queue to clear** (`fd1b-clear-poll.txt`): a read-only squeue every 10 minutes, from 07:30:01Z.
- Through 08:10:51Z, the seven `fd1b_pfd_p3` jobs were all still in the queue.
- At 08:20:57Z, three of them remained.
- At 08:31:01Z, the queue held no job at all.
- No job of any other name appeared.

**`connect-a1-dry.log.txt`** (login20, 2026-11-08T08:31:21Z–08:32:21Z, rc 0):
- **The fence:** pass. `squeue-before.txt` is empty.
  - The line reads "0 jobs, all rs1_*": that is the script's wording for an empty queue.
- **iris, the actual reading** (`iris.txt`): m3246 had charged 18,250.4 of its 20,000.0 allocation, so
  `balance_node_h=1749.6`.
  - Half the balance is 874.8, and the combined caps of 109.0 are below it.
  - Attempt 1's connect read 1,764.5. The director quoted 1,757 at 06:14Z.
- **The stat:** 23 files, 0 missing. Each file's mtime and atime are recorded.
- **The deploy:**
  - HEAD is `f4d2d7f3`, with 0 `porcelain --ignored` lines before and after.
  - 12 blobs and 7 sha256s were checked, with 0 mismatches.
  - Binding 2's A1 section names M_A1.
  - origin/main had moved to `646a50df` (the merge of #927). Binding 2 there has sha256 `614afe02…`.
- **j1–j20:** 20 copies made with `dd iflag=noatime`, with 0 problems (`refs-SHA256SUMS`).
- **A1's preconditions** on the npz's own edges: `ens1_a1_pre.py`, sha256 `4064ef02…`, run under the sourced environment
  (Python 3.11.14). The verdict was **PASS** (`a1-preconditions.json`, `aa88ab5b…`), and the npz's atime did not move.

  | axis | d_min outside the zone | farther neighbour, min (own spacings) | non-representable edges |
  |---|---|---|---|
  | pt | 1.04 | 0.56 | 8 |
  | pz | 2.00 | (none) | 0 |
  | eavail | 1.20 | 0.80 | 4 |
  | q3 | 1.20 | 0.60 | 5 |
  | W | 1.20 | 0.60 | 4 |

  - All three preconditions hold:
    - P1: every d_min is greater than 1 + 2⁻²⁰;
    - P2: every farther neighbour is more than ½ + 2⁻²⁰ of its own spacing from its edge;
    - P3: no non-representable edge has a power-of-two neighbour.
  - The edge counts, non-representable counts and d_min match A1 §3's tables.
- **The environment:** python 3.11.14, lightgbm 4.6.0, scipy 1.16.3, numpy 1.26.4.
- **The stage-1 queue:**
  - `dry.tsv` is `83ae2e8c…` with 9 tasks. It is copied here as `dry.tsv`.
  - shard0–5 have 168/168/167/167/167/167 tasks.
  - All seven files match `queue-sha256.expected`.
- **The submission:**
  - sbatch rc 0, job 60993979.
  - The parsed `TimeLimit` was 00:45:00, as declared.

## The job (`log-dry/`, `connect/job-poll.txt`)

- **`sacct`** (`../post/sacct-60993979.txt`): COMPLETED 0:0 on 1 node, nid004549, from 08:32:43Z to 08:50:56Z.
  ElapsedRaw was 1,093 s, so the charge is **0.3036 node-h**.
- **`log-dry/DONE`:**
  - mode dry, stage 1, 9 tasks, 9 ended, rc 0;
  - job 60993979, pin `f4d2d7f3…`, teardown "".
  - There is no FAILED, `.failed` or `.teardown`.
- **Lanes:** the job ran 8 lanes (`ens1_a1_dry_60993979.out.txt`).
  - Eight tasks started together at 08:33:26Z.
  - `ens1_s01_k004` started at 08:41:18Z, when the first of them (`ens1_s00_k004`) ended. It ended at 08:50:54Z.
- **Environment warnings:** `log-dry/env.log.txt` shows the same two missing `setup.sh` warnings as attempt 1's.
- **Products:** the nine are pinned in `log-dry/SHA256SUMS`.

| task | product (under `runs/`) | sha256 |
|---|---|---|
| ens1_F64 | `F64/ens1_F64_b-_j0.npz` | `a52aab45a6cf62ca94337297d20ae7812cdbb5465ba9af52ecbcdf9cf7bdf4c0` |
| ens1_s00_k001 | `stability/ens1_k001_b-_j0.npz` | `a0c375eabf7ed518a2617b8c6e763c0e6e80bac9976d02a2f55115303d02079f` |
| ens1_s00_k002 | `stability/ens1_k002_b-_j0.npz` | `fcaf6ba9d3bbba3d6f840a6c600eb863ee178c9ab63ffe4bdc466bcaaeb95299` |
| ens1_s00_k003 | `stability/ens1_k003_b-_j0.npz` | `bd5585b93561f9899fbca1105c4c582d2a184802ef2f5cf6bd0f3a4857bd3e65` |
| ens1_s00_k004 | `stability/ens1_k004_b-_j0.npz` | `401086690037dafa370fbe48aa6d9bd536c3d875e70b98e3d54a47443f4dde43` |
| ens1_s01_k001 | `stability/ens1_k001_b-_j1.npz` | `0c75db5b10fc1eb1c9af12a01620c8660f9e899dd808ad7a4b5d9b5fc54dce1d` |
| ens1_s01_k002 | `stability/ens1_k002_b-_j1.npz` | `b027ce42c3a1e8855c976ba805c466ff6d10d87e678314f7a833bfa6f3e17111` |
| ens1_s01_k003 | `stability/ens1_k003_b-_j1.npz` | `1e835499a7b3e333618816c3fe13497ff89af0aebf1bc3d5e3389f6c4d5710fb` |
| ens1_s01_k004 | `stability/ens1_k004_b-_j1.npz` | `0ade03b14e3826ec9db9e0cf1988789c7ba7963d6334d5ec080c80689357d72d` |

The products stay at `/pscratch/sd/j/josephrb/ens1-a1-20261108/runs/`. None is committed.

## The POST-RUN connect (`post/`)

**The scripts and their rcs:**
- `ens1_a1_dry_postrun.sh` is the copy the connect wrote, sha256 `90af5e54…`.
- The launcher is `ens1_a1_dry_postrun_launch.sh`, `2e759784…`.
- The launcher rc and ssh rc were both 0 (`launch-postrun.out.txt`).
- `connect-postrun.log.txt` ran on login06, 2026-11-08T08:51:36Z–08:52:02Z, rc 0.

**The checks:**
- **The fence:** pass, and the job was out of the queue.
- **sacct:** COMPLETED on 1 node. The charge is 0.1586 + 0.3036 = 0.4622 node-h, within the 55.0 cap.
- **DONE:** as above. The deploy is unmodified, and the probe is at sha256 `807c40d3…`.
- **The products:** all 9 paths came from the bound probe's `expect` (`expect-*.txt`, `products.txt`), and each is in
  `SHA256SUMS`.
- **`read.py`** (sha256 `59f861de…`), run under the sourced environment, wrote `a1-dry-read.json` (sha256
  `11663f0c…`) with the verdict **PASS** and no failures:
  - **E5 in the products:** each product's meta `ens1` block has
    `moved_rows == {MCgen: 0, MCreco: 0, measured: 0, bkg_reco: 0}`, ×9.
    - Each block's mode, k and protocol seed match its task.
    - Each block's `code_sha256` is the probe's `807c40d3…`.
  - **E5 in the logs:** each task log has exactly one `[ens1] grid membership moved rows {…}` line, all zero, ×9.
  - **The F₆₄ comparison:** see below.

**F₆₄ against attempt 1 (the director's ruling 3, the exception to A1 §7):**
- Attempt 1's root, `/pscratch/sd/j/josephrb/ens1-20261107`, is kept intact as evidence. Only its
  `runs/F64/ens1_F64_b-_j0.npz` was opened.
  - It was opened through one `dd iflag=noatime` copy, into `post/attempt1/` on pscratch (not committed).
  - The copy has the pinned sha256 `94ef51532161aa578f2c0944658d2172fda9c1c118ea81ffa2415cc74a5808e7`.
  - The source's atime is unchanged (1794100660 → 1794100660).
  - Attempt 1's other four products stay unopened.
- **The arrays:** `xsec_flat` and `xtrue_flat` are float64, shape (65856,), on both sides, and **bitwise identical**.
- **The keys:** both files carry the same set: `meta`, `shape`, `xsec_flat`, `xtrue_flat`.
- **The file digests differ** (`a52aab45…` against `94ef5153…`, 184,487 against 184,442 bytes). The comparison is on the
  two arrays, as bound. The other two keys, `meta` (a JSON string) and `shape`, were not compared.

**The timing readout** for the director's projection gate. Declaration §8 requires 42 × t + 300 s ≤ 8.1 h, which means
t ≤ 687 s.

| task | seconds_unfold | task wall (s, `.start` to `.end`) |
|---|---|---|
| ens1_F64 | 508.025 | 533.6 |
| ens1_s00_k001 | 493.519 | 518.9 |
| ens1_s00_k002 | 485.678 | 510.6 |
| ens1_s00_k003 | 535.880 | 560.9 |
| ens1_s00_k004 | 443.124 | 470.1 |
| ens1_s01_k001 | 509.884 | 535.0 |
| ens1_s01_k002 | 461.693 | 486.3 |
| ens1_s01_k003 | 460.693 | 484.9 |
| ens1_s01_k004 | **537.935** | **575.6** |

- **Maximum seconds_unfold: 537.935 s.** The projected shard wall is 42 × 537.935 + 300 s = 6.359 h.
- **Maximum task wall: 575.6 s.** The same projection with the wall in place of t gives 6.799 h.
- The verdict on these inputs is the director's.

## The ledger and renames

**The ledger:** `fd/LEDGER.tsv` has three rows for this rerun: the SUBMIT connect, the job and the POST-RUN connect.

**Renames:** git ignores `*.log` and `*.out`, so those files carry a `.txt` suffix here. Their contents are unchanged.

**Empty files:** `connect/clone.log.txt`, `connect/squeue-before.txt` and `post/squeue-before.txt` are empty, as they
were on pscratch.
