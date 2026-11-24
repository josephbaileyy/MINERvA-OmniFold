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

The command runs with:

- cwd W, TMPDIR = W/tmp, and stdin /dev/null;
- stdout and stderr captured to W/capture/{stdout,stderr}.log, so nothing reaches the terminal;
- a scrubbed environment: only the gen-spec's `env_keep` variables that are set, plus TMPDIR. In particular, it gets
  no `SCRATCH` unless `env_keep` lists it;
- its own process group, which is killed on failure or SIGTERM.

`seeds.json` is:

```
{"tunes": [{"u": 0, "name": "<tune 0>", "task_seeds": [7 ints]}, {"u": 1, ...}]}
```

with `task_seeds[i]` = base + 10 000·u + i, for i = 0 to 6.

The command must:

- **write every output under W:** products, gevgen.log, gntpc.log, setup_genie_v3.sh output, job scripts, meta JSON,
  the convert stage's f_MEC, p and n_in_grid, and the ratio files. Nothing may go elsewhere. If anything is created or
  changed under $SCRATCH/tmp and it carries a plaintext hash, or a task seed in its name or bytes, it is a spill: the
  binary removes it and fails the run.
- **write W/PRODUCTS.json:** a non-empty JSON list of distinct, safe relative paths of regular files under W, naming
  the physics products PV will read.
- **exit 0 on success.** On a non-zero exit, everything under W is still sealed, and the run fails.
- **not create symlinks or special files under W.** These are refused, and the trap still deletes W.

The gen-spec is a JSON object with exactly four keys:

```
{"command": [<absolute path>, args...], "command_sha256": "<64 hex>",
 "tunes": [<u=0 name>, <u=1 name>], "env_keep": [...]}
```

`env_keep` may not list TMPDIR. The binary's own arguments are:

```
--covfix-attempt <32 hex> --workdir <empty dir> --sealed <new dir, disjoint from W>
--gen-spec <file> --gpg <absolute path> --gpgconf <absolute path>
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

Each call gets a fresh GNUPGHOME under /dev/shm: under 80 characters, mode 700, and never under $SCRATCH. The binary
kills gpg-agent with it and removes it. A removal that cannot be confirmed is a role failure. ~/.gnupg is never touched.

Before generation, the binary runs a synthetic round trip with the pinned gpg and the real passphrase.
