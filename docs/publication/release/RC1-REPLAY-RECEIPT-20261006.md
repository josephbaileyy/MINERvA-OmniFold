# RC1 independent empty-directory replay (2026-10-06)

**Package:** `minerva-omnifold-joint-tests-rc1.tar.gz`. It is local only: not deposited, tagged or sent.

| version | tarball sha256 | change |
|---|---|---|
| tested | `b56aae87ba5724e4155cbafd19840008e6694a91cd5e0cf524baf57de5bebc97` | — |
| current | `7f4cb7864bc9b1aedfe95f4f16863dd893c1e7215179fb413910e1429c1d35c2` | README only |

The checksums are in `RC1-SHA256SUMS.txt`. The source README is `RC1-README.md`.

## Independent replay

**Who:** a fresh Opus 5.5 agent acting as an outside reader. It had no repository access and used only the
tarball and its README.

**Environment:** macOS, Python 3.12.2 (conda-forge), numpy 1.26.4, scipy 1.15.2.

**Result: REPLAY PASS WITH DEFECTS.**
- The tarball sha256 matched, and all 12 entries of `SHA256SUMS` checked OK.
- `verify_rc.py` gave `VERIFY: PASS` in about 2 min 11 s.
- Each individual step returned rc 0. Both replays gave `COMPARE: AGREE (0 differences)`.
- The W1 output agrees with the committed result on all 475 numeric and boolean leaves, to within 1e-12. Only
  labels and paths differ.

**Its own spot-checks:**
- T_total_obs for all 5 nulls, computed as r'W⁻¹r on the domain, matches to within 1e-14;
- the k recount for variant 0.0 matches for all 5 nulls;
- the null medians match to about 1e-15 once the seeded prediction-MC draw is included;
- the README's counts check out: 277 = 211 + 66, 40 W1 claims, and 10 rejections in both files.

**Defects and their fixes (README only, in the current tarball):**

| severity | defect | fix |
|---|---|---|
| SHOULD-FIX | The W1 individual step had no comparison instruction | Added how to compare (claims and criteria must be equal; labels and paths are expected to differ) |
| SHOULD-FIX | The individual steps wrote into the package tree | The steps now write to `mktemp -d`. Verified: after running them on a fresh extraction, 0 checksum mismatches. |
| NOTE | Runtime | Added: about 2–3 min |
| NOTE | Absolute `/pscratch` paths | Stated as provenance only |
| NOTE | `jitters` | Its role is stated (`observed_jitter_p`, not recomputed) |
| NOTE | Claims not verifiable from the package (conditions, DOI, source branch) | Accepted: these are statements whose authority is the cited records |

**Re-verification after the fixes** (by this lane):
- `verify_rc.py` gives PASS;
- the corrected individual steps, run from a fresh extraction, give AGREE, AGREE and 10/10 `false`, with 0 checksum
  mismatches afterwards.

A second independent replay was not run, because the change was confined to the README's instructions and notes.
