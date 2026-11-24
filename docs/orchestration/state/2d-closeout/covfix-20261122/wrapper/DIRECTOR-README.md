# ~/director-tools/covfix/ (secret-free)

This directory is the canonical COVFIX ledger. It is mode 700 and holds no secret. It contains:

- ST4's consumption record, `RECORD.jsonl`: append-only and hash-chained;
- `LEDGER.json`, the mirror's remote URL, branch and path, fixed at first use;
- the lock;
- the `MARK-*` markers;
- the installed `covfix_wrapper.py`, with its sha256 in `INSTALLED.sha256`;
- this README.

The record is mirrored by a commit, pushed before any decryption, on the branch **`covfix-ledger`**. That branch holds
only the record, and it should be protected against force pushes and deletion (Joseph's repository setting).

## The secrets (macOS login Keychain, account `director`)

| Service | Item |
|---|---|
| `covfix-passphrase` | the gpg passphrase: 64 lowercase hex (32 random bytes) |
| `covfix-seed-base` | PG's seed base: ASCII decimal, uniform in [1 000 000 000, 2 000 000 000) |
| `covfix-salt` | the commitment salt: 64 lowercase hex (32 random bytes) |

- **Who reads them.** Only the wrapper, with `/usr/bin/security find-generic-password -s <service> -a director -w
  <login keychain>`.
- **Never pass `-U`, delete these items or copy them.** Losing the passphrase makes the ciphertext unrecoverable, and
  there is no regeneration. Losing the seed base or the salt breaks the commitment reveal.
- **Test and rehearsal items.** The tests use `covfix-test-*` and the rehearsal uses `covfix-synth-*`, with their
  own ledgers. Neither touches the items above.

## Markers and lines that stop things (never delete one)

| Marker or line | Effect |
|---|---|
| `MARK-attempt-<key12>-<role>` | written before every spend; it keeps the role blocked through any later crash |
| `MARK-uncertain-<key12>-<role>` | the lock or the record failed; the role is blocked |
| `MARK-break-<key12>-seal`, or a `break` line | every role of the seal is blocked |
| a `reveal` line | every PV role of the seal is stopped, and `pg-connect` for the commitment |
| `freeze-mismatch-refused` lines | spend nothing; two unresolved ones on a seal block every role until `--freeze-mismatch-resolved <ruling id>` |

## Procedure (each step is the director's)

1. `python3 covfix_wrapper.py generate`.
   - It prints `created`, or `exists` when all three items are already there.
   - If only some are present, it exits 4 and names them, never their values, and changes nothing.
2. `python3 covfix_wrapper.py commitment`. Publish the digest it prints before PG generates.
3. Write the role config (`role-config.example.json` in the repo shows the shape):
   - `record_dir`: `~/director-tools/covfix`;
   - mirror branch: `covfix-ledger`;
   - `binding`: the commitment, and at PV binding the seal and freeze digests;
   - roles: the absolute binary, its sha256, the args, and a `slurm` block for each PV role.

   Pin the config's sha256 in the binding. PV's config is a new file with a new pin.
4. PG: `run --role pg-connect --config C --config-sha256 X --commitment <binding>`.
5. PV writer: `run --role pv-writer --config C --config-sha256 X --seal-digest <binding> --freeze-digest <binding>`.
6. PV readout: the same arguments with `--role pv-readout`. It refuses until the writer's completion is in the pushed
   record.
7. After PV's readout: `reveal --config C --config-sha256 X --seal-digest S --commitment <binding>`.
   - It prints `seed_base=` and `salt=` for publication.
   - If PV never reaches the readout, add `--after-stop <stop id>`.
   - If a role was spent and never recorded an outcome, add `--inflight-resolved <ruling id>` after your ruling.

Each role runs once. A second run, or any run after a marker, a break or a reveal, exits 3 (TERMINAL). To see where the
campaign stands without touching the cluster or the Keychain, run `status --config C --config-sha256 X`.

**Exit codes:** 0 done; 2 refused (nothing spent: fix and retry); 3 terminal (the role or the seal is stopped: take it
to the director's ruling, never retry); 4 usage or environment error.
