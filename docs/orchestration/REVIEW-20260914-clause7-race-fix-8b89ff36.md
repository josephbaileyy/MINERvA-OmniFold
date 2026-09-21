# Independent review: the clause-7 race fix, `79badb2f..8b89ff36`

**Owner:** `lane/z-criteria-independent-assessment-20260910` (independent assessor).
**Subject:** `lane/z-campaign-ownership-20260913` @ `8b89ff3601c990b6a75ccf6769255c236905e755`.
Coverage extends to that sha only. `a71087e3` verified unamended (tree `51583946`); `main` `9dba1194`.

## ⚠ PARTIAL RECUSAL, STATED FIRST BECAUSE IT IS TRUE

**I am not independent of the ordering choice in this fix.** I named the requirement and explicitly
declined to name a mechanism — but I then reported that `require_campaign_complete` "reads products
first and claims second" and that "clause 7 is the outlier, not the pattern," and that observation
became this fix's design rationale. Whatever my intent, **pointing at an existing exemplar is
supplying a mechanism**, and the fix adopted it.

The recusal is per-slice (`a-recusal-may-block-only-one-branch`):

- **NOT independent — do not read my verdict as certification:** the choice of products-then-claims
  ordering.
- **Independent, and reviewed normally:** the `_confirm_unclaimed` re-read (not mine), the two-premise
  correctness argument and premise (B) in particular (not mine), the test design, the mutation
  analysis, and everything in §3.

**VERDICT (on the slices I may judge): the fix works and the delta is sound. ONE FINDING — premise
(B) is now load-bearing for correctness, and both of its guards are narrower than the premise.** Not
a live defect: (B) is true today by whole-module measurement.

**NOT CITABLE FOR:** landing, launch, spend, or anything on Lustre. `R4` suspended; Gate 2 FAIL.

---

## §1 — The defect is closed, measured with the instrument that proved it

**My own probe — the one that proved the defect on `a71087e3` — no longer reproduces it.** Run
unchanged against `8b89ff36`, its defect arm now fails on `AssertionError: Exception not raised`:
the subject no longer refuses when a correctly-bound sibling completes in the window. The control
arm still passes. The instrument that established the finding no longer establishes it, which is the
strongest confirmation available to me.

**Site dispositions verified by AST, not relayed** — each function extracted from both shas and
compared:

| function | verdict |
|---|---|
| `verify_task_ownership` | DIFFERS — repaired |
| `require_campaign_complete` | **IDENTICAL**, byte for byte |
| `campaign_arm_status` | differs in text; **executable code IDENTICAL** — docstring-only, confirmed by comparing the ASTs with docstrings stripped |

So the claim of "+8 docstring lines, 0 code lines" is exact.

**On the declared deviation** — the eight docstring lines added to `campaign_arm_status` against an
instruction to leave it alone. **I agree with it and would not revert it.** Zero code lines, and it
records that the skew was seen, weighed and left, with the view/gate distinction that makes it
correct. A future reader "fixing" it for symmetry is a real hazard, and an undocumented correct
decision is the one most likely to be undone. Declaring it rather than letting it pass is the right
handling.

---

## §2 — FINDING: premise (B)'s guards are narrower than the premise

The correctness argument is: read products at t1, claims at t2 > t1; a product seen at t1 was
published by t1; by **(A)** claim-before-publish its claim is strictly older; by **(B)** claims are
never deleted, that claim still exists at t2. **(B) is what makes the ordering *sufficient* rather
than merely better** — it is doing real work, and it is new.

**(B) is TRUE today, and by a stronger measurement than the one cited.** I swept the whole module by
AST for every deleting or moving call. There are **three**:

```
:656   _atomic_write_json   os.replace(temporary, path)     # publishes its own temp
:659   _atomic_write_json   os.unlink(temporary)            # its own temp, failure path
:2423  recover_task         os.replace(product, target)     # the partial output -> evidence
```

None touches a claim. Claims are written **only** by `_write_json_exclusive` at `:1925`, and
`os.replace` is never pointed at the claims directory. So (B) holds module-wide, not merely on the
recovery path.

**But both of its guards are narrower than the premise they support:**

1. **The AST ban** (`test_NOTHING_IN_THE_MODULE_UNLINKS_A_CLAIM`) is scoped to **seven named
   recovery functions** — deliberately, because a module-wide version fired on `_atomic_write_json`
   unlinking its own temp.
2. **The behavioural arm** (`test_FACT_B_the_claims_set_only_GROWS`) observes that claims grow across
   five happy-path tasks. It never exercises a deleting path, so it cannot detect one.

**Demonstrated, not argued.** I added a claim-deleting helper *outside* the recovery function set —
`def _tidy_claims(paths, arm): os.unlink(paths['claims'])` — and ran the ban:

```
result: OK          <-- premise (B) silently broken, nothing fails
```

**Severity: not a live defect; a durability gap in the protection of a newly load-bearing
invariant.** A future claim deletion added anywhere outside those seven functions breaks the second
leg of this fix's correctness argument with no test failing. That matters more now than it did
yesterday, because before this fix (B) was a design preference and now it is a premise.

**Requirement, not a remedy:** either the guard that supports (B) must cover the claim path wherever
it is touched, or (B) must be restated to what the guards actually establish. I am deliberately not
naming the mechanism — the existing scoping exists for a real reason (the `_atomic_write_json` false
positive), so widening is not free, and having already supplied one mechanism in this thread I am
not supplying a second.

---

## §3 — The mutation limitation: independent sufficiency is REAL, not a harness artifact

I was asked to judge whether M8/M9 passing is genuine. **It is genuine**, and each half is
independently sufficient for a reason:

- **M9 (products-first, no re-check) passes** because the ordering argument *alone* is sufficient
  given (A) and (B). That is exactly what the argument claims, so M9 passing is the argument being
  true, not the harness being blind.
- **M8 (claims-first, re-check kept) passes** because the re-read is strictly later and claims only
  grow, so the phantom is removed before the refusal. Also genuinely correct.

**So the arm cannot kill either half alone, and that is a property of the design rather than a weak
test** — the same situation as the two independently sufficient naming guarantees in the temp-file
repair, which this owner documented then too.

**Is a fix whose test cannot detect the loss of either half adequately guarded? Yes, here — because
the protection is structural rather than behavioural, and I checked that it exists:**
`test_the_READ_ORDER_IS_PRODUCTS_THEN_CLAIMS_in_the_source` pins the order in the source, and
`test_the_REREAD_is_a_NO_OP_when_the_ordering_argument_holds` plus
`test_the_REREAD_KEEPS_a_product_that_is_still_unclaimed` pin the re-check in both directions. When
neither half is individually *necessary*, a behavioural mutant cannot reach them and a structural pin
is the right instrument. Both are present.

**Premise (A) is bound to the real producers, not only to the wrapper** — the concern I was asked to
check. `test_FACT_A_holds_in_the_REAL_PRODUCER_too` reads the source of `do_blockunits` and
`do_throws` and requires the contract, and therefore the claim, to be taken before anything is
written. It is a source-text instrument rather than a behavioural one, which is weaker — but it is
the honest one available without executing the real producer, and it is framed that way rather than
overclaimed.

**Also verified:** the claim create at `:1925` is the last substantive act of
`verify_task_ownership`, which is what (A) asserts of the library call.

**Both self-caught errors are the right shape.** A positive control failing *with* all three mutants
— four identical failures from a harness that copied the tree without `.git`, so
`mnv_source_manifest.build` could not run `git ls-files` — reads exactly like four detections, and
catching it required noticing that the control failed too. And a first detecting arm that detected
nothing, because it completed the sibling *before* the claims snapshot where both orders agree: *"a
test that cannot fail on the pre-repair code is not evidence about the repair."* That is the same
lesson as the `sys.path` defect, in-process.

**Counts verified, not relayed:** read_ordering **17 OK**, recovery **65 OK**, ownership **89 OK**,
precursor **123 OK**, z_build_path **90 OK** — **384**, matching the five named components of the
relayed 635. I did not re-run the remaining two suites (see §4).

---

## §4 — Withheld

**Cluster access is still dead** (rc=255; sshproxy certificate dated Sep 13 08:42; controlmasters
empty), so unchanged from the previous record and not re-attempted:

- **cross-client `O_EXCL` on Lustre** — the case a multi-node array actually exercises;
- **`os.mkdir` EEXIST on Lustre**, a different primitive to which my single-client `O_EXCL`
  measurement does **not** transfer.

The narrowed caveat now in `_write_json_exclusive` states the measured/unmeasured line exactly as I
scoped it, including that the two-node attempt was destroyed by my own cleanup and disclosed as such.
It attributes the measurement to the reviewer rather than claiming it, which is correct.

**Not re-run:** the two remaining suites of the seven-suite 635 total. **Not assessed:** the owner's
questions 3–7, which remain Joseph's.
