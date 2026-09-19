# Validating and timing the final Keras execution path

**CITABLE FOR:** what the port is checked against, the limits those checks use, and
why each limit is independent of the thing it tests.
**NOT CITABLE FOR:** any performance claim. Timing is cost; a cheaper arm is not a
better one.

---

## 1. What the port checks establish, and on how many rows

The receipt records **1,024 forward rows and 64 gradient rows**. Those are two
different populations and quoting one figure for both was wrong:

| check | rows | result |
|---|---:|---|
| P-1 inventory | — | 176 tensors, 2,758,702 parameters, identical by name, shape and traversal order |
| P-2a float32, unmodified upstream | 1,024 | cross-engine **3.65e-7** against a **5.26e-7** limit |
| P-2b float64, declared SDPA repair | 1,024 | **6.73e-16** against a 1e-5 tolerance |
| P-3 gradients | 64 | **5.1e5×** closer than a mutant port |
| P-4 one AdamW step | 64 | **4.0e8×** closer than the nearest off-the-shelf optimizer |
| P-5 masking | 1,024 | padded slots change the output by exactly **0** |
| P-6 repeat and reload | 64 | bitwise |

## 2. The float32 limit no longer moves when the port is wrong

The first version accepted P-2a when

```
cross_engine <= their_float32_deviation + our_float32_deviation
```

which is the triangle inequality — and useless as a gate, because **our** deviation
is on the right-hand side. A port with a float32 defect widened its own acceptance
band in proportion to the defect and could pass by being wrong.

Replaced by two limits, **neither of which reads our float32 output**:

* **(a)** `cross_engine ≤ 2 × their_float32_deviation`. Two independent roundings
  of one computation, each at most `e` from the exact float64 answer, differ by at
  most `2e`. Using the reference's `e` on both sides makes the bound a property of
  the upstream implementation, which is not the object under test.
* **(b)** `our_float32_deviation ≤ 2 × their_float32_deviation`. This is the clause
  the old rule rewarded the violation of, and the one a float32 bug trips.

Measured: cross-engine **3.65e-7**, limit **5.26e-7**, our deviation **1.77e-7**
against the reference's **2.63e-7** — ours is *smaller*.

A third quantity is reported and deliberately does **not** gate: an a-priori
perturbation bound of **5.83e-8**, obtained by jittering every parameter and input
by one float32 ulp and re-running in float64. It touches no float32 run at all, so
it is independent of both implementations — but it models the rounding of inputs
and weights and not of every intermediate, so it is a **floor** on achievable
disagreement, not a ceiling. Quoting it as the limit would have been wrong in the
other direction.

`test_port.Float32Limit` includes the regression directly: inflate our deviation
and the verdict must get **worse**; under the old rule the same inputs passed.

## 3. Mutant controls, kept alongside the numerical limits

P-3 and P-4 are gated on a deliberate minimal structural change, not on a
tolerance, because re-measuring a floor until the check passes is how a port check
becomes decorative. The declared margin is 1,000×; the measured margins are 10⁵–10⁸,
so the constant is not load-bearing.

| check | mutant | margin |
|---|---|---:|
| P-3 | the port with `emulate_upstream_float32_reduction` off — a real implementation choice, arguably the more "correct" one | **5.1e5×** |
| P-4 | `tf.keras.optimizers.AdamW`, the nearest off-the-shelf optimizer | **4.0e8×** |

Round-off floors are still measured three ways — row permutation, half-batch split,
one-ulp jitter — and reported as corroboration.

## 4. Coverage of the execution path

Beyond the port checks, the path is exercised where it will actually run:

* **the real `MultiFold` loop**, not a stand-in, on both step schemas — 5 features /
  13 globals / coord `(1,2)` at reco and 8 / 2 / coord `(5,6,7)` at truth — under
  his optimizer, schedule and clipping, with the `OI-125` fold-forward recorder
  attached and the realized policy verified against the plan;
* **33 tokens, both intended batches (512 and 2048), both step schemas, and
  production precision (float32)** on one GPU, for our incumbent, the ported
  degraded arm and his complete arm;
* **validation inside the timing**, because a loop that reads only the clock cannot
  tell a number from a NaN: every cell records its value, and the receipt requires
  finite values everywhere and a loss that **moves** in every training cell. A
  frozen loss means the optimizer is not connected to the graph, which a ms/step
  figure hides perfectly.
