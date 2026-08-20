# Handoff — publication close-out orchestration, 2026-08-20T21:54Z

**What this is.** The unfinished ledger from the close-out campaign run against
`PROMPTS-20260820-publication-closeout-orchestrator.md`. Six lanes ran; what they fixed is in the
commits from `a2af2454` to this one. **This file records what is NOT done and why**, so that no item
below has to be rediscovered.

**Read the state, not this file, for current facts.** `LIVE-STATE.md` is regenerated at the commit
carrying this handoff; every blocker there now leads with its lifecycle.

---

## 0. The one thing to know first

**The publication critical path is the adopted scalar-5D covariance, and exactly one of the nine
recorded blockers is a live publication blocker** — the B1 steps 4-5 pause. Three are PET
(method-development after `OI-126`), one was ruled and closed by decision, two are discharged or
fixed, one is a corrected preservation item, one is `OI-136`. Before 2026-08-20 all nine read as
live because their corrections were appended at the end of multi-thousand-character strings. **If
you are working the blocker list top-to-bottom, stop and read the lifecycle tags.**

---

## 1. Reserved for Joseph — collected, not decided

| # | Decision | Why it is his |
|---|---|---|
| 1 | **Lift the B1 steps 4-5 pause, or route a Round 3 to lane C.** | Explicit hold; the walltime grant does not reach it. |
| 2 | **Strike or keep `\petClosure` in the external paper** (`paper_body.tex:151,179`). | Changes a published claim. |
| 3 | **The four unreproducible macros** — `\medianBinRatio` 1.006, `\binsFive` 77.6, `\binsTen` 94.1, `\binsTwenty` 98.5. | Re-deriving produces numbers; `\binsTen` prints in the paper. |
| 4 | **The negweight appendix** — 14 macros unbacked on every axis. | Quotability of live note values. |
| 5 | **`OI-136` remedy authorizations** — 6 hash-pinned sites need re-issued gates; guard subprocess propagation changes two production launchers' exit-code surface. | Frozen provenance; `OI-123` forbids re-pointing. |
| 6 | **`policy.json`'s `explicit-blocker` rule.** | Re-classifies up to 20 rows and changes the queue every session reads. |
| 7 | **`OI-137`** — whether the N-D χ² protocol gains a fifth mandated declaration. | Changes the uncertainty model. |
| 8 | **Preservation scope** — extend the HPSS quoted-set from ledger-named to note-named; `sigTwoD` is a 55,513-byte untracked ROOT on no tape. | Storage/tier judgement, per `OI-131`. |
| 9 | **`OI-58` / `OI-93` reclassification.** | Recommendations are filed in both rows; the ruling is his. |

Already-standing and untouched: `OI-71`, `OI-31`, `OI-75`, `OI-131(a)`, `OI-29`.

---

## 2. NOT DONE — with the exact reason, so nobody re-litigates it

### 2.1 `MANIFEST.tsv` is still stale, and is blocked on exactly ONE dirty file

Measured at this commit:

```
generate_manifest.py --check --committed-only
  OUT OF DATE: rows=324 ... mode=committed-only
  committed-only: 49 nonignored untracked path(s) EXCLUDED from both the table and the reference sources
  WARNING: 1 tracked path(s) in the inventory scope are DIRTY, so their lines/bytes/inbound_count
           describe the WORKING TREE, not any commit: docs/orchestration/state/sessions.json
```

**Not landable, and not for want of trying.** `sessions.json` is another session's uncommitted edit
(46,746 B committed vs 51,542 B in-tree). Regenerating would publish a transient as repository state
— `BEN-183` exactly. `--committed-only` filters the *path set*, not working-tree *bytes*, so it does
not save this one.

**What to run once `git status --porcelain -- docs/orchestration` is clean:**

```bash
/usr/bin/python3.11 docs/orchestration/generate_manifest.py --committed-only
/usr/bin/python3.11 docs/orchestration/generate_manifest.py --check --committed-only   # expect exit 0
```

Expected delta: **0 dropped, +1 row (323→324)**, ~15 changed rows, all genuine reconciliation. **If
the `WARNING:` line prints, the tree is not clean and the run is not landable.** Do **not** use the
default mode: it adds 49 foreign untracked paths and lets them move `inbound_count` on 73
already-committed rows.

Recommendation on record: adopt `--committed-only` as this shared checkout's canonical mode. Default
`--check` is red today and stays red while foreign untracked files sit in the tree.

### 2.2 `build_all.sh` cannot exit 0 on this host

All three PDFs compile and are proven written by the run. The script then dies in the containment
stage for **two** environmental reasons, **both pre-existing and neither caused by this campaign**:

1. It calls bare `python3`, which is **3.6.15** on `login19`, while `check_dead_containment.py:37` is
   `from __future__ import annotations` (needs ≥3.7).
2. **`pdftotext` exists nowhere reachable on this node** — not in `/usr/bin`, not in
   `texlive/2024/bin/x86_64-linux`, `module spider poppler` finds nothing, absent from every conda
   env. `check_dead_containment.py:158` gates the PDF half on `shutil.which("pdftotext")`, and the
   2026-08-12 contract makes that skip **fatal**.

**Why it was not fixed:** the interpreter half is patchable, but the `pdftotext` half **cannot be
fixed from the script**, so no patch demonstrates exit 0 here. And `test_build_all.py:289-290`
statically pins the literal strings `python3 check_dead_containment.py --self-test` and
`\npython3 check_dead_containment.py\n`, so script and test must move in one commit. Sketch of the
patch not applied: resolve `PY` once (`for c in python3.11 python3.12 python3; do "$c" -c
'import sys;sys.exit(sys.version_info<(3,7))' && PY=$c && break; done`), fail loudly with the
existing `FAIL python3 not found` text, substitute at both call sites, update the two assertions.
The `pdftotext` half needs a tool install or a checker change.

Substituted evidence that the containment invariant does hold: `--self-test` **PASS**; source half
**PASS** (note 30 `\dead{}` across 3 files, paper and primer each a clean 4-file closure); PDF half
reconstructed with PyMuPDF — the struck magnitudes appear **only** in `main_note.pdf`, **0** in
primer or paper.

### 2.3 `test_build_all.py` fails 11 of 18 — diagnosed, not fixed

`build_all.sh:35` runs `module load texlive/2024`, which **prepends the real texlive bin ahead of the
test's `PATH` shim**, so the fake `latexmk` is bypassed and the real one dies on the sandbox's stub
`.tex` files. Reproduced: `PATH=/usr/bin:/bin bash -c 'module load texlive/2024; command -v latexmk'`
→ the real binary. The harness is only sound where `module` is not exported into non-interactive
bash. Fix (`MODULEPATH=` or a `BUILD_ALL_SKIP_MODULE` guard) is unrelated to PET and wants §2.2
settled first.

### 2.4 The mutation probe cannot run — and a Round 3 needs it

`nd-unfolding/tests/mutation_probe_remedy_a.py:123` shells out to `sys.executable -m pytest`.
**No `pytest` exists under any interpreter here.** So `base_rc != 0` with `names=set()`, and
`main():197` prints `REFUSING TO PROBE: the unmutated suite is not green ([])` — **the empty list is
the tell**: it misattributes a missing dependency to a red suite, while the suite is in fact 70/70
green. This is the instrument that would substantiate any test-power claim in a Round 3 verdict.

**Not fixed because** porting `run_suite()` to `unittest` changes how test names are parsed and
therefore the `CAUGHT`/`UNATTRIBUTED` criterion lane C explicitly ruled on. It needs C's sign-off,
not a unilateral edit.

### 2.5 Remedy (A)'s identity check has never seen a present seed

Measured with PyROOT at HEAD: `uq_5d/unified_throw_cov_5d.root` has 9 keys and **no**
`estimator_seed` or offset pair; `..._combined_bkgaware.root` has 47 keys, **all TH2D, zero
TParameters**. Both predate the writers that stamp those keys. No `.root` under `nd-unfolding/` is
newer than 2026-08-18, and the three member namespaces hold only `res_boot_*.npz`.

**Stronger, and this is the part to carry forward: a DECLARED run would also prove nothing.** With
`off_declared=1`, `assert_legs_are_one_member` skips (`o1 is None and o2 is None`) and
`assert_seeds_match_their_baselines` `continue`s both groups (`seed is None`) — both return having
compared nothing, and the product still gets stamped `est_seed_offset=k`,
`est_seed_offset_declared=1`, `upstream_estimator_seed_{g1,g2}_checked=0`. Exercising the check
requires re-running a **producer** leg under a declared offset; it is not reachable from the adopt
path.

### 2.6 Two launcher defects specified but not applied

Both in `sbatch_finalize_5d_bkgaware_gpu.sh`, whose `:181-185` records that Joseph scoped this file
to *"those two lines only"*:

- **`:130` has no resume guard on the 41.44 GB do-not-delete artifact.** The repo idiom is
  `mr_skip_if_complete "${OUT}" && exit 0` (e.g. `sbatch_unfold_5d_detector_bkgaware_gpu.sh:86,100`);
  this launcher goes straight to `mr_run`, which invalidates any marker and re-runs. The one output
  that cannot be regenerated for under **2.087 TiB** is the one with no guard, and it carries no
  `.done` marker.
- **`--prod` is never forwarded at `:195-204`.** `adopt_unified_5d.py:79` defaults it to the
  *archive* CV while `:105-110` member-scopes `CV`, so a declared member's `median frac/bin`
  diagnostics would compare the archive's CV against the member's covariance. Diagnostic-only, and
  harmless while undeclared; live once the pause lifts.

**Lanes disagreed about one adjacent item and it is unresolved:** whether `:15`'s unconditional
`REPO=` may be changed to the overridable form. One lane called it free and no-authorization; another
called it a frozen-provenance launcher edit in a file Joseph scoped. **Not done**; treat as needing
his word.

### 2.7 `OI-136`: 58 fail-open sites remain (one pilot repaired)

Re-measured at HEAD: **122 candidates / 59 FAIL-OPEN / 13 / 50**, both probe controls holding, and
the fail-open set was **byte-identical** to `2e210468`. **ONE PILOT SITE WAS THEN REPAIRED under single-site
authorization, so the live count is now `121 / 58 / 13 / 50`** — `nd-unfolding/uq_fps/corrected/test_fps_corrected_uq.py`, provably carrying no receipt or launcher pin.
**58 is not a target; it is the number of sites still to repair, one authorized site at a time.** The only
EXECUTABLE pin of the number is `nd-unfolding/tests/test_oi136_failopen_inventory_ratchet.py`, which went
red on the repair as designed and was updated deliberately. Cross-checked by an independently written AST
classifier: same 59, zero difference.

- **6 are hash-pinned** and need a re-issued owning gate, not a refactor:
  `2d-unfolding/unfold_2d_omnifold_unbinned.py`, `nd-unfolding/adopt_unified_5d.py`,
  `pet/dump_pointcloud_inputs.py`, `pet/fullevent_fps_dataloader.py`,
  `pet/train_fullevent_nominal.py`, `pet/validate_pet_nominal_gate4.py`.
- **13 are tier A** — they already derive their own location and then insert the hardcoded root at 0
  *on top of it*, so they lose on insert **order**; a one-line change each. Two of the 13 are among
  the pinned six.
- **~39 are tier B** — never compute their own location; same edit shape, `__file__` must be
  introduced. Depth is uniform per directory. **The pilot came from this group** (it was ~40 before
  the repair), which is why the tier split below sums to 58 and not 59.
- **Do not touch** the three `probe-oi22*`/`probe-oi120c*` scripts: they are *recorded evidence
  artifacts*, and editing them destroys the correspondence between the artifact and the script that
  produced it. Re-run under `--expect-root` instead.
- **The row's proposed shared helper cannot work as described:** for a module imported by something
  else, `sys.path[0]` is the **entry script's** directory, so the helper would itself need a
  hardcoded path. One-line self-derivation per site is the workable form.
- **71** `.sh` launchers (not 286) both assign the root unconditionally and `cd` into it. Exploitable
  but catchable, unlike the `.py` route. **0** set `PYTHONPATH`, so there is no third route.
- **The guard does not cross a subprocess boundary** — so routing
  `sbatch_finalize_5d_bkgaware_gpu.sh` through it today would print a clean banner and refuse
  nothing. Order that works: free `:15` fix → pinned site via re-issued gate → then the guard, or
  teach it to propagate via a `PYTHONPATH` `sitecustomize`.

### 2.8 `OI-130` is 22% enumerated

70 of 70 `values.tex` `\newcommand` macros were swept. **That is 22% of the typeset-quantity
population.** Unswept: **249** `\SI{}`/`\num{}` uses with a *literal numeric* argument, and ~1,949
numeric literals in non-comment body text. `values.tex:5-6` states the design — numbers appearing
once are *not* macroized — so **the inline set is by construction the un-provenanced set**.

Named unread bodies: `sec_experiment.tex` (carries the selection definition), `sec_intro.tex`,
`app_landscape.tex`, `app_codebase.tex`, and the remainders of `sec_3d.tex` and `app_statmethods.tex`
(801 numeric literals alone). **A grep result for these files is evidence about the grep**, not the
files — the defect class is a correct-sounding sentence about the wrong object, which has no
distinctive string.

Counts in each state, for the 70: **26** tracked · **26** untracked sole-copy on purgeable scratch ·
**5** on scratch and HPSS · **11** recorded nowhere · **2** analytic · **1** destroyed (restored at
`feb94310`).

### 2.9 No instrument binds a quoted number to an artifact

`build_all.sh` runs only `check_dead_containment.py`, which checks `\dead{}` *containment*.
`ESTIMATOR_REGISTRY.md` is per-estimator (8 rows) with no tracked/preserved column. **This is why a
destroyed artifact went unnoticed for a day.** Proposed and not built: a tracked
`docs/analysis-note/values_provenance.tsv` (`macro | value | artifact_path | tracked | hpss_archive |
ledger_row | receipt`) plus a checker invoked from `build_all.sh` that fails when a macro has no row,
or names a path absent from both `git ls-files` and the HPSS receipt.

### 2.10 Ten macros could become artifact-backed cheaply — not done

`chiCombined`, `chiCombinedLog`, `chiCombinedSubStat`, `uqMedian`, `pullFrac`, `pullMeanAbs`,
`eavailMargin`, `fpsAbove`, `fpsAnchor`, `gbdtAiEstFrac`. Every producing script prints to stdout or
writes a PNG only. Adding `--receipt <path>.json` to `compare_to_paper_fullcov.py`,
`uq/coverage_toys.py`, `check_5d_anchors.py` and `fps_pilot_compare.py` would convert all ten for a
few hundred bytes each. Not done: running them produces artifacts that then owe ledger/RUN_LOG rows,
which is a larger job than a comment fix and touches quoted numbers.

### 2.11 Off-`main` artifacts with no discovery route

`84607aa3` removed **1,035** tracked files in a commit whose message names **none** of the four
conditions `CLAUDE.md` requires. Most removals *are* covered by `CATALOG.md`'s generic route and
per-file stubs. **Four have no route at all**, and the first two matter for `OI-7`:

- `runs/standard-p4-verifier/20260811T132822Z-packetB-final-pass.md` — **`OI-7`'s PB3/PB4 evidence**
- `runs/standard-p4-verifier/20260817T045149Z-repair12-verdict.json` — supersedes repair-11, which
  *is* on `main`
- `AUDIT-20260819-analysis-note-vs-record.md` (1,375 lines) — the only prior enumeration of the 70
- `state/hpss-residency-inventory-20260812.json`

Partly repaired at `feb94310`: the six unfetchable `evidence/*` tags are fetched and the route is
documented, so these are now *resolvable*. Giving them a **routed** citation is still owed.

### 2.12 Smaller items, each measured and left

- **`verify_hash_bindings.py` already exits 1 at HEAD**, independently of this campaign:
  `RECEIPT_BINDING_COUNT`/`_SHA256` declare **117 / `7586d636…`**, observed is **119 / `cb5df0b8…`**.
  One extra row traces to `nd-unfolding/active_universe_5d/fps/covariance/fps_publication_pass_receipt.json`.
  **No completed real run was obtained all session** — it sha256's every localized bound product and
  at one point nine concurrent instances were saturating login-node I/O.
- **`.githooks/pre-commit` is inert and would fail if enabled.** It invokes bare `python3` (3.6.15),
  so **7 of its 12 checks are `SyntaxError`**. `core.hooksPath` is unset so it bites nobody today —
  but a lane following the documented enable instruction would fail every commit, and the natural
  response is `--no-verify`, which is exactly what its header was written to prevent.
- **13 LIVE docs remain absent from `CATALOG.md`**, reported by `live_doc_indexed.py --check` and
  **not enforced**. The 6 that open items cite were added at this commit; the rest are not routed to
  by any open item.
- **`OI-128` first residual declined**, cascade measured: `STANDARD_P4_ENTRYPOINTS`'s own comment is
  *"what the driver actually invokes"* and the adopter is never invoked (it prints *"would
  promote"*). Adding it would make a true comment false. Surface is **21** paths, not 20. One-line
  diff available if wanted; it needs `test_p4_token_gate_scope_and_rev.py:420`'s `18` pin
  re-measured in the same change.
- **`OI-129`'s recorded blocker is already spent** — repair-11's PASS already fails rules 4b **and**
  4c at HEAD over six surface files, so an in-scope edit costs nothing not already spent.
- **`INTEGRATION_CHECKLIST.md:233`** still lists the pull mean/RMS three-way inconsistency as
  unresolved. It is resolved: three *different* covariances. `0.089/0.598` is best-sourced
  (`receipt_model_chi2_2d.json:196-197`); `0.069/0.466` is struck; the **ledger's own**
  `0.051/0.409` (`VALIDATION_LEDGER.md:1460`) is the pair with **no artifact** — its PNG was
  overwritten 2026-07-16.
- **`values.tex:75-79`** defines five PET uncertainty magnitudes commented `QUARANTINED` and
  **used zero times** in any build. Inert; retiring them is a shared-layer numbers change.

---

## 3. Traps this campaign hit, for the next session

- **A view can be false while its source is right.** `AGENTS.md` said the phrase
  "bootstrap-centering/bias" was *"not part of the ruling and may not be quoted as Joseph's."* It **is**
  in his verbatim ruling; what may not be quoted as his is that phrase **as a determined cause**.
  `live-state.json` kept the qualifier; the front door dropped it. Fixed at `a2af2454`.
- **Corrections appended to the end of a long field do not get read.** Five of nine blockers were
  already superseded in their own tails. Put the lifecycle first.
- **This checkout is shared and moves under you.** Two lanes' before/after test windows were
  contaminated by each other. Both resolved it by attributing failures **by name**, not by count —
  do that.
- **A wrapper's exit code is not its payload's.** `sacct` reports job `57287380` **FAILED** while the
  verify passed 36/36; the last command was `grep -v`, which exits 1 precisely when everything
  passes. Read the tool's own rc.
- **Check the object before the arithmetic.** A `−0.660` Hartlap factor and its `+0.309` replacement
  were both withdrawn as type mismatches (rank vs ensemble size; bin count vs draw count).
  A sample covariance over `N` draws has rank ≤ `N−1` — that identity settles such questions fast.
- **`git fetch github` cannot fetch the tags that matter.** See `CATALOG.md`'s new section.

---

## 4. Standing authorizations, unchanged

Any single Slurm job **under 12 h walltime is pre-approved** — launch it, do not ask. Commit and push
are permitted, including to `main`; never force-push, never rewrite pushed history, never
`git stash` bare (the stack is shared across worktrees). **The grant is about walltime and nothing
else:** a short job under an explicit hold is still refused and the hold wins. Independently **not**
authorized regardless of walltime: the 151 A100-h M(ii) family, `C_ML` construction, lifting the B1
pause, and anything moving a central estimator, an uncertainty model, or a published claim.

**Capacity, re-measured 2026-08-20:** codex-school **17.0%** weekly (resets `2026-08-25T12:45Z`),
codex-personal **46.0%** (resets `2026-08-27T05:54Z`), **0** reset credits. claude-school 5-hour
**77.0%**; **its 7-day window reads `stale`/unknown** — do not assume it. `claude-school` and
`claude-school-legacy` are ONE account; never sum the aliases.
