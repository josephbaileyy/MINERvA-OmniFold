import collections, glob, json, os, re, sys
S = sys.argv[1]
rows = []
for f in glob.glob(f"{S}/dl-xrd/ls_Medium*.txt"):
    for l in open(f):
        p = l.split()
        if not p or p[0].startswith("d"): continue
        rows.append((p[1] + " " + p[2], int(p[3]), p[4]))
by = collections.defaultdict(list)
for t, sz, path in rows:
    rel = path.split("/OpenData/")[1]
    by["/".join(rel.split("/")[:-1])].append((t, sz, rel))
lists = {}
for f in glob.glob(f"{S}/dl-lists/MediumEnergy_*Playlist*.txt"):
    lists[os.path.basename(f)] = {l.strip().split("/OpenData/")[1] for l in open(f) if "root://" in l}
out = {}
for d, v in sorted(by.items()):
    names = {r for _, _, r in v}
    ts = sorted(t for t, _, _ in v)
    ext = collections.Counter(os.path.splitext(r)[1] for r in names)
    out[d] = {"n": len(v), "bytes": sum(s for _, s, _ in v), "mtime_min": ts[0], "mtime_max": ts[-1], "ext": dict(ext),
              "min_size": min(s for _, s, _ in v), "max_size": max(s for _, s, _ in v)}
# match playlist lists to directories
for k, names in sorted(lists.items()):
    m = re.match(r"MediumEnergy_(FHC|RHC)_(Data|StandardMC)_Playlist(\w+?)(_Water\w+)?\.txt", k)
    mode, kind, pl, wat = m.groups()
    d = f"MediumEnergy_{mode}/{'Data' if kind=='Data' else 'MC/StandardMC'}/Playlist{pl}"
    have = {r for _, _, r in by.get(d, [])}
    out.setdefault("_lists", {})[k] = {"dir": d, "n_list": len(names), "in_dir": len(names & have), "dir_not_in_list": len(have - names) if not wat else None,
                                       "bytes": sum(s for _, s, r in by.get(d, []) if r in names)}
json.dump(out, open(f"{S}/release_inventory.json", "w"), indent=1)
for d, r in out.items():
    if d == "_lists": continue
    print(f"{d:55s} {r['n']:5d} {r['bytes']/1e12:8.3f} TB  {r['mtime_min'][:10]}..{r['mtime_max'][:10]} {r['ext']} size {r['min_size']/1e9:.2f}-{r['max_size']/1e9:.2f} GB")
print()
for k, r in out["_lists"].items():
    if r["in_dir"] != r["n_list"] or r["dir_not_in_list"]: print("MISMATCH", k, r)
print("lists checked", len(out["_lists"]))
