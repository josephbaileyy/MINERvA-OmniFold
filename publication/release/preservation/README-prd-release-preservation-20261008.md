# PRD release-audit preservation directory (2026-10-08)

**Location:** `/global/cfs/cdirs/m3246/josephrb/prd-release-preservation-20261008/` (NERSC CFS, durable project
storage). This README is committed in the source repository at
`publication/release/preservation/README-prd-release-preservation-20261008.md`, and a copy sits in the directory.

**What and why.** The PRD release audit (`ea939701`, gaps G1, G3 and G9) found the RC4 release tarball and the
inputs behind many of the article's supported claims only on purgeable `/pscratch` or in a local temporary directory.
Joseph authorized their preservation here on 2026-10-08, within his 3 TB CFS rule.

**Capacity.** `du -s --block-size=1G /global/cfs/cdirs/m3246/josephrb` measured 1,522 GiB on 2026-10-08 at 15:15 UTC,
before the copy. This directory adds 42.4 GB.

## Contents

| path | what |
|---|---|
| `rc4/minerva-omnifold-article-release-rc4.tar.gz` | The RC4 tarball, unchanged: sha256 `46f801bf05bbd18d1fcfe8c8bf5b0e361cd8e352211de641b434547be1680e88`, 15,696,060 B. It was copied by `scp -p` from the publication session's local scratchpad, and `rc4/RC4-TARBALL.sha256` checks it. |
| `rc5/minerva-omnifold-article-release-rc5.tar.gz` | RC5, the first corrected candidate, now superseded by RC6: sha256 `6784708827e8337c7d3f7774e0fb727c24613ed7eb0db4cadf101fc6413124be`, checked by `rc5/RC5-TARBALL.sha256`. It rebuilds byte for byte from repository commit **`f82e6db76f20119450e7364ec2d9919c23c67db7`**. |
| `rc6/minerva-omnifold-article-release-rc6.tar.gz` | RC6, the reviewed candidate: sha256 `71e2b7a4fc952ecd3494f75d4454f7add7ee01eb08aeb77ade5bc62d45c1461e`, checked by `rc6/RC6-TARBALL.sha256`. Its source commit is recorded in the repository's `docs/publication/corrections-20261008/RECORD-20261008-release-audit-corrections.md` §7. |
| `pscratch/sd/j/josephrb/...` | The supporting products, at their original absolute paths without the leading `/`. The source set is in the `SOURCES` list of `publication/release/preservation/preserve_prd_evidence_20261008.sh`. |
| `SOURCE-INVENTORY.tsv` | One row per preserved file: sha256, bytes, mtime (UTC) and source path, hashed at the source before the copy |
| `SHA256SUMS` | The same digests, in `sha256sum -c` form relative to this directory |
| `SYMLINKS.tsv` | The source symlinks: link, target, resolved path. They are recorded, not copied. Every resolved target is itself preserved here (the inventory step refuses otherwise). |
| `VERIFY-RECEIPT.txt` | The destination verification: command, time and result. Its line 4 reads "copy: copy:"; the repetition is a formatting slip, and the receipt is left unedited. |
| `SOURCE-SUMMARY.tsv`, `preserve_prd_evidence_20261008.sh` | Per-source file counts and bytes; the script that made the inventory, copy and verification (sha256 `36102352…`) |
| `.files.txt`, `.rel.txt` | The script's working lists: absolute source paths, and the same paths relative to `/global/`. Kept as provenance. |

**Source set, by claim** (rows of the audit's claim table):

| source | claims |
|---|---|
| `pub-release-20261006/` | RC4 payload: the sufficient inputs (frozen, union), the figure arrays and the export code clone (all RR rows) |
| `s5c-20260924/runs/{d1,s_valid}` | V16, V17, M03 |
| `s5n-20260925/runs` | V17, V18, M03 |
| `s5e-20260925/runs/cand` | V19, V20, V21 |
| `s5p-20260926/runs/{s2,s3,s3r,s3v}`, `stage3/f2` | VL155; the jitter and lateral re-unfolds; the asimovs behind λ and the M1/F2 shifts; the V pilot ensemble (J03, J06, J09, J11, J13) |
| `w2-recoil-20261006/{manifests,logs}`, `w2b/{design,dump-run,eval,logs,unf}` | R04, R05, A02 |
| `ki84-rebuild-20261006/`, `coverage-2d-20261005/`, `MINERvA-OmniFold/2d-unfolding/uq/*_vl170` | V08, V10–V13 |
| `z2m-floor-20260920{,-k1200}`; `mii/member_k00{0000,1200}/uq_5d/{unified_throw_cov_5d.root,uthrow_slabs_5d_sb}` | U02–U04 |
| `MINERvA-OmniFold/nd-unfolding/products/4d/xsec_4d_MEFHC_5iter_lgbm.root` | C04, V15 |
| `MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz` | the 5D unfolding input |
| `MINERvA-OmniFold/nd-unfolding/uq_5d/z_pilot_20260916_a5/`, `z2m-products/PROJ/` | the adopted trunk `z-cv.npz` (`3d7465f6…`) and its projection (`835828bf…`) (U01, Sec. VII; G9) |

**Added 2026-10-08/09** (Joseph's follow-up authorization; repository record
`docs/publication/corrections-20261008/RECORD-20261008-followups-g11-g12-preservation.md` §3):

| path | what |
|---|---|
| `pscratch/sd/j/josephrb/w2-recoil-20261006/w2b/{evloop,lateral,merged,tables,unfold-run}` | The W2 shifted event-loop, lateral and merged outputs the first pass excluded, plus two small W2 directories it had missed: 53 files, 33,779,505,923 B |
| `W2-SOURCE-INVENTORY.tsv`, `W2-SHA256SUMS`, `W2-SYMLINKS.tsv` (empty), `W2-VERIFY-RECEIPT.txt`, `preserve_w2_outputs_20261008.sh`, `.w2-files.txt`, `.w2-rel.txt` | The same method as the first pass: hashed at the source, copied, every destination file re-hashed (53 of 53 match) |
| `anatuple-checksums-20261008/ANATUPLE-SHA256.tsv` | sha256, bytes and mtime of the analysed older-production AnaTuples on `/pscratch/sd/j/josephrb/minerva/minerva_large_files` (corrections record G4). It identifies the files; it is **not** a copy of them. `DEFERRED.tsv` lists the files a watchdog skipped because their Lustre objects hung; the record §3a names the ones still unhashed. `MISMATCH.tsv` (empty) would list any file whose size or mtime differed from the inventory. |
| `anatuple-checksums-20261008/anatuple_checksum_sweep_20261008.sh`, `hpss_second_copy_20261008.sh`, `verify_tar_stream.py` | The sweep script (resumable: re-running it hashes only the missing files), and the HPSS copy script with its stream verifier (below) |

**HPSS second copies** (G9; `hpss_second_copy_20261008.sh`), verified by streaming each back and re-hashing:
- `/home/j/josephrb/prd-release-preservation-20261008/s5p-archive-20261006.tar` (+ `.idx`): an htar archive of
  `/global/cfs/cdirs/m3246/josephrb/s5p-archive-20261006/`, 10,614 of 10,614 listed members matching;
- `/home/j/josephrb/prd-release-preservation-20261008/z-cv.npz`: sha256 `3d7465f6…` (VL142).

**Not preserved here (excluded, with sizes):**
- `w2-recoil-20261006/{deploy,repo,build,cost1A,smoke}`: code snapshots, held in git, plus test runs.
- The s5p calibration products: already archived at `/global/cfs/cdirs/m3246/josephrb/s5p-archive-20261006/`
  (SHA256SUMS `1a72cb43…`).
- The analysed AnaTuples (11.52 TB): only their checksums are here (above). Copying them needs Joseph's decision;
  see the follow-up record §7.

## Recovery

Read the files in place, or copy them back to their original paths:

```
D=/global/cfs/cdirs/m3246/josephrb/prd-release-preservation-20261008
cd $D && sha256sum --quiet -c SHA256SUMS && echo intact                 # re-verify every file
cd $D && sha256sum --quiet -c W2-SHA256SUMS && echo intact              # the W2 addition
# recover the HPSS second copies (on a login node; DTNs have no hsi):
htar -xvf /home/j/josephrb/prd-release-preservation-20261008/s5p-archive-20261006.tar   # recreates s5p-archive-20261006/ here
hsi get z-cv.npz : /home/j/josephrb/prd-release-preservation-20261008/z-cv.npz && sha256sum z-cv.npz
(cd $D/rc4 && sha256sum -c RC4-TARBALL.sha256)                         # the RC4 tarball, original digest
# restore one tree to /pscratch (run on a DTN; /pscratch is /global/pscratch there):
rsync -a $D/pscratch/sd/j/josephrb/s5n-20260925/ /global/pscratch/sd/j/josephrb/s5n-20260925/
# The CFS copy holds regular files only. The 12 z2m-floor subsets/*/slabs directories consisted only of symlinks, so they
# do not exist here; their targets are preserved under mii/member_k00{0000,1200}/uq_5d/uthrow_slabs_5d_sb/. To use the
# tree in place, recreate the links INSIDE this copy, mapping each target's /pscratch prefix to $D/pscratch:
awk -F'\t' -v D="$D" '{l=$1; r=$3; sub("^/", D "/", l); sub("^/pscratch", D "/pscratch", r); print "mkdir -p \"$(dirname \"" l "\")\" && ln -s \"" r "\" \"" l "\""}' $D/SYMLINKS.tsv   # review, then run
# rebuild RC5 (in a repository checkout at f82e6db7) or RC6 (at its source commit, record section 7) from the preserved RC4:
T=$(mktemp -d) && tar -xzf $D/rc4/minerva-omnifold-article-release-rc4.tar.gz -C $T
python3 publication/release/build_rc.py --payload $T/minerva-omnifold-article-release-rc4 \
    --payload-sums docs/publication/release/RC4-SHA256SUMS.txt --name minerva-omnifold-article-release-rc6 --out $T/out
```

- The RC4 payload paths inside `pub-release-20261006/` are `frozen/inference_sufficient.npz*`,
  `union/inference_sufficient.npz*` and `figs/fig_arrays.npz*`.
- `build_rc.py` expects the RC4 layout: `data/frozen`, `data/recovery-union` and `data/figs`. The simplest payload
  is therefore the extracted RC4 tarball, `tar -xzf rc4/minerva-omnifold-article-release-rc4.tar.gz`.
