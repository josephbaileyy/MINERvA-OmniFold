# REVIEW 2026-09-11 — the precursor repairs (b)-(g) and admission accounting, against the
# pre-registered `P1`-`P18`

**CITABLE FOR:** the per-criterion verdicts in §2, the executed verifications in §3, the corrections to
this lane's own earlier findings in §1, and the residual judgement in §5.
**NOT CITABLE FOR:** any launch authorization, any adoption, any grade, any gate movement, or any
significance. **The admission accounting REFUSES this run** (§3.1). `R4` suspended; Gate 2 FAIL;
endpoint B requested-but-unvalidated and not authorized for execution. Nothing was launched.

**Subject:** `lane/z-precursor-repairs-bg-20260911` @ **`8111a951`**, 6 commits off `77a4af38`.
**Yardstick:** `PREREGISTER-20260911-precursor-repair-acceptance-criteria.md` (`2d61d81f`), committed
**before** this work existed. **This lane authored none of the repairs and supplied no remedy.**

**Method:** reviewed in an **isolated worktree** at an absolute path, confirmed afterwards that no
stray was created in the main checkout. Guards were **executed**, not only read.

## 1. Corrections to THIS LANE's earlier findings, first, because they were wrong

### 1.1 My `r5_meter` timezone finding is WITHDRAWN

I reported that `r5_meter.py:_sacct_argv()` emits a naive `--starttime` and therefore **under-meters by
7 h**. **That is FALSE of the meter's live path.** Measured: `_read_source` at **`:551-557`** copies the
environment and sets `{"TZ": "UTC", "SLURM_TIME_FORMAT": ...}` before `subprocess.run`. **The meter's
live `sacct` query is on the UTC basis and always was.**

**What I actually measured was my own hand-rolled `sacct` call** fetched without `TZ`, fed to the meter
through `--from-file`. I then attributed its basis to `_sacct_argv()` because the argv contains a naive
stamp — **which is the exact error I had diagnosed and written up one step earlier**: the argv does not
determine the window, the **environment** does. I applied that rule to the receipt and then failed to
apply it to the meter's own child process. **Third iteration of one error in one session**, and this
time it was in the permissive direction toward my own active finding.

**What survives, relocated.** The naive basis is real but it enters through **hand-rolled captures fed
to `--from-file`**, not through the instrument. Verified on the archived capture:
`state/r5-capture-20260910/sacct-r5-t0-to-20260910T065750Z.psv` holds **1,827 rows**, against the
`2026-09-09` receipt's **1,888 attempts** produced by the meter's live (UTC) path. **Spend only
accumulates, so a 09-10 capture cannot be smaller than the 09-09 value on the same basis** — therefore
that capture is **not** the UTC basis. It matches my own naive dump (1,831 attempts one day later, and
80 vs 80 rows in the 13:44-20:44 own-zone band, against 62 on the UTC basis). **So
`FINDING-20260910`'s "attempt identity is not stable across queries" remains a misdiagnosis — but the
mechanism is a hand capture on the narrow basis compared against a meter-produced receipt, not an
instrument defect.** Stamps cannot discriminate the two bases, because both windows begin at the same
clock-face time in their own zone; only the counts can.

**The owner's version is better than mine and supersedes it**, and it does **not** inherit my error:
`z_precursor_admission.py:47-53` states both consequences explicitly — that `:552-557` sets `TZ=UTC` so
*"the meter's window starts 7 h late is FALSE of that path"*, **and** that `shlex.join(argv)` omits the
`TZ` assignment while `--from-file` records only a path, so **a receipt's own fields cannot establish
which basis produced it**. Its independent measurement (1894 vs 1832 rows) reproduces mine exactly.
**`P16` is satisfied in its restated form**, and declining to encode the `0.4858` figure is right —
encoding it would adopt a threshold and would be wrong the moment the offset changes.

### 1.2 My "the landing is not pushed" finding is RESOLVED, not withdrawn

It was accurate when measured (`origin/main` was `6f24fb00` with `main` 1 ahead). `origin/main` is now
**`77a4af38`**. Recorded so the earlier record is not read as a live defect.

### 1.3 One hasty call of my own, recorded

I read the full-suite run as **blocked** from the parent process sitting at `0.0%` CPU, and terminated
it. It was not blocked: the parent was waiting on a **child** (`mnv_guarded_run.py`, state `R`). The
suite is **subprocess-bound**, not hung, and I killed a run that was progressing. Parent CPU is not a
liveness measure for a process whose work is in children.

## 2. Verdicts, `P1`-`P18`

| criterion | verdict | evidence |
|---|---|---|
| `P1` reach per mutation | **SATISFIED, exceeds** | §3.3 |
| `P2` distinguishable from infra refusal | **SATISFIED by construction** | §3.3 |
| `P3` UNKILLED reported | **SATISFIED for the mutated set**; see §4.1 | §4.1 |
| `P4` fixture from the producer | **SATISFIED, strongly** | §3.4 |
| `P5` identities, named on failure | **SATISFIED** | §3.2 |
| `P6` both directions | **SATISFIED** | §3.2 |
| `P7` every arm | **SATISFIED (executed)** | §3.1 |
| `P8` a glob is not a population | **SATISFIED, on the declaration side too** | §3.2 |
| `P9` non-empty by construction | **SATISFIED** | §3.2 |
| `P10` non-emptiness refuses | **SATISFIED** | §3.2 |
| `P11` writer/reader on the undeclared path | **SATISFIED BY RELOCATION** — see §5 | §5 |
| `P12` `mii/` is a refusal | **SATISFIED (executed)** | §3.5 |
| `P13` `sys.path[0]` named per entrypoint | **SATISFIED** — my own dim-2 finding repaired | §3.6 |
| `P14` reuse, not reimplement | **SATISFIED**, with one durability note | §3.1 |
| `P15` charged + committed, retries and queued | **SATISFIED, and improved on my wording** | §3.1 |
| `P16` declared basis | **SATISFIED (restated)** | §1.1 |
| `P17` R5's running-at-the-stop preserved | **SATISFIED** | §3.1 |
| `P18` silent positive controls, same path | **SATISFIED** | §3.7 |

**No criterion is unmet.** The two items needing a decision are **not** compliance failures: the
refusal in §3.1 and the residual in §5.

## 3. The executed verifications

### 3.1 The accounting refuses the run, and I reproduced it (`P7`, `P14`, `P15`, `P17`)

Executed `z_precursor.parse_sbatch_arm` on the four real launchers and
`z_precursor_admission.committed_task_hours(arm, 0)`:

```
dump     n_tasks= 8  time_limit_h= 6.00  committed=  48.00
block    n_tasks=21  time_limit_h=12.00  committed= 252.00
run      n_tasks=40  time_limit_h= 6.00  committed= 240.00
combine  n_tasks= 1  time_limit_h= 3.00  committed=   3.00
TOTAL committed (0 retries)                      543.00
+ charged 15.4231                            =   558.42   vs R5 500  ->  headroom -58.42
```

**Reproduced to the cent.** The arms are **parsed from the `#SBATCH` lines** (`parse_sbatch_arm(path)`),
so the declaration is derived, not retyped. The dominant term is `21 × 12 h = 252` on a job whose
measured mean is `1.1213` h.

- **`P14`:** `import r5_meter` (*"the charged half, REUSED"*), and it uses `r5_meter._parse_sacct_dump`,
  `r5_meter.SACCT_FIELDS` and the meter's receipt validator. **Durability note, not a defect:** it
  reaches for **private** functions, so the reuse rides an unversioned interface. That is still far
  better than retyping; worth a named dependency if the meter is refactored.
- **`P15`:** `committed = n_tasks × (1 + max_retries) × time_limit_hours`, and `--max-retries` has **no
  default** — correct, since R5 counts a failed task in full and the measured population is 1,882
  requeues of 1,885 attempts. **It improves on my own `P15` wording:** I cited `40 × 6 = 240` in flight,
  which is the **concurrency** bound; the owner is right that for a **total** cap the throttle is
  irrelevant (`:108-109`, *"it bounds CONCURRENCY, not total spend, and a throttled array charges
  exactly as much in the end"*). Queued tasks are handled explicitly because the meter drops
  `Start=Unknown` rows.
- **`P17`:** binds at **admission** — *"What changes is that a NEW admission is priced against the
  committed maximum"* — and quotes R5's running-at-the-stop rule as design rather than defect. **No
  running job is touched.**

**The refusal is the accounting working.** The precursor as currently specified **cannot be admitted**
under R5, and that is a decision for Joseph, not a defect to repair.

### 3.2 Population validation (`P5`, `P6`, `P8`, `P9`, `P10`)

`unified_throw_cov.py:294-315`, all three refusals in one place:

- **`P5`/`P6`:** `missing, undeclared = sorted(want - found), sorted(found - want)` — **both
  directions, identities named.**
- **`P8`, and stronger than I asked:** a declared expected-file entry that is **not a plain basename**
  is refused, because *"a glob or a path here would make the declaration match whatever is present,
  which is the absence of a declaration."* The requirement is enforced on the **declaration** side, not
  only the input side.
- **In-progress temps get their OWN refusal**, deliberately not conflated with a stale foreign file:
  *"conflating the two would give one refusal two meanings."* One refusal, one meaning.
- **`P9`:** `check_namespace_fresh` opens with
  `require(names, "no arms named; an empty sweep checks nothing")` — the empty-population guard applied
  to **its own sweep**, which is the gates-that-cannot-fail defence in the right place.
- **`P10`:** *"Every named arm's directory must be absent or hold NO product. Non-emptiness REFUSES"*,
  with an explicit note that a count-based check calling it *"nearly empty"* would wave it through.

### 3.3 Mutation reach (`P1`, `P2`) — and a correction to the briefing's count

**The briefing says "three mutation controls only". There are five mutation TARGETS** across two test
methods (`hmask`, plus `n_cv_genuine_zero`, `n_cv_support`, `n_cv_executions`, `cv_support_predicate`
via `subTest`), plus a harness positive control.

**`P1` is satisfied and exceeded**, three ways:

1. The harness asserts `hit > 0` with *"this mutation would excise nothing and the arms below would
   pass on an UNMODIFIED module"* — the reach **precondition**, checked before the assertion runs.
2. `ast.parse(mutated)` — *"a broken module makes every absence assertion true."* The harness cannot
   be the cause of its own green.
3. The decisive arm asserts **both** `assertNotIn("hCvSupportMask", rec.written)` **and**
   `assertIn("hCvSupportMask", rec.hists)` — the object is still **BUILT** but not **WRITTEN**. That is
   exactly the `3be8c052` / BEN-450 distinction, and it proves the mutation reached **the write**
   rather than breaking construction.

**`P2` is satisfied by construction, not by exit status:** the recorder exposes two channels, so
"nothing built" (infrastructure) and "built but not written" (mutation reached) are different
observations.

### 3.4 Fixtures from the producer (`P4`)

- `IN_PROGRESS_SUFFIX` is defined once in the producer, **imported** by the consumer
  (`unified_throw_cov.py:302`), by the freshness sweep (`z_precursor.py:212`) and by the tests
  (`:583`, `:606`) — *"a second spelling of this suffix somewhere else could stop matching and nothing
  would say so."*
- **The strongest instance:** `test_the_member_presence_test_matches_the_SHELL_predicate_it_mirrors`
  **executes `lib_member_resume.sh`'s own `mr_declared`** and compares, with expectations
  `("0", True), ("1200", True), ("", False)`. A fixture that agreed with the Python instead of the shell
  would have been worthless here, and it does not.

### 3.5 `mii/` is a refusal (`P12`) — executed by this lane

```
unset          -> PASSED   {'member_axis': 'absent', 'ok': True}
='0'           -> REFUSED  PrecursorError: MNV_EST_SEED_OFFSET='0' is SET ...
='7'           -> REFUSED  PrecursorError
=''  (empty)   -> REFUSED  PrecursorError
```

**`'0'` refuses** — the case a value check waves through, and the whole reason this cannot be a value
check. **One precision from the execution:** the Python guard tests **key presence**, while the shell
predicate tests **non-emptiness**, so they disagree on `MNV_EST_SEED_OFFSET=''` — Python refuses, the
shell would call it undeclared. **The disagreement is in the SAFE direction** (it refuses a state that
would have been fine), and the adjacent test documents the shell's `("", False)`, so it is deliberate
rather than an oversight. Recorded so nobody later "aligns" it without knowing which way it leans.

### 3.6 `sys.path[0]` (`P13`) — this lane's own dim-2 finding, repaired

The dump arm was the one with `GUARD=0 mnv_inv=0 mr_require_valid_offset=0` and a hardcoded
`REPO=/pscratch/...` plus `cd` plus bare `python3`. Now:

```
dump      GUARD=7 mnv_inv=2 member_gate=1 DATA_ROOT=10
block     GUARD=8 mnv_inv=3 member_gate=1 DATA_ROOT=6
run       GUARD=7 mnv_inv=2 member_gate=1 DATA_ROOT=6
combine   GUARD=6 mnv_inv=2 member_gate=1 DATA_ROOT=6
```

`CODE_ROOT="${MNV_CODE_ROOT:?...}"` and `DATA_ROOT="${MNV_DATA_ROOT:?...}"` are both **mandatory with no
default**; `:107-115` adds a git-parity preflight comparing `HEAD:<rel>` against `hash-object` of the
working file under `CODE_ROOT`; and `:16` forbids the literal `REPO=<cluster root>` assignment
**anywhere in a launcher's text, comments included**, so the pattern has a detector. The comment names
the mechanism correctly: *"OI-136, REACHED BY `cd` RATHER THAN BY A PYTHON [insert]"*.

### 3.7 Positive controls (`P18`)

Four, including the two that matter most:

- `test_the_CONTRACT_IS_INERT_when_the_namespace_is_unset` asserts `enforce_namespace_contract(...)`
  returns **`None`** — *"with the namespace unset the contract must do NOTHING, not refuse."* **This is
  the arm that separates a guard from a run-blocker**, and it is asserted in the direction that matters.
- `test_POSITIVE_CONTROL_the_unmutated_module_writes_everything` runs the **same harness path** with no
  mutation — satisfying the same-call-path clause.
- `test_POSITIVE_CONTROL_the_exact_declared_population_passes_silently` and
  `test_POSITIVE_CONTROL_a_healthy_product_gets_a_receipt_that_GATES_CLEAN`.
- And `test_a_FOREIGN_but_inventory_complete_namespace_PASSES_and_that_is_the_LIMIT` keeps a
  **negative** result as a test — recording what the guard does **not** catch, which is the honest
  shape and the reason the freshness check is not redundant.

## 4. The (b) repair, the donor, and the temp-name coupling

### 4.1 (b): leaving `x_cv > 0` unchanged is CORRECT and in scope — confirmed

`CV_SUPPORT_PREDICATE = "x_cv > 0"` (`:172`) is unchanged as a predicate (`:178`, `:664-668`) and is now
**persisted as a string** (`TNamed("cv_support_predicate", …)`, `:922`), alongside `n_cv_support`,
`n_cv_genuine_zero`, `n_cv_negative` and `n_cv_bins_total`.

**The crux is the mask's index space, and the reasoning is right.** `:912-916`: *"`hCvSupportMask` IS
OVER `n_total` BINS, NOT `nrep` … A mask indexed in the support would be **all-ones by construction** —
it would be the vacuous flag again, in array form. The mask's whole content is the bins the support does
NOT contain, so it must be indexed in the BINNING."* **Confirmed:** a support-indexed mask carries zero
information, and indexing over the binning is what makes the **excluded set** recoverable.

**So the owner's reading of Joseph's ruling is correct.** Redefining the predicate would change `nrep`
and hence the covariance dimension — that is criterion adoption and out of scope. *"A pinned-zero
inflation bin is not a null operand"* is answered by making the excluded set **reach the product**, with
genuine-zero and negative counted separately, rather than by changing what is excluded. **`P3` note:**
`n_cv_executions` was deliberately given **two reachable values** (1 without `--null`, 2 with) rather
than a literal `1` on the only path — the vacuous-flag shape avoided in its own new field.

### 4.2 Donor: a RECORD, not a choice — confirmed

`band_donor[...] = os.path.basename(s)` (`:761`, `:770`) is **derived from the glob and the labels**;
one `TNamed` per endpoint (`:965-967`), so two endpoints of one band may legitimately differ. The tests
carry `test_NO_DONOR_IS_DECIDED_ANYWHERE_IN_THIS_WORK` **plus
`test_the_donor_detector_CATCHES_one`** — a detector **with its own positive control**, which is what
makes the absence claim non-vacuous rather than decorative. And `:1577` computes the expected donor
**from the layout** (`u // per + 1`), so a 20x5 -> 10x10 re-lay moves both sides together and **no list
in the code could contradict it.** **No donor is decided; nothing here needs a ruling.**

### 4.3 The temp-name fix is a PRECONDITION for the cap remedy

`_atomic_savez` names its temp `<product>.<random>.tmp.npz`, which **matches the consumers' own globs**;
the `except` branch unlinks it but **a wall-clock kill runs no handler**, and
`sbatch_uthrow_run_5d_fast.sh:14` asserts a wall-kill *"re-runs the whole task cleanly"* on this
function's strength — true of the **product**, false of the leftover.

**This couples directly to the §3.1 refusal.** The obvious remedy for `543 > 500` is to cut `--time`
(the block arm's `12 h` on a `1.1213 h` job is `252` of the `543`). **Cutting `--time` raises
wall-kill probability, which is precisely the path that leaves a temp inside the consumer's glob.** So
the temp-name repair is not tidiness — it is a **prerequisite** for the cap remedy, and the two must be
considered together. Now refused with its own message (§3.2).

## 5. The deliberate residual — the scoping is RIGHT, with one condition

An undeclared **non-precursor** run of `sbatch_uthrow_block_5d.sh` still writes `block_slabs_5d` while
the combine reads `_sb`. Left live because repointing would change **archived** behaviour against the
preservation instruction.

**`P11` is satisfied by RELOCATION rather than repair, and that is legitimate.** The precursor now runs
under a **mandatory declared namespace** (`MNV_Z_PRECURSOR_NS`, no default) with a freshness refusal, so
**it is no longer an undeclared run at all** — it has been moved out of the ambiguous branch instead of
the branch being fixed. `P11` asked for writer/reader agreement on the undeclared path *for the
precursor*; the precursor is no longer on that path, and the requirement is met.

**My judgement: correct, on one condition.** The residual must be recorded **where a future reader
meets it** — a `CITABLE FOR` / `NOT CITABLE FOR` marker at the top of `sbatch_uthrow_block_5d.sh`'s own
namespace block and an owner, not only in a lane record. A caveat that lives in coordination traffic
does not exist, and the general launcher's next user is exactly the reader who will not have read this
review.

## 6. Not verified, disclosed

- **The regression evidence is NOT independently confirmed.** The `+102` **is** — `test_z_precursor.py`
  runs **102 tests, OK, rc 0**, re-run here. The `14 failed / 2997 passed / 6 skipped` and the
  identical 14-name failure set are **not** verified: the full `unittest discover` run is
  subprocess-bound and did not complete within this review, and I terminated one attempt in error
  (§1.3). **Treat the 14-name identity as the owner's claim, not this lane's finding.**
- **The owner's own disclosures are accepted, not re-verified:** no local ROOT or LightGBM, so ROOT
  writes are checked through a written-vs-built recorder and `.root` openability tests magic bytes and
  size rather than a real `TFile` trailer; no cluster execution; and `test_uq_remediation`'s BEN-450
  mutation control is red on `main` for `NameError: __file__ is not defined` in its own harness.
- **The review branch is not on `origin`** (`git fetch` for it fails; it exists as a local branch).
  A review citing a local-only ref is not reachable by anyone else.
- This lane **did not** re-derive the 13/27/5 partition, did not execute any launcher, and **supplied
  no remedy anywhere.**

**Bottom line: every one of `P1`-`P18` is met, and the accounting's refusal at `558.42` against `500` is
the finding, not a failure.** Whether to cut `--time`, reduce the arms, or raise the ceiling is
**Joseph's**, and the temp-name coupling in §4.3 constrains the first of those.
