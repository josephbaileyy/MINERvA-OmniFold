"""Does XNU kill a SIGXCPU-ignoring process at RLIMIT_CPU hard > soft? Wall timeout 8 s per case."""
import json, resource, subprocess, sys
spin = "import signal\nsignal.signal(signal.SIGXCPU, signal.SIG_IGN)\nwhile True: pass"
out = {}
for soft, hard in ((1, 2), (1, 1)):
    def lim(s=soft, h=hard):
        resource.setrlimit(resource.RLIMIT_CPU, (s, h))
    b = resource.getrusage(resource.RUSAGE_CHILDREN)
    p = subprocess.Popen([sys.executable, "-I", "-c", spin], preexec_fn=lim)
    try:
        rc = p.wait(timeout=8); to = False
    except subprocess.TimeoutExpired:
        p.kill(); rc = p.wait(); to = True
    a = resource.getrusage(resource.RUSAGE_CHILDREN)
    out[f"soft{soft}_hard{hard}"] = {"rc": rc, "timed_out": to,
        "cpu_s": round(a.ru_utime - b.ru_utime + a.ru_stime - b.ru_stime, 3)}
print(json.dumps(out))
