# ROUND-7 REPAIR PACKET — pre-use parity for every sourced tracked file, and the M-1…M-6 filing

**CITABLE FOR:** what was built, where it is, and what was measured, on 2026-08-23.

**NOT CITABLE FOR:** a Gate-1 verdict. **Gate 1 is NOT claimed passed.** This packet is graded input,
not a result. The builder does not grade it.

## SHAs and trees

| | value |
|---|---|
| **FINAL CANDIDATE** | `e93364d158ab16c109f124c54199caaad28c0708` (`build-k0-execution-integrity`) |
| **DEPLOYED AT** | `/pscratch/sd/j/josephrb/k0r2/clean`, HEAD `e93364d1…`, `porcelain=0`, **0 writable files** (A-2(g) re-applied) |
| **main** | `c76fdbfac67d39f86bc0ea633e815c926de04add` — carries the ruling record and the same filing bytes |
| graded predecessor | `fabeedc2bf78c81d2931ff4876d161c0abfbdbc4` (round-6, 16 PASS / 2 FAIL) |
| `MNV_ENV_ROOT` | `/pscratch/sd/j/josephrb/k0env` |
| `MNV_CONDA_PREFIX` | `/global/u2/j/josephrb/.conda/envs/root_6_28` |

Deployment path is `canonical → k0r2/bare.git → k0r2/clean`, **fast-forward only**.

**A NOTE ON WHICH SHA IS "FINAL", because a document cannot name its own commit.** `e93364d1` is the
last sha at which any **executable** file changed — the eight launchers, the test file, the
measurement tool. Commits after it are this packet, a correction inside the M-1…M-6 filing, and the
regenerated manifest/catalog views. **The deployed sha is whatever `git -C /pscratch/sd/j/josephrb/
k0r2/clean rev-parse HEAD` returns, and it is the one to grade;** verify with
`git diff --name-only e93364d1..HEAD`, which must list **only** files under `docs/orchestration/`.
If that command ever lists an `.sh` or a test, this note is void and the measurements above were
taken on different bytes than the deployed ones.

## Authorization

Joseph, 2026-08-23, three items and no unrelated changes; ruling recorded at
[`DECISION-20260823-joseph-a2f-does-not-substitute-for-a3.md`](DECISION-20260823-joseph-a2f-does-not-substitute-for-a3.md).
**Explicitly withheld:** Slurm submission, science run, further repair rounds, any Gate-1 pass claim.
None of the withheld actions was taken.

---

## 1. F-2(a) — the parity gate now binds every tracked file the preamble sources

`sha256(gate block) = 3e211fe6831aeb8d93522c6cbd2d72375a09a42ad5440eb9bac2e32e839a4142`, **one distinct
digest across all eight launchers.**

```bash
for _mnv_rel in lib/resume_guard.sh \
                nd-unfolding/lib_mnv_env_preflight.sh \
                nd-unfolding/lib_mnv_env_pathcheck.sh; do
  _mnv_head="$(git -C "$CODE_ROOT" rev-parse "HEAD:${_mnv_rel}" 2>/dev/null || true)"
  _mnv_work="$(git -C "$CODE_ROOT" hash-object "${CODE_ROOT}/${_mnv_rel}" 2>/dev/null || true)"
  ...  exit 3 on either empty, or on mismatch
done
```

**All three are verified before any is sourced.** Verifying each immediately before its own source
would still leave file 2 unbound while file 1 executes.

| launcher | gate | first library source | activator |
|---|---|---|---|
| `sbatch_bootstrap_5d_gpu.sh` | 81–98 | :102 | :105 |
| `sbatch_finalize_5d_bkgaware_gpu.sh` | 74–91 | :95 | :98 |
| `sbatch_uthrow_block_5d.sh` | 71–88 | :92 | :95 |
| `sbatch_unfold_5d_detector_bkgaware_gpu.sh` | 82–99 | :103 | :116 |

**No sourced helper, deliberately.** A helper performing this check would itself execute before
anything bound *its* bytes — F-2(a) reproduced one level down. A test asserts nothing at all is
sourced above the gate.

### Controls — four directions, ten tests

`nd-unfolding/tests/test_k0_launcher_two_roots.py`, class
`EveryTrackedSourcedFileIsGitBoundBEFOREAnyOfThemIsSourced`:

1. **Silent on good** — clean tree, no parity message, all eight exit 0.
2. **Fires on bad** — each of the three mutated, refused **by name**, exit 3, across all eight.
3. **Opposite direction** — (a) an unhashable library refuses too, because `hash-object` on a missing
   file yields the empty string and a naive compare would read *empty == empty* as agreement;
   (b) a tracked file the preamble never sources is **left alone by this gate** and still refused by
   the **later `srcman` gate**, which the arm names rather than merely asserting silence.
4. **Before, not after — dynamically.** **The mutation is the marker:** the appended line writes a
   file, so it both breaks the hash and leaves physical evidence if the library was sourced anyway.
   Plus a **negative control** proving the marker *does* appear when parity holds — without it, every
   `assertFalse` above would also pass if the append had silently never happened.

**Power checked, not assumed.** Reverting the loop to single-file coverage fails four arms — the
ordering arm with `nd-unfolding/lib_mnv_env_preflight.sh WAS SOURCED before/despite the parity
refusal`. **The test reproduces the round-6 defect it forbids.**

## 2. F-17(a) — the M-1…M-6 filing

[`MEASUREMENT-20260823-m1-m6-at-the-candidate-and-canonical.md`](MEASUREMENT-20260823-m1-m6-at-the-candidate-and-canonical.md),
produced by the committed instrument `docs/orchestration/measure_m1_m6.py`.

**Ten M-1 rows, not nine.** `unified_throw_cov.py` restored. **Four** surviving absolute literals on
the candidate — three `_DATA_ROOT` and one **inert** `_REPO` (`adopt_unified_5d.py:35`, zero
repository modules after its insert, *measured*). **Five** on the canonical checkout, all `_REPO`,
and `unified_throw_cov.py:42` is **active** there with five repository imports after `insert(0, …)`.

The instrument takes the tree as a **mandatory argument** and **refuses on CPython < 3.10** — on the
pre-conda 3.6.15 a literal is `ast.Str`, so M-1 would print a clean, silent, wrong zero. Refusal
verified on saul, `rc=1`.

## 3. Runbook and plan §C

Both now export `MNV_ENV_ROOT` and `MNV_CONDA_PREFIX` with concrete values, and the runbook's
variable table gains both plus an explicit note that `MNV_SOURCE_MANIFEST` **does not cover the files
the preamble sources**. **Plan §C-2 carried a live defect and it is removed:** the submitting shell
ran `source "${MNV_CODE_ROOT}/setup_salloc_env.sh"` — the round-4 F-2(a) finding verbatim, from a tree
`.gitignore` guarantees lacks that file.

---

## Post-commit checks, in the deployed tree at the final sha

```
$ git -C /pscratch/sd/j/josephrb/k0r2/clean rev-parse HEAD
e93364d158ab16c109f124c54199caaad28c0708
$ git -C ... status --porcelain | wc -l                       0
$ find ... -type f -writable | wc -l                          0
$ python3 docs/orchestration/measure_m1_m6.py --tree ...      rc=0
$ python3 docs/orchestration/verify_hash_bindings.py          rc=0   ALL BINDINGS INTACT
$ python3 docs/orchestration/generate_manifest.py --check     rc=0   rows=427
$ python3 docs/orchestration/live_doc_indexed.py              rc=0
$ python3 nd-unfolding/mnv_preflight_census.py                rc=0
    8 launcher(s): 14 guarded + 16 declared-preflight + 16 interpreter-probe
                 + 0 unclassified = 46 invocations; 18 commented out
```

**Ruling 21's boundary is untouched at 14 + 16, with the 16 interpreter probes as the visible third
category Joseph ratified.**

### Suite, on matched trees

Both are fresh writable clones from the same bare repo, same host, same interpreter (Linux, CPython
3.13.15, pytest 9.1.1):

| tree | result |
|---|---|
| candidate `e93364d1` | **13 failed, 2531 passed, 17 skipped, 643 subtests passed** |
| baseline `fabeedc2` | **13 failed, 2521 passed, 17 skipped, 581 subtests passed** |

**Failure sets identical; zero regressions, zero accidental fixes.** `+10 passed` are the new arms.
The 13 are pre-existing at the graded predecessor.

---

## THREE THINGS THAT WENT WRONG IN BUILDING THIS, RECORDED RATHER THAN QUIETLY FIXED

1. **I measured the wrong tree and argued from it.** Preparing this repair I read
   `unified_throw_cov.py` on **`main`**, found an active hardcoded `_REPO`, reported it as the
   *candidate's* state, and told Joseph his instruction pre-specified a wrong answer. He re-measured
   `git show fabeedc2:…` and corrected me. **His expected 3 + 1 split is what the candidate actually
   measures.** Wrong tree, real fact — this campaign's named recurring defect, mine again.
2. **My own instrument had the substring bug it exists to catch.** `m6` tested for the `else 0`
   string and returned *"vacuity hole closed"* for the canonical checkout — where the entire
   inventory write is **absent**. It now reports three distinct states.
3. **`generate_manifest --check` exited 1 on the deployed tree while exiting 0 in my worktree**,
   because I ran the generator **before `git add`** and the new filing recorded as `intended` rather
   than `tracked`. Same mechanism as round 5's false "390 passed". Fixed in a separate commit and
   verified idempotent after staging.

**A fourth correction is inside the filing itself:** an earlier draft recorded canonical M-3 as *"did
not complete in 26 minutes."* It does complete, in about 30, and it returns **`rc=1` — bindings NOT
intact.** A slow check reads as an inconvenience; a failing one is a finding. The itemized list of
which bindings break is **owed, not captured.**

## ROUND-7 VERDICT AND THE F-17(a) FIX (appended 2026-08-23, after the terminal regrade)

The round-7 regrade returned **17 PASS / 1 FAIL / 0 NOT-EVALUABLE** — `F-2(a)` and `F-14` **pass**;
`F-17(a)` fails. Verdict `GATE1-VERDICT-ROUND7-20260823-k0-execution-integrity.md`, sha256
`3173c83c76efae4e07dbfaacad2cea68f4b837f01c676d74aefd03f9ae2c760a`, 439 lines.

**The failure was in this packet's own instrument and the grader was right.** `measure_m1_m6.py`
matched the canonical root by **exact equality**, so canonical M-1 reported **five** literals where
there are **seven**: `bootstrap_nd.py:10` and `seedscan_split.py:21` hold it as
`_ND = ".../MINERvA-OmniFold/nd-unfolding"` — the **subpath** form — each feeding
`sys.path.insert(0, _ND)` with three repository modules straight after. Two of ten rows read
`literal=-` for files carrying an active rooted insert.

**Fixed:** `canonical_form()` now returns `exact` / `subpath` / `None`, bounded at
**exact-or-followed-by-a-separator** so a real sibling repository (`…-Analysis-Note`) is *not*
matched — over-broad is not the safe direction either. The scan now walks **every** string constant,
not only assignment right-hand sides, so a bare inline path is visible too. New arms in
`docs/orchestration/test_measure_m1_m6.py`: **9 pass; reverting the detector to exact equality fails
3.** Re-measured: **candidate 4 (unchanged), canonical 7.**

**The root cause is not the missing branch.** The identical exact-match/substring failure was found
and fixed in `m6` **earlier the same day, in this same file**, and the sibling function four
definitions above was never swept — and the instrument shipped with **no tests at all**. A known
limit is now stated in the filing rather than left to be discovered: it counts **literals, not
computed paths**.

The grader also **corrected the commission's framing in the builder's favour** — `e93364d1` touched
only `MANIFEST.tsv`, so executable bytes froze earlier still — and reported two of its own harness
errors against its own interest.

**A separate live hazard, not part of this repair:** the candidate branch carries a **575-line
superseded copy** of the operative rubric (`80402f75…`) against main's authoritative **1160 lines**
(`e0fb342b6466…`). **Grading from the branch would be void.** Unrepaired; flagged.

## What is NOT claimed

- **Gate 1 does not pass**, and this packet does not assert that `F-2(a)` or `F-17(a)` is closed.
  Whether the repair satisfies the criteria is the grader's call, on the frozen rubric.
- No Slurm job was submitted, no science was run, no covariance work was done, no artifact deleted.
- `set -u` was **not** added anywhere.
- The M-6 vacuity hole remains **open** on the candidate, unchanged and out of scope.
- Canonical M-3's failing binding is now **enumerated**: exactly one,
  `nd-unfolding/pet/train_fullevent_nominal.py` bound by an **untracked** run receipt
  (`…/slurm-56534116_2/STEP1_DYNAMICS.json`) that exists only on the canonical checkout. The file is
  byte-identical and at the same git blob on both trees, so this is a stale PET provenance receipt,
  not tree corruption, and it **cannot appear on the candidate**. No repair attempted; none authorized.
