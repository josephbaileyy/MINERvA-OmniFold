"""Checks of $U's O_NOATIME manifest against the committed pins (the director's rulings of 2026-11-16), then the HPSS list.
  1 per truth, the products digest made from the manifest exactly as ll5d_b.products_digest makes it (sorted names
    ll5d_<truth>_*.npz with role central/seed/block/stat; name then hex sha256) equals the null record's products_sha256;
  2 the 13 pilot extras' sha256 in bulk/evidence/extras-vs-pilot-r2.out.txt equal the manifest's;
  3 the four groups partition the files: null_roles (central/seed/block/stat), toys (toy), extras (every other product:
    clipmean and data_control, all among the 13 evidenced), sidecars (atime-*.json); no file unlisted or twice;
  4 the manifest read moved no atime.
Writes the kit's list (group<TAB>sha256<TAB>path, sorted by group then path) on PASS.
    python3 check_manifest.py u_manifest.raw.tsv extras-evidence.txt hpss_ll5d_u_list.tsv"""
import hashlib, sys
U = "/pscratch/sd/j/josephrb/ll5d-unfolds-r2"
NULL = {"g18": "c16e9ce045ed255dda49c8031ca6769cf4285d25fd8f5b3fe86d5a2f8d8508a9",
        "ar23": "b716657b59b0169d50cf5ea2283c353fb4f7b9228ba041d5b54d2c40af796b43"}
ROLES = ("central", "seed", "block", "stat")
man, ev, out = sys.argv[1:4]
rows = [l.rstrip("\n").split("\t") for l in open(man) if not l.startswith("#")]
tail = [l for l in open(man) if l.startswith("#")]
sha = {n: s for s, size, a0, a1, n in rows}
ok = True
moved = sum(a0 != a1 for s, size, a0, a1, n in rows)
print(f"4 manifest: {len(rows)} files, atime moved {moved} ({tail[-1].strip()})"); ok &= moved == 0
for t, want in NULL.items():
    h, k = hashlib.sha256(), 0
    for n in sorted(sha):
        if n.startswith(f"ll5d_{t}_") and n.endswith(".npz") and n.split("_")[2] in ROLES:
            h.update(n.encode()); h.update(sha[n].encode()); k += 1
    good = h.hexdigest() == want; ok &= good
    print(f"1 {t}: {k} null-role products, digest {h.hexdigest()} {'==' if good else '!='} null {want}")
evd = {}
for l in open(ev):
    p = l.split()
    if len(p) == 3 and p[0] == "MATCH":
        evd[p[2]] = p[1]
e_ok = len(evd) == 13 and all(sha.get(n) == s for n, s in evd.items()); ok &= e_ok
print(f"2 extras: {len(evd)} evidenced, all equal to the manifest: {e_ok}")
def group(n):
    if n.startswith("atime-") and n.endswith(".json"): return "sidecars"
    r = n.split("_")[2] if n.startswith("ll5d_") and n.endswith(".npz") else None
    if r in ROLES: return "null_roles"
    if r == "toy": return "toys"
    if n in evd: return "extras"
    return None
G = {}
for n in sha:
    G.setdefault(group(n), []).append(n)
counts = {g: len(v) for g, v in G.items()}
p_ok = None not in G and sum(counts.values()) == len(sha) == len(rows); ok &= p_ok
print(f"3 groups: {counts}; partition of all {len(sha)} files: {p_ok}")
if ok:
    with open(out, "w") as o:
        for g in ("null_roles", "toys", "extras", "sidecars"):
            for n in sorted(G[g]):
                o.write(f"{g}\t{sha[n]}\t{U}/{n}\n")
print("MANIFEST-CHECK", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
