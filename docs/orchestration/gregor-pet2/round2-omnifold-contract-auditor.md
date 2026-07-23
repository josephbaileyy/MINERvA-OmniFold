Continue as the same durable `omnifold_contract_auditor`. This is ROUND 2, a
focused adversarial ruling before code review. Do not edit files and do not
start any provider delegate, subagent, or one-shot external process.

Review the implementation lead's Round-1 design report in
`docs/orchestration/runs/pet2_implementation_lead/` and resolve these concrete
questions against source:

1. Gate-2 telemetry unit issue: `dump_pointcloud_inputs.py` declares scalar
   `(pt,ppar,eavail,q3)` branches in GeV; the domain validator enforces
   `mu_reco_px,py,pz` in MeV divided by 1000 equals the scalar coordinates;
   yet `gate2_target_runtime.py` lines near 421-422 divides
   `measured_scalars` and `bkg_reco_scalars` by 1000 before histogramming
   against GeV edges. Is that division a verified bug, merely a comment/unit
   mismatch, or unable to decide? State whether it affects target construction,
   only independent telemetry, or physics weights. Give exact source evidence
   and the minimal remediation/test if warranted.
2. Ratify or correct the proposed separate Step-1 `w_reco` and Step-2
   `w_truth` formulae, class-mass calibration, treatment of native misses,
   fakes, and the one-million-normalized Gate-2 target.
3. Decide whether deterministic row indices plus the existing three-inventory
   identity/order hashes are enough for an experimental recoil/synthetic pilot
   when physical event keys are absent; distinguish pilot from publication
   requirements.
4. Give a precise allow/defer/block matrix for fields that already exist in
   G2 (`reco cloud E/pos/z`, view, time, seven muon fields, vertex, four reco
   scalars) and Gregor-only fields (photon/blob/prong type, dE/dx, PID,
   Michel/pion summaries, overflow aggregate).
5. Audit the proposed arm definitions: C generic baseline footing; D typed
   tokens only when real reco types exist; E richer audited globals; F strict
   unavailable. Identify any confounding that must be encoded as a separate
   ablation.

End with explicit MUST-FIX-BEFORE-CODE-ACCEPTANCE and
MAY-DEFER-UNTIL-G2 lists. Do not infer a scientific winner.
