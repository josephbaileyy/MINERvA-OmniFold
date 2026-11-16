"""receipt_inventory() rows with and without one receipt, by verify_hash_bindings.py's own collect(),
tracked_paths() and receipt_inventory(), over docs/**/*.json and nd-unfolding/**/*.json, fixtures excluded, as its
main() collects them. Usage: python3 -B binding_delta.py <repo root> <receipt rel path>"""
import glob, json, os, sys
root, target = os.path.abspath(sys.argv[1]), sys.argv[2]
sys.path.insert(0, os.path.join(root, "docs", "orchestration"))
import verify_hash_bindings as V
def rows(skip):
    pairs = []
    for f in (glob.glob(os.path.join(root, "docs/**/*.json"), recursive=True)
              + glob.glob(os.path.join(root, "nd-unfolding/**/*.json"), recursive=True)):
        rel = os.path.relpath(f, root)
        if skip and rel == target:
            continue
        try:
            doc = json.load(open(f))
        except (json.JSONDecodeError, OSError):
            continue
        if isinstance(doc, dict) and V.NEGATIVE_CONTROL_MARKER in doc:
            continue
        try:
            V.collect(doc, rel, pairs, [], [])
        except OSError:
            continue
    return V.receipt_inventory(pairs, root, V.tracked_paths(root))
(w0, d0), (w1, d1) = rows(True), rows(False)
print(f"without: {len(w0)} rows, sha256 {d0} (constant {V.RECEIPT_BINDING_COUNT} / {V.RECEIPT_BINDING_SHA256})")
print(f"with:    {len(w1)} rows, sha256 {d1}")
for r in sorted(set(w1) - set(w0)):
    print(f"  ADDED   {r[0]} {r[1][:8]}")
for r in sorted(set(w0) - set(w1)):
    print(f"  REMOVED {r[0]} {r[1][:8]}")
