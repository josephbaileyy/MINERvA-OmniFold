# Cause 3's `C` leg is INAPPLICABLE to the dominant block — and the answer is a third branch, not either of the two anticipated

**Lane B, 2026-08-17. Read-only: code reads only.** Task 1 of C's ruling. **A MET I reported must be
scoped, and the scoping removes the dominant block from its coverage.**

---

## The two anticipated answers, and the actual one

C framed it as a binary: the `C_syst` input either **carries** a `seed` key (⇒ the guard should have refused
and did not — a live guard defect) or **does not** (⇒ the guard is silently inapplicable to the dominant
block).

**Neither. The dominant block's products are not in the guard's population at all**, and there is no seed
provenance anywhere on that path to be present or absent.

| step | measured |
|---|---|
| the 169 per-universe unfolds | `sweep_bank_5d.py:252` — `omnifold_loop(..., kind="lgbm", ..., seed=42)`, **hardcoded, no CLI flag** (`grep add_argument.*seed` over that module returns nothing) |
| what they write | a **`.root`**, `out = ".../5d_xsec_MEFHC_5iter_lgbm_uni_full_{tag}.root"`, `TFile.Open(out,"RECREATE")` — stamping **only** `ndim`, `globalCompleteness`, `dataPOT`, `hXSecND_flat`. **No seed.** |
| what the guard reads | `unified_throw_cov.py:321` `slabs = glob(args.combine)` and `:363` `bslabs = glob(args.block_slabs)`, then `:328-331` `z = np.load(s); if "seed" in z.files` — **npz only** |
| what combines them into `C_syst` | `analyze_universes_5d.py` — **`grep -c seed` returns `0`. Zero occurrences of "seed" in the entire module.** |

**So:** the sweep products are ROOT files, never globbed as slabs, never `np.load`ed, and never seen by the
mixed-seed guard. **It is not "silently inapplicable to these slabs" — they are a different pipeline.**

## What that does to cause 3's grading

`CRITERIA` §2, cause 3, leg **`C`**: *"One seed threaded and stamped by `do_throws`/`do_blockunits`;
`do_combine` **rejects mixed-seed** combines."*

**That statement is TRUE, and it is true only of the unified-throw pipeline.** `do_throws` and
`do_blockunits` are `unified_throw_cov.py` functions. **The 169-universe `C_syst` path has none of it:** no
seed flag, no stamp, no combiner check, no guard.

**Therefore `C` MET is scoped to the unified-throw legs and does not cover the dominant block.** I reported
that MET; it must be read with this scope attached. **This is a withdrawal of coverage, not a defect in the
guard** — the guard does exactly what it says, over the population it is given.

**And `P`'s "PRESENT" demand cannot be satisfied for the dominant block either.** §2 required the `P` leg to
prove the key is *present* rather than merely not-mismatched (the null-as-absent shape, PB2). **On the
`C_syst` path there is no key to be present**: nothing stamps a seed, so a `P`-style check has nothing to
read. Recorded here because the same measurement answers both legs, and because *"the key is absent"* and
*"the pipeline has no key"* license different repairs.

## Why this was findable only by reading the cited lines

C's own rider applies to itself here: *"a citation true of the file but false of the lines survives every
grep for the claim."* **`C`'s wording names two functions, and both exist and both do what it says.** The
defect is not in either function — it is that the criterion's scope silently equals the union of those two
functions' inputs, and the dominant block is outside it. **No grep for "seed" or for the guard would surface
that; only asking *which files reach the guard* does.**

## What this does NOT say

* **Not a bug in `unified_throw_cov.py:417-419`.** The guard is correct and fires on its population.
* **Not a claim that `C_syst` is wrong.** All 169 universes ran at the same seed (`42`), so they are mutually
  consistent — **by hardcoding rather than by verification**, which is the point: the property holds and
  nothing checks it, so nothing would notice if it stopped holding.
* **Not a re-grading of cause 3 overall.** Legs other than `C` are untouched, and `M(ii)` remains blocked
  on the composite ruling and Joseph's cost decision.
* **Nothing run.** No cluster access was needed: this is entirely a code-path measurement.

## The repair, specified not taken

The minimal fix is **stamping**, not guarding: have `sweep_bank_5d.py`'s `do_run` write a
`TParameter("int")("estimatorSeed", …)` alongside `ndim`/`dataPOT`, and have `analyze_universes_5d.py`
require that all inputs agree on it. **That makes the property that currently holds by hardcoding checkable
— and it is a precondition for `M(ii)` on the composite, since a scan must be able to prove which seed each
universe ran at.** It belongs with the seed-separation change (same two modules, same reviewer), and is
**not** written here: that change stays specified-not-written until Joseph rules on the `28.50 A100-h`.
**⚠ `28.50` SUPERSEDED 2026-08-17 → `39.078` A100-h** (`+37.1 %`; the lateral term costed 5 of 19
universes, missing job `55894759`), and the thing awaiting Joseph is now `39.22` A100-h **plus `55.34` CPU
task-hours` — see [`EXTENT-20260817-2850-a100h-scope-and-missing-legs.md`](EXTENT-20260817-2850-a100h-scope-and-missing-legs.md)
§0 and `BEN-247`. **The dependency stated in this sentence is unchanged**; only the figure it names moved.
Note this is a *definite description* pointing at a number (`BEN-380`): "the `28.50 A100-h`" re-points to
nothing once the value is withdrawn, which is why the replacement is written out here rather than linked.
