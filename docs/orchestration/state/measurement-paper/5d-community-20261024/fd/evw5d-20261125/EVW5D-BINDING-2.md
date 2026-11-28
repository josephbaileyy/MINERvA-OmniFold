# EVW5D BINDING 2: attempt 2 (namespace evw5d-20261125-r2), steps 1–3 (connect, post, fetch), one CPU node, cap 0.5 node-h (director, 2026-11-25)

**Follows** EVW5D BINDING 1 (`EVW5D-BINDING-1.md`, #1342). Attempt 1's one bound connect ended with STOP, rc 6. The
connect compared scontrol's `NumNodes` with the string `1`, but a pending job prints it as `1-1`. Job 61997953 was
cancelled before it started: sacct shows CANCELLED, ElapsedRaw 0, Start None, so 0 node-h was charged. The allocation
itself was correct (one node, 30:00, no array). The record is in `fd/evw5d-20261125/receipts/attempt1/`. Attempt 1's
namespace `/pscratch/sd/j/josephrb/evw5d-20261125` (deploy/, toolclone/, logs/) is left as it is. Removing it is
Joseph's call.

**Authority:** as for binding 1. The declaration is unchanged: revision 5, sha256 `b7646dacc43b3978354b3233e357149d7ce8d802b702829188f6a87a63804923`.

**Binds** the change as merged to main in PR #1343 (merge `fb83c789cf2c893ce6975db6c1fe04b78f23ccf1`), at the reviewed head
`8174725735385c33be1cd288bcdd5b2838769f48`, merged with `--match-head-commit`. The tool commit is unchanged, **`e01dd863787b6ed0b6ccf836ea0a9b60ed6ac3c3`**. `evw5d.py`,
`sbatch_evw5d.sh` and `ess_capture.py` are byte-equal to it. The namespace is
**`/pscratch/sd/j/josephrb/evw5d-20261125-r2`**, and the HPSS path is
`/home/j/josephrb/mnv-evw5d-20261125-r2/evw5d-20261125-r2.tar`.

| file | sha256 |
|---|---|
| `nd-unfolding/evw5d/evw5d.py` | `f6f5bbb5ea1c0c7a704dfcd64e1f214c587db1e64db3d9c9ae4e943ac01ad990` |
| `nd-unfolding/evw5d/sbatch_evw5d.sh` | `60fd4ec26714b2ccb956bd5abec4ba07092eca4c2f80b9ee1ab85bb02fd3533a` |
| `fd/evw5d-20261125/launch/bound/evw5d_launch.sh` | `a7b81113c540bdd0ce425b72277e33a9641cf586131dd9328affd5262d5a2280` |
| `fd/evw5d-20261125/launch/bound/evw5d_connect.sh` | `e81567e0b815de8b1ae0c274f84672540ad191faa13422ac075882722f103a96` |
| `fd/evw5d-20261125/launch/bound/evw5d_post.sh` | `292c4cb99d0bc4b20dd70a12734ca308cf5c8b171779364ac8deecad8e784164` |
| `fd/evw5d-20261125/launch/bound/evw5d_hpss.sh` | `d37a0396de720d35d4c89aff51fd207cd1aba7dea1542f148026c1173235ff08` |
| `fd/evw5d-20261125/launch/bound/PINS.txt` | `a40c70a329b2aa002eea1c6e1c4b2460ee9963c4877eb1372ae0343e5bdcdd79` |
| `nd-unfolding/evw5d/test_evw5d.py` | `387bca3fba103dbdaceaf2241b0f4d165e95ddbe14c48035b8493cdffe3d79ee` |
| `fd/evw5d-20261125/receipts/attempt1/README.md` | `3749b7813ef68b538b83dcdfcad4caf65814f8e4a6c3a3471f2e6a6f320abe82` |
| `ess_capture.py` (at the tool commit) | `4755681f6ba8bd5060fe6ed4902e940b71e3b641d87c978a1f8016faaec468da` |

The `fd/` paths are under `docs/orchestration/state/measurement-paper/5d-community-20261024/`. The binding 1 shas of the
four launch scripts are superseded. Those of `evw5d.py`, `sbatch_evw5d.sh` and `ess_capture.py` stand.

## What the director checked

- **The diff** `aada31f2..` the reviewed head, under `fd/evw5d-20261125/launch/` (templates and bound copies). It
  holds only these changes:
  - the namespace lines (OUT in connect, post and the launcher; R and H/TAR in hpss);
  - in the connect, the one allocation-check line, now `! printf '%s' "$nn" | grep -Eq '^1(-1)?$'` in place of
    `[ "$nn" != 1 ]`;
  - in the bound launcher and PINS.txt, the new script digests.

  No bound script names the old namespace except the connect's comment on attempt 1. `evw5d_post.sh` is byte-equal to
  its template. Each scripted pin equals PINS.txt, hashed from `git show` at main after the merge.
- **The tool.** `git diff --stat e01dd863` on `evw5d.py`, `sbatch_evw5d.sh` and `ess_capture.py` is empty at the head.
- **The test and mutant, as the lane reported them.** `test_connect_allocation_check[template|bound]` runs the check as
  written against real-format scontrol text, with stubbed scontrol, scancel, sacct and sleep.
  - `1-1` and `1` are accepted.
  - `2-2`, `1-2`, `2` and `11`, a 01:00:00 limit, and an ArrayJobId line are each cancelled with rc 6.
  - The mutant restoring `= 1` is killed in both cases (`receipts/mutation-r2-connect.json.txt`).
  - The full suite passes, 122 tests (`receipts/tests.txt`).
- **The field audit, as the lane reported it.** Every other scheduler field the scripts compare was checked against
  its pending or running form. Each check is either a presence test, an exact job-name match, the allocation line's
  JobID as a string, or a form already seen in attempt 1 or in ESS's running job 61082774. None needed a fix.
- **CI.** record-checks passed on the reviewed head.

## Rulings

1. **Attempt 2's steps 1–3 are bound**: `evw5d_launch.sh connect`, then `post` once sacct shows the job terminal,
   then `fetch`. All of them run from `launch/bound/` at or after this binding's merge. Any changed byte goes back to
   the director.
2. **The price and the preconditions are binding 1's rulings 2 and 3**, unchanged. That means about 0.28 node-h with
   a cap of 0.5. It also means a valid certificate checked by command, with no use past expiry. Finally, the
   director's GO must name this binding, and no other bound job may read the three inputs plainly in the window.
3. **One connect.** Any STOP, FAILED or refusal after contact is terminal, and nothing is rerun without the director.
4. **Steps 4–5 (hpss, fetch-products) are not yet bound.** The lane sends binding 1 ruling 5's readout. The director
   then binds the `SHA256SUMS` digest in EVW5D BINDING 3 before the HPSS copy runs.
5. **Hosting and wording are Joseph's**, as in binding 1.

**CITABLE FOR:** that EVW5D's attempt 2 steps 1–3 were bound, and on what, and that attempt 1 ended at a false STOP
with no charge. **NOT CITABLE FOR:** any weight, completeness, cross section or uncertainty, or any note wording.
