# BINDING: GENCMP amendment E, Stage G on the "CH, analysis definitions" predictions, and step C-R (director, 2026-11-01)

**Binds** [`FD-GENCMP-AMENDMENT-E-DECLARATION.md`](FD-GENCMP-AMENDMENT-E-DECLARATION.md) and its inputs file
`fd/gencmp-e/INPUTS.sha256`. It binds them as merged in PR #657 at **M = `6cd095d6773a45c8deef47d298245ea270a636ae`**
(PR head `dd91578f3d7b0ee59728be590e0a413e3ab56132`).

**Under:**
- `DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md`, item 2;
- `DECISION-20261101-joseph-gencmp-paper-adoption.md` (#651), items 5 and 6, and its correction (#652).

## The code bound (git blob digests at M)

| blob | path |
|---|---|
| `07899d161bdb84fe6e6b549a3b8ee5886dde77a7` | `nd-unfolding/fd_gencmp_e.py` |
| `9e0272fab22643749df64ea91a6727130a77c9f5` | `nd-unfolding/fd_gencmp.py` |
| `51b77bb53b195d622b66bf4daad902e45f09a66c` | `nd-unfolding/fd_g_figures.py` |
| `fdaa9dc13c983249d385d16425aff26bdf235097` | `nd-unfolding/fd_g_figures_check.py` |
| `fe60ff68344facab0436f2befd97ced6a490d477` | `nd-unfolding/tests/test_fd_gencmp_e.py` |
| `728e7812efe47b71da102f7a180fd7870e2cfb60` | `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/gencmp-e/INPUTS.sha256` |

The deploy verifies each of these with `git rev-parse M:<path>` and stops on any difference.

## What the director checked

- **The digests:** `git rev-parse dd91578f:<path>` gives the six digests above, which match the lane's list.
- **The tests:** at that head, in a detached worktree with its own TMPDIR, `python3 -B -m pytest` ran
  `test_fd_gencmp_e.py` (43 collected), `test_fd_gencmp.py`, `test_fd_g_figures.py`, `test_fd_cpl_addition.py` and
  `test_fd_gencmp_rebuild.py`.
  - The result was 266 passed and 3 skipped (ROOT- or Linux-only).
  - The lane reported 265 passed for the same set. The one-test difference is noted, and it changes nothing bound.
- **The review:** a fresh Sonnet subagent audited the declaration and code read-only. Its prompt and answer are
  verbatim in `FD-GENCMP-AMENDMENT-E-REVIEW-PROMPT.txt` and `-ANSWER.txt`. The lane answered its three blockers (A1, B1,
  B2) in the code and tests at M.
- **The declaration, §3, §5, §6 and §8:**
  - R0 reproduces every committed Stage G readout before any new number, and it gates everything after it;
  - no tolerance is relaxed;
  - every stop is named;
  - the paper text for every outcome is fixed in advance.

## Rulings

1. **E-S, E-M, E-R0, E-1 and C-R are bound as declared,** on a saul login node at 0 node-h.
   - They run in `root_6_28`, from a fresh clone detached at M with empty porcelain.
   - Each step keeps its declared timeout. A timeout stops the chain, and nothing moves to a compute node without a
     new binding.
2. **R0 is the gate (declaration §3).** If any R0 check fails in either arm, E stops and reports, and the chdefs set
   does not start.
   - Comparing strings only in the with arm (S1) is accepted. It was fixed before any run, and the reason is recorded.
3. **C-R uses `E_R` and `Q_R` (family R)** with the three added stops of §5, and with C-R3D.
   - Its 2D numbers supersede #648 §2.3's in the records.
   - They go to Joseph together with X's result. `paper_body.tex:119` is not touched until X reports.
4. **E2's cap of 0.5 node-h is bound now** (one regular CPU job, ≤ 25 min, basis PV J5 60206336). Its code is not.
   - E2 runs only after its code's blob digests are bound, by an addendum to this binding.
   - Once they are bound, E2 runs whatever E-1 shows (A2).
   - **Added by the director:** E2's report goes to Joseph in every outcome, beside its §8 sentence. If C_model,CH
     would change the reported covariance's χ² by more than the GiBUU rise already disclosed (2.3), the director also
     brings Joseph the question of whether the reported C_model should be rebuilt on CH. No covariance changes without
     him.
5. **The paper.**
   - If E-1 completes, the paper lane re-pins and drops the scoping clause under §8's row. Every changed values key goes
     to Joseph through the paper lane's report, with before and after.
   - No sentence is reworded under this binding.
6. **Reads, writes and storage:**
   - O_NOATIME for every pscratch original;
   - writes only under `$P/gencmp-e-20261101/`, which must be absent before E-S;
   - nothing to CFS;
   - the HPSS copy after `hpssquota`, with an explicit list, `hashverify` and retrieval.
7. **The report** gives:
   - each step's controls and readouts;
   - the §8 outcome it reads;
   - its cost (0 node-h for the login steps, `sacct` for E2);
   - every deviation, unprompted.
   It goes to the director. Declaration X (#653's route B) is reviewed and bound separately. It cites
   `fd/gencmp-e/INPUTS.sha256` at M.

## Fixed, unchanged

Every claim and number in the paper until Joseph rules on the report; the reported covariance; Table IV as adopted
in #656. Nothing is submitted, deposited or tagged.
