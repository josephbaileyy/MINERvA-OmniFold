# Brief: methodological + code audit PLANNER (fresh session, no cluster access)

Written 2026-07-28 for a cold session with no prior campaign context. Read this
whole file before reading code. You are auditing, not fixing.

## What this project is

MINERvA Medium-Energy FHC ν_μ CC-inclusive **double-differential cross section**
in muon (pT, p‖), extracted with **OmniFold** — unbinned iterative Bayesian
unfolding. The estimator under audit is **PET / OmniLearn** (a point-edge
transformer), driven through the vendored `omnifold_nn` package (`MultiFold`,
`DataLoader`).

Two representations exist and **must not be conflated**:

- **recoil-only (`xps2`)** — a cross-check/insurance path. Barred by
  `docs/OPEN_ITEMS.md` from being promoted or extended as a full-event product.
  See KNOWN_ISSUES #19.
- **full-event** — the publication path. Gated by a `g2-fullevent-v1` schema
  marker; `build_fullevent_loaders` fail-closes on anything else.

## Status in one line

**Gate-4 is `PASS_CODE_ONLY`, P5A has never launched, and no cross section has
been extracted.** Nothing is committed to a physics result yet. That is why an
audit now is cheap and an audit later is not.

## HARD CONSTRAINTS — read twice

**1. Gate receipts freeze code by sha256. Editing a frozen file voids the
evidence that its gate passed.**

`docs/orchestration/verify_hash_bindings.py` is the arbiter. Run it before and
after anything sweeping:

```bash
python3 docs/orchestration/verify_hash_bindings.py     # expect: ALL BINDINGS INTACT
```

On 2026-07-28 a well-intentioned repo-root de-rooting refactor (commit `2732304`)
voided **six** bindings at once — both Gate-4 entry points, the Gate-3 launcher
test, and the Gate-2 canonical-runtime dataloader — **while the entire test suite
stayed green**, because the edits were behaviourally inert on Perlmutter. Reverted
at `5a22e1c`. Do not recreate this.

**2. Some hardcoded `/pscratch/sd/j/josephrb/MINERvA-OmniFold` literals are
load-bearing, not tech debt.** Confirmed examples:
`nd-unfolding/pet/fullevent_fps_dataloader.py:611`,
`nd-unfolding/fps_verify_merged_receipt.py:22`. "De-root the hardcoded paths" is
a wrong recommendation here. If you think one should change, say which receipt
must be re-issued and which gate must be re-run.

**3. Your deliverable is FINDINGS, NOT EDITS.** Do not modify code, receipts, or
`RUNS.tsv`. Never hand-edit a recorded sha256 to make a check pass.

**4. You have no cluster access.** No Perlmutter (in maintenance until
2026-08-03 22:00 PT), no NCSA Delta, no Globus, no 2FA. The only full-event input
in existence (`G2_FPS_MEFHC_P12.npz`, 9.9 GB) is on Perlmutter scratch and is
unreachable. So "run X to check" cannot be your primary answer — audit what is
readable, and where a check is genuinely required, specify it precisely enough
that someone with access can run it unattended.

## Do not mistake gate names for evidence strength

This is the most valuable thing you can be skeptical about. Known-weak evidence,
already self-reported in `nd-unfolding/ND_OMNIFOLD_RUN_LOG.md`:

- **The P5A closure receipt is DEAD.** `closure_fullevent_fps.py` passed at
  `36ab84d` against the *pre-schema-gate* dataloader; the `g2-fullevent-v1` gate
  landed the next day and rejects the input that PASS was obtained with. It
  certifies nothing about current code.
- **The 2026-07-26 synthetic-fixture closure has, by its own log entry, "close to
  zero power to detect a real estimator defect"** — random features, and the
  pseudo-data *is* the MC, so push ≈ 1 regardless of correctness.
- **The Gate-2 spatial check is described in the same entry as "degenerate."**
- **The GPU-nondeterminism floor** (`pet_weights_fps_xps2_delta_s101_floor.json`)
  is recoil-only and explicitly `is_publication_result=False`,
  `is_covariance_component=False`. It is not a systematic.
- **A units question in the Gate-2 path is still open.**
  `gate2_target_runtime.py:421-422` divides muon scalars by 1000.0. If the dump is
  already in GeV, both compared histograms are misscaled *identically*, the domain
  guard at `:432-435` passes, and the gate passes while being wrong.

Treat "test suite passes" as near-zero evidence on its own: **7 of the current 7
failures are platform artifacts, and the suite stayed green through six voided
gate bindings.** Audit test *power*, not pass rate. Ask of each test: what
mutation would it actually catch?

## Two open findings you should extend rather than rediscover

Both surfaced incidentally on 2026-07-28 while costing a rehearsal, which is weak
evidence the code has not been read at this depth:

1. **Fixture/real shape mismatch.** `make_synthetic_g2_fullevent.py:189` defaults
   `--tokens 40`; the real dump's `part_gen`/`part_reco` carry **12** slots. Every
   cost or shape number from the synthetic run is ~3.3× too wide per event.
2. **Projected host-RAM exhaustion.** `fullevent_fps_dataloader.py:520-521` does
   `np.asarray(d["part_gen"])[imc]` — materializing the full 49.15M-row array
   *before* subsampling — and `build_truth_cloud` then stacks to (n,12,8) through
   several full-size temporaries. `rank`/`size` only reach `DataLoader` at
   `:612`, **after** the clouds are built, so all 4 MPI ranks build full copies.
   Estimated construction peak ~78 GiB/rank → **~310 GiB against a 251.6 GiB
   node**. Verify or refute this; if real, the fix is a code change (shard before
   build / chunked construction / a full-event memmap builder that does not exist).

## Where the truth lives

| Class | Files |
|---|---|
| Control-plane entrypoint (generated, do not edit) | `docs/orchestration/LIVE-STATE.md` |
| Canonical science | `docs/PUBLICATION_COMPLETION_RUNBOOK.md`, `nd-unfolding/PET_UQ_REMEDIATION_STATUS.md`, `VALIDATION_LEDGER.md` |
| Append-only history (never rewrite) | `nd-unfolding/ND_OMNIFOLD_RUN_LOG.md`, `docs/orchestration/RUNS.tsv` |
| Constraints / open work | `KNOWN_ISSUES.md`, `docs/OPEN_ITEMS.md` |
| Restore sequence + verified test baseline | `docs/orchestration/RESTORE-2026-08-03.md` |
| Porting / control plane | `docs/orchestration/PORTING.md` |

`docs/orchestration/RESTORE-2026-08-03.md` is the fastest orientation to what is
blocked and why; read it early.

## Audit dimensions

Cover these as separable lines of attack. For each finding give: file:line, the
concrete failure scenario (inputs/state → wrong output), severity, and whether it
is frozen-file-constrained.

**Methodological**
1. Unfolding procedure — iteration count, convergence criteria, whether stopping
   is principled or inherited; prior dependence.
2. Negative-weight handling and the **Stay-Positive** refinement
   (`u2d.refine_stay_positive`, arXiv:2505.03724) — correctness, and what
   `refinement_is_learned_production=False` would silently permit.
3. Closure design **power**, not just pass/fail. What defect would each closure
   actually detect? Which are purity controls in disguise?
4. Covariance construction — double-counting between throws/replicas/block units,
   and whether the recoil-only floor could leak into a full-event covariance.
5. Binning, the canonical FPS grid, and the **266/285 reported mask** — edge
   conventions, ravel order, and the sparse-bin behaviour (worst per-bin
   nondeterminism sat in cells with n=2 and n=11 events).
6. Truth/reco leakage — `assert_no_truth_leakage` and the CLM-007 data-scalar
   guard: are they reachable on every path, or bypassable?

**Code / engineering**
7. Loader contract and resource behaviour (see finding 2 above).
8. Fail-closed guards — are they genuinely unreachable-past, or can a caller
   route around them? The `g2-fullevent-v1` gate and the `bkg_mode` split
   (`negweight-refined` nominal vs `purity` control) are the critical two.
9. Receipt/gate provenance integrity — do receipts bind what they claim; is any
   PASS verdict resting on superseded code (the dead P5A closure is one; look for
   others).
10. Test-suite power, per above.
11. Perlmutter/Delta portability seams — which literals are load-bearing, which
    are accidental, and what a legitimate fix would cost in gate re-runs.

## Output format

A prioritized findings list, most severe first. For each: claim, evidence
(file:line), concrete failure scenario, confidence, and the minimal check that
would confirm or refute it. Separate **"blocks the publication nominal"** from
**"should fix eventually."** Explicitly list what you could not assess without
cluster access, so it is not mistaken for a clean bill of health.
