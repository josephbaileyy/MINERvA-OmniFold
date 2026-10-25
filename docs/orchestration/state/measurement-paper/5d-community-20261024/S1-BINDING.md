# Binding: S1, configuration (e)'s 5D covariance on the 16 H2 cells, and the HPSS copy of its inputs (2026-10-24)

**By** the paper-tighten lane, as director.

**Under:** Joseph's approval in `DECISION-20261024-joseph-approve-integration-wording-s1-compute-preserve.md`, items 2
and 3, and the route in `DECISION-20261024-joseph-5d-community-standard-route.md`.

**Binds** [`S1-DECLARATION.md`](S1-DECLARATION.md), merged in PR #339 (`c840c7bc`). The file's sha256 begins
`f1c7288c7f274043`, and it is unchanged at `d5617470`.

**MEASURES:** nothing. It authorizes the declared jobs, the assembly, and one HPSS copy.

**CANNOT AUTHORIZE:**
- a claim, or any printed wording;
- a change to a declared choice, gate or cap;
- GPU use, or premium QOS;
- any write to CFS.

## 1. The bound code

**The deploy pin** is `d5617470a7d08215e1da5622722d348da6a148d1`, main after PR #340. At it, the director checked that
every §6 digest of the declaration matches:
- `s1_assemble.py` `5ebe1a8a…`;
- `s1_controls.py` `bfc8986e…`;
- `test_s1_assemble.py` `a4bb6982…`;
- the three task tables, `6db31a34…`, `bb32d918…` and `4425a91e…`;
- `h2_definition.json` `b6790761…`.

At the same pin:
- `sbatch_timing_packed.sh` has sha256 `b72aaa62…`, and `nd-unfolding/s5c_array.sh` is present;
- `python3 -m unittest test_s1_assemble test_s5p_assemble` runs 20 tests, all passing.

**The C_model input,** the declaration's one `<…>` field:
- `--cmodel-sha256 3008d8f6b1f295cdd648f14e1ab2c20d864ce054a19f97e90e1620d22484e882`;
- this is the file `/pscratch/sd/j/josephrb/cmodel5d-20261024/out/cmodel_5d.npz`, as recorded in
  `state/measurement-scoping/pv-ladder/BUILD-REPORT.md:94` (PR #340);
- its `C_abs` matrix bytes hash to `3f489428…` (`:96`).

The build it comes from ran under `BUILD-BINDING.md` and was reported. So the declaration's condition that "the
assembly does not run before that build has run and been reported" is met.

## 2. The S1 compute

**The cap is 15.5 CPU node-h; 11.2–12.3 is expected.** The jobs are the four declared in §3, exactly:

| job | cap, CPU node-h |
|---|---|
| pilot | 0.5 |
| P1 | 5.25 |
| P2 | 5.25 |
| seed | 4.5 |

- **Conditions on every job:** regular QOS, CPU, account m3246, exclusive and `--no-requeue`. Each is under 12 h.
- **Deploy.** Clone the pin into `$B/deploy/d5617470`, with `B=/pscratch/sd/j/josephrb/s1-20261024`. Check HEAD and a
  clean tree, log both, and rerun the tests in the deploy before G1.

**Conditions, in the declared order:**
1. **G1 and G2** run on a login node before the pilot. Either one's FAIL stops everything.
2. **The pilot,** then G3 and G4 on its products.
   - If any pilot product's `seconds_load + seconds_unfold` exceeds 1,500 s, P1, P2 and the seed job come back to the
     director for re-pricing before submission (declaration §3, rule 2).
3. **P1, P2 and the seed job** may then run concurrently. After them come G3 on all 175 universes and G5 on the four
   seeds.
4. **The assembly and readout** run on a login node, with the §3.1 argv and the C_model digest above.
5. **Stops.** Any FAIL, any non-COMPLETED state, any non-zero exit, or any job past 1.25 × its projected wall stops the
   run and is reported unrepaired. Nothing is resubmitted without the director.
6. **Ledger** every job from `sacct` in `s1/LEDGER.tsv`.
7. **Products** go to HPSS after G3 and G5, as declared (§3 item 6), with `hsi hashcreate`, `hashverify` and a
   retrieval check.
8. **No values** are printed by any gate except G1's simulation-only deviations. The readout JSON is committed with the
   npz's sha256. No cross-section value is quoted in the report beyond that readout.

## 3. The HPSS copy of the bank and the detector dump (0 node-h)

**What is copied.** [`s1/PRESERVE-INVENTORY.sha256`](s1/PRESERVE-INVENTORY.sha256), sha256 begins `cde96ca78f732c0a`:
- 734 files:
  - the 701 files of `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware/`, including
    `cv.npz` `072643e1…`;
  - the 33 files of `/pscratch/sd/j/josephrb/s5p-20260926/bank_detector/`, including `detector-dump.json`
    `c52dca58…`.
- Each line is copied verbatim from the sf1 manifest
  (`state/2d-closeout/stageF/methods/sf1/manifest/inputs-sha256.txt`), selected by those two directory prefixes.

**The director's read-only check on login12, 2026-10-24:**
- the directories hold exactly 701 and 33 regular files, with no subdirectories and no symlinks;
- they total 71,581,990,858 B and 2,126,459,206 B, about 73.7 GB;
- the oldest access time is 2026-10-19;
- `hpssquota` read 353.98 of 512.00 GiB used, so about 158 GiB is free; after the copy about 89 GiB will remain;
- pscratch read 16.99 of 20.00 TiB used.

**What runs.** The committed Stage 0 preserve script, unchanged:
`state/measurement-paper/5d-design-20261023/stage0/stage0_preserve.sh`, sha256 `27ccc04a8c14d640…`. Its PASS record
is `STAGE0-PRESERVE-REPORT.md`. Run it from the deploy:

```bash
bash $D/docs/orchestration/state/measurement-paper/5d-design-20261023/stage0/stage0_preserve.sh \
  $D/docs/orchestration/state/measurement-paper/5d-community-20261024/s1/PRESERVE-INVENTORY.sha256 \
  $B/preserve /home/j/josephrb/mnv-5d-s1-inputs-20261024
```

**Conditions:**
1. **Space.** Before starting, `hpssquota` must show at least 80 GiB free. pscratch must have room for two copies of
   the tar, about 150 GB, because the retrieval lands beside the original.
2. **Where it runs.** On a login node, detached (`setsid nohup … &`) so that a dropped ssh does not kill it, with no
   Slurm job.
3. **Order.** It may run before or alongside the S1 jobs, since both only read the inventoried files. It must not run
   while any inventoried file is being written.
4. **Names.** The script names its tar `stage0-inputs.tar`. The HPSS directory name identifies this copy. The report
   states the name mismatch.
5. **Stops.** Any exit from 3 to 8 is a STOP, reported unrepaired.
6. **Cleanup after PASS.** Delete `$B/preserve/stage0-inputs.tar`. Keep its `.sha256`, `paths.list` and
   `preserve.log`. The inventoried files are not touched.

## 4. Reports

- **`S1-PRESERVE-REPORT.md`** carries:
  - the tar's sha256 and bytes;
  - `hsi ls -l`, and the hashverify and retrieval lines;
  - `hpssquota` before and after;
  - receipts in `s1/receipts-P/`.
- **`S1-REPORT.md`** carries:
  - the deploy log;
  - every gate's output;
  - the ledger with node-h against each cap;
  - the product digests;
  - the readout JSON's per-cell relative σ by component, trace shares, eigenvalue extremes and rank;
  - the HPSS copy of the products;
  - the labels, verbatim.

  It makes no claim and draws no conclusion about publishability. Open a PR to the director.

The jobs and the copy may start once this record is on `main`.
