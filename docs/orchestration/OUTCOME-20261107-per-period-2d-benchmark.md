# OUTCOME 2026-11-07 — the per-period 2D benchmark: R5 reads "no change" in the 73 best-determined directions, and "farther without 1G–1M" in the other 132

**Recorded by** the per-period 2D benchmark lane (Claude session `director-helper-2`), for the director and Joseph.

**The record:** `state/2d-closeout/per-period-benchmark-20261106/receipts/read/readout.json`, sha256
`4872df322a4e2e49ef009c4fa7eb78f273b8bea75a8a97855fd57451d229dca1` (receipt PR #879, head `416d5be63`).
- It was produced by the bound read: `DECLARATION.md` at M = `a7af2e614`, bound by `BINDING-1.md` (#874).
- The read ran from connect 2 (`connect2.sh` `1e0f8efb…`, the director's GO), after the environment receipt passed
  (#878).
- Run 2026-11-07T06:45Z on login01, at 0 node-h.
- Every number below is quoted from `readout.json` or from `readout.txt` beside it.

**CITABLE FOR:**
- the controls and readings as measured;
- the classes the declaration's rules give them;
- the sentences `DECLARATION.md` §5 licenses for those classes, quoted here.

**NOT CITABLE FOR:**
- which run period is right, that 1G–1M is wrong, or that the published result is right;
- a cause of the 2D shape difference or of the run-period step;
- that the published input lacks the step;
- dropping 1G–1M from any result;
- any change to E_R, Q_R, C_PL or the reported cells;
- any wording for the note or the paper. That goes to the director and Joseph, through a referee read
  (`DECLARATION.md` §5, "For every outcome").

## 1. The controls: all 10 PASS

`readout.json` "controls" records each one's compared values:

| control | measured | bar |
|---|---|---|
| C-PARTC | shares constant over rows, maximum deviation 4.4e-7, row sums exactly 1, step equal, 10 replicas | as declared |
| C-IN-cells | each of the 38 products has the 205 published cells | exact |
| C-PUB | 465.4152721171907 against 465.4152721915331, rel 1.6e-10 | ≤ 1e-8 |
| C-SUM | rel 6.5e-9 | ≤ 1e-6 |
| C-K | k = 73; S₇₃(E_R)/205 = 0.66185 | 73; 0.662 ± 0.0005 |
| C-M | all 6 modes; for example rank 23 has λ/λ_max 3.549e-9 and \|z\| 4.747 | 4 significant figures; ±0.005 |
| C-CTRL | cells 7.46e-12; S₇₃ 9.0e-12; S₂₀₅ 1.3e-11 | 1e-8; 1e-6; 1e-4 |
| C-STEP | 0.10235291689162862, rel 0 | ≤ 1e-10 |
| C-GRAD | rel 0 | ≤ 1e-12 |
| C-COMB | weights sum to 1; integral of x_ABC against `pu_CTRL_s42`: −0.0764% | ≤ 0.5% |

**Copies:** `verify.json` shows all 39 copies equal to `INPUTS.sha256`. The fence showed no `cov2d-*` job, both before
the copy and before the read.

## 2. The classes

**The noise models agree on every class.** Every class below is the same under `replica` and under `replica+seed`, so
none reads "unresolved (noise model)". Values are given as `replica` / `replica+seed`.

**Every σ, and so the noise behind every null class, comes from 10 bootstrap draws plus one seed draw per group.** The
director accepted N = 10. At that N a σ is uncertain by about ±24%.

### R5, the primary reading: the three groups combined (A+B+C) against A+C (without 1G–1M)

| set | T̃(x_ABC) | T̃(x_AC) | Δ₅ | σ₅ | z₅ | class |
|---|---:|---:|---:|---:|---:|---|
| K₇₃, the 73 best-determined directions | 1.880 / 1.874 | 1.949 / 1.935 | −0.068 / −0.061 | 0.096 / 0.098 | −0.71 / −0.63 | **no change** |
| K̄, the other 132 directions | 2.240 / 2.231 | 2.933 / 2.921 | −0.693 / −0.690 | 0.154 / 0.154 | −4.50 / −4.48 | **farther without 1G–1M** |

Δ₅ = T̃(x_ABC) − T̃(x_AC). A negative Δ₅ means the A+C combination is the farther of the two from the published
result. Each T is divided by the number of directions kept, |K|.

**K₇₃, "no change."** The licence is `DECLARATION.md` §5, R5 table, row "\|z₅\| ≤ 2", quoted here with its value filled
in:
> "Removing the 1G–1M group does not change the distance in these directions beyond noise; the smallest change
> resolved is 3σ₅ = 0.29"

3σ₅ is 0.288 / 0.295 per direction, about 15% of T̃(x_ABC). That row does **not** license "the step is unrelated to the
shape difference" outside these directions, or at a smaller size.

**K̄, "farther without 1G–1M."** The licence is §5, R5 table, row "≤ −3"; R5̄ reads the same on K̄, so the sentence is
quoted with K̄ as its directions:
> "Removing 1G–1M changes the result's shape against the published result, away from agreement"

> "in the 132 poorly determined directions of the published covariance, the combination of the other two run-period
> groups is farther from the published result than the three-group combination, by Δ₅ = 0.69, a fraction 0.31 of
> T̃(x_ABC), beyond noise estimated from 10 replicas"

It does **not** license:
- that 1G–1M is wrong;
- the cause of the step or of the shape difference;
- that the published result is right;
- which period is right;
- that the published input lacks the step;
- dropping 1G–1M from any result.

**Sensitivity, printed and read by nothing:**

| directions kept | z₅ | class |
|---|---:|---|
| 139 | −2.89 / −2.71 | unresolved |
| 176 | −5.03 / −4.83 | farther |

### R2, per group (the debiased distance T̃ ± σ)

| set | P_A (1A–1F) | P_B (1G–1M) | P_C (1N–1P) | z B−A, B−C, C−A | class |
|---|---:|---:|---:|---|---|
| K₇₃ | 2.049 ± 0.178 | 2.614 ± 0.345 | 2.780 ± 0.506 | 1.45, −0.27, 1.36 | **no group separates** |
| K̄ | 2.762 ± 0.211 | 5.035 ± 0.533 | 3.293 ± 0.662 | 3.96, 2.05, 0.76 | **other pattern** |

The values are from the `replica` model. The `replica+seed` values differ by at most 0.025 in T̃ and 0.05 in z.

**K₇₃.** The licence is §5, R2, "no group separates", quoted:
> "the distance in these directions does not differ between run-period groups beyond noise"

The resolved sizes, 3σ of each pairwise difference, are 1.16 (B−A), 1.84 (B−C) and 1.61 (C−A).

**K̄.** "Other pattern" licenses the values only. P_B is above P_A at z = 3.96, but it is not above P_C at z ≥ 3, so the
"P_B farther" pattern is not met.

### R3, the six leading modes of E_R's χ²

**All six lie outside K₇₃:** λ/λ_max is between 6.6e-11 and 6.05e-5, below the 1e-4 cut.

| rank (λ/λ_max) | z for E_R | class |
|---|---:|---|
| 23 (3.5e-9) | 4.75 | group-independent at this resolution |
| 9 (4.3e-10) | 3.78 | unresolved (C−A Δ₃ 2.42) |
| 118 (5.6e-5) | 3.65 | group-independent at this resolution |
| 2 (6.6e-11) | 3.64 | group-independent at this resolution |
| 79 (4.5e-6) | 3.61 | unresolved (B−A 2.35, B−C 2.08) |
| 121 (6.0e-5) | 3.50 | **group-dependent** (B−A Δ₃ 3.73 / 3.58) |

In mode 121 the components are P_A 3.00 ± 0.40, P_B 5.45 ± 0.52 and P_C 4.45 ± 0.73.

The licence for mode 121 is §5, R3, quoted with the groups filled in:
> "in mode 121, groups P_B and P_A differ beyond noise"

The 18 tests at 3σ are about 5% familywise under Gaussian independence (§5).

No mode read "not resolved by the period groups".

### R4, the p_∥ step against the published high/low ratio

| | st | σ (group noise) | σ_pub | z₄ | class |
|---|---:|---:|---:|---:|---|
| P_A | −3.37% | 0.25% | 4.14% | −0.81 | matches the published p_∥ high/low ratio |
| P_B | +6.52% | 0.51% | 4.56% | +1.42 | matches the published p_∥ high/low ratio |
| P_C | −0.20% | 0.46% | 4.27% | −0.05 | matches the published p_∥ high/low ratio |

**R4 cannot separate the groups here.** As declared before the read (§5, "R4's power"), the published ratio's own
uncertainty (σ_pub 4.1–4.6% here) is wider than the group differences. The group-to-group differences do resolve, since
p cancels in them: B−A z 17.4, B−C 9.8, C−A 6.1. Those differences have no declared class.

**Printed and read by nothing:** E_R −0.11%, A+B+C +0.05%, A+C −2.56%.

## 3. The combined statement licensed by §5

R5 reads "no change", so §5 licenses one sentence:
> *"The run-period step does not account for the distance in the best-determined directions, at the resolved size."*

**No combined sentence covers K̄.** §5 has a combined statement only for R5 on K₇₃. K̄'s reading is the R5̄ sentence of
§2 above, and nothing more.

## 4. Two printed values a reader needs

1. **R5 compares combinations, not E_R itself.** In K₇₃, T(x_ABC) = 1.995, while E_R's T is 1.859. The integrals of
   x_ABC and the pooled control differ by only −0.076% (C-COMB), but the distance metric is not linear. E_R's own value,
   1.8586, reproduces the 1.859 that `DECLARATION.md` §0 derived by arithmetic from `tension_report.txt:56`.
2. **The noise terms subtracted are larger without 1G–1M.** n(x_AC) is 0.173 against n(x_ABC) 0.114 in K₇₃, and 0.431
   against 0.304 in K̄. A+C has less data.

## 5. Limits, carried from `DECLARATION.md` §6

- **The noise is a lower bound:**
  - `--bootstrap-streams both` fluctuates data and signal MC, not the background template;
  - universe systematics are not in σ;
  - there is one seed pair per group;
  - each σ comes from 10 draws, so it is uncertain by about ±24%.
- **The bars are declared, not calibrated.** Every distance is descriptive, because the analyses share data.
- **Each group is unfolded with its own MC prior and response.** At 5 iterations, each may be pulled toward its prior.
- **P_A includes 1F.**
- **k = 73 and the mode set M** come from the published covariance and the pooled comparison already on record. Each was
  fixed before any group reading.
- **Not measured here:** the published result's own period composition and processing.
  <!-- absence-ok: a scoping statement about what this test measures, not a claim that a result does not exist -->

## 6. Where it goes

- **The director and Joseph:** the readings and classes above.
- **Note or paper wording:** later, through a referee read and Joseph. This record proposes none.
- **No follow-up run** is made because of this outcome unless a new declaration binds it (§7).
- **The 39 copies:** they are deleted under a ledger row once this record is merged, as their own receipts PR
  (the director's ruling of 2026-11-07).
