# COVFIX PG: the generic capture, encryption, seal check and scan (cov2d)

Code under COVFIX-BINDING-1 ruling 4, in `2d-unfolding/covfix/`:

| file | role |
|---|---|
| `covfix_seal.py` | library, shared with PV's readers |
| `covfix_pg.py` | the bound PG binary |
| `covfix_sealcheck.py` | the public ciphertext check |

The ST3/ST6 ledger, `covfix_ledger.py`, is in `../../ledger/`. This code runs on no cluster before PG's own binding
addendum. Its receipts are in `code-receipts/`, and its reads in `reads/`.

## The interface for tune-generator's tune code

The PG binary runs tune-generator's command as its only subprocess. It is invoked as:

```
<resolved command, args...> --workdir W --seeds W/seeds.json
```

The binary resolves the command's absolute path once, checks its sha256 against the gen-spec, launches it by that
resolved path, and hashes it again after the run. If the bytes changed, the run is a role failure.

**Residual window (disclosed, the director's ruling R2 of 2026-11-24).** A replacement written by this same account
between the hash and the launch, and restored before the re-hash, would not be seen. §4.2's cooperative assumption
already trusts that account, and the same class was accepted as non-blocking in JE's wrapper. The fix (copying the
command and executing the copy) would forbid $0-relative paths in the command for no gain against the declared threat
model, so the window is disclosed rather than closed.

The command runs with:

- cwd W, TMPDIR = W/tmp (made at mode 0700 whatever the umask, as pg_generate.sh requires), and stdin /dev/null;
- stdout and stderr captured to W/capture/{stdout,stderr}.log, so nothing reaches the terminal;
- a scrubbed environment: only the gen-spec's `env_keep` variables and `env_set` values, plus TMPDIR. In particular,
  it gets no `SCRATCH` unless `env_keep` lists it. Every listed name must be set in the binary's environment, and none may be listed twice,
  or the run is refused before the job check with W untouched (the director's ruling (i) of 2026-11-25). A misspelled
  name used to be dropped silently. An optional variable is simply not listed. `env_set` holds literal values (the
  director's ruling (iii) of 2026-11-25), for `PG_DEPLOY_PIN` and any other value the generator's correctness depends
  on. They are set in the generator's environment, so the gen-spec's pin covers them. If the binary's environment
  already holds a different value for one of them, the run is refused before the job check. A stale value in a login
  dotfile can no longer pass. `env_keep` then holds only what must come from the site: the Slurm names, HOME;
- its own process group. When the command exits, the binary kills the whole group and confirms it is gone before
  sealing, so **no background process the command started survives it**. Anything still writing is killed. The group
  is also killed on failure or SIGTERM.
- **the step check.** Just before the seal, the binary reads its cgroup (`/proc/self/cgroup`, which must be a single
  cgroup v2 entry under exactly one Slurm `job_<id>` cgroup). It then reads `cgroup.procs` in every directory of that
  job's subtree: every step (a background srun, an `--overlap` step), `step_extern` (where pam_slurm_adopt puts an
  ssh session), every task and every nested cgroup. It refuses to seal if any pid there is other than its own and its
  contiguous ancestor chain (the wrapper that launched it). There is no allowlist: a slurmstepd or step_extern's sleep
  is a STOP unless it is in that chain. Any allowlist entry comes to the director first, with the rehearsal's
  inventory and a reason. A descendant that called setsid escapes the process group but not the job's cgroups, so it
  is caught. Any unreadable directory, or a cgroup that is not a single v2 entry under one job, is a STOP. The escape
  itself is disclosed, not prevented (the director's ruling on round 3's item 7; rev 12 §4.2). The summary records
  `step_cgroup` with counts only; a refusal also records `step_cgroup_inventory`, each other process's cgroup path
  under the job, pid, comm and exe. An exe under W, the sealed dir or $SCRATCH is recorded as a fixed token
  (`<workdir>`, `<sealed>`, `<scratch>`), never its path.
- **the same check before anything runs** (`step_cgroup_pre`). The wrapper runs pg-connect on its host with no
  allocation of its own (the director has JE give pg-connect a slurm block, as the PV roles have). So a sealer outside
  a Slurm job, or with another process already in its job, is refused before the synthetic round trip and before the
  generator starts, and W stays empty. Without it, a launch outside a job would have generated and only then refused
  to seal, leaving seed-bearing plaintext in W.

`seeds.json` is:

```
{"tunes": [{"u": 0, "name": "<tune 0>", "task_seeds": [7 ints]}, {"u": 1, ...}]}
```

with `task_seeds[i]` = base + 10 000·u + i, for i = 0 to 6.

The command must:

- **write every output under W:** products, gevgen.log, gntpc.log, setup_genie_v3.sh output, job scripts, meta JSON,
  the convert stage's f_MEC, p and n_in_grid, and the ratio files. Nothing may go elsewhere. If anything (a file, a
  directory or a link) is created or changed under $SCRATCH/tmp and it is a copy of a plaintext file, or carries a task
  seed or a plaintext hash's hex (either case) anywhere in its relative path, its bytes or a link's target, it is a
  spill: the binary removes it (a new directory with its contents) and fails the run. A sums file there is a spill:
  the hash of a seed-bearing file is itself seed-bearing (the director's ruling of 2026-11-25).
  - A file's change includes its ctime, so restoring mtime does not hide an overwrite.
  - An unreadable file is a spill. A directory that cannot be listed fails the run. Neither stops the scan.
  - The trap stays armed until every removal is verified.
- **write W/PRODUCTS.json:** a non-empty JSON list of distinct, safe relative paths of regular files under W, naming
  the physics products PV will read. PG's own files are not products: no entry may lie under `capture/` or `tmp/`, or
  be `seeds.json` or `PRODUCTS.json`.
- **leave the gen-spec's required inventory:** each `required` pattern must match exactly its count of regular files
  under W, or there is no receipt.
- **exit 0 on success.** On a non-zero exit, everything under W is still sealed, and the run fails.
- **not create symlinks or special files under W.** These are refused, and the trap still deletes W.

The gen-spec is a JSON object with exactly six keys:

```
{"command": [<absolute path>, args...], "command_sha256": "<64 hex>",
 "tunes": [<u=0 name>, <u=1 name>], "env_keep": [...], "env_set": {"<name>": "<literal value>", ...},
 "required": [{"pattern": "<glob relative to W>", "count": <n>}, ...]}
```

`env_keep` may not list TMPDIR. `env_set` maps names (letters, digits and `_`, not starting with a digit) to string
values with no NUL. It may be empty, and it may name neither TMPDIR nor an `env_keep` name. `required` is a non-empty list of distinct patterns. Each is relative, with no `..`,
and is matched with fnmatchcase, where `*` crosses `/`. Each count is an integer ≥ 1. tune-generator's
`pg_lib.py inventory` prints the same format.

**The gen-spec is pinned** (the director's ruling (ii) of 2026-11-25). `--gen-spec-sha256` is required, and the binding
pins it in the pg role's arguments. The binary reads the file once, hashes those bytes and parses the same bytes, so
the file cannot change between the check and its use. A mismatch is refused before anything runs. Because
`command_sha256` sits inside the gen-spec, the pin also covers the generator command, `env_keep`, `env_set`'s values
and the required inventory. The pin must be 64 lowercase hex, or the binary refuses before reading its stdin.

gpg_run holds a SIGTERM: it SIGKILLs gpg at once (or as soon as gpg starts), shuts the agent down (gpgconf, at most
`GPGCONF_TIMEOUT_S` = 10 s), removes the home whatever that shutdown raised, then delivers the SIGTERM. The hold is
bounded by `SIGTERM_HOLD_BOUND_S` = 15 s, below Slurm's default KillWait of 30 s; a test measures it under a gpg
that ignores SIGTERM. The binary's own arguments are:

```
--covfix-attempt <32 hex> --workdir <empty dir> --sealed <new dir, disjoint from W>
--gen-spec <file> --gen-spec-sha256 <64 hex> --gpg <absolute path> --gpgconf <absolute path>
--gpg-sha256 <64 hex> --gpgconf-sha256 <64 hex>
```

Its stdin is exactly "<64-hex passphrase>\n<10-digit seed base>\n", 76 bytes, then EOF.

## The seed alias

This follows the director's ruling of 2026-11-24 on B1, option (a).

## Seed-bearing artifacts (the director's ruling of 2026-11-25)

gevgen names its outputs by the run number, which is the seed (`gntp.<seed>.ghep.root`, `genie-mcjob-<seed>.status`),
so W's raw traces, logs and file names carry seeds. The binary is W's boundary, and it enforces the ruling:

- **Nothing in W leaves except encrypted.** Every file under W is sealed, PRODUCTS.json and any sums file included,
  and W is deleted and verified empty. Plaintext hashes leave memory only inside the encrypted manifest.
- **Opaque ids are random.** p0001…pN are assigned over a CSPRNG permutation of the relpaths (`assign_ids`,
  `secrets.SystemRandom`), so an id's position says nothing about its relpath. The mapping is only in the manifest.
- **No compression.** gpg runs with `--compress-algo none`, so a ciphertext's size is its plaintext's plus a constant:
  a fixed-width seed in a status or log text does not change it.
- **The summary is scanned.** Before printing, the binary scans its summary for every task seed and every plaintext
  hash's hex. A hit reduces the inventory to its count, or replaces the summary with a fixed refusal; the summary is
  marked `summary_leak_redacted`, and the run exits 1 (a break stays 66).
- **The gen-spec names no seed.** The gen-spec, re-serialized, must not contain any task seed, or the run is refused
  before anything runs.
- **Decryptors.** The manifest's `paths` and `products` are the seed-named inventory and the seed-bearing hashes.
  Whatever decrypts it (PV, the `read_product` callers) must not publish either before unblinding: a binding
  precondition, enforced in code where it can be (the director's rulings 3 and 4 of 2026-11-25):
  - `open_manifest` returns a `SealedManifest`. Its repr and str give counts only. Pickling, copying, `json.dumps`,
    subscripting, iteration and `vars()` raise TypeError, and it is read-only. It is read through `ids()`, `path(id)`
    and `sha256(id)`, and `read_product` takes nothing else.
  - `publish_guard(data, manifest, seeds)` returns `data` unchanged, or refuses it with a fixed message. It refuses:
    - each given seed in any form: decimal (so also zero-padded), and hex in either case;
    - every run of 10 or more digits in a manifest relpath component;
    - every manifest hash's hex, in either case.
    `seeds` is the exact, non-empty list; an epoch that is not a seed passes. Only when `seeds` is None does it fall
    back to refusing any 10-digit decimal in [SEED_BASE_LO, SEED_LIMIT), which refuses an epoch too.
  - **Who calls it.** Nothing is published at PG: the seal takes every file under W, W is emptied, the sealed dir holds
    only ciphertext, and stdout is the leak-guarded summary. The published set can leave only once it is decrypted,
    which means in PV, and the caller is the process that opens the manifest, calls `read_product` and writes what PV
    publishes. No such caller exists yet. The direction the director accepted on 2026-11-25, not yet a binding, is a
    bound decrypt-and-write binary on cov2d's side, like this one: the frame on stdin (so it holds the seed base for
    the exact seeds), emitting only bytes that passed this guard. Its design note comes in a later round, after the PG
    rehearsal. Under that design the wrapper never holds the passphrase or the manifest.
  - Its one exemption (the director's ruling of 2026-11-25, for tune-generator's published sums file):
    `publish_guard(data, manifest, seeds, published=..., allowlist=...)`. `published` maps each file published
    alongside (manifest relpath -> its bytes), and `allowlist` is the export allowlist's globs; they come together.
    Each published file must match the allowlist and be in the manifest, and the guard recomputes its sha256, which
    must equal its manifest entry, or the call is refused. Only those recomputed hashes may then appear in `data`.
    Every other manifest hash (a trace's, a file outside the allowlist's) still refuses.
- **The probe** (the synthetic round trip before generation) uses exactly the seal's argv, so it exercises the
  uncompressed flags.

Task (u = 0, i = 0)'s seed **is the seed base**. It appears **inside W only**: in W/seeds.json, in that task's gevgen
argv (`--seed` and `-r`), and in its logs. All of these are sealed, and then W is deleted and verified empty.

The spill scan treats the base like every task seed: no file created or changed outside W during the run may carry it.

The binary's stdout summary carries a `"seed_alias"` field that states this. The seed commitment is unchanged.

## What is published

`PG-SEAL.sha256` lists only "<ciphertext sha256>  p0001.gpg" … "pNNNN.gpg" and "PG-MANIFEST.json.gpg".

The relpath map lives only inside the encrypted manifest, as `{"products": {id: plaintext sha256}, "paths": {id:
relpath}}`.

Ciphertext sizes are public; with no compression they are the plaintext sizes plus a constant.

Stdout carries fixed codes, booleans and counts, scanned for seeds and plaintext hashes before printing, and then the
contract's last line:

- `covfix-receipt <attempt>` on full success;
- `covfix-break <attempt>` with exit 66, on a confirmed integrity break.

## gpg

The pinned flags are §4.2's, plus `--compress-algo none` (the director's GO of 2026-11-25; rev 12 §4.2 carries it).
The passphrase is passed on fd 3 only, and gpg is left with exactly fds 0–3 and core
dumps off.

**gpg and gpgconf are pinned (the director's ruling R1).** PG's binding records both binaries' sha256. Both paths
must be absolute and fully resolved. Each binary is hashed through a file descriptor when PG starts and again
immediately before every exec. A mismatch, for example after a NERSC update, is a STOP and a rebinding, never a
fallback. The exec is by path after the hash, the same residual window as above.

Each call gets a fresh GNUPGHOME under /dev/shm: under 80 characters, mode 700, and never under $SCRATCH. The binary
kills gpg-agent with it and removes it. An agent shutdown or a removal that cannot be confirmed is a role failure. ~/.gnupg is never touched.

Before generation, the binary runs a synthetic round trip with the pinned gpg and the real passphrase.
