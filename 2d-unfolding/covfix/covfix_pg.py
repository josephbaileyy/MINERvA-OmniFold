"""COVFIX PG's bound binary (COVFIX-DECLARATION.md rev 11.4 section 4.2; COVFIX-BINDING-1 ruling 4). It runs on one
exclusive node under the director's wrapper (JE's round-3 contract), and is the only PG code that touches the
passphrase, which it hands to gpg on fd 3.

  covfix_pg.py --covfix-attempt <32 hex> --workdir <empty dir> --sealed <new dir, disjoint from it>
               --gen-spec <json> --gen-spec-sha256 <64 hex> --gpg <absolute path> --gpgconf <absolute path>
               --gpg-sha256 <64 hex> --gpgconf-sha256 <64 hex>  < frame

  stdin       exactly "<passphrase, 64 hex>\\n<seed base, 10 digits>\\n" (76 bytes), then EOF
  gen-spec    {"command": [absolute path, args...], "command_sha256": "<64 hex>", "tunes": [u=0 name, u=1 name],
               "env_keep": [variable names the generator needs from the site], "env_set": {name: literal value},
               "required": [{"pattern": <glob relative to W>, "count": <n>}, ...]}. Each required pattern must match exactly n regular files under W after the run
               (fnmatch, '*' crossing '/'), or the run fails with no receipt. The command path is resolved once, hashed, launched
              by that resolved path and hashed again after the run; a change is a role failure. RESIDUAL WINDOW (disclosed,
              the director's ruling R2): a replacement written by this same account between the hash and the exec,
              and restored before the re-hash, would not be seen; section 4.2's cooperative assumption covers it.
              The gen-spec, re-serialized, must name no task seed (the director's 2026-11-25 ruling), or the run is
              refused before anything runs.
              Its bytes are pinned by --gen-spec-sha256 (the binding; the director's ruling (ii) of 2026-11-25): the
              file is read once, and those bytes are hashed and parsed, so command_sha256, env_keep and the required
              inventory are all pinned. Every env_keep name must be set in this process's environment and none may
              be listed twice (ruling (i)); a variable that is optional is not listed. env_set's literal values
              (ruling (iii): PG_DEPLOY_PIN and any other value the generator's correctness depends on) are set in
              the generator's environment, so the pin covers them; an inherited different value refuses, and
              env_set may name neither TMPDIR nor an env_keep name. env_keep holds only what must come from the
              site (the Slurm names, HOME). Each failure, like any malformed value, refuses before the job check,
              with W untouched.
  gpg         gpg and gpgconf are pinned by sha256 (the binding) and hashed before every exec (ruling R1)
  job check   the step check below, run once before anything else runs: the wrapper runs pg-connect on its host with
              no allocation of its own, so a sealer outside a Slurm job, or with another process already in its
              job, is refused before the generator starts and writes nothing to W (step_cgroup_pre)
  before      a synthetic gpg round trip with the pinned gpg and the real passphrase
  generation  <resolved command...> --workdir W --seeds W/seeds.json, with cwd W, stdin /dev/null, stdout and stderr
              into W/capture/, a scrubbed environment (env_keep's variables, env_set's values, TMPDIR = W/tmp at
              mode 0700, which pg_generate.sh requires), in its own process group, which is killed and reaped on any
              failure or SIGTERM
  products    W/PRODUCTS.json: a non-empty JSON list of distinct safe relpaths of regular files under W; and the
              gen-spec's required inventory, every pattern at its exact count
  step check  just before the seal, the sealer reads its cgroup (v2: /proc/self/cgroup), finds its Slurm job_<id>
              cgroup, and reads cgroup.procs in every directory of that job's subtree: every step (a background srun,
              an --overlap step), step_extern (where pam_slurm_adopt puts an ssh session), every task and every
              nested cgroup. It refuses to seal if any pid there is other than its own and its contiguous ancestor
              chain (the wrapper that launched it; a slurmstepd only if it is in that chain). A generator descendant
              that called setsid escapes the process group but not the job's cgroups, so it is caught. Any
              unreadable directory, a cgroup that is not a single v2 entry or not under one job_<id>, is a STOP. A
              refusal records each other process's cgroup path, pid, comm and exe (step_cgroup_inventory). The
              escape itself is disclosed, not prevented (the director's ruling on round 3's item 7): section 4.2's
              same-account cooperative assumption covers F1's bound pipeline, which never detaches. An inventory exe
              under W, the sealed dir or $SCRATCH is recorded as a fixed token (<workdir>, <sealed>, <scratch>).
  seal        every file under W under opaque ids (covfix_seal.seal), then W's plaintext deleted and W verified empty
  spill scan  every entry created or changed (a file's ctime included) during the run at any depth under $SCRATCH/tmp (setup_salloc_env.sh exports
              TMPDIR=$SCRATCH/tmp), and the sealed dir, checked for a plaintext hash; the scratch files also for any
              task seed or any plaintext hash's hex (either case) in their name or bytes: a hash of a seed-bearing
              file is seed-bearing (the director's 2026-11-25 ruling), so a sums file there is a spill. A scratch hit
              is removed, its removal verified, and it fails the run. An entry that cannot be read is a hit; a
              directory that cannot be listed fails the run; neither stops the scan. The trap stays armed until every
              hit's removal is verified.
  final       the sealed dir checked against its own PG-SEAL.sha256 (covfix_seal.seal_check)

THE SEED ALIAS (the director's ruling of 2026-11-24 on B1): task (u=0, i=0)'s seed IS the seed base. It is present
inside W only: in W/seeds.json, in that task's gevgen argv and in its logs, all sealed and then deleted. The spill scan
treats it like every task seed. The summary carries "seed_alias" to say so.

Exits, per the wrapper's contract:
  0   everything above clean; stdout ends with "covfix-receipt <attempt>"
  66  a confirmed integrity break (a round-trip mismatch, or the final seal check); stdout ends "covfix-break <attempt>"
  1   anything else: a refusal, a failed generation, a spill, an unexpected error, or SIGTERM; no receipt
  2   bad arguments (argparse)
Stdout carries one JSON summary of fixed codes, booleans and counts, and the final line. It never carries a secret, a
seed, a plaintext hash, a work-dir name, a physics value or an exception's text. The summary leaves W, so before it is
printed it is scanned for every task seed and every plaintext hash's hex (leak_guard). A hit reduces the inventory to
its count, or, if the summary still hits, replaces it with a fixed refusal; it is marked "summary_leak_redacted" and
the run exits 1 (66 stays 66).

MEASURES: nothing. CANNOT AUTHORIZE: a connect; PG runs only under its binding addendum.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import shutil
import signal
import stat
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import covfix_seal as cs  # noqa: E402

ATTEMPT = re.compile(r"[0-9a-f]{32}")
SPEC_KEYS = {"command", "command_sha256", "tunes", "env_keep", "env_set", "required"}
ENV_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
PROC, CGROUP_ROOT = "/proc", "/sys/fs/cgroup"
JOB_CGROUP = re.compile(r"job_[0-9]+")
HEX_WINDOW = re.compile(rb"(?=([0-9A-Fa-f]{64}))")             # every 64-hex window, overlapping, either case
LEAK_REFUSAL = "the summary named a task seed or a plaintext hash"
SYNTHETIC = b"covfix-pg synthetic round trip"
PG_OWNED = ("capture", "tmp", "seeds.json", "PRODUCTS.json")   # PG's own files under W: never a physics product
GROUP_WAIT_S = 30
SEED_ALIAS = ("task (u=0, i=0) = the seed base: present inside W only (W/seeds.json, that task's gevgen argv and logs), "
              "sealed and deleted; the spill scan treats it like every task seed")


def file_sha256(path: str) -> str:
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError as e:
        raise cs.Refusal("the generator command cannot be read") from e


def load_spec(path: Path, sha256: str) -> dict:
    try:
        raw = Path(path).read_bytes()                # read once: the bytes hashed are the bytes parsed
    except OSError as e:
        raise cs.Refusal("the gen-spec cannot be read") from e
    if hashlib.sha256(raw).hexdigest() != sha256:
        raise cs.Refusal("the gen-spec's sha256 is not its pin")
    try:
        spec = json.loads(raw)
    except ValueError as e:
        raise cs.Refusal("the gen-spec cannot be read") from e
    if not isinstance(spec, dict) or set(spec) != SPEC_KEYS:
        raise cs.Refusal("the gen-spec must have exactly its six keys")
    ok = (isinstance(spec["command"], list) and spec["command"] and all(isinstance(a, str) for a in spec["command"])
          and os.path.isabs(spec["command"][0])
          and isinstance(spec["command_sha256"], str) and cs.HEX64.fullmatch(spec["command_sha256"])
          and isinstance(spec["tunes"], list) and len(spec["tunes"]) == 2
          and all(isinstance(t, str) and t for t in spec["tunes"])
          and isinstance(spec["env_keep"], list) and all(isinstance(v, str) for v in spec["env_keep"])
          and "TMPDIR" not in spec["env_keep"] and _required_ok(spec["required"])
          and isinstance(spec["env_set"], dict)
          and all(ENV_NAME.fullmatch(k) for k in spec["env_set"])
          and all(isinstance(v, str) and "\0" not in v for v in spec["env_set"].values())
          and "TMPDIR" not in spec["env_set"] and not set(spec["env_set"]) & set(spec["env_keep"]))
    if not ok:
        raise cs.Refusal("the gen-spec's values are malformed")
    if len(set(spec["env_keep"])) != len(spec["env_keep"]):
        raise cs.Refusal("an env_keep variable is listed twice")
    if not all(k in os.environ for k in spec["env_keep"]):
        raise cs.Refusal("an env_keep variable is not set")
    if any(os.environ.get(k, v) != v for k, v in spec["env_set"].items()):
        raise cs.Refusal("an env_set variable is inherited with a different value")
    resolved = os.path.realpath(spec["command"][0])
    if file_sha256(resolved) != spec["command_sha256"]:
        raise cs.Refusal("the generator command's sha256 is not the gen-spec's")
    return dict(spec, resolved=resolved)


def _required_ok(req) -> bool:
    """A non-empty list of distinct {"pattern": relative glob, "count": n >= 1}."""
    return isinstance(req, list) and bool(req) and all(
        isinstance(r, dict) and set(r) == {"pattern", "count"} and isinstance(r["pattern"], str) and r["pattern"]
        and not r["pattern"].startswith("/") and ".." not in r["pattern"].split("/") and "\x00" not in r["pattern"]
        and type(r["count"]) is int and r["count"] >= 1 for r in req) and len({r["pattern"] for r in req}) == len(req)


def required_present(workdir: Path, req: list) -> bool:
    """Every required pattern matches exactly its count of regular files under W (never following a link)."""
    rels = []
    for dirpath, _dirs, files in os.walk(workdir, followlinks=False):
        for f in files:
            p = os.path.join(dirpath, f)
            if stat.S_ISREG(os.lstat(p).st_mode):
                rels.append(os.path.relpath(p, workdir))
    return all(sum(fnmatch.fnmatchcase(r, q["pattern"]) for r in rels) == q["count"] for q in req)


def _ppid(pid: int) -> int:
    text = Path(PROC, str(pid), "stat").read_text()
    return int(text[text.rindex(")") + 1:].split()[1])


class StepRefusal(cs.Refusal):
    """The step check's STOP, with the inventory of every other process in the job's cgroups:
    [{"cgroup": its path under job_<id>, "pid", "comm", "exe"}] (comm or exe None where unreadable)."""

    def __init__(self, message: str, inventory: list):
        super().__init__(message)
        self.inventory = inventory


def _proc_field(pid: int, name: str) -> str | None:
    try:
        p = Path(PROC, str(pid), name)
        return os.readlink(p) if name == "exe" else p.read_text().strip()
    except OSError:
        return None


def _raise(e: OSError):
    raise e


def step_cgroup_check() -> dict:
    """Refuse to seal if any cgroup of the sealer's Slurm job (the whole job_<id> subtree: every step, step_extern,
    every task, every nested cgroup) holds a pid other than the sealer's own and its contiguous ancestor chain.
    Returns the counts (for the rehearsal's record): {"pids": all in the job, "ancestors": those of the chain}."""
    me = os.getpid()
    try:
        lines = Path(PROC, "self", "cgroup").read_text().splitlines()
        if len(lines) != 1 or not lines[0].startswith("0::/"):
            raise cs.Refusal("the step's cgroup is not a single cgroup v2 entry (a STOP)")
        parts = lines[0][4:].split("/")
        jobs = [i for i, c in enumerate(parts) if JOB_CGROUP.fullmatch(c)]
        if len(jobs) != 1:
            raise cs.Refusal("the sealer's cgroup is not under exactly one Slurm job_<id> cgroup (a STOP)")
        job = Path(CGROUP_ROOT, *parts[:jobs[0] + 1])
        where: dict = {}
        for dirpath, _dirs, _files in os.walk(job, onerror=_raise, followlinks=False):
            for x in Path(dirpath, "cgroup.procs").read_text().split():
                where[int(x)] = os.path.relpath(dirpath, job)
        if me not in where:
            raise cs.Refusal("the sealer is not in its job's cgroups (a STOP)")
        allowed, pid = {me}, me
        while True:
            pid = _ppid(pid)
            if pid not in where or pid in allowed:
                break
            allowed.add(pid)
    except (OSError, ValueError) as e:
        raise cs.Refusal("the job's cgroups cannot be read (a STOP)") from e
    extra = sorted(set(where) - allowed, key=lambda q: (where[q], q))
    if extra:
        raise StepRefusal("a process outside PG's own chain is in its job's cgroups: no seal",
                          [{"cgroup": where[q], "pid": q, "comm": _proc_field(q, "comm"),
                            "exe": _proc_field(q, "exe")} for q in extra])
    return {"pids": len(where), "ancestors": len(allowed) - 1}


def prepare(workdir: Path, sealed: Path) -> tuple[Path, Path]:
    if not workdir.is_dir() or any(workdir.iterdir()):
        raise cs.Refusal("the work dir must exist and be empty")
    if os.path.lexists(sealed):
        raise cs.Refusal("the sealed dir must not exist")
    w = Path(os.path.realpath(workdir))
    s = Path(os.path.realpath(sealed.parent)) / sealed.name
    if cs._inside(str(s), str(w)) or cs._inside(str(w), str(s)):
        raise cs.Refusal("the sealed dir and the work dir must be disjoint")
    return w, s


# ------------------------------------------------------------------------------------------------ scratch spills
def scratch_tmp() -> Path | None:
    s = os.environ.get("SCRATCH")
    return Path(s) / "tmp" if s else None


def _sig(st: os.stat_result, path: str) -> tuple:
    if stat.S_ISLNK(st.st_mode):
        return ("l", st.st_ino, os.readlink(path))
    if stat.S_ISDIR(st.st_mode):
        return ("d", st.st_ino)
    if stat.S_ISREG(st.st_mode):
        return ("f", st.st_ino, st.st_mtime_ns, st.st_ctime_ns, st.st_size)
    return ("o", st.st_ino, st.st_mode)


def snapshot(root: Path | None, errors: list | None = None) -> dict:
    """{relpath: signature} of every entry under root at any depth (files, directories, links and special entries,
    never followed). A walk or lstat error refuses, or, given `errors`, is appended there and the walk goes on."""
    out = {}
    if root is None or not root.is_dir():
        return out
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False,
                                                onerror=cs._raise if errors is None else errors.append):
        for name in dirnames + filenames:
            p = os.path.join(dirpath, name)
            try:
                out[os.path.relpath(p, root)] = _sig(os.lstat(p), p)
            except OSError as e:
                if errors is None:
                    raise
                errors.append(e)
    return out


def changed(root: Path | None, before: dict, errors: list | None = None) -> list[tuple[str, tuple, bool]]:
    """(relpath, signature, new) for every entry created or changed since `before`."""
    after = snapshot(root, errors)
    return [(rel, sig, rel not in before) for rel, sig in sorted(after.items()) if before.get(rel) != sig]


def names_a_secret(data: bytes, seeds: list[bytes], hashes: set[str]) -> bool:
    """Whether bytes carry a task seed (decimal) or the hex of a plaintext sha256, in either case. A seed-bearing
    file's hash is itself seed-bearing: the seed space can be searched against it (the director's 2026-11-25 ruling)."""
    return any(sd in data for sd in seeds) or (bool(hashes) and any(
        m.group(1).lower().decode() in hashes for m in HEX_WINDOW.finditer(data)))


def spill_hits(root: Path, entries: list, hashes: set[str], seeds: list[bytes]) -> list[tuple[str, tuple, bool]]:
    """Entries carrying a task seed or a plaintext hash's hex anywhere in their relative path (or, for a link, its
    target), or a regular file whose sha256 is a plaintext hash or whose bytes carry a task seed or a plaintext hash's
    hex (a sums file). A file that cannot be read is a hit."""
    hits = []
    for rel, sig, new in entries:
        text = os.fsencode(rel) + (b"\x00" + os.fsencode(sig[2]) if sig[0] == "l" else b"")
        hit = names_a_secret(text, seeds, hashes)
        if not hit and sig[0] == "f":
            try:
                data = cs.noatime_read(root / rel)
                hit = hashlib.sha256(data).hexdigest() in hashes or names_a_secret(data, seeds, hashes)
            except OSError:
                hit = True                             # unverifiable: removed, and it fails the run
        if hit:
            hits.append((rel, sig, new))
    return hits


def remove_verified(root: Path, hits: list) -> bool:
    """Remove each hit (a new directory with its contents; an existing directory is never removed, and fails the
    check), deepest first, never following a link; True only if every hit is gone."""
    ok = True
    for rel, sig, new in sorted(hits, key=lambda h: h[0].count("/"), reverse=True):
        p = root / rel
        try:
            if sig[0] == "d":
                if not new:
                    ok = False
                    continue
                shutil.rmtree(p)
            else:
                os.unlink(p)
        except FileNotFoundError:
            pass
        except OSError:
            ok = False
    return ok and not any(os.path.lexists(root / rel) for rel, _, _ in hits)


def plaintext_hashes(workdir: Path) -> set[str]:
    """For the trap: the hashes of W's regular files, never following or refusing on a link (the trap must not stop)."""
    return {hashlib.sha256(cs.noatime_read(p)).hexdigest() for p in cs._regular_files(workdir)}


# ---------------------------------------------------------------------------------------------------- generation
def private_dir(path: Path) -> None:
    """A new directory at mode 0700 whatever the umask: pg_generate.sh refuses a W/tmp that is not (its contract)."""
    os.mkdir(path, 0o700)
    os.chmod(path, 0o700)


class Generator:
    def __init__(self):
        self.proc = None

    def run(self, spec: dict, workdir: Path, seeds: dict) -> int:
        (workdir / "capture").mkdir()
        private_dir(workdir / "tmp")
        (workdir / "seeds.json").write_text(json.dumps(seeds, sort_keys=True))
        env = {k: os.environ[k] for k in spec["env_keep"] if k in os.environ}
        env.update(spec["env_set"])
        env["TMPDIR"] = str(workdir / "tmp")
        with open(workdir / "capture" / "stdout.log", "xb") as fo, open(workdir / "capture" / "stderr.log", "xb") as fe:
            self.proc = subprocess.Popen([spec["resolved"], *spec["command"][1:], "--workdir", str(workdir),
                                          "--seeds", str(workdir / "seeds.json")], cwd=workdir, env=env,
                                         stdin=subprocess.DEVNULL, stdout=fo, stderr=fe, close_fds=True,
                                         start_new_session=True)
            rc = self.proc.wait()
            end_group(self.proc.pid)
        self.proc = None
        (workdir / "capture" / "rc.txt").write_text(f"{rc}\n")
        return rc

    def kill(self) -> None:
        if self.proc is not None:
            try:
                os.killpg(self.proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            self.proc.wait()
            end_group(self.proc.pid)


def end_group(pgid: int) -> None:
    """Kill the generator's process group (the leader and every descendant that kept it) and confirm it is gone, so
    nothing writes after the seal starts; refuses if the group outlives GROUP_WAIT_S."""
    deadline = time.monotonic() + GROUP_WAIT_S
    while True:
        try:
            os.killpg(pgid, signal.SIGKILL)
        except ProcessLookupError:
            return
        except PermissionError:
            pass
        if time.monotonic() > deadline:
            raise cs.Refusal("the generator's process group did not end")
        time.sleep(0.05)


def products_ok(workdir: Path) -> bool:
    try:
        lst = json.loads((workdir / "PRODUCTS.json").read_text())
    except (OSError, ValueError):
        return False
    if not (isinstance(lst, list) and lst and all(isinstance(p, str) for p in lst) and len(set(lst)) == len(lst)):
        return False
    for p in lst:
        q = workdir / p
        if not cs._safe_rel(p) or p.split("/")[0] in PG_OWNED or not os.path.lexists(q) \
                or not stat.S_ISREG(os.lstat(q).st_mode):
            return False
    return True


# ----------------------------------------------------------------------------------------------------------- run
def exe_token(exe: str | None, workdir: Path, sealed: Path) -> str | None:
    """An inventory exe under W, the sealed dir or $SCRATCH is recorded as that root's fixed token, never its path."""
    for token, root in (("<workdir>", workdir), ("<sealed>", sealed), ("<scratch>", os.environ.get("SCRATCH"))):
        if exe is not None and root and cs._inside(exe, str(root)):
            return token
    return exe


def leak_guard(rc: int, summary: dict, seeds: list[bytes], hashes: set[str]) -> tuple[int, dict]:
    """The summary leaves W, so it is scanned for every task seed and every plaintext hash's hex. On a hit the
    inventory (whose comm and exe are strings a process chooses) is reduced to its count; if the summary still hits,
    it is replaced by a fixed one. Either way it is marked "summary_leak_redacted" and the run fails (a break stays
    a break)."""
    def hit(s):
        return names_a_secret(json.dumps(s, sort_keys=True).encode(), seeds, hashes)
    if not hit(summary):
        return rc, summary
    out = dict(summary)
    if isinstance(out.get("step_cgroup_inventory"), list):
        out["step_cgroup_inventory"] = len(out["step_cgroup_inventory"])
    if hit(out):
        out = {"refused": LEAK_REFUSAL}
    out["summary_leak_redacted"] = True
    return (rc if rc == cs.BREAK_RC else 1), out


def run(workdir: Path, sealed: Path, spec_path: Path, spec_sha256: str, frame: bytes,
        tools: cs.Tools) -> tuple[int, dict]:
    """(exit code, summary). The summary holds fixed codes, booleans and counts only, and passes the leak guard."""
    seen: dict = {"seeds": [], "hashes": set()}
    rc, summary = _run(workdir, sealed, spec_path, spec_sha256, frame, tools, seen)
    return leak_guard(rc, summary, seen["seeds"], seen["hashes"])


def _run(workdir: Path, sealed: Path, spec_path: Path, spec_sha256: str, frame: bytes, tools: cs.Tools,
         seen: dict) -> tuple[int, dict]:
    summary = {"frame_ok": False, "spec_ok": False, "seed_alias": SEED_ALIAS}
    gen = Generator()
    started, stmp, before, seeds_b, known = False, None, {}, [], set()
    try:
        passphrase, base = cs.read_frame(frame, with_seed=True)
        summary["frame_ok"] = True
        spec = load_spec(spec_path, spec_sha256)
        summary["spec_ok"] = True
        workdir, sealed = prepare(workdir, sealed)
        seeds = cs.task_seeds(base, spec["tunes"])
        seeds_b = seen["seeds"] = [str(s).encode() for t in seeds["tunes"] for s in t["task_seeds"]]
        if names_a_secret(json.dumps(spec, sort_keys=True).encode(), seeds_b, set()):
            raise cs.Refusal("the gen-spec names a task seed")
        summary["step_cgroup_pre"] = step_cgroup_check()
        if cs.gpg_run(cs.GPG_DECRYPT, passphrase, cs.gpg_run(cs.GPG_ENCRYPT, passphrase, SYNTHETIC, tools),
                      tools) != SYNTHETIC:
            raise cs.Refusal("the synthetic gpg round trip failed")
        summary["synthetic_round_trip"] = True
        stmp = scratch_tmp()
        if stmp is None:
            raise cs.Refusal("SCRATCH is not set, so the spill scan cannot cover $SCRATCH/tmp")
        before = snapshot(stmp)
        started = True
        rc = gen.run(spec, workdir, seeds)
        summary["generation_rc0"] = rc == 0
        summary["command_unchanged"] = file_sha256(spec["resolved"]) == spec["command_sha256"]
        summary["products_json"] = products_ok(workdir)
        summary["required_products"] = required_present(workdir, spec["required"])
        summary["step_cgroup"] = step_cgroup_check()
        s = cs.seal(workdir, sealed, passphrase, tools)
        known = set(s["hashes"].values())
        seen["hashes"] |= known
        summary |= {"sealed_products": s["n_products"], "round_trip": True}
        summary["plaintext_deleted"] = cs.delete_plaintext(workdir)
        summary["workdir_empty"] = not any(workdir.iterdir())
        errs: list = []
        new = changed(stmp, before, errs)
        hits = spill_hits(stmp, new, known, seeds_b)
        summary |= {"scratch_tmp_changed": len(new), "scratch_spills": len(hits), "scratch_scan_errors": len(errs),
                    "spills_removed": remove_verified(stmp, hits),
                    "sealed_scan_hits": len(cs.content_scan([sealed], known))}
        if summary["spills_removed"]:
            started = False                            # the trap stays armed until every removal is verified
        if not cs.seal_check(sealed, s["seal_text"])["ok"]:
            raise cs.Break("the sealed dir does not match its own seal")
        summary["final_seal_check"] = True
        ok = (summary["generation_rc0"] and summary["command_unchanged"] and summary["products_json"]
              and summary["required_products"] and summary["workdir_empty"] and not hits and not errs
              and summary["sealed_scan_hits"] == 0)
        return (0 if ok else 1), summary
    except cs.Break:
        summary["integrity_break"] = True
        return cs.BREAK_RC, summary
    except cs.Refusal as e:
        summary["refused"] = str(e)
        if isinstance(e, StepRefusal):
            summary["step_cgroup_inventory"] = [dict(r, exe=exe_token(r["exe"], workdir, sealed)) for r in e.inventory]
        return 1, summary
    except (Exception, SystemExit) as e:
        summary["refused"] = "terminated" if isinstance(e, SystemExit) else "internal error"
        return 1, summary
    finally:
        try:
            gen.kill()
        except (OSError, cs.Refusal):
            summary["group_ended"] = "failed"           # only on a failure path: the exit is already 1
        if started and workdir.is_dir():               # the trap: no plaintext and no spill left behind
            try:
                seen["hashes"] |= plaintext_hashes(workdir)
                hits = spill_hits(stmp, changed(stmp, before, []), seen["hashes"], seeds_b)
                summary["trap_spills_removed"] = remove_verified(stmp, hits)
            except (OSError, cs.Refusal):
                summary["trap_spills_removed"] = "failed"
            try:
                summary["trap_deleted"] = cs.delete_plaintext(workdir)
            except (OSError, cs.Refusal):
                summary["trap_deleted"] = "failed"


def _term(signum, frame):
    raise SystemExit(143)


def main(argv=None, stdin=None, stdout=None) -> int:
    ap = argparse.ArgumentParser(prog="covfix_pg.py", allow_abbrev=False)
    ap.add_argument("--covfix-attempt", required=True)
    ap.add_argument("--workdir", type=Path, required=True)
    ap.add_argument("--sealed", type=Path, required=True)
    ap.add_argument("--gen-spec", type=Path, required=True)
    ap.add_argument("--gen-spec-sha256", required=True)
    ap.add_argument("--gpg", required=True)
    ap.add_argument("--gpgconf", required=True)
    ap.add_argument("--gpg-sha256", required=True)
    ap.add_argument("--gpgconf-sha256", required=True)
    a = ap.parse_args(argv)
    out = stdout or sys.stdout
    if not ATTEMPT.fullmatch(a.covfix_attempt):
        print(json.dumps({"refused": "the attempt must be 32 lowercase hex"}), file=out)
        return 1
    if not cs.HEX64.fullmatch(a.gen_spec_sha256):
        print(json.dumps({"refused": "the gen-spec pin must be 64 lowercase hex"}), file=out)
        return 1
    try:
        tools = cs.Tools(a.gpg, a.gpgconf, a.gpg_sha256, a.gpgconf_sha256)
    except cs.Refusal as e:
        print(json.dumps({"refused": str(e)}), file=out)
        return 1
    frame = (stdin or sys.stdin.buffer).read(cs.PG_FRAME_LEN + 1)
    old = signal.signal(signal.SIGTERM, _term)
    try:
        rc, summary = run(a.workdir, a.sealed, a.gen_spec, a.gen_spec_sha256, frame, tools)
    finally:
        signal.signal(signal.SIGTERM, old)
    print(json.dumps(summary, sort_keys=True), file=out)
    if rc == 0:
        print(f"covfix-receipt {a.covfix_attempt}", file=out)
    elif rc == cs.BREAK_RC:
        print(f"covfix-break {a.covfix_attempt}", file=out)
    return rc


if __name__ == "__main__":
    sys.exit(main())
