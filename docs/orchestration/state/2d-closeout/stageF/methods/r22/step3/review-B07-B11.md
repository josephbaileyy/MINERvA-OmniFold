# r22 Step 3 review: pieces B07, B09, B11

Reviewer: independent, read-only. Worktree `wt-con`, HEAD `6420ee7e`. The note files at HEAD equal those at base
`14a0415f`, so every diff below is an uncommitted working-tree edit. I read the diffs with
`git diff 14a0415f -- docs/analysis-note/<file>` for `sec_eavailw.tex` (B07), `sec_fived16.tex` (B09), and
`sec_fps.tex` and `sec_summary.tex` (B11). I checked them against `briefs/B07.md`, `B09.md`, `B11.md`, the three ledgers,
and the Step 2 and Step 3 writer briefs.

**Pieces without gaps (B06, B08, B10).** `git diff 14a0415f` of `sec_3d.tex`, `scalar_kinematics.tex`, `sec_5d.tex`
and `sec_joint.tex` is **empty**. Each file exists at the base, `git diff --quiet` returns rc=0 for each, and the
combined diff is 0 bytes.

**Edits outside the gaps.** There are none. Each changed line in the four files belongs to a listed gap: B07-g-03;
B09-g-04, g-11, g-03 and g-09; B11-g-05, g-09, g-08, g-01 and g-02.

**Counts.** There are 3 findings, all AMBIGUOUS and all minor. No finding is LOST, WEAKENED, MOVED-AWAY, ADDED or
BEYOND-NARROWED. One gap was not made: B11-g-10, which was correctly skipped. One older inaccuracy came to light while
I checked a ledger home: "leading-hadron angle".

## Findings

### F1. sec_eavailw.tex, B07-g-03: "Truth hadronic diagnostics are also retained: …"
- **direction:** AMBIGUOUS
- **base:** "The event-loop output files also store truth hadronic diagnostics: the proton and pion multiplicities and the
  leading-hadron angle."
- **new:** "Truth hadronic diagnostics are also retained: the proton and pion multiplicities and the leading-hadron
  angle."
- **why:** The base verb said what happens to these quantities: they are written out. "Retained" has no object, so it
  can be read as "kept as analysis variables", which the note nowhere claims. The note uses them nowhere else, so the
  narrowed form's "documented analytical role" has no text in the note to carry. The writer correctly added none. The
  storage location may leave the note. The plain fact that the quantities are stored should not become vaguer.
- **fix:** reword to "Truth hadronic diagnostics are also stored: …". This parallels the preceding "a shifted $W$ is
  stored for each lateral universe" and still names no output file. Update probe B07-1 to match.

### F2. sec_fived16.tex, B09-g-03: "The Poisson pseudo-experiments test the bias … this is a bias test, not a coverage test."
- **direction:** AMBIGUOUS (minor narrowing of scope)
- **base:** "This is a bias test, not a coverage test: Poisson pseudo-experiments with no draws of the systematic
  parameters cannot test the width of the intervals, and the detector response is not probed."
- **new:** "The Poisson pseudo-experiments test the bias with the systematic parameters not drawn and the detector
  response fixed, so they cannot test the interval widths or probe the detector response: this is a bias test, not a
  coverage test."
- **why:** In the base, "the detector response is not probed" is a separate clause. It qualifies the whole held-out-tune
  test, which is the pseudo-experiments plus the noise-free closure. The new sentence makes the pseudo-experiments its
  only subject, so the statement no longer covers the closure. The closure is also run under the simulation's detector
  response ("The ratio is applied to the simulated truth, under the simulation's detector response"). The trailing
  "this" now most naturally refers to the pseudo-experiments alone. What the sentence keeps is right: the strength
  ("cannot test"; "not a coverage test"), both limitations, and no new fact, since "fixed" is supported by the sentence
  just quoted.
- **fix:** reword so that the test, not only its pseudo-experiments, is the subject. For example: "The test evaluates
  the bias with the systematic parameters not drawn and the detector response fixed, so it cannot test the interval
  widths or probe the detector response: this is a bias test, not a coverage test." This is the same length. Update
  probe B09-3.

### F3. sec_fived16.tex, B09-g-09: the `tab:fived16-gen` caption
- **direction:** AMBIGUOUS (minor)
- **base caption:** "$\chi^2$ with its number of degrees of freedom, against $C_{\mathrm{total}}+C_{\mathrm{resp}}+V_g$,
  with the shape-only $\chi^2$ beside it." The base prose was: "The variant without the response block, against
  $C_{\mathrm{total}}+V_g$, gives $\chi^2$ of …"
- **new caption:** "$\chi^2$ with its number of degrees of freedom, against $C_{\mathrm{total}}+C_{\mathrm{resp}}+V_g$,
  the shape-only $\chi^2$ and the $\chi^2$ without the response block, against $C_{\mathrm{total}}+V_g$."
- **why:** In "A, against X, B and C, against Y", the final "against $C_{\mathrm{total}}+V_g$" can bind to the
  shape-only $\chi^2$ as well as to the new column. The prose above the table says that the shape-only $\chi^2$ is the
  full-covariance $\chi^2$ with the normalization free, not a $\chi^2$ against $C_{\mathrm{total}}+V_g$. The column values
  themselves are exact; see the ruling below.
- **fix:** reword the caption so that the new covariance binds only to the last column. For example: "$\chi^2$ with its
  number of degrees of freedom against $C_{\mathrm{total}}+C_{\mathrm{resp}}+V_g$, the shape-only $\chi^2$, and, in the
  last column, the $\chi^2$ without the response block, against $C_{\mathrm{total}}+V_g$." The caption is a probe string
  in B09-4, so update that probe.

## A gap not made

- **B11-g-10** (ALLOW-NARROW): "The release design and its public example have no bearing on the choice of the
  five-axis covariance of the configuration-(a) central value (§9.6)."
  - The sentence prints unchanged in `sec_summary.tex`.
  - Configuration (a) is defined in `sec_method.tex` (Table `tab:estimators-matrix`), and its covariance section is
    `sec:eavailw-adopted`. Both are outside B11's files, so skipping the gap was the only move the rules allowed.
  - `sec_method.tex` was edited by another piece, but no "no bearing" statement was added there. The independence fact
    therefore still prints exactly once, with no loss.
  - Nothing in the ledger records the skip. B11's ledger has no row for g-10, so the director should take the skip from
    the writer's report, not from the ledger.

## Older inaccuracy found while checking a ledger home (not a rewrite defect)

- The base and new text both call the third diagnostic the "leading-hadron angle".
  - At `6420ee7e`, the stored branch is `MC_hadangle`, described as "truth hadronic-system angle (rad)"
    (`MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp:438`).
  - It is filled by `CVUniverse::GetHadronAngleTrue()` (`MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h:269-282`).
    That function returns the polar angle of the **summed** momentum of all final-state particles except muons and
    neutrinos, not the angle of a leading hadron.
- The writers were right to keep the base wording, since the round changes no claim. The note's term should be corrected
  in a separate accuracy fix, routed to the director.

## Rulings on the specific points in this range

### B07-g-03: is code an acceptable home for a storage fact?

**Ruling: OK.** Apply F1's reword, and add the caveats below to the record.

- **The source code is an acceptable home.** It is the authoritative statement of what the event loop writes.
  - Ledger row B07-2 records the fact itself in the r22 ledger and points to two homes:
    - `runEventLoopOmniFold.cpp`, whose `out->Branch` lines 436-438 write all three branches;
    - `nd-unfolding/pet/P5B_LATERAL_SOURCE_DECISION.md:12`, an audited endpoint schema that lists
      `MC_hadangle,MC_nproton,MC_npip` in `mc_signal_reco`.
  - Both files are tracked at HEAD and at `d84124c5`, the commit at which the protection's search was run. That search
    used physics words, so it missed the branch-name record.
  - This satisfies "record … in the internal ledger before removing that detail".
- **Caveat 1.** The P5B audit covers the FPS lateral endpoints (`active_universe_5d/fps/`, built by the pre-full-event
  binary). It is not specific to the $W$ outputs this paragraph describes, so it corroborates the home but is not the
  primary home. The source code is.
- **Caveat 2.** The code's own name for the angle differs from the note's. See the older inaccuracy above.
- **The general question.** Code is a fit home for a storage or implementation fact, cited at a sha. It would not be a
  fit home for a presentation fact whose reader is the note's reader, such as B05-g-08, which is not in my range.

### B09-g-09: the column's values, ndf and covariance label

**Ruling: OK on values. Fix the caption per F3.**

- Each row of the new column uses the same macro pair as the base sentence, in the base order (GENIE CV, GENIE+MEC,
  NuWro, GiBUU, Tune v1), as `\fvval{g-<gen>-nocresp-chi2}/\fvval{g-<gen>-total-ndf}`.
- `values_fived16.tex` resolves them as follows, which matches the brief's quote exactly:

  | prediction | value | line | ndf | line |
  |---|---|---|---|---|
  | GENIE CV | 160.62 | :755 | 16 | :779 |
  | GENIE+MEC | 318.26 | :825 | 16 | :849 |
  | NuWro | 298.69 | :868 | 16 | :892 |
  | GiBUU | 68.44 | :790 | 8 | :806 |
  | Tune v1 | 360.79 | :911 | 16 | :935 |

- The ndf is the total ndf, as in the base. It is not the shape-only ndf (15 and 7).
- The covariance is named as $C_{\mathrm{total}}+V_g$, "without the response block", as in the base.
- The removed "in the order of Table …" clause is moot once the values are in the table.

### The other gaps in range, ruled OK

**B07-g-03:** OK apart from F1.

**B09-g-04:** OK.
- "Was measured" survives as "the measured training-seed block", and "zero in every cell" is kept.
- "The other seeds" became "every tested seed", which is the narrowed form's own wording.
- "Bitwise equal" became "identical", which is the narrowed form's word. It still asserts exact equality, so the zero
  stays one by construction, not a claim of negligible uncertainty.
- Nothing moves toward the refused "evaluated and found to be negligible".

**B09-g-11:** OK.
- "Two truths, each counted by its pseudo-experiments and by its closure" is kept as "the pseudo-experiment and closure
  results for two truths".
- The independence count stays attached to the references.
- "Gaussian references" matches the note's existing collective term two paragraphs earlier ("The Gaussian references
  are context only, because the bias is deterministic.").
- "Descriptive" comes from the narrowed form, and no strength is lost.

**B09-g-03:** OK apart from F2. The strength is kept, and the writer rightly kept "cannot test", which is stronger than
the narrowed form's "does not validate".

**B11-g-02:** OK.
- "Exists", "checksums", "a verifier that recomputes and checks its results", the bold "no release has been tagged or
  deposited", and the PDF-build limitation with its App. G citation all print.
- The PDF-build limitation also prints in `app_release.tex`.
- No public availability is implied.

**B11-g-05:** OK. "Without a quoted covariance" stays attached to the scope statement, and "only" adds nothing beyond
the base's "consists of". It also remains true of the existing but unquoted corrected covariance named in the file's
comment.

**B11-g-09:** OK. All five required elements print:
- the fixed estimator seed;
- one disjoint 100/100 split;
- the fixed truth;
- the evaluation (bin, pseudo-experiment) counting unit;
- `\covFPS` against `\covNominal`.

"Learned" was dropped, but the next sentence keeps "estimated widths".

**B11-g-08:** OK. Both scales and both panel roles are kept, and only "hence the two color schemes" is gone.

**B11-g-01:** OK.
- The date is gone. The binned purity correction, "not with refined negative-weight subtraction", and "the treatment
  designated for the extended-fiducial analysis" all print, with the App. C citation.
- The date's home is `app_negweight.tex`: "It comes from the extended-fiducial ME~FHC battery of 2026-06-10."
- It also prints at `app_provenance.tex` `fps-battery`.
- Neither home file changed in this round.
