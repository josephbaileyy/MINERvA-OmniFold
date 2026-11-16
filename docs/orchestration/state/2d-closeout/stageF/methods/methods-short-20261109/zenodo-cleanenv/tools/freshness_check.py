"""S7: does #981's freshness rule hold for a #977 checkout's values_fived16.tex? (D6 clean-env test, addendum)

usage: python3 -I freshness_check.py <a #977 checkout's root>
#981's build requires the parsed \\fvval keys of values_fived16.tex to equal make_values_fived16.all_values().
This counts the file's fv@ keys against all_values(), groups the extra keys by prefix, and tests whether
render(all_values()) equals the file byte for byte (the paper's own freshness rule). Reads only; no bytecode written.
"""
import collections
import importlib.util
import re
import sys

sys.dont_write_bytecode = True


def main():
    root = sys.argv[1].rstrip("/")
    spec = importlib.util.spec_from_file_location("mv", f"{root}/docs/analysis-note/make_values_fived16.py")
    mv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mv)
    v = mv.all_values()
    text = open(f"{root}/docs/analysis-note/values_fived16.tex").read()
    keys = set(re.findall(r"\\@namedef\{fv@([^}]*)\}", text))
    extra, missing = sorted(keys - set(v)), sorted(set(v) - keys)
    print(f"file fv@ keys {len(keys)}; all_values {len(v)}; in the file only {len(extra)}; in all_values only {len(missing)}")
    print("in the file only, by prefix:", dict(collections.Counter(k.split("-")[0] for k in extra)))
    print("render(all_values()) equals the file:", mv.render(mv.all_values()) == text)
    print("key sets equal (necessary for #981's dict equality):", keys == set(v))


if __name__ == "__main__":
    main()
