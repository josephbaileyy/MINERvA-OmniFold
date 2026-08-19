# FINDING — **cardinality cannot witness containment**, and a two-tally report reads identically whether its claim is true or false

**Filed by:** lane C (PET), 2026-08-19. **Row:** `BEN-468`. **Cross-stream:** `OI-121`.
**Attribution up front, because three parties contributed different things:** the catch is mine, the
re-measurement by name is B's, and the observation that it is the same mechanism as this lane's snapshot finding
is the mediator's — which asked me to file rather than filing it, on the principle that the instance and the
introspection belong to whoever did them.

---

## 1. What was reported, and what I measured

A lane reported its suite as **"3 failed, and the three reproduce at baseline `8e48a811`"** — the substantive
claim being *I introduced no new failures*. The recipe was offered precisely so the report would not have to be
trusted, so I ran it.

```
detached worktree at 8e48a811, TMPDIR set explicitly
4 failed, 1722 passed, 4 skipped in 105.09s
   test_gate2_target_runtime.py            canonical NumPy DataLoader source missing/invalid
   test_p4_sweep_snapshots.py              380 != 374 : shell-file count drifted
   test_pet_fullevent_nominal_launcher.py  'tensorflow' unexpectedly found
   test_resume_guard.py                    lib_member_resume.sh: guarded but never stamped
```

**Four at the baseline, not three.** *(The `105 s` matched exactly, which is a good sign about the care taken over
the rest of the report — this is not a finding about sloppiness.)*

## 2. Why the report could not establish its own claim

> **`3 ≤ 4` supports *"no new failures"* ONLY IF the three are a SUBSET of the four. A COUNT CANNOT EXHIBIT A
> SUBSET RELATION.**

**Had one of the three been a genuine regression while one baseline failure was independently fixed, the report
would have read IDENTICALLY.** The tallies are insensitive to exactly the substitution the claim excludes.

**Re-measured by name on request, the claim SURVIVED:**

```
BASELINE (4)  gate2_target_runtime · p4_sweep_snapshots · pet_fullevent DriverConfigGate · resume_guard
HEAD     (3)  gate2_target_runtime · p4_sweep_snapshots · pet_fullevent DriverConfigGate
NEW at HEAD   EMPTY
FIXED         resume_guard   (BEN-482, a lint-reads-prose defect)
```

> **So the report was TRUE AND UNESTABLISHED — and that is the worse of the two failures, because a FALSE claim
> gets caught while a TRUE-BUT-UNWITNESSED one is indistinguishable from a verified one and survives review.**
> The lane's own summary of it is the sharpest available: *"the claim was true and unestablished, which is the
> worse of the two failures because it is invisible."*

## 3. Why this is a new register and not an amendment to the existing count family

**Checked before filing.** The repo's existing rows on counts are all cases where **the count itself was wrong**:

| row | defect |
|---|---|
| `BEN-445` | a row count cannot report a FAILED QUERY — four windows returned `0` because the query never ran |
| `BEN-431` | `sacct -X` alone is a count of ROWS, not TASKS; the tally needs two commands and their sum |
| `BEN-427` | a negative control that fires on nothing looks like one that fires correctly, unless you read the OUTPUT |

> **Here the count is CORRECT and the INFERENCE DRAWN FROM IT IS INVALID.** No better measurement of the tally
> would have helped — `3` and `4` were both right. **That is a different defect from a wrong number, and it is
> not addressed by measuring more carefully.**

## 4. The second instance the same day, which is what argues mechanism rather than slip

`9bb2d5b8` found a **repo-global COUNT assertion** — `n_shell_files` in
`nd-unfolding/tests/test_p4_sweep_snapshots.py` — pinned at `374` against a measured `382`.

> **A count cannot distinguish `+1` from `−1` from `+1 −1`.** One `sbatch_*.sh` deleted and one added leaves the
> count identical — **so even when GREEN the assertion is blind to a RENAME, which is precisely what `CLAUDE.md`
> forbids on the grounds that `115 sbatch_*.sh` names are LOAD-BEARING PROVENANCE.**

**And the same file already carried the rule, twenty lines from the failing assertion:**

```python
# nd-unfolding/tests/test_p4_sweep_snapshots.py:128-133
def test_new_unchecked_fields_are_surfaced_by_name(self):
    """Counts alone would let one field appear as another disappears."""
    cur  = set(...["recorded_fields"]["fields"]);  snap = set(...)
    self.assertEqual(cur - snap, set(), ...);      self.assertEqual(snap - cur, set(), ...)
```

> **Written by that file's own author, predating every arrival of this rule today, and applied to a SIBLING SWEEP
> rather than to the failing one.** The insight was in the file; its application was partial. **Nothing propagated
> it twenty lines** — which is `BEN-467`'s procedural half at the shortest distance yet recorded.

**Four independent arrivals in one repo, the earliest already committed, and three lanes still re-derived it on
2026-08-19. That is evidence about PROPAGATION, not about the rule.**

## 5. The remedy, which is executable and costs nothing

> **PRINT THE SET DIFFERENCE, NOT THE TWO COUNTS.**
>
> `pytest -q` already names its failures; the summary removed them. **The repair is one line of output, and it
> converts an unfalsifiable report into a checkable one.**
>
> **NOT SPECIFIC TO TESTS.** It holds for **any** before/after comparison where **the assertion is CONTAINMENT and
> the evidence is a TALLY** — failure sets, key sets, bin supports, job arrays, file corpora. Wherever the claim
> is *"nothing new appeared"*, the witness is `cur - snap`, and a pair of cardinalities is not a witness.

## 6. Standing

**I have none, and it belongs in the row.** Every figure in this campaign's anchor determination that I have had
to reconcile was **a count I quoted without its identity** — a denominator from another product (`BEN-466`), a grid
where the support was meant (`BEN-467`), and a set of snapshot keys I printed and did not read. **The lane that
reported three failures re-measured by name within one turn of being asked, which is faster than I corrected any
of mine.**
