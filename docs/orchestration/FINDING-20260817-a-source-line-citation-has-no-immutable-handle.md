# `BEN-254`'s remedy is unavailable for SOURCE-LINE citations, and the substitute already exists in the tree

**Lane B, 2026-08-17. Read-only: `git grep`, `git show`, `sha256`. Nothing submitted.**
Every operand re-derived at `origin/main` `65daf8fa` this turn.

**`BEN-254` (lane D) owns this species and states it correctly:** a line-number citation rots
silently on insertion, and the remedy is *"cite a content digest, not a line."* This row adds one
bounded thing and claims nothing else — **for a citation into a MUTABLE SOURCE FILE, that remedy has
no handle, and the tree already contains the only substitute that works.**

---

## 1. Why the digest remedy does not reach a `.py` line

`BEN-254`'s worked case had a handle in hand: `ND_OMNIFOLD_RUN_LOG.md:7922` already pinned a stdout
by sha256, so a reader could `git grep` the digest and land on the corrected receipt. **A source
module has no such object.** Measured:

    sha256(nd-unfolding/unified_throw_cov.py) = ee130b662230fc5cfe3fd490c5ebb3a0245f60e76ae748164b2a2104234da320
    git grep <that digest>                    -> 0 hits

**And pinning the FILE would be the wrong object anyway** — a whole-file digest moves on every
unrelated edit, so it cannot address *a line*. That is the container-digest error in reverse: there,
a file digest was read as evidence about an object inside it; here, the object inside is what needs
addressing and only the container is digestible.

## 2. What the tree does instead, at 58 sites

`nd-unfolding/uq_5d/receipt_candidate_stamps_5d.json` cites `unified_throw_cov.py:445` at four sites
(`:434`, `:464`, `:494`, `:595`) and **quotes the line beside the number**:

    "tol_source": "unified_throw_cov.py:445  tol = 1e-12 * max(||base||, 1.0); ||base|| ~ 1e-36 << 1 so max() binds => absolute 1e-12"

The number LOCATES; the quoted text SURVIVES THE EDIT. A reader whose line has drifted re-finds it by
content, with no digest, no tooling, and no pin.

**Population, measured, with the search stated because it is a lower bound:**

    2004   .py line citations in *.md / *.json / *.tsv        (git grep -ohE '[a-z0-9_]+\.py:[0-9]+(-[0-9]+)?')
      58   of those immediately followed by quoted source text (same corpus, same regex family)
     186   distinct .py modules cited by line

**AS-OF SHAS, AND MY OWN WRITE-UP MOVED THE RATIO IN THE FLATTERING DIRECTION.** All three counts above
are as of `65daf8fa`. Re-measured after the commit that reports them, because in this repo every
measurement runs over the repo and every finding is written into it:

| as of | all `.py` cites | with quoted text | modules | ratio |
|---|---|---|---|---|
| `65daf8fa` (when written) | 2004 | 58 | 186 | 2.89 % |
| `9b1e2d45` (immediately pre-commit) | 2025 | 58 | 187 | 2.86 % |
| `ddfd6e22` (this finding committed) | 2032 | 60 | 187 | **2.95 %** |

**Two things fall out and only one is comfortable.** The population drifted `2004 → 2025` in about
twenty minutes on other lanes' commits alone, so a bare count here is stale inside the hour — an
as-of sha is not optional. And **my own row and long form added `+7` to the total and `+2` to the arm
I am advocating, moving the ratio UP**: the write-up quotes cited lines beside their numbers, which is
the practice being recommended. `BEN-391`'s asymmetry, pointing the wrong way for me — there the
contamination widened a contrast, here it flatters the remedy. **The `58` is the honest operand and
the `60` is contaminated by this document; neither is quotable without its sha.**

**58/2004 = 2.9 % is a FLOOR, not the rate.** The regex recognises only *cite, two-or-more spaces,
text*; a citation that quotes its line in the next sentence or a code fence does not match. So the
practice is commoner than 58 and still nowhere near universal.

## 3. The instance that prompted it, and the negative result inside it

Costing the two-module seed separation, I checked what an insertion into `unified_throw_cov.py` would
break. **No enforced binding: `0` occurrences of either module as a `.py` path in any receipt or state
JSON, `0` of the tree's `66` `EXPECTED_*_SHA` constants, `0` sha-check lines across
`sbatch_sweep_bank_5d_run_bkgaware_gpu.sh`, `..._dump_...` and `sbatch_uthrow_run_5d_fast.sh`.** So
`verify_hash_bindings.py` reads **GREEN** on that edit — correctly, and about a different question
(`BEN-386`'s shape). None of the pre-commit hook's nine checks reads a `.py` line number.

What exists instead: the four receipt citations above, plus **one ledger row** — `VL13`, citing
`unified_throw_cov.py:355,400,407`. All five currently RESOLVE (verified: `:355 C_uni, mean_shift =
joint_throw_covariance(X, base)`, `:445 tol = 1e-12 * max(float(np.linalg.norm(base)), 1.0)`). An
insertion above `:355` rots all five, silently.

**A CORRECTION TO MY OWN FIRST REPORT OF THIS, made before it travelled further.** I said
`VALIDATION_LEDGER-VL-MAP-20260812.json:89` cites the module. **It does not.** That file maps ledger
rows; the object at `:85-90` is `{"vl": "VL13", "row_sha256": "85f695bd…", "row_prefix": "| `unified_throw_cov.py:355,400,407` | `joint_throw_covarian"}` — the `.py` citation is **content of the
ledger row**, captured as a 60-character prefix. The rot lands in `VALIDATION_LEDGER.md`'s `VL13` row,
a different file with a different owner. And `row_sha256` is **deliberately** outside
`verify_hash_bindings.py`'s scope: `FINDING-20260815-a-guard-with-no-cell-for-what-it-cannot-see.md:107`
classifies its 108 occurrences as content hashes with no file to compare against, correctly. **So
there is no broken or unenforced pin here, and my first phrasing implied there was.** The count is
**four receipt citations plus one ledger row**, not five receipt citations.

**And the truncation is the point in miniature:** `row_prefix` stops at 60 characters, so it carries
`:355`'s content and nothing for `:400` or `:407`. The mitigation is present and partial in the same
string.

## 4. Used in anger the same hour, which is the only reason I trust it

Reading the `57194055` traceback (`fullevent_fps_dataloader.py:742`, frozen `d0c42bd`) against
`origin/main` `65daf8fa`, the line number was a cross-ref between two trees. I checked
`assert_refined_target_is_replica` is **byte-identical at both refs** (`:736` in each, so `:742` is
the same `raise` in both) before reasoning from it. **Had it moved, the quoted `raise` text would
still have found it and the bare number would not.**

## 5. The clause

**CITE THE LINE AND QUOTE IT.** The number locates, the content survives the edit. Zero cost, no
tooling, already practised at 58 sites.

**Not written as a check, and the reason is `BEN-381`/`BEN-390`'s:** a lint demanding adjacent text on
every `.py:<n>` would fire on all ~1,946 existing bare citations, which is how a check gets switched
off. **`BEN-254`'s digest remedy stays correct wherever a digest exists — this is the fallback for
where one cannot.**

**Register, not species.** This is `BEN-077` / `BEN-248` §6 in the fifth register — *content of a
cited line* — and `BEN-248` §6 labelled a fifth register as a prediction. It is now an instance, and
it is the register I predicted only in shape: I guessed *provenance of a capability*, and what arrived
was *content of a citation*. **Recorded so the prediction is scored rather than quietly re-aimed.**
