<!-- absence-ok: a reader's verbatim report or the dispositions of one; its "absent", "no" and "never" describe code under review, not a claim that a result does not exist -->

The first finding below is the one most likely to stop a correct run. I did not read the test files in full or the rest of DELTA.patch (I read only the head files). I did not run anything, because this is a read-only review on macOS.

My confidence in Linux, strace, GENIE and ROOT facts:
- **High:**
  - `-q` keeps the `+++ exited` lines; `-qq` removes them.
  - `/proc/self/fd/N` is a magic link that `O_NOFOLLOW` refuses.
  - strace prints path arguments in full, so `-s` doesn't truncate them (about 80%).
  - gevgen's `--message-thresholds` file is opened through libxml2 (about 85%).
- **Medium:** ROOT's `TFile` RECREATE unlinks the file and then creates it with `O_EXCL`, so the output rule works. I could not recall this exactly.
- **Low to medium:**
  - What gspl2root instantiates.
  - Whether the first existing path of GENIE's search order is the one GENIE actually reads.
  - How often the larsoft repo's revision changes.
  - Whether ROOT stores the run number in the gst file.

FINDINGS
1. [blocker] pg_generate.sh:174, 236; pg_replay.sh:149, 164, 189; pg_verify.py:462,479 — The coverage run passes `--message-thresholds W/out/Messenger_pg.xml`, and nothing pins that file for trace-check. `tcheck` pins only `${T}_CH.xml.gz`, the CVMFS spline and README, and the system tools. The file is a `.xml`, so it counts as gated, and it is under W, so it has no manifest entry. libxml2 opens it, so the trace shows a read with no pin and trace-check records `gated-mismatch`. — Every coverage trace check STOPs on a correct run: slot 1 in B3, then both slots in pg_generate. The stub trace in `test_gntpc_and_coverage_roles` never opens the file, and I found no test that does. — Pass `--w-pin "$O/Messenger_pg.xml=<MESSENGER_SHA256>"` for the coverage role only, so the sealed role still rejects it. Add a real-shape test whose coverage trace opens that path.

2. [major] pg_verify.py:504-540 (`role in graphs, gevgen, coverage`) — Every defining file (`master_config`, `ModelConfiguration`, the tune generator list, the ccqe and 2p2h registries) must be read by the initial process, and this is applied to `graphs` too. gspl2root parses splines and probably doesn't configure algorithms, so those files may never be opened. — `defining-not-opened` STOPs the pre-generation graphs check on a correct run, for both slots. — Confirm what gspl2root reads on the node, and use a smaller defining set for `graphs`.

3. [major] pg_verify.py:419-421 — A successful execve whose path can't be resolved is skipped (`not e["abs"]: continue`), not failed. This happens for a relative exec after any chdir, for an exec relative to a dirfd, or when `..` resolution failed (that last case does add its own problem). `watched()` is false for names like `./helper`, so nothing else catches it either. — This breaks D1's rule that every successful exec is bound. A helper started by a relative path after a chdir passes. — For execve, treat `abs is None` as `exec-unresolved`. `execveat` isn't in TRACE_SET at all (fexecve uses it), so add it.

4. [major] pg_lib.py:212-238 and pg_replay.sh:85-98 — The leak scan and the B3 `holds_public_seed` flag look only for ASCII decimal and hex. ROOT stores integers as big-endian binary, inside zlib-compressed baskets. A run number in a gst or flux file is invisible to this scan, so `holds_public_seed: false` is not evidence. Under the compression it can't be seen even with other encodings. — The outcome the rule exists for goes unchecked: a seed leaves W inside `genie_v3.gst.root`, `input-flux.root` or an npz file. — Read the published ROOT files back with ROOT or uproot, and check every key, title, header and branch value against the seeds. Run that on the public-seed B3 files as the real control. Say plainly that the byte scan can't see compressed content.

5. [minor] pg_generate.sh:127 against RULINGS-A2.md:128-129 (D6) — The rule says a survivor still alive 30 s after SIGKILL is a STOP. The code waits `sleep 15`. — The code and the ruling disagree. — Make it 30, or have the director amend the ruling.

6. [minor] pg_generate.sh:107-128 — `survivors` SIGKILLs any live process whose cwd is under W, and the only exclusions are this shell and the scan's own subshell. If cov2d's launcher or a wrapper has chdir'd into W, it is killed and a good run ends. The rules don't say who owns cwd W. — The harness could be killed after a good run. — Exclude the parent chain (`$PPID` and its ancestors), or match only processes started after the script began.

7. [minor] pg_generate.sh:265-270 and pg_verify.py:818-826 — The CVMFS `revision` and `root_hash` must match at the start and end of an 85 minute or longer run. Larsoft publishes regularly, and a client refreshing its catalog bumps both. — A correct run STOPs after all the generation. The content is already sha-pinned, so this rule adds operational risk without much evidence value. — Compare the hashes of the files read, or pin the catalog, or accept a revision bump when every used file's hash is unchanged.

8. [minor] pg_verify.py:261, 505-526 — `cfg_root` is the whole `config/` tree, and the first-existing-path rule applies to every `.xml` read under it. A tune-subdirectory file read by explicit path, whose basename also exists at the top level, would be compared with the wrong path. — False `search-order` STOP, at about 50% confidence. — Apply the rule only to reads GENIE makes through its search, or to basenames absent from the defining set.

9. [minor] pg_generate.sh:172, pg_replay.sh:147 — `--rc 0` is hard-coded, so `strace-rc` can never fire. The real exit status is enforced only by `set -e` in run_gevgen_v3.sh. The `trace-check` rule for strace's exit code is therefore decorative. — This is fine today but fragile. — Write the exit status to a file and pass it.

10. [minor] pg_generate.sh:55-56, 239 — A coverage run that writes any extra file STOPs, because `ls -A "$C"` must equal `coverage.trace`. Any file other than the four listed (gevgen log, ghep, status, input-flux) STOPs a correct run. — Possible false STOP, to be learned in B3. — List the unexpected name in the STOP message, with no file contents.

11. [minor] pg_verify.py:383-400 — A trace-check failure writes W paths into `trace_check.json`, including `gated-mismatch: <path>`. `trace_check.json` is not in SEED_BEARING. — If a failed task's path holds the seed (`gntp.<seed>.ghep.root` is not gated, but the `genie-mcjob-<seed>.status` name contains "genie"), a seed lands in a file that STOP-time collection might treat as outgoing. The publish scan catches it only on success. — Add `out/work/u*/t*/trace_check*.json` to SEED_BEARING, or strip W-relative names from problem text.

Rules that are wrong or weak:
- **D2's revision equality:** see finding 7.
- **D3′(ii):** the one-event coverage run proves that all sealed events use found splines only if GENIE loads every spline at init. I have not read GEVGDriver.cxx, so this is unverified. If lookups are lazy, one event proves little.
- **The "no seed in a path-only trace" claim is gone:** the round-3 ruling already admits that traces hold seeds, and the scan is the only control. That makes finding 4 the main seed risk.

VERDICT: NO-GO. An unpinned `Messenger_pg.xml` will STOP every correct coverage run, unresolved execs and the unseen binary seed encodings each leave a way through, and the gspl2root defining-file rule probably STOPs correct runs too.