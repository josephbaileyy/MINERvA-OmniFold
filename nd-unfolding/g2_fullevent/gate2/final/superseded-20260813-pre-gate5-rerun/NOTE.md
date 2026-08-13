# Superseded 2026-08-13 — archived for the Gate-5-driven Gate-2 re-run

These are the products of the 2026-08-05 Gate-2 canonical runtime run (job `56344268`, `g2reissue2`,
`COMPLETED 00:55:32` on `nid004178`), promoted 2026-08-13 with both promotion requirements closed.

**Why they were archived rather than kept in place.** Gate 5's replica architecture needs
`build_fullevent_loaders` to distinguish a replica's OWN negweight-refined target from the nominal's,
which means editing the loader — and the loader is pinned by the receipt archived here AND by
`run_gate2_target_validator.sh`'s `EXPECTED_LOADER_SHA`, whose own file is in turn pinned by two
launchers. A three-deep chain.

**Joseph decided (2026-08-13 ~02:25 EDT) to RE-RUN Gate 2 rather than re-digest the pin**, and to gate
the re-run on the new weights coming out **BIT-IDENTICAL** to these. Identical means the
`bootstrap_seed` branch is provably inert on the nominal path and Gate 4 stands untouched. NOT
identical means a real defect, and the campaign stops.

The basis was this validator's own header, which records the same situation on 2026-08-04 and
2026-08-05 and both times re-ran rather than re-digested — the second time explicitly refusing to
"argue the change was semantically inert for the negweight-refined path, which is exactly the
reasoning hash pins exist to reject."

**Digests, so the bit-identity claim can be checked against these rather than against a memory of them:**

| file | sha256 | bytes |
|---|---|---|
| `G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy` | `544b2f6a2451480abfe867aede35d31a07178d518754428f43b00b26793d54c9` | 18723004 |
| `G2_GATE2_TARGET_RUNTIME_RECEIPT.json` | `336e8e27fc8afce813f3ee743c6466ea047243c6e4f457e1d040868d5800792f` | 12051 |

The `.npy` digest is also `VL87` in `VALIDATION_LEDGER.md` and the receipt digest is `VL89`, so both
are independently recorded outside this directory.

**Nothing here is deleted.** Copied, verified by digest and size, and only then removed from the live
paths — never `mv`, because a short write on a full filesystem would have lost the only copy of a
certified 18.7 MB product.
