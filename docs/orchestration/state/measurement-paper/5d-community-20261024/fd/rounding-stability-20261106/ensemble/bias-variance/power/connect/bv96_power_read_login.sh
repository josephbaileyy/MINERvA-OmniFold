#!/bin/bash
# BV96 O1 (the director's ruling of 2026-11-10): a read-only copy of FD-STAB's 70 control products for BV96's power
# simulation. These are the base and 51 jitters of the stability input, and the 18 noise-free closures at F0b's truths,
# under $OUT = /pscratch/sd/j/josephrb/fd-stab-a1r-20261104 (fd/receipts-stab-a1r/full/SHA256SUMS, as committed). F0b's truths
# are development truths, not BV96's reserved ones.
# Login node, nice 19, 0 node-h, no Slurm job. Every step stamped to the second. In order:
#   1. every file's stat (%F|%i|%h|%s|%Y|%X|%Z|%n) before the read;
#   2. one read of each through O_NOATIME. Each sha256 must equal its committed line, or nothing is printed and the
#      connect exits 8. Only then is a bundle printed, base64, between markers, with its sha256 and byte count. The bundle
#      is an in-memory np.savez_compressed holding, per product, xsec_flat, xtrue_flat (closures) and meta, and nothing else;
#   3. every stat after the read, which must be byte-identical to the one before, atime included. A difference is a STOP
#      (exit 4), reported unrepaired.
# It writes nothing on the cluster: no file under pscratch, CFS or HPSS. The only file it touches is the /dev/shm copy of
# itself ($1) that the launcher made, which it deletes. It uses no here-document or here-string (bash may back those
# with a temporary file), and no temporary file. The Mac side decodes the bundle and re-checks its sha256.
SELF=$1
OUT=/pscratch/sd/j/josephrb/fd-stab-a1r-20261104
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
ts() { date -u +%FT%TZ; }
finish() { echo "== bv96-o1 rc=$1 $(ts)"; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node: $(hostname)"; finish 9 ;; esac
echo "node $(hostname) $(ts)"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
LIST='0f5c32936c590bee1a90a0a03292105a73eee6ca9dd017b36571ef020e45af19  runs/control/closure/A7_genie_cv/stab_control_A7_genie_cv_s991000.npz
9e2dd31b05fb7dba3ed3622fe72ffdab77fc975ffef0f17b0a780658efae8134  runs/control/closure/A7_genie_mec/stab_control_A7_genie_mec_s991000.npz
b4d2ba5c34199352f90aab36b3a3c1cc9ad55c3cab79b375eb2c398746435179  runs/control/closure/A7_gibuu/stab_control_A7_gibuu_s991000.npz
e651ea2f65618372008d733aaf9c89822b902ffef161d18a12c3582ed8437c5c  runs/control/closure/A7_mnvtune/stab_control_A7_mnvtune_s991000.npz
dc8964923578d8e07efb43bd02f537b413017b4f92d7cfc0c0189d6abcc2be3f  runs/control/closure/A7_nuwro/stab_control_A7_nuwro_s991000.npz
7faa946fb4c13876f8901560187f92ec839837ec99140b6ba65a4729e2d14d9d  runs/control/closure/closure_nuwro/stab_control_closure_nuwro_s991000.npz
3753f4149fdcda5b7a67fad0eddb5b783e4642636d1574849743b9eb733f6cf4  runs/control/closure/nominal/stab_control_nominal_s991000.npz
95e2e352a34149badd49225a1d31204f6e62d314385d9d6e2bb23c20b137c618  runs/control/closure/P1g/stab_control_P1g_s991000.npz
d35c9125ee67705c9767cd7ef8079203f2c1667be6d1c476c9b98851b4ddd45c  runs/control/closure/P1r/stab_control_P1r_s991000.npz
b365e638e6a48848d09b62b82560b010bdc5c54b007a00fcc57cae968d0ee6a5  runs/control/closure/P2g/stab_control_P2g_s991000.npz
cd770c4a825e5852914076b4c23c1ecca2379eacb306c88bfed4d5cf107ef030  runs/control/closure/P2r/stab_control_P2r_s991000.npz
6ef2c11570f3d4706c7789d264b7016ef2045fc3bbb6a01c78978ff954091b18  runs/control/closure/P3g/stab_control_P3g_s991000.npz
e3e145a99e9427297543a6b1b46670b8634983633b971a3876ef5611406d1698  runs/control/closure/P3r/stab_control_P3r_s991000.npz
a197610a55ab0e1f9fafb5ae16ddd43eb15f0d4ca9e21ffaef75eccb729a8392  runs/control/closure/q3/stab_control_q3_s991000.npz
604837020b7b6837f46c6c474d20d7cf170ec6d39f9c5ba3b286cbaff05b7ee9  runs/control/closure/stage0c_gibuu/stab_control_stage0c_gibuu_s991000.npz
b88374383c78159fc6d8b36d7780e7a78543b9c734f9373c5da993aac30be720  runs/control/closure/W1/stab_control_W1_s991000.npz
fc6c57316ea66eba131706d6eac81572dcecf193a9f99d828164c550cb3ba3cf  runs/control/closure/W2/stab_control_W2_s991000.npz
20443186044b4744fe68762dea1798a38ff658debac0cdba241e6cdeacf61dc6  runs/control/closure/W3/stab_control_W3_s991000.npz
531f735102e5ca8ec2fd3f824848bbc05d14b2afe245a0eef3fc4943914d820d  runs/control/stability/stab_control_b-_j10.npz
ef260a1574b21d7fa0122648bead6af62c77e5036e6e5fe54bec8dda312aa812  runs/control/stability/stab_control_b-_j11.npz
233b7cc8e693faa95edb01fdd1516a43263dbbb60e96f3ace2e3996038c3cb35  runs/control/stability/stab_control_b-_j12.npz
af3b3890f93c9808b08a2af0369c7a346201102b96029c568b0893bbd8ce2e4d  runs/control/stability/stab_control_b-_j13.npz
4ebc038a48e2536cf7c937b16512c1417fd8abe27340a2ececceb9952e165d30  runs/control/stability/stab_control_b-_j14.npz
0dd8e30a64fc7a595e2f8659d9e005e598ed8c35ea2c4e8f4c7d46f106441227  runs/control/stability/stab_control_b-_j15.npz
aa5e5d9d7f7da72c1a803c6e58a5590363131c8ac12a9416b311594af9712bff  runs/control/stability/stab_control_b-_j16.npz
e4b8d2ef0ca43c5e8818b8fbf9d1f2e94643605d036eb279b37167261554d274  runs/control/stability/stab_control_b-_j17.npz
e6baf14ec95fb511adedca1abdf236365554e3d6613a6779d8a06c3ea5c88222  runs/control/stability/stab_control_b-_j18.npz
bfc8810ea37c31589773b790b85ea1315bcb1154100770eebc94c2c8446ae441  runs/control/stability/stab_control_b-_j19.npz
e0f9180380843f8d212ba3113ff839a3e2db56dac937b3b61d5882e55990a59b  runs/control/stability/stab_control_b-_j1.npz
99d9e9b4e2ca80028e64c6eab7967411ec36caae1ddaa85b6ba5f8cd42d9e895  runs/control/stability/stab_control_b-_j20.npz
c61378101bbc38178ebe05c81be0a5171cf2c599caa84cf98c744e0eae74f1e8  runs/control/stability/stab_control_b-_j21.npz
cd1cb9664b6b72376ffc9176ee6e8d475d287a5afc1769675696cd52514d17d6  runs/control/stability/stab_control_b-_j22.npz
14905540e1f8138b8394debaffc1015ab1fa23522b30b3c6e5ab97cadafb33b2  runs/control/stability/stab_control_b-_j23.npz
32c1145ecb97d23877d0b5e402be36897d05959abb0c71d3f46087128c59d787  runs/control/stability/stab_control_b-_j24.npz
30f6544bad3a4de78dd48463aa899244a01043ebd4e1f80b9dbbc19f861ba92b  runs/control/stability/stab_control_b-_j25.npz
1a1cf34846f7197d05b485b96d8383db9a915c2b3b426bf328320613d957257e  runs/control/stability/stab_control_b-_j26.npz
af079ba57d7fd05c3072a1ebfa8ce1b81879c30fc96396ef08cd96e5fa723e65  runs/control/stability/stab_control_b-_j27.npz
791803bb2a3a65a2322132f7258113d7a32c0c92506c6141c6f3e867d755ac6b  runs/control/stability/stab_control_b-_j28.npz
3adca9d3e35a89960da8963f2da65d5cd7ba21bd678c9f1687e4a12e506635d2  runs/control/stability/stab_control_b-_j29.npz
ae432bcd71e2ed336bf5b858eba7929ce0a21a9b87d7abf491ad7085815569d7  runs/control/stability/stab_control_b-_j2.npz
9104752c5f45631ec88beb43037e2279db2631ee167d13c75ed3b0ee09c865da  runs/control/stability/stab_control_b-_j30.npz
cff19627e1aed319fb0c4631bb34659ff840ce336dd26cbe5749fd2c940be1c9  runs/control/stability/stab_control_b-_j31.npz
c351dd2df43d3e6536cc5656b8ecdb20458482e7f7a591e28bc3137d50518171  runs/control/stability/stab_control_b-_j32.npz
a63ee3ff5be4a9ff84e68047221462d954647905f8e6688a8d5796f0662fed2e  runs/control/stability/stab_control_b-_j33.npz
59267633bbe80852cbd8d053991ffb14f4b56a8e1367fe9db12972c421d3ec74  runs/control/stability/stab_control_b-_j34.npz
bab7d6a48d29edf476772669f3d2b035660177247fb467dccc2dc750bce56158  runs/control/stability/stab_control_b-_j35.npz
bd2002c8fe1cac7cfcc85ac15617db5b5079e2dad1bfc0105592a878f2fab517  runs/control/stability/stab_control_b-_j36.npz
058607e6711651ab83d4c916640471d218a651de6862bcc9ad9996f79166d079  runs/control/stability/stab_control_b-_j37.npz
6e90c16537afe00ce930e4cb887d87aa89965869db9d5cf939269fd5f00d4c3f  runs/control/stability/stab_control_b-_j38.npz
7d84cbba44e3ad401f510d926f7e25b2863ba739a0bbc82913d811d1883d1c5c  runs/control/stability/stab_control_b-_j39.npz
432028e045a12f392fb325472addef0761a0281515c2683f6cc39373e74155ab  runs/control/stability/stab_control_b-_j3.npz
4266e950c76ea90f6603c65665c430711f239345b61b5e67387abfcd0398c1f9  runs/control/stability/stab_control_b-_j40.npz
5ae1d765420eaeff9177c552c6b12c73f4bd5a4f99402170e1e5e0fdb6ba6cd6  runs/control/stability/stab_control_b-_j41.npz
fb7a9bb5ba81dc7cb16b691d23d0d803fab0399e058e9928b19b549d2a5e4e67  runs/control/stability/stab_control_b-_j42.npz
16516e38bf5a09cfd1663397a293d747cc420d824b3b4eda30616d511070c418  runs/control/stability/stab_control_b-_j43.npz
5bca062994552d86a63756070369da195a580a88597e2a349c876a7070939769  runs/control/stability/stab_control_b-_j44.npz
b192c9f0572913b43c490912302027e975e14a45fd292eb343edf0fae7c70d40  runs/control/stability/stab_control_b-_j45.npz
2c247fc7a0448402cf4fd86156a884af33cff7c6dc4ece9683ed83ef8cf5c25a  runs/control/stability/stab_control_b-_j46.npz
b57b3de52cedc5721b537c7be6773681dd3188986e331e92fe4253ec818c6c92  runs/control/stability/stab_control_b-_j47.npz
dce4d13ca07d643a81dd4f2d2239815fc7c09df9f91cf44f49ac39c15275c11e  runs/control/stability/stab_control_b-_j48.npz
56794a85763ac7d757e0a500e806739d95152684d0ce91d0d1920e30401bab70  runs/control/stability/stab_control_b-_j49.npz
e191ce02b06fc06aaf6026518c9056be7dfba6c69b450f53a87df6d6cbd754e2  runs/control/stability/stab_control_b-_j4.npz
6fc0840b505661ad47f756f9f60dec2e7a7d02f24a621f2a047eb3da6a6f5583  runs/control/stability/stab_control_b-_j50.npz
48c80680ffec4b9d127a8a1e4924a065dbe4aa56de7f405696dc613a4ce7a596  runs/control/stability/stab_control_b-_j51.npz
47664358261fa44779f10ff329401c717fd1b6c4afd0a41318d37243a1b0e42f  runs/control/stability/stab_control_b-_j5.npz
04fd7b68babcd9d4fa9faf69a2a04693496a80f102140c17b9c84accf9ed9a5e  runs/control/stability/stab_control_b-_j6.npz
308581ad9890e00ff6af30504f33919a23f70107f3863375836cd17e6aab4c02  runs/control/stability/stab_control_b-_j7.npz
5aebce67f5dcd555f59602963b2de442374671750aed8d3e72c9d24bd83d76e8  runs/control/stability/stab_control_b-_j8.npz
3ebe77fa4973cf796f80a00bb60b27054d07fe73a45f8648428e0233ab6cfb86  runs/control/stability/stab_control_b-_j9.npz
f7871a93cba0db2923bbf36a5d7ea7d5cbece8c8b36af66630c2f3fd683fae43  runs/control/stability/stab_control_b-_j-.npz'
export BV96_LIST="$LIST"
n=$(printf '%s\n' "$LIST" | wc -l); echo "products listed: $n"; [ "$n" -eq 70 ] || { echo "STOP: the list is not 70 lines"; finish 9; }
PATHS=$(printf '%s\n' "$LIST" | awk '{print $2}')
for p in $PATHS; do [ -f "$OUT/$p" ] || { echo "STOP: $OUT/$p is not a file"; finish 5; }; done
echo "== 1. stat before $(ts)"
before=$(for p in $PATHS; do stat -c '%F|%i|%h|%s|%Y|%X|%Z|%n' "$OUT/$p"; done); echo "$before"
echo "== 2. read (O_NOATIME) $(ts)"
nice -n 19 env -u PYTHONPATH OMP_NUM_THREADS=1 "$PY" -I -B -c '
import base64, hashlib, io, os, sys
import numpy as np
out = sys.argv[1]
rows = [l.split() for l in os.environ["BV96_LIST"].splitlines() if l.strip()]
bundle, bad = {}, 0
for want, rel in rows:
    fd = os.open(os.path.join(out, rel), os.O_RDONLY | os.O_NOATIME)
    chunks = []
    while True:
        b = os.read(fd, 1 << 20)
        if not b:
            break
        chunks.append(b)
    os.close(fd)
    data = b"".join(chunks)
    got = hashlib.sha256(data).hexdigest()
    ok = got == want
    bad += not ok
    status = "OK" if ok else "MISMATCH"
    print(f"{rel} {len(data)} bytes sha256 {got} {status}")
    if ok:
        z = np.load(io.BytesIO(data), allow_pickle=False)
        key = rel.replace("runs/control/", "").replace("/", "__").removesuffix(".npz")
        bundle[key + "__xsec_flat"] = np.asarray(z["xsec_flat"])
        if "xtrue_flat" in z.files:
            bundle[key + "__xtrue_flat"] = np.asarray(z["xtrue_flat"])
        bundle[key + "__meta"] = np.asarray(str(z["meta"]))
if bad:
    print(f"STOP: {bad} products are not the committed files; nothing is printed")
    sys.exit(8)
buf = io.BytesIO()
np.savez_compressed(buf, **bundle)
data = buf.getvalue()
print(f"bundle: {len(bundle)} arrays, {len(data)} bytes, sha256 {hashlib.sha256(data).hexdigest()}")
print("== BEGIN bv96-o1 bundle base64")
enc = base64.b64encode(data).decode()
for i in range(0, len(enc), 76):
    print(enc[i:i + 76])
print("== END bv96-o1 bundle base64")
' "$OUT"
r=$?
echo "read rc=$r $(ts)"
echo "== 3. stat after $(ts)"
after=$(for p in $PATHS; do stat -c '%F|%i|%h|%s|%Y|%X|%Z|%n' "$OUT/$p"; done)
if [ "$before" = "$after" ]; then echo "stat: all 70 byte-identical before and after"; else echo "STOP: a file's stat moved during the read"; echo "-- after"; echo "$after"; finish 4; fi
[ "$r" -eq 0 ] || finish "$r"
finish 0
