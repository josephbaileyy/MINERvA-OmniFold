# RECONCILIATION — one indexed summary of the split round

AUTHORSHIP: assembled by claude-school-main, which AUTHORED the three commits under grade. This file
is an INDEX over other parties' sub-verdicts. It is NOT a verdict and it declares no FIT. No grader
declared an overall FIT for the stack; that declaration is a decision, not a measurement.

STACK: 1aa055d9 (merge candidate) <- 57508b31 (F-7(b) pin gate) <- d0decbd3 (OI-136 successor probe)
BASE : 3ae656951734bc90371bd64c56ccc4ce970b1470

| item | outcome | grader | conversation | tested sha | reached |
|---|---|---|---|---|---|
| P1 pin gate | 3 arms reproduced: rc=2 absent, rc=3 EXCLUSION MOVED, real digest passes | agy-g2-gate-verifier | dc93a0f8 | pin (57508b31) — NOT grader-attested | YES |
| P2 successor probe | "Diff to 2026-08-20 parent lines: 0"; only POSITIVE_CONTROLS differs | agy-g2-gate-verifier | dc93a0f8 | probe — NOT grader-attested | YES |
| P3 constants | probe rc=0; 45 FAIL-OPEN; both controls IN set; negative rejected 21 | agy-g2-gate-verifier | dc93a0f8 | probe — NOT grader-attested | YES |
| P4 checks | MANIFEST rows=551, overrides=101; ALL BINDINGS INTACT (133 OK) | agy-g2-gate-verifier | dc93a0f8 | probe — NOT grader-attested | YES |
| P5 conflicts | all 7 mnv_guarded_run functions present AND _emit_inventory shown CALLED | agy-g2-gate-verifier | dc93a0f8 | merge — NOT grader-attested | YES |
| P6 delisting | base 52/52 STALE 0 NEW 0; merge 46/46 STALE 0 NEW 0; the six leg sites named | agy-capacity-probe | dc2b899d | 3ae65695… and 1aa055d9… ATTESTED | YES |
| P7 overrides | base 98L/97R/97 distinct; merge 102L/101R/101 distinct → NO duplicate path remains | agy-capacity-probe | dc2b899d | 3ae65695… and 1aa055d9… ATTESTED | YES |
| P8 arms | base 1646/8F/18E · merge 1813/12F/18E · pin 1813/12F/18E · probe 1813/8F/18E | agy-g2-gate-verifier | dc93a0f8 | probe d0decbd35b0c4986dc31286a221220d3a29555d1 ATTESTED | YES |
| P9 four files | all four deltas match claims; nothing capital-flagged | agy-publication-redteam | 440f42ef | 3ae65695… and d0decbd35b0c… ATTESTED | YES |

## THE DECIDING MEASUREMENT (P8)
probe = 1813 tests, 8 failures, 18 errors, 11 skipped, in 603.258s.
  BASE minus PROBE : EMPTY
  PROBE minus BASE : EMPTY
The failure-name sets are IDENTICAL to base. 12F -> 8F confirmed: the four OI-136 arms are green and
NO new failure appeared anywhere in 1813 tests.

## TWO CORRECTIONS AGAINST THE AUTHOR (me), FOUND BY THE ANCHORING GRADER
P6: my brief said "STALE 6 at base", which is garbled. STALE 6 described the merged tree BEFORE the
delisting commit — a state neither graded tree exhibits, because 1aa055d9 already contains the fix.
The grader's "REFUTED" is correct about my PHRASING. Substance confirmed: 52 -> 46, NEW = 0 both trees.
P7: my "104 -> 101 BODY ROWS" was a real measurement OF THE DEDUPE OPERATION on the in-conflict file,
reported where it reads as a base->merge delta. Base -> merge is 97 -> 101, an INCREASE. The grader is
right that no unit reconciles them as stated.

## OPEN CAVEATS
1. P1–P5 carry NO grader-attested tested sha; VERDICT.md recorded none. ANCHORING.md supplies
   provenance but was written by the AUTHOR, so it is not grader attestation.
2. No grader declared an overall FIT.
3. test_g2_guards_collected fails at base too (root_6_28 has no pytest): PRE-EXISTING, not a regression.
