#!/usr/bin/env python3
"""Slide 3's authorship floor: how many commits are attributed to a human but carry
positive evidence of agent authorship?

WHY A LOWER BOUND AND NOT AN ESTIMATE. The `Claude-Session` trailer is present only when
a session was configured to emit it, so its ABSENCE proves nothing. That makes every
number here one-directional: a commit counted is definitely mis-attributed, and the
commits not counted are UNMEASURED rather than clean. The 2,581 commits with no trailer
support no claim at all, in either direction.

WHAT WOULD MAKE THIS WRONG IN THE OTHER DIRECTION: a commit whose body quotes the
trailer without being agent-authored (a handoff document pasted into a message, say).
Not observed here, but the check is a substring match and cannot exclude it.

Exit 0 = measured. Exit 2 = cannot check. There is no failure exit: this reports.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HUMAN = "Joseph Bailey"
TRAILER = "Claude-Session"

out = subprocess.run(["git", "log", "--format=\x01%H\x02%cn\x02%B"],
                     cwd=REPO, capture_output=True, text=True)
if out.returncode != 0:
    sys.exit(f"CANNOT CHECK :: git log exited {out.returncode}\n{out.stderr}")

records = [r.split("\x02") for r in out.stdout.split("\x01") if r.strip()]
records = [r for r in records if len(r) > 2]
if not records:
    sys.exit("CANNOT CHECK :: git log returned no parseable records. A tally of zero "
             "here means the parse could not look, not that there are no commits.")

total = len(records)
trailer = sum(TRAILER in "\x02".join(r[2:]) for r in records)
human = sum(r[1] == HUMAN for r in records)
mislabelled = sum(r[1] == HUMAN and TRAILER in "\x02".join(r[2:]) for r in records)

if trailer == 0:
    sys.exit("CANNOT CHECK :: no commit carries the trailer, so this parse has not been "
             "shown to detect one. Without that positive control a zero is not a result.")

print(f"commits parsed              = {total}")
print(f"trailer={trailer}  under-my-name={mislabelled}")
print(f"committer '{HUMAN}'         = {human}")
print()
print(f"LOWER BOUND on mis-attribution: {mislabelled} commits "
      f"({100 * mislabelled / trailer:.0f}% of the {trailer} commits that carry ANY "
      f"positive authorship evidence; {100 * mislabelled / human:.1f}% of the {human} "
      f"attributed to me).")
print(f"UNMEASURED: the {total - trailer} commits with no trailer. Not clean -- unmeasured.")
