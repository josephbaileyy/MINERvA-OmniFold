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

- cwd W, TMPDIR = W/tmp, and stdin /dev/null;
- stdout and stderr captured to W/capture/{stdout,stderr}.log, so nothing reaches the terminal;
- a scrubbed environment: only the gen-spec's `env_keep` variables that are set, plus TMPDIR. In particular, it gets
  no `SCRATCH` unless `env_keep` lists it;
- its own process group. When the command exits, the binary kills the whole group and confirms it is gone before
  sealing, so **no background process the command started survives it**. Anything still writing is killed. The group
  is also killed on failure or SIGTERM.
- **the step check.** Just before the seal, the binary reads its own cgroup (`/proc/self/cgroup`, which must be a
  single cgroup v2 entry, then that cgroup's `cgroup.procs`). It refuses to seal if any pid is there other than its
  own and its ancestors' (the wrapper that launched it). A descendant that called setsid escapes the process group but
  not the cgroup, so it is caught. An unreadable or non-v2 cgroup is a STOP. The escape itself is disclosed, not
  prevented (the director's ruling on round 3's item 7; rev 12 §4.2). The summary records `step_cgroup`, with counts
  only.

`seeds.json` is:

```
{"tunes": [{"u": 0, "name": "<tune 0>", "task_seeds": [7 ints]}, {"u": 1, ...}]}
```

with `task_seeds[i]` = base + 10 000·u + i, for i = 0 to 6.

The command must:

- **write every output under W:** products, gevgen.log, gntpc.log, setup_genie_v3.sh output, job scripts, meta JSON,
  the convert stage's f_MEC, p and n_in_grid, and the ratio files. Nothing may go elsewhere. If anything (a file, a
  directory or a link) is created or changed under $SCRATCH/tmp and it carries a plaintext hash, or a task seed
  anywhere in its relative path, its bytes or a link's target, it is a spill: the binary removes it (a new directory
  with its contents) and fails the run.
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

The gen-spec is a JSON object with exactly five keys:

```
{"command": [<absolute path>, args...], "command_sha256": "<64 hex>",
 "tunes": [<u=0 name>, <u=1 name>], "env_keep": [...],
 "required": [{"pattern": "<glob relative to W>", "count": <n>}, ...]}
```

`env_keep` may not list TMPDIR. `required` is a non-empty list of distinct patterns. Each is relative, with no `..`,
and is matched with fnmatchcase, where `*` crosses `/`. Each count is an integer ≥ 1. The interim list is pinned by
the binding; tune-generator's `pg_lib.py inventory` prints the same format.

gpg_run holds a SIGTERM until gpg has exited and the agent and the home are cleaned up, then delivers it. The binary's own arguments are:

```
--covfix-attempt <32 hex> --workdir <empty dir> --sealed <new dir, disjoint from W>
--gen-spec <file> --gpg <absolute path> --gpgconf <absolute path>
--gpg-sha256 <64 hex> --gpgconf-sha256 <64 hex>
```

Its stdin is exactly "<64-hex passphrase>\n<10-digit seed base>\n", 76 bytes, then EOF.

## The seed alias

This follows the director's ruling of 2026-11-24 on B1, option (a).

Task (u = 0, i = 0)'s seed **is the seed base**. It appears **inside W only**: in W/seeds.json, in that task's gevgen
argv (`--seed` and `-r`), and in its logs. All of these are sealed, and then W is deleted and verified empty.

The spill scan treats the base like every task seed: no file created or changed outside W during the run may carry it.

The binary's stdout summary carries a `"seed_alias"` field that states this. The seed commitment is unchanged.

## What is published

`PG-SEAL.sha256` lists only "<ciphertext sha256>  p0001.gpg" … "pNNNN.gpg" and "PG-MANIFEST.json.gpg".

The relpath map lives only inside the encrypted manifest, as `{"products": {id: plaintext sha256}, "paths": {id:
relpath}}`.

Stdout carries fixed codes, booleans and counts, and then the contract's last line:

- `covfix-receipt <attempt>` on full success;
- `covfix-break <attempt>` with exit 66, on a confirmed integrity break.

## gpg

The pinned flags are §4.2's. The passphrase is passed on fd 3 only, and gpg is left with exactly fds 0–3 and core
dumps off.

**gpg and gpgconf are pinned (the director's ruling R1).** PG's binding records both binaries' sha256. Both paths
must be absolute and fully resolved. Each binary is hashed through a file descriptor when PG starts and again
immediately before every exec. A mismatch, for example after a NERSC update, is a STOP and a rebinding, never a
fallback. The exec is by path after the hash, the same residual window as above.

Each call gets a fresh GNUPGHOME under /dev/shm: under 80 characters, mode 700, and never under $SCRATCH. The binary
kills gpg-agent with it and removes it. An agent shutdown or a removal that cannot be confirmed is a role failure. ~/.gnupg is never touched.

Before generation, the binary runs a synthetic round trip with the pinned gpg and the real passphrase.
