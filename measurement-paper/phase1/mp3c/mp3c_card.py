#!/usr/bin/env python3
"""MP3-C: write the GiBUU free-proton task jobcard from the frozen C12 production jobcard, or check one (C0).

  write: python3 mp3c_card.py write FROZEN_JOBCARD SEED OUT
  check: python3 mp3c_card.py check FROZEN_JOBCARD SEED TASKJOB   -> JSON verdict on stdout, exit 0 iff PASS

The task jobcard = '&initRandom\\n      SEED=<seed>\\n/\\n' + the frozen jobcard with exactly four value changes
(target_Z 6->1, target_A 12->1, include2p2hQE T->F, numEnsembles 4000->48000) and path_to_input set to the short
mirror, as sbatch_gibuu_mefhc.sh prepares every C12 task. 'check' parses every 'name = value' assignment of both
(namelist, name) and allows no other difference.
"""
import json
import re
import sys

SUBS = [(r"(\btarget_Z\s*=\s*)6\b", r"\g<1>1"), (r"(\btarget_A\s*=\s*)12\b", r"\g<1>1"),
        (r"(\binclude2p2hQE\s*=\s*)T\b", r"\g<1>F"), (r"(\bnumEnsembles\s*=\s*)4000\b", r"\g<1>48000")]
SHORT_INPUT = "/pscratch/sd/j/josephrb/gbi"
EXPECT = {("target", "target_z"): ("6", "1"), ("target", "target_a"): ("12", "1"),
          ("neutrino_induced", "include2p2hqe"): ("T", "F"), ("input", "numensembles"): ("4000", "48000")}


def make(frozen: str, seed: int) -> str:
    txt = open(frozen).read()
    for pat, rep in SUBS:
        txt, n = re.subn(pat, rep, txt)
        if n != 1:
            raise SystemExit(f"substitution {pat} applied {n} times (expected 1)")
    txt, n = re.subn(r"path_to_input='[^']*'", f"path_to_input='{SHORT_INPUT}'", txt)
    if n != 1:
        raise SystemExit("path_to_input not found once")
    return f"&initRandom\n      SEED={seed}\n/\n" + txt


def assignments(txt: str) -> dict:
    out, nl = {}, None
    for raw in txt.splitlines():
        line = raw.split("!")[0].strip()
        if not line:
            continue
        if line[0] in "&$":
            nl = line[1:].strip().lower()
            continue
        if line == "/":
            nl = None
            continue
        if "=" in line and nl is not None:
            k, v = line.split("=", 1)
            out[(nl, k.strip().lower())] = v.strip()
    return out


def check(frozen: str, seed: int, task: str) -> dict:
    ref = assignments(f"&initRandom\n      SEED={seed}\n/\n" + open(frozen).read().replace(
        re.search(r"path_to_input='[^']*'", open(frozen).read()).group(0), f"path_to_input='{SHORT_INPUT}'"))
    got = assignments(open(task).read())
    keys = set(ref) | set(got)
    diff = {f"{a}:{b}": [ref.get((a, b)), got.get((a, b))] for a, b in sorted(keys) if ref.get((a, b)) != got.get((a, b))}
    want = {f"{a}:{b}": list(v) for (a, b), v in EXPECT.items()}
    ok = diff == want and got.get(("initrandom", "seed")) == str(seed)
    return {"task_jobcard": task, "seed": seed, "differences_vs_production": diff, "required": want, "pass": bool(ok)}


if __name__ == "__main__":
    mode, frozen, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
    if mode == "write":
        open(sys.argv[4], "w").write(make(frozen, seed))
    else:
        r = check(frozen, seed, sys.argv[4])
        print(json.dumps(r))
        raise SystemExit(0 if r["pass"] else 1)
