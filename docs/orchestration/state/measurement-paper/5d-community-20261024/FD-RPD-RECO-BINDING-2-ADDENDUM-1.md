# BINDING 2, ADDENDUM 1: the config-only flux rerun (rpd_flux2) that unblocks P0 (director, 2026-11-22)

**Authority:** Joseph via the director, 2026-11-22 ("i authorizeit", in reply to "Do you want me to start f1, e1 and
b1?"). e1 is RPD-RECO P0 → d1 → d2, then RPL (i)'s α fit. The director's ruling on the P0 blocker, option (c), is a
config-only rerun of flux connect 1 with the code that binding 2 bound.

**Binds** the rerun as merged to main in PR #1245, at **M_F2 = `62ce018fdf32b5f6b7354ec2e617222ee470f955`**.
`fd/rpd-reco/flux2-20261122/` there is tree-identical to the audited head `9b2ff2e36620fa687d8b637f5b4ae08f716c6f0f`.

| file (under `fd/rpd-reco/flux2-20261122/`) | sha256 |
|---|---|
| `production-config.ready.json` | `7ebc2aa9e254ec99535fab2416617e069f3a97621fa69c1c44b24b31a38c4fa9` |
| `rpd_flux2_connect.sh` | `7a362f34dd00b2422c91ff542366d9cc120c8dedbde730da5592b171bac73fd2` |
| `rpd_flux2_fetch.sh` | `d8f780c917b873a888ce2dd55d8f16f813018a5d4fd87211f24e5d23dea750fc` |
| `rpd_flux2_launch.sh` (pins the connect and the fetch) | `c744061e6a1cbd589a032e91e81d3178b066faa336097a935e4f294486408487` |
| `tools/fence_overlap.py` | `68e4033c8d4cbabe01ea6fdd1645f4ddfb42098a52a5d38c653f708cd80d1553` |
| `tools/gen_flux2.py` | `6344f152e920df64f9a1ba09550c78f3e7b416445ec391b916914eb68782cb56` |
| `tests/test_sacct_fence.sh` (19 checks, 13/13 mutants) | `209736947bd0ab8f1fcd571be3947b509392f46e64c77463ba7c7a79d6baf22e` |
| `tests/test_launch.sh` (7 cases, 2/2 mutants) | `b3abea5bc33fec682fe553fde3cf5bbe82af45e5122b43ca7cafd64c5005e055` |

**The code is binding 2's, unchanged.** The connect clones `S = 763ab4ddcea2d2d3dce56138f8aa7ae7fab4bbe6` (binding 2's
audited head) and refuses unless its pinned files hash to binding 2's values, for example `fd_rpd_reco.py`
`7302cc1d…`, `fd_rpd_reco_custody.py` `867822e3…`, `fd_rpd_inputs.py` `6e4ed0f1…` and
`fd_rpd_reco_flux_connect.sh` `32db5235…`. These four are also byte-identical at M_F2. The config travels inside the
connect as a base64 blob, and the connect checks it against `CFG_SHA`.

## What the director checked

- **S1's survey** (login-only, 2026-11-22T22:01:53Z, login23). The six output shas equal the committed `s1/` copies;
  the remote script is `1a9e244a…` and the launcher `24dddd72…`, as approved. The director read the content directly:
  51 lines, empty stderr. The iris balance was 725.6 node-h.
- **The config's leaf diff against flux1's `cde8d029`**, from the director's own JSON walk. It is exactly the allowed
  set:
  - the two premise booleans, None → True;
  - `flux_custody/path` and `flux_extract/path` moved to the `rpd-reco-flux2-20261122` root;
  - `cov2d_protected_paths/30..35`, the six roots cov2d named;
  - `flux_selection/{1D,1M,1N}/retention`.
- **The retention strings.** Each string's bytes, inode, atime and mtime equal survey.log lines 45, 47 and 49 (the epochs
  converted to UTC), and its purge exposure is atime + 56 d (2027-01-11). No value is typed.
- **The script diffs against flux1** (roots normalized). They show only:
  - CFG_SHA and the config blob;
  - FENCE_SHA;
  - the time strings (×3, 03:00:00 → 01:00:00);
  - the sacct fence in place of squeue;
  - the launcher's pinned shas.

  The scripts contain no squeue.
- **The sacct fence.** It is fail-closed on cov2d rev 2's pattern: stdout and stderr are captured, every non-empty line
  must be a 3-field row with a numeric JobID, State is classified by its first word against the closed terminal set,
  and the window is 14 days.
- **The reads, both taken as fixes.**
  - Grok (FIX `664102c4…`): the launcher's fence mode pinned cov2d_fence rev 1, which calls squeue. It now refuses.
  - agy (FIX `6e2482ef…`): the launcher's ssh rc was the trailing echo's. It now returns the remote script's rc and
    refuses a cert that ends within 30 min.
  - The agy delta confirm `ebac19a0…` is GO.
- **The ssh-rc sweep** (`91318ee4…`) shows AFFECTED 0. No committed verdict rests on a masked ssh rc alone. Five other
  committed launchers keep the echo tail: `vhr_wtruth_launch`, `ess_launch`, `rpd_mnv_check2_launch`, `t2a_launch` and
  `t2a_status_launch`. Any future run of one of them is read from its `script rc=` line.
- **The price.** At flux1's sacct AllocCPUS of 10 out of 256 and the 1 h limit, it is 0.039 node-h. flux1 took 253 s.
  The worst case, if shared QOS were charged a whole node, is 1 node-h.

## Rulings

1. **The rerun is bound** at M_F2 with the shas above. Any changed byte goes back to the director before it runs.
<!-- absence-ok: preconditions the connect itself checks at run time (fence mode not invoked; a fresh run root), not claims that a result does not exist -->
2. **Preconditions at the connect, all required:**
   - cov2d's ack is fresh, taken under 6 h before the connect. The 22:05:53Z ack is too old by then, so it is re-taken.
   - The launcher's cert check passes.
   - The connect's own sacct fence and `fence_overlap.py` read CLEAR. The launcher's fence mode is not run.
   - `/pscratch/sd/j/josephrb/rpd-reco-flux2-20261122` does not exist yet.
3. **The job** runs on shared QOS, with `--time=01:00:00` and job name `rpd_flux2`. scontrol must show TimeLimit
   01:00:00, QOS shared and Account m3246, or the connect scancels it and STOPs. The charge is recorded from sacct after
   the job ends.
4. **The product.** The extract's `flux_selection_digest` must equal the rerun's "P0 form",
   `75c2a1f4435494bf0e2c5bf4d27631781e65bd738c889c667183778e254792e8`, and must differ from flux1's `1c716c12…`.
   `common_units_convention_measured_at_P0` stays null.
5. **Any STOP or guard refusal is terminal** for this connect. It goes to the director with its log, and there is no
   repair round.
6. **Next after the job and its fetch:**
   - the run's records go into a PR, with record-checks passing at its head;
   - the director merges it;
   - P0 READY is bound separately, on the same clone path `/dev/shm/limres-rpd-flux1/repo`, re-cloned.

   Nothing from P0 onward is bound here.

**CITABLE FOR:** that the rerun was bound, and on what. **NOT CITABLE FOR:** any RPD-RECO result, any note wording.
