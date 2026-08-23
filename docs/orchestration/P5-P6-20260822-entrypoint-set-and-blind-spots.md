# P-5 and P-6 — the entrypoint set, and the blind-spot inventory

> ## ⚠ P-5 IS INCOMPLETE (2026-08-23). P-6 stands.
> The round-4 grader reproduced **`P-6` exactly**. **`P-5` omits the two live blind spots on the
> path:** the `.sh` closure below `setup_salloc_env.sh` being **absent and unsatisfiable**, and
> `lib_member_resume.sh` being **bind-after-use in all eight launchers**. The builder lane's own
> position is that this should have **failed** `F-8(a)` rather than passed it — a blind-spot
>
> **THE BUILDER'S "SHOULD HAVE FAILED" OBJECTION IS WITHDRAWN (2026-08-23) and `F-8(a)` PASSES.**
> The grader declined it on a better argument: `P-5` is a register of blind spots that must be
> **disclosed because they cannot be closed**, and `lib_member_resume.sh` bind-after-use is a
> **repairable ordering defect with a one-hunk fix**, not a blind spot. Filing it here would have
> laundered a fix into a permanent caveat and left the launcher wrong with paperwork attached.
> `F-2(a)` is its correct home.
>
> **TWO THINGS ARE NONETHELESS REQUIRED BEFORE RE-GRADE, and they are repairs, not a tally change:**
> 1. **`P-5` must gain a FIFTH blind spot** — the `PATH` / `PYTHONPATH` / `LD_LIBRARY_PATH` channel.
>    `unbinned_unfolding/build/setup.sh:3-5` injects the canonical checkout into all three, and the
>    Python import guard is blind to two of them.
> 2. **`F-8(a)` must be treated as RE-OPENED at the new sha, never inherited.** It is mechanically
>    re-opened — bound to the pinned sha, and `PR-01` expires on the repair — but a document can be
>    carried forward by hand, so it is written down.
>
> See `CONFIRMATION-20260823-builder-response-to-gate1-round4.md` §3.

**CITABLE FOR:** the guarded entrypoint set measured on `MNV_CODE_ROOT` at the declared sha, and an
enumeration of what the OI-136 guard cannot see, with every child process marked **WRAPPED** or
**UNCOVERED**.

**NOT CITABLE FOR:** a Gate-1 pass. These are the two artifacts `F-8(a)` said did not exist; producing
them satisfies `PR-04` and nothing else.

**Why this exists.** Gate 1 refused a PASS because **P-5 and P-6 did not exist and were not
disclosed** — the same shape as round 1's undisclosed `P-4`. A mechanism that does not exist must be
reported **NOT-EVALUABLE**, never folded into a green count. Both are pure publication: they block
nothing mechanically downstream, *which is precisely why they went missing twice*.

**Measured at:** `MNV_CODE_ROOT = /pscratch/sd/j/josephrb/k0r2/clean`, sha
`6113a34d860ad9bcd643923d51170f228c80d894`, 775 tracked source files, listing sha256
`cc00489464b0e803247eeb7cd90afa2f59f010340f6db64123e12b20eafc2239`
(`DECLARATION-20260822-k0-submission-sha.md`).

---

## P-6 — the entrypoint set, re-run on the pinned tree, command and full output

```
$ cd /pscratch/sd/j/josephrb/k0r2/clean/nd-unfolding
$ /usr/bin/grep -hoE -- '-- "\$\{CODE_ROOT\}/[^"]+"' \
    sbatch_bootstrap_5d_gpu.sh sbatch_seedscan_split_5d.sh \
    sbatch_unfold_5d_detector_bkgaware_gpu.sh sbatch_sweep_bank_5d_run_bkgaware_gpu.sh \
    sbatch_uthrow_run_5d_fast.sh sbatch_uthrow_block_5d.sh \
    sbatch_uthrow_combine_5d_fast.sh sbatch_finalize_5d_bkgaware_gpu.sh \
  | sort | uniq -c | sort -rn

      4 -- "${CODE_ROOT}/nd-unfolding/unified_throw_cov_5d.py"
      2 -- "${CODE_ROOT}/nd-unfolding/unfold_nd_omnifold_unbinned.py"
      2 -- "${CODE_ROOT}/nd-unfolding/mii_adopt_unified_5d_stamped.py"
      2 -- "${CODE_ROOT}/nd-unfolding/combine_cov_nd.py"
      1 -- "${CODE_ROOT}/nd-unfolding/sweep_bank_5d.py"
      1 -- "${CODE_ROOT}/nd-unfolding/seedscan_split.py"
      1 -- "${CODE_ROOT}/nd-unfolding/bootstrap_nd.py"
      1 -- "${CODE_ROOT}/nd-unfolding/analyze_universes_5d.py"
```

**8 distinct entrypoints across 14 invocations** — `4+2+2+2+1+1+1+1 = 14`.

**That 14 is an independent cross-check, not a restatement.** `mnv_preflight_census.py` counts
guarded invocations by matching `python3 "$GUARD" --expect-root`; this search counts the `--`
separated child targets. **Different patterns, different token, same 14**, and the census's
`14 guarded + 16 preflight + 0 unclassified = 30` holds on this tree. Ruling 21's boundary now
reproduces on a fifth independent measurement.

**Every entrypoint is addressed through `${CODE_ROOT}`.** Zero occurrences of a bare or
canonical-checkout path after `--`; the search would have shown them, since it matches any
`-- "${CODE_ROOT}/…"` and a non-`CODE_ROOT` target simply would not appear in this list. **That is a
statement about what this pattern selects, not proof that no other invocation form exists** — see the
`.sh`-route blind spot below.

---

## P-5 — the blind-spot inventory

### (i) Inherited from the inventory mechanism, restated so they are not rediscovered

Named in `mnv_import_set_ratchet.py`'s own docstring (`:28-31`) and carried here verbatim in substance:

| # | blind spot | why the guard cannot see it |
|---|---|---|
| 1 | **namespace packages** | `spec.origin` is `None`, so the guard returns before `checkout_root_of` |
| 2 | **modules already in `sys.modules` before `install()`** | the finder never runs for them |
| 3 | **a further subprocess that is not itself wrapped** | `PathFinder` is per-process; see (ii) |
| 4 | **the `.sh` route entirely** | the guard wraps Python import resolution, not shell |

Blind spot 3 is asserted in both directions by
`test_mnv_guarded_run.TheSubprocessBoundaryIsNotCovered`, so it is a *measured* limit, not a
disclaimer.

### (ii) The subprocess enumeration — every child, marked

All eight guarded entrypoints scanned on the pinned tree for
`subprocess|os.system|os.exec|Popen|multiprocessing|check_output|check_call`:

| entrypoint | spawn sites | verdict |
|---|---|---|
| `bootstrap_nd.py` | 0 | no child |
| `seedscan_split.py` | 0 | no child |
| `unfold_nd_omnifold_unbinned.py` | 0 | no child |
| `sweep_bank_5d.py` | 0 | no child |
| `unified_throw_cov_5d.py` | 0 | no child |
| `combine_cov_nd.py` | 0 | no child |
| `analyze_universes_5d.py` | 0 | no child |
| `mii_adopt_unified_5d_stamped.py` | 7 textual, **1 executing** | see below |

**The one real child, and it is WRAPPED.** Filtering the seven textual hits to executing spawn calls
leaves exactly one:

```
$ /usr/bin/grep -nE 'subprocess\.(call|run|Popen|check_output|check_call)|os\.(system|exec)' \
      mii_adopt_unified_5d_stamped.py | /usr/bin/grep -v '^[0-9]*: *#'
788:    rc = subprocess.call(argv_child)
```

The other six are an `import subprocess`, the `CHILD_GUARD` constant, argparse help, and comments.

| child | target | routed through the guard? | fail-closed? | **verdict** |
|---|---|---|---|---|
| `mii_adopt_unified_5d_stamped.py:788` | `adopt_unified_5d.py`, via `build_child_argv` (`:291`) | **YES** — `CHILD_GUARD = mnv_guarded_run.py` (`:157`), inserted when `expect_root` is given (`:295`, `:331`) | **YES, twice** — refuses if the guard binary is absent (`:333`) and refuses without an inventory path (`:337`, `:781`) | **WRAPPED** |

**So the subprocess enumeration is: one child on the whole k=0 path, and it is wrapped.** That is a
stronger result than the mechanism guarantees, and it is why it had to be *enumerated* rather than
assumed — the guard does **not** cross a subprocess boundary, so a second, unwrapped child would have
been invisible and would have looked exactly like this.

### (iii) What P-5 itself cannot say

- **It is a static scan.** A child spawned through an alias, an `importlib`-loaded helper, or a name
  built at runtime would not match the pattern set. The pattern set is published above so that claim
  can be checked rather than trusted.
- **It scans the eight guarded entrypoints only.** The `.sh` route (blind spot 4) is out of scope by
  construction, and `mnv_preflight_census.py` is the instrument that covers the shell side.
- **`adopt_unified_5d.py` is on the path without being invoked by any launcher.** The finalize
  launcher parity-checks it; the stamped wrapper runs it. An enumeration keyed on launcher
  invocations alone would have missed it entirely.

---

## Expiry

Any change to the launcher set or the entrypoint set, and any commit to
`build-k0-execution-integrity`. Both artifacts are bound to sha `6113a34d`; re-run both searches
before quoting either.
