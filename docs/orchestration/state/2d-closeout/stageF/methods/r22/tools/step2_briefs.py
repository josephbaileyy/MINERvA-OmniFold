"""Write r22 Step 2's per-piece writer lists: step2/briefs/Bxx.md, one per note piece.

usage: python3 -I step2_briefs.py R22_DIR
Each list gives the piece's source files (FILES), its in-scope gaps from step2/gaps-ws.tsv (quote, problem, change,
grounds, ledger home), and its out-of-scope gaps from gap/gaps.tsv, whose quoted sentences the writer leaves as they
are. The common instructions are step2/WRITER-BRIEF.md."""
import csv
import sys
from pathlib import Path

R = Path(sys.argv[1])
FILES = {"B01": ["sec_execsummary.tex", "sec_intro.tex"], "B02": ["sec_experiment.tex", "selection_features.tex",
         "sec_method.tex"], "B03": ["sec_systematics.tex"], "B04": ["sec_validation.tex"], "B05": ["sec_results.tex"],
         "B06": ["sec_3d.tex", "scalar_kinematics.tex"], "B07": ["sec_eavailw.tex"], "B08": ["sec_5d.tex"],
         "B09": ["sec_fived16.tex"], "B10": ["sec_joint.tex"], "B11": ["sec_fps.tex", "sec_summary.tex"],
         "B12": ["app_guide.tex", "app_statmethods.tex"], "B13": ["app_statmethods_nd.tex", "app_negweight.tex"],
         "B14": ["app_response_mismatch.tex", "app_landscape.tex", "app_pet_pointer.tex"],
         "B15": ["app_release.tex", "app_codebase.tex"]}
ins = [r for r in csv.DictReader(open(R / "step2" / "gaps-ws.tsv"), delimiter="\t")]
inset = {r["id"] for r in ins}
allg = [r for r in csv.DictReader(open(R / "gap" / "gaps.tsv"), delimiter="\t")]
(R / "step2" / "briefs").mkdir(parents=True, exist_ok=True)
for p, files in FILES.items():
    mine = [r for r in ins if r["input"] == p]
    out = [r for r in allg if r["input"] == p and r["id"] not in inset]
    L = [f"# r22 Step 2, piece {p}: the writer's list", "",
         f"**Your files** (in `docs/analysis-note/`): {', '.join('`' + f + '`' for f in files)}. Edit only these.",
         f"**Rated text** (the blinded PDF extract the raters read): `gap/inputs/{p}/chapter.txt`.", "",
         f"## In scope: fix these ({len(mine)} gaps)", "",
         "Each quote is from the PDF extract; find its sentence in your .tex sources. SCOPE \"pattern\" means the rater "
         "saw about N passages like it: fix those too, in your files, and ledger each.", ""]
    for r in sorted(mine, key=lambda x: -float(x["share"])):
        L += [f"### {r['id']} ({r['model']}, SHARE {float(r['share']):g}; {r['scope']}"
              + ("; **ABSTRACT PAIR: propose, do not edit main_note.tex**" if r["joseph_pair"] == "yes" else "") + ")",
              f"- QUOTE: \"{r['quote']}\"", f"- PROBLEM: {r['problem']}", f"- CHANGE: {r['change']}"]
        if r["ledger"]:
            L.append(f"- Home named by the classification: {r['ledger']}")
        L += ["<!-- absence-ok: quotes the raters' quoted sentences and requested changes; not a claim that a result is absent -->", ""]
    L += [f"## Out of scope: leave these sentences exactly as they are ({len(out)})", "",
          "A rater asked to change each of these, but a protection keeps it until Joseph rules. Do not edit, move or "
          "delete these sentences, even when a pattern above seems to cover them; tools/check_outscope.py fails the "
          "round if one no longer prints.", ""]
    for r in out:
        L.append(f"- {r['id']}: \"{r['quote']}\"")
    L.append("<!-- absence-ok: quotes the raters' quoted sentences and requested changes; not a claim that a result is absent -->")
    (R / "step2" / "briefs" / f"{p}.md").write_text("\n".join(L) + "\n")
    print(p, "in", len(mine), "out", len(out), files)
