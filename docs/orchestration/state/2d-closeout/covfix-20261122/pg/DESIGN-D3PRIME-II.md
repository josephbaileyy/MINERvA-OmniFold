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

All of these are on the `GEVGDriver` stream. The pinned coverage messenger raises only that stream, from WARN
(Messenger_laconic.xml:89) to DEBUG.

| where | priority | text | meaning |
|---|---|---|---|
| `UseSplines`, GEVGDriver.cxx:566-570, run from `GMCJDriver::PopulateEventGenDriverPool` (GMCJDriver.cxx:590) for each (nu, target) | WARN | `*** At least a spline (algorithm: A, interaction: X doesn't exist. Reverting back to not using splines` | a spline the driver needs is missing; the driver's `fUseSplines` becomes false |
| `CreateXSecSumSpline`, :449-451 (from `BootstrapXSecSplineSummation`, GMCJDriver.cxx:661, unconditional) | INFO | `Creating spline (sum-xsec = f(logE)) in E = [..] using 100 knots` | one per (nu, target); 100 is `fXSecSplineNbins` (GMCJDriver.cxx:467) |
| same, :453-455 | FATAL | `You haven't loaded any splines!! ` | that driver's `fUseSplines` is false |
| `XSecSum`, :378 | DEBUG | `Computing the cross section sum` | once per knot |
| `XSecSum`, :419-423 | DEBUG | `Interaction   = X` then `Cross Section *interpolated* = s cm2` (or `*computed*`) | one per interaction per knot. `*interpolated*` prints only when the driver's `fUseSplines` is true, that is when `UseSplines` found every spline (:553). `*computed*` means integrated (:413). |
| `XSecSum`, :429-434 | INFO | `SumXSec(nu+tgt->X, E = e GeV)*interpolated* = s cm2` | one per knot, named by PDG name |

**The assert is compiled out in the pinned build.** `libGFwEG-3.04.00.so` (pin 17a907b1, matched) holds neither the
expression string of GEVGDriver.cxx:457's `assert(Emin<Emax && Emin>0 && nk>2)` nor any `__assert_fail` import (0
and 0, b3-run4-diag2.out §2). The member name `fUseSplines` occurs 4 times through ordinary code and symbols, so it
says nothing either way (the director's caution). The Make files don't set NDEBUG themselves:
`GOPT_WITH_CXX_DEBUG_FLAG=` is empty (Make.config:36), and CXXFLAGS take `$(ENV_CXXFLAGS)` from the build
environment (Make.include:587). The binary is the evidence. So with a missing spline, gevgen logs the WARN and the
FATAL, integrates instead (`*computed*`), and still exits 0. **A coverage run's rc 0 is therefore no evidence that
every spline was found.** That corrects my run-4 reading, which leaned on the assert.
<!-- absence-ok: an inference about what a coverage run's exit status shows, from GENIE's source and the pinned binary; not a claim that a result or study is absent -->

## 3. Proposed replacement for D3′(ii)'s log rule: positive, per pair, bound to the reduced spline

The coverage run itself is unchanged: one event, the public seed, the pinned messenger, and `argv-check`'s argv. Only
`coverage_problems` changes. Its new rules:

- **P1, positive.** For each (nu, target) of F1's argv (`argv_pairs`), the log has at least one `XSecSum` record:
  a line `Interaction   = X` with `nu:<nu>` and `tgt:<target>` in X, followed directly by
  `Cross Section *interpolated* = `. These lines are DEBUG, so a messenger that does not raise GEVGDriver to DEBUG
  leaves P1 unmet: a STOP, not a pass.
- **P2, no integration.** No `Cross Section *computed*` record and no `SumXSec(…)*computed*` line.
- **P3, the pinned file.** Every X in a P1 record is among the reduced spline's codes (`spline_codes`, as today).
- **P4, one sum spline per pair.** Exactly one `Creating spline (sum-xsec = f(logE))` line per (nu, target): two
  for F1's argv. Then a second driver, or a missing one, shows.
- **P5, fail-closed absences.** These print at WARN or FATAL under any messenger, so they also catch a misconfigured
  one. Any of them is a STOP: `Reverting back to not using splines`, `You haven't loaded any splines`,
  `The spline wasn't loaded at initialization`, and `Need xsec spline for`. The last two come from `CreateSplines`.
  If they ever appear, the run took a path this design does not model.

P1 is the primary rule; P5 only backs it up, as the director asked. P1's `*interpolated*` label is the driver's own
verdict that `UseSplines` found every spline its interaction list needs. P3 binds those interactions to the pinned
file.

**Cost, to be measured.** The DEBUG records number about 2 pairs × 100 knots × (interactions per driver) × 3 lines.
For a few hundred interactions that's on the order of 10^5 lines, a few tens of MB, in one log that is deleted after
the check (§4). The next B3 run will measure it.

**Tests and mutants, once ruled.** The fixtures will be built from the format strings cited above:
- for each rule, the line it needs and its near misses (a `*computed*` record; a record for another pair; an X
  missing from the reduced spline; a second sum spline; each absence marker present);
- the drivers' refusals unchanged.
There will be mutants for each rule, red on HEAD for its own reason. The exact log layout around a multi-line LOG
message (its prefix line) is confirmed only by a real log, and §4 keeps one on a STOP. If the format differs, the
next B3 run STOPs on P1 with the evidence kept.

## 4. Proposed runner change: keep the coverage log on a non-pass

Today, on every exit (STOP included), B3 deletes the coverage logs with the public-seed event files:
- pg_replay.sh's D5 trap `delete_events` (pg_replay.sh:94-160, installed at :161; the coverage logs at :120) removes each coverage run's
  `gevgen.log` with its event and status files (DELETABLE in the runner);
- the runner's `leftovers()` sweep (pg-replay-g2111a.py:292-309, called in `finally`) removes any that remain.

That is why run 4's log is gone; only its sha survives.

Proposal:
- On a non-pass exit, pg_replay.sh moves each coverage `gevgen.log` to `R/kept/coverage_slotN/gevgen.log`. This is a
  same-filesystem rename, made with no-follow checks. It still deletes the event, status, GHEP and flux files as D5
  requires, so only text logs are kept.
- deleted.json records the kept logs as `kept` (sha256, size) instead of `deleted`.
- `leftovers()` does not sweep `run/kept/`.
- `deleted_problems` accepts a coverage log as kept only when the driver's rc is not 0.
- On a pass, nothing changes: the log is deleted after its check and its hash is kept (D3′).

An alternative is to keep every coverage output, the public-seed GHEP included. I don't recommend it: D5 deletes
event files on purpose, and the log is the evidence.

pg_generate.sh needs no change for this. Its coverage `rm -f` (pg_generate.sh:281) runs only after `coverage-log`
has passed (:279-280), so a STOP there already keeps the log.

## 5. What moves if both are ruled in

- `pg_verify.py` (`coverage_problems`, its docstring) and README-pg.md's D3′ text.
- `pg_replay.sh` (the trap) and the runner (`leftovers`, `deleted_problems`), then a re-embed.
- The tests, the mutants, and RULINGS-A2.md.
- `pg_generate.sh`'s bytes don't change. It runs the new `coverage-log` through `pg_verify.py`, so any pin cov2d
  holds on `pg_verify.py` moves.
- `run_gevgen_v3.sh` and the messenger are unchanged.
- Then the full verification chain, with PG_MUTANT_JOBS set and recorded, and B3 run 5 on the director's GO.
