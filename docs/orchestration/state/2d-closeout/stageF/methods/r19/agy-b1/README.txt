r19 b1: agy (gemini-3.8-flash-high via register-method/tools/run_x.sh) on the 11 changed printed units, BEFORE = the step-0 build (9df8f748), AFTER = b1 as first applied, before the review fixes. prompt.txt has the context block naming the facts that moved to the note.

- agy-real.txt: 9 SAME. Q2 DIFFERS: the new roadmap's section descriptions (structural) and K11's "already disfavours" fact, which prints in the note (r19/ledger.md K11). Q6 DIFFERS: the ambiguous "The joint cells form ... A coarse cell is reported", fixed by apply_b1_fixes.py S1.
- agy-control.txt and agy-control-r2.txt (pairs-control.txt): the plant "from the reproduction of" -> "from the independent validation against" in Q2. MISSED in both runs; the second run also gave SAME for the unplanted Q6.
- agy-control2.txt (pairs-control2.txt): the plant "not a calibrated bound" -> "a calibrated bound" in Q9. CAUGHT. The first attempt failed on a network error and left no answer; it was rerun.

Reading: agy catches a negation flip, but not a strengthening of a structural sentence (the roadmap). Its SAME verdicts on the structural units are not evidence. The independent review (ADOPT-AFTER-FIXES, 2 BLOCKING, 5 SHOULD-FIX, all addressed in apply_b1_fixes.py or recorded) covers them. The fixed passages and N1-N4 get a second agy pass and review.
