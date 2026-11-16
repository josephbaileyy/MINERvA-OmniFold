# RPD-RECO: startup, custody coverage and real-class reader repair

This is the repair of audit C1–C3 at #848 receipt head `338a1bcb` (code `d9740563`) and the real-platform crash reported in #863. The audit verdict is NO-GO, and the standalone real-MnvH1D check exited 129 without a passing receipt. Those outcomes supersede any code-readiness inference from the earlier local test counts. Their verbatim reports are `AUDIT-C1-C3.txt` and `PLATFORM-CRASH-PR863.txt`.

Owner: Codex2, code and local fixtures. Independent reviewer: coverage-5b-audit. Platform executor: limitation-resolver. The director retains the execution and merge decisions. This round answers whether the startup and custody guards act as specified, and prepares a candidate ownership repair for the native crash. Its local terminal condition is passing tests, behaviour-sensitive required mutants, committed receipts and a new #848 head. The review budget is the requested consolidated repair/re-audit round and concrete findings. No cluster contact or scientific production runs are part of this lane.

## Dictionary load and mapped objects

The traced check now calls GetClass for MnvH1D before reading mapped files, matching the existing instrument's order. The new test models lazy mapping only after GetClass, invokes the real `mat_env_problems` against local instrument fixtures, and uses actual filesystem dev/inode/size. It fires on a changed size or inode and on an altered staged instrument. Named guards separate MAT_MAPPED_STAT from MAT_INSTRUMENT_DIGEST.

The dictionary/map order, mapped-stat loop, staged-instrument digest and constructor input selection each have a required mutant and a firing test. The former empty-map/empty-stat metadata test is retained only for its receipt identity cases; it is not the evidence for mapped-code validation.

## Instrument directory scans

An exact pinned path takes precedence over prefix classes, including a symlink whose resolved target is pinned. Reviewed instrument directories admit their directory listings and non-pinned dictionary/rootmap/header files as `instrument_directory`; they do not acquire a pinned label. Python sys.path entries admit directory listing opens as `python_directory`; that class alone does not admit reading arbitrary files in those directories. The policy records these paths, and the revised DRAFT config names separate instrument-directory fields.

A non-pinned instrument shared library mapped into the process refuses. The mapped checks run before the extract and again after ROOT has read objects and could have autoloaded more dictionaries. Reading a rootmap does not authorize mapping its library. Protected-original attempts, unknown or ambiguous successful opens, failed nonprotected searches and cwd/relative-path rules retain their prior meaning. No protected-root exception is added.

The new data-free prologue command checks the pinned setup/environment untraced, builds the drafted policy, and traces a fresh child through interpreter/module startup and GetClass. It opens no declared data in its local audit-hook test. The platform silent-direction trace is still required: no local protocol fixture establishes that the drafted classes admit the real Perlmutter environment.

## Behaviour-sensitive guard coverage

The custody require function now attaches a guard name at each reported gap: MAT_INVENTORY, STAGE_SOURCE_STAT, NATIVE_SELECTION, RUN_PROTECTED_OVERLAP, NEGATIVE_EXPECTED_GUARD, TRACE_EXTRACT_IDENTITY and PREPARE_FENCE. The fence call itself has an additional required mutant; its firing test verifies that prepare stages no originals when the fence refuses.

Each custody variant is placed beside an unchanged producer under canonical module names. Fixture receipt hashes bind that selected variant, so an unrelated FLUX_CUSTODY hash refusal cannot kill it first. A comment-only custody variant runs the full suite as a control before the full mutation run. Named custody mutations must change exactly one site. The output identifies the selected tests and captures their failures. The previous ten untested sites are represented explicitly; additional required mutants cover exact-pin precedence, non-pinned mappings, directory ownership, proxy release and worker exit. <!-- absence-ok: This describes the ten code-coverage gaps identified in the preserved audit C3, not absence of a scientific result. -->

## Candidate repair for TFile::Close

The reader disables TH1 auto-directory registration while streaming, detaches the nominal MnvH1D, assigns its Python ownership, copies CV values/errors/edges to plain arrays, and releases the histogram proxy before closing the file. The previous directory-registration flag is restored even on a Python refusal. The same registration context encloses the MAT constructor and its native file reads. Metadata readers also release object proxies before file close.

The real-class probe no longer clones MnvH1D objects with error-band ownership. It records ROOT evaluations on the real object before close, reconstructs a plain ROOT TH1 CV witness from the copied bins, and compares the values after the real file has closed. Its interpolation/boundary/zero fixtures then use detached plain ROOT histograms. The production per-row evaluation still calls ROOT on MAT's constrained histograms.

This follows ROOT's documented ownership model ([ROOT object ownership](https://root.cern.ch/manual/object_ownership/), [ROOT ownership guide](https://root.cern/root/html534/guides/users-guide/ObjectOwnership.html)); [MAT's `MnvH1D` destructor at `35097b65`](https://github.com/MinervaExpt/MAT/blob/35097b65ab1680db8058f9ede18fecffdc3a1ea3/PlotUtils/MnvH1D.cxx) deletes its owned error bands. This is an ownership-focused candidate repair, not a determined cause or a verified native fix.

The probe now runs in a child process. The parent publishes real-mnv-check.json only if the child exits normally after ROOT teardown and its worker record passes. A worker crash cannot leave a final PASS receipt, even if it wrote an intermediate worker result. stdout/stderr are retained. Local weak-reference and flag-state tests establish release-before-close and restoration in the Python protocol; only the required platform run can establish real MnvH1D clean close.

## Platform order and commands

After the delta audit's GO, limitation-resolver runs the data-free prologue first. The draft policy's runtime paths must be resolved and reviewed; physics/source-premise fields can remain DRAFT for this data-free check. MAT_PYTHON is the measured root_6_28 interpreter, and all run paths are own local/scratch directories. The shell wrappers check the pinned setup scripts before sourcing, preserve the setup route and re-export TMPDIR.

Run the data-free trace in the checked MAT environment through the wrapper:

```sh
bash "$CHECKOUT/nd-unfolding/fd_rpd_reco_prologue_connect.sh" \
  "$CHECKOUT" "$DRAFT_POLICY_CONFIG" "$CONFIG_SHA" "$PROLOGUE_RUN" "$MAT_PYTHON"
```

After that trace passes, run the real-class check within a separately checked and sourced instance of the same pinned MAT environment. The wrapper above sets a child-local environment; it does not activate the caller's shell:

```sh
nice -n 19 "$MAT_PYTHON" "$CHECKOUT/nd-unfolding/tests/fd_rpd_reco_mat_check.py" \
  --probe "$CHECKOUT/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/timing-20261106/flux-gen2thin-pdg-14-minervame1M_rearrangedUniverses.root" \
  --run "$PROBE_RUN"
```

These commands supply no permission for the full flux connect. That stays held until the re-audit, the ordered platform results and the director's go. The production config remains DRAFT. P-F, A1's factor, background bracket, RNG, streams, readings and licences are unchanged.

## Local verification

At frozen code head `4ea4a113f72f32465f2a8c4eddd7bbaa2db5683c`, the suite printed **153 passed in 367.98s**, the full comment-only custody control printed **153 passed in 366.54s**, and the harness printed **149 required, 149 executed, 149 killed, complete/all_killed true** (all exit 0). Black, Ruff, strict mypy and both shell syntax checks passed. The code-head record-checks CI also passed. `VERIFICATION.json`, `SOURCE-IDENTITIES.json`, `C3-SINGLE-SITE-COVERAGE.json`, the exact runner outputs and their digests bind those measurements. They measure local fixtures only. Native Linux atime preservation, the real silent-direction trace, real MnvH1D close/teardown and the full constructor/cold-data closure remain unverified here.
