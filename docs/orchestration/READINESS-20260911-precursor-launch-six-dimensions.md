# READINESS 2026-09-11 — independent end-to-end launch-readiness check of the Z unified-throw
# precursor, on Joseph's six named dimensions

**CITABLE FOR:** the six verdicts in §1 and the measurements behind them in §2–§8, each with its site,
command or fixture.
**NOT CITABLE FOR:** any launch authorization, any compute, any adoption, any grade, any gate movement,
or any significance. **This is a readiness finding, not an approval.** Endpoint B remains DEFERRED NOT
PASSED; `R4` suspended; Gate 2 FAIL; historical scans closed. Nothing was launched — every cluster
action was a read.

**Subject:** a precursor producing Z's own unified throw (`SPEC §1.3a`, *"Z derives its own"*) then a
1-task assembly/spectrum pilot, at proposed caps of **100** and **6** CPU task-h which Joseph has
stated are **not yet launch authorizations**.

## 1. Verdict — NOT READY. One dimension certifiable, five with live defects.

| # | dimension | verdict |
|---|---|---|
| 1 | actual launchers / real populations | **CERTIFIED**, with two corrections (§2) |
| 2 | import closure, `sys.path[0]` ownership | **BLOCK** — the dump arm reproduces the OI-136 shape and has no guard (§3) |
| 3 | fresh output namespace | **BLOCK** — nothing is fresh, and a live glob mismatch reads 36 stale products (§4) |
| 4 | complete expected population | **BLOCK** — `--expected-ids` is absent from all four arms; the block population is asserted by nothing (§5) |
| 5 | receipt-last completion | **CANNOT BE CERTIFIED** — there is no separate receipt to order (§6) |
| 6 | resource enforcement incl. RUNNING | **BLOCK** — RUNNING *is* counted, but the cap arithmetic does not close (§7) |

**The requester expected to certify five and withhold one. The inverse is closer to the measurement.**
And its bounding conclusion is **correct**: the producer patch does not exist on any ref (§8), so the
final code does not exist and no dimension can be certified against it.

## 2. Dimension 1 — CERTIFIED, with two corrections

All four launchers exist on `main` with **exactly** the pinned specs, read from the scripts rather than
from `sacct` (the catalogued `3-100`-for-`1-100` hazard is avoided by never consulting a bracket):

| launcher | job-name | `--array` | tasks | constraint | mem | time |
|---|---|---|---|---:|---|---|
| `sbatch_uthrow_dump_5d.sh` | `uthrow5d_dump` | `0-7` | 8 | **cpu** | 110G | 06:00:00 |
| `sbatch_uthrow_block_5d.sh` | `uthrow5d_block` | `0-20%10` | 21 | **cpu** | 80G | 12:00:00 |
| `sbatch_uthrow_run_5d_fast.sh` | `uthrow5d_runF` | `0-39%40` | 40 | **cpu** | 90G | 06:00:00 |
| `sbatch_uthrow_combine_5d_fast.sh` | `uthrow5d_combF` | none (single) | 1 | **cpu** | 90G | 03:00:00 |

**70 CPU tasks, 0 GPU — confirmed**, every arm `--constraint=cpu`.

**Correction A — the dump arm runs a DIFFERENT producer.** `sbatch_uthrow_dump_5d.sh:14` invokes
**`unified_throw.py --dump`**, not `unified_throw_cov_5d.py`. The launcher-to-producer mapping is
therefore not one-to-one, and every statement made about "the producer" applies to three arms, not four.

**Correction B — 24 `sbatch_uthrow*` siblings exist, and two are near-name.** No glob-based dispatcher
was found, and job names discriminate (`uthrow5d_run` vs `uthrow5d_runF`; `uthrow5d_comb` vs
`uthrow5d_combF`). All siblings are `--constraint=cpu`, so **no resource-class flip is possible.** But
`sbatch_uthrow_run_5d.sh` declares `--array=0-19%10` and `--time=12:00:00` against the fast arm's
`0-39%40` and `06:00:00` — selecting the wrong one changes **both the population (20 vs 40) and the
time ceiling (12 h vs 6 h)**, which is a budget fact, not only a naming one.

## 3. Dimension 2 — BLOCK: the dump arm is the OI-136 shape, in the one arm with no guard

**The three `uthrow_cov` arms pass.** Import closure resolves in the tracked tree —
`flux_universe.py`, `seed_offset_policy.py`, `compare_unified_throw.py`, `uq_math.py` all present; and
`sys.path[0]` is **derived**, `_REPO = Path(__file__).resolve().parents[1]`, with **no absolute
fallback**, which is the OI-136 repair. Each of the three carries the guard, the inventory pin and the
member gate:

```
sbatch_uthrow_block_5d.sh        GUARD=7  mnv_inv=3  mr_require_valid_offset=1
sbatch_uthrow_run_5d_fast.sh     GUARD=6  mnv_inv=2  mr_require_valid_offset=1
sbatch_uthrow_combine_5d_fast.sh GUARD=6  mnv_inv=2  mr_require_valid_offset=1
sbatch_uthrow_dump_5d.sh         GUARD=0  mnv_inv=0  mr_require_valid_offset=0
```

**`sbatch_uthrow_dump_5d.sh:12-14`:**

```bash
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
python3 unified_throw.py --dump ...
```

**It hardcodes an absolute root, `cd`s into it, and runs a bare `python3`, so `sys.path[0]` is that
tree** — the pscratch data root — **regardless of `MNV_CODE_ROOT`.** This is precisely the defect the
5D shim's own comment describes: *"An absolute `insert(0, …)` executes THAT tree's modules whichever
checkout launched this entrypoint, and `PYTHONPATH` cannot outrank position 0 — so deployment parity
can report every pinned file CURRENT while the interpreter imports a different file entirely. That is
OI-136's measured cause on run `57266000_0` (3 h 08 m of A100 against a tree 211 commits behind)."*

**Achieved by `cd` rather than by a Python insert, and therefore invisible to a search for the repaired
idiom** — which is why the repair swept the inserts and left this arm standing. It is also the **only**
arm with `GUARD=0`, so the check designed to catch exactly this is absent where it is needed.

**A second, related gap.** `unified_throw_cov.py:63-68` justifies its gigabyte gitignored argparse
defaults on the ground that *"every launcher on the k=0 path passes them explicitly from
`${MNV_DATA_ROOT}`"*. Measured `DATA_ROOT` references: block **5**, runF **5**, combF **5**, **dump
0**. The invariant that note relies on does not hold for the dump arm.

## 4. Dimension 3 — BLOCK: no namespace is fresh, and one glob reads stale products silently

Measured on the cluster with **absent distinguished from empty**, because a bare count conflates them:

| namespace | state | products | newest mtime |
|---|---|---:|---|
| `uq_5d/block_slabs_5d` | EXISTS | **8** npz | 2026-07-13 |
| `uq_5d/block_slabs_5d_sb` | EXISTS | **36** npz | 2026-07-13 |
| `uq_5d/uthrow_slabs_5d_sb` | EXISTS | **40** npz | 2026-08-06 |
| `uq_5d/uthrow_slabs_5d` | EXISTS | **160** npz | 2026-07-12 |
| `nd-unfolding/bank_uthrow_5d` | EXISTS | **374** files | 2026-06-30 |

**Not one target namespace is fresh.** The dump arm's `--bankdir bank_uthrow_5d` holds 374 files from
June.

**And a live namespace mismatch on the undeclared path.** `sbatch_uthrow_block_5d.sh` writes
`uq_5d/block_slabs_5d_sb` when a member is declared (`:318`) but **`uq_5d/block_slabs_5d` when it is
not** (`:320`), while `sbatch_uthrow_combine_5d_fast.sh:333` reads
`mr_dir_prefix uq_5d/block_slabs_5d_sb` **unconditionally** — and `mr_dir_prefix` returns its argument
unchanged when undeclared (`lib_member_resume.sh:145-149`). Measured globs today:

```
block_slabs_5d_sb/block5d_*.npz  -> 36 matches   <- what the combine WOULD read
block_slabs_5d/block5d_*.npz     ->  8 matches   <- where the block leg WOULD write
```

**So an undeclared precursor's combine would consume 36 July products and never see its own 21 fresh
slabs — and because the glob matches, it does not fail closed.** The launcher's own comment
(`:321-331`) states this, records that namespacing *"DOES NOT"* resolve it, that for members it is
*"FATAL FOR EVERY MEMBER … Loud, but a total scan failure"*, that *"an UNDECLARED run reads exactly what
it read before"*, and that **"WHICH NAMESPACE IS CANONICAL IS STILL OPEN."** The loud branch is the
member branch; **the precursor is the silent one.**

**On `mii/`:** it exists with 3 subdirs. Nothing can land there **only if `MNV_EST_SEED_OFFSET` is
unset**, since `mr_dir_prefix` inserts the member component only when declared. That makes the
requirement **conditional on undeclaredness**, and it rests on the same `mr_declared()` conflation
already on record — one predicate meaning both *"member of K"* and *"build your own blocks"*. **It
should be enforced by a refusal, not assumed.**

## 5. Dimension 4 — BLOCK: `--expected-ids` is absent, and the block population is asserted by nothing

**`--expected-ids` occurs ZERO times in all four launchers.** The mechanism named in the request is not
the mechanism these arms use. What exists is in the combine only:

```
--expected-throws 0-159          # 160 throws, asserted
--block-slabs "${BLOCK_DIR_SB}/block5d_*.npz"    # a bare glob, NO expected count
```

- **Throws: asserted.** `0-159` against a 40-task array implies 4 throws per task. Today the read
  namespace holds 40, so this check *would* currently fail closed — the one working assertion in the
  chain.
- **Blocks: asserted by nothing.** A short block arm yields a glob that matches fewer files, and the
  combine proceeds. Combined with §4's mismatch, the failure is not merely silent but **actively
  wrong**: it matches 36 files from a different campaign.
- **Dump (`0-7`): asserted by nothing.**

`unified_throw_cov_5d.py` is a 93-line monkeypatching shim with no `add_argument` of its own, so the
declared-set machinery must come from `unified_throw_cov.py`; no block-population validator was found
there.

## 6. Dimension 5 — CANNOT BE CERTIFIED: there is no separate receipt to order

- **No `os._exit` in either producer entrypoint**, so the bypassed-`finally` hazard does not arise here.
- Provenance is written **inside the product**: `unified_throw_cov.py:550-579` writes `n_throws`,
  `estimator_seed`, `draw_seed`, `est_seed_offset_declared`, `est_seed_offset` as ROOT `TParameter`s
  into the product file, and `_atomic_savez` (`:132-142`) writes a temp then renames for the npz.
- **So "a receipt can never attest to a product that does not exist" holds structurally — but
  vacuously.** It holds because there is **no separate receipt artifact for these arms**, not because
  an ordering was enforced. **If the requirement is a run receipt, it does not exist**, and the
  dimension is not satisfied; it is inapplicable. The in-product `TParameter`s are good provenance and
  should not be confused with a receipt.

## 7. Dimension 6 — RUNNING *is* counted; the exposure is different, larger, and the cap does not close

**The feared mechanism is REFUTED, by fixture rather than by docstring.** `_parse_sacct_start`
(`r5_meter.py:214-224`) returns `None` only for `{"", "Unknown", "N/A", "None"}` **in the `Start`
field**; a RUNNING attempt has a `Start` and `End = Unknown`. Fixture — one COMPLETED (3600 s), one
RUNNING (7200 s, `End=Unknown`), one PENDING (`Start=Unknown`):

```
cpu_task_hours : 3.0          (= 1.0 COMPLETED + 2.0 RUNNING)
attempt_count  : 2
by_state       : {'COMPLETED': 1, 'RUNNING': 1}
```

**RUNNING attempts are charged; PENDING are skipped.** So the aggregate cap cannot be overshot by an
*uncounted* in-flight population.

**The real exposure, which is larger.** The meter charges **elapsed-so-far**, not the **committed**
allocation. At `%40` throttling with `--time=06:00:00`, the in-flight population's unspent allocation
at the moment a cap is neared is up to **40 × 6 = 240 CPU task-h** (≈35.3 h at the measured
`0.8824` h mean). **R5 contemplates this** — *"jobs running at the stop run to completion, spend
counted; no new submission after the stop"* — so it is the ruling's design, **not a meter defect**. But
it means **a 100 task-h cap cannot be enforced by a spend check alone**; it needs a submission-side
bound on committed time.

**And the cap arithmetic does not close:**

```
MEASURED    block  21 x 1.1213 h =  23.55
            runF   40 x 0.8824 h =  35.30      subtotal 58.84
UNMEASURED  dump    8 x 6.00 h  =  48.00       (--time ceiling)
            combF   1 x 3.00 h  =   3.00       (--time ceiling)
WORST CASE                       = 109.84 CPU task-h   vs the proposed cap of 100
```

**Over by 9.84 task-h.** The two unmeasured arms are bounded only by `--time`, and the **dump arm alone
carries 48 h of it** — the same arm that fails §3. Either the dump arm is measured first, or its
`--time` is reduced, or the cap is raised knowingly. **A cap whose own worst case exceeds it is not an
enforceable cap.**

**Basis, carried from this lane's earlier finding:** `r5_meter.py:_sacct_argv()` emits a **naive**
`--starttime` that `sacct` parses in the host timezone (uniformly PDT), so a cap enforced on that basis
**under-reads** spend — today by `0.4858` task-h and 62 attempts. Operative UTC-basis spend is CPU
**15.4231**, GPU **0.0**, headroom CPU **≤ 484.58**.

## 8. The OPEN item — the absence claim is CONFIRMED, by a different method

The requester asked to be told if it had missed the patch, and named its own search (path history plus
an all-refs commit-subject grep). **This lane used a different method deliberately: a content search of
every distinct blob, with a positive control.**

- **4 distinct blob versions** of `nd-unfolding/unified_throw_cov.py` exist across all `refs/heads`,
  `refs/remotes` and `refs/tags`.
- **All four have ZERO mask-write hits** (`mask.*\.Write|Write.*mask|support_mask|hmask|savez.*mask|
  cv_exec`), and each mentions `mask` **exactly once**.
- **Positive control:** the same query on `eavailW_covariance.py` at `main` returns **3** — so the query
  detects the pattern where BEN-450 did land.
- **None of the producer's imports writes one either** — `flux_universe`, `seed_offset_policy`,
  `compare_unified_throw`, `uq_math`.

**The site, and why it is the right site.** `unified_throw_cov.py:368-372`:

```python
# CV xsec (reported-bin mask)
x_cv = _xsec_for_weights(...).ravel(order="C")
rep = x_cv > 0
base = x_cv[rep]
nrep = int(rep.sum())
```

The mask is **computed, consumed, and discarded**. And the substantive point, which strengthens
Joseph's correction rather than restating it: **`rep = x_cv > 0` defines support as *strictly
positive*, so a pinned-zero bin is EXCLUDED from `rep`.** The distinction between a genuinely absent
operand and a pinned zero therefore lives **exactly** in this mask — and this mask is the thing not
persisted. *"A pinned-zero inflation bin is not a null operand"* is not a general caution here; it
names this line.

**So: seed provenance is present** (`3dd5e66e` splitting `--draw-seed`/`--estimator-seed`, and
`:569-575` writes both plus the offset pair into the product), **the CV-execution and support-mask
record is absent**, the BEN-450 pattern exists on `main` as a template in a **different** producer, and
the integration fixture (precursor output accepted by the Z reader) was not found. **The requester's
bounding is correct.**

## 9. What this check did not do

It authorized nothing, launched nothing, submitted nothing, implemented nothing, adopted nothing, and
moved no gate. It read `main` at `6f24fb00`, ran `r5_meter.py --self-test` (**PASS**) and one local
fixture, and read the cluster. **It did not execute any launcher, did not verify the three
`uthrow_cov` arms' guards actually fire at runtime** (their presence is measured, their firing is not),
and **did not price the pilot's 6 CPU task-h cap** — only the 100. **The decisions are Joseph's.**
