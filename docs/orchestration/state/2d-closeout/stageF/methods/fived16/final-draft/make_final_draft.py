"""Generate fived16/FINAL-DRAFT.md, the one final draft (d) for Joseph: a numbered decision packet.

usage: python3 -I make_final_draft.py <worktree>

Every quoted current text is read from the sources at the worktree (comments stripped; each \\fvval resolved from
values_fived16.tex; each \\ref from the builds' .aux files; each \\cite from main_paper.aux), and every quoted proposal
or rater reading is read from the record that holds it. Nothing quoted is retyped: an extraction that fails to match
stops the run, and so does any LaTeX left unconverted. The lane's own words are the framing, the one-line reasons and
the proposals marked DRAFT (DECISION-20261028 result-table decision item 3 asks for the deposit's)."""
import re
import subprocess
import sys
from pathlib import Path

W = Path(sys.argv[1]).resolve()
A = W / "docs/analysis-note"
F = W / "docs/orchestration/state/2d-closeout/stageF/methods/fived16"
S = F.parent
FD = W / "docs/orchestration/state/measurement-paper/5d-community-20261024"
OUT = F / "FINAL-DRAFT.md"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import texplain  # noqa: E402  (the shared extraction helpers)
texplain.init(W)
from texplain import VALS, LAB, BIB, src, plain, grab, line_of, rec  # noqa: E402


WAIVE = "<!-- absence-ok: quotes printed limitation wording for Joseph; not a new absence claim -->"


def q(text, waive=False):
    out = "\n".join("> " + l for l in text.split("\n"))
    return out + "\n" + WAIVE if waive else out


# ---- extraction ---------------------------------------------------------------------------------------------------
title = plain(rec(A / "main_paper.tex", r"\\title\{(.*)\}"), "paper")
wp = F / "WORDING-PACKET.md"
T = {k: rec(wp, rf"^- (?:\*\*)?{k}(?: \(current\))?:(?:\*\*)? \"(.*)\"$") for k in ("T0", "T1", "T2", "T3")}
assert T["T0"] == title, "WORDING-PACKET's T0 is not the printed title"

pab = plain(src("main_paper.tex").split("\\begin{abstract}")[1].split("\\end{abstract}")[0], "paper")
nab = plain(src("main_note.tex").split("\\begin{abstract}")[1].split("\\end{abstract}")[0], "note")
rc = subprocess.run([sys.executable, "-I", str(F / "tools/recount.py"), str(W)], capture_output=True, text=True,
                    check=True).stdout
pw, nw = (int(rec_) for rec_ in re.findall(r"(?:paper|note) abstract: (\d+)", rc))
p_joint = grab("main_paper.tex", "As an illustration, simulation-calibrated tests", "coarse projections.", "paper")
n_joint = grab("main_note.tex", "Joint tests calibrated in simulation reject", "hydrocarbon-target correction.", "note")
p_cov = grab("main_paper.tex", "The coverage of the intervals has not been validated;", "interval widths.", "paper")
n_cov = grab("main_note.tex", "The coverage of the result's intervals has not been validated;", "interval widths.", "note")
p_flux_ab = grab("main_paper.tex", "The sixteen-cell $\\chi^{2}$ values fall by", "weakened by \\fvval{sens-alpha-pct}\\%.", "paper")
s1_flux = grab("paper_body.tex", "The generator $\\chi^{2}$ depends on the flux correlations:", "(Sec.~\\ref{sec:gen16}).", "paper")
s1_f1 = grab("paper_body.tex", "Interval coverage has not been validated.", "does not test interval widths.", "paper")
gen16 = grab("paper_body.tex", "Weakening only the flux correlations by", "under the true correlations.", "paper")
note_flux = grab("sec_fived16.tex", "Weakening only the flux correlations by", "under the true correlations.", "note")
h1 = grab("paper_body.tex", "Two GENIE~v3 tunes, \\fvval{f1-tune-g18}", "so interval widths cannot be tested.", "paper")
h1_alt = rec(F / "prd-read/r6/runs/PR6__r2__sol2.txt", r"^H1: VERDICT: SHORTEN\nSHORTER-FORM: (.*)$")
o3_p = grab("paper_body.tex", "We interpret the residual as regularization bias, because", "classifier capacities.", "paper")
o3_n = grab("sec_5d.tex", "No single cause is established,", "GiBUU-to-GENIE departure.", "note")
q4 = grab("paper_body.tex", "The joint-test estimator is unstable at the level of rounding.", "can be reproduced.", "paper")
da = grab("main_paper.tex", "The input data and simulation are the MINERvA open-data AnaTuples", "release decision.}", "paper")
da_pkg = grab("main_paper.tex", "A candidate release package of about", "and the $(\\Eavail,W)$ map.", "paper")
da_prop = rec(wp, r"^\*\*Data availability\*\*.*Proposed: \"(.*)\"$")
assert "of the joint tests" in da_prop and "Sec." not in da_prop, "WORDING-PACKET's proposal no longer keeps the joint-test clause"
# the REWRITE that answers the QUOTE of the release-package sentence, not the file's first REWRITE
da_r = {r: rec(S / f"r19/measure/P1__{r}__sol2.txt", r'QUOTE: "A candidate release package.*?REWRITE: ([^\n]*)', re.S)
        for r in ("r2", "r3")}
assert all("deposited" in v for v in da_r.values()), da_r
rel9_full = grab("app_release.tex", "It also regenerates, from packaged arrays, figures that the article cites from this note:",
                 "the one-dimensional generator projections.", "note")
R = {}
for line in (F / "prd-read/r2/inputs/proposals.tsv").read_text().splitlines():
    c = line.split("\t")
    if re.fullmatch(r"R[1-4]", c[0]):
        R[c[0]] = (c[2], c[3])
assert sorted(R) == ["R1", "R2", "R3", "R4"]
FRAG = {"R1": "or the quoted closure, bias and covariance-status measurements.",   # each base text must still print
        "R2": "the five-axis covariance used in this note and its", "R3": "travel with the five-axis covariance used in this note",
        "R4": "The five-axis covariance used in this note is the file"}
for k, (old, new) in R.items():
    assert FRAG[k].split(" the five")[0] in old or FRAG[k] in old or k != "R1", k
    assert FRAG[k] in src("app_release.tex"), f"{k}'s base text no longer prints in app_release.tex: {FRAG[k]!r}"
gem5 = re.findall(r"^- (.*?)[;.]?$", rec(S / "r20/REPORT.md", r"\*\*Gemini's reasons are concrete[^\n]*\n((?:- .*\n)+)", re.M), re.M)
assert len(gem5) == 5, gem5
p02_agy = rec(F / "c1a/agy/p02/agy-real.txt", r"^DETAIL: (.*)$")
p02_now = grab("paper_body.tex", "The validation studies assess the result", "generator-sized amounts.", "paper")
n4 = rec(S / "r19/outline.md", r"\*\*Open items for the n4 note round,\*\* recorded here, not fixed in r19:\n((?:.+\n)+)")
ki85 = rec(W / "KNOWN_ISSUES.md", r"^\| 85 \| \w+ \| \*\*(.*?)\*\*")
ki85_what = rec(W / "KNOWN_ISSUES.md", r"^\| 85 \|.*?(Joseph ruled 2026-10-06 that [^.]*\.)")
n_pubhold = len(re.findall(r"\\pubhold\{", src("main_paper.tex")))
r11 = {"full": "0.62", "no-gibuu": "0.93", "ce-cresp": "1.07"}   # c1a/REPORT.md, the review's table; restated below
for v in r11.values():
    assert v in (F / "c1a/REPORT.md").read_text(), f"R11 value {v} not in c1a/REPORT.md"

# ---- the packet ---------------------------------------------------------------------------------------------------
P = []
add = P.append
add(f"""# The final draft (d): a decision packet for Joseph (2026-10-28)

**From** the paper rewrite lane, through the director. **Under:** `DECISION-20261027-joseph-5d-integration-then-second-scope-review.md` item 2 (the printed wording is yours and comes to you before #413 merges); the director's work order of 2026-10-28.

**How to read it.** Each item is numbered. It quotes the current printed text exactly, generated from the sources with every value resolved (`final-draft/make_final_draft.py`, which stops if a quoted passage no longer prints). Any proposal stands beside it, with its source and one line of reason. Every protected text of yours is shown unedited. Nothing is submitted, deposited or tagged, and #413 stays a draft PR until you approve.

**The PDFs** (built from #413 at the commit holding this file, `build_all.sh` rc 0):
- the paper: `final-draft/main_paper.pdf`;
- the note: `final-draft/main_note.pdf`;
- the paper redline against the pre-integration base `8b0f83fd`: `final-draft/redline-paper.pdf` (latexdiff, by
  `final-draft/make_redline.sh`). Deleted text is struck through in red, and inserted text is underlined in blue. Tables
  print whole, without markup inside. A "??" appears only inside deleted text, where it refers to a label r19 removed
  (Sec. VI's sections, its tables and Fig. 4, and Table I).

## 1. What changed since you last read it

1. **The 5D integration:** the sixteen-cell five-observable cross section (configuration (e)), with its reported covariance C_total + C_resp, fake-data tests and generator comparison, in the paper and in a new note chapter (§{LAB['note']['sec:fived16']}).
2. **The move:** the non-final configurations, the calibrated hybrid-null tests and their detail now print in the note; the paper points to them.
3. **r19's structure:** the paper is a measurement paper in six sections (Introduction; Data, simulation and observables; Cross-section extraction; Uncertainties and validation; The sixteen-cell cross section; Discussion and conclusions); Table I is folded into the text.
4. **Step (c):** the GENIE v3 held-out bias test (F1) in Sec. I, both abstracts, IV H and the note; the flux-correlation bootstrap band (3D) beside the kept α = 0.1 sentences.
5. **`tab:result16`:** the sixteen-cell result table (Table {LAB['paper']['tab:result16']}), one marginal uncertainty column, with your advice applied (DECISION-20261028, result table).

## 2. The title

**Current (T0):**
{q(title)}

T0 is the methods framing ("Performance and limitations"); the paper is now led by its measurement. **The options** (`WORDING-PACKET.md`; PRD read round 3 chose T1 in all four runs):
- **T1:** "{T['T1']}"
- **T2:** "{T['T2']}"
- **T3:** "{T['T3']}"

**Reason in one line:** the abstract, Sec. I and the result now lead with the cross section, which T0 does not name.

## 3. The two abstracts (drafts; the final wording is yours)

**3.0 The paper abstract as it prints ({pw} words):**
{q(pab, True)}

**The note abstract as it prints ({nw} words):**
{q(nab, True)}

**3.1 The joint-test sentence is stale after the move.** The paper abstract still says:
{q(p_joint)}
The joint tests now print in the note only; the paper body reaches them through one pointer, and its body sentence says "additional discrimination" where this sentence says "gain" (agy-b4 Q2). **Options:** (a) keep it, as an illustration of the note; (b) drop it from the paper abstract, where the note abstract keeps its form ("{n_joint[:120]}…"); (c) your words. *Reason:* the abstract reports a result the paper no longer prints.

**3.2 The 1A addition (step (c)).** Both abstracts' coverage sentence now reads:
{q(p_cov, True)}
{q(n_cov, True)}
Read as printed by PRD read r6 (sol2 ×2, gemini) and agy with a control; no rater form passed both, so the drafts stand (`prd-read/REPORT.md`, "Round 6"). *Reason:* the decision says the paper names 1A as a bias test, not a coverage test.

**3.3 The note abstract's length.** {nw} words (348 before (c)). sol2 called it too long in 2 of 4 runs of round 3; gemini, acceptable in 2 of 2. No rater's shorter form passed the truth column. **A shorter version is drafted only if you ask,** because it would be new wording.

**3.4 Two wordings of one limitation.** Sec. I (PRD read r5's form) says "Interval coverage has not been validated."; the abstracts say "The coverage of the intervals has not been validated" (paper) and "The coverage of the result's intervals has not been validated" (note). **Options:** align them, or keep each as read. *Reason:* each form was read and accepted where it prints; the choice is register only.
{WAIVE}

## 4. The flux band (3D): replace the α = 0.1 sentence, or keep both

**The paper (Sec. {LAB['paper']['sec:gen16']}), as it prints:**
{q(gen16)}

**The note (§{LAB['note']['sec:fived16-gen']}), as it prints:**
{q(note_flux)}

**The abstracts' and Sec. I's flux sentences are unchanged by (c).** The paper abstract:
{q(p_flux_ab)}
Sec. I:
{q(s1_flux)}

**Options:** (a) keep both, as now; (b) replace the α sentences with the band, as DECISION-20261027 (limitation plan) item 3 first said ("replaces"). *Reason for (a):* they answer different questions. The weakening probes sensitivity to incorrect correlations; the band is the estimation scatter of the χ² given these universes, and not an interval for the χ² under the true correlations (FD-FLUX-BOOT-BINDING ruling 2).

## 5. F1, the GENIE v3 held-out bias test

**5.1 The Sec. I sentence, as it prints:**
{q(s1_f1, True)}

**Beside it, what it rests on.** At G18_10a_02_11b's cell R11, the −8.5 % bias stays below σ mainly through C_model's GiBUU vertex. |b|/σ is {r11['full']} under the full reported covariance, {r11['no-gibuu']} without the GiBUU vertex and {r11['ce-cresp']} under C_e + C_resp alone (the independent review of `589f0780`; `c1a/REPORT.md`). **"The reported uncertainty" in that sentence includes C_model,** which the paper calls "not a calibrated bound". The sentence is true as written; whether to say so in the text is yours.

**5.2 IV H's paragraph, as it prints ({len(h1.split())} words):**
{q(h1)}

**Beside it, the alternative** (PRD read r6, sol2 r2's form, {len(h1_alt.split())} words; true in the truth column, and agy reads it SAME; it does not replace the paragraph):
{q(h1_alt)}

*Reason to consider it:* shorter, same facts; it leaves the "GENIE tunes" ground of "partial evidence" to the first sentence.

## 6. Data and release (all protected text yours, shown unedited)

**6.1 Q8, supplemental data.** Whether the article and the release carry the sixteen-cell vector, C_total + C_resp and the cell boxes, and in what format, is open and yours.

**6.2 The deposit candidate** (`measurement-paper/5d-community-20261024/fd/deposit-candidate/`): prepared, not deposited (DECISION-20261028 item 2). It holds the cell definitions, f, the reported covariance and the correlation matrix, verified against the data product (`b79556f0`).
- **DRAFT proposal, the paper's citation of it** (no identifier exists, so none is cited): in `tab:result16`'s caption, "The cell definitions, measured vector, reported covariance and correlation matrix are given in machine-readable form in Ref. [deposit]", with Ref. [deposit] a bibliography entry whose identifier is a `\\pubhold`.
- **DRAFT proposal, Data Availability:** a sentence after the release-package sentence, "The sixteen-cell result's cell definitions, measured vector, reported covariance and correlation matrix are prepared for deposit in machine-readable form," followed by your `\\pubhold` for its identifier.
- **`predictions-reference.json`:** the five predictions' g and V_g, labelled "reference predictions used for the paper's χ²; not part of the measurement". **Options:** in the deposit, or not. *Reason:* with it, the paper's χ² can be reproduced; without it, the deposit is the measurement alone.

**6.3 Data Availability (protected), as it prints:**
{q(da)}
- **One stale pointer, one clause still true.** "of the joint tests" is still true of the package: it recomputes the
  joint tests' p values and decisions, which now print in the note rather than the article. The stale part is "the
  numbers quoted in Sec. {LAB['paper']['sec:central']}": that section now quotes none. **Proposal** (`WORDING-PACKET.md`, after
  the move), which keeps "of the joint tests", replaces the Sec. {LAB['paper']['sec:central']} clause with the map's numbers
  as quoted in the note, and so refers the figure clause to "that map": "{da_prop}"
- **The release-package sentence**, quoted by 2 of 3 P1 runs after r19:
{q(da_pkg)}
  The raters' readings (their own rewrites: not fact-checked, and both carry the stale "Sec. V C"):
  - sol2 run 2: "{da_r['r2']}"
  - sol2 run 3: "{da_r['r3']}"

  Run 2 gives "not yet deposited" a clause of its own; run 3 moves it to a last sentence of its own.

**6.4 `app_release.tex:{line_of('app_release.tex', 'It also regenerates, from packaged arrays, figures that the article cites')}`'s figure list (protected):**
{q(rel9_full)}
The article now reaches the joint tests' null distributions only through one pointer (r19, K8). **Options:** keep; or say "figures that the article cites from this note, directly or through its pointers" (DRAFT). `app_release.tex:{line_of('app_release.tex', "the arrays behind the article's figures;")}`'s "the arrays behind the article's figures" is still right: Figs. 1–3 are the same three figures.

**6.5 R1–R4, the release scopings, as proposals** (round 2 accepted each in all four runs; `prd-read/r2/inputs/proposals.tsv`). *Reason:* each names which central value the release's covariance belongs to, now that the note reports two results.
""")
for k, (old, new) in R.items():
    add(f"- **{k}.** Now: \"{old}\" → proposed: \"{new}\"")
add(f"""
## 7. Wording pairs and questions

**7.1 O3, side by side.** The paper (base wording, kept):
{q(o3_p)}
The note:
{q(o3_n)}
*Reason:* the paper interprets; the note establishes no single cause. Any softening is yours.

**7.2 Q4, the rounding instability.** The paper says:
{q(q4)}
Whether the final uncertainty accounts for this instability is open; no proposal is made, and r19 prints nothing new on it.

## 8. Reading notes, not edits

**8.1 gemini's five** (r20's pairwise; they concern r20's wording, which was not adopted and is reverted, so they are style points to judge by reading):
""")
for g in gem5:
    g = g.rstrip(';').rstrip('.')
    add(f"- {g[0].upper() + g[1:]}.")
add(f"""
**8.2 P02's**, the Sec. I sentence as it prints:
{q(p02_now)}
agy, against the pre-round-3 text: "{p02_agy}" PRD reads r4 and r5 accepted the change 3 of 3 each, so nothing is edited.

## 9. The register result, as measured

- **r19 (the measurement paper's order) was adopted:** the blind pairwise preferred it 4 of 4, with no order flip (`r19/REPORT.md`).
- **r20 was not adopted:** 2 of 4 (sol2 for it, gemini against), and its text is reverted (`r20/REPORT.md`).
- **P1, the absolute rubric (sol2), for the kept text: 3, 3, 3.** The published PRD anchors score **3.67** under the same calibrated prompt. The paper's text stays below them on this measure.
- The paper's register rounds are closed.

## 10. Deferred to the note round n4 (recorded, not fixed)

{n4}

## 11. Untouched, and yours

- **KI-85** (`KNOWN_ISSUES.md` row 85): "{ki85}". "{ki85_what}" Nothing here changes it.
- **`\\pubhold`:** {n_pubhold} uses in `main_paper.tex`, unchanged, including the deposit identifier in Data Availability.
- **Claims:** every claim's wording is yours; this packet changes none beyond the drafts marked here.
""")
text = "\n".join(P).rstrip() + "\n<!-- absence-ok: quotes printed and protected text, decisions and rater readings for Joseph; not a new absence claim -->\n"
assert "\\" not in re.sub(r"`[^`]*`", "", text), [l for l in text.splitlines() if "\\" in re.sub(r"`[^`]*`", "", l)][:3]
OUT.write_text(text, encoding="utf-8")
print(f"wrote {OUT.relative_to(W)}: {len(text.split())} words")
