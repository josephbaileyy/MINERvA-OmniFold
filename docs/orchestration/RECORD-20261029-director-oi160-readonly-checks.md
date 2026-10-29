# RECORD: the read-only checks on the trunk's stat/ML replica provenance (2026-10-29)

**By** the paper-tighten lane, as director. **For** Joseph, beside
[`QUESTION-20261028-trunk-stat-ml-replica-provenance.md`](QUESTION-20261028-trunk-stat-ml-replica-provenance.md),
whose checks 1–3 this runs. **It rules nothing** and answers nothing: the question stays Joseph's.

**CITABLE FOR:** what the scheduler and the pscratch tree showed on 2026-10-29. **NOT CITABLE FOR:** which seed
contract produced the replicas, or any claim that `C_stat` or `C_ML` is right or wrong.

## Check 1: the scheduler (read-only)

On `saul.nersc.gov`, run as `sacct -j 55878359 -X --format=JobID,JobName%20,Start,End,State,ExitCode -P`:

```text
JobID|JobName|Start|End|State|ExitCode
55878359|interactive|2026-07-13T18:02:32|2026-07-13T18:55:10|COMPLETED|0:0
```

The allocation the July log names exists, completed with exit 0, and is named `interactive`. That explains why the
2026-09-10 search by job name found it absent.

## Check 3: the replica directories (read-only)

The location was `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/`. The mtimes are from `ls -l
--time-style=+%FT%T%z`, giving the earliest and latest `.npz` in each directory:

| directory | files | earliest | latest |
|---|---:|---|---|
| `boot_nd_5d_prehm_20260711/` | 100 | 2026-06-27T21:32:24-0700 | 2026-06-29T05:22:39-0700 |
| `boot_nd_5d/` | 100 | 2026-07-11T17:57:21-0700 | 2026-07-13T18:02:01-0700 |
| `seedscan_split_5d_prehm_20260711/` | 24 | 2026-06-27T21:42:03-0700 | 2026-06-28T13:43:12-0700 |
| `seedscan_split_5d/` | 24 | 2026-07-13T03:26:16-0700 | 2026-07-13T09:31:57-0700 |

- **The products:** `uq_cov_stat_5d.root` is 891,732,011 B, modified 2026-07-13T18:04:01-0700. `uq_cov_mlsplit_5d.root`
  is 892,078,834 B, modified 18:05:11-0700. Both mtimes fall inside allocation 55878359, and both sizes are the ones the
  question cites.
- **Digests:** `res_boot_1.npz` differs between the two sets. Its sha256 begins `5e1c42d2607171e9` in `boot_nd_5d/` and
  `2836ff561db04461` in the archive.
- **What this shows:** the archived set was made in late June. The top-level set was regenerated 07-11 to 07-13, after
  the archive, and the products were built from it inside the logged allocation.
- **What it does not show:** which `bootstrap_nd.py` and `seedscan_split.py` ran on 07-11. The fix was committed on
  07-14 (`07c18aee`).

## Check 2: the transcripts

<!-- absence-ok: scoped to the stated search, which is not a covering search of the July sessions -->
A `grep -rl` for `brx2cua11` and `55878359` over `~/.claude*` and `~/.codex*`, cut off at 280 s, returned no file.
It may not have finished, and July's sessions may have run elsewhere, so this is inconclusive.

## What remains

Only check 4 decides it: one replica reproduced with each contract's code, then compared with the stored
`xsec_flat`. That is about one 5D unfold, and it is Joseph's to authorize.
