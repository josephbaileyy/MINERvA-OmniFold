#!/bin/bash
# FD-STAB dry run under ADDENDUM A1, step 1 of 2: the input pins, on a data-transfer node (dtn01), 0 node-h
# (FD-STAB-BINDING-1-A1.md ruling 4, merged at ff6ba188538a50af785d56657de01fbe1832d94c, and its Director's correction
# item 4, merged at c6f104ee as #766: the rerun after job 60826464, which is INVALID, into a NEW $OUT with a fresh
# record; record ad7f21d3 is not reused). The code pin stays M_A1.
# A fresh clone at M_A1 into $OUT/pins/deploy (clean; the A1 binding's five code
# blobs, the two unchanged data blobs, the declaration's and the addendum's sha256), then, with threads 1, nice 19, idle
# I/O and every read through O_NOATIME:
#   of_inputs_5d.npz and bkg_dump.npz against s1_assemble's pins;
#   the pv-ladder NuWro ratio against fd_f0_regrade.RATIO["closure_nuwro"], its schema mapped through the probe's
#     SCHEMA_TRUTH at M_A1, which must give PVL_TRUTH ("pvl_ratio");
#   F0b's closure product L-5D-PV_e_closure_nuwro.npz, from the products directory F0b read (--pvl-products), against
#     fd_f0_regrade.PINS["closure"] (the truth control's sixth argument; addendum §2);
#   the 734 bank and detector files against s1/PRESERVE-INVENTORY.sha256, each directory holding exactly the pinned set.
# Writes only under a NEW $OUT (step one's /pscratch/sd/j/josephrb/fd-stab-20261104 and the invalid run's
# /pscratch/sd/j/josephrb/fd-stab-a1-20261104 are not read or touched): the record pins-check.json (schema fd-stab-pins-check/2; verdict PASS only if every check passed) and
# check.log. Step 2 (stab_dry_a1r_submit.sh) requires this record by its sha256. No set -u. Any stop is final. Launched
# from a /dev/shm copy of itself (its path is $1), which it deletes at exit.
SELF=$1
M=cc54d86f7ac66c1346fa69e5894b2d2f000fb09c
OUT=/pscratch/sd/j/josephrb/fd-stab-a1r-20261104
P=$OUT/pins
D=$P/deploy
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
BKG=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz
BANK=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware
DET=/pscratch/sd/j/josephrb/s5p-20260926/bank_detector
PVL=/pscratch/sd/j/josephrb/pv-ladder-20261024
F0B=$PVL/products/L-5D-PV_e_closure_nuwro.npz
PY=$HOME/.conda/envs/root_6_28/bin/python3
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
case "$(hostname)" in dtn*) ;; *) bail ;; esac
[ ! -e "$OUT" ] && [ -x "$PY" ] || bail
mkdir -p "$P" || bail
exec > "$P/check.log" 2>&1
finish() { echo "pins check rc=$1"; date -u +%FT%TZ; echo "$1" > "$P/check.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "check script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$P/stab_pins_a1r_dtn.sh"

git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$P/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M_A1"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $M; porcelain --ignored lines: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
S=docs/orchestration/state/measurement-paper/5d-community-20261024
bad=0
while read -r b p; do
  [ "$(git -C "$D" rev-parse "$M:$p")" = "$b" ] && [ "$(git -C "$D" hash-object "$p")" = "$b" ] || { echo "MISMATCH $p"; bad=$((bad + 1)); }
done <<BLOBS
25179f9f704e61a920c9d0005283b4fcd357d825 nd-unfolding/estimator_stability_probe.py
9defbb44e99d0dcc538b7254ab998ba13feb354a nd-unfolding/sbatch_fd_stab.sh
0e4718902e1b156d340ba5a9848d522b5be0fc45 nd-unfolding/estimator_stability_analyze.py
22e211a20514f9a3c10145085f813c9f5f63f6f2 nd-unfolding/tests/test_estimator_stability_probe.py
9ab35c9839fc38322c47fedf95b774ea25d8942f nd-unfolding/tests/estimator_stability_mutation.py
27947e1add4dd5fbda17a17020976fd30bea1061 $S/fd/stab/no-ratio.json
dc2ac4e4f3098ce59a81fc043526d87b5c49ec77 $S/s1/PRESERVE-INVENTORY.sha256
BLOBS
decl=$(sha256sum "$D/$S/FD-STAB-DECLARATION.md" | cut -d' ' -f1)
add=$(sha256sum "$D/$S/FD-STAB-ADDENDUM-A1.md" | cut -d' ' -f1)
echo "bound blobs: 7 checked, $bad mismatches; declaration sha256 $decl; addendum A1 sha256 $add"
[ "$bad" -eq 0 ] && [ "$decl" = 6c91c0ccbb8061c0dfe755f2283ecbf0f12ba001737876df09f8882eca4ca2b4 ] \
  && [ "$add" = 277f6c799aca808315ce519f427007b7dec5da0c514dc5d0c229841ec01e23b2 ] || { echo "STOP: bound bytes"; finish 9; }

export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
echo "threads: OMP=$OMP_NUM_THREADS OPENBLAS=$OPENBLAS_NUM_THREADS MKL=$MKL_NUM_THREADS NUMEXPR=$NUMEXPR_NUM_THREADS; nice 19; ionice idle"
nice -n 19 ionice -c3 env -u PYTHONPATH "$PY" -I -B - "$D" "$M" "$NPZ" "$BKG" "$PVL" "$F0B" "$BANK" "$DET" "$P/pins-check.json" <<'PYEOF'
import hashlib, json, os, socket, sys, time
from pathlib import Path
D, M = Path(sys.argv[1]), sys.argv[2]
NPZ, BKG, PVL, F0B, BANK, DET, OUT = map(Path, sys.argv[3:])
sys.path.insert(0, str(D / "nd-unfolding"))
import estimator_stability_probe as ep  # noqa: E402  (SCHEMA_TRUTH, PVL_TRUTH and CLOSURES at M_A1)
import s1_assemble as sa                # noqa: E402  (the npz and bkg pins)
import fd_f0_regrade as f0              # noqa: E402  (the closure ratio's and the F0b product's pins)


def noatime(p, keep=False):
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME)
    h, data, n = hashlib.sha256(), bytearray(), 0
    with os.fdopen(fd, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b); n += len(b)
            if keep:
                data += b
    return h.hexdigest(), n, bytes(data)


t0 = time.time()
rec = {"schema": "fd-stab-pins-check/2", "addendum": "A1", "M": M, "host": socket.gethostname(),
       "started_utc": time.strftime("%FT%TZ", time.gmtime(t0)),
       "rule": "every read O_NOATIME; files against committed pins; each directory exactly its pinned set", "files": {}}
ok = True
for name, p, want in (("npz", NPZ, sa.INPUT_NPZ_SHA256), ("bkg", BKG, sa.BKG_SHA256)):
    got, n, _ = noatime(p)
    rec["files"][name] = {"path": str(p), "sha256": got, "pin": want, "bytes": n, "pin_source": f"s1_assemble.{'INPUT_NPZ_SHA256' if name == 'npz' else 'BKG_SHA256'}", "ok": got == want}
    ok &= got == want
    print(f"{name}: {'== pin' if got == want else '!= pin'} ({n} bytes)", flush=True)
row = [c for c in ep.CLOSURES if c[0] == "closure_nuwro"][0]
ratio = PVL / row[2][len("CLUSTER:"):]
got, n, raw = noatime(ratio, keep=True)
want = f0.RATIO["closure_nuwro"]
schema = json.loads(raw).get("schema")
kind = ep.SCHEMA_TRUTH.get(schema)
good = got == want and row[3] == "SCHEMA" and kind == ep.PVL_TRUTH
rec["files"]["closure_ratio"] = {"path": str(ratio), "sha256": got, "pin": want, "bytes": n, "pin_source": "fd_f0_regrade.RATIO['closure_nuwro']",
                                 "schema": schema, "declared_kind": row[3], "truth_kind": kind, "truth_kind_required": ep.PVL_TRUTH, "ok": good}
ok &= good
print(f"closure ratio: {'== pin' if got == want else '!= pin'}; schema {schema!r} -> {kind} (required {ep.PVL_TRUTH})", flush=True)
got, n, _ = noatime(F0B)
want = f0.PINS["closure"]
rec["files"]["f0b_product"] = {"path": str(F0B), "sha256": got, "pin": want, "bytes": n, "pin_source": "fd_f0_regrade.PINS['closure']", "ok": got == want}
ok &= got == want
print(f"F0b closure product: {'== pin' if got == want else '!= pin'} ({n} bytes)", flush=True)
inv = D / "docs/orchestration/state/measurement-paper/5d-community-20261024/s1/PRESERVE-INVENTORY.sha256"
pins = {Path(p.strip()): h for h, p in (l.split(None, 1) for l in inv.read_text().splitlines() if l.strip())}
rec["inventory"] = {"path": str(inv.relative_to(D)), "sha256": hashlib.sha256(inv.read_bytes()).hexdigest(), "rows": len(pins)}
total = 0
for key, d in (("bank", BANK), ("detector", DET)):
    want_set = {p for p in pins if p.parent == d}
    have = {p for p in d.iterdir() if p.is_file()}
    extra, missing = sorted(map(str, have - want_set)), sorted(map(str, want_set - have))
    mism, nbytes = [], 0
    for p in sorted(want_set & have):
        g, n, _ = noatime(p)
        nbytes += n
        if g != pins[p]:
            mism.append(str(p))
    total += len(want_set)
    good = not (extra or missing or mism) and len(want_set) > 0
    rec[key] = {"dir": str(d), "pinned": len(want_set), "present": len(have), "extra": extra, "missing": missing,
                "digest_mismatches": mism, "bytes_read": nbytes, "ok": good}
    ok &= good
    print(f"{key}: {len(want_set)} pinned, {len(have)} present, extra {len(extra)}, missing {len(missing)}, mismatches {len(mism)}, {nbytes} bytes", flush=True)
rec["pinned_dir_files"] = total
ok &= total == len(pins) == 734
t1 = time.time()
rec |= {"verdict": "PASS" if ok else "FAIL", "seconds": round(t1 - t0, 1), "written_utc": time.strftime("%FT%TZ", time.gmtime(t1)), "written_epoch": t1}
OUT.write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
print(json.dumps({"verdict": rec["verdict"], "wrote": str(OUT), "sha256": hashlib.sha256(OUT.read_bytes()).hexdigest()}))
sys.exit(0 if ok else 1)
PYEOF
rc=$?
echo "pins check python rc=$rc"
[ $rc = 0 ] || { echo "STOP: the inputs are not the pinned ones (final)"; finish 4; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy changed"; finish 9; }
finish 0
