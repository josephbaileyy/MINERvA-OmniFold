# IBUB code, codex-school2 read 3 (run by cov2d, at the director's request; 2026-11-24)

**The read:** of `1031c8200`, from a git archive. The report is `REPORT.txt`, sha256
`a2eb4f32773bfa8e361f641bf50b8fe81f65b3068ae38ef04adf4f3da7f111bf`. It is the relayed `.md`, byte-identical, kept as
`.txt` so its verbatim text is not edited.

**VERDICT: NO-GO,** with 4 blocking items. Item 3 is on connect R (the job and its submission). Items 1, 2 and 4 are
on the readout.

**What it confirmed:** round 2's items 1, 4, 5, 7 and 8 correct. It reproduced connect R byte for byte at M, with
the pinned fence and all six file sums, and found the launcher bound to the connect's sha.

**MEASURES:** one reader's findings. **CANNOT AUTHORIZE:** anything. Every blocking item is taken as a fix.

**The director's split (2026-11-24):**
- (a) item 3 is fixed now, at M′ = `1230e29a8`, followed by a narrow confirm on item 3 alone;
- (b) items 1, 2 and 4 are fixed for the readout connect's own package. The readout then also takes `--job-m` and
  requires IBUB-DONE's M, and every unit's deploy_head, to equal it. This is because the readout's bound deploy head
  is otherwise its own HEAD.

| # | finding | the fix | proved by |
|---|---|---|---|
| 3 | the scontrol log's redirect could follow a planted symlink before `noclobber` was set; StdOut was checked only after Slurm had opened it, in a directory others could write to | (a), at `1230e29a8`. The job sets `noclobber` on its first line. From then on, every `>` to an absent path opens O_CREAT\|O_EXCL, which refuses any symlink, dangling ones too. The scontrol record also has a pre-check (`fresh`: absent and not a symlink), kept as belt and braces. The connect makes `$N/slurm` with mode 700 just before sbatch (it cannot exist: `$N` is the connect's own) and submits `--output="$N/slurm/%x-%j.out"`. The job requires that directory to be a real directory, not a symlink, owned by the job's user, mode 700. StdOut must be a regular file, owned, not a symlink, whose parent is exactly that directory | `test_a_symlink_planted_between_the_check_and_the_redirect_is_refused_by_o_excl` (dangling, and to a regular file: the link is planted by the stub scontrol, after `fresh` ran); `test_a_stale_scontrol_record_is_refused_by_the_pre_check`; `test_stdout_must_be_in_the_private_slurm_directory` (stdout in logs/, slurm/ not private, slurm/ a symlink, each by its own refusal message); `test_a_symlinked_stdout_is_refused`; five mutants at these sites, all killed (`../../code/mutants.txt`); the stand-in at M′ (`../../connect/standin/at-1230e29a8/`) |
| 1 | the readout accepted PASS reference receipts with the reference product files absent | (b): hash the actual NPZ and ROOT files, read through O_NOATIME, against the bound barrier, and check the marker's identity | the readout connect's package |
| 2 | with `--out` equal to the absent write root, `mkdtemp` made a sibling in /dev/shm before the check; a symlinked root was accepted | (b): require the configured root to be a real directory at its declared path, not a symlink, and owned; validate `out.parent` before any staging; temporary files default to that root | the readout connect's package |
| 4 | a job that failed only on missing or failed toys read INVALID at the readout; a pinned-input failure (C2_RECORD) left no diagnostic | (b): INCOMPLETE, naming the missing seeds, when toy completeness is the sole failure (from IBUB-DONE's completion fields). Terminal PASS stays mandatory for any grading. Pinned-input failures go through the diagnostic path | the readout connect's package |

**The residual of item 3, stated:** with `noclobber`, bash still opens an *existing non-regular* file (a FIFO or a
device) for writing. A planted FIFO at a log path is therefore not refused by the redirect itself. The job's logs are
in `$N/logs`. The connect creates `$N` and `$N/logs` fresh with mode 700 (template line 69), and `$N/slurm` the same
way just before sbatch, so planting a file there needs the account's own write access.
