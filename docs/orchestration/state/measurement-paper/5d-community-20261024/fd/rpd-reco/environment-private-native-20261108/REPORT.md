# RPD-RECO: private prepares and native environment boundaries

The code separates a private exact-value environment comparison from its committable diagnostics, and compares the environment at defined points around ROOT initialization. The frozen verification head is `c3c1330f834e6d68e4d100be510de88092c638e2`; SOURCE-IDENTITIES.json binds the exact production, instrument and test bytes at this head, including the two reused input instruments. The prior main merge adds the canonical platform and pymon evidence without changing the executable files.

C1 and C2 were closed by the [independent round-1 review](https://github.com/josephbaileyy/MINERvA-OmniFold/pull/848#issuecomment-6717323539) at `2ed446b4`, tested at `91dbf0a7`. That review reproduced 185 tests, the 185-test comment-only control, and 175 killed mutants. It also corrects the earlier X17 KeyError claim: the existing required-field set already refused a legacy prepare with MAT_PREPARE_PRESENT. The held low findings remain held. This delta answers C3 and the subsequently measured round-2 environment refusal; it does not claim native-platform readiness.

The ROOT Python citation is corrected to raw-file lines 14–20 (assignments at 14, 17 and 20); the pinned file bytes are unchanged. The 226/195 outputs below remain the original verification at the stated head. The [subsequent round-2 audit](https://github.com/josephbaileyy/MINERvA-OmniFold/pull/848#issuecomment-6718925944) is NO-GO on the added/missing import-pin test paths and that citation; the follow-up repair adds those test paths without changing production predicates.

## C3: enforce the private-prepare boundary

Both prepare paths write their canonical JSON to an owner-only sibling directory outside the run: `.rpd-private/<run-and-connect-identity>/<prepare-name>.json`. The leaf directory is 0700 and the canonical file is 0600. The writer refuses CFS and protected-root overlap before creating a private directory or file. The reader checks the file and directory ownership/permissions, the exact location and run identity, the public reference digest, and the canonical digest. It reads the canonical JSON directly; Inputs stages only the public reference, never the fingerprints.

The run contains a digest-pinned `prestage-reference.json` or `prologue-prepare-reference.json`. After the worker comparison, the prologue itself writes the public prepare view and its PASS or STOP comparison status. For every credential-redacted key, exported records contain only the key name, presence on each side, and equal/changed. They contain no value or value fingerprint. Fingerprint maps are removed throughout the export. Worker STOP JSON, stderr and exported environment diagnostics pass through this boundary. Public module origins are a list of module-name components and source-path pairs; joining the name components with a dot exactly reconstructs the qualified module name, preserving the information without treating a module name such as nersc_pymon.log as a file citation.

The trace policy admits only the exact canonical private file, under its own class. It grants no directory-prefix permission. Protected-root attempts still refuse first, including a protected path also listed as private metadata. A neighbouring or child path is unclassified and refuses.

Four actual-worker cases cover equal, changed, added and removed credentials, plus a credential-bearing URL. They scan every file in the run, stdout, stderr and exported diagnostics for the synthetic secrets and their SHA-256 fingerprints, and assert the exact presence/change metadata. Both real prepare writers and Inputs are exercised. Negative tests cover CFS, protected roots, permissions, reference/raw digests and relocation. REQUIRED_PRIVATE_PREPARE_LEAK and five single-site boundary/digest mutants must be killed. The module-origin test also round-trips qualified names and applies the unchanged receipt checker to prove they create no bare artifact tokens. The leak fixture uses a synthetic process mapping so an intentionally failing mutant cannot serialize host credential fingerprints into its transcript.

Retention: limitation-resolver, as the run executor, owns deletion of the canonical private record after all same-connect workers have finished and the filtered receipt has been committed. Until then, the canonical file stays in its original private location and is not copied or staged elsewhere. Deletion uses the exact reference path and digest, records the measured outcome in a deletion ledger row, and never removes another run's sibling directory. The existing [raw-prepare deletion ledger](../prologue3-20261108/delete-copies/row1-dev-shm-raw-prepare/ledger.json) gives the campaign's ledger form; this report does not claim a future deletion occurred or authorize this lane to contact the cluster.

## Round 2: measured input and source evidence

The [third prologue receipt](https://github.com/josephbaileyy/MINERvA-OmniFold/pull/919), merged at `e907ae34624230fbdab122832d25b10b42eb107a`, records MAT_PREPARE_ENVIRONMENT in `run/prologue-worker.STOP.json`: NERSC_PYMON_UUID and ROOTSYS changed; CLING_PREBUILT_MODULE_PATH was added. Run, connect identity and age passed; record_display_diff was empty. The key table records 355 equal, two changed, one added, no removed and `_` excluded. These are measurements of that run, not predictions for the repaired code.

The UUID exclusion is justified by the committed [pymon source receipt](../pymon-fetch-20261107/README.txt) at `d0d4cfd5`: copies/sitecustomize__init__.py.txt:9–11 constructs PyMon at interpreter start; copies/nersc_pymon__init__.py.txt:128 draws uuid4, and :150–151 retains the inherited value only as parent_uuid before overwriting NERSC_PYMON_UUID. The cross-process comparison now excludes exactly `_` and NERSC_PYMON_UUID. The non-protected family oracle uses another NERSC_* key so a blanket NERSC_* filter still fails. No loader, ROOT, cling or CPPYY key is excluded.

The platform record reports ROOT 6.28/12. The relevant upstream source is v6-28-12:

| Effect | Primary source |
| --- | --- |
| ROOTSYS derives from the resolved libCore location | [TUnixSystem.cxx:453–460](https://github.com/root-project/root/blob/v6-28-12/core/unix/src/TUnixSystem.cxx#L453-L460) |
| CLING_PREBUILT_MODULE_PATH is built and assigned during interpreter initialization | [TCling.cxx:1468–1480](https://github.com/root-project/root/blob/v6-28-12/core/metacling/src/TCling.cxx#L1468-L1480) |
| CLING_STANDARD_PCH, CPPYY_API_PATH and CPPYY_NO_ROOT_FILTER are assigned their fixed values | [ROOT/__init__.py:14–20](https://github.com/root-project/root/blob/v6-28-12/bindings/pyroot/pythonizations/python/ROOT/__init__.py#L14-L20) |

A local libc.setenv probe demonstrates that Python's os.environ can retain its old value while an implicitly launched child inherits the new native value; an explicit environment mapping preserves the declared launch value. NATIVE-ENVIRONMENT-PROBE.json records only a disposable probe key. Python [documents the cached mapping](https://docs.python.org/3.11/library/os.html#os.environ). The source and probe establish the mechanism and motivate the boundary; they do not replace a new native MAT prologue measurement.

## Round 2: implementation and refusing conditions

Prepare captures the native environment before any ROOT check. The parent captures the pre-ROOT native launch mapping and explicitly passes it as `env=` to its traced child; it does not clear or selectively rewrite the setup environment. The worker's first comparison happens before ROOT import. Native snapshots read libc's current `environ` through ctypes; they do not rely on Python's cached mapping or on /proc/self/environ's initial exec contents.

The worker records the entire pre-to-post-initialization diff. Its allowed effects are exactly five keys, with checked values:

- CLING_STANDARD_PCH = `none`, CPPYY_API_PATH = `none`, CPPYY_NO_ROOT_FILTER = `1`.
- ROOTSYS equals the realpath of its pre-import value. If previously absent, its absence is recorded and the post value must name an existing directory.
- CLING_PREBUILT_MODULE_PATH may be added or changed, and its value is recorded.

A removal or any other changed/added key refuses MAT_IMPORT_ENVIRONMENT with its diff. The allow-list is scoped to initialization. After initialization, each context retains a native baseline; the final flux_extract recheck compares every native key with **zero exclusions**, then repeats the existing mapped-library/stat/digest checks. A later native ROOTSYS, cling, arbitrary-key or NERSC_PYMON_UUID change refuses MAT_RUNTIME_ENVIRONMENT. The UUID exemption applies only across interpreter starts.

Tests exercise a mutating import, actual libc.setenv after the native snapshot, implicit versus explicit child inheritance, realpath aliases, absent ROOTSYS, the three pinned values, an unreviewed sixth key, and removal of the prebuilt-module path. REQUIRED mutants cover taking the worker snapshot after import, using Python's copy for native reads, allowing a sixth import key, bypassing ROOTSYS validation, dropping each fixed-value check, dropping env=, excluding the runtime UUID, and adding ROOT/cling exclusions. All earlier guard, custody and scientific mutants remain required.

## Scope and next gate

Owner: Codex2 for this bounded code repair and local tests; independent reviewer: coverage-5b-audit; native executor: limitation-resolver. The decision is whether the enforced privacy and environment boundaries satisfy the requested delta. The terminal condition is committed exact-head suite/harness receipts and the delta review; the review budget is this requested round and concrete findings. No held low is silently closed.

SCIENTIFIC-AST-CHECK.json compares with `2ed446b4`: only Inputs.__init__, check_prepare_receipt and checked_prepared_mat change among existing producer functions; load_custody_instrument is added. The other 78 functions/methods are AST-identical. RNG, aggregate, scientific readings, per-step pricing, numerical classification and resource limits are unchanged.

After audit GO, limitation-resolver repeats the data-free prologue. That measurement must pass the environment guard and reach the trace classifier; the real MnvH1D shutdown check and full flux connect retain their separate gates. The production config remains DRAFT. No cluster connection, production analysis input read or campaign compute was performed in this authoring lane.

## Local verification

At the frozen head the suite printed **226 passed in 162.68s**, the comment-only custody control printed **226 passed in 162.57s**, and the harness printed **195 required, 195 executed, 195 killed, complete/all_killed true**. All returned 0; every mutant pytest returned 1 through a test failure, with no collection errors. Black, Ruff, strict production typing and both shell syntax checks passed at that head. The source commits passed 21 repository checks. Source identities were unchanged before and after each run. A scan of the raw report found no actual host credential value or fingerprint. These checks establish local refusal/privacy behavior; the native MAT prologue remains the next measurement.
