#!/usr/bin/env python3
"""Check an SB1 admission record against this checkout, and write a job's ``--expect`` file.

    sb1_admit.py draft  --proposal launch/ADMISSION-PROPOSAL.json --authorization REL
                        --package-commit SHA --out ADM
    sb1_admit.py check  --admission ADM
    sb1_admit.py expect --admission ADM --hashes H0.json --omnifile PATH --out EXPECT.json

``draft`` fills only the mechanical fields of the committed proposal (status, the authorization's
path and digest, HEAD, this checkout, ``outroot = /pscratch/sd/j/josephrb/sb1-<HEAD[:8]>``) and then
runs ``check`` on the result; it chooses no parameter of the plan. It does not create the
authorization: that is a record of Joseph's decision, committed at HEAD before ``draft`` runs.

``check`` runs on a login node before ``launch/sb1_submit.sh`` submits anything; ``expect`` runs
at the start of every job. Both refuse (exit 3) unless:

* the record is an ``sb1-admission/1`` with ``status: ADMITTED`` (the committed proposal says
  ``PROPOSAL-NOT-AN-AUTHORIZATION`` and is always refused);
* its authorization names a committed ``AUTHORIZATION-``/``DECISION-`` record under
  ``docs/orchestration/`` by a repository-relative, normalized, non-symlinked path, with that
  record's sha256 (the rule of ``n2/harness.py`` ``check_admission`` lines 94-109, R2/F4 of the
  integration, restated here because it is inline in an N2-specific function);
* ``checkout`` is this repository, HEAD is ``code.commit``, tracked files are unmodified,
  ``code.package_commit`` is an ancestor of HEAD, and nothing under this package, the executed
  modules or the guard differs between ``code.package_commit`` and HEAD (so the bytes that run are
  the bytes that were reviewed, not whatever a later commit regenerated the manifest for);
* the authorization record's text names ``code.package_commit`` and the sha256 of
  ``manifest/expected-code.json`` in full;
* every file of ``manifest/expected-code.json`` (the executed modules, the guard and its shim,
  the launch scripts) has the stated sha256 at HEAD, and ``code.modules`` equals the manifest's;
* ``launch_spec_sha256`` is ``launch/launch-spec.json``'s, and every job's ceiling equals
  ``billing / 256 * time limit`` from that spec, summing to at most ``ceiling_node_h`` = 2.0;
* each input's size, mtime and inode equal ``inputs_observed`` (now, and in H0's record).

``expect`` writes ``{"commit", "modules", "inputs": {"omnifile", "mcfile"}}`` with the digests H0
measured; ``sb1_run.py`` then requires the same size, mtime and inode at its start and end.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
PKG_REL = HERE.relative_to(REPO).as_posix()
REFUSAL_EXIT = 3
OUTROOT_PREFIX = "/pscratch/sd/j/josephrb/sb1-"
NEED = ("schema", "status", "decision", "authorization", "checkout", "code", "launch_spec_sha256",
        "inputs_observed", "outroot", "ceiling_node_h", "jobs", "cannot_authorize")


class AdmissionError(RuntimeError):
    pass


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(*args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True,
                          env=env, check=True).stdout


def blob_sha256_at_head(rel):
    data = subprocess.run(["git", "-C", str(REPO), "show", f"HEAD:{rel}"], capture_output=True,
                          check=True).stdout
    return hashlib.sha256(data).hexdigest()


def authorization_path(rel, root=REPO):
    """The R2 rule: repository-relative, normalized, inside, not a symlink, correctly named."""
    top = Path(root).resolve()
    norm = "" if Path(rel).is_absolute() else os.path.normpath(rel).replace(os.sep, "/")
    if norm.startswith("../") or norm in ("", ".", "..") or (top / norm).resolve() != top / norm:
        norm = ""
    if not (norm.startswith("docs/orchestration/") and
            Path(norm).name.startswith(("AUTHORIZATION-", "DECISION-"))):
        raise AdmissionError(f"the authorization {rel!r} is not an AUTHORIZATION- or DECISION- "
                             "record under docs/orchestration/")
    return top / norm, norm


def seconds(hms):
    h, m, s = (int(x) for x in hms.split(":"))
    return 3600 * h + 60 * m + s


def spec_ceilings(spec):
    out = {}
    for job in spec["jobs"]:
        bill = 256 * job["nodes"] if job["qos"] == "regular" else job["cpus_per_task"]
        out[job["id"]] = bill / 256 * seconds(job["time"]) / 3600.0
    return out


def stat_of(path):
    st = os.stat(path)
    return {"size": st.st_size, "mtime_ns": st.st_mtime_ns, "ino": st.st_ino}


def check(adm_path):
    adm = json.loads(Path(adm_path).read_text())
    missing = [k for k in NEED if k not in adm]
    if missing:
        raise AdmissionError(f"admission record lacks {missing}")
    if adm["schema"] != "sb1-admission/1":
        raise AdmissionError(f"schema {adm['schema']!r}")
    if adm["status"] != "ADMITTED":
        raise AdmissionError(f"status {adm['status']!r}: only an ADMITTED record can launch SB1")
    auth, norm = authorization_path(str(adm["authorization"].get("path", "")))
    if not auth.is_file() or sha_file(auth) != adm["authorization"].get("sha256"):
        raise AdmissionError("the authorization record is absent or its digest differs")
    if blob_sha256_at_head(norm) != adm["authorization"]["sha256"]:
        raise AdmissionError("the authorization record is not committed at HEAD as stated")
    if Path(adm["checkout"]).resolve() != REPO.resolve():
        raise AdmissionError(f"the admitted checkout is {adm['checkout']}, not {REPO}")
    head = git("rev-parse", "HEAD").strip()
    if adm["code"].get("commit") != head:
        raise AdmissionError(f"admitted commit {adm['code'].get('commit')} is not HEAD {head}")
    if git("status", "--porcelain", "--untracked-files=no").strip():
        raise AdmissionError("tracked files differ from HEAD")
    pkg = adm["code"]["package_commit"]
    try:
        git("merge-base", "--is-ancestor", pkg, head)
    except subprocess.CalledProcessError:
        raise AdmissionError("the package commit is not an ancestor of HEAD") from None
    manifest = json.loads((HERE / "manifest" / "expected-code.json").read_text())
    bound = sorted({PKG_REL, *manifest["modules"], *manifest["guard"]})
    changed = git("diff", "--name-only", pkg, head, "--", *bound).split()
    if changed:
        raise AdmissionError(f"files bound to the package changed after {pkg[:12]}: {changed}")
    manifest_sha = sha_file(HERE / "manifest" / "expected-code.json")
    auth_text = auth.read_text()
    if pkg not in auth_text or manifest_sha not in auth_text:
        raise AdmissionError("the authorization record does not name the package commit and the "
                             "manifest's sha256 in full")
    for rel, want in {**manifest["modules"], **manifest["guard"], **manifest["launch"]}.items():
        if blob_sha256_at_head(rel) != want or sha_file(REPO / rel) != want:
            raise AdmissionError(f"{rel} is not the manifest's {want[:12]}")
    if adm["code"].get("modules") != manifest["modules"]:
        raise AdmissionError("the admitted modules are not the manifest's executed modules")
    spec_path = HERE / "launch" / "launch-spec.json"
    if sha_file(spec_path) != adm["launch_spec_sha256"]:
        raise AdmissionError("the launch spec differs from the admitted one")
    ceilings = spec_ceilings(json.loads(spec_path.read_text()))
    stated = {j["id"]: j["ceiling_node_h"] for j in adm["jobs"]}
    if set(stated) != set(ceilings) or any(abs(stated[k] - ceilings[k]) > 1e-9 for k in ceilings):
        raise AdmissionError(f"job ceilings {stated} are not the spec's {ceilings}")
    if adm["ceiling_node_h"] != 2.0 or sum(ceilings.values()) > adm["ceiling_node_h"]:
        raise AdmissionError("the plan's ceilings exceed the admitted 2.0 node-h")
    if not Path(adm["outroot"]).is_absolute():
        raise AdmissionError("outroot must be absolute")
    for path, want in adm["inputs_observed"].items():
        if stat_of(path) != {k: want[k] for k in ("size", "mtime_ns", "ino")}:
            raise AdmissionError(f"{path} no longer has the admitted size, mtime and inode")
    return adm


def expect(a):
    adm = check(a.admission)
    h0 = json.loads(Path(a.hashes).read_text())["files"]
    spec = json.loads((HERE / "launch" / "launch-spec.json").read_text())
    inputs = {}
    for key, path in (("omnifile", a.omnifile), ("mcfile", spec["inputs"]["mcfile"])):
        full = os.path.realpath(path)
        rec, want = h0.get(full), adm["inputs_observed"].get(full)
        if rec is None or want is None:
            raise AdmissionError(f"{full} is not an admitted, hashed input")
        if any(rec[k] != want[k] for k in ("size", "mtime_ns", "ino")):
            raise AdmissionError(f"{full}: H0 hashed a file other than the admitted one")
        inputs[key] = rec["sha256"]
    out = {"commit": adm["code"]["commit"], "modules": adm["code"]["modules"], "inputs": inputs,
           "note": f"written by {PKG_REL}/sb1_admit.py from {a.admission} and {a.hashes}"}
    with open(a.out, "x") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")


def draft(a):
    prop = json.loads(Path(a.proposal).read_text())
    if prop.get("status") != "PROPOSAL-NOT-AN-AUTHORIZATION":
        raise AdmissionError("draft starts from the committed proposal")
    auth, norm = authorization_path(a.authorization)
    head = git("rev-parse", "HEAD").strip()
    prop.update(status="ADMITTED", authorization={"path": norm, "sha256": sha_file(auth)},
                checkout=str(REPO.resolve()), outroot=f"{OUTROOT_PREFIX}{head[:8]}")
    prop["code"].update(commit=head, package_commit=a.package_commit)
    prop.pop("how_to_admit", None)
    with open(a.out, "x") as fh:
        json.dump(prop, fh, indent=1, sort_keys=True)
        fh.write("\n")
    check(a.out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    d = sp.add_parser("draft")
    d.add_argument("--proposal", required=True)
    d.add_argument("--authorization", required=True)
    d.add_argument("--package-commit", required=True)
    d.add_argument("--out", required=True)
    c = sp.add_parser("check")
    c.add_argument("--admission", required=True)
    e = sp.add_parser("expect")
    e.add_argument("--admission", required=True)
    e.add_argument("--hashes", required=True)
    e.add_argument("--omnifile", required=True)
    e.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "draft":
            draft(a)
            print(f"[sb1-admit] wrote {a.out}; admission holds")
        elif a.cmd == "check":
            check(a.admission)
            print("[sb1-admit] admission holds")
        else:
            expect(a)
            print(f"[sb1-admit] wrote {a.out}")
    except (AdmissionError, OSError, subprocess.CalledProcessError, KeyError, ValueError) as exc:
        print(f"[REFUSED] {type(exc).__name__}: {exc}", file=sys.stderr)
        return REFUSAL_EXIT
    return 0


if __name__ == "__main__":
    sys.exit(main())
