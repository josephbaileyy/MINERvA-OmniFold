# EVW2D follow-ups (not blocking under the director's scope ruling, 2026-11-25)

From the revision-4 re-reads (codex-school gpt-6.2-sol; claude-personal claude-sonnet-5-5) and carried round-2 PARTLY items.
None can change the published weights, the constants or the exactness gates by a mistake or a lasting change.

**At the binding (checks on the cluster, before GO)**
1. ROOT reads the held file through `/proc/self/fd/N` on Lustre (one RDataFrame read of a staged copy by fd).
2. `os.O_NOATIME` is real in the root_6_28 interpreter, and the purge rule (8 weeks unread) is confirmed.
3. Scheduler fields compared as exact strings (director, 2026-11-25, after EVW5D's `NumNodes=1-1`). EVW2D parses no
   scontrol, squeue or sacct output; the launcher, connect and post scripts are binding items and must be checked when
   written. The wrapper compares two environment variables:
   - `SLURM_STEP_ID` must be all digits and below 0xFFFFFFF0. Perlmutter srun steps record `"0"` (threadprobe logs
     60990199, 61014446 and others on main, fd/receipts-1b).
   - `SLURM_JOB_NUM_NODES` must equal `"1"`. A 1-node Perlmutter batch shell records `"1"` (job 61206960,
     flux-extract.json on main). No record shows it inside an srun step; srun inherits it. Print both in the
     launcher's srun step at the binding. A mismatch refuses at preflight (fails closed), before the driver runs.
4. The launcher's `#SBATCH -t` is the 30-minute cap (0.5 node-h), bound with its digest.

**Tests and mutants**
5. An end-to-end run with a real C-CMAP fill-order miss, with nonnegative weights (codex: 1.0 and 20,000 copies of 2^-54 in
   opposite orders give a 1.11e-12 miss). Today the fill-order miss is real at unit level, and the end-to-end fallback
   wiring test mocks the classification.
6. An end-to-end float32 denominator tamper with exactly representable values (`same_bits` dtype has a unit test and
   a mutant).
7. Mutant isolation (codex #7): `GIT_ENV` now has its own test (campaign 10 survivor, killed in the targeted rerun); a config test with a read that changes
   between two reads; the partial-name test with two names under one host and pid; a digest-only `CLEANUP_FILES`
   fixture. Mutants for "ledger opened before unlink", `load_config`'s single buffer and check_staged's second identity
   comparison (Sonnet #7).
8. Spies snapshotting argument digests on entry on both sides (a change made and undone inside a call is not seen;
   the declaration says so).
9. The ROOT tamper test split into before and after C-SELF; the saved paper grid and p∥ grid exercised as well as the
   analysis pT edge.
10. The uncovered refusals: check_tree's four-pin check (C-BIND refuses first), load_runner's module-file check,
    read_signal_tree's length and entry-order checks, own_hist's missing histogram and axis, stage's non-FileExistsError
    copy failure, check_staged's change-while-hashed.

**Hardening**
11. Cleanup: record deletion intent durably before unlinking, check each write's length and close on failure (codex #5).
12. A one-line consistency check of the saved constants: `pot_scale == data_pot / mc_pot` as the driver defines it
    (Sonnet #10); optionally a POT read from the held file against `get_pot_scales` (Sonnet #5).
13. The branch-type check runs after the fit (it fails closed; it costs node time only).
14. The custody snapshot omits `run.json` (it is in the manifest).
15. Allocation provenance rests on the bound launcher; imports reopen the checked paths (within §8's model).
16. C-SELF's bit-for-bit file check compares bin contents; a replacement of `xsec.root` before its first hash that
    changes only bin errors or metadata would pass (codex-school confirmation, 14:04Z). No published value or gate
    depends on them.
17. Cleanup can delete the staged copies before a short or failed ledger write (codex-school confirmation; as 11).
