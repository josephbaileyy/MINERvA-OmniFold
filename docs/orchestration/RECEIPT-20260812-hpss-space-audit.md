# RECEIPT — HPSS space audit, read-only (2026-08-12)

**Why.** Joseph, verbatim via the mediator: *"try to reduce HPSS space when possible, I am exceeding my
allocation"*. This is the audit half. **Nothing was deleted and this script has no delete path.**

**Bottom line, stated first because it changes the decision:** there is **no cruft on HPSS**. Total
residency is **1,457,304,348,109 B (1.4573 TB) across 279 files**, and **99.9999989% of it is two campaign
archives**. The entire non-campaign contents are **15,694 B — 0.0000011% of residency.** The only byte-identical duplicate pair in
the whole archive is worth **12,334 B**. **Reducing HPSS space therefore means deleting campaign physics
data — there is no housekeeping option.**

> **READ THE ADDENDUM BEFORE ACTING ON ANY OF THIS.** Two things below are superseded by measurements
> taken later the same day: the quota **was** found (512.00 GiB; residency is **265.1%** of it, overage
> **845.22 GiB**), and CFS has ~20,990 GB free — so the conclusion inverts from *delete* to **move**, and
> then defers behind Joseph's necessity precondition. §1 and §7 are wrong as written and are kept
> unedited, because a receipt that silently rewrites its own superseded sections cannot be audited.

## Provenance

| field | value |
|---|---|
| script | `docs/orchestration/hpss_space_audit.sh`, sha256 `e260ab36…` at transfer time (superseded by later edits; see git history) |
| run host | `login11` (NERSC), `hsi` at `/usr/bin/hsi` |
| raw output | `docs/orchestration/state/hpss-space-audit-20260812.txt`, 80,634 B, sha256 `031ff1238886dbb787363493550f9e06db69a5edc5da334020c8d3aab9559c7d` |
| transfer | digest-verified remote↔local; copied **off purgeable scratch** |
| hsi calls | 5 in the audit run; **0 mutating, structurally impossible** — `assert_readonly()` gates the only wrapper that invokes `hsi` |
| guard verified | `--self-test` 48/48 under macOS bash 3.2 **and** cluster bash 4.4.23. The guard was verified in the environment that actually gates HPSS, not only where it was written. |

## 1. THE DENOMINATOR IS STILL MISSING, AND IT IS THE BLOCKER — ***SUPERSEDED, SEE ADDENDUM***

**This section is WRONG.** `hpssquota` on the login node answers it. Kept verbatim because the error was
one of scope — I searched `hsi`'s grammar and never questioned the instrument — and that is the finding.

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

## 7. THE DECISION THIS TEES UP FOR JOSEPH — ***PARTIALLY SUPERSEDED, SEE ADDENDUM***

**Item 1 is resolved and items 2–3 are moot:** CFS makes this a move rather than a reduction, and Joseph
has since attached a necessity precondition that outranks both. Kept as written.

1. **The allocation figure, from Iris.** Gates everything; nobody else can read it.
2. **Then, if reduction is genuinely required, the only two pools are physics products:**
   - `mnv-p3f-pet-fullevent-final` — 1.1350 TB, 240 uniform systematic-universe objects. Reduction here
     means dropping universes, which is a coverage decision.
   - `mnv-quoted-products-20260812` — 0.3223 TB, 36 objects, **the set the publication depends on**, and
     80.86% of it is three files. This is the last thing to delete, not the first.
3. **The 12,334 B dedup is available and pointless**, and is mentioned only so it is not later discovered
   and mistaken for an overlooked lever.

---

# ADDENDUM — the denominator was found, and it changes the decision (2026-08-12, later)

**§1 above is SUPERSEDED. The quota exists and I looked in the wrong place.** `hpssquota` and
`showquota` are NERSC **login-node binaries** at `/global/common/software/nersc/bin/`, not `hsi`
subcommands. Found by the mediator; verified independently here in the same turn:

```
| josephrb usage on HPSS charged to m3246 |  1.03TiB |  512.00GiB |  206.5% |
|                                pscratch |  15.93TiB |  20.00TiB  |   79.7% |
|                                    home |  22.47GiB |  40.00GiB  |   56.2% |
```

**My error was of SCOPE, not of method.** I asked *"does `hsi` have a quota verb?"* and answered it
correctly. The question was *"what reports HPSS quota?"* — and I never questioned the instrument. This is
`BEN-190`'s shape a third time: I verified the contents of the thing I was looking at and not whether I
was looking in the right place. Writing *"the figure has to come from Iris"* gave a false floor on the
cost of getting it — it was one login-node command away, and stating a blocker more firmly than the
evidence supports is its own defect.

## The arithmetic, with both unit conventions because they differ materially here

| quantity | value |
|---|---|
| quota | 512.00 GiB |
| charged **now** | 1.03 TiB = 1054.72 GiB = **206.5%** |
| measured residency (§2) | 1,457,304,348,109 B = **1357.22 GiB** = 1.3254 TiB |
| **true figure once accounting catches up** | **265.1%** |
| overage at that point | **845.22 GiB** = 0.8254 TiB = 0.9075 TB |

**The 206.5% reading is STALE, and the staleness is legible rather than assumed:** 1.03 TiB ≈ 1054.72 GiB
sits within 2.33 GiB of the P3F-PET archive alone (1057.05 GiB), and the quoted-products set (300.17 GiB,
copied 16:24) is absent from it. So HPSS accounting has not yet absorbed today's copy.

## THE CONCLUSION OF §7 INVERTS: this is a MOVE question, not a delete question

`/global/cfs/cdirs/m3246` is available and was not in evidence when §7 was written. Verified here:

```
m3246 (CFS)   81,410 GB used / 102,400 GB quota   79%   ->  ~20,990 GB free
```

**Moving `mnv-p3f-pet-fullevent-final` (1,134,998,230,283 B, 240 files) HPSS → CFS takes HPSS to
300.17 GiB = 58.6% of quota**, with the quoted products staying on tape. CFS goes 79% → ~80.6%. **Nothing
is deleted, no physics product is lost, and no coverage decision is required.**

So §2's central finding stands and its conclusion reverses: **because there is no cruft, the answer is
relocation rather than reduction.** The refusal to generate a deletion-candidate list was right and is now
moot. One caveat that belongs with the option: **CFS is disk, not tape.** The P3F set's purpose was durable
off-scratch protection; CFS is not purged (unlike scratch) but it is not an archive, and it draws on a
shared project quota already at 79%.

## A THIRD OPTION NEITHER LANE HAD: the PI offered to raise the allocation

Relayed via the codex channel from Benjamin Nachman's forwarded NERSC notice (2026-08-12 22:15:50Z):
*"I'm happy to increase as you need, just let me know."*

That is a real alternative with **zero data movement and zero durability loss**, and it was absent from
both the move analysis and the delete analysis. It needs ≥1357 GiB to cover current residency; asking for
headroom above that is the obvious framing. **Not mine to request** — it is Joseph's relationship and
Joseph's ask.

## THE PRECONDITION THAT OUTRANKS ALL THREE — Joseph, verbatim via the mediator

> Yes, I approve any moves you make, but make sure you actually need to store these files. It is important
> to recognize how much increased file storage contamines LLM sessions. Feel free to tell other sessions
> (or you yourself) to utilize agy as an auditor

**Approval-by-reference again: his words carry his authority; any unpacking of them does not.** Moves are
approved. **Deletions are not, and nothing here reads as authorizing one.** But the operative clause is
*"make sure you actually need to store these files"* — which lands **before** the move, the ask, and the
delete alike. All three accommodate 1.46 TB without asking whether it should exist.

**His second sentence is the one worth keeping:** storage cost is not only bytes on tape, it is context
every future session pays. `docs/orchestration/` already holds ~498 files at ~14% live, and `CATALOG.md`
exists because that directory outgrew being readable. **This audit alone produced three artifacts.** That
is a cost I imposed while measuring someone else's.

## NECESSITY EVIDENCE — the cluster half, and it weakens the storage case

The repo-side necessity audit (regenerability, supersession by `OI-24`, citations) is with `agy` in a
detached worktree. The cluster-side question `agy` cannot reach:

**Do the 240 archived objects still exist on scratch? YES — all 240, byte-exact.**

| check | value |
|---|---|
| manifest | `nd-unfolding/p3f_pet_fullevent/HPSS_ARCHIVE_MANIFEST.slurm-56692312.json`, 72,139 B, 240 entries, `n_archived_digest_verified: 240` |
| source | `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/p3f_pet_fullevent/final` |
| distinct paths built | **240 of 240** — asserted, see the vacuous-pass note below |
| present on scratch (`isfile`) | **240 of 240** |
| bytes on scratch | 1,134,998,230,283 = 1057.05 GiB |
| manifest `local_size` sum | 1,134,998,230,283 — **exact match** |
| distinct sizes | 169 (so the per-file check is real, not one path repeated) |

**So HPSS is presently a SECOND copy of live scratch data, not a rescue from purge.** That materially
weakens the case for its current residency — though scratch is *purgeable* and at 79.7%, so "still there
today" is not "safe." The two facts point opposite ways and both belong in the decision.

**A vacuous pass I produced and caught, in the same family as `BEN-196`.** My first version of this check
read the manifest entry key as `rel`/`relpath`/`path`/`name` — the actual key is `file` — so every path
fell back to the source *directory*, and I stat'd one directory 240 times. It printed **"240 of 240
present"**: a clean pass, in the right direction, meaning nothing. The tell was uniformity —
6,881,280 / 240 = exactly 28,672 B each. The fix is the `DISTINCT paths built` assertion above, which
fails loudly instead of passing quietly, plus the distinct-size count as a second witness. **Third time
today a check passed without touching its subject.**

## The smoketest/receipt digest collision is RESOLVED — benign, and the 240/240 claim is intact

The §4 collision has an answer rather than an ambiguity, so the PET lane does not need to start cold.
`P3F_PET_receipt_BeamAngleX_0_1A.json` is **genuine production output**: `produced_utc`
`2026-07-20T06:41:42Z`, `slurm.jobid` `56169842`, `array_task_id` 0, node `nid004079`, `verdict: PASS`,
and a `final_root` pointing at the real 20 GB ROOT with its own sha256. Its md5 on scratch is
`5e89461934bf030f0c4881f8dd0a2779`, identical to the HPSS `smoketest.json` stored digest.

**So the smoketest reused a real production receipt as its payload. None of the 240 is a test artifact,
and `240/240 digest-verified` covers 240 production objects.** The alternative reading — that one of the
240 was a smoketest file, which would have made the claim cover 239 — is **refuted**. Still worth the PET
lane knowing the smoketest object is a copy rather than a distinct fixture.
