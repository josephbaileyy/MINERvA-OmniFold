# COVFIX director's wrapper (`covfix_wrapper.py`)

The wrapper runs COVFIX's secret-bearing roles under three sections of the declaration: ST4 (validation is spent once),
§3.4 (who runs the writer and readout, and the synthetic-seal test) and §4.2 (custody). It is the director's tool:
cov2d writes and tests the bound PG and PV code, and it never runs these roles. The wrapper holds no physics. It
guards three things: the secrets, the consumption record, and the order of operations around them.

This directory holds:

- `covfix_wrapper.py`, the wrapper (stdlib only; it needs `security`, `gpg`, `git` and `ssh`);
- `reference_role.py`, a reference bound binary. It is the stdin side of the interface, used by the tests and the
  synthetic seal, and it is not PG or PV code;
- `test_covfix_wrapper.py`, the tests;
- `role-config.example.json`, the shape of the sha-pinned role config;
- `DIRECTOR-README.md`, the secret-free README installed beside the record in `~/director-tools/covfix/`.

## The interface cov2d's binaries must match

**stdin, then EOF:**

| Role | Frame |
|---|---|
| `pg-connect` | `<passphrase: 64 lowercase hex>\n<seed base: ASCII decimal>\n` |
| `pv-writer`, `pv-readout` | `<passphrase>\n` |

The salt never leaves the laptop before `reveal`.

**A bound binary must:**
1. read stdin to EOF and refuse any other frame;
2. hand the passphrase to gpg on **fd 3** through an internal pipe, with §4.2's pinned flags, in a fresh empty
   `GNUPGHOME`, streaming the payload on gpg's stdin and stdout;
3. use no decrypted byte before gpg exits 0;
4. print no secret;
5. exit **66** (`BREAK_RC`) on a confirmed integrity break of its inputs, manifest or chain. Any other non-zero exit is
   a role failure.

`reference_role.py` does all five.

**The launch is built by the wrapper, never written as a command string.** Each role's entry in the config gives:
- `launcher`: an argument list. For the PV roles it must contain `salloc ... --exclusive ...` and then
  `srun ... --exclusive ...`;
- `binary`: an absolute path;
- `binary_sha256`;
- `args`: an argument list.

The wrapper runs:

```
<ssh> -T -o RequestTTY=no [opts] <host> '<launcher> bash -c <exec check> covfix-exec <binary> <sha256> <args>'
```

The exec check runs on the compute node, inside the allocation. It hashes the binary and execs it only on a match
(exit 86 otherwise), leaving stdin untouched for the binary. The frame goes on ssh's stdin, which salloc and srun
forward to the task, and ssh never gets a PTY. Before the spend, the wrapper also hashes the binary on the login
node.

## The binding

The role config is pinned by sha256 in the binding (`--config-sha256`). Its `binding` block pins three digests:
- `commitment`, for `pg-connect`;
- `seal_digest`, the sha256 of the committed `PG-SEAL.sha256`;
- `freeze_digest`, the sha256 of `P2-FREEZE.sha256`.

The digests given on the command line must equal these. A regenerated or reordered list therefore cannot open a
fresh key for an already-spent role.

## Order of operations in `run --role R`

1. **Config.** Its sha256 is the pinned one, its digests are the binding's, and the launch is built and checked.
2. **Record and mirror (pre-check).**
   - The record directory is mode 700 and the record's hash chain intact.
   - The mirror worktree is on its branch, with the record path clean.
   - The remote branch is fetched. A tip that does not descend from what was last seen is a rewound branch and
     terminal, and so is a deleted branch.
   - The pushed record is a prefix of the local record.
   - No commit reachable from any ref holds a line the local record lacks. That includes the local
     `refs/covfix/published/*`, which keep every published version.
   - A line or marker for (key, R) refuses as consumed. A break or a reveal (line or marker) refuses every role of
     the seal.
   - The freeze bound at the seal's first spend must be this one.
   - `pv-readout` needs a **completed** `pv-writer` for the seal.
3. **Secrets.** They are read from the login Keychain and checked: a 64-hex passphrase, and a seed base in
   [1 000 000 000, 2 000 000 000). For `pg-connect`, sha256(seed base ':' salt) must equal the commitment.
4. **Cluster checks.**
   - The bound binary must hash to its pin.
   - For the PV roles, the local `PG-SEAL.sha256` and `P2-FREEZE.sha256` must hash to the binding, and every file they
     list is hashed on the login node. Each path gets exactly one typed answer: a hash, `covfix-missing` (only when
     stat says "No such file or directory"), or `covfix-unreadable`.
   - A missing or altered file, or a list off the binding, is a **break**: a seal-wide marker first, then a mirrored
     line, terminal for every role of the seal.
   - A link or environment failure refuses and spends nothing. That covers a missing end line, a non-zero exit, an
     unreadable path, a missing root, an unexpected line, or an answer count that doesn't match the paths.
5. **The spend, under the lock.**
   - Absorb any markers.
   - Run **step 2 again**.
   - Create the attempt marker, `MARK-attempt-<key12>-<role>` (O_EXCL, fsynced).
   - Append `spent` and fsync the file and the directory.
   - Commit the record path and push.
   - Fetch, require the remote blob to equal the local record, and keep a published ref.

   Any failure from the attempt marker on blocks the role for good, and a lock failure leaves an uncertain marker.
6. **The launch.** The frame is written unbuffered and then zeroed, and the outcome is recorded:

   | What happened | Outcome |
   |---|---|
   | exit 0 with the whole frame delivered | `completed` |
   | exit 66 | `break` (seal-wide) |
   | anything else, including an undelivered frame, a dropped link or an interrupt | `terminal` |

   Nothing retries.

**`reveal`:**
- The seal and the commitment must be the binding's.
- It requires a `pv-readout` outcome line for the seal, or `--after-stop '<named stop>'` (plain words only).
- The seed base and salt must reproduce the commitment.
- The `reveal` line is recorded before anything is printed, and it stops every PV role of the seal for good.

**Exit codes:** 0 done; 2 refused (nothing spent); 3 terminal; 4 usage or environment error.

**Mirror commits and pushes run without the repository's hooks** (`core.hooksPath=/dev/null`; `"run_hooks": true`
turns them on). They touch one path on a dedicated branch, before decryption, and a hook failure there would be an
uncertain spend that burns the role. **The remote should forbid force pushes and deletion of that branch** (a
branch-protection rule on the host). The wrapper detects a rewind or deletion it has seen, but it cannot prevent one.

**Limits, disclosed.** All of this rests on the declaration's cooperative assumption of one shared account (§4.2).

- A session that deletes the local record, the markers, the published and seen refs, and rewinds the remote can
  defeat the history checks.
- Between the login-node checks and the task's own reads, a cluster file could be swapped. The compute-side exec check
  narrows this for the binary. The bound readout re-verifies the freeze and the chain itself (§3.4 point 5).

## Tests

```
cd docs/orchestration/state/2d-closeout/covfix-20261122/wrapper
python3 -W error::ResourceWarning -m unittest test_covfix_wrapper
```

The tests:
- use only `covfix-test-<random>-*` Keychain items in the login Keychain, which they create and delete;
- set `COVFIX_FORBID_REAL_KEYCHAIN=1`, so the real `covfix-` prefix refuses;
- stub ssh, salloc and srun locally;
- run git with no global or system config and the file transport only;
- seal only synthetic truths, so no test is a launch.

## The synthetic seal and the director's rehearsal (§3.4)

`synthetic-seal --keychain-prefix covfix-synth- --out DIR` refuses the real prefix. It builds:
- a dummy truth, encrypted with the pinned flags;
- an encrypted manifest of plaintext hashes;
- a decrypt round trip;
- `PG-SEAL.sha256` over the ciphertexts;
- a dummy `P2-FREEZE.sha256`.

It prints the two digests and the two roots.

**The rehearsal on the cluster** is the director's to run, after cov2d's bound writer and readout exist:

1. `generate --keychain-prefix covfix-synth-`, then `synthetic-seal --keychain-prefix covfix-synth- --out DIR`.
   Copy `DIR/sealed` and `DIR/frozen` to the cluster.
2. Write a rehearsal role config:
   - `keychain_prefix`: `covfix-synth-`;
   - `record_dir`: a fresh mode-700 directory, not the real one;
   - mirror branch: a fresh rehearsal branch;
   - `binding`: the two printed digests;
   - roles: the bound writer and readout, with their launchers.
3. Run `pv-writer`, then `pv-readout`. Record each allocation's job ID and elapsed time (`sacct -j <id> -o
   JobID,Elapsed,State`) in the rehearsal record. §3.4 has these two times replace its 1.0 node-h estimate for PV in the re-price.
4. Check that a second run of each role exits 3, and that `status` shows spent and completed for both.
