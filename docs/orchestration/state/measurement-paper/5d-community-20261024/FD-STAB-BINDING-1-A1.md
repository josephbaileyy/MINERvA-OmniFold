# BINDING 1, addendum A1: the B4 probe's NuWro closure reads its pvl-ratio/1 truth, with a gated truth control (director, 2026-11-04)

**Binds** [`FD-STAB-ADDENDUM-A1.md`](FD-STAB-ADDENDUM-A1.md), sha256
`277f6c799aca808315ce519f427007b7dec5da0c514dc5d0c229841ec01e23b2`, as merged in PR #750 at
**M_A1 = `cc54d86f7ac66c1346fa69e5894b2d2f000fb09c`** (PR head `194a3400`).

**Under** [`FD-STAB-BINDING-1.md`](FD-STAB-BINDING-1.md) (step one, at `dd47f98e`).

**The code, by blob at M_A1:**

| file | blob |
|---|---|
| `nd-unfolding/estimator_stability_probe.py` | `25179f9f` |
| `nd-unfolding/sbatch_fd_stab.sh` | `9defbb44` |
| `nd-unfolding/estimator_stability_analyze.py` | `0e471890` |
| `nd-unfolding/tests/test_estimator_stability_probe.py` | `22e211a2` |
| `nd-unfolding/tests/estimator_stability_mutation.py` | `9ab35c98` |

## What led to it

**The DTN pins check under step one failed on the §11.1 schema clause** (`pins-check.json` `031e6d55…`, a final
STOP). Every byte matched its pin, but `prep/ratios/L-5D-PV/nuwro.json` is schema `pvl-ratio/1`, which the bound
probe's `SCHEMA_TRUTH` lacked. So every candidate's `closure_nuwro` task would have exited 2 in the full run.

## What the director checked

- **The digest.** The addendum's sha256 at M_A1 is the one above.
- **The audit** (`coverage-5b-audit`, #750 comments) of `337fd783`, then of the N1/N2 delta at `194a3400`:
  - nothing blocking;
  - `C2` was verified against the real F0b writer;
  - the STOP path is reachable;
  - there is no bypass of `pvl_truth`;
  - the timing reproduces.

  Two residual notes, neither blocking:
  - numpy integer leaves in the record whitelist would crash the control (rc ≠ 0, a STOP) rather than leak;
  - a number inside a string is not caught.
- **The harness:** 92 of 92 mutations killed (limitations-catalog). Tests: 114.

## Rulings

1. **A1 is bound at M_A1:**
   - `SCHEMA_TRUTH["pvl-ratio/1"]` maps to `pvl_lib.row_weight`, imported unchanged, refusing an off-grid ratio or an
     amplitude other than 1;
   - the analysis requires kind `pvl_ratio` for the SCHEMA closure;
   - `closure_nuwro` is added to `DRY_TASKS` (9 tasks);
   - the dry run takes the pinned F0b product as its sixth argument.
2. **The truth control gates the dry run:**
   - **C1:** the per-row weight equals `pvl_lib.row_weight`, bitwise;
   - **C2:** F0b row 3's `x_true` is reproduced to 1e-12 relative per cell, printing relative differences only;
   - **C3:** descriptive.

   C1 or C2 failing is a STOP that comes to the director unrepaired. It does not change what the probe measures.
3. **The dry run's limit stays at `--time=0:45`.** The worst simulated case is 0.51 node-h. The 8.0 node-h cap and
   the coded cumulative gate are unchanged.
4. **New connects at M_A1:**
   - a new DTN pins check, adding the F0b product's pin;
   - a new dry-run submit gated on that record;
   - each sha256 sent to the director, waiting for the go.

   The cluster lane stays `limitation-resolver`. The step-one record `031e6d55…` is not reused.
5. **Step two** (the full run) is bound after the dry run's record, as before.

## Director's correction (2026-11-04, after the dry run's TIMEOUT): Slurm time limits

**What happened.** The bound texts write the dry run's limit as `--time=0:45`. They are FD-STAB-DECLARATION.md
§7 and §11.2, FD-STAB-ADDENDUM-A1.md §3, §5 and the commands, FD-STAB-BINDING-1.md ruling 3, ruling 3 above, and the
comment in `sbatch_fd_stab.sh:11`. Slurm parses `0:45` as minutes:seconds and rounds 45 s up to 1 minute.
- Job 60826464 got TimeLimit 00:01:00 and ended in TIMEOUT after 1:13, at about 0.02 node-h.
- It was killed inside the truth control, before C1 or C2 reported.
- No task ran, and there is no STOP record and no DONE.

The intent of every text is 45 minutes. The director wrote "`--time=0:45`" into both bindings without checking
Slurm's format, so the error is the director's.

The full run's limit has the same defect. `sbatch_fd_stab.sh:12`'s "at most 7:15" would be read as 7 min 15 s.

**Corrections, binding from here:**
1. **The dry run's limit is `--time=00:45:00`,** 45 minutes and at most 0.75 node-h, as every text intended.
2. **The full run's limit is written as `HH:MM:SS`:** the cap's remainder after the dry run's measured charge, at most
   `07:15:00`.
3. **Every connect prints the job's `scontrol` TimeLimit after submission,** and cancels the job at once if it
   differs from the declared value.
4. **Job 60826464 is INVALID by the director's error.** It is not a probe outcome and not a STOP of the probe.
   - The rerun is a new dry-run connect with a NEW `$OUT`.
   - The rerun runs a fresh DTN pins check into that `$OUT`. Record `ad7f21d3…` is not reused, so the new run's
     inputs are verified at the time it runs.
   - The 0.02 node-h is counted against the 8.0 cap.
5. **The code's comment at `sbatch_fd_stab.sh:11-12`** is left as it is, to keep the bound blob. Ruling 2 above
   governs.

Nothing is submitted, deposited or tagged.
