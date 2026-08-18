# "Each replica target IS the nominal target × Poisson × one constant" is three orders too strong — and the number that supported it was the constant itself

**Status: MEASURED. The claim is over-strong; the conclusion it was used for survives on other grounds.**
Filed by the mediator; the decisive checks were specified by the second key (`Assistant [28640e]`) and
run by the filer. Every figure below computed from `/pscratch` artifacts, not relayed.

## 1. The claim, and the number that was read as supporting it

`RECEIPT-20260815-oi126-mechanism-narrowing.json` asserts each replica target **is** the nominal target
× Poisson(1) × one shared constant, and reports:

```
refinements_agree_to_percent  = 0.06809234619140625
```

**That number is not a residual bound. It is the shared constant's distance from 1:**

```
shared_renormalisation_on_multiplicity_1_rows = 1.000680923461914
(1.000680923461914 − 1) × 100                 = 0.06809234619140625     IDENTICAL TO THE LAST DIGIT
```

**So `refinements_agree_to_percent` says "the scale factor relating them is 1.00068" — it says nothing
about localised disagreement after that constant is removed.** The per-row residual was never measured.

**The key name is what invites the misreading**, and it cost real reasoning: the campaign carried
*"the targets agree to 0.068%"* for two days, and an argument built on it — *"a 0.068% target
difference would need ~300× amplification through training"* — **was the single strongest objection to a
live mechanism. There was no residual to amplify.**

## 2. The residual, measured

Prediction `nominal × data_factor × C`, replica `00`, seed `50000` read from the artifact:

| population | n | median | p90 | p99 | >1% |
|---|---|---|---|---|---|
| all data rows | 4,116,128 | 8.047e-04 | 8.286e-03 | 6.888e-02 | 8.456% |
| `data_factor == 1` | 1,514,402 | 8.066e-04 | 8.309e-03 | 6.877e-02 | 8.464% |
| `data_factor >= 2` | 1,088,215 | 8.022e-04 | 8.263e-03 | 6.898e-02 | 8.445% |

**A multiplicative identity predicts a residual at float precision. The measured median is `8×10⁻⁴` —
three orders too large — and it is present on rows where the input weight did not change at all.**

## 3. The regeneration is exact, so the residual is not an artifact

`data_factor` is persisted nowhere (`reconcile_gate5_family.py:528` — *"THE STREAM NOTHING ELSE
CHECKS"*), so it was regenerated. The second key specified a **discrete, bit-exact** test: where
`data_factor == 0` the prediction is exactly `0`.

```
factor ZERO but target NONZERO :        0   ← the direction that can falsify. ZERO exceptions in 1,513,511 rows
target ZERO but factor NONZERO :      326   ← Stay-Positive clipping, 0.0079% of data rows
```

**Under a wrong stream the probability every regenerated zero lands on a target zero is `0.368^1513511`.**
The test's designed form was set *equality*; the correct form is the *implication* `factor zero ⟹
target zero`, because `clip()` also produces zeros — and the implication holds exactly.

**Three consistent measurements of the generating process:** data-block zeros `0.367782`, implied
background-block zeros `0.369473`, both against `exp(−1) = 0.367879`, decomposing the receipt's own
full-target `n_zero`.

## 4. What this does NOT establish

**It is not an `OI-126` finding.** The residual is **identical to three significant figures** on rows
whose input weight changed and rows whose did not — so it is **independent of the draw**, and a
draw-independent residual cannot produce a draw-dependent family displacement. **The target route to
`OI-126` is dead**, killed by two free checks rather than by compute.

**A caveat on the tail, unresolved:** `max = 6.86e+02` indicates a near-zero-denominator population, so
`8.46% of rows above 1%` is unconditioned and must not travel as a physical statement. Full clipping is
only `326` of the `~24,500` rows above 10% — **1.33%** — so ~98.7% of that tail is partial clipping,
small denominators, or something else. Unseparated.

## 5. ⚠ THE BACKEND CANDIDATE DOES NOT REVIVE, AND HERE IS WHY

**The over-strong identity claim is exactly what refuted the Stay-Positive backend candidate**
(*"the strings differ; the arrays do not"*). A reader discovering §1 will reasonably think that
refutation collapses.

**It does not, and the reason is stronger than the one it replaces:** `G2_GATE2_TARGET_RUNTIME_RECEIPT.json`
carries `"max_mc_events": 200000` and `"refinement_random_state": 45` — **the same parameters
`build_fullevent_replica_target.py` uses (`:37`, `:205`)**. So the archived Gate-2 target and every
replica target are refined under identical parameters, and **there is no mechanism for a backend
difference to exist, independent of how well the arrays agree.**

Recorded here explicitly so the next reader does not have to rediscover it.

## 6. The open question this creates, which is Gate-2's rather than `OI-126`'s

If both targets are built at identical refinement parameters, **where does a systematic `8×10⁻⁴`
draw-independent residual come from?** That is a question about whether the **hash-pinned archived
Gate-2 target is reproducible from its own recorded parameters** — which nobody has asked, and which
bears on Gate-2 provenance regardless of what the `OI-126` band is doing.
