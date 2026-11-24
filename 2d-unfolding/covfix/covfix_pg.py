"""COVFIX PG's bound binary (COVFIX-DECLARATION.md rev 11.4 section 4.2; COVFIX-BINDING-1 ruling 4). It runs on one
exclusive node under the director's wrapper (JE's round-3 contract), and is the only PG code that touches the
passphrase, which it hands to gpg on fd 3.

  covfix_pg.py --covfix-attempt <32 hex> --workdir <empty dir> --sealed <new dir> --gen-spec <json>  < frame

  stdin       exactly "<passphrase, 64 hex>\\n<seed base, decimal>\\n", then EOF (covfix_seal.read_frame)
  gen-spec    {"command": [path, args...], "command_sha256": "<64 hex>", "tunes": [u=0 name, u=1 name],
               "env_keep": [variable names the generator needs]}; the command file's sha256 is checked before it runs
  generation  tune-generator's command, run as <command...> --workdir W --seeds W/seeds.json, with cwd W, stdin
              /dev/null, stdout and stderr into W/capture/, and a scrubbed environment: only env_keep's variables
              that are set, plus TMPDIR = W/tmp. It never sees the passphrase or this process's descriptors.
  seal        every file under W under opaque ids (section 4.2 steps 1-3), the plaintext deleted (step 4), the content
              scan (step 5) of W, the sealed dir and every $SCRATCH/tmp entry created during the run (setup_salloc_env.sh
              exports TMPDIR=$SCRATCH/tmp, so a leak there is caught), and PG-SEAL.sha256 in the sealed dir

Exits, per the wrapper's contract:
  0   generation rc 0, W/PRODUCTS.json present, seal, round trip, deletion and scan all clean; stdout ends with
      "covfix-receipt <attempt>"
  66  a confirmed integrity break (a round-trip mismatch); stdout ends with "covfix-break <attempt>"
  1   anything else (a refusal, a failed generation, a scan hit): no receipt; plaintext under W is deleted
  2   bad arguments (argparse)
Stdout carries one JSON summary of booleans and counts, and the final line. It never carries a secret, a seed, a
plaintext hash or a physics value; the generator's own output goes into the sealed capture files.

MEASURES: nothing. CANNOT AUTHORIZE: a connect; PG runs only under its binding addendum.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import covfix_seal as cs  # noqa: E402

ATTEMPT = re.compile(r"[0-9a-f]{32}")
SPEC_KEYS = {"command", "command_sha256", "tunes", "env_keep"}


def load_spec(path: Path) -> dict:
    try:
        spec = json.loads(Path(path).read_text())
    except (OSError, ValueError) as e:
        raise cs.Refusal(f"the gen-spec cannot be read ({type(e).__name__})") from e
    if not isinstance(spec, dict) or set(spec) != SPEC_KEYS:
        raise cs.Refusal(f"the gen-spec must have exactly the keys {sorted(SPEC_KEYS)}")
    ok = (isinstance(spec["command"], list) and spec["command"] and all(isinstance(a, str) for a in spec["command"])
          and isinstance(spec["command_sha256"], str) and re.fullmatch(r"[0-9a-f]{64}", spec["command_sha256"])
          and isinstance(spec["tunes"], list) and len(spec["tunes"]) == 2
          and all(isinstance(t, str) and t for t in spec["tunes"])
          and isinstance(spec["env_keep"], list) and all(isinstance(v, str) for v in spec["env_keep"])
          and "TMPDIR" not in spec["env_keep"])
    if not ok:
        raise cs.Refusal("the gen-spec's values are malformed")
    try:
        got = hashlib.sha256(Path(spec["command"][0]).read_bytes()).hexdigest()
    except OSError as e:
        raise cs.Refusal("the generator command cannot be read") from e
    if got != spec["command_sha256"]:
        raise cs.Refusal("the generator command's sha256 is not the gen-spec's")
    return spec


def prepare(workdir: Path, sealed: Path) -> None:
    if not workdir.is_dir() or any(workdir.iterdir()):
        raise cs.Refusal("the work dir must exist and be empty")
    if sealed.exists():
        raise cs.Refusal("the sealed dir must not exist")


def generate(spec: dict, workdir: Path, seeds: dict) -> int:
    (workdir / "capture").mkdir()
    (workdir / "tmp").mkdir()
    (workdir / "seeds.json").write_text(json.dumps(seeds, sort_keys=True))
    env = {k: os.environ[k] for k in spec["env_keep"] if k in os.environ}
    env["TMPDIR"] = str(workdir / "tmp")
    with open(workdir / "capture" / "stdout.log", "xb") as fo, open(workdir / "capture" / "stderr.log", "xb") as fe:
        rc = subprocess.run([*spec["command"], "--workdir", str(workdir), "--seeds", str(workdir / "seeds.json")],
                            cwd=workdir, env=env, stdin=subprocess.DEVNULL, stdout=fo, stderr=fe,
                            close_fds=True).returncode
    (workdir / "capture" / "rc.txt").write_text(f"{rc}\n")
    return rc


def scratch_tmp() -> Path | None:
    s = os.environ.get("SCRATCH")
    return Path(s) / "tmp" if s else None


def entries(d: Path | None) -> set[str]:
    return set(os.listdir(d)) if d is not None and d.is_dir() else set()


def run(attempt: str, workdir: Path, sealed: Path, spec_path: Path, frame: bytes, gpg: str = "gpg") -> tuple[int, dict]:
    """(exit code, summary). The summary holds booleans and counts only."""
    summary = {"frame_ok": False, "spec_ok": False}
    started = False
    try:
        passphrase, base = cs.read_frame(frame, with_seed=True)
        summary["frame_ok"] = True
        spec = load_spec(spec_path)
        summary["spec_ok"] = True
        prepare(workdir, sealed)
        seeds = cs.task_seeds(base, spec["tunes"])
        stmp = scratch_tmp()
        before = entries(stmp)
        started = True
        rc = generate(spec, workdir, seeds)
        summary["generation_rc0"] = rc == 0
        summary["products_json"] = (workdir / "PRODUCTS.json").is_file()
        s = cs.seal(workdir, sealed, passphrase, gpg)
        summary |= {"sealed_products": s["n_products"], "round_trip": True}
        summary["plaintext_deleted"] = cs.delete_plaintext(workdir)
        started = False
        new = sorted(entries(stmp) - before)
        summary["scratch_tmp_new_entries"] = len(new)
        hits = cs.content_scan([workdir, sealed, *[stmp / e for e in new]], set(s["hashes"].values()))
        summary["scan_hits"] = len(hits)
        ok = summary["generation_rc0"] and summary["products_json"] and not hits
        return (0 if ok else 1), summary
    except cs.Break:
        summary["integrity_break"] = True
        return cs.BREAK_RC, summary
    except cs.Refusal as e:
        summary["refused"] = str(e)
        return 1, summary
    finally:
        if started and workdir.is_dir():          # the trap: no plaintext is left behind on any failure
            try:
                summary["trap_deleted"] = cs.delete_plaintext(workdir)
            except (OSError, cs.Refusal):
                summary["trap_deleted"] = "failed"


def main(argv=None, stdin=None, stdout=None) -> int:
    ap = argparse.ArgumentParser(prog="covfix_pg.py", allow_abbrev=False)
    ap.add_argument("--covfix-attempt", required=True)
    ap.add_argument("--workdir", type=Path, required=True)
    ap.add_argument("--sealed", type=Path, required=True)
    ap.add_argument("--gen-spec", type=Path, required=True)
    ap.add_argument("--gpg", default="gpg")
    a = ap.parse_args(argv)
    out = stdout or sys.stdout
    if not ATTEMPT.fullmatch(a.covfix_attempt):
        print("covfix-pg: --covfix-attempt must be 32 lowercase hex", file=out)
        return 1
    frame = (stdin or sys.stdin.buffer).read()
    rc, summary = run(a.covfix_attempt, a.workdir, a.sealed, a.gen_spec, frame, a.gpg)
    print(json.dumps(summary, sort_keys=True), file=out)
    if rc == 0:
        print(f"covfix-receipt {a.covfix_attempt}", file=out)
    elif rc == cs.BREAK_RC:
        print(f"covfix-break {a.covfix_attempt}", file=out)
    return rc


if __name__ == "__main__":
    sys.exit(main())
