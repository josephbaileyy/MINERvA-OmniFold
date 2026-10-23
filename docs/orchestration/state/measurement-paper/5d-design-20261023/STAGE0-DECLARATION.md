# DECLARATION: 5D design Stage 0 — preserve its inputs now; hold its analysis (2026-10-23)

**By** the measurement session, at the director's request of 2026-10-23. The design is `DESIGN.md` in this directory, in
PR #284 (head `bc7cc629`). **Compute: 0 node-h.** Nothing here runs before the director's BINDING.

**CITABLE FOR:**
- what Stage 0 reads;
- the inventory of its inputs, with their sha256;
- the preservation step proposed for binding now;
- why the analysis is held.

**NOT CITABLE FOR:** any Stage 0 result, or any authorization beyond Part P.

## 1. The director's question: is Stage 0 a read of existing products only?

**Stages 0a and 0b: yes.** They run no unfold and no Slurm job. They read:
- the seven study-P data unfolds;
- the 140 s5e R assessment products;
- the 73 s5p R data products, base and bootstraps (`runs/s2/num/data`);
- the adopted (a) covariance `z-cv.npz` (sha256 `3d7465f6…`).

They then compute h^(−F), κ, coverage fractions and expected Δχ² locally (DESIGN §2.3, §8).

**Stage 0c: no.** It needs:
- one study-P data unfold at the re-derived D1;
- a 20-experiment R ensemble at the re-derived GiBUU truth;
- a local ratio rebuild.

That is about 0.64 CPU node-h (DESIGN §8). Only the 0c run is binding: the two-family run before it "decides nothing"
(DESIGN §2.3).

**Why the analysis is held.**
- Stage 0b's pass bar is W − 1.4%, where W is Joseph's T1 width (DESIGN §11 item 2: 8.6% if T1 is kept). The design
  says W is fixed "before Stage 0 runs, never after" (DESIGN §6).
- Stage 0a's κ, multiplied by h, gives the model-term size directly.
- So reading either one before §11 item 2 is answered would show Joseph the numbers W is meant to precede.
- The analysis (Part A) is therefore held until item 2 is answered, as the director asked: "Hold anything that needs
  those decisions."
- What needs no decision is protecting the inputs from the purge. That is Part P.

## 2. Part P: preserve the inputs on HPSS (proposed for binding now)

**Inventory.** [`stage0/INVENTORY.sha256`](stage0/INVENTORY.sha256) lists 425 files, 3,302,820,261 bytes, hashed on
2026-10-23 on login10:

| group | files | for |
|---|---:|---|
| `s5p-20260926/runs/s2/prior/prior_R5fix_{CV,prior_d0..d5}.npz` | 7 | study-P shifts (0a, 0b) |
| `s5e-20260925/runs/cand/assess/{eavail_gibuu,q3,W1,W2,W3,nominal}/*.npz` | 140 | R bias folds and nominal (0a, 0b) |
| `s5p-20260926/runs/s2/num/data/*.npz` | 73 | R data base and bootstraps, C_stat (0b) |
| `MINERvA-OmniFold/nd-unfolding/uq_5d/z_pilot_20260916_a5/z-cv.npz` | 1 | systematics approximation (0b) |
| `s5p-20260926/gen5d_fluxfix/**`, `gen5d/**`, `ratios/**` | 202 | the flux-repaired predictions and ratios for the D1 rebuild (0c) |
| `MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz` (`07fccc1a…`), `s5c-20260924/runs/p2/bkg_dump.npz` (`2addac8f…`) | 2 | the 0c unfolds |

All paths are under `/pscratch/sd/j/josephrb/`. The three hashes shown match their records (RUN.md of
`gpu-timing-20261023`; `DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md`).

**What runs.** [`stage0/stage0_preserve.sh`](stage0/stage0_preserve.sh) runs on a login node, with no Slurm job:

```bash
bash stage0_preserve.sh INVENTORY.sha256 /pscratch/sd/j/josephrb/5d-stage0-20261023 /home/j/josephrb/mnv-5d-stage0-inputs-20261023
```

It does the following, in order:
1. Re-verifies all 425 sha256. It stops if any input changed.
2. Writes one uncompressed tar of exactly those paths and checks that the tar has 425 members.
3. Copies the tar to HPSS with `hsi put`, then runs `hsi hashcreate` and `hsi hashverify`, the pattern earlier archives
   used. The inventory goes to HPSS alongside it.
4. Retrieves the tar from HPSS and compares sha256 byte for byte. It then deletes only the retrieved copy.

**Rule.**
- **PASS:** the retrieved copy's sha256 equals the tar's, and hashverify succeeds.
- **Anything else STOPS** and is reported. The script exits 3–8 and names the failing step in `preserve.log`.
- No inventoried file is modified or deleted.

**Cost and storage.**
- 0 node-h.
- About 3.3 GB on HPSS, which has 161 GiB free (`DECISION-20261023-joseph-r8-r9-and-5d-scoping.md:13`).
- About 3.3 GB more on pscratch for the tar, removable after PASS.
- Nothing is written to CFS.
- HPSS for durable copies is the R9 (a) route (`DECISION-20261023-joseph-r8-r9-and-5d-scoping.md`, item 2). Its use
  for these inputs is what this binding would authorize.

**Report.** `STAGE0-PRESERVE-REPORT.md` here: the tar sha256, `hsi ls -l`, the hashverify output and the retrieval
comparison.

## 3. Part A: the Stage 0 analysis (held; declared later)

- **When:** after Joseph answers DESIGN §11 item 2.
- **What it will contain:** its code with sha256, the family assignments (DESIGN §2.3), W, and the rules of DESIGN §8
  rows 0a and 0b.
- **Inputs:** read from pscratch if still present, otherwise from the HPSS tar.

**If the director prefers to run the analysis before item 2 is answered**, one option preserves the design's ordering:
- a sealed run, whose output only goes to a file, with its sha256 committed;
- the file is read only after W is fixed.
- That needs the analysis code written and declared first, which has not been done.

## 4. Unchanged

- MP-2 stays held.
- No claim, target or endpoint changes.
- Joseph's §11 decisions go to him through the director.
