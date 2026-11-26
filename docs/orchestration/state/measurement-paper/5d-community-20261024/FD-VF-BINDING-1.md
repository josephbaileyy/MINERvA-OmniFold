# FD-VF BINDING 1: the V_F recompute, Phase 1, one login-node connect, 0 node-h (director, 2026-11-25)

**Authority:** Joseph, 2026-11-25. Option C for the 5D fluctuation block, with B as the fallback and a checkpoint at
2026-11-28T00:00Z (`docs/orchestration/DECISION-20261125b-joseph-5d-unbinned-release-cinfl-naming-wording.md` §1,
#1338). The same record's §2 fixes the names C_e^infl and ΔC_e and the per-cell σ layout. The declaration is
`FD-VF-ADDITION-DECLARATION.md` (#1334), sha256 `31662736e85f83e3772722fa9ec633ae4f8a9add2fd37c111b801f058dcfe39f`. Amendments A1, A2 and A3 are bound below.

**Binds:**
- **the code**, as merged in PR #1345 (merge `8a7f9f7f64e9fd0725b51d1548ae868686aff89f`, reviewed head `64a93e93`,
  code commit `c0fa0d01aa05d5b6bb9793919768491d8d8a0c23`, which the connect clones);
- **the launch files and A3**, as merged in PR #1350 (merge `a98781f4e11b72a2ae24439dc267ed379f5d6bf2`, at the reviewed head `b654a3d47b9706aae8fd97d8dbda30735b686e23`).

Both were merged with `--match-head-commit`. The namespace is **`/pscratch/sd/j/josephrb/vf-20261125-p1`**. The
`connect-vf-p1.sh` that #1345 merged (`c65ccbcd…`) is superseded and is not bound.

| file | sha256 |
|---|---|
| `nd-unfolding/fd_vf_addition.py` | `3ba320bd8f3de0f2a873e882e327a868a8a385a0a13a511f105a606cc8b77487` |
| `FD-VF-ADDITION-AMENDMENT-A1.md` | `59cd712fe5dbdf94180339f4500b44bce89d3c8b34e728952acb5de36b3c689b` |
| `FD-VF-ADDITION-AMENDMENT-A2.md` | `1c3b150a5b186fa24e21df81dce9c7638fcd27abe837ea3ffaf745811ccbdb78` |
| `FD-VF-ADDITION-AMENDMENT-A3.md` | `c777f0c44a2bd5ec953bad041e2e7d7cddfd9d0c290772e8a619091e23e7edc1` |
| `fd/receipts-vf/p1/connect-vf-p1.sh` | `9cda83f0730350c5e4d73921290c41b127c1299478cc8a49130c33bfe4d48e2f` |
| `fd/receipts-vf/p1/stage-vfp1.sh` | `f05a3e853253fdc088848787c0e590623e233ebda6b4ed2eee2b64375cc712ce` |
| `fd/receipts-vf/p1/test_connect_vf_p1.py` | `6fc95a5388482b02736f35bd5ffea1d69393116bc54904b8bb4d87d24ccfb889` |
| `nd-unfolding/tests/test_fd_vf_addition.py` | `a7503fe6b8465b449f729c09eac51b261b11fbc4a86c26989f8a69940ca9b419` |
| `fd/with-vf/block/vf_block.npz` | `cef8460a1dcc0db64f536af0099db1e1523ed2601d5c8ecc682afc0f9440c99b` |
| `fd/with-vf/block/vf_block.json` | `421da0e683537ad0a47b684e5e6ae42f7f3d63d6cc6038e03671dc7772edb6bd` |

The `FD-VF-*` and `fd/` files are under `docs/orchestration/state/measurement-paper/5d-community-20261024/`.

## What the director checked

- **The shas.** Each file above was hashed from `git show` at main after #1350's merge. Each equals tier3-design's
  binding request. Nothing under `nd-unfolding/` changed after `c0fa0d01`.
- **Amendment A1's routing section, read directly:**
  - in the OLD arms, downstream steps read the committed upstream readouts at their declared digests;
  - the V_F arms read the chain's own outputs;
  - the staged chdefs manifest must be `a45438fa…` and the loaded spec must equal the committed
    `predictions-chdefs.json` before any step;
  - the chain refuses unless the renderer is E-A2's (python 3.11.14, numpy 1.26.4, matplotlib 3.10.8, root_6_28 on
    the login node).
- **Amendment A3, read directly.** On the node, the ten modules run whole, plus test_fd_gencmp_e's Sets, Stage,
  Materialize and Chain: exactly 541 tests, with no skip. Only StepCR's 9 tests are excluded, because root_6_28 has no
  uproot. `fd_vf_addition.py` uses only `E.step_pins`, `E.Paths` and `E.load_chdefs`. StepCR passes locally in the
  317-test run at `1513e63d` (receipt `2675ade6…`).
- **The connect script, read directly.** It refuses unless the host is login02 and claims the namespace with
  `mkdir`. TMPDIR and the caches live under the namespace. It clones with `--no-checkout` and detaches at `c0fa0d01`.
  - Every gate needs both its command's success and the expected output. That covers an empty porcelain (with all
    untracked files shown), exactly 22 blob ids, conda by `CONDA_PREFIX` and the python3 path, and the exact
    environment string.
  - The test gate reads unittest's stderr: exactly one `Ran` line, then a closing block of `Ran 541 tests` and `OK`.
  - The chain runs under `timeout 3600` with `python3 -I -B`. A receipt failure exits 7 and a dirty deploy exits 8.
  - It writes only under the namespace, and removes nothing it did not create.
- **The stager, read directly.**
  - It embeds the connect's bytes in base64. The director decoded them by command: they equal the committed
    `connect-vf-p1.sh` (`9cda83f0…`), as does the stager's WANT.
  - `start` refuses if a V_F chain or worker is running, if the namespace exists, or if either /dev/shm file exists.
    It creates `/dev/shm/vfp1.sh` and `/dev/shm/vfp1.log` exclusively, checks the copy's sha256, and runs it as
    `nohup setsid nice -n 19 bash` inside a wrapper that logs its start and exit. It never signals any process.
  - `finish` checks that the pair is its own (the header, the sha256 and both markers) and that no worker is
    running. It copies the log into `$BA/receipts/` with a sha256 receipt, removes only the two /dev/shm files, and
    exits with the worker's status.
- **The reads and checks, as the lane reported them:**
  - for the code: codex-school gpt-6.2-sol re-read 4 GO, delta read 5 NO-GO (fixed), delta read 6 GO, and
    claude-personal Sonnet 5.5's re-read GO. Its tests are 88, with no skip, plus the 317-test neighbour suites, and
    its mutants were 88/88 killed;
  - for the launch files: codex-school reads 1–6 NO-GO, each fixed, and read 7 GO, with two MINORs disclosed
    (`fd/receipts-vf/p1/reads/`). The dry-run tests number 56, all passing. A3 changed after read 7 only in its
    "Declined" paragraph, which now cites GENCMP E run1's omnifold_py310 test log in place of its earlier wording.
- **CI.** record-checks passed on both reviewed heads.

## Rulings

1. **Phase 1 is bound** with the shas above: the code, A1's routing section, A2, A3, the connect script and the
   stager. Any changed byte goes back to the director.
2. **`rel_sigma_DeltaC_e` in the product's cells CSV stays.** Joseph's "no ΔC_e column" (DECISION-20261125b §2)
   governs the per-cell σ table the note prints. The cells CSV is a build record. If the note or a deposit table is
   ever printed from it, the column is dropped there.
3. **The price: 0 node-h.** One connect on login02, with no Slurm job. Job state comes from sacct only. Nothing is
   written to CFS, and every write is under the namespace except the stager's two /dev/shm files. The invocation is
   `ssh saul.nersc.gov "ssh -o BatchMode=yes login02 'bash -s -- start'" < stage-vfp1.sh`. It is followed by short
   read-only polls (the log, `$BA/receipts/host.txt`, `ps`), each preceded by a certificate check, and then
   `… 'bash -s -- finish'`. The lane's wall-time estimate is 25–35 min, with 40 min as the worst case.
<!-- absence-ok: preconditions checked fresh before the connect (acks, a valid certificate, the director's GO), not claims that a result does not exist -->
4. **Preconditions, all required, before `start`:**
   - a valid NERSC certificate, checked by command, with enough time left for the whole connect plus `finish`. A
     connect that cannot finish before expiry waits, and no session is used past its credential's expiry;
   - fresh acks from cov2d, limitation-resolver and director-helper-3, each read by `date -u`. The window ends 900 s
     after the oldest ack;
   - limitation-resolver told immediately before `start`;
   - the director's GO, by message, naming this binding.
5. **The EVW5D inputs.** tier3-design's static reading is that Phase 1 opens none of EVW5D's three inputs. The
   director accepts it, so the two runs need no ordering. After the run, the lane greps every step log for the three
   paths and reports any hit to the director at once.
6. **One connect.** Any STOP or refusal after contact is terminal, and nothing is rerun without the director. If
   `start` reports UNCONFIRMED, the lane polls read-only and does not start again. END messages go to the fenced lanes
   after `finish`.
7. **The record goes to the director first.** Nothing enters the note until the director has reviewed the readings.
   JE carries A2's names, the table and Joseph's two sentences when they land. The wording is Joseph's.

**CITABLE FOR:** that V_F Phase 1 was bound, and on what. **NOT CITABLE FOR:** any covariance, factor, reading, coverage
statement or note wording.
