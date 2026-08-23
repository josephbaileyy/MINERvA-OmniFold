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

## 3. WHERE I THOUGHT THE GRADER WAS TOO LENIENT — **I WAS WRONG, AND I WITHDRAW IT**

> ### WITHDRAWN 2026-08-23. The grader declined, and its reason is better than my objection.
>
> **The argument that decided it — and it is one I should have reached myself, because this repo
> already has a rule for it.** `P-5` is a register of **blind spots that must be DISCLOSED because
> they cannot be closed.** `lib_member_resume.sh` bind-after-use is **not a blind spot**: it is a
> repairable ordering defect with a known one-hunk fix — *move the `if` above the `source`* — and
> **I already shipped exactly that fix for `_mr_rg` in `finalize`.** Filing it in `P-5` would convert
> a defect that has a remedy into a permanent disclosure. **A caveat standing in for a fix.**
> `F-2(a)` is its correct home precisely because `F-2(a)` FAILS, gets repaired, and the launcher
> stops being wrong; `P-5` would have absorbed it and the launcher would have stayed wrong with
> paperwork attached. **My objection would have made the package worse while looking stricter.**
>
> **And the procedural half is right too.** §4 enumerates `P-5`'s content — four named items — and
> `F-8`'s row asks for those plus the subprocess enumeration with each child wrapped or uncovered.
> My document delivers all of it, and the absent `.sh` closure falls inside named item 4. Failing a
> criterion for omitting something the contract does not name is **selecting the criterion after
> seeing the evidence**, which is the mirror of what this contract exists to prevent.
>
> **My `NOT-EVALUABLE` alternative was the worse of my two suggestions**, and I now think clearly so.
> `P-5` is a static bench artifact that does not need the path to run, and *"the path does not run so
> nothing is evaluable"* propagates to `F-3(a)`, `F-4(a)`, `F-5(a)`, `F-6(a)`, `F-7(a)`, `F-13`,
> `F-15` — every bench criterion. §7.0.8 exists to kill that move. It would have turned a specific,
> locatable, repairable defect into a blanket *"cannot tell"*.
>
> **The grade stands at 16/2. What I was actually right about gets recorded as a repair, not a
> tally:** `P-5` **must gain the `PATH`/`PYTHONPATH`/`LD_LIBRARY_PATH` channel as a fifth blind spot
> BEFORE re-grade**, and the next grader must treat `F-8(a)` as **RE-OPENED at the new sha, never
> inherited**. It is mechanically re-opened anyway — `F-8(a)` is bound to the pinned sha and `PR-01`
> expires on the repair — but a document can be carried forward by hand, so it is said here.
>
> The grader also stated, unprompted, that it considered `FAIL` on my argument and declined it on the
> grounds above, and that the reason it landed on is not the one it would have given an hour earlier.
> That is recorded because a decline with a *new* reason is worth more than one that restates the
> original grade.

### The original objection, kept as the record



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

**I did not implement the repair.** (Refined in §6 and §7 below.) It requires a **third root, `MNV_ENV_ROOT`** — an architecture
change of exactly the class Joseph ruled on for the two-root split (ruling 17). A third mandatory
root, a digest-bound environment manifest substituting for git, and a fail-closed `PATH`/`PYTHONPATH`/
`LD_LIBRARY_PATH` scrub are design decisions, not clerical repairs. **They are Joseph's.**

**I did not add `set -u`.** The grader's warning is specific and evidenced: `activate-binutils_linux-64.sh`
references `ADDR2LINE` unbound and already killed job `57235710` in ten seconds.

**The re-grade must be a third party.** Not this lane, and — the grader's own instruction — not the
grader either.

---

## 6. `MNV_ENV_ROOT` MAY BE A SHARED TREE — measured, with one condition that decides it

I asked whether *"not a symlink"* rules out a bind mount or only the symlink form. The grader's repair
text was too broad and said so. **Measured independently by both of us on `saul` (bash 4.4.23), using
the exact `SCRIPT_DIR` expression from `setup_salloc_env.sh:2`:**

| arm | form | `SCRIPT_DIR` resolves to | transitive `source` | exit |
|---|---|---|---|---|
| **A** | real tree | the real tree | **OK** | 0 |
| **B** | symlink the **FILE** into a bare dir | **the bare dir** | *No such file or directory* | **1** |
| **C** | symlink the **DIRECTORY** | the link path | **OK** | 0 |

**So the prohibition is on ARM B only.** `BASH_SOURCE[0]` is the path *as sourced*, and bare `pwd` is
logical, so a directory link keeps the link path and `${SCRIPT_DIR}/unbinned_unfolding/…` resolves
**through** it. **A bind mount is strictly safer than ARM C** — it changes what is *at* the path
rather than redirecting the path. **`MNV_ENV_ROOT` does not have to be a real per-deploy directory.**

**Availability today is ARM C, not the mount.** `mount --bind` → **rc=32**, *"must be superuser"* —
unavailable to a plain `sbatch` job. `unshare -rm` → rc=0, so a bind inside a user namespace is
possible in principle, but the mount is private to that namespace and every leg would need wrapping.
(The grader notes it tested a login node only, and that its own first attempt read `sed`'s status and
reported rc=0 for a mount that had failed — the pipe-status trap, caught before it was filed.)

### The condition, and it would defeat the whole exercise if missed

**The only existing copy of the env closure lives inside the canonical checkout**, which carries both
checkout markers. **A shared env tree that is a symlink or mount OF THAT PATH resolves back into the
canonical checkout**, and `checkout_root_of` on the resolved path says so. The shared tree must be a
**real copy outside every checkout**, never a view onto the canonical one.

**And no mounting scheme touches the content defect.** `unbinned_unfolding/build/setup.sh:3-5`
hardcodes the canonical path into `PATH`, `PYTHONPATH` and `LD_LIBRARY_PATH` **by content**, so it
must be **regenerated** however the tree is presented.

**One consequence runs opposite to intuition:** a *shared* tree makes the digest manifest **more**
important, not less. It is mutable by an owner outside the deploy and can move between preflight and
the science invocation, where a per-deploy copy under A-2(g) cannot. And with a directory symlink
there are **two paths to the same bytes**, so the manifest's path keys must be expressed **the way the
activator expresses them** — a `realpath`-keyed manifest will not match what actually sourced.

---

## 7. CREDIT — corrected in my favour by the grader, and it goes further than either of us said

The grader volunteered that two of its findings were **not first discoveries**: the *"absent, not
merely unbound"* inference and the file-vs-directory symlink distinction were already in
`nd-unfolding/pet/g2_data_root_setup_salloc_env.template.sh`, written by whoever wrote that template.

**Checked, and the template is even further ahead than that.** It already contains, in prose,
essentially the entire diagnosis *and* the repair now being escalated to Joseph:

- **the three-reference count** — *"the failure list is three long, not one"* (`:13`);
- **absence by construction** — *"NO git worktree or frozen deployment will ever contain them …
  unavailable by construction"* (`:15-17`);
- **the file-symlink trap**, i.e. ARM B — *"`BASH_SOURCE[0]` is the path AS SOURCED, so symlinking
  that file into a bare data root makes `SCRIPT_DIR` the DATA root"* (`:11-12`);
- **the `set -u` kill**, with the job id — `57235710`, *"in 10 seconds"* (`:26-30`);
- **and the third root itself** — *"the right long-term fix is a separate `GATE5_ENV_ROOT`"* (`:22`).

**So the repair Joseph is being asked to design already exists as a written diagnosis in this
repository, for the Gate-5 path, and is referenced by nothing on the k=0 path.** The grader's actual
contribution — which is the hard part and is properly its own — was *noticing the template existed*
and applying it here. The **fixture-stub** observation is the grader's outright.

**This is the campaign's most expensive recurring failure in its purest form:** the answer was
committed, correct, and unrouted. `A-1`'s two-root split then reproduced the same conflation one level
deeper — it separated code from data and left the **environment** bound to the code root through
`SCRIPT_DIR`. **Whatever else the repair does, the template must be routed** so the next lane cannot
re-derive it a third time.

---

## 8. TWO DEFECTS IN THIS LANE'S OWN CORRECTIONS — and the rule they yield

The grader verified the landing by **diffing it against its own copy** rather than reading the
result, and found two defects. Both are at **edit seams**, both were in canonical records, neither
touched a finding. Both are repaired.

**Defect 1 — a truncated sentence that misrepresented a withdrawn position as live.** Replacing the
`See …` pointer in the `P5-P6` banner took the tail of the preceding sentence with it. Line 7 ended
mid-clause at *"— a blind-spot"*, and paragraph 1 then read *"The builder lane's own position **is**
that this should have failed `F-8(a)`"* — **present tense, unterminated, directly above its own
withdrawal.** A reader stopping after the first paragraph would have taken the objection as live.
**That is exactly the mis-citation the withdrawal exists to prevent.** Repaired: clause restored,
tense moved to `WAS`, explicit *"That objection is WITHDRAWN; see below."*

**Defect 2 — the front door asserted both framings, and the superseded one carried the
attribution.** My new leading text says the closure is **absent**, three references, five files. The
old sentence survived unedited below it: *"two UNTRACKED scripts … that no git-based check can
bind"*, attributed to Joseph. One field, both *unbound* and *unsatisfied*, both *two* and
*three/five*, with the superseded pair wearing the attribution and no marker. **Struck**, on the
grader's recommendation and this lane's agreement: Joseph's wording is preserved verbatim in the
`DECISION` record with the correction banner above it, and **the view does not need a second copy**.
A comma splice at the same seam is fixed.

### The rule, which is worth more than the two fixes

**Both defects are the same shape as the finding they document: a repair whose write-up re-creates
the thing being repaired.** The `P-5` fix laundered a sentence the way the objection would have
laundered a fix. The front door's fix left the understatement it corrected standing next to the
correction.

> **A correction needs its SEAMS checked, not just its content** — the *deleted* lines of the hunk,
> and whether the superseded text is still reachable. Reading the result does not catch either;
> **diffing the landing against the source does**, which is how both of these were found.

This is the third instance today of a write-up reproducing its own subject, after the harness that
excluded itself and the brief that re-created its own false hits. It is the normal case here, not an
unlucky one: every measurement runs over the repo and every finding is written into it.

---

## 9. A BETTER INSTRUMENT FOR A LANDED ARTIFACT — strip the declared edit, reproduce the digest

The grader closed by running a check neither of us had run, and it is stronger than what we had.

**Both of us had been verifying the landed verdict by INSPECTING THE DIFF** — "the only change is the
erratum banner". That is an argument about what a diff *looks like*. The better instrument:

```
strip the 20-line erratum banner (lines 3-22) from the landed file
  -> sha256 55e6b7710091405585cf50b7c0eebe8761cfa0a7cbbc0da1c0b3f2e92e79cdf4
  -> IDENTICAL to the grader's original artifact digest
```

**Reproduced independently by this lane, not accepted on report.** It proves the body is verbatim
rather than arguing it, and it fails closed: a single altered character anywhere in the 529 lines
changes the digest, whereas a diff can be read past.

> **The general form, worth using for any landed third-party artifact with a declared single edit:
> STRIP THE DECLARED EDIT AND REPRODUCE THE ORIGINAL DIGEST.** "The diff shows only my banner" and
> "the original bytes are still all there" are different claims, and only the second is what a reader
> of a relayed artifact needs.

**And the method symmetry both lanes agreed on:** *diff the landing against the source* is the
default **in both directions**. The grader found this round's two defects that way after a careful
read had passed over them; this lane should apply it to the grader's landings rather than trust its
reports, and has said so.

**One correction to §8's attribution, made in the direction that costs this lane something.** The
grader credits the sharper half of the seam rule to this lane — that the self-reference is *the normal
case* here rather than bad luck, because every measurement runs over the repo and every finding is
written into it, so the seam check is not tidiness but **the only instrument that covers the class**.
That framing is accepted, and it is recorded that **the observation itself came from the grader**;
this lane generalised a coincidence the grader had already spotted. Both halves belong in the record
and neither lane should be cited alone for it.
