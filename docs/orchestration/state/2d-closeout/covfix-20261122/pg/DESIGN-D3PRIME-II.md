# D3′(ii) on gevgen's flux path: the replacement (rev 12)

**Status: ADOPTED.** Joseph, 2026-11-27: "okay yes I go with the recommendations". He decided after an unanchored
codex-school2 read of this note at 6d78f54a. That read's prompt and report were at
`/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/be6e903d-7ae7-440f-b5aa-de78760f31e0/scratchpad/cx-rev12/{PROMPT.md,report.md}`,
and are committed verbatim in `decision-read/` (PROMPT.txt d0b1690f, report.txt 3051f613). The adopted design is
option A, with the director's tightenings (§3), and the STOP retention rule for production and the replay (§4).

Evidence: B3 run 4's receipt (`install/pg-replay-g2111a.py.out`, 3c88ff0e) and two read-only diagnostics,
`install/b3-diag/b3-run4-diag.out` (1293dd12) and `b3-run4-diag2.out` (1b82fcc7). GENIE lines are R-3_04_00
(GENIE-MC/Generator on GitHub). The copies used compare byte-equal to the tag, and gEvGen.cxx is ff7bce18.

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

## 3. The adopted rule (option A, tightened)

**The messenger.** Two pinned lines of Messenger_laconic.xml are raised to DEBUG: GEVGDriver (:89) and XSecSplLst
(:201). Every other stream keeps its laconic level, `gevgen` included (:219, WARN). `MESSENGER_LINE` becomes those two
replacements, and `MESSENGER_SHA256` becomes the new file's hash.

**Records.** log4cpp's BasicLayout writes each LOG message as one record. The first line is
`<seconds> <PRIORITY> <stream> : [n] <file::function (line)> : <text>`, or `[s] <function (line)> : ` for SLOG
(Messenger.h:84-99). Each `\n` in the message starts a continuation line. The parser splits the log into records at
these prefix lines. It reads the log as a stream and hashes its raw bytes. The prefix form is confirmed only on real
bytes; see the validation below.

**Phases**, in the order GMCJDriver::Configure runs them (GMCJDriver.cxx:399-447):
- **Configure, one per driver.** It opens with GEVGDriver's NOTICE `Configuring event generation driver for initial
  state: `nu-pdg:<nu>;tgt-pdg:<tgt>;' …` (GEVGDriver.cxx:146-156; InitialState.cxx:408-422). Inside it, `UseSplines`
  (:524-571) looks up every interaction the driver needs. Each lookup is a `Checking for spline: K in tune: T` and a
  `Spline found?....Y|N` record (XSecSplineList.cxx:103-104, 115-116). Those keys, in order, are **the driver's
  required inventory I(d)**. K is `alg_name/config/interaction` (XSecSplineList.cxx:541-545), the same string as the
  spline XML's `name`.
- **Summation, one per driver.** It opens with INFO `Creating spline (sum-xsec = f(logE)) in E = [a, b] using N knots`
  (GEVGDriver.cxx:449-451). It has N knot blocks. Each block opens with DEBUG `Computing the cross section sum` (:378).
  For each interaction it then holds, in order:
  - `Compute cross section for interaction: ` + X (:398-399);
  - `Checking for spline: K …` and `Spline found?....Y`, from `SplineExists` (:407);
  - `Getting spline: K in tune: T` (XSecSplineList.cxx:135-136). This is logged only inside `GetSpline`, which
    XSecSum calls only on the Evaluate branch (GEVGDriver.cxx:408-410);
  - `Interaction   = X` / `Cross Section *interpolated* = s cm2` (:419-423).
  The block closes with INFO `SumXSec(…)*interpolated* = …` (:429-434).

**The rules.** Pairs are F1's argv pairs. The tune is the run's. R_T is the reduced spline file's full keys
(tune, name).
- **P1, the inventory.** For each pair there is exactly one Configure phase whose initial state is that pair. Its
  inventory is non-empty and has no duplicates. Every record is `found?....Y`. Every K's tune is T, its interaction
  part has `nu:`/`tgt:` equal to the pair, and (T, K) ∈ R_T. The comparison is against the driver's inventory, not
  against every entry of the reduced XML: the reducer filters by target, so the XML can hold entries no driver
  needs.
- **P2, each lookup evaluated.** For each pair there is exactly one Summation phase, with N = 100 (GMCJDriver.cxx:467).
  It has exactly N blocks, each closed by its `SumXSec(…)*interpolated*`. In each block, the interactions' keys, in
  order, equal I(d), and each interaction's records appear exactly in the order above. The X of `Compute`, the
  interaction part of K in all three lookup records, and the X of `Interaction   =` are one string. Each tune field
  is T. Each label is `*interpolated*`. **Every `Spline found?....Y` inside a block is followed by its
  `Getting spline` for the same key before the `Interaction` record.**
- **P3, absences anywhere in the log.** Any of these is a STOP:
  - `Reverting back to not using splines`, `You haven't loaded any splines`, `Couldn't find spline:`,
    `No splines for tune`, `Spline requested while CurrentTune not set`, `*computed*`;
  - `CreateSplines`' three markers (§2);
  - inside a phase, `Spline found?....N`.
- **P4, damage.** Inside a Summation phase, every GEVGDriver and XSecSplLst record must be one of the types above,
  and no line may stand outside a record. Records of other streams there are counted and kept, but not allowed
  silently: each is a STOP until a real log shows them benign. A log cut off before the last phase closes is
  truncated and STOPs.

Scope: the bootstrap, that is the sum splines GMCJDriver builds in Configure. Event time (interaction selection) is
outside it: lookups after the last Summation phase are not checked.

**Validating the parser on both tunes before it gates G.** No existing log can serve. Every earlier gevgen ran with
Messenger_laconic.xml, with GEVGDriver and XSecSplLst at WARN (:89, :201), so none holds these DEBUG records.
gspl2root's own logs (run_gevgen_v3.sh:116-117) run at the default Messenger.xml levels, also WARN for both streams
(Messenger.xml:96, :207), so they can confirm only the prefix layout. Plan:
1. Offline: fixtures built from the format strings above. Then one read-only diagnostic, for the director's GO, of
   run 4's `run/graphs_G21_11a_00_000.log`: real GENIE records on scratch today. It confirms the BasicLayout prefix
   and the `[n]`/`[s]` forms on real bytes. This is a read, not a run.
2. B3 run 5, a public-seed rehearsal, not G, has a coverage run for each tune: slot 1 G21_11a_00_000 and slot 2
   G18_02a_00_000. On every exit it keeps both coverage logs' recognized records (§4), so a pass can be reviewed
   too. The rule gates the sealed G only after run 5 has passed on both tunes and the director has read the kept
   records. If the real format differs, run 5 STOPs on P1, P2 or P4 with the records and the counts of unrecognized
   records kept. In the replay, keeping on a pass is a deliberate exception for validation; production keeps only
   on a STOP.

**Cost, to be measured.** Per pair, 100 knots × (interactions) × about 10 lines. XSecSplLst at DEBUG also logs each
loaded spline's knots at INFO (XSecSplineList.cxx:461, :486), about 250 × (splines in the reduced file). Together
that is 10^5–10^6 lines. The check streams the log. Run 5 measures it.

**Tests and mutants.** Fixtures for each rule and its near misses:
- a key of another config or tune; a key outside R_T; an R_T entry no driver needs (allowed); a duplicate inventory
  key;
- a missing `Getting spline` after `found?....Y`; `found?....N`; a `*computed*` label;
- 99 or 101 blocks; a block whose keys differ from I(d); a missing or extra Configure or Summation phase; a block
  out of order; a foreign line splitting a record; a truncated log;
- each absence marker; the old CreateSplines markers; an ignored messenger (no DEBUG records);
- both tunes' keys.
Mutants for each rule, red on HEAD for its own reason.

## 4. On a STOP: delete the public-seed files, keep the recognized records

The same in production (pg_generate.sh) and the replay (pg_replay.sh), as the director ruled:
- **Delete.** Once every writer of a coverage directory has exited (production: after `drain`; the replay: in D5's
  trap), its public-seed event, status, GHEP and flux files are deleted: `gntp.123456789.ghep.root`,
  `genie-mcjob-123456789.status` and `input-flux.root`.
- **Keep the records.** A new `pg_verify coverage-keep --log L --out K` streams gevgen.log once. It writes K (JSON)
  with the raw log's sha256 and size, every record of the P1–P4 types in order (their texts, which carry interaction
  codes, keys and cross sections only), and counts of every other record by stream and priority. It keeps no other
  text, so a GHEP dump at a misconfigured level cannot be kept. Then the raw log is deleted. K is written once
  (O_EXCL), mode 0600, beside where the log was, as `coverage_kept.json`.
- **Independence.** Deletion runs even if `coverage-keep` fails, and so does the STOP. A failed keep is reported,
  and the raw log is still deleted. The trap stays safe to run again.
- **Production.** pg_generate.sh's EXIT cleanup gains this for each `O/coverage/<tune>` that exists, on any nonzero
  exit, after `drain`. On a pass, nothing changes: the files are removed after the check (:281), and the check keeps
  the log's hash.
- **Replay.** D5's trap does the same for both coverage directories. During validation (run 5) it does so on every
  exit, pass included (§3). deleted.json records the raw log as deleted, with its sha256 and size, and names K. The
  runner's `deleted_problems` and `leftovers` accept exactly those `coverage_kept.json` files and nothing else new.
  On a nonzero driver exit, which bypasses `deleted_problems` (pg-replay-g2111a.py:420-431), a kept-file check runs
  in `finally` on every path.

## 5. What moves

- `pg_verify.py`:
  - `MESSENGER_LINE`, now two lines, and `MESSENGER_SHA256`, now the new file's hash;
  - `coverage_problems`, replaced by the record parser and P1–P4;
  - `cmd_coverage`, streaming and hashing raw bytes;
  - the new `coverage-keep`;
  - the docstring.
  The coverage trace check's messenger pin moves with `MESSENGER_SHA256`.
- `pg_generate.sh`: the EXIT cleanup's coverage step. Its sha moves; cov2d's pin goes through the director.
- `pg_replay.sh`: D5's trap. The runner: `deleted_problems`, `leftovers` and the kept-file check. Then a re-embed.
- README-pg.md's D3′ text, the tests, the mutants, RULINGS-A2.md and REHEARSAL-CHECKLIST.md.
- `run_gevgen_v3.sh` is unchanged; the messenger file is generated, not edited.
- Then the full verification chain, with PG_MUTANT_JOBS set and recorded. Then the layout diagnostic and B3 run 5,
  each on the director's GO.

## 6. Independent read

codex-school2, gpt-6.2-sol, high, 2026-11-27: SOUND WITH FIXES. It read this note's first version (12cc0d39) against
the GENIE R-3_04_00 sources and the lane's scripts, all copied into its read-only directory. Its three required fixes
are taken in above:
1. bind each sum-spline block to its pair, with complete knot records and exact keys, from lookup evidence
   (XSecSplLst), scoped to the bootstrap;
2. correct the marker table, validate against real logs from both tunes, stream the log and hash its raw bytes;
3. define when retention happens, validate kept files independently, keep D5 and the STOP independent of
   retention, and state what production keeps on a STOP.

The decision read (codex-school2, 2026-11-27, at 6d78f54a, unanchored) recommended option A with the `Getting
spline` requirement and the driver-inventory comparison. For a production STOP it recommended deleting the public-seed
files and keeping only recognized records. The director folded both into §3 and §4.
