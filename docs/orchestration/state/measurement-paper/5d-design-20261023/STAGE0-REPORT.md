# REPORT: 5D design Stage 0 (0c, then binding 0a and 0b) — STOP (2026-10-24)

**By** the measurement session, under [`STAGE0-BINDING-A.md`](STAGE0-BINDING-A.md), which binds
[`STAGE0-PARTA-DECLARATION.md`](STAGE0-PARTA-DECLARATION.md). Part P passed earlier
([`STAGE0-PRESERVE-REPORT.md`](STAGE0-PRESERVE-REPORT.md)).
- Code: `stage0/stage0_analysis.py` (sha256 `b25ff235…`), `stage0/stage0c_ratio.py` (`9bd66d2b…`),
  `stage0/tasks-0c.tsv` (`09b08c13…`). All three were read from the cluster clone `$B/repo` at `dc1db99b`, clean, and
  their sha256 equal the committed files'.
- Receipts are in [`stage0/receipts-A/`](stage0/receipts-A/), listed with sha256 in `SHA256SUMS`. The ledger is
  [`stage0/LEDGER.tsv`](stage0/LEDGER.tsv).
- `receipts-A/post-run.txt` holds the submit time, file mtimes, the tar's member count and the retrieval cleanup,
  captured on login12. It also transcribes the watchers' output and the binding run's start and end times from the
  session's terminal; those lines are not a cluster capture.
- The 20 new GiBUU pseudo-experiment products (`eavail_shape_a1_s801000…801019.npz`, 3.5 MiB in all) are tracked in
  `receipts-A/`, because the binding JSON names them. Their sha256 equal the JSON's.
- `B=/pscratch/sd/j/josephrb/5d-stage0-20261023`.

**CITABLE FOR:** the binding Stage 0 verdict under the bound rules, its numbers, and its controls.
**NOT CITABLE FOR:**
- a negative scoping verdict. DESIGN §9 needs this binding Stage 0 STOP **and** either an R10 STOP or an R10 pass
  after which Stage 0, rerun with the added information, still stops (DESIGN.md:575-580);
- any statement about R10;
- any reading of the numbers under rules other than the bound ones.

## Result: STOP

| reporting definition | 0a (c_F ≥ 0.60 every family, pooled ≥ 0.68) | 0b (median u* ≤ 8.6 %, ≥ 2 pairs Δχ² ≥ 9) | verdict |
|---|---|---|---|
| **J** (RD1) | **FAIL**: NuWro 0.570, GiBUU 0.541; pooled 0.645 | PASS: 7.83 %; 4 of 4 pairs | FAIL |
| **H2** (RD2) | **FAIL**: GiBUU 0.259; pooled 0.697 passes | PASS: 7.45 %; 4 of 4 pairs | FAIL |

**The verdict.**
- The bound rule is "RD1 if J passes 0a and 0b; otherwise RD2 if H2 passes; otherwise STOP".
- Neither J nor H2 passes, so the binding verdict is **STOP**. The JSON says `"verdict": "STOP"`
  (`receipts-A/stage0-binding.json`, sha256 `df70af43…`).
- Both definitions fail on 0a, calibration transfer. Both pass 0b, usefulness.

**What happens next (DESIGN §9, as bound).**
- A Stage 0 FAIL together with an R10 failure is the stop condition (`STAGE0-BINDING-A.md:40-41`).
- "If R10 has not reported: after a binding Stage 0 STOP, the plan holds and the director is told" (DESIGN §9).
- I found no R10 report on main. Two local branches carry "r10" in their names, `w1r10-contract` and `w1r10-guard`
  (2026-09-04/05). Their diffs against main touch only `campaignctl` and `mnv_guarded_run` tooling, not an R10 test.
  R10's status is the validation lane's to state, not this report's.
  Search: `r10` in file paths and ref names; `R10 (report|verdict|PASS|STOP)` and `reconstruction-information test` in docs/; `R10` in commit messages @ ac6bb791
- No GPU stage is authorized.

## 1. Stage 0c: the D1 repair

**Ratio (login node, 2026-10-24 01:23 UTC).**
- **Control: PASS.** The unrepaired 5D marginal reproduces the committed s5n ratio to a max |r / r_s5n − 1| of
  0.0067 per bin; the tolerance is 0.02. Every E_avail bin is positive. As declared (§3), gen5d's GENIE is a different
  sample from the s5n ratio's, so the control shows the two constructions agree in E_avail shape, not that they are
  identical.
- **New ratio** (GiBUU `gen5d` over flux-repaired GENIE `gen5d_fluxfix/genie_cv_xsec5d_full`), sha256 `c001dce8…`:
  [1.3774, 1.4994, 1.2439, 0.9798, 0.7984, 0.9869, 0.7987].
- **The old s5n ratio** was [1.2239, 1.3250, 1.1066, 0.8749, 0.7258, 0.9435, 1.3879]. The last bin moves from 1.39
  to 0.80.
- **Sensitivities, reported only:**
  - A (flux-repaired GiBUU numerator), `d2d05fc0…`: [1.3689, 1.4916, 1.2396, 0.9779, 0.7986, 0.9910, 0.8039];
  - B (the non-`_full` GENIE denominator), `84187414…`: [1.3698, 1.4910, 1.2370, 0.9744, 0.7942, 0.9822, 0.8174].
  - Both stay within 0.019, absolute, of the primary ratio in every bin **(arithmetic)**. In relative terms, B's last
    bin differs by 2.3 %.
- **The GiBUU deficit (KNOWN_ISSUES row 82), as the declaration requires the report to state.** GiBUU is empty above
  E_ν ≈ 20 GeV, about 5.2 % of σ_CC (`state/s5p/gen5d/README-gen5d-fluxfix.md:146-148`). The deficit is in D1 and in
  the GiBUU truth, old and new alike. GiBUU is the family that fails 0a for both J and H2. Whether the deficit
  contributes was not tested. <!-- absence-ok: scope of this report's own work; no test of the deficit was declared or run -->

**Unfolds: job 60182677.**
- One CPU node, regular QOS (sacct `regular_1`), 8 lines × 32 CPUs concurrently, at deploy `97886770`.
- Submitted 01:23:33 UTC, started 2026-10-24 03:10:45 UTC: 1 h 47 min pending. The queue monitor showed the reason
  "Priority". COMPLETED, exit 0:0.
- **Elapsed 1,629 s (27 min 9 s).** That is 0.45 of the 1.0 node-h cap and 0.70 of the 39-min projection. The
  1.25× guard (cancel at 49 min of RUNNING) did not fire. A first guard ran out of iterations while the job was still
  pending. The second was launched before 02:27:16 UTC and ended when the job left the queue (03:38:11 UTC), so it
  covered the whole run from 03:10:45 (`post-run.txt`, transcribed from the session's terminal).
- **Charged: 0.45250 CPU node-h** (billing 256, a full node), 0 GPU node-h.
- **Lines:**
  - lines 3–7, 4 pseudo-experiments each: 1,608–1,617 s, MaxRSS 10.40–10.82 GiB;
  - lines 0 and 1, the D1 data unfolds: 941 and 939 s, 16.03–16.06 GiB;
  - line 2: 627 s, 10.18 GiB.
  - sacct's K is KiB.

**Controls in the binding run (all PASS).**
- **C0c:** line 0's `xsec_flat` equals `prior_R5fix_prior_d1.npz`'s bitwise. Here d1 ran alone; in `prior_a` it ran
  after d0 in the same process. So the result is order-independent. Line 2's `xsec_flat` and `xtrue_flat` equal s5e's 801000 product bitwise.
- **C6:** all 20 seeds 801000–801019 exist by exact name, carry the new ratio's sha256 and the old product's code
  sha256. The new D1 product is prior d1.

## 2. Binding 0a and 0b (login12, 2026-10-24 03:38:41–03:38:51 UTC, 0 node-h)

**Command.** The declared one (`STAGE0-PARTA-DECLARATION.md` §4 step 4). Exit 0, with the output written to a path
that did not exist before the run. <!-- absence-ok: an observation of this run (ls of the output path before the command, session terminal), not a claim about the record -->

**Controls (all PASS).**

| control | result |
|---|---|
| C1 inputs match the inventory | the JSON's 129 files, which count `prior_R5fix_prior_d1.npz` twice (128 distinct); the N1 base, z-cv and the 50 bootstraps (52 files) are checked separately |
| C2 CV equals the N1 base bitwise; d0 within 1e-5 | true; max relative deviation 2.2e-16 (J, EW), 1.1e-16 (H2) |
| C3 envelope receipt's h medians | reproduced exactly: with D1 12.016 / 9.603 / 13.436 %; without D1 11.245 / 4.277 / 9.899 % (J / H2 / EW) |
| C4 z-cv indexing | rows equal the support mask; 10,694²; every J, H2 and EW cell gets rows; J median a/e 1.0013; projection identity ≤ 1.1e-15 |
| C5 positive definite | every graded covariance |
| C0c, C6 | as in §1 |

**0a: family hold-out, M2 (graded).** κ^(−F) is calibrated on the other families' pairs, and c_F is scored on F's own.

| set | family | κ^(−F) | covered / pairs | c_F | M1 c_F (reported) |
|---|---|---:|---:|---:|---:|
| J | NuWro {d2, d4, d5} | 0.709 | 176 / 309 | **0.570** | 0.553 |
| J | GENIE MEC {d3} | 0.466 | 97 / 97 | 1.000 | 0.990 |
| J | GiBUU {d1new} | 0.485 | 59 / 109 | **0.541** | 0.532 |
| J | pooled | | 332 / 515 | **0.645** | |
| H2 | NuWro | 0.822 | 59 / 79 | 0.747 | 0.734 |
| H2 | GENIE MEC | 0.584 | 26 / 26 | 1.000 | 1.000 |
| H2 | GiBUU | 0.496 | 7 / 27 | **0.259** | 0.296 |
| H2 | pooled | | 92 / 132 | 0.697 | |
| EW (reported, not graded) | NuWro / GENIE MEC / GiBUU | 0.724 / 0.544 / 0.549 | 45/70, 34/34, 16/39 | 0.643 / 1.000 / 0.410 (pooled 0.664) | 0.643 / 1.000 / 0.410 |

**0b: usefulness (graded).** Columns 4–7 are noise-corrected shape-only Δχ² values; the graded covariance is
C_stat(e) + C_model + the z-cv total.

| set | κ* (κ*_0.95) | median u* | W2 | W3 | W1 | GiBUU_new | pass |
|---|---|---:|---:|---:|---:|---:|---|
| J | 0.411 (0.912) | **7.83 %** | 1,310 | 8,499 | 4,236 | 21,569 | PASS |
| H2 | 0.483 (0.880) | **7.45 %** | 129.0 | 460.6 | 239.3 | 1,155.6 | PASS |
| EW (reported) | 0.482 (0.774) | 9.03 % | 416.9 | 1,818.9 | 2,480.8 | 8,147.3 | (would fail the bar) |

- The graded noise terms are at most 5.0 (J, W3); the z-cv-only ones at most 7.2 (J, W3). The total and z-cv-only
  variants are in the JSON. Every J and H2 pair is ≥ 128.9 in every variant (H2 W2, graded shape-only: 128.999).
- M1's κ*: 0.553 (J), 0.561 (H2), 0.652 (EW). Reported only.

## 3. The provisional run (2026-10-24 01:22 UTC; decides nothing)

- **Scope:** two families, D1 excluded. Its verdict was "PROVISIONAL, decides nothing: STOP" (`receipts-A/stage0-provisional.json`,
  `7d9f8d81…`).
- **0a coverage:**
  - J: NuWro 0.129, GENIE MEC 1.0, pooled 0.337;
  - H2: NuWro 0.177, GENIE MEC 1.0, pooled 0.381.
- **0b:** passed for J (6.58 %) and H2 (2.64 %), with 3 of 3 pairs.
- **The binding run's NuWro coverage is higher** (J 0.570, H2 0.747). Two things changed for held-out NuWro:
  - its envelope adds d1new to d3;
  - its calibration set adds the GiBUU_new fold. J's κ^(−NuWro) fell from 1.213 to 0.709.
  - Neither change was tested separately **(reading of the family definitions)**.

## 4. Storage and compute

- **HPSS.** The 0c products went to `/home/j/josephrb/mnv-5d-stage0-inputs-20261023/stage0-0c-products-20261024.tar`,
  beside Part P's tar (`receipts-A/hpss.log`). That is 4,403,200 B and 59 members (`post-run.txt`): the 58
  files of `receipts-A/products.sha256` plus that list. They are `runs/` (47 files: the 23 npz products and their
  inventory and log files), `ratio/`, `logs/` and both JSONs.
  - The tar's sha256 is `ee819f4e…`. `hsi hashcreate` gave md5 `69996ff2…`, and `hsi hashverify` gave "(md5) OK".
  - The copy was retrieved, and its sha256 equals the tar's. The retrieved copy was then deleted: `$B/retrieveA` is
    absent, by absolute path (`post-run.txt`).
- **pscratch.** The products remain under `$B`. Nothing was written to CFS.
- **Compute.** 0.45250 CPU node-h, all of it Stage 0's (ledger). The provisional run, ratio and binding run used 0
  node-h on login nodes.

## 5. What was not done

- No rule, threshold, family, truth set or covariance form was changed after output. No alternative reading was
  computed.
- My read of the 0a and 0b code paths (`stage0_analysis.py:263-328`) against the declaration's §5–6 found no
  departure. So did an independent read-only review, in both directions. Had a defect turned up, it would have gone
  to the director before any re-read.
- **One stale comment.** `stage0_analysis.py:252` labels C_stat(e) "(sensitivity variant only)", but the code grades it,
  as declared. The computation is unaffected. The comment was later corrected at the director's request; see the
  addendum.
- MP-2 stays held. No claim, target or endpoint changes.

## Addendum: the comment fix (2026-10-24, after the merge of PR #296)

At the director's request, `stage0_analysis.py:252` now reads "(graded: part of the 0b covariance, DECLARATION
section 6)". That one comment line is the whole diff; no code changed.

- **The run used the earlier file.** Its sha256 is `b25ff23560a80f1f665d3f728c7400602ea8075e8b6652ad581a80a8f766323d`,
  as recorded in `STAGE0-PARTA-DECLARATION.md`, in this report and in `receipts-A/stage0-binding.json` `code_sha256`.
  That version is the file at `dc1db99b`, the clone the binding run read.
- **The current file's sha256** is `f9248e20f924b91ab5e920137e8efecd357331ad34e708aaf43498292aa9f78e`. A check of the
  file on main against `code_sha256` will therefore differ. Check against `git show dc1db99b:<path>` instead.
- No Stage 0 run follows; the director has held Stage 0.

