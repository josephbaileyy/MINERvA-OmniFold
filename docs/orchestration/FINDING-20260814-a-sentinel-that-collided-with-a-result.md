# A verdict string computed from a sentinel that collided with a real result value

`BEN-290`. Filed 2026-08-14 by the OI-120(c) verdict-repair lane. Applied at `143f859`.

**Lane disclosure, first because it governs how to read this file.** The probe is **lane D's**, and lane D
was not running. The **mediator diagnosed** the defect; this repair lane **verified and applied** it. **D did
not review it.** D's receipt prose is untouched apart from the corrected-verdict rows this finding required.

## The headline and its own arms disagreed

Job `56975592` (`OI-120(c)`, no-truth-leakage through the production loader, tested by perturbation)
**COMPLETED, exit 0**, and printed:

```
VERDICT: "LEAKAGE -- event_reco changed when only a truth array changed"
```

Its five arms, from the preserved stdout
([`state/oi120c-loader-purity-perturbation-56975592.txt`](state/oi120c-loader-purity-perturbation-56975592.txt),
5047 B, sha256 `ec5581363f440b153057126996e30f2325cf63c94b27442559a087046522912c`):

| arm | perturbation | expected | observed | scored |
|---|---|---|---|---|
| `P0` | `reco_scalars` ×1.01 (**CONTROL**) | `CHANGED` | `CHANGED` | as predeclared |
| `P1` | `truth_scalars` ×1.05 | `IDENTICAL` | `IDENTICAL` | as predeclared |
| `P2` | `truth_scalars` rows permuted | `IDENTICAL` | `IDENTICAL` | as predeclared |
| `P3` | `part_gen` (truth cloud) ×1.05 | `IDENTICAL` | `IDENTICAL` | as predeclared |
| `P4` | `w_truth` ×1.05 | `IDENTICAL` | **`VOID (perturbation did not perturb)`** | `*** NO ***` |

`P0` moved `event_reco` (`e665e960…` vs baseline `8c88e159…`), so the probe had **demonstrated power**.
`P1`/`P2`/`P3` each left `event_reco` **bit-identical** to baseline under a truth perturbation that the proxy
confirmed had really landed (`arrays_actually_changed: {truth_scalars: true}` etc.). **That is a clean
negative result.** The only arm that failed did so by **not running**: `P4` recorded
`arrays_actually_changed: {}` and `proxy_hits: 0`.

So the receipt reported a positive detection while publishing, beside it, three bit-identical hashes and a
control that fired.

## Cause: one token, and a sentinel that meant two things

The arm flag is **three-valued by design** (`probe-oi120c-loader-purity-perturbation-20260814.py`):

| value | meaning |
|---|---|
| `True` | arm ran and matched its predeclaration |
| `False` | arm ran and **CONTRADICTED** it — the only value that may produce `LEAKAGE` |
| `None` | arm **did not run**; exclude from scoring |

At `f6a52ed` — the tree the job ran — `:219` assigned a **void** arm `False`:

```python
if not r["ok"]:          verdict, ok = "REFUSED", None                          # :217, correct
elif not really_changed: verdict, ok = "VOID (perturbation did not perturb)", False   # :219, THE BUG
...
scored = [v for v in truth_arms if v["as_predeclared"] is not None]             # :232
clean  = all(v["as_predeclared"] for v in scored) if scored else False          # :233
```

`False is not None`, so the void arm **entered the scored set**, forced `clean` False, and the verdict fell
through to the `LEAKAGE` else-branch. Nothing else was wrong with the run.

**The intended semantics were already written down in the same file**, at `:41-44`: *"a perturbation that did
not perturb turns 'no leakage' into 'no test'."* VOID must be excluded exactly like REFUSED. The docstring
and the code disagreed, and **the docstring was right**.

Fix, at `143f859`: `:224` now assigns `None`. Replayed on the recorded arms, off-cluster, nothing re-run:

```
before  LEAKAGE -- event_reco changed when only a truth array changed
after   NO TRUTH LEAKAGE DEMONSTRATED on 3 of 4 truth perturbations, through the production loader
        as_predeclared  P0 True  P1 True  P2 True  P3 True  P4 None
```

## The transferable shape

**A verdict computed from a sentinel whose "not applicable" value collides with a real result value.**

The failure needs no arithmetic error, no bad data and no concurrency. It needs only a flag with **three
states encoded in a type that has two**, and a reader — here `all()` over a filtered list — that treats the
overloaded value as the meaningful one. `bool | None` is the common carrier, and the collision is invisible
at the assignment site: `ok = False` reads as *"this arm is not OK"*, which is **true in English and wrong in
the scoring algebra**, where `False` means *"the property was violated."*

The generalisation, and the check it implies:

1. **Enumerate the states of any flag a verdict reads, and name the ones that mean "no measurement."**
   A tri-state in a boolean is a defect waiting for its third state to occur. Prefer an explicit enum, or a
   sentinel that **cannot** be confused with a result (`"NOT-RUN"`, not `False`).
2. **Test the excluded state, not only the two live ones.** Both directions of the real verdict were
   exercised by construction on every prior run; the *void* path had never occurred until `P4`, so the
   collision had never been executed. The state that means "this did not happen" is precisely the one no
   normal run reaches, so **it is the one a test has to supply.**
3. **Make the program assert its headline against its own operands.** A receipt that prints
   `LEAKAGE` beside three bit-identical hashes and a fired control is **internally contradictory and could
   say so itself.** This is the executable form of the rule (`CLAUDE.md`: *prefer the executable form of any
   rule you are tempted to write down*).

## How it was caught, and it was not by reading the code

**Only because the receipt shipped its ingredients** — `CONVENTION-receipt-ingredients.md`, `BEN-077`. The
verdict string was believable on its own: a `LEAKAGE` headline on a leakage probe is exactly what a real
leak looks like, and no amount of scrutiny of that sentence would have falsified it. What falsified it was
the **operands published beside the conclusion**: per-arm `sha256`, `arrays_actually_changed`, `proxy_hits`
and the control's own hash. The contradiction was then arithmetic rather than interpretive — three truth
arms with the baseline hash cannot coexist with *"`event_reco` changed when only a truth array changed."*

This is now the **second** defect that ingredient-shipping caught with nobody suspecting one (`BEN-077`'s
first-leg-vs-end-to-end mismatch was the first). A verdict-only receipt here would have been believed, and
the sibling finding `BEN-250` makes clear why that mattered: the campaign's *existing* leakage guard has an
empty statement, so this probe was the **replacement** evidence for the property.

## Direction: it failed ALARMING, which is safer and still not free

The collision could only push the verdict **toward** `LEAKAGE`: a void arm can never make a dirty run look
clean, because `clean` is an `all()` and the injected value is falsy. So the failure mode is **loud, not
quiet** — strictly the better direction, and worth stating plainly rather than filing this as a near-miss
catastrophe.

It still cost something, and the cost is specific to *which* alarm fired. **Truth leakage into the reco
input is the campaign's most load-bearing purity property**; a `LEAKAGE` verdict on it, read at face value,
is a publication blocker that invalidates the full-event estimator's input space. The false alarm therefore
competes for exactly the attention that a real blocker would need, at the point in the campaign where Gate 5
and Gate 6 are contending for it. **A fail-alarming bug in a gate is cheap; a fail-alarming bug in a gate
nobody can afford to ignore is not.**

## What was NOT fixed, deliberately

This repair is **one token**. Two cosmetic consequences of routing VOID through the REFUSED sentinel are left
in place and filed rather than patched, because widening the change would put more of lane D's file under an
unreviewed edit:

- The all-void `UNRESOLVED` branch is worded *"the loader refused every truth perturbation; nothing was
  tested."* **VOID is not REFUSED** — the loader accepted the perturbation, the proxy never substituted one.
  The conclusion (nothing was tested) is right; the stated reason can be wrong.
- The per-arm print line labels a void arm `REFUSED`, from `'REFUSED' if ok is None else …`. The `observed`
  column beside it still reads `VOID (perturbation did not perturb)`, so the receipt is not ambiguous — but
  the two columns now disagree in vocabulary.

Both are recorded in `OI-124`.

## `P4`'s void arm: the offered hypothesis is REFUTED, and the real cause is ordering

The dispatch offered a hypothesis, explicitly unverified: *earlier lanes established the trainer consumes the
loader's own weights rather than the NPZ's raw arrays, so perturbing the NPZ `w_truth` may not affect what is
actually read.* **Checked, and it does not hold.** Measured against `HEAD`'s
`nd-unfolding/pet/fullevent_fps_dataloader.py`:

| line | fact |
|---|---|
| `:1121` | `d = np.load(inputs_npz, allow_pickle=True)` — this **is** the object the probe's proxy wraps |
| `:1241` | `event_reco, … = build_event_features(…)` — **the probe's capture point**; `_Captured` is raised inside this call |
| `:1251` | `w_truth_full = np.asarray(d["w_truth"]).astype(np.float32)` — the **first and only** read of the key |

`awk 'NR>=1121 && NR<=1241 && /w_truth/'` over the loader returns **nothing**: no read of `w_truth` exists
between the NPZ open and the capture point. The keys that *are* read in that window are exactly
`data_muon, data_vertex, measured_pc, measured_scalars, part_gen, part_reco, pass_reco, pass_truth,
reco_muon, reco_scalars, reco_vertex, truth_scalars` — which **contains the three arms that fired and does
not contain `w_truth`.**

So the loader **does** read the NPZ's raw `w_truth`, ten lines *after* the probe stops; and what it hands
downstream is derived from it (`:1323`/`:1332` `w_truth_full[imc]`, optionally × `sig_factor`, into
`weight=w_truth` at `:1349`). A perturbation of the NPZ field **would** reach the trainer's weights. The
hypothesis is refuted on both halves.

**The real cause is the probe's own early-stop ordering, and it makes `P4` structurally unfalsifiable rather
than accidentally void.** `event_reco` is fully assigned at `:1241`, *before* any read of `w_truth` at
`:1251`. So `P4`'s predeclared expectation (`IDENTICAL`) is **true by control flow** at that capture point,
and no perturbation of `w_truth` can ever make that arm fail there. `P4` was not a test that missed; it was
a test that could not exist at the place it was run.

That is a **stronger** result than the arm was designed to produce — purity of `event_reco` with respect to
`w_truth` follows from ordering, which no finite set of perturbations could establish — but it is a different
kind of evidence, and the arm should either be **retired with that argument recorded** or **moved to a
capture point past `:1251`**, which is a different probe. **Not attempted here**, per the dispatch.
Recorded as `OI-124`.

**Limit on the loader measurement, stated because the trees fork.** All loader line numbers above are from
**this local checkout at `HEAD`**; job `56975592` ran against `/pscratch`, which I cannot read (no cluster
work authorized or performed). Corroboration, not proof: the probe's own docstring — written by lane D
against the cluster tree — independently cites `:1241` for `build_event_features` and `:1247` for
`assert_no_truth_leakage`, and the local file has them at **exactly** those lines. Two independently authored
citations agreeing is good evidence the trees match here; it is not a verification of the cluster tree.

## Regression

[`test_probe_oi120c_verdict.py`](test_probe_oi120c_verdict.py), written **before** the fix and observed
failing on it: **3 of 6 RED** at `f6a52ed`, **6 of 6 GREEN** at `143f859`. The three RED tests reproduce the
job's exact printed string off-cluster in 0.06 s.

Two properties of the suite are the point, not incidental:

- **It pins both directions.** A void arm must not manufacture `LEAKAGE`, *and* a genuinely `CHANGED` truth
  arm must still produce it. The second test is green before *and* after by design — without it, the fix
  could have been satisfied by deleting the detector, and a test that never had to distinguish those two
  outcomes would not have caught this bug either.
- **The arms are parsed out of the preserved stdout, not hand-written.** So the headline test is a **replay
  of job `56975592`** rather than a re-enactment of it, and it stays honest if the receipt is ever amended.

`run_pass` is the only thing substituted; the `really_changed` assertion, the three-valued scoring, the
filter and the verdict ladder are all the production code path under test.
