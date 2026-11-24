# IBUB code, read 5: agy gemini-3.8-flash-high (2026-11-24)

**By** `director-helper-3`. This read checks codex-school2 read 2's fixes. Its inputs came from `git archive` of
`675e6a4c5` (`inputs.sha256`).

**MEASURES:** one reader's findings. **CANNOT AUTHORIZE:** anything.

**What it confirmed:** items 1–6 of codex2-r2 **CORRECT AND COMPLETE**. Item 7 (P0 serialization) is deferred to
the readout connect by the director's ruling. Item 8's runner and tests are complete, but its receipt was pending.

**VERDICT: REVISE,** on two MAJORs, one MINOR and one NOTE:

| # | label | finding | disposition |
|---|---|---|---|
| 1 | MAJOR | `code/mutants.txt` and `trace.txt` were still those of `ee189fefc` | correct. The runs are made at the final commit, after this read's fixes, in a separate worktree, and the receipts are regenerated there. A 90-mutant run that had started at `675e6a4c5` was stopped, because this read's fixes supersede that commit; it is not counted |
| 2 | MAJOR | the committed connect still names M = `ee189fefc` | correct: the connect is regenerated at the new M with `gen_run_connect.py`, which also rebinds the launcher. The new shas go to the director |
| 3 | MINOR | `write_contained` made a single `os.write`, which may write partially | fixed: it loops until every byte is written, and refuses a write that makes no progress. Test `test_write_contained_...` (a 3-byte short write and a zero write); mutant "a short write is taken as complete" |
| 4 | NOTE | `job_record` did not check each reference marker's own job and deploy | fixed: the marker must name the bound job and deploy. Case "a reference marker from another job" in `test_the_barrier_receipt_must_be_the_bound_jobs_pass`; mutant |
