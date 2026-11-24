"""PG's stat-only probe and novelty test (COVFIX-DECLARATION.md section 4.1), for a Perlmutter login node. Rev 3.

Run with no arguments by pg-probe-launch.py, as `env -i PATH=/usr/bin:/bin LC_ALL=C /usr/bin/python3.11 -I -S -B -`
with this file on stdin. Standard library only. Each step's rule:

0. Identity, before anything else: the host must be a Perlmutter login node (hostname login<NN>, /pscratch,
   /global/common and the CVMFS products tree present). Otherwise STOP with nothing read.
1. Product roots, before any content read: the CVMFS repository path must be on its own mount (or /cvmfs's) of a
   type that is not a node-local filesystem (/proc/mounts). Each product root's real path must lie beneath that
   repository path (so a repository path through a link admits nothing), on that mount, and be a directory. The
   verified real roots are the read boundary. Otherwise STOP.
2. Read boundary: every read resolves (realpath) beneath a verified root and is opened relative to that root's
   directory, without following a final link; files must be regular, listings directories. Otherwise the item is
   unresolved, a STOP.
3. Catalog: a tune's genie_xsec entry is
   - present: its exact qualifier is in both the directory listing and the UPS table's declared qualifiers; the table
     sets GENIE_XSEC_TUNE to the tune; gxspl-NUsmall.xml parses (expat, no DOCTYPE) with root
     <genie_xsec_spline_list> and exactly one top-level <genie_tune>, which names the tune; the README has exactly one
     version line, `version v<N_N_N> qualifier <Q>`, whose whole qualifier field is the tune's;
   - absent: the listing and the table were both read, neither has the qualifier, and no other entry names the tune
     (a listing name or a UPS qualifier containing it, or a UPS entry setting GENIE_XSEC_TUNE to it);
   - unresolved: anything else, including, for G18_02b_02_11b, any other entry naming it.
   Only a confirmed absence of 02b admits the 02a fallback.
4. Configuration, as GENIE v3_04_00 loads it (GENIE-MC/Generator tag R-3_04_00: XmlParserUtils GetXMLFilePath and
   GetXMLPathList; AlgConfigPool LoadMasterConfig, LoadAlgConfig and LoadGlobalParamLists; Algorithm FindConfig; TuneId
   CMCDirectory and TuneDirectory).
   - Any file is the FIRST of config/<CMC>/<tune>/, config/<CMC>/ and config/ that holds it. There is no merge. A
     directory counts as not holding the file only when lstat reports it absent, or its listing lacks the name; any
     other error is unresolved.
   - ModelConfiguration.xml's root must be <global_param_list>, and the active param_set is "Default" (GUSERPHYSOPT
     unset). The genie UPS table must not mention GXMLPATH, GXMLPATHS, GALGCONF or GUSERPHYSOPT.
   - XML is parsed structurally. A DOCTYPE, malformed XML, a duplicate parameter name in an active set, an empty value,
     a type other than alg, or a value that is not genie::<Class>[/<set>] is unresolved.
   - Every reference genie::<Class>/<set> that the probe uses, including each hybrid leaf, must resolve as GENIE's
     registry would: exactly one master_config.xml entry for genie::<Class> (root <genie_config>), its file on the
     search path (root <alg_conf>), and exactly one param_set named <set> in it. Otherwise unresolved, never novel.
   - A HybridXSecAlgorithm value is resolved one level: its set's DefaultXSecAlg and XSecAlg@Interaction=... entries
     (any other parameter is unresolved). The slot's class is DefaultXSecAlg's (the nuclear-target default), and the
     slot's branches are the default and every entry. Every effective value records its file, set and raw text.
5. Novelty: the spent pool is every class and branch of G18_10a_02_11b and AR23_20i_00_000. In each slot (CCQE,
   2p2h), every branch must agree on whether it is in the pool; any disagreement is a STOP for the director, decided
   before the tune-level rule. A tune is then novel if its CCQE class or its 2p2h class is outside the pool. Per slot:
   - u0 is G21_11b_00_000: present, resolved, as section 4.1 declares it (CCQE genie::HybridXSecAlgorithm/SuSAv2-QEL
     with default SuSAv2QELPXSec; 2p2h SuSAv2MECPXSec alone, shared with AR23_20i_00_000 only, the disclosed
     overlap), with agreeing branches, and novel. Agreement and novelty then put no CCQE branch in the pool;
   - u1 is G18_02b_02_11b when present. Its exclusion is a STOP; 02a is never considered then.
   - Only on 02b's confirmed absence, u1 is G18_02a_02_11b, when present, resolved, with agreeing branches and novel,
     and only if 02b's configuration also resolves and its classes and branches equal 02a's (section 4.1's premise).
   The overlap record lists, for each chosen class and branch, every spent tune that uses it in either slot.
6. Positive controls: the spent tunes must be present with F1's pinned digests and README lines
   (gen5d_v3.SPLINE_PINS), and must resolve to their classes at tag R-3_04_00 (SPENT_CLASSES). FD-F1-REPORT.md 1.3's
   "NievesSimoVacasMECPXSec" is the alphabetic prefix of R-3_04_00's NievesSimoVacasMECPXSec2016: a grep token, not
   the class.
7. gpg (section 4.2), with approved absolute executables only:
   - GNUPGHOME and HOME are a fresh mode-700 directory under /tmp, which must be a node-local mount (/proc/mounts),
     in a minimal environment.
   - Before any other gpg call, `gpgconf --list-dirs` must report that homedir, and a socket dir that is either inside
     it, or exactly gpg's own /run/user/<uid>/gnupg/d.<zbase32 of SHA-1(homedir), 120 bits> (GnuPG common/homedir.c)
     with /run/user/<uid>, its gnupg/ and d.* all real directories owned by the user, the last two mode 0700, on tmpfs.
     Every socket it reports must lie in that dir. Anything else is a STOP, and gpg is not run.
   - A synthetic round trip with the pinned flags must reproduce the payload, in an SKESK + SEIPD (MDC) message.
   - Flipping the last byte of the SEIPD packet must exit 2 with "encrypted message has been manipulated", and a
     wrong passphrase must exit 2 with "Bad session key". A signal or any other exit fails.
   - The probe's own agent is identified by `gpg-connect-agent --no-autostart 'getinfo pid'`, and must be gone after
     `gpgconf --kill gpg-agent` (exit 0). Then, success or not, a verified outside socket dir is removed with
     `gpgconf --remove-socketdir`, and an lstat must find that canonical path and the homedir absent. Nothing else is
     removed.
   - The passphrase is synthetic (secrets.token_hex(32)) and is never printed.

Exit 0 on GO, 3 on STOP. The last line is `PG-PROBE-RESULT <json>`.

MEASURES: the product's catalog and the tunes' configured model classes. CANNOT AUTHORIZE: generation or any choice
the declaration leaves to the director.
"""
import datetime
import hashlib
import json
import os
import re
import secrets
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
import xml.parsers.expat as expat

SCHEMA = "covfix-pg-probe/3"
CVMFS_REPO = "/cvmfs/larsoft.opensciencegrid.org"
PRODUCTS = CVMFS_REPO + "/products"
XSEC_PRODUCT = PRODUCTS + "/genie_xsec/v3_04_00"
GENIE_PRODUCT = PRODUCTS + "/genie/v3_04_00"
ROOTS = (XSEC_PRODUCT, GENIE_PRODUCT)
XSEC_ROOT = XSEC_PRODUCT + "/NULL"
XSEC_UPS = XSEC_PRODUCT + "/ups/genie_xsec.table"
GENIE_UPS = GENIE_PRODUCT + "/ups/genie.table"
GENIE_CONFIG = GENIE_PRODUCT + "/Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config"
GNUPG_PARENT = "/tmp"
RUN_USER = "/run/user"
GPG_BINS = {"gpg": ("/usr/bin/gpg", "/usr/bin/gpg2"), "gpgconf": ("/usr/bin/gpgconf",),
            "gpg-connect-agent": ("/usr/bin/gpg-connect-agent",)}
LOCAL_FS = ("tmpfs", "ext4", "xfs", "btrfs", "ext3")

SPENT = ("G18_10a_02_11b", "AR23_20i_00_000")
SLOT1 = "G21_11b_00_000"
SLOT2, SLOT2_FALLBACK = "G18_02b_02_11b", "G18_02a_02_11b"
ALL_TUNES = SPENT + (SLOT1, SLOT2, SLOT2_FALLBACK)

# F1's pins (gen5d_v3.SPLINE_PINS): gxspl-NUsmall.xml sha256, README sha256, the README's version line.
SPENT_PINS = {
    "G18_10a_02_11b": ("1b4b0b37fc8c11acbf00884a94d0a3bda519d9c458f2c916573ef3d673a3ee35",
                       "abfca258817a3f7d8169cdd2dbf9349a025ab38312435c718347598b53f16726",
                       "version v3_02_00 qualifier G1810a0211b:k250:e1000"),
    "AR23_20i_00_000": ("185d7d8a4674b5df445fcadea3d17232804390c8421d563aa402c6ee743a0bbb",
                        "744cba18f82cc5fe4805cd8be120e5f7e5f7b36f657f4cc9f2118e69c803bcb2",
                        "version v3_04_00 qualifier AR2320i00000:k250:e1000")}
# (CCQE class, 2p2h class) at GENIE-MC/Generator tag R-3_04_00, config/<CMC>/ModelConfiguration.xml, set Default.
SPENT_CLASSES = {"G18_10a_02_11b": ("NievesQELCCPXSec", "NievesSimoVacasMECPXSec2016"),
                 "AR23_20i_00_000": ("NievesQELCCPXSec", "SuSAv2MECPXSec")}
# Section 4.1's description of u0: "the SuSAv2 QE and 2p2h model", sharing AR23_20i_00_000's 2p2h (the disclosed
# overlap), with a CCQE that differs from both spent tunes'. At R-3_04_00 that is the hybrid below.
DECLARED = {SLOT1: {"ccqe_alg": ["HybridXSecAlgorithm", "SuSAv2-QEL"], "ccqe": "SuSAv2QELPXSec",
                    "2p2h_branches": ["SuSAv2MECPXSec"], "2p2h_users": ["AR23_20i_00_000"]}}
SLOTS = {"QEL-CC": "ccqe", "MEC-CC": "2p2h"}
KEY = "XSecModel@genie::EventGenerator/{}"
SEARCH_ENV = ("GXMLPATH", "GXMLPATHS", "GALGCONF", "GUSERPHYSOPT")
VERSION_LINE = re.compile(r"version\s+(v\d+_\d+_\d+)\s+qualifier\s+(\S+)")

ENCRYPT = ["--batch", "--yes", "--pinentry-mode", "loopback", "--passphrase-fd", "3", "--no-symkey-cache",
           "--symmetric", "--cipher-algo", "AES256", "--s2k-digest-algo", "SHA512", "--force-mdc"]
DECRYPT = ["--batch", "--pinentry-mode", "loopback", "--passphrase-fd", "3", "--no-symkey-cache", "--decrypt"]
TAMPER_TEXT = "encrypted message has been manipulated"
WRONG_TEXT = "Bad session key"
GPG_TIMEOUT_S = 120
O_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
O_DIRECTORY = getattr(os, "O_DIRECTORY", 0)


class Unresolved(Exception):
    """An input the probe cannot read under its rules, or cannot interpret without guessing."""


# ------------------------------------------------------------------------------------------------------ mounts, roots

def mount_entry(path, mounts_text):
    """(mount point, type, device) of the longest mount point containing path, from /proc/mounts' text."""
    best = ("", None, None)
    for ln in mounts_text.splitlines():
        f = ln.split()
        if len(f) >= 3:
            mp = f[1].replace("\\040", " ")
            if (path == mp or path.startswith(mp.rstrip("/") + "/")) and len(mp) >= len(best[0]):
                best = (mp, f[2], f[0])
    return best


def mount_fs(path, mounts_text):
    return mount_entry(path, mounts_text)[1]


def verify_roots(declared, repo, mounts_text):
    """(verified real roots, record). Each declared root must resolve beneath the repository, on its mount."""
    rec = {"repo": repo, "resolved": {}, "pass": False}
    mp, typ, dev = mount_entry(repo, mounts_text)
    rec["mount"] = {"point": mp, "type": typ, "device": dev}
    if mp not in (repo, os.path.dirname(repo)) or typ is None or typ in LOCAL_FS:
        raise Unresolved(f"{repo} is not on a CVMFS mount of its own: {mp} {typ}")
    out = []
    for r in declared:
        real = os.path.realpath(r)
        rec["resolved"][r] = real
        if not real.startswith(repo + "/"):
            raise Unresolved(f"{r} resolves to {real}, outside {repo}")
        if mount_entry(real, mounts_text)[0] != mp:
            raise Unresolved(f"{r} resolves onto another mount")
        try:
            if not stat.S_ISDIR(os.lstat(real).st_mode):
                raise Unresolved(f"{r} is not a directory")
        except OSError as e:
            raise Unresolved(f"{r}: {e.strerror}") from None
        out.append(real)
    rec["pass"] = True
    return tuple(out), rec


# ------------------------------------------------------------------------------------------------- the read boundary

def _beneath(path, roots):
    """(real path, the verified root it lies beneath)."""
    real = os.path.realpath(path)
    for rr in roots:
        if real == rr or real.startswith(rr.rstrip("/") + "/"):
            return real, rr
    raise Unresolved(f"{path} resolves outside the approved roots")


def _open_beneath(path, roots, flags):
    real, rr = _beneath(path, roots)
    try:
        rfd = os.open(rr, os.O_RDONLY | O_DIRECTORY | O_NOFOLLOW)
    except OSError as e:
        raise Unresolved(f"{rr}: {e.strerror}") from None
    try:
        return os.open(os.path.relpath(real, rr), flags | O_NOFOLLOW, dir_fd=rfd)
    except OSError as e:
        raise Unresolved(f"{path}: {e.strerror}") from None
    finally:
        os.close(rfd)


def _open_regular(path, roots):
    fd = _open_beneath(path, roots, os.O_RDONLY | os.O_NONBLOCK)
    if not stat.S_ISREG(os.fstat(fd).st_mode):
        os.close(fd)
        raise Unresolved(f"{path} is not a regular file")
    return fd


def read_file(path, roots):
    """Bytes of a regular file beneath a verified root, opened without following a final link."""
    fd = _open_regular(path, roots)
    try:
        return b"".join(iter(lambda: os.read(fd, 1 << 20), b""))
    finally:
        os.close(fd)


def list_dir(path, roots):
    fd = _open_beneath(path, roots, os.O_RDONLY | O_DIRECTORY)
    try:
        if not stat.S_ISDIR(os.fstat(fd).st_mode):
            raise Unresolved(f"{path} is not a directory")
        return sorted(os.listdir(fd))
    finally:
        os.close(fd)


def is_regular(path, roots):
    os.close(_open_regular(path, roots))
    return True


def _absent(path):
    """True when lstat reports nothing there; False when something is; Unresolved on any other error."""
    try:
        os.lstat(path)
        return False
    except FileNotFoundError:
        return True
    except OSError as e:
        raise Unresolved(f"{path}: {e.strerror}") from None


# ------------------------------------------------------------------------------------------------------- identity

def identity():
    host = socket.gethostname()
    checks = {"hostname login<NN>": bool(re.fullmatch(r"login\d{2}", host)),
              "/pscratch": os.path.isdir("/pscratch"), "/global/common": os.path.isdir("/global/common"),
              "CVMFS products": os.path.isdir(PRODUCTS)}
    return {"host": host, "checks": checks, "pass": all(checks.values())}


# ------------------------------------------------------------------------------------------------------- catalog

def qualifier(tune):
    """G18_10a_02_11b -> G1810a0211b-k250-e1000 (the genie_xsec directory convention, FD-F1-DECLARATION.md:76)."""
    return tune.replace("_", "") + "-k250-e1000"


def cmc(tune):
    """G18_10a_02_11b -> G18_10a (TuneId::CMC: prefix, year, '_', model id)."""
    return "_".join(tune.split("_")[:2])


def _key(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def ups_table(text):
    """{declared qualifier: GENIE_XSEC_TUNE or None} from a UPS table, in order of declaration."""
    out, cur = {}, None
    for ln in text.splitlines():
        m = re.search(r'Qualifiers\s*=\s*"([^"]*)"', ln)
        if m:
            cur = m.group(1)
            if cur in out:
                raise Unresolved(f"the UPS table declares {cur} twice")
            out[cur] = None
            continue
        m = re.search(r"envSet\s*\(\s*GENIE_XSEC_TUNE\s*,\s*([^)\s]+)\s*\)", ln)
        if m and cur is not None:
            if out[cur] is not None:
                raise Unresolved(f"the UPS table sets GENIE_XSEC_TUNE twice for {cur}")
            out[cur] = m.group(1)
    return out


def spline_scan(path, roots):
    """(sha256, bytes, root element, [top-level genie_tune names]) from one structural (expat) pass of the file."""
    fd = _open_regular(path, roots)
    h, size, st = hashlib.sha256(), 0, {"depth": 0, "root": None, "tunes": []}

    def start(name, attrs):
        if st["depth"] == 0:
            st["root"] = name
        elif st["depth"] == 1 and name == "genie_tune":
            st["tunes"].append(attrs.get("name"))
        st["depth"] += 1

    def end(name):
        st["depth"] -= 1

    def refuse(*a):
        raise Unresolved(f"{path}: a DOCTYPE or entity declaration")

    p = expat.ParserCreate()
    p.SetParamEntityParsing(expat.XML_PARAM_ENTITY_PARSING_NEVER)
    p.StartElementHandler, p.EndElementHandler = start, end
    p.StartDoctypeDeclHandler = p.EntityDeclHandler = refuse
    try:
        for b in iter(lambda: os.read(fd, 1 << 20), b""):
            h.update(b)
            size += len(b)
            p.Parse(b, False)
        if size:
            p.Parse(b"", True)
    except expat.ExpatError as e:
        raise Unresolved(f"{path}: malformed XML ({e})") from None
    finally:
        os.close(fd)
    return h.hexdigest(), size, st["root"], st["tunes"]


def catalog(xsec_root, ups, listing, tune, roots):
    q = qualifier(tune)
    qc = q.replace("-", ":")
    k = _key(tune)
    rec = {"qualifier": q, "status": None, "problems": [], "in_listing": q in listing, "in_ups": qc in ups,
           "ups_tune": ups.get(qc),
           "other_entries": sorted({n for n in listing if n != q and k in _key(n)}
                                   | {u for u, v in ups.items() if u != qc and (k in _key(u) or v == tune)})}
    if not rec["in_listing"] and not rec["in_ups"]:
        if rec["other_entries"]:
            rec["problems"].append(f"not under {q}, but other entries name it: {rec['other_entries']}")
            rec["status"] = "unresolved"
        else:
            rec["status"] = "absent"
        return rec
    if tune == SLOT2 and rec["other_entries"]:
        rec["problems"].append(f"other entries name it besides {q}: {rec['other_entries']}")
    if rec["in_listing"] != rec["in_ups"]:
        rec["problems"].append("the directory listing and the UPS table disagree")
    if rec["in_ups"] and rec["ups_tune"] != tune:
        rec["problems"].append(f"the UPS table sets GENIE_XSEC_TUNE={rec['ups_tune']}")
    d = os.path.join(xsec_root, q, "data")
    spl, readme = os.path.join(d, "gxspl-NUsmall.xml"), os.path.join(d, "README")
    try:
        rec["spline_sha256"], rec["spline_bytes"], rec["spline_root"], rec["spline_tunes"] = spline_scan(spl, roots)
        raw = read_file(readme, roots)
        rec["readme_sha256"] = hashlib.sha256(raw).hexdigest()
        rec["readme_version_lines"] = [ln.strip() for ln in raw.decode(errors="replace").splitlines()
                                       if ln.strip().startswith("version ")]
    except (Unresolved, OSError) as e:
        rec["problems"].append(f"unreadable entry: {e}")
    else:
        if rec["spline_root"] != "genie_xsec_spline_list" or rec["spline_tunes"] != [tune]:
            rec["problems"].append(f"the spline has root <{rec['spline_root']}> and tunes {rec['spline_tunes']}")
        lines = rec["readme_version_lines"]
        m = VERSION_LINE.fullmatch(lines[0]) if len(lines) == 1 else None
        if not m or m.group(2) != qc:
            rec["problems"].append(f"README version lines {lines}")
        else:
            rec["readme_version"] = m.group(1)
    rec["status"] = "unresolved" if rec["problems"] else "present"
    return rec


# ------------------------------------------------------------------------------------------------- configuration

def find_config(config_root, tune, name, roots):
    """GetXMLFilePath: the first of config/<CMC>/<tune>/, config/<CMC>/, config/ that holds name. A directory is
    passed over only when it is confirmed absent or its listing lacks name."""
    for d in (os.path.join(config_root, cmc(tune), tune), os.path.join(config_root, cmc(tune)), config_root):
        if _absent(d) or name not in list_dir(d, roots):
            continue
        p = os.path.join(d, name)
        is_regular(p, roots)
        return p
    raise Unresolved(f"no {name} on the search path for {tune}")


def parse_xml(path, roots):
    data = read_file(path, roots)
    if re.search(rb"<!DOCTYPE|<!ENTITY", data):
        raise Unresolved(f"{path}: a DOCTYPE or ENTITY declaration")
    try:
        return ET.fromstring(data)
    except ET.ParseError as e:
        raise Unresolved(f"{path}: malformed XML ({e})") from None


def _sets(root, set_name):
    return [s for s in root if s.tag == "param_set" and (s.get("name") or "").strip() == set_name]


def param_set(root, path, set_name):
    sets = _sets(root, set_name)
    if len(sets) != 1:
        raise Unresolved(f"{path}: {len(sets)} param_set named {set_name!r}")
    params = {}
    for p in sets[0]:
        if p.tag != "param":
            continue
        k = (p.get("name") or "").strip()
        if k in params:
            raise Unresolved(f"{path}: {k} twice in {set_name}")
        params[k] = ((p.get("type") or "").strip(), (p.text or "").strip())
    return params


def alg_value(typ, raw, where):
    """('Class', 'set') from an alg parameter's text, as AddBasicParameter splits it."""
    if typ != "alg":
        raise Unresolved(f"{where}: type {typ!r}, not alg")
    if not raw:
        raise Unresolved(f"{where}: empty value")
    parts = raw.split("/")
    if len(parts) not in (1, 2) or not re.fullmatch(r"genie::[A-Za-z_][A-Za-z0-9_]*", parts[0].strip()):
        raise Unresolved(f"{where}: {raw!r} is not genie::<Class>[/<set>]")
    conf = parts[1].strip() if len(parts) == 2 else "Default"
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", conf):
        raise Unresolved(f"{where}: set {conf!r}")
    return parts[0].strip().split("::", 1)[1], conf


def master_entries(config_root, tune, roots):
    """(master_config.xml's path, {alg: [file, ...]})."""
    mpath = find_config(config_root, tune, "master_config.xml", roots)
    mroot = parse_xml(mpath, roots)
    if mroot.tag != "genie_config":
        raise Unresolved(f"{mpath}: root <{mroot.tag}>")
    ents = {}
    for c in mroot:
        if c.tag == "config":
            ents.setdefault((c.get("alg") or "").strip(), []).append((c.text or "").strip())
    return mpath, ents


def resolve_ref(config_root, tune, cls, conf, master, roots):
    """(the parsed file, {class, set, file}) for genie::<cls>/<conf>, as GENIE's registry pool would find it."""
    files = master[1].get("genie::" + cls, [])
    if len(files) != 1 or not re.fullmatch(r"[A-Za-z0-9_.-]+\.xml", files[0]):
        raise Unresolved(f"{master[0]}: {len(files)} entries for genie::{cls}")
    path = find_config(config_root, tune, files[0], roots)
    root = parse_xml(path, roots)
    if root.tag != "alg_conf":
        raise Unresolved(f"{path}: root <{root.tag}>")
    n = len(_sets(root, conf))
    if n != 1:
        raise Unresolved(f"{path}: {n} param_set named {conf!r} for genie::{cls}")
    return root, {"class": cls, "set": conf, "file": path}


def resolve_hybrid(config_root, tune, conf, master, roots):
    """HybridXSecAlgorithm/<conf>: its resolved default and per-interaction algorithms."""
    hroot, href = resolve_ref(config_root, tune, "HybridXSecAlgorithm", conf, master, roots)
    hpath = href["file"]
    params = param_set(hroot, hpath, conf)
    if "DefaultXSecAlg" not in params:
        raise Unresolved(f"{hpath}: no DefaultXSecAlg in {conf}")
    default = resolve_ref(config_root, tune, *alg_value(*params["DefaultXSecAlg"], f"{hpath} {conf} DefaultXSecAlg"),
                          master, roots)[1]
    branches = []
    for k, v in params.items():
        if k.startswith("XSecAlg@Interaction="):
            ref = resolve_ref(config_root, tune, *alg_value(*v, f"{hpath} {conf} {k}"), master, roots)[1]
            branches.append(dict(ref, interaction=k))
        elif k != "DefaultXSecAlg":
            raise Unresolved(f"{hpath}: unexpected parameter {k} in {conf}")
    return {"file": hpath, "set": conf, "master_config": master[0], "default": default, "branches": branches}


def model_classes(config_root, genie_ups_text, tune, roots):
    rec = {"cmc": cmc(tune), "ccqe": None, "2p2h": None, "components": {}, "sources": {}, "problems": []}
    try:
        for v in SEARCH_ENV:
            if v in genie_ups_text:
                raise Unresolved(f"the genie UPS table mentions {v}")
        path = find_config(config_root, tune, "ModelConfiguration.xml", roots)
        rec["file"] = path
        root = parse_xml(path, roots)
        if root.tag != "global_param_list":
            raise Unresolved(f"{path}: root <{root.tag}>")
        params = param_set(root, path, "Default")
        master = master_entries(config_root, tune, roots)
        for key, slot in SLOTS.items():
            k = KEY.format(key)
            if k not in params:
                raise Unresolved(f"{path}: no {k} in Default")
            cls, conf = alg_value(*params[k], f"{path} {k}")
            src = {"file": path, "set": "Default", "raw": params[k][1], "alg": [cls, conf]}
            if cls == "HybridXSecAlgorithm":
                h = resolve_hybrid(config_root, tune, conf, master, roots)
                src["hybrid"] = h
                rec[slot] = h["default"]["class"]
                rec["components"][slot] = sorted({h["default"]["class"]} | {b["class"] for b in h["branches"]})
            else:
                src["registry"] = resolve_ref(config_root, tune, cls, conf, master, roots)[1]
                rec[slot], rec["components"][slot] = cls, [cls]
            rec["sources"][slot] = src
    except (Unresolved, OSError) as e:
        rec["problems"].append(str(e))
        rec["ccqe"] = rec["2p2h"] = None
        rec["components"] = {}
    return rec


def resolved(rec):
    return not rec["problems"] and rec["ccqe"] is not None and rec["2p2h"] is not None


# ------------------------------------------------------------------------------------------------------- decision

def decide(cat, cls, spent_pins=SPENT_PINS, spent_classes=SPENT_CLASSES):
    stops, controls = [], {}
    for t in SPENT:
        c, pin = cat[t], spent_pins[t]
        ok = (c["status"] == "present" and c.get("spline_sha256") == pin[0] and c.get("readme_sha256") == pin[1]
              and c.get("readme_version_lines") == [pin[2]])
        okc = resolved(cls[t]) and (cls[t]["ccqe"], cls[t]["2p2h"]) == spent_classes[t]
        controls[f"{t}: catalog equals F1's pins"] = ok
        controls[f"{t}: classes equal R-3_04_00's"] = okc
        if not ok:
            stops.append(f"control: {t}'s catalog is not F1's pins")
        if not okc:
            stops.append(f"control: {t}'s resolved classes are not R-3_04_00's")
    pool = sorted({x for t in SPENT if resolved(cls[t]) for s in SLOTS.values() for x in cls[t]["components"][s]})

    def users(x):
        return [u for u in SPENT if any(x in cls[u]["components"].get(s, []) for s in SLOTS.values())]

    def novelty(t):
        if not resolved(cls[t]):
            return None
        by_slot = {s: {x: x not in pool for x in cls[t]["components"][s]} for s in SLOTS.values()}
        agree = all(len(set(v.values())) == 1 for v in by_slot.values())
        return {"branches": by_slot, "branches_agree": agree,
                "novel": any(by_slot[s][cls[t][s]] for s in SLOTS.values()) if agree else None}

    def undeclared(t):
        d, c = DECLARED.get(t), cls[t]
        if d is None:
            return []
        out = []
        if c["sources"]["ccqe"]["alg"] != d["ccqe_alg"] or c["ccqe"] != d["ccqe"]:
            out.append(f"CCQE {c['sources']['ccqe']['alg']} with class {c['ccqe']}")
        if c["components"]["2p2h"] != d["2p2h_branches"] or users(c["2p2h"]) != d["2p2h_users"]:
            out.append(f"2p2h {c['components']['2p2h']} used by {users(c['2p2h'])}")
        return out

    nov = {t: novelty(t) for t in (SLOT1, SLOT2, SLOT2_FALLBACK)}

    def eligible(t):
        if cat[t]["status"] != "present":
            return f"not eligible: catalog {cat[t]['status']}"
        if nov[t] is None:
            return "not eligible: configuration unresolved"
        bad = undeclared(t)
        if bad:
            return f"not eligible: not section 4.1's configuration ({'; '.join(bad)})"
        if not nov[t]["branches_agree"]:
            return "not eligible: a slot's branches disagree on novelty (director's ruling)"
        return "eligible" if nov[t]["novel"] else "not eligible: both classes in the spent pool"

    elig = {SLOT1: eligible(SLOT1)}
    slot1 = SLOT1 if elig[SLOT1] == "eligible" else None
    if slot1 is None:
        stops.append(f"slot 1: {SLOT1} {elig[SLOT1]}")
    same_02 = None
    if resolved(cls[SLOT2]) and resolved(cls[SLOT2_FALLBACK]):
        same_02 = all(cls[SLOT2]["components"][s] == cls[SLOT2_FALLBACK]["components"][s] for s in SLOTS.values()) \
            and (cls[SLOT2]["ccqe"], cls[SLOT2]["2p2h"]) == (cls[SLOT2_FALLBACK]["ccqe"], cls[SLOT2_FALLBACK]["2p2h"])
    slot2, fallback = None, False
    st02b = cat[SLOT2]["status"]
    if st02b == "present":
        elig[SLOT2] = eligible(SLOT2)
        elig[SLOT2_FALLBACK] = "not considered: 02b is present"
        if elig[SLOT2] == "eligible":
            slot2 = SLOT2
        else:
            stops.append(f"slot 2: {SLOT2} {elig[SLOT2]} (02a substitutes only for 02b's absence)")
    elif st02b == "absent":
        elig[SLOT2] = "not eligible: confirmed absent"
        e = eligible(SLOT2_FALLBACK)
        if e == "eligible" and same_02 is not True:
            e = ("not eligible: its classes differ from 02b's, against section 4.1's premise" if same_02 is False
                 else "not eligible: 02b's configuration is unresolved, so section 4.1's premise cannot be checked")
        elig[SLOT2_FALLBACK] = e
        if e == "eligible":
            slot2, fallback = SLOT2_FALLBACK, True
        else:
            stops.append(f"slot 2: {SLOT2} absent, {SLOT2_FALLBACK} {e}")
    else:
        elig[SLOT2] = "not eligible: catalog unresolved"
        elig[SLOT2_FALLBACK] = "not considered: 02b's presence is unresolved"
        stops.append(f"slot 2: {SLOT2}'s catalog is unresolved; no fallback")
    overlap = {t: {x: users(x) for s in SLOTS.values() for x in cls[t]["components"][s]} for t in (slot1, slot2) if t}
    return {"spent_pool": pool, "novelty": nov, "eligibility": elig, "chosen": {"u0": slot1, "u1": slot2},
            "fallback_taken": fallback, "overlap_with_spent_pool": overlap, "02a_02b_same_classes": same_02,
            "controls": controls, "stops": stops}


# ------------------------------------------------------------------------------------------------------------ gpg

def _fd_open(fd):
    try:
        os.fstat(fd)
        return True
    except OSError:
        return False


def _run_gpg(gpg, args, passphrase, payload, env):
    """One gpg call with the passphrase on fd 3 and the payload on stdin: (rc, stdout, stderr lines)."""
    if _fd_open(3):
        raise RuntimeError("fd 3 is already open in the probe")
    r, w = os.pipe()
    try:
        if r != 3:
            os.dup2(r, 3)
            os.close(r)
            r = 3
        os.write(w, (passphrase + "\n").encode())
        os.close(w)
        w = None
        p = subprocess.run([gpg] + args, input=payload, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           pass_fds=(3,), env=env, timeout=GPG_TIMEOUT_S, cwd=env["GNUPGHOME"])
        return p.returncode, p.stdout, p.stderr.decode(errors="replace").splitlines()
    finally:
        os.close(r)
        if w is not None:
            os.close(w)


def _new_len(data, j):
    """(length, header bytes, partial?) of a new-format length at data[j]."""
    o = data[j]
    if o < 192:
        return o, 1, False
    if o < 224:
        return ((o - 192) << 8) + data[j + 1] + 192, 2, False
    if o == 255:
        return int.from_bytes(data[j + 1:j + 5], "big"), 5, False
    return 1 << (o & 0x1F), 1, True


def packets(data):
    """[(tag, header offset, [(segment offset, segment length)...])] of an OpenPGP message. New-format partial body
    lengths are followed to the final definite segment; an old-format indeterminate length is refused."""
    out, i = [], 0
    try:
        while i < len(data):
            h = data[i]
            if not h & 0x80:
                raise ValueError("not an OpenPGP packet header")
            segs = []
            if h & 0x40:
                tag, j = h & 0x3F, i + 1
                while True:
                    n, hl, partial = _new_len(data, j)
                    segs.append((j + hl, n))
                    j += hl + n
                    if not partial:
                        break
            else:
                tag, lt = (h >> 2) & 0x0F, h & 3
                if lt == 3:
                    raise ValueError("indeterminate length")
                nb = (1, 2, 4)[lt]
                n = int.from_bytes(data[i + 1:i + 1 + nb], "big")
                segs.append((i + 1 + nb, n))
                j = i + 1 + nb + n
            if j > len(data):
                raise ValueError("truncated packet")
            out.append((tag, i, segs))
            i = j
    except IndexError:
        raise ValueError("truncated packet") from None
    return out


def tamper_seipd(ct):
    """The ciphertext with the last byte of its SEIPD packet (inside the encrypted MDC) flipped."""
    pk = packets(ct)
    if [p[0] for p in pk] != [3, 18]:
        raise ValueError(f"packet tags {[p[0] for p in pk]}, not SKESK + SEIPD")
    segs = pk[1][2]
    if sum(n for _, n in segs) < 2 or not segs[0][1] or ct[segs[0][0]] != 1:
        raise ValueError("SEIPD is not version 1 (MDC)")
    last = [(o, n) for o, n in segs if n][-1]
    bad = bytearray(ct)
    bad[last[0] + last[1] - 1] ^= 0x01
    return bytes(bad)


ZB32 = "ybndrfg8ejkmcpqxot1uwisza345h769"


def zb32(data, bits=None):
    """GnuPG's zb32_encode (common/zb32.c): the first `bits` bits of data, 5 at a time, the last group zero-padded."""
    bits = 8 * len(data) if bits is None else bits
    s = "".join(f"{b:08b}" for b in data)[:bits]
    s += "0" * (-len(s) % 5)
    return "".join(ZB32[int(s[i:i + 5], 2)] for i in range(0, len(s), 5))


def socketdir_for(home, uid, base=RUN_USER):
    """gpg's socket dir for a non-default homedir (common/homedir.c, _gnupg_socketdir_internal)."""
    return f"{base}/{uid}/gnupg/d." + zb32(hashlib.sha1(home.encode()).digest(), 8 * 15)


def _inside(p, d):
    return (os.path.realpath(p) + "/").startswith(os.path.realpath(d).rstrip("/") + "/")


def _owned_dir(p, uid, private):
    st = os.lstat(p)
    return stat.S_ISDIR(st.st_mode) and st.st_uid == uid and not (private and st.st_mode & 0o077)


def check_sockets(dirs, home, uid, mounts_text, base=RUN_USER):
    """(confined, the verified socket dir if outside home else None, problems), from `gpgconf --list-dirs`."""
    h, sd = dirs.get("homedir", ""), dirs.get("socketdir", "")
    socks = {k: v for k, v in dirs.items() if k.endswith("-socket")}
    if not h or os.path.realpath(h) != home or not sd or "agent-socket" not in socks:
        return False, None, [f"homedir {h!r}, socketdir {sd!r}, sockets {sorted(socks)}"]
    probs, outside = [], None
    if _inside(sd, home):
        target = home
    else:
        want = socketdir_for(home, uid, base)
        if sd != want:
            return False, None, [f"socketdir {sd} is neither in the homedir nor gpg's {want}"]
        for p, private in ((f"{base}/{uid}", False), (f"{base}/{uid}/gnupg", True), (sd, True)):
            try:
                ok = _owned_dir(p, uid, private)
            except OSError:
                ok = False
            if not ok:
                probs.append(f"{p} is not a {'private ' if private else ''}directory of uid {uid}")
        if os.path.realpath(sd) != sd:
            probs.append(f"{sd} is not its own real path")
        if mount_fs(sd, mounts_text) != "tmpfs":
            probs.append(f"{sd} is on {mount_fs(sd, mounts_text)}, not tmpfs")
        target, outside = sd, sd
    probs += [f"{k} {v} is outside {target}" for k, v in sorted(socks.items()) if not _inside(v, target)]
    return not probs, (outside if not probs else None), probs


def _pid_alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _confirmed_absent(p):
    try:
        os.lstat(p)
        return False
    except FileNotFoundError:
        return True
    except OSError:
        return False


def _genv(home):
    return {"PATH": "/usr/bin:/bin", "HOME": home, "GNUPGHOME": home, "LC_ALL": "C", "LANG": "C"}


def _std_fds_open():
    """Reopen any closed fd 0-2 on /dev/null, so that no pipe end can land on 0-3 by accident."""
    reopened = []
    for fd in (0, 1, 2):
        if not _fd_open(fd):
            n = os.open(os.devnull, os.O_RDWR)
            if n != fd:
                os.dup2(n, fd)
                os.close(n)
            reopened.append(fd)
    return reopened


def gpg_check(bins=None, parent=GNUPG_PARENT, mounts_text=None, run_base=RUN_USER, uid=None):
    """Section 4.2's encryption-tool check, confined to a throwaway GNUPGHOME."""
    rec = {"pass": False, "std_fds_reopened": _std_fds_open()}
    uid = os.getuid() if uid is None else uid
    bins = bins or {k: next((p for p in v if os.path.isfile(p) and os.access(p, os.X_OK)), None)
                    for k, v in GPG_BINS.items()}
    rec["bins"] = bins
    if not all(bins.values()):
        rec["problem"] = "an approved gpg executable is missing"
        return rec
    if mounts_text is None:
        try:
            with open("/proc/mounts") as f:
                mounts_text = f.read()
        except OSError:
            rec["problem"] = "no /proc/mounts"
            return rec
    parent = os.path.realpath(parent)
    rec["parent"], rec["parent_fs"] = parent, mount_fs(parent, mounts_text)
    if rec["parent_fs"] not in LOCAL_FS:
        rec["problem"] = f"{parent} is on {rec['parent_fs']}, not a node-local filesystem"
        return rec
    home, agent_pid, outside, canonical = None, None, None, None
    try:
        home = os.path.realpath(tempfile.mkdtemp(prefix="pgprobe", dir=parent))
        os.chmod(home, 0o700)
        env = _genv(home)
        rec["gnupghome_mode"] = oct(os.stat(home).st_mode & 0o777)
        canonical = socketdir_for(home, uid, run_base)
        rec["canonical_socketdir"] = canonical
        ld = subprocess.run([bins["gpgconf"], "--list-dirs"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            env=env, timeout=30, cwd=home)
        d = {k: v.replace("%3a", ":").replace("%25", "%") for k, v in
             (ln.split(":", 1) for ln in ld.stdout.decode(errors="replace").splitlines() if ":" in ln)}
        rec["gpgconf_dirs"] = {k: v for k, v in d.items() if k in ("homedir", "socketdir") or k.endswith("-socket")}
        rec["confined"], outside, rec["socket_problems"] = check_sockets(d, home, uid, mounts_text, run_base)
        rec["confined"] = rec["confined"] and ld.returncode == 0
        rec["socketdir_outside_home"] = outside
        if not rec["confined"]:
            raise RuntimeError("the agent's sockets are not confined; gpg was not run")
        v = subprocess.run([bins["gpg"], "--version"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
                           timeout=30, cwd=home)
        rec["version"] = v.stdout.decode(errors="replace").splitlines()[:2]
        pw, payload = secrets.token_hex(32), os.urandom(1 << 16)
        rc_e, ct, err_e = _run_gpg(bins["gpg"], ENCRYPT, pw, payload, env)
        rec.update(encrypt_rc=rc_e, encrypt_stderr=err_e[-6:])
        if rc_e != 0:
            raise RuntimeError("encryption failed")
        rec["packet_tags"] = [p[0] for p in packets(ct)]
        bad = tamper_seipd(ct)
        rc_d, pt, err_d = _run_gpg(bins["gpg"], DECRYPT, pw, ct, env)
        rc_t, _, err_t = _run_gpg(bins["gpg"], DECRYPT, pw, bad, env)
        rc_w, _, err_w = _run_gpg(bins["gpg"], DECRYPT, secrets.token_hex(32), ct, env)
        rec.update(decrypt_rc=rc_d, round_trip_equal=hashlib.sha256(pt).digest() == hashlib.sha256(payload).digest(),
                   tampered={"rc": rc_t, "stderr": err_t[-6:], "evidence": any(TAMPER_TEXT in x for x in err_t)},
                   wrong_passphrase={"rc": rc_w, "stderr": err_w[-6:],
                                     "evidence": any(WRONG_TEXT in x for x in err_w)})
        a = subprocess.run([bins["gpg-connect-agent"], "--no-autostart", "getinfo pid", "/bye"],
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env, timeout=30, cwd=home)
        m = re.search(r"^D (\d+)$", a.stdout.decode(errors="replace"), re.M)
        agent_pid = int(m.group(1)) if m else None
        rec["agent_pid"] = agent_pid
        rec["pass"] = (rc_d == 0 and rec["round_trip_equal"] and rec["packet_tags"] == [3, 18]
                       and rc_t == 2 and rec["tampered"]["evidence"] and rc_w == 2
                       and rec["wrong_passphrase"]["evidence"])
    except (OSError, subprocess.SubprocessError, RuntimeError, ValueError) as e:
        rec["problem"] = f"{type(e).__name__}: {e}"
        rec["pass"] = False
    finally:
        if home:
            try:
                rec["gpgconf_kill_rc"] = subprocess.run([bins["gpgconf"], "--kill", "gpg-agent"], env=_genv(home),
                                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                                        timeout=30, cwd=home).returncode
            except (OSError, subprocess.SubprocessError) as e:
                rec["gpgconf_kill_rc"] = f"{type(e).__name__}: {e}"
            gone = False
            if agent_pid is not None:
                t0 = time.time()
                while _pid_alive(agent_pid) and time.time() - t0 < 10:
                    time.sleep(0.1)
                gone = not _pid_alive(agent_pid)
            rec["agent_gone"] = gone
            if outside:
                try:
                    rec["remove_socketdir_rc"] = subprocess.run(
                        [bins["gpgconf"], "--remove-socketdir"], env=_genv(home), stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL, timeout=30, cwd=home).returncode
                except (OSError, subprocess.SubprocessError) as e:
                    rec["remove_socketdir_rc"] = f"{type(e).__name__}: {e}"
            rec["socketdir_absent"] = _confirmed_absent(canonical) if canonical else False
            shutil.rmtree(home, ignore_errors=True)
            rec["gnupghome_removed"] = _confirmed_absent(home)
    rec["pass"] = bool(rec["pass"] and rec.get("confined") and rec.get("gnupghome_mode") == "0o700"
                       and rec.get("gpgconf_kill_rc") == 0
                       and rec.get("agent_gone")
                       and rec.get("socketdir_absent")
                       and rec.get("gnupghome_removed"))
    return rec


# ---------------------------------------------------------------------------------------------------------- probe

def _mounts():
    with open("/proc/mounts") as f:
        return f.read()


def probe(xsec_root=XSEC_ROOT, xsec_ups=XSEC_UPS, genie_ups=GENIE_UPS, config_root=GENIE_CONFIG, roots=ROOTS,
          ident=identity, gpg=gpg_check, spent_pins=SPENT_PINS, spent_classes=SPENT_CLASSES, repo=CVMFS_REPO,
          mounts=_mounts):
    rec = {"schema": SCHEMA, "start_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "roots": list(roots)}
    rec["identity"] = ident()
    if not rec["identity"]["pass"]:
        rec["stops"] = ["identity: not a Perlmutter login node; nothing was read"]
        rec["verdict"] = "STOP"
        return rec
    try:
        roots, rec["roots_verified"] = verify_roots(roots, repo, mounts())
    except (Unresolved, OSError) as e:
        rec["roots_verified"] = {"pass": False, "problem": str(e)}
        rec["stops"] = [f"roots: {e}"]
        rec["verdict"] = "STOP"
        return rec
    try:
        rec["qualifiers"] = list_dir(xsec_root, roots)
        ups = ups_table(read_file(xsec_ups, roots).decode(errors="replace"))
        rec["ups_declared"] = ups
        genie_ups_text = read_file(genie_ups, roots).decode(errors="replace")
        rec["genie_ups_search_env"] = [v for v in SEARCH_ENV if v in genie_ups_text]
    except (Unresolved, OSError) as e:
        rec["stops"] = [f"catalog: {e}"]
        rec["verdict"] = "STOP"
        return rec
    rec["catalog"] = {t: catalog(xsec_root, ups, rec["qualifiers"], t, roots) for t in ALL_TUNES}
    rec["classes"] = {t: model_classes(config_root, genie_ups_text, t, roots) for t in ALL_TUNES}
    rec["decision"] = decide(rec["catalog"], rec["classes"], spent_pins, spent_classes)
    rec["gpg"] = gpg()
    stops = list(rec["decision"]["stops"])
    if not rec["gpg"]["pass"]:
        stops.append("gpg: the tool or its pinned round trip failed")
    rec["stops"] = stops
    rec["verdict"] = "GO" if not stops else "STOP"
    rec["end_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return rec


def report(rec):
    p = print
    p(f"identity {rec['identity']}")
    for q in rec.get("qualifiers") or []:
        p(f"  qualifier {q}")
    for t in ALL_TUNES if "catalog" in rec else ():
        c, m = rec["catalog"][t], rec["classes"][t]
        p(f"{t}: catalog {c['status']} {c['problems']}")
        p(f"  CCQE {m['ccqe']}  2p2h {m['2p2h']}  components {m['components']}  problems {m['problems']}")
    if "decision" in rec:
        d = rec["decision"]
        p(f"eligibility {d['eligibility']}")
        p(f"chosen {d['chosen']} fallback_taken {d['fallback_taken']}")
    p(f"verdict {rec['verdict']}  stops {rec['stops']}")
    p("PG-PROBE-RESULT " + json.dumps(rec, sort_keys=True))


def main():
    rec = probe()
    report(rec)
    return 0 if rec["verdict"] == "GO" else 3


if __name__ == "__main__":
    sys.exit(main())
