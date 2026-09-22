# OUTCOME 2026-09-22 — the ten adopted endpoint receipts are SUPERSEDED BY CODE DRIFT, not re-pinned

**CITABLE FOR:** the measured divergence between the ten adopted endpoint receipts and the current
tree, and the disposition taken.
**NOT CITABLE FOR:** any claim that the adopted covariance is invalid, any claim that it is
re-validated, or any grade. **Nothing here moves `3d7465f6…`.**

| | |
|---|---|
| measured at | `origin/main = 384c2eb1`; deployed checkout `32e403b8` (read-only) |
| receipts | `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/active_universe_5d/standard/unfolds/*.root.done` |
| disposition | **SUPERSEDED-BY-CODE-DRIFT** for all ten; the fail-closed guard stays CLOSED |
| authorization | `HANDOFF-20260922` §12 item 2, worked under decision **D2** |

## 1. ⚠ THE TEN RECEIPTS ARE NOT TEN DIVERGENCES. THEY ARE ONE, INSTANTIATED TEN TIMES.

D2 asked for the pinned blob, the current blob and the moving commit **for each of the ten**. Read
from the receipts themselves, all ten are **byte-identical in every provenance field**:

| field | value — identical across all ten |
|---|---|
| `unfold_blob` | `dc74c38f8ec7b5f6723fa231630e9fc43e7a93f0` |
| `code_rev` | `42268b6dfa2e60a0e4bd491b11ad9b11d0228273` |
| `config_hash` | `4b41fab90a83df08b57361cec4e769447815afe4f751c9f57848a022bf06a382` |

The ten tags are `BeamAngleX_{0,1}`, `BeamAngleY_{0,1}`, `MuonResolution_{0,1}`,
`Muon_Energy_MINERvA_{0,1}`, `Muon_Energy_MINOS_{0,1}`. The `config_hash` is the baseline value
`4b41fab9…` that `HANDOFF-20260922` §3 names, distinct from the L2 member's `4809b4ad…`.

**So there is exactly ONE stale binding to adjudicate**, not ten, and a per-receipt table would have
invented a distinction the artifacts do not carry.

## 2. The divergence, measured symmetrically on both sides

    pinned blob (all ten receipts)      dc74c38f8ec7b5f6723fa231630e9fc43e7a93f0
    blob at the receipts' own code_rev  dc74c38f8ec7b5f6723fa231630e9fc43e7a93f0   (self-consistent)
    blob at deployed HEAD 32e403b8      662951e019f9c96c2876decc7913c7e9b3dbf2ae
    blob at origin/main  384c2eb1       662951e019f9c96c2876decc7913c7e9b3dbf2ae

Both current values agree, so the divergence is not an artefact of which tree was read. The file is
`nd-unfolding/unfold_nd_omnifold_unbinned.py`. Four commits moved it, and they are the four
`HANDOFF-20260922` §4 names:

| commit | date | subject |
|---|---|---|
| `5afb7947` | 2026-08-19 | Remedy (A) lands on TWO of three writers; adopt is BLOCKED by a receipt binding |
| `ae42ae8d` | 2026-08-22 | k=0 M(ii) execution integrity: two roots, six rooted-import repairs |
| `0a4ab263` | 2026-08-25 | WIP sync note and response-mismatch work for travel |
| `1aa055d9` | 2026-08-26 | Merge candidate: closeout grade line + k=0 execution-integrity toolchain |

`git diff 42268b6d 384c2eb1 -- <path>`: **151 insertions, 4 deletions.**

## 3. CLASSIFICATION: **SEMANTIC**, so D2(b) does not apply

D2(b) permits re-pinning only where the diff is *"NON-SEMANTIC (comments, whitespace, strings not
read by the code path)"*. It is not. The four deleted lines are all executable:

1. `_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"` → `str(Path(__file__).resolve().parents[1])`
   — the OI-136 repair. This expression feeds three `sys.path` inserts (`_2D`, `_ND`, and `_OF` at
   the second rooted insert), so it selects **which modules the interpreter loads**.
2. two `argparse` defaults repointed from `_2D` to a new `_DATA_2D` under a separate `_DATA_ROOT`.
3. `if args.closure_reweight_axis and hidden_ax is not None:` → `elif`, with a new `if` branch ahead
   of it.

Plus a new top-level function `apply_record_only_eavail_shift` and a new CLI option
`--closure-response-eavail-frac`.

## 4. ⚠ THE DRIFT IS MEASURABLY BEHAVIOUR-PRESERVING FOR THE PRODUCTION INVOCATION — AND THAT IS **NOT** A LICENCE TO RE-PIN

Recorded because it is true and useful, and fenced because it is the argument that would otherwise
be mistaken for a reason:

- **`_REPO` evaluates to the same string.** Measured on the cluster, for the deployed file:
  `Path(...).resolve().parents[1]` → `/pscratch/sd/j/josephrb/MINERvA-OmniFold`, **identical** to
  the deleted literal. So `_2D`, `_ND`, `_OF` and both argparse defaults are unchanged **when the
  file is run from the canonical deployed path** — which is where the ten endpoints were produced.
- **The new option is inert.** It defaults to `None`; every new statement is behind
  `is not None`, and the `if`→`elif` conversion preserves the original branch whenever it is `None`.
- **The production invocation reaches none of it**: `--iters 5 --use-weights --estimator lgbm
  --seed 42 --bkg-mode purity`, with no `--closure`.

⚠ **This establishes behaviour-equivalence for one invocation from one path. It does not establish
code identity, and code identity is what the receipt asserts.** `validate_endpoint_receipt` compares
the blob strictly and is **right** to: the binding's purpose is to say *these bytes produced this
product*, and those bytes no longer exist in the tree. Re-pinning would replace a true statement
about a blob that is gone with a false statement about a blob that never ran.

**It also fails outside the canonical path by construction.** The OI-136 repair exists precisely so
the value *varies with location*; run from any other checkout, `_REPO` differs and the equivalence
above evaporates. A re-pin would silently assert the equivalence everywhere.

## 5. DISPOSITION — D2(c)

**All ten receipts are marked SUPERSEDED-BY-CODE-DRIFT.**

- The adopted product's **code identity cannot be re-established from the current tree.** The
  producing blob `dc74c38f` is reachable in history (`git cat-file -p 42268b6d:<path>`) but is not
  the file any run would execute today.
- **The fail-closed guard stays CLOSED.** `p4_check_receipt.py` continues to return
  `RECEIPT-REJECT` for all ten, and that is the correct behaviour, not a defect to be silenced.
- **The `e2632ac7` baseline-overwrite guard is what makes this safe to leave**: the rejection no
  longer falls through to a re-unfold. Verified in review — `run_p4_unfold_std.sh` returns `rc 9`
  when the baseline ROOT exists, no offset is declared and `P4_ALLOW_BASELINE_REUNFOLD=1` is absent,
  and the `rm -f` of the receipt now sits **below** that guard, so a refusal leaves the baseline
  exactly as it found it.

## 6. What this does NOT do

- It does **not** invalidate `3d7465f6…`. A stale code binding is a provenance fact about the
  receipts, not a measurement of the covariance.
- It does **not** re-verify any physics, and it is **not** a grade.
- It does **not** re-produce anything. `run_p4_unfold_std.sh` with no offset was **not run**, and
  must not be: it would overwrite the adopted covariance's own inputs.
- It does **not** decide whether the endpoints should eventually be re-produced. That remains a
  decision for Joseph, and re-producing them would invalidate `3d7465f6…` and everything below it.
- `M1`–`M4` are untouched and still travel with every use of the adopted digest.

**Co-Authored-By: Claude Opus 5 (1M context)**
