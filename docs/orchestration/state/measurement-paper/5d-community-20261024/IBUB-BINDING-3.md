# IBUB BINDING 3: the readout (connect O), at M = b43a5b98, login node, 0 node-h (director, 2026-11-25)

**Follows** IBUB BINDING 2 (`IBUB-BINDING-2.md`, #1294). Job 61924744 ran under binding 2 and ended COMPLETED 0:0
(records in #1297 and #1317). Joseph put the IBUB readout (Ben's (a)) into arXiv v1
(`docs/orchestration/DECISION-20261125-joseph-v1-scope-option-i-weights-hydrogen.md`, #1326).

**Authority:** as for bindings 1 and 2. The declaration is `IBUB-DECLARATION.md`, sha256 `3aaf07f12b2ebfc747220704d675b752490dc64d42013324f0a42ff45e345262`, unchanged.

**Binds** connect O as merged to main in PR #1331 (merge `5cf25e484215d7ecab428f589d447ad86f642451`), at the reviewed head
`128042848fea1916442d3ca034668c7ab2a12a3b`, merged with `--match-head-commit`. The node clones
**M = `b43a5b984b28e68b6ea478b8a63329505c8f78be`**. The job is **61924744**; its commit
`d12c4f2a38a53001eb92bbefc8b2dc6001f034dc` is an ancestor of M. The namespace is
**`/pscratch/sd/j/josephrb/ibub-20261124`**.

| file | sha256 |
|---|---|
| `fd/receipts-ibub/connect/ibub_readout_connect.sh` | `5b3cdf7be868fbfb754b9c3f1f4b47cc218d3a80fd6b4ff34eb4ef60703d787d` |
| `fd/receipts-ibub/connect/ibub_readout_launch.sh` | `ed7c2578e1c497032b1afd338cda9d1c6b4411435accb45b254f362964808fb4` |
| `fd/receipts-ibub/connect/ibub_readout_connect.template.sh` | `c14fbc2726657f5611ca9af0c3dc48d19818e92ad7ce409c930920f88a3cdbab` |
| `fd/receipts-ibub/connect/ibub_readout_launch.template.sh` | `3ff1bfcad1cd75ce7b58f664b22d998357ec65066f6d3696232951fc3dce8202` |
| `fd/receipts-ibub/connect/gen_readout_connect.py` | `8ab29944135392cf8e987e4041289a1cc9d6dfd3dc89fb46f334c9bfabeb695e` |
| `2d-unfolding/ibub/ibub_readout.py` | `3a1e96e7f64b8a0ba833acb560767f327c62746ca4b689ca52213a859a26d5a8` |

The `fd/` paths are under `docs/orchestration/state/measurement-paper/5d-community-20261024/`.

## What the director checked

- **The shas.** Each file above was hashed from `git show` at main after the merge. Each equals director-helper-3's
  reported value. The launcher contains the connect's sha256 exactly once.
- **The regeneration.** In a fresh detached worktree at main, `gen_readout_connect.py b43a5b98… 61924744 d12c4f2a3…`
  wrote a connect and launcher byte-equal to the committed ones.
<!-- absence-ok: describes what the connect script's code does (its write paths, sacct only), not a claim that a result does not exist -->
- **The connect.** Read directly. It writes only `/dev/shm/ibub-connect`, `$N/readout`, `$N/fetch-readout(.tar)` and
  `$N/logs/connect-readout.*`, and nothing to CFS. Job state comes from sacct only, and squeue is never run. The job
  must have exactly one sacct row, named ibub_run, in a terminal state, before anything of it is read. It checks that
  the deploy is unchanged (git status --porcelain --ignored) before anything is published, and copies out by sha256.
- **The reads and checks, as the lane reported them:** two agy gemini-4-hydrogen-xhigh reads, both GO, with every
  MINOR and NOTE fixed (`reads/readout-r1/`, `reads/readout-r2/`); 167 tests OK; 141/141 mutants killed; the trace
  misses only the four `__main__` lines; the Docker stand-in's 16 variants behave as intended. No third read was
  required, because read 2's fix stayed on the flagged lines.
- **CI.** record-checks passed on the reviewed head.

## Rulings

1. **Connect O is bound** at M with the shas above. Any changed byte goes back to the director.
2. **The price: 0 node-h.** One login node and no Slurm job. The readout runs under `nice -n 19` and `taskset`, as
   COV2D's readouts did.
<!-- absence-ok: preconditions checked fresh before the connect (acks, a valid certificate), not claims that a result does not exist -->
3. **Preconditions, all required, before the launcher runs:**
   - fresh acks, after this binding is merged, from cov2d (for partb/out/ER/xsec.root and its fence) and from
     limitation-resolver (for the rpd prefix), each naming connect O and the namespace;
   - a valid NERSC certificate, checked by command, with enough time left for the whole connect. A connect that cannot
     finish before the certificate expires waits. A partial connect is a STOP, not a resume;
   - the director's GO, by message, naming this binding.
4. **One connect.** Any STOP or guard refusal after contact is terminal; nothing is re-run without the director.
5. **The record goes to the director first**: each tune's verdict line and rc, the copy-out shas, and the records tar.
   Nothing goes into the note until the director has reviewed it. The wording is Joseph's.

**CITABLE FOR:** that IBUB's readout was bound, and on what. **NOT CITABLE FOR:** any IBU bias, any verdict, any
comparison with OmniFold, any note wording.
