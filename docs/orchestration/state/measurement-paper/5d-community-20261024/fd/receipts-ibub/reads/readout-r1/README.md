# IBUB readout, read 1: agy gemini-4-hydrogen-xhigh, a blocking read (2026-11-25)

**By** `director-helper-3`. The model is `gemini-4-hydrogen-xhigh`, by Joseph's rule (via the director) for a blocking
read. The read ran headless at 2026-11-25T02:49:52Z, read-only (`agy -p … --model gemini-4-hydrogen-xhigh --add-dir
<tree>`), and ended rc 0 with an empty stderr. Before it ran, openusage showed the Gemini session at 96.96% remaining,
from its first fetch after the 02:45:21Z reset (`quota.txt`). Its inputs came from `git archive` of the readout
package's head `d3d9c6b71` (M `94d81351c`), with each file's sha256 in `inputs.sha256`. The prompt (`prompt.txt`)
carries the text of the director's item-4 ruling and `--records` corrections, which were given by message and are not
committed elsewhere.

**MEASURES:** one reader's findings. **CANNOT AUTHORIZE:** anything.

**What it confirmed** (it rebuilt the generated connect and launcher from their templates byte for byte, decoded the
fence to rev 3, and matched the 6 ibub sums and the 13 blob hashes):
- no job-PASS gate, with the job-wide prerequisites and C-COMPLETE per tune: CORRECT;
- the INCOMPLETE / INVALID / PASS classification: CORRECT;
- connect O's order and exit codes: CORRECT;
- the launcher's sha binding: CORRECT;
- the four `--records` mutants (104–107): present and killed.

It did not run the tests or the mutants, because the read was read-only.

**VERDICT: GO** (no BLOCKER or MAJOR), with five MINORs and one NOTE. Each is accommodated below. The fixes are commit
`86c4493f1`. The trace at that commit then found two lines unreached: the new guards in finding 4 against a toy or
reference meta that is not a JSON object. Commit `bee6e5522` adds those test cases and mutants 137–138. The package's
new M, `8cac52ee8`, merges main into it.

| # | label | finding | disposition |
|---|---|---|---|
| 1 | MINOR | connect O made `$N/readout` and copied the products out before it acted on the post-run `git status` | **fixed.** The deploy check now runs straight after the readout's two tunes, before `$N/readout` is made: `STOP: the deploy changed: nothing is published`, rc 9, with the records tar. Stand-in variant `deploy_changed` (the stub readout writes a file into the clone) |
| 2 | MINOR | the re-run guard missed dangling links and `$FR.tar`/`.list`/`.sums` and `connect-readout.done`; a dangling optional record read as "absent"; the `.done` write was unchecked | **fixed.** Every output path must be absent, a dangling link included. The fetch treats a dangling link as not absent: it reaches the regular-file STOP. A failed `.done` write is logged, and a 0 becomes 4. Stand-in variants `done_exists` (a dangling `.done` link: BAIL) and `ibub_done_dangling` (a dangling IBUB-DONE: STOP, not "absent") |
| 3 | MINOR | `pseudo_b.json`, the cells' blocks record and `completeness.tsv` were read but missing from `rec["inventory"]` | **fixed**, with more. The three pinned inputs enter the inventory at their pins, once each read has matched its pin. RECORDS.SHA256SUMS and every fetched record also enter it at their verified digests. `test_every_graded_byte_is_inventoried_from_its_one_read` checks all of them. Mutants 133–135 |
| 4 | MINOR | hardening gaps: a FAIL marker from another job read INCOMPLETE; a stray marker outside the tune's prefix was not seen; toy products were not refused as symlinks; dict guards and a truthy `pass`; references' meta not checked for runner and config | **fixed.** The declaration's C-COMPLETE asks for markers "each from the bound job at the bound deploy", and `ibub_unit` writes job and deploy into every marker, PASS or FAIL. So a marker naming another job or deploy is now a problem whatever its verdict (INVALID). Any undeclared `.done` in units is a problem, with the same known set as `ibub_unit.complete`. A symlinked toy `.done`, `.root` or `.npz` is refused. Meta, controls, the barrier's units and `central_df_vs_central` must be objects, and a control passes only on `True`. Each reference's meta must carry the job's runner and config sha256. Tests in EndToEnd and JobWide; mutants 128–132 and 136–138 |
| 5 | MINOR | no tests for scontrol JobName, NumNodes, AllocTRES cpu, a barrier digest off its marker's, or a sacct row of under 4 columns | **fixed.** Subtests in `test_i_…` and `test_v_…` |
| 6 | NOTE | the launcher's usage line named `ibub_run_launch.sh`; its `/dev/shm` target was not checked absent; the stand-in has no `CANCELLED by <uid>` variant | **fixed.** The usage line is corrected. The node now refuses (exit 8, before writing) if `ibubc.<pid>.sh` or its `.out` exists, a link included. Stand-in variant `cancelled_by` (`CANCELLED by 112498`: terminal, read). The launcher itself still has no stand-in, as for connect R. That is stated as a residual, not fixed |

**After the fixes**, at M `8cac52ee8`: the tests, the 138 mutants, the trace and the 16-variant stand-in are in
`../../code/readout/` as committed at `3a6c1a79f`, and in `../../connect/standin/readout-at-8cac52ee8/`. The second read
(`../readout-r2/`) found all six fixes correct (GO). Its two NOTEs are fixed at the package's later M `b43a5b984`.
