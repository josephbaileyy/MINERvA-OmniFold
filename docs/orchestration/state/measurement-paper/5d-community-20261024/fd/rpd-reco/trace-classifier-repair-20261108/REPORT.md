# RPD-RECO trace classifier and mapped platform code

The [fourth native prologue receipt](../prologue4-20261108/README.txt), merged in #929 at `68a36cf8`, records a passing environment guard and C3 boundary, followed by 146 classifier violations. These comprise 67 unjoined split calls, 77 successful opens that were unclassified or ambiguous, and two clone-directory changes. It does not establish full-connect readiness. This repair is tested at `477d51ead59943af7286ddee3258814f846fa865`; the implementation commit is `d1675b172`, followed by a main merge that makes the canonical trace recoverable from this branch.

## Pairing and evidence retention

Unfinished/resumed calls are joined by PID and syscall name. Each result retains its original lines and one-based line numbers. Missing halves, a duplicate unfinished call, a mismatched syscall name or an unresolved result STOP. Non-call strace lines remain in the record; a final accounting check covers every input line. The three fixture cuts are byte-exact extracts of the committed 446,312-byte trace, whose SHA-256 is `e925be68626e21f88d8ffb2dc5a2295bfe1b3047a00450b4a843ef307105d4ad`. Their source line lists and digests are checked against the original git object.

REQUIRED_TRACE_UNFINISHED_RETAINED drops a pending call into metadata, and REQUIRED_TRACE_PAIRS_SAME_PID joins a resumption to a different pending PID. The tests require an EOF STOP and exact PID/path/raw-line associations, respectively. Orphan, wrong-name and duplicate cases also refuse.

## Disjoint classes and declared platform roots

The policy excludes the run, clone, staged data, reviewed environment/platform/instrument directories and the private prepare file from the system class. Environment excludes the run and the more specific roots; run excludes staged data. Exact pinned code, private prepare, instrument-directory scans and exact Python directory listings keep their explicit classes. The generic double-match refusal remains. The tests exercise run references, staged instrument files, staged data, declared clone source and cache files under `/dev/shm`, and still refuse an unknown clone file and an intentionally ambiguous policy.

The new DRAFT config declares eight platform namespaces with reasons: Cray PE, OVIS/LDMS, NVIDIA HPC, NERSC pymon, nerscjson_client, SSS cache, Darshan and libfabric. Darshan's requested prefix and the descriptor's resolved prefix come from committed trace line 1625; libfabric's versioned lib64 prefix comes from line 1632. The RooUnfold build directory is added to the existing instrument-directory class for rootmap scans. Directory and non-library opens are recorded. This config changes no flux selection, P-F premise, scientific gate, resource request or other unresolved runtime slot.

## Platform library pins

Prepare records every executable file mapping under those platform roots, using the native executable-map permissions rather than a filename-suffix assumption. It pins canonical path, SHA-256, device/inode, size and mtime. The worker requires exactly the same executable mapped paths, then compares every pin and verifies mapped device/inode against the file. New, missing, inconsistent, unavailable, changed or unpinned platform mappings STOP with expected and observed records. Non-executable mappings such as the SSS passwd cache are descriptive and do not become library pins. Existing non-pinned mapped MAT/instrument libraries still refuse.

**Only these mapped platform instrument libraries use ordinary digest reads.** The loader already reads this code plainly; its atime is not custody evidence. A protected-root check runs before any file stat/hash in this path. Tests prove a protected path never reaches the ordinary reader, both at prepare and worker, and verify changes in SHA, inode, size, mtime, mapped identity and read-time stability. Data, source and other protected inputs retain O_NOATIME and the no-original-open trace rule. Both prepare entry points and the production checked_prepared_mat path are tested; an empty fixture pin set cannot conceal a skipped pin call.

## Cwd and public STOP records

The prologue and the missing-dependency child launch with cwd fixed to the source clone before strace starts. The wrappers already cd there before prepare. ROOT's two exact-clone chdir calls remain allowed and recorded; another path or unresolved fchdir refuses. The missing-dependency child's environment inheritance remains the held low, unchanged.

A classifier refusal writes `data-free-trace.STOP.json` (or the corresponding extraction/negative-check record) before propagating the error. It carries every violation's class, path, PID and original raw lines, plus policy/trace/prepare/producer provenance. Writing uses the existing public export function, strips fingerprint maps, and checks CFS before output. The actual prologue main path is tested through STOP, including the complete record and visible stderr. No production fingerprint export or environment exclusion is added.

## Preserved boundaries and verification

PRODUCTION-SCOPE-CHECK.json compares existing functions with `6a287e1a`. Only the named launch, classifier, policy and platform-custody functions change. All scientific functions, RNG/streams, aggregation, readings, pricing, environment comparison/import whitelist and C3 privacy functions remain AST-identical. Both shell wrappers, the reused MAT instrument and the real-MnvH1D shutdown test keep their bytes. The held lows R01, R12, R18 and R22 are not repaired here.

The suite printed **270 passed in 169.63s**; the full comment-only custody control printed **270 passed in 170.64s**; the harness printed **217 required, 217 executed, 217 killed, complete/all_killed true**. All runners returned 0. Every mutant pytest returned 1 through test failure with no collection errors. All earlier 196 REQUIRED mutants remain; the 21 new ones cover split-call evidence/pairing, disjoint classes, platform pins and guards, child cwd and public STOP writing. Formatting, lint, strict production typing and both shell syntax checks passed. Before/after source hashes match throughout verification; raw runner transcripts are preserved, with reversible receipt annotations only.

The offline full-trace replay uses the production policy builder and yields zero violations over 2,709 lines, all 67 joined calls and both declared-clone chdir calls. It supplies the observed Darshan symlink target because the local machine cannot resolve it. This is classifier evidence only: **it establishes neither native platform pin equality nor a production GO**.

Owner: Codex2 for the bounded local repair; independent reviewer: coverage-5b-audit; native executor: limitation-resolver. The decision is whether the requested classifier/custody defects are closed. Terminal condition: this exact-head packet and delta audit. Review budget: this repair and concrete findings; no speculative redesign. No cluster contact or production compute occurred in this lane.

The config stays DRAFT. After audit GO and the run-lane release, prologue rerun 5 must pass the environment and platform-pin guards and the classifier. The native executor resolves all draft policy slots, including the eight reviewed platform roots, and runs:

```sh
bash "$CHECKOUT/nd-unfolding/fd_rpd_reco_prologue_connect.sh" \
  "$CHECKOUT" "$DRAFT_POLICY_CONFIG" "$CONFIG_SHA" "$PROLOGUE_RUN" "$MAT_PYTHON"
```

The real-MnvH1D check and full flux-connect gates remain separate. Private canonical prepare retention is unchanged: the native executor keeps it only in the owner-only sibling directory, copies it nowhere else, then deletes it after committing the redacted receipt under the usual deletion-ledger row.

## Historical trace bindings

The first receipt-commit hook found one extra live binding: the same historical trace was referenced by the fixture manifest, the draft config's evidence metadata and TRACE-EVIDENCE.json without the verifier's canonical `revision` field. All three now explicitly pin `68a36cf8`, and each trace digest was rechecked through `git show` at that revision. The verifier and its binding-inventory constants are unchanged. These metadata-only additions change no runtime policy, fixture bytes, executable, test or harness. SOURCE-IDENTITIES.json retains exact identities at the tested source head and separately records the metadata follow-up. The trace-provenance/replay tests and hash-binding check were repeated for this correction.
