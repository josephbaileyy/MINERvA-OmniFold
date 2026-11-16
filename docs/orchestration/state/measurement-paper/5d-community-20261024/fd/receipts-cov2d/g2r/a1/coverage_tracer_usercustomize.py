import atexit, os, sys, threading
_OUT = os.environ.get("G2R_TRACE_OUT")
if _OUT:
    _T = tuple(os.path.realpath(p) for p in os.environ["G2R_TRACE_FILES"].split(":"))
    _hits = set()
    _real = {}

    def _rp(f):
        r = _real.get(f)
        if r is None:
            r = _real[f] = os.path.realpath(f)
        return r

    def _local(frame, event, arg):
        if event == "line":
            _hits.add((_rp(frame.f_code.co_filename), frame.f_lineno))
        return _local

    def _global(frame, event, arg):
        if _rp(frame.f_code.co_filename) in _T:
            _hits.add((_rp(frame.f_code.co_filename), frame.f_lineno))
            return _local
        return None

    sys.settrace(_global)
    threading.settrace(_global)

    @atexit.register
    def _dump():
        with open(os.path.join(_OUT, f"{os.getpid()}.txt"), "w") as fh:
            for f, l in sorted(_hits):
                fh.write(f"{f}:{l}\n")
