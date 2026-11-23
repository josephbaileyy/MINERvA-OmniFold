# COVFIX director's wrapper (`covfix_wrapper.py`)

The wrapper runs COVFIX's secret-bearing roles under the declaration's ST4 (validation is spent once), §3.4 (who runs
the writer and readout, and the synthetic-seal test) and §4.2 (custody). It is the director's tool: cov2d writes and
tests the bound PG and PV code, and it never runs these roles. The wrapper holds no physics. It guards three things:
the secrets, the consumption record, and the order of operations around them.

This directory holds:

- `covfix_wrapper.py`, the wrapper (stdlib only; `security`, `gpg`, `git` and `ssh` on PATH or as configured);
- `reference_role.py`, a reference bound binary: the stdin side of the interface, used by the tests and the synthetic
  seal (not PG or PV code);
- `test_covfix_wrapper.py`, the tests;
- `role-config.example.json`, the shape of the sha-pinned role config;
- `DIRECTOR-README.md`, the secret-free README installed beside the record in `~/director-tools/covfix/`.

## The interface cov2d's binaries must match

**stdin, then EOF.**

| Role | What it receives |
|---|---|
| `pg-connect` | `<passphrase: 64 lowercase hex>\n<seed base: ASCII decimal>\n` |
| `pv-writer`, `pv-readout` | `<passphrase>\n` |

The salt never leaves the laptop before `reveal`. A binary must:

1. read stdin to EOF and refuse any other frame;
2. hand the passphrase to gpg on **fd 3** through an internal pipe, with the pinned flags of §4.2, streaming the payload
   on gpg's stdin and stdout;
3. use no decrypted byte before gpg exits 0;
4. print no secret.

`reference_role.py` does exactly this.

**The launch.** The role config names, per role:

- `command`: the remote command, for example
  `salloc --exclusive -N 1 ... srun --exclusive -N 1 <binary> <args>`;
- `binary` and `binary_sha256`.

The wrapper runs `<ssh> <host> <command>` and writes the frame on ssh's stdin, which salloc and srun forward to the task.
Before the spend it hashes the binary on the cluster, and any difference refuses. The config file's own sha256 is
pinned in the binding and passed as `--config-sha256`.

## Order of operations in `run --role R`

1. **Config.** Its sha256 must equal the pinned one.
2. **Record and mirror.**
   - The record directory must be mode 700 and the record's hash chain intact.
   - The mirror worktree must be on its branch, with the record path clean.
   - The pushed mirror must be a prefix of the local record, and no mirror commit on any ref may hold a line the local
     record lacks (a restored copy).
   - A record line or an uncertain marker for (key, R) refuses as consumed. A break line refuses every role of its seal.
   - The freeze bound at the seal's first acquisition must equal `--freeze-digest`.
3. **Secrets.** Read from the Keychain and checked: 64-hex passphrase; seed base in [1 000 000 000, 2 000 000 000).
   For `pg-connect`, sha256(seed base ':' salt) must equal `--commitment`.
4. **Cluster checks.**
   - The bound binary must hash to its pin.
   - For the PV roles, `PG-SEAL.sha256` and `P2-FREEZE.sha256` must hash to `--seal-digest` and `--freeze-digest`, and
     every listed file is hashed on the cluster.
   - A missing or altered file, or a list off its digest, is a **break**: recorded, mirrored and terminal for every role
     of the seal.
   - A link or environment failure (no end line, a non-zero rc, an unreadable file, a missing root) refuses and spends
     nothing.
5. **The spend.** Under the lock: append `spent`, fsync the file and the directory, commit the record path, push, fetch,
   and require the remote blob to equal the local record. A lock, write, commit, push or verify failure leaves an
   `UNCERTAIN-<key12>-<role>` marker. The role is then blocked for good, and the marker enters the chain at the next
   locked write.
6. **The launch.** The frame is written unbuffered and then zeroed. A non-zero rc, a dropped link or an interrupt
   records `terminal`; rc 0 records `completed`. Nothing retries.

`reveal` requires a `pv-readout` outcome line for the seal, or `--after-stop '<named stop>'`. The seed base and salt
must reproduce `--commitment`. A `reveal` line is recorded before anything is printed.

**Exit codes:** 0 done; 2 refused (nothing spent); 3 terminal; 4 usage or environment error.

**The mirror commit runs without the repository's hooks** (`core.hooksPath=/dev/null`; `"run_hooks": true` in the
config turns them on). It commits one path on a dedicated branch, before decryption. A hook failure there would be an
uncertain spend that burns the role.

## Tests

```
cd docs/orchestration/state/2d-closeout/covfix-20261122/wrapper
python3 -W error::ResourceWarning -m unittest test_covfix_wrapper
```

The tests:

- use Keychain items named `covfix-test-<random>-*` only, which they create and delete;
- set `COVFIX_FORBID_REAL_KEYCHAIN=1`, so the real `covfix-` prefix refuses;
- stub ssh, salloc and srun locally, so nothing connects anywhere;
- seal only synthetic truths, so no test is a launch.

gpg runs in a throwaway `GNUPGHOME` under `/tmp`, because the agent's socket path must stay short.

## The synthetic seal (§3.4)

`synthetic-seal --keychain-prefix covfix-synth- --out DIR` (it refuses the real prefix) builds:

- a dummy truth, encrypted with the pinned flags;
- an encrypted manifest of plaintext hashes;
- a decrypt round trip;
- `PG-SEAL.sha256` over the ciphertexts;
- a dummy `P2-FREEZE.sha256`.

It prints the two digests and the two roots. Copied to the cluster, it runs end to end through `run` with a role config
whose `keychain_prefix` is `covfix-synth-`, whose record directory and mirror branch are separate from the real ones,
and whose commands name the bound writer and readout. That run also measures the allocation time §3.4 asks for. It is
the director's to launch.
