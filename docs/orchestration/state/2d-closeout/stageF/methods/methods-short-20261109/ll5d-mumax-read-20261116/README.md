# LL5D: the meaning read of D2's mu_max sentence (2026-11-16)

**What it read:** `read-text.txt`, §6.3's new two sentences on prep/ll5d-fill-20261115 (uncommitted, on f3d70998a).
D2 (DECISION-20261112-joseph-consult-d1-d7.md item 2) asks for a bounded quantification of the two GEANT4 bands' effect
in LL5D's own space, presented as an unresolved implementation property. The sentences go to Joseph's batch with the
rest of the branch.

It read them against:
- fd/receipts-ll5d/mumax/README.md: G is the two bands' block, M = C_T (all), mu_max is the largest generalized
  eigenvalue of (G, M), and chi2(M - G)/chi2(M) lies in [1, 1/(1 - mu_max)];
- fd/receipts-ll5d/mumax/run/node/mumax.json (`422db056…`), key "primary C_T (all)" per truth;
- make_values_fived16.py's mumax_values;
- paper §6.2-6.3 in context.

The reader was an independent general-purpose subagent, read-only.

**Verdict: PASS.**
- **The numbers:** 1/(1 - mu_max) is 1.0700193 at G18 and 1.0942260 at AR23. Both are rounded up to 1.071 and 1.095,
  and mumax_values asserts that each printed value is not below the exact one. Rounding to nearest (1.070, 1.094)
  would have made "at most" false.
- **The direction and the matrix:** removing G never lowers a chi-square, so "raises ... by at most" is correct. "Any"
  holds for every fixed residual vector: M has 16 positive eigenvalues, G has rank 2 and mu_max < 1. "The covariance
  graded with them" is C_T (all). The removal control gives C_T (minus2) = C_T (all) - G to 7.5e-96.
- **No overreach:** the second sentence excludes the pseudo-data draws and keeps the separation unclassified. Nothing
  says the block explains, or cannot explain, the joint result.
- **The referents** agree with §6.2.

**Adopted (optional):** "any chi-square" could be read as any of the test's chi-squares, but the two variants also
differ in their pseudo-data. The first sentence now says "the chi-square of any fixed set of residuals". "The block's
largest eigenvalue relative to that covariance" is replaced by the exact gloss: "the largest fraction of that
covariance, in any direction, that the block carries".

**Before the read, from the drafting:** an earlier draft said "far less than this excess, so that block cannot account
for it". It was removed because mu_max bounds removing the block, not scaling it up. The printed precision also went
from 2 to 3 decimals: rounding up at 2 decimals gave 1.08, which is true but loose.
