# FINDING 2026-08-13 — a rule consistent with its examples is not entailed by them

**BEN-182.** Lane D (verifier), from the design review of putting `verify_hash_bindings.py` into
`.githooks/pre-commit`. **The review itself is `VERDICTS-20260811-session-D.md` §V50** and is not
repeated here; this is the transferable mechanism.

## The rule and its evidence

Lane A extracted, from the pre-commit dispatcher's two documented exclusions:

> *A check belongs in the hook if and only if it can only fail on what THIS commit changed.*

It is a good-sounding rule, it is consistent with both exclusions, and **neither exclusion is an
instance of it.** The dispatcher's own header says why each is out:

| excluded check | the header's stated reason | is it about scope? |
|---|---|---|
| `generate_live_state.py --check-freshness` | *"returns 1 whenever `LIVE-STATE.md`'s sha is not HEAD's — a condition it **CANNOT ESCAPE**… A check that always fires is a check nobody reads, and putting it in a hook would train every lane to `--no-verify`."* | **No** — inescapability |
| `merge_guard.sh` | *"needs a lane argument and belongs at merge time, not commit time."* | **No** — wrong phase, missing inputs |

Both are whole-tree-ish *and* excluded, so the rule fits. But the property that did the excluding is
different in each case, and different again from the one the rule names. **Two points, three
properties, and the rule picked the one that generalises worst.**

## Why the wrong generalisation was expensive

The rule forbids, by construction, the exact category the work needed: **a whole-tree invariant that
should block everyone.** A code-freeze gate is that category — the evidence a gate passed against
specific code is worth what its weakest binding is worth, so its scope is global by definition. Having
adopted the rule, the design then had to add staged-diff scoping to satisfy it, and the scoping
introduced a day-one silent pass (§V50).

**The rule generated a requirement, the requirement generated a mechanism, and the mechanism had the
defect.** None of that traces to an error in the mechanism.

## The rule that survives the same two examples

> **A check belongs in the hook iff a committer who did nothing wrong can always make it pass.**

- `--check-freshness` — never passable. Excluded. ✔
- `merge_guard.sh` — not passable at commit time. Excluded. ✔
- `verify_hash_bindings` whole-tree — passable iff the tree is clean. **Admitted**, which the first rule
  forbids.

It also keeps the teeth the first rule had, in the right place: it **forbids** installing a whole-tree
gate while the tree is dirty and unwaived. That is a real precondition, and naming it as a precondition
is better than designing around it.

> **Check:** when a rule is derived from N examples, do not ask *"is the rule consistent with them?"* —
> ask, for each example, **which property actually did the work**, and whether the rule names that
> property. A rule consistent with every example and entailed by none is unfalsifiable against its own
> evidence, and it will be defended with those examples the first time it is questioned.

Related in shape: `BEN-174` (a summary stated more confidently than its source) and `BEN-179` (a
correction applied to the paragraph rather than the claim). All three are compression steps that
preserve truth locally and lose the thing that made it true.

## Named interest

I have an interest in this finding: the alternative rule is mine, and a reviewer who proposes a
replacement has a motive to overstate the defect in the original. Stated so it can be discounted —
**the load-bearing part is the table above, which is quotation from the dispatcher header, not my
reasoning.** If the header's two reasons are what they say they are, the first rule is not entailed by
them regardless of whether the replacement is any good.
