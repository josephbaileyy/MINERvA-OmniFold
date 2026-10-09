# Session 2 — import safeguards and an unlaunched N2 harness

| field | content |
|---|---|
| `Lane` | Session 2, guard |
| `Decision` | Can a future 2D diagnostic demonstrably execute the reviewed implementation and record its provenance, while the repository detects new checkout-hijacking imports? |
| `Branch` / `Base` / `Head` | `prep/next-guard-20261009` / `5ac9706a21e8a5ac8863a65fd7623d8ab8d22269` (the merged baseline Joseph set; supersedes the dispatch commit) / see §11 for the reviewed and the final head |
| `Owned files` | §2 lists every path, by commit |
| `Pinned inputs` | §1 |
| `Resources` | §10. Cluster/GPU/training: **0** |
| `Review` | §9 |
| `Model / effort` | Claude Opus 5.5 (`claude-opus-5-5`), as stated by the session environment; effort not observable |
| `Disposition` | **PASS** for the engineering decision, with the limits in §8. This is not a scientific validation. N2 is not admitted, and the publication-ready measurement is **not** achieved by this lane (§12) |
| `Next action` | §13 |

## 1. Baseline and pinned inputs

- `git fetch origin` on 2026-10-09: `origin/main` = `5ac9706a` (PR #61 merge). That is the pin, with
  0 commits beyond it, so there is no newer remote change to reconcile. The worktree
  `MINERvA-OmniFold-next-guard-20261009` was branched from the pin at 19:58:44Z.
- Inputs at the pin (sha256 prefix / blob):
  - `closeout/GOALS-20261009-as-dispatched.md`: `81496789…`, equal to DISPATCH's recorded digest. Read: the shared contract and Goal 2.
  - `DISPATCH.md`: the writer table and report fields.
  - `closeout/REPORT.md` §11: Joseph's ruling.
  - `AUTHORIZATION-20260903-oi136-failopen-repair.md`: `1aaa0d90…`.
  - `KNOWN_ISSUES.md` row 89.
  - `docs/OPEN_ITEMS.md` OI-136.
  - DELIVERY-20261008 §5.
  - DESIGN-20261008 §2–§4, §16 and §16.1 (`815509e0…`).
  - Lane A's `verification.md`.
  - `nd-unfolding/mnv_guarded_run.py`: `30162f57…`.
  - The probe `probe-oi136-sys-path-hijack-20260826.py`: `253d9fd9…`.
  - `unbinned_unfolding/python/omnifold.py`: `e96234124a31…`, the ratchet's pinned constant.
  - The 2D driver: `3cc5adc7…`, lane A's post-repair digest.
- **Unchanged from the pin, and checked by diff:**
  - the guard core and the probe;
  - the pinned helper;
  - the 2D driver (its rooted insert stays inside `main()`, and its arm of the rooted ratchet passes);
  - the seven frozen scripts and their directories;
  - `verify_hash_bindings.py`.

## 2. What changed, by commit (behaviour and classification kept apart)

| commit | kind | paths |
|---|---|---|
| `5e5f742b` | classification only | `nd-unfolding/tests/test_oi136_rooted_insert_ratchet.py` (new `frozen_record` class plus the seven paths); `nd-unfolding/tests/test_oi136_failopen_inventory_ratchet.py` (constants 9 → 18, every site named) |
| `65c543eb` | behaviour | `2d-unfolding/uq/coverage_fixed_truth/fixed_truth_toy.py`, `…/ki85_compare.py`, new `…/n2/{__init__,execution,test_producer_provenance}.py`; fail-open constants 18 → 16 **in the same commit as the repair**, both sites named |
| `6e8ff685` | new subtree | `…/n2/{identity,members,design,harness,synthetic_producer,test_n2_harness}.py`, `…/n2/README.md`; one-line `execution.git_identity` change |
| `732b75dd` | test strength | `…/n2/test_producer_provenance.py` (§6.2, a mutant the old test missed) |
| later (§11) | behaviour + record | `…/n2/harness.py` and its test (a real member must record the frozen thread count); this report and `Q/guard/` evidence |

`2d-unfolding/uq/coverage_fixed_truth/test_coverage_fixed_truth.py` was **not** changed. Its 20
tests pass unchanged against the repaired `ki85_compare.py`.

## 3. The inventory, re-measured, with what each count measures

Instrument: [`inventory.py`](inventory.py). It **imports** the rooted ratchet's AST scanner and runs
the probe's CLI. Neither instrument is retyped. Outputs:
[`inventory-base-5ac9706a.json`](inventory-base-5ac9706a.json) and
[`inventory-final.json`](inventory-final.json).

| count | population it measures | at the pin | after this lane |
|---|---|---:|---:|
| 18 | probe FAIL-OPEN set: `.py` in the **working tree** (untracked included) whose `insert(0, …)` argument the probe's regex links to the canonical literal | 18 (`04357e1a…`) | 16 (`7aa29431…`) |
| 19 | AST rooted set: **tracked** `.py` where the literal reaches `sys.path.insert(0, …)` | 19 | 17 |
| 1 | AST-only member (pathlib binding the probe's regex cannot follow): `nd-unfolding/pet/gate2_target_runtime.py` | 1 | 1 |
| 10 | rooted ratchet's listed set before this lane = the nine 2026-09-03 non-repaired + `gate2_target_runtime.py` | 10 | 17 listed (10 + 7 `frozen_record`) |
| 9 | "original exceptions": the 2026-09-03 authorization's not-repaired list (3 probe records, the 2D arm, 5 receipt-bound) = the fail-open constant `9 / 0939e159…` | 9 | unchanged, still listed |
| 9 | the October sites on neither list: 2 live producers + 7 frozen records | 9 | 0 unlisted (2 repaired, 7 classified) |
| 21 | position-0 insert **call sites** over the 19 AST files (an occurrence count: two files have two each) | 21 | 19 |
| 144 / 66 / 60 | probe candidates (literal anywhere) / insert-but-not-rooted / no insert | 144 / 66 / 60 | 143 / 67 / 60 |
| 0 | adjacent shapes outside both ratchets: literal reaching `insert(k≠0, …)`, `sys.path.append` or `site.addsitedir` | 0 | 0 |
| 2 of 17 | failing tests across both ratchet suites (`test_no_file_outside_the_named_set_feeds_a_rooted_insert`, `test_the_fail_open_set_is_EXACTLY_the_recorded_one`); KI-89's "9/10" and "6/7" are the same two failures, counted per suite | 2 red | **0 red, 17/17** |
| 20 | the merge log's "site paths before 20 after 20" (`closeout/logs/integration.txt`) | — | — |

**The "20" is reconstructed, not measured.** The script that printed it was never committed. Among
the path-qualified `.py` tokens in `closeout/logs/oi136_ratchets.txt`, exactly 20 are unique: the 18
probe-measured sites plus the two ratchet test files named in traceback frames. The probe's 18
already contains all nine AST-new sites. The log also holds a bare `omnifold.py` (a test docstring),
which would make 21. So "20 site paths" counts sites plus test files in a log. It is neither 18 nor
19 nor 9.

**Dispositions.**

| set | disposition |
|---|---|
| `fixed_truth_toy.py`, `ki85_compare.py` | **repaired** (§4) |
| `state/ki84-adopt-20261006/{purity_datastream_check,recompute_2d_budget}.py`, `state/ki84-rebuild-20261006/{boot_spreads_vl170,compare_ki84_band,predict_ki84}.py`, `state/note-boot-20261003/boot_spreads.py`, `state/uqpaper-median-20261006/paper_median.py` | **classified `frozen_record`**, byte-for-byte unchanged. Each is a one-off analysis committed beside the JSON it writes (named per file in the ratchet). Nothing imports or launches any of them (`git grep`, 2026-10-09). No digest of any of them appears in the tree, so the reason they stay exceptional is that they are records, not that they are bound. A re-run must go through the guard, which refuses their canonical-checkout import |
| the 3 probe records, the 2D arm, the 5 receipt-bound files, `gate2_target_runtime.py` | **unchanged classes**. No authority here to move them |
| adjacent families outside these populations: `.sh` launchers that `cd` to the canonical root (OI-136 row: 71 exposed at 2026-08-20), the `MNV_REPO` idiom (35 files per the guard's docstring), the gate6 launcher defaults (OI-138) | **not re-measured and not repaired**. Recorded so that "16 / 17" is not read as the whole hazard |

## 4. The two live producers

**Repair (OI-136).**

- `fixed_truth_toy.py` sets `OMNIFOLD_PY = REPO / "unbinned_unfolding" / "python"`, with
  `REPO = parents[2]` of its own file. The canonical literal leaves the file.
- `ki85_compare.py` sets `UQ = HERE.parent`. Its `REALBOOT` data root keeps the literal, which is the
  two-root design.
- With `__file__` bound to the canonical checkout, each derived path equals the literal it replaced
  ([`noop_check.py`](noop_check.py), [`logs/noop_check.txt`](logs/noop_check.txt)). So behaviour on
  the tree that produced existing products is unchanged.

**What executes, and what is recorded** ([`n2/execution.py`](../../../../../2d-unfolding/uq/coverage_fixed_truth/n2/execution.py)):

- Before reading any input, each producer runs its repository modules from **bytes it has just
  hashed**, and only from inside its own checkout. For the toy that is the toy design, the driver
  module and the OmniFold helper. For KI-85 it is `analyze_uq.py`. The hashed bytes are the compiled
  bytes, so neither a later edit nor a stale `.pyc` can separate record from code. This closes lane
  A's F12 `.pyc` residual for these modules.
- A same-named module already imported from anywhere else is **refused** (exit 3). Examples are a
  conflicting checkout on `sys.path`, a `sitecustomize`, or an earlier import.
- The output records:
  - each executed file's path, sha256 and git blob;
  - HEAD, and the executed files that are not HEAD's blob;
  - the guard's state (installed, expect root, allow list);
  - the effective estimator arguments, i.e. the dicts actually passed to the helper;
  - Python, package versions read from metadata, the thread variables and the host;
  - input path, size and mtime, plus sha256 when stated or requested.
- The toy writes these as `producerProvenance`, and also as the driver's own record names
  `runConfig`, `omnifoldHelperFile` and `omnifoldHelperSha256`. KI-85 writes a `provenance` block
  that also lists every replica file read, with digests.
- `toyMetadata` and every KI-85 statistic are unchanged. Commit `65c543eb` has the full list.
- `--expect FILE` (commit, module digests, input digests) refuses any contradiction **before the
  mismatched module body executes**.
- `--require-provenance` also refuses when something is merely unknown:
  - not under `mnv_guarded_run.py` on exactly this checkout, with no `--allow`;
  - git unavailable;
  - an executed file that is not HEAD's;
  - a module or input with no stated digest;
  - an existing `--out`.
- `git` runs with every `GIT_*` variable removed. `GIT_DIR` would answer for another repository, and
  this shell's `GIT_EDITOR` was correctly refused by the guard at first.
- **Compatibility.** Without the strict flag an existing `--out` is recreated as before. The
  resume-guarded launchers rerun into a partial output, so they keep working. The three
  `sbatch_*.sh` launchers are outside this lane's write set and **unchanged**. They neither use the
  guard nor pass the strict flag (§13 gives the required form).

## 5. The N2 harness (synthetic-test readiness only)

`2d-unfolding/uq/coverage_fixed_truth/n2/` holds the harness. Its README carries the module table,
the real-launch path and the missing pieces.

- **Data resampling versus conditioned MC.**
  - Arm T has 50 fresh reservoir pseudo-data sets. Arm B has 50 data-only bootstraps of T001.
  - Every member carries `mc_stream: held`. `validate_plan` refuses any departure from the frozen
    plan: estimator settings (thread count included), seeds, base set, streams or member count.
  - A real member must also record `OMP_NUM_THREADS` = 64.
- **Identity and split.**
  - The key is `(source, mc_run, mc_subrun, mc_nthEvtInFile)`. Missing columns, missing or negative
    values and repeated keys are refused; a duplicate is a stop condition.
  - The DESIGN §4 hash split is implemented with an explicit `|` encoding, which the registration
    must adopt. The split manifest holds the rule plus per-(tree, fold) key-list digests.
  - C1, C2, C3 and C5 run on the **materialized** folds. A split recomputed from the rule is
    disjoint by construction, so testing it would pass whatever was handed over; the rule is checked
    separately.
  - C4 is an equality check (production versus rebuild, row by row, bit for bit). C6 checks each
    member's identity sidecar. C7 is review, not code.
- **Members.**
  - Every declared member ends `ok`, `failed` or `missing`. A record naming another plan or spec is
    `failed`. A member with both a result and a failure record is `failed`, with the contradiction
    kept.
  - The only route to a statistic needs all 100 members `ok`. Otherwise the verdict is
    `INCONCLUSIVE`, with every non-ok member listed. There is no success-only subset.
- **Outputs.** Every record and result is published by atomic hard-link (`write_new`), which refuses
  any existing name. `run-member` runs a member once, through the guard with
  `--require-provenance`, and records a failure rather than retrying.
- **Admission.** `run-member`, `aggregate` and `admit` need an admission record binding:
  - the design digest;
  - the plan digest;
  - the code commit and every module digest;
  - the split manifest digest;
  - an absolute output root;
  - for a real run, the authorization record by digest and the identity-carrying rebuild by digest.
  
  A synthetic admission runs only `synthetic_producer.py`, and that producer refuses a real
  admission. **No real admission exists, and no real N2 producer exists (§8).**

**Generic or N2-specific.** `execution.py`, `identity.py`, `members.py` and the admission pattern
serve any admitted 2D investigation unchanged. That includes a prospective transfer test or a
redesigned validation. Each would supply its own design module in place of `design.py`. Specific to
N2:

- the two arms;
- holding the MC stream;
- the T001 base rule;
- the seeds;
- the [0.80, 1.25] rule;
- `INTENDED_FOLDS` (bank and background template from training, pseudo-data from the reservoir).

`design.py` names three §16.1 gaps that the registration must settle:

- the resample seed;
- `sd` (what §16.1 writes) versus the KI-85 relative spread `sd/mean`, which differ when the arms'
  means differ;
- which fold supplies the purity background template.

## 6. Verification

### 6.1 Commands and results

All runs used one thread (`OMP_NUM_THREADS=1`) and `TMPDIR` in this session's scratch directory.
Local absolute paths in the committed logs are replaced by `<worktree>`, `<scratch>`, `<tmp>` and
`<home>`, as the closeout logs do.
`python3` is 3.12.2 (numpy 1.26.4, pytest 8.3.4, no ROOT). `python3.13` is 3.13.7 with ROOT 6.36.000
via `PYTHONPATH=$(root-config --libdir)`.

| check | command | result | log |
|---|---|---|---|
| ratchets at the pin | `inventory.py` plus the closeout log | 2 of 17 red, failure lists as recorded | [`logs/inventory-base.txt`](logs/inventory-base.txt) |
| ratchets after classification (`5e5f742b`) | `python3 -m unittest <both suites>` | exactly 1 red: the forward arm naming the two live producers | [`logs/ratchets-commitA.txt`](logs/ratchets-commitA.txt) |
| ratchets after the repair (`65c543eb`) | same | **17/17 OK**, exit 0 | [`logs/ratchets-commitB.txt`](logs/ratchets-commitB.txt) |
| ratchets at code head `df21dea7` | same, `-v` | **17/17 OK** | [`logs/ratchets-final.txt`](logs/ratchets-final.txt) |
| producer provenance | `python3.13 -m unittest discover -s …/n2 -p 'test_producer*.py' -v` | **20/20** with ROOT at `df21dea7`, 0 skipped; 9 pass + 11 skipped without ROOT | [`logs/producer-final.txt`](logs/producer-final.txt) |
| N2 harness | `python3 -m unittest discover -s …/n2 -p 'test_n2*.py' -v` | **21/21** at `df21dea7`, including a 100-member guarded synthetic campaign | [`logs/harness-final.txt`](logs/harness-final.txt) |
| KI-84 regression | `python3.13 -W error::ResourceWarning -m unittest 2d-unfolding/tests/test_bootstrap_completeness_ki84.py -v` | **15/15**, 0 skipped (lane A's post-repair count) | [`logs/ki84.txt`](logs/ki84.txt) |
| shared callers | `test_k0_5ab_separated_roots`, `test_flux_universe_fix`, `test_p4_resume_integration`, `test_fullevent_extract`, `pytest test_hash_bindings.py`, `pytest test_coverage_fixed_truth.py` | 4/4, 51/51, 50/50, 28/28, 33 passed, 20 passed. The `exit=` lines in that log are `tail`'s status; the `OK`/`passed` lines are the evidence | [`logs/shared-callers.txt`](logs/shared-callers.txt) |
| bindings, before and after | `python3 docs/orchestration/verify_hash_bindings.py` | `ALL BINDINGS INTACT` at the pin and at the head. Neither live file's digest appears anywhere in the tree, so neither is newly bound | [`logs/bindings-base.txt`](logs/bindings-base.txt), [`logs/shared-callers.txt`](logs/shared-callers.txt) |
| pre-commit hook | every commit | `13 checks passed` | — |

**What the producer tests show.** The tests use throwaway checkouts holding the real producer,
driver, toy design, guard and `n2/execution.py`, each with a **stub** helper whose factor names the
checkout that ran: A is ×2, B is ×3.

- *Control:* the toy as of the pin, run from A with B first on `PYTHONPATH`, executes **B's** helper
  (ratio 3.0) and writes no record. The fixture really hijacks.
- *Positive:* a strict, guarded run in A exits 0 with ratio **2.0** (to 12 places). It records A's
  helper path and digest, A's HEAD, no mismatched file and the input digests. The arguments the
  helper received equal the recorded `estimator` block, including `random_state` 7/8/9 for `--seed 7`.
- *Refusals (exit 3, no output file):*
  - B's helper pre-imported;
  - changed helper bytes, refused before the changed body runs (marker file absent);
  - helper bytes edited since HEAD;
  - unguarded strict run;
  - strict run with no expectations;
  - strict run with no input digest;
  - checkout with no git;
  - a script from another checkout (the guard's own refusal);
  - an overwrite attempt, after which the existing bytes are unchanged.
- *KI-85, guarded:* the producer reads through A's analyzer, and its medians equal the pure
  functions' on the same arrays to 12 places.

The harness tests run without ROOT. Their negative controls, each firing:

- missing IDs (3 forms);
- a repeated key;
- C1: a reservoir key moved into training;
- C2: a truth row dropped;
- C3: a key in both trees;
- C4: one value moved by one ulp;
- C5: a biased threshold;
- C6: a reservoir row in the bank, and a sidecar with a role missing;
- manifest tampering;
- plan edits: estimator, MC stream, base, seed, a dropped member;
- admission: no record, real with the synthetic producer, no authorization, wrong authorization
  digest, no producer digest, no rebuild, another design, another commit;
- overwrite attempts;
- a real member with the wrong thread count.

The two synthetic campaigns:

- **Positive:** 100 guarded members recover `M` ≈ 1 and **faithful**, with every record strict.
- **Broken:** T003 is contaminated, B007 fails and 94 members are never run. The result is
  **INCONCLUSIVE**, ledger 4 ok / 2 failed / 94 missing, with T003's C6 reason and B007's exit
  status. No `M` is computed.

The known-ratio unit tests separately give faithful / over-scatter / under-scatter at
`b/t` = 1.0 / 1.6 / 0.6.

### 6.2 Negative controls by mutation ([`mutation.py`](mutation.py))

Each mutant is applied in a fresh `git clone --shared` of the head. The unmutated clone must pass the
same commands first, and did. Run 1 ([`mutation-results-run1.json`](mutation-results-run1.json))
caught 18 of 19. The miss was `loader-skips-digest`: the KI-85 test still saw exit 3, but only
because `finalize` re-checked the digest **after** the mismatched analyzer body had run. The test was
strengthened (`732b75dd`), and run 2 ([`mutation-results.json`](mutation-results.json),
[`logs/mutation.txt`](logs/mutation.txt)) is the record: **19 of 19 caught**, unmutated baseline green, 326 s wall, 266 s CPU.

| mutant | must turn red |
|---|---|
| **new tracked live site** (`2d-unfolding/uq/new_live_site.py` inserting the canonical root) | **both ratchets' identity arms** — the required negative control |
| new untracked live site | the fail-open ratchet only. The AST ratchet reads `git ls-files` by design, and the probe reads the working tree |
| literal re-planted in the toy / in KI-85 (string form) | both ratchets |
| literal re-planted as `Path("…")` | the AST ratchet only. The probe's regex does not follow a pathlib binding (the `gate2_target_runtime.py` shape), which is why both instruments are kept |
| loader accepts a pre-imported module / skips the digest | pre-import and changed-bytes tests (toy, KI-85, loader) |
| strict mode skips the guard / ignores HEAD drift / allows overwrite | the matching strict tests |
| IDs allow duplicates / missing; C1 / C6 disabled | the matching identity tests, and the broken campaign for C6 |
| ledger drops `missing`; `write_new` overwrites | ledger, broken campaign, overwrite tests |
| arm B's MC stream resampled | the plan test |
| a real admission without authorization | the admission test |

## 7. Proposed patches for shared-document owners (not applied here)

**KNOWN_ISSUES row 89**, status column:

> *RESOLVED for the ratchets 2026-10-09 on `prep/next-guard-20261009` (Session 2), not yet on
> `main`.*
> - The two live producers derive their roots from `__file__` and run their code from verified bytes
>   with provenance records.
> - The seven October records are classified `frozen_record`, byte-for-byte unchanged.
> - Both suites pass 17/17. The fail-open set is 16 / `7aa29431…`; the AST set is 17, all listed.
> - A new tracked live site turns both red; an untracked one turns the fail-open suite red.
> - The hook still does not run these suites.
> - Route: `state/next-preparation-20261009/guard/REPORT.md`.

The row's consequence clause becomes: *a toy or KI-85 output written with `--require-provenance`
under `mnv_guarded_run.py` now records the executed helper's path, digest and HEAD. The existing
`sbatch_*.sh` launchers still run unguarded and must be replaced for any admitted run.*

**OPEN_ITEMS OI-136**, appended:

> *2026-10-09 (Session 2): fail-open set 18 → 16 (`7aa29431…`); AST rooted set 19 → 17, all named
> with a class; 0 unlisted. New class `frozen_record` (7 files, Goal 2 authority). The 2D arm's latency
> conditions still hold: insert in `main()`, `omnifold.py` `e96234124a31…`. Residual unchanged: the 10
> older exceptions, the `.sh` and `MNV_REPO` families, and the hook not running the ratchets.*

**Integration requirement (manifest).** `generate_manifest.py --check --at-sha` reports **OK at the
pin** and **OUT OF DATE at this branch's head**. The difference is:

- `consumer` / `inbound_count` columns of existing rows, because this lane's code and comments name
  existing records;
- new rows for the files under `Q/guard/`.

No LIVE/ARCHIVAL class changes. The integration owner must regenerate `MANIFEST.tsv` from source
after merging. This lane does not edit it, and does not change the generator or checker. The exact
delta, measured at `a5bb866d`, is in [`logs/manifest-delta.txt`](logs/manifest-delta.txt):
21 rows added (every one a `Q/guard/` file), 59 changed and 0 removed. Of the changed rows, 42
differ in `consumer` and 59 in `inbound_count`, plus the manifest's own size row. No class
column changes. Each later commit on this branch adds only its own `Q/guard/` rows.

**Guard core.** No change is needed or proposed. The guard ran unmodified in every test. The one
interaction found (it refuses a `git` child while `$GIT_EDITOR` is set) is handled in the caller by
removing `GIT_*` from git's environment.

## 8. Limitations

- **Engineering, not science.** No real input, classifier, toy, bootstrap or experiment ran. The
  stub helpers prove which code executed, not what the real helper computes.
- **No real N2 producer.** It must build experiment inputs from the R0 folds: reservoir pseudo-data
  as expanded rows, the training bank and the background template. It must run the production
  driver (`--bootstrap-streams data` for arm B), emit the C6 sidecar, and return the 205 values under
  strict provenance. It needs the R0 schema, which does not exist.
- **Production scale.** `identity.py` checks run in pure Python over tuples. At 32.8 M signal rows
  they need vectorizing (or chunked hashing) before R1. The cost is unmeasured here.
- **Residual windows.**
  - The entry script is read by the interpreter before its first statement hashes it.
  - `n2/execution.py` and the `n2` package are imported normally (bootstrap), then hashed and checked
    against HEAD and the expectations. A hostile module already in the interpreter is the guard's
    case, not this module's.
  - Third-party libraries (ROOT, numpy, LightGBM, scikit-learn) are identified by version, not by
    digest.
  - Inputs are hashed only when a digest is stated or `--hash-inputs` is given. Under the strict
    flag both producer inputs need stated digests.
- **Platform.** All tests ran on macOS with local Python. The production `root_6_28` environment,
  Perlmutter filesystems (hard links for `write_new`) and Slurm were not exercised.
- **Not touched:** the `sbatch_*.sh` launchers, the 10 older exceptions, the `.sh` and `MNV_REPO`
  families, and the hook wiring of the ratchets.

## 9. Independent review

See §11.

## 10. Resources

- **Elapsed:** active time from about 19:55Z; see §11 for the end.
- **CPU:** single-threaded throughout. The summed `user+sys` of the timed heavy commands (two
  mutation runs, ratchet suites, inventories, test suites, hash bindings) is below 0.5 core-hours.
  The final figure is in §11. Cap: 4.
- **Scratch:** this session's scratch directory, measured in §11. Cap: 2 GiB.
- **Tracked bytes added:** about 0.2 MiB including logs. Cap: 10 MiB.
- **Cluster / GPU / training:** 0.

## 11. Final head, review and measured totals

To be completed at delivery.

## 12. Disposition

**PASS** for the engineering decision. With the producers run as §13 specifies, a future 2D
diagnostic built on `fixed_truth_toy.py`, `ki85_compare.py` or the N2 harness:

- executes the checkout it was launched from;
- refuses a conflicting module, changed bytes, missing provenance, overlapping or missing event IDs
  and an overwrite before any output;
- records which implementation ran.

Both ratchets discriminate. They pass on the reasoned inventory and fail on an injected new live
site.

What this does **not** establish:

- no scientific result;
- no admission of N2;
- no transfer or coverage measurement;
- no change to KI-85, gates, the central value or the publication.

The overall publication-ready measurement remains unmet.

## 13. Next action

1. **Integration decision (Joseph, then the integration owner).**
   - Merge or decline this branch.
   - On merge, regenerate `MANIFEST.tsv` and apply §7's KI-89/OI-136 text.
   - Cost: one regeneration plus the hook.
2. **Before any admitted 2D run, whatever the experiment.** Replace the unguarded launch with the
   guarded strict form:
   ```bash
   python "$CODE/nd-unfolding/mnv_guarded_run.py" --expect-root "$CODE" --inventory "$OUT.inventory.jsonl" \
     -- "$CODE/2d-unfolding/uq/coverage_fixed_truth/fixed_truth_toy.py" <frozen args> \
     --expect "$ADMITTED/expect.json" --require-provenance --out "$OUT"
   ```
   - `$CODE` is the admitted clean checkout.
   - `expect.json` states the commit, the six executed-module digests and both input digests.
   - The launchers are outside this lane's write set.
3. **N2 specifically, only if Joseph lifts the KI-85 deferral after the stage-0 scope choice**
   (DESIGN §17):
   1. Settle the three §5 gaps.
   2. Price and run R0: 0.4–2.3 node-h (C's figure).
   3. Vectorize `identity.py` for production scale.
   4. Write and review the real N2 producer against `synthetic_producer.py`'s interface.
   5. Write the admission record.
   6. Run. 9.8–12.2 node-h including R0 and a 20 % reserve (B §16.1).
   
   None of this is authorized by this report.
4. **A transfer test or redesigned validation** reuses `execution.py`, `identity.py`, `members.py`
   and the admission pattern. Its design module (arms, statistic, rule, population construction)
   does not exist and is the next design task, not engineering.
