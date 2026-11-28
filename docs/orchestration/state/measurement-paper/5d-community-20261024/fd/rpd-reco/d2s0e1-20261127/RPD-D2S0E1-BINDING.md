# RPD-D2S0E1-BINDING: e1's d2-predict and step0, with true Eν (RPD-RECO amendment 1)

Follows RPD-P0E1-BINDING (#1407; P0 PASS, receipts #1408). On 2026-11-24 d2s0 STOPped at C-E3 with the inverted Eν (#1284). This binds the rerun with true Eν from flux4's products, as amendment 1 declares. C-E3's formula and gates are unchanged: weighted median |q₃′/q₃ − 1| ≤ 0.002 and 99th percentile ≤ 0.03, per p∥ stratum.

## What is bound

The d2s0e1 package merged in #1414 (head `e7e75bb68f89e344bc104a4070416af0a195becd`), on main at `3f04cadc8e0b944528cc3a7b3d4b85324c13feb1`. S = `2415e8d66d1a9160e724d426eaeb54d458d4b4f7`. sha256:

    f92d034df0db5bf487f689b0efc1eb8862396303647fa1172ad5e6eaa3f4c47a  production-config.ready.json
    e1b5084b153d81bbba307f73e83231c7669ec4adeb0992f6ac5971a87db3090b  rpd_d2s0_connect.sh
    0853a02969f35f74c4e37c41b74247de102b2944486d7de81ad6f43306d662ca  rpd_d2s0_fetch.sh
    24739c022ac04202f9e0fecf017fc07ca36fd60159a8b4294a298f3b1475352c  rpd_d2s0_launch.sh
    06b5e7cb95c551a85738a3fc1366650f351895f528f43f454ff1b42e8a879442  tools/d2s0_checks.py
    47d7570677baaee68241d76c059312592e7c8b8a61bfc2885d98add6712a711b  tools/d2s0_expected.json
    6ad0f68fb309a7b83adc0f65ed709e5e2412e650e115075fe41ebbc7a070134f  tools/p0_supervise.py
    6503ab07f5d2b4afe88720064d2f9ceac0dbe03aa4c1425a94805c99710fcb5a  tools/fence_overlap.py

The runner, as the connect's heredoc writes it, has sha256 `7f7c7e1509cb56401d547d488944b2a0d5db62b97face153df5fbdf43a8b41d1`. The package was generated from d2s0-20261124 by counted replacements, and its normalized diff holds only the declared changes. The tests and mutants all pass, and the agy read (gemini-4-hydrogen-high) gave GO. Blinding holds: data=False, and no --prediction is passed.

## What the GO covers

One connect with the three-lane ack file (cov2d, tier3-design, minerva-lib), with ibu-chi told, then one fetch. Login-node work only, 0 node-h. The measured expectation is about 7 min (the 11-24 aggregate pass took 6 min 42 s with a 2.0 GB peak), against the runner's deadline. Root: `/pscratch/sd/j/josephrb/rpd-reco-d2s0e1-20261127/`. It opens no NuE file.

**C-E3's outcome comes to the director before anything downstream is packaged.** A C-E3 STOP with true Eν is a finding, reported as it stands. No gate is loosened.

Not covered: the c0 harness and c0 (each needs its own binding), any resubmission, and any write outside the root or to CFS. The NERSC certificate is valid until 2026-11-28T02:05:18Z.
