# Bounded repair of the Valencia feasibility study

**Status:** plan frozen before any repair computation. Results are appended below the freeze line.

**Object:** branch `study/valencia-feasibility-20261011`, reviewed head `d75987e17cfd5a3635f027a902d8545c70107fce`.

**Authorization:** Joseph, 2026-10-11. This is a bounded repair, not a reopened physics campaign.
- 300 aggregate CPU-s for all tests and numerical checks, including failures and review.
- Zero production compute, and no new events, fits, unfolding, detector work, adoption or contact.
- The old campaign allowance is not reused.
- The original ledger `logs/budget_ledger.jsonl` and the frozen criteria in `PLAN.md` are preserved
  unchanged.
- Commit on this branch; do not merge or push.

**Roles:**
- **Owner:** this Claude lane.
- **Scientific decision:** Joseph.
- **Review:** one fresh, read-only, targeted reviewer subagent, then one correction pass, then stop.

**Decision answered:** do the study's results, cost claims and verdict survive the two named defects?
- The VA sign was chosen from the sign of the integrated interference.
- The launcher's `ulimit -t` is not an aggregate process-tree cap.

**Terminal conditions:** the correction pass is committed, or the next metered step would exceed
300 CPU-s.

**Metering:**
- Every check runs through `code/repair_meter.py`, which writes to `logs/repair_ledger.jsonl` with a
  cap of 300 CPU-s.
- It reserves before launch, under a lock. A reservation that is never settled stays charged in full.
- It charges the measured user+sys CPU of all waited descendants.
- A process orphaned on purpose is charged at its certified bound.
- The reviewer's checks go through the same meter.

## 1. VA-interference convention

**Primary-source conventions.** Nieves, Ruiz Simo and Vicente Vacas 2011 (arXiv:1102.2777, TeX
`paper.v10.tex`) define:
- `eq:sec` (TeX line 227): dσ/dΩdE′ = (|k′|/|k|) G²/4π² L_{μσ} W^{μσ}.
- Footnote to `eq:lep` (line 241): ε_{0123} = +1 and g = (+,−,−,−).
- `eq:lep` (lines 244–247): L_{μσ} = k′_μ k_σ + k′_σ k_μ − g_{μσ} k·k′ + i ε_{μσαβ} k′^α k^β.
- `eq:wmunu` (lines 260–264): W^{μσ} ∝ Σ ⟨f|j^μ|i⟩⟨f|j^σ|i⟩*.
- The unlabelled hadronic-current equation (lines 273–276): j^μ = Ψ̄_u γ^μ(1−γ₅)(cos θ_C Ψ_d + …).
- W^{μσ} = W_s^{μσ} + i W_a^{μσ}, with real symmetric and antisymmetric parts (lines 281–285).
- `sec:anti` (lines 1639–1651): ν̄ is obtained by changing the sign of L^a.

Sobczyk, Nieves and Sánchez 2020 (PRC 102, 024601; arXiv TeX `revisited2p2h.tex`) repeat `eq:sec` and `eq:lep` with the same footnote (lines 140–155).

**Consequence.** L_{μσ}W^{μσ} = L^s_{μσ}W_s^{μσ} − L^a_{μσ}W_a^{μσ}. With q along +z, the only
antisymmetric component is W_a^{12} = −W_a^{21}, and L^a_{12} = ±(E|q| − ω k_z). The interference term
is therefore ∓2(E|q| − ω k_z) W_a^{12}, with the upper sign for ν.

**Table encoding.** The table column "W12" has to be mapped to W_a^{12} (= Im W^{12}).
- No author-documented definition was found in the papers above.
- NuWro, which distributes the tables, uses w3 = (1−2·ap) W12/|q| with −w3(E+E′) sin²(θ/2).
- Check C6 tests whether NuWro's reading is W12 = Im W^{12}.
- **Frozen status rule:** unless an author-documented definition is found, the encoding is recorded as
  *distributor-corroborated, not author-confirmed*. B1 and B2 are then labelled **UNVALIDATED
  (table W12 encoding)**. The numerical deviation is still reported against the frozen PLAN.md
  tolerances, but no PASS or QUALIFIED word is attached to them.
- The integrated sign of the data is never used to choose the convention.

**Checks** (tolerances frozen):

| id | Check | Tolerance |
|---|---|---|
| C1 | L_{μσ} from `eq:lep` equals Tr[(k̸′+m)γ_μ(1−γ₅)k̸γ_σ(1−γ₅)]/8 (ν), and the ν̄ trace Tr[k̸γ_μ(1−γ₅)(k̸′−m)γ_σ(1−γ₅)]/8 equals `eq:lep` with L^a reversed. The trace uses explicit Dirac matrices with γ₅ = iγ⁰γ¹γ²γ³; checked at 200 random kinematic points. | max abs deviation ≤ 1e-9 × max\|L\| |
| C2 | `lepton_contraction` (code) equals the full complex 4×4 sum L_{μσ}W^{μσ} built from the C1 trace, with W^{12} = i·W12 and W^{21} = −i·W12. Random tensor inputs at 200 points, both beams. The imaginary part of the sum vanishes. | rel. ≤ 1e-9 |
| C3 | Beam reversal at identical E, ω, \|q\| and tensor input: the symmetric part is unchanged and the interference flips. No nuclear energy shift is involved. | ≤ 1e-12 rel. |
| C4 | W12 = 0: ν equals ν̄ at identical inputs (`lepton_contraction`, and `sigma` with a forced common shift). | ≤ 1e-12 rel. |
| C5 | W12 → −W12 in the tables: σ_ν − S reverses sign exactly, where S is the W12 = 0 value, with no compensation. A source scan shows no remaining data-dependent sign selection. | ≤ 1e-9 rel.; scan empty |
| C6 | NuWro's transcribed expression (`nuwro_formula_contraction`), with only W12 nonzero, equals the code's interference term for ν and ν̄. | ≤ 1e-9 rel. |
| C7 | The fixed-convention integrator, rerun on the committed 1 GeV n_sub = 8 configurations, compared with the committed values. | report any change; ≤ 1e-12 rel. means "unchanged" |

Physical neutrino/antineutrino differences (the energy shift B, the published values) enter only C7
and the B1/B2 status. They do not enter C1–C6.

## 2. Launcher aggregate bound

**Implementation.** `code/pilot_run.py` is repaired as follows.
- **Reservation:** it reserves durably under `flock` before launch.
- **Unsettled reservations** count in full.
- **Interruption** settles at the full reservation.
- **Unreadable ledgers** stop every launch.
- **Execution mode:** one mode is supported, a single process. Forking is denied with `sandbox-exec`,
  so `ulimit -t` bounds the whole job, even after the launcher dies. A preflight probe must show that
  the fork is denied.
- **Other modes** are refused.

**Checks** (`tests/test_pilot_run.py`, using temporary ledgers and lowered caps; never NuWro, never
the campaign ledger):

| id | Check | Pass condition |
|---|---|---|
| L1 | Concurrency: 8 launchers start simultaneously against a cap that admits 3 reservations | exactly 3 run; the totals never exceed the cap |
| L2 | Crash after reservation (launcher SIGKILLed mid-job) | the reservation stays charged in full; the next request is refused when it would exceed the cap counting it |
| L3 | Interruption (SIGTERM to the launcher) | the job is killed; the settlement is at the full reservation |
| L4 | Child-process workload (a shell that forks; Python `subprocess`) | the fork is denied, and the job fails inside its reservation |
| L5 | CPU spinner, including one that ignores SIGXCPU, under `ulimit -t 1` | killed; measured CPU ≤ reserved (1 + margin); the overshoot is recorded |
| L6 | Fail-closed ledger: truncated line, unknown kind, orphan settlement | every launch refused |
| L7 | Caps can only be lowered (`--cpu-cap 1e9` does not raise 36,000) | enforced |
| L8 | Legacy ledger compatibility: the original campaign ledger read, without being modified, gives its recorded totals | totals equal; file hash unchanged |
| L9 | Orphan bound: after its launcher is SIGKILLed, the sandboxed spinner still stops at its own RLIMIT | stops; charged at its certified bound |

## 3. Claims to update

The following are updated only where the defects affect them:
- REPORT §1, §2, §4, §6, §9 and §11;
- REVIEW (a repair section);
- cost wording: extrapolated runtime versus a certified per-run bound.

Results already in the repository are reused, with no new events.

---

## Results (appended after the freeze)

### R1. VA convention (checks C1–C7: all pass)

Source: `results/repair/va_convention_checks.json`, from `tests/check_va_convention.py`; latest run
`C-va-convention-3`.

| id | Measured | Tolerance | Result |
|---|---|---|---|
| C1 | trace vs `eq:lep`: max dev / max\|L\| = 4.1×10⁻¹⁶ (both beams, 200 points, E 0.3–20 GeV) | ≤ 1e-9 | pass |
| C2 | code vs full complex contraction: max rel 9.9×10⁻¹²; imaginary part 0 | ≤ 1e-9 | pass |
| C3 | beam reversal at identical inputs: symmetric part identical (0); interference sum 0 | ≤ 1e-12 | pass |
| C4 | W12 = 0, common shift 15 MeV: σ_ν − σ_ν̄ = 0 | ≤ 1e-12 | pass |
| C5 | W12 → −W12: interference +4.013×10⁻⁴⁰ → −4.013×10⁻⁴⁰ cm² (rel 4×10⁻¹⁶); source scan of `valencia_tensor_xsec.py` for data-dependent sign selection: no hits | ≤ 1e-9; empty | pass |
| C6 | NuWro's transcribed expression, W12 only: max rel 1.2×10⁻¹⁴ for ν and ν̄ | ≤ 1e-9 | pass |
| C7 | committed 1 GeV n_sub = 8 totals recomputed: ν +2.2×10⁻¹⁶, ν̄ +6.7×10⁻¹⁶ | ≤ 1e-12 = unchanged | unchanged |

**What this establishes:**
- The integrator's contraction is exactly the authors' `eq:sec`/`eq:lep` convention with W = W_s + iW_a.
- `eq:lep` itself agrees with the V−A Dirac trace for the index order of `eq:wmunu`.
- The interference reverses with W12 and with the beam, with no compensation.
- NuWro reads W12 the same way.
- The old data-driven rule happened to select this same sign (−1 on the raw term, recorded in all
  four committed integrator JSONs), so no committed number changes.

**What it does not establish:** the authors never state that the tabulated W12 is Im W^{12}. Support
found by the review:
- the authors' 2004 paper defines W₃ = −i W^{xy}/|q| with the same ε₀₁₂₃ = +1, and gives the
  −W₃(E+E′) sin²(θ/2) cross-section term (Nieves, Amaro and Valverde, PRC 70, 055503, TeX lines
  279–312; checked by the owner). NuWro's expression is that formula with w3 = W12/|q|, so C6 is in
  effect a check against the authors' own formula, given W12 = Im W^{xy};
- GENIE independently reads the authors' 2015 tables' fourth column as `ImWxy`.

Neither is an author definition of the table column. Following
the frozen status rule, B1 and B2 are now **UNVALIDATED (table W12 encoding not author-confirmed)**.
- Their deviations are unchanged: −5.5% and +16.3%.
- The superseded grades are kept in `results/benchmarks.json`.
- B3 and B4 compare two implementations with the same reading (C6), so they stand.
- The flux-fold and convention-sensitivity outputs were not rerun by the owner. Those scripts
  discarded the selected sign without recording it. The reviewer then measured the 36-point flux fold
  (`results/integrator-C12-nu-fluxfold.json`, n_sub = 4):
  - the fixed code reproduces every committed σ(E) to within 4.4×10⁻¹⁶;
  - the interference is positive at all 36 energies (150 MeV–100 GeV), so the old rule selected −1
    there too (`results/repair/review/va_extra.json`).

  The 72-point n_sub = 8 fold and the B = 0 / 27.41 MeV sensitivity runs remain unverified. The same
  sign is expected.

**Free-nucleon check (the reviewer's, not frozen).** For n → p, a nucleon at rest and a pure V−A trace,
with no table involved:
- Im W¹² = −M|q| < 0;
- the code's contraction equals the full trace contraction;
- σ_ν > σ_ν̄ at three kinematic points.

So the fixed convention gives constructive neutrino interference from first principles.

**Isospin assumption.** `sec:anti` also says the W⁻N → N′π amplitudes are to be used for ν̄. The tables,
like NuWro, reuse one tensor for both beams, an isospin assumption for N = Z nuclei that the authors do
not state. It is now named in the module docstring.

**C5's power.** C5's source scan is a literal pattern over one file and has little power. The numerical
W12 → −W12 reversal is the real guard: it would fail under the old rule. The review found no remaining
data-dependent sign selection anywhere in `code/`.

**Descriptive only** (never used to choose the convention): the fraction of nonzero W12 cells that are
negative is pp 1.00, np 0.65, pn 1.00, 3p3h 1.00.

**Diagnostics adapted, not rerun.** `algebra_check*.py` hard-coded the old raw-term sign −1 for ν. They
now call the new signature through a one-line shim that preserves their arithmetic. Their committed
logs (D1–D4) came from the `d75987e1` code.

### R2. Launcher (checks L1–L9 and L9b: all pass, after one design change)

Source: `results/repair/launcher_checks.json`, from `tests/test_pilot_run.py`; latest run
`L-launcher-2`.

**Design change after the freeze.** The plan assumed that, once forking is denied, `ulimit -t` bounds
the job even after the launcher dies. The first test run (`L-launcher-1`) and probe P1 falsified that.
- On this macOS, a process that ignores SIGXCPU is **not** stopped by RLIMIT_CPU, neither with soft =
  hard = 1 s nor with soft 1 s / hard 2 s. Both probe processes ran until the 8 s wall timeout.
- The launcher therefore gained a watchdog (layer 1): it polls the job's CPU with `ps`, includes its
  own measured child CPU, and SIGKILLs at the allotment.
- RLIMIT_CPU stays as layer 2.
- A `start` record names the job, and later launches are refused while that job lives.
- The reservation is N + `WATCHDOG_MARGIN_S` = N + 1.5 s on 10 cores. That is an engineering margin,
  not a derived bound. The measured overshoot was 0.02–0.03 s for single-threaded spinners, and 0.25 s
  for one 10-thread job ignoring SIGXCPU (reviewer probe).
- L9b was added to measure the residual.

**Harness defect found in the first run.** `pgrep -f <marker>` matched the launcher's own argv, which
contains the marker. That invalidated L3 and L9 in run 1, and L9's apparent pass there. Jobs are now
identified as direct children of the launcher (`pgrep -P`). L4 `sh_fork` was also invalid, because
`sh -c` exec'd its single command without forking; it now forces a fork.

| id | Result (run `L-launcher-2`) |
|---|---|
| L1 | 8 simultaneous launchers, cap for 3: 3 ran, 5 refused (rc 3), 3 reserve records; charged total never above the cap (7.5 of 8.5) after any append. **Power control:** with a 0.3 s delay between reading totals and appending, the locked `reserve()` admitted 3 of 8. The same harness without the lock admitted **8 of 8**, charging 16.0 against a cap of 6.5. |
| L2 | Launcher SIGKILLed mid-job: the reservation stays charged (2.5 s). (a) While the orphaned job lives, even a request inside the cap is refused, naming the job pid. (b) After the job exits, the unsettled reservation still counts in full and the next request is refused on the cap. |
| L3 | SIGTERM to the launcher: rc 130; the job is killed; settled at the full reservation (2.5 s). |
| L4 | `sh` fork, `bash` background job, Python `subprocess`, `os.posix_spawn`, `os.fork`: all denied ("Operation not permitted"); no marker file created; each settled ≤ 0.05 s. **Positive control:** all five create their marker outside the sandbox. |
| L5 | 1 s spinner: killed by the watchdog at 1.016 s. Spinner ignoring SIGXCPU: killed by the watchdog at 1.021 s. Both ≤ 2.5 s reserved. |
| L6 | Truncated line, unknown kind, orphan settlement, duplicate reservation: every launch refused; ledger byte-identical. |
| L7 | `--cpu-cap 1e9` / `--event-cap 1e9` do not raise 36,000 / 10,000. |
| L8 | The original campaign ledger reads as 242.875 CPU-s and 7,900 events, with no unsettled reservations. SHA-256 `b22d4d78…` is unchanged and no lock file was created. |
| L9 | Orphan with default SIGXCPU action: stopped by the kernel at 0.96 s of observed CPU; a new launch was refused while it lived. |
| L9b | Orphan ignoring SIGXCPU: **still running at the 3 s timeout** (3.07 s CPU, above its 2.5 s reservation). This confirms the residual. A new launch was refused while it lived; the test then killed it. |

**Scope.** The sandbox denies fork, vfork and posix_spawn by the job itself. Processes that launchd, XPC
or other system services start on the job's behalf are outside the bound; this is not tested and not
relevant to NuWro.

**Remaining residual (not certified).** If the launcher dies and its job ignores, catches or blocks
SIGXCPU, that orphaned job has no CPU bound. Its reservation stays charged and no new launch proceeds
while it lives, but its own consumption is unbounded until a person kills it. Whether NuWro and ROOT
leave SIGXCPU at its default action, or run at all with forking denied, was not executed: zero
production compute was authorized. Static evidence covers only the executable: its only process-creating
import is `popen`, reached only from NIWG plotting code. The ROOT libraries it links can create
processes (`libCore`: popen and system; `libCling`: fork, execv, posix_spawn; `libMultiProc`: fork).
Under the sandbox, NuWro may therefore fail closed.

### R3. Metering

- **Ledger:** `logs/repair_ledger.jsonl`. Each check's log is under `logs/repair/`.
- **Coverage:** the meter charges the measured CPU of all waited descendants, plus declared extra
  charges for processes a check orphans on purpose.
- **Undercount found and corrected:** the failed run `L-launcher-1` orphaned its SIGXCPU-ignoring
  spinner when its cleanup killed the launcher. That CPU was unmeasured, at most 15 s by the test's
  wall timeout. It is charged as `X-correction-…` (16 s).
- **Probe P1** is `tests/probe_rlimit_sigxcpu.py` (run from a scratch copy; the content is identical).
- **Backstop:** the meter enforces its 300 s cap at admission only. A settlement may exceed its
  reservation, and its per-process `ulimit -t` is subject to the macOS SIGXCPU limitation.
  - The convention checks and the grade/cost run do not touch SIGXCPU, so RLIMIT bounded them.
  - The launcher tests were bounded by their wall-clock timeouts and the watchdog.
- **Correction charge:** the 15 s bound for the run-1 orphan rests on the run-1 cleanup having killed
  every process that matched `while True: pass`. The run-1 test source was not committed and its
  JSON was overwritten, so this cannot be re-checked. No such process was alive when checked during
  the correction pass.

Totals before review: 77.3 of 300 CPU-s, zero events, no NuWro execution, campaign ledger untouched.

### R4. Review and correction pass

**Review.** One fresh, read-only, targeted reviewer subagent examined `fedcc918` in a detached worktree.
- It ran 27.05 CPU-s through the meter, against a copy of the repair ledger in which 162.7 s was held
  for this pass. Its records are merged into `logs/repair_ledger.jsonl` (`REV2-*`).
- Its outputs are in `results/repair/review/`.
- It reproduced L1–L9b and the committed integrator numbers.
- The worktree stayed clean.
- **Verdict:** no blocker; the convention is fixed and correctly derived; the launcher meets the
  requirement, with the residual stated correctly; INCONCLUSIVE unchanged.

| # | Severity | Finding | Disposition |
|---|---|---|---|
| 1 | MAJOR | REPORT §9 still said "B2 is QUALIFIED". | **Fixed.** |
| 2 | MINOR | "Flux-fold sign was −1" was asserted without a check. | **Fixed.** The text now cites the reviewer's 36-point measurement; the 72-point fold and the sensitivity runs are labelled unverified. |
| 3 | MINOR | "NuWro creates no child process" covers only the executable; the linked ROOT libraries can fork. | **Fixed** in REPORT §2 and §9 and in R2. The charged CPU stands because waited children are counted. |
| 4 | MINOR | The watchdog margin was asserted, not derived. | **Fixed.** It is labelled an engineering margin, with the measured overshoots. |
| 5 | MINOR | The meter's own bound was misdescribed. | **Fixed** (R3). |
| 6 | MINOR | The encoding is better supported than stated: the authors' 2004 W₃ = −iW^{xy}/\|q\|, and GENIE's `ImWxy`. | **Fixed.** Both are cited in R1, REPORT §1, §4 and §9, and the docstring; the owner checked the 2004 TeX lines 279–312. The label is now "generator-corroborated" (the frozen plan text above says "distributor-corroborated"). The status stays UNVALIDATED. |
| 7 | MINOR | The `sec:anti` paraphrase dropped the W⁻ amplitudes clause, leaving an isospin assumption unstated. | **Fixed** (docstring, R1). |
| 8 | MINOR | Start-record gap; `proc is None` on an interrupted `Popen`. | **Fixed.** SIGINT/TERM/HUP are blocked from before `Popen` until the `start` record, so a pending signal lands with `proc` set. The child unblocks them before exec (L10: the job's mask is empty). A SIGKILL inside the window remains, documented. |
| 9 | MINOR | `job_alive` failed open when `ps` printed nothing. | **Fixed.** It uses `os.kill(pid, 0)`; it reports dead only for a missing pid or a different start time (L10). |
| 10 | MINOR | "Cannot create children" was unscoped (launchd/XPC). | **Fixed** (docstring, R2). |
| 11 | MINOR | Stale wording: CATALOG "measured to be cheap"; REPORT §2/§11 omitted the residual; REVIEW had no repair section. | **Fixed.** |
| 12 | MINOR | The X-correction cannot be re-checked. | **Documented** (R3). It cannot be fixed after the fact. |
| 13 | NIT | An RLIMIT-killed job was settled as "completed". | **Fixed.** The status is "killed by signal N" when rc < 0. |
| 14 | NIT | The cap was printed with `.0f`. | **Fixed** (`.3f`). |
| 15 | NIT | `fsync` is not durable on macOS. | **Fixed.** It uses `F_FULLFSYNC` where available. |
| 16 | NIT | The C5 scan has little power. | **Documented** (R1). |
| 17 | NIT | A stale comment in `algebra_check_components.py`. | **Fixed.** |

**Reruns after the fixes:**
- `L-launcher-3-correction`: L1–L9b and the new L10 all pass; L5 overshoots 0.028 and 0.025 s.
- `C-va-convention-4-correction`: C1–C7 all pass; the encoding label is updated.
- No numerical result changed.

**Remaining issues** (not fixed in this bounded repair):
- **Table encoding.** The W12 encoding is not author-confirmed, so B1 and B2 stay UNVALIDATED. Only the
  authors can resolve it (REPORT §8 item 2).
- **Orphan residual.** A launcher crash with a job that ignores SIGXCPU leaves that job unbounded, and
  a SIGKILL between `Popen` and the `start` record leaves no live-orphan refusal.
- **NuWro untested in the new launcher.** NuWro's compatibility with the fork-denying sandbox and its
  SIGXCPU disposition were never executed.
- **Unverified reruns.** The 72-point flux fold and the sensitivity runs were not rerun.
- **Margin.** The watchdog margin is empirical.

**Verdict change: none.** INCONCLUSIVE, blocked on the authors' corrected tables and conventions.


**Final repair accounting** (all of `logs/repair_ledger.jsonl`, no unsettled reservations): 127.8 of
300 CPU-s.

| Part | CPU-s |
|---|---:|
| Owner checks, probes and correction charges before review | 77.3 |
| Review | 27.05 |
| Correction-pass reruns | 23.4 |

There were zero events and no NuWro execution, and `logs/budget_ledger.jsonl` is unchanged (SHA-256
`b22d4d78…`). The branch is not merged or pushed.

### R5. Closeout record (CAMPAIGN-REVIEW-20260929 §1 and §6.7)

The campaign review was read in full during closeout. It is unchanged between this branch's base
`3892e769` and remote main `d81f532b`.

**Owner:** Claude Opus 5.5 (`claude-opus-5-5`), session `c89a62fc-4a1b-4827-a04d-d76daccaa218`, the
same session that ran the original pilot.

**Reviewer:** one fresh general-purpose Claude subagent of the same model, read-only, on fixed commit
`fedcc918`. The review recommends an Astra High reviewer for consequential code review. None was
available in this environment. Review independence is therefore limited to a fresh context and a
frozen object; this is not cross-model or domain-expert review.

**Budget:** one review and one correction pass, as authorized. The pass did not re-open review, so the
review-loop failure mode of §4 does not apply.

**Commits:**
- input `d75987e1`;
- outputs `89254dd5` (frozen plan), `fedcc918` (pre-review) and `288c5c97` (correction pass), plus
  this record.

**Compute:** 127.8 of 300 CPU-s on one Apple M1 Pro; zero events; no GPU. Inference cost is not
available.

**Consequential findings accepted:**
- *the repair's own tests:* macOS RLIMIT_CPU does not stop a process that ignores SIGXCPU; a harness
  `pgrep` matched the launcher's own command line;
- *the reviewer:* the stale B2 grade, the start-record window, fail-open liveness, and support for
  the W12 encoding from the authors' 2004 paper.

**Residual defects and decision:** the residual defects are as in R4. The decision resolved: both named
defects are repaired without changing any committed number, and the verdict stays INCONCLUSIVE.

**Baseline divergence (measured at closeout):**
- The branch is 6 commits ahead of and 16 behind remote main `d81f532b`, from merge base `3892e769`.
- Main's 16 commits change 30 paths (paper and note). None is under this study directory, CATALOG.md
  or the MANIFEST files.
- `git merge-tree` reports no textual conflict. `MANIFEST.tsv` would still need regenerating at any
  integration, because main added documents.
- This branch is not merged or rebased; integration is Joseph's decision.
