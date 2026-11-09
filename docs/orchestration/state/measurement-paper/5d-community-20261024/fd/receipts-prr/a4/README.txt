FD-PRR addendum A4 receipts (FD-PRR-ADDENDUM-A4.md sections 6, 7 and 9). Run locally on the lane's machine, at
0 node-h, with no cluster contact. The one cluster session the trace cites (login30, 18:34:37Z) is recorded in
ls-slip.txt.

MADE AT: commit febf481f67467971a385b9792a9e9b8555f5c1fa (the A4 code commit), in a clean clone of it, which showed
0 porcelain lines before and after every run. The commit that adds this README changes only this directory's files
and the generated MANIFEST.tsv. Nothing under nd-unfolding changes, so the six FD-PRR files are the same at both
commits. Every run is one serial process, under nice -n 19, with every BLAS/OpenMP thread cap at 1. Each log's header
carries the clone's HEAD and the six files' sha256, which are the addendum's section 8 digests.

tests-serial.txt         every test class but JobScript (selected by the test loader): 116 collected, 101 run, OK,
                         rc 0. Among them are the REQUIRED test_the_run_path_end_to_end_with_every_path_protected and
                         the five other new Route2Run and Route2StageA4 tests.
tests-jobscript.txt      the JobScript class alone, run after the first had ended: 15 run, OK, rc 0 (unchanged by A4).
probe-earlier-mains.txt  old_main_probe.py: each prr_ibu.py's own main on A4's REQUIRED fixture, with every path
                         protected and the same substitutions as the REQUIRED test.
                         - M_A3 (06657cff, prr_ibu.py 17acad82...): rc 2, "a plain read of <tmp>/stage.json". This is
                           job 61043652's refusal.
                         - 0d6656be (the stage.json fix alone, 6388f9ef...): rc 2, "a plain read of
                           /pscratch/.../s5p-20260926/ratios/nullsF/rho-genie_cv-F.npz".
                         - this commit (fa913945...): rc 1, with C-IBU failing on synthetic rows; route2.json and
                           route2.npz written, and no refusal.
trace-run-path.txt       trace_run_path.py: the dynamic trace of the run path at this commit. It covers every open
                         and filesystem event inside REF-G1's guard, grouped by root and by its innermost repository
                         frame (file:line).
                         - Totals: 631 events; 0 reads the guard would refuse.
                         - Imports attempted inside the guard: 16 top-level names, with no ROOT.
                         - The fixture's hypothesis copies under $OUT/stage/hyp stand in for the repository's
                           nullsF json.
search-closure.txt       search_closure.py: the AST import closure of prr_probe.py, prr_ibu.py, prr_read.py and
                         s5p_nullexp.py, 32 modules, and their 8 lines carrying a /pscratch or /global literal. Each
                         is classified in the addendum's section 7. closure-modules.txt lists the 32.
search-json.txt          search_json.py, at ef9411a3:
                         - every absolute path in the 181 queue lines, all under $OUT;
                         - every committed json the runner names (15 resolved), with each absolute path value it
                           carries.
                         Which of those fields any runner code opens is in the addendum's section 7. Only rho_npz.path
                         is opened.
mutation.txt             prr_mutation.py: the unmutated suite at 116 tests, then 81 mutants, each killed by its named
                         test, the 10 new ones of section 6 among them.
ls-slip.txt              the lane's directory listing of s5p-20260926/ratios/nullsF on 2026-11-09, as the director
                         ruled it be recorded.
prr_stage_a4.sh.template the staging connect of section 5, with @M@, @A4_SHA@, @BIND_SHA@ and @SUMS@ filled after the
                         binding by make_stage_a4.py. Its sha256 goes to the director before it runs.
prr_move_attempt2.sh     the move of section 10.1, for the director's go after the binding.
old_main_probe.py, trace_run_path.py, search_closure.py, search_json.py, make_stage_a4.py, prr_ibu_at_06657cff.py,
prr_ibu_at_0d6656be.py   the scripts above, and the two earlier prr_ibu.py sources the probe ran (from git show).

CITABLE FOR: that the listed tests passed and the listed mutants were killed, on the listed files at the commit named
above; that the earlier mains refuse on the same fixture as stated; the trace's and the searches' outputs.
NOT CITABLE FOR: the cluster's own run of route 2, which attempt 3 meets first; anything about LightGBM, the real inputs
or a route-2 result; the staging step, which has not run.
