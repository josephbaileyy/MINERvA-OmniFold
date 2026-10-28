"""Write the Q3 variant documents, the PQ inputs (excerpt + clause list + table question) and the job list."""
import re
X = "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/796e7ecc-51d8-4fd5-a926-09de706955fd/scratchpad/xmodel/prd5d"
ex = open(f"{X}/inputs/excerpt.txt").read()
I = ("Weakening only the flux correlations by 10 % lowers the χ² of the 16-cell predictions by 24–48 %. The same change "
     "to the detector or lateral correlations lowers it by at most 18 %. With the correlations of the interaction, flux, "
     "detector and lateral groups removed, every 16-cell prediction keeps χ² ≥ 45 for 16 degrees of freedom.")
II = ("Weakening only the flux correlations by 10 % lowers the χ² of the 16-cell predictions by 24–48 %, against at most "
      "18 % for the detector or lateral correlations.")
III = ("Weakening only the flux correlations by 10 % lowers the χ² of the 16-cell predictions by 24–48 %, against at most "
       "18 % for the detector or lateral correlations, and with the correlations of the interaction, flux, detector and "
       "lateral groups removed every 16-cell prediction still has χ² ≥ 45 for 16 degrees of freedom.")
assert ex.count(I) == 1
part1 = ex[ex.index("PART 1."):ex.index("PART 2.")].replace("PART 1. Two subsections of the paper (tables omitted).", "").strip()
assert part1.endswith(I)
for k, v in (("i", I), ("ii", II), ("iii", III)):
    open(f"{X}/inputs/q3-{k}.txt", "w").write(part1[:-len(I)] + v + "\n")
CL = ["is reported separately from those reporting definitions",
      "of which the study's 27 coarser cells are the supported ones; each supported box with purity below 0.1 is merged into a neighbour, 4 boxes remain unreported, and every reported cell passes the support rule",
      "Its model term differs from the study's envelope: there, the largest shift of a cell over five generator-sized truth changes, added linearly to the half-width; here, a covariance built from three generator shifts.",
      "a training-seed term measured to be zero",
      "it is generator-shape model dependence, unscaled and not a calibrated bound",
      "and its coverage at truths held out of its construction has not been validated",
      "it does not cover neutron or muon deposits, nor species, energy-dependence or resolution effects beyond a scale",
      "and it does not enter the generator tests of Sec. VII or the paper's other results",
      "(6.74% without C_resp)",
      "so that no such truth is compared with a covariance that includes its own generator's component",
      "6 further truths, whose offset correction failed its control, are ungraded and given in the note",
      "Under the reported covariance, without the GiBUU component for the two GiBUU truths,",
      "the reported uncertainty does not cover the fake-data bias at these GiBUU-like truths or at the q_3 tilt",
      "no diagonal-only χ² is formed",
      "so it is compared on the 8 cells with p_∥<4.5 GeV/c only",
      "The reported uncertainty does not cover the fake-data bias at the GiBUU-like truths (Sec. V F).",
      "NuWro and GiBUU are on carbon, with no correction to CH",
      "Because C_model is built from shifts toward GENIE + MEC, NuWro and GiBUU, each relative to GENIE CV, those comparisons use a covariance built in part from the compared generator, and the GENIE CV comparison does through that reference.",
      "The sixteen-cell result of Sec. V F also has total uncertainties, whose coverage is not validated.",
      "This bias is not included in the uncertainties quoted for the configuration-(a) central value.",
      "No uncertainty quoted for the configuration-(a) central value includes the regularization bias, and its five-observable covariance omits it.",
      "unscaled and not a calibrated bound, and Sec. V F gives the fake-data study's measured comparison of the estimator's bias with the reported covariance",
      "The seed dependence of this five-observable covariance rests on one seed pair, and the spread over seed pairs has not been measured.",
      "The higher-dimensional results are central values without intervals of validated coverage, and no uncertainty quoted for the configuration-(a) five-observable central value includes its regularization bias (Sec. V B).",
      "The sixteen-cell result also has total uncertainties, whose coverage is not validated; Sec. V F gives the fake-data study's measured comparison of the estimator's bias with its reported covariance.",
      "the configuration-(a) central value"]
for c in CL:
    assert c in ex, c
open(f"{X}/inputs/clauses.tsv", "w").write("".join(f"C{i+1:02d}\t{c}\n" for i, c in enumerate(CL)))
T = ("QUESTION T. The paper's table of each prediction against the sixteen-cell result prints, for five generator "
     "predictions, the χ² with its number of degrees of freedom and a shape-only χ². Printed as integers it reads:\n"
     "  GENIE 2.12.10 CV 109/16, shape-only 109/15; GENIE 2.12.10 + Valencia MEC 272/16, 258/15; NuWro 21.09 188/16, 188/15; "
     "GiBUU 2019 58/8, 28/7; MINERvA Tune v1 330/16, 311/15.\nPrinted with two decimals it reads:\n"
     "  GENIE 2.12.10 CV 109.35/16, 108.51/15; GENIE 2.12.10 + Valencia MEC 272.12/16, 258.07/15; NuWro 21.09 188.03/16, "
     "188.00/15; GiBUU 2019 58.46/8, 27.69/7; MINERvA Tune v1 329.72/16, 311.19/15.\n"
     "Which would a PRD paper print in this table: integers, one decimal or two decimals?\n")
for tag, order in (("fwd", CL), ("rev", CL[::-1])):
    ids = {c: i for i, c in enumerate(CL)}
    lst = "".join(f'C{ids[c]+1:02d}. "{c}"\n' for c in order)
    open(f"{X}/inputs/pq-{tag}.txt", "w").write(ex + "\nTHE QUALIFYING CLAUSES (answer in the order listed)\n\n" + lst + "\n" + T)
J = []
for m in ("sol2", "gemini"):
    for a, b in (("i", "ii"), ("i", "iii"), ("ii", "iii")):
        for o in ("AB", "BA"):
            A, B = (a, b) if o == "AB" else (b, a)
            for r in (1, 2):
                J.append((f"P2S__{a}v{b}-{o}__{m}__r{r}", m, f"{X}/prompts/P2S.prompt.txt", f"{X}/runs/P2S__{a}v{b}-{o}__{m}__r{r}.md",
                          f"{X}/inputs/A/{A}.txt {X}/inputs/B/{B}.txt"))
    for tag in ("fwd", "rev"):
        J.append((f"PQ__{tag}__{m}", m, f"{X}/prompts/PQ.prompt.txt", f"{X}/runs/PQ__{tag}__{m}.md", f"{X}/inputs/pq-{tag}.txt"))
open(f"{X}/jobs.tsv", "w").write("".join("\t".join(j) + "\n" for j in J))
print(len(J), "jobs")
