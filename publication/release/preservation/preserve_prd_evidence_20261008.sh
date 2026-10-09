#!/usr/bin/env bash
# Preserve the PRD release-audit evidence (audit ea939701, gaps G1/G3/G9) from purgeable /pscratch to a new
# durable CFS directory. Run on a NERSC data-transfer node (dtn01.nersc.gov), which mounts both file systems.
#
#   bash preserve_prd_evidence_20261008.sh inventory   # hash every source file -> $DEST/SOURCE-INVENTORY.tsv
#   bash preserve_prd_evidence_20261008.sh copy        # rsync -a the inventoried files (sources are only read)
#   bash preserve_prd_evidence_20261008.sh verify      # re-hash every destination file against the inventory
#
# The RC4 tarball is copied separately from the publication session's local scratchpad with scp (see README.md).
# Nothing is moved or deleted; the sources stay where they are. Symlinks are recorded in SYMLINKS.tsv (link, target,
# resolved path), not copied; the inventory refuses unless every resolved target is itself preserved.
set -euo pipefail

P=/pscratch/sd/j/josephrb
M=$P/MINERvA-OmniFold
DEST=/global/cfs/cdirs/m3246/josephrb/prd-release-preservation-20261008

# The exact source set. Directories are taken whole; files singly. W2 keeps only its evidence subtrees: the
# 32 GB of shifted event-loop and lateral outputs (w2b/evloop, w2b/lateral, w2b/merged) are excluded and listed
# in README.md as a separate option.
SOURCES=(
  "$P/pub-release-20261006"
  "$P/s5c-20260924/runs/d1"
  "$P/s5c-20260924/runs/s_valid"
  "$P/s5n-20260925/runs"
  "$P/s5e-20260925/runs/cand"
  "$P/s5p-20260926/runs/s2"
  "$P/s5p-20260926/runs/s3"
  "$P/s5p-20260926/runs/s3r"
  "$P/s5p-20260926/runs/s3v"
  "$P/s5p-20260926/stage3/f2"
  "$P/w2-recoil-20261006/manifests"
  "$P/w2-recoil-20261006/logs"
  "$P/w2-recoil-20261006/w2b/design"
  "$P/w2-recoil-20261006/w2b/dump-run"
  "$P/w2-recoil-20261006/w2b/eval"
  "$P/w2-recoil-20261006/w2b/logs"
  "$P/w2-recoil-20261006/w2b/unf"
  "$P/ki84-rebuild-20261006"
  "$P/coverage-2d-20261005"
  "$M/2d-unfolding/uq/bootstrap_MEFHC_300_vl170"
  "$M/2d-unfolding/uq/universe_stage2_MEFHC_full_matcorr_fluxfix_vl170"
  "$P/z2m-floor-20260920"
  "$P/z2m-floor-20260920-k1200"
  "$M/nd-unfolding/mii/member_k000000/uq_5d/unified_throw_cov_5d.root"
  "$M/nd-unfolding/mii/member_k000000/uq_5d/uthrow_slabs_5d_sb"   # targets of the floor ensembles' slab links
  "$M/nd-unfolding/mii/member_k001200/uq_5d/unified_throw_cov_5d.root"
  "$M/nd-unfolding/mii/member_k001200/uq_5d/uthrow_slabs_5d_sb"
  "$M/nd-unfolding/products/4d/xsec_4d_MEFHC_5iter_lgbm.root"
  "$M/nd-unfolding/of_inputs_5d.npz"
  "$M/nd-unfolding/uq_5d/z_pilot_20260916_a5"
  "$P/z2m-products/PROJ"
)

list_files() {  # absolute paths of every regular file in the source set, sorted
  local s
  for s in "${SOURCES[@]}"; do
    [ -e "$s" ] || { echo "MISSING SOURCE $s" >&2; exit 3; }
    find "$s" -type f
  done | LC_ALL=C sort
}

list_links() {  # every symlink: link<TAB>target<TAB>resolved. Links are recorded, not copied; each resolved target
  local s l t r    # must itself be a preserved regular file or directory, else the inventory refuses.
  for s in "${SOURCES[@]}"; do
    find "$s" -type l | LC_ALL=C sort | while IFS= read -r l; do
      t=$(readlink "$l"); r=$(readlink -f "$l"); r=${r/#\/global\/pscratch//pscratch}  # DTN mounts /pscratch via /global
      printf '%s\t%s\t%s\n' "$l" "$t" "$r"
    done
  done
}

case "${1:-}" in
  inventory)
    mkdir -p "$DEST"
    [ ! -e "$DEST/SOURCE-INVENTORY.tsv" ] || { echo "inventory exists; refusing to overwrite" >&2; exit 5; }
    list_files > "$DEST/.files.txt"
    list_links > "$DEST/SYMLINKS.tsv"
    while IFS=$'\t' read -r l t r; do
      if [ -f "$r" ]; then grep -qxF "$r" "$DEST/.files.txt" || { echo "link target not preserved: $l -> $r" >&2; exit 4; }
      elif [ -d "$r" ]; then grep -qF "$r/" "$DEST/.files.txt" || { echo "link target dir not preserved: $l -> $r" >&2; exit 4; }
      else echo "dangling link: $l -> $t" >&2; exit 4; fi
    done < "$DEST/SYMLINKS.tsv"
    printf 'sha256\tbytes\tmtime_utc\tsource_path\n' > "$DEST/SOURCE-INVENTORY.tsv.part"
    while IFS= read -r f; do
      printf '%s\t%s\t%s\t%s\n' "$(sha256sum "$f" | cut -d' ' -f1)" "$(stat -c %s "$f")" \
        "$(date -u -d @"$(stat -c %Y "$f")" +%Y-%m-%dT%H:%M:%SZ)" "$f"
    done < "$DEST/.files.txt" >> "$DEST/SOURCE-INVENTORY.tsv.part"
    mv "$DEST/SOURCE-INVENTORY.tsv.part" "$DEST/SOURCE-INVENTORY.tsv"
    echo "inventory: $(($(wc -l < "$DEST/SOURCE-INVENTORY.tsv") - 1)) files, $(awk -F'\t' 'NR>1{s+=$2} END{print s}' "$DEST/SOURCE-INVENTORY.tsv") bytes"
    ;;
  copy)
    # Every file lands at DEST/<absolute source path without the leading slash>. On the DTN /pscratch is a symlink to
    # /global/pscratch and rsync's sender refuses a symlinked path component ("Too many levels of symbolic links"),
    # so the transfer root is /global/ and the listed paths start at pscratch/.
    tail -n +2 "$DEST/SOURCE-INVENTORY.tsv" | cut -f4 | sed 's#^/##' > "$DEST/.rel.txt"
    rsync -a --files-from="$DEST/.rel.txt" /global/ "$DEST/"
    echo "copy: rsync rc 0"
    ;;
  verify)
    tail -n +2 "$DEST/SOURCE-INVENTORY.tsv" | awk -F'\t' '{sub("^/","",$4); print $1"  "$4}' > "$DEST/SHA256SUMS"
    ( cd "$DEST" && sha256sum --quiet -c SHA256SUMS ) && echo "verify: all $(wc -l < "$DEST/SHA256SUMS") destination files match the source inventory"
    ;;
  *) echo "usage: $0 inventory|copy|verify" >&2; exit 2 ;;
esac
