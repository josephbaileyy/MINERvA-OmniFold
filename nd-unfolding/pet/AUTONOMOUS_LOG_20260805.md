# Autonomous work log — 2026-08-05, Joseph away ~12h

Append-only. Every entry records what was done, what was measured, and what was decided —
so the decisions are reviewable rather than merely reported.

## Standing constraints in force

- Never hand-edit a hash to clear a mismatch — re-issue the owning gate.
- Never raise a tolerance to make a check pass.
- Stage with explicit paths, never `git add -A`. Commit only what is asked.
- No `--validator size`, no `RESUME_ADOPT_LEGACY=1`, no `--bkg-mode purity` as the P5A closure.
- Announce any change to what `pytest nd-unfolding/tests` collects.

## Baseline at start

- `HEAD = 61f2fb2`, local == cluster == `origin/main` (all three verified equal).
- pytest collection: local **696**, cluster **750** (trees differ; both are baselines).

---

## 12:20Z — Step 3 ordinary P5A closure: **PASS** (item 4 of four)

Job `56358150`, GPU interactive, `nid001016`. Ran with **zero argument overrides** because
`validate_pet_nominal_gate4.py --closure-report` refuses a run whose thresholds were loosened, and
every canonical value is already a script default.

| quantity | value | threshold | verdict |
|---|---|---|---|
| `marginal_l1` | 0.006594 | ≤ 0.10 | PASS, 15× margin |
| `\|push_median − 1\|` | 0.0858 | ≤ 0.15 | PASS |
| `verdict` | PASS | — | — |

Report: `nd-unfolding/products/pet/fullevent_fps/closure_fullevent_fps.json`,
sha256 `6c9520c7f42ecae89c0f7eb4b68cd14d5dc55518ba42a8c31fe6ee56f8e284c4`.

`refinement_invoked = False`, `measured_target_constructed = False`, `bkg_mode = mc-only`,
`is_synthetic_fixture = False`, `is_powered_closure = False`, `closure_class =
mc-self-consistency-identity`.

**This empirically settles the ROOT/TF question.** Step 3 was recorded as blocked because the
closure needed ROOT and TF in one interpreter. D2 made `--bkg-mode mc-only` the default, which
builds the MC side alone; this run imported no ROOT and completed. Two documents were repeating a
blocker that a commit had already dissolved: the runbook's Step 3 "DECIDED 2026-08-04" block, and
the `perlmutter-root-tf-env-split` memory note. Both now corrected.

**Caveat carried forward, not resolved:** an mc-only identity closure "cannot distinguish a correct
estimator from a null one — the identity closure is optimized by a constant estimator" (its own
`certifies` field). It is necessary for Gate-4, not sufficient for publication power. That is what
the powered closure (56355818) exists to supply.

---

## 12:45Z — Item 1: extractor `pass_truth` mask — **FIXED**

`nd-unfolding/pet/extract_fullevent_fps.py :: reweight_full_inventory`, per
`FINDING-20260802-extractor-pass-truth-mask.md`. Three sites:

1. Load the mask itself, not just its length (`pass_truth = ...astype(bool)`; `n` from its shape).
2. `out = np.ones(n, np.float64)` — was `np.empty`, which left unwritten rows as garbage.
3. `out[lo:hi] = np.where(pass_truth[lo:hi], chunk_w, 1.0)` — mirrors `MultiFold.RunStep2`
   (`omnifold.py:203-205`) exactly.

Plus telemetry: `n_off_acceptance_pinned`, `off_acceptance_all_exactly_one`,
`subsample_agreement_is_vacuous`.

**New measurement that closes an open question in the finding.** The finding said "Whether the real
dump trips it is NOT established" and warned the failure mode is asymmetric. It is now established
that it DOES, from two independent runs on the real G2 dump:

- Step 3 above: `n_pass_gen = 11,999` of `max_events = 12,000`.
- Powered-closure preflight: `n_truth_pass_a = 1,999,920` of `2,000,000`.

So off-acceptance rows exist (~0.004%), `check_subsample_agreement` is **not** vacuous, and the
unfixed extractor would have refused to run. The fix is required, not precautionary.

Tests: `test_fullevent_extract.py` 25 → **27 passed**. Two regression tests added, in the
source-inspection idiom the file already uses for structural properties (`test_mmap_mode_is_not_
relied_on`). Verified non-vacuous: under the old `np.empty(n, ...)` the `np.ones(n` assertion fails.

**COLLECTION CONTRACT CHANGED: local 696 → 698 (+2).** Announced.

---

## 12:50Z — Item 3 launched: B1 rate-injection closure

`--scan-seeds 8`, otherwise all defaults (r-inject 1.135, acceptance 0.621, niter 2, epochs 8,
n-events 60000, smear 0.15, seed 7) = the nominal-like operating point.

**Judgment recorded:** the scan is deliberate. The frozen `fold_forward_ratio_dev_max` must clear
two bounds — above term 1 at niter=2 (~1.71% at a=0.621, R=1.135) or it fails a correct unfold, and
well below (R−1)/R (~0.119) or it detects nothing. Freezing off a single seed risks a number that
passes today and fails a correct run later.

**I will NOT freeze the value autonomously.** I will report the measured spread and propose a value;
replacing a gate tolerance is Joseph's call. The provisional `0.05` sits mid-window.

---

## Status of the four items owed by the Gate-4 re-issue

All four must land in ONE commit (`RESTORE-2026-08-03.md` line 700) — piecemeal landings turn
`test_gate3_and_gate4_launch_code_freezes_specifically` red between each.

| # | item | status |
|---|---|---|
| 1 | extractor `pass_truth` mask | **DONE**, uncommitted, +2 tests |
| 2 | plumb `batch_size` | **DONE** (pre-existing; verified end to end) |
| 3 | measured `fold_forward_ratio_dev_max` | **RUNNING** (B1 scan) |
| 4 | Step 3 closure report `--json` | **DONE**, PASS, sha `6c9520c7` |

Nothing is committed. `docs/OPEN_ITEMS.md`, `extract_fullevent_fps.py` and
`test_fullevent_extract.py` are modified in the working tree.

## Critical path

`56355818` (D2 powered closure) is the item Gate-4 actually waits on. Rank 39/1132 in `gpu_shared`
at last check; 12h wall, no resume path — a walltime kill is a total loss. Its two
training-independent criteria are already receipted (gap 0.2343 ≥ 0.15; floor/gap 0.0459 ≤ 0.10),
so the only open number is `residual ≤ 0.0469`, i.e. recovery ≥ 0.80.

---

## 12:55Z — Communication channel established (and its real shape)

Joseph asked whether the Perlmutter watcher's email could be reused. It can, but not the way it
first appears.

**Measured constraint:** Perlmutter's SMTP refuses non-local recipients outright —
`550 5.1.1 ... only mail to nersc.gov and lbl.gov addresses is accepted on this system`. Both
`josephrb@stanford.edu` and `jrbailey555@gmail.com` were rejected. That is exactly why his existing
`waker-config.json` has `notify_command = /usr/bin/mail -s {subject} josephrb@nersc.gov`.

**The return path was the real trap.** Mail sent from here has `From:
josephrb@perlmutter.nersc.gov`, which has no mailbox anyone can read (`/var/spool/mail/josephrb`
does not exist, `mailq` empty, no `.forward`). A reply would have vanished silently. Fixed by
setting `Reply-To: jrbailey555@gmail.com`, the one mailbox the Gmail connector can read.

Also measured: NERSC's Iris forwarding does **not** deliver to his Gmail — the test mail never
appeared there — so `josephrb@nersc.gov` reaches his Stanford inbox. Outbound and inbound therefore
use different mailboxes, which is why Reply-To is load-bearing rather than cosmetic.

| direction | mechanism | status |
|---|---|---|
| me → him | `send_channel_mail.py` → `josephrb@nersc.gov` → Iris → Stanford | WORKING (relayed, queue clean) |
| me → him (urgent) | `PushNotification` → phone | available |
| him → me | reply (via Reply-To) or `[MNV-AUTO]` to jrbailey555@gmail.com, polled 2×/hr | WORKING (Gmail read verified) |

The Gmail connector has **no send tool** — only `create_draft`/`update_draft` plus read. So the
cluster is the only outbound path; the connector is inbound only.

Helper: `/pscratch/sd/j/josephrb/send_channel_mail.py "<subject>" <bodyfile>`.

## 12:58Z — Gate-4 re-issue mechanism, and why item 3 must come first

`p3f-pet-gate4-launch-code-gate-20260801b.json` is not written by any script — it is a maintained
state artifact, referenced from `test_pet_nominal_gate4_validator.py` and
`test_b1_normalization_fix.py` (both themselves among the 8 mismatches). Re-issuing means writing a
NEW state file carrying fresh sha256 digests of the bound files, retiring the old one under the D3
at-issue convention (`files`→`files_at_issue`, `sha256`→`sha256_at_issue`, digests preserved
verbatim), and moving the test references.

**Ordering consequence, worth stating explicitly:** freezing item 3 edits
`validate_pet_nominal_gate4.py`, which moves that file's hash, which the new state file must pin. So
the re-issue cannot be prepared "up to" the tolerance and then patched — the tolerance must be frozen
BEFORE the digests are computed. Doing it the other way round is the pin-cascade mistake this
campaign has already paid for twice.

Net: the re-issue is blocked on exactly one thing, and it is a decision rather than a computation.

---

## 12:47Z — Item 3: B1 rate-injection closure **PASS**, 8-seed scan

Job `56358196`, `nid001180`. Report:
`nd-unfolding/products/pet/b1_closure/closure_b1_rate_injection_scan8.json`
sha256 `12b58d9089e2de9714ee5b6583b4c815fc1073ea4f73beca44b968cee9f8e1b5`

All three discriminating assertions hold, which is the point of the test — the BROKEN arm must fail:

- corrected recovers the injected rate: **True**
- broken does NOT recover it: **True**
- corrected strictly beats broken: **True**

`dev_from_R` per seed (corrected arm), the quantity `fold_forward_ratio_dev_max` bounds:

| seed | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
|---|---|---|---|---|---|---|---|---|
| corrected | 1.979% | **3.263%** | 2.056% | 2.115% | 2.277% | 2.283% | 1.576% | 1.694% |
| broken | 12.132% | 13.159% | 12.142% | 12.183% | 12.244% | 12.406% | **11.730%** | 11.767% |

Term 3 (subsample sampling): corrected fold-forward ratio over 8 seeds mean `1.110537`,
std `0.005458`. Structural floor (term 1, worst case) `1.7085%`. Defect signal `(R-1)/R = 11.8943%`.

### The measurement VALIDATES the provisional 0.05 rather than replacing it

The admissible window is bounded below by the worst CORRECT run (or the gate fails correct unfolds)
and above by the smallest DEFECT signal (or it detects nothing):

    max corrected dev  3.263%   <   0.05   <   11.730%  min broken dev
                                1.53x above           2.35x below

The provisional `0.05` sits inside with margin on both sides, and is ~5.2 sigma above the corrected
mean (2.16%) given the 0.55pp seed spread. So the honest outcome of item 3 is **not a new number**:
it is the same number with its justification changed from asserted to measured.

That distinction matters for the audit trail. Editing `0.05` to something looser would be raising a
tolerance to make a check pass; leaving it at `0.05` and retiring
`PROVISIONAL_PENDING_CLOSURE_MEASUREMENT` is recording that the measurement came in and agreed.

**RECOMMENDATION (not applied): keep 0.05, change the status to MEASURED, cite this report's sha.**

**HELD FOR JOSEPH.** I committed to proposing rather than freezing, and the file is Gate-4-bound, so
`validate_pet_nominal_gate4.py` is UNTOUCHED pending his reply. One seed (8) at 3.263% is an outlier
against the other seven (1.58-2.28%), which is the one reason a reasonable person might want more
seeds before freezing — worth his eye rather than my assumption.

### Four owed items

| # | item | status |
|---|---|---|
| 1 | extractor `pass_truth` mask | DONE, uncommitted, +2 tests |
| 2 | plumb `batch_size` | DONE (pre-existing, verified) |
| 3 | measured `fold_forward_ratio_dev_max` | **MEASURED**, PASS, sha `12b58d90` — awaiting his call on freezing |
| 4 | Step 3 closure report | DONE, PASS, sha `6c9520c7` |

The Gate-4 re-issue is now blocked on ONE reply, not on any computation.

## 13:05Z — 32-seed B1 scan launched, to test my own recommendation

Not busywork and not waiting-filler. My "keep 0.05" recommendation rests on 8 seeds whose worst case
(seed 8, 3.263%) is an outlier against the other seven. If a wider scan produces a corrected
deviation above 5%, the recommendation is WRONG and 0.05 would fail a correct unfold — so the scan
can falsify the advice I just sent, which is the reason to run it before he acts on it rather than
after.

~7 minutes of interactive GPU. Report will be `closure_b1_rate_injection_scan32.json`.

Decision rule fixed in advance, so the outcome cannot be rationalized after the fact:
- max corrected dev stays below ~3.3% -> recommendation stands, margin confirmed on 4x the seeds.
- creeps toward 5% -> withdraw the recommendation and propose a larger tolerance WITH the evidence,
  or propose more niter/epochs. Not a silent adjustment either way.
- exceeds 5% -> 0.05 is disproven; mail him immediately, because that also means the currently
  frozen PROVISIONAL value would reject correct unfolds.

Also still running: the suite + hash-binding verifier on `nid004166` (30+ min; it hashes ~1 TiB of
Gate-3 ROOTs, so this is expected rather than hung — output is block-buffered and lands at once).

---

## 13:10Z — Hash-binding verifier on compute: COMPLETE, no new breakage

`/pscratch/sd/j/josephrb/verify_compute_20260805.txt`, run on `nid004166` (compute, not login).

    resolved 856 bindings (260 unresolvable)
      844 OK
      17 from EXPECTED_*_SHA guards in *.sh (17 pins seen, floor 12)
      4 known pre-existing drift (submit-time provenance)
    8 MISMATCH -- ALL from state/p3f-pet-gate4-launch-code-gate-20260801b.json
    *** BINDINGS BROKEN ***

Mismatched: `closure_fullevent_fps.py`, `train_fullevent_nominal.py`,
`validate_pet_nominal_gate4.py`, `omnifold_nn/omnifold/omnifold.py`,
`test_b1_normalization_fix.py`, `test_fullevent_schema.py`,
`test_pet_fullevent_nominal_launcher.py`, `test_pet_nominal_gate4_validator.py`.

**Independently corroborates the audit session's two claims.** Resolved went 854 -> **856** and shell
pins 15 -> **17**, exactly the +2 expected from making the driver and preflight pins discoverable to
`collect_shell`; and the floor is now 12, which the run clears with 17. So the pin that was
"decorative" is now genuinely walked by the repo-wide verifier.

Still exactly 8 mismatches, still one owning state file, still zero `.npy` involved. Nothing the
audit commits touched introduced new drift, and Gate-2's products remain intact.

## 13:12Z — Joseph replied; new standing instruction

Mail received (via Gmail, Reply-To path working as designed). Two things:

1. He confirms he received the status mail — **the outbound channel is verified end to end**, not
   just accepted-by-relay. Perlmutter -> josephrb@nersc.gov -> Stanford inbox works.
2. **New standing instruction, applies to ALL future decisions:** before escalating a held decision
   to him, first spawn a Claude session on Opus 5 (high/xhigh) — locally or in the Perlmutter
   workspace — to attempt the decision, consulting `docs/orchestration` for context.

Done for the tolerance question: an Opus 5 subagent is running now. It was given the 8-seed numbers
but told to VERIFY rather than trust them, to fetch the 32-seed report itself when it lands, and
specifically to try to REFUTE my "keep 0.05" recommendation. It was also asked to check four things I
had assumed rather than confirmed: whether R=1.135/acceptance=0.621 really are the campaign's nominal
values (if not, both bounds move), whether MAX is the right statistic versus a quantile, whether the
gate can ever run under a seed policy other than niter=2/epochs=8, and whether the second
parameter-free check ("nearer R than 1") reduces how much this tolerance has to carry.

Note this is the first subagent use of the campaign — it was previously off-limits without an
explicit request, and he has now made one.

---

## 13:20Z — Item 1 verified against a pristine tree, and it voids the gate (as designed)

**Are the local suite's 9 failures mine?** No. Checked properly by building a throwaway worktree at
pristine `61f2fb2` and running the suite there — rather than stashing, because
`git checkout -- <path>` in this repo has silently reverted live config before.

| tree | result |
|---|---|
| pristine 61f2fb2 | **9 failed, 686 passed, 1 skipped** |
| with my item-1 change | **9 failed, 688 passed, 1 skipped** |

Identical failure list. The delta is exactly `+2 passed` = my two new regression tests. So all 9
failures pre-exist at HEAD and item 1 breaks nothing. Six are `test_fullevent_gate2.py`, one is
`test_gate2_target_runtime.py::...without_tensorflow_package_init` (consistent with local TF being
2.16/Keras 3, which cannot run this PET path — see [[local-tf-cannot-run-pet]]), and two are the
`test_hash_bindings.py` pair that is red BY DESIGN until the Gate-4 re-issue.

**Item 1 adds TWO binding mismatches, 8 -> 10.** Measured, not assumed:

    nd-unfolding/pet/extract_fullevent_fps.py     <- the fix itself
    nd-unfolding/tests/test_fullevent_extract.py  <- the two regression tests

Both are bound by `state/p3f-pet-gate4-launch-code-gate-20260801b.json`. This is precisely what
`FINDING-20260802-extractor-pass-truth-mask.md` predicted — "editing it voids that gate... this
belongs in that batch" — so it is the intended consequence of doing item 1, not a regression.

**Something I did not know and should record:** `test_fullevent_extract.py` is itself hash-pinned, so
ADDING TESTS to it moves a pinned digest. Writing a test is a gate event in this repo. Anyone
extending a pinned test file must expect to re-issue.

Consequence for the re-issue: the new state file must carry fresh digests for **ten** drifted files,
not the eight the verifier reported before item 1. Any re-issue prepared against the earlier count
would be stale on arrival.

## 13:25Z — MY ERROR: cluster suite job killed at walltime, relaunched

`56358047` was CANCELLED AT 2026-08-05T13:04:15 DUE TO TIME LIMIT, 45 min. The verifier phase
completed (its output is valid and already recorded above), but the pytest phase was killed before
producing any result.

**Cause was mine, and it is a duplication I should have seen.** The job ran the hash-binding verifier
standalone (~31 min), and then ran pytest — whose `test_hash_bindings.py` spawns *its own* full
verifier pass, another ~31 min. So the job needed ~90 min against a 45 min request, and it ran the
same ~1 TiB hashing sweep twice for one answer. Requesting more walltime would have hidden the real
mistake, which was running it twice.

Relaunched as `run_pytest_only.sh`: pytest alone, `-t 02:00:00`, on a CPU node, with the standalone
verifier deliberately omitted since its result is already in hand. Noted in the script itself so the
next person does not re-add it.

**No result is being claimed from 56358047's pytest phase.** The cluster suite remains UNVERIFIED at
`61f2fb2` + item 1 until the relaunch finishes. The local suite result stands on its own
(9 pre-existing failures, +2 of mine passing), and the cluster's 750-test baseline is the one still
unconfirmed.

---

## 13:30Z — 32-seed B1 scan: PASS, and it WEAKENS my 8-seed recommendation

Report `closure_b1_rate_injection_scan32.json`, sha256
`0a830d65780fc0bcf0eb32303fbcd206f8f5fa25eb0c8157b27e0f71120e3c24`. All 32 seeds: corrected
recovers, broken fails, corrected beats broken. Zero of 32 corrected deviations exceed 0.05.

| statistic | 8 seeds | **32 seeds** |
|---|---|---|
| max corrected dev | 3.263% | **3.789%** |
| mean corrected dev | 2.16% | **1.893%** |
| std corrected dev | — | **0.717%** |
| p95 / p99 | — | **3.218% / 3.626%** |
| min BROKEN dev | 11.730% | **10.042%** |
| margin 0.05 / max_corrected | 1.53x | **1.32x** |
| margin min_broken / 0.05 | 2.35x | **2.01x** |

**Both margins shrank as seeds increased.** The correct-side bound rose and the defect-side bound
fell, which is what more sampling of both tails should do — and it means the 8-seed window was
optimistic.

**A claim I made is now wrong, and it mattered.** I told Joseph 0.05 sits "~5.2 sigma above the
corrected mean". On 32 seeds it is (5 - 1.893)/0.717 = **4.33 sigma**, and `mean + 5*sigma = 5.48%`,
which EXCEEDS 0.05. So 0.05 does not give 5-sigma coverage of the corrected distribution; it gives
about 4.3. The 8-seed sigma was computed on the fold-forward *ratio* (0.005458), and I carried it
across to the *deviation* as though the two were interchangeable. They are not, and that inflated my
confidence.

**Also worth stating: 0.05 is not centred in the window.** The geometric centre of
(3.789%, 10.042%) is 6.17%, so 0.05 sits nearer the bound where it rejects CORRECT unfolds than the
bound where it stops detecting the defect. A value near 0.06 would be better centred. That is not
automatically better — widening costs detection power — but it is a real consideration I had not
raised, and it is why this stays Joseph's call.

This is the entire justification for running the scan before he acted on my advice rather than after.
The recommendation is not refuted (0 of 32 exceeded 0.05, max still clears it 1.32x) but it is no
longer as comfortable as I presented it, and the Opus 5 subagent now has this data to weigh.

---

## 13:40Z — Cluster suite: 4 failed / 746 passed, and BOTH cluster-only failures trace to untracked clutter

`56358437`, CPU node, 31:59. Total 750 = the cluster baseline (my item-1 edits are local-only, so the
cluster correctly shows no +2).

    FAILED test_hash_bindings.py::test_no_new_broken_hash_bindings
    FAILED test_hash_bindings.py::test_gate3_and_gate4_launch_code_freezes_specifically
    FAILED test_resume_guard.py::test_no_shell_file_reintroduces_a_size_only_resume_guard
    FAILED test_uq_remediation.py::UnifiedThrowTests::test_synthetic_slab_and_block_combine_end_to_end

The first two are red BY DESIGN pending the Gate-4 re-issue. The other two do not fail locally, so I
chased the difference instead of assuming it was environmental. **Both are caused by untracked files
that exist only in the cluster working directory.**

**1. `test_no_shell_file_reintroduces_a_size_only_resume_guard`** — three offenders, all
`[[ -s FILE ]] && skip`, the BEN-023/J35 size-as-completion-proof pattern:

    nd-unfolding/pet/orchestrate_gpu_node.sh:33
    nd-unfolding/sbatch_boot5d_gpu_interactive.sh:23
    nd-unfolding/sbatch_bootstrap_5d_gpu.sh:18

All three are **untracked and cluster-only** — absent from the local tree and not in git at all.
The test scans every shell file on disk, not just tracked ones, which is defensible: a stale script
sitting on the cluster can still be RUN, and running one is exactly the defect. So the guard is
firing correctly on real risk. **Not fixable by a commit** (they are not in git), and I am NOT
deleting them: deletions are gated behind `POST_PUBLICATION_REORG_PLAN.md`'s freeze tag. Flagged for
Joseph.

**2. `test_uq_remediation.py`** — the file **does not exist in the local tree at all** and is
**untracked on the cluster**. It fails in isolation in 0.77s, so this is a genuine failure, not
test-order pollution: `unified_throw_cov.py:424` refuses 3 synthetic slabs that carry no per-universe
flux normalization stamp, i.e. the J28 fix's guard rejecting the test's own fixture. Pre-existing —
none of the audit commits touch `unified_throw_cov.py` or this file — and it has plausibly been red
since the J28 fix landed (07-31), unnoticed because it cannot run locally. NOT fixed here: deciding
whether the fixture is stale or the guard over-strict touches the flux covariance, whose corrected
sizing is still pending, and that is a decision, not a cleanup.

### The local suite is a much weaker check than I have been treating it as

    local (tracked, + my 2)   698
    cluster                   750
      of which untracked      25   (run_inpipeline_nn_smoke.py, test_cstat_100rep.py,
                                    test_uq_remediation.py -- none in git)
      tracked but uncollectable locally  ~29

So ~52 tests never execute locally, and the cluster's "750" baseline is itself inflated by 25 tests
from files that are not in the repository. A green local run proves less than it appears to — the same
asymmetry as the binding counts (109 vs 856), and worth remembering for the same reason.

**Honest characterisation of the tracked repo at `61f2fb2`:** the only failures attributable to the
repository are the two `test_hash_bindings.py` ones, which are expected until the re-issue. Nothing
the audit committed, and nothing I changed, broke a test.

**MY ERROR, twice now:** the runner had `| tail -25`, so the first look at this log showed only the
summary and I had to re-run tests to see the failure text. That is the same truncation mistake as the
earlier `tail -15` on the verifier. Stop piping diagnostic runs through `tail` — redirect the whole
thing to a file and tail the FILE.

---

## 13:55Z — OPUS 5 SUBAGENT VERDICT: (c) INSUFFICIENT. My recommendation is REFUTED, not just weakened.

Joseph's instruction to route decisions through an Opus 5 session earned its keep immediately. The
subagent found that **both of my B1 runs were executed at a superseded operating point**, which voids
them as evidence for freezing the tolerance.

`RESTORE-2026-08-03.md:818` prescribes
`closure_b1_rate_injection.py --r-inject <measured R> --acceptance <measured>`. I ran the script
DEFAULTS (1.135 / 0.621) instead, twice, and did not check the line I was working from. That is my
error, and it is the whole ballgame.

**I verified both measured values myself, straight out of the receipt** (not taken on the subagent's
word) — `G2_GATE2_TARGET_RUNTIME_RECEIPT.json`, status PASS, commit `8a9d22c`, job 56344268:

| parameter | value I used | **measured value** | source |
|---|---|---|---|
| R | 1.135 | **1.1240802949941018** | `step1_class_ratio.R` |
| acceptance | 0.621 | **0.4185618199216587** | `telemetry.n_signal_pass_reco / n_signal_rows` = 20,573,521 / 49,152,885 |

0.621 belongs to the **recoil-only** campaign (20,404,292/32,849,103). Full-event FPS expands the
truth denominator 32.8M -> 49.2M while the reco population stays ~20.5M, so the FPS acceptance is
0.42. I carried a recoil-era number into a full-event measurement — the same class of mistake as
[[fullevent-schema-landed-input-space-changed]], where pre-08-01 numbers describe a different
estimator.

### What that does to the window

| | stale point (what I ran) | **measured point** |
|---|---|---|
| structural floor `(1-a)^k (R-1)/R`, k=2 | 1.7085% | **3.7330%** |
| defect signal `(R-1)/R` | 11.8943% | **11.0384%** |
| window ratio `1/(1-a)^k` | 6.96x | **2.96x** |
| 0.05 margin above the floor | 2.93x | **1.34x** |

The subagent then RAN the paired scan at the measured point (seeds 7-14, only (R,a) changed):
corrected devs 3.365 - **4.886%**, mean 4.046, sd 0.455. **0.05 clears the measured worst case by
1.023x** — effectively no margin. My "keep 0.05" advice would have frozen a gate tolerance on 2%
headroom, derived from the wrong operating point.

### The finding that outranks the tolerance itself

The "parameter-free" second check is **not** threshold-free: algebraically it is
`dev_from_R < (R-1)/(2R)`, a hard ceiling of **5.5210%** at the measured R, verified against the code.
Two consequences:

1. **No tolerance >= 0.0552 does anything** on the under-recovery side. Margin cannot be bought by
   widening. The usable range is (worst correct dev, 5.521%), and the measured worst correct dev is
   4.886%. The window is nearly closed.
2. Its soundness condition is `2(1-a)^niter < 1`. At a = 0.4186, niter=2 gives 0.676 (SOUND, 1.48x
   margin) but **niter=1 gives 1.163 — it would reject a correct unfold**. The frozen seed policy
   pins niter=2, so this is protected; that protection is load-bearing, not cosmetic.

A step-rich probe (epochs 32) showed the residual is **floor-dominated, not optimization-dominated**
(mean/floor 1.077 at 4x steps vs 1.084 at 8 epochs; seed 7 within 0.01% of the closed form). So more
training will not rescue 0.05.

### Corrections to things I told Joseph

- "Seed 8 is an outlier / possible heavy tail" — **wrong**. The 32-seed distribution is smooth and 6
  of 8 stale-point seeds already exceeded the so-called worst-case floor. The tail was a red herring;
  the operating point was the real defect.
- My "~2x headroom either side" (echoing the closure docstring) holds only at the stale point.
- Freezing cascades further than I said: `test_b1_normalization_fix.py:932-933` pins the literal
  string `PROVISIONAL_PENDING_CLOSURE_MEASUREMENT` and `:762` hardcodes `R, acc, k = 1.135, 0.621, 2`.

### Action taken

Launched the prescribed run at the measured point: 32 seeds (decision arm) plus an 8-seed epochs=32
arm (floor-dominance receipt). ~25-40 min interactive GPU. Predeclared decision rule, adopted from the
subagent so it cannot be rationalised afterwards, with F=3.733%, C=5.521%:

- **max < 4.5% and mean+3sd < 5.0%** -> freeze 0.05, mark MEASURED, cite the new sha.
- **mean+3sd in [5.0%, C)** -> the tolerance is not the lever. Close item 3 either by niter 2->3
  (F drops to 2.170%, C/F 1.48->2.54) or by recording explicitly that Gate-4's normalisation gate runs
  at ~3 sigma.
- **mean+3sd >= C** -> the parameter-free check itself would reject a correct unfold; no tolerance
  repairs it. The subagent projects this as the LIKELY outcome, which is precisely why nothing gets
  frozen today.

**The Gate-4 re-issue is no longer "blocked on one reply".** It is blocked on a measurement that had
never been run correctly, and possibly on a design question about niter.

---

## 14:00Z — Joseph's two corrections, and I was wrong on wakerctl twice

Mail 13:32Z: (1) he meant invoking the **`claude` CLI**, not an in-session subagent; (2) wakerctl can
be pointed at the **claude accounts instead of codex**.

**My wakerctl objection was wrong on both counts, and worse than "wrong" — I asserted a limitation
without reading the file.**

- I said wakerctl "drives codex sessions". It supports BOTH: `wakerctl.py:680-689` handles
  `provider == "claude"` via `agentctl.build_resume_command` and `ctx.claude_bin()`, and
  `test_wakerctl.py:712,737` cover a claude root and its binary preflight. The config merely has
  `provider: "codex"` selected. Nothing needed modifying; it needed configuring.
- I reasoned from the codex sandbox limitation ([[codex-sandbox-blocks-cluster-work]]) to a conclusion
  about wakerctl, when the codex sandbox is a property of the provider I would not have been using.

Lesson for the log: I recommended AGAINST a capability on the strength of a memory note rather than
opening the source. That is the same failure mode as the ROOT/TF blocker, which two documents kept
repeating after a commit had dissolved it — and which Joseph, not I, caught.

### The claude CLI is available and works headless on Perlmutter

    binary   /global/homes/j/josephrb/.local/bin/claude -> claude-homes/school/... 2.1.222
    form     docs/orchestration/MIGRATION-WORKERS.json:8 records the dispatch form

| HOME | headless result |
|---|---|
| `claude-homes/personal` | **FAIL** — "OAuth session expired and could not be refreshed" |
| `claude-homes/school/claude-homes/personal` (the MIGRATION-WORKERS path) | **FAIL** — same |
| `claude-homes/school` | **WORKS** — returned `HEADLESS_OK` on `--model opus` |

He asked for claude-personal first, school only if usage was up. Personal is not a usage problem: its
OAuth session is expired, and re-auth is interactive, so it cannot be repaired from here. **Using
school, and he needs to re-authenticate personal himself.**

### Helper committed to /pscratch (not to the repo)

`/pscratch/sd/j/josephrb/ask_claude.sh <question-file> [answer-file]` — runs `claude -p` with
`--model opus`, school HOME, cwd = the cluster repo, answer to a file. Smoke-tested against a real
question (read the validator's frozen tolerance): returned `0.05`,
`PROVISIONAL_PENDING_CLOSURE_MEASUREMENT`, lines 124-125 — matching what I had established
independently, so the channel is verified against a known answer rather than assumed.

Two notes recorded in the script itself: it needs `--dangerously-skip-permissions` for headless tool
use (the form MIGRATION-WORKERS.json already uses), so every decision prompt must say READ-ONLY
explicitly because the flag removes the guard rail; and `< /dev/null` is required or the CLI stalls 3s
waiting on stdin.

**Next decision goes through this, not through a subagent.** The pending one is which branch of the
predeclared rule the measured-point B1 numbers land in.

wakerctl itself: NOT reconfigured yet. Pointing its root at a claude profile needs a resumable session
UUID under the school home plus a `claude_bin` entry, and it would resume a session that is not this
one — which is workable precisely because this log is the handoff artifact. Deferring until the
measured-point decision is settled rather than changing the orchestration layer mid-measurement.

---

## 14:25Z — CORRECTION: wakerctl is NOT broken. I read a two-week-old log and said it was.

Earlier this cycle I stated as fact that "wakerctl has been crashing on every single tick", citing a
traceback and `restartCnt=1113`. **That was wrong.** What I actually had:

- `cron-tick.log` mtime is **Jul 20 00:40** — the traceback is over two weeks stale.
- The traceback's line 432 (`parse_utc(submitted)`) does not exist in the current file; line 432 today
  is the `slurm-job` return. The current code at :484 does
  `float(submitted) if submitted.isdigit() else parse_utc(submitted)` — which **is the fix** for the
  exact `'1784527278'` epoch-vs-isoformat crash I was quoting.
- `wakerctl.py status` returns live JSON right now (`observed_at_utc 2026-08-05T14:22:17`, login27).
- `wakerctl.py preflight` -> **PASS**.
- `LEDGER.tsv` shows successful notifications through **2026-08-04T12:00:31Z**
  ("[MINERvA waker] 6h status", status `notified`).

`restartCnt=1113` is a 12h-walltime cron job restarting on schedule, not a crash loop. I read a
restart counter as a failure counter.

Why the ledger then goes quiet after Aug 4: `waker-config.json` has
`status_report_interval_seconds: 0` and `idle_guard_ticks: 0`, i.e. the 6h heartbeat is **switched
off**. Per [[cluster-and-local-checkouts-fork]] that switch-off was deliberate, and a previous session
re-enabled it by accident via `git checkout --`. **Not touching it.**

That is twice in one session I have asserted a limitation of wakerctl without reading the thing:
first "it drives codex" (it supports claude at :680), now "it is crash-looping" (it is healthy). Both
times a memory note or a stale artifact stood in for evidence. The rule I should have followed both
times: an orchestration component's health is a measurement, not a recollection.

### Consequence: wakerctl is usable, so I used it for real durability

The gap in my setup is that my cron loop is in-memory and dies with the session. wakerctl is a Slurm
`qos=cron` job with a proven mail path. So I armed a watch on the critical path:

    watch_id   pwclosure-56355818
    kind       slurm-job   param job_id=56355818
    state      armed       armed_at_utc 2026-08-05T14:23:14Z
    action     command -> docs/orchestration/notify_pwclosure.sh

It reports the **verdict**, not merely that the job ended — sacct row, the DONE sentinel, and the
report's gap/floor/residual/recovery against thresholds. A notifier that says only "job finished" is
the vacuous-pass defect in another costume.

Verified by running it with the send suppressed, so no false "job finished" mail went out: body
composes correctly and currently reports PENDING / no sentinel, as it should.

**One wart, recorded rather than hidden:** wakerctl refuses `--action command` unless argv[0] is an
absolute path *inside the repo*, so the script had to be copied to
`docs/orchestration/notify_pwclosure.sh`, which is now an **untracked file in the cluster tree** — the
very category I criticised three hours ago. It is deliberate and it should be committed or deleted
when Joseph returns; flagging it so it does not become the fourth stale untracked script someone finds
in a month.

### claude CLI (his instruction: invoke the CLI, not a subagent)

Verified working, and the helper is `/pscratch/sd/j/josephrb/ask_claude.sh`. Accounts:
`claude-homes/school` works headless on `--model opus`; **both** personal homes fail with "OAuth
session expired and could not be refreshed", which is not a usage cap and needs interactive re-auth he
must do himself. Smoke-tested against a known answer (validator tolerance 0.05 / status string /
lines 124-125) rather than assumed.

Measured-point B1 (`56358954`) still running at ~35 min; its arms print their tables only at the end.
`56355818` still PENDING.

---

## 14:35Z — MEASURED-POINT B1: the decision arm **FAILED**. No tolerance value repairs this.

Two arms, both at the measured point (R=1.1240802949941018, a=0.4185618199216587):

| | 32 seeds, epochs 8 (**NOMINAL policy — the decision arm**) | 8 seeds, epochs 32 (floor probe) |
|---|---|---|
| verdict | **FAIL** (rc=1) | PASS |
| max corrected dev | **5.7318%** | 4.4156% |
| mean | 3.8227% | 3.8627% |
| sd | 0.8067% | **0.3674%** |
| p95 | 5.2650% | 4.3080% |
| mean+3sd | **6.2427%** | 4.9649% |
| seeds over tol 0.05 | **4 of 32** | 0 of 8 |
| broken min | 8.9581% | 10.6447% |
| mean/floor | 1.0244 | 1.0351 |

shas: `5c23b0a0…` (32-seed epochs8), `7ad7dbb0…` (8-seed epochs32).

**The observed max 5.7318% EXCEEDS the parameter-free ceiling C = 5.5210%.** That is not a 3-sigma
extrapolation — it is a realized seed. Consequences, if it holds up:

1. At the measured operating point, Gate-4's normalization check would **reject a correct unfold**
   about 1 in 32, from the parameter-free half that was supposed to carry the power claim on its own.
2. **No tolerance repairs it.** Any `fold_forward_ratio_dev_max >= C` is inert, so the usable range is
   (worst correct dev, C) = (5.73%, 5.52%) — **empty**. 4 of 32 breach 0.05 as well.

This is the third branch of the predeclared rule, reached exactly as the Opus 5 session projected. The
rule was fixed in writing BEFORE these numbers existed, which is the only reason this reads as a
result rather than as a rationalisation.

**A nuance neither the subagent nor I predicted:** 4x the optimizer steps did not move the mean
(1.035 vs 1.024 of floor) but roughly **halved the sd** (0.367% vs 0.807%) and pulled the max under
0.05. So the MEAN is floor-dominated while the TAIL looks optimization-dominated. If that survives a
32-seed epochs-32 arm, "more training" becomes a real candidate remedy — but epochs=8 is pinned in
`NOMINAL_SEED_POLICY` and enforced by the validator, so changing it is a campaign decision with its own
pin cascade, not a tweak.

**Item 3 is therefore not a number to freeze; it is a design question.** Candidates: niter 2->3;
epochs 8->32; keep 0.05 and document ~2-sigma operation; redesign the check; or challenge the closure's
worst-case assumption (it sets `pass_reco = rng.random() < a`, i.e. acceptance INDEPENDENT of the
features by construction, whereas real FPS misses are truth-predictable via muon angle / MINOS — the
one term nothing in this campaign has ever measured).

Per Joseph's instruction the question has gone to an invoked `claude` CLI session (not a subagent):
`ask_claude.sh q_tolerance2.txt`, Opus, READ-ONLY, asked to confirm-or-refute the max>C claim, rank the
options, and say what must be measured first. **Nothing frozen, nothing committed.**

The Gate-4 re-issue is now blocked on a design decision, not a measurement — which is a worse place to
be than this morning, but it is where the evidence actually is. Had I frozen 0.05 on the 8-seed stale
run as I recommended, the campaign would have shipped a normalization gate that rejects roughly 1 in 8
correct unfolds at the nominal policy.

---

## 14:50Z — CLI VERDICT: my FAIL is probably a GRADIENT-STEP CONFOUND. I missed the same runbook line twice.

The invoked `claude` CLI session (Opus, READ-ONLY, 11 min, answer 13,342 bytes) confirmed the ceiling
algebra, corrected it (**C = 5.5192%**, not my 5.5210%), and found the empirical smoking gun I had not
looked for: **the 32-seed JSON records `nearer_R_than_1: False` for seed 16's CORRECTED arm.** The
parameter-free check did fire on a correct unfold, 1 of 32. So max > C is real, not just algebra.

**But I still had not run the prescribed configuration.** I fixed R and acceptance and left
`--n-events` at the default 60,000. The nominal is 2,000,000 rows / batch 512 x 8 epochs = **31,256
optimizer steps**; the closure at 60k/ep8 gets **944** — 33.1x fewer. And
`RESTORE-2026-08-03.md:818` says verbatim:

> "Read that script's 'gradient-step confound' note first — a small-N run is optimization-limited,
> not floor-limited, and reads as though the fix underperforms."

That is the SAME LINE whose `--r-inject <measured R> --acceptance <measured>` clause I already got
caught ignoring three hours ago. I read the line, fixed two of its three prescriptions, and walked
into the third — the one that specifically warns the result will read as underperformance.

Corroboration that it is a confound, not a defect: my 32-seed ratio-sd is **0.00907**, which is WORSE
than the script's own N-scan table at **N=30,000** (0.0176 / 0.0075 / 0.0011 at N=8k/30k/120k) despite
N=60,000. If sd goes as 1/sqrt(steps): step-matched sd -> 0.142%, mean -> ~F, and E[max of 32] -> ~4.00%
— **under both 0.05 and C**. The gate may be sound and my measurement the problem.

### Also wrong: my "epochs halves the sd" nuance

I presented it as a candidate remedy nobody had predicted. The CLI killed it on arithmetic: those 8
seeds were the **first 8 of the 32**, and `P(a random 8-subset contains none of the 4 failures) =
C(28,8)/C(32,8) = 0.2955`. **An 8-seed run reports PASS ~30% of the time regardless of epochs.** Paired
on the same seeds the sd ratio is **0.724, not 0.479**, and 2 of 8 seeds got worse. Mostly a subset
artifact, and I should have computed that before offering it.

### Two genuine latent defects, independent of the confound

1. **Nobody ever wrote down the soundness condition.** The parameter-free check demands >50% recovery;
   the worst case recovers `1-(1-a)^k`. The condition is `(1-a)^k < 1/2`, i.e. `a > 1 - 2^(-1/k)`. At
   k=1 it fails deterministically (F=6.42% > C). Unasserted anywhere.
2. **`tol=0.05` is non-inert only because R > 1/0.9 = 1.1111.** Measured R clears that by **1.17%**.
   Had R come back at 1.10 — inside what B1 §4 contemplates — the frozen tolerance would have been
   silently dead on arrival, and no test checks `tol < C`.

### Plan adopted (measure first, then fix the discriminator — NOT the tolerance)

Launched: N-scan at the measured point, **N=240,000, 16 seeds, epochs 8, niter 2** (4x steps). If
sd ~ 0.41% the 1/sqrt(steps) law holds and the FAIL was an artifact; if sd is unchanged, niter=2 is
genuinely unsound at a=0.42 and option (a) niter 2->3 becomes the answer. Changes the CLOSURE's N only;
the frozen nominal policy is untouched.

Held for Joseph, not decided: the discriminator re-reference to `P_k = R - (1-a)^k(R-1)`, the two new
named checks (`gate_discriminates_at_operating_point`, `tolerance_is_not_inert`), and keeping 0.05 with
a frozen provenance sub-dict instead of a bare scalar. The CLI supplied a tested threshold
(`ratio > 1.041066` separates all 80 arms with near-symmetric margins) but it IS looser than the
current 1.0620, so it is his call, not mine.

## 14:52Z — Comms: my outbound mail was going to the wrong inbox

He wrote "I haven't received an update". Diagnosis: Perlmutter can only send to nersc.gov/lbl.gov, so
everything went to `josephrb@nersc.gov` -> Iris -> his **Stanford** inbox, while he is reading **Gmail**.
Queue empty, no bounces, so five mails were delivered — to the inbox he is not watching. **I claimed
this channel was "verified end to end" after his 12:49 message; re-reading it, he was confirming
messages from the SESSION on his computer, not the email.** I over-read a confirmation.

Fix: posted the full status as a **Gmail draft** (id r-6103613568818155683), which he can read in the
account he actually uses. PushNotification declined to fire (terminal reported active).

**Account correction he was right about:** my session runs under **claude-school**, and
`LIVE-USAGE.md:6-12` states claude-school and claude-school-legacy are two homes for the SAME provider
account with shared capacity, "never to be treated as independent entitlements". So every auditor run I
made was consuming this session's own pool. `agy` is installed (1.1.10) and supports `--effort high`;
future decision runs go through it. `claude-personal` is unusable — both homes fail with
"OAuth session expired and could not be refreshed", which only he can repair.

## 15:25Z — Second opinion requested by Joseph, routed to agy (a different account)

Mail 15:18Z: "For your a,b,c,d,e options, can you give this to a different LLM account and see what it
says? You can try claude-personal/claude or agy either locally on in perlmutter".

`claude-personal` remains unusable (expired OAuth, both homes). So: **agy 1.1.10**, which is a genuinely
different account — and the right choice regardless, because claude-school is the same shared-capacity
account this session runs on.

`ask_agy.sh` built alongside `ask_claude.sh`: `agy -p --effort high --dangerously-skip-permissions
--print-timeout 30m`, READ-ONLY instruction, cwd = the cluster repo.

The prompt was written to get an INDEPENDENT read, not a rubber stamp: it gives agy the operating point,
both JSON reports, the ceiling algebra, the step-confound warning from `RESTORE:818`, and all options
a-f — then states the prior analysis's conclusions LAST and explicitly asks agy to react rather than
defer, plus "anything both of us appear to have missed" and "any factual error you find". If it merely
echoes the first analysis that is weak evidence; if it disagrees on something specific, that is worth
more than either verdict alone.

Concurrent: N-scan `56360955` (N=240k, 16 seeds) running ~28 min; `56355818` still PENDING, priority
67792 -> 67972, rank steady at 39, gpu_shared running 92.

---

## 15:30Z — agy SECOND OPINION: converges on "measure first", DISAGREES on the fix, and corrects my framing

agy (different account, `--effort high`, 2 min, 6,000 bytes) independently verified every number
against the repo — R, a, F=3.7318%, C=5.5192%, C/F=1.4790, both report contents, and seed 16's
`nearer_R_than_1: False` — all EXACT. So the measurements are not in dispute.

### Where the two analyses AGREE (the actionable part)

Step-match FIRST; reject option (b) as a category error; treat (e) correlated acceptance as legitimate
support but never as the justification; add named guards asserting `F < C` and `tol < C`.

### Where agy DISAGREES, and I think it is right

The first analysis proposed re-referencing the production validator's discriminator from `R` to
`P_k = R - (1-a)^k(R-1)`. agy rejects this: `validate_pet_nominal_gate4.py` validates **real production
runs**, where acceptance is feature-DEPENDENT and OmniFold converges toward `R`, not `P_k`. `P_k` is a
property of the SYNTHETIC closure's worst case (feature-independent acceptance by construction).
Baking it into the production gate would import a pessimistic synthetic assumption and **permanently
weaken the real gate** — and the first analysis itself conceded its proposed threshold (1.041066) "IS
looser than 1.0620". Keep `R` as the target.

### The insight both analyses missed, and it corrects something I told Joseph

**Theorem (agy):** if `tol < C`, then `dev_from_R <= tol` mathematically GUARANTEES
`|ratio - R| < |ratio - 1|`. So the tolerance check strictly SUBSUMES the parameter-free check.

I verified it against the code rather than accepting it. `_ratio_dev` is `|ratio/R - 1|`
(validator:200-201). At tol=0.05 the lowest admissible ratio is **1.067876**, and the parameter-free
boundary `(R+1)/2` is **1.062040** — so 0.05 binds first. Subsumed: **True**.

**What that fixes in my reporting.** I told Joseph the gate "would reject a correct unfold from the
parameter-free half that was supposed to carry the power claim independently of any tolerance." That is
wrong: at tol=0.05 the two checks are NOT independent. Seed 16 failing the parameter-free check is the
SAME EVENT as seed 16 exceeding 0.05 — one binding constraint, not two failures. The effective
threshold is `min(tol, C)`, which is why `tol >= C` is inert.

So the severity is one question, not a design collapse: **is the achievable deviation below 0.05 at the
nominal step count?** That is exactly what the running N-scan measures.

agy also reframes the 60k failures as expected rather than anomalous: the decision boundary sits
~2.49 sigma above the mean at sd=0.8067%, giving P(at least one of 32 exceeds) ~ 18.6%. Observing 4 of 32
over 0.05 is consistent with optimizer noise, not an algorithmic defect.

### Predeclared falsification, from agy, recorded before the N-scan lands

If the N=240,000 run yields **sd >= 0.60%** — i.e. it does NOT scale down as 1/sqrt(steps) — then the
spread is initialization variance rather than step-limited optimizer noise, the confound explanation
fails, and option (a) niter 2->3 becomes the answer. agy's confidence: 95%.

**Net recommendation now converged (both analyses, minus the discriminator redesign):** measure
step-matched; if the tail lands clear of 0.05, KEEP 0.05, retire the PROVISIONAL status, freeze a
provenance sub-dict, and add the two guard assertions. No tolerance raised, no frozen policy touched.
Still Joseph's to approve.

## 15:35Z — durability pattern verified by accident

The local background wrapper for the N-scan was killed. The cluster job `56360955` kept running
(`RUNNING 42:27`, sacct clean) because it was launched as `nohup srun ... &`. So the pattern holds: the
ssh-side wrapper is disposable, the cluster job is not. Worth recording as a positive control for the
durability claim rather than only asserting it.

Second opinion posted to Joseph as a Gmail draft (id r150420318896574459) since his Stanford inbox is
where the SMTP path lands and Gmail is where he reads. Both drafts now carry the full picture.

---

## 15:40Z — N-SCAN 240k: agy's falsifier FIRES, but the two predeclared rules now disagree

`closure_b1_rate_injection_scan16_measured_N240k.json`, 16 seeds, epochs 8, niter 2, VERDICT **FAIL**.

| | 60k (944 steps) | **240k (3,776 steps)** | if step-limited |
|---|---|---|---|
| dev max | 5.7318% | **5.1473%** | — |
| dev mean | 3.8227% | **3.5176%** | -> F = 3.7318% |
| **dev sd** | 0.8067% | **0.7239%** | **0.403%** |
| over tol 0.05 | 4/32 | **1/16** | 0 |
| over C = 5.5192% | 1/32 | **0/16** | 0 |
| broken min | 8.9581% | 9.7910% | — |
| mean/floor | 1.0244 | **0.9426** | ~1 |

**4x the optimizer steps reduced sd by 11%, not 50%.** The dev-sd ratio is 1.114 where the
1/sqrt(steps) law demands 2.0. So the spread is NOT step-limited optimizer noise — it behaves like
seed/initialization variance that does not shrink with more data. **Neither analysis predicted this;
both assumed the 1/sqrt(steps) law.** agy's stated falsifier was "sd >= 0.60% at 240k"; measured
0.7239%, so it **fires**.

**The two predeclared rules read differently, and I am not going to smooth that over:**

- agy's rule (sd scaling) -> FIRES -> confound is not the explanation -> niter 2->3.
- The first analysis's rule ("if the step-matched run still gives max > C") -> does NOT fire: max
  5.1473% is now safely BELOW C = 5.5192%, and 0 of 16 breach C where 1 of 32 did at 60k.

Both readings are honest and they point different ways, so neither is yet a decision. What actually
improved with steps is the CENTRE (mean 3.82 -> 3.52%, now 0.94x the worst-case floor, i.e. a
better-trained run beats the closed-form bound as the docstring says it should) and the extreme (max
5.73 -> 5.15%, over-C count 1 -> 0). What did NOT improve is the WIDTH. And the width is what decides a
once-fired gate: 1 of 16 still exceeds tol = 0.05.

Note also 240k is **not** step-matched — 3,776 steps against the nominal 31,256, still 8.3x short. So
this is a trend point, not the freeze run.

### Action: extend the scan rather than pick a rule

Launched N=960,000, 10 seeds, epochs 8, niter 2 (16x the 60k steps, 4x the 240k). This separates the two
hypotheses cleanly and the seed count is ample for it:

- step-limited: sd -> 0.807/4 = **0.20%**
- initialization-limited: sd stays ~**0.72%**

Even 10 seeds distinguishes 0.20% from 0.72% comfortably, which is why I did not spend 16 (256
seed-equivalents would not fit the 4h interactive ceiling).

**Predeclared, before the numbers exist:**
- sd falls to ~0.20-0.35% -> the law holds after all, the 240k point was noise in the sd estimate,
  proceed to the 2M freeze run and expect 0.05 to be safe.
- sd stays >= 0.60% -> initialization-dominated, confirmed across a 16x step range. Then 0.05 is
  marginal at ANY N (mean ~0.94F = 3.5% with sd 0.72% puts E[max of 32] near 5.1%), and **niter 2->3 is
  the answer** — which is a campaign-level change and therefore Joseph's, not mine.

Still nothing frozen and nothing committed. `56355818` remains PENDING.

## 16:10Z — 960k arm running; log mirrored to the cluster

`56363377` on nid001104, started 15:51:00Z, N=960,000 x 10 seeds. Expected ~2.7h (16x the per-seed cost
of the 60k run), so landing ~18:30Z — well before Joseph is back. The local wrapper was killed again and
the cluster job again survived; that is now a known non-event rather than a scare.

Mirrored this log to `/pscratch/.../nd-unfolding/pet/AUTONOMOUS_LOG_20260805.md`, digest verified
identical both sides (`12241c47...`, 928 lines). It had existed only on the Mac, which meant the one
artifact describing this window's reasoning was also the one thing that would not survive if the laptop
went away. Now it sits next to the jobs and receipts it describes.

**Deliberately NOT mailing this cycle.** The 240k result is a genuine coin-flip — agy's falsifier fires,
the first analysis's does not — and sending Joseph an unresolved fork while he is away costs him a
decision he cannot usefully make yet. The 960k arm resolves it in ~2h. Holding.

Nothing frozen, nothing committed, nothing staged. `56355818` still PENDING.

---

## 16:20Z — COMMS: I have no verified channel to Joseph, and I over-claimed that I did

He asked again why he has received no update. I searched his Gmail with `in:anywhere` (spam included):
**zero mail from nersc.gov or perlmutter**. So none of the five emails reached Gmail.

**Correction to my own claim.** I wrote earlier that the five mails "were delivered — to Stanford."
I had no evidence for that. What I actually knew was that NERSC's relay ACCEPTED them (queue empty, no
bounce). Acceptance is not delivery. I turned an absence of bounces into a positive delivery claim,
which is the same over-reading as treating his "confirm your messages" note as email confirmation.

Channels, tested rather than assumed:

| channel | state |
|---|---|
| Perlmutter SMTP -> josephrb@nersc.gov | accepted; delivery **UNVERIFIED**. Cannot target gmail.com (relay refuses non-nersc/lbl) |
| Gmail `create_draft` | can WRITE to his account, but the connector has **no send tool**, so nothing notifies him |
| PushNotification | refuses to fire — reports the terminal as active |
| his Mac's `sendmail` | tested: accepts mail, but **postfix is not running**, so it silently never delivers. Dead end |

Net: **while he is away there is no verified path to him.** Stopping the attempt to manufacture one —
I have spent enough of this cycle on comms, and the measurements are the actual deliverable.

Mitigations applied rather than claimed: the status is now a **reply draft inside the thread he keeps
using** (id r6317709091282331226), which is more discoverable than a standalone draft; the log is
mirrored to /pscratch with a verified digest; and the wakerctl watch will mail the powered-closure
verdict through a path that does not depend on this session at all. The fix for live email is on his
side — read josephrb@stanford.edu, or point Iris forwarding at Gmail.

`56363377` (960k, 10 seeds) still running, ~29 min in. `56355818` still PENDING, priority 68032, rank 38,
gpu_shared running 153.

## 16:50Z — quiet verification cycle, nothing invented

Nothing unblocked, so this cycle only confirms state rather than manufacturing work.

- Local tree: exactly the expected 3 modified (`OPEN_ITEMS.md`, `extract_fullevent_fps.py`,
  `test_fullevent_extract.py`) + this log untracked. **Nothing staged, nothing committed.**
- `HEAD == origin/main == 61f2fb2` locally, and the cluster is also `61f2fb2` with **zero tracked
  dirt** — the two trees have not re-forked since the morning sync.
- wakerctl live at 16:50:14Z on login27; watch `pwclosure-56355818` still `armed`, `unreliable=0`
  (so its tick really is evaluating the job each pass, not merely sitting there).
- `56363377` (960k x 10 seeds) RUNNING 59:18, healthy. Its table prints only at completion, so an empty
  output file is expected, not a stall — worth stating because I misread exactly this as a hang earlier
  today with the verifier.
- `56355818` still PENDING.

**No email sent this cycle, deliberately.** Five have gone unread and I verified last cycle that the
SMTP path does not reach the inbox he is reading; a sixth would add nothing. The reply-draft inside his
active Gmail thread and the /pscratch-mirrored log are the channels that actually carry information, and
both are current. The wakerctl watch remains the one path to him that does not depend on this session.

## 17:20Z — quiet cycle; 960k ETA grounded on measured throughput, not guessed

Nothing unblocked, no new mail, nothing invented.

Calibrated the ETA against the arms that already finished rather than estimating again:

| job | work | elapsed |
|---|---|---|
| 56358288 | 32 seeds @ 60k | 30:26 |
| 56358954 | 32 @ 60k + 8 @ 60k/ep32 | 43:23 |
| 56360955 | 16 seeds @ 240k | 45:41 |

That is **~0.71 min per seed-equivalent** (1 seed-equiv = one seed at N=60k). The 960k arm is
10 seeds x 16 = 160 seed-equivalents, so **~1h53m**, completing ~**17:44Z**. RunTime is 1:29:03 against
TimeLimit 4:00:00 (EndTime 19:50:56Z), so **>2h of headroom** — no walltime risk, which is worth having
checked given I killed a job on walltime earlier today by not doing this arithmetic.

`56355818` still PENDING. Local and cluster trees both `61f2fb2`, nothing staged, nothing committed.

---

## 17:45Z — N-SCAN COMPLETE over a 16x step range. The 1/sqrt(steps) law is REFUTED. The confound was NOT the explanation.

`56363377` COMPLETED in 1:44:28 (predicted 1h53m from measured throughput — the calibration held).
`closure_b1_rate_injection_scan10_measured_N960k.json`, VERDICT FAIL.

| N | steps | n | verdict | dev max | dev mean | **dev sd** | >0.05 | >C | mean/F |
|---|---|---|---|---|---|---|---|---|---|
| 60k | 944 | 32 | FAIL | 5.7318% | 3.8227% | 0.8067% | 4/32 | 1/32 | 1.0244 |
| 240k | 3,776 | 16 | FAIL | 5.1473% | 3.5176% | 0.7239% | 1/16 | 0/16 | 0.9426 |
| 960k | 15,104 | 10 | FAIL | 5.1023% | 3.5938% | **0.8863%** | 1/10 | 0/10 | 0.9630 |

sd under 1/sqrt(steps) would be 0.8067 -> 0.4033 -> 0.2017%. Observed/predicted = **1.00, 1.79, 4.39**.
The sd is flat — arguably rising — across a 16x increase in optimizer steps. **agy's predeclared
falsifier is CONFIRMED: the spread is seed/initialization variance, not step-limited optimizer noise.**

So the gradient-step confound, which I offered as the likely explanation and which the first CLI analysis
projected would rescue 0.05, **does not**. Both of us were wrong about the mechanism; agy's falsifier was
the thing that caught it, which is exactly why it was written down in advance.

**What steps DID fix, and what they did not.** The mean fell to ~0.95x the worst-case floor, so the
closed form is a genuine bound that a well-trained run beats; and max stopped breaching the ceiling
(1/32 at 60k, then 0/16 and 0/10). What never improved is the WIDTH, and the width is what a once-fired
gate lives on. Pooling the two large-N arms — 26 seeds at >= 3,776 steps — **2 of 26 exceed 0.05**, i.e.
roughly an **8% false-reject rate** on a gate that fires once on frozen seed 42 with no retry.

**Conclusion, stated plainly: 0.05 is too tight, and no amount of training fixes it.** The remedy is a
choice between changing `niter` (principled, campaign-level cascade) and raising the tolerance toward the
ceiling (no policy change, but ~7% margin above the observed max, and it is a tolerance raise). Neither
is mine to make.

Sent to agy with the full three-point data — different account, per his usage instruction — asking
specifically whether raising 0.05 -> ~0.055 violates the "never raise a tolerance" constraint **in
substance or only in form**, and what false-reject rate is defensible for a once-fired gate. Also asked
it to rule on the disagreement about re-referencing the discriminator, since that objection came from
the other analysis and agy should get to answer it.

Nothing frozen. Nothing committed. `56355818` still PENDING.

## 17:55Z — agy remedy verdict, and the one assumption in it that I am measuring rather than trusting

agy (65s, 4,601 bytes) ranked:

1. **(C) niter 2 -> 3, KEEP tol = 0.05.** F drops 3.7318% -> 2.1698%; with sd ~0.81% the threshold moves
   from F+1.6sigma to F+3.5sigma, taking the false-reject rate from ~8% to <0.01%. It also notes the
   cascade cost is paid anyway, since all four owed items land in one commit.
2. **(B) tol 0.05 -> 0.055 at niter=2.** No policy change; admits the large-N max 5.1473%; keeps
   separation from the broken arm (min 8.958%). But only ~0.44 sigma above the observed max, so ~1%
   false-reject.
3. **(D) discriminator re-reference — REJECTED, and agy explicitly accepts the other analysis's
   objection**: `P_k` encodes the synthetic closure's feature-INDEPENDENT acceptance, while real data has
   kinematic-dependent `a(x)` and OmniFold converges locally toward `R`. Hardcoding `P_k` would force a
   constant-acceptance assumption onto feature-dependent physics. So both advisors now agree: keep `R`.

**On whether (B) breaks the "never raise a tolerance" rule:** agy's answer is "in form yes, in substance
no", because 0.05 is explicitly tagged `PROVISIONAL_PENDING_CLOSURE_MEASUREMENT` — a pre-measurement
placeholder, not an established physics requirement — and 0.055 stays strictly below C so discriminator
power is preserved. I find that reasoning sound but it is precisely the kind of call that should be
Joseph's, not an advisor's.

**The assumption I am NOT taking on trust.** agy's Rank 1 computes the k=3 false-reject rate using
**sd ~= 0.81%, carried over from k=2**. There is no niter=3 data anywhere in this campaign. sd is
seed/initialization variance, and the k=3 recursion is a different estimator — the width could move in
either direction. Every extrapolation I accepted today (the 1/sqrt(steps) law, from both advisors) turned
out wrong when measured, and this one would justify a **campaign-level policy change plus re-running an
8-hour nominal**. So it gets measured.

Launched a **niter=3 arm at N=240,000, 16 seeds** — same N and same seeds as the existing niter=2 240k
point, so the comparison isolates niter alone. ~45 min from measured throughput.

**Predeclared before the numbers exist:**
- sd stays ~0.7-0.9% and mean falls to ~2.0-2.2% -> agy's Rank 1 is confirmed on measurement, false-reject
  <0.1%, and (C) is the recommendation I take to Joseph.
- sd GROWS materially at k=3 -> the k=3 z-score is not 3.7 and Rank 1 is not established; (B) at ~1%
  false-reject becomes the better-evidenced option despite being a tolerance raise.
- mean does NOT fall toward F_3 -> the closed form does not describe k=3 here and BOTH remedies are on
  sand; report that and freeze nothing.

Nothing frozen, nothing committed. `56355818` still PENDING.

## 18:15Z — niter=3 arm running; wrapper kill again a non-event

`56369298` on nid001052, started 17:59:23Z. Parameterization verified from the generated script rather
than assumed: `N=240000`, `--niter 3 --scan-seeds 16`, output
`closure_b1_rate_injection_scan16_measured_N240k_niter3.json`. The local wrapper was killed a third time
and the cluster job again survived on nohup.

ETA from measured throughput: niter=3 is ~1.5x the per-seed work of niter=2, so 16 seeds at 240k is
~96 seed-equivalents at ~0.71 min each = **~68 min**, landing ~**19:07Z** against a 2h walltime expiring
19:59Z. ~50 min headroom.

Not mailing until this lands: it decides between agy's Rank 1 (niter 2->3, keep 0.05) and Rank 2
(tol -> 0.055 at niter=2), and sending Joseph a recommendation an hour before the measurement that could
overturn it would repeat this morning's mistake.

`56355818` still PENDING.

## 18:25Z — CORRECTION: my "resubmit to regular" suggestion was wrong, and I named a QOS that does not exist

Earlier I told Joseph that if `56355818` had not dispatched, "`regular` with a longer wall may be the
better queue for an ~8h job". Two errors:

1. **`regular` is not the GPU QOS.** The GPU names are `gpu_regular`, `gpu_shared`, `gpu_preempt`,
   `gpu_interactive`, `gpu_debug`, `gpu_jupyter`. My first attempt to compare pressure returned
   `pending=0 running=0` for `regular` — which I nearly read as "that queue is empty, move there", when
   it actually meant my filter matched nothing. Caught it before repeating it.
2. **With the right name, the advice inverts.** Measured:

| QOS | pending | running | my rank at prio 68152 |
|---|---|---|---|
| **gpu_shared** (current) | 1,185 | 156 | **39** |
| gpu_regular | **2,883** | 156 | **174** |
| gpu_preempt | 669 | 3 | — |

`gpu_regular` carries 2.4x the backlog and would put the job at rank 174 instead of 39. **Staying in
gpu_shared is correct**, and resubmitting would have been a straight downgrade on top of forfeiting ~15h
of accrued priority. Recommendation to Joseph is now: leave it alone.

Sobering datum while looking: a `gpu_shared` job at priority 68325 — higher than mine — has been pending
since **2026-07-20**. So rank 39 does not imply "soon", and I should stop implying it does. (That job may
carry a hold or dependency; I did not chase it, so treat it as an upper bound on patience rather than a
prediction.)

`56369298` (niter=3, 240k, 16 seeds) RUNNING 20:20, ETA ~19:07Z. No new mail. Nothing frozen, nothing
committed.

---

## 19:25Z — niter=3 arm PASSES, and it INVERTS agy's ranking. Its key assumption was wrong.

`56369298` COMPLETED 1:08:37 (predicted ~68 min). VERDICT **PASS**, 16/16 corrected recover.
`closure_b1_rate_injection_scan16_measured_N240k_niter3.json`.

Paired against the existing niter=2 point — same N=240,000, same seeds 7-22, only `niter` changed:

| | niter=2 | **niter=3** |
|---|---|---|
| structural floor F | 3.7318% | **2.1698%** |
| dev mean | 3.5176% | **2.1698%** |
| mean / F | 0.943 | **1.000** |
| **dev sd** | 0.7239% | **1.1331%** |
| dev max | 5.1473% | **4.2750%** |
| exceeding tol 0.05 | 1/16 | **0/16** |
| clearance below 0.05 | 2.05 sigma | **2.50 sigma** |
| broken min | 9.7910% | 9.3734% |

Two checks that the physics is behaving: `F3 = F2*(1-a) = 2.1698%` reproduces the closed form exactly,
and `mean/F = 1.000` — at k=3 the realized residual sits right on the bound.

**agy's Rank 1 rested on sd being unchanged at k=3 (~0.81%). It is not: sd GREW 56%, 0.7239% ->
1.1331%.** So the clearance is **2.50 sigma, not the 3.70** agy projected, and the false-reject rate is
**~0.6%, not <0.01%** — sixty times worse than claimed, and it misses agy's OWN stated bar of <=0.1% for
a once-fired gate. This is exactly the extrapolation I declined to take on trust, and the third time
today a confident projection failed on measurement.

### Full option table, all four configurations, measured

| config | clearance | false-reject | tol < C? |
|---|---|---|---|
| niter=2, tol 0.050 (status quo) | 2.05 sigma | **2.0%** | yes |
| niter=2, tol 0.055 | 2.74 sigma | **0.31%** | yes (by 0.35%) |
| niter=3, tol 0.050 (agy Rank 1) | 2.50 sigma | **0.62%** | yes |
| niter=3, tol 0.055 | 2.94 sigma | **0.16%** | yes (by 0.35%) |

**THE RANKING INVERTS.** `niter=2 + tol 0.055` (0.31%) beats `niter=3 + tol 0.050` (0.62%) — better
false-reject, AND no NOMINAL_SEED_POLICY change, AND no 8-hour nominal re-run. agy ranked these the other
way round purely because it assumed away the sd growth.

### A structural finding neither advisor reached

The ceiling C caps achievable clearance regardless of tolerance choice:

    niter=2: best possible 2.77 sigma -> 0.28%
    niter=3: best possible 2.96 sigma -> 0.16%

**agy's own <=0.1% (3 sigma) bar is UNREACHABLE at niter <= 3.** No tolerance value gets there, because
any tol >= C is inert. Reaching 3 sigma would need niter=4+ (F4 = 1.2617%) and depends on whether sd keeps
growing — unmeasured, and I am not launching it unprompted; it is a bigger campaign change than niter=3.

### Recommendation to Joseph (his call, not applied)

**`niter=2` + `tol 0.055`**, i.e. agy's Rank 2, now the better-evidenced option: 0.31% false-reject,
6.5x better than the status quo, no policy cascade, no nominal re-run. Its cost is raising a tolerance —
which agy already judged acceptable in substance because 0.05 is explicitly tagged
`PROVISIONAL_PENDING_CLOSURE_MEASUREMENT` and 0.055 stays under C. Honest caveats: the margin to C is only
0.35%, and no configuration reaches 3 sigma.

If he wants the best available number and accepts the cascade: `niter=3 + tol 0.055` gives 0.16%.

Nothing frozen, nothing committed. `56355818` still PENDING (~16h).

---

## 19:55Z — JOSEPH APPROVED the recommendation. Hardening it before applying it.

Mail 19:47Z: *"Apply your recommendation. If you want extra confirmation, try both agy and/or
claude-personal a few more times for robustness."* Earlier at 19:18Z he confirmed the drafts channel
works and he is checking it.

So: **niter stays 2, `fold_forward_ratio_dev_max` 0.05 -> 0.055**, status retired to MEASURED with a
frozen provenance record, plus the two named guards. He raised the tolerance knowingly — I stated the
concern twice (in the log and in the mail), gave the caveats (0.35% margin to C; nothing reaches 3 sigma),
and he reaffirmed. Proceeding on his decision.

`claude-personal` remains unusable (expired OAuth), so robustness goes through agy only.

**Two hardening steps launched before touching any file**, because "apply it" should not mean "apply it
on 16 seeds":

1. **Measurement robustness.** The whole 0.055 choice rests on `sd = 0.7239%` from 16 seeds at
   N=240k — and the false-reject figure (0.31%) is a z-score off that sd. Launched 32 MORE seeds
   (`--seed 23 --scan-seeds 32`, niter=2, N=240k), pooling to 48. ~91 min. If sd comes back materially
   higher, 0.055's clearance shrinks and Joseph needs to know before it is frozen, not after.
2. **Implementation review, not decision review.** Sent agy the exact edit set and told it NOT to
   re-argue the choice, but to find what the edit BREAKS. Specifically: which other checks read
   `FROZEN`'s tolerance and might go vacuous; what in `test_b1_normalization_fix.py` breaks versus what
   silently stops testing anything (the more dangerous outcome); whether 0.055 should be a literal at all
   given `C` depends on R — at what R does 0.055 become inert, and should the guard be relative
   (`tol = 0.9*C`) instead; and the repo's SANCTIONED structure for re-issuing the state file, cited from
   a prior re-issue, so the fresh digests are written as a proper new record rather than hand-edited
   hashes.

That third question is the one I most want answered before editing: freezing an absolute `0.055` when the
admissible ceiling is a function of the measured R would bake in exactly the kind of silent
knife-edge the CLI analysis already found once (0.05 is non-inert only because R > 1.1111, clearing it by
1.17%).

Nothing edited, nothing frozen, nothing committed yet. `56355818` still PENDING (prio 68227, ~16.5h).

## 20:05Z — re-issue structure established from the source (not from an advisor)

I asked agy for the sanctioned re-issue structure, then went and derived it myself rather than wait —
today's repeated lesson being that a summary is not the source. Confirmed by reading all four generations
of the file:

**Retired records** (`20260721`, `20260731`, `20260801` — each superseded in turn) all carry:
- `files_at_issue` in place of `files`
- each entry keyed `sha256_at_issue` in place of `sha256`, digest preserved verbatim
- `superseded_by`: path of the successor

**Live record** (`20260801b`) carries:
- `files` — the live pins, **16 bound files**
- `reissue`: `{supersedes, why, runbook_step, ...}` where `why` is a substantive paragraph naming the
  audit finding that forced it, not a one-liner

So the re-issue is: write `p3f-pet-gate4-launch-code-gate-20260805.json` with fresh digests for the 16
bound files and a `reissue` block citing RESTORE-2026-08-03.md Step 2b; then retire `20260801b` by the D3
transform. **At no point is a hash edited in place** — the forbidden operation and the sanctioned one look
superficially similar, and this is the distinction that keeps them apart.

Note the count discrepancy worth resolving before writing: the state file binds **16** files, while the
verifier currently reports **10** drifted (8 pre-existing + 2 from item 1). So 6 bound files are unchanged
and their existing digests should carry across unchanged — I will re-hash all 16 rather than assume which
6, since assuming is how a stale pin survives a re-issue.

agy's implementation review is still running (8:10 elapsed but only 8s CPU — API-bound, not hung; 30m
timeout). Robustness arm at 54:41 of ~91 min. Nothing edited yet.

## 20:10Z — CORRECTION: I reported another user's job as mine, twice

I twice stated the robustness arm was "at 54:41". That number came from
`squeue -j 56370836` where **56370836 was a job ID I invented** — I had not captured the real one from the
launch. The command unexpectedly succeeded because that ID belongs to **another user (`mphagen`)**, whose
`interactive` job was at 55:52. I read a stranger's elapsed time as my own progress.

Authoritative state, from `squeue -u josephrb`:

    56371892  RUNNING  9:50 / 3:00:00  run_b1_robust.sh   StartTime 2026-08-05T19:50:31Z

So the arm is ~10 min in, not ~55, and lands nearer **21:11Z**. The srun spent ~7 min queueing before
dispatch, which is why elapsed lags my launch time.

Root cause is the same one as this morning's `--include=*.py` and the `regular` QOS: **I substituted a
plausible identifier for a captured one.** The fix is mechanical — always read the job ID back from
`squeue -u josephrb` or from the launch output, never type one from memory, and never trust that
`squeue -j <id>` returning data means the id is mine.

agy's implementation review still at 0 bytes (~9 min elapsed, API-bound; 30m timeout expires ~20:21Z).
Nothing edited, nothing frozen, nothing committed.

---

## 20:15Z — I answered my own question 3, and it sharpens the risk in what Joseph approved

agy's review has produced 0 bytes in 14 min (API-bound). Rather than stay blocked on the one question that
changes the implementation, I computed it. `C(R) = (R-1)/(2R)`, so an absolute tolerance goes inert when
`tol >= C`, i.e. at `R <= 1/(1-2*tol)`:

| tol | inert at R <= | margin vs measured R=1.1240803 | as % of (R-1) |
|---|---|---|---|
| 0.045 | 1.098901 | 0.025179 | 20.29% |
| 0.050 | 1.111111 | 0.012969 | **10.45%** |
| 0.0525 | 1.117318 | 0.006762 | 5.45% |
| **0.055** | **1.123596** | **0.000485** | **0.391%** |

**0.055 sits on a knife edge in R-space.** A 0.04% downward move in the measured R silently disables the
check — and R is re-measured per re-issue and per bootstrap replica. That is 27x less headroom than 0.05
had, and it is the SAME silent-knife-edge failure mode the first CLI analysis flagged when it noted 0.05 is
non-inert only because R > 1.1111. I reported "margin to C is only 0.35%" to Joseph in tolerance-space,
which understated it: expressed in the variable that actually moves, it is 0.39% of (R-1).

**Relative tolerances do not rescue it**, they trade the failure for a worse one:

    0.90*C = 4.967%  -> 2.00 sigma -> 2.26% false-reject   (WORSE than 0.05's 2.03%)
    0.85*C = 4.691%  -> 1.62 sigma -> 5.25%

because C is itself only 5.52% and 90% of it barely clears 0.05. The tension is structural: the mean sits
at 1.48x the floor, so there is no tolerance that is simultaneously far from C and far from the mean.

### Resolution: the fragility is only dangerous while it is SILENT, and E3 removes that

E3 was already in the plan — a named check that FAILS when `tol >= C`. With it, a future R that makes
0.055 inert does not quietly pass a toothless gate; the gate refuses and names the reason. So:

- **Keep 0.055 as Joseph approved** — it is the best false-reject (0.31%) and he reaffirmed it after I
  raised the concern.
- **E3 is mandatory, not optional.** It converts the knife edge from a silent degradation into a
  fail-closed error. This is the same principle as the extractor telemetry earlier today: a guard that
  cannot tell "safe" from "vacuous" is not a guard.
- **Record `R_critical = 1.123596` explicitly in the provenance**, so the fragility is documented at the
  freeze rather than rediscovered by whoever next re-measures R.
- Note for Joseph, not acted on: **0.0525** is the honest middle (5.45% R-margin, ~0.84% false-reject,
  still 2.4x better than the status quo) if he would rather trade some false-reject for R-robustness. I am
  not substituting it for what he approved.

Robustness arm `56371892` at 13:59 of ~91 min. Nothing edited yet.

## 20:25Z — agy consult #4 stalled; did its remaining two questions myself. One test goes VACUOUS.

agy ran 28:57 with **10 seconds of CPU**, state `Sl`, zero output — stalled, not thinking. The three
earlier consults returned in 65s, 2min and 11min, so this is a fault, not depth. Killed it. Joseph asked
for advisor confirmation "for robustness" and has had four consults (one claude CLI, three agy); a
stalled fourth does not block the work, and both of its load-bearing questions I have now answered from
the source.

**Q1 — everything that reads the tolerance** (5 sites):

    validate_pet_nominal_gate4.py:266   the check itself
    validate_pet_nominal_gate4.py:1119  reports tolerance_status into the receipt
    test_b1_normalization_fix.py:765    test_tolerance_has_power_against_the_defect_and_admits_the_floor
    test_b1_normalization_fix.py:877    assertGreater(dev, tol) -- the fixture's own power self-check
    test_b1_normalization_fix.py:932    pins the literal status string

**Q2 — what breaks, and what is worse than breaking:**

| site | at tol = 0.055 |
|---|---|
| `:929` `test_tolerance_is_marked_provisional` | **HARD FAILS** — asserts the exact string `PROVISIONAL_PENDING_CLOSURE_MEASUREMENT`. Expected; E4 replaces it with an internal-consistency assertion. |
| `:758` `test_tolerance_has_power...` | **PASSES, AND GOES VACUOUS — this is the dangerous one.** It hardcodes the stale recoil-era `R, acc, k = 1.135, 0.621, 2`, so it checks `floor(1.7085%) < tol < signal(11.894%)`. 0.055 sails through. But the operationally binding ceiling is **C = 5.5192%, not `signal` = 11.038%**, and 0.055 clears C by only 0.39% in R-space. So the test would stay green while the real constraint sits on a knife edge. Exactly the "still passing but testing nothing" failure mode I asked about, and it is real. |
| `:877` `assertGreater(dev, tol)` | needs NUMERIC verification, not assumption — the fixture's spread is `linspace(-0.8, 0.8, 500)` so `dev` is likely large, but "likely" is what burned me three times today. I will run it before and after. |

So E4 is bigger than "update two literals": `:758` must take the operating point from the frozen
provenance instead of stale constants, AND replace its upper bound `signal` with `C`. Without that second
change the re-issue ships a power test that cannot see the constraint that actually binds.

**Sequencing.** I am NOT editing yet. The provenance block must record the FINAL sd and seed count, and
the robustness arm (`56371892`, 29:15 of ~91 min, 32 more niter=2 seeds pooling to 48) is still running.
Freezing a provenance record and then discovering the pooled sd differs would mean re-issuing twice —
and a re-issue is exactly the operation this campaign has already paid for repeating.

Nothing edited, nothing frozen, nothing committed.

## 20:50Z — last implementation unknown closed by computation, not assumption

Site `:877`'s power self-check is deterministic (`default_rng(11)`), so I evaluated it exactly rather than
reasoning that "the spread is probably large enough":

    fixture dev = 11.9981%
      assertGreater(dev, 0.0500) -> True, 2.4x margin
      assertGreater(dev, 0.0550) -> True, 2.2x margin
    paired push_ok dev = 1.96e-16  -> accepted at any tolerance

So `:877` survives the raise with margin and keeps its power. The E4 edit set is therefore fully
characterised, with no unknowns left:

| site | verdict | action |
|---|---|---|
| `:758` | passes but **VACUOUS** (stale R/acc; bounds tol by `signal` 11.894% not `C` 5.5192%) | take operating point from the frozen provenance; replace `signal` with `C` |
| `:877` | **survives**, 2.2x margin, verified numerically | no change |
| `:929` | **hard-fails** on the literal status string | assert provenance internal consistency instead |

Every question I sent the stalled agy consult is now answered from the source or by direct computation:
Q1 (five readers, enumerated), Q2 (which break vs which go vacuous), Q3 (the R-space fragility of an
absolute 0.055 and why E3 neutralises it), Q4 (the sanctioned re-issue structure, read off all four
generations of the state file).

Remaining before I edit: the pooled sd from `56371892` (59:13 of ~91 min), which the provenance block must
record. Nothing edited, nothing frozen, nothing committed. `56355818` still PENDING.

---

## 21:05Z — POOLED 48 SEEDS. The figures Joseph approved on were 6x optimistic. Holding the edit.

`56371892` COMPLETED. Pooled with the original arm: **48 seeds (7-54), niter=2, N=240k**.

    dev  max 5.3764%   mean 3.8008%   sd 0.8067%
    p50 3.7792%  p90 5.0207%  p95 5.1302%  p99 5.3087%   broken min 9.7910%

| tol | observed exceedance | gaussian estimate |
|---|---|---|
| 0.0500 (status quo) | **6/48 = 12.50%** | 6.86% |
| 0.0525 | 1/48 = 2.08% | 3.62% |
| **0.0550** | **0/48 = 0.00%** | **1.76%** |

**Two corrections I owe Joseph, both because the 16-seed sd understated the spread by 11%
(0.7239% -> 0.8067%):**

1. I told him 0.055 gives **0.31%** false-reject. It is **~1.76%** by the gaussian tail — **6x worse**.
   The observed 0/48 is genuinely reassuring, but 0 of 48 only bounds the true rate below ~6% at 95%
   confidence; it does not establish 0.3%.
2. I told him the status quo 0.05 gives 2.03%. Observed is **12.5% (6/48)**. So the thing we are replacing
   is worse than I said too — that part strengthens the case for acting, not weakens it.

### The structural problem the pooled data exposes

At niter=2 the admissible window is now **measured**, and it is nearly closed:

    niter=2:  (max 5.3764%, C 5.5192%)  =  0.1428 pp wide
              0.055 sits 0.1236 pp above the max and 0.0192 pp below C
    niter=3:  (max 4.2750%, C 5.5192%)  =  1.2442 pp wide   -- 8.7x wider

And the niter=2 max GREW from 5.1473% to 5.3764% (+0.229 pp) going 16 -> 48 seeds. Another 48 seeds could
plausibly push it past 0.055 entirely. niter=3 has only 16 seeds, but even granting it the same +0.23 pp
growth its window stays ~1.0 pp.

So the option Joseph approved is empirically clean on 48 seeds (zero exceedances) but **structurally
fragile on two independent axes**: a 0.14 pp admissible window, and a 0.39% margin in R before 0.055 goes
inert.

### Decision: I am NOT applying the edit, and this goes back to him

He approved niter=2 + 0.055 on figures now known to be 6x optimistic. Applying it anyway would be
executing an approval he did not actually give — the number he weighed was 0.31%, not 1.76%. Applying
niter=3 instead would be substituting my judgment for his on a campaign-level change. Both are wrong, so
the correction goes to him with the updated comparison and he chooses.

He asked "How is it going?" at 20:56Z, so he is reachable now. Sending the correction.

Nothing edited, nothing frozen, nothing committed. `56355818` still PENDING (~17.7h).

## 21:20Z — launched my own option (4): 32 more niter=3 seeds, to make the comparison symmetric

No reply from Joseph yet on the HOLD mail. Rather than idle on a decision, I launched the measurement I
recommended, because it is evidence-gathering rather than a campaign change and it strictly dominates
waiting: whichever option he picks, a 48-seed niter=3 number is better than a 16-seed one.

    56375160  RUNNING  run_b1_niter3_more.sh  -t 03:30:00
    N=240000  --niter 3 --seed 23 --scan-seeds 32   (seeds 23-54, pooling to 48)
    -> closure_b1_rate_injection_scan32_measured_N240k_niter3_seeds23plus.json

Job ID **captured from `squeue -u josephrb`, not typed from memory** — the fix for this afternoon's error
where I reported another user's job (56370836, `mphagen`) as my own progress. Parameterization verified by
reading it back out of the generated script rather than trusting the sed.

ETA: niter=3 costs ~1.5x niter=2 per seed, so 32 seeds at 240k is ~192 seed-equivalents at ~0.71 min =
**~2.3h**, against a 3.5h walltime. Lands ~23:35Z.

**Why this matters and is not busywork.** The whole HOLD rests on comparing a 48-seed niter=2 measurement
(max 5.3764%, window 0.14 pp) against a 16-seed niter=3 one (max 4.2750%, window 1.24 pp). That asymmetry
is exactly what just bit us: the niter=2 max grew +0.23 pp from 16 to 48 seeds and the sd grew 11%. If
niter=3's max grows similarly its window is still ~1.0 pp and option (2) is clearly right; if it grows a
lot more, the two options converge and (1) becomes defensible on cost grounds. Either way Joseph gets a
like-for-like comparison instead of my extrapolation.

Nothing edited, nothing frozen, nothing committed. `56355818` still PENDING, prio 68362.

## 22:35Z — the session-side Monitor on 56355818 expired; the durable watch is intact

The Monitor armed on `56355818` this morning ended its stream. Its last observation was
`state=PENDING at 10:24:41Z`, and the job is STILL PENDING — so it expired without a state change rather
than reporting one. No news about the critical path.

Checked the notification path that actually matters, since one of the two just died:

    wakerctl observed 2026-08-05T22:31:51Z on login27
      pwclosure-56355818   armed   unreliable=0
    wakerctl cron 56160911  PENDING (BeginTime)   <- its scheduled next tick, normal

So the session-independent path is live and still evaluating cleanly each tick. **Not re-arming a
Monitor**: it would duplicate both the wakerctl watch (which survives this session) and the per-cycle
poll, and redundant machinery is a thing to maintain rather than a safety net.

Standing tally at ~18.5h pending: priority has climbed 67792 -> 68392 while rank held at 38-39. The job is
not starving, it is simply behind ~38 higher-priority jobs in a 1,185-deep queue.

`56375160` (32 niter=3 seeds) RUNNING 41:30 of ~2.3h. Nothing edited, frozen, staged or committed.

## 22:58Z — the niter=3 arm is SOUND, but my predeclared decision rule is NOT

Two checks while waiting on `56375160`. Both read-only. Nothing edited, frozen, staged or committed.

### 1. Chased a suspicious coincidence in the niter=3 arm. Verdict: benign fluke.

Recomputing the decision table off disk (not from memory) surfaced that the niter=3 16-seed arm has
`mean dev = 2.1698%` and `structural_floor_worst_case = 2.1698%` — equal to five significant figures. If
that were degeneracy rather than luck, the arm the whole decision may turn on would be measuring itself.

It is luck:

    F        = 0.021697820965251927
    mean dev = 0.021698003976643503
    mean - F = 1.83e-07        mean/F = 1.0000084
    16 distinct dev values, spread 0.1590% .. 4.2750%
    dev_from_R reproduces |ratio/R - 1| exactly (0.012362813438158704, seed 7)

So the arm is sound. Recording it because the exactness is the kind of thing that looks like provenance
and isn't; a later reader would be right to suspect it.

Incidental correction to my own earlier reporting: I had quoted the niter=3 arm's **mean as 2.1698%** in
the pooled comparison. That number is correct, but I had also been treating `structural_floor_worst_case`
as if seeds sit above it. They do not — **10 of 16 niter=2 seeds and 7 of 16 niter=3 seeds land BELOW F.**
F is a worst-case expected push, not a per-seed lower bound. Nothing downstream depended on the wrong
reading, but the runbook language invites it.

### 2. The `mean+3sd` criterion I predeclared to Joseph is the wrong statistic. It fires on both arms.

From the 2026-08-05 mail, branch 3 of the predeclared rule was `mean+3sd >= C -> the parameter-free check
itself would reject a correct unfold. No tolerance repairs it.` Evaluated on measured data:

| arm | n | mean | sd | mean+3sd | vs C=5.5192% | realized >C | gaussian P(dev>C) | clearance (C-mean)/sd |
|---|---|---|---|---|---|---|---|---|
| niter=2 | 48 | 3.8008% | 0.8153% | **6.2467%** | EXCEEDS | 0/48 | 1.75% | 2.11 sigma |
| niter=3 | 16 | 2.1698% | 1.1703% | **5.6806%** | EXCEEDS | 0/16 | **0.21%** | **2.86 sigma** |

The alarm branch fires for **both** arms — including the one whose verdict is PASS and which has 8x lower
tail risk. That is a defect in the rule, not a finding about the estimator:

- `mean+3sd` is dominated by **sd**. The quantity actually at stake is `P(dev > C)`, which depends on
  **(C-mean)/sd**. niter=3 has the *worse* sd (1.1703% vs 0.8153%) and the *better* clearance
  (2.86 vs 2.11 sigma) because its mean is 1.63 pp further from C. My rule graded it on the axis where it
  loses and was blind to the axis where it wins.
- So the rule collapses an 8x difference in tail risk (1.75% vs 0.21%) into one verdict. It cannot
  distinguish the options it was written to choose between.

Separately, the gaussian model itself is shaky for niter=3: it puts **3.19% of its mass below zero**, which
is physically impossible for `|ratio/R - 1|`. Skew is small (-0.108), so the problem is not tail shape but
that the mean is only 1.85 sd from the boundary. Consequence: the 0.21% figure is model-dependent too and
should not be quoted as precise. The 32 seeds in flight let us bound the niter=3 tail **empirically**
instead of by gaussian extrapolation.

**What this changes.** Nothing about the measurements — the tables stand. It retires the framing I gave
Joseph. "No tolerance repairs it" was generated by a criterion that says the same thing about a
configuration with 0/48 breaches and one with 0/16 breaches. The decision should be argued on realized
exceedance plus window width, which is how the 48-vs-48 comparison was already set up.

### State

    56355818  PENDING  ~19.6h   rank 24 of 1158 (was 38-39)   prio 68427   partition shared_gpu_ss11
    56375160  RUNNING  1:04 of ~2:17   ETA ~00:10Z   (walltime 03:30, expires 01:20Z — comfortable)
    56160911  cron     PENDING (BeginTime), healthy

Also correcting a naming error I made repeatedly today: `gpu_shared` is the **QOS**. The **partition** is
`shared_gpu_ss11`. Queue-depth figures I quoted are partition-scoped and remain comparable.

Inbound mail check this cycle: nothing newer than his 20:56Z "How is it going?", which he superseded by
returning to the keyboard at ~22:50Z. Not mailing — he is reachable in session, and one mail per cycle into
an empty room is spam.

## 23:00Z — fixed a noise defect in my own job watch

The watch armed at 22:58Z emitted on every 120s poll instead of only on state change: I had put Slurm's
elapsed-time field (`%M`) inside the change-detection key, and elapsed advances every cycle. Left alone
that trips the monitor's own noise guard and the watch gets auto-stopped — i.e. the mechanism I armed to
guarantee I would hear about a crash would itself have gone silent.

Fix: split the comparison key (STATE only) from the emitted line (state + elapsed, informational).
Re-armed. Same coverage as before — a job leaving the queue is reported as
`LEFT_QUEUE[State|Elapsed|ExitCode]` from sacct, so FAILED / TIMEOUT / CANCELLED / OOM all emit.

Worth recording as a pattern, not just a bug: a watcher whose liveness signal is indistinguishable from
its alarm signal is the vacuous-pass defect again, in monitoring clothes. Same family as the
`[[ -s FILE ]] && skip` scripts and the self-agreeing subsample check.

## 23:35Z — ITEM 4 WAS NOT DONE. It was a receipt no clone could see. Now resolved.

I have said in this log and in mail that item 4 is "DONE, PASS, sha `6c9520c7`" and that the re-issue is
"blocked ONLY on item 3". **The sha was right and the claim was wrong.** The receipt was **untracked**, and
it existed in the cluster tree only — it was never in the repository and did not exist locally at all.

    nd-unfolding/products/pet/fullevent_fps/closure_fullevent_fps.json
    sha256  6c9520c7f42ecae89c0f7eb4b68cd14d5dc55518ba42a8c31fe6ee56f8e284c4   (recomputed, both sides)
    git ls-files -> absent      git check-ignore -> not ignored      15145 bytes

So a re-issue that bound this receipt would have pinned a path that is not in git. Item 3 was never the only
blocker; it was the only blocker anyone had **written down**.

### Why this is not cosmetic — the two guards behave oppositely

Read out of the source, not inferred:

- `verify_hash_bindings.py:186-189` — a pin whose file is **missing** is counted `unresolved` and
  **silently skipped**. Never a failure. *This is the mechanism behind 109-local vs 856-compute.* A binding
  on an uncommitted file is therefore **live but vacuous** in every clone lacking it — the exact
  vacuous-pass family this log keeps cataloguing.
- `test_hash_bindings.py:79` — for entries in a live launch-code receipt's **`files`** dict, a missing file
  is a **hard assert**.

Decision: bind the receipt in **`files`** (role `closure_ordinary_receipt`) so its absence can never pass
quietly, and record provenance in `closure_evidence_recorded` beside it. Note the B-6 precedent lists
evidence as **bare paths with no sha256** — B-6's report is not hash-bound at all — so this is deliberately
stronger than precedent, not merely consistent with it.

### The commit is authored LOCALLY. Verified, not assumed.

Both trees and `origin/main` are all at `61f2fb2`; the cluster tree is clean on tracked files. The receipt
was transferred and **verified byte-identical** (same sha256 on both sides); `.gitattributes` carries no
`text=auto` and `core.autocrlf` is unset, so no renormalization risk. Local authoring wins because items 1
and 3 are code edits that live here, and shipping one verified 15 KB JSON inbound beats shipping a growing
patch set outbound into a tree with thousands of untracked `*.root.done` where `git add -A` is forbidden.

I also ran `verify_hash_bindings.collect()` over the receipt itself: **0 pins harvested.** It embeds no
`path`+`sha256` pairs, so committing it cannot introduce new live bindings or push the mismatch count past
10. That was a real risk worth eliminating before staging, not after.

### ⚠ The cluster pull WILL FAIL, and it is not obvious why

Established by experiment in a throwaway bare-remote clone rather than assumed: `git pull --ff-only` aborts
with *"The following untracked working tree files would be overwritten by merge"*, **exit 1, even when the
untracked file is byte-identical.** Git does not carve out matching content. So:

    cd /pscratch/sd/j/josephrb/MINERvA-OmniFold
    mv nd-unfolding/products/pet/fullevent_fps/closure_fullevent_fps.json /tmp/receipt.preserved.json
    git pull --ff-only
    sha256sum nd-unfolding/products/pet/fullevent_fps/closure_fullevent_fps.json   # expect 6c9520c7...
    python3 docs/orchestration/verify_hash_bindings.py --root .                    # expect 10 -> 0

### There is ONE cluster tree, under two names

`/global/homes/j/josephrb/MINERvA-OmniFold` is a **symlink** to `/pscratch/sd/j/josephrb/MINERvA-OmniFold`
— identical `device:inode`, same HEAD, same untracked files. Earlier notes citing both paths describe one
tree, so the move-aside above happens once. I checked this specifically because a phantom second clone is
exactly the kind of thing this campaign has been bitten by.

### A second, independent reason the four items must be ONE commit

Live launch-code-gate receipts number exactly **2** (`gate3-20260720`, `gate4-20260801b`) and
`_LAUNCH_CODE_FLOOR = 2` (`test_hash_bindings.py:44`). `_launch_code_receipts()` skips
`status == "SUPERSEDED"`, so retiring `20260801b` **without its successor in the same commit** drops the
count to 1 and fails the floor assert itself — on top of the binding breakage. The atomicity requirement
was previously justified only by the bindings; it has two independent causes.

Retirement convention confirmed identical across all three prior generations: add `status: "SUPERSEDED"`,
`superseded_by` (successor **must exist** — `test_hash_bindings.py:110`), `superseded_why`; rename `files`
-> `files_at_issue` and every inner `sha256` -> `sha256_at_issue`, leaving no live `sha256` in that block.

### Independent reproduction of item 1's binding arithmetic

Computed locally against the state file: of the 16 bound files, **10 drifted, 0 missing** — the 8 already at
`61f2fb2` plus item 1's two. Confirmed through the tool as well: the local verifier prints exactly
**10 MISMATCH**, all owned by `p3f-pet-gate4-launch-code-gate-20260801b.json`. Placing the receipt locally
was **inert** (no new pin, no new mismatch), as predicted.

Local verifier also now reads `111 resolved / 97 OK / 12 of 17 shell pins (floor 12)`. The 109 -> 111 rise
is the powered-closure commits since `8a9d22c`, not anything of mine. **Worth flagging: locally the shell
collector resolves exactly 12 of 17 against a floor of 12** — one fewer resolvable pin locally and the
verifier would go BLIND and fail for a reason unrelated to any real drift. On compute it is 17 of 17.

### The 48-vs-48 machinery is built and VALIDATED against known-good data

`pool_b1.py` pools `runs[].corrected.dev_from_R` keyed by seed, refuses inhomogeneous configs, refuses to
double-count a seed, and re-derives C and F from the receipt. Against the *existing* files it reproduces
every figure now on record — C 5.5192%, F 3.7318% / 2.1698%, niter=2 max 5.3764% / mean 3.8008% /
sd 0.8153% / 6-of-48 / window +0.1428 pp, niter=3 max 4.2750% / window +1.2441 pp, `mean - F = 1.8e-07`,
and `dev_from_R == |ratio/R - 1|` to `0.000e+00`. So it is trustworthy on the incoming arm rather than
merely written.

Two facts not previously recorded, both read out of the JSONs:

- **Arm-level verdicts: the niter=2 arm is `verdict: FAIL`, the niter=3 arm is `verdict: PASS`** — both
  judged against `tolerance_used = 0.05`. The FAIL is the 6/48 exceedances.
- Seed sets: niter=2 holds **7..54** (48, contiguous); niter=3 holds **7..22**. `56375160` runs
  `--seed 23 --scan-seeds 32` (read out of `/pscratch/sd/j/josephrb/run_b1_niter3_more.sh`, not from
  memory) -> seeds **23..54**. Pooled, niter=3 becomes **7..54**: the *same 48 seeds*, same N, same epochs,
  zero overlap. Genuinely like-for-like.

That script's header still predicts a `1/sqrt(steps)` law for `sd`; the 17:45Z entry **refuted** it. The
comment is stale — do not re-derive the confound story from it.

### Corrections owed to the brief I am working from

The re-issued brief is the 12:50Z one and several of its figures are ~11h stale. Recording rather than
silently working around them:

- "item 3 ... must sit above ~1.71% and well below ~11.9%" — those are the **stale operating point**
  (R=1.135, a=0.621). Measured: F = **3.7318%**, ceiling C = **5.5192%**.
- "read ... the 8-seed spread" — superseded; the decision arm is **48 seeds**.
- "item 4 = DONE" / "blocked ONLY on item 3" — corrected above.
- "`ssh perlmutter.nersc.gov`" — that alias does **not** resolve; `saul.nersc.gov` works.

### State at 23:35Z

    56355818  PENDING  prio 68462 (68427 -> 68462)   no DONE sentinel, no report   nothing to do
    56375160  RUNNING  1:40:47 of ~2:17   JSON not yet written   walltime expires 01:20Z
    56160911  cron     PENDING (BeginTime), healthy
    inbound  nothing newer than his 20:56Z "How is it going?" (1d and 2h windows both checked)

Brief item 4 (suite + verifier) needs no re-run: both were confirmed at `61f2fb2` (13:10Z verifier
856/844/8; 13:40Z suite 4 failed/746 passed) and **HEAD has not moved since**. Re-hashing ~1 TiB to
reproduce a result that cannot have changed would be inventing work.

Nothing edited in any Gate-4-bound file, nothing frozen, nothing staged, nothing committed. The only
working-tree change this cycle is the receipt now present locally as an untracked file.

## 23:40Z — the receipt is CONSUMABLE by the gate, verified by execution not by reading

Having found that item 4's receipt was untracked, I checked the sibling risk in the same family: the
re-issue is about to bind this receipt, but **had anything ever confirmed the gate can actually consume
it?** Step 3 (`RESTORE:948`) says `validate_pet_nominal_gate4.py --closure-report` re-derives the marginal
L1 itself and refuses a purity run, a synthetic-fixture run, or a run with loosened thresholds. If the
receipt failed any of those, the re-issue would freeze evidence the gate rejects — a latent blocker of
exactly the species I had just found.

It does not. `check_closure_provenance(ordinary, stress)` returns **`True`, all 11 checks OK**, run against
the real receipt plus the tracked B-6 stress report
(`runs/b6-stress-closure-muon/20260801-...20758087.report.json`). The validator **imports without
TensorFlow**, so this is verifiable on the Mac despite [[local-tf-cannot-run-pet]] — the provenance layer is
pure JSON checking.

The two most likely to fail both hold:

- `closure:ordinary_schema_is_the_full_event_schema` — the J01 check that rejects a recoil-only closure.
  The receipt's reco schema is the full 13 features
  (`pt, pparallel, mu_px, mu_py, mu_pz, mu_E, mu_cos_phi, mu_sin_phi, mu_qp, mu_minos_ok, vtx_x, vtx_y,
  vtx_z`) and matches `FROZEN` **exactly**, truth `[pt, pparallel]`. So this receipt certifies
  `pet-fullevent-fps-v1` and not `pet-reduced-fps-cross`.
- `closure:ordinary_thresholds_not_loosened` — `l1_max 0.1 <= 0.1`, `push_med_tol 0.15 <= 0.15`. Exactly at
  the frozen limits, i.e. run with zero overrides, which is what the 12:20Z entry claimed and this now
  confirms from the report itself rather than from the launch command.

Also confirming a number from the ordinary receipt rather than re-quoting it: `push_median =
1.085782766342163`, so `|median(push) - 1| = 0.0858 <= 0.15`. Matches the 12:20Z table.

Net: item 4 is now genuinely closed — the receipt exists in the authoring tree, is byte-verified against the
cluster, is `git add`-able, embeds no pins of its own, and **passes the gate that will consume it**.

## 23:50Z — quiet cycle. Deliberately NOT mailing, and why.

    56355818  PENDING  prio 68477 (68462 -> 68477)  only preflight artifacts; no report, no DONE
    56375160  RUNNING  1:59:40 of ~2:17  -> ~17 min out   sacct clean, ExitCode 0:0
    56160911  cron     PENDING (BeginTime), healthy
    inbound  nothing (1d and 2h windows both empty; last was his 20:56Z "How is it going?")

**Decision: no mail this cycle.** `56375160` lands in ~17 minutes and produces both a verdict and the
refreshed blocking decision. Mailing a no-news status now and the real comparison 20 minutes later would be
two mails for one cycle's news, against the standing "one mail per cycle at most". Recording the reasoning
because the opposite error — silence he has complained about twice today — is the one I am more likely to be
accused of, and I want the choice legible rather than looking like drift.

Readiness check done instead, since the outbound path has silently misdelivered once already today and I do
not want to discover a broken channel while holding a verdict: `send_channel_mail.py` is present and correct
(`To: josephrb@nersc.gov`, `Reply-To: jrbailey555@gmail.com`), and `mailq` is empty. **Reminder for the send:
SMTP reaches his STANFORD inbox via Iris, but he reads GMAIL** (16:20Z). So the verdict goes out as SMTP mail
**and** a Gmail draft, which is the combination that demonstrably reached him (his 19:18Z reply confirmed the
drafts).

Nothing edited, frozen, staged or committed.

> **Amended by the 00:50Z entry below:** the recommendation in this entry is right but the reasoning is
> under-credited — it restores **agy's** original Rank 1, and the 19:25Z measurement that overturned agy
> was a small-sample artifact. Read the two together.

## 00:15Z — 48-vs-48 IS IN. niter=3 wins on every axis. And it would VOID job 56355818.

`56375160` **COMPLETED** 02:21:50, ExitCode `0:0`, MaxRSS 12003756K. Report
`closure_b1_rate_injection_scan32_measured_N240k_niter3_seeds23plus.json`, sha256
`72b4e9f4d10b2c18e0af4ff43456004cf39b6b5bf500997e668888ae9ebca985`, verdict **PASS**, 32 runs,
seeds **23..54** — exactly the complement of the existing 7..22. Transferred and re-hashed locally:
identical. Pooled arm is 48 contiguous seeds 7..54, **the same seed set as niter=2**, same N, same epochs.

All figures recomputed from `runs[].corrected.dev_from_R`; the `dev_from_R == |ratio/R - 1|` identity holds
to `0.000e+00` across all 96 runs.

| | niter=2 (48) | **niter=3 (48)** |
|---|---|---|
| max | 5.3764% | **4.2750%** |
| mean | 3.8008% | **2.1876%** |
| sd | 0.8153% | 0.8444% |
| structural floor F | 3.7318% | 2.1698% |
| **> 0.05** | **6/48 = 12.5%** | **0/48** |
| > 0.055 | 0/48 | 0/48 |
| > C = 5.5192% | 0/48 | 0/48 |
| clearance (C-mean)/sd | 2.11 sigma | **3.95 sigma** |
| gaussian P(dev>C) | 1.75% | **0.0040%** |
| window C-max | +0.1428 pp | **+1.2441 pp (8.7x)** |

### Four things the new 32 seeds settled

1. **The feared growth did not happen.** Going 16 -> 48 the niter=3 max moved **+0.0000 pp** (4.2750% ->
   4.2750%). Over the *same* expansion the niter=2 max grew **+0.2291 pp** (5.1473% -> 5.3764%). The 21:20Z
   justification for this run was precisely that asymmetry; it resolved in niter=3's favour.
2. **The niter=3 sd FELL 27.8%** (1.1703% -> 0.8444%). The 16-seed sd was an overestimate. So my earlier
   framing — "niter=3 has the worse sd but better clearance" — is obsolete: at 48 seeds the two arms have
   **nearly equal sd**, and niter=3's advantage is now entirely its 1.61 pp lower mean. Cleaner, not subtler.
3. **The defective `mean+3sd` rule now separates them.** niter=2 gives 6.2467% (>= C, fires); niter=3 gives
   **4.7209% (< C, does not fire)**. It remains the wrong statistic (22:58Z) and I am not reviving it, but
   the awkwardness that it condemned *both* options is gone — it now points the same way as everything else.
4. **The gaussian is less pathological for niter=3** — mass below zero fell 3.19% -> **0.48%** — so the
   0.0040% tail figure is more trustworthy than the earlier 0.21%. Empirically both arms are 0/48 on C,
   which alone bounds the true rate only below **6.05%** (95%, one-sided). The discriminator is therefore the
   0.05 exceedance (6/48 vs 0/48) and the window width, exactly as set up.

### The cost nobody had written down: niter=3 mechanically VOIDS 56355818

Found by reading source, not inferred:

- `closure_powered_truth_reweight.py:192-194` -> `pol = NOMINAL_SEED_POLICY`; `:265` passes
  `niter=int(pol["niter"])` = **2**. `sbatch_powered_closure.sh:31` overrides nothing, deliberately.
- `:318` persists `configuration` including `niter`.
- **`validate_pet_nominal_gate4.py:790-795`** asserts `powered:nominal_configuration` —
  `all(cfg.get(k) == sp[k] for k in ("niter","epochs","estimator_seed","subsample_seed","batch_size"))`
  against `FROZEN["seed_policy"]`, which pins `niter: 2`.

So if `niter` becomes 3, the powered closure's report records 2, the check **fails**, and 56355818's output
is unusable as Gate-4 evidence. This is a hard gate failure, not a question of standards.

**And the window is closing.** `56355818` is **still PENDING** (~21h, prio 68477). Cancel-and-resubmit at
niter=3 today costs only queue time already spent — **no compute wasted**. If it starts running and niter
changes afterwards, up to 12 GPU-hours are burned producing a report the gate will reject, and the re-run
still has to happen. That makes this decision time-sensitive in a way it was not an hour ago.

**I have not cancelled, resubmitted, or touched it.** If he chooses niter=2 the queued job is exactly right,
and cancelling the critical path on my own judgment is precisely the irreversible call that is not mine.

### The honest trade

- **niter=2 + tol 0.055** (what he approved at 19:47Z): 0/48 realized exceedance — empirically clean. But
  the window to C is **0.1428 pp**, 0.055 sits **0.0192 pp** below C, and **the niter=2 max is still growing
  with seed count** (+0.2291 pp over the last expansion). Another expansion of that size would put the max
  at ~5.61%, past both 0.055 **and** C = 5.5192% — a ceiling no tolerance can move. Separately 0.055 goes
  inert at R <= 1.123596, only **0.391%** below measured R.
- **niter=3 + keep 0.05**: 0/48 at the *existing* tolerance, 8.7x the window, a max that did not move under
  a 3x seed increase, and 1.17% R margin before 0.05 goes inert. Costs: the powered-closure re-run above,
  a pin cascade (`NOMINAL_SEED_POLICY`, `FROZEN["seed_policy"]`, validator, `test_b1_normalization_fix.py`),
  and — **the part that is genuinely his and not mine** — it changes the nominal estimator from 2 to 3
  OmniFold iterations, which moves the published central values, not merely a gate threshold.

**Recommendation, on robustness: niter=3.** The deciding fact is not that its numbers are prettier but that
niter=2's max sits 0.14 pp from an immovable ceiling *and has not stopped rising*, so niter=2 buys a gate
that may fail a correct unfold on the next 48 seeds. But the central-value change and the 56355818 re-run
are costs only he can accept.

**Nothing applied. Nothing frozen. Nothing staged. Nothing committed. No job cancelled.**

## 00:25Z — quiet cycle. Decision window still fully open; wakerctl false alarm avoided (third variant).

    56355818  PENDING  prio 68512   sacct Start=Unknown, Elapsed 00:00:00 -> HAS NEVER STARTED
    56375160  COMPLETED (reported and mailed at 00:15Z)
    56160911  cron     PENDING (BeginTime), healthy
    inbound  nothing (1d and 2h both empty; last is still his 20:56Z)

**The decision window has not closed.** `56355818` has never started, so choosing niter=3 today would
still waste **zero compute** — only the ~21h of queue position already spent. That was the time-sensitive
part of the 00:15Z mail and it remains true.

No mail this cycle: I sent a substantial decision mail ~10 minutes ago, he has not replied, and nothing has
finished since. A second mail with no new content is the spam the standing instruction forbids.

### I almost declared wakerctl broken for the THIRD time. It is healthy.

`python3 docs/orchestration/wakerctl.py status` failed with
`SyntaxError: future feature annotations is not defined` at line 14. Earlier today I twice asserted
wakerctl was broken on indirect evidence and was wrong both times, so this time I attributed the error
before believing it:

    login20:  python3 -V  ->  Python 3.6.15
    `from __future__ import annotations` requires 3.7+

**It is an interpreter mismatch, not a defect.** The login node's default `python3` is 3.6; the wakerctl
cron job runs under `/usr/bin/python3.11` (visible as the job *name* in `squeue`). Re-run correctly:

    /usr/bin/python3.11 docs/orchestration/wakerctl.py status     -> exit 0, clean JSON
    /usr/bin/python3.11 docs/orchestration/wakerctl.py preflight  -> PASS, python=/usr/bin/python3.11

And the watch that matters is intact:

    {"watch_id": "pwclosure-56355818", "kind": "slurm-job", "state": "armed",
     "armed_at_utc": "2026-08-05T14:23:14+00:00", "fired_at_utc": null, "unreliable": 0}
    17 watches total, 1 armed

So the session-independent notification path for the critical path is live. Recorded in
[[perlmutter-root-tf-env-split]] with the root cause, because three false alarms on one component in one
day is a pattern about my diagnosis, not about wakerctl: **check `python3 -V` before reading a traceback
as a verdict.**

Nothing edited, frozen, staged or committed.

## 00:50Z — Joseph asked whether agy really hadn't helped. It HAD, and I under-credited it TWICE.

He asked: *"Has agy really not helped with the niter 2 vs 3 decision?"* Checked rather than answered from
impression. **agy helped decisively, and my 00:15Z mail presented the niter=3 recommendation as mine while
omitting that it restores agy's original ranking.** Worse than an attribution slip — the reason agy was
overturned turns out to be an artifact.

### agy's two decisive contributions

1. **Its predeclared falsifier caught an error both I and the first CLI analysis had made.** agy wrote in
   advance (15:30Z, 95% confidence): if the N=240k run yields `sd >= 0.60%`, the spread is
   initialization variance rather than step-limited optimizer noise, the gradient-step confound story
   fails, and **niter 2->3 becomes the answer**. At 17:45Z the 16x step scan gave obs/pred sd ratios of
   1.00 / 1.79 / 4.39 — the `1/sqrt(steps)` law **refuted**, exactly as agy predicted.
2. **Its Rank 1 — niter 2->3, KEEP tol 0.05 — is what the 48-seed data now supports.**

### The 19:25Z inversion that overturned agy was a SMALL-SAMPLE ARTIFACT

That entry compared two **16-seed** sd estimates and concluded "sd GREW 56%", cutting the k=3 clearance to
2.50 sigma and a 0.62% false-reject, which flipped the ranking to niter=2 + 0.055 — the option he approved
at 19:47Z. Recomputed on the same seeds vs the full 48:

    niter=2   sd(seeds 7-22) 0.7477%  ->  sd(48) 0.8153%   (+9.0%)
    niter=3   sd(seeds 7-22) 1.1703%  ->  sd(48) 0.8444%   (-27.8%)
    sd_3/sd_2:  1.565x at n=16   ->   1.036x at n=48        <- essentially EQUAL

So **agy's assumption that sd is ~unchanged at k=3 was correct within 4.2%** (assumed ~0.81%, measured
0.8444%), and its projected clearance of **F+3.5 sigma measures F+3.35 sigma**. The "56% growth" was two
noisy 16-seed variance estimates being differenced.

### The ranking RE-INVERTS, restoring agy's Rank 1

| config | clearance | gaussian false-reject | observed |
|---|---|---|---|
| niter=2, tol 0.050 (status quo) | 1.47 sigma | 7.07% | **6/48** |
| niter=2, tol 0.055 (**he approved this**) | 2.08 sigma | 1.86% | 0/48 |
| **niter=3, tol 0.050 (agy Rank 1)** | **3.33 sigma** | **0.043%** | 0/48 |
| niter=3, tol 0.055 | 3.92 sigma | 0.0044% | 0/48 |

**niter=3 + 0.050 beats niter=2 + 0.055 by ~43x on false-reject** — and it **raises no tolerance at all**,
so it satisfies "never raise a tolerance" in form as well as substance. The approved option is the only one
of the two that touches a tolerance, and its statistical case rests on the artifact above.

This also strengthens my 00:15Z recommendation with a better argument than the one I gave. I argued
niter=3 from window width and the still-rising niter=2 max; the stronger argument is that **agy's original
quantitative case was right all along** and the campaign detoured through niter=2+0.055 for ~5 hours
because of a 16-seed variance estimate.

### Process failure of mine, stated plainly

His standing instruction (13:12Z, reinforced 15:18Z: use a *different account*) is to route a held
decision through another LLM **before** escalating it to him. I mailed the 00:15Z recommendation on the new
48-seed data **without** doing that. Corrected now: agy is running on the pooled data
(`/pscratch/sd/j/josephrb/q_agy5.txt`, effort high, READ-ONLY), asked adversarially to attack all four of
my claims, to say whether the 19:25Z inversion was defensible *on the data it had* (F-test / chi-square CI
on the variance ratio, not hindsight), whether it still endorses Rank 1, whether a gaussian false-reject
figure is trustworthy at 0/48, whether the 56355818 voiding chain really holds in source, and whether the
central-value change should dominate the statistics.

Nothing edited, frozen, staged or committed.

## 00:55Z — 56355818 IS RUNNING, and agy's verdict landed in the same minute. Both mailed.

**`56355818` STARTED at 00:51:36Z on nid002356**, after ~21.5h pending. 12h wall, no resume, so it ends
~12:51Z. Confirmed from `sacct` (`Start=2026-08-05T17:51:36`, `TimeLimit=12:00:00`), not from squeue alone.
Its `weights.slurm-56355818` directory has appeared. The critical path is finally moving.

**This closes the free window I flagged at 00:15Z.** The job runs at niter=2, so if niter=3 is adopted the
job is voided and its compute is wasted. At the moment of mailing it was ~2 minutes in, so cancelling was
still nearly free; the price rises with every hour. **I have not cancelled it.** Cancelling the critical
path is irreversible and is his call — and if he picks niter=2 the running job is exactly what is wanted.

### agy's verdict on the 48-seed data: endorses niter=3 + KEEP tol 0.05

`q_agy5.agy.txt`, rc=0, 64s, 7,817 bytes. It confirmed **all four** of my claims and — importantly —
reproduced my F-test independently to the same interval:

    F = 2.4498, df (15,15);  95% CI for sd ratio [0.925, 2.648];  p = 0.091 (I measured 0.093)
    agy's words: "premature over-interpretation of sampling noise"

So the 19:25Z inversion is confirmed **not significant on the data it had**, by a separate account
computing it independently. That is the strongest form this correction could take.

**Two things agy added that I had missed:**

1. **Fisher's exact test on realized exceedances** (6/48 vs 0/48 at tol 0.050) gives **p ~ 0.026**. The arms
   differ significantly with **no gaussian assumption at all**. My case leaned on the gaussian plus raw
   counts; this is the distribution-free version of the same claim, and it is the better argument.
2. **The n=16 variance comparison was PAIRED, not independent.** Both arms use identical seeds, so a
   two-sample F-test was not even the right test — and the pairing makes that fluctuation *less* meaningful,
   not more. My own F-test was conservative in the wrong direction.

It also verified the voiding chain in source with line cites and found **one check I had not cited**:
`validate_pet_nominal_gate4.py:937` `freeze:seed_policy` asserts the persisted artifact's `seed_policy`
equals `FROZEN`, on top of `:789-795` `powered:nominal_configuration`. Verdict: *"YES, job 56355818 will be
voided if niter=3 is adopted."*

On central values it gave the one correct conditional: niter=3 moves the unfolded central values, so it is
acceptable **only if those are still unfrozen/unblinded** — his knowledge, not mine, and flagged as such
rather than assumed either way.

### Sent

One mail, both channels: SMTP + Gmail draft (`r8968033757792590850`), queue drained clean.
PushNotification correctly declined as redundant (terminal active).

### A third instance of the watcher-self-match defect, mine

My background watch for agy polled `pgrep -f "bin/agy -p"` — but the watcher's **own** command line contains
that string, so it matched itself and would never have exited. Same family as the 23:00Z noise defect and
the `[[ -s FILE ]] && skip` scripts: **a watcher whose liveness signal is indistinguishable from its subject
is not a watcher.** The real signal was in the driver log all along (`rc=0 end=00:50:08Z bytes=7817`).

Nothing edited, frozen, staged, committed, or cancelled.

## 01:20Z — JOSEPH DECIDED: niter=3. Job cancelled, re-issue LANDED as `2b2e5f1`, closure re-submitted.

His instruction: *"cancel 56355818 and switch to niter=3"*, then *"Re-issue as soon as everything is
good. Is there a place to record this mishap in docs/orchestration?"*

### 1. Cancelled

`scancel 56355818` at 00:57Z, **5:18 elapsed** of 12h. `sacct` -> `CANCELLED`. Only preflight artifacts
and an empty `weights.slurm-56355818` existed; no report was produced, so nothing was lost but ~5 GPU
minutes. Catching it minutes after dispatch rather than hours is the entire value of having flagged the
window at 00:15Z.

### 2. Two things verified BEFORE editing, either of which would have forced more re-runs

- **Item 4's ordinary closure receipt SURVIVES the switch.** `check_closure_provenance` returns True,
  11/11, with `FROZEN["seed_policy"]["niter"]` patched to 3 — the provenance check never references
  `niter`, and Step 3 legitimately runs at its own `--niter 2 --epochs 6` (`RESTORE:942-944`). So item 4
  did **not** need re-running.
- **The powered-closure launcher's shell pins are unaffected.** It pins `DRIVER`
  (`closure_powered_truth_reweight.py`), `PREFLIGHT`, `INPUTS`, `PRODUCER` — **not**
  `train_fullevent_nominal.py`. Changing `NOMINAL_SEED_POLICY` therefore does not trip its
  self-checks. (It also means the launcher does not pin the seed policy it claims to inherit. Real gap,
  recorded, not fixed here.)

### 3. Edits — six sites, surveyed before touching any

    train_fullevent_nominal.py:51            NOMINAL_SEED_POLICY niter 2 -> 3
    validate_pet_nominal_gate4.py:92         FROZEN["seed_policy"] niter 2 -> 3
    test_pet_nominal_gate4_validator.py:69   the INDEPENDENT retyped literal, 2 -> 3
    validate_pet_nominal_gate4.py:~125       status PROVISIONAL... -> MEASURED_20260806_B1_48SEEDS_NITER3
                                             (value HELD at 0.05 -- no tolerance was raised)
    test_b1_normalization_fix.py:~758        the VACUOUS test, repaired
    test_b1_normalization_fix.py:~929        renamed test_tolerance_is_marked_provisional

`:69` matters: it deliberately retypes the policy rather than reading `FROZEN`, with a comment saying
that reading `FROZEN` would make the freeze check compare `FROZEN` with itself — the exact defect audit
B2 found in four other checks. So it had to move deliberately, and it is load-bearing that it did.

`:877` needed **no** change: its fixture deviation is ~11.998%, so it retains power against a tolerance
held at 0.05. It would only have gone weak had the tolerance been raised.

### 4. The vacuous test, repaired and PROVED non-vacuous by mutation

It hardcoded `R, acc, k = 1.135, 0.621, 2` and bounded the tolerance above by the defect signal
`(R-1)/R`. Now reads `R` and the acceptance from the **tracked** Gate-2 receipt
(`step1_class_ratio.R`, `.telemetry.n_signal_pass_reco / n_signal_rows`) and `niter` from `FROZEN`,
asserts the soundness condition `2(1-a)^k < 1`, and bounds by the ceiling `C = (R-1)/(2R)`.

Mutation-tested rather than trusted:

    tol := C            -> FAILS (good: catches an inert tolerance)
    tol := (R-1)/R      -> FAILS (good: the OLD upper bound is now rejected)
    tol := 0.01         -> FAILS (good: below the structural floor)
    niter := 1          -> FAILS (good: 2(1-a)^k >= 1, the leg would reject a correct unfold)
    status := PROVISIONAL -> FAILS (good)

Two mutations correctly **pass**: `tol := 0.055` (genuinely < C) and `niter := 2` (0.05 genuinely sits
between F_2 and C). I initially mislabelled those as vacuity; they are not. **The closed-form window
cannot discriminate niter=2 from niter=3 — only realized exceedance can (6/48 vs 0/48).** Worth stating
because it bounds what this test is for.

### 5. A gap of the same species as item 4, caught before committing

The new status string cites a 48-seed measurement — and the four B1 receipts were **untracked and did
not exist locally at all**. A status claiming `MEASURED` while citing evidence in no clone is precisely
the item-4 defect. All four are now committed (0 embedded pins each, digests byte-verified against the
cluster) and bound in the re-issue's `evidence_bindings`.

### 6. The re-issue

`state/p3f-pet-gate4-launch-code-gate-20260806.json`, generated by a script that computes digests **at
write time, after** the edits landed — the ordering the 12:58Z entry says is load-bearing. **10 binding
moves**, exactly the 10 predicted. 17 code bindings (16 + `closure_ordinary_receipt`, in `files`
because `--closure-report` is a required argument and the gate genuinely reads it) plus 4
`evidence_bindings`. `20260801b` retired under the D3 convention: `status: SUPERSEDED`,
`superseded_by`, `files` -> `files_at_issue`, every `sha256` -> `sha256_at_issue`.

Local verification: **verifier 10 mismatches -> 0, ALL BINDINGS INTACT** (116 resolved / 112 OK);
pytest **698 collected, 7 failed / 690 passed / 1 skipped** — the 2 `test_hash_bindings` guards went
GREEN, leaving only the documented pre-existing 7. **Collection count unchanged at 698.**

### 7. Committed, pushed, pulled

`2b2e5f1`, 16 files, staged by explicit path (never `git add -A`). Pushed; `origin/main` == local.
The cluster pull **aborted exactly as predicted** on 5 untracked paths (the closure receipt plus 4 B1
receipts), not 1 — the trap scales with the number of newly-tracked products. Moved aside to
`/pscratch/sd/j/josephrb/preserved-20260806/`, pulled `--ff-only`, and re-verified every restored
digest. Cluster now at `2b2e5f1` with `niter: 3` live in both policy sites.

### 8. Powered closure re-submitted at niter=3

    56381674  pwclosure  PENDING  prio 67679   12h wall, qos=shared, 1 GPU, launcher UNMODIFIED

Job id captured from `sbatch`/`squeue`, not typed. `RUN_ID="slurm-${SLURM_JOB_ID}"`, so no artifact
collides with the cancelled run, and there is no skip-if-exists guard that could make it a no-op.

### 9. The mishap is recorded where he asked

`docs/orchestration/FINDING-20260806-campaign-pin-inverted-on-insignificant-variance.md`, plus ledger
row **BEN-025** in `FINDINGS.md` (the reusable-methodology genre, alongside BEN-023/024). Eight
concrete prescriptions, the load-bearing ones being: never escalate "X changed by N%" from sample
statistics without an interval; paired designs get paired tests; to overturn an assumption show the
data EXCLUDES it; re-route through the second account after every material data change; and never
hardcode an operating point in a test that guards an operating-point-dependent bound.

### 10. Watches re-pointed

`pwclosure-56355818` **fired at 01:03:02Z** on the cancellation and mailed (ledger `rc=0`), so Joseph
has a "56355818 left the queue" mail reporting CANCELLED with no report — accurate, but it looks like a
failure without context. Now disarmed. `notify_pwclosure.sh` **parameterised** (job id was hardcoded in
4 places; a re-run would have mailed sacct for a dead job) and `pwclosure-56381674` armed, verified by
composing the body with the send suppressed.

Cluster suite verification running as `56381705` on nid004164 (compute, not login), via a runner that
writes full output to a **file** rather than piping through `tail` — the 13:40Z lesson.

## 01:50Z — he asked "Status update?"; answered on BOTH channels

Mail 01:35:59Z, full text fetched: *"Status update?"* — no further instruction. Answered immediately
rather than waiting for the cluster suite, because a direct request outranks my batching preference.

Sent as **SMTP mail AND a Gmail draft** (`r-8283599444821305033`, threaded into `[MNV-AUTO]`). The
reason for both is recorded in this thread's own history: an earlier session searched his Gmail with
`in:anywhere` and found **zero** mail from `nersc.gov` or `perlmutter`, i.e. **SMTP delivery is
UNVERIFIED** — the relay accepting a message is not delivery. He confirmed at 19:18Z that the *drafts*
reach him. So the brief's claim that SMTP is "the ONLY working outbound path" is half right: it is the
only path I can *originate*, but the draft is the only one **observed** to arrive. Both, every time.

Reported: the switch is committed as `2b2e5f1` and pulled on the cluster; the tolerance was held at
0.05 so nothing was raised; `56355818` cancelled at 5:18 and `56381674` re-submitted at niter=3; the agy
correction (its Rank 1 was right, my 19:25Z inversion was p=0.093); the mishap recorded as a FINDING
plus ledger row BEN-025; and the two same-species gaps caught before committing (item 4's receipt and
the four B1 receipts were both untracked and absent locally, so the binding and the new MEASURED status
would each have cited evidence in no clone).

Also warned him about the wakerctl mail he may have received: `pwclosure-56355818` fired at 01:03Z on
**my** cancellation and reported CANCELLED with no report. Accurate, but it reads as a failure without
context.

### State

    56381674  pwclosure  PENDING   prio 67713   niter=3 re-run; watch armed
    56381705  suite      RUNNING   37:35        block-buffered, in the ~31 min verifier phase
    56160911  cron       PENDING (BeginTime), healthy

Expectation on record for the cluster suite, so it can be checked rather than rationalised afterwards:
**752 collected** (the 750 cluster baseline plus item 1's two new tests) and **0 binding mismatches**.
750 or 754 would be a discrepancy to chase, not rounding.

Nothing edited, staged or committed beyond `2b2e5f1`.

## 01:55Z — CLUSTER SUITE: the re-issue is verified. And the job's "FAILED" was MY invocation bug.

`56381705` reported `FAILED`, `ExitCode 0:15`, 38:18 — and the watch fired on its failure branch, which
is exactly why that branch exists. But **the suite completed and wrote its result** before dying:

    2 failed, 750 passed in 2291.19s (0:38:11)      ->  752 collected

**752 is the number I predeclared** at 01:50Z before seeing it (750 cluster baseline + item 1's two new
tests). And **both `test_hash_bindings.py` tests PASSED on the cluster** — they are absent from the
failure list, so the re-issue closes the bindings against all ~856 pins, not merely the ~116 that
resolve locally. That is the verification that actually matters; a green local run leaves 740 pins
unexamined.

Arithmetic reconciles exactly against the 13:40Z cluster baseline of 4 failed / 746 passed:

    4 failed - 2 (both hash-binding guards now green)                = 2 failed
    746 passed + 2 (item 1's tests) + 2 (the guards now passing)     = 750 passed

The 2 remaining failures are the documented untracked-only pair, unchanged and not repo defects:

  - `test_resume_guard.py` — the three cluster-only `[[ -s ... ]] && skip` scripts
    (`pet/orchestrate_gpu_node.sh:33`, `sbatch_boot5d_gpu_interactive.sh:23`,
    `sbatch_bootstrap_5d_gpu.sh:18`). Not in git, so not fixable by a commit; deletion sits behind the
    reorg freeze tag. Still Joseph's call.
  - `test_uq_remediation.py` — the J28 flux guard rejecting its own synthetic fixture for lacking a
    per-universe flux stamp. Untracked, absent locally, red since ~07-31.

### MY BUG: I ran the suite EIGHT times concurrently

`srun -N 1 -c 32` with **no `-n 1`**. srun therefore launched 8 tasks, each running the entire suite —
including `test_hash_bindings`, which spawns its own ~31-min verifier over ~1 TiB. So this was 8x the
intended I/O on a shared filesystem, i.e. the "throttled and antisocial" behaviour the brief warns
about, merely relocated from a login node to a compute node.

The `FAILED 0:15` is a second-order consequence, not a real failure: task 5's pytest exited 1 because
2 tests legitimately failed, and srun killed the remaining tasks — `CANCELLED ... DUE TO TASK FAILURE`.
A suite with any failing test will always make srun report the step as failed.

**And I had the evidence and missed it.** The driver log printed "The following have been reloaded with a
version change" **eight times** at 01:14Z, and I read past it twice this cycle. Eight copies of a
one-task message is a task-count signal.

Consequence for the result's provenance: all 8 tasks wrote to the SAME output file with `>`. The content
is internally coherent and self-consistent (2 FAILED lines listed, counts agreeing, one timing line),
and it matches the predeclared 752 — so I believe it. But "8 writers, one file, truncating" is not a
provenance I will certify a gate on.

### Clean confirmation launched

`56383493`, **`-n 1`** this time, writing each number to its own file: `pytest --collect-only -q` for an
authoritative collection count, and the standalone verifier for an authoritative mismatch count. ~31 min.
Recording the expectation first, again: **752 collected, 0 mismatches, ALL BINDINGS INTACT.**

Nothing edited, staged or committed beyond `2b2e5f1`.

## 02:25Z — CLEAN VERIFICATION COMPLETE (see also the 02:50Z entry at the end). The re-issue is fully verified on the cluster.

`56383493`, single task (`-n 1`), nid004143, `HEAD=2b2e5f1`, 01:54:17Z -> 02:25:19Z. Each number to its
own file, no shared-writer contention.

    collection:  752 tests collected        (also 752 by counting node ids directly)
    verifier:    rc=0   mismatches=0
                 resolved 861 bindings (260 unresolvable)
                 857 OK
                 ALL BINDINGS INTACT

**All three predeclared expectations met exactly**, each written down before the number existed:

| claim | predeclared | measured |
|---|---|---|
| cluster collection | 752 | **752** |
| binding mismatches | 0 | **0** |
| `test_hash_bindings` guards | both green | **both green** |

### The arithmetic reconciles completely

Against the pre-re-issue cluster figure at `61f2fb2` (856 resolved / 844 OK / 8 mismatches / 4 known
drift, and `844 + 8 + 4 = 856`):

    resolved  856 -> 861   = +5   exactly the five newly-committed receipts
                                  (closure_fullevent_fps.json + 4 B1 receipts)
    OK        844 -> 857   = +13  = 8 repaired mismatches + 5 new pins
    mismatches  8 -> 0
    known drift 4 -> 4     unchanged (the wakerctl submit-time provenance pair)
    closure:  857 + 0 + 4 = 861

Nothing unexplained, no residual, and the +5 confirms the newly-tracked receipts are genuinely being
walked on compute rather than merely committed. That was the point of tracking them: on 08-05 those pins
would have been counted `unresolved` and silently skipped in every clone.

### What this closes

RESTORE Step 2b is **DONE**. All four owed items landed in one commit, the gate is re-issued, and both
the local (116 pins) and cluster (861 pins) verifiers are clean. The two remaining cluster test failures
are the untracked-only pair and are not repo defects.

### What remains

    56381674  pwclosure  PENDING  prio 67743  -- the niter=3 powered closure, 12h wall, no resume

That is now the **only** thing between Gate-4 and a runtime verdict. gap/floor stand (training-independent,
0.2343 / 0.0459); the open number is `residual <= 0.0469`, i.e. recovery >= 0.80. Nothing speeds it; the
wakerctl watch `pwclosure-56381674` will mail the verdict independently of this session.

### Also worth recording: a small extraction bug of mine, and why it did not matter

My runner printed `COLLECT: ` empty — `tail -2 | head -1` grabbed the file's trailing blank line instead
of the count. The count was in the file the whole time, and I read it from the file rather than trusting
the summary line. That is the 13:40Z lesson working as intended: **write the full output to a file, then
read the file.** Had the runner only echoed a summary, this would have cost a re-run.

Nothing edited, staged or committed beyond `2b2e5f1`.

## 02:50Z — "Do you need me to make any decisions?" — No. Answered, with four items surfaced.

Mail 02:29:59Z. Answered on both channels (SMTP + Gmail draft `r-6297203775878288356`). The answer is
that **nothing is blocked on him**, and I deliberately kept it short — the previous two mails were long
and he asked a yes/no question.

Everything verified; the whole remaining critical path is one queued job:

    56381674  pwclosure  PENDING  prio 67773 (67713 -> 67743 -> 67773)  never started (Start=Unknown)
    56160911  cron       PENDING (BeginTime), healthy
    wakerctl  pwclosure-56381674  armed, unreliable=0, the only armed watch

**Four things surfaced as his eventually, none urgent.** Recording them here so they cannot quietly become
invisible again — three of the four are only visible on the cluster:

1. **The nominal training launch.** Gate-4 remains `PASS_CODE_ONLY` with
   `nominal_pet_training_allowed: false`. Authorising the nominal to run is a separate decision he owns,
   and it only becomes live if `56381674` passes.
2. **The three untracked cluster-only `[[ -s FILE ]] && skip` scripts** keeping `test_resume_guard` red.
   Not in git, so no commit fixes them; deletion is behind the reorg freeze tag. The test fires correctly
   on real risk — a stale script on the cluster can still be run.
3. **`test_uq_remediation.py`'s J28 flux fixture.** Deciding fixture-stale vs guard-over-strict touches
   the flux covariance whose corrected sizing is still pending, so it is a decision, not a cleanup.
4. **The two narrative docs** (`AUTONOMOUS_LOG`, `HANDOFF`) remain untracked by choice; his call.

**And one thing I asked him to sanity-check rather than decide:** niter 2 -> 3 changes the nominal
estimator from 2 to 3 OmniFold iterations, so it **moves published central values**, not just a gate
threshold. agy's caveat is the right one — acceptable only if those values are still unfrozen/unblinded.
He knows whether anything downstream has been quoted at niter=2; I do not, and I said so rather than
assuming. This is the one residual risk in today's change that I cannot close myself.

Nothing edited, staged or committed beyond `2b2e5f1`.

## 03:20Z — quiet cycle. Queue position measured properly after I botched it once.

    56381674  pwclosure  PENDING  prio 67803  never started (Start=Unknown)
              priority track: 67679 -> 67713 -> 67743 -> 67773 -> 67803  (~60/hr)
              rank 45 of 1162 pending in shared_gpu_ss11; 44 ahead; 86 running
    56160911  cron       PENDING (BeginTime), healthy
    wakerctl  pwclosure-56381674 armed, unreliable=0
    inbound   nothing newer than his 02:29Z, which I answered at 02:50Z

**A miscomputation of mine, corrected in the same cycle.** My first rank query printed
`rank ~47 of 47`, which is nonsense — I used `NR` outside an `END` block, so it reported the current
record number rather than the total. Recomputed properly by counting pending jobs with strictly higher
priority: **44 ahead, rank 45 of 1162.** Recording it because a plausible-looking bogus number is exactly
what this campaign has been burned by, and the fix is the same each time: compute it, do not eyeball it.

**Honest ETA, since it is the only thing he actually wants to know.** For calibration, `56355818` was at
rank 24 of 1158 (prio 68427) at 22:58Z and dispatched at 00:51Z, ~2h later. We are at rank 45 accruing
~60 points/hr. So dispatch is plausibly several hours out, then 12h of runtime: **Gate-4's runtime verdict
is realistically 12-24h away.** Nothing compresses that — the two training-independent criteria are
already receipted, and the only open number needs the full training.

No mail this cycle: his 02:29Z question was answered at 02:50Z, and a priority counter ticking up is not
news. The durable watch reports the verdict without this session.

Nothing edited, staged or committed beyond `2b2e5f1`.

## 03:50Z — no-change cycle. Adopting a logging policy so this file stays readable.

    56381674  PENDING  prio 67833 (was 67803)  rank 44 of 1151 (43 ahead)  advanced 1 place in 30 min
    56160911  cron PENDING (BeginTime); wakerctl observing live at 03:49:42Z
    watch     pwclosure-56381674 armed, unreliable=0
    inbound   nothing newer than his 02:29Z (answered 02:50Z)

**Decision, recorded once rather than re-stated hourly:** while the only open item is a queued job whose
state cannot change except by dispatching, I will **not** append a section per polling cycle. This file is
already 2,300+ lines and "still PENDING, priority +30" repeated every half hour degrades it as a handoff
artifact — the thing it exists to be. From here I log only **material** changes: dispatch, completion,
any verdict, inbound instructions, or anything I get wrong. Polling continues every cycle regardless; the
absence of entries below means the absence of change, not the absence of checking.

Nothing edited, staged or committed beyond `2b2e5f1`. Trees: local == origin == cluster == 2b2e5f1.

## 04:40Z — out-of-band audit landed three corrections to me. All three acted on.

Pulled **`8d6e358`** ("Give Claude agents an entry point, and make findings reachable") on both trees.
It adds the `CLAUDE.md` this repo never had — the root cause of recorded lessons not reaching the agents
that needed them, since Claude Code does not auto-load `AGENTS.md` — plus a long-form index at the top of
`FINDINGS.md` (9 of 10 `FINDING-*.md` were unindexed), and rows BEN-026/027/028.

### 1. The niter question is CLOSED, and I owed two consequences I had not recorded

The audit checked `values.tex`, `paper_body.tex`, `VALIDATION_LEDGER.md`, `CLAIMS.md`: **nothing
downstream is quoted at niter=2 for the estimator I changed.** The note's PET numbers are the
RECOIL-ONLY track (`paper_body.tex:163` captions it as a cross-check), that legacy arm is niter=**5**,
the total/trace/four entries are QUARANTINED, and `paper_body.tex:156` says outright that the full-event
estimator receives a fresh uncertainty budget. So the residual risk I flagged at 02:50Z is closed.

**But two consequences of the switch were missed in my framing, and both are mine to own:**

  (a) **`niter` is a REGULARIZATION parameter, not a threshold.** More iterations = less regularization
      = more variance, less bias. Everything in `2b2e5f1` and in the FINDING argues the choice from
      **gate behaviour** — 0/48 vs 6/48, window width, false-reject. That shows the choice is *sound*.
      **It does not show it is right.** A B1 closure passing is not a bias-variance argument. I framed a
      regularization decision as a gate-clearance decision for the entire day and nobody caught it,
      including me, including both advisors.
  (b) **The uncertainty budget must be RECOMPUTED at niter=3.** Any covariance component derived at
      niter=2 is now inconsistent with the central value. Nothing in the repo said this until now.

Both recorded in `docs/OPEN_ITEMS.md` as items (d) and (e) under the D2 block — (d) explicitly coupled
to the pending flux covariance sizing, with the sequencing consequence that the J28 fixture question is
now **after** it, not before.

### 2. I was WRONG that the three `[[ -s ]]` scripts could not be fixed

I said repeatedly, including to Joseph by mail, that "no commit can fix them since they aren't in git."
**The freeze tag in `POST_PUBLICATION_REORG_PLAN.md` gates DELETIONS and reorgs, not ADDITIONS.** They
could have been `git add`ed and repaired at any point today. The test's own assert message spells out
that path and I read past it.

Fixed now. All three fetched from the cluster (none existed locally), converted, and committed:

    nd-unfolding/sbatch_bootstrap_5d_gpu.sh:18       -> rg_skip_if_complete + rg_run
    nd-unfolding/sbatch_boot5d_gpu_interactive.sh:23 -> rg_skip_if_complete + rg_run
    nd-unfolding/pet/orchestrate_gpu_node.sh:33      -> rg_skip_if_complete + rg_run (in a subshell)

**Cost of the conversion: zero recompute.** `rg_valid_npz` already exists in `lib/resume_guard.sh` ("an
npz whose central directory is intact and every member decompresses" — exactly the truncated-file case),
and `boot_nd_5d/` holds **100/100 outputs with 0 markers**, so passing it as the validator means the
existing files are validated and *adopted* rather than re-run. Without the validator all 100 would have
been redone.

**The test taught me two invariants I did not know, and I got both wrong on the first attempt:**

  - `test_every_guarded_output_has_a_producer_stamp` — a guard with no matching `rg_run`/
    `rg_mark_complete` for the same output token never skips, so every run redoes everything. Safe
    direction, still a bug, silently burns the allocation. My first patch had exactly this.
  - `test_every_rg_caller_sources_the_library_first` — and it reads the first *mention* as the first
    use, so naming `rg_skip_if_complete` in an explanatory comment ABOVE the `source` line trips it.

**And one bug I introduced and caught myself, by reasoning about bash rather than by a test:** an
env-assignment prefix is scoped correctly for an external command but for a shell FUNCTION bash leaves
the variable set in the caller. So rewriting `CUDA_VISIBLE_DEVICES=$gpu bash "$PAYLOAD"` as
`... rg_run ... bash "$PAYLOAD"` would have leaked `CUDA_VISIBLE_DEVICES` into the next iteration and
pinned every later replica to GPU 0 — a silent 4x throughput loss in a script whose whole purpose is
one-replica-per-GPU. Wrapped in a subshell, with the reason in a comment so it is not "tidied" away.

Recorded as **BEN-029**, since `rg_run`'s own docstring says the BEN-023 conversion is repo-wide (~60
launchers) and the next agent doing one will hit both traps.

### 3. Durability, per the audit's item 4 and CLAUDE.md's "scratch is purgeable"

`notify_pwclosure.sh` — the thing that delivers the critical-path verdict — existed ONLY as an untracked
file on purgeable scratch while `56381674` sits in queue. Now committed. Its body mails
"Log: nd-unfolding/pet/AUTONOMOUS_LOG_20260805.md" to a reader who could not find it in git; rather than
delete the line I tracked the log, which makes the reference true. The `HANDOFF` doc goes with it. The
waker `LEDGER.tsv` stays untracked deliberately — it is live runtime state and would produce a diff on
every tick.

Verification: verifier **0 mismatches, ALL BINDINGS INTACT**; `test_resume_guard.py` **21/21 passed**
(was 2 failed); full suite **698 collected, 690 passed**, the same documented pre-existing 7, so
**collection is unchanged and no new failure was introduced.**

## 05:35Z — CLUSTER SUITE AT ITS FLOOR: 1 failed / 751 passed. Receipt for `62eab87`.

`56388888`, nid004164, **`NumTasks=1`** (verified with `scontrol`/`sacct`, not inferred), 05:02:35Z ->
05:34:40Z, `COMPLETED 0:0`, 32:03.

    1 failed, 751 passed in 1923.83s        ->  752 collected
    only failure: test_uq_remediation.py::UnifiedThrowTests::test_synthetic_slab_and_block_combine_end_to_end
    test_hash_bindings: ZERO mentions in the whole log -> both guards PASSED -> 0 binding mismatches
    test_resume_guard:  ABSENT from failures -> PASSED on the cluster

**All three predeclared expectations met exactly**, written down before the run:

| claim | predeclared | measured |
|---|---|---|
| cluster collection | 752 | **752** |
| suite | 1 failed / 751 passed | **1 failed / 751 passed** |
| binding mismatches | 0 | **0** |

This closes the gap I had explicitly flagged to Joseph as "an EXPECTATION, not a measurement". Running it
was not invented work: the prior full-suite figure came from the contaminated 8-copy run AND predated the
three shell-script repairs, so nothing had actually measured the tree I pushed.

**The cluster suite is now at its floor.** The single remaining failure is the J28 flux fixture, which the
audit sequenced to come **after** the niter=3 covariance recompute (OPEN_ITEMS item (d)) — resolving it now
would risk doing it twice against a moving target. So one known, deliberately-deferred item, and nothing
else red. Track the arc across the day:

    13:40Z  4 failed / 746 passed   (2 hash-binding by design, resume_guard, uq_remediation)
    01:55Z  2 failed / 750 passed   (re-issue landed: both hash-binding guards green)
    05:35Z  1 failed / 751 passed   (resume_guard repaired: the last 3 BEN-023 offenders retired)

**Two instrumentation faults of my own this cycle, both caught before they misled me:**

1. My task-count check was **self-defeating**: I keyed it on counting module-reload banners while the same
   script suppressed module output, so `0` was uninformative rather than reassuring. `scontrol show job`
   is the authority (`NumTasks=1`), and that is what I used. A check whose negative result is
   indistinguishable from "nothing to report" is not a check — same family as the watcher whose liveness
   signal equalled its alarm signal (23:00Z) and the `[[ -s ]]` guards retired this morning.
2. The output file sat at **492 bytes with a 17-minute-old mtime** and read as stalled. It was not:
   `sstat` showed `AveCPU 00:17:59` against 17:25 elapsed (~100% CPU) and `MaxRSS 3.1 GB`. This is exactly
   **BEN-028**, added to the ledger only hours earlier — the entry earned its keep immediately, on the
   first job it could have applied to.

## 12:20Z — `56381674` IS RUNNING. Preflight PASS, and the training-independent claim held EXACTLY.

The niter=3 powered closure dispatched after ~10.9h queued.

    56381674  RUNNING on nid008668   started 2026-08-06T11:52:56Z   12h wall -> HARD KILL 23:52:56Z
    at 12:19:53Z: elapsed 26:58, sstat AveCPU 00:30:05 (~100% CPU), MaxRSS 13.9 GiB
    artifacts appeared: POWERED_PREFLIGHT.slurm-56381674.json, weights.slurm-56381674/

Liveness judged by `sstat` CPU time and produced artifacts, **not** log growth (BEN-028).

### The preflight gate PASSED, and it reproduced the receipted numbers bit-for-bit

`POWERED_PREFLIGHT.slurm-56381674.json`, `verdict: PASS`, `criteria_are_training_independent`:

| quantity | receipted (`PREFLIGHT_GAP_FLOOR.json`) | this run |
|---|---|---|
| `gap` | 0.23427036248451102 | **0.23427036248451102** |
| `floor` | 0.010747273589844064 | **0.010747273589844064** |
| `floor_over_gap` | 0.045875515263074 | **0.045875515263074** |

Identical to the last digit, on a **different job at a different `niter`**. That upgrades "these two criteria
are training-independent so they stand regardless" from an assertion carried all day to a **measured**
fact. It also confirms the niter 2 -> 3 switch perturbed nothing it was not supposed to touch — which was
the one thing that could have quietly invalidated the preflight half of the gate.

**A precision correction to my own shorthand.** I have written "gap/floor 0.2343 / 0.0459" repeatedly,
including in mail. 0.0459 is `floor_over_gap`, not `floor`; `floor` is **0.01075**. The comparison against
the `<= 0.10` threshold was always the ratio, so no conclusion changes, but the label was wrong.

### What is still open

`residual <= 0.0469`, i.e. recovery >= 0.80. That needs the full training and cannot be short-circuited.
Nothing to do but let it run: 12h wall, **no resume**, so a walltime kill is a total loss and there is no
intervention that helps. The wakerctl watch `pwclosure-56381674` reports the verdict independently of this
session, and its notifier is now tracked in git rather than sitting on purgeable scratch.

## 12:50Z — a SECOND session is active in this repo, and the RSS question resolved

### `56381674` healthy; the memory growth is not a risk

    56:58 elapsed, sstat AveCPU 01:04:20 (>100%, multithreaded), MaxRSS 13.9 -> 15.4 GiB in 30 min
    weights.slurm-56381674/ = 2.9M across 6 files  <- real artifact progress, unlike the buffered log

RSS is above the predeclared 12.84 GiB peak sizing and still climbing, so I checked the headroom rather
than either alarming or dismissing: `scontrol` gives `mem=57472M` (~56 GiB, from
`MinMemoryCPU=1796M x 32`). **15.4 of 56 GiB = 27%, i.e. 3.6x headroom** — tripling would not OOM. Not a
risk; still worth watching, since an OOM kill at hour 8 of a no-resume run is a total loss.

### A job appeared that I did not submit: `56397442 b1niter4`

    submitted 2026-08-06T12:24:12Z from login35, same account, QOS gpu_shared, 2h wall, 1 GPU
    prio 67697 (below our 68313, so it queues behind the closure)
    script: nd-unfolding/pet/sbatch_b1_niter4_scan48.sh

Read its header rather than guessing: it is a **B1 rate-injection scan at niter=4, 48 seeds**, and its
comment **explicitly cites `docs/OPEN_ITEMS.md` item (e)** — the regularization-justification gap I wrote
at ~04:40Z. So a second agent session is acting on that entry. Its reasoning is sound and worth recording
because it sharpens my own: the receipted k=2/k=3 pair shows bias 3.8008% -> 2.1876% tracking
`(1-a)^k (R-1)/R` to under 0.1 pp at flat variance, which argues **`k >= 3`, not `k = 3`** — the bias term
is monotone decreasing in k and nothing measured bounds k from above. It measures k=4 (closed form predicts
bias 1.2617%) and predeclares that if the spread is again flat, the record must say plainly that the
stopping point is set by **cost and the literature default**, not by the data. That is a better answer to
item (e) than "the gate passes", which is exactly the criticism the audit levelled at me.

**Coordination note, and it is the live risk now.** BEN-023's corollary: *"two agents each believed they
owned the FPS P4 chain — ownership maps must live in a file agents re-read, not in each agent's memory."*
There are now two sessions writing to this repo. I am NOT touching `56397442`, its script, or
`products/pet/b1_closure/`, and I am not editing item (e) while another session is measuring it. My lane
this cycle is `56381674` only. Recording that division here because a log both sessions can read is the
only place it is real.

## 13:20Z — WATCH ITEM: `56381674`'s working set is growing, and I am predeclaring the escalation rule

Both jobs running: `56381674` at 1:27:07 (12h wall), `56397442 b1niter4` at 23:19 (2h wall, other session's
lane). `56381674` is healthy on CPU (`AveCPU 01:39:18` vs 1:27 elapsed) and past preflight into training —
stdout confirms `preflight PASS -- allocating the training`, stderr shows XLA compiled and batch callbacks
firing. Preflight echo, for the record: `gap=0.2343 (min 0.15) floor=0.0107 floor/gap=0.0459 (max 0.1)
residual_budget=0.0469 budget/floor=4.36x -> PASS`.

### The memory trend, stated as data rather than as reassurance

    elapsed   MaxRSS
    27 min    13.90 GiB
    57 min    15.44 GiB
    87 min    17.64 GiB       AveRSS 17.2 GiB  <- ~= MaxRSS, so the WORKING SET is growing,
                                                  not transient peaks
    limit     56.13 GiB  (mem=57472M, from MinMemoryCPU=1796M x 32)

Observed growth over that window is ~3.6 GiB/h. **Linear extrapolation to the 12h wall gives ~55.5 GiB
against a 56.13 GiB limit** — i.e. marginal, arriving right at the deadline. An OOM kill would be a total
loss (no resume) and the *second* lost attempt at this closure.

I am NOT raising this with Joseph yet, and the reason is the lesson from this morning: extrapolating a
3-point trend for a quantity that normally **plateaus** once caching is done would be precisely the
small-sample overreach of BEN-025. Training-phase RSS typically flattens after the first epoch; the
inputs are 9.9 GB and both `MultiFold` legs cache early, so the memory-hungry phase is behind it.

### Predeclared escalation rule, fixed now so the outcome cannot be rationalised later

- **RSS > 28 GiB (50% of limit) before 6h elapsed** -> the linear trend is real, not a plateau. Escalate
  immediately with a recommendation to cancel and resubmit with a raised `--mem`, because losing 2-3h is
  strictly better than losing 10h. That is his call, not mine, and it is time-sensitive the same way the
  niter decision was.
- **RSS flattens below that** -> plateau confirmed, no action, no mail. This is the expected case.
- **Either way**: keep sampling every cycle and record the points, so the trajectory is legible to whoever
  reads this rather than living in one session's head.

One incidental observation, not acted on: stderr warns `on_train_batch_end` takes 0.1455s against a
0.0230s batch time — a 6x callback overhead. If that callback accumulates per-batch state it would be both
a throughput drag and a candidate source of the RSS growth. Recording it as a lead for whoever profiles
this later; I am not touching a running critical-path job to chase it.

## 14:20Z — POWERED CLOSURE VERDICT: **FAIL**. And the cancelled niter=2 run could never have passed.

`56381674` ran the **complete protocol** in **1:58:19** and wrote a verdict — rc=3, not a crash.
`DONE.slurm-56381674.txt`: `verdict=FAIL`, `preflight_verdict=PASS`, `preflight_xcheck=AGREE`.
Configuration confirmed from the report: `niter=3, epochs=8, seeds 42/0, batch 512`.

    metric              measured     threshold
    gap                 0.234270     >= 0.15     PASS
    floor_over_gap      0.045876     <= 0.10     PASS
    residual_over_gap   0.453147     <= 0.20     FAIL  (2.27x over)
    recovery            0.546853     >= 0.80     FAIL

`residual = 0.106159` against the 0.0469 budget, 2.26x. Verified by recomputation from the report's own
spectra: `gap` = L1(prior,target) = 0.234270, `residual` = L1(unfolded,target) = 0.106159, and
`recovery == 1 - residual/gap` exactly — so those are **one criterion stated twice**, not two failures.
`floor` = L1(untilted,prior) = 0.010747, which also confirms floor is the sampling-noise scale.

**Not the 08-04 smoke's problem.** That FAIL was the 20k half-size making `floor/gap = 0.4040` unpassable.
Here `floor/gap = 0.0459` with 2.2x margin. This is a genuine under-recovery. **No threshold touched.**

### The finding that matters most, and it cuts two ways

The report's own `samples` block gives `n_step1_a/n_truth_a = 837494/1999920 = 0.418764` — **the
acceptance**. Only 41.9% of truth rows carry information; `RunStep2` pins the other 58.1% to exactly 1.
Applying B1's structural bound `1-(1-a)^k` to recovery:

| k | ceiling | vs predeclared `recovery_min = 0.80` |
|---|---|---|
| 1 | 0.41876 | impossible in principle |
| **2 (old policy)** | **0.66216** | **IMPOSSIBLE IN PRINCIPLE**, short by 0.138 |
| 3 (current) | 0.80364 | achievable, headroom **+0.0036** |
| 4 | 0.88587 | headroom +0.086 |

Measured 0.546853 = **68% of the k=3 ceiling**, sitting between the k=1 and k=2 ceilings.

1. **`56355818` could never have passed.** Its ceiling was 0.662 against a 0.80 bar. I sold Joseph the
   cancellation as a *cost* of the niter=3 decision. It was not a cost — that job was doomed by
   construction and would have burned 12h to prove it. The niter 2->3 switch was not merely
   statistically better for B1; it was **necessary for this criterion to be satisfiable at all.** Nobody
   anticipated that, including both advisors.
2. **`recovery_min = 0.80` was never compared against the achievable ceiling.** At k=3 it leaves 0.36 pp,
   i.e. it demands a near-perfect estimator. Same species as the B1 defect where any `tol >= C` is inert:
   a bar set without checking it against the structural limit. **Not** a proposal to lower it.

**CAVEAT, and it is the first thing to verify:** `1-(1-a)^k` is B1's bound for the fold-forward **RATE**
ratio. I applied it by analogy to a **spectral L1**. Same mechanism (each iteration propagates information
only through accepted rows) and the numbers line up suggestively, but I have **not proven it transfers.**

### Shape of the miss: asymmetric in the tilt direction

    bins 242/244/243  (pt idx 12, tilt UP ~2.65x)     recovery 0.72 / 0.91 / 0.82
    bins 38/57/76/95  (pt idx 2-5, tilt DOWN ~0.55x)  recovery 0.24 / 0.21 / 0.19 / 0.17

89% of displaced bins move the **right** direction — it under-shoots rather than breaking, and resists
moving DOWN. Median per-bin recovery 0.84, but the aggregate L1 is dominated by those large-displacement
failing bins, which is why the headline 0.55 is so much worse than the median. Leading hypothesis: the
step-2 classifier captures the sharp high-pT enhancement and under-fits the diffuse low-pT suppression —
an under-fitting story consistent with ~1.5 effective iterations at k=3, which points at `epochs=8` and
connects to OPEN_ITEMS item (e).

**REFUTED before reporting it:** I suspected the reweight logit cap clipped downward weights. It does not.
`REWEIGHT_LOGIT_CAP = 30.0` spans weights 1e-13..1e13; the injection needs only 0.55..2.65; and the engine
logged **zero** saturation lines. Two independent checks, hypothesis dead.

### The OOM escalation was a false alarm, and I own it

The job finished in 1:58, never near the 56 GiB ceiling. My projection's arithmetic was fine but its
runtime input was wrong — I flagged 5-10h, actual was 2h. Joseph replied "Do (c)" at 13:56Z, five minutes
after the job had already finished at 13:51Z. **I did not queue the hedge**: the premise had evaporated and
executing the letter of an instruction whose purpose is gone would waste a 12h GPU block. Told him so.
The finding *underneath* the alarm still stands: the 12.84 GiB sizing came from a 20k-row 4-minute smoke
that had ~224 GiB allocated, so it never described this 2M-row 56 GiB run.

### Gate-4 cannot PASS

The powered closure is its publication-power evidence and does not clear its own predeclared bar. Evidence
preserved off purgeable scratch (report 32 KB, DONE 755 B, preflight 25 KB); the 20.8 MB artifact npz is
**not** committed pending his say-so.

## 15:10Z — FRESH-CONTEXT CONSULT: it corrected me twice, and the framing was the error

Joseph asked (mail 14:29Z) for a fresh claude-school session's view on the decisions and next steps.
Launched via `ask_claude.sh` (school HOME, `--model opus`, READ-ONLY), 13 min, rc=0, 13,042 bytes.
Transcript committed as `docs/orchestration/CONSULT-20260806-fresh-context-powered-closure.md`.
It was the highest-value consult of the campaign and it overturned my two central claims.

### Correction 1 — `1-(1-a)^k` is an EQUALITY, not a ceiling

Derived from `omnifold.py:198-200,218-220`:
`nu_k(x) = a(x) C_k t(x) + (1-a(x)) nu_{k-1}(x)`, so for x-independent `a`,
`nu_k - t = (1-a)^k (1-t)` pointwise and the spectral L1 follows exactly. **So the transfer I flagged as
unproven DOES hold** — but calling it a *ceiling* let 0.547 read as "68% of the way to a structural limit"
when the ideal limit **predicts** 0.804 and the estimator **missed it by 0.257**. The correct framing makes
the result look worse, not partially excused. Verified the derivation against the source.

### Correction 2 — my number was wrong: `a(x)` spans 0.003 to 0.81

Measured per-bin from the dump. The driver is the **MINOS match threshold**: below `p_parallel` 0.75 GeV
the muon never reaches MINOS. **35 bins with `a_b < 1%` carry 23.2% of the injected displacement mass**, so
by Jensen my global-`a` form was only an upper bound.

    exact per-bin recursion   k=1 0.426   k=2 0.572   k=3 0.635   k=4 0.657   k=8 0.686
    my global-a claim         k=1 0.419   k=2 0.662   k=3 0.804   k=4 0.886   <- WRONG

Confirmed, not fitted: over the 121 bins carrying the top 90% of displacement mass, measured vs predicted
per-bin recovery gives **Pearson 0.862 / Spearman 0.879**, weighted signed means agreeing to **0.3%**.
**Measured 0.5469 against an achievable 0.6347.**

Consequence (i) **survives and strengthens** — `niter=2`'s ideal is 0.572, further below 0.80, so
`56355818` was unpassable. Consequence (ii) **retracted and reversed**: the bar sits **16.5 pp ABOVE** the
achievable, not 0.36 pp under a ceiling. Unreachable at any practical `k` (~100). **No `k` fixes this.**

### Correction 3 — my tilt-direction diagnosis was CONFOUNDED, and I verified that myself

`cell = i_pt*19 + i_pp`, checked against the report's own edges: bins 38/57/76/95 are **all four at
`i_pp = 0`** (`p_parallel` 0.0-0.75 GeV, `a_b = 0.003`); 242/243/244 at `i_pp = 14/15/16` (10-40 GeV,
`a_b ~ 0.64-0.71`). My 0.17-0.24 vs 0.72-0.91 contrast was **the `p_parallel` acceptance gradient read at
two different `p_parallel` values.** Marginalized over all 19 `p_parallel` cells there is **no down-tilt
deficit** and the sign is if anything opposite. Ironically the reading the concurrent session *retracted*
was closer to right than my correction to it.

`epochs=8` is dead too, and measured rather than argued: the six surviving training histories show step-2
train loss moving **3.2e-5** across 8 epochs with iteration 2's `val_loss` getting **worse**.

### The enabling bug, now filed in `KNOWN_ISSUES.md`

`omnifold.py:303` logs `hist.history['val_loss'][0]` under the label **"Last val loss"** — it prints
**epoch 1**. Two sessions proposed "optimization-limited, raise epochs" without ever opening the pickles.
Verified the line myself. Related: `ModelCheckpoint(save_best_only=True)` (`:272-275`) saves best-val
weights while `reweight` uses the last-epoch in-memory model, so on-disk checkpoints are **not**
bit-identical to what a run used — a calibration caveat for any inference-only reproduction.

### What all three of us missed, and it is the important part

**The test grades the wrong thing, and a PASS would be bad news.** The injection is a function of truth pT
only; the acceptance gradient is almost entirely in `p_parallel`. **Orthogonal.** So an estimator that
*pools across `p_parallel`* scores well on this closure whether or not the pooling is justified — and the
PET net **is** pooling: it recovers 0.208 in cells where the detector sees 0.3% of events, ~25x the
pointwise-optimal 0.008. Getting 0.635 -> 0.80 requires **more** of exactly that extrapolation into
near-zero-efficiency cells, which `OPEN_ITEMS` item 6 already forbids trusting. So the FAIL is arguably
**correct behaviour**, and a future PASS on this criterion should be treated as **suspicious**. The test
with real power is a **second injection carrying `p_parallel` dependence**.

Underneath it, a publication-level fact: **21.1% of the declared fiducial truth population sits at
`p_parallel` < 1.5 GeV with 0.3-1.2% reco acceptance.** `KNOWN_ISSUES.md:17` (#5) tracks a data/MC **ratio**
gradient in exactly that region; the **absolute** acceptance appears nowhere in the repo. Two independent
problems on the same fifth of phase space, one of them untracked.

On my convergence worry its answer was blunt and correct: **all three prior readings shared the framing
"the estimator under-performed, find the mechanism." Nobody computed `a(x)`. The convergence was on a
framing, and the framing was the error.** That is the lesson of the day, and it outranks any of the
numbers.

### Done, and not done

Step 0 (retract and record) is **done** — `25d276b` rewrites both wrong passages in `OPEN_ITEMS` rather
than patching them quietly, and files the telemetry bug. Steps 1-5 I have **not** run: step 1 is free
(inference-only from the step-2 checkpoints, predicted 0.426/0.572/0.635) but belongs with steps 2-3; step 2
redefines a Gate-4 criterion (`recovery / ideal_recovery(a_b,k) >= theta`, theta from a measured noise floor,
**not** from today's numbers) and is a re-issue; step 3 spends 16 GPU-hours on an 8-seed ensemble to decide
whether the 0.212 per-bin scatter averages down or is bias. Both are Joseph's.

## 16:30Z — SECOND fresh consult found a 2.36x error in the DELIVERABLE, and I committed the acceptance map

Joseph granted standing permission (mail 15:22Z) to execute any step **provided a fresh-context agent agrees
with the decision**, and asked how far we are from a full-phase-space cross section with an uncertainty.
Second consult run (16 min, rc=0, 18,204 bytes), transcript committed as
`docs/orchestration/CONSULT-20260806-fresh-context-distance-to-goal.md`.

### It found the extractor divides the cross section by an efficiency twice

I verified all three legs in source before relaying it:

    completeness_2d (:390-404)   c = sum_w(pass_truth & pass_reco)/sum_w(pass_truth)  <- reco EFFICIENCY
    xsec_nd.py:79                denom = completeness * flux * n_nucleons * pot * vol  <- DIVIDES by it
    :431-434                     counts histograms (w_truth*push) over ALL pass_truth rows, whose push
                                 is the nu_k step 2 assigns to truth-only misses -> ALREADY corrected

**2.36x too high on the integral (1/0.4235), 398x in the lowest `p_parallel` bin (1/0.00251).** On this
grid the correct completeness is **identically 1** — the validated GBDT FPS unfolds carry
`globalCompleteness = 1.0000000000000002`, all 266 nonzero bins at 1.000000, and the validated driver
defines completeness as **coverage**, not efficiency. `PETxsec5D` only survived carrying an efficiency there
because `pet_systematics_5d.py:127-141` overrides it with the GBDT value; the FPS port dropped that anchor
and asserts "no such anchor exists for this domain" — **which is false.**

Worse than the bug: **two tests look like coverage and provide none.**
`test_fullevent_extract.py:351-376` recomputes the formula by calling `ex.completeness_2d` *itself* and
asserts bit-equality at `rtol=0, atol=0` — the self-agreement antipattern of
`AUDIT-FINDINGS-20260729-B.md` §4. And `:331-342` **pins the reco-efficiency semantics as intended
behaviour**, so a repairer must first break a test that reads as authoritative. Both filed in
`KNOWN_ISSUES.md` (`1b0e499`).

**I am holding the fix**, although Joseph's permission formally covers it, because the two candidate repairs
differ in *what the measurement is*: (A) drop the division, preserving step 2's full-inventory extrapolation
and matching the GBDT reference; (B) mask `counts` to `pass_truth & pass_reco`, which discards the FPS
extension the campaign exists to add. Evidence favours (A). It sets the published normalization, so it is
his. **Step 4 (train) is unaffected; Step 4b (extract) must not run until it is settled.**

### Four corrections to my own distance assessment

1. **`nominal_pet_training_allowed: false` is not a gate.** Hardcoded literal at
   `validate_pet_nominal_gate4.py:1117`, emitted unconditionally, no code path sets it True, and the
   launcher never reads it. The nominal's real preconditions are all satisfied **today**.
   *Training the nominal is unblocked; what is blocked is quoting the result.*
2. The powered closure does **not** have to pass first — the redesign changes the criterion, not the
   estimator, and even a mask change applies at histogramming.
3. **Step 7 is not on the path.** `RESTORE:28-32` spine is `0a->0->0b->1->2->6->3->2b->4->4b`; 5/7/7b are
   independent. I overstated the distance.
4. My proposed `recovery / ideal_recovery >= theta` criterion is **the inert-tolerance defect in new dress**
   — at `a_b = 0.0025` the ideal is 0.0075, so a *null* estimator passes. Needs two criteria: a ratio
   criterion on a predeclared high-acceptance subdomain, and a prior-sensitivity criterion elsewhere.

### And the long pole nobody had listed

**C_stat for this lane has no implementation.** `extract_fullevent_fps.py:148,165` refuses
`bootstrap_seed != -1`; the bootstrap launchers are the recoil/5D path. A full-event statistical covariance
is an unwritten launcher plus ~20x(8h train + push) = **170-250 GPU-hours**, untracked as an open item.
Distance: ~14-16 steps; **<100 GPU-h for the central value**, far more for the uncertainty.

### ACCEPTANCE MAP COMMITTED — the tracked product all three items were arguing without

`nd-unfolding/pet/acceptance_map_fullevent_fps.py` + product
`products/pet/fullevent_fps/acceptance_map_fullevent_fps.json`, run on compute.

    global acceptance   weighted 0.423516   unweighted 0.418539   (Gate-2 receipt 0.418562)
    populated cells     266 of 285
    37 cells with a_b < 0.01, carrying 25.93% of truth mass
    30.84% OF TRUTH MASS SITS IN CELLS WHERE >90% OF THE ANSWER IS STILL PRIOR AT k=3

    p_par (GeV)    % fiducial    a_b        (1-a_b)^3
    0.00-0.75        10.32%    0.00251      0.9925
    0.75-1.50        10.80%    0.00722      0.9785
    1.50-2.00         7.51%    0.10024      0.7284
    whole domain       100%    0.4235       0.3905

**It settles the disagreement between the two consults**: `a_b` for `p_parallel` 0.75-1.5 is **0.00722**, so
the second consult was right and the first's 0.012 was wrong. It also explains the 0.4235-vs-0.4186
confusion — those are the `w_truth`-weighted and unweighted values, and the unweighted one reproduces the
Gate-2 receipt to 2e-5.

**The 30.84% is sharper than either consult had**, because it is a per-cell census rather than the
`p_parallel` marginal (21.12%): the marginal hides cells inside better-accepted `p_parallel` slices that are
themselves nearly blind.

The product **deliberately creates one live hash pin** on the G2 dump (`inputs`/`inputs_sha256`), verified
to resolve and match on compute and to be silently unresolved on a laptop. Documented in the script so a
future editor does not "clean it up".

## 16:45Z — MY ERROR: `git stash -u` on the shared cluster tree swept up 2147 files. Restored and filed.

To clear the way for a fast-forward merge on the cluster I ran `git stash -q -u`. It captured **2147
untracked files** — `.mcp.json`, `scratch/`, `scratch_audit.py`, and **302
`2d-unfolding/uq/*.root.done`**. No tracked edits were taken (`git stash show --stat` was empty), so
nobody's in-progress work was lost, and the concurrent session's commits were untouched.

**But the `.root.done` files are not clutter — they are the resume markers.** `rg_marker_path()` is
`printf '%s.done\n'` (`lib/resume_guard.sh:67`), so those 302 files are exactly the completion markers
`rg_is_complete` reads. With them gone, a re-run of the 2D bootstrap launchers would have recomputed
hundreds of unfolds — **the precise failure the BEN-023 conversion I did this morning exists to prevent.**
I removed the safety net for the defect I had just finished repairing.

Restored with `git stash pop`, then **verified every one of the 2147 stashed paths was present on disk
before dropping the stash** rather than trusting pop's exit status. Cluster clean at `1dd92ca`, 0 stashes,
0 tracked modifications, 302 markers back.

What went wrong is not the command's syntax but its **scope**: I reached for a bulk verb on a tree another
session shares, minutes after writing in this log that I would stay out of its lane. The correct move —
which I had already used twice today for the pull-abort trap — is to move the *specific* blocking paths
aside. Filed as **BEN-030**, with the general rule: in this repo the untracked set is load-bearing state,
so any `git` verb scoped to "everything not tracked" is unsafe by default.

## 18:25Z — CLM-011 fixed and Gate-4 re-issued; **RESTORE Step 4 SUBMITTED as 56410365**

Joseph, mail 16:26Z: *"Do A. If you want, ask a fresh context claude, but otherwise keep going until the
central value and uncertainties are done."*

### The completeness fix landed as `d22dd20`, after a third fresh consult said "do not commit this version"

I implemented (A), then had a fresh-context session review the 226-line diff before committing. Verdict:
**"the decision is right, do not commit this version"** — four must-fixes, and the largest was mine.

**MY MAGNITUDES WERE WRONG, AND TOO SMALL.** I told Joseph 2.36x on the integral and 398x in the lowest
`p_parallel` bin. `2.36 = 1/<a>`, but the code divided **cell by cell**, so Jensen applies:

    integral inflation   = sum_b m_b/a_b / sum_b m_b = **122.6x**   (not 2.36x)
    per pT row, over rows carrying >99% of truth mass = **48-177x**
    worst single CELL    a_b = 0.0012397 -> **807x**   (398x was the p_par MARGINAL, not a cell)

Recomputed independently from the committed acceptance map. I had propagated 2.36 into a code comment,
into telemetry **persisted into every future receipt**, and into two test docstrings. All four removed;
the derivation now lives in **CLM-011**.

The other three must-fixes, all real:
- **Lead structurally, not empirically.** Coverage is 1 **by construction** — `extract_cross_section_nd`'s
  argument means coverage of the truth denominator, and here the declared fiducial domain *is*
  `pass_truth`. The GBDT `globalCompleteness = 1.0000000000000002` is corroboration only; leading with a
  measurement is what invites a future re-anchoring.
- **Guard it, don't assume it.** `assert_truth_denominator_coverage` now fails closed, mirroring
  `unfold_nd_omnifold_unbinned.py:747-752`, which *raises* rather than assuming its analogue. Without it
  the fix swapped a wrong divisor for an invisible assumption.
- **The module docstring still stated the defect as the design.** I had corrected the telemetry copy and
  left the copy at the top of the file — the first thing any reader sees. *That is how it survived the
  first time.*

Two errors of my own caught in flight: my replacement test was **itself vacuous** (numpy's default
`atol=1e-8` is meaningless against cross sections of ~1e-38, so the mutation check passed trivially —
`atol=0` is now load-bearing and commented), and my power-proof harness patched a name that is imported
**function-locally**, so it reported "no power" for a test that has it.

Also: the suite was **actively pinning the false claim** — a pre-existing assertion required
`completeness_anchor.startswith("NONE")`. And two items from the concurrent session's lane, fixed rather
than left red: `SHELL_PIN_FLOOR` 12 -> 13 (their `sbatch_b1_niter4_scan48.sh` pins a tracked file; I
*verified* the verifier still resolves 13 rather than going BLIND, having first wrongly assumed it would
not), and a duplicate `BEN-030` — mine renumbered **BEN-031**.

**Collection announced: 698 -> 699 local, 752 -> 753 cluster.** Verifier 0 mismatches, ALL BINDINGS
INTACT, 691 passed with exactly the documented 7 pre-existing failures.

### Step 4 submitted — and pre-flighting it caught a job-killer

    56410365  fe_pet_nom  PENDING  prio 67679  8h wall, qos=shared, 1 GPU, launcher UNMODIFIED

Preconditions verified rather than assumed: Gate-2 target **size AND sha** both match the launcher's pins
(`fa6b3463...`, 9897374636), Gate-3 is `PROMOTED_PASS`, policy is niter=3.

**The catch:** `#SBATCH --output` writes into `nd-unfolding/pet/fullevent_nominal/logs/`, which **did not
exist**. Slurm opens that path *before* the job script runs, so the launcher's own `mkdir -p` at `:98`
cannot save it — the job would have held its queue slot for hours and died instantly at dispatch with
nothing to diagnose. This is the identical failure the powered-closure launcher's header already
documents. Fixed the same way, a committed `.gitkeep` (`e23bb13`), so it cannot recur in any checkout.

**The product will be NON-QUOTABLE.** Gate-4 cannot PASS on present evidence — the powered closure's
criterion is unreachable as written — so this run produces a central value for the first time but nothing
promotable. That must be recorded with the product, per the fresh session's advice: train it, mark it
non-quotable, and keep the gating on 4b.

### The launcher I called UNMODIFIED was the defect

The line above — `launcher UNMODIFIED` — was written as reassurance. It was the bug. `sbatch_pet_fullevent_nominal.sh` **restated the policy it was supposed to inherit**: `NITER=2`, plus `ESTIMATOR_SEED`, `SUBSAMPLE_SEED`, `EPOCHS`, `TRAIN_EVENTS`, each passed as an explicit `--flag`. Every one of those overrides the driver's `NOMINAL_SEED_POLICY`, so job 56410365 would have trained at **niter=2** — the value we had just spent a day deciding against — while every receipt, validator and test in the tree said 3. `freeze:seed_policy` would have rejected the result after 8 GPU-hours.

Caught pre-dispatch. `scancel 56410365`, **0 GPU-h lost**.

The repair is structural, not a value edit: the launcher now passes **no policy-owned flag at all**, so the driver constant is the single source of truth. Two tests hold that shut, both mutation-proved — `test_launcher_passes_no_policy_owned_flag` (restore any flag, it fails) and `test_flag_map_covers_the_whole_policy` (add a policy key without a flag mapping, it fails). The retyped `POLICY_FLAGS` map is asserted equal to the driver's own dict, so the two cannot drift silently. Walltime also went 8h -> 12h. Gate-4 re-issued as `...-20260806c` (predecessor retired under `files_at_issue`, no digest hand-edited). Resubmitted as **56415634**.

My own test failed on its own rationale comment twice — mention-vs-use, once on `rg_*` names and once on `--niter` in prose — so `_executable_lines()` is now comment-aware.

### Armed a durable watch, and checked the thing that would have made it theater

`56415634` had **no armed watch**: the `pwclosure-56381674` one fired at 13:55Z and is spent. A session-local watch dies with the session, so a 12-hour job needed a session-independent notifier. New `docs/orchestration/notify_nominal.sh`, armed as `nominal-56415634`.

It reports the *outcome*, not "job finished" — a notifier that only says the latter is the vacuous-pass antipattern wearing a different hat. Three branches, each proved by running it, in a sandbox with the repo root redirected (writing anything to the real nominal path would make `is_complete()` true and cause the live job to skip its own training):

- **both artifacts present** — sha + size for each;
- **the policy the run actually used**, read from the artifact's argv-derived `seed_policy`. Proved to have power: an artifact carrying `niter=2` flips the line to `*** EXPECTED 3 -- freeze:seed_policy WILL REJECT THIS RUN`;
- **the partial case** — nominal present, floor repeat absent, which a walltime kill between the two trainings produces and which a plain resubmit cannot recover, because `is_complete(nominal_out)` kills it before it reaches the floor.

Two things I checked instead of assuming, one of which I had backwards:

**The tick log looked dead and is not.** `cron-tick.log` was 17.5 days stale and ended in a traceback, which read as a broken cron. It isn't: the scrontab block sets `--open-mode=append` and the tick runs `--quiet`, so it writes *nothing* when it has nothing to say, and a stale mtime is the expected steady state. The live evidence is elsewhere — cron job 56160911 COMPLETED today 12:20:09 exit `0:0`, and `evt-pwclosure-56381674.log` was written at 06:55 by that same path firing a real watch.

**The historical traceback could not hit this watch, but it was right to check.** The crash was `parse_utc('1784527278\nRUNNING|1784527278')` — multi-row `sacct` output — and `sacct -j` starts returning three rows (`X`, `X.batch`, `X.extern`) precisely when a job completes, which is the transition this watch depends on. It turns out that call is in the `queue-latency` branch, not `slurm-job`; the `slurm-job` branch goes through `slurm_job_state`, which handles multi-row output and carries an `unreliable` counter, and both queue-latency watches are retired. A clean `tick` confirmed the watch evaluates and correctly does **not** fire while PENDING. Worth noting the fragility anyway: that exception aborted the *whole* scan, so one bad watch can silently stop every other one.

**It also fires on failure.** `run_action` resolves the action from the watch file by id, not from the event type, so `slurm-job-error` — a 12h TIMEOUT, the realistic bad outcome — dispatches the same notifier as `slurm-job-complete`.

Verifier: 13 shell pins resolved against floor 13, ALL BINDINGS INTACT (a pin-free script leaves the collector untouched).
