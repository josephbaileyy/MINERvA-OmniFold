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
