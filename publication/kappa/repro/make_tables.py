#!/usr/bin/env python3
"""Render the tables of kappa_repro_results.json as markdown (stdout). Usage: make_tables.py <results.json>"""
import json
import sys

R = json.load(open(sys.argv[1]))
ABBR = {"rejected": "R", "undetermined": "U", "not rejected": "N"}
OWN = {"below": "b", "straddles": "s", "above": "a"}


def short(key):
    g, s = key.split(":")
    g = {"MnvTune_v1": "Tune", "GENIE_2_12_10_CV": "GCV", "GENIE_2_12_10_MEC": "GMEC", "NuWro_21_09": "NuWro",
         "GiBUU_2019": "GiBUU"}[g]
    return f"{g}:{s[0].upper()}"


def compact(task):
    T = R[task]
    kappas = list(T)
    keys = list(T[kappas[0]])
    print("| test | " + " | ".join(kappas) + " |")
    print("|---|" + "---|" * len(kappas))
    for key in keys:
        cells = [f"{ABBR[T[k][key]['decision']]} k={T[k][key]['k']} ({OWN[T[k][key]['own_status']]})" for k in kappas]
        print(f"| {short(key)} | " + " | ".join(cells) + " |")
    print()


def full(task):
    T = R[task]
    for kap, dec in T.items():
        print(f"**kappa = {kap}**\n")
        print("| test | k | B | p | step | threshold | CP 95% | own | decision |")
        print("|---|---|---|---|---|---|---|---|---|")
        for key, d in sorted(dec.items(), key=lambda kv: kv[1]["step"]):
            lo, hi = d["interval"]
            print(f"| {key} | {d['k']} | {d['B']} | {d['p']:.6g} | {d['step']} | {d['threshold']:.6g} | "
                  f"[{lo:.6g}, {hi:.6g}] | {d['own_status']} | {d['decision']} |")
        print()


def mono():
    M = R["task4_monotonicity_frozen_family_A"]
    grid = M["grid"]
    keys = list(M["claim_k"][repr(grid[0])])
    print("| test | " + " | ".join(f"{g:g}" for g in grid) + " |")
    print("|---|" + "---|" * len(grid))
    for key in keys:
        print(f"| {short(key)} | " + " | ".join(str(M["claim_k"][repr(g)][key]) for g in grid) + " |")
    print(f"\nDecreases: {M['decreases'] if M['decreases'] else 'none'}\n")


if __name__ == "__main__":
    which = sys.argv[2]
    {"c2": lambda: compact("task2_frozen_family_A"), "c3": lambda: compact("task3_union_family_A"),
     "f2": lambda: full("task2_frozen_family_A"), "f3": lambda: full("task3_union_family_A"), "m": mono}[which]()
