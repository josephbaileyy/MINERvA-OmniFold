# Audit findings — can the FPS event-loop files be removed, deleted, or archived? (2026-08-20)

> **Scope.** The scientific- and preservation-removability question for the **extended-fiducial (FPS)**
> event-loop ROOT files on pscratch, seeded with the two objects flagged in
> `AUDIT-FINDINGS-20260820.md` §7. This is the sibling audit that §7 asked for; it is **not** the
> `bkgaware` pair-set audit, and it does not revisit that verdict.

**Read-only audit. Nothing was deleted, moved, or archived. No mutating `hsi` call was issued — every
cluster command was `find`/`stat`/`du`/`ls`/`sacct`/`squeue`/`hpssquota`/`hsi -q ls`/`hsi -q hashlist`/
`hsi -q hashverify`/`hsi -q dump`, all read-only.** No ROOT file was opened by this audit at all; the
dependency findings are from source text and committed receipts, not from reading the files.
Written 2026-08-20.

**Verdict in one line: NO for both named targets — and the framing is wrong twice over. The FPS family
is 1244.70 GiB across 58 files, not the 247.29 GiB in the seed; and the largest exposure (696.79 GiB,
sha256-bound in a committed receipt) is in neither the seed nor the trap glob it warns about.**

**This memo does not authorize deletion of anything. Deletion is Joseph's alone.**

---

## 0. Enumeration instrument, published so it can be falsified

```
find /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding -name "*FPS*.root" \
     -printf "%s\t%TY-%Tm-%Td %TH:%TM\t%p\n"     # login30, 2026-08-20, rc=0
```

**No `-maxdepth`** — this recurses, deliberately, because the seed's two objects live at the top level
and the biggest part of the family does not. A second pass rooted at
`/pscratch/sd/j/josephrb/MINERvA-OmniFold` (whole repo, not just `nd-unfolding`) returned no FPS `.root`
outside `nd-unfolding`.

**Result: 58 files, 1,336,485,096,491 B = 1244.70 GiB.** The seed's two objects are 265,520,433,671 B
= **247.29 GiB, i.e. 19.9% of the FPS family by bytes.**

| target | bytes | GiB | mtime |
|---|---|---|---|
| `runEventLoopOmniFold_5D_FPS_MEFHC_universes_full.root` | 192,868,793,175 | 179.62 | 2026-06-10 11:23 |
| `runEventLoopOmniFold_PC_FPS_MEFHC.root` | 72,651,640,496 | 67.66 | 2026-06-30 01:27 |
| **seed subtotal** | **265,520,433,671** | **247.29** | |

**Coverage limit, stated rather than buried.** `*FPS*.root` is a *name* filter. An FPS-derived object
that does not carry `FPS` in its filename is **not** in this enumeration — the `uq_fps/` product tree is
found by directory name, not by this glob, and non-`.root` FPS products (`of_inputs_fps.npz`,
`of_inputs_pc_fps_npy/`) were located by explicit `stat`, not by the glob. Treat the table above as
complete for **FPS-named ROOT files under `nd-unfolding`** and nothing wider.

---

## 1. The space case is weak, and that is the finding, not a caveat

`hpssquota`, 2026-08-20: pscratch **15.99 TiB / 20.00 TiB = 79.9%**. The seed set is 247.29 GiB
= 0.2415 TiB, so deleting **both** named targets moves pscratch to **78.7% — a 1.2 pp gain.**

The seed said the space case is weak and that I should say so if that is what I found. It is what I
found, and it is weaker than the arithmetic alone suggests, because the prior audit's §6 note still
holds: every large path's atime was reset by a tree walk at 2026-08-20 02:00–02:01, so NERSC's purge
timer carries **no disuse information right now** and "these are cold" is not currently measurable.

**The bytes that would actually matter are elsewhere** (§4): 696.79 GiB in one sha256-bound family.
If pscratch relief is the goal, the seed set is the wrong 247 GiB to be looking at.

---

## 2. Target 1 — `5D_FPS_MEFHC_universes_full.root` (179.62 GiB): RETAIN, on the strongest ground available

**A live, unstruck analysis-note number is derived from this file.** That alone ends the question under
the inherited burden of proof, and it is a *measured* chain, not an inferred one:

```
runEventLoopOmniFold_5D_FPS_MEFHC_universes_full.root          192,868,793,175 B, sole copy
  └─ sbatch_dump_fps_inputs.sh:19   --omnifile <this file>
       └─ of_inputs_fps.npz                                    1,282,852,815 B, sole copy, pscratch
            └─ uq_fps/corrected/coverage_valid_fps.json
                 truth = "fixed closure truth from of_inputs_fps.npz"      ← the file names its source
                 variant_B_split_ensemble.coverage_aggregate = 0.6867293233082706
                 variant_A_independent_cov.coverage_aggregate = 0.776296992481203
                 └─ docs/analysis-note/values.tex:29  \newcommand{\covFPS}{68.67}
                    docs/analysis-note/values.tex:31  \newcommand{\covFPSanalytic}{77.6}
                      └─ docs/analysis-note/sec_fps.tex:76,81   \SI{\covFPS}{\percent}, \SI{\covFPSanalytic}{\percent}
                           └─ docs/analysis-note/main_note.tex:79  \input{sec_fps}
```

**Checked that it is live, not struck.** `sec_fps.tex` contains four occurrences of the string `dead`
and **none is a `\dead{}` strike macro** — all four are the physics *dead region* (`\epsilon<2\%`
acceptance) at `:33`, `:38`, `:107`, `:125`. `\input{sec_fps}` at `main_note.tex:79` is uncommented.
So `\covFPS` = 68.67 and `\covFPSanalytic` = 77.6 are live note content today.

**Precision that matters, because the over-claim is available and wrong.** `sec_fps.tex` is `\input`
into `main_note.tex` **only**. `docs/analysis-note/paper_body.tex` contains **zero** occurrences of
`FPS` or `covFPS`. So this is a live **analysis-note** dependency, not an external-paper dependency.
That is still squarely inside the burden of proof ("no live claim, note/paper figure … may be derived
from them"), but it is the note, and the memo should not inflate it.

**Second axis — the file is a hard precondition of a 188-job array that is still in the tree.**
`sbatch_unfold_fps_universes_full.sh:28` sets `OMNIFILE="${ND}/runEventLoopOmniFold_5D_FPS_MEFHC_universes_full.root"`,
and `:36` is an abort:

```
[[ -s "${OMNIFILE}" ]] || { echo "[sbatch] FAIL: FPS universe omnifile missing" >&2; exit 2; }
```

`--array=0-187%32` (`:11`), index 0 the matched CV, 1–187 the universe list; output
`uq_fps/universe_sweep/`, which is present on disk with **188 entries**. Deleting the file does not
break a stale script — it converts a re-runnable systematic sweep into a dead end that fails loudly.

**`_REPO` is hardcoded** to `/pscratch/sd/j/josephrb/MINERvA-OmniFold` in both scripts
(`sbatch_unfold_fps_universes_full.sh:25`, `sbatch_dump_fps_inputs.sh:10`), so the tree enumerated in §0
**is** the tree that runs and these paths resolve to the measured files.

**Third axis — thirteen tracked files consume the npz it is the sole source of.**
`git ls-files | xargs grep -Fl of_inputs_fps` returns 13: `coverage_toy_nd.py`, `coverage_valid_nd.py`,
`fps_extension_validation.py`, `sbatch_bootstrap_fps.sh`, `sbatch_bootstrap_fps_corrected_cpu.sh`,
`sbatch_bootstrap_fps_corrected_gpu.sh`, `sbatch_coverage_fps.sh`, `sbatch_dump_fps_inputs.sh`,
`sbatch_seedscan_split_fps.sh`, `sbatch_seedscan_split_fps_corrected_cpu.sh`,
`sbatch_seedscan_split_fps_corrected_gpu.sh`, `uq_fps/corrected/run_fps_uq_packed.sh`,
`uq_fps/corrected/test_fps_corrected_uq.py` (plus `docs/STATVAL_REPAIR.md` and
`uq_fps/corrected/FPS_UQ_CORRECTED_STATE.md` as prose).

### 2b. A naming collision that a future reader will get wrong

`sbatch_dump_fps_inputs.sh:7` describes its own product as the npz "for the FPS bootstrap (**C_stat**)
+ split-seedscan (**C_ML**) stages". **That `C_stat` is not Gate 5's `C_stat`.** Measured:
`nd-unfolding/pet/build_cstat_gate5_n50.py` reads a member manifest and `GATE5_REPLICA_XSEC.npz` on
schema `pet-fullevent-fps-gate5-replica-xsec-v1` (`:58`), and `CSTAT-R2` (`:201-205`) requires the
canonical extended-FPS **285-cell** layout. It does **not** read `of_inputs_fps.npz` and it does not
read either target file. Gate 5 runs on the PET **full-event** FPS chain.

So: two distinct objects are called `C_stat` in this repository, on two different FPS grids, with two
different inputs. **Do not use "the FPS C_stat" as a citation** — it re-points. Neither target file is a
Gate-5 dependency, and this memo does not claim otherwise.

---

## 3. Target 2 — `PC_FPS_MEFHC.root` (67.66 GiB): RETAIN, but the case is genuinely weaker — and the seed's stated reason for it is wrong

**RETAIN, on live code and one derived systematic — not on a note number.** I could not trace any
live note or paper number to this file, and I looked.

Consumers (all default or hardcode this omnifile):

| site | role |
|---|---|
| `sbatch_hadd_pc_fps.sh:22` | **writes** it (`OUT=`) — it is a hadd product of 12 per-playlist `PC_FPS_1[A-P]` files, which are also present |
| `sbatch_npz_pc_fps.sh:14-19` | → `of_inputs_pc_fps.npz` (**6,575,612,207 B**, on disk) → `pet/npz_to_npy.py` → `of_inputs_pc_fps_npy/` (**13,591,352,124 B**) |
| `sbatch_pet_train_fps_hvd.sh:24-25` | consumes that npz/memmap — the 4-GPU horovod full-phase-space PET train |
| `sbatch_nn_dump_fps_5d.sh:17-19` | → `of_inputs_5d_fps_full.npz` (**1,552,038,759 B**, on disk) |
| `fps_gbdt_prior_reunfold_5d.py:62` | → `products/pet/fps_envelope_5d/fps_modeldep_cov_5d.root` (**868,435,949 B**), `fps_gbdt_prior_xsec_5d.npz`, `fps_gbdt_envelope_5d_summary.json` — this is **`C_modeldep`** (`:15`) |
| `build_fps_prior_genie_5d.py:34`, `build_fps_prior_nuwro_5d.py:50`, `dump_w_source_fps.py:39` | `--omnifile` default |
| `sbatch_nn_dump_fps_5d_xps.sh:17`, `_xps2.sh:20`, `sbatch_npz_pc_fps_xps.sh:16`, `_xps2.sh:17` | grid variants |

`fps_modeldep_cov_5d.root` is a model-dependence covariance and is **not** referenced by any `.tex`
file, `VALIDATION_LEDGER.md` row, `docs/OPEN_ITEMS.md` row, or `LIVE-STATE.md` line — greps for
`fps_modeldep_cov_5d`, `fps_envelope_5d`, `C_modeldep`, `modeldep` over the tracked tree return
nothing outside the producing script itself. So this is a **built-but-unquoted** systematic. It is the
weakest RETAIN in this memo and I flag it as such rather than dressing it up.

### 3b. Correction: the trap glob in §7 of the prior audit cannot match this file

`AUDIT-FINDINGS-20260820.md` §7 states *"Same trap applies to `runEventLoopOmniFold_PC_FPS_MEFHC.root`."*
**Measured false.** The trap glob is `*_universes_full.root` minus `*_bkgaware*`;
`runEventLoopOmniFold_PC_FPS_MEFHC.root` has no `_universes_full` component, so the pattern cannot
match it:

```
find … -maxdepth 1 -name "*_universes_full.root" ! -name "*_bkgaware*" -name "*PC_FPS*" | wc -l
→ 0
```

The hazard for target 2 is real but it is a **different** glob — anything of the form
`runEventLoopOmniFold_PC_*.root` minus an exclusion. Stated precisely so the mitigation guards the
pattern that actually fires. This is the same class of error as reading `-A` for "all" in §6 below: the
unit is the whole invocation, and a suffix claim has to be checked against the literal pattern.

### 3c. Correction: the note's three-prior envelope does **not** come from either target

The seed's implicit worry — that the FPS note figures are downstream of these files — is half right and
the half that is wrong matters, because it points at a **third** file that the seed does not mention.
`docs/analysis-note/make_figures.sh` builds all three FPS figures from
`runEventLoopOmniFold_5D_FPS_MEFHC.root` (**6,858,231,993 B**, mtime 2026-06-10 02:17), not from either
target:

| make_figures.sh | figure | omnifile |
|---|---|---|
| `:86` | `fps_pilot_compare_MEFHC.png` (`sec_fps.tex:91`) | `runEventLoopOmniFold_5D_FPS_MEFHC.root` |
| `:87` | `fps_acceptance_MEFHC.png` | `runEventLoopOmniFold_5D_FPS_MEFHC.root` |
| `:88` | `fps_prior_envelope_MEFHC.png` (`sec_fps.tex:104`, `\label{fig:fpsenv}`) | `fps_prior_envelope.py:36` default = `runEventLoopOmniFold_5D_FPS_MEFHC.root` |

**The near-homophone that produced my own first wrong answer, recorded so the next reader does not
repeat it:** `build_fps_prior_nuwro.py` (envelope leg, reads the 6.86 GB merged file) and
`build_fps_prior_nuwro_5d.py` (reads the 67.66 GiB `PC_FPS_MEFHC.root`) differ by one `_5d` suffix and
do different things. I initially attributed the note's ±1.5% three-prior envelope to target 2; it
belongs to the 6.86 GB file.

**Consequence, and it is a new finding:** `runEventLoopOmniFold_5D_FPS_MEFHC.root` (6.86 GB) is the
regeneration source for **three live note figures** and is not on HPSS or CFS either. It is small enough
to archive trivially and it is not in anyone's target set. See §7(2).

---

## 4. THE LARGEST EXPOSURE IS IN NEITHER THE SEED NOR THE TRAP GLOB IT WARNS ABOUT

`nd-unfolding/active_universe_5d/fps/merged/` holds **10 FPS active-lateral merged omnifiles**,
**748,174,751,685 B = 696.79 GiB** — 2.8× the entire seed set, and the single biggest block of FPS bytes
on pscratch.

**They are sha256-bound in committed receipts.** Ten lines each in:
- `docs/orchestration/state/merged-input-hashes/p4-merged-20260718/fps.sha256` (10 digests)
- `docs/orchestration/state/merged-input-hashes/p4-merged-20260718/fps.inventory.tsv` (10 rows; summing
  column 1 gives 748,174,751,685 B exactly — the receipt and the filesystem agree today)

**They are named as inputs in two tracked manifests**, 10 sites each:
- `nd-unfolding/active_universe_5d/fps/covariance/fps_control_manifest.json` — as `input_merged_root`
- `nd-unfolding/active_universe_5d/fps/covariance/audit_merged_fps.json` — as `path`

**And they are the sources of a DISCHARGED ledger entry.** `VALIDATION_LEDGER.md` VL68 records
*"DISCHARGED 2026-08-07 — for the FPS covariance ONLY"* via
`uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined_activelat.root`, job
`56431823`, and the 2026-08-07 entry states the chain ran *"on the ten"* FPS endpoints. VL72/VL73 quote
the combined FPS budget before/after as `8.040779e-39` → `8.774217e-39` (+9.1215%) from that chain.

The file name carries the word **control**. Under the inherited burden of proof — *"a superseded arm can
still be load-bearing as a control or as the denominator of a ratio"* — a set of files whose own
manifest calls them a control manifest is exactly the case the rule was written for. **These 696.79 GiB
are the least removable FPS bytes on the system, and no glob in the seed or in §7 of the prior audit
points at them.**

### 4b. The trap glob is worse than advertised, quantified

The seed's given #3 is confirmed and then some. Same glob, two scopes:

| scope | N | bytes | GiB | sweeps the seed's target 1? |
|---|---|---|---|---|
| `-maxdepth 1` | 14 | — | — | **yes**, as the largest single entry |
| recursive (no maxdepth) | 24 | 1,281,013,193,365 | **1193.04** | yes |
| recursive, FPS only | 11 | 941,043,544,860 | **876.42** | yes |

So `find … -name "*_universes_full.root" ! -name "*_bkgaware*"` run **recursively** sweeps **876.42 GiB
of FPS files** — the seed's target 1 *plus* all ten of §4's sha256-bound control inputs. The trap the
seed flagged is a 179.62 GiB trap at `-maxdepth 1` and an **876.42 GiB** trap without it. State the
depth whenever this glob is written down.

---

## 5. Preservation: the sources are sole-copy, the derived products are on tape

**No `_bkgaware` twin exists for any FPS file — confirmed, not assumed.**
`find /pscratch/…/nd-unfolding -name "*FPS*bkgaware*" | wc -l` → **0**. The seed's given #2 holds, and
its consequence holds with it: for the `bkgaware` pairs, deleting the plain arm removes a superseded
duplicate; for every FPS file, deletion removes the only copy.

**HPSS — re-confirmed cheaply, and the result is more interesting than "absent".**
`hsi -q "ls -lR"` over `/home/j/josephrb`, grepped case-insensitively for `FPS`, returns **11 lines /
6 file objects**, all inside `mnv-quoted-products-20260812`:

| bytes | object |
|---|---|
| 9,897,374,636 | `nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz` |
| 9,419,026,130 | `nd-unfolding/pet/g2_smoke/runEventLoopOmniFold_G2_FPS_1A.root` |
| 25,092,215 | `nd-unfolding/uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined_activelat.root` |
| 1,609,132 | `nd-unfolding/uq_fps/corrected/unified_throw_cov_fps.root` |
| 1,607,692 | `nd-unfolding/uq_fps/unified_throw_cov_fps.root` |
| 30,701 | `nd-unfolding/products/5d/closure_2d_FPS_hidden_eavail_MEFHC.root` |

**Neither named target is among them**, and neither are any of §4's ten. So the seed's given #1 is
confirmed for the two targets — but *"FPS is not on tape"* would be false. The structure is exactly the
prior audit's §1: **the FPS arm's derived uncertainty products are archived; its event-loop sources are
not.** Losing the sources would not lose the quoted FPS covariance results — including VL68's
discharged `activelat` product, which is on tape — it would lose the ability to **rebuild or re-throw**
them. That is a real exposure and a weaker one than "sole copy of the results", and the two must not be
blurred.

**All the intermediate npz products are also sole-copy on purgeable scratch**, so target 1's chain to
`\covFPS` is sole-copy at *two* consecutive links:

| product | bytes | on HPSS? |
|---|---|---|
| `of_inputs_fps.npz` | 1,282,852,815 | no |
| `of_inputs_pc_fps.npz` | 6,575,612,207 | no |
| `of_inputs_5d_fps_full.npz` | 1,552,038,759 | no |
| `of_inputs_pc_fps_npy/` | 13,591,352,124 | no |

**CFS — measured, and a covering null for the question actually asked.**

```
find /global/cfs/cdirs/m3246/josephrb -name "*FPS*"     # full depth, no -maxdepth
→ rc 0, stderr 0 lines, 2 hits
    /global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12.npz
    /global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12_RECEIPT.json
```

**Neither target is present.** That null means something, and the reason it means something is worth
stating: the search exited **0** (read unpiped, not through a pipe), and it produced **zero stderr
lines**, so there was no unreadable subtree anywhere in our own CFS space for a copy to hide in. The
only FPS-named objects we hold on CFS are the G2 full-event input npz and its receipt — consistent with
§5's HPSS finding that the archived FPS objects are full-event and product-side, never event-loop
sources.

**The boundary, stated because it is real and this search does not cover it.** A walk of the *whole*
project directory `/global/cfs/cdirs/m3246` hits **34 permission-denied subtrees**, all under five
**other** members' directories (`kgreif`, `mpettee`, `msmith`, `phebbar`, `Runze`) and **zero under
`josephrb`**. A copy parked in another member's space would be invisible to any search we can run — and
equally unusable as a recovery path, since we cannot read it. **Within our own allocation the
enumeration is complete; outside it, it is not, and cannot be made so.**

**Two earlier attempts are not evidence, and are recorded rather than reported as nulls.** One exited
**124** — `timeout` killed it. One returned rc 0 that was **`head`'s status through a pipe, not
`find`'s**. A third, unbounded walk of the full project directory ran ~50 minutes without finishing and
was terminated; its output file was still empty at that point, which — `find`'s stdout to a file being
block-buffered — is **not** the same as "no hits found yet" and is not reported as one. The number above
comes from the scoped search, chosen because it can finish *and* because it has no unreadable regions to
hide behind. A search that cannot complete does not become a null by being abandoned.

**"Archive instead of delete" — measured, and it does not fit.** HPSS today is **300.17 / 512.00 GiB =
58.6%**, i.e. **211.83 GiB free**. Against that:

- target 1 alone (179.62 GiB) **fits**, with 32.2 GiB to spare;
- both targets (247.29 GiB) **do not fit**;
- §4's ten control inputs (696.79 GiB) **do not fit**, by more than 3×;
- the whole FPS family (1244.70 GiB) **does not fit**, by ~6×.

The m3246 **CFS project quota remains unmeasured** — `showquota` reports only home and pscratch, and
`df -h /global/cfs` returns the shared filesystem, which is not evidence about our allocation. That
number must come from Iris before any archive plan is costed. Note also that HPSS free space is a
**moving** constraint: §6's verify read 300.17 GiB back but wrote nothing, so it did not change it.

---

## 6. OI-50 discharged as a measurement — the quoted archive verifies clean, and it read tape

Reported in full in `RECEIPT-20260820-oi50-hashverify.md`. Summary, because §5's "the derived products
are on tape" is only worth anything if the tape copy is good:

**`hsi hashverify -R mnv-quoted-products-20260812` → rc 0, 36/36 objects `(md5) OK`, zero non-OK lines,
322,306,102,132 B = 300.17 GiB, the complete archive.** Slurm `57287380`, `-q xfer`, 10:32:58Z→10:40:02Z
(7 m 04 s). Coverage is a **set** identity, not a count match: the 36 verified paths and the 36 paths
from `hashlist -R` are byte-identical as sorted sets (`diff` rc 0).

**It read tape, not disk cache** — which is what OI-50 actually needs.
`hsi -q "ls -V"` on the 158 GiB member reports a single storage level, `1 (tape)`, holding all
169,974,191,800 bytes, with `PV List: AH099400` and tape position `2466+0`; **no disk-cache level is
listed.** `hsi -q "dump"` shows `TimeLastRead ... Thu Aug 20 03:37:52 2026` (local = 10:37:52Z), inside
the job window.

**Two corrections this produced, both to claims in the prior audit and the seed:**

1. **`AUDIT-FINDINGS-20260820.md` §1b is wrong that `hashverify` is free.** It says *"digests are
   already stored, so it reads metadata and moves zero bytes."* `hashverify` **recomputes** the digest
   and therefore reads every byte — 300.17 GiB off tape here. It cost 7 minutes rather than hours, so
   the recommendation was right; the stated mechanism was not, and anyone sizing a bigger archive from
   that sentence would under-budget it.
2. **The seed's diagnosis of its own trap is close but not the mechanism.** `hashverify -A <dir>` does
   no-op with `*** Warning: … is a directory - ignored` and exit 0 — reproduced exactly. But the cause
   is not that `hashverify` cannot recurse: **`-R` (`recursively traverse directories`) is in
   `hashverify`'s own usage string and works.** `-A` means *enable auto-scheduling of retrievals*, not
   *all*. The fix is one flag, not a file list. (hsi's *general* `help` text lists the recursion-capable
   commands and omits `hashverify` — that list is incomplete; the per-command usage is authoritative.
   I believed the general help first and had to re-measure.)

**What this does and does not do for the FPS question.** It makes the tape copies of the six FPS
products in §5 verified rather than hoped-for. It says **nothing** about either target file, because
neither is on tape. It does not discharge OI-50 as an open item — that is a claim for Joseph.

---

## 7. Recommendation

1. **Do not delete either named target.** Target 1 (179.62 GiB) is the sole source of a chain ending in
   live, unstruck analysis-note numbers (`\covFPS` 68.67, `\covFPSanalytic` 77.6) and is a hard
   precondition of a 188-job array still in the tree. Target 2 (67.66 GiB) has eleven live code readers
   and one built systematic (`C_modeldep`); its case is weaker and I have said where.
2. **Archive `runEventLoopOmniFold_5D_FPS_MEFHC.root` (6.86 GB) first — it is the cheapest real risk
   reduction available and nobody has asked for it.** Three live note figures regenerate only from it
   (§3c), it is sole-copy, and at 6.4 GiB it fits in HPSS's 211.83 GiB with room to spare. It is not in
   any target set precisely because it is small.
3. **Route §4 to its own decision.** 696.79 GiB, sha256-bound in `fps.sha256`/`fps.inventory.tsv`, named
   in a file called `fps_control_manifest.json`, and the source of VL68's discharge. It is too large for
   HPSS today, so the only options are CFS (quota unmeasured) or accepting sole-copy exposure on
   purgeable scratch. This is a decision, not an audit finding, and it is bigger than the one asked for.
4. **Whenever the `universes_full`-minus-`bkgaware` glob is written down, write the depth with it.**
   179.62 GiB at `-maxdepth 1`; **876.42 GiB** recursive. Pin it in the script, not in prose — a prose
   caveat did not stop the seed from stating the wrong companion file in §3b.
5. **CFS is settled for the two targets; the project quota is not.** Neither target is anywhere under
   `/global/cfs/cdirs/m3246/josephrb` — covering search, rc 0, zero unreadable subtrees (§5). What still
   blocks costing any archive plan is the **m3246 CFS project quota**, which `showquota` does not report
   and which `df -h /global/cfs` does not answer. That number must come from Iris. Until it does, "move
   it to CFS" is a direction, not a plan.
6. **Quarantine is not permission.** `AGENTS.md:28` places *"Historical unified 4D/FPS and PET
   uncertainty products"* at `QUARANTINED` — *"Old unified 4D/FPS covariances … are unquotable."*
   Unquotable is not deletable: those products are retained for audit, and the omnifiles in §0 are their
   only regeneration route. Nothing in the FPS quarantine licenses removing anything in this memo.
7. **`main`-removal machinery does not apply.** As in the prior audit: these files were never in `main`,
   so `CLAUDE.md`'s pushed-evidence-tag / tested-recovery / removal-family-authorization route is not the
   governing procedure. That makes the decision *less* ceremonious, not more permitted.

**Deletion is Joseph's alone. This memo authorizes nothing.**
