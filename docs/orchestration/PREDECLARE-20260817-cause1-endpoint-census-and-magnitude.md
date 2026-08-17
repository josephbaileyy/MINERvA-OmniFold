# PREDECLARE — cause 1's two open legs: the per-band endpoint census (`P`) and the one-sided magnitude (`M`)

**Lane E, 2026-08-17, written at `4dfeccd` BEFORE any covariance was reconstructed.** Scope: quarantine
cause **1**, one-sided endpoint interpolation, for **X** — the adopted 5D GBDT covariance,
background-aware footing, 10,694 reported bins.

**This adopts nothing.** `docs/analysis-note/` untouched, not one character; `values.tex` untouched; no
ROOT modified; no covariance product rebuilt or replaced. Every file is opened READ. The only writes are
one JSON receipt and documentation.

---

## 1. The has-this-been-done search, and what it found — including that it found something

Run at `4dfeccd`, terms the dispatch did not use:

```
git grep -iln 'one-sided|one_sided|endpoint census|endpoint interpolation' -- 'docs/*' '*.md'   -> 20 files
git ls-files | grep -iE 'census|endpoint|onesided|one_sided'
   -> nd-unfolding/active_universe_5d/standard/evidence/p4_endpoint_evidence.json
      nd-unfolding/fps_endpoint_receipt.py
      nd-unfolding/pet/fps_census.py
      nd-unfolding/merge_active_endpoints.sh
git grep -iln 'cause 1\b' -- 'docs/*' 'nd-unfolding/*'                                          -> 8 files
grep -nE '^#{2,3} ' CRITERIA-20260811…md                                                        -> 4.1 … 4.7, NO 4.8
```

**Two results that change the work, and one that does not.**

**(a) The `C` leg's evidence EXISTS and is stronger than the criterion asked for — but its citation is
dangling.** `CRITERIA` §3 grades cause 1's `C` leg **MET** citing *"(§4.8)"*, and **§4 of that document
runs 4.1 through 4.7; there is no §4.8.** Following the pointer yields nothing. **I did not stop there,
and the audit is real:** it is committed as `Cause1PathAuditTests` in
`nd-unfolding/tests/test_uq_remediation.py` and recorded in `ND_OMNIFOLD_RUN_LOG.md` under
*"2026-08-11 — BEN-106 VERIFIED; cause 1's path audited"* — 11 modules in the transitive closure from
four production entry points, four covariance constructors, both unfixed one-sided sites shown to be
`pet_*` and unreachable, four mutations. **So this is a citation defect, not a missing audit**, and the
distinction is the whole of why the search had to be covering rather than a single grep. It is also the
second dangling pointer this campaign has found in this document class — `CRITERIA` §4.4 is *itself* the
finding *"the only predeclared discharge criterion any of these five causes has is cited by a line number
that no longer contains it."*

**(b) The four `endpoint`/`census` artifacts are a DIFFERENT OBJECT and none of them is X's census.**
`p4_endpoint_evidence.json`, `fps_endpoint_receipt.py`, `pet/fps_census.py` and
`merge_active_endpoints.sh` are FPS / P4-standard lateral-endpoint artifacts on the **266-bin** FPS grid,
not the 10,694-bin 5D GBDT sweep. *"Endpoint"* is overloaded across the two campaigns exactly as
*"quarantine"* is (`MAP-20260817` §3), and a census of the wrong grid would look like a discharge.
**No per-band endpoint census exists for X** — bounded by the four searches above, not asserted.

**(c) Nothing has computed cause 1's `M`.** `CRITERIA` §2 says so in its own words — *"This number does
not exist anywhere"* — and the searches above return no candidate.

## 2. Scouting already done, declared as scouting rather than presented as measurement

A **filename listing** of `uq_5d/universe_sweep_bkgaware/` (no ROOT opened, no value read) gave:

* **188 files** matching the production glob — the same 188 the note's prose names.
* **42 bands with exactly 2 universes** (`_0`, `_1`) — the ±1σ pairs.
* **`Flux` with 100**, indices **exactly `0…99`, contiguous, verified by sort**.
* **`2p2h` with THREE** (`_0`, `_1`, `_2`) — **not a ±pair**, and this is a declared unknown, see §4.
* **one `…_uni_full_CV.root`** carrying no numeric index, which production's `UNI_RE` does not match and
  therefore skips.

**This is inventory, not physics**, and it is written down here so that no number below can be presented
as a prediction that was really a peek.

## 3. What will be measured, and why it needs no cluster job

X's band covariances are built by `analyze_universes_5d.py:91-104` from per-universe flat vectors already
on disk. **The two open legs come out of one pass over those files.**

**Fidelity rule: the reader IMPORTS production's own `load_flat` and `UNI_RE` from
`analyze_universes_5d`** rather than reimplementing them, so a discrepancy cannot be my parsing.

**`P` — the census.** Per band: which indices are present, how many, and whether both ± endpoints exist;
`Flux` exactly 100 and contiguous from zero. Recorded per band, absence never omitted.

**`M` — the magnitude, and it is diagonal-only BY SUFFICIENCY, not as a shortcut.** The criterion asks for
*"√Tr and per-bin median of X built both ways on X's own bank … reported as a distribution, not a max"*.
Trace and per-bin σ depend only on the **diagonal**, and the diagonal of each form is computable without
ever materialising a 10,694² matrix:

    as-built (mean-centered, biased 1/N, analyze_universes_5d:96-97)
        Z = D - D.mean(axis=0);   diag_b = (Z**2).sum(axis=0) / N
    one-sided CV-centered (the defect)
        diag_b = d_{+1σ} ** 2                       i.e. diag(outer(x_{+1σ} - CV))

    trace_b = diag_b.sum();  total_diag = Σ_b diag_b;  √Tr = sqrt(total_diag.sum())
    per-bin rel σ = sqrt(total_diag) / cv_reported;  reported as a median over bins

**Stated limit: this compares traces and per-bin σ exactly and does NOT compare off-diagonal structure.**
The criterion is phrased over √Tr and per-bin median, so this is exactly sufficient for it and exactly
insufficient for any claim about correlation structure. I will not make one.

**The counterfactual is applied ONLY to the 42 N=2 pair bands.** The defect is defined for a ±pair; `Flux`
(N=100) has no "the +1σ endpoint", and `__Normalization_flat` is a documented rank-1 band, not a one-sided
construction (`CRITERIA` §2 cause 1; RUN_LOG 2026-08-11). Both are carried **unchanged** in both totals, so
the difference between the two totals is attributable to the pair bands alone.

## 4. Declared unknowns — named now so the answer cannot be shaped later

* **`2p2h` has N=3.** I do not yet know whether that is a ±pair plus a third variant or a three-point
  model band. **It will be reported in the census verbatim and EXCLUDED from the one-sided
  counterfactual**, with its exclusion and its contribution stated separately. If the exclusion turns out
  to matter to the `M` verdict, that is a finding and not a choice I will make quietly.
* **Which index is `+1σ`.** The convention `idx 0 = −1σ, idx 1 = +1σ` is stated in
  `unified_throw_cov.py:52-53`. **I will compute the one-sided form BOTH WAYS** — `outer(d_0)` and
  `outer(d_1)` — and report both, so the verdict does not rest on my reading of a comment in a
  different module.

## 5. Predeclared reproduction targets — five numbers, all committed

The as-built reconstruction must reproduce
`nd-unfolding/uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_summary.txt`:

| quantity | committed value |
|---|---|
| reported bins | `10694` of `65856` |
| total syst √Tr | `4.3515e-38` |
| total syst median rel | `13.235%` |
| `Flux` category sum √Tr | `3.993e-39` |
| `Models` category sum √Tr | `8.964e-38` |
| `Normalization` category sum √Tr | `4.507e-39` |
| `Hadronic response` category sum √Tr | `4.017e-38` |
| `Muon reconstruction` category sum √Tr | `2.789e-38` |

`--add-norm 0.014` per `sbatch_finalize_5d_bkgaware_gpu.sh:26`; CV
`products/5d/xsec_5d_MEFHC_5iter_lgbm.root` per `:18`. Category sums are **sums of per-band √Tr**, not
√Tr of the category sum — reproduced as production defines them.

## 6. Branch set — declared now, with two dominators

* **C1 — MEASURED.** Reconstruction reproduces all eight §5 targets to their quoted precision; the census
  is complete (42 pair bands with both endpoints, `Flux` 100 contiguous); the one-sided total is computed
  and reported as a **per-band distribution** (min / median / p90 / max of the per-band trace ratio) plus
  the two totals. → **`P` MET; `M` MEASURED and no longer "does not exist anywhere".** Whether the
  measured magnitude discharges cause 1 is a separate question — see §7.
* **C2 — RECONSTRUCTION FAILS (dominator).** Any §5 target not reproduced. → **The one-sided comparison
  is VOID**, whatever it says, because an instrument that cannot rebuild the committed number is not
  measuring X. Report and stop; do not present the ratio.
* **C3 — CENSUS INCOMPLETE.** A pair band missing an endpoint, or `Flux` not exactly 100 contiguous.
  → **`P` FAILS by measurement**, which is a stronger and more useful result than PARTIAL.
* **C4 — EVIDENCE GONE.** A file absent or unreadable on purgeable scratch. (A listing at 06:0xZ showed
  all 188 present; **a listing is not a read**, so this stays live.)
* **C5 — DEGENERATE (dominator).** The one-sided total equals the as-built total, or every per-band ratio
  is `1.000`. → **My counterfactual is not implementing the defect and the measurement is VOID**, not
  "the defect is harmless". This is the control in the direction the computation acts: the two forms
  must be shown to differ before a difference can be interpreted.

## 7. What this CANNOT do

* **It cannot discharge cause 1 by itself.** `C` is MET (§1a), `T` is MET and I will re-derive it. If C1
  holds, all four legs have content — **but `M` MEASURED is not `M` ACCEPTABLE**, and whether the measured
  magnitude is small enough to leave X's published numbers standing is a **physics-presentation
  judgement**. I will report the number and name the judgement. **I will not take it.**
* **It says nothing about causes 2–7**, nor about whether X is replaced by the candidate.
* **`CRITERIA`'s dangling `§4.8`**: I will record the correction and a pointer to where the audit actually
  lives. **I will not rewrite another lane's row text.**
