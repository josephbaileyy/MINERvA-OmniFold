# Receipt: PET studies preserved on CFS (2026-10-06)

**CITABLE FOR:** where the raw PET run directories are preserved, how the copy was verified, and that nothing on
scratch was removed.
**NOT CITABLE FOR:** any scientific result.

**Authority:** Joseph, 2026-10-06: "yes you can put them in CFS". This answers the recommendation to preserve the PET
study runs on CFS instead of HPSS (handoff §13 of `../../HANDOFF-COLDSTART-20260929.md`). Joseph's CFS rule is
"as long as I am under 3 TB it is fine".

## What was copied

- **Destination:** `/global/cfs/cdirs/m3246/josephrb/pet-studies-20261006/`. Each item keeps its scratch name.
- **Source:** `/pscratch/sd/j/josephrb/`.
- **Items:** 249 (`items.txt`):
  - the three studies: `pet-final-design-20260925` (326 G), `pet-improvement-20260922` (37 G) and
    `pet-direct-token-runtime-20260911` (4.9 G);
  - `campaign-20260920` (5.5 G), the historical configuration comparison's run directory, which one improvement-study
    symlink points into;
  - 245 smaller PET execution directories, bundles and scripts from 2026-08-26 to 2026-09-21 (about 18 G). These are
    every top-level `*pet*` / `*PET*` name on scratch, plus `MINERvA-OmniFold-gbdt-20260922` and
    `theirs_token_schema.py`.
- **Size:** 394 G in total. Joseph's CFS directory went from 1.1 T to about 1.5 T, within the 3 TB rule.

## How it was verified

- **Job:** Slurm job **59411014**, qos `xfer`, account `m3246`, on login06. It ran 2026-10-06 05:21:49Z to
  07:59:31Z (02:42:24) and ended `COMPLETED 0:0`.
- **Script:** `pet_cfs_preserve.sh` (sha256 `544782dc…5387`).
- **Method:** for each item, the script did three things:
  1. took a sha256 manifest of every regular file, and a list of every symlink with its target, from the
     **source**, before copying;
  2. ran `rsync -a`, which copies symlinks as links and dereferences nothing;
  3. took the same manifest and link list from the **copy**.

  An item was marked verified only if rsync exited 0 and both lists were byte-identical to the source's.
- **Result:** `RESULT COPY_VERIFY_COMPLETE_PASS`, 249/249 verified, 0 mismatches (`preserve_59411014.out`). The
  file counts match the pre-copy survey: 338,284 / 131,248 / 35,277 files.
- **Self-test before submission,** on a scratch fixture, in both directions:
  - clean items verified, with the symlink preserved as a link;
  - a copy corrupted with the same size and mtime (which rsync's quick check skips) was refused as `MISMATCH`.
- **Manifests:** the per-file manifests are kept beside the copy, in `_preserve/manifests/`. Their digests for the
  four large items are in `manifest_digests.tsv`.

## Notes

- **Nothing was removed from scratch.** Removing scratch copies is a separate decision.
- **The copy is not a second archive tier.** No HPSS copy was made. HPSS had about 164 GiB free of 512 on
  2026-10-05.
- **One absolute symlink**, `pet-improvement-20260922/phaseB2/scorer-check/hist-ours-127/weights_ours_final_127.npz`,
  still points to its scratch path under `campaign-20260920`. Its target is preserved at the same relative place in
  the CFS copy. `pet-direct-token-runtime-20260911/bin/python` points to a conda environment in `$HOME`.
- **A MISMATCH is not repaired by re-running the script.** rsync's quick check would skip a same-size, same-mtime
  file. Repair such an item with `rsync -c` and re-verify. No MISMATCH occurred.
