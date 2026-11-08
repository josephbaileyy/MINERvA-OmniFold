Per-period 2D benchmark, CONNECT 2: the read. read rc 0: every control PASSED and the readings were written.
Run 2026-11-07T06:45Z on login01, at 0 node-h.

Bound by BINDING-1.md (PR #874), ruling 3. Code at M = a7af2e614f2d65ca10d169e6d73582e83f9ecf1d.
connect2.sh sha256 1e0f8efbdb74a71f4b3310ee4a56c92a1600735bef496d62ab7aed620ad1a881; the director gave GO.
It ran after connect 1's PASS (PR #878).
The deploy archive sha256 is bb1e00e4ed9c8ef27b9681a9daf47078b9d89d5559937104f778afd5c06c716e, the same as connect 1's.

The steps, each with its own rc (remote2.out):
1. The pins are equal (pins.check).
2. Fence: 0 rows (squeue_before_copy.txt).
3. copy: rc 0. These are O_NOATIME copies of the 39 operands (copies.json).
4. verify: rc 0. All 39 sha256 equal INPUTS.sha256, and both the declared and the measured value are recorded
   (verify.json).
5. Fence: 0 rows (squeue_before_read.txt).
6. read: rc 0, and readout.json has verdict READ.

The controls, with their compared values in readout.json "controls":
C-PARTC, C-IN-cells, C-PUB (465.4152721 against 465.4152721915, rel 1.6e-10), C-SUM (rel 6.5e-9), C-K (k = 73,
0.66185), C-M (6/6 modes), C-CTRL (7.46e-12 cells), C-STEP (rel 0), C-GRAD (rel 0) and C-COMB (-0.076%).
Every one is PASS.

readout.json sha256 4872df322a4e2e49ef009c4fa7eb78f273b8bea75a8a97855fd57451d229dca1. Its readings are interpreted
only in the outcome record, under DECLARATION.md section 5.

CITABLE FOR: the controls and the readings exactly as written in readout.json.
NOT CITABLE FOR: any interpretation beyond DECLARATION.md section 5's licences. That interpretation is the outcome
record's job.

The 39 copies are kept in /pscratch/sd/j/josephrb/per-period-benchmark-20261106/read/copies until the outcome record
is merged. After that they are deleted under a ledger row (the director's ruling of 2026-11-07).
