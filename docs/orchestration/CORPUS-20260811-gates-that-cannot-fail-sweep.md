# Corpus definition — "gates that cannot fail" sweep, four confirmed shapes

**Author:** Session D (verifier), 2026-08-11 · **Status:** ROUTED FOR REVIEW, NOT YET SWEPT
· **Reviewer:** Session A (orchestrator), per §D of `PROMPTS-20260811-four-session-closeout.md`
· **Prior art:** `FINDING-20260807-gates-that-cannot-fail-sweep.md` (BEN-070), 624 files, 1 new instance

**Why this document exists before the sweep.** A sweep whose corpus nobody checked returns a plausible
list. The `93/6/1` undefined-reference count was plausible and wrong. Everything below is stated so a
reviewer can attack it *before* it produces numbers: every count carries the command that produced it,
every detector carries a positive control it must fire on and a negative control it must not, and every
detector carries the direction of its own error.

**All counts below were produced by commands run on `78296de` in this session.** None are remembered.

---

## 1. The corpora, enumerated

| id | contents | enumeration command | measured |
|---|---|---|---|
| **C1** | tracked Python | `git ls-files '*.py'` | **338 files, 338/338 parse under `ast`** |
| **C2** | tracked shell | `git ls-files '*.sh'` | **337 files** |
| **C3** | orchestration state receipts | `docs/orchestration/state/**/*.json` | **113 files, 884 hash-valued pin fields, 139 distinct pin field names** |
| **C4** | all tracked JSON | `git ls-files '*.json'` | **311 files** |

C1 includes `omnifold_nn/omnifold/` (9 files), which is vendored upstream OmniFold. **Included, tagged
`vendored`**: a gate that cannot fail inside the engine still gates our results, even though the fix is
not ours to make. First-party C1 is therefore 329.

C1 by owning tree, so a reviewer can see whose code this sweep will land on:
`nd-unfolding` 454 · `2d-unfolding` 108 · `3d-unfolding` 50 · `docs` 43 · `omnifold_nn` 11 · other 9
(counts are over C1 ∪ C2 = 675 files; command: `git ls-files '*.py' '*.sh' | cut -d/ -f1 | sort | uniq -c`).

**Not in any corpus, stated so the silence is not read as coverage:** C++ (6 `.cpp`, 3 `.h`, 2 `.C`),
notebooks (2 `.ipynb`), the cluster checkout (forked from local by construction — see the
cluster/local fork rule), and anything untracked. The sweep says nothing about these.

---

## 2. The four detectors, with controls

A detector that does not fire on its own known instance is not evidence. This is BEN-070's §4.1 —
two detectors in the last sweep were silent on their known instances because `_` is a word character.
**Every control below was run in this session; the results are quoted, not predicted.**

### S1 — a predicate READ before it is registered (PB3 shape)

*Mechanism:* a mutable accumulator is consumed at a point where code below it can still change the
accumulator, so the checks below cannot influence the decision above.

- **Detector:** AST. Per scope (module body, and each function), collect names mutated by
  `.append/.extend/.update/.add/.insert/.setdefault` or `+=`. Flag any *decision read* — the name
  appearing inside an `if`/`while`/`IfExp`/`assert` **test** — at line `L` where a mutation of the same
  name exists at line `M > L` **in the same scope**.
- **Positive control — FIRES.** The pre-fix PB3 shape (`blockers` read into a `.FAILED`-vs-consumable
  ternary above a later `blockers.append`) → detector returns `('blockers', 4)`.
- **Negative control — required before the sweep runs:** HEAD's `p4_evidence.py` `_publish_evidence()`
  path must NOT be flagged (the `.PENDING`+rename repair moved the publish below every blocker).
  *Not yet run; it is the first thing the sweep does, and a failure here withholds S1 entirely.*
- **Measured candidate load: 84 sites across 27 files.** Hand-triageable.
- **Direction of error — OVER-reports.** The dominant false-positive class is a loop that legitimately
  reads and then appends within the same iteration. Triage is by hand and every dismissal will be named.
- **Blind spot:** intraprocedural only. An accumulator mutated inside a *callee* invoked after the
  caller read it is invisible. This is not a small gap — it is how the class would appear in
  well-factored code — and the sweep will not claim to have covered it.

### S2 — a marker never FETCHED (PB4 shape)

*Mechanism:* the consumer obliged to inherit a marker never opens the producer's artifact at all. The
verdict reads as a lost copy in transit; it is a missing input.

- **THE POSITIVE CONTROL FAILS, AND THIS IS THE MOST IMPORTANT LINE IN THIS DOCUMENT.**
  I built an orphan-key census (every string key written into a dict literal or `d["k"] = v` in C1,
  counted across the whole tracked tree, flagging keys whose only occurrence is the write site) and
  then checked it against PB4. **It does not fire on PB4.** `publication_gate_rejects_this` *was* read
  — by `p4_lib.require_adoptable` and by the validator. What was missing was that **one specific
  consumer**, `p4_project_4d.py`, never read it. That is a property of an *edge* (this consumer owes
  this producer), and the obligation exists only in the specification, not anywhere in the code.
  **PB4's shape is therefore not statically detectable in general, and I am not going to claim it is.**
- **What S2 will actually sweep, which is strictly weaker and honestly labelled:** the
  *produced-and-consumed-by-nothing* class. Two detectors:
  - **S2a — orphan key census** over C1 as described.
  - **S2b — decorative pin census** over C3: a pin field whose name occurs nowhere outside the receipts
    that write it has no reader, so nothing can ever act on it.
- **Positive control for the weaker class — FIRES, and it is a live instance found while building this
  document.** `wakerctl_sha256` in
  `docs/orchestration/state/p3f-pet-gate3-queue-latency-reconciliation-56169838.json:70` occurs
  **exactly once in the entire tracked tree** (`grep -rn <value>` and `grep -rn wakerctl_sha256`). It is
  written and fetched by nothing. See §4.
- **Direction of error — UNDER-reports, deliberately.** Occurrence counting is over *all* tracked files,
  so a key merely *mentioned* in a markdown log counts as "fetched". S2's output is a floor on the
  orphan population, never a total. Also blind to dynamic access (`d[k]` for variable `k`), `**kwargs`
  merges, and any consumer outside the tracked tree (including a human reading the JSON).

### S3 — null-as-absent (PB2 shape)

*Mechanism:* `dict.get()` returns `None` for *absent* and for *present-and-explicitly-null*, so a
writer's explicit null inherits a grandfather clause written for receipts that predate the field.

- **Detector:** AST. Flag `x = <expr>.get(k)` **with no default argument**, followed in the same module
  by a control-flow test on `x` (`x is None` / `x is not None` / `if x:` / `if not x:`).
  A regex detector was tried first and **rejected**: the real PB2 code binds the `.get()` to a variable
  on one line and tests it four lines later, so every line-local regex is silent on the known instance.
- **Positive control — FIRES.** Pre-fix `p4_lib.py` (parent of `1440b58`): detector returns both
  `('declared', 5)` and `('got', 7)`, which are exactly the two reads the repair replaced.
- **Negative control — DOES NOT FIRE.** Post-fix `1440b58` (`has_schema = FIELD in receipt`, then
  subscript): detector returns `[]`.
- **Measured candidate load: 69 sites across 26 files** (top: `validate_pet_nominal_gate4.py` 11,
  `wakerctl.py` 6, `train_fullevent_nominal.py` 6, `validate_p3f_pet_fullevent.py` 5).
- **Triage rule, stated in advance so it cannot be chosen to fit the answer:** a site is a DEFECT
  candidate only if the `None` branch is **permissive** — returns `True`/`PASS`, grandfathers, skips a
  check, or `continue`s past one. A `None` branch that refuses is the correct use of the idiom.
- **Blind spot:** `.get(k, <non-None default>)`, which collapses null into the *default* rather than
  into absence — a different bug in the opposite direction, not swept here. Also blind to truthiness
  collapse (`if d["k"]:` treating `null`, `0`, `""` and `[]` alike) and to non-JSON inputs.

### S4 — an artifact asserting a state it cannot have

*Mechanism:* nobody established the artifact's **write condition**, so a reader takes it as evidence of
something the write can never have witnessed.

**This one is only partly mechanizable and the split is stated rather than blurred.**

- **S4a — write-condition slice (mechanical).** For each `json.dump` / `open(..., 'w')` site in C1
  (**measured: 277 write sites across 124 files**), determine statically whether the write sits in a
  failure-only branch (`except`, or under a truthiness test on a blockers/failures accumulator) while
  the payload carries an outcome-ish key (`verdict|status|outcome|ok|pass|result|state`). Flag the
  mismatches. Overlaps S1 by construction and the overlap will be reported, not double-counted.
- **S4b — stale-pin slice (mechanical, and the highest-confidence part of this sweep).** For every pin
  in C3 that names a **tracked repo path**, recompute the digest and compare. A pin that no longer
  holds is an artifact asserting an integrity state it does not have. Instrument already built and
  validated against a known answer (§4). Population: 884 pinned values, of which the tracked-path
  subset is the sweepable part — **that subset has not been sized yet and sizing it is step 1 of S4b.**
- **S4c — residue, HAND REVIEW, not a sweep.** Named explicitly so its silence is not read as coverage:
  `state/waker/BLOCKED-ON-USER.json`, `state/waker/PROCESSED.txt`, `state/waker/events/*.done`,
  `LIVE-STATE.md`, and the three `INTEGRATION_CHECKLIST.md` GATED rows. Session A has already reported
  one instance in this set (BLOCKED-ON-USER.json presenting `\dead{}` scoping as a live gate under
  `second_decision_required`), which is corroboration that the residue is where the class lives — and
  a reminder that **hand review finding one instance is not evidence about the other four.**

---

## 3. What this corpus does about the three classes BEN-070 declared unreachable

Session A asked for this explicitly. Answering it is the difference between a bounded sweep and a
plausible list.

| BEN-070's unreachable class | this sweep's position |
|---|---|
| **wrong population** (BEN-032/025) — whether a check runs over rows that *can* exhibit the defect is a runtime property | **Still unreachable, and not attempted.** One narrow subclass is caught for free: S4b flags a pin over a path that no longer exists, which is a wrong-population instance. Nothing broader is claimed. |
| **never returned PASS on real input** (BEN-040) — needs execution history, not a grep | **Still unreachable. NOT attempted, and the proxy is labelled a proxy.** S2b is its static shadow: a gate whose verdict field nothing ever reads has never influenced anything. That is strictly weaker than "never fired" and will be reported as a *reader* census, never as a coverage claim. BEN-070 called an execution-history harness the highest-value gap; it still is, and this sweep does not close it. |
| **cross-document comparison** (BEN-042) — the two quantities live in different files | **Unreachable in general.** S4b is exactly one cross-document check — receipt digest versus source file — and covers the hash-pin subclass and nothing else. |

**Consequence for how the result must be read.** If this sweep returns few instances, the two readings
BEN-070 left open remain open: either the class is genuinely concentrated in recently-written code, or
the detectors are too narrow. One sweep will not choose between them and this one will not pretend to.

---

## 4. One instance already confirmed while building this document

Recorded here rather than held back, because it is the S2b/S4b positive control and A asked for it
independently as claim (b).

`docs/orchestration/state/p3f-pet-gate3-queue-latency-reconciliation-56169838.json:70` pins
`wakerctl_sha256 = d7c6a215…9bd99c` for path `docs/orchestration/wakerctl.py`.

**Three instruments, deliberately different — not three runs of one.** BEN-088 rule (vi): two runs of
a broken instrument agreeing is determinism. A and the GBDT lane both ran `shasum` against the git
object store, so that is *one* instrument measured twice.

| instrument | what it reads | result |
|---|---|---|
| I1 `git show origin/main:… \| shasum -a 256` | git object store | `04d2e957…` (A's and the GBDT lane's) |
| **I2** `hashlib.sha256` on the **working-tree file** | the filesystem, not git | `04d2e957…` |
| **I3** sha256 of **every historical blob** of the path across `origin/main` | git history — a *different question*: was the pin ever valid? | see below |

I3 is the one that says something the other two cannot:

    04d2e957…  2026-07-20  7e69926d  Cut over to interim Claude root…      <- current content
    bf459853…  2026-07-20  442aee35  Send a 6-hour status digest email
    d7c6a215…  2026-07-20  8c8775f8  Reconcile P3F PET queue latency wake  <- THE PIN
    6c5e97e6…  2026-07-19  f54848dc  Notify the user by email…
    c4ad82be…  2026-07-19  32f62aad  Harden waker…
    0b4c463c…  2026-07-19  be4cd789  Replace hand-cloned wake watchers…

**Verdict: BLOCK — A's claim `PIN HOLDS: False` is CONFIRMED, and the history says more than the
comparison did.**

- The pin was **correct when written**: `d7c6a215…` is exactly the content of `wakerctl.py` at
  `8c8775f8`, the same commit that created the receipt (`git log --all --oneline -- <receipt>` returns
  that one commit and no other — the receipt has never been updated).
- It broke at `442aee35` and again at `7e69926d`, **both on 2026-07-20, the same day it was written.**
- Working tree is byte-identical to `origin/main` (`git diff --quiet origin/main -- <path>`).

**Two of the four seeded shapes, in one artifact.** (i) *S2, never fetched*: `wakerctl_sha256` occurs
exactly once in the whole tracked tree, so **nothing reads it** — no gate could ever have reported the
break. (ii) *S4, asserting a state it cannot have*: the receipt asserts a control-plane integrity
binding that has been false for three weeks with no mechanism capable of noticing.

**And the consequence is an attribution, which is the part a hash comparison does not reach.**
`FINDINGS.md` BEN-084 justifies a design decision with this pin: *"Deliberately a text file and not a
feature: `wakerctl.py` is hash-pinned into `p3f-pet-gate3-…json`, so adding an event-lifecycle state
machine would move a sha a receipt cites."* **That premise was already void when it was written on
2026-08-11** — the sha had moved twice, three weeks earlier. The decision may well still be right on
its *other* stated ground (new surface generates defects faster than it closes them), and I am not
challenging the decision. I am recording that one of its two stated reasons does not exist.

**Not filed against BEN-084 by me.** It is another lane's row; per §D the correction routes to its
owner. Disposition of the pin itself (re-run and re-issue, or record the pin as deliberately retired)
is Session C's, per A. **Nobody should hand-edit the hash.**

---

## 5. Abort conditions — how this sweep is allowed to fail

Adopted from BEN-070 §4.2, where a sweep reported "0 hits" from a `--root` that examined nothing.

1. **Corpus floor.** C1 < 300 files parsed, or C2 < 300 files read → abort. Do not report.
2. **Control gate.** Any detector whose positive control does not fire is **withheld entirely**, and its
   absence is reported as a hole rather than as a clean result. S2's positive control against PB4
   already failed; S2 ships only under its weaker, relabelled claim (§2).
3. **Print the matched lines, not only the count** (BEN-088 rule v). A count cannot show that it matched
   the wrong thing.
4. **Every dismissal is named.** A triage table with "the remaining ~20 are false positives" is not
   reviewable; each dismissal gets its reason.

## 6. What review should attack

1. **Is C1 ∪ C2 the right corpus, or does the class live in C3/C4 (the artifacts) more than in the
   code?** §4 is one data point that it lives in the artifacts, and my detector weight is on the code.
2. **S2 is the weak one.** Its positive control failed and it ships relabelled. Is the weaker class
   worth sweeping at all, or is that budget better spent on S4c hand review?
3. **S4b needs sizing before it is credible** — how many of the 884 pins name a tracked repo path?
4. **Is 84 (S1) + 69 (S3) + 277 (S4a) hand-triageable in one session**, or should S4a be dropped in
   favour of finishing S1/S3/S4b properly? My inclination is the latter; I would rather return three
   complete detectors than four partial ones.
