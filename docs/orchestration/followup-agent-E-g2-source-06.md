Resume as the same G2 owner UUID. Implement an additive, publication-grade
recovery for the isolated playlist-1D validation failure. Preserve all running
array tasks and do not submit/retry/cancel jobs, publish ROOTs, consume reset
credits, or modify the canonical validator/binary/launcher currently hash-bound
by active job 56106974.

Confirmed evidence:
- Task 4 / playlist 1D loop completed; final ROOT+receipt are both absent.
- Work ROOT is nd-unfolding/g2_fullevent/work/1D/runEventLoopOmniFold.root.
- Validator failure: one background entry, index 16074, identity
  (111114,296,375), has a 31.37-billion-MeV reco four-vector.
- Direct upstream AnaTuple inspection at MasterAnaDev entry 109204 confirms the
  same native MasterAnaDev_muon_{E,P,Px,Py,Pz} and MINOS p/qp values. This is
  upstream corruption, not a G2 conversion/dump error.
- Output scalar pT=2,960,428 GeV and p_parallel=31,233,701 GeV, far outside the
  canonical extended PET domain pT<=30, p_parallel<=120 GeV. The downstream
  publication inventory must reject it before training.
- Existing validator samples only 20,000 background/data rows. Gemini verifier
  UUID dc93a0f8... returned BLOCK on unchanged retry and requires exhaustive
  scalar validation; it says event loops need not rerun if existing ROOTs pass.
- Active tasks have post-loop validator-hash drift guards. Therefore touching
  validate_g2_fullevent_smoke.py now could fail healthy running tasks.

Create ONLY new additive files (new validator/recovery helper/tests/receipt
schema as needed), leaving all hash-bound active files byte-identical. The new
validator must:
1. exhaustively validate scalar reco-domain membership/finite/sentinel handling
   for all relevant rows, not merely 20k;
2. fail closed on any corrupt row that could enter the canonical extended FPS
   domain;
3. census and bind out-of-domain corrupt rows by tree/index/event identity and
   values, proving downstream exclusion rather than silently accepting them;
4. preserve the existing 50 structural checks or explicitly compose their
   existing receipt;
5. support read-only supplemental validation of completed/future ROOTs without
   invalidating or overwriting original receipts;
6. offer a no-clobber, hash-bound recovery path for the preserved 1D work ROOT
   that validates then can publish it without recomputing, but DO NOT execute
   publication in this turn.

Add focused tests, run static/unit checks, commit and push the scoped additive
implementation plus status/RUN_LOG/ledger only if facts belong there. Report
commit, hashes, tests, exact recovery command, and whether independent recheck
is required before publication. Do not inspect other playlist logs/artifacts.
