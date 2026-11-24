# BINDING 2, ADDENDUM 4: d2-predict and step0 (rpd_d2s0), on P0's records (director, 2026-11-24)

**Authority:** Joseph via the director, 2026-11-22 (e1). It extends addendum 3. P0 ran DONE, rc 0, and its records are
merged in #1273 and #1274.

**Binds** the d2s0 package as merged to main in PR #1277, at **M_D2S0 =
`48537ff7a068ec06f8d431285116b4f5ae3b2ba0`**. There, `fd/rpd-reco/d2s0-20261124/` is the tree of the read head
`3620ec487e95ca88b35c6cfde5fbd31378182bb6`, merged with `--match-head-commit`.

| file (under `fd/rpd-reco/d2s0-20261124/`) | sha256 |
|---|---|
| `production-config.ready.json` | `3b2afde495d630cc44df730e3e1acf12e0c332953e9fa298fa979f2e2e39b057` (P0's) |
| `rpd_d2s0_connect.sh` | `8bf94bb0244bf341c2fd883a03e01b22a3fffea32131d41834819012e8e4f783` |
| `rpd_d2s0_fetch.sh` | `55227af2fa4d0a4b526e2224ee6736b8cfdb5aea1c16bcfb698abefcfd79b287` |
| `rpd_d2s0_launch.sh` | `e2bde947866807baf7a5ee92c5ec3842e9c6e96f68abc58e74fc08a92b426e61` |
| `tools/d2s0_checks.py` | `d3ff48f98cd797434c213730b9cf6b8bae6904be2b352f499efa1bb29086a506` |
| `tools/d2s0_expected.json` | `17a13256bac006c87703249989d4504af3144523a4797b95a51ee4a88699b509` |
| `tools/fence_overlap.py` | `33ba39c3ac65e5ca0c6f1c1657fb41a6edbda4af11b94bc3242892774b1c4e21` |
| `tools/p0_supervise.py` | `6ad0f68fb309a7b83adc0f65ed709e5e2412e650e115075fe41ebbc7a070134f` (P0's) |
| `tools/gen_d2s0.py` | `a6899040f97d9fe0a647c1dd65d903276422e75a35effe61b9cbb2804955ad7c` |
| the runner `rpd_d2s0_runner.sh`, written by the connect (its lines 195–335) | `9303b1cfc0a6e5c26ad40abcd8f2ae6f321846b0611a92d93d954d7070f72c44` |

**The code.** The clone is S = `6896e7871421469ce72c6b93188d2d1a55c82ec6` with flux3's 14 pins, as in addendum 3, and
`fd_rpd_reco.py` `7302cc1d`.

## What the director checked

- **The shas.** The director hashed each file above from `git show` at the read head, and each equals the table. The
  runner's sha256 is the director's hash of the connect's heredoc body.
- **The five embedded payloads** were decoded by the director from the connect, and each decodes to its sha256 above:
  the config, `d2s0_checks.py`, `d2s0_expected.json`, `p0_supervise.py` and the fence copy.
- **The delta after the reads.** The director diffed codex-school2's input copy of `d2s0_checks.py` against the read
  head. The only changes are output labels ("P0 INPUTS" → "INPUTS", "P0 STAT" → "STAT"), a narrowed docstring and a
  guarded `unlink`. The connect does not match on those labels. The suites were rerun on the final bytes.
- **No squeue** in the connect. Its iris line is a read-only balance read, recorded in the connect output only, with
  `PIPESTATUS` taken for its rc.
- **Threads 1** are exported in the runner. The connect's checks run at nice 19.
- **Each step's own deadline** is set inside `step()`.
- **The test receipts,** as the README lists them:
  - the sacct fence: 24 checks, 17/17 mutants;
  - the launcher: 23 cases, 13/13;
  - the connect startup: 4 cases, 6/6;
  - the runner: 25 cases, 25/25;
  - the fetch: 20 cases, 12/12;
  - the checks: 9; the supervisor: 17;
  - the overlap fence: CLEAR.
- **The reads.** agy gave GO. codex-school2 gave FIX on one item: d2-predict had been described as the c0 pilot. That
  description is corrected, and its confirmations are listed in the README.

## Rulings

1. **d2s0 is bound** at M_D2S0 with the shas above. Any changed byte goes back to the director.
2. **The price is 0 node-h:** one login node, no job, threads 1, nice 19, O_NOATIME reads, nothing written to CFS.
   - **d2-predict** is planned at 3,895 s at S × 1.5, inside its own 7200 s deadline.
   - **step0** has its own 7200 s deadline. Its cost is unmeasured: decompression and five weighted sorts.
   - A wall-cap STOP is recorded as a measurement. Nothing moves to a compute node without a price to the director.
<!-- absence-ok: preconditions the connect itself checks at run time (a fresh run root, no unended fenced job), not claims that a result does not exist -->
3. **Preconditions at the connect, all required:**
   - the launcher's ack file holds cov2d's ack under an `ACK-UTC` first line no more than 6 h old;
   - tier3-design's ack;
   - the cert check passes;
   - the sacct fence and `fence_overlap.py` read CLEAR;
   - `/pscratch/sd/j/josephrb/rpd-reco-d2s0-20261124` does not exist yet.
4. **The inputs.**
   - P0's in-place inputs and its two run records (`run/pins.json` `52fc41f4`, `run/p0.json` `8ed2faf7`) are checked
     against the committed records before staging.
   - They are copied byte for byte into the new run directory, so `require_predecessors` sees the chain.
   - The `ibuchi_` family stays out of the fence, as in addendum 3, ruling 4.
   - IBUB's write roots are disjoint from d2s0's, and director-helper-3 lists d2s0's roots as protected.
5. **Blinding.** Neither step opens a data row: both pass `data=False`, and no `--prediction` is passed, so
   `require_prediction` would STOP any "measured" read. c0, the first step that reads data, needs d2-predict's record
   committed and merged first.
6. **d2-predict is not the c0 pilot.** It is a 1-axis pass that measures I/O and Poisson draws. c0's price comes from a
   separate MC-only harness at step0's bins, under its own binding.
7. **Any STOP or guard refusal after contact is terminal.** A local refusal before any ssh is reported, and nothing is
   retried without the director's word.
8. **Next:** the fetch until DONE or STOP, a records PR, and then the director's merge.

**CITABLE FOR:** that d2s0 was bound, and on what. **NOT CITABLE FOR:** any RPD-RECO result, any note wording.
