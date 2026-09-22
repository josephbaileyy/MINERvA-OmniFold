# HANDOFF 2026-09-22 — GBDT / scalar-5D, written to be read COLD

**READ THIS FIRST:** you have none of the prior session's context and you do not need it. Every
number below carries the receipt it came from, every path is absolute or repo-relative from the
repository root, and every open item states **what a terminal result would NOT authorize**. Where a
claim is dated, its sha is given, because a `file:line` citation is stale the moment the file is
edited.

**CITABLE FOR:** the state of the GBDT path at `origin/main = d2f29ca504e5d195756174569a70969986d98be1`
and what remains.
**NOT CITABLE FOR:** publication readiness, any grade, or any claim that an item below is resolved.

| | |
|---|---|
| monorepo head | `d2f29ca504e5d195756174569a70969986d98be1` (`origin/main`) |
| standalone note head | `908c0568e9a704c4b145f04723c723da7ff67568` (`analysis-note/main`) |
| adopted covariance | `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/uq_5d/z_pilot_20260916_a5/z-cv.npz` |
| its `sha256` | `3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5`, `890,500,272` B |
| assembling revision | `fb9ec3560fd6d62295dffc81b5694c9e26667d5b`, tag `evidence/z-assembling-revision-fb9ec356` |
| deployed cluster checkout | `/pscratch/sd/j/josephrb/MINERvA-OmniFold` at **`32e403b8`** — ⚠ do not move it, §7 |

---

## 0. ⚠ SCOPE: PET IS DELIBERATELY OUT

Joseph, 2026-09-21, verbatim: *"The pending jobs are for PET. I don't want to focus on it and just
want to focus on finishing GBDT."* PET has live jobs on the cluster (array `58692544`) and its own
session. **Do not fold PET work into this path** and do not read PET's queue as GBDT's. Two PET
items are noted in §9 only so you do not rediscover them as GBDT problems.

## 1. THE FOUR MEASUREMENTS THAT TRAVEL WITH THE ADOPTION — stated, not referenced

These are the most-dropped facts in the whole path. A session reading a summary loses them, and
then quotes the covariance as if it were unqualified. **All four travel with any use of
`3d7465f6…`.** Source: `docs/orchestration/DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md` §4.

**M1 — `s_proj = 6.145%` against a `5%` bound.** `(cause 3, Z)`'s `M(ii)` graded **branch 5,
NOT MET — PER-BIN** on a fully valid campaign (all nine validity fields passed). `s_agg = 0.471%`
and `s_med = 0.485%` were inside the bound; `s_proj` — the only correlation-sensitive leg — was
`6.145%`. Receipt: `docs/orchestration/state/GRADE-20260920-cause3-two-member.json`. Graded /
compared digests `361090f9…` / `7e4636a3…`. **This is why no generator significance is quoted.**

**M2 — the `6.145%` is a property of the estimator, not resampling noise.** With throws held fixed
and only the estimator seed changed: `s_proj = 6.04% ± 0.39%` at `N = 40, 80, 160`, scaling
exponent `p = 0.000`, while the same-seed resampling floor falls `20.91% → 7.57%` at `p = 1.467`.
Statistical noise must fall with `N`; this did not.
⚠ **The `± 0.39%` is scatter across throw SUBSETS at ONE seed pair, and the width of the seed-pair
distribution is UNMEASURED.** ⚠ **A corollary once attached here — *"a larger ensemble would not
reduce it"* — is WITHDRAWN** (`docs/orchestration/CORRECTION-20260921-seed-effect-larger-ensemble-corollary-withdrawn.md`).
The `N = 40` and `N = 80` points are **nested subsets of the same 160 throws**: see
`docs/orchestration/state/SEED-EFFECT-20260920.json`, whose top-level key is literally
`seed_effect_same_throws` and which holds `Q1–Q4` at `n_throws=40` and `HA/HB` at `n_throws=80`.
**What survives: the flatness measurement, M1's FAIL, and the inference that the failing leg is not
reporting its own resampling noise. What does not: any statement about untested `N`.**

**M3 — five bands sit outside what the seed variation probes.** `BeamAngleX`, `BeamAngleY`,
`MuonResolution`, `Muon_Energy_MINERvA`, `Muon_Energy_MINOS` carry **26.0% of `√Tr C_Z`** and
**6.75% of the trace** and contribute **zero** movement by construction.
⚠ **The *"lower bound"* reading is WITHDRAWN** (`CORRECTION-20260920-lower-bound-inference-withdrawn.md`):
`s_proj` is a **maximum** over the functional set (`z_statistics.s_proj`, at `z_statistics.py:319`
as of `2a2196e3` — cite the symbol, the line moves), **not a sum of nonnegative magnitudes**, so
releasing a held-fixed PSD component can move the total **either way**.

**M4 — the estimator seed moves the CENTRAL VALUES too.** On the 43 `M1` projection functionals:
median `0.104%`, max `0.761%` (at index 2, *the same functional that failed `s_proj`*), against
relative uncertainties of median `10.1%` — i.e. median `1.06%` and **max `6.02%` of the quoted
`σ`**. Same-seed control `9.4e-13`, ten orders below, so the movement is real.
⚠ **Per individual 5D bin it is much larger: median `3.77%` of `σ`, p90 `13.6%`, max `49.8%`.**
**A statement about one 5D bin carries that; the projections do not, because aggregation suppresses
it.**

## 2. ⚠ ITEM 1 — STANDARD-P4 STAGE 4 IS BLOCKED LANE-WIDE (not just for the L2 probe)

`nd-unfolding/p4_build_components.py` is self-gated (repair-12) and refuses without
`P4_VERIFIER_PASS` — the sha256 of a **committed** `standard-p4-verifier` verdict carrying
`authorizes_covariance_stages_4_6=true`. **Tested with the real checker, not read:**

| verdict (in `docs/orchestration/runs/standard-p4-verifier/`) | field | result |
|---|---|---|
| `20260815T232546Z-repair8-verdict.json` | `BLOCK` | `TOKEN-REJECT` — authorizes nothing |
| `20260816T220615Z-repair11-verdict.json` | **`PASS`**, `authorizes_4_6: true` | `TOKEN-REJECT` — **13 files in scope changed at HEAD** |

> *"A PASS cannot authorize code the verifier never saw; re-run the verifier."*

**It was already unsatisfiable before the 2026-09-21 L2 change, and that is measured:** the same
token against `f6f54e73` rejects with **10** changed files. The ten that predate L2 are `p4_lib.py`,
`p4_evidence.py`, `p4_build_components.py`, `seed_offset_policy.py`, `project_cov_nd.py`,
`uq_math.py`, `p4_project_4d.py`, `p4_validate_active_lateral.py`, `p4_check_verifier_token.py`,
`unfold_nd_omnifold_unbinned.py`. L2 added `p4_check_receipt.py`, `run_p4_standard.sh`,
`run_p4_unfold_std.sh`.

### ⚠ 2.1 WHO MAY RE-RUN THE VERIFIER — and why the previous session did not

The previous session **declined to self-issue the token** because it authored all eight sites under
review. `nd-unfolding/p4_check_verifier_token.py`'s own docstring records why the gate exists:

> It was demonstrated load-bearing on 2026-08-07: an autonomous run that **self-authorized** would
> have written a candidate ROOT at stage 4 … **The fix is deliberately not "check the variable
> harder."** An agent that can set an env var can also write a JSON file.

⚠ **A COMPUTE AUTHORIZATION DOES NOT DISSOLVE THIS.** Joseph authorized compute (*"use as much
compute as you want"*, 2026-09-21). He has **not** dispensed the independence requirement, and the
two are different permissions. **If you did not author those 13 files you may legitimately run the
verifier. If you did, you may not — route it to Joseph for an explicit dispensation and let him
choose.** Do not read a compute grant as a review authorization.

**A PASS must carry:** `verdict: "PASS"`, `authorizes_covariance_stages_4_6: true`, a **literal
40-hex** `code_rev` that is an ancestor of `HEAD`, and its scope byte-identical between that commit,
`HEAD` **and** the working tree. Scope is the **union** with the execution surface — a verifier may
review more than the chain executes, never less.

**What a PASS would NOT authorize:** it unblocks stages 4–6 mechanically. It is **not** a grade, not
a clearance of M1–M4, and not a licence to quote a significance.

## 3. ⚠ ITEM 2 — THE L2 PROBE: TEN UNFOLDS EXIST, THERE IS NO `s_proj`, AND THE ANSWER IS UNKNOWN

Full record: `docs/orchestration/OUTCOME-20260921-L2-probe-blocked-at-stage-4.md`.
Predeclaration (with two amendments): `docs/orchestration/PREDECLARATION-20260921-L2-lateral-seed-release.md`.

The probe asked whether M1's FAIL survives releasing M3's five seed-pinned bands. **It is not
answered** — it stopped at §2's gate. This is recorded as an **inability** under the
predeclaration's own third outcome row (*"cannot be computed … it is not a result of any kind"*),
fixed before the run.

**What exists and must not be recreated** — ~2.9 CPU node-hours through a queue with 11 idle nodes
of 2853:

| | |
|---|---|
| worktree | `/pscratch/sd/j/josephrb/MINERvA-OmniFold-l2-20260921`, **detached** at `c05c64a9` |
| ten member unfolds | `<worktree>/nd-unfolding/mii/member_k001200/active_universe_5d/standard/unfolds/` |
| member manifest | `…/standard/evidence/p4_standard_manifest.json`, `sha256 aa5c22226f2ac84b…` |
| uniformity proof | **one** distinct `config_hash` `4809b4ad399f999c…` across all ten receipts (baseline is `4b41fab90a83df08…`) |
| stage 4–6 scripts | `<worktree>/{l2_stages_2_to_4.sh,l2_stage5_assemble.sh,l2_stage6_measure.sh,sbatch_l2_debug.sh}` |

⚠ **`git worktree prune`, `git worktree remove`, or a scratch purge destroys all of it**; the
products are gitignored and nothing else holds a copy. The name looks dated and disposable. It is
not.

**Two design facts a fresh session will otherwise get wrong:**
1. The member to rebuild is **`member_k001200` with its lateral block swapped**, reusing that
   member's own `stat`/`ml`/`support`/`throw`. The graded pair
   (`/pscratch/sd/j/josephrb/z2m-products/member_k000000` and `…/member_k001200`) already differ in
   those four legs and **share `active`** — both z-manifests name candidate
   `sha256 950f8cb15c5a0bd785d65e7f85f4cb40fa86e27383973f82ef15c7ef525c1263`. **That shared row IS
   the L2 limitation, readable from the campaign's own records.** Building against the archive
   instead varies four extra legs and measures a different question.
2. **Stage 6 runs a reproduction control FIRST** and declares the released-lateral number
   uninterpretable unless the control reproduces `s_proj = 6.145388143592225%` to `1e-12`. **A
   released-lateral number arriving with a failed control is not a result.**

**THE OUTCOME MAP IS FIXED AND MAY NOT BE RE-CHOSEN AFTER SEEING A NUMBER:**
`> 5%` confirms M1's FAIL with the five varying; **`< 5%` LICENSES NOTHING** — one seed pair cannot
show a maximum over the declared set lies below a bound; "cannot be computed" is an inability.
**Nothing in either branch** moves `3d7465f6…`, regrades cause 3, or licenses a significance.

## 4. ⚠ ITEM 3 — THE TEN ADOPTED RECEIPTS ARE STALE, AND THE DOCUMENTED COMMAND DESTROYS THEM

**Measured read-only on the deployed checkout, 10 of 10:**

```
RECEIPT-REJECT :: receipt BeamAngleX_0 unfold_blob dc74c38f8ec7b5f6723fa231630e9fc43e7a93f0
                  != committed 662951e019f9c96c2876decc7913c7e9b3dbf2ae:
                  the unfold driver changed since this endpoint was produced
```

`nd-unfolding/unfold_nd_omnifold_unbinned.py` changed after 2026-08-08 (`5afb7947`, `ae42ae8d`,
`0a4ab263`, `1aa055d9`) and `validate_endpoint_receipt` compares that blob **strictly** — correctly;
it is the producing-code binding. Consequence: **`bash run_p4_unfold_std.sh` with no offset
re-unfolds and `mv -f`s over the ten endpoint unfolds the adopted covariance is built from, exit 0,
no warning.**

**Guarded at `e2632ac7`:** the driver now refuses (`rc 9`) when the ROOT exists, the namespace is
not member-scoped, and `P4_ALLOW_BASELINE_REUNFOLD=1` is absent. Tests:
`nd-unfolding/tests/test_baseline_overwrite_guard.py`.

⚠ **THE GUARD PREVENTS ACCIDENT; IT DOES NOT RESTORE VALIDITY.** Whether the ten receipts should be
re-pinned — or the endpoints re-produced and the covariance re-derived — is a **decision nobody has
taken**, and it is not a code change. **What re-pinning would NOT authorize:** it would not
re-verify the physics, and a re-produced endpoint set would invalidate `3d7465f6…` and everything
downstream of it.

## 5. ITEM 4 — NO INDEPENDENT CUTOFF SCAN ON THE PUBLICATION PROJECTION

| | |
|---|---|
| product | `/pscratch/sd/j/josephrb/z2m-products/PROJ/cov_5d_to_eavailW_publication.root` |
| `sha256` | `835828bf3e25bbd9f279088e5cc89b8b325d727446fec9fabbbc92fd7e71a54e`, `17,101` B |
| receipts | `docs/orchestration/state/PROJ-20260920-m1-publication-receipt.json`, `…/PROJ-20260920-binding-check.json` |

Every statement about this product's spectrum currently rests on **that run's own output** agreeing
digit-for-digit with the diagnostic's. **No independent 42×42 scan on those bytes exists.**

**This is a MEASUREMENT, not an authorization**, on code (`nd-unfolding/project_cov_nd.py`) that the
L2 session did not author — so the independence bar of §2.1 does not apply, and Joseph's compute
grant covers it. It is cheap. It needs **its own receipt and a `VALIDATION_LEDGER.md` row**.
**What it would NOT authorize:** a spectral scan confirms the spectrum; it does not discharge
M1–M4, does not bear on cause 3, and does not make the projection publication-ready.

## 6. ITEM 5 — CAUSE 3 IS NOT DISCHARGED FOR THE ADOPTED BYTES

Three separate facts, all live:
- `M(i)` is **`UNRESOLVED` on `4c`** — a **permanent** predeclaration failure. It cannot be cured by
  running anything.
- `C3` is **predeclared and NOT computed** for `3d7465f6…`.
- **All seven declared boundaries measure `read_by_production: no`** — `z_validator.assess` had no
  production caller when that census was taken. ⚠ **This changed on 09-19**: `z_build.py:762` and
  `z_grade.py:616` are now callers (`VERIFICATION-20260921-v6-six-items-reproduced.md` §1 item 4).
  **Re-measure before quoting the census.**

⚠ **No criterion may be described as *applied*, *satisfied*, *passed* or *met*.**

## 7. ⚠ CLUSTER RULES THAT WILL BITE YOU

- **The deployed checkout `/pscratch/sd/j/josephrb/MINERvA-OmniFold` is at `32e403b8` and must not
  be moved.** PET's array `58692544` runs from it and a HEAD-pinning launcher turns a redeploy into
  killed PENDING jobs. Use a **detached worktree** instead; verify the deployed HEAD before **and**
  after (`git -C <deploy> rev-parse HEAD`).
- When you create a worktree, its data inputs must be symlinked **at the granularity where no
  tracked file exists** — `active_universe_5d/standard/{merged,unfolds,unfolds__SUPERSEDED_20260718}`,
  `products/5d`, `products/4d`, `MINERvA101/opt`. Linking a parent directory makes `ln -sfn` nest
  the link **inside** it rather than replacing it.
- `run_p4_standard.sh` **REFUSES** a declared `MNV_EST_SEED_OFFSET` (exit 2). Stages 2–4 are
  member-aware; 1, 5 and 6 are not, so the orchestrator refuses rather than running half-aware.
  Drive member stages directly.
- **CPU is the scarce allocation**, not GPU: `m3246` at `16,529 / 20,000` node-hours vs `m3246_g` at
  `120,669 / 180,000`. The CPU partition was saturated (11 idle of 2853); `regular` quoted **8
  days**, `debug` started in minutes with a 30-minute cap. A P4 endpoint unfold is **~23 min** at
  `CONC=2`. The driver publishes atomically and resumes, so chained `debug` jobs make cumulative
  progress.
- Read a job's status **without a pipe**; a pipe rewrites `$?`.

## 8. ⚠ SHARED-CHECKOUT AND INSTRUMENT HAZARDS MEASURED ON 2026-09-21

These cost real damage in one evening. They are not style notes.

1. **`git commit -m` without a pathspec commits the WHOLE INDEX**, including whatever another
   session staged seconds ago in this shared checkout. It happened twice; the second time it
   committed 24 files belonging to another lane under an unrelated subject line **and pushed them**,
   pre-empting a push reserved to Joseph. **Always `git commit -- <explicit paths>`, and run
   `git show --stat HEAD` before pushing** to confirm every path is one you meant to write.
2. **`git ls-files` counts a peer's STAGED path as tracked.** For "is it committed", use
   `git ls-tree HEAD <path>`.
3. **`git log -1` on a path dates its LATEST touch, not the claim's first landing.** Use
   `git log -S '<string>' -- <path>`. Using different instruments on the two sides of a comparison
   inverted a 2h05m ordering into a 4h28m one pointing the other way.
4. **An occurrence detector pointed at a document that DISCUSSES the occurrence is unsound.** A file
   that correctly withdraws a claim must quote the claim, so `grep` for the claim matches the fixed
   file. Match the **assertion form**, or strip the correction block first. This produced both a
   false negative and a false positive on the same file within ten minutes.
5. **A quote that spans a newline is invisible to a line-oriented grep.** Use `tr '\n' ' '` first.
6. **zsh does not word-split unquoted variables** — `for f in $LIST` iterates once over the whole
   blob. Use `while read -r`.
7. Before running any "check that nothing happens" command against a product you care about, **state
   its FAILURE branch**. If the failure branch writes, deletes or regenerates, it is not a control.
   A predeclared safety check here would have destroyed the adopted covariance's inputs (§4).

## 9. THE NOTE SIDE — resolved in the document, DISCLOSED but not fixed underneath

Relayed from the lane that did the 2026-09-21 manuscript-review fixes; independently spot-checked
where cheap (marked ✓). A manuscript review raised 10 publication blockers plus minor items; **all
are resolved in the document.** What follows is what is *disclosed and not fixed*. **A fresh session
must not read any of it as settled.**

### 9.1 Appendix F specifies a result package that DOES NOT EXIST

`docs/analysis-note/app_release.tex` is a **specification plus identity register**, not an index of
something published. ✓ **Verified: 35 tags — 30 `evidence/*`, 1 `freeze/*`, 4 `z-deploy-*`, and
ZERO matching `*release*`.**

Already pinned, needing no work: digests, shapes, the C-order row index, dropped-axes bin-width
weighting, `src_cells_dropped = 0`, exact bin edges for all five axes, one worked projection
example.

**What remains is packaging, not analysis** — the arrays are on `/pscratch`, not in the repository.
⚠ **One field must be carried VERBATIM and never defaulted:** the projection receipt records
`acceptance_question: UNDECLARED`. A silent default there is **a scientific choice made by a data
format**. ⚠ Shipping the package is **outward-facing and therefore reserved**.

### 9.2 Four live figures read a QUARANTINED covariance — marked, not fixed

| figure | producer | reads |
|---|---|---|
| `generators_vs_unfolded_band` (note Fig. 20) | `overlay_generators_band.py` | `hCov_combined3d_total` |
| `compare_mec_eavail` (`fig:mec`) | `compare_mec_eavail.py` | same |
| `mode_decomp_eavail` (`fig:modedecomp`) | `mode_decomp_eavail.py` | same |
| `ascencio_fullcov_compare` (`fig:ascencio`) | `compare_ascencio_fullcov.py` | historical unified-throw **4D** covariance |

Every caption now says so. **They cannot be regenerated correctly yet**: the quotable 3D covariance
must be projected from the adopted 5D trunk and **that projection has not been built**. Marking is
the remedy until it is.
⚠ **The primer no longer uses any of them** — Fig. 3 was swapped to `eavailW_band` (central-value
only, no `--cov`) and Fig. 4 to `paper_joint_localization`. **If you regenerate these, do NOT
silently reintroduce them to the primer**; that leakage was blocker 2 of the review.

### 9.3 ⚠ DISCLOSED, NOT RESOLVED — seven items a cold reader will otherwise treat as settled

- **Detector-response mismatch: NO RESULT EXISTS.** `app_response_mismatch.tex` defines the closure;
  §7's closure title was narrowed because its one injected `+30%` Gaussian in truth `E_avail` uses
  **the same response on both sides**, so it cannot speak to mismatch at all.
- **Independent-truth coverage: no claim supported.** The 200-toy 2D ensemble fluctuates the *stored*
  truth. **No 2D coverage number is quoted anywhere**; Appendix A's calibration language was removed
  on this ground.
- **The hidden-variable closure EXCEEDS its own threshold** at the largest amplitude — `3.43%`
  against a `3.0%` bound at `A = 0.30`. "Safely ignorable" was an arithmetic error and is withdrawn.
  Linear in amplitude, `κ = 0.113`, so the bound holds to about `A ≈ 0.26` and **fails above it**.
- **No goodness-of-fit is claimed for the 2D reproduction**, and it cannot be calibrated: shared
  data, and `Cov(x−y) = C_x + C_y − C_xy − C_yx` with the cross terms unavailable. The agreement
  claims are the ratio, the per-bin ratio distribution, and published-σ standardized differences.
- **The smaller bootstrap is NOT established as higher efficiency.** The data/MC split excludes an
  MC-statistics omission and nothing more; regularization bias and undercoverage remain live.
- **PET carries no adopted uncertainty.** `OI-126` declined the pairing 2026-08-20; reconsideration
  needs estimator-equivalence **and** coverage — a different object from verifying construction.
- **Background-footing equivalence is BINNED-LIMIT ONLY.** Purity weighting gives
  `D(x)(1 − B_b/D_b)`, equal to `D(x) − B(x)` only when `B/D` is constant within the bin. The 2D
  agreement is measured; **there is no 5D both-footing comparison at the publication configuration.**

### 9.4 ISSUE-59 — a stale figure asset, with its exact re-run

`docs/analysis-note/figures/pet_cloud_projection_xsec.pdf` is the **pre-coverage-fix** projection
(written at `6749ddf8`, 2026-07-05); the corrected summary is `b203b3d5`, 2026-07-16, whose three
curves agree to `0.4555%` max relative spread over seven bins (`values.tex`'s `\pcCloudFull`).
**The note's NUMBERS are correct and come from the JSON; only the picture is stale**, and
`sec_pet.tex` now says so in caption and body.

Re-run is `docs/analysis-note/make_figures.sh:78-83`, on Perlmutter, `/pscratch`-only inputs:

    cd $REPO/nd-unfolding && env \
      PCPROJ_PC="$REPO/nd-unfolding/of_inputs_pc_fullcloud.npz" \
      PCPROJ_WEIGHTS="$REPO/nd-unfolding/products/pet/pet_weights_fullcloud.npz" \
      PCPROJ_OMNI="$REPO/nd-unfolding/runEventLoopOmniFold_PC_MEFHC_fullcloud.root" \
      PCPROJ_OUTDIR="$REPO/nd-unfolding/products/pet/fullcloud" \
      python pet/pointcloud_projection.py

⚠ **Do NOT run it with the defaults** — those are the pre-fix diagnostic inputs and would reproduce
the defect. ⚠ **This is PET-adjacent; §0 applies.**

⚠ **Adjacent, unexplained, and DO NOT "fix" it by substitution:** the pre-fix `empty_cloud` fraction
is `27.395%`, **not** the `37.885%` `truth_only_miss` fraction `sec_pet.tex`'s prose implies by
saying the appended miss rows carried no cloud. Either not every miss row lacked one, or some
reco-signal rows did. **Real, and the two numbers are not interchangeable.**

### 9.5 Two dangling/cosmetic defects, both verified, both deliberately unfixed

- ✓ **`VALIDATION_LEDGER.md` VL143 has two unescaped pipes** inside `max|C − Cᵀ|` — **measured
  5 / 7 / 5 pipes for VL142 / VL143 / VL144**, so VL143 splits a cell in a strict renderer. Left
  alone because fixing it **edits a rendered measurement string**.
- ✓ **`docs/analysis-note/make_figures.sh:59` cites `KNOWN_ISSUES #18`, and there is no row 18** —
  **measured: rows run … 16, 17, 19, 20 …**, so the citation dangles. (Rows 12–15, 18 and 22 are all
  absent; only 18 is cited.)

## 10. ⚠ WHO MAY CHECK WHAT — three items have no independent checker left

Tonight's two other lanes each fixed things they had also found, which spends their independence:

| item | not independent | needs |
|---|---|---|
| **site 9** (`nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md`) fix | the reviewing lane (it made the fix) | a third pair of eyes |
| **ISSUE-60** (three unmappable-green checks) | the reviewing lane (it filed it) | a third pair of eyes |
| **§4c of the 09-21 correction record** | the note lane (the instrument is credited to it) | a third pair of eyes |

⚠ **A lane that supplies a remedy has spent its next verdict on that object.** The same rule stopped
this lane issuing its own `P4_VERIFIER_PASS` (§2.1). Do not let a fresh session accept any of the
three on the word of the lane that produced it — including this handoff's own account of them.

### 10.1 The sweep method that found site 9 after two sweeps missed it

Carry this; it is the most reusable thing from the evening.

1. **A phrase search cannot separate an assertion from its own retraction**, because this tree
   retracts by **quoting**. The discriminator is the part of the sentence the correction *changed*
   — here `estimator and …` versus `estimator rather than of the ensemble's …` — plus a count of the
   `⚠ CORRECTED` marker.
2. **The population for a withdrawal is NOT a directory glob.** It is **the file list of the commit
   that planted the claim**: `git log -S '<claim>' --reverse` for the sha, then
   `git show --name-only` for the blast radius. **Site 9 was outside `docs/`, which is exactly why
   two `docs/`-scoped sweeps never saw it.**
3. **A quote spanning a newline is invisible to a line-oriented grep** — `tr '\n' ' '` first.

## 11. NOT GBDT — listed only so you do not adopt them

- **ISSUE-60 (HIGH)** — three unmappable-green checks: `generate_manifest --check` needs a
  `--staged`/`--at-sha` mode (it regenerates from the WORKTREE even under `--committed-only`, so its
  green attests nothing about a sha); a caller-discipline item; and `live_doc_indexed.py` needs a
  whole-tree-first inversion (it is staged-diff based, so it reported "nothing newly LIVE" on every
  run while a new record went in unindexed). ⚠ **Filed by the session that also fixed site 9, so
  that session is no longer independent on either — both need fresh eyes.**
- **Appendix F specifies an external result package that DOES NOT EXIST.** The arrays are on
  `/pscratch`; there is no release tag or manifest (35 tags, none a release). **Assembling it is
  packaging, not reanalysis** — and shipping it is outward-facing and therefore reserved.
- **ISSUE-59** — detailed at §9.4 with its exact re-run. **PET-adjacent; out of scope per §0.**

## 12. THE SHORT VERSION

**Nothing here blocks publication on its own. Two items need a human decision, one needs a
non-authoring lane, and three have no independent checker left.**

| # | item | § | who |
|---|---|---|---|
| 1 | verifier re-run → unblocks standard-P4 stages 4–6 **lane-wide** | §2 | a lane that did **not** author the 13 files, or Joseph dispensing explicitly |
| 2 | the ten stale adopted receipts: re-pin, re-produce, or accept | §4 | **Joseph** — no code change resolves it |
| 3 | 42×42 cutoff scan on `835828bf…` | §5 | anyone; cheap; needs its own receipt + ledger row |
| 4 | L2's `s_proj` with the five laterals released | §3 | after item 1; ten unfolds already exist, do not recreate |
| 5 | the 3D covariance projection from the adopted 5D trunk | §9.2 | unblocks four marked figures |
| 6 | Appendix F package | §9.1 | packaging, not analysis; **shipping is reserved** |
| 7 | site 9 / ISSUE-60 / §4c | §10 | a **third** lane — their authors are spent |

⚠ **THE THREE THINGS MOST LIKELY TO BE GOT WRONG BY A SESSION READING A SUMMARY:**

1. **M1–M4 travel with every use of `3d7465f6…`** (§1). The adoption is
   *publication-under-exception*, not a clean pass. `M2`'s *"larger ensemble would not reduce it"*
   is **withdrawn**; `M3`'s *"lower bound"* is **withdrawn**; `M4` is **much larger per single 5D
   bin** (max `49.8%` of `σ`) than per projection.
2. **A COMPUTE grant is not a REVIEW authorization** (§2.1). Joseph authorized compute; he did not
   dispense the independence requirement, and a lane may not certify code it wrote.
3. **`bash run_p4_unfold_std.sh` destroys the adopted covariance's inputs** unless the `e2632ac7`
   guard is present (§4). Do not run it. Do not "fix" a stale receipt by re-unfolding.

**And two instrument rules that cost real damage on 2026-09-21** (§8, §10.1): `git commit --
<explicit paths>` always, never `git commit -m` alone in this shared checkout; and an occurrence
detector pointed at a document that discusses the occurrence is unsound by construction — this tree
retracts by quoting.

**Co-Authored-By: Claude Opus 5 (1M context)**
