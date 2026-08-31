# FINDING 2026-08-31 — `audit_gates_that_cannot_fail.py` blanks 95% of a file it audits, because its
# comment stripper reads a CLOSING triple quote as an OPENING docstring. The gate-that-cannot-fail
# detector is itself, on 15 files, a gate that cannot fail.

**CITABLE FOR:** the measured survival rates in §2; the root cause in §1; the statement that any
"0 hits" this tool has reported over an affected file is unfounded; and the correction it forces on
`FINDING-20260831-ben039-detector-is-triple-bound.md` §1. **NOT CITABLE FOR:** any gate movement;
authorization to edit the audit tool, any test, or any launcher; a claim that any *specific* defect
exists in the blanked regions — nobody has looked at them; `OI-177`; leg 6; the M(ii) family; or
adoption. **Gate 2 remains FAIL.** Filed as `OI-180`.

## 1. Root cause — a one-line pattern that cannot tell an opening quote from a closing one

`docs/orchestration/audit_gates_that_cannot_fail.py:59`

```python
_PY_DOC = re.compile(r"^\s*(\"\"\"|''')")
```

`strip_noncode` uses it as a docstring **opener** whenever a line's first non-space characters are a
triple quote, entering "inside a docstring" mode until it next sees that quote. **But the terminator
of an assigned multi-line string is also a line whose first non-space characters are a triple
quote.** So in

```python
STUB_MR = '''echo "[stub] ..."      <- does NOT match: the line starts with STUB_MR
...
'''                                  <- MATCHES, and is read as OPENING a docstring
```

the closing delimiter flips the state machine on. From that point the sense of every subsequent
triple quote is **inverted**: real code is blanked, and the next assigned-string opener is treated as
the close. Replayed on `nd-unfolding/tests/test_k0_launcher_two_roots.py`, the machine opens at `:2`
(a real docstring), closes at `:20`, then **opens at `:80` on a closing `'''`** and never recovers —
at EOF it still believes it is inside a docstring.

**This is exactly the class the tool exists to find.** Its own `--min-files` guard was added because
the author shipped a sweep that examined zero files and printed a clean bill of health; the docstring
`says so`. The same defect survived one level down: the sweep now visits the file and reads almost
none of it.

## 2. Blast radius — measured, 473 Python files with ≥40 non-blank lines

15 files lose **more than half** their non-blank lines. **3,730 code lines are invisible to every
detector.** It is not confined to tests:

| survival | non-blank | kept | file |
|---:|---:|---:|---|
| **5.0%** | 978 | 49 | `nd-unfolding/tests/test_k0_launcher_two_roots.py` |
| 12.3% | 219 | 27 | `2d-unfolding/agreement_windows_receipt.py` |
| 17.7% | 237 | 42 | `nd-unfolding/tests/test_n2_child_boundary.py` |
| 24.0% | 430 | 103 | `nd-unfolding/tests/test_conftest_tmpdir_guard_live.py` |
| 27.8% | 230 | 64 | `docs/orchestration/test_measure_m1_m6.py` |
| 31.3% | 284 | 89 | `nd-unfolding/tests/test_oi136_failopen_inventory_ratchet.py` |
| 41.0% | 166 | 68 | `docs/orchestration/state/probe-oi136-sys-path-hijack-20260826.py` |
| 41.6% | 197 | 82 | `nd-unfolding/tests/conftest.py` |
| 44.4% | 151 | 67 | `nd-unfolding/tests/test_pet_diagnostic_artifact_identity_guards.py` |
| 45.9% | 74 | 34 | `nd-unfolding/pet/annealed_estimator.py` |
| 46.9% | 145 | 68 | `docs/orchestration/state/probe-oi136-sys-path-hijack-20260820.py` |
| 47.3% | 518 | 245 | `nd-unfolding/launcher_argv_probe.py` |
| **48.6%** | 733 | 356 | **`nd-unfolding/mii_adopt_unified_5d_stamped.py`** |
| 48.8% | 650 | 317 | `nd-unfolding/mii_root_payload_classes.py` |
| 49.2% | 648 | 319 | `nd-unfolding/pet/cstat_data_only.py` |

The last three are not fixtures. `mii_adopt_unified_5d_stamped.py` is an **adoption path**.

**The `[oi136]` probes are the sharpest illustration:** files written to investigate an import-path
hijack are themselves 41% visible to the auditor.

## 3. What this CORRECTS in this lane's own record, committed hours earlier

`FINDING-20260831-ben039-detector-is-triple-bound.md` §1 reports the sweep returning **0** hits for
the `OI-179` defect-2 surfaces and attributes that to the detector being triple-bound. **The triple
binding is real and independently proven** — it was measured by importing the module and calling
`d_tautological_datum` on single-line probes with a positive control that fires, and that method does
not involve the stripper at all. That section stands.

**But the SWEEP's zero has a second and sufficient cause, and the record does not say so:** the file
is 5% visible, so no detector of any design could have hit it. Two independent causes were collapsed
into one. The earlier finding is not wrong about the detector; it is incomplete about the sweep, and a
reader would conclude that repairing the detector would make the sweep see the instance. **It would
not.** That correction is applied in the same commit as this document.

## 4. A detector was written for `OI-179` defect 2 and DELIBERATELY NOT SHIPPED

Joseph authorized it, with a power arm, on 2026-08-31. It was written, its `POWER` arm was added, and
`--power-only` passed **8 of 8**. It is preserved unshipped and the working tree is reverted to
`HEAD`. Three measured reasons, and the third is the decisive one:

1. **It cannot see the instance it was written for.** Called directly on
   `test_k0_launcher_two_roots.py` it returns **0** hits, because §1 has already blanked
   `_ambient_prefixes`, `good_env` and `subprocess.run`. Its power arm passed only because
   `run_power` feeds detectors **raw** lines with no stripping — so the power fixture and the real
   file are not the same object, and the power arm was a strawman without either of us intending one.
2. **It produced 170 `REVIEW` findings repo-wide** across launcher tests that legitimately build an
   environment and spawn a child. The tool's own docstring names this failure: mixing certain and
   speculative hits "is how a report becomes noise".
3. **Shipping it would have created the very thing it hunts.** A registered detector for this class,
   passing its power test, silent on every real instance, would read as coverage. That is a gate that
   cannot fail, inside the instrument built to find gates that cannot fail, added by the commit that
   claimed to close the gap.

**The detector is therefore BLOCKED ON §1, not abandoned.** Its acceptance criterion is already
recorded at `FINDING-20260831-ben039-detector-is-triple-bound.md` §4 and stands unchanged.

## 5. REPAIR APPLIED 2026-08-31 on Joseph's authorization (*"Yes can you fix them all?"*)

**All three proposed steps are done.** `strip_noncode` is now `tokenize`-based, the stripper has its
own power arm, and the sweep was re-run and its delta measured.

**Measured survival after the repair**, same files as §2: `test_k0_launcher_two_roots.py`
**5.0% → 74.9%** (49 → 733 of 978); `test_n2_child_boundary.py` 17.7% → 75.9%;
`test_measure_m1_m6.py` 27.8% → 78.7%; `agreement_windows_receipt.py` 12.3% → 67.6%;
`mii_adopt_unified_5d_stamped.py` 48.6% → 40.8%; `conftest.py` 41.6% → 40.6%. **The last two went
DOWN and that is correct, not a regression** — the old stripper left real docstrings visible while the
state machine was inverted, so prose was being swept as code. The new one blanks docstrings properly
and preserves assigned string literals, which is why the shell text inside a `STUB = '''…'''` block
now survives: those literals carry the patterns `size-only-completeness` exists to find, and the old
stripper was destroying them.

**Line counts are preserved exactly** on every file checked, which every detector depends on because
it reports `lines[ln - 1]`.

**THE RE-SWEEP COST, which was the reason this was a decision: it is small. Net +1 finding, 46 → 47.**
Four additions, all `strong-name-weak-body`: `docs/orchestration/agentctl.py:132`
(`assert_clean_git_start`), `nd-unfolding/mii_adopt_unified_5d_stamped.py:456`
(`assert_diag_matches_sqrt_tr_old`, on an ADOPTION path), `nd-unfolding/p4_lib.py:1489`
(`check_projection_matrix_matches_recipe`), `nd-unfolding/pet/extract_fullevent_fps.py:405`
(`assert_truth_denominator_coverage`) — each an `assert_*`/`check_*` function whose body asserts only
presence or finiteness. Three removals, of which two are confirmed **mention-vs-use false positives**
now correctly treated as data: `test_validator_units_auditor.py:74`, which is the literal string
`"    b = d >= -1e-30\n"` inside a fixture *about* this auditor, and
`unfold_nd_omnifold_unbinned.py:834`, an f-string message.

**ATTRIBUTION OF THE DELTA IS PARTIAL AND THIS DOCUMENT DOES NOT PRETEND OTHERWISE.** One removal,
`measure_joint_vs_additive_nuisance_retrain.py:114`, is unexplained: the line is visible under both
strippers. And the precise mechanism of the four additions is not established — the first check tried
compared the COUNT of visible body lines rather than their identity, which is an asymmetric
comparison, and the counts were equal while the sets need not be. The delta is reported as measured;
the causal story for 5 of the 7 changed rows is not claimed.

**Fail-closed verified by sabotage, not by reading:** breaking one stripper assertion makes the sweep
exit **1** and print *"stripper power FAILED -- no detector output is trustworthy"* and
*"refusing to report a sweep whose detectors are not shown to fire"*. Restored, and
`--power-only` returns 0 with 8 stripper arms and 7 detector arms.

## 5b. The original proposal, retained


1. **Fix the stripper** so a triple quote is classified by whether it opens or closes, e.g. by
   tracking whether the line's quote count is odd and whether the line has code before the quote, or
   by using `tokenize`/`ast` instead of a line regex. `tokenize` is the honest instrument: it knows
   what a string literal is.
2. **Give the stripper its own power arm.** It has none. The natural one: assert that a
   reconstruction of `STUB = '''…\n'''\nCODE` leaves `CODE` visible, and assert a floor on survival —
   a stripper that blanks more than some fraction of a real file should refuse, in the same spirit as
   `--min-files`.
3. **Re-run the whole sweep afterwards.** Every prior "0 hits" over the 15 files is unfounded and
   must be re-measured. This is the expensive part and it is why the fix is a decision, not a chore:
   it may surface a queue of real findings, and `5d`'s independent sweep has already produced nine
   candidates including one on an `F-7(b)` Gate-2 surface.

**Nothing in the blanked regions has been examined.** This document claims a measurement gap, not a
defect count.
