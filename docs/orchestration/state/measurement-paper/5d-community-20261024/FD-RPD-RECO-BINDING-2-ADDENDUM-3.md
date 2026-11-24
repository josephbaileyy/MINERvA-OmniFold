# BINDING 2, ADDENDUM 3: the P0 package (rpd_p0), rebuilt on flux3's records (director, 2026-11-23)

**Authority:** Joseph via the director, 2026-11-22 (e1). It extends addendum 2, whose ruling 6 said P0 gets its own
binding once it is rebuilt on flux3's records with findings 1–9.

**Binds** the P0 package as merged to main in PR #1271, at **M_P0 =
`13aee9c05c7c36cf1cf1e642d58244400932e841`**. There, `fd/rpd-reco/p0-20261123/` is the tree of the read head
`094ab6c9d4b592c2f71b23c714e157e53b8546a9`, merged with `--match-head-commit`.

| file (under `fd/rpd-reco/p0-20261123/`) | sha256 |
|---|---|
| `production-config.ready.json` | `3b2afde495d630cc44df730e3e1acf12e0c332953e9fa298fa979f2e2e39b057` |
| `rpd_p0_connect.sh` | `6a1bed9547b7a462b3ccdbbe05c34f322a27980be085d2996eb89950a25da678` |
| `rpd_p0_fetch.sh` | `12626af6f6ff5d765b602ebd0f012f2e3d6f8d3f1fa60969b0f8bd4d4e022b6a` |
| `rpd_p0_launch.sh` | `b70998fffa5de0f585ef3e60e24b17c7ba166bc10e718d13187e424928e4e366` |
| `tools/p0_supervise.py` | `6ad0f68fb309a7b83adc0f65ed709e5e2412e650e115075fe41ebbc7a070134f` |
| `tools/p0_checks.py` | `93d0de8bda48a00eeba4edab306590146f5c1d807bed701be021bdfb0b864fcc` |
| `tools/p0_expected.json` | `bb175e948fff89fc1e3097b0aaf5107e5e796bc05e1f4892e0d00b07b2a5b6b6` |
| `tools/fence_overlap.py` | `23d0ffc7bf89a4b81a33b081fa7377401dec33634372d5ed5b106bee6c4fd22b` |
| `tools/gen_p0.py` | `07395b1d4f9e6e94fc2dda858ba318b9f707ac90b436def5a0fa33e9c1b0d1bf` |
| the runner `rpd_p0_runner.sh`, written by the connect (its lines 188–331) | `3ef4abad4f05a8ef9fb5319c6d463d72e5ecabb3bed75defa74c712a28df07c4` |

**The code.** The connect clones `S = 6896e7871421469ce72c6b93188d2d1a55c82ec6`, flux3's clone, with flux3's 14 pins
(addendum 2): custody `634670b3`, `fd_rpd_reco.py` `7302cc1d`, and the rest unchanged.

## What the director checked

- **The shas.** The director hashed each file above from `git show` at the read head, and each equals the table. The
  runner's sha256 is the director's hash of the connect's heredoc body.
- **The five embedded payloads** (the config, `p0_checks.py`, `p0_expected.json`, `p0_supervise.py` and the fence copy)
  were decoded by the director from the connect, and each decodes to its sha256 above.
- **The config's leaf diff against flux3's `d797183b`,** from the director's own JSON walk, is exactly two leaves:
  - `flux_extract/sha256`: null → `90445ece…`;
  - `flux_custody/sha256`: null → `226c7a68…`.

  Both equal the director's hash of the committed `flux3-20261123/run-61861637/records/run/flux-extract.json` and
  `flux-custody.json`, and both appear in that run's `SHA256SUMS`.
- **No squeue** in the connect, the fetch, the launcher or the runner. `gen_p0.py` names it only in three assertions
  that it is absent.
- **Threads 1** for OMP, OpenBLAS, MKL, NumExpr and vecLib, exported in the runner, and the runner and its checks run at
  nice 19.
- **The ancestors** `1a015eef` and `3c3a6f74` are ancestors of the read head.
- **The test receipts** at the read head:
  - the sacct fence: 24 checks, 17/17 mutants;
  - the launcher: 23 cases, 13/13;
  - the connect startup: 4 cases, 6/6;
  - the runner: 25 cases, 22/22;
  - the fetch: 20 cases, 12/12;
  - `p0_supervise.py`: 17 passed;
  - `p0_checks.py`: 6 passed;
  - the overlap fence: CLEAR over 57 staged originals.
- **The reads.** agy gave GO on the package and on confirms 1 and 2. codex-school2 gave FIX on the package and on
  confirms 1–3, with every blocking item fixed, and GO on confirm 4 (`abf3b10c…`).
- **The delta after confirm 4.** The director diffed confirm 4's inputs against the read head, and read it:
  - in the runner, the three deadline checks now call one `past_deadline` function. Its probe answers 10 or 11, and
    any other status is its own STOP (`clock-check`, rc 4), never a wall cap. All three calls are in a condition, so a
    status of 11 cannot end the shell;
  - the launcher's pin of the connect moves to `6a1bed95…`;
  - `gen_p0.py` carries the same runner text;
  - two tests are stronger, and one new runner case is killed by its new mutant (`probe-failure-as-not-passed`);
  - the README changes.

  The change answers confirm 4's note 4 and fails closed, so the director ruled that no fifth read is needed.

## Rulings

1. **P0 is bound** at M_P0 with the shas above. Any changed byte goes back to the director.
2. **The price is 0 node-h** (binding 1, ruling 3; declaration §5):
   - it runs on one login node, with no job and no job-name family;
   - threads 1, nice 19, O_NOATIME reads, from a fresh clone at S;
   - nothing is written to CFS;
   - the chain has one deadline, 7200 s after the handoff. If it is reached, that is a wall-cap STOP, and moving P0 to
     a compute node is priced to the director first.
<!-- absence-ok: preconditions the connect itself checks at run time (a fresh run root, no unended fenced job), not claims that a result does not exist -->
3. **Preconditions at the connect, all required:**
   - The launcher's ack file holds cov2d's ack verbatim, under an `ACK-UTC` first line no more than 6 h old.
   - tier3-design's ack.
   - The cert check passes. Joseph renewed the cert, valid to 2026-11-25T01:36:35Z. The README's earlier date is stale,
     and the launcher's check is the authority.
   - The connect's sacct fence and `fence_overlap.py` read CLEAR.
   - `/pscratch/sd/j/josephrb/rpd-reco-p0-20261123` does not exist yet.
   - The connect's sha256 named in the director's GO equals the table's.
4. **The `ibuchi_` family stays out of the fence,** as the director agreed before the rebuild. Its write roots are
   disjoint from P0's, and P0's input checks compare sha256, bytes and inode. **director-helper-3's IBUB lane
   (`ibub_`)** has not been given a GO. Its binding, when written, must keep its write roots disjoint from P0's two
   roots, `/pscratch/sd/j/josephrb/rpd-reco-p0-20261123` and `/dev/shm/limres-rpd-flux1`.
5. **The product.**
   - The in-place input check must find flux3's extract, custody record and 12 factor products equal to
     run-61861637's records.
   - The retention record must find the three gen2thin files and the 24 dumps with S1's bytes and inodes.
   - Both dry runs and both real steps must exit clean under the supervisor.

   Any difference is a STOP to the director, not a reading.
6. **Any STOP or guard refusal after contact is terminal.** A local refusal before any ssh is reported, and nothing is
   retried without the director's word.
7. **Next:** the fetch until DONE or STOP, a records PR, and then the director's merge. P0's records are read before
   step0 is bound.

**CITABLE FOR:** that P0 was bound, and on what. **NOT CITABLE FOR:** any RPD-RECO result, any note wording.
