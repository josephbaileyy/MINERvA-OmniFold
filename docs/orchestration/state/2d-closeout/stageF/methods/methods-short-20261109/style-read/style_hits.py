import sys, json, importlib.util
spec=importlib.util.spec_from_file_location("sm", sys.argv[1]); sm=importlib.util.module_from_spec(spec); spec.loader.exec_module(sm)
r=sm.score(open(sys.argv[2],encoding="utf-8",errors="replace").read(), n_examples=999)
print("words",r["words"])
for k in ["1_comma_not","4_corrective","5_semicolon_chain"]:
    e=r["patterns"][k]; print("===",k,e["count"],e["per_1000"])
    for x in e["examples"]: print("  [%s] %s"%(x["match"],x["sentence"][:300]))
