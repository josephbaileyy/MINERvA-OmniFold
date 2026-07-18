#!/usr/bin/env python3
"""Blocker 4 (Agent C, 2nd repair round): READ-ONLY reuse + verification of the orchestrator's
owner-neutral full-file merged-input hash receipt (docs/orchestration/state/merged-input-hashes/
p4-merged-20260718/). Avoids a second 748GB hash pass: it recomputes only live size + integer-mtime
against the committed inventory and binds the committed hash-list / inventory digests.

Requires COMPLETE, summary.tsv, validation.tsv (result=PASS), fps.sha256, fps.inventory.tsv. For each
of the ten FPS merged inputs it checks the file exists and its live (size, int(mtime)) equals the
inventory row (i.e. unchanged since the validated hashing), then verifies sha256(fps.sha256) ==
validation.fps_hash_list_sha256 and sha256(fps.inventory.tsv) == validation.fps_inventory_sha256.
Exposes load_verified_input_hashes() -> {abs_path: full_sha256} for the publication manifest builder.

Fail-closed: any missing file, non-PASS validation, size/mtime drift, or digest mismatch raises.

  python fps_verify_merged_receipt.py         # prints bound digests + 10/10 size/mtime OK
"""
import os
import sys

import fps_provenance as fp

REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
RECEIPT = os.path.join(REPO, "docs/orchestration/state/merged-input-hashes/p4-merged-20260718")
REQUIRED = ["COMPLETE", "summary.tsv", "validation.tsv", "fps.sha256", "fps.inventory.tsv"]


def _read_kv_tsv(path):
    d = {}
    for line in open(path):
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 2:
            d[parts[0]] = parts[1]
    return d


def verify(receipt=RECEIPT):
    for f in REQUIRED:
        if not os.path.exists(os.path.join(receipt, f)):
            raise fp.FpsGateError(f"receipt: required file absent: {f}")
    val = _read_kv_tsv(os.path.join(receipt, "validation.tsv"))
    if val.get("result") != "PASS":
        raise fp.FpsGateError(f"receipt validation result != PASS ({val.get('result')})")

    # bind committed digests (recompute, don't trust strings)
    sha_list = os.path.join(receipt, "fps.sha256")
    inv = os.path.join(receipt, "fps.inventory.tsv")
    hl = fp.sha256_file(sha_list)
    iv = fp.sha256_file(inv)
    if hl != val.get("fps_hash_list_sha256"):
        raise fp.FpsGateError(
            f"fps.sha256 digest {hl} != validation.fps_hash_list_sha256 {val.get('fps_hash_list_sha256')}")
    if iv != val.get("fps_inventory_sha256"):
        raise fp.FpsGateError(
            f"fps.inventory.tsv digest {iv} != validation.fps_inventory_sha256 {val.get('fps_inventory_sha256')}")

    # recompute live size + integer mtime vs inventory (cheap; proves files unchanged since hashing)
    inv_rows = {}
    for line in open(inv):
        c = line.rstrip("\n").split("\t")
        if len(c) >= 3:
            inv_rows[c[2]] = (int(c[0]), int(c[1]))     # rel_path -> (size, int_mtime)
    hashes = {}
    for line in open(sha_list):
        c = line.rstrip("\n").split()
        if len(c) >= 2:
            hashes[c[1]] = c[0]                          # rel_path -> sha256
    fps_rows = {p: v for p, v in inv_rows.items() if "/fps/merged/" in p}
    if len(fps_rows) != fp.N_ENDPOINTS:
        raise fp.FpsGateError(f"receipt fps inventory has {len(fps_rows)} rows != {fp.N_ENDPOINTS}")
    verified = {}
    for rel, (size, mt) in sorted(fps_rows.items()):
        ap = os.path.join(REPO, rel)
        if not os.path.exists(ap):
            raise fp.FpsGateError(f"receipt: merged input missing on disk: {rel}")
        st = os.stat(ap)
        if st.st_size != size:
            raise fp.FpsGateError(f"{rel}: live size {st.st_size} != inventory {size}")
        if int(st.st_mtime) != mt:
            raise fp.FpsGateError(f"{rel}: live int(mtime) {int(st.st_mtime)} != inventory {mt}")
        if rel not in hashes:
            raise fp.FpsGateError(f"{rel}: present in inventory but absent from fps.sha256")
        verified[ap] = hashes[rel]
    return {
        "receipt_dir": receipt,
        "run_id": open(os.path.join(receipt, "COMPLETE")).read().strip(),
        "fps_hash_list_sha256": hl,
        "fps_inventory_sha256": iv,
        "launcher_sha256": val.get("launcher_sha256"),
        "fps_bytes": int(val.get("fps_bytes", 0)),
        "verified_input_sha256": verified,          # abs_path -> full sha256
    }


def load_verified_input_hashes(receipt=RECEIPT):
    return verify(receipt)["verified_input_sha256"]


def main():
    r = verify()
    print(f"[receipt] PASS  run_id={r['run_id']}  fps_bytes={r['fps_bytes']}")
    print(f"[receipt] fps_hash_list_sha256={r['fps_hash_list_sha256']}")
    print(f"[receipt] fps_inventory_sha256={r['fps_inventory_sha256']}")
    print(f"[receipt] launcher_sha256={r['launcher_sha256']}")
    print(f"[receipt] 10/10 live size+int(mtime) match inventory; full input SHA256 bound:")
    for ap, h in sorted(r["verified_input_sha256"].items()):
        print(f"   {os.path.basename(ap)[:52]:52s} {h[:16]}")
    sys.exit(0)


if __name__ == "__main__":
    main()
