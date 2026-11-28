# PG plan: slot 1 from a private G21_11a copy, and the probe rebuild

By the PG session, for the director's approval before any SciSoft download or NERSC action. Joseph chose route A,
relayed on 2026-11-24: a sha-pinned private copy of SciSoft's G2111a00000 product. Slot 2 is G18_02a_00_000 from
CVMFS. The design is `record/SLOT1-PRIVATE-PRODUCT.md`. Nothing here has run.

## The director's three conditions, and how each is met

1. **The extracted files.** Every member of the tarball is checked by sha256 against a pinned member listing, and
   there must be no extra and no missing member. The listing is computed offline from SciSoft's tarball (step A1),
   and checked on the node after extraction (step B2).
2. **The GENIE configuration actually loaded.** This comes from an open-trace of the run, not from inference.
   - GENIE's own messages are not enough. `AlgConfigPool::LoadAlgConfig` logs only the algorithm config files, at
     NOTICE (`*** GENIE XML config file <path>`, AlgConfigPool.cxx:127). It never names `ModelConfiguration.xml`,
     `master_config.xml` or the generator list, and F1's laconic messenger suppresses NOTICE.
   - So the run is wrapped in `strace -f -qq -e trace=open,openat,openat2 -o <file>`. It traces no execve, so no
     argument and no seed is recorded.
   - Every file the run opens under the genie product, the private product or CVMFS's genie_xsec must equal the
     corresponding SciSoft file by sha256. The pins are a manifest of every regular file in the SciSoft trees
     (step A1).
   - The opened set must include the record's defining files for G21_11a: its ModelConfiguration.xml,
     EventGenerator.xml and TuneGeneratorList.xml, master_config.xml, HybridXSecAlgorithm.xml and the class files.
   - No opened file may lie under any other `GXMLPATH` entry. The receipt lists every opened config file with its
     sha256.
3. **The spline actually used.** It comes from the same trace.
   - The generator's opened spline must be `$SPLDIR/G21_11a_00_000_CH.xml.gz`, the reduced file.
   - Its sha256 must equal the reduce step's output.
   - spline-check must already have shown that file is exactly the C12 and H1 subset of the pinned private
     `gxspl-NUsmall.xml` (`fa475f7f…ed1c`).
   - The reduce step's awk is traced too, so the source it opened is the private copy and no other file.

If any of the three can't be shown, the result is reported, and slot 1 is dropped without a workaround.

**Which run.** There are two traced runs, both inside the steps F1's pipeline already has:
- **B3, the replay on a login node, before generation:** `run_gevgen_v3.sh reduce`, `gen5d_v3.py spline-check` and
  `run_gevgen_v3.sh graphs` (gspl2root) for G21_11a.
  - gspl2root builds the same tune through the same `AlgConfigPool`. The pool loads every master_config entry
    regardless of the application, and it reads the same reduced spline that gevgen is given (`--cross-sections
    "$GENIE_SPLINES_V3"`).
  - This is not event generation: there are no seeds and no events. It verifies conditions 2 and 3 before any
    compute is spent.
- **In the bound PG binary, during generation:** each gevgen task runs under the same strace into W. After the run,
  pg_generate.sh checks the traces against the same pins, before anything is sealed.
  - Only booleans and the public config pins reach PRODUCTS. The traces stay in W and are sealed with the rest.
  - If strace is missing or fails on the compute node, the binary STOPs. Question 2 below covers that case.

## Steps, in order, each needing your GO

### A. Local (laptop): no cluster contact

**A1. The pins.** This step needs your OK for one SciSoft download.
- URL: `https://scisoft.fnal.gov/scisoft/packages/genie_xsec/v3_04_00/genie_xsec-3.04.00-noarch-G2111a00000-k250-e1000.tar.bz2`.
- Expected sha256 `ae159887772a54891fc4bddb189ab108d74c4a48db68c13ed7166524e8797590` (measured 2026-11-24).
- Write root: the session scratchpad, `record/xsec/`.
- I'll compute the full member listing of every file, link and directory, with the sha256 of each regular file,
  and refuse any absolute or `..` member.
- From the already-extracted SciSoft genie tree (`d1a08091…f37f`), I'll compute a manifest of every regular file
  under `genie/v3_04_00/` and its `ups/`.
- Both go into the record as `G2111a-members.json` and `genie-manifest.json`, built by `build_record.py`. No other
  download is needed. The data/ listings for CVMFS tunes come from the node, by names only, as you accepted.

**A2. The code.** These are local edits, sent to you as a diff with shas before any read.
- **Tune support,** per SLOT1-PRIVATE-PRODUCT.md, items 1–8:
  - setup_genie_v3.sh: the `G21_11a_00_000` and `G18_02a_00_000` qualifier cases, and `PRODUCTS` prepended with
    the private products directory, for G21_11a only;
  - run_gevgen_v3.sh: the reduce cases, and SRC taken from one variable that is the CVMFS root, or the private root
    for G21_11a;
  - gen5d_v3.py: `TUNES`, and `PG_SPLINE_PINS` for both tunes;
  - pg_generate.sh, pg_lib.py and fd_f1_prep.py: the truth names.
  The G21_11b and G18_02b entries come out.
- **pg_generate.sh** adds:
  - a private-product check before reduce, of every member against `G2111a-members.json`;
  - strace around the reduce awk, the graphs step and each gevgen task;
  - `pg_lib.py trace-check`, which parses opened paths and compares them with the manifest and the record's
    defining files.
- **The probe rebuild,** as accepted:
  - pinned files, listings and links, by O_NOATIME opens relative to a verified root descriptor, with no symlink
    followed;
  - the live qualifier listing, exact names only;
  - xattr `user.fqrn` == `larsoft.opensciencegrid.org`, required, with revision and root_hash recorded;
  - STOP on any mismatch, recording the node's sha for every pinned path;
  - instantiability, through the pinned .so, .rootmap and _rdict.pcm;
  - each used tune's data/ listing, by names;
  - the gpg rule.
  New checks:
  - strace: path, sha through the fd, and a self-test tracing one open of a probe-created file;
  - `products/.upsfiles/dbconfig` on CVMFS (question 3);
  - after B2, the private product against `G2111a-members.json`.
- **R1.** gpg, gpgconf and strace are opened once, hashed through the fd, and run as `/proc/self/fd/<n>`, so the
  bytes hashed are the bytes run. Question 1 asks where their pins come from.
- **Tests and mutants.** Tests cover all of it. Mutants are killed only by an assertion FAIL, and import errors,
  collection errors and timeouts are INVALID, listed and counted. An agy read follows. The changes then go to you
  for codex-school2.

### B. NERSC, login node only, through reviewed connect scripts

Each script's sha comes to you before it runs. ssh is the launcher's: `-F /dev/null`, explicit options, no
forwarding.

**B1. The probe.** Read-only, on a login node. It covers both tunes' CVMFS side, the spent controls, gpg, strace
and dbconfig. It writes only `pg-probe.out`, on the laptop.

**B2. Installing the private product.** This writes to NERSC. Script `pg-install-g2111a.sh`:
- Write root: `/pscratch/sd/j/josephrb/covfix-pg/products/`. That's scratch, not CFS. Nothing else is written.
- The steps:
  ```
  P=/pscratch/sd/j/josephrb/covfix-pg/products; T=genie_xsec-3.04.00-noarch-G2111a00000-k250-e1000.tar.bz2
  mkdir -p "$P/dl" (refused if $P already exists)
  curl -sf --proto =https -o "$P/dl/$T" https://scisoft.fnal.gov/scisoft/packages/genie_xsec/v3_04_00/$T
  sha256 must be ae159887…7590, or the script removes the download and STOPs
  tar -tjf must equal G2111a-members.json's names (no absolute or .. member); then tar -xjf -C "$P" --no-same-owner
  every extracted member's type and sha256 must equal the pins, with no extra file under $P/genie_xsec
  cp CVMFS products/.upsfiles/dbconfig to $P/.upsfiles/dbconfig, then check its sha against the probe's (question 3)
  chmod -R a-w "$P/genie_xsec" "$P/.upsfiles"; rm "$P/dl/$T"
  ```
- Its receipt lists each check and each sha, and holds no physics.

**B3. The replay.** On a login node, after B2. Script `pg-replay-g2111a.sh`:
- Write root: a fresh `/pscratch/sd/j/josephrb/covfix-pg/replay-<utc>/`.
- It runs, under strace: `run_gevgen_v3.sh reduce G21_11a_00_000 <W>/spl`, then `gen5d_v3.py spline-check`, then
  `run_gevgen_v3.sh graphs G21_11a_00_000 <W>/spl <W>/graphs.root`. These are F1's steps from the PG branch at a
  pinned commit, with no seeds and no events.
- Then `pg_lib.py trace-check` gives the receipt for conditions 2 and 3: each opened config file and the opened
  spline, with its sha256 and its match.
- The graphs file is public cross-section text with no seed. It stays on pscratch, and its sha is in the receipt.
- B3 runs the same code the bound binary runs, so a pass here predicts the binary's own pre-generation checks.

**C. The generation** is not mine to run. It's the bound PG binary, through cov2d and your wrapper, as before.

## Open questions for you

1. **R1's pins for gpg, gpgconf and strace.** I don't have node shas for them. I propose the probe records them, by
   a hash through the fd, then you pin them in a confirm, and pg_generate.sh checks them through the fd at run
   time. If R1 needs pins in hand first, which receipt holds them?
2. **strace on compute nodes** is unknown until a job runs there. If it's missing, the binary STOPs at the first
   traced step. Is B3's login-node replay sufficient for conditions 2 and 3 in that case, or does a missing
   compute-node trace drop slot 1?
3. **The UPS database file.** `setup` needs each `PRODUCTS` directory to be a UPS database, which normally holds
   `.upsfiles/dbconfig`. The tarball has none, so B2 would copy CVMFS's byte for byte and check it against the
   probe's sha. If you'd rather not author any file in the product directory, the alternative is that
   setup_genie_v3.sh skips `setup genie_xsec` for G21_11a and sets the table's four variables itself. That
   departs further from F1, and weakens the `GENIE_XSEC_TUNE` check to a tautology, so I recommend the dbconfig
   copy.
4. **The pscratch purge.** Files unread for 8 weeks are purged, per NERSC policy as I understand it, unverified. B2
   writes the product shortly before generation, and the binary re-verifies every member before use. If it has
   been purged, the binary STOPs.
