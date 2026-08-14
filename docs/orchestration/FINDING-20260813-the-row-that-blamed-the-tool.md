# A finding that blames the tool is a suppressor

**Indexed from `FINDINGS.md` as `BEN-208`, which is itself the instance.** Pairs with `BEN-221` (a
premise recorded as `private` that ended inquiry without raising an error) and `BEN-207` (a PRESENT
verdict is a statement about the search).

## What happened

A `peer_request` arrives carrying two adjacent attributes:

```
from="uds:/var/folders/.../peer-mesh-501/req-70005-8b1ea196ef.sock"   <- addressable
from-name="Codex"                                                     <- a label
```

I replied with `SendMessage(to="Codex")` and got:

```
No agent named 'Codex' is reachable.
```

**I read that as a statement about the transport.** It is a statement about my argument. The tool's own
description says, in terms: *"To reply to an incoming message, copy its `from` attribute as your `to`."*
I had that instruction available and used the field next to it.

**Measured afterwards, at codex's request:** `SendMessage` with `to=` set to the literal
`uds:/var/folders/.../req-70005-2c7ce9d61b.sock` returns `success: true` with a `msg_id`. A raw socket
write to the same address also succeeds. **Two-way peer-mesh transport was healthy the entire time.**

## Why it is worse than a wrong row

I did not merely record the wrong diagnosis. **I filed it as a finding, and then acted on it.**

- The row instructed future agents to *"treat `peer_request` as one-way; reply via the human or the
  tree."*
- On that belief I began **re-routing codex's Gate-5 reconciler audit to lane D**, and told the user
  the reply had bounced.
- **Joseph's manual relay is the only reason that audit ran.** It returned seven confirmed defects,
  including that `reconcile_gate5_family.py` emitted exact `FAMILY_COMPLETE_PASS` on `--n 0` — the tool
  that gates promotion of the campaign's `C_stat` family.

**A false transport finding came within one manual relay of costing the campaign its only independent
verification.**

## The mechanism, stated so it is checkable

**An error message that names a real, specific, controllable mechanism reads as a lead rather than as a
prompt to check the premise.** *"No agent named 'Codex' is reachable"* is true, precise, and about the
wrong thing — it describes the resolver's view of the string I supplied, not the reachability of the
peer.

This is the same shape as `BEN-153` (a `JobArrayTaskLimit` reason string that could not literally be
true at 2 running against a throttle of 10, and cost two lanes their first hypothesis) and of
`BEN-149`'s `_verified_input_sha256`. **The common property: the output was accurate and the reader
supplied the scope.**

## What makes a *finding* the dangerous form

A wrong belief in a message dies with the session. **A wrong belief in `FINDINGS.md` is read by every
future agent as established, and this one carried an instruction not to try.** `BEN-221` — filed by
lane A four hours earlier, on the same day — established that `private` is *"the one attribute that
ends enquiry without raising an error."* **`structurally one-way` is that attribute, authored rather
than inherited.**

A's untested premise came from an advisory it did not write. Mine I wrote myself, from a single
observation, and indexed.

## The check

- **When a bounce names your argument, test the argument before describing the system.** One
  substituted field is cheaper to check than a transport is to characterise.
- **Before filing a row that says a capability does not exist, exercise the capability.** A row
  asserting absence is a statement about the search (`BEN-086`, `BEN-207`), and filing promotes it to a
  statement about the world.
- **Adjacent fields are the hazard.** `from` and `from-name`; `_verified_target_sha256` and
  `_verified_input_sha256`; `M_PION_EAVAIL` and `M_PI`. Naming the field you copied, out loud, is the
  whole check.

## Retraction discipline

The original wording is preserved **verbatim inside the row** rather than deleted, per the
`OI-57`/`OI-58` precedent: *a retraction that erases its own text leaves nothing for anyone who already
acted on it* — and here at least one agent had, namely its author.

## Related

`BEN-221`, `BEN-207`, `BEN-153`, `BEN-149`, `BEN-086`, `BEN-183` (the right command against the wrong
object).
