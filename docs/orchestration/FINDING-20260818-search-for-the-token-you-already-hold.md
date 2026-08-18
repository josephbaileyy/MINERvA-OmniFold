# FINDING 2026-08-18 — a search for the token you already hold is the cheapest one available

**BEN-451.** Lane D (verifier). **Filed at lane A's insistence that it be a rule rather than a
confession**, which is the right call: the instance is mine, the transferable form is not about me.

## The rule

> When a search fails, ask what **string you are already holding** and whether you have searched for
> **that**. A token in hand — a path, a digest, an id, an error message — is the highest-yield query
> available and costs one command. **It is also the one most often skipped, because holding it feels
> like already having used it.**

## The instance

Chasing `BEN-259` I needed to know whether the 9.9 GB G2 dump had a copy off purgeable scratch. I:

1. ran `git ls-files` on the two directories the dependency chain led me through — receipts, no payload;
2. ran a `find` over CFS — **killed**, then a bounded re-run that timed out at 90 s and found the copy;
3. hashed it, 9.9 GB, and matched it to the pin.

Then lane A found, in **one `git grep`**,
`docs/orchestration/state/restore-step1-g2-durability-20260804.json` — committed, `verdict: PASS`,
dated two weeks earlier, **naming both paths**, with the reason stated. `minerva-shutdown-stage`
appears in **8 tracked files.**

**I had the CFS path in hand from step 2 and never searched the repository for it.** I searched the
filesystem the path pointed into, and not the repository I was standing in. The answer was one
command away and already written down, by someone who had done the work deliberately and recorded it.

## Why it is skipped, which is the part worth having

The other searches all felt like *work*: enumerate the chain, walk the tree, hash the bytes. Grepping
for a string you are already looking at feels like it cannot tell you anything you do not know —
**because the token feels like the answer rather than like a query.** It is a query. What it returns
is not the token; it is **everyone else who has ever mentioned it**, which is exactly the thing an
enumeration over structure cannot reach.

**The structural reason it works here:** the repository indexes by *content*, and a preservation
receipt filed under `state/` is not on any dependency path from the artifact that depends on it. No
walk of the chain reaches it. Only a content search does — and the content is the token.

## Companions

Same failure family, different query defect, all found by the other lane:

| defect | example |
|---|---|
| wrong **predicate** | *"which launchers pass `--seed 1000`"* cannot enumerate those that pass none |
| wrong **spelling** | `unified_throw_cov\.py` excludes `unified_throw_cov_5d.py` |
| predicate changed **mid-search** | broad file filter, narrow line filter; candidates admitted then discarded |
| **corpus** unstated | a count over a mutable tree without a ref |
| **token in hand, never queried** | **this row** |

The first four are wrong questions. **This one is a question never asked**, and it is the cheapest of
the five to fix.

## The check, such as it is

Not a lint — it is a habit with one prompt, asked when a search comes back empty or expensive:

> **What am I already holding, and have I grepped for it?**

Costs one command. If the answer had been *"nothing"*, the cost is one command. Here the answer was a
committed `PASS` receipt that made a 9.9 GB hash unnecessary for the question it was run to settle —
though not for the one it did settle, since only the hash says **the bytes match** and the receipt
only says **the copy was intended and recorded.**

## Family

- `BEN-255` — a check on the wrong population. Here: the wrong *corpus* — filesystem where the
  answer was in the repository.
- `BEN-259` — the row this came out of; amendment 1 records the miss.
- **`BEN-451`** — the cheapest available search, skipped because holding the token feels like having
  used it.
