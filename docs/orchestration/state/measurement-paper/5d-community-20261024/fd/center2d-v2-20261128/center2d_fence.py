"""CENTER2D fence decision (laptop only; reads the two files center2d_fetch.sh wrote, nothing else).

usage: python3 -I -B center2d_fence.py "FAMILY ..." SACCT_TXT SQUEUE_TXT

SACCT_TXT is `sacct -X -n -P -u josephrb -S now-14days -o JobID,JobName,State` (no -s: sacct's -s selects jobs that
were in a state at any time in the window, so it would refuse on jobs that have since ended). A row of a fenced family
(job name starting with a family, case-insensitive) refuses unless its State is terminal. SQUEUE_TXT is
`squeue -h -u josephrb -o "%i|%j|%T"`: squeue lists only live jobs, so any fenced-family row there refuses.

Fail closed: a row with fewer than three fields refuses, and so does a fenced-family row whose State is not in the
terminal list (an unknown state is not terminal).

Prints the number of refusing rows on stdout (0 means clear) and each refusing row on stderr; exits 0 when it could
decide, 2 on a usage error.
"""
import sys

TERMINAL = ("COMPLETED", "FAILED", "TIMEOUT", "OUT_OF_MEMORY", "NODE_FAIL", "PREEMPTED", "BOOT_FAIL", "DEADLINE",
            "REVOKED")


def terminal(state: str) -> bool:
    s = state.strip().upper()
    return s in TERMINAL or s == "CANCELLED" or s.startswith("CANCELLED ")


def hits(families, sacct_lines, squeue_lines) -> list:
    fam = tuple(f.lower() for f in families)
    bad = []
    for source, lines, live in (("sacct", sacct_lines, False), ("squeue", squeue_lines, True)):
        for ln in lines:
            if not ln.strip():
                continue
            p = ln.rstrip("\n").split("|")
            if len(p) < 3:
                bad.append(f"{source} malformed: {ln.strip()}")
                continue
            if not p[1].strip().lower().startswith(fam):
                continue
            if live or not terminal(p[2]):
                bad.append(f"{source}: {ln.strip()}")
    return bad


def main(argv) -> int:
    if len(argv) != 4 or not argv[1].split():
        print("usage: center2d_fence.py \"FAMILY ...\" SACCT_TXT SQUEUE_TXT", file=sys.stderr)
        return 2
    with open(argv[2]) as f:
        sa = f.readlines()
    with open(argv[3]) as f:
        sq = f.readlines()
    bad = hits(argv[1].split(), sa, sq)
    print(len(bad))
    for b in bad:
        print(b, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
