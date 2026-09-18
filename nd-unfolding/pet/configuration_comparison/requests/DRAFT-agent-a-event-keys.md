# DRAFT — not sent. Request to Agent A: three event-key branches

**Status: DRAFT.** Nothing has been sent to Agent A or to anyone else. Sending this is
Joseph's call.

**Addressed to:** Agent A, owner of `runEventLoopOmniFold.cpp` and its active-universe
production.
**From:** Publication Agent B (PET).
**This is an interface request, not an edit.** `FULL_EVENT_INTERFACE_REQUEST.md` states
that A owns the running C++ and that it must not be edited by us; this follows that rule.

---

## The ask, in one line

Emit three existing scalar quantities as branches under the existing
`MNV101_DUMP_POINTCLOUD` gate: **`ev_run`, `ev_subrun`, `ev_gate`**, on
`mc_signal_reco`, `data` and `mc_background`.

No new physics, no new getters, no change to any existing branch, and no change to
selection, weights or ordering.

## Why

The full-event point-cloud npz identifies rows **positionally**: `sig_identity_hash`,
`data_identity_hash` and `bkg_indices` protect the order but carry no event identity. The
MasterAnaDev tuples carry `ev_run`/`ev_subrun`/`ev_gate`.

We want to evaluate a reconstructed-object representation (photons, blobs, prongs) as a
candidate PET input. Every branch it needs already exists in the tuples. What does not
exist is any way to attach those objects to the estimator's rows, because the key that
would join them is not carried through the dump.

With the three keys, the join happens in our Python and the object vocabulary stays
somewhere we can iterate on it. Without them, the only alternative is to ask you to emit
roughly twenty-one typed-object vector branches — a much larger change to your running
production, and it would fix the vocabulary in C++ before anyone has measured whether it
helps.

## Exact deliverables, and what each unblocks

| deliverable | form | unblocks |
|---|---|---|
| `ev_run`, `ev_subrun`, `ev_gate` on `mc_signal_reco` | three scalar branches under `MNV101_DUMP_POINTCLOUD` | joining typed objects to MC estimator rows |
| the same three on `data` | same | the measured leg of the join |
| the same three on `mc_background` | same | the negweight-refined background leg |
| the production tag they first appear in | one line | knowing which dumps carry them |

**Dependency:** this gates the representation half of the comparison and nothing
else. The architecture-and-recipe half runs without it, on the token schema we
already dump, so a delay here narrows the comparison rather than stopping it.

## Scope and cost

* three scalar branches per tree, under the gate that already exists;
* no effect on any current consumer: additive branches, existing readers unchanged;
* our side absorbs the join and proves it — uniqueness, unmatched rows, native
  truth-only misses, ordering and inventory symmetry are all checked fail-closed
  (`identity_contract.py`, 14 tests).

## What we are not asking for

* No change to the FPS domain gate, `pass_reco`/`pass_truth`, weights or POT handling.
* No typed-object branches **at this stage**. If the representation later earns adoption
  we would come back, with evidence, about moving the extraction into C++.
* No change to the 12-token cap: that truncation is a **Python** choice in
  `dump_pointcloud_inputs._pad_tokens` and is ours to change.

## What we would send back

The join verification receipt, so the keys' usefulness is demonstrated rather than
asserted: matched and unmatched counts per inventory, the native-miss census, the
per-event order proof against the ROOT, and the provenance digests.
