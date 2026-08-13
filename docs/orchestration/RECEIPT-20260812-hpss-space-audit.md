# RECEIPT — HPSS space audit, read-only (2026-08-12)

**Why.** Joseph, verbatim via the mediator: *"try to reduce HPSS space when possible, I am exceeding my
allocation"*. This is the audit half. **Nothing was deleted and this script has no delete path.**

**Bottom line, stated first because it changes the decision:** there is **no cruft on HPSS**. Total
residency is **1,457,304,348,109 B (1.4573 TB) across 279 files**, and **99.9999989% of it is two campaign
archives**. The entire non-campaign contents are **15,694 B — 0.0000011% of residency.** The only byte-identical duplicate pair in
the whole archive is worth **12,334 B**. **Reducing HPSS space therefore means deleting campaign physics
data — there is no housekeeping option.** That is a decision for Joseph, per item, and it needs a number
nobody has yet: **the allocation itself.**

## Provenance

| field | value |
|---|---|
| script | `docs/orchestration/hpss_space_audit.sh`, sha256 `e260ab36…` at transfer time (superseded by later edits; see git history) |
| run host | `login11` (NERSC), `hsi` at `/usr/bin/hsi` |
| raw output | `docs/orchestration/state/hpss-space-audit-20260812.txt`, 80,634 B, sha256 `031ff1238886dbb787363493550f9e06db69a5edc5da334020c8d3aab9559c7d` |
| transfer | digest-verified remote↔local; copied **off purgeable scratch** |
| hsi calls | 5 in the audit run; **0 mutating, structurally impossible** — `assert_readonly()` gates the only wrapper that invokes `hsi` |
| guard verified | `--self-test` 48/48 under macOS bash 3.2 **and** cluster bash 4.4.23. The guard was verified in the environment that actually gates HPSS, not only where it was written. |

## 1. THE DENOMINATOR IS STILL MISSING, AND IT IS THE BLOCKER

**No `hsi` command yields a quota.** `lsquota`, `quota`, `lsquota -h` all return
`*** unrecognized command` with exit 64. Recorded as a **reported failure, not a blank**.

**Consequence:** the *size of the overage is unknown*. We know residency (1.4573 TB) and we do not know
the budget, so we cannot tell whether freeing 100 GB suffices or 1 TB is needed — and those imply
completely different actions. **The figure has to come from the NERSC Iris portal
(https://iris.nersc.gov), which only Joseph can read.** Everything else below is ready; this gates it.

## 2. RESIDENCY BY TOP-LEVEL DIRECTORY — and the mediator's prime suspect is 3.4 kB

Measured with `hsi du -s` per directory, discovered by `ls -1` rather than hardcoded.

| directory | bytes | files | share |
|---|---|---|---|
| `mnv-p3f-pet-fullevent-final` | 1,134,998,230,283 | 240 | **77.8834%** |
| `mnv-quoted-products-20260812` | 322,306,102,132 | 36 | **22.1166%** |
| `mnv-p3f-smoketest` | 12,334 | 1 | 0.00000085% |
| `backups` | 3,360 | 2 | 0.00000023% |
| **total (summed)** | **1,457,304,348,109** | **279** | 100% |

**The sum closes exactly against an independent measurement.** `hsi du -s .` at HPSS home returned
**1,457,304,348,109 B / 279 Files** — identical to the sum of the four per-directory figures, which were
obtained by four separate `du` calls. Two derivations, no shared operand, exact agreement.

**`backups/` was the mediator's stated most-likely home of the overage — it is
`backups/scratch_backup/backup_2026-02-20.tar` (2,048 B) and its `.idx` (1,312 B), dated 2026-02-20.**
The hypothesis is refuted by measurement, not argued down. It was a reasonable prior — the directory had
genuinely never been measured — and measuring it cost one command.

## 3. CONCENTRATION — real, and lopsided within the quoted set

Largest objects (full list in the raw output):

| bytes | object |
|---|---|
| 169,974,191,800 | `runEventLoopOmniFold_5D_MEFHC_universes_full.root` |
| 49,215,205,065 | `runEventLoopOmniFold_PC_MEFHC.root` |
| 41,436,632,945 | `uq_universe_5d_covariance_combined_bkgaware.root` |

**The single largest object is 169.97 GB = 11.663% of all HPSS residency.** Those three total
260,626,029,810 B = **80.86% of the 0.3223 TB quoted set** and 17.884% of residency.

The 240 P3F-PET full-event objects are by contrast **uniform** — banded at ~20.0 GB, ~16.3 GB, ~14.15 GB
and ~13.72 GB per systematic universe, twelve objects per band. That shape matters for a deletion
decision: there is no single fat object to remove, so any reduction there is *"drop N universes"*, which
is a physics-coverage decision rather than a storage one.

**One parse caveat, stated because the numbers must be able to contradict each other.** The script's
size-extraction reported `objects_parsed=151 bytes=1457302726101` against `du`'s 279 files /
1,457,304,348,109 B. The gap is **128 objects and 1,622,008 B**, and it is fully explained by the
parser's own `length>=6` digit filter, which skips every object under ~100 kB. **The parse is a lower
bound by construction; `du` is the authority.** The raw listing is preserved, so this needed no re-run.

## 4. TRUE DUPLICATES BY DIGEST — a well-founded negative, and the safeguard that nearly wasn't

**Digest coverage: 277 of 279 objects carry a stored md5.** The 2 without are exactly the two `backups/`
files. So this negative result is **not vacuous** — it rests on near-complete coverage.

**Exactly one repeated digest exists in the entire archive:**

```
2 x 5e89461934bf030f0c4881f8dd0a2779
      /home/j/josephrb/mnv-p3f-smoketest/smoketest.json
      /home/j/josephrb/mnv-p3f-pet-fullevent-final/P3F_PET_receipt_BeamAngleX_0_1A.json
```

**Recoverable space from deduplication: 12,334 B.** Deduplication is not a lever on this allocation.

**But this pair is worth routing to the PET lane as a PROVENANCE question, not a storage one.** A
receipt among the 240 "verified" P3F-PET objects is byte-identical to the *smoketest* object. Either the
smoketest deliberately reused a real receipt as its payload, or one of the 240 is a smoketest artifact
filed among the production receipts. **Session A is not the owner of that question and is not answering
it** — flagged, per the standing rule that superseded/duplicate judgements belong to the lane that owns
the product.

**Name matching would have been wrong here and was not used.** The quoted set contains five basename
collisions across ten files, every pair `X/` vs `X/corrected/`, differing by ~2 KB with distinct md5s.
They are corrected-vs-uncorrected products of a campaign whose entire story is which products are
corrected. Digest-only was a correctness requirement.

### The parser reported the wrong answer first, and the safeguard failed in the direction it guarded

Recorded because the fix is trivial and the failure mode is not. Version 1 matched `(md5)` — the
**parenthesised** form `hsi hashcreate` prints. `hsi hashlist` prints `<hex> md5 /path [hsi]`, no
parentheses. So on real output:

- `objects_with_stored_digest=0`
- duplicate list: **empty**

Read at face value that says *"HPSS stores no digests, so there is nothing to compare"* — when the truth
is 277/279 covered with one duplicate pair. **Section 4 exists specifically to stop a vacuous negative by
printing its denominator, and the denominator was computed by the broken parser — so the safeguard
emitted the one value that makes an empty duplicate list look expected.** A denominator only guards
anything if it is derived independently of what it certifies. Filed as `BEN-196`.

**Two design choices made this recoverable without a second HPSS run:** raw output was dumped alongside
every parse, and a `--parse-file` mode now re-runs the parse over saved evidence with zero HPSS calls.
The corrected parse is under test (`--self-test` 48/48, fixture covers **both** hsi formats, the exact
lines that broke v1, and a regression check that fails if the parser ever matches only `(md5)` again),
and the committed function reproduces the ad-hoc result on the real file exactly.

## 5. A FIGURE IN CIRCULATION FOR A DAY HAS NO SOURCE AND IS 30% LOW

**`0.874 TB` for the 240 P3F-PET objects does not appear in any committed artifact.** Grepped the repo:
the only `0.874` hits are unrelated 2D physics ratios. `hpss-protect-p3f-complete-56692312.json` carries
`size_bytes` for the manifest (72,139), a marker (460), an empty (0) and one more (124,502) — **no byte
total for the archived set.**

**Measured: 1,134,998,230,283 B = 1.1350 TB.** Both normalizations, because one of them is the one a
reader will reuse: **`0.874 TB` sits 22.995% below the measured value, and the measured value is 29.862%
above `0.874 TB`.** (I first wrote the second figure while describing the first — the two differ by the
choice of denominator, which is the same defect as `BEN-193`, committed inside the paragraph reporting it.)

This matters beyond bookkeeping: the copy authorization required *"the incremental figure after overlap
with the 0.874 TB already HPSS-protected"*, and the overlap was measured as zero against a base that was
itself wrong. The conclusion (zero overlap) is unaffected — the two directories are disjoint by
construction, now confirmed by `du` summing exactly to the whole — but **the base figure it was stated
against was not measured.** Continuation of `BEN-193`'s denominator family rather than a new row.

## 6. WHAT IS NOT IN THIS RECEIPT, AND WHY

- **Superseded-product candidates.** Not computed. Deciding a product is superseded needs
  `VALIDATION_LEDGER.md` and the analysis note, and it is a physics-provenance judgement. Routed to the
  owning lane; not Session A's to make.
- **Any deletion candidate.** Per the standing instruction: every candidate goes to the mediator, then to
  Joseph, **per item**. The audit deliberately produces no candidate list, because with 99.9989% of
  residency being campaign data, a "candidate list" would be a list of physics products and generating
  one would be making the decision.
- **`hsi hashverify` after tape migration.** Still open, still the PET lane's, unchanged by this audit.

## 7. THE DECISION THIS TEES UP FOR JOSEPH

1. **The allocation figure, from Iris.** Gates everything; nobody else can read it.
2. **Then, if reduction is genuinely required, the only two pools are physics products:**
   - `mnv-p3f-pet-fullevent-final` — 1.1350 TB, 240 uniform systematic-universe objects. Reduction here
     means dropping universes, which is a coverage decision.
   - `mnv-quoted-products-20260812` — 0.3223 TB, 36 objects, **the set the publication depends on**, and
     80.86% of it is three files. This is the last thing to delete, not the first.
3. **The 12,334 B dedup is available and pointless**, and is mentioned only so it is not later discovered
   and mistaken for an overlooked lever.
