Compact XR evidence (no data values). Sources on Perlmutter:
  outroot  /pscratch/sd/j/josephrb/xr-two-d-followup-20261010
  reduce   /pscratch/sd/j/josephrb/xr-reduce.4fPw

comparisons.json   xr_compare.py over the frozen outroot (all INCONCLUSIVE; no complete attempt)
ledger.txt         xr_admit.py ledger --now 2026-10-11T00:26:52Z, on sacct.psv
sacct.psv          sacct -X for the five xr_* jobs (times cluster-local PDT)
submissions.jsonl  the outroot's submission record, verbatim
joblogs.txt        the ten Slurm .out/.err files concatenated (the repository ignores *.out/*.err)

admission.json is NOT tracked. It holds two path+sha256 pairs (authorization, setup), so tracking it
adds two live receipt bindings to the shared inventory (pre-commit: 144 -> 146), and that inventory's
owner must approve such a change. Its identity and the values it binds:
  /pscratch/sd/j/josephrb/xr-two-d-followup-20261010/admission.json
  sha256 ef8b49b364a908e2edcc10322ea3a6f6f15bd4aacb5c749d0c3b253104459e1f (7029 bytes)
  package_commit  06eae0fede3508419f235f8cbe61954b33de8497
  manifest_sha256 fbca1be80d56b09751bcd9f8fbe698ac65786ebe08e21ae04e561e5c73dd06b8
  head            b838fc02d599947858daae4778bb31d1f01f2856
  runs_sha256     b38d6e2d509db692b1443de30592c4afabed8e7558d93a96e03b5953e1232b7f
  references_sha256 af7d5a1935176367e3c6cff9c17986e8e4e5c15c91b75d73efb3ccec04b88c89
  authorization   docs/orchestration/AUTHORIZATION-20261010-xr.md d368967b2b2b2a2568688f4eaf0f647cb38bc421845776be6cc86d92c6a8240f
  setup           /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh ea3c6998d33f45c831b80da5e5228032a19fc392018ede54a7f52f2f283d1d48 (+ five nested scripts, B7)
  outroot, grant_date 2026-10-10
