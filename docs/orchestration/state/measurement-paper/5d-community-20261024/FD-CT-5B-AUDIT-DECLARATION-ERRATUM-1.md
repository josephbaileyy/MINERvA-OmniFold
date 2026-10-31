# ERRATUM 1 to FD-CT-5B-AUDIT-DECLARATION.md: §9's mutant count (2026-10-30)

**By** the measurement session `coverage-5b-audit`, at the director's request of 2026-10-30, which asked for the
correction to be made "beside the declaration, not inside it".

**Corrects** [`FD-CT-5B-AUDIT-DECLARATION.md`](FD-CT-5B-AUDIT-DECLARATION.md) (`65213f15a68010e5…`, bound by
[`FD-CT-5B-AUDIT-BINDING.md`](FD-CT-5B-AUDIT-BINDING.md)). The declaration is not edited, so its bound sha256 still
holds.

**The error.** §9, "Mutation receipt", reads: "Its 46 mutants cover every clause's threshold, comparison and operand
…".
- 46 is pass 1's count (`mutants_5b_audit-pass1.log`, 41 of 46 killed).
- The committed receipt is pass 2's, with **54 mutants**: `mutants_5b_audit.log` ends "killed 54 of 54; survived 0;
  not applied 0; file restored True".
- The declaration's own §13 states pass 2 correctly ("54 of 54 killed"), and the binding checked 54 of 54.

**The corrected sentence:** "Its 54 mutants (pass 2) cover every clause's threshold, comparison and operand, the
statistics behind the clauses, each refusing control, and the guard's table."

**What it changes:** nothing that was bound or run. The pinned mutants file (`0206b2d3…`) and the receipt are
unchanged, and so is the audit's verdict in [`FD-CT-5B-AUDIT-REPORT.md`](FD-CT-5B-AUDIT-REPORT.md) (§9 there noted the
discrepancy).
