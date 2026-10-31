"""Apply r22 Step 2's adoption rule (STEP2-PLAN.md §4, committed before any score) to each note piece.

usage: python3 -I adopt_step2.py R22_DIR RUNS_DIR [--base-runs DIR --base-pattern PAT] [--self-test]
A piece is adopted if, and only if, all three hold:
  1. NEW beats the base in at least 3 of the 4 blind P2N runs (sol2 and gemini, each in both orders); a run without a
     WINNER line (failed both attempts) counts as a loss for NEW;
  2. sol2 picks the same version in both orders;
  3. NEW's 3 sol2 P1N runs have a mean at least the base's mean and a lowest run at least the base's lowest run (base:
     R22_DIR/runs/P1N__<id>__sol2__r{1,2,3}.txt, Step 1; or --base-runs DIR with --base-pattern PAT, where PAT has {i}
     for the piece and {k} for the run: Step 3's base is the note round's adopted runs, step2/runs/P1N.{i}.sol2.r{k}.txt).
Writes RUNS_DIR/adoption.tsv and prints one line per piece. AB: A = base, B = NEW; BA: A = NEW, B = base."""
import re
import statistics as st
import sys
from pathlib import Path


def winner(p):
    m = re.search(r"WINNER:\s*\**\s*([AB])", p.read_text()) if p.exists() else None
    return m.group(1) if m else None


def rating(p):
    m = re.search(r"^RATING:\s*\**\s*([0-9.]+)", p.read_text(), re.M) if p.exists() else None
    return float(m.group(1)) if m else None


def decide(R, D, ids, base_dir=None, pat="P1N__{i}__sol2__r{k}.txt"):
    rows = []
    for i in ids:
        v = {}
        for m in ("sol2", "gemini"):
            for o in ("AB", "BA"):
                w = winner(D / f"P2N.{i}.{m}.{o}.md")
                v[f"{m}.{o}"] = None if w is None else ("NEW" if (o == "AB") == (w == "B") else "OLD")
        wins = sum(x == "NEW" for x in v.values())
        noflip = v["sol2.AB"] is not None and v["sol2.AB"] == v["sol2.BA"]
        new = [rating(D / f"P1N.{i}.sol2.r{k}.md") for k in (1, 2, 3)]
        base = [rating((base_dir or R / "runs") / pat.format(i=i, k=k)) for k in (1, 2, 3)]
        p1ok = None not in new and None not in base and st.mean(new) >= st.mean(base) and min(new) >= min(base)
        adopt = wins >= 3 and noflip and p1ok
        rows.append((i, v, wins, noflip, new, base, p1ok, adopt))
    return rows


def show(rows):
    out = ["piece\tsol2.AB\tsol2.BA\tgemini.AB\tgemini.BA\tNEW_wins\tsol2_noflip\tP1N_new\tP1N_base\tP1N_ok\tADOPT"]
    for i, v, wins, nf, new, base, ok, ad in rows:
        out.append("\t".join([i, *[str(v[k]) for k in ("sol2.AB", "sol2.BA", "gemini.AB", "gemini.BA")], str(wins),
                              str(nf), ",".join(map(str, new)), ",".join(map(str, base)), str(ok), "YES" if ad else "no"]))
    return "\n".join(out)


if __name__ == "__main__":
    R, D = Path(sys.argv[1]), Path(sys.argv[2])
    if "--self-test" in sys.argv:
        import tempfile
        t = Path(tempfile.mkdtemp())
        rr = t / "r"; (rr / "runs").mkdir(parents=True); dd = t / "d"; dd.mkdir()
        for k in (1, 2, 3):
            (rr / "runs" / f"P1N__X__sol2__r{k}.txt").write_text("RATING: 3\n")
            (rr / "runs" / f"P1N__Y__sol2__r{k}.txt").write_text("RATING: 3\n")
        def put(i, ab, ba, gab, gba, p1):
            for (m, o), w in {("sol2", "AB"): ab, ("sol2", "BA"): ba, ("gemini", "AB"): gab, ("gemini", "BA"): gba}.items():
                if w: (dd / f"P2N.{i}.{m}.{o}.md").write_text(f"WINNER: {w}\nSTRENGTH: 2\n")
            for k, r in enumerate(p1, 1):
                (dd / f"P1N.{i}.sol2.r{k}.md").write_text(f"RATING: {r}\n")
        put("X", "B", "A", "B", None, [3, 3, 3.5])   # NEW, NEW, NEW, failed -> 3 wins; no flip; P1N up -> ADOPT
        put("Y", "B", "B", "B", "A", [3, 3, 3])      # sol2 flips (NEW, OLD) -> not adopted
        r = {x[0]: x[-1] for x in decide(rr, dd, ["X", "Y"])}
        ok = r == {"X": True, "Y": False}
        print("SELF-TEST ::", "PASS" if ok else f"FAIL {r}")
        sys.exit(0 if ok else 1)
    ids = sorted({p.name.split(".")[1] for p in D.glob("P2N.*.md")} | {p.name.split(".")[1] for p in D.glob("P1N.*.md")})
    bd = Path(sys.argv[sys.argv.index("--base-runs") + 1]) if "--base-runs" in sys.argv else None
    bp = sys.argv[sys.argv.index("--base-pattern") + 1] if "--base-pattern" in sys.argv else "P1N__{i}__sol2__r{k}.txt"
    txt = show(decide(R, D, ids, bd, bp))
    (D / "adoption.tsv").write_text(txt + "\n")
    print(txt)
