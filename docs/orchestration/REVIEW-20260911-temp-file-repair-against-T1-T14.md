# Independent review: the temporary-file repair @ `05cf2d00` against the pre-registered `T1`-`T14`

**Owner of this record:** `lane/z-criteria-independent-assessment-20260910` (independent assessor).
**Subject:** `lane/z-precursor-repairs-bg-20260911` @ `05cf2d00fc22cb0f84cfd1ad6030a1d71ef05512`,
against the yardstick committed at `e92d4a85` **before the implementation existed**. Delta from
`10eb1bac`: 5 files, +411/−60.

**VERDICT: 12 of 14 criteria MET, four of them EXCEEDED. `T9` is UNEVIDENCED (the property holds and
nothing asserts it); `T14` is PARTIAL (the at-risk population is matched and clean; the full-suite
figure was killed by system memory pressure and I am not quoting a partial run). Two findings, and
neither touches Joseph's primary guarantee — that one rests on the temp NAME, which holds
unconditionally.** Guards were **executed**, not read, in an isolated worktree.

**CITABLE FOR:** the criterion-by-criterion verdict and the measurements below.
**NOT CITABLE FOR:** any launch authorization, any `--time` or `--mem` value, adoption, gate
movement, or spend. `R4` suspended; Gate 2 FAIL.

---

## Part 0 — Corrections to my own prior record, first

**0.1 The mechanism I published for the `MaxRSS` zero was not the mechanism that produced it.**
At `e92d4a85` I wrote *"`MaxRSS` is a step-level field. `-X` returns allocation rows only, where it
is empty by construction,"* and presented that as the explanation of the relayed observation. The
field is indeed step-level and `-X` does indeed suppress it — that part is reproduced. But **the
sweep that reported the zero did not use `-X`**; its filter was a JobName predicate, and step rows
carry JobName `batch`/`extern`, not the job name. Confirmed on **my own** 651-row capture, which
also did not use `-X`:

```
rows total                                     651
rows with non-empty MaxRSS                     206
rows whose JobName matches /uthrow5d_/         239
  ... of those, with non-empty MaxRSS            0     <-- a JobName filter alone suffices
distinct JobName on MaxRSS-bearing rows        batch   (.extern rows: 206, all empty)
```

So there are **two independent, sufficient ways** to get a can't-look zero on this field, and I
attributed the incident to the one I happened to reproduce rather than the one that occurred. My
finding (the field is populated; the probe's resource justification is void) is unaffected and was
accepted. The causal claim was an inference presented as established —
`a-conciliatory-mechanism-is-still-a-technical-claim`. Corrected here and in
`an-empty-sacct-column-may-be-a-row-granularity-artifact`.

Also measured while re-checking: **only the `.batch` step carries `MaxRSS`; all 206 `.extern` rows
are empty.** Any per-arm join must select the `.batch` step specifically, not "any step row."

**0.2 My reachability flag is WITHDRAWN.** I twice recorded that
`lane/z-precursor-repairs-bg-20260911` was local-only and that records citing it were unresolvable.
Re-fetched: `origin/lane/z-precursor-repairs-bg-20260911` = `05cf2d00`, and
`git for-each-ref --contains 10eb1bac refs/remotes` returns that ref, so **`10eb1bac` is reachable
from a remote ref** and `e92d4a85`'s citation resolves for anyone who fetches. The claim was true
when made and I did not re-fetch before repeating it — `a-hold-on-shared-main-is-not-a-hold`, whose
whole content is *fetch first*.

---

## Part 1 — The verdict

| | criterion | verdict |
|---|---|---|
| `T1` | incomplete outputs unselectable | **EXCEEDED** — a property, not an enumeration |
| `T2` | interrupted write, manufactured | **EXCEEDED** — real child, `SIGKILL`, precondition asserted |
| `T3` | stale temp at selection time | MET |
| `T4` | successful completion, contents | **EXCEEDED** — and it caught a real regression |
| `T5` | atomic publication preserved | MET — plus `flush()`+`fsync()` |
| `T6` | exclusion derived, not retyped | MET |
| `T7` | mutation reach proven | **EXCEEDED** — both directions, each with a power argument |
| `T8` | must not fire on a correct run | MET |
| `T9` | concurrent writers | **UNEVIDENCED** — property holds, nothing asserts it |
| `T10` | no accumulation on success | MET |
| `T11` | in-progress ≠ stale-foreign | MET — with finding **F1** |
| `T12` | R5 coupling stated with numbers | MET — with finding **F2** |
| `T13` | no new tracked launcher | MET |
| `T14` | regression population named and matched | **PARTIAL** — at-risk population clean; full run killed |

### `T1` — exceeded, because it is a property rather than a list

The repair renames the temp to `.mnv-incomplete.<product>.<token>.partial`, and rests on **two
independent guarantees, either sufficient**: the **leading dot**, which `glob` will not match unless
the pattern itself begins with one, and the **non-npz suffix**, which covers a consumer that bypasses
globbing with `os.listdir` + `endswith(".npz")`.

I required proof against the actual glob strings the launchers pass. The leading-dot property makes
that enumeration unnecessary, which is strictly stronger. Verified by execution:

```
glob.glob('*')            -> ['block5d_knobs.npz']          (the temp is NOT returned)
glob.glob('*.npz')        -> ['block5d_knobs.npz']
glob.glob('block5d_*.npz')-> ['block5d_knobs.npz']
glob.glob('*.np[yz]')     -> ['block5d_knobs.npz']
os.listdir + endswith npz -> ['block5d_knobs.npz']
bash `ls block5d_*.npz`   -> (empty)
```

**Scope correction (F4, not live).** The producer comment says the write is invisible to
*"`*.npz`, `block5d_*.npz`, `*.np[yz]` and even `*`."* True of `glob.glob` and of shell globs; **not**
true of `pathlib.Path.glob('*')`, which returns the dotfile — measured. It is not live: no production
module selects slabs or bank files with `Path().glob`, `rglob`, `iterdir` or `os.scandir` (swept; the
only hit is a test file), and `Path().glob('*.npz')` excludes it correctly anyway, as does guarantee
(2). But the claim is interpreter-specific and the comment states it universally —
`a-universal-claim-implemented-as-the-diff`, and the reason
`shell-semantics-must-be-measured-on-the-target-interpreter` exists. **Requirement: qualify the
claim to the globbing implementations it holds for, or a future consumer will pick the one idiom it
does not cover.**

### `T2` — exceeded

A real child process writes a partial payload, `flush`es, `fsync`s, then `os.kill(os.getpid(),
SIGKILL)`. No handler of any kind runs, which is the modelled hazard. Beyond what I required: the
arm **asserts its own fixture precondition** (`wrote-partial` on the child's stderr) and that the
child died rather than returned, so a fixture that missed the hazard cannot read as a passing guard
(`a-fixture-that-misses-the-hazard-looks-like-a-failed-guard`); it checks a **bash** glob as well as
Python's; and it confirms the directed scan still reports the file as `INCOMPLETE write` and not as
`UNDECLARED`.

The record also states that the first version of the stand-in took a *path* and failed, because the
producer passes a *handle* — "the fixture disagreeing with the producer rather than with the world."
That is the right diagnosis and the right fix.

**Not required by me, and an improvement:** `except Exception` was widened to `except BaseException`,
because a `SIGINT` mid-write *is* an interrupted write and under `Exception` it left the temp behind.
`SIGKILL` remains covered by the name, not by cleanup, which is the point.

### `T4` — exceeded, and it did the job it was written for

ARM3 asserts the product is present, **loads, and has its contents intact** (`xs` array-equal,
`seed == 7`), that the directory holds *exactly* the published products, that the glob still selects
all of them, and that `check_slab_population` reports the right counts. That is the contents
assertion `T4` was specified around rather than an existence check.

**And it caught the exact inverted repair `T4`/`T5` were written for, on its first run.**
`np.savez_compressed` **appends `.npz` when given a name that lacks it** — verified independently:
asking for `x.partial` produces `x.partial.npz`, while a file **object** gets no suffix. So the first
attempt, which renamed the temp to `.partial` while still passing a *name*, wrote the arrays to a
fourth filename and `os.replace` published the empty `NamedTemporaryFile` placeholder. Every reader
got `EOFError: No data left in file`. A repair that made incomplete writes unselectable by breaking
publication is precisely the failure the arm exists for, and it fired. The fix — write through the
open handle — is correct and I verified the handle-written file loads.

### `T5`, `T6`, `T7`, `T8`, `T10`, `T13`

- **`T5`** `os.replace(tmp, path)` with `dir=os.path.dirname(path)` is unchanged, so publication is
  still a same-directory rename and still atomic; the repair calls this out as deliberately
  untouched. `flush()` + `fsync()` were added before the rename, which I did not require and which
  closes a crash-after-rename window.
- **`T6`** `incomplete_name()` and `is_incomplete_write()` are the single source, and
  `z_precursor.py:217` switched from `endswith(IN_PROGRESS_SUFFIX)` to
  `producer.is_incomplete_write(p)`. Derived, not retyped.
- **`T7`** Two mutation arms, one per direction, each carrying an explicit power argument in its own
  docstring — *"if it is not, arms 1 and 2 are asserting something that was never capable of being
  false and they prove nothing"* — which is the gates-that-cannot-fail concern stated by the author
  against the author's own work. The pre-repair-naming arm additionally carries a **positive control
  on its restore**, so a leaked mutation cannot silently weaken later tests.
- **`T8`** `test_the_FRESHNESS_check_does_not_read_a_temp_as_a_product` is the over-fire direction: a
  temp must not refuse a genuinely fresh namespace.
- **`T10`** ARM3's exhaustive directory assertion covers it.
- **`T13`** No tracked `.sh` added; `sbatch_uthrow_run_5d_fast.sh` is modified, not new, so the
  216/217 launcher census is untouched. (That census failure is pre-existing on `main`.)

**Worth singling out, because it is the subtlest thing in the delta and nobody asked for it.** Two
checks were **neutered by the repair itself** and both were caught:

1. `check_slab_population` used to find in-progress temps *in the consumer's own glob*. Post-repair
   they are glob-invisible, so reading them from `matched` would report nothing — "a diagnostic that
   worked only while the defect existed." The scan was made **directed** (`os.listdir`) instead.
2. `test_uq_remediation.py:151` asserted `Path(td).glob("*.tmp.npz") == []`. After the rename that
   glob is empty **whatever cleanup does**, so the assertion would have passed vacuously. It was
   repointed to the producer's own predicate plus an exhaustive `iterdir()` assertion.

Both are `a-lower-layer-must-not-re-read-my-own-repair`: the repair narrows the state a check reads,
and only *correct* runs break. Finding them required looking for checks whose operand the repair had
changed, which is not a step anyone prompts you to take. I confirmed `test_uq_remediation.py` is
**not** sha-frozen into any state receipt, so editing another lane's test file here does not void a
gate binding — the trap `tests/conftest.py:224-231` documents.

---

## Part 2 — Findings

### F1 — `find_incomplete_writes` converts "could not look" into "nothing there"

`except OSError: return []`. A directory the scan cannot read returns the same answer as a clean
one. Demonstrated:

```
readable directory containing one temp -> ['.mnv-incomplete.block5d_knobs.npz.t1.partial']
same directory, chmod 000              -> []            <-- identical to clean
```

And the same branch swallows a second case. `check_slab_population` derives the scan directory as
`os.path.dirname(pattern)`; if a pattern ever carries a **wildcard in its directory component**,
that dirname is an unopenable literal and the scan silently reports nothing:

```
pattern                         .../tmpXXXX/*/block5d_*.npz
os.path.dirname(pattern)        .../tmpXXXX/*
find_incomplete_writes(dirname) []
  ... but the temp IS in the selected directory
check_slab_population(...)   -> PASSED, with an incomplete write present
```

**Latent, not live: every slab pattern in the tree has a fixed directory** — all **18**
distinct patterns the launchers pass, across **three** glob-bearing flags, plus all four
`ARM_LAYOUT` globs, enumerated rather than sampled.

*(My first enumeration here said "ten, across `--block-slabs`/`--throw-slabs`". That was short:
`check_slab_population` is called on `args.combine` as well as `args.block_slabs`
(`unified_throw_cov.py:735,738`), so `--combine` is a third selection surface feeding the same
function, and including it takes the population from 10 to 18. The verdict is unchanged — all 18
are fixed-directory — but the population was wrong before it was right, which is
`an-expected-count-selected-which-rows-i-kept` inside my own document, caught by re-running the raw
grep against a widened flag set rather than by re-reading my table.)*

**Severity is bounded and I want to be exact about it.** Joseph's primary requirement — *incomplete
outputs must never match the consumer's input selection* — is **not** affected in either case,
because it rests on the **name**, not on the scan. What degrades is `T11`: the operator is not told a
task died. This is `a-monitors-tally-of-zero-may-mean-it-could-not-look`, one layer below the place
the repair correctly identified the same shape (it fixed the glob-derived scan precisely because it
would report nothing). **Requirement: the scan must distinguish "no incomplete writes" from "could not
look", and the directory it scans must be the directory the glob actually selects from.**

### F2 — two withdrawn figures are now in a production code comment

`unified_throw_cov.py:144`: *"the block arm's 12 h ceiling is 1.39x its observed maximum of 8.6389 h
**over 74 tasks**, with a **7.7x** runtime spread."*

`8.6389` and `1.39x` are confirmed — I reproduced both to four decimals and showed the maximum is
invariant across all three candidate populations. The other two figures come from the `n`/`mean`
columns the author has now **withdrawn as unreconcilable**:

```
MAX                        8.6389 h   CONFIRMED
all states    n=83  mean=1.1017 h  ->  max/mean = 7.84x
COMPLETED     n=72  mean=1.2695 h  ->  max/mean = 6.80x
claimed       n=74  mean=1.1213 h  ->  max/mean = 7.70x
```

**`7.7x` reproduces only from the withdrawn mean**; my two populations give 7.84× and 6.80×. So a
figure retired in coordination traffic has landed in a durable production artifact —
`a-withdrawal-must-reach-every-site-that-states-the-rule`, and **the second instance of that exact
shape in this review round**, the first being the marker at `:33-35`. A withdrawal that reaches the
message and not the code has not happened. **Requirement: the comment carries only the two figures
that survive re-measurement, or names the population for the other two.**

### F3 — `T9` is unevidenced

No arm asserts the concurrency property. It **holds**: `_atomic_savez` still uses
`NamedTemporaryFile`, so two writers of the same product get two distinct tokens. But nothing tests
it, and the tempting simplification — dropping the token for readability, giving
`.mnv-incomplete.<product>.partial` — would remove the safety with every existing arm still green.
The criterion asked for the assertion precisely because the property is invisible until it is gone.
**Not met; it is the one gap.**

---

## Part 3 — `T14`, the regression: PARTIALLY established, and I am not rounding that up

**The full-suite run at `05cf2d00` does not exist.** I started it and the system **killed it at
roughly 30%** under memory pressure (63 MB free, load 5.4, with peer sessions working). A killed run
is not a result and its partial dot-line is not a count, so I am not quoting one. I did not retry:
re-running a 3,000-test suite on a machine that just ran out of memory would risk other sessions'
work for a number I can get more cheaply and more precisely.

**What I ran instead is the correctly-scoped population, and it is arguably the better measurement.**
Only **two** suites in the tree import the changed modules (`unified_throw_cov`, `z_precursor`) — and
they are exactly the two the repair touched on the test side:

| suite | `77a4af38` (control) | `05cf2d00` (tip) | delta |
|---|---|---|---|
| `test_uq_remediation.py` | 237 tests, `failures=3, errors=2, skipped=2` | 237 tests, `failures=3, errors=2, skipped=2` | **none** |
| `test_z_precursor.py` | *(does not exist)* | **111 tests, OK, rc 0** | +5 over `10eb1bac`'s 106 |

The five named failures in `test_uq_remediation.py` are **identical** at both shas: `comm` gives zero
only-at-tip and zero only-in-control. So the repair introduces no failure and fixes none in the only
population that can be affected by it, and the suite it rewrote an assertion in still has exactly its
pre-existing failure set.

**The honest boundary.** This establishes that the changed modules' dependents are clean. It does
**not** reproduce the full-suite figure, so the `14 / 2895 / 6` control stands unmatched at
`05cf2d00`. Whoever needs the full number should run it on an unloaded machine with
`--continue-on-collection-errors`; `T14`'s requirement to name the runner, root, flags and both
endpoints applies to that run, not to this one. I am labelling this population *"suites importing the
changed modules"* rather than *"the regression"*, because they are different populations and
collapsing them is the error this criterion exists to prevent
(`a-right-pattern-over-wrong-rows-is-undetectable`).

## Part 4 — The reframed probe justification, which is the one thing I was asked

The reframe — *first-execution mechanics validation of code that has never run on the scheduler,
saying plainly that its runtime and memory add nothing to a 2,356-observation record* — is **sound in
class and is the right justification. It is not yet a justification, for one structural reason and
with one self-undermining risk.**

**It is the right class, and this project has the receipts.** There are defects only a real
submission can reach: `sbatch` runs a **spool copy**, so `$0` and `BASH_SOURCE` resolve to the spool
path and no local test sees it; Slurm **rewrites array brackets** — a declared `1-100` was observed
as `3-100` under throttling, truncating the *low* end, which is exactly where an `--expected-ids`
population check would be fooled; and the batch environment is not the login environment, which is
where the two-root `${VAR:?}` forms and the ROOT/TF interpreter split actually bite. So
"mechanics only a submission establishes" is a real and non-empty set.

**The structural gap: it must enumerate those mechanics, each with the reason a local test cannot
reach it, and each with what FAILURE would look like.** A probe that "validates mechanics" otherwise
passes whenever it completes, which is a gate that cannot fail (`BEN-032`/`BEN-025`) — the shape this
campaign catalogues. Name what would count as the probe failing; if nothing would, it is an
execution, not a validation.

**The self-undermining risk, and this is the sharpest thing I can say: a first-execution validation
must not exempt the admission gate from first execution.** `z_precursor_admission.py` is the module
that refuses this campaign at 558.42 against 500, and it has never run on the scheduler either. If
the probe is submitted without passing through its own admission path — its committed task-hours
computed, its spend basis declared, a decision recorded — then the component whose first execution
matters most is the one the probe skips. Run the other way, admitting the probe through its own
instrument is the single highest-value mechanics test available. **Requirement: the probe's record
shows its own admission report, with its committed cost and the decision.**

**The "adds nothing" line is honest and must be made load-bearing in the NOT-CITABLE direction.**
If the probe's runtime and memory add nothing to the record, then the probe must be explicitly
**not citable for a `--time` or `--mem` value**, at the top of its record and not beside the number.
Someone will reach for "we ran it and it took X" as the basis for cutting `--time`, and
`a-verdict-column-outranks-the-caveat-beside-it` says which of the two wins.

**One point in the reframe's favour that has not been claimed.** The 2,356 observations are of the
**pre-repair** code. The repairs added guard code to the dump arm (full guard parity, both roots
mandatory via `:?`) and moved the namespace contract inside the guarded producer. Those costs are
small relative to the payload, so the historical record still bounds the resources — but strictly it
bounds the **payload**, and the new guard and contract path has no measured cost at all. That is a
modest, true addition to the mechanics case, and it is a better argument than the resource claim it
replaces.

**Authorization is unchanged by a reframe.** `R4` is suspended, Gate 2 is FAIL, `R5` is a prohibition
and an accounting boundary rather than an allowance, and a probe is a **new submission**. Reframing
the scientific justification does not alter the authorization status, and the record should name the
route it claims rather than leaving it inferred.
