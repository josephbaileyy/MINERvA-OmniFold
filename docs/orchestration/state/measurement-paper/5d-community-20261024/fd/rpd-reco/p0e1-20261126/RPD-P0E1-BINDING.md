# RPD-P0E1-BINDING: e1's P0 (RPD-RECO amendment 1, C-JOIN part 2)

Follows RPD-FLUX4-BINDING (#1397; flux4 PASS, receipts #1403). This binds P0 for e1: C-JOIN part 2 (the omnifile spot check, bitwise) and P0's checks on flux4's products.

## What is bound

The p0e1 package merged in #1406 (head `99535a1ad03db4fbce60f9383417fbb4eb055205`), on main at `0ea95a4e8172d5724b81f62a645c74fbf3a0d398`. S = `2415e8d66d1a9160e724d426eaeb54d458d4b4f7`. sha256:

    f92d034df0db5bf487f689b0efc1eb8862396303647fa1172ad5e6eaa3f4c47a  production-config.ready.json
    5016f37822af9c43e52b8fe9379757306c8dd47948115d9dad566d88ab242434  rpd_p0_connect.sh
    d52f3576192b25672f892808c0f740accfb392813ef525e4ffad5ea3da03b35b  rpd_p0_fetch.sh
    4ffd4a596e5339476cd129306dc7d34c0a51ea5b68718568520c3d4421588efd  rpd_p0_launch.sh
    bcdc1b99aa4aff1e645e8000b7630d38d3bcafda74f70b43869195dc64071008  tools/p0_checks.py
    c9d5e9567eba82818616c2b25c0162f113026e5feec8d2971dbe8f18d5f3dee9  tools/p0_expected.json
    6ad0f68fb309a7b83adc0f65ed709e5e2412e650e115075fe41ebbc7a070134f  tools/p0_supervise.py
    940fb7598c782c77c2b3dd0e677f80568f0fdb31fd033e8e8988404049f38810  tools/fence_overlap.py

The runner, as the connect's heredoc writes it, has sha256 `f145f41f32741119ae016b815e5a2b00f9da9ad55cb8bc053e7e7d52ade8902f`. The package was generated from p0-20261123 by counted replacements, and its normalized diff holds only the declared changes. The tests and mutants all pass, and the agy read (gemini-4-hydrogen-high) gave GO.

## What the GO covers

One connect, `rpd_p0_launch.sh connect …`, with the three-lane ack file (cov2d, tier3-design, minerva-lib, each at most 6 h old). It runs pins-dry, p0-dry, then pins and p0. The real steps run only if both dry steps pass, and any failure is a STOP, as ruled on 2026-11-23. After it, one fetch. Login-node work only, 0 node-h. Root: `/pscratch/sd/j/josephrb/rpd-reco-p0e1-20261126/`. flux4's products are read in place with O_NOATIME.

C-JOIN part 2 copies the 12 RDX omnifiles with O_NOATIME, pinned at c2's shas, once into dry/ and once into run/: 14.75 GB on pscratch. Peak RSS is bounded at 1.23 GB, 15% of the 8e9 B cap. P0 opens no MAT library and no NuE file. ibu-chi is told before the connect.

Not covered: d2-predict, step0, the c0 harness, c0 (each needs its own binding), any resubmission, and any write outside the root or to CFS.

## Post-receipt, through the director

Removal of P0's root (the omnifile copies first), and of flux4's lane `rpd-reco-flux4-20261126/`.

The NERSC certificate is valid until 2026-11-27T14:22:19Z. The launcher refuses within 30 min of expiry.
