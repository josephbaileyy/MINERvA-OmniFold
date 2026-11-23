# BINDING 2, ADDENDUM 2: the flux rerun on the sacct-only custody (rpd_flux3), which P0 reads (director, 2026-11-23)

**Authority:** Joseph via the director, 2026-11-22 (e1). It extends addendum 1.

**Why the rerun is needed:**
- The bound `fd_rpd_reco.py` (`7302cc1d`), at `extracted_flux` (:1994–2013), requires the flux custody receipt's
  `custody_code_sha256` to equal the digest of the custody module beside it. flux2's receipt binds custody `867822e3`.
- PR #1251 replaced that custody with `634670b3`, which reads sacct only and removes the in-job squeue call at the old
  :408 (standing rule: sacct, never squeue).
- P0 at the new code would therefore refuse flux2's records (agy and codex-school2, blocking 1).
- The director ruled (A): rerun the flux stage with the new custody, so that the whole chain from here runs on it.
  Option (B), P0 at `763ab4dd`, and option (C), editing `fd_rpd_reco.py`, were rejected.

**Binds** the flux3 package as merged to main in PR #1255, at **M_F3 =
`710f9e059c7b664a6b3c1d0e2ef99db80207f8dc`**. There, `fd/rpd-reco/flux3-20261123/` is tree-identical to the audited head
`97b4805a91497499a3de9b5d01cab4c116182ae2`.

| file (under `fd/rpd-reco/flux3-20261123/`) | sha256 |
|---|---|
| `production-config.ready.json` | `d797183bb5d459285224e4ee4d3fc8a0cc6cd64b136745ebf182bd716800e229` |
| `rpd_flux3_connect.sh` | `0a50f7db15df9bb31fe574c588a43c7f455609bb5f34e0e5acadd66aa062fbb4` |
| `rpd_flux3_fetch.sh` | `40645b69f02ee67db830fc9f95e3c69bf79cf46a9db4fbada26ce9da7ccf0f2e` |
| `rpd_flux3_launch.sh` | `91ae3a6a35c97040cfc444b4b91b29e63682ae80bd9221f1a2e71e85470459f6` |
| `tools/fence_overlap.py` | `f6541713e2cd4c8b342da5b76f59eec0662555e1cbe97da9ad95a52995594b35` |
| `tools/gen_flux3.py` | `f760c20d8c739ba4cf1a181ef1a970fad48e6c80ba207c8ffc1376f26527eccc` |

**The code.** The connect clones `S = 6896e7871421469ce72c6b93188d2d1a55c82ec6` (main after #1251). The director
hashed all 14 pinned files at S and found each equal to its pin.
- **The only code change from binding 2** is `nd-unfolding/fd_rpd_reco_custody.py`, from `867822e3` to `634670b3`
  (#1251). With it come its tests: `test_fd_rpd_reco.py` `e1b92ef0`, the new `fd_rpd_reco_fence_mutation.py`
  `138bc5b4`, and `fd_rpd_reco_mutation.py` `f2612369` (unchanged).
- `fd_rpd_reco.py` `7302cc1d`, `fd_rpd_inputs.py` `6e4ed0f1` and `fd_rpd_reco_flux_connect.sh` `32db5235` are
  binding 2's.

## What the director checked

- **The config's leaf diff against flux2's `7ebc2aa9`,** from the director's own JSON walk, is exactly two leaves:
  `flux_custody/path` and `flux_extract/path` move to the `rpd-reco-flux3-20261123` root. The digest's P0 form stays
  `75c2a1f4`.
- **No squeue** appears in the connect, the fetch or the launcher. `gen_flux3.py` names it only in refusal assertions.
- **The new custody's two sacct reads ran for real** on Perlmutter (login30, 2026-11-23T05:45:40Z) before this binding,
  and custody's own parser read that output as PASS (#1251, custody-sacct-20261123/probe/).
- **The tests:** the sacct fence (24 cases, 17/17 mutants), the launcher with its ack-file guard (23 cases, 13/13), the
  fetch's finish check (11, 5/5), and the flux2-identity check (4, 3/3). The overlap fence is CLEAR over 57 originals.
- **The reads:**
  - agy: GO on the package and on two confirms.
  - codex-school2: FIX, with every blocking item fixed; confirm 3 (`dfb4a065…`) GO.
  - Two non-blocking notes from confirm 3 were taken after it: a refusal message and a test-stub key. Every suite was
    rerun, so no fourth read is needed.

## Rulings

1. **The rerun is bound** at M_F3 with the shas above. Any changed byte goes back to the director.
<!-- absence-ok: preconditions the connect itself checks at run time (fence mode not invoked; a fresh run root), not claims that a result does not exist -->
2. **Preconditions at the connect, all required:**
   - The launcher's ack file holds cov2d's ack verbatim, under an `ACK-UTC` first line no more than 6 h old.
   - tier3-design's ack.
   - The cert check passes. The cert is valid to 2026-11-24T05:57:28Z.
   - The connect's sacct fence and `fence_overlap.py` read CLEAR, and the launcher's fence mode is not run.
   - `/pscratch/sd/j/josephrb/rpd-reco-flux3-20261123` does not exist yet.
3. **The job** runs on shared QOS, with `--time=01:00:00` and job name `rpd_flux3`, which is in the rpd* family every
   fence watches. scontrol must match, or the job is scancelled and the run STOPs. The charge is recorded from sacct.
4. **The product.**
   - The extract's selection digest must equal the P0 form `75c2a1f4…`.
   - Its custody receipt must bind custody `634670b3`.
   - **All 12 factor products must be byte-identical to flux2's** (the fetch's FLUX2 IDENTITY, exit 15 otherwise).
     Any difference is a STOP to the director, not a reading.
5. **Any STOP or guard refusal after contact is terminal.** A local refusal before any ssh is reported, and nothing is
   retried without the director's word.
6. **Next:** the records PR, then the director's merge. Then P0 is rebuilt on flux3's records with findings 1–9 and gets
   its own binding.

**CITABLE FOR:** that the rerun was bound, and on what. **NOT CITABLE FOR:** any RPD-RECO result, any note wording.
