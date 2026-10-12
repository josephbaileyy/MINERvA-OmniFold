"""Print verify_hash_bindings' full resolved-binding status table for a tree.

Usage: python3.12 binding_table.py <tree-root>
One TSV row per deduplicated binding: rel, want, src-or-blank, status (OK/KNOWN/MISMATCH).
Replicates main()'s collection and dedupe by calling the verifier's own functions.
"""
import glob, importlib.util, json, os, sys

root = os.path.abspath(sys.argv[1])
spec = importlib.util.spec_from_file_location(
    "vhb", os.path.join(root, "docs/orchestration/verify_hash_bindings.py"))
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

receipt_pairs, unpaired, revpinned, fixture_pairs = [], [], [], []
for f in (glob.glob(os.path.join(root, "docs/**/*.json"), recursive=True)
          + glob.glob(os.path.join(root, "nd-unfolding/**/*.json"), recursive=True)):
    try:
        doc = json.load(open(f))
    except (json.JSONDecodeError, OSError):
        continue
    rel = os.path.relpath(f, root)
    if isinstance(doc, dict) and v.NEGATIVE_CONTROL_MARKER in doc:
        v.collect(doc, rel, fixture_pairs, None)
        continue
    try:
        v.collect(doc, rel, receipt_pairs, unpaired, revpinned)
    except OSError:
        continue
shell_pairs, shell_unwalked = [], []
for f in (glob.glob(os.path.join(root, "docs/**/*.sh"), recursive=True)
          + glob.glob(os.path.join(root, "nd-unfolding/**/*.sh"), recursive=True)
          + glob.glob(os.path.join(root, "2d-unfolding/**/*.sh"), recursive=True)):
    try:
        v.collect_shell(open(f).read(), os.path.relpath(f, root), shell_pairs, shell_unwalked)
    except OSError:
        continue
py_pairs, py_unwalked = [], []
for f in v.py_files(root):
    try:
        v.collect_python(open(f).read(), os.path.relpath(f, root), py_pairs, py_unwalked)
    except (OSError, UnicodeDecodeError):
        continue

seen = set()
for p, want, src in receipt_pairs + shell_pairs + py_pairs:
    lp = v.localize(p, root)
    if lp is None:
        continue
    rel = os.path.relpath(lp, root)
    code_site = src.endswith((".sh", ".py"))
    key = (rel, want, src if code_site else "")
    if key in seen:
        continue
    seen.add(key)
    if v.sha256(lp) == want:
        st = "OK"
    elif (rel, src, want) in v.KNOWN_PREEXISTING:
        st = "KNOWN"
    else:
        st = "MISMATCH"
    print(f"{rel}\t{want}\t{src}\t{st}")
