#!/bin/bash
# Unit cases for tools/fence_overlap.py: the READY config, then variants of its cov2d_protected_paths (the variants are
# test copies; the connect checks the real config's sha256 before the fence runs). The clone is #848's tree at a4c3e556.
SP=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/7e3f49f7-e8e4-452d-b380-399d4f6c529e/scratchpad
D=$SP/wtrc/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/flux1-20261111
T=$SP/flux1/tf; mkdir -p "$T" || exit 9
CLONE=$SP/clone848
EXC=/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt
variant() {  # name, python expression editing list p
  python3 -I -c "import json,sys; c=json.load(open(sys.argv[1])); p=c['cov2d_protected_paths']; $2; c['cov2d_protected_paths']=p; json.dump(c, open(sys.argv[2],'w'))" \
    "$D/production-config.ready.json" "$T/$1.json"
  python3 -I "$D/tools/fence_overlap.py" "$T/$1.json" "$CLONE" > "$T/$1.out" 2>&1
  echo "CASE $1 rc=$? $(grep -E '^FENCE OVERLAP' "$T/$1.out")"; grep -E '^FENCE (STOP|allowed)' "$T/$1.out" | head -3 | sed 's/^/   /'
}
variant ready "pass"
variant dump_root_protected "p.append('/pscratch/sd/j/josephrb/fd-rpd-20261103/dumps')"
variant write_root_inside_protected "p.append('/pscratch/sd/j/josephrb')"
variant exception_directory_protected "p.append('/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data')"
variant clone_protected "p.append('/dev/shm/limres-rpd-flux1/repo/nd-unfolding')"
variant cn_file_protected "p.append('/pscratch/sd/j/josephrb/minerva/minerva_large_files/MATFluxAndReweightFiles/flux/flux-gen2thin-pdg14-minervame1M_rearrangedUniverses.root')"
variant exception_not_listed "p.remove('$EXC')"
