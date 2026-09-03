# AUTHORIZATION 2026-09-03 — Joseph authorizes the OI-136 fail-open entrypoint repair

**CITABLE FOR:** the authorization in §1 and its scope in §2. **NOT CITABLE FOR:** any deployment,
redeploy, freeze expiry, grade, adoption, gate movement, launch, spend, or publication claim.
**Gate 2 remains FAIL. CAND `1 of 7`, QUOTED `0 of 7`.** PET `C_stat` remains
`EXISTS — UNVERIFIED, PAIRING DECLINED`. The five Gate-6 prohibitions stand.

## 1. Authority — his own turn, to the integration lane

The integration ledger `INTEGRATION-20260903-wave1-routing-freeze-and-ledger.md` §7.1 put this
ruling to Joseph: *authorize a repair of the 45 sites (replace each absolute `sys.path.insert(0,
<cluster root>)` with a `__file__`-relative root, updating the two ratchet constants in the same
commit and naming every site), or rule that the guard is the accepted mechanism.* Joseph,
2026-09-03, on the integrator's return:

> *"I authorize it, can you provide the updated envelope so I can give it to the reviewer?"*

Read as authorizing the first option — the repair — since that is what the request asked him to
authorize. The scoping in §2 is this lane's and remains open to challenge; the authorization is his.
Recorded because in this repository an authorization is itself an evidence artifact.

## 2. Scope — 36 of the 45, and the 9 that are NOT repaired, each with its measured reason

Population: the FAIL-OPEN SET printed by
`docs/orchestration/state/probe-oi136-sys-path-hijack-20260826.py` at `71839696`, **45 files**,
pinned by `nd-unfolding/tests/test_oi136_failopen_inventory_ratchet.py` (`FAILOPEN_COUNT = 45`,
sha256 `4201aceed0604f92…`).

**Repaired (36):** every file in the set not listed below. The transformation is one thing only:
the root that feeds a `sys.path.insert(0, …)` is derived from `__file__`; sub-paths, data-path
defaults, and every other line are unchanged. Both ratchet constants move in the same commit and
every site is named there, as the ratchet's own rule requires.

**Not repaired (9), measured before dispatch:**

| file | reason |
|---|---|
| `docs/orchestration/state/probe-oi120c-loader-purity-perturbation-20260814.py` | probe RECORD of what was run; editing it falsifies the record (`test_oi136_rooted_insert_ratchet.py` reason `probe`) |
| `docs/orchestration/state/probe-oi22-leakage-real-input-20260814.py` | same |
| `docs/orchestration/state/probe-oi22-schema-parity-real-input-20260814.py` | same |
| `2d-unfolding/unfold_2d_omnifold_unbinned.py` | the published 2D arm; **Joseph ruled 2026-08-23 to leave it** (dormant insert inside `main()`, sha pinned in three places, advancing needs a Gate-2 re-run). A blanket authorization today does not silently override that specific ruling |
| `nd-unfolding/pet/train_fullevent_nominal.py` | receipt-bound: `verify_hash_bindings.py` reports **BINDINGS BROKEN** on any byte change (measured by appending one comment and reverting); 29 receipts name it |
| `nd-unfolding/pet/validate_pet_nominal_gate4.py` | receipt-bound, measured as above; 17 receipts |
| `nd-unfolding/pet/fullevent_fps_dataloader.py` | receipt-bound, measured; 14 receipts |
| `nd-unfolding/adopt_unified_5d.py` | receipt-bound, measured; 7 receipts. One of `OI-136`'s two named remedy-(A) covers — it stays behind the guard |
| `nd-unfolding/pet/dump_pointcloud_inputs.py` | receipt-bound, measured |

The five receipt-bound files can only move through the binding owner's process (the receipts pin
their bytes and the pre-commit hook enforces the pin); that is a separate act this authorization
does not perform. For all nine, `nd-unfolding/mnv_guarded_run.py` remains the door, and the
campaign queue refuses any compute whose producer or validator does not route through it.

## 3. What this authorization does NOT do

It expires no freeze: `FREEZE-20260830-k0-deployment-7ac0edec.md` remains live, and the deployed
cluster copies of the repaired files stay at their frozen bytes until an authorized redeploy under
that freeze's own process — after which `verify_executing_copy_is_committed.py` will report the 36
as changed relative to `7ac0edec`, which is the expected and honest state. It launches nothing,
adopts nothing, grades nothing, and moves no count.
