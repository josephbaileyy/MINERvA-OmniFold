# RDX code5: the stage-3 fix, gs3a's deploy and the arms' pin read (receipt)

**By** session tier3-design, under the director's rulings of 2026-11-17 on tier3-design's stage-3 packet: the probe go
at `facd34ad`, F1 option (a), F2 as proposed, s1 folded in, and the go to write this code. Code head `29481cdc` (two
commits on `origin/main` `7effa70f`). Nothing in this receipt ran on the cluster except the read-only probe.

## The two blockers

Both were found by tracing stage 3's steps for the director's packet, before any stage-3 go.

**F2: the gates and the arms disagreed about the pin.**
- At M_RDXD, `rdx_connect.sh`:53 set `DEP=$D3` only for s3a and s3b. gs3a and gs3b therefore checked `$D`, the deploy at
  `ad0535c4`, and :59-60 STOP unless that deploy's HEAD is PIN.
- Given stage 3's pin (the merge of `rdx-inputs-SHA256SUMS`), gs3a would STOP at :60.
- Given `ad0535c4`, gs3a would write `pin=ad0535c4` (:102). s3a's arms smoke then requires `S3a.ok` to name s3a's own
  PIN (`sbatch_rdx_arms.sh`:59), so s3a would STOP. Line :100 never lets a gate file be rewritten.
- **Why the smoke missed it.** The smoke wrote `S3a.ok` and `S3b.ok` by hand and ran the arms directly. No connect case
  ran gs3a, gs3b, s3a or s3b.

**F1: the arms read MP-1's pins under an interpreter that cannot import the module.**
- At M_RDXD, `sbatch_rdx_arms.sh`:72 read `MP1_ZERO` with bare `python3 -B -c "...import fd_ct_period_inputs..."`, with
  stderr discarded. The read ran before the env activation at :90, in the smoke and in the job alike.
- `fd_ct_period_inputs.py` needs Python 3.7+ (:37, `from __future__ import annotations`) and numpy (:49).
- **The probe** (`probe/`) confirmed it. `probe/s3probe.sh` (sha256 `facd34ad…`) ran once on login27 at 09:59:43Z on
  2026-11-17, piped to `bash -s` over ssh. It is read-only, and the deploy's porcelain was 0 before and after
  (`probe/s3probe.session.txt:2, 27`).
  - PATH's `python3` is `/usr/bin/python3`, which resolves to `/usr/bin/python3.6`, Python 3.6.15 (6-8).
  - Line 72's read, run verbatim with stderr shown, raises `SyntaxError` at :37 (10-17).
  - The job runs with `--export=ALL`, so it inherits the connect's PATH. That part is inferred, not probed.
  - s3a's smoke would therefore have refused with "could not read MP-1's lat_zero pins", and the connect would STOP.
- **The probe's stage-3 state** (18-26):
  - `out/gates/` holds only `ll5d_atime_post.txt`, `merge.ok` and `s2.ok`;
  - `deploy3` is absent;
  - `ls` of `out/products` fails with "No such file or directory";
  - `tune_v1.json` (461,744 B) has sha256 `13bb1eae…`, equal to its `prep-SHA256SUMS` pin.

## The fix

| file | M_RDXD sha256 | code5 sha256 |
|---|---|---|
| `rdx_connect.sh` | `52ad6a0edf92b4ed…` | `1760327b21f21958…` |
| `rdx_connect_launch.sh` | `256003a1b997a57d…` | `def31c020870bc66…` |
| `sbatch_rdx_arms.sh` | `e3e031e754351847…` | `f77c89a5dd3f59ce…` |
| `smoke_rdx_stages.sh` | `916473e546c60b13…` | `274ecd02afcdcb23…` |
| `test_rdx_stages.py` | | `adad784a48d5ea67…` |
| `rdx_mutation_stages.py` | | `d9fe7c2d1473f7ef…` |

Full digests are in the headers of `tests.txt` and the other receipts.

- **F2.**
  - All four stage-3 steps use `DEP=$D3`.
  - gs3a clones deploy3 at PIN if it is absent. gs3b, s3a and s3b STOP without it: "no …/deploy3 (gs3a clones it at the
    stage-3 pin)".
  - The pin check that follows applies to every step. So `S3a.ok` and `S3b.ok` name the pin deploy3 is at, and the arms
    run from that deploy.
- **F1 (ruling (a)).**
  - The arms read the two lat_zero pins from the committed `rdx-inputs-SHA256SUMS` (`./lat_zero.npz`,
    `./lat_zero_bkg.npz`), with the same awk `sum_of` as the three dumps.
  - They refuse unless all five sums are 64-hex.
  - No python reads a pin. The only python before the activation is the stdlib TimeLimit check (:38). Its 3.6-safety is
    tested, and the merge job's identical check already ran under 3.6 in m's smoke on login27.
  - `rdx-inputs-SHA256SUMS` itself is PR #1204's. It becomes five lines there, with a test that the two lat_zero lines
    equal `fd_ct_period_inputs.MP1_ZERO`.
- **s1.**
  - s3a and s3b run `policy()` over their six reads, before the arms smoke: the three dumps, the two staged lat_zero
    copies and `$PVL_RATIO`.
  - `$PVL_RATIO` is the arms' default `tune_v1.json` path, and a test requires the two to agree.
- **The launcher** pins the new connect, `1760327b…`.

## What was checked

All at `29481cdc`, in a clean clone, serial, nice 19, BLAS threads 1:
- **Tests:** `tests.txt`, 62 OK under Python 3.12.2 (38 in `test_rdx`, 24 in `test_rdx_stages`). `tests_py310.txt`, 62
  OK in a uv venv matching omnifold_py310's versions (Python 3.10.20, numpy 2.2.6, uproot 5.6.9).
  - The new class `Stage3` (`tests.txt:64-66`) runs the extracted lines rather than only matching text.
  - `test_the_arms_read_every_pin_with_awk_and_no_python_reads_a_pin`: the arms' sums block reads five sums from a
    stand-in file, and exits 2 naming the missing key when any line is absent.
  - `test_stage3_gates_and_submits_share_deploy3_cloned_by_gs3a`: the DEP line, the clone condition and the deploy3
    STOP, for every step with deploy3 present and absent.
  - `test_s3_checks_its_reads_and_names_the_arms_paths`: s3's policy reads equal the arms' input paths.
- **Mutation:** `mutation.txt`, 51/51 killed. `mutation_stages.txt`, 55/55 killed, 8 of them new:
  - gs3a/gs3b back on the old deploy;
  - s3a cloning again;
  - no STOP without deploy3;
  - s3 without the policy check, or without the ratio;
  - the arms reading lat_bkg with python;
  - lat_bkg taking lat_zero's sum;
  - the sums unchecked.
- **Smoke:** `smoke.txt`, exit 0 (232). The new cases:
  - **The arms:** a lat_zero copy off its committed sum refuses (70-71). Under a `python3` that cannot import the pin
    module, the arms still pass, because nothing imports it (72-73).
  - **The connect, as on the cluster.** The old deploy is held at `<pin>`, and stage 3's pin `<pin3>` is a later commit.
    - s3a and gs3b STOP without deploy3 (180-187).
    - gs3a clones deploy3 at `<pin3>`, clean, and writes `pin=<pin3>` (188-192). A second gs3a refuses (193-196).
    - s3b before gs3b STOPs at the arms smoke (197-200). gs3b then writes its gate (201-204).
    - s3a at the old deploy's pin STOPs (205-208).
    - s3a and s3b pass their checks and submit from deploy3 at `<pin3>` (209-218).
  - Three arms refusal lines (63, 65, 67) print the absolute work dir, because those cases pipe through `tail` only. The
    output is kept byte for byte.
- **`smoke_at_m_rdxd.txt`:** the same smoke, with M_RDXD's `rdx_connect.sh` and `sbatch_rdx_arms.sh` swapped in for the
  run, then reverted (the clone's status afterwards was 0 lines). The new cases catch both defects:
  - F1: "refusing: could not read MP-1's lat_zero pins" (73-74).
  - F2: every gs3a and gs3b STOPs at the old deploy's pin check, "not `<pin3>` clean (HEAD=`<pin>`)" (185-205). s3a and
    s3b STOP at the arms smoke (181-183, 210-217).
  - Line 193's deploy3 at `<pin3>` was cloned by the old s3a's first case (181), which still cloned it.
- **The first smoke version** (commit `7aefe3a5`) had the old deploy and deploy3 as one stub repo at one pin. That hid
  F2: M_RDXD's connect passed the chain there. Commit `29481cdc` separates them. It is the second instance in this lane
  of a smoke that never ran a step's real predecessor.

## Next

coverage-5b-audit's delta on code5, then the director's J6 with the new shas. Then #1204 (five lines, with main merged
in once code5 has merged), and then the stage-3 goes, each on its own.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:**
  - the two defects and the probe's three measurements;
  - the fix's shas and the checks above.
- **Not citable for:** any stage-3 run or verdict, or any RDX reading. Only the read-only probe ran on the cluster.
