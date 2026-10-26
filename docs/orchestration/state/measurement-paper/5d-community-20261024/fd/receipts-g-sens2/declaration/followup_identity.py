"""FD-G-SENS2-DECLARATION.md section 6.1: run main's fd_g_followup.py (at the given source file) and this tree's,
with the G-FOLLOWUP part (no --part), on the same synthetic trees and the same argv, and compare:
* the readout files byte for byte, after the one field that must differ, code_sha256["fd_g_followup.py"], is set to
  main's digest in this tree's readout (the readout embeds its own tool's sha256);
* stdout line for line, apart from the final "wrote" line, whose sha256 is of that readout;
and a control: the same comparison reports a difference when one label of this tree's tool is changed.
Usage: python3 -I -B followup_identity.py <worktree> <main's fd_g_followup.py>"""
import contextlib
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
from pathlib import Path
from unittest import mock

wt, main_src = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(wt / "nd-unfolding"))
sys.path.insert(0, str(wt / "nd-unfolding/tests"))
import fd_g_followup as NEW  # noqa: E402
import test_fd_g_followup as T  # noqa: E402

spec = importlib.util.spec_from_file_location("fd_g_followup_main", main_src)
OLD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(OLD)
sha = {m: hashlib.sha256(p.read_bytes()).hexdigest() for m, p in (("main", main_src), ("this", Path(NEW.__file__)))}
for m, h in sha.items():
    print(f"{m}: fd_g_followup.py sha256 {h}")
bad = 0
for seed in (0, 1, 2):
    for role in ("adopted", "sensitivity"):
        tree = T.FollowupTree(Path(tempfile.mkdtemp()) / "t", seed=seed).write(role=role)
        outs = {}
        for name, mod in (("main", OLD), ("this", NEW)):
            o = tree.out / f"{name}.json"
            argv = tree.fargv[:-1] + [str(tree.out / "readout.json")]
            buf = io.StringIO()
            with mock.patch.object(sys, "argv", ["fd_g_followup.py"] + argv), contextlib.redirect_stdout(buf):
                rc = mod.run(mod.build_args(argv), tree.fpins, tree.predictions)
            (tree.out / "readout.json").rename(o)
            outs[name] = (rc, o.read_bytes(), buf.getvalue().splitlines()[:-1])
        new_bytes = outs["this"][1].replace(sha["this"].encode(), sha["main"].encode())
        same_bytes = outs["main"][1] == new_bytes
        same_out = outs["main"][2] == outs["this"][2]
        n_sub = outs["this"][1].count(sha["this"].encode())
        bad += not (same_bytes and same_out and n_sub == 1)
        print(f"seed {seed} role {role}: rc {outs['main'][0]}/{outs['this'][0]}; readout {len(outs['main'][1])} B, "
              f"{'byte-identical' if same_bytes else 'DIFFERS'} after {n_sub} substitution of the tool's own sha256; "
              f"stdout {len(outs['main'][2])} lines {'identical' if same_out else 'DIFFER'}")
# the comparison's control: one label changed in this tree's tool must be reported as a difference
tree = T.FollowupTree(Path(tempfile.mkdtemp()) / "t", seed=0).write()
got = {}
for name, mod, patch in (("main", OLD, {}), ("this", NEW, {"what": "changed"})):
    argv = tree.fargv[:-1] + [str(tree.out / "readout.json")]
    with mock.patch.object(sys, "argv", ["fd_g_followup.py"] + argv), mock.patch.dict(mod.LABELS, patch),             contextlib.redirect_stdout(io.StringIO()):
        mod.run(mod.build_args(argv), tree.fpins, tree.predictions)
    got[name] = (tree.out / "readout.json").read_bytes()
    (tree.out / "readout.json").unlink()
caught = got["main"] != got["this"].replace(sha["this"].encode(), sha["main"].encode())
bad += not caught
print(f"control: one changed label is {'reported as a difference' if caught else 'NOT DETECTED'}")
print("identical on all 6, control fires" if not bad else f"{bad} failures")
raise SystemExit(1 if bad else 0)
