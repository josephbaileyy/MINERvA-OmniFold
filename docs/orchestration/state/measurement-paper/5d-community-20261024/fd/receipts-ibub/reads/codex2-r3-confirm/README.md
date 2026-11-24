# IBUB code, codex-school2's narrow confirm of item 3 at `1230e29a8` (run by cov2d, at the director's request; 2026-11-24)

**The read:** item 3 alone, at M′ = `1230e29a8`. The report is `REPORT.txt`, sha256
`161a231a6c74fdba021290f0d85e95abcc29b40bd548026ee9778b75fe769705`. It is the relayed `.md`, byte-identical, kept as
`.txt` so its verbatim text is not edited.

**VERDICT: NO-GO,** on one new collision. The reader accepted the stated residual (a FIFO or device under noclobber)
and found no new production writes outside the declared roots.

**MEASURES:** one reader's findings. **CANNOT AUTHORIZE:** anything. Each finding is taken as a fix at
M″ = `db8854e28`. The director reviews that delta directly, with no further codex round.

| finding | the fix at `db8854e28` | proved by |
|---|---|---|
| the connect and the batch both wrote `$N/logs/scontrol-$jid.txt`. If the connect wrote first, the batch's noclobber refused it and the job exited before any work. If the batch wrote first, the connect could overwrite the batch's record | separate names: the connect writes `scontrol-connect-<id>.txt` and the batch `scontrol-batch-<id>.txt`. Each is checked fresh (absent, not a symlink) and written under noclobber | `test_connect_first_then_the_batch_runs_and_leaves_the_connects_record` and `test_batch_first_then_the_connect_writes_its_own_and_leaves_the_batchs`. Both run the template's own record block (cut from `ibub_run_connect.template.sh`) against the real job. `test_the_connect_and_the_batch_name_their_records_apart` reads both names from the two scripts. `test_the_connect_refuses_an_existing_or_symlinked_record_of_its_own`. Mutants restore the shared name on each side, and drop the connect's fresh check; all are killed. The stand-in at M″: in every variant that submits, the batch's record is written first and survives, and `connect_record_exists` STOPs |
| only `--output` was pinned, so an inherited `SBATCH_ERROR` could send stderr outside `$N/slurm` | the connect pins `--error="$N/slurm/%x-%j.err"`. The batch checks StdErr exactly as StdOut (`in_sd`: a regular file, owned, not a symlink, in exactly `$N/slurm`) | the `stderr` and `stderr absent` allocation cases; `test_a_symlinked_stderr_is_refused`; the mutant "StdErr is not checked", killed; sbatch's argv in the stand-in |
| the residual's wording: "every redirect uses O_EXCL" is too broad | reworded in the job's comment, in `../codex2-r3/README.md` and in the package README, to exactly what bash's noclobber does: O_EXCL on an absent path; an existing regular file, or a symlink to one, is refused; a FIFO or device is still opened | the text |
