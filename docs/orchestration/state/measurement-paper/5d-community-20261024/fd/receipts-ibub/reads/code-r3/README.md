# IBUB code, read 3: agy gemini-3.8-flash-high (2026-11-24)

**By** `director-helper-3`. This is a confirm read of read 2's fixes, plus a first read of the step-5 files: the lanes,
the overlap check, the job, and the connect template, generator and launcher. Its inputs came from `git archive` of
`d2b7a9d8c` (`inputs.sha256`). **VERDICT: GO.** It found no BLOCKER and no MAJOR, and confirmed read 2's fixes.

**MEASURES:** one reader's findings. **CANNOT AUTHORIZE:** anything. The same commit's codex-school2 read was NO-GO;
`../codex2-r1/README.md` gives its dispositions. Every finding of both reads is taken as a fix in the commit that adds
this record.

| # | label | finding | disposition |
|---|---|---|---|
| 1 | MINOR | IBUB-DONE was written with rc 0 before the verdict check | fixed, as codex B2: one atomic IBUB-DONE after every check |
| 2 | MINOR | the srun step names used `ibub-`, not `ibub_` | fixed: `--job-name="ibub_$tag"` |
| 3 | MINOR | the AllocTRES cpu parse assumed `cpu=` came first | fixed: AllocTRES is split on commas, `cpu=` and `mem=` (M or G) are read by key, and an unreadable value refuses |
| 4 | NOTE | the launcher held a `@@CONNECT_SHA@@` placeholder | fixed: the launcher is now `ibub_run_launch.template.sh`. `gen_run_connect.py` writes `ibub_run_launch.sh` with the generated connect's sha256 bound in |
| 5 | NOTE | the generator had no usage check | fixed: no M, or an M that is not 40 hex characters, prints the usage and exits 2 |
