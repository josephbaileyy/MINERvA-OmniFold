"""PG's probe (COVFIX-DECLARATION.md section 4.1, rev 12), for a Perlmutter login node. Rev 4: verify, don't interpret.

Run with no arguments by pg-probe-launch.py, as `env -i PATH=/usr/bin:/bin LC_ALL=C /usr/bin/python3.11 -I -S -B -`
with this file on stdin. Standard library only. The novelty test and every interpretation of GENIE's configuration are
in PG's offline record (state/2d-closeout/covfix-20261122/pg/record/PG-RECORD.json); PINS_JSON below is derived from
it by make_pins.py. On the node the probe only checks that bytes, links and listings equal those pins. It parses no
XML, emulates no registry and follows no search path. Each step:

0. Identity, before anything else: hostname login<NN>, /pscratch, /global/common and the CVMFS tree. Otherwise STOP
   with nothing read.
1. The repository. /cvmfs/larsoft.opensciencegrid.org must be on its own mount (or /cvmfs's) of a type that is not
   node-local (/proc/mounts), and its xattr user.fqrn must be larsoft.opensciencegrid.org. user.revision and
   user.root_hash are recorded. Unreadable xattrs are a STOP.
2. The genie product, through a descriptor of its root (which must be its own real path). Every pinned file is opened
   relative to it, one component at a time with O_NOFOLLOW, and hashed through its descriptor (O_NOATIME when the
   kernel allows it). Every pinned link is read with readlink, every pinned listing is listed. Any missing, extra or
   different item is a STOP, and the node's value is recorded for every pinned path, hash only.
3. genie_xsec: the live qualifier listing of NULL/ (exact names), with the three used qualifiers required; the pinned
   spline and README of each, hashed as above; and each used data/ listing by names, where a name ending in .xml that
   is not a gxspl-* file is a STOP (GXMLPATH searches data/ first).
4. The UPS database file products/.upsfiles/dbconfig, hashed and recorded, for slot 1's private product (B2).
5. Tools (R1): strace, gpg, gpgconf and gpg-connect-agent are each opened once, on a descriptor of 10 or more (clear
   of gpg's --passphrase-fd 3), and hashed through the descriptor,
   and every later run executes that descriptor. `rpm -qf` names each one's package, and the package's recorded
   digest (`rpm -q --dump`) must equal the hash; a tool with no RPM record is recorded as first-use. strace's
   self-test traces one open of a probe-created file, through its descriptor, and the trace must be complete.
6. gpg (section 4.2) in a fresh mode-700 GNUPGHOME under a node-local /tmp. `gpgconf --list-dirs` comes first: the
   socket dir must be the homedir (or in it) or exactly gpg's /run/user/<uid>/gnupg/d.<zbase32(SHA-1(home))>, private,
   real and on tmpfs, with every reported socket directly in it. Otherwise nothing else runs, not even --kill. The
   round trip, tamper (exit 2, "encrypted message has been manipulated") and wrong passphrase (exit 2, "Bad session
   key") follow. The agent is identified (getinfo pid) once gpg has run, even if crypto failed; then --kill, the
   agent gone, and only then a verified outside socket dir removed; the canonical socket dir and the homedir must be
   lstat-absent at the end.

Exit 0 on GO, 3 on STOP. The last line is `PG-PROBE-RESULT <json>`.

MEASURES: byte identity of the pinned GENIE files, the product listing, the tools. CANNOT AUTHORIZE: generation, or
any choice the declaration leaves to the director.
"""
import datetime
import fcntl
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

SCHEMA = "covfix-pg-probe/4"
REPO = "/cvmfs/larsoft.opensciencegrid.org"
FQRN = "larsoft.opensciencegrid.org"
GENIE_ROOT = REPO + "/products/genie/v3_04_00"
XSEC_REL = "products/genie_xsec/v3_04_00/NULL"
DATA_NAMES = ("README", "isotopes.cfg", "reduce_gxspl.awk", "xsec_graphs.root")   # and gxspl-<name>.xml[.gz]
DBCONFIG_REL = "products/.upsfiles/dbconfig"
GNUPG_PARENT = "/tmp"
RUN_USER = "/run/user"
TOOLS = {"strace": ("/usr/bin/strace",), "gpg": ("/usr/bin/gpg", "/usr/bin/gpg2"), "gpgconf": ("/usr/bin/gpgconf",),
         "gpg-connect-agent": ("/usr/bin/gpg-connect-agent",),
         "awk": ("/usr/bin/gawk", "/bin/gawk", "/usr/bin/awk")}      # the reduce's awk, exec'd under strace: pinned (D1)
RPM = ("/usr/bin/rpm", "/bin/rpm")
LOCAL_FS = ("tmpfs", "ext4", "xfs", "btrfs", "ext3")
TRACE_SET = ("trace=open,openat,openat2,access,faccessat,faccessat2,stat,lstat,newfstatat,statx,readlink,readlinkat,"
             "chdir,fchdir,execve,execveat,rename,renameat,renameat2,link,linkat,symlink,symlinkat,unlink,unlinkat")
ENCRYPT = ["--batch", "--yes", "--pinentry-mode", "loopback", "--passphrase-fd", "3", "--no-symkey-cache",
           "--symmetric", "--cipher-algo", "AES256", "--s2k-digest-algo", "SHA512", "--force-mdc"]
DECRYPT = ["--batch", "--pinentry-mode", "loopback", "--passphrase-fd", "3", "--no-symkey-cache", "--decrypt"]
TAMPER_TEXT = "encrypted message has been manipulated"
WRONG_TEXT = "Bad session key"
GPG_TIMEOUT_S = 120
O_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
O_DIRECTORY = getattr(os, "O_DIRECTORY", 0)
O_NOATIME = getattr(os, "O_NOATIME", 0)
FD_DIR = "/proc/self/fd" if os.path.isdir("/proc/self/fd") else "/dev/fd"

PINS_JSON = r'''{
 "genie_files": {
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/AR23_20i/CommonParam.xml": "aac2040eff7ee43afe9ef859ef512569a01935ff9e35c296d4701f15d66757ef",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/AR23_20i/MECInteractionListGenerator.xml": "b9112c10f460ea6400d9b77653f0bc782c530e6b25b39c6224b32c1bf4b9cfc3",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/AR23_20i/ModelConfiguration.xml": "67f7bf23160a4f92b1f9f69676fc307416d9365950bcda5acd9aa9930e4c0220",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/AR23_20i/NucDeExcitationSim.xml": "83fd8f2072f3f21793ef8e0a6caebe65decd0b838aa8441018a81b4a99ae5c72",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/AR23_20i/README.md": "6fa1fcf2913bab8ddb98b5f646f04c2d98e84040f9b09df34575c61e3b5b2785",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/AR23_20i/TuneGeneratorList.xml": "7a51f7565e0574bbb27749772eeb1f89d2cc2216f55d9e4523d5b408fb397c70",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/EmpiricalMECPXSec2015.xml": "cf4bdcf5a00efe795973e5fdd3b1c3af252ced3b28ac3cc3493f0cf87ad10af4",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/EventGenerator.xml": "6de7109b5bba799d075700d41032ea9c4c10afabc99c14d7af9cf5346adea09d",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/G18_02a/ModelConfiguration.xml": "abb2ac669975a0ff75429b71593c1e4ebd98ea5f21cf2dab75052b2f864acd8c",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/G18_02a/TuneGeneratorList.xml": "7a51f7565e0574bbb27749772eeb1f89d2cc2216f55d9e4523d5b408fb397c70",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/G18_10a/G18_10a_02_11b/CommonParam.xml": "c59dfd384799cf134675b052d5f0009b8531ef49dbd1ceec25ef17b4e9f79df4",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/G18_10a/MECInteractionListGenerator.xml": "b9112c10f460ea6400d9b77653f0bc782c530e6b25b39c6224b32c1bf4b9cfc3",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/G18_10a/ModelConfiguration.xml": "0a861e5c54806f79cdadaa3d175a29e428354d623dc3290b97a1ba2bacbfdbcc",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/G18_10a/TuneGeneratorList.xml": "7a51f7565e0574bbb27749772eeb1f89d2cc2216f55d9e4523d5b408fb397c70",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/G21_11a/CommonParam.xml": "06eaf6bfacc5e891275ddcdb748dd7f6c28168e2032d728f7e9f9da2446011b2",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/G21_11a/EventGenerator.xml": "1430cb7a7ddd76149c2e10ed22227f8c125941d06fa7f772bcfc5db58fc90ea2",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/G21_11a/MECInteractionListGenerator.xml": "d8eef71429aa49f0eaa2aa14e14d6955ca39e36313c30d2d6b5f0276d53cbcf3",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/G21_11a/ModelConfiguration.xml": "2d92e16023607a9998bea383732585a66b3857ec6a23e1abf0f8a28e9bc33611",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/G21_11a/TuneGeneratorList.xml": "531d2749ed4416bfb317fe074ad72536c01b6c682d3f5eaae32a3afb98cb82ad",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/HybridXSecAlgorithm.xml": "1e196c647991b2b5d9ddcdcadefa0e9adde4f80a9a81a381d96311854119e00d",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/LwlynSmithQELCCPXSec.xml": "f1f5c1e4ec47958b9e43e2555ba39e13c81deb2b2b520f0c3a6502fe1e947404",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/NievesQELCCPXSec.xml": "38333360158eab5d0f84dec5ff46f8fdb8ddc169b38da40dd08255a3a2bd033f",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/NievesSimoVacasMECPXSec2016.xml": "e97dfcce427f963dcd8e8c8b15a987785b2172522ae60d4cf96ab36ce181abff",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/RosenbluthPXSec.xml": "c916a07c32ae11bdd05df2a3f9b4818b07d41b11f5836f9a00f39dd4792a127e",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/SuSAv2MECPXSec.xml": "eefaf070e5e8714cc8db74de8835919759f88f3d0c8b01f185046d17477d3d97",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/SuSAv2QELPXSec.xml": "66f2deb1099578c4451201b16e284af0c52632e835becfa39b34dc25ee9ab41b",
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/master_config.xml": "e7ee825dbbf646f71c07db1d0e5f7ed4f2b9044b1163038ed153d88673a534b1",
  "Linux64bit+3.10-2.17-e20-prof/lib/libGFwEG-3.04.00.so": "17a907b15fcef1edb5731d18cd046b77161e7b2c57e3e41b1f15a82d2ba38288",
  "Linux64bit+3.10-2.17-e20-prof/lib/libGFwEG.rootmap": "9aabd31c4b1ea36db2fa2b0cea393a2d4cc405ec974a7d35f22a432f937607ff",
  "Linux64bit+3.10-2.17-e20-prof/lib/libGFwEG_rdict.pcm": "47da9af85b35c3505d77725ef5b74afd5146f5636aca0dfd823643f4630f4494",
  "Linux64bit+3.10-2.17-e20-prof/lib/libGPhMNucXS-3.04.00.so": "b6416ed4e2c86ee9b81ae0c144388d02edb237e7731c12f3d228a131c902c4be",
  "Linux64bit+3.10-2.17-e20-prof/lib/libGPhMNucXS.rootmap": "7633da40522401ed4c429be77b470c8f463c50d6f4ff76445efe220788b714cd",
  "Linux64bit+3.10-2.17-e20-prof/lib/libGPhMNucXS_rdict.pcm": "8e0f991f28210544d3417bbce4becbc8a874e8e142934024d7113bd013ff1121",
  "Linux64bit+3.10-2.17-e20-prof/lib/libGPhQELXS-3.04.00.so": "ee5b004d549fc8eb8070089abe9f1b5a19f1b30696769ebea2d9fc5c5bf88b2b",
  "Linux64bit+3.10-2.17-e20-prof/lib/libGPhQELXS.rootmap": "71a163dfa7290867bef8f55ff64f0b90afb3e55a6c98c8cdf8835ddf49a56d6e",
  "Linux64bit+3.10-2.17-e20-prof/lib/libGPhQELXS_rdict.pcm": "f14b52a17b00adfc7d3ba3a2a57884ecc88bcb3aea32efed8ef526813b71c133",
  "ups/genie.table": "bea8ac631c5f4dc067e723cae6bab22ed37bad4d6184e8950ccbc60dd772a031"
 },
 "genie_links": {
  "Linux64bit+3.10-2.17-e20-prof/lib/libGFwEG.so": "libGFwEG-3.04.00.so",
  "Linux64bit+3.10-2.17-e20-prof/lib/libGPhMNucXS.so": "libGPhMNucXS-3.04.00.so",
  "Linux64bit+3.10-2.17-e20-prof/lib/libGPhQELXS.so": "libGPhQELXS-3.04.00.so"
 },
 "genie_listings": {
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/AR23_20i": [
   "CommonParam.xml",
   "MECInteractionListGenerator.xml",
   "ModelConfiguration.xml",
   "NucDeExcitationSim.xml",
   "README.md",
   "TuneGeneratorList.xml"
  ],
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/AR23_20i/AR23_20i_00_000": null,
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/G18_02a": [
   "G18_02a_02_11a/",
   "G18_02a_02_11b/",
   "G18_02a_03_320/",
   "G18_02a_03_330/",
   "ModelConfiguration.xml",
   "TuneGeneratorList.xml"
  ],
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/G18_02a/G18_02a_00_000": null,
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/G18_10a": [
   "G18_10a_02_11a/",
   "G18_10a_02_11b/",
   "G18_10a_03_320/",
   "G18_10a_03_330/",
   "MECInteractionListGenerator.xml",
   "ModelConfiguration.xml",
   "TuneGeneratorList.xml"
  ],
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/G18_10a/G18_10a_02_11b": [
   "CommonParam.xml"
  ],
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/G21_11a": [
   "CommonParam.xml",
   "EventGenerator.xml",
   "MECInteractionListGenerator.xml",
   "ModelConfiguration.xml",
   "TuneGeneratorList.xml"
  ],
  "Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config/G21_11a/G21_11a_00_000": null
 },
 "record_sha256": "7b8c7a88458acfdee3fd2d1ed9fe85c1945a629861d5552c2120bbc5274b87a2",
 "required_qualifiers": [
  "AR2320i00000-k250-e1000",
  "G1802a00000-k250-e1000",
  "G1810a0211b-k250-e1000"
 ],
 "xsec_files": {
  "AR2320i00000-k250-e1000/data/README": "744cba18f82cc5fe4805cd8be120e5f7e5f7b36f657f4cc9f2118e69c803bcb2",
  "AR2320i00000-k250-e1000/data/gxspl-NUsmall.xml": "185d7d8a4674b5df445fcadea3d17232804390c8421d563aa402c6ee743a0bbb",
  "AR2320i00000-k250-e1000/ups/genie_xsec.table": "fe9c08d6ea916a3e00e2fd14e7632fe1b47a26e7046aa8bea5757da26db02145",
  "G1802a00000-k250-e1000/data/README": "740bc066a9f41f67910e711ebb856be5aed61ee7b71c59895d001d83e80ab0ae",
  "G1802a00000-k250-e1000/data/gxspl-NUsmall.xml": "f7ad710100f66e2bb9f260e328fe7fb10ac063148b4222eebe0e3b61b8bfa45a",
  "G1802a00000-k250-e1000/ups/genie_xsec.table": "d9e54113fccd1f6b7ee48399be1e1aa46d2fede79a0610899f681565d36ede03",
  "G1810a0211b-k250-e1000/data/README": "abfca258817a3f7d8169cdd2dbf9349a025ab38312435c718347598b53f16726",
  "G1810a0211b-k250-e1000/data/gxspl-NUsmall.xml": "1b4b0b37fc8c11acbf00884a94d0a3bda519d9c458f2c916573ef3d673a3ee35",
  "G1810a0211b-k250-e1000/ups/genie_xsec.table": "6ee162520b9ce2a9d439d4ed5277aee6d73c0c107afc5a5ec85a057d64f05800"
 }
}'''
PINS = json.loads(PINS_JSON)


class Unverified(Exception):
    """An item that cannot be read under the probe's rules."""


def exe(fd):
    """The path that executes descriptor fd (Linux: /proc/self/fd/<fd>, valid in the child that inherits it)."""
    return f"{FD_DIR}/{fd}"


# ------------------------------------------------------------------------------------------------ reading by descriptor

def _open_final(dirfd, name, flags):
    try:
        return os.open(name, flags | O_NOFOLLOW | O_NOATIME, dir_fd=dirfd)
    except PermissionError:
        if not O_NOATIME:
            raise
        return os.open(name, flags | O_NOFOLLOW, dir_fd=dirfd)      # O_NOATIME needs ownership; still unfollowed


def _walk(rootfd, rel):
    """(descriptor of rel's parent directory, rel's last component), every component opened with O_NOFOLLOW."""
    parts = rel.split("/")
    if not rel or rel.startswith("/") or any(p in ("", ".", "..") for p in parts):
        raise Unverified(f"{rel!r} is not a plain relative path")
    fd = os.dup(rootfd)
    dev = os.fstat(rootfd).st_dev
    try:
        for p in parts[:-1]:
            nfd = os.open(p, os.O_RDONLY | O_DIRECTORY | O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = nfd
            if os.fstat(fd).st_dev != dev:
                raise Unverified(f"{rel}: {p} is another mount")
    except OSError:
        os.close(fd)
        raise
    return fd, parts[-1]


def sha_rel(rootfd, rel):
    dfd, name = _walk(rootfd, rel)
    try:
        fd = _open_final(dfd, name, os.O_RDONLY | os.O_NONBLOCK)
    finally:
        os.close(dfd)
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise Unverified(f"{rel} is not a regular file")
        if st.st_dev != os.fstat(rootfd).st_dev:
            raise Unverified(f"{rel} is on another mount")
        h = hashlib.sha256()
        for b in iter(lambda: os.read(fd, 1 << 20), b""):
            h.update(b)
        return h.hexdigest()
    finally:
        os.close(fd)


def link_rel(rootfd, rel):
    dfd, name = _walk(rootfd, rel)
    try:
        st = os.stat(name, dir_fd=dfd, follow_symlinks=False)
        if not stat.S_ISLNK(st.st_mode):
            raise Unverified(f"{rel} is not a link")
        if st.st_dev != os.fstat(rootfd).st_dev:
            raise Unverified(f"{rel} is on another mount")
        return os.readlink(name, dir_fd=dfd)
    finally:
        os.close(dfd)


def list_rel(rootfd, rel):
    """Sorted names, directories marked with a trailing '/', or None when lstat reports rel absent."""
    try:
        dfd, name = _walk(rootfd, rel)
    except FileNotFoundError:
        return None
    try:
        try:
            fd = os.open(name, os.O_RDONLY | O_DIRECTORY | O_NOFOLLOW, dir_fd=dfd)
        except FileNotFoundError:
            return None
    finally:
        os.close(dfd)
    try:
        dev = os.fstat(rootfd).st_dev
        if os.fstat(fd).st_dev != dev:
            raise Unverified(f"{rel} is another mount")
        out = []
        for n in sorted(os.listdir(fd)):
            st = os.stat(n, dir_fd=fd, follow_symlinks=False)
            if st.st_dev != dev:
                raise Unverified(f"{rel}/{n} is another mount")
            out.append(n + "/" if stat.S_ISDIR(st.st_mode) else n)
        return out
    finally:
        os.close(fd)


def mount_control(root="/", rel="proc"):
    """A positive control, on the node: list_rel from / into /proc (another mount) must refuse."""
    fd = os.open(root, os.O_RDONLY | O_DIRECTORY)
    try:
        list_rel(fd, rel)
        return {"pass": False, "refused": None}
    except Unverified as e:
        return {"pass": "another mount" in str(e), "refused": str(e)}
    except OSError as e:
        return {"pass": False, "refused": f"{type(e).__name__}"}
    finally:
        os.close(fd)


def _try(fn, *a):
    try:
        return fn(*a), None
    except (OSError, Unverified) as e:
        return None, f"{type(e).__name__}: {e}"


# ------------------------------------------------------------------------------------------------------- identity

def identity():
    host = socket.gethostname()
    checks = {"hostname login<NN>": bool(re.fullmatch(r"login\d{2}", host)),
              "/pscratch": os.path.isdir("/pscratch"), "/global/common": os.path.isdir("/global/common"),
              "CVMFS products": os.path.isdir(REPO + "/products")}
    return {"host": host, "checks": checks, "pass": all(checks.values())}


def read_xattr(path, name):
    return os.getxattr(path, name).decode()


# ---------------------------------------------------------------------------------------------- the verify steps

def verify_repo(repo, mounts_text, xattr=read_xattr):
    rec = {"pass": False}
    mp, typ, dev = mount_entry(repo, mounts_text)
    rec["mount"] = {"point": mp, "type": typ, "device": dev}
    probs = []
    if os.path.realpath(repo) != repo:
        probs.append(f"repo-realpath: {repo} is not its own real path")
    if mp not in (repo, os.path.dirname(repo)) or typ is None or typ in LOCAL_FS:
        probs.append(f"repo-mount: {repo} is not on a CVMFS mount of its own: {mp} {typ}")
    rec["xattrs"] = {}
    for k in ("user.fqrn", "user.revision", "user.root_hash"):
        try:
            rec["xattrs"][k] = xattr(repo, k)
        except (OSError, AttributeError) as e:
            probs.append(f"repo-xattr: xattr {k}: {type(e).__name__}: {e}")
    if rec["xattrs"].get("user.fqrn") != FQRN:
        probs.append(f"repo-fqrn: user.fqrn is {rec['xattrs'].get('user.fqrn')!r}, not {FQRN}")
    for k in ("user.revision", "user.root_hash"):
        if k in rec["xattrs"] and not str(rec["xattrs"][k]).strip():
            probs.append(f"repo-xattr-empty: {k} is empty")
    rec["problems"], rec["pass"] = probs, not probs
    return rec


def verify_genie(genie_root, pins, repo=None):
    rec = {"files": {}, "links": {}, "listings": {}, "problems": []}
    if os.path.realpath(genie_root) != genie_root:
        rec["problems"].append(f"genie-realpath: {genie_root} is not its own real path")
        return rec
    try:
        rfd = os.open(genie_root, os.O_RDONLY | O_DIRECTORY | O_NOFOLLOW)
    except OSError as e:
        rec["problems"].append(f"genie-open: {genie_root}: {e.strerror}")
        return rec
    if repo is not None and os.fstat(rfd).st_dev != os.stat(repo, follow_symlinks=False).st_dev:
        os.close(rfd)                                         # a mount at the genie product itself
        rec["problems"].append(f"genie-mount: {genie_root} is not on the repository's device")
        return rec
    try:
        for rel, want in pins["genie_files"].items():
            got, err = _try(sha_rel, rfd, rel)
            rec["files"][rel] = {"sha256": got, "match": got == want, **({"error": err} if err else {})}
        for rel, want in pins["genie_links"].items():
            got, err = _try(link_rel, rfd, rel)
            rec["links"][rel] = {"target": got, "match": got == want, **({"error": err} if err else {})}
        for rel, want in pins["genie_listings"].items():
            got, err = _try(list_rel, rfd, rel)
            rec["listings"][rel] = {"names": got, "match": err is None and got == want, **({"error": err} if err else {})}
    finally:
        os.close(rfd)
    for kind in ("files", "links", "listings"):
        bad = sorted(k for k, v in rec[kind].items() if not v["match"])
        if bad:
            rec["problems"].append(f"genie-{kind}: {len(bad)} {kind} differ from the pins: {bad}")
    return rec


def verify_xsec(repo, pins):
    rec = {"qualifiers": None, "files": {}, "data_listings": {}, "problems": []}
    try:
        rfd = os.open(repo, os.O_RDONLY | O_DIRECTORY | O_NOFOLLOW)
    except OSError as e:
        rec["problems"].append(f"xsec-open: {repo}: {e.strerror}")
        return rec
    try:
        rec["qualifiers"], err = _try(list_rel, rfd, XSEC_REL)
        if err or rec["qualifiers"] is None:
            rec["problems"].append(f"xsec-qualifiers: the qualifier listing: {err or 'absent'}")
        else:
            names = [n.rstrip("/") for n in rec["qualifiers"]]
            missing = [q for q in pins["required_qualifiers"] if q + "/" not in rec["qualifiers"]]
            if missing:
                rec["problems"].append(f"xsec-qualifiers: required qualifiers missing (exact names): {missing}")
            rec["qualifier_names"] = names
        for rel, want in pins["xsec_files"].items():
            got, err = _try(sha_rel, rfd, f"{XSEC_REL}/{rel}")
            rec["files"][rel] = {"sha256": got, "match": got == want, **({"error": err} if err else {})}
        for q in pins["required_qualifiers"]:
            got, err = _try(list_rel, rfd, f"{XSEC_REL}/{q}/data")
            shadow = [n for n in (got or []) if not (n in DATA_NAMES or re.fullmatch(r"gxspl-[A-Za-z]+\.xml(\.gz)?", n))]
            rec["data_listings"][q] = {"names": got, "config_like": shadow, **({"error": err} if err else {})}
            if err or got is None:
                rec["problems"].append(f"xsec-data: {q}/data: {err or 'absent'}")
            elif shadow:
                rec["problems"].append(f"xsec-data-names: {q}/data holds names outside the allowlist: {shadow}")
        rec["dbconfig"] = {}
        got, err = _try(sha_rel, rfd, DBCONFIG_REL)
        rec["dbconfig"] = {"path": f"{repo}/{DBCONFIG_REL}", "sha256": got, **({"error": err} if err else {})}
        if got is None:
            rec["problems"].append(f"xsec-dbconfig: {err}")
    finally:
        os.close(rfd)
    bad = sorted(k for k, v in rec["files"].items() if not v["match"])
    if bad:
        rec["problems"].append(f"xsec-files: {len(bad)} genie_xsec files differ from the pins: {bad}")
    return rec


def _rpm_digest(path, rpm_run):
    """(package, the digest RPM records for path, rpm -V's output for path) or Nones."""
    out = rpm_run(["-qf", "--qf", "%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}\\n", path])
    if out is not None and out[0] != 0 and "not owned" in out[1]:
        return None, None, None                                  # no RPM record: the first use pins it
    if out is None or out[0] != 0 or not out[1].strip():
        raise Unverified("the RPM query failed")                 # not the same as no record
    pkg = out[1].strip().splitlines()[0]
    dump = rpm_run(["-q", "--dump", pkg])
    if dump is None or dump[0] != 0:
        raise Unverified("the RPM query failed")                 # an owned file whose record could not be read
    digest = None
    for ln in dump[1].splitlines():
        f = ln.split()
        if len(f) >= 4 and f[0] == path:
            digest = f[3]
    if digest is None:
        raise Unverified("the RPM query failed")                 # owned, yet absent from its package's dump
    v = rpm_run(["-V", pkg])
    verify = [ln for ln in (v[1] if v else "").splitlines() if ln.rstrip().endswith(" " + path)]
    return pkg, digest, verify


def _rpm_runner():
    rpm = next((p for p in RPM if os.path.isfile(p)), None)
    if rpm is None:
        return lambda args: None

    def run(args):
        try:
            p = subprocess.run([rpm] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120,
                               env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"})
            return p.returncode, p.stdout.decode(errors="replace")
        except (OSError, subprocess.SubprocessError):
            return None
    return run


def open_tools(tools=TOOLS, rpm_run=None):
    """({name: fd}, record): each tool opened once, hashed through its descriptor, checked against RPM's digest."""
    rpm_run = rpm_run or _rpm_runner()
    fds, rec = {}, {}
    for name, paths in tools.items():
        path = next((p for p in paths if os.path.lexists(p) and stat.S_ISREG(os.lstat(p).st_mode)), None)   # gpg -> gpg2
        r = {"path": path}
        if path is None:
            r["problem"] = ("no regular file among the candidates" if any(os.path.lexists(x) for x in paths)
                            else "missing")
            rec[name] = r
            continue
        try:
            low = os.open(path, os.O_RDONLY | O_NOFOLLOW)
            fd = fcntl.fcntl(low, fcntl.F_DUPFD, 10)      # above 0-3: fd 3 is gpg's --passphrase-fd
            os.close(low)
        except OSError as e:
            r["problem"] = f"cannot open: {e.strerror}"
            rec[name] = r
            continue
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            os.close(fd)
            r["problem"] = "not a regular file"
            rec[name] = r
            continue
        h = hashlib.sha256()
        for b in iter(lambda: os.read(fd, 1 << 20), b""):
            h.update(b)
        os.lseek(fd, 0, os.SEEK_SET)
        r["sha256"] = h.hexdigest()
        try:
            r["rpm_package"], r["rpm_digest"], r["rpm_verify"] = _rpm_digest(path, rpm_run)
            r["rpm_status"] = "recorded" if r["rpm_digest"] else "not-owned"
        except Unverified:
            r["rpm_package"], r["rpm_digest"], r["rpm_verify"], r["rpm_status"] = None, None, None, "query-failed"
            r["problem"] = "the RPM query failed"
        if r.get("problem"):
            r["rpm_match"], r["pin_basis"] = None, None
        elif r["rpm_digest"] is None:
            r["rpm_match"], r["pin_basis"] = None, "first use: no RPM record"
        else:
            r["rpm_match"], r["pin_basis"] = r["rpm_digest"] == r["sha256"], "RPM's recorded digest"
            if not r["rpm_match"]:
                r["problem"] = "the hash differs from RPM's recorded digest"
        fds[name] = fd
        rec[name] = r
    return fds, rec


def trace_complete(text, rc):
    """pg_verify.trace_problems, the same rules and codes (C16): strace's rc, a whole last line, a pid on every line,
    every unfinished call resumed by the same syscall, an exit record for every pid, every exit 0."""
    probs = []
    if rc != 0:
        probs.append(f"strace-rc: strace exited {rc}")
    if not text:
        return probs + ["empty: the trace is empty"]
    if not text.endswith("\n"):
        probs.append("truncated: the trace's last line is truncated")
    ms = [re.match(r"^(\d+) +(.*)$", ln) for ln in text.splitlines()]
    if not all(ms):
        return probs + ["no-pid: a trace line has no pid"]
    first = ms[0].group(1)
    pending, exits, seen, killed = {}, {}, set(), set()
    for m in ms:
        pid, rest = m.group(1), m.group(2)
        seen.add(pid)
        r = re.match(r"^<\.\.\. ([a-z0-9_]+) resumed>", rest)
        if r:
            if pending.pop(pid, None) != r.group(1):
                probs.append(f"resume-mismatch: process {pid} resumed {r.group(1)} without its unfinished call")
        elif rest.endswith("<unfinished ...>"):
            sm = re.match(r"^([a-z0-9_]+)\(", rest)
            pending[pid] = sm.group(1) if sm else "?"
        x = re.match(r"\+\+\+ exited with (\d+) \+\+\+", rest)
        if x:
            exits[pid] = int(x.group(1))
        if rest.startswith("+++ killed by"):
            probs.append(f"killed: process {pid} was killed")
            killed.add(pid)
    if exits.get(first) != 0:
        probs.append("initial-exit: the initial process did not exit 0")
    probs += [f"child-exit: process {q} exited {v}" for q, v in sorted(exits.items()) if q != first and v != 0]
    if pending:
        probs.append(f"unresumed: calls left unfinished in processes {sorted(pending)}")
    open_ended = sorted(seen - set(exits) - killed)
    if open_ended:
        probs.append(f"no-terminal: processes {open_ended} have no exit record")
    return probs


def strace_self_test(fd, parent=GNUPG_PARENT):
    rec = {"pass": False}
    d = tempfile.mkdtemp(prefix="pgst", dir=parent)
    try:
        probe, out = os.path.join(d, "pg-self-test.txt"), os.path.join(d, "trace.txt")
        with open(probe, "w") as f:
            f.write("pg\n")
        p = subprocess.run([exe(fd), "-f", "-q", "-e", TRACE_SET, "-o", out, "/bin/cat", probe], pass_fds=(fd,),
                           stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=60,
                           env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"})
        text = ""
        if os.path.exists(out):
            with open(out) as f:
                text = f.read()
        probs = trace_complete(text, p.returncode)
        if not re.search(r'open(at)?\((AT_FDCWD, )?"' + re.escape(probe) + r'", .*\) = \d+$', text, re.M):
            probs.append("self-test-open: the self-test's open is not in the trace")
        rec.update(rc=p.returncode, n_lines=len(text.splitlines()), problems=probs)
        rec["pass"] = not probs
    except (OSError, subprocess.SubprocessError) as e:
        rec["problems"] = [f"self-test-error: {type(e).__name__}: {e}"]
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return rec


# ------------------------------------------------------------- rev 3's reviewed mount, OpenPGP and socket helpers

def proc_mount(mounts_text):
    """{options, hidepid}: /proc's mount, recorded (C3; the director: other users are excluded by the exclusive
    allocation, which pg_generate records on the compute node itself; B1 runs on a login node and has none)."""
    opts = [ln.split()[3] for ln in mounts_text.splitlines() if len(ln.split()) > 3 and ln.split()[1] == "/proc"]
    if not opts:
        return {"options": None, "hidepid": None}
    hp = [o.split("=", 1)[1] for o in opts[-1].split(",") if o.startswith("hidepid=")]
    return {"options": opts[-1], "hidepid": hp[-1] if hp else "0"}


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
    st = os.lstat(p)          # never writable by another user; the gnupg dirs not even readable
    return stat.S_ISDIR(st.st_mode) and st.st_uid == uid and not st.st_mode & (0o077 if private else 0o022)


def check_sockets(dirs, home, uid, mounts_text, base=RUN_USER):
    """(confined, the verified socket dir if outside home else None, problems), from `gpgconf --list-dirs`, before
    any other gpg call. The socket dir is the homedir itself (or inside it), or exactly gpg's canonical
    /run/user/<uid>/gnupg/d.<hash> for it; every reported socket lies directly in that socket dir."""
    h, sd = dirs.get("homedir", ""), dirs.get("socketdir", "")
    socks = {k: v for k, v in dirs.items() if k.endswith("-socket") and v}
    if not h or os.path.realpath(h) != home or not sd or "agent-socket" not in socks:
        return False, None, [f"sockets-listing: homedir {h!r}, socketdir {sd!r}, sockets {sorted(socks)}"]
    probs, outside = [], None
    if not _inside(sd, home):
        want = socketdir_for(home, uid, base)
        if sd != want:
            return False, None, [f"socketdir-place: socketdir {sd} is neither in the homedir nor gpg's {want}"]
        for p, private in ((f"{base}/{uid}", False), (f"{base}/{uid}/gnupg", True), (sd, True)):
            try:
                ok = _owned_dir(p, uid, private)
            except OSError:
                ok = False
            if not ok:
                probs.append(f"socketdir-owner: {p} is not a {'private ' if private else 'non-writable '}directory of uid {uid}")
        if os.path.realpath(sd) != sd:
            probs.append(f"socketdir-realpath: {sd} is not its own real path")
        if mount_fs(sd, mounts_text) != "tmpfs":
            probs.append(f"socketdir-fs: {sd} is on {mount_fs(sd, mounts_text)}, not tmpfs")
        outside = sd
    real_sd = os.path.realpath(sd)
    probs += [f"socket-place: {k} {v} is not directly in the socket dir {sd}" for k, v in sorted(socks.items())
              if os.path.realpath(os.path.dirname(v)) != real_sd]
    probs += [f"socket-link: {k} {v} is a link" for k, v in sorted(socks.items()) if os.path.islink(v)]
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




def _fd_open(fd):
    try:
        os.fstat(fd)
        return True
    except OSError:
        return False


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


def _genv(home):
    return {"PATH": "/usr/bin:/bin", "HOME": home, "GNUPGHOME": home, "LC_ALL": "C", "LANG": "C"}


def _run(fd, args, env, home, **kw):
    """Run the tool on descriptor fd (the descriptor that was hashed)."""
    return subprocess.run([exe(fd)] + args, env=env, cwd=home, timeout=kw.pop("timeout", 30),
                          pass_fds=tuple(sorted({fd} | set(kw.pop("extra_fds", ())))), **kw)


def _run_gpg(gfd, args, passphrase, payload, env):
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
        p = _run(gfd, args, env, env["GNUPGHOME"], input=payload, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                 extra_fds=(3,), timeout=GPG_TIMEOUT_S)
        return p.returncode, p.stdout, p.stderr.decode(errors="replace").splitlines()
    finally:
        os.close(r)
        if w is not None:
            os.close(w)


def gpg_check(fds, parent=GNUPG_PARENT, mounts_text=None, run_base=RUN_USER, uid=None):
    """Section 4.2's encryption-tool check, confined to a throwaway GNUPGHOME, with the tools run by descriptor."""
    rec = {"pass": False, "std_fds_reopened": _std_fds_open(), "gpg_started": False}
    uid = os.getuid() if uid is None else uid
    if not all(k in fds for k in ("gpg", "gpgconf", "gpg-connect-agent")):
        rec["problem"] = "an approved gpg executable is missing"
        return rec
    parent = os.path.realpath(parent)
    rec["parent"], rec["parent_fs"] = parent, mount_fs(parent, mounts_text)
    if rec["parent_fs"] not in LOCAL_FS:
        rec["problem"] = f"{parent} is on {rec['parent_fs']}, not a node-local filesystem"
        return rec
    home, canonical, outside, crypto = None, None, None, False
    try:
        home = os.path.realpath(tempfile.mkdtemp(prefix="pgprobe", dir=parent))
        os.chmod(home, 0o700)
        env = _genv(home)
        rec["gnupghome_mode"] = oct(os.stat(home).st_mode & 0o777)
        canonical = socketdir_for(home, uid, run_base)
        rec["canonical_socketdir"] = canonical
        ld = _run(fds["gpgconf"], ["--list-dirs"], env, home, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        d = {k: v.replace("%3a", ":").replace("%25", "%") for k, v in
             (ln.split(":", 1) for ln in ld.stdout.decode(errors="replace").splitlines() if ":" in ln)}
        rec["gpgconf_dirs"] = {k: v for k, v in d.items() if k in ("homedir", "socketdir") or k.endswith("-socket")}
        ok, outside, rec["socket_problems"] = check_sockets(d, home, uid, mounts_text, run_base)
        rec["confined"] = ok and ld.returncode == 0
        rec["socketdir_outside_home"] = outside
        if not rec["confined"]:
            raise RuntimeError("the agent's sockets are not confined; nothing else was run")
        rec["gpg_started"] = crypto = True
        v = _run(fds["gpg"], ["--version"], env, home, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        rec["version"] = v.stdout.decode(errors="replace").splitlines()[:2]
        pw, payload = secrets.token_hex(32), os.urandom(1 << 16)
        rc_e, ct, err_e = _run_gpg(fds["gpg"], ENCRYPT, pw, payload, env)
        rec.update(encrypt_rc=rc_e, encrypt_stderr=err_e[-6:])
        if rc_e != 0:
            raise RuntimeError("encryption failed")
        rec["packet_tags"] = [p[0] for p in packets(ct)]
        bad = tamper_seipd(ct)
        rc_d, pt, _ = _run_gpg(fds["gpg"], DECRYPT, pw, ct, env)
        rc_t, _, err_t = _run_gpg(fds["gpg"], DECRYPT, pw, bad, env)
        rc_w, _, err_w = _run_gpg(fds["gpg"], DECRYPT, secrets.token_hex(32), ct, env)
        rec.update(decrypt_rc=rc_d, round_trip_equal=hashlib.sha256(pt).digest() == hashlib.sha256(payload).digest(),
                   tampered={"rc": rc_t, "stderr": err_t[-6:], "evidence": any(TAMPER_TEXT in x for x in err_t)},
                   wrong_passphrase={"rc": rc_w, "stderr": err_w[-6:],
                                     "evidence": any(WRONG_TEXT in x for x in err_w)})
        rec["pass"] = (rc_d == 0 and rec["round_trip_equal"] and rec["packet_tags"] == [3, 18]
                       and rc_t == 2 and rec["tampered"]["evidence"] and rc_w == 2
                       and rec["wrong_passphrase"]["evidence"])
    except (OSError, subprocess.SubprocessError, RuntimeError, ValueError) as e:
        rec["problem"] = f"{type(e).__name__}: {e}"
        rec["pass"] = False
    finally:
        agent_pid = None
        if home and crypto:              # gpg has run: identify its agent, kill it, and only then remove its sockets
            try:
                a = _run(fds["gpg-connect-agent"], ["--no-autostart", "getinfo pid", "/bye"], _genv(home), home,
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
                m = re.search(r"^D (\d+)$", a.stdout.decode(errors="replace"), re.M)
                agent_pid = int(m.group(1)) if m else None
            except (OSError, subprocess.SubprocessError):
                pass
            rec["agent_pid"] = agent_pid
            try:
                rec["gpgconf_kill_rc"] = _run(fds["gpgconf"], ["--kill", "gpg-agent"], _genv(home), home,
                                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
            except (OSError, subprocess.SubprocessError) as e:
                rec["gpgconf_kill_rc"] = f"{type(e).__name__}: {e}"
            gone = False
            if agent_pid is not None:
                t0 = time.time()
                while _pid_alive(agent_pid) and time.time() - t0 < 10:
                    time.sleep(0.1)
                gone = not _pid_alive(agent_pid)
            rec["agent_gone"] = gone
            if outside and gone:
                try:
                    rec["remove_socketdir_rc"] = _run(fds["gpgconf"], ["--remove-socketdir"], _genv(home), home,
                                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
                except (OSError, subprocess.SubprocessError) as e:
                    rec["remove_socketdir_rc"] = f"{type(e).__name__}: {e}"
        if home:
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


def probe(ident=identity, repo=REPO, genie_root=GENIE_ROOT, pins=None, mounts=_mounts, xattr=read_xattr,
          tools=TOOLS, rpm_run=None, gpg=gpg_check, self_test=strace_self_test, control=None):
    pins = pins or PINS
    rec = {"schema": SCHEMA, "start_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "pins_sha256": hashlib.sha256(json.dumps(pins, sort_keys=True).encode()).hexdigest(),
           "record_sha256": pins.get("record_sha256")}
    rec["identity"] = ident()
    if not rec["identity"]["pass"]:
        rec["stops"] = ["identity: not a Perlmutter login node; nothing was read"]
        rec["verdict"] = "STOP"
        return rec
    stops = []
    try:
        mounts_text = mounts()
    except OSError as e:
        rec["stops"] = [f"mounts: {e}"]
        rec["verdict"] = "STOP"
        return rec
    rec["proc_mount"] = proc_mount(mounts_text)
    rec["mount_control"] = (control or mount_control)()
    if not rec["mount_control"]["pass"]:
        stops.append("mount-control: a walk into /proc did not refuse at its final directory")
    rec["repo"] = verify_repo(repo, mounts_text, xattr)
    stops += [f"repo: {p}" for p in rec["repo"]["problems"]]
    if rec["repo"]["pass"]:
        rec["genie"] = verify_genie(genie_root, pins, repo)
        stops += [f"genie: {p}" for p in rec["genie"]["problems"]]
        rec["xsec"] = verify_xsec(repo, pins)
        stops += [f"genie_xsec: {p}" for p in rec["xsec"]["problems"]]
    rec["std_fds_reopened"] = _std_fds_open()
    fds, rec["tools"] = open_tools(tools, rpm_run)
    try:
        stops += [f"tool {k}: {v['problem']}" for k, v in rec["tools"].items() if "problem" in v]
        rec["strace_self_test"] = self_test(fds["strace"]) if "strace" in fds else {"pass": False,
                                                                                   "problems": ["no strace"]}
        if not rec["strace_self_test"]["pass"]:
            stops.append(f"strace self-test: {rec['strace_self_test'].get('problems')}")
        rec["gpg"] = gpg(fds, mounts_text=mounts_text)
        if not rec["gpg"]["pass"]:
            stops.append("gpg: the tool or its pinned round trip failed")
    finally:
        for fd in fds.values():
            os.close(fd)
    rec["stops"] = stops
    rec["verdict"] = "GO" if not stops else "STOP"
    rec["end_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return rec


def report(rec):
    p = print
    p(f"identity {rec['identity']}")
    if "repo" in rec:
        p(f"repo {rec['repo'].get('mount')} xattrs {rec['repo'].get('xattrs')}")
    for q in (rec.get("xsec") or {}).get("qualifiers") or []:
        p(f"  qualifier {q}")
    for k, v in (rec.get("tools") or {}).items():
        p(f"tool {k}: {v.get('path')} {v.get('sha256')} rpm {v.get('rpm_package')} match {v.get('rpm_match')}")
    p(f"verdict {rec['verdict']}  stops {rec['stops']}")
    p("PG-PROBE-RESULT " + json.dumps(rec, sort_keys=True))


def main():
    try:
        rec = probe()
    except Exception as e:                 # fail closed, with a reason no other test expects
        rec = {"schema": SCHEMA, "identity": {}, "verdict": "STOP", "stops": [f"internal-error: {type(e).__name__}"]}
    report(rec)
    return 0 if rec["verdict"] == "GO" else 3


if __name__ == "__main__":
    sys.exit(main())
