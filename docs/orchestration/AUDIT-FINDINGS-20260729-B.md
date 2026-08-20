# Audit findings B — MINERvA-OmniFold full-event PET path (2026-07-29)

> **Read after [`AUDIT-FINDINGS-20260728.md`](AUDIT-FINDINGS-20260728.md) (B1–B5, M1–M14) and
> [`AUDIT-FINDINGS-20260729.md`](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/0b329e8ae8482e6334a68faf947fc80ae7265ac9/docs/orchestration/AUDIT-FINDINGS-20260729.md "evidence/prepublication-2026-08-20-0b329e8a:docs/orchestration/AUDIT-FINDINGS-20260729.md") (N1–N8, G1–G2).** Both stand;
> this document does not restate them. Everything below was checked for novelty against both
> before being written, and findings that merely corroborate prior work are segregated into
> §3 rather than presented as new.
>
> Produced by a four-lane parallel audit (two codex accounts, one gemini, one claude), each
> given a disjoint dimension set from `start-audit-planner.md`, with every load-bearing claim
> re-verified by the orchestrating session against the source before inclusion. One lane's
> output was discarded outright — see §6.

## 1. Audit basis and its limits

- Read-only. **No repo file was created or modified except this document.** No receipt, no
  `RUNS.tsv`, no `git` write command, no hand-edited sha256, no job submitted, no de-rooting
  of the load-bearing `/pscratch` literals.
- `python3 docs/orchestration/verify_hash_bindings.py` → `92 resolved / 88 OK / 4 known
  drift / ALL BINDINGS INTACT`, exit 0, both before and after.
- **HEAD moved during this audit**, `5718449 → 381828c → 2c750a3 → a7d3ef6`. Another session
  was live in the repo throughout. Line numbers below were read at `a7d3ef6`.
- **This host has numpy 1.26.4, pytest 8.3.4, sklearn 1.6.1 — and no ROOT.** This is the
  material difference from the 2026-07-29 pass, which had none of them and therefore carried
  every "reproduced locally" and "mutation-tested" claim in the 07-28 document forward on the
  prior session's authority. §4 below is executed evidence, not code reading. Anything
  needing ROOT or the 9.9 GB dump remains unexecuted (§7).
- The brief that commissioned this audit (`start-audit-planner.md`) is stale: it asks for two
  open findings to be verified or refuted, and both were answered at `5718449`. That staleness
  is itself corroborated by N4 and cost one audit lane (§6).

---

## 2. BLOCKS the publication nominal

### B-1. The vendored estimator engine is bound by no receipt at all

*Dimensions: receipt provenance (dim 9), test power (dim 10). Verdict: CONFIRMED. Not frozen
— that is the finding.*

**Claim.** `omnifold_nn/omnifold/net.py` (the PET network) and `omnifold_nn/omnifold/omnifold.py`
(MultiFold — the iteration loop, both classifier legs, the weight recursion) are referenced by
**no receipt or state JSON in the repository**, and are **not among the 92 bindings**
`verify_hash_bindings.py` resolves. Every file wrapped around them — the loader, the driver,
the launcher, the Gate-4 validator — is frozen.

**Evidence.**
- `grep -rl 'omnifold/net\.py|omnifold/omnifold\.py' docs/orchestration/state nd-unfolding/g2_fullevent`
  → no matches.
- `verify_hash_bindings.py` output contains neither filename.
- Both were modified at `25d8360` *"#19 P5B: F2 (FiLM/attention pad-masking) + F3 logit-space
  reweight (publication form)"* — `net.py` +25 lines, `omnifold.py` +34 lines. That commit
  changes how the answer is computed, not how it is plumbed.

**Failure scenario.** Any edit to the network architecture, the loss, the logit-space
reweighting, or the two-step recursion changes the estimator's output while
`verify_hash_bindings.py` continues to print `ALL BINDINGS INTACT` and every gate receipt
continues to certify. The freeze system's entire purpose — "this PASS was obtained against
*this* code" — does not extend to the code that produces the number. This is the same class of
failure as the six voided bindings at `2732304`, except that here there is no binding to void,
so nothing can detect it even in principle.

**Confidence: high.** Direct grep, negative result, reproducible in one command.

**Frozen: no** — and that is the defect. The fix is additive: bind both files into the Gate-4
launch-code gate receipt. Because Gate-4 is `PASS_CODE_ONLY` and has never run at runtime,
binding them now costs a receipt re-issue but no re-run of any physics.

**Minimal check.**
```bash
grep -rl 'omnifold/net\.py\|omnifold/omnifold\.py' docs/orchestration/state nd-unfolding \
  || echo "UNBOUND"
```
Refuted if any receipt names them.

---

### B-2. The independent-verification evidence for Gate-4 and Gate-3 promotion was never committed

*Dimension: receipt provenance (dim 9). Verdict: CONFIRMED by git history. Not frozen.*

**Claim.** The transcripts that Gate-4's `PASS_CODE_ONLY` and Gate-3's `PROMOTED_PASS` cite as
their owner-neutral independent verification do not exist in the repo and **were never added
to it at any commit**, so both gates' independence claims are unfalsifiable from the record.

**Evidence.** `git log --all --oneline --diff-filter=A -- <path>` returns **zero commits** for
each of:

| cited by | path |
|---|---|
| `p3f-pet-gate4-launch-code-gate-20260721.json:24` | `docs/orchestration/runs/agent-B-p5b/gate4-build.capture.txt` |
| `p3f-pet-gate4-launch-code-gate-20260721.json:80` + `state/sessions.json` | `docs/orchestration/runs/agy-publication-redteam/20260721T193131Z-send-fc5cee97.txt` |
| `state/p3f-pet-gate3-promotion-56169838.json` | `docs/orchestration/runs/agy-publication-redteam/20260720T235712Z-send-7a2b0bfb.txt` |

None exists on disk. Committed transcript dates under `docs/orchestration/runs/` are
`20260718, 20260719, 20260720, 20260729` — **2026-07-21, the day Gate-4 was built and
verified, is a hole.** Nothing is `.gitignore`d that would explain it.

The Gate-3 transcript is the one `RUNS.tsv` describes as *"VERDICT PASS (rc=0),
evidence-backed: agy independently ran sacct, reloaded 120 receipts, recomputed on-disk
hashes…"* — i.e. the strongest independence claim in the campaign rests on a file that was
never committed.

Lane D's exhaustive scan reports **33 missing of 314 in-repo paths cited by receipts or
`RUNS.tsv`**, including `p3s_fps_manifest_historical.json` (a Gate-3 prerequisite). *I
spot-verified 3 of 3 above; the count of 33 is lane-D-reported and not independently
re-enumerated here.*

**Failure scenario.** A reader — or the next cold session — treats Gate-4's `PASS_CODE_ONLY`
and Gate-3's `PROMOTED_PASS` as independently verified because the receipts say so and name
evidence. The evidence cannot be produced. This is not hypothetical suspicion:
`p3f-pet-gate3-launch-code-gate-20260720.json:85` already records
`"initial_agy_verdict": "REJECTED_OVERCLAIM"`, so the verifier's *first* pass rejected the
claim, and the transcript recording what changed on the second pass is exactly what is
missing.

**Confidence: high** that the files were never committed. **Unknown** whether the verification
happened and simply went unrecorded — most likely, given `sessions.json` names the specific
file. The finding is that the record cannot distinguish "verified" from "asserted".

**Frozen: no.** If the transcripts still exist in a live agy session store, recovering them is
`RESTORE-2026-08-03.md` Step 6, which is already scheduled and independently justified — this
finding raises its priority from housekeeping to evidence recovery. If they are gone, the
honest move is to amend both receipts to record the evidence as unrecoverable, or re-run the
independent verification, rather than leaving a citation that does not resolve.

**Minimal check.** The `git log --diff-filter=A` command above, per path. Zero output ⇒ never
committed.

---

### B-3. The "full-event" estimator does not consume the full-event payload

*Dimensions: loader contract (dim 7), fail-closed guards (dim 8). Verdict: CONFIRMED.
**Frozen — Gate-2 re-issue** (see the consolidation note at the end of §2).*

**Claim.** The estimator that stamps `pet-fullevent-fps-v1` reads a recoil cloud and two muon
scalars. The muon four-vector, MINOS information, reco vertex, view and timing arrays — the
things that make the representation "full-event" — are dumped, required by the schema
contract, and never read.

**Evidence.** Occurrence counts in `nd-unfolding/pet/fullevent_fps_dataloader.py` vs
`nd-unfolding/pet/fullevent_dump_contract.py`:

| array | loader | dump contract |
|---|---|---|
| `reco_muon` | **0** | 2 |
| `reco_vertex` | **0** | 2 |
| `reco_view` | **0** | 3 |
| `reco_time` | **0** | 3 |
| `data_muon` / `data_vertex` | **0** | 2 each |
| `data_view` / `data_time` | **0** | 3 each |

- `fullevent_dump_contract.py:28-32` declares them required:
  `RECO_KEYS = ("part_reco","reco_scalars","reco_muon","reco_vertex","reco_view","reco_time")`
- `fullevent_fps_dataloader.py:133` — `DEFAULT_EVT_FEATURES = ("pt", "pparallel")`
- `fullevent_fps_dataloader.py:520-525` reads only `part_reco`, `part_gen`, `reco_scalars`,
  `truth_scalars`.
- `train_fullevent_nominal.py:134-137` nonetheless writes
  `estimator_fingerprint=ESTIMATOR_FINGERPRINT` = `pet-fullevent-fps-v1`.
- `FULL_EVENT_FEATURE_CONTRACT.md:19-21` defines that fingerprint as *"full muon object:
  px,py,pz,E,φ,charge,MINOS + reco vertex + view/timing + residual summaries"*.

**Failure scenario.** Two valid `g2-fullevent-v1` NPZs with identical recoil clouds and
identical `(pT,p‖)` scalars but entirely different muon four-vectors, MINOS bits, vertices,
views and timings pass the schema gate and produce **byte-identical classifier inputs**, hence
identical weights modulo GPU nondeterminism. Both products are recorded as
`pet-fullevent-fps-v1`. P5B, the technote, and any downstream consumer inherit a fingerprint
that overstates what the estimator saw.

**Confidence: high** on the code facts (a zero-occurrence grep over eight names). The loader
docstring at `:130-133` does self-describe the reduction — *"Default = the muon (pT,
p_parallel) available NOW (reduced set; the reduction is recorded…)"* — so this is a
contract-and-labelling integrity finding, not a concealed bug. It matters because the label is
what P5B will trust, and because the schema gate's fail-closed strictness on arrays the loader
then ignores creates an unearned impression of coverage.

**Novelty.** Grepping `AUDIT-FINDINGS-20260728.md` for `reco_muon|reco_view|reco_time|reco_vertex`
returns nothing. Not previously raised.

**Minimal check** (login-safe, no cluster). On a small synthetic `g2-fullevent-v1` fixture:
build loaders and hash `mc.reco`, `mc.reco_evt`, `data.reco`, `data.reco_evt`; mutate only the
`*_muon`, `*_vertex`, `*_view`, `*_time` arrays; rebuild and re-hash. **Current code produces
identical hashes.** Either accept and re-label the fingerprint, or extend the feature block.

---

### B-4. `w_reco` is dumped, declared required, and never used — one weight vector drives both legs

*Dimension: unfolding procedure (dim 1). Verdict: CONFIRMED. **Frozen — Gate-2 re-issue.***

**Claim.** The G2 contract deliberately carries separate reco-leg and truth-leg MC weights.
The full-event loader uses `w_truth` for both. The validated 2D path uses both, separately.

**Evidence.**
- `dump_pointcloud_inputs.py:201` — `a["w_reco"] = np.asarray(sig["w_reco"], np.float32)`;
  listed as a required branch at `:299` and `:540`.
- `grep -n "w_reco" nd-unfolding/pet/fullevent_fps_dataloader.py` → **no matches.**
- `fullevent_fps_dataloader.py:551` — `w_truth_full = np.asarray(d["w_truth"])…`, and that one
  vector is passed to `DataLoader(weight=w_truth, …)` at `:612-614`.
- `omnifold_nn/omnifold/omnifold.py:176-177` (step 1, detector level) and `:196-197` (step 2,
  truth level) both consume that single `mc.weight`.
- Contrast `2d-unfolding/unfold_2d_omnifold_unbinned.py:1715-1716` —
  `MCgen_weights=sig["w_truth"]`, `MCreco_weights=sig["w_reco"]`.

**Failure scenario.** Any reco-side efficiency, detector or selection reweighter that moves
`w_reco` without moving `w_truth` leaves step 1 training against a mis-weighted simulated reco
density. The learned density ratio is then wrong before any of the iteration machinery runs,
and step 2 propagates that error to truth. It is invisible to a fixture that uses independent
random positive weights, because such a fixture never distinguishes the legs.

**Confidence: high** that `w_reco` is unused. **Medium** on the numerical effect for the CV,
which depends on whether `w_reco == w_truth` in the frozen dump — unknown without the file.

**Novelty.** `AUDIT-FINDINGS-20260728.md:527` is the only mention of `w_reco` in the prior
audit, and it appears inside a *mutation-test predicate* that pins `mc.weight ∝ w_truth[imc]`
and `!= w_reco * k` as the **expected correct** behaviour. The question of whether the reco leg
should use `w_reco` is not asked there.

**Minimal check** (needs the dump; seconds of I/O, no compute). Over `pass_reco`, report:
count and fraction with `w_reco != w_truth`; min/median/max of `w_reco / w_truth`; the weighted
sum difference. Bit-identical for the CV ⇒ refutes activation for the nominal but **not** for
the systematic universes, where reco-side reweighters are exactly the point — so repeat per
endpoint before P5B.

---

### B-5. Stay-Positive is learned on a 2D muon marginal and consumed in cloud space

*Dimensions: negative-weight handling (dim 2), covariance (dim 4). Verdict: CONFIRMED.
**Frozen — Gate-2 re-issue.***

**Claim.** The Stay-Positive refiner estimates the signed measured density as a function of
`(pT, p‖)` only. PET then discriminates using the full point cloud. The refinement's
guarantee therefore does not cover the space the classifier actually sees.

**Evidence.**
- `fullevent_fps_dataloader.py:638-640`:
  ```python
  # refinement feature = continuous reco (pT, p_parallel) on the reco manifold (g(x)=D/(D+B))
  cols = [SCALAR_COLS[f] for f in feature_names]
  refine_feat_data = np.asarray(meas_scalars, float)[:, cols]
  ```
  with `feature_names` defaulting to `DEFAULT_EVT_FEATURES = ("pt","pparallel")` (`:133`).
- `G2_GATE2_TARGET_RUNTIME_RECEIPT.json` records `"features": ["pt", "pparallel"]`, and its
  independent validation is a 15×19 muon grid.
- The refined weights are attached to the concatenated clouds at `:652-659` —
  `meas_cloud_all = np.concatenate([meas_cloud, bkg_cloud], axis=0)`, then
  `DataLoader(reco=meas_cloud_all, weight=w_refined, reco_evt=event_meas_all)`.

**Failure scenario.** Within a fixed `(pT,p‖)` cell, background events differ from data in
recoil energy, token multiplicity or view/timing topology. The refiner, blind to those
variables, reproduces the correct *signed total* in that cell — but the background rows retain
their background-like clouds and receive non-negative weight. PET's step-1 classifier sees
that residual background topology as part of the positive measured target and learns it as
signal. **Every Gate-2 `(pT,p‖)` projection can agree to machine precision while this
happens**, because those projections are exactly the space the refiner was fit on. The
resulting bias is conditional on hadronic activity, which is precisely what the full-event
representation exists to exploit.

**Confidence: high** for the feature-space mismatch (read directly). **Unknown** magnitude —
it is set by real data/background cloud differences at fixed muon kinematics, which needs the
dump.

**Novelty.** `AUDIT-FINDINGS-20260728.md:529-530` mentions `refine_feat_data`/`refine_feat_bkg`
only in a row-alignment mutation predicate (M2). The dimensional mismatch is not raised.

**Minimal check** (login-safe, and it is the decisive one). Build a synthetic fixture in which
data and background share an identical `(pT,p‖)` distribution but have separable recoil
clouds. Verify that the current 2D refiner fails to recover the known signed cloud
distribution, while a cloud-summary-augmented refiner closes it. Then, on the real dump,
compare signed vs refined targets in independent cloud observables (total recoil energy, token
multiplicity, longitudinal extent, view fractions) and require a held-out full-space
classifier to be compatible with chance.

---

### B-6. A second dead closure: `stress_closure_muon.py` was edited after the Gate-4 PASS, is bound by nothing, and has never recorded a PASS

*Dimension: receipt provenance (dim 9), closure power (dim 3). Verdict: CONFIRMED. This is the
"find the others" the brief asked for.*

**Claim.** The omitted-muon stress closure — the only check that demonstrates the full-event
path is sensitive to the muon at all — was modified by the de-rooting commit five days after
Gate-4 passed, was not among the six files reverted, is bound by no receipt, and has no
recorded PASS anywhere in the repo.

**Evidence.**
- `validate_pet_nominal_gate4.py:57-59` names it in the frozen contract:
  `FROZEN["closure_scripts"]["omitted_muon_stress"] = "nd-unfolding/pet/stress_closure_muon.py"`.
- `git log --oneline -1 2732304 -- nd-unfolding/pet/stress_closure_muon.py` →
  `2732304 Derive the repo root from __file__ across 26 pet/ and tests/ modules`. Gate-4 passed
  2026-07-21; `2732304` landed 2026-07-28.
- `5a22e1c` reverted the six binding-voiding files. `stress_closure_muon.py` is in the
  unreverted remainder.
- `grep -c stress_closure_muon docs/orchestration/state/*.json` → no receipt names it.

**Failure scenario.** Gate-4's frozen contract points at a closure script as evidence that the
estimator is muon-sensitive. That script is in a state no gate has ever certified, in a version
no gate has ever seen, and its verdict has never been recorded. Because it is unbound,
`verify_hash_bindings.py` cannot report the drift. The structural parallel to the dead P5A
closure is exact — a named closure whose PASS does not certify the code that exists — except
that here there is no PASS to be dead.

**Confidence: high.**

**Frozen: the script itself, no.** But it is *named inside* frozen Gate-4 contract text, so
running it and recording a receipt is free, while changing what Gate-4 points at is a Gate-4
re-issue.

**Minimal check.** Run it and record the verdict. It is login-safe by construction (identity
response, all-pass masks, `stress_closure_muon.py:38-73`). Costs minutes; retires the finding
either way.

---

### B-7. `data_identity_hash` binds the data cloud and not the data scalars

*Dimension: truth/reco leakage (dim 6). Verdict: CONFIRMED. Upgrades a prior open question.*

**Claim.** The persisted data identity covers `measured_pc` alone. A permutation of
`measured_scalars` preserves the identity hash and the row count, and silently pairs cloud row
*i* with the reconstructed muon of row *π(i)*.

**Evidence.**
- `dump_pointcloud_inputs.py:234` —
  `a["data_identity_hash"] = np.asarray(fed.inventory_order_hash(a["measured_pc"]))`.
  `measured_scalars`, `data_muon`, `data_vertex`, `data_view`, `data_time` are all omitted.
- `fullevent_fps_dataloader.py:585-591` re-verifies using the same incomplete definition:
  `_verify_stored_identity(d, "data_identity_hash", (np.asarray(d["measured_pc"]),), "data")`.
- `fullevent_fps_dataloader.py:528-529` accepts `measured_scalars` directly; only the *sidecar*
  path checks row count (`:535-537`).
- `FULL_EVENT_FEATURE_CONTRACT.md:143-145` concedes the gap: *"row-count alignment is enforced;
  a full event-by-event order proof … is a P5B hardening item."*

**Failure scenario.** A producer-side reordering of `measured_scalars` relative to
`measured_pc` passes the domain checks, the stored identity, and the row-count check. Step 1
then trains on data rows whose cloud and muon come from different events — manufacturing
data-only correlations with no MC counterpart, which is the single most learnable artifact you
can hand a discriminator.

**Confidence: high** that the receipt cannot prove ordering. **Low** that the frozen artifact
is actually misordered — the dumper fills both in the same event loop
(`dump_pointcloud_inputs.py:375-383`).

**Novelty.** `AUDIT-FINDINGS-20260728.md:1188` lists *"whether `measured_scalars` is row-order
aligned to `measured_pc`"* under what it could not assess. This finding is that it is not
merely unassessed but **structurally unprovable by the current identity definition** — the
check would fail to detect it even with the dump in hand.

**Frozen: yes, and expensively.** Changing the identity definition touches
`dump_pointcloud_inputs.py` / `fullevent_dump_contract.py`, bound at
`state/g2-dump-submit-20260719.json:26-32`. That changes the G2 NPZ sha256, cascading to
Gate-1B, Gate-2, Gate-3 and Gate-4. **Do not do this before P5A.** The affordable move is a
read-only verification script that recomputes an all-consumed-arrays identity on the existing
dump and records the result — no re-dump, no re-issue.

**Minimal check.** On a synthetic fixture, permute only `measured_scalars` and confirm the
stored `data_identity_hash` still validates. Then, on Perlmutter, stream the source ROOT and
the NPZ together and hash stable data event keys in order.

---

### B-8. 503 guard checks are never collected by the test suite

*Dimension: test power (dim 10). Verdict: CONFIRMED.*

**Claim.** The `test_g2_*.py` guard files live under `nd-unfolding/pet/`, while the suite is
run as `pytest nd-unfolding/tests`. They never execute — including the C++ truth↔reco leakage
guard.

**Evidence.** `ls nd-unfolding/pet/test_g2_*.py` → 2 files. `RESTORE-2026-08-03.md:42` defines
the baseline command as `python -m pytest nd-unfolding/tests -q`, which cannot reach them.
Lane D reports 503 individual guard checks across them; *I verified the location and
non-collection, not the check count.*

**Failure scenario.** The leakage guard that the campaign believes is enforced by the suite is
never run by the suite, so the 333-passed baseline carries no evidence about it. Combined with
§4's mutation results, "the tests pass" says even less than the 07-28 document already warned.

**Confidence: high** on non-collection; **medium** on the 503 count (delegate-reported).

**Frozen: no.** Adding a `pytest.ini` / `conftest.py` collection path is unbound. But note
these guards may require ROOT and therefore may not be login-safe off Perlmutter — confirm
before wiring them into the default baseline, or the 7-failure baseline becomes a moving
target.

---

**Consolidation note.** B-3, B-4 and B-5 all land on `nd-unfolding/pet/fullevent_fps_dataloader.py`,
which `G2_GATE2_TARGET_RUNTIME_RECEIPT.json` binds **jointly with** `gate2_target_runtime.py`.
Fixing them is **one** Gate-2 canonical-runtime re-issue and **one** Gate-2 re-run, not three.
Sequence them into a single deliberate patch set together with the B1 normalization fix
(`B1-NORMALIZATION-FIX-DESIGN.md` §2a, same file) — the dominant failure mode on 08-03 is a
partial fix that consumes the restore window and leaves the gate asserting a stale target.

---

## 3. Corroborated, not new

Recorded so the independent agreement is on file, and so these are not double-counted as fresh
findings:

- **Gate-4's freeze check compares `FROZEN` to `FROZEN`** (`validate_pet_nominal_gate4.py:218-222`
  populates `frozen_observed` *from* `FROZEN`; `check_freeze:137-143` then asserts equality) —
  already 07-28 **B2**.
- **Gate-4's `main()` runs 2 of 7 advertised check families.** I confirmed the call site at
  `:223-229` passes no `marginal=`, `normalization=`, `saturation_frac=` or `closure=`, all of
  which are `if … is not None`-gated, and that `check_normalization` (`:107-110`) is therefore
  dead code today — already 07-28 **B2**, and cited in `B1-NORMALIZATION-FIX-DESIGN.md` §2d.
- **The launcher never invokes the validator** (`sbatch_pet_fullevent_nominal.sh`, three
  `$DRIVER` calls, exits at `:119`) — found independently by two lanes; adjacent to 07-28 **B3**.
- **The driver produces weights only for the 2M subsample, never reweight-all on 49.2M** —
  already 07-28 **B3 / CLM-006** (`:179-212`).
- **A null estimator `push = ones` passes the ordinary closure** — already 07-28 (`:485`, `:1315`).
- **The B1 normalization defect** was re-derived independently from the vendored engine, and the
  same `1e6·R` fix shape was reached without sight of the design doc. Genuine independent
  support for `B1-NORMALIZATION-FIX-DESIGN.md`.

One partly-new angle on iteration policy: `omnifold.py:53-59` sets early-stop patience to **10**
epochs while the nominal runs **8**, and the LR-reduction callback patience is **1000**
(`:247-252`). Both stopping mechanisms are structurally inert at the frozen configuration, and
models warm-start across iterations (`:261-272`), so apparent iteration-to-iteration convergence
partly reflects continued optimization of the same weights. 07-28 covers `niter` only as a
*metadata-persistence* problem (`:126-156`), not as dead convergence machinery.

---

## 4. Executed evidence — mutation testing

The 2026-07-29 pass explicitly flagged that its container had no numpy, sklearn, pytest or ROOT,
so the 07-28 mutation matrix was carried forward unverified. This host has them. Mutations were
applied **in memory only** — no repo file was edited.

Baseline: `7 failed / 333 passed / 1 skipped` (all 7 failures the documented off-Perlmutter
`/pscratch` artifact).

| Mutation | Suite result | Detected? |
|---|---|---|
| driver `niter 2→1` | 7F / 333P / 1S | **no** |
| driver `train_events 2_000_000→1000` | 7F / 333P / 1S | **no** |
| validator `epochs 8→99` | 7F / 333P / 1S | **no** |
| Gate-4 frozen grid → single garbage bin | 7F / 333P / 1S | **no** |
| tolerance loosening | 3 tests fail | yes |
| `bkg_mode` label swap | 8 tests fail | yes |

**All 49 `test_fps_provenance.py` tests caught nothing**, because they derive their fixtures
from the constant under test — the tautology pattern the brief asked to look for, found and
quantified.

This is the concrete answer to "what mutation would the suite actually catch?": it catches
*label and tolerance* changes and misses *physics-configuration* changes. Seed policy, iteration
count, training-set size and the binning grid are all unprotected.

## 5. Verified negative results

Stated explicitly so absence of a finding is not mistaken for absence of a check.

- **No hash falsification anywhere.** `5a22e1c` reverted code and touched no JSON. The four
  `KNOWN_PREEXISTING` drift entries are correctly classified.
- **No recoil-only GPU-floor leakage into any executable covariance path.** The
  `is_publication_result=false` / `is_covariance_component=false` flags are inert metadata that
  no assembler enforces — but no consumer capable of transferring the file into a full-event
  covariance exists today. The future P5B assembler should enforce a component allowlist rather
  than rely on the absence of a reader.
- **No live C/F ravel-order mismatch** in the scalar FPS chain. The convention is coherent
  (`fps_provenance.py:31-32`, `RAVEL_ORDER="C"`); per N7 it currently binds no full-event code.
- **No data-side truth-padding channel.** The data loader is constructed with `reco`/`reco_evt`
  only (`fullevent_fps_dataloader.py:658-659`), and step 1 concatenates only reco clouds and
  reco event blocks (`omnifold.py:318-330`). No manufactured truth tensor reaches data.
- **`purity` cannot silently become the nominal.** `train_fullevent_nominal.py:32-37` hardcodes
  `BKG_MODE="negweight-refined"` and `assert_publication_config`
  (`fullevent_fps_dataloader.py:439-456`) rejects purity. Delta and legacy uses are labelled
  controls.
- **The core OmniFold recursion is correct.** `weights_push` starts at 1 (`omnifold.py:153-157`),
  step 1 forms `weights_pull = weights_push * new_weights` (`:184-187`), step 2 replaces the push
  (`:202-204`). No accidental re-multiplication of prior ratios; no mask inversion in
  `:176-187` / `:194-204`.
- **Stay-Positive ordering is correct** — background and bootstrap factors applied before
  refinement (`:643-650`), refined once per nominal/replica. Re-refining per iteration would be
  wrong, and it does not happen.

## 6. One audit lane was discarded

The gemini lane, briefed from the stale `start-audit-planner.md`, reproduced **exactly the error
N1 diagnoses**: it evaluated the 40M-event / 4-rank configuration as "the production case",
concluded ~61 GiB/rank and ~244 GiB/node with "memory exhaustion an imminent, severe threat",
and recommended the shard-before-build refactor against a frozen file. That is the wasted
restore-window trap N1 exists to prevent. It also misidentified the binding receipt as
`G2_1A_VALIDATION_RECEIPT.json` (the actual joint binding is
`G2_GATE2_TARGET_RUNTIME_RECEIPT.json`). Its output is not carried into this document.

Recorded because it is evidence about the brief, not only about the lane: **a stale brief
reliably reproduces the stale finding.** N4's recommendation to regenerate `LIVE-STATE.md`
before the next cold session enters through it should be read as load-bearing.

## 7. A correction to `B1-NORMALIZATION-FIX-DESIGN.md` §2d

The design's proposed Gate-4 replacement check is
`pot_scale * sum(w_truth * push over pass_reco) == n_data − pot_scale * sum(w_bkg)`.

**This is not subsample-invariant.** The nominal trains on a 2M subsample of 49,152,885 rows,
so the left-hand side is computed over the subsample while the right-hand side is a
full-inventory measured yield. As written the check fails a *correct* unfold by a factor of
≈ N/n_sub ≈ 24. This is the same class of trap as the `pot_scale` trap the document itself
identifies two sections earlier.

Use the ratio form:

```
sum(w_truth * push over pass_reco) / sum(w_truth over pass_reco)  ==  R
```

i.e. *the reco-weighted mean of push equals R*. Multiplying through by
`pot_scale * sum(w_truth_full[pass_reco_full])` recovers the document's absolute statement, but
the ratio form never needs the subsample factor.

Two consequences, both favourable to the design:

1. **It is cheaper, not more expensive.** `check_normalization` (`validate_pet_nominal_gate4.py:107-110`)
   already computes `sum_w_push / sum_w`, and `build_gate4_report` already carries the pair as
   `normalization=(sum_w_push, sum_w)` (`:160`). The change is the **mask** (`pass_reco` instead
   of all truth) and the **target** (`R` instead of `1`) — no new machinery.
2. **It preserves §2d's own correction.** §2d is right that at truth level over the full
   population the expected ratio is `1 + ⟨a⟩(R−1)` ≈ 1.08, which depends on the acceptance being
   measured, so asserting ≈R there would fail a correct unfold. Restricting the mask to
   `pass_reco` is exactly what removes the acceptance dependence and makes `R` the exact target.
   §2d found the right objection and then reached for an absolute-yield form when the mask change
   was sufficient.

Two smaller notes. The new check's **tolerance is unspecified** and cannot simply inherit the old
`1e-3`: it is not exact even for a correct unfold, because step 2 smooths and the reco-level sum
under `push` differs from that under `pull` at finite iteration count. That number must come out
of the closure run §4 already requires. And §6's *"can the Gate-2 re-issue be validator-only?"*
is mis-framed — §2a edits `fullevent_fps_dataloader.py`, whose sha256 the Gate-2 receipt binds
jointly with `gate2_target_runtime.py`, so the receipt moves regardless. The real question, worth
asking as stated, is whether the expensive **canonical refiner re-run** can be skipped because
`w_refined` is bit-identical.

## 8. NOT ASSESSED — this is not a clean bill of health

- **No ROOT on this host**, so nothing PyROOT-backed was executed: the C++ guards (B-8), the
  Gate-3 domain validator's `TTree::Draw` paths, and G1's cloud-length scan remain read-verified
  only.
- **The 9.9 GB `G2_FPS_MEFHC_P12.npz` is unreachable.** Therefore unknown: the value of `R`;
  whether `w_reco == w_truth` for the CV (sets B-4's magnitude); conditional data/background
  differences in cloud space at fixed muon kinematics (sets B-5's magnitude); whether
  `measured_scalars` is actually misordered (B-7); and whether any negative signal-MC weights
  exist, which would make the step-1 cross-entropy ill-posed independently of everything above.
- **The 120 Gate-3 endpoint receipts** live on `/pscratch` and were not read. N2's census sweep
  remains the decisive first move on 08-03.
- **Whether the missing transcripts (B-2) still exist** in a live agy session store. This is
  answerable only on Perlmutter, via `RESTORE-2026-08-03.md` Step 6.
- **The 33-missing-of-314 dangling-pointer count and the 503 guard-check count** are
  delegate-reported; I spot-verified 3 of 3 transcripts and the guard files' location, not the
  full enumerations.
- **P5A has never run**, so there is no full-event central vector, no PET-derived reported mask,
  no cross-section normalization and no matched floor spectrum to audit numerically. Nothing here
  can substitute for that.

---

**Standing constraints observed.** No repo file edited, no receipt or `RUNS.tsv` touched, no
sha256 hand-edited, no job submitted, no de-rooting of the load-bearing `/pscratch` literals.
`verify_hash_bindings.py` → `ALL BINDINGS INTACT`, before and after.

---

## 9. Addendum — a claimed generalization of B-1, refuted (2026-07-29, reviewing session)

A review of this document proposed extending B-1: that because
`G2_GATE2_TARGET_RUNTIME_RECEIPT.json` records its four code bindings as absolute
`/pscratch/...` paths, they fall in the 301-unresolvable set, so `verify_hash_bindings.py`
would print `ALL BINDINGS INTACT` after an edit to the vendored `omnifold/dataloader.py` — or
to `fullevent_fps_dataloader.py` and `gate2_target_runtime.py`, the files the B1 patch set
edits.

**Refuted.** `verify_hash_bindings.py:74-78` (`localize`) strips the
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/` prefix and hashes the local checkout, and the
module docstring at `:17-21` records that this remapping exists *precisely because* the Gate-2
dataloader binding was missed on a first pass. Driving `collect()` + `localize()` directly over
every receipt JSON:

| bound file | resolved | hash | receipt |
|---|---|---|---|
| `omnifold_nn/omnifold/dataloader.py` | yes | MATCH | `G2_GATE2_TARGET_RUNTIME_RECEIPT.json` |
| `fullevent_fps_dataloader.py` | yes | MATCH | `G2_GATE2_TARGET_RUNTIME_RECEIPT.json` + `g2-gate2-construction-20260719.json` |
| `gate2_target_runtime.py` | yes | MATCH | `G2_GATE2_TARGET_RUNTIME_RECEIPT.json` |
| `train_fullevent_nominal.py` | yes | MATCH | `p3f-pet-gate4-launch-code-gate-20260721.json` |
| `validate_pet_nominal_gate4.py` | yes | MATCH | `p3f-pet-gate4-launch-code-gate-20260721.json` |
| `omnifold/net.py`, `omnifold/omnifold.py` | — | — | **bound by nothing (B-1 stands)** |

The 301 unresolvable entries are data files, off-repo artifacts and binaries, as the summary
line says — not these.

**The inference trap that produced it, recorded because it will recur.**
`verify_hash_bindings.py:115-123` prints only the summary count, the known-drift list, and
mismatches. It **never names a binding that is OK.** So `grep <filename>` over its stdout
returns nothing both when a file is unbound *and* when its binding is perfectly intact — the
two cases this document's B-1 needs to distinguish. Absence of a filename in the verifier's
output is not evidence about coverage in either direction; the receipt JSONs are the only place
to settle it. B-1's own evidence is sound because it greps the *receipts*, not the verifier;
the reviewing session's `grep -c` over verifier stdout (0 matches) added nothing and was
misread as corroboration.

**Consequence for the B1 patch set:** `verify_hash_bindings.py` *is* a valid backstop for every
file §2a/§2c/§2d touch. Run it before and after and expect a MISMATCH on each edited file —
that is the receipt correctly reporting it must be re-issued, not a failure. What it still
cannot see is an edit to `net.py` or `omnifold.py`, which is why §2a routes through the existing
`normalization_factor` argument rather than the vendored engine.
