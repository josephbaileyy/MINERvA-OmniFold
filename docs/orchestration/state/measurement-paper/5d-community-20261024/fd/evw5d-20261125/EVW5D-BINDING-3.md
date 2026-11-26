# EVW5D BINDING 3: the HPSS copy and the deposit fetch (steps 4–5), bound to SHA256SUMS 31075af6 (director, 2026-11-26)

**Follows** EVW5D BINDING 2 (`EVW5D-BINDING-2.md`, #1344). Attempt 2's job 62000819 ran under binding 2 and ended
COMPLETED 0:0 in 776 s, charged 0.2156 node-h. The receipts are merged in PR #1353 (merge `afc09214adc4ec1c4fad42aef160761720d6a6eb`, at the reviewed
head `3132b7ac294b8c56d971ae13231881683164a02b`), under `fd/evw5d-20261125/receipts/attempt2/`. Attempt 1's namespace was removed under
`DECISION-20261125c` (`receipts/attempt1/removal.txt`).

**Authority:** as for bindings 1 and 2. Joseph decided that every weight file goes on Zenodo in the same release
(`DECISION-20261125c` §1). The deposit itself is Joseph's, after Ben approves. No lane uploads anything.

**Binds** the HPSS step and the fetch-products step of the launcher bound in binding 2 (`launch/bound/`, launcher
`a7b81113…`, hpss `d37a0396…`), with the products' manifest digest:

**SHA256SUMS sha256 = `31075af667c6cda13d76b0e09831a5e40180069615853a30ae34a325b8be8718`**

The director hashed the committed copy `receipts/attempt2/post/evw5d/SHA256SUMS` by command, and it gives this digest.
The same digest appears in the post's log and in `evw5d.done`, and the lane recomputed it on the Mac from the fetched
file.

| product | sha256 (from the committed SHA256SUMS) |
|---|---|
| `constants.json` | `8f009d828163161418e94997428c80a8c723fa3a015fcb63165861aa3312c3aa` |
| `constants.npz` | `d2aac0664f8677b29414a0be9cfdf570af54f3df80a851297ccef21ebdf98e01` |
| `product/data_b-_j-.npz` | `83436d151d45a2ba01947a7d780a649fd250e1adec60e9003bf78ac351bb951a` |
| `run.json` | `c2ec93fb529769b5b8cdb56966ac115a4e02da90880e83b8fd23513de9b500f6` |
| `weights.npz` | `0fceefcdcfcd5c48070453707b55f40e55787909f98481dadcdc82dd0897aba6` |

## What the director checked

- **The run, as recorded in the merged receipts:**
  - VERIFY=PASS and post rc 0, with the product set exact;
  - `evw5d.done` verdict PASS, controls_verdict PASS, failed_controls `[]`;
  - acceptance passes;
  - C-BIND: `xsec_flat` byte-equal to fb5cc679's, with meta equal except the per-run fields;
  - C-F: 3.3e-16 from the result and 3.8e-15 from the rows;
  - every other gated control passes;
  - the three inputs' size, inode, mtime and atime unchanged.
- **C-COMPLETE**, a finding, not a failure. 32 of the 65,856 fine cells (16 adjacent pairs) depart from 1 by at most
  4.1e-4. The pairs are equal and opposite, consistent with 16 events binned across an edge by the float32 cast of the
  truth inputs. Setting c = 1 moves the sixteen f by at most 3.3e-6. The weights and the published f are unchanged.
  How the release describes this is Joseph's call (option (a) or (b), put to him on 2026-11-26).

## Rulings

1. **Steps 4 and 5 are bound**, with the digest above:
   - `evw5d_launch.sh hpss <new dir> <loginNN> 31075af6…`;
   - then, only after hpss exits 0, `evw5d_launch.sh fetch-products <new dir> 31075af6…`.
   Both run from `launch/bound/` at or after this binding's merge. Any changed byte goes back to the director.
2. **The HPSS path** is `/home/j/josephrb/mnv-evw5d-20261125-r2/evw5d-20261125-r2.tar`, a new archive. The step
   refuses if it exists. It verifies by htar CRC, hashcreate and hashverify, retrieves the whole archive, and runs
   `accepted()` on the retrieved copy. Nothing is written to CFS.
3. **The deposit copy** goes into a new directory under `$HOME`, outside `/private/tmp`. `accepted()` must pass there
   on the Mac with the bound digest. The lane reports the path and the five shas, recomputed there. The Mac has about
   29 GiB free for the 1.74 GB.
<!-- absence-ok: preconditions checked fresh before each step (a valid certificate, the director's GO), not claims that a result does not exist -->
4. **Preconditions:** a valid NERSC certificate checked by command before each step, with no use past expiry, and
   the director's GO naming this binding.
5. **One run of each step.** Any STOP or refusal is terminal, and nothing is rerun without the director. The scratch
   products stay where they are. Removing them is Joseph's call.

**CITABLE FOR:** that EVW5D's HPSS copy and deposit fetch were bound, and to which digest. **NOT CITABLE FOR:** any
weight, completeness, cross section or uncertainty, the deposit, or any note wording.
