# UQ Remediation — Meta-prompts

Two hand-off prompts for external verification of the uncommitted UQ
remediation. Both are READ-ONLY and share the operating rules below. UNCOMMITTED
working-tree artifact.

## Shared operating rules (paste into either prompt)
```
- Repo: /pscratch/sd/j/josephrb/MINERvA-OmniFold. HEAD 3e85589. Read AGENTS.md first.
- READ-ONLY. Do NOT edit, commit, push, or delete anything. Do NOT launch event
  loops, SLURM arrays, or PET ensembles. Do NOT scancel or end any SLURM job.
  Preserve every dirty/untracked file (concurrent work from another account).
- A shared allocation (job 55798579, node nid004282) is live; run bounded checks
  through:  ./alloc_run.sh '<cmd>'
- For PyROOT, setup_salloc_env.sh resolves $HOME wrong for this account; activate
  ROOT directly:
    eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)" \
      && conda activate /global/homes/j/josephrb/.conda/envs/root_6_28
- Put temp scripts under /pscratch/sd/j/josephrb/tmp_claude_school/ (shared FS;
  the login-node /tmp is NOT visible on the compute node).
- You may run  python3 -m unittest discover -s nd-unfolding/tests -q  and write
  small throwaway probes, but mutate no repo state and run no heavy jobs.
```

---

## Prompt A — Blind audit (does NOT reveal candidate defects)
```
You are an independent correctness reviewer. A single uncommitted diff in this
repository implements a batch of uncertainty-quantification changes for a
MINERvA OmniFold cross-section analysis. Find correctness defects in that diff:
logic errors, silent failure modes, state-management bugs, off-by-one / dedupe
errors, RNG or seeding mistakes, incorrect merge/aggregation behavior, and
validation that does not actually validate. Report what is wrong; do not assume
anything is correct because it "looks done" or is commented as done.

[Shared operating rules]

Scope — review the uncommitted changes to (get the exact diff with `git diff`
and `git status --short`):
  MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp
  nd-unfolding/uq_math.py
  nd-unfolding/unified_throw_cov.py
  nd-unfolding/replica_manifest.py
  nd-unfolding/pet_bootstrap.py
  nd-unfolding/pet/extract_bootstrap_replica.py
  nd-unfolding/pet/minerva_pet_dataloader.py
  nd-unfolding/pet/sbatch_pet_bootstrap_replica.sh
  unbinned_unfolding/python/omnifold.py
  nd-unfolding/tests/*
The MNV101_DUMP_POINTCLOUD background-cloud hunk in the C++ diff is separate
user-owned work — out of scope.

Deliverable: a ranked list (most-severe first) of confirmed or plausible
defects. For each: file+line, one-sentence defect, and a concrete failure
scenario (inputs/state -> wrong output). If an area is clean, say so briefly.
Do not propose fixes unless a defect is confirmed.
```

---

## Prompt B — Adversarial "disprove each fix" (reveals the fixes)
```
You are an adversarial verification agent. Below are specific fixes/claims from
an uncommitted UQ remediation. For EACH claim, actively try to DISPROVE it:
construct an input, edge case, or code path where it fails; otherwise show via
the actual code/tests that it holds. Default to skepticism — a claim is HOLDS
only after you tried and failed to break it. Do not treat the claim's wording as
evidence.

[Shared operating rules]

Claims to disprove (cite file:line; give a concrete counterexample if broken):

C++ active-universe mode (MINERvA101/.../runEventLoopOmniFold.cpp):
 1. The truth-denom migration census restores truthCV + evt + model state so
    the truth-denom fill is unchanged vs. non-active mode.
 2. The reco census restores recoCV + evt; and moving
    `if(!isSignalTruth) continue;` below the reco block does not change which
    rows are written to mc_signal_reco or their branch values.
 3. CVUniverse::SetTruth is re-established each iteration; no census leaves the
    static truth/reco flag wrong for the next event or the next loop.
 4. Invariant metadata (hasActiveUniverse / activeUniverseIndex /
    activeUniverseIsLateral) uses TParameter merge mode 'f' (keep-first) under
    hadd; migration counters are additive. Node-local evidence on nid004282:
    /tmp/mnv101_active_pc_final{,_hadd}.root.
 5. MNV101_ACTIVE_UNIVERSE rejects malformed spec, unknown/unmatched band,
    out-of-range index, null universe, reco/truth IsVerticalOnly mismatch, and
    combination with MNV101_SKIP_SYST — before any event loop.
 6. Background selection/kinematics/weights use the active universe; data stays
    data-CV.

PET bootstrap replica chain:
 7. The MC Poisson draw used in training (minerva_pet_dataloader.build_loaders /
    _build_pointcloud_memmap) and the mc_bootstrap_factor saved for extraction
    are the SAME coherent per-event draw — same default_rng(seed+10_000_000)
    .poisson(1.0,N), same full N — for both the memmap and non-memmap paths.
 8. --reweight-all makes mc_indices == arange(N) (ordered, full) and evaluates
    w_push over all N events regardless of the --max-events training subsample.
 9. validate_full_replica_weights rejects: missing keys, seed mismatch,
    partial/unordered coverage, non-finite, and a factor inconsistent with the
    canonical seed draw. Try to slip an invalid file past it.
10. The replica launcher trains at the SAME config (niter/epochs/max-events) as
    the nominal fullcloud train.

unified_throw_cov + uq_math:
11. The combine path requires --expected-throws and fails on any throw-id
    mismatch, missing knob endpoint, non-contiguous/mismatched flux bank,
    non-finite value, or duplicate slab.
12. --null (fixed-seed CV repeat) yields identically zero — no OmniFold jitter
    is subtracted anywhere.
13. interpolate_asymmetric_ratio has correct endpoints (+1->plus, 0->ones,
    -1->minus) and geometric interior; invalid (non-positive/NaN) ratios raise.
    mat_covariance is the mean-centred 1/N pair form.
14. finite_observable_mask excludes exactly the same rows from signal and
    truth-denominator (closure); total_xsec integrates density x bin-volume
    (not a bare sum).

For each claim output:  CLAIM N — {HOLDS | BROKEN | UNCERTAIN} — evidence
(file:line + what you did) — if BROKEN, the exact failing input/scenario.
Finish with a short list of BROKEN/UNCERTAIN items ranked by severity.
```
