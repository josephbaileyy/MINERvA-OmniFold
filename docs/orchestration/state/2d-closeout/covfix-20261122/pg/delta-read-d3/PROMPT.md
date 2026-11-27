You are an independent reviewer. Read ONLY files inside this directory (the current working directory). Do not open
any path outside it. Report findings; change nothing.

Subject: DESIGN-D3PRIME-II.md proposes replacing a log check (D3′(ii)) in a GENIE event-generation verifier. The old
check, `coverage_problems` in lane/pg_verify.py, needs "Need xsec spline for X" lines that the run never printed. The
note says these come only from GEVGDriver::CreateSplines, which gevgen's flux mode never reaches. It proposes rules
P1-P5 based on what that path does log, plus a change that keeps the coverage log on a failed run (§4).

Files:
- genie-R-3_04_00/: GENIE R-3_04_00 sources (GEVGDriver.cxx, GMCJDriver.cxx, gEvGen.cxx, AppInit.cxx, Messenger.cxx,
  Messenger.h, XSecSplineList.cxx, Interaction.cxx, InitialState.cxx, XmlParserUtils.cxx).
- lane/: pg_verify.py (the checks: coverage_problems, spline_codes, argv_pairs, messenger, MESSENGER_LINE),
  pg_replay.sh (the replay driver; its D5 trap delete_events), pg_generate.sh (the production driver), run_gevgen_v3.sh
  (gevgen's argv: gevgen_cmd and the coverage mode), Messenger_laconic.xml (the pinned messenger the coverage file is
  built from), and pg-replay-g2111a.stripped.py (the replay runner: DELETABLE, leftovers, deleted_problems; its
  embedded archive is removed).
- evidence/: the failed run's receipt and two read-only diagnostics.

The pinned GENIE build has asserts compiled out (evidence/b3-run4-diag2.out §2). The coverage run is one event with
gevgen's flux driver (-f file,hist,NOWIDTH), probe 14, targets 1000060120 and 1000010010, with GEVGDriver raised to
DEBUG and every other stream at the laconic levels.

Answer each question with a verdict (YES / NO / UNSURE), the file:line evidence, and a concrete scenario where one
applies:
Q1. Is each marker the note cites (§2 table, §3 P1-P5) emitted on THIS flux-mode path, at the priority stated, and on
    the GEVGDriver stream? Check the exact text the code produces, including spacing and how a multi-line LOG message
    reaches the log file (Messenger.h/.cxx's layout and prefix). Would P1's "Interaction   = X" line followed directly
    by "Cross Section *interpolated* = " actually appear as two consecutive lines? Is X in the same format as
    spline_codes returns? Is the messenger applied before these calls (gEvGen.cxx Initialize vs Configure)?
Q2. Fail open: can P1-P5 all pass while a spline the run needs is missing from the loaded spline file, or while
    cross sections are integrated rather than interpolated? Consider: a driver whose UseSplines fails; XSecSum calls
    made outside CreateXSecSumSpline; an interaction list that differs between UseSplines and XSecSum; SplineExists
    keying (algorithm + config + interaction); log interleaving; a misconfigured or ignored messenger; and anything
    else you find.
Q3. False STOP: can P1-P5 STOP a correct run? Consider: P4's exact count; other GEVGDriver DEBUG output; whether
    "Need xsec spline for" or "The spline wasn't loaded" could legitimately appear; XSecSum labels for every
    interaction; target and probe codes in X; log size.
Q4. Is §4's kept-log change safe and complete? Can a kept log be confused with a pass, leak anything the D5 deletion
    rule protects, or break the runner's leftovers() / deleted_problems() checks or pg_generate.sh's behaviour?
Q5. Anything else in the note that is wrong, unsupported by the sources, or missing.

End with one line: VERDICT: SOUND | SOUND WITH FIXES | UNSOUND, then a numbered list of the fixes you require.
Keep the report under 1500 words.
