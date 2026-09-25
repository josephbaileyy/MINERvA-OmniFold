# RECOVERY MANIFEST 2026-09-24 — the preparation evidence epoch and the scalar-5D trunk's bytes

**CITABLE FOR:** the evidence tags, bundles and checksums of the 2026-09-24 epoch; the recovery tests
executed on them; which external scalar-5D objects have a durable copy; the frozen simplification
family list.
**NOT CITABLE FOR:** scientific verification of any object, adoption, or publication readiness. A
checksum match says the bytes are the bytes; it says nothing about whether they are right.

Authorization: [`AUTHORIZATION-20260924-preservation-and-simplification-pass.md`](AUTHORIZATION-20260924-preservation-and-simplification-pass.md).
Machine-readable inventory: [`state/RECOVERY-MANIFEST-20260924-trunk-external-artifacts.json`](state/RECOVERY-MANIFEST-20260924-trunk-external-artifacts.json).

## 1. The evidence epoch

| | monorepo | standalone note repository |
|---|---|---|
| tag | `evidence/preparation-2026-09-24-bf34a12c` | `evidence/preparation-2026-09-24-a11b7055` |
| tag object | `6bb0af34bd0721b359bf6c6b5ffdd19e9c2a0d18` | `4a58ba4209a37732a1635b622e72e55b1fbd9641` |
| commit | `bf34a12cff9a2f06f0a3f1c516628085565eef60` | `a11b70556cea4e23b4db7881a8033c8dd2632563` |
| remote target | verified with `git ls-remote` after push, 2026-09-25T02:37Z | same |
| tracked paths at tag | 2,399 | 99 |
| all-ref bundle | `repository-all.bundle`, 236,358,640 B, sha256 `31aba79ca6a345f82bb1f9cf55c15871fbc2ea66a9b0bd0eabcca9b77f743d5b` | `analysis-note-all.bundle`, sha256 `36e294ae458929ce078372d3bff44f4acd12be0c69fbe74a26e92a28c21cc5e1` |

The monorepo commit is the draft-preservation commit, so the epoch contains both preserved drafts.
The older epoch `evidence/prepublication-2026-08-20-0b329e8a` is untouched.

**Storage.** Two copies of the epoch directory, each sealed by the same `SHA256SUMS` (29 files, itself
sha256 `7431f87f1159aee688340fec5a687aecc988de6fd982c46fa8f6eb8343814c23`, resealed after the review added `trunk-baseline-verify.txt`):

- local: `/Users/josephbailey/local-research/evidence-epochs/preparation-2026-09-24-bf34a12c/`
- NERSC global home: `/global/homes/j/josephrb/evidence/repository-epochs/preparation-2026-09-24-bf34a12c/`

Both passed `sha256sum -c SHA256SUMS` after the last write. Home quota after all copies (re-read after the last copy): 21.38 of 40.00
GiB. The directory's `RECOVERY.md` gives the commands.

### Recovery tests executed

| test | result |
|---|---|
| fresh GitHub clone → detach at the tag | HEAD `bf34a12c…`; both drafts restored with blobs `cf3c2e85…` / `8b0617b6…`; 2,399 paths |
| clone from the local bundle only (no network) | HEAD `bf34a12c…`; drafts restored; four anchored cited commits and two local-only cited commits resolve |
| clone from the NERSC copy of the bundle, on a login node | HEAD `bf34a12c…`; both draft blobs equal |
| note repository: GitHub clone and bundle clone | both HEAD `a11b7055…`, trees identical |

### Cited commits

A scan of every text blob at the tag found 3,116 distinct commits cited: 3,087 reachable from pushed
monorepo refs, 10 from the note repository's pushed `main`, and **19 only from local refs**. Those 19
are in the bundle and on no public remote: 15 sit on local branches; 4 were dangling and are now
anchored at `refs/preserved/preparation-20260924/cited-<sha>` (local refs, not pushed). Pushing them
would publish unreviewed local work to a public remote, so this pass did not.

### Outside every snapshot

Uncommitted bytes are not in git and were left untouched: 11 untracked files in the shared main
checkout (listed with blobs in the epoch's `main-untracked-exclusions-blobs.txt`), 37 staged paths in
`MINERvA-OmniFold-pet-prong-semantics`, 36 untracked in `MINERvA-OmniFold-presentation-sep09`, 3
untracked in `MINERvA-OmniFold-z-build`. 35 local branches are neither in the tag nor on a remote;
they exist only in the bundle (`local-branch-inventory.tsv`).

⚠ **The shared main checkout still holds untracked copies of the two drafts**, byte-identical to the
committed blobs. `git pull --ff-only` there refuses until they are removed (measured on git 2.39.3 with
an identical-content control). They were not touched: the checkout is shared. Whoever next updates it
can confirm `git hash-object` equals the blobs above, remove the two files, and pull.

## 2. External scalar-5D objects (not in git)

Measured 2026-09-25T02:44–03:00Z by login-node reads only, no allocation. Every sha256 below was
recomputed on the original. **All 8 inputs named by the trunk manifest** (`z-manifest.json`, sha256
`44ab73ba…`, producing revision `fb9ec356…`), the adopted bytes, both projections and the graded pair
**re-hash to their recorded digests.**

| group | objects | status |
|---|---|---|
| adopted `z-cv.npz` `3d7465f6…`, 890,500,272 B | 1 | **PRESERVED — restore tested** (NERSC home copy → scratch, re-hashed equal) |
| its own records: manifest, provenance, receipts, bridge, primary, null pair | 9 | PRESERVED — checksum-verified copy |
| `(E_avail,W)` projection `835828bf…` + receipt, binding, comparison, cutoff scan, job logs | 9 | PRESERVED (the ROOT file restore tested) |
| `(p_T,p_∥,E_avail)` projection `20c16e16…` + receipt + logs (constructed, not adopted) | 6 | PRESERVED — checksum-verified copy |
| Appendix F release-package draft arrays (not shipped) | 5 | PRESERVED — checksum-verified copy |
| grade records `GRADE.json`, `r5-asm.json`, `r5-grade.json`; both members' manifests, receipts, bridges, null pairs | 15 | PRESERVED — checksum-verified copy |
| input `central` `630306e2…` (5D central value ROOT, 479,553 B) | 1 | PRESERVED — checksum-verified copy |
| input `parent` `4f168e83…` | 1 | **PRESERVED — restore tested** from HPSS tape (`mnv-quoted-products-20260812`, PV `AB014700`) |
| input `support` `9f7b2f55…`, 41,436,632,945 B | 1 | PRESERVED — HPSS copy, md5 equal to the original's; **restore not tested** (41 GB) |
| **the nine below** | 9 | **UNPRESERVED — sole copy on purgeable `/pscratch`** |

The copies are under `…/preparation-2026-09-24-bf34a12c/trunk-baseline/`, 46 files, 908,624,492 B of file content,
mirroring the `/pscratch/sd/j/josephrb/` relative paths; `trunk-baseline.SHA256SUMS` verifies them.
The copy was made in three steps (23 files by `copy_and_restore.sh`, then 19 and 4 small files); the
copy-versus-original comparison for all 46 is in the epoch's `trunk-baseline-verify.txt`.

### The gaps

| object | size (B) | why it matters | what would close it |
|---|---:|---|---|
| input `active` `std_final5_candidate.root` `950f8cb1…` | 42,326,607,877 | rebuild input; its lineage is the ten endpoint unfolds | a durable copy — ~39.4 GiB against ~212 GiB free HPSS; needs a storage decision (the kind `OI-131` reserves) and an `xfer` job |
| input `throw` `z_precursor_20260914/unified_throw_cov_5d.root` `09a029ed…` | 2,668,265,910 | rebuild input (HPSS holds a **different** 08-12 ensemble) | same |
| input `stat` `uq_cov_stat_5d.root` `6580016f…` | 891,732,011 | rebuild input | same |
| input `ml` `uq_cov_mlsplit_5d.root` `27b2e456…` | 892,078,834 | rebuild input | same |
| `z-mean.npz` `61b7a493…` (not adopted) | 890,383,062 | the mean-centered comparison AGENTS.md quotes (`√tr` 7.13% below) | same |
| graded pair `member_k000000/z-cv.npz` `361090f9…`, `member_k001200/z-cv.npz` `7e4636a3…` and both `z-mean.npz` | 3,549,178,987 | the bytes behind M1's `s_proj = 6.145%` | same |

> **Forward pointer, added 2026-09-25 by the s5c campaign:** these nine objects now have an HPSS copy,
> tape-resident and restore-verified by SHA-256 —
> [`RECEIPT-20260925-d3-hpss-backup-of-nine-sole-copy-objects.md`](RECEIPT-20260925-d3-hpss-backup-of-nine-sole-copy-objects.md).
> The table below is kept as measured on 2026-09-25T02:44–03:00Z.

Total unpreserved: **51,218,246,681 B (47.7 GiB)**. **Full preservation is NOT certified.** The adopted
bytes and every reporting product can be recovered without them; **a rebuild of the trunk from its
manifest cannot**, and neither can an independent recomputation of M1 from the graded bytes.

**Not inventoried by this pass:** the L2 probe product (`z2m-products/member_k001200_L2laterals/`,
`48713676…`), the ten endpoint unfolds under `active_universe_5d/standard/unfolds/`, and the event-loop
inputs upstream of `central`, `support` and `active`.

**Three kinds of verification, kept apart.** *Checksum*: the sha256 of the original and of the copy.
*Restore*: a copy read back to a new path and re-hashed — done for `z-cv.npz`, the publication
projection and `parent`. *Scientific*: none; nothing here is independently re-verified.

## 3. The frozen simplification family list

Frozen before any change, after the inventory. **No file is removed from `main` by this pass.** Every
candidate removal was scanned for consumers and each had a surviving reader — code, a test, a probe
or routed prose — so each stays:

| candidate | consumer that retains it |
|---|---|
| `HANDOFF-20260815-0455Z.md` | `nd-unfolding/pet/closure_foldforward_instrumented.py` |
| `HANDOFF-20260819-lane-e-data-only-cstat-smoke-57266000.md` | `watch_report_train_run.py`, `state/gate5-do-train-array-active-57266000.json` |
| `HANDOFF-20260820-2154Z-publication-closeout.md` | `FINDING-20260830…`, `PUBLICATION-READINESS-20260822.md` (routed prose) |
| `MIGRATION-HANDOFF.md` | `RUNS.tsv`, `MIGRATION-DELTA.md`, `LIVE-USAGE.md` |
| `HANDOFF-20260921-gbdt-remaining.md`, `HANDOFF-20260922-gbdt-cold-start.md` | `state/check-withdrawal-completeness-20260910.py` (pinned counts) |
| `REPORT-20260922-review-residue.md` | `.githooks/pre-commit` advisory, three `probes/probe-20260922-*` |
| `NAVIGATION-20260917-z-pilot-outcome-route.md` | `nd-unfolding/tests/test_run_m1_projection_refusals.py` |

**F1 — the scalar-5D discovery route in `CATALOG.md`.** Nine sections, in the six line ranges below, move **verbatim** into a new
declared continuation, `CATALOG-ARCHIVE-scalar5d.md` (the phase-2 split `CATALOG.md` § *Regenerate*
already specifies), and one compact current entry route replaces them. Headings and line ranges at
`bf34a12c`:

| lines | section |
|---|---|
| 45–533 | THE SCALAR-5D REQUIRED DELIVERABLE PATH … (2026-09-18) |
| 599–650 | Decisions awaiting Joseph — cause 7's subject and magnitude, cause 3's seed scan, the stop rule |
| 651–689 | Y as R2 permits it, the complete-successor question, and #11-#30 reconciled (2026-09-05) |
| 690–2779 | Joseph rules the complete-successor question: Z may be specified (2026-09-06) |
| 2780–2837 | Z assembly/spectrum pilot — the outcome route (2026-09-17) |
| 3949–4020 | the four 2026-09-18 scalar-5D sections: completion inventory, the plan, rank-6 consumer, reproduction path |

Paths: `CATALOG.md`, `CATALOG-ARCHIVE-scalar5d.md` (new), `MANIFEST-overrides.tsv`, `MANIFEST.tsv`
(regenerated), `state/check-withdrawal-completeness-20260910.py` (registers the continuation so its
pinned occurrence moves with the text rather than vanishing). Gate: the link-target set of router
plus continuations is unchanged; `live_doc_indexed.py --check/--unrowed`, the withdrawal check,
`generate_manifest.py --check`, `control_plane_lint.py` and the render/table probes stay green.
**Not moved:** *ROUND 11* and *B1 steps 4-5*, for the reasons `CATALOG.md` § *Regenerate* records.

**F2 — the superseded GBDT work orders and the ended review ledger, reclassified in place.**
`MANIFEST-overrides.tsv` rows only (plus the regenerated `MANIFEST.tsv`); no file bytes change:
`REPORT-20260922-review-residue.md` → `ARCHIVAL terminal` (Joseph ended the loop at `c496135f`, whose
message leaves archiving to this pass); `HANDOFF-20260921-gbdt-remaining.md` and
`HANDOFF-20260922-gbdt-cold-start.md` → `ARCHIVAL superseded`, **only if** every item they list as
open is routed by a surviving record — otherwise they stay `LIVE` and the reason is recorded.

Historical lookup for anything moved or reclassified:

```bash
git show evidence/preparation-2026-09-24-bf34a12c:docs/orchestration/CATALOG.md
git grep '<identifier>' evidence/preparation-2026-09-24-bf34a12c -- docs/orchestration/
```

### Execution record (added 2026-09-25)

- **F1 executed** at `8cffde7b`, **except one frozen gate clause**: the render probe does not stay
  green. `probe-20260922-render-checks.py` reports 61 inline-marker leaks in the continuation; the
  identical 61 texts parse as leaks in the full pre-move router and the new router has 0, so they are
  pre-existing and surfaced only because the probe scopes by lines added since `177af61b`. The move was
  kept verbatim rather than reformatted. `probe-20260922-seven-gates.sh` is therefore red on `main`;
  `probe-20260922-render-checks.py --since 8cffde7b` exits 0. Every other F1 gate held.
- **F2 not executed**: its precondition failed. A read-only sweep of both handoffs found five open
  items tracked nowhere else; they are routed in
  [`HANDOFF-20260924-preparation-for-scalar5d-campaign.md`](HANDOFF-20260924-preparation-for-scalar5d-campaign.md)
  D10–D11, and the three documents stay `LIVE`.
