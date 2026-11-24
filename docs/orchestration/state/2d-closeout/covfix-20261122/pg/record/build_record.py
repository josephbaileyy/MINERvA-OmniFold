"""Build PG's offline record (PG-RECORD.json, PG-RECORD.md) from public GENIE v3_04_00 files. Offline only.

The probe on the node does not interpret anything. It checks that the node's files are byte-identical to the pins
here, and this record carries the interpretation: which files define each tune's CCQE and 2p2h, the classes they
resolve to, and the novelty verdict against the spent tunes.

Inputs, all public, each given as a directory holding the extracted product tree:
  --genie   genie/v3_04_00 from SciSoft's genie-3.04.00-sl7-x86_64-e20-prof.tar.bz2 (the CVMFS build's layout);
  --xsec    genie_xsec/v3_04_00/NULL from SciSoft's genie_xsec-3.04.00-noarch-<Q>-k250-e1000.tar.bz2 tarballs;
  --github  raw copies of the same config files from GENIE-MC/Generator at tag R-3_04_00, named by their path under
            config/ with "/" replaced by "__" (a cross-check only);
  --tree    the tag's git tree (api.github.com/repos/GENIE-MC/Generator/git/trees/R-3_04_00?recursive=1), for each
            class's source file;
  --sources a JSON file naming each input tarball and its sha256, copied into the record.
Run: python3 -I build_record.py --genie G --xsec X --github H --tree T --sources S --out DIR

Resolution rules, as GENIE v3_04_00 applies them (R-3_04_00: XmlParserUtils GetXMLFilePath, AlgConfigPool,
Algorithm::FindConfig):
- any file is the first of config/<CMC>/<tune>/, config/<CMC>/ and config/ that holds it;
- ModelConfiguration.xml's param_set "Default" gives XSecModel@genie::EventGenerator/QEL-CC and /MEC-CC, which
  EventGenerator.xml's QEL-CC and MEC-CC threads take when they set no XSecModel of their own (checked);
- genie::<Class>/<set> needs exactly one master_config.xml entry, its file (root <alg_conf>), and exactly one
  param_set of that name;
- HybridXSecAlgorithm/<set> is resolved one level, to DefaultXSecAlg and XSecAlg@Interaction=... entries, and a
  nested hybrid is refused;
- novelty: the pool is every class and branch of the spent tunes. Within a slot all branches must agree, and a tune
  is novel if its CCQE or 2p2h class is outside the pool.
Any departure raises, so the record is either complete or not written.
"""
import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import xml.etree.ElementTree as ET

FLAVOR = "Linux64bit+3.10-2.17-e20-prof"
CONFIG = FLAVOR + "/GENIE-Generator/config"
SPENT = ("G18_10a_02_11b", "AR23_20i_00_000")
CANDIDATES = ("G21_11b_00_000", "G18_02b_02_11b", "G18_02a_02_11b", "G21_11a_00_000", "G18_02a_00_000")
SLOTS = {"QEL-CC": "ccqe", "MEC-CC": "2p2h"}
KEY = "XSecModel@genie::EventGenerator/{}"


class RecordError(Exception):
    pass


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def cmc(t):
    return "_".join(t.split("_")[:2])


def qualifier(t):
    return t.replace("_", "") + "-k250-e1000"


def listing(d):
    """Sorted entry names, a directory marked with a trailing '/', or None if d does not exist."""
    if not os.path.lexists(d):
        return None
    out = []
    for n in sorted(os.listdir(d)):
        m = os.lstat(os.path.join(d, n)).st_mode
        if stat.S_ISLNK(m):
            raise RecordError(f"{d}/{n} is a link")
        out.append(n + "/" if stat.S_ISDIR(m) else n)
    return out


class Tune:
    def __init__(self, genie, name):
        self.genie, self.name = genie, name
        self.dirs = [f"{CONFIG}/{cmc(name)}/{name}", f"{CONFIG}/{cmc(name)}", CONFIG]
        self.used = {}

    def find(self, fname):
        for d in self.dirs:
            p = f"{d}/{fname}"
            if os.path.isfile(os.path.join(self.genie, p)):
                self.used[p] = sha256(os.path.join(self.genie, p))
                return p
        raise RecordError(f"{self.name}: no {fname}")

    def xml(self, rel):
        data = open(os.path.join(self.genie, rel), "rb").read()
        if re.search(rb"<!DOCTYPE|<!ENTITY", data):
            raise RecordError(f"{rel}: DOCTYPE")
        return ET.fromstring(data)

    @staticmethod
    def sets(root, name):
        return [s for s in root if s.tag == "param_set" and (s.get("name") or "").strip() == name]

    def params(self, root, rel, name):
        ss = self.sets(root, name)
        if len(ss) != 1:
            raise RecordError(f"{rel}: {len(ss)} param_set {name!r}")
        out = {}
        for p in ss[0]:
            if p.tag == "param":
                k = (p.get("name") or "").strip()
                if k in out:
                    raise RecordError(f"{rel}: {k} twice")
                out[k] = ((p.get("type") or "").strip(), (p.text or "").strip())
        return out

    @staticmethod
    def alg(v, where):
        typ, raw = v
        m = re.fullmatch(r"genie::([A-Za-z_][A-Za-z0-9_]*)(?:/([A-Za-z0-9_.-]+))?", raw)
        if typ != "alg" or not m:
            raise RecordError(f"{where}: {v}")
        return m.group(1), m.group(2) or "Default"

    def ref(self, cls, conf):
        mrel = self.find("master_config.xml")
        mroot = self.xml(mrel)
        if mroot.tag != "genie_config":
            raise RecordError(f"{mrel}: root {mroot.tag}")
        files = [(c.text or "").strip() for c in mroot if c.tag == "config" and (c.get("alg") or "").strip() == f"genie::{cls}"]
        if len(files) != 1:
            raise RecordError(f"{mrel}: {len(files)} entries for {cls}")
        rel = self.find(files[0])
        root = self.xml(rel)
        if root.tag != "alg_conf" or len(self.sets(root, conf)) != 1:
            raise RecordError(f"{rel}: root {root.tag}, set {conf}")
        return root, {"class": cls, "set": conf, "file": rel, "master_config_entry": files[0]}

    def resolve(self):
        rec = {"tune": self.name, "cmc": cmc(self.name), "search_dirs": self.dirs}
        mrel = self.find("ModelConfiguration.xml")
        root = self.xml(mrel)
        if root.tag != "global_param_list":
            raise RecordError(f"{mrel}: root {root.tag}")
        gpl = self.params(root, mrel, "Default")
        erel = self.find("EventGenerator.xml")
        eroot = self.xml(erel)
        trel = self.find("TuneGeneratorList.xml")
        tl = self.params(self.xml(trel), trel, "Default")
        rec["model_configuration"], rec["event_generator"], rec["tune_generator_list"] = mrel, erel, trel
        rec["hadron_transport"] = gpl["HadronTransp-Model"][1]           # for the declaration's FSI-twin rule
        for thread, slot in SLOTS.items():
            ep = self.params(eroot, erel, thread)
            if "XSecModel" in ep:
                raise RecordError(f"{erel}: {thread} sets its own XSecModel")
            if f"genie::EventGenerator/{thread}" not in [v[1] for k, v in tl.items() if k.startswith("Generator-")]:
                raise RecordError(f"{trel}: {thread} not enabled")
            raw = gpl[KEY.format(thread)]
            cls, conf = self.alg(raw, f"{mrel} {thread}")
            s = {"raw": raw[1], "alg": [cls, conf]}
            if cls == "HybridXSecAlgorithm":
                hroot, href = self.ref(cls, conf)
                hp = self.params(hroot, href["file"], conf)
                leaves = []
                for k, v in hp.items():
                    if k != "DefaultXSecAlg" and not k.startswith("XSecAlg@Interaction="):
                        raise RecordError(f"{href['file']}: {k}")
                    lc, lconf = self.alg(v, f"{href['file']} {k}")
                    if lc == "HybridXSecAlgorithm":
                        raise RecordError(f"{href['file']}: nested hybrid at {k}")
                    leaves.append(dict(self.ref(lc, lconf)[1], role=k))
                default = [x for x in leaves if x["role"] == "DefaultXSecAlg"]
                if len(default) != 1:
                    raise RecordError(f"{href['file']}: no DefaultXSecAlg")
                s.update(hybrid=href, leaves=leaves)
                s["class"], s["branches"] = default[0]["class"], sorted({x["class"] for x in leaves})
            else:
                s["registry"] = self.ref(cls, conf)[1]
                s["class"], s["branches"] = cls, [cls]
            rec[slot] = s
        cdir, tdir = f"{CONFIG}/{cmc(self.name)}", f"{CONFIG}/{cmc(self.name)}/{self.name}"
        rec["listings"] = {cdir: listing(os.path.join(self.genie, cdir)), tdir: listing(os.path.join(self.genie, tdir))}
        for d, names in rec["listings"].items():
            for n in names or []:
                if not n.endswith("/"):
                    self.used.setdefault(f"{d}/{n}", sha256(os.path.join(self.genie, d, n)))
        rec["files"] = dict(sorted(self.used.items()))
        return rec


def novelty(recs):
    pool = sorted({x for t in SPENT for s in SLOTS.values() for x in recs[t][s]["branches"]})
    out = {}
    for t in CANDIDATES:
        by = {s: {x: x not in pool for x in recs[t][s]["branches"]} for s in SLOTS.values()}
        agree = all(len(set(v.values())) == 1 for v in by.values())
        novel = any(by[s][recs[t][s]["class"]] for s in SLOTS.values())
        users = {x: [u for u in SPENT if any(x in recs[u][s]["branches"] for s in SLOTS.values())]
                 for s in SLOTS.values() for x in recs[t][s]["branches"]}
        out[t] = {"branches_novel": by, "branches_agree": agree, "novel": novel and agree,
                  "overlap_with_spent": users}
    return pool, out


def libraries(genie, classes):
    """Each class's library from the build's .rootmap files, the link and its target, and the constructor symbol."""
    lib = os.path.join(genie, FLAVOR, "lib")
    owner = {}
    for rm in sorted(n for n in os.listdir(lib) if n.endswith(".rootmap")):
        cur = None
        for ln in open(os.path.join(lib, rm)):
            m = re.match(r"\[\s*(\S+)\s*\]", ln)
            if m:
                cur = m.group(1)
            m = re.match(r"class\s+genie::(\w+)\s*$", ln)
            if m and m.group(1) in classes:
                owner.setdefault(m.group(1), set()).add((rm, cur))
    out, pins, links = {}, {}, {}
    for c in sorted(classes):
        if len(owner.get(c, ())) != 1:
            raise RecordError(f"{c}: rootmap owners {owner.get(c)}")
        rm, so = next(iter(owner[c]))
        link = os.path.join(lib, so)
        if not os.path.islink(link):
            raise RecordError(f"{so} is not a link")
        target = os.readlink(link)
        if "/" in target:
            raise RecordError(f"{so} -> {target}")
        syms = subprocess.run(["nm", "-D", "--defined-only", os.path.join(lib, target)], capture_output=True,
                              text=True, check=True).stdout
        ctor = [f"_ZN5genie{len(c)}{c}C1Ev", f"_ZN5genie{len(c)}{c}C2Ev"]
        found = [s for s in ctor if re.search(rf"\b{s}\b", syms)]
        if not found:
            raise RecordError(f"{c}: no default constructor in {target}")
        pcm = so[:-3] + "_rdict.pcm"
        for n in (rm, target, pcm):
            pins[f"{FLAVOR}/lib/{n}"] = sha256(os.path.join(lib, n))
        links[f"{FLAVOR}/lib/{so}"] = target
        out[c] = {"rootmap": rm, "library": so, "target": target, "constructor_symbols": found}
    return out, pins, links


def splines(xsec, tunes):
    out = {}
    for t in tunes:
        d = os.path.join(xsec, qualifier(t))
        if not os.path.isdir(d):
            out[t] = {"published": False}
            continue
        readme = open(os.path.join(d, "data", "README"), "rb").read().decode()
        lines = [ln.strip() for ln in readme.splitlines() if ln.strip().startswith("version ")]
        table = open(os.path.join(d, "ups", "genie_xsec.table")).read()
        out[t] = {"published": True, "qualifier": qualifier(t),
                  "spline": f"NULL/{qualifier(t)}/data/gxspl-NUsmall.xml",
                  "spline_sha256": sha256(os.path.join(d, "data", "gxspl-NUsmall.xml")),
                  "readme_sha256": sha256(os.path.join(d, "data", "README")), "readme_version_lines": lines,
                  "ups_table_sha256": sha256(os.path.join(d, "ups", "genie_xsec.table")),
                  "ups_table_genie_xsec_tune": re.findall(r'envSet\s*\(\s*GENIE_XSEC_TUNE\s*,\s*"?([^)\s"]+)"?\s*\)', table)}
    return out


def main():
    a = argparse.ArgumentParser()
    for k in ("genie", "xsec", "github", "tree", "sources", "out"):
        a.add_argument("--" + k, required=True)
    o = a.parse_args()
    recs = {t: Tune(o.genie, t).resolve() for t in SPENT + CANDIDATES}
    for t in SPENT:
        recs[t]["role"] = "spent"
    for t in CANDIDATES:
        recs[t]["role"] = "candidate"
    pool, nov = novelty(recs)
    classes = {x for r in recs.values() for s in SLOTS.values() for x in r[s]["branches"] + [r[s]["alg"][0]]}
    libs, lib_pins, lib_links = libraries(o.genie, classes)
    tree = {x["path"] for x in json.load(open(o.tree))["tree"]}
    src = {}
    for c in sorted(classes):
        hits = sorted(p for p in tree if p.startswith("src/") and p.endswith(f"/{c}.cxx"))
        if len(hits) != 1:
            raise RecordError(f"{c}: source {hits}")
        src[c] = hits[0]
    config_pins = {}
    for r in recs.values():
        config_pins.update(r["files"])
    github = {}
    for p, h in sorted(config_pins.items()):
        g = os.path.join(o.github, p[len(CONFIG) + 1:].replace("/", "__"))
        github[p] = (sha256(g) == h) if os.path.isfile(g) else None
    rec = {"schema": "covfix-pg-record/1", "sources": json.load(open(o.sources)),
           "genie_root": "/cvmfs/larsoft.opensciencegrid.org/products/genie/v3_04_00",
           "xsec_root": "/cvmfs/larsoft.opensciencegrid.org/products/genie_xsec/v3_04_00",
           "tunes": recs, "spent_pool": pool, "novelty": nov, "classes": libs, "class_sources_at_tag": src,
           "pins": {"files": dict(sorted({**config_pins, **lib_pins,
                                          "ups/genie.table": sha256(os.path.join(o.genie, "ups", "genie.table"))}.items())),
                    "links": lib_links,
                    "listings": {d: v for r in recs.values() for d, v in r["listings"].items()}},
           "github_tag_equal": github, "splines": splines(o.xsec, SPENT + CANDIDATES)}
    os.makedirs(o.out, exist_ok=True)
    with open(os.path.join(o.out, "PG-RECORD.json"), "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
        f.write("\n")
    with open(os.path.join(o.out, "PG-RECORD.md"), "w") as f:
        f.write(markdown(rec))


def markdown(r):
    L = ["# PG offline record: GENIE v3_04_00 model classes, novelty and pins", "",
         "Generated by `build_record.py` from public files only. The numbers are in `PG-RECORD.json`; this page shows",
         "the same content for reading.", "", "## Method", "",
         "- The GENIE tree is SciSoft's build at CVMFS's path layout. Every pinned config file is also compared with",
         "  GENIE-MC/Generator's tag R-3_04_00 (`github_tag_equal`).",
         "- Resolution follows R-3_04_00's loader: the first of config/<CMC>/<tune>/, config/<CMC>/ and config/;",
         "  ModelConfiguration's set `Default`; each genie::<Class>/<set> through exactly one master_config.xml entry,",
         "  its file and exactly one param_set; hybrids resolved one level, a nested hybrid refused. The QEL-CC and MEC-CC",
         "  threads must be in TuneGeneratorList and must not set their own XSecModel in EventGenerator.xml.",
         "- Novelty: the pool is every class and branch of the spent tunes. All branches in a slot must agree, and a tune",
         "  is novel if its CCQE or 2p2h class is outside the pool.",
         "- Instantiability: each class must be listed in exactly one of the build's .rootmap files, with a defined",
         "  default constructor (`nm -D`) in that library's target. The .so target, its .rootmap and _rdict.pcm are pinned,",
         "  and the .so link by its target.",
         "- The probe pins: every file in each tune's CMC and tune directories, each config/ file the resolution used,",
         "  the listings of those directories (absent when there is none), the libraries and ups/genie.table.",
         "- Limits: the record covers the CCQE and 2p2h classes only; other models are outside §4.1's test. SciSoft is",
         "  not CVMFS. The node's bytes are checked against these pins, and the qualifier listing is the node's own.",
         "", "## Sources", ""]
    L += [f"- `{k}`: sha256 `{v}`" for k, v in sorted(r["sources"].items())]
    L += ["", "## Classes per tune", "", "| tune | role | CCQE (raw) | CCQE class | CCQE branches | 2p2h (raw) | 2p2h class |",
          "|---|---|---|---|---|---|---|"]
    for t, x in r["tunes"].items():
        L.append(f"| {t} | {x['role']} | `{x['ccqe']['raw']}` | {x['ccqe']['class']} | {', '.join(x['ccqe']['branches'])} "
                 f"| `{x['2p2h']['raw']}` | {x['2p2h']['class']} |")
    L += ["", "Intranuclear transport (ModelConfiguration's `HadronTransp-Model`, for the FSI-twin rule): "
          + "; ".join(f"{t} `{x['hadron_transport']}`" for t, x in r["tunes"].items()) + ".",
          "", f"Spent pool: {', '.join(r['spent_pool'])}.", "", "## Novelty", "",
          "| tune | novel | branches agree | CCQE branches novel | 2p2h branches novel | shared with spent |", "|---|---|---|---|---|---|"]
    for t, n in r["novelty"].items():
        sh = "; ".join(f"{k}: {', '.join(v)}" for k, v in n["overlap_with_spent"].items() if v) or "none"
        L.append(f"| {t} | {n['novel']} | {n['branches_agree']} | {n['branches_novel']['ccqe']} | "
                 f"{n['branches_novel']['2p2h']} | {sh} |")
    L += ["", "## Files that define each tune's models", ""]
    for t, x in r["tunes"].items():
        L.append(f"- **{t}**: ModelConfiguration `{x['model_configuration']}`; EventGenerator `{x['event_generator']}`; "
                 f"TuneGeneratorList `{x['tune_generator_list']}`.")
        for s in ("ccqe", "2p2h"):
            y = x[s]
            if "hybrid" in y:
                L.append(f"  - {s}: hybrid `{y['hybrid']['file']}` set `{y['hybrid']['set']}`; leaves "
                         + "; ".join(f"{z['role']} → {z['class']}/{z['set']} (`{z['file']}`)" for z in y["leaves"]))
            else:
                L.append(f"  - {s}: {y['registry']['class']}/{y['registry']['set']} (`{y['registry']['file']}`)")
    L += ["", "## Classes in the build", "", "| class | rootmap | library → target | constructor | source at R-3_04_00 |",
          "|---|---|---|---|---|"]
    for c, x in r["classes"].items():
        L.append(f"| {c} | {x['rootmap']} | {x['library']} → {x['target']} | {', '.join(x['constructor_symbols'])} | "
                 f"`{r['class_sources_at_tag'][c]}` |")
    L += ["", "## Splines (SciSoft genie_xsec v3_04_00)", "", "| tune | published | spline sha256 | README sha256 | README version lines | table's GENIE_XSEC_TUNE |",
          "|---|---|---|---|---|---|"]
    for t, s in r["splines"].items():
        if s["published"]:
            L.append(f"| {t} | yes | `{s['spline_sha256']}` | `{s['readme_sha256']}` | {s['readme_version_lines']} | "
                     f"{s['ups_table_genie_xsec_tune']} |")
        else:
            L.append(f"| {t} | no | | | | |")
    eq = r["github_tag_equal"]
    L += ["", "## Pins", "", f"{len(r['pins']['files'])} files by sha256, {len(r['pins']['links'])} links by target, and "
          f"{len(r['pins']['listings'])} directory listings, relative to `genie_root`. Of the {len(eq)} config files, "
          f"{sum(v is True for v in eq.values())} equal the GitHub tag's bytes, {sum(v is False for v in eq.values())} "
          f"differ and {sum(v is None for v in eq.values())} were not fetched.", ""]
    L += [f"- `{p}` `{h}`" for p, h in r["pins"]["files"].items()]
    L += [f"- link `{p}` → `{t}`" for p, t in r["pins"]["links"].items()]
    L += [f"- listing `{d}`: {v if v is not None else 'absent'}" for d, v in r["pins"]["listings"].items()]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
