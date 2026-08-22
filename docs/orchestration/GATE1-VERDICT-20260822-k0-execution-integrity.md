# GATE-1 VERDICT 2026-08-22 — pre-submission readiness for the k=0 M(ii) member

**GATE 1 DOES NOT PASS.**

Stated in the words §7.0.6 requires: **Gate 1 DOES NOT PASS.** Thirteen of the eighteen
pre-submission halves pass; **five fail** — F-1(a), F-2(a), F-7(a), F-8(a), F-17(a). No criterion is
recorded NOT-EVALUABLE. Under §F's no-partial-credit rule as scoped by §7.0.6, any single miss at a
gate is a FAIL of that gate.

**What this verdict blocks.** The seven jobs of logical legs 1–5 for k=0 are **not** authorized for
submission. Nothing here touches Gate 2, which is not graded and legitimately cannot be.

**What this verdict does not say.** It does not say the package is bad work. Four of the five FAILs
are *filing and enumeration* gaps sitting on top of mechanisms that are built, exercised and — where
I could reach them — correct. F-9, the criterion ruling 20 restated and the one this round turned
on, **passes on the record**, verified by me against the live artifacts on `saul` and not taken on
report. The gap that worries me most is F-8, because it is absent from the builder's own disclosure
list in the same way P-4 was absent in round 1.

---

## 0. Eligibility, scope, and what I graded against

**Eligibility (§7.0.10, restated by ruling 23).** I am neither the builder nor the lane that wrote
the §7.0 split. I authored no code in this package and no part of the rubric. §7.0.10 disqualifies
the round-1 reviewer from grading Gate 1 against a rubric that reviewer reshaped; that lane's
disclosure is honoured here by a separate lane taking the verdict.

**RUBRIC.** `main` @ `7165ea5c`, `docs/orchestration/REVIEW-CONTRACT-20260822-k0-execution-integrity.md`.
Verified this is the operative copy and not the branch's:

```
$ git show 7165ea5c:docs/orchestration/REVIEW-CONTRACT-...md | grep -c 'refused:script-outside-expect-root'   -> 7
$ git show origin/build-k0-execution-integrity:docs/orchestration/REVIEW-CONTRACT-...md | grep -c ... -> 0
```

The build branch carries a **superseded** contract: F-9 and F-12 were restated on `main` after the
branch was cut. A verdict graded against the branch's copy would be void.

**CODE.** `origin/build-k0-execution-integrity` @ `48170de9`, base `8c156a37`, 14 commits.
Graded in a clean detached worktree at `/Users/josephbailey/local-research/mnv-k0-builder`
(`git status --porcelain` → 0 lines), outside `.claude/worktrees/`.

**CLUSTER.** Read-only over `ssh saul.nersc.gov`. No Slurm job submitted, no `--allow` run, no
scientific artifact opened, moved or deleted, no `*combined_bkgaware.root` touched, nothing written
to `/pscratch`. Every cluster number below is a re-measurement I made, not a quotation of the
receipt.

**Local shell notes** carried out as instructed: `/usr/bin/grep` throughout (the shell's `grep` is a
ugrep wrapper); `TMPDIR=/private/tmp` on every suite; no `$?` read after a pipe; multi-file greps run
under `/bin/bash -c` because zsh does not word-split an unquoted variable and silently produced a
single 8-filename argument on my first attempt.

### 0.1 The digest claim, verified first, because everything downstream depends on it

The builder reports F-9 measured **at code root `de040d9b`** while the graded tip is `48170de9`. If
the executing bytes differ from the graded bytes the evidence is about a different tree.

```
$ for f in mnv_guarded_run.py mnv_source_manifest.py mnv_import_set_ratchet.py mii_adopt_unified_5d_stamped.py; do
    git show de040d9b:nd-unfolding/$f | shasum -a 256 ; git show 48170de9:nd-unfolding/$f | shasum -a 256 ; done
```

All four **byte-identical**. `mnv_guarded_run.py` = `bd2ccce19181b075091569fe4ee89b52e6eb0aa0e4e65c165fe2292e2234924f`
at both shas. Stronger, the whole diff `de040d9b..48170de9` is five files, of which **no launcher and
no entrypoint**: `MANIFEST.tsv`, `PLAN`, `RECEIPT`, `RUNBOOK`, `tests/test_p4_ratchet_fail_closed.py`.
Independently confirmed by the source manifest itself — the only path whose digest differs between
the constituted cluster tree and the graded tip is `nd-unfolding/tests/test_p4_ratchet_fail_closed.py`.

**The digest claim holds.** The cluster evidence is about the graded bytes.

### 0.2 The tree that would execute, measured live

```
$ ssh saul.nersc.gov 'cd /pscratch/sd/j/josephrb/k0r2/clean && git rev-parse HEAD && git status --porcelain | wc -l'
de040d9b0ccd594240b0a617298c533f2f249a65
0
$ ssh saul.nersc.gov 'cd .../clean && source setup_salloc_env.sh; python3 nd-unfolding/mnv_source_manifest.py \
    --repo .../clean --compare .../n1/srcman.json --require-clean --require-checkout \
    --require-no-nested-checkout --require-not-nested --require-readonly'
[srcman] .../clean: 773 tracked source files, listing sha256 afc572b0277b063a6d23a701ccbacd0ad516545e9fc0201baa14553940ca206b, HEAD de040d9b..., dirty 0
[srcman] SOURCE MANIFEST IDENTICAL (773 files, afc572b0...)
A2_CHECK_EXIT=0
```

All five A-2 fail-closed flags pass **live, today**, on the real tree, unpiped exit 0. Write
protection is still on: `nd-unfolding` is `dr-xr-x---`, `seed_offset_policy.py` is `-r--r-----`.

---

## 1. The Gate-1 column, criterion by criterion

| # | verdict |
|---|---|
| F-1(a) | **FAIL** — the A-2(f) digest that is *filed* is superseded, and two shas are named for the code root |
| F-2(a) | **FAIL** — two executing `.sh` files are covered by no `--pair`; count 2 is not zero |
| F-3(a) | PASS |
| F-4(a) | PASS |
| F-5(a) | PASS |
| F-6(a) | PASS, with a residual recorded |
| F-7(a) | **FAIL** — the §7.0.13 exclusion is not pinned with the mechanism |
| F-8(a) | **FAIL** — P-6's enumeration and P-5's blind-spot inventory do not exist |
| F-9 | PASS — verified on the live records, including the inversion |
| F-10 | PASS |
| F-11 | PASS |
| F-12 | PASS |
| F-13 | PASS |
| F-14 | PASS |
| F-15 | PASS — 50 and 7 at the graded sha |
| F-16 | PASS |
| F-17(a) | **FAIL** — declared open by the builder; §7.0.8 makes that a FAIL, not a park |
| F-18(a) | PASS on delivery of this document |

---

### F-1(a) — code root constituted at a named sha; A-2(a)–(g) measured and filed — **FAIL**

**What passes.** A-2(a)(b)(c)(d)(e)(f)(g) all hold on the constituted tree, measured live by me in
§0.2: HEAD `de040d9b`, porcelain **0**, both markers, no nested checkout, not nested, manifest
identical over 773 files, protection applied and still in force. (c)(d)(e)(g) are **executable
fail-closed checks**, not documentation, as ruling 22 requires — five flags on
`mnv_source_manifest.py`, invoked by all eight launchers before anything else. Both preflight tools
are in the manifest (`test_BOTH_preflight_tools_are_covered_by_the_source_manifest`, green).

**Why it fails.** F-1(a) requires the A-2(f) source-manifest digest to be **measured and filed**. The
digest filed in the committed package is not the digest of any tree in play:

| where | files | listing sha256 | HEAD |
|---|---|---|---|
| **filed** — `RECEIPT-…-k0-n1-and-guarded-arms.md` §4 | 771 | `4ab22f9326810f75…` | `a902b781` |
| constituted cluster tree, measured by me | 773 | `afc572b0277b063a…` | `de040d9b` |
| graded tip, measured by me | 773 | `4ad599f7e623111f…` | `48170de9` |

Three digests, and the one on the record is the oldest. F-1(b) turns on *"the manifest digest
identical at both ends"*, so a stale filed value is not cosmetic — it is the thing the far-end
comparison will be made against.

Compounding it, the receipt names **two different shas** for `MNV_CODE_ROOT` without reconciling
them: §0's table says `a902b781`, §2 and §7.1 say `de040d9b`. And no document in the package declares
which sha the Gate-1 submission pins. §7.0.11 is explicit that F-9 *"is gradable against the build
branch at the sha the Gate-1 submission declares"* — that declaration is missing.

**Not a reason to fail it, recorded so the fix is cheap.** The delta is one test file. Re-record the
manifest on the tree the submission will actually use, file the digest and the file count beside a
single declared sha, and this closes.

**On A-2(g) applied to `k0r2/clean` and not to a real submission tree** — the builder flags this and
asks for a ruling. My judgement: it is a **Gate-1 obligation**, and it is *discharged for
`k0r2/clean`*. F-1(a) asks for A-2 on the code root at the pinned sha, and I verified it there today.
It becomes an open Gate-1 item only if the submission declares a different tree — which is precisely
why the missing sha declaration above matters. It is not a Gate-2 obligation; F-1(b) is the
re-measurement *after the last leg*, a different thing.

### F-2(a) — both counts zero, plus the preflight ordering criterion — **FAIL**

**Count 1 — zero unguarded production `python3` invocations other than the enumerated preflight set:
SATISFIED.** Re-derived, and the instrument trap §7.0.13 warns about reproduced exactly:

```
$ /usr/bin/grep -c -- '--expect-root' <the eight>            -> 2 2 2 3 3 2 2 6  = 22
$ /usr/bin/grep -v '^[[:space:]]*#' <each> | grep -c -- '--expect-root'
  bootstrap 1, seedscan 1, sweep 1, detector 2, uthrow-block 2, uthrow-combine 1, uthrow-run 1, finalize 5 = 14
```

**14**, matching ruling 21's enumeration exactly, plus 16 preflight calls (two per launcher) = 30. A
line-by-line read of every `python3` occurrence in the eight launchers finds no other invocation.

**The ordering criterion: SATISFIED, and verified rather than arranged.** Three instruments, as
ruling 21 demands, and the third is dynamic:
`test_the_preflight_is_textually_BEFORE_every_guarded_science_invocation` (with a power arm asserting
there *are* science invocations to order against);
`test_no_launcher_defines_a_shell_function_that_could_hoist_a_later_line` (only `mnv_inv` is allowed,
and it runs nothing); and `test_EVERY_preflight_refusal_mode_leaves_ZERO_inventories`, which breaks
six preconditions one at a time and asserts **zero inventories exist** — a statement about what ran.
`test_the_preflight_block_is_BYTE_IDENTICAL_across_all_eight_except_its_pair_list` is what carries
the single-launcher dynamic arm to the other seven. All green. This is the strongest part of the
package and I want it recorded as such.

**Why it fails — count 2 is not zero.** F-2(a) requires *"the number of `.py` and `.sh` files that
will execute on the path, plus `mnv_guarded_run.py` itself, not covered by an A-3 `--pair`"* to be
**zero**. It is at least **2**:

```
$ /usr/bin/grep -vn '^[[:space:]]*#' <each launcher> | grep -E '(^|[^a-z])source '
  source "${CODE_ROOT}/setup_salloc_env.sh"      # all eight
  source "${CODE_ROOT}/lib/resume_guard.sh"      # all eight (finalize via _mr_rg="${_mr_lib}/../lib/resume_guard.sh")
$ /usr/bin/grep -o -- '--pair "[^"]*"' <each launcher>
  # setup_salloc_env.sh: absent from every pair set
  # lib/resume_guard.sh: absent from every pair set
```

Both are tracked (`git ls-files --error-unmatch` succeeds on both), both resolve under
`${MNV_CODE_ROOT}`, and both **execute** — they are `source`d, which is execution in the same shell.
Neither is bound by any `--pair` in any of the eight launchers. `lib_member_resume.sh`, the launcher
`.sh` itself, all entrypoints, the guard, the parity tool and the manifest tool **are** all bound; it
is exactly these two that are not.

This is not covered by the A-2(f) manifest in the sense A-3 means. The contract draws the distinction
itself, and the launcher's own comment repeats it: the manifest asks *"has any source byte moved since
the snapshot"*, the parity check asks *"is the file at this named path the committed one"*, against
git. A code root constituted from the wrong sha satisfies the first and fails the second. That is the
question A-3 exists to ask.

Two things make this worse rather than better, and both should be fixed together:

1. `RUNBOOK-20260822-b1-lift-preflight.md` §0b-0 states the parity call runs
   *"over the files it executes plus the guard, the parity checker and the manifest tool"*. It does
   not; two executed files are outside it. The document claims coverage the artifact does not have.
2. Both are sourced at launcher lines ~41–42, **before** the preflight runs at ~93/102. Adding a
   `--pair` for them is necessary but not sufficient — a `.sh` that has already executed cannot be
   retroactively bound. This does **not** violate the ordering criterion, which is scoped to science
   invocations, but it is a finding in ruling 21's own terms: a file executes from the code root
   before anything has checked that the code root is the approved one.

**Also recorded here, graded under F-7(a):** nothing in the suite would fail if a fifteenth unguarded
production invocation were added to a launcher. Count 1 is currently a property of the source text
that I verified by hand, with no test standing behind it.

### F-3(a) — zero `--allow` across the eight launchers and every guard invocation — **PASS**

```
$ /bin/bash -c '/usr/bin/grep -n -- "--allow" <the eight>'
sbatch_sweep_bank_5d_run_bkgaware_gpu.sh:11:# purity down-weight (per-universe background). FAIL-CLOSED: no --allow-cv-background,
```

One hit, in a comment, and it is `--allow-cv-background` — a different flag on a different subject,
not the guard's `--allow`. Zero guard `--allow` on any command line. Backed by
`test_no_allow_FLAG_appears_on_any_command_line_in_any_launcher`, which carries a power arm
(`assertTrue(pat.search('python3 x.py --allow /tmp/tree -- y.py'))`) so the pattern is shown able to
match its own negation. Every guard invocation I read passes `--expect-root` and `--inventory` and no
`--allow`; the live records on the cluster carry `allow: []` on all four arms. The criterion's
"publish the command" is discharged by the command above.

`--expect-root` naming the canonical checkout on the O-1/U′ paired arm is **not** an `--allow` and
§7.0.11 says a grader must not refuse it. I do not.

### F-4(a) — the denominator is fixed on the bench and is > 0 — **PASS**

Guarded production invocations **14** == production Python invocations **30** less the enumerated
preflight set **16**, and 14 > 0. Plus the pinned-writer child, which `build_child_argv` wraps
(`test_the_guarded_argv_is_the_documented_template_and_forwards_the_child_verbatim`,
`test_it_REFUSES_when_the_inventory_is_missing`, `test_there_is_no_bypass_FLAG_declared_anywhere`).
The anti-vacuity trap §7.0.8 warns about — `0 == 0` reading as a pass — does not arise: the
denominator is 14, re-derived above from the comment-filtered count.

### F-5(a) — generator and comparator exist, each with a firing and a silent test — **PASS**

Generator `nd-unfolding/mnv_source_manifest.py`; comparator `nd-unfolding/mnv_import_set_ratchet.py`.
Both directions pinned:

- *fires on mismatch* — `test_a_sha256_that_disagrees_with_the_source_manifest_is_refused`,
  `test_an_origin_absent_from_the_source_manifest_is_refused`, and the launcher-level dynamic arms
  "A-2(f) manifest describes a DIFFERENT tree" / "foreign schema" / "not valid JSON", each of which
  leaves zero inventories;
- *silent on a match* — `test_a_well_formed_record_against_its_own_pin_is_GREEN`, and the eight
  launchers running green under stubs.

`test_WITHOUT_a_source_manifest_the_sha256_half_is_OFF_and_says_so` is the right shape too: a
degraded instrument that announces its own degradation rather than passing quietly. I confirmed the
manifest comparator on the real cluster tree in §0.2: `SOURCE MANIFEST IDENTICAL`, exit 0.

### F-6(a) — the child argv emits the guard and an inventory; a flagged `repo_origin_count: 0` — **PASS**

`build_child_argv` emits `[python, mnv_guarded_run.py, --expect-root, …, --inventory, …, --, adopt_unified_5d.py, …]`
and `main()` refuses both missing operands rather than falling back
(`test_main_REFUSES_to_run_the_child_unguarded_in_BOTH_missing_operands`). The explicitly flagged
empty record is asserted at `test_mnv_guarded_run.py:434-445`
(`test_an_entrypoint_with_NO_repository_import_is_EXPLICITLY_EMPTY_not_silent`: `assertIn` the key,
then `assertEqual(…, 0)` — present, not absent, which is P-3's whole point), and
`test_the_two_kinds_of_ZERO_are_distinguishable` separates it from the containment zero.

Confirmed against the **real** record on the cluster rather than only a fixture — the child arm of
the guarded production run:

```
script                 /pscratch/sd/j/josephrb/k0r2/clean/nd-unfolding/adopt_unified_5d.py
guard_installed        True     checked 213
repo_origin_count      0        repo_origin_inventory_is_empty True
verdict                EMPTY-REPOSITORY-ORIGIN-SET -- THE GUARD REFUSED NOTHING BECAUSE IT SAW NOTHING
```

`checked = 213` with `repo_origin_count = 0` is exactly the state P-3 exists to make distinguishable
from a guard that never ran, and M-1's AST prediction for `adopt_unified_5d.py` is now measured at
runtime rather than inferred.

**Residual, recorded not waived.** No single test binds the flagged-empty record to the
`build_child_argv` argv *shape*: the argv shape is asserted in `test_remedy_a_adopt_wrapper` with
`--inventory /dev/null` (so no record is read), and the flagged-empty record is asserted in
`test_mnv_guarded_run` on a synthetic entrypoint. The two halves are joined only by the cluster
record above. That record is real evidence and I count it, but it is a one-off artifact, not a test.

### F-7(a) — the P-4 mechanism, fail-closed, with the §7.0.13 exclusion pinned — **FAIL**

**What passes, and it is nearly all of it.** `nd-unfolding/mnv_import_set_ratchet.py` with
`nd-unfolding/tests/test_p4_ratchet_fail_closed.py` — **30 arms, all green** at the graded sha:

- identity **in both directions** — `test_a_set_that_GREW_is_refused`,
  `test_a_set_that_SHRANK_is_refused_TOO_and_that_is_the_whole_point`;
- exact match green — `test_a_well_formed_record_against_its_own_pin_is_GREEN`;
- **absent or undeclared pin fails closed** — `test_an_UNDECLARED_entrypoint_is_refused_rather_than_absorbed`,
  `test_a_PINNED_entrypoint_with_no_inventory_is_refused`, `test_an_UNDECLARED_empty_import_set_is_refused`,
  `test_write_pins_REFUSES_a_declared_empty_without_its_disclosure`;
- CANNOT-LOOK is never a pass — an empty or missing inventory directory is **exit 2**, a malformed
  line **raises** rather than being skipped, a foreign schema is refused;
- a refusal record sitting in a production set is refused, on **both** `outcome` and `verdict`,
  because those two fields disagreed once already.

**"Production pins NOT manufactured": confirmed.** No pins file is committed on the branch. The two
pins on scratch came from a two-process throwaway arm and the receipt says so in those words.

**Why it fails.** §7.0.5's F-7 row and §7.0.15 both require *"the §7.0.13 exclusion pinned with
it… so that the exclusion cannot widen unnoticed."* It is not pinned anywhere:

```
$ /usr/bin/grep -n 'exclu\|preflight\|EXCLU\|allowlist\|SKIP' nd-unfolding/mnv_import_set_ratchet.py \
      nd-unfolding/tests/test_p4_ratchet_fail_closed.py
(no output)
```

The pins schema (`mnv_import_set_pins/1`) has `entrypoints{modules, declared_empty, disclosure}` and
nothing else — no declared exclusion set. The 16 preflight call sites are excluded **implicitly**, by
producing no inventory record at all, rather than **declaredly**. Ruling 21's stated reason for
pinning is that *"standing exceptions weaken P-4"*, and §7.0.13's first requirement — *"a test must
fail when a production invocation appears that is neither guarded nor on the list"* — has no
implementation. I confirmed the consequence directly: **no test in the suite fails if a fifteenth
unguarded production `python3` line is added to a launcher.** The exclusion can widen silently, which
is the exact failure mode the requirement names.

### F-8(a) — P-6's enumeration re-run and published; P-5's blind-spot inventory produced — **FAIL**

Neither artifact exists.

```
$ /usr/bin/grep -c 'P-5\|P-6\|namespace package\|blind' \
    docs/orchestration/{RECEIPT-20260822-k0-n1-and-guarded-arms,PLAN-20260822-oneMember-mii-staged,RUNBOOK-20260822-b1-lift-preflight,CATALOG}.md
RECEIPT 1   PLAN 0   RUNBOOK 0   CATALOG 0
```

The single RECEIPT hit is line 265, *"Both instruments … are blind by construction"*, about
`__pycache__` — a different subject.

- **P-6 is not discharged.** The contract requires the entrypoint-set search
  (`grep -nE 'python[0-9]*\s|\.py'` over the eight launchers, comment-filtered) re-run **on
  `MNV_CODE_ROOT` at the pinned sha**, published **with its command and its full output**, and any
  difference reconciled. Nothing in the package publishes it. I ran the search myself for F-2(a) and
  F-4(a) and it reconciles — but *me running it is not the builder discharging P-6*, and P-6's own
  text is that a null result from that grep is evidence about the grep. The published command and
  full output are the artifact, and they are absent.
- **P-5 is not discharged.** The contract requires a blind-spot inventory *"including the subprocess
  enumeration with each child either wrapped or recorded as uncovered"* — concretely
  `grep -n "subprocess\.\(run\|call\|Popen\)\|os\.system\|os\.exec"` over the entrypoint set. No such
  enumeration exists. Partial credit is real and I record it: `mnv_import_set_ratchet.py`'s docstring
  names all four blind spots (namespace packages, pre-`install()` `sys.modules`, unwrapped
  subprocesses, the `.sh` route), and `test_mnv_guarded_run.TheSubprocessBoundaryIsNotCovered` proves
  the subprocess hole in both directions with a docstring test so callers can read it. But the
  enumeration over the entrypoint set — the list of every child, each marked wrapped or uncovered —
  was never produced.

**F-8 is absent from the builder's own C-6 gap list.** That list is otherwise written clause by clause
against the contract, and its stated purpose was to fix round 1's failure mode. F-8 is the one
criterion it skips entirely. See §3.

### F-9 — N-1 restated: the six-row table of §7.0.11 — **PASS**

Graded against the build branch, as §7.0.11 requires, and settled on the **live inventory record** at
`/pscratch/sd/j/josephrb/k0r2/n1/inv/armN1.jsonl`, which I read directly rather than quoting the
receipt:

```
label                 'N-1 REFUSED ARM: real canonical-checkout wrapper, --expect-root=clean tree.
                       B-4 refuses before imports begin.'
expect_root           /pscratch/sd/j/josephrb/k0r2/clean
script                /pscratch/.../MINERvA-OmniFold/nd-unfolding/mii_adopt_unified_5d_stamped.py
script_checkout_root  /pscratch/sd/j/josephrb/MINERvA-OmniFold
outcome               refused:script-outside-expect-root
refusal_site          b4-script-containment
verdict               REFUSED -- THE SCRIPT ITSELF LIES IN A CHECKOUT THAT IS NOT --expect-root;
                      nothing was imported because nothing was run
guard_installed       False
checked               0
checked_provenance    not-measured-no-guard-was-installed
repo_origin_count     0        allow []        violation None
```

| clause | verdict | how I settled it |
|---|---|---|
| 9.1 exit 3 **through B-4** | PASS, with a residual | see below |
| 9.2 `outcome` exactly `refused:script-outside-expect-root`, never empty/green | PASS | read off the record above. The verdict string is `VERDICT_REFUSED_SCRIPT`, not the old `EMPTY-REPOSITORY-ORIGIN-SET` — the defect §7.0.11 flagged as unsatisfiable is genuinely fixed |
| 9.3 names the script, canonical root, expected clean root | PASS | all three on the record; and all three in the banner, from `armN1.log` |
| 9.4 `checked == 0` **and** `guard_installed == false`, together | PASS | both on the record, plus `checked_provenance = not-measured-no-guard-was-installed` |
| 9.5 O-1…O-4, no child marker, no output | PASS | see below |
| 9.6 `seed_offset_policy` neither required nor expected | PASS | **not graded as a string test.** See below |

**9.4 and the inversion (§7.0.8's carve-out).** I applied the carve-out, not the general rule.
`checked == 0` is the **required** value here and I did not fail F-9 on it. I also did not accept the
bare zero: §7.0.11 is right that `write_inventory` emits `guard.checked if guard is not None else 0`,
making it a default. The record carries the full triple, and the builder's two added fields —
`checked_provenance` and `refusal_site` — do exactly what is claimed for them. I checked they are not
decoration: `refusal_site` distinguishes `b4-script-containment` from `import-tree-violation`, both of
which return the same exit 3, and `test_the_refusal_SITE_is_a_field_because_exit_3_cannot_carry_it`
and `test_the_two_kinds_of_ZERO_are_distinguishable` pin both.

**9.6.** I did **not** grep the arm for `seed_offset_policy`. §7.0.11 is explicit that the string test
is deleted because it always passes and is a proxy that fails in both directions. I graded the
positive falsifier instead: `checked > 0`, or `guard_installed == true`, or a non-null `violation`
naming a resolved import. None is present. (For completeness, and as an observation carrying no
weight: the token appears 0 times in `armN1.log`.)

**9.5, O-1 through O-4**, each measured on the cluster:

- **O-1** — `[remedyA] running the PINNED writer as a subprocess:` occurs **0** times in `armN1.log`
  and **1** time in `armUp.log`. One binary, one marker, two outcomes.
- **O-2** — `witness_N1/` is the empty set after the arm (`ls -la` shows `.` and `..` only) and the
  `--out` path does not exist. `[adopt5d]` count 0.
- **O-3** — `armN1.log` is one merged stream; the banner is its only content, so the interleaving is
  not a stdout-vs-stderr comparison.
- **O-4** — the receipt states `RC=$?` was captured unpiped before any `grep`/`wc`. **Residual:** the
  inventory schema has **no `exit` field**, so no durable artifact carries the exit status. I could
  not re-run the arm (read-only on the cluster by instruction). I settled 9.1 by entailment instead:
  `mnv_guarded_run.py:524` returns `VIOLATION_EXIT` unconditionally on the containment path,
  `test_a_script_in_another_checkout_is_refused_3` pins it, and `refusal_site = b4-script-containment`
  on the record identifies *which* protection fired. That is sound, but it is the one clause of F-9
  resting partly on the builder's prose. **Recommendation, not a FAIL: add `exit` to the inventory
  schema.**

**F-9's clauses all hold.** The builder's central claim reproduces.

### F-10 — N-2 as replaced by ruling 19 — **PASS**

`nd-unfolding/tests/test_n2_child_boundary.py`, 7 arms, green
(`TMPDIR=/private/tmp python3 -m unittest test_n2_child_boundary` → `Ran 7 tests … OK`). It matches
ruling 19's replacement rather than the contract's rejected N-2: a purpose-built fixture writer
**inside** a disposable expected checkout (so it passes containment and the *resolution* guard is
what fires), importing a repository-local module from a second checkout, invoked through the real
`build_child_argv`. Exit 3 through the child wrapper (`test_B`). O-1/O-2/O-3 in `test_C`, and the
ordering is asserted properly — the writer must have `STARTED` (or the arm measures a startup failure
instead of an import refusal), the banner precedes any further writer output, the witness directory is
empty, the output does not exist. O-4 is the subprocess return code, unpiped. `test_E` asserts no
`--allow` on any arm. `test_F` asserts ruling 19's hard limit: the pinned science writer is neither
copied nor executed, and no file named like it exists anywhere in the fixture checkout.

### F-11 — N-3 for each of the six B-1 files, both directions — **PASS**

`test_n3_rooted_import_repair.py`, 8 arms, green. `REPAIRED` names all six and only six:
`bootstrap_nd.py`, `seedscan_split.py`, `unfold_nd_omnifold_unbinned.py`, `sweep_bank_5d.py`,
`unified_throw_cov_5d.py`, `unified_throw_cov.py`. Both directions, per file:
`test_PRE_repair_the_entrypoint_imports_the_OTHER_trees_copy`,
`test_PRE_repair_PYTHONPATH_CANNOT_OUTRANK_POSITION_ZERO`,
`test_POST_repair_the_same_fixture_resolves_to_ITS_OWN_tree`. The repair form is checked too —
`test_the_repaired_prologues_derive_from___file___with_no_absolute_fallback` — which is B-1's actual
requirement and not merely "it works now". `TheOffenderCheckerHasPower` gives the detector a firing
arm, a silent arm, and a check that the loop shape really is what four of the six files use.

### F-12 — the hijack/non-vacuity anchors — **PASS**

*N-2 and N-3, unchanged, on `__file__`:* `test_A_UNGUARDED_the_fixture_really_loads_the_SECOND_checkouts_module`
asserts the loaded module's `__file__`; N-3's pre-repair arms do the same. Both green.

*N-1 restated (§7.0.12), all three clauses:*

- **(i) the fixture really is misplaced** — from the refused arm's own record,
  `script_checkout_root = /pscratch/sd/j/josephrb/MINERvA-OmniFold` ≠
  `expect_root = /pscratch/sd/j/josephrb/k0r2/clean`. Asserted on the resolved path the guard
  computed, not on the command line as typed.
- **(ii) the arm can succeed** — the O-1 paired arm reaches `[remedyA]`, measured by me:
  `grep -c '\[remedyA\] running the PINNED writer' armUp.log` → **1**. Its record shows
  `expect_root = script_checkout_root = the canonical checkout`, `guard_installed true`, `checked 9`,
  and an outcome from *downstream* of the marker (`child-systemexit: '[FAIL] the pinned writer exited
  1…'`), which is emitted after `subprocess.call`. So the refusal was containment, not breakage. This
  is the clause that would have caught the original F-9 collision, and it is genuinely armed.
- **(iii) U/U′ retains and NAMES `seed_offset_policy`** — from `armUp.jsonl`:
  `repo_origins: [('seed_offset_policy', '/pscratch/.../MINERvA-OmniFold/nd-unfolding/seed_offset_policy.py')]`.
  The counterfactual origin is on the record and it is the canonical checkout's copy.

The three arms are separated **by the artifact, not by the reader**, as §7.0.11 requires: each has its
own inventory path, its own capture file, and a `--label` naming which arm produced it. I verified the
labels are present and correct on both records. `expect_root` differs between them, which is the arm's
identity. Nothing conflates U′'s naming of the token with the refused arm.

### F-13 — B-4's script-containment refusal, covered in both directions — **PASS**

`test_mnv_guarded_run.ScriptContainment`, all green:
`test_a_script_in_another_checkout_is_refused_3` (fires),
`test_the_SAME_script_inside_expect_root_is_NOT_refused` (**silent on good** — the direction a filter
usually loses), `test_allow_does_NOT_launder_a_script_from_another_checkout`,
`test_a_script_outside_EVERY_checkout_is_not_refused_and_is_recorded_as_such`,
`test_the_refusal_happens_before_the_script_produces_anything`, and
`test_the_import_half_of_the_guard_has_nothing_to_fire_on_here` — which is the arm that documents
*why* B-4 had to exist at all. No bypass flag: `test_there_is_no_bypass_FLAG_declared_anywhere`.
Ruling 20's *"No B-4 bypass flag or production exception is authorized"* is honoured.

`EveryRefusalSiteHasAControlThatNamesItsOutcome` deserves separate mention: it enumerates every
`refused:` / `cannot-check:` / `child-` outcome string **from the source** and requires each to be
named by a control, with a power arm so an empty enumeration cannot pass forever. That is §7.0.16(e)'s
standing rule made executable, and it is the right response to a shape that has now recurred twice.

### F-14 — every §6 row discharged in the same commit as the repair — **PASS**

All six rows moved in `ae42ae8d`, the same commit as the six B-1 repairs
(`git log --oneline 8c156a37..48170de9 -- <the ratchet test> <the probe>` → `ae42ae8d` only):

- ratchet `FAILOPEN_COUNT` 58 → **52**, `FAILOPEN_SHA256` → `40bd83ca…`, with the source comment
  recording *"58 → 52 … SIX SITES REPAIRED IN ONE AUTHORIZED STEP, named as the rule requires"* and
  the values taken from the test's own printed output, not by hand. Ruling 18's *"new ratchet values
  must come from the probe/test output"* is honoured.
- `POSITIVE_CONTROLS` replaced: `unfold_nd_omnifold_unbinned.py` retired,
  `3d-unfolding/unfold_3d_omnifold_unbinned.py` added, **chosen from the probe's own printed
  fail-open list** and justified on classifier shape (it is the only remaining member reproducing the
  retired control's derived-name branch, so that branch would otherwise have no control and could
  under-count silently). `adopt_unified_5d.py` survives, exactly as §6 predicts.
- the `--pair "${GUARD}=nd-unfolding/mnv_guarded_run.py"` assertion is present at
  `test_oi136_failopen_inventory_ratchet.py:192`.
- `test_mnv_guarded_run.py` carries all four new arms §6 names.
- `verify_hash_bindings.py` re-run after the edits — see F-16.
- RUNBOOK and PLAN §C rewritten on `MNV_CODE_ROOT`/`MNV_DATA_ROOT` (18 and 7 occurrences); no
  `cd /pscratch/sd/j/josephrb/MINERvA-OmniFold` survives as a working-directory instruction.

**§7.0.7's addition 1**, measured in the clean worktree at the graded sha:

```
$ TMPDIR=/private/tmp python3 docs/orchestration/generate_manifest.py --check ; echo EXIT=$?
OK: docs/orchestration/MANIFEST.tsv; rows=425 ARCHIVAL=102 DEAD=1 LIVE=43 MACHINE=279 overrides=64 defaults=361
EXIT=0
```

### F-15 — the two named suites green, counts as measured at the graded sha, explicit TMPDIR — **PASS**

```
$ cd nd-unfolding/tests
$ TMPDIR=/private/tmp python3 -m unittest test_mnv_guarded_run              -> Ran 50 tests   OK
$ TMPDIR=/private/tmp python3 -m unittest test_oi136_failopen_inventory_ratchet -> Ran 7 tests   OK
```

**50 and 7, measured at `48170de9`.** Per §7.0.7 addition 2 these are bound to this sha and must not
be carried forward; the suite has now moved 21 → 24 → 41 → 50. Note the invocation: the module form
run from inside `tests/` is required, because `tests/` has no `__init__.py` and both the dotted form
and the path form fail to import.

The builder's package quotes **no** test counts anywhere, which is why this criterion's count is
recorded here rather than cited.

### F-16 — `verify_hash_bindings.py` exits 0 with `ALL BINDINGS INTACT` after all edits — **PASS**

```
$ TMPDIR=/private/tmp python3 docs/orchestration/verify_hash_bindings.py ; echo EXIT=$?
… 132 OK … ALL BINDINGS INTACT
EXIT=0
```

Run unpiped and as a **postcondition**, in a clean detached worktree at `48170de9`.

### F-17(a) — M-1…M-6 re-measured at the pinned sha and on the canonical checkout — **FAIL**

Not performed, and the builder says so twice in the builder's own words:
`PLAN` C-6 — *"F-17 freshness is open. M-1 through M-6 have not been re-measured on `MNV_CODE_ROOT` at
the pinned sha and on the canonical checkout as it stands."* — and `RECEIPT` §6.

F-17(a) sits in the **pre-submission** column. §7.0.8 is unambiguous: *"A NOT-EVALUABLE in the
PRE-SUBMISSION column is a FAIL of Gate 1. There is nothing a pre-submission half can legitimately be
waiting on."* An open pre-submission half is a fortiori a FAIL. I record it as such and did not spend
effort rediscovering it.

Two fragments exist and I extend them by one: M-1's empty import set for `adopt_unified_5d.py` is now
confirmed at runtime (`checked 213`, `repo_origin_count 0`); the canonical checkout's 721 dirty
entries are the most perishable claim in the package; and M-4's "identical digests" claim is the other
one that must be re-taken. M-2 — the 717-untracked-file inventory claim — is the one §H.1 says the
authorized work can itself falsify.

### F-18(a) — a fresh non-builder records the pre-submission verdict clause by clause — **PASS**

This document, clause by clause, with the command for each. It is not a summary attesting "all
controls passed"; §7.0.10's three eligibility rules are stated and met in §0.

---

## 2. Builder claims I could not reproduce, or reproduced differently

Recorded because a claim I could not check is not a claim I can count.

1. **"16 unique failing node-ids across 7 modules, byte-identical to the `8c156a37` baseline."**
   The *substance* holds; the *number* does not. Measured on both trees with the same command:

   ```
   $ cd <tree>/nd-unfolding/tests && TMPDIR=/private/tmp python3 -m unittest discover -s . -p 'test_*.py' -t .
   8c156a37 : Ran 1580 tests   FAILED (failures=5, errors=2, skipped=4)
   48170de9 : Ran 1705 tests   FAILED (failures=5, errors=2, skipped=4)
   $ diff <(sorted FAIL/ERROR lines, base) <(sorted FAIL/ERROR lines, build)   -> no difference
   ```

   **7** unique failing node-ids, not 16, across **7** modules (`test_gate2_target_runtime`,
   `test_p3f_pet_fullevent_launcher`, `test_uq_remediation`, `test_pet_fullevent_nominal_launcher`,
   `test_p4_resume_integration`, `test_p4_token_gate_scope_and_rev`, `test_p4_sweep_snapshots`). The
   module count matches; the node-id count does not, and I cannot tell from here which runner or
   discovery root produced 16. **The load-bearing half is confirmed: the failing set is identical
   before and after, so the package introduces no regression, and it adds +125 passing tests.** Given
   the builder's own note that its first sweep reported 32 by double-running one file, this count has
   now been wrong twice in two directions; quote 7 at `8c156a37`, or re-derive.

2. **`RECEIPT` §4: "[p4] P-2, P-3 and P-4 HOLD for every inventory record read. rc=0".**
   Does not reproduce at the graded sha. Running the graded ratchet over the same records:

   ```
   $ python3 mnv_import_set_ratchet.py --inventory-dir <the real invP records> --pins <pins> --source-manifest <srcman>
   [p4] 2 VIOLATION(S):  … no `checked_provenance`. … this record predates the field that says which.
   VERIFY EXIT=3
   ```

   **This is the mechanism working, not failing** — the records in `k0r2/n1/invP/` were written at
   12:53 by a pre-`de040d9b` guard and carry no `checked_provenance`, and the ratchet correctly
   refuses them. But it means the receipt's §3 and §4 evidence is **at a superseded sha**, and its
   quoted `rc=0` is not reproducible against the bytes being graded. The F-9 and U′ arms *were* re-run
   at 12:58 with the `de040d9b` guard (they carry `label`, `refusal_site` and `checked_provenance`);
   §3 and §4 were not.

3. **`k0r2/n1/pins.json` contradicts the receipt.** The on-disk pins record
   `mii_adopt_unified_5d_stamped.py: {"modules": []}` while the receipt quotes
   `1 module(s) ['seed_offset_policy']`. I re-derived from the same two records with the graded
   ratchet and **the receipt's output is what the graded mechanism produces**
   (`nd-unfolding/mii_adopt_unified_5d_stamped.py: 1 module(s) ['seed_offset_policy']`), so the
   scratch file is a stale artifact of an earlier ratchet, not a defect in the graded one. It matters
   only because someone may read it. These are not the production pins and must not become them.

4. **N-1's exit status.** No durable artifact carries it (see F-9, O-4). Read-only access meant I
   could not re-run the arm. Settled by entailment; recorded as a residual.

5. **Nothing under `sbatch`.** Confirmed and unchanged: `MNV_LAUNCHER_DIR`, `BASH_SOURCE`-under-spool
   and the Slurm resolver are untested, exactly as ruling 14 anticipates. Both local harnesses
   preserve `BASH_SOURCE`, so only a real submission can test it — which is the rehearsal's job, not
   Gate 1's.

---

## 3. The builder's five self-disclosed defects, and whether the disclosure is complete

**All five fixes are real. I verified each one rather than reading the claim.**

| disclosed defect | fix | verified how |
|---|---|---|
| the shipped `chmod` remedy string was wrong (`dirname` emits newline-separated into `sort -z`, so the directory pass silently did nothing) | replaced by `--apply-readonly` on the tool, chmod-ing exactly the set `--require-readonly` checks | the flag exists; the runbook carries "do not hand-roll the chmod" and the reason; protection is live on the real tree today |
| `__pycache__` was outside the protected set — a guarded arm wrote a `.pyc` into a `drwxrwx---` directory and `git status` stayed clean because it is gitignored | every directory under the root is protected; non-tracked writable files refused separately | `ls -ld .../clean/nd-unfolding` → `dr-xr-x---`; A-2 re-check exit 0 today |
| `checked = 0` was a **default** on the containment path | `checked_provenance` and `refusal_site`, both written unconditionally | both present on the live `armN1` record with the right values; pinned by `test_the_two_kinds_of_ZERO_are_distinguishable` and `test_the_refusal_SITE_is_a_field_because_exit_3_cannot_carry_it` |
| a B-4 refusal recorded itself as `EMPTY-REPOSITORY-ORIGIN-SET — THE GUARD REFUSED NOTHING BECAUSE IT SAW NOTHING`, both clauses false | third verdict constant `VERDICT_REFUSED_SCRIPT`; a refusal outranks emptiness | the live record carries the correct string; `VERDICT_EMPTY` remains reachable (the child arm still has it, correctly), so F-6 was not broken by the fix — this was the direction that mattered and it is clean |
| the builder's own A-2(f) mutation arm was **inert** and passed vacuously (renaming `file_count` changes nothing `compare()` reads) | recorded in the test source rather than quietly replaced; three real mutation arms added | read at `test_k0_launcher_two_roots.py`, and the three arms are in the green dynamic sweep |

Two of the five were found only by running against the real cluster tree — `__pycache__` in
particular could not have been found locally. That is the right instinct and it is worth saying.

**The disclosure is NOT complete, and completeness is gradeable.** Round 1's failure was an
undisclosed gap (P-4), and the builder's stated fix was to write C-5/C-6 against the contract's clause
numbers instead of against memory. C-6 is genuinely better — it is thorough on F-9, A-2, ordering,
P-4, the 14/30 boundary, `sbatch` and the `2d-unfolding` scope question. But four things are missing
from it, and three of them are Gate-1 FAILs:

1. **F-8 is not mentioned at all** — P-5 and P-6 appear nowhere in the package. This is the same shape
   as round 1's P-4: a clause that was never a *decision*, so walking the decisions does not surface
   it. Writing against clause numbers was the right fix; it was applied to §7.0's numbered rulings but
   not to the full §F list.
2. **The two unpaired executing `.sh` files** are not mentioned, and the RUNBOOK positively overstates
   the coverage.
3. **The §7.0.13 exclusion-pinning requirement** is not mentioned. C-6 discloses the 14/30 boundary as
   a scope question — which ruling 21 then accepted — but the ruling's *first* requirement, that the
   excluded set be enumerated and pinned so it cannot widen, is not addressed.
4. **The staleness of §3/§4 and of the filed A-2(f) digest** is not mentioned.

---

## 4. Known-open items, dispositions

Recorded so the next lane does not rediscover them, and so that "known" is not read as "passing".

| item | disposition |
|---|---|
| F-17 freshness | **FAIL of Gate 1** (§7.0.8). Not parked. |
| production P-4 pins | correctly **Gate 2** (ruling 22, §7.0.15). Not manufactured — verified. The mechanism is Gate-1 and fails for a different reason (F-7(a)). |
| nothing under `sbatch` | correctly outside Gate 1; ruling 14's business. |
| the two adopt invocations unreachable while the pause branch stands (ruling 13) | accepted. Their guarding is verified statically and by `test_n2_child_boundary`, never by running the launcher, and the test file says so in those words. |
| the 14-of-30 guarding boundary | **ACCEPTED** by ruling 21 and correctly built as 14. Not a FAIL. What fails is the missing *pinned enumeration* of the 16 exclusions. |
| A-2(g) on `k0r2/clean` rather than a real submission tree | **Gate-1** obligation, **discharged for that tree** (verified live). It reopens only if the submission declares a different code root — which no document currently declares, and that is part of F-1(a). |

---

## 5. What would close Gate 1

Not a design; the shortest honest list, so the next round is not a guess.

1. **F-2(a)** — add `--pair` entries for `setup_salloc_env.sh` and `lib/resume_guard.sh` in all eight
   launchers, and correct the RUNBOOK §0b-0 sentence. Then decide whether a file sourced *before* the
   preflight can be bound at all, and record the answer either way.
2. **F-7(a)** — declare the 16 preflight call sites in the pins artifact and add a test that fails
   when a production `python3` invocation appears that is neither guarded nor on that list.
3. **F-8(a)** — publish P-6's search with its command and full output, re-run on the code root at the
   declared sha and reconciled; produce P-5's blind-spot inventory including the subprocess
   enumeration, each child marked wrapped or uncovered.
4. **F-1(a)** — declare one sha for the Gate-1 submission, constitute the code root at it, and file
   that tree's A-2(f) file count and listing digest.
5. **F-17(a)** — re-measure M-1 through M-6 on the code root at the declared sha and on the canonical
   checkout, and report every difference from the contract as a finding.

Items 1–4 are bench work of a few hours and none of them requires the cluster except for a
re-measurement. Item 5 requires the cluster and no run.

---

## 6. Confidence

**High** on the five FAILs. Each rests on a measurement I made and can be falsified by re-running the
command beside it: two absent `--pair` strings, a zero-hit grep for the exclusion, a zero-hit grep for
P-5/P-6, three disagreeing manifest digests, and the builder's own written statement that F-17 is
open. None turns on judgement about intent.

**High** on F-9, F-10, F-11, F-12, F-13, F-15, F-16 — all settled on live artifacts or green suites I
ran myself at the graded sha.

**Moderate** on F-3(a), F-4(a) and F-6(a). F-3(a) and F-4(a) rest on a comment-filtered grep and a
hand read of every `python3` line in eight files; both reproduce ruling 21's independent count of 14,
which is real corroboration, but there is no test standing behind either and a fifteenth invocation
would not be caught. F-6(a) I passed on the combination of two tests plus one cluster record rather
than on a single binding test, and I have recorded that residual.

**The one thing I want flagged rather than buried:** F-9's exit status has no durable artifact. Every
other clause of the criterion I read off a file on `pscratch`; `rc=3` I took from the builder's prose
plus the code path. It is very likely correct — `mnv_guarded_run.py:524` has no other branch — but it
is the single place in this verdict where I am relying on a report, and the contract's own §7.0.16(e)
says an exit-3 control must assert the discriminator rather than the status. Adding `exit` to the
inventory schema would remove the residual entirely.

I would not sign a PASS on this package today, and the reason is not F-9 — which passes — but F-8:
an entire criterion with no artifact and no mention in the disclosure that was specifically rewritten
to catch that. **Gate 1 DOES NOT PASS.**

---

**CITABLE FOR:** the Gate-1 (pre-submission) verdict against
`REVIEW-CONTRACT-20260822-k0-execution-integrity.md` as it stands on `main` at `7165ea5c`, graded
against `origin/build-k0-execution-integrity` at `48170de9`.

**NOT CITABLE FOR:** Gate 2 in any part; any statement about the rehearsal's products; any
authorization to submit, merge or adopt; any scientific verdict. §8/§G of the contract is unchanged:
even a PASS here would discharge corrections 2–4 for the k=0 arm and nothing else.
