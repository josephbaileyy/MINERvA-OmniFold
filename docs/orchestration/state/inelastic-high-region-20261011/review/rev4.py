import sys, json
r = json.load(open(sys.argv[1] + "/R3R4_decomposition.json"))["results"]
for k, v in r["production_S20"].items():
    c = v["inclusive_first"]["C"]
    print("S20", k, None if c is None else (round(c["ln_rho"], 4), {a: round(b, 4) for a, b in c["steps"].items()}), v["fallback"])
mx = {}
for k, v in r["production"].items():
    if k == "GiBUU": continue
    for reg in ("C", "M", "C_no_overflow", "C_overflow"):
        a, b = v["inclusive_first"][reg]["steps"], v["partition_first"][reg]["steps"]
        sd = v["mc_sd"]["inclusive_first"][reg]["steps_sd"]
        mx[(k, reg)] = (round(max(abs(a[s] - b[s]) for s in a), 4), round(max(sd.values()), 4))
print(mx)
