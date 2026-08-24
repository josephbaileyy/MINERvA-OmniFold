# Active process-evidence index

The complete pre-freeze casebook and every long-form finding live at
`evidence/prepublication-2026-08-20-0b329e8a`. Recover an indexed row with:

```bash
git show evidence/prepublication-2026-08-20-0b329e8a:docs/orchestration/FINDINGS.md | rg '<BEN-ID>'
```

This file retains only BEN identifiers used by the active generated playbook. `PLAYBOOK.md` owns the
current operating rule and observable check; the tag owns the complete evidence and chronology.

The allocation table remains machine-readable because the merge guard derives ownership from it. Full
allocation rationale is frozen at the evidence tag; new allocations still require a fetched-remote
freeness check and a closed ten-block claimed with its first filing.

**`530-539` freeness check, 2026-08-24.** `git fetch origin`, then this file's own allocation tail
read at every one of the 43 refs under `refs/heads`, `refs/remotes` and `refs/tags` — all 43 carry a
`FINDINGS.md`, so the search covers the ref set rather than a sample. 39 refs read `unallocated 520+`
and 4 read `unallocated 530+`; none allocates any id in `530-539`. The block is claimed here with its
first filing (`BEN-530`).

| lane | block |
|---|---|
| pre-block era | `001-089` |
| D — verifier | `090-099` |
| B — uncertainty | `100-129` |
| C — PET | `130-159` |
| D — verifier successor | `160-189` |
| A — orchestrator | `190-199` |
| repository infrastructure | `200-209` |
| A — orchestrator continued | `210-229` |
| C — PET continued | `230-239` |
| B — uncertainty continued | `240-249` |
| D — verifier continued | `250-259` |
| receipt repair | `260-269` |
| Gate-6 Leg 0 | `270-279` |
| P5A extraction repair | `280-289` |
| OI-120(c) repair | `290-299` |
| mediator | `300-309` |
| executor | `310-319` |
| propagation correction | `320-329` |
| OI-124 disposition | `330-339` |
| diagnostic review | `340-349` |
| PET verification | `350-359` |
| fold-forward closure | `360-369` |
| hook dispatch | `370-379` |
| quarantine provenance | `380-389` |
| seconding | `390-399` |
| C — PET third block | `400-409` |
| quarantine provenance second block | `410-419` |
| C — PET fourth block | `420-429` |
| mediator second block | `430-439` |
| seconding second block | `440-449` |
| D — verifier second block | `450-459` |
| C — PET fifth block | `460-469` |
| quarantine provenance third block | `470-479` |
| B — uncertainty third block | `480-489` |
| storage migration | `490-499` |
| fixture-decoy block — do not allocate without exact review | `500-509` |
| remedy-(A) verification | `510-519` |
| review-round governance | `520-529` |
| C — PET sixth block | `530-539` |
| unallocated | `540+` |

## Long-form findings index

All pre-freeze long forms are indexed by the frozen `FINDINGS.md` at the evidence tag.

Four long forms remain in the live checkout: three because the canonical-designation guard inventories
their paths, and one because hash-pinned runtime diagnostics route to it. All other long forms are
recovered from the frozen index.

| retained long form | route |
|---|---|
| `FINDING-20260730-event-feature-nonfinite.md` | Retained for hash-pinned runtime diagnostics; exact full evidence also exists at the evidence tag. |
| `FINDING-20260807-checkpoint-is-not-the-trained-model.md` | Full evidence row at the evidence tag. |
| `FINDING-20260807-step1-under-achieves.md` | Full evidence row at the evidence tag. |
| `FINDING-20260811-promotion-by-move-silently-repoints-artifacts.md` | Full evidence row at the evidence tag. |

| id | frozen evidence |
|---|---|
| BEN-023 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-025 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-026 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-027 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-028 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-035 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-074 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-077 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-080 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-082 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-119 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-191 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-193 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-199 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-205 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-214 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-228 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-300 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-304 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-305 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-312 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-322 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-323 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-328 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-331 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-335 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-383 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-387 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-392 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-398 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-410 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-454 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-455 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-456 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-468 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-476 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-477 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-478 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-482 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-483 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-484 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-520 | Post-freeze. Evidence: `docs/orchestration/GATE1-VERDICT-ROUND4-20260823-k0-execution-integrity.md`, `docs/orchestration/GATE1-VERDICT-ROUND5-20260823-k0-execution-integrity.md`, `docs/orchestration/GATE1-VERDICT-ROUND6-20260823-k0-execution-integrity.md`, `docs/orchestration/DECISION-20260823-joseph-a2f-does-not-substitute-for-a3.md`. |
| BEN-530 | Post-freeze. A bar calibrated against one noise source is silent about a second, not conservative about it. Evidence: `docs/orchestration/FINDING-20260824-five-rules-from-the-r5-night.md` (BEN-530); `docs/orchestration/state/RECEIPT-20260823-oi126-r5-loss-interpolation-sweep.json` per-member `dL_rowset_max_dev`; retraction at `7da3b3d6`, strike at `74cee642`. |
| BEN-531 | Post-freeze. A discriminating test publishes its endpoint separation, the residual it must resolve, and its size under its own null BEFORE it runs. Evidence: `docs/orchestration/FINDING-20260824-five-rules-from-the-r5-night.md` (BEN-531); `docs/orchestration/state/RECEIPT-20260823-oi126-r5-loss-interpolation-sweep.json` key `C2_DISCRIMINATOR_20260824`; job `57507676`. |
| BEN-532 | Post-freeze. ssh ControlMaster multiplexing pins repeated connections to one login node, so a process list answers about that node and reads as corroborated. Evidence: `docs/orchestration/FINDING-20260824-five-rules-from-the-r5-night.md` (BEN-532). |
| BEN-533 | Post-freeze. Another lane's scheduler state is not yours to act on, and `squeue --me` returns the whole shared account. Evidence: `docs/orchestration/FINDING-20260824-five-rules-from-the-r5-night.md` (BEN-533); duplicate job `57506433`; foreign job `57275989` in the same `--me` output. Ruled by Joseph 2026-08-24. |
| BEN-534 | Post-freeze. A hold is a property of the branch, not of restraint: five commits described as held published as ancestors of another lane's push. Evidence: `docs/orchestration/FINDING-20260824-five-rules-from-the-r5-night.md` (BEN-534); `9a881c03`, `82cac45f`, `87310615`, `bc76ac6c`, `0e53f962` under `origin/main`. |
