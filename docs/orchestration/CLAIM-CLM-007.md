# CLM-007 claim detail

## Original claim cell

DEFECT (found by V1, confirmed by me): `build_fullevent_loaders` falls back to MC `reco_scalars` when `measured_scalars` is absent — and of_inputs_pc_fps_xps2.npz LACKS `measured_scalars` — so any data-side run on xps2 trains step-1 on misaligned MC rows incl. −9999 sentinels (8k smoke: 4411/8000 rows were MC misses). Synthetic stress + ordinary closure + census are unaffected (no data-scalar path).

## Status history

VERIFIED-CODE (defect)

## Evidence artifact

codex_audit.out F1; my key-inventory check (measured_scalars absent; 5D xps2 npz `measured` (4116128,5) exists as repair source)

## Data/config hash

npz sha dfd52750…

## Commit

defect in 9d353e1 (fallback at fullevent_fps_dataloader.py:229)

## Slurm job(s)

—

## Independent verifier

codex V1 + me

## 2026-07-17 — Residual history

RESOLVED UPSTREAM 2026-07-17: Agent B landed aa3f44c (fail-closed guard + row-count alignment gate + regression tests + xps2 callers pass of_inputs_5d_fps_xps2.npz); orchestrator verified the guard in-tree (fullevent_fps_dataloader.py:250). Full event-by-event order proof remains a P5B hardening item
