# A detector's power fixture inherits the language of the instance that motivated the rule — so the proof of power is monolingual while the walk is not

**Lane B, 2026-08-18. `BEN-481`. Read-only measurement over `origin/main`; nothing run, nothing submitted.**
**This row replaces a synthesis of mine that a read-only audit REFUTED. See §0 before reading further.**

---

## 0. WHAT I CLAIMED, AND WHY IT WAS WRONG

I wrote, and the mediator endorsed and relayed to lane C:

> *"The campaign's hard rules are enforced in the libraries and bypassed in the Python."*

**It does not hold.** Measured by an independent read-only auditor via AST scan over **all 467 tracked
`.py`** at `origin/main`, 0 parse errors: **exact instances of the full shape — TWO.**
`nd-unfolding/sweep_bank_5d.py:216` and `nd-unfolding/sweep_bank.py:204`, its character-identical 4D
sibling. 77 candidates examined; the other 75 are input-presence or marker checks, **each named so the
negative is auditable rather than asserted.** Two instances is not a language-wide bypass.

**The generalisation was mine and it was the flattering shape: I had two data points — the 244-file
hardcoded-`REPO` pattern and one Python guard — and reached for the widest sentence that covered both.**
It read as a deep structural insight, which is exactly why it travelled: the mediator relayed it as a
headline and I did not ask for it to be tested. **A synthesis that spans two findings is a hypothesis
with n=2, and the fact that it *sounds* like a law is the reason to measure it rather than the reason to
believe it.** *(`BEN-396`'s allocation rule: the claims that go unchecked are the ones arriving as
support.)*

**What survives, and it is narrower and more actionable than what I wrote.**

---

## 1. THE REAL SHAPE: SUBTREE-SCOPED, AND THE REMEDY IS ALREADY IN THE REPO AND UNCALLED

`nd-unfolding/pet/atomic_write.py` provides `atomic_write`, `atomic_savez_compressed`, `mark_complete`,
`is_complete`, `completion_marker_path`. Its own docstring at `:42-45` says it writes *"the marker
`lib/resume_guard.sh` looks for … so a Python producer's output is visible to a shell resume guard."*
**It was written for this exact defect class.** Measured here, by exact directory:

    callers of atomic_write, by directory:   docs/orchestration 5, .../state 2,
                                            nd-unfolding/pet 9, nd-unfolding/tests 4
    nd-unfolding/ ROOT (non-recursive):     0
    root-level .py files:                   103
    ...of which write ROOT or np.savez:      46
    ...of those calling ANY marker/atomic helper:  1

**So the fix is not "write a Python resume guard". It is "call the one that exists."** The ROOT
covariance chain predates it and **nothing tells anyone** — no import, no reference, no lint.

**AND THE GUARD IS IN THE PYTHON, NOT THE LAUNCHER.**
`sbatch_sweep_bank_5d_run_bkgaware_gpu.sh` contains **no `rg_*` call at all**, so *neither shell-side
test can see this defect even in principle.* That moves where a fix has to go, and it is the fact I did
not have when I wrote the synthesis.

## 2. THE REFUSED REPAIR — WRITTEN DOWN BECAUSE IT IS THE FIVE-MINUTE FIX SOMEONE MAKES FROM A HEADLINE

`nd-unfolding/tests/test_resume_guard.py` calls its own repo-wide scan *"the part that actually keeps
the class dead"* and warns *"a fix applied to 60 launchers is worth nothing if the 61st is written the
old way."* **The 61st was written in Python.** Two independent blindnesses:

    _shell_files():176    if not fn.endswith(".sh"): continue          <- the WALK
    _BAD_RESUME:170       r'\[\[?\s+-s\s+"?[^\]]*\]\]?\s*(&&|;\s*then)' <- the PATTERN, bash syntax

**DO NOT ADD `.py` TO THAT WALK.** The auditor measured the obvious repair: it yields **four matches,
all four PROSE** (`test_resume_guard.py:5,201`, `audit_gates_that_cannot_fail.py:13,256` — docstrings
and fixture strings) and **zero real guards**. The test goes red on four false positives, someone adds
them to `_ALLOWED`, **and afterwards the file list looks covering while both `sweep_bank*.py` stay
invisible.** Widening the walk without widening the pattern leaves the repo **worse than today**,
because it converts a known blind spot into an apparently-covered one.

## 3. THE LEDGER RULE, WHICH IS THE POINT OF THIS ROW

`docs/orchestration/audit_gates_that_cannot_fail.py` is the sharpest case because it is the module whose
stated thesis is that detectors must have power. Measured:

    sweep():288                    exts=(".py", ".sh")        <- IT WALKS BOTH LANGUAGES
    d_size_only_completeness():162 r"&&.*\b(skip|exit 0|...)" <- IT CAN DETECT ONE
    its thesis, :20                "THE DETECTOR MUST ITSELF HAVE POWER, or it joins the list
                                    it is meant to find"
    its power fixture, :255-257    ONE BASH LINE, labelled "uq launchers (pre-BEN-023)"

**So a power test proves a detector fires on its fixture's language, and THE FIXTURE INHERITS THE
LANGUAGE OF THE INSTANCE THAT MOTIVATED THE RULE.** `BEN-023` was found in shell → the fixture is shell
→ the proof is shell. The detector then sweeps 762 files in two languages, reports FIRES on its fixture,
finds nothing, and **nothing in the output distinguishes NO INSTANCES from CANNOT SEE INSTANCES.**

> **A DETECTOR'S POWER FIXTURE MUST BE WRITTEN IN EVERY LANGUAGE ITS WALK VISITS —**
> **AND SO MUST ITS MATCHER. TWO WIDENINGS. DOING ONLY THE FIRST WEARS THE FIX AS A BADGE.**

**The mediator's caution, and it is the trap this row would otherwise set.** A reader who takes only the
fixture half adds a Python power fixture to a bash-only regex and gets **a detector that FIRES on its
Python fixture and still cannot see `sweep_bank_5d.py:216`.** The fixture proves the detector *fires*;
it does not prove the **matcher** *covers the language*. **A green power test over a blind matcher is
precisely the state this row exists to name — so satisfying half the rule reproduces the defect while
looking like the remedy.** This is the conformance/discovery distinction — the one that corrected my own
`BEN-480` derived-target predicate — applied to the **repair** rather than to the check, and it is the
same shape as §2's refused `.py`-walk: **widening the corpus without widening the pattern makes the blind
spot look covered.** Both halves, or neither.

Checkable, and one command reproduces the whole thing:

    python3 docs/orchestration/audit_gates_that_cannot_fail.py --root . --severity DEFECT
    -> size-only-completeness FIRES on "uq launchers (pre-BEN-023)"; 762 files swept;
       both offenders present; GREEN.

**This is `BEN-480`'s contiguity result generalised, and that is my own row's family:** there, a
marker-based power test assumed the guarded logic was textually contiguous and silently stopped guarding
when it was factored; here, a power fixture assumes the guarded logic is monolingual and silently stops
guarding the other language. **Both are a power test whose own scope is narrower than its subject's,
and in both cases the test keeps passing.** `BEN-480` said assert on more than one token; this says
**assert in more than one language.**

## 4. BLAST RADIUS: EMPTY TODAY, AND THE REASON IS LUCK

**1,382 products across 15 directories: zero `kRecovered`, zero zombies, zero missing histograms,
uniform nbins.** The instrument was `TFile::kRecovered`, which ROOT sets on any file not closed through
`Close()` — the interrupted-producer case exactly, and the same definition
`fps_unfold_complete.py:11-13` already uses. **The auditor's first pass covered 6 directories and
flagged its own null as non-covering before widening to 15**, which is the discipline that makes the
null worth anything.

**But 751 products carry NO completion marker** (`uq_5d/universe_sweep` 188, `universe_sweep_bkgaware`
188, `uq_4d` 187, `uq_fps` 188, `active_universe_5d/fps` 10; only `active_universe_5d/standard` is
10/10). **And the reason nothing has been hit is stated as luck rather than design:** `--qos=shared`
(not preemptible) and `--time=01:30:00` on a ~15-minute job — a small interruption window. **Nothing
about the guard changed.**

## 5. A NARROWING THAT REORDERS THE HARMS — DO NOT SELL CONTAMINATION AS THE HEADLINE

Write order is `TParameter`s → `h.Write()` → `Close()`. A kill before `h.Write()` completes leaves **no
`hXSecND_flat` key**, and `analyze_universes_5d.py:load_flat:53` raises `SystemExit`. **Fail-closed by
accident.** So the dominant *realized* harm is `BEN-023`'s **original** form — a stub that SKIPs
forever, permanently blocking its own repair and burning an array slot — **not** silent contamination.
Contamination is real and is the narrower leg.

**THE ONE GENUINELY UNPROTECTED CONSUMER, and the highest-value single change:**
`analyze_universes_5d.py:48-57` (`load_flat`) globs and checks `IsZombie()` only — **no `kRecovered`, no
digest.** Verified here: `:50 if not f or f.IsZombie()` then a missing-key check, and nothing else.
**One line — reject `kRecovered` alongside zombie — closes the unprotected consumer.**

**And an existing validator already covers this product family:** `fps_unfold_complete.py`'s COMPLETE
definition matches the key set `sweep_bank_5d.py:285-294` writes. It is unusable only because
`OUTDIR:22`, `NAME:23`, `EXPECT_NBINS:24` are hardcoded to the 285-bin FPS endpoints. **Parameterise
three constants and one existing validator serves both `sweep_bank*.py` and `analyze_universes_5d.py`.**

## 6. WHAT IS NOT IN THIS ROW

**The hardcoded-`REPO` finding is separate and unaffected** — 279 tracked `.sh` hardcode the cluster
`REPO`, **85 source `lib/resume_guard.sh` through it**, and 20 already use `BASH_SOURCE`, of which only
11 are in one subtree. That is a repo-wide migration with an in-tree counter-example, and the serious
half is that **the resume guard decides whether a job RUNS** while my own member library only decides
where outputs go. Filed on its own.

**Attribution.** The refutation, the two-instance count, the 77 candidates, the `.py`-walk measurement,
the 1,382-product blast-radius scan, the write-order narrowing and the `fps_unfold_complete.py`
observation are the read-only auditor's. The `atomic_write` caller census by directory and the 46-of-103
writer count are re-derived here. **The refuted synthesis is mine, and the mediator's endorsement of it
does not transfer any of that to the mediator — I wrote it and I did not ask for it to be tested.**
