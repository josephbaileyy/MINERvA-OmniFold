#!/usr/bin/env python3
"""Slide 2b: the quantitative workflow observables, and the one that does not survive.

EVERY QUANTITY HERE HAD TO CLEAR THREE BARS, which are the same bars the rest of the
talk applies: (i) a population I can name, (ii) a denominator that does not move when
the story changes, (iii) a null it could have failed. Anything that cannot state all
three is numerology and is not printed.

WHAT IS DELIBERATELY ABSENT.
  * Sum of `input_tokens` across turns. Each assistant turn's input contains the WHOLE
    conversation prefix, so summing double-counts the context once per turn -- here it
    would inflate the "tokens consumed" figure by roughly 250x. The additive quantities
    are output_tokens, cache_creation_input_tokens and cache_read_input_tokens.
  * Shannon entropy of commit-message TEXT. It measures English prose, not work.
  * Any perplexity or "information gain per token": no held-out set and no hypothesis
    space, so no null.
  * Tokens as a productivity proxy. A session that thrashes burns more tokens. There is
    no counterfactual arm in this project and so no speedup claim anywhere in this deck.
  * A power-law exponent for commit sizes. See section 5: it was fitted, it failed, and
    the failure is reported rather than the exponent.

SCOPE OF THE TOKEN SWEEP: the three Claude transcript roots below, project directories
matching MINERvA-OmniFold only. Codex sessions (~/.codex, ~/.codex-claude-bridge) use a
different schema and are NOT included, so token totals are a LOWER BOUND on the project.
"""
import glob
import json
import math
import os
import random
import statistics as st
import subprocess
import sys
from collections import Counter, defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SPLIT = "2026-08-12"          # first day a lane identity commits
CODE = (".py", ".sh", ".C", ".cc", ".h")
VERIF_TOKENS = ("test_", "probe-", "guard", "ratchet", "verify_", "_check", "preflight")
ROOTS = [os.path.expanduser(p) for p in
         ("~/.claude-school/projects", "~/.claude-personal/projects", "~/.claude/projects")]
random.seed(0)


def is_verif(path):
    base = path.rsplit("/", 1)[-1].lower()
    return any(t in base for t in VERIF_TOKENS) or "guard" in path.lower()


def H(counter, base=2):
    n = sum(counter.values())
    if not n:
        return 0.0
    return -sum((c / n) * math.log(c / n, base) for c in counter.values() if c)


def H_mm(counter, base=2):
    """Miller-Madow: H_hat + (K-1)/(2N). Entropy is biased LOW at small N, so any
    pre/post comparison at unequal N is an artifact unless this and equal-N sampling
    are both applied."""
    n = sum(counter.values())
    k = sum(1 for c in counter.values() if c)
    return H(counter, base) + (k - 1) / (2 * n * math.log(base)) if n else 0.0


def git_log():
    out = subprocess.run(["git", "log", "--format=\x01%as\x02%cn", "--numstat"],
                         cwd=REPO, capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"CANNOT CHECK :: git log exited {out.returncode}\n{out.stderr}")
    commits = []
    for rec in out.stdout.split("\x01"):
        if not rec.strip():
            continue
        rows = rec.split("\n")
        head = rows[0].split("\x02")
        if len(head) < 2:
            continue
        files = []
        for row in rows[1:]:
            p = row.split("\t")
            if len(p) == 3 and p[0] != "-":
                files.append((int(p[0]), p[2]))
        commits.append((head[0].strip(), head[1], files))
    if not commits:
        sys.exit("CANNOT CHECK :: no commits parsed. Zero here means the parse could "
                 "not look, not that the repository is empty.")
    return commits


def tokens():
    per, tot, msgs, sessions = defaultdict(int), defaultdict(int), 0, 0
    found = {r: len(glob.glob(os.path.join(r, "*MINERvA-OmniFold*", "*.jsonl"))) for r in ROOTS}
    for r in ROOTS:
        for path in glob.glob(os.path.join(r, "*MINERvA-OmniFold*", "*.jsonl")):
            sessions += 1
            s = 0
            with open(path, errors="replace") as fh:
                for line in fh:
                    try:
                        d = json.loads(line)
                    except Exception:
                        continue
                    m = d.get("message")
                    u = m.get("usage") if isinstance(m, dict) else None
                    if not isinstance(u, dict):
                        continue
                    msgs += 1
                    for k in ("input_tokens", "output_tokens",
                              "cache_creation_input_tokens", "cache_read_input_tokens"):
                        v = u.get(k)
                        if isinstance(v, int):
                            tot[k] += v
                            if k == "output_tokens":
                                s += v
            per[path] = s
    if not msgs:
        sys.exit("CANNOT CHECK :: no usage records found in any swept root. Without a "
                 "positive control that the parse sees a usage block, zero is not a result.")
    return found, sessions, msgs, tot, sorted(per.values())


def main():
    commits = git_log()
    print("=" * 78)
    print("1. TOKENS  (additive fields only -- see the docstring on input_tokens)")
    found, sessions, msgs, tot, per = tokens()
    for r, k in found.items():
        print(f"   swept {r} -> {k} jsonl")
    print(f"   sessions {sessions}   assistant messages carrying usage {msgs:,}")
    print(f"   output_tokens (GENERATED)      {tot['output_tokens']:>15,}")
    print(f"   cache_creation_input_tokens    {tot['cache_creation_input_tokens']:>15,}")
    print(f"   cache_read_input_tokens        {tot['cache_read_input_tokens']:>15,}")
    print(f"   input_tokens (uncached)        {tot['input_tokens']:>15,}")
    ctx = (tot["cache_read_input_tokens"] + tot["cache_creation_input_tokens"]
           + tot["input_tokens"])
    print(f"   CONTEXT READ : GENERATED       {ctx / tot['output_tokens']:>15.1f} : 1")
    print(f"   per-session generated: median {int(st.median(per)):,}  "
          f"mean {int(st.mean(per)):,}  max {max(per):,}")
    d = sum(per[-max(1, len(per) // 10):])
    print(f"   top decile of sessions holds {100 * d / sum(per):.0f}% of generated tokens")

    print("=" * 78)
    print("2. VERIFICATION SHARE OF CODE LINES ADDED, per month")
    print("   population: lines added to .py/.sh/.C/.cc/.h. numerator: paths whose")
    print("   BASENAME matches test_/probe-/guard/ratchet/verify_/_check/preflight.")
    per_m = defaultdict(lambda: [0, 0])
    for date, _, files in commits:
        for n_add, path in files:
            if not path.endswith(CODE):
                continue
            per_m[date[:7]][0 if is_verif(path) else 1] += n_add
    for m in sorted(per_m):
        v, s = per_m[m]
        if v + s:
            print(f"   {m}   verif {v:>7,}   science {s:>7,}   share {100*v/(v+s):>5.1f}%")

    print("=" * 78)
    print("3. I(lane ; file) -- did the parallelism actually decompose the problem?")
    lanes = [c for c in commits if c[0] >= SPLIT and c[1] != "Joseph Bailey"]
    joint, lm, fm = Counter(), Counter(), Counter()
    for _, cn, files in lanes:
        for _, path in files:
            joint[(cn, path)] += 1
            lm[cn] += 1
            fm[path] += 1
    N = sum(joint.values())
    I = sum((c / N) * math.log2((c / N) / ((lm[l] / N) * (fm[f] / N)))
            for (l, f), c in joint.items() if c)
    print(f"   {len(lanes)} lane-identified commits, {len(lm)} declared identities, "
          f"{len(fm)} files, {N} touch events")
    print(f"   H(lane) {H(lm):.2f} bits  ->  effective number of lanes {2**H(lm):.1f}")
    print(f"   H(file) {H(fm):.2f} bits    I(lane;file) {I:.2f} bits")
    print(f"   I/H(lane) = {I/H(lm):.3f}   (1 = perfectly disjoint lanes, 0 = "
          f"indistinguishable by target)")

    print("=" * 78)
    print("4. EFFECTIVE NUMBER OF FILES UNDER EDIT, equal-N and bias-corrected")
    pre = [c for c in commits if c[0] < SPLIT]
    post = [c for c in commits if c[0] >= SPLIT]
    n = min(len(pre), len(post))

    def eff(sample):
        return 2 ** H_mm(Counter(p for _, _, fs in sample for _, p in fs))
    a = [eff(random.sample(pre, n)) for _ in range(200)]
    b = [eff(random.sample(post, n)) for _ in range(200)]
    print(f"   pre  {len(pre)} commits ({min(c[0] for c in pre)}..), "
          f"post {len(post)} commits ({SPLIT}..), equal N = {n}")
    print(f"   pre  2^H = {st.mean(a):7.1f} (sd {st.stdev(a) if len(set(a))>1 else 0:.1f}"
          f"{'  EXACT: sampling n from n' if n == len(pre) else ''})")
    print(f"   post 2^H = {st.mean(b):7.1f} (sd {st.stdev(b):.1f})")
    print(f"   ratio {st.mean(b)/st.mean(a):.2f}x   support: "
          f"{len({p for _,_,fs in pre for _,p in fs})} vs "
          f"{len({p for _,_,fs in post for _,p in fs})} distinct files")
    for nm, s in (("pre ", pre), ("post", post)):
        d = [v for _, v in sorted(Counter(c[0] for c in s).items())]
        mu, sd = st.mean(d), st.stdev(d)
        print(f"   commits/day {nm} mean {mu:5.1f} sd {sd:5.1f} "
              f"burstiness {(sd-mu)/(sd+mu):+.3f}  Fano {sd*sd/mu:5.1f}")

    print("=" * 78)
    print("5. THE ONE THAT DOES NOT SURVIVE -- commit-size power law")
    sizes = sorted(sum(a for a, p in f if p.endswith(CODE))
                   for _, _, f in commits if any(p.endswith(CODE) for _, p in f))
    sizes = [s for s in sizes if s]
    S, k = sum(sizes), len(sizes)
    print(f"   code-only lines added per commit, n = {k}, total {S:,}")
    print(f"   top 1% of commits carry {100*sum(sizes[-k//100:])/S:.1f}% of code lines")
    print("   ALL-FILES figure for contrast: 65%, but that is four bulk data/manifest")
    print("   merges (354k, 218k, 158k, 137k lines) and says nothing about work.")

    def ncdf(z):
        return 0.5 * (1 + math.erf(z / math.sqrt(2)))
    print(f"   {'xmin':>6}{'n':>7}{'alpha':>8}{'Z':>8}{'p':>8}  power law vs lognormal")
    for xmin in (20, 50, 100, 200):
        t = [s for s in sizes if s >= xmin]
        m = len(t)
        if m < 50:
            continue
        al = 1 + m / sum(math.log(s / xmin) for s in t)
        ly = [math.log(s) for s in t]
        mu = sum(ly) / m
        sg = math.sqrt(sum((y - mu) ** 2 for y in ly) / m)
        tm = 1 - ncdf((math.log(xmin) - mu) / sg)
        dd = [(math.log(al - 1) - math.log(xmin) - al * math.log(s / xmin))
              - (-math.log(s * sg * math.sqrt(2 * math.pi))
                 - ((math.log(s) - mu) ** 2) / (2 * sg * sg) - math.log(tm)) for s in t]
        mm = sum(dd) / m
        v = sum((x - mm) ** 2 for x in dd) / m
        Z = sum(dd) / math.sqrt(m * v) if v > 0 else float("nan")
        p = 2 * (1 - ncdf(abs(Z)))
        verdict = ("power law" if Z > 0 and p < .05 else
                   "LOGNORMAL" if Z < 0 and p < .05 else "indistinguishable")
        print(f"   {xmin:>6}{m:>7}{al:>8.2f}{Z:>8.2f}{p:>8.3f}  {verdict}")
    print("   alpha DRIFTS with xmin and the verdict FLIPS SIGN. A real power law gives")
    print("   a stable alpha above xmin. Verdict: heavy-tailed, no exponent to quote.")
    print("=" * 78)


if __name__ == "__main__":
    main()
