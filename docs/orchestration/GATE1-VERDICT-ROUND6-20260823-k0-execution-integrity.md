# GATE-1 VERDICT (ROUND 6) 2026-08-23 — pre-submission readiness for the k=0 M(ii) member

**GATE 1 DOES NOT PASS.**

Stated in the words §7.0.6 requires: **Gate 1 DOES NOT PASS.** Sixteen of the eighteen
pre-submission halves pass; **two fail** — **`F-2(a)`** and **`F-17(a)`**. No criterion is recorded
NOT-EVALUABLE. Under §F's no-partial-credit rule as scoped by §7.0.6, any single miss at a gate is a
FAIL of that gate.

**Exact failed criteria: `F-2(a)`, `F-17(a)`.**

**What this blocks.** The seven jobs of logical legs 1–5 for k=0 are **not** authorized for
submission. Gate 2 is not graded and legitimately cannot be.

**Round 6 did what it set out to do.** Both round-5 defects it targeted are genuinely repaired and I
could not break either: the ordering inversion is gone from all eight launchers and is now settled by
a *running* detector with a proven-fireable negative control, and both `F-14` grounds are closed and
re-measured in the correct tree. Both of the packet's previously false claims are now true. **`F-2(a)`
fails on a different ground**, which the round-6 commit touched in all eight launchers without
closing: the two environment libraries execute from the code root **unverified**. **`F-17(a)` fails
unrepaired** — it was not in round 6's scope, and a difference I reported in writing in round 5
remains both uncorrected and unreported.

---

## 0. Eligibility, the frozen objects, and hygiene

**Eligibility (F-18, §7.0.10, ruling 23, as extended by Joseph's process ruling of 2026-08-23).** I
did not build `fabeedc2` or any predecessor; I authored no code in this repository and no part of the
k=0 plan. I did not author the review contract or its operative §7.0 split, nor §7.0.11–§7.0.16. I
**am** the round-5 grader, and Joseph has ruled explicitly that prior service as grader does not
disqualify me. I record that dependency plainly rather than leaving it implicit: two of the three
round-5 findings under review are **my own**, so I have a standing incentive to find them
unrepaired. I therefore tried hardest to *break* the round-6 fixes, and I record below that I
**could not** — and I correct one of my own round-5 measurements against my own interest in §3.1.

| object | value |
|---|---|
| **RUBRIC / filings** | `main` @ `03b95409f2661af2f218a475eeeecf6aa1427699` |
| **contract** | `docs/orchestration/REVIEW-CONTRACT-20260822-k0-execution-integrity.md`, **1160 lines**, sha256 `e0fb342b6466ab9bb7fbcdef4b7a65a40351a2a0b22ab8f4fb534486dd5f1173` |
| **CANDIDATE / DEPLOYED** | `fabeedc2bf78c81d2931ff4876d161c0abfbdbc4`, on `build-k0-execution-integrity`; deployed at `/pscratch/sd/j/josephrb/k0r2/clean`, porcelain **0** |
| **source listing** | **778** tracked source files, `528dae8feabc9139484eb03cc92d8cc124f2dcc9bbfa7ab7971632493d962784` — REPRODUCED |
| **env-manifest digest** | `499e923aaabfcf310e0abdc4a5bdd877cf58d3a9c52bd41d76fa0a05eb131392` — unchanged, REPRODUCED |
| **guard bytes** | `mnv_guarded_run.py` sha256 `bd2ccce19181b075091569fe4ee89b52e6eb0aa0e4e65c165fe2292e2234924f` — **byte-identical to `f3c27870`** |
| **hosts** | local `Josephs-MacBook-Pro-9.local`; cluster `saul.nersc.gov` → `login34` (bash 4.4.23) |
| **window (UTC)** | `2026-08-23T05:09:59Z` → `2026-08-23T05:25:16Z` |

**The rubric did not move, and I checked rather than assumed.**
`git diff a8f79c9a 03b95409 -- <contract>` is **empty**: the operative criteria are byte-identical to
those I graded in round 5. Same eighteen, same §7.0. The branch copy is still the **superseded**
575-line one, so a verdict graded against the branch would be void; this one is graded against
`main`. **I added no acceptance criterion.** Every clause below is quoted from the operative
contract; two observations that fall *outside* it are recorded in §5 as future findings for Joseph
and are explicitly **not** counted against Gate 1.

**Hygiene BEFORE.** Primary checkout `03b95409`; porcelain exactly two untracked files
(`PROJECT_STATE_PILOT_PROPOSAL.tmp.md`, `log_test.txt`). Untouched.

**Hygiene AFTER.** Primary checkout still `03b95409`; porcelain still exactly those two files.
Work done read-only in two isolated detached worktrees outside `.claude/worktrees/`
(`g6-code` @ `fabeedc2`, `g6-main` @ `03b95409`), both porcelain **0** when removed, both removed.
Deployed root still `fabeedc2`, porcelain **0**, no probe residue. Canonical checkout porcelain
**721**, unchanged. Cluster writes confined to `/tmp`; every temp dir removed.

**Instrument discipline.** `bash -c` for all multi-file work (zsh does not word-split unquoted
variables and eats `--include=*.py`). Every exit status read **unpiped**. `TMPDIR` explicit on every
suite. One of my own harness errors is reported against me in §3.1.

---

## 1. The Gate-1 column, criterion by criterion

| # | verdict | first-hand basis |
|---|---|---|
| F-1(a) | PASS | A-2(a)–(g) each a separate observation on the deployed root, all rc=0; porcelain 0; 778 / `528dae8f…`; writable-walk 0; **attempted write refused**; both preflight tools *and* both env libs IN the 778-entry manifest |
| F-2(a) | **FAIL** | `lib_mnv_env_preflight.sh` and `lib_mnv_env_pathcheck.sh` are sourced from the code root in **all eight** with **zero** `--pair`, **zero** git-parity gate, and execute **77–193 lines before** the only instrument covering their bytes (§2.2) |
| F-3(a) | PASS | non-comment `--allow` = **0** across all eight; `build_child_argv` emits none |
| F-4(a) | PASS | denominator **14** + the pinned-writer child, > 0, three independent ways: non-comment `--expect-root` 14, P-6 `--` targets 14, census `14 guarded` |
| F-5(a) | PASS | `test_source_manifest_constitution` **28** and `test_p4_ratchet_fail_closed` **30**, rc=0, fires-on-mismatch **and** silent-on-match both pinned |
| F-6(a) | PASS | code root's `build_child_argv` emits guard + mandatory inventory, fail-closed twice; `repo_origin_count` unconditional; both directions pinned |
| F-7(a) | PASS | identity comparator, undeclared pin fails closed, 30 arms; **13** census arms incl. fires-on-added-unguarded, fires-on-shrunk-set, silent-on-real-tree; ruling 21's boundary asserted by test |
| F-8(a) | PASS (flagged) | P-6 re-run by me at `fabeedc2`, reproduces **exactly** (8 entrypoints / 14); subprocess enumeration 1 child, **WRAPPED**; blind spot 5 published. Flag: filings not re-published at the new sha (§3.4) |
| F-9 | PASS | **re-run first-hand at `fabeedc2`**; all six rows of §7.0.11 discharged on the `guard_installed`/`checked`/`outcome` triple (§3.3) |
| F-10 | PASS | `test_n2_child_boundary` **7** arms rc=0, ruling 19's replacement shape, pinned writer neither copied nor executed |
| F-11 | PASS | `test_n3_rooted_import_repair` **8** arms rc=0, both directions + power + silence; all six B-1 prologues `__file__`-derived, no absolute fallback |
| F-12 | PASS | N-1's three restated clauses discharged first-hand; N-2/N-3 `__file__` anchors green |
| F-13 | PASS | refused-outside **and** not-refused-inside, plus `--allow`-cannot-launder and outside-every-checkout |
| F-14 | **PASS** — was FAIL in round 5 | `generate_manifest.py --check` **rc=0** at `fabeedc2` in a clean worktree; `SubstitutionFenceS1` **11 arms rc=0**, the 199 remainder restored by a principled reclassification whose own count is asserted (§3.2) |
| F-15 | PASS | `TMPDIR=/private/tmp python3 -m unittest test_mnv_guarded_run test_oi136_failopen_inventory_ratchet` → **`Ran 57 tests … OK`**, rc=0 unpiped; counts as measured: **50 and 7** |
| F-16 | PASS | `verify_hash_bindings.py` rc=0, `ALL BINDINGS INTACT`, run after all other observations |
| F-17(a) | **FAIL** | no M-1…M-6 re-measurement exists at the pinned sha; and the M-1 filing still drops `unified_throw_cov.py` and still says "the three that remain" where there are **four** — a difference I reported in round 5, now canonical on `main`, neither repaired nor reported (§2.3) |
| F-18(a) | PASS | this document, clause by clause, by an eligible grader under Joseph's process ruling |

**TALLY: 16 PASS / 2 FAIL / 0 NOT-EVALUABLE.**

---

## 2. The findings

### 2.1 What round 6 fixed, verified adversarially

I tried to break both repairs. Both hold.

**The round-5 ordering inversion is gone.** Real file line numbers, all eight, deployed bytes:

```
LAUNCHER                                       PREFLT  ACTIV PATHCK SRCMAN PARITY
sbatch_bootstrap_5d_gpu.sh                         85     87     94    161    170
sbatch_seedscan_split_5d.sh                        72     74     81    148    157
sbatch_unfold_5d_detector_bkgaware_gpu.sh          86     98    104    171    180   <- was act 227 / SRCMAN 139
sbatch_sweep_bank_5d_run_bkgaware_gpu.sh           80     82     89    157    166
sbatch_uthrow_run_5d_fast.sh                       79     81     88    158    167
sbatch_uthrow_block_5d.sh                          75     77     84    152    161
sbatch_uthrow_combine_5d_fast.sh                   76     78     85    168    177
sbatch_finalize_5d_bkgaware_gpu.sh                 78     80     87    270    279
```

preflight → activator → pathcheck → SRCMAN → PARITY in every one, and `parityOK < firstScience` in
every one. **The exact arm that failed round 5 now passes**: `unfold_detector`'s preamble to its
parity line, under the *login-default* (un-activated) interpreter, `unfold_EXIT=0`, `6 of 6 CURRENT`
— where round 5 gave `REPRO_EXIT=3` and a `SyntaxError`. All eight reach parity under that
interpreter.

**The ordering is now settled by RUNNING, as ruling 21 requirement 3 demands.** The purely textual
arm is joined by `NoPythonRunsBeforeTheActivator`, four arms, all green: a `python3` shim earlier on
`PATH` that exits 42 unless the activator has run (asserted `!= 42` for all eight, so it cannot
silently pass); a **negative control** proving the detector can fire; and an arm pinning the
misattribution — an unusable interpreter must report *"ENVIRONMENT fault, not a wrong-tree fault"*
and must **not** say *"is not the tree that was approved"*. The launcher suite is **38 arms, rc=0**
(34 + these 4). The fixture-supplies-what-is-under-test hole I identified is genuinely closed.

**Both false packet claims are now true, measured in the right tree.** `generate_manifest.py --check`
**rc=0** at `fabeedc2` in a clean worktree *and* rc=0 on `main` — the asymmetric comparison is gone.
The broader suite on the target platform is **394 passed / 2 skipped**, exactly as claimed: I measured
`393 passed / 1 failed / 2 skipped` on macOS and confirmed the single failure is the same
`/private/tmp`-symlink artifact I diagnosed in round 5, which **passes on Linux** (`Ran 1 test … OK`).
I am not counting it.

**Ruling 21's guarding boundary is untouched**, which is the load-bearing null: census rc=0,
`14 guarded + 16 declared-preflight + 16 interpreter-probe + 0 unclassified = 46`. Guarded stayed
**14**, declared-preflight stayed **16**, unclassified stayed **0**.

### 2.2 F-2(a) — FAIL. Two executing shell files run unverified, in all eight launchers.

F-2(a) requires *"the number of `.py` and `.sh` files that will execute on the path, plus
`mnv_guarded_run.py` itself, **not** covered by an A-3 `--pair`"* to be **zero**. It is **two**.

`lib_mnv_env_preflight.sh` and `lib_mnv_env_pathcheck.sh` are `source`d from `${CODE_ROOT}` — so they
**execute** — and measured on the deployed bytes across all eight launchers:

```
$ grep -h -- '--pair' <the eight> | grep -c 'lib_mnv_env'          -> 0
$ grep -h -E 'hash-object|rev-parse' <the eight> | grep -c 'lib_mnv_env'  -> 0

  launcher                                     sourced   manifest-compare
  sbatch_bootstrap_5d_gpu.sh                        84         161   EXECUTES BEFORE VERIFICATION
  sbatch_seedscan_split_5d.sh                       71         148   EXECUTES BEFORE VERIFICATION
  sbatch_unfold_5d_detector_bkgaware_gpu.sh         85         171   EXECUTES BEFORE VERIFICATION
  sbatch_sweep_bank_5d_run_bkgaware_gpu.sh          79         157   EXECUTES BEFORE VERIFICATION
  sbatch_uthrow_run_5d_fast.sh                      78         158   EXECUTES BEFORE VERIFICATION
  sbatch_uthrow_block_5d.sh                         74         152   EXECUTES BEFORE VERIFICATION
  sbatch_uthrow_combine_5d_fast.sh                  75         168   EXECUTES BEFORE VERIFICATION
  sbatch_finalize_5d_bkgaware_gpu.sh                77         270   EXECUTES BEFORE VERIFICATION
```

**Neither accepted substitution covers them, and I checked both.**

* **Not `--pair`.** Zero occurrences in any launcher.
* **Not the pure-git gate.** Ruling 25 accepted a pure-git parity gate *before the source* as the
  substitute for `--pair` on `setup_salloc_env.sh` and `lib/resume_guard.sh`. That gate exists in
  these same launchers — **17 lines above the defect** — and names only `lib/resume_guard.sh`:
  `git rev-parse "HEAD:lib/resume_guard.sh"` / `git hash-object` at `:67-68`, under the comment
  *"lib/resume_guard.sh is TRACKED, so git binds it — verified before it is sourced."*
* **Not the digest manifest.** In round 5 I accepted `mnv_env_manifest.tsv` as the substitute for the
  thirteen closure files, because those live **outside every checkout** and are structurally
  unpairable. These two are different in exactly the way that matters: they are **tracked**, and git
  *can* bind them — I verified it works:
  `lib_mnv_env_preflight.sh HEAD=f5abad89… work=f5abad89… MATCH`,
  `lib_mnv_env_pathcheck.sh HEAD=bad2010e… work=bad2010e… MATCH`.
* **Not A-2(f).** The whole-tree source-manifest comparison is the *only* instrument that covers
  their bytes, and it runs at `:148–:270` — **after** they have already executed. The launchers'
  own comment says A-2(f) and A-3 answer different questions; and a check that runs after the bytes
  execute is the **bind-after-use** shape ruling 25 forbids in terms — *"do not redefine an
  after-the-fact check as preflight"* — and the shape round 4 failed `F-2(a)` for in
  `lib_member_resume.sh`. `lib_member_resume.sh` is `--pair`ed; these two, sourced far earlier, are
  not.

**There is no structural obstacle here.** This is not the round-4 situation where git could not reach
the bytes; it is an omission, in files the round-6 commit renamed and re-pointed in all eight
launchers.

**I must correct my own round-5 verdict.** I wrote there that executing files not covered by a
`--pair` numbered *"**0** among files under the code root."* **That was wrong**, and it was wrong at
`f3c27870` for the same two files under their former names. I graded `F-2(a)` FAIL in round 5 on the
ordering ground, so the error never changed a verdict — but the statement was false and I am
retracting it, not restating it. This finding is therefore **not** a round-6 regression: it is a
round-5-era defect that my round-5 measurement missed and that round 6 did not close.

### 2.3 F-17(a) — FAIL. Unrepaired, and one difference was already reported in writing.

F-17(a) requires M-1…M-6 *"re-measured on `MNV_CODE_ROOT` at the pinned sha and on the canonical
checkout as it stands at submission time, and **any difference from this document reported as a
finding**."*

**No such re-measurement exists at `fabeedc2`.** `MEASUREMENT-20260822-m1-m6-at-pinned-sha.md` is
pinned to `6113a34d` and carries an `f3c27870` M-5 banner; neither it nor
`P5-P6-20260822-…md` carries any `fabeedc2` or round-6 banner (grep: zero hits in both). The sha has
moved twice since M-1 was taken, and the document's own expiry clause says *"Re-run all six
immediately before the first `sbatch` … Do not inherit a number from this table."*

**I re-measured all six myself, and the substance is largely sound** — which is why this is a FAIL of
the reporting obligation and not of the underlying tree:

* **M-2** 125 importable names, **zero** collisions both directions — reproduces.
* **M-3 / F-16** `ALL BINDINGS INTACT`, rc=0 — reproduces.
* **M-4** `b2d7d4ca…`, **721** dirty = **717 `??` + 4 ` M`** — reproduces exactly.
* **M-6** repaired, `checked_provenance` present — reproduces.
* **M-5** all four filed quantities hold at `fabeedc2` (`REPO=` 0/8, unguarded activator sources 0/8,
  `ENV_ROOT` sources 8/8, `_mr_lib` bind-after-use 0/8) **and the fifth quantity is now repaired**:
  `python3` before the activator = **0 of 8**. That repair is real and it is **not filed anywhere** as
  a measurement.

**The decisive part is M-1, and it is a difference already handed to the builder.** The filing's M-1
table carries **nine** rows; the contract's M-1 table (`REVIEW-CONTRACT…:54`) carries **ten**.
`unified_throw_cov.py` is dropped — and it is one of the six **B-1 repair files**
(`REVIEW-CONTRACT…:228-232`), so its status is load-bearing, not incidental. The filing then states
*"the three that remain"* and lists three. Measured at `fabeedc2` there are **four**:

```
unfold_nd_omnifold_unbinned.py:73   _DATA_ROOT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
sweep_bank_5d.py:59                 _DATA_ROOT = …
unified_throw_cov.py:69             _DATA_ROOT = …          <-- ABSENT from the filed table
adopt_unified_5d.py:35              _REPO      = …
```

**The substance is benign and I say so plainly**: the omitted one is a `_DATA_ROOT`, the data role the
two-root design permits, and I re-verified that all six B-1 prologues derive from
`Path(__file__).resolve().parents[N]` with **no absolute fallback**. The defect is the enumeration.
I reported it in the round-5 verdict; that verdict is now committed on `main` at `03b95409`
(`docs/orchestration/GATE1-VERDICT-ROUND5-…md`). It is still uncorrected and still unreported — and
the filing's own sentence warns that *"a bare '3 still carry the literal' is the sentence that would
mislead."*

**Why this is a FAIL and F-8(a) is a flagged PASS**, since both turn on filings bound to a superseded
sha and I should not apply two standards. F-8(a)'s artifacts are **stale but true**: every claim in
them reproduces at `fabeedc2` when I re-run it. F-17(a)'s artifact contains an **affirmative false
statement** on a point already reported in writing, and F-17(a)'s obligation *is* reporting
differences. Staleness alone I did not fail; a wrong number that survived being pointed out, inside
the criterion whose whole subject is reporting differences, I did.

---

## 3. Supporting measurements

### 3.1 An error of mine, and a correction against my own interest

Running all eight preambles to their parity line under the login-default interpreter, seven exited 0
and **`sbatch_finalize_5d_bkgaware_gpu.sh` exited 2**. That was **my harness's fault, not a defect**:
finalize resolves its member-axis library *before* its parity block, and I had omitted
`MNV_LAUNCHER_DIR`, which A-5 and `RUNBOOK…:416` both require the submitter to export. With it set,
finalize exits **0** with `9 of 9 CURRENT`. Recorded because an unexplained exit 2 in a grader's
table would read as a ninth defect, and because the fix was in the runbook I had already read.

### 3.2 F-14, closed on both grounds

```
@ fabeedc2 (clean worktree)  rc=0  OK: docs/orchestration/MANIFEST.tsv; rows=425 …
@ 03b95409 (clean worktree)  rc=0  OK: docs/orchestration/MANIFEST.tsv; rows=435 …
SubstitutionFenceS1          rc=0  Ran 11 tests OK   (macOS and Linux)
```

**The reclassification is principled, and I checked that it is not a dodge.** The two files were
*renamed* `mnv_env_*.sh` → `lib_mnv_env_*.sh` (git records R100) so they satisfy the fence's **own**
definition-file rule — each defines a function, neither carries `#SBATCH` — rather than being added
to a name-list exemption. The 199 remainder is restored unchanged, the exclusion count is itself
asserted (`…_are_exactly_four`, moved 2→4 with the delta named), and the docstring records that the
199 pin *worked*: it forced a classification instead of letting the default be "unfenced". That is the
ratchet behaving as designed.

I note without counting it that the same rename is the vehicle of the §2.2 defect: the files were
touched in all eight launchers and still not bound.

### 3.3 F-9, re-run at `fabeedc2` rather than inherited

`mnv_guarded_run.py`, `mii_adopt_unified_5d_stamped.py` and `adopt_unified_5d.py` are **byte-identical**
to `f3c27870` (`git diff --stat` empty; guard sha256 `bd2ccce19181b075…`), but I re-ran the control
anyway. Arm A, `A_EXIT=3` unpiped: `outcome='refused:script-outside-expect-root'`,
`guard_installed=False`, `checked=0`, `checked_provenance='not-measured-no-guard-was-installed'`,
`refusal_site='b4-script-containment'`, `expect_root` = clean tree, `script_checkout_root` = canonical
— all three named. `[remedyA]` absent, `[adopt5d]` absent, `--out` fails `test -e`, witness directory
empty before **and** after, one merged stream per arm, status captured unpiped. 9.6 graded on the
triple, not by grepping a token; reported not graded, the token occurs 0 times. Arm B (O-1 paired)
reaches the marker with `guard_installed=True`, `checked=9`, so the arm **could** have succeeded —
F-12(N-1)(ii). Arm C (U/U′, unguarded, no record) named
`seed_offset_policy.__file__ = /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/seed_offset_policy.py`
— F-12(N-1)(iii).

### 3.4 F-8(a)'s flag, stated so it is not mistaken for a pass on trust

P-6 re-run by me on the deployed root at `fabeedc2`: `4+2+2+2+1+1+1+1 = 14` across 8 distinct
entrypoints, every one addressed through `${CODE_ROOT}` — reproduces the filed table exactly.
Subprocess enumeration: **0** executing spawn sites in eight of nine files, exactly **1** at
`mii_adopt_unified_5d_stamped.py:788`, **WRAPPED**. Blind spot 5 is published. **Flag:** no P-5/P-6
artifact was re-published at `fabeedc2`; I graded on content I measured myself. A stricter grader
could call the filing half NOT-EVALUABLE and therefore a FAIL under §7.0.8, which would read
**15/3**. Gate 1 fails either way.

### 3.5 F-1(a)

Each A-2 clause a separate observation, every status unpiped: `HEAD fabeedc2…`; porcelain **0**
(`wc -l` on a redirected file); `--require-checkout`, `--require-no-nested-checkout`,
`--require-not-nested`, `--require-readonly` each **rc=0**; A-2(f) **778** / `528dae8f…`. (g) on three
instruments: mode bits `dr-xr-x---` / `-r--r-----`, independent writable walk **0**, and an
**attempted write as this user refused** (`Permission denied`, no file created, no residue). §7.0.13
requirement 2 holds: both preflight tools **and** both env libs are in the 778-entry manifest — which
is precisely why §2.2 is an A-3 failure and not an A-2(f) one.

---

## 4. Regression check against round 5

| round-5 finding | status at `fabeedc2` |
|---|---|
| `F-2(a)` ordering inversion in `unfold_detector` | **FIXED**, verified by execution; dynamic detector added with a working negative control |
| `F-2(a)` env libs unbound *(mis-measured by me as 0)* | **STILL PRESENT** — §2.2, now the sole `F-2(a)` ground |
| `F-14` `generate_manifest --check` rc=1 | **FIXED**, rc=0 in a clean worktree at the graded sha |
| `F-14` `SubstitutionFenceS1` 201≠199 | **FIXED**, 199 restored by principled reclassification |
| `F-17(a)` M-5 silent on the execution property | **FIXED IN CODE** (0 of 8), **NOT FILED** as a measurement |
| `F-17(a)` M-1 drops `unified_throw_cov.py`, 3 vs 4 | **UNREPAIRED and UNREPORTED** — §2.3 |
| packet: "390 passed, 2 skipped" | **CORRECTED**; 394/2 on Linux, verified |
| packet: "`generate_manifest --check` rc 0" | **CORRECTED**; true in the graded tree now |
| misattributing refusal message | **FIXED** and pinned by a test |
| ruling 21 boundary 14/16/0 | **UNCHANGED**, census rc=0 |

No criterion that passed in round 5 regressed.

---

## 5. Future findings — recorded, NOT counted against Gate 1

Per Joseph's ruling, these fall outside the operative rubric and **do not** expand Gate 1. They are
for his decision, not for a grader's tally.

1. **Ruling 21's excluded set has grown from 16 call sites to 32.** Round 6 adds **16** interpreter-
   capability probes (2 per launcher) as a declared **third** category. I did **not** count this as an
   `F-2(a)` failure, and the reason is on the record: §7.0.13 requirement 1 prohibits an exclusion
   that can grow **silently**, and this one cannot — it is enumerated, pinned in
   `mnv_preflight_exclusions.json` with counts derived from the launcher bytes, declared visibly as a
   separate category rather than folded into a total (that is what the `fabeedc2` commit exists to
   do), and covered by 13 census arms including *fires-on-an-added-unguarded-invocation* and
   *fires-on-a-shrunk-set*. The probes also import no repository module — `python3 -c 'import sys; …'`,
   `command -v python3`, `python3 -V` — so guarding them would be vacuous by construction, which is
   ruling 21's own stated rationale for the first exclusion. **But the size of the boundary is
   Joseph's to ratify, not a grader's to widen**, and it should be ratified explicitly.
2. **`ROOT628_CONDA` is still `${VAR:-default}`** (`setup_salloc_env.sh:11`). Carried forward from my
   round-5 verdict, unchanged, still bounded (the *prefix* is mandatory, so the digest-bound
   `activate.d` set is determined, and the pathcheck would refuse a rogue conda that touched any
   channel). Round 4's repair item asked for both to be pinned; only the prefix was.
3. **The unreadable-closure-member arm still refuses with the wrong reason** — `COULD NOT LOOK: no
   sha256 tool for <path>` when the cause is a permission. Fails closed, so not a defect in behaviour.
4. **`RUNBOOK-20260822-b1-lift-preflight.md` and the plan's §C still export neither `MNV_ENV_ROOT` nor
   `MNV_CONDA_PREFIX`** (0 occurrences of each). Following the procedure of record, every launcher
   refuses at `${MNV_ENV_ROOT:?}`. I recorded this in round 5 and declined to rest `F-14` on it then,
   for the same reason I decline now: those §6 rows' literal text names only the two roots. It remains
   an operational blocker for whoever submits.

---

## 6. The parts of this verdict most likely to be wrong

1. **Failing `F-2(a)` on the two env libs.** The counter-argument is that A-2(f)'s 778-file manifest
   *does* cover their bytes and the tree is read-only under A-2(g), so the residual risk is small. My
   answer: the manifest comparison runs after they execute, A-3 and A-2(f) are different questions by
   the launchers' own comment, and ruling 25's accepted substitute is a gate *before* the source — one
   that exists 17 lines away for a sibling file. If Joseph rules A-2(f) sufficient for sourced
   libraries, this ground falls and **Gate 1 passes on my measurements**, since `F-17(a)` would then
   be the only failure — so this is the single most consequential judgement in the document.
2. **Failing `F-17(a)` on a filing defect** whose substance is benign. A grader who treats the
   criterion as satisfied by *my* re-measurement rather than by the package's would pass it.
3. **Not failing `F-2(a)` on the 16→32 exclusion growth.** A stricter grader would, and would report
   a third failure. I judged the mechanism intact and the boundary Joseph's; §5.1 records it so it
   cannot be lost.
4. **Passing `F-8(a)`** where the artifacts were not re-published at the graded sha (§3.4).

---

## 7. What this verdict does and does not authorize

**Nothing.** §G is unchanged. The k=0 rehearsal is **not** launched and no downstream work is
authorized. Gate 2 is not graded and cannot be. `OI-136` is not closed. No member `k≠0`, no leg 6, no
scientific verdict of any kind. This is a **terminal handoff**: I have implemented no repair,
requested no further grader, and taken no action beyond grading.

## 8. Explicit confirmation of non-mutation

* **No Slurm job was submitted.** `squeue -u josephrb` shows exactly one job, `57275989`, submitted
  `2026-08-20T15:02:55` — three days before this session — `PENDING`. `sacct -S 2026-08-22T00:00`
  returns that same single row and nothing else.
* **No science was run**, no covariance constructed or adopted, no rehearsal started, no leg launched.
* **No scientific artifact** created, opened for write, moved, renamed or deleted. The negative
  controls used only nonexistent throwaway paths under `/tmp`; the witness directory was empty before
  and after.
* **No deployment changed.** `/pscratch/sd/j/josephrb/k0r2/clean` still `fabeedc2…`, porcelain **0**,
  A-2(g) intact and demonstrated by a refused write with no residue. Canonical checkout still
  `b2d7d4ca…` with **721** dirty entries, unchanged.
* **No repository edit, commit, push or merge.** Primary checkout still `03b95409`, with exactly the
  two pre-existing untracked files, untouched. Both detached worktrees had porcelain **0** and were
  removed.
* **`set -u` was neither added nor invoked.** Cluster writes confined to `/tmp`, all removed.

---

*Recorded by the Gate-1 grader under Joseph's process ruling of 2026-08-23. PRE-SUBMISSION column
only. **GATE 1 DOES NOT PASS. Failed criteria: `F-2(a)`, `F-17(a)`.** Terminal handoff — no repair,
no further grader requested, no action taken.*
