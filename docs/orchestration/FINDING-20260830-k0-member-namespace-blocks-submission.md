# FINDING 2026-08-30 — the k=0 member namespace still holds the `aa67c426` rehearsal's complete
# products, and that makes the seven arms unsubmittable as specified

**CITABLE FOR:** the measured state of `nd-unfolding/mii/member_k000000/` in the data root on
2026-08-30, the measured resume-guard mechanism that acts on it, the arm-by-arm consequence of
submitting the seven arms against it, and the fact that **no `sbatch` was issued**.

**NOT CITABLE FOR:** any gate movement; any claim that Gate 1 round 2 was wrongly graded; any claim
that the F-17(a) operands are stale; any defect finding against the four repaired F-17(b) surfaces or
the 2026-08-30 Step-3 **FIT**; leg 6; any member `k != 0`; the M(ii) family; covariance construction
or adoption; or a publication claim. Gate 2 remains **FAIL** for the `aa67c426` rehearsal. Nothing
here authorizes a disposition of any product.

## 0. Why this document exists instead of a submission record

This lane is `claude-school`, the named rehearsal producer of §4 of
`PROPOSAL-20260830-forward-only-rehearsal.md`, and the producer that filed the deployment at
`3994b4c6`. It was tasked to execute step 4 of the §9 sequence — submit the seven bounded arms for
run `k0-7ac0edec-20260830T000215Z` — after all three step-3 conditions passed.

**All three conditions do pass, and the preflight re-verifies clean (§1). The submission was still
not made**, because a precondition that no gate measures and that the proposal never mentions is
false: the seven arms' products from the previous, Gate-2-**FAIL** `aa67c426` rehearsal are still in
place in the member namespace, complete, and stamped with markers that match this run's declared
offset. Submitting against that state cannot produce the run-bound operands the rehearsal exists to
create (§2–§4), and the remedy is outside this lane's delegation (§5).

## 1. Preflight re-verification — all PASS, including the 726

Re-measured by this lane rather than inherited. Submitting host `login23`
(`ssh -n -o BatchMode=yes -o ConnectTimeout=30 saul.nersc.gov`), `GIT_OPTIONAL_LOCKS=0`,
`GIT_PAGER=cat`, `PAGER=cat`. Nothing was written to either protected tree.

| property | required | measured 2026-08-30T15:06:16Z–15:06:56Z | result |
|---|---|---|---|
| deploy HEAD | `7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b` | same | PASS |
| deploy detachment | detached | `symbolic-ref -q HEAD` rc=1 | PASS |
| deploy porcelain | 0 | 0 | PASS |
| deploy source dir modes | `dr-xr-x---` | 184 dirs, all `dr-xr-x---` | PASS |
| deploy regular file modes | `-r--r-----` | 1638 `-r--r-----`, 165 `-r-xr-x---` (executables; no write bit) | PASS |
| `.git` mode | `drwxrwx---` (§11.1.1 forbids read-only) | `drwxrwx---` | PASS |
| writable source paths | 0 | 0, by independent `-writable` walk pruning `.git` | PASS |
| measurer `measure_m1_m6.py` | `ce52ff77…3ed51` | same | PASS |
| comparator `compare_m1_m6.py` | `28490539…65242` | same | PASS |
| expected differences | `13547f3f…5efc2c` | same | PASS |
| canonical HEAD / branch | `32e403b8…`, `main` | same | PASS |
| **canonical porcelain** | **726**, matching the committed recapture operand | **726**, 726 untracked, 0 modified | **PASS** |
| canonical status digest | — | sha256 `d429f0f3daa5efe43519b1ccf02614f50fe1c45a2c837a5f4fbb94d6bc08146a` | see below |
| queue | only the waker cron | `57712764 WAKER_STATE_DI PENDING`, nothing else | PASS |
| pscratch | ~80% | 17173163560 / 21474836480 KiB soft = **79.97%** | PASS |

The canonical status digest is **byte-identical** to the one the Gate-1 round-2 grader measured at
`09:49:32Z` and again at `10:11:11Z`. So the quiesce of
`FREEZE-20260830-canonical-quiesce-k0-7ac0edec.md` held for the full 5 h 15 m to this read: the
population did not merely re-count to 726, it is the same 726 paths. **F-17(a)'s operand still
describes its subject.** The three step-3 conditions are also confirmed present and committed:
Step-3 full-chain **FIT** at `974f3ddd`, §10.1 readiness **PASS**, Gate 1 **PASS 18/18** at
`22fc4e84`.

**Nothing in §2 below contradicts any of that.** The blocker is in the **data root**, which no
Gate-1 clause and neither F-17 operand measures — `M-4` measures the two *checkouts*, and the review
contract names `mii/member_k000000/` only once, at `:173`, as an example of a CWD-relative output
path. This is a gap in the pre-submission checklist, not an error by any grader.

## 2. The measured state of the member namespace

`MNV_EST_SEED_OFFSET=0` resolves, through `mr_prefix` in
`nd-unfolding/lib_member_resume.sh`, to `mii/member_k000000` under the data root
`/pscratch/sd/j/josephrb/MINERvA-OmniFold`. Measured there 2026-08-30, total 2.6 GB:

| directory | contents | `.done` markers | modes |
|---|---|---:|---|
| `boot_nd_5d/` | 100 `.npz` | **100** | — |
| `seedscan_split_5d/` | 24 `.npz` | **24** | — |
| `uq_5d/universe_sweep_bkgaware/` | 188 `.root` | **19** | 188 `-rw-r-----`, 19 `-rw-rw----` |
| `uq_5d/uthrow_slabs_5d_sb/` | 40 `.npz` | 0 | 40 `-rw-------` |
| `uq_5d/block_slabs_5d_sb/` | 21 `.npz` | 0 | 21 `-rw-------` |
| `uq_5d/unified_throw_cov_5d.root` | 1 file, 2 668 024 337 B, 2026-08-25 | 0 | — |

**These are the `aa67c426` rehearsal's products, and the attribution is measured, not inferred.**
`sacct -X` on the seven arm ids recorded in `state/k0r2-*-active-*.json` returns every arm complete
at its full population on 2026-08-24:

```text
57527866  100 boot5dG         COMPLETED
57527869   24 ssplit5d        COMPLETED
57527870   19 det5dBKG        COMPLETED
57527872   40 uthrow5d_runF   COMPLETED
57527873   21 uthrow5d_block  COMPLETED
57527874  169 sweep5dBKGrun   COMPLETED
57527875    1 uthrow5d_combF  COMPLETED
```

Those populations reconcile with the files exactly, including the one non-obvious sum: the 188
`.root` files are **19 detector + 169 sweep**, because
`sbatch_unfold_5d_detector_bkgaware_gpu.sh:285` and
`sbatch_sweep_bank_5d_run_bkgaware_gpu.sh:278` write into the *same* `universe_sweep_bkgaware`
directory, and only the detector marks completion — which is also why there are 19 markers and not
188. The markers name their producing jobs directly:

```json
{"output":"mii/member_k000000/boot_nd_5d/res_boot_1.npz","size":92693,
 "marked_at":"2026-08-24T15:07:55Z","host":"nid001388","job":"57527867:1",
 "note":"est_seed_offset=0"}
```

**The `aa67c426` rehearsal's physics all ran and completed.** It failed on evidence clauses — the
three missing producer filings and F-17's `N1` schema mismatch — not on the legs.

## 3. The mechanism, measured

`mr_skip_if_complete` in `nd-unfolding/lib_member_resume.sh:164-207` reads the marker's `note` and
compares it to `mr_note()`, which for this run emits `est_seed_offset=0`:

```bash
note="$(sed -n 's/.*"note":"\([^"]*\)".*/\1/p' "$marker" 2>/dev/null)"
if [[ "$note" != "$want" ]]; then ... exit 3; fi
rg_skip_if_complete "$out" "$@"
```

A **different** offset, or an absent one, is a hard failure — that is the archive-handoff defect the
function was written to catch. **A matching offset is a skip.** Every marker on disk reads
`"note":"est_seed_offset=0"`, which is exactly what this k=0 anchor declares. So the guard does not
fire; it falls through and adopts.

Which arms carry the guard was measured per launcher, not assumed — and it is not uniform:

| arm | launcher | population | `mr_skip_if_complete` calls |
|---|---|---:|---:|
| 1 bootstrap | `sbatch_bootstrap_5d_gpu.sh` | 1-100 | 1 |
| 2 seed split | `sbatch_seedscan_split_5d.sh` | 1-24 | 1 |
| 3 detector | `sbatch_unfold_5d_detector_bkgaware_gpu.sh` | 0-18 | 2 (CV + universe) |
| 4 sweep | `sbatch_sweep_bank_5d_run_bkgaware_gpu.sh` | 1-169 | **0** |
| 5 uthrow run | `sbatch_uthrow_run_5d_fast.sh` | 0-39 | **0** |
| 6 uthrow block | `sbatch_uthrow_block_5d.sh` | 0-20 | **0** |
| 7 uthrow combine | `sbatch_uthrow_combine_5d_fast.sh` | single | **0** |

No force, redo, overwrite or no-skip override exists in either resume library or the launchers
(measured: a `MNV_*(FORCE|REDO|OVERWRITE|NOSKIP|IGNORE)*` search returns nothing).

## 4. Arm-by-arm consequence of submitting as specified

| arm | products present | consequence |
|---|---|---|
| 1 bootstrap | 100/100 + matching markers | **all 100 tasks skip.** Zero new products |
| 2 seed split | 24/24 + matching markers | **all 24 tasks skip** |
| 3 detector | 19/19 markers | **all 19 tasks skip** |
| 4 sweep | 169 `.root`, no markers, no guard | recomputes and **overwrites in place** |
| 5 uthrow run | 40 `.npz`, no markers, no guard | recomputes and **overwrites in place** |
| 6 uthrow block | 21 `.npz`, no markers, no guard | recomputes and **overwrites in place** |
| 7 combine | 2.67 GB output present, no guard | recomputes over overwritten inputs |

This fails the rehearsal in **two independent directions**, and clearing one does not clear the other:

1. **Arms 1–3 would produce nothing.** Their guard inventories would be emitted by new jobs at the
   new pin while every product they cover was built under the failed candidate `aa67c426`. That is a
   cross-run, mixed-pin record. §7 lists "cross-run inventory" and "mixed-pin" as **abort**
   conditions and requires "all expected outputs and `.done` markers bound to this run and pin"; §8
   rules out exactly this object — *"paperwork written around the old seven jobs would be backfill
   rather than a new forward-only rehearsal."*
2. **Arms 4–6 would destroy evidence.** They overwrite, in place, the products of a rehearsal whose
   Gate 2 is **FAIL** and whose record is still the campaign's account of that failure. The campaign
   has ruled twice on this class of file and both times the disposition was a same-filesystem
   **move**, never a destruction —
   `state/RECEIPT-20260822-quarantine-member-k000000-stale-replicas.json` and
   `state/RECEIPT-20260823-quarantine-k0-failed-rehearsal.json`.

The proposal's own cost model corroborates that it assumed an empty namespace: §6 budgets 14.00
A100-h for the 100 bootstrap replicas and §8 totals 52.07 A100-h + 47.12 CPU-h. If 143 of the 273
array tasks skip, those figures are not the cost of anything. **And the proposal never raises the
question at all** — a search of it for `quarantin|resume|skip|existing product` returns **zero**
matches.

There is also no route around this by relocating the namespace. `mr_prefix` can only emit
`mii/member_k<offset>/…`, so the only way to reach a fresh member directory is a different
`MNV_EST_SEED_OFFSET`, which would be a different M(ii) member and is expressly prohibited. A fresh
data root is not available either: the legs read ~560 GiB of universe inputs on that tree (`OI-174`),
and pscratch is at 79.97%.

## 5. Why the remedy is not this lane's to apply

The precedent for this exact namespace is unambiguous, and in both instances the authority was
Joseph, per instance, naming the exact file set:

- 2026-08-22, six files: *"quarantine, do not delete and do not reuse. Move exactly those six files
  to a recoverable location outside every production and resume glob…  No other file may be moved or
  removed under this authorization."*
- 2026-08-23, the exact union of 415 products and 123 markers, whose receipt states the hazard in the
  same terms this finding measures: *"Left in place, 123 tasks of the rerun would have SILENTLY
  SKIPPED and the fresh single-SHA run would have reused products built under the defective sha."*
  Its `not_authorized` list includes *"reusing these products in the eventual accepted member"* —
  which is precisely what arms 1–3 would do.

`DECISION-20260830-joseph-accept-forward-only-rehearsal.md` delegates **the §9 sequence and nothing
wider**: *"The delegation is scoped to this sequence, the one enumerated in §9 of the proposal. It is
not a general grant."* None of §9's six steps is a disposition of pre-existing products, and the
standing per-arm compute delegation is about GPU/CPU-hours, not about moving 600 files out of the
data root. Ruling 12's prohibition on marker backfill points the same way.

**The two available routes are both decisions, not executions:**

- **(a) Authorize a quarantine** of the k=0 member products on the 2026-08-23 pattern — a
  same-filesystem move to a recoverable location outside every production and resume glob, with a
  per-file digest ledger — then submit the seven arms against an empty namespace, which is the state
  §6's estimates and §8's cost model assume. This is the route with precedent. It needs an
  authorization naming the file set.
- **(b) Rule that resume-adoption is acceptable**, which requires amending §7's terminal conditions
  (the run-bound-marker, cross-run-inventory and mixed-pin clauses) and answering §8's question about
  how an old-run product can satisfy the new pin without backfill. §8 says a lane must not partially
  execute the proposal under that reading, and that the ruling comes first.

This finding does **not** recommend between them, and it does not treat (a) as pre-approved because
it has precedent.

## 6. What this lane did and did not do

- **Did not** issue any `sbatch`, `srun`, `scancel`, `scontrol`, `scrontab` or any other scheduler
  write. The queue holds only the pre-existing waker cron.
- **Did not** run leg 6 / `fin5dBKG`, any member other than the k=0 anchor, or any family work.
- **Did not** delete, move, overwrite or modify any product, marker or intermediate, including the
  41.44 GB combined intermediate (which is not under the member namespace; the member totals 2.6 GB).
- **Did not** write into the deploy tree or the canonical checkout. All cluster reads used
  `GIT_OPTIONAL_LOCKS=0`; the canonical status digest is unchanged after this lane's work.
- **Did not** move a gate, adopt anything, file Gate-2 evidence, or retake or regenerate any F-17
  operand.

## 7. One perishable claim in the runbook has flipped, in the direction nobody expected

`RUNBOOK-20260822-b1-lift-preflight.md` §6b names *"no member is runnable"* as a claim that expires,
records it as **two** independent refusals — `:167` finding 3 of 100 bootstrap replicas and `:168`
finding 0 of 24 seedscan splits with `seedscan_split_5d/` absent entirely — and instructs a later
lane to **re-measure both rather than inherit the row**. Re-measured here: **100 of 100** and **24 of
24**, and `seedscan_split_5d/` is present. §6b anticipated a lane clearing `:167` and dying on
`:168`; what actually happened is that the failed rehearsal satisfied both.

**So `fin5dBKG`'s two documented validators would now pass.** That makes the leg-6 prohibition more
load-bearing than when it was written, not less: leg 6 is gated behind Gate 2 and behind one member
completing end to end, and the fact that its inputs are now present is a consequence of the failed
rehearsal, not evidence that it may run. It was not run.

## 8. What this finding does not establish

- Not that Gate 1 round 2, the §10.1 readiness verdict, or the Step-3 **FIT** are wrong. Each is
  sound on its own subject; none has the data root as its subject.
- Not that the F-17(a) operands are stale. Measured here: they still describe their subject.
- Not any result about the `aa67c426` products, whose Gate-2 disposition is **FAIL** and unchanged.
- Not that route (a) or (b) is correct, and not an authorization for either.
- Not that the seven arms are unsubmittable in principle — only that they are unsubmittable **as
  specified, against this namespace state**, without a decision on the products.
