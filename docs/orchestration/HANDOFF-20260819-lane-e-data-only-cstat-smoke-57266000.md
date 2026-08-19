# HANDOFF — lane E, data-only C_stat, array `57266000`

*Written 2026-08-19 by lane E, immediately before a full session reset and an account migration. **Assume the
reader has none of my context.*** Every value below was read from a command in the session that wrote this
file; nothing is from memory.

---

## 1. THE ONE THING TO KNOW FIRST

**Array `57266000` is submitted, queued, and CANNOT RUN UNTIL AT LEAST 2026-08-26T06:00.**

```
ReservationName=maintenance_20260819  StartTime=2026-08-19T06:00:00  EndTime=2026-08-26T06:00:00
                                      Duration=7-00:00:00  NodeCnt=5248  Flags=MAINT,IGNORE_JOBS,SPEC_NODES
57266000_0  PENDING  Reason=ReqNodeNotAvail,_Reserved_for_maintenance
squeue --start estimate: N/A          jobs RUNNING on the gpu partition: 0
```

The run itself takes ~178 min once it starts. **Those are different numbers and quoting the second alone is the
mistake `BEN-473` is about.**

**IF THE MAINTENANCE DRAINED THE QUEUE, THIS JOB NEEDS RESUBMITTING — AND THAT IS NOT PRE-AUTHORISED.** The go
I was given covers *this* submission. Check the array still exists before assuming it will run; if it is gone,
the resubmit decision belongs to the orchestrator and then to Joseph.

## 2. Paste-ready facts

| what | value |
|---|---|
| array | `57266000` (task `57266000_0`, spec `0-0`, ONE member) |
| stage | `train` — no `--dependency`; targets pre-exist and were asserted |
| deployment | `/pscratch/sd/j/josephrb/gate5-data-only-frozen-377c713` @ `377c713d1790d96d15f7d115d9c903fd556c5943` |
| data root | `/pscratch/sd/j/josephrb/gate5-do-g2` |
| family root | `<data root>/nd-unfolding/pet/fullevent_cstat_data_only_n50` |
| logs | `<family root>/logs/train_57266000_0.{out,err}` |
| watch | `gate5-do-train-57266000`, armed, verified 3 ways |
| addendum | `docs/orchestration/state/DIVERGENCE-MANIFEST-ADDENDUM-20260819-train-57266000.json` |
| evidence | `/global/homes/j/josephrb/evidence/BEN-477-57256638_0/` **and** `/pscratch/sd/j/josephrb/gate5-do-g2-evidence/BEN-477-57256638_0/` |

Deployment digests, computed in the frozen tree:

```
c92c9cc06033f195ac48cddc86eea95a67b3038ae12fcffcd3cc966540b4e75f  train_fullevent_replica.py
a8263000e43f43d17f33b5bf855413287c731645c33bb61ac5886d365f966d35  cstat_data_only.py
20524894b7bd8906876cc58572ae54983f6f5ae3441a350bfd695dc80ffc4434  cstat_data_only_readback.py
76c92af0c682f6d6d89d0d9d36d21fd62310a7f27af61c9b9f827aa02aa192e5  submit_gate5_data_only_n50.sh
ce4c0aa3187904eb1065ddda852664aaa9e002e6ef1cba6d324936cc5bedde5f  sbatch_gate5_data_only_train_array.sh  (unchanged from smoke 3)
91144bee2ff89ae62497c8282174f0fc1c344f455945d6b52b7b8219ecb4e7bc  train_fullevent_nominal.py  (PINNED, matches its gate)
e1402370cdb8bd6349419ba6fbefa68817b799b3699cc97b673933f1f0220ce1  fullevent_fps_dataloader.py (PINNED)
```

## 3. How to read the result — FIVE NAMED SIGNATURES, not a binary verdict

Three prior attempts failed, **each further down the path and each a different cause**, so "did it fail" is not
a useful question. Grep `logs/train_57266000_0.{out,err}`:

| signature | meaning if present |
|---|---|
| `bootstrap_seed=None (NOMINAL)` | the module-global substitution did NOT take effect (`57194055`'s cause) |
| `replicas/replicas` | the `parents[3]` family-root fix regressed (`57253127`'s cause) |
| `withheld key(s) present` | **must now be impossible** — the withheld set is empty (`57256638`'s cause, `BEN-476`) |
| `not -1 -- in a data-only build` | the NEW positive seed check fired: `bootstrap_seed` was not `-1` |
| `no-clobber guard (checkpoints)` | the `BEN-477` quarantine did not take |

**Success is a `PASS` receipt plus `DONE index=0 seed=50000`.** Anything matching none of the five is a *fourth
thing* — report it as itself rather than forcing it into one of these.

Prior attempts, for calibration: `57235710` (killed 50/50 in 10 s by a `set -u` I added to a shim);
`57253127_0` (131 s, the F2 off-by-one); `57256638_0` (02:58:44 — trained fully, six fits, LR anneal verified
from the optimizer, both final checkpoints round-trip verified, then died at the receipt write).

## 4. What is UNTESTED, stated so nobody infers otherwise

**The controller's INTEGRATION of the new checkpoint-collision guard is exercised for the first time by this
submission.** The guard itself was power-tested five ways by executing its production text extracted from the
file by content anchor, plus a deployed probe in the frozen tree — but a faithful full-controller test needs the
pinned input npz, hence a clean cluster checkout, hence the freeze. **Untested, not assumed.**

## 5. After it lands

1. Read the five signatures above and the four declared products.
2. Run `verify_manifest_precedes_artifacts.py` against the addendum's commit sha — **from the cluster**, where
   the family root is visible, or the check passes vacuously (`BEN-474`).
3. **A PASS IS NOT AUTHORISATION FOR THE 151 A100-h FAMILY.** That decision returns to the orchestrator and then
   to Joseph. Also not authorised: the full family, any second member, `OI-133`'s digest binding, a resubmit,
   and any cleanup of the cluster checkout.

## 6. Open items this run touches

- **`OI-132`** — the divergence manifest's 18/55/4 partition is **embargoed**: its recorded reason was wrong.
  **Zero of the 55 are uncovered**, so this is *restate why each is covered*, not *find the gaps*. Gates no run.
- **`OI-133`** — nothing binds a checkpoint to the run that wrote it. **Widened on lane D's report: a digest
  proves the bytes, only an identity binding proves whose bytes.** Deferred until one receipt exists end to end,
  because the receipt write is the step never yet observed completing. **Ordering constraint: land the identity
  binding BEFORE anything that removes bytes** — the 41.44 GB gate is enforced by nothing today and getting it
  backwards is not recoverable.
- **`BEN-476`** — a guard citing an authority that did not say it. **Re-read any rule a guard's message cites.**
- **`BEN-477`** — the failed run's 14 checkpoints are complete *by name*; evidence preserved in two places.
- **`BEN-478`** — three controls failed in the manner each was written to detect, within one hour.

## 7. Environment facts that cost me time

- **The cluster's git remote is named `github`, not `origin`.** `git fetch origin` fails outright.
- **`python3` on the login node is 3.6** and cannot parse `wakerctl.py`. Use `/usr/bin/python3.11`, which is
  what the live cron entry already uses.
- **The main cluster checkout `/pscratch/sd/j/josephrb/MINERvA-OmniFold` has 727 porcelain entries**, including
  four MODIFIED TRACKED files belonging to other lanes (`p4_endpoint_evidence.json`, `p4_merged_audit.json`,
  `p4_standard_manifest.json`, `sessions.json`). **Do not clean it** — inventory first (`OI-130`'s ordering). A
  blanket clean deletes un-reproducible state. Use `fetch` and a detached worktree; never `pull`/`reset` there.
- **The controller refuses ANY porcelain output** in its code root, which is why deployments are detached
  worktrees named `gate5-data-only-frozen-<sha7>`. Do not write paperwork into a freeze.
- **`myquota`, not `df`**, for home: `df` reports the raw filesystem (22.8 TiB), the quota is 40 GiB.
