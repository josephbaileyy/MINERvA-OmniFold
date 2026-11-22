# RDX c2/m fix: the pin reads under omnifold_py310, c2's policy check and record names (receipts, for the audit delta)

**By** session tier3-design, under the director's approved outline of 2026-11-16, with l1 and l2. The defect was found
by reading c2's code before the c2 packet. It was then confirmed by the director's read-only probe (`probe/`). Code HEAD
`d76b932c`. Only these five files change from M_RDXC `11e36cf1`:

| file | sha256 at M_RDXC | sha256 now |
|---|---|---|
| `nd-unfolding/rdx/rdx_connect.sh` | `eae946894be8ce02354e8bd6aaf038d78bd8f574772a359b90eaeb0d1dfd985d` | `52ad6a0edf92b4ed31058d27c2a9793042f425befcfc0268176707593c295cc6` |
| `nd-unfolding/rdx/rdx_connect_launch.sh` | `602c728a7b4326f2146bc219ec88ffb5da145869e81df9f4c1e214022e94212b` | `256003a1b997a57de0efccafde57d7f906113a2e2e95aae4e40433cde5f79b1e` |
| `nd-unfolding/rdx/smoke_rdx_stages.sh` | `f02ca57acdfab743dc4774393d6d2742e07c1dd9badfdb0f639a152737511a54` | `916473e546c60b13a68cf2e9559e8e67528d233de1e8eb3cb10bb9151bf4c7ad` |
| `nd-unfolding/rdx/test_rdx_stages.py` | `b40f5beeb0cea98cfceb3451f9f9342986a1f779bd35ba946701f02ec69f4681` | `0dab0bb8434e0a191913b0ba185fedd81843b400dc55c10b9066698d9874ac4c` |
| `nd-unfolding/rdx/rdx_mutation_stages.py` | `bc06bf00dc8326f28ce36c921873b6d77ddcd687c7cd1dd8a0523c3f17de51b6` | `37e89147dc5f28f61a1b3f191227a0975b5b59928ef80f4b8ec8c77d5fbe2fbd` |

No checker, job script, deploy module or other file changes. The deploy stays at M_RDXS `ad0535c4`. On the node, the
deploy's `fd_ct_period_inputs.py` has sha256 `4d005f26…` (`probe/pyprobe.session.txt:3`), the same as the blob at
`ad0535c4`.

## The defect

- **c2's ZERO_LOOPS read** (line 192 at M_RDXC) imported the deploy's `nd-unfolding/fd_ct_period_inputs.py` under
  `$SYSPY=/usr/bin/python3`. So did **m's MP1_ZERO read** (line 206).
- That module starts with `from __future__ import annotations` (its line 37), which needs Python 3.7, and it imports
  numpy.
- The login nodes' `/usr/bin/python3` is 3.6.15. So c2 would have STOPped with "no zero-loop pin for 1A" on every run,
  and m with "could not read MP-1's lat_zero pins". Both fail closed.

**Why the smoke and tests missed it:**
- the smoke's stand-in module had neither the `__future__` line nor ZERO_LOOPS;
- its SYSPY was the laptop's python3;
- its only c2 case STOPped at chkenv;
- no test reached either pin read.

## The probe (the director's go, read-only)

`probe/pyprobe.sh` (sha256 `4f14d7ba…`) ran once on login27 at 01:17:20Z on 2026-11-17, piped to `bash -s` over ssh.
It runs `-B`, so it writes no `.pyc`, and it wrote nothing on the cluster. The deploy's porcelain was 0 before and after
(lines 2, 18).
1. `/usr/bin/python3 -V`: **Python 3.6.15** (5).
2. Line 192's import, verbatim, under SYSPY for 1A: **SyntaxError: future feature annotations is not defined**, at the
   module's line 37, rc 1 (8-14).
3. The same line under CHKPY: **`2745e38c…`**, the 1A pin, rc 0 (16-17).

The probe agrees with the premise, so the fix went ahead. `probe/pyprobe.session.err.txt` is the ssh session's
stderr, NERSC's login banner.

## The change

**`rdx_connect.sh`:**
- **c2 and m read their pins under `$CHKPY`** (omnifold_py310: 3.10, numpy).
  - c2's read follows its existing chkenv. m now calls `chkenv` after its policy check and before the read.
  - c2 also requires the pin to be 64 hex digits.
  - `SYSPY` now runs only `rdx_paths.py` and `rdx_cap.py`. A comment on its definition records why.
- **c2 runs the policy check (l2)** over its 24 reads before any staging or read: the 12 MP-1 zero loops and the 12 RDX
  outputs.
- **c2 writes `checks/align_<PL>_pl.json` and `checks/truthx_rows_<PL>_pl.json` (l1)** for all 12 playlists, so c1's
  `align_1A.json` and `truthx_rows_1A.json` are never overwritten. Nothing reads these names except the connect itself.
  The merge job reads only `out/loops.sha256`.

**`rdx_connect_launch.sh`:** the new connect sha256 only.

**`smoke_rdx_stages.sh`:**
- **The stand-in module** starts with `from __future__ import annotations` and carries a ZERO_LOOPS dict for the smoke's
  own zero loops.
- **The SYSPY stub** stands in for 3.6. It runs only `rdx_paths.py` and `rdx_cap.py` and refuses `-c`. It is shared by
  both connect copies.
- **New cases:**
  - c2 with a zero loop off its pin: STOP at the staging (`smoke.txt:136-140`);
  - c2 with a failing alignment: STOP, `loops.sha256` not written (141-145);
  - c2 passes: STAGE 2 CHECKS PASS (146-150), with 12 zero loops staged by the real `rdx_paths.py stage`, 24 `_pl`
    records, and c1's `align_1A.json` still the PASS it wrote (151);
  - c2 refuses a second run (152-156);
  - m with no uproot: STOP at chkenv (157-160);
  - m reads MP-1's pins and submits (161-165).

**`test_rdx_stages.py`** (18 → 21 tests), class `PinLookup`:
- `test_syspy_runs_only_the_36_tools_and_the_pins_are_read_under_chkpy_behind_chkenv` (static):
  - every `$SYSPY` line runs `rdx_paths.py` or `rdx_cap.py`, never `-c`;
  - neither of those files has `from __future__ import annotations`;
  - both pin reads run under `$CHKPY -I -B -c`;
  - c2 and m call chkenv before the read.
- `test_the_pin_reads_give_every_committed_pin_and_fail_closed` (behavioural). It runs c2's and m's lines verbatim in
  bash, with CHKPY set to the test's python, against the committed module:
  - all 12 ZERO_LOOPS and both MP1_ZERO pins come out equal to the module's literals, read by `ast`;
  - a non-hex pin STOPs, rc 8;
  - a deploy without the module STOPs, rc 8, for both lines.
- `test_c2_checks_its_reads_and_never_writes_c1s_records` (static):
  - c2's READS hold the zero loops and the outputs;
  - `policy "${READS[@]}"` precedes the staging and every read;
  - c2's `--out` names are the `_pl` ones, and none equals one of c1's.

**`rdx_mutation_stages.py`:** `EXPECTED_TESTS` is 21, with eleven new mutants, each killed by its named test:
- c2's pin read back on SYSPY;
- m's pin read back on SYSPY;
- m without chkenv;
- `rdx_paths.py` given the `__future__` line;
- c2's 64-hex check dropped;
- c2 reading 1A's pin for every playlist;
- m reading lat_bkg twice;
- c2 without the policy check;
- c2's policy check without the zero loops;
- c2's align output on c1's name;
- c2's rows output on c1's name.

## The receipts (clean clone at `d76b932c`, serial, nice 19, threads 1)

| file | result |
|---|---|
| `tests.txt` | 59 tests (`test_rdx.py` 38, `test_rdx_stages.py` 21), OK: Python 3.12.2, numpy 1.26.4 |
| `tests_py310.txt` | the same 59, OK, under a uv venv at omnifold_py310's measured versions: Python 3.10.20, numpy 2.2.6, uproot 5.6.9 |
| `mutation.txt` | 51 of 51 declared mutants killed by their named tests |
| `mutation_stages.txt` | 47 of 47 killed: 36 as before, and the eleven above |
| `smoke.txt` | 44 cases, exit 0. Against `../code3/smoke.txt`, the only behavioural changes are the six new c2 and m cases |
| `smoke_at_m_rdxc.txt` | the same smoke, with `rdx_connect.sh` replaced by M_RDXC's for the run (then reverted; the clone's status afterwards was 0). Every c2 case past chkenv STOPs with "no zero-loop pin for 1A" (lines 9, 14, 19, 25), the probe's failure. Its m cases STOP earlier, at "no loops.sha256" (29, 33), because c2 never wrote it. So m's pin read under SYSPY is shown by its mutant and the static test, not by this run |

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:**
  - the probe's three measurements;
  - what the tests, mutants and smoke check at `d76b932c`;
  - the five files' shas.
- **Not citable for:** any c2 or m verdict, or any RDX reading. Only the read-only probe ran on the cluster.
