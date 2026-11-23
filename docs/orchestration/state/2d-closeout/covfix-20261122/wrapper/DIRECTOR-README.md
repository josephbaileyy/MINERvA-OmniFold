# ~/director-tools/covfix/ (secret-free)

This directory is mode 700 and holds no secret. It contains:

- ST4's consumption record (`RECORD.jsonl`), append-only and hash-chained;
- its lock;
- any `UNCERTAIN-*` markers;
- the installed `covfix_wrapper.py`, with its sha256 in `INSTALLED.sha256`;
- this README.

The record is mirrored by a commit, pushed before any decryption, on the branch the role config names.

## The secrets (macOS login Keychain, account `director`)

| Service | Item |
|---|---|
| `covfix-passphrase` | the gpg passphrase: 64 lowercase hex (32 random bytes) |
| `covfix-seed-base` | PG's seed base: ASCII decimal, uniform in [1 000 000 000, 2 000 000 000) |
| `covfix-salt` | the commitment salt: 64 lowercase hex (32 random bytes) |

- **Nothing reads them but the wrapper.** It reads them with `security find-generic-password -s <service> -a director -w`.
- **Never pass `-U`, delete these items or copy them.** Losing the passphrase makes the ciphertext unrecoverable, and
  there is no regeneration. Losing the seed base or the salt breaks the commitment reveal.
- **Test items.** The tests use `covfix-test-*` and the synthetic seal uses `covfix-synth-*`. Neither ever touches the
  items above.

## Procedure (each step is the director's)

1. `python3 covfix_wrapper.py generate`. It prints `created`, or `exists` if any of the three items is already there,
   and then changes nothing. The values never appear on any argument vector.
2. `python3 covfix_wrapper.py commitment`. Publish the digest it prints (sha256 of `<seed base>:<salt hex>`, no newline)
   before PG generates.
3. Write the role config (`role-config.example.json` in the repo shows the shape) and pin its sha256 in the binding.
   - **Record directory:** this one.
   - **Mirror:** a dedicated worktree on a dedicated branch.
4. PG: `run --role pg-connect --config C --config-sha256 X --commitment <published digest>`.
5. PV writer: `run --role pv-writer --config C --config-sha256 X --seal-digest <sha256 of PG-SEAL.sha256> --freeze-digest <sha256 of P2-FREEZE.sha256>`.
6. PV readout: the same arguments with `--role pv-readout`. The freeze must be the one bound at the writer.
7. After PV's readout: `reveal --config C --config-sha256 X --seal-digest S --commitment <published digest>`.
   - It prints `seed_base=` and `salt=` for publication.
   - If PV never reaches the readout, add `--after-stop '<the named stop>'`.

Each role runs once. A second run, or any run after an uncertain spend or a break, exits 3 (TERMINAL). To see where the
campaign stands without touching the cluster, run `status --config C --config-sha256 X`. It prints the record lines
and markers.

**Exit codes:** 0 done; 2 refused (nothing spent: fix and retry); 3 terminal (the role or the seal is stopped: take it
to the director's ruling, never retry); 4 usage or environment error.
