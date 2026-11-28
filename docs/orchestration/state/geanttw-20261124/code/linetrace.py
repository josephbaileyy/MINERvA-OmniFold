#!/usr/bin/env python3
"""Line trace of the geanttw P0 package under its own tests.

    python3 linetrace.py [--out linetrace.txt]

Everything runs in a scratch copy of this directory; nothing here is modified.

  - Python (dumpcmp.py, p0_check.py, geanttw_sacct.py, geanttw_provenance.py): coverage.py, with `patch = subprocess`, so the tests' `python3 -I` child
    processes are measured too. The report lists every executable line that no test runs.
  - Shell (geanttw_evloop.sbatch, geanttw_build.sh, geanttw_connect.sh, geanttw_remote.sh): in the copy, one line is inserted after
    the shebang. It sets a DEBUG trap (with set -T, so functions inherit it) that writes '+<file>:<line>:' to a
    trace file. bash 3.2 on macOS has no BASH_XTRACEFD. Lines are mapped back to the original numbering (minus 1). A shell line counts as executable unless it is blank, a comment, an SBATCH
    header, a heredoc body, the inside of a multi-line quoted string, a continuation line or a case label. The report lists every executable line that never appears in the trace.
"""
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = ["dumpcmp.py", "p0_check.py", "geanttw_sacct.py", "geanttw_provenance.py"]
SH = ["geanttw_evloop.sbatch", "geanttw_build.sh", "geanttw_connect.sh", "geanttw_remote.sh"]
HEREDOC = re.compile(r"<<-?\s*['\"]?([A-Za-z_]+)['\"]?")


CASE_LABEL = re.compile(r"^[A-Za-z0-9_|*.-]+\)$")


def shell_executable(text):
    """Executable lines: not blank, not a comment, not a heredoc body, not the inside of a multi-line quoted string
    (a `python3 -c "..."` body), not a continuation of the previous line (`\\`), not a bare case label and not a
    block keyword. bash's DEBUG trap fires once per simple command, usually on its first line; inside a command
    substitution that continues over `\\` lines, bash 3.2 reports the last line instead. So the second value maps every
    continuation line to the line its command starts on, and a hit there counts for that line."""
    lines, out, term, in_str, cont = text.splitlines(), set(), None, False, False
    owner, start = {}, None
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        if term is not None:
            if s == term:
                term = None
            continue
        if in_str:
            if ln.count('"') % 2 == 1:
                in_str = False
            continue
        was_cont, cont = cont, ln.rstrip().endswith("\\")
        if not was_cont:
            start = i
        elif start is not None:
            owner[i] = start
        if not s.startswith("#") and ln.count('"') % 2 == 1:
            in_str = True
        if was_cont or CASE_LABEL.match(s):
            continue
        m = HEREDOC.search(ln)
        if m and not s.startswith("#"):
            term = m.group(1)
        if not s or s.startswith("#") or s in ("fi", "done", "esac", "}", "else", "then", "do", ";;", "EOF"):
            continue
        out.add(i)
    return out, owner


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "linetrace.txt"))
    args = ap.parse_args()
    report = []
    with tempfile.TemporaryDirectory(prefix="geanttw-trace-") as td:
        work = Path(td) / "code"
        shutil.copytree(HERE, work, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "mutation.out",
                                                                  "linetrace*.txt"))
        trace = Path(td) / "sh.trace"
        for name in SH:
            p = work / name
            lines = p.read_text().splitlines(keepends=True)
            # macOS bash 3.2 has no BASH_XTRACEFD, so a DEBUG trap (inherited by functions under set -T) writes
            # each line number to fd 9 instead of xtrace, which would land in the tests' captured stderr.
            inject = (f'exec 9>>"{trace}"; set -T; '
                      f"trap 'echo \"+{name}:$LINENO:\" >&9' DEBUG\n")
            p.write_text(lines[0] + inject + "".join(lines[1:]))
            p.chmod((HERE / name).stat().st_mode)
        rc = work / ".coveragerc"
        rc.write_text(f"[run]\npatch = subprocess\nparallel = True\ndata_file = {td}/.coverage\n"
                      f"source = {work}\n")
        env_cmd = [sys.executable, "-m", "coverage", "run", f"--rcfile={rc}", "-m", "pytest", "tests", "-q",
                   "-p", "no:cacheprovider"]
        r = subprocess.run(env_cmd, cwd=work, capture_output=True, text=True)
        report.append(f"pytest under trace: rc={r.returncode}; {r.stdout.strip().splitlines()[-1] if r.stdout else ''}")
        subprocess.run([sys.executable, "-m", "coverage", "combine", f"--rcfile={rc}"], cwd=work,
                       capture_output=True, text=True)
        cov = subprocess.run([sys.executable, "-m", "coverage", "report", "-m", f"--rcfile={rc}",
                              "--include=" + ",".join(str(work / n) for n in PY)], cwd=work,
                             capture_output=True, text=True)
        report.append("")
        report.append("== Python line coverage (coverage.py, subprocesses included) ==")
        report.append(cov.stdout.replace(str(work) + "/", "").rstrip())
        hit = {}
        if trace.exists():
            for ln in trace.read_text(errors="replace").splitlines():
                m = re.match(r"^\++([A-Za-z_.]+):(\d+):", ln)
                if m:
                    hit.setdefault(m.group(1), set()).add(int(m.group(2)) - 1)
        report.append("")
        report.append("== Shell line trace (DEBUG trap; heredoc bodies, comments and block keywords excluded) ==")
        for name in SH:
            exe, owner = shell_executable((HERE / name).read_text())
            got = {owner.get(i, i) for i in hit.get(name, set())} & exe
            miss = sorted(exe - got)
            report.append(f"{name}: {len(got)}/{len(exe)} executable lines traced; not traced: "
                          f"{', '.join(map(str, miss)) if miss else 'none'}")
    Path(args.out).write_text("\n".join(report) + "\n")
    print("\n".join(report))


if __name__ == "__main__":
    main()
