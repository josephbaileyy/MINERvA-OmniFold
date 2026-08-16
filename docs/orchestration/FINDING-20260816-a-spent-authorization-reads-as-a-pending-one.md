# BEN-346 — a spent authorization reads exactly like a pending one, and the check I was about to propose for it is fail-open

**Date:** 2026-08-16 · **Lane:** B (adjudicating a mediator dispatch) · **Cost avoided:** 5.9 GPU-h and a duplicate scientific population
**Index row:** `docs/orchestration/FINDINGS.md`

---

## The instance

The mediator dispatched a confirm/deny on re-running arm 1 of the fold-forward closure, stating its
purpose was *"to complete arm 1, which has **never succeeded**"* — it *"died at ~2 min on a
float64/float32 promotion fixed at `4e85f0e`, never exercised on the cluster."*

**Arm 1 had succeeded the previous day.** `RECEIPT-foldforward-instrumented-closure-20260815.json`
reads arm 0 = `57012031_0/_1/_2` and **arm 1 = `57038937_3/_4/_5`**, three completed draws, all six
clearing `CLM-012`. Confirmed by the mediator in its own turn per `BEN-027`:

```
57038937_3  COMPLETED  01:56:59  0:0
57038937_4  COMPLETED  01:57:24  0:0
57038937_5  COMPLETED  01:58:29  0:0
```

The "never succeeded" claim is true of `57012031_3/_4/_5` — the **first** array — and false of the
second. Two lanes stated it; neither checked; it took a third running `sacct`.

## The mechanism, which is not `BEN-300`'s

`BEN-300` is *who holds a task* and *is the work already done*. This is narrower and sharper:

> **An authorization document is written to permit work that has not happened yet. Once the work
> happens, the document does not change. So its existence is evidence in BOTH directions and reads,
> forever, as the prospective one.**

`AUTHORIZATION-20260815-arm1-resubmit.md` was written *because* a resubmit was authorized — by the
same session that later cited its existence as evidence the resubmit was still pending. **The
document's existence was the strongest available evidence that the run had been dispatched, and it
was used as evidence that it had not.** The artifact even carried the backward link: the receipt names
the authorization *and its blob* in its own `authorizations` array, `0fb56af`.

This is a **time-direction** error on a document class this campaign produces constantly — 17 of them
so far — and it is invisible to re-reading, because nothing in the document is wrong.

## THE PART WORTH THE ID: the check I was about to propose is fail-open

Having found the instance, I drafted the obvious remedy — *"before re-issuing an authorization, grep
the receipts for it; the receipt records which authorizations it consumed."* It worked here. **I tested
whether it generalizes before proposing it, and it does not:**

| measured over `docs/orchestration/` | count |
|---|---|
| `AUTHORIZATION-*.md` documents | **17** |
| whose consumption is recorded in **any** JSON | **7** |
| for which the grep returns **nothing** | **10** |
| JSON files searched (widest scope: every `*.json` under `docs/orchestration/`) | 274 |
| carrying an `authoriz*` key at all | 47 |

**So for 10 of 17 the check returns empty, and empty would be read as "not yet consumed" — the exact
inversion that caused this.** A guard that answers "no" both when the thing did not happen and when
the format does not record it is `BEN-344` and `BEN-315` in the shape I had spent the same day filing
about. A narrower first pass over `state/RECEIPT-*.json` alone gave **2/17**, so the number also
depends on the search scope — and a remedy whose answer depends on how hard you looked is not a
remedy.

**The generalisation about this repo's paper trail:** it is written strictly **forward** — proposal →
predeclaration → authorization → receipt — and carries **no backward links**. Every artifact names
its antecedents; none names its consequences. So any question of the form *"has this been acted on?"*
is **structurally unanswerable from the document you are holding**, no matter how carefully you read
it. That is a property of the convention, not of any lane's diligence.

## What the authority actually is

**For "has this already run?", the authority is the scheduler, not the paperwork.** `sacct` over the
jobs the authorization describes is derived from the system of record; a job either exists or does
not, and the answer cannot be fail-open in the way a document search can. The mediator's own
`sacct` call is what settled this, and it cost one command.

Corollaries, all cheap:

* **Before re-issuing an authorization, run `sacct` for the work it describes** — not a grep of the
  docs. If the work is on the cluster, the cluster knows.
* **Treat an authorization as a single-use token.** Its consumption belongs *in the authorization
  document*, appended at consumption time, which is the only place a reader of that document will
  look. 10 of 17 currently record nothing, so this is a convention gap, not a lane's oversight.
* **When a dispatch rests on a premise about past state, put the confirmable fact first and make
  everything downstream conditional on it.** That is what stopped this: the mediator ran the `sacct`
  before finishing the message, precisely because the adjudication was ordered that way.

## And the honest note about my own contribution

I nearly filed a fail-open remedy as the fix for a fail-open reading. The only reason I did not is
that I measured whether it generalised before proposing it — the day's own rule (`BEN-345`: a filter
gets a test in the direction it acts) applied to a proposal rather than to code. **A remedy is a
claim and gets tested like one.** It took about two minutes and changed the finding's conclusion from
"grep the receipts" to "ask the scheduler," which are not the same advice and would not have failed
in the same way.

## Related

`BEN-300` (task state has no machine-derivable source; its second instance already says *ask the
artifact whether the change is in it* — this adds that for **consumption** the artifact usually
cannot answer), `BEN-344` (a null must be shown capable of being non-null), `BEN-315` (a null grep is
evidence about the search), `BEN-244`/`BEN-027` (agreement among restatements is not corroboration;
IDs come from a command in the same turn), `BEN-345` (the filter rule this applied to itself).
