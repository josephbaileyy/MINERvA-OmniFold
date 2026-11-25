I found no blocker, but I found several majors. None of it was run: I had only Read, Grep and Glob. The test and mutant counts in R4-DISPOSITIONS.md (pytest 216, mutants 257 of 257 and so on) are the dispositions' claims, not something I checked. I read the full diffs for pg_lib.py, pg_verify.py, pg_generate.sh, pg_replay.sh, run_gevgen_v3.sh and the node-launch/install pieces. I skimmed the probe diff and did not review the mutant files, README-only changes or the checklist docs.

**Confidence in the outside facts**
- **GNU `timeout` leaving the process group** (`setpgid(0,0)` unless `--foreground`): high.
- **strace -q/-f output format, and execveat/renameat2/linkat/symlinkat as valid trace names:** high for strace 5.x. `faccessat2` needs strace ≥5.9, which is an older assumption; the B1 self-test would catch it.
- **ROOT RECREATE as access(ENOENT) or lstat+unlink, then `open(O_RDWR|O_CREAT)`:** about 80%. It matches my memory of TFile::Init and codex's cited source. The code fails closed if I'm wrong.
- **ROOT key-record layout, block header, ZL = zlib stream, L4 = 8-byte checksum:** about 80%. Only synthetic fixtures exist on this host. B3's decode is the real control, and it fails closed.
- **GENIE's `GetXMLPathList(bool add_tune)` and what it does before the tune is known:** about 50%.
- **What `Need xsec spline for` prints (full spline key or interaction string):** not verified. I could only see the tests' synthetic format.

**Round-4 fixes that close what they claim, by my read**
- **S1/C1:** the messenger pin is in code (`pg_verify.py:419-424`), with a role guard and an initial-pid read check.
- **S3/C5:** `exec-unresolved`, `execveat`, and the `initial-program` rule.
- **C2:** the RECREATE rule at `pg_verify.py:494-509`.
- **C7:** the write-outside-W check, with the gaps in finding 8.
- **C9, C10, C12, C14–C18:** all closed in code.
- **S5/S9/C17/C19:** also closed.

**FINDINGS**

1. [major] pg_generate.sh:136,286 — The C13 process-group scan misses almost everything it was added to catch. GNU `timeout` puts itself in a new process group. Everything below it (run_gevgen_v3.sh, strace, gevgen, gntpc) is therefore not in `XPG`, and only xargs, `bash -c` and `time` are. The scan reduces to the old cwd test, so a task that `chdir`s out of W escapes as before. A test that puts a process in the xargs group would pass anyway. Fix: key the scan on session id (`ps -A -o pid=,sid=`). `setsid` gives one SID, and `timeout` does not change it. Add a test whose survivor sits under a `timeout`-style `setpgid` and has `cd /`.

2. [major] pg_generate.sh:137-139,149 — S6 is only half fixed. Ancestors are spared, but any non-ancestor process with cwd under W is SIGKILLed. That includes a sibling of this shell such as the `| tee` of a cov2d wrapper, a log shipper, or a heartbeat started by the parent from W. It happens in `drain`, which runs on the success path, before publication. Scenario: `cd W && pg_generate.sh | tee log` ends with the tee killed and the log truncated. Fix: act only on pids in this run's session or descendants of this shell. Report foreign cwd-in-W pids as a STOP without killing them.

3. [major] pg_lib.py `root_schema` / root-schemas.json / pg_generate.sh:76 / pg_replay.sh:110 — The gst schema comes from one B3 file: slot 1, task 0, 100 events, written by gntpc. It is then required of two other kinds of file:
   - the 160000-event task gsts;
   - `out/gst/*_ALL.gst.root`, which is hadd output under conda ROOT 6.28 and matches the `.gst.root` suffix in `schema_problems`.

   `keys` includes every TBasket key (name = branch, title = tree). Those, the TTree cycle layout, and the hadd StreamerInfo bytes are not shown to match across file sizes or writers. If they differ, publish refuses after hours of generation. If they only look equal, the check proves less than the README claims. Fix: B3 also hadds its public gst under the same `anaenv` and records both schemas. Define the schema over non-TBasket keys plus the branch list parsed from the TTree object, and confirm it is invariant to entry count.

4. [major] pg_lib.py `seed_int32_forms`/`leak_scan` — The rule is wrong for the likeliest leak. A seed (below 2³¹ by SEED_CEIL) stored once as a 4-byte int, for example a `TParameter<int>`, a header field or a TNamed payload, passes. Over about a GB of data with 28 patterns, chance gives about 6 hits, so a single hit cannot be told from noise. The schema check is no backstop. It compares key class, name and title and the StreamerInfo hash, not the contents of an object with the same identity. cov2d's condition (ii), that no branch carries the run number, is a human check on B3's file. It does not check sealed output. Fix: for every non-basket, non-TTree object in a published ROOT file, compare its inflated bytes or hash to B3's public-seed object, with the seed normalised. Alternatively STOP on int32 for those objects, and keep count-only for basket payloads. If B3's public-seed gst shows int32 count ≥ 1 above its chance expectation, this becomes a blocker.

5. [major] pg_lib.py `leak_scan` (`rel.endswith(".root")` branch) — C4's "compressed seeds pass" is closed only for ROOT. Published `.npz` (gen5d, if `savez_compressed`) and `.gz` files are scanned as raw bytes only, so a seed inside a deflated member is invisible. I can't tell whether gen5d writes one, because gen5d_v3.py isn't in the copy. Fix: inflate zip and gzip members, or STOP on any compressed container that isn't ROOT.

6. [major] pg_verify.py:653-680 — The probe-walk compares probes against one static `full` list: GXMLPATH, the search_dirs, then GNuMINtuple. If GENIE builds its path list per call, with the tune dir only after RunOpt has the tune, early lookups such as `Messenger.xml` (under cfg_root, so `searched()` is true) are probed with a shorter list. That gives `search-probes` or `search-path` on a correct run. Two other ways it can STOP a correct run:
   - Stale `pend` entries: one failed all-ENOENT walk for a basename merges with a later successful walk. `cur` is then non-empty, so the check reports `bad`.
   - A basename probed and later read through a different resolved path.

   B3 would show it, as a STOP rather than a pass. Fix: take the expected list per call from B3's observed probes (which prefixes occur). At least reset `cur` at the start of each walk, which means at the first probe whose dirname is `full[0]`.

7. [major] pg_verify.py:1032-1044 (`revision_problems`) — S7 is weaker than D2. "Every CVMFS file the run read re-hashes" really means every file that `trace_check` recorded: gated, `root_config`, libs and execs. Three problems:
   - Other CVMFS reads, such as headers, are not rechecked.
   - Gated entries are re-hashed by `x["path"]` with `sha_path`, which uses O_NOFOLLOW. A symlinked path fails with OSError, so a changed revision STOPs a correct run.
   - Existence and shadowing are not re-evaluated. A new file in an earlier search dir passes.

   Fix: use `real` for gated entries too, and state in the rule that coverage is the pinned classes only.

8. [minor] pg_verify.py:511-516 — Write confinement covers open, rename, link, symlink and unlink only. `mkdir`, `mknod`, `truncate`, `chmod` and `utimensat` outside W pass. Conversely, any `O_RDWR` or `O_CREAT` open outside W other than `/dev/null` STOPs a correct run, for example `/dev/tty` or `/dev/shm`. Probably harmless on this workload, but it is worth knowing which.

9. [minor] pg_verify.py:1069 — `ROOT_GENIE_LIB` can match system libraries. `EG[A-Za-z]*` matches `libEGL.so.1`, and `Net`, `Math`, `Gui` and `Graf` have the same problem. A system copy in `/usr/lib64` gives `so-not-cvmfs`. It also assumes log4cpp, LHAPDF and Pythia6 come from CVMFS. Fix: anchor on the actual ROOT/GENIE lib lists from the manifest.

10. [minor] pg_replay.sh:86-128 — Two issues in the B3 deletion record:
    - Only `OSError` and `Refusal` are caught. `root_keys` can also raise `struct.error` or `IndexError` (`_tstring`, pg_lib.py:507-513) or `ValueError`. That aborts mid-loop. The `finally` unlinks only the current file, so with the one-shot retry the later files can remain and `deleted.json` is unwritten. Fix: `except Exception`, and write the record before the unlinks.
    - `"$PY" -I -` with no `-B` imports pg_lib from the deploy. `-I` ignores `PYTHONDONTWRITEBYTECODE`, so it writes `__pycache__` into the deploy copy, contrary to the README's "nothing is written into the deploy". Fix: add `-B`.

11. [minor] pg_lib.py:cmd_publish — `os.walk(followlinks=False)` does not flag a symlink to a directory inside W, because it lands in `dirs` and not `names`. Only file symlinks are refused. `W/tmp` is skipped by name without a type check, though pg_generate checks it at the start.

12. [minor] pg_generate.sh:288 — The task shell discards `seedfree`'s status. The later `seedfree || need` at line 294 catches it, so this is cosmetic. The "two guards untestable here" (reap-when-dead and the 30 s poll) are a fair disclosure. They log count-only lines, and I saw no seed in them.

**Rule notes**
- The C2 RECREATE rule is right as far as I can tell. The `unlink` and `lstat` order is covered by `fresh()`, and the CREATE-time `access` ENOENT also satisfies it. Checking only the last same-pid event is conservative.
- The "exact output path" requirement protects `genie_v3.gst.root`, which contains "genie" and is gated by name. The failure mode is a STOP.
- The C3 hidepid record is a record, not a gate. That is the director's ruling. I saw no seed on any Slurm-recorded surface in the scripts: pg_generate takes only `--workdir` and `--seeds`, and exports only G, O, NEV and TO. Live `/proc/<pid>/cmdline` still carries the seed, as ruled.
- `trace_check*.json` is published. Its problem text can name W paths, but a seed-named path (`gntp.<seed>.ghep.root`) appears only if that file is gated, and its relative name has no "genie". I found no leak there.

VERDICT: No blocker found, but the survivor/process-isolation fix is largely ineffective (1, 2), and the publication gate's int32 rule, gst schema and compressed-container coverage (3–5) are too weak or unproven to rely on. Clear 1–6 and the B3 schema question before PG.