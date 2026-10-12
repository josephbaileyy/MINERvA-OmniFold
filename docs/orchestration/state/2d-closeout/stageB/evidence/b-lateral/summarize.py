import json,glob,sys
for fn in sorted(glob.glob("cmp_*.json")):
    try: d=json.load(open(fn))
    except Exception: print(fn,"not ready"); continue
    s=d["signal"]
    print(fn.replace("cmp_","").replace(".json",""))
    print("  rows",s["rows"],"MC==",s["mc_equal"],"MCpz==",s["mcpz_equal"],"MCshift==act",s["mcshift_equal"],"wtruth==",s["wtruth_equal"],"wtruth_u==",s["wtruth_u_equal"])
    print("  cv_pass",s["cv_pass"],"act_pass",s["act_pass"],"dump_win",s["dump_win"],"act_win",s["act_win"],"both",s["both"],"dump_only",s["dump_only"],"act_only",s["act_only"])
    print("  on both: sim==",s["sim_equal_both"],"simpz==",s["simpz_equal_both"],"wreco==",s["wreco_equal_both"])
    print("  bkg",d["bkg"])
    print("  sig reco rel err (dump-act)/cv",d["sig_reco_rel_err"],"| act shift",d["sig_reco_rel_shift_active"],"| |err|/|shift|",d["err_over_shift"],"| bkg rel err",d["bkg_rel_err"],"| s",round(d["seconds"]))
