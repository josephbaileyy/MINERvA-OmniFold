"""FD-G-FOLLOWUP-REPORT.md section 2.5: outside the run, re-search the five committed JSON products' key names with a
plain substring rule (no word boundaries) and list every key it matches that the run's whole-word rule (in the readout)
did not. The seven npz products are on the cluster and are not searched here.
Usage (repo root): python3 -I -B <this> <readout> <definition> <s1_json> <cmodel_json> <g_readout> <g_diag_readout>"""
import json
import re
import sys

LOOSE = re.compile(r"data|reco|eff|count|nevt|n_ev|event|purity|stabil|truth|signal|accept", re.IGNORECASE)
readout, paths = json.load(open(sys.argv[1])), sys.argv[2:]
names = ("definition", "s1_json", "cmodel_json", "g_readout", "g_diag_readout")


def leaves(o):
    if isinstance(o, dict):
        for k, v in o.items():
            yield str(k)
            yield from leaves(v)
    elif isinstance(o, list):
        for v in o:
            yield from leaves(v)


for name, path in zip(names, paths):
    strict = {m.split(" / ")[-1] for m in readout["r04"]["item5_search"]["matches"][name]}
    extra = sorted({k for k in leaves(json.load(open(path))) if LOOSE.search(k)} - strict)
    print(f"{name} ({path}): {len(extra)} substring-only: {extra}")
