# VERIFICATION 2026-08-22 — `build-k0-execution-integrity` against the k=0 review contract

**Verdict: NOT A PASS.** Against
[`REVIEW-CONTRACT-20260822-k0-execution-integrity.md`](REVIEW-CONTRACT-20260822-k0-execution-integrity.md)
§F — whose own rule is *"Any single miss is a FAIL; there is no partial credit and no waiver by
caveat"* — the eighteen criteria come out **7 PASS, 6 FAIL, 5 NOT-EVALUABLE**. Nothing here
authorizes a submission and nothing here is a merge.

**Reviewer eligibility (F-18).** Written by a fresh non-builder who has authored no code in this
repository, wrote no part of the contract, the plan or the decision, and did not build what is under
review. Every measurement below was produced read-only from an isolated worktree
`/Users/josephbailey/local-research/mnv-k0-verify` at `ae42ae8dec1417bb7be71bc9e314ac7f18c33ab5`,
with a pristine detached comparison worktree `/Users/josephbailey/local-research/mnv-k0-base` at the
branch point `8c156a374a00e024b9f28d575d38c75f345dcb3b`. **No Slurm job was submitted**, no
scientific artifact was opened, moved or deleted, the 41.44 GB `*combined_bkgaware.root` was not
touched, and no `--allow` run of any kind was performed. The only cluster contact was four read-only
`ssh saul.nersc.gov` invocations, recorded inline.

**Subject.** Branch `build-k0-execution-integrity` @ `ae42ae8dec1417bb7be71bc9e314ac7f18c33ab5`,
one commit, branched from `main` `8c156a37`. `git diff --stat 8c156a37 ae42ae8d` → 24 files,
1835 insertions, 83 deletions. **Not merged, and this document does not merge it.**

**Governing documents, read in the contract's own order:** the contract (§F, 18 criteria);
[`DECISION-20260822-joseph-b1-lift-and-clause-c.md`](DECISION-20260822-joseph-b1-lift-and-clause-c.md)
rulings 17, 18 and 19; [`PLAN-20260822-oneMember-mii-staged.md`](PLAN-20260822-oneMember-mii-staged.md)
Amendments 1, 2 and the builder's Amendment 3.

---

## 0. THE ANSWER TO THE QUESTION THAT MATTERS MOST — CORRECTION 2 IS **NOT** MET

Joseph's correction 2 requires *"the minimum OI-136 protection necessary for every Python entrypoint
on this path, including the adopter's subprocess boundary."*

**No. This build does not meet it, and the shortfall is not marginal.** Measured, not inferred:

```
cd nd-unfolding && grep -c 'mnv_guarded_run' \
  sbatch_bootstrap_5d_gpu.sh sbatch_seedscan_split_5d.sh \
  sbatch_unfold_5d_detector_bkgaware_gpu.sh sbatch_sweep_bank_5d_run_bkgaware_gpu.sh \
  sbatch_uthrow_run_5d_fast.sh sbatch_uthrow_block_5d.sh \
  sbatch_uthrow_combine_5d_fast.sh sbatch_finalize_5d_bkgaware_gpu.sh
→ 0 in all eight (grep exit 1)
```

and at the child boundary, `mii_adopt_unified_5d_stamped.py:710-712` is unchanged on this branch:

```python
argv_child = build_child_argv(a.uthrow, a.combined, a.out, a.extras)
print(f"[remedyA] running the PINNED writer as a subprocess: {' '.join(argv_child)}")
rc = subprocess.call(argv_child)
```

So **not one Python entrypoint on the k=0 path is protected by the guard at run time, and the
adopter's subprocess boundary is protected by nothing at all.** The guard was improved (B-4
containment, P-1 inventory) and is well tested; it is simply never invoked by anything that will
run. That is the OI-64 shape — *"an unwired check is a check nobody runs"* — which this repository's
own ratchet test names in its docstring.

**What the build DID achieve on correction 2's subject, and it is real.** The six source repairs and
the two-root launcher repair mean the *wrong tree is no longer selected*. That is genuine and
verified below (F-11, F-13, and §2). But selection is not measurement: the contract's §0 exists
precisely because *"a green production arm may be vacuous"*, and the whole positive arm (§4, P-1
through P-4, F-4 through F-8) was specified as the instrument that turns a green run into evidence.
This build ships that instrument and connects it to nothing. A run of legs 1–6 today would emit no
inventory, and its exit 0 would be indistinguishable from a clean run in exactly the way §0 forbids.

### The minimum additional change, and whether ruling 18 covers it

**(a) Route the production entrypoints through the guard — 8 one-line edits, one per launcher.**

```bash
mr_run "${OUT}" python3 "${CODE_ROOT}/nd-unfolding/mnv_guarded_run.py" \
       --expect-root "${CODE_ROOT}" --inventory "${INV}" \
       -- "${CODE_ROOT}/nd-unfolding/bootstrap_nd.py" ...
```

**A point that is not obvious and that changes the cost-benefit: after the six repairs, this now
works.** The contract's B-1 said *"a wrapper cannot help them and would block the run"* and gave
`bootstrap_nd.py`'s `import xsec_nd` resolving under the canonical checkout as the reason the guard
would *correctly exit 3*. **That argument was about the PRE-repair bytes and it has expired.**
Post-repair, `_ND = str(Path(__file__).resolve().parents[0])`, so an entrypoint launched from
`${MNV_CODE_ROOT}/nd-unfolding` resolves its imports under `--expect-root`, the guard's B-4 script
check passes, and the run goes green **non-vacuously** — `checked > 0` and `repo_origin_count > 0`,
which is exactly P-2. Re-measured M-1 (§3, F-17) confirms every one of the six still imports 3–5
repository modules after its insert, so there is something for the guard to inspect on every leg.
The wrapper is no longer a blocker; it is the only thing that produces F-4/F-5's evidence.

*Authorization:* ruling 18 authorizes *"the eight launchers' shell-root repairs"* and *"the
necessary guard, tests, ... couplings"*. The files are inside the authorized set; the specific edit
("shell-root repair") is narrower than this. **My reading: inside ruling 18's file set, outside its
named repair, so it needs one confirming word from Joseph rather than a new authorization round.**
The builder's Amendment 3 C-5 reads the same fence the same way and declined — that reading is
defensible, and I am not calling it wrong. I am recording that the consequence of the fence, as
drawn, is that correction 2 is unmet and the contract's entire positive arm has no carrier.

**(b) `build_child_argv` must emit the guard — for the subprocess boundary specifically.**

*Authorization:* **outside** ruling 18. It names six Python repairs and
`mii_adopt_unified_5d_stamped.py` is not one of them. The builder's reason is correct as far as it
goes.

*And state its value honestly, because it is smaller than Amendment 1 §D claimed.* Wrapping the
child does **not** buy import protection today: M-1 re-measured on this branch still shows
`adopt_unified_5d.py` importing **the empty set** of repository modules, so its guarded run would
refuse nothing — that is the contract's B-2 and it survives. What wrapping the child *does* buy is
(i) the F-6 record, an explicitly empty, flagged `repo_origin_count: 0` inventory line for the child
process, which is the only thing that can distinguish "no repository import occurred" from "the
inventory did not run"; and (ii) the §H.1 insurance, because `PINNED_WRITER` is
`os.path.join(_HERE, "adopt_unified_5d.py")` — derived from the parent's `__file__` — so B-4
containment on the child is trivially satisfied and adds nothing, while a colliding name appearing
among the canonical checkout's 717 untracked files would make the file's insert live overnight.

**Do not soften this into "mostly done."** Correction 3 (do not execute from the dirty canonical
checkout) is substantially discharged by the two-root work. Correction 2 is not discharged at all in
its measurement half.

---

## 1. §F — criterion by criterion

Every command below was run by me. Where a criterion requires a production run, that run does not
exist: **NOT-EVALUABLE is not a pass**, and under §F's no-partial-credit rule an unevaluable
criterion cannot be counted toward one.

### Tree

**F-1 — `MNV_CODE_ROOT` satisfies A-2(a)–(g) before the first `sbatch` and after the last leg.
NOT-EVALUABLE.**
No code root has been constituted and no `sbatch` was run. The A-2(a)–(g) checklist is written down
faithfully at `RUNBOOK-20260822-b1-lift-preflight.md` §0b-i (all seven rows, verbatim in substance),
so the *instruction* exists; the *measurement* cannot exist until a tree is designated.
`grep -rn 'MNV_CODE_ROOT=' docs/ nd-unfolding/` finds only the placeholder
`<the approved clean tree at the declared sha>`.

**F-2 — no production process executes or imports any file under the canonical checkout,
established by P-2 plus A-3's `--pair` set. NOT-EVALUABLE, and unsatisfiable as specified.**
No production process ran. Separately: the criterion names two instruments and **neither is wired**.
P-2 is read off P-1 inventories, and no launcher invokes the guard (§0). A-3's
`verify_executing_copy_is_committed.py --pair` is called by zero of the eight
(`grep -c verify_executing_copy_is_committed <the eight>` → 0 each, grep exit 1). The builder
discloses both in Amendment 3 C-5. So even after a run, F-2 could not be established the way the
contract requires — only "by inspection of the commands", which F-2 explicitly refuses.

**F-3 — `--allow` appears in no production invocation. NOT-EVALUABLE (script half PASSES).**
Script half, measured: `grep -c '\-\-allow' <the eight>` → 0, 0, 0, **1**, 0, 0, 0, 0. The single
hit is `sbatch_sweep_bank_5d_run_bkgaware_gpu.sh:11`, a comment reading
`FAIL-CLOSED: no --allow-cv-background`, which is a different flag on a different program and not a
guard `--allow`. Guard `--allow` count across the eight: **zero**. `test_n2_child_boundary.py::
test_E_no_allow_appears_on_any_arm` asserts the same for the N-2 arms. The job-stdout half cannot be
evaluated: there is no job stdout.

### Positive arm

**F-4 — every guarded process emitted a P-1 inventory; count of inventories == count of guarded
processes. FAIL.**
The count of guarded production processes is **zero** (§0). Read literally, `0 == 0` and this
"passes" — and that reading is exactly the vacuity §0 was written to forbid, so I refuse it. F-4's
subject is that every process on the path is guarded and every guarded process leaves a record.
Neither half exists on legs 1–6. The mechanism itself is sound and I verified it independently:
`python3 tests/test_mnv_guarded_run.py` → `Ran 41 tests ... OK`, including
`TheInventoryIsThePositiveEvidence::test_it_APPENDS_so_a_multi_process_run_keeps_every_record` and
`test_an_UNWRITABLE_inventory_downgrades_a_green_run_to_CANNOT_CHECK`.

**F-5 — P-2 holds for every inventory (all origins under `MNV_CODE_ROOT`, all sha256 match the
A-2(f) manifest, `checked > 0`). FAIL.**
There are no inventories, and there is no A-2(f) source manifest to match sha256 against — no code
was written to produce one, on either side of the comparison. `grep -rn 'A-2(f)\|source manifest'`
over `nd-unfolding/` finds nothing executable.

**F-6 — P-3's disclosure is present for `adopt_unified_5d.py` and its `repo_origin_count` is
recorded as an explicit `0`. FAIL.**
The *guard-side half is built and correct*: `mnv_guarded_run.write_inventory` writes
`repo_origin_count` and `repo_origin_inventory_is_empty` unconditionally, with two distinguishable
green verdicts (`VERDICT_INSPECTED` / `VERDICT_EMPTY`), covered by
`test_an_entrypoint_with_NO_repository_import_is_EXPLICITLY_EMPTY_not_silent`, which asserts key
presence, `count == 0`, the flag `True`, `checked > 0`, and the stderr line. That is a good
implementation of P-3. **But the child is not guarded, so no such record will ever be produced for
`adopt_unified_5d.py`**, and the B-2 disclosure sentence appears nowhere outside the contract itself
(`grep -rn "refused nothing because" docs/ nd-unfolding/` → 1 hit, the contract, line 264). There is
no run receipt to carry it.

**F-7 — P-4's per-entrypoint import-set identity ratchet holds. FAIL.**
**No mechanism exists.**
`grep -rn 'expected_imports\|import_set\|EXPECTED_IMPORTS\|import-set' nd-unfolding/mnv_guarded_run.py
nd-unfolding/tests/ docs/orchestration/RUNBOOK-…md docs/orchestration/PLAN-…md` → 0 hits, grep exit 1.
P-4 was not implemented and is not mentioned in Amendment 3 C-5's list of disclosed gaps, so this is
a gap the builder did **not** disclose.

**F-8 — P-5's blind spots stated in the receipt; P-6's entrypoint enumeration published with its
command. FAIL.**
P-5: no receipt exists, and the required subprocess enumeration
(`grep -n "subprocess\.\(run\|call\|Popen\)\|os\.system\|os\.exec"` over the entrypoint set) is not
published anywhere on the branch. P-6: `grep -rn 'P-6\|entrypoint enumeration' RUNBOOK-…md PLAN-…md`
→ 0 hits, grep exit 1. The contract required the enumeration be **re-run on `MNV_CODE_ROOT` at the
pinned sha and its full output published**; it was not re-run and not published. The guard's own
docstring does state the namespace-package and `sys.modules` blind spots, which is a partial and
welcome discharge of P-5 in the code — but P-5 asks for them in the receipt, and there is no receipt.

### Negative controls

**F-9 — N-1 exits 3, names `seed_offset_policy`, names both roots, satisfies O-1…O-4. FAIL.**
N-1 was not performed. It is a cluster control by construction (it runs the real
`mii_adopt_unified_5d_stamped.py` from the canonical checkout under the guard) and no cluster
execution of any kind appears in this branch. There is no artifact, log or receipt for it.
`grep -rn 'N-1' nd-unfolding/tests/` finds only cross-references. Note this is **not** blocked by
authorization: N-1 needs no fixture, no copy, no edit and no ROOT, per the contract's own §5.

**F-10 — N-2 exits 3 through the child wrapper on the `build_child_argv` template, satisfying
O-1…O-4. PASS, as amended by ruling 19.**
`python3 tests/test_n2_child_boundary.py` → `Ran 7 tests ... OK` (TMPDIR=/private/tmp). I read every
arm rather than the exit code:
* the fixture writer lives **inside** the disposable expected checkout, so B-4 cannot be what fires
  — ruling 19's central objection to the contract's own N-2 is respected;
* the victim is the **real** `seed_offset_policy` resolved out of the **real** repository as the
  second checkout, so nothing is fabricated;
* the argv comes from `STAMPED.build_child_argv(..., writer=fixture)` — the production function —
  and `test_D` asserts `argv[argv.index("--")+1:] == child[1:]`, i.e. the wrap forwards verbatim;
* **O-1**: `test_A` (unguarded) emits `[fixture-writer] O1-MARKER about to open the output` and
  writes the file; `test_C` (guarded) asserts the marker is **absent** and that `STARTED` is
  **present** — the same binary, two outcomes, and the non-vacuity check that the writer really
  started rather than failing at launch;
* **O-2**: `_empty_outdir` asserts the directory starts empty, and after the refusal asserts
  `not out.exists()` and `os.listdir(outdir) == []`;
* **O-3**: one merged stream (`stderr=subprocess.STDOUT`), the banner's index is located, and every
  line at or after it is asserted not to start with `[fixture-writer]` — a genuine interleaving
  argument, not a stdout-vs-stderr comparison;
* **O-4**: the status is `subprocess.run(...).returncode`, captured into a variable, never read
  after a pipe;
* §5.5's fixture rule is `test_A` and it asserts the loaded module's `__file__`, not exit 0.

One recorded difference from the contract, and it is ruling 19's doing, not the builder's: the
contract's O-1 wanted the paired arm to be *the same file guarded with `--expect-root` set to its
own tree*; ruling 19 specified *"unguarded: prove the wrong module loads"*, and that is what was
built. I accept the ruling's form.

**F-11 — N-3 holds for each of the six B-1 files, both directions. PASS, with its limit stated.**
`python3 tests/test_n3_rooted_import_repair.py` → `Ran 5 tests ... OK`.
The criterion I was asked to judge is whether it *genuinely shows the repairs repaired something*
given that only each file's root-resolution prologue executes. **It does**, for four reasons I
checked myself:
1. the pre-repair bytes come from `git show 8c156a37:<path>`, not from inverting the repair, so the
   fixture cannot be derived from the rule it tests; the only edit is the cluster root → scratch
   stand-in, and that substitution is asserted to have changed the string and removed the root;
2. the cut is located by `ast`, at the **last top-level statement containing a `sys.path.insert`**,
   and asserted to be the file's own insert — I re-derived the cut line for all six independently
   (28, 37, 77, 51, 42, 61) and each is that file's insert statement;
3. the hijack direction is asserted on the loaded module's `__file__`, and there is a separate
   `PYTHONPATH`-cannot-outrank-position-0 arm, which is the exact reason a re-deploy or an env var
   is the wrong repair;
4. the silent direction (post-repair resolves to its own tree) is asserted on `__file__` too.

Its stated limit is real and correctly stated: nothing below the cut runs, so this says nothing
about the science, and `ROOT` is a stub. That limit does not touch the claim being made.

**F-12 — §5.5's hijack arm demonstrated for N-1, N-2 and each N-3 by asserting `__file__`. FAIL.**
N-2 ✓ (`test_A`), N-3 ✓ (`test_PRE_repair_the_entrypoint_imports_the_OTHER_trees_copy`), **N-1 ✗** —
N-1 does not exist, so its hijack arm does not either.

### Repairs and couplings

**F-13 — B-4's script-containment refusal is implemented and covered in both directions. PASS.**
`mnv_guarded_run.py:450-464`: `script_root = checkout_root_of(str(script.resolve()))` at `:450`,
refusing with `VIOLATION_EXIT` when it is a checkout other than `--expect-root`, and
`guard = install(...)` is at `:465` — so the check is placed **before `install()`** and
the refusal precedes the first import as well as the work. `--allow` deliberately does not extend to
it, and that is asserted, not merely commented. Coverage, both directions and then some:
`test_a_script_in_another_checkout_is_refused_3`,
`test_the_SAME_script_inside_expect_root_is_NOT_refused`,
`test_allow_does_NOT_launder_a_script_from_another_checkout`,
`test_a_script_outside_EVERY_checkout_is_not_refused_and_is_recorded_as_such`,
`test_the_refusal_happens_before_the_script_produces_anything`, and the fixture-rule arm
`test_unguarded_the_forbidden_copy_really_runs_and_says_so`. The B-4 trap was respected: the guard
gains no new occurrence of the root literal — the probe's candidate count moves 118 → 115 and the
guard is not among the movers.

**F-14 — every row of §6 is discharged in the same commit as the repair that moves it. PASS on §6's
six rows.** Each verified independently in §2 below: the ratchet constants (58/`21828143…` →
52/`40bd83ca…`, both reproduced from the probe's own printed output), the probe's
`POSITIVE_CONTROLS` replacement, the `:157` `--pair` assertion (green), the four required new arms of
`test_mnv_guarded_run.py` (present, plus 13 more), `verify_hash_bindings.py` (green, re-run after the
edits), and the RUNBOOK §0b / PLAN Amendment 3 rewrite. **A separate coupled-artifact defect that is
not one of §6's rows is recorded as Finding 1 below and it is real.**

**F-15 — `python3 -m unittest` over the two named files is green, counts quoted as measured, with an
explicit `TMPDIR`. PASS.**
```
cd nd-unfolding/tests && TMPDIR=/private/tmp python3 -m unittest \
    test_mnv_guarded_run test_oi136_failopen_inventory_ratchet -v
→ Ran 48 tests in 2.565s / OK / exit 0
```
Measured counts: `grep -c 'def test_'` → **41** in `test_mnv_guarded_run.py` (M-8 recorded 24 before
this branch; the branch adds 17) and **7** in the ratchet. 41 + 7 = 48, which matches the runner.
Negative control on the harness itself: `python3 -m unittest test_mnv_guarded_run.NoSuchClass` →
`FAILED (errors=1)`, so a failure would have been visible. **Environment note, not a build defect:**
`python3 -m unittest tests/test_mnv_guarded_run.py` from `nd-unfolding/` fails with
`ModuleNotFoundError: No module named 'tests.test_mnv_guarded_run'` because a `tests` package in
`site-packages` shadows the directory — `python3 -c "import tests; print(tests.__file__)"` →
`…/miniconda3/lib/python3.12/site-packages/tests/__init__.py`. Running from inside `tests/` avoids it.

**F-16 — `verify_hash_bindings.py` exits 0 with `ALL BINDINGS INTACT` after all edits. PASS.**
```
cd <verify worktree> && TMPDIR=/private/tmp python3 docs/orchestration/verify_hash_bindings.py
→ exit 0; "resolved 133 bindings (806 unresolvable…)"; "132 OK"; "ALL BINDINGS INTACT"
```
Run at `ae42ae8d`, after the edits, in a worktree with `git status --porcelain | wc -l` = 0. Byte-for-byte
the same summary lines at the base worktree `8c156a37`, so **no binding moved**. Note the contract's
M-3 quotes "133 OK"; the live output is `resolved 133 bindings` / `132 OK`. That is a difference in
which number M-3 copied, not a change in the world — base and branch agree exactly.

### Freshness

**F-17 — M-1…M-6 re-measured on `MNV_CODE_ROOT` at the pinned sha and on the canonical checkout at
submission time. NOT-EVALUABLE (no code root, no submission), with what I could re-measure filed.**
See §3. In summary: **M-1 reproduces** (the import sets are unchanged and `adopt_unified_5d.py` is
still the empty set), **M-4 reproduces exactly** on the cluster today, **M-5 and M-6 are now false by
authorized construction**, and **M-8's 24 is now 41**. M-2 and M-3 were not re-measured on a code
root because there is no code root.

**F-18 — the PASS is recorded by a fresh non-builder against this document clause by clause. PASS in
form.** This document is that record: eighteen numbered verdicts, each with the command and its
output, written by a non-builder. It records a **FAIL**, not a PASS. §F's own anti-pattern — *"a
summary attesting 'all controls passed' is a FAIL of F-18"* — is avoided.

**Tally: PASS F-10, F-11, F-13, F-14, F-15, F-16, F-18 (7). FAIL F-4, F-5, F-6, F-7, F-8, F-9, F-12
(7). NOT-EVALUABLE F-1, F-2, F-3, F-17 (4).**

---

## 2. Independent verification of the repairs and couplings

Everything in this section was measured by me from the artifact, not read from the builder's report.

### 2.1 The six repairs — `parents[N]`, and no absolute fallback

Whole-file AST walk over each of the six, listing every `sys.path` insert argument and every
`parents[N]`:

| file | `parents[N]` | inserts | verdict |
|---|---|---|---|
| `nd-unfolding/bootstrap_nd.py` | `parents[0]` :27 | `sys.path.insert(0, _ND)` :28 | correct — needs only `nd-unfolding/` |
| `nd-unfolding/seedscan_split.py` | `parents[0]` :35 | :37 | correct — needs only `nd-unfolding/` |
| `nd-unfolding/unfold_nd_omnifold_unbinned.py` | `parents[1]` :63 | :77 and **:971** `insert(0, _OF)` | correct — the second, in-function insert derives `_OF` from the repaired `_REPO`, so it moved too |
| `nd-unfolding/sweep_bank_5d.py` | `parents[1]` :48 | :51 | correct — inserts both `2d-` and `nd-unfolding/` |
| `nd-unfolding/unified_throw_cov_5d.py` | `parents[1]` :39 | :42 | correct |
| `nd-unfolding/unified_throw_cov.py` | `parents[1]` :58 | :61 | correct — module, in the set per ruling 18's transitive reason |

**No absolute fallback survives in any of the six.** I ran a transitive taint analysis (fixed point
over `Assign` / `AnnAssign` / `For`-target, propagating through f-strings, then testing every
`sys.path.insert/append/extend` argument):

```
bootstrap_nd.py            tainted=[]                                               BAD_INSERTS=[]
seedscan_split.py          tainted=[]                                               BAD_INSERTS=[]
unfold_nd_omnifold_…py     tainted=['_DATA_2D', '_DATA_ROOT']                        BAD_INSERTS=[]
sweep_bank_5d.py           tainted=['OMNIFILE_5D','SWEEPDIR','VLIST','_DATA_ROOT']   BAD_INSERTS=[]
unified_throw_cov_5d.py    tainted=[]                                               BAD_INSERTS=[]
unified_throw_cov.py       tainted=['_DATA_ROOT']                                    BAD_INSERTS=[]
```

**So the builder's substantive claim is TRUE: the `_DATA_ROOT` constant reaches argparse defaults and
data paths only, and no `sys.path` statement in any of the six touches it.** I confirm the property.

### 2.2 …but the ASSERTION of that property is much weaker than its docstring says

The builder states, in the commit message and at
`tests/test_n3_rooted_import_repair.py:180-183`, that this is *"asserted here rather than trusted"*
for *"the three files that keep the literal"*. **Measured, that assertion has power over one file,
and only against two of four ways to violate it.**

*It analyses the prologue, and for two of the three files the literal is BELOW the cut:*

| file | prologue cut | `CLUSTER_ROOT` inside the analysed text? | rooted names the assertion can see |
|---|---|---|---|
| `unfold_nd_omnifold_unbinned.py` | line 77 | **yes** | `['_DATA_ROOT']` |
| `sweep_bank_5d.py` | line 51 | **no** (`_DATA_ROOT` is at :59) | `[]` |
| `unified_throw_cov.py` | line 61 | **no** (`_DATA_ROOT` is at :69) | `[]` |

*And mutation-testing the assertion body against `unfold_nd_omnifold_unbinned.py`, the one file where
it can see anything:*

| mutation | caught? |
|---|---|
| `sys.path.insert(0, "<cluster root>/nd-unfolding")` — bare literal in the insert | **caught** |
| `sys.path.insert(0, _DATA_ROOT)` — the rooted name directly in the insert | **caught** |
| `sys.path.insert(0, _DATA_2D)` — one hop derived (`_DATA_2D = f"{_DATA_ROOT}/2d-unfolding"`, a `JoinedStr`, so it never enters the `rooted` set) | **NOT caught** |
| `for p in (_2D, _ND, _DATA_ROOT):` — rooted value entering through the loop **iterable**, which is the shape four of the six actually use | **NOT caught** |

The last row is the important one: the assertion inspects the `Name` nodes *inside the insert call*,
and in four of the six files that call is `sys.path.insert(0, _p)` inside a `for` loop, so the only
name it ever sees is the loop variable. **The property holds today — I verified it transitively — but
the test that claims to guard it would not fire on the most likely way to break it.** This is a
FINDING against the strength of a control, not a defect in the code under it, and it does not change
F-11's verdict because F-11 is about N-3's two directions, both of which are genuine.

### 2.3 The eight launchers — mandatory `:?`, no defaults, unset **and** empty refused

Form: all eight carry `CODE_ROOT="${MNV_CODE_ROOT:?…}"` and `DATA_ROOT="${MNV_DATA_ROOT:?…}"`.
`grep -nE '^[[:space:]]*(export[[:space:]]+)?REPO=' <the eight>` → **no match, exit 1**: the
unconditional hardcode is gone from all eight. `grep -nE 'MNV_(CODE|DATA)_ROOT:-'` → no match,
exit 1: **no defaulted form anywhere**. Non-comment occurrences of the cluster literal in the eight:
**0 in every file**.

Behaviour, four arms per launcher, run rather than read. The fragment is `head -n <the DATA_ROOT
line>` of each real launcher — which **includes the `set -eo pipefail` line**, so the extraction does
not lose the options above the cut — plus `echo REACHED_END`:

| arm | all eight |
|---|---|
| both variables unset | exit **1** |
| `MNV_CODE_ROOT=` (empty) | exit **1** |
| `MNV_DATA_ROOT=` (empty) | exit **1** |
| both set (positive control) | exit **0**, stdout `REACHED_END` |

The positive control matters: without it, four refusals would be consistent with a fragment that
cannot run at all.

**Confirmed on the target interpreter, because `set -e` and parameter-expansion semantics must not be
measured on the wrong shell.** Local `/bin/bash` is 3.2.57 (macOS); Perlmutter is
`GNU bash, version 4.4.23(1)-release`. Re-run over `ssh saul.nersc.gov 'bash -s'` with the fragment
on stdin (writes nothing on the cluster) for `sbatch_seedscan_split_5d.sh` and
`sbatch_finalize_5d_bkgaware_gpu.sh`: unset → 1, empty → 1, both set → `REACHED_END` / 0. Same
answers on both interpreters.

Beyond the contract's ask, and verified: every `source` and every `python3` in the eight resolves
under `${CODE_ROOT}` by absolute path, `cd` goes to `${DATA_ROOT}/nd-unfolding`, and
`setup_salloc_env.sh`, `lib/resume_guard.sh` and `nd-unfolding/lib_member_resume.sh` contain no
`PYTHONPATH` assignment and no cluster literal, so nothing re-injects the data root onto `sys.path`.
A member-library containment check (`exit 2` when the resolved library is not
`${CODE_ROOT}/nd-unfolding`) is present in all eight, byte-identically by message.

### 2.4 The ratchet — both constants re-derived from the probe's own printed output

I did not take 52 or the digest from the test file. I ran the probe in each worktree and recomputed
the digest the way the test does (`sha256` over `"".join(r + "\n" for r in sorted(rels))`):

| tree | probe exit | header line | fail-open count | digest |
|---|---|---|---|---|
| base `8c156a37` | 0 | `[118 .py contain the hardcoded root; 58 FAIL-OPEN, 13 insert-but-not-rooted, 47 no insert(0,…)]` | **58** | `21828143e40961c9c8f5ee9f0e7a3473f915462a6e440581af8859963943be66` |
| branch `ae42ae8d` | 0 | `[115 .py …; 52 FAIL-OPEN, 16 insert-but-not-rooted, 47 no insert(0,…)]` | **52** | `40bd83ca3993f1a383d38a3a57e9479058224f6d7f0bd00a241f8955a6269d86` |

Both recorded constants match my recomputation exactly, at both ends. The candidate move 118 → 115
and the negative-control bucket move 13 → 16 also match the file's stated reasoning. Both worktrees
had `git status --porcelain | wc -l` = 0, which matters: the ratchet walks the working tree, and a
peer's live worktree has previously made it read 369.

**Exactly six paths left the set, and zero joined:**

```
./nd-unfolding/bootstrap_nd.py
./nd-unfolding/seedscan_split.py
./nd-unfolding/sweep_bank_5d.py
./nd-unfolding/unfold_nd_omnifold_unbinned.py
./nd-unfolding/unified_throw_cov.py
./nd-unfolding/unified_throw_cov_5d.py
```

— precisely the B-1 / ruling-18 set, no more and no less. **"58 is not a target" is honoured: the
number fell because six named files were repaired, and the same six are named in the test file with
their `parents[N]`.**

**The replacement positive control was chosen from the probe's printed list, and its stated reason
holds.** `./3d-unfolding/unfold_3d_omnifold_unbinned.py` appears in the probe's fail-open output at
**both** ends (the 58-set and the 52-set), so it was selectable from printed output rather than
guessed. Its cited shape checks out at the cited lines: `_REPO` :39, the derived
`_2D = f"{_REPO}/2d-unfolding"` :40, `sys.path.insert(0, _2D)` :42, and
`sys.path.insert(0, f"{_REPO}/3d-unfolding")` :45. I then reconstructed the probe's `rooted_names()`
branches and classified all 52 members by which branch flags them:

```
Counter({('LOOP',): 39, ('DIRECT',): 12, ('DIRECT','DERIVED'): 1})
files flagged via the DERIVED branch:  ./3d-unfolding/unfold_3d_omnifold_unbinned.py   ← the only one
./nd-unfolding/adopt_unified_5d.py → ['LOOP']
```

**The claim that it is the only remaining member exercising the derived-name branch is TRUE**, so
without it that branch of the classifier would have had no control. One imprecision, immaterial: the
comment says every other candidate binds "through the LOOP branch only" — 12 of them bind through
the direct-assignment branch. My classifier is my own decomposition of `rooted_names()`; the probe
does not label branches, so treat the table as a reconstruction.

No digest binding on the replacement: `shasum -a 256` →
`2c228ce58e51fe64c6e342d9cde051895c199a828af99a396957f2e44d780df3`, and
`grep -rl <that digest> docs nd-unfolding 2d-unfolding 3d-unfolding` → **0 hits, exit 1** (status
read unpiped). Consistent with the builder's stated search.

One instrument caveat, checked rather than assumed: the probe shells out to `grep`, and this session's
interactive `grep` is a `ugrep` wrapper. It does not apply — `subprocess.run(["grep", …])` execs
`/usr/bin/grep` (`shutil.which('grep')` → `/usr/bin/grep`), and running the probe's exact discovery
command directly with `/usr/bin/grep` returns the same **115** candidates.

### 2.5 B-4 containment and the P-1 inventory, in the guard

Verified by reading the implementation and by the 41-arm suite (see F-13, F-4, F-6). Two design
points I checked specifically because they are easy to get wrong:

* the refusal ordering is real — the containment check sits above `guard = install(...)`, so it
  precedes both the work and the first import, and `_safe_inventory` is called on that path;
* the inventory is written from a `finally`, so a refused run also leaves a record; an unwritable
  inventory downgrades a would-be `0` to `2` but leaves a `3` as `3`. Both directions are tested
  (`test_an_UNWRITABLE_inventory_downgrades_a_green_run_to_CANNOT_CHECK`,
  `test_an_unwritable_inventory_does_NOT_downgrade_a_REFUSAL`). One residual, minor and unexercised:
  when the child raises `SystemExit`, the `finally` computes `recorded` but the exception propagates,
  so an inventory-write failure on that path does not downgrade. It cannot mask a violation.

**The "explicitly empty FLAGGED" requirement is met and is genuinely distinguishable.**
`test_an_entrypoint_with_NO_repository_import_is_EXPLICITLY_EMPTY_not_silent` asserts key presence
(not just value), `repo_origin_count == 0`, `repo_origin_inventory_is_empty is True`,
`verdict` starting `EMPTY-REPOSITORY-ORIGIN-SET`, **and `checked > 0`** — that last assertion is what
separates "it looked and found nothing repository-local" from "it never looked". Its sibling
`test_a_repository_import_is_recorded_with_its_origin_root_and_digest` asserts the other verdict
string with the origin path, checkout root and sha256. The two verdict strings are asserted unequal.
This is the right shape.

### 2.6 The DECOY question — scope difference, but a live documentation trap

`test_uq_remediation.py::LibraryResolverSurvivesSbatch::
test_a_DECOY_library_in_the_spool_would_be_used_and_that_is_CORRECT` asserts that a spool directory
containing `lib_member_resume.sh` would be used, and its docstring says *"recorded so nobody 'fixes'
it"* and *"the file beside the running script IS the frozen library in a direct deployment."*

**Judgement: it is a SCOPE DIFFERENCE, not a logical contradiction — and it is nonetheless a real
defect that should be repaired.**

Not a contradiction, because the two assertions have different units. `_block()` extracts the
resolver **verbatim from `# --- M(ii) member axis: LOCATE` down to the `source … mr_require_valid_offset`
line inclusive**, and the new containment check is placed *after* that line, deliberately and
disclosed. So the DECOY test measures a fragment that still behaves as it says: the resolver *does*
pick the spool copy. The launcher then refuses it two lines later.

But the docstring's claim is about the file, not the fragment, and **on these eight launchers it is
now false**: under ruling 17 the frozen library must be under `MNV_CODE_ROOT`, and a "direct
deployment" beside the running script somewhere else is exactly what the new check exits 2 on. A
test that instructs future readers not to fix a behaviour the file no longer has is a trap of the
kind this repository has been bitten by before — a caveat that a later ruling turns into a live
defect. **Minimum remedy, documentation only, no behaviour change:** scope the docstring to the
resolver fragment and record that the eight k=0 launchers now refuse any resolution outside
`${MNV_CODE_ROOT}/nd-unfolding`. I am reporting it, not fixing it.

Incidentally, that test is currently **red for an unrelated reason on both trees** — see Finding 2 —
so it is not presently asserting anything about either subject.

---

## 3. Freshness re-measurement (partial discharge of F-17)

**M-1 — re-measured on this branch, from `nd-unfolding/`, same method (AST, first `sys.path` insert,
top-level names of `nd-unfolding/` + `2d-unfolding/` = 123 in this tree):**

| entrypoint | root literal | first insert | repository modules imported AFTER it |
|---|---|---|---|
| `bootstrap_nd.py` | **no** (was yes) | :28 | `omnifold_nn_core, seed_offset_policy, xsec_nd` |
| `seedscan_split.py` | **no** (was yes) | :37 | `omnifold_nn_core, seed_offset_policy, xsec_nd` |
| `unfold_nd_omnifold_unbinned.py` | yes (`_DATA_ROOT` only) | :77 | `flux_universe, seed_offset_policy, unfold_2d_omnifold_unbinned, xsec_nd` |
| `sweep_bank_5d.py` | yes (`_DATA_ROOT` only) | :51 | `flux_universe, omnifold_nn_core, unfold_2d_omnifold_unbinned, unfold_nd_omnifold_unbinned, xsec_nd` |
| `unified_throw_cov_5d.py` | **no** (was yes) | :42 | `omnifold_nn_core, unified_throw_cov, xsec_nd` |
| `unified_throw_cov.py` | yes (`_DATA_ROOT` only) | :61 | `compare_unified_throw, flux_universe, seed_offset_policy, unfold_2d_omnifold_unbinned, uq_math` |
| `combine_cov_nd.py` | no | none | — (imports `replica_manifest` from its own directory) |
| `analyze_universes_5d.py` | no | none | — (imports `fps_unfold_complete` from its own directory) |
| `mii_adopt_unified_5d_stamped.py` | no | :149, from `__file__` | `seed_offset_policy` |
| **`adopt_unified_5d.py`** | **yes** | **:38** | **NONE — the empty set** |

**M-1's central finding survives the build unchanged**, which is what B-2 rests on. The import sets
are identical to the contract's table. The only column that moved is the literal column, and it moved
for the authorized reason.

**M-4 — reproduces exactly, measured today, read-only:**
```
ssh saul.nersc.gov 'cd /pscratch/sd/j/josephrb/MINERvA-OmniFold && git rev-parse HEAD; …'
→ b2d7d4ca24707344cf12f99c0aa51381b81dd445 ; 721 lines ; 717 "??" + 4 " M"
```
Identical to the contract's measurement. The hazard is still latent, and still 717 untracked files
wide.

**M-5 — now FALSE by authorized construction.** All eight launchers are repaired (§2.3). This is the
change ruling 18 asked for.

**M-6 — now FALSE by authorized construction.** `checked` is read and published in the P-1 record and
echoed to stderr. The guard *can* now produce the positive evidence Joseph asked for; nothing on the
k=0 path asks it to.

**M-8 — 24 → 41** `def test_` in `test_mnv_guarded_run.py`, measured, not quoted.

**M-2 and M-3 — not re-measured.** M-2 needs a designated `MNV_CODE_ROOT`, which does not exist.
M-3's conclusion is corroborated by F-16: `verify_hash_bindings.py` is green and identical at base
and branch, so no digest that the repository pins moved.

---

## 4. Findings

**Finding 1 (real, blocks the branch as it stands) — `MANIFEST.tsv` is stale at `ae42ae8d`, and the
commit message says otherwise.**
```
cd <clean worktree at ae42ae8d> && python3 docs/orchestration/generate_manifest.py --check
→ exit 1
OUT OF DATE: docs/orchestration/MANIFEST.tsv; rows=424 ARCHIVAL=102 DEAD=1 LIVE=42 MACHINE=279 …
```
at base `8c156a37` the same command prints `OK` and exits 0. Reproduced in **three** clean trees at
`ae42ae8d`, including the builder's own worktree (`git status --porcelain | wc -l` = 0 in each), so
it is not a worktree artifact. The diff is three lines: the reference-source lists of the
`DECISION-…` and `REVIEW-CONTRACT-…` rows are **missing the three new test files**
(`tests/test_k0_launcher_two_roots.py`, `tests/test_n2_child_boundary.py`,
`tests/test_n3_rooted_import_repair.py`), and the manifest's own byte count is 89038 where the
generator computes 89232. The commit message states *"MANIFEST.tsv regenerated;
generate_manifest.py --check exits 0."* — that claim does not hold at the committed tree. The cause
looks like regenerating before the new test files landed: measure after the change, not before.

*Disposition, stated so the evidence is not lost:* this commit adds a new `LIVE` document and must
therefore run `generate_manifest.py`, which incidentally repairs those three rows **on this
verification branch**. **The defect stands at `ae42ae8d` on `build-k0-execution-integrity`**, which
is the tree under review, and it is reproducible there with the command above. It is not fixed by me
on the builder's branch and it should not be read as fixed there.

**Finding 2 — seven pre-existing test failures, not two, and I could not reproduce the "two".**
The reviewer's brief relayed a builder claim that **two** test failures are pre-existing at
`8c156a37`. `TMPDIR=/private/tmp python3 -m pytest tests -q` over `nd-unfolding/tests` gives:

| tree | result |
|---|---|
| branch `ae42ae8d` | **7 failed, 2077 passed, 4 skipped** in 132.45s |
| base `8c156a37` | **7 failed, 2043 passed, 4 skipped** in 126.17s |

The failing node-id sets are **identical** (`diff` of the sorted lists exits 0), and the failure
messages are identical too — I diffed the full traceback block of the one launcher-adjacent failure
(`PB2ProducingClosureResume::test_launcher_emits_exactly_the_six_producing_paths`) and it is
byte-identical across the two trees, so none of the seven changed cause:

```
tests/test_gate2_target_runtime.py::TargetOnlyDataLoader::test_exact_numpy_source_loads_without_tensorflow_package_init
tests/test_hash_bindings.py::test_every_longform_finding_is_indexed
tests/test_p4_resume_integration.py::PB2ProducingClosureResume::test_launcher_emits_exactly_the_six_producing_paths
tests/test_p4_sweep_snapshots.py::SweepSnapshots::test_pipeline_sweep_matches_its_snapshot
tests/test_p4_token_gate_scope_and_rev.py::Defect4b_ShellInvokedScriptsAreOnTheSurface::test_MUTATION_prefix_surface_OMITS_the_shell_invoked_scripts
tests/test_pet_fullevent_nominal_launcher.py::DriverConfigGate::test_config_gate_only_cli_no_train
tests/test_uq_remediation.py::LibraryResolverSurvivesSbatch::test_a_DECOY_library_in_the_spool_would_be_used_and_that_is_CORRECT
```

**The substantive claim is CONFIRMED — the branch introduces no new failure — but the count "two"
is not reproducible; it is seven.** The +34 passing tests on the branch (2077 − 2043) exactly match
17 new guard arms + 7 N-2 + 5 N-3 + 5 launcher arms. The last of the seven is a `TMPDIR` artifact
(`RESOLVED=/private/tmp/…` vs `RESOLVED=/tmp/…`) and is the DECOY test of §2.6.

**Finding 3 — the N-3 `_DATA_ROOT` assertion is largely vacuous.** §2.2. The property is true; the
control over it is not the control its docstring describes.

**Finding 4 — P-4 was not built and was not disclosed.** Amendment 3 C-5 lists three gaps honestly.
The per-entrypoint import-set identity ratchet (P-1's companion, F-7) is a fourth, and it is not in
that list.

**Finding 5 (scope reasoning: the builder is right, and the residual is smaller than it sounds) —
`2d-unfolding/unfold_2d_omnifold_unbinned.py:1679-1681`.** The site is real: `_OF_PY` is the
hardcoded root and it is inserted at position 0, and the module is imported by both
`unfold_nd_omnifold_unbinned.py` and `sweep_bank_5d.py`, which are on the k=0 path. Leaving it is
correct under ruling 18, which names six sites. **And it is not reachable on this path:** the insert
sits inside `main()` (lines 997–1997 by AST), so importing the module as a library does not execute
it, and `grep -rn 'u2d\.main\|unfold_2d_omnifold_unbinned\.main' nd-unfolding/ 2d-unfolding/` → 0
hits, exit 1. It is a latent fail-open site (it is one of the 52), not a live hole on legs 1–5. By
contrast the same shape inside `unfold_nd_omnifold_unbinned.py` at :971 **is** on the executed path
and **was** repaired, correctly.

**Finding 6 — the two Gate-5 launchers already show what a wired guard looks like.** The ratchet's
own `TheMitigationIsStillDeployed` asserts that
`nd-unfolding/pet/sbatch_gate5_data_only_{train,target}_array.sh` each invoke
`"$GUARD" --expect-root "$CODE_ROOT" --` **and** pass
`--pair "${GUARD}=nd-unfolding/mnv_guarded_run.py"`. Those tests are green on this branch. The
pattern correction 2 needs on the eight k=0 launchers is already written, tested and deployed
elsewhere in this repository — which is why the gap is a one-line-per-launcher gap and not a design
problem.

---

## 5. What I could not evaluate, and why

* **Anything requiring a production run** — F-1, F-2, F-3's stdout half, F-9, and F-17's
  submission-time half. No `sbatch` was run by the builder and none may be run by me. Rulings 17–19
  authorize no submission, so this is a property of where the work legitimately stopped, not a
  builder omission — except for **N-1 (F-9), which needs no submission**: it is a single guarded
  invocation with throwaway paths and it was simply not performed.
* **The A-2(f) source manifest and the `MNV_CODE_ROOT` constitution** — nothing to measure until a
  tree is designated at a named sha.
* **`bash` behaviour under `sbatch`** — `BASH_SOURCE`-in-spool remains ruling 14's business; neither
  the launcher test nor I can reach it without submitting.
* **Correction 2's exact wording** — I could not find it verbatim anywhere in the repository
  (`grep -rn 'every Python entrypoint' .` excluding `.git` and `.claude` → 0 hits;
  `grep -rn 'minimum OI-136'` → 0 hits). §0 answers it as quoted in my brief. If the canonical
  wording differs, §0 should be re-read against it.

## 6. What a FAIL here does and does not mean

It does not condemn the build. Seven of the eighteen criteria pass on measurement, the six repairs
are correct and genuinely tested in both directions, the two-root work is thorough and verified on
the target interpreter, the ratchet was moved honestly from printed output, and every gap the builder
disclosed is a gap I confirmed rather than a gap I had to find. The FAIL is that the contract's
positive arm — the half that turns a green run into evidence — is built and unconnected, and that
correction 2 therefore stands undischarged.

**Per Amendment 2's own terms, *"nothing is submitted until the reviewer records a clean PASS."* This
is not a clean PASS. The conditional authorization does not become operative.**
