# RDX s1's job outcome, and the c1 STOP (receipt)

**By** session tier3-design, under the director's goes of 2026-11-15. One receipt for both, as the director asked.

## s1's job: 61315648, COMPLETED 0:0

The submit receipt is `../run-s1-20261115/` (#1160). The job's own log is `s1-job/rdx_s1_1A_61315648.out.txt`, a byte
copy taken by `cat` of `rdx-20261112b/out/logs/rdx_s1_1A_61315648.out` (sha256 `69fb2c75…`, as `sha256sum` printed on
the node). `s1-job/sacct.psv` is the job's sacct row.

| | value | source |
|---|---|---|
| state | COMPLETED 0:0, Elapsed 01:48:02 (6482 s), QOS shared, limit 02:15:00 | `sacct.psv` |
| CPUs | 10 allocated for the 2 requested. The connect's request is MP-1 S1's (2 CPUs, 16G), whose billing gives the rate | `sacct.psv` |
| charge | 6482 s × 0.0391 node-h per hour = **0.0704 node-h**, against the 0.088 ceiling. RDX's total spent is 0.0704 of the 2.5 cap | `rdx_cap.py`'s rate |
| AnaTuples at job start | 294 checked by size and mtime, 0 differ | log line 1 |
| binary | `bld_rdx` md5 `38398191…`, the build's | 2 |
| env | `MNV101_DUMP_TRUTHX=1`, no other `MNV101_*` | 3 |
| the NuE file | before: atime 2026-11-05T15:18:14Z. After: atime 2026-11-15T02:37:00Z. mtime 2021-08-31T15:49:26Z and size 25403 unchanged | 4, 831 |
| the run | rc 0, 6470 s | 832 |
| output | `out/evloop/runEventLoopOmniFold_RDX_1A.root`, 605076305 bytes, sha256 `e042d19173305ea0dcbaf28bcd08077937439e7d9458877d3b6141e4223594ee` | 833 |

The NuE file was read plainly once, at the loop's initialisation, under the exception of 2026-11-12. Its atime moved to
02:37:00Z, after cov2d's LL5D atime-post time 02:21:21Z (condition a). The atimes above are converted from the logged
`atime_ns`. The director accepted the outcome on 2026-11-15.

## c1: STOP, "the checker python has no uproot"

c1 ran once on login27 at the connect `11e7ef92…` and launcher `165fb98e…`, pin M_RDXS `ad0535c4`. The run was at
22:18:54–22:18:56Z: launcher rc 0, ssh rc 0, script rc 8 (`c1.session.txt:1-4, 147-148`).

**What passed before the STOP:**
- the 15 purge-exposed MP-1 inputs: PRESENT, by stat only (5-101);
- `squeue --me`: empty (102-103);
- the policy check: CLEAR. c1's two reads, S0's `base_cv.root` and the pilot output, hit nothing (104-131);
- the staging: S0's `base_cv.root` was copied by O_NOATIME to `out/stage/base_cv.root`, 398375089 bytes, at sha256
  `c76256a4…`, the connect's pin (132-142).

**The STOP:** `$PY -I -B -c "import uproot"` (`rdx_connect.sh:136` at M_RDXS) raised `ModuleNotFoundError: No module
named 'uproot'` (143-146). `$PY` is root_6_28's python3, which has PyROOT but no uproot. No checker ran: C-ALIGN-1A,
C-TRUTHX and the walk probe have no verdict, and nothing was written under `out/checks/`.

**Why the smoke missed it:** `smoke_rdx_stages.sh:106` at M_RDXS answered any `import uproot` call with exit 0. The
stub answered the very check that would have caught this. The 54 tests ran locally, where uproot is installed.

**State left in place:** the staged copy `out/stage/base_cv.root` (a rerun of c1 skips the staging), and the pilot
output, unchanged. No job was submitted.

## The env probe (the director's go, read-only)

`envprobe.sh` (sha256 `1dcf0b60…`) ran once on login27 at 22:20:38–22:20:41Z, piped to `bash -s` over ssh. It wrote
nothing on the cluster. The output is `envprobe.session.txt`:
- the deploy is HEAD `ad0535c4` with porcelain 0 (line 2);
- `omnifold_py310`'s python is Python 3.10.19, numpy 2.2.6, uproot 5.6.9 (4);
- from the deploy, `omnifile_io` (mp1) and `compare_omnifiles` (w2, with `same`) both import, and ROOT is not
  imported (5);
- `omnifile_io.cycles`, given the staged copy opened by `os.open(O_RDONLY | O_NOATIME)`, lists mc_truth_denom;5
  2682267 and ;4 2217328, mc_signal_reco;9 2682267 and ;8 2489136, mc_background;1 52626, and data;1 360123 (6-15);
- the staged copy's size, atime and mtime are unchanged across the read (16-26).

The fix is `../code3/`. Its rerun of c1 is a separate go.

The `*.session.err.txt` files are the ssh sessions' stderr, NERSC's login banner.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:**
  - s1's job outcome: the state, the charge, the NuE log and the output sha256;
  - the c1 STOP, its cause, and the state it left;
  - the env probe's measurements.
- **Not citable for:** any C-ALIGN-1A, C-TRUTHX or walk-probe verdict (none ran), or any reading.
