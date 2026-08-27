reviewer role     : agy-publication-redteam
conversation uuid : 440f42ef-c271-4f77-a410-a4a999166f44
export PATH=/global/u2/j/josephrb/.conda/envs/root_6_28/bin:$PATH
export TMPDIR=/tmp/readiness-successor-20260827
`command -v python3` -> /global/u2/j/josephrb/.conda/envs/root_6_28/bin/python3
`python3 -V` -> Python 3.11.14

### SELF-DISCLOSURE
I previously graded the `generate_manifest.py` discriminating DIRTY-warning delivery as FIT. That was a strictly bounded and separate subtask concerning manifest dirtiness logic. Grading that specific manifest output formatting does not construct, design, or dictate the implementation of the three mechanisms evaluated here (the F-7(b) import ratchet, F-17(b) M1/M6 comparators, or the F-8(b) NO-ZERO receipt checkers). I remain an independent reviewer because I acted only as a third-party evaluator of a discrete prior delivery; I am neither the builder nor the remedy-spec author of any of these orchestration guards. My independence is not compromised.


### VERBATIM QUOTES FROM DECISION RECORD
From `docs/orchestration/DECISION-20260825-joseph-gate2-fail-and-four-rulings.md` at `9f088f9a`:

#### 10.1 A SEPARATE READINESS CHECK gates step 4 (Joseph, 2026-08-25)

Completing and grading any prospective mechanism — including the `verify_receipt_artifacts.py`
repair — **authorizes only that mechanism**. It is not a step toward permission and it accumulates
no credit.

**Do not start a rehearsal, file Gate-2 evidence, or launch compute without a separate readiness
check confirming that ALL prospective F-7(b), F-8(b) and F-17(b) mechanisms are present AND
independently graded.**

Stated as a gate rather than a habit because the failure it prevents is the one this campaign
already made: a sequence of individually-authorized steps read, at the end, as authorization for the
thing none of them authorized. The readiness check is a distinct act with its own evidence. A lane
that has just finished the last mechanism is not thereby cleared to proceed, and "all three are
done" asserted by the lane that built them is not the check.

#### 10.3 §10.1 ran and returned NOT READY; the block is answered by a redesign (2026-08-26)

The readiness check §10.1 creates was run by `agy-g2-gate-verifier` (conversation
`dc93a0f8-6863-48c8-9b7b-76f22f6deae2`) and returned **`READINESS-10-1: NOT READY`**, preserved
verbatim at `docs/orchestration/runs/agy-g2-gate-verifier/20260826-readiness-10-1-VERDICT.md`,
sha256 `67bee6f2dd710659d1442780c99792ef5c6d4dc0e33dca00b76104c16c87099e`, 8136 B. All three
mechanisms were present and independently graded; the block was the F-8(b) prefilter's `rc=0`
semantics, ruled a **fail-open gate**.

The redesign that answers it — a linter with **no passing exit status**, plus a fail-closed
independent-attestation validator that is the actual gate — is recorded at
`docs/orchestration/state/DESIGN-20260826-f8b-no-green-linter-and-attestation-gate.md`. That record
also carries two measured corrections: the recorded BREAK-1 `rc=0` **does not reproduce**, and the
readiness verdict recorded a tip (`3ae65695`) at which the instrument it graded **does not exist**.
Neither correction changes the direction of the block.

**§10.1 must be re-run on the successor tip.** A NOT READY that has been answered is not thereby
READY, and this lane built the mechanisms, so it is not the check. **Gate 2 remains FAIL.**


### F-7(b) MECHANISM: `nd-unfolding/mnv_import_set_ratchet.py`
1. **Blob at `9f088f9a`**: Using `git ls-tree -r 9f088f9a`, the blob id for `nd-unfolding/mnv_import_set_ratchet.py` is exactly `c1e745eb9e494ae7d9070515a323da5c953f224c`.
2. **Blob at prior readiness tip (`5cb9dfb9`)**: Using `git ls-tree -r 5cb9dfb99c7667e4fc6f3cb2fa929736d123097a`, the blob id is also `c1e745eb9e494ae7d9070515a323da5c953f224c`. The blob is UNCHANGED.
3. **Independent Grade**: The readiness verdict `20260826-readiness-10-1-VERDICT.md` claims it was "INDEPENDENTLY GRADED FIT by agy-g2-gate-verifier". However, using `git grep c1e745eb docs/orchestration/runs/agy-g2-gate-verifier`, I find that **no tracked verdict artifact** at `9f088f9a` from that grader contains this blob SHA. A claim with no receipt mapping is not a grade. There is no tracked verdict artifact establishing an independent grade of that exact blob `c1e745eb9e494ae7d9070515a323da5c953f224c`.
* Missing requirement: No mapped receipt proving the blob was graded.


### F-17(b) MECHANISM: `docs/orchestration/compare_m1_m6.py` and `docs/orchestration/measure_m1_m6.py`
1. **Blobs at `9f088f9a`**: Using `git ls-tree -r 9f088f9a`, the blob ids are exactly:
   - `compare_m1_m6.py`: `7ca17299739e208f8fe4b87b44dfba0c296b575e`
   - `measure_m1_m6.py`: `9d52f06ea793ec7b1f4e25052016f526474f269d`
2. **Blobs at prior readiness tip (`5cb9dfb9`)**: Using `git ls-tree -r 5cb9dfb9`, the blob ids are identical (`7ca17299...` and `9d52f06e...`). The blobs are UNCHANGED.
3. **Independent Grade**: The readiness verdict `20260826-readiness-10-1-VERDICT.md` broadly claims "INDEPENDENTLY GRADED (previously graded FIT)". However, searching tracked files in `docs/orchestration/runs` and `docs/orchestration/state` for those two exact SHAs reveals **no tracked verdict artifact** (other than the readiness checks themselves) that maps these blobs to an independent grade. As established, "previously graded FIT" without an exact mapped receipt of those blobs is NOT READY.
* Missing requirement: No mapped receipt proving the blobs were independently graded.

(Note: The F-17 pre-submission half is measured AT SUBMISSION TIME, which is a fact about discharge and cannot be substituted for the prospective mechanism's existence and independent grade.)


### F-8(b) MECHANISM: `docs/orchestration/verify_run_receipt_blind_spots.py` and `docs/orchestration/verify_f8b_attestation.py`
1. **Blobs at `9f088f9a`**: Using `git ls-tree -r 9f088f9a`, the blob ids are exactly:
   - `verify_run_receipt_blind_spots.py`: `4ca2dbe3a91b0c8049ced0e58885f2ee3b458e7e`
   - `verify_f8b_attestation.py`: `0b8baec5b15f0b5aa90b52c4b9713bc0b8aabdf9`
2. **Independent Grade**:
   - Grader role: `agy-f8b-final-tip`
   - Conversation UUID: `7a312e96-cc1b-46c7-866e-952939d68f28`
   - Artifact path at tip: `docs/orchestration/runs/agy-f8b-final-tip/20260827-f8b-final-tip-VERDICT.md`
   - Recomputed artifact digest (SHA256): `73b295c832564252040d655f6a48c4256d24e9542b43edcbea13cb3d72cac4f7`
   - Verdict: `F8B-FINAL-TIP: FIT`
   - Graded SHA: `5b1f989c2957cb6a6f73aa091db6f8be3b7a7c5f`
3. **Blob Identity Proof**: Using `git ls-tree -r 5b1f989c`, the exact blob ids for these two files are identical to those at `9f088f9a` (`4ca2dbe3...` and `0b8baec5...`). The mechanisms are proven identical between the graded tip and the successor tip.
4. **Test Suite Counts**:
   - `python3 -m unittest discover -s docs/orchestration -p 'test_verify_run_receipt_blind_spots.py'` -> `Ran 18 tests`
   - `python3 -m unittest discover -s docs/orchestration -p 'test_verify_f8b_attestation.py'` -> `Ran 70 tests`
   - Total F-8(b) suite count is exactly 88. I also explicitly ran `test_verify_receipt_artifacts.py` which returned `Ran 15 tests`, conclusively proving the 103 figure was an over-globbed error including that unrelated file.


### TERMINAL VERDICT

* F-7(b)  present, blob-mapped to an independent grade?   NO (Present, but no tracked receipt maps the blob)
* F-8(b)  present, blob-mapped to an independent grade?   YES
* F-17(b) present, blob-mapped to an independent grade?   NO (Present, but no tracked receipt maps the blobs)
* every command in this brief actually run?               YES

READINESS-10-1-SUCCESSOR: NOT READY

REACHABILITY: I completed environment setup in a detached clean worktree, self-disclosure, quote extraction, F-7(b) check (missing receipt map found), F-17(b) check (missing receipt map found), and F-8(b) check (full verification, blob identity, and explicit test counts run). I ran every requested command. No items were unreached.

## CORRECTION AFTER COVERING SEARCH

### ITEM 1: F-7(b) RE-EXAMINED
- **From `RECEIPT-20260826-stack-grade-and-landing.json` at `9f088f9a`**:
  - `overall_verdict`: verdict "FIT", grader_role "agy-g2-gate-verifier", conversation_uuid "dc93a0f8-6863-48c8-9b7b-76f22f6deae2".
  - `ruled_on_shas`: `[ "3ae656951734bc90371bd64c56ccc4ce970b1470", "1aa055d9cd40964cff3b3d0d63ea616d26d5f515", "57508b319a184cd968b191448aeaafb1bd8ed4b7", "d0decbd35b0c4986dc31286a221220d3a29555d1" ]`
  - `attested_shas_P1_to_P5.P1_pin_gate`: `"57508b319a184cd968b191448aeaafb1bd8ed4b7"`
  - `work_packages`: Graded instrument commits are listed under "closeout grade and delegated Gate-2 re-evaluation" shas `["b8dc7814", "327bc105"]` and others.
- **Blob comparison**: The git blob id of `nd-unfolding/mnv_import_set_ratchet.py` at `57508b319a184cd968b191448aeaafb1bd8ed4b7` is `c1e745eb9e494ae7d9070515a323da5c953f224c`. This is EXACTLY identical to the blob at the successor tip `9f088f9a`.
- **Conclusion for F-7(b)**: My first NO was **WRONG**. My instrument missed it because I performed a simple string search (`git grep`) for the *blob id* directly against the text of the verdict artifacts, whereas the graders correctly pin and cite *commit SHAs* (like `57508b319a18...`) and file content digests. The receipt maps the P1 pin gate explicitly to `57508b31...` which maps exactly to the current blob. Items 1-3 are SATISFIED for F-7(b).

### ITEM 2: F-17(b) RE-EXAMINED
I examined all three grade artifacts at `9f088f9a`:

1. `docs/orchestration/GRADE-20260825-selector-narrowing-fitness.md`
   - Recomputed content digest: `ff2738383c006a22aa7db29dbaed7661f52d660f8a664d2c33ea3ff5197d3930`
   - Graded SHA: `63262a3a`
   - Pin: Content sha256 `5dc92487` for `compare_m1_m6.py` (which MATCHES the content digest at `9f088f9a`).
   - Identity: Grader role and UUID are ABSENT.
   - Scope: Fitness of `compare_m1_m6.py` against the "selector syntax narrows" spec.

2. `docs/orchestration/GRADE-20260825-d3-comparator-repair-fitness.md`
   - Recomputed content digest: `6ecb39afa13ab4a0df9bc522fa62488a0f93dfe7401e1996417c9c94c0f0920c`
   - Graded SHA: `c8a29082`
   - Pin: Content sha256 `68b4af12` for `compare_m1_m6.py`.
   - Identity: Grader role and UUID are ABSENT.
   - Scope: Fitness of `compare_m1_m6.py` against defect D-3. Explicitly states "The correctness of `measure_m1_m6.py`... is NOT CITABLE FOR".

3. `docs/orchestration/GRADE-20260825-f17b-comparison-instrument-fitness.md`
   - Recomputed content digest: `aa1b6eeec464dcd4495071b6f39fc715e267b097aa39ff8f22c5daa4d6c72fea`
   - Graded SHA: `2790ba904ae31bebd3f96d9a77cf95d0d8698e2e`
   - Pin: Content sha256 `422ed9e7eaf16af6b6f110e480e0c7843c9612f3eb20ba08be60919a020bf430` for `compare_m1_m6.py`.
   - Identity: Grader role and UUID are ABSENT.
   - Scope: Explicitly limits the grade to `compare_m1_m6.py`, stating verbatim for the other required half: `docs/orchestration/measure_m1_m6.py (input instrument, not graded)`.

- **Conclusion for F-17(b)**: The mechanism `compare_m1_m6.py` is mapped to an independent grade via content digest `5dc92487`. However, the required component `measure_m1_m6.py` is EXPLICITLY UNGRADED by the very artifact that evaluates the instrument, stating exactly "input instrument, not graded". Thus, the complete F-17(b) mechanism (which is the pair) lacks a covering independent grade. Furthermore, the three F-17(b) grade artifacts violate the identity requirement as they lack both a grader role and a conversation UUID.


### ITEM 3: COMPONENT MAPPINGS AND DIGESTS
- **F-7(b) Mechanism (`nd-unfolding/mnv_import_set_ratchet.py`)**:
  - Artifact Path: `docs/orchestration/state/RECEIPT-20260826-stack-grade-and-landing.json`
  - Graded SHA: `57508b319a184cd968b191448aeaafb1bd8ed4b7`
  - Mapping: Pinned by commit SHA. The blob ID `c1e745eb9e494ae7d9070515a323da5c953f224c` at that graded SHA perfectly matches the current blob ID at `9f088f9a`.

- **F-8(b) Mechanism (`verify_run_receipt_blind_spots.py`, `verify_f8b_attestation.py`)**:
  - Artifact Path: `docs/orchestration/runs/agy-f8b-final-tip/20260827-f8b-final-tip-VERDICT.md`
  - Graded SHA: `5b1f989c2957cb6a6f73aa091db6f8be3b7a7c5f`
  - Mapping: The blob IDs `4ca2dbe3a91b0c8049ced0e58885f2ee3b458e7e` and `0b8baec5b15f0b5aa90b52c4b9713bc0b8aabdf9` at that graded SHA perfectly match the current blob IDs at `9f088f9a`.

- **F-17(b) Mechanism (`compare_m1_m6.py`, `measure_m1_m6.py`)**:
  - Artifact Paths:
    - `docs/orchestration/GRADE-20260825-selector-narrowing-fitness.md`
    - `docs/orchestration/GRADE-20260825-d3-comparator-repair-fitness.md`
    - `docs/orchestration/GRADE-20260825-f17b-comparison-instrument-fitness.md`
  - Graded SHAs: `63262a3a`, `c8a29082`, `2790ba904ae31bebd3f96d9a77cf95d0d8698e2e` respectively.
  - Mapping: `compare_m1_m6.py` maps to `GRADE-20260825-selector-narrowing-fitness.md` via its current content digest `5dc92487bd5c2f6a82d2d4ba51ccd57fa73abeac6eb836ab0343e95206595301`. However, `measure_m1_m6.py` is entirely unmapped because `GRADE-20260825-f17b-comparison-instrument-fitness.md` explicitly designates it as "input instrument, not graded".


### CORRECTED TALLY AND VERDICT
* F-7(b)  present, blob-mapped to an independent grade?   YES
* F-8(b)  present, blob-mapped to an independent grade?   YES
* F-17(b) present, blob-mapped to an independent grade?   NO (The `measure_m1_m6.py` component is explicitly declared ungraded in its F-17(b) grader artifact, and all three grader artifacts lack an identity/UUID header)

READINESS-10-1-SUCCESSOR-CORRECTED: NOT READY

REACHABILITY (CORRECTION): I successfully re-read the receipt for F-7(b) and mapped the PIN commit SHA to the unchanged tip blob. I examined all three F-17(b) `GRADE` artifacts, recomputed their content digests, searched for absent identity headers, and extracted their explicit scoping statements (verifying the un-graded status of the input instrument). I successfully mapped all components, providing content hashes and exact SHAs, and issued the corrected final verdict.
