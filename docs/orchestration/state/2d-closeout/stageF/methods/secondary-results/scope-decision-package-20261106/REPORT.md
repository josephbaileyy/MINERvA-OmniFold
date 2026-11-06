# Publication-scope decision package — DRAFT for the director

**Decision supported:** OI-205, measurement or methods-study framing, after the coverage and
run-period follow-up reports. The measurement framing currently in force is the decision of
2026-10-27; this draft changes neither it nor a scientific claim. The later decision reserves
the fake-data bias item for the same scope decision. The newer ruling makes measurement
options primary and the methods study the stated fallback; it does not adopt a result or
resolve its conditions. [QUEUE] [FRAME] [BIAS] [FRAME06:26–41]

**Evidence snapshot:** `origin/main` fetched at the start of this task, commit
`1aa805b59eb037c5fcd978037ae282189aa33634`. All source labels resolve in
[SOURCES.tsv](SOURCES.tsv) to `file:line @ full commit` or a packaged-advice digest, with each source blob's SHA256.
**Scope/status refresh:** `2968b58ac9c9031a13dd5acb98e661f28964423d`, after the director’s
queued instructions were received. The framing ruling, terminal 1B STOP and later bindings
use that refresh commit; other citations retain their explicitly pinned versions. Packaged
Grok advice is identified by its SHA256 rather than a self-referential commit. Earlier
review targets remain historical; the update-review attempt and its limits are recorded
separately. The bound 1B
design is read at the exact commit its main-branch binding names,
`6d93dd4284c1d378836ba275923d490f0f6c62f3`, rather than reconstructed from an older declaration.
[1B-B3]

**CITABLE FOR:** the inventory, the model referees' advice, the declared outcome licences and
the choices reserved for the scope decision at that snapshot. **NOT CITABLE FOR:** a new
measurement, an adoption, a coverage claim, publication readiness or authorization to run.
Campaign status below means **committed reporting status at this snapshot**, not a fresh
scheduler observation. A pending campaign's result is **not yet reported**; its outcome is
not forecast here. <!-- absence-ok: pending status is scoped to the cited committed reports and bindings at the frozen snapshot; no claim of global absence -->

**Ownership, review and stop:** the scope-package owner prepares this inventory; the director
writes the recommendation; Joseph decides. One independent read-only second read through
Antigravity, using an available Gemini model, checks the frozen draft against its sources.
At most one focused repair/recheck is budgeted; a remaining material disagreement is carried
to the director. The terminal deliverable is this draft, verbatim review evidence and a PR,
including an explicit pending-result list. No scientific compute, campaign rerun, manuscript
wording or external contact is part of this task. This follows the bounded-review guidance.
[REVIEW-RULE]

## 1. What the model referees require

These are **model-generated advisory reports, not journal peer review**. Each read concerns
the blinded manuscript named in its README. The later read followed a presentation revision;
the reports are repeated assessments of related material, not independent measurements of
the science. Neither a favourable methods opinion nor agreement among reports is a
publication decision. [READ04] [READ05]

| advisory report | Measurement framing: requested conditions and disqualifying items | Methods framing: what the report would accept |
|---|---|---|
| Sonnet, 2026-11-04 | Calls the combination of unvalidated/stopped coverage, generator-like fake-data failure in low-stability cells, failed numerical-stability requirement and unexplained period inconsistency disqualifying. Calls the low-stability cells individually disqualifying as reported. Requests resolved covariance/toy disagreement and coverage, bias treatment or demonstrated recovery, a stable estimator and a diagnosed period issue. Its exact conditional is a revised result with “validated or conservatively inflated uncertainties, a stable estimator, and a diagnosed run-period issue”. [S04:26–80,150–160] | If these cannot be delivered, calls the benchmark and documented failure modes “a legitimate methods contribution”, with the title and abstract saying so. This is conditional advice, not acceptance of the current measurement. [S04:160] |
| Gemini, 2026-11-04 | Says fake-data bias, aborted coverage and floating-point instability together are “completely disqualifying for a primary experimental cross section”. Also makes the unexplained benchmark difference, period treatment, low-stability cells and circular/target-mismatched comparisons major issues. Requires successful re-analysis or a validated bias envelope, coverage, stability, benchmark diagnosis, defensible period treatment and comparator repairs. [G04:32–68,140–144] | Requires a “major pivot in scope”, with the table an “empirical case study” rather than definitive physical cross sections. Describes the proposed result as a diagnostic methodological investigation. [G04:146–147] |
| Sonnet, 2026-11-05 | Its disqualifying combination remains stopped coverage, instability with the zero seed block, generator-sized prior dependence and the period step. Requests resolving major issues 1–4 and 6 for a measurement; low-stability R02/R06 remain deficiencies, while R10/R15 may be acceptable if flagged. Requests bias-versus-width diagnosis, direct prior comparisons, coverage, stability and playlist diagnostics. [S05:26–61,89–120,135–144] | Would consider “a methodology and validation study” with the table “a demonstration with explicitly unvalidated uncertainties”. Known failures stay visible; moving them into the note does not resolve them. [S05:131–144] |
| Gemini, 2026-11-05 | Names fake-data bias, unvalidated/aborted coverage and rounding instability “individually and collectively disqualifying”. Also requires resolving the benchmark discrepancy, period covariance treatment, model-covariance circularity, defective comparator samples and low-stability cells. Requests cross-fitting separately. [G05:25–69,122–124,140–144] | Proposes an “experimental/methodological techniques paper” that “would not claim to report a new benchmark cross section”, documenting diagnostic requirements and limitations instead. [G05:146] |

The reports differ in severity and in what they would tolerate. In particular, the later
Sonnet report permits a disclosed period block after investigation if the cause remains
unknown, and treats some low-stability cells more leniently; Gemini continues to request a
physical or regularized treatment and revised cells. Preserve that disagreement rather than
reporting a unanimous route to a publishable measurement. [S05:92–105] [G05:86–104]

### Advice that must not become a scientific conclusion

- Gemini converts the benchmark's descriptive distance into a compatibility p-value. That
  inference is not adopted: the declared comparison shares data and systematics and is not
  a calibrated compatibility test. The shape difference remains real as a recorded
  descriptive difference; its cause is not established. [G04:45–48] [G05:43–46] [C2:29–55]
- Some Gemini passages interpret reconstruction stability as the fraction of reconstructed
  events originating in the same cell. That is a purity interpretation. The adopted
  definition conditions on generated events that reconstruct; its denominator must be kept.
  A low stability alone neither measures prior dominance nor proves bias. [G05:66–69]
  [PAPER:301] [H2:35–43]
- The zero seed block and input-rounding spread are different measurements. The statistical
  construction refits with jitter, as the head-to-head declaration explicitly records.
  The referees' request for another covariance term is advice, not proof that adding it
  would avoid double counting. B0's reconciliation remains Joseph's reserved wording item.
  [S05:42–45] [G1:198–202] [B4:40–54]
- A stopped construction/variance gate is not a measured undercoverage of the final reported
  intervals, and a held-out truth is not an independent detector-simulation sample. The
  explicit restrictions of both coverage declarations remain operative. [1B-STOP:14–58]
  [COV:630–654] [1B:715–728]

### Additional advice received after the initial draft

[The Grok referee-sufficiency assessment](INPUT-20261106-grok-referee-sufficiency.txt) is
preserved byte-for-byte as relayed by the interpreter. It is advice, not a decision or an
independent measurement. Its stage-status observations predate the terminal 1B outcome and
must not be presented as current execution state. Its framing point is retained: the
referees’ methods alternative does not scientifically require waiting for these campaigns
to finish. Joseph’s newer ruling nevertheless makes it the stated fallback, with measurement
options primary. It changes no scientific gate. [GROK] [FRAME06:26–32] [STOP06:91–121]

## 2. Evidence ledger

Each row keeps the referee request separate from the record that might answer it. “Reported”
does not mean resolved, validated or adopted. Numeric results are included only where they
change the scope decision, with their matrix or test kept beside them.

| Item and advisory origin | Current committed evidence and reporting state | Record/campaign that could change the assessment | What its outcomes license, and the surviving limit |
|---|---|---|---|
| **Coverage: adopted 2D procedure** — S04 issue 1; S05 issue 1; both Gemini coverage issues | **Not yet reported** for campaign (c). A2 revision 2 remains bound at `a6054769…`; A3 rules on the pilot-label collision and stage-4 completeness without changing M. Its affected labels are INVALID, not a new STOP; the two-STOP count and third-STOP rule stand. [COV-B2:125–162] [COV-A3:166–227] | COV2D (c), including the remade covariance at each held-out tune. [COV:600–654] | **Both COVER:** a bounded method-coverage statement at the tested truths, per bin and in the declared joint region. **Either UNDER-COVER:** identify tune/cells, factors and bias/width readouts. **INVALID/STOP/no result:** paper unchanged. No outcome validates the reported data-point intervals, draws the run-period/model terms, validates independent training samples, or removes the earlier fixed-truth failure. [COV:600–654] |
| **Coverage: 5D procedure and stopped attempt** — S04/S05 issue 1; Gemini coverage issues | **Reported, terminal: 1B stage 1 ended, §2b STOP under rule (iii).** The completed receipt fired the declared non-positive-denominator rule. Staged rule K and prerequisite checks had passed, but the attempt produced no 5D coverage reading. [1B-K:12–40] [1B-B3:32–85] [STOP06:70–121] | No continuation or redesign under the existing sequence. Stages 4–7 do not run. Joseph alone may override (iii) with an authorized new, post hoc declaration. [STOP06:91–97] | The actual STOP licenses reporting that the declared test did not run to a coverage result and describing its rule. It licenses neither coverage nor undercoverage of the 5D intervals, a general failure of first-order composition, a cause, or a statement about the 2D result. The earlier **both COVER / mixed / both UNDER-COVER** branches remain conditional design licences, not pending outcomes of this closed attempt. No inflation or compute follows. [STOP06:99–121] [1B:650–728] [1B-AM2:378–407] <!-- absence-ok: test-scope and terminal consequences of the cited STOP record, not a global absence claim --> |
| **Fake-data bias and prior dependence** — S04 issues 2/3/11; S05 issue 2; Gemini bias issues | **Reported, unresolved:** the with-period-block readout still lists the q3 tilt and A7 GiBUU; the latter flags R02/R06. The listing uses its declared grade matrix, with own-vertex omission where applicable; it is not a coverage test of the whole reported covariance. Joseph decided to build neither A1 nor A2. [FD-CPL:229–287] [FD-RULE:35–48] [BIAS:79–92] | The 1B attempt ended without a coverage reading; its declared tunes would probe a different, bounded question. [STOP06:91–114] REF-G1 adds an estimator comparison; B4 is terminal. Data-driven prior routes a1/a2 are not commissioned. [COMMISSION:35–52] [B4] [G1-OUT] | A 1B pass cannot erase known failures at different truths or certify a bias envelope. REF-G1 cannot identify which estimator is correct. B4's measured bias readout does not adopt a new estimator or term. Keeping this as a limitation versus changing the result belongs to the scope decision. [1B:719–728] [G1:204–225] [BIAS:85–89] |
| **Rounding instability and stability remedy** — all reports | **Reported, terminal:** B4 reads **NONE_PASS**, with G0 informative, no winner and no passer. The current estimator stays. The control's mean median/maximum are 0.759/6.83 statistical σ; cross-fitting's 0.528/4.22 still fail the fixed 0.3/1.0 bars and worsen bias at some truths. These are pseudo-data probe units, not a new data measurement. [B4:10–54] | No continuation from this probe. B0's exact reconciliation wording remains reserved. [B4:38–54] | **NONE_PASS** licenses the terminal failure statement and 1B on the current estimator after binding; it does not license presenting cross-fitting as a passing improvement, adding a seed/jitter term, or calling the estimator stable. Another remedy would need a new decision and declaration. [B4:38–54] |
| **Run-period inconsistency and block size** — all reports | **Reported:** RPD's readout is stage-0 SEES, R1 **OTHER**, R2 **CLUSTERED**; the quoted block is unchanged. Clustering concerns the cell offsets, not a causal localisation of the momentum step. [RPD-READ] [RPD-TEXT:9–23] | RPD itself is already reported. d1/d2 follow up at reco level. A replacement playlist block would be a separate covariance adoption. [RPD:598–657] [RECO:310–334] | RPD's declared **PERIOD-WIDE/SUBSET** would permit only their named localisations, but **OTHER** does not. **CLUSTERED** permits the between-group offset statement. **EXCHANGEABLE-COMPATIBLE** would permit a same-events size estimate; replacement requires Joseph. **INCONCLUSIVE** leaves the statement unchanged. None removes the unknown cause or validates block size/coverage. [RPD:598–657] |
| **Run-period reco diagnostics d1** — playlist/experimental investigation requested by all reports | **Not yet reported** in the committed record set: design bound, code/tests/mutation/audit and binding 2 required before a run. [RECO-B1:29–43] | d1's reco step, axis/rate tests and hadronic tests conditioned on common muon bins. [RECO:143–164] | **SEEN:** the step precedes unfolding, with its measured size/sign, not that unfolding contributes nothing. **NOT-SEEN-AT-3σ:** non-detection at that sensitivity, not absence. **HADRONIC-CONDITIONAL:** a recoil-side difference beyond the muon distribution; **VIA-MUON/NOT-DETECTED:** only their scoped non-detections. Axes/rates/carriers are descriptive. **STOP:** identify control only. No detector location or cause is licensed. [RECO:310–334] |
| **Run-period flux assignment d2** — the same experimental investigation | **Not yet reported**; same binding boundary as d1. Simulation fixes the predicted size before the data-side read. [RECO-B1:17–43] [RECO:203–229] | Declared flux-file swap, with its ordered outcome table. [RECO:203–229,310–334] | **NOT-SEEN:** no further d2 reading. **TRACKS:** the measured removed fraction and agreement with predicted playlist steps, naming only coincidence with the assigned flux files. **PARTIAL:** fraction descriptively. **DOES-NOT-TRACK:** reject this candidate as reproducing the step. **INCONCLUSIVE:** undecided. **STOP:** no reading. Even TRACKS neither determines which period/flux is right nor licenses “explained”, “corrected”, dropping the unknown cause, or changing C_PL. [RECO:310–334] |
| **2D shape difference: upstream accounting B-C** — S04 issue 9; S05 issue 5; both Gemini benchmark issues | **Reported, partial:** no new numerical upstream defect demonstrated in the inspected records; publication-side intermediate comparison remains partial. E_R and the precision reference are digest-bound. B-C supplies identities and internal consistency, not equality of every published extraction stage. [BC:1–27,29–66,89–126] | The prepared intermediate-array question, and REF-C2C1 on this analysis's inputs. Sending a question remains Joseph's act. [BC:89–126] | B-C permits no correction, coverage claim or claim of complete publication-pipeline reproduction. Missing comparison operands are a terminal limit of that inventory. c2 can narrow the location by one level; neither comparison supplies the absent publication intermediates. [BC:89–126] [C2:201–211] |
| **2D shape difference: c2** — binned cross-check requested by all reports | **Not yet reported.** Code/configuration bound; the addendum inserts a committed cells identity before the read. [C2-B2:39–85] | REF-C2C1's paired binned comparison at the frozen settings. [C2:142–211] | **input side:** similar descriptive distance from the publication on shared inputs; **algorithm side:** binned result closer at the published iteration count, sized by the declared ratio; **IBU farther:** descriptive only; **unresolved:** statistics only. Paired agreement/marginality/difference is read separately. No outcome identifies a cause, validates upstream equality, switches estimator or selects iterations by the result. A failed control ends the run. [C2:92–125,142–211] |
| **2D benchmark of the reported estimator: c1** — S04 issue 9; S05 limitation 8 | **Not yet reported** with c2. [C2-B2:39–85] | Run the joint-test settings on E_R's 2D inputs; paired difference from E_R. [C2:251–287] | **equivalent:** reproduces E_R within paired noise on these inputs; **setting-dependent:** measured setting dependence, not the right setting; **marginal:** statistic only. No combination of results or change to E_R/Q_R. Controls must pass. [C2:251–287] |
| **Algorithm/estimator dependence and claimed added information** — S04 issue 8; S05 learner-dependence item | **Reported:** REF-G1 R1 **differ**, T = 194.4 against calibrated bars 28.12/39.04; all controls pass. R2 is per-truth closure description, R3 descriptive precision. [G1-OUT:10–47] | Its uncertainty disposition is reserved for this scope decision. No new run follows from this reading. [G1-OUT:49–54] | **differ** licenses measured algorithm dependence, not an IBU replacement or a new systematic. **agree** would not have established superiority/additional information; **marginal** would have licensed only statistics. R2/R3 license neither coverage nor extra discrimination. All three outcome branches are included here to preserve the declaration's meaning, not to reopen the completed result. [G1:204–225] |
| **Low-stability cells** — S04 issue 7; S05 issue 6; Gemini low-stability issues | **Reported, disclosed:** R02/R06/R10/R15 have stability 0.16–0.25. Joseph retained all cells, with no stability criterion, and later required flags beside the values. This is not a finding that the affected cells are unbiased. [H2:35–43] [COMMISSION:47–52] | New scope/adoption decision only; no commissioned cell-removal campaign. [BIAS:85–89] [COMMISSION:47–52] | Referee suggestions to merge/drop cells do not authorize a selection after the data read. A change is Joseph's, explicitly post hoc; the current decision says no merge. No running campaign automatically licenses fewer cells or rehabilitates their precision. [FD-RULE:21–33] [FRAME:45–46] [BIAS:85–89] |
| **Detector-response mismatch and held-out samples** — S04 issue 4; S05 issues 8/9; Gemini cross-fitting item | The prior-shape/fixed-response tests and presentation disclosures are reported. Broader response mock-data b1/b2 were **not commissioned**; b0 is a bounded existing-record disclosure, not a new validated response study. The declared coverage natures keep the nominal detector response and training rows. [COMMISSION:35–52] [1B:719–728] [COV:645–654] | Existing COV2D/1B for their truth-specific questions; a genuinely different response/sample test would require separate authorization. | Both tunes COVER would still concern these truths on fixed simulation. It would not prove coverage on independent detector simulation, calibrate absent response components, or satisfy every referee's response-mismatch request. B4's cross-fit candidate failed its own probe and is not adopted. [1B:719–728] [COV:645–654] [B4] |
| **C_model, generator comparisons, target/sample defects and correlation sensitivity** — S04 issue 10; S05 issue 7; Gemini model/comparator issues | The paper reports descriptive comparisons with explicit construction and sample limitations. The presentation read still treats these as major requests. Changing the framing does not certify comparator samples or turn a distance into exclusion. [PAPER:251–279] [S05:63–72] [G05:53–64] | Referee-scope items e1–e5 were not commissioned. REF-G1 compares algorithms, not generator validity. [COMMISSION:47] [G1:204–213] | No coverage or head-to-head pass supplies native-target predictions, repairs sample integrity or calibrates physical generator exclusion. A descriptive-only presentation may satisfy part of Sonnet's request; Gemini asks for further work. Such work or a covariance change needs its own decision. [S04:99–109,138–139] [S05:104–105,119–123] [G05:53–64] |
| **Self-containment, matched figures, definitions and reproducibility** — S04 issue 12; S05 presentation/figure-band items; Gemini presentation items | **Reported presentation revision**, not scientific resolution: the later read acknowledges added uncertainty tables and correlation matrix but still requests accessible load-bearing evidence, matched estimator/band figures, clearer definitions/normalization provenance and reproducible release products. [READ05:35–50] [S05:128–164] [G05:150–175] | Paper lane's future revision and Joseph's release/review acts; no new analysis commissioned by this inventory. | Moving technical details is acceptable only if the remaining claims can be assessed. A methods framing does not permit hiding failures or treating an obsolete covariance as the current interval. Collaboration contact, data release, submission/deposit and claim changes remain reserved. [FRAME:47–54] |

### Why remaining favourable results still leave a scope decision

COV2D and the declared 1B design concern the **procedure's remade covariance at particular truths**.
The 1B attempt is now terminal without a reading; it is not among the remaining campaigns.
The restrictions below describe their scientific scope, with the omissions
and carryovers stated in their declarations. Neither certifies the reported intervals made at
the data. d1/d2 cannot remove the unknown-cause clause even under their most informative
readings. c2/c1 can localise estimator/input sensitivity but cannot identify the correct
pipeline. The fake-data failures, terminal stability failure and measured estimator
dependence therefore still require disposition if the remaining campaigns report favourable
outcomes. This is an inference about the declarations' scope, not a forecast or a veto on
Joseph's framing decision. [COV:630–654] [1B:715–728] [RECO:310–334] [C2:201–287]
[BIAS:85–92] [B4:38–54] [G1-OUT:38–54]

The truth provenance also travels with a favourable result: G18 shares the model term’s
2p2h family, and AR23 shares G18’s quasielastic model. Changing truth does not create a new
training sample. COV2D’s test is one-sided; its report must identify weakened cells and give
the spread-alone readout beside the verdict, because the undrawn model term can mask a
shortfall in drawn blocks. Clipping’s false-pass risk and the linear composition/endpoint
approximation remain report/note facts; a pass does not establish multiplicative composition.
[1B:660–673] [COV:613–654] [1B-AM2:388–407]

REF-G1’s central-difference reading uses paired statistical, universe and normalization
blocks. It excludes the model block and the carried lateral, C_resp and C_PL blocks. Its
precision comparison includes the model block but still excludes those carried blocks. The
measured algorithm dependence is scoped to that comparison; it is not a test with a fully
remade publication covariance for both estimators. [G1:113–126]

## 3. Options for the batched decision

Joseph’s current target makes **A and B the primary measurement paths, and C the stated
fallback**; D is a holding posture, not a coequal publication target. This ordering is his
ruling, not the owner’s recommendation. [FRAME06:26–32]

The following are conditional choices, **not recommendations or admissions**. “Needs” names
the evidential or decision conditions; it does not commission extra work. Text consequences
give locations and direction only. No replacement manuscript language is drafted.

| Option | What the paper would claim | Outcomes/decisions it needs | Text locations and direction | Stated limitations that remain |
|---|---|---|---|---|
| **A. Primary: measurement as currently framed** | The adopted multi-observable cell-integrated measurement and covariance remain the headline, with methods findings supporting it. [FRAME:22–31] | A defensible uncertainty interpretation for the primary 5D claim; the current 1B route has ended without the intended reading, so that condition is unmet. Joseph must dispose of this terminal limit, the COV2D result when reported, known bias, B4 NONE_PASS, REF-G1 dependence and low-stability cells. Remaining favourable results alone cannot satisfy every referee request. No new run is authorized here. [STOP06:91–121] [FRAME06:26–32] [BIAS:79–92] [G1-OUT:49–54] | Title/abstract/Introduction keep the measurement lead. Validation/Limitations integrate only the licensed results; generator-comparison prominence and precision language follow the decided scope. Tables/covariance change only under an adoption decision. [FRAME:22–31] [PAPER] | Tested-truth and fixed-response limits, unvalidated data-point intervals, residual bias, instability, unknown period cause, cell stability and descriptive generator interpretation, except insofar as separately resolved and ratified. [COV:645–654] [1B:719–728] [RECO:310–334] [B4] |
| **B1. Primary: narrow the headline to the existing 2D result; higher dimensions diagnostic** | E_R/Q_R, with model dependence beside it, supply the measurement headline; the higher-dimensional results become demonstrations or supporting diagnostics. There is a recorded earlier “for now” 2D-led scope, but the subsequent measurement framing supersedes any assumption that it is automatically current. [ADOPT2D:28–59] [FRAME:22–31] | Joseph explicitly narrows the headline and makes the 5D intervals diagnostic; a 5D coverage pass is then not a prerequisite for a primary 2D claim. COV2D and c2/c1 inform the 2D case, but no favourable result automatically validates the reported data-point intervals or explains the period/benchmark differences. The terminal 1B STOP itself adopts no narrowing. [FRAME06:26–32] [STOP06:106–121] [COV:630–654] [C2:201–287] | Title/abstract/Introduction and results ordering make the 2D result primary. Multi-observable table and Discussion change claim status; the companion note retains measured outcomes and their qualifications. [ADOPT2D:54–59] [FRAME:22–31] | Current 2D covariance's data-point validation limit, prior/model dependence, post-comparison estimator choice, benchmark shape difference and run-period cause; higher-dimensional bias/stability findings remain diagnostics. [COV:645–654] [C2:29–55] [RECO:310–334] |
| **B2. Primary scope variant: narrow the reported cells or phase space** | A restricted measurement only where the newly defined result can be supported, with excluded/diagnostic regions identified. This is a referee-suggested possibility, not an available selection under the current contract. [S04:160] [S05:37–40,57–61] | A new Joseph decision explicitly superseding the fixed-cell/no-merge rules, a post hoc label and separately declared estimator/covariance/validation consequences. Removing a failing cell is not evidence that the retained joint result is valid. No subset is selected in this package. [FD-RULE:21–33] [BIAS:85–89] [COMMISSION:47–50] | Cell/result/covariance tables and their denominators, title/abstract scope and Limitations would all need revision after the new decision. [H2:35–43] [FD-RULE:21–33] | Selection history, remaining coverage/bias/period limits and any unrecovered response components. A reporting restriction does not establish independent validation. [FD-RULE:21–33] [1B:719–728] |
| **C. Stated fallback: methods and validation study** | Empirical performance and limitations of unfolding on these open data; the multi-observable table illustrates algorithm behaviour with explicitly unvalidated intervals, rather than serving as a new calibrated benchmark. This is the alternative both advisory series describe. [S04:160] [G04:146–147] [S05:144] [G05:146] | Put the fallback to Joseph if intended measurement conditions fail: adverse coverage, a terminal STOP preventing a required reading without an override, or unresolved bias/stability/period problems that he does not accept under the intended measurement claim. The referees’ methods alternative does not scientifically require campaign completion. Joseph still decides adoption and timing; a STOP is not automatic demotion or measured undercoverage. [FRAME06:26–32] [STOP06:91–121] [GROK] [S05:131–144] | Title/abstract/Introduction, table purpose, comparison prominence and Discussion lead with demonstrated successes/failures and the bounds of interpretation. Keep load-bearing evidence accessible; update future release scope to match. [S05:131–149] [G05:132–153] | All measured failures and untested components remain visible. Methods framing does not validate uncertainties, repair samples or permit physical exclusions, and does not itself clear publication/release holds. [FRAME:47–54] [G1:204–213] <!-- absence-ok: this option preserves the explicitly cited validation limits; it makes no claim that results are absent beyond those products --> |
| **D. Keep the decision pending; no publication advance yet** | No new claim: preserve the current disclosed state while the named reports arrive. This is the existing WAITING-JOSEPH posture, not an extra scientific campaign. [QUEUE:92] | Refresh the packet from committed terminal reports, or bring an inability to report/stopping-rule event to Joseph. Do not treat a deadline, stopped test or partial ensemble as permission to continue indefinitely. [COV:553–566] [COV-B2:95–162] [1B-B3:60–85] | No manuscript change from this option alone; update the evidence packet and pending-status dates. [QUEUE:92] | Current limitations and publication holds all remain. [FRAME:47–54] |

**Measurement conditions after the terminal STOP.** The declared 1B reading cannot now
arrive from this attempt. Joseph must decide whether to narrow the headline, explicitly
accept the unresolved limitation, authorize a new post hoc route, or take the stated
fallback. A COV2D pass cannot supply a 5D reading. B1 can avoid a primary 5D interval claim
only through an explicit narrowing decision; its own 2D limits remain. B2 still needs a new
cell-definition decision and separate evidence. The STOP triggers consideration of these
choices, not an automatic methods framing, observed undercoverage or a 2D adoption.
[STOP06:91–121] [FRAME06:26–32] [COV:645–654]

### Required outcome and disposition map for the primary measurement paths

| path | Coverage condition | Other conditions that no pending pass silently discharges |
|---|---|---|
| A, current 5D headline | The intended 5D method reading is unavailable from the terminal 1B attempt. A fresh reading needs Joseph’s override of (iii), a new post hoc declaration and a successful new route; accepting an unresolved uncertainty interpretation instead is also his separate scope/claim decision. COV2D’s possible COVER result cannot stand in for 5D. [STOP06:91–121] [FRAME06:26–32] | Bias/prior dependence, B4 NONE_PASS, algorithm dependence, low-stability cells and the unexplained period effect each need explicit disposition. Even d2 TRACKS cannot remove the unknown-cause clause. REF-G1 differ neither supplies an uncertainty nor identifies the correct estimator. No current declared pass meets every referee condition. [BIAS:85–92] [B4:38–54] [RECO:310–334] [G1-OUT:38–54] |
| B1, existing 2D headline with 5D diagnostic | COV2D both COVER would supply its bounded procedure statement; either UNDER-COVER requires disposition of the named shortfall; STOP/INVALID supplies no coverage reading. None validates the reported data-point intervals. A 5D coverage pass need not be a scientific prerequisite once Joseph explicitly removes a primary 5D interval claim, but the scope change is not automatic. [COV:600–654] [STOP06:106–121] | c2/c1 outcomes only narrow the diagnostic statement under their licence tables. The published-shape difference, period cause, estimator-selection history and the reported 2D interval limits still need appropriate claims. The higher-dimensional failures stay visible as diagnostics. [C2:201–287] [FRAME06:26–32] |
| B2, restricted cells/phase space | No outcome of the existing campaigns authorizes the new subset or establishes its intervals. A new definition and its corresponding covariance/validation obligations would need Joseph’s explicit post hoc decision before this can be a concrete measurement option. [FD-RULE:21–33] [COMMISSION:47–52] | Removing a low-stability or failing cell is not evidence that the retained joint result is valid. Preserve the selection history and obtain evidence for the actual proposed estimator/region. No cells or cuts are selected here. [FD-RULE:21–33] [BIAS:85–89] |

The final-decision timing itself is now reserved: the framing ruling calls for coverage
readouts on main, while the adopted stopping rule ended 1B without a coverage reading. The
STOP is a terminal report, not fulfillment of that readout condition. Joseph must dispose
of this branch of the decision, including whether to proceed on narrowed claims or the
stated fallback; this package grants no waiver or automatic restart. [FRAME06:26–32]
[STOP06:91–121]

## 4. Reserved items that travel with the scope decision

| Item | Decision to make and record to carry |
|---|---|
| **Estimator-dependence uncertainty** | REF-G1's measured difference enters as an uncertainty, a stated limitation, or both. A new block needs Joseph's adoption and construction/validation choices; the readout neither defines nor authorizes it. Do not silently add the outer product or replace the estimator. [G1-OUT:38–54] [G1:204–225] |
| **Plug-in truth in 1B — moot unless (iii) is overridden** | The terminal STOP makes this item moot under the current sequence. Only after Joseph overrides (iii) would inclusion be reconsidered. Binding 3’s separate-binding/capture/new-gate requirements and recorded estimate of about 120 CPU node-h or more are historical scope/price information, not a live request or authority to restart. [STOP06:91–121] [1B-B3:50–59] |
| **Known fake-data bias/prior dependence** | Decide its consequence for framing. The operative decision builds neither A1 nor A2, keeps measured failures stated and makes no cell merge. A different uncertainty/correction route would require a new decision. [BIAS:79–92] |
| **B0 reconciliation** | The seeds-inert/bootstrap-jitter explanation is still Joseph's exact-wording decision, through the paper lane and PRD read. It is not settled by B4, REF-G1 or this package, and is not permission for another variance block. [B4:40–54] [G1:198–202] |
| **Cells, estimator, period block and calibration claims** | Whether a narrowed scope changes any adopted product; any such change must identify what is superseded, how the dependent covariance/tests/release change and the post hoc history. Current d1/d2 licences keep the period block and unknown cause. Claims/KI-85 are Joseph's. [FD-RULE:21–33] [RECO:310–334] [FRAME:51–54] |
| **Comparators and added-information claims** | Decide how prominently descriptive generator distances and algorithm precision ratios belong under the chosen framing. REF-G1 adds no extra-discrimination or coverage claim; comparator/sample repair and physical exclusion remain separate questions. [G1:204–213] [S05:63–72] [G05:53–64] |
| **Compute availability** | Delta’s availability is a separate operational ruling. It does not move the bound COV2D/1B sequences off Perlmutter or authorize this package to launch compute. Any new use needs its own price, environment/access and binding. [FRAME06:34–41] |
| **Publication and release acts** | Collaboration review/contact, data-file release, manuscript wording/claim approval, deposit, submission and tagging remain separate reserved acts. An evidence-package PR approves none of them. [FRAME:47–54] |

## 5. Pending reports and calendar

These are dates and gates in committed declarations, **not promises of completion**. The
1B row is now terminal, not a pending coverage campaign; the older conditional clauses above
remain design history only. [STOP06:91–121] The
snapshot's front-door queue lags the actual COV2D binding, 1B binding and REF-G1 terminal
outcome; the entries below use the governing artifacts. No scheduler was queried. [QUEUE]
[COV-B2] [1B-B3] [G1-OUT]

| Item | Status at snapshot; next report | Dated constraint and meaning |
|---|---|---|
| COV2D (c) | **Not yet reported.** A2 revision 2 remains the bound M; A3 defines the pilot-label repair and stage-4 completeness requirement before blocks/readout. [COV-A3:166–227] | **2026-12-01 is the latest submission date for every universe-input-reading job**, not the result due date. The declaration gives latest completion **2026-12-12**, readout/rest **2026-12-18**, against input exposure **2026-12-19**. If the submission cutoff cannot be met, the bulk does not start and no partial ensemble is graded. [COV:553–566] |
| 1B method coverage | **Reported, terminal:** stage 1 ended on the §2b receipt STOP under rule (iii); no coverage reading. The staged κ and prerequisite checks remain measured history. [STOP06:70–121] [1B-K] | Outcome dated **2026-11-06**. The bulk and operational stages 4–7 do not run. This is a terminal report to scope, not an overdue coverage readout or permission to redesign. Reopening needs Joseph’s override and a new post hoc declaration; the plug-in item is moot meanwhile. [STOP06:91–121] |
| REF-C2C1 read | **Outcome not yet reported at the refresh snapshot.** The read is re-bound at M′ `af70e9c4…` after the C-PUB operand control STOP; the units stand and its readings/licences are unchanged. A successful read receipt alone does not substitute for the director’s outcome record. [C2-NEW:99–196] | Binding/addendum dated **2026-11-06**; no result date is fixed there. The declaration records universe-input exposure **2026-12-19** and production-flux exposure **2026-12-25**. The actual binding has **no universe pass**, so do not present the optional pass as commissioned work or those exposure dates as a forecast. [C2:288–318] [C2-B2:61–65] <!-- absence-ok: completion-date statement is scoped to the cited binding, and the optional universe-pass exclusion is its explicit scope --> |
| d1/d2 | **Not yet reported**; design bound, code audit and binding 2 required before run. [RECO-B1:29–43] | Design binding **2026-11-04**. The commissioning decision gives **before 2026-12-15 if d2 reads the zero loops**; the later design instead uses the inverse reco relation, not that new loop pass. Its dumps' recorded exposure is **about 2026-12-30** and retention is rechecked at P0. Neither date is a completion commitment. [COMMISSION:41–46] [RECO:165–177,230–257] [RECO-B1:38–43] |
| B4 / REF-G1 / RPD / B-C | **Reported**, respectively terminal NONE_PASS, R1 differ, R1 OTHER/R2 CLUSTERED and partial component accounting. They are inputs to the decision, not pending campaigns to rerun. [B4] [G1-OUT] [RPD-READ] [BC] | Dated outcomes and source snapshot are in the cited records. Their unresolved interpretation is not missing execution. |

## 6. Recommendation — reserved for the director

<!-- Intentionally empty: the director writes the recommendation. -->

## 7. Review and refresh handoff

The independent second read and its [disposition](REVIEW-DISPOSITION.md) accompany this package. Refresh the source
snapshot, campaign terminal-report rows, and any new adoption/wording decisions before
presenting this as the final batched decision. Preserve earlier STOPs and qualifications.
The review checks this inventory's fidelity; it does not independently validate a covariance
or grant publication approval.

[QUEUE]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/OPEN_ITEMS.md
[FRAME]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/DECISION-20261027-joseph-measurement-framing-and-limitation-scoping.md
[BIAS]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/DECISION-20261102-joseph-bias-and-stabilisation-routes.md
[FRAME06:26–41]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/2968b58ac9c9031a13dd5acb98e661f28964423d/docs/orchestration/DECISION-20261106-joseph-measurement-target-and-delta.md#L26-L41
[1B-B3]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-1B-STAGED-BINDING-3.md
[REVIEW-RULE]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/CAMPAIGN-REVIEW-20260929.md
[READ04]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261104/README.md
[READ05]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261105/README.md
[S04:26–80,150–160]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261104/sonnet-referee-answer.txt#L26-L160
[S04:160]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261104/sonnet-referee-answer.txt#L160
[G04:32–68,140–144]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261104/gemini-referee-answer.txt#L32-L144
[G04:146–147]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261104/gemini-referee-answer.txt#L146-L147
[S05:26–61,89–120,135–144]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261105/sonnet-referee-answer.txt#L26-L144
[S05:131–144]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261105/sonnet-referee-answer.txt#L131-L144
[G05:25–69,122–124,140–144]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261105/gemini-referee-answer.txt#L25-L144
[G05:146]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261105/gemini-referee-answer.txt#L146
[S05:92–105]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261105/sonnet-referee-answer.txt#L92-L105
[G05:86–104]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261105/gemini-referee-answer.txt#L86-L104
[G04:45–48]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261104/gemini-referee-answer.txt#L45-L48
[G05:43–46]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261105/gemini-referee-answer.txt#L43-L46
[C2:29–55]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/REF-C2C1-DECLARATION.md#L29-L55
[G05:66–69]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261105/gemini-referee-answer.txt#L66-L69
[PAPER:301]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/analysis-note/paper_body.tex#L301
[H2:35–43]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/DECISION-20261024-joseph-h2-16-cell-definition.md#L35-L43
[S05:42–45]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261105/sonnet-referee-answer.txt#L42-L45
[G1:198–202]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/REF-G1-DECLARATION.md#L198-L202
[B4:40–54]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/OUTCOME-20261105-fd-stab-none-pass.md#L40-L54
[1B-STOP:14–58]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-1B-STAGED-STAGE1-STOP-REPORT.md#L14-L58
[COV:630–654]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/COV2D-DECLARATION.md#L630-L654
[1B:715–728]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-1B-STAGED-DECLARATION.md#L715-L728
[GROK]: INPUT-20261106-grok-referee-sufficiency.txt
[FRAME06:26–32]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/2968b58ac9c9031a13dd5acb98e661f28964423d/docs/orchestration/DECISION-20261106-joseph-measurement-target-and-delta.md#L26-L32
[STOP06:91–121]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/2968b58ac9c9031a13dd5acb98e661f28964423d/docs/orchestration/OUTCOME-20261106-1b-stage1-receipt-stop.md#L91-L121
[COV-B2:125–162]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/COV2D-BINDING-2.md#L125-L162
[COV-A3:166–227]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/2968b58ac9c9031a13dd5acb98e661f28964423d/docs/orchestration/state/measurement-paper/5d-community-20261024/COV2D-BINDING-2.md#L166-L227
[COV:600–654]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/COV2D-DECLARATION.md#L600-L654
[1B-K:12–40]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-1B-STAGED-STAGE0-REPORT.md#L12-L40
[1B-B3:32–85]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-1B-STAGED-BINDING-3.md#L32-L85
[STOP06:70–121]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/2968b58ac9c9031a13dd5acb98e661f28964423d/docs/orchestration/OUTCOME-20261106-1b-stage1-receipt-stop.md#L70-L121
[STOP06:91–97]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/2968b58ac9c9031a13dd5acb98e661f28964423d/docs/orchestration/OUTCOME-20261106-1b-stage1-receipt-stop.md#L91-L97
[STOP06:99–121]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/2968b58ac9c9031a13dd5acb98e661f28964423d/docs/orchestration/OUTCOME-20261106-1b-stage1-receipt-stop.md#L99-L121
[1B:650–728]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-1B-STAGED-DECLARATION.md#L650-L728
[1B-AM2:378–407]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/6d93dd4284c1d378836ba275923d490f0f6c62f3/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-1B-STAGED-AMENDMENT-2.md#L378-L407
[FD-CPL:229–287]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-CT-5B-ADDITION-REPORT.md#L229-L287
[FD-RULE:35–48]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-DIRECTOR-RULINGS.md#L35-L48
[BIAS:79–92]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/DECISION-20261102-joseph-bias-and-stabilisation-routes.md#L79-L92
[STOP06:91–114]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/2968b58ac9c9031a13dd5acb98e661f28964423d/docs/orchestration/OUTCOME-20261106-1b-stage1-receipt-stop.md#L91-L114
[COMMISSION:35–52]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/DECISION-20261104-joseph-referee-analysis-commission.md#L35-L52
[B4]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/OUTCOME-20261105-fd-stab-none-pass.md
[G1-OUT]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/OUTCOME-20261106-ref-g1-r1-differ.md
[1B:719–728]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-1B-STAGED-DECLARATION.md#L719-L728
[G1:204–225]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/REF-G1-DECLARATION.md#L204-L225
[BIAS:85–89]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/DECISION-20261102-joseph-bias-and-stabilisation-routes.md#L85-L89
[B4:10–54]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/OUTCOME-20261105-fd-stab-none-pass.md#L10-L54
[B4:38–54]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/OUTCOME-20261105-fd-stab-none-pass.md#L38-L54
[RPD-READ]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-rpd/run/readout/fd_rpd.json
[RPD-TEXT:9–23]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/rpd-sentence-paper-20261104/REPORT.md#L9-L23
[RPD:598–657]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-RPD-DECLARATION.md#L598-L657
[RECO:310–334]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-RPD-RECO-DECLARATION.md#L310-L334
[RECO-B1:29–43]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-RPD-RECO-BINDING-1.md#L29-L43
[RECO:143–164]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-RPD-RECO-DECLARATION.md#L143-L164
[RECO-B1:17–43]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-RPD-RECO-BINDING-1.md#L17-L43
[RECO:203–229]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-RPD-RECO-DECLARATION.md#L203-L229
[RECO:203–229,310–334]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-RPD-RECO-DECLARATION.md#L203-L334
[BC:1–27,29–66,89–126]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/component-accounting-20261104/REPORT.md#L1-L126
[BC:89–126]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/component-accounting-20261104/REPORT.md#L89-L126
[C2:201–211]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/REF-C2C1-DECLARATION.md#L201-L211
[C2-B2:39–85]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/REF-C2C1-BINDING-2.md#L39-L85
[C2:142–211]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/REF-C2C1-DECLARATION.md#L142-L211
[C2:92–125,142–211]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/REF-C2C1-DECLARATION.md#L92-L211
[C2:251–287]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/REF-C2C1-DECLARATION.md#L251-L287
[G1-OUT:10–47]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/OUTCOME-20261106-ref-g1-r1-differ.md#L10-L47
[G1-OUT:49–54]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/OUTCOME-20261106-ref-g1-r1-differ.md#L49-L54
[COMMISSION:47–52]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/DECISION-20261104-joseph-referee-analysis-commission.md#L47-L52
[FD-RULE:21–33]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-DIRECTOR-RULINGS.md#L21-L33
[FRAME:45–46]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/DECISION-20261027-joseph-measurement-framing-and-limitation-scoping.md#L45-L46
[COV:645–654]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/COV2D-DECLARATION.md#L645-L654
[PAPER:251–279]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/analysis-note/paper_body.tex#L251-L279
[S05:63–72]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261105/sonnet-referee-answer.txt#L63-L72
[G05:53–64]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261105/gemini-referee-answer.txt#L53-L64
[COMMISSION:47]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/DECISION-20261104-joseph-referee-analysis-commission.md#L47
[G1:204–213]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/REF-G1-DECLARATION.md#L204-L213
[S04:99–109,138–139]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261104/sonnet-referee-answer.txt#L99-L139
[S05:104–105,119–123]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261105/sonnet-referee-answer.txt#L104-L123
[READ05:35–50]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261105/README.md#L35-L50
[S05:128–164]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261105/sonnet-referee-answer.txt#L128-L164
[G05:150–175]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261105/gemini-referee-answer.txt#L150-L175
[FRAME:47–54]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/DECISION-20261027-joseph-measurement-framing-and-limitation-scoping.md#L47-L54
[C2:201–287]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/REF-C2C1-DECLARATION.md#L201-L287
[BIAS:85–92]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/DECISION-20261102-joseph-bias-and-stabilisation-routes.md#L85-L92
[G1-OUT:38–54]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/OUTCOME-20261106-ref-g1-r1-differ.md#L38-L54
[1B:660–673]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-1B-STAGED-DECLARATION.md#L660-L673
[COV:613–654]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/COV2D-DECLARATION.md#L613-L654
[1B-AM2:388–407]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/6d93dd4284c1d378836ba275923d490f0f6c62f3/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-1B-STAGED-AMENDMENT-2.md#L388-L407
[G1:113–126]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/REF-G1-DECLARATION.md#L113-L126
[FRAME:22–31]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/DECISION-20261027-joseph-measurement-framing-and-limitation-scoping.md#L22-L31
[PAPER]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/analysis-note/paper_body.tex
[ADOPT2D:28–59]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/DECISION-20261024-joseph-adopt-re2-2d-refined.md#L28-L59
[STOP06:106–121]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/2968b58ac9c9031a13dd5acb98e661f28964423d/docs/orchestration/OUTCOME-20261106-1b-stage1-receipt-stop.md#L106-L121
[ADOPT2D:54–59]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/DECISION-20261024-joseph-adopt-re2-2d-refined.md#L54-L59
[S05:37–40,57–61]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261105/sonnet-referee-answer.txt#L37-L61
[COMMISSION:47–50]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/DECISION-20261104-joseph-referee-analysis-commission.md#L47-L50
[S05:144]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261105/sonnet-referee-answer.txt#L144
[S05:131–149]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261105/sonnet-referee-answer.txt#L131-L149
[G05:132–153]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/referee-rerun-20261105/gemini-referee-answer.txt#L132-L153
[QUEUE:92]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/OPEN_ITEMS.md#L92
[COV:553–566]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/COV2D-DECLARATION.md#L553-L566
[COV-B2:95–162]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/COV2D-BINDING-2.md#L95-L162
[1B-B3:60–85]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-1B-STAGED-BINDING-3.md#L60-L85
[1B-B3:50–59]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-1B-STAGED-BINDING-3.md#L50-L59
[FRAME:51–54]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/DECISION-20261027-joseph-measurement-framing-and-limitation-scoping.md#L51-L54
[FRAME06:34–41]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/2968b58ac9c9031a13dd5acb98e661f28964423d/docs/orchestration/DECISION-20261106-joseph-measurement-target-and-delta.md#L34-L41
[COV-B2]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/COV2D-BINDING-2.md
[1B-K]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-1B-STAGED-STAGE0-REPORT.md
[C2-NEW:99–196]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/2968b58ac9c9031a13dd5acb98e661f28964423d/docs/orchestration/state/measurement-paper/5d-community-20261024/REF-C2C1-BINDING-2.md#L99-L196
[C2:288–318]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/REF-C2C1-DECLARATION.md#L288-L318
[C2-B2:61–65]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/REF-C2C1-BINDING-2.md#L61-L65
[COMMISSION:41–46]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/DECISION-20261104-joseph-referee-analysis-commission.md#L41-L46
[RECO:165–177,230–257]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-RPD-RECO-DECLARATION.md#L165-L257
[RECO-B1:38–43]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/measurement-paper/5d-community-20261024/FD-RPD-RECO-BINDING-1.md#L38-L43
[BC]: https://github.com/josephbaileyy/MINERvA-OmniFold/blob/1aa805b59eb037c5fcd978037ae282189aa33634/docs/orchestration/state/2d-closeout/stageF/methods/secondary-results/component-accounting-20261104/REPORT.md
