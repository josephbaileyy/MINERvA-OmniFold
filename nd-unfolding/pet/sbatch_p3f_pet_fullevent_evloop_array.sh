#!/bin/bash
#SBATCH --job-name=p3fpet_fe
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=12:00:00
#SBATCH --array=0-119%16
#SBATCH --output=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/p3f_pet_fullevent/logs/p3fpet_fe_%a_%A.out
#SBATCH --error=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/p3f_pet_fullevent/logs/p3fpet_fe_%a_%A.err
#
# GATE-3 P3F-PET fresh full-event active-universe point-cloud production array.
# 120 tasks = 5 bands x 2 endpoints x 12 playlists, band-major (task = band*24 + endpoint*12 + pl).
# ONE band/endpoint/playlist per task. Generates FRESH full-event ROOTs from the canonical raw
# Data/MC manifests; existing scalar/purity/reduced-schema ROOTs are CONTROLS ONLY and are never read
# or written here. Fail-closed. NOT auto-submitted; the orchestrator submits after binding the P3F
# validator SHA and supplying the launcher SHA. No hadd/merge/NPZ, and NO PET training.
#
# RECOVERY / PUBLICATION CONTRACT (identical hardened mechanics to the committed G2 launcher
# nd-unfolding/pet/sbatch_g2_fullevent_evloop_array.sh, which this MIRRORS without modifying):
#  * Publication state classified by EXISTENCE (dangling symlink counts occupied), not size. Neither
#    final ROOT nor receipt -> RUN. Both -> full resume rehash, skip only on exact match. Any one-sided
#    / zero-length / malformed / mismatched pair -> DIE before env/compute, NEVER mutated.
#  * All 24 canonical manifest SHA-256, the binary SHA + built-source commit, the base-G2 validator
#    SHA, the NEW P3F validator SHA, and the launcher SHA (supplied at submit) are bound here and
#    reasserted before compute, after the event loop, after validation, and immediately before publish.
#  * ROOT + receipt publication are no-clobber atomic (hardlink -> identity/hash proof -> unlink src).
#    A crash after ROOT publish leaves ROOT-only; the next run STOPS for manual reconciliation.
#  * The P3F validator SHA is BOUND (Gate-3 final); the launcher invokes ONLY the P3F validator, which
#    composes domain -> base. assert_validator_bound fails closed on any unresolved/malformed hash.
#
# set -u intentionally OMITTED (root_6_28 conda deactivate aborts under nounset -- AGENTS.md).
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"

# ---- Immutable bound footing (matches the validated G2 build) ----------------
BUILT_SOURCE_COMMIT="486e53e677eb64eb9d622ff6e5daecb3e62aab22"          # commit the binary was BUILT from
ACTIVE_INTERFACE_COMMIT="2e8c214abc4b3ffc4ef371e8da6b5f107611862f"      # full active-interface commit
EXPECTED_BIN_SHA="61d7dfbf7ee38f39e51c656b48702056c773c3d1c5d1b2d9bf08a6da42d2e19b"
# Built-source provenance: the C++ source the binary was built from must match byte-for-byte. Fail
# closed on any drift; NEVER rebuild or launch under a drifted source.
EXPECTED_SOURCE_BLOB="b7e1edbce21545f1f824fe706047bd0f943a60ea"
EXPECTED_SOURCE_SHA="57792e42fe3f5a663016f94b91a5631fc50349135c92b35a08eaefcb85812be3"
# Validator composition: P3F -> domain -> base. The launcher invokes ONLY the P3F validator, which
# composes the domain validator, which forwards the base smoke validator. A DIRECT base invocation is
# INVALID (known finite out-of-domain rows in 1D/1E/1F/1P); only P3F->domain->base is authoritative.
EXPECTED_P3F_VAL_SHA="d782a47868863f2fc9a743f25f91549f0ab70a3ce7ff64f4db946b36a2df38ed"
EXPECTED_DOMAIN_VAL_SHA="32634d6832b4c1f6e5f9036a425b7412f004e2de0aa77828106646d7fc6e3739"
EXPECTED_BASE_G2_VAL_SHA="3b5c4ae9b954a6db2ac8dadf25abb433cc0024f9ee182e589de654ba44b5f1f8"
RECEIPT_SCHEMA="p3f-pet-production-playlist-receipt-v1"

BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"
SOURCE="${REPO}/MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp"
SOURCE_REL="MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp"
P3F_VALIDATOR="${REPO}/nd-unfolding/pet/validate_p3f_pet_fullevent.py"       # authored by Agent B (do not edit)
DOMAIN_VALIDATOR="${REPO}/nd-unfolding/pet/validate_g2_fullevent_domain.py"  # composed by the P3F validator
BASE_G2_VALIDATOR="${REPO}/nd-unfolding/pet/validate_g2_fullevent_smoke.py"  # forwarded by domain; NEVER called directly
MANIFEST_DIR="${REPO}/2d-unfolding/playlist_manifests"
# collision-isolated namespace
WORK_ROOT="${REPO}/nd-unfolding/p3f_pet_fullevent/work"
FINAL_DIR="${REPO}/nd-unfolding/p3f_pet_fullevent/final"
LOG_DIR="${REPO}/nd-unfolding/p3f_pet_fullevent/logs"

BANDS=(BeamAngleX BeamAngleY MuonResolution Muon_Energy_MINERvA Muon_Energy_MINOS)
ENDPOINTS=(0 1)
PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)

# 24 canonical manifest SHA-256, bound at commit time from the committed G2 launcher (12 Data + 12 MC).
declare -A MANIFEST_SHA=(
  [1A_Data.txt]=b74d89654a4fc0400e100c3f6d30d6b87082e3fba0444b7f2dcfda8682488495
  [1A_MC.txt]=4100dca453de1beef0213a0feac1fe4faa77d769f2dd5f36f4e11c6cea4894f8
  [1B_Data.txt]=91fa4a24774bfa800cd021dd712e61c777f600a7fa0c77ef1f54dad289764b1e
  [1B_MC.txt]=89328d4fafe4d59818cbd0ea5c30427fe3221b800a057d100ed79866fb8a5bad
  [1C_Data.txt]=c9fb92bdd9e905e3ec67a85b5eb07e0e964116cb998887c50113ef59aab21464
  [1C_MC.txt]=efabcb1a5bb0db7cda0c40779fc4b50e7f0dfae8c7b0d7441886005f3b72ba60
  [1D_Data.txt]=a79b49dc2964e303e2cfb578c0ac9840684b82469d3aff57fbd56950dfc8dbd8
  [1D_MC.txt]=86b2fa7b30f483f1273d23ab36fa0b2f0c72eba0cbd9044af87b06b5c5d9ca77
  [1E_Data.txt]=ca171e580c1d4f10d21ef8fa0dc362415089bd52ce74bd72f06be14e96003422
  [1E_MC.txt]=621336248107b238dab2b9ab6d540886afd729f2175e045a67e479422202d908
  [1F_Data.txt]=96520de6b8948ded10a8780f029e9a4beb3966a8becc0c71250ae21609735e0d
  [1F_MC.txt]=88bbe5135e14bd4437d65b3ee3c2be7ab0ad2b72b4afde1821ca456f0edbac10
  [1G_Data.txt]=1972d2cba379c0cbacbacad7dc0b50100baef466b31621a7812cc8a2b31b36c6
  [1G_MC.txt]=d8e1b3751cdc72e9b515e3d911d1bf0966dc3172e12fb0b6463ed248d2498ffc
  [1L_Data.txt]=e3d5b12da14d2b846bbe59727cf5a8a619442fab53af875bf506358ce2f4e96e
  [1L_MC.txt]=0a9bc517601401bd097c5334deaf2e22f28ea8ba0352ba134ccb72155e4e9fb3
  [1M_Data.txt]=2fcf89d6d2046a52c5824eba4e55dcdf134f35236e1c85d32959bf2434849286
  [1M_MC.txt]=81ac1c7a45f6d6a287c4f0318537555921f1e88efd8060388a410587e21d0083
  [1N_Data.txt]=6d043afad8b3e699f58a8c930ce3f75b33b013c8758c3b8edb8f7de62eb9f006
  [1N_MC.txt]=c259ee39f17493e75b67fe618aa15fb67b93041ef05f7f2d4a538953ff27ce5c
  [1O_Data.txt]=14c50cdffad134a842a67a50aa00799e2c8b1268fe85b9642e4338c2900f64c3
  [1O_MC.txt]=bab6e708decd89f01ee35a76cd4d374d22e4985a8a112df3b9685fc18845f646
  [1P_Data.txt]=227387cc36f85f45f6f9c8fc180b59c15601d5379604ba73242b01927600a331
  [1P_MC.txt]=da814d6bc23340a0126e3b3870f921dd76bb6fe3cd8264ce9e5dd20e7f8d218c
)

die() { echo "[p3fpet][FAIL] $*" >&2; exit 1; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }
path_occupied() { [[ -e "$1" || -L "$1" ]]; }       # dangling symlink counts occupied
dev_ino() { stat -c '%d:%i' "$1"; }

# LOUD fail-closed guard: the P3F validator SHA must be a real bound 64-hex. Any unresolved or
# malformed value (empty, a re-introduced placeholder token, wrong length) is not 64-hex and dies here.
assert_validator_bound() {
  [[ "${EXPECTED_P3F_VAL_SHA}" =~ ^[0-9a-f]{64}$ ]] || die "P3F validator SHA is not a bound 64-hex (unresolved/malformed): ${EXPECTED_P3F_VAL_SHA}"
}

assert_isolated_namespace() {
  case "${WORK_ROOT}${FINAL_DIR}${LOG_DIR}" in
    *recoil*|*purity*|*of_inputs_pc*|*bkgsub*|*_PC_*|*/g2_fullevent/*|*/active_universe_5d/*)
      die "output namespace resolves to a forbidden/shared path" ;;
  esac
  [[ "${WORK_ROOT}" == *"/nd-unfolding/p3f_pet_fullevent/work" ]]  || die "WORK_ROOT not the isolated P3F-PET namespace: ${WORK_ROOT}"
  [[ "${FINAL_DIR}" == *"/nd-unfolding/p3f_pet_fullevent/final" ]] || die "FINAL_DIR not the isolated P3F-PET namespace: ${FINAL_DIR}"
  [[ "${LOG_DIR}"   == *"/nd-unfolding/p3f_pet_fullevent/logs"  ]] || die "LOG_DIR not the isolated P3F-PET namespace: ${LOG_DIR}"
}

# task -> BAND_IDX ENDPOINT PL_IDX BAND PL   (band-major)
decode_task() {
  local t="$1"
  [[ "$t" =~ ^[0-9]+$ ]] || die "task id not numeric: $t"
  (( t >= 0 && t < 120 )) || die "task $t out of range 0-119"
  BAND_IDX=$(( t / 24 )); ENDPOINT=$(( (t / 12) % 2 )); PL_IDX=$(( t % 12 ))
  BAND="${BANDS[$BAND_IDX]}"; PL="${PLAYLISTS[$PL_IDX]}"
}

# The launcher SHA is supplied at submit (P3F_LAUNCHER_SHA256) and verified == this script's self-hash.
assert_launcher_sha() {
  local self="${BASH_SOURCE[0]}" selfsha
  selfsha=$(sha_of "$self")
  [[ -n "${P3F_LAUNCHER_SHA256:-}" ]] || die "P3F_LAUNCHER_SHA256 must be supplied at submission (bind the launcher hash)"
  [[ "${P3F_LAUNCHER_SHA256}" == "$selfsha" ]] || die "launcher SHA drift: supplied ${P3F_LAUNCHER_SHA256} != self ${selfsha}"
  echo "$selfsha"
}

# Existence-based classification. Prints: RUN | CHECK | DIE <reason>
classify_publication() {
  local root="$1" receipt="$2" re=0 ce=0
  path_occupied "$root" && re=1
  path_occupied "$receipt" && ce=1
  if (( re==0 && ce==0 )); then echo "RUN"; return 0; fi
  if (( re==1 && ce==0 )); then echo "DIE ROOT-only: published ROOT without receipt ($root) — manual reconciliation"; return 0; fi
  if (( re==0 && ce==1 )); then echo "DIE receipt-only: receipt without ROOT ($receipt) — manual reconciliation"; return 0; fi
  if [[ ! -s "$root" ]]; then echo "DIE zero-length final ROOT ($root)"; return 0; fi
  if [[ ! -s "$receipt" ]]; then echo "DIE zero-length receipt ($receipt)"; return 0; fi
  echo "CHECK"
}

# Initial-run drift guard (before compute). Reasserted after loop, after validation, before publish.
assert_input_footing() {
  local pl="$1" dman="$2" mman="$3" g
  assert_validator_bound
  [[ -s "$dman" ]] || die "missing/empty data manifest $dman"
  [[ -s "$mman" ]] || die "missing/empty mc manifest $mman"
  [[ -x "$BIN" ]] || die "canonical binary missing/executable: $BIN"
  [[ -f "$SOURCE" ]] || die "built-source missing: $SOURCE"
  [[ -f "$P3F_VALIDATOR" ]] || die "P3F validator missing: $P3F_VALIDATOR"
  [[ -f "$DOMAIN_VALIDATOR" ]] || die "domain validator missing: $DOMAIN_VALIDATOR"
  [[ -f "$BASE_G2_VALIDATOR" ]] || die "base validator missing: $BASE_G2_VALIDATOR"
  g=$(sha_of "$BIN");               [[ "$g" == "$EXPECTED_BIN_SHA" ]] || die "binary drift: $g != $EXPECTED_BIN_SHA"
  # Fail closed on the declared build lineage as well as the working-tree bytes. This proves the
  # active-interface commit is in the built-source history and that the source blob at the declared
  # build commit is exactly the source used for the installed binary.
  git -C "$REPO" cat-file -e "${BUILT_SOURCE_COMMIT}^{commit}" 2>/dev/null || die "built-source commit is unavailable: $BUILT_SOURCE_COMMIT"
  git -C "$REPO" merge-base --is-ancestor "$ACTIVE_INTERFACE_COMMIT" "$BUILT_SOURCE_COMMIT" || die "active-interface commit is not an ancestor of built-source commit"
  g=$(git -C "$REPO" rev-parse "${BUILT_SOURCE_COMMIT}:${SOURCE_REL}" 2>/dev/null); [[ "$g" == "$EXPECTED_SOURCE_BLOB" ]] || die "built-commit source blob drift: $g != $EXPECTED_SOURCE_BLOB"
  # Working-tree source provenance: git blob AND sha256 must match the built-source binding (never rebuild/launch on drift).
  g=$(cd "$REPO" && git hash-object "$SOURCE_REL" 2>/dev/null); [[ "$g" == "$EXPECTED_SOURCE_BLOB" ]] || die "source git blob drift: $g != $EXPECTED_SOURCE_BLOB (do NOT rebuild/launch)"
  g=$(sha_of "$SOURCE");            [[ "$g" == "$EXPECTED_SOURCE_SHA" ]] || die "source sha256 drift: $g != $EXPECTED_SOURCE_SHA (do NOT rebuild/launch)"
  g=$(sha_of "$P3F_VALIDATOR");     [[ "$g" == "$EXPECTED_P3F_VAL_SHA" ]] || die "P3F validator drift: $g != $EXPECTED_P3F_VAL_SHA"
  g=$(sha_of "$DOMAIN_VALIDATOR");  [[ "$g" == "$EXPECTED_DOMAIN_VAL_SHA" ]] || die "domain validator drift: $g != $EXPECTED_DOMAIN_VAL_SHA"
  g=$(sha_of "$BASE_G2_VALIDATOR"); [[ "$g" == "$EXPECTED_BASE_G2_VAL_SHA" ]] || die "base validator drift: $g != $EXPECTED_BASE_G2_VAL_SHA"
  g=$(sha_of "$dman");              [[ "$g" == "${MANIFEST_SHA[${pl}_Data.txt]}" ]] || die "data manifest drift for $pl ($g)"
  g=$(sha_of "$mman");              [[ "$g" == "${MANIFEST_SHA[${pl}_MC.txt]}" ]]   || die "mc manifest drift for $pl ($g)"
}

quarantine_stale_partial() {
  local wf="$1" workdir="$2" tag="$3"
  path_occupied "$wf" || return 0
  local q="${workdir}/partial_${tag}"
  mkdir -p "$q" || die "cannot create quarantine dir ${q}"
  mv "$wf" "$q/" || die "failed to quarantine stale work partial ${wf}"
  ! path_occupied "$wf" || die "stale work partial still present after quarantine: ${wf}"
  echo "$q"
}

publish_root_noclobber() {
  local src="$1" dst="$2"
  path_occupied "$dst" && die "refuse ROOT publish: destination already exists (race): $dst"
  local src_sha src_di; src_sha=$(sha_of "$src"); src_di=$(dev_ino "$src")
  ln "$src" "$dst" || die "atomic hardlink ROOT publish failed (destination may have appeared): $dst"
  path_occupied "$dst" || die "post-publish: ROOT destination absent: $dst"
  local dst_sha dst_di; dst_sha=$(sha_of "$dst"); dst_di=$(dev_ino "$dst")
  [[ "$dst_di" == "$src_di" ]] || die "post-publish ROOT not a hardlink of source (dev:ino $dst_di != $src_di)"
  [[ "$dst_sha" == "$src_sha" ]] || die "post-publish ROOT content hash mismatch: $dst_sha != $src_sha"
  rm "$src" || die "failed to unlink work ROOT after publish: $src"
  ! path_occupied "$src" || die "post-publish: work ROOT source still present: $src"
  echo "$dst_sha"
}

publish_receipt_noclobber() {
  local tmp="$1" dst="$2"
  path_occupied "$dst" && die "refuse receipt publish: destination already exists: $dst"
  local tmp_sha tmp_di; tmp_sha=$(sha_of "$tmp"); tmp_di=$(dev_ino "$tmp")
  ln "$tmp" "$dst" || die "atomic hardlink receipt publish failed: $dst"
  path_occupied "$dst" || die "post-publish: receipt destination absent: $dst"
  local dst_sha dst_di; dst_sha=$(sha_of "$dst"); dst_di=$(dev_ino "$dst")
  [[ "$dst_di" == "$tmp_di" ]] || die "post-publish receipt not a hardlink of temp (dev:ino $dst_di != $tmp_di)"
  [[ "$dst_sha" == "$tmp_sha" ]] || die "post-publish receipt content hash mismatch: $dst_sha != $tmp_sha"
  rm "$tmp" || die "failed to unlink receipt temp after publish: $tmp"
  ! path_occupied "$tmp" || die "post-publish: receipt temp still present: $tmp"
}

# Deep resume validation on a both-present pair. exit 0 = resume-skip; nonzero = caller must DIE.
validate_resume() {
  local root="$1" receipt="$2" band="$3" ep="$4" pl="$5" dman="$6" mman="$7" launchersha="$8"
  local dsha msha vsha domsha g2sha bsha srcblob srcsha
  dsha=$(sha_of "$dman"); msha=$(sha_of "$mman")
  vsha=$(sha_of "$P3F_VALIDATOR"); domsha=$(sha_of "$DOMAIN_VALIDATOR"); g2sha=$(sha_of "$BASE_G2_VALIDATOR")
  bsha=$(sha_of "$BIN"); srcblob=$(cd "$REPO" && git hash-object "$SOURCE_REL" 2>/dev/null); srcsha=$(sha_of "$SOURCE")
  python3 - "$receipt" "$root" "$band" "$ep" "$pl" "$EXPECTED_BIN_SHA" "$bsha" \
           "$EXPECTED_P3F_VAL_SHA" "$vsha" "$EXPECTED_DOMAIN_VAL_SHA" "$domsha" "$EXPECTED_BASE_G2_VAL_SHA" "$g2sha" \
           "$EXPECTED_SOURCE_BLOB" "$srcblob" "$EXPECTED_SOURCE_SHA" "$srcsha" \
           "$dman" "$mman" "$dsha" "$msha" "${MANIFEST_SHA[${pl}_Data.txt]}" "${MANIFEST_SHA[${pl}_MC.txt]}" \
           "$RECEIPT_SCHEMA" "$BUILT_SOURCE_COMMIT" "$launchersha" <<'PY'
import json,sys,hashlib
(rc,root,band,ep,pl,expbin,curbin,expval,curval,expdom,curdom,expg2,curg2,
 expsrcblob,cursrcblob,expsrcsha,cursrcsha,dman,mman,curd,curm,bndd,bndm,schema,builtcommit,launchersha)=sys.argv[1:27]
def fail(m): print("[resume-reject]",m,file=sys.stderr); sys.exit(3)
def sha256(path):
    h=hashlib.sha256()
    try:
        with open(path,"rb") as f:
            for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    except Exception as e: fail(f"cannot read {path}: {e}")
    return h.hexdigest()
try: d=json.load(open(rc))
except Exception as e: fail(f"receipt not valid JSON: {e}")
if d.get("receipt_schema")!=schema: fail("schema mismatch")
if d.get("verdict")!="PASS": fail("verdict != PASS")
if d.get("playlist")!=pl: fail("playlist mismatch")
env=d.get("env",{})
if env.get("MNV101_ACTIVE_UNIVERSE")!=f"{band}:{ep}": fail("active-universe env identity mismatch")
if env.get("MNV101_DUMP_POINTCLOUD")!="1" or env.get("MNV101_FULL_PHASE_SPACE")!="1": fail("pointcloud/full-phase env not '1'")
if env.get("MNV101_DUMP_UNIVERSES","<unset>")!="<unset>": fail("MNV101_DUMP_UNIVERSES must be unset")
if d.get("binary_sha256")!=expbin or curbin!=expbin: fail("binary hash mismatch/drift")
if d.get("built_source_commit")!=builtcommit: fail("built_source_commit mismatch")
if d.get("active_interface_commit")!="2e8c214abc4b3ffc4ef371e8da6b5f107611862f": fail("active_interface_commit mismatch")
if d.get("source_git_blob")!=expsrcblob or cursrcblob!=expsrcblob: fail("source git blob mismatch/drift")
if d.get("source_sha256")!=expsrcsha or cursrcsha!=expsrcsha: fail("source sha256 mismatch/drift")
if d.get("launcher_sha256")!=launchersha: fail("launcher sha mismatch")
fr=d.get("final_root",{})
if fr.get("path")!=root: fail("final_root.path mismatch")
root_sha=sha256(root)
if fr.get("sha256")!=root_sha: fail("final ROOT content hash != receipt")
md=d.get("manifest_data",{}); mm=d.get("manifest_mc",{})
if md.get("sha256")!=curd or curd!=bndd: fail("data manifest hash mismatch/drift")
if mm.get("sha256")!=curm or curm!=bndm: fail("mc manifest hash mismatch/drift")

# The final receipt is self-contained: it embeds the complete atomic P3F report rather than
# depending on mutable WORK receipts. Revalidate all scientific/provenance components on resume.
report=d.get("validation_report")
if not isinstance(report,dict): fail("embedded validation_report missing")
if report.get("verdict")!="PASS" or report.get("n_failed")!=0: fail("embedded P3F report not zero-failure PASS")
components=report.get("component_verdicts") or {}
if set(components)!={"inventory","domain","active","census"} or not all(components.values()): fail("embedded component verdicts incomplete/non-PASS")
if (report.get("root") or {}).get("sha256")!=root_sha: fail("embedded P3F root hash mismatch")
if (report.get("this_validator") or {}).get("sha256")!=curval or curval!=expval: fail("embedded P3F validator hash mismatch/drift")
inv=report.get("inventory") or {}
if inv.get("band")!=band or int(inv.get("endpoint",-1))!=int(ep) or inv.get("playlist")!=pl or inv.get("n_total_files")!=120 or inv.get("in_inventory") is not True: fail("embedded inventory identity mismatch")
expected={"activeUniverseBand":band,"activeUniverseIndex":int(ep),"hasActiveUniverse":1,"activeUniverseIsLateral":1}
ea=report.get("expected_active") or {}; oa=report.get("observed_active") or {}
for key,value in expected.items():
    if ea.get(key)!=value or oa.get(key)!=value: fail(f"embedded active identity mismatch: {key}")
census_names=["activeUniverseTruthEntrants","activeUniverseTruthExits","activeUniverseRecoEntrants","activeUniverseRecoExits"]
if ea.get("census_params")!=census_names: fail("embedded expected census parameter list mismatch")
oc=report.get("observed_census") or {}
for key in census_names:
    value=oc.get(key)
    if not isinstance(value,(int,float)) or int(value)!=value or value<0: fail(f"embedded census invalid: {key}")
if d.get("expected_active")!=ea or d.get("observed_active")!=oa or d.get("observed_census")!=oc: fail("top-level active/census copy differs from embedded report")

val=d.get("p3f_validator") or {}
if val.get("sha256")!=curval or curval!=expval: fail("P3F validator hash mismatch/drift")
if val.get("verdict")!="PASS" or val.get("n_failed")!=0 or val.get("component_verdicts")!=components: fail("P3F receipt summary mismatch")
if not isinstance(val.get("report_sha256"),str) or len(val["report_sha256"])!=64: fail("P3F report byte hash missing")
dom=report.get("domain_validator") or {}
if d.get("domain_validator")!=dom: fail("top-level domain report differs from embedded P3F report")
if dom.get("sha256")!=curdom or curdom!=expdom or dom.get("ran") is not True or dom.get("exit")!=0 or dom.get("status")!="PASS" or dom.get("fatal")!=[]: fail("domain validator evidence mismatch/non-PASS")
g2=report.get("base_validator") or {}
if d.get("base_validator")!=g2: fail("top-level base report differs from embedded P3F report")
if g2.get("sha256")!=curg2 or curg2!=expg2 or g2.get("ran") is not True or g2.get("exit") not in (0,1): fail("base validator evidence mismatch/nonterminal")
if g2.get("non_superseded_failures")!=[]: fail("base validator has non-superseded failures")
if not set(g2.get("superseded_failures") or []) <= {"bkg_reco_muon_valid","data_reco_muon_valid"}: fail("base validator superseded unexpected failures")
if d.get("inventory")!=inv or d.get("counts")!=report.get("counts"): fail("top-level inventory/counts copy differs from embedded report")
print("[resume-ok]"); sys.exit(0)
PY
}

# ---- define-only selftest (config view; NO compute). Sourced/run with P3F_PET_SELFTEST=1. ----
if [[ "${P3F_PET_SELFTEST:-0}" == "1" ]]; then
  assert_isolated_namespace
  bound="PLACEHOLDER(UNBOUND)"; [[ "${EXPECTED_P3F_VAL_SHA}" =~ ^[0-9a-f]{64}$ ]] && bound="bound"
  echo "[p3fpet-selftest] tasks=120 bands=${#BANDS[@]} endpoints=${#ENDPOINTS[@]} playlists=${#PLAYLISTS[@]} array=0-119%16"
  echo "[p3fpet-selftest] namespace work=${WORK_ROOT} final=${FINAL_DIR} logs=${LOG_DIR}"
  echo "[p3fpet-selftest] flags: MNV101_ACTIVE_UNIVERSE=<band>:<ep> MNV101_DUMP_POINTCLOUD=1 MNV101_FULL_PHASE_SPACE=1 MNV101_DUMP_UNIVERSES=<unset>"
  echo "[p3fpet-selftest] bin_sha=${EXPECTED_BIN_SHA} built_commit=${BUILT_SOURCE_COMMIT} interface_commit=${ACTIVE_INTERFACE_COMMIT}"
  echo "[p3fpet-selftest] source_blob=${EXPECTED_SOURCE_BLOB} source_sha=${EXPECTED_SOURCE_SHA}"
  echo "[p3fpet-selftest] validators: p3f=${EXPECTED_P3F_VAL_SHA} (${bound}) domain=${EXPECTED_DOMAIN_VAL_SHA} base=${EXPECTED_BASE_G2_VAL_SHA}"
  echo "[p3fpet-selftest] composition: P3F->domain->base (base NEVER invoked directly)  manifests=${#MANIFEST_SHA[@]}  schema=${RECEIPT_SCHEMA}"
  return 0 2>/dev/null || exit 0
fi

# ---- map-print mode (login-safe mapping check; NO compute). P3F_PET_MAP_TASK=<n>. ----
if [[ -n "${P3F_PET_MAP_TASK:-}" ]]; then
  decode_task "${P3F_PET_MAP_TASK}"
  echo "task ${P3F_PET_MAP_TASK} -> band=${BAND} endpoint=${ENDPOINT} playlist=${PL}"
  exit 0
fi

# ============================ array-task body ============================
assert_isolated_namespace
assert_validator_bound          # LAUNCH IMPOSSIBLE while the placeholder token is present (before anything else)
LAUNCHER_SHA="$(assert_launcher_sha)"
[[ -n "${SLURM_ARRAY_TASK_ID:-}" ]] || die "must run as an sbatch array task (SLURM_ARRAY_TASK_ID unset)"
decode_task "${SLURM_ARRAY_TASK_ID}"

DATA_MANIFEST="${MANIFEST_DIR}/${PL}_Data.txt"
MC_MANIFEST="${MANIFEST_DIR}/${PL}_MC.txt"
WORK="${WORK_ROOT}/${BAND}_${ENDPOINT}_${PL}"
FINAL_ROOT="${FINAL_DIR}/runEventLoopOmniFold_P3F_PET_FE_${BAND}_${ENDPOINT}_${PL}.root"
RECEIPT="${FINAL_DIR}/P3F_PET_receipt_${BAND}_${ENDPOINT}_${PL}.json"
VAL_JSON="${WORK}/p3f_pet_validation_${BAND}_${ENDPOINT}_${PL}.json"
WORK_ROOT_FILE="${WORK}/runEventLoopOmniFold.root"

echo "[p3fpet] node=$(hostname) job=${SLURM_JOB_ID:-NA} task=${SLURM_ARRAY_TASK_ID} band=${BAND} ep=${ENDPOINT} pl=${PL} $(date -u '+%Y-%m-%dT%H:%M:%SZ')"

# 1. Classify publication state (existence-based, fail-closed).
VERDICT="$(classify_publication "$FINAL_ROOT" "$RECEIPT")"
case "$VERDICT" in
  RUN) : ;;
  CHECK)
    if validate_resume "$FINAL_ROOT" "$RECEIPT" "$BAND" "$ENDPOINT" "$PL" "$DATA_MANIFEST" "$MC_MANIFEST" "$LAUNCHER_SHA"; then
      echo "[p3fpet] RESUME-SKIP: ${BAND}_${ENDPOINT}_${PL} already published and fully validated (exact match)."; exit 0
    else
      die "existing ${BAND}_${ENDPOINT}_${PL} final ROOT/receipt pair FAILED resume validation; refusing to overwrite. Manual reconciliation required."
    fi ;;
  DIE*) die "${VERDICT#DIE }" ;;
  *)    die "unknown publication classification: ${VERDICT}" ;;
esac

# 2. Initial-execution drift guard BEFORE any compute.
assert_input_footing "$PL" "$DATA_MANIFEST" "$MC_MANIFEST"
mkdir -p "$WORK" "$FINAL_DIR" "$LOG_DIR"

# 3. Duplicate-writer guard (per-task nonblocking flock).
exec 200>"${WORK}/.p3fpet.lock"
flock -n 200 || die "another writer holds the lock for ${BAND}_${ENDPOINT}_${PL} (${WORK}/.p3fpet.lock)"

# 4. Re-classify under the lock.
VERDICT2="$(classify_publication "$FINAL_ROOT" "$RECEIPT")"
[[ "$VERDICT2" == "RUN" ]] || die "publication state changed after acquiring lock (${VERDICT2}); refusing to run ${BAND}_${ENDPOINT}_${PL}"

# 5. Quarantine a stale WORK partial (fatal on failure).
QDIR="$(quarantine_stale_partial "$WORK_ROOT_FILE" "$WORK" "$(date -u '+%Y%m%dT%H%M%SZ')_${SLURM_JOB_ID:-NA}")"
[[ -n "$QDIR" ]] && echo "[p3fpet] quarantined stale work partial -> ${QDIR}"

# 6. Environment + event loop. EXACTLY three flags: active universe + point cloud + full phase space;
#    MNV101_DUMP_UNIVERSES explicitly unset. Fresh full-event ROOT from canonical raw Data/MC manifests.
source "${REPO}/setup_salloc_env.sh"
cd "$WORK"
unset MNV101_DUMP_UNIVERSES
echo "[p3fpet] START loop ${BAND}_${ENDPOINT}_${PL} $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
env -u MNV101_DUMP_UNIVERSES \
    MNV101_ACTIVE_UNIVERSE="${BAND}:${ENDPOINT}" MNV101_DUMP_POINTCLOUD=1 MNV101_FULL_PHASE_SPACE=1 \
    "$BIN" "$DATA_MANIFEST" "$MC_MANIFEST"
[[ -s "$WORK_ROOT_FILE" ]] || die "event loop produced no/empty ROOT for ${BAND}_${ENDPOINT}_${PL}"
echo "[p3fpet] END loop ${BAND}_${ENDPOINT}_${PL} $(date -u '+%Y-%m-%dT%H:%M:%SZ')"

# 6b. Reassert footing after the (multi-hour) loop, BEFORE validating.
assert_input_footing "$PL" "$DATA_MANIFEST" "$MC_MANIFEST"

# 7. Validation BEFORE publication: invoke ONLY the P3F validator (exact named-option CLI). It composes
#    the domain validator, which forwards the base smoke validator; the launcher NEVER calls the base
#    smoke validator directly (known finite out-of-domain rows in 1D/1E/1F/1P make a direct call
#    invalid). Require top-level verdict == PASS from its atomic report.
python3 "$P3F_VALIDATOR" --root "$WORK_ROOT_FILE" --band "$BAND" --endpoint "$ENDPOINT" --playlist "$PL" \
    --work "$VAL_JSON" --domain-validator "$DOMAIN_VALIDATOR" --base-validator "$BASE_G2_VALIDATOR" \
    || die "P3F validation FAILED for ${BAND}_${ENDPOINT}_${PL} (see ${VAL_JSON})"
python3 - "$VAL_JSON" "$BAND" "$ENDPOINT" "$PL" "$EXPECTED_P3F_VAL_SHA" "$EXPECTED_DOMAIN_VAL_SHA" "$EXPECTED_BASE_G2_VAL_SHA" <<'PY' || die "P3F report integration check failed for ${BAND}_${ENDPOINT}_${PL}"
import json,sys
path,band,ep,pl,p3fsha,domsha,basesha=sys.argv[1:8]
d=json.load(open(path))
assert d.get("verdict")=="PASS" and d.get("n_failed")==0, (d.get("verdict"),d.get("n_failed"))
components=d.get("component_verdicts") or {}
assert set(components)=={"inventory","domain","active","census"} and all(components.values()), components
assert (d.get("this_validator") or {}).get("sha256")==p3fsha
inv=d.get("inventory") or {}
assert inv.get("band")==band and int(inv.get("endpoint"))==int(ep) and inv.get("playlist")==pl and inv.get("n_total_files")==120 and inv.get("in_inventory") is True
expected={"activeUniverseBand":band,"activeUniverseIndex":int(ep),"hasActiveUniverse":1,"activeUniverseIsLateral":1}
for key,value in expected.items():
    assert (d.get("expected_active") or {}).get(key)==value and (d.get("observed_active") or {}).get(key)==value, key
dom=d.get("domain_validator") or {}
assert dom.get("sha256")==domsha and dom.get("ran") is True and dom.get("exit")==0 and dom.get("status")=="PASS" and dom.get("fatal")==[], dom
base=d.get("base_validator") or {}
assert base.get("sha256")==basesha and base.get("ran") is True and base.get("exit") in (0,1), base
assert base.get("non_superseded_failures")==[]
assert set(base.get("superseded_failures") or []) <= {"bkg_reco_muon_valid","data_reco_muon_valid"}
PY

# 8. Reassert footing + require RUN once more immediately before publish.
VERDICT3="$(classify_publication "$FINAL_ROOT" "$RECEIPT")"
[[ "$VERDICT3" == "RUN" ]] || die "publication state changed before publish (${VERDICT3}); refusing to publish ${BAND}_${ENDPOINT}_${PL}"
assert_input_footing "$PL" "$DATA_MANIFEST" "$MC_MANIFEST"
PUB_SHA="$(publish_root_noclobber "$WORK_ROOT_FILE" "$FINAL_ROOT")"
ROOT_SIZE="$(stat -c '%s' "$FINAL_ROOT")"

# 9. Build receipt into a unique same-dir temp (fsync), then no-clobber atomic publish LAST.
DSHA=$(sha_of "$DATA_MANIFEST"); MSHA=$(sha_of "$MC_MANIFEST")
VSHA=$(sha_of "$P3F_VALIDATOR"); DOMSHA=$(sha_of "$DOMAIN_VALIDATOR"); BASESHA=$(sha_of "$BASE_G2_VALIDATOR")
SRCBLOB=$(cd "$REPO" && git hash-object "$SOURCE_REL"); SRCSHA=$(sha_of "$SOURCE")
TMP_RCPT="$(mktemp "${FINAL_DIR}/.p3frcpt_${BAND}_${ENDPOINT}_${PL}.XXXXXX")"
python3 - "$TMP_RCPT" "$FINAL_ROOT" "$PUB_SHA" "$ROOT_SIZE" "$BAND" "$ENDPOINT" "$PL" \
         "$EXPECTED_BIN_SHA" "$BUILT_SOURCE_COMMIT" "$ACTIVE_INTERFACE_COMMIT" "$SRCBLOB" "$SRCSHA" "$LAUNCHER_SHA" \
         "$DATA_MANIFEST" "$MC_MANIFEST" "$DSHA" "$MSHA" \
         "$P3F_VALIDATOR" "$VSHA" "$VAL_JSON" "$DOMAIN_VALIDATOR" "$DOMSHA" "$BASE_G2_VALIDATOR" "$BASESHA" \
         "${SLURM_JOB_ID:-NA}" "${SLURM_ARRAY_TASK_ID}" "$REPO" "$RECEIPT_SCHEMA" <<'PY'
import json,sys,os,datetime,subprocess,hashlib
(tmp,root,root_sha,root_size,band,ep,pl,binsha,builtcommit,ifacecommit,srcblob,srcsha,launchersha,
 dman,mman,dsha,msha,valp,vsha,valjson,domp,domsha,basep,basesha,jid,tid,repo,schema)=sys.argv[1:29]
try: head=subprocess.check_output(["git","-C",repo,"rev-parse","HEAD"]).decode().strip()
except Exception: head="UNKNOWN"
report=json.load(open(valjson))          # complete atomic P3F report, embedded below for self-contained resume/audit
rpt_sha=hashlib.sha256(open(valjson,"rb").read()).hexdigest()
r={"receipt_schema":schema,"playlist":pl,"verdict":report.get("verdict"),
   "expected_active":report.get("expected_active"),
   "observed_active":report.get("observed_active"),
   "observed_census":report.get("observed_census"),
   "inventory":report.get("inventory"),"counts":report.get("counts"),
   "validation_report":report,
   "binary_sha256":binsha,"binary_sha256_expected":binsha,
   "built_source_commit":builtcommit,"active_interface_commit":ifacecommit,
   "source_git_blob":srcblob,"source_sha256":srcsha,
   "runtime_launcher_head":head,"launcher_sha256":launchersha,
   "env":{"MNV101_ACTIVE_UNIVERSE":f"{band}:{ep}","MNV101_DUMP_POINTCLOUD":"1",
          "MNV101_FULL_PHASE_SPACE":"1","MNV101_DUMP_UNIVERSES":"<unset>"},
   "manifest_data":{"path":dman,"sha256":dsha},
   "manifest_mc":{"path":mman,"sha256":msha},
   "p3f_validator":{"path":valp,"sha256":vsha,"report_path":valjson,"report_sha256":rpt_sha,
                    "verdict":report.get("verdict"),"n_checks":report.get("n_checks"),
                    "n_failed":report.get("n_failed"),"component_verdicts":report.get("component_verdicts")},
   "domain_validator":report.get("domain_validator"),
   "base_validator":report.get("base_validator"),
   "final_root":{"path":root,"sha256":root_sha,"size_bytes":int(root_size)},
   # This is a running task receipt, so it intentionally records task identity but does not fabricate
   # terminal sacct state. Terminal accounting belongs to the complete Gate-3 manifest.
   "slurm":{"jobid":jid,"array_task_id":int(tid),"node":os.uname().nodename},
   "produced_utc":datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}
with open(tmp,"w") as f:
    f.write(json.dumps(r,indent=2)+"\n"); f.flush(); os.fsync(f.fileno())
print("receipt-temp-written")
PY
publish_receipt_noclobber "$TMP_RCPT" "$RECEIPT"
echo "[p3fpet] DONE ${BAND}_${ENDPOINT}_${PL} root=${FINAL_ROOT} sha=${PUB_SHA} receipt=${RECEIPT} $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
