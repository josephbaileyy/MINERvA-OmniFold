"""The audit-sensitive operations of g2r_readout.py (at 401733bc), done as the readout does them, under the open audit
installed as cov2d_readout.Run installs it, with the guarded trees = cov2d_blocks.GUARDED plus G2R_GUARD (a local
stand-in for /pscratch). Used by test_readout_place.sh only; it does not run a phase (that needs real products).
    python test_readout_place.py <checkout to import from> <products tsv> <out dir>      (TMPDIR from the environment)
Prints one line per operation, OK or REFUSED (or ERROR), then a JSON summary; exit 0 only if every one is OK."""
import csv
import gzip
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

root, tsv, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
G = os.path.realpath(os.environ["G2R_GUARD"])
sys.path.insert(0, str(root / "2d-unfolding/cov2d/g2r"))
import g2r_readout as gr  # noqa: E402
import cov2d_blocks as cb  # noqa: E402
import numpy as np  # noqa: E402

guarded = tuple(cb.GUARDED) + (G,)
cb.OpenAudit.__init__.__defaults__ = (guarded,)
cb.AUDIT = cb.OpenAudit().install()          # cov2d_readout.Run: cb.AUDIT = cb.OpenAudit().install(ROOT)
res = {}


def op(name, f):
    try:
        f()
        res[name] = "OK"
    except Exception as exc:                 # cov2d.Refusal from the audit, or anything else
        res[name] = "REFUSED" if "open audit" in str(exc) else f"ERROR {type(exc).__name__}: {exc}"
    print(name, res[name], flush=True)


def budget():                                # g2r_readout.py:285-287
    raw = gzip.decompress((gr.OUTA / "budget_Q.json.gz").read_bytes())
    assert hashlib.sha256(raw).hexdigest() == gr.BUDGET_Q, "budget_Q.json is not at its digest"


def tempdir():                               # :203 and :266 (TemporaryDirectory under $TMPDIR; a write; its rmtree)
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
        (Path(td) / "products").mkdir()
        (Path(td) / "products" / "x.root").write_bytes(b"x")


def products():                              # :161 (the products TSV, opened plainly)
    with open(tsv, newline="") as fh:
        assert [r for r in csv.reader(fh, delimiter="\t") if r]


def out_npz():                               # :251, :315
    np.savez(out / "blocks_g2r_X.npz", a=np.zeros(3))


def out_json():                              # cov2d_readout.Run.finish: (out / name).write_text(...)
    (out / "data_g2r.json").write_text(json.dumps({"t": 1}))


def modules():                               # Run.finish: modules imported from outside the clone are a STOP
    mods = {m.__name__: os.path.realpath(m.__file__) for m in (gr, cb)}
    rp = os.path.realpath(gr.REPO)
    outside = [k for k, f in mods.items() if not f.startswith(rp + os.sep)]
    assert not outside, f"outside the clone: {outside}"
    if rp.startswith(guarded):
        raise RuntimeError(f"open audit: REPO {rp} is under a guarded tree")


for name, f in (("budget", budget), ("tempdir", tempdir), ("products_tsv", products), ("out_npz", out_npz),
                ("out_json", out_json), ("modules", modules)):
    op(name, f)
cb.AUDIT.uninstall()
print(json.dumps({"repo": os.path.realpath(gr.REPO), "results": res, "refused": len(cb.AUDIT.refused)}))
sys.exit(0 if all(v == "OK" for v in res.values()) else 1)
