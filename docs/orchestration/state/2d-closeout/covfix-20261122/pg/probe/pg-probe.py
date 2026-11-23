"""PG's stat-only probe and novelty test (COVFIX-DECLARATION.md section 4.1), for a Perlmutter login node.

Run with no arguments, as `ssh saul.nersc.gov '/usr/bin/python3.11 -I -B -' < pg-probe.py` (pg-probe-launch.sh does
this after checking this file's sha256). Standard library only. It reads catalog and configuration files only:
  - the genie_xsec v3_04_00 product's qualifier list, each tune's gxspl-NUsmall.xml and README (sha256, version
    line), and the product's UPS table (GENIE_XSEC_TUNE);
  - GENIE v3_04_00's own tune configuration (config/<CMC>/ModelConfiguration.xml and config/<CMC>/<tune>/), for the
    CCQE (QEL-CC) and 2p2h (MEC-CC) cross-section model classes.
It reads no generated content.

Then it applies section 4.1's novelty test: a chosen tune qualifies only if at least one of its CCQE class and its
2p2h class is used by neither spent tune (G18_10a_02_11b, AR23_20i_00_000). Slot 1 is G21_11b_00_000. Slot 2 is
G18_02b_02_11b, or G18_02a_02_11b only if 02b is absent from the product; a novelty exclusion of 02b excludes 02a.

Positive controls: the spent tunes' spline and README digests and README version lines must equal F1's pins
(gen5d_v3.SPLINE_PINS), and their parsed classes must equal FD-F1-REPORT.md section 1.3's. A failed control is a STOP.

Encryption tool (section 4.2): gpg must exist, and a synthetic round trip with the pinned flags (passphrase on fd 3)
must reproduce a random payload. A tampered ciphertext and a wrong passphrase must each make decrypt exit non-zero.
GNUPGHOME is a fresh mode-700 directory in the login node's own temp dir (node-local, so gpg-agent can make its
socket there and the path stays short), removed at the end after `gpgconf --kill gpg-agent`, which must exit 0. The
probe records that no agent for it survives (ps must work, so that "none" is a measurement) and that ~/.gnupg was
not created or changed. The passphrase is synthetic (secrets.token_hex(32)) and is never printed.

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
import subprocess
import sys
import tempfile

PRODUCTS = "/cvmfs/larsoft.opensciencegrid.org/products"
XSEC_ROOT = PRODUCTS + "/genie_xsec/v3_04_00/NULL"
UPS_DIR = PRODUCTS + "/genie_xsec/v3_04_00/ups"
GENIE_CONFIG = PRODUCTS + "/genie/v3_04_00/Linux64bit+3.10-2.17-e20-prof/GENIE-Generator/config"

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
# FD-F1-REPORT.md section 1.3: (CCQE class, 2p2h class).
SPENT_CLASSES = {"G18_10a_02_11b": ("NievesQELCCPXSec", "NievesSimoVacasMECPXSec"),
                 "AR23_20i_00_000": ("NievesQELCCPXSec", "SuSAv2MECPXSec")}
SLOTS = {"QEL-CC": "ccqe", "MEC-CC": "2p2h"}

ENCRYPT = ["--batch", "--yes", "--pinentry-mode", "loopback", "--passphrase-fd", "3", "--no-symkey-cache",
           "--symmetric", "--cipher-algo", "AES256", "--s2k-digest-algo", "SHA512", "--force-mdc"]
DECRYPT = ["--batch", "--pinentry-mode", "loopback", "--passphrase-fd", "3", "--no-symkey-cache", "--decrypt"]
GPG_TIMEOUT_S = 120


def qualifier(tune):
    """G18_10a_02_11b -> G1810a0211b-k250-e1000 (the genie_xsec directory convention, FD-F1-DECLARATION.md:76)."""
    return tune.replace("_", "") + "-k250-e1000"


def cmc(tune):
    """G18_10a_02_11b -> G18_10a, the comprehensive model configuration's config directory."""
    return "_".join(tune.split("_")[:2])


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def catalog(xsec_root, tune):
    """The tune's genie_xsec entry: whether its qualifier directory is in the product (present), whether it holds its
    spline file and README (complete), their digests and the README's version lines."""
    q = os.path.join(xsec_root, qualifier(tune))
    spl, readme = os.path.join(q, "data", "gxspl-NUsmall.xml"), os.path.join(q, "data", "README")
    rec = {"qualifier": qualifier(tune), "present": os.path.isdir(q),
           "complete": os.path.isfile(spl) and os.path.isfile(readme)}
    if rec["complete"]:
        with open(readme, errors="replace") as f:
            versions = [ln.strip() for ln in f if ln.strip().startswith("version ")]
        rec.update(spline_sha256=sha256_file(spl), spline_bytes=os.path.getsize(spl),
                   readme_sha256=sha256_file(readme), readme_version_lines=versions)
    return rec


_COMMENT = re.compile(r"<!--.*?-->", re.S)
_PARAM = re.compile(r'<param\b[^>]*\bname\s*=\s*"XSecModel@genie::EventGenerator/(QEL-CC|MEC-CC)"[^>]*>(.*?)</param>',
                    re.S)


def xsec_models(text):
    """{'QEL-CC': [values], 'MEC-CC': [values]} from one GENIE XML file, comments removed."""
    out = {k: [] for k in SLOTS}
    for key, val in _PARAM.findall(_COMMENT.sub("", text)):
        out[key].append(val.strip())
    return out


def class_name(value):
    """genie::NievesQELCCPXSec/Default -> NievesQELCCPXSec."""
    return value.split("/")[0].strip().split("::")[-1]


def model_classes(config_root, tune):
    """The tune's QEL-CC and MEC-CC classes: the CMC's ModelConfiguration.xml, overridden by the tune's own
    configuration directory, which GENIE may place inside the CMC's (config/<CMC>/<tune>/) or beside it
    (config/<tune>/); both are read. A slot set twice in one file, or to different classes by two override files,
    is a problem (unresolved), never a guess."""
    rec = {"cmc": cmc(tune), "files": [], "lines": [], "problems": [], "ccqe": None, "2p2h": None, "sources": {},
           "tune_dirs": []}
    base = os.path.join(config_root, cmc(tune))
    mc = os.path.join(base, "ModelConfiguration.xml")
    if not os.path.isfile(mc):
        rec["problems"].append(f"no {mc}")
        return rec
    overrides = []
    for sub in (os.path.join(base, tune), os.path.join(config_root, tune)):
        if os.path.isdir(sub):
            rec["tune_dirs"].append(sub)
            overrides += sorted(os.path.join(sub, n) for n in os.listdir(sub) if n.endswith(".xml"))
    found = {}
    for path in [mc] + overrides:
        with open(path, errors="replace") as f:
            text = f.read()
        rec["files"].append(path)
        rec["lines"] += [f"{os.path.relpath(path, config_root)}: {ln.strip()}" for ln in text.splitlines()
                         if "QEL-CC" in ln or "MEC-CC" in ln
                         or ("XSecModel" in ln and ("QEL" in ln or "MEC" in ln))]
        for key, vals in xsec_models(text).items():
            if len(vals) > 1:
                rec["problems"].append(f"{path}: {len(vals)} uncommented {key} XSecModel entries")
            elif vals:
                found.setdefault(key, []).append((path, class_name(vals[0])))
    for key, slot in SLOTS.items():
        hits = found.get(key, [])
        base_hits = [h for h in hits if h[0] == mc]
        over = [h for h in hits if h[0] != mc]
        if len({c for _, c in over}) > 1:
            rec["problems"].append(f"{key}: the tune's override files disagree: {over}")
        pick = over[-1] if over else (base_hits[0] if base_hits else None)
        if pick:
            rec["sources"][slot], rec[slot] = pick
        else:
            rec["problems"].append(f"no {key} XSecModel for {tune}")
    return rec


def ups_lines(ups_dir):
    """The UPS table lines that name a qualifier or GENIE_XSEC_TUNE."""
    out = []
    if not os.path.isdir(ups_dir):
        return [f"(no {ups_dir})"]
    for n in sorted(os.listdir(ups_dir)):
        p = os.path.join(ups_dir, n)
        if n.endswith(".table") and os.path.isfile(p):
            with open(p, errors="replace") as f:
                out += [f"{n}: {ln.strip()}" for ln in f if "Qualifiers" in ln or "GENIE_XSEC_TUNE" in ln]
    return out


def novel(rec, spent_set):
    return rec["ccqe"] not in spent_set or rec["2p2h"] not in spent_set


def resolved(rec):
    return not rec["problems"] and rec["ccqe"] is not None and rec["2p2h"] is not None


def decide(cat, cls, spent_pins=SPENT_PINS, spent_classes=SPENT_CLASSES):
    """Section 4.1's controls, novelty test and fallback rule on the probe's records. Returns the verdict record."""
    stops, controls = [], {}
    for t in SPENT:
        c, pin = cat[t], spent_pins[t]
        ok = (c["complete"] and c["spline_sha256"] == pin[0] and c["readme_sha256"] == pin[1]
              and c["readme_version_lines"] == [pin[2]])
        controls[f"{t}: catalog equals F1's pins"] = ok
        okc = resolved(cls[t]) and (cls[t]["ccqe"], cls[t]["2p2h"]) == spent_classes[t]
        controls[f"{t}: classes equal FD-F1-REPORT 1.3"] = okc
        if not ok:
            stops.append(f"control: {t}'s catalog is not F1's pins")
        if not okc:
            stops.append(f"control: {t}'s parsed classes are not FD-F1-REPORT 1.3's")
    spent_set = sorted({cls[t][s] for t in SPENT for s in ("ccqe", "2p2h") if cls[t][s]})

    def judge(t):
        if not cat[t]["present"]:
            return "absent"
        if not cat[t]["complete"]:
            return "incomplete (qualifier directory without its spline file or README)"
        if not resolved(cls[t]):
            return "unresolved"
        return "qualifies" if novel(cls[t], spent_set) else "excluded (both classes used by a spent tune)"

    status = {t: judge(t) for t in (SLOT1, SLOT2, SLOT2_FALLBACK)}
    slot1 = SLOT1 if status[SLOT1] == "qualifies" else None
    if slot1 is None:
        stops.append(f"slot 1: {SLOT1} {status[SLOT1]}")
    fallback = False
    if status[SLOT2] == "absent":
        fallback = True
        slot2 = SLOT2_FALLBACK if status[SLOT2_FALLBACK] == "qualifies" else None
        if slot2 is None:
            stops.append(f"slot 2: {SLOT2} absent, {SLOT2_FALLBACK} {status[SLOT2_FALLBACK]}")
    elif status[SLOT2] == "qualifies":
        slot2 = SLOT2
    else:
        slot2 = None
        stops.append(f"slot 2: {SLOT2} {status[SLOT2]} (02a substitutes only for 02b's absence)")
    overlap = {}
    for t in (slot1, slot2):
        if t:
            overlap[t] = {s: [u for u in SPENT if cls[u][s] == cls[t][s]] for s in ("ccqe", "2p2h")}
    same_02 = None
    if resolved(cls[SLOT2]) and resolved(cls[SLOT2_FALLBACK]):
        same_02 = (cls[SLOT2]["ccqe"], cls[SLOT2]["2p2h"]) == (cls[SLOT2_FALLBACK]["ccqe"], cls[SLOT2_FALLBACK]["2p2h"])
    if fallback and slot2 and same_02 is False:
        stops.append("slot 2: 02a's configured classes differ from 02b's, against section 4.1's premise")
    return {"spent_classes": spent_set, "status": status, "chosen": {"u0": slot1, "u1": slot2},
            "fallback_taken": fallback if slot2 else None, "overlap_with_spent": overlap,
            "02a_02b_same_classes": same_02, "controls": controls, "stops": stops}


def _fd_open(fd):
    try:
        os.fstat(fd)
        return True
    except OSError:
        return False


def _run_gpg(gpg, args, passphrase, payload, env):
    """One gpg call with the passphrase on fd 3 and the payload streamed on stdin. Returns (rc, stdout, the last
    lines of stderr)."""
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
                           pass_fds=(3,), env=env, timeout=GPG_TIMEOUT_S)
        return p.returncode, p.stdout, p.stderr.decode(errors="replace").splitlines()[-6:]
    finally:
        os.close(r)
        if w is not None:
            os.close(w)


def _agents(home):
    """PIDs of this user's gpg-agent processes whose command line names home (ps, matched in Python)."""
    try:
        p = subprocess.run(["ps", "-u", str(os.getuid()), "-o", "pid=,args="], stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if p.returncode != 0:
        return None
    out = []
    for ln in p.stdout.decode(errors="replace").splitlines():
        pid, _, args = ln.strip().partition(" ")
        if "gpg-agent" in args and home in args:
            out.append(pid)
    return out


def _tree_state(path):
    """Existence and (relative path, size, mtime_ns) of every entry under path, by stat only."""
    if not os.path.exists(path):
        return None
    out = []
    for root, dirs, files in os.walk(path):
        for n in sorted(dirs + files):
            p = os.path.join(root, n)
            try:
                st = os.lstat(p)
                out.append([os.path.relpath(p, path), st.st_size, st.st_mtime_ns])
            except OSError:
                out.append([os.path.relpath(p, path), None, None])
    st = os.lstat(path)
    return {"mtime_ns": st.st_mtime_ns, "entries": sorted(out)}


def gpg_check(gpg=None, scratch=None):
    """Section 4.2's encryption-tool check under a throwaway GNUPGHOME."""
    gpg = gpg or shutil.which("gpg")
    rec = {"gpg": gpg, "pass": False}
    if not gpg:
        rec["problem"] = "no gpg on PATH"
        return rec
    user_home = os.path.expanduser("~/.gnupg")
    before = _tree_state(user_home)
    base = scratch or tempfile.gettempdir()
    home = None
    env = {k: v for k, v in os.environ.items() if k not in ("GNUPGHOME", "GPG_AGENT_INFO")}
    try:
        home = os.path.realpath(tempfile.mkdtemp(prefix="pgprobegnupg", dir=base))
        os.chmod(home, 0o700)
        env["GNUPGHOME"] = home
        rec["gnupghome_base"], rec["gnupghome_mode"] = base, oct(os.stat(home).st_mode & 0o777)
        v = subprocess.run([gpg, "--version"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, timeout=30)
        rec["version"] = v.stdout.decode(errors="replace").splitlines()[:2]
        pw, payload = secrets.token_hex(32), os.urandom(1 << 16)
        rc_e, ct, err_e = _run_gpg(gpg, ENCRYPT, pw, payload, env)
        skip = (None, b"", [])
        rc_d, pt, err_d = _run_gpg(gpg, DECRYPT, pw, ct, env) if rc_e == 0 else skip
        bad = bytearray(ct)
        if bad:
            bad[len(bad) // 2] ^= 0x01
        rc_t, _, _ = _run_gpg(gpg, DECRYPT, pw, bytes(bad), env) if rc_e == 0 else skip
        rc_w, _, _ = _run_gpg(gpg, DECRYPT, secrets.token_hex(32), ct, env) if rc_e == 0 else skip
        rec.update(encrypt_stderr=err_e, decrypt_stderr=err_d)
        rec.update(encrypt_rc=rc_e, decrypt_rc=rc_d, ciphertext_differs=bool(ct) and ct != payload,
                   round_trip_equal=hashlib.sha256(pt).digest() == hashlib.sha256(payload).digest(),
                   tampered_decrypt_rc=rc_t, wrong_passphrase_decrypt_rc=rc_w)
        rec["pass"] = (rc_e == 0 and rc_d == 0 and rec["ciphertext_differs"] and rec["round_trip_equal"]
                       and rc_t not in (0, None) and rc_w not in (0, None))
    except (OSError, subprocess.SubprocessError, RuntimeError) as e:
        rec["problem"] = f"{type(e).__name__}: {e}"
        rec["pass"] = False
    finally:
        rec["agents_before_kill"] = _agents(home) if home else None
        conf = shutil.which("gpgconf", path=os.path.dirname(gpg)) or shutil.which("gpgconf")
        rec["gpgconf"] = conf
        try:
            rec["gpgconf_kill_rc"] = subprocess.run([conf, "--kill", "gpg-agent"], env=env, stdout=subprocess.DEVNULL,
                                                    stderr=subprocess.DEVNULL, timeout=30).returncode \
                if conf and home else None
        except (OSError, subprocess.SubprocessError) as e:
            rec["gpgconf_kill_rc"] = f"{type(e).__name__}: {e}"
        rec["agents_after_kill"] = _agents(home) if home else None
        if home:
            shutil.rmtree(home, ignore_errors=True)
        rec["gnupghome_removed"] = bool(home) and not os.path.exists(home)
        after = _tree_state(user_home)
        rec["user_gnupg_existed_before"] = before is not None
        rec["user_gnupg_unchanged"] = before == after
    rec["pass"] = bool(rec["pass"] and rec["gpgconf_kill_rc"] == 0 and rec["agents_before_kill"] is not None
                       and rec["agents_after_kill"] == [] and rec["gnupghome_removed"]
                       and rec["user_gnupg_unchanged"])
    return rec


def probe(xsec_root=XSEC_ROOT, config_root=GENIE_CONFIG, ups_dir=UPS_DIR, gpg=None, scratch=None,
          spent_pins=SPENT_PINS, spent_classes=SPENT_CLASSES):
    rec = {"schema": "covfix-pg-probe/1", "host": socket.gethostname(),
           "start_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "roots": {"xsec": xsec_root, "config": config_root, "ups": ups_dir}}
    rec["qualifiers"] = sorted(os.listdir(xsec_root)) if os.path.isdir(xsec_root) else None
    rec["catalog"] = {t: catalog(xsec_root, t) for t in ALL_TUNES}
    rec["classes"] = {t: model_classes(config_root, t) for t in ALL_TUNES}
    rec["ups"] = ups_lines(ups_dir)
    rec["decision"] = decide(rec["catalog"], rec["classes"], spent_pins, spent_classes)
    rec["gpg"] = gpg_check(gpg, scratch)
    stops = list(rec["decision"]["stops"])
    if rec["qualifiers"] is None:
        stops.append(f"no {xsec_root}")
    if not rec["gpg"]["pass"]:
        stops.append("gpg: the tool or its pinned round trip failed")
    rec["stops"] = stops
    rec["verdict"] = "GO" if not stops else "STOP"
    rec["end_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return rec


def report(rec):
    p = print
    p(f"host {rec['host']}  start {rec['start_utc']}")
    p(f"genie_xsec v3_04_00 qualifiers ({len(rec['qualifiers'] or [])}):")
    for q in rec["qualifiers"] or []:
        p(f"  {q}")
    for t in ALL_TUNES:
        c, m = rec["catalog"][t], rec["classes"][t]
        p(f"{t}: qualifier {c['qualifier']} present={c['present']} complete={c['complete']}")
        if c["complete"]:
            p(f"  gxspl-NUsmall.xml sha256 {c['spline_sha256']} ({c['spline_bytes']} B)")
            p(f"  README sha256 {c['readme_sha256']}  version lines {c['readme_version_lines']}")
        p(f"  CMC {m['cmc']}: CCQE {m['ccqe']}  2p2h {m['2p2h']}  tune dirs {m.get('tune_dirs')}  problems {m['problems']}")
        for ln in m["lines"]:
            p(f"    {ln}")
    p("UPS table:")
    for ln in rec["ups"]:
        p(f"  {ln}")
    d = rec["decision"]
    p(f"spent classes: {d['spent_classes']}")
    p(f"status: {d['status']}")
    p(f"chosen: {d['chosen']}  fallback_taken {d['fallback_taken']}  02a==02b classes {d['02a_02b_same_classes']}")
    p(f"overlap with spent: {d['overlap_with_spent']}")
    p(f"controls: {d['controls']}")
    g = {k: v for k, v in rec["gpg"].items()}
    p(f"gpg: {g}")
    p(f"verdict {rec['verdict']}  stops {rec['stops']}")
    p("PG-PROBE-RESULT " + json.dumps(rec, sort_keys=True))


def main():
    rec = probe()
    report(rec)
    return 0 if rec["verdict"] == "GO" else 3


if __name__ == "__main__":
    sys.exit(main())
