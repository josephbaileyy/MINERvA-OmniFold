# FINDING 2026-09-19 — the build-time `cv_held_fixed` tests a different proposition than its name

**CITABLE FOR:** the measurement below and its consequence for reading a build-time outcome.
**NOT CITABLE FOR:** any grade. **Nothing is changed:** a production output of this goal exists
(`361090f9…`), so every criterion, boundary and reject condition is frozen. This is disclosure, not
a repair.

## 1. What was measured

The first real member built under the computed-acceptance path,
`z2m-products/member_k000000/z-cv.npz` (`361090f94446260f8fd78ad46214118ad2c9d43a3fbcef295b499c2bdbf7e214`),
came back with:

```
outcome branch    : 1  INCONCLUSIVE / WRONG FOOTING
branch1_failures  : ['cv_held_fixed']
branch2_failures  : ['offsets_match_K', 'offset_declared_nonzero', 'product_digests_distinct']
```

`z_build.build_validity` sets `cv_held_fixed = np.array_equal(x1, central)`, where `x1` is the
**null slab's `x_cv`** — this member's own internal CV execution, transcribed out of its throw
product — and `central` is the **declared production CV**,
`products/5d/xsec_5d_MEFHC_5iter_lgbm.root:hXSecND_flat`. Measured on this member:

| | |
|---|---|
| product `hXSecND_flat` **vs** archive central | **byte-identical**, digest `0f04abce…` both |
| null `x_cv` **vs** archive central | **differs in all 10,694 reported bins** |
| max abs difference on the support | `3.845e-40` |
| **relative L2 on the support** | **`5.20e-3` — 0.52%** |

**0.52% is not round-off.** It is the same background-treatment difference
`DECISION-PACKET-20260918` §12.4 already measured between the budget-era CV and the finalize CV
(*"values bitwise equal: False, max|delta| 4.470e-40, relative 9.055e-03"*). The member's internal
CV comes from the bkgaware sweep bank; the declared central is the archive product. They are not
the same object and were never going to be bitwise equal.

## 2. Why the field reads False, and what it should have been testing

`SPEC` §3.7b's branch-1 condition is **cross-member**: *"`x_i` is not held fixed at `k = 0`."* It
asks whether the central value is the same for every member. **One build cannot evaluate that**, and
under `R1` I bound the field to the nearest single-build proposition instead — *"the null's `x_cv`
is the declared central"* — and defended that binding in a review round as *"the check the comment
always cited"*.

> **The binding is sound as a claim and wrong as a name.** It is a real, checkable property; it is
> just not the property `cv_held_fixed` denotes, and on any real member it is **false by
> construction**. Every real build under this path will therefore report branch 1 with
> `cv_held_fixed` failing, for a reason that is not a footing failure.

## 3. What it does NOT affect, verified rather than argued

- **The campaign grade is untouched.** `z_grade.cross_member_validity` does not read the build-time
  `Validity` at all — it re-measures all nine fields from the members' own bytes, and its
  `cv_held_fixed` is `all(np.array_equal(m.central, base.central))` over the products'
  `hXSecND_flat`. That array is **byte-identical to the archive central** (measured above), and both
  members are built against the same central file, so the grade-time field will be **True** and
  branch 3 stays reachable.
- **No outcome changes.** A single-member build is non-MET regardless: the three genuine
  member-campaign fields fail. What the defect costs is the **reason** a reader is given — WRONG
  FOOTING instead of the honest VACUOUS BASELINE for a lone member.
- **The null itself is fine.** `r_null = 2.442e-13`, verdict **within bound** against `ε = 1e-9`.

## 4. Why it is not being fixed

Joseph's reservation, verbatim: *"Changing any declared boundary value, criterion, threshold,
reject condition, `S` or `ε` after ANY production output of this goal exists."* A `Validity` field's
meaning is a criterion, and `361090f9…` exists. **Frozen.**

The repair, when it is authorized, is one of two and the choice is the decider's:

1. **Rename and re-scope** the build-time field to what it tests — e.g. `null_cv_is_declared_cv` —
   and leave `cv_held_fixed` to the grader, which is the only place the cross-member question can be
   asked; or
2. **Drop it from the build-time `Validity`** on the same ground the three member-campaign fields
   are left `False` with notes: one build cannot establish it.

**Option 1 is the stricter of the two** — it keeps the measurement and fixes only the label — and is
this lane's recommendation, recorded for whoever holds the next authorization.

## 5. The shape this belongs to

A field whose **name** asserts one proposition while its **code** tests another, defended in review
because the code's own claim was true. The review round that produced it asked *"is this claim
justified?"* and got a correct answer to that question; nobody asked *"is this the proposition the
field is named for?"* — which is the question that fails here. It is
`a-claims-scope-is-the-scope-of-what-it-negates` one level down: the scope of a **field** is the
scope of the condition it is read as.

**Co-Authored-By: Claude Opus 5 (1M context)**
