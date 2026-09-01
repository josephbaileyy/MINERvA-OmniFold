# FINDING 2026-09-01 — what the `7ac0edec` → `main` redeploy changes for the other eight k=0 arms, and the ninth's submit recipe

**CITABLE FOR:** the per-launcher precondition delta in §2, the corrected refusal-time claim in §3,
the resolved environment values in §4, and the residual `UNKNOWN`s in §5.

**NOT CITABLE FOR:** authorization to submit anything; a Gate-1 or Gate-2 clause; a readiness or
fitness finding; leg 6; any `M(ii)` leg; adoption; or discharge of any quarantine cause. **Gate 2
remains FAIL.** CAND `1 of 7`, QUOTED `0 of 7`. This document measures preconditions; it satisfies
none of them.

**Why it exists.** `DECISION-20260901-joseph-authorizes-k0r2-redeploy.md` §2 carries Joseph's
instruction *"and reconcile the other issues"*, and §4 of that record makes the precondition delta
something to be **measured and recorded, not discovered by a later lane at its own submit time.**
This is that measurement.

## 1. Provenance of the measurement, including a lane that could not finish

Q1 and Q2 were measured by the **`gemini` (Antigravity)** lane, read-only, and independently
spot-checked here against the launcher bytes at `050dbb72`. An earlier `codex-school` dispatch
reached the same conclusions on the adjacent questions and **ran out of account credits at the point
of writing its report**; its surviving measurements are cited in §6 and are marked as such, because a
number recovered from a delegate's log is weaker evidence than one re-measured, and the difference
should be visible rather than smoothed over.

## 2. THE DELTA — all eight launchers gain one fail-closed requirement

Commit `865b42d7` (`[oi179] Defect 3 ENFORCED`) landed **after** `7ac0edec` and added a
byte-identical block to all eight. The claim *"the redeploy changes preconditions for the other eight
arms"* is **CORRECT**.

The new variable is **`MNV_ENV_PROVENANCE`**. It is required by all eight, and it refuses both when
**unset** and when **set-but-empty** — the `:?` form, not `?`:

```bash
ENVPROV="${CODE_ROOT}/nd-unfolding/mnv_env_provenance.py"
ENVPROV_RECORD="${MNV_ENV_PROVENANCE:?set MNV_ENV_PROVENANCE to the submission-environment baseline
written by mnv_env_provenance.py --emit BEFORE the first sbatch. It has no default: OI-179 round 1
recorded no environment at all, and a defaulted path would let this run emit its own baseline and
then agree with it.}"
```

**The artifact it names must exist before the first `sbatch`.** Produced by
`nd-unfolding/mnv_env_provenance.py --emit`; read on the compute node by the same tool's
`--check-inherited`; its path is supplied entirely by the operator, with **no default by design** —
a defaulted path would let a run emit its own baseline and then agree with it, which is `OI-179`
defect 2's shape one level up.

| launcher (`050dbb72`) | `ENVPROV_RECORD` | `--check-inherited` call |
|---|---:|---:|
| `sbatch_bootstrap_5d_gpu.sh` | 164 | 234 |
| `sbatch_finalize_5d_bkgaware_gpu.sh` | 273 | 346 |
| `sbatch_seedscan_split_5d.sh` | 151 | 221 |
| `sbatch_sweep_bank_5d_run_bkgaware_gpu.sh` | 160 | 230 |
| `sbatch_unfold_5d_detector_bkgaware_gpu.sh` | 174 | 244 |
| `sbatch_uthrow_block_5d.sh` | 155 | 225 |
| `sbatch_uthrow_combine_5d_fast.sh` | 171 | 241 |
| `sbatch_uthrow_run_5d_fast.sh` | 161 | 231 |

**Note that `sbatch_finalize_5d_bkgaware_gpu.sh` is in this set.** That is leg 6, which is not
authorized and is not being submitted — but its preconditions move with the redeploy just the same,
and a lane that later picks leg 6 up will meet the new requirement whether or not it read this record.

## 3. A CORRECTION: the refusal is at EXECUTION time, not submit time

**This lane previously reported that the redeploy makes the other eight arms refuse at submit time.
That was wrong, and the error understates the hazard rather than overstating it.**

`sbatch` parses `#SBATCH` directives and does **not** evaluate the body's shell. Every line quoted in
§2 lives in the batch body, which runs on the **compute node**. So a launcher that submitted cleanly
at `7ac0edec` still **submits cleanly** at `050dbb72` with `MNV_ENV_PROVENANCE` unset — and then
**every task in the array dies on the node**, after queueing, on the `:?` expansion or on a non-zero
`--check-inherited`. Verified here against the script bytes: `#SBATCH` block at `:1-7`, the
requirement at `:174`.

**Why the distinction is worth a paragraph.** A submit-time refusal is free and immediate. An
execution-time refusal costs queue time and scheduler slots, and is discovered only when the array
starts. **This is `OI-179` round 1's exact shape** — six tasks failing in 8–15 seconds — and it is
what the enforcement was built to make loud rather than silent.

The corollary for the operator: `#SBATCH --export=ALL` means the variable must be exported **in the
submitting shell**, and the baseline must exist **before** the first `sbatch`, even though nothing
checks either at that moment.

### THE RESIDUAL GAP, stated so "ENFORCED" does not read as "enforced at submit time"

**No submit-time gate exists, and the enforcing lane agrees.** What `865b42d7` bought is real and
should not be undersold: it converts a *silent* wrong-environment run into a *loud* early death. But
it cannot move the refusal earlier than the node, because there is no preflight in the submitting
shell to move it to. `RECORD-20260901-oi179-defect3-enforced.md` discharges `OI-179` on the strength
of the node-side check; **this paragraph is the part that discharge does not cover.**

Anyone reading *"defect 3 is enforced"* and inferring that a mis-set submission environment will be
caught before jobs queue is reading more than the enforcement says. Confirmed with
`minerva-omnifold-38`, the lane that shipped it: *"it cannot move the refusal earlier than the node.
Anyone wanting a submit-time gate needs a preflight at the submitting shell, and none exists."*

## 4. THE NINTH LAUNCHER — resolved values, taken from a run that actually completed

`nd-unfolding/sbatch_mii_estimator_scan_5d_bkgaware_gpu.sh` requires **fourteen** files and reads
**nine** `MNV_*` variables plus four Slurm-supplied ones. The `gemini` lane correctly declined to
guess eight of the nine values and marked them `UNKNOWN — needs ruling`; that was the right refusal,
and the values are recoverable from better evidence than a guess.

**The source is `…/runs/k0-7ac0edec-20260830T000215Z/submission-environment-round2.txt`, recorded
`2026-08-30T20:47:32Z` on `login23` before the first `sbatch` of the run that then completed 374/374
with zero failures.** These are not proposed values; they are the values under which the arms ran.

| variable | value | carries over? |
|---|---|---|
| `MNV_CODE_ROOT` | `/pscratch/sd/j/josephrb/k0r2/clean` | yes — the path, though its **sha** moves |
| `MNV_DATA_ROOT` | `/pscratch/sd/j/josephrb/MINERvA-OmniFold` | yes |
| `MNV_ENV_ROOT` | `/pscratch/sd/j/josephrb/k0env` | yes |
| `MNV_CONDA_PREFIX` | `/global/u2/j/josephrb/.conda/envs/root_6_28` | yes |
| `MNV_ENV_SYSTEM_PREFIXES` | the **widened eleven-entry** list | yes — see below |
| `MNV_LAUNCHER_DIR` | `${MNV_CODE_ROOT}/nd-unfolding` | yes, derived |
| `MNV_GUARD_INVENTORY_DIR` | `…/runs/<RUN_ID>/inv` | **NO — run-scoped** |
| `MNV_SOURCE_MANIFEST` | `…/runs/<RUN_ID>/source-manifest.json` | **NO — run-scoped** |
| `MNV_ENV_PROVENANCE` | — | **NO — did not exist for round 2; see §5** |

**`MNV_ENV_SYSTEM_PREFIXES` is the one variable whose value is load-bearing and non-obvious.**
`RECORD-20260901-…` §1 records it as *"the only change between the two rounds"* — round 1 died,
round 2 completed, and nothing else moved. `RECORD-20260830-k0r2-round2-submission.md` §4 records that
the **two**-entry line documented at `PACKET-20260823:122` returns **rc 3** with a `VIOLATION` on
`$HOME/bin`, and that the packet *"is still uncorrected — `OI-179` defect 1, Joseph's call"*. The
in-job proof is `[env-pathcheck] OK: 46 search-path entr(ies) checked`; the proposal's 37 was measured
with the guard unactivated.

### THE TRAP, confirmed against the bytes

`:154-157` of the ninth launcher:

```bash
if [[ -n "${MNV_EST_SEED_OFFSET:-}" ]]; then
  echo "[mii-seed] FAIL: MNV_EST_SEED_OFFSET must be unset for the estimator-seed scan" >&2
  exit 2
fi
```

> **The round-2 environment file contains `MNV_EST_SEED_OFFSET=0`.** It is the ninth line of the very
> file §4 recommends as the source of the other values. **Copying that recipe verbatim kills this
> launcher at `:154-157`** — and it fails at *execution* time per §3, so the array queues first. The
> recipe must `unset` it, never export it, not even to `0`.

## 5. WHAT REMAINS GENUINELY UNKNOWN, and it is not a lookup

Three values cannot be taken from round 2 because they are properties of a run that does not exist yet:

1. **`RUN_ID`** — and therefore `MNV_GUARD_INVENTORY_DIR` and `MNV_SOURCE_MANIFEST`, both run-scoped.
2. **`MNV_ENV_PROVENANCE`** — round 2 satisfied `OI-179` defect 3 with a hand-written 16-line text
   file, **not** with `mnv_env_provenance.py --emit`, which did not yet exist. So there is no
   precedent baseline to point at: one must be emitted, and the emitting is itself a step no record
   currently describes for a ninth arm.
3. **Whether a ninth arm may share a `RUN_ID` with the completed round-2 run at all**, or must open its
   own. Sharing would write new inventory into a directory whose contents are part of a filed
   measurement; opening a new one changes what `F-4(b)`'s population glob sees. **NOT MEASURED**, and
   it is a ruling rather than a lookup.

## 6. Carried from the credit-exhausted lane, marked as second-hand

Recovered from the `codex-school` session log rather than re-measured here. **Re-measure before
citing any of these in a filing:**

- the advance moves the A-2(f) source manifest from **820 to 833** tracked `.py`/`.sh` files, and its
  `listing_sha256` with it;
- `docs/orchestration/MANIFEST.tsv` moves **611 → 664** lines;
- the preflight census `guarded` count **stays 14**; declared exclusions **16 → 24**; the derived
  boundary **30 → 38**. **This lane's earlier worry that the new launcher would move the pinned
  guarded count 14 → 18 does not materialise.**

## 7. What this finding does NOT do

It authorizes no submission and moves no gate. It does not emit the baseline, choose a `RUN_ID`, or
settle §5's third question. It does not redeploy anything: at the time of writing the deploy tree is
still detached at `7ac0edec`, porcelain 0, under a **live** freeze whose expiry condition is the
round-2 `F-1(b)` producer filing.
