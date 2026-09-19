# INVENTORY — what `scientific_acceptance` actually depends on, read from CODE

**Step 1 of the new-candidate goal, read-only.** Derived from the code that writes the field, **not
from documentation**. Conclusion: **(C) BLOCKED at step 1, before any compute**, for **two
independent reasons**, each reserved to Joseph.

---

## ⚠ FINDING 1 — `scientific_acceptance` IS NOT COMPUTED. IT IS A HARDCODED LITERAL.

`scientific_acceptance` is assigned in **exactly two places in the entire tree**, both in
`z_build.py`, and both are the constant `"NON-PASSING"`:

| site | code |
|---|---|
| `z_build.py:608` | `"scientific_acceptance": "NON-PASSING",` — per-variant product metadata |
| `z_build.py:788` | `"scientific_acceptance": "NON-PASSING",` — the build's return envelope |

**There is no conditional, no computation, and no code path that emits `"PASS"`.** The only `"PASS"`
string anywhere is a **test fixture** (`tests/test_project_cov_nd_receipt.py:505`).

**`outcome.assessable` is likewise a literal.** `z_build.py:652-658` builds `science` as a constant:

```
science = {"assessable": False, "branch": None, "branch_label": None,
           "reject_conditions": ["4c"],
           "reason": "Scientific criteria and real-input evidence remain unresolved."}
```

and passes it at `:768` as `outcome=science`. **`z_validator.assess()` — the only function that ever
returns `assessable=True` — is not called by the builder** (and has no production caller at all).

**The code says so itself**, `z_build.py:841`:

> *"2 = the build RAN TO COMPLETION and its science is NON-PASSING, **which is the only outcome this
> command can produce**"*

### What this means for the goal's success conditions

**Neither (A) nor (B) is reachable by running a new job.**
- **(A) PASS** requires `scientific_acceptance: PASS` — no code path produces it.
- **(B) ASSESSABLE FAIL** requires `outcome.assessable: true` — the builder writes `False` as a
  constant.

A new build would emit `NON-PASSING` / `assessable: false` / `reject_conditions: ["4c"]` **whatever
the data and whatever `ε` is**. Making the builder *compute* acceptance is a **material change to how
acceptance is decided** — reserved, and forbidden outright once any output of the new job exists.

⚠ **ONE PLACE `ε` WOULD ACTUALLY BITE, so the inventory is not overstated:** `z_build.py:521` calls
`validator.assess_null(null_measurement["r_null"])`, and `z_validator.py:355-366` **does** read the
boundary — with `ε` declared it returns `assessable: True`, a `limit`, and `within bound` /
`exceeds bound`, dropping `4c`/`11`. **But that result lands in the NULL SUB-BLOCK only**
(`null_block["assessment"]`). It does **not** reach `science`, and it does **not** reach
`scientific_acceptance`. Declaring `ε` changes the null assessment and changes **neither** field the
goal's success conditions name.

---

## ⚠ FINDING 2 — `ε` CANNOT BE DERIVED WITHOUT `S`, WHICH IS A SCIENTIFIC DECISION

`z_contract.py:243-248`, the withheld boundary's own reason:

> *"Needs an operating-error bound **B** with stated assumptions and confidence, an **independently
> justified scientific cap S**, the precondition **B ≤ S**, and an epsilon argued **within [B, S]**.
> **Neither B nor S is established.**"*

`NAVIGATION-20260917:12-13` and `:82-84` agree and widen it: *"`B`, `S` (in full) and `ε` are **all
open**"*, and *"`B`, `S` — **in full**, not only the F7 channel — and `ε` are open. `ε = 1e-9` is
**PROPOSED** and…"*

**The goal's step 3 supplies B, not S.** P0's measured run-to-run noise — `3.27e-16` at the first
checkpoint, `5.33e-15` on `x_cv` — is exactly an **operating-error bound**. **`S` is an independently
justified *scientific* cap**: how much null violation is scientifically acceptable. That is a
scientific acceptance threshold, which is Joseph's reserved class of decision, and it cannot be
derived from run-to-run noise without making the measurement pick the criterion.

**Also open and also his:** `NAVIGATION-20260917:30` records **THE OPEN RULING**,
`c4baf0d29297de0d0f50d5ea1d8b869ddaf83520` §19.8 — *does a pre-dating tolerance transferred from a
different subject satisfy `SPEC` §3.6a item 3?*

---

## The inventory, as the route asked

| criterion | state for `z-cv.npz` | open? | whose |
|---|---|---|---|
| `scientific_acceptance` | `NON-PASSING` — **hardcoded, not computed** | **structurally unreachable** | Joseph (material change) |
| `outcome.assessable` | `False` — **hardcoded** | **structurally unreachable** | Joseph (material change) |
| `reject_conditions` | `["4c"]` — **hardcoded** | — | — |
| **`null_epsilon` / 4c** | **WITHHELD** | **OPEN** | Joseph |
| **`B`** — operating-error bound | **not established** | **OPEN** | derivable; P0 gives the input |
| **`S`** — scientific cap | **not established** | **OPEN** | **Joseph — scientific threshold** |
| `B ≤ S`, `ε ∈ [B, S]` | unevaluable without `S` | **OPEN** | follows `S` |
| **open ruling §19.8** (`c4baf0d2`) | pre-dating tolerance vs `SPEC` §3.6a item 3 | **OPEN** | **Joseph** |
| `cause3_agg/med/corr`, both coverages, `cause2_f7_margin` | declared | closed | — |
| C1–C7 | closed (C7 closed 2026-09-19 under the ruling) | closed | — |

---

## Outcome: **(C) BLOCKED**, at step 1, **zero compute spent**

**Two independent blockers, either alone sufficient:**

1. **No new build can produce `PASS` or `assessable: true`** — those fields are constants, so the
   goal's (A) and (B) are both unreachable by running a job. Changing that is a material change to
   how acceptance is decided.
2. **`ε` cannot be derived**, because `S` — an independently justified *scientific* cap — is
   undefined, and deriving it from the run-to-run noise that `B` already measures would let the
   measurement choose the criterion. The `§19.8` ruling is also open and also Joseph's.

**Not attempted and deliberately so:** no job submitted, no `ε` declared, no edit to `z_build.py`,
`z_contract.py` or the tripwire test. **`SPEC` stays frozen; no amendment or exception written.**
