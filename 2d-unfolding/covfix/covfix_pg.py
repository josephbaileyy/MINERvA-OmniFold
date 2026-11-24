"""COVFIX PG's bound binary (COVFIX-DECLARATION.md rev 11.4 section 4.2; COVFIX-BINDING-1 ruling 4). It runs on one
exclusive node under the director's wrapper (JE's round-3 contract), and is the only PG code that touches the
passphrase, which it hands to gpg on fd 3.

  covfix_pg.py --covfix-attempt <32 hex> --workdir <empty dir> --sealed <new dir, disjoint from it>
               --gen-spec <json> --gpg <absolute path> --gpgconf <absolute path>
               --gpg-sha256 <64 hex> --gpgconf-sha256 <64 hex>  < frame

  stdin       exactly "<passphrase, 64 hex>\\n<seed base, 10 digits>\\n" (76 bytes), then EOF
  gen-spec    {"command": [absolute path, args...], "command_sha256": "<64 hex>", "tunes": [u=0 name, u=1 name],
               "env_keep": [variable names the generator needs]}. The command path is resolved once, hashed, launched
              by that resolved path and hashed again after the run; a change is a role failure. RESIDUAL WINDOW (disclosed,
              the director's ruling R2): a replacement written by this same account between the hash and the exec,
              and restored before the re-hash, would not be seen; section 4.2's cooperative assumption covers it.
  gpg         gpg and gpgconf are pinned by sha256 (the binding) and hashed before every exec (ruling R1)
  before      a synthetic gpg round trip with the pinned gpg and the real passphrase
  generation  <resolved command...> --workdir W --seeds W/seeds.json, with cwd W, stdin /dev/null, stdout and stderr
              into W/capture/, a scrubbed environment (env_keep's set variables, plus TMPDIR = W/tmp), in its own
              process group, which is killed and reaped on any failure or SIGTERM
  products    W/PRODUCTS.json: a non-empty JSON list of distinct safe relpaths of regular files under W
  seal        every file under W under opaque ids (covfix_seal.seal), then W's plaintext deleted and W verified empty
  spill scan  every file created or changed during the run at any depth under $SCRATCH/tmp (setup_salloc_env.sh exports
              TMPDIR=$SCRATCH/tmp), and the sealed dir, checked for a plaintext hash; the scratch files also for any
              task seed in their name or bytes. A scratch hit is removed, its removal verified, and it fails the run.
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
seed, a plaintext hash, a work-dir name, a physics value or an exception's text.

MEASURES: nothing. CANNOT AUTHORIZE: a connect; PG runs only under its binding addendum.
"""
from __future__ import annotations

import argparse
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
SPEC_KEYS = {"command", "command_sha256", "tunes", "env_keep"}
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


def load_spec(path: Path) -> dict:
    try:
        spec = json.loads(Path(path).read_text())
    except (OSError, ValueError) as e:
        raise cs.Refusal("the gen-spec cannot be read") from e
    if not isinstance(spec, dict) or set(spec) != SPEC_KEYS:
        raise cs.Refusal("the gen-spec must have exactly its four keys")
    ok = (isinstance(spec["command"], list) and spec["command"] and all(isinstance(a, str) for a in spec["command"])
          and os.path.isabs(spec["command"][0])
          and isinstance(spec["command_sha256"], str) and cs.HEX64.fullmatch(spec["command_sha256"])
          and isinstance(spec["tunes"], list) and len(spec["tunes"]) == 2
          and all(isinstance(t, str) and t for t in spec["tunes"])
          and isinstance(spec["env_keep"], list) and all(isinstance(v, str) for v in spec["env_keep"])
          and "TMPDIR" not in spec["env_keep"])
    if not ok:
        raise cs.Refusal("the gen-spec's values are malformed")
    resolved = os.path.realpath(spec["command"][0])
    if file_sha256(resolved) != spec["command_sha256"]:
        raise cs.Refusal("the generator command's sha256 is not the gen-spec's")
    return dict(spec, resolved=resolved)


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
        return ("f", st.st_ino, st.st_mtime_ns, st.st_size)
    return ("o", st.st_ino, st.st_mode)


def snapshot(root: Path | None) -> dict:
    """{relpath: signature} of every entry under root at any depth (files, directories, links and special entries,
    never followed); a walk error refuses."""
    out = {}
    if root is None or not root.is_dir():
        return out
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False, onerror=cs._raise):
        for name in dirnames + filenames:
            p = os.path.join(dirpath, name)
            out[os.path.relpath(p, root)] = _sig(os.lstat(p), p)
    return out


def changed(root: Path | None, before: dict) -> list[tuple[str, tuple, bool]]:
    """(relpath, signature, new) for every entry created or changed since `before`."""
    after = snapshot(root)
    return [(rel, sig, rel not in before) for rel, sig in sorted(after.items()) if before.get(rel) != sig]


def spill_hits(root: Path, entries: list, hashes: set[str], seeds: list[bytes]) -> list[tuple[str, tuple, bool]]:
    """Entries carrying a task seed anywhere in their relative path (or, for a link, its target), or a regular file
    whose sha256 is a plaintext hash or whose bytes carry a task seed."""
    hits = []
    for rel, sig, new in entries:
        text = os.fsencode(rel) + (b"\x00" + os.fsencode(sig[2]) if sig[0] == "l" else b"")
        hit = any(sd in text for sd in seeds)
        if not hit and sig[0] == "f":
            data = cs.noatime_read(root / rel)
            hit = hashlib.sha256(data).hexdigest() in hashes or any(sd in data for sd in seeds)
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
class Generator:
    def __init__(self):
        self.proc = None

    def run(self, spec: dict, workdir: Path, seeds: dict) -> int:
        (workdir / "capture").mkdir()
        (workdir / "tmp").mkdir()
        (workdir / "seeds.json").write_text(json.dumps(seeds, sort_keys=True))
        env = {k: os.environ[k] for k in spec["env_keep"] if k in os.environ}
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
def run(workdir: Path, sealed: Path, spec_path: Path, frame: bytes, tools: cs.Tools) -> tuple[int, dict]:
    """(exit code, summary). The summary holds fixed codes, booleans and counts only."""
    summary = {"frame_ok": False, "spec_ok": False, "seed_alias": SEED_ALIAS}
    gen = Generator()
    started, stmp, before, seeds_b, known = False, None, {}, [], set()
    try:
        passphrase, base = cs.read_frame(frame, with_seed=True)
        summary["frame_ok"] = True
        spec = load_spec(spec_path)
        summary["spec_ok"] = True
        workdir, sealed = prepare(workdir, sealed)
        seeds = cs.task_seeds(base, spec["tunes"])
        seeds_b = [str(s).encode() for t in seeds["tunes"] for s in t["task_seeds"]]
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
        s = cs.seal(workdir, sealed, passphrase, tools)
        known = set(s["hashes"].values())
        summary |= {"sealed_products": s["n_products"], "round_trip": True}
        summary["plaintext_deleted"] = cs.delete_plaintext(workdir)
        summary["workdir_empty"] = not any(workdir.iterdir())
        new = changed(stmp, before)
        hits = spill_hits(stmp, new, known, seeds_b)
        summary |= {"scratch_tmp_changed": len(new), "scratch_spills": len(hits),
                    "spills_removed": remove_verified(stmp, hits),
                    "sealed_scan_hits": len(cs.content_scan([sealed], known))}
        started = False                                # the trap stays armed until the scan and removal are done
        if not cs.seal_check(sealed, s["seal_text"])["ok"]:
            raise cs.Break("the sealed dir does not match its own seal")
        summary["final_seal_check"] = True
        ok = (summary["generation_rc0"] and summary["command_unchanged"] and summary["products_json"]
              and summary["workdir_empty"] and not hits and summary["sealed_scan_hits"] == 0)
        return (0 if ok else 1), summary
    except cs.Break:
        summary["integrity_break"] = True
        return cs.BREAK_RC, summary
    except cs.Refusal as e:
        summary["refused"] = str(e)
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
                hits = spill_hits(stmp, changed(stmp, before), known | plaintext_hashes(workdir), seeds_b)
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
    ap.add_argument("--gpg", required=True)
    ap.add_argument("--gpgconf", required=True)
    ap.add_argument("--gpg-sha256", required=True)
    ap.add_argument("--gpgconf-sha256", required=True)
    a = ap.parse_args(argv)
    out = stdout or sys.stdout
    if not ATTEMPT.fullmatch(a.covfix_attempt):
        print(json.dumps({"refused": "the attempt must be 32 lowercase hex"}), file=out)
        return 1
    try:
        tools = cs.Tools(a.gpg, a.gpgconf, a.gpg_sha256, a.gpgconf_sha256)
    except cs.Refusal as e:
        print(json.dumps({"refused": str(e)}), file=out)
        return 1
    frame = (stdin or sys.stdin.buffer).read(cs.PG_FRAME_LEN + 1)
    old = signal.signal(signal.SIGTERM, _term)
    try:
        rc, summary = run(a.workdir, a.sealed, a.gen_spec, frame, tools)
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
