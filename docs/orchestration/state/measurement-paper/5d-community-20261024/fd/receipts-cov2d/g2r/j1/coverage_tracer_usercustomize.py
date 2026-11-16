# COV2D-G2R J1's line tracer: as amendment 1's (coverage_tracer_usercustomize.py), but G2R_TRACE_SUFFIXES names files by
# their repository-relative path, so a test's fixture deploy (a copy of the tree at another path) is traced too. At
# exit it records each traced file's sha256; the reader counts a copy's hits only if that sha256 equals the worktree
# file's.
import atexit, os, sys, threading
_OUT = os.environ.get("G2R_TRACE_OUT")
if _OUT:
    _S = tuple(os.environ["G2R_TRACE_SUFFIXES"].split(":"))
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
        if _rp(frame.f_code.co_filename).endswith(_S):
            _hits.add((_rp(frame.f_code.co_filename), frame.f_lineno))
            return _local
        return None

    sys.settrace(_global)
    threading.settrace(_global)

    @atexit.register
    def _dump():
        import hashlib
        with open(os.path.join(_OUT, f"{os.getpid()}.txt"), "w") as fh:
            for p in sorted({p for p, _ in _hits}):
                try:
                    with open(p, "rb") as src:
                        fh.write(f"#sha256 {hashlib.sha256(src.read()).hexdigest()} {p}\n")
                except OSError:
                    pass
            for p, l in sorted(_hits):
                fh.write(f"{p}:{l}\n")
