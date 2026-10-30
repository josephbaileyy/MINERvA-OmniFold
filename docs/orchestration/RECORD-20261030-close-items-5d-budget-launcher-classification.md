# RECORD — the two July-era 5D budget launchers, classified (2026-10-30)

**By** the close-items session, on the director's order of 2026-10-30 (backlog candidate 1, read-only). Measured at
`origin/main` `c3acf1616`.

**Carries out** OI-160's next action, which its retirement left unsettled
([`RECORD-20261030-close-items-oi160-closed.md`](RECORD-20261030-close-items-oi160-closed.md)): *"Classify
`run_budget_5d.sh` and `sbatch_combine_5d_budget.sh` as superseded pre-M(ii) launchers, or state why they are live."*

**MEASURES:** nothing. Repository reads only, no cluster access.
<!-- absence-ok: a scoping statement about this record's own method -->

**CHANGES:** no file. Neither launcher is edited, moved or deleted. Classification is never deletion.

**CITABLE FOR:** the class of each launcher and the evidence for it.

**NOT CITABLE FOR:**
- an authorization to run either launcher;
- any claim that `C_stat` or `C_ML` is right or wrong;
- what ran in the 07-13 combine, beyond the log and the timing (§2, §3).

## 1. The classification

| launcher | class | in one line |
|---|---|---|
| `nd-unfolding/run_budget_5d.sh` | **RETAINED: the archive's producer of record.** Not superseded as a record; not a route for new production | It is the launcher the July log names for the act that wrote `uq_cov_stat_5d.root` and `uq_cov_mlsplit_5d.root`, the archive products the adopted trunk's stat and ML blocks are |
| `nd-unfolding/sbatch_combine_5d_budget.sh` | **SUPERSEDED for production.** Retained as a tracked file | It is the batch twin of the same commands, and it did not run on 07-13. Member-scoped production builds `C_stat` and `C_ML` in `sbatch_finalize_5d_bkgaware_gpu.sh`'s member-local combines instead |

**OI-160's framing was half right.** Both launchers are pre-M(ii), but `run_budget_5d.sh` is not merely an old
launcher. The trunk adopted on 2026-09-20 rests on what it wrote, so "superseded" would misdescribe it.

## 2. The evidence

**The two run the same commands.** `run_budget_5d.sh:5` says *"Mirrors sbatch_combine_5d_budget.sh exactly"*. Checked:
the `CV=`, `python3` and argument lines of the two files are identical, 11 lines each. That is two `combine_cov_nd.py`
calls (`--glob 'boot_nd_5d/res_boot_*.npz' --expected-ids 1-100 … --out uq_cov_stat_5d.root`, and the
`seedscan_split_5d` one with `1-24` and `uq_cov_mlsplit_5d.root`), then `analyze_universes_5d.py` with both as
`--bootstrap-cov`. They differ only in the environment preamble and the `#SBATCH` header.

**`run_budget_5d.sh` is the one the July log names.** In `nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md` @ `c3acf1616`:
- `:542`, 16:53 PDT: *"CPU m3246 queue UNUSABLE … -> run budget/adopt/eavailW via 1-node interactive-GPU salloc CPU
  fallback (srun --gres=none), NOT CPU sbatch"*;
- `:544`: *"budget (interactive fallback, run_budget_5d.sh)"*;
- `:546`, 18:02 PDT: *"STAGE2 LAUNCHED: budget via interactive fallback (salloc 55878359 nid001021, bg brx2cua11,
  run_budget_5d.sh) -> uq_cov_stat_5d.root + uq_cov_mlsplit_5d.root + …"*.

The log is a narrative, not a record of the bytes. Two measurements corroborate it:
- **The allocation.** `55878359` exists, is named `interactive`, and ran 2026-07-13T18:02:32 to 18:55:10, COMPLETED
  0:0. Both products' mtimes, 18:04:01 and 18:05:11 −0700, fall inside it
  ([`RECORD-20261029-director-oi160-readonly-checks.md`](RECORD-20261029-director-oi160-readonly-checks.md), checks 1
  and 3).
- **No batch combine.** `sacct` holds no combine job on 07-13/14, by name or in the 18:00–18:10 window
  (`DECISION-PACKET-20260918-scalar5d-publication-blockers.md:802-803`, *"The combine ran interactively — consistent
  with `run_budget_5d.sh`"*). So `sbatch_combine_5d_budget.sh` did not write the archive products.

**The adopted trunk rests on those products.** Their digests, `6580016f…` and `27b2e456…`, match the Z pilot
manifest's declared `sources.stat` and `sources.ml` (`DECISION-PACKET-20260918…:435`). Joseph adopted the pilot's
`z-cv.npz`, `3d7465f6…`, on 2026-09-20 (`DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md`). The replicas
the products were built from read CORRECTED under OI-160's two tolerance runs (#506, #526).

**Member-scoped production does not use either launcher.** In `sbatch_finalize_5d_bkgaware_gpu.sh` @ `c3acf1616`:
- `:413-414` resolve `STAT_COV` and `ML_COV` through `mr_prefix`, under the member's own namespace;
- `:417-424` are *"THE TWO MEMBER-LOCAL COMBINES"*, each with `--expected-ids` at the full ranges;
- `:425` is the undeclared branch: *"reusing the archive's C_stat/C_ML, per this script's original contract"*. It reads
  the archive products, and does not rebuild them.

**No current plan runs either launcher.** No open register row, KNOWN_ISSUES entry or AUTHORIZATION record names them.
- `COSTMODEL-20260911-z-pilot-and-scan.md:30` lists `sbatch_combine_5d_budget.sh` as the "budget combine" stage. That
  is a table of declared `--time` walls for a plan, which says of itself *"nothing here is a measured runtime"*. It
  authorizes nothing.
- `SPEC-20260906-complete-scalar5d-successor-Z.md:2628` calls it *"not one of the seven arms"*.

Search: `git grep -n -E "run_budget_5d|sbatch_combine_5d_budget"` over the tree, excluding `MANIFEST.tsv`, @ `c3acf1616`.
It returns 37 lines in 14 files.
- **The register:** the only hit is OI-160's retired row. Its retirement record names them too.
- **The rest:** records, specs and packets; the July status log; a presentation inventory; `run_budget_5d.sh`'s own
  header; and one launcher comment, `sbatch_uthrow_combine_5d_fast.sh:387`, which lists where `--expected-ids` lives.

## 3. What the classification does not settle

- **The 07-13 combine has no scheduler record of its own,** and no recorded argv or code digest. That `run_budget_5d.sh`'s
  committed bytes are what ran rests on the log and the timing above (`DECISION-PACKET-20260918…:802-807`). This record
  does not close that gap.
- **One citation in the tree names a different producer.** `DECISION-PACKET-20260918…:436` gives the products' producer
  as *"`sbatch_finalize_5d_bkgaware_gpu.sh:167`/`:168`"*, citing `RUNBOOK-20260822-b1-lift-preflight.md:290`. That RUNBOOK row
  lists a *member's* inputs, the files a member run would produce under `mii/`, not the archive's. The finalize
  launcher's own header (`:8-10`) says it reuses the archive products. That row is not relied on here, and it is not
  changed.
- **Both launchers write the archive products in place.** Each does `cd "$REPO/nd-unfolding"` in the canonical checkout
  and writes `--out uq_cov_stat_5d.root` and `--out uq_cov_mlsplit_5d.root` there. Running either would overwrite the
  two files the adopted trunk names by digest. The adoption's digests would show the replacement; nothing in the
  launchers prevents it. No change is made or proposed here.
