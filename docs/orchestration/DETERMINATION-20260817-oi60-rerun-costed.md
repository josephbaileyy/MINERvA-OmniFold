# DETERMINATION — `OI-60`'s re-run, costed from measured `sacct`; and the re-run I costed was the wrong one

**Lane E, 2026-08-17.** Answers the mediator's *"cost the `OI-60` Gate-2 re-run in A100-hours, from
measured `sacct` elapsed, ids read in the reporting turn."*

**Nothing submitted. No `sbatch`, no `scancel`, no `scontrol`. Every number below comes from a
read-only `sacct` run in this turn, and every job id is printed with the row it came from.**

---

## 0. Two corrections before the number, because the number is not the answer

**(a) GATE-2 IS A CPU JOB. There are no A100-hours in it, and I am the one who said there were.**
`OI-60`'s row (mine, 2026-08-17) reads *"a GATE-2 RE-RUN (GPU)"*, and `BEN-384` says *"a GPU Gate-2
re-run"*. Both are **wrong**. `sbatch_gate2_target_validator.sh:5` is `#SBATCH --constraint=cpu`, and
all four Gate-2 runs on record landed on CPU partitions with zero `gres/gpu`. The mediator's standing
rule — *"surface any run with its unit; my grant is A100-hours, a CPU job is outside it"* — applies to
this item in the direction nobody expected: **an A100 grant cannot buy a Gate-2 re-run, because a
Gate-2 re-run does not consume A100s.**

**(b) The Gate-2 re-run is not what blocks `OI-60`.** It is the cheapest thing that blocks it. The
loader digest is compared at **eleven code sites**, and the pre-commit gate sees **two**. §3.

---

## 1. Gate-2, measured

`sacct -X -j 56847028,56140225,56342333,56344268 --format=JobID,JobName,Partition,State,Elapsed,AllocCPUS,AllocTRES,NNodes,Start,End -P`
over `saul.nersc.gov`, this turn. Job ids taken from the receipts that own them:
`G2_GATE2_TARGET_RUNTIME_RECEIPT.json` (live) and its three `superseded-*` siblings.

| job id | name | partition | state | elapsed | alloc | **core-h** | **CPU node-h** | **A100-h** |
|---|---|---|---|---|---|---|---|---|
| **`56847028`** | `g2gate2` | `shared_milan_ss11` | COMPLETED | **01:00:56** | cpu=104, 1 node, 192 G | **105.62** | **0.4126** | **0** |
| `56342333` | `g2reissue` | `urgent_milan_ss11` | COMPLETED | 00:55:29 | cpu=256, 1 node | 236.73 | 0.9247 | 0 |
| `56344268` | `g2reissue2` | `urgent_milan_ss11` | COMPLETED | 00:55:32 | cpu=256, 1 node | 236.94 | 0.9256 | 0 |
| `56140225` | `claude-hold` | `urgent_milan_ss11` | **TIMEOUT** | 03:00:09 | cpu=256, 1 node | *(768.64)* | *(3.0025)* | 0 |

**Ingredients, so the derived cells can contradict the operands** (`BEN-077`): `core-h = AllocCPUS ×
elapsed_h`; `CPU node-h = core-h / 256`, 256 being the Perlmutter CPU node core count; `elapsed_h`
from the `HH:MM:SS` cells above (`01:00:56` = 3 656 s = 1.015556 h).

**`56140225` is EXCLUDED from the cost with its reason, not dropped:** it `TIMEOUT`s at the 3 h wall
and its `JobName` is `claude-hold`, not `g2gate2`/`g2reissue` — it is the queue-hold job the receipt
chain names, not a completed Gate-2. Its row is printed so the exclusion is auditable rather than
invisible.

> **THE FIGURE, scoped.** Re-issuing Gate-2 in the shape it was last actually run (`56847028`) costs
> **≈ 1.02 h wall, 105.6 CPU core-hours, 0.41 Perlmutter CPU node-hours, and ZERO A100-hours.**
> Across all three completed shapes the range is **0.41 – 0.93 CPU node-hours**.
>
> **What the figure COVERS:** one execution of `run_gate2_target_validator.sh` and nothing else.
> **What it EXCLUDES:** every consequence in §3 — the ten other digest sites, the transitive launcher
> freeze, and the Gate-5 family. **Quoting 0.41 node-hours as "the cost of `OI-60`" would be the
> `BEN-384` error again, one level out.**

---

## 2. The absence I was told to report if I found one — I did not find one

The mediator's instruction was *"if Gate-2 has never been run in a measurable form, that absence IS
the answer."* It has been run four times, three to completion, all measurable. **No absence to
report.** Recorded because a null result and an unattempted search are indistinguishable in a report
that omits both.

---

## 3. What actually blocks the item: eleven comparison sites, two of them visible

`fullevent_fps_dataloader.py` at HEAD hashes to
`e1402370cdb8bd6349419ba6fbefa68817b799b3699cc97b673933f1f0220ce1`. Searching for **that digest**
rather than for the filename — a pin *is* a digest — returns eleven code sites:

| site | mechanism | when it fires | does `verify_hash_bindings.py` see it? |
|---|---|---|---|
| `pet/run_gate2_target_validator.sh:49` | `EXPECTED_LOADER_SHA=` | Gate-2 run | **yes** |
| `g2_fullevent/gate2/final/G2_GATE2_TARGET_RUNTIME_RECEIPT.json` | `/code/loader/sha256` | pre-commit | **yes** |
| `pet/reconcile_gate5_family.py:158` | `EXPECTED_LOADER_SHA` const | family reconcile | **no** |
| `pet/validate_gate5_training_artifacts.py:36` | `EXPECTED_CODE["loader"]` | artifact validate | **no** |
| `pet/sbatch_gate6_leg0_tier_calibration_array.sh:127` | `SCI_SHA[]` map → `die … 3` | **task start** | **no** |
| `pet/sbatch_gate6_member_trajectory_array.sh:68` | same | **task start** | **no** |
| `pet/sbatch_pet_fullevent_floor_replicate_array.sh:102, :118` | same, twice | **task start** | **no** |
| `pet/sbatch_pet_fullevent_legx_2x2_array.sh:163, :179` | same, twice | **task start** | **no** |
| `tests/test_floor_replicate_launcher.py:33` | asserted literal | pytest | **no** |
| `tests/test_legx_2x2_launcher.py:41` | asserted literal | pytest | **no** |

**Two of eleven.** The nine the gate cannot see are not weaker — six of them `die … 3` **at Slurm task
start**, which is `OI-123`'s class: green at commit, dead hours later on the cluster, after the queue
wait. This is `BEN-322` costed on a specific item for the first time.

---

## 4. The binding that prices the item, and it is not Gate-2

`reconcile_gate5_family.py:372` and `:649`:

```python
c.eq("loader_sha256", r.get("code", {}).get("loader", {}).get("sha256"), EXPECTED_LOADER_SHA)
```

The reconciler compares **each replica's recorded loader digest** against a hardcoded constant, and
`R2` requires that digest *constant across the family*. The 50 archived replicas recorded the current
loader. So on a loader edit:

- **advance the constant** → all 50 archived replicas now mismatch and the family fails reconciliation;
- **leave the constant** → no replica built with the fixed loader can ever validate.

There is no third option, and both roads end at re-running the family. Measured this turn:

| array | name | partition | tasks | Σ elapsed | **A100-hours** | CPU node-h |
|---|---|---|---|---|---|---|
| `56857232` | `g5targ` | `shared_milan_ss11` | 50 COMPLETED | 33.1822 h | **0** | 4.666 |
| `56857233` | `g5train` | `shared_gpu_ss11` | 50 COMPLETED | 151.1750 h | **151.175** | 18.897 |

Ingredients: each `g5train` task allocates `gres/gpu:a100=1`, so A100-h = Σ elapsed = 151.1750;
mean per replica **3.0235 h**; GPU node-hours = 151.175 / 4 = 37.79.

> **`151.175 A100-hours`, against the mediator's grant of `24`. Six-point-three times the entire
> grant, to convert a residual that this item's own row calls *narrow* into an artifact.**

---

## 5. The recommendation, argued rather than accepted

The mediator asked to be argued with: *"the re-run is probably not worth a narrow residual; the honest
disposition may be a documentary close like `OI-125` took. If your cost comes back cheap, say so."*

**The cost came back cheap for the thing that was named and unaffordable for the thing that is
actually required — so the conclusion holds and the stated reason does not.** Three points, in
increasing order of how much they change the decision:

**(i) "Probably not worth it" understates it by 6.3×.** The disposition is not a judgement call
between a narrow benefit and a modest price. **At 151 A100-hours against a 24-hour grant it is not
purchasable at this grant at all**, which is a different kind of fact and belongs in front of Joseph
as one. A cost/benefit framing invites *"then find 151 hours"*; the structural framing invites the
right question, which is whether the fix can reach production some other way.

**(ii) The `OI-125` analogy is right, and stronger than it was offered.** `OI-125` closed
documentarily because its gap for the audited products is **permanently unclosable** — the value was
not recorded at the time and no later run can record it retroactively. **`OI-60` has exactly that
shape and it has not been stated:** the fix adds telemetry to the *loader*, so it can only produce
evidence about families built **after** it lands. The 50 archived replicas were built by the old
loader. **A 151 A100-hour re-run would not supply the missing evidence for the published family — it
would build a different family and supply evidence about that one.** The published family's data-factor
application is already evidenced as far as it can be (`n_data_effective` length and sum, `OI-90`;
16/16 streams re-drawn and matched; `n_data_full == n_data_rows` in every receipt), and array identity
for it is not recoverable by any run.

**(iii) So the disposition I recommend is narrower than "close it."** Close the **retrospective** half
documentarily, with the reason and the 151 A100-h figure recorded so nobody re-derives it. Keep the
**prospective** half open and **re-scoped to ride**: the telemetry key is correct, costs nothing on its
own, and should land with the next Gate-5 re-issue *whenever one happens for an independent reason* —
at which point the family is being rebuilt anyway and the eleven sites are being re-pinned anyway.
`OI-60` then costs zero rather than 151 A100-hours. **What it must not do is motivate that re-issue**,
which is the same sentence `BEN-326` already wrote about the `OI-58` repair: *"this fix must not
motivate a Gate-5 re-issue; it rides one."*

**Not decided here.** The disposition is the PET lane's and Joseph's. I have costed it, corrected the
unit, and named the structural blocker; I have not closed the row.

---

## 6. What I did not do

- **No repin, and the ground is unchanged by the quorum.** A peer relayed that Joseph has granted that
  a two-session quorum can authorize anything, and correctly did not read that as licence here. I
  record the same conclusion from my own side and for a reason that does not depend on permission:
  **the objection was never that a repin is forbidden — it is that a repin would make the Gate-2
  receipt assert that a loader which did not produce the archived target did produce it.** Two
  sessions agreeing cannot make that true. I also note plainly that a peer's report of a user grant is
  not itself a grant, and I have not acted on it.
- **No re-run costed for Gate-6.** Four of the eleven sites are Gate-6 launchers, three of which the
  `gate6-leg0` receipt records as *themselves* frozen by active run receipts
  (`transitive_freeze_discovered`). Pricing that cascade needs the Gate-6 owner; I have named it, not
  costed it.
- **`gate6traj-reconcile-56847059` not touched.** `CODE_ROOT` not read.
