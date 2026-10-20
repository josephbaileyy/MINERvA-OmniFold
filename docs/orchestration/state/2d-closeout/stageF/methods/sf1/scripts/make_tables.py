"""SF-1 task tables (SF1-SPEC.md section 2).

For each null, the first 200 seeds of its production calibration ensemble by seed order (finished products only,
the production glob of prod/design.json, partials excluded), and s5c_array.sh task tables whose lines are the
production task-table line of that null (prod/tables/cal-<null>-b0.tsv) with exactly three changes:
--mc-fraction quarter added, --pseudo-seeds set to the item's seeds, and --tag/--out pointing to the SF-1 tree.

usage: make_tables.py dryrun | main
"""
import glob, json, sys
from pathlib import Path

S = Path("/pscratch/sd/j/josephrb/methods-paper/sf1-20261019")
D = S / "deploy-4f5a613f"
NULLS = ["NuWro_21_09", "GENIE_2_12_10_CV", "GENIE_2_12_10_MEC"]
design = json.loads((D / "docs/orchestration/state/s5p/prod/design.json").read_text())


def first200(null):
    files = [p for p in glob.glob(design["nulls"][null]["calibration_glob"]) if ".partial" not in Path(p).name]
    seeds = sorted(int(Path(p).stem.rsplit("_s", 1)[1]) for p in files)
    return seeds[:200], len(seeds)


def prod_args(null):
    lines = [l for l in (D / f"docs/orchestration/state/s5p/prod/tables/cal-{null}-b0.tsv").read_text().splitlines()
             if l and not l.startswith("#")]
    f = lines[0].split("\t")
    assert f[1] == "s5p_nullexp.py"
    args = f[2:]
    i = args.index("--pseudo-seeds")
    del args[i:i + 2]
    for k in ("--tag", "--out"):
        i = args.index(k)
        del args[i:i + 2]
    # every production line of this table must carry the same args apart from seeds
    for l in lines[1:]:
        g = l.split("\t")[2:]
        j = g.index("--pseudo-seeds"); del g[j:j + 2]
        for k in ("--tag", "--out"):
            j = g.index(k); del g[j:j + 2]
        assert g == args, l
    return args


def line(name, null, first, last, quarter=True, out=None, tag=None):
    a = prod_args(null) + (["--mc-fraction", "quarter"] if quarter else []) + \
        ["--pseudo-seeds", f"{first}:{last}", "--tag", tag or f"sf1q_{null}", "--out", str(out or S / "runs/quarter" / null)]
    return "\t".join([name, "s5p_nullexp.py"] + a)


def chunks(seeds, size=2):
    out, cur = [], []
    for s in seeds:
        if cur and (s != cur[-1] + 1 or len(cur) == size):
            out.append(cur); cur = []
        cur.append(s)
    if cur:
        out.append(cur)
    return out


def main(mode):
    sel = {}
    for n in NULLS:
        seeds, total = first200(n)
        sel[n] = {"seeds": seeds, "ensemble_B": total}
        (S / "tables").mkdir(exist_ok=True)
        (S / "tables" / f"seeds-{n}.txt").write_text("\n".join(map(str, seeds)) + "\n")
    (S / "tables" / "selection.json").write_text(json.dumps({n: {"n": len(v["seeds"]), "first": v["seeds"][0],
        "last": v["seeds"][-1], "ensemble_B": v["ensemble_B"]} for n, v in sel.items()}, indent=1) + "\n")
    if mode == "dryrun":
        n = "NuWro_21_09"; s = sel[n]["seeds"]
        rows = [line("sf1-dry-q0", n, s[0], s[0]),
                line("sf1-dry-h0", n, s[0], s[0], quarter=False, out=S / "runs/halfcheck" / n, tag=f"cal_{n}")]
        rows += [line(f"sf1-dry-q{i}", n, x, x) for i, x in enumerate(s[1:7], start=1)]
        (S / "tables" / "dryrun.tsv").write_text("# SF-1 dry run (SF1-SPEC step 1): NuWro quarter seeds s[0..6] and the half rerun of s[0]\n" + "\n".join(rows) + "\n")
        print(len(rows), "dry-run lines")
        return
    # main: every selected seed without a finished quarter product, split per null into two jobs
    for n in NULLS:
        qdir = S / "runs/quarter" / n
        done = {int(Path(p).stem.rsplit("_s", 1)[1]) for p in glob.glob(str(qdir / f"sf1q_{n}_s*.npz")) if ".partial" not in Path(p).name}
        todo = [x for x in sel[n]["seeds"] if x not in done]
        half = (len(todo) + 1) // 2
        for part, ss in (("a", todo[:half]), ("b", todo[half:])):
            rows = [line(f"sf1-{n}-{part}{i}", n, c[0], c[-1]) for i, c in enumerate(chunks(ss))]
            (S / "tables" / f"main-{n}-{part}.tsv").write_text(f"# SF-1 main runs: {n} part {part}, {len(ss)} seeds\n" + "\n".join(rows) + "\n")
            print(n, part, len(ss), "seeds", len(rows), "lines")


if __name__ == "__main__":
    main(sys.argv[1])
