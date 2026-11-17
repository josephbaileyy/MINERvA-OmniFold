# #977 C-BKG-2: the analysis's own fiducial test, read from source, and the 1A template's composition with it (receipt)

**What ran.** One session on login27, 2026-11-12T05:50:09Z, under the director's go for exactly `code/mat_remote.sh`
(4819fb42…) and `code/mat_fetch.sh` (793a29f5…). 0 node-h.
- Fence clear: only ll5d_gate_G18 and ll5d_gate_AR23 running; no rpd_ job queued or running.
- Every file was read through O_NOATIME, whole and stat unchanged. Log: `session/fetch.out.txt`, ending MATBKG-977 OK.
- **Stated caveat (the director accepted it):** the source search used `os.walk`, so directories' atime may update
  under relatime. Purge is file-based, and no walked root is on `cov2d_protected_paths`. Files' atime did not move.

**The source** (`members/mat_source.json`, excerpts with line numbers):
- The event loop's `truth::Apothem` and `truth::ZRange` (runEventLoopOmniFold.cpp:1720-1721, `#include
  "PlotUtils/CCInclusiveSignal.h"` :62) are defined in `MINERvA101/MAT-MINERvA/calculators/CCInclusiveSignal.h`,
  sha256 cf9ee8c47a983070487db8f94bfa7c3b2831d52a25e66ee3e2ff972cbd9660ca:
  - Apothem :92-109, whose `checkConstraint` at :103-104 is `fabs(y) < fSlope*fabs(x) + 2*fApothem/sqrt(3)` and
    `fabs(x) < fApothem`, with `fSlope = -1/sqrt(3)` (:108);
  - ZRange :112-127, `z >= fMin && z <= fMax` (:122).
- The installed copies, `opt/include/PlotUtils/CCInclusiveSignal.h` and `opt/include/calculators/CCInclusiveSignal.h`,
  are byte-identical to it.
- `TargetUtils::IsInHexagon` (utilities/TargetUtils.cxx:34-46, sha256 64f47c7c…) is a different function, which
  `truth::Apothem` does not call. The transcriptions in probe_mad.py and intensity.py copy it faithfully, including
  its `yp*yp < lenOfSide/2.0` line.
- Revisions, read from `.git/HEAD` and refs through O_NOATIME, without running git:
  - MAT-MINERvA `main` = 50d7631416d1c93edd4db6886a2ca29da64fee60, equal to M4-W-RECORD.md:32's 50d76314;
  - MAT `main` = 35097b65ab1680db8058f9ede18fecffdc3a1ea3, equal to policy-config.json's mat_constructor git_sha.

**Port 1 against the source, line by line:** identical. `nd-unfolding/bkg_channel_split.py:58-70` is
`(z >= MINZ) & (z <= MAXZ)`, `abs(y) < _SLOPE*abs(x) + 2*APOTHEM/sqrt(3)` with `_SLOPE = -1/sqrt(3)`, and
`abs(x) < APOTHEM`. The same strict and non-strict comparisons, the same slope and the same constants (MINZ, MAXZ and
APOTHEM against runEventLoopOmniFold.cpp:1708). So the port-1 fraction is the measured value.

**Control (exact).** The producer's rule on base_cv (c76256a4) reproduces work_proxy's 1A__ana__B (42ce788b) with a
largest difference of 0.0 over 52,626 rows. The closure, genuine + out-of-phase-space = all, holds to 9×10⁻¹³.

**The 1A template's composition, with the analysis's own fiducial test** (`members/cbkg2_summary.json`; weighted by
w_bkg, over the 49,551 passing rows in the grid):

| class | weighted | raw |
|---|---|---|
| out-of-phase-space signal (ν_μ CC, truth vertex inside the fiducial volume) | **10.4 %** | 11.4 % (5,670) |
| genuine: ν_μ CC with the truth vertex outside the fiducial volume | 82.4 % | 80.8 % (40,036) |
| genuine: other flavor, wrong sign or NC | 7.2 % | 7.8 % (3,845) |

- **±1 mm sensitivity:** ν_μ CC rows whose class changes when the apothem and z limits move by ±1 mm number 1,333,
  2.5 % of the weight.
- The test's inequalities are those of the source, so this band is the sensitivity to the vertex position. It is not
  an ambiguity in the rule.
- It lies inside C-BKG's radius bracket of 9.6–32.0 %.

**Scope:** playlist 1A only, one of the twelve; base_cv exists for 1A only.
