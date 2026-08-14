# Session D (verifier) — verdicts, 2026-08-11

Three branches, always: **PASS / BLOCK / UNRESOLVED**. UNRESOLVED is a real outcome and must never be
re-read as the nearer of the other two. Where I tried to refute a claim and failed, I say so; where I was
right without evidence, I say that too.

**Tree state.** Measurements are stamped with the commit they were taken at. The working tree moved three
times during this session (`78296de` → `a0d8eb7` → `ceb2037`) because other lanes are committing into it.
`docs/analysis-note/` is byte-identical across all three (`git diff --stat 78296de ceb2037 --
docs/analysis-note/` empty), so the `\dead{}` measurements are unaffected. Corpus counts are stamped
`78296de`.

**Footprint.** Read-only outside `docs/orchestration/`. Every mutation ran on a copy: the note tests
against a `cp -R` of `docs/analysis-note/` under the job tmp, the p4 tests against a
`git clone --local --no-hardlinks` of the repo. `git status` shows no modification by me to any tracked
file; my only additions are the three documents in `docs/orchestration/`.

---

## V1 — `check_dead_containment.py` power test → **BLOCK**

Detail: `FINDING-20260811-dead-containment-evadable.md`. Ten mutations; nine behave.

`\dead {9.87654}` — one space, valid LaTeX, renders identically — is invisible to
`DEAD_RE = r"\\dead\{"`. Demonstrated end to end: checker `RESULT :: PASS` exit 0, `latexmk` exit 0,
`pdftotext` finds `9.87654` at line 1013 of the built `main_paper.pdf`. Both stages are blinded by the one
regex, because `struck_values` is derived through the same matcher, so the two-direction design does not
catch it.

Second, weaker exposure: with a real violation present, removing `pdftotext` from `PATH` yields `PASS`
exit 0. Documented behaviour, but `exit 0` cannot distinguish *the PDF stage passed* from *the PDF stage
did not run*.

Zero spaced instances exist in the tree today, so the containment currently holds. Not fixed — the note
lane owns the file.

## V2 — Session A's claim (a): *"the `\dead{}` build-scoping decision is CLOSED"* → **PASS, with two named exposures**

A's stated basis was that the branch landed and the test exists, and A correctly flagged that as the
BEN-088 shape. Checked properly:

- The test **passes** on the current tree, and it **did open the PDFs**: `pdftotext` present, all three
  PDFs present, positive control firing at 17/17 in `main_note.pdf` and 0/17 in each of paper and primer.
  So the stronger of A's two readings is the true one.
- The test **can be made to fail** in both directions it argues for (PT1/PT2 containment, PT3 positive
  control), plus closure resolution (PT4) and the PDF stage itself (PT5). It is genuine evidence.
- **The decision is closed.** Do not restate it as *"the containment is enforced"* without V1's two
  exposures: enforcement is evadable by an ordinary LaTeX idiom, and degrades silently to source-only
  where `pdftotext` is missing.

I attempted one further refutation and it failed: I suspected the paper's 4-file include closure was an
under-resolution hiding inputs. It is not — `paper_body.tex`'s seven `\include`-prefixed lines are all
`\includegraphics`, which `INPUT_RE` correctly does not match, and the paper's closure genuinely is
`main_paper → preamble, values, paper_body`. Recorded because a refutation that fails is evidence.

## V3 — Session A's claim (b): the `wakerctl` hash pin → **BLOCK (confirmed), and already filed by another lane**

A and the GBDT lane both ran `shasum` against the git object store — one instrument, twice. I ran two
others: `hashlib.sha256` on the working-tree file (`04d2e957…`, agrees), and sha256 of **every historical
blob** of the path along `origin/main`, which answers a different question — *was the pin ever valid?*

    04d2e957  2026-07-20  7e69926d  Cut over to interim Claude root        <- current
    bf459853  2026-07-20  442aee35  Send a 6-hour status digest email
    d7c6a215  2026-07-20  8c8775f8  Reconcile P3F PET queue latency wake   <- THE PIN
    6c5e97e6  2026-07-19  f54848dc  Notify the user by email
    c4ad82be  2026-07-19  32f62aad  Harden waker
    0b4c463c  2026-07-19  be4cd789  Replace hand-cloned wake watchers

The pin was correct when written — `d7c6a215` is `wakerctl.py` at `8c8775f8`, the receipt's own commit,
and `git log --all` on the receipt returns that one commit and no other. It broke twice on 2026-07-20,
the same day. Stale, not dangling.

**Verified as already filed, and therefore NOT re-filed by me.** `f27a302` carries the canonical
correction in `KNOWN_ISSUES.md` with the same history table plus byte counts (50283 / 53113 / 54600),
reached independently by the GBDT lane. My I3 adds nothing to it. The correct verifier outcome here is
corroboration and silence, not a second account.

## V4 — the BEN-084 attribution → **already corrected at `acb5555`; my reading and theirs agree**

BEN-084 justified `PROCESSED.txt` being a text file rather than a feature on the premise that editing
`wakerctl.py` would move a pinned sha. That premise was void by three weeks when it was written.
Verified `acb5555` inserts exactly that correction inline, flagged *"re-examine, do not inherit"* rather
than reversed, leaving BEN-084's other ground (new surface generates defects faster than it closes them)
untouched. Verified the correction's pointer resolves: `KNOWN_ISSUES.md:589`, the `wakerctl install-cron`
fail-open section. Nothing for me to add.

## V5 — Session A's claim: *"BEN-089 carries BOTH the peer-starvation mechanism AND the pin lapse"* → **BLOCK, in the specific form stated**

The conclusion A drew from it (do not re-file the pin) is right. The stated evidence is not.

- `2b50c3f` touched two files: `KNOWN_ISSUES.md` **+38** lines (the pin) and `FINDINGS.md` **+1** (the
  BEN-089 row).
- The BEN-089 row is **2629 characters about channel starvation and nothing else.** Searched for
  `8c8775f`, `50283`, `d7c6a215`, `04d2e957`, `442aee35`, `7e69926d`, `byte-for-byte`, `byte-identical`:
  **zero hits.** The pin lives in `KNOWN_ISSUES.md`, which is its canonical home and the right place
  for it.

A read the commit **subject** (*"BEN-089: … And the wakerctl pin lapsed 07-20"*) and attributed both
halves to the row. That is BEN-080 rule (1) verbatim: *a cross-lane status signal is not actionable until
you have read the commit body or diff, never the subject alone.* Low cost here — A's instruction to me
was correct anyway — but it is the second time in one session that A reached a right conclusion from
evidence that does not support it (see V6), and that pattern is the thing worth naming.

## V6 — Session A's BEN-range evidence → **BLOCK on the evidence; the assignment itself stands**

A wrote: *"`git show origin/main:…FINDINGS.md | grep -oE 'BEN-[0-9]{3}'` → 001-046, 060-089 present; max
089; **repo-wide grep returns the same set**."*

The first half reproduces exactly. **The second half is false.** Repo-wide returns the same set **plus
`BEN-100` and `BEN-105`**, both in `docs/orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md`,
which was untracked when A measured and is now committed. Session B has taken **100–105** and states in
that file that it is *"leaving 089–099 as a deliberate unused buffer."*

- **090–099 is genuinely free**: `grep -rn "BEN-09[0-9]" .` returns nothing. So A's assignment is safe and
  I am using **BEN-090** for V1.
- **But A assigned me the block B had declared a buffer**, and B's own new row `BEN-105` says *"the BEN
  namespace is exhausted inside its own documented ranges, and the next allocation by either rule is a
  collision."* Two lanes now hold different beliefs about what 090–099 is for. **No collision has
  occurred**; this is the BEN-080 shape caught by mechanism rather than attention, which is the outcome
  BEN-080 said the namespace was *not* protected by. A and B should reconcile it in one place.
- The repo-wide grep is the check the range rule depends on, and it was the half that was wrong. Stated
  plainly: A was right about 090–099 for a reason A did not measure.

## V7 — `test_p4_resume_integration.py` power test → **PASS**

Baseline 50 passed in 27 s, reproduced in a clean clone. Five mutations of the **code under test**, each
from a hard reset:

| mutation | result |
|---|---|
| M1 revert the PB2 explicit-null repair (`git checkout 1440b58^ -- p4_lib.py`) | **5 failed** — and exactly the right five: `test_null_schema_is_rejected_not_grandfathered`, `test_null_surface_record_…`, `test_both_fields_null_…`, `test_null_schema_with_a_valid_map_is_rejected`, `test_null_is_distinguished_from_absent_at_the_helper` |
| M2 widen `producing_closure` to the whole surface | **3 failed** — the over-rejection control fires |
| M3 invert the launcher's degenerate-closure guard | **1 failed** — exactly `test_launcher_aborts_on_a_degenerate_closure` |
| M4 launcher stops stamping `receipt_schema` | **5 failed** |
| **M5 NEGATIVE CONTROL** — comment appended to `p4_project_4d.py`, a non-producing module | **50 passed** — a change that must not stale an endpoint does not |

Every assertion I targeted can be made to fail, for its own reason, and the suite does not fire on a
change it is contractually required to ignore. **This test is evidence.** Two of its choices deserve
naming as good practice rather than being taken for granted: `test_launcher_aborts_on_a_degenerate_closure`
**executes** the extracted shell guard against four values instead of substring-matching it (its docstring
says why: *"a guard asserted by `assertIn` passes just as happily when its condition is inverted"*), and
`test_no_skip_is_reachable_without_the_gate` is stated as a reachability claim over every `return 0`
rather than as a substring check.

### V7a — my own instrument was broken first, and the negative control is what caught it

The first pass of this battery used `git checkout -q -- .` to reset between mutations. That restores the
worktree **from the index**, and M1's `git checkout <commit> -- <path>` had written the reverted
`p4_lib.py` into the index — so M1's revert persisted through M2, M3, M4 and M5. The first run reported
M5 (the negative control) as **5 failed**, which read as a real defect: a comment on a non-producing
module appearing to stale an endpoint. It was M1's residue.

I would have reported a defect that does not exist. What stopped it was that the run I had designed to
prove nothing was the only one whose expected answer I knew exactly. **A negative control is the cheapest
thing in a battery and the only part that audits the harness.** Re-run with `git reset --hard` it is clean.
Recorded here rather than quietly fixed, because the failure was mine and it is the same class I am
auditing others for.

## V8 — `PROMPTS-20260811 §3`'s *"struck magnitudes appear 8× in `main_note.pdf`"* → **UNRESOLVED**

Direction confirmed independently and more strongly than stated: 0 of 17 derived literals in
`main_paper.pdf`, 0 of 17 in `main_primer.pdf`. **The `8×` itself does not reproduce and cannot be
refuted either.** At `4f75e50` — the commit carrying the sentence — the note's two using files already
held **25** `\dead{}` uses giving **17** distinct literals appearing **51** times, so "five magnitudes"
was not the population. But neither §3 nor the docstring names which five, and several of my 17
(`1.6`, `6.5`, `9.9`) are collision-prone, so 51 certainly over-counts struck renderings. **The claim is
unreproducible as written for want of its population** — BEN-079's shape one level up. Its conclusion is
unaffected and independently confirmed. This is UNRESOLVED; do not round it to either side.

## V10 — S3 (null-as-absent) executed → **PASS: zero new defects, over a scope narrower than I sized**

Run after V9 was written; V9's "not run" now applies to S1, S2 and S4b only.

Controls asserted **before** the sweep, and it would have withheld itself had either failed: positive
(pre-fix PB2) fired 2, negative (post-fix `1440b58`) fired 0, corpus floor 340 tracked `.py` ≥ 300.

**34 sites, 9 flagged as permissive-`None`-branch, 0 defects after triage.** Every dismissal named, per
the corpus doc's abort condition 4:

| site | why dismissed |
|---|---|
| `p4_check_verifier_token.py:107` | `raise P4GateError` — restrictive |
| `pet/step1_increment_trajectory.py:201` | `raise SystemExit` — restrictive |
| `pet/gate2_target_runtime.py:108` | returns an explicit *"fail closed"* refusal — restrictive |
| `pet/validate_pet_nominal_gate4.py:1225` | appends a **failing** check (`_ck(..., False, "NOT SUPPLIED…")`) — restrictive |
| `lib/enumerate_backfill_families.py:77` | appends to `unresolved` — restrictive |
| `pet/validate_p3f_pet_fullevent.py:181` | `continue`, with the comment *"truth/miss checks carry no out_of_domain field"* — scoped by design |
| `pet/fullevent_fps_dataloader.py:296` | `blocks.get(key)` → `continue`. The docstring says *"fail closed"* while an absent-or-null block is **skipped** — but the function scopes itself to *"the supplied muon/vertex blocks"*, so skipping an unsupplied one is the stated contract. **Refuted**, per default-to-refuted. Noted only because the docstring's "fail closed" is broader than the behaviour |
| `usagectl.py:345`, `:448` | `continue` on an absent config window, with a type check immediately below; usage accounting, not a gate. Also a detector artifact — one `.get` at `:344` reported against two `if` lines |

**The classifier over-reports and I am naming the mechanism rather than the rate:** it substring-matches
permissive tokens, and `"ok"` is inside `"token"` and `"blocked"`. Three of the nine were tagged that way.
Harmless here — over-reporting sends work to triage, which is the safe direction — but it is why the
9 is not a count of anything.

**THE SCOPE GAP, stated because my own two numbers disagree.** The corpus doc sized S3 at **69** sites;
the executed sweep visited **34**. They are not the same detector: sizing counted a `None`-comparison or
truthiness read of a `.get`-bound variable **anywhere** — inside `while`, ternaries, boolean operands,
`assert` — while the executed version only visits a bare `if` test. **So roughly 35 sized sites were not
swept**, and S3's clean result covers the `if`-statement form only. Reconciling these two numbers, rather
than reporting the smaller one, is the entire point of having sized it first.

**Reading, per the corpus doc §3:** BEN-070's two readings stay open. Zero new instances in the swept
scope is consistent both with the class being concentrated in recently-written code and with the detector
being too narrow, and one sweep does not choose between them.

## V11 — S4b (stale-pin census) executed → **BLOCK on 3 pins; and the alarming reading REFUTES**

Filed as **BEN-091**. Corpus C3, all 113 receipts under `docs/orchestration/state/`. Method: pair a
path-valued key with a sha256-valued key sharing its stem in the same object, restrict to paths in
`git ls-files`, recompute with `hashlib` off the filesystem, and for each mismatch walk the path's
history to ask *was this pin ever valid?* — the I3 instrument from V3, applied to the whole population.

**338 path+sha pairs · 238 hold · 71 broken · 29 paths not tracked (unswept).**

**The headline number is not the finding, and reporting it alone would have been alarmism.**

- **The live Gate-4 receipt is CLEAN.** `p3f-pet-gate4-launch-code-gate-20260810c.json` —
  `verdict PASS_CODE_ONLY`, `nominal_pet_training_allowed: True`, identified as live by
  `KNOWN_ISSUES.md:25` and `INDEX-retracted-and-superseded-values.md:85`, not by its filename sorting
  last — carries **23 pins and all 23 hold.** My sweep never flagged it; I checked it directly rather
  than inferring that from its absence. **No live gate in this population is compromised.**
- **68 of the 71 are superseded dated receipts** — the `20260721 … 20260810b` Gate-4 chain and the
  July G2 receipts. Each is a snapshot that a later re-issue replaced, so staleness is the design, and
  **every one of those 68 pins resolves to a real commit** (`5a22e1c`, `ada72b0`, `5410ab0`, `dfef335`,
  `2b2e5f1`, `feb446d`, `8f2bcb0`, `37b9355`, `3fc1f3a`, `01fcb72`, `25d8360`, `8c8775f`). Stale, fully
  auditable, no action. Same disposition the GBDT lane reached for the wakerctl pin.

**THE ACTUAL FINDING — 3 pins are DANGLING, not stale, and that is a different class:**

| receipt | pinned path | pin | revisions searched |
|---|---|---|---|
| `g2-dump-submit-20260719.json` | `nd-unfolding/pet/sbatch_dump_g2_mefhc.sh` | `324a4081…` | **1** |
| `p3f-pet-gate4-launch-code-gate-20260801.json` | `nd-unfolding/pet/train_fullevent_nominal.py` | `42194360…` | **12** |
| `sessions.json` `/sessions/agent-E-g2-source/account_migrations[0]` | `state/agent-E-account-migration-20260719.json` | `87833e8c…` | **2** |

**Refutation attempted and failed.** The first pass searched only `origin/main`, which would have missed
an unmerged branch or a rename. Re-run across **all refs with `--follow`**: **no revision of any of the
three ever had the pinned content.** So unlike the wakerctl pin, the code these three receipts attest to
**cannot be produced from git at all** — the receipt asserts an integrity binding to content that does
not exist anywhere in history. That is exactly the fourth seeded shape: *an artifact asserting a state it
cannot have.* `sbatch_dump_g2_mefhc.sh` is the sharpest: the file has **exactly one** revision ever, so
its pin has never matched.

**The most likely mechanism, and it is not carelessness.** The pin was computed against a file the
committed tree never held — either an uncommitted working-tree edit hashed before the commit that
followed, or a hash taken on the **cluster checkout**, which is forked from local by construction. The
second is the more probable and the more instructive: *a content pin taken on one tree is meaningless in
another*, and this campaign's own cluster/local fork rule already says the two trees are not comparable.
It does not rescue the pins — unrecoverable is unrecoverable — but it changes the disposition from
*someone erred* to *the pin was taken against a tree git cannot see*, which is a process fix rather than
a correction.

**Disposition is NOT mine, and no hash should be hand-edited** — the same argument the GBDT lane made
for the wakerctl pin applies with more force here: for a stale pin the value still identifies real code,
and for a dangling one the value is the only remaining evidence that the attested content ever differed.
Overwriting either destroys the only information left. Routed to Session A for owner assignment; the two
PET receipts are Session C's by path, `sessions.json` is control-plane.

**Two limits on this result, stated because the number invites over-reading.** (i) **29 pinned paths are
not tracked** — scratch ROOTs and cluster paths — and were not checked at all; the census is silent on
them, not clean. (ii) The pairing heuristic requires a path key and a sha key sharing a stem in the same
JSON object, so **a pin recorded without an adjacent path was never examined.** 338 pairs out of the 884
hash-valued fields counted in the corpus doc: this covers **38%** of the pinned values, and the other 62%
are unswept.

## V12 — S1 (read-before-registered) executed → **PASS: 0 new instances. Two detector bugs found first**

Filed as **BEN-093**. Controls against the **real** artifact, not synthetic snippets: pre-fix
`p4_evidence.py` at `c308a9c^`, post-fix at `c308a9c`.

**v1 was silent on the known instance and withheld itself.** The reason was a sentence I had written
into the routed corpus definition and A had accepted: *"intraprocedural only… an accumulator mutated
inside a callee invoked after the caller read it is invisible."* The real PB3 mutation is exactly that —
`need(cond, msg)`, a module-level helper that appends to the global `blockers`. **The known instance
was the declared blind spot.** With a synthetic control, or none, S1 would have swept 84 sites, found
nothing, and reported clean from a detector that could not have found a single instance of its target.

**v2 resolves one level** (a function mutating a module-global accumulator is an alias for mutating it;
a call to it is a mutation at the call site). Positive control then fires on exactly the three reads
BEN-084 names — `:402`, `:405`, `:413`, each against the `need()` at `:423`.

**The negative control then failed, and caught a second, unrelated detector bug:** scope partitioning
skipped descending when the *child* was a `FunctionDef` rather than when the *popped node* was, so a
top-level `def` was popped and its body absorbed into module scope — pairing a read inside
`_publish_evidence()` with a module-level `need()` and firing on the committed repair.

**Result with both controls passing, corpus floor 341 ≥ 300: 52 sites across 21 files, 0
verdict-accumulator sites.** No new PB3-shape instance. Read as *the swept scope is clean*, not *the
class is absent*.

## V13 — Session A's Step-2 defect, and its proposed fix → **defect CONFIRMED; fix REFUTED**

Filed as **BEN-092**. Verified independently, every number from a command run this turn on `origin/main`.

**The defect is real.** `56692312` 0 message hits / 9 tracked files; `56695130` 0 / 9; `56693776` 0 / 6 —
all three properly filed in `RUNS.tsv`, `VALIDATION_LEDGER.md` and terminal per-job receipts, by commits
whose message never repeats the id. Controls `56691812` 8/15, `56693207` 3/11, `56563761` 7/21.

**The proposed cheap fix — `git grep -l <jobid>` anywhere ⇒ filed — is unsafe, and the counterexample
is live rather than hypothetical.** `56695424` is **PENDING**, so no verdict can exist, yet it matches
6 tracked files including `state/ben106-stamp-verify-**active**-56695424.json`. Predeclaring and arming
a watch puts an id across the tree before any verdict exists. A asked to be told if this was real: it is.

**A sharper rule exists in the tree's own convention**, so this needs no new mechanism. `RUNS.tsv`
carries `slurm_job`, `end_utc`, `exit` and a **`verdict`** column; `state/` receipts carry a lifecycle
token — measured `-submit` 16, `-complete` 11, `-error` 4, `-active` 3, where **`-complete`/`-error` are
terminal and `-submit`/`-active` are not.** Either discriminator separates all seven test ids correctly
and marks `56695424` unfiled. Recommended rule, with its own limit stated: *filed iff `RUNS.tsv` has a
row whose `slurm_job` contains the id and whose `verdict`/`end_utc` is non-empty* — which assumes
`RUNS.tsv` is written for every job, so a ledger-only verdict would under-report. That is the safe
direction and the same direction the step errs in today, but it should be checked, not assumed.

## V14 — Session C's canonical-designation count (32) → **PASS on the count, BLOCK on the corpus, UNRESOLVED on the class**

Filed as **BEN-095**. Commissioned by A. Five instruments, none of them C's script.

**(1) No site 33 in the declared corpus — PASS.** Instruments: strict matcher run *outside* `.py`/`.sh`;
an inverse pass enumerating everything the matcher structurally cannot see (93 lookahead misses, 3
lookbehind rejections); a composed-name search; a filesystem check under `nd-unfolding/pet/`; and
`git log -S --diff-filter=D` for renamed-away sites. All 96 unseen occurrences triage correctly as
class-4 module names, backticked prose, or the directory-independent basename
`pet_fullevent_nominal_weights.npz`. **The dangerous class-3 form does not occur** — there is no
unquoted end-of-line `X=${PET}/fullevent_nominal`; all four directory compositions end in a quote and
the matcher sees them. **32 is right for its corpus.**

**(2) The corpus is narrower than the claim — BLOCK.** `_tracked()` is `git ls-files "*.py" "*.sh"`,
while the docstring asserts *"every occurrence in the tree must appear in the inventory"* and rests the
designation's safety on completeness. The **same matcher** finds **74 occurrences in 33 tracked files**
outside that corpus. Almost all are genuinely `RECORD`, so the dispositions are cheap — the defect is
the unstated scope. A file whose subject is that implicit exclusions hide real sites carries one in its
own corpus definition. Same shape as BEN-090 and BEN-092: the range was argued over, the corpus was not.

**(3) A fifth spelling class — UNRESOLVED, and unresolvable statically.** The namespace arrives from a
**data file at run time**: `train_fullevent_nominal.py:529,534` stamps `weights_folder` and
`step2_checkpoint` as absolute paths into the artifact's own `inference_contract`, and
`extract_fullevent_fps.py:243` does `ckpt = contract["step2_checkpoint"]` → `model.load_weights(ckpt)`.
Verified path-key reads: `gate_ab_push_provenance.py` 3, `extract_fullevent_fps.py` 2,
`step1_increment_trajectory.py` 1, `step1_pull_push_decomposition.py` 1. No source-text matcher over any
corpus can see these. **Not hypothetical — BEN-133 already proved it**, and it does not raise an error
because the path it names exists.

**This cuts in C's favour on the decision and against the number.** Designation-without-moving is safe
precisely because a consumer resolves the contract of whichever artifact it is handed — BEN-133's own
argument, independently corroborated here. But it means the checker is the deliverable and 32 is a
snapshot, which is C's stated position, now corroborated rather than asserted.

Nothing edited; `nd-unfolding/pet/` is C's.

## V15 — is RECORD-counts-unenforced too weak? → **not too weak as a class; wider than its justification**

Asked by A after C widened the corpus to 105/51. Detail amended into BEN-095.

**My suspicion refuted first.** `audit()` tests `if n is not None`, not `if disp != "RECORD"`, so the
exemption could have leaked to any entry. Measured: **0 non-RECORD entries carry `None`**, and one
RECORD entry keeps an enforced count. It is exactly where C says it is.

**My own instrument over-matched and I caught it by inspecting matches** (BEN-088 v): a first pass said
*"34/34 RECORD files are referenced by code"* — true and meaningless, since the checker names every
inventory key in its own source.

**The real answer: the exemption is keyed on the DISPOSITION, not on the property that justifies it.**
C's cry-wolf rationale is about *append-only-ness*. Splitting the 33 unenforced entries by commits ever
touching them: **10 are genuinely append-only** (`ND_OMNIFOLD_RUN_LOG.md` 145, `AUTONOMOUS_LOG` 131,
`FINDINGS.md` 118, `OPEN_ITEMS.md` 54, +6) and **23 are frozen, one commit each** — every
`GATE_AB_PUSH_PROVENANCE.*`, `STEP1_DECOMPOSITION.*`, `STEP1_TRAJECTORY.*`, the per-job `state/*.json`.
A frozen receipt cannot cry wolf, so enforcing its count costs nothing and catches the one event that
should never happen silently: a committed receipt's content changing — the BEN-091 and BEN-133 classes,
both live in this namespace. `STEP1_DECOMPOSITION.slurm-56445883.json` is `json.load`ed at
`step1_increment_trajectory.py:120` as a gated run's reproduction anchor.

**Recommendation: keep `None` for the 10, give the 23 their counts.** C's argument survives intact.
Heuristic boundary stated: commit-count proxies append-only-ness and misclassifies
`p3f-pet-gate4-launch-code-gate-20260731.json` (3 commits = revised, not appended).

## V9 — the rest of the sweep → **NOT RUN. UNRESOLVED, and its silence means nothing**

Corpus defined and routed (`CORPUS-20260811-gates-that-cannot-fail-sweep.md`), reviewed by A, three of
four detectors carry live controls, S4a dropped on A's endorsement. **The sweep has not been executed and
no triage has been done.** Sizing only, at `78296de`: S1 84 sites / 27 files; S3 69 sites / 26 files; S2a
223 write-only keys out of 2293 (a floor, and noisy — most are report fields nobody was ever going to
read programmatically, which is the under/over-report asymmetry §2 predicted); S4b unsized.

**S2's positive control against PB4 failed and S2 ships relabelled** as the strictly weaker
produced-and-consumed-by-nothing class. PB4's obligation lives in the specification, not the code, so its
shape is not statically detectable in general.

Nobody should read this section as *"the sweep found little."* It found nothing because it has not run.

---

## Filing status — one row is owed and I am deliberately not writing it

**BEN-090 (V1) needs a row in `FINDINGS.md` and an index line for
`FINDING-20260811-dead-containment-evadable.md`. I have not added either**, and the reason is a live
hazard rather than an omission: throughout this session `docs/orchestration/FINDINGS.md` has carried
another lane's **staged, uncommitted** edits (Session B's BEN-100…105 block). Editing and committing that
file would sweep B's in-progress work into my commit. The repo convention that a result does not exist
until its commit lands is real, and so is the rule against entangling another lane's work.

Routed to Session A: the row lands the moment `FINDINGS.md` is clean, either by me or by whoever holds it
then. Until it lands, this finding is not filed and should be treated as such.

I have not edited `FINDINGS.md`, `KNOWN_ISSUES.md`, BEN-084, or any other lane's row.

---

*(The "one row is owed" section immediately above is SUPERSEDED: BEN-090 landed in `FINDINGS.md`
row 87 with its long-form doc indexed, in commit `4e0bb74`. Left in place per this repo's convention
of leaving written history written.)*

---

## V16 — close-out re-verification, 2026-08-11 21:2x, at `35464a4`

Session A asked what in tonight's summary to Joseph would be an overclaim. Three answers, in
descending order of how wrong the summary would be.

### V16.a — `check_dead_containment.py` is STILL EVADABLE. **BLOCK, unchanged.**

    $ grep -n DEAD_RE docs/analysis-note/check_dead_containment.py
      50:DEAD_RE = re.compile(r"\\dead\{")
    $ git log --oneline 4e0bb74..HEAD -- docs/analysis-note/check_dead_containment.py
      (empty)

**Zero commits have touched the file since BEN-090 was filed.** The one-character repair
(`r"\\dead\s*\{"`) has not been made. Distinguish two statements that are easy to merge and that
differ in what they license:

- **The containment HOLDS.** `grep -rn '\dead[ ]\+{' docs/analysis-note/` still returns nothing;
  no spaced instance exists in the tree.
- **The GATE does not enforce it.** A `\dead {x}` written tomorrow passes the checker, builds, and
  renders in `main_paper.pdf` — demonstrated end to end in
  `FINDING-20260811-dead-containment-evadable.md` §1.

Any summary sentence of the form *"struck-value containment is enforced as a test"* is an overclaim
tonight. The supportable sentence is *"containment is true today and the test that is supposed to
keep it true has a known hole that is one character to close."*

### V16.b — MY OWN justification, now embedded in `0b6af48`'s commit body, OVERSTATES what the fix buys. **BLOCK, against myself.**

Session C adopted my RECORD re-key recommendation (`0b6af48`) and quoted my reason verbatim: enforcing
a frozen receipt's count *"buys a check on the one event that must never happen silently: a committed
receipt's content changing."*

**That is false as written, and I wrote it.** The enforced count counts `fullevent_nominal` *namespace
occurrences*, not content. Demonstrated in an isolated clone at `35464a4`, on the exact file my
justification named as the reproduction anchor:

    MK4  edit a numeric field in fullevent_nominal/STEP1_DECOMPOSITION.slurm-56445883.json
         (0.0 -> 9.87654321), leaving its single namespace occurrence untouched
         -> check_canonical_designation.py exit=0, PASS

The true statement is narrower: **it catches a content change that alters the namespace-occurrence
count, and nothing else.** For `STEP1_DECOMPOSITION.slurm-56445883.json` that count is **1**, in a
`gate_receipt` path — so essentially every physics-bearing edit to that receipt is invisible to it.
The fix is still correct and still worth having; it is a *drift detector for new references*, which is
what the `COUNT DRIFT` message itself says. It is not a content pin, and the sha256 pins in the Gate-4
receipts are what actually serve that role.

**C's fix itself is REAL — power-tested here with C's own script and four mutations, in a clone:**

| # | mutation | expected | got |
|---|---|---|---|
| MK0 | none | PASS | **PASS**, exit 0 |
| MK1 | a `RECORD-FROZEN` entry waives its count (`None`) | report | **`EXEMPTION MISKEYED …`, exit 1** |
| MK3 | a `RECORD-FROZEN` count set wrong (8 → 7) | report | **`COUNT DRIFT … expected 7, found 8`, exit 1** |
| MK2 | the same entry **relabelled** `RECORD-APPEND` and waived | — | **PASS, exit 0** |

MK2 is the residual, and it is weak rather than a defect: the keying is now structural against
*accidental* drift, but nothing verifies that a file labelled `RECORD-APPEND` is actually append-only,
so a wrong label is still a silent exemption. Honest naming — the label now names the property — and
worth one sentence in the docstring, not a repair. Counts reconcile: 9 `RECORD-APPEND` / 26
`RECORD-FROZEN`, exactly as `0b6af48`'s body states. C's 9/26 against my 10/23 is C's classification
by file kind beating my commit-count proxy, whose boundary I had named; C is right.

### V16.c — my BEN-091 Gate-4 certification is STALE. **UNRESOLVED, and it is a coverage hole, not a defect.**

BEN-091 records *"the live Gate-4 `20260810c` is clean at 23/23."* Measured this turn:

- `20260810c` was **rewritten** after my sweep — `git diff --stat 8b7c1c5 HEAD` on it shows
  **74 insertions / 70 deletions**. Its 23-entry `files` map is gone; it is now a superseded stub with
  `superseded_by: …-20260812.json`, `superseded_on: 2026-08-12`, and **5** `files_at_issue` pins.
  All 5 match the tree. **My "23/23" describes a version of the file that no longer exists.**
- The live receipt is now `p3f-pet-gate4-launch-code-gate-20260812.json`, `verdict:
  PASS_CODE_ONLY`. **Independently re-verified here: 22 pins, 22 match the working tree, 0 mismatch,
  0 missing.** Clean, but clean *because I just checked it*, not because BEN-091 covered it.
- **14 receipt files under `state/` were added or modified after my sweep commit `8b7c1c5`** (10 added,
  4 modified). None was in the corpus BEN-091 measured. BEN-091's stated coverage (338 of 884 pin
  fields, 38%) is a snapshot of a tree that has since moved.

**Instrument caveat, stated because it would otherwise read as drift:** a quick re-count this turn
returned 360 hash-valued fields over 124 files against BEN-091's 884, but that is a *different
definition* (bare 7–40-hex string values only, versus BEN-091's field-name-driven enumeration), not a
change in the tree. Two numbers from two instruments are not a delta. BEN-079's shape — treat 884 as
scoped to the script that produced it.

Also corrected in the same breath: an intermediate pass this turn reported **8 DANGLING** hashes in
`20260810c`. They are 12-character prefixes of sha256 digests, never git objects. My matcher was
wrong, not the receipt. Caught by looking at the matched strings rather than the count — BEN-088 (v),
again, and this is the second time this session that rule has caught my own instrument.

### V16.a — CORRECTED, same turn, by Session A's independent re-run

Two corrections, and I am recording them here as well as in the BEN-090 row because V16.a as first
written is what Session A was about to hand Joseph.

**(1) My containment grep was wrong, and the exception argues my side.** I wrote that
`grep -rn '\dead[ ]\+{' docs/analysis-note/` "still returns nothing." It returns **one** file:
`main_note.aux:345`, `\dead {\petRatio }` inside a `\newlabel` for `fig:petabs`. Verified here: the
source at `sec_pet.tex:91` is `$\dead{\petRatio}$` — **unspaced** — and LaTeX's own `\newlabel`
serialisation inserts the space. **The string the regex cannot match is the string LaTeX writes when
it round-trips its own input.**

Boundary, measured, because it is what keeps the claim honest: `main_note.aux` is untracked build
output, and `resolve_closure()` walks only the driver `\input`/`\include` closure — re-derived at
**4 / 19 / 4** files for paper / note / primer, **zero untracked or generated files in any of them**,
no `.tex` in the directory gitignored. So the hole is **latent in the corpus and occupied outside
it**. `\petRatio` resolves cleanly (`values.tex:72`, `\newcommand{\petRatio}{0.912}`, flat body) and
`0.912` measures 0 / 0 / 2 in paper / primer / note — containment holds for the corpus that matters.

**(2) I overstated the severity, and A was right to push back.** I wrote that `4f75e50`'s subject
*"Enforce struck-value containment as a test"* "asserts the thing that is not yet true." It does not:
that commit creates the 232-line checker and wires it into `build_all.sh`, and it catches the
unspaced form, which is every occurrence in the tree. **The supportable sentence is *enforcement
landed and is evadable by one character*.** A's stated reason is the one that matters — the wider
claim invites the owner to discount a finding that is true.

For a verifier lane that is not a stylistic point. Overstating the severity of a real defect spends
the credibility that makes the next true finding actionable, and it is the same error as understating
one, in the direction that feels like diligence. **Rule: state the narrowest claim the evidence
supports, especially when the wider one is rhetorically better.** Note the shape: BEN-096, filed
thirty minutes earlier this same turn, is a wrong REASON under a right conclusion. This is a wrong
SEVERITY over a right finding. Both survive a check aimed at the finding itself.

**(3) D2 independently verified by A**, and it lands harder than §4 of the finding doc states:
`:121` early-returns when the PDF or `pdftotext` is absent, `:196` records a note, `:228` returns 0
absent failures, `build_all.sh:25-29` branches only on `python3` existing. `pdftotext` is present on
this machine so the stage does run — which makes the check **silently machine-dependent**, the worst
version of that shape rather than the mildest.

---

## V17 — Session A's TOCTOU claim: **PASS on the diagnosis, BLOCK on the conclusion, and one clause of BEN-115 is wrong**

A asked me to refute, before Joseph reads it, the claim that *"no per-session discipline closes the
index race"* — naming the risk that A was overgeneralising from one incident toward a per-lane
worktree decision A already favours. Refuted. Three controlled tests in an isolated clone at
`3292345`, none in the shared checkout.

**First, the thing A should hear before any of it: A's committed row already refutes A's question.**
`BEN-115` states *"the structural fix is one flag … `git commit -- <pathspec>`"* and, explicitly,
*"it argues for [the worktree] more weakly than it appears to … the worktree decision should be made
on its merits rather than under the pressure of this incident."* That is the correct answer and it is
already in the ledger. **The message asking me to refute it is behind the row that refutes it** — a
small instance of the shape this session keeps finding, a claim travelling in a channel that its own
artifact has already superseded.

### The measurements

| test | setup | result |
|---|---|---|
| **T1** | peer stages `KNOWN_ISSUES.md`; I `git commit -- docs/OPEN_ITEMS.md` | commit contains **only my path**; peer's staged work **survived**, still staged |
| **T2** | peer has **staged** content in `docs/OPEN_ITEMS.md`; I edit it too and `git commit -- docs/OPEN_ITEMS.md` | committed blob contains **both** the peer's staged line **and** mine |
| **T3b** | two concurrent `git commit -- <path>` on disjoint paths, ×3 | loser fails **loudly**: `fatal: Unable to create .git/index.lock`, `rc=128`, work left in the tree. 3/3 |

### What that settles

**The diagnosis is right: `git diff --cached --stat` is a TOCTOU read, not a guard.** It is a read of
process-external state with a window before the write. Nothing per-session closes *that*.

**The conclusion does not follow, and T1 is why.** The discipline that survives concurrency is not a
better *check* on staging — it is **not staging at all**. `git commit -- <pathspec>` builds a
temporary index and never writes the shared one, so there is no read-modify-write cycle to race. The
whole incident began with `git add`; had the two paths been passed to `git commit` directly, there
would have been nothing staged for B to absorb and nothing to unstage. **That rule is already in the
ledger as BEN-094(i), filed by this lane earlier tonight, and the incident is what happens when it is
bypassed rather than evidence that it fails.**

**T3b is better news than anyone has stated:** the residual concurrency failure is *loud*. `index.lock`
contention returns `rc=128` with a fatal message and leaves the work in the tree. A commit discipline
whose failure mode is a visible non-zero exit is in a different class from one whose failure mode is a
commit containing someone else's work.

### **BLOCK — one clause of BEN-115 is measurably false, and it is the load-bearing one**

BEN-115 says `git commit -- <pathspec>` *"cannot absorb another lane's staged content."* **T2 shows it
can.** Partial commit takes the **working tree** version of every path you name. If a peer has staged
— or merely edited — a file **you name**, their uncommitted work is committed under your message, and
their staged version is silently consumed.

This is not a corner case. The file it applies to is **`FINDINGS.md`**, which three lanes wrote to
tonight, and it is the exact file the original incident was about. The correct statement is:

> `git commit -- <pathspec>` cannot absorb a peer's work in files **you do not name**. In files you
> **do** name it behaves exactly as `git add` did, because it reads the working tree. **The protection
> is the pathspec, and it is only as good as your ownership of those paths.**

So the surviving rule has two halves, and only the first is in the ledger: **(a)** never write the
shared index; **(b)** name only paths you own — and for a shared file like `FINDINGS.md`, "own" means
*you are the only lane with uncommitted changes to it right now*, which is itself a TOCTOU read. **The
race is not eliminated for shared files; it is narrowed from every staged path to the paths you
name.** That is a large reduction and it is not zero, and BEN-115 currently reads as zero.

**Not edited — routed to Session A, who owns BEN-115.** For the worktree question this cuts the same
way A already wrote: the residual is real but small and bounded by discipline over a handful of shared
documents, so it strengthens the worktree case slightly and still does not decide it. Decide it on its
merits.

### V17 — CORRECTED. **I got the attribution wrong, and it is instance (5) of the class I then filed.**

V17 above says the correction is *"routed to Session A, who owns BEN-115."* **BEN-115 is Session B's
row**, filed at `3292345` inside B's 100-129 block; A's involvement is one credited framing inside it.
Session A caught it. I read a row containing A's sentence and inferred authorship — and the cost is
concrete rather than cosmetic: routed as written, the correction would have gone to a lane with no
standing to act on it. Filed as BEN-099(5), against myself.

**And B already knew the limit I "refuted".** `3292345`'s commit body reads: *"Caveat recorded in the
row: it takes the whole working-tree file, so it fixes the cross-file race and not the same-file one;
GIT_INDEX_FILE is the tool when both apply."* Measured: the row contains **zero** occurrences of that
caveat and states the opposite flatly. **So my BLOCK on the row stands unchanged — the row is wrong as
written and the row is what gets read — but my characterisation of B does not.** B did not miss it. B
wrote it in the body and asserted it was in the row. That is a different and more interesting defect,
and it is BEN-099(2).

Session B had also already argued, in the relay A forwarded, that rule (i) *"is not sufficient on a
shared checkout, because two lanes can touch the same path… `FINDINGS.md`, `VALIDATION_LEDGER.md` and
the RUN_LOGs are exactly the files every lane writes to."* **B reached the correct position first and
against its own row's interest.** My measurement corroborates B; it does not originate the point, and
I had it as originating.

### V18 — **BLOCK against myself: my commit `7b26803` contains Session C's BEN-137 row.**

`git log -S'| BEN-137 |' -- docs/orchestration/FINDINGS.md` returns `7b26803` and nothing earlier. Its
message describes BEN-097/098 and a BEN-091 amendment and is silent about BEN-137. **I used
`git commit -- <path>`, my own BEN-094 rule (i), and it absorbed C's row anyway** — the exact T2
mechanism I measured hours later and published.

**Audited all ten of my commits tonight against T2, which is what I should have done the moment T2
existed:** `4e0bb74`, `7386a9b`, `8b7c1c5`, `5b13501`, `e572d34`, `57c8234`, `2ae151b`, `e6b0aa9`,
`f013c68` are **clean** — own rows, own files only. `7b26803` is the **one** absorption. Scope
correction filed into BEN-094 in the `ae7e615` form; not reverted, per the pushed-history convention.

**The failure worth carrying is not the absorption — it is that I built the instrument and did not
aim it at myself.** T1/T2/T3 were run, published, and turned into a corrected rule, and I did not
re-audit my own commits with them. C's message prompted the audit. That is the third instance this
session of the same miss: BEN-093 (test the declared blind spot against the known instance), BEN-096
(power-test the justification, not only the implementation), and now this. **A newly built instrument's
first target should be the author's own recent work.**

### V19 — Session C's scope correction against itself is **BLOCK: two of its three instances did not happen**

C reported that `e572d34` introduced my V14 and `57c8234` introduced my V15, and filed it into BEN-134
as a scope correction against itself. **Both are my own commits.** `e572d34`'s body opens *"Session D
(verifier), commissioned by Session A to break Session C's canonical-designation count of 32"*;
`57c8234`'s opens *"Session D (verifier), answering A's question about C's counts-unenforced-for-RECORD
design"*; both file BEN-095, in my own block. My text was introduced by my own commits. `git log -S`
returned the right hash and the lane attached to it was invented.

**Why it happened, and it is not carelessness:** all **92** commits on `origin/main` since 2026-08-11
12:00 carry one identity, `Joseph Bailey <jrbailey555@gmail.com>`. No git query can attribute a commit
to a lane. C's audit had no lane axis, so every returned hash was ambiguous and C resolved the
ambiguity by assumption — inferring authorship from **topic** (BEN-095 is about C's checker) exactly as
I inferred it from **voice** in V17. Filed as BEN-160, with BEN-099(5) as its pair.

**Not disturbed:** C's third instance, `7c3f617` carrying B's row, is real. C's finding that pathspec
does not help because the loss window is *between editing a shared file and committing it* is real and
is the sharpest git result anyone produced tonight — my T1/T2/T3 do not cover it, because I tested the
index and that window is not in the index. C's rule about unexplained `-` lines with no matching `+`
is real and I have adopted it.

**What is corrected is the tally and the provenance, not C's diligence.** C's count of "at least seven"
is at most five, and the ledger currently says C's commits carried my verdicts.

---

### V20 — the `VALIDATION_LEDGER.md` VL re-id (`1ec042e`): **PASS**, and the post-condition I required is the reason I can say so

I gave Session A the GO on this design after attacking it, and the GO carried one condition A had not
proposed: a **structural post-condition**, re-measured after the edit. A's own two-sided check counted
ids against rows, which cannot see whether the edit changed how the file *partitions* — and the edit
touches separators and header rows, which are exactly what the partition keys on. A's separator
detector had missed 15 of 22 headers a few hours earlier, so a post-edit count computed by that
detector would have been the numerator certifying its own denominator.

Measured now with my own regexes, independent of A's:

    separators  22      headers  22      data rows  108
    VL ids     108      unique  108      data rows with NO VL id: 0

That is exactly the 22 / 22 / 108 I required, with complete coverage and no duplicate ids. The **leading
cell** decision I surfaced was taken, so `^\|\s*(VL\d+)\s*\|` matches the same shape as the existing
`BEN_ROW` / `OI_ROW` / `CLM_ROW` forms rather than needing a width-aware scan across the file's seven
table widths.

**Not disturbed and still true:** the latent hazard I named — a data row of literal dashes
(`| --- | --- |`) matches the separator regex and would promote the row above it to "header" — remains
latent. Zero instances today, and it is a property of the matcher, not of this edit.

**What this verdict does not cover:** the *content* of the 108 rows, the mapping receipt's correctness,
and whether the ledger freeze window is closed. The freeze is A's to close with the lanes and had not
been closed at `9ba19fa`.

---

### V21 — Gate 2 promotion requirement 1, independent receipt review: **PASS**

`G2_GATE2_TARGET_RUNTIME_RECEIPT.json`, job `56344268`, `status: PASS`,
`verdict: GATE2_CANONICAL_RUNTIME_PASS_INDEPENDENT_PROMOTION_PENDING`. Reviewed by Session D because
Session C promoted the gate and cannot review it. Requirement 1 is *"independent receipt review of
hashes, exact configuration, and binned telemetry"*; all three are addressed below.

**HASHES — verified against my own tree, not taken from C.** All four pinned sources are
byte-identical at `HEAD`: `2d-unfolding/unfold_2d_omnifold_unbinned.py`,
`nd-unfolding/pet/fullevent_fps_dataloader.py`, `omnifold_nn/omnifold/dataloader.py`,
`nd-unfolding/pet/gate2_target_runtime.py`. `execution.head_at_runtime` `beb40c9` **is an ancestor of
`origin/main`** (2026-08-05, "Fix the powered closure's weight dtype"). The product is bound to
today's tree.

**CONFIGURATION.** `target_mode negweight-refined`, `estimator exact`, `master_seed 42`,
`refinement_random_state 45`, `mc_normalization 1e6`, measured `1e6*R`, `dataloader_import_mode`
target-only with TensorFlow *not imported*, `pet_training_started: false`. Coherent with a
target-only gate; nothing claims a training run that did not occur.

**BINNED TELEMETRY — every published number re-derived from the receipt's own operands.**

    ps*sum(w_bkg)      109599.39938418806      == published        (exact)
    numerator          4006528.600615812       == published        (exact)
    R  (reco leg)      1.1240802949941018      == published        relative error 0.0
    R  (truth leg)     1.103260884167167       == published        (exact)
    shift factor       1.018870795770713       == published, and   == sum_w_truth/sum_w_reco
    1e6 * R            1124080.2949941019      == normalization_target, bit-for-bit
    data - bkg         4006528.600615812       vs raw_signed_sum 4006528.6006158125  (last ulp)
    n_data + n_bkg     4680719                 == n_measured_rows  (exact)
    n_negative_rows    564591                  == n_bkg_rows       (exact)
    rows*4 + 128       18723004                == published file size -> float32, from a SECOND instrument

The last line matters: the byte count confirms the declared `dtype: float32` independently of the
declaration.

**`b4_gated: true` IS EARNED, NOT DECORATION — the claim C flagged as its own weakest, refuted in the
gate's favour.** `die()` raises `RuntimeError`; the gate runs at `:587` in straight-line code, before
the receipt dict is built at `:624` and written at `:735`; **there is no `try`/`except` anywhere between
`:585` and `:740`**, so no write-always path exists. Power-tested the predicate directly over its
failure space — it BLOCKS on all seven of: absent telemetry block, `{}`, `None`, `present_in_dump`
false, leg `w_truth`, leg key absent, leg `None`; and passes only the correct configuration. It is also
numerically corroborated rather than merely flagged: `R_if_reco_leg_used_w_reco` equals the reported `R`
exactly, while the `w_truth` alternative is `1.1033` — the legs differ by 1.9% on this data, so "which
leg" is a distinguishable question here and the answer is the reco leg.

**C's open question on `normalized_sum` — ANSWERED, and the tolerance is not vacuous.**
`step1_target_sum_matches` = `np.isclose(rtol=3e-6, atol=2.0)`, budget **5.372** absolute; the observed
gap is **0.2927**, i.e. **5.4%** of budget. Power-tested: it blocks 1 part in 1e5, the missing-`R`
factor, and a bare `1e6`. The residual `2.6e-7` is **consistent with** the target being float32
(`2.2 x` float32 eps) — stated as consistency, not proof.

**One residual I closed rather than leave:** `max_mc_events: 200000` is the bounded MC *validation*
cloud only. `R`'s denominator sums `n_signal_rows: 49,152,885` with `n_signal_pass_reco: 20,573,521`
— the full population, not the subsample.

### What this verdict does NOT cover

- **I did not re-run the gate.** I reviewed the receipt, the code that writes it, and re-derived its
  arithmetic.
- **The target `.npy` digest `544b2f6a…` is UNVERIFIED BY ME** — the file is on `/pscratch`.
  C re-verified it this turn. **That is the one link in the chain resting on the lane that promoted the
  gate**, which is the exact thing requirement 1 exists to prevent, and it should be confirmed by
  someone with cluster access who is not C. It is a one-command ask and I am not treating it as
  blocking, because every number the digest would corroborate reconciles here from independent operands.
- The 166-test on-cluster green is the personal-orchestrator's measurement, not mine. I verified the
  off-cluster subset (165 across five files, plus 12 dual-leg mutation tests).
- **D2's MC-only closure path was read, not executed** (C's own limit): no runtime confirmation that
  ROOT is not imported.

---

### V22 — job `56818470`, Branch REPAIRED: the `iter0` exclusion **holds**, but the load-bearing check is a different one — **UNRESOLVED from this lane**

Session A asked me to attack the indexing choice: *"`iter0` is excluded from Branch REPAIRED because the
predeclaration's line 41 names the inventory `iter0/1/2` and localizes the defect to dynamics after
initial feedback. If that reading is wrong, the verdict is UNRESOLVED, not REPAIRED."*

**The reading is not wrong, and it is not a reading.** A's citation is off and its conclusion is better
supported than A thought.

- **Line 41 is a checkpoint-artifact inventory row** in the two-artifact comparison table
  (`per-iteration checkpoints | iter0/1/2 step1+step2 | same inventory`). It carries no scope claim and
  nothing should rest on it.
- **The exclusion is PREDECLARED at line 70**, in the criterion itself: *"Branch REPAIRED — for **both**
  iterations 1 and 2."* `iter0` is out of scope by the written criterion, not by interpretation.
- **The rationale is at lines 8–9**, not 41: job `56525829` localized the defect to *"iteration dynamics
  after initial feedback"*, so the pre-feedback iteration is not where the tested defect lives.
- **It predates the result by 26 hours** and was never edited: predeclaration `831043d`
  2026-08-11 18:31:53 -0400, single commit; job submitted `02dfb68` 2026-08-12 20:39:52 -0400.

So `iter0` at `0.1101` is not a suppressed failure. It is outside the predeclared scope, and the
annealed arm's `iter0` being worse than the control's is a real trade that belongs in the reporting —
which the mediator already stated — but it does not touch the REPAIRED/PERSISTS/UNRESOLVED partition.

### The check that actually decides this, and A did not name it

The predeclaration's **UNRESOLVED condition 1** is a domain-of-validity guard: *any* iteration with
`|r1_required_mean − 1| < 0.02` returns **no information**, and is predeclared UNRESOLVED rather than a
pass. Its author then wrote, of the annealed arm specifically:

> *"…much closer to the no-information point than the pre-anneal arm ever was. **This is the most likely
> single outcome of this run and it is predeclared as UNRESOLVED, not as a pass.**"*

**The predeclaration predicted UNRESOLVED-by-domain-failure as the single most likely result, and the
reported verdict is REPAIRED.** That is the discrepancy worth an adversary, not `iter0`.

From the published operands, the annealed arm sits at:

    push 1.0840530   R 1.1240803   required ~ R/push = 1.036924   |required - 1| = 0.036924
    guard threshold 0.02  ->  margin factor 1.85          (pre-anneal arm: 0.5257, margin factor 26.3)

So it plausibly clears the guard — **by 1.85x, where the arm it replaced cleared by 26x.** The anneal
moved this measurement an order of magnitude closer to the point where its own criterion stops
discriminating.

**VERDICT: UNRESOLVED from this lane** — *resolved 2026-08-13 by `cb41436`; see the correction at the end of this entry. The domain guard clears at every iteration, REPAIRED stands, and my proxy comparison below is REFUTED and INVERTED.*

**[original verdict as written:]** Not because I think REPAIRED is wrong, but because the one
number that separates REPAIRED from UNRESOLVED — `r1_required_mean` at iterations 1 and 2, against
`0.02` — is in receipts on `/pscratch` that I cannot read. `R/push` is my proxy, not the field.

**What closes it, in one command by anyone with cluster access:** print `r1_required_mean` for
iterations 1 and 2 from `STEP1_TRAJECTORY.slurm-56818470.json` and state both against `0.02`. If either
is under, the predeclared verdict is UNRESOLVED and REPAIRED must be withdrawn. If both clear, REPAIRED
stands on its own predeclared terms and **the margin should be published beside it**, because a
criterion clearing by 1.85x on the arm being promoted, having cleared by 26x on the arm being retired,
is a fact a reader needs in order to weigh it.

**Not verified by me:** every number attributed to the run itself — `iter0` `0.0279`/`0.1101`, the sign
inversions, Arm 1's reproduction gate, Arm 2's Gate A. `push`, `R` and the guard threshold are from
committed documents; the arithmetic above is mine.

#### V22 CORRECTION — the guard clears, and my proxy reversed the ordering it was used to establish

Session A ran the field values (`cb41436`). I re-derived every figure below from them rather than
accepting the summary.

    r1_required_mean        iter0                iter1                iter2           tightest  clears 0.02 by
    control          0.1240802949941018   0.0286839584480088   0.1616496092824724     iter1        1.434x
    annealed         0.1240802949941018   0.0991591571769675   0.0318598809751991     iter2        1.593x

**No iteration in either arm is under `0.02`. UNRESOLVED condition 1 does not fire and REPAIRED stands
on its predeclared terms.** My call to publish the margin is satisfied: `1.593x` at the deciding
iteration, `4.958x` at iter1.

**MY PROXY WAS WRONG IN THE DIRECTION THAT MATTERS.** I wrote that the anneal moved this measurement
*"an order of magnitude closer to the point where its own criterion stops discriminating"* — `1.85x`
promoted against `26.3x` retired. **From the field it is the reverse:** the annealed arm's tightest
iteration (`0.0318599`) sits *farther* from the no-information point than the control's (`0.0286840`).
The arm being retired was the tighter one.

`R/push` aggregates over a trajectory; `r1_required_mean` is per iteration. They diverge — and **by
unequal factors on the two arms**: the proxy overstates the control's clearance by **18.33x** and the
annealed arm's by **1.16x**. **A proxy wrong by unequal factors on the two things being compared does
not add noise, it reverses the ordering.** That is the shared-wrong-operand family pointed at my own instrument — **and I cited it as `BEN-086` here and in three peer messages, which `BEN-172` records as wrong: `BEN-086` is about `UNSOURCEABLE` verdicts being statements about the search, and no row makes the claim I attached to it.** The ratio `26.3` is arithmetically correct as `|R/push_final − 1|` — it simply is not the quantity the
criterion tests.

**One corroboration A did not run, and it holds.** At `iter0` there has been no reweighting, so
`push = 1` and `required` should equal `R` analytically — i.e. `r1_required_mean = |R − 1|` exactly, and
identically in both arms. Measured: both arms report `0.1240802949941018`; `R − 1` computes to
`0.12408029499410178`, differing by **1 ulp**.

**I gave the wrong mechanism for that ulp and A's follow-up (`c94d6f2`) exposes it.** I said it was
float64 cancellation in my subtraction. It is not: for `R` in `[1,2)`, `R − 1` is **exact** — verified,
`(R−1)+1 == R` — so there is no cancellation loss to attribute. A measured `r1_required_mean[iter0] == R`
**bit-for-bit in both arms**, hence `abs(field − 1)` equals `R − 1` at **0 ulps**. The 1-ulp gap is
between `R − 1` and the *printed* table entry, which carries 16 significant figures where the value needs
17. **The table rounded; nothing measured differently.** That makes the corroboration stronger than I
stated it: the true deviation at `iter0` is exactly `abs(R − 1)` in both arms, not merely close to it. The two arms agreeing bit-for-bit at the one iteration where they must is an
independent check that these are real per-iteration field values.

**What kept this from becoming a false finding was the label, not the reasoning.** The proxy was
labelled *"my proxy, not the field"* and the entry issued **UNRESOLVED**, not a measurement. Had it gone
out as a verdict, the record would now assert that the anneal degraded a criterion it slightly improved
— inside a verifier's verdict, which is the hardest place to dislodge a wrong number from.

**Standing, both caveats attached:** REPAIRED on the predeclared criterion, domain guard clearing at
every iteration; annealed `iter0` at `0.1101` is a real trade outside the predeclared scope; and
`1.593x` is not a comfortable margin even though it clears.

---

### V23 — the ledger rejects the arm the disposition adopts, and nothing reconciles them: **BLOCK on the record, not on the physics**

Routed by Session C, which flagged that `VL101` and the estimator disposition rest on the same number.
Measured here.

**`VALIDATION_LEDGER.md:1660`, live and unqualified:**

    | VL101 | recovery vs baseline | -0.034249724 | SECONDARY 0.546853 +/- 0.02 | **TRADE-OFF / ARM REJECTED** |

**`AUTHORIZATION-20260813-gate4-estimator-disposition.md` adopts the annealed arm and never mentions
`VL101`, `ARM REJECTED`, or the SECONDARY criterion.** It cites `0.546853` once, as *"full-LR recovery —
clears by 0.052271"* — i.e. it quotes the baseline while omitting that the same comparison is recorded
elsewhere as a rejection of the arm being adopted.

**`VL101` is referenced in exactly one place in the repository — its own ledger row.** It is not in
`INDEX-retracted-and-superseded-values.md`, not superseded, not qualified. `VALIDATION_LEDGER.md` is this
repo's canonical home for technote-quoted numbers, so **as the record stands, anyone quoting the ledger
for the annealed arm quotes `ARM REJECTED` for the arm the campaign adopted.**

This is `BEN-201`'s shape run backwards: there, a retraction reached the index but not the point of use;
here, a decision reached the point of use but not the ledger. Same defect, opposite direction, and the
ledger is the harder one to leave stale because it is the file the technote quotes.

**BLOCK is on the record, not the physics.** I am not saying the annealed arm is wrong or that VL101's
arithmetic is wrong. Both may stand. What cannot stand is the two of them standing *silently side by
side*. The fix is a ledger annotation naming the disposition and what overrode the SECONDARY reading —
`VL101`'s row is B's or A's to touch, not mine.

**And the baseline the rejection rests on is the open question.** `VL101` rejects against
`0.546853 ± 0.02`, the full-LR figure. Job `56818470` was launched precisely because that arm runs the
configuration `KNOWN_ISSUES.md` names as a tail-collapse candidate — *"if the collapse inflates recovery,
full-LR's advantage is the defect."* `56818470` returned REPAIRED, which establishes that the
sign-inversion defect is a property of the retired LR policy. **It does not establish that `0.546853` is
uninflated, and that is a different claim.** So `VL101` currently rejects the adopted arm against a
baseline whose validity is an open item — stated as an unresolved dependency, not as a reason to doubt
the number.

### OI-23 — C's caution is right, and the disposition has INVERTED which half is at risk

`OI-23` requires *"a nontrivial injected truth-reweight recovery closure **at the final nominal
configuration**."* C declined to call it discharged because job `56552326` was the annealed-LR shape
validation — a changed job — and existence is not configuration. Correct as of when C wrote it.

**But Joseph then adopted the annealed arm.** The estimator moved toward the closure rather than the
closure toward the estimator, so the question is no longer *"the closure ran a different configuration
than the nominal"*. It is now **"does `56552326`'s configuration match the adopted nominal in every
dimension, or only in the LR policy?"** — schema, seeds, epochs, `niter`, subsample, batch. A reviewer
who checks only the LR policy would find a match and stop.

**UNRESOLVED from this lane**: the configuration comparison needs `56552326`'s receipt, which is on
`/pscratch`. What closes it is a field-by-field diff of that receipt's `seed_policy` and configuration
block against the adopted nominal's, published rather than asserted — **not** a statement that both are
"the annealed configuration."

#### V23 NARROWED — the ledger is not silent, it is PRE-DISPOSITION, and one thing I nearly raised is already handled

Two corrections against myself after reading the whole `VL98–VL101` section rather than the rows.

**1. My "standing silently side by side" overstates it.** The section says, two lines under the table:
*"Per the predeclaration amendment, the adopted PRIMARY criterion decides and the PRIMARY/SECONDARY
disagreement is itself the finding."* So the ledger does record that PRIMARY governs. What it does not
record is that the escalation was **answered** — Joseph selected the annealed arm on 2026-08-13. The row
is a true statement of the pre-disposition state that reads as current. **That is `BEN-098`, not a
contradiction**: a section's stale parts are exactly the ones that were true when written, and nothing
in the text can expire on its own. The block stands and the required fix is smaller than I implied —
one clause on the row pointing at the disposition, not a rewrite.

**2. Something I nearly raised and should not have.** I went to check whether the ledger — the canonical
home for *technote-quoted* numbers — carries `VL100` from an artifact declaring itself
`quotable: False`. It does, **and it says so on its face**: *"This remains diagnostic and non-quotable.
No engine edit, threshold change, promotion, or Branch C reopening is authorized."* The ledger and the
receipt agree. Nothing to route. Recording the non-finding because the near-miss is the same shape as
routing a defect that existed only in a chat summary, two turns ago: **I checked the artifact instead of
reasoning from the category, and the category was wrong both times.**

#### The VL re-id destroyed blame ownership — I approved that re-id and did not check for it

`git blame` attributes **all 108 VL rows to `1ec042e`**, the re-id, reproduced here. A reported this as
unresolvable in both directions.

**It is recoverable, and A's mechanism is only half the cause.** `git blame --ignore-rev 1ec042e`
restores **18 distinct owning commits**. So blame was *masked*, not destroyed, and the standard remedy
applies: a `.git-blame-ignore-revs` file naming `1ec042e`, with `git config blame.ignoreRevsFile`.
**Limit worth stating: that config is per-clone**, so the file alone does not help anyone who has not
set it — it is a remedy for the repo's maintainers, not an automatic property of the history.

**But unmasking does not yield a lane for `VL101`.** It resolves to `c56fc5f`,
`Joseph Bailey <jrbailey555@gmail.com>` — the shared pre-`BEN-160` identity. So **there were two
independent causes and A conflated them**: the re-id masks ownership for all 108 rows, and underneath
the mask this particular row was already lane-unattributable for the reason `BEN-160` records. Removing
one does not remove the other, and A's conclusion is right for a cause A did not name.

**My part in this, which is the part worth carrying.** `V20` gave the GO on that re-id. I checked
freshness, consumers anchored on `^|`, the leading-vs-trailing decision, the 22/22/108 structural
post-condition, and the literal-dashes hazard. **I never asked what the edit does to provenance.** I
enumerated what could break *programmatically* and never asked what could break *evidentially* — the
coverage-invisible-by-construction shape applied to my own review checklist, on the one file whose whole
purpose is being citable.

#### V23 addendum — OI-23's configuration question is CLOSED; C's residual is real and I can size it

C published the field-by-field diff (`316475e`): `56552326` against `56563761`, 12 of 12 recorded
dimensions identical, including `estimator_seed 42`, `subsample_seed 0`, the input NPZ digest, and
2,000,000 rows per arm on both. **That answers my UNRESOLVED**: identical estimator seed *and* subsample
seed *and* input digest *and* row count means the same subsample, not merely the same schedule — which
is the dimension a reviewer stopping at the LR policy would have skipped, and the reason the warning was
worth issuing.

**C's residual is not pedantic, and the Gate-2 receipt I reviewed for `V21` sizes it.** `features`,
`truth_features` and `bkg_mode` are recorded by neither closure receipt, so schema equivalence is
*inferred* from the shared NPZ. That inference is weaker than it looks: `G2_GATE2_TARGET_RUNTIME_RECEIPT`
carries **`configuration.features` (13 entries) and `configuration.truth_features` (2)** as fields
*separate from* `input_preflight.sha256`. **The feature selection is therefore a configuration choice
made over the input, not a property of it** — two runs can share an NPZ digest byte-for-byte and select
different columns from it. So a shared input constrains the schema only in the sense that it bounds what
*could* be selected. NEARLY CLOSED is the correct state and C's named finish — record the fingerprint and
feature lists in the closure receipt — is the right one.

#### V23 addendum 2 — the feature-schema residual is CLOSED, by pins and by a guard neither of us cited

C discharged it (`9322003`) via the route I proposed — derive the selection from the code that does the
selecting, since a shared NPZ bounds what *could* be selected without pinning what *was*. Verified here
rather than accepted, all four claims:

    closure driver  a45fae7c  MATCH      loader defaults 13 == receipt configuration.features       True
    nominal driver  5fda80df  MATCH      loader defaults  2 == receipt configuration.truth_features True
    engine          3a2022b0  MATCH      neither driver passes feature_names/truth_feature_names
    loader          57f33f87  MATCH      (all such hits are READS of meta for reporting, not overrides)

Element-for-element equality, not length agreement.

**A second, independent mechanism neither of us cited, and it is stronger than the derivation.**
`train_fullevent_nominal.py:393` is not a behaviour switch — it is a **fail-closed guard**: if the loader
built `REDUCED_EVT_FEATURES` (the 2-column `{pT, p‖}` schema), the nominal **refuses**, because that
schema is marked *"CROSS-CHECK ONLY — never a publication lateral/central source"* and stamping the
publication fingerprint over it is audit finding J01. So the exact failure the residual described —
a run selecting a different feature set while claiming the publication estimator — is refused at runtime,
not merely improbable.

**Derivation from pins and a runtime refusal are different instruments**, which is the property that made
this worth closing properly rather than inferring from the input digest.

**Still open and correctly so:** full OI-23 discharge hangs on `56563761` remaining the final nominal,
which is Joseph's promotion call, not a verification result.

---

### V24 — `E_avail` audit: **Finding 1 is OI-30, live and blocked. Finding 2's code half is OVERSTATED.**

Read-only, **local tree at `origin/main`** (the fork caveat is answered below). No cluster access from this
lane, so every population number below is the codex census as relayed, not mine; everything about *code*
is measured here.

## Q3 — Finding 1 is not a new finding. It is `OI-30`, **LIVE and BLOCKED**, and its stated action is this exact check

`docs/OPEN_ITEMS.md:45` — *"`OI-30` | BLOCKED | Eavail definition / Gregor | … Reconcile the truth Eavail
definitions and **verify the charged-pion convention against arXiv:2312.16631 Equation 4**."* The long
form is `OPEN_ITEMS-ARCHIVE-2026-08.md:1005-1035`, and it already contains the whole finding: *"our
charged-pion mass constant is `135` — the pi0 mass; charged pi is 139.57 — worth ~4.6 MeV per charged
pion."*

**So the drafted Slack reply asserting Finding 1 is a bug would assert a resolution this repo records as
unsettled.** The archived item says in terms: *"Both look inherited verbatim from MAT
(`CCQE3DFitFunctions.h` / arXiv:2312.16631 Eq. 4, which our code cites); **that citation has not been read
against the code**, so which side matches the published convention is not established here."* The code
agrees — `CVUniverse.h:160-164` says *"Copied verbatim from MAT"* and names the same header and equation.
**Neither cited header is vendored in this tree**, so the verbatim claim cannot be checked from here. That
is the one action that closes it, and it is unchanged since 2026-08-12.

**AND THE 4.57 MeV IS THE SMALLER OF TWO DISCREPANCIES ON THE SAME TABLE ROW.** The archived comparison
against `minerva-ml` records: ours `pi+-` = **kinetic (E − 135)**, theirs = **total E**. The item's own
words: *"The charged-pion row is the material one: **~140 MeV per charged pion**, not a rounding
difference."* That is **30x** the constant error, it is definitional rather than numeric, and it is the
actual open question with Gregor. **A reply that leads with 4.57 MeV leads with the small half of a row
whose large half is unresolved.**

**On regeneration: I agree with the mediator and for a stronger reason.** *"No event-loop regeneration
needed"* cannot stand while a truth-value question is open — a census showing zero negatives and max
91.77 GeV is equally consistent with a uniformly shifted distribution, so it establishes non-negativity,
not correctness. But the regeneration question is dominated by the ~140 MeV definitional issue, not by
the 4.57 MeV constant, and settling `OI-30(i)` decides both at once.

## Q1 — **Contract/diagnostic gap, NOT a correctness defect. I am downgrading Finding 2's code half, with the code.**

The relayed claim is that a negative reco value *"is either dropped or lands in the highest `E_avail` bin
depending on which path touches it."* **Measured, the second half does not happen.**

    :105  histogramdd                     -> silently drops out-of-range              (confirmed)
    :533  np.digitize(c, edges) - 1       -> yields -1 for any negative               (confirmed)
    :538  `if not all(0 <= coord[a] < shape[a])`  -> **-1 fails this and gets weight 0, counted in n_zero**

`build_measured_training_nd` **bounds-checks before it dereferences**, so the `-1`-indexes-the-last-bin
hazard is real in the NumPy idiom and **unreachable at this call site**. Every other `digitize` in the
driver is `np.clip(..., 0, n-1)` (`:789`, `:790`). `:828` is a comment and documents the behaviour:
*"weight 0 via `build_measured_training_nd`'s digitize."*

**So the two paths do not disagree about where a negative goes — both exclude it.** One drops silently,
one assigns weight zero and counts it in `n_zero`, which is printed under `verbose`. The defect is that
the exclusion is not surfaced at analysis level, and that a reader of the idiom cannot tell the guard is
there. **That is a contract and reporting gap.** The latent hazard is worth recording: above the last
edge, `digitize - 1` returns `7` for a 7-bin axis, which the same guard also catches — unoccupied, since
truth max is 91.77 against a 100 GeV top edge.

**Deferrable?** Yes, for the code half — there is nothing to fix that changes a number. **A matched
current-vs-parity rerun is still the only thing that demonstrates the numerical null**, it needs no ROOT
rebuild, and at ~1e-5 of support the null is plausible and undemonstrated. **Plausible-and-undemonstrated
is exactly what a receipt must not report as verified.**

## Q2 — **(b)**, and the deciding argument is definitional, not the 2.3 sigma

**I addressed the tension rather than noting it:**

    predicted 53.39   data 73   diff 19.61
      data-only                       2.30 sigma   (the relay figure)
      + MC stat on 218/91 rows (3.04) 2.16 sigma
      + 15% background normalisation  2.08 sigma

**It narrows and does not close.** Caveat: my MC term uses mean-weight x sqrt(N) because I do not have
`sum(w^2)`; the exact figure needs it.

**But I would not decide (a) vs (b) on this.** A ~2 sigma excess in a 73-event region at 1e-5 of support
is an ordinary fluctuation, and choosing a repair on it is fitting the noise. **The decisive argument is
categorical: truth in-range with reco failed IS a miss.** That is what a miss *means* in a response
matrix, the codex split shows all 218 are truth-selected, and truth `E_avail` for them spans 0 to 21.11
GeV — large mis-reconstructions, exactly the population the miss category exists for. **(b) puts them in
the category the response matrix already has for their condition, and matches the data side, which
`_fid_mask` and `build_measured_training_*` already zero.** (a) invents a region, and would need a
matching data-side change to stay symmetric.

Clamping stays refused, and the mediator's measured argument is the right one: clamping would pile events
carrying up to 21 GeV of true available energy into the lowest reco bin.

## Fork caveat — closed for the reco path, and I checked closure rather than assuming it

SHA-256 identity local-vs-cluster was reported for three files. **The `pass_reco` / `_fid_mask` /
`build_measured_training_nd` definitions I relied on are all inside `unfold_nd_omnifold_unbinned.py`**, so
the reco half of this verdict is closed over the covered set. `unfold_3d_omnifold_unbinned.py` **is not in
this tree at all**, so any 3D-specific claim is outside what I checked. The quoted hashes were truncated
to 8 hex characters, which I did not re-verify.

---

### V25 — independent derivation of the 5D reported-bin mapping, and a discriminating test

Derived from artifacts without reading Session A's mapping or code. **Read-only, local tree at
`origin/main`. I opened no ROOT file: `CEN5`, `CEN4` and the covariance are cluster paths and this lane
has no cluster access**, so this is the mapping plus a test someone with access must run — not a
completed check.

## The mapping

    p4_lib.py:22    GRID_NBINS = 65856   # 14*16*7*7*6 full 5D grid (pt,pz,eavail,q3,W)
    p4_lib.py:1106  require(m.ndim == 1, "mask must be 1-D (C-order ravel over the 5D grid)")
    p4_lib.py:750   vol = _np.multiply.outer(vol, w).ravel()   # C-order product of bin widths
    p4_evidence.py:112  man = {"grid_nbins": P.GRID_NBINS, "corder": "C", ...}

    flat = ((((i_pt*16 + i_pz)*7 + i_eavail)*7 + i_q3)*6 + i_W)
    C-order strides   pt 4704 · pz 294 · eavail 42 · q3 6 · W 1

Row `r` of `hCov_combined5d_total_uthrow` is the `r`-th `True` of that 1-D ravel in ascending flat index.

**Corroborated from a second, independent file.** The axis lengths are not taken from `p4_lib.py`'s
comment alone — `unfold_nd_omnifold_unbinned.py`'s edge table gives `eavail` 8 edges = **7** bins (`:76`),
`q3` 8 edges = **7** (`:81`), `W` 7 edges = **6** (`:93`), matching `14*16*7*7*6` in the stated order.
Two files, one written for the covariance path and one for the unfolder, agree on the factorization.

## THE HAZARD THIS TASK EXISTS FOR, MADE EXPLICIT

**`eavail` and `q3` both have length 7.** A swap of those two axes is **dimensionally silent** — the
reshape succeeds, no error is raised, every downstream shape check passes, and the projection is
plausible. Their *edges differ* (`eavail` `[0,.1,.2,.4,.8,1.5,3,100]` vs `q3` `[0,.2,.4,.6,.8,1.2,2,100]`),
so the result is wrong physics with correct arithmetic. **This is the one transposition a convention
string cannot exclude and a shape assertion cannot catch**, and it is between the two axes most easily
confused. `corder: "C"` in the manifest is a *declaration*; it is not evidence that the producer honoured
it.

## The discriminating test — uses a SEPARATE artifact, not this mapping's assumptions

Marginalise the 5D mask over `W` and compare it to the independently stored **4D** mask.

    m5 = mask5d.reshape(14,16,7,7,6, order="C")
    m4_from5 = m5.any(axis=4)              # -> (14,16,7,7)
    compare against CEN4's own mask, reshaped (14,16,7,7);  14*16*7*7 = 10976 = 65856/6

**Why it discriminates.** Under an `eavail`↔`q3` swap the `(eavail,q3)` plane of `m4_from5` is the
**transpose** of the 4D mask, and the two edge vectors differ, so the masks are not symmetric and the
comparison fails. Under F-order every axis is wrong and it fails harder. `p4_lib.py:990`
`cmask_order_hash_4d` exists for exactly this object and its docstring at `:1009` states the property the
test needs — *"a transposed/reshaped M cannot collide with the original."* So the comparison can be run as
a hash equality rather than an array diff.

**Discriminating power, stated rather than assumed:** the test fails under `eavail`↔`q3` transposition,
under F-order, and under any axis permutation that moves `W`. It does **not** discriminate a `pt`↔`pz`
swap (14 vs 16 — but that one is *not* silent: the reshape raises). It cannot detect an error present
identically in both the 4D and 5D masks.

## What I could not verify

- **I opened no ROOT file.** The adopted covariance
  (`.../universe_stage2_5d/uq_universe_5d_covariance_combined_uthrow.root`, 892,224,371 B), `CEN5` and
  `CEN4` are all cluster paths. I state the path and size **as relayed**, not as read — the artifact
  caution about the `_cvcentered` sibling and the `_archive_prehm_20260713` variant is exactly why I will
  not assert which file I used when I used none.
- **The 10,694 dimension is unread.** I did not confirm the matrix is 10,694-square, and I specifically
  did not reconstruct it from file size: A's 890-vs-915 MB argument was arithmetically tight and false
  because ROOT compresses, and the same trap is available to me.
- **The 4D-mask test rests on one assumption I could not check**: that the 4D and 5D reported-bin
  criteria are the same selection. `FINDING-20260809-stage6-central-gate-cannot-pass.md` records that
  5D→4D marginal and independent 4D disagree at median 4.43% *in values*; whether their *masks* coincide
  is a different question and I have not established it. **If they do not, the test needs a different
  second artifact** — and that, not the mapping, is where I would look next.
- 10,550 + 144 = 10,694 reproduces, so the PET-COMMON subset and the full GBDT reported set are distinct
  as stated. I did not verify which set the stored matrix uses.

#### V25 PREDECLARATION — what each outcome licenses, written BEFORE the run

I designed the test and I have been named its adjudicator. That is the configuration in which a result
gets read favourably after the fact, so the reading is fixed here first.

**A POSITIVE CONTROL IS REQUIRED, NOT OPTIONAL.** As specified, the test has never been made to fail.
Run it twice:

    PASS ARM     m4_from5 = mask5d.reshape(14,16,7,7,6, order="C").any(axis=4)
    CONTROL ARM  m4_swap  = mask5d.reshape(14,16,7,7,6, order="C").swapaxes(2,3).any(axis=4)

**The control arm MUST disagree with the 4D mask.** If both arms agree with it, the `(eavail,q3)` plane
is symmetric on this data and **the test is not discriminating here** — that outcome is VOID, not a pass,
and it is the one I would otherwise be most tempted to accept. This is my own "a gate that examines zero
items must never print a pass," pointed at a gate I wrote.

| outcome | adjudication |
|---|---|
| control FAILS, pass arm AGREES | **mapping CONFIRMED** for C-order and the stated axis assignment |
| control FAILS, pass arm DISAGREES | **mapping REFUTED.** Then try `swapaxes(2,3)` against the 4D mask — if *that* agrees, the producer transposed `eavail`/`q3` |
| control AGREES (either arm) | **VOID.** Test not discriminating on this data; needs a different second artifact. Not a pass |
| 4D/5D selection criteria differ | **VOID before running.** A failure cannot be attributed between wrong mapping and different selection. Settle this first |

**And the order matters:** the selection-criteria question must be settled *before* the run, not used to
explain a failure afterwards. An explanation available only after seeing the result is not a control.

**What a PASS does not license.** It confirms the mapping of reported rows to grid cells. It says nothing
about the covariance's dimension (10,694 unread by me), which set it is on (full GBDT vs the 10,550
PET-COMMON subset), or whether the projection onto the `E_avail` marginal is correctly weighted by bin
volume — `p4_lib.py:750` builds that volume vector by the same C-order ravel, so a mapping error and a
volume error would share a cause and **agree with each other**.

### V25 RULING — the two-arm run is **VOID**, and re-running it in the correct order is **also void**

**Two branches of my predeclared table fired at once**, which is the case the table was written for.

    control FAILS, pass arm DISAGREES        -> mapping REFUTED
    4D/5D selection criteria differ          -> VOID BEFORE RUNNING

**The precondition branch takes precedence, and not as a tie-break.** A precondition *gates* a test; it
does not compete with the test's outcome. A run whose precondition is false does not return REFUTED — it
returns nothing. `p4_lib.py:1217` establishes the criteria differ: *"5 of the 4830 reported 4D bins
receive no contribution from any reported 5D bin"*, committed `a1c9d10` 2026-08-09, four days early, a
different author, a different purpose, and matching on **both** numbers. So the VOID branch is triggered
literally, and its trigger has nothing to do with how small the difference is.

**I am not letting 1330x do the work.** Control 6,651 against pass-arm 5 is three orders of magnitude and
reads as decisive, which is exactly the condition under which a favourable reading is easiest and the
reason I fixed the table before the data existed. Renegotiating it now because the number came out well
is the failure the predeclaration was written to prevent.

**But "redo it in the correct order" buys nothing, so do not task it.** The precondition is now *known*
false. Running the same test in the right order fires the same VOID branch before any data. The ordering
error cost the status of this answer; it did not cost information, and the information is not recoverable
by repeating the procedure. **The repair is an amended test, not a re-run.**

### The amended test — a precondition that can actually hold

    EXCLUDE the 5 documented 4D bins (p4_lib.py:1217) from the comparison set.
    PASS ARM     m4_from5 vs the 4D mask over the remaining 4,825  -> require EXACTLY 0 mismatches
    DIRECTION    require 0 in the 5D-reported-with-no-4D-bin direction, unconditionally
    CONTROL ARM  swapaxes(2,3), same exclusion                     -> must still FAIL

The exclusion is legitimate *only because it is documented independently and in advance*; it is a
precondition, not a carve-out fitted to the residual. If the control arm's 6,651 does not survive the
exclusion, the exclusion is too large and the test is void again — that check is not optional.

### The evidence that makes me expect it to pass, labelled as what it is

**The direction is the discriminator, and nobody drew it.** All 5 mismatches are 4D-reported-with-no-5D-cell;
**0** are the reverse. **A mapping error scatters cells and populates BOTH directions** — a transposition
sends 5D cells to wrong 4D coordinates, producing orphans on both sides. **A pure selection difference
populates exactly one.** Observed: one, and the documented mechanism predicts that one.

That is a strong argument and it is **mine, produced after seeing the result**. It is a reason to expect
the amended test to pass. **It is not a substitute for running it**, and I will not promote it into a
verdict — which is the same discipline I applied to `R/push` and got right for a bad reason, and am now
applying with a good one.

### Not covered, and still owed

The projection remains unpromoted and should. `p4_lib.py:750` builds the bin-volume vector by the **same
C-order ravel** as the mask, so a mapping error and a volume error share a cause and would agree; the
projection needs its own check and cannot inherit this one. A was right to hold it.

**A's conduct is the part to reinforce:** it disclosed the ordering error unprompted, refused to
self-resolve a test it had run, caught its own width-weighting prescription (`8.47%` against `13.69%` —
a 2.7x underestimate that would have looked plausible), and avoided shipping it only by reusing the
tracked tool instead of writing its own `M`. Three of those are the same reflex.

### V27 — amended mapping test **PASSES**. Projection: **PROMOTE FOR THE MATERIALITY USE ONLY**, two residuals, one of them new

**The amended test passes all four conditions and the non-optional one is met to the unit.** Control was
6,651 before the exclusion and 6,646 after; `6,651 − 5 = 6,646 = 3,323 × 2` exactly. The exclusion removed
precisely the 5 documented cells and is demonstrably not what produces the pass. **The construction choice
is what makes it non-vacuous**: A applied the exclusion as a **fixed set of 5 cells**, not as *"bins the 5D
support fails to reach"* — the computed form would have absorbed a mapping error's mismatches by
construction. A chose the version that can still fail.

**Mapping: CONFIRMED.** My one-directional-orphan prediction held and I am not citing it as corroboration —
it was produced post-hoc and A was right not to lean on the positional pattern either.

### A SECOND RESIDUAL, WHICH NEITHER A NOR THE MEDIATOR NAMED

**Everything verified so far concerns the MASK. Nothing verifies that the covariance matrix's ROW ORDER
matches the mask's enumeration.** The only binding is `p4_lib.py:1300`:

    require(M.shape[1] == C_high.shape[0], f"M cols ... != C dim ...")

That is a **shape** check, and a shape check cannot see a **permutation**. Under a consistent row+column
reordering of `C`:

    trace / sqrt_tr_old / sqrt_tr_new     PRESERVED EXACTLY  -> the receipt's scalar summary is blind
    multiset of diagonal entries          PRESERVED          -> per-bin sigma still looks normal
    M.shape[1] == C.shape[0]              PASSES
    per-bin assignment                    DESTROYED          <- the only casualty, and nothing checks it

`p4_evidence.py:409` pins `mask5d_hash` against a hardcoded `OBS` constant, which fixes the *mask*. The
covariance is produced by a separate stage-2 universe job; I found nothing binding its row emission order
to that mask.

**This changes the promotion calculus, and it is why I am not simply adopting the mediator's reading.**
Promote-on-materiality works against a *small* shared convention error: a 4.4x margin absorbs it. **It does
not work against a permutation**, because a permutation preserves the scale of the projected uncertainty
while destroying its per-bin meaning — the marginal would land plausibly inside 4.4x and be wrong anyway.
Materiality is the wrong shield for this residual.

### RULING

**PROMOTE, scoped: the number may be used for the order-of-magnitude materiality check it was computed
for, with both residuals recorded on the artifact.**

    RESIDUAL 1 (A / mediator)  both checks reference the 4D chain, so a global axis-convention error
                               shared by the 4D and 5D producers survives both. Mitigated only by the
                               `unfold_nd_omnifold_unbinned.py:76/:81` edge table, which is outside that
                               family, and by the one-directional orphan result.
    RESIDUAL 2 (this verdict)  the covariance's ROW ORDER is unverified against the mask; the existing
                               guard is a shape check and the receipt's summary is trace-based, so both
                               are blind to a permutation.

**Required before this number is used for anything PER-BIN rather than in aggregate:** correlate the
covariance diagonal against the central values bin-by-bin. Under the correct order they track; under a
permutation the correlation collapses while every existing check still passes. **That uses the central
values as the instrument — a different one from both the mask and the 4D chain**, which is the property
neither existing check has. It is cheap and it needs no rebuild.

**Why not BLOCK.** Residual 2 is unverified, not suspected — a wholesale permutation would be an odd bug
and the producer chain is shared with the central values. Blocking a materiality check with 4.4x margin on
an unevidenced permutation would be the mirror of promoting on 1330x, and I declined that one for the same
reason: neither a favourable number nor an unfavourable imagination is evidence.

### V28 — residual 2 **CLOSED**. The per-bin **verification** gate lifts; the per-bin **granularity** question is not mine and must not be folded into it

**Residual 2 is closed.** `S1` Spearman `+0.9947` real against `-0.0106` control is a gap of `1.0053` on a
bounded statistic; `S3` is `363x`. The predeclaration is genuine and was checked rather than taken —
`3de5143` committed `03:16:41`, result `cbce0ad` at `03:18:16`, 95 s later, and `3de5143` is an ancestor of
`cbce0ad`. A applied the ordering discipline unasked, after I had insisted on it once.

**All three residuals are now closed by three different instruments** — axis assignment by the 4D mask,
volume weighting by the 4D chain's different width products, row order by the central values. On
correctness that is as independent as this artifact admits.

**S2 IS THE FINDING AND IT IS A's AGAINST ITSELF.** Control median frac `14.746%` against real `13.761%` —
one of the three statistics **would have passed a permuted matrix**, because a median of a ratio is robust
to permutation when the two distributions have similar medians. **The adjudication survives because the
predeclaration set per-statistic thresholds rather than requiring the battery to collapse as a whole.**
That is foresight in how the table was written, not margin in the result, and it is the generalisable
half: **predeclare each statistic's threshold separately, because a battery scored as a unit hides the
member that has no power.**

### The ruling, in two parts that must stay separate

**1. The per-bin VERIFICATION gate LIFTS.** Nothing remaining in the verification blocks per-bin use. The
scope condition I attached in `V27` is discharged.

**2. Whether per-bin is the right GRANULARITY is NOT a verification question and I am not deciding it.**
Per-bin fractional uncertainty spans `3.47%` to `213.8%`; above 100% the central value is roughly
consistent with zero, and quoting such a bin invites a reader to treat it as measured. That is a physics
call — Joseph's or the analysis's — and **folding it into a verification PASS would decide it invisibly**,
which is the failure mode this lane exists to prevent. Verification PASSES; granularity is ROUTED. They
must not be merged into one word.

**One requirement that IS mine, and the codebase already agrees with it.** A per-bin number must not
travel without its own fractional uncertainty, and the artifact must record **the COUNT of bins over
100%**, not only the `3.47–213.8%` span. A span says extremes exist; a count says how much of the
deliverable they are, and nobody has produced it. This is not a new rule:
`crosscheck_marginal_vs_independent` (`p4_lib.py:1343`) already *"returns the full distribution rather
than a max, because on the real products the max is owned by a handful of near-empty bins and is actively
misleading about the body of the comparison (`BEN-064`)."* The near-empty-bin problem is known, recorded,
and already shaped that function's interface. The per-bin lift should inherit that, not re-derive it.

**Fourth instance of cite-without-opening**, and `:1343` is stronger than it was relayed to me: it is
`REPORT ONLY -- no pass/fail, by specification`, it is exactly the 5D-vs-independent-4D comparison A
performed by hand, and its docstring says so plainly. Like `:1318`, it is honest in its own text and
dangerous only to a reader who cites it without opening it. That is now `BEN-172`'s mechanism four times
in one night, three of them in this file's neighbours.

**A's third float-equality slip, filed against itself as one pattern rather than three incidents, is the
right aggregation** — and the invariant it replaced the bad check with (`sorted(diag)` identical) is the
one that actually demonstrates why the trace cannot see a permutation, which is the claim `V27` rested on.

### V29 — advisory on Gate 6: **13.9x is not quotable as a margin**, for two reasons, and the second is not about precision

A's floor correction is right and the verdict is unchanged: the spread exceeds **both** floors, so the
ensemble resolves estimator variation either way. Only the margin moves, `1792x` → `13.94x`. What follows
is about whether that number can be quoted, not whether the branch passes.

**REASON 1 — `n=1` is a factor-of-a-few estimate, and it is STRUCTURAL rather than a shortcut.**
The across-process floor is a single `|difference|` draw. For `d = x₁ − x₂` with sd `s`, `|d|` has
`E ≈ 1.13 s` and a spread of roughly `0.76 E`, so one draw locates the floor to within a factor of a few:

    true floor = 1.5x the observed draw  ->  margin 9.3x
                 2x                      ->  margin 7.0x
                 3x                      ->  margin 4.6x

All still exceed. **But `13.9` is a point estimate carrying no dispersion, and it should not be written as
if it were a measurement.** And the reason `n=1` cannot be improved matters: **member 1 is the only member
that replicates the nominal's seed policy**, so it is the only across-process control that exists in this
ensemble. Members 2–5 confound seed variation with process variation. A did not take a shortcut; the
design admits one pair. That makes the imprecision irreducible from existing artifacts and worth stating
as such rather than apologising for.

**REASON 2, AND IT IS THE ONE THAT DECIDES IT — the numerator is the population being routed to Joseph.**
Member deviations are `0.101`, `0.180`, `0.247` against a nominal `0.0356`, and the spread is `0.2272`.
`0.247 − 0.0356 = 0.2114` — **essentially the entire spread is set by the members that exceed
`fold_forward_ratio_dev_max = 0.05`.** Those are exactly the members whose status — estimator variation or
unconverged — A correctly declined to adjudicate and the mediator is routing to Joseph.

**So `13.9x` is not merely imprecise, it is CONDITIONAL on an unresolved physics question.** If those
members are unconverged, the numerator is inflated by the very population under question and the margin is
overstated by an unknown amount. The margin and the routed question are not independent, and I do not
think anyone had connected them.

**Recommended output**, and it is not a hedge — it is the operand set: *"the member spread exceeds an
across-process floor estimated from a single pair; the ratio is ~14x on that estimate, and both the floor's
precision and the spread's composition are open."* Quote the two floors, the five member deviations, and
the pair the floor came from. That is `BEN-077` — a reader who has the operands can see the conditionality;
a reader given `13.9x` cannot.

**This is my magnitude question in its own costume, and the answer is the reverse of last time.** At
`1792x` nobody needed to name the error classes the margin could see, because none of them were that large.
At `13.9x` two are: a single-draw floor fluctuation (bounded, survivable) and an inflated numerator
(unbounded until the convergence question is answered). **A margin only shields against errors smaller
than itself, and one of these is not yet sized.**

### On member 1 as a control — what the driver hash does not cover

The byte-identical driver hash between `54a8797` and `5fda80df` is a strong control **for code and seed
policy**. It is not a control for the **execution environment**, and for an ML training that is precisely
where across-process variation lives: GPU model, cuDNN algorithm selection, reduction order under atomics,
thread counts, CUDA/TF library versions on the node. A code hash cannot see any of them.

**This cuts both ways and that is why it should be stated rather than assumed.** If member 1 ran on
different hardware from the nominal, the floor **absorbs** hardware variation and is inflated — making the
margin conservative. If on identical hardware, the floor is cleaner but less representative of what the
ensemble's spread actually samples. **The control's scope is unknown until someone says which.**

**Cheap and checkable:** Gate 2's receipt schema already carries `execution.host`, `environment.platform`,
`environment.tensorflow` and `environment.python`. Compare those four fields between the nominal's receipt
and member 1's. If they match, the control is tight and should say so. If they differ, the floor is an
across-*node* floor and should be labelled as one. If the member receipts do not record them, that is the
finding.

---

# Round 2 — sole-auditor pass over C (Gate 5), B (Gate 6), A (E_avail), 2026-08-13

Fresh process (started `12:26:14Z`). Nothing below resumes a prior adjudication; every claim was
re-derived. Read-only throughout: no tracked file outside `docs/orchestration/` was modified, no job
touched, no cluster write. Repo measured at `origin/main` = `39b0021`; this worktree at `c249f78`, three
commits behind, and I confirmed by `--stat` that all three are documentation-only.

## V30 — Gate 5 / lane C: `train_fullevent_replica.py:112` — **BLOCK, scoped to provenance.** The defect is now EXECUTED rather than argued, and it reaches further than any of its three writeups say

**What was already known and is correct.** `BEN-149`, `c249f78`'s body, and
`state/gate5-source-npz-verified-20260813.json` all describe :112 accurately: the source NPZ is checked
by path and size, the receipt is checked for *carrying* a sha256, and then the receipt's own claim is
copied into a field named `_verified_input_sha256`. The file is never hashed. C measured the real file
out of band (`fa6b3463…`, 9,897,374,636 B, 42.6 s) and it matches. I re-read the code and confirm every
one of those statements.

**What was asserted but not demonstrated, and now is.** All three writeups say a same-size substitution
"would still pass unnoticed." I rebuilt the committed acceptance test's own fixture
(`test_gate5_replica_driver.py::target_receipt`, reproduced byte-for-byte) and ran four arms against the
real `read_replica_target_receipt`. Artifact:
`docs/orchestration/state/probe-gate5-verified-input-sha-20260813.py`.

```
[A0 baseline, nothing touched]              expected PASSED         observed PASSED
    _verified_input_sha256=cea2990714915956   actual file sha=cea2990714915956   equal=True
[A1 SOURCE substituted, SAME size 24 B]     expected FAILED-CLOSED  observed PASSED   *** ***
    _verified_input_sha256=cea2990714915956   actual file sha=81cd0be5ef193b7c   equal=False
[A2 SOURCE substituted, size changes]       expected FAILED-CLOSED  observed FAILED-CLOSED
    "[gate5-train] source dump size differs from target receipt"
[A3 TARGET one bit flipped, SAME size]      expected FAILED-CLOSED  observed FAILED-CLOSED
    "[gate5-train] target SHA-256 differs from its receipt"
```

**A1 and A3 are the whole finding: the identical mutation class, two lines apart in one function, caught
on the target and not on the source.** A2 is the control proving the probe reaches its subject — without
it, A1's pass is indistinguishable from a probe that never ran. A0 is the part that matters to a reader:
**when nothing is wrong the field is right**, so no amount of spot-checking published values finds this.

**My probe's first run was itself a vacuous pass, and A0 is the only reason I caught it.** All four arms
died at `target path differs from the path owned by its receipt` — on macOS `tempfile` yields `/var/…`
while `Path.resolve()` yields `/private/var/…`, and the fixture stores the resolved form. Three of the
four arms reported "as expected" because failing closed was what I expected of them. Without the baseline
arm I would have reported a confirmed finding from a probe that never reached the code. Recorded because
it is the same shape as the defect being audited.

**RESIDUAL 1, NEW — the committed test cannot fail on this.** `test_gate5_replica_driver.py:67-82` is the
test *of this function*. It asserts `_verified_target_sha256 == sha256_file(target)` (`:72`) and **tampers
the target** (`:77`) to prove that check bites. There is no assertion on `_verified_input_sha256` and **no
tamper of `source` at all**. The positive control exists for the computed field and is absent for the
copied one. Separately, `:87` in the next test performs the copy itself —
`rec["_verified_input_sha256"] = rec["input_preflight"]["sha256"]` — so the fixture reproduces the code's
rule and cannot exhibit disagreement with it.

**RESIDUAL 2, NEW AND THE ONE WITH GATE CONSEQUENCES — the copied value is not inert; it is published.**
`train_fullevent_nominal.py:359` binds `target_receipt = assert_target_provenance(...)`, and `:642` stamps
`inputs_sha256=np.asarray(target_receipt["_verified_input_sha256"])` into the training artifact. The
adapter's `replica_atomic` (`train_fullevent_replica.py:196-230`) augments the array dict and does **not**
overwrite that key, so it ships. The comment at `:639-641` reads *"Already computed and CHECKED against
the receipt by assert_target_provenance; reused rather than recomputed, so the artifact records the digest
that was actually verified."* **That comment is TRUE on the nominal path** — `:277`
`got_in_sha = sha256_file(inputs_npz)`, compared at `:278`. **It is FALSE on the replica path**, because
`run_nominal_adapter` replaces `assert_target_provenance` with `replica_provenance`
(`train_fullevent_replica.py:140-147`), which returns the receipt from `:112`. Same consumer line, same
comment, opposite epistemic status — `BEN-149`'s own shape one level up, in a comment instead of a field
name.

**And nothing downstream re-checks it for replicas.** `validate_pet_nominal_gate4.py:1029-1030` *does*
hash independently (`src["inputs_sha256"] == _sha256_file(inputs_npz)`) — but that is the nominal Gate-4
validator, and `extract_fullevent_fps.py:178-181` **refuses** any artifact with `bootstrap_seed != -1`
("this path extracts the NOMINAL, fail closed"). The replica path rides `combine_cstat_bkgsub*.py` /
`replica_manifest`, and `inputs_sha256` appears in neither. **So the copied value will be the only
in-artifact record of source identity across all 50 Gate-5 replicas.**

**VERDICT.** Gate 5 execution: **not blocked** — the source file is in fact correct, by C's measurement,
so no member is training on the wrong dump. **Quoting `inputs_sha256` from any Gate-5 replica artifact as
verified provenance: BLOCKED.** It is a relayed claim in all 50.

**The consequence for `c249f78` that belongs where the gate can see it:** C's out-of-band measurement is
not belt-and-braces. It is the *only* independent check of source identity that exists for the Gate-5
replica family, and it is currently reachable only from a `state/` receipt and a commit body. It needs to
be cited from Gate 5's own receipt, or the family ships with its provenance resting on a document nobody
downstream reads.

## V31 — the deferral reason for the :112 repair is **REFUTED as non-discriminating.** The conclusion is right; the reason given is not the reason

`state/gate5-source-npz-verified-20260813.json:49` and `c249f78`'s body both say the one-line repair is
*"Deliberately NOT done while the campaign runs: editing the driver would break
`GATE5_EXPECTED_TRAIN_DRIVER_SHA` for every member still to start."*

**Mechanism, verified.** `submit_gate5_replica_n50.sh:50` computes the pin once at submit from
`${CODE_ROOT}/nd-unfolding/pet/train_fullevent_replica.py` and exports it;
`sbatch_gate5_replica_train_array.sh:20,24,42` re-reads `${GATE5_CODE_ROOT}`'s copy at task start and
compares. `GATE5_CODE_ROOT=/pscratch/sd/j/josephrb/gate6traj-reconcile-56847059` — **not this repo.**

**Three measurements against the stated reason.**

1. C's *own* earlier receipt, 50 minutes before, `state/gate5-n50-progress-56857232-20260813.json:46`:
   *"Editing the repo tree cannot reach these members."* The two receipts contradict each other.
2. `:41` of the train launcher checks `git -C "$CODE_ROOT" rev-parse HEAD == $EXPECTED_HEAD`, which fires
   on **any** commit pulled into CODE_ROOT — driver or not. This guard cannot distinguish the :112 repair
   from any other commit.
3. **Already realized empirically.** Three commits landed on `origin/main` during the campaign —
   `b8159ad` 08:10:32, `0198c7e` 08:28:22, `39b0021` 08:36:16 EDT — and the 08:37:33 reading has targets
   at 13 COMPLETED / 10 RUNNING and training at 10 RUNNING. Repo commits demonstrably did not trip the
   pin. **The :112 repair carries exactly the marginal risk those three carried: zero.**

**I tried to refute this and found the strongest counter-argument, which does not save the reason.**
`88785a1` records C correcting itself: the cluster checkout *is* a git repo with a GitHub remote, 309
commits behind "because nobody has pulled, not because it is disconnected" — *"the isolation is a POLICY
barrier … and not a technical one."* True, and it applies to CODE_ROOT as well (the submit script runs
`git -C "$CODE_ROOT"` at `:19-20`, so CODE_ROOT is a checkout and can pull). **But that hazard is already
fully present from the three commits above.** A reason equally true of every commit made during the
window cannot be the reason *this* commit is withheld.

**VERDICT: the conclusion "do not touch CODE_ROOT" is CORRECT. The reason as written is REFUTED.** The
cost is not hypothetical: `docs/OPEN_ITEMS.md` and `KNOWN_ISSUES.md` grepped for
`train_fullevent_replica` and `BEN-149` return **zero hits**. The repair is deferred behind a blocker that
does not hold, with no owner and no trigger — so when the campaign ends, nothing fires. **Routed to C:
either land the repair now (a repo commit cannot reach the running members), or give it an OI number.
Not my call and not my edit.**

## V32 — Gate 6 / lane B: **UNRESOLVED**, and that is the honest branch rather than the nearer of the other two

Block confirmed intact at `19585b7` ("Block Gate 6 after member trajectory control", Joseph, 2026-08-13
05:44 EDT). Searched all branches for Gate-6 commits after it: the only two are C's `d9b09b6` and
`f69d6cf` (06:39, 06:42), both analysis. **Lane B has committed nothing since 2026-08-12 10:29**
(`7b9afe8`, a `BEN-117` compression). No committed movement toward execution.

**What I could not check, stated rather than rounded up to PASS.** This session is worktree-isolated and
the harness refuses git operations targeting other worktrees, so I cannot read lane B's uncommitted state;
and I cannot reach `/pscratch` or Slurm from this checkout, so **every job-state number in this pass came
from the orchestrator's relay, not from a command I ran.** Per `CLAUDE.md`'s rule that IDs and counts must
come from a command run in the same turn, the Gate-5 counts quoted in V31 corroborate a conclusion that
the commit timestamps already establish without them. **"No committed movement" is what I verified; "B is
not executing" is not.**

## V33 — lane A / `OI-30`: **PASS**, and it passes the check that is usually unfalsifiable

`OI-30` is now split (`OI-30` = the `135` constant; `OI-56` = the species rule, FROZEN). V24's Finding 1
is closed: Eq. 4 was read directly at `arxiv.org/html/2312.16631v2`, and the ~140 MeV kinetic-vs-total gap
I had flagged as the material half resolves in our favour.

**I re-derived every quoted number from the row's own operands — `BEN-077`, and it is the only heuristic
here that has caught a defect with nobody suspecting one:**

```
1.0563 pi+-/evt x 4.57 MeV/pion  = 4.8273 MeV/evt      row says 4.827     OK
439 / 65,911                     = 0.66605 %           row says 0.666%    OK
1.049 / 13.69                    = 7.66 %              row says 7.7%      OK
7.66% x sqrt(1507)               = 297.5 %             row says 297%      OK
```

The bracket `[7.7%, 297%]` is not two independently asserted endpoints — the upper is the lower times
`sqrt(1507)`, exactly the perfect-correlation-to-perfect-independence span the row says it is. **It could
have contradicted itself and does not.** The row also states plainly that the naive end is the most
favourable reading rather than the answer, and that the denominator's own `VL62/63/64/65` are OPEN. No
finding.

---

# V34–V40 — sole-auditor pass on `docs/EAVAIL_DEFINITION.md` (`bcdb388`)

> **STATUS AFTER `4788598`, added 2026-08-13 before pushing.** Lane A source-checked the same document
> in parallel and **independently found V35, V37, V38 and V40(a)**, landing repairs at `4788598` while
> this pass was still running. Two auditors approaching from different directions converged on the same
> spine sentence, which is worth more than either finding alone. **Current state of each verdict below:**
>
> | | verdict | now |
> |---|---|---|
> | V35 | five-species claim | **CLOSED** — `4788598` rewrites §1 to *"MINUS e±… we implement four of them"* and deletes *"deliberately"*. Lane A's `BEN-220`, filed with better detail than mine; my `BEN-174` is reduced to a pointer. |
> | V36 | `kEAvail` relabelled as "the open convention" | **LIVE** — §2 unchanged. Not found by lane A. |
> | V37 | who gets which verb | **SUBSTANTIALLY CLOSED** — the e± mirror is now adjacent to the defect sentence in §1. The verb itself stands; the reader can no longer meet it alone. |
> | V38 | §5 had one self-cutting item | **CLOSED** — `4788598` adds §5 item 6, for the reason I gave. |
> | V39 | five-site list over six sites | **LIVE** — unchanged, and the omitted site is in the live PET path. |
> | V40(a) | the `:1043` citation | **SUPERSEDED by `BEN-219`, and my version was wrong** — see the correction inline. |
> | V40(b) | provenance sorted by effort | **LIVE** — provenance section unchanged. |
>
> **Nothing was re-litigated to preserve authorship.** Where lane A got there first or got it more right,
> that is recorded as such.

**Commissioned by `personal-orchestrator`, who wrote the document and correctly declined to check it.**
It is the only artifact in this campaign written to go in front of an external collaborator: Joseph
intends to paste it to Gregor Kafka and defend it line by line. Audited at `bcdb388`, which is
`origin/main`'s tip; lane-d fast-forwarded to it. Read-only throughout — no code, launcher, ledger row,
`values.tex` or gated artifact touched; the only writes are this file, the `FINDINGS.md` rows, and one
probe under a path this lane owns.

**Verdict on the document as a whole: BLOCK — do not send as-is.** Four defects reach the
collaborator-facing text and **three of the four run in the flattering direction**. None of them is an
arithmetic error; the arithmetic is clean, which is the point. Repairs are small and are the author's to
make.

## V34 — the two questions asked directly, answered first

**(a) "Check I did not introduce a third rounding error." — PASS. No third error.** Re-derived every
number from its source row's own operands:

| claim | re-derivation | source |
|---|---|---|
| fidelity ratio `37.6x` | `4.837 / 0.1286 = 37.61` | `OI-56` (which rounds to `37x` off `4.84`; same operands) |
| `4.827` MeV/event | `1.0563 x 4.57 = 4.8273` | `OI-30(c)` |
| `439 / 65,911 = 0.666%` | `0.0066605` | `OI-30(c)` |
| bracket lower `7.7%` | `1.049 / 13.69 = 7.6625%` | `OI-30(d)` |
| bracket upper `297%` | `7.6625% x sqrt(1507) = 297.4%` | derived in the document, not in `OI-30` |

The upper end **only works from the unrounded `7.66`** — `7.7 x sqrt(1507) = 299`, not `297`. The
document states `7.66%` explicitly and is therefore self-consistent. The correction the author made
before committing is sound and I could not break it.

**(b) "Scope creep — it must adopt nothing, unfreeze nothing." — PASS, cleanly.** `OI-56` is named
**FROZEN** at :8; §4 closes *"Computing this further is `OI-56`'s arithmetic pointed at a published PASS,
and `OI-56` is frozen. That is Joseph's decision, not a lane's"*; §3 closes *"Not applied; nothing quoted
moves"*; `OI-40` is respected at :9-10. No sentence in the document reads as a decision. This is the one
thing the author was most at risk of getting wrong under time pressure and it is right.

## V35 — BLOCK: the headline paragraph claims a five-species list the code and the ledger both call four

`docs/EAVAIL_DEFINITION.md:16-18`, the paragraph explicitly framed as *"The position, in one paragraph"*
and therefore built to be extracted and pasted standalone:

> **We implement the Rodrigues 2016 convention** (arXiv:1511.05944), deliberately and uniformly:
> available energy is the summed kinetic energy of protons and charged pions plus the summed total
> energy of neutral pions, over a **closed** five-species list.

Three counts appear in one sentence and no two agree.

- **It enumerates three species** (p, π±, π⁰) — dropping γ, which we do include.
- **It labels the list five.**
- **The code implements four.** `CVUniverse.h:361-374`, fourteen unambiguous lines: γ total E (`:368`),
  π± `E − 135` (`:369`), π⁰ total E (`:370`), p `E − 938.27` (`:371`). No e± branch.
- **`VALIDATION_LEDGER.md:1331` — written by lane A in this same thread on 2026-08-13 — says so:**
  *"we unfold to `GetEAvailableTrue()`'s **closed four-species list** with `mass_pion = 135`."*
- **`OI-56` states the qualifier in exactly the words the document drops:** *"ours is the 2016 convention
  **minus e±**."*

Rodrigues' list is five because it includes electron total energy. Ours is four because it does not. The
document upgrades a qualified source claim to an unqualified one **and deletes the qualifier that both
the ledger and the row spell out**. The correction does exist in the document — at `:63-64`, forty-seven
lines below the claim, in the last paragraph of §2 — and it is **not** in §5.

**"deliberately and uniformly" is the part that should not survive contact with Gregor.** The advisory's
own §5 concludes the opposite: *"our exclusion follows the νe-era code and not the νμ paper."* The e±
exclusion is inherited from `kEAvail`'s `abs(pdg)==11||13` charged-lepton skip, which exists because in a
νe analysis the primary electron *is* the lepton. And `135` is likewise inherited — advisory §2: *"one
inherited copy, not two choices,"* from the 2021-07-28 MINERvA 101 tutorial import. **A word asserting
intent, placed where the repo's own evidence records inheritance.** That is the failure mode this lane
was told to watch for, in the first sentence of the document.

## V36 — BLOCK: the measured numbers are the `kEAvail` comparison, relabelled as "the open convention"

§2 is headed *"Where the two published conventions differ"* and its table columns are Rodrigues 2016 and
Ascencio 2022. Inside it:

> Four species carry the disagreement, all of which we exclude and **the open convention** includes …
> **Measured effect of moving to the open convention, on our sample:** `+212.18` MeV/event, `4.837%`,
> `−10.99%`.

**Every source attributes those numbers to a different comparator.** `OI-56`: the mismatch is against
*"MINERvA's own reference implementation (`GENIEXSecExtract/src/XSec.cxx` `case kEAvail:`)"*. `OI-59`:
*"`OI-56` measures **the reference rule** as −10.99% out of truth bin 1."* Advisory §6: *"`OI-56` measures
adopting **the reference rule**."* `VALIDATION_LEDGER.md:1334`: *"`OI-56` measures **the reference rule**."*
Four independent statements, one comparator, and it is the code — not the paper.

**The two are not interchangeable, and the advisory devotes its entire §3 to saying so** — *"'The MINERvA
reference implementation' IS A νe ARTIFACT, AND IT POST-DATES ASCENCIO v1 … `kEAvail` cannot have produced
Ascencio v1's numbers — it did not exist."* Per the advisory's own §4 table they differ on at least two
rows: **e±** (`kEAvail` excluded, Ascencio open list total E) and **the clamp** (`kEAvail` `max(0,·)`,
Ascencio unstated).

**The document contradicts itself on this and the contradiction is the proof.** "Four species carry the
disagreement" is true against `kEAvail`. Against the open list it is **five**, because the open list
includes e± — which the document itself asserts twenty lines later at `:63-64`. A count of four and an
e± exclusion cannot both be true of the same comparator. This is `BEN-150`'s shape one level up: not two
JSON keys sharing a name, but a measurement and a convention sharing one.

Direction: including e± would make the shift **larger** (advisory §5 puts e± at `1.462` MeV/signal event).
So the relabelled number understates the quantity it is relabelled as. Small — ~0.7% of `212.18` — and in
the favourable direction.

## V37 — BLOCK, and this one is about the reader: the framing is asymmetric toward the recipient

`minerva-ml` is **`gregorkrz/minerva-ml`** (`docs/GREGOR_FOUNDATION_MODEL_REFERENCE.md:5`) — the
repository of the person this document is written to be handed to. The opening paragraph, `:26-27`:

> (`minerva-ml` uses total energy for charged pions, which adds ~140 MeV/pion; **that is a defect in that
> code, not in ours**.)

`OI-30`, the source, says only: *"Ours matches; minerva-ml's total-energy charged pion adds ~140
MeV/pion."* **The document adds the defect verdict.** On substance the verdict is defensible — Rodrigues,
Ascencio Eq. 1, `kEAvail` and 2312.16631 Eq. 4 all specify charged-pion *kinetic* energy, so `minerva-ml`
is out of line with all four. That is not the finding.

**The finding is that the mirror-image case is not framed the same way.** On e±, `minerva-ml` matches
Rodrigues and we do not — the same class of disagreement, the same kind of evidence, the recipient right
and us wrong. It appears at `:63-64`, forty lines later, under a heading that partly editorialises
(*"cuts against us and is stated for that reason"*), and §5 item 2 characterises our own divergence as
*"a **declared convention choice**, not a negligible one."*

**So: their divergence is a defect in their code; ours is a declared convention choice.** Both readings
may be defensible in isolation. Presented together, in the opening paragraph and forty lines apart
respectively, to the author of the code called defective, the asymmetry is the first thing an advisor
notices — and it is the kind of thing that costs a reader's trust in the numbers, which here are sound.

## V38 — BLOCK: §5 has one self-cutting item, not the two its author believes

The commissioning message asked me to check that **two** §5 items *"deliberately cut against us"* were not
softened — *"the e± case where `minerva-ml` matches the νμ paper and we do not, and the 'reference
implementation' that is not independent."*

**Item 4 is not softened.** *"Our cited authority and our putative independent reference are one
analysis"* is the advisory §3 conclusion at full strength, and it survives the check.

**The e± item is not in §5.** §5's five items are: no single published definition; the difference is not
immaterial; `135` not proven immaterial; not a neutral reference implementation; the Ascencio check does
not independently validate us. The e± concession is in §2 and nowhere else.

Recorded not as a gotcha but because of what it implies: **the author's model of their own document
places the concession in the section a sceptical reader turns to first, and it is not there.** That is
precisely why one reviewer per artifact has to be someone other than the author, and it is the strongest
argument in this pass for the orchestrator's decision to commission it.

## V39 — BLOCK: "a five-site change or nothing" is a five-site list over six sites, and the omitted one is the live one

`:101-103`: *"**Correcting it is a five-site change or nothing:** `CVUniverse.h:364` plus four generator
converters that bind to our value by comment. They must move in one commit, or the four-generator
comparison silently compares two different observables."*

Executed rather than argued — `state/probe-eavail-pion-mass-sites-20260813.py`, committed and rerunnable,
five arms with expectations predeclared before the run:

| arm | expected | observed | |
|---|---|---|---|
| P1 sites named by path | 1 | **1** | the list names one of its five; the other four must be re-derived |
| P2 code sites binding `135` as an E_avail π± mass | > 5 | **6** | the count is short by one |
| P3 of the 4 converters, how many bind BY COMMENT | 2 | **2** | the document says all four do |
| P4 CONTROL: `139.57` in an E_avail π± term | 0 | **1** ✗ | **fired — see below** |
| P5 each `135` declaration has a re-read use line | 6 | **6** | all six genuinely subtracted |

**The omitted site is `nd-unfolding/pet/pointcloud_projection.py:51` (`M_PION_EAVAIL = 135.0`, consumed at
`:107`)** — the PET truth-cloud projector, i.e. the path the live Gate-5 campaign runs. **The document's
own source names it**: `ADVISORY-…-oi30-eavail-residuals.md:95` calls it one of *"the two mirrors
deliberately kept in lockstep"* and warns it *"will **silently desync** if only one is changed."* A
repairer executing "a five-site change or nothing" produces exactly the partial change the phrase
"or nothing" exists to forbid, in the live path.

**"bind to our value by comment" is true of two of the four converters**, not four:
`genie_to_xsec3d.py:42` (*"matches CVUniverse mass_pion=135 MeV"*) and `nuwro_to_flat.C:31`
(*"(match CVUniverse)"*). `gibuu_to_xsec3d.py:53` and `gibuu_to_xsec_eavailW.py:38` are bare
`MASS_PI … = 0.135` with no reference. **A repairer who trusts the comment-binding and greps for
`CVUniverse` finds half the set.** Both errors run the same direction: the repair looks smaller and more
discoverable than it is.

**Compounding, and not the document's fault but on its execution path:** `pointcloud_projection.py:50` and
`POINTCLOUD_PROJECTION.md:28` both cite *"`GetEAvailableTrue()` … (CVUniverse.h:330-343)"*. Line 330-343
is `GetRecoClusters`, the full-event cluster-dump overload. `GetEAvailableTrue()` is at `:361-374`. A
repairer opening the PET mirror's own comment to confirm it is the same quantity lands on an unrelated
function — the shape already filed as `FINDING-20260813-line-range-on-a-file-that-never-existed.md`.

**The four-generator comparison is a real object** (GENIE 2.12, MnvTune v1, NuWro 21.09, GiBUU 2019 —
`docs/slides_3D+_outline.md:58`), so that clause stands. Checked because it read like an invented
consequence and it is not.

### The control fired, and I am reporting it rather than relaxing it

**P4 expected zero and observed one.** The ±8-line context window cannot separate two constants declared
four lines apart in the same file — `M_PION_EAVAIL = 135.0` at `:51` and `M_PI = 139.57` at `:55`. Kept at
its predeclared expectation instead of moved to 1, because adjusting an expectation after seeing output
is how a probe stops being able to fail.

**And it surfaced a hazard I had not looked for.** `pointcloud_projection.py` holds *both* constants,
deliberately, four lines apart: `M_PION_EAVAIL` for the E_avail convention and `M_PI` for the
charged-pion multiplicity KE threshold at `:116`. Correcting the convention constant to `139.57` there
makes the two numerically identical and the deliberate separation invisible to the next reader. The
one-line instruction "five-site change" does not mention it.

**A second arm fired first and I want it on the record.** P5b, the arm built to refute me, reported only
2 of 6 declarations reaching an accumulation line — which would have meant four of my six sites were dead
code and the finding inflated. **I read all six use lines by hand before touching the regex**, in that
order, and all six are genuine. The pattern had simply never covered `econ[m] = E[m] - MASS_PI` or
`np.copyto(contrib, E - …)`. I then did **not** write a cleverer regex: separating "subtracted into an
E_avail sum" from "subtracted to test a KE threshold" is semantics, and a wrong automated oracle is worse
than none, so P5 is now a recorded table of six use lines re-read from disk and checked verbatim. Its
first run caught two of *my* transcriptions as fragments rather than whole lines.

## V40 — a citation that lands on text reading as the opposite, and a provenance split sorted the wrong way

**Neither is filed as a lane-D `BEN-*`: the first is inherited from `OI-30(d)`, the second is the
author's to reshape. Both are routed, not fixed.**

> **CORRECTED 2026-08-13, and the correction is against me.** The paragraph below claimed *"It was
> never right."* **That is false.** `13.69%` sat at **`:1043`** at `668a965` (08-12 22:37 EDT =
> 02:37Z) — I checked two revisions of `VALIDATION_LEDGER.md`, found `:1011` and `:1116`, and
> generalised a two-point sample into a universal. **A universal claim from a two-point sample is the
> same error class this whole pass is about**, committed in the paragraph auditing someone else for it.
> Lane A got it right and better: the citation was **exact when written at 02:34Z** and rotted within
> 15 h because Gate 5 appended 73 lines above it. Filed by lane A as **`BEN-219`**
> (`FINDING-20260813-citation-correct-at-write-time.md`), which supersedes this item and states a
> sharper rule than mine — a `file:line` into an append-heavy ledger has a shelf life of hours, and four
> documents carry the stale one. The observation below about *where* `:1043` now lands still holds and
> lane A independently made it. Everything else in (a) is withdrawn.

**(a) `VALIDATION_LEDGER.md:1043` does not contain `13.69%`.** §3:82 cites *"13.69% median per-bin,
`VALIDATION_LEDGER.md:1043`"*. The figure is at **`:1116`**, under *"5D GBDT systematic covariance
campaign (completed 2026-06-29): **PASS**"* — correct, adopted, and the right number. Line 1043 reads
*"auxiliary robustness check and **is not part of this candidate budget**"*, under the `:823` header
*"2026-07-14 corrected 5D GBDT covariance — **CANDIDATE**"*. So a reader who follows the pointer lands on
a sentence that reads as an exclusion of the quantity cited, in a section marked candidate rather than
adopted. It was never right: `13.69%` sat at `:1011` before the 2026-08-12 VL re-id and at `:1116` after.
Inherited verbatim from `OI-30(d)` — but this is the document whose pointers a collaborator will actually
follow.

**(b) The provenance section's two buckets are sorted by author effort, not by checkability, and the
sort is inverted.** `:153-161` labels the `GENIEXSecExtract` archaeology *"Relayed from lane A and NOT
independently verified by the author"* and supplies two `gh` commands needing no credentials. Honest, and
the strongest paragraph in the document. But the *other* bucket — *"Measured in this repo and
re-derivable: every number in §2 and §3"* — silently absorbs the **two-paper reading**: the CLOSED/OPEN
table, the *"`strange` and `kaon` appear zero times"* count, the Rodrigues and Ascencio quotations. Those
are external `ar5iv` fetches, not repo measurements, and **advisory §7.1 records them as the one piece of
lane A's evidence that produced disagreeing results** — a summarising `WebFetch` and a verbatim `WebFetch`
contradicted each other about Ascencio Eq. (1)'s surroundings until a third instrument settled it, with
the note *"the disagreement is the only warning you get."*

So the claim labelled unverified is two commands away from confirmation, while the claim §1's entire
position rests on is bucketed as repo-measured, is not, and is the one the source flags as
instrument-fragile. **No instrument is named for it anywhere in the document.** An honesty section that
sorts by "how much of this did I personally do" rather than "how hard is this for the reader to check"
inverts its own purpose.

## What this pass did not establish

- **I did not re-fetch either paper.** Rodrigues' closed five-species list and Ascencio's open list are
  taken from advisory §1's verbatim quotations. V35 does not depend on them — it rests on
  `CVUniverse.h:361-374`, `VALIDATION_LEDGER.md:1331` and `OI-56`, all in-tree — but V36 does.
- **I did not run the `gh` commands** in the provenance section. Untested, not endorsed.
- **P2's six is a lower bound.** A regex over declarations can prove a list incomplete; it cannot prove
  a count total. "At least six," never "exactly six."
- **`docs/EAVAIL_DEFINITION.md` is the only artifact audited here.** Gate 5's throughput anomaly and
  Gate 6's floor are untouched by this pass — see the note below.

---

# V41–V43 — second pass, against `c3771f7` (the text as it now stands)

The document was rewritten twice while this audit ran (`4788598`, then `c3771f7`). Re-read in full at
`c3771f7` before reporting. **`BEN-175`, `BEN-177` and `BEN-178` all survive both rewrites unchanged.**

## V41 — PASS, and it is the newest claim in the document: the MAT token-identity reproduces

`c3771f7`'s §1 asserts our `GetEAvailableTrue()` body is *"token-identical to MAT-MINERvA's
`calculators/CCQE3DFitFunctions.h` — both **424 chars**, sha256 `5296998043add43c`."* I cannot reach
MAT-MINERvA, so I checked the operand I can: `CVUniverse.h:361-374`, comments stripped, all whitespace
removed.

**424 characters. sha256 prefix `5296998043add43c`. Exact match, on the first normalisation tried** —
five were tried and only that one lands, so *"comments and whitespace stripped"* is an adequate recipe
and I withdraw the concern I had queued about it being unreproducible. One operand of a two-operand
identity claim is now independently confirmed; the MAT side is not, and the document should not be read
as though it were.

**One label:** `5296998043add43c` is 16 of sha256's 64 hex characters. Truncation is fine and standard;
saying so costs four words and stops a reader concluding the algorithm is something else.

## V42 — BLOCK: both spine corrections stopped at the §1 boundary, and the corrected phrase still stands twice

This is the second pass's finding and it is a direct consequence of how the first two were applied.

**Round 2's whole point** is that *"we implement Rodrigues"* is the wrong framing — we implement MAT's
list, which *coincides* with Rodrigues minus e±, and §1 now says so in terms: *"the inheritance is what
makes 'deliberate' false."*

**§2's table, twelve lines later, still says the corrected-away thing, unqualified:**

> | what we do | **implement this** [Rodrigues 2016] | do not implement [Ascencio 2022] |

A table row is scanned, not read. This is the version of the claim most likely to be extracted.

**§5 item 2 still says it too, and it now contradicts §5 item 6 four lines below:**

> 2. … It is a **declared convention choice**, not a negligible one.
> 6. … The exclusion is **inherited** from a νe-analysis charged-lepton branch, **not established as a
>    choice**.

*Declared convention choice* is the exact framing round 2 refuted. **§5 is the section the document
itself designates as the one a reader trusts as complete** — item 6 says so in its own text: *"§5 is the
list a reader trusts as complete."* A reader who reads only §5, which is what §5 is for, gets the
pre-correction position and an internal contradiction inside one numbered list.

**I do not disagree with lane A on §1.** Round 2 is right, is an improvement on round 1, and its one
locally-checkable claim reproduces (V41). **The finding is that a correction was applied where the
defect was found rather than everywhere the claim appears** — and that both rounds made the same choice,
which is why the second round did not catch the first round's residue.

## V43 — the parts nobody had audited: PASS, with one hardening

Checked because the commissioning message was right that two spine corrections in one afternoon argue
for looking harder at the rest, not less.

- **§4 (the Ascencio caveat) — PASS.** `p = 0.432` on 2 dof, `1.68/2`, `ours/theirs = 1.092` and `1.063`,
  both maximal common super-cells low-E_avail: all match `VALIDATION_LEDGER.md:1314-1320`. *"Shipped
  three caveats"* is exact — `nd-unfolding/compare_ascencio_fullcov.py:21-26` enumerates three. The
  heading's tense (*"a caveat it did not **previously** carry"*) is correct: the ledger now carries it at
  `:1326`.
- **§5 items 1, 3, 4, 5 — PASS.** Item 4 is at full advisory strength and was the one I was asked to
  check for softening; it is not softened.
- **The `P7` / `OI-40` status claims — PASS.** `OI-40` is `BLOCKED` with exactly the stated condition;
  `PUBLICATION_COMPLETION_RUNBOOK.md:257` §P7 covers note updates and externally-tracked `OPEN_ITEMS`
  questions, so *"the analysis note absorbs this at Packet P7"* is supported.
- **Scope creep after both rewrites — still PASS.** Nothing adopted, nothing unfrozen.
- **One hardening, low severity.** §4: *"`p = 0.432` on 2 dof **separates nothing**."* Advisory §6 says
  it *"cannot distinguish a **~10%** definitional offset from noise either way."* Dropping the scope
  turns a bounded statement into an absolute — `p = 0.432` on 2 dof would separate a 100% offset
  perfectly well. The document's conclusion does not depend on the stronger form.

---

# V44–V49 — independent pass on Gate 6 Leg F floor replication (`2fecce7`)

Second assignment, kept separate from the E_avail pass. Artifacts: `nd-unfolding/pet/gate6_floor_statistics.py`,
`PREDECLARATION-20260813-gate6-floor-replication.md`, `state/gate6-floor-replication-partial-56863958.json`,
`VL116–VL120`. Read-only; the only write is my own mutation harness under `state/`.

**Headline: this is the most defensible artifact I have audited on this campaign.** Five of the six
things I was asked to attack hold, and two of them hold by a stronger route than the one proposed.
**One real hole**, and it is in the test battery rather than the code. **One promotion of the
iteration-0 observation did occur — not in B's artifacts, but in the message that asked me to watch
for it.**

## V44 — thresholds tuned to the data? PASS, and the timestamp question is not the one that settles it

The brief said to check B's authoring claim *"against commit timestamps and job states, not against
B's account."* **Timestamps would have been the weak check, and they are unnecessary.**

`git log` on the predeclaration returns **exactly one commit** — `2beead8`, 08-13 09:21, *"committed
BEFORE submission"* — and **`git diff 2beead8 HEAD` is empty**. All three frozen numbers are inside
that blob: `0.05` and `0.10` at `:93-94`, `0.1740029887300910` at `:97`. **So the thresholds were fixed
at 09:21, before any draw existed, whatever time the statistics script was authored.** That is a content
check on an immutable object; it does not depend on trusting a timestamp, a job state, or B's account,
and it is strictly stronger than all three. **V49 answers item 5 with the same evidence.**

The derivation also traces: `0.1740029887300910 = 0.5 × S_range[2]`, `S_range[2] = 1.1014828481277632 −
0.7534768706675813`, and those two operands are `VL117`'s and `VL120`'s iteration-2 values — the
committed five-member spread, which predates the floor entirely. Re-derived: the subtraction is exact
in IEEE double.

**One note, immaterial to the verdict.** `0.5 × 0.3480059774601819` is `0.17400298873009096`; the
predeclaration writes `= 0.1740029887300910`, which is that value rounded to 16 significant figures.
The gap is 4e-17 and no physically-derived `F_range` will land inside it. **The code handles this
correctly and deliberately** — `_verify_frozen_threshold_against_member_receipts` checks
`S_RANGE_2_MAX`/`S_RANGE_2_MIN` with exact equality, i.e. the **operands**, never `0.5*S == THRESHOLD`,
which would fail closed on its own predeclared constant. Worth one word in the predeclaration: that `=`
is `≈ to 16 s.f.`

## V45 — branch 1's unreachability: a theorem, PASS, and it rests on a second rule

`F_range[2] = 0.0523993868023519 > 0.05` on draws 1–3. For any superset `S' ⊇ S`, `max(S') ≥ max(S)`
and `min(S') ≤ min(S)`, so `range(S') ≥ range(S)`. Branch 1 requires `F_range[2] ≤ 0.05`. **Unreachable
for any completion of the set.** Sound. It moves no threshold, selects no subset, and the receipt
carries `still_a_verdict: False`.

**The interlock is worth naming because it is load-bearing and undocumented.** The theorem holds only
while draws 1–3 stay in the final set. A rule that allowed dropping an invalid draw and verdicting on
the survivors could *shrink* the range and resurrect branch 1 — so the deduction's validity depends on
the `do_not_select_passing_subset` clause, and that clause's value here is not just anti-cherry-picking.
**Two rules holding each other up, which neither document says.**

## V46 — the refusal test binds. Demonstrated by mutation, not by reading

Item 3 asked whether the refusal test binds or passes vacuously — this campaign's signature defect, and
not answerable by running a suite that passes. So I broke the code and checked the battery noticed:
[`state/probe-gate6-floor-mutation-20260813.py`](state/probe-gate6-floor-mutation-20260813.py), which
copies module and tests to a scratch dir and mutates the **copy**. Predeclared: every mutation removes a
property the battery claims to test, so every one must produce a failure.

| mutation | result |
|---|---|
| M1 refusal removed (`if False:`) | **2 failed** — caught |
| M2 refusal kept, but stops naming `do_not_select_passing_subset` | **1 failed** — caught |
| M3 process threshold `>=` → `>` | **1 failed** — caught |
| M4 seed threshold `<=` → `<` | **1 failed** — caught |
| M5 band condition dropped from branch 1 | **2 failed** — caught |
| M6 frozen `THRESH_PROCESS_RANGE` silently retuned to `0.05` | **8 failed** — caught |
| M7 sd `n-1` → `n` | **2 failed** — caught |
| M8 `F_range` sign flipped | **7 failed** — caught |
| **M9 `abs()` dropped from `d_by_draw`** | **52 passed — SURVIVED** |

**M2 is the direct answer to item 3: the assertion on the prohibition's name binds.** Keeping the
refusal but renaming the message still fails the test. Not vacuous.

## V47 — BLOCK-worthy as a coverage finding: the band check's below-1 side is untested

**M9 survives all 52 tests.** `d_by_draw[j] = abs(v[j,k] − 1.0)`; drop the `abs` and **every draw below
1 is unconditionally in-band, however far below.** The band check would then only ever catch draws
*above* 1.

All four band tests exercise the above-1 side only:

- `test_small_range_but_a_draw_outside_the_band_is_intermediate_not_seed_determined` — values `1.20, 1.21`
- `test_band_boundary_is_inclusive`, `test_band_one_float_step_outside_is_not_inclusive`,
  `test_a_single_draw_outside_the_band_is_enough_to_fail_branch1` — all via `stats_at`, which
  **hand-builds the stats dict and never calls `floor_statistics`**, so the `abs` is not on their path
  at all.

`stats_at`'s docstring is candid that it bypasses values (*"`<=` vs `<` at the boundary … is only
testable at the predicate"*) and says *"the value-driven tests below cover the wiring."* **They cover it
on one side.**

**Why this side and not the other matters here.** Members 4 and 5 sit at `0.819792` and `0.753477` at
iteration 2 — below 1. Draw 3's iteration-0 value is `0.8400`. **The below-1 half of the band is exactly
where this campaign's data lives**, and it is the half the battery cannot defend. `d = −0.16` reads as
in-band without the `abs`.

**The code is correct.** This is a hole in the instrument protecting a frozen rule from, in B's own
words, *"a future edit under schedule pressure."* Same shape as `BEN-173`: a control present for one
sibling and absent for its mirror. `BEN-180`.

### My own mutation was void first, and reported a hole that was not there

M7's first form replaced the string `ddof=1` — which occurs **only in a docstring (`:198`) and a key
name (`:219`)**; the sd is computed by hand. The regex mutated prose, changed no behaviour, and my
harness printed **SURVIVED**. I nearly reported a hole in B's battery that was a hole in my harness —
and `test_sd_is_ddof1_not_population` is a perfectly good binding test, as the corrected M7 shows.
**A mutation harness that can silently mutate a comment manufactures false holes**, and "the mutation
applied" is not the same check as "the mutation applied to executable code." Kept in the committed
harness as `M7void` rather than deleted. `BEN-181`.

## V48 — the iteration-0 discipline: B's artifacts PASS; the framing that reached me did not

**B declined the promotion, explicitly.** The receipt's `why_provisional` reads *"the VERDICT is defined
at iteration 2 only and requires all five draws present and valid. **Do not quote any number here as
'the across-process floor'.**"* The `HEADLINE` carries no iteration-0 claim. Item 4 passes on the
artifacts.

**It does not pass on the message that assigned me item 4.** That message's lead is: *"draw 3 … its
`v[0] = 0.8400` sits between members 4 (`0.8748`) and 5 (`0.7614`) … If that holds, some of what Gate 6
recorded as a seed effect is process noise."*

**All three of those numbers are iteration-0 values.** `0.8748` and `0.7614` are the *first* entries of
`VL119` and `VL120`; those members' **iteration-2** values are `0.819792` and `0.753477`. And at
iteration 2 — the only iteration where the verdict is defined — draw 3 reads `0.9431`, which does not
sit between them but well above both, and `F_range[2]` is **15.1%** of the member spread rather than
**89.6%**.

**So the conclusion is supported at iteration 0 and unsupported at iteration 2.** Recorded without any
suggestion of bad faith: the iteration-0 number is the arresting one, which is precisely why the
discipline was predeclared, and B holding the line while the relay did not is the ordinary way a
predeclaration earns its keep. **Flagged because that framing is one hop from Joseph.**

## V49 — the predeclaration is genuinely unedited: PASS

One commit in its history (`2beead8`), `git diff 2beead8 HEAD` empty. B corrected the now-false claim in
the RUN_LOG rather than editing the frozen document, exactly as reported.

## What this pass did not establish

- **No Slurm reach**, so *"3 of 5 draws, tasks 2 and 3 COMPLETED"* is B's measurement, not mine. I
  verified the *rule* and the *battery*, not the job states or that the receipt's `v` values were read
  off the artifacts they claim.
- **I did not verify the eight validity clauses against real draw artifacts** — only that each has an
  independent test that fails on a single degradation, which the battery does provide.
- **`52 passed` is not coverage.** Nine mutations is a sample of the mutation space; M9 was found
  because I went looking at the `abs`, and there may be other survivors I did not construct.

---

# V50 — design review: putting `verify_hash_bindings.py` in the pre-commit hook

> ## CORRECTED 2026-08-13 — the decisive evidence below was measured on the wrong tree
>
> **I measured lane-d's worktree, not `main`.** Re-run on `6637d63`: **`ALL BINDINGS INTACT`, exit 0,
> 0.563 s.** Verified the mechanism myself rather than accepting the report:
> `git merge-base --is-ancestor` returns **NO** for both `5ad5ac7` (A's Gate-4 retirement, 18:59) and
> `466ab0d` (C's R2, 19:53) against `dd27cee`, the commit I measured at. I then merged `cfe3422` and
> pushed — so the commit I *shipped* contains the repairs and the measurement I *reported* did not.
>
> **Withdrawn:** *"the tree is broken right now, twice"*; *"~19 h and counting"* (it was ~18 h and
> closed at `5ad5ac7`); *"0-for-2 on the current state"*; and the sentence the verdict was framed on —
> *"day one, the hook prints `5 checks passed` while the gate prints `*** BINDINGS BROKEN ***`."*
> **That is false of `main`.** `test_hash_bindings.py` also passes 6/6, so A's reported third defect
> (the `superseded-*` Gate-2 receipt) is closed too. Both instruments are green.
>
> **This is the class I spent the day auditing, aimed at my own report** — a measurement whose scope
> went unstated and was presented as covering a broader domain. It is the same shape as the
> `git log -1 -- <path>` slip I caught and disclosed in the same message, one level out: **the
> repository I measured was not the repository I reported on.** `BEN-183`.
>
> **A second prediction of mine also failed on test, and it failed in A's favour.** I expected the two
> retirements to instantiate `OI-65`'s divergence — A used `status: SUPERSEDED` **and** the field
> rename, C used the field rename with no `status`. Measured: C's receipt has **no `files` key**, so
> `"files" not in payload` classifies it retired under the status-side predicate too. **Both predicates
> agree. A's measured-zero survives this instance**, and the `files` clause is carrying more of that
> predicate than the `status` clause is.
>
> **THE VERDICT HOLDS, on Q2 and Q5 alone, and neither references the tree's state.** Details in the
> re-statement at the foot of this section.

Requested by `personal-orchestrator` after Joseph asked *"does D think it's a good idea too?"* — a
review before anything is built. Lane A proposed; lane C found the mechanism; I am independent of both.
Cited by claimant throughout, because two `OI-64` and two `OI-65` rows exist.

**VERDICT: YES to the hook. NO to file-side staged-diff scoping. Ship it whole-tree, and then the
`OI-65` dependency dissolves rather than needing resolution.**

## The finding that decides it: the tree is broken right now, twice

Ran the gate whole-tree this turn:

```
resolved 170 bindings (531 unresolvable) — 164 OK, 4 known pre-existing
MISMATCH nd-unfolding/pet/reconcile_gate5_family.py      <- gate5-family-reconciliation-20260813.json
MISMATCH nd-unfolding/pet/train_fullevent_nominal.py     <- p3f-pet-gate4-launch-code-gate-20260812.json
*** BINDINGS BROKEN ***                                            0.555s
```

**The `ce03f2c` break is not fixed.** It is ~19 h old and still live. And a **second, independent**
break has appeared since: `reconcile_gate5_family.py` was correct at `69c577b` (09:25, receipt and code
committed together, hash `e536540d…` = the pin) and was broken by `eedcfc9` (18:52) and `466ab0d`
(19:53), the BEN-157 R1/R2 edits. Tree now reads `11e4f440…`.

**This settles question 2 without needing an exotic evasion.** Score the proposal honestly:

| | catches? |
|---|---|
| break #1 **at the moment of introduction** (`ce03f2c` staged the pinned file) | **yes** |
| break #2 **at the moment of introduction** (`eedcfc9`/`466ab0d` staged the pinned file) | **yes** |
| break #1 **as it exists in the tree today** | **no** |
| break #2 **as it exists in the tree today** | **no** |

So file-side scoping is 2-for-2 on introduction and 0-for-2 on the current state — **and the current
state is what ships.** On day one, the hook prints `pre-commit: 5 checks passed` while
`verify_hash_bindings` prints `*** BINDINGS BROKEN ***`. That is not a hypothetical evasion; it is the
design working as specified. **An absent check converted into a false assurance is worse than the
absent check**, and the orchestrator named this as the campaign's signature defect before I looked.

**I initially got break #2 backwards** and nearly reported the proposal as 0-for-2 on introduction too.
`git log -1 -- <path>` returned `ac540d5`, and I read that as the receipt and code never landing
together; `git show --name-only 69c577b` shows both staged. Re-derived by hashing the blob at each
commit. **The proposal catches both introductions and that is a point in its favour.**

## Question 1 — the design rule is fitted to two exclusions that do not exhibit the property it names

> *A check belongs in the hook if and only if it can only fail on what THIS commit changed.*

**Both cited exclusions are excluded for other reasons, stated in the dispatcher's own header.**

- `--check-freshness`: *"returns 1 whenever `LIVE-STATE.md`'s sha is not HEAD's — a condition it
  **CANNOT ESCAPE**… A check that always fires is a check nobody reads."* That is **inescapability**.
  Its scope is irrelevant; a whole-tree check that can be satisfied would not have this problem.
- `merge_guard.sh`: *"needs a lane argument and belongs at merge time, not commit time."* That is
  **wrong phase and missing inputs**.

Neither is about whole-tree-ness. **The rule explains its two data points by a property they happen to
share rather than by the property that excluded them** — and it then forbids, by construction, the
category the orchestrator correctly identified: a whole-tree invariant that *should* block everyone.

**A rule that survives both exclusions and admits the hash gate:**

> **A check belongs in the hook iff a committer who did nothing wrong can always make it pass.**

`--check-freshness` — never passable, excluded. `merge_guard.sh` — not passable at commit time,
excluded. `verify_hash_bindings` whole-tree — passable iff the tree is clean, and a clean tree is two
waivers away. **Admitted.**

It also has the right teeth: it *forbids* adding a whole-tree gate while the tree is dirty and unwaived.
**Which is the actual precondition A's proposal routes around by scoping.** Read that way, the scoping
is not a design improvement; it is a way to ship without confronting two unfixed breaks.

## Question 2 — the remaining hole, beyond the day-one one

**A receipt-introduced break is invisible to file-side scoping**, and this repo has the specific
mechanism for it. A commit that adds or edits a receipt pinning an *unmodified* file with a
non-matching hash stages only the receipt; no live receipt pins a receipt; the hook checks nothing.
Whole-tree catches it.

This is not exotic here. `KNOWN_PREEXISTING`'s four entries are all *"submit-time provenance"* —
receipts written on Perlmutter against a checkout that forks from local. A cluster-written receipt
pinning a locally-different file is the established failure mode in this repo, and it arrives **as a
receipt**, with no code staged.

**It is the exact mirror of the rejected alternative.** Pin-side misses code-introduced breaks; file-side
misses receipt-introduced breaks. The rejection reasoning for pin-side is correct **and symmetric**. If
scoping is wanted later it must be the **union**, never either alone.

## Question 3 — today's evidence: the dichotomy is false, and the repo already solved it

A argues a wholesale gate would have had three lanes blocked on each other. The counter-reading is that
all three were real and a blocking gate forces them fixed. **Both are right, and the third option is
already built into the module A is proposing to install.**

`KNOWN_PREEXISTING` exists precisely for *"bindings known to have drifted … and deliberately not
'fixed' … **Listed so real regressions stay visible above the noise.**"* That is the correct instrument:
pre-existing breaks are **waived by name**, new ones block.

**A waiver and a scope do the same job and differ in the only way that matters: a waiver is a visible,
reviewable, four-line list in the source; a scope is silent.** Under scoping nobody learns the tree is
broken. Under a waiver, the two current mismatches appear in a diff with an owner and a reason.

So: neither "block everyone" nor "scope it away." **Waive the two, block everything new.** Zero lanes
blocked on each other, zero silent passes.

## Question 4 — `OI-65` (lane A's): a blocker for the scoped design, a non-issue for whole-tree

The framing understates it in one direction and overstates it in another.

**It is not two predicates. It is one predicate and none.** `verify_hash_bindings.py` contains **zero**
occurrences of `status`, `SUPERSEDED`, `RETIRED` or `live` — grepped this turn. `collect()` harvests
every `(path, sha256)` pair from every receipt and the only exclusion is a hardcoded four-entry
allowlist. `test_hash_bindings._launch_code_receipts()` has a real predicate
(`status == "SUPERSEDED" or "files" not in payload`). **There is nothing to reconcile; there is one to
author**, and the proposal's *"any **live** receipt pins it"* is asking for a concept that does not
exist in the tool it would live in.

**The measured zero is over the wrong population.** The test globs `*launch-code-gate*.json` — **15
files**. `verify_hash_bindings` walks **158** receipts in `state/` and resolves **170 bindings**. Zero
divergence across 15 says nothing about the 158 the scoped gate would decide liveness over. A ~10×
population gap, checkable in one `ls | wc -l`. **A's "measured zero rather than dressed as risk" is the
right instinct and the measurement does not cover the domain.**

**And the proposal changes the predicate's consequence from visible to silent.** Today a
misclassification is a reporting discrepancy someone notices. Under the scoped hook, a receipt wrongly
deemed retired means the gate checks nothing and prints green.

**But whole-tree needs no liveness predicate at all** — `verify` already runs correctly without one.
So the answer is neither "resolve first" nor "ride along": **ship whole-tree and `OI-65` stops being a
dependency of this work.** It stays worth fixing on its own merits.

## Question 5 — cost: confirmed irrelevant, and containment is the wrong goal here

**0.555 s measured whole-tree**, matching the claimed 0.58 s. Scoping buys no speed.

So the justification reduces entirely to blast-radius containment — and **for a freeze gate that is not
a benefit.** A code freeze is global by definition; the evidence a gate passed against specific code is
worth exactly as much as its weakest binding. Containing the blast radius of a broken freeze is a
synonym for letting a broken freeze persist, which is what the ~19 h and the second break both are.

## Recommendation, in the order it should be done

1. **Fix or waive the two current mismatches.** `KNOWN_PREEXISTING` is the mechanism and it already has
   the right comment; extend each new entry with owner, date, and the gate re-issue that would clear it.
2. **Add `verify_hash_bindings.py` to `.githooks/pre-commit`, whole-tree, unscoped.** 0.555 s.
3. **Update the dispatcher header's exclusion list either way.** Its documenting *exactly two*
   deliberate exclusions is what made "never considered" indistinguishable from "considered and
   rejected" — that is the actual root cause here, and it recurs unless the header is treated as the
   record of the decision.
4. **If scoping is ever wanted**, it must be file-side **∪** pin-side, and it needs `OI-65` (A's)
   resolved over all 158 receipts, not 15.

**What I did not check:** I did not run the proposed scoped implementation — it does not exist yet, so
every statement about it is from its description, and I may be attacking a design that would ship with
the day-one gap already closed. **If A's implementation intends to run whole-tree once at install and
scope only thereafter, most of this review's force is spent** and the remaining points are the design
rule (question 1), the receipt-introduced hole (question 2), and the population gap (question 4).

## Re-statement on a clean tree — the verdict, without the withdrawn leg

**It holds, and it rests on two points that never referenced the tree's state.**

- **Q2 — file-side scoping has a structural blind spot.** A commit that adds or edits a receipt pinning
  an *unmodified* file stages only the receipt; nothing pins receipts; the hook checks nothing.
  Whole-tree catches it. All four `KNOWN_PREEXISTING` entries are exactly that shape — cluster-written
  submit-time provenance — so the class is live in this repo, not exotic.
- **Q5 — scoping buys nothing.** 0.563 s whole-tree, re-measured on `main`.

**A design that is strictly weaker at equal cost is dominated.** That is the whole argument, and the
broken tree was never part of it. Q1 (the rule is fitted to two exclusions that the dispatcher's header
excludes for other reasons) and Q3 (a waiver is visible, a scope is silent) are analytical and stand;
**Q3 is stronger now**, because it no longer needs a broken tree to be true.

### What the correction changes, in the honest direction

1. **The urgency is gone.** This was framed as "the proposal ships a false assurance." It does not.
   It is a choice between a dominated option and a dominating one — a clear recommendation, not an
   emergency, and it should be taken to Joseph as the former.
2. **My step (1) is now a no-op, which simplifies my own recommendation.** The tree is clean, so
   **whole-tree can be installed today with no new waivers.** "Fix or waive the two" was work the
   correction deleted.
3. **`OI-65`'s exposure is smaller than I argued.** The one-predicate-and-none point stands —
   `verify_hash_bindings.py` has zero occurrences of `status`/`SUPERSEDED`/`live`, so the proposal's
   *"live receipt"* is a concept to be authored, not reconciled. The population gap stands: A's zero is
   over **15** `*launch-code-gate*.json` files, and `state/` holds **162** receipts. But my predicted
   live divergence did not materialise when tested.

### One new condition, and it is the most useful thing this round produced

**`verify_hash_bindings` floors its shell-pin half and does not floor its receipt half.**

```
failed = bool(new_bad) or blind or (a.strict and bool(known_bad))
blind  = shell_resolved < SHELL_PIN_FLOOR      # SHELL_PIN_FLOOR = 15
```

`blind` protects shell pins, with an explicit *"Do NOT lower the floor to make this pass — an unwalked
pin is how the Gate-2 pair went stale."* **There is no equivalent for receipt bindings.** `ok` may fall
to any value, including zero, and so long as `new_bad` is empty the gate prints `ALL BINDINGS INTACT`
and exits 0.

**The correct retirement convention is what erodes it.** Retiring a receipt means renaming `sha256` →
`sha256_at_issue`, which is exactly what removes it from `collect()`'s harvest — properly, by design,
with A's conversion asserting the digest multiset unchanged. **Each retirement is right and the coverage
falls silently.** The repair path and the erosion path are the same path.

Its sibling already solved this: `test_hash_bindings` carries `_LAUNCH_CODE_FLOOR` with the comment
*"a discoverer that matches nothing reports success."* **Third sibling asymmetry today** — after
`BEN-173` (one `_verified_` field controlled, its twin not) and `BEN-180` (a band tested above 1 and not
below). `BEN-184`.

**Condition on the recommendation: if this gate becomes the hook's guarantee, give the receipt half a
floor before installing it.** A green that erodes one legitimate retirement at a time is the failure
mode the hook is being added to prevent.

### Unrelated tripwire, surfaced by A's own commit and worth knowing

A recorded *"`_LAUNCH_CODE_FLOOR = 2` and live went 3 → 2. Holds exactly at the floor."* **Zero margin.**
The next legitimate retirement of a launch-code-gate receipt takes it to 1 and fails
`test_gate3_and_gate4_launch_code_freezes_specifically`. Independent of this review; A's, to act on or
not.

## Gate 5 and Gate 6 — deliberately not reported

The commissioning message relayed job-state counts and said *"if you report them, re-run them yourself."*
**I cannot: this session has no Slurm reach.** So I report nothing. What I verified from the tree alone:
Gate 6's block at `19585b7` is intact, and lane B's `PLAN-20260813-gate6-cml-retry-design.md` and
`PREDECLARATION-20260813-gate6-floor-replication.md` landed on `origin/main` as **design and
predeclaration documents**, which is what B is authorised for. **No evidence of movement toward
constructing `C_ML`.** That is "no committed movement," not "B is not executing" — this session still
cannot read another worktree's uncommitted state, the same limit recorded in V32.

