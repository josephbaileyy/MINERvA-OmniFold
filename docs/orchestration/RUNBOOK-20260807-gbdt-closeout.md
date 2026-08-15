# RUNBOOK — closing out the GBDT (scalar) lane, 2026-08-07

**Purpose.** Take the scalar/GBDT side from its 2026-08-07 state (FPS lateral adopted, 5D still
CANDIDATE) to *adopted 5D + marginalized 4D + final FPS + note updated*. Written to be handed to a
fresh Claude session that has read `CLAUDE.md` and nothing else about this lane.

**Both blocking decisions were made by Joseph on 2026-08-07, before this runbook was handed off — see
§2.** You do not need to wait on anything to start. Nothing in this lane needs a GPU.

**Scope.** Runbook packets **P3S, P3F-scalar, P4-5D, P4-4D, P4-FPS**, plus the P7 note update for
those products only. The PET lane (`P5A`/`P5B`, Gate-4, the D2 closure, the nominal's normalization
failure) is **explicitly out of scope** — it is blocked on decisions that are Joseph's and on GPU
contention, and mixing the two lanes is how a session burns a cycle on neither. If you find yourself
reading `nd-unfolding/pet/`, you have left this runbook.

**Instructions only; never a run receipt.** Per this repo's convention, completion state goes to
`docs/OPEN_ITEMS.md` and the STATUS files, numbers to `VALIDATION_LEDGER.md`, chronology to the
RUN_LOGs. Do not record results here.

**Read first:** `docs/orchestration/FINDINGS.md` (especially BEN-036, BEN-040, BEN-041 — all three are
this lane), `KNOWN_ISSUES.md` **#20**, then `docs/PUBLICATION_COMPLETION_RUNBOOK.md` packets P3S /
P3F-scalar / P4, and `docs/RESULT_DEPENDENCY_AND_RERUN_MAP.md` for the invalidation frontiers.

---

## 1. State as verified 2026-08-07

Everything in this table was read from a command run while writing this file — code and launchers from
the tree, artifacts and job records from Perlmutter. Re-verify before acting; scratch is purgeable.

| Item | State | Evidence |
|---|---|---|
| P3S / P3F event-loop coverage | **COMPLETE** — 120/120 P3F + 120/120 P3S per-playlist, ten 74.8 GB merged omnifiles | BEN-036; merged-input receipt `run_id 56090877`, 748 GB, 10/10 unchanged |
| P3F-scalar publication-footing unfolds | **DONE** — ten `negweight-refined` endpoint unfolds | `56430128_[0-9]`, all `COMPLETED 0:0` |
| **P4-FPS lateral component** | **ADOPTED, VERIFIED-NUMERIC** — lateral `7.30356e-39 → 8.10399e-39` (+10.96%); combined FPS `8.040779e-39 → 8.774217e-39` (+9.1215%) | job `56431823`, 53:56, four steps rc=0; ledger "2026-08-07 selection-complete five-band FPS active lateral" |
| J28 flux defect | **RESOLVED on 160/160** — adopted mean-centered `5.2600e-38`, CV-centered `5.6609e-38`, both PSD | regen `56427580` (tasks 30–39), adopt `56429334` rc=0 |
| **P4-5D adoption** | **CANDIDATE — not adopted** | ledger heading "2026-07-14 corrected 5D GBDT covariance — CANDIDATE; final lateral replacement pending"; the J28 entry states this remains true and is unaffected by J28 |
| Standard (5D) lateral component | **NOT BUILT, AND NOT ONE RUN AWAY** — no `*activelat*` product exists outside the FPS namespace, and candidate construction is **BLOCKED by the standard-p4-verifier**: repair-3 `74fa362` returned **BLOCK with six ranked defects** and **no repair-4 commit was ever made**. Added 2026-08-12: this row said only "NOT BUILT", which reads as a launch away, and `P4_STANDARD_STATUS.md` names that omission as the finding — the brief sat five days unworked because the only doc most readers open did not carry the BLOCK. Repair brief: [`followup-agent-A-standard-05.md`](followup-agent-A-standard-05.md). ~~Two preconditions for whoever takes it: **stage 3 must not run on pre-G-1 code** (it writes ten receipts with no `bkg_mode`, the launcher skips endpoints that already have one, and deletions are frozen → unfixable provenance regression), and **G-1 is code-only and not on the cluster checkout**.~~ **BOTH PRECONDITIONS STRICKEN 2026-08-15 (`BEN-352`); superseded text retained per this repo's convention. NEITHER SURVIVES.** (a) **G-1 IS on the cluster checkout** — cluster `HEAD` `683bdcc`, `git merge-base --is-ancestor 5a4009f HEAD` → true, measured this session. (b) **Stage 3 ALREADY RAN on it**, 2026-08-08: ten ROOTs + ten `.done`, `mode=produced`, `bkg_mode=purity`, `code_rev=42268b6` (which contains `5a4009f`). (c) **The irreversibility claim is REFUTED IN CODE** — `run_p4_unfold_std.sh:77-84` skips only on a PASSING `p4_check_receipt.py`, not on receipt existence; `bkg_mode` is required (`p4_lib.py:796-797`, enforced `:949-950`) and compared (`:961-962`), so a receipt without it fails the gate, is `rm -f`'d and re-run. **The claim was TRUE when this row was written and was fixed by `febb9a1` the same day**, then copied forward here. **NOTE: this row's `BLOCK` verdict and "NOT BUILT" status are UNAFFECTED and still stand** — the products above are untracked, unreconciled with Joseph's cluster-P4 hold, and authorize nothing (`OI-75`). | `find` over `uq_5d` + `uq_fps` on scratch returns exactly one, the FPS one; BLOCK verdict and the never-made repair-4 per `active_universe_5d/standard/P4_STANDARD_STATUS.md` (BEN-046 correction), which verified it by `git log 74fa362..HEAD` over `p4_*`/`run_p4_*`/`tests/test_p4_repair.py` |
| Standard lateral endpoint unfolds | **EXIST but are not publication-grade** — see §3 | ten ROOTs + ten logs dated 2026-07-18 03:53–05:34Z, **zero `.done` receipts** |
| P4-4D | **NOT DONE** | no adoption packet |
| Final FPS budget | **NOT FINAL** — the +9.12% is to the *pre-uthrow* covariance | ledger "Scope" paragraph of the 08-07 entry |
| `values.tex` | **STALE** — still quotes the superseded `5.81e-38` / `6.24e-38` / `1.65e-38` | `docs/analysis-note/values.tex:57-60` |
| 2026-07-12 quarantine | **STANDS** — the lateral discharges one named precondition only | ledger head, and the 08-07 entry's own "Scope" |

**Resource note.** Nothing in this runbook needs a GPU. The FPS analogue chain ran
`--qos=shared --constraint=cpu --cpus-per-task=16 --mem=32G`, and the standard unfolds ran CPU-only
under `srun --gres=none`. That matters because the PET lane is holding the GPU queue (`56431651` has
been PENDING ~16 h) — this lane can proceed in parallel without contending.

---

## 2. DECISIONS — both made by Joseph 2026-08-07, before the executing session starts

> **DECIDED (2026-08-07).**
> 1. **Footing: the standard 5D chain is quoted on `purity`, revisited before submission.** Not a
>    silent default — a recorded choice, backed by the measurements in §2.1, and carrying an explicit
>    obligation to revisit (tracked as **G-0** below). Proceed on purity so P4-5D/4D and the note
>    unblock; do **not** re-run the standard chain on `negweight-refined`.
> 2. **4D: adopt the exact 5D→4D marginal and label the independent 4D estimator a cross-check.**
>    No separate 4D lateral work — the 4D inherits the corrected 5D lateral. `p4_project_4d.py` is the
>    implementation (stage 6 of the canonical chain).
>
> The reasoning that produced these is kept below because a referee question, or a future session
> tempted to "fix" the footing, needs it.

### 2.1 The data backing the purity choice

Joseph asked whether the negweight-vs-purity impact was ever quantified. **It was, at full statistics
with the adopted estimator, and the answer is ~1–2% on the covariance.** All of this is 2D MEFHC unless
stated; source `2d-unfolding/HANDOFF_bkg_negweight/bkg_negweight_state.md`, 2026-07-09/11 entries.

| Comparison | Result |
|---|---|
| **SYST (universe) covariance**, 187 universes, both modes, #13-active | negweight `sqrt(tr) = 2.9828e-39` vs purity `3.0242e-39` → **ratio 0.9863** |
| **STAT (bootstrap) covariance**, matched first-50 seeds | negweight `1.7260e-40` vs purity `1.7576e-40` → **ratio 0.982** |
| **CV identity**, MEFHC, adopted **lgbm** | per-bin median **1.0001**; 127/148 within 1%, 145/148 within 5% |
| **Real-data totals** | agree to **−0.13%**; per-bin median 1.000, **1.4% RMS**; the only >few-% bin is one low-`pT`, high-background edge bin (0.874) |
| **5D spot check** — the on-disk 5D universe omnifile, 2 universes | `2p2h:0` purity `3.014e-38` = negweight `3.014e-38`, per-bin median 1.0005; `MaCCQE:0` **−0.03%**, median 0.9990 |

**Why this generalizes rather than being two lucky universes:** the ρ1 = D − B_u identity. A systematic
covariance is the *spread across* universes, and each universe shifts by the same ~0.1% in both modes,
so the two covariances agree by construction. The negweight state doc calls the full 187-universe
rebuild "CONFIRMATORY" on exactly those grounds — and then ran it anyway, which is where the 0.9863
comes from.

**The one real estimator caveat, and why it does not bite here.** Raw `negweight` *breaks* the `exact`
GradientBoosting backend — a ~5×10⁴ blow-up across the `iy=1` row, the classic negative-sample-weight
pathology of gradient-boosted trees. Stay-Positive (`negweight-refined`) cures it (refined/purity
median 0.9991, 141/148 within 5%, blow-up row 36000× → ~0.9×). **The standard 5D chain runs `lgbm`**
(`--estimator lgbm` in the unfold invocation), which is the clean backend, so neither footing risks
that pathology in this lane.

**What is still NOT measured, and is the whole content of the revisit obligation:** there is no full 5D
187-universe both-mode comparison at the publication 5-iter lgbm config. The 5D evidence is a
two-universe spot check at 1 iter / `hist`, plus the structural identity, plus the 2D full-statistics
result. That is ample for "quote purity and say so" and **not** ample for "footing is proven
irrelevant in 5D". Do not write the latter.

### 2.2 The reasoning (retained)

**Question: what background footing does the *standard* 5D chain stand on for publication?**

The FPS lane's publication footing is `negweight-refined` (`fps_provenance.PUBLICATION_BKG_MODE`), and
its purity products are labeled controls. The standard 5D chain is **entirely purity-footed**, and
consistently so — see §3. Locked estimator decision 1 in
`docs/PUBLICATION_COMPLETION_RUNBOOK.md` reads *"Scalar FPS/N-D production uses explicit
`--bkg-mode negweight-refined` … Purity products are matched controls only."* Whether "N-D" reaches the
standard-phase-space 5D chain or only its FPS form is **not resolved anywhere in the repo**, and the
two readings differ by more than an order of magnitude in cost:

| Reading | What must run | Cost |
|---|---|---|
| **(A) Standard 5D stays purity, consistently labeled** | Build + validate + adopt the standard lateral from the *existing* ten unfolds; add a footing field so the choice is provable (§4) | Hours, CPU only. No physics re-run. |
| **(B) "N-D" includes standard 5D** | Re-run the central, **169 vertical**, **18 detector**, and 10 lateral unfolds on `negweight-refined`, then rebuild every component and re-adopt | A full chain rebuild. Invalidates the J28-corrected covariance that was just adopted. |

**Recommendation: (A), with the footing stated explicitly in the note.** Reasoning:

1. **Mixing footings inside one covariance is strictly worse than either consistent choice.** The
   adopted 5D covariance is `lateral + stat + ML + G C_vert G`; dropping a `negweight-refined` lateral
   block into a purity-footed central and vertical set is a footing mismatch, not an upgrade.
2. **The FPS lane already delivers the negweight-footed measurement.** Under (A) the standard chain
   is the matched control/cross-check at a different footing, which is a defensible published pair.
3. **The runbook's own P4-5D text asks only for "the P3S lateral replacement"** — it does not ask for
   a footing change, and it lists no footing precondition for P4-5D.
4. **The 2026-07-12 quarantine's cause list does not include background mode.** Its named causes are
   one-sided endpoint interpolation, CV centering, varying estimator seeds, scalar jitter subtraction,
   frozen PET weights, incomplete statistical projection, and CV-support-limited lateral selection.
   If purity footing invalidated the standard 5D, that list is where it would say so.
5. `2d-unfolding/HANDOFF_bkg_negweight/bkg_negweight_state.md` explicitly leaves this open:
   *"ND/5D CV + any FPS rerun: coordinate with user first"* and *"Default switch + headline reruns
   remain the user's call."* The port added `--bkg-mode` to the ND driver as an **option**; the
   standard default was never switched. That is a deliberate deferral, not an oversight.

**Do not re-open this by reading the runbook sentence harder.** It is genuinely ambiguous; that is why
it went to Joseph rather than being resolved from the text. Reading (A) is the recorded decision. If
someone later reverses it to (B), this runbook's §4 is wrong about cost and the re-plan starts from
`RESULT_DEPENDENCY_AND_RERUN_MAP.md`'s "Scalar FPS background mode or target changes" trigger row.

**The 4D route.** Decided: the exact 5D→4D marginal, with the independent 4D labeled a cross-check.
`p4_project_4d.py` (stage 6) implements it, and the 4D inherits the corrected 5D lateral, so there is
no separate 4D lateral component to build. **Do not rerun the corrected R1 4D throws** — that holds
under either route and is an explicit "explicitly unaffected" row in the dependency map.

---

## 3. The footing check — what was run, and what it proves

This is the check that motivated this runbook. Recorded in full because the conclusion is load-bearing
for §2 and because a future session will otherwise re-derive it.

**Question.** Are the ten standard active-lateral endpoint unfolds at
`nd-unfolding/active_universe_5d/standard/unfolds/` publication-grade, and on what footing?

**Method.** The same three-part evidence structure `fps_build_control_manifest.py` uses to prove a
purity control: (a) does the producing launcher pass `--bkg-mode`; (b) what is the driver's source
default; (c) negative evidence from the logs.

**Findings.**

1. **They are purity-footed, positively identified — not merely unstamped.**
   - (a) Neither possible producer passes `--bkg-mode`: the canonical `run_p4_unfold_std.sh:43` and
     the retired `run_active_lateral_unfolds_interactive.sh:40` both invoke the driver with
     `--axes eavail,q3,W --iters 5 --use-weights --estimator lgbm --seed 42` and no mode flag.
   - (b) `unfold_nd_omnifold_unbinned.py:566` — `--bkg-mode` default is `"purity"`.
   - (c) The driver announces its mode **only on the negweight branches** (lines 842 and 895); the
     purity branch (`elif args.bkg_mode == "purity":`, line 883) prints nothing about mode and instead
     calls `build_measured_training_nd(..., verbose=…)`. All ten logs contain that call's signature
     line `[INFO] measured training: sum=… zero=…` and **no** `bkg-mode=` line anywhere. So the logs
     positively identify the purity code path, rather than being silent.
   - Note `--bkg-mode` and both announcements landed together in `cf8a4a6` (2026-07-11), a week
     *before* these files, so absence of the announcement is informative rather than a version gap.
2. **They were produced by the RETIRED launcher and have never been receipted or attested.**
   `run_p4_unfold_std.sh` writes `${OUT}.done` last, after an atomic rename, and its legacy-attest
   path writes one too. The directory holds **zero** `.done` files. The ROOTs are dated 2026-07-18
   03:53–05:34Z; `run_p4_unfold_std.sh` was added the *same day* in `553a6a6` ("#16 P4
   standard-lateral: fail-closed hardening + tests (REPAIR ONLY)"). These files predate or bypass the
   hardened path. `run_active_lateral_unfolds_interactive.sh` now aborts with exit 9 on
   `MODE=standard` unless `ALLOW_RETIRED=1`.
3. **The standard manifest cannot record a footing at all.** `p4_evidence.py` contains no
   `bkg`/`footing`/`mode` handling; the standard manifest binds `endpoint_sha256` and code/config
   hashes only. Contrast `fps_provenance.require_footing`, which fails closed when an entry has no
   `bkg_mode` ("unprovable"). **The standard lane's provenance is footing-blind by construction** — so
   whichever way §2 is decided, the choice is unprovable downstream until a footing field is added.
   This is the actionable defect, and it is cheap to fix.
4. **The rest of the standard chain is purity-footed too, so the existing ten are *consistent* with
   it.** Only eleven launchers in the repo pass `--bkg-mode`, and every one is 2D-negweight, FPS, or
   PET; no `nd-unfolding/sbatch_unfold_5d*.sh` does. The central, the 169 vertical and the 18 detector
   unfolds therefore share the purity footing. ("Background-aware" in the `_bkgaware_` launcher names
   refers to per-universe background *columns* in the dump — a different axis from the measured-side
   subtraction mode.)

**Verdict.** The ten standard lateral unfolds are **purity-footed, unreceipted, and produced by a
retired launcher**. Under the recorded purity decision their *footing* is correct and only their *provenance* needs
repair — which the canonical chain can do by attestation without recomputing physics. Under (B) they
must be re-run along with the rest of the chain.

---

## 4. Execution packets

Preflight for every packet: the "Execution preflight" list in
`docs/PUBLICATION_COMPLETION_RUNBOOK.md` §"Execution preflight for every packet". In particular record
source commit, input manifests, target namespace, and the output validation command *before* launching.

### G-0 — Record the footing decision and its revisit obligation. **Do this first; it is cheap.**

The purity choice is provisional-by-design ("revisit before submission"), and a provisional decision
that is not written down becomes a silent default — which is the exact failure this whole runbook
documents. Before touching the chain:

1. Add an open item to `docs/OPEN_ITEMS.md`: *the standard 5D chain is quoted on `purity` by decision
   of 2026-08-07; revisit before submission; what would close it is a full 5D 187-universe both-mode
   comparison at 5-iter lgbm, and what stands in for it today is §2.1 of this runbook.*
2. Add the `bkg_mode` field (G-1) so the choice is machine-readable, not merely prose.
3. Do **not** write "footing proven irrelevant in 5D" anywhere. §2.1's last paragraph says exactly how
   far the evidence reaches.

### G-1 — Make the footing explicit in code, and give the standard manifest somewhere to record it

Required regardless of which footing had been chosen, because "no reliance on a default is allowed" is
a locked runbook rule and §3's finding 3 shows the standard lane currently cannot express a footing at
all. **The value to pass is `purity`**, per §2.

1. `run_p4_unfold_std.sh:43` — pass `--bkg-mode purity` explicitly. Note this is a *no-op on the
   physics* (it is already the driver default) and a change purely to provenance: after it, the footing
   is asserted by the launcher instead of inferred from a silent branch. Which means **it must not
   change any output hash** — if a re-unfold after this edit produces a different ROOT than the
   attested one, stop and find out why before proceeding.
2. `p4_evidence.py` — record the footing (at minimum `bkg_mode`, ideally the five-key estimator
   footing `fps_provenance.REQUIRED_FOOTING` uses) in `p4_standard_manifest.json`, and fail closed
   when it is absent or mismatched.
3. **Do not edit `fps_provenance.py`'s constants.** Its grid (`PT_EDGES`/`PZ_EDGES`, `N_REPORTED=266`,
   `REPORTED_MASK_FINGERPRINT`) is FPS-specific and is hash-pinned into gates that just passed. If you
   need shared logic, add a standard-side module or parameterize by profile — do not mutate the FPS
   constants. (BEN-040's lane; the FPS chain is freshly green and must stay that way.)
4. Add tests. **Build fixtures by calling the real producer**, never by hand-assembling what the
   consumer expects — that is exactly the defect BEN-040 records, in this same chain.

Gate: existing standard-lane tests green, plus a new negative test proving a missing/mismatched
footing is rejected, plus a positive test proving `purity` is accepted.

> *There is no G-2 — it was folded into G-1 when the footing decision landed. G-3…G-9 keep their
> original numbers so that cross-references elsewhere in this file stay valid.*

### G-3 — Run the canonical standard chain to `evidence`, then attest or re-unfold

The chain already exists end to end: `bash nd-unfolding/run_p4_standard.sh`, six stages —
merge+audit → evidence → unfold → **hard verifier gate** → components → validate → project. It runs
inside a compute alloc via `srun --overlap --jobid=<holder>`; do not nest `srun` inside stages.
`STOP_AFTER` defaults to `evidence`, which is a safe preflight that stops *before* covariance.

1. `STOP_AFTER=evidence bash run_p4_standard.sh` — builds hashes, receipts and the manifest.
2. Then stage 3 (`STOP_AFTER=unfold`). Because the purity decision means the existing ten are on the
   *correct* footing, `run_p4_unfold_std.sh` should **legacy-attest** them if their sha256 matches the
   committed manifest — writing the missing receipts without recomputing, nearly free. If attestation
   fails, they re-unfold: budget **~1h40m wall** for all ten at `CONC=6` (measured from the 07-18 log
   span 03:53→05:34Z), CPU only.
   - **Attestation certifies identity, not footing.** If you attest, the footing claim rests on §3's
     launcher+default+log evidence, so record that evidence in the manifest via G-1 rather than
     leaving it implicit in this file.
3. **Preserve the ten 07-18 ROOTs.** Deletions are frozen behind
   `docs/POST_PUBLICATION_REORG_PLAN.md`'s freeze tag. If they are superseded, supersede by
   namespace and keep them as labeled controls (the FPS lane's `*__SUPERSEDED_support` renaming is the
   precedent).

Gate: ten valid ROOTs, ten `.done` receipts, manifest bound, footing recorded and matching.

### G-4 — Pass the independent verifier, then build the standard lateral component

Covariance stages 4–6 refuse to run without `P4_VERIFIER_PASS=<token>` — the `standard-p4-verifier`
must PASS on the **committed** patch first. Per `CLAUDE.md`, the audit lane gets read-only tooling:
`codex exec --sandbox read-only`, or `claude -p --allowedTools "Read,Grep,Glob,Bash"`, or `agy` in a
throwaway worktree. `git status` after it finishes, and preserve the diff before reverting.

Then stages 4–6: `p4_build_components.py` (manifest-bound, named bkgaware components + the 5 active
bands) → `p4_validate_active_lateral.py` (exact-5-bands / traces / component-sum / PSD / support) →
`p4_project_4d.py` (5D→4D mask/edge hashes + central non-mutation).

Gate: validator `RESULT PASS` with zero fails; symmetry, PSD/eigen, finite diagonal, exact
component-sum reconstruction, rollup identity.

### G-5 — Adopt P4-5D

Swap the selection-complete lateral into the J28-corrected full-160 covariance
(`nd-unfolding/uq_5d/unified_throw_cov_5d_fluxfix_20260806_full160.root`, `n_throws = 160` read from
the file). The adoption packet must contain, per the runbook's P4-5D list: common central and
reported-bin mask/order, estimator/background fingerprint, component inventory, **pre/post hashes
proving no frozen component changed**, exact block-sum reconstruction, symmetry, PSD/eigen, finite
diagonal, and mean-shift records in **both** conventions (F7 requires the CV-centered variant to exist
and the shift reported either way).

Expect the total to move, and **expect it to be a redistribution, not a scale** — the FPS analogue
moved +10.96% on the lateral block with a per-bin σ ratio spanning 0.7897–1.4402 over 266 bins. Do not
apply any single factor to a published number.

Output: a committed adoption packet — product summary + ledger entry + RUN_LOG entry + STATUS
one-liner **in the same commit** as the code/launcher. An uncommitted artifact is provisional.

### G-6 — P4-4D: adopt the exact 5D→4D marginal (decided, §2)

Use `p4_project_4d.py` (stage 6 of the canonical chain) to project the G-5-adopted 5D covariance, and
label the independent 4D estimator a **cross-check** in the note. The 4D inherits the corrected 5D
lateral, so **there is no separate 4D lateral component to build.**

- Validate `M C M^T` against direct block sums, plus the stage's own 5D→4D mask/edge hashes and
  central non-mutation checks, plus symmetry, PSD, and normalization.
- **Do not rerun the corrected R1 4D throws or non-lateral components.**
  `RESULT_DEPENDENCY_AND_RERUN_MAP.md` lists them as explicitly unaffected by a lateral change.
- Keep the independent 4D product as provenance, reported as a cross-check. If the two disagree by more
  than the projection tolerance, that is a finding to report, **not** a number to reconcile by
  adjusting either one.

### G-7 — Finalize the FPS budget

The adopted `uq_universe_fps_covariance_combined_activelat.root` is *pre-uthrow*; the +9.12% is not
the final quoted budget. Apply the FPS unified-throw adoption stage on top and re-validate. **Unsized
— I found no timing evidence for this step**; measure it before committing to a window.

### G-8 — The note update (P7, this lane only)

Only from committed ledger entries. `values.tex` is written from the ledger, never from a job log.

**Macros, `docs/analysis-note/values.tex`:**

| Line | Macro | Current (superseded) | Replace with |
|---|---|---|---|
| 57 | `\gbdtFiveBlockMedian` | `13.36` | recomputed post-G-5 median frac/bin (%) — the J28 candidate read 13.61 mean-centered / 14.09 CV-centered, but **recompute after the lateral swap** |
| 58 | `\gbdtFiveAdoptTrace` | `5.81e-38` | post-G-5 adopted mean-centered `sqrt(Tr C)` (J28 candidate: `5.2600e-38`) |
| 59 | `\gbdtFiveCVTrace` | `6.24e-38` | post-G-5 CV-centered variant (J28 candidate: `5.6609e-38`) |
| 60 | `\gbdtFiveMeanShift` | `1.65e-38` | post-G-5 joint mean-shift norm (J28 candidate: `1.8787e-38`) |

**Do not write the J28 candidate values.** They are the pre-lateral numbers and will move again in
G-5; they are listed only so a reader can sanity-check the direction and magnitude of the final ones.
The J28 correction alone made the totals **~9% smaller** than what the note currently quotes — so the
note is currently overstated, and the mechanism is that correcting the understated Flux block drove
the nonlinearity inflation `g` toward 1.

**Prose:**
- `values.tex:56` — the section comment "corrected 5D GBDT candidate campaign; final active-lateral
  replacement pending" loses "candidate"/"pending".
- `sec_systematics.tex:170` — remove the hedge "until the selection-complete lateral replacement
  lands", and re-check the surrounding sentences at `:163-168` which narrate the block median, the
  adopted trace, the separately-reported mean shift, and the retained conservative CV-centered
  variant.
- **Add an explicit footing statement — this is now a positive claim, not a caveat.** The note must say
  that the standard 5D covariance is quoted on `purity` while the FPS product is on
  `negweight-refined`, and it must back that with §2.1's measurements rather than asserting
  equivalence. The defensible sentence is: *the two background treatments agree to 1.4% (SYST
  covariance ratio 0.9863) and 1.8% (STAT, matched-seed ratio 0.982) at full 2D statistics with the
  adopted lgbm estimator, consistent with the ρ1 = D − B_u identity, which makes the systematic
  covariance insensitive to the choice by construction.* `app_negweight.tex` is the home for the mode
  discussion and already carries the Phase-E writeup; the systematics section carries one sentence.
  **Do not write that footing is proven irrelevant in 5D** — §2.1's last paragraph bounds what the
  evidence supports, and the 5D leg of it is a two-universe spot check at 1 iter/`hist`.

**Build and check:** `docs/analysis-note/build_all.sh` builds all three targets (note, primer,
paper); run the link/reference/provenance checks. The Overleaf subtree sync is a separate action and
**only on Joseph's say-so**.

### G-9 — Bookkeeping that makes the work exist

- `VALIDATION_LEDGER.md` — adoption entries with full receipt chains.
- `docs/OPEN_ITEMS.md` + the STATUS files — state, one line each.
- `nd-unfolding/ND_OMNIFOLD_RUN_LOG.md` — chronology, append-only.
- `docs/orchestration/CLAIMS.md` — `CLM-006` is this lane; promotion needs a recoverable artifact plus
  an independent check. Worker agreement is not verification.
- **The 2026-07-12 quarantine.** State precisely which of its named causes each adoption discharges.
  It lists seven; the lateral discharges one. Do not write "quarantine lifted" unless every listed
  cause is addressed for the product in question — and the 4D/FPS replacements and the
  covariance-dependent generator significances are explicitly still inside it.

---

## 5. Traps specific to this lane

- **A number's existence on disk is not a footing claim, and not a receipt.** This runbook exists
  because ten ROOTs sat in a publication namespace for three weeks, purity-footed, unreceipted, from a
  retired launcher (BEN-036, BEN-041).
- **`P4_VERIFIER_PASS` is a speed bump, not a lock — do not set it yourself.**
  `run_p4_standard.sh:41` tests only `[[ -z "${P4_VERIFIER_PASS}" ]]`, so *any* non-empty string opens
  stages 4–6; nothing binds the value to a `standard-p4-verifier` PASS, a receipt, or a patch hash. The
  gate's own refusal message names the variable, which is precisely the shape that invites an agent
  under "finish the task" pressure to self-authorize. Treat it as a **human/independent checkpoint**:
  run the verifier read-only per `CLAUDE.md`, report the verdict, and let Joseph authorize. Same family
  as BEN-040 — a gate whose PASS condition cannot distinguish success from a caller asserting success.
- **The chain stops at CANDIDATE by design.** Its final line says so
  (`CANDIDATE only; adoption is a separate authorized step`). Adoption (G-5), the 4D marginal
  adoption (G-6), `values.tex` (G-8) and any Overleaf sync are **publication decisions**: the ledger
  states that replacing published macros "is a publication decision, not a bookkeeping one", and the
  negweight state doc holds the Overleaf push for explicit user OK. Do not cross that line unattended,
  and never write "quarantine lifted" on your own judgment.
- **Never apply +10.96% or +9.12% as a uniform scale.** Per-bin σ ratio 0.79–1.44.
- **Do not rerun the corrected R1 4D throws or the non-lateral 5D components** to repair
  documentation. `RESULT_DEPENDENCY_AND_RERUN_MAP.md`'s last trigger row is explicit: a missing
  summary is repaired by a provenance commit, not by rerunning physics.
- **Never raise a tolerance or hand-edit a hash to clear a mismatch.**
- **`fps_provenance.py` constants are hash-pinned into freshly-green gates.** Add, do not mutate.
- **Do not pipe a diagnostic run through `tail`/`head`** — redirect the whole stream, filter reads
  (BEN-026, and BEN-035 extends it to test suites and to `rc=$?` after a pipeline).
- **Every ID, rank, count and queue name comes from a command run in the same turn** (BEN-027).
- **A quiet log does not mean a dead job** — 4 MiB block buffering on this Lustre filesystem. Judge
  liveness by `sstat` CPU time and produced artifacts. Use `python3 -u` (BEN-028).
- **Never infer service state from one client command** — probe with `scontrol ping`/`sinfo`/a
  single-job `squeue` (BEN-035, four instances).
- **Audit/verifier lanes get read-only tooling**, and `git status` after any delegate finishes.
- **Scratch is purgeable.** Nine throw slabs were already lost once from
  `uq_5d/uthrow_slabs_5d_sb/`, making the adopted covariance a 76.2% subsample until `56427580`
  regenerated them. Copy anything irreplaceable off scratch (CFS) as you produce it.

---

## 6. Definition of done

The GBDT lane is closed when all of:

1. A committed **P4-5D adoption packet** exists on the selection-complete lateral, with pre/post
   hashes proving no frozen component moved.
2. The **exact 5D→4D marginal** is adopted and validated, and the independent 4D is explicitly labeled
   a cross-check.
3. The **final FPS budget** is adopted post-unified-throw.
4. `values.tex` and the systematics prose quote only post-adoption numbers, all three note targets
   build, and the footing is stated explicitly **with §2.1's numbers**.
5. Every quoted number traces to a `VALIDATION_LEDGER.md` entry whose artifacts are reachable from a
   commit.
6. The quarantine paragraph names exactly which causes remain open, per product.
7. The **footing revisit obligation** (G-0) is an open item in `docs/OPEN_ITEMS.md`, stating what would
   close it. The lane is *closed*; that question is *deferred*, and the difference has to be legible.

What is **not** required for this lane and must not be waited on: anything in P5A/P5B/PET, and the
`combine_cstat_bkgsub_100rep.py` tracking question (that is a PET-lane item).

---

## 7. Open questions

1. ~~§2's footing scope.~~ **DECIDED 2026-08-07: purity, revisit before submission** (§2). The revisit
   is tracked as G-0; what would close it is a full 5D 187-universe both-mode comparison at 5-iter lgbm.
2. ~~P4-4D route.~~ **DECIDED 2026-08-07: exact 5D→4D marginal, independent 4D a cross-check** (§2).
3. **G-7's cost — still open.** No timing evidence found for the FPS unified-throw adoption stage.
   Measure before committing to a window.
4. ~~Whether the standard 5D reported-bin mask has a pinned fingerprint.~~ **Resolved while writing
   this file, and the answer is a caveat rather than a blocker.** The mechanism exists —
   `p4_lib.mask_order_hash(mask)` hashes the reported-bin mask plus C-order over
   `GRID_NBINS = 65856` (14·16·7·7·6), and fails closed on a size mismatch or an empty mask. But it is
   a *computed* hash with **no pinned canonical target**, unlike FPS's
   `REPORTED_MASK_FINGERPRINT`/`N_REPORTED=266`, which are recomputed and compared against a locked
   string. So G-5 can prove all components share **one** mask/order, which is what stops a silent mask
   mix — but it cannot prove that mask is the externally-declared publication mask. Note also that
   `p4_validate_active_lateral.py` itself contains no mask handling; the check lives in `p4_lib.py`
   and must be invoked. **If the note quotes a reported-bin count, pin the target constant first.**
