# ~/director-tools/covfix/ (secret-free)

This directory is mode 700 and holds no secret. It contains:

- ST4's consumption record, `RECORD.jsonl`: append-only and hash-chained;
- its lock;
- the `MARK-*` markers;
- the installed `covfix_wrapper.py`, with its sha256 in `INSTALLED.sha256`;
- this README.

The record is mirrored by a commit, pushed before any decryption, on the branch the role config names. That remote
branch should be protected against force pushes and deletion.

## The secrets (macOS login Keychain, account `director`)

| Service | Item |
|---|---|
| `covfix-passphrase` | the gpg passphrase: 64 lowercase hex (32 random bytes) |
| `covfix-seed-base` | PG's seed base: ASCII decimal, uniform in [1 000 000 000, 2 000 000 000) |
| `covfix-salt` | the commitment salt: 64 lowercase hex (32 random bytes) |

- **Who reads them.** Only the wrapper, with `security find-generic-password -s <service> -a director -w <login
  keychain>`.
- **Never pass `-U`, delete these items or copy them.** Losing the passphrase makes the ciphertext unrecoverable, and
  there is no regeneration. Losing the seed base or the salt breaks the commitment reveal.
- **Test and rehearsal items.** The tests use `covfix-test-*` and the rehearsal uses `covfix-synth-*`. Neither touches
  the items above.

## Markers (never delete one)

| Marker | Meaning |
|---|---|
| `MARK-attempt-<key12>-<role>` | written before every spend; it keeps the role blocked through any later crash |
| `MARK-uncertain-<key12>-<role>` | the lock or the record failed; the role is blocked |
| `MARK-break-<key12>-seal` | a confirmed break; every role of the seal is blocked |

Each marker enters the record at the next locked write.

## Procedure (each step is the director's)

1. `python3 covfix_wrapper.py generate`.
   - It prints `created`, or `exists` when all three items are already there.
   - If only some are present, it exits 4 and names them, never their values, and changes nothing. That is the
     director's to resolve.
   - The values never appear on any argument vector.
2. `python3 covfix_wrapper.py commitment`. Publish the digest it prints (sha256 of `<seed base>:<salt hex>`, no newline)
   before PG generates.
3. Write the role config. `role-config.example.json` in the repo shows the shape.
   - `binding`: the commitment, and at PV binding the seal and freeze digests;
   - record directory: this one;
   - mirror: a dedicated worktree on a dedicated, protected branch;
   - per role: the launcher, the absolute binary and its sha256, and the args.

   Pin the config's sha256 in the binding. PV's config is a new file with a new pin.
4. PG: `run --role pg-connect --config C --config-sha256 X --commitment <the binding's commitment>`.
5. PV writer: `run --role pv-writer --config C --config-sha256 X --seal-digest <binding> --freeze-digest <binding>`.
6. PV readout: the same arguments with `--role pv-readout`. It refuses until the writer has completed.
7. After PV's readout: `reveal --config C --config-sha256 X --seal-digest S --commitment <binding>`.
   - It prints `seed_base=` and `salt=` for publication, and stops every PV role of the seal for good.
   - If PV never reaches the readout, add `--after-stop '<the named stop, plain words>'`.

Each role runs once. A second run, or any run after a marker, a break or a reveal, exits 3 (TERMINAL). To see where
the campaign stands without touching the cluster, run `status --config C --config-sha256 X`. It prints the record
lines and markers.

**Exit codes:** 0 done; 2 refused (nothing spent: fix and retry); 3 terminal (the role or the seal is stopped: take it
to the director's ruling, never retry); 4 usage or environment error.
