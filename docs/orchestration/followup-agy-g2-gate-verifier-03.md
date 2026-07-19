You are the preserved independent G2 gate verifier. Perform a read-only,
publication-grade audit of the isolated task-4 failure; do not edit files,
dispatch jobs, inspect other task logs/artifacts, or replace any role.

Evidence:
- Array 56106974 task 4 maps to playlist 1D and failed 1:0 after its event loop.
- Final 1D ROOT and receipt are both absent.
- Preserved work ROOT:
  nd-unfolding/g2_fullevent/work/1D/runEventLoopOmniFold.root
  (14,150,286,041 bytes).
- Preserved validator JSON:
  nd-unfolding/g2_fullevent/work/1D/g2_validation_1D.json
- Exactly one of 50 checks failed: bkg_reco_muon_valid was 19999/20000.
- The exact row is mc_background entry 16074, identity
  (mc_run,mc_subrun,mc_nthEvtInFile)=(111114,296,375), with
  mu_reco_E=31373686868.197517, px=-2349993841.390295,
  py=-1800462284.564315, pz=31233701224.974899, minos_ok=1.
- The committed launcher safely quarantines work-only partials when both final
  paths are absent, but unchanged rerun is deterministic and would fail again.
- The validator samples only the first 20,000 background/data rows.

Inspect only the committed launcher, validator/source code relevant to this
row, and the failed 1D evidence named above. Answer:
1. Is an unchanged failed-task-only retry scientifically justified? (Expected
   no unless you find nondeterminism.)
2. Is this most likely upstream corrupt input, unit/conversion overflow, or a
   selection/dump bug? State what evidence is still required.
3. What minimal fail-closed code/validator remedy is publication-grade?
4. Does that remedy invalidate already published playlist receipts, require
   full validation of existing ROOTs, or require rerunning their event loops?
5. Give explicit PASS/BLOCK conditions for retrying only task 4.

Preserve your UUID and return a concise verdict with no scientific PASS beyond
the evidence.
