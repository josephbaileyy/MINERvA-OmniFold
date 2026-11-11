#!/bin/bash
# LL5D, before the first ll5d_ go (LL5D BINDING 2; the director, 2026-11-08): a realpath overlap check of LL5D's
# declared inputs against the band diagnosis's (FD-1B-BAND-DIAGNOSIS-DECLARATION.md section 6) and FD-PRR's (PR #937,
# FD-PRR-DECLARATION.md section 10.4), so the director can sequence them. Login node, 0 node-h, no job. stat and
# realpath only: no file's contents are read. The two weight directories are listed whole (a superset of what LL5D
# reads). Keys are device:inode of the realpath. Scratch under /dev/shm (umask 077), removed at the end and logged.
P=/pscratch/sd/j/josephrb; ND=$P/MINERvA-OmniFold/nd-unfolding
umask 077
D=$(mktemp -d /dev/shm/josephrb-ll5d-ovl.XXXXXX) || { echo "STOP mktemp"; exit 2; }
echo "overlap host=$(hostname) utc=$(date -u +%FT%TZ) scratch=$D"
ll5d() {
  printf '%s\n' "$ND/of_inputs_5d.npz" "$P/s5c-20260924/runs/p2/bkg_dump.npz" "$P/fd-1b-20261030/pins.json" \
    "$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt" \
    "$P/fd-1b-staged-20261102/stage1/in/flux_universes.npz" "$P/fd-f1-20261027/f1b3/prep/bridged/genie_v3_g18.json" \
    "$P/fd-f1-20261027/f1b3/prep/bridged/genie_v3_ar23.json" "$P/fd-1b-inv-20261101/i0/in/s1/s1_assembly.npz"
  find "$ND/bank_sweep_5d_bkgaware" "$P/s5p-20260926/bank_detector" -maxdepth 1 -type f
}
bd() {
  printf '%s\n' "$ND/of_inputs_5d.npz" "$P/s5c-20260924/runs/p2/bkg_dump.npz"
  find "$P/s5p-20260926/bank_detector" -maxdepth 1 -type f
  find "$P/fd-1b-precheck-fd-20261107/stage" "$P/fd-1b-precheck-fd-20261107/unf" -type f 2>/dev/null
}
prr() {
  printf '%s\n' "$ND/of_inputs_5d.npz" "$P/s5c-20260924/runs/p2/bkg_dump.npz" "$ND/bank_sweep_5d_bkgaware/cv.npz" \
    "$P/pv-ladder-20261024/prep/ratios/L-5D-PV/nuwro.json"
  find "$P/fd-stab-a1r-20261104/runs/control/closure" -type f 2>/dev/null
}
key() { while read -r f; do if [ -e "$f" ]; then r=$(realpath "$f"); echo "$(stat -c '%d:%i' "$r") $r"; else echo "MISSING $f" >&2; fi; done | sort -u; }
ll5d | key > "$D/ll5d" 2> "$D/ll5d.missing"
bd | key > "$D/bd" 2> "$D/bd.missing"
prr | key > "$D/prr" 2> "$D/prr.missing"
for x in ll5d bd prr; do echo "$x files=$(wc -l < "$D/$x") missing=$(wc -l < "$D/$x.missing")"; sed 's/^/  /' "$D/$x.missing"; done
for o in bd prr; do
  join <(cut -d' ' -f1,2 "$D/ll5d") <(cut -d' ' -f1 "$D/$o") > "$D/ll5d_x_$o"
  echo "== LL5D x $o: $(wc -l < "$D/ll5d_x_$o") shared files (realpath)"
  awk '{print $2}' "$D/ll5d_x_$o" | sed 's|/[^/]*$||' | sort | uniq -c
  awk '{print "  " $2}' "$D/ll5d_x_$o" | grep -v -e '/bank_detector/' -e '/bank_sweep_5d_bkgaware/'
done
rm -rf "$D"; echo "rm -rf $D rc=$?"
ls -d /dev/shm/josephrb-ll5d-ovl.* 2>/dev/null || echo "no ll5d-ovl scratch left"
echo "DONE utc=$(date -u +%FT%TZ)"
