# DECISION 2026-09-01 — Joseph ratifies `OI-185`: the boundary stands at 14/38, and the authored totals are replaced by invariants

**Status:** RECORDED. **Owner of the decision:** Joseph. **Recorded by:** the `claude-school` k=0 lane.
**Row:** `OI-185`. **Prior ruling touched:** ruling 21 of 2026-08-22.
**Tree at recording:** `050dbb72`. **Recorded at:** 2026-09-01T17:17:26Z.

## 0. What this document is, and what it is NOT

**THIS LANE IS RECORDING JOSEPH'S RULING, NOT GRADING IT.** `OI-185` was filed by this same lane —
the one that shipped `OI-179` defect-3 enforcement — precisely so that the lane which caused the
widening would not be the one to bless it. The row's own text says so: *"ruling 21 accepted a
specific boundary, so moving it is his, not the producing lane's."* Nothing below is this lane
concluding that its own change was acceptable. The decision is Joseph's; this file exists so a third
party can check that he made it and what he was shown when he made it.

**§4 records a place where the implementation is BROADER than the ratified words**, on measurement.
That is flagged, not buried, and it is his to reverse.

## 1. The ruling

Joseph, in his own turn, 2026-09-01, in this session, unrelayed:

> Okay I like your recommendation for OI-185, do it

**A ruling of the form "I like your recommendation, do it" takes 100% of its content from the
recommendation.** So the recommendation is reproduced verbatim in §2 rather than summarised. If §2
and this lane's later description of §2 ever disagree, §2 governs.

## 2. The recommendation he accepted, VERBATIM

Reproduced exactly as put to him earlier in the same session, including the parts that are now known
to be wrong (see §4):

> ## Recommendation for `OI-185`: ratify at 14/38 — and stop pinning a total
>
> **Ratify.** Guarded stayed at **14**, unclassified at **0**. Ruling 21 was about the *guarding*
> boundary — which `python3` calls need `mnv_guarded_run.py` — and zero science invocations changed.
> The exclusion rests on identical ground to the two existing entries: `mnv_env_provenance.py`
> imports only the standard library, so the guard has no repository import to contain. Its executing
> copy **is** bound — I measured 8/8 `--pair` in every launcher, same as `SRCMAN` and `PARITY`.
>
> Every alternative is worse, and priced:
>
> - **Route it through the guard** — doesn't preserve 30. The boundary is `guarded + excluded`, so
>   it becomes 22+16 = **38 anyway**, and it moves the one number ruling 21 actually pinned. Strictly
>   worse.
> - **Reimplement in pure bash** — keeps 14/30 by duplicating a tool with 25 self-test arms, in bash
>   4.4. A rule retyped is a second implementation.
> - **Fold it into an existing tool** — keeps 14/30, but a provenance failure would then surface as a
>   source-manifest failure. That's exactly the wrong-diagnosis hazard the launcher preamble was
>   rebuilt to prevent after round 5.
> - **Reclassify it out of the boundary** — threshold-shopping. It's a repository file invoked by
>   path, the same shape as the two entries already inside.
>
> **And the part I'd actually push for: replace the magic total with the invariants that make it mean
> something.** 38 will move again the next time a preflight tool is added, and each move costs you a
> ruling — while the number itself protects nothing. What protects it is: `guarded == 14`,
> `unclassified == 0`, and *every* excluded entry declares its `resolves_to`/`role`/`shell_var`
> **and** is `--pair` bound in all eight launchers. I verified that invariant holds today for all
> three entries, 8/8 each. Under it, a principled stdlib-only preflight tool needs no ruling; an
> unprincipled one still fails — which answers `F-7(a)`'s complaint structurally instead of
> numerically. Precedent exists: round 6 created the interpreter-probe category and deliberately kept
> it out of the boundary.
>
> That second part changes how your ruling is *enforced*, so it needs your say-so — I won't do it
> unilaterally.

**THE LAST SENTENCE IS THE LOAD-BEARING ONE FOR PROVENANCE.** The structural change was flagged to
him as needing his authorization BEFORE he ruled, and was withheld pending it. That flag is the
difference between a ratified change and a lane ratifying itself, and it is why this record can claim
the second half is authorized at all.

## 3. What was decided, in two parts

**(1) THE BOUNDARY STANDS AT 14 GUARDED / 38.** `OI-179` defect-3 enforcement is a legitimate
preflight exclusion. It did not move `guarded` (14) or `unclassified` (0); it moved the declared
exclusion set 16 → 24 and therefore the derived boundary 30 → 38.

**(2) THE AUTHORED TOTALS ARE REPLACED BY INVARIANTS.** `excluded_preflight` (24),
`non_comment_python3_invocations` (54), `inline_interpreter_probes` (16) and `launchers` (8) are
removed from `mnv_preflight_exclusions.json` — **removed, not bumped**. Three pins survive, and only
three: `guarded == 14` (ruling 21's actual subject, still needing a ruling to move),
`unclassified == 0`, and `commented_out_python3_lines == 18`.

**WHY `commented_out_python3_lines` STAYS PINNED, since nothing in §2 says to keep it.** It is a
TRIPWIRE against commenting out a guarded call to hide it, not part of the guarding boundary. §2
authorizes de-pinning the boundary totals. Quietly de-pinning an unrelated tripwire on the way past
would be scope creep under someone else's authorization, so it was left alone.

## 4. ✅ RESOLVED — the implementation is broader than the ratified words, and that is intended

**RESOLVED 2026-09-01 BY JOSEPH, IN HIS OWN TURN, ON BEING SHOWN THIS SECTION:**

> I don't think I meant it literally

**So the shipped criterion stands and §4 is closed.** The stdlib-only phrasing in §2 was descriptive of
the tool that prompted the row (`mnv_env_provenance.py`, which genuinely imports only the standard
library), not a criterion he was fixing. The binding criterion is the one in §5 and
`exclusion_criterion` (5): **an excluded preflight tool's repository imports must be a SUBSET of
`{mnv_guarded_run}`.** No code, test or declaration changes as a result of this ruling — the
enforcement shipped in this form; what changed is that its authorization is no longer provisional.

**WHY THIS WAS WORTH ASKING RATHER THAN ASSUMING, given the answer was the convenient one.** The
convenient reading and the correct reading coincided here, which is exactly the condition under which
a lane should not be the one to decide. The two readings led to materially different work — the literal
one obliges routing `mnv_source_manifest.py` through the guard or granting it a named exception, which
is a change to a tool ruling 21 already accepted. That is not a judgment call a producing lane makes on
its own behalf, and the cost of asking was one sentence.

**The record below is kept unchanged as the state at ratification.** It is what he was shown when he
ruled, and deleting it would remove the evidence that the departure was disclosed before it was blessed
rather than discovered afterwards.

---

**AS FILED — the disclosure that prompted the ruling above.**

§2 gives the exclusion ground as *"imports only the standard library"*. **Implemented as written,
that criterion is unsatisfiable by the set ruling 21 already accepted.** Measured 2026-09-01 with
`mnv_guarded_run.py --expect-root <repo> --inventory`, `--help` on each tool:

| declared exclusion | `checked` | `repo_origin_count` | repository origins |
|---|---|---|---|
| `nd-unfolding/mnv_env_provenance.py` | 13 | **0** | — |
| `nd-unfolding/pet/verify_executing_copy_is_committed.py` | 14 | **0** | — |
| `nd-unfolding/mnv_source_manifest.py` | 15 | **1** | `mnv_guarded_run` |

`mnv_source_manifest.py:61` reads `from mnv_guarded_run import MARKERS, is_checkout`. So a literal
stdlib-only rule **would have fired on an entry ruling 21 already accepted — on every correct tree.**
That is the over-broad-guard failure: it looks like rigour, it fails closed, and it refuses correct
work.

**The rule was not relaxed to fit the measurement; the question was restated.** The ground the
declaration always gave for the first two entries is CIRCULARITY — *"routing them through the guard
would make the check depend on the thing it is checking"* — and the shipped criterion is that ground
made falsifiable:

> **An excluded preflight tool's repository imports must be a SUBSET OF `{mnv_guarded_run}` — the
> guard has nothing to contain but itself.**

All three entries satisfy it as measured. It is **more permissive than §2's words by exactly one
module, the guard**, and strictly stricter than no criterion at all. ~~**If Joseph reads §2 as binding literally, the remedy is not to re-read this record: it is to route
`mnv_source_manifest.py` through the guard or to grant it a named exception, and this lane will do
either on his word.**~~ — **ANSWERED at the top of this section: he did not mean it literally. No
remedy is owed and nothing is routed differently.**

## 5. What now enforces the ruling

Byte-level, in `nd-unfolding/mnv_preflight_census.py` (schema bumped `mnv_preflight_exclusions/1` →
`/2`; a v1 declaration is now REFUSED as could-not-look rather than read under v2 semantics, because
its `counts` block pins totals this code no longer enforces):

1. entry declares `shell_var`, `resolves_to`, `role`, `per_launcher`, all non-empty;
2. `<VAR>="${CODE_ROOT}/<resolves_to>"` present in EVERY declared launcher;
3. invoked exactly `per_launcher` times in EVERY declared launcher;
4. **`--pair` bound in EVERY declared launcher** — new; §2 verified this by hand and nothing asserted
   it, which is F-7(a)'s complaint about the exclusion itself;
5. derived totals internally consistent with the declaration's own per-launcher structure. Not
   redundant with (3): one line naming two tool variables classifies once and counts twice, and only
   this sees it.

Dynamic, in `tests/test_k0_preflight_exclusion_census.py::TheExclusionCriterionIsMeasuredNotAsserted`:
criterion (5) of §4, run against the real guard, plus a non-vacuity arm (an empty origin set must
mean *looked and saw none*, never *never looked*) and **two power arms in a synthetic checkout built
in `TMPDIR`** — one tool importing a sibling repository module must be REJECTED, one stdlib-only tool
in the same fixture must be ACCEPTED. The fixture reads the guard's own `MARKERS` rather than
retyping them, so it cannot go quiet if the markers change.

## 6. The promise in §2, made falsifiable

§2 claims *"a principled stdlib-only preflight tool needs no ruling; an unprincipled one still
fails."* That claim is now two tests, with identical launcher bytes and only the declaration entry
differing between them:

- `test_a_PRINCIPLED_fourth_preflight_tool_needs_NO_ruling` — a declared, `--pair`-bound fourth tool
  passes, boundary moves to 46, `guarded` stays 14, **no ruling required**. Under the old authored
  totals this same change failed on three separate counts.
- `test_an_UNDECLARED_fourth_preflight_tool_STILL_FAILS` — the same bytes without the declaration
  entry is `UNCLASSIFIED`, exit 3.

## 7. Verification at recording

- `mnv_preflight_census.py` on the real tree: rc 0 — `14 guarded + 24 declared-preflight +
  16 interpreter-probe + 0 unclassified = 54`; `guarding boundary … = 38, DERIVED`.
- `tests/test_k0_preflight_exclusion_census.py`: **25/25**, up from 13.
- `--pair` binding re-derived, not recalled: 3 tools × 8 launchers = **24/24 present**.
- No launcher was edited. **No `F-14`/§7.0.7 launcher coupling and no `OI-123` pin supersession is
  triggered by this change.**
- The declaration's sha256 is not pinned anywhere in the tree (`mnv_import_set_ratchet.py` computes
  it live), so editing it breaks no binding — checked before editing, not after.

## 8. Scope

**THIS RECORD MOVES NO GATE AND AUTHORIZES NO COMPUTE.** Gate 2 remains FAIL, nothing is adopted,
CAND 1 of 7 / QUOTED 0 of 7, leg 6 stays prohibited. It does not touch the publication path, which by
Joseph's separate ruling waits on the common five-dimensional covariance.
