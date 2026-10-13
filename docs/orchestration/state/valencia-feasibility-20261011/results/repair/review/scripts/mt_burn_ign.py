import hashlib, os, signal, threading
signal.signal(signal.SIGXCPU, signal.SIG_IGN)
threading.Timer(1.0, lambda: os._exit(42)).start()  # reviewer safety: wall stop at 1 s
buf = b"x" * (1 << 20)
def f():
    while True:
        hashlib.sha256(buf).digest()
for _ in range(10):
    threading.Thread(target=f, daemon=True).start()
threading.Event().wait()
