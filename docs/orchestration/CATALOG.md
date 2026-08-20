# Orchestration router

This is a pointer-only active-tree router. It contains no scientific evidence or authorization.

## Current work

- Live snapshot: [`LIVE-STATE.md`](LIVE-STATE.md); run its freshness check before use.
- Bounded queue: [`../CURRENT_WORK.md`](../CURRENT_WORK.md); sources live in
  [`control-plane/`](control-plane/).
- Queue overflow: [`../CURRENT_WORK_OVERFLOW.md`](../CURRENT_WORK_OVERFLOW.md).
- Unpromoted active records: [`../CURRENT_WORK_BACKLOG.md`](../CURRENT_WORK_BACKLOG.md).
- Active process rules: [`PLAYBOOK.md`](PLAYBOOK.md).
- Open/deferred source records: [`../OPEN_ITEMS.md`](../OPEN_ITEMS.md).
- Joseph-only decisions: [`USER-DECISIONS.md`](USER-DECISIONS.md).

## Evidence and claims

- Verified numbers: [`../../VALIDATION_LEDGER.md`](../../VALIDATION_LEDGER.md).
- Physics claims: [`CLAIMS.md`](CLAIMS.md).
- Active BEN identifiers: [`FINDINGS.md`](FINDINGS.md); full evidence is at the frozen tag.
- Bugs and traps: [`../../KNOWN_ISSUES.md`](../../KNOWN_ISSUES.md).
- Retracted values: [`INDEX-retracted-and-superseded-values.md`](INDEX-retracted-and-superseded-values.md).

## Task routes

| Task | Route |
|---|---|
| Change code | `KNOWN_ISSUES.md`, relevant status/reference, callers, tests, and hash bindings |
| Quote a result | `VALIDATION_LEDGER.md`, then the exact product or live receipt |
| Run or monitor compute | fresh `LIVE-STATE.md`, direct scheduler observation, then the exact launcher receipt |
| Work on 2D/3D/N-D/PET | relevant workstream status; PET also `PET_UQ_REMEDIATION_STATUS.md` |
| Maintain queue/playbook | [`control-plane/policy.json`](control-plane/policy.json), [`control-plane/source-record-inventory.tsv`](control-plane/source-record-inventory.tsv), then `control_plane_lint.py` |
| Maintain classifications | `MANIFEST-overrides.tsv`, then `generate_manifest.py` |
| Operate continuation | `WAKER.md`, `wakerctl.py`, `waker-config.json`, and `profiles.json` |
| Build deliverables | `docs/analysis-note/build_all.sh` for note, primer, and paper |

## Frozen pre-compaction evidence

Complete history, terminal receipts, long-form findings, audits, determinations, prompts, and old paths
live at:

`evidence/prepublication-2026-08-20-0b329e8a`

Recover a known path without changing the current checkout:

```bash
git show evidence/prepublication-2026-08-20-0b329e8a:<old-path>
```

Search the complete frozen tree:

```bash
git grep '<identifier>' evidence/prepublication-2026-08-20-0b329e8a --
```

The independently stored bundle and recovery proof are recorded in
[`../POST_PUBLICATION_REORG_PLAN.md`](../POST_PUBLICATION_REORG_PLAN.md).

## Regenerate

```bash
python3 docs/orchestration/control_plane_lint.py
python3 docs/orchestration/generate_manifest.py
python3 docs/orchestration/generate_manifest.py --check
```
