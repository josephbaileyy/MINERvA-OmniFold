"""Claimed vs recomputed. Claimed values are typed from the task brief."""
import json
from decimal import Decimal
r = json.load(open("recompute_results.json"))
S = r["sigma"]
rows = [  # group, label, claimed (string, printed precision), recomputed
 ("sigma", "Q median %", "6.447900", S["Q"]["median"]),
 ("sigma", "Q p84 %", "9.183914", S["Q"]["p84"]),
 ("sigma", "Q max %", "23.636160", S["Q"]["max"]),
 ("sigma", "Q integral %", "4.754980", S["Q"]["integral"]),
 ("sigma", "total median %", "6.040559", S["total"]["median"]),
 ("sigma", "total integral %", "4.328436", S["total"]["integral"]),
 ("sigma", "universe median %", "5.968625", S["universe"]["median"]),
 ("sigma", "stat median %", "0.684334", S["stat"]["median"]),
 ("sigma", "c08 median %", "0.057192", S["c08"]["median"]),
 ("sigma", "C_PL median %", "2.136848", S["C_PL"]["median"]),
 ("sigma", "C_PL integral %", "1.968370", S["C_PL"]["integral"]),
 ("sigma", "universe+stat median %", "6.039778", S["universe+stat"]["median"]),
 ("sigma", "band_Flux median %", "3.746744", S["band_Flux"]["median"]),
 ("rank", "universe 1e-10", "123", r["ranks"]["universe"][0]),
 ("rank", "universe 1e-12", "137", r["ranks"]["universe"][1]),
 ("rank", "universe+stat 1e-10", "197", r["ranks"]["universe+stat"][0]),
 ("rank", "universe+stat 1e-12", "205", r["ranks"]["universe+stat"][1]),
 ("rank", "total 1e-10", "197", r["ranks"]["total"][0]),
 ("rank", "total 1e-12", "205", r["ranks"]["total"][1]),
 ("rank", "Q 1e-10", "197", r["ranks"]["Q"][0]),
 ("rank", "Q 1e-12", "205", r["ranks"]["Q"][1]),
 ("chi2", "standard chi2", "197.59", r["chi2"]["standard"]),
 ("chi2", "standard chi2/205", "0.964", r["chi2"]["standard"] / 205),
 ("chi2", "lognormal (def B) chi2", "202.33", r["chi2"]["lognormal_B"]),
 ("chi2", "lognormal (def B) chi2/205", "0.987", r["chi2"]["lognormal_B"] / 205),
 ("chi2", "stat-subtracted chi2", "1232.38", r["chi2"]["stat_subtracted"]),
 ("chi2", "stat-subtracted chi2/205", "6.012", r["chi2"]["stat_subtracted"] / 205),
 ("direct", "Q chi2/205", "23.233", r["direct"]["Q"]["ndf"]),
 ("direct", "Q cond", "8.633e11", r["direct"]["Q"]["cond"]),
 ("direct", "universe+stat chi2/205", "23.566", r["direct"]["universe+stat"]["ndf"]),
 ("direct", "universe+stat cond", "8.172e11", r["direct"]["universe+stat"]["cond"]),
]
def at_printed(claim, val):
    d = Decimal(claim)
    if "e" in claim:
        m = len(claim.split("e")[0].split(".")[1])
        return ("%.*e" % (m, val)).replace("e+", "e").replace("e0", "e") == claim.replace("e+", "e")
    q = d.as_tuple().exponent
    return Decimal(repr(float(val))).quantize(Decimal(1).scaleb(q)) == d
print("%-7s %-28s %14s %22s %12s %s" % ("group", "quantity", "claimed", "recomputed", "rel diff", "match@printed"))
for g, lab, c, v in rows:
    rd = (float(v) - float(c)) / float(c)
    print("%-7s %-28s %14s %22.12g %12.3e %s" % (g, lab, c, v, rd, at_printed(c, v)))
