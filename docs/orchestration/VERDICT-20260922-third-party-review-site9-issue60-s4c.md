# VERDICT 2026-09-22 — third-party review of site 9, ISSUE-60 and §4c

**CITABLE FOR:** one independent lane's verdict on the three objects `HANDOFF-20260922` §10 lists
as having no independent checker left, and for the tenth site that review found.
**NOT CITABLE FOR:** publication readiness, any grade, `M1`–`M4`, cause 3, or any claim that the
scalar-5D adoption is qualified differently than its adoption record says.

| | |
|---|---|
| reviewed at | `origin/main = 384c2eb17e94a9b7a11f5e6237955eb63be6b423` |
| objects | site 9's fix; ISSUE-60 (three checks); `CORRECTION-20260921-…` §4c |
| requested by | `HANDOFF-20260922-gbdt-cold-start.md` §10, §12 item 7 |

## 0. Why this lane is the third party

§10 records that the two lanes active on 2026-09-21 each fixed something they had also found, which
spends their independence. **This lane made none of the three objects**: site 9's fix and ISSUE-60
both landed at `d2f29ca5` (author: *fixer-reviewer lane*), and §4c's content landed in the same
commit. This lane's first commit in this tree is `384c2eb1`. The three reviews below were completed
**before** this lane edited any of the files involved, which is the ordering the independence claim
needs and not merely the fact of different authorship.

⚠ **This verdict does NOT inherit that independence for site 10.** This lane both FOUND and FIXED
site 10 (§3 below), so by the same rule it has spent its verdict on that object. Site 10 needs a
fourth pair of eyes.

---

## 1. SITE 9's FIX — **CONFIRMED CORRECT, and its table row matches the diff**

Measured by opening the diff, which is the check §4 of the correction record says was skipped when
rows 7 and 8 misdescribed themselves.

| check | result |
|---|---|
| substantive sentence replaced | ✅ `"a property of the estimator and a larger ensemble would not reduce it"` → `"a property of the estimator rather than of the ensemble's resampling noise"` |
| wording identical to sites 7–8 | ✅ byte-for-byte the same replacement clause |
| inline `⚠ M1 CORRECTED` block added | ✅ present, and it names the operand (`SEED-EFFECT-20260920.json`, key `seed_effect_same_throws`, `Q1`–`Q4` at `N=40`, `HA`/`HB` at `N=80`) |
| any number moved | ✅ **none**; the diff changes no numeric literal |
| `M1`'s `6.145%` FAIL | ✅ untouched, and the block says so |
| surviving `flat in N` claim is scoped | ✅ reads `over N = 40–160`, not unqualified |
| row 9 written from the diff, not from intent | ✅ the row's description matches `git show d2f29ca5 -- nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md` |

**VERDICT: ACCEPTED, with no exceptions.**

⚠ **THIS SECTION CARRIED A WRONG CORRECTION OF ITS OWN FOR ONE REVISION, AND WITHDRAWING IT IS THE POINT.** It read: *"One imprecision, not a defect: the commit message says the asserting sentence sat 'three lines above' the existing `⚠ M3 CORRECTED 2026-09-20` block; measured, it is two lines above."* **That is withdrawn — `d2f29ca5` was right and this record was wrong.** Measured at `d2f29ca5^`: the asserting sentence begins at line index **13** and the `M3 CORRECTED` block at index **16**, so it sits **three lines above**, exactly as the commit message said. The error came from measuring the gap from the sentence's **wrapped second line** (index 14, `reduce it;`) instead of from where the sentence starts. **A hard-wrapped sentence has two plausible anchors and they differ by one**, so a line-gap claim must name which end it counts from — and a reviewer correcting another lane on a point where *nothing rests on the number* should be held to a higher bar than the claim it corrects, not a lower one. Found by this session's own round-1 review.

## 2. ISSUE-60 — **TWO CONFIRMED AS STATED; ONE CONFIRMED WITH ITS MECHANISM CORRECTED**

**(1) `generate_manifest.py --check` is a function of the WORKING TREE — CONFIRMED.**
`inventory()` takes the path SET from `git ls-files` and `committed_only` only drops the untracked
half (`generate_manifest.py:92-94`); the digests come from `path.read_bytes()` (`:390`) and `--check`
compares against `TARGET.read_bytes()` (`:617`). So `--committed-only` restricts *which paths*, never
*which bytes*. Its green attests nothing about a sha. **As filed.**

**(2) the status is invisible through a pipe — CONFIRMED.** `main()` returns `1` on mismatch
(`:620`) and `0` on match (`:622`); a pipe replaces that with the last command's status. This is a
property of the shell rather than of the script, which is what makes it easy to report wrongly.
**As filed.**

**(3) `live_doc_indexed.py` cannot fire on the failure it exists to catch — CONFIRMED, BUT THE
STATED MECHANISM IS WRONG IN ONE CLAUSE, AND THE REAL HOLE IS WIDER.**

ISSUE-60 says *"by the time the row could be staged the doc was no longer 'newly' LIVE in any
diff."* That is not what the code does. `in_scope()` (`live_doc_indexed.py:94-98`) has **two**
branches, and the second does not depend on newness in the diff at all:

```python
newly_added  = {p for p in added_md   if p in staged_live}
reclassified = {p for p in staged_live if p not in head_live and p.endswith(".md")}
```

`reclassified` fires precisely when a row becomes LIVE in the staged overrides while it was not LIVE
at `HEAD` — i.e. exactly the "row added later" case ISSUE-60 says is unreachable. **So a later-added
row WOULD be caught.**

The actual hole is that **both branches intersect `staged_live`**. A document that never receives a
LIVE overrides row is in neither set, so it is outside the checker's scope permanently. Measured on
the commit ISSUE-60 cites, `15edf148`, which added two orchestration records:

| record added by `15edf148` | LIVE overrides row in that commit | in `CATALOG.md` by that commit | ever gets a row? |
|---|---|---|---|
| `CORRECTION-20260921-seed-effect-…md` | ✅ yes | ✅ yes | — |
| `OUTCOME-20260921-L2-probe-blocked-at-stage-4.md` | ❌ **no** | ❌ no | ❌ **still none at `384c2eb1`** |

`15edf148` also did **not** contain `docs/orchestration/MANIFEST.tsv` (0 of its 25 paths), which is
the half of the claim that is exactly right.

**VERDICT: ISSUE-60 STANDS as a HIGH item and all three checks are real.** Item (3)'s remedy is
correctly named in `HANDOFF-20260922` §11 — *"a whole-tree-first inversion"* — and that handoff's
one-line statement of the defect (*"it reported 'nothing newly LIVE' on every run while a new record
went in unindexed"*) is **more accurate than `d2f29ca5`'s commit message**. Use the handoff's
wording, not the commit's.

## 3. §4c — **ITS CONCLUSION IS CORRECT; ITS PRESCRIBED INSTRUMENT DOES NOT REPRODUCE IT, AND IT HAS NO HEADING**

### 3a. The substance is right, and reproduces

| §4c claim | measured |
|---|---|
| `e7f8f365` planted the claim in the status file | ✅ its diff adds the sentence to `nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md` |
| that commit touched seven files | ✅ exactly seven |
| *"Six are clean; one asserted"* | ✅ 1 of 7 carries the claim at that commit |
| *"four surfaces received the claim and three received the correction"* | ✅ 4 files and 3 files respectively — but see 3b |
| `EVIDENCE` §5 is left standing beneath its pointer | ✅ §5's text is intact under an `⚠ CORRECTED` blockquote |
| `CATALOG.md` quotes the claim under **WITHDRAWN** | ✅ at `CATALOG.md`'s entry for the correction record |

### 3b. Defect 1 — the prescribed command does not return the sha §4c attributes to it

§4c prescribes `git log -S '<the claim>' --reverse` and states the answer is `e7f8f365`. Run with
the claim **as this record quotes it**, it is not:

    git log -S 'a larger ensemble would not reduce it' --reverse -- .   -> 7257b255 (oldest)
    git log -S 'property of the estimator and a larger ensemble would not' --reverse -- .
                                                                        -> e7f8f365 (oldest)

The site-9 instance wraps as `would not` + newline + `reduce it`, so the quoted claim **does not
occur as a contiguous string in the blob** and `-S` cannot see it. The conclusion is right; the
instrument as written does not produce it, and a reader following the recipe gets a different,
later commit and no warning.

### 3c. Defect 2 — the two adjacent sentences count over two different populations

*"Seven files … Six are clean; one asserted. Four surfaces received the claim and three received the
correction"* reads as four **of the seven**. It is not: only one of the seven ever carried it. The
`4`/`3` are tree-wide counts. Both numbers reproduce, each over a population the sentence does not
name.

### 3d. Defect 3 — **§4c HAS NO HEADING, and three pointers resolved to nothing**

`d2f29ca5`'s message says *"Recorded at the record's new S4c."* No `4c` heading was written; the
content landed as an unlabelled block inside §4. The record's own row 9 (*"see §4c"*), the block's
own *"(§4c)"*, and two pointers in `CATALOG.md` all dangled. **FIXED 2026-09-22**: the heading is
added over the block it describes.

**VERDICT ON §4c: SUBSTANCE ACCEPTED, INSTRUMENT AND LABELLING CORRECTED.** Its central rule — *a
claim's blast radius is the file list of the commit that spread it* — is sound and is what found
site 9. It is **not sufficient**, which §4d now records.

## 4. WHAT THIS REVIEW FOUND THAT WAS NOT ASKED FOR — site 10

Reviewing §4c's population claim required re-running the sweep over every wording rather than the
one §4c uses. That found a **tenth site, live on the discovery surface**:
`docs/orchestration/CATALOG.md`'s `EVIDENCE-20260920` entry asserted *"Corollary: a larger ensemble
would not change it"* in bold, unmarked, planted at `128a5e7a`.

**It was missed by INSTRUMENT, not by scope** — `CATALOG.md` is under `docs/` and was inside every
sweep's path scope. The phrase wraps as `a larger<LF>  ensemble`, and **`tr '\n' ' '` — the remedy
this tree's own rules state at `HANDOFF-20260922` §8.5 and §10.1.3 — still returns 0**, because it
leaves the two-space Markdown continuation indent behind. Only collapsing whitespace finds it.
Recorded with its measurements at the correction record's new §4d; the entry is patched, retaining
the two clauses `EVIDENCE` §5 explicitly does not withdraw.

## 5. What this verdict does NOT authorize

- It does **not** clear `M1`–`M4`, which travel with every use of `3d7465f6…`.
- It does **not** bear on cause 3, which is not discharged for the adopted bytes.
- It does **not** close ISSUE-60: three fixes in two owners' files remain unwritten and unauthorized.
- It does **not** make this lane an independent checker of site 10, which it fixed.
- No number in the scalar-5D result moved, in either direction, as a result of anything here.

**Co-Authored-By: Claude Opus 5 (1M context)**
