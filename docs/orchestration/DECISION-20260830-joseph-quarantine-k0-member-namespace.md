# DECISION 2026-08-30 — Joseph: quarantine the `aa67c426` products out of the k=0 member namespace

**CITABLE FOR:** the authorized disposition of the exact file set named below.
**NOT CITABLE FOR** any other file set, any future member, deletion of anything, a gate movement, or
adoption. Gate 2 remains **FAIL**; no scalar-5D covariance is adopted.

## Authority

The rehearsal producer withheld the seven-arm submission (`d3742e93`, `OI-176`,
`FINDING-20260830-k0-member-namespace-blocks-submission.md`) and put two routes to Joseph:
quarantine the namespace on the 2026-08-23 pattern, or rule resume-adoption acceptable and amend
§7's run-bound / cross-run / mixed-pin clauses. His words:

> *"do option 1"*

**The scope wording below is this lane's drafting, ratified by him.** He did not type it into the
repository. It is a **per-instance** authorization naming an exact file set, in the same shape as the
2026-08-22 and 2026-08-23 dispositions of this same namespace — **not** a standing rule and **not** a
precedent that pre-approves the next one.

## Why it is needed

`mii/member_k000000` still holds the **failed `aa67c426` rehearsal's complete products**. Measured
2026-08-30: **517 files, 7 directories, 2,733,149,261 bytes (2.6 GB)** — 189 `.root`, 185 `.npz`,
143 `.done` — under `boot_nd_5d/`, `seedscan_split_5d/` and `uq_5d/`, carrying **143 distinct Slurm
job ids** from that rehearsal (`57527866` … `57587242`).

Every marker records `"note":"est_seed_offset=0"`, which is exactly what this k=0 anchor declares, so
`mr_skip_if_complete` does **not** fail on them — **it adopts them**. Guard coverage is not uniform:
`sbatch_bootstrap_5d_gpu.sh` (1 call), `sbatch_seedscan_split_5d.sh` (1) and
`sbatch_unfold_5d_detector_bkgaware_gpu.sh` (2) call it; the uthrow and combine arms do not. So a
submission against this namespace would either **skip 143 tasks and emit new-pin inventories over
products built under the failed candidate** — cross-run and mixed-pin, both §7 abort conditions and
precisely §8's *"backfill rather than a new forward-only rehearsal"* — or **overwrite a Gate-2-FAIL
rehearsal's evidence in place**.

**No gate measures this.** `M-4` and F-17 compare the two *checkouts*; all eighteen Gate-1 clauses
are code-root integrity clauses. The data root was nobody's subject, and the proposal never raises it
(`quarantin|resume|skip|existing product` returns zero matches in it).

## THE AUTHORIZED ACTION

> **MOVE — never delete — the entire contents of
> `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/mii/member_k000000` to a dated quarantine
> directory outside the member namespace**, preserving relative structure, so the k=0 anchor submits
> against an empty namespace.

- **MOVE, NOT DELETE.** This file class has twice been ruled to be moved and never destroyed. The
  quarantine is the evidence of the failed rehearsal and must remain readable and digest-checkable.
- Destination must be **outside** `nd-unfolding/mii/`, so `mr_prefix` — which can only emit
  `mii/member_k<offset>/…` — cannot see it. Same filesystem, so this is a rename: no copy, no space
  cost, no quota movement.
- **File and byte counts must be verified equal before and after**, and the move recorded with the
  destination path, the counts, and the 143 job ids.

## The operand is NOT disturbed by this, and that was checked before authorizing

`nd-unfolding/mii` is **untracked and not ignored**, and `git status --porcelain` collapses it to a
**single line**, `?? nd-unfolding/mii/`. Because `member_k001200` (312 K) and `member_k002400`
(296 K) remain, `mii/` stays non-empty, the single line persists, and **canonical porcelain stays
726** — matching the committed recapture operand and the status digest `d429f0f3…`.

**This must be verified, not assumed.** Re-measure porcelain and the status digest after the move and
immediately before `sbatch`. **If either has changed, STOP and do not submit** — that is the
condition `F-17(a)` tests and the one that blocked Gate 1 round 1.

## What this does NOT authorize

- **No deletion of anything**, including the quarantined set and the 41.44 GB combined intermediate,
  whose deletion §11g gates on `MVFINAL_j`.
- **No disposition of `member_k001200` or `member_k002400`.** They are outside this authorization and
  must not be moved — moving them would empty `mii/` and break the operand.
- **No leg 6, no other member, no family work.** Those remain gated behind Gate 2 and
  `DECISION-20260830-joseph-mii-family-and-leg6.md`.
- **No gate movement, no adoption, no Gate-2 evidence.** Gate 2 stays FAIL until the run-bound
  evidence is filed and independently graded.
- **No reuse of the quarantined products** in this or any later member. The 2026-08-23 disposition's
  `not_authorized` list already names *"reusing these products in the eventual accepted member"*, and
  that prohibition is carried forward here unchanged.
