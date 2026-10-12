# Focused re-review 1 of 2: P4 G1 census package

**Reviewer:** the same read-only Claude Opus 5.5 session that wrote REVIEW.md (sha256 `f2cc6aaf…`), 2026-10-12.
**Same-model caveat:** the author is the same model family. Separate sessions of one model are not
independent review from another provider, and re-reviewing my own findings adds its own bias.
**Scope:** the changed files, the new analysis-smoke evidence, the NERSC copies, and a check for new defects.
I edited nothing in the package, committed nothing and submitted no Slurm job. The tests below ran only in
`review-p4/ana/` and `review-p4/sbtest/`.

## Verdict: **APPROVE**

Every finding is resolved or correctly recorded as open. The fixes add no blocking defect: the sbatch guards
pass legitimate runs and refuse bad ones, and every INCONCLUSIVE gate fires on its fault and stays silent on
a good input, which I tested in both directions. **One condition remains from M3:** the package must land in
a commit before the first `sbatch`, and the REPORT must cite that commit. DESIGN.md records this; it is an
action to take, not a defect. Two new MINOR items (r1, r2) and three NITs are optional.

## Resolution of the findings

| finding | status | evidence |
|---|---|---|
| **M1** billing and cost | **Resolved** | `sbatch_p4.sh:8-9`: `--mem=7600M` (≤ 4 × 1905) and `--time=02:00:00`. Enforced worst case 13 × 2 × 4/256 = 0.41 node-h. DESIGN §5 states the billing rule and the corrected figures |
| **M2** import and pins | **Resolved** | `analyze_p4.py:56-82` imports from `/pscratch/sd/j/josephrb/2d-closeout-c04repair-20261012/repo/2d-unfolding/uq`. I checked that file's sha256 `2ddf7c9f…` against origin/main (now `b456fa4d`) and against that commit's blob: both match. E_U and σ pins are at :59-61, checked at :130-133. `grid_hist_to_array` at :203. The σ cells are checked against E_U at :210 |
| **M3** pre-declaration | **Disclosure resolved; the commit is still a precondition** | DESIGN.md:10-14 gives the order (09:21 result, 09:23-09:24 rule) and freezes the rule at the landing commit. The package is still untracked, and origin/main has no `stageB/diagnostics/p4` path |
| **m4** INCONCLUSIVE gates | **Resolved** | :135-147 (files present and non-empty, provenance sha and rc), :154-155 (no-op control), :176-179 (self-test and counter identity), :210 (cells). `nSigLoopNoTruthPassReco` is reported against `nG1` (:220). Each gate tested below |
| **m5** census write failure exits 0 | **Resolved** | `sbatch_p4.sh:62-64`. Tested: exit 3 with no census file; the control is unaffected |
| **m6** out-of-grid G1 | **Resolved** | :217-219 report the census wG1, the binned sum and the out-of-grid weight; the integrals are renamed `*_grid224` (:224-226). The self-test smoke shows the path working: 4,273.9 = 4,257.6 + 16.4 |
| **m7** unknown classes in compare | **Resolved** | `compare_outputs.py:99-102`: an unhandled class is DIFFERENT |
| **m8** job-name guard | **Resolved** | `sbatch_p4.sh:38`. Tested: right names pass, wrong names refuse |
| **m9** 13 loops | **Recorded** | DESIGN §5 puts the reading to the director |
| **n10** docstring bits | **Resolved** | docstring :32-33, "lowest-numbered … bits 0-7" |
| **n11** duplicate-key weight | **Recorded** | DESIGN §7.4 |
| **n12** "differs only by build paths" | **Resolved** | DESIGN §3 and §7.5 now say "same size, not characterised" |
| **n13** script sha in provenance | **Resolved** | `sbatch_p4.sh:52` |
| **n14** key-packing risk | **Resolved** | DESIGN §7.1 marks it closed |

## What I tested myself

1. **NERSC copies.** NERSC `p4/` has the same sha256 as the local package for `sbatch_p4.sh` `c35c98b3…`,
   `analyze_p4.py` `16905517…`, `compare_outputs.py` `bb3c8d7f…`, `build.sh`, `smoke.sh` and `patch.diff`. The
   binaries are unchanged: patched `d1a7cf34…c9e0`, unpatched `1ab7525e…`. The evidence files match their
   NERSC originals (`analyze_smoke/{analyze.txt,result.json,make_layout.sh}` and `analyze_smoke_self/*`). The
   production source on main `b456fa4d` and on NERSC is still `57792e42…`, and the grant is still
   `ac1bce59…`. DESIGN.md, SHA256SUMS and `review/REVIEW.md` exist only locally, which does not matter for
   running the jobs. The local `review/REVIEW.md` is `f2cc6aaf…`, the same as the NERSC original.
2. **Analysis, reproduced.** I built my own layout from my earlier re-run outputs. Its provenance files use
   **the exact format `sbatch_p4.sh` writes**: task line, `bin=… sha256=`, `script …`, manifest sums,
   `MNV101_*`, `rc=0 end=…`. Run with `--playlists 1A --control ctl1A:1A`:
   - good inputs: `MEASURED; below the pre-declared materiality bound`, exit 0. The result.json is
     **byte-identical** to the author's evidence (`1278d413…`);
   - wrong binary sha: `INCONCLUSIVE (…binary sha256 … != d1a7cf34…)`, exit 3;
   - `rc=1`: `INCONCLUSIVE (…rc != 0)`, exit 3;
   - no census file: `INCONCLUSIVE (…g1_census.root missing or empty)`, exit 3;
   - control file replaced by the May 1A product: `INCONCLUSIVE (no-op control ctl1A vs 1A DIFFERENT)`, exit 3;
   - a forged census with nBkgSkipped + 1: `INCONCLUSIVE (1A: counter identity …)`, exit 3;
   - the self-test gate: covered by the author's `analyze_smoke_self` (selftestN 7, injected 5,285).

   A job killed by Slurm (TIMEOUT or OOM) writes no `rc=` line, so the rc gate also catches scheduler kills.
3. **sbatch guards.** I ran a harness copy of the script in `review-p4/sbtest/`. It differs from the real
   script in exactly two lines, `NS` pointed at the scratch dir and the binary call replaced by a stub (diff
   recorded). Results:
   - task 0 / `2dc_B4_1A`, task 7 / `2dc_B4_1L` and task 12 / `2dc_B4_ctl1L` run: exit 0, census present
     for the playlists, absent for the control;
   - provenance is written as expected, and the analysis regexes match it;
   - re-running task 0 refuses ("already has an output", exit 2);
   - task 3 named `sbatch_p4.sh` refuses (exit 2), and task 12 named `2dc_B4_1L` refuses (exit 2);
   - a failing binary exits 1 with `rc=1` recorded;
   - a stub that writes no census file gets "REFUSE: no census file", exit 3; the same stub on the control
     gets exit 0.

## New findings (none blocking)

**r1 — MINOR — analyze_p4.py:122-123,243-247: a subset run can report "MEASURED".**
`--playlists` and `--control` (added for the smoke) let a partial run print `MEASURED; below the
pre-declared materiality bound`. The evidence file `analyze_smoke/result.json` says exactly that for one MC
file. `playlists` is recorded in the JSON, but the outcome string can be quoted without it. Fix: unless
`playlists == PLAYLISTS` and `control == "ctl1L:1L"`, prefix the outcome with `SMOKE/SUBSET (not the P4
result): `, or make it INCONCLUSIVE. Failing that, the REPORT must never cite the smoke outcome string as a
P4 outcome.

**r2 — MINOR — operator note for sbatch_p4.sh:41.** The driver opens its output file before the loops
(prod `:1856`). So a job killed by the scheduler, or a failed binary, leaves `runEventLoopOmniFold.root`
behind, and an infrastructure retry is refused until `out/<tag>` is moved aside. That refusal is the safe
behaviour, but the operator should know the retry procedure: move the directory, record it, and stay inside
the 3.0 ceiling. Add one line to DESIGN §5.

**r3 — NIT — analyze_p4.py:79-80, :206.** A wrong `reported_cells.py` sha exits with a message, and a missing
σ JSON raises (exit 1, which I tested). Neither writes a result.json with an INCONCLUSIVE outcome. Both
fail closed and are operator errors made before any data is read, so the docstring's "never an exception"
claim is only slightly too strong.

**r4 — NIT — analyze_p4.py:243-244.** When a gate fails, the INCONCLUSIVE string drops the materiality flag.
Consider appending `; would implicate E_U` when `implicates` is true, so the director sees it at once. The
self-test smoke would have shown 183 cells.

**r5 — NIT — DESIGN.md:127-128,132.** "That includes the May production event-loop array's '2 CPUs, 8 GB'"
reads as garbled; the intended meaning is "the same rule applies to…". Line 132 runs the wall-time bullet
into the output-path sentence.

## sha256 of every file reviewed

| file | sha256 |
|---|---|
| sbatch_p4.sh (local = NERSC) | c35c98b3a4da37424f6e5d1252fa083c8464eebcf9d401253ee2dfd326b02a0b |
| analyze_p4.py (local = NERSC) | 169055177a14302139ce9f036f0e30e1d8eeefca483d44c0df7176a03d7d7a67 |
| compare_outputs.py (local = NERSC) | bb3c8d7f642f2642892848dfe23f97280e6fc1398b68eb4a3d41fa1234386644 |
| DESIGN.md (local only) | 64f335cd64a6eba83b62ec1e3fa09557bdc24c99038caa75ce167089090f140b |
| SHA256SUMS (local only) | c2fb9fd63a49252b0d853ead1330739873457bd6d7e4d24754568c22dfba0291 |
| build.sh / smoke.sh / patch.diff (unchanged, local = NERSC) | da5a8a58… / b19419ea… / 6e9171fe… |
| runEventLoopOmniFold_g1census.cpp (unchanged) | fb23240e971fd78d8117c274a02eb375714906a88e7a6f2fad54652342ad00f8 |
| evidence/analyze_smoke/analyze.txt | f36387d5da4a0fb262140871e45d2f19826c44a2cb35b65d98e3da236955fd6c |
| evidence/analyze_smoke/result.json | 1278d413113043019da5dd052c95a1f7d4cdf61c377b29d6727b6822582686ad |
| evidence/analyze_smoke/make_layout.sh | 0a57885a36f5b17d79a83bde952d7ff3c376f7aa6c4ce181b89212eb9a3d8b6c |
| evidence/analyze_smoke_self/analyze.txt | e4dfb165e38b36359572c854aa1c97ebc4f4d94c757fd894949d43afb04dfdf2 |
| evidence/analyze_smoke_self/result.json | e1c5bd4c670370fe275dcc2815db63a260916dbb8cc3876f5019f041f29cb6e9 |
| review/REVIEW.md (local copy = NERSC) | f2cc6aaf83b6144295514b8ce255a58df9726771c9f07913962acd830a4eb797 |
| patched / unpatched binary (NERSC) | d1a7cf346bed88d60e7edc360ca4836ee46a968dc6a7abd4400e066bc4a9c9e0 / 1ab7525e41c4a16eba728ac29dac8bfdcbfa792cc16bb8ca2ba141a24eb950ae |
| pinned reported_cells.py (c04repair repo = origin/main b456fa4d) | 2ddf7c9fbe4c0ffc236c3f82e4b81b12204d17005f90b2dcc0f7a5db5e501594 |
| production runEventLoopOmniFold.cpp (main b456fa4d, NERSC) | 57792e42fe3f5a663016f94b91a5631fc50349135c92b35a08eaefcb85812be3 |
| grant (origin/main) | ac1bce590be2606da9ccfb81637ca659348161851c283c093af258b2d10df008 |
| reviewer harness review-p4/sbtest/sb.sh / sb_nocen.sh | 2a41abe2… / 19bc02d3… |
| reviewer gate-test results review-p4/ana/{good,badsha,badrc,nocen,ctldiff,ident}.json | 1278d413… / 63878afa… / 3c7895df… / 899e78a0… / 253af682… / 54c02956… |
