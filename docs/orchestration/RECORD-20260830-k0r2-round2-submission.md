# RECORD 2026-08-30 — round 2 of the seven k=0 arms, submitted with the allowlist declared

**CITABLE FOR:** the seven round-2 job ids; the preconditions measured before each `sbatch`; the
positive control's result in the real activated environment; and the environment provenance now
recorded on disk. **NOT CITABLE FOR:** the run's OUTCOME, which was not known when this record was
written (§6); any gate movement; discharge of any `F-*` clause; `OI-177` ratification; a
`PACKET-20260823` correction; leg 6; the M(ii) family; or adoption. **Gate 2 remains FAIL and no
scalar-5D covariance is adopted.**

## Authority

`PROPOSAL-20260830-k0r2-resubmission.md`, authorized by Joseph: *"do all of it, can you continue on
the runs too?"* Round 1 died on `OI-179` — the submitter allowlist was never declared. Nothing in the
repository was changed to fix it.

## 1. Run identity — REUSED, and why

Run `k0-7ac0edec-20260830T000215Z`, **the same run id as round 1**, deployment frozen detached at
`7ac0edec`. Reused rather than reissued because the rehearsal, the deployment sha, the `F-17`
operands and the governing proposal are all unchanged, and **round 1's arms produced nothing** —
they died in the launcher preamble before any science. Slurm's `%A` in the output patterns keys log
files by job id, so round 1's six `.err` files remain in place as evidence and cannot be overwritten.

## 2. Preconditions, measured in order

| # | precondition | measured |
|---|---|---|
| 1 | canonical re-quiesced | `FREEZE-20260830-canonical-requiesce-k0r2-resubmission.md`, pushed at `29057db2` **before any operand read** |
| 2 | deploy HEAD | `7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b` |
| 2 | deploy detached | `symbolic-ref -q HEAD` rc 1 |
| 2 | deploy porcelain | **0**, and `--ignored` also **0** |
| 2 | deploy writable source paths | **0**, by an independent `-writable` walk pruning `.git` |
| 2 | `measure_k0_farend_f1b_f17b.sh` | `ad1a8b6405e55094…`, matching the `DECLARATION-20260830` pin |
| 4 | `mii/member_k000000` | **0 entries** — nothing for `mr_skip_if_complete` to adopt |

## 3. The positive control — run this time, in the ACTIVATED environment

The step whose absence let round 1 reach a compute node to fail in 12 seconds.
`PACKET-20260823:123-127`'s method: the deployed launcher truncated at its `mnv_env_pathcheck` line
and executed.

```
[env-preflight] OK: 14 closure member(s) verified against mnv_env_manifest.tsv; env root /pscratch/sd/j/josephrb/k0env
[env-pathcheck] OK: 46 search-path entr(ies) checked; none inside a checkout, none outside the declared environment
--- PREAMBLE_EXIT=0 ---
```

**46, not 37.** The 37 in `PROPOSAL-20260830-k0r2-resubmission.md` §1 was measured on the login PATH
with the guard **unactivated**, and that document says so. The extra nine entries are the env root and
conda prefix, which branch (b) allows via `MNV_ENV_ROOT` / `MNV_CONDA_PREFIX` rather than via the
declared list. **This is the in-job proof the proposal said it did not yet have.**

**A LINE NUMBER THAT DIFFERS BETWEEN TREES, recorded so no later reader thinks one of them is wrong.**
The `mnv_env_pathcheck` call is at **`:112`** in the deployed tree at `7ac0edec` and at **`:107`** in
`main` at the time of this record. `FINDING-20260830-k0r2-env-pathcheck-submitter-declaration-omitted.md`
cites `:107` — correct for `main`, not for the deployed copy. Cite the sha with the line.

## 4. The declaration — the whole fix

```bash
export MNV_ENV_SYSTEM_PREFIXES="/usr /bin /sbin /lib /lib64 /etc /opt /global/common/software \
$HOME/.local/bin $HOME/.nvm $HOME/bin"
```

Three entries, not the two at `PACKET-20260823:122`. Measured against the deployed library on the
real login PATH, the packet's documented two-entry line returns **rc 3** with one `VIOLATION` on
`$HOME/bin`. **The packet is still uncorrected — `OI-179` defect 1, Joseph's call — so this record and
the proposal are the operative recipe.**

## 5. The submission

Environment provenance was written to
`…/runs/k0-7ac0edec-20260830T000215Z/submission-environment-round2.txt` (16 lines) **before** the
first `sbatch`, carrying all nine `MNV_*` values plus `PATH`, `PYTHONPATH`, `LD_LIBRARY_PATH` and
`HOME`. That closes `OI-179` defect 3 for this run: round 1 recorded none of it.

**The abort arm was armed and read three times**, requiring porcelain **726** and status digest
`d429f0f3`, with `exit 9` and no `sbatch` on a mismatch:

| read | UTC | porcelain | digest | |
|---|---|---|---|---|
| 1 | `20:47:32Z` | 726 | `d429f0f3` | before the first `sbatch` |
| 2 | `20:47:37Z` | 726 | `d429f0f3` | before the two dependent arms |
| 3 | `20:47:38Z` | 726 | `d429f0f3` | after the last `sbatch` |

| arm | launcher | JobId | array as queued |
|---|---|---|---|
| 1 bootstrap | `sbatch_bootstrap_5d_gpu.sh` | **`57753239`** | `[1-100]` |
| 2 seedscan split | `sbatch_seedscan_split_5d.sh` | **`57753243`** | `[1-24]` |
| 3 detector bkgaware | `sbatch_unfold_5d_detector_bkgaware_gpu.sh` | **`57753244`** | `[0-18%8]` |
| 4 unified-throw run | `sbatch_uthrow_run_5d_fast.sh` | **`57753245`** | `[0-39%40]` |
| 5 unified-throw block | `sbatch_uthrow_block_5d.sh` | **`57753246`** | `[0-20%10]` |
| 6 sweep bank | `sbatch_sweep_bank_5d_run_bkgaware_gpu.sh` | **`57753247`** | `[1-169%48]`, `afterok:57753244` |
| 7 unified-throw combine | `sbatch_uthrow_combine_5d_fast.sh` | **`57753248`** | single, `afterok:57753245:57753246` |

All seven were `PENDING` immediately after submission; arms 6 and 7 on `(Dependency)`, the rest on
`(None)`/`(Priority)`.

## 6. WHAT THIS RECORD DOES NOT SAY

**It does not say the run worked.** At the time of writing no task had started. Round 1 queued
healthily for about 22 minutes and then failed in 8–15 seconds, so **a clean queue state is not
evidence of anything** and neither is this record. The outcome is owed as a separate record, and the
first thing it must state is whether a task got PAST `env-pathcheck`.

Even a complete successful run does not turn this rehearsal's Gate 2 into **PASS**: three of the six
clauses of the delegated re-evaluation at `327bc105` need producer filings that do not exist, and
`F-17(b)`'s `:1471` half is impossible for this rehearsal by construction.

`OI-177` remains **OPEN and unratified**: arms 2, 5 and 6 are running against §6 ceilings that three
prior actuals exceed by 1.38 CPU task-h in total.
