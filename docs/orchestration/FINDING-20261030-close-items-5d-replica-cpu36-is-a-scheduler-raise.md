# FINDING — the 5D replica arrays' 36 CPUs were granted by the scheduler, not requested (2026-10-30)

**By** the close-items session, on the director's order of 2026-10-30 (backlog candidate 3: sacct metadata and
transcripts only; any launcher change comes to the director as a proposal). Measured at `origin/main` `c3acf1616`, and by
two `sacct` reads on `login37` at 2026-10-30T08:22:08Z and 08:23:08Z
([`state/ssplit5d-cpu36-20261030/sacct-session.txt`](state/ssplit5d-cpu36-20261030/sacct-session.txt), sha256
`1aa64c1f8a717aa9…`).

**CITABLE FOR:** what the six 5D replica arrays requested, what they were allocated, and how they were submitted. Its proposal was declined, so no launcher changes (§6).

**NOT CITABLE FOR:**
- the scheduler rule that raised the count, which is inferred, not measured (§3);
- the CPU affinity the stored runs' processes saw (§3);
- any change to a launcher, `C_stat`, `C_ML` or the trunk.

## 1. The answer

**The committed launchers asked for 16 CPUs, and the scheduler allocated 36.** `sbatch_seedscan_split_5d.sh` and
`sbatch_bootstrap_5d.sh` both request `--qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=64G`.
That line reads `--cpus-per-task=16` in all 15 commits of `sbatch_seedscan_split_5d.sh`, from `923d8de6b` (2026-07-02)
to `865b42d7b` (2026-09-01). For every 5D replica array read:
- `SubmitLine` carries no CPU option;
- `ReqTRES` is `cpu=16,mem=64G`, the launcher's own request;
- `ReqCPUS` is 35 and `AllocTRES` is `cpu=36`.

| array task | job | submitted (as `sacct` prints it) | `SubmitLine` | `ReqTRES` | `ReqCPUS` | `AllocTRES` |
|---|---|---|---|---|---:|---|
| `55849763_1` | `ssplit5d` (the `C_ML` producer) | 2026-07-13T02:24:50 | `sbatch --parsable --export=ALL,HOME=/global/homes/j/josephrb sbatch_seedscan_split_5d.sh` | `cpu=16,mem=64G` | 35 | `cpu=36,mem=64G` |
| `57527869_1` | `ssplit5d` (member) | 2026-08-24T07:57:58 | `sbatch --parsable /pscratch/…/k0r2/clean/nd-unfolding/sbatch_seedscan_split_5d.sh` | `cpu=16,mem=64G` | 35 | `cpu=36,mem=64G` |
| `57753243_1` | `ssplit5d` (member) | 2026-08-30T13:47:37 | the same launcher path | `cpu=16,mem=64G` | 35 | `cpu=36,mem=64G` |
| `58598278_1` | `ssplit5d` | 2026-09-19T16:36:54 | `sbatch --parsable --time=00:45:00 /pscratch/…/z2m-20260919/clean/nd-unfolding/sbatch_seedscan_split_5d.sh` | `cpu=16,mem=64G` | 35 | `cpu=36,mem=64G` |
| `55151671_1` | `boot5d` (the late-June set) | 2026-06-27T16:42:26 | `sbatch --parsable --dependency=afterok:55151668 sbatch_bootstrap_5d.sh` | `cpu=16,mem=64G` | 35 | `cpu=36,mem=64G` |
| `55805463_1` | `boot5d` (a `C_stat` producer) | 2026-07-11T17:11:35 | `sbatch --parsable --export=ALL,HOME=/global/homes/j/josephrb sbatch_bootstrap_5d.sh` | `cpu=16,mem=64G` | 35 | `cpu=36,mem=64G` |

**Controls:** the two OI-160 tolerance arrays, `60489457_0` and `60530414_0`, passed `--cpus-per-task=36` and got
`ReqTRES` `cpu=36`, `ReqCPUS` 36 and `AllocTRES` `cpu=36`. So `ReqTRES` records what the job asked for, and a 16 in it
is the launcher's own value.

**This has been seen before, at another size.** `PLAN-20260918-scalar5d-publication-completion.md:1535-1537` records a
`--cpus-per-task=16 --mem=90G` job getting *"`SLURM_CPUS 49 / AllocCPUS 50`"*.

**Transcripts.** Search: `rg -l -F "55849763" -g '*.jsonl'` over `~/.claude`, `~/.claude-personal`, `~/.claude-school`,
`~/.codex`, `~/.codex-personal`, `~/.codex-school` and `~/.codex-school2`, rc 0, 8 files. One is this session; the other
seven date from 2026-07-31 on. Six of them quote the July status log's submission line (`nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md:524`), which
has no CPU count. The
seventh holds this lane's message of 2026-10-29, which made the inference §4 corrects. None records a CPU override.

## 2. What it means

- **The committed launcher bytes are consistent with what ran,** as far as the CPU request goes. The "discrepancy"
  between `--cpus-per-task=16` and `cpu=36` is the scheduler's adjustment, not different bytes.
- **The thread count the stored replicas were fitted with depends on the site's allocation policy,** not only on the
  committed launcher. LightGBM's threads follow the CPUs the process can use (the `C_ML` DECLARATION §3.1, P3). The same bytes
  would get a different count under a different policy, with no change in the repository.
- **The OI-160 reproductions were right to take 36 from `sacct`.** They requested 36 explicitly and measured affinity 36
  (P3).

## 3. The limits of this finding

- **The rule.** `ReqCPUS` 35 against a request of 16 means the scheduler rewrote the request before allocating. 36 is 35
  rounded up to a whole core of two hardware threads. A memory-per-CPU limit applied to `--mem=64G` fits both numbers,
  as the 90G case fits 50. But the site's configured limit was not read: no `scontrol`, under the read scope.
- **The stored runs' affinity.** #526's P3 measured affinity 36 when 36 was requested. When the scheduler raised 16 to
  36, what `os.sched_getaffinity` returned inside the batch step was not recorded. #526 reproduced the five graded split
  replicas at affinity 36 to within 6.46 × 10⁻¹², which is consistent with 36, but does not measure it.

## 4. Corrections, beside the records (none edited)

Three sentences infer, from 16 against 36 alone, that the launcher that ran was not the committed one or was overridden.
Both alternatives are wrong. All three were written by this lane:
- **`state/oi160-cml-tolerance-20261029/DECLARATION.md:77-78`:** *"So the launcher that ran was not the committed one,
  or it was overridden at submission."*
- **`state/oi160-cml-tolerance-20261029/REPORT.md:117-120`:** *"By `sacct`, then, the stored run was not submitted with
  the committed launcher's `--cpus-per-task`, or that value was overridden at submission."* Its next sentences still
  hold: the run did not try 16, and does not establish which bytes ran.
- **`state/oi160-reproduction-20261029/DECLARATION.md:73-74`:** *"The launcher that ran is not the committed one. It
  took 36 CPUs, where the committed script says `--cpus-per-task=16`."*

The OI-160 verdicts do not rest on these sentences, and they stand. `BINDING.md` ruling 4 only asks that the 36-vs-16
discrepancy be stated. It does not draw the inference.

## 5. Recommendation

**No launcher change is needed to reproduce the stored runs on this system.** Six arrays from 2026-06-27 to 2026-09-19
show the committed request gets 36.

**For the director, as a proposal only:** state the effective allocation where the request is made, so the declared
shape stops reading as 16. Either:
- **(a)** a header comment in `sbatch_seedscan_split_5d.sh` and `sbatch_bootstrap_5d.sh`: at `--mem=64G` on shared QOS
  the scheduler allocates 36 CPUs, per this finding; or
- **(b)** request `--cpus-per-task=36` explicitly. That pins the shape the replicas were fitted with, independent of
  site policy. `sbatch_seedscan_split_5d.sh` is one of the eight k=0 launchers (`865b42d7b`), so a change to it needs
  their parity checks re-run. `sbatch_bootstrap_5d.sh` is not among them; the k=0 bootstrap launcher is
  `sbatch_bootstrap_5d_gpu.sh`.

No change is made here.

## 6. The director's decision (2026-10-30): neither (a) nor (b)

- **The finding is enough.** The launchers' bytes are consistent with what ran.
- **(b) is declined.** It would touch a k=0 launcher and its parity checks, and change no result.
- **(a) is declined too.** No header note is added.
- **The `scontrol` read is not needed.** The rule stays labelled *not measured* (§3).

Nothing is left open here.
