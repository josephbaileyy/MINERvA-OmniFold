import hashlib, threading
buf = b"x" * (1 << 20)
def f():
    while True:
        hashlib.sha256(buf).digest()
for _ in range(10):
    threading.Thread(target=f, daemon=True).start()
threading.Event().wait()
