# Brief: B1 normalization fix implementer

Written 2026-07-29. Point a fresh session at this file path — do not paste it inline. Three
successive inline pastes of this brief arrived damaged (duplicated blocks, a severed table,
and systematic ~24-character mid-line excisions), and each time the damage was initially
read as a content error. `cat` it, or tell the session to read this path first.

---

## Validity — check this before trusting anything below

**This brief was accurate at `25e72f0`.** Run:

```bash
git -C /Users/josephbailey/local-research/MINERvA-OmniFold log --oneline 25e72f0..HEAD
```

**If that prints anything, read those commits before you rely on a single claim here.** Not a
formality: the first version of this file asserted that no runbook step owned the Gate-4
re-issue, and a commit landed ten minutes later that added one. It was wrong by the time
anyone could have read it.

This is the standing hazard for any brief kept as a file. `AUDIT-FINDINGS-20260729-B.md` §6
records a whole audit lane wasted because it was briefed from a stale
`start-audit-planner.md` and faithfully reproduced the stale finding — "a stale brief reliably
reproduces the stale finding." A file-based brief trades paste damage for staleness. That is
the right trade, but only if you check.

---

You are the B1 fix implementer for the MINERvA-OmniFold campaign.

Repo: `/Users/josephbailey/local-research/MINERvA-OmniFold` (branch `main`, HEAD `25e72f0`).

Another session has been active in this repo. `docs/POST_PUBLICATION_REORG_PLAN.md` may show
uncommitted changes that are not yours. Leave them alone.

## Read first, in order

1. `docs/orchestration/B1-NORMALIZATION-FIX-DESIGN.md` — your spec; §2 is the deliverable.
2. `docs/orchestration/AUDIT-FINDINGS-20260729-B.md` — §7, B-3/B-4/B-5, the consolidation
   note at the end of §2, and §9 (a refuted finding — read it for the trap it records).
3. The four 2026-07-29 entries at the tail of `nd-unfolding/ND_OMNIFOLD_RUN_LOG.md`.

## How to read the facts in this brief

Every factual claim below is tagged with its provenance:

- **[EXEC]** — verified by running something on 2026-07-29.
- **[READ]** — verified by reading the named `file:line`.
- **[RELAY]** — asserted from another session's report and **not** verified. Treat each as a
  hypothesis and check it before you depend on it.
- **[EXEC-OTHER]** — executed, but by a different session than the one writing it down. For
  you that is a **[RELAY]**: you have the outcome, not the evidence.

This tagging exists because an earlier version of this brief stated eight confident facts, one
of which was false, and it survived two reviews precisely because it was dense and
well-formatted. Density reads as authority. Spend your verification budget accordingly.

## Deliverable

One coherent patch set. Code-only; nothing here needs the cluster. `/pscratch` returns
2026-08-03 22:00 PT.

**a. §2a loader.** `normalization_factor = 1e6 * R` on the measured `DataLoader` call.

**b. §2c Gate-2.** Retarget the hardcoded `1e6` assertions. The validator must derive `R`
from the dump itself rather than read it from the loader's `meta`, or the gate certifies the
loader against the loader's own claim.

**c. §2d Gate-4.** The reco-level **ratio** check (`== R`) — *not* the absolute-yield form
printed in the design doc, which is not subsample-invariant; see `AUDIT-FINDINGS-20260729-B.md`
§7 — **and the plumbing that makes it fire.**

`check_normalization` is dead code today:

- **[READ]** `validate_pet_nominal_gate4.py:210` is `def main(argv=None)`; its only call to
  `build_gate4_report` is at `:223` and passes no `normalization=`. The parameter is
  `if ... is not None`-gated, so the check is silently skipped.
- **[READ]** the driver's `np.savez_compressed` at `train_fullevent_nominal.py:134-137` emits
  only `weights_push, mc_indices, estimator_fingerprint, bkg_mode, tag, target` — none of the
  check's inputs.

A correct assertion that never executes is the same partial-fix failure one level down.

Preferred shape, per §2d: the driver persists the reco-masked sums, the validator
independently recomputes them from the G2 dump, and the gate asserts the two agree. Do not let
the driver be the sole source — a gate fed the driver's own arithmetic certifies nothing.
**[READ]** both files are bound by the same receipt
(`p3f-pet-gate4-launch-code-gate-20260721.json`), so this costs one Gate-4 re-issue either
way; independence is the only tie-break, which is why the design rejects the driver-only
route. If you see a better shape, propose it.

**d. The two tests §4 requires.** A closure that injects a known truth-level rate change and
verifies recovery, and a unit test that **FAILS** a `1e6`-normalized step-1 target and
**PASSES** a `1e6*R` one.

Prefer **new** test files. **[EXEC]** `test_pet_nominal_gate4_validator.py` and
`test_pet_fullevent_nominal_launcher.py` are both bound by
`p3f-pet-gate4-launch-code-gate-20260721.json`, so editing them voids two further bindings
for no necessary reason.

**Land it whole.** The dominant failure mode is a partial fix that consumes the 08-03 window.
**But "stop and report" is an authorized outcome:** if a blocker makes the full set
unlandable, land **nothing**, write the blocker up, and say so plainly. Do not ship a subset.

## The binding checkpoint — read before editing anything

**A correct patch cannot leave the verifier green.**

**[EXEC]** `verify_hash_bindings.py` resolves 92 of 393 bindings. `localize()` at `:74-78`
remaps the receipts' `/pscratch` prefixes onto the local checkout, so every file you are about
to edit **is** covered and currently matches. Run it before and after.

- **Before:** `ALL BINDINGS INTACT`.
- **After:** it **must** report mismatches. **[EXEC]** the expected set is exactly these four
  files / five bindings / three receipts:

| file | receipt | from |
|---|---|---|
| `fullevent_fps_dataloader.py` | `g2-gate2-construction-20260719.json` | §2a |
| `fullevent_fps_dataloader.py` | `G2_GATE2_TARGET_RUNTIME_RECEIPT.json` | §2a |
| `gate2_target_runtime.py` | `G2_GATE2_TARGET_RUNTIME_RECEIPT.json` | §2c |
| `train_fullevent_nominal.py` | `p3f-pet-gate4-launch-code-gate-20260721.json` | §2d |
| `validate_pet_nominal_gate4.py` | `p3f-pet-gate4-launch-code-gate-20260721.json` | §2d |

Note the loader is bound **twice**. Going red on those five is the fix working — the receipts
correctly noticing their frozen code changed. Record the exact list. Any file outside that set
going red is yours to explain. **Never hand-edit a sha256 to restore green.** Also record each
edited file's sha256 by hand, before and after, as documentation for the re-issue.

**The verifier will print FOUR `MISMATCH` lines, not five** (`88 OK` → `84 OK`) — confirmed by
running the patch on 2026-07-29. Both Gate-2 receipts bind the loader to the *same* sha256, and
`verify_hash_bindings.py:105-107` dedupes on `(path, expected_hash)`, so the second binding is
collapsed and only one receipt is named. The five-binding table above is still the correct
re-issue list; the verifier's line count is not. Do not go hunting for a fifth line.

**Three receipts must be re-issued on 08-03, and both re-issues are now scheduled** — say so in
your commit message rather than flagging anything as missing:

- The two **Gate-2** freezes (`g2-gate2-construction-20260719.json` and
  `G2_GATE2_TARGET_RUNTIME_RECEIPT.json`) — `RESTORE-2026-08-03.md` **Step 2** already schedules
  a Gate-2 re-issue for the separate MeV/GeV units question, so B1 rides along on it.
- The **Gate-4** launch-code gate — `RESTORE-2026-08-03.md` **Step 2b**, added at `25e72f0`.
  *(An earlier version of this brief said no step owned this and told you to flag it. That is
  now wrong; do not flag it.)*

**Read Step 2b before you write §2d.** It is not just scheduling — it fixes the shape of your
patch in three ways: (i) the Gate-4 receipt binds **five** files, so editing the driver or the
validator voids all five, which is why the brief tells you to prefer new test files; (ii) the
re-issue is the moment three audit findings get folded in at zero marginal cost — binding
`omnifold/net.py` + `omnifold/omnifold.py` (B-1), binding and finally running
`stress_closure_muon.py` (B-6), and resolving B-2's dangling independence citation; (iii) it
carries the same expected-red table as above, so the two documents must not drift. If your patch
makes any of Step 2b's statements wrong, update Step 2b in the same commit.

None of those re-issues are yours to perform — they need `/pscratch`. Your job is to leave the
patch in a state where 08-03 can perform them.

**[EXEC]** What the verifier genuinely cannot see is an edit to `omnifold_nn/omnifold/net.py`
or `omnifold_nn/omnifold/omnifold.py` — they appear in no receipt at all (audit B-1). That is
a second reason §2a routes through the existing `normalization_factor` argument rather than
the vendored engine. **[EXEC]** `omnifold_nn/omnifold/dataloader.py` **is** bound and **is**
checked — do not edit it.

The verifier prints only the summary, known drift, and mismatches; it never names an OK
binding. **Grepping its stdout for a filename tells you nothing in either direction.** Settle
coverage from the receipt JSONs. This exact inference error produced a false finding on
2026-07-29; §9 of the audit doc records it.

## Other constraints

**Do not measure `R`, and do not freeze a numeric `R`.** Per §2b its denominator depends on
unresolved finding **B-4** (the reco leg uses `w_truth`; the contract carries an unused
`w_reco`). Compute `R` in **one named function**, with the `w_truth`-vs-`w_reco` assumption
stated at the definition, and record at runtime whether `w_reco == w_truth` in the loaded
dump. Then 08-03's first run answers B-4 as a side effect, and if the answer flips, one
function body changes instead of a search through the patch.

**On the independence this implies** — deliverable (b) and the "one named function" rule are
not in conflict, and the distinction matters:

- Share the **formula**. One named function, called by both the loader and the Gate-2
  validator, so the B-4 flip is a one-body change.
- Keep the **inputs** independent. The validator loads the G2 dump and derives its own sums,
  rather than consuming sums the loader or driver reported. **Independence of data, not
  duplication of arithmetic.**

**[EXEC]** Suite baseline is exactly **7 failed / 333 passed / 1 skipped** (6.12 s).
**[READ]** all seven come from the `/pscratch` literal `REPO = Path(...)` at
`gate2_target_runtime.py:35`, surfacing via `die()` at `:56`.

An unchanged baseline proves only that you broke nothing. **[RELAY, audit §4]** mutating
`niter 2→1`, `train_events 2M→1000`, `epochs 8→99`, and the Gate-4 grid to garbage all
reportedly left it at 7/333/1. **Your two new tests are the only real signal** — do not treat
the baseline as a box to tick.

Commit locally with a substantive message. Do not push. No jobs, no GPU, no `sbatch`.

## Verify, don't relay — with a target list

The spec has been corrected three times and both prior sessions were wrong in both directions.
Spend your verification budget on every **[RELAY]** above and on any `file:line` you actually
depend on. You need not re-derive the **[EXEC]** items unless something looks off. If the spec
is wrong, fix the spec first and say so — that has happened three times already and is the
expected outcome, not a failure.

## Delegates

**[EXEC]** These home directories exist: `~/.codex-personal`, `~/.codex-school`,
`~/.claude-school`. `~/codex-homes` does **not** — that is what `agentctl.py`'s codex profiles
expect, so route codex directly, not through agentctl.

**[EXEC-OTHER]** The invocation forms below are reported to have been run on 2026-07-29, all
three returning substantial reports — but by a *different* session, not the one that wrote this
brief, which verified only that the three home directories exist. **Someone else's [EXEC] is
your [RELAY].** Expect them to work; do not be surprised if a flag has drifted. This distinction
is the point of the tagging scheme, and it is the one place in this brief where it was
originally elided.

```bash
env CODEX_HOME="$HOME/.codex-personal" codex exec -c model_reasoning_effort="high" \
    --sandbox read-only --skip-git-repo-check -C <repo> "$(cat prompt.md)" < /dev/null
# same form with ~/.codex-school

env CLAUDE_CONFIG_DIR="$HOME/.claude-school" claude -p "$(cat prompt.md)" \
    --model opus --allowedTools "Read,Grep,Glob,Bash"
```

Always append `< /dev/null` to `codex exec` — without a closed stdin it hangs silently rather
than erroring. Prefer `--sandbox read-only` for codex: it makes READ-ONLY an enforced property
rather than a request.

**[RELAY, audit §6]** agy (Gemini, via agentctl) works but was the weakest lane in the last
audit — it reproduced a known stale-brief error and misnamed a binding receipt. Do not use it
alone.

Brief every referee READ-ONLY, tell it to default to REFUTED, and verify what it returns
rather than adopting it. **Give referees this file's path rather than pasting its contents** —
see the note at the top.
