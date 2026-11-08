# RS1 dry run: the receipt (job 60970044, 2026-11-07)

**Recorded by** the rounding-instability lane (`director-helper-3`). The run was made under `RS1-BINDING-2.md`
(rulings 2 and 4) at M = `e306087e68fd497541d32b440848a40f7f29611e`, after the director's go on the connect script's
sha256. **No RS1 product has been read**, and no gate or reading has been evaluated. The audit reads the
tie-invariance property next (binding 2, ruling 2).

**CITABLE FOR:**
- the dry run's execution: the connect's checks, the job's state, charge, task walls and product digests;
- the full-run projection under `RS1-DECLARATION.md` §7 item 2.

**NOT CITABLE FOR:**
- any gate (G1, G2, G4), any reading (K1–K6) or R0. This receipt evaluates none of them;
  <!-- absence-ok: scopes what this receipt records, not a claim that a result is absent from the repository -->
- tie invariance through real LightGBM. coverage-5b-audit reads that from the products named below.

## The connect (`connect/`)

- **The scripts:**
  - `rs1_dry_submit.sh`, sha256 `3f84decba23305f0e87a748610ea7e9d034a7405f619276dd5edbcffc9f4a2f9`, the copy the job
    wrote to `$OUT/logs/`. It is byte-identical to the one sent to the director;
  - `rs1_dry_launch.sh`, sha256 `7b49cdbb3a769f9ab153c808394f63a31608930ebca2691e69dd3f9875c57c5b`.
- **`launch-dry.out.txt`:** ssh rc 0, read unpiped.
- **`connect-dry.log.txt`:** login14, 2026-11-07T17:52:18Z–17:53:09Z, rc 0 (`connect-dry.done`). In order:
  - **the COV2D fence:** no cov2d-* job queued or running. `squeue-before.txt` is empty: josephrb had no job at all;
  - **iris:** m3246 has 1,774.4 node-h remaining, half is 887.2, against a price of 8.0 (`iris.txt`);
  - **stat:** both inputs and the 21 G1 references are present. The atimes are those printed before any copy;
  - **the deploy:** a fresh clone at M, clean; 6 of 6 blobs match; the declaration (`dbfb0c94…`), binding 1
    (`947fd275…`) and FD-STAB's `SHA256SUMS` (`e2c35e55…`) as sent;
  - **the G1 references:** 21 copied with `dd iflag=noatime`, no original's atime moved, all 21 at their pins
    (`refs-SHA256SUMS`, the copies in `$OUT/refs`);
  - **the environment:** python 3.11.14, lightgbm 4.6.0, scipy 1.16.3, numpy 1.26.4;
  - **the queue:** 66 tasks, 229 unfolds, 9 dry. `queue.tsv` is `58c213a2…` and `dry.tsv` is `5579ea8c…`, both equal
    to the digests sent (both files are committed here);
  - **the submission:** sbatch rc 0, job 60970044; scontrol shows `TimeLimit=00:45:00`; the deploy was still clean
    after submission.

## The job (`log-dry/`, `sacct-60970044.txt`)

- **`sacct`:** COMPLETED 0:0, 1 node (nid005821), ElapsedRaw 944 s, so the **charge is 0.2622 node-h**.
- **`DONE`:** `{"mode": "dry", "tasks": 9, "ended": 9, "rc": 0, "job": "60970044", "pin": "e306087e…"}`. There is no
  `FAILED`.
- **The task walls** (`<id>.start` and `<id>.end`, in seconds):

  | task | wall |
  |---|---|
  | A0 `-:-` | 524.7 |
  | A0 `-:0` | 489.5 |
  | A0 `-:1` | 463.4 |
  | V `-:1` | 554.3 |
  | B1023 `-:0` | 463.0 |
  | B63 `-:0` | 438.8 |
  | S_ref `-:1` | 458.2 |
  | S_all `-:1` | 495.7 |
  | P1 `-:0` | 477.8 |

  The peak RSS is 12.9–18.3 GB per task (`tasks/*.time`).
- **`SHA256SUMS`:** 9 products and 9 trace sidecars, written by the job.
  - **The products the tie-invariance reading compares** are under `/pscratch/sd/j/josephrb/rs1-20261106/`:
    - V jitter 1, `runs/V/rs1_V_b-_j1.npz` (`d0c07829…`);
    - A0's float64 seed-0 base, `runs/A0/rs1_A0_b-_j0.npz` (`73ed3bd0…`).
  - Their npz digests differ by construction, because the meta carries the arm and the seed. The property is about
    `xsec_flat` and the split tables in the trace sidecars.
- **`env.log.txt`:** `setup_salloc_env.sh` reports two missing build setups in the fresh clone
  (`unbinned_unfolding/build`, `MINERvA101/opt`), as in FD-STAB's deploy. Neither is used by this path; lightgbm and
  numpy loaded.

## The projection (`project_full.py`, `projection.out.txt`)

**The rule** (`RS1-DECLARATION.md` §7 item 2): the full run starts only if the projected wall, from the dry run's
per-kind times packed on 8 lanes, is at most the smaller of 7.25 h and 0.9 × (8.0 − the dry charge). With the charge
of 0.2622 node-h that limit is 6.964 h.

**The method:**
- each arm's per-unfold time is its dry task's wall. Those one-unfold tasks include an input load, so the times are
  conservative for tasks of 4;
- an arm absent from the dry run takes its family's largest time: S_omni takes the S arms', P2 takes P1's;
  <!-- absence-ok: a parameter of this projection's own method, not a claim that a result is absent from the repository -->
- failing a family, an arm takes the largest time overall, 554.3 s. These are the F axis arms;
- the 57 remaining tasks (220 unfolds) are packed in queue order onto the lane that frees first, plus 120 s of setup.

**The result:** a **projected full wall of 4.08 h**, so the full run may start under the rule. It also needs
coverage-5b-audit's tie-invariance reading and the director's go (binding 2, ruling 2).

**Charge so far:** 0.2622 of the 8.0 node-h cap.

**Renames:** git ignores `*.log` and `*.out`, so those files carry a `.txt` suffix here. Their contents are unchanged.
