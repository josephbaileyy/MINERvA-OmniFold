# Focused re-review, cycle 1: Stage A checklist repair (commit `4122f928`)

**Reviewer:** the same read-only Claude Opus 5.5 session that reviewed `8d086a20`. The owner is the same model, so this is not cross-provider independence (plan §5).
**Target:** `docs/orchestration/state/2d-closeout/stageA/REPORT.md` at `4122f928`, compared against `8d086a20`.
**Scope:** only the four checks the coordinator asked for.

## Verdict: PASS WITH CHANGES

All 14 findings from the first review are resolved as §7 says: M1, m1–m4 and N1–N8. Both hygiene checks pass. The preserved review file matches what I wrote.

The repair adds one new overclaim (R1, MINOR). It also leaves one loose phrase in §1 (R2, NOTE). Both are one-line wording fixes and need no new compute. R3 and R4 are notes on my own earlier review text and need no change to the record.

## (1) Is each finding resolved as §7 says?

| finding | resolved? | evidence at `4122f928` |
|---|---|---|
| M1 | **Yes** | §1 now says "EXIT MET for the candidate procedure, via L0". It states plainly that `E_U`'s own manifest is not complete. It declares L0's manifest as the frozen producer: driver `3cc5adc7…`, helper `e9623412…`, omnifile `43f8cc16…`, flux `d40aea69…`, 64 threads, seeds 42/43/44, argv, `bkg_mode purity`. It says not to re-run `E_U`'s launcher. The CATALOG row now says "via L0". (R1 qualifies the word "frozen".) |
| m1 | **Yes** | The §1 table row 2 and §3.2 now say: bitwise equal to `integral_ours_all_bins`, 1 ulp from `integral_ours_reported`. They also disclose that `analyze.py` does not open the receipt. I re-checked: `integral_ours_all_bins` = 3.0730230563866027e-38, the record's value. |
| m2 | **Yes** | KI 90 is now in NOT CITABLE FOR, with the closure requirement (a refusing negative control with the same size and different cells). Row 1 is labelled "(`E_U`'s own set; not KI 90)". The §3.1 wording about the plan is corrected. |
| m3 | **Yes** | §6 now says the input is unavailable (quoting KI 93) and that its equivalence is inferred, mainly from the 1.4e-11 output agreement. (R3 is about my original wording here.) |
| m4 | **Yes, in substance** | §1 says the selective-I/O delivery is outside this record. The producer-change sentence is correct (see section 2). R2 is about the phrase "is delivered separately (A-1)". |
| N1 | Yes | The base is now `7edb65fab817b9bf04749dcafb12971352b3c64f` (PR #93); I confirmed this full sha. |
| N2 | Yes | 25 keys: 16 histograms (13 TH2D, 3 TH1D), 7 TParameters, 2 TNamed. |
| N3 | Yes | The two adjacent doubles are named. The wording is now "equal to 1 ulp". |
| N4 | Yes | The README units and the source of "per nucleon" are now kept separate. |
| N5 | Yes | §3.4 now calls this a transcription check, not an independent derivation. The parameters are cited to `runEventLoop.cpp:361` and `runEventLoopOmniFold.cpp:1708`. Both citations and driver `:38` checked. |
| N6 | Yes | The new citations, checked at `37985acc`: `:1488` purity comment; `:1472–1474` `hMeasSub2D` = data − bkg; `:338` `build_measured_training_2d`; `:1475` its call. |
| N7 | Yes | §4 and §8 now carry `220c479e…`, with an end time of 08:20:38Z. |
| N8 | Yes | §3.8 now says the comparison is independent of XR's code, not of the owner, and cites my GetArray reproduction. |
| N9 | Not this record's (correctly no change) | — |

The repair commit leaves `scripts/` and `operands/` unchanged, so the earlier byte-for-byte re-run of `analyze.py` still applies.

## (2) Does the repair add a new defect or overclaim?

**R1 (MINOR). "Frozen for Stages B and C" includes the CV omnifile as the frozen input, but Stage B's job is to resolve inputs.**
`REPORT.md` §1, the frozen-producer bullet; the CATALOG row ("whose manifest is frozen for Stages B–C").

- The declared manifest names `43f8cc16…` as the input. That is the 2.1 GB CV omnifile, with no universe content.
- Plan §4 Stage B is "resolve inputs and define the complete uncertainty recipe". KI 93 leaves open which universe and truth inputs the construction should use.
- **Failure scenario:** a Stage C lane reads "frozen for Stages B and C". It either treats `43f8cc16` as the input for universe and replica products, or concludes that Stage B may not change any input.
- **Fix:** scope the freeze. For example: "the central-value producer frozen for Stages B–C; the inputs for universe and replica products are Stage B's to resolve (KI 93)". Apply the same wording to the CATALOG row.

**R2 (NOTE). "Delivered separately (A-1)" can be misread as already delivered.**
`REPORT.md` §1, the last paragraph.

- "A-1" is defined nowhere in the repository. The selective-I/O work exists on branch `closeout/stage-a-selective-io-20261012` (`798f8340`) and on `impl/selective-io-20261010`, and is not on `main`.
- "Is delivered separately" could be read as "already delivered".
- **Suggested wording:** "is outstanding at this commit; it is the director's A-1 deliverable".

The producer-change sentence itself is correct. Both selective-I/O branches change `2d-unfolding/unfold_2d_omnifold_unbinned.py` (+354/−11 lines), which moves its sha256 from `3cc5adc7…` to `6be77c51…`. So after a merge, `main`'s driver is no longer L0's, and the plan's equivalence bridge applies.

**§3.4:** correct as rewritten; nothing new to report.

**§6:** the "no unexplained drift, so no Stop" reasoning is sound and properly qualified. One phrase comes from my own review and is looser than the evidence; see R3.

**Notes on my own earlier review (no change to the record required):**

- **R3 (NOTE). The "about 1e-3" phrase overstates the evidence.** In §6, "a different event sample would move LightGBM at about 1e-3" comes from my m3 wording. The measured 1e-3 is the *seed* effect. Sensitivity to a change in the event sample was not measured, and a tiny difference in events could move the output by less. The argument still holds, because the 1.4e-11 agreement is about 10⁸ times below the seed effect. Suggested wording: "about 10⁸ times below the 1e-3 seed effect".
- **R4 (NOTE). My citation count was off by one.** My earlier review said "14 checked", but its list has 15 entries; the 15th is `:49`. §7 repeats "14". This is my error, and it is preserved verbatim as it should be.

## (3) Is `review/review-8d086a20.md` byte-identical to what I wrote?

**Yes.**

- I re-typed the first 82 lines of my original message (through N9) from my own context into a scratch file. `diff` against the committed file shows no differences.
- I read the remaining 67 lines (assessment table, recomputation table, hygiene, citations, worktree status) line by line against my message. They are identical.
- The file ends without a trailing newline, as my message did.
- File: 149 lines, 14,747 B, sha256 `cba4aaa3312609d457fa8cff0487e867ed25adf35effd0dd76fe43f5ee9119ab`.
- Its MANIFEST row is the default `MACHINE … generated`.

## (4) Hygiene checks

- **`python3.12 docs/orchestration/generate_manifest.py --check --at-sha 4122f928`:** `MANIFEST-CHECK :: OK exit=0`. rows=2318, one more than at `8d086a20`, for the review file; one unused override, unchanged.
- **`python3.12 docs/orchestration/verify_hash_bindings.py`:** rc 0, `ALL BINDINGS INTACT`.

## Worktree status

- **Start:** a new detached worktree at `/private/tmp/claude-501/review-a2-4122f928`, HEAD `4122f928e92350d40cf122eedf249cf64b3eb56b`. `git status --short` was empty.
- **End:** `git status --short` was empty (0 lines) and HEAD was unchanged. The worktree was removed with `git worktree remove` (rc 0) and is no longer listed.
- **No other writes.** Nothing was edited, committed or pushed, there was no cluster access in this cycle, and no Slurm job ran. Local scratch only, in `/private/tmp/claude-501/review-a2-scratch/`: `my-review-8d086a20.md` (used for the byte check) and `vhb-4122.txt`.