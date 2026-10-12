#!/usr/bin/env python3
"""Preflight control: a guarded child that starts a process the OI-136 guard must refuse.

Run by ``launch/xr_job.sbatch`` under ``nd-unfolding/mnv_guarded_run.py`` before the preflight. On
Linux it calls ``threadpoolctl.threadpool_info()``, the call that reached ``/sbin/ldconfig -p``
through ``ctypes.util.find_library`` in the 2026-10-11 preflight; elsewhere (the tests) it runs
loky's macOS query, ``sysctl -n hw.physicalcpu``. The guard must refuse the launch, so this script
exits non-zero with the guard's banner on stderr. Exit 0 means the launch was NOT refused: the
control failed. It shows the guard is still strict; it is not part of any run's path.
"""
import subprocess
import sys

if sys.platform.startswith("linux"):
    import threadpoolctl
    threadpoolctl.threadpool_info()
else:
    subprocess.run(["sysctl", "-n", "hw.physicalcpu"], check=False)
print("[xr-guard-control] the launch was not refused", file=sys.stderr)
sys.exit(0)
