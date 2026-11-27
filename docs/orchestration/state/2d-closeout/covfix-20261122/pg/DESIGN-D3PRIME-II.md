# D3′(ii) on gevgen's flux path: a proposed replacement (for the director, then Joseph, rev 12)

Status: PROPOSAL. No code has changed. Evidence: B3 run 4's receipt (`install/pg-replay-g2111a.py.out`, 3c88ff0e) and
two read-only diagnostics, `install/b3-diag/b3-run4-diag.out` (1293dd12) and `b3-run4-diag2.out` (1b82fcc7). GENIE
lines are R-3_04_00 (GENIE-MC/Generator on GitHub). The local copies of GEVGDriver.cxx and GMCJDriver.cxx compare
byte-equal to the tag, and gEvGen.cxx is ff7bce18.

## 1. What run 4 showed

Slot 1's coverage run exited 0 and passed its trace check. `coverage-log` then failed with `coverage-none: the log
names no spline needed`, plus two `coverage-pair` problems that follow from it. The director has classed this as a
design false STOP (class c): it fires on every correct flux-mode run.

- D3′(ii)'s three markers are printed only in `GEVGDriver::CreateSplines` (GEVGDriver.cxx:646, :652, :656).
- In flux mode, gevgen reaches `CreateSplines` only through `GMCJDriver::BootstrapXSecSplines` (GMCJDriver.cxx:622).
  That function returns at once unless `GMCJDriver::fUseSplines` is set (:606).
- F1's argv selects flux mode with `-f flux,flux_numu,NOWIDTH`. In that mode gevgen calls `mcj_driver->Configure()`
  before `mcj_driver->UseSplines()` (gEvGen.cxx:360-361). So the flag is unset during `Configure`, and the markers
  never print, at any messenger level.

## 2. What GENIE does log on the flux path, and at what level

Corrected after the independent read (§6). The pinned coverage messenger raises only `GEVGDriver`, from WARN
(Messenger_laconic.xml:89) to DEBUG. `XSecSplLst` stays at WARN (:201).

Each LOG message is one record. Its prefix (layout, priority, stream, and `[n] <file::Function (line)> : `) sits on
the first physical line, and each `\n` in the message starts a new line (Messenger.h:84-99, Messenger.cxx:61-76). The
records go to stdout, and run_gevgen_v3.sh merges stderr into the same gevgen.log (run_gevgen_v3.sh:96-108).

| where | stream, priority | text | meaning |
|---|---|---|---|
| `UseSplines`, GEVGDriver.cxx:566-570, from `PopulateEventGenDriverPool` (GMCJDriver.cxx:590), each (nu, target) | GEVGDriver WARN | `*** At least a spline (algorithm: A, interaction: X doesn't exist. Reverting back to not using splines` (the parenthesis is never closed) | a needed key is missing; that driver's `fUseSplines` becomes false |
| `CreateXSecSumSpline`, :449-451, from `BootstrapXSecSplineSummation` (GMCJDriver.cxx:661, unconditional) | GEVGDriver INFO | `Creating spline (sum-xsec = f(logE)) in E = [min, max] using 100 knots` | one per driver. It names no pair; the records after it do. 100 is `fXSecSplineNbins` (GMCJDriver.cxx:467) |
| same, :453-455 | GEVGDriver FATAL | `You haven't loaded any splines!! ` | that driver's `fUseSplines` is false. The asserts are compiled out, so the run goes on |
| `XSecSum`, :378 | GEVGDriver DEBUG | `Computing the cross section sum` | opens each knot's block |
| `XSecSum`, :398-399 | GEVGDriver DEBUG | `Compute cross section for interaction: ` then X | per interaction per knot |
| `XSecSplineList::SplineExists`, XSecSplineList.cxx:103-104, 115-116 | XSecSplLst DEBUG (not raised today) | `Checking for spline: K in tune: T`, then `Spline found?....Y` or `N` | per lookup, with the full key K (algorithm, config and X) and the tune |
| `XSecSum`, :419-423 | GEVGDriver DEBUG | `Interaction   = X`, then `Cross Section *interpolated* = s cm2` or `*computed*` | per interaction per knot. **The label is the driver-wide flag (:421). It is not this lookup's branch (:408-413):** a lookup that missed while the flag stayed true would integrate and still print `*interpolated*` |
| `XSecSum`, :429-434 | GEVGDriver INFO | `SumXSec(<probe>+<target>->X, E = e GeV)*interpolated* = s cm2` (no space after `)`) | closes each knot's block; PDG names |
| `CreateSplines`, :646, :652, :656 | INFO, DEBUG, DEBUG | `Need xsec spline for `, `The spline wasn't loaded at initialization…`, `Spline was found` | unreachable on this path (§1) |

**The asserts are compiled out in the pinned build.** `libGFwEG-3.04.00.so` (pin 17a907b1, matched) holds neither
GEVGDriver.cxx:457's expression string `Emin<Emax && Emin>0 && nk>2` nor any `__assert_fail` import (0 and 0,
b3-run4-diag2.out §2). `fUseSplines` occurs 4 times through ordinary code and symbols, so it decides nothing. The Make
files don't set NDEBUG: `GOPT_WITH_CXX_DEBUG_FLAG=` is empty (Make.config:36), and CXXFLAGS take `$(ENV_CXXFLAGS)`
from the build environment (Make.include:587). So with a missing spline, gevgen **can** go on, integrating, and exit
0. **A coverage run's rc 0 is therefore no evidence that every spline was found.** (This corrects my run-4 reading,
which leaned on the assert. Run 4's rc 0 shows nothing either way: its log is gone.)
<!-- absence-ok: an inference about what a coverage run's exit status shows, from GENIE's source and the pinned binary; not a claim that a result or study is absent -->

## 3. Proposed replacement for D3′(ii)'s log rule

The coverage run stays one event, with the public seed and `argv-check`'s argv. `coverage_problems` changes. The log is
read as a stream and hashed over its raw bytes, the same bytes deleted.json hashes. Records are parsed whole,
prefix line included, and a payload line that is not inside its own record counts as damage.

**Scope.** These rules certify the bootstrap: the per-driver sum splines that GMCJDriver builds in `Configure`. Event
time (interaction selection by `PhysInteractionSelector`) is not in the staged sources, and the log does not certify
it.

**Option A, the stronger one (recommended): raise XSecSplLst to DEBUG as well.** The messenger replaces two pinned
lines instead of one (:89 and :201), and its pin MESSENGER_SHA256 moves. Then:

- **P1, positive, per lookup.** For each (nu, target) of F1's argv, the log has exactly 100 complete knot blocks. A
  block runs from `Computing the cross section sum` to its `SumXSec(…)*interpolated*` line. In each block, every
  interaction of that pair's driver has, in order: `Checking for spline: K in tune: T`, then `Spline found?....Y`, then
  the `Interaction   = X` / `Cross Section *interpolated* = ` record. K must be a full key of the reduced spline file
  (tune, algorithm, config and X), T must be the run's tune, and K's interaction part must equal X. Every block of a
  pair has the same set of X. A pair is the `nu:`/`tgt:` fields of X, parsed as fields so that an optional `N:` does
  not matter.
- **P2.** No `*computed*` record, no `SumXSec(…)*computed*` line, no `Spline found?....N` inside a block.
- **P3.** The X set for each pair equals the reduced spline's codes for that pair (`spline_codes`). Today's rule only
  required that X be among them.
- **P4.** Exactly two `Creating spline (sum-xsec = f(logE))` records. Each is bound to its pair by the blocks that
  follow it, and no pair has two.
- **P5, backup absences.** These print at WARN or FATAL under any messenger: `Reverting back to not using splines`,
  `You haven't loaded any splines`, and `CreateSplines`' three markers (§2, last row). Any of them is a STOP.

**Option B, the messenger unchanged.** The same rules without the `Checking for spline` and `Spline found?` lines.
P1 then rests on the driver-wide label. That is weaker in two ways (§2): a later lookup miss with the flag still true
would read as `*interpolated*`, and nothing binds X to the algorithm and config that the key holds, so P3 can match a
spline of another config with the same X. The staged bootstrap code shows neither the interaction list nor the spline
list changing between `UseSplines` and `XSecSum`, so B covers the ordinary case only.

Either option fails closed on a messenger that is ignored or misconfigured: P1's lines are DEBUG and would be absent.

**Cost, to be measured.** At least four physical lines per interaction per knot, six with option A, plus each block's
two lines. That is 2 pairs × 100 knots × (interactions per driver) of them: a few hundred interactions gives
10^5–10^6 lines. The check streams the log; today's `cmd_coverage` reads it whole. The next B3 run measures it.

**Tests and mutants, once ruled.** The fixtures come from the format strings above. Near misses for each rule: a
`*computed*` record; `Spline found?....N`; a key of another config or tune; a missing or duplicate block; a block of
99 knots; an interleaved stderr line splitting a record; a truncated log; a record of another pair; an X missing
from the reduced spline, or one too many; three sum splines; each absence marker present; and an ignored messenger.
Mutants for each rule, red on HEAD for its own reason. The real layout is confirmed only by a real log, so §4 keeps
one on a STOP, and the first B3 run with the new rule is its validation, on both tunes.

## 4. Proposed runner change: keep the coverage log on a non-pass

Today, on every exit (STOP included), B3 deletes the coverage logs with the public-seed event files:
- pg_replay.sh's D5 trap `delete_events` (pg_replay.sh:94-160, installed at :161; the coverage logs at :120);
- the runner's `leftovers()` sweep (pg-replay-g2111a.py:292-309, called in `finally`), for any that remain.

That is why run 4's log is gone; only its sha survives.

Proposal, made stricter after the read:

- **When.** A log is kept only when its own coverage run ended and the messenger check passed. The messenger then
  held `gevgen` at its laconic level (Messenger_laconic.xml:219), so the log has no GHEP dump of the public-seed
  event. Every other non-pass deletes it as today.
- **What and where.** Only `gevgen.log`, and only to the two exact paths `R/kept/coverage_slot1/gevgen.log` and
  `R/kept/coverage_slot2/gevgen.log`. The move is a same-filesystem rename after the writers have ended, with
  no-follow checks, mode 0600. The event, status, GHEP and flux files are deleted as D5 requires.
- **Independence.** The D5 deletion and the STOP hold whether or not retention succeeds. A failed rename is reported
  and the log is then deleted. The trap stays safe to run again.
- **Checks.** deleted.json lists a kept log as `kept` (sha256 over raw bytes, size). A nonzero driver exit bypasses
  `deleted_problems()` today (pg-replay-g2111a.py:420-431), so the runner gets its own kept-log check, run in
  `finally` on every path. It requires only those two paths, regular files, the recorded sha, and nothing else under
  `run/kept/`. `leftovers()` already ignores `run/kept/`, and the new check closes that gap. A slot whose run never
  started (an early STOP) is simply absent.
- **Pass.** Unchanged: the log is deleted after its check and its hash kept (D3′).

**Production's STOP, stated plainly.** pg_generate.sh's coverage `rm -f` (:281) runs only after `coverage-log` passes
(:279-280). So a STOP there keeps the log, and also the public-seed GHEP, status and flux files in `O/coverage/T`.
`seedfree` (:96-106) covers only `work/u*/t*`. Its EXIT cleanup (:150-159) withdraws publication. This proposal
leaves production as it is. Whether production should delete those public-seed files on a STOP is a separate
question for the director.

## 5. What moves if both are ruled in

- `pg_verify.py` (`coverage_problems`, its docstring) and README-pg.md's D3′ text.
- `pg_replay.sh` (the trap) and the runner (`leftovers`, `deleted_problems`), then a re-embed.
- The tests, the mutants, and RULINGS-A2.md.
- `pg_generate.sh`'s bytes don't change. It runs the new `coverage-log` through `pg_verify.py`, so any pin cov2d
  holds on `pg_verify.py` moves.
- `run_gevgen_v3.sh` is unchanged. The messenger is unchanged under option B. Under option A,
  `MESSENGER_LINE` becomes two lines and `MESSENGER_SHA256` moves, so the coverage trace check's pin moves with it.
- Then the full verification chain, with PG_MUTANT_JOBS set and recorded, and B3 run 5 on the director's GO.

## 6. Independent read

codex-school2, gpt-6.2-sol, high, 2026-11-27: SOUND WITH FIXES. It read this note's first version (12cc0d39) against
the GENIE R-3_04_00 sources and the lane's scripts, all copied into its read-only directory. Its three required fixes
are taken in above:
1. bind each sum-spline block to its pair, with complete knot records and exact keys, from lookup evidence
   (XSecSplLst), scoped to the bootstrap;
2. correct the marker table, validate against real logs from both tunes, stream the log and hash its raw bytes;
3. define when retention happens, validate kept files independently, keep D5 and the STOP independent of
   retention, and state what production keeps on a STOP.
