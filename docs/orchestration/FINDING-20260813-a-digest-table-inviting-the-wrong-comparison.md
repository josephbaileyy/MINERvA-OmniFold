# FINDING 2026-08-13 — a retirement convention and a certifying digest cannot both hold

**BEN-158.** Lane C (PET), while retiring an archived Gate-2 receipt routed from lane A.

**One-line version:** `NOTE.md` publishes a digest table headed *"so the bit-identity claim can be
checked against these rather than against a memory of them"* — and the receipt sitting **next to that
note has never had the digest in its own row.** A reader doing exactly what the note invites gets a
mismatch and would reasonably conclude the archive is corrupt.

## The routed task, which was the easy half

`gate2/final/superseded-20260813-pre-gate5-rerun/G2_GATE2_TARGET_RUNTIME_RECEIPT.json` sat inside a
`superseded-*` directory with `status: PASS`. The supersession was recorded in the **directory name**
and in **`NOTE.md`**, and never in the file. Anything reading the file rather than the path read it as
live — and a reader grepping for `PASS` is doing precisely that.

Lane A's defect was the mirror image: a Gate-4 *successor* that named its predecessor while the
predecessor itself was never marked. **Same failure, opposite half.** A's template applied verbatim:
`status: SUPERSEDED` + `superseded_by`/`_on`/`_why`, block renamed to `code_at_issue`, and digest
preservation **asserted rather than claimed** — the conversion refuses to write unless the digest
multiset is identical. 13 values, unchanged. `verdict` deliberately left alone: it states what that
run found, which is still true; `status` is the live-vs-retired axis.

`test_archived_gate2_receipts_hold_no_live_bindings` now passes; that file is 6 of 6.

## The half that was not on the ticket

`VALIDATION_LEDGER.md` VL89 certifies `receipt sha256 = 336e8e27…`. Measured, every version that has
ever existed:

| file | commit | sha256 |
|---|---|---|
| live `gate2/final/…RECEIPT.json` | `3d4cbdb` 07-19 | `f09db8fc…` |
| live `gate2/final/…RECEIPT.json` | `8a9d22c` 08-05 | **`336e8e27…` ← VL89** |
| live `gate2/final/…RECEIPT.json` | `fb3a4f9` 08-13 | `8b858622…` (the re-run's own receipt) |
| archived copy | `fb3a4f9` 08-13 | `23935993…` — **on its first commit** |
| archived copy | today | `c959a3a8…` after the `status` marking |

**The archive was never byte-identical to the certified digest.** The `sha256` → `sha256_at_issue`
rename happened *as part of the archiving*, in the same commit that created the directory. So the
mismatch predates my edit by twelve hours; my supersession marking moved it a second time.

**VL89 is not wrong.** It certifies the 08-05 re-issued receipt, that is exactly what it says, and the
bytes are still recoverable — verified, not asserted:

```
$ git show 8a9d22c:nd-unfolding/g2_fullevent/gate2/final/G2_GATE2_TARGET_RUNTIME_RECEIPT.json | sha256sum
336e8e27fc8afce813f3ee743c6466ea047243c6e4f457e1d040868d5800792f
```

What was wrong is that **nothing on disk said so**, while `NOTE.md` actively invited the wrong
comparison. No digit of any digest was changed to fix it: VL89's *quantity* cell now names which
receipt, which commit, and that no file on disk carries it; `NOTE.md` carries the caveat and the
recovery command above.

## The tension, stated because it will recur

> **A retirement convention that annotates a file in place cannot coexist with a ledger digest that
> certifies that file's bytes.** One of the two has to give, and it must not be the digest.

Lane A's template never hit this because A's receipts live in `docs/orchestration/state/`, which
nothing digest-certifies. Gate-2 runtime receipts *are* certified, by VL89, so the same convention
that makes `verify_hash_bindings` green makes the ledger row uncheckable against the file.

Three ways out, and the third is the one this finding recommends:

1. **Don't annotate archives** — keep them byte-frozen and exempt the directory in the checker.
   Rejected: the archive was already annotated on arrival, and un-annotating it re-breaks the
   verifier.
2. **Re-digest the ledger row.** Rejected outright — that is the antipattern every hash gate in this
   repo exists to catch.
3. **Make the certifying row name its own recoverable location.** A ledger digest whose bytes live
   only in git history is fine *provided the row says so.* That is cheap, changes no value, and is
   what was done.

The general form is the same lesson as the whole day: **an archive's provenance has to travel in the
artifact, not in its neighbourhood.** Directory name, sibling `NOTE.md`, and a successor's commit
message are all *neighbourhood*.

## Related

- `BEN-156` — "committed" and "running" are two different facts; the deployment half of the same idea.
- `BEN-157` — the verifier trusting claims instead of measuring; `OI-65`.
- Lane A's Gate-4 retirement at `5ad5ac7` — the mirror-image half, and the template used here.
- `VALIDATION_LEDGER.md` VL89; `NOTE.md` in the archive directory.
