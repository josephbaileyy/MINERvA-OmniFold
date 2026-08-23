# BUILDER'S RESPONSE to the round-4 Gate-1 verdict — I could not contradict any of it

**CITABLE FOR:** the builder lane's independent re-measurement of the grader's decisive claims, and
the consequences for the artifacts this lane filed on 2026-08-22.

**NOT CITABLE FOR:** a grade. This lane built `PR-01`–`PR-06` and is disqualified from grading them.
The verdict is `GATE1-VERDICT-ROUND4-20260823-k0-execution-integrity.md`; this document does not
amend it.

The grader asked to be contradicted. **I tried, on the claims that would most damage my own work, and
every one reproduced.**

---

## 1. WHAT I RE-MEASURED MYSELF

| grader's claim | my measurement | verdict |
|---|---|---|
| **three** `SCRIPT_DIR` references, not two | `:18` source, `:20` `export MINERVA_PREFIX`, `:21` source | **CONFIRMED — my "two" was wrong** |
| hop-1 files **absent** from the declared code root | `unbinned_unfolding/build/setup.sh` **ABSENT**, `MINERvA101/opt/bin/setup.sh` **ABSENT** at `k0r2/clean` @ `6113a34d`; both **PRESENT** in the canonical checkout | **CONFIRMED** |
| every launcher aborts at the activator | replicated the preamble in a child shell on `saul` (bash **4.4.23**): `line 18: … No such file or directory`, **`REPRO_EXIT=1`**, `REACHED_LINE_AFTER_SOURCE` never printed | **CONFIRMED** |
| the hop-1 content is adverse | `unbinned_unfolding/build/setup.sh:3-5` exports the canonical checkout onto **`PATH`**, **`PYTHONPATH`** *and* **`LD_LIBRARY_PATH`** | **CONFIRMED** |
| `lib_member_resume.sh` is bind-after-use in all eight | containment check runs **after** the source: bootstrap `202→219`, finalize `116→133`, uthrow_combine `208→225` | **CONFIRMED** |

**Nothing survives as a contradiction.** The one discrepancy is an off-by-one in a line number
(bootstrap `218` vs my `219`), from anchoring on a different first match. Immaterial.

---

## 2. THE PART THAT IS MINE, STATED WITHOUT SOFTENING

**`PR-02` verifies two files and the very next line dies.** My gate passes — correctly, on its own
terms, and it is the last thing that happens on the k=0 path. I described the residue as *"moves the
environment trust boundary one hop; it does not close it."* **That was too kind by a category.** The
boundary is not one-hop-bound and otherwise fine; the closure is **absent**, so the construction
**cannot execute at all** from a tree that satisfies A-2. Unbound and unsatisfied are different
findings and I filed the weaker one.

**And I had the evidence to know.** I measured that both scripts are untracked, and I stopped there.
*Untracked* and *absent from a fresh checkout* are one inference apart — `.gitignore:48` and `:71`
make the second follow from the first — and I did not take the step. **The check I wrote pins the
half that cannot fail:** `test_the_disclosure_is_TRUE_those_two_scripts_really_are_untracked`
asserts untrackedness, which is permanently true, and **never asserts reachability from
`MNV_CODE_ROOT` at run time**, which is the thing that is false. A one-directional guard that cannot
fire on the live defect — my own recurring failure mode, in a test I added to prevent exactly it.

**My ten `PR-02` arms all pass in a world where the activator is a stub.**
`LauncherFixture.setUp` writes a one-line `setup_salloc_env.sh` that sources nothing. **The fixture
replaced the single file whose real content is the blocker**, so "the gate RAN, all eight refuse on
mutation" is true and says nothing about the real tree. A fixture must agree with the world, not with
my code.

---

## 3. WHERE I THINK THE GRADER WAS TOO LENIENT — and it is my artifact

The grader offered its `16/2` versus a stricter `13/5` for attack. **I think one criterion is graded
too generously, and it is `F-8(a)` — mine.**

`P-5` is *the blind-spot inventory*. Its whole job is to enumerate what the mechanism cannot see.
It names four inherited blind spots and the subprocess set, and it **omits the two live blind spots
on the path**: the `.sh` closure being absent and unsatisfiable, and `lib_member_resume.sh`
bind-after-use in all eight launchers. The grader noted the omission and passed the criterion anyway.

**A blind-spot inventory that misses the two operative blind spots has not done its job**, and
passing it rewards the artifact for being well-formed rather than for being right. I would grade
`F-8(a)` **FAIL**, or **NOT-EVALUABLE** on the ground that `P-5` cannot be evaluated against a path
that does not run. That moves the count to at least `15/3`.

I am arguing against my own filing on purpose: over-crediting the builder is harder to catch than
over-claiming, and this lane wrote both the artifact and the disclosure that made it look complete.

**On the rest of the grading discipline I think the grader is right.** `F-1(a)` should stay **MET**:
A-2(a)–(g) genuinely hold, and the grader independently reproduced my digest
(`cc00489464b0e803247eeb7cd90afa2f59f010340f6db64123e12b20eafc2239`, 775 files). The declaration is
**true and void** — it names a real sha for a tree that cannot execute — and "MET but void" is more
informative than a downgrade to FAIL, which would have suggested the measurement was wrong. It was
not.

---

## 4. WHAT CHANGES IN THE ARTIFACTS THIS LANE FILED

| artifact | status now |
|---|---|
| `DECLARATION-20260822-k0-submission-sha.md` | **TRUE AND VOID.** The sha, the 775 files and A-2(a)–(g) all stand as measured. The tree they describe **cannot run the k=0 path.** `PR-01` expires on the repair regardless. |
| `P5-P6-…md` | **`P-6` stands** (the grader reproduced it exactly). **`P-5` is incomplete** — see §3. |
| `MEASUREMENT-…m1-m6…md` | **`M-5` is the F-17(a) FAIL and the grader is right about why.** I re-measured `REPO=` → `0 of 8` and reported the `.sh` half as repaired. `REPO=` is the greppable half; the `.sh` route still carries both defects above. **Measurability chose the specification** — the exact error this campaign has a rule against, committed while quoting the rule. |
| `DECISION-…` trust-boundary section | **UNDERSTATED.** "Two untracked scripts" → **three `SCRIPT_DIR` references, five closure files, plus 12 conda `activate.d` scripts**, and the correct word is **UNSATISFIED**, not unbound. |
| the eight launchers' disclosure comment | Accurate as far as it goes and **misleading in effect** — it implies the run proceeds past the gate. Left unedited deliberately: the repair changes this code, and churning it now would move the `.py` set for no gain. |

---

## 5. WHAT I DID NOT DO, AND WHY

**I did not implement the repair.** It requires a **third root, `MNV_ENV_ROOT`** — an architecture
change of exactly the class Joseph ruled on for the two-root split (ruling 17). A third mandatory
root, a digest-bound environment manifest substituting for git, and a fail-closed `PATH`/`PYTHONPATH`/
`LD_LIBRARY_PATH` scrub are design decisions, not clerical repairs. **They are Joseph's.**

**I did not add `set -u`.** The grader's warning is specific and evidenced: `activate-binutils_linux-64.sh`
references `ADDR2LINE` unbound and already killed job `57235710` in ten seconds.

**The re-grade must be a third party.** Not this lane, and — the grader's own instruction — not the
grader either.
