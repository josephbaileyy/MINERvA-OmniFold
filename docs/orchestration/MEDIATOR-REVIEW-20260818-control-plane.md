# Mediator review — generated documentation control plane

## Requested answer

Reply `APPROVE FOR MIGRATION`, `REVISE: <specific change>`, or `DECLINE: <reason>`.

`APPROVE FOR MIGRATION` approves the staged implementation on branch
`codex/docs-control-plane`: classification rules, the single `OI-80` override, promoted leaves and
weights, owner escalation, bounded playbook, manifest-semantics repair, and the atomic landing commit.

## What changes

- `OPEN_ITEMS.md` and `FINDINGS.md` remain byte-for-byte unchanged evidence stores.
- All 94 OI records are classified from explicit state-cell language; unknown wording defaults
  `active/NOW`. Duplicate `OI-64`/`OI-65` rows receive stable occurrence keys.
- Fourteen promoted leaves render in `CURRENT_WORK.md`; all 59 other active records render in
  `CURRENT_WORK_BACKLOG.md` and cannot disappear by omission.
- Twenty-two BEN-backed rules render in `PLAYBOOK.md`; active rules are capped at 25.
- Unassigned promoted work is mechanically routed to `WAITING-JOSEPH`.
- `generate_manifest.py` inventories tracked plus nonignored intended files, emits `tracking`, and
  excludes ignored artifacts.

## Measured result

| population | count |
|---|---:|
| OI source records classified | 94 / 94 |
| retired | 20 |
| deferred | 2 |
| waiting Joseph | 16 |
| blocked external | 19 |
| otherwise active | 37 |
| promoted leaves | 14 |
| active unpromoted backlog | 59 |
| active playbook rules | 22 |

Manifest regeneration produces 1,029 unique tracked rows. Relative to the stale committed manifest,
five paths disappear and all five are Git-ignored artifacts (four `.pyc`, one `.out`); 38 tracked
paths appear. No tracked path is dropped, ignored paths are absent, and unused overrides are zero.

## Review surface

1. [`PROPOSAL-20260818-control-plane-compaction.md`](PROPOSAL-20260818-control-plane-compaction.md)
2. [`control-plane/policy.json`](control-plane/policy.json)
3. [`control-plane/work-items.tsv`](control-plane/work-items.tsv)
4. [`control-plane/owners.tsv`](control-plane/owners.tsv)
5. [`control-plane/playbook.tsv`](control-plane/playbook.tsv)
6. [`control_plane_lint.py`](control_plane_lint.py)
7. [`generate_manifest.py`](generate_manifest.py)

Generated outputs are review aids, not separate judgment sources:
[`../CURRENT_WORK.md`](../CURRENT_WORK.md),
[`../CURRENT_WORK_BACKLOG.md`](../CURRENT_WORK_BACKLOG.md),
[`PLAYBOOK.md`](PLAYBOOK.md), and
[`control-plane/source-record-inventory.tsv`](control-plane/source-record-inventory.tsv).

## Verification

```bash
python3 docs/orchestration/control_plane_lint.py --self-test
python3 docs/orchestration/control_plane_lint.py --coverage-report
python3 docs/orchestration/control_plane_lint.py
python3 docs/orchestration/generate_manifest.py --self-test
python3 docs/orchestration/generate_manifest.py --check
.githooks/pre-commit
```

`python3 docs/orchestration/control_plane_lint.py --adoption-check` must pass in the isolated final
candidate. The approval flag permits final-byte generation; it does not authorize a push by itself.

## After approval

No design or classification work remains. Confirm `main` still equals the candidate base `4ad061b0`,
require `--adoption-check` and all checks to remain green, and push the atomic commit. If main
moved, rebase and re-verify. This packet and the proposal are already archival in the final manifest;
neither remains a standing live document.
