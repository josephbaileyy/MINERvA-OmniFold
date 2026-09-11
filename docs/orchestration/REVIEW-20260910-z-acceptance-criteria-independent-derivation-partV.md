# PART V — pin 2 (`cc42cc3e`): BLOCK on the non-member return contract; the categories themselves are proved sound

**Owner:** independent-assessment lane. **Subject:** `cc42cc3e`. **Baseline:** Part T (`7b9214cd`).
**Prior verdict:** Part U (`08b1a9c6`) blocked on the enumeration's population. **No grade assigned.**

## VERDICT ON THIS PIN'S PORTION OF MY SLICE

> **My Part U BLOCK is DISCHARGED** — the population is now nine, the third category is warranted, and
> the universal is derived.
>
> **BLOCK — one new consequential issue: `enumerate_recomputation`'s non-member branch omits the
> coverage flag, so `covers_all_member_local` reads FALSE on a correct configuration.** That is the
> exact failure mode `:171-172` says the fourth category was added to prevent, surviving one branch
> over. Everything else on this pin is **READY**.

---

## V.1 — EXHAUSTIVENESS AND DISJOINTNESS: PROVED OVER THE WHOLE CONFIGURATION SPACE, NOT SAMPLED

Asked to verify the four categories are exhaustive **and** mutually exclusive over what `BuildPath`
can express. The space is finite, so this is provable rather than testable: `member_offset ∈ {None,
0, 7}` × `block_source ∈ {SHARED_DIGEST_BOUND, PER_MEMBER}`.

| `member_offset` | `block_source` | keys | exhaustive | disjoint | overlaps |
|---|---|---|---|---|---|
| `None` | `SHARED_DIGEST_BOUND` | 3 | ✅ | ✅ | — |
| `None` | `PER_MEMBER` | 3 | ✅ | ✅ | — |
| `0` | `SHARED_DIGEST_BOUND` | 8 | ✅ | ✅ | — |
| `0` | `PER_MEMBER` | 8 | ✅ | ✅ | — |
| `7` | `SHARED_DIGEST_BOUND` | 8 | ✅ | ✅ | — |
| `7` | `PER_MEMBER` | 8 | ✅ | ✅ | — |

**Exhaustive in all six; disjoint in all six.** The categories are sound.

**And I am supplying a property the code does not check.** `:176` computes
`covered = set(recomputed) | set(pinned) | set(must_populate) | set(not_used)` — **a union**. A union
tests **coverage** and is blind to **overlap**: if a component appeared in two categories,
`covered` would still equal the population and `covers_all_member_local` would still read `True`.
Disjointness holds today, by my measurement, and **nothing in the artifact would notice if it
stopped.** That is a gap in the self-check rather than in the categories, and it is one line.

## V.2 — THE BLOCKING ISSUE: THE COVERAGE FLAG READS FALSE ON A CORRECT CONFIGURATION

`:153-155`, the non-member early return:

    if not path.is_member:
        return {"recomputed": (), "pinned": MEMBER_LOCAL_TODAY,
                "note": "not a member of K: the archive path, nothing member-local"}

**Three keys.** The member branch returns **eight**. So `covers_all_member_local`, `uncovered`,
`must_be_populated`, `not_used` and `dominant_cost_terms` are **absent** on the non-member path.
Measured, on a fully specified and entirely correct non-member `BuildPath`:

    r.get("covers_all_member_local", False)  ->  False
    r["covers_all_member_local"]             ->  KeyError

**This is the fourth-state defect, one branch over, arriving by absence instead of by a computed
value.** `:171-172` states the reason the `not_used` category exists: *"Without this the coverage flag
read False for a configuration that is fully specified, **which would have looked like the omission it
exists to detect**."* That sentence is true verbatim of the non-member branch as it now stands.

**And it is worse on the majority path.** Non-member *is* the archive path — the normal production
run. A receipt that records the flag would record `False` (or crash) for every non-member run, so the
flag cannot distinguish a correct archive build from a defective enumeration, which is the only thing
it exists to do.

**The campaign has already ruled the right shape for this.** Joseph's Ruling 2 requires the inverted
dimension be marked **not applicable** rather than left blank, and `F22` was carried as **mandatory**
on exactly the not-applicable-versus-satisfied distinction. A flag that is **vacuously true** for a
path with nothing member-local is being represented by **absence**, and absence reads as `False`.

**I am not prescribing the representation** — `True`, an explicit `"not applicable"`, or a fifth
category are all available and the choice is the designer's. What I am stating is that **absence is
not one of the admissible options**, on the designer's own stated reasoning.

## V.3 — READY: MY PART U BLOCK IS DISCHARGED, AND ONE TRAP WAS AVOIDED THAT DESERVES SAYING

- **Population is nine** (`:111-121`), with `boot_nd_5d` `# :422` and `seedscan_split_5d` `# :423`
  added and flagged `⚠` with their declared id ranges.
- **The third category is warranted, not tidy.** `MEMBER_LOCAL_INPUTS_REQUIRING_POPULATION`
  (`:135-140`) carries `n=100` / `n=24` and `cost: "DOMINANT"`, and `:127-134` states the cost
  asymmetry and `:418-420`'s full-range refusal as the reason there is no cheap third option. That is
  my Part U reason 3 implemented rather than acknowledged.
- **The universal is now derived.** `:177` computes `uncovered` from `MEMBER_LOCAL_TODAY` rather than
  asserting over a hand-listed set, which was my Part U reason 2, and `:178-179` records why.
- **⚠ A trap avoided, and it is worth crediting because it fails silently.** `:88`
  `is_member` is `self.member_offset is not None` — **not truthiness.** `MNV_EST_SEED_OFFSET=0` is a
  real declared offset; I measured `est_seed_offset=0` in the member-scoped npz keys back in Part I. A
  `bool(self.member_offset)` implementation would classify offset `0` as **not a member** and route it
  to the archive path. My probe confirms `member_offset=0` returns the eight-key member form.

## V.4 — READY: ADDITIVITY HOLDS CUMULATIVELY

`git diff --name-status 6f24fb00..cc42cc3e`: eleven `A`, and the only `M` entries are
`CATALOG.md`, `MANIFEST-overrides.tsv` and `MANIFEST.tsv` — **the three router files the pre-commit
hook requires.** **No production `.py` modified.** The `RECREATE` / defaulted-`--out` hazards remain
untriggered and uncited-as-closed, as in Part U §U.3.

## V.5 — READY: SUITES RE-RUN WITH THE CONTROL FIRST

| suite | result |
|---|---|
| `test_z_validator` **[control]** | **136 passed** |
| `test_z_build_path` | **46 passed**, no skips |
| `test_z_contract` | **56 passed, 1 skipped** — the pre-existing lightgbm skip at `:628`, unchanged |

Matches the relayed figures exactly.

## V.6 — THE `U` QUESTION, TAKEN: THE EXCLUSION LEDGER IS DESTINATION-SCOPED AND THE EXTRAS ARE NOT

Offered rather than assigned; I take it, because it is a question about what population each arm is
quantified over and not about A-7's mathematics.

**The map-arm exemption is correct.** Arm 1 asks whether every reported source bin lands somewhere —
a property of a *partition*. An all-ones total-rate functional touches every source bin, so it cannot
orphan one, and arm 2 is vacuous for a dense row. Exempting the extras from the map arms is right, and
the `37 of 40` firing was a predicate applied to the wrong operand.

**But exempt from the map arms is not the same as needing no accounting, and the gap is measurable:**

- `:470` — `require_projection_support(M, declared_exclusions, …)`. The ledger is applied to **`M`
  only.**
- `:471-472` — `extras` are converted and `vstack`ed with no exclusion handling.
- `:307` — `declared_exclusions` are *"intentional, enumerated **destination rows**."*

So exclusions are **destination-row**-scoped while the extras are **dense over source columns**. A
declared destination exclusion therefore does **not** reach the extras — and for P2 the `[3,100] GeV`
catch bin **is** destination row 7. **So an all-ones total rate would include the support of a
destination row the displayed projection excludes**, and "total rate" and "sum of displayed bins"
would differ by exactly that bin's content.

**That may well be correct** — a total should plausibly be a total. **The defect would be leaving it
undeclared**, against Joseph's *"any exclusion must be explicit and accounted for."* This is a
two-ledger question: the ledgers currently record what `M` excludes, and nothing records whether the
extras honour or ignore that exclusion. **Which it should be is not mine to choose.**

## V.7 — `S2` HELD, AND WHAT I DID NOT ASSESS

- **`S2` still not triggered** — the projection maps are not in this pin either.
- **Not assessed:** the 1% threshold in either direction, terminal handling, `κ`, A-7's predicate
  mathematics, the claim-scoping / cause-3 question, and the **power** of the 46 tests. The reviewer
  holds enrolment power and has reported it `ast`-derived; I verified only that the suites run and
  pass.
- **Still open:** `A-6(a)`, `A-6(b)`, the excluded producing execution, the three-or-four block
  population.
