# PREDECLARATION — read `hRowIndex4D` out of the closed object and verify it

**Committed BEFORE execution.** Lane B, 2026-08-16. Supersedes
[`PREDECLARATION-20260816-c4-persisted-projection-identity.md`](PREDECLARATION-20260816-c4-persisted-projection-identity.md),
which I withdrew before running it: the identity it proposed already existed, had already returned
`ESTABLISHED`, and could not have come out differently because both covariance objects are
bit-identical in content to the ones audited on 2026-08-10.

---

## 1. The gap, named by the audit that left it

`20260810T0630Z-cross-object-verdict.json`, `gaps_remaining[0]`:

> *"Exact covariance-row to physical-bin labels remain unaudited. A verified `hRowIndex4D` of length
> 4825 matching the independently derived effective4 index vector…"*

`hRowIndex4D` was written into the product **that same day** — `p4_project_4d.py:186`, *"ITEM 2 of the
narrow freeze lift (2026-08-10)"*, added because *"both product-audit legs could only test row
alignment INDIRECTLY without it"* — and **has never been verified in the six days since.**

**Why the existing receipt field cannot close it.** `p4_project_4d.py:226-227` computes
`row_index_sha256` from `np.ascontiguousarray(np.nonzero(m4_eff)[0].astype(np.int64)).tobytes()` — the
**same in-memory array** used to write the histogram three lines earlier. It hashes the *intent*, not
the *artifact*, so it cannot detect a write that did not land, a truncated `TH1D`, or a wrong bin
offset. Two digests of one array are not two digests. (Lane A is carrying the receipt-side fix under
`OI-129`; this run is only the measurement of whether it matters today.)

## 2. What is measured

Read `hRowIndex4D` out of the **closed** file and compare it to an **independently derived**
effective-4D index vector.

**The derivation is independent of `p4_lib`, of `build_projection_M`, and of `AXIS_EDGES`' values.** The
index set needs only the grid *shape* and the two central supports — not bin widths:

* 5D grid `14 × 16 × 7 × 7 × 6 = 65856`; 4D grid `14 × 16 × 7 × 7 = 10976` (`grid_nbins` in the
  manifest; cardinalities confirmed by the Aug-10 audit's own independent count).
* `W_AXIS = 4` is the **last** axis in C order, so a 5D flat index maps to `i5 // 6`.
* `m5 = central5.hXSecND_flat > 0`, `m4 = central4.hXSecND_flat > 0`.
* `reachable = unique(i5 // 6 for i5 in nonzero(m5))`; `effective4 = nonzero(m4 & reachable)`.

No widths enter, so this leg is **not** exposed to the `AXIS_EDGES` question at all — which is a
strictly better position than the withdrawn proposal was in.

## 3. `falsified_by` — observations that would show a defect PRESENT

| # | observation | meaning |
|---|---|---|
| G1 | `hRowIndex4D` read back ≠ independently derived `effective4` | the row labels in the object are wrong |
| G2 | `len(hRowIndex4D)` ≠ 4825, or `TH1D` bin count ≠ 4825 | truncated or mis-sized write |
| G3 | sha256 of the **read-back** int64 array ≠ the receipt's `row_index_sha256` | the artifact disagrees with the intent it was hashed from |
| G4 | `m4 & ~reachable` ≠ exactly `{9679, 9686, 9714, 9721, 10169}` | the excluded set differs from the recorded one |
| G5 | any bin content non-integral, negative, non-monotonic, or ≥ 10976 | corrupt index vector |
| G6 | the 4D product's `sha256` differs before vs after | the check was not read-only |
| G7 | the mutation control does **not** fire | instrument cannot detect a defect; **no PASS may be reported** |

`G1`/`G3` have a reachable other outcome: a bin-offset error (ROOT's `SetBinContent(i+1, …)` vs
0-based) shifts every entry, and a truncation shortens the array — neither produces agreement.

## 4. Conditions (1, 3, 5-9 of the prior brief; 2 and 4 do not apply)

1. Read the array **out of the closed file**, never from an in-memory reconstruction of it.
2. *(n/a — no matrix product, so `_block_sum_projection` is not involved.)*
3. **Mutation control in the same run**: perturb one entry of an in-memory copy; the comparison must
   fire. Per `G7`, a non-firing control voids the PASS.
4. *(n/a — no tolerance; this is an exact integer comparison, which is why no threshold is
   predeclared. An exact comparison needs no tolerance and must not be given one.)*
5. **Read-only made falsifiable**: `sha256` the 4D product before and after, record both, require
   equality. `TFile` opened `READ` only; no `UPDATE`, no `RECREATE`; no stage invocation. **The 39.4 GiB
   `C5` is not opened at all** — its recorded digest is carried forward rather than re-hashed, and the
   receipt says so rather than implying it was checked.
6. Cross-check the recorded unreachable indices and `row_index_sha256`.
7. **Assert** length 4825 rather than assuming it.
8. **Write set: exactly one new receipt JSON** under `docs/orchestration/state/`, plus a force-added
   log (`KNOWN_ISSUES 48`). Nothing else.
9. Record the **read-back** digest so the next run detects drift instead of re-deriving this gap.

**Plus, for this run specifically:** a covering `git grep` — unrestricted, with the patterns stated in
the receipt — before any negative sentence appears in it. That discipline is here because its absence
is what produced the withdrawn proposal.

## 5. Scope of what a PASS licenses

**Only: that the row-label vector stored in the 4D product equals the independently derived effective-4D
index set, today, for this object.** It closes `gaps_remaining[0]` of the 2026-08-10 audit for these
products.

It does **not** license adoption or promotion (construction is not adoption; the five Gate-6
prohibitions at `19585b7` stay live); does not revalidate the identity (already `ESTABLISHED`, and
transferred by content bit-identity, not by this run); does not address `M`, the geometry, or
`W_AXIS = 4` being unpinned at `p4_project_4d.py:27` — which is for repair-12 or a follow-on, raised
with lane C rather than edited into the surface here; and does not repair the `row_index_sha256`
self-reference, which is `OI-129`'s.
