<!-- codex-school2 (gpt-6.2-sol, high), the round-5 confirm read of 6ba32779 -> b9642de9, run 2026-11-27 04:58:18-05:02:47Z,
rc 0, 112,968 tokens. Verbatim, except that the reader's absolute input-directory prefix was removed from its links,
which are relative to that directory (code/, receipts/, context/). -->
<!-- absence-ok: verbatim third-party read report; the reader's findings about this lane's code, not claims that a result does not exist -->
**NO-GO**

- **2 — PARTIAL.** The named near-misses are refused. Python splits a directive at a vertical tab, while Slurm treats it as whitespace on the same line. A forbidden array option can reach `sbatch`. [covfix_ledger.py:393](code/covfix_ledger.py:393), [Slurm’s parser](https://raw.githubusercontent.com/SchedMD/slurm/master/src/sbatch/opt.c)
- **4 — FIXED.** Replay blocks a second intent while one lacks a job ID, shares the live claim’s budget check, and requires string digests for amendments and product acceptance. `covfix_ledger.py:249,263,267,284,379,504,516`
- **5 — FIXED.** Live reconcile and replay share `_charge`, which checks the job ID, name, terminal state and counters. Replay requires the recorded charge to match the evidence. `covfix_ledger.py:99,276,492`
- **new (format 4) — PARTIAL.** The policy carries format 4. Replay parses the full file first, so a torn append after an older policy produces a JSON error before the format diagnostic. `covfix_ledger.py:176,216,235`
- **7 + new — PARTIAL.** The detector walks the whole job subtree and applies the contiguous ancestor rule. An undecodable `comm` aborts the required inventory. `covfix_pg.py:189,201,229`
- **8 + new — PARTIAL.** SIGTERM kills the GPG child, and home removal is in `finally`. The 15-second bound is unenforced. A stalled read while verifying the pinned `gpgconf` binary can exhaust the scheduler’s kill grace before the subprocess timeout starts. `covfix_seal.py:140,189,201,249,255`
- **10 — FIXED.** All six supplied receipt headers match the snapshot bytes. The recorded runs report 219/219 PG and 114/114 ledger mutants killed, with one Linux-only PG test skipped on Darwin. `receipts/pg/tests.txt:172`, `receipts/pg/mutation.txt:233`, `receipts/ledger/mutation.txt:121`
- **M1 — PARTIAL.** The serialized-summary scan, redaction and path tokens work with available hashes. One unreadable work file can leave the guard without any hashes from the failure trap. `covfix_pg.py:337,413,421,517`
- **M2 — PARTIAL.** Scratch filenames and contents are checked for case-insensitive hash text at any offset. A work-file read error in the failure trap skips the scratch scan. `covfix_pg.py:290,297,517`
- **(a) — FIXED.** `SystemRandom.shuffle` assigns opaque IDs, and the encrypted manifest holds the mapping. `covfix_seal.py:327,347,356`
- **(b) — FIXED.** The seal’s encryption argv includes `--compress-algo none`. `covfix_seal.py:59,352`
- **gen-spec — PARTIAL.** The scan sees decoded Unicode escapes. Duplicate JSON keys can discard a seed-bearing value before the scan. `covfix_pg.py:126,459`
- **decryptors — PARTIAL.** The manifest has the specified representation and serialization guards, and `read_product` requires its type. Its backing dictionaries remain mutable. `covfix_seal.py:515,527,572,577`
- **job check first — FIXED.** The precheck precedes both the synthetic GPG probe and generation, leaving W empty on refusal. `covfix_pg.py:457,462,472`
- **publish_guard exemption — PARTIAL.** The guard checks the allowlist, manifest membership and recomputed digest. It can still refuse a valid sums line when the verified digest happens to contain a seed’s hex digits. `covfix_seal.py:619,628,633,639`
- **env_keep (i) — FIXED.** Unset and duplicate names are refused during spec loading. `covfix_pg.py:144`
- **gen-spec pin (ii) — FIXED.** The required pin is checked before stdin, and the parser uses the same bytes that were hashed. `covfix_pg.py:118,538,548,556`
- **env_set (iii) — PARTIAL.** Literal values are pinned, validated and injected, and conflicting inherited values are refused. Both environment maps still admit `SCRATCH`. `covfix_pg.py:136,148,357`
- **W/tmp mode — FIXED.** Exclusive creation followed by `chmod(0700)` meets the generator’s ownership and mode check across umasks. `covfix_pg.py:343,355`, `context/pg_generate.sh:58`
- **PG call site for publish_guard — FIXED.** PG seals all of W, including `out/`, then empties W. The guard belongs at PV’s decrypt-and-write step. `covfix_seal.py:344,595`, `covfix_pg.py:478,482`
- **probe — FIXED.** The synthetic probe and the seal use the same `GPG_ENCRYPT` constant. `covfix_pg.py:463`, `covfix_seal.py:352`

**New defects**

- **MAJOR — A cleanup read error can leak a plaintext hash.** If the post-generation job check finds a stray whose executable path contains a trace digest, and an unrelated W file is unreadable, the trap discards all computed digests. The summary emits the trace digest, and the trap skips scratch cleanup. `covfix_pg.py:337,505,517`
- **MAJOR — A pinned gen-spec can retain a task seed.** If a hand-edited `env_set` repeats a key, with the task seed in the first value and a clean value second, JSON parsing drops the first value. PG proceeds while the pinned file still contains the seed. `covfix_pg.py:126,459`
- **MAJOR — The generator can receive forbidden `SCRATCH`.** With site `SCRATCH` set, either listing it in `env_keep` or pinning its matching value in `env_set` passes validation and forwards it to the child. `covfix_pg.py:136,148,357`
- **MAJOR — Mutating the manifest can disable hash protection.** If a PV caller removes a processed entry from `manifest._products`, a later guard call passes that entry’s plaintext hash because `ids()` no longer includes it. `covfix_seal.py:517,541,634`
- **MINOR — A valid published sums file can be refused.** The SHA-256 of `b'{"ratio": 1.02}\n'` contains `6bd2c85c`, the hex form of legal seed `1808975964`. The guard rejects the sums line even after verifying the allowlisted file and its digest. `covfix_seal.py:625,633,639`
- **MINOR — One process name can erase the cgroup inventory.** If Linux truncates a stray’s `comm` mid-UTF-8 character, decoding raises before `StepRefusal` is built. PG reports `internal error` without the inventory. `covfix_pg.py:189,230,507`, [Linux `proc_pid_comm` manual](https://man7.org/linux/man-pages/man5/proc_pid_comm.5.html)