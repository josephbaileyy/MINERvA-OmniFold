# INTERIM HANDBACK — Claude interim root → canonical Codex root

- Written: 2026-08-03T23:50Z by interim Claude root `4a8668e1` (`interim_for` `019f749a-857b-7790-8cec-bc36b22908be`).
- Trigger: `evt-codex-personal-reset-20260726` (provider-reset, codex-personal) fired on the first post-restore tick after the 2026-07-22→2026-08-03 maintenance.
- Repo at handback: rebased onto `github/main` head `6cabd4d` (my handback commit on top); clean and synced. Post-restore `wakerctl.py preflight` PASS; `codex-cli 0.144.5` at `~/.nvm/versions/node/v24.18.0/bin/codex`; canonical session store intact (`…019f749a….jsonl`).

## IMPORTANT: substantial downtime (Delta) work has superseded parts of my interim state

While I was the interim root and during the shutdown, extensive campaign work landed on `github/main` (commits up to `6cabd4d`: B1 normalization fix, Gate-4 re-issue, adversarial defect fixes, flux-universe J28/J29, matcorr J18, four-account audit, etc.). **Treat the repo at `6cabd4d` as authoritative, not my pre-shutdown summary.** In particular:

- **The authoritative post-restore plan is [`RESTORE-2026-08-03.md`](RESTORE-2026-08-03.md)** (ordered, science-side): Step 0 `verify_hash_bindings.py` (expect ALL BINDINGS INTACT), Step 1 protect the sole G2 dump copy, Steps 2–4 Gate-2 units resolution → P5A closure receipt → P5A launch. Control-plane restore is PORTING §4 (independent).
- **Gate 4:** my 07-21 launch-code gate (`state/p3f-pet-gate4-launch-code-gate-20260721.json`) is **SUPERSEDED** → `state/p3f-pet-gate4-launch-code-gate-20260731.json` (RESTORE Step 2b re-issued it after the B1 normalization fix edited the driver+validator; binding moves recorded there). Use the 07-31 receipt.
- The 07-21 transcript "hole" flagged in the superseded receipt is **resolved on restored Perlmutter scratch**: the Gate-4 agy verification transcript is present at `runs/agy-publication-redteam/20260721T193131Z-send-fc5cee97.txt` (RESTORE Step 6 recovery is no longer blocked).

## Campaign state (as of handback)

| Gate | State |
|---|---|
| Gate 1 / Gate 2 | PASS (Gate-2 units resolution is RESTORE Steps 2–3 — verify) |
| **Gate 3** (P3F-PET source array `56169838`) | **PROMOTED PASS** — 120/120; manifest `state/p3f-pet-gate3-source-manifest-56169838.json` (sha `306e5459`), agy-verified. |
| **Gate 4** (nominal + GPU floor) | launch-code gate **re-issued PASS_CODE_ONLY** (07-31 receipt). Nominal PET training **NOT launched**; launch is a pending user decision (RESTORE Step 4 = P5A launch). |

## Interim rounds I ran (all in RUNS.tsv, committed+pushed)

1. `MIG-P3F-PET-G3-SOURCE-RECON1` — reconciled array 56169838 (120/120); built + audited the source manifest.
2. `MIG-P3F-PET-G3-PROMOTE` + `MIG-AGY31` — agy independent verification PASS → Gate 3 PROMOTED.
3. `MIG-P3F-PET-G4-BUILD*` / `MIG-AGY32` / `MIG-P3F-PET-G4-CODEGATE` — built + agy-verified the 07-21 Gate-4 launch-code gate (two background dispatches were reaped at session teardown; the third **synchronous foreground** send succeeded — prefer synchronous `agentctl` sends). This gate was later superseded by the Delta B1 re-issue (above).
4. `MIG-PRESHUTDOWN-20260721` — PORTING §3 checklist PASS; bundle `orchestration-handoff-20260721T200209Z.tar.gz` (sha `a1006bae`).
5. This handback.

## Capacity (fresh snapshot 2026-08-03T23:47Z)

- codex-personal **6%** weekly remaining (reset 2026-08-08T03:35:36Z) — nearly empty; the pre-shutdown "100%/rolling-reset" reading was transient and capacity was consumed during downtime. **Conserve.**
- codex-school **75%** (reset 2026-08-07T06:27Z). Claude per usual. agy usable via `agentctl` (28bc7c3 HOME fix). **0 Full reset credits; protected-reserve rule stands.**

## Worker UUIDs (preserved — route only via agentctl.py send)

- agent-B-p5b `46e4af3e-c3f2-4fa5-abc7-f0da72817282` · agent-C-fps `4580f42d-77db-4f59-88c4-1b2854f24d82` · agy-publication-redteam `440f42ef-c271-4f77-a410-a4a999166f44`.

## Routing

On rc=0 of this handback resume, the interim root restores `waker-config.json` `root` and `state/live-state.json` `orchestrator_thread_id` to `019f749a-857b-7790-8cec-bc36b22908be` (provider codex, profile codex-personal, goals disabled), commits, ledgers, and stands down. All future wakerctl wakes resume you (the Codex root). Start from `RESTORE-2026-08-03.md` Step 0; re-arm continuation coverage per WAKER.md before ending your turn.
