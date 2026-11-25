# COVFIX director's wrapper (`covfix_wrapper.py`)

The wrapper runs COVFIX's secret-bearing roles under three sections of the declaration: ST4 (validation is spent once),
§3.4 (who runs the writer and readout, and the synthetic-seal test) and §4.2 (custody). It is the director's tool:
cov2d writes and tests the bound PG and PV code, and it never runs these roles. The wrapper holds no physics. It
guards three things: the secrets, the consumption record, and the order of operations around them.

This directory holds:

- `covfix_wrapper.py`, the wrapper (stdlib only; it needs `security`, `gpg`, `git` and `ssh`);
- `reference_role.py`, a reference bound binary. It is the interface's other side, used by the tests and the synthetic
  seal, and it is not PG or PV code;
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

**Arguments:**
- first, the config's `args`;
- then the wrapper's own `--covfix-attempt <32 hex>`;
- for the PV roles, also `--covfix-seal-root <dir> --covfix-freeze-root <dir>`. These are the roots the wrapper just
  verified, and the binary must read from them.
- for `pg-connect`, the config's `args` are covfix_pg's own, as COVFIX-DECLARATION rev 12 §4.2 records them:
  `--workdir <empty dir> --sealed <new dir> --gen-spec <file> --gen-spec-sha256 <64 hex> --gpg <path> --gpgconf <path>
  --gpg-sha256 <64 hex> --gpgconf-sha256 <64 hex>`. The wrapper adds `--covfix-attempt`. Since the role config is
  sha-pinned in the binding, so is `--gen-spec-sha256`; covfix_pg refuses a gen-spec whose bytes do not hash to it.
  The wrapper checks only that `args` is a list of strings with no `--covfix-*` entry, so covfix_pg checks the rest.
- covfix_pg refuses unless every `env_keep` name in the gen-spec is set in its environment. The wrapper sets no
  variable and unsets only the six Slurm I/O variables, so what Slurm sets in the task, such as `SLURM_JOB_ID` and
  `SLURM_CPUS_ON_NODE`, passes through. Any other listed name must already be set in the cluster account's login
  environment.

**stdout, last line:**
- `covfix-receipt <attempt>` after the role's work succeeded. Without it the run is terminal, even at exit 0.
- `covfix-break <attempt>`, with exit status **66**, for a confirmed integrity break of its inputs, manifest or chain.
  That is recorded as a break of the whole seal. Exit 66 without the line is only a role-terminal outcome.

**The binary must also:**
- hand the passphrase to gpg on **fd 3** through an internal pipe, with §4.2's pinned flags and a fresh empty
  `GNUPGHOME`;
- use no decrypted byte before gpg exits 0;
- print no secret, and disable core dumps;
- **check every ciphertext it opens against its `PG-SEAL.sha256` entry before decrypting it.** The wrapper verifies
  the listed files and requires the list to include `PG-MANIFEST.json.gpg`, but it cannot see which products the
  manifest names;
- report only a **confirmed** break as `covfix-break`: a missing file (ENOENT), or content that fails its pinned hash
  or the manifest's schema. An access or storage error (EACCES, EIO, an unavailable mount) is a role failure
  (non-zero exit, no break line).

`reference_role.py` does all of this.

**The launch is built by the wrapper from validated fields, never from a command string.** Each role's `slurm`
block may name `salloc` and `srun` (paths ending in those names) and set `account`, `qos`, `constraint` and `time`,
with plain values. The wrapper runs:

```
/usr/bin/ssh <the forced options> -l <user> -i <identity_file> [-o CertificateFile=...] <host> \
  'env -u SRUN_INPUT -u SRUN_OUTPUT -u SRUN_ERROR -u SLURM_STD{IN,OUT,ERR}MODE \
   salloc --exclusive -N 1 -n 1 -J covfix_<role> [-A -q -C -t] srun --exclusive -N 1 -n 1 \
   bash -c <exec check> covfix-exec <binary> <sha256> <args> --covfix-...'
```

That is one task on one exclusive node. The exec check runs on the compute node: it hashes the binary and execs it only
on a match (exit 86 otherwise), leaving stdin untouched. The job name is a constant per role in the code (`JOB_NAMES`: covfix_pg_connect, covfix_pv_writer, covfix_pv_readout), never from config or input, so fences and sacct can recognize covfix jobs; the config cannot set `-J`. Every role runs this way, `pg-connect` included: its role config needs the same `slurm` block (cov2d, 2026-11-25; before, `pg-connect` had no allocation and would have run on the login host).

**ssh is built by the wrapper from a closed schema (director, 2026-11-23).** The role config's `ssh` object may hold
only these keys; any other key is refused:

| Key | Rule |
|---|---|
| `program` | must be `/usr/bin/ssh` for the real items |
| `user` | a plain user name |
| `identity_file` | absolute, literal, a regular file owned by this user |
| `certificate_file` | optional; absolute, literal, a regular file owned by this user |
| `agent` | optional, a boolean |

`host` is a plain host name. The wrapper's argv is exactly:

```
/usr/bin/ssh -F none -T -o RequestTTY=no -o StrictHostKeyChecking=yes -o BatchMode=yes
  -o PreferredAuthentications=publickey -o PasswordAuthentication=no -o KbdInteractiveAuthentication=no
  -o IdentitiesOnly=yes -o ControlMaster=no -o ControlPath=none -o NoHostAuthenticationForLocalhost=no
  -o PermitLocalCommand=no -o ProxyCommand=none -o ProxyJump=none
  -o UserKnownHostsFile=<home>/.ssh/known_hosts -o GlobalKnownHostsFile=/dev/null
  -l <user> -i <identity_file> [-o CertificateFile=<certificate_file>] <host> <command>
```

With `-F none`, no ssh_config is read.

**One trust anchor.** ssh would otherwise also accept a host key listed in `~/.ssh/known_hosts2`,
`/etc/ssh/ssh_known_hosts` or `/etc/ssh/ssh_known_hosts2`. The wrapper names exactly one host-key file:
`<home>/.ssh/known_hosts`, where `<home>` comes from the password database and must be a literal path. The global file
is `/dev/null`. For the real items, `known_hosts` must be a regular file owned by this user.

ssh starts from an **empty environment** plus:
- `HOME`, this user's home from the password database, never the launch environment's;
- `PATH=/usr/bin:/bin`;
- `LANG=C`;
- `SSH_AUTH_SOCK`, only if the config declares `"agent": true`.

`SSH_ASKPASS`, `DISPLAY`, `LD_*` and everything else are therefore absent by construction. The wrapper's own `security`
calls run in the same minimal environment.

For NERSC:

```
"ssh": {"user": "<user>", "identity_file": "/Users/<user>/.ssh/nersc",
        "certificate_file": "/Users/<user>/.ssh/nersc-cert.pub"},
"host": "perlmutter.nersc.gov"
```

The certificate is named explicitly. Perlmutter's host key must already be in `<home>/.ssh/known_hosts`. No other file
is consulted.

Any `-t`, port forward or other option is refused. The frame goes on ssh's stdin, and the task's stdout and stderr
come back through the wrapper. Any passphrase or seed base in that output is replaced by `[redacted]`, and the run is
then terminal.

## The binding and the ledger

The role config is pinned by sha256 in the binding (`--config-sha256`). Its `binding` block pins three digests:
- `commitment`;
- `seal_digest`, the sha256 of the committed `PG-SEAL.sha256`;
- `freeze_digest`, the sha256 of `P2-FREEZE.sha256`.

The digests given on the command line must equal these.

The real items (`covfix-`) use one canonical ledger, `~/director-tools/covfix`, and take no `security` or
`keychain` override. At its first use the ledger writes `LEDGER.json`, recording the mirror's remote URL, branch and
path. A config pointing elsewhere is refused, and a ledger that has records but no `LEDGER.json` is terminal. For the
real items the mirror branch must be **`covfix-ledger`**, a dedicated branch that holds only the consumption record.
A shallow mirror clone is refused, because its history cannot be scanned.

**`covfix-ledger` is protected** by GitHub ruleset 27996874, "covfix-ledger append-only" (requested by Joseph, set 2026-11-24). It is
active with no bypass actors, and its rules are `non_fast_forward` and `deletion`. Creation and fast-forward pushes
are allowed, and those are the only pushes the wrapper makes: a plain `git push <remote> HEAD:refs/heads/<branch>`,
never forced. The wrapper does not rely on the ruleset. A refused push is an uncertain spend that blocks the role, and
a rewound or deleted branch is terminal, all before any launch (`LedgerProtectionTests`).

## Order of operations in `run --role R`

1. **Config.**
   - The config's sha256 is the pinned one, and its digests are the binding's.
   - The real items are on the canonical ledger.
   - The launch is built and validated.
2. **Local terminal states first.** A line or marker for (key, R) is consumed, and so is a seal-wide break or reveal.
   These checks run before any transport or mirror step, so a refusal there can't mask them.
3. **The mirror.**
   - The worktree is on its branch, with the record path clean, and `LEDGER.json` matches.
   - The remote tip, fetched to a commit id, must descend from the last-seen one; otherwise the branch was rewound,
     which is terminal. A vanished branch after any publication is also terminal.
   - The pushed record must be a prefix of the local one.
   - No commit reachable from any ref (full history) holds a line the local record lacks. That includes
     `refs/covfix/published/<ledger>/*`, which keep every published version.
4. **Spend conditions.**
   - Not consumed.
   - The freeze is the seal's bound one; the freeze-conflict rule below applies otherwise.
   - For `pv-readout`, a completed `pv-writer` in the pushed record.
5. **Secrets.** Read from the login Keychain and checked. For `pg-connect`, sha256(seed base ':' salt) must equal the
   commitment.
6. **The local lists.** `PG-SEAL.sha256` and `P2-FREEZE.sha256` must hash to the binding and parse. A failure is a
   break, found before any ssh call.
7. **The cluster.** The bound binary must hash to its pin, and every listed file is hashed on the login node, one typed
   answer per path. The outcomes:

   | Answer | Outcome |
   |---|---|
   | an altered file | a break, even if other paths were unreadable |
   | an unreadable path | refused |
   | none of the files found (wrong or unmounted storage?) | refused |
   | some files missing | a break |
   | incomplete or contradictory answers | refused |

8. **The spend, under the lock.** The record is read once, as the lock is taken, and every check in the transaction
   reads that snapshot. The append refuses if the file no longer matches it, and publishes the snapshot plus the new
   line, never a re-read of the file.
   1. Steps 3 and 4 again.
   2. The attempt marker, `MARK-attempt-<key12>-<role>` (O_EXCL, fsynced). If it can't be written, nothing is spent.
   3. Append `spent` (with the attempt id), fsync, commit, push, and fetch the remote record back; it must equal the
      local one. Keep a published ref.

   Any failure from the marker on blocks the role for good.
9. **A stop recorded during the spend wins.** If a break or reveal for the seal appeared meanwhile, the run is terminal
   and nothing launches.
10. **The launch.** The frame is written unbuffered and then zeroed. The outcome is recorded under the lock, with the
    mirror re-checked first:

    | What happened | Outcome |
    |---|---|
    | exit 0, the frame delivered, the receipt line present, no secret echoed | `completed` |
    | exit 66 with the break line | `break` (seal-wide) |
    | anything else | `terminal` |

    Nothing retries.

## The freeze conflict (director's ruling, 2026-11-23)

A freeze other than the one already bound to the seal is **refused (exit 2) and spends nothing**. A
`freeze-mismatch-refused` line, holding the presented and bound digests, is **appended, committed and pushed**, so the
attempt is visible.

It is not a break, because a configuration mistake must not burn a validation that can be spent only once.

Two unresolved refusals on one seal block **every** role of the seal, the right freeze included, until a director
ruling clears them with `run ... --freeze-mismatch-resolved <ruling id>`. The ruling itself is recorded as a line.
This way repeated attempts can't be retried silently. Neither line spends or binds anything. If the refusal cannot be
recorded, the run still refuses and marks nothing.

## reveal

- The seal and the commitment must be the binding's.
- It needs a **confirmed** `pv-readout` end in the pushed record, or `--after-stop <stop id>`. A confirmed end is
  `completed` or `break` carrying the **attempt id of the readout's spend**, so it is the task's own receipt or break
  line. A wrapper preflight break, or another invocation's line, does not end that task.
- It refuses while a PV role is spent with no confirmed end in the **pushed** record (in flight), unless
  `--inflight-resolved <ruling id>`. A local-only outcome whose push failed, and a `terminal` outcome, count as in
  flight. After a dropped link or a crash the task may still be running, so a `terminal` readout needs both
  `--after-stop` and `--inflight-resolved`, once the director has ruled.
- This eligibility is checked again under the lock, just before the reveal line is written.
- Stop and ruling ids are identifiers: a letter, then letters, digits, `.`, `_` or `-`, with no long hex or digit runs.
  So a pasted secret can't reach the mirror.
- The seed base and salt must reproduce the commitment.
- The `reveal` line (with the commitment) is recorded before anything is printed. It stops every PV role of the seal,
  and `pg-connect` for the commitment, for good.

**Exit codes:** 0 done; 2 refused (nothing spent); 3 terminal; 4 usage or environment error.

**Mirror commits, pushes and fetches run without the repository's hooks** (`core.hooksPath=/dev/null`;
`"run_hooks": true` turns them on). A hook failure there would be an uncertain spend that burns the role.

## Limits, disclosed

All of this rests on §4.2's cooperative assumption of one shared account.

- **A lock failure whose fallback marker also fails leaves nothing durable.** At that point nothing has been spent, so
  a retry after the storage recovers is harmless. The run exits 3 and says so.
- **A healthy seal root from which every listed file was deleted refuses (exit 2) rather than breaking.** The wrapper
  cannot tell it from an unmounted or wrong root, and refusing is the choice that does not burn a validation spent only
  once. A partial absence is a break.
- **Ciphertext-before-decrypt inside the task is the bound binary's job.** The wrapper verifies the listed files and
  requires the manifest's entry, but the products named inside the manifest are visible only to the task. So the task
  must check each ciphertext it opens against `PG-SEAL.sha256` before decrypting it (the interface rule above).

- A session that deletes the local record, markers, `LEDGER.json`, the published and seen refs, and rewinds the remote
  can defeat the history checks. Branch protection on `covfix-ledger` closes the remote half.
- Between the login-node checks and the task's own reads, a cluster file could be swapped, and the exec check reopens
  the binary by path after hashing it. The bound readout re-verifies freeze and chain itself (§3.4 point 5).
- The pass-through redaction catches the secrets verbatim only, not an encoded copy. The bound binaries must print
  none.


## Known limitations, accepted as non-blocking (director, 2026-11-23)

The final confirms judged each of these non-blocking: none can leak a secret, lose or double a spend, or spend validation
without a durable record.

- **Late uncertain marker from a lock contender.** Two runs of the same role can both pass the pre-checks. The one that
  loses the lock times out and writes an uncertain marker. If that marker lands after the winner's launch gate has read
  the markers, the winner still launches. The role is still spent exactly once, and the late marker only blocks
  further runs.
- **A reveal's recorded detail can omit a ruling.** If a role becomes in flight between reveal's first check and its
  locked re-check, the locked check accepts the `--inflight-resolved` ruling. The reveal line's detail, though, is
  built from the first check and may not name that ruling. The ruling id is still on the director's command line.
- **A refused reveal can leave one local-only line.** If reveal's locked re-check refuses after the lock absorbed a
  pending marker, that marker's line is in the local record but not pushed. The next locked write re-checks the mirror
  and publishes it (the local record still extends the pushed one).
- **A failed fd move in `gpg_run` skips its cleanup.** If moving the passphrase pipe above stdio fails (for example
  when descriptors are exhausted), the original read end stays open until the process exits, and the temporary
  `GNUPGHOME` is left on disk. Nothing secret is written there; the failure comes before gpg starts.
- **The ssh file checks run at setup.** The wrapper checks that `known_hosts`, the identity and the certificate are
  regular files owned by this user before ssh starts, and ssh opens them by path later. Swapping one of them in
  between needs this same account, which §4.2's cooperative assumption already trusts (confirm 6).

## Tests

```
cd docs/orchestration/state/2d-closeout/covfix-20261122/wrapper
python3 -W error::ResourceWarning -m unittest test_covfix_wrapper
```

The tests:
- use only `covfix-test-<random>-*` Keychain items in the login Keychain, which they create and delete;
- set `COVFIX_FORBID_REAL_KEYCHAIN=1`, so the real `covfix-` prefix refuses;
- stub ssh, salloc and srun locally; the stub remote gets a fixed list of environment names (PATH, HOME, TMPDIR,
  LANG and the test git settings), never the caller's whole environment;
- run git with every inherited `GIT_*` variable removed, no global or system config, an empty template and the file
  transport only;
- seal only synthetic truths, so no test is a launch;
- push only to local bare repositories, never to the real `covfix-ledger`. `LedgerProtectionTests` sets
  `receive.denyNonFastForwards` and `receive.denyDeletes` on one to stand in for the ruleset.

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
   - `record_dir`: a fresh mode-700 directory, not the canonical one;
   - mirror branch: a fresh rehearsal branch;
   - `binding`: the two printed digests;
   - `seal_root` and `freeze_root`: the cluster copies;
   - roles: the bound writer and readout, with their `slurm` blocks.
3. Run `pv-writer`, then `pv-readout`. Record each allocation's job ID and elapsed time (`sacct -j <id> -o
   JobID,Elapsed,State`) in the rehearsal record. §3.4 has these two times replace its 1.0 node-h estimate for PV in
   the re-price.
4. Check that a second run of each role exits 3, and that `status` shows spent and completed for both.
