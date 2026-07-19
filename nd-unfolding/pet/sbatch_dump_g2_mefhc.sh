#!/bin/bash
#SBATCH --job-name=g2fe_dump
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=192G
#SBATCH --time=12:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=nd-unfolding/g2_fullevent/logs/g2fe_dump_%j.out
#SBATCH --error=nd-unfolding/g2_fullevent/logs/g2fe_dump_%j.err
# Fail-closed, receipt-last G2 MEFHC full-schema NPZ production.
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
ROOT_IN="${REPO}/nd-unfolding/g2_fullevent/merged/runEventLoopOmniFold_G2_FPS_MEFHC.root"
MERGE_RECEIPT="${REPO}/nd-unfolding/g2_fullevent/merged/G2_MEFHC_MERGE_RECEIPT.json"
OUT_DIR="${REPO}/nd-unfolding/g2_fullevent/input"
FINAL_NPZ="${OUT_DIR}/G2_FPS_MEFHC_P12.npz"
FINAL_RECEIPT="${OUT_DIR}/G2_FPS_MEFHC_P12_RECEIPT.json"
DUMPER="${REPO}/nd-unfolding/pet/dump_pointcloud_inputs.py"
CONTRACT="${REPO}/nd-unfolding/pet/fullevent_dump_contract.py"

die() { echo "[g2-dump][FAIL] $*" >&2; exit 1; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }
[[ -s "$ROOT_IN" && -s "$MERGE_RECEIPT" ]] || die "committed Gate-1B merge input/receipt missing"
[[ -f "$DUMPER" && -f "$CONTRACT" ]] || die "dumper/contract missing"
mkdir -p "$OUT_DIR" "${REPO}/nd-unfolding/g2_fullevent/logs"
exec 200>"${OUT_DIR}/.g2_dump.lock"
flock -n 200 || die "another G2 dump owns the lock"
[[ ! -e "$FINAL_NPZ" && ! -L "$FINAL_NPZ" ]] || die "refuse occupied final NPZ"
[[ ! -e "$FINAL_RECEIPT" && ! -L "$FINAL_RECEIPT" ]] || die "refuse occupied final receipt"

source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" && -x "$PYTHON_BIN" ]] || die "environment python3 is not executable"
"$PYTHON_BIN" -c 'import numpy' || die "environment python3 lacks numpy"
cd "${REPO}/nd-unfolding"

NPZ_TMP="$(mktemp "${OUT_DIR}/.g2_npz.XXXXXX.npz")"
RECEIPT_TMP="$(mktemp "${OUT_DIR}/.g2_npz_receipt.XXXXXX.json")"
cleanup() { rm -f -- "$NPZ_TMP" "$RECEIPT_TMP"; }
trap cleanup EXIT

# Recompute the large ROOT hash once and require the committed merge receipt to
# bind exactly this source before spending hours on the Python inventory pass.
ROOT_SHA="$(sha_of "$ROOT_IN")"
"$PYTHON_BIN" - "$MERGE_RECEIPT" "$ROOT_IN" "$ROOT_SHA" <<'PY' || die "merge receipt/source mismatch"
import json,sys
r=json.load(open(sys.argv[1])); source=sys.argv[2]; actual=sys.argv[3]
assert r.get("status")=="PASS"
assert r["merged_root"]["path"]==source
assert r["merged_root"]["sha256"]==actual
assert r["domain_validation"]["status"]=="PASS"
assert not r["domain_validation"]["non_superseded_failures"]
PY

echo "[g2-dump] reading validated MEFHC G2 ROOT and writing transactional P=12 NPZ"
python3 pet/dump_pointcloud_inputs.py --omnifile "$ROOT_IN" --num-part 12 --out "$NPZ_TMP"
[[ -s "$NPZ_TMP" ]] || die "dumper produced empty NPZ"
NPZ_SHA="$(sha_of "$NPZ_TMP")"
NPZ_SIZE="$(stat -c %s "$NPZ_TMP")"
DUMPER_SHA="$(sha_of "$DUMPER")"
CONTRACT_SHA="$(sha_of "$CONTRACT")"
MERGE_RECEIPT_SHA="$(sha_of "$MERGE_RECEIPT")"

# Read every NPY member header without materializing the multi-GB cloud arrays;
# the dumper itself already ran the full in-memory schema/alignment/identity
# contract immediately before its atomic write.
"$PYTHON_BIN" - "$RECEIPT_TMP" "$NPZ_TMP" "$NPZ_SHA" "$NPZ_SIZE" \
  "$ROOT_IN" "$ROOT_SHA" "$MERGE_RECEIPT" "$MERGE_RECEIPT_SHA" \
  "$DUMPER" "$DUMPER_SHA" "$CONTRACT" "$CONTRACT_SHA" "$SLURM_JOB_ID" <<'PY'
import datetime,hashlib,json,os,struct,subprocess,sys,zipfile
import numpy as np
(out,npz_path,npz_sha,npz_size,root_path,root_sha,merge_path,merge_sha,
 dumper_path,dumper_sha,contract_path,contract_sha,jobid)=sys.argv[1:14]
sys.path.insert(0,os.path.dirname(contract_path))
import fullevent_dump_contract as c

def npy_header(zf,name):
    with zf.open(name+".npy") as f:
        version=np.lib.format.read_magic(f)
        shape,fortran,dtype=np.lib.format._read_array_header(f,version)
        return {"shape":list(shape),"dtype":str(dtype),"fortran_order":bool(fortran)}

with zipfile.ZipFile(npz_path) as z:
    keys=sorted(x[:-4] for x in z.namelist() if x.endswith(".npy"))
    missing=sorted(set(c.REQUIRED_KEYS)-set(keys))
    assert not missing, missing
    headers={k:npy_header(z,k) for k in keys}
    def scalar(k):
        with z.open(k+".npy") as f: return np.lib.format.read_array(f).item()
    markers={k:scalar(k) for k in c.G2_SCHEMA}
c.assert_g2_schema(markers)
ns=headers["part_gen"]["shape"][0]
nd=headers["measured_pc"]["shape"][0]
nb=headers["bkg_part_reco"]["shape"][0]
for k in ("part_reco","reco_scalars","reco_muon","reco_vertex","reco_view","reco_time",
          "pass_reco","pass_truth","w_truth","w_reco","truth_scalars"):
    assert headers[k]["shape"][0]==ns,(k,headers[k]["shape"][0],ns)
for k in ("measured_scalars","data_muon","data_vertex","data_view","data_time"):
    assert headers[k]["shape"][0]==nd,(k,headers[k]["shape"][0],nd)
for k in ("bkg_reco_scalars","bkg_muon","bkg_vertex","bkg_view","bkg_time","w_bkg"):
    assert headers[k]["shape"][0]==nb,(k,headers[k]["shape"][0],nb)
assert headers["part_gen"]["shape"][1:]==[12,5]
assert headers["part_reco"]["shape"][1:]==[12,3]
assert headers["measured_pc"]["shape"][1:]==[12,3]
assert headers["bkg_part_reco"]["shape"][1:]==[12,3]
receipt={
 "receipt_schema":"g2-mefhc-fullschema-npz-v1","status":"PASS",
 "source_root":{"path":root_path,"sha256":root_sha},
 "merge_receipt":{"path":merge_path,"sha256":merge_sha},
 "dumper":{"path":dumper_path,"sha256":dumper_sha},
 "contract":{"path":contract_path,"sha256":contract_sha},
 "npz":{"path":os.path.join(os.path.dirname(npz_path),"G2_FPS_MEFHC_P12.npz"),
        "sha256":npz_sha,"size_bytes":int(npz_size)},
 "schema_markers":markers,"num_part":12,
 "inventory_rows":{"signal":ns,"data":nd,"background":nb},
 "member_headers":headers,"missing_required_keys":[],
 "runtime_contract":"full in-memory gates passed before atomic NPZ write; receipt revalidated all member headers",
 "slurm_job_id":jobid,"runtime_head":subprocess.check_output(["git","-C",os.path.dirname(os.path.dirname(os.path.dirname(dumper_path))),"rev-parse","HEAD"],text=True).strip(),
 "produced_utc":datetime.datetime.now(datetime.timezone.utc).isoformat()}
with open(out,"w") as f:
    json.dump(receipt,f,indent=2,sort_keys=True); f.write("\n"); f.flush(); os.fsync(f.fileno())
PY

# No-clobber product first, receipt last. Hard links make publication atomic
# within this filesystem; cleanup removes only the temporary names.
[[ ! -e "$FINAL_NPZ" && ! -e "$FINAL_RECEIPT" ]] || die "final path race"
ln "$NPZ_TMP" "$FINAL_NPZ" || die "NPZ publication failed"
[[ "$(sha_of "$FINAL_NPZ")" == "$NPZ_SHA" ]] || die "published NPZ hash mismatch"
ln "$RECEIPT_TMP" "$FINAL_RECEIPT" || die "receipt publication failed"
rm -f "$NPZ_TMP" "$RECEIPT_TMP"
echo "[g2-dump] PASS npz=$FINAL_NPZ sha=$NPZ_SHA receipt=$FINAL_RECEIPT"
