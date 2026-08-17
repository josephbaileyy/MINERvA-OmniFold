# RECONCILIATION — the four `\gbdtFive*` macros against the rebuilt 5D candidate

**Lane A, 2026-08-17. READ-ONLY. `docs/analysis-note/` was not edited — not one character.**
Whether any of this reaches the note is Joseph's call and a separate act.

**Environment for every count below:** repo `56e7f6d` (`origin/main` at the time of measurement),
`TMPDIR=/Users/josephbailey/.claude-school/jobs/92633334/tmp`, pytest colour **on** (default), platform
`darwin`. Recorded because two variables — ANSI colour and `TMPDIR` — were each shown last night to move
a suite count on an unchanged tree.

---

## 0. Bottom line

**None of the four macros is changed by tonight's rebuild, and the reason is not "the numbers happen to
agree" — it is that stage 4 does not compute the quantity the macros hold.**

**They are stale anyway**, for a reason established *before* tonight and still unresolved: the J28 flux
correction. That is a footing decision, not a bookkeeping one, and it is not mine to make.

| macro | value in note | moved by tonight's rebuild? | stale for another reason? |
|---|---|---|---|
| `\gbdtFiveBlockMedian` | `13.36` | **No** | **Yes** — `13.43` under the non-bkgaware footing |
| `\gbdtFiveAdoptTrace` | `5.81e-38` | **No** | **Yes** — `5.2600e-38` proposed (J28) |
| `\gbdtFiveCVTrace` | `6.24e-38` | **No** | **Yes** — `5.6609e-38` proposed (J28) |
| `\gbdtFiveMeanShift` | `1.65e-38` | **No** | **Not established either way** — see §4c |

---

## 1. The has-this-been-done check, run first, with the searches named

Per the standing rule that a negative must be bounded by the search that produced it, here is the
search rather than the conclusion. All at `56e7f6d`, unrestricted over **all tracked files** (no path
globs, which is the failure mode that produced a false absence last night):

```
git grep -n 'gbdtFive' $(git rev-parse origin/main) --                       -> 40 hits, 12 files
git grep -il 'reconcil' ... -- 'docs/orchestration/*gbdt*'                   -> 1 (RUNBOOK-20260807)
git ls-tree -r --name-only origin/main | grep -i gbdt                        -> 19 paths
git grep -n '4\.3513\|4\.3576\|sqrt_tr_syst\|sqrt_tr_full' origin/main --    -> 12 hits
git log --oneline -S'0.30}{\percent}' -- docs/analysis-note/sec_systematics.tex
git log --oneline -S'0.28}{\percent}' -- docs/analysis-note/sec_systematics.tex
```

**Substantially done already, and that changes what is left to do:**

* **`PROCEDURE-gbdtFive-macro-update.md` exists** (176 lines, written cold 2026-08-11) and
  `INTEGRATION_CHECKLIST.md:65` calls it *"correct and deliberately unused."* It is a contingency
  procedure, explicitly **not an authorization**, and it supplies no replacement magnitude.
* **`VALIDATION_LEDGER.md` VL46/VL47 already record two of the four derivations** with full-precision
  operands.
* **A replacement pair already exists** — `5.2600e-38` / `5.6609e-38` — recorded at
  `VALIDATION_LEDGER.md:925-926` with its own footing caveat, from **before** tonight.
* **`INDEX-retracted-and-superseded-values.md` already flags a `\gbdtFive*` update as pending.**

**The genuinely new question is only the one asked: does tonight's rebuild move them.** Everything
else here is re-derivation for the receipt, not discovery.

---

## 2. What each macro IS, from its producer rather than its comment

The `values.tex` comments are narration. These are the derivations.

### 2a. `\gbdtFiveBlockMedian` = `13.36`

**Producer:** `nd-unfolding/uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_summary.txt` — **tracked,
487 bytes, readable, mtime Jul 23**. Line 5:

```
CV: products/5d/xsec_5d_MEFHC_5iter_lgbm.root
glob: uq_5d/universe_sweep_bkgaware/5d_xsec_*_uni_full_*.root
reported bins: 10694/65856
total syst sqrt-trace=4.3515e-38 median rel=13.235%
combined sqrt-trace=4.3578e-38 median rel=13.359%
```

`13.359% → 13.36`. **Footing: background-aware**, which is what the note's prose asserts at
`sec_systematics.tex:164`. Its non-bkgaware sibling
(`uq_5d/universe_stage2_5d/uq_universe_5d_summary.txt`) reads `13.432%`, so this macro is **not** a
footing-neutral fourth number that can be left alone while the other three move.

### 2b, 2c. `\gbdtFiveAdoptTrace` = `5.81e-38` and `\gbdtFiveCVTrace` = `6.24e-38`

**Producer:** `nd-unfolding/adopt_unified_5d.py`, the `sqrt_tr_new` TParameter (`:154`, written `:178`).
The two macros are **the same script in two modes**:

* **default = mean-centered.** `:89` `vu = clip(_diag(fu.Get("C_unified")), 0, None)`, the unified
  per-bin variance.
* **`--cv-centered` = F7 variant.** `:91-95` adds the per-bin joint `mean_shift²` to that variance —
  the flag's help text says *"do NOT silently drop the shift"*.

Both then apply a per-bin inflation factor `g` derived from the throw (`:87-89`), and the adopted
covariance is `lateral+stat+ML + G C_vert G` (`VALIDATION_LEDGER.md:925-930`).

Full-precision operands, from **VL46/VL47** (`VALIDATION_LEDGER.md:500-501`):

```
input  (sqrt_tr_old, bkgaware block combined)   4.357790406860002e-38
AdoptTrace (sqrt_tr_new, mean-centered)         5.807716496958672e-38   ->  5.81e-38
CVTrace    (sqrt_tr_new, --cv-centered)         6.236702327843976e-38   ->  6.24e-38
```

### 2d. `\gbdtFiveMeanShift` = `1.65e-38`

**Producer:** the `joint_mean_shift_norm` key, read by `adopt_unified_5d.py:104` and recorded at
`VALIDATION_LEDGER.md:197` as `1.654393237996853e-38`. It is an **input** to the CV-centered variant,
not an output of either adoption — which is why the note reports it *"separately rather than folded
into that covariance."*

---

## 3. Does tonight's rebuild move any of them? **No.** Three independent grounds.

### 3a. Tonight's numbers are not new — they were recorded eight days ago

Stage 4 tonight reported `sqrt_tr_syst = 4.3513e-38`, `sqrt_tr_full = 4.3576e-38`, 45 bands / 40
retained. **`FINDING-20260809-stage6-central-gate-cannot-pass.md:312` already records, for
`std_final5_candidate.root`:**

> `42.3 GB, 45 bands, sqrt_tr_syst 4.3513e-38, sqrt_tr_full 4.3576e-38`

**Identical to all quoted digits, at the same band count, from 2026-08-09.** So the rebuild reproduced
the prior build in exactly these quantities. Consistent with lane B's independent measurement that the
covariance **content** is bit-identical across the rebuild (`f26b3bfe…` for the rebuilt C5 total), while
only the whole-file digest moved (`602bbcf2… → 950f8cb1…`, ~24 KB of metadata/band-level bytes).

> **Provenance of tonight's two numbers, stated because it matters:** they reached me as a relay from
> the mediator, not as my own measurement — the products are on `/pscratch` and unreadable from this
> checkout. What I verified myself is that **the repo already contains those exact values** at the line
> above. If the relay is wrong, §3a is wrong with it; §3b does not depend on it.

### 3b. Stage 4 does not compute the macros' quantity — the structural answer

`nd-unfolding/p4_build_components.py:164-166` prints exactly what stage 4 produces:

```
Csyst_active = sum(retained non-lateral bands) + sum(5 active MAT bands)
Ccomb_active = Csyst_active + C_stat + C_ml
sqrt_tr_syst = sqrt(trace(Csyst_active));  sqrt_tr_full = sqrt(trace(Ccomb_active))
```

**No mean-centering, no `g`.** The macros live one step further on. The chain, with every operand:

| step | quantity | value | change |
|---|---|---|---|
| 1 | support-family combined, bkgaware (`uq_universe_5d_summary.txt:5`) | `4.357790e-38` | — |
| 2 | candidate block-sum after the 5-band lateral swap (stage 4) | `4.3576e-38` | **−0.0044%** |
| 3 | adopted mean-centered, after `g` (`adopt_unified_5d.py`) | `5.807716e-38` | **×1.3327** |
| 3′ | CV-centered variant | `6.236702e-38` | **×1.4312** |

The syst leg has the same shape: `4.3515e-38 → 4.3513e-38`, **−0.0046%**.

**Stage 4 stops at step 2. All four macros are at step 3 or are inputs to it.** So the ~34% gap between
`4.36e-38` and `5.81e-38` is not a discrepancy — it is the documented inflation the note's own prose
describes at `sec_systematics.tex:165-167` (*"including cross-source nonlinear response raises the
candidate mean-centered covariance to…"*). **The mediator was right not to assert a contradiction;
there is none, and the two figures were never the same quantity.**

### 3c. The one number that did move, moved by 0.004%, and it is not a macro

Step 1 → step 2 is the only place tonight's work touches this chain at all, and it is the lateral
replacement rather than the rebuild. At 4 significant figures the candidate differs from the support
family by **−0.0044%** (combined) and **−0.0046%** (syst) — far below the 3 s.f. any macro is quoted at.

---

## 4. What *does* make the macros stale — established before tonight, still unresolved

### 4a. The J28 flux correction

`VALIDATION_LEDGER.md:925-926` records the replacement pair and its mechanism:

```
\gbdtFiveAdoptTrace   5.81e-38  ->  5.2600e-38
\gbdtFiveCVTrace      6.24e-38  ->  5.6609e-38
```

Re-derived here, and it reproduces the ledger's own arithmetic exactly, which is the point of shipping
operands: the footing-**matched** change is `5.2600/5.80 − 1 =` **−9.31%**, and against the bkgaware
`5.81e-38` it would read **−9.47%** — the ledger names −9.31% as correct and −9.47% as the mismatched
comparator, and both of my figures agree with it to the digit.

### 4b. But the replacement pair is on the *other* footing, and that is the unresolved part

`VALIDATION_LEDGER.md:900-911`: the J28 adoption ran **without** `--combined`, so it defaulted to
**non-bkgaware**, while the note's prose says *"background-aware"*. The inflation ratios differ
correspondingly — bkgaware `×1.3327` / `×1.4312`, J28 non-bkgaware `×1.2104` / `×1.3027` — and
`\gbdtFiveBlockMedian` would move `13.36 → 13.43`.

**The ledger records this as UNRESOLVED between two options**: re-adopt with `--combined` on the
bkgaware product (a job well under 12 h), or adopt non-bkgaware with the prose rewritten. **That is a
footing choice and it is outside this task's remit** — I was asked to establish what the numbers are and
whether they moved, not to adjudicate the physics, and I am holding that line as I did on `OI-6`.

### 4c. `\gbdtFiveMeanShift` — not established either way, and I am not guessing

None of the sources I read gives a J28-corrected `joint_mean_shift_norm`. It is an input to the
CV-centered variant, so a J28 re-adoption would consume a new one, but **whether the shift itself moves
is not recorded anywhere I found.** Marked unestablished rather than unchanged.

### 4d. A derivation that does NOT close, reported rather than smoothed over

Per `CONVENTION-receipt-ingredients.md`, the operands must be able to contradict each other. They
partly do:

```
sqrt(CVTrace² − AdoptTrace²) = 2.273078e-38     MeanShift = 1.654393e-38     ratio 1.374
```

So the naive identity `Tr(C_cv) = Tr(C_mean) + |shift|²` does **not** reproduce the published mean-shift
norm. The code ordering is consistent with why — `adopt_unified_5d.py:91-95` adds `shift²` to the
variance `vu` **before** `g` is derived from it, so the shift is itself inflated — but **I have not
established that this fully accounts for the factor 1.374, and I do not claim it does.** Recorded as an
open arithmetic residual for whoever owns the re-adoption.

---

## 5. Unsourceable operands — **yes, three, and they are exactly the `\petRatio` shape**

`INDEX-retracted-and-superseded-values.md` records the trap: a derived macro looks managed while its
operands sit outside the marking convention as inline `\SI{}` literals. **The same shape is present in
this very prose chain.**

The four macros are consumed at `sec_systematics.tex:165, :167, :168, :170`. Three lines later, in the
same continuous block:

```
:174   sqrt-trace by only \SI{0.28}{\percent}; the effect on the \emph{adopted}
:175   covariance is smaller still, \SI{0.09}{\percent} before the flux (J28)
:176   correction and \SI{0.18}{\percent} after it, because the adoption's per-bin
```

**`0.28`, `0.09` and `0.18` are inline literals, not `values.tex` entries.** They quantify the
background-subtraction refinement and its transfer to the adopted covariance — i.e. they are operands of
the same J28/footing question that moves the macros — and **nothing in the macro-marking convention
covers them.** A `\gbdtFive*` update that leaves them untouched would leave the block internally
inconsistent, and no search over `values.tex` would reveal it.

### 5a. And two documents quote the note's text as it no longer reads

`PROCEDURE-gbdtFive-macro-update.md` §2 and `VALIDATION_LEDGER.md:225, :515, :517, :911` all describe
the note as quoting **`0.30%`**. **The note says `0.28`.** Traced: `git log -S` shows `d75833a` changed
it, and `VALIDATION_LEDGER.md:855` records the underlying measurement as **`+0.2839%`**, noting
`+0.30%` was the earlier *rounded* form.

So the ledger is right about the physics and stale about the note's wording. **Not a numerical error —
a dated claim about a document**, and it matters only because those four citations are how an updater
would locate the sentence.

### 5b. Line-number drift, same class

Three documents give three different consumption-line sets, none matching the file:

| source | claims | actual |
|---|---|---|
| `PROCEDURE §1` | `:163, :165, :166, :168` | `:165, :167, :168, :170` |
| `CRITERIA-20260811:48` | `:162, :164, :165, :167` | same |
| `INTEGRATION_CHECKLIST:59` | `:162-173` | block spans `:164-176` |

Each was true when written. Cite by macro name, not by line.

---

## 6. Limits of this document, stated rather than left to be discovered

* **I did not measure tonight's stage-4 output.** It is a relay; the products are on `/pscratch`. §3a
  verifies only that the repo already holds those exact values. **§3b is independent of the relay** and
  is the load-bearing argument.
* **I did not verify the July artifacts' contents against their producing run** — the summary files are
  tracked and were read as committed.
* **I did not adjudicate any physics**: not the footing choice (§4b), not the `g` construction, not
  whether the J28 pair is correct. Establishing what the numbers are and whether they moved is the whole
  scope, deliberately.
* **`\gbdtFiveMeanShift` is unestablished, not unchanged** (§4c), and the §4d residual is open.
* **Nothing here authorizes an edit to `docs/analysis-note/`.** The macros also carry a second live gate
  the note states itself — *"neither is adopted for publication until the selection-complete lateral
  replacement lands"* — and that sentence is about the very candidate stage 4 built tonight, which
  `std_component_manifest.json` marks `publication_gate_rejects_this: true`.
