r19 second agy pass, over the b1 review fixes and the note additions N1-N4 (BEFORE = the step-0 paper; AFTER = ac1508ec's paper or note text, from pdftotext).

- agy-control.txt (pairs-control.txt; plant in Q6, N1: "We have not compared their power ..." -> "Their power exceeds that of a reconstruction-level test."): CAUGHT.
- agy-real.txt: Q1 and Q8 SAME. The DIFFERS verdicts:
  - Q4: "Its covariance" has an unclear antecedent. Fixed: "The result's covariance" (apply_b1n_fixes.py).
  - Q2: "target 3 difference" is a pdftotext page-number artifact. The rescoping to "the comparison of Sec. V A" is the first review's B1 fix, and the tests' "as run" fact prints in the note (ledger K3).
  - Q3: "these are the joint cells" is a definition, matching the paper's later uses of "joint cells". "The generator tests use" left with the tests.
  - Q5: the Table I clause left with Table I. The prompt's context block did not name it.
  - Q6: N1 omits the paper's clause "which is what makes the two-dimensional result reusable ...". That clause stays in the paper: b3 moves the first half of the former VI lead to V B (T4). b3 must keep it.
  - Q7 and Q9: AFTER included neighbouring note text that BEFORE lacks (the definition of the rate, and the q3 behaviour). These are artefacts of how the pairs were built. N2's sentence is identical to the paper's, and N4's qualifier is supported by DIAGNOSIS-20260926-s5e-oi192-estimator.md:115, :137, :140.
