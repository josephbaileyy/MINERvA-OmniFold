# R10 ledger notes (2026-10-24)

**By** the validation lane, under [`BINDING.md`](BINDING.md). The charges are in [`LEDGER.tsv`](LEDGER.tsv). Times are
PDT, from `sacct` and the receipts under `/pscratch/sd/j/josephrb/r10-20261024/`.

**CITABLE FOR:** what each job ran, its controls, and X's projection, fixed before X was submitted.
**NOT CITABLE FOR:** any R10 result.

## Step 0: controls-only (local, 0 node-h)
- **Run:** `r10.py --controls-only` at the bound commit `b4b1136c`, from a clean detached worktree, with 2 BLAS
  threads. The events were copied read-only and their sha256 is `07fccc1a…`, equal to the pin.
- **Result:** K0, K1 and K2 all pass.
  - K1: D-ID's committed `tables.npz` widths at T1 and T2 (183 functionals) and the K = 5 trajectory row for all six
    weight sets are reproduced bitwise, and the six J medians match exactly.
  - K2: the generic path equals D-ID at f = 1, bitwise, split widths included.
- **Resources:** 126 s wall (`timing.wall_s` in [`receipts/controls-only-b4b1136c.json`](receipts/controls-only-b4b1136c.json);
  127 s by the shell's timer), 130 CPU-s, peak RSS 4.48 GB.
- No R10 readout was kept.

## X0 (60195994, debug): playlist 1L
- **Run:** 00:11:43–00:14:11, ElapsedRaw 148 s, 0.0411 CPU node-h. Every sacct row is COMPLETED 0:0.
- **The guard:** all four modules it lists were loaded from the deploy.
- **Admission, 1L:**
  - 383,848 rows; identity and truth equal to S1; truth bitwise equal to MCgen;
  - the manifest equals S1's record;
  - `pass_reco` is a subset of G2's selection (1,102 rows pass G2 only);
  - G2's reco values equal `MCreco` bitwise on `pass_reco` rows.
- **Join:** 231,021 of 231,021 rows joined, from 6 files and 1,056,661 reco entries. No duplicate keys; the maximum
  vertex difference is 0.0 mm.
- **An observation, not a defect in any result:** the extraction step ran with `cpu=1` (sacct `AllocTRES` for step
  `.0`), so the 64-process pool shared one core. X uses the same launcher, so X0's rates apply to X unchanged.

## X's projection (DECLARATION section 7), fixed before X is submitted

From X0's receipt and sacct:

| term | X0 | scaling | X |
|---|---:|---|---:|
| job overhead (ElapsedRaw − python wall) | 83.7 s | fixed | 83.7 s |
| hashing | 20.9 s for 3.04 GB | × 128.75 GB / 3.04 GB | 886.8 s |
| loading | 5.2 s | fixed | 5.2 s |
| playlists | 32.7 s for 383,848 rows | × 32,849,103 / 383,848 | 2,799.4 s |
| output and finish | 5.4 s | fixed (every row is always written) | 5.4 s |
| **projection** | | | **3,781 s = 63.0 min** |

- **Limit:** 1.25 × 63.0 min, rounded up: **1:19:00**.
- **Worst-case charge:** 1.317 CPU node-h. With X0, that totals ≤ 1.36, inside the 4 granted and the declared worst
  case of 2.33.
- **Cross-check:** MP-2 S1's whole pass took 0.102 CPU node-h with its parallel steps. X is slower because its step
  holds one CPU.

## X (60196485, regular): FAILED closed on playlist 1E (exit 7)
<!-- absence-ok: records that failed job 60196485 wrote no output file in its own run directory; not a claim that a result is absent from the repository -->
- **Run:** 00:24:29–00:46:29, ElapsedRaw 1,320 s, 0.3667 CPU node-h. The step exited 7, which is `r10_extract.py`'s
  admission/control failure. Nothing was written: the job left no `r10_extra.npz` in
  `run/extract/`.
- **1A–1D:** every admission and join control passed. Rows, reco-passing rows, joins, vertex differences:

  | playlist | rows | reco-passing | joined | max vertex difference |
  |---|---:|---:|---:|---:|
  | 1A | 2,682,267 | 1,729,050 | 1,729,050 | 0.0 mm |
  | 1B | 721,082 | 467,021 | 467,021 | 0.0 mm |
  | 1C | 1,376,832 | 890,128 | 890,128 | 0.0 mm |
  | 1D | 4,003,632 | 2,583,713 | 2,583,713 | 0.0 mm |

- **1E:** every admission passed (3,350,021 rows; 2,156,139 reco-passing), and all of them joined. **The join control
  failed**:
  - 111 surplus reco-tree entries repeat another entry's identity within the same file (the receipt's
    `duplicate_keys_within_file_all`), all in one file (`MasterAnaDev_mc_AnaTuple_run00111353`,
    manifest index 28);
  - exactly 1 of the rows to join has such an identity (S1 row 1,418,107 of 1E).
- **Diagnosis** (read-only, login node, after the failure; no R10 quantity):
  - The two reco entries under that identity (tree entries 180,991 and 181,206) are **different events**. Their branch
    values differ, and their vertices are 1,665 mm apart.
  - Exactly one, entry 180,991, has G2's reco vertex (difference 0.0 mm). The vertex therefore picks the entry
    uniquely.
  - The bound code's sorted lookup had happened to take that entry, so its recorded vertex difference was 0.0. Only
    the duplicate control caught the ambiguity.
  - MP-2 S1 reported 133 duplicated identities in 1E on the Truth side (`S0-S1-REPORT.md:27-28`). This is the reco-side
    counterpart.
- **Rate, for X's projection:** 1A–1E took 1,151 s of playlist time for 12,133,834 rows (95 µs per row, against X0's
  85). Scaled, the full pass is ≈ 55 min, inside the 63 min projected.
- **Status:** a code change after binding is the director's call. The proposed fix and its tests are with the director.
  X is not resubmitted until the director rules.
- **Ruling:** the director accepted the vertex resolution (PR #309, `289a1ff7`), bound it in
  [`BINDING-AMENDMENT-1.md`](BINDING-AMENDMENT-1.md), and directed: re-deploy at `289a1ff7`, re-run controls-only for
  the record, then X once at the bound 1:19:00, then Y at the same commit.

## Step 0 again: controls-only at `289a1ff7` (local, 0 node-h)
- **Run:** `r10.py --controls-only` from a clean detached worktree at `289a1ff7`, with 2 BLAS threads. `r10.py`
  sha256 `e2fedfcf…`, `config.json` `2366c41d…`, both unchanged by the amendment.
- **Result:** K0, K1 and K2 all pass, with the same values as at `b4b1136c`. Every admission check passes.
- **Resources:** 123 s wall, 128 CPU-s, peak RSS 5.06 GB. `r10_results.json` sha256 `741594d7…`.
- No R10 readout was kept.

## X (60200309, regular): the re-run at `289a1ff7`, COMPLETED
- **Deploy:** `/pscratch/sd/j/josephrb/r10-20261024/deploy/289a1ff7`, clean at the pin; `r10_extract.py` sha256
  `3b539d4a…` (the receipt's own record).
- **Run:** submitted 01:07:10, ran 01:09:03–02:03:22. ElapsedRaw 3,259 s, which is 0.862 × the 3,781 s projection,
  inside the bound 1:19:00. Exit 0:0. **Charge 0.9053 CPU node-h**.
- **Admission and join:** all twelve playlists passed every admission control. 32,849,103 rows were covered, and the
  receipt records `complete: true`.
  - Every reco-passing row joined in every playlist, and the maximum vertex difference is 0.0 mm everywhere.
  - **Duplicates:** 111 surplus reco-tree entries repeat another entry's identity within the same file, all in 1E.
    The count is 0 in every other playlist, over the files its rows point to.
  - **Rows resolved by vertex:** 1, the 1E row diagnosed above.
  - **Unresolved:** 0 in every playlist (`duplicated_rows_unresolved_by_vertex`).
- **Guard:** the OI-136 inventory shows one checkout root, the deploy, with 4 modules. Its verdict line reads
  `EMPTY-REPOSITORY-ORIGIN-SET`, as it did for X0 and the first X, because `r10_extract.py` imports no repository
  package.
- **Memory:** the parent's max RSS is 7.70 GB. The step's MaxRSS is 68.5 GB, which includes the 64 workers, on a
  488 GB node.
- **Products** (sha256, identical after copying them locally for Y):

  | file | sha256 |
  |---|---|
  | `run2/extract/r10_extra.npz` (2,365,138,466 bytes) | `923e958a3def73bb44048052cac5ec933ae524b4fb66da052e22aa1fda63ae3d` |
  | `run2/extract/r10_extract_receipt.json` | `3849b14373f9c5abb81593ed8873881c3b8a58b329768370216820c88200dec8` |
  | `run2/inventory/extract-60200309.jsonl` | `001e5669cd6c416ade862999de5414d40d32ac2f83a9991c0fcecce806ce164d` |

- **Running total:** 0.0411 + 0.3667 + 0.9053 = **1.3131 CPU node-h** of the 4 granted.
