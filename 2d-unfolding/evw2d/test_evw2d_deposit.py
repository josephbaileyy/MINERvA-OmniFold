"""Controls for EVW2D's HPSS copy and deposit fetch (EVW2D BINDING 2): evw2d_hpss.sh, the Mac launcher
evw2d_deposit.sh and fill_deposit_pins.sh. Nothing reaches HPSS or a cluster: hsi, htar, hpssquota, ssh, scp and
ssh-keygen are stubs; HPSS is a temporary directory. The products are a small, real accepted set, and the checker is
the real evw2d.accepted() (numpy only).
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

EV = Path(__file__).resolve().parent
REPO = EV.parents[1]
LAUNCH = REPO / "docs/orchestration/state/2d-closeout/evw2d-20261124/launch"
CFG = "c" * 64
JOBID = "4242"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def stub(bin_: Path, name: str, body: str) -> None:
    (bin_ / name).write_text("#!/bin/bash\n" + body + "\n")
    (bin_ / name).chmod(0o755)


def git_repo(path: Path, files: dict) -> None:
    path.mkdir(parents=True)
    for rel, text in files.items():
        (path / rel).parent.mkdir(parents=True, exist_ok=True)
        (path / rel).write_bytes(text if isinstance(text, bytes) else text.encode())
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t")
    for cmd in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "x"]):
        subprocess.run(["git", "-C", str(path), *cmd], check=True, env=env, capture_output=True)


def products(out: Path, job: str = JOBID, cfg: str = CFG) -> str:
    """A small accepted product set in ``out``; returns the SHA256SUMS digest."""
    out.mkdir(parents=True)
    files = {"constants.json": b'{"c": 1}\n', "run.json": json.dumps({"config_sha256": cfg, "slurm_job": job}).encode(),
             "weights.npz": os.urandom(4096), "xsec.root": os.urandom(512)}
    for n, b in files.items():
        (out / n).write_bytes(b)
    (out / "SHA256SUMS").write_text("".join(f"{sha(out / n)}  {n}\n" for n in sorted(files)))
    s = sha(out / "SHA256SUMS")
    (out / "evw2d.done").write_text(json.dumps({"verdict": "PASS", "SHA256SUMS": s, "findings": []}) + "\n")
    return s


def fill(text: str, lane: Path, bound: str, **extra) -> str:
    for k, v in {"__LANE_ROOT__": str(lane), "__EVW2D_PY_SHA256__": sha(EV / "evw2d.py"), "__CONFIG_SHA256__": CFG,
                 "__PRODUCTS_SHA256SUMS_SHA256__": bound, "__JOB_ID__": JOBID, **extra}.items():
        text = text.replace(k, v)
    return text


# ------------------------------------------------------------------------------------------------ evw2d_hpss.sh

@pytest.fixture()
def hpss(tmp_path):
    """A lane after a passing post: out/ with an accepted product set, post.pass, deploy_M (the setup) and deploy_C
    (the real evw2d.py), a root_6_28 python3 under a fake HOME; stubs for hsi, htar and hpssquota over a temporary
    HPSS, and the script's /dev/shm retrieval directory mapped to a temporary one."""
    tmp = Path(os.path.realpath(tmp_path))
    lane = tmp / "evw2d-20261126"
    lane.mkdir()
    bound = products(lane / "out")
    (lane / "post.pass").write_text(f"job={JOBID}\nconfig_sha256={CFG}\nproducts_SHA256SUMS_sha256={bound}\n")
    home = tmp / "home"
    py = home / ".conda/envs/root_6_28/bin"
    py.mkdir(parents=True)
    stub(py, "python3", f'exec "{sys.executable}" "$@"')
    git_repo(lane / "deploy_M", {"setup_salloc_env.sh": f'export PATH="{py}:$PATH"\nreturn 0\n'})
    git_repo(lane / "deploy_C", {"2d-unfolding/evw2d/evw2d.py": (EV / "evw2d.py").read_bytes()})
    store, shm, b = tmp / "hpss", tmp / "shm", tmp / "bin"
    for d in (store, shm, b):
        d.mkdir()
    m = f'map() {{ printf "%s" "${{1/#\\/home\\/j\\/josephrb/{store}}}"; }}'
    stub(b, "hsi", m + '\nc="$2"; set -- $c\ncase "$1" in\n'
                   '  mkdir) mkdir -p "$(map "$3")";;\n'
                   '  ls) [ "$2" = -l ] && exit 0; [ -e "$(map "$2")" ];;\n'
                   '  hashcreate) exit ${HC_RC:-0};;\n'
                   '  hashverify) echo "hashverify: $2 OK"; exit ${HV_RC:-0};;\n'
                   '  *) exit 2;;\nesac')
    stub(b, "htar", m + '\nfor a; do case "$prev" in -cvf|-xf) T="$a";; -L) L="$a";; esac; prev="$a"; done\n'
                   'case " $* " in\n'
                   '  *" -cvf "*) [ -n "$HTAR_RC" ] && exit "$HTAR_RC"; tar cf "$(map "$T")" -T "$L" || exit 1\n'
                   '     [ -n "$HTAR_TOUCH" ] && printf " " >> "$(grep evw2d.done "$L")"; exit 0;;\n'
                   '  *" -xf "*) tar xf "$(map "$T")" || exit 1\n'
                   '     [ -n "$HTAR_CORRUPT" ] && printf x >> "$(find . -name xsec.root)"\n'
                   '     [ -n "$HTAR_EXTRA" ] && mkdir -p extra && echo e > extra/file; exit 0;;\n'
                   'esac')
    stub(b, "hpssquota", 'echo "HPSS usage 1 GiB"')
    stub(b, "sha256sum", 'a=(); for x; do [ "$x" = --strict ] || a+=("$x"); done; shasum -a 256 "${a[@]}"')
    env = dict(os.environ, PATH=f"{b}:{os.environ['PATH']}", HOME=str(home))

    def run(bound_pin=bound, edit=None, **e):
        text = fill((LAUNCH / "evw2d_hpss.sh").read_text(), lane, bound_pin)
        assert text.count("mktemp -d /dev/shm/jrb-evw2d-retrieve.XXXXXX") == 1
        text = text.replace("/dev/shm/", f"{shm}/")
        if edit:
            text = edit(text)
        f = tmp / "evw2d-hpss.copy"
        f.write_text(text)
        return subprocess.run(["bash", str(f), str(f)], capture_output=True, text=True, env=dict(env, **e))

    return {"lane": lane, "run": run, "bound": bound, "store": store, "shm": shm}


def _log(h) -> str:
    return (h["lane"] / "hpss" / "hpss.log").read_text()


def test_hpss_archives_retrieves_and_accepts(hpss):
    before = {p.name: sha(p) for p in (hpss["lane"] / "out").iterdir()}
    r = hpss["run"]()
    log = _log(hpss)
    assert r.returncode == 0, log
    assert (hpss["store"] / "mnv-evw2d-20261126" / "evw2d-20261126.tar").is_file()
    assert "retrieved and equal to their pins: 6 of 6; files retrieved: 6" in log
    assert "checker on scratch: ACCEPTED rc=0" in log and "checker on the retrieved copy: ACCEPTED rc=0" in log
    assert (hpss["lane"] / "hpss.tar.gz").is_file() and not (hpss["lane"] / "hpss.tar.gz.partial").exists()
    assert list(hpss["shm"].iterdir()) == [], "the retrieved copy was left"
    assert {p.name: sha(p) for p in (hpss["lane"] / "out").iterdir()} == before, "the products changed"
    assert (hpss["lane"] / "hpss" / "htar_files.txt").read_text().splitlines() == sorted(
        f"evw2d-20261126/out/{n}" for n in before)


def _refuses_before_writing(h, r, why):
    assert r.returncode == 9 and why in r.stdout and not (h["lane"] / "hpss").exists(), r.stdout


def test_hpss_needs_post_pass_for_this_job_config_and_products(hpss):
    pp = hpss["lane"] / "post.pass"
    good = pp.read_text()
    for bad in (good.replace(f"job={JOBID}", "job=4243"), good.replace(CFG, "d" * 64),
                good.replace(hpss["bound"], "e" * 64)):
        pp.write_text(bad)
        _refuses_before_writing(hpss, hpss["run"](), "post.pass does not name")
    pp.unlink()
    _refuses_before_writing(hpss, hpss["run"](), "no post.pass")


def test_hpss_needs_the_bound_manifest_and_the_approved_checker(hpss):
    _refuses_before_writing(hpss, hpss["run"](bound_pin="f" * 64), "post.pass does not name")
    sums = hpss["lane"] / "out" / "SHA256SUMS"
    sums.write_text(sums.read_text() + "\n")
    _refuses_before_writing(hpss, hpss["run"](), "SHA256SUMS is not the bound one")


def test_hpss_refuses_a_wrong_checker_a_linked_out_or_an_existing_receipt_dir(hpss):
    lane = hpss["lane"]
    w = lane / "deploy_C/2d-unfolding/evw2d/evw2d.py"
    good = w.read_bytes()
    w.write_bytes(good + b"\n")
    _refuses_before_writing(hpss, hpss["run"](), "the checker is not the approved bytes")
    w.write_bytes(good)
    (lane / "out").rename(lane / "out2")
    (lane / "out").symlink_to(lane / "out2")
    _refuses_before_writing(hpss, hpss["run"](), "is not a real directory")
    (lane / "out").unlink()
    (lane / "out2").rename(lane / "out")
    (lane / "hpss.tar.gz").write_text("x")
    _refuses_before_writing(hpss, hpss["run"](), "exists")


@pytest.mark.parametrize("pin", ["__LANE_ROOT__", "__JOB_ID__"])
def test_hpss_refuses_an_unfilled_pin(hpss, pin):
    r = hpss["run"](edit=lambda t: re.sub(r"^(LANE|JOBID)=.*$", lambda m: f"{m.group(1)}={pin}", t, flags=re.M))
    _refuses_before_writing(hpss, r, "a pin is not filled in")


def test_hpss_refuses_an_extra_entry_in_out(hpss):
    (hpss["lane"] / "out" / "stray.txt").write_text("s")
    r = hpss["run"]()
    log = _log(hpss)   # accepted()'s "present" check refuses it first; the listing check is the second line
    assert r.returncode == 1 and ("checker refused the products on scratch" in log or "outside the verified set" in log)
    assert not any(hpss["store"].rglob("*.tar")), "archived despite the stray file"


def test_hpss_refuses_products_bound_to_another_job(tmp_path, hpss):
    lane = hpss["lane"]
    shutil.rmtree(lane / "out")
    bound = products(lane / "out", job="999")
    (lane / "post.pass").write_text(f"job={JOBID}\nconfig_sha256={CFG}\nproducts_SHA256SUMS_sha256={bound}\n")
    r = hpss["run"](bound_pin=bound)
    assert r.returncode == 1 and "checker on scratch: REFUSED" in _log(hpss)
    assert not any(hpss["store"].rglob("*.tar"))


def test_hpss_refuses_products_bound_to_another_config(hpss):
    lane = hpss["lane"]
    shutil.rmtree(lane / "out")
    bound = products(lane / "out", cfg="d" * 64)
    (lane / "post.pass").write_text(f"job={JOBID}\nconfig_sha256={CFG}\nproducts_SHA256SUMS_sha256={bound}\n")
    r = hpss["run"](bound_pin=bound)
    assert r.returncode == 1 and "checker on scratch: REFUSED" in _log(hpss)


def test_hpss_fails_when_the_scratch_marker_changes_after_the_archive(hpss):
    r = hpss["run"](HTAR_TOUCH="1")
    log = _log(hpss)
    assert r.returncode == 1 and "the scratch evw2d.done changed during the archive" in log, log
    assert "checker on the retrieved copy: ACCEPTED" in log          # only the snapshot comparison sees it


def test_hpss_refuses_an_existing_archive_and_a_failed_htar(hpss):
    tar = hpss["store"] / "mnv-evw2d-20261126" / "evw2d-20261126.tar"
    tar.parent.mkdir(parents=True)
    tar.write_text("old")
    r = hpss["run"]()
    assert r.returncode == 1 and "exists" in _log(hpss) and tar.read_text() == "old"


def test_hpss_fails_on_a_failed_htar(hpss):
    r = hpss["run"](HTAR_RC="1")
    assert r.returncode == 1 and "htar rc 1" in _log(hpss)


@pytest.mark.parametrize("env,why", [({"HV_RC": "1"}, "hashverify rc=1"), ({"HC_RC": "1"}, "hashcreate rc=1"),
                                     ({"HTAR_CORRUPT": "1"}, "retrieved and equal to their pins: 5 of 6")])
def test_hpss_fails_on_a_hash_or_retrieval_miss(hpss, env, why):
    r = hpss["run"](**env)
    log = _log(hpss)
    assert r.returncode == 1 and why in log and "hpss rc=1" in log, log
    assert list(hpss["shm"].iterdir()) == [], "the retrieved copy was left"


def test_hpss_reports_unexpected_retrieved_files_and_removes_only_the_pinned_names(hpss):
    r = hpss["run"](HTAR_EXTRA="1")
    log = _log(hpss)
    assert r.returncode == 1 and "files retrieved: 7" in log and "left files" in log
    left = [p for p in hpss["shm"].rglob("*") if p.is_file()]
    assert [p.name for p in left] == ["file"], left       # only the unexpected file stays; no recursive removal


def test_hpss_removes_nothing_but_the_retrieved_pinned_names():
    text = (LAUNCH / "evw2d_hpss.sh").read_text()
    code = [ln.split("#", 1)[0] for ln in text.splitlines()]
    removals = [m.group(0).strip() for ln in code for m in re.finditer(r"\b(rm|rmdir|unlink|shred)\b[^;|&]*", ln)]
    assert removals == ['rm -f -- "$T/$n"', 'rmdir -- "$T/$R/out" "$T/$R" "$T"'], removals
    assert not any("rm -r" in ln or "-delete" in ln or "rm -f -- \"$T\"" in ln for ln in code)


# ----------------------------------------------------------------------------------------------- evw2d_deposit.sh

def _local(seconds: int) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() + seconds))


@pytest.fixture()
def deposit(tmp_path):
    """The deposit launcher in a checkout-like directory (a git repo holding the real evw2d.py), with a fake remote lane
    behind ssh and scp stubs, and ssh-keygen and ssh -G stubs for the certificate checks."""
    tmp = Path(os.path.realpath(tmp_path))
    top = tmp / "top"
    git_repo(top, {"2d-unfolding/evw2d/evw2d.py": (EV / "evw2d.py").read_bytes()})
    lane = tmp / "remote" / "evw2d-20261126"
    bound = products(lane / "out")
    ld = top / "launch"
    ld.mkdir()
    (ld / "evw2d_hpss.sh").write_text("#!/bin/bash\necho remote-hpss-ran\nexit 0\n")
    text = fill((LAUNCH / "evw2d_deposit.sh").read_text(), Path("/pscratch/sd/j/josephrb/evw2d-20261126"), bound,
                __HPSS_SHA256__=sha(ld / "evw2d_hpss.sh"))
    (ld / "evw2d_deposit.sh").write_text(text)
    shm, b = tmp / "shm", tmp / "stubbin"
    shm.mkdir()
    b.mkdir()
    rl = "/pscratch/sd/j/josephrb/evw2d-20261126"
    esc = rl.replace("/", "\\/")
    stub(b, "ssh", f'if [ "$1" = -G ]; then printf "identitiesonly yes\\nidentityfile {tmp / "key"}\\n'
                   f'certificatefile {tmp / "key-cert.pub"}\\n"; exit 0; fi\n'
                   f'echo "ssh $*" >> "{tmp / "ssh.calls"}"; [ -n "$SSH_RC" ] && exit "$SSH_RC"\n'
                   f'last="${{@: -1}}"; last="${{last//{esc}/{lane}}}"\nexec bash -c "${{last//\\/dev\\/shm/{shm}}}"')
    stub(b, "scp", f'[ -n "$SCP_RC" ] && exit "$SCP_RC"\nsrc="${{@: -2:1}}"; src="${{src#saul.nersc.gov:}}"\n'
                   f'cp "${{src/#{esc}/{lane}}}" "${{@: -1}}"')
    stub(b, "sha256sum", 'shasum -a 256 "$@"')
    stub(b, "ssh-keygen", f'[ "$TZ" = UTC ] || exit 3\necho "        Valid: from 2026-01-01T00:00:00 to '
                          f'${{CERT_TO:-{_local(6 * 3600)}}}"')
    env = dict(os.environ, PATH=f"{b}:{os.environ['PATH']}", EVW2D_CERT=str(tmp / "key-cert.pub"),
               EVW2D_PY=sys.executable)

    def run(*args, **e):
        return subprocess.run(["bash", str(ld / "evw2d_deposit.sh"), *map(str, args)], capture_output=True,
                              text=True, env=dict(env, **e))

    return {"tmp": tmp, "top": top, "ld": ld, "lane": lane, "run": run, "bound": bound, "shm": shm}


@pytest.fixture()
def home_dest():
    """A new empty directory under the real $HOME (fetch-products refuses temporary roots), removed afterwards."""
    d = Path(tempfile.mkdtemp(prefix=".evw2d-deposit-test-", dir=Path.home()))
    yield d
    shutil.rmtree(d)


pytestmark_mac = pytest.mark.skipif(sys.platform != "darwin", reason="the launcher runs on the Mac (BSD date -j)")


@pytestmark_mac
def test_fetch_products_copies_and_accepts_into_a_home_directory(deposit, home_dest):
    r = deposit["run"]("fetch-products", home_dest)
    assert r.returncode == 0 and "ACCEPTED" in r.stdout and "checker rc=0" in r.stdout, r.stdout + r.stderr
    got = {p.name: sha(p) for p in (home_dest / "out").iterdir()}
    assert got == {p.name: sha(p) for p in (deposit["lane"] / "out").iterdir()}


@pytestmark_mac
def test_fetch_products_refuses_temporary_or_non_empty_destinations(deposit):
    d = deposit["tmp"] / "dest"
    d.mkdir()
    r = deposit["run"]("fetch-products", d)                       # tmp_path is under /private/var
    assert r.returncode == 9 and "STOP" in r.stdout and not (deposit["tmp"] / "ssh.calls").exists(), r.stdout
    (d / "x").write_text("x")
    r = deposit["run"]("fetch-products", d)
    assert r.returncode == 9 and "not a new empty directory" in r.stdout


@pytestmark_mac
def test_fetch_products_refuses_a_wrong_local_checker(deposit, home_dest):
    w = deposit["top"] / "2d-unfolding/evw2d/evw2d.py"
    w.write_bytes(w.read_bytes() + b"\n")
    r = deposit["run"]("fetch-products", home_dest)
    assert r.returncode == 8 and "not the approved bytes" in r.stdout and not (home_dest / "out").exists()


@pytestmark_mac
def test_fetch_products_refuses_products_that_are_not_the_bound_ones(deposit, home_dest):
    out = deposit["lane"] / "out"
    shutil.rmtree(out)
    products(out)                                                # a different accepted set: another digest
    r = deposit["run"]("fetch-products", home_dest)
    assert r.returncode == 1 and "REFUSED" in r.stdout, r.stdout


@pytestmark_mac
@pytest.mark.parametrize("over", [{"job": "999"}, {"cfg": "d" * 64}])
def test_fetch_products_refuses_products_of_another_job_or_config(deposit, home_dest, over):
    out = deposit["lane"] / "out"
    shutil.rmtree(out)
    bound = products(out, **over)
    text = (deposit["ld"] / "evw2d_deposit.sh").read_text().replace(deposit["bound"], bound)
    (deposit["ld"] / "evw2d_deposit.sh").write_text(text)                     # the digest matches; the binding does not
    r = deposit["run"]("fetch-products", home_dest)
    assert r.returncode == 1 and "REFUSED" in r.stdout and '"pass": true' in r.stdout, r.stdout


@pytestmark_mac
def test_fetch_products_refuses_a_temporary_root_even_under_home(deposit):
    home = deposit["tmp"] / "home"
    (home / "dest").mkdir(parents=True)
    r = deposit["run"]("fetch-products", home / "dest", HOME=str(home))     # under HOME, but HOME is in /private/var
    assert r.returncode == 9 and "temporary root" in r.stdout, r.stdout


@pytestmark_mac
def test_fetch_products_refuses_a_directory_outside_home(deposit, home_dest):
    fake_home = home_dest / "h"
    fake_home.mkdir()
    dest = home_dest / "elsewhere"
    dest.mkdir()
    r = deposit["run"]("fetch-products", dest, HOME=str(fake_home))         # not a temporary root, not under HOME
    assert r.returncode == 9 and "not a directory under" in r.stdout, r.stdout


@pytestmark_mac
def test_deposit_hpss_needs_an_hour_of_certificate(deposit):
    s = deposit["tmp"] / "s1"
    s.mkdir()
    r = deposit["run"]("hpss", s, "login27", CERT_TO=_local(40 * 60))
    assert r.returncode == 7 and "expires too soon" in r.stdout and not (deposit["tmp"] / "ssh.calls").exists()


@pytestmark_mac
def test_fetch_products_stops_on_a_failed_copy(deposit, home_dest):
    r = deposit["run"]("fetch-products", home_dest, SCP_RC="1")
    assert r.returncode == 1 and "scp SHA256SUMS rc=1" in r.stdout and "ACCEPTED" not in r.stdout
    assert "scp evw2d.done" not in r.stdout and "checker rc" not in r.stdout     # it stops at the first failed copy


@pytestmark_mac
def test_deposit_hpss_runs_only_the_approved_bytes(deposit):
    s = deposit["tmp"] / "s1"
    s.mkdir()
    r = deposit["run"]("hpss", s, "login27")
    assert r.returncode == 0 and "remote-hpss-ran" in r.stdout and "script rc=0" in r.stdout, r.stdout + r.stderr
    assert list(deposit["shm"].iterdir()) == [], "the staged copy was left"
    (deposit["ld"] / "evw2d_hpss.sh").write_text("#!/bin/bash\nexit 0\n")
    s2 = deposit["tmp"] / "s2"
    s2.mkdir()
    r = deposit["run"]("hpss", s2, "login27")
    assert r.returncode == 8 and "not the approved one" in r.stdout


@pytestmark_mac
def test_deposit_fetch_tells_absent_from_unreachable(deposit):
    def fetch(**e):
        d = deposit["tmp"] / f"f{len(list(deposit['tmp'].glob('f*')))}"
        d.mkdir()
        return deposit["run"]("fetch", d, **e), d
    r, d = fetch()
    assert r.returncode == 4 and "hpss.tar.gz absent" in r.stdout
    (deposit["lane"] / "hpss.tar.gz").write_bytes(b"h")
    r, d = fetch()
    assert r.returncode == 0 and (d / "hpss.tar.gz").read_bytes() == b"h"
    r, d = fetch(SSH_RC="255")
    assert r.returncode == 255 and "could not ask saul" in r.stdout


def test_deposit_refuses_unfilled_pins(tmp_path):
    d = Path(os.path.realpath(tmp_path)) / "s"
    d.mkdir()
    r = subprocess.run(["bash", str(LAUNCH / "evw2d_deposit.sh"), "fetch", str(d)], capture_output=True, text=True)
    assert r.returncode == 9 and "a pin is not filled in" in r.stdout


# ------------------------------------------------------------------------------------------ fill_deposit_pins.sh

RD = "docs/orchestration/state/2d-closeout/evw2d-20261124/receipts/run-test"


def _fill_tree(tmp: Path, accepted_edit=None) -> Path:
    top = tmp / "top"
    rel = LAUNCH.relative_to(REPO)
    lane = "/pscratch/sd/j/josephrb/evw2d-20261126"
    files = {"2d-unfolding/evw2d/evw2d.py": (EV / "evw2d.py").read_bytes()}
    for f in ("evw2d_hpss.sh", "evw2d_deposit.sh", "fill_deposit_pins.sh"):
        files[f"{rel}/{f}"] = (LAUNCH / f).read_bytes()
    files[f"{rel}/bound/PINS.txt"] = (f"tool commit        {'1' * 40}\nlane root          {lane}\n"
                                      f"evw2d.py           {sha(EV / 'evw2d.py')}\nconfig.json        {CFG}\n")
    work = tmp / "work"
    bound = products(work / "out")
    files[f"{RD}/post/out/SHA256SUMS"] = (work / "out" / "SHA256SUMS").read_bytes()
    files[f"{RD}/post/logs/evw2d.jobid"] = f"{JOBID}\n"
    acc = {"pass": True, "config_bound": True, "job_bound": True, "run_config_sha256": CFG, "run_slurm_job": JOBID,
           "done": {"verdict": "PASS", "SHA256SUMS": bound}}
    if accepted_edit:
        accepted_edit(acc)
    files[f"{RD}/post/accepted.json"] = json.dumps(acc)
    files[f"{RD}/post/post.log"] = f"SHA256SUMS sha256 {bound}\nPOST: accounting=true PASS=true\n"
    git_repo(top, files)
    return top


def test_fill_deposit_pins_writes_every_pin_from_the_receipts(tmp_path):
    tmp = Path(os.path.realpath(tmp_path))
    top = _fill_tree(tmp)
    ld = top / LAUNCH.relative_to(REPO)
    r = subprocess.run(["bash", str(ld / "fill_deposit_pins.sh"), RD], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    b = ld / "bound-deposit"
    pins = dict(re.match(r"(.+?)\s{2,}(\S+)$", ln).groups() for ln in (b / "PINS.txt").read_text().splitlines())
    bound = sha(top / RD / "post/out/SHA256SUMS")
    assert pins["products SHA256SUMS"] == bound and pins["job"] == JOBID and pins["config.json"] == CFG
    assert pins["evw2d_hpss.sh"] == sha(b / "evw2d_hpss.sh") and pins["evw2d_deposit.sh"] == sha(b / "evw2d_deposit.sh")
    dep = (b / "evw2d_deposit.sh").read_text()
    assert f"SHA={pins['evw2d_hpss.sh']};" in dep and f"BOUND={bound}\n" in dep and f"JOBID={JOBID}\n" in dep
    for f in ("evw2d_hpss.sh", "evw2d_deposit.sh"):
        assert not re.search(r"__[A-Z0-9_]*__", (b / f).read_text()), f


@pytest.mark.parametrize("edit", [lambda a: a.update(run_slurm_job="999"), lambda a: a.update(job_bound=False),
                                  lambda a: a["done"].update(SHA256SUMS="0" * 64), lambda a: a.update({"pass": False})])
def test_fill_deposit_pins_refuses_receipts_that_disagree(tmp_path, edit):
    tmp = Path(os.path.realpath(tmp_path))
    top = _fill_tree(tmp, edit)
    ld = top / LAUNCH.relative_to(REPO)
    r = subprocess.run(["bash", str(ld / "fill_deposit_pins.sh"), RD], capture_output=True, text=True)
    assert r.returncode != 0 and not (ld / "bound-deposit").exists(), r.stdout + r.stderr


def test_fill_deposit_pins_refuses_uncommitted_receipts_or_another_evw2d(tmp_path):
    tmp = Path(os.path.realpath(tmp_path))
    top = _fill_tree(tmp)
    ld = top / LAUNCH.relative_to(REPO)
    (top / RD / "post/logs/evw2d.jobid").write_text("4243\n")
    r = subprocess.run(["bash", str(ld / "fill_deposit_pins.sh"), RD], capture_output=True, text=True)
    assert r.returncode != 0 and "differ from HEAD" in r.stdout and not (ld / "bound-deposit").exists()
    subprocess.run(["git", "-C", str(top), "checkout", "-q", "--", RD], check=True)
    (top / "2d-unfolding/evw2d/evw2d.py").write_text("x")
    r = subprocess.run(["bash", str(ld / "fill_deposit_pins.sh"), RD], capture_output=True, text=True)
    assert r.returncode != 0 and "not the bound one" in r.stdout


def test_every_deposit_script_parses():
    for f in ("evw2d_hpss.sh", "evw2d_deposit.sh", "fill_deposit_pins.sh"):
        r = subprocess.run(["bash", "-n", str(LAUNCH / f)], capture_output=True, text=True)
        assert r.returncode == 0, (f, r.stderr)
