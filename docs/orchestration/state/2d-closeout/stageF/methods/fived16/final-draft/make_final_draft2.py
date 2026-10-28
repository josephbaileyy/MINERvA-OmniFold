"""Generate fived16/FINAL-DRAFT-2.md, the revised packet d2 for Joseph (DECISION-20261028-joseph-final-draft-d).

usage: python3 -I make_final_draft2.py <worktree>

As for the first packet (make_final_draft.py): every quoted current text is read from the sources with values resolved
(texplain), and every candidate, option, rater tally and record from the file that holds it. A quote that no longer
matches stops the run. The lane's own words are the framing, the one-line reasons and the DRAFT proposals."""
import json
import re
import sys
from pathlib import Path

W = Path(sys.argv[1]).resolve()
F = W / "docs/orchestration/state/2d-closeout/stageF/methods/fived16"
D2 = F / "d2"
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(D2))
import texplain as X  # noqa: E402
import options as OP  # noqa: E402

X.init(W)
from texplain import LAB, src, plain, grab, rec  # noqa: E402

OUT = F / "FINAL-DRAFT-2.md"
WAIVE = "<!-- absence-ok: quotes printed limitation wording for Joseph; not a new absence claim -->"
C = json.loads((D2 / "candidates.json").read_text())


def q(text, waive=False):
    out = "\n".join("> " + l for l in text.split("\n"))
    return out + "\n" + WAIVE if waive else out


def tally(path):
    rows = dict(re.findall(r"^\| (\w+) \| (.*?) \|$", Path(path).read_text(), re.M))
    return {k: v for k, v in rows.items() if re.fullmatch(r"A\d|B\d|P02", k)}


T1, T2 = tally(D2 / "raters/TABLE.md"), tally(D2 / "raters-v2/TABLE.md")
title = plain(rec(X.A / "main_paper.tex", r"\\title\{(.*)\}"), "paper")
pab = plain(src("main_paper.tex").split("\\begin{abstract}")[1].split("\\end{abstract}")[0], "paper")
nab = plain(src("main_note.tex").split("\\begin{abstract}")[1].split("\\end{abstract}")[0], "note")
cand = {d: {n: plain(c["tex"], d) for n, c in C[d]["candidates"].items()} for d in ("paper", "note")}
assert cand["paper"]["PB"] == pab and cand["note"]["NA"] == nab, "the applied abstracts are not candidates PB and NA"
words = {n: c["words"] for d in C for n, c in C[d]["candidates"].items()}
h1 = grab("paper_body.tex", "Two GENIE~v3 tunes,", "so interval widths cannot be tested.", "paper")
s1 = grab("paper_body.tex", "Interval coverage has not been validated.", "does not test interval widths.", "paper")
o3 = grab("paper_body.tex", "We interpret the residual as regularization bias,", "no single cause is established.", "paper")
da = grab("main_paper.tex", "The input data and simulation are the MINERvA open-data AnaTuples", "release decision.}", "paper")
fid = "whose true vertex lies in the tracker fiducial volume"
assert fid in src("paper_body.tex"), "the fiducial-volume phrase no longer prints"
note_ch = grab("sec_experiment.tex", "Its central tracker comprises", "scintillator strips", "note")
survey = (D2 / "DA-SURVEY.md").read_text()
typ = re.findall(r'^\d\. "(.*?)" \(', survey, re.M) or re.findall(r'"(The data release[^"]*)"', survey)
r14 = [(plain(k, "note"), plain(s, "note")) for k, s in OP.R14["pairs"]]
for k, _ in OP.R14["pairs"]:
    assert k in src("app_release.tex"), k
flux_r_note = "the band sentences stay; the two weakening sentences and the clause \"which the weakening probes\" leave V B, and Sec. I's flux sentence keeps its numbers and points to the note"

P = []
add = P.append
add(f"""# The revised draft (d2): a decision packet for Joseph (2026-10-28)

**From** the paper rewrite lane, through the director. **Under:** your decisions on (d), `DECISION-20261028-joseph-final-draft-d.md` (PR #452). The record of this round is `d2/REPORT.md`. #413 stays a draft PR, and everything here returns to you before it merges.

**How to read it.** Each item gives what was done, the independent raters' choice and its runner-up, and the current printed text, quoted exactly from the sources (`final-draft/make_final_draft2.py`, which stops if a quote no longer matches). Your protected text is shown unedited, with proposals beside it. Every rater read was blind and in both orders, by sol2 (gpt-6.1-sol) and by gemini, with controls; the tallies are `d2/raters/TABLE.md` and `d2/raters-v2/TABLE.md`.

**The PDFs** (`build_all.sh` rc 0): `final-draft-2/main_paper.pdf` (11 pp), `final-draft-2/main_note.pdf` (130 pp), and `final-draft-2/redline-paper.pdf` (17 pp), the paper against the pre-integration base `8b0f83fd` (`final-draft/make_redline.sh`; a "??" appears only inside deleted text, at a label r19 removed).

## 1. What changed since (d)

1. **The title is T1** (your decision).
2. **Both abstracts are rewritten to the genre's typical form,** by removing whole sentences only, and the raters chose among the candidates (§3).
3. **IV H takes the shorter F1 paragraph** (your decision), and it adds one sentence on R11 (the raters' choice, §5).
4. **O3's sentence** adds the note's "although no single cause is established" (the raters' choice, §7).
5. **Data Availability, R1–R4 and the release text** are your protected text: the raters' choices are proposals here (§6), and nothing there is edited.

## 2. The title (applied)

{q(title)}

The note's title is its own ("Analysis Note: Unbinned OmniFold analysis of MINERvA charged-current inclusive data") and is unchanged. **For you:** T1 says "on hydrocarbon", and no sentence of the paper's body names the target material: the body places the vertex in "{fid}". The note does ("{note_ch}", `sec_experiment.tex`). **DRAFT:** "…whose true vertex lies in the fiducial volume of the polystyrene-scintillator (CH) tracker…". The plain-language primer's title still follows the old methods framing (its source comment says so); the primer is outside this round.

## 3. The abstracts (applied; drafts, yours)

**What is typical, measured** (`d2/MEASURE.md`, with register-prd-study's tools):
- **The paper:** the corpus's eight abstracts have 98–141 words (median about 120). At most one sentence carries a scope, condition or status marker, and no sentence carries two. Ours had 238 words with 5 of 8 sentences marked. **Caps:** 120–150 words; at most one marked sentence, with one marker.
- **The note:** the long-document anchors, T2K (PRD 91, 072010) and ProtoDUNE-SP (JINST 15, P12004), have 184 and 190 words, with no marked sentence. Ours had 382 words with 5 of 9 marked. **Caps:** at most 190 words, and the same marker caps.
- **No metatext** ("As an illustration", "This note documents", "The note also gives", and similar).

**How the candidates were made.** Each is whole sentences of the printed abstract, so no sentence that stays is weakened. Every fact of a dropped sentence still prints in a body, and the ledger probes each one there (rows D2-M4 … D2-A8). The note's candidates open with the paper abstract's first sentence: without the metatext sentence, the note's own "principal result" sentence no longer named the measurement.

**The raters' choice.**
- **Paper:** PB in all 8 runs over the two reads ({T1['A1']}; v2 {T2['A1']}). Runners-up PA and PC tie on mean rank.
- **Note** (v2): NA, 3 of 4 ({T2['A2']}). gemini chose NA in both orders; sol2's two runs split by order. The runner-up is ND.
- **The control,** P02: ACCEPT in all 8 runs.

**The paper abstract as it now prints ({words['PB']} words; PB):**
{q(pab, True)}

**Runner-up PA ({words['PA']} words), which keeps the coverage and bias-test sentence:**
{q(cand['paper']['PA'], True)}

**Runner-up PC ({words['PC']} words), which keeps the validation findings:**
{q(cand['paper']['PC'], True)}

**The note abstract as it now prints ({words['NA']} words; NA):**
{q(nab, True)}

**Runner-up ND ({words['ND']} words), which keeps the flux sentence instead of the coverage one:**
{q(cand['note']['ND'], True)}

**What left the abstracts, and where it still prints** (ledger rows D2-*):
- **The paper:**
  - the coverage and bias-test sentence (Sec. I);
  - the flux sentence (Sec. I and Sec. {LAB['paper']['sec:gen16']});
  - the validation findings (Sec. IV);
  - the joint-test sentence. Its limitation, "no evidence of additional discrimination beyond matched coarse projections", is in the paper's Scope paragraph. Its rejections ("five generator predictions all reject at the 5% familywise level") now print only in the note.
- **The note:** the metatext opening; the list of covariance terms; the flux, reproduction, validation and joint-test sentences. Each prints in the note's body.
- **Two facts print in no note body file, for you:**
  - the note abstract's "principal result": the executive summary and summary say the validation findings are the main results (the n4 inconsistency, §10). agy flags the new opener, "We report a simultaneous measurement", for this framing;
  - "on a finer grid", which the cell counts only imply.

## 4. The wording of the coverage limitation (§3.4 of d)

The raters chose **(i) "Interval coverage has not been validated."** in 4 of 4 runs, against (ii) "The coverage of the intervals …" and (iii) "The coverage of the result's intervals …". The runner-up is (ii). Sec. I already prints (i), and the paper abstract no longer carries the sentence, so nothing changes. The note abstract keeps its own (iii); the read asked about the paper.
{WAIVE}

## 5. F1 (applied)

**5.1 IV H's paragraph, as it now prints** (PRD read r6's sol2 r2 form, your decision; then the R11 sentence, the raters' choice in 4 of 4):
{q(h1, True)}

**The R11 sentence** says what the review measured: |b|/σ at G18's R11 is 0.62 under the full covariance, 0.93 without GiBUU's vertex and 1.07 with C_e + C_resp alone. agy asks for the fuller form. **DRAFT, for you:** "…only with C_model included, mainly through its GiBUU component." The runner-up is not adding it.

**5.2 Sec. I's sentence** (unchanged; the R11 sentence qualifies it):
{q(s1, True)}

## 6. Data and release (protected; proposals only)

**What is typical** (`d2/DA-SURVEY.md`, the seven corpus measurement papers, from source):
- all seven release cross sections, a covariance and the binning in machine-readable form;
- four say where; three point to the Supplemental Material; two cite a collaboration web page;
- none has a Data Availability section (all predate the 2024 PRD requirement), and none cites a DOI or HEPData.

The most typical sentences (verbatim from the corpus sources, as LaTeX):
""")
add("\n".join(f"- `{s}`" for s in typ[:3]) if typ else "(see DA-SURVEY.md)")   # verbatim corpus source, as code
add(f"""
**6.1 Data Availability, as it prints:**
{q(da)}

**The raters' choice:** the typical DRAFT, in 4 of 4 runs at strength 3. The runner-up is the current text.
{q(plain(OP.DA['T'], 'paper'))}
- **Its condition:** it is true only if you answer **Q8** yes, the article carries the sixteen-cell vector, covariance and cell definitions as supplemental files, and the files are made.
- **What it leaves out:** the release package and the input-file checksums, both described in the note's App. {LAB['note']['app:release']}.
- **It also removes** the stale pointer "the numbers quoted in Sec. {LAB['paper']['sec:central']}" (`FINAL-DRAFT.md` 6.3).

**6.2 The deposit, beyond typical, for later.**
- The raters chose to add the caption's citation (B6, 4 of 4), but it fails the truth column: nothing is deposited.
- The raters chose not to add the Data Availability deposit sentence (B8, 4 of 4).
- `predictions-reference.json`, in the deposit or not, is still yours.

**6.3 R1–R4,** the release appendix's scopings. The raters chose the scoped forms in 4 of 4 runs; the runner-up keeps the current text. This is a proposal, because `app_release.tex` is protected:
""")
for i, (k, s) in enumerate(r14, 1):
    add(f"- **R{i}.** Now: \"{k}\" → proposed: \"{s}\"")
add(f"""
**6.4 `app_release.tex:9`'s figure list:** the raters chose to keep it, in 4 of 4 runs. The runner-up is "directly or through its pointers".

## 7. O3 (applied) and Q4 (open)

**7.1 O3, as it now prints** (the raters' choice: sol2 2 of 2 for the qualified form, gemini 2 of 2 for keeping it; the models split, so sol2's true form, by round 3's rule. The runner-up is the unqualified sentence):
{q(o3)}

**7.2 Q4,** whether the final uncertainty accounts for the rounding instability. It has no options and stays an open question for you.

## 8. The flux band (§4 of d)

The raters chose **keep both** in 4 of 4 runs. The runner-up is replace: {flux_r_note}. The paper is unchanged, and ruling 2's band constraints hold.

## 9. Unchanged from (d)

These items are in `FINAL-DRAFT.md` and are not repeated here:
- the reading notes: gemini's five, and P02's;
- the register result: r19 adopted; r20 not; P1 3, 3, 3 against the anchors' 3.67.

## 10. Deferred to the note round n4

The two items of (d) §10, now sharpened: with the note abstract opening "We report a simultaneous measurement", the inconsistency with the executive summary's "The main results are the validation findings" is visible on the note's first page.

## 11. Untouched, and yours

KI-85, `\\pubhold`, claims, Q8, Q4, the deposit, and every protected text (Data Availability, `app_release.tex`, `values.tex`, `values_inference.tex`, `app_history.tex`), which are byte-identical.

## 12. Gates and build

- `build_all.sh` rc 0: paper 11 pp, note 130 pp; no undefined reference; no `??`; SEC4 15/15.
- The ledger (`r19/check_ledger.py --base 9df8f748`): 255 rows, 475 probes, 0 failures. Its `--self-test` passes, with 57 scope guards, each planted strengthening caught, and the title, abstract and allowance pins (T1 and PB, by sha256) each caught.
- `make_values_fived16.py --check`, fived16 rule 7, reflow, swallowed-text, the registry, absence-claims, the live-doc index and the manifest all pass.
- agy, with a control (5 of 5 caught): `d2/agy/README.txt`.
""")
text = "\n".join(P).rstrip() + "\n<!-- absence-ok: quotes printed and protected text, decisions and rater readings for Joseph; not a new absence claim -->\n"
assert "\\" not in re.sub(r"`[^`]*`", "", text).replace("\\mathrm", ""), [l for l in text.splitlines() if "\\" in re.sub(r"`[^`]*`", "", l)][:3]
OUT.write_text(text, encoding="utf-8")
print(f"wrote {OUT.relative_to(W)}: {len(text.split())} words")
