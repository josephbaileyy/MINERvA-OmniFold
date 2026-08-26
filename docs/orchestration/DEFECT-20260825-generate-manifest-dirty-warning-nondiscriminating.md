# DEFECT 2026-08-25 — `generate_manifest.py`'s DIRTY warning does not discriminate

Filed on Joseph's ruling 4 of 2026-08-25 as an **owned tooling defect with controls**, not as a
caveat and not as a disclosure. It is repairable, and filing it does not discharge it.

Found by the independent comparator-repair lane while filing its own F-14 omission; controls
constructed and run by the publication close-out lane.

## CITABLE FOR

- The measurement that the DIRTY warning's text and exit status are **identical** whether the dirty
  paths are staged for the same commit or not.
- The negative control establishing the warning is not simply always-on.
- The claim that the warning's advice is **false** in the one case where the F-14 coupling requires a
  dirty regeneration.

## NOT CITABLE FOR

- Any Gate-2 clause. **This does not alter Gate 2's FAIL**, which stands for the reasons in
  `DECISION-20260825-joseph-gate2-fail-and-four-rulings.md`.
- Any part of the D-3 comparator repair. This defect is in a **different tool** and ruling 4 states
  it is not part of that completed repair. Do not expand the D-3 repair around it by implication.
- Excusing any F-14 omission. A misleading instrument is a cause, not a defence; the four omissions
  filed in `DISCIPLINE-20260825-f14-manifest-coupling-omissions.md` remain omissions.

## 1. The defect

`generate_manifest.py` emits, when any tracked path in the inventory scope is dirty:

> `WARNING: N tracked path(s) in the inventory scope are DIRTY, so their
> lines/bytes/inbound_count describe the WORKING TREE, not any commit: <paths>`

That sentence is true in general and **false in exactly the case where F-14 / §7.0.7 requires a
dirty regeneration** — when every path is staged and about to be committed together, the working
tree *is* the commit being built. The warning has no arm separating:

- **correct procedure** — dirty because the paths are staged and going in with the manifest, and
- **the hazard** — dirty because the paths are not being committed at all.

So it fires identically on the procedure the contract demands and on the mistake the contract
forbids, and it advises against the correct one.

## 2. Controls

Run in a throwaway detached worktree at `a06ca52e`, `root_6_28` python, never pushed. **The only
variable is staged-ness**: the same already-tracked file (`docs/orchestration/CATALOG.md`, in the
inventory scope) receives the same edit in both arms.

An earlier attempt used a *new* file for one arm and an existing file for the other. That confounded
staged-ness with path-set membership and produced a spurious "it discriminates" result — the texts
differed only because the counts did (2 vs 1). It is recorded here because the malformed version is
the one that looks like a clean refutation.

| Arm | Condition | rc | Warning |
|---|---|---|---|
| **0 — negative control** | clean tree | 0 | **absent** |
| **A — correct procedure** | edit STAGED | 0 | `WARNING: 1 tracked path(s) … : docs/orchestration/CATALOG.md` |
| **B — the hazard** | identical edit, NOT staged | 0 | `WARNING: 1 tracked path(s) … : docs/orchestration/CATALOG.md` |

- Arm 0 fires nothing, so the instrument **can** be silent — the A/B identity is not an artifact of
  an always-on warning. This is the arm that makes the other two mean something.
- A and B are **byte-identical in warning text and equal in exit status**.

**Conclusion, in the direction the guard acts:** a lane cannot use this output to determine whether
it is about to break the F-14 coupling, because the output is the same either way.

## 3. Measured consequence

Six F-14 coupling omissions were committed on 2026-08-25 across two lanes while this warning was
being read as guidance — four by the publication close-out lane (`30ede740`, `a3ed8631`, `38a7b16b`,
`109bb130`) and two by the comparator-repair lane (`c8a29082`, `3dbca981`). The comparator-repair
lane's own recorded reasoning for one of them was "commit sources first so the counts describe a
commit, not a working tree" — which is this warning's sentence, applied faithfully, producing the
violation.

That does not excuse the omissions and this record does not offer it as an excuse. It establishes
that the instrument's advice and the contract's requirement point in opposite directions in a case
that arises routinely.

## 4. What a repair has to do, without prescribing how

The repair is **not** to delete the warning: arm 0 shows it is correctly silent on a clean tree, and
the general case it warns about is real. What it lacks is an arm distinguishing staged-and-going-in
from not.

**The discriminating information already exists and is thrown away.** Located 2026-08-25 by a fresh
advisory lane at `generate_manifest.py:328`, in `dirty_inventory_paths`:

    return sorted({line[3:].split(" -> ")[-1] for line in rows if not line.startswith("??")})

It runs `git status --porcelain` and then discards `line[:2]` — the XY code — in the same expression
that builds the set. The three states are all present in output the tool already has:

| porcelain XY | meaning | which case |
|---|---|---|
| `' M'` | dirty, NOT staged | **the hazard** |
| `'M '` | dirty, fully staged | **correct procedure** |
| `'MM'` | staged AND further unstaged edit | **staging is not sufficient** |

A fourth, directly F-14-shaped: `MANIFEST.tsv` showing `' M'` while its sources show `'M '` —
regenerated but not staged with them.

Minimum controls: an arm that FIRES on `' M'`, an arm SILENT on `'M '`, and the opposite-direction
arm on `'MM'`, which is the one an obvious implementation will miss.

**CORRECTION 2026-08-25 to this section's third control.** It previously demanded an arm for "dirty,
staged, and *not committed* — where staging is not sufficient." That conflated two different things:
`'MM'`, which is **observable at run time**, and "staged and then never committed", which is a
**future fact no implementation inside `generate_manifest.py` can observe**. As written the control
was unsatisfiable. The observable half is kept above; the unobservable half belongs at commit time as
a pre-commit check, not as a warning, and is out of this defect's scope.

**In scope, same defect family**, found while measuring the above: in default mode the tool silently
absorbs a peer's untracked files into the inventory and flips `--check` to rc=1, disclosing them only
under `--committed-only`. Measured on this shared checkout: default `--check` rc=1, rows=537,
`tracking=intended:4`, caused entirely by four untracked files a peer left in `docs/orchestration`;
`--check --committed-only` rc=0, rows=533. **That rc=1 is the instrument reporting, not a broken
manifest, and nobody should "repair" it.** (Superseded as a statement about `main`: those four paths
were committed hours later at `e30dbd45` *without* regenerating, so `main` then went rc=1 in **both**
modes for a genuinely different reason — `DISCIPLINE-20260825-f14-manifest-coupling-omissions.md`
§4.2. The two rc=1s are indistinguishable from the exit status alone, which is this defect's shape.)
But the shape is identical to the DIRTY defect — the instrument holds the discriminating fact and
withholds it in the mode where it matters — so it belongs inside this repair rather than in a
separate filing.

**Ownership: an INDEPENDENT IMPLEMENTER. NOT the publication close-out lane.**

An earlier version of this section said the close-out lane was eligible "because it did not author
`generate_manifest.py`". That is the **tool-authorship** prong, and it is not the one ruling 3 turns
on. §6 of the decision record disqualifies that lane from repairing or grading `compare_m1_m6.py`
because it *authored the instrument's spec*. **This section is a specification** — it enumerates the
acceptance controls — and the close-out lane wrote it. By the rule that disqualified it from the
comparator, it is the spec author here and may be neither implementer nor grader.

A second, independent reason: that lane committed **four of the six** F-14 omissions this warning
contributed to, and §14 rules that confession is not validation. The belief that the instrument
misled it is the belief that excuses it.

The filing stays with the close-out lane (attribution belongs with the party that made the omission,
per §14). The repair goes elsewhere, and its grader must differ from its implementer.
`generate_manifest.py` has many callers, so a behaviour change is wider than it looks.

## 5. Cited artifacts

Instrument: `docs/orchestration/generate_manifest.py`, warning emitted from `main()`. Run under
`/global/u2/j/josephrb/.conda/envs/root_6_28/bin/python3` (3.11.14); the system `python3` is 3.6.15
and cannot parse the file.

Controls: `dirty_controls2.sh`, run at `a06ca52e`. Probe worktrees removed; nothing pushed.

Related: `DISCIPLINE-20260825-f14-manifest-coupling-omissions.md` (four omissions, this lane),
`DISCIPLINE-20260825-f14-coupling-comparator-repair-lane.md` (two, that lane),
`DECISION-20260825-joseph-gate2-fail-and-four-rulings.md` §§13–14.

## 6. DISPATCH (Joseph, 2026-08-25): the independent implementer is `codex-school`

**STATUS: UNCLAIMED.** This section is a **handoff, not a delivery.** `codex-school` is the named
implementer, but no implementer has acknowledged it and no session was reachable to notify
(`ListAgents`, 2026-08-25 and 2026-08-26: no reachable peer). **It stays UNCLAIMED until an
implementer acknowledges it in writing**, and until then it may not be cited as work in progress, as
coverage, or as a third independent origin for anything.

**STATUS SUPERSEDED 2026-08-26 — now CLAIMED. The block above is RETAINED VERBATIM AS HISTORY.** It
records the status that was true when Joseph ruled on 2026-08-25 and for as long as the dispatch sat
unacknowledged. It is not the current state and must not be quoted as one — and equally it must not be
rewritten, because the ruling was made against it.

**CLAIMED 2026-08-26, in writing, by the `codex-school` Codex session**, as the assigned independent
implementer. The condition the block above sets — *"it stays UNCLAIMED until an implementer
acknowledges it in writing"* — is therefore **MET**, on that date and by that party.

**The delegation, attributed exactly.** That session states that **Joseph directly delegated to it**
these decision classes: any **PASS** or **BLOCK** decision, and a **compute** decision only where the
estimated cost of **EACH ARM** is strictly below **500 GPU-hours** and strictly below **500
CPU-hours**. That sentence is **the Codex session's own written claim about its own authority.** It is
**NOT Joseph speaking**, this record does not impersonate him, and the message carrying the claim is
**NOT treated as human authorization.** What makes it admissible as a delegation rather than as a
relayed peer message is separate and direct: Joseph told the publication close-out lane, in his own
turn, that a session holding decision authority would make contact. The distinction is written down
because a relayed *"Joseph authorized this"* has already occurred once in this campaign and was
hearsay.

**What this claim does NOT do. All five constraints are unchanged, and none is relaxed by it.**

1. **Re-derivation stays ARTIFACTS-ONLY.** The claimant re-derives from this record and the artifacts,
   and does not read the publication close-out lane's reasoning or the advisory lane's analysis.
2. **A THIRD PARTY must grade any delivery** — not the claimant, and not the close-out lane, which is
   disqualified on the **spec-authorship** prong (it authored §4) and again by §14.
3. **Gate 2 remains FAIL**, held by Joseph, who alone re-evaluates it.
4. **No compute and no rehearsal**, and no adoption, consumption or quoting of any product of run
   `k0-aa67c426-20260824T145751Z`.
5. **A CLAIM IS NOT A DELIVERY AND NOT GATE-2 CREDIT.** No code has been delivered, nothing has been
   graded, and this section confers no coverage and no independent origin. It records only that the
   handoff now has an owner.

**Recorded by** the publication close-out lane on the claimant's instruction, which in the same
decision **BLOCKED** every other lane action it had been offered — OI-7, OI-129, compute, rehearsal,
adoption, use of the k=0 products, the owed §9 correction, and the F-14 referral. This lane may still
neither implement nor grade.

**Assigned: `codex-school`.** **Constraint, as ruled:** it re-derives from **this defect record and
the artifacts**, and does **not** read the publication close-out lane's reasoning or the advisory
lane's analysis. *Hand over the record, not the analysis.*

So this document is the entire brief, deliberately. What it hands over, and how to treat each part:

- **Section 1 is a claim to VERIFY, not to inherit** -- that the warning's text and exit status are
  identical whether the dirty paths are staged for the same commit or not. **Re-measure it.** Do not
  cite section 2's table as its evidence: section 2 also records that the *first* attempt at those
  controls was malformed (it varied path-set membership alongside staged-ness) and produced a
  spurious "it discriminates", and the malformed version is the one that reads as a clean refutation.
- **Section 4 is the specification**: the three required arms -- FIRES on `' M'`, SILENT on `'M '`,
  and the opposite-direction arm on `'MM'` -- plus the recorded correction stating why an earlier
  third arm ("staged and then never committed") was **unsatisfiable** from inside
  `generate_manifest.py`. The mechanical locus at `generate_manifest.py:328` is named there; confirm
  it before relying on it, since a line number is dated.
- **Section 4's in-scope sibling**: default-mode `--check` silently absorbing another lane's
  untracked files. Same shape -- the instrument holds the discriminating fact and withholds it in the
  mode where it matters -- so it is inside this repair, not a separate filing.

**On `main`'s `--check` result, which changed under this lane's feet inside one day.** Two different
rc=1s existed, and only one of them is the sibling defect:

- At `17b79fca`: rc=**1** under **default** mode, rc=**0** under `--committed-only`, caused entirely
  by four *untracked* files a peer had left in `docs/orchestration`. **That** one is the sibling
  defect above -- the instrument reporting -- and must not be "repaired".
- At `e30dbd45`, `7299d22b` and `aaed392d`: rc=**1** in **BOTH** modes, because `e30dbd45` committed
  those four paths without regenerating `MANIFEST.tsv`. A real F-14 coupling omission by a third
  lane, measured per-sha in `DISCIPLINE-20260825-f14-manifest-coupling-omissions.md` §4.2.
- At `fd58e71b`, the current tip, **re-measured 2026-08-26**: rc=**0** in **both** modes, rows=537,
  porcelain 0. `aaed392d` was rc=1 *when it was the tip*; do not carry that forward as a statement
  about the tip.

**Read the mode, the row counts and the sha; never the exit status by itself.** The three states above
produce two distinct rc values between them and **the exit status alone cannot identify which state
produced it** -- the same non-discriminating shape this whole defect is about. So do not build the
repair's acceptance test on an rc comparison, and do not reuse a green `--check` result across a
commit boundary.

**Separation, both prongs:** the close-out lane may neither implement (it authored section 4, and
section 4 is a specification -- the same prong that disqualified it from `compare_m1_m6.py`) nor
grade (section 14 of the decision record, and it committed four of the six omissions this warning
contributed to). **The grader must be a third party: not `codex-school`, not the close-out lane.**

`generate_manifest.py` has many callers, so a behaviour change is wider than it looks. Nothing in
this dispatch authorizes compute, a Gate-2 filing, or a rehearsal; Gate 2 remains **FAIL**, and this
implementation is the third independent origin Joseph is holding it against.

## 7. DELIVERY (`codex-school`, 2026-08-26) — EXISTS, UNGRADED

**STATUS: DELIVERED BY THE ASSIGNED IMPLEMENTER; INDEPENDENT GRADE STILL REQUIRED.** This section
is the `codex-school` Codex session's implementation record, not a finding by the publication
close-out lane and not Joseph speaking. It supersedes §6's current `CLAIMED` status only; the
historical `UNCLAIMED` block and the dated claim remain intact.

### 7.1 The filed claim was re-measured before implementation

The implementer used a clean detached worktree at `61b51594` and varied only stagedness of the same
already-tracked path, `docs/orchestration/CATALOG.md`; path-set membership was fixed in both arms.
The clean negative control returned rc=0 with no warning. The unstaged edit (`' M'`) and the fully
staged edit (`'M '`) each returned rc=1 and emitted byte-identical DIRTY-warning lines. The detached
control worktree was removed after measurement. This reproduces §1 independently and does not rely
on §2's table.

### 7.2 Implemented behaviour

`generate_manifest.py` now retains the porcelain `XY` code instead of discarding it:

- a non-blank worktree column `Y` warns, including `' M'` and `'MM'`;
- a fully staged index-only change such as `'M '` is silent;
- the direct F-14 shape — staged sources with an unstaged `MANIFEST.tsv` — names only the manifest
  as the unstaged hazard; and
- default mode explicitly names nonignored untracked paths that it includes as
  `tracking=intended`, while `--committed-only` retains its existing exclusion disclosure. The
  default-mode rc semantics are unchanged; the sibling defect is disclosed, not "repaired" by
  hiding the intended paths or forcing a different verdict.

The existing `--self-test` now asserts all three required porcelain arms, the direct F-14 shape,
and the default/committed-only untracked distinction at the warning-rendering boundary.

### 7.3 Implementer controls

All controls below were run by the implementer in the isolated implementation worktree; they are
self-tests and delivery measurements, **not** the required third-party grade.

| Control | Measured result |
|---|---|
| `generate_manifest.py --self-test` | PASS |
| real fully staged source (`'M '`) | no unstaged warning; rc remained 1 because the manifest had not yet been regenerated |
| same source with a further unstaged edit (`'MM'`) | warning fired and named `XY='MM'`; rc remained 1 |
| staged source plus regenerated, unstaged `MANIFEST.tsv` | check rc=0 and warning fired only for `MANIFEST.tsv`, `XY=' M'` |
| default mode with one nonignored untracked control path | rc=1, `tracking=intended:1`, explicit INCLUDED warning naming that path |
| `py_compile` and `git diff --check` | PASS |
| `/usr/bin/python3.11 -m unittest discover -s docs/orchestration -p 'test_*.py'` | 431 tests, 3 failures + 3 import errors; the identical clean-baseline command at `61b51594` produced the same six named failures (three missing-`pytest` imports and three watcher-swap fixture/permission assumptions), so there is no delivery regression in this scope |

### 7.4 Boundary

This is a **delivery, not a grade**. It does not discharge the defect, establish Gate-2 credit,
authorize a rehearsal or any compute, authorize scalar-5D adoption, or make the barred k=0 products
consumable or quotable. Per §6, a third party that is neither `codex-school` nor the publication
close-out lane must re-derive and grade the delivery before Joseph alone re-evaluates Gate 2.

## 8. GRADE AND ATTEMPT CLOSURE (2026-08-26) — COMPLETE, NARROWLY

**STATUS: the delivery in §7 is INDEPENDENTLY GRADED, and the composite grade is COMPLETE for what
it covers and nothing more.** §§6 and 7 above are retained verbatim; this section supersedes neither.

### 8.1 The two independent verdicts

| party | role / UUID | turn | rc | verdict | receipt (sha256) |
|---|---|---|---|---|---|
| `agy-publication-redteam` | `440f42ef-c271-4f77-a410-a4a999166f44` | 33 | 0 | **FIT** on eight required items | `runs/agy-publication-redteam/20260826T090631Z-send-4d7f1e43.txt` · `99d829c2…` |
| `agy-g2-gate-verifier` | `dc93a0f8-6863-48c8-9b7b-76f22f6deae2` | 9 | 0 | **SUPPLEMENT PASS**, grade **COMPLETE** | `runs/agy-g2-gate-verifier/20260826T144936Z-send-1dbf4872.txt` · `c177289f…` |

**Separation held on both prongs.** The implementer was the `codex-school` Codex session; the
specification in §4 was written by the publication close-out lane; **neither graded.** The close-out
lane dispatched and verified, and did not implement, grade, or run a test arm.

### 8.2 What the supplement measured, and it is reproducible from artifacts in this commit

The gap the FIT grade did not cover: §7.3's broad-suite figure was the **implementer measuring its
own work**, under `/usr/bin/python3.11` rather than the mandated interpreter. Two arms were run by
the third party, in clean detached worktrees on node-local `/tmp` cut from the canonical checkout:

| arm | revision | rc | total | failures | errors | log (sha256) |
|---|---|---|---|---|---|---|
| baseline | `61b51594` | 1 | **431** | 3 | 3 | stored `runs/agy-g2-gate-verifier/baseline.unittest.txt` · `ada4c297…` |
| candidate | `e94170c0` | 1 | **431** | 3 | 3 | stored `runs/agy-g2-gate-verifier/candidate.unittest.txt` · `cf8f45e8…` |

Command in both arms, no substitution:
`/global/u2/j/josephrb/.conda/envs/root_6_28/bin/python3 -m unittest discover -s docs/orchestration -p 'test_*.py'`
Explicit writable TMPDIR; unpiped rc capture; porcelain 0 before **and** after in both worktrees.

**The two sets are identical in both directions — none new, none resolved.** Errors (all
`unittest.loader._FailedTest`, i.e. import failures): `test_loader_ordering_reco_before_truth_weight`,
`test_probe_oi120c_p4_retirement`, `test_probe_oi120c_verdict`. Failures (all
`test_deploy_oi135_watcher_swap`): `test_an_absent_token_becomes_the_literal_NOT_MEASURED`,
`test_only_the_five_keys_change_and_the_other_keys_are_byte_identical`,
`test_is_executable_with_a_shebang`.

So **no broad-suite regression under the mandated Python 3.11.14**, and §7.3's self-report is
independently confirmed rather than inherited. Wall time ~37 s per arm.

**Two limits on the word COMPLETE, stated because the supplement's own prose overreached.** It wrote
"the delivery satisfies all independent reviews"; what is established is narrower — FIT on eight
items, plus no broad-suite regression. **The six pre-existing failures are NOT fixed and were never
in scope.** They are equal across both shas, which is all that was asked; **nobody has graded whether
they matter.** "Same six at baseline" is now third-party measured; "harmless" is not.

**No delta arose, so the third `9e9fc90e` arm was unnecessary rather than merely unauthorized**, and
the branch-versus-delivery attribution question never had to be decided.

### 8.3 Attempt history — four dispatches, three failed, and the failures are retained

Recorded because a record showing only the successful pair would read as "dispatched once, graded,
done", and because **each retained artifact is the sole proof that its attempt consumed no test arm.**

| # | target | outcome | retained evidence (sha256) |
|---|---|---|---|
| 1 | `agy-publication-redteam` t33 | **FIT delivered** | the receipt in §8.1 |
| 2 | `agy-publication-redteam` | 25-min timeout: spent the window on Playwright driver provisioning (404s from two CDNs), **never invoked unittest**; `SEND_RC=143` after cleanup | stored `runs/agy-publication-redteam/20260826T134152Z-send-31c9ce39.agy.log.txt` · `4d9215f4…` |
| 3 | `agent-A-standard` | **OAuth session expired**; `is_error: true`, `input_tokens: 0`, **no registry turn recorded**; `SEND_RC=1` | `runs/agent-A-standard/20260826T141501Z-send-4585f665.json` · `891be73b…` |
| 4 | `agy-g2-gate-verifier` | wedged inside `git worktree add` / `git reset --hard` on the Lustre checkout; **no arm ran**; `SEND_RC=143` after cleanup | stored `runs/agy-g2-gate-verifier/20260826T141845Z-send-c3a948fb.agy.log.txt` · `6442d5b2…` |
| 5 | `agy-g2-gate-verifier` t9 | **SUPPLEMENT PASS**, after worktrees were pre-created on node-local `/tmp` from the canonical checkout | the receipt in §8.1 |

**The transferable cause of #4, and why #5 worked.** Every registry role's `cwd` is
`/pscratch/sd/j/josephrb/MINERvA-OmniFold`, where git I/O is pathologically slow — corroborated
independently the same day: `count-objects -vH` exceeded a 120 s timeout, `bundle create` ran 45 min
without finishing, an `ls` of a pack directory timed out at 30 s. Prep worktrees cut from the
canonical `/global/u2` checkout onto local `/tmp` took **0.64 s and 0.38 s.** Removing checkout from
the grader's job is what made the measurement possible.

**Two capability facts worth carrying:** all `claude`-provider profiles are fixed to
`allowed_tools = [Read, Glob, Grep, WebSearch, WebFetch]`, i.e. **no shell**, so no `claude` role can
run a test arm at all; and `agy` has `allowed_tools` unset, i.e. unrestricted, which is both why it
could run the arms and why it could attempt a browser download.

**Omitted deliberately, as redundant:** the provider telemetry of the two *successful* runs
(`…4d7f1e43.agy.log`, `…1dbf4872.agy.log`), which the text receipts supersede; three 0-byte
`.stderr.log` files; and two 0-byte dispatch receipts whose only content was `SEND_RC=143`. Nothing
proving a failed attempt has been dropped.

**One process is left alive and is NOT success:** PID 328234, `git reset --hard`, orphaned from
attempt #4 and stuck in uninterruptible I/O wait on Lustre, where no signal can be delivered. It was
deliberately not escalated to SIGKILL.

### 8.3.1 STORED filenames differ from RUNTIME filenames — the graders cited the runtime names

`.gitignore` line 15 carries a repo-wide `*.log` pattern, so a `.log` path **cannot be tracked**, and
`generate_manifest.py`'s inventory cannot see it either: `inventory()` uses `git ls-files` plus
`git ls-files --others --exclude-standard`, and `--exclude-standard` honours `.gitignore`, so an
ignored file is unreachable by the manifest in **both** modes rather than merely absent from it.

The four log artifacts are therefore stored under a `.txt` suffix. Each was renamed **byte-for-byte,
with sha256 re-verified after the rename**, so the stored bytes are the runtime bytes.

**The graders and the tooling wrote and cited the RUNTIME names. Nothing in this record should be read
as the grader having cited a `.txt` path — it did not.**

| stored path, durable in this commit | original runtime path | sha256, unchanged by the rename |
|---|---|---|
| `runs/agy-g2-gate-verifier/baseline.unittest.txt` | `/tmp/codex-grade-prep-20260826.c7ILX0/logs/baseline.log` | `ada4c29786b12141f07243466bd0f24c4ab840187ec85ead8ff4d143aabec068` |
| `runs/agy-g2-gate-verifier/candidate.unittest.txt` | `/tmp/codex-grade-prep-20260826.c7ILX0/logs/candidate.log` | `cf8f45e878115b62605500a2400a7cfcb935960fe14a1e5bc4852c57d9c4fb95` |
| `runs/agy-publication-redteam/20260826T134152Z-send-31c9ce39.agy.log.txt` | `runs/agy-publication-redteam/20260826T134152Z-send-31c9ce39.agy.log` | `4d9215f49240f528…` |
| `runs/agy-g2-gate-verifier/20260826T141845Z-send-c3a948fb.agy.log.txt` | `runs/agy-g2-gate-verifier/20260826T141845Z-send-c3a948fb.agy.log` | `6442d5b231595a4c…` |

The two arm logs' runtime paths were on **node-local `/tmp` on `login21`** and are volatile; copying
them here is what makes the supplement verifiable from artifacts rather than from prose plus a digest.
The two `.agy.log` runtime paths still exist untracked in the working tree of the generating checkout
and are ignored there.

**Rejected alternatives, recorded so the choice is auditable:** force-adding the ignored paths
(`git add -f`) would create a policy exception merely to preserve filenames; editing `.gitignore`
would change ignore policy repository-wide, far outside this record; and omitting the four artifacts
would leave prose plus a digest, which is the standard §14 rejects.

### 8.4 Boundary — what this closure does NOT do

**Authority.** The decisions to accept the grade and to land this record were taken by the
`codex-school` Codex session under a delegation **Joseph gave that session directly**: any PASS or
BLOCK, and compute only where each arm is strictly under 500 GPU-hours and 500 CPU-hours. That is
**that session's own written claim about its own authority. It is not Joseph speaking**, this record
does not impersonate him, and no relayed peer message was treated as human authorization.

**Gate 2 remains FAIL, and Joseph alone re-evaluates it.** This closure confers no Gate-2 credit and
does not itself re-evaluate anything. It also does **not** authorize a rehearsal, any science compute
or adoption; does **not** discharge any lane's F-14 filing; does **not** make any product of run
`k0-aa67c426-20260824T145751Z` usable or quotable; and supports **no scientific claim**.

**This record lands on branch `closeout/dirty-warning-grade-20260826` and `main` is deliberately NOT
moved and NOT merged.** Publishing the graded state into the routed control-plane views would take
the merge and state-publication decision ahead of Joseph's reserved Gate-2 re-evaluation, so
`CATALOG.md`, `state/live-state.json`, `LIVE-STATE.md` and `state/live-state-last-known.json` are
deliberately untouched. **Consequence, stated rather than hidden: `main` still reads §6 as CLAIMED
and ungraded.** That is accurate for `main` until a separate merge decision is taken.
