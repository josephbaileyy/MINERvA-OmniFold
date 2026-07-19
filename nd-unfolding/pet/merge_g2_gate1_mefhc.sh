#!/bin/bash
# Hash-bound, receipt-last MEFHC merge of the twelve committed G2 Gate-1A ROOTs.
# No overwrite, no partial final accepted, and no PET/NPZ work.
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
GATE_SUMMARY="${REPO}/docs/orchestration/state/g2-gate1-all12-validation-20260719.json"
EXPECTED_GATE_SHA="23b652d69460d61f2c347d0ec50c883043df83e0aa3fab3eda56b18b7364911f"
PAIR_VALIDATOR="${REPO}/nd-unfolding/pet/validate_g2_gate1_pairs.py"
DOMAIN_VALIDATOR="${REPO}/nd-unfolding/pet/validate_g2_fullevent_domain.py"
FINAL_DIR="${REPO}/nd-unfolding/g2_fullevent/merged"
FINAL_ROOT="${FINAL_DIR}/runEventLoopOmniFold_G2_FPS_MEFHC.root"
FINAL_RECHECK="${FINAL_DIR}/G2_MEFHC_PREMERGE_REVALIDATION.json"
FINAL_DOMAIN="${FINAL_DIR}/G2_MEFHC_DOMAIN_VALIDATION.json"
FINAL_DOMAIN_BASE="${FINAL_DIR}/G2_MEFHC_DOMAIN_VALIDATION.json.base.json"
FINAL_RECEIPT="${FINAL_DIR}/G2_MEFHC_MERGE_RECEIPT.json"
PLAYLISTS="1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P"

die() { echo "[g2-merge][FAIL] $*" >&2; exit 1; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }
occupied() { [[ -e "$1" || -L "$1" ]]; }

[[ -f "$GATE_SUMMARY" ]] || die "Gate-1A summary missing"
[[ "$(sha_of "$GATE_SUMMARY")" == "$EXPECTED_GATE_SHA" ]] || die "Gate-1A summary hash drift"
[[ -f "$PAIR_VALIDATOR" && -f "$DOMAIN_VALIDATOR" ]] || die "validator missing"
mkdir -p "$FINAL_DIR"
exec 200>"${FINAL_DIR}/.g2_merge.lock"
flock -n 200 || die "another G2 merge owns the lock"
for path in "$FINAL_ROOT" "$FINAL_RECHECK" "$FINAL_DOMAIN" "$FINAL_DOMAIN_BASE" "$FINAL_RECEIPT"; do
  occupied "$path" && die "refuse occupied final path: $path"
done

source "${REPO}/setup_salloc_env.sh"
cd "$REPO"

PAIR_TMP="$(mktemp "${FINAL_DIR}/.all12_recheck.XXXXXX.json")"
ROOT_TMP="$(mktemp "${FINAL_DIR}/.g2_mefhc.XXXXXX.root")"
DOMAIN_TMP="$(mktemp "${FINAL_DIR}/.g2_domain.XXXXXX.json")"
RECEIPT_TMP="$(mktemp "${FINAL_DIR}/.g2_receipt.XXXXXX.json")"
cleanup() { rm -f -- "$PAIR_TMP" "$ROOT_TMP" "$DOMAIN_TMP" "${DOMAIN_TMP}.base.json" "$RECEIPT_TMP"; }
trap cleanup EXIT

echo "[g2-merge] revalidating all twelve immutable inputs ..."
/usr/bin/python3.11 "$PAIR_VALIDATOR" --repo "$REPO" --output "$PAIR_TMP" --hash-workers 4
/usr/bin/python3.11 - "$PAIR_TMP" "$EXPECTED_GATE_SHA" <<'PY' || die "all-12 premerge recheck failed"
import json,sys
d=json.load(open(sys.argv[1]))
assert d.get("status")=="PASS" and not d.get("failures") and len(d.get("pairs",{}))==12
PY

INPUTS=()
for pl in $PLAYLISTS; do
  root="${REPO}/nd-unfolding/g2_fullevent/final/runEventLoopOmniFold_G2_FPS_${pl}.root"
  [[ -s "$root" ]] || die "input missing: $root"
  INPUTS+=("$root")
done

echo "[g2-merge] TFileMerger 12 G2 ROOTs (explicit >100GB TTree limit) ..."
python3 - "$ROOT_TMP" "${INPUTS[@]}" <<'PY' || die "ROOT merge failed"
import sys
import ROOT
out=sys.argv[1]; inputs=sys.argv[2:]
# ROOT's default 100-GB tree limit auto-splits and breaks hadd/TFileMerger for
# this 113.5-GB cloud product. Keep the exact Gate-1 object in one file.
ROOT.TTree.SetMaxTreeSize(4 * 1024**4)
merger=ROOT.TFileMerger()
assert merger.OutputFile(out,"RECREATE"), "cannot open merge output"
for path in inputs:
    assert merger.AddFile(path), "cannot add %s" % path
assert merger.Merge(), "TFileMerger.Merge returned false"
PY
[[ -s "$ROOT_TMP" ]] || die "merge produced empty ROOT"

# TFileMerger adds TParameter values.  That is correct for POT and event
# counts, but hasTruthOnlyMisses is a semantic boolean: twelve validated input
# flags merge to 12 and must be normalized back to 1.  Require the exact
# expected pre-value so an unexpected metadata state fails closed.
python3 - "$ROOT_TMP" <<'PY' || die "merged boolean metadata normalization failed"
import sys
import ROOT

path = sys.argv[1]
f = ROOT.TFile.Open(path, "UPDATE")
assert f and not f.IsZombie(), "cannot reopen merged ROOT"
flag = f.Get("hasTruthOnlyMisses")
assert flag, "missing hasTruthOnlyMisses"
before = int(flag.GetVal())
assert before == 12, "unexpected merged hasTruthOnlyMisses=%d" % before
f.Delete("hasTruthOnlyMisses;*")
ROOT.TParameter(int)("hasTruthOnlyMisses", 1).Write()
f.Close()

f = ROOT.TFile.Open(path, "READ")
assert f and not f.IsZombie(), "cannot verify normalized merged ROOT"
after = f.Get("hasTruthOnlyMisses")
assert after and int(after.GetVal()) == 1, "boolean normalization did not persist"
f.Close()
print("[g2-merge] normalized hasTruthOnlyMisses: 12 -> 1")
PY

echo "[g2-merge] exhaustive merged-domain/schema validation ..."
python3 "$DOMAIN_VALIDATOR" "$ROOT_TMP" "$DOMAIN_TMP" || die "merged ROOT validation failed"
/usr/bin/python3.11 - "$DOMAIN_TMP" "$GATE_SUMMARY" "$FINAL_DOMAIN_BASE" "$FINAL_ROOT" <<'PY' || die "merged counts/provenance mismatch"
import hashlib,json,os,sys,tempfile
domain_path,gate_path,final_base,final_root=sys.argv[1:5]
domain=json.load(open(domain_path)); gate=json.load(open(gate_path))
assert domain.get("status")=="PASS" and not domain.get("fatal")
assert domain.get("domain")=={"pt_max":30.0,"p_par_max":120.0}
assert not domain.get("structural",{}).get("non_superseded_failures")
base_path=domain["structural"]["receipt"]
base=json.load(open(base_path)); expected=gate["aggregate_counts"]
for key in ("mc_truth_denom","mc_signal_reco","mc_background","data","nTruthOnlyMisses"):
    assert base["counts"][key]==expected[key], (key,base["counts"][key],expected[key])
for key in ("mcPOTUsed","dataPOTUsed"):
    got=float(base["counts"][key]); want=float(expected[key])
    assert abs(got-want) <= max(1.0,abs(want))*1e-12, (key,got,want)
# Replace temporary artifact paths with durable publication paths and rebind.
base["file"]=final_root
fd,tmp=tempfile.mkstemp(prefix=".base_rewrite.",dir=os.path.dirname(base_path))
with os.fdopen(fd,"w") as f:
    json.dump(base,f,indent=2); f.write("\n"); f.flush(); os.fsync(f.fileno())
os.replace(tmp,base_path)
domain["structural"]["base_receipt_sha256"]=hashlib.sha256(open(base_path,"rb").read()).hexdigest()
domain["structural"]["receipt"]=final_base
fd,tmp=tempfile.mkstemp(prefix=".domain_rewrite.",dir=os.path.dirname(domain_path))
with os.fdopen(fd,"w") as f:
    json.dump(domain,f,indent=2); f.write("\n"); f.flush(); os.fsync(f.fileno())
os.replace(tmp,domain_path)
PY

ROOT_SHA="$(sha_of "$ROOT_TMP")"
ROOT_SIZE="$(stat -c %s "$ROOT_TMP")"
DOMAIN_SHA="$(sha_of "$DOMAIN_TMP")"
PAIR_SHA="$(sha_of "$PAIR_TMP")"

/usr/bin/python3.11 - "$RECEIPT_TMP" "$REPO" "$GATE_SUMMARY" "$EXPECTED_GATE_SHA" \
  "$PAIR_TMP" "$PAIR_SHA" "$ROOT_TMP" "$ROOT_SHA" "$ROOT_SIZE" "$DOMAIN_TMP" "$DOMAIN_SHA" <<'PY'
import datetime,json,os,subprocess,sys
(out,repo,gate_path,gate_sha,recheck_path,recheck_sha,root_tmp,root_sha,root_size,
 domain_path,domain_sha)=sys.argv[1:12]
gate=json.load(open(gate_path)); domain=json.load(open(domain_path))
head=subprocess.check_output(["git","-C",repo,"rev-parse","HEAD"],text=True).strip()
receipt={
 "receipt_schema":"g2-mefhc-merge-receipt-v1","status":"PASS",
 "gate1a_summary":{"path":gate_path,"sha256":gate_sha},
 "premerge_revalidation":{"path":os.path.join(repo,"nd-unfolding/g2_fullevent/merged/G2_MEFHC_PREMERGE_REVALIDATION.json"),
                          "sha256":recheck_sha,"status":"PASS","n_pairs":12},
 "ordered_inputs":[{"playlist":pl,
   "path":gate["pairs"][pl]["root_path"],
   "sha256":gate["pairs"][pl]["root_sha256_actual"],
   "size_bytes":gate["pairs"][pl]["root_size_bytes"]} for pl in gate["playlist_order"]],
 "merged_root":{"path":os.path.join(repo,"nd-unfolding/g2_fullevent/merged/runEventLoopOmniFold_G2_FPS_MEFHC.root"),
                "sha256":root_sha,"size_bytes":int(root_size)},
 "metadata_normalization":{"field":"hasTruthOnlyMisses","merge_pre_value":12,
                           "published_value":1,"reason":"semantic boolean; TFileMerger adds TParameter values"},
 "domain_validation":{"path":os.path.join(repo,"nd-unfolding/g2_fullevent/merged/G2_MEFHC_DOMAIN_VALIDATION.json"),
                      "sha256":domain_sha,"status":domain["status"],
                      "base_receipt_path":domain["structural"]["receipt"],
                      "base_receipt_sha256":domain["structural"]["base_receipt_sha256"],
                      "out_of_domain_censused_and_bound":domain["out_of_domain_censused_and_bound"],
                      "non_superseded_failures":domain["structural"]["non_superseded_failures"]},
 "aggregate_counts":gate["aggregate_counts"],
 "conditional_use":gate["conditional_use"],
 "runtime_head":head,
 "produced_utc":datetime.datetime.now(datetime.timezone.utc).isoformat()}
with open(out,"w") as f:
    json.dump(receipt,f,indent=2,sort_keys=True); f.write("\n"); f.flush(); os.fsync(f.fileno())
PY

# Receipt-last, no-clobber publication under the held namespace lock.
for path in "$FINAL_ROOT" "$FINAL_RECHECK" "$FINAL_DOMAIN" "$FINAL_DOMAIN_BASE" "$FINAL_RECEIPT"; do
  occupied "$path" && die "race: final path appeared: $path"
done
ln "$ROOT_TMP" "$FINAL_ROOT" || die "ROOT hardlink publication failed"
[[ "$(sha_of "$FINAL_ROOT")" == "$ROOT_SHA" ]] || die "published ROOT hash mismatch"
ln "$PAIR_TMP" "$FINAL_RECHECK" || die "premerge recheck publication failed"
[[ "$(sha_of "$FINAL_RECHECK")" == "$PAIR_SHA" ]] || die "published premerge recheck hash mismatch"
ln "${DOMAIN_TMP}.base.json" "$FINAL_DOMAIN_BASE" || die "domain base receipt publication failed"
[[ "$(sha_of "$FINAL_DOMAIN_BASE")" == "$(/usr/bin/python3.11 -c 'import json,sys; print(json.load(open(sys.argv[1]))["structural"]["base_receipt_sha256"])' "$DOMAIN_TMP")" ]] || die "published domain base hash mismatch"
ln "$DOMAIN_TMP" "$FINAL_DOMAIN" || die "domain receipt publication failed"
[[ "$(sha_of "$FINAL_DOMAIN")" == "$DOMAIN_SHA" ]] || die "published domain hash mismatch"
ln "$RECEIPT_TMP" "$FINAL_RECEIPT" || die "merge receipt publication failed"
rm -f "$ROOT_TMP" "$PAIR_TMP" "$DOMAIN_TMP" "${DOMAIN_TMP}.base.json" "$RECEIPT_TMP"
echo "[g2-merge] PASS root=${FINAL_ROOT} sha=${ROOT_SHA} receipt=${FINAL_RECEIPT}"
