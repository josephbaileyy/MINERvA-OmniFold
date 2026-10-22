"""Our FHC anatuples (ANATUPLE-SHA256.tsv) against the current release listing (xrdfs ls -l), per file by size."""
import collections, json, sys
S = sys.argv[1]
rel = {}
for l in open(f"{S}/dl-xrd/ls_MediumEnergy_FHC.txt"):
    p = l.split()
    if p and not p[0].startswith("d") and p[4].endswith(".root") and ("/StandardMC/" in p[4] or "/MediumEnergy_FHC/Data/" in p[4]):
        r = p[4].split("/OpenData/MediumEnergy_FHC/")[1]
        key = ("MC" if r.startswith("MC/") else "Data", r.split("/")[-2], r.split("/")[-1])
        rel[key] = int(p[3])
ours = {}
for i, l in enumerate(open(f"{S}/anatuple_manifest.tsv")):
    c = l.rstrip("\n").split("\t")
    if i == 0 or not c[3].split("/")[-1].startswith("MasterAnaDev_"): continue
    r = c[3]
    key = ("MC" if r.startswith("MC/") else "Data", r.split("/")[-2], r.split("/")[-1])
    ours[key] = int(c[1])
agg = collections.defaultdict(lambda: {"release_n": 0, "release_bytes": 0, "ours_n": 0, "ours_bytes": 0, "same_size": 0, "ours_not_in_release": 0})
for k, b in rel.items():
    a = agg[(k[0], k[1])]; a["release_n"] += 1; a["release_bytes"] += b
    if k in ours: a["same_size"] += ours[k] == b
for k, b in ours.items():
    a = agg[(k[0], k[1])]; a["ours_n"] += 1; a["ours_bytes"] += b
    if k not in rel: a["ours_not_in_release"] += 1
out = {f"{k[0]}/{k[1]}": v for k, v in sorted(agg.items())}
tot = {kind: {f: sum(v[f] for kk, v in agg.items() if kk[0] == kind) for f in ("release_n", "release_bytes", "ours_n", "ours_bytes", "same_size", "ours_not_in_release")} for kind in ("MC", "Data")}
json.dump({"per_playlist": out, "totals": tot}, open(f"{S}/fhc_compare.json", "w"), indent=1)
for k, v in out.items():
    print(k, v, "ratio %.4f" % (v["release_bytes"] / v["ours_bytes"]) if v["ours_bytes"] else "")
print(tot)
