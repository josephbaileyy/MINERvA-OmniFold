# IBUB readout, read 2: agy gemini-4-hydrogen-xhigh, a blocking read of read 1's fixes (2026-11-25)

**By** `director-helper-3`. The model is `gemini-4-hydrogen-xhigh`, by Joseph's rule (via the director) for a blocking
read. The read ran headless from 2026-11-25T08:00:06Z to 08:09:03Z, read-only (`agy -p … --model
gemini-4-hydrogen-xhigh --add-dir <tree>`), and ended rc 0 with an empty stderr. Afterwards the tree's sha256 list was
unchanged. Before it ran, openusage showed the Gemini session at 87.56% remaining, from a fetch at 07:55:50Z
(`quota.txt`). Its inputs came from `git archive` of the package's head `3a6c1a79f` (M `8cac52ee8`), on the same
paths as read 1, with each file's sha256 in `inputs.sha256` (277 files). The prompt (`prompt.txt`) carries the
director's rulings as in read 1, and asks for a verdict on each of read 1's six fixes, for regressions, and on mutants
128–138.

**MEASURES:** one reader's findings. **CANNOT AUTHORIZE:** anything.

**What it confirmed:**
- it rebuilt the generated connect and launcher from their templates byte for byte, and matched the fence, the 6 ibub
  sums and the 13 blob hashes;
- `bash -n` passes on the connect, the launcher, the launcher's remote command and the stand-in driver;
- all six of read 1's fixes are CORRECT and COMPLETE (file:line in its report);
- no regression: no new way to grade a tune, no job-PASS gate, no new write path;
- mutants 128–138 each have one site, compile, and are killed by a named test, not by a harness failure.

It did not run the tests or the mutants, because the read was read-only.

**VERDICT: GO** (no BLOCKER, MAJOR or MINOR), with two NOTEs. Both are accommodated. The fixes are commit
`0cde04040`. The package's new M, `b43a5b984`, merges main into it. The director ruled (2026-11-25) that both NOTEs
be fixed. That ruling included a sweep of the readout for every rc or count compared with `== 0` or `== 1`, and no
third read unless the fix touched more than those lines.

| # | label | finding | disposition |
|---|---|---|---|
| 1 | NOTE | a reference's `.done` (`reference_products`) and `units/refcheck.json` (`job_wide`) are read with no symlink check, unlike the toy products; `srun_rc == 0` accepts a JSON `false` (`False == 0`); `ibu_products` has an unused `expected` | **fixed.** A symlinked reference marker returns `<u>'s marker is a symlink`, and a symlinked `units/refcheck.json` fails C-JOB with `units/refcheck.json is a symlink`, each before the read. A reference passes only if `type(srun_rc) is int and srun_rc == 0`. `expected` is removed. Subtests in `JobWide.test_i_…`; mutants 139–141 |
| 2 | NOTE | the launcher's remote command checks `/dev/shm/ibubc.<pid>.sh` and `.out` absent, then opens them; `set -o noclobber` would close that window. The stand-in stubs sacct, the clone URL, the MAT check, the readout, `taskset` and `time`, and does not run the launcher | **fixed** for the launcher: the remote command now sets `set -o noclobber` after `umask 077`, so both writes refuse an existing file. Checked with `bash -n` on the remote command string. The stub boundaries were already listed in the stand-in's README, and the launcher still has no stand-in, as for connect R. That remains a stated residual |

**The sweep** (the director's ruling): `grep -nE "(==|!=) *(0|1)\b"` and the related forms over `ibub_readout.py`
found one comparison of a JSON-read value with 0 or 1: `srun_rc`, now fixed. The others compare numpy arrays
(lines 95–96), a float difference (185), `subprocess` return codes (323, 328), `len()` (402) and a `sum()` of
booleans (533). None of these can be a JSON boolean. `ibub_unit.py:592`, the job's own barrier check, has the same
`srun_rc == 0`. That file is the job's approved code at `d12c4f2a3` and has already run, so it is unchanged. The
readout now re-checks the field itself, and it does not rely on the job's check.

**After the fixes**, at M `b43a5b984`: the tests, the 141 mutants, the trace and the 16-variant stand-in are in
`../../code/readout/` and `../../connect/standin/readout-at-b43a5b984/`.
