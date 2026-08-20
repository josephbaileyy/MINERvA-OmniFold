# 2026-08-20 — LANE C's VERDICT ON REMEDY (A): **FAIL**

**`HANDOFF-20260819-lane-b-member-axis.md:64`'s expiry condition — "remedy (A) VERIFIED BY C, not merely
landed" — IS NOT MET AND REMAINS IN FORCE. B1 steps 4-5 STAY PAUSED.** This verdict grants no permission to
delete, move, truncate, archive or release the 41.44 GB intermediate, and nothing here may be read as such.
`BEN-485`(b) stands exactly as filed; the code pin at `nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh:172`
stays live.

**PASS-WITH-SCOPE was considered and is not available**, because the two decisive defects lie on the *only*
path B1 steps 4-5 would take. There is no scope in which the remedy works.

Verifier: a fresh lane-C session, deliberately NOT the session that wrote
`RULING-20260820-lanec-stamp-coverage-is-a-file-claim-the-class-table-is-an-artifact-claim.md`, and not the
builder. It inherited none of the mediator's mechanical check
(`VERIFICATION-20260820-mediator-remedy-a-wrapper-mechanical.md`) and re-derived what it relied on.

## D1 — THE WRAPPER CANNOT SUCCEED ON ANY REAL PRODUCT, AND ITS REFUSAL FALSELY ACCUSES THE 41.44 GB INTERMEDIATE

`mii_adopt_unified_5d_stamped.py:375` reads scalars through
`out[k] = int(obj.GetVal()) if obj else None` — an **integer truncation**. The TOCTOU anchor it fetches at
`:465` is `sqrt_tr_old`, a `ROOT.TParameter("double")` (`adopt_unified_5d.py:177`) whose value is
**`4.357790406860002e-38`** (`VALIDATION_LEDGER.md` VL1; restated `mii_anchor_comparator.py:23`).

**`int(4.357790406860002e-38) == 0`.** So `assert_diag_matches_sqrt_tr_old` (`:316-321`) takes its `want == 0.0`
branch and **refuses**. Reproduced end-to-end by lane C on the real VL1 value, with a control showing the
uncoerced float passes. **Independently re-confirmed by the mediator** at `:375`, `adopt_unified_5d.py:177`,
the ledger value, and `int()` in a live interpreter.

Two consequences, the second worse than the first:

1. **Remedy (A) cannot complete on anything.** Every adopted root is refused before one key is written, so
   `hDiagCombinedOld` — §11g's precondition and `sqrt_tr_old`'s only surviving ingredient — is never produced.
2. **The refusal names the combined intermediate as the culprit.** On the cluster it reads as a
   TOCTOU/corruption event on the 41.44 GB member intermediate — *the one artifact this campaign cannot
   regenerate for under 2.087 TiB*. **A false accusation aimed at exactly that file is the worst available
   diagnostic, and it is the one the code emits.**

**The defect sits on the untested side of the cluster boundary**, which is why the boundary could not be waved
through: it was not a thin residue of PyROOT semantics, it contained a live functional defect reachable by
static reasoning.

## D2 — NOTHING INVOKES THE WRAPPER. THE ADOPTION PATH STILL CALLS THE UNWRAPPED WRITER.

The wrapper has **zero callers**. The declared-member adoption steps B1 4-5 would run are
`nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh:181` and `:186` — the same script whose `:172` carries the
do-not-delete pin — and neither landing commit touches it (both diffs are 5 `.py` files). Six further launchers
call the writer directly: `sbatch_adopt_stamped_footing.sh:43,46`, `sbatch_j28_adopt_5d.sh:111,113`,
`sbatch_stamp_verify.sh:14`, `run_adopt_5d.sh:19,22`, `sbatch_readopt_5d_bkgaware_footing.sh:100`,
`sbatch_adopt_5d.sh:11`. **Mediator-confirmed: `grep -rln mii_adopt_unified_5d_stamped --include=*.sh` → no
files.**

**The composition a PASS would have authorised:** pause lifts → steps 4-5 run through the *unwrapped* writer →
the two 892 MB adopted roots carry no identity keys and no `hDiagCombinedOld` → the class-table flip just
landed makes `anchor_identity` FAIL CLOSED on them (`mii_root_payload_classes.py:448-450`, `compare():514`) →
and if §11g's release were then read as satisfied, `sqrt_tr_old`'s only ingredient is destroyed. **That is the
direct line from a wrong PASS to the loss the pause exists to prevent.**

## D3 — RULING §5(e) IS UNMET

The ruling required the prose defect corrected **in the wrapper's commit**, because after the wrapper the two
readings name different files. Still uncorrected: `mii_root_payload_classes.py:488` (*"Does this artifact's
**writer** stamp identity at all?"*) and `:491`, which cites *"`STAMP_COVERAGE` records `adopt_unified_5d.py:
0`"* — **a schema that no longer exists**, since the same commit converted that table from a count to a
boolean + `how`, making the cited evidence doubly stale. Also `mii_anchor_comparator.py:525` and the **emitted**
message at `:536-537`, including a now-false *"cannot be admitted until it lands"*.

## THE TEST SUITE HAS ZERO POWER OVER THE ROOT PATH — 6 OF 8 MUTATIONS SURVIVED

Lane C ran eight mutations of its own, on copies under `$TMPDIR`, each with its prediction stated first and
each restored byte-exact. **2 caught, 6 not.** Uncaught: fixing D1 (M1); stamping the unclipped diagonal (M3);
deleting the double-stamp refusal (M5); deleting the write read-back (M6); **deleting the entire TOCTOU closure
call from `main` (M7)**; deleting the read-only-reopen guard (M8).

**M7 is the pointed one:** the TOCTOU closure B advertises as the compensating benefit for the extra 0.915 GB
read can be deleted outright and the suite stays green. **M1 is the decisive one:** the suite cannot see the
coercion that makes that same closure misfire on every real product.

**And the cause is the fixture rule this repo already knows.** `TheDiagonalIsTiedToTheProduct` passes
`math.sqrt(t)` — *a float* — into the function, and its own docstring says *"The 5D traces are ~1e-76"*. **B knew
the magnitude, wrote it down, and did not carry it across the one boundary its own reader crosses.** A fixture
built from the PRODUCER (`_read_scalars`) would have failed on day one.

**B's claimed "8/8 mutations caught" has no recoverable artifact** — no `RUN_LOG` entry, no mutation list, only
a report. Per `CLAUDE.md` that is a claim, not evidence; lane C neither verified nor relied on it.

## WHAT PASSED, AND IT IS MOST OF THE WORK

- **(a) The stamped key set is EXACT in both directions** — 7 required, 7 written, no missing, no extra, plus a
  runtime refusal of any unclassified key. **VL141 compliance verified, row read to its END** including the
  08-17 amendment; no single `estimator_seed` is producible. Lane C went one level deeper than asked and
  confirmed `LEG_BASELINES:142-151` puts `bootstrap_nd` and `seedscan_split` in g1 at 42 too, so
  `upstream_estimator_seed_g1` is an honest label for every contribution.
- **(b) The pinned writer is genuinely untouched and the subprocess claim is real.** Digest re-derived against
  the receipt, not relayed. **No code copied:** of all substantive code lines, exactly 4 are shared with the
  pinned writer and all 4 are boilerplate.
- **(d) The cluster-unverified boundary is drawn honestly and IS asserted** — markers in each function's
  docstring, not just a banner *"because a banner scrolls away"*, and a test that turns ROOT becoming available
  into a prompt to re-derive rather than a silent pass. **Lane C called this the most honest part of the work.**
- **(e)(i)(iii)(iv) three of the four specification defects are real and correctly fixed.** Both size figures
  re-derived on the `cv>0` support: 0.915 GB and 0.0856 MB both correct. **The third mis-sizing against the
  wrong support did not happen.**
- **(f) The table changes follow the ruling, including the dangerous one.** `:3872` was **replaced, not
  dropped**: it now asserts the pause rests solely on "VERIFIED BY C" and that nothing licenses releasing the
  intermediate. Lane C read the test rather than the commit message. `covered_by` is falsifiable in four
  directions. No `RECOMPUTABILITY` key flipped to `IN_FILE`. **Nothing was lifted as a side effect.**

## RULED ON THE DEFERRALS — TRIGGERS, NOT DATES

- **`adopt_unified_5d.py:35`'s hardcoded `_REPO = "/pscratch/..."` on `sys.path` — deferral SAFE ON THE MERITS**,
  and lane C verified the reason rather than assuming it: that file imports **nothing repo-local**
  (`argparse`, `gc`, `os`, `sys`, `numpy`, `ROOT`), so the insertion is inert. **TRIGGER: the file acquiring any
  repo-local import** — which is exactly what the preserved `PENDING` patch would have done
  (`import seed_offset_policy`), *and is precisely why that patch must never be applied*. Operationally, a
  re-issue or retirement of `ben106-stamp-verify-active-56695424.json`.
- **Ruling §8 item 2 still OPEN**: nothing enforces that `STAMP_COVERAGE`'s keys are existing files; the
  producer-derived test opens only `stamps: True` rows, so a typo in a `False` row still vanishes silently from
  `writers_without_identity_stamps()`. **TRIGGER: any new row, or any edit to a `covered_by` value.**

## WHERE LANE C DISAGREES WITH THE PRIOR AUTHORITIES, INCLUDING ITS OWN

- **The mediator's mechanical check is sound but its framing understated the position.** Calling what remained
  a *cluster-execution* gap is wrong in kind: the gap contained a functional defect reachable statically (D1),
  and a wiring gap needing no cluster at all (D2).
- **Lane C's own prior ruling was right on both halves** — `identity_is_checkable` reads `ARTIFACTS`, and the
  class-block flip fails closed — **and its §5(d) was too permissive in one respect.** Holding the *table row*
  to a cluster standard the four existing `True` rows do not meet would indeed have been asymmetric, and that
  stands. But the ruling named the boundary as an inherited precondition and listed three open items, **and the
  boundary was where the defect was.** §8 was the place to ask what the wrapper's reader does to a `double`.
  **It did not, nor did the mediator, nor did B. That question is not asymmetric — it is the one question the
  wrapper form newly creates.**

## OPEN, in the order it should be taken

1. **D1** — the `int()` coercion. One line, but it needs a **producer-derived** test: one that obtains the
   anchor the way `main` does, not one that hands the assertion a float. M1 proves the suite has no power here
   in either direction.
2. **D2** — rewiring. A launcher change inside the frozen-provenance rule, so it needs its own decision about
   which of the seven call sites are in scope. **NOT a fix to be made unilaterally.**
3. **D3** — ruling §5(e), two files.
4. **M5-M8**: four ROOT-path behaviours, each *correctly written* and *entirely uncovered*.
5. Ruling §8 item 2.
6. **The class-table flip's declared cost is LIVE NOW** — every pre-wrapper adopted root FAILS CLOSED, while
   D1+D2 mean no product can yet be built that passes. Fail-closed and intended, but the window should be short.
7. The landing commit carried no `RUN_LOG`, ledger or `STATUS` entry, against `CLAUDE.md`'s hard rule.

**Read-only discipline held:** no file created, edited, moved or deleted; no commit, push, checkout, reset or
stash. All mutation work on copies under `$TMPDIR/lanec-mut`, restored byte-exact.
