# A task can FAIL with its products complete and correct — `BEN-023`'s mirror

**Lane E, 2026-08-18. `BEN-471`.** `57194054` finished **49 COMPLETED / 1 FAILED**. The failure,
`57194054_42`, exit `129:0`, elapsed `00:49:28`, **had written every one of its products correctly before it
died.**

`49 of 50` leads any reader to discard member 42. The products are sound.

## What was measured

```
stdout, last line:
  {"bootstrap_seed": 50042, ..., "status": "PASS",
   "target_sha256": "c96982b4e7f04e89a1d262ffefa310db3920eb2fc6c20736141c8765ccb943b9"}

products:    GATE5_REPLICA_TARGET.npy          18,723,004 B  + .npy.done
             GATE5_REPLICA_TARGET_RECEIPT.json      7,463 B  + .json.done
neighbours:  replica_41  18,723,004 / 7,468        replica_43  18,723,004 / 7,471
timing:      file mtimes 00:35   ==   job End 00:35:29
exit:        129:0  =  128 + 1  =  SIGHUP
stderr:      ends in a ROOT stack trace terminating at `_start`
```

The driver ran to completion, printed its PASS receipt line **with the target digest**, wrote both artifacts
**and both `.done` markers**, and produced an `.npy` byte-for-byte the same size as its neighbours' with a
receipt inside the family's size range. The signal arrived during interpreter shutdown.

## The check that made the conclusion safe

If the other 49 tasks had crashed the same way and merely exited 0, then COMPLETED-vs-FAILED here would be
luck rather than information — so that had to be ruled out, not assumed:

| task | stderr bytes | trace lines |
|---|---|---|
| `replica_41` | 1,164 | 0 |
| **`replica_42`** | **121,068** | **14** |
| `replica_43` | 1,164 | 0 |

One-off, in `_42`'s teardown only. **Ruling out the alternative is what licenses the reading** — without it,
"the products are fine" would have been a claim about one task with no comparison.

## Why this is `BEN-023`'s mirror and not a footnote

`BEN-023`: a resume guard **accepted an incomplete product because it existed** — `[[ -s $OUT ]] && skip` let
7 partial slabs permanently block their own repair. The remedy: **validate completeness, not existence.**

This is the same axis, opposite sign: a **scheduler verdict rejecting a complete product because the process
died after making it.**

> **A SLURM EXIT STATUS DESCRIBES THE PROCESS, NOT THE PRODUCT.**

And the two findings agree on the remedy, which is the useful part: **a guard that validates COMPLETENESS
would accept `_42`, and would be right.** So `BEN-023`'s rule is not merely a way to avoid a false pass — it
is also what stops a *false discard*. Existence-checking is wrong in both directions; completeness-checking
is right in both.

## The trap this sets, stated plainly

The obvious response to `1 FAILED` is to re-run the member. That is not wrong here — it is just uninformed,
and it costs ~49 minutes of the tighter allocation for a product that already exists. The reverse error is
worse and is the one to guard against: **treating `COMPLETED` as evidence about a product**. Nothing in an
exit code inspects an artifact.

In this instance nothing turns on it — the whole gen1 family is being discarded and rebuilt from a later
deployment, and nothing on scratch is being deleted — so this is recorded rather than acted on.

## The check to steal

- When a scheduler reports a failure, **ask what the products look like before deciding what happened.** The
  four cheap operands: the driver's own last stdout line, the presence of completion markers, the artifact
  sizes against a sibling's, and the file mtimes against the job's End time.
- **`exit != 0` and `product incomplete` are independent facts.** So are `exit == 0` and `product complete`.
  Four combinations, and a campaign that reads two of them is reading an exit code as a receipt.
- Before concluding a failure is a one-off, **check whether the same event is present-but-unreported in the
  successes.** Here it was not; had it been, the verdict split would have carried no information.

**Cross-references.** `BEN-023` (validate completeness, not existence — the mirror), `BEN-027` (every count
in a status report comes from a command run in the same turn), `BEN-028` (a quiet log does not mean a dead
job — the same category: judge by artifacts, not by a proxy), `BEN-415`/`BEN-417` (a verdict that does not
name its population).
