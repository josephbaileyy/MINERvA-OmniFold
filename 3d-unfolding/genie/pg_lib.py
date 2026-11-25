#!/usr/bin/env python3
"""Helpers for pg_generate.sh, COVFIX PG's generation of its two validation truths
(state/2d-closeout/covfix-20261122/COVFIX-DECLARATION.md sections 4.1-4.2). Standard library only.

  queue    --seeds W/seeds.json --out W/run/queue.txt
           validate seeds.json and write one line per gevgen task: "<tune> <seed> u<u>/t<k>". Never prints a seed:
           every refusal names the rule, not the value.
  products --workdir W --seeds W/seeds.json
           write W/PRODUCTS.json, the relative paths of the ratio files PV uses, after checking they exist, with the
           pass of every verification step (strace, slot 1's product and UPS file, every trace check).
  inventory [--workdir W]
           print the required inventory, [{"pattern": glob relative to W, "count": n}], in covfix_pg.py's gen-spec
           form (fnmatchcase, '*' crossing '/'). With --workdir, check that each pattern matches exactly n regular
           files under W, following no link, and exit 1 if not.

seeds.json is {"tunes": [{"u": 0, "name": "G21_11a_00_000", "task_seeds": [7 ints]},
                         {"u": 1, "name": "G18_02a_00_000", "task_seeds": [7 ints]}]}.
Section 4.2's rule: tune u's task seed = base + 10_000 u + task index, with the base uniform in [1e9, 2e9), and no
seed at or above 2**31 - 1 (run_gevgen_v3.sh passes it to both --seed and -r). The base itself is not given, so the
checks are: u0's first seed in [1e9, 2e9); consecutive seeds within a tune; u1's first = u0's first + 10_000; every
seed below 2**31 - 1.

MEASURES: nothing. CANNOT AUTHORIZE: anything.
"""
import argparse
import fnmatch
import hashlib
import json
import os
import sys
from pathlib import Path

N_TASKS = 7
U_STRIDE = 10_000
BASE_LO, BASE_HI = 1_000_000_000, 2_000_000_000
SEED_CEIL = 2 ** 31 - 1
U0 = "G21_11a_00_000"                                   # slot 1, from a sha-pinned private copy of the product
U1 = ("G18_02a_00_000",)                                 # slot 2, from CVMFS
TRUTH = {"G21_11a_00_000": "genie_v3_g21", "G18_02a_00_000": "genie_v3_g18_02a"}   # fd_f1_prep.PG_TRUTHS keys
RUNG = "L-5D-PV"                                         # fd_f1_prep.RUNG


class Refusal(Exception):
    pass


def _int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def load_seeds(path):
    """The validated tunes, sorted by u: [(u, name, [seeds])]. Raises Refusal naming the rule only."""
    try:
        d = json.loads(Path(path).read_text())
    except (OSError, ValueError):
        raise Refusal("seeds.json is missing or not JSON") from None
    if not isinstance(d, dict) or set(d) != {"tunes"} or not isinstance(d["tunes"], list) or len(d["tunes"]) != 2:
        raise Refusal("seeds.json must be {\"tunes\": [two entries]}")
    out = []
    for t in d["tunes"]:
        if not isinstance(t, dict) or set(t) != {"u", "name", "task_seeds"}:
            raise Refusal("each tune entry must have exactly u, name and task_seeds")
        if not _int(t["u"]) or not isinstance(t["name"], str) or not isinstance(t["task_seeds"], list):
            raise Refusal("u must be an int, name a string, task_seeds a list")
        out.append((t["u"], t["name"], t["task_seeds"]))
    out.sort(key=lambda x: x[0])
    if [u for u, _, _ in out] != [0, 1]:
        raise Refusal("the tunes must be u = 0 and u = 1, once each")
    if out[0][1] != U0:
        raise Refusal(f"u0 must be {U0}")
    if out[1][1] not in U1:
        raise Refusal(f"u1 must be one of {', '.join(U1)}")
    for u, _, s in out:
        if len(s) != N_TASKS or not all(_int(x) for x in s):
            raise Refusal(f"u{u} must have {N_TASKS} integer task seeds")
        if any(b - a != 1 for a, b in zip(s, s[1:])):
            raise Refusal(f"u{u}'s task seeds are not consecutive (base + 10000 u + task index)")
        if any(x >= SEED_CEIL for x in s):
            raise Refusal(f"u{u} has a task seed at or above 2**31 - 1")
    if not BASE_LO <= out[0][2][0] < BASE_HI:
        raise Refusal("u0's first task seed is outside the declared base range [1e9, 2e9)")
    if out[1][2][0] - out[0][2][0] != U_STRIDE:
        raise Refusal("u1's first task seed is not u0's plus 10000")
    return out


def cmd_queue(a):
    tunes = load_seeds(a.seeds)
    if os.path.exists(a.out):
        raise Refusal("the queue file already exists")
    lines = [f"{name} {s} u{u}/t{k}\n" for u, name, seeds in tunes for k, s in enumerate(seeds)]
    Path(a.out).write_text("".join(lines))
    print(f"[pg_lib] queue: {len(lines)} tasks, tunes {[name for _, name, _ in tunes]}")
    return 0


def products(workdir, tunes):
    rec = {"schema": "covfix-pg-products/1", "products": []}
    for u, name, _ in tunes:
        t = TRUTH[name]
        p = {"u": u, "tune": name, "truth": t, "bridged": f"out/prep/bridged/{t}.json",
             "ratio": f"out/prep/ratios/{RUNG}/{t}.json", "prediction": f"out/gen5d/{t}_xsec5d.npz"}
        for k in ("bridged", "ratio", "prediction"):
            if not (Path(workdir) / p[k]).is_file():
                raise Refusal(f"u{u}: the {k} file is missing")
        rec["products"].append(p)
    return rec


CHECKS = ("out/tool_check_strace.json", "out/members_check_G21_11a_00_000.json", "out/dbconfig_check.json")


def inventory(tunes=None):
    """[{pattern, count}]: every file pg_generate.sh leaves under W on success, with its fixed count. Optional files
    (gntp.ghep.root, kept only after a failed gntpc) are not listed: covfix_pg.py seals them as extras."""
    tunes = tunes or [U0] + list(U1)
    req = []

    def add(p, n=1):
        req.append({"pattern": p, "count": n})
    for u, t in enumerate(tunes):
        n = TRUTH[t]
        for p in (f"out/splines/{t}_CH.xml.gz", f"out/spline_check_{t}.json", f"out/graphs_{t}.root",
                  f"out/graphs_{t}.log", f"out/gst/{n}_ALL.gst.root", f"out/gen5d/{n}_xsec5d.npz",
                  f"out/gen5d/{n}_xsec5d.meta.json", f"out/prep/bridged/{n}.json", f"out/prep/ratios/{RUNG}/{n}.json",
                  f"out/logs/reduce_{t}.log", f"out/logs/graphs_{t}.log", f"out/logs/hadd_u{u}.log",
                  f"out/logs/convert_u{u}.log", f"out/logs/env-c_u{u}.log", f"out/traces/reduce_{t}.trace",
                  f"out/traces/graphs_{t}.trace", f"out/trace_check_reduce_{t}.json", f"out/trace_check_graphs_{t}.json",
                  f"out/exe_check_{t}.json", f"run/exe_{t}.txt", f"out/logs/exe_{t}.log", f"out/reduce_check_{t}.json",
                  f"out/coverage_check_{t}.json", f"out/trace_check_coverage_{t}.json", f"out/coverage/{t}/coverage.trace",
                  f"out/logs/coverage_{t}.log", f"run/gxmlpath_{t}.txt", f"run/ld_library_path_{t}.txt", f"run/awk_{t}.txt"):
            add(p)
        for f in ("task.time", "task.log", "gevgen.log", "gntpc.log", "genie_v3.gst.root", "input-flux.root",
                  "gevgen.status", "gevgen.trace", "trace_check.json", "gntpc.trace", "trace_check_gntpc.json"):
            add(f"out/work/u{u}/t*/{f}", N_TASKS)
    for p in ("seeds.json", "PRODUCTS.json", "out/PG-SHA256SUMS", PUBLISH_SUMS, "out/flux_phi_t_0_100.root",
              "out/argv_check.json", "out/messenger_check.json", "out/Messenger_pg.xml", "out/revision_start.json",
              "out/revision_end.json",
              "out/prep/config-pg.json", "out/prep/f1-prep-SHA256SUMS", f"out/prep/ratios/{RUNG}/ratios.json",
              "run/queue.txt", "run/truths.txt", "run/deploy-status-before.txt", "run/deploy-status-setup.txt",
              "run/deploy-status-after.txt") + CHECKS:
        add(p)
    for lg in ("queue", "flux_and_splines", "xargs", "flux_check", "prep", "products", "sums", "trace_check",
               "tool_check_strace", "members_check", "dbconfig_check", "inventory", "env-q", "env-a1", "env-fc",
               "env-p", "env-w", "env-i", "env-l", "reduce_check", "coverage", "revision", "publish"):
        add(f"out/logs/{lg}.log")
    return req


def inventory_problems(workdir, req):
    files = []
    for d, dirs, names in os.walk(workdir, followlinks=False):
        for x in names:
            q = os.path.join(d, x)
            if os.path.isfile(q) and not os.path.islink(q):
                files.append(os.path.relpath(q, workdir))
    return [f"{r['pattern']}: {n} files, not {r['count']}" for r in req
            for n in [sum(fnmatch.fnmatchcase(f, r["pattern"]) for f in files)] if n != r["count"]]


def cmd_inventory(a):
    req = inventory()
    if a.workdir is None:
        print(json.dumps(req, indent=1))
        return 0
    probs = inventory_problems(a.workdir, req)
    print(json.dumps({"check": "inventory", "pass": not probs, "n_patterns": len(req), "problems": probs}))
    return 0 if not probs else 1


def cmd_products(a):
    out = Path(a.workdir) / "PRODUCTS.json"
    if out.exists():
        raise Refusal("PRODUCTS.json already exists")
    rec = products(a.workdir, load_seeds(a.seeds))
    globs = ("out/**/trace_check*.json", "out/exe_check_*.json", "out/reduce_check_*.json", "out/coverage_check_*.json",
             "out/argv_check.json", "out/messenger_check.json", "out/revision_*.json")
    checks = list(CHECKS) + sorted({str(q.relative_to(a.workdir)) for g in globs for q in Path(a.workdir).glob(g)})
    rec["checks"] = {}
    for c in checks:
        try:
            text = (Path(a.workdir) / c).read_text()
            try:
                d = json.loads(text)                            # trace checks: one JSON document
            except ValueError:
                d = json.loads(text.splitlines()[-1])           # tool and members checks: their one-line result
            ok = d.get("pass") is True
        except (OSError, ValueError, IndexError, AttributeError):
            ok = False
        rec["checks"][c] = ok
    # per tune: exe, the reduce, graphs and coverage traces, reduce and coverage checks, and each task's gevgen and gntpc
    # traces; once: the argv, the messenger and the revision at the start and the end
    if len(checks) != len(CHECKS) + (1 + len(U1)) * (6 + 2 * N_TASKS) + 4 or not all(rec["checks"].values()):
        raise Refusal("a verification step did not pass, or is missing")
    out.write_text(json.dumps(rec, indent=1) + "\n")
    print(f"[pg_lib] products: {len(rec['products'])} truths")
    return 0


# ------------------------------------------------------------------------- the seed (codex 11; the director's ruling)

# Files that hold the sealed seed, or could be searched for it, and so never leave W: gevgen names its outputs by the
# run number, which is the seed, so every trace and log of a task carries it; their hashes would let a reader search
# the seed space, so the published sums omit them. PG-SHA256SUMS (all files) stays in W for the seal.
SEED_BEARING = ("seeds.json", "run/queue.txt", "out/PG-SHA256SUMS", "out/work/u*/t*/gevgen.trace",
                "out/work/u*/t*/gntpc.trace", "out/work/u*/t*/gevgen.log", "out/work/u*/t*/gntpc.log",
                "out/work/u*/t*/task.log", "out/work/u*/t*/task.time", "out/work/u*/t*/gevgen.status",
                "out/work/u*/t*/gntp.ghep.root", "out/logs/*")
PUBLISH_SUMS = "out/PG-PUBLISH-SHA256SUMS"


def seed_forms(seed):
    """The byte strings a seed is searched as: decimal (any zero-padding contains it) and hex in both cases."""
    return sorted({str(seed).encode(), format(seed, "x").encode(), format(seed, "X").encode()})


def seed_bearing(rel):
    return any(fnmatch.fnmatchcase(rel, g) for g in SEED_BEARING)


def leak_hits(workdir, files, seeds):
    """[(relpath, where)]: each outgoing file whose path or bytes hold any form of any seed. Never prints a seed."""
    forms = [f for s in seeds for f in seed_forms(s)]
    width = max(len(f) for f in forms)
    hits = []
    for rel in files:
        if any(f in rel.encode() for f in forms):
            hits.append((None, "path"))                    # the path itself is not repeated
            continue
        with open(os.path.join(workdir, rel), "rb") as fh:
            tail = b""
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                buf = tail + chunk
                if any(f in buf for f in forms):
                    hits.append((rel, "bytes"))
                    break
                tail = buf[-(width - 1):]
    return hits


def cmd_publish(a):
    w = Path(a.workdir)
    out = w / PUBLISH_SUMS
    if out.exists():
        raise Refusal("the publish sums already exist")
    seeds = [s for _, _, ss in load_seeds(a.seeds) for s in ss]
    files = []
    for d, dirs, names in os.walk(w, followlinks=False):
        for x in names:
            q = os.path.join(d, x)
            rel = os.path.relpath(q, w)
            if os.path.islink(q) or not os.path.isfile(q):
                raise Refusal("a link or special file in W")
            if not seed_bearing(rel) and rel != PUBLISH_SUMS:
                files.append(rel)
    hits = leak_hits(w, sorted(files), seeds)
    if hits:
        raise Refusal(f"leak scan: {len(hits)} outgoing files hold a seed ({sum(1 for r, _ in hits if r is None)} "
                      f"in their path)")
    lines = []
    for rel in sorted(files):
        h = hashlib.sha256()
        with open(w / rel, "rb") as fh:
            for b in iter(lambda: fh.read(1 << 20), b""):
                h.update(b)
        lines.append(f"{h.hexdigest()}  {rel}\n")
    out.write_text("".join(lines))
    print(f"[pg_lib] publish: {len(files)} files scanned clean; {PUBLISH_SUMS} written")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("queue")
    q.add_argument("--seeds", required=True)
    q.add_argument("--out", required=True)
    p = sub.add_parser("products")
    p.add_argument("--workdir", required=True)
    p.add_argument("--seeds", required=True)
    i = sub.add_parser("inventory")
    i.add_argument("--workdir")
    b = sub.add_parser("publish")
    b.add_argument("--workdir", required=True)
    b.add_argument("--seeds", required=True)
    a = ap.parse_args(argv)
    try:
        return {"queue": cmd_queue, "products": cmd_products, "inventory": cmd_inventory,
                "publish": cmd_publish}[a.cmd](a)
    except Refusal as e:
        print(f"[pg_lib] refusing: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
